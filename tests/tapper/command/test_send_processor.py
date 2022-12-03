import time
from typing import Callable

import pytest
from conftest import Dummy
from tapper.boot import initializer
from tapper.command.keyboard.keyboard_commander import KeyboardCmdProxy
from tapper.command.mouse.mouse_commander import MouseCmdProxy
from tapper.command.send_processor import SendCommandProcessor
from tapper.model import constants
from tapper.model.types_ import Signal
from tapper.signal.wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import event

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
    send: Callable[[str], None]
    pressed: keeper.Pressed
    all_signals: list[Signal]
    real_signals: list[Signal]
    """Should be empty in this test: send means emul only."""

    @pytest.fixture(autouse=True)
    def setup(self, dummy: Dummy) -> None:
        self.all_signals = []
        self.real_signals = []

        pressed = initializer.default_keeper_pressed()
        self.pressed = pressed

        emul = keeper.Emul()

        parser = initializer.default_send_parser()

        listener = dummy.Listener()
        ListenerWrapper(
            lambda _: constants.ListenerResult.PROPAGATE,
            emul,
            pressed,
        ).wrap(listener)

        kbc = KeyboardCmdProxy.from_all(dummy.KbCmd(listener, self.all_signals), emul)
        mousec = MouseCmdProxy.from_all(
            dummy.MouseCmd(listener, self.all_signals), emul
        )

        self.sender = SendCommandProcessor("", parser, kbc, mousec)
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
        self.sender.send("$(alt 1ms+\t 20ms;1s)")
        assert not self.real_signals
        assert not self.pressed.get_state(now)
        assert self.all_signals == [
            down("left_alt"),
            sleep(0.001),
            down("tab"),
            sleep(0.02),
            up("tab"),
            up("left_alt"),
            sleep(1.0),
        ]
