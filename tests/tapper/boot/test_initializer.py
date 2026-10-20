from typing import Callable

import pytest

from tapper import config
from tapper.boot import initializer
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.window.window_api import WindowController
from tapper.model.tap_tree import Group
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.signal.mouse.mouse_listener import MouseSignalListener
from testutil_model import Dummy


def test_init_skips_components_not_implemented_for_os(
    monkeypatch: pytest.MonkeyPatch, make_group: Callable[[str], Group], dummy: Dummy
) -> None:
    injected_kbc = KeyboardController()
    kb_tc = dummy.KbTC(dummy.Listener(), [])
    injected_kbc._tracker, injected_kbc._commander = kb_tc, kb_tc

    monkeypatch.setattr(config, "os", "dummy")
    monkeypatch.setattr(config, "tapper_logging_config", False)
    monkeypatch.setattr(
        config,
        "listeners",
        [KeyboardSignalListener, MouseSignalListener, dummy.Listener],
    )
    monkeypatch.setattr(
        config,
        "controllers",
        [KeyboardController(), MouseController(), WindowController(), injected_kbc],
    )

    runtime = initializer.init(
        make_group("root"),
        make_group("control"),
        SendCommandProcessor.from_none(),
        SleepCommandProcessor.from_none(),
    )

    assert len(runtime.listeners) == 1
    assert type(runtime.listeners[0]) is dummy.Listener
    assert runtime.controllers == [injected_kbc]
