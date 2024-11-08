import time
from typing import Callable

from attr import dataclass
from tapper.parser import common


class StopTapperActionException(Exception):
    """Normal way to interrupt tapper's action. Will not cause error logs etc."""


@dataclass
class SleepCommandProcessor:
    """Implementation of tapper's "sleep" command."""

    check_interval: float
    """How often the check is made for whether to continue sleeping."""
    kill_check_fn: Callable[[], bool]
    """Checks whether action should be killed."""
    _actual_sleep_fn: Callable[[float], None] = time.sleep

    def __post_init__(self) -> None:
        if self.check_interval <= 0:
            raise ValueError(
                "SleepCommandProcessor check_interval must be greater than 0."
            )

    def sleep(self, length_of_time: float | str) -> None:
        """
        Suspend execution for a length of time.
        This is functionally identical to `time.sleep`, but tapper
        has control needed to interrupt or pause this.

        :param length_of_time: Either number (seconds),
            or str seconds/millis like: "1s", "50ms".
        """
        self.kill_if_required()
        started_at = time.perf_counter()
        time_s = (
            common.parse_sleep_time(length_of_time)
            if isinstance(length_of_time, str)
            else length_of_time
        )
        if time_s is None or time_s < 0:
            raise ValueError(f"sleep {length_of_time} is invalid")
        finish_time = started_at + time_s
        while (now := time.perf_counter()) < finish_time:
            self._actual_sleep_fn(min(self.check_interval, finish_time - now))
            self.kill_if_required()

    def kill_if_required(self) -> None:
        if self.kill_check_fn():
            raise StopTapperActionException
