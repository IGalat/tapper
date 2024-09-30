import os
from typing import Any
from typing import Callable

import tapper
from tapper.helper._util.image import base
from tapper.helper.model_types import BboxT
from tapper.helper.model_types import ImagePixelMatrixT
from tapper.helper.model_types import XyCoordsT

snip_start_coords: XyCoordsT | None = None


def toggle_snip(
    prefix: str | None = None,
    bbox_to_name: bool = True,
    override_existing: bool = True,
    bbox_callback: Callable[[tuple[int, int, int, int]], Any] | None = None,
    picture_callback: Callable[[ImagePixelMatrixT], Any] | None = None,
) -> None:
    global snip_start_coords
    if not snip_start_coords:
        start_snip()
    else:
        stop_coords = tapper.mouse.get_pos()
        x1 = min(snip_start_coords[0], stop_coords[0])
        x2 = max(snip_start_coords[0], stop_coords[0])
        y1 = min(snip_start_coords[1], stop_coords[1])
        y2 = max(snip_start_coords[1], stop_coords[1])
        snip_start_coords = None
        finish_snip_with_callback(
            prefix,
            bbox_to_name,
            (x1, y1, x2, y2),
            override_existing,
            bbox_callback,
            picture_callback,
        )


def start_snip() -> None:
    global snip_start_coords
    snip_start_coords = tapper.mouse.get_pos()


def finish_snip_with_callback(
    prefix: str | None = None,
    bbox_to_name: bool = True,
    bbox: BboxT | None = None,
    override_existing: bool = True,
    bbox_callback: Callable[[tuple[int, int, int, int]], Any] | None = None,
    picture_callback: Callable[[ImagePixelMatrixT], Any] | None = None,
) -> None:
    nd_sct, bbox = finish_snip(prefix, bbox, bbox_to_name, override_existing)
    if bbox and bbox_callback:
        bbox_callback(bbox)
    if picture_callback:
        picture_callback(nd_sct)


def finish_snip(
    prefix: str | None,
    bbox: BboxT | None,
    bbox_to_name: bool,
    override_existing: bool,
) -> tuple[ImagePixelMatrixT, BboxT | None]:
    sct = base.get_screenshot_if_none_and_cut(None, bbox)
    if prefix is not None:
        bbox_str = (
            f"-BBOX({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"
            if bbox and bbox_to_name
            else ""
        )
        ending = bbox_str + ".png"
        full_name = ""
        if override_existing or not os.path.exists(prefix + ending):
            full_name = prefix + ending
        else:
            for i in range(1, 100):
                potential_name = prefix + f"({i})" + ending
                if not os.path.exists(potential_name):
                    full_name = potential_name
                    break
        base.save_to_disk(sct, full_name)
    return sct, bbox
