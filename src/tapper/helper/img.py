import re
import time
from functools import partial
from typing import Any
from typing import Callable
from typing import Union

from numpy import ndarray
from tapper.helper._util.image import _find_on_screen
from tapper.helper._util.image import _normalize
from tapper.helper._util.image import _toggle_snip

SearchableImage = Union[
    str,
    tuple[str, tuple[int, int, int, int]],
    tuple[ndarray, tuple[int, int, int, int]],
    tuple[ndarray, None],
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


def find(image: SearchableImage, precision: float = 1.0) -> tuple[int, int] | None:
    """
    Search a region of the screen for an image.

    :param image: see SearchableImage
    :param precision: A number between 0 and 1 to indicate the allowed deviation from the searched image.
        0.95 is a difference visible to the eye, and random images can sometimes match up to 0.8.

    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
        If image not found, None is returned.
    """
    return _find_on_screen(_normalize(image), precision)


def wait_for(
    image: SearchableImage,
    timeout: int | float = 5,
    interval: float = 0.2,
    precision: float = 1.0,
) -> tuple[int, int] | None:
    """
    Regularly search for image, returning coordinates when it appears, or None if timeout.
    This is blocking until timeout, obviously.

    :param image: see SearchableImage
    :param timeout: How long to search for.
    :param interval: Time between searches. Note that search can take significant time as well,
        and actual frequency may be lower than you expect because of this.
    :param precision: see `find` param.
    :return: Coordinates X and Y of top-left of the found image relative to the bounding box (if any).
    """
    finish_time = time.perf_counter() + timeout
    normalized = _normalize(image)
    while time.perf_counter() < finish_time:
        if found := _find_on_screen(normalized, precision):
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
    Regularly search for images, returning first that appears, or None if timeout.
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

        if (btn := img.wait_for_one_of([yes_btn, no_btn, close_btn], 2) == yes_btn:
            continue_flow()
        elif btn == no_btn:
            warn()
        elif btn == close_btn:
            close_app()
        else:
            raise ValueError
    """
    finish_time = time.perf_counter() + timeout
    normalized = [_normalize(image) for image in images]
    while time.perf_counter() < finish_time:
        for i in range(len(normalized)):
            if _find_on_screen(normalized[i], precision):
                return images[i]
        time.sleep(interval)
    return None


def snip(
    prefix: str = "snip",
    bbox_in_name: bool = True,
    bbox_callback: Callable[[int, int, int, int], Any] | None = None,
) -> Callable[[], None]:
    """
    Press twice to get a picture(.png) of a region the screen.
    Region is the rectangle between mouse cursor positions on first and second click.

    :param prefix: Name prefix. It may be a path.
    :param bbox_in_name: If true, will include in the name -(BBOX_{x1}_{y1}_{x2}_{y2}), with actual coordinates.
        This will allow for precise-position search with `find` and `wait_for` methods.
    :param bbox_callback: Action to be applied to bbox coordinates when snip is taken.
        This is an alternative to bbox_in_name, if you want to supply it separately later.
    :return: callable toggle, to be set into a Tap

    Example:
        {"a": img.snip()}
            Mouseover a corner of desired snip, click "a", mouseover diagonal corner, click "a",
            and you'll get an image with default name and bounding box in the name in the working dir of the script.

        {"a": img.snip("image", False, pyperclip.copy)}
            Same procedure to get an image, but this will be called "image.png" without bounding box in the name,
            instead it will be copied to your clipboard. Package pyperclip if required for this.
    """
    return partial(_toggle_snip, prefix, bbox_in_name, bbox_callback)
