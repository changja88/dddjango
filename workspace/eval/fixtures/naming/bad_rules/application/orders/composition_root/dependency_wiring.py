from __future__ import annotations

from application.billing.composition_root.dependency_wiring import build_invoice


def build_place_order() -> object:
    return build_invoice()
