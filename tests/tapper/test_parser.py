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
        assert parse("a") == Trigger(main=MainKey(["a"]))

    def test_non_registered_symbol(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("qwerasdf")

    def test_with_alias(self, parse: ParseFn) -> None:
        assert parse("mmb") == Trigger(main=MainKey(["middle_mouse_button"]))

    def test_combo_with_aliases(self, parse: ParseFn) -> None:
        assert parse("esc+scroll_up") == Trigger(
            main=MainKey(["scroll_wheel_up"]), aux=[AuxiliaryKey(["escape"])]
        )

    def test_combo_with_nothing(self, parse: ParseFn) -> None:
        with pytest.raises(TriggerParseError):
            parse("1+")
        with pytest.raises(TriggerParseError):
            parse("+home")

    def test_alias_points_to_many(self, parse: ParseFn) -> None:
        assert parse("control") == Trigger(main=MainKey(ctrl_list))

    def test_alias_with_modifier(self, parse: ParseFn) -> None:
        assert parse("alt+f1") == Trigger(
            main=MainKey(["f1"]), aux=[AuxiliaryKey(alt_list)]
        )

    def test_uppercase(self, parse: ParseFn) -> None:
        assert parse("R") == Trigger(
            main=MainKey(["r"]), aux=[AuxiliaryKey(shift_list)]
        )

    def test_many_modifiers(self, parse: ParseFn) -> None:
        assert parse("ctrl+lalt+right_shift+scroll_down") == Trigger(
            main=MainKey(["scroll_wheel_down"]),
            aux=[
                AuxiliaryKey(ctrl_list),
                AuxiliaryKey(["left_alt"]),
                AuxiliaryKey(["right_shift"]),
            ],
        )

    def test_shift_and_uppercase(self, parse: ParseFn) -> None:
        assert parse("shift+A") == Trigger(
            main=MainKey(["a"]), aux=[AuxiliaryKey(shift_list)]
        )
        assert parse("shift+A") == parse("A")

    def test_one_aux_many_main(self, parse: ParseFn) -> None:
        assert parse("clear+ctrl") == Trigger(
            main=MainKey(shift_list), aux=[AuxiliaryKey(["clear"])]
        )

    def test_control_symbols(self, parse: ParseFn) -> None:
        assert parse("\t+\n") == Trigger(
            main=MainKey(["enter"]), aux=[AuxiliaryKey(["tab"])]
        )

    def test_space(self, parse: ParseFn) -> None:
        assert parse(" ") == Trigger(main=MainKey(["space"]))

    def test_plus(self, parse: ParseFn) -> None:
        assert parse("1++") == Trigger(
            main=MainKey(["="]),
            aux=[AuxiliaryKey(["1"]), AuxiliaryKey(shift_list)],
        )
        assert parse("++-") == Trigger(
            main=MainKey(["-"]),
            aux=[AuxiliaryKey(["="]), AuxiliaryKey(shift_list)],
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
            main=MainKey(["b"]),
            aux=[AuxiliaryKey(["a"]), AuxiliaryKey(shift_list)],
        )

    def test_space_and_plus(self, parse: ParseFn) -> None:
        assert parse("++ ") == Trigger(
            main=MainKey(["space"]),
            aux=[AuxiliaryKey(["="]), AuxiliaryKey(shift_list)],
        )
        assert parse(" ++") == Trigger(
            main=MainKey(["="]),
            aux=[AuxiliaryKey(["space"]), AuxiliaryKey(shift_list)],
        )

    def test_up_simplest(self, parse: ParseFn) -> None:
        assert parse("num0 up") == Trigger(
            main=MainKey(["num0"], direction=constants.KEY_DIR.UP)
        )

    def test_up_with_modifier(self, parse: ParseFn) -> None:
        assert parse("\\+] up") == Trigger(
            main=MainKey(["]"], direction=constants.KEY_DIR.UP),
            aux=[AuxiliaryKey(["\\"])],
        )

    def test_time_simplest(self, parse: ParseFn) -> None:
        assert (
            parse("space 0.5s")
            == parse("space 500ms")
            == Trigger(main=MainKey(["space"], time=0.5))
        )

    def test_time_with_aux(self, parse: ParseFn) -> None:
        assert parse("ctrl+a 1s") == Trigger(
            main=MainKey(["a"], time=1),
            aux=[AuxiliaryKey(ctrl_list)],
        )

    def test_time_on_aux(self, parse: ParseFn) -> None:
        assert parse("f3 300ms+\n") == Trigger(
            main=MainKey(["enter"]),
            aux=[AuxiliaryKey(["f3"], time=0.3)],
        )

    def test_time_main_and_aux(self, parse: ParseFn) -> None:
        assert parse("num_lock 1s+del 300ms") == Trigger(
            main=MainKey(["delete"], time=0.3),
            aux=[AuxiliaryKey(["num_lock"], time=1)],
        )

    def test_up_time(self, parse: ParseFn) -> None:
        assert parse("q 2s up") == Trigger(
            main=MainKey(["q"], time=2, direction=constants.KEY_DIR.UP)
        )

    def test_up_time_with_mod_time(self, parse: ParseFn) -> None:
        assert parse("alt 1s+esc 350ms up") == Trigger(
            main=MainKey(["escape"], time=0.35, direction=constants.KEY_DIR.UP),
            aux=[AuxiliaryKey(alt_list, time=1)],
        )

    def test_up_time_different_order(self, parse: ParseFn) -> None:
        assert parse("g up 1s") == Trigger(
            main=MainKey(["g"], time=1, direction=constants.KEY_DIR.UP)
        )
