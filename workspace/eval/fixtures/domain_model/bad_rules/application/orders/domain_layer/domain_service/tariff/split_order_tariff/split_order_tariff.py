from __future__ import annotations

from application.orders.domain_layer.shared_value_object.tariff.tariff_band import TariffBand
from application.orders.domain_layer.shared_value_object.tariff.tariff_zone import TariffZone

from .order_tariff_step import order_tariff_step


def split_order_tariff(band: TariffBand, zone: TariffZone) -> bool:
    return order_tariff_step(band, zone)
