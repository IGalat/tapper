import copy
import re
from dataclasses import dataclass
from dataclasses import field
from functools import cache
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
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.parser import common
from tapper.util import datastructs

SYMBOL_DELIMITER = "+"
PROPERTY_DELIMITER = " "
COMMA_DELIMITER = ","
COMBO_DELIMITER = ";"

shift = "left_shift"

ki_shift_down = lambda: KeyInstruction(shift, constants.KeyDir.DOWN)
ki_shift_up = lambda: KeyInstruction(shift, constants.KeyDir.UP)


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

    def __hash__(self) -> int:
        return super().__hash__()


def to_content(combo: re.Match[str]) -> str:
    """Extracts contents of the combo from re.Match object."""
    return combo.group()[2:-1]  # todo len, minus escaping backslashes


def resolve_last_with_props(
    base_ins: SendInstruction, props: list[str]
) -> list[SendInstruction]:
    mult_allowed = True
    dir_allowed = True
    result = [base_ins]
    for prop in props:
        if sleep := sleep_prop(prop):
            if result[-1].dir == constants.KeyDir.CLICK:
                result[-1].dir = constants.KeyDir.DOWN
                result.append(sleep)
                result.append(KeyInstruction(result[-2].symbol, constants.KeyDir.UP))
                dir_allowed = False
            else:
                result.append(sleep)
        elif mult := mult_prop(prop):
            if not mult_allowed:
                raise SendParseError
            result = result * mult
        elif dir := dir_prop(prop):
            if not dir_allowed:
                raise SendParseError
            dir_allowed = False
            ins = result[-1]
            if not isinstance(ins, KeyInstruction):
                raise SendParseError
            else:
                last = copy.deepcopy(ins)
                last.dir = dir
                result[-1] = last
                if constants.KeyDir.DOWN != dir:
                    mult_allowed = False
        else:
            raise SendParseError
    return result


def resolve_chain_opening_with_props(
    base_ins: SendInstruction, props: list[str]
) -> list[SendInstruction]:
    result = [base_ins]
    for prop in props:
        if sleep := sleep_prop(prop):
            result.append(sleep)
        else:
            raise SendParseError
    return result


def sleep_prop(prop: str) -> Optional[SleepInstruction]:
    if common.SECONDS.regex.fullmatch(prop):
        return SleepInstruction(common.SECONDS.fn(prop))
    if common.MILLIS.regex.fullmatch(prop):
        return SleepInstruction(common.MILLIS.fn(prop))
    return None


def mult_prop(prop: str) -> Optional[int]:
    if re.fullmatch(r"\d+x", prop):
        result = int(prop[:-1])
        if result <= 0:
            raise ValueError
        return result
    return None


def dir_prop(prop: str) -> Optional[str]:
    try:
        return constants.KeyDir(prop)
    except ValueError:
        return None


