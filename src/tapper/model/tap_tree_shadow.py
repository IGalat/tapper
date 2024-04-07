"""See tap_tree for docs, same fields as here."""
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from tapper.model import constants
from tapper.model.tap_tree import TapGeneric
from tapper.model.trigger import Trigger
from tapper.model.types_ import Action
from tapper.model.types_ import TriggerConditionFn
from tapper.util.cache import lru_cache
from tapper.util.datastructs import to_flat_list
from tapper.util.datastructs import unique_list


class STapGeneric(ABC):
    """Shadow TapGeneric: used during runtime.
    All fields and methods in case of group refer to children's.
    """

    original: Optional[TapGeneric]
    """Item based on which this shadow is created."""
    send_interval: float
    send_press_duration: float
    trigger_conditions: list[TriggerConditionFn]

    @abstractmethod
    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:
        """All main keys. If group - all children's main keys."""


@dataclass
class STap(STapGeneric):
    """Shadow Tap: used during runtime."""

    trigger: Trigger
    action: Action
    executor: int
    suppress_trigger: constants.ListenerResult

    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:
        if self.trigger.main.direction == direction:
            return self.trigger.main.symbols
        else:
            return []


@dataclass
class SGroup(STapGeneric):
    """Shadow Group: used during runtime."""

    children: list[STapGeneric] = field(default_factory=list)

    @lru_cache  # type: ignore
    def get_main_triggers(self, direction: constants.KeyDirBool) -> list[str]:  # type: ignore
        nested_non_unique = [
            child.get_main_triggers(direction) for child in self.children
        ]
        return unique_list(to_flat_list(nested_non_unique))

    def add(self, *children: STapGeneric) -> "SGroup":
        self.children.extend(children)
        return self
