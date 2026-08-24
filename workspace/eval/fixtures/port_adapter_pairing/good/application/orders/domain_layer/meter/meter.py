from __future__ import annotations


class Meter:
    def __init__(self, meter_id: str) -> None:
        self.meter_id: str = meter_id
        self._readings: list = []

    def record(self, value: int) -> None:
        self._readings.append(value)

    @property
    def readings(self) -> tuple:
        return tuple(self._readings)
