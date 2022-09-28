from abc import ABC
from functools import cache

from tapper.model import keyboard
from tapper.signal.listener import base_signal_listener


class KeyboardSignalListener(base_signal_listener.SignalListener, ABC):
    """Listens to keyboard key presses and releases.
    See SignalListener for listener documentation."""

    def get_possible_signal_symbols(self) -> list[str]:
        temp: list[str] = keyboard.get_key_list()  # pls mypy chill
        return temp


@cache
def get_os_keyboard_signal_listener(os: str) -> KeyboardSignalListener:
    """
    :param os: Result of sys.platform() call.
    :return: Per-OS implementation of KeyboardSignalListener. Singleton.
    """
    if os == "win32":
        from tapper.signal.listener.keyboard import win32_kb_listener

        temp: KeyboardSignalListener = win32_kb_listener.Win32KeyboardSignalListener()
        return temp
    else:
        raise NotImplementedError
