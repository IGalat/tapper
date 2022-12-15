from typing import Optional

from tapper.controller.mouse.mouse_api import MouseCommander
from tapper.controller.mouse.mouse_api import MouseTracker
from tapper.model import mouse
from tapper.util import datastructs
from tapper.validation import report
from winput import winput

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


def button_state(symbol: str) -> int:
    return user32.GetKeyState(symbol_button_map[symbol])


class Win32MouseTrackerCommander(MouseTracker, MouseCommander):
    def start(self) -> None:
        winput.set_DPI_aware(per_monitor=True)

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        try:
            winput.press_mouse_button(symbol_button_map[symbol])
        except KeyError:
            amount, horizontal = symbol_wheel_map[symbol]
            winput.move_mousewheel(amount, horizontal)

    def release(self, symbol: str) -> None:
        try:
            winput.release_mouse_button(symbol_button_map[symbol])
        except KeyError:
            if symbol not in symbol_wheel_map:
                raise KeyError

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

    def pressed(self, symbol: str) -> bool:
        return button_state(symbol) >> 15 == 1

    def toggled(self, symbol: str) -> bool:
        return button_state(symbol) & 1 == 1

    def get_pos(self) -> tuple[int, int]:
        return winput.get_mouse_pos()