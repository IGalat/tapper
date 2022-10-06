from abc import ABC
from abc import abstractmethod

from tapper.command import base_commander
from tapper.model import constants


class KeyboardCommander(base_commander.Commander, ABC):
    """Sends commands to the keyboard. Allows inquiring state of keys."""

    @abstractmethod
    def press(self, symbol: str) -> None:
        """Presses down one key."""

    @abstractmethod
    def release(self, symbol: str) -> None:
        """Releases (presses up) one key."""

    @abstractmethod
    def pressed(self, symbol: str) -> bool:
        """Is key held down."""

    @abstractmethod
    def toggled(self, symbol: str) -> bool:
        """Is key toggled."""

    @abstractmethod
    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        """Is key pressed; toggled."""

    @staticmethod
    def get_for_os(os: str) -> "KeyboardCommander":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of KeyboardCommander.
        """
        return _os_impl_list[os]()()


def _get_win32_impl() -> type[KeyboardCommander]:
    from tapper.command.keyboard import win32_kb_commander

    return win32_kb_commander.Win32KeyboardCommander


_os_impl_list = {constants.OS.win32: _get_win32_impl}
