"""All mouse buttons"""
from functools import cache

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

aliases = {
    "lmb": ["left_mouse_button"],
    "rmb": ["right_mouse_button"],
    "mmb": ["middle_mouse_button"],
    "x1m": ["x1_mouse_button"],
    "x2mb": ["x2_mouse_button"],
    # wheel
    "wheel_up": ["scroll_wheel_up"],
    "wheel_down": ["scroll_wheel_down"],
    "wheel_left": ["scroll_wheel_left"],
    "wheel_right": ["scroll_wheel_right"],
    "scroll_up": ["scroll_wheel_up"],
    "scroll_down": ["scroll_wheel_down"],
    "scroll_left": ["scroll_wheel_left"],
    "scroll_right": ["scroll_wheel_right"],
}


@cache
def get_key_list() -> list[str]:
    """All mouse buttons, BUT no aliases"""
    return [*regular_buttons, *wheel_buttons]


@cache
def get_keys() -> dict[str, list[str] | None]:
    """All mouse buttons and aliases.

    Only aliases value is not None but a list of non-alias keys."""
    all_keys = dict.fromkeys(get_key_list(), None)
    all_keys.update(aliases)
    return all_keys
