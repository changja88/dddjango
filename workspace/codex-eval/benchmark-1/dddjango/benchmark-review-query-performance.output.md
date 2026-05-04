**주요 내용**

워크스페이스 `/private/tmp/dddjango-codex-eval`가 비어 있어 실제 `orders` 코드 라인 단위 리뷰와 테스트 실행은 불가능했습니다. 아래는 주문 목록 API에서 흔히 발생하는 N+1과 느린 pagination을 Django ORM + Django Ninja 구조 기준으로 대조해야 할 핵심 findings입니다. 이 프로젝트 정책상 API는 DRF가 아니라 Django Ninja `Schema`/`Router` 기준으로 봅니다.

**Findings**

[Convention: QuerySet에서 관계 로딩을 명시해야 함] -- 주문 목록 응답에서 `order.customer`, `order.payment`, `order.shipping_address` 같은 FK/O2O를 직렬화한다면 `select_related()`가 필요합니다. `order.items`, `item.product`, `item.options`처럼 역참조 FK/M2M를 포함하면 `prefetch_related()` 또는 `Prefetch()`가 필요합니다. 특히 Ninja `Schema`의 nested field나 resolver가 각 주문별로 `.items.all()`을 호출하면 페이지 크기 50 기준으로 `1 + N + items N` 형태로 터집니다.

```python
from django.db.models import Prefetch

def order_list_queryset(*, user):
    return (
        Order.objects
        .filter(user=user)
        .select_related("customer", "payment", "shipping_address")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=(
                    OrderItem.objects
                    .select_related("product")
                    .only(
                        "id",
                        "order_id",
                        "product_id",
                        "quantity",
                        "unit_price",
                        "product__id",
                        "product__name",
                    )
                ),
                to_attr="prefetched_items",
            )
        )
        .order_by("-created_at", "-id")
    )
```

[Convention: 목록 응답 Schema는 상세 응답보다 얕아야 함] -- 주문 목록 API가 상세 화면 수준의 nested item/product 전체를 반환하면 ORM 최적화를 해도 응답 직렬화 비용과 payload가 커집니다. 목록은 `OrderListItemSchema`처럼 요약 필드, 금액, 상태, 주문일, 고객 요약 정도로 제한하고, 품목 전체는 상세 API로 분리하는 편이 낫습니다. `ModelSchema fields="__all__"`도 목록 API에서는 과다 노출과 불필요한 lazy loading 위험이 있습니다.

```python
from datetime import datetime
from decimal import Decimal
from ninja import Schema

class CustomerSummarySchema(Schema):
    id: int
    name: str

class OrderListItemSchema(Schema):
    id: int
    number: str
    status: str
    total_amount: Decimal
    customer: CustomerSummarySchema
    created_at: datetime
```

[Convention: pagination 전에 list 변환 금지] -- Ninja `@paginate`를 쓰더라도 endpoint나 selector에서 `list(queryset)`, list comprehension, Python 정렬, Python 필터링을 먼저 하면 DB pagination이 아니라 메모리 pagination이 됩니다. 목록 endpoint는 최종 QuerySet을 반환하고, slicing은 paginator가 하도록 유지해야 합니다.

```python
from typing import List
from ninja import Router
from ninja.pagination import CursorPagination, paginate

router = Router(tags=["orders"])

@router.get("/", response=List[OrderListItemSchema])
@paginate(CursorPagination, ordering=("-created_at", "-id"), page_size=50)
def list_orders(request):
    return order_list_queryset(user=request.user)
```

[원칙: 대용량 주문 목록에는 offset pagination이 병목이 됨] -- `?limit=50&offset=500000` 구조는 뒤 페이지로 갈수록 DB가 많은 행을 건너뛰어야 해서 느려집니다. 주문 목록은 보통 최신순 피드 성격이므로 cursor/keyset pagination이 더 적합합니다. 정렬 키는 변하지 않고 인덱스를 탈 수 있어야 하며, `created_at`만 쓰면 동률 문제가 있으니 `("-created_at", "-id")`처럼 유니크 tie-breaker를 같이 둬야 합니다.

[원칙: 인덱스는 조회 워크로드 기준으로 설계해야 함] -- 주문 목록이 보통 `user_id`, `status`, 기간, 최신순 정렬을 같이 사용한다면 단일 인덱스 여러 개보다 실제 WHERE/ORDER BY 조합에 맞춘 복합 인덱스가 필요합니다. 등호 조건 컬럼을 앞에 두고, 범위/정렬 컬럼을 뒤에 두는 식입니다.

```python
class Order(models.Model):
    ...

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["user", "status", "-created_at", "-id"],
                name="idx_order_user_status_created_id",
            ),
            models.Index(
                fields=["user", "-created_at", "-id"],
                name="idx_order_user_created_id",
            ),
        ]
```

[Convention: aggregate/count를 per-row resolver에서 계산하면 안 됨] -- `item_count`, `total_quantity`, `paid_amount` 같은 값이 Schema resolver에서 주문마다 `.items.count()`나 `.payments.aggregate()`로 계산되면 N+1입니다. 목록에서 필요한 계산값은 `annotate()`로 QuerySet에 붙이거나, 이미 주문 테이블에 신뢰 가능한 스냅샷 컬럼으로 저장된 값을 사용해야 합니다.

```python
from django.db.models import Count, Sum

def order_list_queryset(*, user):
    return (
        Order.objects
        .filter(user=user)
        .select_related("customer")
        .annotate(
            item_count=Count("items", distinct=True),
            total_quantity=Sum("items__quantity"),
        )
        .order_by("-created_at", "-id")
    )
```

[Convention: 성능 회귀 테스트가 필요함] -- N+1 수정은 `assertNumQueries` 없으면 쉽게 되돌아갑니다. 페이지 크기와 관련 객체 수를 고정한 테스트로 쿼리 수 상한을 박아야 합니다. `pytest-django`라면 Django `CaptureQueriesContext`나 `django_assert_num_queries`를 쓰는 식이 적합합니다.

```python
import pytest

@pytest.mark.django_db
def test_order_list_query_count(api_client, django_assert_num_queries, order_factory):
    order_factory.create_batch(50, with_items=True)

    with django_assert_num_queries(4):
        response = api_client.get("/api/orders/?cursor=")

    assert response.status_code == 200
```

검증은 실행하지 못했습니다. 현재 디렉터리에 Django 프로젝트 파일이 없고 sandbox도 read-only라 실제 endpoint 호출, `EXPLAIN ANALYZE`, pytest 실행은 불가능했습니다.

---
> **관련 스킬 참조:**
> - Django ORM N+1 최적화 → **implementation-django** 스킬
> - Django Ninja 응답/페이지네이션 → **implementation-django-ninja** 스킬
> - Cursor/Keyset pagination 설계 → **architecture-api** 스킬
> - 인덱스와 쿼리 성능 검토 → **architecture-db** 스킬