from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.state import keeper


class MouseTracker(ABC):
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
    def get_pos(self) -> tuple[int, int]:
        pass


class MouseCommander(ABC):
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

    @abstractmethod
    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        pass


class MouseController(ResourceController):
    _os: str
    """Provided before init."""
    _tracker: MouseTracker
    _commander: MouseCommander
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
        """Is key held down. Not applicable to wheel."""
        return self._tracker.pressed(symbol)

    def toggled(self, symbol: str) -> bool:
        """Is key toggled. Not applicable to wheel."""
        return self._tracker.toggled(symbol)

    def get_pos(self) -> tuple[int, int]:
        """Coordinates (x, y) of current mouse position."""
        return self._tracker.get_pos()

    def press(self, symbol: str) -> None:
        """Presses down one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.DOWN))
        self._commander.press(symbol)

    def release(self, symbol: str) -> None:
        """Releases (presses up) one key. Not applicable to wheel."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.UP))
        self._commander.release(symbol)

    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        """Move mouse cursor.

        Absolute movement moves cursor to the coordinates.
        Relative movement adds coordinates to current position.

        If one coordinate is not specified, only the other will be moved.
        At least one of the coordinates must be specified.
        """
        self._commander.move(x, y, relative)


def win32_winput() -> tuple[MouseTracker, MouseCommander]:
    from tapper.controller.mouse.mouse_win32_winput_impl import (
        Win32MouseTrackerCommander,
    )

    r = Win32MouseTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[MouseTracker, MouseCommander]]] = {
    constants.OS.win32: win32_winput
}
