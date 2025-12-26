import logging
from dataclasses import dataclass
from uuid import UUID

from tapper.controller import flow_control
from tapper.controller.flow_control import config_thread_local_storage
from tapper.feedback.logger import LogExceptions
from tapper.model import types_
from tapper.model.tap_tree_shadow import STap


@dataclass
class ActionConfig:
    """Config for a single action. See tap_tree for info on configs."""

    send_interval: float
    send_press_duration: float
    kill_id: UUID

    @classmethod
    def from_tap(cls, tap: STap) -> "ActionConfig":
        return ActionConfig(
            send_interval=tap.send_interval,
            send_press_duration=tap.send_press_duration,
            kill_id=flow_control.kill_id,
        )


def wrapped_action(tap: STap) -> types_.Action:
    """
    :param tap: source.
    :return: Action that sets config before running.
    """
    config = ActionConfig.from_tap(tap)

    def wrapped() -> None:
        config_thread_local_storage.action_config = config
        LogExceptions(log_level=logging.WARNING)(tap.action)()

    return wrapped
