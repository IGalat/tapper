"""What each OS implements, by aspect. A missing key means not implemented there."""

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from tapper import config
from tapper.model import constants
from tapper.model.constants import Aspect
from tapper.signal.base_listener import SignalListener


@dataclass(frozen=True)
class Platform:
    listeners: dict[Aspect, Callable[[], SignalListener]] = field(default_factory=dict)
    """SignalListener.name -> listener factory."""
    drivers: dict[Aspect, Callable[[], Any]] = field(default_factory=dict)
    """ResourceController.aspect -> driver factory."""


def win32() -> Platform:
    from tapper.controller.keyboard.kb_win32_winput_impl import Win32KeyboardDriver
    from tapper.controller.mouse.mouse_win32_winput_impl import Win32MouseDriver
    from tapper.controller.window.window_win32_impl import Win32WindowDriver
    from tapper.signal.keyboard.win32_kb_listener import Win32KeyboardSignalListener
    from tapper.signal.mouse.win32_mouse_listener import Win32MouseSignalListener

    return Platform(
        listeners={
            Aspect.keyboard: Win32KeyboardSignalListener,
            Aspect.mouse: Win32MouseSignalListener,
        },
        drivers={
            Aspect.keyboard: Win32KeyboardDriver,
            Aspect.mouse: Win32MouseDriver,
            Aspect.window: lambda: Win32WindowDriver(config.only_visible_windows),
        },
    )


def linux() -> Platform:
    from tapper.controller.keyboard.kb_linux_evdev_impl import LinuxKeyboardDriver
    from tapper.signal.keyboard.linux_kb_listener import LinuxKeyboardSignalListener

    return Platform(
        listeners={Aspect.keyboard: LinuxKeyboardSignalListener},
        drivers={Aspect.keyboard: LinuxKeyboardDriver},
    )


by_os: dict[str, Callable[[], Platform]] = {
    constants.OS.win32: win32,
    constants.OS.linux: linux,
}


def for_os(os: str) -> Platform:
    make = by_os.get(os)
    if not make:
        raise ValueError(f"No adapter exists for this platform '{os}'.")
    return make()
