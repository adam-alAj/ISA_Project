"""Image transforms that retain a mapping back to original source pixels."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PreprocessedImage:
    """Image and homogeneous transforms between processed and source pixels."""

    image: np.ndarray
    processed_to_source: np.ndarray
    source_to_processed: np.ndarray


def preprocess_image(
    image: np.ndarray,
    *,
    exif_orientation: int = 1,
    crop_xywh: tuple[int, int, int, int] | None = None,
    output_size_wh: tuple[int, int] | None = None,
) -> PreprocessedImage:
    """Apply EXIF orientation, crop and resize while preserving pixel transforms."""
    if image.ndim not in (2, 3) or image.size == 0:
        raise ValueError("image must be a non-empty 2D or 3D array")
    work = image
    h, w = work.shape[:2]
    orientation_transforms = {
        1: np.eye(3, dtype=float),
        2: np.array([[-1, 0, w - 1], [0, 1, 0], [0, 0, 1]], float),
        3: np.array([[-1, 0, w - 1], [0, -1, h - 1], [0, 0, 1]], float),
        4: np.array([[1, 0, 0], [0, -1, h - 1], [0, 0, 1]], float),
        5: np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]], float),
        6: np.array([[0, 1, 0], [-1, 0, h - 1], [0, 0, 1]], float),
        7: np.array([[0, -1, w - 1], [-1, 0, h - 1], [0, 0, 1]], float),
        8: np.array([[0, -1, w - 1], [1, 0, 0], [0, 0, 1]], float),
    }
    if exif_orientation not in orientation_transforms:
        raise ValueError("EXIF orientation must be in 1..8")
    transform = orientation_transforms[exif_orientation]
    if exif_orientation == 2:
        work = np.fliplr(work)
    elif exif_orientation == 3:
        work = np.rot90(work, 2)
    elif exif_orientation == 4:
        work = np.flipud(work)
    elif exif_orientation == 5:
        work = np.transpose(work, (1, 0) + tuple(range(2, work.ndim)))
    elif exif_orientation == 6:
        work = np.rot90(work, 3)
    elif exif_orientation == 7:
        work = np.flipud(np.fliplr(np.transpose(work, (1, 0) + tuple(range(2, work.ndim)))))
    elif exif_orientation == 8:
        work = np.rot90(work, 1)
    if crop_xywh is not None:
        x, y, cw, ch = crop_xywh
        if x < 0 or y < 0 or cw <= 0 or ch <= 0 or x + cw > work.shape[1] or y + ch > work.shape[0]:
            raise ValueError("crop must be a positive rectangle inside the oriented image")
        work = work[y:y + ch, x:x + cw]
        transform = transform @ np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], float)
    if output_size_wh is not None:
        out_w, out_h = output_size_wh
        if out_w <= 0 or out_h <= 0:
            raise ValueError("output dimensions must be positive")
        old_h, old_w = work.shape[:2]
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("OpenCV is required for resizing") from exc
        work = cv2.resize(work, (out_w, out_h), interpolation=cv2.INTER_AREA if out_w < old_w else cv2.INTER_LINEAR)
        scale_x, scale_y = old_w / out_w, old_h / out_h
        resize_transform = np.array([
            [scale_x, 0, (scale_x - 1) / 2],
            [0, scale_y, (scale_y - 1) / 2],
            [0, 0, 1],
        ])
        transform = transform @ resize_transform
    inverse = np.linalg.inv(transform)
    return PreprocessedImage(np.ascontiguousarray(work), transform, inverse)
