from __future__ import annotations

from collections import defaultdict
from typing import Any

from tapper.action.runner import ActionRunner
from tapper.controller.keyboard.kb_api import KeyboardCommander
from tapper.controller.keyboard.kb_api import KeyboardTracker
from tapper.controller.mouse.mouse_api import MouseCommander
from tapper.controller.mouse.mouse_api import MouseTracker
from tapper.controller.window.window_api import WindowCommander
from tapper.controller.window.window_api import WindowTracker
from tapper.model import constants
from tapper.model import languages
from tapper.model import types_
from tapper.model.languages import Lang
from tapper.model.types_ import Signal
from tapper.model.window import Window
from tapper.signal.base_listener import SignalListener

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
    lang_ = languages.get("en")

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

    def lang(self, lang: str | int | Lang | None = None) -> None:
        if lang is None:
            return self.lang_
        else:
            return self.lang_ if self.lang_ == languages.get(lang) else None

    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
        self.lang_ = languages.get(lang)


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
        x = x or 0
        y = y or 0
        if not relative:
            self.x, self.y = x, y
        else:
            self.x, self.y = self.x + x, self.y + y

    def pressed(self, symbol: str) -> bool:
        return symbol in self.pressed_symbols

    def toggled(self, symbol: str) -> bool:
        return symbol in self.toggled_symbols

    def get_pos(self) -> tuple[int, int]:
        return self.x, self.y

    def memorize_pos(self) -> None:
        pass

    def to_memorized_pos(self) -> None:
        pass


def str_match(filtered: str | None, iterated: str | None, strict: bool) -> bool:
    if not filtered or not iterated:
        return False
    if strict:
        return filtered == iterated
    else:
        return filtered.casefold() in iterated.casefold()


class DummyWindowTrackerCommander(WindowTracker, WindowCommander):
    open_windows: list[str]
    fore_window: str

    def __init__(self, open_windows: list[str]) -> None:
        self.open_windows = open_windows
        self.fore_window = ""

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_open(
        self,
        exec_or_title: str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
        limit: int | None = None,
    ) -> list[Window]:
        exec_or_title = exec_or_title or exec or title
        return [
            Window(w) for w in self.open_windows if str_match(exec_or_title, w, strict)
        ]

    def active(
        self,
        exec_or_title: str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
    ) -> Window | None:
        exec_or_title = exec_or_title or exec or title
        if str_match(exec_or_title, self.fore_window, strict):
            return Window(exec_or_title)
        return None

    def to_active(
        self,
        window_or_exec_or_title: Window | str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
    ) -> bool:
        self.fore_window = window_or_exec_or_title  # type: ignore
        if window_or_exec_or_title not in self.open_windows:
            self.open_windows.append(window_or_exec_or_title)  # type: ignore
        return True

    def close(
        self,
        window_or_exec_or_title: Window | str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
        force: bool = True,
    ) -> bool:
        pass

    def minimize(
        self,
        window_or_exec_or_title: Window | str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
    ) -> bool:
        pass

    def maximize(
        self,
        window_or_exec_or_title: Window | str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
    ) -> bool:
        if window_or_exec_or_title not in self.open_windows:
            self.open_windows.append(window_or_exec_or_title)  # type: ignore
        return True

    def restore(
        self,
        window_or_exec_or_title: Window | str | None = None,
        title: str | None = None,
        exec: str | None = None,
        strict: bool = False,
        process_id: int | None = None,
        handle: Any = None,
    ) -> bool:
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
    KbTC = DummyKbTrackerCommander
    MouseTC = DummyMouseTrackerCommander
    WinTC = DummyWindowTrackerCommander
    ActionRunner = DummyActionRunner
