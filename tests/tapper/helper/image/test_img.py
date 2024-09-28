import img_for_test
from tapper.helper import img

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0, 0, 0
white = 255, 255, 255


class TestFind:
    def test_simplest(self) -> None:
        absolutes = img_for_test.absolutes()
        xy = img.find(img_for_test.from_matrix([[red]]), outer=absolutes)
        assert xy == (0, 0)
