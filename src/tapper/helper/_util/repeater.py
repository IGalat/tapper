import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Callable

executor = ThreadPoolExecutor(max_workers=1)

registered_repeatables: dict[Callable[[], Any], tuple[float, int]] = {}

running_repeatable: Callable[[], Any] | None = None
new_repeatable_queued: bool = False


def run_task(repeatable: Callable[[], Any]) -> None:
    global new_repeatable_queued
    new_repeatable_queued = False
    end_run = lambda: new_repeatable_queued or not running_repeatable

    to_wait, repeats = registered_repeatables[repeatable]
    for _ in range(repeats):
        if end_run():
            return
        repeatable()
        if end_run():
            return

        if to_wait <= 0.2:
            time.sleep(to_wait)
        else:
            started_at = time.perf_counter()
            elapsed = 0
            while to_wait - elapsed > 0:
                time.sleep(min(0.2, to_wait - elapsed))
                elapsed = time.perf_counter() - started_at
                if end_run():
                    return


def toggle_repeatable(action: Callable[[], Any]) -> None:
    global running_repeatable
    global new_repeatable_queued
    if action is not running_repeatable:
        running_repeatable = action
        new_repeatable_queued = True
        executor.submit(run_task, action)
    else:
        running_repeatable = None
