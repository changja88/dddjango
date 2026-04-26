# PostgreSQL 특화 기능 레퍼런스

Django의 PostgreSQL 전용 필드, 검색, 집계, 인덱스, 제약 조건에 대한 상세 규칙과 예시.

---

## 1. JSONField 쿼리

**Source: Django JSONField 공식 문서**

### 키 / 인덱스 / 경로 조회

```python
from django.db.models import JSONField

class Product(models.Model):
    metadata = models.JSONField(default=dict)

# 최상위 키 조회
Product.objects.filter(metadata__brand="Samsung")

# 중첩 키 경로 조회 (__ 구분자)
Product.objects.filter(metadata__specs__weight__lt=500)

# 배열 인덱스 조회 (0-based)
Product.objects.filter(metadata__tags__0="electronics")

# 깊은 경로
Product.objects.filter(metadata__specs__display__resolution="4K")
```

### 포함 조회 (contains / contained_by)

```python
# contains: JSON 값이 주어진 구조를 포함하는지
Product.objects.filter(
    metadata__contains={"brand": "Samsung", "specs": {"color": "black"}}
)

# contained_by: JSON 값이 주어진 구조에 포함되는지
Product.objects.filter(
    metadata__contained_by={
        "brand": "Samsung",
        "category": "phone",
        "specs": {"color": "black", "weight": 200},
    }
)
```

### 키 존재 (has_key / has_keys / has_any_keys)

```python
# 단일 키 존재 확인
Product.objects.filter(metadata__has_key="warranty")

# 모든 키가 존재해야 함 (AND)
Product.objects.filter(metadata__has_keys=["brand", "warranty"])

# 키 중 하나라도 존재하면 됨 (OR)
Product.objects.filter(metadata__has_any_keys=["discount", "promotion"])
```

### KT() 표현식

```python
from django.db.models.fields.json import KT

# KT()로 JSON 키를 표현식으로 사용 (annotation, order_by 등에 활용)
queryset = Product.objects.annotate(
    brand=KT("metadata__brand"),
    weight=KT("metadata__specs__weight"),
).filter(
    brand="Samsung",
).order_by("weight")

# 집계에 활용
from django.db.models import Avg
from django.db.models.functions import Cast
from django.db.models import FloatField

Product.objects.annotate(
    weight_val=Cast(KT("metadata__specs__weight"), FloatField()),
).aggregate(avg_weight=Avg("weight_val"))
```

### None vs JSON null 구분

```python
# Python None (SQL NULL) - 필드 자체가 NULL
Product.objects.filter(metadata__isnull=True)

# JSON null - 필드에 JSON null 값이 저장됨
from django.db.models import Value
Product.objects.filter(metadata=Value("null"))

# 특정 키가 JSON null인 경우
Product.objects.filter(metadata__brand=None)  # JSON null

# 특정 키가 아예 없는 경우와 구분
Product.objects.exclude(metadata__has_key="brand")  # 키 자체가 없음
Product.objects.filter(metadata__brand=None)         # 키 존재, 값이 null
```

---

## 2. ArrayField

**Source: Django PostgreSQL Fields 공식 문서**

### 기본 정의 및 조회

```python
from django.contrib.postgres.fields import ArrayField
from django.db import models

class Post(models.Model):
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    scores = ArrayField(models.IntegerField(), size=10, default=list)
    matrix = ArrayField(
        ArrayField(models.IntegerField(), size=3),
        size=3,
    )  # 중첩 배열
```

### 포함 조회

```python
# contains: 배열이 주어진 값을 모두 포함하는지
Post.objects.filter(tags__contains=["django", "python"])

# contained_by: 배열이 주어진 값에 포함되는지
Post.objects.filter(tags__contained_by=["django", "python", "web", "api"])

# overlap: 하나라도 겹치는지
Post.objects.filter(tags__overlap=["django", "flask"])
```

### 길이 / 인덱스 / 슬라이스 조회

