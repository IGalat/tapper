from abc import ABC

from tapper.model import constants
from tapper.signal import base_signal_listener


class KeyboardSignalListener(base_signal_listener.SignalListener, ABC):
    """Listens to keyboard key presses and releases.
    See SignalListener for listener documentation."""

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


_os_impl_list = {constants.os.win32: _get_win32_impl}
