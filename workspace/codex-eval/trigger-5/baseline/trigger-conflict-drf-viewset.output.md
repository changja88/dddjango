이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다. 현재 워크스페이스가 비어 있고 read-only라 파일 생성/테스트 실행은 못 했습니다. 아래는 `products` 앱 기준으로 바로 넣을 수 있는 상품 CRUD API입니다.

**주요 내용**

`products/models.py`

```python
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
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name
```

`products/api/selectors.py`

```python
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from products.models import Product


def product_list() -> QuerySet[Product]:
    return Product.objects.all()


def product_get(product_id: int) -> Product:
    return get_object_or_404(Product, id=product_id)
```

`products/api/schemas.py`

```python
from ninja import ModelSchema

from products.models import Product


class ProductIn(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "status"]


class ProductPatch(ModelSchema):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "status"]
        fields_optional = "__all__"


class ProductOut(ModelSchema):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "status",
            "created_at",
            "updated_at",
        ]


class ProblemDetail(ModelSchema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
```

`products/api/router.py`

```python
from typing import Any

from django.http import HttpRequest
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from ninja.security import django_auth

from products.api.schemas import ProductIn, ProductOut, ProductPatch
from products.api.selectors import product_get, product_list
from products.models import Product

router = Router(tags=["products"], auth=django_auth)


@router.get("", response=list[ProductOut])
@paginate(LimitOffsetPagination)
def list_products(request: HttpRequest) -> Any:
    return product_list()


@router.get("/{product_id}", response=ProductOut)
def get_product(request: HttpRequest, product_id: int) -> Product:
    return product_get(product_id)


@router.post("", response={201: ProductOut})
def create_product(request: HttpRequest, payload: ProductIn) -> tuple[int, Product]:
    product = Product.objects.create(**payload.dict())
    return 201, product


@router.patch("/{product_id}", response=ProductOut)
def update_product(
    request: HttpRequest,
    product_id: int,
    payload: ProductPatch,
) -> Product:
    product = product_get(product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(product, field, value)

    product.full_clean()
    product.save()
    return product


@router.delete("/{product_id}", response={204: None})
def delete_product(request: HttpRequest, product_id: int) -> tuple[int, None]:
    product = product_get(product_id)
    product.delete()
    return 204, None
```

`config/api.py`

```python
from ninja import NinjaAPI

from products.api.router import router as products_router

api = NinjaAPI(title="Product API", version="1.0.0")
api.add_router("/products", products_router)
```

`config/urls.py`

```python
from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
```

실행 확인은 실제 프로젝트 파일에 반영한 뒤 다음 순서로 보면 됩니다.

```bash
python manage.py makemigrations products
python manage.py migrate
python manage.py runserver
```

---
> **관련 스킬 참조:**
> - DRF 대체 API 구현 → **implementation-django-ninja** 스킬