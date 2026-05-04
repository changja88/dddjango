현재 `/private/tmp/dddjango-codex-eval`에는 Django 소스 파일이 없어 실제 모델 기준으로는 확인할 수 없었습니다. 대신 주문 목록 API에서 흔히 병목이 나는 패턴 기준으로 제안합니다.

**인덱스 전략**

주문 목록은 보통 `user`, `status`, `created_at`, `paid_at`, `shop/store`, `is_deleted` 조건과 `created_at DESC` 정렬이 핵심입니다.

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["user", "status", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]
```

추천 기준은 다음과 같습니다.

- “내 주문 목록”: `WHERE user_id = ? ORDER BY created_at DESC`
  - `Index(fields=["user", "-created_at"])`
- 관리자 주문 목록에서 상태 필터:
  - `Index(fields=["status", "-created_at"])`
- 사용자 + 상태 필터가 자주 같이 쓰이면:
  - `Index(fields=["user", "status", "-created_at"])`
- 삭제 제외 조건이 항상 붙고 PostgreSQL이면 partial index도 고려:
  - `condition=Q(is_deleted=False)`
- 검색어가 주문번호 exact lookup이면 `order_number`에 unique/index
- `icontains` 검색이 많으면 일반 B-tree 인덱스가 잘 안 먹으므로 PostgreSQL trigram index 고려

**QuerySet 최적화**

목록 조회에서는 N+1 제거가 우선입니다.

```python
orders = (
    Order.objects
    .filter(user=request.user, is_deleted=False)
    .select_related("user", "shipping_address", "payment")
    .prefetch_related("items", "items__product")
    .order_by("-created_at")
)
```

관계 기준은 이렇게 나누면 됩니다.

- `ForeignKey`, `OneToOneField`: `select_related`
  - 예: `user`, `payment`, `shipping_address`
- 역참조, `ManyToMany`: `prefetch_related`
  - 예: `items`, `items__product`, `coupons`

필드가 많은 테이블이면 목록에 필요한 컬럼만 가져옵니다.

```python
orders = orders.only(
    "id",
    "order_number",
    "status",
    "total_price",
    "created_at",
    "user_id",
)
```

다만 `only()`는 serializer가 제외된 필드를 접근하면 추가 쿼리가 발생할 수 있으니, DRF/Ninja 응답 필드와 반드시 맞춰야 합니다.

**페이지네이션**

큰 주문 테이블에서는 offset pagination이 느려질 수 있습니다.

```python
Order.objects.filter(
    created_at__lt=cursor_created_at,
).order_by("-created_at")[:limit]
```

가능하면 cursor pagination을 권장합니다. 정렬 안정성을 위해 `created_at`만 쓰지 말고 보통 `("-created_at", "-id")` 조합을 씁니다.

```python
models.Index(fields=["-created_at", "-id"])
models.Index(fields=["user", "-created_at", "-id"])
```

**집계 최적화**

목록에서 주문상품 개수, 총 수량 등을 보여줄 때 Python loop로 계산하지 말고 annotate를 사용합니다.

```python
from django.db.models import Count, Sum

orders = orders.annotate(
    item_count=Count("items"),
    total_quantity=Sum("items__quantity"),
)
```

단, 조인이 많아지면 중복 row로 느려질 수 있으니 실제 SQL을 확인해야 합니다.

**검증 방법**

적용 전후로 아래를 확인하는 게 좋습니다.

```python
print(Order.objects.filter(user_id=1).order_by("-created_at").explain())
```

PostgreSQL이면 `EXPLAIN ANALYZE`로 실제 실행 계획을 확인하고, `Seq Scan`, 큰 `Sort`, 과도한 `Nested Loop`가 보이면 인덱스나 queryset을 조정합니다.

요약하면, 주문 목록은 대개 `user/status + created_at desc` 복합 인덱스, `select_related/prefetch_related`로 N+1 제거, cursor pagination 전환이 가장 큰 효과를 냅니다.