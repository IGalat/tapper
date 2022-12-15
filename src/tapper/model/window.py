from dataclasses import dataclass
from typing import Any
from typing import Optional


@dataclass
class Window:
    """Data about an OS window."""

    title: Optional[str] = None
    exec: Optional[str] = None
    process_id: Optional[int] = None
    handle: Any = None
