"""Optional image-analysis suggestions; candidates always require human approval."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PixelSuggestion:
    """Candidate wall mask explicitly marked as unconfirmed."""

    mask: np.ndarray
    method: str
    human_confirmation_required: bool = True


def suggest_walls(image: np.ndarray, *, method: str = "edges") -> PixelSuggestion:
    """Suggest likely wall pixels using optional OpenCV threshold or edge detection."""
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("OpenCV is required for image suggestions") from exc
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    if method == "edges":
        result = cv2.Canny(gray, 50, 150) > 0
    elif method == "threshold":
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        result = threshold > 0
    else:
        raise ValueError("method must be 'edges' or 'threshold'")
    result.setflags(write=False)
    return PixelSuggestion(result, method)
