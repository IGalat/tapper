from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import ClassVar

from tapper.model import constants


class ResourceController(ABC):
    """
    Allows issuing commands and getting the state of
    a resource, such as keyboard, windows, cpu, os, network.

    This is a high-level component that doesn't implement platform-dependent logic.
    Instead, it is given this OS's implementation on init, see boot.platforms.
    The underlying component is the Driver.

    This implements common logic, such as caching.
    Also is responsible for notifying about emulated actions that are about to be performed.
    """

    aspect: ClassVar[constants.Aspect]
    """Key in Platform.drivers."""
    _driver: Any

    def _init(self, driver: Any) -> None:
        self._driver = driver

    @abstractmethod
    def _start(self) -> None:
        """Assumes init already called."""

    @abstractmethod
    def _stop(self) -> None:
        """And clean resources, this is terminal."""
