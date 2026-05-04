**주요 내용**

프로젝트 파일이 없어 실제 모델명은 가정합니다. 주문 목록의 대표 조회가 `shop_id/customer_id/status/date range + 최신순 페이지네이션`이라면, 인덱스는 테이블 구조가 아니라 **조회 패턴 단위**로 잡아야 합니다.

| 조회 패턴 | 권장 인덱스 | 이유 |
|---|---|---|
| 관리자 주문 목록: `shop_id`, `status`, 최신순 | `(shop_id, status, -created_at, -id)` | 동등 조건을 앞에, 정렬/커서를 뒤에 둠 |
| 전체 상태 탭: `shop_id`, 최신순 | `(shop_id, -created_at, -id)` | `status` 없는 목록도 별도 최적화 필요 |
| 고객 주문 내역 | `(customer_id, -created_at, -id)` | 마이페이지 주문 목록 전용 |
| 기간 필터가 핵심 | `(shop_id, status, created_at)` | `created_at BETWEEN` 범위 조건은 뒤쪽 |
| 주문번호 검색 | `order_number` unique/index | exact lookup은 단일 인덱스 |
| soft delete 사용 | partial index: `deleted_at IS NULL` | 활성 주문만 조회하면 인덱스 크기 감소 |

Django 모델 예시는 PostgreSQL 기준입니다.

```python
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        SHIPPING = "shipping", "Shipping"
        DONE = "done", "Done"
        CANCELED = "canceled", "Canceled"

    shop = models.ForeignKey("shops.Shop", on_delete=models.PROTECT)
    customer = models.ForeignKey("users.User", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status)
    order_number = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["shop", "status", "-created_at", "-id"],
                name="order_shop_status_recent_idx",
                condition=Q(deleted_at__isnull=True),
            ),
            models.Index(
                fields=["shop", "-created_at", "-id"],
                name="order_shop_recent_idx",
                condition=Q(deleted_at__isnull=True),
            ),
            models.Index(
                fields=["customer", "-created_at", "-id"],
                name="order_customer_recent_idx",
                condition=Q(deleted_at__isnull=True),
            ),
        ]
```

QuerySet은 목록 화면에서 실제로 렌더링하는 관계만 가져옵니다.

```python
from django.db.models import Prefetch, Q


def order_list_qs(*, shop_id, status=None, cursor=None):
    qs = (
        Order.objects.filter(shop_id=shop_id, deleted_at__isnull=True)
        .select_related("customer", "shipping_address")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product").only(
                    "id",
                    "order_id",
                    "quantity",
                    "product__name",
                ),
                to_attr="prefetched_items",
            )
        )
        .order_by("-created_at", "-id")
    )

    if status:
        qs = qs.filter(status=status)

    if cursor:
        qs = qs.filter(
            Q(created_at__lt=cursor.created_at)
            | Q(created_at=cursor.created_at, id__lt=cursor.id)
        )

    return qs[:50]
```

`select_related()`와 `prefetch_related()`는 구분해서 써야 합니다.

`select_related()`는 `Order.customer`, `Order.shipping_address`처럼 FK/O2O에 사용합니다. SQL JOIN으로 한 번에 가져오므로 주문 50건의 고객 접근에서 N+1을 막습니다.

`prefetch_related()`는 `Order.items`, `items.product_options` 같은 역방향 FK/M2M에 사용합니다. 별도 쿼리 + Python 매칭 방식이라, 주문 목록에서 주문별 상품 라인을 보여줄 때 적합합니다. 단, 상품까지 FK라면 prefetch 내부 queryset에서 `select_related("product")`를 같이 씁니다.

검증 기준은 추측이 아니라 측정입니다.

```bash
python manage.py sqlmigrate orders 000X
python manage.py shell
```

```python
qs = order_list_qs(shop_id=1, status="paid")
print(qs.explain(analyze=True, buffers=True))
```

확인할 기준은 다음입니다.

- 대형 주문 테이블에서 `Seq Scan`이 사라지고 `Index Scan`, `Bitmap Index Scan`, 가능하면 `Index Only Scan`이 나오는지
- `Execution Time`이 목표 SLA 안에 들어오는지, 예: p95 100ms 이하
- `actual rows`와 예상 `rows` 차이가 크지 않은지, 크면 `ANALYZE` 필요
- 목록 1페이지 렌더링 쿼리 수가 고정인지

```python
with self.assertNumQueries(3):
    list(order_list_qs(shop_id=shop.id, status="paid"))
```

인덱스는 쓰기 비용을 늘리므로 위 후보를 전부 넣지 말고, 실제 목록 endpoint의 필터 조합과 `EXPLAIN ANALYZE` 결과로 2~3개만 유지하는 쪽이 안전합니다.

---
> **관련 스킬 참조:**
> - 주문 조회 QuerySet 리팩터링 및 회귀 테스트 작성 → **implementation-django** 스킬