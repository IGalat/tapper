from typing import Final


class _OS:
    dummy: Final[str] = "dummy"
    win32: Final[str] = "win32"


os = _OS
