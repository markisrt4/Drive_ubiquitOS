import time
import serial

from modules.automotive.obd2.obd2_errors import (
    Obd2CommandError,
    Obd2ConnectionError,
)


class Elm327Client:
    def __init__(self, port: str = "/dev/rfcomm0", baud: int = 38400) -> None:
        self._port = port
        self._baud = baud
        self._serial: serial.Serial | None = None

    def connect(self) -> None:
        try:
            self._serial = serial.Serial(self._port, self._baud, timeout=1)
            self.initialize()
        except (serial.SerialException, OSError) as ex:
            self.disconnect()
            raise Obd2ConnectionError(
                f"Unable to connect to ELM327 on {self._port}. "
                "Check Bluetooth/rfcomm, adapter power, and whether another app is connected."
            ) from ex

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            finally:
                self._serial = None

    def initialize(self) -> None:
        for cmd in ["ATZ", "ATE0", "ATL0", "ATS0", "ATH1", "ATSP0"]:
            self.send_command(cmd, delay=0.6)

    def send_command(self, command: str, delay: float = 0.25) -> str:
        if self._serial is None:
            raise Obd2ConnectionError("ELM327 client is not connected")

        try:
            self._serial.reset_input_buffer()
            self._serial.write((command + "\r").encode("ascii"))
            self._serial.flush()
            time.sleep(delay)
            return self._read_available()
        except (serial.SerialException, OSError) as ex:
            raise Obd2CommandError(f"OBD command failed: {command}") from ex

    def read_mode01_pid(self, pid: str) -> str | None:
        raw = self.send_command(f"01{pid}")
        return self._extract_mode01_response(raw, pid)

    def _read_available(self) -> str:
        if self._serial is None:
            raise Obd2ConnectionError("ELM327 client is not connected")

        data = bytearray()
        deadline = time.monotonic() + 1.0

        while time.monotonic() < deadline:
            chunk = self._serial.read(1)

            if chunk:
                data.extend(chunk)
                if chunk == b">":
                    break
            else:
                break

        return bytes(data).decode("ascii", errors="replace")

    @staticmethod
    def _extract_mode01_response(raw: str, pid: str) -> str | None:
        cleaned = (
            raw.replace(" ", "")
            .replace("\r", "")
            .replace("\n", "")
            .replace(">", "")
            .upper()
        )

        expected = f"41{pid.upper()}"
        index = cleaned.find(expected)

        if index < 0:
            return None

        return cleaned[index:]
