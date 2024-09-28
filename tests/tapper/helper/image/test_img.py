import img_for_test
from tapper.helper import img

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
black = 0, 0, 0
white = 255, 255, 255
gray = 128, 128, 128

absolutes = img_for_test.absolutes()


class TestFind:
    def test_simplest(self) -> None:
        xy = img.find(img_for_test.from_matrix([[blue]]), outer=absolutes)
        assert xy == (2, 0)

    def test_target_is_path(self) -> None:
        pic_path = img_for_test.get_image_path("absolutes.png")
        xy = img.find(img_for_test.from_matrix([[green]]), outer=pic_path)
        assert xy == (1, 0)

    def test_corner_case_black_not_found(self) -> None:
        """This is technically a bug of tapper, but caused by openCV
        algorithm that's searching. All-black picture will not be found.
        This is corner case where all target pixels are same, in which case
        user should do pixel_find instead."""
        xy = img.find(img_for_test.from_matrix([[black]]), outer=absolutes)
        assert xy is None

    def test_corner_case_gray_is_white(self) -> None:
        """This is technically a bug of tapper, but caused by openCV
        algorithm that's searching. Picture of gray pixel is found
        on white pixel, with 100% match.
        This is corner case where all target pixels are same, in which case
        user should do pixel_find instead."""
        xy = img.find(img_for_test.from_matrix([[gray]]), outer=absolutes)
        assert xy == (0, 4)

    def test_dependencies_not_installed(self) -> None:
        pass

    def test_with_bbox(self) -> None:
        xy = img.find(img_for_test.from_matrix([[white]]), (2, 2, 3, 5), absolutes)
        assert xy == (2, 4)

    def test_not_found(self) -> None:
        xy = img.find(img_for_test.from_matrix([[(100, 150, 50)]]), outer=absolutes)
        assert xy is None

    def test_bbox_larger_than_outer(self) -> None:
        # with pytest.raises(ValueError):
        #     img.find(img_for_test.from_matrix([[green]]), (0, 0, 100, 100), absolutes)
        pass

    def test_target_larger_than_outer(self) -> None:
        pass

    def test_screenshot_not_outer(self) -> None:
        pass


class TestFindFuzz:
    def test_precise_not_found__approximate_found(self) -> None:
        pass

    def test_several_similar_targets(self) -> None:
        pass


class TestSnip:
    def test_simplest(self) -> None:
        pass

    def test_saved_image_same_as_on_disk(self) -> None:
        pass
