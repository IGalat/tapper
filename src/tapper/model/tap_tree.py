from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Optional

from tapper.model.constants import ListenerResult
from tapper.model.types_ import TapAction
from tapper.model.types_ import TriggerStr


class TapGeneric(ABC):
    """
    Shared data between Tap and Group.
    In a Group, each field will be inherited
    by its children, unless overridden down the line.
    """

    executor: int | None
    """Which executor to run the action in. see `ActionRunner`."""
    suppress_trigger: ListenerResult | None
    """Whether to suppress main key when an action is triggered."""
    send_interval: float | None
    """Time before keypress for `send` command, in seconds. Will be overridden if specified on `send` itself."""
    send_press_duration: float | None
    """
    Time between key press and release, in seconds. Will be overridden if specified on `send` itself.
    Only applies to click, not up/down. `e down;e up` will not have this time inbetween, `e` will.
    """
    trigger_conditions: dict[str, Any]
    """Keyword trigger conditions that can be used as part of `Tap` or `Group`. See config for docs."""
    _parent: Optional["Group"]


@dataclass(init=False)
class Tap(TapGeneric):
    """Trigger-action plan API."""

    trigger: TriggerStr
    """Combo or a single key that will trigger the action."""
    action: TapAction
    """
    Action to be executed when triggered. Will run in a separate thread.
    If string is specified, it will send(action) instead.
    None does nothing: with the default suppress_trigger, that swallows the key.
    """

    def __init__(
        self,
        trigger: TriggerStr,
        action: TapAction,
        executor: int | None = None,
        suppress_trigger: bool | None = None,
        send_interval: float | None = None,
        send_press_duration: float | None = None,
        **trigger_conditions: Any,
    ) -> None:
        self.trigger = trigger
        self.action = action
        self.executor = executor
        self.suppress_trigger = (
            ListenerResult(suppress_trigger) if suppress_trigger is not None else None
        )
        self.send_interval = send_interval
        self.send_press_duration = send_press_duration
        self.trigger_conditions = trigger_conditions
        self._parent = None

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

    _children: list[TapGeneric | dict[TriggerStr, TapAction]]

    def add(self, *children: TapGeneric | dict[TriggerStr, TapAction]) -> "Group":
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
                child._parent = self
        return self

    def __init__(
        self,
        name: str | None = None,
        executor: int | None = None,
        suppress_trigger: bool | None = None,
        send_interval: float | None = None,
        send_press_duration: float | None = None,
        **trigger_conditions: Any,
    ) -> None:
        self.name = name
        self.executor = executor
        self.suppress_trigger = (
            ListenerResult(suppress_trigger) if suppress_trigger is not None else None
        )
        self.send_interval = send_interval
        self.send_press_duration = send_press_duration
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
