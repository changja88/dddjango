from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.orders.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderDetailAPIView(APIView):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        return Response(OrderSerializer(order).data)
