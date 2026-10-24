from winput import winput

from tapper.controller.mouse.mouse_api import MouseDriver
from tapper.controller.mouse.mouse_api import calc_move
from tapper.model import mouse
from tapper.util import datastructs

"""Winput wheel scroll argument values."""
win32_wheel_code_symbol_map: dict[tuple[int, bool], str] = {
    (1, False): "scroll_wheel_up",
    (-1, False): "scroll_wheel_down",
    (-1, True): "scroll_wheel_left",
    (1, True): "scroll_wheel_right",
}

mouse_buttons_w_aliases = {
    **mouse.button_aliases,
    **{b: [b] for b in mouse.regular_buttons},
}

symbol_button_map = datastructs.symbols_to_codes(
    mouse.win32_button_code_symbol_map,
    mouse_buttons_w_aliases,
)

wheel_w_aliases = {**mouse.wheel_aliases, **{b: [b] for b in mouse.wheel_buttons}}

symbol_wheel_map = datastructs.symbols_to_codes(
    win32_wheel_code_symbol_map,
    wheel_w_aliases,
)

user32 = winput.user32


def button_state(code: int) -> int:
    return user32.GetKeyState(code)


class Win32MouseDriver(MouseDriver):
    def start(self) -> None:
        winput.set_DPI_aware(per_monitor=True)

    def stop(self) -> None:
        pass

    def press(self, symbol: str) -> None:
        try:
            winput.press_mouse_button(symbol_button_map[symbol][0])
        except KeyError:
            amount, horizontal = symbol_wheel_map[symbol][0]
            winput.move_mousewheel(amount, horizontal)

    def release(self, symbol: str) -> None:
        try:
            winput.release_mouse_button(symbol_button_map[symbol][0])
        except KeyError:
            if symbol not in symbol_wheel_map:
                raise KeyError(symbol) from None

    def move(
        self, x: int | None = None, y: int | None = None, relative: bool = False
    ) -> None:
        if relative:
            winput.move_mouse(x or 0, y or 0)
        else:
            winput.set_mouse_pos(*calc_move(self.get_pos, x, y, False))

    def pressed(self, symbol: str) -> bool:
        return any(button_state(code) >> 15 == 1 for code in symbol_button_map[symbol])

    def toggled(self, symbol: str) -> bool:
        return any(button_state(code) & 1 == 1 for code in symbol_button_map[symbol])

    def get_pos(self) -> tuple[int, int]:
        return winput.get_mouse_pos()
