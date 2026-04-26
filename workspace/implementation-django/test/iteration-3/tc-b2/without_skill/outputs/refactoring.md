# 가격 일괄 변경 코드 리팩토링

## 원본 코드의 문제점

1. **N+1 쿼리 문제**: `for` 루프 안에서 개별 `save()` 호출 -- 상품 10만 개면 SELECT 1회 + UPDATE 10만 회 = 총 100,001회 DB 호출
2. **메모리 과다 사용**: `filter()`가 QuerySet을 반환하지만, 루프 진입 시 전체 10만 개 객체를 한 번에 메모리에 로드
3. **불필요한 Python 연산**: 가격 계산을 Python에서 수행하지만, DB에서 직접 처리 가능

## 리팩토링 결과

```python
from decimal import Decimal
from datetime import timedelta
from django.db import models
from django.db.models import F
from django.utils import timezone


def update_prices(category_id, increase_percent):
    """
    카테고리별 가격 일괄 변경.

    F() 표현식으로 DB 레벨에서 단일 UPDATE 쿼리 실행.
    기존: SELECT 1회 + UPDATE 10만 회 -> 개선: UPDATE 1회
    """
    return Product.objects.filter(category_id=category_id).update(
        price=F('price') * (1 + Decimal(str(increase_percent)) / 100),
        updated_at=timezone.now(),
    )


def create_sample_products(names, category):
    """
    샘플 상품 일괄 생성.

    bulk_create로 단일 INSERT 쿼리 실행.
    기존: INSERT N회 -> 개선: INSERT 1회 (batch_size로 메모리 제어)
    """
    products = [
        Product(
            name=name,
            category=category,
            price=Decimal('10000'),
        )
        for name in names
    ]
    return Product.objects.bulk_create(products, batch_size=1000)


def deactivate_old_products(days=365):
    """
    오래된 상품 비활성화.

    단일 UPDATE 쿼리로 처리.
    기존: SELECT 1회 + UPDATE N회 -> 개선: UPDATE 1회
    """
    cutoff = timezone.now() - timedelta(days=days)
    return Product.objects.filter(
        updated_at__lt=cutoff,
        is_active=True,
    ).update(is_active=False)
```

## 변경 사항 요약

### update_prices

| 항목 | Before | After |
|------|--------|-------|
| DB 호출 | 100,001회 (SELECT 1 + UPDATE 100,000) | 1회 (UPDATE 1) |
| 방식 | Python 루프 + 개별 save() | `QuerySet.update()` + `F()` 표현식 |
| 소수점 처리 | `increase_percent / 100` (float 연산) | `Decimal(str(increase_percent)) / 100` (정확한 소수 연산) |

- `F('price')`를 사용하면 DB가 직접 현재 price 값을 읽어서 계산하므로, Python으로 객체를 가져올 필요가 없다.
- `QuerySet.update()`는 단일 `UPDATE ... SET ... WHERE ...` SQL을 실행한다.

### create_sample_products

| 항목 | Before | After |
|------|--------|-------|
| DB 호출 | N회 (INSERT N) | ceil(N/1000)회 |
| 방식 | 루프 내 `objects.create()` | `bulk_create(batch_size=1000)` |

- `bulk_create`는 여러 행을 하나의 INSERT 문으로 묶는다.
- `batch_size=1000`으로 메모리 사용량을 제어한다.

### deactivate_old_products

| 항목 | Before | After |
|------|--------|-------|
| DB 호출 | N+1회 (SELECT 1 + UPDATE N) | 1회 (UPDATE 1) |
| 방식 | Python 루프 + 개별 save() | `QuerySet.update()` |

## 주의 사항

- `QuerySet.update()`와 `bulk_create()`는 `save()` 메서드와 시그널(`pre_save`, `post_save`)을 호출하지 않는다. 시그널에 의존하는 로직이 있다면 별도 처리가 필요하다.
- `F()` 표현식은 race condition을 방지한다. 두 요청이 동시에 가격을 변경해도 각각 DB의 현재 값을 기준으로 계산한다.
- `bulk_create`의 반환값에서 `id`가 채워지려면 PostgreSQL이 필요하다. MySQL/SQLite에서는 `id`가 `None`일 수 있다.
