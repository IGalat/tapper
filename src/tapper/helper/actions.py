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
    """When toggled, starts repeating the action until toggled again."""
    max_repeats_int = max_repeats or 999999999999999
    repeater.registered_repeatables[action] = period_s, max_repeats_int
    return partial(_util.repeater.toggle_repeatable, action)
