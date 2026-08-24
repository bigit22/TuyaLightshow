"""Glass primary/secondary buttons."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget

from tuyalight.gui.theme import (
    BUTTON_PRIMARY_QSS,
    BUTTON_SECONDARY_QSS,
    METRICS,
)


class GlassButton(QPushButton):
    def __init__(
        self,
        text: str,
        primary: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setMinimumHeight(METRICS.button_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(BUTTON_PRIMARY_QSS if primary else BUTTON_SECONDARY_QSS)
