import os.path
import sys
from functools import lru_cache

import mss
import numpy as np
import PIL.Image
import PIL.ImageGrab
from mss.base import MSSBase
from numpy import ndarray
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePathT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import XyCoordsT
from tapper.model import constants


def find_fuzzy_cv2(target: ndarray, outer: ndarray) -> tuple[float, XyCoordsT]:
    import cv2

    comparison = cv2.matchTemplate(outer, target, cv2.TM_CCORR_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(comparison)
    return max_val, max_loc  # type: ignore


mss_instance: MSSBase


def get_mss() -> MSSBase:
    global mss_instance
    mss_instance = mss.mss()
    return mss_instance


@lru_cache(maxsize=5)
def from_path(pathlike: ImagePathT) -> ImagePixelMatrixT:
    if isinstance(pathlike, str):
        pathlike = os.path.abspath(pathlike)
    pil_img = PIL.Image.open(pathlike).convert("RGB")
    return np.asarray(pil_img)


def api_from_path(pathlike: ImagePathT, cache: bool) -> ImagePixelMatrixT:
    if not cache:
        from_path.cache_clear()
    return from_path(pathlike)  # type: ignore


def to_pixel_matrix(image: ImageT | None) -> ImagePixelMatrixT | None:
    if image is None:
        return None
    elif isinstance(image, ndarray):
        return image
    elif isinstance(image, (str, bytes, os.PathLike)):
        return from_path(os.path.abspath(image))
    else:
        raise TypeError(f"Unexpected type, {type(image)} of {image}")


def get_image_size(image: ImagePixelMatrixT) -> tuple[int, int]:
    return image.shape[1], image.shape[0]


def get_screenshot_if_none_and_cut(
    maybe_image: ImagePixelMatrixT | None, bbox: BboxT | None
) -> ImagePixelMatrixT:
    if maybe_image is not None:
        if bbox:
            return maybe_image[bbox[1] : bbox[3], bbox[0] : bbox[2]]
        return maybe_image
    if bbox is not None:
        try:
            sct = get_mss().grab(bbox)
        except Exception as e:
            raise e
    else:
        sct = get_mss().grab(get_mss().monitors[0])
    pil_rgb = PIL.Image.frombytes("RGB", sct.size, sct.bgra, "raw", "BGRX")
    return np.asarray(pil_rgb)


def check_bbox_smaller_or_eq(
    image: ImagePixelMatrixT | None, bbox: BboxT | None
) -> None:
    if image is None or bbox is None:
        return
    bbox_x = abs(bbox[2] - bbox[0])
    bbox_y = abs(bbox[3] - bbox[1])
    image_x, image_y = get_image_size(image)
    if bbox_x > image_x or bbox_y > image_y:
        raise ValueError(
            f"Bbox should NOT be bigger, but got {bbox_x}x{bbox_y} vs image {image_x}x{image_y}"
        )


def check_bbox_bigger_or_eq(
    image: ImagePixelMatrixT | None, bbox: BboxT | None
) -> None:
    if image is None or bbox is None:
        return
    bbox_x = abs(bbox[2] - bbox[0])
    bbox_y = abs(bbox[3] - bbox[1])
    image_x, image_y = get_image_size(image)
    if bbox_x < image_x or bbox_y < image_y:
        raise ValueError(
            f"Bbox should NOT be smaller, but got {bbox_x}x{bbox_y} vs image {image_x}x{image_y}"
        )


def get_start_coords(
    outer: ndarray | None,
    bbox_or_coords: BboxT | XyCoordsT | None,
) -> XyCoordsT:
    if bbox_or_coords is not None:
        return bbox_or_coords[0], bbox_or_coords[1]
    if outer is None and sys.platform == constants.OS.win32:
        return win32_coords_start()
    return 0, 0


def win32_coords_start() -> XyCoordsT:
    """Win32 may start with negative coords when multiscreen."""
    import winput
    from win32api import GetSystemMetrics

    winput.set_DPI_aware(per_monitor=True)
    x = GetSystemMetrics(76)
    y = GetSystemMetrics(77)
    return x, y


def target_to_image(target: ImageT, bbox: BboxT | None) -> ImagePixelMatrixT:
    """Transform and verify target from API input to workable image-array."""
    target_image = to_pixel_matrix(target)
    assert target_image is not None  # for mypy
    if bbox is not None:
        bbox_x = abs(bbox[2] - bbox[0])
        bbox_y = abs(bbox[3] - bbox[1])
        image_x, image_y = get_image_size(target_image)
        if bbox_x < image_x or bbox_y < image_y:
            raise ValueError(
                f"Bbox should NOT be smaller than target, "
                f"but got {bbox_x}x{bbox_y} vs target {image_x}x{image_y}"
            )
    return target_image


def outer_to_image(
    outer_or_path_maybe: ImageT | None, bbox: BboxT | None
) -> ImagePixelMatrixT:
    """Transform and verify target from API input (or screenshot) to workable image-array."""
    outer_maybe = to_pixel_matrix(outer_or_path_maybe)
    if outer_maybe is not None and bbox is not None:
        bbox_x = abs(bbox[2] - bbox[0])
        bbox_y = abs(bbox[3] - bbox[1])
        image_x, image_y = get_image_size(outer_maybe)
        if bbox_x > image_x or bbox_y > image_y:
            raise ValueError(
                f"Bbox should NOT be bigger than outer, "
                f"but got {bbox_x}x{bbox_y} vs outer {image_x}x{image_y}"
            )
    return get_screenshot_if_none_and_cut(outer_maybe, bbox)


def targets_normalize(
    targets: (
        list[ImageT] | tuple[list[ImageT], BboxT] | list[tuple[ImageT, BboxT | None]]
    )
) -> list[tuple[ImagePixelMatrixT, BboxT | None, ImageT]]:
    """Transform any variant of input to :func:find_one_of to list[image-array, bbox, original target]"""
    if not targets:
        ValueError("find_one_of no targets supplied.")
    if isinstance(targets, tuple):
        target_images, bbox = targets
        return [(to_pixel_matrix(image), bbox, image) for image in target_images]
    elif isinstance(targets, list) and isinstance(targets[0], tuple):
        return [(to_pixel_matrix(image), bbox, image) for image, bbox in targets]
    else:
        return [(to_pixel_matrix(image), None, image) for image in targets]


def save_to_disk(image: ImagePixelMatrixT, full_name_no_ext: ImagePathT) -> None:
    PIL.Image.fromarray(image).save(full_name_no_ext, "PNG")
