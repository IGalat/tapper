import sys

from manual.util_mantest import killme_in
from tapper.model.constants import KeyDirBool
from tapper.model.constants import ListenerResult
from tapper.model.types_ import Signal
from tapper.signal.keyboard.keyboard_listener import KeyboardSignalListener


def on_signal(signal: Signal) -> ListenerResult:
    if signal[1] == KeyDirBool.UP:
        return ListenerResult.SUPPRESS
    print(signal[0])
    return ListenerResult.SUPPRESS


def kb_listener() -> None:
    listener: KeyboardSignalListener = KeyboardSignalListener.get_for_os(sys.platform)
    listener.on_signal = on_signal
    listener.start()


def main() -> None:
    killme_in(30)
    kb_listener()


if __name__ == "__main__":
    main()
