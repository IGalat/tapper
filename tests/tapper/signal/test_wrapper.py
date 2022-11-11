import time

import pytest
from tapper import dummy
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.types_ import Signal
from tapper.signal.base_signal_listener import SignalListener
from tapper.signal.signal_wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import event


def noop(no: Signal) -> constants.ListenerResult:
    pass


WrapFixture = tuple[ListenerWrapper, SignalListener, keeper.Emul, keeper.Pressed]


@pytest.fixture
def wrap_fixture() -> WrapFixture:
    emul = keeper.Emul()
    pressed = keeper.Pressed()
    pressed.registered_symbols.extend(keyboard.get_key_list())
    pressed.registered_symbols.extend(mouse.regular_buttons)

    listener = dummy.Listener()
    wrapper = ListenerWrapper(listener, noop, emul, pressed)
    return wrapper, listener, emul, pressed


def down(symbol: str) -> Signal:
    return symbol, constants.KeyDirBool.DOWN


def up(symbol: str) -> Signal:
    return symbol, constants.KeyDirBool.UP


def test_simplest(wrap_fixture: WrapFixture) -> None:
    _, listener, _, pressed = wrap_fixture
    listener.on_signal(down("a"))
    state = pressed.get_state(time.perf_counter())
    assert state["a"] > 0


def test_subscription(wrap_fixture: WrapFixture) -> None:
    _, listener, _, pressed = wrap_fixture
    subscription_log: list[Signal] = []

    def sub_fn(signal: Signal) -> None:
        nonlocal subscription_log
        subscription_log.append(signal)

    event.subscribe(listener.__class__.__name__, sub_fn)

    will_signal = [
        down("a"),
        up("a"),
        down("left_control"),
        down("c"),
        up("c"),
        up("left_control"),
    ]

    [listener.on_signal(signal) for signal in will_signal]

    state = pressed.get_state(time.perf_counter())
    assert not state

    assert subscription_log == will_signal


def test_suppress(wrap_fixture: WrapFixture) -> None:
    wrapper, listener, _, pressed = wrap_fixture

    def on_ctrl_alt_0(signal: Signal) -> constants.ListenerResult:
        nonlocal pressed
        state = pressed.get_state(time.perf_counter())
        if signal == down("0"):
            if "left_control" in state and "left_alt" in state:
                return constants.ListenerResult.SUPPRESS
        return constants.ListenerResult.PROPAGATE

    wrapper.on_signal = on_ctrl_alt_0

    will_signal = [
        down("a"),
        down("0"),
        up("a"),
        up("0"),
        down("left_control"),
        down("c"),
        up("c"),
        down("left_alt"),
        down("0"),
        up("left_alt"),
        up("0"),
        up("left_control"),
    ]

    signals_propagated = [listener.on_signal(signal) for signal in will_signal]

    expected = [constants.ListenerResult.PROPAGATE for _ in range(len(will_signal))]
    expected[8] = constants.ListenerResult.SUPPRESS

    assert signals_propagated == expected
