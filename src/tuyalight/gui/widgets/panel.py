"""Rounded translucent glass panel with soft shadow and top highlight."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QWidget

from tuyalight.gui.theme import METRICS, PALETTE


class GlassPanel(QFrame):
    def __init__(self, parent: QWidget | None = None, radius: int | None = None) -> None:
        super().__init__(parent)
        self._radius = radius if radius is not None else METRICS.panel_radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)

        # glass fill
        fill = QLinearGradient(0, 0, 0, self.height())
        fill.setColorAt(0, PALETTE.glass_fill_top)
        fill.setColorAt(1, PALETTE.glass_fill_bot)
        p.fillPath(path, fill)

        # top highlight (upper 50%)
        p.setClipPath(path)
        hi_rect = QRectF(rect.x(), rect.y(), rect.width(), rect.height() * 0.5)
        hi = QLinearGradient(0, hi_rect.top(), 0, hi_rect.bottom())
        hi.setColorAt(0, QColor(255, 255, 255, 45))
        hi.setColorAt(1, QColor(255, 255, 255, 0))
        p.fillRect(hi_rect, hi)
        p.setClipping(False)

        # border
        p.setPen(QPen(PALETTE.glass_border, 1.2))
        p.drawPath(path)
