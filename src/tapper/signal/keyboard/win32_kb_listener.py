from typing import Final

from tapper.model import constants
from tapper.model import keyboard
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from winput import winput

WINPUT_PROPAGATE: Final[int] = 0
WINPUT_SUPPRESS: Final[int] = 4

EVENT_PRESS: Final[set[int]] = {256, 260}
EVENT_RELEASE: Final[set[int]] = {257, 261}


def to_callback_result(inner_func_result: bool) -> int:
    if inner_func_result:
        return WINPUT_PROPAGATE
    else:
        return WINPUT_SUPPRESS


class Win32KeyboardSignalListener(KeyboardSignalListener):
    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        return keyboard.get_key_list(constants.OS.win32)

    def start(self) -> None:
        winput.set_DPI_aware(True)
        winput.hook_keyboard(self.keyboard_callback)
        winput.wait_messages()

    def stop(self) -> None:
        winput.stop()
        winput.unhook_keyboard()

    def keyboard_callback(self, event: winput.KeyboardEvent) -> int:
        key = keyboard.win32_vk_code_to_symbol_map[event.key]
        if event.action in EVENT_PRESS:
            return to_callback_result(self.on_signal((key, True)))
        elif event.action in EVENT_RELEASE:
            return to_callback_result(self.on_signal((key, False)))
        else:
            return WINPUT_PROPAGATE
