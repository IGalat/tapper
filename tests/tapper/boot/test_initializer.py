from typing import Callable

import pytest

from tapper import config
from tapper.boot import initializer
from tapper.boot import platforms
from tapper.boot.platforms import Platform
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.window.window_api import WindowController
from tapper.model import constants
from tapper.model.constants import Aspect
from tapper.model.tap_tree import Group
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.signal.mouse.mouse_listener import MouseSignalListener
from testutil_model import Dummy


def test_init_skips_components_not_implemented_for_os(
    monkeypatch: pytest.MonkeyPatch, make_group: Callable[[str], Group], dummy: Dummy
) -> None:
    listener = dummy.Listener()
    kb_driver = dummy.KbDriver(listener, [])
    keyboard_only = Platform(
        listeners={Aspect.keyboard: lambda: listener},
        drivers={Aspect.keyboard: lambda: kb_driver},
    )
    monkeypatch.setitem(platforms.by_os, constants.OS.dummy, lambda: keyboard_only)
    monkeypatch.setattr(config, "os", constants.OS.dummy)
    monkeypatch.setattr(config, "tapper_logging_config", False)
    monkeypatch.setattr(
        config, "listeners", [KeyboardSignalListener, MouseSignalListener]
    )
    kbc = KeyboardController()
    monkeypatch.setattr(
        config, "controllers", [kbc, MouseController(), WindowController()]
    )

    runtime = initializer.init(
        make_group("root"),
        make_group("control"),
        SendCommandProcessor.from_none(),
        SleepCommandProcessor.from_none(),
    )

    assert runtime.listeners == [listener]
    assert runtime.controllers == [kbc]
    assert kbc._driver is kb_driver
