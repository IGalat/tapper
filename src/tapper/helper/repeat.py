from functools import partial
from typing import Any
from typing import Callable

from tapper.helper._util import repeat_util
from tapper.helper.model import Repeatable


def while_fn(
    condition: Callable[[], Any],
    action: Callable[[], Any],
    interval: float = 0.1,
    max_repeats: int | None = None,
) -> Callable[[], None]:
    """
    Repeats an action while condition applies.

    Notes:
    - runs in one separate thread, so cannot launch multiple toggle_repeats
    - if another repeat is triggered, the current execution stops immediately

    :param condition: Checked every loop, `not bool(condition())` stops.
    :param action: what to repeat.
    :param interval: how often to repeat, in seconds.
    :param max_repeats: optional limit.
    :return: callable toggle, to be set into a Tap.
    """
    return partial(
        repeat_util.run_action,
        Repeatable(
            condition=condition,
            action=action,
            interval=interval,
            max_repeats=max_repeats,
        ),
    )


def while_pressed(
    symbol: str,
    action: Callable[[], Any],
    interval: float = 0.1,
    max_repeats: int | None = None,
) -> Callable[[], None]:
    """
    Repeats action until key is released.

    :param symbol: keyboard or mouse key, aliases are accepted.
        Only a single key works, combinations don't.
    See :func:`while_fn` for other docs.
    """
    return partial(
        repeat_util.run_action,
        Repeatable(
            condition=repeat_util.to_pressed_condition(symbol),
            action=action,
            interval=interval,
            max_repeats=max_repeats,
        ),
    )


def toggle(
    action: Callable[[], Any],
    interval: float = 0.1,
    max_repeats: int | None = None,
    condition: Callable[[], Any] | None = None,
) -> Callable[[], None]:
    """
    When toggled, starts repeating the action until toggled again.

    :param condition: Additional optional condition. If not set, will repeat until toggled off.

    See :func:`while_fn` for docs.
    """
    return partial(
        repeat_util.toggle_run,
        Repeatable(
            condition=condition if condition else lambda: True,
            action=action,
            interval=interval,
            max_repeats=max_repeats,
        ),
    )
