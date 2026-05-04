**[주요 내용]**

관리자 주문 목록이 느릴 때는 먼저 “어떤 조건으로 필터링하고 어떤 순서로 정렬하는지”를 기준으로 복합 인덱스를 검토합니다. 단순히 `status`, `created_at`, `customer_id`에 각각 인덱스를 추가하는 방식은 쓰기 비용과 저장 공간만 늘릴 수 있습니다.

대표적인 관리자 주문 목록 패턴이 아래라면:

```python
Order.objects.filter(
    status="PAID",
    created_at__gte=started_at,
    created_at__lt=ended_at,
).order_by("-created_at", "-id")
```

우선 검토할 인덱스는 다음 형태입니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["status", "-created_at", "-id"],
                name="order_status_created_id_idx",
            ),
        ]
```

이유는 `status`가 동등 조건이고, `created_at`이 범위 조건 겸 정렬 조건이며, `id`가 같은 시각 주문의 안정적인 tie-breaker가 되기 때문입니다. 복합 인덱스는 보통 `동등 조건 → 범위/정렬 조건 → 보조 정렬 조건` 순서로 잡습니다.

다른 자주 쓰는 패턴별 후보는 이렇게 나눠 봅니다.

```python
# 특정 고객의 주문 목록
Order.objects.filter(customer_id=customer_id).order_by("-created_at", "-id")

models.Index(
    fields=["customer", "-created_at", "-id"],
    name="order_customer_created_id_idx",
)
```

```python
# 배송 상태별 관리자 목록
Order.objects.filter(
    delivery_status="READY",
).order_by("-paid_at", "-id")

models.Index(
    fields=["delivery_status", "-paid_at", "-id"],
    name="order_delivery_paid_id_idx",
)
```

```python
# 삭제/취소 제외 목록이 대부분이라면 PostgreSQL partial index 검토
models.Index(
    fields=["status", "-created_at", "-id"],
    name="order_active_status_created_id_idx",
    condition=Q(is_deleted=False),
)
```

다만 `status` 값 종류가 적고 거의 모든 주문이 같은 상태라면 `status` 단독 인덱스는 효과가 낮습니다. 이 경우에도 정렬과 결합된 복합 인덱스인지, partial index로 범위를 줄일 수 있는지가 더 중요합니다.

조회 쿼리는 `select_related`와 `prefetch_related`를 구분해서 봅니다.

```python
orders = (
    Order.objects
    .select_related("customer", "payment")
    .filter(status="PAID")
    .order_by("-created_at", "-id")
)
```

`customer`, `payment`, `address`처럼 FK 또는 OneToOne은 `select_related()`가 맞습니다. 목록 50건을 보여주면서 각 주문의 고객명, 결제수단을 접근한다면 N+1을 JOIN 1회로 줄입니다.

```python
orders = (
    Order.objects
    .prefetch_related("items", "items__product")
    .filter(status="PAID")
    .order_by("-created_at", "-id")
)
```

`items`, `coupons`, `tags`처럼 역방향 FK나 M2M은 `prefetch_related()`가 맞습니다. 단, 관리자 목록에서 주문별 상품 전체를 항상 펼치지 않는다면 목록 쿼리에 넣지 않는 편이 낫습니다. prefetch는 페이지의 주문 수만큼 관련 객체를 메모리에 올리므로, N+1은 줄이지만 메모리와 별도 쿼리 비용이 생깁니다.

페이지네이션 비용은 별도 문제입니다. `select_related/prefetch_related`는 관련 객체 로딩 비용을 줄이는 것이고, `OFFSET` 기반 페이지네이션은 뒤 페이지로 갈수록 DB가 앞 행을 많이 건너뛰는 비용이 생깁니다.

```python
# 뒤 페이지가 느려지는 전형적인 패턴
Order.objects.order_by("-created_at", "-id")[10000:10050]
```

대량 주문 테이블에서는 keyset pagination을 검토합니다.

```python
Order.objects.filter(
    Q(created_at__lt=cursor_created_at)
    | Q(created_at=cursor_created_at, id__lt=cursor_id)
).order_by("-created_at", "-id")[:50]
```

이 경우에도 인덱스는 정렬과 커서 조건에 맞춰야 합니다.

```python
models.Index(
    fields=["-created_at", "-id"],
    name="order_created_id_idx",
)
```

검증은 추측이 아니라 실행 계획과 쿼리 수로 봅니다.

```python
qs = Order.objects.filter(status="PAID").order_by("-created_at", "-id")
print(qs.explain(analyze=True, buffers=True))
```

확인 기준은 다음 정도가 실용적입니다.

- `Seq Scan`이 큰 주문 테이블에서 반복되는지
- 정렬 단계에서 큰 `Sort`가 발생하는지
- `actual rows`와 예상 `rows` 차이가 큰지
- `Buffers`에서 read/hit 비용이 과도한지
- 관리자 목록 1페이지 렌더링 쿼리 수가 고정되는지

테스트에는 N+1 회귀 방지를 넣습니다.

```python
with self.assertNumQueries(3):
    response = self.client.get("/admin/orders/")
```

최종적으로 인덱스는 “관리자 목록의 실제 필터 조합 + 정렬 조합” 상위 2~3개에만 우선 추가하는 것이 좋습니다. 주문 테이블은 쓰기가 많기 때문에 인덱스를 많이 추가하면 `INSERT`, `UPDATE`, 상태 변경 배치가 느려질 수 있습니다.

---
> **관련 스킬 참조:**
> - Django ORM 쿼리 리팩터링 → **implementation-django** 스킬
> - 복합 인덱스와 실행 계획 분석 → **architecture-db** 스킬