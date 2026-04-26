# Raw SQL to Django ORM Conversion

## Query 1: Customer First/Last Order Amount (Window Functions)

### Raw SQL

```sql
SELECT c.name,
       FIRST_VALUE(o.total_amount) OVER (PARTITION BY c.id ORDER BY o.created_at) as first_order,
       LAST_VALUE(o.total_amount) OVER (PARTITION BY c.id ORDER BY o.created_at
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_order
FROM customers_customer c
JOIN orders_order o ON c.id = o.customer_id
```

### Django ORM

```python
from django.db.models import F, Window
from django.db.models.expressions import RowRange
from django.db.models.functions import FirstValue, LastValue

queryset = Order.objects.select_related("customer").annotate(
    customer_name=F("customer__name"),
    first_order=Window(
        expression=FirstValue("total_amount"),
        partition_by=[F("customer_id")],
        order_by=F("created_at").asc(),
    ),
    last_order=Window(
        expression=LastValue("total_amount"),
        partition_by=[F("customer_id")],
        order_by=F("created_at").asc(),
        frame=RowRange(start=None, end=None),
    ),
)
```

`FIRST_VALUE`는 기본 프레임(`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`)으로도 항상 파티션의 첫 행 값을 반환하므로 별도의 frame 지정이 필요 없다. 반면 `LAST_VALUE`는 기본 프레임에서는 현재 행의 값을 반환하므로, 원본 SQL과 동일하게 `RowRange(start=None, end=None)` (`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`)을 명시해야 파티션 전체의 마지막 값을 얻는다.

---

## Query 2: Order Amount Percentage by Status (Window + Aggregate)

### Raw SQL

```sql
SELECT status,
       SUM(total_amount) as status_total,
       SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER () as percentage
FROM orders_order
GROUP BY status
```

### Django ORM

```python
from django.db.models import F, Sum, Value, Window
from django.db.models.functions import Cast
from django.db.models import FloatField

queryset = (
    Order.objects
    .values("status")
    .annotate(status_total=Sum("total_amount"))
    .annotate(
        percentage=Cast(F("status_total"), FloatField())
        * Value(100.0)
        / Window(expression=Sum("status_total")),
    )
)
```

`SUM(SUM(total_amount)) OVER ()`는 그룹별 합계의 전체 합계이다. Django ORM에서는 먼저 `.values("status").annotate(status_total=Sum("total_amount"))`로 그룹별 집계를 수행한 뒤, 두 번째 `.annotate()`에서 `Window(expression=Sum("status_total"))`로 전체 합계를 구한다. `partition_by`와 `order_by`를 생략하면 `OVER ()` (전체 윈도우)가 된다.

---

## Query 3: NULL Handling + Type Casting (Database Functions)

### Raw SQL

```sql
SELECT
    COALESCE(nickname, name, 'Unknown') as display_name,
    CAST(total_amount AS INTEGER) as rounded_amount,
    CONCAT(name, ' (', tier, ')') as label
FROM customers_customer
```

### Django ORM

```python
from django.db.models import Value, IntegerField
from django.db.models.functions import Cast, Coalesce, Concat

queryset = Customer.objects.annotate(
    display_name=Coalesce("nickname", "name", Value("Unknown")),
    rounded_amount=Cast("total_amount", IntegerField()),
    label=Concat("name", Value(" ("), "tier", Value(")")),
)
```

`Coalesce`는 왼쪽부터 평가하여 첫 번째 non-NULL 값을 반환한다. 마지막 인자로 `Value("Unknown")`을 넣으면 모든 필드가 NULL일 때의 폴백이 된다. `Cast`의 두 번째 인자는 Django `Field` 인스턴스이며, `IntegerField()`는 SQL의 `CAST(... AS INTEGER)`로 변환된다. `Concat`에서 리터럴 문자열은 반드시 `Value()`로 감싸야 한다.
