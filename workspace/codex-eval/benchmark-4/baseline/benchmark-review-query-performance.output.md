**[주요 내용]**

작업 디렉터리(`/private/tmp/dddjango-codex-eval`)에 Django 코드가 없어 실제 파일/라인 단위 리뷰는 못 했습니다. 대신 주문 목록 API에서 흔히 터지는 N+1과 pagination 병목을 Django ORM + Django Ninja 응답 구조 기준으로 보면, 우선순위는 아래입니다.

1. **[QuerySet 최적화] -- 응답 Schema가 접근하는 관계를 QuerySet에서 미리 로딩해야 합니다.**

주문 목록에서 보통 `order.customer`, `order.items`, `item.product`, `order.payment`, `order.shipment` 같은 필드를 응답에 포함합니다. 이때 Ninja `Schema`/resolver가 ORM 객체 속성을 읽는 순간 lazy loading이 발생하면 `1 + N + N*M` 쿼리로 커집니다.

권장 형태:

```python
from django.db.models import Prefetch

orders = (
    Order.objects
    .select_related("customer", "payment", "shipment")
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
    .only(
        "id",
        "number",
        "status",
        "created_at",
        "total_amount",
        "customer_id",
        "customer__id",
        "customer__name",
    )
)
```

FK/O2O는 `select_related`, 역방향 FK/M2M는 `prefetch_related`가 맞습니다. `Schema.resolve_*` 안에서 `obj.items.all()`, `obj.customer.name`, `obj.payment.status`를 처음 접근하게 두면 N+1 가능성이 큽니다.

2. **[Pagination] -- 대량 주문 목록에 offset/page-number pagination만 쓰면 뒤 페이지가 느려집니다.**

`?page=10000` 또는 `?offset=500000` 형태는 DB가 앞의 행을 계속 스캔/건너뛰어야 해서 주문 테이블이 커질수록 느려집니다. 주문 목록은 보통 최신순 조회가 많으므로 cursor/keyset 기반이 더 적합합니다.

권장 정렬 기준은 안정적인 복합 키입니다.

```python
.order_by("-created_at", "-id")
```

그리고 커서는 `(created_at, id)` 조합으로 잡아야 합니다. `created_at` 단독은 같은 시각 주문이 있을 때 중복/누락 위험이 있습니다.

필요 인덱스 예:

```python
class Meta:
    indexes = [
        models.Index(fields=["-created_at", "-id"], name="order_created_id_idx"),
        models.Index(fields=["customer", "-created_at", "-id"], name="order_customer_created_idx"),
        models.Index(fields=["status", "-created_at", "-id"], name="order_status_created_idx"),
    ]
```

복합 인덱스는 실제 필터 워크로드에 맞춰야 합니다. 예를 들어 `customer_id = ? AND status = ? AND created_at < ? ORDER BY created_at DESC, id DESC`가 핵심이면 `(customer, status, -created_at, -id)` 순서를 검토합니다. 등호 조건 컬럼을 범위/정렬 컬럼보다 앞에 둡니다.

3. **[Django Ninja 응답 구조] -- ORM 객체를 그대로 깊은 중첩 Schema에 넘기면 직렬화 단계에서 쿼리가 숨어듭니다.**

Ninja 응답 Schema는 편하지만, nested Schema와 resolver가 ORM lazy loading을 유발할 수 있습니다. 목록 API에서는 상세 API와 같은 깊이의 응답을 피하고, 목록 전용 `OrderListItemOut`을 두는 편이 낫습니다.

```python
class OrderListItemOut(Schema):
    id: int
    number: str
    status: str
    created_at: datetime
    total_amount: Decimal
    customer_name: str
    item_count: int
```

`item_count`, `latest_payment_status` 같은 값은 Python resolver에서 관계를 훑기보다 `annotate()`로 붙이는 쪽이 안전합니다.

```python
from django.db.models import Count

orders = orders.annotate(item_count=Count("items"))
```

4. **[Response Envelope] -- `@paginate`와 커스텀 `items/meta` envelope를 섞지 마세요.**

Django Ninja 내장 `@paginate`를 쓰면 해당 paginator의 응답 형식을 따르는 게 맞습니다. 팀 표준이 `{"items": [...], "meta": {...}}`라면 `@paginate`에 얹기보다 커스텀 `PaginationBase` 또는 명시적 selector에서 슬라이싱/커서 처리를 일관되게 구현하세요.

예상 응답:

```json
{
  "items": [],
  "meta": {
    "next_cursor": "opaque-token",
    "has_more": true,
    "limit": 50
  }
}
```

5. **[검증] -- N+1은 테스트로 고정해야 합니다.**

리뷰에서 가장 중요한 회귀 방지는 쿼리 수 테스트입니다. 주문 1개가 아니라 주문 여러 개와 각 주문의 여러 item을 만든 뒤 쿼리 수가 주문 수에 비례해 증가하지 않는지 봐야 합니다.

```python
def test_order_list_query_count(client, django_assert_num_queries):
    create_orders(count=20, items_per_order=3)

    with django_assert_num_queries(4):
        response = client.get("/api/v1/orders?limit=20")

    assert response.status_code == 200
```

정확한 쿼리 수는 인증/세션/권한 로직에 따라 달라질 수 있지만, 핵심은 `orders` 수를 늘려도 쿼리 수가 선형 증가하지 않아야 한다는 점입니다.

정리하면, 주문 목록 API는 `목록 전용 Schema`, `select_related/prefetch_related/annotate`, `cursor 또는 keyset pagination`, `워크로드 기반 복합 인덱스`, `assertNumQueries`가 같이 들어가야 합니다. 상세 응답과 목록 응답을 같은 Schema로 재사용하는 구조라면 그 자체가 N+1과 과한 payload의 출발점일 가능성이 큽니다.

---
> **관련 스킬 참조:**
> - Django ORM QuerySet 최적화 → **implementation-django** 스킬
> - Django Ninja Schema/Router/페이지네이션 → **implementation-django-ninja** 스킬
> - 인덱스와 쿼리 실행 계획 → **architecture-db** 스킬