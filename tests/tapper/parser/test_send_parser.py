from typing import Callable

import pytest
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.errors import SendParseError
from tapper.model.keyboard import shift
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.parser import common
from tapper.parser import send_parser
from tapper.util import datastructs

down = constants.KeyDir.DOWN
up = constants.KeyDir.UP
on = constants.KeyDir.ON
off = constants.KeyDir.OFF

KI = KeyInstruction

shift_down = KI(shift, down)
shift_up = KI(shift, up)

ParseFn = Callable[[str], list[SendInstruction]]


@pytest.fixture(scope="module")
def parse() -> ParseFn:
    _parser = send_parser.SendParser()
    for symbol in [
        *keyboard.get_keys().keys(),
        *mouse.regular_buttons,
        *mouse.button_aliases.keys(),
    ]:
        _parser.symbols[symbol] = KI
    for wheel in [*mouse.wheel_buttons, *mouse.wheel_aliases.keys()]:
        _parser.symbols[wheel] = WheelInstruction
    _parser.regexes[common.SECONDS.regex] = (SleepInstruction, common.SECONDS.fn)
    _parser.regexes[common.MILLIS.regex] = (SleepInstruction, common.MILLIS.fn)
    return _parser.parse


def key_ins(symbols: str | list[str]) -> list[KeyInstruction]:
    return [KI(sym) for sym in symbols]


class TestNonCombos:
    def test_simplest(self, parse: ParseFn) -> None:
        assert parse("a") == [KI("a")]

    def test_unregistered_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("⊕")

    def test_sequence(self, parse: ParseFn) -> None:
        assert parse("zxcvbn") == key_ins("zxcvbn")

    def test_shift_simplest(self, parse: ParseFn) -> None:
        assert parse("Q") == [shift_down, KI("q"), shift_up]

    def test_shift_multi(self, parse: ParseFn) -> None:
        assert parse("P%I") == [
            shift_down,
            *key_ins("p5i"),
            shift_up,
        ]

    def test_shift_mixed(self, parse: ParseFn) -> None:
        assert parse("2007 Ahoy!") == [
            *key_ins("2007 "),
            shift_down,
            KI("a"),
            shift_up,
            *key_ins("hoy"),
            shift_down,
            KI("1"),
            shift_up,
        ]

    def test_control_chars(self, parse: ParseFn) -> None:
        assert parse("\n\t ") == [
            KI("\n"),
            KI("\t"),
            KI(" "),
        ]


