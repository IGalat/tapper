import time

from tapper.helper._util.image import base
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import ImageT
from tapper.helper.model_types import XyCoordsT


def find_raw(
    target: ImagePixelMatrixT,
    outer: ImagePixelMatrixT,
) -> tuple[float, XyCoordsT]:
    """Doesn't account for the starting coords of the search."""
    confidence, coords = base.find_fuzzy_cv2(target, outer)
    target_size_x, target_size_y = base.get_image_size(target)
    return confidence, (coords[0] + target_size_x // 2, coords[1] + target_size_y // 2)


def api_find_raw(
    target: ImagePixelMatrixT,
    bbox: BboxT | None,
    outer_maybe: ImagePixelMatrixT | None = None,
) -> tuple[float, XyCoordsT]:
    x_start, y_start = base.get_start_coords(outer_maybe, bbox)
    outer = base.outer_to_image(outer_maybe, bbox)
    confidence, xy = find_raw(target, outer)
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
    outer_or_path_maybe: ImageT | None,
    precision: float,
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


def find_one_of(
    targets_normalized: list[tuple[ImagePixelMatrixT, BboxT | None, ImageT]],
    outer_or_path_maybe: ImageT | None,
    precision: float,
) -> tuple[ImageT, XyCoordsT] | tuple[None, None]:
    outer = base.outer_to_image(outer_or_path_maybe, None)
    for target, bbox, original in targets_normalized:
        outer_cut = base.outer_to_image(outer, bbox)
        if (xy := find(target, outer_cut, precision)) is not None:
            return original, xy
    return None, None


def api_find_one_of(
    targets: list[ImageT]
    | tuple[list[ImageT], BboxT]
    | list[tuple[ImageT, BboxT | None]],
    outer_or_path_maybe: ImageT | None,
    precision: float,
) -> tuple[ImageT, XyCoordsT] | tuple[None, None]:
    targets_normalized = base.targets_normalize(targets)
    return find_one_of(targets_normalized, outer_or_path_maybe, precision)


def wait_for(
    target: ImageT,
    bbox: BboxT | None,
    timeout: int | float,
    interval: float,
    precision: float,
) -> XyCoordsT | None:
    target_image = base.target_to_image(target, bbox)
    finish_time = time.perf_counter() + timeout
    while time.perf_counter() < finish_time:
        outer = base.outer_to_image(None, bbox)
        if found := find(target_image, outer, precision):
            return found
        time.sleep(interval)
    return None


def wait_for_one_of(
    targets: list[ImageT]
    | tuple[list[ImageT], BboxT]
    | list[tuple[ImageT, BboxT | None]],
    timeout: int | float,
    interval: float,
    precision: float,
) -> tuple[ImageT, XyCoordsT] | tuple[None, None]:
    targets_normalized = base.targets_normalize(targets)
    finish_time = time.perf_counter() + timeout
    while time.perf_counter() < finish_time:
        found, xy = find_one_of(targets_normalized, None, precision)
        if found is not None and xy is not None:
            return found, xy
        time.sleep(interval)
    return None, None
