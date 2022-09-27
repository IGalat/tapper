"""Keyboard keys, including lang-specific, and OS-specific."""
from functools import cache

from tapper import config

fn_keys = ["f" + str(i + 1) for i in range(24)]

numpad_keys = [
    "num0",
    "num1",
    "num2",
    "num3",
    "num4",
    "num5",
    "num6",
    "num7",
    "num8",
    "num9",
    "numpad_divide",
    "numpad_multiply",
    "numpad_minus",
    "numpad_plus",
    "numpad_dot",  # vk_decimal
    "numpad_separator",  # ?
]

lock_keys = ["caps_lock", "scroll_lock", "num_lock"]

modifiers = [
    "left_shift",
    "right_shift",
    "virtual_shift",  # windows defines them as separate VKs(16 here), so might be something
    "left_control",
    "right_control",
    "virtual_control",
    "left_alt",
    "right_alt",
    "virtual_alt",
]

navigation_keys = [
    "up_arrow",
    "down_arrow",
    "left_arrow",
    "right_arrow",
    "home",
    "end",
    "page_up",
    "page_down",
]

control_chars = ["enter", "tab", "return", "space"]

special_chars = [
    "escape",
    "windows",  # can be 'super' or 'meta' on linux, 'command' on mac
    "apps",  # opens the menu like right mouse button. Near rctrl usually
    "clear",  # num5 when num lock off
    "backspace",
    "delete",
    "insert",
    "print_screen",
    "control_break",
    "pause",
    *numpad_keys,
    *lock_keys,
    *modifiers,
    *navigation_keys,
    *control_chars,
]

"""If alias is to many keys, first is preferred."""
aliases = {
    # modifiers
    "lshift": ["left_shift"],
    "rshift": ["right_shift"],
    "shift": ["left_shift", "right_shift", "virtual_shift"],
    "lalt": ["left_alt"],
    "ralt": ["right_alt"],
    "alt": ["left_alt", "right_alt", "virtual_alt"],
    "lcontrol": ["left_control"],
    "lctrl": ["left_control"],
    "rcontrol": ["right_control"],
    "rctrl": ["right_control"],
    "control": ["left_control", "right_control", "virtual_control"],
    "ctrl": ["left_control", "right_control", "virtual_control"],
    # navigation
    "arrow_up": ["up_arrow"],
    "arrow_down": ["down_arrow"],
    "arrow_left": ["left_arrow"],
    "arrow_right": ["right_arrow"],
    # other special chars
    "esc": ["escape"],
    "win": ["windows"],
    "del": ["delete"],
    "ins": ["insert"],
    "caps": ["caps_lock"],
    "break": ["control_break"],
}

platform_specific_keys = {
    "win32": [
        "browser_back",
        "browser_forward",
        "browser_refresh",
        "browser_stop",
        "browser_search",
        "browser_favorites",
        "browser_start_and_home",
        #
        "volume_mute",
        "volume_down",
        "volume_up",
        "next_track",
        "previous_track",
        "stop_media",
        "play_pause_media",
        "start_mail",
        "select_media",
        "launch_app1",
        "launch_app2",
        #
        "attn",
        "crsel",
        "exsel",
        "erase_eof",
        "play",
        "zoom",
        "pa1",
        "oem_clear",
    ]
}

chars_en = [
    *"`1234567890-="
    "qwertyuiop[]\\"
    "asdfghjkl;'"
    "zxcvbnm,./"
    "~!@#$%^&*()_+"
    "QWERTYUIOP{}|"
    'ASDFGHJKL:"'
    "ZXCVBNM<>?"
]
chars_en_lower = chars_en[: len(chars_en) // 2]
chars_en_upper = chars_en[len(chars_en) // 2 :]


@cache
def get_key_list() -> list[str]:
    """All keys on en-US keyboard, including platform specific, BUT not aliases."""
    plat_keys = []
    if config.platform in platform_specific_keys:
        plat_keys = platform_specific_keys[config.platform]
    return [*special_chars, *chars_en, *plat_keys]


@cache
def get_keys() -> dict[str, list[str] | None]:
    """All keys on en-US keyboard, including platform specific and aliases.

    Only aliases value is not None but a list of non-alias keys.
    """
    all_keys = dict.fromkeys(get_key_list(), None)
    all_keys.update(aliases)
    return all_keys


"""Dev note
Use cases:
    User looking up all keys
    Input parsing with aliases. Need to count any alias as target (e.g. lshift and rshift counts as shift)
    Output parsing with aliases. Can use first alias(shift -> lshift)
    Multilang. Whether caps matters to char depends on language(is char a symbol or letter?)
        @cache fn-> is char a symbol? use on english as well as other lang
"""
