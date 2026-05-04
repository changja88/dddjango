프로젝트 디렉터리가 비어 있어서 실제 `Order` 모델/뷰는 확인하지 못했습니다. 대신 Django 주문 목록 조회에서 보통 효과가 큰 최적화 전략은 아래 순서로 잡는 게 좋습니다.

**1. 목록 필터/정렬 기준에 맞춘 복합 인덱스**

주문 목록은 보통 다음 조건을 같이 씁니다.

- `customer_id`
- `status`
- `created_at`
- `paid_at`
- `shop_id` / `seller_id` / `tenant_id`
- 최신순 정렬: `ORDER BY created_at DESC`
- 기간 검색: `created_at BETWEEN ...`

예시:

```python
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
            models.Index(fields=["status", "customer", "-created_at"]),
        ]
```

실제 API가 멀티테넌트라면 가장 앞에 `shop_id`나 `tenant_id`를 두는 게 중요합니다.

```python
models.Index(fields=["shop", "status", "-created_at"])
models.Index(fields=["shop", "customer", "-created_at"])
```

핵심은 “자주 쓰는 `WHERE` 조건 + `ORDER BY` 순서”에 맞추는 것입니다.

**2. N+1 제거**

주문 목록에서 고객, 배송지, 결제, 주문상품을 같이 보여주면 N+1이 쉽게 생깁니다.

```python
qs = (
    Order.objects
    .select_related("customer", "payment", "shipping_address")
    .prefetch_related("items", "items__product")
)
```

- `ForeignKey`, `OneToOneField`: `select_related`
- 역참조, `ManyToMany`, 주문상품 목록: `prefetch_related`

주문상품까지 보여주되 필요한 필드가 적다면:

```python
from django.db.models import Prefetch

qs = Order.objects.prefetch_related(
    Prefetch(
        "items",
        queryset=OrderItem.objects.select_related("product").only(
            "id", "order_id", "quantity", "price", "product__name"
        ),
    )
)
```

**3. 필요한 컬럼만 조회**

목록 화면에서 상세 컬럼을 전부 가져오지 않도록 제한합니다.

```python
qs = Order.objects.select_related("customer").only(
    "id",
    "order_number",
    "status",
    "created_at",
    "total_amount",
    "customer__id",
    "customer__name",
)
```

단, `only()`를 쓸 때 나중에 빠진 필드에 접근하면 추가 쿼리가 발생하므로 serializer/template 접근 필드와 맞춰야 합니다.

**4. count 비용 줄이기**

Django pagination은 기본적으로 `COUNT(*)`를 실행합니다. 주문 테이블이 크면 이게 병목입니다.

대안:

- 무한 스크롤 또는 cursor pagination 사용
- “다음 페이지 존재 여부”만 확인하도록 `limit + 1` 조회
- 관리자/백오피스에서 정확한 전체 건수가 꼭 필요하지 않다면 estimated count 사용

예시 cursor 방식:

```python
qs = Order.objects.filter(created_at__lt=cursor).order_by("-created_at")[:page_size + 1]
```

이 경우 인덱스는 `created_at DESC` 또는 조건 포함 복합 인덱스가 잘 맞습니다.

**5. annotate 남용 주의**

목록에서 주문상품 합계, 리뷰 수, 환불 여부 등을 `annotate()`로 매번 계산하면 느려질 수 있습니다.

가능하면:

- `Order`에 집계값 저장: `item_count`, `total_amount`, `paid_amount`
- 상태값 저장: `has_refund`, `is_delayed`
- 주기적/이벤트 기반 denormalization

예:

```python
class Order(models.Model):
    item_count = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
```

**6. 권장 queryset 형태**

```python
def get_order_list_queryset(*, shop_id, status=None, customer_id=None):
    qs = (
        Order.objects
        .filter(shop_id=shop_id)
        .select_related("customer", "payment")
        .only(
            "id",
            "order_number",
            "status",
            "created_at",
            "total_amount",
            "customer__id",
            "customer__name",
            "payment__method",
        )
        .order_by("-created_at")
    )

    if status:
        qs = qs.filter(status=status)

    if customer_id:
        qs = qs.filter(customer_id=customer_id)

    return qs
```

이에 대응하는 인덱스:

```python
models.Index(fields=["shop", "-created_at"]),
models.Index(fields=["shop", "status", "-created_at"]),
models.Index(fields=["shop", "customer", "-created_at"]),
```

**7. 적용 전 확인할 것**

실제 인덱스는 감으로 추가하지 말고 아래를 확인하는 게 좋습니다.

```python
print(qs.explain(analyze=True, buffers=True))
```

PostgreSQL 기준으로 봐야 할 지점:

- `Seq Scan`이 큰 테이블에서 발생하는지
- `Sort` 비용이 큰지
- `Index Scan` 또는 `Index Only Scan`이 쓰이는지
- `Rows Removed by Filter`가 과도한지
- `COUNT(*)`가 병목인지

정리하면, 주문 목록은 보통 `tenant/shop + filter + created_at desc` 복합 인덱스, `select_related/prefetch_related`로 N+1 제거, cursor pagination, 목록용 필드 제한이 가장 효과가 큽니다. 실제 모델과 API 코드가 있으면 그 기준으로 정확한 인덱스 조합과 queryset을 더 좁혀서 제안할 수 있습니다.