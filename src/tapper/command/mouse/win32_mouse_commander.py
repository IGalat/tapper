from typing import Optional

import winput
from tapper.command.mouse import mouse_commander
from tapper.model import mouse
from tapper.util import datastructs
from tapper.validation import report

"""Winput wheel scroll argument values."""
win32_wheel_code_symbol_map: dict[tuple[int, bool], str] = {
    (1, False): "scroll_wheel_up",
    (-1, False): "scroll_wheel_down",
    (-1, True): "scroll_wheel_left",
    (1, True): "scroll_wheel_right",
}

symbol_button_map = datastructs.symbols_to_codes(
    mouse.win32_button_code_symbol_map, mouse.button_aliases
)

symbol_wheel_map = datastructs.symbols_to_codes(
    win32_wheel_code_symbol_map, mouse.wheel_aliases
)

user32 = winput.user32


class Win32MouseCommander(mouse_commander.MouseCommander):
    def start(self) -> None:
        print("Starting Win32MouseCommander")
        winput.set_DPI_aware(per_monitor=True)

    def press(self, symbol: str) -> None:
        try:
            winput.press_mouse_button(symbol_button_map[symbol])
        except KeyError:
            amount, horizontal = symbol_wheel_map[symbol]
            self.scroll_wheel(amount, horizontal)

    def release(self, symbol: str) -> None:
        try:
            winput.release_mouse_button(symbol_button_map[symbol])
        except KeyError:
            if symbol not in symbol_wheel_map:
                raise KeyError

    def scroll_wheel(self, amount: int, horizontal: bool = False) -> None:
        winput.move_mousewheel(amount, horizontal)

    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        if x is None and y is None:
            report.error("Win32MouseCommander move with no coordinates specified.")

        if not relative:
            if x is None:
                x = self.get_pos()[0]
            elif y is None:
                y = self.get_pos()[1]
        else:  # winput.move_mouse (relative) is bugged, so calculate here and absolute move
            current_x, current_y = self.get_pos()
            if x is None:
                x = current_x
            else:
                x += current_x
            if y is None:
                y = current_y
            else:
                y += current_y
        winput.set_mouse_pos(x, y)

    def relative_move(self, dx: Optional[int] = None, dy: Optional[int] = None) -> None:
        if dx is None:
            dx = 0
        elif dy is None:
            dy = 0
        print(f"relative_move {dx=} {dy=}")
        winput.move_mouse(dx, dy)

    def pressed(self, symbol: str) -> bool:
        return self.pressed_toggled(symbol)[0]

    def toggled(self, symbol: str) -> bool:
        return self.pressed_toggled(symbol)[1]

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        key_state = user32.GetKeyState(symbol_button_map[symbol])
        pressed = key_state >> 15 == 1
        toggled = key_state & 1 == 1
        return pressed, toggled

    def get_pos(self) -> tuple[int, int]:
        return winput.get_mouse_pos()
