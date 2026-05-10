from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Coupon:
    code: str
    discount_amount: int
    minimum_order_amount: int
    expires_on: date
    used: bool = False


def apply_coupon(coupon: Coupon, order_amount: int, today: date) -> int:
    if coupon.used:
        raise ValueError("coupon already used")
    if today > coupon.expires_on:
        raise ValueError("coupon expired")
    if order_amount < coupon.minimum_order_amount:
        raise ValueError("minimum order amount not met")
    return max(order_amount - coupon.discount_amount, 0)
