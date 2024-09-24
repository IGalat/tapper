import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any
from typing import Callable
from typing import Optional

from tapper.action.wrapper import ActionConfig
from tapper.action.wrapper import config_thread_local_storage
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import Signal
from tapper.util import event

"""For actions.toggle_repeat"""

TIME_SPLIT = 0.1

executor = ThreadPoolExecutor(max_workers=1)

registered_repeatables: dict[Callable[[], Any], tuple[float, int]] = {}

running_repeatable: Callable[[], Any] | None = None
new_repeatable_queued: bool = False


def run_task(repeatable: Callable[[], Any]) -> None:
    global new_repeatable_queued
    new_repeatable_queued = False
    end_run = lambda: new_repeatable_queued or not running_repeatable
    config_thread_local_storage.action_config = ActionConfig(
        send_interval=0.01, send_press_duration=0.01
    )

    to_wait, repeats = registered_repeatables[repeatable]
    for _ in range(repeats):
        if end_run():
            return
        repeatable()
        if end_run():
            return

        if to_wait <= TIME_SPLIT:
            time.sleep(to_wait)
        else:
            started_at = time.perf_counter()
            elapsed = 0.0
            while to_wait - elapsed > 0:
                time.sleep(min(TIME_SPLIT, to_wait - elapsed))
                elapsed = time.perf_counter() - started_at
                if end_run():
                    return


def equal_fn(fn1: Optional[Callable], fn2: Optional[Callable]) -> bool:
    if fn1 is None or fn2 is None:
        return False
    if fn1 is fn2 or fn1 == fn2:
        return True
    return (
        fn1.__code__.co_code == fn2.__code__.co_code
        and fn1.__code__.co_consts == fn2.__code__.co_consts
        and fn1.__code__.co_stacksize == fn2.__code__.co_stacksize
        and fn1.__code__.co_varnames == fn2.__code__.co_varnames
        and fn1.__code__.co_flags == fn2.__code__.co_flags
        and fn1.__code__.co_name == fn2.__code__.co_name
        and fn1.__code__.co_names == fn2.__code__.co_names
    )


def toggle_repeatable(action: Callable[[], Any]) -> None:
    global running_repeatable
    global new_repeatable_queued
    if action is not None and not equal_fn(action, running_repeatable):
        running_repeatable = action
        new_repeatable_queued = True
        executor.submit(run_task, action)
    else:
        running_repeatable = None


def remove_repeatable_and_unsub(signal: Signal, expected_symbol: str) -> bool:
    """return False for unsub."""
    global running_repeatable
    if signal[0] == expected_symbol and signal[1] == KeyDirBool.UP:
        running_repeatable = None
        return False
    return True


def while_pressed(symbol: str, action: Callable[[], Any]) -> None:
    if equal_fn(action, running_repeatable):
        return
    toggle_repeatable(action)
    event.subscribe(
        "keyboard", partial(remove_repeatable_and_unsub, expected_symbol=symbol)
    )
    event.subscribe(
        "mouse", partial(remove_repeatable_and_unsub, expected_symbol=symbol)
    )
