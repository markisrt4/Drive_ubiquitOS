import time
import serial


PORT = "/dev/rfcomm0"
BAUD = 9600


def send_cmd(ser: serial.Serial, cmd: str, delay: float = 0.15) -> str:
    ser.write((cmd + "\r").encode("ascii"))
    time.sleep(delay)
    raw = ser.read_all().decode("ascii", errors="ignore")
    return raw.replace("\r", "").replace("\n", "").replace(">", "").strip()


def clean_response(resp: str) -> str:
    return resp.replace(" ", "").upper()


def read_pid(ser: serial.Serial, pid: str) -> str | None:
    resp = clean_response(send_cmd(ser, pid))
    expected = "41" + pid[2:]

    idx = resp.find(expected)
    if idx < 0:
        return None

    return resp[idx:]


def parse_hex_byte(value: str, index: int) -> int:
    return int(value[index:index + 2], 16)


def main() -> None:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        for cmd in ["ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP0"]:
            print(cmd, "=>", send_cmd(ser, cmd, 0.5))

        print("Reading OBD data. Ctrl+C to stop.")

        while True:
            rpm_resp = read_pid(ser, "010C")
            speed_resp = read_pid(ser, "010D")
            map_resp = read_pid(ser, "010B")
            baro_resp = read_pid(ser, "0133")
            throttle_resp = read_pid(ser, "0111")

            rpm = None
            speed_mph = None
            map_kpa = None
            baro_kpa = None
            boost_psi = None
            throttle_pct = None

            if rpm_resp and len(rpm_resp) >= 8:
                a = parse_hex_byte(rpm_resp, 4)
                b = parse_hex_byte(rpm_resp, 6)
                rpm = int(((a * 256) + b) / 4)

            if speed_resp and len(speed_resp) >= 6:
                speed_kph = parse_hex_byte(speed_resp, 4)
                speed_mph = speed_kph * 0.621371

            if map_resp and len(map_resp) >= 6:
                map_kpa = parse_hex_byte(map_resp, 4)

            if baro_resp and len(baro_resp) >= 6:
                baro_kpa = parse_hex_byte(baro_resp, 4)

            if map_kpa is not None and baro_kpa is not None:
                boost_psi = (map_kpa - baro_kpa) * 0.145038

            if throttle_resp and len(throttle_resp) >= 6:
                throttle_raw = parse_hex_byte(throttle_resp, 4)
                throttle_pct = throttle_raw * 100.0 / 255.0

            print(
                f"RPM={rpm} | "
                f"Speed={speed_mph:.1f} mph | " if speed_mph is not None else f"RPM={rpm} | Speed=None | ",
                end="",
            )

            print(
                f"MAP={map_kpa} kPa | "
                f"BARO={baro_kpa} kPa | "
                f"Boost={boost_psi:.1f} psi | " if boost_psi is not None else f"MAP={map_kpa} kPa | BARO={baro_kpa} kPa | Boost=None | ",
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
