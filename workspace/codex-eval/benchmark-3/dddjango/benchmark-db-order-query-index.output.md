**[주요 내용]**

관리자 주문 목록은 보통 `WHERE 조건 + ORDER BY + pagination + related 객체 표시`가 섞여 느려집니다. 먼저 “목록에서 실제로 자주 쓰는 필터/정렬 조합”을 기준으로 복합 인덱스를 검토해야 합니다.

대표 패턴이 아래라면:

```python
Order.objects.filter(
    status=status,
    created_at__gte=start,
    created_at__lt=end,
).select_related(
    "customer",
).order_by(
    "-created_at",
    "-id",
)
```

우선 검토할 인덱스는 다음입니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="order_status_created_id_idx",
            ),
        ]
```

이유는 `status = ...` 같은 동등 조건을 앞에 두고, 그 뒤에 범위/정렬 컬럼인 `created_at`, tie-breaker인 `id`를 둬서 필터와 정렬을 한 인덱스로 처리할 가능성을 높이기 위해서입니다.

조회 조건이 `payment_status`, `seller_id`, `deleted_at IS NULL` 중심이면 인덱스도 달라집니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["seller", "payment_status", "-created_at", "-id"],
                name="order_seller_pay_created_idx",
            ),
            models.Index(
                fields=["status", "-created_at", "-id"],
                condition=models.Q(deleted_at__isnull=True),
                name="order_active_status_created_idx",
            ),
        ]
```

단, `condition=`은 PostgreSQL partial index에 특히 유효합니다. MySQL 등에서는 DB별 지원 여부를 확인해야 합니다.

인덱스를 무조건 많이 추가하면 주문 생성/상태 변경/결제 상태 변경 때마다 쓰기 비용이 증가합니다. 보통은 다음처럼 “관리자 목록의 주요 검색 경로” 1~3개만 먼저 잡는 편이 낫습니다.

검토 우선순위:

1. 기본 정렬만 자주 사용: `("-created_at", "-id")`
2. 상태 필터 + 최신순: `("status", "-created_at", "-id")`
3. 판매자/상점 필터 + 상태 + 최신순: `("seller", "status", "-created_at", "-id")`
4. soft delete가 대부분 붙음: partial index `WHERE deleted_at IS NULL`
5. 키워드 검색 `icontains`는 일반 B-tree로 해결되지 않음. PostgreSQL이면 trigram/Gin index를 별도 검토

`select_related()`와 `prefetch_related()`는 인덱스와 다른 문제를 해결합니다.

```python
qs = (
    Order.objects.filter(status=status)
    .select_related("customer", "payment")
    .prefetch_related(
        Prefetch(
            "items",
            queryset=OrderItem.objects.select_related("product"),
        )
    )
    .order_by("-created_at", "-id")
)
```

`select_related()`는 FK/O2O를 JOIN으로 가져와 주문 행마다 고객/결제 객체를 다시 조회하는 N+1을 줄입니다. 하지만 `WHERE`나 `ORDER BY` 자체를 빠르게 만들지는 않습니다.

`prefetch_related()`는 M2M/역방향 FK를 별도 `IN (...)` 쿼리로 가져옵니다. 관리자 목록 한 페이지에 주문 50개를 보여주고 각 주문의 상품 목록을 표시한다면 효과가 큽니다. 반대로 목록에서 related 데이터를 표시하지 않으면 불필요한 추가 쿼리와 메모리 비용입니다.

pagination 비용도 따로 봐야 합니다. Django admin의 일반 페이지네이션은 보통 `COUNT(*)`와 `LIMIT/OFFSET` 비용이 있습니다. 깊은 페이지로 갈수록 `OFFSET 100000`처럼 앞 행을 건너뛰는 비용이 커집니다. 관리자에서 전체 개수 표시가 꼭 필요하지 않다면 다음도 검토합니다.

```python
class OrderAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_select_related = ("customer", "payment")
    ordering = ("-created_at", "-id")
```

검증은 추측이 아니라 실제 실행계획으로 합니다.

```python
qs = Order.objects.filter(
    status="paid",
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")[:50]

print(qs.explain(analyze=True, buffers=True))
```

확인 기준:

- 대형 주문 테이블에서 `Seq Scan`이 반복되는가
- `Sort`가 큰 비용을 쓰는가
- `actual rows`와 예상 `rows` 차이가 큰가
- `Execution Time`이 인덱스 추가 전후로 줄었는가
- `Buffers: shared read`가 줄었는가
- admin 목록 한 페이지의 쿼리 수가 `assertNumQueries`로 고정 가능한가
- 새 인덱스가 주문 생성/상태 변경 처리량을 떨어뜨리지 않는가

결론적으로 먼저 자주 쓰는 관리자 필터 조합을 로그나 `pg_stat_statements`로 확인하고, 그 조합에 맞춰 `동등 조건 컬럼 -> 정렬/범위 컬럼 -> id` 순서의 복합 인덱스를 1~3개만 추가하는 방식이 좋습니다. Related 객체 표시 문제는 `select_related/prefetch_related`, 깊은 페이지 문제는 pagination/count 비용으로 별도 측정해야 합니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리 최적화 → **implementation-django** 스킬
> - 복합 인덱스와 실행계획 분석 → **architecture-db** 스킬