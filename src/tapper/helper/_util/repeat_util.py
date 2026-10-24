import contextlib
import queue
import threading
import time
from collections.abc import Callable

import tapper
from tapper.controller import flow_control
from tapper.controller.flow_control import ActionConfig
from tapper.controller.flow_control import StopTapperActionError
from tapper.controller.flow_control import config_thread_local_storage
from tapper.feedback.logger import log
from tapper.helper.model import Repeatable
from tapper.model import keyboard as keyboard_model
from tapper.model import mouse as mouse_model

TIME_SPLIT = 0.1

running_repeatable: Repeatable | None = None

_to_run: queue.Queue[Repeatable] = queue.Queue()


def is_end_run(repeatable: Repeatable) -> bool:
    try:
        return (
            flow_control.shutdown.is_set()
            or running_repeatable is None
            or running_repeatable.uid != repeatable.uid
            or not bool(repeatable.condition())
        )
    except Exception:  # noqa: BLE001  # user condition: any failure ends the repeat
        return True


def _run_task(repeatable: Repeatable) -> None:
    config_thread_local_storage.action_config = ActionConfig(
        send_interval=tapper._runtime.root.send_interval,
        send_press_duration=tapper._runtime.root.send_press_duration,
        kill_id=flow_control.kill_id,
    )
    for _ in range(repeatable.max_repeats or 99999999999999):
        if is_end_run(repeatable):
            return
        try:
            repeatable.action()
        except Exception:  # noqa: BLE001  # user action: any failure ends the repeat
            return
        if is_end_run(repeatable):
            return
        # if long wait, break into chunks to check if to end runnable
        if repeatable.interval <= TIME_SPLIT:
            tapper.sleep(repeatable.interval)
        else:
            started_at = time.perf_counter()
            elapsed = 0.0
            while repeatable.interval - elapsed > 0.0:
                tapper.sleep(min(TIME_SPLIT, repeatable.interval - elapsed))
                elapsed = time.perf_counter() - started_at
                if is_end_run(repeatable):
                    return


def _finish(repeatable: Repeatable) -> None:
    """A newer repeat may already own the slot; only clear it if this one still does."""
    global running_repeatable
    if running_repeatable is repeatable:
        running_repeatable = None


def _worker() -> None:
    while True:
        task = _to_run.get()
        try:
            with contextlib.suppress(StopTapperActionError):
                _run_task(task)
        except Exception:  # noqa: BLE001  # the worker must outlive a broken repeat
            log.warning("Repeat failed", exc_info=True)
        finally:
            _finish(task)
            _to_run.task_done()


threading.Thread(target=_worker, name="tapper-repeat", daemon=True).start()


def run_action(in_repeatable: Repeatable) -> None:
    global running_repeatable
    running_repeatable = in_repeatable
    _to_run.put(in_repeatable)


def to_pressed_condition(symbol: str) -> Callable[[], bool]:
    if symbol in [
        *mouse_model.regular_buttons,
        *mouse_model.button_aliases.keys(),
    ]:
        device = tapper.mouse
    elif symbol in keyboard_model.get_keys(tapper.config.os):
        device = tapper.kb
    else:
        raise ValueError(f"Repeat while pressed: '{symbol}' not recognised.")
    return lambda: (
        device.pressed(symbol) or symbol in tapper._runtime.pressed.pressed_keys
    )


def toggle_run(repeatable: Repeatable) -> None:
    global running_repeatable
    if running_repeatable and repeatable.uid == running_repeatable.uid:
        running_repeatable = None
        return
    else:
        run_action(repeatable)
