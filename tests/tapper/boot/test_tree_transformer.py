from functools import partial
from typing import Callable

import pytest

from tapper import config
from tapper.boot import initializer
from tapper.boot.tree_transformer import TreeTransformer
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.tap_tree import Group
from tapper.model.tap_tree import Tap
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap


def send_fn(text: str) -> None:
    return


send_action = lambda: send_fn

TransformFn = Callable[[Group], SGroup]


class TestTreeTransformer:
    ex = 2
    res = ListenerResult.SUPPRESS
    si = 0.02
    spd = 0.03

    @pytest.fixture(scope="class")
    def transform(self) -> TransformFn:
        return TreeTransformer(
            send_fn,
            initializer.default_trigger_parser(),
            initializer.default_trigger_conditions(config.controllers),
        ).transform

    @pytest.fixture
    def group(self) -> Group:
        return Group(
            "fixture_group",
            self.ex,
            self.res,
            send_interval=self.si,
            send_press_duration=self.spd,
        )

    def test_empty_with_props(self, transform: TransformFn) -> None:
        group = Group()
        group.executor = 33
        group.suppress_trigger = ListenerResult.PROPAGATE
        group.send_interval = 0
        group.send_press_duration = 0
        group.name = "blah"
        transform(group)

    def test_simplest(self, transform: TransformFn, group: Group) -> None:
        tap = Tap("a", send_action)
        group.add(tap)
        shadow_group = transform(group)

        assert shadow_group.get_main_triggers(KeyDirBool.DOWN) == {"a"}
        assert shadow_group.get_main_triggers(KeyDirBool.UP) == set()
        assert len(shadow_group.children) == 1
        t = shadow_group.children[0]
        assert isinstance(t, STap)
        if isinstance(t, STap):
            assert t.executor == self.ex
            assert t.suppress_trigger == self.res
            assert t.send_interval == self.si
            assert t.send_press_duration == self.spd
            assert t.get_main_triggers(KeyDirBool.DOWN) == {"a"}
            assert t.original == tap
            assert t.action == send_action

    def test_nesting(self, transform: TransformFn, group: Group) -> None:
        tap1 = Tap("1", send_action)
        group1 = Group().add(tap1)
        group2 = Group().add({"a": send_action, "b": partial(send_action, "b")})
        group.add(group1, Tap("f1", partial(send_action, "f1")), group2)
        sg = transform(group)

        assert sg.get_main_triggers(KeyDirBool.DOWN) == {"1", "f1", "a", "b"}
        assert len(sg.children) == 3
        g1, t2, g3 = sg.children
        assert isinstance(g1, SGroup)
        assert isinstance(g3, SGroup)
        assert len(g1.children) == 1
        assert len(g3.children) == 2
        assert g3.get_main_triggers(KeyDirBool.DOWN) == {"a", "b"}

    def test_prop_override(self, transform: TransformFn, group: Group) -> None:
        tap1 = Tap("1", send_action)
        group1 = Group().add(tap1)
        group1.executor = 3
        group.add(group1)

        sg = transform(group)
        sub_sg = sg.children[0]
        assert isinstance(sub_sg, SGroup)
        sub_sub_stap = sub_sg.children[0]
        assert isinstance(sub_sub_stap, STap)

        assert sub_sub_stap.executor == 3
