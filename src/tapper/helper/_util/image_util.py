import os.path
import re
import sys
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Union

import mss
import numpy as np
import PIL.Image
import PIL.ImageGrab
import tapper
from mss.base import MSSBase
from numpy import ndarray
from tapper.helper._util import image_fuzz
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePathT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import PixelColorT
from tapper.helper.model_types import XyCoordsT
from tapper.model import constants

_bbox_pattern = re.compile(r"\(BBOX_-?\d+_-?\d+_-?\d+_-?\d+\)")

mss_instance: MSSBase


def get_mss() -> MSSBase:
    global mss_instance
    mss_instance = mss.mss()
    return mss_instance


@lru_cache(maxsize=5)
def from_path(pathlike: ImagePathT) -> ImagePixelMatrixT:
    if isinstance(pathlike, str):
        pathlike = os.path.abspath(pathlike)
    pil_img = PIL.Image.open(pathlike).convert("RGB")
    return np.asarray(pil_img)


def get_image_size(image: ImagePixelMatrixT) -> tuple[int, int]:
    return image.shape[1], image.shape[0]


def to_pixel_matrix(image: ImageT | None) -> ImagePixelMatrixT | None:
    if image is None:
        return None
    elif isinstance(image, ndarray):
        return image
    elif isinstance(image, (str, bytes, os.PathLike)):
        return from_path(os.path.abspath(image))
    else:
        raise TypeError(f"Unexpected type, {type(image)} of {image}")


def normalize(
    data_in: Union[
        None,
        ImageT,
        tuple[ImageT, BboxT],
        tuple[ImageT, None],
    ]
) -> tuple[ImagePixelMatrixT | None, BboxT | None]:
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
        return from_path(data_in), bbox
    raise TypeError(f"Unexpected type {type(data_in)} of {data_in!r}")


def get_screenshot_if_none_and_cut(
    maybe_image: ImagePixelMatrixT | None, bbox: BboxT | None
) -> ImagePixelMatrixT:
    if maybe_image is not None:
        if bbox:
            return maybe_image[bbox[1] : bbox[3], bbox[0] : bbox[2]]
        return maybe_image
    if bbox is not None:
        try:
            sct = get_mss().grab(bbox)
        except Exception as e:
            raise e
    else:
        sct = get_mss().grab(get_mss().monitors[0])
    pil_rgb = PIL.Image.frombytes("RGB", sct.size, sct.bgra, "raw", "BGRX")
    return np.asarray(pil_rgb)


def find_in_image_raw(
    inner_image_bbox: tuple[ndarray, BboxT | None],
    outer: ImagePixelMatrixT | None = None,
) -> tuple[float, XyCoordsT]:
    image_arr, bbox = inner_image_bbox
    x_start, y_start = get_start_coords(outer, bbox)
    outer = get_screenshot_if_none_and_cut(outer, bbox)
    confidence, coords = image_fuzz.find(outer, image_arr)

    return confidence, (x_start + coords[0], y_start + coords[1])


def check_bbox_smaller_or_eq(image: ImagePixelMatrixT, bbox: BboxT | None) -> None:
    if image is None or bbox is None:
        return
    bbox_x = abs(bbox[2] - bbox[0])
    bbox_y = abs(bbox[3] - bbox[1])
    image_x, image_y = get_image_size(image)
    if bbox_x > image_x or bbox_y > image_y:
        raise ValueError(
            f"Bbox should NOT be bigger, but got {bbox_x}x{bbox_y} vs image {image_x}x{image_y}"
        )


def check_bbox_bigger_or_eq(image: ImagePixelMatrixT, bbox: BboxT | None) -> None:
    if image is None or bbox is None:
        return
    bbox_x = abs(bbox[2] - bbox[0])
    bbox_y = abs(bbox[3] - bbox[1])
    image_x, image_y = get_image_size(image)
    if bbox_x < image_x or bbox_y < image_y:
        raise ValueError(
            f"Bbox should NOT be smaller, but got {bbox_x}x{bbox_y} vs image {image_x}x{image_y}"
        )


def find(
    target: ImageT,
    bbox: tuple[int, int, int, int] | None,
    outer: ImageT | None = None,
    precision: float = 1.0,
) -> XyCoordsT | None:
    if target is None:
        raise ValueError("image_find nees something to search for.")
    target_image = to_pixel_matrix(target)
    assert target_image is not None  # for mypy
    check_bbox_bigger_or_eq(target_image, bbox)

    outer_image = to_pixel_matrix(outer)
    check_bbox_smaller_or_eq(outer_image, bbox)
    outer_certain = get_screenshot_if_none_and_cut(outer_image, bbox)

    confidence, coords = image_fuzz.find(outer_certain, target_image)
    if confidence < precision:
        return None
    target_x, target_y = get_image_size(target_image)
    x_start, y_start = get_start_coords(outer_image, bbox)
    return x_start + coords[0] + target_x // 2, y_start + coords[1] + target_y // 2


