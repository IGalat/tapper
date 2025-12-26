import sys
from typing import Callable
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import tapper.config
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.model.tap_tree import Group
from testutil_model import Dummy
from testutil_model import FakeClock
from testutil_model import SleepFixture


@pytest.fixture
def dummy() -> Dummy:
    return Dummy()


@pytest.fixture
def make_group() -> Callable[[str], Group]:
    return lambda name: Group(
        name,
        executor=0,
        suppress_trigger=True,
        send_interval=0,
        send_press_duration=0,
    )


@pytest.fixture
def is_debug() -> bool:
    return hasattr(sys, "gettrace") and (sys.gettrace() is not None)


@pytest.fixture(autouse=True)
def disable_file_logs() -> None:
    tapper.config.log_level_file = None


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


@pytest.fixture
def mock_sleep(sleep_fixture: SleepFixture) -> None:
    with patch("tapper.sleep", new=sleep_fixture.sleep):
        yield


@pytest.fixture
def fake_perf_counter():
    fake = FakeClock()
    with patch("time.perf_counter", new=fake):
        yield fake
