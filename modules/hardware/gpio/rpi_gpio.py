from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class GpioPin:
    """
    Represents a Raspberry Pi header pin.
    """

    bcm: Optional[int]
    pin: int
    name: str
    function: str

    @property
    def is_gpio(self) -> bool:
        return self.bcm is not None


class RpiGpio:
    """
    Raspberry Pi 4 GPIO header mapping.

    Physical pin numbers are used as the primary key.
    """

    _pins: Dict[int, GpioPin] = {
        1:  GpioPin(None, 1,  "3V3",    "Power"),
        2:  GpioPin(None, 2,  "5V",     "Power"),
        3:  GpioPin(2,    3,  "GPIO2",  "I2C1 SDA"),
        4:  GpioPin(None, 4,  "5V",     "Power"),
        5:  GpioPin(3,    5,  "GPIO3",  "I2C1 SCL"),
        6:  GpioPin(None, 6,  "GND",    "Ground"),
        7:  GpioPin(4,    7,  "GPIO4",  "GPCLK0"),
        8:  GpioPin(14,   8,  "GPIO14", "UART0 TXD"),
        9:  GpioPin(None, 9,  "GND",    "Ground"),
        10: GpioPin(15,  10,  "GPIO15", "UART0 RXD"),
        11: GpioPin(17,  11,  "GPIO17", "GPIO"),
        12: GpioPin(18,  12,  "GPIO18", "PWM0"),
        13: GpioPin(27,  13,  "GPIO27", "GPIO"),
        14: GpioPin(None, 14, "GND",    "Ground"),
        15: GpioPin(22,  15,  "GPIO22", "GPIO"),
        16: GpioPin(23,  16,  "GPIO23", "GPIO"),
        17: GpioPin(None, 17, "3V3",    "Power"),
        18: GpioPin(24,  18,  "GPIO24", "GPIO"),
        19: GpioPin(10,  19,  "GPIO10", "SPI0 MOSI"),
        20: GpioPin(None, 20, "GND",    "Ground"),
        21: GpioPin(9,   21,  "GPIO9",  "SPI0 MISO"),
        22: GpioPin(25,  22,  "GPIO25", "GPIO"),
        23: GpioPin(11,  23,  "GPIO11", "SPI0 SCLK"),
        24: GpioPin(8,   24,  "GPIO8",  "SPI0 CE0"),
        25: GpioPin(None, 25, "GND",    "Ground"),
        26: GpioPin(7,   26,  "GPIO7",  "SPI0 CE1"),
        27: GpioPin(0,   27,  "GPIO0",  "ID_SD"),
        28: GpioPin(1,   28,  "GPIO1",  "ID_SC"),
        29: GpioPin(5,   29,  "GPIO5",  "GPIO"),
        30: GpioPin(None, 30, "GND",    "Ground"),
        31: GpioPin(6,   31,  "GPIO6",  "GPIO"),
        32: GpioPin(12,  32,  "GPIO12", "PWM0"),
        33: GpioPin(13,  33,  "GPIO13", "PWM1"),
        34: GpioPin(None, 34, "GND",    "Ground"),
        35: GpioPin(19,  35,  "GPIO19", "PWM1"),
        36: GpioPin(16,  36,  "GPIO16", "GPIO"),
        37: GpioPin(26,  37,  "GPIO26", "GPIO"),
        38: GpioPin(20,  38,  "GPIO20", "GPIO"),
        39: GpioPin(None, 39, "GND",    "Ground"),
        40: GpioPin(21,  40,  "GPIO21", "GPIO"),
    }

    _bcm_lookup: Dict[int, GpioPin] = {
        pin.bcm: pin
        for pin in _pins.values()
        if pin.bcm is not None
    }

    @classmethod
    def by_pin(cls, pin_number: int) -> GpioPin:
        """
        Lookup by physical header pin number.
        """
        try:
            return cls._pins[pin_number]
        except KeyError:
            raise ValueError(f"Invalid physical pin: {pin_number}")

    @classmethod
    def by_bcm(cls, bcm_number: int) -> GpioPin:
        """
        Lookup by BCM GPIO number.
        """
        try:
            return cls._bcm_lookup[bcm_number]
        except KeyError:
            raise ValueError(f"Invalid BCM GPIO: {bcm_number}")

    @classmethod
    def bcm_from_pin(cls, pin_number: int) -> int:
        """
        Return BCM GPIO number from a physical pin.
        """
        pin = cls.by_pin(pin_number)

        if pin.bcm is None:
            raise ValueError(
                f"Pin {pin_number} ({pin.name}) is not a GPIO pin"
            )

        return pin.bcm

    @classmethod
    def pin_from_bcm(cls, bcm_number: int) -> int:
        """
        Return physical header pin from BCM GPIO.
        """
        return cls.by_bcm(bcm_number).pin

    @classmethod
    def is_gpio_pin(cls, pin_number: int) -> bool:
        return cls.by_pin(pin_number).is_gpio

    @classmethod
    def all_gpio_pins(cls) -> list[GpioPin]:
        return [pin for pin in cls._pins.values() if pin.is_gpio]

    @classmethod
    def print_table(cls) -> None:
        """
        Debug helper.
        """
        print(
            f"{'PIN':>4} {'BCM':>4} {'NAME':<8} FUNCTION"
        )

        for pin_num in sorted(cls._pins):
            pin = cls._pins[pin_num]

            bcm = "-" if pin.bcm is None else str(pin.bcm)

            print(
                f"{pin.pin:>4} "
                f"{bcm:>4} "
                f"{pin.name:<8} "
                f"{pin.function}"
            )
