from abc import ABC
from dataclasses import dataclass

from tapper.model import constants


class SendInstruction(ABC):
    """Single instruction parsed from send command."""


@dataclass(init=False)
class KeyInstruction(SendInstruction):
    """Regular key, such as on keyboard or mouse button. Generic."""

    symbol: str
    dir: constants.KEY_DIR

    def __init__(self, symbol: str, dir: constants.KEY_DIR | str) -> None:
        self.symbol = symbol
        self.dir = dir if isinstance(dir, constants.KEY_DIR) else constants.KEY_DIR[dir]


@dataclass
class WheelInstruction(SendInstruction):
    """Single mouse wheel scroll."""

    wheel_symbol: str


@dataclass
class SleepInstruction(SendInstruction):
    time: float
    """Seconds."""
