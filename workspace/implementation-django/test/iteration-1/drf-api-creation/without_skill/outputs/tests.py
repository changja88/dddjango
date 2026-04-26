from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order, OrderItem, Product

User = get_user_model()


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="testpass123")
        self.other_user = User.objects.create_user(username="other", password="testpass123")

        self.product_a = Product.objects.create(name="상품A", price=Decimal("10000"))
        self.product_b = Product.objects.create(name="상품B", price=Decimal("25000"))

        self.list_url = reverse("order-list")

    def _create_order(self, user=None):
        """헬퍼: 대기 상태의 주문을 직접 생성한다."""
        user = user or self.user
        order = Order.objects.create(user=user, total_amount=Decimal("35000"))
        OrderItem.objects.create(order=order, product=self.product_a, quantity=1, price=Decimal("10000"))
        OrderItem.objects.create(order=order, product=self.product_b, quantity=1, price=Decimal("25000"))
        return order

    # --- 주문 생성 ---

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "items": [
                {"product": self.product_a.pk, "quantity": 2},
                {"product": self.product_b.pk, "quantity": 1},
            ]
        }
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.Status.PENDING)
        self.assertEqual(Decimal(response.data["total_amount"]), Decimal("45000.00"))
        self.assertEqual(Order.objects.count(), 1)

    def test_create_order_empty_items_rejected(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, {"items": []}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_unauthenticated(self):
        data = {"items": [{"product": self.product_a.pk, "quantity": 1}]}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 주문 목록 조회 ---

    def test_list_own_orders(self):
        self._create_order(user=self.user)
        self._create_order(user=self.other_user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # --- 주문 상세 조회 ---

    def test_retrieve_own_order(self):
        order = self._create_order(user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse("order-detail", args=[order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], order.pk)

    def test_cannot_retrieve_other_user_order(self):
        order = self._create_order(user=self.other_user)
        self.client.force_authenticate(user=self.user)
        url = reverse("order-detail", args=[order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- 상태 변경: 확정 ---

    def test_confirm_pending_order(self):
        order = self._create_order(user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse("order-change-status", args=[order.pk])
        response = self.client.post(url, {"action": "confirm"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Order.Status.CONFIRMED)

    def test_confirm_non_pending_order_rejected(self):
        order = self._create_order(user=self.user)
        order.status = Order.Status.CONFIRMED
        order.save()

        self.client.force_authenticate(user=self.user)
        url = reverse("order-change-status", args=[order.pk])
        response = self.client.post(url, {"action": "confirm"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 상태 변경: 취소 ---

    def test_cancel_pending_order(self):
        order = self._create_order(user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse("order-change-status", args=[order.pk])
        response = self.client.post(url, {"action": "cancel"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Order.Status.CANCELLED)

    def test_cancel_already_cancelled_order_rejected(self):
        order = self._create_order(user=self.user)
        order.status = Order.Status.CANCELLED
        order.save()

        self.client.force_authenticate(user=self.user)
        url = reverse("order-change-status", args=[order.pk])
        response = self.client.post(url, {"action": "cancel"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_status_other_user_order_denied(self):
        order = self._create_order(user=self.other_user)
        self.client.force_authenticate(user=self.user)
        url = reverse("order-change-status", args=[order.pk])
        response = self.client.post(url, {"action": "confirm"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
