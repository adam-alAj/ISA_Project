"""Reusable desktop UI components for app pages."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", actions: list[QWidget] | None = None, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 16)
        top = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("PageTitle")
        top.addWidget(title_label)
        top.addStretch(1)
        for action in actions or []:
            top.addWidget(action)
        root.addLayout(top)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("PageSubtitle")
            root.addWidget(subtitle_label)


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(10)


class SectionTitle(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", "section")


class StatusChip(QFrame):
    STATE_LABELS = {
        "idle": "Idle",
        "running": "Running",
        "paused": "Paused",
        "stopped": "Stopped",
        "error": "Error",
        "complete": "Complete",
    }

    def __init__(self, state: str = "idle", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 4, 10, 4)
        row.setSpacing(8)
        self.dot = QLabel("●")
        self.dot.setProperty("variant", "muted")
        self.label = QLabel("")
        row.addWidget(self.dot)
        row.addWidget(self.label)
        self.set_state(state)

    def set_state(self, state: str) -> None:
        label = self.STATE_LABELS.get(state, state.title())
        self.label.setText(label)


class MetricTile(Card):
    def __init__(self, label: str, value: str = "—", unit: str = "", parent=None):
        super().__init__(parent)
        self.layout.setContentsMargins(12, 10, 12, 10)
        self.name = QLabel(label)
        self.name.setProperty("variant", "muted")
        self.value = QLabel(value)
        self.value.setProperty("variant", "section")
        self.unit = QLabel(unit)
        self.unit.setProperty("variant", "muted")
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.value)
        if unit:
            self.layout.addWidget(self.unit)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class EmptyState(Card):
    def __init__(self, message: str, action_text: str | None = None, parent=None):
        super().__init__(parent)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text = QLabel(message)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setProperty("variant", "muted")
        self.layout.addWidget(text)
        self.action = None
        if action_text:
            self.action = QPushButton(action_text)
            self.action.setProperty("variant", "primary")
            self.layout.addWidget(self.action)


class Banner(QFrame):
    def __init__(self, kind: str = "info", text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        self.label = QLabel(text)
        row.addWidget(self.label)
        self.set_kind(kind)

    def set_kind(self, kind: str) -> None:
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_text(self, text: str) -> None:
        self.label.setText(text)
