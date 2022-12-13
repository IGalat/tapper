from abc import ABC
from abc import abstractmethod
from typing import Callable

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.state import keeper


class KeyboardTracker(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def pressed(self, symbol: str) -> bool:
        pass

    @abstractmethod
    def toggled(self, symbol: str) -> bool:
        pass

    @abstractmethod
    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        pass


class KeyboardCommander(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def press(self, symbol: str) -> None:
        pass

    @abstractmethod
    def release(self, symbol: str) -> None:
        pass


class KeyboardController(ResourceController):
    _os: str
    """Provided before init."""
    _tracker: KeyboardTracker
    _commander: KeyboardCommander
    _emul_keeper: keeper.Emul

    def _init(self) -> None:
        if not hasattr(self, "_tracker") or not hasattr(self, "_commander"):
            self._tracker, self._commander = by_os[self._os]()

    def _start(self) -> None:
        self._commander.start()
        self._tracker.start()

    def _stop(self) -> None:
        self._tracker.stop()
        self._commander.stop()

    def pressed(self, symbol: str) -> bool:
        """Is key held down."""
        return self._tracker.pressed(symbol)

    def toggled(self, symbol: str) -> bool:
        """Is key toggled."""
        return self._tracker.toggled(symbol)

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        """Is key pressed; toggled."""
        return self._tracker.pressed_toggled(symbol)

    def press(self, symbol: str) -> None:
        """Presses down one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.DOWN))
        self._commander.press(symbol)

    def release(self, symbol: str) -> None:
        """Releases (presses up) one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.UP))
        self._commander.release(symbol)


def win32_winput() -> tuple[KeyboardTracker, KeyboardCommander]:
    from tapper.controller.keyboard.kb_win32_winput_impl import (
        Win32KeyboardTrackerCommander,
    )

    r = Win32KeyboardTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[KeyboardTracker, KeyboardCommander]]] = {
    constants.OS.win32: win32_winput
}
