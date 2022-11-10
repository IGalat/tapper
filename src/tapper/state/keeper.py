import time
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from tapper.model import constants
from tapper.model.types_ import Signal


@dataclass
class Emul:
    """Keeps track of emulated actions."""

    to_emulate: set[tuple[Any, ...]] = field(default_factory=set)

    def will_emulate(self, *signal: Any) -> None:
        """Notify that will emulate a command.
        :param signal: Any symbol, props.
        """
        self.to_emulate.add(signal)

    def is_emulated(self, *signal: Any) -> bool:
        """Check if signal that was received is emulated.
        :param signal: Any symbol, props.
        """
        if signal in self.to_emulate:
            self.to_emulate.remove(signal)
            return True
        return False


@dataclass
class Pressed:
    """Keeps track of the currently pressed buttons."""

    registered_symbols: list[str] = field(default_factory=list)
    """Only keys that can be pressed down. No aliases."""
    pressed_keys: dict[str, float] = field(default_factory=dict)
    """Keys, and pressed at time."""

    def key_event(self, on_signal: Signal) -> None:
        symbol, direction = on_signal
        if direction == constants.KeyDirBool.DOWN:
            self.key_pressed(symbol)
        else:
            self.key_released(symbol)

    def key_pressed(self, symbol: str) -> None:
        """Key has been pressed."""
        if symbol in self.registered_symbols and symbol not in self.pressed_keys:
            self.pressed_keys[symbol] = time.perf_counter()

    def key_released(self, symbol: str) -> None:
        """Key has been released."""
        if symbol in self.pressed_keys:
            del self.pressed_keys[symbol]

    def get_state(self, current_time: float) -> dict[str, float]:
        """Keys currently pressed and for how long."""
        return {
            s: current_time - pressed_at
            for (s, pressed_at) in self.pressed_keys.items()
        }
