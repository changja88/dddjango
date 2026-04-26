# Django ORM 리뷰: `get_dashboard_stats()`

## 총평

이 함수는 네 가지 통계 쿼리를 모두 `connection.cursor()`를 사용한 Raw SQL로 작성하고 있다. 네 쿼리 모두 Django ORM의 표준 기능(`annotate`, `aggregate`, `values`, `Exists`, `TruncMonth` 등)으로 완전히 대체할 수 있으며, Raw SQL을 사용할 정당한 이유가 없다.

Raw SQL은 ORM으로 표현할 수 없는 DB 고유 기능이 필요할 때만 사용해야 한다. 이 코드에서 수행하는 `GROUP BY`, `HAVING`, `NOT IN` 서브쿼리, `DATE_TRUNC` 등은 모두 Django ORM이 기본으로 지원하는 연산이다.

---

## 리뷰 결과

### 1. Raw SQL 대신 ORM 사용 필요 -- 전체 함수

```
[QuerySet/Manager 패턴] -- Django ORM은 GROUP BY, 집계, 서브쿼리, 날짜 절삭을 모두 지원한다.
connection.cursor()로 직접 SQL을 실행하면 ORM이 제공하는 타입 안전성, DB 백엔드 이식성,
QuerySet 체이닝, 그리고 모델 필드 매핑을 모두 포기하게 된다.
ORM으로 표현 가능한 쿼리에 Raw SQL을 사용하는 것은 Django의 "Less Code"와
"DRY" 설계 철학에 반한다.
```

### 2. 상태별 주문 수 -- `values()` + `annotate()` 대체 가능

```
[조건부 집계 / annotate] -- 상태별 COUNT는 values("status").annotate(count=Count("id"))로
표현할 수 있다. 또는 단일 aggregate()에서 filter=Q()를 사용하여 상태별 조건부 집계로
한 번에 가져올 수도 있다. advanced-orm.md의 "조건부 집계 (filter=Q())" 패턴이
정확히 이 유스케이스에 해당한다.
```

**ORM 대체:**

```python
from django.db.models import Count

# 방법 1: values + annotate
status_counts = dict(
    Order.objects
    .values_list("status")
    .annotate(count=Count("id"))
    .values_list("status", "count")
)
```

### 3. 월별 매출 -- `TruncMonth` + `annotate()` 대체 가능

```
[고급 ORM / TruncMonth] -- DATE_TRUNC('month', created_at)는 Django의
TruncMonth("created_at")와 정확히 동일한 SQL을 생성한다.
advanced-orm.md의 Extract/Trunc 섹션에서 월별 집계의 표준 패턴을 제시하고 있다.
ORM을 사용하면 DB 백엔드에 관계없이 동일한 코드가 동작한다
(PostgreSQL의 DATE_TRUNC는 MySQL에서는 동작하지 않는다).
```

**ORM 대체:**

```python
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

monthly_revenue = (
    Order.objects
    .exclude(status="cancelled")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(total_revenue=Sum("total_amount"))
    .order_by("month")
)
```

### 4. VIP 고객 -- `annotate()` + `filter()` 대체 가능

```
[QuerySet 집계 / annotate + filter] -- JOIN + GROUP BY + HAVING은
annotate(total=Sum("order__total_amount")).filter(total__gte=1000000)로
표현할 수 있다. queryset-manager.md의 annotate() 섹션에서 이 패턴을 설명하고 있다.
ORM을 사용하면 Customer 모델 인스턴스를 직접 반환받을 수 있어
후속 로직에서 바로 사용 가능하다.
```

**ORM 대체:**

```python
from django.db.models import Sum

vip_customers = (
    Customer.objects
    .annotate(
        total=Sum(
            "order__total_amount",
            filter=Q(order__status__ne="cancelled"),
        )
    )
    .filter(total__gte=1000000)
    .order_by("-total")
)
```

더 정확하게는 `exclude`를 활용하거나 `filter=Q()` 파라미터를 사용한다:

```python
from django.db.models import Sum, Q

vip_customers = (
    Customer.objects
    .annotate(
        total=Sum(
            "order__total_amount",
            filter=Q(~Q(order__status="cancelled")),
        )
    )
    .filter(total__gte=1000000)
    .order_by("-total")
    .values("id", "name", "total")
)
```

### 5. 비활성 고객 -- `~Exists()` 대체 가능

```
[고급 ORM / Exists] -- NOT IN 서브쿼리는 Django ORM의 ~Exists(OuterRef)로 표현해야 한다.
advanced-orm.md의 Exists 섹션에서 명시적으로 설명하는 바와 같이,
Exists는 첫 번째 일치 행을 찾으면 즉시 True를 반환(short-circuit)하므로
NOT IN보다 성능이 우수하다. 또한 NOT IN은 NULL 값이 포함된 경우
예상치 못한 결과를 반환할 수 있어 NOT EXISTS가 더 안전하다.
```

