from abc import ABC


class Commander(ABC):
    """Allows sending commands. Convenience class.

    Inheritors focus on one aspect, such as keyboard.
    """
