`config.toml`은 `/private/tmp/dddjango-codex-eval`에 없어 확인하지 못했습니다. 아래는 일반적인 Django 주문 목록 조회 기준의 전략입니다. 전제는 `Order`가 `customer`, `status`, `created_at`, `deleted_at`, `total_amount` 등을 갖고 있고, 목록은 `-created_at, -id`로 정렬된다는 것입니다.

**주요 내용**

먼저 최적화 순서는 `느린 쿼리 확인 → QuerySet 수정 → 인덱스 추가 → 캐시/비정규화`가 맞습니다. 주문 목록은 보통 쓰기도 많은 테이블이라 인덱스를 많이 붙이면 조회는 빨라지지만 주문 생성, 상태 변경, 결제 처리의 쓰기 비용이 올라갑니다. `EXPLAIN ANALYZE`와 실제 목록 필터 조합을 기준으로 추가해야 합니다.

대표 인덱스는 “필터 조건 + 정렬 조건”을 한 묶음으로 잡습니다.

```python
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "결제 대기"
        PAID = "paid", "결제 완료"
        SHIPPING = "shipping", "배송 중"
        COMPLETED = "completed", "완료"
        CANCELED = "canceled", "취소"

    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices)
    order_number = models.CharField(max_length=32, unique=True)
    total_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            # 내 주문 목록: WHERE customer_id = ? ORDER BY created_at DESC, id DESC
            models.Index(
                fields=["customer", "-created_at", "-id"],
                name="idx_order_customer_recent",
            ),
            # 운영자/CS 상태별 목록: WHERE status = ? ORDER BY created_at DESC, id DESC
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="idx_order_status_recent",
            ),
            # soft delete를 쓴다면 활성 주문만 대상으로 하는 부분 인덱스
            models.Index(
                fields=["customer", "-created_at", "-id"],
                name="idx_order_customer_active",
                condition=Q(deleted_at__isnull=True),
            ),
            # PostgreSQL에서 목록 카드가 인덱스만으로 처리될 가능성을 높임
            models.Index(
                fields=["status", "-created_at", "-id"],
                include=["order_number", "total_amount"],
                name="idx_order_status_cover",
            ),
        ]
```

인덱스 컬럼 순서는 보통 `동등 조건 → 범위 조건 → 정렬 조건`입니다. 예를 들어 `WHERE customer_id = ? AND status = ? AND created_at BETWEEN ... ORDER BY created_at DESC, id DESC`가 핵심 쿼리라면 다음이 더 적합합니다.

```python
models.Index(
    fields=["customer", "status", "-created_at", "-id"],
    name="idx_order_customer_status_recent",
)
```

반대로 `status` 단독 인덱스는 대개 효과가 낮습니다. 상태값은 카디널리티가 낮아서 단독으로는 많은 행을 읽게 됩니다. `status + created_at`처럼 목록 정렬과 같이 묶어야 의미가 있습니다.

QuerySet 쪽은 read 전용 selector로 분리하는 편이 좋습니다.

```python
# apps/orders/api/selectors.py 또는 apps/orders/selectors.py

from django.db.models import Count, Prefetch

from apps.orders.models import Order, OrderItem


def order_list_for_customer(*, customer, status=None, cursor=None, limit=20):
    queryset = (
        Order.objects
        .filter(customer=customer, deleted_at__isnull=True)
        .select_related("customer", "payment")
        .annotate(item_count=Count("items"))
        .only(
            "id",
            "order_number",
            "status",
            "total_amount",
            "created_at",
            "customer_id",
            "payment_id",
        )
        .order_by("-created_at", "-id")
    )

    if status:
        queryset = queryset.filter(status=status)

    if cursor:
        queryset = queryset.filter(
            created_at__lt=cursor.created_at,
        )

    return queryset[:limit]
```

목록에서 주문 상품 일부를 보여줘야 한다면 `prefetch_related()`를 조건부로 씁니다. `items.product`는 역참조 FK이므로 `select_related()`가 아니라 `Prefetch()`가 맞습니다.

```python
def order_list_with_items_for_customer(*, customer, limit=20):
    item_queryset = (
        OrderItem.objects
        .select_related("product")
        .only(
            "id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "product__name",
            "product__thumbnail_url",
        )
    )

    return (
        Order.objects
        .filter(customer=customer, deleted_at__isnull=True)
        .select_related("payment")
        .prefetch_related(
            Prefetch("items", queryset=item_queryset, to_attr="prefetched_items")
        )
        .order_by("-created_at", "-id")[:limit]
    )
```

주의할 점은 `only()`를 썼는데 템플릿이나 Schema 변환에서 빠진 필드를 접근하면 추가 쿼리가 발생한다는 것입니다. 실제 응답 필드와 정확히 맞춰야 합니다.

페이지네이션은 주문 테이블이 커질수록 offset 기반보다 keyset/cursor 기반이 유리합니다.

```python
from django.db.models import Q


def apply_order_cursor(queryset, *, created_at, order_id):
    return queryset.filter(
        Q(created_at__lt=created_at)
        | Q(created_at=created_at, id__lt=order_id)
    )
```

이 경우 인덱스도 정렬과 맞춰야 합니다.

```python
models.Index(
    fields=["customer", "-created_at", "-id"],
    name="idx_order_customer_cursor",
)
```

검색 조건이 있다면 구분해야 합니다. `order_number = ?`는 `unique=True`나 단일 인덱스로 충분합니다. 하지만 `order_number__icontains`, 수령자명 부분 검색, 상품명 검색은 일반 B-tree 인덱스가 잘 안 맞습니다. PostgreSQL이면 `pg_trgm` 기반 trigram index 또는 별도 검색 전략을 검토해야 합니다. 주문 목록 기본 쿼리에 무리하게 `icontains`를 섞으면 인덱스가 무력화되기 쉽습니다.

검증은 반드시 쿼리 수와 실행 계획으로 봅니다.

```python
def test_order_list_query_count(django_assert_num_queries, customer, order_factory):
    order_factory.create_batch(30, customer=customer)

    with django_assert_num_queries(2):
        orders = list(order_list_with_items_for_customer(customer=customer))
        for order in orders:
            list(order.prefetched_items)
```

운영 SQL은 다음 기준으로 확인합니다.

```sql
EXPLAIN ANALYZE
SELECT ...
FROM orders_order
WHERE customer_id = 123
  AND deleted_at IS NULL
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

확인 포인트는 `Seq Scan`이 대형 주문 테이블에서 발생하는지, 예상 rows와 actual rows가 크게 다른지, `Sort`가 따로 발생하는지, `Index Scan` 또는 `Index Only Scan`으로 가는지입니다. 예상 rows가 크게 틀리면 인덱스보다 먼저 통계 갱신과 쿼리 조건을 확인해야 합니다.

요약하면, 주문 목록의 1차 추천 조합은 다음입니다.

```python
# 사용자별 최신 주문
["customer", "-created_at", "-id"]

# 사용자 + 상태 필터가 자주 쓰이면
["customer", "status", "-created_at", "-id"]

# 운영자 상태별 주문 처리 화면
["status", "-created_at", "-id"]

# soft delete가 있고 대부분 deleted_at IS NULL만 조회하면
condition=Q(deleted_at__isnull=True)

# PostgreSQL이고 목록 응답 필드가 작고 고정적이면
include=["order_number", "total_amount"]
```

---
> **관련 스킬 참조:**
> - QuerySet 최적화와 selector 패턴 → **implementation-django** 스킬
> - 복합/부분/커버링 인덱스와 EXPLAIN 분석 → **architecture-db** 스킬