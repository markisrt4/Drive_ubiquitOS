"""Display network interfaces and their capabilities."""

from __future__ import annotations

import argparse
import sys

from networking.router.interface_probe import (
    InterfaceProbe,
    InterfaceProbeError,
)
from networking.router.network_interface import NetworkInterface


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _format_optional(value: object | None) -> str:
    return str(value) if value not in {None, ""} else "-"


def _print_interface(interface: NetworkInterface) -> None:
    print(interface.name)
    print(f"  Kind:            {interface.kind.value}")
    print(f"  State:           {interface.state.value}")
    print(f"  MAC address:     {_format_optional(interface.mac_address)}")
    print(f"  Connection:      {_format_optional(interface.connection_name)}")
    print(f"  Driver:          {_format_optional(interface.driver)}")
    print(f"  Driver version:  {_format_optional(interface.driver_version)}")
    print(f"  Firmware:        {_format_optional(interface.firmware_version)}")
    print(f"  Bus:             {interface.bus.value}")
    print(f"  Bus info:        {_format_optional(interface.bus_info)}")
    print(f"  USB ID:          {_format_optional(interface.usb_id)}")
    print(f"  PHY:             {_format_optional(interface.phy_name)}")
    print(f"  Default route:   {_yes_no(interface.is_default_route)}")

    if interface.addresses:
        print("  Addresses:")

        for address in interface.addresses:
            print(f"    - {address}")
    else:
        print("  Addresses:       -")

    if interface.is_wireless:
        capabilities = interface.capabilities

        print("  Wi-Fi capabilities:")
        print(
            f"    Managed:       {_yes_no(capabilities.managed)}"
        )
        print(
            f"    Access point:  "
            f"{_yes_no(capabilities.access_point)}"
        )
        print(
            f"    AP/VLAN:       "
            f"{_yes_no(capabilities.access_point_vlan)}"
        )
        print(
            f"    Monitor:       {_yes_no(capabilities.monitor)}"
        )
        print(
            f"    P2P client:    "
            f"{_yes_no(capabilities.p2p_client)}"
        )
        print(
            f"    P2P GO:        "
            f"{_yes_no(capabilities.p2p_group_owner)}"
        )

    roles: list[str] = []

    if interface.is_wan_candidate:
        roles.append("WAN")

    if interface.is_access_point_candidate:
        roles.append("wireless LAN access point")

    print(
        "  Candidate roles: "
        + (", ".join(roles) if roles else "-")
    )
    print()


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Discover Linux network interfaces and display "
            "their capabilities."
        )
    )

    parser.add_argument(
        "--interface",
        help="Display only the named network interface.",
    )

    return parser.parse_args()


def main() -> int:
    """Run the interface discovery CLI."""

    arguments = _parse_arguments()
    probe = InterfaceProbe()

    try:
        interfaces = probe.discover()
    except InterfaceProbeError as exc:
        print(f"Interface probe failed: {exc}", file=sys.stderr)
        return 1

    if arguments.interface:
        interfaces = [
            interface
            for interface in interfaces
            if interface.name == arguments.interface
        ]

        if not interfaces:
            print(
                f"Interface not found: {arguments.interface}",
                file=sys.stderr,
            )
            return 2

    print("Network interfaces")
    print("==================")
    print()

    for interface in interfaces:
        _print_interface(interface)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    