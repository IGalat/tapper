import sys

from manual.util_mantest import killme_in
from tapper.boot import platforms
from tapper.model.constants import Aspect
from tapper.model.constants import ListenerResult
from tapper.model.types_ import Signal


def on_signal(signal: Signal) -> ListenerResult:
    print(signal)
    return ListenerResult.SUPPRESS


def mouse_listener() -> None:
    listener = platforms.for_os(sys.platform).listeners[Aspect.mouse]()
    listener.on_signal = on_signal
    listener.start()


def main() -> None:
    killme_in(30)
    mouse_listener()


if __name__ == "__main__":
    main()
