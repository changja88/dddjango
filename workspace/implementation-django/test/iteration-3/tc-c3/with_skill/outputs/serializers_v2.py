from rest_framework import serializers

from apps.products.models import Product, Seller


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "name", "email", "is_verified"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    seller_name = serializers.CharField(source="seller.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "category_name",
            "stock",
            "discount_rate",
            "avg_rating",
            "seller_name",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    seller = SellerSerializer(read_only=True)
    discounted_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category_name",
            "stock",
            "discount_rate",
            "discounted_price",
            "avg_rating",
            "seller",
            "created_at",
            "updated_at",
        ]
