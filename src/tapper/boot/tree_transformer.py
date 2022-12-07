"""
Transform Tree - user-configured hierarchical API structure,
into Shadow Tree - identically structured tree with useful for runtime fields.
"""
from functools import partial
from typing import Any

from tapper.model.tap_tree import Group
from tapper.model.tap_tree import Tap
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap
from tapper.model.types_ import Action
from tapper.model.types_ import SendFn
from tapper.model.types_ import TriggerStr
from tapper.parser.trigger_parser import TriggerParser


def find_property(prop_name: str, group: Group) -> Any:
    if (result := getattr(group, prop_name)) is not None:
        return result
    return find_property(prop_name, group._parent)


class TreeTransformer:
    send: SendFn
    trigger_parser: TriggerParser

    def __init__(self, send: SendFn, trigger_parser: TriggerParser) -> None:
        self.send = send  # type: ignore
        self.trigger_parser = trigger_parser

    def transform(self, group: Group) -> SGroup:
        result = SGroup()
        result.original = group

        for child in group._children:
            if isinstance(child, Group):
                result.add(self.transform(child))
            elif isinstance(child, Tap):
                result.add(self._transform_tap(child))
            elif isinstance(child, dict):
                result.add(*self._transform_dict(child, group))
            else:
                raise TypeError
        return result

    def _transform_tap(self, tap: Tap) -> STap:
        trigger = self.trigger_parser.parse(tap.trigger)
        if (executor := tap.executor) is None:
            executor = find_property("executor", tap._parent)
        if (suppress_trigger := tap.suppress_trigger) is None:
            suppress_trigger = find_property("suppress_trigger", tap._parent)
        action = self.to_action(tap.action)
        result = STap(trigger, action, executor, suppress_trigger)
        result.original = tap

        return result

    def _transform_dict(
        self, taps: dict[TriggerStr, Action | str], parent: Group
    ) -> list[STap]:
        result = []
        executor = find_property("executor", parent)
        suppress_trigger = find_property("suppress_trigger", parent)
        for trigger_str, action in taps.items():
            trigger = self.trigger_parser.parse(trigger_str)
            action = self.to_action(action)
            result.append(STap(trigger, action, executor, suppress_trigger))
        return result

    def to_action(self, action: Action | str) -> Action:
        if isinstance(action, str):
            action = partial(self.send, action)
        return action
