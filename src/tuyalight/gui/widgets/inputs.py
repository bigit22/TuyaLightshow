"""Glass-styled QLineEdit."""

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit, QWidget

from tuyalight.gui.theme import LINE_EDIT_QSS, METRICS


class GlassLineEdit(QLineEdit):
    def __init__(self, placeholder: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(METRICS.input_height)
        self.setStyleSheet(LINE_EDIT_QSS)
