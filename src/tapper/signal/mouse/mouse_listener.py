from abc import ABC

from tapper.model import constants
from tapper.model import mouse
from tapper.signal import base_listener


class MouseSignalListener(base_listener.SignalListener, ABC):
    """Listens to mouse button presses and releases, and movement.
    See SignalListener for listener documentation.

    Mouse move and wheel scroll are on_signal(symbol, down=True)
    """

    name = constants.Aspect.mouse

    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        temp: list[str] = mouse.get_key_list()
        return temp
