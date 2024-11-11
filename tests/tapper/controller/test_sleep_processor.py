import time
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from unittest.mock import call
from unittest.mock import MagicMock

import pytest
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.sleep_processor import StopTapperActionException


@dataclass
class SleepFixture:
    sleep: Callable[[Any], None]
    processor: SleepCommandProcessor
    mock_actual_sleep: MagicMock | Callable[[Any], None]

    def get_time_slept(self) -> float:
        return sum(call_.args[0] for call_ in self.mock_actual_sleep.call_args_list)


@pytest.fixture
def sleep_fixture() -> SleepFixture:
    processor = SleepCommandProcessor(
        check_interval=1,
        kill_check_fn=MagicMock(return_value=False),
        pause_check_fn=MagicMock(return_value=False),
        actual_sleep_fn=MagicMock(),
        get_time_fn=MagicMock(return_value=0),
    )
    return SleepFixture(
        processor=processor,
        sleep=processor.sleep,
        mock_actual_sleep=processor.actual_sleep_fn,
    )


@dataclass
class Counter:
    count: int = 0
    ticks: list[float] = field(default_factory=list)
    result: bool = False
    at_3: Callable[[], bool] | None = None

    def tick(self) -> bool:
        self.count += 1
        if self.count == 3 and self.at_3 is not None:
            return self.at_3()
        return self.result


class TestSleep:
    def test_simplest(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.sleep(123)
        assert sleep_fixture.get_time_slept() == 123
        assert sleep_fixture.processor.pause_check_fn.call_args_list != []
        assert sleep_fixture.processor.kill_check_fn.call_args_list != []

    def test_zero_time(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.sleep(0)
        assert sleep_fixture.get_time_slept() == 0
        assert sleep_fixture.processor.pause_check_fn.call_args_list != []
        assert sleep_fixture.processor.kill_check_fn.call_args_list != []

    def test_negative_time(self, sleep_fixture: SleepFixture) -> None:
        with pytest.raises(ValueError):
            sleep_fixture.sleep(-1)

    def test_correct_number_of_sleeps(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.check_interval = 0.05
        sleep_fixture.sleep(0.4)
        assert sleep_fixture.get_time_slept() == 0.4
        assert sleep_fixture.mock_actual_sleep.call_args_list == [call(0.05)] * 8

    def test_check_interval_bigger_than_sleep_time(
        self, sleep_fixture: SleepFixture
    ) -> None:
        sleep_fixture.processor.check_interval = 1
        sleep_fixture.sleep(0.02)
        assert sleep_fixture.get_time_slept() == 0.02
        assert sleep_fixture.processor.pause_check_fn.call_args_list != []
        assert sleep_fixture.processor.kill_check_fn.call_args_list != []

    def test_time_str_seconds(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.sleep("2.1s")
        assert sleep_fixture.get_time_slept() == 2.1

    def test_time_str_millis(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.sleep("20ms")
        assert sleep_fixture.get_time_slept() == 0.02

    def test_repeat_sleep(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.sleep(123)
        sleep_fixture.sleep(".123s")
        assert sleep_fixture.get_time_slept() == 123.123


class TestSleepKill:
    def test_immediate_kill(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.kill_check_fn = lambda: True
        with pytest.raises(StopTapperActionException):
            sleep_fixture.sleep(20)

    def test_killed_after_some_time_interval(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.check_interval = 0.01
        sleep_fixture.processor.kill_check_fn.side_effect = lambda: bool(
            sleep_fixture.get_time_slept() >= 1.234
        )
        with pytest.raises(StopTapperActionException):
            sleep_fixture.sleep(10)
        assert sleep_fixture.get_time_slept() == pytest.approx(1.234, abs=0.01)
        assert len(sleep_fixture.processor.kill_check_fn.call_args_list) >= 123


class TestSleepPause:
    def test_time_slept_extends_with_pause(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.check_interval = 0.1
        sleep_fixture.processor.pause_check_fn.side_effect = lambda: bool(
            1 <= sleep_fixture.get_time_slept() <= 8
        )
        sleep_fixture.sleep(10)
        assert sleep_fixture.get_time_slept() == pytest.approx(17, abs=0.2)


def assert_time_equals(time_1: float, time_2: float) -> None:
    assert abs(time_1 - time_2) < 0.05


class TestRealSleep:
    def test_zero_time(self) -> None:
        processor = SleepCommandProcessor(
            check_interval=1,
            kill_check_fn=lambda: False,
            pause_check_fn=lambda: False,
        )

        time_start = time.perf_counter()
        processor.sleep(0)
        assert_time_equals(time_start, time.perf_counter())

    def test_correct_time_slept(self) -> None:
        kill_c = Counter()
        pause_c = Counter()
        processor = SleepCommandProcessor(
            check_interval=0.05,
            kill_check_fn=kill_c.tick,
            pause_check_fn=pause_c.tick,
        )

        time_start = time.perf_counter()
        processor.sleep(0.1)

        assert_time_equals(time_start + 0.1, time.perf_counter())
        assert kill_c.count >= 2
        assert pause_c.count >= 2
