import time
from functools import partial
from typing import Callable

import pytest
import tapper
from conftest import Dummy
from tapper import configuration
from tapper import Tap
from tapper.action.runner import ActionRunner
from tapper.command.keyboard.keyboard_commander import KeyboardCommander
from tapper.command.mouse.mouse_commander import MouseCommander
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import Signal


# todo


def down(*symbols: str) -> Signal | list[Signal]:
    return _to_dir(KeyDirBool.DOWN, *symbols)


def up(*symbols: str) -> Signal | list[Signal]:
    return _to_dir(KeyDirBool.UP, *symbols)


def _to_dir(dir: KeyDirBool, *symbols: str) -> Signal | list[Signal]:
    if len(symbols) == 1:
        return symbols[0], dir
    return [(s, dir) for s in symbols]


def sleep(time_s: float) -> str:
    return f"Sleep {time_s}"


class Fixture:
    kb: KeyboardCommander
    mouse: MouseCommander

    all_signals: list[Signal]
    runner: ActionRunner
    _acts: dict[int, Callable[[], partial]]
    actions: list[int]

    def act(self, n: int) -> Callable[[], partial]:
        if n not in self._acts:
            self._acts[n] = lambda: partial(self.actions.append, n)
        return self._acts[n]


@pytest.fixture
def f(dummy: Dummy) -> Fixture:
    listener = dummy.Listener.get_for_os("")
    configuration.listeners = [listener]

    f = Fixture()
    f._acts = {}
    f.actions = []
    f.all_signals = []

    f.kb = tapper.kb
    f.kb._commander = dummy.KbCmd(listener, f.all_signals)
    f.mouse = tapper.mouse
    f.mouse._commander = dummy.MouseCmd(listener, f.all_signals)

    def sleep_fake(time_s: float) -> None:
        f.all_signals.append((sleep(time_s), KeyDirBool.DOWN))
        if time_s > 0:
            time.sleep(0.01)  # for concurrent action tests

    tapper._send_processor.sleep_fn = sleep_fake

    return f


@pytest.mark.xfail
class TestSimple:
    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add(Tap("a", f.act(1)))
        tapper.start(False)
        f.kb.press("a")
        assert f.all_signals == [down("a")]
        assert f.actions == [1]

    # def test_simplest(self, tap_fixt: Fixture) -> None:
    #     pass
    #
    # def test_simplest(self, tap_fixt: Fixture) -> None:
    #     pass
    #
    # def test_simplest(self, tap_fixt: Fixture) -> None:
    #     pass
    #
    # def test_simplest(self, tap_fixt: Fixture) -> None:
    #     pass