```python
# 길이 조회
Post.objects.filter(tags__len=3)
Post.objects.filter(tags__len__gte=2)

# 인덱스 조회 (0-based)
Post.objects.filter(tags__0="django")     # 첫 번째 요소
Post.objects.filter(scores__2__gte=90)    # 세 번째 요소가 90 이상

# 슬라이스 조회 (Python 슬라이싱 구문)
Post.objects.filter(tags__0_2=["django", "python"])  # 처음 2개 요소
```

### GinIndex 권장

```python
from django.contrib.postgres.indexes import GinIndex

class Post(models.Model):
    tags = ArrayField(models.CharField(max_length=50), default=list)

    class Meta:
        indexes = [
            # ArrayField에는 GIN 인덱스 필수
            GinIndex(fields=["tags"], name="idx_post_tags_gin"),
        ]

# GIN 인덱스가 있어야 contains, contained_by, overlap 조회가 빠름
# 인덱스 없이 ArrayField 조회하면 Full Table Scan 발생
```

---

## 3. Full-Text Search

**Source: Django PostgreSQL Search 공식 문서**

### SearchVector, SearchQuery, SearchRank

```python
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, SearchHeadline,
)

# 기본 검색
queryset = Article.objects.annotate(
    search=SearchVector("title", "body"),
).filter(search=SearchQuery("django 튜토리얼"))

# SearchRank로 관련성 순위 정렬
vector = SearchVector("title", "body")
query = SearchQuery("django 튜토리얼")

queryset = (
    Article.objects
    .annotate(rank=SearchRank(vector, query))
    .filter(rank__gte=0.1)
    .order_by("-rank")
)
```

### 가중치 멀티필드 검색

```python
# 필드별 가중치 부여 (A > B > C > D)
vector = (
    SearchVector("title", weight="A")
    + SearchVector("summary", weight="B")
    + SearchVector("body", weight="C")
    + SearchVector("tags", weight="D")
)

query = SearchQuery("django REST API")

queryset = (
    Article.objects
    .annotate(rank=SearchRank(vector, query, weights=[0.1, 0.2, 0.4, 1.0]))
    .filter(rank__gte=0.1)
    .order_by("-rank")
)
```

### search_type 옵션

```python
# plain (기본값): 각 단어를 OR로 검색
query = SearchQuery("django tutorial", search_type="plain")

# phrase: 정확한 구문 검색
query = SearchQuery("django REST framework", search_type="phrase")

# raw: PostgreSQL tsquery 문법 직접 사용
query = SearchQuery("django & (tutorial | guide)", search_type="raw")

# websearch: 웹 검색 엔진 스타일 구문
query = SearchQuery('"django tutorial" -beginner', search_type="websearch")
```

### SearchHeadline

```python
# 검색 결과에서 매칭 부분 하이라이트
queryset = Article.objects.annotate(
    headline=SearchHeadline(
        "body",
        SearchQuery("django"),
        start_sel="<mark>",
        stop_sel="</mark>",
        max_words=50,
        min_words=20,
    ),
)
```

### TrigramSimilarity (퍼지 매칭)

```python
from django.contrib.postgres.search import TrigramSimilarity, TrigramDistance

# pg_trgm 확장 필요: CREATE EXTENSION pg_trgm;

# 유사도 기반 검색 (오타 허용)
queryset = (
    Product.objects
    .annotate(similarity=TrigramSimilarity("name", "삼성갤럭시"))
    .filter(similarity__gt=0.3)
    .order_by("-similarity")
)

# TrigramDistance (1 - similarity, 정렬용)
queryset = (
    Product.objects
    .annotate(distance=TrigramDistance("name", "삼성갤럭시"))
    .filter(distance__lt=0.7)
    .order_by("distance")
)
```

### SearchVectorField + GIN 인덱스 성능 최적화

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector

class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    # 미리 계산된 검색 벡터 필드
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"], name="idx_article_search_gin"),
        ]

