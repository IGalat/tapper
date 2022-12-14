"""See config.tree_possible_kwargs for docs."""
from functools import partial
from typing import Any
from typing import Callable

from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController


def generic() -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    kwargs["trigger_if"] = lambda fn: fn()
    return kwargs


def keyboard(controller: KeyboardController) -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    if not controller:
        return kwargs

    kwargs["toggled_on"] = controller.toggled
    kwargs["toggled_off"] = lambda symbol: not controller.toggled(symbol)

    kwargs["kb_key_pressed"] = controller.pressed
    kwargs["kb_key_not_pressed"] = lambda symbol: not controller.pressed(symbol)

    return kwargs


def mouse(controller: MouseController) -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    if not controller:
        return kwargs

    kwargs["mouse_key_pressed"] = controller.pressed
    kwargs["mouse_key_not_pressed"] = lambda symbol: not controller.pressed(symbol)

    def is_cursor_near(target_xy_precision: tuple[tuple[int, int], int]) -> bool:
        """Circle with "precision" radius."""
        target_xy, precision = target_xy_precision
        target_x, target_y = target_xy
        x, y = controller.get_pos()
        return (x - target_x) ** 2 + (y - target_y) ** 2 <= precision**2

    kwargs["cursor_near"] = partial(is_cursor_near)

    def is_cursor_in_rect(
        up_down_coords: tuple[tuple[int, int], tuple[int, int]]
    ) -> bool:
        xy1, xy2 = up_down_coords
        x1, y1 = xy1
        x2, y2 = xy2
        x, y = controller.get_pos()
        return x1 <= x <= x2 and y1 <= y <= y2

    kwargs["cursor_in"] = is_cursor_in_rect

    return kwargs
