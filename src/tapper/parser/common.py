from typing import Any
from typing import Callable


class ParsedProp:
    regex: str
    fn: Callable[[str], Any]


class SECONDS(ParsedProp):
    @staticmethod
    def parse_seconds(s: str) -> float:
        return float(s[:-1])

    regex = r"\d*\.?\d+s"
    fn = parse_seconds


class MILLIS(ParsedProp):
    @staticmethod
    def parse_millis(ms: str) -> float:
        return float(ms[:-2]) / 1000

    regex = r"\d+ms"
    fn = parse_millis


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
