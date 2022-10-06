from tapper.model.trigger import Trigger
from tapper.model.types_ import SymbolsWithAliases


class TriggerParser:
    """Parses trigger string supplied by the user."""

    registered_symbols: SymbolsWithAliases

    def __init__(self, symbols_to_register: list[SymbolsWithAliases]) -> None:
        self.registered_symbols = {}
        for symbol_dict in symbols_to_register:
            for symbol, value in symbol_dict.values():
                if symbol in self.registered_symbols:
                    raise ValueError(f"Symbol already registered: {symbol}")
                self.registered_symbols[symbol] = value

    def parse(self, text: str) -> Trigger:
        """Parse single combo, to be pressed in one go."""
