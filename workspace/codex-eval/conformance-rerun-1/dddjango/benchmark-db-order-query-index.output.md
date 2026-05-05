**조회 패턴 / 워크로드**

관리자 주문 목록이 느릴 때는 먼저 “목록에서 실제로 어떤 필터와 정렬을 같이 쓰는가”를 고정해야 합니다. 대표 패턴은 보통 아래입니다.

```python
Order.objects.filter(status=...).order_by("-created_at", "-id")
Order.objects.filter(payment_status=...).order_by("-created_at", "-id")
Order.objects.filter(status=..., created_at__gte=..., created_at__lt=...).order_by("-created_at", "-id")
Order.objects.filter(customer_id=...).order_by("-created_at", "-id")
Order.objects.filter(order_number=...)
Order.objects.select_related("customer", "payment").prefetch_related("items")
```

인덱스는 테이블 컬럼 목록이 아니라 이 패턴 기준으로 검토합니다.

**우선 검토할 인덱스**

가장 흔한 관리자 목록이 최신 주문순이면 기본 후보는 정렬용 인덱스입니다.

```python
class Order(models.Model):
    class Meta:
        indexes = [
            models.Index(
                fields=["-created_at", "-id"],
                name="order_admin_recent_idx",
            ),
        ]
```

상태 필터와 최신순 정렬을 같이 쓰면 복합 인덱스를 검토합니다. 동등 조건 컬럼을 앞에 두고, 그다음 정렬 컬럼을 둡니다.

```python
models.Index(
    fields=["status", "-created_at", "-id"],
    name="order_status_recent_idx",
)
```

결제 상태, 배송 상태도 관리자 필터에서 자주 쓰이면 같은 방식입니다.

```python
models.Index(
    fields=["payment_status", "-created_at", "-id"],
    name="order_pay_status_recent_idx",
)
```

날짜 범위 필터가 항상 들어가는 화면이면 아래도 후보입니다.

```python
models.Index(
    fields=["-created_at", "-id"],
    name="order_created_id_idx",
)
```

단, `status` 값이 몇 개 안 되고 거의 모든 주문이 같은 상태라면 `status` 단독 인덱스는 효과가 낮을 가능성이 큽니다. 이 경우 단독 인덱스보다 `status + created_at + id` 복합 인덱스 또는 PostgreSQL 부분 인덱스를 봅니다.

```python
from django.db.models import Q

models.Index(
    fields=["-created_at", "-id"],
    condition=Q(status__in=["paid", "shipping", "pending"]),
    name="order_active_recent_idx",
)
```

부분 인덱스는 “관리자가 주로 미완료/진행 중 주문만 본다”처럼 조건이 명확할 때만 좋습니다. 전체 상태를 자주 바꿔 조회한다면 일반 복합 인덱스가 더 낫습니다.

검색 조건도 별도로 봐야 합니다.

```python
Order.objects.filter(order_number="20260505-000123")
```

이런 정확 일치 검색이면 `order_number`에 `unique=True` 또는 B-tree 인덱스가 맞습니다.

```python
order_number = models.CharField(max_length=40, unique=True)
```

반면 관리자 검색이 아래처럼 되어 있으면 일반 B-tree 인덱스로는 부족할 수 있습니다.

```python
Order.objects.filter(order_number__icontains=keyword)
Order.objects.filter(customer__email__icontains=keyword)
```

PostgreSQL이면 `pg_trgm` 기반 `GinIndex`를 검토합니다. 다만 이건 실제 검색 빈도와 데이터 크기를 보고 넣어야 합니다.

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import TrigramSimilarity

models.Index(fields=["order_number"], name="order_number_idx")
# icontains 중심이면 별도 GinIndex + pg_trgm 검토
```

**ORM 쿼리 개선**

관리자 목록에서 가장 먼저 볼 것은 N+1입니다. 주문마다 고객, 결제, 배송지, 라인아이템을 접근한다면 목록 쿼리가 빠르더라도 화면 렌더링에서 느려집니다.

```python
orders = (
    Order.objects
    .select_related("customer", "payment", "shipping_address")
    .prefetch_related(
        Prefetch(
            "items",
            queryset=OrderItem.objects.select_related("product").only(
                "id",
                "order_id",
                "product_id",
                "quantity",
                "unit_price",
                "product__name",
            ),
        )
    )
    .filter(status=status)
    .order_by("-created_at", "-id")
)
```

Django admin이면 `ModelAdmin`에서도 같은 방향으로 잡습니다.

```python
class OrderAdmin(admin.ModelAdmin):
    list_select_related = ("customer", "payment")
    show_full_result_count = False
    ordering = ("-created_at", "-id")
