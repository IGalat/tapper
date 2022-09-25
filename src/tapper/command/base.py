from abc import ABC

from tapper.command.symbol import CommandSymbol


class Commander(ABC):
    """Allows sending commands. Convenience class.

    Inheritors focus on one aspect, such as keyboard.
    """

    def get_possible_command_symbols(self) -> list[CommandSymbol]:
        """"""
        return []
