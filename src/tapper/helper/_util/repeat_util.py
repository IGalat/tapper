import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import tapper
from tapper.action.wrapper import ActionConfig
from tapper.action.wrapper import config_thread_local_storage
from tapper.boot import initializer
from tapper.helper.model import Repeatable

TIME_SPLIT = 0.1

executor = ThreadPoolExecutor(max_workers=1)
sleep = time.sleep  # for testing


running_repeatable: Repeatable | None = None


def is_end_run(repeatable: Repeatable) -> bool:
    try:
        return (
            running_repeatable is None
            or running_repeatable.uid != repeatable.uid
            or not bool(repeatable.condition())
        )
    except Exception:
        return True


def _run_task(repeatable: Repeatable) -> None:
    global running_repeatable
    running_repeatable = repeatable
    config_thread_local_storage.action_config = ActionConfig(
        send_interval=tapper.root.send_interval,  # type: ignore
        send_press_duration=tapper.root.send_press_duration,  # type: ignore
    )
    for i in range(repeatable.max_repeats or 99999999999999):
        if is_end_run(repeatable):
            running_repeatable = None
            return
        try:
            repeatable.action()
        except Exception:
            running_repeatable = None
            return
        if is_end_run(repeatable):
            running_repeatable = None
            return
        # if long wait, break into chunks to check if to end runnable
        if repeatable.interval <= TIME_SPLIT:
            sleep(repeatable.interval)
        else:
            started_at = time.perf_counter()
            elapsed = 0.0
            while repeatable.interval - elapsed > 0.0:
                time.sleep(min(TIME_SPLIT, repeatable.interval - elapsed))
                elapsed = time.perf_counter() - started_at
                if is_end_run(repeatable):
                    running_repeatable = None
                    return
    else:
        # looped until max repeats
        running_repeatable = None


def run_action(in_repeatable: Repeatable) -> None:
    global running_repeatable
    running_repeatable = in_repeatable
    executor.submit(_run_task, in_repeatable)


def to_pressed_condition(symbol: str) -> Callable[[], bool]:
    if symbol in [
        *tapper.model.mouse.regular_buttons,
        *tapper.model.mouse.button_aliases.keys(),
    ]:
        device = tapper.mouse  # type: ignore
    elif symbol in tapper.model.keyboard.get_keys(tapper.config.os).keys():
        device = tapper.kb  # type: ignore
    else:
        raise ValueError(f"Repeat while pressed: '{symbol}' not recognised.")
    return (
        lambda: device.pressed(symbol)
        or symbol in initializer.keeper_pressed.pressed_keys  # type: ignore
    )


def toggle_run(repeatable: Repeatable) -> None:
    global running_repeatable
    if running_repeatable and repeatable.uid == running_repeatable.uid:
        running_repeatable = None
        return
    else:
        run_action(repeatable)
