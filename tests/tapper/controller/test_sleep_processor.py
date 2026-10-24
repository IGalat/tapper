from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import call

import pytest

from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.sleep_processor import StopTapperActionError
from testutil_model import FakeClock


@dataclass
class SleepFixture:
    sleep: Callable[[Any], None]
    processor: SleepCommandProcessor
    mock_actual_sleep: MagicMock | Callable[[Any], None]

    def get_time_slept(self) -> float:
        return round(
            sum(call_.args[0] for call_ in self.mock_actual_sleep.call_args_list), 5
        )


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

    def test_check_overhead_shortens_the_sleep(
        self, sleep_fixture: SleepFixture
    ) -> None:
        """Time the pause/kill checks take counts towards the requested duration."""
        clock = FakeClock()
        sleep_fixture.processor.get_time_fn = clock
        sleep_fixture.processor.check_interval = 0.1
        sleep_fixture.processor.kill_check_fn.side_effect = lambda: clock.advance(0.02)
        sleep_fixture.sleep(0.5)
        # 4 full chunks, each followed by a 0.02 check, then the 0.02 that is left
        assert sleep_fixture.get_time_slept() == pytest.approx(0.42)
        assert sleep_fixture.mock_actual_sleep.call_args_list == [call(0.1)] * 4 + [
            call(0.02)
        ]


class TestSleepKill:
    def test_immediate_kill(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.kill_check_fn = lambda: True
        with pytest.raises(StopTapperActionError):
            sleep_fixture.sleep(20)

    def test_killed_after_some_time_interval(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.check_interval = 0.01
        sleep_fixture.processor.kill_check_fn.side_effect = lambda: bool(
            sleep_fixture.get_time_slept() >= 1.234
        )
        with pytest.raises(StopTapperActionError):
            sleep_fixture.sleep(10)
        assert sleep_fixture.get_time_slept() == pytest.approx(1.234, abs=0.01)
        assert len(sleep_fixture.processor.kill_check_fn.call_args_list) >= 123


class TestSleepPause:
    def test_killed_while_paused(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.pause_check_fn.return_value = True
        sleep_fixture.processor.kill_check_fn.side_effect = [False, False, True]
        with pytest.raises(StopTapperActionError):
            sleep_fixture.sleep(1)

    def test_time_slept_extends_with_pause(self, sleep_fixture: SleepFixture) -> None:
        sleep_fixture.processor.check_interval = 0.1
        sleep_fixture.processor.pause_check_fn.side_effect = lambda: bool(
            1 <= sleep_fixture.get_time_slept() <= 8
        )
        sleep_fixture.sleep(10)
        assert sleep_fixture.get_time_slept() == pytest.approx(17, abs=0.2)
