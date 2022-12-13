from abc import ABC
from typing import Callable

from tapper.model import constants
from tapper.tracking.base_tracker import ResourceTracker


class WindowTracker(ResourceTracker, ABC):
    @staticmethod
    def get_for_os(os: str) -> "ResourceTracker":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of WindowTracker.
        """
        return _os_impl_list[os]()()


def _get_win32_impl() -> type[WindowTracker]:
    from tapper.tracking.window import win32_window_tracker

    return win32_window_tracker.Win32WindowTracker


_os_impl_list: dict[str, Callable[[], type[WindowTracker]]] = {
    constants.OS.win32: _get_win32_impl
}
