"""Router runtime status models."""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import IPv4Interface, IPv6Interface
from typing import Union


IpInterface = Union[IPv4Interface, IPv6Interface]


@dataclass(frozen=True, slots=True)
class RouterStatus:
    """Describes the current runtime state of a router connection."""

    running: bool
    connection_name: str
    wan_interface: str
    lan_interface: str
    ssid: str | None = None
    internet_connected: bool = False
    addresses: tuple[IpInterface, ...] = field(default_factory=tuple)

    @property
    def state_text(self) -> str:
        """Return a user-friendly router state string."""

        return "running" if self.running else "stopped"
