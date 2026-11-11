"""Metric scale calibration from labelled pixel distances."""

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CalibrationResult:
    """Scale estimate and per-measurement fit residuals."""

    pixels_per_meter: float
    residuals_px: tuple[float, ...]
    rms_residual_px: float


def calibrate_two_points(point_a: Sequence[float], point_b: Sequence[float], distance_m: float) -> float:
    """Compute pixels per metre from two (x,y) points and a known distance."""
    if distance_m <= 0:
        raise ValueError("distance_m must be positive")
    a, b = np.asarray(point_a, float), np.asarray(point_b, float)
    if a.shape != (2,) or b.shape != (2,):
        raise ValueError("points must each contain x and y")
    ppm = float(np.linalg.norm(b - a) / distance_m)
    if ppm <= 0:
        raise ValueError("calibration points must be distinct")
    return ppm


def calibrate_least_squares(pixel_distances: Sequence[float], known_distances_m: Sequence[float]) -> CalibrationResult:
    """Fit `pixels = ppm * metres` through the origin and report residuals."""
    pixels = np.asarray(pixel_distances, dtype=float)
    metres = np.asarray(known_distances_m, dtype=float)
    if pixels.ndim != 1 or metres.ndim != 1 or pixels.size != metres.size or pixels.size == 0:
        raise ValueError("pixel and metric distances must be non-empty equal-length sequences")
    if np.any(pixels <= 0) or np.any(metres <= 0):
        raise ValueError("all calibration distances must be positive")
    ppm = float(np.dot(metres, pixels) / np.dot(metres, metres))
    residuals = pixels - ppm * metres
    return CalibrationResult(ppm, tuple(float(v) for v in residuals), float(np.sqrt(np.mean(residuals ** 2))))
