# 주문 통계 대시보드 QuerySet

## 모델 기준

```python
class Customer(models.Model):
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=[
        ('basic', '일반'), ('silver', '실버'),
        ('gold', '골드'), ('platinum', '플래티넘'),
    ])
    joined_at = models.DateTimeField()


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', '대기'), ('confirmed', '확정'),
        ('shipped', '배송중'), ('delivered', '배송완료'),
        ('cancelled', '취소'),
    ])
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 1. 월별 매출 집계 + 전월 대비 증감률 (Window 함수)

`TruncMonth`로 월 단위로 절삭한 뒤 집계하고, `Lag` Window 함수로 전월 매출을 참조하여 증감률을 계산한다.
취소 주문은 매출에서 제외한다.

```python
from django.db.models import Sum, Count, F, Window, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth, Lag, Coalesce

monthly_revenue = (
    Order.objects
    .exclude(status="cancelled")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(
        revenue=Sum("total_amount"),
        order_count=Count("id"),
    )
    .order_by("month")
)

monthly_revenue_with_growth = (
    Order.objects
    .exclude(status="cancelled")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(revenue=Sum("total_amount"))
    .order_by("month")
    .annotate(
        prev_month_revenue=Window(
            expression=Lag("revenue", offset=1, default=0),
            order_by=F("month").asc(),
        ),
        revenue_change=F("revenue") - Window(
            expression=Lag("revenue", offset=1, default=0),
            order_by=F("month").asc(),
        ),
    )
)
```

`Lag`는 정렬 기준(`order_by=F("month").asc()`)에 따라 직전 행의 `revenue` 값을 가져온다.
첫 번째 월은 이전 데이터가 없으므로 `default=0`으로 처리한다.
`revenue_change`는 당월 매출에서 전월 매출을 뺀 절대 증감액이다.

증감률을 퍼센트로 구하려면 Python 후처리가 안전하다. DB 레벨에서 나눗셈 시 전월 매출이 0인 경우(첫 월) division by zero가 발생하기 때문이다.

```python
results = list(monthly_revenue_with_growth)
for row in results:
    prev = row["prev_month_revenue"]
    if prev and prev > 0:
        row["growth_rate"] = (row["revenue"] - prev) / prev * 100
    else:
        row["growth_rate"] = None
```

DB 레벨에서 증감률까지 처리해야 한다면 `Case/When`으로 zero division을 방어한다.

```python
from django.db.models import Case, When, Value
from django.db.models.functions import Cast
from django.db.models import FloatField

monthly_revenue_with_pct = (
    Order.objects
    .exclude(status="cancelled")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(revenue=Sum("total_amount"))
    .order_by("month")
    .annotate(
        prev_month_revenue=Window(
            expression=Lag("revenue", offset=1, default=0),
            order_by=F("month").asc(),
        ),
        growth_rate=Case(
            When(
                prev_month_revenue__gt=0,
                then=(
                    Cast(F("revenue") - F("prev_month_revenue"), FloatField())
                    / Cast(F("prev_month_revenue"), FloatField())
                    * Value(100.0)
                ),
            ),
            default=Value(None),
            output_field=FloatField(),
        ),
    )
)
```

---

## 2. 고객 등급별 주문 건수와 평균 금액 (조건부 집계)

`filter=Q()` 파라미터를 사용하여 상태별 조건부 집계를 수행한다.
`Case/When`보다 `filter=Q()`가 Django에서 권장되는 조건부 집계 패턴이다.

```python
from django.db.models import Count, Avg, Sum, Q, DecimalField
from django.db.models.functions import Coalesce

