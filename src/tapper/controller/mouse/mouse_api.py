from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.state import keeper
from tapper.validation import report


def is_near(current_x: int, current_y: int, x: int, y: int, precision: int) -> bool:
    return (current_x - x) ** 2 + (current_y - y) ** 2 <= precision**2


def calc_move(
    get_pos: Callable[[], tuple[int, int]],
    x: Optional[int],
    y: Optional[int],
    relative: bool,
) -> tuple[int, int]:
    if x is None and y is None:
        report.error("MouseCommander move with no coordinates specified.")
    if not relative:
        if x is None:
            x = get_pos()[0]
        elif y is None:
            y = get_pos()[1]
    else:  # calculate here and absolute move
        current_x, current_y = get_pos()
        if x is None:
            x = current_x
        else:
            x += current_x
        if y is None:
            y = current_y
        else:
            y += current_y
    return x, y  # type: ignore


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
    _memorized_pos: tuple[int, int] | None = None

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

    def is_near(self, x: int, y: int, precision: int = 50) -> bool:
        """Circle with "precision" radius."""
        return is_near(*self.get_pos(), x, y, precision)

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

    def memorize_pos(self) -> None:
        """Remember current cursor position. Only used for to_memorized_pos."""
        self._memorized_pos = self.get_pos()

    def to_memorized_pos(self) -> None:
        """Return to cursor to memorized position."""
        if self._memorized_pos:
            self.move(*self._memorized_pos)


def win32_winput() -> tuple[MouseTracker, MouseCommander]:
    from tapper.controller.mouse.mouse_win32_winput_impl import (
        Win32MouseTrackerCommander,
    )

    r = Win32MouseTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[MouseTracker, MouseCommander]]] = {
    constants.OS.win32: win32_winput,
}
