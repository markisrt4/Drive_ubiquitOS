# Keyboard Reader

The `KeyboardReader` provides a simple interface for reading keyboard input from Linux input devices.

It uses `evdev` to monitor keyboard events and reports the Linux key name when a key is pressed.

## Example

```python
from hardware_io.keyboard import KeyboardReader


def key_pressed(key: str) -> None:
    print(f"Pressed: {key}")


reader = KeyboardReader(callback=key_pressed)
reader.start()
