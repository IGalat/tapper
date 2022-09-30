import random
from typing import Any

import hypothesis.strategies as st
import strategies
from hypothesis import given
from hypothesis.strategies import lists
from tapper.model.types_ import SymbolsWithAliases
from tapper.util import datastructs


@given(st.dates() | lists(st.dates() | lists(st.dates() | lists(st.dates()))))
def test_to_flat_list(input_: Any | list[Any]) -> None:
    flat = datastructs.to_flat_list(input_)
    assert isinstance(flat, list)
    assert not any(isinstance(item, list) for item in flat)


@st.composite
def tuple_for_sym_to_codes(
    draw: st.DrawFn,
) -> tuple[dict[int, str], SymbolsWithAliases]:
    _codes = draw(st.lists(st.integers(), unique=True))
    _symbols = draw(st.lists(strategies.words, unique=True))
    code_symbol_map = dict(zip(_codes, _symbols))
    symbols = {v: None for v in code_symbol_map.values()}
    if symbols:
        references = list(symbols.keys())
        aliases = draw(
            st.lists(strategies.words).filter(lambda word: word not in references)
        )
        for alias in aliases:
            quantity_of_refs = random.randint(1, len(references))
            symbols[alias] = random.choices(references, k=quantity_of_refs)

    return code_symbol_map, symbols


# noinspection PyTypeChecker
@given(tuple_for_sym_to_codes())
def test_symbols_to_codes(in_tuple: tuple[dict[int, str], SymbolsWithAliases]) -> None:
    code_symbol_map, symbols = in_tuple
    symbol_code_map = datastructs.symbols_to_codes(code_symbol_map, symbols)
    assert len(symbol_code_map) == len(symbols), "len diff"
    for symbol, code in symbol_code_map.items():
        assert code in code_symbol_map, "code not in"
        assert symbol in symbols, "symbol not in"
