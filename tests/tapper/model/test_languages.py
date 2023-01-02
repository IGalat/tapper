import pytest
from tapper.model import languages


def test_find_by_alias() -> None:
    assert languages.get("ua") == next(
        lang for lang in languages.languages if lang.locale_id == 1058
    )


def test_find_by_letter_code() -> None:
    assert languages.get("es-ES") == next(
        lang for lang in languages.languages if lang.locale_id == 1034
    )


def test_find_by_language_name() -> None:
    assert languages.get("portuguese") == next(
        lang for lang in languages.languages if lang.locale_id == 1046
    )


def test_find_by_language_after_dash() -> None:
    with pytest.raises(KeyError):
        assert languages.get("brazil")


def test_find_non_implemented() -> None:
    with pytest.raises(KeyError):
        assert languages.get(12300)
