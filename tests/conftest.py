from __future__ import annotations

import sys

from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.controller.mouse.mouse_api import MouseCommander
from tapper.controller.mouse.mouse_api import MouseTracker

"""This file in tests root is required for pytest path discovery for some reason."""
from collections import defaultdict

import pytest
from tapper.action.runner import ActionRunner
from tapper.model import constants
from tapper.model import types_
from tapper.model.types_ import Signal
from tapper.signal.base_listener import SignalListener

# DUMMY START #

dumL = None


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
    def get_for_os(os: str) -> SignalListener:
        global dumL
        if not dumL:
            dumL = DummyListener()
        return dumL


class DummyKbTrackerCommander(KeyboardTracker, KeyboardCommander):
    listener: SignalListener
    all_signals: list[Signal]
    pressed_symbols: list[str]
    toggled_symbols: list[str]

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def __init__(
        self,
        listener: SignalListener,
        all_signals: list[Signal],
        pressed_symbols: list[str] | None = None,
        toggled_symbols: list[str] | None = None,
    ) -> None:
        self.listener = listener
        self.all_signals = all_signals
        if pressed_symbols is not None:
            self.pressed_symbols = pressed_symbols
        else:
            self.pressed_symbols = []
        if toggled_symbols is not None:
            self.toggled_symbols = toggled_symbols
        else:
            self.toggled_symbols = []

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def pressed(self, symbol: str) -> bool:
        return symbol in self.pressed_symbols

    def toggled(self, symbol: str) -> bool:
        return symbol in self.toggled_symbols


class DummyMouseTrackerCommander(MouseTracker, MouseCommander):
    listener: SignalListener
    all_signals: list[Signal]
    pressed_symbols: list[str]
    toggled_symbols: list[str]
    x: int = 0
    y: int = 0

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def __init__(
        self,
        listener: SignalListener,
        all_signals: list[Signal],
        pressed_symbols: list[str] | None = None,
        toggled_symbols: list[str] | None = None,
    ) -> None:
        self.listener = listener
        self.all_signals = all_signals
        if pressed_symbols is not None:
            self.pressed_symbols = pressed_symbols
        else:
            self.pressed_symbols = []
        if toggled_symbols is not None:
            self.toggled_symbols = toggled_symbols
        else:
            self.toggled_symbols = []

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def move(
        self, x: int | None = None, y: int | None = None, relative: bool = False
    ) -> None:
        if not x or x < 0:
            x = 0
        if not y or y < 0:
            y = 0
        if not relative:
            self.x, self.y = x, y
        else:
            self.x, self.y = max(0, self.x + x), max(0, self.y + y)

    def pressed(self, symbol: str) -> bool:
        return symbol in self.pressed_symbols

    def toggled(self, symbol: str) -> bool:
        return symbol in self.toggled_symbols

    def get_pos(self) -> tuple[int, int]:
        return self.x, self.y


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
    KbTC = DummyKbTrackerCommander
    MouseTC = DummyMouseTrackerCommander
    ActionRunner = DummyActionRunner


@pytest.fixture
def dummy() -> Dummy:
    return Dummy()


# DUMMY END #


@pytest.fixture
def is_debug() -> bool:
    return hasattr(sys, "gettrace") and (sys.gettrace() is not None)
