import time
from functools import partial
from typing import Any
from typing import Callable

import pytest
import tapper
from conftest import Dummy
from tapper import config
from tapper import Group
from tapper import Tap
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.model.constants import KeyDirBool
from tapper.model.types_ import SendFn
from tapper.model.types_ import Signal
from tapper.state import keeper


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


def append(arr: list[Any], item: Any) -> None:
    arr.append(item)


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
            self._acts[n] = partial(append, self.actions, n)
        return self._acts[n]


@pytest.fixture
def f(dummy: Dummy, is_debug: bool) -> Fixture:
    debug_sleep_mult = 5 if is_debug else 1

    # restore default before each
    config.action_runner_executors_threads = [1]
    tapper.root = Group("root")
    tapper.control_group = Group("control_group")
    tapper._initialized = False

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

    def sleep_logged(time_s: float, signals: list[Signal]) -> None:
        signals.append(sleep_signal(time_s))
        time.sleep(time_s)

    sender = tapper._send_processor
    sender.sleep_fn = partial(sleep_logged, signals=fixture.emul_signals)

    def send_and_sleep(send: SendFn, command: str) -> None:
        send(command)
        time.sleep(0.01 * debug_sleep_mult)  # so actions can run their course

    real_sender = SendCommandProcessor.from_none()
    fixture.send_real = partial(send_and_sleep, real_sender.send)

    def start() -> None:
        tapper.init()  # this will init sender
        real_sender.os = sender.os
        real_sender.parser = sender.parser
        real_sender.sleep_fn = partial(sleep_logged, signals=fixture.real_signals)

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

        tapper.start(False)

    fixture.start = start  # type: ignore

    return fixture


class TestSimple:
    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add(Tap("a", f.act(1)))
        tapper.root.add(Tap("b", "q"))
        f.start()

        f.send_real("a")
        assert f.real_signals == click("a")
        assert f.actions == [1]

        f.send_real("b")
        assert f.real_signals == [*click("a"), *click("b")]
        assert f.emul_signals == click("q")

    def test_up(self, f: Fixture) -> None:
        tapper.root.add({"alt up": "q"})
        f.start()

        f.send_real("$(ralt down)")
        assert not f.emul_signals
        f.send_real("$(ralt up)")
        assert f.emul_signals == click("q")

    def test_time(self, f: Fixture) -> None:
        config.action_runner_executors_threads = [5]
        tapper.root.add(
            {
                "shift": f.act(1),
                "shift 50ms up": f.act(2),
                "shift 50ms+enter": f.act(3),
                " ": f.act(4),
                "  up 50ms": f.act(5),
                " +enter up 50ms": f.act(6),
            }
        )
        f.start()

        f.send_real("$(shift down)")
        time.sleep(0.05)
        f.send_real("$(enter;shift up)")
        assert f.actions == [1, 3, 2]

        f.send_real(" ")
        assert ends_with(f.actions, [4])
        assert 5 not in f.actions

        f.send_real("$(  down)")
        assert ends_with(f.actions, [4, 4])
        assert 5 not in f.actions

        time.sleep(0.05)
        f.send_real("$(  up)")
        assert ends_with(f.actions, [5])

        f.send_real("$(  down;enter down)")
        time.sleep(0.05)
        f.send_real("$(enter up;  up)")
        assert ends_with(f.actions, [4, 6, 5])

    def test_trigger_if(self, f: Fixture) -> None:
        conditions = []
        is_in_conditions = lambda x: x in conditions

        tapper.root.add(
            {"q": "0"},
            Group(trigger_if=partial(is_in_conditions, 1)).add({"q": "1"}),
            Tap("q", "2", trigger_if=partial(is_in_conditions, 2)),
        )
        f.start()

        f.send_real("q")
        assert f.emul_signals == click("0")

        conditions.append(1)
        f.send_real("q")
        assert f.emul_signals == click("01")

        conditions.append(2)
        f.send_real("q")
        assert f.emul_signals == click("012")


class TestTreeOrder:
    """React to the last trigger that matches, depth-first."""

    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add(Tap("a", f.act(1)))  # never triggers
        tapper.root.add(Tap("a", f.act(2)))
        f.start()

        f.send_real("aa")
        assert f.real_signals == click("a") * 2
        assert f.actions == [2, 2]

    def test_nested(self, f: Fixture) -> None:
        group1_1 = Group("nested twice").add({"ctrl+1": "w/ctrl"})
        group1 = Group().add(Tap("ctrl+!", "never triggers"), group1_1, {"!": "excl"})
        group2 = Group().add({"ctrl": "control", "left_alt+ctrl": "flip"})
        tapper.root.add({"1": "first"}, group1, group2, {"ctrl+left_alt+!": "last"})
        f.start()

        f.send_real("1")
        assert ends_with(f.emul_signals, click("first"))

        f.send_real("$(ctrl+left_alt 50ms+1)")
        assert ends_with(f.emul_signals, click("control" + "w/ctrl"))

        time.sleep(1)
        f.send_real("$(shift+1 50ms+ctrl)")
        assert ends_with(f.emul_signals, click("excl" + "control"))

        f.send_real("$(alt+ctrl 50ms+shift+1)")
        assert ends_with(f.emul_signals, click("flip" + "last"))


