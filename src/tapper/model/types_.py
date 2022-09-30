Signal = tuple[str, bool]
"""
:param symbol: for possible symbols see model/keyboard.py and similar.
        Alternatively, KeyboardSignalListener.get_possible_signal_symbols() and similar.
:param down: Is key pressed down? False if it is released.
"""
