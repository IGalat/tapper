import sys

import win32con
import win32gui
from winput import winput

from tapper.controller.keyboard.kb_api import KeyboardDriver
from tapper.model import keyboard
from tapper.model import languages
from tapper.model.languages import Lang
from tapper.util import datastructs

keys_wo_upper = {
    k: v
    for k, v in keyboard.get_keys(sys.platform).items()
    if k not in keyboard.chars_en_upper
}

symbol_code_map = datastructs.symbols_to_codes(
    keyboard.win32_vk_code_to_symbol_map,
    keys_wo_upper,
)

user32 = winput.user32


def change_lang(hwnd: int, locale_id: int) -> None:
    win32gui.PostMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, locale_id)


def change_lang_system_wide(locale_id: int) -> None:
    win32gui.PostMessage(
        win32con.HWND_BROADCAST, win32con.WM_INPUTLANGCHANGEREQUEST, 0, locale_id
    )


def key_state(code: int) -> int:
    return user32.GetKeyState(code)


class Win32KeyboardDriver(KeyboardDriver):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        winput.press_key(symbol_code_map[symbol][0])

    def release(self, symbol: str) -> None:
        winput.release_key(symbol_code_map[symbol][0])

    def lang(self, lang: str | int | Lang | None = None) -> Lang | None:
        curr_window = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
        locale_id = user32.GetKeyboardLayout(thread_id) & (2**16 - 1)
        actual = languages.get(locale_id)
        if lang:
            return actual if actual == languages.get(lang) else None
        else:
            return actual

    def pressed(self, symbol: str) -> bool:
        return any(key_state(code) >> 15 == 1 for code in symbol_code_map[symbol])

    def toggled(self, symbol: str) -> bool:
        return any(key_state(code) & 1 == 1 for code in symbol_code_map[symbol])

    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
        target_locale = languages.get(lang).locale_id
        if system_wide:
            change_lang_system_wide(target_locale)
        else:
            change_lang(user32.GetForegroundWindow(), target_locale)
