"""Lightweight guard against UI/graphics imports in core packages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_DIRS = ("environment", "robot", "algorithms", "coverage", "simulation")
FORBIDDEN = re.compile(r"^\s*(?:from|import)\s+(?:PySide6|matplotlib)(?:\.|\s|$)", re.MULTILINE | re.IGNORECASE)


def main() -> int:
    """Return nonzero if a core module directly imports a UI/graphics package."""
    violations: list[str] = []
    for package in CORE_DIRS:
        for path in (ROOT / "src" / package).glob("*.py"):
            if FORBIDDEN.search(path.read_text(encoding="utf-8")):
                violations.append(str(path.relative_to(ROOT)))
    if violations:
        print("Forbidden UI/graphics imports found:")
        print("\n".join(violations))
        return 1
    print("Core package import boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

