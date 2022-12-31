from abc import ABC
from abc import abstractmethod


class ResourceController(ABC):
    """
    Allows issuing commands and getting the state of
    a resource, such as keyboard, windows, cpu, os, network.

    This is a high-level component that doesn't implement platform-dependent logic.
    Instead, it contains a class with specific implementation, which during init it instantiates.
    Underlying component's naming is Tracker for getting state,
    Commander for issuing commands, TrackerCommander for both.

    This implements common logic, such as caching.
    Also is responsible for notifying about emulated actions that are about to be performed.
    """

    @abstractmethod
    def _init(self) -> None:
        """Initialize underlying components. All required data should be provided as fields beforehand."""

    @abstractmethod
    def _start(self) -> None:
        """Assumes init already called."""

    @abstractmethod
    def _stop(self) -> None:
        """And clean resources, this is terminal."""
