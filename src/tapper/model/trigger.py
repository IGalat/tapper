from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from dataclasses import field


@dataclass
class TriggerKey(ABC):
    """A single key in trigger."""

    symbols: list[str]
    """Non-alias symbol(s) representing a key that can come from listeners.

        Example:
            For 'a' it's just ['a']
            For 'lmb' it's ['left_mouse_button']
            For 'alt' it's ['right_alt', 'left_alt', 'virtual_alt']
    """


@dataclass
class MainKey(TriggerKey):
    """Key that actually triggers the action, if other conditions are met."""

    time: float = field(default=0)
    """Minimum time it has to be pressed for trigger to work. (! or released after. see future plans)"""
    direction: bool = True
    """When to trigger on main key: down(press)(True)/up(release)(False)."""


@dataclass
class AuxiliaryKey(TriggerKey):
    """Key that must be pressed in a combination with main key."""

    time: float = field(default=0)
    """Minimum time between its press and main signal for the trigger to work."""


@dataclass(frozen=True)
class Trigger:
    """Signals are compared against this to determine if action should be performed."""

    main: MainKey
    aux: list[AuxiliaryKey] = field(default_factory=list)
    """List of keys that have to be pressed before main key for trigger to work."""
