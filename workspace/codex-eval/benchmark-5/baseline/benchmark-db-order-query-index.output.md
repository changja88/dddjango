지정된 fixture path(`/Users/hyun/Desktop/dddjango/none`)는 존재하지 않았습니다. 대신 저장소 안의 Django fixture인 [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:5)를 읽었습니다. 관리자 주문 목록 코드는 없어서, 현재 `Order` 필드(`customer_email`, `status`, `created_at`, `paid_at`, `cancelled_at`, `total_amount`) 기준으로 검토할 항목은 아래입니다.

**검토 제안**

1. 관리자 기본 정렬이 최신 주문순이면 `created_at` 단독 또는 복합 인덱스가 우선입니다.

```python
class Order(models.Model):
    ...

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="order_created_desc_idx"),
        ]
```

2. 목록에서 상태 필터와 최신순 정렬을 같이 쓴다면 단독 `status`보다 `(status, -created_at)` 복합 인덱스를 먼저 검토하세요.

```python
models.Index(
    fields=["status", "-created_at"],
    name="order_status_created_idx",
)
```

예상 ORM:

```python
Order.objects.filter(status=Order.STATUS_PAID).order_by("-created_at")
```

3. 기간 필터가 자주 붙으면 `created_at` 범위 조건과 정렬이 같은 방향으로 타는지 `EXPLAIN`으로 확인하세요.

```python
Order.objects.filter(
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at")
```

상태 + 기간이 함께 쓰이면 `(status, -created_at)`가 더 유리할 가능성이 큽니다.

4. `customer_email` 검색이 관리자 `search_fields`에 있다면 `icontains` 기본 검색은 일반 btree 인덱스를 거의 못 씁니다. PostgreSQL이면 trigram 인덱스를 검토하세요.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramExtension

# migration에서 TrigramExtension 추가 후
GinIndex(
    fields=["customer_email"],
    name="order_email_trgm_idx",
    opclasses=["gin_trgm_ops"],
)
```

가능하면 관리자 검색은 prefix 검색으로 제한해 `customer_email__istartswith` 형태로 바꾸는 것도 검토할 만합니다.

5. 목록에 예약 수량, 상품명, SKU 같은 역방향 관계 정보가 표시되면 N+1을 막아야 합니다. 현재 `Reservation.order`와 `Reservation.product` FK가 있으므로 주문 목록에서 예약/상품을 보여줄 경우 `Prefetch + select_related` 조합이 맞습니다.

```python
from django.db.models import Prefetch

Order.objects.prefetch_related(
    Prefetch(
        "reservation_set",
        queryset=Reservation.objects.select_related("product").only(
            "id", "order_id", "product_id", "quantity",
            "product__sku", "product__name",
        ),
    )
)
```

6. 관리자 `list_display`에서 총 예약 수, 총 수량만 필요하면 Python 루프 대신 `annotate()`를 쓰는 쪽을 검토하세요.

```python
from django.db.models import Count, Sum

Order.objects.annotate(
    reservation_count=Count("reservation"),
    reserved_quantity=Sum("reservation__quantity"),
)
```

다만 정렬까지 `reservation_count`로 한다면 조인/집계 비용이 커질 수 있어 실제 관리자 요구에 따라 별도 읽기 모델이나 캐시 컬럼도 검토 대상입니다.

7. Django admin 쪽에서는 이런 형태가 기본 출발점입니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_email", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_email",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ()
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "id",
            "customer_email",
            "status",
            "total_amount",
            "created_at",
        )
```

핵심은 추측으로 인덱스를 많이 추가하지 않는 것입니다. 실제 관리자에서 가장 느린 쿼리를 `queryset.explain(analyze=True, buffers=True)` 또는 DB slow query log로 확인한 뒤, `status + created_at`, `created_at`, `customer_email 검색 방식`, 역방향 `Reservation` 접근으로 인한 N+1 순서로 좁혀 보는 게 좋습니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리 최적화 → **implementation-django** 스킬