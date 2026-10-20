from abc import ABC

from tapper.model import constants
from tapper.signal import base_listener


class KeyboardSignalListener(base_listener.SignalListener, ABC):
    """Listens to keyboard key presses and releases.
    See SignalListener for listener documentation."""

    name = constants.Aspect.keyboard
