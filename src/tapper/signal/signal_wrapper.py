from tapper.model import constants
from tapper.model.types_ import OnSignalFn
from tapper.model.types_ import Signal
from tapper.signal.base_signal_listener import SignalListener
from tapper.state import keeper
from tapper.util import event


class ListenerWrapper:
    """Adds higher-level logic to the listener:
    call to a state keeper, bounce of emulated signals and publishing of events."""

    listener: SignalListener
    """Underlying listener."""

    on_signal: OnSignalFn
    """External action to do on signal, if it's not emulated."""

    emul_keeper: keeper.Emul
    """Dependency injected, not a special instance."""

    state_keeper: keeper.Pressed
    """Dependency injected, not a special instance."""

    def __init__(
        self,
        listener: SignalListener,
        on_signal: OnSignalFn,
        emul_keeper: keeper.Emul,
        state_keeper: keeper.Pressed,
    ) -> None:
        listener.on_signal = self.on_signal_wrap
        self.listener = listener
        self.on_signal = on_signal
        self.emul_keeper = emul_keeper
        self.state_keeper = state_keeper

    def on_signal_wrap(self, signal: Signal) -> constants.ListenerResult:
        if self.emul_keeper.is_emulated(signal):
            self.state_keeper.key_event(signal)
            return constants.ListenerResult.PROPAGATE
        result = self.on_signal(signal)
        event.publish(self.listener.__class__.__name__, signal)
        self.state_keeper.key_event(signal)
        return result
