from __future__ import annotations

import unittest

from apps.orders.models import OrderStatus
from apps.orders.services import _ORDERS, confirm_order, place_order


class OrderServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        _ORDERS.clear()

    def test_place_order_moves_to_pending_payment(self) -> None:
        order = place_order("customer-1", ["sku-1"])

        self.assertEqual(order.status, OrderStatus.PENDING_PAYMENT)
        self.assertEqual(_ORDERS[order.id], order)

    def test_confirm_order_moves_to_confirmed(self) -> None:
        order = place_order("customer-1", ["sku-1"])

        confirmed = confirm_order(order.id)

        self.assertEqual(confirmed.status, OrderStatus.CONFIRMED)


if __name__ == "__main__":
    unittest.main()
