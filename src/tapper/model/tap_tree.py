from dataclasses import dataclass
from dataclasses import field

from tapper.model.types_ import Action
from tapper.model.types_ import Trigger


@dataclass
class TapGeneric:
    """
    Shared data between Tap and Group.
    In a Group, each field will be inherited by Taps and other Groups in it, unless overridden.
    """

    executor: int
    """Which executor to run the action in. see ActionRunner."""
    suppress_trigger: bool
    """Whether to suppress main key when an action is triggered."""


@dataclass
class Tap(TapGeneric):
    """Trigger-action plan API."""

    trigger: Trigger
    """Combo or a single key that will trigger the action."""
    action: Action
    """Action to be executed when triggered. Will run in a separate thread."""


@dataclass
class Group(TapGeneric):
    """Contains taps or other groups. Allows hierarchical structure."""

    name: str

    _children: list[TapGeneric | dict[Trigger, Action]] = field(default_factory=list)

    def add(self, *children: TapGeneric | dict[Trigger, Action]) -> "Group":
        """
        Add new child elements to the group.

        Trigger order is reverse. It is recommended to put more specific actions after generic.

        Trigger order example:
            If you add({"a": action1, "ctrl+a": action2})
                , pressing ctrl+a will trigger action2
            If you add({"ctrl+a": action2, "a": action1})
                , pressing ctrl+a will trigger action1
        """
        self._children.append(*children)
        return self
