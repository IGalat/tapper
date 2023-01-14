from numpy import ndarray


def find(outer: ndarray, inner: ndarray) -> tuple[float, tuple[int, int]]:
    import cv2

    comparison = cv2.matchTemplate(outer, inner, cv2.TM_CCORR_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(comparison)
    return max_val, max_loc
