"""See config.tree_possible_kwargs for docs."""
from typing import Any
from typing import Callable

from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.window.window_api import WindowController


def generic() -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    kwargs["trigger_if"] = lambda fn: fn()
    return kwargs


def keyboard(kb_c: KeyboardController) -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    if not kb_c:
        return kwargs

    kwargs["toggled_on"] = kb_c.toggled
    kwargs["toggled_off"] = lambda symbol: not kb_c.toggled(symbol)

    kwargs["kb_key_pressed"] = kb_c.pressed
    kwargs["kb_key_not_pressed"] = lambda symbol: not kb_c.pressed(symbol)

    kwargs["lang"] = kb_c.lang
    kwargs["lang_not"] = lambda lang: kb_c.lang(lang) is None

    return kwargs


def mouse(mouse_c: MouseController) -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    if not mouse_c:
        return kwargs

    kwargs["mouse_key_pressed"] = mouse_c.pressed
    kwargs["mouse_key_not_pressed"] = lambda symbol: not mouse_c.pressed(symbol)

    def is_cursor_near(
        xy_precision: tuple[int, int] | tuple[tuple[int, int], int]
    ) -> bool:
        """
        Circle with "precision" radius.
        Could be supplied ((x, y), precision) or (x, y) with default(50) precision.
        """
        param1, param2 = xy_precision
        if isinstance(param1, tuple):
            return mouse_c.is_near(*param1, precision=param2)
        return mouse_c.is_near(x=param1, y=param2)

    kwargs["cursor_near"] = is_cursor_near
    kwargs["cursor_in"] = lambda bbox: mouse_c.is_in(bbox[0], bbox[1], bbox[2], bbox[3])

    return kwargs


def window(window_c: WindowController) -> dict[str, Callable[[Any], Any]]:
    kwargs: dict[str, Callable[[Any], Any]] = {}
    if not window_c:
        return kwargs

    kwargs["win"] = window_c.active
    kwargs["win_title"] = lambda title: window_c.active(title=title)
    kwargs["win_exec"] = lambda ex: window_c.active(exec=ex, strict=True)

    kwargs["open_win"] = window_c.is_open
    kwargs["open_win_title"] = lambda title: window_c.is_open(title=title)
    kwargs["open_win_exec"] = lambda ex: window_c.is_open(exec=ex, strict=True)

    return kwargs
