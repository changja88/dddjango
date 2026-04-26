from django.contrib import admin
from django.urls import include, path

from products.urls import v1_urlpatterns, v2_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    # URL-based API versioning
    path("api/v1/products/", include((v1_urlpatterns, "products"), namespace="v1")),
    path("api/v2/products/", include((v2_urlpatterns, "products"), namespace="v2")),
]
