import time
from functools import partial
from typing import Any
from typing import Callable
from typing import Iterable

import tapper
from tapper.helper._util import image_util as _image_util
from tapper.helper._util.image import base as _base_util
from tapper.helper._util.image import find_util as _find_util
from tapper.helper._util.image import snip_util as _snip_util
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePathT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import PixelColorT
from tapper.helper.model_types import XyCoordsT

STD_PRECISION = 0.999


def _check_dependencies() -> None:
    try:
        import PIL  # noqa
        import mss  # noqa
        import cv2  # noqa
        import numpy  # noqa
    except ImportError as e:
        raise ImportError(
            "Looks like you're missing dependencies for tapper img helper."
            "Try `pip install tapper[img]` or `pip install tapper[all]`.",
            e,
        )


def from_path(pathlike: ImagePathT, cache: bool = True) -> ImagePixelMatrixT:
    """Get image from file path."""
    _check_dependencies()
    return _base_util.api_from_path(pathlike, cache)  # type: ignore


def find(
    target: ImageT,
    bbox: BboxT | None = None,
    outer: ImageT | None = None,
    precision: float = STD_PRECISION,
) -> XyCoordsT | None:
    """
    Search a region of the screen for an image.

    :param target: what to find. Path to an image, or image object(numpy array).
    :param bbox: bounding box of where to search in the outer.
    :param outer: Optional image in which to find, path or numpy array. If not specified, will search on screen.
    :param precision: A number between 0 and 1 to indicate the allowed deviation from the searched image.
        0.95 is a difference visible to the eye, and random images can sometimes match up to 0.8.
        To calibrate, use get_find_raw function.

    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
        If image not found, None is returned.
    """
    _check_dependencies()
    return _find_util.api_find(target, bbox, outer, precision=precision)  # type: ignore


def find_one_of(
    targets: (
        list[ImageT] | tuple[list[ImageT], BboxT] | list[tuple[ImageT, BboxT | None]]
    ),
    outer: str | ImagePixelMatrixT | None = None,
    precision: float = STD_PRECISION,
) -> tuple[ImageT, XyCoordsT] | tuple[None, None]:
    """
    Get first image found. Faster than several calls to :func:find
    due to not taking screenshot every time.

    :param targets: what to find. Can be just a list of targets, a list with one bbox, or
        pairs of target and bbox.
    :param outer: see the same param of :func:find
    :param precision: see the same param of :func:find
    :return: First image detected and coords, if found.
        Will return object supplied in the list if it finds corresponding image.
        In case many images could match, first match in the `images` list will be returned.
    """
    _check_dependencies()
    return _find_util.api_find_one_of(targets, outer, precision)


def wait_for(
    target: ImageT,
    bbox: BboxT | None = None,
    timeout: int | float = 5,
    interval: float = 0.2,
    precision: float = STD_PRECISION,
) -> XyCoordsT | None:
    """
    Regularly search the screen or region of the screen for image,
    returning coordinates when it appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param target: what to find. Path to an image, or image object(numpy array).
    :param bbox: bounding box of where to search in the outer.
    :param timeout: If this many seconds elapsed, return None.
    :param interval: Time between searches. Note that search can take significant time as well,
        and actual frequency may be lower than you expect because of this.
    :param precision: see `find` param.
    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
    """
    _check_dependencies()
    return _find_util.wait_for(target, bbox, timeout, interval, precision)


def wait_for_one_of(
    targets: (
        list[ImageT] | tuple[list[ImageT], BboxT] | list[tuple[ImageT, BboxT | None]]
    ),
    timeout: int | float = 5,
    interval: float = 0.4,
    precision: float = STD_PRECISION,
) -> tuple[ImageT, XyCoordsT] | tuple[None, None]:
    """
    Regularly search the screen or region of the screen for images,
    returning first that appears, or None if timeout.
    This is blocking until timeout or until found something.
    For performance, it's recommended to use images and not filenames as targets.
        see :func:from_path.

    :param targets: what to find. Can be just a list of targets, a list with one bbox, or
        pairs of target and bbox.
    :param timeout: If this many seconds elapsed, return None.
    :param interval: Time between searches. Note that search can take significant time as well,
        and actual frequency may be lower than you expect because of this.
    :param precision: see `find` param.

    :return: First image detected, or (None, None) if timeout.
        Will return object supplied in the list if it finds corresponding image.
        In case many images appear in one search (e.g. there were none and then 2 appeared),
        first found in the `images` list will be returned.

    Usage example:
        yes_btn = "yes.png"
        no_btn = "no.png"
        close_btn = "close.png"

        btn, btn_xy = img.wait_for_one_of(([yes_btn, no_btn, close_btn], (100, 213, 256, 412)))

        if btn == yes_btn:  click(btn_xy)
        elif btn == no_btn:  warn()
        elif btn == close_btn:  close_app()
        else:  raise ValueError
    """
    _check_dependencies()
    return _find_util.wait_for_one_of(targets, timeout, interval, precision)


