from django.test import TestCase

from shop.orders.models import Order


class OrderModelTests(TestCase):
    def test_cancel_sets_status(self):
        order = Order.objects.create(
            customer_email="buyer@example.com",
            total_amount="100.00",
        )

        order.cancel(reason="customer request", actor_email="ops@example.com")

        self.assertEqual(order.status, Order.STATUS_CANCELLED)
