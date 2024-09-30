from unittest.mock import MagicMock
from unittest.mock import patch

import img_test_util
import pytest
from tapper.helper import img

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0, 0, 0
white = 255, 255, 255
gray = 128, 128, 128

absolutes = img_test_util.absolutes()


@pytest.fixture
def mock_get_sct() -> MagicMock:
    with patch(
        "tapper.helper._util.image.base.get_screenshot_if_none_and_cut"
    ) as mock_sct:
        yield mock_sct


@pytest.fixture
def mock_mouse_pos() -> MagicMock:
    with patch("tapper.mouse.get_pos") as mock_mouse_get_pos:
        yield mock_mouse_get_pos


class TestPixelGetColor:
    def test_simplest(self) -> None:
        color = img.pixel_get_color((2, 0), outer=absolutes)
        assert color == blue

    def test_hexagonal(self) -> None:
        color = img.pixel_get_color_hex((0, 0), outer=absolutes)
        assert color == "#ff0000"

    def test_from_sct(self, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        color = img.pixel_get_color((2, 4))
        # as sct is "cut" at 2, 4, first pixel is assumed, which is red(0, 0) not white(actual 2,4)
        assert color == red


class TestPixelInfo:
    def test_simplest(self, mock_get_sct, mock_mouse_pos) -> None:
        mock_get_sct.return_value = absolutes
        mock_mouse_pos.return_value = 0, 0
        pixel_data = "_"

        def fill_px_data(rgb, xy) -> None:
            nonlocal pixel_data
            pixel_data = rgb, xy

        img.pixel_info(callback_for_data=fill_px_data)()

        assert pixel_data == (red, (0, 0))

    def test_str(self, mock_get_sct, mock_mouse_pos) -> None:
        mock_get_sct.return_value = absolutes
        mock_mouse_pos.return_value = 1, 2
        pixel_str = "_"

        def fill_px_str(px: str) -> None:
            nonlocal pixel_str
            pixel_str = px

        img.pixel_info(
            callback_for_str=fill_px_str,
            str_format="({r}, {g}, {b}), ({x}, {y}) | x{{{x}}}y{{{y}}} | {hex}",
        )()

        assert pixel_str == "(255, 0, 0), (1, 2) | x{1}y{2} | #ff0000"


class TestFind:
    def test_simplest(self) -> None:
        xy = img.pixel_find(green, outer=absolutes)
        assert xy == (0, 1)

    def test_not_found(self) -> None:
        xy = img.pixel_find(gray, outer=absolutes)
        assert xy is None

    def test_precise_not_found__approximate_found(self) -> None:
        almost_blue = 0, 8, 240
        xy = img.pixel_find(almost_blue, outer=absolutes)
        assert xy is None
        xy = img.pixel_find(almost_blue, outer=absolutes, variation=20)
        assert xy == (0, 2)

    def test_pixel_color_out_of_bounds(self) -> None:
        with pytest.raises(ValueError):
            img.pixel_find((1000, -200, 0))


class TestWaitFor:
    def test_simplest(self, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        xy = img.pixel_wait_for(green)
        assert xy == (0, 1)

    def test_not_found(self, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        xy = img.pixel_wait_for(gray, timeout=0.001, interval=0.001)
        assert xy is None
