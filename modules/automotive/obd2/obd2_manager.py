from datetime import datetime

from modules.automotive.obd2.elm327_client import Elm327Client
from modules.automotive.obd2.obd_pids import (
    AcceleratorPedalPositionPid,
    BarometricPressurePid,
    ControlModuleVoltagePid,
    CoolantTempPid,
    EngineLoadPid,
    EngineRpmPid,
    FuelLevelPid,
    IntakeAirTempPid,
    IntakeManifoldPressurePid,
    MassAirFlowPid,
    ThrottlePositionPid,
    VehicleSpeedPid,
)
from modules.automotive.obd2.vehicle_state import VehicleState


class Obd2Manager:
    def __init__(self, client: Elm327Client) -> None:
        self._client = client

        self._rpm_pid = EngineRpmPid()
        self._speed_pid = VehicleSpeedPid()
        self._map_pid = IntakeManifoldPressurePid()
        self._baro_pid = BarometricPressurePid()
        self._throttle_pid = ThrottlePositionPid()
        self._accelerator_pedal_pid = AcceleratorPedalPositionPid()
        self._engine_load_pid = EngineLoadPid()
        self._coolant_pid = CoolantTempPid()
        self._intake_temp_pid = IntakeAirTempPid()
        self._maf_pid = MassAirFlowPid()
        self._fuel_level_pid = FuelLevelPid()
        self._voltage_pid = ControlModuleVoltagePid()

    def connect(self) -> None:
        self._client.connect()

    def disconnect(self) -> None:
        self._client.disconnect()

    def read_state(self) -> VehicleState:
        rpm = self._read(self._rpm_pid)
        speed_mph = self._read(self._speed_pid)

        throttle_pct = self._read(self._throttle_pid)
        accelerator_pedal_pct = self._read(self._accelerator_pedal_pid)
        engine_load_pct = self._read(self._engine_load_pid)

        map_kpa = self._read(self._map_pid)
        baro_kpa = self._read(self._baro_pid)
        maf_gps = self._read(self._maf_pid)

        coolant_temp_f = self._read(self._coolant_pid)
        intake_temp_f = self._read(self._intake_temp_pid)

        fuel_level_pct = self._read(self._fuel_level_pid)
        control_voltage = self._read(self._voltage_pid)

        boost_psi = self._calculate_boost_psi(map_kpa, baro_kpa)

        return VehicleState(
            timestamp=datetime.now(),
            rpm=rpm,
            speed_mph=speed_mph,
            throttle_pct=throttle_pct,
            accelerator_pedal_pct=accelerator_pedal_pct,
            engine_load_pct=engine_load_pct,
            map_kpa=map_kpa,
            baro_kpa=baro_kpa,
            boost_psi=boost_psi,
            maf_gps=maf_gps,
            coolant_temp_f=coolant_temp_f,
            intake_temp_f=intake_temp_f,
            fuel_level_pct=fuel_level_pct,
            control_voltage=control_voltage,
        )

    def _read(self, pid_decoder):
        response = self._client.read_mode01_pid(pid_decoder.pid)

        if response is None:
            return None

        return pid_decoder.decode(response)

    @staticmethod
    def _calculate_boost_psi(
        map_kpa: int | None,
        baro_kpa: int | None,
    ) -> float | None:
        if map_kpa is None or baro_kpa is None:
            return None

        return (map_kpa - baro_kpa) * 0.145038
