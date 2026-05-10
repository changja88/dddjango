from __future__ import annotations

import unittest

from apps.orders.services import create_order


class OrderServiceTests(unittest.TestCase):
    def test_create_order_starts_pending(self) -> None:
        order = create_order("customer-1", ["sku-1"], "gift")
        self.assertEqual(order.status.value, "pending")
