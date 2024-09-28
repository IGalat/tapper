import os
from typing import TypeAlias
from typing import Union

from numpy import ndarray

PixelColorT: TypeAlias = tuple[int, int, int]
"""RGB color of a pixel, 0-255 values."""

XyCoordsT: TypeAlias = tuple[int, int]
""" x, y coordinates on an image or screen."""

BboxT: TypeAlias = tuple[int, int, int, int]
"""Bounding box for an image (rectangle), defined by two points.
x1 y1 x2 y2. Top left is point 1 (x1 y1), bottom right is point 2 (x2 y2)."""

ImagePixelMatrixT: TypeAlias = ndarray
"""List of lists of pixel colors.

example, picture with 2x2 green pixels: (not a python's list, but a numpy array)
[[[0, 255, 0], [0, 255, 0]],
[[0, 255, 0], [0, 255, 0]]]
"""

ImagePathT: TypeAlias = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]

ImageT: TypeAlias = Union[ImagePixelMatrixT, ImagePathT]
""" Can be:
- Image as numpy RGB array.
- str or bytes path to an image.
"""
