# Django Model Index Strategy Review (PostgreSQL)

## 현재 인덱스 구성 평가

### Product 모델

현재 4개의 B-tree 인덱스가 설정되어 있다. 기본적인 단일 컬럼 인덱스로, 자주 수행되는 쿼리 패턴에 비해 PostgreSQL 특화 인덱스가 전혀 활용되지 않고 있다.

### Order 모델

`status`와 `created_at`에 대한 단일 B-tree 인덱스만 존재한다. `customer` FK에는 Django가 자동으로 인덱스를 생성하므로 별도 정의가 불필요하다.

---

## Review Findings

### 1. JSONField에 GIN 인덱스 누락

```
[Convention] -- JSONField에 contains, has_key 등의 조회를 수행하려면 GIN 인덱스가 필수다.
인덱스 없이 JSON 필터링을 하면 Full Table Scan이 발생한다.
```

`Product.attributes`에서 `color='red' AND size='L'` 같은 필터를 수행하려면 `__contains` 조회를 사용해야 하는데, 이를 효율적으로 처리하려면 GIN 인덱스가 반드시 필요하다.

```python
# 쿼리 예시
Product.objects.filter(attributes__contains={"color": "red", "size": "L"})
```

**필요한 인덱스:**
```python
from django.contrib.postgres.indexes import GinIndex

GinIndex(fields=["attributes"], name="idx_product_attrs_gin"),
```

### 2. ArrayField에 GIN 인덱스 누락

```
[Convention] -- ArrayField에는 GIN 인덱스가 필수다. contains, contained_by, overlap 조회가
GIN 인덱스 없이는 Full Table Scan을 유발한다.
```

`tags`에 'organic' 포함 여부를 확인하는 쿼리는 `__contains` 조회를 사용한다.

```python
# 쿼리 예시
Product.objects.filter(tags__contains=["organic"])
```

**필요한 인덱스:**
```python
GinIndex(fields=["tags"], name="idx_product_tags_gin"),
```

### 3. 텍스트 검색에 Full-Text Search 인덱스 누락

```
[Convention] -- 이름+설명 텍스트 검색에는 SearchVectorField + GIN 인덱스 조합이 필요하다.
단순 B-tree 인덱스로는 LIKE '%keyword%' 형태의 검색을 인덱스로 처리할 수 없다.
```

현재 `name`에 B-tree 인덱스만 있으며, `description`에는 인덱스가 없다. 텍스트 검색을 위한 두 가지 접근이 가능하다.

**접근 A -- SearchVectorField (권장, 검색 빈도가 높을 때):**

```python
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Product(models.Model):
    # ... 기존 필드 ...
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"], name="idx_product_search_gin"),
        ]
```

```python
# 벡터 업데이트
from django.contrib.postgres.search import SearchVector
Product.objects.update(
    search_vector=SearchVector("name", weight="A")
    + SearchVector("description", weight="B")
)

# 검색
from django.contrib.postgres.search import SearchQuery, SearchRank
query = SearchQuery("organic cotton", search_type="websearch")
Product.objects.filter(search_vector=query).annotate(
    rank=SearchRank(F("search_vector"), query)
).order_by("-rank")
```

**접근 B -- Trigram 유사도 (오타 허용 검색이 필요할 때):**

```python
GinIndex(
    fields=["name"],
    name="idx_product_name_trgm",
    opclasses=["gin_trgm_ops"],
),
```

### 4. `is_active` 단일 B-tree 인덱스의 낮은 선택도

```
[Convention] -- Boolean 필드의 단일 B-tree 인덱스는 선택도(selectivity)가 매우 낮아 옵티마이저가
인덱스를 무시할 가능성이 높다. 자주 사용되는 필터 조합에 맞는 복합 인덱스 또는 부분 인덱스로
대체해야 한다.
```

"활성 상품만 가격순 정렬"이라는 쿼리 패턴에 맞는 복합/부분 인덱스가 필요하다.

**필요한 인덱스:**
```python
# 부분 인덱스: 활성 상품에 대해서만 가격순 정렬 인덱스
models.Index(
    fields=["price"],
    name="idx_product_active_price",
    condition=models.Q(is_active=True),
),
```

이 인덱스는 `Product.objects.filter(is_active=True).order_by("price")` 쿼리에서 인덱스 스캔만으로 결과를 반환할 수 있다. 기존의 `is_active` 단일 인덱스와 `price` 단일 인덱스를 이 하나의 부분 인덱스로 대체 가능하다.

### 5. `created_at`에 B-tree 대신 BRIN 인덱스 적용 가능

```
[Convention] -- 시계열 데이터(created_at 등 자동증가 성격의 필드)에는 BRIN 인덱스가
B-tree 대비 인덱스 크기가 수십 배 작으면서 범위 검색 성능이 우수하다.
```

"최근 6개월 주문만 조회"와 같은 시계열 범위 검색에는 BRIN이 적합하다. `created_at`은 레코드 삽입 순서와 물리적 저장 순서가 일치하므로 BRIN의 이상적인 대상이다.

