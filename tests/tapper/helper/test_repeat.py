import time
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Generator
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from tapper.helper import repeat
from tapper.helper._util import repeat_util


@pytest.fixture
def mock_sleep() -> Any:
    repeat_util.sleep = MagicMock()
    yield repeat_util.sleep
    repeat_util.sleep = time.sleep


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
def assert_clean_state_after_test() -> Generator:
    yield
    assert repeat_util.running_repeatable is None


class TestRepeatWhileFn:
    def test_simplest(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 1, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 1

    def test_several_times(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 5, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 5

    def test_zero_times(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 0

    def test_max_repeats(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0, max_repeats=5)()
        time.sleep(0.001)

        assert counter.count == 5

    def test_condition_false_from_start(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 0

    def test_sleep_time(self, mock_sleep: Any) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0.035, max_repeats=2)()
        time.sleep(0.001)
        assert counter.count == 2
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args == call(0.035)

    def test_second_repeat_overrides_first(self) -> None:
        counter1 = Counter()
        counter2 = Counter()
        repeat.while_fn(lambda: True, counter1.tick, interval=0.05)()
        time.sleep(0.01)
        repeat.while_fn(lambda: counter2.count < 5, counter2.tick, interval=0)()
        time.sleep(
            0.05
        )  # if less time, wait for 1st will be longer since switch is not instant.

        assert counter1.count == 1
        assert counter2.count == 5

    def test_second_repeat_overrides_without_repeats(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0.01)()
        time.sleep(0.001)
        assert counter.count == 1
        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        time.sleep(0.02)  # enough for 1st to repeat
        assert counter.count == 1


class TestRepeatWhilePressed:
    @pytest.fixture
    def mock_pressed(self) -> Any:
        with patch("tapper.kb.pressed") as mock_pressed:
            mock_pressed.return_value = True
            yield mock_pressed

    def test_simplest(self, mock_pressed: Any, mock_sleep: Any) -> None:
        counter = Counter()
        counter.action_at_5 = lambda: mock_return_false(mock_pressed)
        repeat.while_pressed("q", counter.tick)()
        time.sleep(0.001)
        mock_pressed.return_value = False
        assert counter.count == 5

    def test_press_and_release(self, mock_pressed: Any, mock_sleep: Any) -> None:
        counter = Counter()
        counter.action_at_5 = lambda: mock_return_false(mock_pressed)
        repeat.while_pressed("q", counter.tick)()
        time.sleep(0.001)

        mock_pressed.return_value = False
        time.sleep(0.001)

        mock_pressed.return_value = True
        time.sleep(0.001)

        assert counter.count == 5
        assert mock_sleep.call_count == 4

    def test_nonexistent_symbol(self) -> None:
        with pytest.raises(Exception):
            repeat.while_pressed("some_key", lambda: False)

    def test_max_repeats(self, mock_pressed: Any, mock_sleep: Any) -> None:
        counter = Counter()
        counter.action_at_5 = lambda: mock_return_false(mock_pressed)
        repeat.while_pressed("q", counter.tick, max_repeats=3)()
        time.sleep(0.001)
        mock_pressed.return_value = False
        assert counter.count == 3


class TestRepeatToggle:
    def test_simplest(self, mock_sleep: Any) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick)

        toggle()
        time.sleep(0.001)
        toggle()
        assert counter.count > 0

    def test_toggle_twice(self, mock_sleep: Any) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick)

        toggle()
        time.sleep(0.001)
        toggle()
        time.sleep(0.001)
        count_1 = counter.count
        assert counter.count > 0

        time.sleep(0.001)
        assert counter.count == count_1

        toggle()
        time.sleep(0.001)
        toggle()
        assert counter.count > count_1

    def test_two_toggles(self, mock_sleep: Any) -> None:
        counter1 = Counter()
        counter2 = Counter()
        toggle1 = repeat.toggle(counter1.tick)
        toggle2 = repeat.toggle(counter2.tick)

        toggle1()
        time.sleep(0.001)
        toggle2()
        time.sleep(0.001)
        count_1 = counter1.count
        time.sleep(0.001)
        assert counter1.count == count_1

        toggle1()
        time.sleep(0.001)
        count_2 = counter2.count
        time.sleep(0.001)
        assert counter2.count == count_2
        toggle1()

    def test_max_repeats(self, mock_sleep: Any) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick, max_repeats=2)

        toggle()
        time.sleep(0.001)
        assert counter.count == 2

        toggle()
        time.sleep(0.001)
        assert counter.count == 4

    def test_toggle_again_after_exception(self, mock_sleep: Any) -> None:
        counter = Counter()
        counter.action_at_5 = raise_io_error
        toggle = repeat.toggle(counter.tick)

        toggle()
        time.sleep(0.001)
        assert counter.count == 5

        toggle()
        time.sleep(0.001)
        toggle()
        assert counter.count > 5

    def test_condition(self, mock_sleep: Any) -> None:
        counter = Counter()
        toggle = repeat.toggle(counter.tick, condition=lambda: counter.count < 3)

        toggle()
        time.sleep(0.001)

        assert counter.count == 3