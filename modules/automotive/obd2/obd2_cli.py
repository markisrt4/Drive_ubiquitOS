import argparse
import sys
import time

from modules.automotive.obd2.elm327_client import Elm327Client
from modules.automotive.obd2.obd2_errors import Obd2CommandError, Obd2ConnectionError
from modules.automotive.obd2.obd2_manager import Obd2Manager


def fmt_float(value: float | None, precision: int = 1) -> str:
    if value is None:
        return "None"

    return f"{value:.{precision}f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read live OBD-II telemetry.")
    parser.add_argument("--port", default="/dev/rfcomm0")
    parser.add_argument("--baud", type=int, default=38400)
    parser.add_argument("--rate", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    client = Elm327Client(port=args.port, baud=args.baud)
    manager = Obd2Manager(client)

    try:
        manager.connect()
    except Obd2ConnectionError as ex:
        print(f"ERROR: {ex}", file=sys.stderr)
        return 1

    try:
        while True:
            try:
                state = manager.read_state()
            except Obd2CommandError as ex:
                print(f"WARNING: {ex}", file=sys.stderr)
                time.sleep(args.rate)
                continue

            print(
                f"{state.timestamp.strftime('%H:%M:%S')} | "
                f"RPM={state.rpm} | "
                f"Speed={fmt_float(state.speed_mph)} mph | "
                f"Boost={fmt_float(state.boost_psi)} psi | "
                f"MAP={state.map_kpa} kPa | "
                f"BARO={state.baro_kpa} kPa | "
                f"Throttle={fmt_float(state.throttle_pct)}% | "
                f"Pedal={fmt_float(state.accelerator_pedal_pct)}% | "
                f"Load={fmt_float(state.engine_load_pct)}% | "
                f"MAF={fmt_float(state.maf_gps, 2)} g/s | "
                f"Coolant={fmt_float(state.coolant_temp_f)}°F | "
                f"IAT={fmt_float(state.intake_temp_f)}°F | "
                f"Fuel={fmt_float(state.fuel_level_pct)}% | "
                f"Voltage={fmt_float(state.control_voltage, 2)}V"
            )

            time.sleep(args.rate)

    except KeyboardInterrupt:
        print()
        return 0

    finally:
        manager.disconnect()


if __name__ == "__main__":
    raise SystemExit(main())
