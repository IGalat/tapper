import re
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Iterator

from tapper.model import constants
from tapper.model import keyboard
from tapper.model.errors import TriggerParseError
from tapper.model.trigger import AuxiliaryKey
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger
from tapper.model.types_ import SymbolsWithAliases
from tapper.parser import common
from tapper.util import datastructs

SYMBOL_DELIMITER = "+"
PROPERTY_DELIMITER = " "
_SHIFT_LIST = keyboard.aliases["shift"]


@dataclass
class _TriggerProp:
    regex: re.Pattern[str]
    name: str
    fn: Callable[[str], Any]


_COMMON_PROPS = {
    "Time in seconds": _TriggerProp(common.SECONDS.regex, "time", common.SECONDS.fn),
    "Time in millis": _TriggerProp(common.MILLIS.regex, "time", common.MILLIS.fn),
}
_MAIN_PROPS = {
    **_COMMON_PROPS,
    "up": _TriggerProp(
        re.compile(r"up"), "direction", lambda _: constants.KeyDirBool.UP
    ),
}
_AUX_PROPS = {**_COMMON_PROPS}


def _resolve_props(
    props: list[str], allowed_props: dict[str, _TriggerProp]
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for prop in props:
        for candidate in allowed_props.values():
            if candidate.regex.fullmatch(prop):
                result[candidate.name] = candidate.fn(prop)
                break
        else:
            raise TriggerParseError(f"Unknown property: '{prop}'")
    return result


@dataclass
class _Key:
    """Half-parsed trigger key."""

    symbols: list[str]
    """Parsed symbols. Non-aliases."""
    props: list[str]
    """Unparsed properties."""


def _lower_and_add_shift_if_required(keys: list[_Key]) -> list[_Key]:
    """
    Maps all uppercase keys to lowercase, and adds shift if
    not already present and any uppercase present.
    """
    implied_shift = False
    shift_present = False
    for key in keys:
        if lower := keyboard.chars_en_upper_to_lower.get(key.symbols[0]):
            implied_shift = True
            key.symbols = [lower]
        elif key.symbols[0] in _SHIFT_LIST:
            shift_present = True
    if implied_shift and not shift_present:
        main = keys.pop()
        keys.append(_Key(_SHIFT_LIST, []))
        keys.append(main)
    return keys


def _validate(trigger: Trigger) -> None:
    aux_symbols = [aux.symbols for aux in trigger.aux]
    symbols_already_present = []
    for symbol in datastructs.to_flat_list([aux_symbols, trigger.main.symbols]):
        if symbol in symbols_already_present:
            raise TriggerParseError(
                f"Key detected twice in trigger '{trigger}': '{symbol}'"
            )
        symbols_already_present.append(symbol)


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

    def parse(self, trigger_text: Trigger) -> Trigger:
        """Parse single combo, to be pressed in one go."""
        try:
            keys = list(self._parse_keys(trigger_text))
        except ValueError as e:
            raise TriggerParseError(f"Trigger: '{trigger_text}', error: {e}")
        keys = _lower_and_add_shift_if_required(keys)
        main = MainKey(keys[-1].symbols, **_resolve_props(keys[-1].props, _MAIN_PROPS))
        auxiliary = [
            AuxiliaryKey(key.symbols, **_resolve_props(key.props, _AUX_PROPS))
            for key in keys[:-1]
        ]
        trigger = Trigger(main=main, aux=auxiliary)
        _validate(trigger)
        return trigger

    def _parse_keys(self, trigger_text: str) -> Iterator[_Key]:
        """Parses whole combo to keys."""
        for symbols_props in common.split(trigger_text, SYMBOL_DELIMITER):
            symbol_unresolved, props = common.parse_symbol_and_props(
                symbols_props, PROPERTY_DELIMITER
            )
            symbols = self._resolve_symbol(symbol_unresolved)
            yield _Key(symbols, props)

    def _resolve_symbol(self, symbol: str) -> list[str]:
        """List of corresponding symbols."""
        try:
            symbols = self.registered_symbols[symbol]
        except KeyError:
            raise TriggerParseError(f"Symbol not registered: '{symbol}'")
        return symbols
