from abc import ABC
from abc import abstractmethod


class SignalListener(ABC):
    """Listens to signals that may trigger actions.

    Will run in a separate thread.
    """

    @abstractmethod
    def get_possible_signal_symbols(self) -> list[str]:
        """All symbols that this listener may send to on_signal."""

    def on_signal(self, symbol: str, down: bool) -> bool:
        """This function is substituted with actual signal processing.

        Do not override.

        :param symbol: Must be symbol from get_possible_signal_symbols
        :param down:
        :return:
        """

    @abstractmethod
    def start(self) -> None:
        """Initialize resources and start listening."""

    @abstractmethod
    def stop(self) -> None:
        """And clean resources, this is terminal."""
