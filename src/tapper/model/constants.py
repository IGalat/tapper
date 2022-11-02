from enum import Enum
from typing import Final


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


class KeyDirBool:
    """Key direction. Used for signal recognition."""

    UP: Final[bool] = False
    """Key released."""
    DOWN: Final[bool] = True
    """Key pressed."""


class OS(str, Enum):
    dummy = "dummy"
    win32 = "win32"
