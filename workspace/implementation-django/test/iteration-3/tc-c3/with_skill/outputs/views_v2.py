from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets

from apps.products.models import Product

from .serializers_v2 import ProductDetailSerializer, ProductListSerializer


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    filterset_class = ProductFilter

    def get_queryset(self):
        return (
            Product.objects.active()
            .select_related("category", "seller")
            .with_avg_rating()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
