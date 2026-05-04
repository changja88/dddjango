이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 읽기 전용이라 파일 생성/테스트 실행은 못 했습니다. 아래는 `products` 앱과 `Product` 모델을 가정한 TDD 순서의 붙여넣기용 코드입니다.

**RED: pytest 먼저**
```python
# tests/isolated/integration/test_products_api.py
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from ninja.testing import TestClient

from products.api import router
from products.models import Product


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="seller", password="testpass")


@pytest.mark.django_db
def test_create_product_returns_created_product(client, user):
    response = client.post(
        "/",
        json={
            "name": "Keyboard",
            "description": "Low profile keyboard",
            "price": "129000.00",
            "stock": 10,
            "status": "active",
        },
        user=user,
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Keyboard"
    assert Product.objects.filter(name="Keyboard").exists()


@pytest.mark.django_db
def test_patch_product_updates_only_sent_fields(client, user):
    product = Product.objects.create(
        name="Mouse",
        price=Decimal("49000.00"),
        stock=5,
        status=Product.Status.ACTIVE,
    )

    response = client.patch(
        f"/{product.id}",
        json={"stock": 3},
        user=user,
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.name == "Mouse"
    assert product.stock == 3
```

예상 RED 실패 이유: 아직 `products.api`, `Product`, 라우터 엔드포인트가 없어서 import 실패 또는 404가 납니다.

**GREEN: 최소 구현**
```python
# products/models.py
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        indexes = [
            models.Index(fields=["status", "name"]),
        ]

    def __str__(self) -> str:
        return self.name
```

```python
# products/api/schemas.py
from decimal import Decimal
from typing import Literal

from ninja import ModelSchema, Schema

from products.models import Product

ProductStatus = Literal["draft", "active", "archived"]


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "status"]


class ProductCreate(Schema):
    name: str
    description: str = ""
    price: Decimal
    stock: int = 0
    status: ProductStatus = "draft"


class ProductPatch(Schema):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    status: ProductStatus | None = None
```

```python
# products/api/selectors.py
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.all().order_by("name", "id")


def product_get(*, product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

```python
# products/api/services.py
from decimal import Decimal
from typing import Any

from django.db import transaction

from products.models import Product


def product_create(
    *,
    name: str,
    description: str,
    price: Decimal,
    stock: int,
    status: str,
) -> Product:
    with transaction.atomic():
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            status=status,
        )
        product.full_clean()
        product.save()
    return product


def product_update(*, product: Product, data: dict[str, Any]) -> Product:
    if not data:
        return product

    for field, value in data.items():
        setattr(product, field, value)

    with transaction.atomic():
        product.full_clean()
        product.save(update_fields=[*data.keys(), "updated_at"])

    return product


def product_delete(*, product: Product) -> None:
    product.delete()
```

```python
# products/api/router.py
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from ninja.security import django_auth

from products.api.schemas import ProductCreate, ProductOut, ProductPatch
from products.api.selectors import product_get, product_list
from products.api.services import product_create, product_delete, product_update

router = Router(tags=["products"], auth=django_auth)


@router.get("/", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request):
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request, product_id: int) -> ProductOut:
    return product_get(product_id=product_id)


@router.post("/", response={201: ProductOut})
def create_product(request, payload: ProductCreate) -> tuple[int, ProductOut]:
    product = product_create(**payload.dict())
    return 201, product


@router.patch("/{product_id}", response=ProductOut)
def patch_product(
    request,
    product_id: int,
    payload: ProductPatch,
) -> ProductOut:
    product = product_get(product_id=product_id)
    data = payload.dict(exclude_unset=True, exclude_none=True)
    return product_update(product=product, data=data)


@router.delete("/{product_id}", response={204: None})
def delete_product(request, product_id: int) -> tuple[int, None]:
    product = product_get(product_id=product_id)
    product_delete(product=product)
    return 204, None
```

```python
# products/api/__init__.py
from products.api.router import router

__all__ = ["router"]
```

```python
# config/api.py
from django.http import Http404, JsonResponse
from ninja import NinjaAPI
from ninja.errors import HttpError

from products.api import router as products_router

api = NinjaAPI(title="Product API", version="1.0.0")
api.add_router("/products/", products_router)


def problem_response(request, *, status: int, title: str, detail: str):
    return JsonResponse(
        {
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail,
            "instance": request.path,
        },
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(Http404)
def handle_not_found(request, exc):
    return problem_response(
        request,
        status=404,
        title="Not Found",
        detail="The requested product was not found.",
    )


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    return problem_response(
        request,
        status=exc.status_code,
        title=str(exc),
        detail=str(exc),
    )
```

```python
# config/urls.py
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

실행 명령은 다음 순서입니다.

```bash
python manage.py makemigrations products
python manage.py migrate
pytest tests/isolated/integration/test_products_api.py
```

**REFACTOR 방향**
다음 단계에서는 `FilterSchema`로 `status`, `name` 검색을 추가하고, 상품 수가 커지면 cursor pagination으로 바꾸는 편이 좋습니다. 재고 차감처럼 동시성 영향을 받는 동작이 생기면 단순 `stock` 수정이 아니라 `F()` 표현식 기반 서비스 함수로 별도 분리해야 합니다.

---
> **관련 스킬 참조:**
> - API 구현/테스트 → **implementation-django-ninja** 스킬
> - REST 상태 코드/오류 형식 → **architecture-api** 스킬
> - 서비스/셀렉터 분리 → **implementation-django** 스킬