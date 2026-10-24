import random
import sys

import pytest

from tapper.boot import platforms
from tapper.model import constants
from tapper.model import keyboard
from tapper.model.constants import ListenerResult
from tapper.model.constants import WinputListenerResult
from tapper.model.types_ import Signal
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener


@pytest.mark.skipif(sys.platform != constants.OS.win32, reason="")
class TestWin32Listener:
    def get_listener(self) -> KeyboardSignalListener:
        return platforms.for_os(sys.platform).listeners[constants.Aspect.keyboard]()

    def test_all_keys(self) -> None:
        from winput import KeyboardEvent

        from tapper.signal.keyboard import win32_kb_listener

        press = next(iter(win32_kb_listener.EVENT_PRESS))
        release = next(iter(win32_kb_listener.EVENT_RELEASE))
        listener: win32_kb_listener.Win32KeyboardSignalListener = self.get_listener()

        last_signal: Signal | None = None
        c: int | None = None

        callback_result: int = 4

        def on_signal(signal: Signal) -> bool:
            nonlocal last_signal
            nonlocal callback_result
            last_signal = signal
            result = random.choice([ListenerResult.SUPPRESS, ListenerResult.PROPAGATE])
            callback_result = WinputListenerResult[result]
            return result

        listener.on_signal = on_signal

        for c, symbol_ in keyboard.win32_vk_code_to_symbol_map.items():
            actual_result = listener.keyboard_callback(
                KeyboardEvent(vkCode=c, action=press, time=0)
            )
            assert last_signal == (symbol_, constants.KeyDirBool.DOWN)
            assert callback_result == actual_result
            actual_result = listener.keyboard_callback(
                KeyboardEvent(vkCode=c, action=release, time=0)
            )
            assert last_signal == (symbol_, constants.KeyDirBool.UP)
            assert callback_result == actual_result

        listener.keyboard_callback(KeyboardEvent(vkCode=c, action=12345, time=0))
