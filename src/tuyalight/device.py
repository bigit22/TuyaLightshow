import socket
from typing import Self

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
            self._device = tinytuya.OutletDevice(self.device_id, self.ip, self.local_key)
            self._device.set_version(self.version)
            self._device.set_socketPersistent(True)
            self._device.set_socketTimeout(0.4)

            # Форсируем создание сокета и настраиваем TCP_NODELAY
            if hasattr(self._device, "connect"):
                self._device.connect()

            if hasattr(self._device, "socket") and self._device.socket:
                sock = self._device.socket
                # Отключаем задержки Нейгла — шлем пакеты мгновенно
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                # Уменьшаем буфер отправки, чтобы Винда не заталкивала туда мертвые кадры
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
        except Exception:
            self._device = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def set_hsv(self, h: int, s: int = 1000, v: int = 1000) -> bool:
        """Возвращает True если кадр реально ушел в сеть, иначе False."""
        if not self._device:
            self._connect()
        return self._send(h, s, v)

    def close(self) -> None:
        """Мгновенное выключение без подвисаний."""
        if not self._device:
            return

        try:
            payload = self._device.generate_payload(tinytuya.CONTROL, {"20": False})
            self._device.send(payload)
        except Exception:
            pass

        self._force_socket_reset()

    def _send(self, h: int, s: int, v: int) -> bool:
        if not self._device:
            return False

        hex_data = f"0{int(h):04x}{int(s):04x}{int(v):04x}00000000"
        payload = self._device.generate_payload(
            tinytuya.CONTROL, {"20": True, "21": "music", "27": hex_data}
        )
        try:
            self._device.send(payload)
            return True
        except Exception:
            # Сокет умер — мгновенно сбрасываем и переподключаемся
            self._force_socket_reset()
            return False

    def _force_socket_reset(self) -> None:
        try:
            if hasattr(self._device, "socket") and self._device.socket:
                self._device.socket.shutdown(socket.SHUT_RDWR)
                self._device.socket.close()
        except Exception:
            pass

        try:
            if self._device:
                self._device.close()
        except Exception:
            pass
        finally:
            self._device = None
