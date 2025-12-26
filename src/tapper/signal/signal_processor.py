import time

from tapper.action import wrapper
from tapper.action.runner import ActionRunner
from tapper.feedback.logger import LogExceptions
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap
from tapper.model.types_ import Signal
from tapper.state import keeper


class SignalProcessor:
    """Highest-level component for signal processing."""

    root: SGroup
    control: SGroup
    state_keeper: keeper.Pressed
    runner: ActionRunner

    def __init__(
        self,
        root: SGroup,
        control: SGroup,
        state_keeper: keeper.Pressed,
        runner: ActionRunner,
    ) -> None:
        self.root = root
        self.control = control
        self.state_keeper = state_keeper
        self.runner = runner

    @LogExceptions()
    def on_signal(self, signal: Signal) -> ListenerResult:
        """
        This method is used in wrapped listeners.
        Only real signals are expected.
        """
        symbol, direction = signal
        state = self.state_keeper.get_state(time.perf_counter())
        if tap := self.match(self.control, symbol, direction, state):
            self.runner.run_control(wrapper.wrapped_action(tap))
            return tap.suppress_trigger
        elif tap := self.match(self.root, symbol, direction, state):
            self.runner.run(wrapper.wrapped_action(tap), tap.executor)
            return tap.suppress_trigger
        else:
            return ListenerResult.PROPAGATE

    def match(
        self, group: SGroup, symbol: str, direction: KeyDirBool, state: dict[str, float]
    ) -> STap | None:
        """Find first Tap that matches, recursive."""
        if symbol not in group.get_main_triggers(direction):  # type: ignore
            return None
        if not all(bool(fn()) for fn in group.trigger_conditions):
            return None

        for child in reversed(group.children):
            if isinstance(child, SGroup):
                if found := self.match(child, symbol, direction, state):
                    return found
            elif isinstance(child, STap):
                if self.tap_matches(child, symbol, direction, state):
                    return child
            else:
                raise ValueError(f"FATAL TYPE MISMATCH: {type(child) = }")
        return None

    def tap_matches(
        self, tap: STap, symbol: str, direction: KeyDirBool, state: dict[str, float]
    ) -> bool:
        """Check if Tap matches all conditions."""
        if symbol not in tap.get_main_triggers(direction):
            return False
        if len(state) < len(tap.trigger.aux):
            return False
        if not all(bool(fn()) for fn in tap.trigger_conditions):
            return False

        for aux in tap.trigger.aux:
            pressed = False
            for aux_symbol in aux.symbols:
                if aux_symbol in state and aux.time <= state[aux_symbol]:
                    pressed = True
                    break
            if not pressed:
                return False

        if tap.trigger.main.time:
            if symbol in state and tap.trigger.main.time < state[symbol]:
                return True
            else:
                return False

        return True
