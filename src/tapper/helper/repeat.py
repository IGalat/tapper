import time
from functools import partial
from typing import Any
from typing import Callable

from tapper.helper._util import repeat_util


def repeat_while(
    condition: Callable[[], Any],
    action: Callable[[], Any],
    period_s: float = 0.1,
    max_repeats: int | None = None,
) -> Callable[[], None]:
    """Repeats an action while condition applies."""

    def fn() -> None:
        for _ in range(max_repeats or 999999999999999):
            if not bool(condition()):
                break
            action()
            time.sleep(period_s)

    return fn


def repeat_while_pressed(
    symbol: str,
    action: Callable[[], Any],
    period_s: float = 0.1,
    max_repeats: int | None = None,
) -> Callable[[], None]:
    """
    Repeats action in a separate thread until key is released.

    Warning: if key up is suppressed (used in another Tap), action will be
    repeated forever(or until overridden by another toggle_repeat or repeat_while_pressed)
    """

    repeat_util.registered_repeatables[action] = (
        period_s,
        max_repeats or 999999999999999,
    )
    return partial(repeat_util.while_pressed, symbol, action)


def toggle_repeat(
    action: Callable[[], Any], period_s: float = 0.1, max_repeats: int | None = None
) -> Callable[[], None]:
    """
    When toggled, starts repeating the action until toggled again.

    Notes:
        - runs in one separate thread, so cannot launch multiple toggle_repeats
        - if another toggle_repeat is triggered, the current execution stops immediately
        - execution immediately stops on second toggle of toggle_repeat

    :param action: what to repeat
    :param period_s: how often to repeat, seconds
    :param max_repeats: optional limit
    :return: callable toggle, to be set into a Tap

    Example:
        {"a": toggle_repeat(lambda: print("p")) }

        When you press 'a', 'p' will be pressed every 0.1 sec until you
        press 'a' again or press another button which triggers a different toggle_repeat.
    """
    repeat_util.registered_repeatables[action] = (
        period_s,
        max_repeats or 999999999999999,
    )
    return partial(repeat_util.toggle_repeatable, action)
