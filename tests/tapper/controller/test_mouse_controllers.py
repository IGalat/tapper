from functools import partial

from tapper.controller.mouse.mouse_api import calc_move
from tapper.controller.mouse.mouse_api import MouseController
from tapper.model import constants
from tapper.state import keeper
from testutil_model import Dummy


class TestMouseController:
    def test_wheel_calc(self) -> None:
        def get_pos() -> tuple[int, int]:
            return 200, 200

        c_move = partial(calc_move, get_pos)

        assert c_move(500, 500, False) == (500, 500)
        assert c_move(None, 100, False) == (200, 100)
        assert c_move(100, None, False) == (100, 200)

        assert c_move(10, 10, True) == (210, 210)
        assert c_move(-20, -20, True) == (180, 180)
        assert c_move(-20, None, True) == (180, 200)
        assert c_move(None, -20, True) == (200, 180)

    def test_tuple_move(self, dummy: Dummy) -> None:
        mouse_tc = dummy.MouseTC(dummy.Listener.get_for_os(""), [])

        mouse = MouseController()
        mouse._tracker = mouse_tc
        mouse._commander = mouse_tc
        mouse.move((1, 2))
        assert mouse_tc.x == 1
        assert mouse_tc.y == 2

    def test_click(self, dummy: Dummy) -> None:
        mouse_tc = dummy.MouseTC(dummy.Listener.get_for_os(""), [])
        mouse_tc.listener.on_signal = lambda x: True
        mouse = MouseController()
        mouse._tracker = mouse_tc
        mouse._commander = mouse_tc
        mouse._emul_keeper = keeper.Emul()

        mouse.click(1, 2)
        assert mouse_tc.x == 1
        assert mouse_tc.y == 2
        assert mouse_tc.all_signals == [
            ("left_mouse_button", constants.KeyDirBool.DOWN),
            ("left_mouse_button", constants.KeyDirBool.UP),
        ]

    def test_right_click(self, dummy: Dummy) -> None:
        mouse_tc = dummy.MouseTC(dummy.Listener.get_for_os(""), [])
        mouse_tc.listener.on_signal = lambda x: True
        mouse = MouseController()
        mouse._tracker = mouse_tc
        mouse._commander = mouse_tc
        mouse._emul_keeper = keeper.Emul()

        mouse.right_click(1, 2)
        assert mouse_tc.x == 1
        assert mouse_tc.y == 2
        assert mouse_tc.all_signals == [
            ("right_mouse_button", constants.KeyDirBool.DOWN),
            ("right_mouse_button", constants.KeyDirBool.UP),
        ]
