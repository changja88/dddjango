from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price"]


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "status",
            "item_count",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "status",
            "items",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["items"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        total = sum(
            item["unit_price"] * item["quantity"] for item in items_data
        )
        order = Order.objects.create(
            user=self.context["request"].user,
            total_amount=total,
        )
        OrderItem.objects.bulk_create(
            [OrderItem(order=order, **item) for item in items_data]
        )
        return order
