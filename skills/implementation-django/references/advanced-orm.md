# 고급 ORM 표현식 레퍼런스

Django ORM의 고급 쿼리 표현식에 대한 상세 규칙과 예시.

---

## 1. Case/When 조건부 표현식

**Source: Django Conditional Expressions 공식 문서**

### 다중 조건 annotation

```python
from django.db.models import Case, When, Value, IntegerField, CharField

# 여러 조건을 순서대로 평가하여 값 할당
queryset = Order.objects.annotate(
    priority=Case(
        When(status="urgent", total__gte=100000, then=Value(1)),
        When(status="urgent", then=Value(2)),
        When(status="normal", total__gte=100000, then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
).order_by("priority")

# 문자열 매핑
queryset = Product.objects.annotate(
    category_label=Case(
        When(category="A", then=Value("프리미엄")),
        When(category="B", then=Value("일반")),
        default=Value("기타"),
        output_field=CharField(),
    )
)
```

### Q 객체 조합

```python
from django.db.models import Q

queryset = User.objects.annotate(
    tier=Case(
        When(Q(is_staff=True) | Q(membership="premium"), then=Value("VIP")),
        When(
            Q(date_joined__year__gte=2024) & Q(order_count__gte=10),
            then=Value("우수"),
        ),
        default=Value("일반"),
        output_field=CharField(),
    )
)
```

### 조건부 bulk update

```python
# Case/When으로 한 번의 쿼리로 조건별 일괄 업데이트
Product.objects.update(
    discount=Case(
        When(stock__lte=10, then=Value(0.3)),
        When(stock__lte=50, then=Value(0.1)),
        default=Value(0.0),
    )
)
```

### 조건부 집계 (filter=Q())

```python
from django.db.models import Count, Sum, Avg, Q

# filter= 파라미터로 조건부 집계 (Case/When보다 권장)
stats = Order.objects.aggregate(
    total_orders=Count("id"),
    urgent_orders=Count("id", filter=Q(status="urgent")),
    completed_revenue=Sum("total", filter=Q(status="completed")),
    avg_premium_total=Avg("total", filter=Q(customer__membership="premium")),
)

# 그룹별 조건부 집계
monthly = (
    Order.objects
    .values("created_at__month")
    .annotate(
        total=Count("id"),
        cancelled=Count("id", filter=Q(status="cancelled")),
        cancel_rate=Cast(
            Count("id", filter=Q(status="cancelled")),
            FloatField(),
        ) / Cast(Count("id"), FloatField()),
    )
)
```

---

## 2. Window 함수

**Source: Django Query Expressions 공식 문서**

### 기본 Window 함수 (Rank, DenseRank, RowNumber)

```python
from django.db.models import F, Window
from django.db.models.functions import Rank, DenseRank, RowNumber

# 부서별 급여 순위
queryset = Employee.objects.annotate(
    salary_rank=Window(
        expression=Rank(),
        partition_by=[F("department")],
        order_by=F("salary").desc(),
    ),
    salary_dense_rank=Window(
        expression=DenseRank(),
        partition_by=[F("department")],
        order_by=F("salary").desc(),
    ),
    row_num=Window(
        expression=RowNumber(),
        partition_by=[F("department")],
        order_by=F("salary").desc(),
    ),
)
```

### Lag, Lead

```python
from django.db.models.functions import Lag, Lead

# 이전/다음 행의 값 참조
queryset = SalesRecord.objects.annotate(
    prev_month_revenue=Window(
        expression=Lag("revenue", offset=1, default=0),
        partition_by=[F("region")],
        order_by=F("month").asc(),
    ),
    next_month_revenue=Window(
        expression=Lead("revenue", offset=1, default=0),
        partition_by=[F("region")],
        order_by=F("month").asc(),
    ),
    mom_change=F("revenue") - Window(
        expression=Lag("revenue", offset=1, default=0),
        partition_by=[F("region")],
        order_by=F("month").asc(),
    ),
)
```

### Ntile

```python
from django.db.models.functions import Ntile

# N등분 그룹 분류
queryset = Customer.objects.annotate(
    spending_quartile=Window(
        expression=Ntile(num_buckets=4),
        order_by=F("total_spent").desc(),
    )
)
```

