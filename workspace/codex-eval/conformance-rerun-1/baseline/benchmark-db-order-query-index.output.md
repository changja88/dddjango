관리자 주문 목록이 느릴 때는 “admin이 실제로 어떤 WHERE / ORDER BY / JOIN / COUNT를 만드는지”부터 확인한 뒤, 그 패턴에 맞춰 인덱스와 ORM을 같이 조정하는 게 좋습니다.

**조회 패턴 확인**

우선 Django admin 주문 목록에서 자주 발생하는 조건을 분리해서 봅니다.

- 기본 정렬: 보통 `ORDER BY -created_at`, `ORDER BY -id`
- 상태 필터: `status`, `payment_status`, `fulfillment_status`
- 기간 필터: `created_at`, `paid_at`, `updated_at`
- 고객/상점 필터: `user_id`, `customer_id`, `store_id`
- 검색: `order_number`, `user__email`, `user__name`, `phone`
- 리스트 표시 JOIN: `user`, `payment`, `shipping_address`, `items` 등
- admin 페이지네이션용 `COUNT(*)`

Django admin에서는 다음 항목이 성능에 직접 영향 줍니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_display = (...)
    list_filter = (...)
    search_fields = (...)
    ordering = ("-created_at",)
    list_select_related = ("user",)
    show_full_result_count = False
```

`show_full_result_count = False`는 대량 테이블에서 admin 검색/필터 시 전체 개수 카운트를 줄이는 데 도움이 됩니다.

**검토할 인덱스**

가장 먼저 볼 후보는 admin의 기본 정렬과 필터 조합입니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["payment_status", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]
```

자주 `store_id + status + created_at` 형태로 조회한다면 복합 인덱스가 더 효과적입니다.

```python
models.Index(fields=["store", "status", "-created_at"])
```

기간 필터가 항상 들어가고 상태도 함께 쓰이면:

```python
models.Index(fields=["status", "created_at"])
```

PostgreSQL에서 “최근 주문 중 미처리 주문”처럼 특정 상태만 압도적으로 자주 본다면 partial index도 검토할 만합니다.

```python
models.Index(
    fields=["-created_at"],
    name="order_pending_created_idx",
    condition=models.Q(status="pending"),
)
```

검색 필드는 별도로 봐야 합니다. `order_number`처럼 exact/prefix 검색이면 일반 btree 인덱스가 유효합니다.

```python
models.Index(fields=["order_number"])
```

하지만 `icontains` 검색, 예를 들어 admin의 `search_fields = ("user__email",)` 또는 `("^order_number",)`가 아닌 기본 검색은 DB에 따라 인덱스를 못 탈 수 있습니다. PostgreSQL에서 `icontains`가 많으면 `pg_trgm` + GIN 인덱스를 검토합니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):
    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name="order",
            index=GinIndex(
                name="order_number_trgm_idx",
                fields=["order_number"],
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
```

**ORM 쿼리 개선**

admin 목록에서 FK를 표시한다면 `select_related`를 우선 적용합니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("user", "payment")
```

`get_queryset()`을 쓴다면 명시적으로:

```python
def get_queryset(self, request):
    qs = super().get_queryset(request)
    return qs.select_related("user", "payment")
```

역참조나 M2M, 주문 아이템 집계가 필요하면 `prefetch_related`를 쓰되, admin 목록에서 모든 주문의 모든 아이템을 가져오는 구조는 피하는 게 좋습니다.

```python
return qs.prefetch_related(
    Prefetch("items", queryset=OrderItem.objects.select_related("product"))
)
```

`list_display` 메서드 안에서 매 행마다 `.count()`, `.exists()`, `.first()`, `.aggregate()`를 호출하면 N+1이 됩니다. 이 경우 `annotate()`로 목록 쿼리에 합칩니다.

```python
from django.db.models import Count, Sum

def get_queryset(self, request):
    return (
        super()
        .get_queryset(request)
        .select_related("user")
        .annotate(
            item_count=Count("items"),
            total_quantity=Sum("items__quantity"),
        )
    )
```

검색도 조정합니다. `search_fields`에서 불필요한 JOIN 검색을 줄이고, exact 검색 가능한 필드는 `=` prefix를 고려합니다.

```python
search_fields = (
    "=order_number",
    "=id",
    "user__email",
)
```

**Migration 검증**

인덱스 추가 전에는 반드시 실제 SQL과 migration 결과를 확인합니다.

```bash
python manage.py makemigrations
python manage.py sqlmigrate orders 000X
python manage.py migrate --plan
```

PostgreSQL 운영 테이블이 크면 잠금도 고려해야 합니다. Django 기본 `AddIndex`는 상황에 따라 쓰기 잠금을 유발할 수 있으므로, 큰 테이블에서는 `CREATE INDEX CONCURRENTLY` 전략을 별도 migration으로 검토합니다.

검증할 것:

- 인덱스 이름이 30자 제한/DB 제한에 걸리지 않는지
- 복합 인덱스 컬럼 순서가 실제 WHERE + ORDER BY와 맞는지
- 이미 유사한 인덱스가 있어서 중복 생성하지 않는지
- partial index 조건이 실제 admin 필터 조건과 정확히 같은지
- migration이 운영 DB에서 긴 lock을 만들지 않는지

**EXPLAIN 기준**

Django ORM에서는 `.explain()`으로 먼저 확인합니다.

```python
qs = Order.objects.filter(status="paid").order_by("-created_at")
print(qs.explain(analyze=True, buffers=True))
```

PostgreSQL 기준으로는 이런 신호를 봅니다.

좋은 신호:

- `Index Scan`, `Index Only Scan`, `Bitmap Index Scan`
- `Sort`가 사라지거나 비용이 작음
- `Rows Removed by Filter`가 과도하지 않음
- `actual rows`와 예상 rows 차이가 크지 않음
- `shared hit/read buffers`가 줄어듦
- `Execution Time`이 개선됨

나쁜 신호:

- 대량 `Seq Scan`
- `ORDER BY` 때문에 큰 `Sort`
- `Nested Loop` 안쪽에서 반복적으로 큰 테이블 조회
- admin 한 페이지 조회인데 수천~수만 row를 읽음
- `COUNT(*)`가 전체 테이블 스캔에 가까움

비교는 인덱스 추가 전후로 같은 조건에서 합니다.

```python
Order.objects.filter(
    status="paid",
    created_at__gte="2026-01-01",
).order_by("-created_at").explain(analyze=True, buffers=True)
```

핵심은 단일 컬럼 인덱스를 많이 추가하는 게 아니라, admin의 실제 필터 조합과 정렬 순서에 맞는 소수의 복합 인덱스를 두는 것입니다. 보통 주문 admin에서는 `status + created_at`, `user/customer + created_at`, 기본 `created_at desc`, 그리고 검색 필드용 인덱스부터 검토하는 순서가 현실적입니다.