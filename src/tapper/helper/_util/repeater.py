import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any
from typing import Callable

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


def toggle_repeatable(action: Callable[[], Any]) -> None:
    global running_repeatable
    global new_repeatable_queued
    if action is not running_repeatable:
        running_repeatable = action
        new_repeatable_queued = True
        executor.submit(run_task, action)
    else:
        running_repeatable = None


@dataclass
class Sub:
    symbol: str
    action: Callable[[], Any]

    def unsub(self, signal: Signal) -> None:
        global running_repeatable
        if signal[1] == KeyDirBool.UP and signal[0] == self.symbol:
            if running_repeatable == self.action:
                running_repeatable = None
            event.unsubscribe("keyboard", self.unsub)
            event.unsubscribe("mouse", self.unsub)


def while_pressed(symbol: str, action: Callable[[], Any]) -> None:
    if action == running_repeatable:
        return
    toggle_repeatable(action)
    sub = Sub(symbol, action)
    event.subscribe("keyboard", sub.unsub)
    event.subscribe("mouse", sub.unsub)
