from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.model import keyboard
from tapper.util import datastructs
from winput import winput

symbol_code_map = datastructs.symbols_to_codes(
    keyboard.win32_vk_code_to_symbol_map, keyboard.aliases
)

user32 = winput.user32


class Win32KeyboardTrackerCommander(KeyboardTracker, KeyboardCommander):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        winput.press_key(symbol_code_map[symbol])

    def release(self, symbol: str) -> None:
        winput.release_key(symbol_code_map[symbol])

    def pressed(self, symbol: str) -> bool:
        return self.pressed_toggled(symbol)[0]

    def toggled(self, symbol: str) -> bool:
        return self.pressed_toggled(symbol)[1]

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        key_state = user32.GetKeyState(symbol_code_map[symbol])
        pressed = key_state >> 15 == 1
        toggled = key_state & 1 == 1
        return pressed, toggled
