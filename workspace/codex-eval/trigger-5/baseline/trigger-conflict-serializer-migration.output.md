이 프로젝트 정책상 DRF `Serializer`는 쓰지 않고 Django Ninja의 `Schema`로 요청 검증을 작성합니다.

현재 `/private/tmp/dddjango-codex-eval` 워크스페이스가 비어 있고 세션이 read-only라 파일 생성은 못 했습니다. 아래처럼 붙이면 됩니다.

```python
# products/schemas.py
from ninja import Schema


class ProductCreateRequest(Schema):
    name: str
    price: int
    description: str | None = None


class ProductResponse(Schema):
    id: int
    name: str
    price: int
    description: str | None = None
```

```python
# products/api.py
from ninja import Router

from products.models import Product
from products.schemas import ProductCreateRequest, ProductResponse

router = Router(tags=["products"])


@router.post("/", response={201: ProductResponse})
def create_product(request, payload: ProductCreateRequest) -> tuple[int, Product]:
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
        description=payload.description,
    )
    return 201, product
```

```python
# config/api.py
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products/", products_router)
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

`payload: ProductCreateRequest`가 요청 본문 검증 역할을 합니다. 타입이 맞지 않거나 필수 필드가 빠지면 Django Ninja가 자동으로 422 응답을 반환합니다.

검증은 실행하지 못했습니다. 프로젝트 파일이 없고 현재 세션이 읽기 전용입니다.

---
> **관련 스킬 참조:**
> - 요청/응답 스키마와 라우터 구성 → **implementation-django-ninja** 스킬