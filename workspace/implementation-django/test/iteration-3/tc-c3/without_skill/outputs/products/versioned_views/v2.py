from decimal import Decimal, InvalidOperation

from django.db.models import QuerySet
from rest_framework.generics import ListAPIView, RetrieveAPIView

from products.models import Product
from products.versioned_serializers.v2 import (
    ProductDetailSerializerV2,
    ProductListSerializerV2,
)


class ProductListV2(ListAPIView):
    """V2 product list endpoint.

    Returns products with extended fields: v1 fields + stock, discount_rate,
    rating, seller info.

    Supports filtering via query parameters:
    - category: filter by category slug (e.g., ?category=electronics)
    - min_price: minimum price inclusive (e.g., ?min_price=100)
    - max_price: maximum price inclusive (e.g., ?max_price=50000)
    """

    serializer_class = ProductListSerializerV2

    def get_queryset(self) -> QuerySet:
        queryset = Product.objects.filter(is_active=True).select_related(
            "category", "seller"
        )
        return self._apply_filters(queryset)

    def _apply_filters(self, queryset: QuerySet) -> QuerySet:
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        min_price = self._parse_decimal(self.request.query_params.get("min_price"))
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self._parse_decimal(self.request.query_params.get("max_price"))
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    @staticmethod
    def _parse_decimal(value: str | None) -> Decimal | None:
        if value is None:
            return None
        try:
            parsed = Decimal(value)
            if parsed < 0:
                return None
            return parsed
        except InvalidOperation:
            return None


class ProductDetailV2(RetrieveAPIView):
    """V2 product detail endpoint.

    Returns a single product with extended fields: v1 fields + stock,
    discount_rate, rating, seller info, description, timestamps.
    """

    serializer_class = ProductDetailSerializerV2

    def get_queryset(self) -> QuerySet:
        return Product.objects.filter(is_active=True).select_related(
            "category", "seller"
        )
