"""Image import helpers. Source files are read without modifying them."""

from pathlib import Path

import numpy as np


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def load_image(path: str | Path) -> np.ndarray:
    """Load a PNG/JPEG as a BGR NumPy image using OpenCV."""
    source = Path(path)
    if source.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        raise ValueError(f"Unsupported image type: {source.suffix}")
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError("OpenCV is required to load floor-plan images") from exc
    flags = cv2.IMREAD_COLOR | getattr(cv2, "IMREAD_IGNORE_ORIENTATION", 128)
    image = cv2.imread(str(source), flags)
    if image is None:
        raise ValueError(f"Could not read image: {source}")
    return image


def read_exif_orientation(path: str | Path) -> int:
    """Read EXIF orientation for `preprocess_image`; default to normal orientation."""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Pillow is required to read EXIF orientation") from exc
    with Image.open(path) as image:
        return int(image.getexif().get(274, 1))


def pdf_to_image(path: str | Path, page: int = 0, dpi: int = 200) -> np.ndarray:
    """Optionally rasterize a PDF page; not used for the current JPEG map."""
    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Optional PyMuPDF is required for PDF rasterization") from exc
    document = fitz.open(str(path))
    if page < 0 or page >= document.page_count:
        raise IndexError("PDF page index is out of range")
    pixmap = document[page].get_pixmap(dpi=dpi, alpha=False)
    return np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
