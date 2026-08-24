import time

import tinytuya


class TuyaLED:
    def __init__(self, device_id: str, ip: str, local_key: str, version: float = 3.5):
        self._device = tinytuya.OutletDevice(device_id, ip, local_key)
        self._device.set_version(version)
        self._device.set_socketPersistent(True)

    def __enter__(self) -> "TuyaLED":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def set_hsv(self, h: int, s: int = 1000, v: int = 1000) -> None:
        self._send(h, s, v)

    def close(self) -> None:
        try:
            self.set_hsv(0, 1000, 0)
            time.sleep(0.05)
            payload = self._device.generate_payload(tinytuya.CONTROL, {"20": False})
            self._device.send(payload)
            self._device.close()
        except Exception:
            pass

    def _send(self, h: int, s: int, v: int) -> None:
        hex_data = f"0{int(h):04x}{int(s):04x}{int(v):04x}00000000"
        payload = self._device.generate_payload(
            tinytuya.CONTROL, {"20": True, "21": "music", "27": hex_data}
        )
        self._device.send(payload)
