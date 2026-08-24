"""Main GUI window."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from tuyalight.gui.config_io import load_config, save_config
from tuyalight.gui.runner import EngineRunner
from tuyalight.gui.theme import (
    LABEL_SECTION_QSS,
    LABEL_STATUS_QSS,
    LABEL_SUBTITLE_QSS,
    LABEL_TITLE_QSS,
    METRICS,
)
from tuyalight.gui.widgets import (
    AuroraBackground,
    GlassButton,
    GlassCheckBox,
    GlassLineEdit,
    GlassPanel,
    GlassSlider,
)


class MainWindow(QWidget):
    def __init__(self, config_path: str = "config.toml") -> None:
        super().__init__()
        self.config_path = Path(config_path)
        self.cfg: dict[str, Any] = load_config(self.config_path)
        self.runner = EngineRunner(self.config_path)

        self.setWindowTitle("TuyaLight ✦ Liquid Control")
        self.setMinimumSize(METRICS.window_min_w, METRICS.window_min_h)

        self._bg = AuroraBackground(self)
        self._build_ui()

        # Таймер для обновления FPS/Ping
        self._stat_timer = QTimer(self)
        self._stat_timer.timeout.connect(self._update_stats)
        self._stat_timer.start(500)  # Раз в полсекунды

    def _update_stats(self) -> None:
        if self.runner.is_running:
            fps = self.runner.stats.get("fps", 0)
            ping = self.runner.stats.get("ping", 0.0)
            self.status.setText(f"● Running | LED FPS: {fps} | Ping: {ping} ms")
        elif self.status.text().startswith("●"):
            # Если процесс упал сам по себе
            self.status.setText("Stopped (Engine exited)")
            self.btn_run.setText("▶  Start Lightshow")

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(
            METRICS.root_margin,
            METRICS.root_margin,
            METRICS.root_margin,
            METRICS.root_margin,
        )
        root.setSpacing(METRICS.root_spacing)

        root.addLayout(self._build_header())
        root.addWidget(self._build_device_panel())
        root.addWidget(self._build_effect_panel())
        root.addLayout(self._build_actions())
        root.addWidget(self._build_status())
        root.addStretch(1)

    def _build_header(self) -> QVBoxLayout:
        title = QLabel("TuyaLight")
        title.setStyleSheet(LABEL_TITLE_QSS)

        subtitle = QLabel("Music-reactive lightshow")
        subtitle.setStyleSheet(LABEL_SUBTITLE_QSS)

        header = QVBoxLayout()
        header.setSpacing(2)
        header.addWidget(title)
        header.addWidget(subtitle)
        return header

    def _build_device_panel(self) -> GlassPanel:
        panel = GlassPanel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            METRICS.panel_margin,
            METRICS.panel_margin - 2,
            METRICS.panel_margin,
            METRICS.panel_margin - 2,
        )
        layout.setSpacing(10)
        layout.addWidget(self._section_label("DEVICE"))

        d = self.cfg["device"]

        self.in_id = GlassLineEdit("Device ID")
        self.in_id.setText(str(d.get("device_id", "")))

        self.in_ip = GlassLineEdit("IP address")
        self.in_ip.setText(str(d.get("ip", "")))

        self.in_key = GlassLineEdit("Local key")
        self.in_key.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.in_key.setText(str(d.get("local_key", "")))

        layout.addWidget(self.in_id)
        layout.addWidget(self.in_ip)
        layout.addWidget(self.in_key)
        return panel

    def _build_effect_panel(self) -> GlassPanel:
        panel = GlassPanel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            METRICS.panel_margin,
            METRICS.panel_margin - 2,
            METRICS.panel_margin,
            METRICS.panel_margin - 2,
        )
        layout.setSpacing(METRICS.panel_spacing)
        layout.addWidget(self._section_label("EFFECT"))

        e = self.cfg["effect"]

        self.sl_gamma = GlassSlider("Gamma", 0.5, 5.0, float(e.get("gamma", 2.8)), 0.1)
        self.sl_cutoff = GlassSlider("Low cutoff", 0.0, 0.5, float(e.get("low_cutoff", 0.08)), 0.01)
        self.sl_bass = GlassSlider(
            "Bass dominance", 0.0, 1.0, float(e.get("bass_dominance", 0.30)), 0.01
        )
        self.sl_floor = GlassSlider(
            "Min peak floor", 0.001, 0.100, float(e.get("min_peak_floor", 0.015)), 0.001
        )
        self.sl_smooth = GlassSlider("Smoothing", 0.05, 1.00, float(e.get("smoothing", 0.25)), 0.01)
        self.sl_fps = GlassSlider("Target FPS", 10, 60, float(e.get("target_fps", 30)), 1)

        row_hue = QHBoxLayout()
        self.sl_hue_lo = GlassSlider("Hue low", 0, 360, float(e.get("hue_low", 40)), 1)
        self.sl_hue_hi = GlassSlider("Hue high", 0, 360, float(e.get("hue_high", 280)), 1)
        row_hue.addWidget(self.sl_hue_lo)
        row_hue.addWidget(self.sl_hue_hi)

        for slider in (
            self.sl_gamma,
            self.sl_cutoff,
            self.sl_bass,
            self.sl_floor,
            self.sl_smooth,
            self.sl_fps,
        ):
            layout.addWidget(slider)

        layout.addLayout(row_hue)

        self.cb_dyn = GlassCheckBox("Dynamic color (pitch → hue)")
        self.cb_dyn.setChecked(bool(e.get("dynamic_color", True)))
        layout.addWidget(self.cb_dyn)

        return panel

    def _build_actions(self) -> QHBoxLayout:
        self.btn_save = GlassButton("Save")
        self.btn_save.clicked.connect(self._on_save)

        self.btn_run = GlassButton("▶  Start Lightshow", primary=True)
        self.btn_run.clicked.connect(self._on_toggle_run)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self.btn_save)
        row.addWidget(self.btn_run, stretch=1)
        return row

    def _build_status(self) -> QLabel:
        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(LABEL_STATUS_QSS)
        return self.status

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_SECTION_QSS)
        return lbl

    def resizeEvent(self, event) -> None:
        self._bg.setGeometry(self.rect())
        self._bg.lower()
        super().resizeEvent(event)

    def closeEvent(self, event) -> None:
        self.runner.stop()
        super().closeEvent(event)

    def _collect(self) -> dict[str, Any]:
        return {
            "device": {
                "device_id": self.in_id.text().strip(),
                "ip": self.in_ip.text().strip(),
                "local_key": self.in_key.text().strip(),
                "version": float(self.cfg["device"].get("version", 3.5)),
            },
            "audio": self.cfg.get("audio", {}),
            "effect": {
                "gamma": float(self.sl_gamma.value()),
                "low_cutoff": float(self.sl_cutoff.value()),
                "bass_dominance": float(self.sl_bass.value()),
                "min_peak_floor": float(self.sl_floor.value()),
                "smoothing": float(self.sl_smooth.value()),
                "target_fps": int(self.sl_fps.value()),
                "dynamic_color": self.cb_dyn.isChecked(),
                "hue_low": int(self.sl_hue_lo.value()),
                "hue_high": int(self.sl_hue_hi.value()),
            },
        }

    def _on_save(self) -> None:
        data = self._collect()
        save_config(self.config_path, data)
        self.cfg = data
        self.status.setText(f"✓ Saved · {self.config_path.name}")

    def _on_toggle_run(self) -> None:
        if self.runner.is_running:
            self.runner.stop()
            self.btn_run.setText("▶  Start Lightshow")
            self.status.setText("Stopped")
            return

        self._on_save()
        try:
            self.runner.start()
            self.btn_run.setText("■  Stop")
        except Exception as exc:
            self.status.setText(f"Error: {exc}")
