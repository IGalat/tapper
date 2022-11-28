import time

import pytest
from conftest import Dummy
from conftest import DummyActionRunner
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap
from tapper.model.trigger import AuxiliaryKey
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger
from tapper.model.types_ import Action
from tapper.model.types_ import Signal
from tapper.signal.processor import SignalProcessor
from tapper.state import keeper

generic_action = lambda: "Will check if this was scheduled to run."

left_control = "left_control"
right_control = "right_control"
virtual_control = "virtual_control"
ctrl = [left_control, right_control, virtual_control]

left_alt = "left_alt"
right_alt = "right_alt"
virtual_alt = "virtual_alt"
alt = [left_alt, right_alt, virtual_alt]


def tap(
    keys: list[list[str]],
    action: Action = generic_action,
    time_main: float = 0,
    direction: KeyDirBool = KeyDirBool.DOWN,
    ordinal: int = 0,
    result: ListenerResult = ListenerResult.SUPPRESS,
) -> STap:
    main = MainKey(keys[-1], time_main, direction=direction)
    aux = keys[:-1] if len(keys) > 1 else []
    trigger = Trigger(main, [AuxiliaryKey(arr) for arr in aux])
    return STap(trigger, action, ordinal, result)


def down(symbol: str) -> Signal:
    return symbol, KeyDirBool.DOWN


def up(symbol: str) -> Signal:
    return symbol, KeyDirBool.UP


class TestSignalProcessor:
    root: SGroup
    control: SGroup
    state_keeper: keeper.Pressed
    runner: DummyActionRunner
    processor: SignalProcessor

    @pytest.fixture(autouse=True)
    def setup(self, dummy: Dummy) -> None:
        self.root = SGroup()
        self.control = SGroup()
        pressed = keeper.Pressed()
        pressed.registered_symbols.extend(keyboard.get_key_list())
        pressed.registered_symbols.extend(mouse.regular_buttons)
        self.state_keeper = pressed
        self.runner = dummy.ActionRunner()
        self.processor = SignalProcessor.from_all(
            self.root, self.control, pressed, self.runner
        )

    def test_simplest(self) -> None:
        self.root.add(tap([["a"]]))
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

    def test_with_aux(self) -> None:
        self.root.add(tap([["a"], ["left_mouse_button"], ["f1"]]))
        assert self.processor.on_signal(down("f1")) == ListenerResult.PROPAGATE

        self.press("a")
        assert self.processor.on_signal(down("f1")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]

        self.press("left_mouse_button")
        assert self.processor.on_signal(down("f1")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

        assert self.processor.on_signal(down("f1")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action] * 2

    def test_multi_aux(self) -> None:
        self.root.add(tap([ctrl, ["a"]]))
        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]

        self.press(["q", "left_alt"])
        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]

        self.press(right_control)
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

        self.press(left_control)
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action] * 2

    def test_multi_main(self) -> None:
        self.root.add(tap([ctrl]))
        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]
        assert self.processor.on_signal(down(left_control)) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]
        assert self.processor.on_signal(down(right_control)) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action] * 2

    def test_multi_both_up(self) -> None:
        self.root.add(tap([ctrl, alt], direction=KeyDirBool.UP))
        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]
        assert self.processor.on_signal(down(left_alt)) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]

        self.press(left_control)
        assert self.processor.on_signal(up(left_alt)) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]
        assert self.processor.on_signal(down(right_control)) == ListenerResult.PROPAGATE

    def test_time_simplest(self) -> None:
        self.root.add(tap([["a"]], time_main=0.5, direction=KeyDirBool.UP))
        assert self.processor.on_signal(up("a")) == ListenerResult.PROPAGATE
        assert not self.runner.actions_ran[0]

        self.press({"a": 0.5})
        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert self.processor.on_signal(up("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

    def test_time_aux(self) -> None:
        stap = tap([alt, ["wheel_up"]])
        stap.trigger.aux[0].time = 2
        self.root.add(stap)
        assert self.processor.on_signal(down("wheel_up")) == ListenerResult.PROPAGATE

        self.press(left_alt)
        assert self.processor.on_signal(down("wheel_up")) == ListenerResult.PROPAGATE

        self.press({left_alt: 1})
        assert self.processor.on_signal(down("wheel_up")) == ListenerResult.PROPAGATE

        self.press({left_alt: 2.2})
        assert self.processor.on_signal(down("wheel_up")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

    def test_nested_simplest(self) -> None:
        self.root.add(SGroup().add(tap([["a"]])))
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

    def test_order(self) -> None:
        another_action = lambda: "some"
        third_action = lambda: "some3"
        self.root.add(
            tap([alt, ["a"]], action=third_action),
            tap([ctrl, ["a"]], action=another_action),
            tap([["a"]]),
        )

        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action]

        self.press(right_control)
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [generic_action, another_action]

        self.press(left_alt)
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [
            generic_action,
            another_action,
            third_action,
        ]

        self.state_keeper.key_released(left_alt)
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert self.runner.actions_ran[0] == [
            generic_action,
            another_action,
            third_action,
            another_action,
        ]

    def test_order_with_control(self) -> None:
        another_action = lambda: "some"
        self.root.add(tap([["a"]]))
        self.control.add(tap([["a"]], action=another_action))
        assert self.processor.on_signal(down("a")) == ListenerResult.SUPPRESS
        assert not self.runner.actions_ran[0]
        assert self.runner.control_actions_ran == [another_action]

    def test_different_executors(self) -> None:
        self.root.add(tap([["b"]], ordinal=1))
        self.root.add(tap([["c"]], ordinal=2))

        assert self.processor.on_signal(down("a")) == ListenerResult.PROPAGATE
        assert self.processor.on_signal(down("b")) == ListenerResult.SUPPRESS
        assert self.processor.on_signal(down("c")) == ListenerResult.SUPPRESS
        assert (
            self.runner.actions_ran[1] == self.runner.actions_ran[2] == [generic_action]
        )

    """UTIL"""

    def press(self, keys: str | list[str] | dict[str, float]) -> None:
        if isinstance(keys, str):
            keys = [keys]
        if isinstance(keys, list):
            keys = {key: 0 for key in keys}
        if isinstance(keys, dict):
            now = time.perf_counter()
            for symbol, offset in keys.items():
                self.state_keeper.pressed_keys[symbol] = now - offset
