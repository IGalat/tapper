import pytest
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse

kb_lang_dependent_characters = (
    13 + 13 + 11 + 10  # numbers row  # qwerty row  # asdf row  # zxcv row
) * 2  # lower, upper


@pytest.mark.parametrize(
    "os", [constants.OS.dummy, constants.OS.win32, constants.OS.linux]
)
def test_keyboard_alias(os: str) -> None:
    all_keys = keyboard.get_keys(os)
    keys_no_alias = keyboard.get_key_list(os)
    assert len(keys_no_alias) + len(keyboard.aliases) == len(all_keys)
    for ref_keys in all_keys.values():
        if not ref_keys:
            continue
        for ref_key in ref_keys:
            assert ref_key in keys_no_alias


def test_keyboard_lang_chars_len() -> None:
    assert kb_lang_dependent_characters == len(keyboard.chars_en)
    assert len(keyboard.chars_en_lower) == len(keyboard.chars_en_upper)


def test_win32_vk_code_symbol_map() -> None:
    os_kb_map_test(constants.OS.win32, keyboard.win32_vk_code_to_symbol_map)


def test_linux_vk_code_symbol_map() -> None:
    os_kb_map_test(constants.OS.linux, keyboard.linux_evdev_code_to_symbol_map)


def os_kb_map_test(os: constants.OS, code_to_symbol_map: dict[int, str]) -> None:
    assert len(code_to_symbol_map) == len(keyboard.get_key_list(os)) - len(
        keyboard.chars_en_upper
    )
    reverse_map = [key for (code, key) in code_to_symbol_map.items()]
    for symbol in keyboard.get_key_list(os):
        assert symbol in reverse_map or symbol in keyboard.chars_en_upper


def test_mouse_alias() -> None:
    all_keys = mouse.get_keys()
    keys_no_alias = mouse.get_key_list()
    assert len(keys_no_alias) + len(mouse.aliases) == len(all_keys)
    for ref_keys in all_keys.values():
        if not ref_keys:
            continue
        for ref_key in ref_keys:
            assert ref_key in keys_no_alias
