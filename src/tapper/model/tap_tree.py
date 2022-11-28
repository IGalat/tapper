from abc import ABC
from dataclasses import dataclass
from dataclasses import field

from tapper.model.types_ import Action
from tapper.model.types_ import TriggerStr


class TapGeneric(ABC):
    """
    Shared data between Tap and Group.
    In a Group, each field will be inherited by Taps and other Groups in it, unless overridden.
    """

    executor: int | None
    """Which executor to run the action in. see ActionRunner."""
    suppress_trigger: bool | None
    """Whether to suppress main key when an action is triggered."""


@dataclass(init=False)
class Tap(TapGeneric):
    """Trigger-action plan API."""

    trigger: TriggerStr
    """Combo or a single key that will trigger the action."""
    action: Action
    """Action to be executed when triggered. Will run in a separate thread."""

    def __init__(
        self,
        trigger: TriggerStr,
        action: Action,
        executor: int | None = None,
        suppress_trigger: bool | None = None,
    ) -> None:
        self.trigger = trigger
        self.action = action
        self.executor = executor
        self.suppress_trigger = suppress_trigger


@dataclass(init=False)
class Group(TapGeneric):
    """Contains taps or other groups. Allows hierarchical structure."""

    name: str | None

    _children: list[TapGeneric | dict[TriggerStr, Action]] = field(default_factory=list)

    def add(self, *children: TapGeneric | dict[TriggerStr, Action]) -> "Group":
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
        return self

    def __init__(
        self,
        name: str | None = None,
        executor: int | None = None,
        suppress_trigger: bool | None = None,
    ) -> None:
        self.name = name
        self.executor = executor
        self.suppress_trigger = suppress_trigger
