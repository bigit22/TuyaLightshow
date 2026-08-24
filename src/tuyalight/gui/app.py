"""GUI entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from tuyalight.gui.theme import default_font
from tuyalight.gui.window import MainWindow


def run_gui(config_path: str = "config.toml") -> None:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(sys.argv)

    app.setStyle("Fusion")
    app.setFont(default_font())

    window = MainWindow(config_path=config_path)
    window.show()

    sys.exit(app.exec())
