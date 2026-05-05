읽은 fixture 기준으로는 실제 “주문 목록 API” 구현이 없습니다. `/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders`에는 `models.py`, `views.py`, `api_drf.py`, `tests.py`만 있고, 목록 endpoint나 Django Ninja router는 없습니다. 그래서 특정 목록 함수의 라인 단위 버그로 확정할 수는 없고, 현재 모델/응답 구조에서 목록 API를 만들거나 이식할 때 생길 위험을 리뷰합니다.

**Findings**

1. **High: 주문 목록이 최신순/상태별 조회라면 pagination을 받칠 인덱스가 없습니다.**  
   [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:12)의 `status`, [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:17)의 `created_at`은 목록 조회 핵심 컬럼이 될 가능성이 큰데 `Meta.indexes`가 없습니다. `ORDER BY -created_at, -id`, `WHERE status = ? ORDER BY -created_at, -id` 같은 API라면 복합 인덱스가 필요합니다.

2. **High: 주문 목록에서 예약/상품 정보를 중첩 응답하면 N+1이 납니다.**  
   [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:41)의 `Reservation`은 `order`, `product` FK를 갖습니다. 목록 응답에서 주문별 reservation 또는 product를 접근하면 `order.reservation_set`과 `reservation.product` 접근이 주문 수/라인 수만큼 쿼리를 늘립니다. 목록용 queryset은 `select_related`와 `Prefetch`를 명시해야 합니다.

3. **Medium: 기존 API가 DRF `ModelSerializer(fields="__all__")` 기반이라 목록 응답 구조로 확장하면 과다 노출/과다 직렬화 위험이 큽니다.**  
   [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:8)는 DRF이고 [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:11)에서 전체 필드를 노출합니다. 프로젝트 방향이 Django Ninja라면 목록 API는 상세 모델 직렬화가 아니라 `OrderListItemSchema`처럼 얕은 응답을 별도로 둬야 합니다.

4. **Medium: N+1 회귀를 잡는 테스트가 없습니다.**  
   [tests.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/tests.py:6)는 cancel 모델 테스트만 있습니다. 주문 50개, reservation 여러 개를 만든 뒤 목록 API query count가 고정되는지 `assertNumQueries`/`django_assert_num_queries`로 보호해야 합니다.

권장 구조는 이렇습니다.

```python
# orders/selectors.py
from django.db.models import Prefetch
from shop.orders.models import Order, Reservation

def order_list_queryset():
    return (
        Order.objects
        .order_by("-created_at", "-id")
        .prefetch_related(
            Prefetch(
                "reservation_set",
                queryset=Reservation.objects.select_related("product").only(
                    "id", "order_id", "product_id", "quantity", "product__sku", "product__name"
                ),
                to_attr="prefetched_reservations",
            )
        )
    )
```

```python
# orders/api.py
from ninja import Router, Schema
from ninja.pagination import CursorPagination, paginate

router = Router(tags=["orders"])

class OrderListItemSchema(Schema):
    id: int
    customer_email: str
    status: str
    total_amount: str
    created_at: str

@router.get("", response=list[OrderListItemSchema])
@paginate(CursorPagination, ordering=("-created_at", "-id"), page_size=50)
def list_orders(request):
    return order_list_queryset()
```

모델 쪽은 대표 조회 패턴에 맞춰 최소 인덱스부터 추가하는 게 좋습니다.

```python
class Order(models.Model):
    ...

    class Meta:
        indexes = [
            models.Index(fields=["-created_at", "-id"], name="order_created_cursor_idx"),
            models.Index(fields=["status", "-created_at", "-id"], name="order_status_cursor_idx"),
        ]
```

핵심은 `select_related/prefetch_related`는 직렬화 중 추가 조회를 줄이는 문제이고, cursor/keyset pagination과 복합 인덱스는 큰 페이지에서 행을 찾고 정렬하는 문제입니다. 둘을 같은 최적화로 보면 원인을 놓치기 쉽습니다.