### RowRange / ValueRange 프레임

```python
from django.db.models import Avg, Sum, Window
from django.db.models.expressions import RowRange, ValueRange

# 현재 행 기준 앞뒤 2행 이동 평균
queryset = StockPrice.objects.annotate(
    moving_avg=Window(
        expression=Avg("close_price"),
        order_by=F("date").asc(),
        frame=RowRange(start=-2, end=0),
    ),
)

# 누적 합계 (처음부터 현재까지)
queryset = SalesRecord.objects.annotate(
    cumulative_revenue=Window(
        expression=Sum("revenue"),
        partition_by=[F("region")],
        order_by=F("month").asc(),
        frame=RowRange(start=None, end=0),  # None = UNBOUNDED PRECEDING
    ),
)

# ValueRange: 값 기반 프레임 (날짜 범위 등)
queryset = SalesRecord.objects.annotate(
    rolling_30day_sum=Window(
        expression=Sum("revenue"),
        order_by=F("date").asc(),
        frame=ValueRange(start=-30, end=0),
    ),
)
```

---

## 3. Subquery와 OuterRef

**Source: Django Query Expressions 공식 문서**

### 상관 서브쿼리 기본

```python
from django.db.models import Subquery, OuterRef

# 각 카테고리의 최신 상품명을 annotation
newest_product = (
    Product.objects
    .filter(category=OuterRef("pk"))
    .order_by("-created_at")
    .values("name")[:1]  # 반드시 .values()[:1]로 단일 값 반환
)

queryset = Category.objects.annotate(
    newest_product_name=Subquery(newest_product)
)
```

### .values()[:1] 규칙

```python
# Subquery는 반드시 단일 행, 단일 컬럼을 반환해야 한다
# .values("컬럼명")[:1] 패턴을 항상 적용

# 올바른 패턴
subq = Model.objects.filter(...).values("field")[:1]

# 잘못된 패턴 (에러 발생)
# subq = Model.objects.filter(...)[:1]           # values 누락
# subq = Model.objects.filter(...).values("field")  # [:1] 누락
```

### 집계 서브쿼리

```python
from django.db.models import Subquery, OuterRef, Count, Avg
from django.db.models.functions import Coalesce

# 서브쿼리에서 집계 함수 사용
order_count = (
    Order.objects
    .filter(customer=OuterRef("pk"))
    .values("customer")  # GROUP BY를 위해 필요
    .annotate(cnt=Count("id"))
    .values("cnt")[:1]
)

avg_total = (
    Order.objects
    .filter(customer=OuterRef("pk"))
    .values("customer")
    .annotate(avg=Avg("total"))
    .values("avg")[:1]
)

queryset = Customer.objects.annotate(
    order_count=Coalesce(Subquery(order_count), 0),
    avg_order_total=Coalesce(Subquery(avg_total), 0),
)
```

### 중첩 OuterRef

```python
# 2단계 바깥 쿼리 참조
inner_subquery = (
    OrderItem.objects
    .filter(
        order=OuterRef("pk"),                    # Order 참조
        product__category=OuterRef(OuterRef("pk")),  # Category 참조 (2단계)
    )
    .values("order")
    .annotate(total=Sum("quantity"))
    .values("total")[:1]
)

order_subquery = (
    Order.objects
    .filter(customer__category=OuterRef("pk"))
    .annotate(item_total=Subquery(inner_subquery))
    .values("customer__category")
    .annotate(grand_total=Sum("item_total"))
    .values("grand_total")[:1]
)

queryset = Category.objects.annotate(
    grand_total=Subquery(order_subquery)
)
```

---

## 4. Exists() 표현식

**Source: Django Query Expressions 공식 문서**

### annotation으로 boolean 컬럼

```python
from django.db.models import Exists, OuterRef

# 각 고객에 대해 활성 주문이 있는지 boolean annotation
active_orders = Order.objects.filter(
    customer=OuterRef("pk"),
    status="active",
)

queryset = Customer.objects.annotate(
    has_active_order=Exists(active_orders)
)

# 결과 사용
for customer in queryset:
    if customer.has_active_order:
        print(f"{customer.name}: 활성 주문 있음")
```

