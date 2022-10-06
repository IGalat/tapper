from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from tapper.util import type_check


@dataclass(init=False)
class TriggerKey:
    """A single key in trigger."""

    symbols: list[str]
    """Non-alias symbol(s) representing a key that can come from listeners.

        Example:
            For 'a' it's just ['a']
            For 'lmb' it's ['left_mouse_button']
            For 'alt' it's ['right_alt', 'left_alt', 'virtual_alt]
    """
    time: float = field(default=0)
    """For main key: minimum time it has to be pressed for trigger to work. (! or released after. see future plans)
    For auxiliary keys: minimum time between its press and main signal for the trigger to work."""

    def __init__(self, symbols: list[str], time: float = 0) -> None:
        self.symbols = symbols
        self.time = time


@dataclass(frozen=True)
class Trigger:
    """Signals are compared against this to determine if action should be performed."""

    main: TriggerKey
    """Main key that actually triggers the action, if other conditions are met."""

    main_direction: bool = True
    """When to trigger on main key: down(press)(True)/up(release)(False)."""

    auxiliary: list[TriggerKey] = field(default_factory=list)
    """List of keys that have to be pressed before main key for trigger to work."""

    @classmethod
    def from_simple(cls, main: list[str], aux: list[str] | None = None) -> Trigger:
        main_ = TriggerKey(main)
        aux_: list[TriggerKey] = []
        if type_check.is_list_of(aux, str):
            aux_ = [TriggerKey(aux)]  # type: ignore
        return Trigger(main=main_, auxiliary=aux_)
