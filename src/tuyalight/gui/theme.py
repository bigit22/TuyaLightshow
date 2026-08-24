"""Design tokens: colors, fonts, sizes. Single source of truth."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from PyQt6.QtGui import QColor, QFont


@dataclass(frozen=True)
class Palette:
    # Background gradient
    bg_top: QColor = field(default_factory=lambda: QColor(15, 20, 40))
    bg_bottom: QColor = field(default_factory=lambda: QColor(40, 15, 60))

    # Accents
    accent_blue: QColor = field(default_factory=lambda: QColor(120, 180, 255))
    accent_purple: QColor = field(default_factory=lambda: QColor(200, 140, 255))

    # Text
    text: QColor = field(default_factory=lambda: QColor(240, 245, 255))
    text_dim: QColor = field(default_factory=lambda: QColor(200, 210, 230))
    text_muted: QColor = field(default_factory=lambda: QColor(180, 200, 220))
    text_accent: str = "#78b4ff"

    # Glass
    glass_border: QColor = field(default_factory=lambda: QColor(255, 255, 255, 45))
    glass_fill_top: QColor = field(default_factory=lambda: QColor(255, 255, 255, 35))
    glass_fill_bot: QColor = field(default_factory=lambda: QColor(255, 255, 255, 12))


@dataclass(frozen=True)
class Metrics:
    window_min_w: int = 520
    window_min_h: int = 780
    panel_radius: int = 22
    control_radius: int = 12
    button_radius: int = 14
    button_height: int = 42
    input_height: int = 38
    root_margin: int = 24
    root_spacing: int = 18
    panel_margin: int = 20
    panel_spacing: int = 14


PALETTE = Palette()
METRICS = Metrics()


def default_font() -> QFont:
    family = "Segoe UI" if sys.platform == "win32" else "SF Pro Display"
    font = QFont(family, 10)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    return font


# ---------- QSS building blocks (reused across widgets) ----------

LINE_EDIT_QSS = """
QLineEdit {
    background: rgba(255, 255, 255, 25);
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 12px;
    padding: 6px 14px;
    color: #f0f5ff;
    font-size: 13px;
    selection-background-color: rgba(120, 180, 255, 120);
}
QLineEdit:focus {
    border: 1px solid rgba(120, 180, 255, 180);
    background: rgba(255, 255, 255, 40);
}
"""

BUTTON_PRIMARY_QSS = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(120, 180, 255, 220),
        stop:1 rgba(200, 140, 255, 220));
    border: 1px solid rgba(255, 255, 255, 80);
    border-radius: 14px;
    color: white;
    font-size: 14px;
    font-weight: 600;
    padding: 8px 20px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(140, 200, 255, 240),
        stop:1 rgba(220, 160, 255, 240));
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(100, 160, 235, 220),
        stop:1 rgba(180, 120, 235, 220));
}
"""

BUTTON_SECONDARY_QSS = """
QPushButton {
    background: rgba(255, 255, 255, 30);
    border: 1px solid rgba(255, 255, 255, 60);
    border-radius: 14px;
    color: #f0f5ff;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 20px;
}
QPushButton:hover  { background: rgba(255, 255, 255, 50); }
QPushButton:pressed{ background: rgba(255, 255, 255, 20); }
"""

CHECKBOX_QSS = """
QCheckBox {
    color: #d0d8ea;
    font-size: 13px;
    spacing: 10px;
    background: transparent;
}
QCheckBox::indicator {
    width: 20px; height: 20px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 25);
    border: 1px solid rgba(255, 255, 255, 60);
}
QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(120, 180, 255, 220),
        stop:1 rgba(200, 140, 255, 220));
    border: 1px solid rgba(255, 255, 255, 100);
}
"""

SLIDER_QSS = """
QSlider { background: transparent; }
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(255, 255, 255, 30);
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(120, 180, 255, 220),
        stop:1 rgba(200, 140, 255, 220));
    border-radius: 3px;
}
QSlider::add-page:horizontal {
    background: rgba(255, 255, 255, 18);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        stop:0 rgba(255, 255, 255, 255),
        stop:1 rgba(220, 230, 255, 255));
    width: 18px; height: 18px;
    margin: -6px 0;
    border-radius: 9px;
    border: 1px solid rgba(120, 180, 255, 180);
}
QSlider::handle:horizontal:hover {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        stop:0 rgba(255, 255, 255, 255),
        stop:1 rgba(180, 210, 255, 255));
}
"""

LABEL_TITLE_QSS = (
    "color: white; font-size: 32px; font-weight: 700; "
    "letter-spacing: -1px; background: transparent;"
)
LABEL_SUBTITLE_QSS = "color: rgba(200, 210, 230, 180); font-size: 13px; background: transparent;"
LABEL_SECTION_QSS = (
    "color: rgba(200, 210, 230, 200); font-size: 11px; font-weight: 700; "
    "letter-spacing: 2px; background: transparent;"
)
LABEL_STATUS_QSS = "color: rgba(180, 200, 220, 200); font-size: 12px; background: transparent;"
LABEL_SLIDER_NAME_QSS = (
    "color: #d0d8ea; font-size: 12px; font-weight: 500; background: transparent;"
)
LABEL_SLIDER_VALUE_QSS = (
    "color: #78b4ff; font-size: 12px; font-weight: 700; background: transparent;"
)
