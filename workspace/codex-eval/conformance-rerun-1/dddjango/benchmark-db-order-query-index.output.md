**[주요 내용]**

관리자 주문 목록은 먼저 실제 조회 패턴을 나눠서 봐야 합니다. 인덱스는 “컬럼 중요도”가 아니라 `WHERE + ORDER BY + pagination` 조합에 맞춥니다.

**1. 대표 조회 패턴별 composite index**

가장 흔한 관리자 목록:

```python
Order.objects.filter(
    status="PAID",
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")
```

권장 인덱스:

```python
models.Index(
    fields=["status", "-created_at", "-id"],
    name="order_status_created_id_idx",
)
```

이유: `status`는 동등 조건, `created_at`은 범위와 정렬, `id`는 같은 시각 주문의 안정적 pagination용 tie-breaker입니다.

판매자/입점사/스토어 단위 관리자라면:

```python
models.Index(
    fields=["seller_id", "status", "-created_at", "-id"],
    name="order_seller_status_created_id_idx",
)
```

고객별 주문 검색이 잦다면:

```python
models.Index(
    fields=["customer_id", "-created_at", "-id"],
    name="order_customer_created_id_idx",
)
```

삭제 제외 조건이 항상 붙는다면 PostgreSQL 부분 인덱스를 검토합니다:

```python
models.Index(
    fields=["status", "-created_at", "-id"],
    name="order_active_status_created_idx",
    condition=models.Q(deleted_at__isnull=True),
)
```

주의할 점은 `icontains` 검색입니다.

```python
Order.objects.filter(buyer_name__icontains=keyword)
```

일반 B-tree composite index로는 거의 해결되지 않습니다. 주문번호 exact/prefix 검색은 별도 인덱스를 두고, 이름/전화번호/주소 부분 검색은 PostgreSQL `pg_trgm` GIN 인덱스나 검색 전용 테이블을 검토해야 합니다.

**2. Django ORM 쿼리 개선**

FK/O2O는 `select_related()`를 사용합니다.

```python
qs = (
    Order.objects
    .select_related("customer", "seller", "payment")
    .filter(status=status, created_at__gte=start, created_at__lt=end)
    .order_by("-created_at", "-id")
)
```

`select_related()`는 N+1을 줄이는 JOIN 최적화입니다. 목록의 필터/정렬 비용을 직접 줄이지는 않습니다. JOIN 대상 컬럼이 많으면 row가 넓어져 오히려 느려질 수 있으므로 목록에 실제 표시하는 FK만 붙입니다.

M2M/역방향 FK는 `prefetch_related()`입니다.

```python
qs = qs.prefetch_related(
    models.Prefetch(
        "items",
        queryset=OrderItem.objects.select_related("product").only(
            "id", "order_id", "product_id", "quantity"
        ),
    )
)
```

`prefetch_related()`는 별도 쿼리로 배치 로딩합니다. 페이지당 50개 주문의 품목을 보여줄 때는 효과가 있지만, 깊은 pagination이나 대량 export 쿼리에 붙이면 메모리와 두 번째 쿼리 비용이 커집니다. 관리자 목록에서는 “현재 페이지에 표시하는 관계”에만 제한합니다.

**3. Pagination 비용 분리**

`LIMIT 50 OFFSET 100000`은 인덱스를 써도 앞의 100000건을 건너뛰는 비용이 큽니다. 깊은 페이지 접근이 느리면 keyset pagination을 검토합니다.

```python
qs = Order.objects.filter(
    created_at__lt=last_created_at,
).order_by("-created_at", "-id")[:50]
```

동일 timestamp까지 안정적으로 처리하려면 조건을 분리합니다.

```python
qs = Order.objects.filter(
    models.Q(created_at__lt=last_created_at)
    | models.Q(created_at=last_created_at, id__lt=last_id)
).order_by("-created_at", "-id")[:50]
```

Django admin 자체의 `COUNT(*)`도 느릴 수 있습니다. 정확한 전체 건수가 필요 없으면 `ModelAdmin.show_full_result_count = False`를 검토합니다.

**4. Migration 검증**

대형 테이블 PostgreSQL에서는 일반 `AddIndex`가 쓰기 락 리스크를 만들 수 있습니다. 운영 테이블이면 concurrent index를 우선 검토합니다.

```python
from django.contrib.postgres.operations import AddIndexConcurrently

class Migration(migrations.Migration):
    atomic = False

    operations = [
        AddIndexConcurrently(
            model_name="order",
            index=models.Index(
                fields=["status", "-created_at", "-id"],
                name="order_status_created_id_idx",
            ),
        ),
    ]
```

검증 순서:

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 00xx
python manage.py migrate --plan
python manage.py migrate
python manage.py test
```

`sqlmigrate`에서 인덱스 컬럼 순서, `DESC`, 부분 인덱스 `WHERE` 조건, concurrent 생성 여부를 확인합니다.

**5. EXPLAIN 기준**

운영과 유사한 데이터량에서 확인합니다.

```python
print(qs.explain(analyze=True, buffers=True, verbose=True))
```

통과 기준은 다음 정도로 잡습니다.

- `Seq Scan`이 대형 `orders` 테이블에서 사라지고 `Index Scan`, `Bitmap Index Scan`, 가능하면 `Index Only Scan`이 사용된다.
- `Sort` 노드가 없어지거나 정렬 대상 rows가 페이지 크기에 가깝다.
- `actual rows`와 planner `rows` 추정치 차이가 크지 않다. 크면 `ANALYZE` 또는 통계 설정을 본다.
- `Rows Removed by Filter`가 과도하지 않다. 인덱스 선두 컬럼이 조회 조건과 안 맞는 신호다.
- `shared read blocks`가 줄고, 반복 실행 시 `shared hit blocks` 중심으로 바뀐다.
- `LIMIT 50` 쿼리의 실제 시간이 페이지 깊이에 따라 선형 증가하지 않는다. 증가하면 OFFSET 문제가 남아 있다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리/마이그레이션 최적화 → **implementation-django** 스킬
> - 복합 인덱스/EXPLAIN ANALYZE 기준 → **architecture-db** 스킬