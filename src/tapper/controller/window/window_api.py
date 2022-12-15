from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import Optional

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.model.window import Window


class WindowTracker(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
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

    @abstractmethod
    def is_fore(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> Optional[Window]:
        pass


class WindowCommander(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
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

    @abstractmethod
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


class WindowController(ResourceController):
    """Allows checking window status and giving commands."""

    _os: str
    """Provided before init."""
    _tracker: WindowTracker
    _commander: WindowCommander

    def _init(self) -> None:
        if not hasattr(self, "_tracker") or not hasattr(self, "_commander"):
            self._tracker, self._commander = by_os[self._os]()

    def _start(self) -> None:
        self._commander.start()
        self._tracker.start()

    def _stop(self) -> None:
        self._tracker.stop()
        self._commander.stop()

    def get_open(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        limit: Optional[int] = None,
    ) -> list[Window]:
        """
        Fetches open windows that have name or exec. Ignores ones without.

        If no params are specified, fetches all, otherwise filters.

        :param title: Window title, what you see on upper border or on mouseover in taskbar.
        :param exec: Executable name, on win32 something like "notepad.exe".
        :param strict: If this is true, title or exec (if specified)
            are filtered with == , otherwise substring ignore case.

        :param process_id: Unique, changes each launch.
        :param handle: OS-specific window ID. Unique, changes each launch.

        :param limit: Search will stop after getting this many results.
        """
        return self._tracker.get_open(title, exec, strict, process_id, handle, limit)

    def is_open(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> Optional[Window]:
        """
        First open window with params specified.
        If no windows match params, None is returned.

        At least one param must be supplied.
        See get_open above for param docs.

        Can be used like:
        # if is_open("notepad"):
        #     do_my_thing()
        """
        if title is None and exec is None and process_id is None and handle is None:
            raise ValueError(
                "Must specify at least one param for window.is_open method."
            )
        try:
            return self.get_open(title, exec, strict, process_id, handle, 1)[0]
        except IndexError:
            return None

    def is_fore(
        self,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> Optional[Window]:
        """
        Foreground window, if params match.
        If the foreground window doesn't match params, None is returned.

        At least one param must be supplied.
        See get_open above for param docs.

        Can be used like:
        # if is_fore("notepad"):
        #     do_my_thing()
        """
        return self._tracker.is_fore(title, exec, strict, process_id, handle)

    def set_fore(
        self,
        window: Optional[Window] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Set an open window as foreground window, if found.

        See get_open above for param docs.

        :param window: Object obtained by running one of get operations above.
        :return: True if found and successfully set as foreground, else False.
        """
        return self._commander.set_fore(window, title, exec, strict, process_id, handle)

    def close(
        self,
        window: Optional[Window] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Close an open window, if found.

        See get_open above for param docs.

        :param window: Object obtained by running one of get operations above.
        :return: True if found and successfully closed, else False.
        """
        return self._commander.close(window, title, exec, strict, process_id, handle)


def win32_impl() -> tuple[WindowTracker, WindowCommander]:
    from tapper.controller.window.window_win32_impl import Win32WindowTrackerCommander

    r = Win32WindowTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[WindowTracker, WindowCommander]]] = {
    constants.OS.win32: win32_impl
}
