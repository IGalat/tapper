import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.model import constants
from tapper.state import keeper


def test_press_alias_is_recorded_as_emulated_non_alias() -> None:
    kb = KeyboardController()
    kb._init(MagicMock())
    kb._emul_keeper = keeper.Emul()

    kb.press("rctrl")
    assert kb._emul_keeper.is_emulated(("right_control", constants.KeyDirBool.DOWN))


@pytest.mark.skipif(sys.platform != constants.OS.linux, reason="imports evdev")
def test_linux_pressed_multi_key_alias_sees_second_key() -> None:
    from tapper.controller.keyboard.kb_linux_evdev_impl import LinuxKeyboardDriver
    from tapper.controller.keyboard.kb_linux_evdev_impl import symbol_code_map

    driver = LinuxKeyboardDriver()
    right_control_code = symbol_code_map["right_control"][0]
    driver.real_kbs = [SimpleNamespace(active_keys=lambda: [right_control_code])]
    assert driver.pressed("ctrl")
