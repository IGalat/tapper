from abc import ABC

from tapper.model import constants
from tapper.model import mouse
from tapper.signal import base_signal_listener


class MouseSignalListener(base_signal_listener.SignalListener, ABC):
    """Listens to mouse button presses and releases, and movement.
    See SignalListener for listener documentation.

    Mouse move and wheel scroll are on_signal(symbol, down=True)
    """

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        temp: list[str] = mouse.get_key_list()
        return temp

    @staticmethod
    def get_for_os(os: str) -> "MouseSignalListener":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of MouseSignalListener.
        """
        return _os_impl_list[os]()()


def _get_win32_impl() -> type[MouseSignalListener]:
    from tapper.signal.mouse import win32_mouse_listener

    return win32_mouse_listener.Win32MouseSignalListener


_os_impl_list = {constants.os.win32: _get_win32_impl}
