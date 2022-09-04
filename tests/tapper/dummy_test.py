from tapper.dummy import dumdum


def test_dummy() -> None:
    assert 1 == 1


def test_dumdum() -> None:
    assert dumdum() == "dum"
