import random
import sys
from functools import partial

import pytest
from tapper.model import constants
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.constants import WinputListenerResult
from tapper.model.types_ import Signal
from tapper.signal.mouse.mouse_listener import MouseSignalListener


@pytest.mark.skipif(sys.platform != constants.OS.win32, reason="")
class TestWin32Listener:
    get_listener: MouseSignalListener = partial(
        MouseSignalListener.get_for_os, sys.platform
    )

    def assert_result(
        self,
        expected_signal: Signal,
        callback_result: int,
        actual_signal: Signal,
        event_action: int,
        event_add: int | None = None,
    ) -> None:
        pass

    def test_all_keys(self) -> None:
        from tapper.signal.mouse import win32_mouse_listener
        from winput import MouseEvent

        listener: win32_mouse_listener.Win32MouseSignalListener = self.get_listener()

        last_signal: Signal | None = None
        callback_result: int = 4

        def on_signal(signal: Signal) -> ListenerResult:
            nonlocal last_signal
            nonlocal callback_result
            last_signal = signal
            random_result = random.choice(
                [ListenerResult.SUPPRESS, ListenerResult.PROPAGATE]
            )
            callback_result = WinputListenerResult[random_result]
            return random_result

        listener.on_signal = on_signal

        event = lambda action, add: MouseEvent((0, 0), action, 0, add)

        result = listener.mouse_callback(event(522, 1))
        assert last_signal == ("scroll_wheel_up", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(522, -1))
        assert last_signal == ("scroll_wheel_down", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(513, None))
        assert last_signal == ("left_mouse_button", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(514, None))
        assert last_signal == ("left_mouse_button", KeyDirBool.UP)
        assert result == callback_result

        result = listener.mouse_callback(event(516, None))
        assert last_signal == ("right_mouse_button", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(517, None))
        assert last_signal == ("right_mouse_button", KeyDirBool.UP)
        assert result == callback_result

        result = listener.mouse_callback(event(519, None))
        assert last_signal == ("middle_mouse_button", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(520, None))
        assert last_signal == ("middle_mouse_button", KeyDirBool.UP)
        assert result == callback_result

        result = listener.mouse_callback(event(523, 1))
        assert last_signal == ("x1_mouse_button", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(524, 1))
        assert last_signal == ("x1_mouse_button", KeyDirBool.UP)
        assert result == callback_result

        result = listener.mouse_callback(event(523, 2))
        assert last_signal == ("x2_mouse_button", KeyDirBool.DOWN)
        assert result == callback_result

        result = listener.mouse_callback(event(524, 2))
        assert last_signal == ("x2_mouse_button", KeyDirBool.UP)
        assert result == callback_result
