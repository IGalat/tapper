from abc import ABC
from abc import abstractmethod

from tapper.command import base_commander


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
