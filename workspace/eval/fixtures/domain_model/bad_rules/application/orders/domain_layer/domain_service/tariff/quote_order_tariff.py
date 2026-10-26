from __future__ import annotations

from application.orders.domain_layer.shared_value_object.tariff.tariff_band import TariffBand
from application.orders.domain_layer.shared_value_object.tariff.tariff_zone import TariffZone


def quote_order_tariff(band: TariffBand, zone: TariffZone) -> TariffBand:
    return band
