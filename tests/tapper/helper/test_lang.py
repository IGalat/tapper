from functools import partial

import pytest
from tapper.helper.lang import to_en


def test_to_en_simplest() -> None:
    assert to_en("ua", "їхати") == "][fnb"


def test_to_en_with_upper() -> None:
    assert to_en(1058, "Привіт!№") == "Ghbdsn!#"


def test_to_en_combo() -> None:
    assert to_en("uk-UA", "йцукен$(1s;q up 2x)%:?*(") == "qwerty$(1s;q up 2x)%^&*("


def test_to_en_combo_start_end() -> None:
    assert (
        to_en("ukrainian", "$(ctrl down) імматеріально$(ctrl up)")
        == "$(ctrl down) svvfnthsfkmyj$(ctrl up)"
    )


def test_to_en_wrong_lang() -> None:
    ua = partial(to_en, "ua")
    assert ua("ії") == "s]"
    with pytest.raises(ValueError):
        ua("hi there")
