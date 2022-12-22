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
        exec_or_title: Optional[str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        limit: Optional[int] = None,
    ) -> list[Window]:
        pass

    @abstractmethod
    def active(
        self,
        exec_or_title: Optional[str] = None,
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
    def to_active(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
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
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        force: bool = True,
    ) -> bool:
        pass

    @abstractmethod
    def minimize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        pass

    @abstractmethod
    def maximize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        pass

    @abstractmethod
    def restore(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
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
    _only_visible_windows: bool
    """Provided before init."""

    _tracker: WindowTracker
    _commander: WindowCommander

    def _init(self) -> None:
        if not hasattr(self, "_tracker") or not hasattr(self, "_commander"):
            self._tracker, self._commander = by_os[self._os](self._only_visible_windows)

    def _start(self) -> None:
        self._commander.start()
        self._tracker.start()

    def _stop(self) -> None:
        self._tracker.stop()
        self._commander.stop()

    def get_open(
        self,
        exec_or_title: Optional[str] = None,
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

        :param exec_or_title: Will try to match either exec or title.
        :param title: Window title, what you see on upper border or on mouseover in taskbar.
        :param exec: Executable name, on win32 something like "notepad.exe".
        :param strict: If this is true, title or exec (if specified)
            are filtered with == , otherwise substring ignore case.

        :param process_id: Unique, changes each launch.
        :param handle: OS-specific window ID. Unique, changes each launch.

        :param limit: Search will stop after getting this many results.
        """
        return self._tracker.get_open(
            exec_or_title, title, exec, strict, process_id, handle, limit
        )

    def is_open(
        self,
        exec_or_title: Optional[str] = None,
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
        if (
            exec_or_title is None
            and title is None
            and exec is None
            and process_id is None
            and handle is None
        ):
            raise ValueError("Specify at least one param for window.is_open method.")
        try:
            return self.get_open(
                exec_or_title, title, exec, strict, process_id, handle, 1
            )[0]
        except IndexError:
            return None

    def active(
        self,
        exec_or_title: Optional[str] = None,
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
        return self._tracker.active(
            exec_or_title, title, exec, strict, process_id, handle
        )

    def to_active(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Set an open window as foreground window, if found.

        :param window_or_exec_or_title:
            Object obtained by running one of get operations above, or name of exec or title.
        :param title: Window title, what you see on upper border or on mouseover in taskbar.
        :param exec: Executable name, on win32 something like "notepad.exe".
        :param strict: If this is true, title or exec (if specified)
            are filtered with == , otherwise substring ignore case.

        :param process_id: Unique, changes each launch.
        :param handle: OS-specific window ID. Unique, changes each launch.

        :return: True if found and successfully set as foreground, else False.
        """
        return self._commander.to_active(
            window_or_exec_or_title, title, exec, strict, process_id, handle
        )

    def close(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
        force: bool = True,
    ) -> bool:
        """
        Close(destroy) a window, if found.
        See to_fore above for param docs.

        If no params supplied, the foreground window will be closed.

        :param force: if window does not close politely, will kill it.
        :return: True if found and successfully closed, else False.
        """
        return self._commander.close(
            window_or_exec_or_title, title, exec, strict, process_id, handle, force
        )

    def minimize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Minimize a window, if found.
        See to_fore above for param docs.

        If no params supplied, the foreground window will be minimized.

        :return: True if found and successfully minimized, else False.
        """
        return self._commander.minimize(
            window_or_exec_or_title, title, exec, strict, process_id, handle
        )

    def maximize(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Maximize a window, if found.
        See to_fore above for param docs.

        If no params supplied, the foreground window will be maximized.

        :return: True if found and successfully minimized, else False.
        """
        return self._commander.maximize(
            window_or_exec_or_title, title, exec, strict, process_id, handle
        )

    def restore(
        self,
        window_or_exec_or_title: Optional[Window | str] = None,
        title: Optional[str] = None,
        exec: Optional[str] = None,
        strict: bool = False,
        process_id: Optional[int] = None,
        handle: Any = None,
    ) -> bool:
        """
        Restore a minimized or maximized window to previous size and position, if found.
        See to_fore above for param docs.

        If no params supplied, the foreground window will be
        restored (de-maximized, as foreground window cannot be minimized).

        :return: True if found and successfully restore, else False.
        """
        return self._commander.restore(
            window_or_exec_or_title, title, exec, strict, process_id, handle
        )


def win32_impl(
    only_visible_windows: bool = True,
) -> tuple[WindowTracker, WindowCommander]:
    from tapper.controller.window.window_win32_impl import Win32WindowTrackerCommander

    r = Win32WindowTrackerCommander(only_visible_windows)
    return r, r


by_os: dict[str, Callable[[bool], tuple[WindowTracker, WindowCommander]]] = {
    constants.OS.win32: win32_impl
}
