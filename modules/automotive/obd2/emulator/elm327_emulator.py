import argparse
import math
import os
import pty
import random
import select
import time


def hex_byte(value: int) -> str:
    return f"{max(0, min(255, value)):02X}"


def hex_word(value: int) -> str:
    value = max(0, min(65535, value))
    return f"{(value >> 8) & 0xFF:02X}{value & 0xFF:02X}"


class Elm327Emulator:
    def __init__(self) -> None:
        self._start = time.monotonic()

    def handle(self, command: str) -> str:
        cmd = command.strip().upper().replace(" ", "")

        if not cmd:
            return ">"

        if cmd == "ATZ":
            return "ELM327 v1.5\r\r>"

        if cmd in {"ATI", "ATE0", "ATL0", "ATS0", "ATH0", "ATH1", "ATSP0"}:
            return "OK\r\r>"

        if cmd == "0100":
            return "7E8064100BE3EA813\r\r>"

        if cmd.startswith("01"):
            return self._mode01(cmd[2:])

        return "NO DATA\r\r>"

    def _mode01(self, pid: str) -> str:
        t = time.monotonic() - self._start

        rpm = int(850 + 1200 * (0.5 + 0.5 * math.sin(t / 2.0)))
        speed_kph = int(45 + 35 * (0.5 + 0.5 * math.sin(t / 5.0)))
        throttle = int(20 + 55 * (0.5 + 0.5 * math.sin(t / 1.6)))
        load = int(25 + 60 * (0.5 + 0.5 * math.sin(t / 2.5)))

        baro_kpa = 98
        map_kpa = int(35 + 95 * (throttle / 100.0))
        coolant_c = int(88 + random.uniform(-1.5, 1.5))
        iat_c = int(30 + random.uniform(-2.0, 2.0))
        maf = int((rpm * map_kpa) / 180.0)
        fuel = 152
        voltage_mv = int(14200 + random.uniform(-150, 150))

        if pid == "04":
            return f"7E8034104{hex_byte(load)}\r\r>"
        if pid == "05":
            return f"7E8034105{hex_byte(coolant_c + 40)}\r\r>"
        if pid == "0B":
            return f"7E803410B{hex_byte(map_kpa)}\r\r>"
        if pid == "0C":
            return f"7E804410C{hex_word(rpm * 4)}\r\r>"
        if pid == "0D":
            return f"7E803410D{hex_byte(speed_kph)}\r\r>"
        if pid == "0F":
            return f"7E803410F{hex_byte(iat_c + 40)}\r\r>"
        if pid == "10":
            return f"7E8044110{hex_word(maf)}\r\r>"
        if pid == "11":
            return f"7E8034111{hex_byte(throttle)}\r\r>"
        if pid == "2F":
            return f"7E803412F{hex_byte(fuel)}\r\r>"
        if pid == "33":
            return f"7E8034133{hex_byte(baro_kpa)}\r\r>"
        if pid == "42":
            return f"7E8044142{hex_word(voltage_mv)}\r\r>"
        if pid == "49":
            return f"7E8034149{hex_byte(throttle)}\r\r>"

        return "NO DATA\r\r>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple ELM327/OBD-II serial emulator.")
    parser.add_argument("--link", default="/tmp/obd_emulator")
    args = parser.parse_args()

    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)

    if os.path.exists(args.link):
        os.unlink(args.link)

    os.symlink(slave_name, args.link)

    print(f"ELM327 emulator running.")
    print(f"Serial device: {slave_name}")
    print(f"Symlink:       {args.link}")
    print()
    print("Run client with:")
    print(f"  python3 -m modules.automotive.obd2.obd2_cli --port {args.link}")
    print()

    emulator = Elm327Emulator()
    buffer = bytearray()

    try:
        while True:
            readable, _, _ = select.select([master_fd], [], [], 0.1)

            if master_fd not in readable:
                continue

            data = os.read(master_fd, 1024)

            for byte in data:
                if byte in (ord("\r"), ord("\n")):
                    command = buffer.decode("ascii", errors="replace")
                    buffer.clear()

                    response = emulator.handle(command)
                    os.write(master_fd, response.encode("ascii"))
                else:
                    buffer.append(byte)

    except KeyboardInterrupt:
        print("\nEmulator stopped.")
        return 0

    finally:
        if os.path.exists(args.link):
            os.unlink(args.link)

        os.close(master_fd)
        os.close(slave_fd)


if __name__ == "__main__":
    raise SystemExit(main())