def get_find_raw(
    target: ImageT, bbox: BboxT | None = None, outer: ImageT | None = None
) -> tuple[float, XyCoordsT]:
    """
    Find an image within a region of the screen or image, and return raw result.
    Immediate function, wrap in lambda if setting as action of Tap.

    :param target: what to find. Path to an image, or image object(numpy array).
    :param bbox: bounding box of where to search in the outer.
    :param outer: Optional image in which to find, path or numpy array. If not specified, will search on screen.
    :return: Match precision, and coordinates.
    """
    _check_dependencies()
    return _find_util.api_find_raw(target, bbox, outer)


def snip(
    prefix: str | None = "snip",
    bbox_to_name: bool = True,
    override_existing: bool = True,
    bbox_callback: Callable[[tuple[int, int, int, int]], Any] | None = None,
    picture_callback: Callable[[ImagePixelMatrixT], Any] | None = None,
) -> Callable[[], None]:
    """
    Click twice to get a picture(.png) of a region the screen.
    Region is the rectangle between mouse cursor positions on first and second click.

    :param prefix: Name prefix. It may be a path. If your picture is not in same dir as script with tapper.start,
        has to be a path, absolute or relative to that dir.
    :param bbox_to_name: If true, will include in the name "-(BBOX_{x1}_{y1}_{x2}_{y2})", with actual coordinates.
        This is useful for precise-position search with `find` and `wait_for` methods.
    :param override_existing: Will override existing file if prefix exists, otherwise will save as prefix(2).png
    :param bbox_callback: Action to be applied to bbox coordinates when snip is taken.
        This is an alternative to bbox_to_name, if you want to supply it separately later.
    :param picture_callback: Action to be applied to the array of resulting picture RGB.
    :return: callable toggle, to be set into a Tap

    Example:
        {"a": img.snip()}
            Mouseover a corner of desired snip, click "a", mouseover diagonal corner, click "a",
            and you'll get an image with default name and bounding box in the name in the working dir of the script.

        {"a": img.snip(prefix=None, bbox_callback=pyperclip.copy)}
            This will only copy bounding box to your clipboard. Package pyperclip if required for this.
    """
    _check_dependencies()
    return partial(
        _snip_util.toggle_snip,
        prefix=prefix,
        bbox_to_name=bbox_to_name,
        override_existing=override_existing,
        bbox_callback=bbox_callback,
        picture_callback=picture_callback,
    )


def get_snip(
    bbox: BboxT | None,
    prefix: str | None = None,
    bbox_to_name: bool = True,
    override_existing: bool = True,
) -> ImagePixelMatrixT:
    """
    Screenshot with specified bounding box, or entire screen. Optionally saves to disk.

    Immediate function, wrap in lambda if setting as action of Tap.

    :param bbox: Bounding box of the screenshot or image. If None, the whole screen or image is snipped.
    :param prefix: Optional name, may be a path of image to save, without extension. If not specified,
    will not be saved to disk.
    :param bbox_to_name: If true, will append to the name "-BBOX({x1},{y1},{x2},{y2})", with corner coordinates.
    :param override_existing: Will override existing file if prefix exists, otherwise will save as prefix(2).png
    :return: Resulting image RGB, transformed to numpy array.

    Usage:
        my_pic = img.get_snip(bbox=(100, 100, 200, 400))
        ...
        img.wait_for(my_pic)
    """
    return _snip_util.finish_snip(
        bbox=bbox,
        prefix=prefix,
        bbox_to_name=bbox_to_name,
        override_existing=override_existing,
    )[0]


def pixel_info(
    callback: Callable[[PixelColorT, XyCoordsT], Any],
    outer: ImageT | None = None,
) -> Callable[[], Any]:
    """
    Click to get pixel color and coordinates and call the callback with it.

    :param callback: Action to do with resulting data.
        Data example:
        (255, 255, 255), (1919, 1079)
         Red Green Blue    X      Y
    :param outer: Optional image in which to find, pathname or numpy array. If not specified, will search on screen.
    :return: callable toggle, to be set into a Tap.
    """
    return lambda: callback(
        pixel_get_color(tapper.mouse.get_pos(), outer), tapper.mouse.get_pos()
    )


