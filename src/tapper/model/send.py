from abc import ABC
from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants


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
