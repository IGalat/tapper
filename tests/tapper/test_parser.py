from typing import Callable

import pytest
from tapper import parser
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.errors import TriggerParseError
from tapper.model.trigger import AuxiliaryKey
from tapper.model.trigger import MainKey
from tapper.model.trigger import Trigger

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
        assert parse("a") == Trigger(MainKey(["a"]))

    def test_non_registered_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("qwerasdf")

    def test_with_alias(self, parse: ParseFn) -> None:
        assert parse("mmb") == Trigger(MainKey(["middle_mouse_button"]))

    def test_combo_with_aliases(self, parse: ParseFn) -> None:
        assert parse("esc+scroll_up") == Trigger(
            MainKey(["scroll_wheel_up"]), [AuxiliaryKey(["escape"])]
        )

    def test_combo_with_nothing(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("1+")
        with pytest.raises(TriggerParseError):
            parse("+home")

    def test_alias_points_to_many(self, parse: ParseFn) -> None:
        assert parse("control") == Trigger(MainKey(ctrl_list))

    def test_alias_with_modifier(self, parse: ParseFn) -> None:
        assert parse("alt+f1") == Trigger(MainKey(["f1"]), [AuxiliaryKey(alt_list)])

    def test_uppercase(self, parse: ParseFn) -> None:
        assert parse("R") == Trigger(MainKey(["r"]), [AuxiliaryKey(shift_list)])

    def test_many_modifiers(self, parse: ParseFn) -> None:
        assert parse("ctrl+lalt+right_shift+scroll_down") == Trigger(
            MainKey(["scroll_wheel_down"]),
            [
                AuxiliaryKey(ctrl_list),
                AuxiliaryKey(["left_alt"]),
                AuxiliaryKey(["right_shift"]),
            ],
        )

    def test_shift_and_uppercase(self, parse: ParseFn) -> None:
        assert parse("shift+A") == Trigger(MainKey(["a"]), [AuxiliaryKey(shift_list)])
        assert parse("shift+A") == parse("A")

    def test_concrete_shift_and_uppercase(self, parse: ParseFn) -> None:
        assert parse("lshift+)") == Trigger(
            MainKey(["0"]), [AuxiliaryKey(["left_shift"])]
        )

    def test_one_aux_many_main(self, parse: ParseFn) -> None:
        assert parse("clear+ctrl") == Trigger(
            MainKey(shift_list), [AuxiliaryKey(["clear"])]
        )

    def test_control_symbols(self, parse: ParseFn) -> None:
        assert parse("\t+\n") == Trigger(MainKey(["enter"]), [AuxiliaryKey(["tab"])])

    def test_space(self, parse: ParseFn) -> None:
        assert parse(" ") == Trigger(MainKey(["space"]))

    def test_plus(self, parse: ParseFn) -> None:
        assert parse("1++") == Trigger(
            MainKey(["="]),
            [AuxiliaryKey(["1"]), AuxiliaryKey(shift_list)],
        )
        assert parse("++-") == Trigger(
            MainKey(["-"]),
            [AuxiliaryKey(["="]), AuxiliaryKey(shift_list)],
        )

    def test_same_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("+++")
        with pytest.raises(TriggerParseError):
            parse(" +space")

    def test_two_capital_letters(self, parse: ParseFn) -> None:
        assert parse("A+B") == Trigger(
            MainKey(["b"]),
            [AuxiliaryKey(["a"]), AuxiliaryKey(shift_list)],
        )

    def test_space_and_plus(self, parse: ParseFn) -> None:
        assert parse("++ ") == Trigger(
            MainKey(["space"]),
            [AuxiliaryKey(["="]), AuxiliaryKey(shift_list)],
        )
        assert parse(" ++") == Trigger(
            MainKey(["="]),
            [AuxiliaryKey(["space"]), AuxiliaryKey(shift_list)],
        )

    def test_up_simplest(self, parse: ParseFn) -> None:
        assert parse("num0 up") == Trigger(
            MainKey(["num0"], direction=constants.KEY_DIR.UP)
        )

    def test_up_with_modifier(self, parse: ParseFn) -> None:
        assert parse("\\+] up") == Trigger(
            MainKey(["]"], direction=constants.KEY_DIR.UP),
            [AuxiliaryKey(["\\"])],
        )

    def test_time_simplest(self, parse: ParseFn) -> None:
        assert (
            parse("space 0.5s")
            == parse("space 500ms")
            == Trigger(MainKey(["space"], time=0.5))
        )

    def test_time_with_aux(self, parse: ParseFn) -> None:
        assert parse("ctrl+a 1s") == Trigger(
            MainKey(["a"], time=1),
            [AuxiliaryKey(ctrl_list)],
        )

    def test_time_on_aux(self, parse: ParseFn) -> None:
        assert parse("f3 300ms+\n") == Trigger(
            MainKey(["enter"]),
            [AuxiliaryKey(["f3"], time=0.3)],
        )

    def test_time_main_and_aux(self, parse: ParseFn) -> None:
        assert parse("num_lock 1s+del 300ms") == Trigger(
            MainKey(["delete"], time=0.3),
            [AuxiliaryKey(["num_lock"], time=1)],
        )

    def test_up_time(self, parse: ParseFn) -> None:
        assert parse("q 2s up") == Trigger(
            MainKey(["q"], time=2, direction=constants.KEY_DIR.UP)
        )

    def test_up_time_with_mod_time(self, parse: ParseFn) -> None:
        assert parse("alt 1s+esc 350ms up") == Trigger(
            MainKey(["escape"], time=0.35, direction=constants.KEY_DIR.UP),
            [AuxiliaryKey(alt_list, time=1)],
        )

    def test_up_time_different_order(self, parse: ParseFn) -> None:
        assert parse("g up 1s") == Trigger(
            MainKey(["g"], time=1, direction=constants.KEY_DIR.UP)
        )
