import threading
import uuid


config_thread_local_storage = threading.local()
"""Used to store config for running actions."""


class StopTapperActionException(Exception):
    """Normal way to interrupt tapper's action. Will not cause error logs etc."""


paused = False
"""When this is True, running actions will wait unpause when they call tapper.sleep."""


kill_id = uuid.uuid4()
"""When this is changed, all running actions will be killed
with StopTapperActionException when they call tapper.sleep."""


def should_be_paused() -> bool:
    return paused


def should_be_killed() -> bool:
    config = config_thread_local_storage.action_config
    if config is None:
        raise ValueError(
            "No config for action. "
            "Did you initialize tapper and are you running this inside an action?"
        )
    return config.kill_id != kill_id
