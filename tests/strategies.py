from hypothesis import strategies as st

chars = st.characters(blacklist_categories=["C", "Zl", "Zp"])
"""Any character that isn't a control character or whitespace other than ' '."""

text_printable = st.text(chars, min_size=2).filter(lambda data: data.isprintable())

word_chars = st.characters(blacklist_categories=["C", "Z"])
"""Characters that are valid to be in a word."""

words = st.text(word_chars, min_size=1)
"""A single word (no whitespace)"""

word_lists = st.lists(words, max_size=100)

primitives = (
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats()
    | st.decimals()
    | st.fractions()
    | st.complex_numbers()
    | st.text()
    | st.characters()
    | st.times()
    | st.datetimes()
    | st.dates()
    | st.timedeltas()
    | st.timezone_keys()
    | st.binary()
)

"""Dictionaries not included."""
primitives_and_seq = (
    primitives | st.lists(primitives) | st.tuples(primitives) | st.sets(primitives)
)


@st.composite
def code_symbol_maps(draw: st.DrawFn) -> dict[int, str]:
    """To simulate platform-specific mapping of codes to symbols."""
    codes = draw(st.lists(st.integers(), unique=True))
    symbols = draw(st.lists(words, unique=True))
    return dict(zip(codes, symbols))
