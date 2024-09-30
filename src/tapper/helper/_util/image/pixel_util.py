from typing import Any
from typing import Callable

import tapper
from tapper.helper._util.image import base
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


def get_pixel_color(coords: XyCoordsT, outer: ImageT | None) -> PixelColorT:
    outer_image = base.to_pixel_matrix(outer)
    bbox = coords_to_bbox_1_pixel(coords)
    outer_certain = base.get_screenshot_if_none_and_cut(outer_image, bbox)
    nd_pixel = outer_certain[0][0]
    return (
        int(nd_pixel[0]),
        int(nd_pixel[1]),
        int(nd_pixel[2]),
    )  # made stupid enough for type checkers.


def get_pixel_color_hex(coords: XyCoordsT, outer: ImageT | None) -> PixelHexColorT:
    r, g, b = get_pixel_color(coords, outer)
    return rgb_to_hex(r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> PixelHexColorT:
    if 0 > r > 255 or 0 > g > 255 or 0 > b > 255:
        raise ValueError(f"grb_to_hex: {r}, {g}, {b} should be 0-255.")
    return f"#{r:02x}{g:02x}{b:02x}"


def pixel_info(
    callback_for_str: Callable[[str], Any] | None,
    str_format: PixelStrFormatT,
    callback_for_data: Callable[[PixelColorT, XyCoordsT], Any] | None,
) -> None:
    x, y = tapper.mouse.get_pos()
    r, g, b = get_pixel_color((x, y), None)
    hex_ = rgb_to_hex(r, g, b)
    formatted = str_format.format(r=r, g=g, b=b, x=x, y=y, hex=hex_)
    if callback_for_str is not None:
        callback_for_str(formatted)
    if callback_for_data is not None:
        callback_for_data((r, g, b), (x, y))


def pixel_str(coords: XyCoordsT, outer: ImageT | None) -> str:
    color = get_pixel_color(coords, outer)
    return f"({color[0]}, {color[1]}, {color[2]}), ({coords[0]}, {coords[1]})"
