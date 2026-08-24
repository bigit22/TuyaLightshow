from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class DeviceConfig(BaseModel):
    device_id: str
    ip: str
    local_key: str
    version: float = 3.5


class AudioConfig(BaseModel):
    sample_rate: int = 44100
    buffer_size: int = 512
    bass_freq_min: int = 20
    bass_freq_max: int = 140


class EffectConfig(BaseModel):
    gamma: float = 2.8
    low_cutoff: float = 0.08
    bass_dominance: float = 0.30
    min_peak_floor: float = 0.015
    smoothing: float = 0.25
    dynamic_color: bool = True
    hue_low: int = 40
    hue_high: int = 280
    target_fps: int = 30  # Лимит отправки пакетов


class AppConfig(BaseSettings):
    device: DeviceConfig
    audio: AudioConfig = AudioConfig()
    effect: EffectConfig = EffectConfig()

    @classmethod
    def load(cls, path: str = "config.toml") -> "AppConfig":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with p.open("rb") as f:
            data = tomllib.load(f)
        return cls(**data)
