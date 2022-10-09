import re
from typing import Any

from tapper.model import constants
from tapper.model import keyboard
from tapper.model.errors import TriggerParseError
from tapper.model.trigger import AuxiliaryKey
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger
from tapper.model.types_ import SymbolsWithAliases

SYMBOL_DELIMITER = "+"
PROPERTY_DELIMITER = " "
SHIFT_LIST = keyboard.aliases["shift"]


def split(text: str, delimiter: str, min_len: int = 1) -> list[str]:
    """Split str, with minimum length of tokens.

    Allows using the same delimiter as token.

    Example:
        ("a++", "+") => ["a", "+"]
        ("++a++", "+") => ["+", "a", "+"]
    """
    if not text:
        return []
    if not delimiter:
        raise ValueError("No delimiter specified.")
    result = []
    start_pos = 0
    while (delim_pos := text.find(delimiter, start_pos + min_len)) != -1:
        result.append(text[start_pos:delim_pos])
        start_pos = delim_pos + len(delimiter)
    result.append(text[start_pos:])
    if not result[-1]:
        raise ValueError(f"Delimiter was in the last position in '{text}'.")
    return result


def _resolve_trigger_main_props(symbol_and_props: list[str]) -> dict[str, Any]:
    if len(symbol_and_props) <= 1:
        return {}
    props: dict[str, Any] = {}
    for prop in symbol_and_props[1:]:
        if re.fullmatch(r"\d*\.?\d+s", prop):
            props["time"] = float(prop[:-1])
        elif re.fullmatch(r"\d+ms", prop):
            props["time"] = float(prop[:-2]) / 1000
        elif prop == "up":
            props["direction"] = constants.KEY_DIR.UP
        else:
            raise TriggerParseError(f"Property unknown: '{prop}'")
    return props


def _resolve_trigger_aux_props(symbol_and_props: list[str]) -> dict[str, Any]:
    if len(symbol_and_props) <= 1:
        return {}
    props: dict[str, Any] = {}
    for prop in symbol_and_props[1:]:
        if re.fullmatch(r"\d*\.?\d+s", prop):
            props["time"] = float(prop[:-1])
        elif re.fullmatch(r"\d+ms", prop):
            props["time"] = float(prop[:-2]) / 1000
        else:
            raise TriggerParseError(f"Property unknown: '{prop}'")
    return props


class TriggerParser:
    """Parses trigger string supplied by the user."""

    registered_symbols: SymbolsWithAliases

    def __init__(self, symbols_to_register: list[SymbolsWithAliases]) -> None:
        self.registered_symbols = {}
        for symbol_dict in symbols_to_register:
            for symbol, value in symbol_dict.items():
                if symbol in self.registered_symbols:
                    raise ValueError(f"Symbol already registered: {symbol}")
                self.registered_symbols[symbol] = value

    def parse(self, trigger_text: str) -> Trigger:
        """Parse single combo, to be pressed in one go."""
        try:
            strs_symbols_props = split(trigger_text, SYMBOL_DELIMITER)
            symbols_props = [
                split(sym_prop, PROPERTY_DELIMITER) for sym_prop in strs_symbols_props
            ]
        except ValueError as e:
            raise TriggerParseError(
                f"Failed to parse trigger: '{trigger_text}', reason: {e}"
            )
        auxiliary = []
        for sym_props in symbols_props[:-1]:
            auxiliary.append(
                AuxiliaryKey(
                    self._resolve_symbol(sym_props[0]),
                    **_resolve_trigger_aux_props(sym_props),
                )
            )
        sym_props = symbols_props[-1]
        main = MainKey(
            self._resolve_symbol(sym_props[0]), **_resolve_trigger_main_props(sym_props)
        )

        keys = [main, *auxiliary]
        all_symbols = []
        for key in keys:
            for symbol in key.symbols:
                if symbol in all_symbols:
                    raise TriggerParseError(
                        f"Key detected twice in expression '{trigger_text}': '{symbol}'"
                    )
                all_symbols.append(symbol)

        implicit_shift = any(
            sym_props[0] in keyboard.chars_en_upper for sym_props in symbols_props
        )
        shift_already_present = any(shift in all_symbols for shift in SHIFT_LIST)
        if implicit_shift and not shift_already_present:
            auxiliary.append(AuxiliaryKey(SHIFT_LIST))

        return Trigger(main=main, aux=auxiliary)

    def _resolve_symbol(self, symbol: str) -> list[str]:
        """List of corresponding symbols."""
        try:
            symbols = self.registered_symbols[symbol]
        except KeyError:
            raise TriggerParseError(f"Symbol not registered: '{symbol}'")
        if lowercase := keyboard.chars_en_upper_to_lower.get(symbols[0], None):
            return [lowercase]
        return symbols
