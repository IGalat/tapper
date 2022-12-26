from typing import Callable

import pytest
from tapper.boot import initializer
from tapper.model import constants
from tapper.model.errors import SendParseError
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.parser.send_parser import default_shift
from tapper.parser.send_parser import ki_shift_down
from tapper.parser.send_parser import ki_shift_up
from tapper.parser.send_parser import SendParser
from tapper.util import datastructs

down = constants.KeyDir.DOWN
up = constants.KeyDir.UP
click = constants.KeyDir.CLICK
on = constants.KeyDir.ON
off = constants.KeyDir.OFF

KI = KeyInstruction

ParseFn = Callable[[str], list[SendInstruction]]


@pytest.fixture(scope="module")
def parse() -> ParseFn:
    return initializer.default_send_parser().parse


@pytest.fixture(scope="module")
def parser() -> SendParser:
    return initializer.default_send_parser()


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
        assert parse("Q") == [ki_shift_down(), KI("q"), ki_shift_up()]

    def test_shift_multi(self, parse: ParseFn) -> None:
        assert parse("P%I") == [
            ki_shift_down(),
            *key_ins("p5i"),
            ki_shift_up(),
        ]

    def test_shift_mixed(self, parse: ParseFn) -> None:
        assert parse("2007 Ahoy!") == [
            *key_ins("2007"),
            KI("space"),
            ki_shift_down(),
            KI("a"),
            ki_shift_up(),
            *key_ins("hoy"),
            ki_shift_down(),
            KI("1"),
            ki_shift_up(),
        ]

    def test_control_chars(self, parse: ParseFn) -> None:
        assert parse("\n\t ") == [
            KI("enter"),
            KI("tab"),
            KI("space"),
        ]


