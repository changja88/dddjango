`/Users/hyun/Desktop/dddjango/none`는 존재하지 않아 fixture 파일을 읽을 수 없었습니다. 현재 작업 디렉터리에도 fixture/code 파일이 없어, 아래는 실제 코드 변경이 아닌 Django 관리자 주문 목록의 전형적인 조회 패턴 기준 검토안입니다.

**[주요 내용]**

우선 인덱스는 “주문 테이블에 뭐가 있나”가 아니라 실제 관리자 목록의 `filter() + order_by()` 조합에 맞춰야 합니다. 보통 느린 쿼리는 이런 형태입니다.

```python
Order.objects.filter(
    status=status,
    payment_status=payment_status,
    created_at__gte=start,
    created_at__lt=end,
).order_by("-created_at", "-id")
```

이 패턴이 실제로 자주 호출된다면 1순위 후보는 복합 인덱스입니다.

```diff
 class Order(models.Model):
     ...

     class Meta:
         indexes = [
+            models.Index(
+                fields=["status", "payment_status", "-created_at", "-id"],
+                name="idx_order_admin_status_pay_created",
+            ),
         ]
```

단, `status`만 자주 쓰고 `payment_status`는 가끔 쓰는 정도라면 아래처럼 더 작은 인덱스가 낫습니다.

```diff
         indexes = [
+            models.Index(
+                fields=["status", "-created_at", "-id"],
+                name="idx_order_admin_status_created",
+            ),
         ]
```

고객별 주문 조회가 관리자에서 자주 느리다면 별도 패턴으로 봐야 합니다.

```diff
         indexes = [
+            models.Index(
+                fields=["customer", "-created_at", "-id"],
+                name="idx_order_admin_customer_created",
+            ),
         ]
```

Soft delete나 활성 주문만 관리자에서 조회한다면 PostgreSQL에서는 부분 인덱스를 검토합니다.

```python
models.Index(
    fields=["status", "-created_at", "-id"],
    name="idx_order_admin_active_status_created",
    condition=models.Q(deleted_at__isnull=True),
)
```

검색 조건은 별도로 봐야 합니다. `order_number__exact`는 단일 B-tree 또는 unique index가 맞지만, `customer_name__icontains`, `memo__icontains` 같은 부분 문자열 검색은 일반 B-tree 인덱스로 해결되지 않습니다. PostgreSQL이면 trigram index나 full-text search를 별도 검토해야 합니다.

쿼리 개선은 인덱스와 분리해서 봅니다. 관리자 목록에서 FK/O2O 필드를 표시한다면 `select_related()`가 N+1을 줄입니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("customer", "payment", "shipping_address")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("customer", "payment", "shipping_address")
        )
```

주문 항목을 목록 행마다 렌더링한다면 `prefetch_related()`를 쓰되, 관리자 목록에서는 비용이 커질 수 있습니다. 단순히 상품 수나 총액만 필요하다면 매 행의 items 전체를 prefetch하기보다 이미 저장된 요약 컬럼 또는 제한된 annotation을 검토합니다.

```python
from django.db.models import Prefetch

Order.objects.prefetch_related(
    Prefetch(
        "items",
        queryset=OrderItem.objects.select_related("product").only(
            "id",
            "order_id",
            "product_id",
            "quantity",
            "product__name",
        ),
    )
)
```

중요한 구분은 `select_related/prefetch_related`는 N+1 쿼리 수를 줄이는 장치이고, pagination 비용을 없애지 않는다는 점입니다. Django admin의 느림이 `COUNT(*)`, 큰 `OFFSET`, 정렬 때문에 발생하면 관계 로딩 최적화만으로는 해결되지 않습니다.

관리자에서 전체 건수 계산이 부담이면 먼저 이것을 검토합니다.

```python
class OrderAdmin(admin.ModelAdmin):
    show_full_result_count = False
```

커스텀 목록 화면이라면 offset pagination 대신 keyset pagination을 검토합니다.

```python
Order.objects.filter(
    created_at__lt=cursor_created_at,
).order_by("-created_at", "-id")[:50]
```

검증 기준은 아래 순서가 적절합니다.

1. Django Debug Toolbar, django-silk, DB slow query log로 실제 느린 관리자 쿼리를 캡처합니다.
2. `QuerySet.explain(analyze=True, buffers=True)` 또는 DB 콘솔의 `EXPLAIN ANALYZE`로 `Seq Scan`, `Sort`, `COUNT`, 큰 `OFFSET` 여부를 확인합니다.
3. 인덱스 추가 전후로 `actual time`, `shared read`, `rows` 추정 오차를 비교합니다.
4. `assertNumQueries`로 N+1 회귀만 별도 테스트합니다.
5. 쓰기 많은 주문 테이블이므로 위 후보 인덱스를 전부 넣지 말고, 실제 관리자 필터 조합 상위 1~2개부터 추가합니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리/관리자 최적화 → **implementation-django** 스킬
> - 복합 인덱스와 EXPLAIN 기준 검증 → **architecture-db** 스킬