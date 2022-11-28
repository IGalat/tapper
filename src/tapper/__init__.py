from tapper.model import tap_tree

_stub = object()  # will be removed when this file is implemented


def _stub_fn() -> None:  # will be removed when this file is implemented
    pass


Tap = tap_tree.Tap
"""Trigger-action plan. Main part of this library. Allows setting hotkeys."""

Group = tap_tree.Group
"""Group of Taps, and/or other Groups."""

root = _stub
"""Root group, the parent to all except control group."""

control_group = _stub
"""
A special group, intended to control the flow of tapper - pause, shutdown, reboot.
Actions of this group have a dedicated executor, to avoid being blocked by other running actions.
It has the highest priority of triggering, before the root group.
If user doesn't add any controls, default ones will be added on init.
"""

send = _stub_fn
"""A versatile command, allows sending many instructions in one str."""

kb = _stub
"""Keyboard controller. Mainly useful for getting the state of keys, send is recommended for typing."""

mouse = _stub
"""Mouse controller."""


def init() -> None:
    """Initializes all underlying tools."""


def start() -> None:
    """
    Initializes all underlying tools, and starts listeners.
    This method is blocking, it should be the last in your script.
    """