# 검색 벡터 업데이트 (save 시 또는 관리 커맨드로)
Article.objects.update(
    search_vector=SearchVector("title", weight="A")
    + SearchVector("body", weight="B")
)

# 검색 시 벡터 재계산 없이 인덱스 바로 활용
queryset = Article.objects.filter(
    search_vector=SearchQuery("django 튜토리얼")
)

# 시그널로 자동 업데이트
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Article)
def update_search_vector(sender, instance, **kwargs):
    Article.objects.filter(pk=instance.pk).update(
        search_vector=SearchVector("title", weight="A")
        + SearchVector("body", weight="B")
    )
```

---

## 4. Range Fields

**Source: Django PostgreSQL Fields 공식 문서**

### 기본 정의

```python
from django.contrib.postgres.fields import (
    IntegerRangeField,
    BigIntegerRangeField,
    DecimalRangeField,
    DateRangeField,
    DateTimeRangeField,
)
from psycopg.types.range import Range

class Event(models.Model):
    name = models.CharField(max_length=200)
    duration = DateTimeRangeField()  # 시작~종료 시간 범위

class Product(models.Model):
    name = models.CharField(max_length=200)
    price_range = IntegerRangeField()  # 가격 범위

# Range 객체로 값 생성
from datetime import datetime
Event.objects.create(
    name="컨퍼런스",
    duration=Range(
        datetime(2025, 6, 1, 9, 0),
        datetime(2025, 6, 3, 18, 0),
    ),
)

Product.objects.create(
    name="노트북",
    price_range=Range(800000, 1500000),
)
```

### 포함 / 중첩 / 경계 조회

```python
from datetime import date, datetime
from psycopg.types.range import Range

# contains: 범위가 값 또는 다른 범위를 포함하는지
Event.objects.filter(duration__contains=datetime(2025, 6, 2, 12, 0))
Product.objects.filter(price_range__contains=Range(900000, 1000000))

# contained_by: 범위가 다른 범위에 포함되는지
Event.objects.filter(
    duration__contained_by=Range(
        datetime(2025, 1, 1), datetime(2025, 12, 31)
    )
)

# overlap: 범위가 겹치는지
Event.objects.filter(
    duration__overlap=Range(
        datetime(2025, 6, 2), datetime(2025, 6, 4)
    )
)

# fully_lt / fully_gt: 범위가 완전히 이전/이후
Event.objects.filter(
    duration__fully_lt=Range(
        datetime(2025, 7, 1), datetime(2025, 7, 31)
    )
)

# startswith / endswith: 범위의 시작/끝 값
Event.objects.filter(duration__startswith__gte=datetime(2025, 6, 1))
Event.objects.filter(duration__endswith__lte=datetime(2025, 12, 31))

# isempty: 빈 범위인지
Product.objects.filter(price_range__isempty=False)

# adjacent_to: 인접한 범위
Product.objects.filter(
    price_range__adjacent_to=Range(1500000, 2000000)
)
```

### ExclusionConstraint로 겹침 방지

```python
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators

class RoomBooking(models.Model):
    room = models.ForeignKey("Room", on_delete=models.CASCADE)
    duration = DateTimeRangeField()

    class Meta:
        constraints = [
            ExclusionConstraint(
                name="no_overlapping_bookings",
                expressions=[
                    ("room", RangeOperators.EQUAL),
                    ("duration", RangeOperators.OVERLAPS),
                ],
            ),
        ]
# 같은 room에 대해 duration이 겹치는 레코드 삽입 시 DB 레벨에서 거부
```

---

## 5. PostgreSQL 집계 함수

**Source: Django PostgreSQL Aggregates 공식 문서**

### ArrayAgg

```python
from django.contrib.postgres.aggregates import ArrayAgg

# 그룹별 값을 배열로 수집
result = (
    Order.objects
    .values("customer__name")
    .annotate(
        order_ids=ArrayAgg("id", ordering="id"),
        statuses=ArrayAgg("status", distinct=True),
    )
)

