from typing import Any
from typing import Callable

Signal = tuple[str, bool]
"""        (symbol, down)
Signal emitted by SignalListener. Is not alias to other symbol.

:param symbol: A symbol emitted by SignalListener.
        For possible symbols see implementations of
            SignalListener.get_possible_signal_symbols().
        Alternatively, look at tapper/model/keyboard.py and similar.
:param down: Is key pressed down? False if it is released.
"""

SymbolsWithAliases = dict[str, list[str] | None]
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

Action = Callable[[], Any]
"""An action to run in ActionRunner.
It must require no arguments. Use `functools.partial` to provide arguments beforehand."""
