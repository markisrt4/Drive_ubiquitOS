"""Router TOML configuration loading and validation."""

from __future__ import annotations

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
    
from dataclasses import dataclass
from ipaddress import IPv4Interface
from pathlib import Path
from typing import Any


class RouterConfigError(ValueError):
    """Raised when router configuration is invalid."""


@dataclass(frozen=True, slots=True)
class RouterIdentityConfig:
    """General router identity settings."""

    name: str
    profile: str


@dataclass(frozen=True, slots=True)
class WanConfig:
    """WAN interface settings."""

    connection_type: str
    interface: str


@dataclass(frozen=True, slots=True)
class WifiLanConfig:
    """Wireless LAN access-point settings."""

    enabled: bool
    interface: str
    driver: str | None
    usb_id: str | None
    ssid: str
    country: str
    band: str
    channel: int
    address: IPv4Interface
    security: str
    password_file: Path


@dataclass(frozen=True, slots=True)
class EthernetLanConfig:
    """Optional wired LAN settings."""

    enabled: bool
    interface: str


@dataclass(frozen=True, slots=True)
class DnsConfig:
    """DNS forwarding configuration."""

    mode: str
    servers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class VpnConfig:
    """VPN gateway configuration."""

    enabled: bool
    interface: str
    kill_switch: bool


@dataclass(frozen=True, slots=True)
class RouterConfig:
    """Complete router configuration."""

    router: RouterIdentityConfig
    wan: WanConfig
    lan_wifi: WifiLanConfig
    lan_ethernet: EthernetLanConfig
    dns: DnsConfig
    vpn: VpnConfig

    @classmethod
    def load(cls, path: str | Path) -> "RouterConfig":
        """Load and validate a router configuration file."""

        config_path = Path(path).expanduser().resolve()

        try:
            with config_path.open("rb") as config_file:
                data = tomllib.load(config_file)
        except FileNotFoundError as exc:
            raise RouterConfigError(
                f"Router configuration not found: {config_path}"
            ) from exc
        except tomllib.TOMLDecodeError as exc:
            raise RouterConfigError(
                f"Invalid TOML in {config_path}: {exc}"
            ) from exc

        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RouterConfig":
        """Build a validated configuration from a dictionary."""

        router_data = cls._require_table(data, "router")
        wan_data = cls._require_table(data, "wan")
        wifi_data = cls._require_table(data, "lan_wifi")
        ethernet_data = cls._require_table(data, "lan_ethernet")
        dns_data = cls._require_table(data, "dns")
        vpn_data = cls._require_table(data, "vpn")

        address_text = cls._require_string(wifi_data, "address")

        try:
            address = IPv4Interface(address_text)
        except ValueError as exc:
            raise RouterConfigError(
                f"lan_wifi.address is invalid: {address_text}"
            ) from exc

        country = cls._require_string(wifi_data, "country").upper()

        if len(country) != 2 or not country.isalpha():
            raise RouterConfigError(
                "lan_wifi.country must be a two-letter country code"
            )

        band = cls._require_string(wifi_data, "band").lower()

        if band not in {"2.4ghz", "5ghz", "6ghz", "auto"}:
            raise RouterConfigError(
                "lan_wifi.band must be one of: "
                "2.4ghz, 5ghz, 6ghz, auto"
            )

        security = cls._require_string(
            wifi_data,
            "security",
        ).lower()

        if security not in {"wpa2", "wpa3", "wpa2-wpa3"}:
            raise RouterConfigError(
                "lan_wifi.security must be one of: "
                "wpa2, wpa3, wpa2-wpa3"
            )

        channel = cls._require_integer(wifi_data, "channel")

        if channel < 0:
            raise RouterConfigError(
                "lan_wifi.channel cannot be negative"
            )

        dns_servers = dns_data.get("servers", [])

        if not isinstance(dns_servers, list) or not all(
            isinstance(server, str)
            for server in dns_servers
        ):
            raise RouterConfigError(
                "dns.servers must be an array of strings"
            )

        return cls(
            router=RouterIdentityConfig(
                name=cls._require_string(router_data, "name"),
                profile=cls._require_string(router_data, "profile"),
            ),
            wan=WanConfig(
                connection_type=cls._require_string(
                    wan_data,
                    "connection_type",
                ),
                interface=cls._require_string(
                    wan_data,
                    "interface",
                ),
            ),
            lan_wifi=WifiLanConfig(
                enabled=cls._require_boolean(
                    wifi_data,
                    "enabled",
                ),
                interface=cls._require_string(
                    wifi_data,
                    "interface",
                ),
                driver=cls._optional_string(
                    wifi_data,
                    "driver",
                ),
                usb_id=cls._optional_string(
                    wifi_data,
                    "usb_id",
                ),
                ssid=cls._require_string(
                    wifi_data,
                    "ssid",
                ),
                country=country,
                band=band,
                channel=channel,
                address=address,
                security=security,
                password_file=Path(
                    cls._require_string(
                        wifi_data,
                        "password_file",
                    )
                ).expanduser(),
            ),
            lan_ethernet=EthernetLanConfig(
                enabled=cls._require_boolean(
                    ethernet_data,
                    "enabled",
                ),
                interface=cls._require_string(
                    ethernet_data,
                    "interface",
                    allow_empty=True,
                ),
            ),
            dns=DnsConfig(
                mode=cls._require_string(
                    dns_data,
                    "mode",
                ),
                servers=tuple(dns_servers),
            ),
            vpn=VpnConfig(
                enabled=cls._require_boolean(
                    vpn_data,
                    "enabled",
                ),
                interface=cls._require_string(
                    vpn_data,
                    "interface",
                ),
                kill_switch=cls._require_boolean(
                    vpn_data,
                    "kill_switch",
                ),
            ),
        )

    @staticmethod
    def _require_table(
        data: dict[str, Any],
        key: str,
    ) -> dict[str, Any]:
        value = data.get(key)

        if not isinstance(value, dict):
            raise RouterConfigError(
                f"Missing or invalid [{key}] table"
            )

        return value

    @staticmethod
    def _require_string(
        data: dict[str, Any],
        key: str,
        *,
        allow_empty: bool = False,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str):
            raise RouterConfigError(
                f"{key} must be a string"
            )

        if not allow_empty and not value.strip():
            raise RouterConfigError(
                f"{key} cannot be empty"
            )

        return value.strip()

    @staticmethod
    def _optional_string(
        data: dict[str, Any],
        key: str,
    ) -> str | None:
        value = data.get(key)

        if value is None:
            return None

        if not isinstance(value, str):
            raise RouterConfigError(
                f"{key} must be a string"
            )

        value = value.strip()
        return value or None

    @staticmethod
    def _require_boolean(
        data: dict[str, Any],
        key: str,
    ) -> bool:
        value = data.get(key)

        if not isinstance(value, bool):
            raise RouterConfigError(
                f"{key} must be a boolean"
            )

        return value

    @staticmethod
    def _require_integer(
        data: dict[str, Any],
        key: str,
    ) -> int:
        value = data.get(key)

        if not isinstance(value, int) or isinstance(value, bool):
            raise RouterConfigError(
                f"{key} must be an integer"
            )

        return value