class TestSimplestCombosAndMix:
    def test_simplest(self, parse: ParseFn) -> None:
        assert parse("$(a)") == [KI("a")]

    def test_simplest_mouse_wheel(self, parse: ParseFn) -> None:
        assert parse("$(wheel_left)") == [WheelInstruction("wheel_left")]

    def test_unregistered_symbol_combo(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(qwerty)")

    def test_combo_surrounded(self, parse: ParseFn) -> None:
        assert parse("\n$(f5)q") == key_ins(["\n", "f5", "q"])

    def test_two_combos(self, parse: ParseFn) -> None:
        assert parse("$(ctrl)$(page_up)") == [
            KI("ctrl"),
            KI("page_up"),
        ]

    def test_combos_mix(self, parse: ParseFn) -> None:
        assert parse("$(caps)bc$(lshift)$(esc)f") == key_ins(
            ["caps", "b", "c", "lshift", "esc", "f"]
        )

    def test_empty_combo_is_not_combo(self, parse: ParseFn) -> None:
        assert parse("$()") == [shift_down, *key_ins("490"), shift_up]

    def test_sleep_s(self, parse: ParseFn) -> None:
        assert parse("$(2s)") == [SleepInstruction(2)]

    def test_sleep_ms(self, parse: ParseFn) -> None:
        assert parse("$(1234ms)") == [SleepInstruction(1.234)]


class TestCombosWithoutProps:
    def test_simplest(self, parse: ParseFn) -> None:
        assert parse("$(alt+q)") == [KI("alt", down), KI("q"), KI("alt", up)]

    def test_long_combo(self, parse: ParseFn) -> None:
        assert parse("$(q+w+e+r+\t)") == [
            KI("q", down),
            KI("w", down),
            KI("e", down),
            KI("r", down),
            KI("\t"),
            KI("r", up),
            KI("e", up),
            KI("w", up),
            KI("q", up),
        ]

    def test_comma(self, parse: ParseFn) -> None:
        assert parse("$(ctrl+a,c,v)") == [
            KI("ctrl", down),
            KI("a"),
            KI("c"),
            KI("v"),
            KI("ctrl", up),
        ]

    def test_semicolon(self, parse: ParseFn) -> None:
        assert (
            parse("$(ctrl+c,v;alt+tab)")
            == parse("$(ctrl+c,v)$(alt+tab)")
            == [
                KI("ctrl", down),
                KI("c"),
                KI("v"),
                KI("ctrl", up),
                KI("alt", down),
                KI("tab"),
                KI("alt", up),
            ]
        )

    def test_upper(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(A+B)")

    def test_literal_plus(self, parse: ParseFn) -> None:
        """Plus is an uppercase so nope."""
        with pytest.raises(SendParseError):
            parse("$(++lmb)")

    def test_literal_comma(self, parse: ParseFn) -> None:
        assert parse("$(a+,+b)") == [
            KI("a", down),
            KI(",", down),
            KI("b"),
            KI(",", up),
            KI("a", up),
        ]

    def test_literal_semicolon(self, parse: ParseFn) -> None:
        assert parse("$(a+b+;;c)") == [
            KI("a", down),
            KI("b", down),
            KI(";"),
            KI("b", up),
            KI("a", up),
            KI("c"),
        ]


class TestCombosWithOneProp:
    def test_prop_invalid(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a someprop)")

    def test_time_s(self, parse: ParseFn) -> None:
        assert (
            parse("$(f9 0.5s)")
            == parse("$(f9 .5s)")
            == [KI("f9"), SleepInstruction(0.5)]
        )

    def test_time_ms(self, parse: ParseFn) -> None:
        assert parse("$(1 1ms)") == [KI("1"), SleepInstruction(0.001)]

    def test_literal_space(self, parse: ParseFn) -> None:
        assert parse("$(  123s)") == [KI(" "), SleepInstruction(123)]

    def test_time_in_chain(self, parse: ParseFn) -> None:
        assert parse("$(a 50ms+b)") == [
            KI("a", down),
            SleepInstruction(0.05),
            KI("b"),
            KI("a", up),
        ]

    def test_invalid_time(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a -1s)")
        with pytest.raises(SendParseError):
            parse("$(a -123ms)")

    def test_mult(self, parse: ParseFn) -> None:
        assert parse("$(lmb 4x)") == [KI("lmb")] * 4

    def test_invalid_mult(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a 0x)")
        with pytest.raises(SendParseError):
            parse("$(b -2x)")

    def test_mult_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(shift 2x+q)")

    def test_mult_chain_end(self, parse: ParseFn) -> None:
        assert parse("$(shift+lmb 2x)") == [shift_down, KI("lmb"), KI("lmb"), shift_up]

    def test_dir_simplest(self, parse: ParseFn) -> None:
        assert parse("$(a down)") == [KI("a", down)]

    def test_dir_chain(self, parse: ParseFn) -> None:
        assert parse("$(a+b up)") == [KI("a", down), KI("b", up), KI("a", up)]

    def test_dir_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(1 down+2)")

    def test_dir_on(self, parse: ParseFn) -> None:
        assert parse("$(caps on)") == [KI("caps", on)]

    def test_dir_off(self, parse: ParseFn) -> None:
        assert parse("$(j off)") == [KI("j", off)]

    def test_dir_on_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(caps on+q)")


class TestCombosWithManyProps:
    def test_time_mult(self, parse: ParseFn) -> None:
        assert parse("$(g 50ms 5x)") == [KI("g"), SleepInstruction(0.05)] * 5

    def test_mult_time(self, parse: ParseFn) -> None:
        assert parse("$(v+clear 2x 1s)") == [
            KI("v", down),
            KI("clear"),
            KI("clear"),
            SleepInstruction(1),
            KI("v", up),
        ]

    def test_time_dir(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a+b 1s down)")

    def test_dir_time(self, parse: ParseFn) -> None:
        assert parse("$(a+b down 1s)") == [
            KI("a", down),
            KI("b", down),
            SleepInstruction(1),
            KI("a", up),
        ]

    def test_mult_dir(self, parse: ParseFn) -> None:
        assert parse("$(esc 7x down)") == datastructs.to_flat_list(
            [[KI("esc")] * 6, KI("esc", down)]
        )

    def test_dir_mult(self, parse: ParseFn) -> None:
        assert parse("$(esc down 3x)") == [KI("esc", down)] * 3

    def test_off_mult(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(caps off 4x)")
