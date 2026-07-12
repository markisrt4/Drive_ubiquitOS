# ELM327 Adapter

The `Elm327Adapter` provides an OBD-II adapter implementation for ELM327-compatible devices.

It implements the `Obd2Adapter` interface and communicates with an ELM327 device using a serial connection.

## Connection

By default, the adapter connects using:

```text
/dev/rfcomm0
```

at:

```text
38400 baud
```

The serial device and baud rate can be configured when creating the adapter.

## Example

```python
from hardware_io.automotive.obd2.elm327 import Elm327Adapter


adapter = Elm327Adapter(
    port="/dev/rfcomm0",
    baud=38400,
)

try:
    adapter.connect()

    response = adapter.send_command("010C")

    print(response.raw)

finally:
    adapter.disconnect()
```

## Initialization

When connected, the adapter sends the following ELM327 initialization commands:

```text
ATZ
ATE0
ATL0
ATS0
ATH1
ATSP0
```

These commands reset the adapter and configure the response format used by the application.

## Dependency

The ELM327 adapter requires `pyserial`.

Install the dependency using:

```bash
python3 -m pip install pyserial
```

## Bluetooth RFCOMM

Bluetooth ELM327 adapters may be exposed as a Linux serial device using RFCOMM.

Example device:

```text
/dev/rfcomm0
```

The RFCOMM connection must be established before the `Elm327Adapter` connects to the serial device.

## Design

The `Elm327Adapter` is responsible only for ELM327-specific communication.

It does not interpret OBD-II PIDs or convert vehicle data into application-specific values.

OBD-II protocol interpretation should be handled by higher-level components.
