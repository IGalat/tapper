from typing import Optional

from tapper.command.keyboard.keyboard_commander import KeyboardCommander
from tapper.command.mouse.mouse_commander import MouseCommander
from tapper.model import constants
from tapper.model.types_ import Signal
from tapper.signal.base_signal_listener import SignalListener


class Listener(SignalListener):
    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @staticmethod
    def get_for_os(os: str) -> "SignalListener":
        return Listener()


class KbCmd(KeyboardCommander):
    listener: SignalListener
    all_signals: list[Signal]

    def __init__(self, listener: SignalListener, all_signals: list[Signal]) -> None:
        self.listener = listener
        self.all_signals = all_signals

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def pressed(self, symbol: str) -> bool:
        pass

    def toggled(self, symbol: str) -> bool:
        pass

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        pass


class MouseCmd(MouseCommander):
    listener: SignalListener
    all_signals: list[Signal]

    def __init__(self, listener: SignalListener, all_signals: list[Signal]) -> None:
        self.listener = listener
        self.all_signals = all_signals

    def press(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.DOWN)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def release(self, symbol: str) -> None:
        signal = (symbol, constants.KeyDirBool.UP)
        self.all_signals.append(signal)
        self.listener.on_signal(signal)

    def move(
        self, x: Optional[int] = None, y: Optional[int] = None, relative: bool = False
    ) -> None:
        pass

    def pressed(self, symbol: str) -> bool:
        pass

    def toggled(self, symbol: str) -> bool:
        pass

    def pressed_toggled(self, symbol: str) -> tuple[bool, bool]:
        pass

    def get_pos(self) -> tuple[int, int]:
        pass
