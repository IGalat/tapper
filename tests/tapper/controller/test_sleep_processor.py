import time
from dataclasses import dataclass
from dataclasses import field
from typing import Callable

import pytest
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.sleep_processor import StopTapperActionException


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


def assert_time_equals(time_1: float, time_2: float) -> None:
    assert abs(time_1 - time_2) < 0.05


class TestSleepProcessor:
    def test_simplest(self) -> None:
        processor = SleepCommandProcessor(
            check_interval=1,
            kill_check_fn=lambda: False,
        )

        time_start = time.perf_counter()
        processor.sleep(0)
        assert_time_equals(time_start, time.perf_counter())

    def test_immediate_kill(self) -> None:
        counter = Counter(result=True)
        processor = SleepCommandProcessor(check_interval=1, kill_check_fn=counter.tick)
        with pytest.raises(StopTapperActionException):
            processor.sleep(20)

    def test_zero_time(self) -> None:
        counter = Counter()
        processor = SleepCommandProcessor(
            check_interval=1,
            kill_check_fn=counter.tick,
        )
        processor.sleep(0)
        assert counter.count == 1

    def test_negative_time(self) -> None:
        processor = SleepCommandProcessor(
            check_interval=1,
            kill_check_fn=lambda: False,
        )
        with pytest.raises(ValueError):
            processor.sleep(-1)

    def test_correct_time_and_number_of_checks(self) -> None:
        counter = Counter()
        processor = SleepCommandProcessor(
            check_interval=0.05,
            kill_check_fn=counter.tick,
        )

        time_start = time.perf_counter()
        processor.sleep(0.1)
        assert counter.count == 3  # 1 check at the start and 2 intervals
        assert_time_equals(time_start + 0.1, time.perf_counter())

    def test_check_interval_bigger_than_sleep_time(self) -> None:
        counter = Counter()
        processor = SleepCommandProcessor(
            check_interval=1,
            kill_check_fn=counter.tick,
        )

        time_start = time.perf_counter()
        processor.sleep(0.02)
        assert counter.count == 2
        assert_time_equals(time_start + 0.02, time.perf_counter())

    def test_time_str_seconds(self) -> None:
        processor = SleepCommandProcessor(
            check_interval=0.01,
            kill_check_fn=lambda: False,
        )

        time_start = time.perf_counter()
        processor.sleep("0.02s")
        assert_time_equals(time_start + 0.02, time.perf_counter())

    def test_time_str_millis(self) -> None:
        processor = SleepCommandProcessor(
            check_interval=0.01,
            kill_check_fn=lambda: False,
        )

        time_start = time.perf_counter()
        processor.sleep("20ms")
        assert_time_equals(time_start + 0.02, time.perf_counter())

    def test_killed_after_3_interval(self) -> None:
        counter = Counter(at_3=lambda: True)
        processor = SleepCommandProcessor(
            check_interval=0.01,
            kill_check_fn=counter.tick,
        )

        time_start = time.perf_counter()
        with pytest.raises(StopTapperActionException):
            processor.sleep(1)
        assert counter.count == 3  # 1 initial and 2 sleeps
        assert_time_equals(time_start + 0.02, time.perf_counter())
