from rest_framework import serializers

from products.models import Product, Seller


class SellerSerializer(serializers.ModelSerializer):
    """Seller info serializer for v2 product responses."""

    class Meta:
        model = Seller
        fields = ["id", "name", "email", "phone", "is_verified"]


class ProductListSerializerV2(serializers.ModelSerializer):
    """V2 list serializer: v1 fields + stock, discount_rate, rating, seller info."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    seller = SellerSerializer(read_only=True)
    discounted_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "category_name",
            "stock",
            "discount_rate",
            "discounted_price",
            "rating",
            "seller",
        ]


class ProductDetailSerializerV2(serializers.ModelSerializer):
    """V2 detail serializer: v1 fields + stock, discount_rate, rating, seller info, description."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    seller = SellerSerializer(read_only=True)
    discounted_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "category_name",
            "stock",
            "discount_rate",
            "discounted_price",
            "rating",
            "seller",
            "description",
            "created_at",
            "updated_at",
        ]
