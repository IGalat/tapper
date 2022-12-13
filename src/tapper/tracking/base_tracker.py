from abc import ABC
from abc import abstractmethod


class ResourceTracker(ABC):
    """
    Tracks a resource, supplying state information.

    Does not impact tapper on its own, but user can access it,
    and can be used as condition for a Tree trigger.
    """

    @abstractmethod
    def start(self) -> None:
        """Initialize resources and start listening.

        This will be launched in a separate thread.
        """

    @abstractmethod
    def stop(self) -> None:
        """And clean resources, this is terminal."""

    @staticmethod
    @abstractmethod
    def get_for_os(os: str) -> "ResourceTracker":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of a specific ResourceTracker.
        """
