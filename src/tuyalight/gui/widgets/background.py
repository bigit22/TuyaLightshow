"""Animated aurora-style background (static-looking, gently flowing)."""

from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget

from tuyalight.gui.theme import PALETTE


class AuroraBackground(QWidget):
    """Living gradient background with floating colored blobs."""

    _FRAME_INTERVAL_MS = 33  # ~30 FPS

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._t = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self._FRAME_INTERVAL_MS)

    def _tick(self) -> None:
        self._t += 0.008
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # base vertical gradient
        base = QLinearGradient(0, 0, 0, self.height())
        base.setColorAt(0, PALETTE.bg_top)
        base.setColorAt(1, PALETTE.bg_bottom)
        p.fillRect(self.rect(), base)

        # floating light blobs
        w, h = self.width(), self.height()
        blobs = (
            (
                w * (0.30 + 0.15 * math.sin(self._t)),
                h * (0.25 + 0.10 * math.cos(self._t * 0.7)),
                QColor(255, 100, 200, 90),
            ),
            (
                w * (0.70 + 0.12 * math.cos(self._t * 0.9)),
                h * (0.40 + 0.15 * math.sin(self._t * 1.1)),
                QColor(100, 150, 255, 100),
            ),
            (
                w * (0.50 + 0.20 * math.sin(self._t * 0.5)),
                h * (0.80 + 0.08 * math.cos(self._t)),
                QColor(180, 100, 255, 80),
            ),
        )

        radius = min(w, h) * 0.55
        p.setPen(Qt.PenStyle.NoPen)
        for cx, cy, color in blobs:
            rg = QRadialGradient(QPointF(cx, cy), radius)
            rg.setColorAt(0, color)
            fade = QColor(color)
            fade.setAlpha(0)
            rg.setColorAt(1, fade)
            p.setBrush(rg)
            p.drawEllipse(QPointF(cx, cy), radius, radius)
