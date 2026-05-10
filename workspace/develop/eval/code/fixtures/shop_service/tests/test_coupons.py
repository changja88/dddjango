from __future__ import annotations

import unittest
from datetime import date

from apps.coupons.policy import Coupon, apply_coupon


class CouponPolicyTests(unittest.TestCase):
    def test_applies_discount_when_rule_matches(self) -> None:
        coupon = Coupon("WELCOME", 1000, 5000, date(2099, 1, 1))
        self.assertEqual(apply_coupon(coupon, 7000, date(2026, 1, 1)), 6000)
