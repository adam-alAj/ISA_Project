"""Exercise each P0 dependency and print an individual pass/fail result."""

from __future__ import annotations

import importlib.metadata
import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Callable


def run_check(name: str, check: Callable[[], None]) -> bool:
    """Run one dependency check and display its result."""
    try:
        check()
    except Exception as exc:  # smoke test must continue to report every package
        print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return False
    print(f"PASS {name}")
    return True


def main() -> int:
    """Run minimal operations for the requested dependency set."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    results: list[bool] = []

    def pyside_check() -> None:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        assert app is not None

    def opencv_check() -> None:
        import cv2
        import numpy as np

        image = np.zeros((2, 2, 3), dtype=np.uint8)
        assert cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).shape == (2, 2)

    def numpy_check() -> None:
        import numpy as np

        assert int(np.array([1, 2, 3]).sum()) == 6

    def shapely_check() -> None:
        from shapely.geometry import Point

        assert Point(0, 0).buffer(1).area > 3

    def matplotlib_check() -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "smoke.png"
            figure, axes = plt.subplots()
            axes.plot([0, 1], [0, 1])
            figure.savefig(target)
            plt.close(figure)
            assert target.is_file() and target.stat().st_size > 0

    def pandas_check() -> None:
        import pandas as pd

        frame = pd.DataFrame({"step": [1, 2]})
        assert int(frame["step"].sum()) == 3

    def reportlab_check() -> None:
        from reportlab.pdfgen import canvas

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "smoke.pdf"
            pdf = canvas.Canvas(str(target))
            pdf.drawString(72, 720, "Smart Vacuum smoke test")
            pdf.save()
            assert target.is_file() and target.stat().st_size > 0

    def ursina_check() -> None:
        import ursina  # noqa: F401

    def docx_check() -> None:
        from docx import Document

        assert Document is not None

    def networkx_check() -> None:
        import networkx as nx

        assert nx.number_of_nodes(nx.path_graph(2)) == 2

    def pytest_check() -> None:
        import pytest

        assert pytest.__version__

    def ruff_check() -> None:
        import ruff  # noqa: F401

    checks = [
        ("PySide6 QApplication (offscreen)", pyside_check),
        ("opencv-python image operation", opencv_check),
        ("numpy operation", numpy_check),
        ("shapely geometry", shapely_check),
        ("matplotlib PNG output", matplotlib_check),
        ("pandas DataFrame", pandas_check),
        ("reportlab one-page PDF", reportlab_check),
        ("ursina import", ursina_check),
        ("python-docx import", docx_check),
        ("networkx graph", networkx_check),
        ("pytest import", pytest_check),
        ("ruff import", ruff_check),
    ]
    for name, check in checks:
        results.append(run_check(name, check))

    for distribution in ("PySide6", "opencv-python", "numpy", "shapely", "matplotlib", "pandas", "ursina", "reportlab", "python-docx", "networkx", "pytest", "ruff"):
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = "NOT INSTALLED"
        print(f"VERSION {distribution} {version}")

    passed = sum(results)
    print(f"RESULT {passed}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
