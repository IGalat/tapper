"""This file in tests root is required for pytest path discovery for some reason."""
from collections import defaultdict
from typing import Optional

import pytest
from tapper.action.runner import ActionRunner
from tapper.command.keyboard.keyboard_commander import KeyboardCommander
from tapper.command.mouse.mouse_commander import MouseCommander
from tapper.model import constants
from tapper.model import types_
from tapper.model.types_ import Signal
from tapper.signal.base_listener import SignalListener


# DUMMY START #


class DummyListener(SignalListener):
    name = "dummy"

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @staticmethod
    def get_for_os(os: str) -> "SignalListener":
        return DummyListener()


class DummyKbCmd(KeyboardCommander):
    listener: SignalListener
    all_signals: list[Signal]

    def __init__(self, listener: SignalListener, all_signals: list[Signal]) -> None:
        self.listener = listener
        self.all_signals = all_signals

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def pressed(self, symbol: str) -> bool:
        pass

    def toggled(self, symbol: str) -> bool:
        pass

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        pass


class DummyMouseCmd(MouseCommander):
    listener: SignalListener
    all_signals: list[Signal]

    def __init__(self, listener: SignalListener, all_signals: list[Signal]) -> None:
        self.listener = listener
        self.all_signals = all_signals

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        pass

    def pressed(self, symbol: str) -> bool:
        pass

    def toggled(self, symbol: str) -> bool:
        pass

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        pass

    def get_pos(self) -> tuple[int, int]:
        pass


class DummyActionRunner(ActionRunner):
    actions_ran: defaultdict[int, list[types_.Action]]
    """{executor ordinal: list of every action ran}"""
    control_actions_ran: list[types_.Action]

    def __init__(self) -> None:
        self.actions_ran = defaultdict(list)
        self.control_actions_ran = []

    def run(self, fn: types_.Action, executor_ordinal: int = 0) -> None:
        self.actions_ran[executor_ordinal].append(fn)

    def run_control(self, fn: types_.Action) -> None:
        self.control_actions_ran.append(fn)


class Dummy:
    Listener = DummyListener
    KbCmd = DummyKbCmd
    MouseCmd = DummyMouseCmd
    ActionRunner = DummyActionRunner


@pytest.fixture
def dummy() -> Dummy:
    return Dummy()


# DUMMY END #