tier_stats = (
    Customer.objects
    .values("tier")
    .annotate(
        total_orders=Count("order"),
        confirmed_orders=Count(
            "order", filter=Q(order__status="confirmed")
        ),
        shipped_orders=Count(
            "order", filter=Q(order__status="shipped")
        ),
        delivered_orders=Count(
            "order", filter=Q(order__status="delivered")
        ),
        cancelled_orders=Count(
            "order", filter=Q(order__status="cancelled")
        ),
        avg_order_amount=Coalesce(
            Avg("order__total_amount"),
            0,
            output_field=DecimalField(),
        ),
        total_revenue=Coalesce(
            Sum(
                "order__total_amount",
                filter=~Q(order__status="cancelled"),
            ),
            0,
            output_field=DecimalField(),
        ),
        avg_revenue_per_customer=Coalesce(
            Avg(
                "order__total_amount",
                filter=~Q(order__status="cancelled"),
            ),
            0,
            output_field=DecimalField(),
        ),
    )
    .order_by("tier")
)
```

`filter=Q()`는 SQL의 `FILTER (WHERE ...)` 또는 `CASE WHEN ... END` 구문으로 변환되어
한 번의 쿼리로 여러 조건별 집계를 수행한다.
`Coalesce`로 주문이 없는 등급의 `NULL`을 `0`으로 처리한다.

---

## 3. 최근 3개월 주문 없는 고객 목록 (Subquery/Exists)

존재 여부 확인에는 `Subquery + Count`보다 `Exists`가 효율적이다.
`EXISTS`는 일치하는 첫 번째 행을 찾으면 즉시 `True`를 반환(short-circuit)하므로
모든 행을 세야 하는 `Count`보다 빠르다.

```python
from datetime import timedelta

from django.db.models import Exists, OuterRef
from django.utils import timezone

three_months_ago = timezone.now() - timedelta(days=90)

recent_orders = Order.objects.filter(
    customer=OuterRef("pk"),
    created_at__gte=three_months_ago,
)

inactive_customers = (
    Customer.objects
    .filter(~Exists(recent_orders))
    .select_related()
)
```

`~Exists()`는 SQL의 `NOT EXISTS` 서브쿼리로 변환된다.
`OuterRef("pk")`로 외부 쿼리(Customer)의 기본 키를 참조하여 상관 서브쿼리를 구성한다.

추가 컨텍스트가 필요하다면 마지막 주문일과 가입일을 함께 annotation 할 수 있다.

```python
from django.db.models import Subquery, Max
from django.db.models.functions import Coalesce, Now

last_order_date = (
    Order.objects
    .filter(customer=OuterRef("pk"))
    .values("customer")
    .annotate(last_date=Max("created_at"))
    .values("last_date")[:1]
)

inactive_customers_with_detail = (
    Customer.objects
    .filter(~Exists(recent_orders))
    .annotate(
        last_order_date=Subquery(last_order_date),
        days_since_last_order=ExpressionWrapper(
            Now() - Coalesce(Subquery(last_order_date), F("joined_at")),
            output_field=DurationField(),
        ),
    )
    .order_by("tier", "name")
)
```

`Subquery`에서 `.values("last_date")[:1]` 패턴을 사용하여 반드시 단일 행, 단일 컬럼을 반환한다.
주문이 한 번도 없는 고객은 `last_order_date`가 `NULL`이므로 `Coalesce`로 `joined_at`을 대체값으로 사용한다.

---

## 4. 고객별 주문 순위 (Window Rank)

`Window` 함수와 `DenseRank`를 사용하여 고객별 주문 금액 순위를 매긴다.
`Rank`는 동일 순위 시 다음 순위를 건너뛰고(1, 2, 2, 4), `DenseRank`는 건너뛰지 않는다(1, 2, 2, 3).

```python
from django.db.models import F, Window
from django.db.models.functions import Rank, DenseRank, RowNumber

orders_with_rank = (
    Order.objects
    .exclude(status="cancelled")
    .select_related("customer")
    .annotate(
        customer_rank=Window(
            expression=DenseRank(),
            partition_by=[F("customer")],
            order_by=F("total_amount").desc(),
        ),
        customer_row_num=Window(
            expression=RowNumber(),
            partition_by=[F("customer")],
            order_by=F("total_amount").desc(),
        ),
    )
)
```

`partition_by=[F("customer")]`로 고객별 파티션을 나누고, `order_by=F("total_amount").desc()`로 금액 내림차순 정렬 후 순위를 부여한다.
`select_related("customer")`로 N+1 쿼리를 방지한다.

고객별 상위 N건만 조회하려면 서브쿼리로 필터링한다.

```python
from django.db.models import Subquery, OuterRef

