"""Validate the supported Python environment and the removed graphics runtime."""

from __future__ import annotations

import importlib.metadata
import sys


REQUIRED = (
    "PySide6", "opencv-python", "numpy", "shapely", "matplotlib", "pandas",
    "reportlab", "pypdf", "jsonschema", "python-docx", "pytest", "pytest-qt",
)
REMOVED = ("ursina", "panda3d")


def main() -> int:
    failures = []
    if sys.version_info[:2] not in {(3, 11), (3, 12)}:
        failures.append(f"Python 3.11 or 3.12 required; found {sys.version.split()[0]}")
    for package in REQUIRED:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"missing required package: {package}")
        else:
            print(f"PASS {package} {version}")
    for package in REMOVED:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            print(f"PASS removed package absent: {package}")
        else:
            failures.append(f"removed package is installed: {package}")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"RESULT {'FAIL' if failures else 'PASS'}")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
