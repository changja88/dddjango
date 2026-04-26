from decimal import Decimal

from rest_framework import serializers

from .models import Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
        read_only_fields = ["price"]


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ["id", "items", "total_amount", "status", "created_at"]
        read_only_fields = ["total_amount", "status", "created_at"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("주문에는 최소 하나 이상의 상품이 필요합니다.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(user=user)

        total = Decimal("0")
        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            item_price = product.price * quantity
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=item_price,
            )
            total += item_price

        order.total_amount = total
        order.save(update_fields=["total_amount"])
        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "items",
            "total_amount",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderStatusSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["confirm", "cancel"])
