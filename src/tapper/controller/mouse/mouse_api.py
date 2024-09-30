import time
from abc import ABC
from abc import abstractmethod
from typing import Callable
from typing import Optional

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.state import keeper


def is_near(current_x: int, current_y: int, x: int, y: int, precision: int) -> bool:
    return (current_x - x) ** 2 + (current_y - y) ** 2 <= precision**2


def calc_move(
    get_pos: Callable[[], tuple[int, int]],
    x: Optional[int],
    y: Optional[int],
    relative: bool,
) -> tuple[int, int]:
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

    def is_in(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Is cursor within bounding box - rectangle between x1 y1 and x2 y2."""
        x, y = self.get_pos()
        x_left = min(x1, x2)
        x_right = max(x1, x2)
        y_top = min(y1, y2)
        y_bottom = max(y1, y2)
        return x_left <= x <= x_right and y_top <= y <= y_bottom

    def press(self, symbol: str) -> None:
        """Presses down one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.DOWN))
        self._commander.press(symbol)

    def release(self, symbol: str) -> None:
        """Releases (presses up) one key. Not applicable to wheel."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.UP))
        self._commander.release(symbol)

    def move(
        self,
        x_or_xy: int | tuple[int, int] | None = None,
        y: int | None = None,
        relative: bool = False,
    ) -> None:
        """Move mouse cursor.

        Absolute movement moves cursor to the coordinates.
        Relative movement adds coordinates to current position.

        If one coordinate is not specified, only the other will be moved.
        At least one of the coordinates must be specified.
        """
        if x_or_xy is not None and isinstance(x_or_xy, tuple):
            x, y = x_or_xy
        else:
            x = x_or_xy  # type: ignore
        self._commander.move(x, y, relative)

    def memorize_pos(self) -> None:
        """Remember current cursor position. Only used for to_memorized_pos."""
        self._memorized_pos = self.get_pos()

    def to_memorized_pos(self) -> None:
        """Return to cursor to memorized position."""
        if self._memorized_pos:
            self.move(*self._memorized_pos)

    def click(
        self,
        x_or_xy: int | tuple[int, int] | None = None,
        y: int | None = None,
        relative: bool = False,
    ) -> None:
        """Move mouse cursor if coords supplied, then click left mouse button."""
        if x_or_xy is not None or y is not None:
            self.move(x_or_xy, y, relative)
        time.sleep(0)
        self.press("left_mouse_button")
        time.sleep(0)
        self.release("left_mouse_button")

    def right_click(
        self,
        x_or_xy: int | tuple[int, int] | None = None,
        y: int | None = None,
        relative: bool = False,
    ) -> None:
        """Move mouse cursor if coords supplied, then click right mouse button."""
        if x_or_xy is not None or y is not None:
            self.move(x_or_xy, y, relative)
        time.sleep(0)
        self.press("right_mouse_button")
        time.sleep(0)
        self.release("right_mouse_button")


def win32_winput() -> tuple[MouseTracker, MouseCommander]:
    from tapper.controller.mouse.mouse_win32_winput_impl import (
        Win32MouseTrackerCommander,
    )

    r = Win32MouseTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[MouseTracker, MouseCommander]]] = {
    constants.OS.win32: win32_winput,
}
