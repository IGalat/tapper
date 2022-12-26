import time

import pytest
from tapper.boot import initializer
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.model import constants
from tapper.model.types_ import Signal
from tapper.signal.wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import event
from testutil_model import Dummy

now = time.perf_counter()


def down(symbol: str) -> Signal:
    return symbol, constants.KeyDirBool.DOWN


def up(symbol: str) -> Signal:
    return symbol, constants.KeyDirBool.UP


def click(symbol: str) -> tuple[Signal, Signal]:
    return down(symbol), up(symbol)


def sleep(time_s: float) -> Signal:
    return down(f"sleep {time_s}")


class TestSendCommandProcessor:
    sender: SendCommandProcessor
    pressed: keeper.Pressed
    all_signals: list[Signal]
    real_signals: list[Signal]
    """Should be empty in this test: send means emul only."""
    mc: MouseController
    toggled: list[str]

    @pytest.fixture(autouse=True)
    def setup(self, dummy: Dummy) -> None:
        self.all_signals = []
        self.real_signals = []

        pressed = initializer.default_keeper_pressed()
        self.pressed = pressed

        emul = keeper.Emul()
        toggled = []
        self.toggled = toggled

        parser = initializer.default_send_parser()

        listener = dummy.Listener()
        ListenerWrapper(
            lambda _: constants.ListenerResult.PROPAGATE,
            emul,
            pressed,
        ).wrap(listener)

        kb_tc = dummy.KbTC(listener, self.all_signals, None, toggled)
        kbc = KeyboardController()
        kbc._tracker, kbc._commander, kbc._emul_keeper = kb_tc, kb_tc, emul

        mouse_tc = dummy.MouseTC(listener, self.all_signals, None, toggled)
        mc = MouseController()
        mc._tracker, mc._commander, mc._emul_keeper = mouse_tc, mouse_tc, emul
        self.mc = mc

        self.sender = SendCommandProcessor("", parser, kbc, mc, 0)
        self.sender.sleep_fn = lambda f: self.all_signals.append(sleep(f))

        event.subscribe(listener.name, lambda signal: self.real_signals.append(signal))

    def test_simplest(self) -> None:
        self.sender.send("a")
        assert not self.real_signals
        assert not self.pressed.get_state(now)
        assert self.all_signals == [down("a"), up("a")]

    def test_state_after(self) -> None:
        self.sender.send("$(alt down)")
        assert not self.real_signals
        assert self.pressed.get_state(now)["left_alt"]
        assert self.all_signals == [down("left_alt")]

    def test_many_keys_with_combo(self) -> None:
        self.sender.send("Hi\n$(ctrl+c,v down)")
        assert not self.real_signals
        assert self.pressed.get_state(now)["v"]
        assert self.all_signals == [
            down("left_shift"),
            *click("h"),
            up("left_shift"),
            *click("i"),
            *click("enter"),
            down("left_control"),
            *click("c"),
            down("v"),
            up("left_control"),
        ]

    def test_sleep(self) -> None:
        self.sender.send("$(lmb 1ms+\t 20ms;1s)")
        assert not self.real_signals
        assert not self.pressed.get_state(now)
        assert self.all_signals == [
            down("left_mouse_button"),
            sleep(0.001),
            down("tab"),
            sleep(0.02),
            up("tab"),
            up("left_mouse_button"),
            sleep(1.0),
        ]

    def test_default_interval(self) -> None:
        self.sender.default_interval = 0.5
        self.sender.send("hello")
        result = []
        for letter in "hello":
            result.append(sleep(0.5))
            result.extend(click(letter))
        assert self.all_signals == result

    def test_interval_variable(self) -> None:
        self.sender.default_interval = 0.1
        self.sender.send("hi")
        self.sender.send("q", interval=10)
        assert self.all_signals == [
            sleep(0.1),
            *click("h"),
            sleep(0.1),
            *click("i"),
            sleep(10),
            *click("q"),
        ]

    def test_speed(self) -> None:
        self.sender.send("w$(10ms)e", speed=0.02)
        self.sender.send("z$(20s)x", speed=5)
        assert self.all_signals == [
            *click("w"),
            sleep(0.5),
            *click("e"),
            *click("z"),
            sleep(4.0),
            *click("x"),
        ]

    def test_speed_and_interval(self) -> None:
        self.sender.send("h$(1s)k", interval=0.1, speed=2)
        assert self.all_signals == [
            sleep(0.1),
            *click("h"),
            sleep(0.5),
            sleep(0.1),
            *click("k"),
        ]

    def test_wheel_and_cursor(self) -> None:
        self.sender.send("$(x230y340;wheel_up)")
        assert self.all_signals == [down("scroll_wheel_up")]
        assert self.mc.get_pos() == (230, 340)

    def test_on_off(self) -> None:
        self.toggled.append("scroll_lock")
        self.sender.send("$(scroll_lock on;caps off)")
        assert not self.all_signals

        self.sender.send("$(scroll_lock off;caps on)")
        assert self.all_signals == [*click("scroll_lock"), *click("caps_lock")]
