import threading
from dataclasses import dataclass

from tapper.model import types_
from tapper.model.tap_tree_shadow import STap


@dataclass
class ActionConfig:
    """Config for a single action. See tap_tree for info on configs."""

    send_interval: float
    send_press_duration: float

    @classmethod
    def from_tap(cls, tap: STap) -> "ActionConfig":
        return ActionConfig(
            send_interval=tap.send_interval, send_press_duration=tap.send_press_duration
        )


config_thread_local_storage = threading.local()


def wrapped_action(tap: STap) -> types_.Action:
    """
    :param tap: source.
    :return: Action that sets config before running.
    """
    config = ActionConfig.from_tap(tap)

    def wrapped() -> None:
        config_thread_local_storage.action_config = config
        tap.action()

    return wrapped
