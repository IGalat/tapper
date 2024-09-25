from functools import cache

from tapper import config
from tapper.model import keyboard
from tapper.model import languages
from tapper.model.languages import Lang
from tapper.parser import send_parser

_combo_pattern = send_parser.parse_wrap(config.send_combo_wrap)


@cache
def to_en(language: str | int | Lang, text: str) -> str:
    """
    Transliterates to en_US, so tapper can understand your hotkeys/actions.

    Will only transliterate characters outside $() - or whatever the send_combo_wrap is in your tapper.config
    """
    lang = languages.get(language)
    if len(lang.charset) != len(keyboard.chars_en):
        raise NotImplementedError(
            f"Language {language} you're trying to transliterate is not implemented."
        )
    result = []
    combos = send_parser.match_combos(text, _combo_pattern)
    i = 0
    while i < len(text):
        if combos:
            combo = combos[0]
            if i == combo.start():
                combos.remove(combo)
                result.append(combo.group())

                i = combo.end()
                if i >= len(text):
                    break
        if text[i] == " ":
            result.append(" ")
        else:
            i18n_index = lang.charset.index(text[i])
            result.append(keyboard.chars_en[i18n_index])
        i += 1
    return "".join(result)
