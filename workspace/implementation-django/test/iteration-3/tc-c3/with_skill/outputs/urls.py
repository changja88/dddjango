from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.products.views_v1 import ProductViewSet as ProductViewSetV1
from apps.products.views_v2 import ProductViewSet as ProductViewSetV2

router_v1 = DefaultRouter()
router_v1.register("products", ProductViewSetV1, basename="product-v1")

router_v2 = DefaultRouter()
router_v2.register("products", ProductViewSetV2, basename="product-v2")

urlpatterns = [
    path("api/v1/", include(router_v1.urls)),
    path("api/v2/", include(router_v2.urls)),
]
