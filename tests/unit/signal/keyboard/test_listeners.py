import functools
import sys

import pytest
from tapper.model import constants
from tapper.model import keyboard
from tapper.model.types_ import Signal
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener


@pytest.mark.skipif(sys.platform != constants.OS.win32, reason="")
class TestWin32Listener:
    get_listener: KeyboardSignalListener = functools.partial(
        KeyboardSignalListener.get_for_os, constants.OS.win32
    )

    def test_all_keys(self) -> None:
        from tapper.signal.keyboard import win32_kb_listener
        from winput import KeyboardEvent

        press = list(win32_kb_listener.EVENT_PRESS)[0]
        release = list(win32_kb_listener.EVENT_RELEASE)[0]
        listener: win32_kb_listener.Win32KeyboardSignalListener = self.get_listener()

        last_signal: Signal | None = None
        c: int | None = None

        def on_signal(signal: Signal) -> bool:
            nonlocal last_signal
            last_signal = signal
            return False

        listener.on_signal = on_signal

        for c, symbol_ in keyboard.win32_vk_code_to_symbol_map.items():
            listener.keyboard_callback(KeyboardEvent(vkCode=c, action=press, time=0))
            assert last_signal == (symbol_, True)
            listener.keyboard_callback(KeyboardEvent(vkCode=c, action=release, time=0))
            assert last_signal == (symbol_, False)

        listener.keyboard_callback(KeyboardEvent(vkCode=c, action=12345, time=0))
