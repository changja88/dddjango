from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from .models import Order, OrderItem

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.order = Order.objects.create(
            user=self.user, total_amount=Decimal("100.00")
        )

    def test_confirm_from_pending(self):
        self.order.confirm()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CONFIRMED)

    def test_confirm_from_non_pending_raises(self):
        self.order.status = Order.Status.CONFIRMED
        self.order.save(update_fields=["status"])
        with self.assertRaises(Exception):
            self.order.confirm()

    def test_cancel_from_pending(self):
        self.order.cancel()
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_cancel_from_non_pending_raises(self):
        self.order.status = Order.Status.CONFIRMED
        self.order.save(update_fields=["status"])
        with self.assertRaises(Exception):
            self.order.cancel()


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        data = {
            "items": [
                {
                    "product_name": "Widget",
                    "quantity": 2,
                    "unit_price": "10.00",
                },
                {
                    "product_name": "Gadget",
                    "quantity": 1,
                    "unit_price": "25.00",
                },
            ]
        }
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.total_amount, Decimal("45.00"))
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_create_order_no_items_fails(self):
        response = self.client.post(
            "/api/orders/", {"items": []}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_own_only(self):
        Order.objects.create(
            user=self.user, total_amount=Decimal("50.00")
        )
        Order.objects.create(
            user=self.other_user, total_amount=Decimal("75.00")
        )
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_own_order(self):
        order = Order.objects.create(
            user=self.user, total_amount=Decimal("50.00")
        )
        response = self.client.get(f"/api/orders/{order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_other_user_order_forbidden(self):
        order = Order.objects.create(
            user=self.other_user, total_amount=Decimal("50.00")
        )
        response = self.client.get(f"/api/orders/{order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_pending_order(self):
        order = Order.objects.create(
            user=self.user, total_amount=Decimal("50.00")
        )
        response = self.client.post(f"/api/orders/{order.pk}/confirm/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    def test_confirm_non_pending_order_fails(self):
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("50.00"),
            status=Order.Status.CONFIRMED,
        )
        response = self.client.post(f"/api/orders/{order.pk}/confirm/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_pending_order(self):
        order = Order.objects.create(
            user=self.user, total_amount=Decimal("50.00")
        )
        response = self.client.post(f"/api/orders/{order.pk}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)

    def test_cancel_non_pending_order_fails(self):
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("50.00"),
            status=Order.Status.CANCELLED,
        )
        response = self.client.post(f"/api/orders/{order.pk}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_query_count(self):
        Order.objects.create(
            user=self.user, total_amount=Decimal("50.00")
        )
        Order.objects.create(
            user=self.user, total_amount=Decimal("75.00")
        )
        with self.assertNumQueries(3):
            self.client.get("/api/orders/")
