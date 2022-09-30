from abc import ABC
from functools import cache

from tapper.model import constants
from tapper.model import mouse
from tapper.signal import base_signal_listener


class MouseSignalListener(base_signal_listener.SignalListener, ABC):
    """Listens to mouse button presses and releases, and movement.
    See SignalListener for listener documentation.

    Mouse move and wheel scroll are on_signal(symbol, down=True)
    """

    def get_possible_signal_symbols(self) -> list[str]:
        temp: list[str] = mouse.get_key_list()
        return temp


@cache
def get_for_os(os: str) -> MouseSignalListener:
    """
    :param os: Result of sys.platform() call.
    :return: Per-OS implementation of MouseSignalListener.
    """
    if os == constants.os.win32:
        from tapper.signal.mouse import win32_mouse_listener

        temp: MouseSignalListener = win32_mouse_listener.Win32MouseSignalListener()
        return temp
    else:
        raise NotImplementedError