top_orders_subquery = (
    Order.objects
    .filter(
        customer=OuterRef("customer"),
        status__in=["confirmed", "shipped", "delivered"],
    )
    .order_by("-total_amount")
    .values("pk")[:3]
)

top3_orders_per_customer = (
    Order.objects
    .filter(pk__in=Subquery(top_orders_subquery))
    .select_related("customer")
    .order_by("customer__name", "-total_amount")
)
```

---

## 통합 서비스 함수

대시보드 쿼리를 서비스 레이어로 추출하면 뷰를 얇게 유지할 수 있다.
서비스 함수는 `<entity>_<action>` 네이밍을 따른다.

```python
# services/order_selectors.py
from datetime import timedelta
from decimal import Decimal

from django.db.models import (
    Avg, Case, Count, DecimalField, DurationField, Exists,
    ExpressionWrapper, F, FloatField, Max, OuterRef, Q,
    Subquery, Sum, Value, When, Window,
)
from django.db.models.functions import (
    Cast, Coalesce, DenseRank, Lag, Now, Rank, RowNumber, TruncMonth,
)
from django.utils import timezone

from orders.models import Customer, Order


def order_monthly_revenue_get() -> list[dict]:
    """월별 매출 집계 + 전월 대비 증감률."""
    return list(
        Order.objects
        .exclude(status="cancelled")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"))
        .order_by("month")
        .annotate(
            prev_month_revenue=Window(
                expression=Lag("revenue", offset=1, default=0),
                order_by=F("month").asc(),
            ),
            growth_rate=Case(
                When(
                    prev_month_revenue__gt=0,
                    then=(
                        Cast(
                            F("revenue") - F("prev_month_revenue"),
                            FloatField(),
                        )
                        / Cast(F("prev_month_revenue"), FloatField())
                        * Value(100.0)
                    ),
                ),
                default=Value(None),
                output_field=FloatField(),
            ),
        )
    )


def order_tier_stats_get() -> list[dict]:
    """고객 등급별 주문 건수와 평균 금액."""
    return list(
        Customer.objects
        .values("tier")
        .annotate(
            total_orders=Count("order"),
            confirmed_orders=Count(
                "order", filter=Q(order__status="confirmed")
            ),
            shipped_orders=Count(
                "order", filter=Q(order__status="shipped")
            ),
            delivered_orders=Count(
                "order", filter=Q(order__status="delivered")
            ),
            cancelled_orders=Count(
                "order", filter=Q(order__status="cancelled")
            ),
            avg_order_amount=Coalesce(
                Avg("order__total_amount"),
                Decimal("0"),
                output_field=DecimalField(),
            ),
            total_revenue=Coalesce(
                Sum(
                    "order__total_amount",
                    filter=~Q(order__status="cancelled"),
                ),
                Decimal("0"),
                output_field=DecimalField(),
            ),
        )
        .order_by("tier")
    )


def customer_inactive_list(*, days: int = 90):
    """최근 N일 주문 없는 고객 목록."""
    cutoff = timezone.now() - timedelta(days=days)

    recent_orders = Order.objects.filter(
        customer=OuterRef("pk"),
        created_at__gte=cutoff,
    )

    last_order_date = (
        Order.objects
        .filter(customer=OuterRef("pk"))
        .values("customer")
        .annotate(last_date=Max("created_at"))
        .values("last_date")[:1]
    )

    return (
        Customer.objects
        .filter(~Exists(recent_orders))
        .annotate(
            last_order_date=Subquery(last_order_date),
            days_since_last_order=ExpressionWrapper(
                Now() - Coalesce(
                    Subquery(last_order_date), F("joined_at")
                ),
                output_field=DurationField(),
            ),
        )
        .order_by("tier", "name")
    )


def order_customer_rank_get():
    """고객별 주문 금액 순위."""
    return (
        Order.objects
        .exclude(status="cancelled")
        .select_related("customer")
        .annotate(
            customer_rank=Window(
                expression=DenseRank(),
                partition_by=[F("customer")],
                order_by=F("total_amount").desc(),
            ),
            customer_row_num=Window(
                expression=RowNumber(),
                partition_by=[F("customer")],
                order_by=F("total_amount").desc(),
            ),
        )
    )
```
