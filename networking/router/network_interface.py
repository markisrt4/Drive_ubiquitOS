"""Network interface data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from ipaddress import IPv4Interface, IPv6Interface
from typing import TypeAlias


IpInterface: TypeAlias = IPv4Interface | IPv6Interface


class InterfaceKind(Enum):
    """High-level network interface types."""

    ETHERNET = "ethernet"
    WIFI = "wifi"
    LOOPBACK = "loopback"
    BRIDGE = "bridge"
    VLAN = "vlan"
    WIREGUARD = "wireguard"
    CELLULAR = "cellular"
    UNKNOWN = "unknown"


class InterfaceBus(Enum):
    """Physical or virtual interface attachment type."""

    USB = "usb"
    PCI = "pci"
    PLATFORM = "platform"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"


class InterfaceState(Enum):
    """Observed interface operational state."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNAVAILABLE = "unavailable"
    UNMANAGED = "unmanaged"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class InterfaceCapabilities:
    """Capabilities reported by the network interface driver."""

    managed: bool = False
    access_point: bool = False
    access_point_vlan: bool = False
    monitor: bool = False
    p2p_client: bool = False
    p2p_group_owner: bool = False


@dataclass(frozen=True, slots=True)
class NetworkInterface:
    """Describes a network interface discovered on the host."""

    name: str
    kind: InterfaceKind
    state: InterfaceState

    mac_address: str | None = None
    driver: str | None = None
    driver_version: str | None = None
    firmware_version: str | None = None

    bus: InterfaceBus = InterfaceBus.UNKNOWN
    bus_info: str | None = None
    usb_id: str | None = None

    connection_name: str | None = None
    phy_name: str | None = None

    addresses: tuple[IpInterface, ...] = field(default_factory=tuple)
    is_default_route: bool = False

    capabilities: InterfaceCapabilities = field(
        default_factory=InterfaceCapabilities
    )

    @property
    def is_wireless(self) -> bool:
        """Return whether this is a Wi-Fi interface."""

        return self.kind == InterfaceKind.WIFI

    @property
    def is_wan_candidate(self) -> bool:
        """Return whether the interface is a likely WAN candidate."""

        return (
            self.kind in {InterfaceKind.ETHERNET, InterfaceKind.WIFI}
            and self.state == InterfaceState.CONNECTED
            and self.is_default_route
        )

    @property
    def is_access_point_candidate(self) -> bool:
        """Return whether the interface can host a Wi-Fi access point."""

        return (
            self.kind == InterfaceKind.WIFI
            and self.capabilities.access_point
        )
