from __future__ import annotations

import asyncio

from bleak import BleakScanner


async def main() -> None:
    devices = await BleakScanner.discover(timeout=10.0)
    for device in devices:
        name = device.name or ""
        if name.startswith("LEDDMX"):
            print(f"{device.address}  {name}")


if __name__ == "__main__":
    asyncio.run(main())