class TestSimplestCombosAndMix:
    def test_simplest(self, parse: ParseFn) -> None:
        assert parse("$(a)") == [KI("a")]

    def test_simplest_mouse_wheel(self, parse: ParseFn) -> None:
        assert parse("$(wheel_left)") == [WheelInstruction("scroll_wheel_left")]

    def test_unregistered_symbol_combo(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(qwerty)")

    def test_combo_surrounded(self, parse: ParseFn) -> None:
        assert parse("\n$(f5)q") == key_ins(["enter", "f5", "q"])

    def test_combo_after_text(self, parse: ParseFn) -> None:
        assert parse("Hi\n$(ctrl+c,v down)") == [
            ki_shift_down(),
            KI("h"),
            ki_shift_up(),
            KI("i"),
            KI("enter"),
            KI("left_control", down),
            KI("c"),
            KI("v", down),
            KI("left_control", up),
        ]

    def test_two_combos(self, parse: ParseFn) -> None:
        assert parse("$(ctrl)$(page_up)") == [
            KI("left_control"),
            KI("page_up"),
        ]

    def test_combos_mix(self, parse: ParseFn) -> None:
        assert parse("$(caps)bc$(lshift)$(esc)f") == key_ins(
            ["caps_lock", "b", "c", "left_shift", "escape", "f"]
        )

    def test_empty_combo_is_not_combo(self, parse: ParseFn) -> None:
        assert parse("$()") == [ki_shift_down(), *key_ins("490"), ki_shift_up()]

    def test_sleep_s(self, parse: ParseFn) -> None:
        assert parse("$(2s)") == [SleepInstruction(2)]

    def test_sleep_ms(self, parse: ParseFn) -> None:
        assert parse("$(1234ms)") == [SleepInstruction(1.234)]


class TestCombosWithoutProps:
    def test_simplest(self, parse: ParseFn) -> None:
        assert parse("$(alt+q)") == [KI("left_alt", down), KI("q"), KI("left_alt", up)]

    def test_long_combo(self, parse: ParseFn) -> None:
        assert parse("$(q+w+e+r+\t)") == [
            KI("q", down),
            KI("w", down),
            KI("e", down),
            KI("r", down),
            KI("tab"),
            KI("r", up),
            KI("e", up),
            KI("w", up),
            KI("q", up),
        ]

    def test_comma(self, parse: ParseFn) -> None:
        assert parse("$(ctrl+a,c,v)") == [
            KI("left_control", down),
            KI("a"),
            KI("c"),
            KI("v"),
            KI("left_control", up),
        ]

    def test_semicolon(self, parse: ParseFn) -> None:
        assert (
            parse("$(ctrl+c,v;alt+tab)")
            == parse("$(ctrl+c,v)$(alt+tab)")
            == [
                KI("left_control", down),
                KI("c"),
                KI("v"),
                KI("left_control", up),
                KI("left_alt", down),
                KI("tab"),
                KI("left_alt", up),
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

    def test_mouse_move(self, parse: ParseFn) -> None:
        assert parse("$(x340y980)") == [CursorMoveInstruction(xy=(340, 980))]


class TestCombosWithOneProp:
    def test_prop_invalid(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a someprop)")

    def test_time_s(self, parse: ParseFn) -> None:
        assert (
            parse("$(f9 0.5s)")
            == parse("$(f9 .5s)")
            == [KI("f9", down), SleepInstruction(0.5), KI("f9", up)]
        )

    def test_time_ms(self, parse: ParseFn) -> None:
        assert parse("$(1 1ms)") == [
            KI("1", down),
            SleepInstruction(0.001),
            KI("1", up),
        ]

    def test_literal_space(self, parse: ParseFn) -> None:
        assert parse("$(  123s)") == [
            KI("space", down),
            SleepInstruction(123),
            KI("space", up),
        ]

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
        assert parse("$(lmb 4x)") == [KI("left_mouse_button")] * 4

    def test_invalid_mult(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(a 0x)")
        with pytest.raises(SendParseError):
            parse("$(b -2x)")

    def test_mult_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(shift 2x+q)")

    def test_mult_chain_end(self, parse: ParseFn) -> None:
        assert parse("$(shift+lmb 2x)") == [
            ki_shift_down(),
            KI("left_mouse_button"),
            KI("left_mouse_button"),
            ki_shift_up(),
        ]

    def test_dir_simplest(self, parse: ParseFn) -> None:
        assert parse("$(a down)") == [KI("a", down)]

    def test_dir_chain(self, parse: ParseFn) -> None:
        assert parse("$(a+b up)") == [KI("a", down), KI("b", up), KI("a", up)]

    def test_dir_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(1 down+2)")

    def test_dir_on(self, parse: ParseFn) -> None:
        assert parse("$(caps on)") == [KI("caps_lock", on)]

    def test_dir_off(self, parse: ParseFn) -> None:
        assert parse("$(j off)") == [KI("j", off)]

    def test_dir_on_in_chain(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(caps on+q)")


class TestCombosWithManyProps:
    def test_time_mult(self, parse: ParseFn) -> None:
        assert (
            parse("$(g 50ms 5x)")
            == [KI("g", down), SleepInstruction(0.05), KI("g", up)] * 5
        )

    def test_mult_time(self, parse: ParseFn) -> None:
        assert parse("$(v+clear 2x 1s)") == [
            KI("v", down),
            KI("clear", down),
            KI("clear", down),
            SleepInstruction(1),
            KI("clear", up),
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
            [[KI("escape")] * 6, KI("escape", down)]
        )

    def test_dir_mult(self, parse: ParseFn) -> None:
        assert parse("$(esc down 3x)") == [KI("escape", down)] * 3

    def test_off_mult(self, parse: ParseFn) -> None:
        with pytest.raises(SendParseError):
            parse("$(caps off 4x)")


class TestShiftIn:
    def test_no_chars(self, parser: SendParser) -> None:
        assert parser.parse("$(esc)", default_shift) == [KI("escape", click)]

    def test_simplest(self, parser: SendParser) -> None:
        assert parser.parse("a", default_shift) == [
            ki_shift_up(),
            KI("a", click),
            ki_shift_down(),
        ]

    def test_uppercase(self, parser: SendParser) -> None:
        assert parser.parse("!", default_shift) == [KI("1", click)]

    def test_mixed_chars_non_chars(self, parser: SendParser) -> None:
        assert parser.parse("y\no", default_shift) == [
            ki_shift_up(),
            KI("y", click),
            KI("enter", click),
            KI("o", click),
            ki_shift_down(),
        ]

    def test_mixed_case(self, parser: SendParser) -> None:
        assert parser.parse("Hi", default_shift) == [
            KI("h", click),
            ki_shift_up(),
            KI("i", click),
            ki_shift_down(),
        ]

    def test_different_shift(self, parser: SendParser) -> None:
        rshift = "right_shift"
        assert parser.parse("u", rshift) == [
            KI(rshift, up),
            KI("u", click),
            KI(rshift, down),
        ]
