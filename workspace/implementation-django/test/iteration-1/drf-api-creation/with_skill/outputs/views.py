from django.core.exceptions import ValidationError

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .permissions import IsOrderOwner
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return (
            Order.objects.for_user(self.request.user)
            .prefetch_related("items")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "create":
            return OrderCreateSerializer
        return OrderDetailSerializer

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        order = self.get_object()
        try:
            order.confirm()
        except ValidationError as e:
            return Response(
                {"detail": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(OrderDetailSerializer(order).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        try:
            order.cancel()
        except ValidationError as e:
            return Response(
                {"detail": str(e.message)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(OrderDetailSerializer(order).data)
