import sys

import pytest
from tapper.model import constants


@pytest.mark.skipif(sys.platform != constants.OS.win32, reason="")
class TestWin32MouseController:
    def test_wheel_calc(self) -> None:
        from tapper.controller.mouse.mouse_win32_winput_impl import (
            Win32MouseTrackerCommander,
        )

        mouse_tc = Win32MouseTrackerCommander()

        current_x, current_y = 200, 200

        mouse_tc.get_pos = lambda: (current_x, current_y)

        assert mouse_tc.calc_move(500, 500, False) == (500, 500)
        assert mouse_tc.calc_move(None, 100, False) == (200, 100)
        assert mouse_tc.calc_move(100, None, False) == (100, 200)

        assert mouse_tc.calc_move(10, 10, True) == (210, 210)
        assert mouse_tc.calc_move(-20, -20, True) == (180, 180)
        assert mouse_tc.calc_move(-20, None, True) == (180, 200)
        assert mouse_tc.calc_move(None, -20, True) == (200, 180)
