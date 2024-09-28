import os.path
import re
import sys
from functools import lru_cache
from lib2to3.pytree import convert
from sys import prefix
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
from tapper.helper._util.image import base
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePathT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import PixelColorT
from tapper.helper.model_types import XyCoordsT
from tapper.model import constants


def find_raw(
    target: ImagePixelMatrixT,
    outer: ImagePixelMatrixT,
) -> tuple[float, XyCoordsT]:
    """Doesn't account for the starting coords of the search."""
    confidence, coords = base.find_fuzzy_cv2(target, outer)
    target_size_x, target_size_y = base.get_image_size(target)
    return confidence, (coords[0] + target_size_x // 2, coords[1] + target_size_y // 2)


def api_find_raw(
    image: ImagePixelMatrixT,
    bbox: BboxT | None,
    outer_maybe: ImagePixelMatrixT | None = None,
) -> tuple[float, XyCoordsT]:
    x_start, y_start = base.get_start_coords(outer_maybe, bbox)
    outer = base.outer_to_image(outer_maybe, bbox)
    confidence, xy = find_raw(image, outer)
    return confidence, (x_start + xy[0], y_start + xy[1])


def find(
    target: ImageT,
    outer: ImageT,
    precision: float,
) -> XyCoordsT | None:
    """Doesn't account for the starting coords of the search."""
    confidence, xy = find_raw(target, outer)
    if confidence < precision:
        return None
    return xy


def api_find(
    target: ImageT,
    bbox: BboxT | None,
    outer_or_path_maybe: ImageT | None = None,
    precision: float = 1.0,
) -> XyCoordsT | None:
    if target is None:
        raise ValueError("image_find nees something to search for.")
    target_image = base.target_to_image(target, bbox)
    outer = base.outer_to_image(outer_or_path_maybe, bbox)
    found = find(target_image, outer, precision)
    if found is None:
        return None
    x_start, y_start = base.get_start_coords(outer_or_path_maybe, bbox)
    return x_start + found[0], y_start + found[1]


def find_one_of() -> None:
    pass


def wait_for() -> None:
    pass


def wait_for_one_of() -> None:
    pass
