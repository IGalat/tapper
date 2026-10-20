from abc import ABC
from abc import abstractmethod

from tapper.controller.resource_controller import ResourceController
from tapper.model import constants
from tapper.model.languages import Lang
from tapper.state import keeper


class KeyboardDriver(ABC):
    """OS implementation of one aspect: reads its state and commands it."""

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
    def lang(self, lang: str | int | Lang | None = None) -> Lang | None:
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
    aspect = constants.Aspect.keyboard
    _driver: KeyboardDriver
    _emul_keeper: keeper.Emul

    def _start(self) -> None:
        self._driver.start()

    def _stop(self) -> None:
        self._driver.stop()

    def pressed(self, symbol: str) -> bool:
        """Is key held down."""
        return self._driver.pressed(symbol)

    def toggled(self, symbol: str) -> bool:
        """Is key toggled."""
        return self._driver.toggled(symbol)

    def lang(self, lang: str | int | Lang | None = None) -> Lang | None:
        """Get current language. If param `lang` specified, will return None if it doesn't match."""
        return self._driver.lang(lang)

    def press(self, symbol: str) -> None:
        """Presses down one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.DOWN))
        self._driver.press(symbol)

    def release(self, symbol: str) -> None:
        """Releases (presses up) one key."""
        self._emul_keeper.will_emulate((symbol, constants.KeyDirBool.UP))
        self._driver.release(symbol)

    def set_lang(self, lang: str | int | Lang, system_wide: bool = False) -> None:
        """
        Switch input to specified language.

        If this language is not in your user's language input list, nothing happens.

        :param lang: see model.languages
        :param system_wide: change lang for all apps. If False, only for active one.
        """
        self._driver.set_lang(lang, system_wide)
