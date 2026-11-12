from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}")


def _scan(path: Path) -> list[str]:
    hits = []
    for file in path.rglob("*.py"):
        if "src/app/theme" in file.as_posix():
            continue
        text = file.read_text(encoding="utf-8")
        if HEX_RE.search(text):
            hits.append(str(file.relative_to(ROOT)))
    return hits


def test_no_hardcoded_hex_outside_theme():
    targets = [ROOT / "src" / "app", ROOT / "src" / "visualization" / "two_d"]
    hits = []
    for target in targets:
        hits.extend(_scan(target))
    assert not hits, f"Hard-coded hex colors detected outside theme package: {sorted(set(hits))}"
