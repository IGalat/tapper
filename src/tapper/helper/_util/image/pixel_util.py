import time
from typing import Any
from typing import Callable

import numpy as np
import tapper
from PIL import ImageColor
from tapper.helper._util.image import base
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import PixelColorT
from tapper.helper.model_types import PixelHexColorT
from tapper.helper.model_types import PixelStrFormatT
from tapper.helper.model_types import XyCoordsT

coords_to_bbox_1_pixel = lambda coords: (
    coords[0],
    coords[1],
    coords[0] + 1,
    coords[1] + 1,
)


def hex_or_rgb_to_rgb(color: PixelColorT | PixelHexColorT) -> PixelColorT:
    if isinstance(color, str):
        result = ImageColor.getcolor(color, "RGB")
        r, g, b = result[0], result[1], result[2]  # type checkers
    else:
        r, g, b = color
    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
        return r, g, b
    else:
        raise ValueError(f"Color {color} is out of range.")


def rgb_to_hex(r: int, g: int, b: int) -> PixelHexColorT:
    if 0 > r > 255 or 0 > g > 255 or 0 > b > 255:
        raise ValueError(f"grb_to_hex: {r}, {g}, {b} should be 0-255.")
    return f"#{r:02x}{g:02x}{b:02x}"


def get_color(coords: XyCoordsT, outer: ImageT | None) -> PixelColorT:
    outer_image = base.to_pixel_matrix(outer)
    bbox = coords_to_bbox_1_pixel(coords)
    outer_certain = base.get_screenshot_if_none_and_cut(outer_image, bbox)
    nd_pixel = outer_certain[0][0]
    return (
        int(nd_pixel[0]),
        int(nd_pixel[1]),
        int(nd_pixel[2]),
    )  # made stupid enough for type checkers.


def get_color_hex(coords: XyCoordsT, outer: ImageT | None) -> PixelHexColorT:
    r, g, b = get_color(coords, outer)
    return rgb_to_hex(r, g, b)


def pixel_info(
    callback_for_str: Callable[[str], Any] | None,
    str_format: PixelStrFormatT,
    callback_for_data: Callable[[PixelColorT, XyCoordsT], Any] | None,
) -> None:
    x, y = tapper.mouse.get_pos()
    r, g, b = get_color((x, y), None)
    hex_ = rgb_to_hex(r, g, b)
    formatted = str_format.format(r=r, g=g, b=b, x=x, y=y, hex=hex_)
    if callback_for_str is not None:
        callback_for_str(formatted)
    if callback_for_data is not None:
        callback_for_data((r, g, b), (x, y))


def px_eq(im: ImagePixelMatrixT, color: PixelColorT) -> bool:
    return (
        (im[:, :, 0] == color[0])
        & (im[:, :, 1] == color[1])
        & (im[:, :, 2] == color[2])
    )


def get_first_match_coords(
    image: ImagePixelMatrixT, color: PixelColorT, variation: int
) -> XyCoordsT | None:
    """Probably horribly inefficient"""
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            px = image[i, j]
            if (
                abs(int(px[0]) - color[0]) <= variation
                and abs(int(px[1]) - color[1]) <= variation
                and abs(int(px[2]) - color[2]) <= variation
            ):
                return j, i  # transposed. why?
    return None


def find(
    color_in: PixelColorT | PixelHexColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    return_absolute_coords: bool,
    outer_maybe: ImageT | None,
    variation: int,
) -> XyCoordsT | None:
    start_x, start_y = base.get_start_coords(outer_maybe, bbox_or_coords)
    color = hex_or_rgb_to_rgb(color_in)

    bbox: BboxT | None = None
    if isinstance(bbox_or_coords, tuple):
        if len(bbox_or_coords) == 2:
            bbox = coords_to_bbox_1_pixel(bbox_or_coords)
        elif len(bbox_or_coords) == 4:
            bbox = bbox_or_coords  # type: ignore
    outer = base.get_screenshot_if_none_and_cut(outer_maybe, bbox)
    if variation == 0:
        matching_px = np.argwhere(px_eq(outer, color))
        if matching_px.size <= 0:
            return None
        first_match = matching_px[0]
        y = first_match[0]
        x = first_match[1]
        match = int(x), int(y)
    else:
        if (match := get_first_match_coords(outer, color, variation)) is None:
            return None

    if bbox is None or return_absolute_coords is False:
        return match
    else:
        x, y = match
        return start_x + x, start_y + y


def wait_for(
    color: PixelColorT | PixelHexColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    return_absolute_coords: bool,
    timeout: int | float,
    interval: float,
    variation: int,
) -> XyCoordsT | None:
    finish_time = time.perf_counter() + timeout
    while True:
        if found := find(
            color, bbox_or_coords, return_absolute_coords, None, variation=variation
        ):
            return found
        if time.perf_counter() > finish_time:
            return None
        tapper.sleep(interval)
        if time.perf_counter() > finish_time:
            return None


def wait_for_disappear(
    color: PixelColorT | PixelHexColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    timeout: int | float,
    interval: float,
    variation: int,
) -> bool:
    finish_time = time.perf_counter() + timeout
    while time.perf_counter() < finish_time:
        if not find(color, bbox_or_coords, False, None, variation=variation):
            return True
        tapper.sleep(interval)
    return False
