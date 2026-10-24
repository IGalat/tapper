import os

from numpy import ndarray

type PixelColorT = tuple[int, int, int]
"""RGB color of a pixel, 0-255 values."""

type PixelHexColorT = str
"""Hexadecimal color: '#RRGGBB', case-insensitive."""

type PixelStrFormatT = str
""" Format for pixel's data, f-string that gets filled with data:
- {x}, {y} - coordinates of pixel.
- {r}, {g}, {b} - decimal values of Red, Green, and Blue components of the pixel color.
- {hex} - Hexadecimal color, like '#FFFFFF'

For example, on green pixel at 100x150:
"{x}, {y}" -> "100, 150"
"({r}, {g}, {b}), ({x}, {y})" -> "(0, 255, 0), (100, 150)"
"{hex}, {x}x{y}" -> "#00ff00, 100x150"
"x{{{x}}}y{{{y}}}" -> "x{100}y{150}"   - this one is useful to put in `send`
"""

type XyCoordsT = tuple[int, int]
""" x, y coordinates on an image or screen."""

type BboxT = tuple[int, int, int, int]
"""Bounding box for an image (rectangle), defined by two points.
x1 y1 x2 y2. Top left is point 1 (x1 y1), bottom right is point 2 (x2 y2)."""

type ImagePixelMatrixT = ndarray
"""List of lists of pixel colors.

example, picture with 2x2 green pixels: (not a python's list, but a numpy array)
[[[0, 255, 0], [0, 255, 0]],
[[0, 255, 0], [0, 255, 0]]]
"""

type ImagePathT = str | bytes | os.PathLike[str] | os.PathLike[bytes]

type ImageT = ImagePixelMatrixT | ImagePathT
""" Can be:
- Image as numpy RGB array.
- str or bytes path to an image.
"""
