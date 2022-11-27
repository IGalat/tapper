from functools import partial

from tapper.model import constants
from tapper.model.types_ import OnSignalFn
from tapper.model.types_ import Signal
from tapper.signal.base_listener import SignalListener
from tapper.state import keeper
from tapper.util import event


class ListenerWrapper:
    """Adds higher-level logic to the listener:
    call to a state keeper, bounce of emulated signals and publishing of events."""

    on_signal: OnSignalFn
    """External action to do on signal, if it's not emulated."""

    emul_keeper: keeper.Emul
    """Dependency injected, not a special instance."""

    state_keeper: keeper.Pressed
    """Dependency injected, not a special instance."""

    def __init__(
        self,
        on_signal: OnSignalFn,
        emul_keeper: keeper.Emul,
        state_keeper: keeper.Pressed,
    ) -> None:
        self.on_signal = on_signal
        self.emul_keeper = emul_keeper
        self.state_keeper = state_keeper

    def wrap(self, listener: SignalListener) -> None:
        listener.on_signal = partial(
            self._on_signal_wrap, topic=listener.__class__.__name__
        )

    def _on_signal_wrap(self, signal: Signal, topic: str) -> constants.ListenerResult:
        if self.emul_keeper.is_emulated(signal):
            self.state_keeper.key_event(signal)
            return constants.ListenerResult.PROPAGATE
        result = self.on_signal(signal)
        event.publish(topic, signal)
        self.state_keeper.key_event(signal)
        return result
