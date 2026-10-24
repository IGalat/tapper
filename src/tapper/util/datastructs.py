"""Data structures transform"""

from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any

from tapper.model.types_ import SymbolsWithAliases


def unique_list(data_structure: Sequence[Any]) -> list[Any]:
    result = []
    for item in data_structure:
        if item not in result:
            result.append(item)
    return result


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


def symbols_to_codes[T](
    code_symbol_map: dict[T, str], symbols: SymbolsWithAliases
) -> dict[str, list[T]]:
    """Maps all symbols, including aliases, to codes.

    Assumes every symbol except aliases is in code_symbol_map.
    """
    symbol_code_map = {v: k for (k, v) in code_symbol_map.items()}
    result = {}
    for maybe_alias, references in symbols.items():
        result[maybe_alias] = [symbol_code_map[r] for r in references]
    return result


def get_first_in[T](_type: type[T], seq: Sequence[Any]) -> T | None:
    for s in seq:
        if isinstance(s, _type):
            return s
    return None
