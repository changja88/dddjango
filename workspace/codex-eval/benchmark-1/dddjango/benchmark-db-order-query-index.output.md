## [주요 내용]

관리자 주문 목록이 느릴 때는 먼저 “관리자가 실제로 쓰는 필터 + 정렬 + 표시 컬럼” 조합을 기준으로 봐야 합니다. 인덱스는 테이블 구조가 아니라 쿼리 워크로드에 맞춰야 합니다.

가장 흔한 관리자 주문 목록 쿼리는 대략 이 형태입니다.

```python
Order.objects.filter(
    status=...,
    created_at__gte=...,
    created_at__lt=...,
).order_by("-created_at")
```

이 경우 우선 검토할 인덱스는 다음입니다.

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "결제대기"
        PAID = "paid", "결제완료"
        SHIPPED = "shipped", "배송중"
        CANCELLED = "cancelled", "취소"

    status = models.CharField(max_length=20, choices=Status)
    created_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)

    class Meta:
        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="idx_order_status_created",
            ),
            models.Index(
                fields=["-created_at"],
                name="idx_order_created_desc",
            ),
            models.Index(
                fields=["paid_at"],
                name="idx_order_paid_at",
            ),
        ]
```

복합 인덱스 순서는 보통 `=` 조건이 먼저, 범위/정렬 컬럼이 뒤입니다. 예를 들어 `status = 'paid' AND created_at BETWEEN ... ORDER BY created_at DESC`라면 `["status", "-created_at"]`가 자연스럽습니다. `created_at`만으로 최신 주문 목록을 자주 보면 `["-created_at"]` 단독 인덱스도 검토합니다.

멀티테넌트나 입점사별 관리자 화면이면 `store`, `seller`, `tenant`, `site` 같은 범위 제한 컬럼을 맨 앞에 둡니다.

```python
models.Index(
    fields=["store", "status", "-created_at"],
    name="idx_order_store_status_created",
)
```

삭제되지 않은 주문만 본다면 PostgreSQL에서는 부분 인덱스가 더 낫습니다.

```python
models.Index(
    fields=["status", "-created_at"],
    name="idx_order_active_status_created",
    condition=models.Q(deleted_at__isnull=True),
)
```

관리자 검색도 중요합니다. `order_number`처럼 정확히 찾는 값은 `unique=True` 또는 단일 인덱스가 맞습니다. 반면 `customer__email__icontains`, `customer__name__icontains`처럼 `%검색어%` 패턴은 일반 B-tree 인덱스를 거의 못 씁니다. PostgreSQL이라면 `pg_trgm` 기반 `GinIndex`를 검토해야 합니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity

class Customer(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)

    class Meta:
        indexes = [
            GinIndex(
                fields=["email"],
                name="idx_customer_email_trgm",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                fields=["name"],
                name="idx_customer_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]
```

Django admin 또는 관리자 전용 selector에서는 N+1 제거가 1순위입니다.

```python
# orders/selectors.py

from django.db.models import Prefetch, QuerySet

from orders.models import Order, OrderItem


def admin_order_list_queryset() -> QuerySet[Order]:
    return (
        Order.objects.select_related(
            "customer",
            "payment",
            "shipping_address",
        )
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product").only(
                    "id",
                    "order_id",
                    "product_id",
                    "quantity",
                    "unit_price",
                    "product__id",
                    "product__name",
                ),
            )
        )
        .defer(
            "memo",
            "internal_note",
            "raw_payment_payload",
        )
        .order_by("-created_at")
    )
```

Django admin을 쓴다면 최소한 아래를 확인합니다.

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("=order_number", "customer__email")
    ordering = ("-created_at",)
    list_select_related = ("customer", "payment", "shipping_address")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("customer", "payment", "shipping_address")
            .defer("memo", "internal_note", "raw_payment_payload")
        )
```

`list_display` 안의 메서드에서 `obj.items.count()`, `obj.payment.status`, `obj.customer.profile.name` 같은 접근을 반복하면 목록 100개에서 추가 쿼리 100개가 쉽게 생깁니다. 이 경우 `select_related`, `prefetch_related`, `annotate(Count(...))`, `Exists(...)`로 목록 쿼리에 포함시키는 편이 낫습니다.

```python
from django.db.models import Count, Exists, OuterRef

Order.objects.select_related("customer").annotate(
    item_count=Count("items"),
    has_refund=Exists(
        Refund.objects.filter(order_id=OuterRef("pk"))
    ),
)
```

추가로 검토할 쿼리 개선은 다음입니다.

| 증상 | 개선 |
|---|---|
| 최신순 목록이 느림 | `created_at DESC` 인덱스, 불필요한 기본 `Meta.ordering` 제거 |
| 상태 + 기간 필터가 느림 | `status, created_at` 복합 인덱스 |
| 입점사/관리자 권한 범위가 있음 | `store, status, created_at` 또는 `tenant, created_at` |
| 주문번호 검색이 느림 | `order_number` unique/index + `=order_number` 검색 |
| 이메일/이름 부분 검색이 느림 | PostgreSQL trigram `GinIndex` |
| 결제완료/배송대기만 자주 조회 | 부분 인덱스 |
| 목록 렌더링 쿼리 수가 많음 | `select_related`, `prefetch_related`, `Prefetch` |
| 큰 JSON/Text 필드 때문에 느림 | `defer()` 또는 목록 전용 projection |
| 페이지 뒤쪽이 느림 | offset pagination 대신 keyset pagination 검토 |
| 카운트가 느림 | admin count 최적화 또는 추정 count 전략 검토 |

검증은 추측으로 끝내면 안 됩니다. Django에서 실제 SQL과 실행 계획을 확인하세요.

```python
qs = (
    Order.objects.filter(status=Order.Status.PAID)
    .filter(created_at__gte=start, created_at__lt=end)
    .order_by("-created_at")
)

print(qs.explain(analyze=True, buffers=True))
```

테스트에는 쿼리 수 회귀 방지를 넣는 게 좋습니다.

```python
def test_admin_order_list_query_count(django_assert_num_queries):
    create_orders_with_items(count=50)

    with django_assert_num_queries(3):
        list(admin_order_list_queryset()[:50])
```

정리하면, 우선순위는 `EXPLAIN ANALYZE`로 느린 쿼리 확인 → N+1 제거 → 실제 필터/정렬 조합에 맞춘 복합 인덱스 → 부분/커버링/trigram 인덱스 → 마지막으로 캐시나 비정규화입니다. 인덱스는 읽기를 빠르게 하지만 주문 생성/상태 변경 같은 쓰기 비용을 올리므로, 관리자 화면에서 실제로 자주 쓰는 조건부터 제한적으로 추가하는 편이 맞습니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리 최적화 → **implementation-django** 스킬
> - 인덱스/EXPLAIN/쿼리 성능 설계 → **architecture-db** 스킬