코드가 없는 상태라 일반적인 Django 관리자 주문 목록 기준으로 보면, 우선 아래를 검토하는 게 좋습니다.

**인덱스 후보**

1. `created_at` / `ordered_at`
   관리자 목록이 최신 주문순이면 거의 항상 필요합니다.

```python
models.Index(fields=["-created_at"], name="order_created_desc_idx")
```

2. 상태 필터 + 최신순

```python
models.Index(fields=["status", "-created_at"], name="order_status_created_idx")
```

3. 결제 상태 / 배송 상태 필터가 있다면

```python
models.Index(fields=["payment_status", "-created_at"], name="order_pay_created_idx")
models.Index(fields=["shipping_status", "-created_at"], name="order_ship_created_idx")
```

4. 고객별 주문 조회가 많다면

```python
models.Index(fields=["customer", "-created_at"], name="order_customer_created_idx")
```

5. 관리자 검색 필드
   `order_number`, `merchant_uid`, `tracking_number`처럼 정확 검색이 많은 값은 `db_index=True` 또는 `unique=True`.

```python
order_number = models.CharField(max_length=64, unique=True)
```

   단, `icontains` 검색은 일반 B-tree 인덱스를 잘 못 씁니다. PostgreSQL이면 `pg_trgm` + `GinIndex` 검토가 낫습니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity
```

**ORM 쿼리 개선**

관리자 `ModelAdmin`에서 `get_queryset()`을 명시적으로 최적화하세요.

```python
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "order_number", "customer", "status", "total_price", "created_at"]
    list_select_related = ["customer", "payment"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .select_related("customer", "payment", "shipping_address")
            .only(
                "id",
                "order_number",
                "status",
                "total_price",
                "created_at",
                "customer__id",
                "customer__email",
                "payment__id",
                "payment__status",
            )
        )
```

`list_display`에서 역참조나 M2M, 주문 상품 개수, 합계 등을 매 row마다 계산하면 N+1이 납니다. 이런 값은 `annotate()`로 가져오는 게 좋습니다.

```python
from django.db.models import Count, Sum

def get_queryset(self, request):
    return (
        super().get_queryset(request)
        .select_related("customer")
        .annotate(
            item_count=Count("items"),
            item_total=Sum("items__price"),
        )
    )
```

**관리자 설정에서 주의할 점**

- `search_fields = ["customer__email"]`처럼 조인 검색이 많으면 느려질 수 있습니다.
- 가능하면 `=order_number`, `=merchant_uid` 같은 exact search를 사용하세요.

```python
search_fields = ["=order_number", "=merchant_uid", "customer__email"]
```

- `list_filter`에 쓰는 필드는 복합 인덱스 후보입니다.
- `ordering = ["-created_at"]`이면 `created_at` 단독 또는 필터와 묶은 복합 인덱스를 맞추세요.
- 큰 테이블에서는 관리자 전체 count도 느릴 수 있어 `show_full_result_count = False`를 고려하세요.

```python
show_full_result_count = False
```

가장 먼저 볼 조합은 보통 이겁니다:

```python
models.Index(fields=["status", "-created_at"])
models.Index(fields=["payment_status", "-created_at"])
models.Index(fields=["customer", "-created_at"])
```

그리고 실제로는 Django Debug Toolbar나 `QuerySet.explain()`으로 관리자 목록 쿼리의 실행 계획을 확인한 뒤, `WHERE`, `ORDER BY`, `JOIN`에 맞춰 인덱스를 확정하는 게 맞습니다.