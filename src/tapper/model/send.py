from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants

COMBO_WRAP: str = r"\$\(_\)"
"""Symbols that wrap the combo.
Must contain "_" as placeholder for content, at least 1 opening and closing char."""
COMBO_CONTENT = "[ -(*-~\n\t]+"
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
class CursorMoveInstruction(SendInstruction):
    """Move mouse cursor. Absolute."""

    xy: tuple[int, int]
    relative: bool = field(default=False)

    def __init__(self, xy_rel: tuple[int, int] | tuple[tuple[int, int], bool]) -> None:
        self.xy = xy_rel if isinstance(xy_rel[0], int) else xy_rel[0]
        self.relative = isinstance(xy_rel[1], bool) and xy_rel[1]


@dataclass
class SleepInstruction(SendInstruction):
    time: float
    """Seconds."""
