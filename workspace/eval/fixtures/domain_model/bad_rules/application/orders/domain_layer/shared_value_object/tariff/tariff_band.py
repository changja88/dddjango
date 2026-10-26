from __future__ import annotations

from dataclasses import dataclass

from .tariff_zone import TariffZone


@dataclass(frozen=True)
class TariffBand:
    zone: TariffZone

    def __post_init__(self) -> None:
        if not self.zone.value:
            raise ValueError("요금 구간")
