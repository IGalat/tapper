from abc import ABC
from typing import Callable

from tapper.model import constants
from tapper.signal import base_listener


class KeyboardSignalListener(base_listener.SignalListener, ABC):
    """Listens to keyboard key presses and releases.
    See SignalListener for listener documentation."""

    name = "keyboard"

    @staticmethod
    def get_for_os(os: str) -> "KeyboardSignalListener":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of KeyboardSignalListener.
        """
        return _os_impl_list[os]()()


def _get_win32_impl() -> type[KeyboardSignalListener]:
    from tapper.signal.keyboard import win32_kb_listener

    return win32_kb_listener.Win32KeyboardSignalListener


def _get_linux_impl() -> type[KeyboardSignalListener]:
    from tapper.signal.keyboard import linux_kb_listener

    return linux_kb_listener.LinuxKeyboardSignalListener


_os_impl_list: dict[str, Callable[[], type[KeyboardSignalListener]]] = {
    constants.OS.win32: _get_win32_impl,
    constants.OS.linux: _get_linux_impl,
}
