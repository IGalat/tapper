import time as _time

from tapper import config
from tapper.boot import initializer as _initializer
from tapper.controller.keyboard.kb_api import KeyboardController as _KeyboardController
from tapper.controller.mouse.mouse_api import MouseController as _MouseController
from tapper.controller.send_processor import (
    SendCommandProcessor as _SendCommandProcessor,
)
from tapper.controller.window.window_api import WindowController as _WindowController
from tapper.model import tap_tree as _tap_tree
from tapper.signal.base_listener import SignalListener as _SignalListener
from tapper.util import datastructs as _datastructs

_listeners: list[_SignalListener]

_send_processor = _SendCommandProcessor.from_none()
_initialized = False

Tap = _tap_tree.Tap
"""Trigger-action plan. Main part of this library. Allows setting hotkeys."""

Group = _tap_tree.Group
"""Group of Taps, and/or other Groups."""

root = Group("root")
"""Root group, the parent to all except control group."""

control_group = Group("control_group")
"""
A special group, intended to control the flow of tapper - pause, shutdown, reboot.
Actions of this group have a dedicated executor, to avoid being blocked by other running actions.
It has the highest priority of triggering, before the root group.
If user doesn't add any controls, default ones will be added on init.
"""

send = _send_processor.send
"""A versatile command, allows sending many instructions in one str."""

if _kbc := _datastructs.get_first_in(_KeyboardController, config.controllers):
    """Keyboard controller. Mainly useful for getting the state of keys, send is recommended for typing."""
    kb = _kbc

if _mc := _datastructs.get_first_in(_MouseController, config.controllers):
    """Mouse controller. Primarily for moving the cursor and getting the state."""
    mouse = _mc

if _wc := _datastructs.get_first_in(_WindowController, config.controllers):
    """Window controller. Primarily for moving the cursor and getting the state."""
    window = _wc


def init() -> None:
    """Initializes all underlying tools."""
    global _listeners
    global _initialized
    _listeners = _initializer.init(root, control_group, _send_processor, send)
    _initialized = True


def start(blocking: bool = True) -> None:
    """
    Initializes all underlying tools, and starts listeners.
    No changes by user in any elements of tapper are expected after this command,
    it should be the last in your script.
    """
    global _listeners
    global _initialized

    if not _initialized:
        init()
    _initializer.start(_listeners)

    if blocking:
        while True:
            _time.sleep(1000000)
