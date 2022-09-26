from tapper.model import keyboard
from tapper.model import mouse

kb_lang_dependent_characters = (
    13 + 13 + 11 + 10  # numbers row  # qwerty row  # asdf row  # zxcv row
) * 2  # lower, upper


def test_keyboard_alias() -> None:
    all_keys = keyboard.get_keys()
    keys_no_alias = keyboard.get_key_list()
    assert len(keys_no_alias) + len(keyboard.aliases) == len(all_keys)
    for ref_keys in all_keys.values():
        if not ref_keys:
            continue
        for ref_key in ref_keys:
            assert ref_key in keys_no_alias


def test_keyboard_lang_chars_len() -> None:
    assert kb_lang_dependent_characters == len(keyboard.chars_en)
    assert len(keyboard.chars_en_lower) == len(keyboard.chars_en_upper)


def test_mouse_alias() -> None:
    all_keys = mouse.get_keys()
    keys_no_alias = mouse.get_key_list()
    assert len(keys_no_alias) + len(mouse.aliases) == len(all_keys)
    for ref_keys in all_keys.values():
        if not ref_keys:
            continue
        for ref_key in ref_keys:
            assert ref_key in keys_no_alias