@dataclass
class SendParser:
    """Parses the 'send' command."""

    combo_prefix: str = ""
    combo_suffix: str = ""
    pattern: re.Pattern[str] = ""  # type: ignore
    """Pattern of the combo."""
    symbols: dict[str, type[SendInstruction]] = field(default_factory=dict)
    """Symbol and corresponding command. Includes aliases."""
    aliases: dict[str, str] = field(default_factory=dict)
    """Alias to first non-alias mapping."""
    regexes: dict[
        re.Pattern[str], tuple[type[SendInstruction], Callable[[str], Any]]
    ] = field(default_factory=dict)
    """Regex and corresponding instruction and action to parse values for the instruction."""

    def __hash__(self) -> int:
        return super().__hash__()

    def set_wrap(self, combo_wrap: str) -> None:
        self.combo_prefix, self.combo_suffix, self.pattern = parse_wrap(combo_wrap)

    @cache
    def parse(self, command: str, shift_in: str | None = None) -> list[SendInstruction]:
        """Parse send command into sequential instructions."""
        global shift
        if not self.pattern:
            self.set_wrap(COMBO_WRAP)

        if shift_in:
            shift = shift_in
        shift_down = bool(shift_in)
        result = []
        combos = self.match_combos(command).copy()

        i = 0
        while i < len(command):
            if combos:
                combo = combos[0]
                if i == combo.start():
                    combos.remove(combo)
                    cmds = self.parse_combo(to_content(combo), shift_down)
                    result.extend(cmds)

                    i = combo.end()
                    if i >= len(command):
                        break
                    continue
            symbol = self.unalias(command[i])
            if symbol not in self.symbols:
                raise SendParseError(
                    f"Symbol '{symbol}' not recognised in command '{command}'"
                )
            if symbol in keyboard.chars_en_upper:
                symbol = keyboard.chars_en_upper_to_lower[symbol]
                if not shift_down:
                    result.append(ki_shift_down())
                    shift_down = True
                result.append(KeyInstruction(symbol))
            else:
                if shift_down:
                    result.append(ki_shift_up())
                    shift_down = False
                result.append(KeyInstruction(symbol))
            i += 1

        if shift_down and not shift_in:
            result.append(ki_shift_up())
        elif shift_in and not shift_down:
            result.append(ki_shift_down())
        return result

    @cache
    def match_combos(self, command: str) -> list[re.Match[str]]:
        start = 0
        matches = []
        while match := self.pattern.search(command, pos=start):
            matches.append(match)
            start = match.end()
        return matches

    def parse_combo(self, content: str, shift_down: bool) -> list[SendInstruction]:
        """
        Parse a combo from content string
        :param content: string like "a+b"
        :param shift_down: if shift is down before combo
        :return: parsed instructions
        """
        result = self._parse_combo(content).copy()
        if shift_down:
            result.insert(0, ki_shift_up())
            result.append(ki_shift_down())
        return result

    @cache
    def _parse_combo(self, content: str) -> list[SendInstruction]:

        if not content:
            raise SendParseError

        symbols_split = common.split(content, SYMBOL_DELIMITER)
        chain_symbols_split = symbols_split[:-1]

        for i in range(len(symbols_split)):
            one_split = symbols_split[i]
            if COMBO_DELIMITER in one_split[1:]:
                combo_delim_index = i + 1 + one_split.index(COMBO_DELIMITER, 1)
                combo_delim_index += sum(len(s) for s in symbols_split[:i])

                parsed_combos = [
                    self._parse_combo(combo).copy()
                    for combo in [
                        content[: combo_delim_index - 1],
                        content[combo_delim_index:],
                    ]
                ]
                return datastructs.to_flat_list(parsed_combos)

        result = []
        result_wrap = []

        for chain_split in chain_symbols_split:
            symbol, props = common.parse_symbol_and_props(
                chain_split, PROPERTY_DELIMITER
            )
            key = _Key(self.unalias(symbol), props)
            opening, closing = self.parse_chain_split(key)
            result.extend(opening)
            if closing:
                result_wrap.append(closing)

        last_symbols_split = common.split(symbols_split[-1], COMMA_DELIMITER)
        for last_split in last_symbols_split:
            symbol, props = common.parse_symbol_and_props(
                last_split, PROPERTY_DELIMITER
            )
            instructions = self.parse_last_split(_Key(self.unalias(symbol), props))
            result.extend(instructions)

        result.extend(result_wrap[::-1])
        return result

    @cache
    def parse_chain_split(
        self, key: _Key
    ) -> tuple[list[SendInstruction], Optional[SendInstruction]]:
        """
        In combo like       "a+b 20ms+lmb 2x"
        :param key: one of   ^ ^^^^^^
        :return: opening instruction, closing instruction
        """
        if key.symbol not in self.symbols:
            if key.props:
                raise SendParseError
            return self.parse_regex_symbol(key.symbol), None

        if key.symbol in keyboard.chars_en_upper:
            raise SendParseError

        instruction_type = self.symbols[key.symbol]
        if instruction_type == KeyInstruction:
            base_ins = KeyInstruction(key.symbol)
        else:
            base_ins = WheelInstruction(key.symbol)

        opening = copy.deepcopy(base_ins)
        opening.dir = constants.KeyDir.DOWN
        closing = copy.deepcopy(base_ins)
        closing.dir = constants.KeyDir.UP

        if key.props:
            try:
                return resolve_chain_opening_with_props(opening, key.props), closing
            except ValueError:
                raise SendParseError

        return [opening], closing

    def unalias(self, symbol: str) -> str:
        """Returns non-alias symbol for a given symbol"""
        try:
            return self.aliases[symbol]
        except KeyError:
            return symbol

    @cache
    def parse_last_split(self, key: _Key) -> list[SendInstruction]:
        """
        In combo like       "a+b 20ms+lmb 2x"
        :param key:                   ^^^^^^
        :return: all instructions
        """
        if key.symbol not in self.symbols:
            if key.props:
                raise SendParseError
            return self.parse_regex_symbol(key.symbol)

        if key.symbol in keyboard.chars_en_upper:
            raise SendParseError

        instruction_type = self.symbols[key.symbol]
        if instruction_type == KeyInstruction:
            base_ins = KeyInstruction(key.symbol)
        else:
            base_ins = WheelInstruction(key.symbol)

        if key.props:
            try:
                return resolve_last_with_props(base_ins, key.props)
            except ValueError:
                raise SendParseError
        return [base_ins]

    @cache
    def parse_regex_symbol(self, symbol: str) -> list[SendInstruction]:
        for regex, value in self.regexes.items():
            instruction_type, fn = value
            if regex.fullmatch(symbol):
                return [instruction_type(fn(symbol))]  # type: ignore
        else:
            raise SendParseError
