import time as _time

from tapper import config
from tapper.boot import initializer as _initializer
from tapper.command.keyboard.keyboard_commander import (
    KeyboardCmdProxy as _KeyboardCmdProxy,
)
from tapper.command.mouse.mouse_commander import MouseCmdProxy as _MouseCmdProxy
from tapper.command.send_processor import SendCommandProcessor as _SendCommandProcessor
from tapper.model import tap_tree as _tap_tree
from tapper.signal.base_listener import SignalListener as _SignalListener

_listeners: list[_SignalListener]

_send_processor = _SendCommandProcessor.from_none()
_initialized = False

Tap = _tap_tree.Tap
"""Trigger-action plan. Main part of this library. Allows setting hotkeys."""

Group = _tap_tree.Group
"""Group of Taps, and/or other Groups."""

root = Group()
"""Root group, the parent to all except control group."""

control_group = Group()
"""
A special group, intended to control the flow of tapper - pause, shutdown, reboot.
Actions of this group have a dedicated executor, to avoid being blocked by other running actions.
It has the highest priority of triggering, before the root group.
If user doesn't add any controls, default ones will be added on init.
"""

send = _send_processor.send
"""A versatile command, allows sending many instructions in one str."""

kb = _KeyboardCmdProxy()
"""Keyboard commander. Mainly useful for getting the state of keys, send is recommended for typing."""

mouse = _MouseCmdProxy()
"""Mouse commander."""


def init() -> None:
    """Initializes all underlying tools."""
    global _listeners
    global _initialized
    _listeners = _initializer.init(
        root, control_group, _send_processor, kb, mouse, send
    )
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
    _initializer.start([kb, mouse], _listeners)

    if blocking:
        while True:
            _time.sleep(1000000)
