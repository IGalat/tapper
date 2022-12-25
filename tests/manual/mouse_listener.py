import sys

from tapper.model.types_ import Signal
from tapper.signal.mouse.mouse_listener import MouseSignalListener


def on_signal(signal: Signal) -> bool:
    print(signal)
    return False


def mouse_listener() -> None:
    listener: MouseSignalListener = MouseSignalListener.get_for_os(sys.platform)
    listener.on_signal = on_signal
    listener.start()


def main() -> None:
    mouse_listener()


if __name__ == "__main__":
    main()
