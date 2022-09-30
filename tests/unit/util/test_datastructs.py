from typing import Any

import hypothesis.strategies as st
from hypothesis import given
from hypothesis.strategies import lists
from tapper.util.datastructs import to_flat_list


@given(st.dates() | lists(st.dates() | lists(st.dates() | lists(st.dates()))))
def test_to_flat_list(input_: Any | list[Any]) -> None:
    flat = to_flat_list(input_)
    assert isinstance(flat, list)
    assert not any(isinstance(item, list) for item in flat)
