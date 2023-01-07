import os.path
import re
import time
from functools import lru_cache
from typing import Any
from typing import Union

import numpy
import PIL.Image
import PIL.ImageGrab
from numpy import dtype
from numpy import ndarray
from tapper.helper._util import image_fuzz

_bbox_pattern = re.compile(r"\(BBOX_-?\d+_-?\d+_-?\d+_-?\d+\)")

ndArray = ndarray[Any, dtype[Any]]


@lru_cache
def from_path(pathlike: str) -> ndArray:
    pil_img = PIL.Image.open(pathlike).convert("RGB")
    return numpy.asarray(pil_img)


def _normalize(
    data_in: Union[
        str,
        tuple[str, tuple[int, int, int, int]],
        tuple[ndArray, tuple[int, int, int, int]],
        tuple[ndArray, None],
    ]
) -> tuple[ndArray, tuple[int, int, int, int] | None]:
    bbox = None
    if isinstance(data_in, tuple):
        data_in, bbox = data_in  # type: ignore
    if isinstance(data_in, ndarray):  # type: ignore
        return data_in, bbox  # type: ignore
    if isinstance(data_in, str):
        if not bbox and (str_bbox := _bbox_pattern.match(data_in)):
            sx = str_bbox.group().split("_")
            bbox = int(sx[1]), int(sx[2]), int(sx[3]), int(sx[4].rstrip(")"))
        return from_path(os.path.abspath(data_in)), bbox
    raise TypeError(f"Unexpected type, {type(data_in)} of {data_in}")


def _find_on_screen(
    image_bbox: tuple[ndArray, tuple[int, int, int, int] | None], precision: float = 1.0
) -> tuple[int, int] | None:
    image, bbox = image_bbox
    sct = PIL.ImageGrab.grab(bbox=bbox, all_screens=True).convert("RGB")
    if precision == 1.0:
        return subimg_location(sct, PIL.Image.fromarray(image))
    else:
        return image_fuzz.find(numpy.array(sct), image, precision)


def subimg_location(haystack, needle) -> tuple[int, int] | None:
    start = time.perf_counter()
    haystack = haystack.convert("RGB")
    needle = needle.convert("RGB")

    haystack_str = haystack.tobytes()
    needle_str = needle.tobytes()

    gap_size = (haystack.size[0] - needle.size[0]) * 3
    gap_regex = "(?s).{" + str(gap_size) + "}"
    gap_regex = gap_regex.encode("utf-8")

    # Split b into needle.size[0] chunks
    chunk_size = needle.size[0] * 3
    split = [
        needle_str[i : i + chunk_size] for i in range(0, len(needle_str), chunk_size)
    ]

    # Build regex
    regex = re.escape(split[0])
    for i in range(1, len(split)):
        regex += gap_regex + re.escape(split[i])

    p = re.compile(regex)
    m = p.search(haystack_str)

    if not m:
        return None

    x, _ = m.span()

    left = x % (haystack.size[0] * 3) / 3
    top = x / haystack.size[0] / 3

    return (left, top)