**필요한 인덱스:**
```python
from django.contrib.postgres.indexes import BrinIndex

# Product.created_at
BrinIndex(fields=["created_at"], name="idx_product_created_brin"),

# Order.created_at
BrinIndex(fields=["created_at"], name="idx_order_created_brin"),
```

### 6. Order 모델의 `status` + `created_at` 복합 인덱스 누락

```
[Convention] -- 함께 필터링되는 필드는 복합 인덱스로 묶어야 한다. 개별 단일 인덱스보다
복합 인덱스가 쿼리 효율이 높다.
```

주문 조회 시 상태 + 기간 필터가 함께 사용될 가능성이 높다 (예: 최근 6개월의 'completed' 주문).

```python
models.Index(
    fields=["status", "-created_at"],
    name="idx_order_status_created",
),
```

### 7. Order.metadata JSONField에 GIN 인덱스 누락

```
[Convention] -- JSONField를 정의해 놓았으나 인덱스가 없다. 향후 metadata로 필터링할 경우
Full Table Scan이 발생한다.
```

현재 쿼리 패턴에 `metadata` 필터가 명시되어 있지는 않지만, JSONField를 사용하는 이상 GIN 인덱스를 선제적으로 추가하는 것이 좋다.

```python
GinIndex(fields=["metadata"], name="idx_order_metadata_gin"),
```

---

## 개선된 전체 인덱스 구성

```python
from django.contrib.postgres.indexes import GinIndex, BrinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    attributes = models.JSONField(default=dict)
    tags = ArrayField(models.CharField(max_length=50), default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)  # Full-Text Search용

    class Meta:
        indexes = [
            # B-tree: 이름 정확 매칭 / 정렬용 (유지)
            models.Index(fields=["name"]),

            # 부분 인덱스: 활성 상품의 가격순 정렬 (is_active + price 대체)
            models.Index(
                fields=["price"],
                name="idx_product_active_price",
                condition=models.Q(is_active=True),
            ),

            # BRIN: 시계열 데이터 (B-tree 대체, 크기 수십 배 절감)
            BrinIndex(
                fields=["created_at"],
                name="idx_product_created_brin",
            ),

            # GIN: JSONField 필터 (contains, has_key 등)
            GinIndex(
                fields=["attributes"],
                name="idx_product_attrs_gin",
            ),

            # GIN: ArrayField 필터 (contains, overlap 등)
            GinIndex(
                fields=["tags"],
                name="idx_product_tags_gin",
            ),

            # GIN: Full-Text Search
            GinIndex(
                fields=["search_vector"],
                name="idx_product_search_gin",
            ),

            # GIN + trigram: 이름 퍼지 검색 (pg_trgm 확장 필요)
            GinIndex(
                fields=["name"],
                name="idx_product_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]


class Order(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    status = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        indexes = [
            # 복합 인덱스: 상태 + 기간 필터 (단일 인덱스 2개 대체)
            models.Index(
                fields=["status", "-created_at"],
                name="idx_order_status_created",
            ),

            # BRIN: 시계열 범위 검색 (최근 6개월 조회 등)
            BrinIndex(
                fields=["created_at"],
                name="idx_order_created_brin",
            ),

            # GIN: JSONField 필터
            GinIndex(
                fields=["metadata"],
                name="idx_order_metadata_gin",
            ),
        ]
```

---

## 변경 요약

| 쿼리 패턴 | 기존 인덱스 | 개선 인덱스 | 근거 |
|-----------|------------|------------|------|
| 이름+설명 텍스트 검색 | `name` B-tree (부분 매칭 불가) | `SearchVectorField` + GIN, `name` trigram GIN | Full-Text Search와 퍼지 매칭 지원 |
| JSON attributes 필터 | 없음 | `attributes` GIN | `__contains` 조회에 GIN 필수 |
| 태그 필터 | 없음 | `tags` GIN | ArrayField `__contains`에 GIN 필수 |
| 활성 상품 가격순 정렬 | `is_active` B-tree + `price` B-tree | `price` 부분 인덱스 (condition: is_active=True) | 낮은 선택도의 boolean 인덱스 대체 |
| 최근 6개월 주문 조회 | `created_at` B-tree | `created_at` BRIN | 시계열 데이터에 BRIN이 크기/성능 모두 우수 |
| 상태+기간 복합 필터 | `status` B-tree + `created_at` B-tree | `status, -created_at` 복합 인덱스 | 함께 필터되는 컬럼은 복합 인덱스로 |

## 필요한 PostgreSQL 확장

```sql
-- Full-Text Search 퍼지 매칭용
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## 주의 사항

- GIN 인덱스는 B-tree보다 크기가 크고 쓰기 시 오버헤드가 있다. 읽기 위주 워크로드에 적합하다.
- BRIN 인덱스는 데이터가 물리적 삽입 순서와 일치할 때만 효과적이다. `created_at`처럼 단조 증가하는 필드에 적합하다. 대량 `UPDATE`로 행이 재배치되면 효율이 떨어진다.
- `SearchVectorField`는 별도로 벡터를 갱신해야 한다. `post_save` 시그널이나 DB 트리거로 자동화할 수 있다.
- 인덱스 추가 후 반드시 `EXPLAIN ANALYZE`로 실행 계획을 확인하고, 불필요한 인덱스는 제거한다.
