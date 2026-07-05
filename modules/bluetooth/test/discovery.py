# requires apt packages bluez python3-pip
# & pip bleak

import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover(timeout=15)
    for d in devices:
        print(d.address, d.name, d.rssi)

asyncio.run(main())
