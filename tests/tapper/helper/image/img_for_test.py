import importlib.resources

import numpy as np
import testresources
from numpy import ndarray
from PIL import Image


def from_matrix(matrix: list[list[tuple[int, int, int]]]) -> ndarray:
    return np.uint8(matrix)  # type: ignore


def get_picture(name: str) -> ndarray:
    full_name = (
        importlib.resources.files(testresources).joinpath("image").joinpath(name)
    )
    pil_img = Image.open(full_name).convert("RGB")
    return np.asarray(pil_img)


def absolutes() -> ndarray:
    return get_picture("absolutes.png")
