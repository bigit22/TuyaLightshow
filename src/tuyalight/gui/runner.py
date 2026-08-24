"""Manage the background lightshow subprocess and non-blocking LED cleanup."""

from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

from tuyalight.config import AppConfig
from tuyalight.device import TuyaLED


class EngineRunner:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._process: subprocess.Popen | None = None
        self.stats = {"fps": 0, "ping": 0.0}

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def pid(self) -> int | None:
        return self._process.pid if self.is_running else None

    def start(self) -> None:
        if self.is_running:
            return

        self.stats = {"fps": 0, "ping": 0.0}
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        is_frozen = getattr(sys, "frozen", False)

        cmd = [
            sys.executable,
            "run" if is_frozen else "-m",
        ]
        if not is_frozen:
            cmd.append("tuyalight")
            cmd.append("run")

        cmd.extend(["--background", "-c", str(self.config_path)])

        # Запускаем движок и цепляемся к его консоли
        self._process = subprocess.Popen(
            cmd,
            creationflags=flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Построчное чтение
        )

        # Поток для чтения статистики
        threading.Thread(target=self._monitor_stdout, daemon=True).start()

    def _monitor_stdout(self) -> None:
        """Читает JSON-логи от движка и обновляет self.stats."""
        if not self._process or not self._process.stdout:
            return

        for line in iter(self._process.stdout.readline, ""):
            if not line:
                break
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    self.stats["fps"] = data.get("fps", 0)
                    self.stats["ping"] = data.get("ping", 0.0)
                except Exception:
                    pass

    def stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

        threading.Thread(target=self.turn_off_leds, daemon=True).start()

    def turn_off_leds(self) -> None:
        try:
            if not self.config_path.exists():
                return
            cfg = AppConfig.load(str(self.config_path))
            with TuyaLED(
                cfg.device.device_id,
                cfg.device.ip,
                cfg.device.local_key,
                cfg.device.version,
            ) as led:
                led.close()
        except Exception:
            pass
