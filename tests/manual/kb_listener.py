import sys

from tapper.model.constants import ListenerResult
from tapper.model.types_ import Signal
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener


def on_signal(signal: Signal) -> ListenerResult:
    print(signal)
    return ListenerResult.SUPPRESS


def kb_listener() -> None:
    listener: KeyboardSignalListener = KeyboardSignalListener.get_for_os(sys.platform)
    listener.on_signal = on_signal
    listener.start()


def main() -> None:
    kb_listener()


if __name__ == "__main__":
    main()
