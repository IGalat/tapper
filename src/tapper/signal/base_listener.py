from abc import ABC
from abc import abstractmethod

from tapper.model import constants
from tapper.model import errors
from tapper.model.types_ import Signal


class SignalListener(ABC):
    """Listens to signals that may trigger actions.

    When an implementation receives the signal, it must call on_signal fn.
    """

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

    @property
    @abstractmethod
    def name(self) -> str:
        """Aspect, not concrete impl. Used as topic in event subscription."""

    @staticmethod
    @abstractmethod
    def get_for_os(os: str) -> "SignalListener":
        """
        :param os: Result of sys.platform() call, or see model/constants.
        :return: Per-OS implementation of a specific SignalListener.
        """
