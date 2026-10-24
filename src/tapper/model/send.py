from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants

COMBO_WRAP: str = r"\$\(_\)"
"""Symbols that wrap the combo.
Must contain "_" as placeholder for content, at least 1 opening and closing char."""
COMBO_CONTENT = "[ -(*-~\n\t]+"
"""Symbols inside the combo.
Here it's all printable ASCII characters."""


@dataclass(frozen=True)
class KeyInstruction:
    """Regular key, such as on keyboard or mouse button. Generic."""

    symbol: str
    dir: constants.KeyDir = field(default=constants.KeyDir.CLICK)


@dataclass(frozen=True)
class WheelInstruction:
    """Single mouse wheel scroll."""

    wheel_symbol: str


@dataclass(frozen=True)
class CursorMoveInstruction:
    """Move mouse cursor."""

    xy: tuple[int, int]
    relative: bool = field(default=False)


@dataclass(frozen=True)
class SleepInstruction:
    time: float
    """Seconds."""


type SendInstruction = (
    KeyInstruction | WheelInstruction | CursorMoveInstruction | SleepInstruction
)
"""Single instruction parsed from send command."""
