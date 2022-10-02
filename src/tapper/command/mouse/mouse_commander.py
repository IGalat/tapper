from abc import ABC
from abc import abstractmethod
from typing import Optional

from tapper.command import base_commander
from tapper.model import constants


class MouseCommander(base_commander.Commander, ABC):
    """Sends commands to the mouse. Allows inquiring state of keys."""

    @abstractmethod
    def press(self, symbol: str) -> None:
        """Presses down one key."""

    @abstractmethod
    def release(self, symbol: str) -> None:
        """Releases (presses up) one key. Not applicable to wheel."""

    @abstractmethod
    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        """Move mouse cursor.

        Absolute movement moves cursor to the coordinates.
        Relative movement adds coordinates to current position.

        If one coordinate is not specified, only the other will be moved.
        At least one of the coordinates must be specified.
        """

    @abstractmethod
    def pressed(self, symbol: str) -> bool:
        """Is key held down. Not applicable to wheel."""

    @abstractmethod
    def toggled(self, symbol: str) -> bool:
        """Is key toggled. Not applicable to wheel."""

    @abstractmethod
    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        """Is key pressed; toggled. Not applicable to wheel."""

    @abstractmethod
    def get_pos(self) -> tuple[int, int]:
        """Coordinates (x, y) of current mouse position."""

    @staticmethod
    def get_for_os(os: str) -> "MouseCommander":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of MouseCommander.
        """
        return _os_impl_list[os]()()


def _get_win32_impl() -> type[MouseCommander]:
    from tapper.command.mouse import win32_mouse_commander

    return win32_mouse_commander.Win32MouseCommander


_os_impl_list = {constants.os.win32: _get_win32_impl}