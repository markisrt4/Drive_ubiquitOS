from __future__ import annotations

import argparse
import asyncio

from modules.lighting.leddmx.bluetooth_controller import LedDmxBluetoothController
from modules.lighting.lighting_types import RgbColor


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("address", help="BLE address for LEDDMX controller")
    args = parser.parse_args()

    controller = LedDmxBluetoothController(args.address)
    await controller.connect()
    await controller.set_power(True)
    await controller.set_brightness(60)
    await controller.set_color(RgbColor(255, 0, 0))
    await asyncio.sleep(1)
    await controller.set_color(RgbColor(0, 255, 0))
    await asyncio.sleep(1)
    await controller.set_color(RgbColor(0, 0, 255))
    await controller.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
