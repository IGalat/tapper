import logging

import pytest

from tapper.action.wrapper import wrapped_action
from tapper.controller.flow_control import StopTapperActionError
from tapper.model.constants import ListenerResult
from tapper.model.tap_tree_shadow import STap
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger


def make_stap(action) -> STap:
    stap = STap(Trigger(MainKey(["a"])), action, 0, ListenerResult.SUPPRESS)
    stap.send_interval = 0
    stap.send_press_duration = 0
    return stap


def killed() -> None:
    raise StopTapperActionError


def broken() -> None:
    raise ValueError("boom")


def test_killed_action_is_not_logged_as_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG, logger="tapper"):
        wrapped_action(make_stap(killed))()
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


def test_failing_action_is_logged_as_warning(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="tapper"):
        wrapped_action(make_stap(broken))()
    [record] = [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert record.levelno == logging.WARNING
    assert "boom" in record.getMessage()
