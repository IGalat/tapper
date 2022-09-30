from abc import ABC
from abc import abstractmethod

from tapper.command import base_commander
from tapper.model import mouse
from tapper.model import types_


class KeyboardCommander(base_commander.Commander, ABC):
    """Sends commands to the keyboard. Allows inquiring state of keys."""

    @classmethod
    @abstractmethod
    def get_possible_command_symbols(cls) -> types_.SymbolsWithAliases:
        """Symbols, including aliases, that can be used to give commands."""
        return mouse.get_keys()

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
