from dataclasses import dataclass
from typing import Any


@dataclass
class Window:
    """Data about an OS window."""

    title: str | None = None
    exec: str | None = None
    process_id: int | None = None
    handle: Any = None

    def __repr__(self) -> str:
        return f"Win({self.exec} | {self.title})"
