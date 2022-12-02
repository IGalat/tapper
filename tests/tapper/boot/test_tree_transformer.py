from functools import partial
from typing import Callable

import pytest
from tapper.boot import initializer
from tapper.boot.tree_transformer import TreeTransformer
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.tap_tree import Group
from tapper.model.tap_tree import Tap
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap


def send(text: str) -> str:
    return text * 2 + "qwe"


TransformFn = Callable[[Group], SGroup]


class TestTreeTransformer:
    ex = 2
    res = ListenerResult.SUPPRESS

    @pytest.fixture(scope="class")
    def transform(self) -> TransformFn:
        return TreeTransformer(send, initializer.default_trigger_parser()).transform

    @pytest.fixture
    def group(self) -> Group:
        return Group("fixture_group", self.ex, self.res)

    def test_empty_with_props(self, transform: TransformFn) -> None:
        group = Group()
        group.executor = 33
        group.suppress_trigger = ListenerResult.PROPAGATE
        group.name = "blah"
        transform(group)

    def test_simplest(self, transform: TransformFn, group: Group) -> None:
        tap = Tap("a", send)
        group.add(tap)
        sg = transform(group)

        assert sg.get_main_triggers(KeyDirBool.DOWN) == ["a"]
        assert sg.get_main_triggers(KeyDirBool.UP) == []
        assert len(sg.children) == 1
        t = sg.children[0]
        assert isinstance(t, STap)
        if isinstance(t, STap):
            assert t.executor == self.ex
            assert t.suppress_trigger == self.res
            assert t.get_main_triggers(KeyDirBool.DOWN) == ["a"]
            assert t.original == tap
            assert t.action == send

    def test_nesting(self, transform: TransformFn, group: Group) -> None:
        tap1 = Tap("1", send)
        group1 = Group().add(tap1)
        group2 = Group().add({"a": send, "b": partial(send, "b")})
        group.add(group1, Tap("f1", partial(send, "f1")), group2)
        sg = transform(group)

        assert sg.get_main_triggers(KeyDirBool.DOWN) == ["1", "f1", "a", "b"]
        assert len(sg.children) == 3
        g1, t2, g3 = sg.children
        assert len(g1.children) == 1
        assert len(g3.children) == 2
        assert g3.get_main_triggers(KeyDirBool.DOWN) == ["a", "b"]

    def test_prop_override(self, transform: TransformFn, group: Group) -> None:
        tap1 = Tap("1", send)
        group1 = Group().add(tap1)
        group1.executor = 3
        group.add(group1)
        sg = transform(group)

        assert sg.children[0].children[0].executor == 3
