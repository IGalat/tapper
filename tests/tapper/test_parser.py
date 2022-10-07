from typing import Callable

import pytest
from tapper import parser
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.errors import TriggerParseError
from tapper.model.trigger import Trigger
from tapper.model.trigger import TriggerKey

shift_list = keyboard.aliases["shift"]
alt_list = keyboard.aliases["alt"]
ctrl_list = keyboard.aliases["ctrl"]


@pytest.mark.xfail
class TestTriggerParser:
    ParseFn = Callable[[str], Trigger]

    @pytest.fixture(scope="class")
    def parse(self) -> ParseFn:
        return parser.TriggerParser([keyboard.get_keys(), mouse.get_keys()]).parse

    def test_register_existing_symbol(self) -> None:
        with pytest.raises(ValueError):
            parser.TriggerParser([keyboard.get_keys(), {"a": ["a"]}])

    def test_one_symbol_simplest(self, parse: ParseFn) -> None:
        assert parse("a") == Trigger.from_simple(main=["a"])

    def test_non_registered_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("qwerasdf")

    def test_with_alias(self, parse: ParseFn) -> None:
        assert parse("mmb") == Trigger.from_simple(main=["middle_mouse_button"])

    def test_combo_with_aliases(self, parse: ParseFn) -> None:
        assert parse("esc+scroll_up") == Trigger.from_simple(
            main=["escape"], aux=["scroll_wheel_up"]
        )

    def test_combo_with_nothing(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("1+")
        with pytest.raises(TriggerParseError):
            parse("+home")

    def test_alias_points_to_many(self, parse: ParseFn) -> None:
        assert parse("control") == Trigger.from_simple(
            main=["left_control", "right_control", "virtual_control"]
        )

    def test_alias_with_modifier(self, parse: ParseFn) -> None:
        assert parse("alt+f1") == Trigger.from_simple(main=["f1"], aux=alt_list)

    def test_uppercase(self, parse: ParseFn) -> None:
        assert parse("R") == Trigger.from_simple(main=["r"], aux=shift_list)

    def test_many_modifiers(self, parse: ParseFn) -> None:
        assert parse("ctrl+lalt+right_shift+scroll_down") == Trigger(
            main=TriggerKey(["scroll_wheel_down"]),
            auxiliary=[
                TriggerKey(ctrl_list),
                TriggerKey(["left_alt"]),
                TriggerKey(["right_shift"]),
            ],
        )

    def test_shift_and_uppercase(self, parse: ParseFn) -> None:
        assert parse("shift+A") == Trigger.from_simple(main=["a"], aux=shift_list)
        assert parse("shift+A") == parse("A")

    def test_one_aux_many_main(self, parse: ParseFn) -> None:
        assert parse("clear+ctrl") == Trigger.from_simple(
            main=shift_list, aux=["clear"]
        )

    def test_control_symbols(self, parse: ParseFn) -> None:
        assert parse("\t+\n") == Trigger.from_simple(main=["enter"], aux=["tab"])

    def test_space(self, parse: ParseFn) -> None:
        assert parse(" ") == Trigger.from_simple(main=["space"])

    def test_plus(self, parse: ParseFn) -> None:
        assert parse("1++") == Trigger(
            main=TriggerKey(["="]),
            auxiliary=[TriggerKey(["1"]), TriggerKey(shift_list)],
        )
        assert parse("++-") == Trigger(
            main=TriggerKey(["-"]),
            auxiliary=[TriggerKey(["="]), TriggerKey(shift_list)],
        )

    def test_same_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("+++")
        with pytest.raises(TriggerParseError):
            parse("lshift+A")
        with pytest.raises(TriggerParseError):
            parse(" +space")

    def test_two_capital_letters(self, parse: ParseFn) -> None:
        assert parse("A+B") == Trigger(
            main=TriggerKey(["b"]),
            auxiliary=[TriggerKey(["a"]), TriggerKey(shift_list)],
        )

    def test_space_and_plus(self, parse: ParseFn) -> None:
        assert parse("++ ") == Trigger(
            main=TriggerKey(["space"]),
            auxiliary=[TriggerKey(["="]), TriggerKey(shift_list)],
        )
        assert parse(" ++") == Trigger(
            main=TriggerKey(["="]),
            auxiliary=[TriggerKey(["space"]), TriggerKey(shift_list)],
        )

    def test_up_simplest(self, parse: ParseFn) -> None:
        assert parse("num0 up") == Trigger(
            main=TriggerKey(["num0"]), main_direction=constants.KEY_DIR.UP
        )

    def test_up_with_modifier(self, parse: ParseFn) -> None:
        assert parse("\\+] up") == Trigger(
            main=TriggerKey(["]"]),
            auxiliary=[TriggerKey(["\\"])],
            main_direction=constants.KEY_DIR.UP,
        )

    def test_time_simplest(self, parse: ParseFn) -> None:
        assert (
            parse("space 0.5s")
            == parse("space 500ms")
            == Trigger(main=TriggerKey(["space"], time=0.5))
        )

    def test_time_with_aux(self, parse: ParseFn) -> None:
        assert parse("ctrl+a 1s") == Trigger(
            main=TriggerKey(["a"], time=1),
            auxiliary=[TriggerKey(ctrl_list)],
        )

    def test_time_on_aux(self, parse: ParseFn) -> None:
        assert parse("f3 300ms+\n") == Trigger(
            main=TriggerKey(["enter"]),
            auxiliary=[TriggerKey(["f3"], time=0.3)],
        )

    def test_time_main_and_aux(self, parse: ParseFn) -> None:
        assert parse("num_lock 1s+del 300ms") == Trigger(
            main=TriggerKey(["delete"], time=0.3),
            auxiliary=[TriggerKey(["num_lock"], time=1)],
        )

    def test_up_time(self, parse: ParseFn) -> None:
        assert parse("q 2s up") == Trigger(
            main=TriggerKey(["q"], time=2), main_direction=constants.KEY_DIR.UP
        )

    def test_up_time_with_mod_time(self, parse: ParseFn) -> None:
        assert parse("alt 1s+esc 350ms up") == Trigger(
            main=TriggerKey(["escape"], time=0.35),
            main_direction=constants.KEY_DIR.UP,
            auxiliary=[TriggerKey(alt_list, time=1)],
        )

    def test_up_time_different_order(self, parse: ParseFn) -> None:
        assert parse("g up 1s") == Trigger(
            main=TriggerKey(["g"], time=1), main_direction=constants.KEY_DIR.UP
        )
