from rest_framework.generics import ListAPIView, RetrieveAPIView

from products.models import Product
from products.versioned_serializers.v1 import (
    ProductDetailSerializerV1,
    ProductListSerializerV1,
)


class ProductListV1(ListAPIView):
    """V1 product list endpoint.

    Returns products with basic fields: name, price, category name.
    """

    serializer_class = ProductListSerializerV1

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category")


class ProductDetailV1(RetrieveAPIView):
    """V1 product detail endpoint.

    Returns a single product with basic fields: name, price, category name.
    """

    serializer_class = ProductDetailSerializerV1

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category")
