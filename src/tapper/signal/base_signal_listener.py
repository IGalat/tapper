from abc import ABC
from abc import abstractmethod

from tapper.model import errors
from tapper.model import types_


class SignalListener(ABC):
    """Listens to signals that may trigger actions.

    When an implementation receives the signal, it must call on_signal fn.
    """

    @classmethod
    @abstractmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        """All symbols that this listener may send to on_signal."""

    def on_signal(self, signal: types_.Signal) -> bool:
        """This function is substituted with actual signal processing.

        Do not implement.

        :return: If True: signal must be propagated further to system as normal.
                 If False: signal must be suppressed, so that other apps don't
                    receive it. This means an action has been triggered.
        """
        raise errors.NotSubstitutedError

    @abstractmethod
    def start(self) -> None:
        """Initialize resources and start listening.

        This will be launched in a separate thread.
        """

    @abstractmethod
    def stop(self) -> None:
        """And clean resources, this is terminal."""
