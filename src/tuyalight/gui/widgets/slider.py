"""Magnetic slider with click-to-jump and exact step snapping."""

from __future__ import annotations

import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from tuyalight.gui.theme import (
    LABEL_SLIDER_NAME_QSS,
    LABEL_SLIDER_VALUE_QSS,
    SLIDER_QSS,
)


class _JumpSlider(QSlider):
    """Handle jumps exactly to the clicked position."""

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is not None and event.button() == Qt.MouseButton.LeftButton and self.width() > 0:
            ratio = event.position().x() / self.width()
            ratio = max(0.0, min(1.0, ratio))
            val = self.minimum() + ratio * (self.maximum() - self.minimum())
            self.setValue(round(val))
            event.accept()

        if event is not None:
            super().mousePressEvent(event)


class GlassSlider(QWidget):
    """Labeled slider with strict step snapping and formatted value."""

    def __init__(
        self,
        label: str,
        minimum: float,
        maximum: float,
        value: float,
        step: float = 0.01,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = float(minimum)
        self._max = float(maximum)
        self._step = float(step)

        # exact number of magnetic stops
        self._n = round((self._max - self._min) / self._step)
        # decimals for display
        self._decimals = 0 if step >= 1 else max(0, round(-math.log10(step)))

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(5)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(label)
        self._name_lbl.setStyleSheet(LABEL_SLIDER_NAME_QSS)

        self._value_lbl = QLabel()
        self._value_lbl.setStyleSheet(LABEL_SLIDER_VALUE_QSS)
        self._value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(self._name_lbl)
        header.addWidget(self._value_lbl)
        root.addLayout(header)

        self._slider = _JumpSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, self._n)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(max(1, self._n // 10))
        self._slider.setTracking(True)
        self._slider.setStyleSheet(SLIDER_QSS)

        init = max(0, min(self._n, round((float(value) - self._min) / self._step)))
        self._slider.setValue(init)
        self._slider.valueChanged.connect(self._sync_label)
        self._sync_label(init)

        root.addWidget(self._slider)

    # ---- API ----

    def value(self) -> float:
        real = self._min + self._slider.value() * self._step
        return round(real, self._decimals + 2)

    # ---- internals ----

    def _sync_label(self, index: int) -> None:
        real = self._min + index * self._step
        real = round(real, self._decimals + 2)
        if self._decimals == 0:
            self._value_lbl.setText(str(round(real)))
        else:
            self._value_lbl.setText(f"{real:.{self._decimals}f}")
