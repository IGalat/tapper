from typing import Any
from typing import Optional

from tapper.controller.window.window_api import WindowCommander
from tapper.controller.window.window_api import WindowTracker
from tapper.model.window import Window


class Win32WindowTrackerCommander(WindowTracker, WindowCommander):
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_open(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        limit: Optional[int] = None,
    ) -> list[Window]:
        pass

    def is_fore(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> Optional[Window]:
        pass

    def set_fore(
        self,
        window: Optional[Window] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        pass

    def close(
        self,
        window: Optional[Window] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        pass
