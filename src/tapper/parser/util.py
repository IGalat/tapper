def split(text: str, delimiter: str, min_len: int = 1) -> list[str]:
    """Split str, with minimum length of tokens.

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
    while (delim_pos := text.find(delimiter, start_pos + min_len)) != -1:
        result.append(text[start_pos:delim_pos])
        start_pos = delim_pos + len(delimiter)
    result.append(text[start_pos:])
    if not result[-1]:
        raise ValueError(f"Delimiter was in the last position in '{text}'.")
    return result
