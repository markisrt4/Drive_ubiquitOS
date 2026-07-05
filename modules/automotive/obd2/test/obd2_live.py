import time
import serial


PORT = "/dev/rfcomm0"
BAUD = 38400


def send_cmd(ser: serial.Serial, cmd: str, delay: float = 0.25) -> str:
    ser.reset_input_buffer()
    ser.write((cmd + "\r").encode("ascii"))
    ser.flush()
    time.sleep(delay)
    return ser.read_all().decode("ascii", errors="replace")


def extract_response(raw: str, pid: str) -> str | None:
    cleaned = (
        raw.replace(" ", "")
        .replace("\r", "")
        .replace("\n", "")
        .replace(">", "")
        .upper()
    )

    expected = "41" + pid[2:]
    idx = cleaned.find(expected)

    if idx < 0:
        return None

    return cleaned[idx:]


def byte_at(resp: str, index: int) -> int:
    return int(resp[index:index + 2], 16)


def read_pid(ser: serial.Serial, pid: str) -> str | None:
    raw = send_cmd(ser, pid)
    return extract_response(raw, pid)


def setup_adapter(ser: serial.Serial) -> None:
    for cmd in ["ATZ", "ATE0", "ATL0", "ATS0", "ATH1", "ATSP0"]:
        raw = send_cmd(ser, cmd, 0.6)
        print(f"{cmd}: {raw!r}")


def main() -> None:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        setup_adapter(ser)

        print()
        print("Reading live OBD-II data. Ctrl+C to stop.")
        print()

        while True:
            rpm = None
            speed_mph = None
            map_kpa = None
            baro_kpa = None
            boost_psi = None
            throttle_pct = None

            rpm_resp = read_pid(ser, "010C")
            if rpm_resp and len(rpm_resp) >= 8:
                a = byte_at(rpm_resp, 4)
                b = byte_at(rpm_resp, 6)
                rpm = int(((a * 256) + b) / 4)

            speed_resp = read_pid(ser, "010D")
            if speed_resp and len(speed_resp) >= 6:
                speed_kph = byte_at(speed_resp, 4)
                speed_mph = speed_kph * 0.621371

            map_resp = read_pid(ser, "010B")
            if map_resp and len(map_resp) >= 6:
                map_kpa = byte_at(map_resp, 4)

            baro_resp = read_pid(ser, "0133")
            if baro_resp and len(baro_resp) >= 6:
                baro_kpa = byte_at(baro_resp, 4)

            if map_kpa is not None and baro_kpa is not None:
                boost_psi = (map_kpa - baro_kpa) * 0.145038

            throttle_resp = read_pid(ser, "0111")
            if throttle_resp and len(throttle_resp) >= 6:
                throttle_pct = byte_at(throttle_resp, 4) * 100.0 / 255.0

            print(
                f"RPM={rpm} | "
                f"Speed={speed_mph:.1f} mph | " if speed_mph is not None else f"RPM={rpm} | Speed=None | ",
                end="",
            )

            print(
                f"MAP={map_kpa} kPa | "
                f"BARO={baro_kpa} kPa | "
                f"Boost={boost_psi:.1f} psi | " if boost_psi is not None else f"MAP={map_kpa} | BARO={baro_kpa} | Boost=None | ",
                end="",
            )

            print(
                f"Throttle={throttle_pct:.1f}%"
                if throttle_pct is not None
                else "Throttle=None"
            )

            time.sleep(0.5)


if __name__ == "__main__":
    main()
