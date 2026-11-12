from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QAbstractButton, QAbstractSpinBox, QComboBox, QLabel, QWidget

from src.app.app_controller import AppController
from src.app.main_window import MainWindow
from src.app.theme import apply_theme


def _lum(channel: int) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _contrast(fg: QColor, bg: QColor) -> float:
    l1 = 0.2126 * _lum(fg.red()) + 0.7152 * _lum(fg.green()) + 0.0722 * _lum(fg.blue())
    l2 = 0.2126 * _lum(bg.red()) + 0.7152 * _lum(bg.green()) + 0.0722 * _lum(bg.blue())
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _bg(widget: QWidget) -> QColor:
    node: QWidget | None = widget
    while node is not None:
        col = node.palette().color(node.backgroundRole())
        if col.alpha() > 0:
            return col
        node = node.parentWidget()
    return QColor("#FFFFFF")


def _is_large(widget: QWidget) -> bool:
    f = widget.font()
    px = f.pixelSize()
    if px <= 0 and f.pointSizeF() > 0:
        px = int(round(f.pointSizeF() * 96.0 / 72.0))
    if px <= 0:
        return False
    return px >= 24 or (f.weight() >= 700 and px >= 18)


def _text(widget: QWidget) -> str:
    if isinstance(widget, QLabel):
        return widget.text().strip()
    if isinstance(widget, QAbstractButton):
        return widget.text().strip()
    if isinstance(widget, QAbstractSpinBox):
        return widget.text().strip()
    if isinstance(widget, QComboBox):
        return widget.currentText().strip()
    return ""


def test_ui_visibility_across_pages_and_themes(qtbot, tmp_path):
    controller = AppController(data_root=tmp_path / "data")
    window = MainWindow(controller)
    qtbot.addWidget(window)
    window.show()

    failures: list[str] = []
    for mode in ("light", "dark"):
        apply_theme(QApplication.instance(), mode, window=window)
        qtbot.wait(20)
        for i in range(window.stack.count()):
            window.nav.setCurrentRow(i)
            qtbot.wait(10)
            page = window.stack.currentWidget()
            for widget in page.findChildren(QWidget):
                if not isinstance(widget, (QLabel, QAbstractButton, QAbstractSpinBox, QComboBox)):
                    continue
                if not widget.isVisible():
                    continue
                txt = _text(widget)
                if not txt:
                    continue
                ratio = _contrast(widget.palette().color(widget.foregroundRole()), _bg(widget))
                required = 3.0 if _is_large(widget) else 4.5
                if ratio < required:
                    failures.append(f"{mode} page={i} widget={widget.metaObject().className()} text={txt!r} ratio={ratio:.3f} req={required:.1f}")

    assert not failures, "Visibility contrast failures:\n" + "\n".join(failures[:40])
