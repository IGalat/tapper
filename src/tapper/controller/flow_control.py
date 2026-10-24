import threading
import uuid
from dataclasses import dataclass


@dataclass
class ActionConfig:
    """Config for a single action. See tap_tree for info on configs."""

    send_interval: float
    send_press_duration: float
    kill_id: uuid.UUID


class _ActionLocal(threading.local):
    action_config: ActionConfig | None = None
    """None outside of actions (e.g. main thread after init)."""


config_thread_local_storage = _ActionLocal()


class StopTapperActionError(Exception):
    """Normal way to interrupt tapper's action. Will not cause error logs etc."""


initialized = False
"""Set by tapper.init(). Flow control functions must not be used before that."""

paused = False
"""When this is True, running actions will wait unpause when they call tapper.sleep."""


kill_id = uuid.uuid4()
"""When this is changed, all running actions will be killed
with StopTapperActionError when they call tapper.sleep."""

shutdown = threading.Event()
"""Set to make tapper.start() stop everything and return."""


def should_be_paused() -> bool:
    return paused


def should_be_killed() -> bool:
    if not initialized:
        raise RuntimeError(
            "tapper is not initialized. You should call this inside an action instead."
        )
    config = config_thread_local_storage.action_config
    return config is not None and config.kill_id != kill_id
