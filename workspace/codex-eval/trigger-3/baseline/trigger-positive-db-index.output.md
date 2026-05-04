현재 `/private/tmp/dddjango-codex-eval`에는 Django 코드가 없어 실제 모델 기준으로 검토하진 못했습니다. 아래는 일반적인 `Order` 목록 조회 기준의 권장 전략입니다.

**주요 내용**

주문 목록 조회는 보통 다음 패턴이 많습니다.

```python
Order.objects.filter(
    user=request.user,
    status=...,
    created_at__gte=...,
    created_at__lte=...,
).order_by("-created_at", "-id")
```

이 경우 핵심 인덱스는 “필터 + 정렬”을 같이 태우는 복합 인덱스입니다.

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["user", "status", "-created_at", "-id"],
                name="idx_order_user_status_created",
            ),
            models.Index(
                fields=["user", "-created_at", "-id"],
                name="idx_order_user_created",
            ),
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="idx_order_status_created",
            ),
        ]
```

컬럼 순서는 보통 `=` 조건이 먼저, 범위/정렬 컬럼이 뒤입니다. 예를 들어 `user = ? AND status = ? ORDER BY created_at DESC`라면 `user, status, -created_at` 순서가 맞습니다. `created_at`을 맨 앞에 두면 `user/status` 필터 효율이 떨어질 수 있습니다.

soft delete를 쓴다면 PostgreSQL에서는 부분 인덱스를 권장합니다.

```python
from django.db import models
from django.db.models import Q

class Meta:
    indexes = [
        models.Index(
            fields=["user", "status", "-created_at", "-id"],
            name="idx_order_active_user_status",
            condition=Q(deleted_at__isnull=True),
        ),
    ]
```

주문번호 검색이 많으면 `order_number`에는 `unique=True` 또는 `db_index=True`가 적절합니다. 다만 `icontains` 검색은 일반 B-tree 인덱스를 잘 못 탑니다. PostgreSQL이면 `pg_trgm` + `GinIndex`를 따로 검토해야 합니다.

QuerySet 쪽은 목록에 필요한 관계를 명확히 분리하는 게 중요합니다.

```python
orders = (
    Order.objects
    .filter(user=request.user, deleted_at__isnull=True)
    .select_related("user", "payment", "shipping_address")
    .prefetch_related("items", "items__product")
    .order_by("-created_at", "-id")
)
```

기준은 단순합니다.

`select_related()`:
FK, OneToOne처럼 한 주문당 하나만 붙는 관계. 예: `user`, `payment`, `shipping_address`.

`prefetch_related()`:
역참조 FK, M2M처럼 여러 개가 붙는 관계. 예: `items`, `items__product`, `coupons`.

주문 목록 화면에서 상품명/수량 정도만 필요하다면 `Prefetch`로 필요한 컬럼만 제한합니다.

```python
from django.db.models import Prefetch

orders = (
    Order.objects
    .select_related("user", "payment")
    .prefetch_related(
        Prefetch(
            "items",
            queryset=OrderItem.objects.select_related("product").only(
                "id",
                "order_id",
                "quantity",
                "price",
                "product__id",
                "product__name",
            ),
        )
    )
)
```

페이지네이션은 offset이 깊어질수록 느려집니다. 주문 목록처럼 최신순 무한스크롤이면 keyset pagination을 우선 검토하세요.

```python
orders = Order.objects.filter(deleted_at__isnull=True)

if cursor_created_at and cursor_id:
    orders = orders.filter(
        Q(created_at__lt=cursor_created_at)
        | Q(created_at=cursor_created_at, id__lt=cursor_id)
    )

orders = orders.order_by("-created_at", "-id")[:50]
```

이 방식은 `("-created_at", "-id")` 정렬과 같은 복합 인덱스가 있을 때 안정적입니다.

집계가 필요하면 Python 루프 대신 DB에서 처리합니다.

```python
from django.db.models import Count, Sum

orders = Order.objects.annotate(
    item_count=Count("items"),
    total_quantity=Sum("items__quantity"),
)
```

다만 목록마다 복잡한 `annotate()`가 반복되면 조인 비용이 커질 수 있으니, 자주 필요한 값은 `Order.total_amount`, `Order.item_count` 같은 파생 컬럼으로 보관하는 것도 검토할 수 있습니다. 이건 인덱스와 쿼리 최적화 후에도 부족할 때 적용하는 마지막 단계에 가깝습니다.

검증은 추측이 아니라 실제 실행계획으로 해야 합니다.

```python
qs = Order.objects.filter(
    user=user,
    status=Order.Status.PAID,
).order_by("-created_at", "-id")

print(qs.explain(analyze=True, buffers=True))
```

확인할 것:

- `Seq Scan`이 큰 테이블에서 발생하는지
- `Index Scan` 또는 `Index Only Scan`을 타는지
- 정렬에 `Sort`가 별도로 발생하는지
- 예상 rows와 실제 rows 차이가 큰지
- `buffers`에서 불필요한 heap read가 많은지

테스트에는 쿼리 수 회귀 방지를 넣는 게 좋습니다.

```python
with self.assertNumQueries(3):
    list(get_order_list_queryset(user)[:20])
```

권장 순서는 이렇습니다.

1. 실제 목록 필터/정렬 조건을 확정한다.
2. `select_related`, `prefetch_related`, `Prefetch`로 N+1을 제거한다.
3. 필터와 정렬을 함께 만족하는 복합 인덱스를 추가한다.
4. `EXPLAIN ANALYZE`로 인덱스 사용 여부를 확인한다.
5. offset pagination이 병목이면 keyset pagination으로 바꾼다.
6. 그래도 부족하면 캐시나 파생 컬럼을 검토한다.

---
> **관련 스킬 참조:**
> - 인덱스/실행계획 검증 → **architecture-db** 스킬
> - Django QuerySet/selectors 최적화 → **implementation-django** 스킬