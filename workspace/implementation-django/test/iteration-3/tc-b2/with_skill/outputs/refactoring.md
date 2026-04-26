# Refactoring: 가격 일괄 변경 및 배치 처리 코드

## Change 1: 개별 save() 루프를 F() 표현식 기반 update()로 교체

[Before]
```python
def update_prices(category_id, increase_percent):
    products = Product.objects.filter(category_id=category_id)
    for product in products:
        product.price = product.price * (1 + increase_percent / 100)
        product.updated_at = timezone.now()
        product.save()
    return products.count()
```

[After]
```python
def update_prices(category_id, increase_percent):
    return Product.objects.filter(category_id=category_id).update(
        price=F("price") * (1 + increase_percent / 100),
        updated_at=Now(),
    )
```

[Reason] Individual save() in loop -> REPLACE with update() -- 10만 개 상품에 대해 개별 `save()`를 호출하면 10만 번의 UPDATE 쿼리가 발생한다. `QuerySet.update()`와 `F()` 표현식을 사용하면 단일 SQL UPDATE 문으로 처리되어 30분 걸리던 작업이 수 초 이내로 완료된다. `F("price")`는 Python으로 값을 가져오지 않고 DB 레벨에서 연산하므로 race condition도 방지된다. `Now()`는 DB 서버 시각을 사용하여 일관성을 보장한다. `update()`는 영향받은 행 수를 반환하므로 별도의 `count()` 쿼리도 불필요하다.

## Change 2: 개별 create() 루프를 bulk_create()로 교체

[Before]
```python
def create_sample_products(names, category):
    products = []
    for name in names:
        p = Product.objects.create(
            name=name,
            category=category,
            price=Decimal('10000'),
        )
        products.append(p)
    return products
```

[After]
```python
def create_sample_products(names, category):
    products = Product.objects.bulk_create(
        [
            Product(name=name, category=category, price=Decimal("10000"))
            for name in names
        ],
        batch_size=500,
    )
    return products
```

[Reason] Individual save() in loop -> REPLACE with bulk_create() -- 루프 안에서 `objects.create()`를 호출하면 이름 개수만큼 INSERT 쿼리가 발생한다. `bulk_create()`는 한 번의 SQL INSERT로 다수의 행을 삽입한다. `batch_size=500`으로 메모리 사용량을 제어하면서도 쿼리 횟수를 N에서 ceil(N/500)으로 줄인다.

## Change 3: 비활성화 루프를 단일 update()로 교체

[Before]
```python
def deactivate_old_products(days=365):
    cutoff = timezone.now() - timedelta(days=days)
    products = Product.objects.filter(
        updated_at__lt=cutoff,
        is_active=True
    )
    for product in products:
        product.is_active = False
        product.save()
```

[After]
```python
def deactivate_old_products(days=365):
    cutoff = timezone.now() - timedelta(days=days)
    return Product.objects.filter(
        updated_at__lt=cutoff,
        is_active=True,
    ).update(is_active=False)
```

[Reason] Individual save() in loop -> REPLACE with update() -- 단일 필드를 동일한 값으로 변경하는 작업은 `update()`의 가장 직관적인 사용 사례다. 개별 `save()`는 모든 필드를 UPDATE 절에 포함하지만(`save(update_fields=...)`를 쓰지 않은 경우), `update()`는 지정한 필드만 변경한다. 반환값으로 영향받은 행 수를 얻을 수 있어 로깅이나 후속 처리에 활용 가능하다.

---

## Complete Refactored Code

```python
from decimal import Decimal
from datetime import timedelta

from django.db.models import F
from django.db.models.functions import Now
from django.utils import timezone

from .models import Product


def update_prices(category_id, increase_percent):
    return Product.objects.filter(category_id=category_id).update(
        price=F("price") * (1 + increase_percent / 100),
        updated_at=Now(),
    )


def create_sample_products(names, category):
    products = Product.objects.bulk_create(
        [
            Product(name=name, category=category, price=Decimal("10000"))
            for name in names
        ],
        batch_size=500,
    )
    return products


def deactivate_old_products(days=365):
    cutoff = timezone.now() - timedelta(days=days)
    return Product.objects.filter(
        updated_at__lt=cutoff,
        is_active=True,
    ).update(is_active=False)
```
