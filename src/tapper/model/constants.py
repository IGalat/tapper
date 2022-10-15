from enum import Enum
from typing import Final


class KEY_DIR(str, Enum):
    """Key direction. This is used for commands.

    Some keys may only be pressed (example: mouse wheel).
    """

    up = "up"
    """Key released."""
    down = "down"
    """Key pressed."""
    click = "click"
    """Key pressed, the released."""
    on = "on"
    """If key is not toggled on, click, else nothing."""
    off = "off"
    """If key is not toggled off, click, else nothing."""


class KEY_DIR_BOOL:
    """Key direction. Used for signal recognition."""

    up: Final[bool] = False
    """Key released."""
    down: Final[bool] = True
    """Key pressed."""


class OS(str, Enum):
    dummy = "dummy"
    win32 = "win32"
