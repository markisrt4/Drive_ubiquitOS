# Audio Controller

The `audio` controller provides a common interface for controlling system audio output.

Audio applications and input components can use the audio controller without depending directly on a specific operating system audio implementation.

## Components

| Component | Description |
|-----------|-------------|
| `AudioControllerIf` | Defines the common audio control interface. |
| `PipewireAudioController` | Controls PipeWire audio output using `wpctl`. |

## Directory Layout

```text
audio/
├── __init__.py
├── audio_controller_if.py
├── pipewire_audio_controller.py
├── README.md
└── component_test/
    ├── __init__.py
    └── audio_cli.py
```

## Features

The audio controller provides:

- Volume increase
- Volume decrease
- Discrete volume levels
- Direct volume level selection
- Relative volume adjustment
- Replaceable audio controller implementations

## Audio Controller Interface

`AudioControllerIf` defines the common audio control interface.

Implementations provide:

```python
volume_up()
volume_down()
get_volume_level()
set_volume_level(level)
adjust_volume(steps)
```

Higher-level components should depend on `AudioControllerIf` rather than a specific audio implementation.

Example:

```python
from controllers.audio import AudioControllerIf


def adjust_output_volume(
    controller: AudioControllerIf,
    steps: int,
) -> None:
    controller.adjust_volume(steps)
```

## PipeWire Audio Controller

`PipewireAudioController` controls the default PipeWire audio sink using `wpctl`.

The controller operates on:

```text
@DEFAULT_AUDIO_SINK@
```

This allows the operating system to determine the active audio output device.

Example:

```python
from controllers.audio import PipewireAudioController


controller = PipewireAudioController()

controller.volume_up()
controller.volume_down()

level = controller.get_volume_level()

controller.set_volume_level(10)
```

## Volume Levels

The PipeWire controller exposes system volume as discrete levels.

By default:

```text
steps = 20
step_percent = 5
```

This produces levels from:

```text
0 through 20
```

where:

```text
0  = 0%
1  = 5%
2  = 10%
...
20 = 100%
```

The number of levels can be configured:

```python
controller = PipewireAudioController(
    steps=10,
    step_percent=10,
)
```

## Relative Volume Adjustment

`adjust_volume()` changes the current volume by a number of discrete steps.

Example:

```python
controller.adjust_volume(1)
```

Increase volume by one level.

```python
controller.adjust_volume(-1)
```

Decrease volume by one level.

Multiple steps may be applied at once:

```python
controller.adjust_volume(3)
controller.adjust_volume(-4)
```

This is useful for input devices that report relative movement, such as rotary encoders.

Example:

```python
def volume_rotated(turns: int) -> None:
    audio_controller.adjust_volume(turns)
```

## Dependencies

The PipeWire implementation requires `wpctl`.

Verify that `wpctl` is available:

```bash
wpctl --version
```

The active audio sink can be inspected using:

```bash
wpctl status
```

Current volume can be read using:

```bash
wpctl get-volume @DEFAULT_AUDIO_SINK@
```

## Component Test

A CLI component test is provided.

Run from the project root:

```bash
python3 -m controllers.audio.component_test.audio_cli
```

Available commands:

```text
+          Volume up
-          Volume down
s <level>  Set volume level
g          Get volume level
q          Quit
```

Example session:

```text
audio> g
Volume level: 8

audio> +
Volume level: 9

audio> s 12
Volume level: 12

audio> -
Volume level: 11
```

## Design

The audio controller represents system audio control behavior.

Higher-level components interact with `AudioControllerIf` and do not need to know how system volume is controlled.

Concrete implementations are responsible for interacting with the underlying audio system.

For example:

```text
Input Device
     |
     v
AudioControllerIf
     |
     v
PipewireAudioController
     |
     v
wpctl
     |
     v
PipeWire
```

This allows additional audio controller implementations to be added without changing components that use audio control.

Possible implementations may include:

- PipeWire
- PulseAudio
- ALSA
- Remote audio services
- Mock audio controllers

Operating system and audio-system-specific behavior remains inside the concrete audio controller implementation.
