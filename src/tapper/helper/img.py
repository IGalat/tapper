import re
import time
from functools import partial
from typing import Any
from typing import Callable
from typing import Union

import tapper
from numpy import ndarray
from tapper.helper._util.image import _find_in_image
from tapper.helper._util.image import _finish_snip
from tapper.helper._util.image import _get_pixel_color
from tapper.helper._util.image import _normalize
from tapper.helper._util.image import _pixel_find
from tapper.helper._util.image import _pixel_str
from tapper.helper._util.image import _toggle_snip

SearchableImage = Union[
    str,
    tuple[str, tuple[int, int, int, int]],
    tuple[ndarray, tuple[int, int, int, int] | None],
]
"""
Image to be searched for. May be:
    - numpy array: pimg = numpy.array(PIL.Image.open('Image.jpg')). RGB is expected.
    - numpy array with bounding box: (pimg, (0, 0, 200, 50)), where coordinates are x_left, y_top, x_right, y_bottom
    - file path, absolute or relative: pic_name = "my_button.png"
    - file path with bounding box: (pic_name, (0, 0, 200, 50))
    - file path with bounding box in the name: pic_name = "my_button(BBOX_-100_213_-56_412).png"
        Pattern is: (BBOX_{int}_{int}_{int}_{int})
        If bounding box is specified separately, BBOX in the name will be ignored.
Coordinates of bounding box may be negative on win32 with multiple screens.
If bounding box is not specified as tuple or in the name, the whole screen will be searched.
For performance, it's highly recommended to specify bounding box: searching smaller area is faster.
"""

_bbox_pattern = re.compile(r"\(BBOX_-?\d+_-?\d+_-?\d+_-?\d+\)")


def find(
    image: SearchableImage, outer: str | ndarray | None = None, precision: float = 1.0
) -> tuple[int, int] | None:
    """
    Search a region of the screen for an image.

    :param image: see SearchableImage
    :param outer: Optional image in which to find, pathname or numpy array. If not specified, will search on screen.
    :param precision: A number between 0 and 1 to indicate the allowed deviation from the searched image.
        0.95 is a difference visible to the eye, and random images can sometimes match up to 0.8.

    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
        If image not found, None is returned.
    """
    norm_outer = _normalize(outer)[0] if outer is not None else None  # type: ignore
    return _find_in_image(_normalize(image), norm_outer, precision=precision)  # type: ignore


def wait_for(
    image: SearchableImage,
    timeout: int | float = 5,
    interval: float = 0.2,
    precision: float = 1.0,
) -> tuple[int, int] | None:
    """
    Regularly search the screen or region of the screen for image,
    returning coordinates when it appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param image: see SearchableImage
    :param timeout: How long to search for.
    :param interval: Time between searches. Note that search can take significant time as well,
        and actual frequency may be lower than you expect because of this.
    :param precision: see `find` param.
    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
    """
    finish_time = time.perf_counter() + timeout
    normalized = _normalize(image)  # type: ignore
    while time.perf_counter() < finish_time:
        if found := _find_in_image(normalized, precision=precision):  # type: ignore
            return found
        time.sleep(interval)
    return None


def wait_for_one_of(
    images: list[SearchableImage],
    timeout: int | float = 5,
    interval: float = 0.4,
    precision: float = 1.0,
) -> SearchableImage | None:
    """
    Regularly search the screen or region of the screen for images,
    returning first that appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param images: see SearchableImage
    :param timeout: see `wait_for` param.
    :param interval: see `wait_for` param.
    :param precision: see `find` param.

    :return: First image detected, or None if timeout.
        Will return object supplied in the list if it finds corresponding image.
        In case many images appear in one search (e.g. there were none and then 2 appeared),
        first found in the `images` list will be returned.

    Usage:
        yes_btn = "yes.png", (-100, 213, -56, 412)
        no_btn = "no(BBOX_-100_213_-56_412).png"
        close_btn = "close.png"

        if (btn := img.wait_for_one_of([yes_btn, no_btn, close_btn], timeout=2) == yes_btn:
            continue_flow()
        elif btn == no_btn:
            warn()
        elif btn == close_btn:
            close_app()
        else:
            raise ValueError
    """
    finish_time = time.perf_counter() + timeout
    normalized = [_normalize(image) for image in images]  # type: ignore
    while time.perf_counter() < finish_time:
        for i in range(len(normalized)):
            if _find_in_image(normalized[i], precision=precision):  # type: ignore
                return images[i]
        time.sleep(interval)
    return None


