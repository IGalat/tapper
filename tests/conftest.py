import sys
from typing import Callable

import pytest
import tapper.config
from tapper.model.tap_tree import Group
from testutil_model import Dummy


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
    tapper.config.loglevel_file = None
