from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor

from src.app.theme.tokens import TOKENS


@dataclass(frozen=True)
class Pair:
    fg: str
    bg: str
    min_ratio: float


def _luminance(c: QColor) -> float:
    def chan(v: int) -> float:
        x = v / 255.0
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4

    return 0.2126 * chan(c.red()) + 0.7152 * chan(c.green()) + 0.0722 * chan(c.blue())


def _contrast(fg: str, bg: str) -> float:
    a = _luminance(QColor(fg))
    b = _luminance(QColor(bg))
    lighter = max(a, b)
    darker = min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def _pairs(theme: str) -> list[Pair]:
    t = TOKENS[theme]
    return [
        Pair(t.text, t.bg, 4.5),
        Pair(t.text, t.surface, 4.5),
        Pair(t.text_muted, t.bg, 4.5),
        Pair(t.on_primary, t.primary, 4.5),
        Pair(t.text, t.surface_alt, 4.5),
        Pair(t.sidebar_text, t.sidebar_bg, 4.5),
        Pair(t.text, t.border, 3.0),
        Pair(t.focus_ring, t.bg, 3.0),
        Pair(t.danger, t.surface, 3.0),
        Pair(t.warning, t.surface, 3.0),
        Pair(t.success, t.surface, 3.0),
        Pair(t.info, t.surface, 3.0),
    ]


def test_wcag_pairs_light_and_dark():
    failures = []
    for theme in ("light", "dark"):
        for pair in _pairs(theme):
            ratio = _contrast(pair.fg, pair.bg)
            if ratio < pair.min_ratio:
                failures.append((theme, pair, ratio))
    assert not failures, f"Contrast failures: {failures}"
