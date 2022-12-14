from typing import Any
from typing import Callable

from tapper.model import constants

Signal = tuple[str, constants.KeyDirBool]
"""        (symbol, down)
Signal emitted by SignalListener. Is not alias to other symbol.

:param symbol: A symbol emitted by SignalListener.
        For possible symbols see implementations of
            SignalListener.get_possible_signal_symbols().
        Alternatively, look at tapper/model/keyboard.py and similar.
"""

OnSignalFn = Callable[[Signal], constants.ListenerResult]
"""An action to execute on receiving a signal from a listener."""

SymbolsWithAliases = dict[str, list[str]]
"""              symbol/alias, reference
A collection of symbols that may be aliases to other symbols, or not.

:param symbol or alias: Symbol that can be used for command or triggering.
:param reference: If None, the symbol(key of dict) is not an alias. If present, then
    the symbol is an alias, and each element refers to actual symbols, not other aliases.

This is used for:
 - giving commands to specific commanders
 - reacting to signals, in triggers

Example:
    left_control: None
    lctrl: [left_control]
    ctrl: [left_control, right_control]

    Keyboard command to press "ctrl" will press its first reference - left_control.

    Trigger for "ctrl" will work when signal is received for any of the references.
"""

TriggerStr = str
"""Combo or a single key that will trigger the action.

Examples:
    a
    ctrl+f11
    scroll_up
    left_mouse_button+j

Last key in the combo is called main key, other keys are auxiliary.
"""

Action = Callable[[], Any]
"""An action to run in ActionRunner.
It must require no arguments. Use `functools.partial` to provide arguments beforehand."""

SendFn = Callable[[str], None]
"""Send command type."""

TriggerIfFn = Callable[[], bool]
"""Tap cannot trigger unless this resolves to True."""

TriggerConditionFn = Callable[[], Any]
"""Actual trigger condition."""

KwTriggerConditions = dict[str, Callable[[Any], Any]]
"""Keyword trigger conditions that can be used as part of Tap or Group. See config for docs."""
