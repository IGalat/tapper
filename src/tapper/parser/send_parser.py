import re
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Optional

from tapper.model import constants
from tapper.model import keyboard
from tapper.model.errors import SendParseError
from tapper.model.send import COMBO_CONTENT
from tapper.model.send import COMBO_WRAP
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import WheelInstruction
from tapper.parser import common
from tapper.util import datastructs

SYMBOL_DELIMITER = "+"
PROPERTY_DELIMITER = " "
COMMA_DELIMITER = ","
COMBO_DELIMITER = ";"

ki_shift_down = KeyInstruction(keyboard.shift, constants.KeyDir.DOWN)
ki_shift_up = KeyInstruction(keyboard.shift, constants.KeyDir.UP)


def parse_wrap(combo_wrap: str) -> tuple[str, str, re.Pattern[str]]:
    prefix, suffix = combo_wrap.split("_")
    return prefix, suffix, re.compile(prefix + COMBO_CONTENT + suffix)


@dataclass
class _Key:
    """Half-parsed send key."""

    symbol: str
    """Parsed symbol."""
    props: list[str]
    """Unparsed properties."""


def to_content(combo: re.Match[str]) -> str:
    """Extracts contents of the combo from re.Match object."""
    return combo.group()[2:-1]  # todo len, minus escaping backslashes


@dataclass
class SendParser:
    """Parses the 'send' command."""

    combo_prefix: str = ""
    combo_suffix: str = ""
    pattern: re.Pattern[str] = ""  # type: ignore
    """Pattern of the combo."""
    symbols: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Symbol and corresponding command."""
    regexes: dict[
        re.Pattern[str], tuple[type[SendInstruction], Callable[[str], Any]]
    ] = field(default_factory=dict)
    """Regex and corresponding instruction and action to parse values for the instruction."""

    def set_wrap(self, combo_wrap: str) -> None:
        self.combo_prefix, self.combo_suffix, self.pattern = parse_wrap(combo_wrap)

    def parse(self, command: str) -> list[SendInstruction]:
        """Parse send command into sequential instructions."""
        if not self.pattern:
            self.set_wrap(COMBO_WRAP)

        shift_down = False
        result = []
        combos = self.match_combos(command)

        i = 0
        while i < len(command):
            if combos:
                combo = combos[0]
                if i == combo.start():
                    combos.remove(combo)
                    cmds, shift_down = self.parse_combo(to_content(combo), shift_down)
                    result.extend(cmds)

                    i = combo.end()
                    if i >= len(command):
                        break
                    continue
            symbol = command[i]
            if symbol not in self.symbols:
                raise SendParseError(
                    f"Symbol '{symbol}' not recognised in command '{command}'"
                )
            if symbol in keyboard.chars_en_upper:
                symbol = keyboard.chars_en_upper_to_lower[symbol]
                if not shift_down:
                    result.append(ki_shift_down)
                    shift_down = True
                result.append(KeyInstruction(symbol))
            else:
                if shift_down:
                    result.append(ki_shift_up)
                    shift_down = False
                result.append(KeyInstruction(symbol))
            i += 1

        if shift_down:
            result.append(KeyInstruction(keyboard.shift, constants.KeyDir.UP))
        return result

    def match_combos(self, command: str) -> list[re.Match[str]]:
        start = 0
        matches = []
        while match := self.pattern.search(command, pos=start):
            matches.append(match)
            start = match.end()
        return matches

    def parse_combo(
        self, content: str, shift_down: bool
    ) -> tuple[list[SendInstruction], bool]:
        """
        Parse a combo from content string
        :param content: string like "a+b"
        :param shift_down: if shift is down before combo
        :return: parsed instructions, new shift_down value
        """
        if not content:
            raise SendParseError

        symbols_split = common.split(content, SYMBOL_DELIMITER)
        chain_symbols_split = symbols_split[:-1]

        # Buggy but will do for now. If ; - recursive
        for one_split in chain_symbols_split:
            if COMBO_DELIMITER in one_split[1:]:
                parsed_combos = [
                    self.parse_combo(combo, shift_down)
                    for combo in content.split(COMBO_DELIMITER)
                ]
                return (
                    datastructs.to_flat_list(parsed_combos),
                    shift_down,
                )

        result = []
        result_wrap = []

        for chain_split in chain_symbols_split:
            key = _Key(*common.parse_symbol_and_props(chain_split, PROPERTY_DELIMITER))
            opening, closing, shift_down = self.parse_chain_split(key, shift_down)
            result.append(opening)
            if closing:
                result_wrap.append(closing)

        last_symbols_split = common.split(symbols_split[-1], COMMA_DELIMITER)
        for last_split in last_symbols_split:
            symbol, props = common.parse_symbol_and_props(
                last_split, PROPERTY_DELIMITER
            )
            instructions, shift_down = self.parse_last_split(
                _Key(symbol, props), shift_down
            )
            result.extend(instructions)

        result.extend(result_wrap[:-1:])
        return result, shift_down

    def parse_chain_split(
        self, key: _Key, shift_down: bool
    ) -> tuple[SendInstruction, Optional[SendInstruction], bool]:
        """
        In combo like       "a+b 20ms+lmb 2x"
        :param key: one of   ^ ^^^^^^
        :param shift_down: if shift is down before symbol
        :return: opening instruction, closing instruction, new shift_down value
        """
        pass

    def parse_last_split(
        self, key: _Key, shift_down: bool
    ) -> tuple[list[SendInstruction], bool]:
        """
        In combo like       "a+b 20ms+lmb 2x"
        :param key:                   ^^^^^^
        :param shift_down: if shift is down before symbol
        :return: all instructions, new shift_down value
        """
        result = []
        if key.symbol not in self.symbols:
            if key.props:
                raise SendParseError
            return self.parse_regex_symbol(key.symbol), shift_down

        instruction_type = self.symbols[key.symbol]
        if instruction_type == KeyInstruction:
            base_ins = KeyInstruction(key.symbol)
        else:
            base_ins = WheelInstruction(key.symbol)

        result = [base_ins]

        return result, shift_down

    def parse_regex_symbol(self, symbol: str) -> list[SendInstruction]:
        for regex, value in self.regexes.items():
            instruction_type, fn = value
            if regex.fullmatch(symbol):
                return [instruction_type(fn(symbol))]  # type: ignore
        else:
            raise SendParseError
