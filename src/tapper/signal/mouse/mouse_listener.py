from abc import ABC
from typing import Callable

from tapper.model import constants
from tapper.model import mouse
from tapper.signal import base_listener


class MouseSignalListener(base_listener.SignalListener, ABC):
    """Listens to mouse button presses and releases, and movement.
    See SignalListener for listener documentation.

    Mouse move and wheel scroll are on_signal(symbol, down=True)
    """

    @property
    def name(self) -> str:
        return "mouse"

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        temp: list[str] = mouse.get_key_list()
        return temp

    @staticmethod
    def get_for_os(os: str) -> "MouseSignalListener | None":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of MouseSignalListener.
        """
        get_impl = _os_impl_list.get(os)
        return get_impl()() if get_impl else None


def _get_win32_impl() -> type[MouseSignalListener]:
    from tapper.signal.mouse import win32_mouse_listener

    return win32_mouse_listener.Win32MouseSignalListener


_os_impl_list: dict[str, Callable[[], type[MouseSignalListener]]] = {
    constants.OS.win32: _get_win32_impl
}
