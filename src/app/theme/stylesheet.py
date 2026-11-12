"""Build application stylesheet from semantic tokens."""

from __future__ import annotations

from src.app.theme.tokens import FONT_FAMILY, RADII, SPACING, TYPE_SCALE, ThemeTokens


def build_stylesheet(t: ThemeTokens) -> str:
    return f"""
    * {{
        color: {t.text};
        font-family: {FONT_FAMILY};
        font-size: {TYPE_SCALE['body']}px;
    }}

    QMainWindow, QWidget {{
        background: {t.bg};
        color: {t.text};
    }}

    #Sidebar {{
        background: {t.sidebar_bg};
        border-right: 1px solid {t.border};
    }}

    #SidebarBrandTitle {{
        color: {t.sidebar_text};
        font-weight: 700;
        font-size: {TYPE_SCALE['section_title']}px;
    }}

    #Sidebar QListWidget {{
        background: transparent;
        color: {t.sidebar_text};
        border: 0;
        outline: none;
    }}

    #Sidebar QListWidget::item {{
        padding: {SPACING['md']}px;
        margin: {SPACING['xs']}px {SPACING['sm']}px;
        border-radius: {RADII['md']}px;
    }}

    #Sidebar QListWidget::item:selected {{
        background: {t.sidebar_active};
    }}

    #PageTitle {{
        font-size: {TYPE_SCALE['page_title']}px;
        font-weight: 700;
        color: {t.text};
        background: transparent;
    }}

    #PageSubtitle {{
        font-size: {TYPE_SCALE['body']}px;
        color: {t.text_muted};
        background: transparent;
    }}

    #Card {{
        background: {t.surface};
        border: 1px solid {t.border};
        border-radius: {RADII['lg']}px;
    }}

    QPushButton {{
        background: {t.surface_alt};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: {RADII['sm']}px;
        padding: 8px 14px;
        min-height: 32px;
    }}

    QPushButton:hover {{
        background: {t.surface};
    }}

    QPushButton:pressed {{
        background: {t.surface_alt};
    }}

    QPushButton[variant='primary'] {{
        background: {t.primary};
        color: {t.on_primary};
        border-color: {t.primary};
        font-weight: 600;
    }}

    QPushButton[variant='primary']:hover {{
        background: {t.primary_hover};
        border-color: {t.primary_hover};
    }}

    QPushButton[variant='primary']:pressed {{
        background: {t.primary_pressed};
        border-color: {t.primary_pressed};
    }}

    QPushButton[variant='danger'] {{
        background: {t.danger};
        color: {t.on_primary};
        border-color: {t.danger};
    }}

    QPushButton:focus, QToolButton:focus, QLineEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus,
    QListWidget:focus, QTableView:focus {{
        border: 2px solid {t.focus_ring};
        outline: none;
    }}

    QLabel[variant='muted'] {{
        color: {t.text_muted};
    }}

    QLabel[variant='section'] {{
        font-size: {TYPE_SCALE['section_title']}px;
        font-weight: 600;
    }}

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QPlainTextEdit {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: {RADII['sm']}px;
        padding: 6px 8px;
        selection-background-color: {t.primary};
    }}

    QComboBox QAbstractItemView,
    QListWidget,
    QTableView,
    QTreeView,
    QListView {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        alternate-background-color: {t.surface_alt};
    }}

    QHeaderView::section {{
        background: {t.surface_alt};
        color: {t.text};
        border: 0;
        border-right: 1px solid {t.border};
        border-bottom: 1px solid {t.border};
        padding: 6px;
        font-weight: 600;
    }}

    QProgressBar {{
        background: {t.surface_alt};
        border: 1px solid {t.border};
        border-radius: {RADII['sm']}px;
        text-align: center;
        color: {t.text};
    }}

    QProgressBar::chunk {{
        background: {t.primary};
        border-radius: {RADII['sm']}px;
    }}

    QTabBar::tab {{
        background: {t.surface_alt};
        border: 1px solid {t.border};
        border-bottom: 0;
        padding: 8px 12px;
        margin-right: 4px;
        border-top-left-radius: {RADII['sm']}px;
        border-top-right-radius: {RADII['sm']}px;
    }}

    QTabBar::tab:selected {{
        background: {t.surface};
    }}

    QStatusBar {{
        background: {t.surface};
        border-top: 1px solid {t.border};
    }}

    QToolTip {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
        padding: 6px;
    }}

    QMenu {{
        background: {t.surface};
        color: {t.text};
        border: 1px solid {t.border};
    }}

    QMenu::item:selected {{
        background: {t.surface_alt};
    }}

    QScrollBar:vertical {{
        background: {t.surface_alt};
        width: 12px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {t.border};
        border-radius: 6px;
        min-height: 24px;
    }}

    QScrollBar:horizontal {{
        background: {t.surface_alt};
        height: 12px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background: {t.border};
        border-radius: 6px;
        min-width: 24px;
    }}
    """
