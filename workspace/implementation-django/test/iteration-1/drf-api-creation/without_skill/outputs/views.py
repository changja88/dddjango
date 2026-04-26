from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin

from .models import Order
from .permissions import IsOrderOwner
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusSerializer


class OrderViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    주문 관리 API.

    - POST   /orders/          : 주문 생성
    - GET    /orders/          : 본인 주문 목록 조회
    - GET    /orders/{id}/     : 본인 주문 상세 조회
    - POST   /orders/{id}/change_status/ : 주문 상태 변경 (확정/취소)
    """

    permission_classes = [IsAuthenticated, IsOrderOwner]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "change_status":
            return OrderStatusSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_name = serializer.validated_data["action"]

        if action_name == "confirm":
            if order.status != Order.Status.PENDING:
                return Response(
                    {"detail": "대기 상태의 주문만 확정할 수 있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = Order.Status.CONFIRMED

        elif action_name == "cancel":
            if order.status == Order.Status.CANCELLED:
                return Response(
                    {"detail": "이미 취소된 주문입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = Order.Status.CANCELLED

        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)
