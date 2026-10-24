import functools
import logging
import time
from dataclasses import dataclass
from typing import Callable
from unittest.mock import MagicMock

import pytest

from tapper import config
from tapper.boot import initializer
from tapper.boot import platforms
from tapper.boot.initializer import Runtime
from tapper.boot.platforms import Platform
from tapper.controller import flow_control
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.window.window_api import WindowController
from tapper.model import constants
from tapper.model.constants import Aspect
from tapper.model.tap_tree import Group
from tapper.signal.base_listener import SignalListener
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.signal.mouse.mouse_listener import MouseSignalListener
from testutil_model import Dummy


@dataclass
class KeyboardOnly:
    """Tapper initialized on an OS that implements only the keyboard."""

    runtime: Runtime
    listener: SignalListener
    kbc: KeyboardController
    kb_driver: object


@pytest.fixture
def keyboard_only(
    monkeypatch: pytest.MonkeyPatch, make_group: Callable[[str], Group], dummy: Dummy
) -> KeyboardOnly:
    listener = dummy.Listener()
    kb_driver = dummy.KbDriver(listener, [])
    platform = Platform(
        listeners={Aspect.keyboard: lambda: listener},
        drivers={Aspect.keyboard: lambda: kb_driver},
    )
    monkeypatch.setitem(platforms.by_os, constants.OS.dummy, lambda: platform)
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
        SendCommandProcessor(),
        SleepCommandProcessor(),
    )
    return KeyboardOnly(runtime, listener, kbc, kb_driver)


def test_init_skips_components_not_implemented_for_os(
    keyboard_only: KeyboardOnly,
) -> None:
    assert keyboard_only.runtime.listeners == [keyboard_only.listener]
    assert keyboard_only.runtime.controllers == [keyboard_only.kbc]
    assert keyboard_only.kbc._driver is keyboard_only.kb_driver


def test_stop_stops_listeners(keyboard_only: KeyboardOnly) -> None:
    keyboard_only.listener.stop = MagicMock()
    initializer.stop(keyboard_only.runtime)
    keyboard_only.listener.stop.assert_called_once()


def test_stop_kills_running_actions(keyboard_only: KeyboardOnly) -> None:
    kill_id_before = flow_control.kill_id
    initializer.stop(keyboard_only.runtime)
    assert flow_control.kill_id != kill_id_before


def test_stop_rejects_new_actions(keyboard_only: KeyboardOnly) -> None:
    initializer.stop(keyboard_only.runtime)
    with pytest.raises(RuntimeError):
        keyboard_only.runtime.runner.run(lambda: None)


def test_stop_reports_actions_still_running(
    keyboard_only: KeyboardOnly,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(initializer, "STOP_TIMEOUT", 0.01)
    keyboard_only.runtime.runner.run(functools.partial(time.sleep, 0.2))
    with caplog.at_level(logging.WARNING, logger="tapper"):
        initializer.stop(keyboard_only.runtime)
    assert "1 action(s) still running" in caplog.text
