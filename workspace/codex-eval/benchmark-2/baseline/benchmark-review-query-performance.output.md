**주요 내용**

코드 파일을 찾을 수 없어 특정 라인 리뷰는 못 했습니다. `/private/tmp/dddjango-codex-eval`이 비어 있어서, 주문 목록 API에서 보통 발생하는 Django ORM + Django Ninja 문제 기준으로 리뷰합니다.

**Findings**

1. **[QuerySet 최적화] 주문 목록에서 관계 필드를 응답 스키마가 lazy loading하면 N+1이 납니다.**  
   `OrderOut`이 `customer`, `items`, `items.product`, `payment`, `shipping_address` 같은 중첩 필드나 resolver를 갖고 있는데 queryset이 `select_related`/`prefetch_related` 없이 `Order.objects.all()`이면, Ninja가 응답 직렬화 중 객체별로 추가 쿼리를 실행합니다.

   권장 형태:

   ```python
   orders = (
       Order.objects
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
                       "quantity",
                       "unit_price",
                       "product__id",
                       "product__name",
                   )
               ),
           )
       )
       .order_by("-created_at", "-id")
   )
   ```

2. **[Django Ninja Schema] `resolve_<field>` 안에서 ORM 접근을 하면 숨은 N+1이 됩니다.**  
   예를 들어 `resolve_total_items()`에서 `obj.items.count()`를 호출하거나, `resolve_customer_name()`에서 `obj.customer.name`을 접근하면 prefetch/select가 없을 때 응답 생성 단계에서 쿼리가 터집니다. 집계값은 `annotate()`로 올리고, 관계 객체는 사전에 로딩해야 합니다.

   ```python
   orders = orders.annotate(
       item_count=Count("items"),
       total_quantity=Sum("items__quantity"),
   )
   ```

3. **[Pagination] offset/page-number 기반 pagination은 주문 테이블이 커질수록 느려집니다.**  
   주문 목록은 보통 최신순 조회가 많고 데이터가 계속 삽입됩니다. `?page=10000` 또는 큰 `offset`은 DB가 앞 행을 계속 스캔/버리게 만들고, 중간 삽입으로 중복/누락도 생깁니다. 대량 주문 목록은 cursor/keyset pagination이 맞습니다.

   기준 정렬은 반드시 안정적이어야 합니다:

   ```python
   .order_by("-created_at", "-id")
   ```

   커서 조건은 이런 형태가 됩니다:

   ```python
   Q(created_at__lt=cursor_created_at)
   | Q(created_at=cursor_created_at, id__lt=cursor_id)
   ```

4. **[Index 설계] pagination 정렬과 필터 조건을 받치는 복합 인덱스가 필요합니다.**  
   예를 들어 사용자별 주문 목록이면 다음 계열 인덱스가 필요합니다.

   ```python
   models.Index(
       fields=["user", "-created_at", "-id"],
       name="order_user_created_id_idx",
   )
   ```

   상태 필터가 자주 붙으면 워크로드에 따라 `["user", "status", "-created_at", "-id"]`가 더 적합할 수 있습니다. 인덱스 순서는 “동등 조건 → 정렬/범위 조건” 순서로 잡아야 합니다.

5. **[Response 구조] 목록 API에서 전체 count를 매번 반환하면 count 쿼리가 병목이 될 수 있습니다.**  
   `total_count`가 꼭 필요한 관리자 화면이 아니라면 주문 목록 응답은 `results`, `next_cursor`, `has_more` 중심이 낫습니다. `count()`는 대형 테이블에서 별도 비용이 큽니다.

   ```python
   class OrderListOut(Schema):
       results: list[OrderOut]
       next_cursor: str | None
       has_more: bool
   ```

6. **[회귀 방지 테스트] N+1은 `assertNumQueries`로 고정해야 합니다.**  
   주문 10개와 각 주문 item 2개를 만든 뒤 목록 API 쿼리 수가 주문 수에 비례해 증가하지 않는지 테스트해야 합니다. 목표는 보통 `orders + selected FK join + items prefetch + product join` 정도의 고정 쿼리 수입니다.

**권장 구조**

```python
@router.get("/orders", response=OrderListOut)
def list_orders(
    request,
    cursor: str | None = None,
    limit: int = 50,
) -> OrderListOut:
    queryset = (
        Order.objects
        .filter(user=request.user)
        .select_related("customer", "payment", "shipping_address")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product"),
            )
        )
        .annotate(item_count=Count("items"))
        .order_by("-created_at", "-id")
    )

    queryset = apply_order_cursor(queryset, cursor)

    rows = list(queryset[: limit + 1])
    has_more = len(rows) > limit
    results = rows[:limit]

    return OrderListOut(
        results=results,
        next_cursor=encode_order_cursor(results[-1]) if has_more else None,
        has_more=has_more,
    )
```

핵심은 API 함수가 “페이지 크기 + 1개”만 가져오고, Ninja 스키마가 접근할 모든 관계와 집계를 queryset 단계에서 이미 준비하는 것입니다.

---
> **관련 스킬 참조:**
> - QuerySet/N+1 최적화 → **implementation-django** 스킬
> - Cursor/Keyset pagination 설계 → **architecture-api** 스킬
> - Django Ninja 응답/Schema 구조 → **implementation-django-ninja** 스킬