```

`show_full_result_count = False`는 대형 테이블에서 admin이 전체 건수 계산을 반복하는 비용을 줄이는 데 도움이 됩니다. 특히 필터와 검색이 붙은 주문 테이블에서 `COUNT(*)`가 병목이면 효과가 큽니다.

불필요한 컬럼을 많이 읽는다면 `only()`나 `defer()`도 검토합니다.

```python
orders = (
    Order.objects
    .only(
        "id",
        "order_number",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
        "customer_id",
        "customer__email",
    )
    .select_related("customer")
    .order_by("-created_at", "-id")
)
```

다만 `only()`를 쓴 뒤 템플릿이나 admin 컬럼에서 빠진 필드를 접근하면 추가 쿼리가 나갈 수 있으므로 `assertNumQueries`나 Django Debug Toolbar로 확인해야 합니다.

페이지가 깊어질수록 느리면 OFFSET pagination도 의심합니다.

```python
# 느려질 수 있음: 깊은 페이지에서 OFFSET 비용 증가
Order.objects.order_by("-created_at", "-id")[100000:100050]
```

관리자 UX가 허용한다면 keyset pagination 형태가 더 안정적입니다.

```python
Order.objects.filter(
    created_at__lt=last_created_at,
).order_by("-created_at", "-id")[:50]
```

동일한 `created_at` 값이 있을 수 있으므로 실제로는 `created_at`, `id`를 같이 써서 커서 조건을 구성하는 편이 안전합니다.

**EXPLAIN 기준**

Django에서 바로 확인할 수 있습니다.

```python
qs = (
    Order.objects
    .filter(status="paid")
    .order_by("-created_at", "-id")
    .select_related("customer")
)

print(qs.explain(analyze=True, buffers=True))
```

PostgreSQL 기준으로는 아래를 봅니다.

- `Seq Scan`이 대형 `orders` 테이블에서 발생하는지
- `Index Scan`, `Bitmap Index Scan`, `Index Only Scan`으로 바뀌는지
- `Sort`가 별도로 크게 발생하는지
- `actual rows`와 planner의 `rows` 추정치가 크게 어긋나는지
- `Buffers: shared read`가 과도한지
- `Execution Time`이 목표 응답 시간 안에 들어오는지
- 인덱스 추가 후 쓰기 비용이 감당 가능한지

좋은 방향의 예시는 `WHERE status = ... ORDER BY created_at DESC, id DESC LIMIT 50`에서 `order_status_recent_idx`를 타고 별도 대형 `Sort` 없이 상위 N개를 빨리 찾는 것입니다.

나쁜 신호는 이런 쪽입니다.

```text
Seq Scan on orders
Filter: status = 'paid'
Sort Key: created_at DESC, id DESC
Rows Removed by Filter: very large
```

또는 인덱스를 타더라도 결과가 너무 많아 `Bitmap Heap Scan` 후 정렬 비용이 커지는 경우입니다. 이때는 복합 인덱스 순서가 실제 쿼리와 맞는지, `order_by`가 인덱스 순서와 일치하는지 봅니다.

**마이그레이션 검증**

대형 주문 테이블이면 인덱스 추가도 운영 작업입니다. PostgreSQL에서는 가능한 한 concurrent index를 검토합니다.

```python
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("orders", "0001_previous"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="order",
            index=models.Index(
                fields=["status", "-created_at", "-id"],
                name="order_status_recent_idx",
            ),
        ),
    ]
```

검증 순서는 이렇게 잡습니다.

```bash
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate orders 0002
python manage.py migrate --plan
python manage.py migrate
python manage.py showmigrations orders
```

운영 전에는 프로덕션과 비슷한 데이터량의 복제 DB에서 아래를 비교합니다.

```python
before = qs.explain(analyze=True, buffers=True)
# migration 적용
after = qs.explain(analyze=True, buffers=True)
```

확인 기준은 단순히 “인덱스를 탄다”가 아니라 실제 관리자 목록 쿼리의 `Execution Time`, 읽은 buffer 수, 정렬 제거 여부, 반환 row 수가 개선되는지입니다.

마지막으로 인덱스는 쓰기 비용을 늘립니다. 주문 생성/상태 변경이 많은 서비스라면 아래도 같이 확인해야 합니다.

- 주문 생성 TPS에 영향이 있는지
- 상태 변경 업데이트가 느려졌는지
- 중복 인덱스가 생기지 않았는지
- `status` 단독 인덱스처럼 복합 인덱스에 흡수 가능한 인덱스가 남아 있는지
- 실제 쿼리가 새 인덱스를 쓰는지

---
> **관련 스킬 참조:**
> - 관리자 주문 API 응답/페이지네이션 설계 → **architecture-api** 스킬
> - Django admin 또는 selector 코드 리팩터링 → **implementation-django** 스킬