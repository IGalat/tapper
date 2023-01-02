from abc import ABC
from abc import abstractmethod
from typing import Callable

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.model.languages import Lang
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
    def lang(self, lang: str | int | Lang | None = None) -> None:
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

    @abstractmethod
    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
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

    def lang(self, lang: str | int | Lang | None = None) -> None:
        """Get current language. If param `lang` specified, will return None if it doesn't match."""

    def press(self, symbol: str) -> None:
        """Presses down one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.DOWN))
        self._commander.press(symbol)

    def release(self, symbol: str) -> None:
        """Releases (presses up) one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.UP))
        self._commander.release(symbol)

    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
        """
        Switch input to specified language.

        If this language is not in your user's language input list, nothing happens.

        :param lang: see model.languages
        :param system_wide: change lang for all apps. If False, only for active one.
        """
        self._commander.set_lang(lang, system_wide)


def win32_winput() -> tuple[KeyboardTracker, KeyboardCommander]:
    from tapper.controller.keyboard.kb_win32_winput_impl import (
        Win32KeyboardTrackerCommander,
    )

    r = Win32KeyboardTrackerCommander()
    return r, r


def linux_evdev() -> tuple[KeyboardTracker, KeyboardCommander]:
    from tapper.controller.keyboard.kb_linux_evdev_impl import (
        LinuxKeyboardTrackerCommander,
    )

    r = LinuxKeyboardTrackerCommander()
    return r, r


by_os: dict[str, Callable[[], tuple[KeyboardTracker, KeyboardCommander]]] = {
    constants.OS.win32: win32_winput,
    constants.OS.linux: linux_evdev,
}
