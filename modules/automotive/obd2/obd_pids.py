from modules.automotive.obd2.obd_pid import byte_at


class EngineLoadPid:
    @property
    def pid(self) -> str:
        return "04"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4) * 100.0 / 255.0


class EngineRpmPid:
    @property
    def pid(self) -> str:
        return "0C"

    def decode(self, response: str) -> int | None:
        if len(response) < 8:
            return None

        a = byte_at(response, 4)
        b = byte_at(response, 6)
        return int(((a * 256) + b) / 4)


class VehicleSpeedPid:
    @property
    def pid(self) -> str:
        return "0D"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        speed_kph = byte_at(response, 4)
        return speed_kph * 0.621371


class IntakeManifoldPressurePid:
    @property
    def pid(self) -> str:
        return "0B"

    def decode(self, response: str) -> int | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4)


class BarometricPressurePid:
    @property
    def pid(self) -> str:
        return "33"

    def decode(self, response: str) -> int | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4)


class ThrottlePositionPid:
    @property
    def pid(self) -> str:
        return "11"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4) * 100.0 / 255.0


class AcceleratorPedalPositionPid:
    @property
    def pid(self) -> str:
        return "49"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4) * 100.0 / 255.0


class CoolantTempPid:
    @property
    def pid(self) -> str:
        return "05"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        temp_c = byte_at(response, 4) - 40
        return temp_c * 9.0 / 5.0 + 32.0


class IntakeAirTempPid:
    @property
    def pid(self) -> str:
        return "0F"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        temp_c = byte_at(response, 4) - 40
        return temp_c * 9.0 / 5.0 + 32.0


class MassAirFlowPid:
    @property
    def pid(self) -> str:
        return "10"

    def decode(self, response: str) -> float | None:
        if len(response) < 8:
            return None

        a = byte_at(response, 4)
        b = byte_at(response, 6)
        return ((a * 256) + b) / 100.0


class FuelLevelPid:
    @property
    def pid(self) -> str:
        return "2F"

    def decode(self, response: str) -> float | None:
        if len(response) < 6:
            return None

        return byte_at(response, 4) * 100.0 / 255.0


class ControlModuleVoltagePid:
    @property
    def pid(self) -> str:
        return "42"

    def decode(self, response: str) -> float | None:
        if len(response) < 8:
            return None

        a = byte_at(response, 4)
        b = byte_at(response, 6)
        return ((a * 256) + b) / 1000.0