**ORM 대체:**

```python
from datetime import timedelta
from django.db.models import Exists, OuterRef
from django.utils import timezone

recent_orders = Order.objects.filter(
    customer=OuterRef("pk"),
    created_at__gte=timezone.now() - timedelta(days=180),
)

inactive_customers = Customer.objects.filter(
    ~Exists(recent_orders)
).values("id", "name")
```

### 6. DB 이식성 상실

```
[보안/이식성] -- Raw SQL에서 PostgreSQL 전용 문법을 사용하고 있다.
DATE_TRUNC('month', ...), NOW(), INTERVAL '6 months' 등은 PostgreSQL에서만 동작한다.
Django ORM의 TruncMonth, timezone.now(), timedelta를 사용하면
SQLite, MySQL, PostgreSQL 모두에서 동일하게 동작한다.
이는 테스트 환경에서 SQLite를 사용하는 경우 특히 문제가 된다.
```

### 7. SQL Injection 리스크 부재 확인

```
[보안] -- 현재 코드에서는 사용자 입력이 SQL에 직접 삽입되지 않으므로
SQL Injection 취약점은 없다. 그러나 향후 파라미터가 추가될 경우(날짜 범위 필터 등)
connection.cursor() 기반 코드에서는 문자열 보간 실수가 발생하기 쉽다.
ORM을 사용하면 파라미터화 쿼리가 자동으로 적용되어 이 위험이 원천 차단된다.
```

---

## 리뷰 체크리스트 결과

| 항목 | 결과 |
|------|------|
| Project structure | N/A (단일 함수) |
| Model field ordering | N/A |
| Boolean flag proliferation | N/A |
| Missing select_related/prefetch_related | N/A (집계 쿼리) |
| N+1 queries | N/A |
| save() without update_fields | N/A |
| Signals for same-app logic | N/A |
| fields = "\_\_all\_\_" | N/A |
| Multi-table inheritance | N/A |
| **Raw SQL with string interpolation** | **주의 -- Raw SQL 자체가 불필요. 현재 인젝션 위험은 없으나 ORM 전환 권장** |
| Missing CSRF protection | N/A |
| CBV with 4+ Mixins | N/A |
| Fat views with business logic | N/A (유틸리티 함수) |
| Missing assertNumQueries | 해당 -- 이 함수에 대한 테스트에서 쿼리 수 검증 권장 |
| Django 5.x features not used | 해당 없음 (이 코드에 적용 가능한 5.x 기능 없음) |

---

## 전체 개선 코드

```python
from datetime import timedelta

from django.db.models import Count, Exists, OuterRef, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone


def get_dashboard_stats():
    # 1. 상태별 주문 수
    status_counts = dict(
        Order.objects
        .values_list("status")
        .annotate(count=Count("id"))
        .values_list("status", "count")
    )

    # 2. 월별 매출 (취소 주문 제외)
    monthly_revenue = list(
        Order.objects
        .exclude(status="cancelled")
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total_revenue=Sum("total_amount"))
        .order_by("month")
    )

    # 3. VIP 고객 (총 주문 100만원 이상, 취소 제외)
    vip_customers = list(
        Customer.objects
        .annotate(
            total=Sum(
                "order__total_amount",
                filter=~Q(order__status="cancelled"),
            )
        )
        .filter(total__gte=1000000)
        .order_by("-total")
        .values_list("id", "name", "total")
    )

    # 4. 비활성 고객 (6개월 내 주문 없음) -- ~Exists로 NOT EXISTS 사용
    recent_orders = Order.objects.filter(
        customer=OuterRef("pk"),
        created_at__gte=timezone.now() - timedelta(days=180),
    )
    inactive_customers = list(
        Customer.objects
        .filter(~Exists(recent_orders))
        .values_list("id", "name")
    )

    return {
        "status_counts": status_counts,
        "monthly_revenue": monthly_revenue,
        "vip_customers": vip_customers,
        "inactive_customers": inactive_customers,
    }
```

**개선 요약:**
- 4개의 `connection.cursor()` Raw SQL을 모두 Django ORM으로 전환
- `TruncMonth`으로 DB 독립적인 월별 집계 구현
- `~Exists(OuterRef)`로 NOT IN 서브쿼리를 NOT EXISTS로 개선 (성능 + NULL 안전성)
- `filter=~Q()` 파라미터로 조건부 집계 구현
- DB 백엔드 이식성 확보 (PostgreSQL 전용 문법 제거)
- SQL Injection 리스크 원천 차단
