from threading import Thread
from typing import Final

from tapper.feedback.logger import LogExceptions
from tapper.model import constants
from tapper.model import keyboard
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.constants import WinputListenerResult
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from winput import winput

EVENT_PRESS: Final[set[int]] = {256, 260}
EVENT_RELEASE: Final[set[int]] = {257, 261}


class Win32KeyboardSignalListener(KeyboardSignalListener):
    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        return keyboard.get_key_list(constants.OS.win32)

    @LogExceptions()
    def start(self) -> None:
        Thread(target=self.event_loop_start).start()

    @LogExceptions()
    def event_loop_start(self) -> None:
        winput.set_DPI_aware(True)
        winput.hook_keyboard(self.keyboard_callback)
        winput.wait_messages()

    @LogExceptions()
    def stop(self) -> None:
        winput.stop()
        winput.unhook_keyboard()

    @LogExceptions()
    def keyboard_callback(self, event: winput.KeyboardEvent) -> int:
        key = keyboard.win32_vk_code_to_symbol_map.get(event.key, "NONEXISTENT_KEY")
        if event.action in EVENT_PRESS:
            return WinputListenerResult[self.on_signal((key, KeyDirBool.DOWN))]
        elif event.action in EVENT_RELEASE:
            return WinputListenerResult[self.on_signal((key, KeyDirBool.UP))]
        else:
            return WinputListenerResult[ListenerResult.PROPAGATE]
