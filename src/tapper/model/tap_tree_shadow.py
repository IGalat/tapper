from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants
from tapper.model.tap_tree import TapGeneric
from tapper.model.trigger import Trigger
from tapper.model.types_ import Action
from tapper.model.types_ import TriggerStr
from tapper.util.cache import lru_cache
from tapper.util.datastructs import to_flat_list
from tapper.util.datastructs import unique_list


class STapGeneric(ABC):
    """Shadow TapGeneric: used during runtime.
    All fields and methods in case of group refer to children's.
    """

    original: TapGeneric | tuple[TriggerStr, Action | str]
    """Item based on which this shadow is created."""

    @abstractmethod
    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:
        """All main keys. If group - all children's main keys."""


@dataclass(slots=False)
class STap(STapGeneric):
    """Shadow tap: used during runtime."""

    trigger: Trigger
    """Combo or a single key that will trigger the action."""
    action: Action
    """Action to be executed when triggered. Will run in a separate thread."""
    executor: int
    """Which executor to run the action in. see ActionRunner."""
    suppress_trigger: constants.ListenerResult
    """Whether to suppress main key when an action is triggered."""

    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:
        if self.trigger.main.direction == direction:
            return self.trigger.main.symbols
        else:
            return []


@dataclass(slots=False)
class SGroup(STapGeneric):
    """Shadow group: used during runtime."""

    children: list[STapGeneric] = field(default_factory=list)

    @lru_cache
    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:
        nested_non_unique = [
            child.get_main_triggers(direction) for child in self.children
        ]
        return unique_list(to_flat_list(nested_non_unique))

    def add(self, *children: STapGeneric) -> "SGroup":
        self.children.extend(children)
        return self
