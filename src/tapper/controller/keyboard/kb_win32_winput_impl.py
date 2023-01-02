import sys

import win32con
import win32gui
from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.model import keyboard
from tapper.model import languages
from tapper.model.languages import Lang
from tapper.util import datastructs
from winput import winput

keys_wo_upper = {
    k: v
    for k, v in keyboard.get_keys(sys.platform).items()
    if k not in keyboard.chars_en_upper
}

symbol_code_map = datastructs.symbols_to_codes(
    keyboard.win32_vk_code_to_symbol_map, keys_wo_upper  # type: ignore
)

user32 = winput.user32


change_lang = lambda hwnd, locale_id: win32gui.PostMessage(
    hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, locale_id
)

change_lang_system_wide = lambda locale_id: win32gui.PostMessage(
    win32con.HWND_BROADCAST, win32con.WM_INPUTLANGCHANGEREQUEST, 0, locale_id
)


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

    def lang(self, lang: str | int | Lang | None = None) -> None:
        curr_window = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
        locale_id = user32.GetKeyboardLayout(thread_id) & (2**16 - 1)
        actual = languages.get(locale_id)
        if lang:
            return actual if actual == languages.get(lang) else None
        else:
            return actual

    def pressed(self, symbol: str) -> bool:
        return any(key_state(code) >> 15 == 1 for code in symbol_code_map[symbol])  # type: ignore

    def toggled(self, symbol: str) -> bool:
        return any(key_state(code) & 1 == 1 for code in symbol_code_map[symbol])  # type: ignore

    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
        target_locale = languages.get(lang).locale_id
        if system_wide:
            change_lang_system_wide(target_locale)
        else:
            change_lang(user32.GetForegroundWindow(), target_locale)
