from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.model import keyboard
from tapper.util import datastructs
from winput import winput

symbol_code_map = datastructs.symbols_to_codes(
    keyboard.win32_vk_code_to_symbol_map, keyboard.aliases
)

user32 = winput.user32


def key_state(code: int) -> int:
    return user32.GetKeyState(code)


class Win32KeyboardTrackerCommander(KeyboardTracker, KeyboardCommander):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        winput.press_key(symbol_code_map[symbol][0])

    def release(self, symbol: str) -> None:
        winput.release_key(symbol_code_map[symbol][0])

    def pressed(self, symbol: str) -> bool:
        return any(key_state(code) >> 15 == 1 for code in symbol_code_map[symbol])

    def toggled(self, symbol: str) -> bool:
        return any(key_state(code) & 1 == 1 for code in symbol_code_map[symbol])
