from typing import Final


class OS:
    dummy: Final[str] = "dummy"
    win32: Final[str] = "win32"


class KEY_DIR:
    UP: Final[bool] = False
    """Key released."""
    DOWN: Final[bool] = True
    """Key pressed."""
    CLICK: Final[None] = None
    """Key pressed, the released."""