### filter로 존재 확인

```python
# 최근 30일 내 주문이 있는 고객만 필터링
from datetime import timedelta
from django.utils import timezone

recent_orders = Order.objects.filter(
    customer=OuterRef("pk"),
    created_at__gte=timezone.now() - timedelta(days=30),
)

active_customers = Customer.objects.filter(Exists(recent_orders))
```

### ~ 부정 (NOT EXISTS)

```python
# 주문이 전혀 없는 고객
any_orders = Order.objects.filter(customer=OuterRef("pk"))

no_order_customers = Customer.objects.filter(~Exists(any_orders))

# 리뷰가 없는 상품
any_reviews = Review.objects.filter(product=OuterRef("pk"))
unreviewed_products = Product.objects.filter(~Exists(any_reviews))
```

### Subquery보다 Exists 선호 이유

```python
# 비권장: Subquery + Count로 존재 여부 확인
from django.db.models import Subquery, IntegerField
queryset = Customer.objects.annotate(
    order_count=Subquery(
        Order.objects.filter(customer=OuterRef("pk"))
        .values("customer")
        .annotate(c=Count("id"))
        .values("c")[:1],
        output_field=IntegerField(),
    )
).filter(order_count__gt=0)

# 권장: Exists (데이터베이스가 첫 번째 행을 찾으면 즉시 중단하므로 빠름)
queryset = Customer.objects.filter(
    Exists(Order.objects.filter(customer=OuterRef("pk")))
)
# EXISTS는 일치 행 발견 시 즉시 True 반환 (short-circuit)
# Subquery + Count는 모든 행을 세야 하므로 비효율적
```

---

## 5. 데이터베이스 함수

**Source: Django Database Functions 공식 문서**

### Coalesce

```python
from django.db.models.functions import Coalesce
from django.db.models import Value

# NULL을 기본값으로 대체
queryset = Product.objects.annotate(
    display_name=Coalesce("display_name", "name", Value("이름 없음")),
    effective_price=Coalesce("sale_price", "price"),
)
```

### Cast

```python
from django.db.models.functions import Cast
from django.db.models import FloatField, CharField, DateField

# 타입 변환
queryset = Order.objects.annotate(
    total_as_float=Cast("total", FloatField()),
    id_as_str=Cast("id", CharField()),
    str_date=Cast("date_string", DateField()),
)
```

### Concat

```python
from django.db.models.functions import Concat
from django.db.models import Value

queryset = User.objects.annotate(
    full_name=Concat("last_name", Value(" "), "first_name"),
    display=Concat("last_name", Value("("), "department__name", Value(")")),
)
```

### Lower / Upper / Length / Trim

```python
from django.db.models.functions import Lower, Upper, Length, LTrim, RTrim, Trim

queryset = Product.objects.annotate(
    name_lower=Lower("name"),
    name_upper=Upper("name"),
    name_length=Length("name"),
    name_trimmed=Trim("name"),
    name_ltrimmed=LTrim("name"),
    name_rtrimmed=RTrim("name"),
)

# 검색에 활용
queryset = Product.objects.filter(name_lower=Lower(Value("검색어")))
```

### Extract / Trunc / Now

```python
from django.db.models.functions import (
    Extract, ExtractYear, ExtractMonth, ExtractDay,
    ExtractHour, ExtractWeekDay,
    Trunc, TruncMonth, TruncDate, TruncHour,
    Now,
)

# 날짜/시간 부분 추출
queryset = Order.objects.annotate(
    order_year=ExtractYear("created_at"),
    order_month=ExtractMonth("created_at"),
    order_day=ExtractDay("created_at"),
    order_hour=ExtractHour("created_at"),
    weekday=ExtractWeekDay("created_at"),
)

# 날짜/시간 절삭 (그룹핑용)
monthly_stats = (
    Order.objects
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(
        total_revenue=Sum("total"),
        order_count=Count("id"),
    )
    .order_by("month")
)

# Now()
from datetime import timedelta
queryset = Order.objects.filter(
    created_at__gte=Now() - timedelta(days=7)
)

queryset = Subscription.objects.annotate(
    is_expired=Case(
        When(expires_at__lt=Now(), then=Value(True)),
        default=Value(False),
        output_field=BooleanField(),
    )
)
```