def find_in_image(
    target: ImagePixelMatrixT,
    bbox: BboxT | None,
    outer: ndarray | None = None,
    precision: float = 1.0,
) -> tuple[int, int] | None:
    x_start, y_start = get_start_coords(outer, bbox)
    outer = get_screenshot_if_none_and_cut(outer, bbox)
    confidence, coords = image_fuzz.find(outer, target)

    if confidence < precision:
        return None
    return x_start + coords[0], y_start + coords[1]


def get_start_coords(
    outer: ndarray | None,
    bbox_or_coords: BboxT | XyCoordsT | None,
) -> XyCoordsT:
    if bbox_or_coords is not None:
        return bbox_or_coords[0], bbox_or_coords[1]
    screenshot_required = outer is None
    if screenshot_required and sys.platform == constants.OS.win32:
        return win32_coords_start()
    return 0, 0


def win32_coords_start() -> XyCoordsT:
    """Win32 may start with negative coords when multiscreen."""
    import winput
    from win32api import GetSystemMetrics

    winput.set_DPI_aware(per_monitor=True)
    x = GetSystemMetrics(76)
    y = GetSystemMetrics(77)
    return x, y


snip_start_coords: XyCoordsT | None = None


def toggle_snip(
    prefix: str | None = None,
    bbox_to_name: bool = True,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
    picture_callback: Callable[[ImagePixelMatrixT], Any] | None = None,
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
            prefix, bbox_to_name, (x1, y1, x2, y2), bbox_callback, picture_callback
        )
        snip_start_coords = None


def start_snip() -> None:
    global snip_start_coords
    snip_start_coords = tapper.mouse.get_pos()


def finish_snip_with_callback(
    prefix: str | None = None,
    bbox_to_name: bool = True,
    bbox: BboxT | None = None,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
    picture_callback: Callable[[ImagePixelMatrixT], Any] | None = None,
) -> None:
    nd_sct, bbox = finish_snip(prefix, bbox, bbox_to_name)
    if bbox and bbox_callback:
        bbox_callback(*bbox)
    if picture_callback:
        picture_callback(nd_sct)


def finish_snip(
    prefix: str | None = None,
    bbox: BboxT | None = None,
    bbox_to_name: bool = True,
) -> tuple[ImagePixelMatrixT, BboxT | None]:
    sct = get_screenshot_if_none_and_cut(None, bbox)
    if prefix is not None:
        save_to_disk(sct, prefix, bbox, bbox_to_name)
    return sct, bbox


def save_to_disk(
    sct: ImagePixelMatrixT,
    prefix: str,
    bbox: BboxT | None,
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
                break
    PIL.Image.fromarray(sct).save(full_name, "PNG")


coords_to_bbox_1_pixel = lambda coords: (
    coords[0],
    coords[1],
    coords[0] + 1,
    coords[1] + 1,
)


def get_pixel_color(coords: XyCoordsT, outer: ImageT | None) -> PixelColorT:
    outer_image = to_pixel_matrix(outer)
    bbox = coords_to_bbox_1_pixel(coords)
    outer_certain = get_screenshot_if_none_and_cut(outer_image, bbox)
    nd_pixel = outer_certain[0][0]
    return tuple(c for c in nd_pixel)  # type: ignore


def pixel_str(coords: XyCoordsT, outer: ImageT | None) -> str:
    color = get_pixel_color(coords, outer)
    return f"({color[0]}, {color[1]}, {color[2]}), ({coords[0]}, {coords[1]})"


px_eq = (
    lambda im, color: (im[:, :, 0] == color[0])
    & (im[:, :, 1] == color[1])
    & (im[:, :, 2] == color[2])
)
px_between = lambda im, min_mask, max_mask: (
    (max_mask[0] >= im[:, :, 0])
    & (im[:, :, 0] >= min_mask[0])
    & (max_mask[1] >= im[:, :, 1])
    & (im[:, :, 1] >= min_mask[1])
    & (max_mask[2] >= im[:, :, 2])
    & (im[:, :, 2] >= min_mask[2])
)


def pixel_find(
    color: PixelColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    outer: ndarray | None,
    variation: int,
) -> XyCoordsT | None:
    start_x, start_y = get_start_coords(outer, bbox_or_coords)

    bbox: BboxT | None = None
    if isinstance(bbox_or_coords, tuple):
        if len(bbox_or_coords) == 2:
            bbox = coords_to_bbox_1_pixel(bbox_or_coords)
        elif len(bbox_or_coords) == 4:
            bbox = bbox_or_coords  # type: ignore

    outer = get_screenshot_if_none_and_cut(outer, bbox)
    if variation == 0:
        matching_px = np.argwhere(px_eq(outer, color))
    else:
        min_mask = color[0] - variation, color[1] - variation, color[2] - variation
        max_mask = color[0] + variation, color[1] + variation, color[2] + variation
        matching_px = np.argwhere(px_between(outer, min_mask, max_mask))
    if matching_px.size > 0:
        first_match = matching_px[0]
        x = start_x + first_match[1]
        y = start_y + first_match[0]
        return x, y
    return None
