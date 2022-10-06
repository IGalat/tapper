from dataclasses import dataclass


@dataclass(frozen=True)
class _TriggerKey:
    """A single key in trigger."""

    symbols: list[str]
    """Non-alias symbol(s) representing a key that can come from listeners.

        Example:
            For 'a' it's just ['a']
            For 'lmb' it's ['left_mouse_button']
            For 'alt' it's ['right_alt', 'left_alt', 'virtual_alt]
    """
    time: float
    """For main key: minimum time it has to be pressed for trigger to work.
    For auxiliary keys: minimum time between its press and main key press for the trigger to work."""


@dataclass(frozen=True)
class Trigger:
    """Signals are compared against this to determine if action should be performed."""

    auxiliary: list[_TriggerKey]
    """List of keys that have to be pressed before main key for trigger to work."""

    main: _TriggerKey
    """Main key that actually triggers the action, if other conditions are met."""

    main_direction: bool
    """When to trigger on main key: down(press)(True)/up(release)(False)."""