class TestConcurrentActions:
    def test_simplest(self, f: Fixture) -> None:
        tapper.root.add({"a": "$(1ms)", "b": "$(2ms)"})
        f.start()

        f.send_real("ab")
        assert f.emul_signals == [sleep_signal(0.001)]

    def test_actual_concurrent_simplest(self, f: Fixture) -> None:
        config.action_runner_executors_threads = [3]
        tapper.root.add({"a": "$(10ms)", "b": "$(20ms)"})
        f.start()

        f.send_real("ababab")
        assert f.emul_signals == [
            sleep_signal(0.01),
            sleep_signal(0.02),
            sleep_signal(0.01),
        ]

    def test_mix_concurrent(self, f: Fixture) -> None:
        config.action_runner_executors_threads = [1, 3]
        tapper.root.add(
            {
                "z": "$(1ms)",
                "x": "$(2ms)",
            },
            Group(executor=1).add(
                {
                    "a": "$(11ms)",
                    "s": "$(12ms)",
                    "d": "$(13ms)",
                    "f": "$(14ms)",
                    "g": "$(15ms)",
                    "h": "$(16ms)",
                }
            ),
        )
        f.start()

        f.send_real("xzhgfdsa")
        assert f.emul_signals == [sleep_signal(ms / 1000) for ms in [2, 16, 15, 14]]


class TestTriggerConditions:
    def test_trigger_if(self, f: Fixture) -> None:
        flag = True
        tapper.root.add(
            Tap("t", "0"),
            Tap("t", "1", trigger_if=lambda: not flag),
            Tap("t", "2", trigger_if=lambda: flag),
        )
        f.start()

        f.send_real("t")
        assert ends_with(f.emul_signals, click("2"))

        flag = False
        f.send_real("t")
        assert ends_with(f.emul_signals, click("1"))

    def test_toggled(self, f: Fixture) -> None:
        tapper.root.add(
            Tap("t", "0"),
            Tap("t", "1", toggled_on="caps"),
            Tap("t", "2", toggled_on="num_lock"),
            Tap("p", "9"),
            Tap("p", "8", toggled_off="q"),
            Tap("p", "7", toggled_off="w"),
        )
        f.start()

        tp = lambda: f.send_real("t$(50ms)p")

        tp()
        assert ends_with(f.emul_signals, click("07"))

        f.toggled.extend(["caps", "w"])
        tp()
        assert ends_with(f.emul_signals, click("18"))

        f.toggled.extend(["num_lock", "q"])
        tp()
        assert ends_with(f.emul_signals, click("29"))

        f.toggled.clear()
        tp()
        assert ends_with(f.emul_signals, click("07"))

    def test_cursor_near(self, f: Fixture) -> None:
        tapper.root.add(
            Tap("\n", "0"),
            Tap("\n", "1", cursor_near=((500, 500), 200)),
            Tap("\n", "2", cursor_near=((500, 500), 50)),
        )
        f.start()

        tapper.mouse.move(1, 1)
        f.send_real("\n")
        assert ends_with(f.emul_signals, click("0"))

        tapper.mouse.move(400, 400)
        f.send_real("\n")
        assert ends_with(f.emul_signals, click("1"))

        tapper.mouse.move(510, 490)
        f.send_real("\n")
        assert ends_with(f.emul_signals, click("2"))

    def test_cursor_in(self, f: Fixture) -> None:
        tapper.root.add(
            Tap("a", "0"),
            Tap("a", "1", cursor_in=((10, 10), (20, 20))),
            Tap("a", "2", cursor_in=((500, 500), (600, 600))),
        )
        f.start()

        tapper.mouse.move(1, 1)
        f.send_real("a")
        assert ends_with(f.emul_signals, click("0"))

        tapper.mouse.move(10, 10)
        f.send_real("a")
        tapper.mouse.move(15, 15)
        f.send_real("a")
        tapper.mouse.move(20, 20)
        f.send_real("a")
        assert ends_with(f.emul_signals, click("111"))

        tapper.mouse.move(500, 600)
        f.send_real("a")
        assert ends_with(f.emul_signals, click("2"))
