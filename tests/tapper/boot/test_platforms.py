import sys

import pytest

from tapper.boot import platforms
from tapper.controller.keyboard.kb_api import KeyboardDriver
from tapper.model import constants


@pytest.mark.skipif(
    sys.platform not in (constants.OS.win32, constants.OS.linux), reason="no adapters"
)
def test_this_os_has_keyboard() -> None:
    platform = platforms.for_os(sys.platform)
    assert constants.Aspect.keyboard in platform.listeners
    assert isinstance(platform.drivers[constants.Aspect.keyboard](), KeyboardDriver)
