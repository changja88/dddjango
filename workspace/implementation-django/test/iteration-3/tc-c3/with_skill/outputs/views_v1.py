from rest_framework import permissions, viewsets

from apps.products.models import Product

from .serializers_v1 import ProductDetailSerializer, ProductListSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.active().select_related("category")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
