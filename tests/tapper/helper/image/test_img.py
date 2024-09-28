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

btn_red_xy = 60, 60
btn_yellow_xy = 310, 60
btn_blue_xy = 310, 180
btn_pink_xy = 310, 305


class TestFind:
    def test_simplest(self) -> None:
        xy = img.find(img_test_util.from_matrix([[blue]]), outer=absolutes)
        assert xy == (2, 0)

    def test_target_is_path(self) -> None:
        pic_path = img_test_util.get_image_path("absolutes.png")
        xy = img.find(img_test_util.from_matrix([[green]]), outer=pic_path)
        assert xy == (1, 0)

    def test_corner_case_black_not_found(self) -> None:
        """This is technically a bug in tapper, but caused by openCV
        algorithm that's searching. All-black picture will not be found.
        This is corner case where all target pixels are same, in which case
        user should do pixel_find instead."""
        xy = img.find(img_test_util.from_matrix([[black]]), outer=absolutes)
        assert xy is None

    def test_corner_case_gray_is_white(self) -> None:
        """This is technically a bug in tapper, but caused by openCV
        algorithm that's searching. Picture of gray pixel is found
        on white pixel, with 100% match.
        This is corner case where all target pixels are same, in which case
        user should do pixel_find instead."""
        xy = img.find(img_test_util.from_matrix([[gray]]), outer=absolutes)
        assert xy == (0, 4)

    def test_dependencies_not_installed(self) -> None:
        pass

    def test_with_bbox(self) -> None:
        xy = img.find(img_test_util.from_matrix([[white]]), (2, 2, 3, 5), absolutes)
        assert xy == (2, 4)

    def test_not_found(self) -> None:
        xy = img.find(img_test_util.from_matrix([[(100, 150, 50)]]), outer=absolutes)
        assert xy is None

    def test_bbox_larger_than_outer(self) -> None:
        with pytest.raises(ValueError):
            img.find(img_test_util.from_matrix([[green]]), (0, 0, 5, 3), absolutes)

    def test_bbox_smaller_than_target(self) -> None:
        with pytest.raises(ValueError):
            img.find(absolutes, (0, 0, 2, 2), absolutes)

    def test_target_larger_than_outer(self) -> None:
        with pytest.raises(ValueError):
            img.find(absolutes, (0, 0, 1, 1), img_test_util.from_matrix([[black]]))

    def test_screenshot_not_outer(self) -> None:
        """Touches internals to simulate taking screenshot."""
        sct = img_test_util.btn_all()
        with patch(
            "tapper.helper._util.image_util" ".get_screenshot_if_none_and_cut"
        ) as mock_get_sct:
            mock_get_sct.return_value = sct
            xy = img.find(img_test_util.btn_red(), precision=0.999)
            assert xy == pytest.approx(btn_red_xy, abs=10)

    def test_target_wrong_type(self) -> None:
        with pytest.raises(TypeError):
            img.find(1)  # noqa


class TestFindFuzz:
    def test_precise_find(self) -> None:
        xy = img.find(
            img_test_util.btn_yellow(), outer=img_test_util.btn_all(), precision=0.999
        )
        assert xy == pytest.approx(btn_yellow_xy, abs=10)

    def test_precise_not_found__approximate_found(self) -> None:
        target = img_test_util.get_picture("btn_red_less_bright.png")
        xy = img.find(target, outer=img_test_util.btn_all(), precision=0.999)
        assert xy is None
        xy = img.find(target, outer=img_test_util.btn_all(), precision=0.95)
        assert xy == pytest.approx(btn_red_xy, abs=10)

    def test_several_similar_targets(self) -> None:
        target = img_test_util.get_picture("btn_blue_changed.png")
        xy = img.find(target, outer=img_test_util.btn_all(), precision=0.95)
        assert xy == pytest.approx(btn_blue_xy, abs=10)
        xy = img.find(  # exclude third column with actual blue button
            target, bbox=(0, 0, 250, 361), outer=img_test_util.btn_all(), precision=0.95
        )
        assert xy is not None

    def test_jpg(self) -> None:
        target_jpg = img_test_util.get_picture("btn_pink.jpg")
        xy_jpg = img.find(target_jpg, outer=img_test_util.btn_all(), precision=0.98)
        xy_png = img.find(
            img_test_util.btn_pink(), outer=img_test_util.btn_all(), precision=0.98
        )
        assert xy_jpg == xy_png == pytest.approx(btn_pink_xy, abs=10)


class TestSnip:
    def test_simplest(self) -> None:
        pass

    def test_saved_image_same_as_on_disk(self) -> None:
        pass
