import threading
import time
from collections.abc import Callable
from collections.abc import Iterator
from concurrent.futures import wait
from functools import partial
from typing import Any

import pytest

import tapper
from tapper import config
from tapper.boot import platforms
from tapper.boot.platforms import Platform
from tapper.controller import flow_control
from tapper.controller.flow_control import ActionConfig
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.model import constants
from tapper.model.constants import Aspect
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import SendFn
from tapper.model.types_ import Signal
from tapper.signal.base_listener import SignalListener
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener
from tapper.state import keeper
from testutil_model import Dummy
from testutil_model import FakeClock


def click(symbols: str) -> list[Signal]:
    result = []
    for s in symbols:
        result.extend([(s, KeyDirBool.DOWN), (s, KeyDirBool.UP)])
    return result


def down(symbols: str) -> list[Signal]:
    return [(s, KeyDirBool.DOWN) for s in symbols]


def up(symbols: str) -> list[Signal]:
    return [(s, KeyDirBool.UP) for s in symbols]


def sleep_signal(time_s: str | float) -> tuple[str, KeyDirBool]:
    return f"Sleep {time_s}", KeyDirBool.DOWN


def ends_with(outer: list[Any], sub: list[Any]) -> bool:
    return len(outer) >= len(sub) and outer[-len(sub) :] == sub


def wait_actions() -> None:
    """Every action triggered so far has finished."""
    runner = tapper._runtime.runner
    futures = [future for futures in runner._runnables for future in futures]
    if hasattr(runner, "_control_runnable"):
        futures.append(runner._control_runnable)
    assert not wait(futures, timeout=5).not_done, "actions still running"


class Fixture:
    listener: SignalListener
    clock: FakeClock
    """time.perf_counter for the duration of the test; sleeps in real input advance it."""
    gate: threading.Event
    """Clear it to make every sleep inside an emulated send block until it is set again."""
    _arrived: threading.Semaphore
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

    def wait_blocked(self, actions: int) -> None:
        """That many actions have reached a sleep and are parked at the closed gate."""
        for _ in range(actions):
            assert self._arrived.acquire(timeout=5), "fewer actions reached the gate"


@pytest.fixture
def f(
    dummy: Dummy, make_group: Callable, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Fixture]:
    """Emulation of the entire tapper setup."""
    # restore default before each
    config.action_runner_executors_threads = [1]
    config.tray_icon = False
    tapper.root = make_group("root")
    tapper.control_group = make_group("control_group")
    flow_control.initialized = False
    flow_control.config_thread_local_storage.action_config = ActionConfig(
        0, 0, flow_control.kill_id
    )

    listener = dummy.Listener()
    config.listeners = [KeyboardSignalListener]

    fixture = Fixture()
    fixture.listener = listener
    fixture.clock = FakeClock()
    monkeypatch.setattr(time, "perf_counter", fixture.clock)
    fixture.gate = threading.Event()
    fixture.gate.set()
    fixture._arrived = threading.Semaphore(0)
    fixture._acts = {}
    fixture.emul_signals = []
    fixture.real_signals = []
    fixture.pressed = []
    fixture.toggled = []
    fixture.actions = []

    kb_driver = dummy.KbDriver(
        listener, fixture.emul_signals, fixture.pressed, fixture.toggled
    )
    mouse_driver = dummy.MouseDriver(
        listener, fixture.emul_signals, fixture.pressed, fixture.toggled
    )
    window_driver = dummy.WindowDriver([])
    dummy_platform = Platform(
        listeners={Aspect.keyboard: lambda: listener},
        drivers={
            Aspect.keyboard: lambda: kb_driver,
            Aspect.mouse: lambda: mouse_driver,
            Aspect.window: lambda: window_driver,
        },
    )
    monkeypatch.setattr(config, "os", constants.OS.dummy)
    monkeypatch.setitem(platforms.by_os, constants.OS.dummy, lambda: dummy_platform)

    def start() -> None:
        tapper.init()  # this will init sender

        def emul_sleep(time_s: float) -> None:
            fixture.emul_signals.append(sleep_signal(time_s))
            fixture._arrived.release()
            fixture.gate.wait()

        def real_sleep(time_s: float) -> None:
            """Time passes: the clock moves and actions triggered so far get to finish."""
            fixture.real_signals.append(sleep_signal(time_s))
            fixture.clock.advance(time_s)
            if fixture.gate.is_set():
                wait_actions()

        def send_real(send: SendFn, command: str) -> None:
            send(command)
            if fixture.gate.is_set():
                wait_actions()

        sender = tapper._send_processor
        sender.sleep_fn = emul_sleep

        real_sender = SendCommandProcessor()
        real_sender.os = sender.os
        real_sender.parser = sender.parser
        real_sender.sleep_fn = real_sleep
        fixture.send_real = partial(send_real, real_sender.send)

        emul_keeper = keeper.Emul()

        kb_driver2 = dummy.KbDriver(
            listener, fixture.real_signals, fixture.pressed, fixture.toggled
        )
        kbc = KeyboardController()
        kbc._init(kb_driver2)
        kbc._emul_keeper = emul_keeper

        mouse_driver2 = dummy.MouseDriver(
            listener, fixture.real_signals, fixture.pressed, fixture.toggled
        )
        mc = MouseController()
        mc._init(mouse_driver2)
        mc._emul_keeper = emul_keeper

        real_sender.kb_controller = kbc
        real_sender.mouse_controller = mc

        tapper._blocking = False
        tapper.start()

    fixture.start = start

    yield fixture
    fixture.gate.set()