# NULL 제외
result = Author.objects.annotate(
    book_titles=ArrayAgg("books__title", filter=Q(books__is_published=True))
)
```

### StringAgg

```python
from django.contrib.postgres.aggregates import StringAgg

# 문자열을 구분자로 합치기
result = (
    Category.objects
    .annotate(
        product_names=StringAgg(
            "products__name",
            delimiter=", ",
            ordering="products__name",
            distinct=True,
        )
    )
)

# filter와 함께 사용
result = Author.objects.annotate(
    recent_titles=StringAgg(
        "books__title",
        delimiter=" | ",
        filter=Q(books__published_date__year__gte=2024),
    )
)
```

### JSONBAgg

```python
from django.contrib.postgres.aggregates import JSONBAgg

# 값을 JSON 배열로 수집
result = (
    Customer.objects
    .annotate(
        order_totals=JSONBAgg("orders__total", ordering="-orders__created_at"),
    )
)

# 복합 값을 JSON 배열로 (values와 함께)
from django.db.models.functions import JSONObject

result = (
    Customer.objects
    .annotate(
        order_details=JSONBAgg(
            JSONObject(
                id="orders__id",
                total="orders__total",
                status="orders__status",
            ),
            ordering="-orders__created_at",
        )
    )
)
```

### filter + default 지원, Django 5.0+ 변경 사항

```python
# filter 파라미터: 조건부 집계
from django.db.models import Q

result = Order.objects.aggregate(
    active_ids=ArrayAgg("id", filter=Q(status="active")),
    cancelled_ids=ArrayAgg("id", filter=Q(status="cancelled")),
)

# default 파라미터 (Django 5.0+)
# 결과가 없을 때 기본값 반환 (이전에는 None 반환)
result = Order.objects.aggregate(
    active_ids=ArrayAgg("id", filter=Q(status="active"), default=Value([])),
    summary=StringAgg("note", delimiter=", ", default=Value("")),
)

# Django 5.0 변경 사항:
# - ArrayAgg, StringAgg, JSONBAgg 모두 default 파라미터 지원
# - 빈 결과에 대해 None 대신 지정한 기본값 반환
# - ordering 파라미터가 모든 PostgreSQL 집계에서 일관되게 동작
```

---

## 6. PostgreSQL 인덱스

**Source: Django PostgreSQL Indexes 공식 문서**

### 인덱스 유형 비교 표

| 인덱스 | 용도 | 적합한 필드/조회 | 크기 |
|--------|------|-----------------|------|
| **GinIndex** | 역인덱스 | ArrayField, JSONField, Full-Text Search, HStoreField | 큼 |
| **GistIndex** | 범용 검색 트리 | Range Fields, 지리 데이터, 근접 검색, ExclusionConstraint | 중간 |
| **BrinIndex** | 물리적 정렬 데이터 | 시계열 데이터 (created_at 등), 자동증가 필드 | 매우 작음 |
| **HashIndex** | 등가 비교 전용 | 등가(=) 비교만 하는 필드 | 작음 |
| **BloomIndex** | 다중 컬럼 등가 | 여러 컬럼의 동시 등가 비교 (bloom 확장 필요) | 작음 |

### 코드 예시

```python
from django.contrib.postgres.indexes import (
    GinIndex, GistIndex, BrinIndex, HashIndex, BloomIndex,
)

