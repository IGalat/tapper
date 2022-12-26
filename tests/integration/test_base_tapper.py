import time
from functools import partial

import tapper
from integration.conftest import click
from integration.conftest import ends_with
from integration.conftest import Fixture
from integration.conftest import sleep_signal
from tapper import config
from tapper import Group
from tapper import Tap


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
