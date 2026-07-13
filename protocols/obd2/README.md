# OBD-II Protocol Models

This package defines the application-independent model used to issue SAE J1979 OBD-II requests, normalize ECU responses, and decode a small set of standardized Mode 01 PIDs.

It intentionally does **not** know about serial ports, Bluetooth, ELM327 command syntax, UI widgets, vehicle dashboards, or display preferences. Concrete adapters translate their transport into these models.

## Layer responsibilities

### This package owns

- OBD-II request and response value objects
- The transport-independent adapter interface
- Protocol-specific exceptions
- Standard PID identifiers and decoding formulas
- Canonical SAE units

### Concrete adapters own

- Connection setup and teardown
- ELM327 or other adapter initialization
- Transport framing and ISO-TP reassembly
- Removing command echo, headers, byte counts, and prompt characters
- Parsing positive, negative, malformed, and `NO DATA` responses
- Returning one normalized `Obd2Response` per responding ECU

### Higher layers own

- Polling schedules and caching
- Choosing which ECU response to use
- Derived values such as boost pressure
- Unit conversion, such as km/h to mph or °C to °F
- UI formatting and presentation

## Request and response semantics

A current-data RPM request is represented as:

```python
Obd2Request(mode=0x01, pid=0x0C)
```

A positive legacy J1979 response normally adds `0x40` to the request mode. A response to the request above therefore uses mode `0x41`:

```python
Obd2Response(
    mode=0x41,
    pid=0x0C,
    data=bytes.fromhex("1AF8"),
    ecu_id=0x7E8,
)
```

The response `data` contains only PID payload bytes. It must not include the response mode, PID byte, CAN/ISO-TP framing, ELM327 echo, or prompt.

## Multiple ECUs

Functional OBD-II requests can receive responses from more than one ECU. For that reason:

```python
responses = adapter.request(request)
```

returns `tuple[Obd2Response, ...]`. An empty tuple means that no ECU produced a usable response. The adapter must not silently choose one ECU on behalf of higher-level code.

## Canonical units

PID decoders return standardized metric/SI values:

| PID | Decoder | Unit |
|---:|---|---|
| `0x04` | `EngineLoadPid` | `%` |
| `0x05` | `CoolantTempPid` | `°C` |
| `0x0B` | `IntakeManifoldPressurePid` | `kPa` |
| `0x0C` | `EngineRpmPid` | `rpm` |
| `0x0D` | `VehicleSpeedPid` | `km/h` |
| `0x0F` | `IntakeAirTempPid` | `°C` |
| `0x10` | `MassAirFlowPid` | `g/s` |
| `0x11` | `ThrottlePositionPid` | `%` |
| `0x2F` | `FuelLevelPid` | `%` |
| `0x33` | `BarometricPressurePid` | `kPa` |
| `0x42` | `ControlModuleVoltagePid` | `V` |
| `0x49` | `AcceleratorPedalPositionPid` | `%` |

Display conversions belong outside this package:

```python
speed_mph = speed_kph * 0.621371
coolant_f = coolant_c * 9.0 / 5.0 + 32.0
```

## Decoder behavior

A decoder returns `None` when the payload is too short. Transport corruption and structurally invalid messages should be rejected by the concrete adapter before a decoder is called.

```python
rpm = EngineRpmPid().decode(bytes.fromhex("1AF8"))
assert rpm == 1726.0
```

## Component test

From the repository root:

```bash
python -m protocols.obd2.component_test
```

The component test checks model validation, known PID vectors, canonical units, and truncated payload behavior. It requires no adapter and no vehicle, because dragging a Hyundai into a unit test would be considered excessive even by integration-test standards.
