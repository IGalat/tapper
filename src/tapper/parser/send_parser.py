from dataclasses import dataclass

from tapper.model.send import SendInstruction


@dataclass
class SendParser:
    """Parses the 'send' command."""

    def parse(self, command: str) -> list[SendInstruction]:
        """Parse send command into sequential instructions."""
        pass