### Greatest / Least

```python
from django.db.models.functions import Greatest, Least

queryset = Product.objects.annotate(
    effective_price=Least("price", "sale_price"),
    max_dimension=Greatest("width", "height", "depth"),
)
```

### 커스텀 Func 서브클래스

```python
from django.db.models import Func, FloatField

# 데이터베이스 함수를 직접 래핑
class Log(Func):
    function = "LOG"
    output_field = FloatField()

class Power(Func):
    function = "POWER"
    output_field = FloatField()

class DateDiff(Func):
    """PostgreSQL age() 함수 래핑"""
    function = "AGE"
    template = "%(function)s(%(expressions)s)"

# 사용
queryset = Product.objects.annotate(
    log_price=Log("price"),
    price_squared=Power("price", Value(2)),
)

# 커스텀 template 활용
class ArrayLength(Func):
    function = "ARRAY_LENGTH"
    template = "%(function)s(%(expressions)s, 1)"

class JsonExtract(Func):
    """PostgreSQL JSON 추출"""
    template = "(%(expressions)s)::text"

    def __init__(self, expression, path, **extra):
        super().__init__(expression, Value(path), **extra)
```

---

## 6. 집합 연산 (union, intersection, difference)

**Source: Django QuerySet API 공식 문서**

### union(all=True)

```python
# 기본 union (중복 제거)
recent_orders = Order.objects.filter(created_at__year=2025)
large_orders = Order.objects.filter(total__gte=100000)

combined = recent_orders.union(large_orders)

# union all (중복 허용, 더 빠름)
combined_all = recent_orders.union(large_orders, all=True)

# 3개 이상 쿼리셋 union
qs1 = Order.objects.filter(status="pending")
qs2 = Order.objects.filter(status="processing")
qs3 = Order.objects.filter(status="shipped")

all_active = qs1.union(qs2, qs3)
```

### cross-model union

```python
# 서로 다른 모델의 쿼리셋도 union 가능 (컬럼 수와 타입이 일치해야 함)
from django.db.models import Value, CharField

customer_emails = (
    Customer.objects
    .values_list("email", "name")
    .annotate(source=Value("customer", output_field=CharField()))
)

supplier_emails = (
    Supplier.objects
    .values_list("email", "contact_name")
    .annotate(source=Value("supplier", output_field=CharField()))
)

all_contacts = customer_emails.union(supplier_emails)
```

### intersection / difference

```python
# intersection: 두 쿼리셋의 교집합
premium_customers = Customer.objects.filter(membership="premium")
active_customers = Customer.objects.filter(last_login__year=2025)

premium_and_active = premium_customers.intersection(active_customers)

# difference: 차집합
all_products = Product.objects.all()
sold_products = Product.objects.filter(
    pk__in=OrderItem.objects.values("product_id")
)

unsold_products = all_products.difference(sold_products)
```

### 제한 사항

```python
# 1. 집합 연산 후에는 filter(), exclude(), annotate() 불가
combined = qs1.union(qs2)
# combined.filter(...)  # 에러 발생

# 2. order_by()만 허용되며, 컬럼명으로만 가능 (annotation 이름 불가)
combined = qs1.union(qs2).order_by("created_at")

# 3. 집합 연산 전에 모든 필터링/annotation 완료해야 함
qs1 = Order.objects.filter(status="active").annotate(label=Value("A"))
qs2 = Order.objects.filter(status="closed").annotate(label=Value("B"))
combined = qs1.union(qs2).order_by("-created_at")

# 4. values() / values_list()는 union 전에 호출
result = (
    Order.objects.filter(status="a").values("id", "total")
    .union(
        Order.objects.filter(status="b").values("id", "total")
    )
)

# 5. slicing(LIMIT/OFFSET)은 union 결과에 적용 가능
paginated = qs1.union(qs2).order_by("id")[10:20]

# 6. count()는 union 결과에 사용 가능
total = qs1.union(qs2).count()
```
