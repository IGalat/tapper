import time
from dataclasses import dataclass
from unittest.mock import patch

from tapper.helper import repeat


@dataclass
class Counter:
    count: int = 0

    def tick(self) -> None:
        self.count += 1


class TestRepeatWhileFn:
    def test_simplest(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 1, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 1

    def test_several_times(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: counter.count < 5, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 5

    def test_zero_times(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: False, counter.tick, interval=0)()
        time.sleep(0.001)

        assert counter.count == 0

    def test_max_repeats(self) -> None:
        counter = Counter()
        repeat.while_fn(lambda: True, counter.tick, interval=0, max_repeats=5)()
        time.sleep(0.001)

        assert counter.count == 5

    def test_second_repeat(self) -> None:
        counter1 = Counter()
        counter2 = Counter()
        repeat.while_fn(lambda: True, counter1.tick, interval=0.005)()
        time.sleep(0.001)
        repeat.while_fn(lambda: counter2.count < 5, counter2.tick, interval=0)()
        time.sleep(
            0.01
        )  # if not given enough time, wait for 1st will be longer since switch is not instant.

        assert counter1.count == 1
        assert counter2.count == 5


class TestRepeatWhilePressed:
    def test_simplest(self) -> None:
        with patch("tapper.kb.pressed") as mock_pressed:
            counter = Counter()
            mock_pressed.return_value = True
            repeat.while_pressed("q", counter.tick, interval=0.02)()
            time.sleep(0.05)
            mock_pressed.return_value = False
            assert counter.count == 3

    # def test_press_and_release(self) -> None:
    #     with patch("tapper.kb.pressed") as mock_pressed, patch("time.sleep") as mock_sleep:
    #         counter = Counter()
    #         mock_pressed.return_value = True
    #         repeat.while_pressed("q", counter.tick)()
    #         while mock_sleep.call_count < 2:
    #         time.sleep(0.05)
    #         mock_pressed.return_value = False
    #         time.sleep(0.03)
    #         mock_pressed.return_value = True
    #         time.sleep(0.03)
    #         assert counter.count == 3
