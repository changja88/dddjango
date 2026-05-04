이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja `Schema`로 작성합니다. 현재 `/private/tmp/dddjango-codex-eval`에는 프로젝트 파일이 없고 세션도 읽기 전용이라 직접 파일 생성은 못 했습니다. 대신 아래처럼 붙여 넣으면 됩니다.

[예시: `products/schemas.py`]

```python
from ninja import Schema
from pydantic import Field, field_validator


class ProductCreateRequest(Schema):
    name: str = Field(min_length=1, max_length=120)
    price: int = Field(ge=0)
    stock: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name is required")
        return value


class ProductResponse(Schema):
    id: int
    name: str
    price: int
    stock: int
```

[예시: `products/api.py`]

```python
from ninja import Router

from products.models import Product
from products.schemas import ProductCreateRequest, ProductResponse

router = Router(tags=["products"])


@router.post("/", response={201: ProductResponse})
def create_product(request, payload: ProductCreateRequest) -> tuple[int, Product]:
    product = Product.objects.create(
        name=payload.name,
        price=payload.price,
        stock=payload.stock,
    )
    return 201, product
```

[예시: `config/api.py`]

```python
from ninja import NinjaAPI

from products.api import router as products_router

api = NinjaAPI()
api.add_router("/products/", products_router)
```

[예시: `config/urls.py`]

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

핵심은 요청 본문 파라미터에 `payload: ProductCreateRequest`처럼 `Schema` 클래스를 타입으로 지정하는 것입니다. 그러면 Django Ninja가 JSON body를 자동으로 파싱하고 타입, 길이, 범위, 커스텀 validator까지 검증합니다.

검증은 실행하지 못했습니다. 프로젝트 파일을 실제 위치에 둔 뒤 `python manage.py test` 또는 API 호출로 확인하면 됩니다.

---
> **관련 스킬 참조:**
> - 요청/응답 Schema 설계 → **implementation-django-ninja** 스킬