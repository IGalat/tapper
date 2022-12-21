import time
from functools import partial
from typing import Any
from typing import Callable

from tapper.helper import _util
from tapper.helper._util import repeater


def repeat_while(
    condition: Callable[[], Any],
    action: Callable[[], Any],
    period_s: float = 0.1,
    max_repeats: int | None = None,
) -> Callable[[], None]:
    """Repeats an action while condition applies."""
    max_repeats_int = max_repeats or 999999999999999

    def fn() -> None:
        for _ in range(max_repeats_int):
            if not bool(condition()):
                break
            action()
            time.sleep(period_s)

    return fn


def toggle_repeat(
    action: Callable[[], Any], period_s: float = 0.1, max_repeats: int | None = None
) -> Callable[[], None]:
    """
    When toggled, starts repeating the action until toggled again.

    Notes:
        - runs in one separate thread, so cannot launch multiple toggle_repeats
        - execution is immediately overridden by triggering another toggle_repeat
        - execution immediately stops on second toggle

    :param action: what to repeat
    :param period_s: how often to repeat, seconds
    :param max_repeats: optional limit
    :return: callable toggle, to be set into a Tap
    """
    max_repeats_int = max_repeats or 999999999999999
    repeater.registered_repeatables[action] = period_s, max_repeats_int
    return partial(_util.repeater.toggle_repeatable, action)
