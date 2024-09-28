import importlib.resources
from pathlib import Path

import numpy as np
import resources
from numpy import ndarray
from PIL import Image


def from_matrix(matrix: list[list[tuple[int, int, int]]]) -> ndarray:
    return np.uint8(matrix)  # type: ignore


def get_image_path(name: str) -> Path:
    return importlib.resources.files(resources).joinpath("image").joinpath(name)  # type: ignore


def get_picture(name: str) -> ndarray:
    path = get_image_path(name)
    pil_img = Image.open(path).convert("RGB")
    return np.asarray(pil_img)


def absolutes() -> ndarray:
    return get_picture("absolutes.png")


def btn_all() -> ndarray:
    return get_picture("btn_all.png")


def btn_red() -> ndarray:
    return get_picture("btn_red.png")


def btn_yellow() -> ndarray:
    return get_picture("btn_yellow.png")


def btn_blue() -> ndarray:
    return get_picture("btn_blue.png")


def btn_pink() -> ndarray:
    return get_picture("btn_pink.png")
