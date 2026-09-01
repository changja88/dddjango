from __future__ import annotations

import django


TARGET_MODULE = "application.orders.domain_layer"


def resolve() -> str:
    return TARGET_MODULE
