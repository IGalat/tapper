import img_test_util
from tapper.helper import img

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0, 0, 0
white = 255, 255, 255
gray = 128, 128, 128

absolutes = img_test_util.absolutes()


class TestFind:
    def test_simplest(self) -> None:
        xy = img.pixel_find(green, outer=absolutes)
        assert xy == (1, 0)

    def test_not_found(self) -> None:
        pass

    def test_precise_not_found__approximate_found(self) -> None:
        pass

    def test_pixel_color_out_of_bounds(self) -> None:
        pass


class TestPixelStr:
    def test_simplest(self) -> None:
        pass

    def test_hexagonal(self) -> None:
        pass
