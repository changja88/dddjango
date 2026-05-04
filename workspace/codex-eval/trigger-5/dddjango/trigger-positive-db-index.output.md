**[주요 내용]**

현재 워크스페이스에는 주문 모델 코드가 없어, 아래는 일반적인 “주문 목록” 조회 패턴 기준 제안입니다. 핵심은 테이블 구조가 아니라 실제 `WHERE + ORDER BY + JOIN/프리페치` 조합에 맞춰 인덱스를 잡는 것입니다.

가정한 주문 목록 조회 패턴:

| 패턴 | 예시 | 권장 인덱스 |
|---|---|---|
| 최신 주문 목록 | `ORDER BY -created_at, -id` | `("-created_at", "-id")` |
| 상태별 최신 목록 | `status = ? ORDER BY -created_at, -id` | `("status", "-created_at", "-id")` |
| 고객별 주문 목록 | `customer_id = ? ORDER BY -created_at` | `("customer", "-created_at", "-id")` |
| 기간 + 상태 필터 | `status = ? AND created_at BETWEEN ...` | `("status", "-created_at", "-id")` |
| 미처리 주문만 자주 조회 | `status IN pending/paid` | PostgreSQL 부분 인덱스 |
| 주문번호 검색 | `order_number = ?` | `unique=True` 또는 단일 인덱스 |

모델 인덱스 예시는 이렇게 시작하는 것이 적절합니다.

```python
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELED = "canceled", "Canceled"

    order_number = models.CharField(max_length=32, unique=True)
    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status)
    created_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["-created_at", "-id"],
                name="order_created_id_idx",
            ),
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="order_status_created_idx",
            ),
            models.Index(
                fields=["customer", "-created_at", "-id"],
                name="order_customer_created_idx",
            ),
            models.Index(
                fields=["-created_at", "-id"],
                name="order_open_created_idx",
                condition=Q(status__in=["pending", "paid"]),
            ),
        ]
```

`status` 단독 인덱스는 보통 피합니다. 카디널리티가 낮고 목록 조회는 대부분 정렬까지 같이 하므로 `status + created_at + id` 복합 인덱스가 더 직접적입니다. 복합 인덱스 순서는 동등 조건인 `status`, `customer`를 앞에 두고, 범위/정렬 컬럼인 `created_at`, `id`를 뒤에 둡니다.

QuerySet은 목록에서 실제로 렌더링하는 관계 기준으로 나눕니다.

```python
from django.db.models import Count, Prefetch


def order_list_queryset(*, status=None, customer_id=None):
    qs = (
        Order.objects
        .select_related("customer")
        .annotate(item_count=Count("items"))
        .order_by("-created_at", "-id")
    )

    if status:
        qs = qs.filter(status=status)

    if customer_id:
        qs = qs.filter(customer_id=customer_id)

    return qs
```

`select_related()`는 `Order.customer`, `Order.payment`, `Order.shipping_address`처럼 `ForeignKey`나 `OneToOneField`에만 사용합니다. SQL `JOIN`으로 한 번에 가져오므로 목록의 각 행에서 고객명, 결제상태, 배송지 같은 단일 객체를 보여줄 때 적합합니다.

`prefetch_related()`는 `Order.items`, `Order.logs`, `Order.tags`처럼 역방향 FK나 M2M에 사용합니다. 별도 쿼리 후 Python에서 매칭하므로 주문 50개에 상품 라인들을 같이 펼쳐 보여줄 때 씁니다.

```python
def order_list_with_items_queryset():
    return (
        Order.objects
        .select_related("customer")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product").only(
                    "id",
                    "order_id",
                    "product__name",
                    "quantity",
                    "unit_price",
                ),
                to_attr="prefetched_items",
            )
        )
        .order_by("-created_at", "-id")
    )
```

단, 목록에서 “상품 수”만 필요하면 `prefetch_related("items")`보다 `annotate(Count("items"))`가 낫습니다. 실제 item row를 화면에 그릴 때만 prefetch를 붙이세요.

측정 기준은 다음으로 잡습니다.

```python
with self.assertNumQueries(2):
    list(order_list_with_items_queryset()[:50])
```

검증 절차:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
FROM orders_order
WHERE status = 'paid'
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

통과 기준은 목록 페이지 기준으로 잡습니다: 페이지 크기 50에서 쿼리 수가 고정값이어야 하고, `select_related`만 쓰는 목록은 1쿼리, item prefetch 포함 목록은 2-3쿼리 이내가 적절합니다. 대형 주문 테이블에서 주요 목록 쿼리가 `Seq Scan`으로 떨어지면 인덱스 재검토 대상입니다. `actual rows`와 예상 `rows`가 크게 어긋나면 `ANALYZE`로 통계를 갱신한 뒤 다시 봅니다. 운영 기준은 p95 latency, `Buffers: shared read`, 정렬 단계 발생 여부를 함께 봐야 합니다.

---
> **관련 스킬 참조:**
> - 쿼리 실측/인덱스 검증 → **architecture-db** 스킬
> - Django QuerySet/selector 리팩터링 → **implementation-django** 스킬