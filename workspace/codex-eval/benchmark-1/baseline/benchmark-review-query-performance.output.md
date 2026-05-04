**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`에는 리뷰할 Django 코드가 없습니다. 그래서 파일/라인 단위 지적은 못 하고, 주문 목록 API에서 N+1과 느린 pagination을 만드는 전형적인 구조 기준으로 리뷰합니다.

**Findings**

[Convention: QuerySet 최적화] -- 주문 목록 응답 Schema가 `customer`, `items`, `product`, `payment`, `shipping_address` 같은 관계 필드를 직접 노출하거나 resolver에서 접근한다면 N+1 가능성이 큽니다. FK/O2O는 `select_related()`, M2M/역방향 FK는 `prefetch_related()` 또는 `Prefetch()`로 목록 조회 selector에서 고정해야 합니다.

```python
orders = (
    Order.objects
    .select_related("customer", "payment", "shipping_address")
    .prefetch_related(
        Prefetch(
            "items",
            queryset=OrderItem.objects.select_related("product"),
        )
    )
    .order_by("-created_at", "-id")
)
```

[Convention: Django Ninja Schema] -- `ModelSchema`에서 nested relation이나 `depth`, `fields = "__all__"`을 쓰면 응답 직렬화 단계에서 ORM lazy loading이 터질 수 있습니다. 주문 목록용 Schema는 상세 Schema와 분리하고, 목록에 필요한 필드만 명시하는 편이 안전합니다. resolver가 `obj.items.count()`, `obj.items.all()`, `obj.customer.name` 등을 호출한다면 그 값은 `annotate()`나 prefetch된 `to_attr` 기반으로 바꿔야 합니다.

[Convention: Pagination] -- `LimitOffsetPagination` 또는 `PageNumberPagination`은 큰 offset에서 DB가 앞 행을 계속 스캔해야 해서 느려질 수 있습니다. 주문 목록처럼 최신순으로 계속 조회되는 API는 `CursorPagination` 또는 keyset pagination이 더 적합합니다. 정렬은 반드시 유일하고 안정적인 조합이어야 하므로 `("-created_at", "-id")`처럼 tie-breaker를 둬야 합니다.

[원칙: 인덱스 설계] -- 주문 목록 필터/정렬이 보통 `user_id`, `status`, `created_at`, `id` 조합이라면 쿼리 워크로드에 맞는 복합 인덱스가 필요합니다. 예를 들어 “내 주문 최신순”이면 `(user_id, -created_at, -id)`, “상태별 최신순”이면 `(status, -created_at, -id)` 후보를 `EXPLAIN ANALYZE`로 검증해야 합니다.

[Convention: 응답 구조] -- 커스텀 paginator가 `total = queryset.count()`를 매 요청마다 반환하면 대형 주문 테이블에서 count가 병목이 됩니다. 무조건 total이 필요한 화면이 아니라면 cursor 응답의 `next/previous/results` 구조로 바꾸거나, total은 별도 endpoint/cache/근사값으로 분리하는 편이 낫습니다.

[Convention: 테스트] -- N+1 회귀 방지 테스트가 필요합니다. 주문 1개일 때와 50개일 때 쿼리 수가 선형 증가하지 않는지 `assertNumQueries`로 고정하세요.

```python
with self.assertNumQueries(4):
    response = client.get("/api/orders")
```

**권장 구조**

읽기 전용 조회는 endpoint 안에 두지 말고 `api/selectors.py` 같은 selector로 분리하는 것이 좋습니다.

```python
def order_list_queryset(user):
    return (
        Order.objects
        .filter(user=user)
        .select_related("customer", "payment")
        .prefetch_related(
            Prefetch("items", queryset=OrderItem.objects.select_related("product"))
        )
        .order_by("-created_at", "-id")
    )
```

Django Ninja endpoint는 QuerySet을 그대로 반환하고 `@paginate(CursorPagination, ordering=("-created_at", "-id"))`를 적용하는 방향이 가장 단순합니다.

추가 확인 항목: `Order.Meta.ordering`, 주요 filter/order 컬럼의 `Meta.indexes`, `Order.__str__`, `datetime` 같은 빌트인과 충돌하는 필드명 사용 여부도 모델 리뷰에서 확인해야 합니다.

---
> **관련 스킬 참조:**
> - Django ORM N+1/QuerySet 최적화 → **implementation-django** 스킬
> - Django Ninja Schema/페이지네이션 구조 → **implementation-django-ninja** 스킬
> - 주문 목록 인덱스/EXPLAIN ANALYZE 검증 → **architecture-db** 스킬