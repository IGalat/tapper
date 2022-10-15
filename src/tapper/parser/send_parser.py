from dataclasses import dataclass
from dataclasses import field

from tapper.model.send import SendInstruction


@dataclass
class SendParser:
    """Parses the 'send' command."""

    symbol_inn_map: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Symbol and its corresponding command."""
    regex_inn_map: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Regex and corresponding command."""

    def parse(self, command: str) -> list[SendInstruction]:
        """Parse send command into sequential instructions."""
        pass
