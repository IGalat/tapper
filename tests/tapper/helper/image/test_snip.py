import os
import random
import shutil
from pathlib import Path
from string import ascii_uppercase
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import patch

import img_test_util
import numpy
import pytest
from tapper.helper import img

absolutes = img_test_util.absolutes()


@pytest.fixture
def mock_get_sct() -> MagicMock:
    with patch(
        "tapper.helper._util.image.base.get_screenshot_if_none_and_cut"
    ) as mock_sct:
        yield mock_sct


@pytest.fixture
def temp_dir(tmpdir_factory) -> Path:
    temp_name = "".join(random.choice(ascii_uppercase) for i in range(12))
    my_tmpdir = tmpdir_factory.mktemp(temp_name)
    yield my_tmpdir
    shutil.rmtree(str(my_tmpdir))


@pytest.fixture
def mock_save_to_disk() -> MagicMock:
    with patch("tapper.helper._util.image.base.save_to_disk") as mock_save:
        yield mock_save


@pytest.fixture
def mock_mouse_pos() -> MagicMock:
    with patch("tapper.mouse.get_pos") as mock_mouse_get_pos:
        yield mock_mouse_get_pos


class TestSnip:
    def test_simplest(self, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        snipped = img.get_snip(None)
        assert numpy.array_equal(snipped, absolutes)

    def test_saved_image_same_as_on_disk(self, temp_dir, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        get_name = lambda name: str(Path(temp_dir / name))
        img.get_snip(bbox=None, prefix=get_name("qwe"))
        on_disk = img.from_path(get_name("qwe.png"), cache=False)
        assert numpy.array_equal(on_disk, absolutes)

    def test_bbox_to_name(self, mock_get_sct, mock_save_to_disk) -> None:
        mock_get_sct.return_value = absolutes
        img.get_snip(bbox=(0, 0, 20, 20), prefix="qwe", bbox_to_name=True)
        assert mock_save_to_disk.call_count == 1
        assert mock_save_to_disk.call_args == call(absolutes, "qwe-BBOX(0,0,20,20).png")

    def test_no_override_creates_different_file(self, temp_dir, mock_get_sct) -> None:
        mock_get_sct.return_value = absolutes
        get_name = lambda name: str(Path(temp_dir / name))
        img.get_snip(bbox=None, prefix=get_name("qwe"))
        on_disk_0 = img.from_path(get_name("qwe.png"), cache=False)
        img.get_snip(bbox=None, prefix=get_name("qwe"), override_existing=False)
        on_disk_1 = img.from_path(get_name("qwe(1).png"), cache=False)
        assert numpy.array_equal(on_disk_0, on_disk_1)
        assert not os.path.exists(get_name("qwe(2).png"))

    def test_override(self, temp_dir, mock_get_sct) -> None:
        get_name = lambda name: str(Path(temp_dir / name))
        mock_get_sct.return_value = absolutes
        img.get_snip(bbox=None, prefix=get_name("qwe"))
        on_disk_0 = img.from_path(get_name("qwe.png"), cache=False)

        mock_get_sct.return_value = img_test_util.btn_yellow()
        img.get_snip(bbox=None, prefix=get_name("qwe"), override_existing=True)
        on_disk_1 = img.from_path(get_name("qwe.png"), cache=False)
        assert not os.path.exists(get_name("qwe(1).png"))
        assert len([name for name in os.listdir(temp_dir)]) == 1
        assert numpy.array_equal(on_disk_0, absolutes)
        assert numpy.array_equal(on_disk_1, img_test_util.btn_yellow())

    def test_bbox_is_correct(
        self, mock_get_sct, mock_save_to_disk, mock_mouse_pos
    ) -> None:
        snip_fn = img.snip()
        mock_mouse_pos.return_value = 100, 450
        snip_fn()
        mock_mouse_pos.return_value = 300, 0
        snip_fn()
        assert mock_get_sct.call_args == call(None, (100, 0, 300, 450))
