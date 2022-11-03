import re
from dataclasses import dataclass
from dataclasses import field

from tapper.model import constants
from tapper.model import keyboard
from tapper.model.errors import SendParseError
from tapper.model.send import COMBO_CONTENT
from tapper.model.send import COMBO_WRAP
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction


def parse_wrap(combo_wrap: str) -> tuple[str, str, re.Pattern[str]]:
    prefix, suffix = combo_wrap.split("_")
    return prefix, suffix, re.compile(prefix + COMBO_CONTENT + suffix)


@dataclass
class SendParser:
    """Parses the 'send' command."""

    combo_prefix: str = ""
    combo_suffix: str = ""
    pattern: re.Pattern[str] = ""  # type: ignore
    """Pattern of the combo."""
    symbols: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Symbol and corresponding command."""
    regexes: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Regex and corresponding command."""

    def set_wrap(self, combo_wrap: str) -> None:
        self.combo_prefix, self.combo_suffix, self.pattern = parse_wrap(combo_wrap)

    def parse(self, command: str) -> list[SendInstruction]:
        """Parse send command into sequential instructions."""
        if not self.pattern:
            self.set_wrap(COMBO_WRAP)

        shift_down = False
        result = []
        combos = self.match_combos(command)
        for i in range(len(command)):
            for combo in combos:
                if i == combo.start():
                    i = combo.end() - 1
                    combos.pop()
                    result.extend(self.parse_combo(self.to_content(combo)))
                    continue
            symbol = command[i]
            if symbol not in self.symbols:
                raise SendParseError(
                    f"Symbol '{symbol}' not recognised in command '{command}'"
                )
            if symbol in keyboard.chars_en_upper:
                symbol = keyboard.chars_en_upper_to_lower[symbol]
                if not shift_down:
                    result.append(KeyInstruction(keyboard.shift, constants.KeyDir.DOWN))
                    shift_down = True
                result.append(KeyInstruction(symbol))
            else:
                if shift_down:
                    result.append(KeyInstruction(keyboard.shift, constants.KeyDir.UP))
                    shift_down = False
                result.append(KeyInstruction(symbol))

        if shift_down:
            result.append(KeyInstruction(keyboard.shift, constants.KeyDir.UP))
        return result

    def match_combos(self, command: str) -> list[re.Match[str]]:
        start = 0
        matches = []
        while match := self.pattern.search(command[start:]):
            matches.append(match)
            start = match.end()
        return matches

    def to_content(self, combo: re.Match[str]) -> str:
        """Extracts contents of the combo from re.Match object."""
        pass

    def parse_combo(self, combo: str) -> list[SendInstruction]:
        pass
