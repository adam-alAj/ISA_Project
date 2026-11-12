"""Check package contents and imports for the retained 2D application."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "src", ROOT / "scripts")
FORBIDDEN = re.compile(r"\b(?:ursina|panda3d|simulation_3d|three_d)\b", re.IGNORECASE)


def main() -> int:
    violations = []
    for path in (ROOT / "src" / "visualization", ROOT / "tests"):
        if path.exists():
            for item in path.rglob("*"):
                if item.is_file() and re.search(r"(?:three_d|simulation_3d)", item.name, re.I):
                    violations.append(f"removed module path remains: {item.relative_to(ROOT)}")
    for root in CODE:
        for path in root.rglob("*.py"):
            if path in {Path(__file__).resolve(), ROOT / "scripts" / "check_env.py"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if FORBIDDEN.search(text):
                violations.append(f"removed runtime reference in {path.relative_to(ROOT)}")
    for package in ("ursina", "panda3d"):
        if importlib.util.find_spec(package) is not None:
            violations.append(f"removed import is discoverable: {package}")
    for item in violations:
        print(f"FAIL {item}")
    print(f"RESULT {'FAIL' if violations else 'PASS'}")
    return bool(violations)


if __name__ == "__main__":
    sys.exit(main())
