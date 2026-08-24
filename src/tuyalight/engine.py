import sys
import threading
import time
import warnings

import numpy as np
import soundcard as sc
from tuyalight.config import AppConfig
from tuyalight.device import TuyaLED

warnings.filterwarnings("ignore", category=RuntimeWarning)


class LightshowEngine:
    def __init__(self, config: AppConfig):
        self.cfg = config
        self.shared_state = {
            "target_v": 0,
            "target_h": self.cfg.effect.hue_low,
            "ping_ms": 0.0,
            "running": True,
        }

    def _network_worker(self, led: TuyaLED) -> None:
        last_v, last_h = -1, -1

        while self.shared_state["running"]:
            v = self.shared_state["target_v"]
            h = self.shared_state["target_h"]

            if (
                abs(v - last_v) >= 8
                or (v == 0 and last_v != 0)
                or (v > 100 and abs(h - last_h) > 5)
            ):
                t_send = time.perf_counter()
                try:
                    led.set_hsv(h=h, s=1000, v=v)
                    self.shared_state["ping_ms"] = (time.perf_counter() - t_send) * 1000.0
                    last_v, last_h = v, h
                except Exception:
                    pass

            time.sleep(0.002)

    def run(self, background: bool = False) -> None:
        try:
            speaker = sc.default_speaker()
            mic = sc.get_microphone(speaker.id, include_loopback=True)
        except Exception as e:
            if not background:
                sys.stdout.write(f"Audio error: {e}\n")
            return

        if not background:
            sys.stdout.write(f"Capture: {speaker.name}\n")
            sys.stdout.write(f"Running... Smoothing: {self.cfg.effect.smoothing}\n\n")
            sys.stdout.flush()

        b_lo = max(
            1,
            int(
                self.cfg.audio.bass_freq_min
                * self.cfg.audio.buffer_size
                / self.cfg.audio.sample_rate
            ),
        )
        b_hi = max(
            b_lo + 1,
            int(
                np.ceil(
                    self.cfg.audio.bass_freq_max
                    * self.cfg.audio.buffer_size
                    / self.cfg.audio.sample_rate
                )
            ),
        )

        peak_bass = self.cfg.effect.min_peak_floor
        current_v = 0.0
        current_h = float(self.cfg.effect.hue_low)

        frame_times = []

        with TuyaLED(
            self.cfg.device.device_id,
            self.cfg.device.ip,
            self.cfg.device.local_key,
            self.cfg.device.version,
        ) as led:
            net_thread = threading.Thread(target=self._network_worker, args=(led,), daemon=True)
            net_thread.start()

            with mic.recorder(samplerate=self.cfg.audio.sample_rate, channels=1) as rec:
                try:
                    while True:
                        data = rec.record(numframes=self.cfg.audio.buffer_size)
                        spectrum = np.abs(
                            np.fft.rfft(data[:, 0] * np.hanning(self.cfg.audio.buffer_size))
                        )

                        raw_bass = np.mean(spectrum[b_lo:b_hi])
                        total_energy = np.mean(spectrum[1:128]) + 1e-8
                        bass_share = raw_bass / total_energy

                        peak_bass = max(peak_bass * 0.988, raw_bass, self.cfg.effect.min_peak_floor)
                        norm_bass = np.clip(raw_bass / peak_bass, 0.0, 1.0)

                        if (
                            self.cfg.effect.bass_dominance > 0
                            and bass_share < self.cfg.effect.bass_dominance
                        ):
                            norm_bass *= (bass_share / self.cfg.effect.bass_dominance) ** 2

                        if norm_bass < self.cfg.effect.low_cutoff:
                            shaped_bass = 0.0
                        else:
                            adjusted = (norm_bass - self.cfg.effect.low_cutoff) / (
                                1.0 - self.cfg.effect.low_cutoff
                            )
                            shaped_bass = adjusted**self.cfg.effect.gamma

                        target_v = shaped_bass * 1000.0
                        current_v += (target_v - current_v) * self.cfg.effect.smoothing
                        v_int = int(current_v)
                        self.shared_state["target_v"] = v_int

                        if (
                            self.cfg.effect.dynamic_color
                            and raw_bass > (peak_bass * 0.1)
                            and v_int > 50
                        ):
                            p_lo, p_hi = 1, 5
                            energies = spectrum[p_lo:p_hi]
                            sum_e = np.sum(energies) + 1e-9
                            centroid = np.sum(np.arange(p_lo, p_hi) * energies) / sum_e

                            pitch_norm = np.clip((centroid - p_lo) / (p_hi - p_lo - 1.0), 0.0, 1.0)
                            target_hue = self.cfg.effect.hue_low + pitch_norm * (
                                self.cfg.effect.hue_high - self.cfg.effect.hue_low
                            )
                            current_h += (target_hue - current_h) * (
                                self.cfg.effect.smoothing * 0.8
                            )

                        self.shared_state["target_h"] = int(current_h)

                        if not background:
                            now = time.perf_counter()
                            frame_times.append(now)
                            frame_times = [t for t in frame_times if now - t <= 1.0]

                            bar = "█" * int((v_int / 1000.0) * 20)
                            line = f"\rBASS: [{bar:<20}] {v_int:4d}/1000 | Hue: {int(current_h):3d} | {len(frame_times):2d} FPS | Ping: {self.shared_state['ping_ms']:4.1f}ms "
                            sys.stdout.write(line)
                            sys.stdout.flush()

                except KeyboardInterrupt:
                    self.shared_state["running"] = False
                    if not background:
                        sys.stdout.write("\nStopped.\n")
                        sys.stdout.flush()