class Article(models.Model):
    title = models.CharField(max_length=200)
    tags = ArrayField(models.CharField(max_length=50), default=list)
    metadata = models.JSONField(default=dict)
    search_vector = SearchVectorField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    duration = DateTimeRangeField(null=True)
    category = models.CharField(max_length=50)
    author = models.CharField(max_length=100)

    class Meta:
        indexes = [
            # GIN: ArrayField, JSONField, Full-Text Search에 필수
            GinIndex(fields=["tags"], name="idx_article_tags_gin"),
            GinIndex(fields=["metadata"], name="idx_article_meta_gin"),
            GinIndex(fields=["search_vector"], name="idx_article_search_gin"),

            # GIN + opclass: trigram 유사도 검색용
            GinIndex(
                fields=["title"],
                name="idx_article_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),

            # GiST: Range Field, ExclusionConstraint에 필요
            GistIndex(fields=["duration"], name="idx_article_duration_gist"),

            # BRIN: 시계열/자동증가 데이터에 매우 효율적 (작은 크기)
            BrinIndex(fields=["created_at"], name="idx_article_created_brin"),

            # Hash: 등가 비교만 하는 필드
            HashIndex(fields=["slug"], name="idx_article_slug_hash"),

            # Bloom: 여러 컬럼 등가 비교 (CREATE EXTENSION bloom 필요)
            BloomIndex(
                fields=["category", "author"],
                name="idx_article_bloom",
                length=80,       # 전체 서명 길이 (비트)
                columns=[2, 4],  # 각 컬럼의 비트 수
            ),
        ]
```

---

## 7. ExclusionConstraint

**Source: Django PostgreSQL Constraints 공식 문서**

### btree_gist 확장 필요

```python
# ExclusionConstraint에서 Range 외의 필드(예: 정수, 문자열)를
# 등가(=) 비교하려면 btree_gist 확장이 필요함

# 마이그레이션에서 확장 설치
from django.contrib.postgres.operations import BtreeGistExtension

class Migration(migrations.Migration):
    operations = [
        BtreeGistExtension(),
    ]
```

### 겹치는 예약 방지 예시

```python
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import (
    DateTimeRangeField,
    RangeOperators,
)
from django.db import models

class MeetingRoom(models.Model):
    name = models.CharField(max_length=100)

class Reservation(models.Model):
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE)
    time_slot = DateTimeRangeField()
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # 같은 회의실에서 시간이 겹치는 예약 방지
            ExclusionConstraint(
                name="no_overlapping_reservations",
                expressions=[
                    ("room", RangeOperators.EQUAL),         # room이 같고
                    ("time_slot", RangeOperators.OVERLAPS),  # 시간이 겹치면 거부
                ],
                # 취소된 예약은 제외 (Django 4.0+)
                condition=Q(is_cancelled=False),
            ),
        ]

# 사용 예시
from psycopg.types.range import Range
from datetime import datetime

# 정상 예약
Reservation.objects.create(
    room=room_a,
    time_slot=Range(datetime(2025, 6, 1, 9, 0), datetime(2025, 6, 1, 10, 0)),
)

# 겹치는 예약 시도 -> IntegrityError 발생
try:
    Reservation.objects.create(
        room=room_a,
        time_slot=Range(datetime(2025, 6, 1, 9, 30), datetime(2025, 6, 1, 11, 0)),
    )
except IntegrityError:
    print("해당 시간에 이미 예약이 있습니다.")

# 다른 회의실은 같은 시간에 예약 가능
Reservation.objects.create(
    room=room_b,
    time_slot=Range(datetime(2025, 6, 1, 9, 30), datetime(2025, 6, 1, 11, 0)),
)
```

### 복합 ExclusionConstraint

```python
class DoctorSchedule(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    location = models.ForeignKey("Clinic", on_delete=models.CASCADE)
    time_slot = DateTimeRangeField()
    day_of_week = models.IntegerField()  # 0=월, 6=일

    class Meta:
        constraints = [
            # 같은 의사가 같은 요일에 시간이 겹치는 스케줄 방지
            ExclusionConstraint(
                name="no_doctor_double_booking",
                expressions=[
                    ("doctor", RangeOperators.EQUAL),
                    ("day_of_week", RangeOperators.EQUAL),
                    ("time_slot", RangeOperators.OVERLAPS),
                ],
            ),
            # 같은 장소에서 같은 시간에 겹치는 스케줄 방지
            ExclusionConstraint(
                name="no_location_double_booking",
                expressions=[
                    ("location", RangeOperators.EQUAL),
                    ("time_slot", RangeOperators.OVERLAPS),
                ],
            ),
        ]
```
