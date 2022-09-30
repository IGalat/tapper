"""Data structures transform"""
from typing import Any
from typing import Iterable
from typing import Sequence

from tapper.model.types_ import SymbolsWithAliases


def to_flat_list(data_structure: Sequence[Any] | Any) -> list[Any]:
    """Transforms single values to list; flattens to list any (nested too) Sequence."""
    return list(_flatten(data_structure))


def _flatten(xs: Sequence[Any]) -> Iterable[Any]:
    if isinstance(xs, Sequence) and not isinstance(xs, (str, bytes)):
        for x in xs:
            if isinstance(x, Sequence) and not isinstance(x, (str, bytes)):
                yield from _flatten(x)
            else:
                yield x
    else:
        yield xs


def symbols_to_codes(
    code_symbol_map: dict[int, str], symbols: SymbolsWithAliases
) -> dict[str, int]:
    """Maps all symbols, including aliases, to codes. In case of alias, it's the first reference.

    Assumes every symbol except aliases is in code_symbol_map.
    """
    symbol_code_map = {v: k for (k, v) in code_symbol_map.items()}
    for maybe_alias, references in symbols.items():
        if references:  # then maybe_alias is alias
            code = symbol_code_map[references[0]]
            symbol_code_map[maybe_alias] = code
    return symbol_code_map
