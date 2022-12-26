from enum import Enum
from enum import Flag


class KeyDir(str, Enum):
    """Key direction. This is used for commands.

    Some keys may only be pressed (example: mouse wheel).
    """

    UP = "up"
    """Key released."""
    DOWN = "down"
    """Key pressed."""
    CLICK = "click"
    """Key pressed, the released."""
    ON = "on"
    """If key is not toggled on, click, else nothing."""
    OFF = "off"
    """If key is not toggled off, click, else nothing."""

    def __repr__(self) -> str:
        return self.name


class KeyDirBool(Flag):
    """Key direction. Used for signal recognition."""

    UP = False
    """Key released."""
    DOWN = True
    """Key pressed."""

    def __repr__(self) -> str:
        return self.name if self.name else ""


class OS(str, Enum):
    dummy = "dummy"
    win32 = "win32"


class ListenerResult(Flag):
    PROPAGATE = True
    """Signal will be received by other apps."""
    SUPPRESS = False
    """Signal will be suppressed and will not be received by other apps."""


WinputListenerResult = {ListenerResult.SUPPRESS: 4, ListenerResult.PROPAGATE: 0}
"""Corresponding result for winput, win32 low-level adapter."""
