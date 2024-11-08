import re
from typing import Any
from typing import Callable


class ParsedProp:
    regex: re.Pattern[str]
    fn: Callable[[str], Any]


class SECONDS(ParsedProp):
    @staticmethod
    def parse_seconds(s: str) -> float:
        result = float(s[:-1])
        if result <= 0:
            raise ValueError
        return result

    regex = re.compile(r"\d*\.?\d+s")
    fn = parse_seconds


class MILLIS(ParsedProp):
    @staticmethod
    def parse_millis(ms: str) -> float:
        result = float(ms[:-2]) / 1000
        if result <= 0:
            raise ValueError
        return result

    regex = re.compile(r"\d+ms")
    fn = parse_millis


class CURSOR_MOVE(ParsedProp):
    @staticmethod
    def parse_xy(coord_str: str) -> tuple[tuple[int, int], bool]:
        y_pos = coord_str.find("y")
        relative = coord_str[-1] == "r"
        last_pos = len(coord_str) - 1 if relative else len(coord_str)
        return (int(coord_str[1:y_pos]), int(coord_str[y_pos + 1 : last_pos])), relative

    regex = re.compile(r"^x-?\d+y-?\d+r?$")
    fn = parse_xy


def parse_sleep_time(prop: str) -> float | None:
    """If doesn't match sleep pattern, will return None."""
    if SECONDS.regex.fullmatch(prop):
        return SECONDS.fn(prop)
    if MILLIS.regex.fullmatch(prop):
        return MILLIS.fn(prop)
    return None


def split(text: str, delimiter: str) -> list[str]:
    """Split str, with minimum length of tokens same as delimiter.

    Allows using the same delimiter as token.

    Example:
        ("a++", "+") => ["a", "+"]
        ("++a++", "+") => ["+", "a", "+"]
    """
    if not text:
        return []
    if not delimiter:
        raise ValueError("No delimiter specified.")
    result = []
    start_pos = 0
    while (delim_pos := text.find(delimiter, start_pos + len(delimiter))) != -1:
        result.append(text[start_pos:delim_pos])
        start_pos = delim_pos + len(delimiter)
    result.append(text[start_pos:])
    if not result[-1]:
        raise ValueError(f"Delimiter was in the last position in '{text}'.")
    return result


def parse_symbol_and_props(
    sym_props_str: str, property_delimiter: str
) -> tuple[str, list[str]]:
    """String of symbol and props from one string.
    Example: "lmb 2x 20ms" -> ("lmb", ["2x", "20ms"])
    """
    sym_props = split(sym_props_str, property_delimiter)
    props = [] if len(sym_props) < 2 else sym_props[1:]
    return sym_props[0], props
