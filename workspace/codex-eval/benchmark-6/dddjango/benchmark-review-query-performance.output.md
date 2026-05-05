지정된 `/Users/hyun/Desktop/dddjango/none`은 없어서, 실제로 읽을 수 있는 fixture인 `evals/fixtures/django-shop`을 기준으로 봤습니다. 이 fixture에는 “주문 목록 API” 자체는 없고, 레거시 DRF 상세 API만 있습니다: [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:1). 아래 리뷰는 이 코드를 주문 목록 API로 확장/전환할 때의 수정 방향입니다.

**Findings**

High: [Django Ninja 전환] -- [api_drf.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:1)는 DRF `APIView`/`ModelSerializer`이고 [fields = "__all__"](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/api_drf.py:11)를 씁니다. 이 프로젝트 정책에서는 API를 Django Ninja `Router`/`Schema`로 옮겨야 하고, 목록 응답은 명시 필드만 노출해야 합니다.

High: [ORM N+1] -- `Order`는 현재 FK가 없어서 목록 summary에는 `select_related()`가 필요 없습니다. 하지만 주문 목록에서 [Reservation.order/product FK](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:41)를 함께 보여주면 reverse FK인 `reservation_set`은 `prefetch_related()`, 각 예약의 `product` FK는 `Prefetch(... queryset=Reservation.objects.select_related("product"))`가 맞습니다. `select_related`와 `prefetch_related`를 구분하지 않으면 주문 N개마다 예약/상품 조회가 반복됩니다.

High: [Pagination] -- 목록 엔드포인트와 페이지네이션이 없습니다. 대량 주문에서 offset/page-number는 뒤 페이지로 갈수록 느려지므로 고객 주문 목록/운영 피드에는 `created_at,id` 기반 cursor pagination을 우선하세요. 랜덤 페이지 이동이 필요한 소규모 관리자 화면만 offset을 허용하는 쪽이 낫습니다.

Medium: [Schema 과중첩] -- 목록 응답에서 상품 전체 객체, 예약 전체 객체를 중첩하면 payload가 커지고 serializer가 관계를 계속 따라가게 됩니다. 목록은 주문 summary와 얕은 line summary까지만 두고, 상세 API에서 전체 line을 내려주는 구조가 안전합니다.

**Suggested Diff**

```diff
diff --git a/shop/orders/models.py b/shop/orders/models.py
@@
 class Order(models.Model):
@@
     created_at = models.DateTimeField(auto_now_add=True)
+
+    class Meta:
+        indexes = [
+            models.Index(
+                fields=["-created_at", "-id"],
+                name="order_list_cursor_idx",
+            ),
+        ]

diff --git a/shop/orders/api.py b/shop/orders/api.py
new file mode 100644
--- /dev/null
+++ b/shop/orders/api.py
@@
+from decimal import Decimal
+
+from django.db.models import Count, Prefetch, QuerySet
+from django.http import HttpRequest
+from ninja import Router, Schema
+from ninja.pagination import CursorPagination, paginate
+
+from shop.orders.models import Order, Reservation
+
+router = Router(tags=["orders"])
+
+
+class OrderLineSummaryOut(Schema):
+    product_id: int
+    product_sku: str
+    product_name: str
+    quantity: int
+
+
+class OrderListOut(Schema):
+    id: int
+    customer_email: str
+    status: str
+    total_amount: Decimal
+    created_at: str
+    line_count: int
+    lines: list[OrderLineSummaryOut]
+
+    @staticmethod
+    def resolve_lines(obj: Order) -> list[OrderLineSummaryOut]:
+        return [
+            OrderLineSummaryOut(
+                product_id=reservation.product_id,
+                product_sku=reservation.product.sku,
+                product_name=reservation.product.name,
+                quantity=reservation.quantity,
+            )
+            for reservation in getattr(obj, "prefetched_reservations", [])
+        ]
+
+
+class OrderCursorPagination(CursorPagination):
+    ordering = ("-created_at", "-id")
+    page_size = 50
+    max_page_size = 100
+
+
+@router.get("", response=list[OrderListOut])
+@paginate(OrderCursorPagination)
+def list_orders(request: HttpRequest) -> QuerySet[Order]:
+    reservations = Reservation.objects.select_related("product").only(
+        "order_id",
+        "product_id",
+        "product__sku",
+        "product__name",
+        "quantity",
+    )
+    return (
+        Order.objects.annotate(line_count=Count("reservation"))
+        .prefetch_related(
+            Prefetch(
+                "reservation_set",
+                queryset=reservations,
+                to_attr="prefetched_reservations",
+            )
+        )
+        .order_by("-created_at", "-id")
+    )
```

`lines`가 목록 화면에 꼭 필요 없다면 `lines`와 `prefetch_related()`를 제거하고 `line_count`만 내려주세요. 그 경우 목록 쿼리는 더 가벼워집니다.

**Verification**

1. N+1 회귀 테스트: 주문 50개, 주문당 예약 2개를 만들고 `assertNumQueries(2)` 수준으로 고정되는지 확인합니다. line summary를 제거하면 1 query까지 기대할 수 있습니다.
2. Pagination 측정: PostgreSQL/stage에서 `Order.objects.order_by("-created_at", "-id").explain(analyze=True, buffers=True)`로 cursor index 사용 여부를 확인합니다.
3. API 테스트: `ninja.testing.TestClient(router)`로 첫 페이지 응답에 `next` cursor가 있고, 응답 schema가 `OrderListOut` 필드만 포함하는지 검증합니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리 최적화 → **implementation-django** 스킬
> - Django Ninja Schema/Router/pagination → **implementation-django-ninja** 스킬
> - 인덱스와 EXPLAIN 측정 → **architecture-db** 스킬