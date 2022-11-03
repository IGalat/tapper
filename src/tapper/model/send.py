from abc import ABC
from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants


COMBO_WRAP: str = "$(_)"
"""Symbols that wrap the combo.
Must contain "_" as placeholder for content, at least 1 opening and closing char."""
COMBO_CONTENT = "[ -~]+"
"""Symbols inside the combo.
Here it's all printable ASCII characters."""


class SendInstruction(ABC):
    """Single instruction parsed from send command."""


@dataclass
class KeyInstruction(SendInstruction):
    """Regular key, such as on keyboard or mouse button. Generic."""

    symbol: str
    dir: constants.KeyDir = field(default=constants.KeyDir.CLICK)


@dataclass
class WheelInstruction(SendInstruction):
    """Single mouse wheel scroll."""

    wheel_symbol: str


@dataclass
class SleepInstruction(SendInstruction):
    time: float
    """Seconds."""
