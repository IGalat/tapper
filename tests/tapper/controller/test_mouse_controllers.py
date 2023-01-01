from functools import partial

from tapper.controller.mouse.mouse_api import calc_move


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
