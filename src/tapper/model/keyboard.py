"""Keyboard keys, including lang-specific, and OS-specific."""
from functools import cache

from tapper.model import constants
from tapper.model.types_ import SymbolsWithAliases

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
    # windows defines separate shift, control, alt as separate VKs(16 here). Their purpose is
    # tracking the state: if any of two shifts is pressed, this will be pressed. Not is
    # not very useful in tapper, as users can inquire .pressed("shift") to get the same result.
    "virtual_shift",
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
    "left_windows",  # can be 'super' or 'meta' on linux, 'command' on mac
    "right_windows",
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
aliases: SymbolsWithAliases = {
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
    "lwin": ["left_windows"],
    "rwin": ["right_windows"],
    "win": ["left_windows", "right_windows"],
    "del": ["delete"],
    "ins": ["insert"],
    "caps": ["caps_lock"],
    "break": ["control_break"],
    # control chars
    "\n": ["enter"],
    "\t": ["tab"],
    "\r": ["return"],
}

platform_specific_keys = {
    constants.os.win32: [
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
def get_key_list(os: str | None = None) -> list[str]:
    """All keys on en-US keyboard, including platform specific, BUT not aliases."""
    plat_keys = []
    if os in platform_specific_keys:
        plat_keys = platform_specific_keys[os]
    return [*special_chars, *chars_en, *plat_keys]


@cache
def get_keys(os: str | None = None) -> SymbolsWithAliases:
    """All keys on en-US keyboard, including platform specific and aliases.

    Only aliases value is not None but a list of non-alias keys.
    """
    all_keys = dict.fromkeys(get_key_list(os), None)
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

"""All VK codes that Windows keyboard may output or take and corresponding symbols."""
win32_vk_code_to_symbol_map: dict[int, str] = {
    # chars_en
    192: "`",
    49: "1",
    50: "2",
    51: "3",
    52: "4",
    53: "5",
    54: "6",
    55: "7",
    56: "8",
    57: "9",
    48: "0",
    189: "-",
    187: "=",
    81: "q",
    87: "w",
    69: "e",
    82: "r",
    84: "t",
    89: "y",
    85: "u",
    73: "i",
    79: "o",
    80: "p",
    219: "[",
    221: "]",
    220: "\\",
    65: "a",
    83: "s",
    68: "d",
    70: "f",
    71: "g",
    72: "h",
    74: "j",
    75: "k",
    76: "l",
    186: ";",
    222: "'",
    90: "z",
    88: "x",
    67: "c",
    86: "v",
    66: "b",
    78: "n",
    77: "m",
    188: ",",
    190: ".",
    191: "/",
    # numpad_keys
    96: "num0",
    97: "num1",
    98: "num2",
    99: "num3",
    100: "num4",
    101: "num5",
    102: "num6",
    103: "num7",
    104: "num8",
    105: "num9",
    111: "numpad_divide",
    106: "numpad_multiply",
    109: "numpad_minus",
    107: "numpad_plus",
    110: "numpad_dot",
    108: "numpad_separator",
    # lock_keys
    20: "caps_lock",
    145: "scroll_lock",
    144: "num_lock",
    # modifiers
    160: "left_shift",
    161: "right_shift",
    16: "virtual_shift",
    162: "left_control",
    163: "right_control",
    17: "virtual_control",
    164: "left_alt",
    165: "right_alt",
    18: "virtual_alt",
    # navigation_keys
    38: "up_arrow",
    40: "down_arrow",
    37: "left_arrow",
    39: "right_arrow",
    36: "home",
    35: "end",
    33: "page_up",
    34: "page_down",
    # control_chars
    13: "enter",
    9: "tab",
    10: "return",
    32: "space",
    # special_chars
    27: "escape",
    91: "left_windows",
    92: "right_windows",
    93: "apps",
    12: "clear",
    8: "backspace",
    46: "delete",
    45: "insert",
    44: "print_screen",
    3: "control_break",
    19: "pause",
    # windows-specific keys
    166: "browser_back",
    167: "browser_forward",
    168: "browser_refresh",
    169: "browser_stop",
    170: "browser_search",
    171: "browser_favorites",
    172: "browser_start_and_home",
    #
    173: "volume_mute",
    174: "volume_down",
    175: "volume_up",
    176: "next_track",
    177: "previous_track",
    178: "stop_media",
    179: "play_pause_media",
    180: "start_mail",
    181: "select_media",
    182: "launch_app1",
    183: "launch_app2",
    #
    246: "attn",
    247: "crsel",
    248: "exsel",
    249: "erase_eof",
    250: "play",
    251: "zoom",
    253: "pa1",
    254: "oem_clear",
}