def snip(
    prefix: str | None = "snip",
    bbox_in_name: bool = True,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
    picture_callback: Callable[[ndarray], Any] | None = None,
) -> Callable[[], None]:
    """
    Click twice to get a picture(.png) of a region the screen.
    Region is the rectangle between mouse cursor positions on first and second click.

    :param prefix: Name prefix. It may be a path. If your picture is not in same dir as script with tapper.start,
        has to be a path, absolute or relative to that dir.
    :param bbox_in_name: If true, will include in the name -(BBOX_{x1}_{y1}_{x2}_{y2}), with actual coordinates.
        This is useful for precise-position search with `find` and `wait_for` methods.
    :param bbox_callback: Action to be applied to bbox coordinates when snip is taken.
        This is an alternative to bbox_in_name, if you want to supply it separately later.
    :param picture_callback: Action to be applied to the array of resulting picture RGB.
    :return: callable toggle, to be set into a Tap

    Example:
        {"a": img.snip()}
            Mouseover a corner of desired snip, click "a", mouseover diagonal corner, click "a",
            and you'll get an image with default name and bounding box in the name in the working dir of the script.

        {"a": img.snip("image", False, pyperclip.copy)}
            Same procedure to get an image, but this will be called "image.png" without bounding box in the name,
            instead it will be copied to your clipboard. Package pyperclip if required for this.
    """
    return partial(_toggle_snip, prefix, bbox_in_name, bbox_callback, picture_callback)


def get_snip(
    bbox: tuple[int, int, int, int] | None,
    prefix: str | None = None,
    bbox_in_name: bool = True,
) -> ndarray:
    """
    Screenshot with specified bounding box, or entire screen. Optionally saves to disk.

    NOTE: This is an immediate function and should not be set as action of Tap.

    :param bbox: Bounding box of the screenshot or image. If None, the whole screen or image is snipped.
    :param prefix: Optional name, may be a path of image to save, without extension. If not specified,
    will not be saved to disk.
    :param bbox_in_name: If true, will include in the name -(BBOX_{x1}_{y1}_{x2}_{y2}), with actual coordinates.
        This is useful for precise-position search with `find` and `wait_for` methods.
    :return: Resulting image RGB, transformed to numpy array.

    Usage:
        my_pic = img.snip_bbox((100, 100, 200, 400))
        ...
        img.wait_for(my_pic)
    """
    return _finish_snip(prefix, bbox, bbox_in_name)[0]


def pixel_info(
    callback: Callable[[tuple[int, int, int], tuple[int, int]], Any],
    outer: str | ndarray | None = None,
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
        get_pixel_color(tapper.mouse.get_pos(), outer), tapper.mouse.get_pos()
    )


def pixel_str(
    callback: Callable[[str], Any], outer: str | ndarray | None = None
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
    return lambda: callback(_pixel_str(tapper.mouse.get_pos(), outer))


def get_pixel_color(
    coords: tuple[int, int], outer: str | ndarray | None = None
) -> tuple[int, int, int]:
    """
    Get pixel color.

    NOTE: This is an immediate function and should not be set as action of Tap.

    :param coords: x, y coordinates of the pixel, absolute to screen, or relative to outer.
    :param outer: Optional image, pathname or numpy array. If not specified, will get color from screen.
    :return: Decimal values of Red, Green, and Blue components of the pixel color.
    """
    return _get_pixel_color(coords, outer)


def pixel_find(
    color: tuple[int, int, int],
    bbox_or_coords: tuple[int, int, int, int] | tuple[int, int] | None = None,
    outer: str | ndarray | None = None,
    variation: int = 0,
) -> tuple[int, int] | None:
    """
    Search a region of the screen or an image for a pixel with matching color.
    :param color: Red, Green, Blue components ranging from 0 to 255.
    :param outer: Optional image in which to find, pathname or numpy array. If not specified, will search on screen.
    :param bbox_or_coords: Bounding box of the screenshot or image. If None, the whole screen or image is snipped.
        If coordinates are supplied, only one pixel at those coordinates will be checked.
    :param variation: Allowed number of shades of variation in either direction for the intensity of the
        red, green, and blue components, 0-255. For example, if 2 is specified and color is (10, 10, 10),
        any color from (8, 8, 8) to (12, 12, 12) will be considered a match.
        This parameter is helpful if the color sought is not always exactly the same shade.
        If you specify 255 shades of variation, all colors will match.
    :return: Coordinates X and Y of the first pixel that matches, or None if no match.
    """
    return _pixel_find(color, bbox_or_coords, outer, variation)
