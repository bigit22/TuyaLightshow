"""Load/save config.toml for the GUI layer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

try:
    import tomli_w
except ModuleNotFoundError:
    tomli_w = None


DEFAULT_CONFIG: dict[str, Any] = {
    "device": {"device_id": "", "ip": "", "local_key": "", "version": 3.5},
    "audio": {
        "sample_rate": 44100,
        "buffer_size": 512,
        "bass_freq_min": 20,
        "bass_freq_max": 140,
    },
    "effect": {
        "gamma": 2.8,
        "low_cutoff": 0.08,
        "bass_dominance": 0.30,
        "min_peak_floor": 0.015,
        "smoothing": 0.25,
        "dynamic_color": True,
        "hue_low": 40,
        "hue_high": 280,
        "target_fps": 30,  # <-- ДОБАВИЛИ СЮДА
    },
}


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
    with path.open("rb") as f:
        data = tomllib.load(f)
    merged = {k: dict(v) for k, v in DEFAULT_CONFIG.items()}
    for section, values in data.items():
        merged.setdefault(section, {})
        merged[section].update(values)
    return merged


def save_config(path: Path, data: dict[str, Any]) -> None:
    if tomli_w is not None:
        with path.open("wb") as f:
            tomli_w.dump(data, f)
        return
    _write_toml_fallback(path, data)


def _write_toml_fallback(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []
    for section, values in data.items():
        lines.append(f"[{section}]")
        for k, v in values.items():
            if isinstance(v, bool):
                lines.append(f"{k} = {'true' if v else 'false'}")
            elif isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            else:
                lines.append(f"{k} = {v}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
