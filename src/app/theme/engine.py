"""Theme application engine for palette + stylesheet + title bar sync."""

from __future__ import annotations

import ctypes
import platform
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontDatabase, QPalette, QGuiApplication
from PySide6.QtWidgets import QApplication

from src.app.theme.stylesheet import build_stylesheet
from src.app.theme.tokens import TOKENS, ThemeTokens


def _qcolor(hex_color: str) -> QColor:
    return QColor(hex_color)


def _apply_font(app: QApplication) -> None:
    font_path = Path(__file__).resolve().parents[3] / "assets" / "fonts" / "DejaVuSans.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))


def build_palette(tokens: ThemeTokens) -> QPalette:
    palette = QPalette()
    window = _qcolor(tokens.bg)
    base = _qcolor(tokens.surface)
    alt = _qcolor(tokens.surface_alt)
    text = _qcolor(tokens.text)
    muted = _qcolor(tokens.text_muted)
    button = _qcolor(tokens.surface_alt)
    highlight = _qcolor(tokens.primary)
    highlighted = _qcolor(tokens.on_primary)
    border = _qcolor(tokens.border)

    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
        palette.setColor(group, QPalette.ColorRole.Window, window)
        palette.setColor(group, QPalette.ColorRole.WindowText, text)
        palette.setColor(group, QPalette.ColorRole.Base, base)
        palette.setColor(group, QPalette.ColorRole.AlternateBase, alt)
        palette.setColor(group, QPalette.ColorRole.ToolTipBase, base)
        palette.setColor(group, QPalette.ColorRole.ToolTipText, text)
        palette.setColor(group, QPalette.ColorRole.Text, text)
        palette.setColor(group, QPalette.ColorRole.Button, button)
        palette.setColor(group, QPalette.ColorRole.ButtonText, text)
        palette.setColor(group, QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, highlighted)
        palette.setColor(group, QPalette.ColorRole.Light, border)
        palette.setColor(group, QPalette.ColorRole.Midlight, border)
        palette.setColor(group, QPalette.ColorRole.Dark, border)
        palette.setColor(group, QPalette.ColorRole.Mid, border)
        palette.setColor(group, QPalette.ColorRole.Shadow, QColor("#000000"))
        palette.setColor(group, QPalette.ColorRole.Link, _qcolor(tokens.info))
        palette.setColor(group, QPalette.ColorRole.LinkVisited, _qcolor(tokens.primary_pressed))
        palette.setColor(group, QPalette.ColorRole.PlaceholderText, muted)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, _qcolor(tokens.border))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, _qcolor(tokens.text_muted))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, _qcolor(tokens.surface_alt))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, _qcolor(tokens.surface_alt))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, _qcolor(tokens.bg))

    return palette


def _set_qt_color_scheme(mode: str) -> None:
    color_scheme_enum = getattr(Qt, "ColorScheme", None)
    style_hints = QGuiApplication.styleHints()
    if color_scheme_enum is None or not hasattr(style_hints, "setColorScheme"):
        return
    style_hints.setColorScheme(color_scheme_enum.Dark if mode == "dark" else color_scheme_enum.Light)


def _set_windows_title_bar_theme(window, mode: str) -> None:
    if platform.system() != "Windows":
        return
    try:
        hwnd = int(window.winId())
        value = ctypes.c_int(1 if mode == "dark" else 0)
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            ctypes.c_uint(DWMWA_USE_IMMERSIVE_DARK_MODE),
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        return


def apply_theme(app: QApplication, mode: str, *, window=None) -> None:
    mode_key = mode if mode in TOKENS else "light"
    tokens = TOKENS[mode_key]
    app.setStyle("Fusion")
    _apply_font(app)
    _set_qt_color_scheme(mode_key)
    app.setPalette(build_palette(tokens))
    app.setStyleSheet(build_stylesheet(tokens))
    if window is not None:
        _set_windows_title_bar_theme(window, mode_key)
