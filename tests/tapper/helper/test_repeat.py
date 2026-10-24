import threading
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterator
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

import tapper
from tapper.controller import flow_control
from tapper.controller.flow_control import StopTapperActionError
from tapper.helper import repeat
from tapper.helper._util import repeat_util
from testutil_model import Stepper
from testutil_model import join_repeat_worker


@dataclass
class Counter:
    count: int = 0
    action_at_5: Callable[[], None] | None = None

    def tick(self) -> None:
        self.count += 1
        if self.count == 5 and self.action_at_5 is not None:
            self.action_at_5()


def mock_return_false(mock: Any) -> None:
    mock.return_value = False


def raise_io_error() -> None:
    raise OSError()


@pytest.fixture(autouse=True)
def runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    """What a repeat reads from the initialized tapper: root send settings and key state."""
    stub = SimpleNamespace(
        root=SimpleNamespace(send_interval=0, send_press_duration=0),
        pressed=SimpleNamespace(pressed_keys={}),
    )
    monkeypatch.setattr(tapper, "_runtime", stub, raising=False)


@pytest.fixture(autouse=True)
def assert_clean_state_after_test() -> Generator:
    yield
    join_repeat_worker()
    assert repeat_util.running_repeatable is None


class TestRepeatWhileFn:
    def test_simplest(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 1, counter.tick, interval=0)()
        join_repeat_worker()  # the condition is false right after the action, so no sleep
        assert counter.count == 1

    def test_several_times(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 5, counter.tick, interval=0)()
        stepper.wait_action()
        stepper.step(3)
        stepper.release()
        join_repeat_worker()
        assert counter.count == 5

    def test_zero_times(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        join_repeat_worker()
        assert counter.count == 0

    def test_max_repeats(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0, max_repeats=5)()
        stepper.wait_action()
        stepper.step(4)
        stepper.release()
        join_repeat_worker()
        assert counter.count == 5

    def test_sleeps_the_interval(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0.035, max_repeats=2)()
        stepper.wait_action()
        stepper.step()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 2
        assert stepper.slept == [0.035, 0.035]

    def test_second_repeat_overrides_first(self, stepper: Stepper) -> None:
        counter1 = Counter()
        counter2 = Counter()
        repeat.while_fn(lambda: True, counter1.tick, interval=0.05)()
        stepper.wait_action()

        repeat.while_fn(lambda: counter2.count < 5, counter2.tick, interval=0)()
        stepper.release()  # the first loop ends at its next check
        stepper.wait_action()
        stepper.step(3)
        stepper.release()
        join_repeat_worker()
        assert (counter1.count, counter2.count) == (1, 5)

    def test_second_repeat_overrides_without_repeats(self, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0.05)()
        stepper.wait_action()

        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 1


class TestRepeatWhilePressed:
    @pytest.fixture
    def mock_pressed(self) -> Iterator[Any]:
        with patch("tapper.kb.pressed") as mock_pressed:
            mock_pressed.return_value = True
            yield mock_pressed

    def test_stops_when_released_by_action(
        self, mock_pressed: Any, stepper: Stepper
    ) -> None:
        counter = Counter()
        counter.action_at_5 = lambda: mock_return_false(mock_pressed)
        repeat.while_pressed("q", counter.tick)()
        stepper.wait_action()
        stepper.step(3)
        stepper.release()  # the 5th action releases the key, so the loop ends
        join_repeat_worker()
        assert counter.count == 5

    def test_stops_when_released(self, mock_pressed: Any, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_pressed("q", counter.tick)()
        stepper.wait_action()
        stepper.step(1)
        mock_pressed.return_value = False
        stepper.release()
        join_repeat_worker()
        assert counter.count == 2
        assert repeat_util.running_repeatable is None

    def test_nonexistent_symbol(self) -> None:
        with pytest.raises(ValueError):
            repeat.while_pressed("some_key", lambda: False)

    def test_max_repeats(self, mock_pressed: Any, stepper: Stepper) -> None:
        counter = Counter()
        repeat.while_pressed("q", counter.tick, max_repeats=3)()
        stepper.wait_action()
        stepper.step(2)
        stepper.release()
        join_repeat_worker()
        assert counter.count == 3


class TestRepeatToggle:
    def test_simplest(self, stepper: Stepper) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick)

        toggle()
        stepper.wait_action()
        toggle()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 1

    def test_toggle_twice(self, stepper: Stepper) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick)

        toggle()
        stepper.wait_action()
        toggle()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 1

        toggle()
        stepper.wait_action()
        stepper.step(1)
        toggle()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 3

    def test_two_toggles(self, stepper: Stepper) -> None:
        counter1 = Counter()
        counter2 = Counter()
        toggle1 = repeat.toggle(counter1.tick)
        toggle2 = repeat.toggle(counter2.tick)

        toggle1()
        stepper.wait_action()
        toggle2()  # takes over: the first loop ends at its next check
        stepper.release()
        stepper.wait_action()
        assert (counter1.count, counter2.count) == (1, 1)

        toggle1()
        stepper.release()
        stepper.wait_action()
        assert (counter1.count, counter2.count) == (2, 1)

        toggle1()
        stepper.release()
        join_repeat_worker()

    def test_max_repeats(self, stepper: Stepper) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick, max_repeats=2)

        toggle()
        stepper.wait_action()
        stepper.step(1)
        stepper.release()
        join_repeat_worker()
        assert counter.count == 2

        toggle()
        stepper.wait_action()
        stepper.step(1)
        stepper.release()
        join_repeat_worker()
        assert counter.count == 4

    def test_toggle_again_after_exception(self, stepper: Stepper) -> None:
        counter = Counter()
        counter.action_at_5 = raise_io_error
        toggle = repeat.toggle(counter.tick)

        toggle()
        stepper.wait_action()
        stepper.step(3)
        stepper.release()  # the 5th action raises, which ends the loop
        join_repeat_worker()
        assert counter.count == 5

        toggle()
        stepper.wait_action()
        toggle()
        stepper.release()
        join_repeat_worker()
        assert counter.count == 6

    def test_condition(self, stepper: Stepper) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick, condition=lambda: counter.count < 3)

        toggle()
        stepper.wait_action()
        stepper.step(1)
        stepper.release()  # the 3rd action makes the condition false
        join_repeat_worker()
        assert counter.count == 3


class TestKill:
    def test_toggle_runs_after_a_kill(self, monkeypatch: pytest.MonkeyPatch) -> None:
        killed = Counter()
        survivor = Counter()

        def kill(*_: Any) -> None:
            raise StopTapperActionError

        monkeypatch.setattr(tapper, "sleep", kill)
        repeat.toggle(killed.tick)()
        join_repeat_worker()
        assert killed.count == 1

        monkeypatch.setattr(tapper, "sleep", lambda *_: None)
        repeat.toggle(survivor.tick, max_repeats=3)()
        join_repeat_worker()
        assert survivor.count == 3


class TestShutdown:
    def test_repeat_ends_when_tapper_stops(
        self, monkeypatch: pytest.MonkeyPatch, stepper: Stepper
    ) -> None:
        shutdown = threading.Event()
        monkeypatch.setattr(flow_control, "shutdown", shutdown)
        counter = Counter()

        repeat.toggle(counter.tick)()
        stepper.wait_action()
        shutdown.set()
        stepper.release()
        join_repeat_worker()

        assert repeat_util.running_repeatable is None
        assert counter.count == 1
