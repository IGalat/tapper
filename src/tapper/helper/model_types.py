import os
from typing import TypeAlias
from typing import Union

from numpy import ndarray

PixelColorT = tuple[int, int, int]
"""RGB color of a pixel, 0-255 values."""

XyCoordsT = tuple[int, int]
""" x, y coordinates on an image or screen."""

ImagePixelMatrixT: TypeAlias = ndarray
"""List of lists of pixel colors.

2x2 green pixels:
[[[0, 255, 0], [0, 255, 0]],
[[0, 255, 0], [0, 255, 0]]]
"""

BboxT = tuple[int, int, int, int]
"""Bounding box for an image.
x1 y1 x2 y2. usually top left is x1 y1, and bottom right is x2 y2."""


ImagePathT = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]

ImageT = Union[ImagePixelMatrixT, ImagePathT]
""" Can be:
- Image as numpy RGB array.
- str or bytes path to an image.
"""
