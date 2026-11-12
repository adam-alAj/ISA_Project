"""Capture Smart Vacuum UI screenshots and basic contrast diagnostics.

This script supports two modes:
1) orchestrator mode (default): spawns worker processes for each
   (color scheme, scale factor) combination.
2) worker mode (--worker): creates one QApplication and captures all pages
   for a fixed scheme/scale at multiple resolutions.

Outputs:
- PNG screenshots for each page and viewport
- JSON and CSV contrast records based on visible text widgets
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QAbstractButton,
    QAbstractSpinBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QTableView,
    QWidget,
)

from src.app.app_controller import AppController
from src.app.main_window import MainWindow


PAGES = (
    (0, "project_home"),
    (1, "map_editor"),
    (2, "robot_configuration"),
    (3, "algorithm_setup"),
    (4, "simulation_2d"),
    (5, "simulation_3d_launcher"),
    (6, "results_dashboard"),
    (7, "report_export"),
)

RESOLUTIONS = (
    (1280, 720),
    (1600, 900),
    (1920, 1080),
)

SCALES = ("1.0", "1.25", "1.5")
SCHEMES = ("light", "dark")
WINDOWS_DARKMODE = {
    "light": "0",
    "dark": "2",
}


@dataclass
class ContrastRecord:
    scheme: str
    scale: str
    resolution: str
    page: str
    widget_class: str
    widget_name: str
    text: str
    fg_hex: str
    bg_hex: str
    ratio: float
    min_required: float
    pass_wcag_aa: bool


def _rel_luminance(channel_255: int) -> float:
    c = channel_255 / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def contrast_ratio(fg: QColor, bg: QColor) -> float:
    l_fg = 0.2126 * _rel_luminance(fg.red()) + 0.7152 * _rel_luminance(fg.green()) + 0.0722 * _rel_luminance(fg.blue())
    l_bg = 0.2126 * _rel_luminance(bg.red()) + 0.7152 * _rel_luminance(bg.green()) + 0.0722 * _rel_luminance(bg.blue())
    lighter = max(l_fg, l_bg)
    darker = min(l_fg, l_bg)
    return (lighter + 0.05) / (darker + 0.05)


def _effective_background(widget: QWidget) -> QColor:
    # Walk up to find a non-transparent window background role.
    node: QWidget | None = widget
    while node is not None:
        col = node.palette().color(node.backgroundRole())
        if col.alpha() > 0:
            return col
        node = node.parentWidget()
    return QColor("#ffffff")


def _is_large_text(widget: QWidget) -> bool:
    f = widget.font()
    size_px = f.pixelSize()
    if size_px <= 0:
        size_px = int(round(f.pointSizeF() * 96.0 / 72.0)) if f.pointSizeF() > 0 else 0
    boldish = f.weight() >= 700
    return size_px >= 24 or (boldish and size_px >= 18)


def _iter_text_widgets(page: QWidget) -> Iterable[QWidget]:
    types = (QLabel, QAbstractButton, QLineEdit, QAbstractSpinBox, QComboBox, QListWidget, QListView, QTableView)
    seen: set[int] = set()
    for cls in types:
        for widget in page.findChildren(cls):
            key = id(widget)
            if key in seen:
                continue
            seen.add(key)
            if not widget.isVisible():
                continue
            if isinstance(widget, QLabel):
                if not widget.text().strip():
                    continue
            elif isinstance(widget, QAbstractButton):
                if not widget.text().strip():
                    continue
            elif isinstance(widget, QLineEdit):
                if not (widget.text().strip() or widget.placeholderText().strip()):
                    continue
            yield widget


def _widget_text(widget: QWidget) -> str:
    if isinstance(widget, QLabel):
        return widget.text().strip()
    if isinstance(widget, QAbstractButton):
        return widget.text().strip()
    if isinstance(widget, QLineEdit):
        return (widget.text() or widget.placeholderText() or "").strip()
    if isinstance(widget, QAbstractSpinBox):
        return widget.text().strip()
    if isinstance(widget, QComboBox):
        return widget.currentText().strip()
    if isinstance(widget, QListWidget):
        return "list"
    if isinstance(widget, QListView):
        return "list_view"
    if isinstance(widget, QTableView):
        return "table"
    return ""


def _set_runtime_color_scheme(app: QApplication, scheme: str) -> None:
    color_scheme_enum = getattr(Qt, "ColorScheme", None)
    style_hints = QGuiApplication.styleHints()
    if color_scheme_enum is None or not hasattr(style_hints, "setColorScheme"):
        return
    if scheme == "dark":
        style_hints.setColorScheme(color_scheme_enum.Dark)
    else:
        style_hints.setColorScheme(color_scheme_enum.Light)


def capture_worker(scheme: str, scale: str, output_root: Path) -> int:
    output_root.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance() or QApplication([])
    _set_runtime_color_scheme(app, scheme)

    controller = AppController(data_root=ROOT / "data")
    window = MainWindow(controller, theme_mode=scheme)
    controller.load_map(ROOT / "data" / "maps" / "department_v1")
    window.show()
    app.processEvents()

    records: list[ContrastRecord] = []

    for width, height in RESOLUTIONS:
        res_label = f"{width}x{height}"
        res_dir = output_root / f"scale_{scale}" / res_label / scheme
        res_dir.mkdir(parents=True, exist_ok=True)

        window.resize(width, height)
        app.processEvents()

        for index, page_name in PAGES:
            window.nav.setCurrentRow(index)
            app.processEvents()
            page = window.stack.currentWidget()
            shot_path = res_dir / f"{page_name}.png"
            page.grab().save(str(shot_path))

            for widget in _iter_text_widgets(page):
                text = _widget_text(widget)
                if not text:
                    continue
                fg = widget.palette().color(widget.foregroundRole())
                bg = _effective_background(widget)
                ratio = contrast_ratio(fg, bg)
                min_required = 3.0 if _is_large_text(widget) else 4.5
                records.append(
                    ContrastRecord(
                        scheme=scheme,
                        scale=scale,
                        resolution=res_label,
                        page=page_name,
                        widget_class=widget.metaObject().className(),
                        widget_name=widget.objectName() or "",
                        text=text.replace("\n", " ")[:120],
                        fg_hex=fg.name(QColor.NameFormat.HexRgb),
                        bg_hex=bg.name(QColor.NameFormat.HexRgb),
                        ratio=round(ratio, 3),
                        min_required=min_required,
                        pass_wcag_aa=ratio >= min_required,
                    )
                )

    json_path = output_root / f"contrast_{scheme}_scale_{scale}.json"
    csv_path = output_root / f"contrast_{scheme}_scale_{scale}.csv"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump([record.__dict__ for record in records], fh, indent=2)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(ContrastRecord.__annotations__.keys()))
        writer.writeheader()
        writer.writerows([record.__dict__ for record in records])

    worst = min(records, key=lambda row: row.ratio) if records else None
    failed = sum(1 for row in records if not row.pass_wcag_aa)
    print(
        json.dumps(
            {
                "scheme": scheme,
                "scale": scale,
                "records": len(records),
                "failed": failed,
                "worst_ratio": worst.ratio if worst else None,
                "worst_widget": worst.text if worst else None,
            }
        )
    )

    window.close()
    app.quit()
    return 0


def orchestrate(output_root: Path) -> int:
    output_root.mkdir(parents=True, exist_ok=True)
    failures = 0

    for scheme in SCHEMES:
        for scale in SCALES:
            env = os.environ.copy()
            env["QT_SCALE_FACTOR"] = scale
            env["QT_QPA_PLATFORM"] = f"windows:darkmode={WINDOWS_DARKMODE[scheme]}"
            cmd = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--scheme",
                scheme,
                "--scale",
                scale,
                "--output",
                str(output_root),
            ]
            print(f"[ui_screenshots] running scheme={scheme} scale={scale}")
            completed = subprocess.run(cmd, env=env, cwd=str(ROOT), check=False)
            if completed.returncode != 0:
                failures += 1

    return 1 if failures else 0


def build_before_after(before_root: Path, after_root: Path, out_root: Path) -> int:
    from PIL import Image, ImageOps, ImageDraw

    out_root.mkdir(parents=True, exist_ok=True)
    count = 0
    for scale in SCALES:
        for width, height in RESOLUTIONS:
            res = f"{width}x{height}"
            for scheme in SCHEMES:
                for _, page_name in PAGES:
                    before = before_root / f"scale_{scale}" / res / scheme / f"{page_name}.png"
                    after = after_root / f"scale_{scale}" / res / scheme / f"{page_name}.png"
                    if not before.exists() or not after.exists():
                        continue
                    lhs = Image.open(before).convert("RGB")
                    rhs = Image.open(after).convert("RGB")
                    max_h = max(lhs.height, rhs.height)
                    lhs = ImageOps.pad(lhs, (lhs.width, max_h), color=(255, 255, 255))
                    rhs = ImageOps.pad(rhs, (rhs.width, max_h), color=(255, 255, 255))
                    canvas = Image.new("RGB", (lhs.width + rhs.width + 8, max_h + 26), (245, 246, 250))
                    draw = ImageDraw.Draw(canvas)
                    draw.text((8, 4), "Before", fill=(15, 23, 42))
                    draw.text((lhs.width + 16, 4), "After", fill=(15, 23, 42))
                    canvas.paste(lhs, (0, 24))
                    canvas.paste(rhs, (lhs.width + 8, 24))
                    out_path = out_root / f"{page_name}__{scheme}__{scale}__{res}.png"
                    canvas.save(out_path)
                    count += 1
    print(f"[ui_screenshots] generated {count} before/after composites")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture UI screenshots and contrast diagnostics")
    parser.add_argument("--worker", action="store_true", help="Run in worker mode")
    parser.add_argument("--scheme", choices=SCHEMES, default="light")
    parser.add_argument("--scale", choices=SCALES, default="1.0")
    parser.add_argument("--output", default=str(ROOT / "docs" / "img" / "ui_before"))
    parser.add_argument("--make-before-after", action="store_true")
    parser.add_argument("--before-root", default=str(ROOT / "docs" / "img" / "ui_before"))
    parser.add_argument("--after-root", default=str(ROOT / "docs" / "img" / "ui_after"))
    parser.add_argument("--before-after-root", default=str(ROOT / "docs" / "img" / "ui_before_after"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.make_before_after:
        return build_before_after(Path(args.before_root), Path(args.after_root), Path(args.before_after_root))
    output_root = Path(args.output)
    if args.worker:
        return capture_worker(args.scheme, args.scale, output_root)
    return orchestrate(output_root)


if __name__ == "__main__":
    raise SystemExit(main())
