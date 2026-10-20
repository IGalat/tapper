from abc import ABC
from abc import abstractmethod
from typing import ClassVar

from tapper.model import constants
from tapper.model import errors
from tapper.model.types_ import Signal


class SignalListener(ABC):
    """Listens to signals that may trigger actions.

    When an implementation receives the signal, it must call on_signal fn.
    """

    name: ClassVar[constants.Aspect]
    """Aspect, not concrete impl. Used as topic in event subscription and in boot.platforms."""

    @classmethod
    @abstractmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        """All symbols that this listener may send to on_signal."""

    def on_signal(self, signal: Signal) -> constants.ListenerResult:
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

        Implementations should start the event loop in a separate thread.
        """

    @abstractmethod
    def stop(self) -> None:
        """And clean resources, this is terminal."""
