from rest_framework import serializers

from products.models import Product


class ProductListSerializerV1(serializers.ModelSerializer):
    """V1 list serializer: name, price, category name only."""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "category_name"]


class ProductDetailSerializerV1(serializers.ModelSerializer):
    """V1 detail serializer: name, price, category name only."""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "price", "category_name"]
