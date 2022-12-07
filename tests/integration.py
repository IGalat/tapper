import time
from functools import partial
from typing import Any
from typing import Callable

import pytest
import tapper
from conftest import Dummy
from tapper import configuration
from tapper import Tap
from tapper.command.send_processor import SendCommandProcessor
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import SendFn
from tapper.model.types_ import Signal


def click(*symbols: str) -> Signal | list[Signal]:
    result = []
    for s in symbols:
        result.extend([(s, KeyDirBool.DOWN), (s, KeyDirBool.UP)])
    return result


def down(*symbols: str) -> Signal | list[Signal]:
    return [(s, KeyDirBool.DOWN) for s in symbols]


def up(*symbols: str) -> list[Signal]:
    return [(s, KeyDirBool.UP) for s in symbols]


def sleep(time_s: float) -> str:
    return f"Sleep {time_s}"


def append(arr: list[Any], item: Any) -> None:
    arr.append(item)


class Fixture:
    emul_signals: list[Signal]
    real_signals: list[Signal]

    send_real: SendFn
    start: Any  # type:ignore
    _acts: dict[int, partial[Any]]
    actions: list[int]

    def act(self, n: int) -> Callable[[], partial[Any]]:
        if n not in self._acts:
            self._acts[n] = partial(append, self.actions, n)
        return self._acts[n]


@pytest.fixture
def f(dummy: Dummy, is_debug: bool) -> Fixture:
    debug_sleep_mult = 5 if is_debug else 1

    listener = dummy.Listener.get_for_os("")
    configuration.listeners = [listener]

    f = Fixture()
    f._acts = {}
    f.emul_signals = []
    f.real_signals = []
    f.actions = []

    tapper.kb = dummy.KbCmd(listener, f.emul_signals)
    tapper.mouse = dummy.MouseCmd(listener, f.emul_signals)

    def sleep_fake(time_s: float, signals: list[Signal]) -> None:
        signals.append((sleep(time_s), KeyDirBool.DOWN))
        if time_s > 0:
            time.sleep(0.01 * debug_sleep_mult)  # for concurrent action tests

    sender = tapper._send_processor
    sender.sleep_fn = partial(sleep_fake, signals=f.emul_signals)

    def send_and_sleep(send: SendFn, command: str) -> None:
        send(command)
        time.sleep(0.01 * debug_sleep_mult)  # so actions can run their course

    real_sender = SendCommandProcessor.from_none()
    f.send_real = partial(send_and_sleep, real_sender.send)

    def start() -> None:
        tapper.init()  # this will init sender
        real_sender.os = sender.os
        real_sender.parser = sender.parser
        real_sender.sleep_fn = partial(sleep_fake, signals=f.real_signals)
        real_sender.kb_commander = dummy.KbCmd(listener, f.real_signals)
        real_sender.mouse_commander = dummy.MouseCmd(listener, f.real_signals)

        tapper.start(False)

    f.start = start  # type: ignore

    return f


class TestSimple:
    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add(Tap("a", f.act(1)))
        tapper.root.add(Tap("b", "q"))
        f.start()

        f.send_real("a")
        time.sleep(0.01)
        assert f.real_signals == click("a")
        assert f.actions == [1]

        f.send_real("b")
        assert f.real_signals == [*click("a"), *click("b")]
        assert f.emul_signals == click("q")


class TestTreeOrder:
    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add(Tap("a", f.act(1)))
        tapper.root.add(Tap("a", f.act(2)))
        f.start()

        f.send_real("aa")
        assert f.real_signals == click("a") * 2
        assert f.actions == [2, 2]


class TestConcurrentActions:
    pass
