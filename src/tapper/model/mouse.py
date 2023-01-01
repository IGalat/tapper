"""All mouse buttons"""
from functools import cache

from tapper.model.types_ import SymbolsWithAliases

regular_buttons = [
    "left_mouse_button",
    "right_mouse_button",
    "middle_mouse_button",
    "x1_mouse_button",
    "x2_mouse_button",
]

wheel_buttons = [
    "scroll_wheel_up",
    "scroll_wheel_down",
    "scroll_wheel_left",
    "scroll_wheel_right",
]

button_aliases: SymbolsWithAliases = {
    "lmb": ["left_mouse_button"],
    "rmb": ["right_mouse_button"],
    "mmb": ["middle_mouse_button"],
    "x1mb": ["x1_mouse_button"],
    "x2mb": ["x2_mouse_button"],
}

wheel_aliases: SymbolsWithAliases = {
    "wheel_up": ["scroll_wheel_up"],
    "wheel_down": ["scroll_wheel_down"],
    "wheel_left": ["scroll_wheel_left"],
    "wheel_right": ["scroll_wheel_right"],
    "scroll_up": ["scroll_wheel_up"],
    "scroll_down": ["scroll_wheel_down"],
    "scroll_left": ["scroll_wheel_left"],
    "scroll_right": ["scroll_wheel_right"],
}

aliases: SymbolsWithAliases = {**button_aliases, **wheel_aliases}


@cache
def get_key_list() -> list[str]:
    """All mouse buttons, BUT no aliases"""
    return [*regular_buttons, *wheel_buttons]


@cache
def get_keys() -> SymbolsWithAliases:
    """All mouse buttons and aliases.

    Non-aliases value is list of one item: themselves.
    Aliases value is a list of non-alias keys.
    """
    all_keys = {key: [key] for key in get_key_list()}
    all_keys.update(aliases)
    return all_keys


"""Win codes of button codes (not mouse wheel), and corresponding symbols."""
win32_button_code_symbol_map: dict[int, str] = {
    1: "left_mouse_button",
    4: "right_mouse_button",
    2: "middle_mouse_button",
    8: "x1_mouse_button",
    16: "x2_mouse_button",
}

"""Evdev (type, code)."""
linux_evdev_code_button_map: dict[int, str] = {
    272: "left_mouse_button",
    273: "right_mouse_button",
    274: "middle_mouse_button",
    # hope these are correct, no way to check
    275: "x1_mouse_button",
    276: "x2_mouse_button",
}

"""Evdev (type, code)."""
linux_evdev_code_wheel_map: dict[tuple[int, int, int], str] = {
    (2, 8, 1): "scroll_wheel_up",
    (2, 8, -1): "scroll_wheel_down",
}
