from __future__ import annotations

import socket
from types import TracebackType

import tinytuya


class TuyaLED:
    def __init__(self, device_id: str, ip: str, local_key: str, version: float = 3.5):
        self.device_id = device_id
        self.ip = ip
        self.local_key = local_key
        self.version = version
        self._device: tinytuya.OutletDevice | None = None
        self._connect()

    def _connect(self) -> None:
        """Подключение с отключением буферизации Windows."""
        try:
            dev = tinytuya.OutletDevice(self.device_id, self.ip, self.local_key)
            dev.set_version(self.version)
            dev.set_socketPersistent(True)
            dev.set_socketTimeout(0.4)

            if hasattr(dev, "connect"):
                dev.connect()

            sock = getattr(dev, "socket", None)
            if sock:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

            self._device = dev
        except Exception:
            self._device = None

    def __enter__(self) -> TuyaLED:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def set_hsv(self, h: int, s: int = 1000, v: int = 1000) -> bool:
        if self._device is None:
            self._connect()
        return self._send(h, s, v)

    def close(self) -> None:
        """Мгновенное выключение без подвисаний."""
        dev = self._device
        if dev is None:
            return

        try:
            payload = dev.generate_payload(tinytuya.CONTROL, {"20": False})
            dev.send(payload)
        except Exception:
            pass

        self._force_socket_reset()

    def _send(self, h: int, s: int, v: int) -> bool:
        dev = self._device
        if dev is None:
            return False

        hex_data = f"0{int(h):04x}{int(s):04x}{int(v):04x}00000000"
        payload = dev.generate_payload(
            tinytuya.CONTROL, {"20": True, "21": "music", "27": hex_data}
        )
        try:
            dev.send(payload)
            return True
        except Exception:
            self._force_socket_reset()
            return False

    def _force_socket_reset(self) -> None:
        dev = self._device
        if dev is not None:
            sock = getattr(dev, "socket", None)
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except Exception:
                    pass

            try:
                dev.close()
            except Exception:
                pass

        self._device = None
