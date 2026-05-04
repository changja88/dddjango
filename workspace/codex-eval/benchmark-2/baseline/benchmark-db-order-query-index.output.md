`/private/tmp/dddjango-codex-eval`에서 `config.toml`이나 Django 코드가 확인되지 않아, 일반적인 “관리자 주문 목록” 기준으로 제안합니다.

관리자 주문 목록이 느릴 때는 보통 `ORDER BY`, 필터, 검색, FK 표시, 집계 때문에 병목이 납니다.

**검토할 인덱스**

```python
class Order(models.Model):
    status = models.CharField(...)
    created_at = models.DateTimeField(db_index=True)
    customer = models.ForeignKey(Customer, ...)
    payment_status = models.CharField(...)
    total_price = models.DecimalField(...)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["payment_status", "-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
        ]
```

우선순위는 다음입니다.

1. 관리자 기본 정렬이 최신순이면 `created_at` 또는 `-created_at`
2. 상태 필터가 많으면 `status, -created_at`
3. 결제 상태 필터가 많으면 `payment_status, -created_at`
4. 고객별 주문 조회가 많으면 `customer, -created_at`
5. 삭제/숨김 플래그가 있다면 `is_deleted, -created_at` 또는 partial index 검토

PostgreSQL을 쓴다면 상태별 활성 주문만 자주 보면 partial index도 좋습니다.

```python
from django.db.models import Q

models.Index(
    fields=["-created_at"],
    name="order_active_created_idx",
    condition=Q(is_deleted=False),
)
```

**Django Admin 쿼리 개선**

`list_display`에서 FK 필드나 related object를 보여주면 N+1이 쉽게 납니다. `ModelAdmin.get_queryset()`에서 명시적으로 줄이는 게 좋습니다.

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "payment_status", "created_at"]
    list_filter = ["status", "payment_status", "created_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("customer", "shipping_address", "payment")
```

M2M이나 reverse relation을 표시한다면 `prefetch_related()`를 사용합니다.

```python
return qs.select_related("customer").prefetch_related("items")
```

**검색 개선**

`search_fields = ["customer__name", "customer__email", "id"]` 같은 설정은 테이블이 커지면 느릴 수 있습니다.

검토할 것:

```python
search_fields = ["=id", "^customer__email"]
```

`=id`는 정확히 일치, `^email`은 prefix 검색이라 일반 `icontains`보다 인덱스를 타기 쉽습니다. PostgreSQL에서 부분 문자열 검색이 꼭 필요하면 `pg_trgm` + GIN index를 검토합니다.

**피해야 할 패턴**

```python
def customer_email(self, obj):
    return obj.customer.email
```

이런 코드는 `select_related("customer")` 없으면 주문 수만큼 추가 쿼리가 발생합니다.

또한 `list_display`에서 주문 합계, 아이템 수 등을 매번 계산하면 느립니다. 필요하면 `annotate()`로 한 번에 가져오거나, 자주 쓰는 값은 주문 테이블에 denormalized field로 저장하는 것도 검토합니다.

```python
from django.db.models import Count

def get_queryset(self, request):
    return (
        super()
        .get_queryset(request)
        .select_related("customer")
        .annotate(item_count=Count("items"))
    )
```

**확인 순서**

1. Django Debug Toolbar 또는 DB 로그로 실제 SQL 확인
2. 느린 SQL에 `EXPLAIN ANALYZE`
3. `WHERE`, `ORDER BY`, `JOIN`에 맞춰 복합 인덱스 추가
4. Admin의 `select_related`, `prefetch_related`, `search_fields`, `ordering` 조정
5. 추가 후 실제 운영 데이터 크기에서 다시 `EXPLAIN ANALYZE`

핵심은 단일 인덱스를 많이 추가하기보다, 관리자 목록의 실제 패턴인 “상태 필터 + 최신순 정렬”에 맞춘 복합 인덱스를 우선 검토하는 것입니다.