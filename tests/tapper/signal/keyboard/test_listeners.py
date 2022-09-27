import functools
import sys

import pytest
from tapper.signal.listener.keyboard import keyboard_listener


@pytest.mark.skipif(sys.platform != "win32", reason="")
class TestWin32Listener:
    get_listener = functools.partial(
        keyboard_listener.get_os_keyboard_signal_listener, "win32"
    )

    def test_factory_is_singleton(self) -> None:
        assert self.get_listener() is self.get_listener()

    # def test_all_keys_with_suppression(self) -> None:
