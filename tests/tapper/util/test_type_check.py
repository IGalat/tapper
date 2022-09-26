from typing import Any

import hypothesis.strategies as st
from hypothesis import example
from hypothesis import given
from hypothesis.strategies import lists
from tapper.util.type_check import is_list_of
from tapper.util.type_check import is_tuple_of


@given(lists(st.characters()) | lists(st.dates()) | lists(st.integers()))
@example(["mixed list", 2])
@example((123, "what about tuple?"))
@example({"some dict too": 456})
def test_data_structures__is_list_of(input_: Any) -> None:
    if type(input_) == list:
        if not input_:
            assert is_list_of(input_, int)
        else:
            type_ = type(input_[0])
            assert is_list_of(input_, type_) == all(
                isinstance(x, type_) for x in input_
            )
    else:
        assert not is_list_of(input_, int)


@given(st.characters() | st.dates() | st.integers())
def test_primitives__is_list_of(input_: Any) -> None:
    assert not is_list_of(input_, int)


@given(st.tuples(st.characters()) | lists(st.dates()) | lists(st.integers()))
@example(("mixed tuple", 2))
@example([123, "what about list?"])
@example({"some dict too": 456})
def test_data_structures__is_tuple_of(input_: Any) -> None:
    if type(input_) == tuple:
        if not input_:
            assert is_tuple_of(input_, int)
        else:
            type_ = type(input_[0])
            assert is_tuple_of(input_, type_) == all(
                isinstance(x, type_) for x in input_
            )
    else:
        assert not is_tuple_of(input_, int)
