import re
import time
from collections.abc import Callable
from typing import Any

import numpy as np

import tapper
from tapper.helper._util.image import base
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import PixelColorT
from tapper.helper.model_types import PixelHexColorT
from tapper.helper.model_types import PixelStrFormatT
from tapper.helper.model_types import XyCoordsT


def coords_to_bbox_1_pixel(coords: XyCoordsT) -> BboxT:
    return coords[0], coords[1], coords[0] + 1, coords[1] + 1


HEX_COLOR = re.compile(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})")


def hex_or_rgb_to_rgb(color: PixelColorT | PixelHexColorT) -> PixelColorT:
    if isinstance(color, str):
        if not (match := HEX_COLOR.fullmatch(color)):
            raise ValueError(f"Color {color!r} must look like '#RRGGBB'.")
        r, g, b = (int(channel, 16) for channel in match.groups())
    else:
        r, g, b = color
    if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
        return r, g, b
    else:
        raise ValueError(f"Color {color} is out of range.")


def rgb_to_hex(r: int, g: int, b: int) -> PixelHexColorT:
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


def get_first_match_coords(
    image: ImagePixelMatrixT, color: PixelColorT, variation: int
) -> XyCoordsT | None:
    """First match in row-major order: top row first, left to right."""
    # uint8 subtraction wraps around, so widen before taking the difference
    close = np.abs(image.astype(np.int16) - color) <= variation
    matching_px = np.argwhere(close.all(axis=2))
    if matching_px.size == 0:
        return None
    y, x = matching_px[0]
    return int(x), int(y)


def to_bbox(bbox_or_coords: BboxT | XyCoordsT | None) -> BboxT | None:
    if bbox_or_coords is None:
        return None
    if len(bbox_or_coords) == 2:
        return coords_to_bbox_1_pixel(bbox_or_coords)
    return bbox_or_coords


def find(
    color_in: PixelColorT | PixelHexColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    return_absolute_coords: bool,
    outer_maybe: ImageT | None,
    variation: int,
) -> XyCoordsT | None:
    start_x, start_y = base.get_start_coords(outer_maybe, bbox_or_coords)
    color = hex_or_rgb_to_rgb(color_in)

    bbox = to_bbox(bbox_or_coords)
    outer = base.get_screenshot_if_none_and_cut(base.to_pixel_matrix(outer_maybe), bbox)
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


def pixel_get_with_best_match_color(
    color_in: PixelColorT | PixelHexColorT,
    bbox_or_coords: BboxT | XyCoordsT | None,
    outer_maybe: ImageT | None,
    max_variation: int,
    within_radius: tuple[XyCoordsT, int] | None = None,
) -> tuple[XyCoordsT, PixelColorT] | None:
    """The pixel whose color is closest to the one asked for, and that color.
    Closest means the smallest largest-channel difference, the same measure `variation` uses;
    ties go to the first pixel in reading order. None if even the best is off by more than
    max_variation. within_radius limits the search to a circle (center, radius) in absolute coords.
    """
    color = hex_or_rgb_to_rgb(color_in)
    bbox = to_bbox(bbox_or_coords)
    start_x, start_y = base.get_start_coords(outer_maybe, bbox)
    outer = base.get_screenshot_if_none_and_cut(base.to_pixel_matrix(outer_maybe), bbox)

    # uint8 subtraction wraps around, so widen before taking the difference
    distance = np.abs(outer.astype(np.int16) - color).max(axis=2)
    if within_radius is not None:
        (center_x, center_y), radius = within_radius
        rows, cols = np.ogrid[: distance.shape[0], : distance.shape[1]]
        outside = (cols + start_x - center_x) ** 2 + (
            rows + start_y - center_y
        ) ** 2 > radius**2
        distance[outside] = 256
    y, x = np.unravel_index(int(distance.argmin()), distance.shape)
    if distance[y, x] > max_variation:
        return None
    r, g, b = outer[y, x]
    return (start_x + int(x), start_y + int(y)), (int(r), int(g), int(b))


def pixel_get_with_best_match_color_near(
    color_in: PixelColorT | PixelHexColorT,
    xy_position: XyCoordsT,
    max_distance: int,
    outer_maybe: ImageT | None,
    max_variation: int,
) -> tuple[XyCoordsT, PixelColorT] | None:
    x, y = xy_position
    square = (
        x - max_distance,
        y - max_distance,
        x + max_distance + 1,
        y + max_distance + 1,
    )
    bbox = base.clamp_bbox(square, base.to_pixel_matrix(outer_maybe))
    return pixel_get_with_best_match_color(
        color_in, bbox, outer_maybe, max_variation, (xy_position, max_distance)
    )
