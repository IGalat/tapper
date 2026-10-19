import threading
import uuid
from typing import Any


class _ActionLocal(threading.local):
    action_config: Any = None
    """ActionConfig of the running action; None outside of actions (e.g. main thread after init)."""


config_thread_local_storage = _ActionLocal()


class StopTapperActionException(Exception):
    """Normal way to interrupt tapper's action. Will not cause error logs etc."""


initialized = False
"""Set by tapper.init(). Flow control functions must not be used before that."""

paused = False
"""When this is True, running actions will wait unpause when they call tapper.sleep."""


kill_id = uuid.uuid4()
"""When this is changed, all running actions will be killed
with StopTapperActionException when they call tapper.sleep."""


def should_be_paused() -> bool:
    return paused


def should_be_killed() -> bool:
    if not initialized:
        raise RuntimeError(
            "tapper is not initialized. You should call this inside an action instead."
        )
    config = config_thread_local_storage.action_config
    return config is not None and config.kill_id != kill_id
