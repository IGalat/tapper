from numpy import ndarray


def find(outer: ndarray, inner: ndarray, precision: float) -> tuple[int, int] | None:
    import cv2

    comparison = cv2.matchTemplate(outer, inner, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(comparison)
    return max_loc if max_val >= precision else None
