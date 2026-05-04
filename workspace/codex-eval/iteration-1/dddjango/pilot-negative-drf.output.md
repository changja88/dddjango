## [주요 내용]

현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 `config.toml`, Django 프로젝트, `Product` 모델이 없습니다. 세션도 읽기 전용이라 파일을 실제로 생성하지는 못했습니다. `products` 앱에 `Product` 모델이 이미 있다는 가정으로 DRF `serializer`, `viewset`, `router` 구성은 아래처럼 두면 됩니다.

`products/serializers.py`

```python
from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """상품 리소스의 API 표현입니다."""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
```

`products/views.py`

```python
from rest_framework.viewsets import ModelViewSet

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    """상품 목록, 상세, 생성, 수정, 삭제 API입니다."""

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
```

`products/urls.py`

```python
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProductViewSet

router = SimpleRouter(trailing_slash=False)
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
```

프로젝트 루트 `urls.py`에는 보통 이렇게 연결합니다.

```python
from django.urls import include, path

urlpatterns = [
    path("api/", include("products.urls")),
]
```

생성되는 엔드포인트는 다음과 같습니다.

```text
GET     /api/products
POST    /api/products
GET     /api/products/{id}
PUT     /api/products/{id}
PATCH   /api/products/{id}
DELETE  /api/products/{id}
```

`settings.py`에는 DRF와 앱이 등록되어 있어야 합니다.

```python
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "products",
]
```

검증은 실행하지 못했습니다. 현재 폴더에 Django 프로젝트 파일이 없고, 세션 권한이 읽기 전용입니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - API 설계와 URL/상태 코드 정리 → **architecture-api** 스킬
> - Python/Django 코드 품질 점검 → **implementation-python**, **implementation-cleancode** 스킬