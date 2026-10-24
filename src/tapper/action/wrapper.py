import logging

from tapper.controller import flow_control
from tapper.controller.flow_control import ActionConfig
from tapper.controller.flow_control import config_thread_local_storage
from tapper.feedback.logger import LogExceptions
from tapper.model import types_
from tapper.model.tap_tree_shadow import STap


def wrapped_action(tap: STap) -> types_.Action:
    """
    :param tap: source.
    :return: Action that sets config before running.
    """
    config = ActionConfig(
        send_interval=tap.send_interval,
        send_press_duration=tap.send_press_duration,
        kill_id=flow_control.kill_id,
    )

    action = tap.action
    assert action is not None  # a tap without an action is never dispatched

    def wrapped() -> None:
        config_thread_local_storage.action_config = config
        LogExceptions(log_level=logging.WARNING)(action)()

    return wrapped
