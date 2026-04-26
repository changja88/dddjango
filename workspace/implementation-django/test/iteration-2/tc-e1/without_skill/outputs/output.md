# 주문 통계 대시보드 QuerySet

## 공통 import

```python
from datetime import timedelta

from django.db.models import (
    Avg, Case, Count, DecimalField, F, Q, Sum, Value, When, Window,
)
from django.db.models.functions import (
    Coalesce, ExtractMonth, ExtractYear, Lag, Rank, TruncMonth,
)
from django.utils import timezone
```

---

## 1. 월별 매출 집계 + 전월 대비 증감률 (Window 함수)

```python
monthly_revenue = (
    Order.objects
    .exclude(status="cancelled")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(
        total_revenue=Sum("total_amount"),
        order_count=Count("id"),
    )
    .annotate(
        prev_month_revenue=Window(
            expression=Lag("total_revenue", offset=1),
            order_by=F("month").asc(),
        ),
    )
    .annotate(
        growth_rate=Case(
            When(
                prev_month_revenue__isnull=False,
                prev_month_revenue__gt=0,
                then=(
                    (F("total_revenue") - F("prev_month_revenue"))
                    * Value(100.0)
                    / F("prev_month_revenue")
                ),
            ),
            default=None,
            output_field=DecimalField(max_digits=7, decimal_places=2),
        ),
    )
    .order_by("month")
)
```

**결과 예시:**

| month      | total_revenue | order_count | prev_month_revenue | growth_rate |
|------------|--------------|-------------|--------------------|-------------|
| 2026-01-01 | 5,200,000    | 42          | None               | None        |
| 2026-02-01 | 6,100,000    | 51          | 5,200,000          | 17.31       |
| 2026-03-01 | 5,800,000    | 48          | 6,100,000          | -4.92       |

---

## 2. 고객 등급별 주문 건수와 평균 금액 (조건부 집계)

```python
tier_stats = (
    Customer.objects
    .values("tier")
    .annotate(
        customer_count=Count("id", distinct=True),
        total_orders=Count("order"),
        avg_order_amount=Avg("order__total_amount"),
        # 상태별 건수
        pending_count=Count("order", filter=Q(order__status="pending")),
        confirmed_count=Count("order", filter=Q(order__status="confirmed")),
        shipped_count=Count("order", filter=Q(order__status="shipped")),
        delivered_count=Count("order", filter=Q(order__status="delivered")),
        cancelled_count=Count("order", filter=Q(order__status="cancelled")),
        # 취소 제외 실매출 평균
        avg_active_amount=Avg(
            "order__total_amount",
            filter=~Q(order__status="cancelled"),
        ),
        total_revenue=Coalesce(
            Sum(
                "order__total_amount",
                filter=~Q(order__status="cancelled"),
            ),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    )
    .order_by("-total_revenue")
)
```

**결과 예시:**

| tier     | customer_count | total_orders | avg_order_amount | cancelled_count | total_revenue |
|----------|---------------|-------------|------------------|-----------------|---------------|
| platinum | 15            | 320         | 185,000          | 8               | 57,720,000    |
| gold     | 42            | 580         | 120,000          | 25              | 66,600,000    |
| silver   | 78            | 430         | 75,000           | 40              | 29,250,000    |
| basic    | 160           | 310         | 45,000           | 55              | 11,475,000    |

---

## 3. 최근 3개월 주문 없는 고객 목록 (Subquery / Exists)

```python
three_months_ago = timezone.now() - timedelta(days=90)

recent_order_exists = Order.objects.filter(
    customer=models.OuterRef("pk"),
    created_at__gte=three_months_ago,
)

inactive_customers = (
    Customer.objects
    .exclude(models.Exists(recent_order_exists))
    .annotate(
        last_order_date=models.Subquery(
            Order.objects
            .filter(customer=models.OuterRef("pk"))
            .order_by("-created_at")
            .values("created_at")[:1]
        ),
        total_order_count=Count("order"),
        total_spent=Coalesce(
            Sum(
                "order__total_amount",
                filter=~Q(order__status="cancelled"),
            ),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    )
    .order_by("last_order_date")
)
```

**결과 예시:**

| name   | tier   | last_order_date     | total_order_count | total_spent |
|--------|--------|---------------------|-------------------|-------------|
| 김철수 | gold   | 2025-11-15 09:30:00 | 28                | 3,360,000   |
| 이영희 | silver | 2025-12-02 14:20:00 | 12                | 900,000     |
| 박민수 | basic  | 2026-01-03 11:00:00 | 5                 | 225,000     |

> `Exists`는 `Subquery`보다 효율적이다. 서브쿼리가 행의 존재 여부만 확인하면 되므로 매칭 행을 찾는 즉시 평가를 중단한다. 반면 `Subquery`로 `Count`를 구한 뒤 `0`과 비교하면 모든 행을 스캔해야 한다.

---

## 4. 고객별 주문 순위 (Window Rank)

```python
customer_order_ranking = (
    Order.objects
    .exclude(status="cancelled")
    .values(
        "customer__id",
        "customer__name",
        "customer__tier",
    )
    .annotate(
        order_count=Count("id"),
        total_spent=Sum("total_amount"),
        avg_amount=Avg("total_amount"),
    )
    .annotate(
        # 총 지출 기준 순위
        rank_by_spent=Window(
            expression=Rank(),
            order_by=F("total_spent").desc(),
        ),
        # 등급 내 순위
        rank_in_tier=Window(
            expression=Rank(),
            partition_by=[F("customer__tier")],
            order_by=F("total_spent").desc(),
        ),
    )
    .order_by("rank_by_spent")
)
```

**결과 예시:**

| customer__name | customer__tier | order_count | total_spent | rank_by_spent | rank_in_tier |
|----------------|---------------|-------------|-------------|---------------|--------------|
| 정우성         | platinum       | 45          | 8,325,000   | 1             | 1            |
| 한지민         | platinum       | 38          | 7,030,000   | 2             | 2            |
| 손예진         | gold           | 52          | 6,240,000   | 3             | 1            |
| 공유           | gold           | 41          | 4,920,000   | 4             | 2            |

---

## 참고: SQL 생성 확인

각 QuerySet이 생성하는 SQL을 확인하려면 `.query` 속성을 사용한다.

```python
print(monthly_revenue.query)
print(customer_order_ranking.query)
```
