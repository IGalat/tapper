import time
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from functools import partial
from typing import Callable

import tapper
from tapper.action.wrapper import ActionConfig
from tapper.action.wrapper import config_thread_local_storage
from tapper.helper.model import Repeatable

TIME_SPLIT = 0.1

executor = ThreadPoolExecutor(max_workers=1)


running_repeatable: Repeatable


def _run_task(repeatable: Repeatable) -> None:
    global running_repeatable
    end_run = lambda: running_repeatable.uid != repeatable.uid
    config_thread_local_storage.action_config = ActionConfig(
        send_interval=tapper.root.send_interval,  # type: ignore
        send_press_duration=tapper.root.send_press_duration,  # type: ignore
    )
    for i in range(repeatable.max_repeats or 99999999999999):
        if end_run() or not bool(repeatable.condition()):
            return
        repeatable.action()
        if end_run():
            return
        # if long wait, break into chunks to check if to end runnable
        if repeatable.interval <= TIME_SPLIT:
            time.sleep(repeatable.interval)
        else:
            started_at = time.perf_counter()
            elapsed = 0.0
            while repeatable.interval - elapsed > 0.0:
                time.sleep(min(TIME_SPLIT, repeatable.interval - elapsed))
                elapsed = time.perf_counter() - started_at
                if end_run():
                    return


def run_action(repeatable: Repeatable) -> None:
    global running_repeatable
    running_repeatable = repeatable
    executor.submit(_run_task, repeatable)


@cache
def is_mouse_symbol(symbol: str) -> bool:
    """False is keyboard"""
    return symbol in [
        *tapper.model.mouse.regular_buttons,
        *tapper.model.mouse.button_aliases.keys(),
    ]


def to_pressed_condition(symbol: str) -> Callable[[], bool]:
    if is_mouse_symbol(symbol):
        return partial(tapper.mouse.pressed, symbol)
    else:
        return partial(tapper.kb.pressed, symbol)


def toggle_run(repeatable: Repeatable) -> None:
    global running_repeatable
    if repeatable.uid == running_repeatable.uid:
        running_repeatable.condition = lambda: False
        return
    running_repeatable.condition = lambda: True
    run_action(repeatable)
