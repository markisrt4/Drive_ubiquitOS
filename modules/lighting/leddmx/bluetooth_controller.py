from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from collections.abc import Coroutine
from typing import Any, Final

from modules.lighting.lighting_controller_if import LightingControllerIf
from modules.lighting.lighting_types import CustomPatternMode, RgbColor

from .protocol import LedDmxProtocol

try:
    from bleak import BleakClient
except ImportError:  # pragma: no cover - lets CarSDR import without BLE deps installed
    BleakClient = None  # type: ignore[assignment]


LEDDMX_SERVICE_UUID: Final[str] = "0000ffe0-0000-1000-8000-00805f9b34fb"
LEDDMX_CHARACTERISTIC_UUID: Final[str] = "0000ffe1-0000-1000-8000-00805f9b34fb"


class LedDmxBluetoothController(LightingControllerIf):
    """Persistent LEDDMX BLE controller with its own asyncio event loop.

    Public methods are intentionally synchronous from the UI's perspective: they
    return concurrent.futures.Future objects instead of coroutines. This keeps
    Tkinter out of asyncio and prevents the classic "Lock is bound to a
    different event loop" failure caused by calling asyncio.run() repeatedly.
    """

    def __init__(
        self,
        address: str,
        *,
        write_with_response: bool = False,
        command_delay_seconds: float = 0.05,
        reconnect_delay_seconds: float = 0.25,
    ) -> None:
        if BleakClient is None:
            raise RuntimeError("bleak is not installed. Install with: pip install bleak")

        self._address = address
        self._write_with_response = write_with_response
        self._command_delay_seconds = command_delay_seconds
        self._reconnect_delay_seconds = reconnect_delay_seconds

        self._loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()
        self._closed = False
        self._connected = False

        self._client: BleakClient | None = None
        self._lock: asyncio.Lock | None = None

        self._thread = threading.Thread(
            target=self._run_loop,
            name="CarSDRLedDmxBleLoop",
            daemon=True,
        )
        self._thread.start()
        self._loop_ready.wait(timeout=5.0)

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> Future[None]:
        return self._submit(self._connect())

    def disconnect(self) -> Future[None]:
        return self._submit(self._disconnect())

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        try:
            self.disconnect().result(timeout=2.0)
        except Exception:
            pass

        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    def set_power(self, enabled: bool) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.power(enabled)))

    def set_color(self, color: RgbColor) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.color(color)))

    def set_brightness(self, percent: int) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.brightness(percent)))

    def set_color_temperature(self, percent: int) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.color_temperature(percent)))

    def set_pattern(self, pattern_index: int) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.pattern(pattern_index)))

    def set_music_mode(self, eq_mode: int) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.mic_eq(eq_mode)))

    def set_custom_pattern_mode(self, mode: CustomPatternMode) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.custom_pattern_mode(mode)))

    def set_custom_pattern_direction(self, is_forward: bool) -> Future[None]:
        return self._submit(self._write(LedDmxProtocol.custom_pattern_direction(is_forward)))

    def _submit(self, coroutine: Coroutine[Any, Any, None]) -> Future[None]:
        if self._closed:
            future: Future[None] = Future()
            future.set_exception(RuntimeError("lighting controller is closed"))
            return future

        return asyncio.run_coroutine_threadsafe(coroutine, self._loop)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        self._loop.run_forever()

        # Best effort loop cleanup. Anything left pending is cancelled so Python
        # does not complain during application shutdown like a haunted teapot.
        pending = asyncio.all_tasks(self._loop)
        for task in pending:
            task.cancel()
        if pending:
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self._loop.close()

    async def _ensure_loop_objects(self) -> None:
        if self._client is None:
            self._client = BleakClient(self._address)
        if self._lock is None:
            self._lock = asyncio.Lock()

    async def _connect(self) -> None:
        await self._ensure_loop_objects()
        assert self._client is not None
        assert self._lock is not None

        async with self._lock:
            if not self._client.is_connected:
                await self._client.connect()
            self._connected = bool(self._client.is_connected)

    async def _disconnect(self) -> None:
        await self._ensure_loop_objects()
        assert self._client is not None
        assert self._lock is not None

        async with self._lock:
            if self._client.is_connected:
                await self._client.disconnect()
            self._connected = False

    async def _connect_unlocked(self) -> None:
        await self._ensure_loop_objects()
        assert self._client is not None

        if not self._client.is_connected:
            await self._client.connect()
        self._connected = bool(self._client.is_connected)

    async def _write(self, packet: bytes) -> None:
        await self._ensure_loop_objects()
        assert self._client is not None
        assert self._lock is not None

        async with self._lock:
            await self._connect_unlocked()

            try:
                await self._client.write_gatt_char(
                    LEDDMX_CHARACTERISTIC_UUID,
                    packet,
                    response=self._write_with_response,
                )
            except Exception:
                self._connected = False
                if self._client.is_connected:
                    await self._client.disconnect()

                await asyncio.sleep(self._reconnect_delay_seconds)
                await self._connect_unlocked()
                await self._client.write_gatt_char(
                    LEDDMX_CHARACTERISTIC_UUID,
                    packet,
                    response=self._write_with_response,
                )

            self._connected = bool(self._client.is_connected)
            if self._command_delay_seconds > 0:
                await asyncio.sleep(self._command_delay_seconds)
