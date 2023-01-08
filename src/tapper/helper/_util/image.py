import os.path
import re
import sys
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Union

import numpy
import PIL.Image
import PIL.ImageGrab
import tapper
from numpy import ndarray
from tapper.helper._util import image_fuzz
from tapper.model import constants

_bbox_pattern = re.compile(r"\(BBOX_-?\d+_-?\d+_-?\d+_-?\d+\)")


@lru_cache
def from_path(pathlike: str) -> ndarray:
    pil_img = PIL.Image.open(pathlike).convert("RGB")
    return numpy.asarray(pil_img)


def _normalize(
    data_in: Union[
        str,
        tuple[str, tuple[int, int, int, int]],
        tuple[ndarray, tuple[int, int, int, int]],
        tuple[ndarray, None],
    ]
) -> tuple[ndarray, tuple[int, int, int, int] | None]:
    bbox = None
    if isinstance(data_in, tuple):
        data_in, bbox = data_in  # type: ignore
    if isinstance(data_in, ndarray):  # type: ignore
        return data_in, bbox  # type: ignore
    if isinstance(data_in, str):
        if not bbox and (str_bbox := _bbox_pattern.search(data_in)):
            sx = str_bbox.group().split("_")
            bbox = int(sx[1]), int(sx[2]), int(sx[3]), int(sx[4].rstrip(")"))
        return from_path(os.path.abspath(data_in)), bbox
    raise TypeError(f"Unexpected type, {type(data_in)} of {data_in}")


def _find_on_screen(
    image_bbox: tuple[ndarray, tuple[int, int, int, int] | None], precision: float = 1.0
) -> tuple[int, int] | None:
    image_arr, bbox = image_bbox
    sct = PIL.ImageGrab.grab(bbox=bbox, all_screens=True).convert("RGB")
    sct_arr = numpy.array(sct)
    result = image_fuzz.find(sct_arr, image_arr, precision)

    if result is None:
        return None
    if sys.platform == constants.OS.win32:
        return win32_multiscreen_normalize(result)
    else:
        return result


def precise_find(haystack: ndarray, needle: ndarray) -> tuple[int, int] | None:
    haystack_size = len(haystack[0])
    needle_size = len(needle[0])

    haystack_bytes = haystack.tobytes()
    needle_bytes = needle.tobytes()

    gap_size = (haystack_size - needle_size) * 3
    gap_regex = ("(?s).{" + str(gap_size) + "}").encode("utf-8")

    chunk_size = needle_size * 3
    split = [
        needle_bytes[i : i + chunk_size]
        for i in range(0, len(needle_bytes), chunk_size)
    ]

    regex = gap_regex.join([re.escape(s) for s in split])
    p = re.compile(regex)
    m = p.search(haystack_bytes)

    if not m:
        return None

    x, _ = m.span()

    left = x % (haystack_size * 3) / 3
    top = x / haystack_size / 3

    return int(left), int(top)


def win32_multiscreen_normalize(coords: tuple[int, int]) -> tuple[int, int]:
    """Win32 may have negative coords when multiscreen."""
    import winput
    from win32api import GetSystemMetrics

    winput.set_DPI_aware(per_monitor=True)
    min_x = GetSystemMetrics(76)
    min_y = GetSystemMetrics(77)
    return coords[0] + min_x, coords[1] + min_y


snip_start_coords: tuple[int, int] | None = None


def _toggle_snip(
    prefix: str,
    bbox_in_name: bool,
    bbox_callback: Callable[[int, int, int, int], Any] | None,
    picture_callback: Callable[[PIL.Image.Image], Any] | None = None,
) -> None:
    if not snip_start_coords:
        start_snip()
    else:
        stop_snip(prefix, bbox_in_name, bbox_callback, picture_callback)


def start_snip() -> None:
    global snip_start_coords
    snip_start_coords = tapper.mouse.get_pos()


def stop_snip(
    prefix: str,
    bbox_in_name: bool,
    bbox_callback: Callable[[int, int, int, int], Any] | None,
    picture_callback: Callable[[PIL.Image.Image], Any] | None = None,
) -> None:
    global snip_start_coords
    if not snip_start_coords:
        return
    stop_coords = tapper.mouse.get_pos()
    x1 = min(snip_start_coords[0], stop_coords[0])
    x2 = max(snip_start_coords[0], stop_coords[0])
    y1 = min(snip_start_coords[1], stop_coords[1])
    y2 = max(snip_start_coords[1], stop_coords[1])
    bbox = (x1, y1, x2, y2)
    sct = PIL.ImageGrab.grab(bbox=bbox, all_screens=True)
    if prefix is not None:
        bbox_str = (
            f"-(BBOX_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]})" if bbox_in_name else ""
        )
        ending = bbox_str + ".png"
        full_name = ""
        if not os.path.exists(prefix + ending):
            full_name = prefix + ending
        else:
            for i in range(1, 100):
                potential_name = prefix + f"({i})" + ending
                if not os.path.exists(potential_name):
                    full_name = potential_name
        sct.save(full_name, "PNG")
    if bbox_callback:
        bbox_callback(*bbox)
    if picture_callback:
        picture_callback(sct)
    snip_start_coords = None
