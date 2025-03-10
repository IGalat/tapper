import time
from functools import partial
from typing import Any
from typing import Callable

import pytest
import tapper
from tapper import config
from tapper.action import wrapper
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import SendFn
from tapper.model.types_ import Signal
from tapper.state import keeper
from testutil_model import Dummy


def click(symbols: str) -> Signal | list[Signal]:
    result = []
    for s in symbols:
        result.extend([(s, KeyDirBool.DOWN), (s, KeyDirBool.UP)])
    return result


def down(symbols: str) -> Signal | list[Signal]:
    return [(s, KeyDirBool.DOWN) for s in symbols]


def up(symbols: str) -> list[Signal]:
    return [(s, KeyDirBool.UP) for s in symbols]


def sleep_signal(time_s: str | float) -> tuple[str, KeyDirBool]:
    return f"Sleep {time_s}", KeyDirBool.DOWN


def ends_with(outer: list[Any], sub: list[Any]) -> bool:
    return len(outer) >= len(sub) and outer[-len(sub) :] == sub


class Fixture:
    emul_signals: list[Signal]
    real_signals: list[Signal]
    pressed: list[str]
    toggled: list[str]

    send_real: SendFn
    start: Any  # type:ignore
    _acts: dict[int, partial[Any]]
    actions: list[int]

    def act(self, n: int) -> Callable[[], partial[Any]]:
        if n not in self._acts:
            self._acts[n] = partial(self.actions.append, n)
        return self._acts[n]


@pytest.fixture
def f(dummy: Dummy, is_debug: bool, make_group: Callable) -> Fixture:
    """Emulation of the entire tapper setup."""
    debug_sleep_mult = 5 if is_debug else 1

    # restore default before each
    config.action_runner_executors_threads = [1]
    config.tray_icon = False
    tapper.root = make_group("root")
    tapper.control_group = make_group("control_group")
    tapper._initialized = False
    tapper.controller.flow_control.config_thread_local_storage.action_config = (
        wrapper.ActionConfig(0, 0, tapper.controller.flow_control.kill_id)
    )

    listener = dummy.Listener.get_for_os("")
    config.listeners = [listener]

    fixture = Fixture()
    fixture._acts = {}
    fixture.emul_signals = []
    fixture.real_signals = []
    fixture.pressed = []
    fixture.toggled = []
    fixture.actions = []

    kb_tc = dummy.KbTC(listener, fixture.emul_signals, fixture.pressed, fixture.toggled)
    tapper.kb._tracker, tapper.kb._commander = kb_tc, kb_tc
    mouse_tc = dummy.MouseTC(
        listener, fixture.emul_signals, fixture.pressed, fixture.toggled
    )
    tapper.mouse._tracker, tapper.mouse._commander = mouse_tc, mouse_tc
    wtc = dummy.WinTC([])
    tapper.window._tracker, tapper.window._commander = wtc, wtc

    def start() -> None:
        tapper.init()  # this will init sender

        def sleep_logged(time_s: float, signals: list[Signal]) -> None:
            signals.append(sleep_signal(time_s))
            time.sleep(time_s)

        def send_and_sleep(send: SendFn, command: str) -> None:
            send(command)
            time.sleep(0.01 * debug_sleep_mult)  # so actions can run their course

        sender = tapper._send_processor
        sender.sleep_fn = partial(sleep_logged, signals=fixture.emul_signals)

        real_sender = SendCommandProcessor.from_none()
        real_sender.os = sender.os
        real_sender.parser = sender.parser
        real_sender.sleep_fn = partial(sleep_logged, signals=fixture.real_signals)
        fixture.send_real = partial(send_and_sleep, real_sender.send)

        emul_keeper = keeper.Emul()

        kb_tc2 = dummy.KbTC(
            listener, fixture.real_signals, fixture.pressed, fixture.toggled
        )
        kbc = KeyboardController()
        kbc._tracker, kbc._commander, kbc._emul_keeper = kb_tc2, kb_tc2, emul_keeper

        mouse_tc2 = dummy.MouseTC(
            listener, fixture.real_signals, fixture.pressed, fixture.toggled
        )
        mc = MouseController()
        mc._tracker, mc._commander, mc._emul_keeper = mouse_tc2, mouse_tc2, emul_keeper

        real_sender.kb_controller = kbc
        real_sender.mouse_controller = mc

        tapper._blocking = False
        tapper.start()

    fixture.start = start

    return fixture
