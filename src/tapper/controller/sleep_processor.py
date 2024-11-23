import time
from dataclasses import dataclass
from typing import Callable

from tapper.controller.flow_control import StopTapperActionException
from tapper.parser import common


def parse_sleep_time(length_of_time: float | str) -> float:
    if isinstance(length_of_time, str):
        sleep_time = common.parse_sleep_time(length_of_time)
        if sleep_time is None:
            raise ValueError(
                f"tapper.sleep length_of_time {length_of_time} could not be parsed."
            )
    elif isinstance(length_of_time, (float, int)):
        sleep_time = length_of_time
    else:
        raise ValueError(f"tapper.sleep length_of_time {length_of_time} is invalid.")
    if sleep_time < 0:
        raise ValueError(f"tapper.sleep time {sleep_time} should not be negative.")
    return sleep_time


@dataclass
class SleepCommandProcessor:
    """Implementation of tapper's "sleep" command."""

    check_interval: float
    """How often the check is made for whether to continue sleeping."""
    kill_check_fn: Callable[[], bool]
    """Checks whether action should be killed."""
    pause_check_fn: Callable[[], bool]
    """Checks whether action should be paused."""
    actual_sleep_fn: Callable[[float], None] = time.sleep
    get_time_fn: Callable[[], float] = time.perf_counter

    @classmethod
    def from_none(cls) -> "SleepCommandProcessor":
        """To be filled during init."""
        return SleepCommandProcessor(None, None, None)  # type: ignore

    def __post_init__(self) -> None:
        if self.check_interval is not None and self.check_interval <= 0:
            raise ValueError(
                "SleepCommandProcessor check_interval must be greater than 0."
            )

    def sleep(self, length_of_time: float | str) -> None:
        """
        Ultimate function of this module and class.
        Suspends execution for a length of time.
        This is functionally identical to `time.sleep`, but tapper
        has control needed to interrupt or pause this.

        :param length_of_time: Either number (seconds),
            or str seconds/millis like: "1s", "50ms".
        """
        self.kill_if_required()
        self.pause_if_required()
        sleep_time = parse_sleep_time(length_of_time)
        while sleep_time > 0:
            sleep_time = round(sleep_time, 3)
            to_sleep = min(self.check_interval, sleep_time)
            self.actual_sleep_fn(to_sleep)
            sleep_time = sleep_time - to_sleep

            operational_start_time = self.get_time_fn()
            self.kill_if_required()
            self.pause_if_required()
            operational_total_time = self.get_time_fn() - operational_start_time
            sleep_time = sleep_time - operational_total_time

    def pause_if_required(self) -> None:
        while self.pause_check_fn():
            self.actual_sleep_fn(self.check_interval)

    def kill_if_required(self) -> None:
        if self.kill_check_fn():
            raise StopTapperActionException