# todo custom format? like format=r"({r}, {g}, {b}), ({x}, {y})"
def pixel_str(
    callback: Callable[[str], Any], outer: str | ImagePixelMatrixT | None = None
) -> Callable[[], Any]:
    """
    Click to get pixel color and coordinates in as text and call the callback with it.

    :param callback: Action to do with resulting data.
        Data example:
        "(255, 255, 255), (1919, 1079)"
    :param outer: Optional image in which to find, pathname or numpy array. If not specified, will search on screen.
    :return: callable toggle, to be set into a Tap.

    Example usage:
    {"a": img.pixel_str(pyperclip.copy)}
    ... then press "a" to get pixel, and paste it into another script:
    img.pixel_find((255, 255, 255), (1919, 1079))
    """
    return lambda: callback(_image_util.pixel_str(tapper.mouse.get_pos(), outer))


# todo method to get color #FFFFFF? or remove this, and use format on pixel_str
def pixel_get_color(coords: XyCoordsT, outer: ImageT | None = None) -> PixelColorT:
    """
    Get pixel color.

    Immediate function, wrap in lambda if setting as action of Tap.

    :param coords: x, y coordinates of the pixel, absolute to screen, or relative to outer.
    :param outer: Optional image, pathname or numpy array. If not specified, will get color from screen.
    :return: Decimal values of Red, Green, and Blue components of the pixel color.
    """
    return _image_util.get_pixel_color(coords, outer)


# todo accept color #FFFFFF
def pixel_find(
    color: PixelColorT,
    bbox_or_coords: BboxT | XyCoordsT | None = None,
    outer: str | ImagePixelMatrixT | None = None,
    variation: int = 0,
) -> XyCoordsT | None:
    """
    Search a region of the screen or an image for a pixel with matching color.
    :param color: Red, Green, Blue components ranging from 0 to 255.
    :param outer: Optional image in which to find, pathname or numpy array. If not specified, will search on screen.
    :param bbox_or_coords: Bounding box of the screenshot or image. If None, the whole screen or image is snipped.
        If coordinates are supplied, only one pixel at those coordinates will be checked.
    :param variation: Allowed number of shades of variation in either direction for the intensity of the
        red, green, and blue components, 0-255.
        For example, if 2 is specified and color is (10, 10, 10),
        any color from (8, 8, 8) to (12, 12, 12) will be considered a match.

        This parameter is helpful if the color sought is not always exactly the same shade.
        If you specify 255 shades of variation, all colors will match.
    :return: Coordinates X and Y of the first pixel that matches, or None if no match.
    """
    return _image_util.pixel_find(
        color, bbox_or_coords, _image_util.normalize(outer)[0], variation
    )


def pixel_wait_for(
    color: PixelColorT,
    bbox_or_coords: BboxT | XyCoordsT | None = None,
    timeout: int | float = 5,
    interval: float = 0.1,
    variation: int = 0,
) -> XyCoordsT | None:
    """
    Regularly search the screen or region of the screen for a pixel,
    returning coordinates when it appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param color: see `pixel_find` param.
    :param bbox_or_coords: see `pixel_find` param.
    :param timeout: If this many seconds elapsed, return None.
    :param interval: Time between searches, in seconds.
    :param variation: see `pixel_find` param.
    :return: Coordinates of the pixel if found, else None.
    """
    finish_time = time.perf_counter() + timeout
    while True:
        if found := pixel_find(color, bbox_or_coords, variation=variation):
            return found
        if time.perf_counter() > finish_time:
            return None
        time.sleep(interval)
        if time.perf_counter() > finish_time:
            return None


def pixel_wait_for_one_of(
    colors_coords: Iterable[tuple[PixelColorT, BboxT | XyCoordsT | None]],
    timeout: int | float = 5,
    interval: float = 0.1,
    variation: int = 0,
) -> tuple[PixelColorT, BboxT | XyCoordsT | None] | None:
    """
    Regularly search the screen or region of the screen for pixels,
    returning first that appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param colors_coords: list of tuples(color, coords) - for color and coords see pixel_find.
        Each pixel may have own coords/bbox to be searched in. Coords None will search entire screen.
    :param timeout: see `pixel_wait_for` param.
    :param interval: see `pixel_wait_for` param.
    :param variation: see `pixel_find` param.
    :return: tuple(color, coords) that was found, else None.
    """
    # Todo rework: colors_coords now: (color, coords | None), to: color | (color, coords)
    finish_time = time.perf_counter() + timeout
    while True:
        for _, color_coords in enumerate(colors_coords):
            if pixel_find(*color_coords, variation=variation):
                return color_coords
        if time.perf_counter() < finish_time:
            return None
        time.sleep(interval)
        if time.perf_counter() < finish_time:
            return None
