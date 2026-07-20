"""NetworkManager router backend."""

from __future__ import annotations

import json
import subprocess
from ipaddress import ip_interface
from typing import Any

from ..router_if import RouterIf
from ..router_status import RouterStatus


class NetworkManagerRouterError(RuntimeError):
    """Raised when a NetworkManager router operation fails."""


class NetworkManagerRouter(RouterIf):
    """Controls an existing NetworkManager hotspot connection."""

    def __init__(
        self,
        connection_name: str,
        wan_interface: str,
        lan_interface: str,
    ) -> None:
        if not connection_name.strip():
            raise ValueError("connection_name cannot be empty")

        if not wan_interface.strip():
            raise ValueError("wan_interface cannot be empty")

        if not lan_interface.strip():
            raise ValueError("lan_interface cannot be empty")

        self._connection_name = connection_name
        self._wan_interface = wan_interface
        self._lan_interface = lan_interface

    @property
    def connection_name(self) -> str:
        """Return the managed NetworkManager connection name."""

        return self._connection_name

    @property
    def wan_interface(self) -> str:
        """Return the configured WAN interface name."""

        return self._wan_interface

    @property
    def lan_interface(self) -> str:
        """Return the configured LAN interface name."""

        return self._lan_interface

    def start_router(self) -> None:
        """Activate the configured NetworkManager connection."""

        if self.is_running():
            return

        self._run(
            [
                "nmcli",
                "connection",
                "up",
                self._connection_name,
            ]
        )

    def stop_router(self) -> None:
        """Deactivate the configured NetworkManager connection."""

        if not self.is_running():
            return

        self._run(
            [
                "nmcli",
                "connection",
                "down",
                self._connection_name,
            ]
        )

    def restart_router(self) -> None:
        """Restart the configured NetworkManager connection."""

        if self.is_running():
            self.stop_router()

        self.start_router()

    def get_status(self) -> RouterStatus:
        """Return the current NetworkManager router status."""

        connection_exists = self._connection_exists()

        if not connection_exists:
            raise NetworkManagerRouterError(
                "NetworkManager connection does not exist: "
                f"{self._connection_name}"
            )

        active_connection = self._find_active_connection()
        running = active_connection is not None

        ssid = self._read_connection_ssid()
        addresses = self._read_interface_addresses(
            self._lan_interface
        )
        internet_connected = self._has_default_route(
            self._wan_interface
        )

        return RouterStatus(
            running=running,
            connection_name=self._connection_name,
            wan_interface=self._wan_interface,
            lan_interface=self._lan_interface,
            ssid=ssid,
            internet_connected=internet_connected,
            addresses=addresses,
        )

    def _connection_exists(self) -> bool:
        result = self._run(
            [
                "nmcli",
                "--terse",
                "--fields",
                "NAME",
                "connection",
                "show",
            ],
            check=False,
        )

        if result.returncode != 0:
            return False

        connection_names = {
            self._unescape_nmcli_value(line.strip())
            for line in result.stdout.splitlines()
            if line.strip()
        }

        return self._connection_name in connection_names

    def _find_active_connection(self) -> dict[str, str] | None:
        result = self._run(
            [
                "nmcli",
                "--terse",
                "--fields",
                "NAME,DEVICE,TYPE",
                "connection",
                "show",
                "--active",
            ],
            check=False,
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            fields = self._split_nmcli_line(line)

            if len(fields) != 3:
                continue

            name, device, connection_type = fields

            if (
                name == self._connection_name
                and device == self._lan_interface
            ):
                return {
                    "name": name,
                    "device": device,
                    "type": connection_type,
                }

        return None

    def _read_connection_ssid(self) -> str | None:
        result = self._run(
            [
                "nmcli",
                "--get-values",
                "802-11-wireless.ssid",
                "connection",
                "show",
                self._connection_name,
            ],
            check=False,
        )

        if result.returncode != 0:
            return None

        ssid = result.stdout.strip()
        return ssid or None

    def _read_interface_addresses(
        self,
        interface_name: str,
    ) -> tuple[Any, ...]:
        result = self._run(
            [
                "ip",
                "-json",
                "address",
                "show",
                "dev",
                interface_name,
            ],
            check=False,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return tuple()

        try:
            interface_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return tuple()

        addresses = []

        for entry in interface_data:
            for address_info in entry.get("addr_info", []):
                local = address_info.get("local")
                prefix_length = address_info.get("prefixlen")

                if local is None or prefix_length is None:
                    continue

                try:
                    addresses.append(
                        ip_interface(
                            f"{local}/{prefix_length}"
                        )
                    )
                except ValueError:
                    continue

        return tuple(addresses)

    def _has_default_route(self, interface_name: str) -> bool:
        result = self._run(
            [
                "ip",
                "-json",
                "route",
                "show",
                "default",
            ],
            check=False,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return False

        try:
            routes = json.loads(result.stdout)
        except json.JSONDecodeError:
            return False

        return any(
            route.get("dev") == interface_name
            for route in routes
        )

    @staticmethod
    def _split_nmcli_line(line: str) -> list[str]:
        fields: list[str] = []
        current: list[str] = []
        escaped = False

        for character in line:
            if escaped:
                current.append(character)
                escaped = False
                continue

            if character == "\\":
                escaped = True
                continue

            if character == ":":
                fields.append("".join(current))
                current = []
                continue

            current.append(character)

        fields.append("".join(current))
        return fields

    @staticmethod
    def _unescape_nmcli_value(value: str) -> str:
        characters: list[str] = []
        escaped = False

        for character in value:
            if escaped:
                characters.append(character)
                escaped = False
                continue

            if character == "\\":
                escaped = True
                continue

            characters.append(character)

        if escaped:
            characters.append("\\")

        return "".join(characters)

    @staticmethod
    def _run(
        command: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except FileNotFoundError as exc:
            raise NetworkManagerRouterError(
                f"Required command is not installed: {command[0]}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise NetworkManagerRouterError(
                f"Command timed out: {' '.join(command)}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""

            message = (
                f"Command failed with exit code "
                f"{exc.returncode}: {' '.join(command)}"
            )

            if stderr:
                message = f"{message}: {stderr}"

            raise NetworkManagerRouterError(message) from exc
