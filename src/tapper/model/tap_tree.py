from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Optional

from tapper.model.constants import ListenerResult
from tapper.model.types_ import Action
from tapper.model.types_ import TriggerStr


class TapGeneric(ABC):
    """
    Shared data between Tap and Group.
    In a Group, each field will be inherited
    by its children, unless overridden down the line.
    """

    executor: Optional[int]
    """Which executor to run the action in. see ActionRunner."""
    suppress_trigger: Optional[ListenerResult]
    """Whether to suppress main key when an action is triggered."""
    trigger_conditions: dict[str, Any]
    """Keyword trigger conditions that can be used as part of Tap or Group. See config for docs."""


@dataclass(init=False)
class Tap(TapGeneric):
    """Trigger-action plan API."""

    trigger: TriggerStr
    """Combo or a single key that will trigger the action."""
    action: Action | str
    """
    Action to be executed when triggered. Will run in a separate thread.
    If string is specified, it will send(action) instead.
    """
    _parent: "Group"

    def __init__(
        self,
        trigger: TriggerStr,
        action: Action | str,
        executor: Optional[int] = None,
        suppress_trigger: Optional[bool] = None,
        **trigger_conditions: Any,
    ) -> None:
        self.trigger = trigger
        self.action = action
        self.executor = executor
        self.suppress_trigger = (
            ListenerResult(suppress_trigger) if suppress_trigger else None
        )
        self.trigger_conditions = trigger_conditions

    def conditions(self, **trigger_conditions: Any) -> "Tap":
        """Add new trigger conditions. Can also be done in constructor."""
        if not self.trigger_conditions:
            self.trigger_conditions = {}
        self.trigger_conditions.update(trigger_conditions)
        return self

    def __repr__(self) -> str:
        return f"Tap('{self.trigger}')"


@dataclass(init=False)
class Group(TapGeneric):
    """Contains taps or other groups. Allows hierarchical structure."""

    name: str | None

    _children: list[TapGeneric | dict[TriggerStr, Action | str]]
    _parent: Optional["Group"] = None

    def add(self, *children: TapGeneric | dict[TriggerStr, Action | str]) -> "Group":
        """
        Add new child elements to the group.

        Trigger order is reverse. It is recommended to put more specific actions after generic.

        Trigger order example:
            If you add({"a": action1, "ctrl+a": action2})
                , pressing ctrl+a will trigger action2
            If you add({"ctrl+a": action2, "a": action1})
                , pressing ctrl+a will trigger action1
        """
        self._children.extend(children)
        for child in children:
            if isinstance(child, TapGeneric):
                child._parent = self  # type: ignore
        return self

    def __init__(
        self,
        name: Optional[str] = None,
        executor: Optional[int] = None,
        suppress_trigger: Optional[bool] = None,
        **trigger_conditions: Any,
    ) -> None:
        self.name = name
        self.executor = executor
        self.suppress_trigger = (
            ListenerResult(suppress_trigger) if suppress_trigger else None
        )
        self.trigger_conditions = trigger_conditions

        self._children = []

    def conditions(self, **trigger_conditions: Any) -> "Group":
        """Add new trigger conditions. Can also be done in constructor."""
        if not self.trigger_conditions:
            self.trigger_conditions = {}
        self.trigger_conditions.update(trigger_conditions)
        return self

    def __repr__(self) -> str:
        return f"Group '{self.name}': {self._children}"
