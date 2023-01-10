import os.path
import re
import sys
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Union

import numpy
import numpy as np
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
        None,
        str,
        tuple[str, tuple[int, int, int, int]],
        tuple[ndarray, tuple[int, int, int, int]],
        tuple[ndarray, None],
        ndarray,
    ]
) -> tuple[ndarray | None, tuple[int, int, int, int] | None]:
    if data_in is None:
        return None, None
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


def get_screenshot_if_none_and_cut(
    maybe_image: ndarray | None, bbox: tuple[int, int, int, int] | None
) -> ndarray:
    if maybe_image is not None:
        if bbox:
            return maybe_image[bbox[1] : bbox[3], bbox[0] : bbox[2]]
        return maybe_image
    sct = PIL.ImageGrab.grab(bbox=bbox, all_screens=True).convert("RGB")
    return numpy.asarray(sct)


def _find_in_image(
    inner_image_bbox: tuple[ndarray, tuple[int, int, int, int] | None],
    outer: ndarray | None = None,
    precision: float = 1.0,
) -> tuple[int, int] | None:
    image_arr, bbox = inner_image_bbox
    x_start, y_start = get_start_coords(outer, bbox)
    outer = get_screenshot_if_none_and_cut(outer, bbox)
    result = image_fuzz.find(outer, image_arr, precision)

    if result is None:
        return None
    return x_start + result[0], y_start + result[1]


def get_start_coords(
    outer: ndarray | None,
    bbox_or_coords: tuple[int, int, int, int] | tuple[int, int] | None,
) -> tuple[int, int]:
    if bbox_or_coords:
        return bbox_or_coords[0], bbox_or_coords[1]
    screenshot_required = outer is None
    if screenshot_required and sys.platform == constants.OS.win32:
        return win32_coords_start()
    return 0, 0


def win32_coords_start() -> tuple[int, int]:
    """Win32 may start with negative coords when multiscreen."""
    import winput
    from win32api import GetSystemMetrics

    winput.set_DPI_aware(per_monitor=True)
    x = GetSystemMetrics(76)
    y = GetSystemMetrics(77)
    return x, y


snip_start_coords: tuple[int, int] | None = None


def _toggle_snip(
    prefix: str | None = None,
    bbox_in_name: bool = True,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
    picture_callback: Callable[[ndarray], Any] | None = None,
) -> None:
    global snip_start_coords
    if not snip_start_coords:
        start_snip()
    else:
        stop_coords = tapper.mouse.get_pos()
        x1 = min(snip_start_coords[0], stop_coords[0])
        x2 = max(snip_start_coords[0], stop_coords[0])
        y1 = min(snip_start_coords[1], stop_coords[1])
        y2 = max(snip_start_coords[1], stop_coords[1])
        finish_snip_with_callback(
            prefix, bbox_in_name, (x1, y1, x2, y2), bbox_callback, picture_callback
        )
        snip_start_coords = None


def start_snip() -> None:
    global snip_start_coords
    snip_start_coords = tapper.mouse.get_pos()


def finish_snip_with_callback(
    prefix: str | None = None,
    bbox_in_name: bool = True,
    bbox: tuple[int, int, int, int] | None = None,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
    picture_callback: Callable[[ndarray], Any] | None = None,
) -> None:
    nd_sct, bbox = _finish_snip(prefix, bbox, bbox_in_name)
    if bbox_callback:
        bbox_callback(*bbox)
    if picture_callback:
        picture_callback(nd_sct)


def _finish_snip(
    prefix: str | None = None,
    bbox: tuple[int, int, int, int] | None = None,
    bbox_in_name: bool = True,
) -> tuple[ndarray, tuple[int, int, int, int]]:
    sct = PIL.ImageGrab.grab(bbox=bbox, all_screens=True)
    if prefix is not None:
        save_to_disk(sct, prefix, bbox, bbox_in_name)
    return numpy.asarray(sct.convert("RGB")), bbox  # type: ignore


def save_to_disk(
    sct: PIL.Image.Image,
    prefix: str,
    bbox: tuple[int, int, int, int] | None,
    bbox_in_name: bool,
) -> None:
    bbox_str = (
        f"-(BBOX_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]})"
        if bbox and bbox_in_name
        else ""
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


coords_to_bbox_1_pixel = lambda coords: (
    coords[0],
    coords[1],
    coords[0] + 1,
    coords[1] + 1,
)


def _get_pixel_color(
    coords: tuple[int, int], outer: str | ndarray | None
) -> tuple[int, int, int]:
    outer, _ = _normalize(outer)  # type: ignore
    bbox = coords_to_bbox_1_pixel(coords)
    outer = get_screenshot_if_none_and_cut(outer, bbox)
    return outer[0][0]


def _pixel_str(coords: tuple[int, int], outer: str | ndarray | None) -> str:
    color = _get_pixel_color(coords, outer)
    return f"({color[0]}, {color[1]}, {color[2]}), ({coords[0]}, {coords[1]})"


def _pixel_find(
    color: tuple[int, int, int],
    bbox_or_coords: tuple[int, int, int, int] | tuple[int, int] | None,
    outer: ndarray | None,
    variation: int,
) -> tuple[int, int] | None:
    start_x, start_y = get_start_coords(outer, bbox_or_coords)

    bbox: tuple[int, int, int, int] | None = None
    if isinstance(bbox_or_coords, tuple):
        if len(bbox_or_coords) == 2:
            bbox = coords_to_bbox_1_pixel(bbox_or_coords)
        elif len(bbox_or_coords) == 4:
            bbox = bbox_or_coords  # type: ignore

    outer = get_screenshot_if_none_and_cut(outer, bbox)
    min_mask = color[0] - variation, color[1] - variation, color[2] - variation
    max_mask = color[0] + variation, color[1] + variation, color[2] + variation
    if variation == 0:
        matching_px = np.array(np.where(outer == color))
    else:
        matching_px = np.array(np.where(outer >= min_mask))
        matching_px = np.array(np.where(matching_px <= max_mask))

    if matching_px.size > 0:
        first_match = matching_px[:, 0]
        x = start_x + first_match[0]
        y = start_y + first_match[1]
        return x, y
    return None
