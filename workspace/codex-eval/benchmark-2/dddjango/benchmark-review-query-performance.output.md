**주요 내용**

`/private/tmp/dddjango-codex-eval` 경로가 비어 있고 `config.toml`도 없어 특정 파일/라인 기반 리뷰는 못 했습니다. 코드 확인 없이도 주문 목록 API에서 우선 봐야 할 위험은 아래 순서입니다.

**Findings**

1. **[Django ORM: N+1 위험] -- 목록 응답 schema가 `order.customer`, `order.payment`, `order.lines`, `line.product` 같은 관계를 직렬화 중에 접근하면 쿼리가 주문 수에 비례해 증가합니다.**  
   `select_related()`와 `prefetch_related()`를 관계 유형별로 분리해야 합니다.  
   `customer`, `payment`처럼 FK/O2O 단일 객체는 `select_related()`.  
   `lines`, `discounts`, `shipments`처럼 M2M 또는 역방향 FK 컬렉션은 `prefetch_related()` 또는 `Prefetch()`입니다.

2. **[API Pagination: offset 기반 페이지네이션 부적합] -- 주문 테이블이 커질수록 `LIMIT/OFFSET`은 뒤 페이지에서 느려지고, 삽입/삭제가 많은 주문 데이터에서는 누락/중복도 생길 수 있습니다.**  
   관리자 화면처럼 랜덤 페이지 이동이 중요하면 offset을 유지할 수 있지만, 고객/운영 주문 목록의 기본 API는 `created_at + id` 기반 cursor/keyset 전략이 더 맞습니다. 정렬 필드는 인덱싱되고 안정적이어야 합니다.

3. **[Django Ninja Schema: 과도한 중첩] -- `OrderSchema` 안에 `CustomerSchema`, `OrderLineSchema`, `ProductSchema`, `PaymentSchema`를 깊게 넣으면 응답 크기와 ORM 접근 경로가 동시에 커집니다.**  
   목록 API는 상세 API가 아닙니다. 목록 schema는 “스캔에 필요한 요약 필드”만 노출하고, 라인 상세는 `/orders/{id}`에서 별도 제공하는 편이 낫습니다.

권장 구조는 아래처럼 읽기 전용 selector와 얕은 응답 schema를 분리하는 방식입니다.

```python
# orders/schemas.py
from datetime import datetime
from decimal import Decimal
from ninja import Schema

class OrderListItemSchema(Schema):
    id: int
    number: str
    status: str
    placed_at: datetime
    customer_id: int
    customer_name: str
    total_amount: Decimal
    item_count: int
```

```python
# orders/selectors.py
from django.db.models import Count, Prefetch

def order_list_queryset(user):
    return (
        Order.objects
        .filter(customer__user=user)
        .select_related("customer")
        .annotate(item_count=Count("lines"))
        .order_by("-placed_at", "-id")
    )
```

라인 미리보기가 반드시 필요할 때만 컬렉션을 prefetch합니다.

```python
def order_list_queryset(user):
    return (
        Order.objects
        .filter(customer__user=user)
        .select_related("customer")
        .prefetch_related(
            Prefetch(
                "lines",
                queryset=OrderLine.objects.select_related("product")
                .only("id", "order_id", "quantity", "product__name"),
                to_attr="prefetched_lines",
            )
        )
        .order_by("-placed_at", "-id")
    )
```

```python
# orders/api.py
from ninja import Router
from ninja.pagination import CursorPagination, paginate

router = Router()

@router.get("", response=list[OrderListItemSchema])
@paginate(CursorPagination, ordering=("-placed_at", "-id"), page_size=50, max_page_size=100)
def list_orders(request):
    return order_list_queryset(request.user)
```

DB 인덱스는 실제 필터와 정렬에 맞춥니다.

```python
class Meta:
    indexes = [
        models.Index(fields=["customer", "-placed_at", "-id"], name="order_customer_cursor_idx"),
        models.Index(fields=["status", "-placed_at", "-id"], name="order_status_cursor_idx"),
    ]
```

**검증 방법**

```python
def test_order_list_query_count(client, django_assert_num_queries, user):
    create_orders_with_lines(user=user, count=50, lines_per_order=3)

    # lines를 응답하지 않으면 orders + count/join 수준으로 고정되어야 함.
    with django_assert_num_queries(2):
        response = client.get("/api/orders")

    assert response.status_code == 200
```

추가로 PostgreSQL에서 실제 API 쿼리에 대해 `EXPLAIN ANALYZE`를 확인하세요. 기대값은 cursor 정렬 인덱스를 타는 `Index Scan` 또는 상황에 따라 `Bitmap Index Scan`이며, 깊은 페이지에서도 실행 시간이 크게 증가하지 않아야 합니다.

---
> **관련 스킬 참조:**
> - ORM 최적화와 `assertNumQueries` 회귀 테스트 → **implementation-django** 스킬
> - Django Ninja `Schema`/`Router`/pagination 구조 → **implementation-django-ninja** 스킬
> - cursor/keyset pagination과 인덱스 설계 → **architecture-api**, **architecture-db** 스킬