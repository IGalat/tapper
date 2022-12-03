from abc import ABC
from abc import abstractmethod


class Commander(ABC):
    """Allows sending commands. Convenience class.

    Inheritors focus on one aspect, such as keyboard.
    """

    def start(self) -> None:
        """Initialize resources. Not a separate thread; shouldn't be blocking."""

    def stop(self) -> None:
        """And clean resources, this is terminal."""

    @staticmethod
    @abstractmethod
    def get_for_os(os: str) -> "Commander":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of a specific Commander.
        """
