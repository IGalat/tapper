import time
from functools import partial
from typing import Any
from typing import Callable

from tapper.helper import _util
from tapper.helper._util import repeater
from tapper.helper.helper_model import RecordConfig


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
    max_repeats_int = max_repeats or 999999999999999
    repeater.registered_repeatables[action] = period_s, max_repeats_int
    return partial(_util.repeater.toggle_repeatable, action)


def record(
    callback: Callable[[str], Any], config: RecordConfig = RecordConfig()
) -> Callable[[], None]:
    """
    Gives a callable, that:
    On first stroke, starts recording keystrokes and mouse clicks, and position of the mouse during these actions.
    On second stroke, stops recording, transforms recorded actions into a string that can be supplied to tapper.send
        and calls the callback with this string.

    :param callback: What to do with resulting string
    :param config: config settings
    :return: callable toggle, to be set into a Tap
    """

    return partial(_util.recorder.toggle_recording, callback, config)
