"""Linux network interface discovery."""

from __future__ import annotations

import json
import re
import subprocess
from ipaddress import ip_interface
from pathlib import Path
from typing import Any

from .network_interface import (
    InterfaceBus,
    InterfaceCapabilities,
    InterfaceKind,
    InterfaceState,
    NetworkInterface,
)


class InterfaceProbeError(RuntimeError):
    """Raised when interface discovery cannot be completed."""


class InterfaceProbe:
    """Discovers Linux network interfaces and driver capabilities."""

    SYS_CLASS_NET = Path("/sys/class/net")

    def discover(self) -> list[NetworkInterface]:
        """Return all network interfaces discovered on the host."""

        if not self.SYS_CLASS_NET.exists():
            raise InterfaceProbeError(
                f"Network sysfs path does not exist: {self.SYS_CLASS_NET}"
            )

        link_data = self._read_ip_link_data()
        address_data = self._read_ip_address_data()
        default_interfaces = self._read_default_route_interfaces()
        nmcli_data = self._read_network_manager_state()
        wireless_data = self._read_wireless_capabilities()

        interfaces: list[NetworkInterface] = []

        for interface_path in sorted(self.SYS_CLASS_NET.iterdir()):
            name = interface_path.name

            link_entry = link_data.get(name, {})
            address_entry = address_data.get(name, {})
            nm_entry = nmcli_data.get(name, {})
            wifi_entry = wireless_data.get(name, {})

            driver_data = self._read_driver_data(name)
            bus, bus_info = self._detect_bus(name, driver_data)
            usb_id = self._find_usb_id(name)

            interface = NetworkInterface(
                name=name,
                kind=self._detect_kind(name),
                state=self._parse_state(
                    nm_entry.get("state"),
                    link_entry.get("operstate"),
                ),
                mac_address=self._read_text(
                    interface_path / "address"
                ),
                driver=driver_data.get("driver"),
                driver_version=driver_data.get("version"),
                firmware_version=driver_data.get("firmware-version"),
                bus=bus,
                bus_info=bus_info,
                usb_id=usb_id,
                connection_name=nm_entry.get("connection"),
                phy_name=wifi_entry.get("phy_name"),
                addresses=self._parse_addresses(address_entry),
                is_default_route=name in default_interfaces,
                capabilities=wifi_entry.get(
                    "capabilities",
                    InterfaceCapabilities(),
                ),
            )

            interfaces.append(interface)

        return interfaces

    def discover_by_name(self, name: str) -> NetworkInterface | None:
        """Return one interface by name, if present."""

        for interface in self.discover():
            if interface.name == name:
                return interface

        return None

    def _read_ip_link_data(self) -> dict[str, dict[str, Any]]:
        result = self._run(["ip", "-json", "link", "show"])
        parsed = json.loads(result.stdout)

        return {
            entry["ifname"]: entry
            for entry in parsed
            if "ifname" in entry
        }

    def _read_ip_address_data(self) -> dict[str, dict[str, Any]]:
        result = self._run(["ip", "-json", "address", "show"])
        parsed = json.loads(result.stdout)

        return {
            entry["ifname"]: entry
            for entry in parsed
            if "ifname" in entry
        }

    def _read_default_route_interfaces(self) -> set[str]:
        result = self._run(
            ["ip", "-json", "route", "show", "default"],
            check=False,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return set()

        try:
            routes = json.loads(result.stdout)
        except json.JSONDecodeError:
            return set()

        return {
            route["dev"]
            for route in routes
            if route.get("dev")
        }

    def _read_network_manager_state(
        self,
    ) -> dict[str, dict[str, str | None]]:
        result = self._run(
            [
                "nmcli",
                "--terse",
                "--fields",
                "DEVICE,TYPE,STATE,CONNECTION",
                "device",
                "status",
            ],
            check=False,
        )

        if result.returncode != 0:
            return {}

        interfaces: dict[str, dict[str, str | None]] = {}

        for line in result.stdout.splitlines():
            fields = self._split_nmcli_line(line)

            if len(fields) != 4:
                continue

            device, device_type, state, connection = fields

            interfaces[device] = {
                "type": device_type or None,
                "state": state or None,
                "connection": (
                    None if connection in {"", "--"} else connection
                ),
            }

        return interfaces

    def _read_wireless_capabilities(
        self,
    ) -> dict[str, dict[str, Any]]:
        result = self._run(["iw", "dev"], check=False)

        if result.returncode != 0:
            return {}

        interface_to_phy: dict[str, str] = {}
        current_phy: str | None = None

        for raw_line in result.stdout.splitlines():
            line = raw_line.strip()

            phy_match = re.match(r"phy#(\d+)", line)
            if phy_match:
                current_phy = f"phy{phy_match.group(1)}"
                continue

            interface_match = re.match(r"Interface\s+(\S+)", line)
            if interface_match and current_phy:
                interface_to_phy[interface_match.group(1)] = current_phy

        phy_capabilities = self._read_phy_capabilities()

        return {
            interface_name: {
                "phy_name": phy_name,
                "capabilities": phy_capabilities.get(
                    phy_name,
                    InterfaceCapabilities(),
                ),
            }
            for interface_name, phy_name in interface_to_phy.items()
        }

    def _read_phy_capabilities(
        self,
    ) -> dict[str, InterfaceCapabilities]:
        result = self._run(["iw", "phy"], check=False)

        if result.returncode != 0:
            return {}

        capabilities: dict[str, InterfaceCapabilities] = {}
        current_phy: str | None = None
        reading_modes = False
        modes: set[str] = set()

        def save_current() -> None:
            if current_phy is None:
                return

            capabilities[current_phy] = InterfaceCapabilities(
                managed="managed" in modes,
                access_point="AP" in modes,
                access_point_vlan="AP/VLAN" in modes,
                monitor="monitor" in modes,
                p2p_client="P2P-client" in modes,
                p2p_group_owner="P2P-GO" in modes,
            )

        for raw_line in result.stdout.splitlines():
            stripped = raw_line.strip()

            phy_match = re.match(r"Wiphy\s+(\S+)", stripped)
            if phy_match:
                save_current()
                current_phy = phy_match.group(1)
                reading_modes = False
                modes = set()
                continue

            if stripped == "Supported interface modes:":
                reading_modes = True
                continue

            if reading_modes:
                mode_match = re.match(r"\*\s+(.+)", stripped)

                if mode_match:
                    modes.add(mode_match.group(1).strip())
                    continue

                if stripped and not stripped.startswith("*"):
                    reading_modes = False

        save_current()
        return capabilities

    def _read_driver_data(self, name: str) -> dict[str, str]:
        result = self._run(
            ["ethtool", "-i", name],
            check=False,
        )

        if result.returncode != 0:
            return {}

        data: dict[str, str] = {}

        for line in result.stdout.splitlines():
            key, separator, value = line.partition(":")

            if not separator:
                continue

            data[key.strip()] = value.strip()

        return data

    def _detect_kind(self, name: str) -> InterfaceKind:
        interface_path = self.SYS_CLASS_NET / name

        if name == "lo":
            return InterfaceKind.LOOPBACK

        if (interface_path / "wireless").exists():
            return InterfaceKind.WIFI

        if (interface_path / "bridge").exists():
            return InterfaceKind.BRIDGE

        if name.startswith("wg"):
            return InterfaceKind.WIREGUARD

        if "." in name:
            return InterfaceKind.VLAN

        interface_type = self._read_text(interface_path / "type")

        if interface_type == "1":
            return InterfaceKind.ETHERNET

        return InterfaceKind.UNKNOWN

    def _detect_bus(
        self,
        name: str,
        driver_data: dict[str, str],
    ) -> tuple[InterfaceBus, str | None]:
        bus_info = driver_data.get("bus-info")

        device_path = self.SYS_CLASS_NET / name / "device"

        try:
            resolved = device_path.resolve(strict=True)
        except FileNotFoundError:
            return InterfaceBus.VIRTUAL, bus_info

        path_text = str(resolved)

        if "/usb" in path_text:
            return InterfaceBus.USB, bus_info

        if "/pci" in path_text:
            return InterfaceBus.PCI, bus_info

        if "/platform" in path_text:
            return InterfaceBus.PLATFORM, bus_info

        return InterfaceBus.UNKNOWN, bus_info

    def _find_usb_id(self, name: str) -> str | None:
        device_path = self.SYS_CLASS_NET / name / "device"

        try:
            current = device_path.resolve(strict=True)
        except FileNotFoundError:
            return None

        for candidate in (current, *current.parents):
            vendor_path = candidate / "idVendor"
            product_path = candidate / "idProduct"

            if not vendor_path.exists() or not product_path.exists():
                continue

            vendor = self._read_text(vendor_path)
            product = self._read_text(product_path)

            if vendor and product:
                return f"{vendor}:{product}"

        return None

    @staticmethod
    def _parse_addresses(
        entry: dict[str, Any],
    ) -> tuple[Any, ...]:
        addresses = []

        for address in entry.get("addr_info", []):
            local = address.get("local")
            prefix_length = address.get("prefixlen")

            if local is None or prefix_length is None:
                continue

            try:
                addresses.append(
                    ip_interface(f"{local}/{prefix_length}")
                )
            except ValueError:
                continue

        return tuple(addresses)

    @staticmethod
    def _parse_state(
        nm_state: str | None,
        operational_state: str | None,
    ) -> InterfaceState:
        normalized_nm_state = (nm_state or "").lower()

        if normalized_nm_state in {
            "connected",
            "connected (externally)",
        }:
            return InterfaceState.CONNECTED

        if normalized_nm_state == "disconnected":
            return InterfaceState.DISCONNECTED

        if normalized_nm_state == "unavailable":
            return InterfaceState.UNAVAILABLE

        if normalized_nm_state == "unmanaged":
            return InterfaceState.UNMANAGED

        if (operational_state or "").lower() == "up":
            return InterfaceState.CONNECTED

        if (operational_state or "").lower() in {
            "down",
            "dormant",
        }:
            return InterfaceState.DISCONNECTED

        return InterfaceState.UNKNOWN

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
    def _read_text(path: Path) -> str | None:
        try:
            value = path.read_text(encoding="utf-8").strip()
        except (FileNotFoundError, PermissionError, OSError):
            return None

        return value or None

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
                timeout=10,
            )
        except FileNotFoundError as exc:
            raise InterfaceProbeError(
                f"Required command is not installed: {command[0]}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise InterfaceProbeError(
                f"Command timed out: {' '.join(command)}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""
            message = f"Command failed: {' '.join(command)}"

            if stderr:
                message = f"{message}: {stderr}"

            raise InterfaceProbeError(message) from exc
