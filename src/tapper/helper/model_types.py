from numpy import ndarray

PixelColorT = tuple[int, int, int]
"""RGB color of a pixel, 0-255 values."""

XyCoordsT = tuple[int, int]
""" x, y coordinates on an image or screen."""

ImagePixelMatrixT = ndarray
"""List of lists of pixel colors.

2x2 green pixels:
[[[0, 255, 0], [0, 255, 0]],
[[0, 255, 0], [0, 255, 0]]]
"""

BboxT = tuple[int, int, int, int]
"""Bounding box for an image.
x1 y1 x2 y2. usually top left is x1 y1, and bottom right is x2 y2."""
