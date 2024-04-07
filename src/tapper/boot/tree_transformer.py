"""
Transform Tree - user-configured hierarchical API structure,
into Shadow Tree - identically structured tree with useful for runtime fields.
"""
from functools import partial
from typing import Any

from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.tap_tree import Group
from tapper.model.tap_tree import Tap
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.tap_tree_shadow import STap
from tapper.model.types_ import Action
from tapper.model.types_ import KwTriggerConditions
from tapper.model.types_ import SendFn
from tapper.model.types_ import TriggerConditionFn
from tapper.model.types_ import TriggerStr
from tapper.parser.trigger_parser import TriggerParser

all_symbols = [*keyboard.get_keys().keys(), *mouse.get_keys().keys()]


def find_property(prop_name: str, group: Group) -> Any:
    if (result := getattr(group, prop_name)) is not None:
        return result
    return find_property(prop_name, group._parent)  # type: ignore


def transform_trigger_conditions(
    possible_conditions: KwTriggerConditions, trigger_conditions: dict[str, Any]
) -> list[TriggerConditionFn]:
    result = []
    for name, user_supplied_value in trigger_conditions.items():
        if name not in possible_conditions:
            raise ValueError(
                f"Condition '{name}' not recognised. Add it to config.kw_trigger_conditions"
            )
        fn = possible_conditions[name]
        result.append(partial(fn, user_supplied_value))
    return result


class TreeTransformer:
    send: SendFn
    trigger_parser: TriggerParser
    possible_trigger_conditions: KwTriggerConditions

    def __init__(
        self,
        send: SendFn,
        trigger_parser: TriggerParser,
        conditions: KwTriggerConditions,
    ) -> None:
        self.send = send  # type: ignore
        self.trigger_parser = trigger_parser
        self.possible_trigger_conditions = conditions

    def transform(self, group: Group) -> SGroup:
        result = SGroup()
        result.original = group
        result.send_interval = group.send_interval  # type: ignore  # it's not None here
        result.send_press_duration = group.send_press_duration  # type: ignore  # it's not None here
        result.trigger_conditions = transform_trigger_conditions(
            self.possible_trigger_conditions, group.trigger_conditions
        )

        for child in group._children:
            if isinstance(child, Group):
                result.add(self.transform(child))
            elif isinstance(child, Tap):
                result.add(self._transform_tap(child))
            elif isinstance(child, dict):
                result.add(*self._transform_dict(child, group))
            else:
                raise TypeError(f"{child}")
        return result

    def _transform_tap(self, tap: Tap) -> STap:
        trigger = self.trigger_parser.parse(tap.trigger)
        if (executor := tap.executor) is None:
            executor = find_property("executor", tap._parent)
        if (suppress_trigger := tap.suppress_trigger) is None:
            suppress_trigger = find_property("suppress_trigger", tap._parent)
        if (send_interval := tap.send_interval) is None:
            send_interval = find_property("send_interval", tap._parent)
        if (send_press_duration := tap.send_press_duration) is None:
            send_press_duration = find_property("send_press_duration", tap._parent)
        action = self.to_action(tap.action)
        result = STap(trigger, action, executor, suppress_trigger)
        result.original = tap
        result.send_interval = send_interval
        result.send_press_duration = send_press_duration
        result.trigger_conditions = transform_trigger_conditions(
            self.possible_trigger_conditions, tap.trigger_conditions
        )

        return result

    def _transform_dict(
        self, taps: dict[TriggerStr, Action | str], parent: Group
    ) -> list[STap]:
        result = []
        executor = find_property("executor", parent)
        suppress_trigger = find_property("suppress_trigger", parent)
        send_interval = find_property("send_interval", parent)
        send_press_duration = find_property("send_press_duration", parent)
        for trigger_str, action in taps.items():
            trigger = self.trigger_parser.parse(trigger_str)
            action = self.to_action(action)
            stap = STap(trigger, action, executor, suppress_trigger)
            stap.send_interval = send_interval
            stap.send_press_duration = send_press_duration
            stap.trigger_conditions = []
            result.append(stap)
        return result

    def to_action(self, action: Action | str) -> Action:
        if isinstance(action, str):
            if action in all_symbols and action not in keyboard.chars_en:
                action = f"$({action})"
            action = partial(self.send, action)
        return action
