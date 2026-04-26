from django.urls import path

from products.versioned_views.v1 import ProductDetailV1, ProductListV1
from products.versioned_views.v2 import ProductDetailV2, ProductListV2

app_name = "products"

# URL-based versioning: /api/v1/products/ and /api/v2/products/
v1_urlpatterns = [
    path("", ProductListV1.as_view(), name="product-list-v1"),
    path("<int:pk>/", ProductDetailV1.as_view(), name="product-detail-v1"),
]

v2_urlpatterns = [
    path("", ProductListV2.as_view(), name="product-list-v2"),
    path("<int:pk>/", ProductDetailV2.as_view(), name="product-detail-v2"),
]
