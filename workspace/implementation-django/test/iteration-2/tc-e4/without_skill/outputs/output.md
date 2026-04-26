# Raw SQL to Django ORM Conversion

## Query 1: Window Functions (FIRST_VALUE / LAST_VALUE)

**Original SQL:**
```sql
SELECT c.name,
       FIRST_VALUE(o.total_amount) OVER (PARTITION BY c.id ORDER BY o.created_at) as first_order,
       LAST_VALUE(o.total_amount) OVER (PARTITION BY c.id ORDER BY o.created_at
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_order
FROM customers_customer c
JOIN orders_order o ON c.id = o.customer_id
```

**Django ORM:**
```python
from django.db.models import F, Window
from django.db.models.functions import FirstValue, LastValue

result = Order.objects.annotate(
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
).values("customer_name", "first_order", "last_order")
```

> **Note:** `RowRange(start=None, end=None)` corresponds to `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`. Import it from `django.db.models`:
> ```python
> from django.db.models import RowRange
> ```
> Without this frame specification, `LAST_VALUE` would only consider rows up to the current row (the default frame), which would not return the true last value in each partition.

---

## Query 2: GROUP BY with Window Function for Percentage

**Original SQL:**
```sql
SELECT status,
       SUM(total_amount) as status_total,
       SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER () as percentage
FROM orders_order
GROUP BY status
```

**Django ORM:**
```python
from django.db.models import F, Sum, Value, Window
from django.db.models.functions import Cast
from django.db.models import FloatField

result = (
    Order.objects.values("status")
    .annotate(status_total=Sum("total_amount"))
    .annotate(
        percentage=F("status_total")
        * Value(100.0)
        / Window(expression=Sum("status_total"))
    )
)
```

> **Explanation:**
> - `.values("status").annotate(status_total=Sum("total_amount"))` produces the `GROUP BY status` with `SUM(total_amount)`.
> - The second `.annotate()` uses `Window(expression=Sum("status_total"))` with no `partition_by`, which maps to `SUM(SUM(total_amount)) OVER ()` -- i.e., the grand total across all groups.
> - The arithmetic `F("status_total") * 100.0 / Window(...)` computes the percentage.

---

## Query 3: COALESCE, CAST, CONCAT

**Original SQL:**
```sql
SELECT
    COALESCE(nickname, name, 'Unknown') as display_name,
    CAST(total_amount AS INTEGER) as rounded_amount,
    CONCAT(name, ' (', tier, ')') as label
FROM customers_customer
```

**Django ORM:**
```python
from django.db.models import Value, IntegerField
from django.db.models.functions import Coalesce, Cast, Concat

result = Customer.objects.annotate(
    display_name=Coalesce("nickname", "name", Value("Unknown")),
    rounded_amount=Cast("total_amount", output_field=IntegerField()),
    label=Concat("name", Value(" ("), "tier", Value(")")),
).values("display_name", "rounded_amount", "label")
```

> **Explanation:**
> - `Coalesce` accepts field names and `Value()` for literals. It returns the first non-null argument.
> - `Cast` converts `total_amount` to an integer, truncating any decimal portion.
> - `Concat` joins multiple expressions. String literals must be wrapped in `Value()`.

---

## Required Imports (Combined)

```python
from django.db.models import (
    F, Sum, Value, Window, RowRange,
    FloatField, IntegerField,
)
from django.db.models.functions import (
    Cast, Coalesce, Concat, FirstValue, LastValue,
)
```
