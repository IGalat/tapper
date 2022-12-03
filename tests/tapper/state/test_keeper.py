import time

import pytest
from tapper.boot import initializer
from tapper.model import constants
from tapper.state.keeper import Emul
from tapper.state.keeper import Pressed


class TestEmul:
    @pytest.fixture
    def emul_keeper(self) -> Emul:
        return Emul()

    def test_simplest(self, emul_keeper: Emul) -> None:
        emul_keeper.will_emulate("a")
        assert emul_keeper.is_emulated("a")

    def test_twice_emul(self, emul_keeper: Emul) -> None:
        emul_keeper.will_emulate("a")
        emul_keeper.will_emulate("a")
        assert emul_keeper.is_emulated("a")
        assert not emul_keeper.is_emulated("a")

    def test_different_props(self, emul_keeper: Emul) -> None:
        emul_keeper.will_emulate("lmb", constants.KeyDirBool.UP)
        assert not emul_keeper.is_emulated("lmb", constants.KeyDirBool.DOWN)
        assert emul_keeper.is_emulated("lmb", constants.KeyDirBool.UP)

    def test_complex_props(self, emul_keeper: Emul) -> None:
        emul_keeper.will_emulate("move", 1920, 1080, False)
        assert not emul_keeper.is_emulated("move", 500, 700, False)
        assert emul_keeper.is_emulated("move", 1920, 1080, False)


class TestPressed:
    @pytest.fixture
    def pressed_keeper(self) -> Pressed:
        pressed = initializer.default_keeper_pressed()
        return pressed

    def test_simplest(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("a")
        state = pressed_keeper.get_state(time.perf_counter())
        assert len(state) == 1
        assert state["a"] < 0.001

    def test_nonexistent(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("no_such_symbol")
        state = pressed_keeper.get_state(time.perf_counter())
        assert len(state) == 0

    def test_press_and_release(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("a")
        pressed_keeper.key_released("a")
        state = pressed_keeper.get_state(time.perf_counter())
        assert len(state) == 0

    def test_double_press(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("a")
        after_first = time.perf_counter()
        state = pressed_keeper.get_state(after_first)
        pressed_keeper.key_pressed("a")
        state2 = pressed_keeper.get_state(after_first)
        assert state["a"] == state2["a"]

    def test_double_press_and_release(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("a")
        pressed_keeper.key_pressed("a")
        pressed_keeper.key_released("a")
        state = pressed_keeper.get_state(time.perf_counter())
        assert len(state) == 0

    def test_many_keys(self, pressed_keeper: Pressed) -> None:
        pressed_keeper.key_pressed("right_control")
        pressed_keeper.key_pressed("left_alt")
        pressed_keeper.key_pressed("left_shift")
        pressed_keeper.key_released("right_control")
        state = pressed_keeper.get_state(time.perf_counter())
        assert state["left_alt"]
        assert state["left_shift"]
