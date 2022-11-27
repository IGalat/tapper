from tapper.model import constants
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger


def stap(key: str, direction: constants.KeyDirBool = constants.KeyDirBool.DOWN) -> STap:
    return STap(Trigger(MainKey([key], direction=direction)), None, None, None)


def test_get_triggers() -> None:
    inner_tap1 = stap("in1", constants.KeyDirBool.UP)
    inner_tap2 = stap("in2")
    inner_group = SGroup([inner_tap1, inner_tap2])

    outer_tap1 = stap("out1")
    outer_tap2 = stap("out2", constants.KeyDirBool.UP)
    outer_tap3 = stap("out3")
    outer_group = SGroup([outer_tap1, inner_group, outer_tap2, outer_tap3])

    assert outer_group.get_triggers(constants.KeyDirBool.DOWN) == [
        "out1",
        "in2",
        "out3",
    ]

    assert outer_group.get_triggers(constants.KeyDirBool.UP) == ["in1", "out2"]

    assert inner_tap1.get_triggers(constants.KeyDirBool.DOWN) == []
    assert inner_tap1.get_triggers(constants.KeyDirBool.UP) == ["in1"]
