"""Glass-styled QCheckBox."""

from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QWidget

from tuyalight.gui.theme import CHECKBOX_QSS


class GlassCheckBox(QCheckBox):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet(CHECKBOX_QSS)
