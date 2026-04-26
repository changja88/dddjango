# Django 코드 리뷰: `get_dashboard_stats()`

## 종합 판정: ORM 미활용 — 전면 리팩터링 권장

이 함수는 4개의 Raw SQL 쿼리를 `connection.cursor()`로 직접 실행하고 있다. Django ORM을 전혀 사용하지 않고 있으며, 이로 인해 여러 문제가 발생한다.

---

## 1. Raw SQL 직접 사용의 문제점

### 1-1. DB 벤더 종속성
```python
# 현재 코드 — PostgreSQL 전용 함수 사용
cursor.execute('''
    SELECT DATE_TRUNC('month', created_at) as month, SUM(total_amount)
    ...
''')
```
- `DATE_TRUNC`는 PostgreSQL 전용 함수다.
- `NOW() - INTERVAL '6 months'`도 PostgreSQL 방언이다.
- SQLite, MySQL 등 다른 DB로 전환하면 즉시 깨진다.
- 테스트 환경에서 SQLite를 사용하는 경우 테스트 자체가 불가능하다.

### 1-2. SQL Injection 위험
현재 코드에는 사용자 입력이 없어 직접적인 위험은 없지만, 향후 필터 조건(날짜 범위, 상태 등)이 추가될 때 Raw SQL 패턴을 그대로 유지하면 파라미터 바인딩을 누락할 가능성이 높아진다.

### 1-3. 모델 변경 시 동기화 실패
- 테이블명(`orders_order`, `customers_customer`)과 컬럼명(`total_amount`, `created_at`)을 문자열로 하드코딩하고 있다.
- 모델 필드명이 변경되면 Django migration은 DB 스키마를 업데이트하지만, 이 Raw SQL은 자동으로 반영되지 않는다.
- 런타임에서야 오류가 발견된다.

### 1-4. 쿼리셋 체이닝 및 재사용 불가
- ORM 쿼리셋은 `.filter()` 등으로 조건을 추가하며 재사용할 수 있지만, Raw SQL 문자열은 그렇지 않다.
- `WHERE status != 'cancelled'` 조건이 3곳에서 반복되고 있다.

---

## 2. ORM 활용 리팩터링 제안

### 2-1. 주문 상태별 집계
```python
# Before (Raw SQL)
cursor.execute('SELECT status, COUNT(*) FROM orders_order GROUP BY status')

# After (ORM)
from django.db.models import Count

status_counts = dict(
    Order.objects.values_list('status').annotate(count=Count('id')).values_list('status', 'count')
)
```

### 2-2. 월별 매출 집계
```python
# Before (Raw SQL) — DATE_TRUNC는 PostgreSQL 전용
cursor.execute('''
    SELECT DATE_TRUNC('month', created_at) as month, SUM(total_amount)
    FROM orders_order WHERE status != 'cancelled'
    GROUP BY month ORDER BY month
''')

# After (ORM) — DB 벤더 무관
from django.db.models import Sum
from django.db.models.functions import TruncMonth

monthly_revenue = (
    Order.objects
    .exclude(status='cancelled')
    .annotate(month=TruncMonth('created_at'))
    .values('month')
    .annotate(total=Sum('total_amount'))
    .order_by('month')
)
```
- `TruncMonth`은 Django가 DB 벤더에 맞는 SQL을 자동 생성한다.

### 2-3. VIP 고객 조회
```python
# Before (Raw SQL)
cursor.execute('''
    SELECT c.id, c.name, SUM(o.total_amount) as total
    FROM customers_customer c JOIN orders_order o ON c.id = o.customer_id
    WHERE o.status != 'cancelled'
    GROUP BY c.id, c.name HAVING SUM(o.total_amount) >= 1000000
    ORDER BY total DESC
''')

# After (ORM)
from django.db.models import Sum

vip_customers = (
    Customer.objects
    .filter(order__isnull=False)
    .exclude(order__status='cancelled')
    .annotate(total=Sum('order__total_amount'))
    .filter(total__gte=1000000)
    .order_by('-total')
    .values('id', 'name', 'total')
)
```
- JOIN 관계를 Django가 자동으로 처리한다.
- `HAVING` 절은 `annotate()` 후 `.filter()`로 자연스럽게 표현된다.

### 2-4. 비활성 고객 조회
```python
# Before (Raw SQL) — NOW(), INTERVAL 은 PostgreSQL 방언
cursor.execute('''
    SELECT id, name FROM customers_customer
    WHERE id NOT IN (
        SELECT DISTINCT customer_id FROM orders_order
        WHERE created_at > NOW() - INTERVAL '6 months'
    )
''')

# After (ORM)
from django.utils import timezone
from datetime import timedelta

six_months_ago = timezone.now() - timedelta(days=180)

inactive_customers = (
    Customer.objects
    .exclude(
        order__created_at__gt=six_months_ago
    )
    .values('id', 'name')
)
```
- `timezone.now()`를 사용하여 Django의 시간대 설정(`USE_TZ`)을 올바르게 반영한다.
- 서브쿼리 대신 역방향 관계 lookup으로 간결하게 표현된다.

---

## 3. 추가 구조적 개선 사항

### 3-1. 반복 조건 상수화
`status != 'cancelled'` 조건이 3곳에서 반복된다. 모델 매니저나 쿼리셋 메서드로 추출해야 한다.

```python
class OrderQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status='cancelled')

class Order(models.Model):
    objects = OrderQuerySet.as_manager()
```
이후 `Order.objects.active()`로 일관되게 사용할 수 있다.

### 3-2. 매직 넘버 제거
`1000000`(VIP 기준 금액), `6 months`(비활성 기준 기간)가 하드코딩되어 있다. 설정 값이나 상수로 분리해야 한다.

```python
# constants.py 또는 settings.py
VIP_THRESHOLD_AMOUNT = 1_000_000
INACTIVE_PERIOD_DAYS = 180
```

### 3-3. 반환 타입 명확화
딕셔너리 대신 dataclass나 TypedDict를 사용하면 호출측에서 타입 안전성을 확보할 수 있다.

```python
from typing import TypedDict

class DashboardStats(TypedDict):
    status_counts: dict[str, int]
    monthly_revenue: QuerySet
    vip_customers: QuerySet
    inactive_customers: QuerySet
```

---

## 4. 요약

| 항목 | 현재 | 권장 |
|------|------|------|
| 쿼리 방식 | `connection.cursor()` Raw SQL | ORM `QuerySet` API |
| DB 호환성 | PostgreSQL 전용 | DB 벤더 무관 |
| 모델 변경 추적 | 수동 (문자열 하드코딩) | 자동 (필드 참조) |
| 테스트 용이성 | SQLite 사용 불가 | SQLite/모든 DB 가능 |
| 조건 재사용 | 문자열 복붙 | 커스텀 매니저/체이닝 |
| SQL Injection 방어 | 현재는 안전하나 확장 시 위험 | ORM이 자동 파라미터화 |

4개 쿼리 모두 Django ORM의 `annotate()`, `values()`, `exclude()`, `TruncMonth` 등으로 완전히 대체 가능하다. Raw SQL을 사용할 정당한 이유가 없으므로 전면 리팩터링을 권장한다.
