# Django Model Index Strategy Review (PostgreSQL)

## 1. 현재 인덱스 분석

### Product 모델

| 인덱스 | 평가 | 비고 |
|--------|------|------|
| `Index(fields=['name'])` | 부분 적합 | B-tree. 정확 매칭/정렬엔 유효하나 텍스트 검색에는 부적합 |
| `Index(fields=['price'])` | 부분 적합 | 단독 price 인덱스는 활용 빈도 낮음 (보통 조건부 정렬에 사용) |
| `Index(fields=['created_at'])` | 적합 | 시계열 조회에 유효 |
| `Index(fields=['is_active'])` | 비효율 | Boolean은 카디널리티가 2이므로 단독 B-tree 인덱스의 효용이 매우 낮음 |

### Order 모델

| 인덱스 | 평가 | 비고 |
|--------|------|------|
| `Index(fields=['status'])` | 부분 적합 | 카디널리티 낮을 가능성 높음. 단독보다 복합 인덱스 권장 |
| `Index(fields=['created_at'])` | 적합 | 시계열 조회에 유효 |

### 누락된 인덱스

- `customer` ForeignKey에 대한 인덱스가 명시되어 있지 않음 (Django가 ForeignKey에 `db_index=True`를 기본 적용하므로 자동 생성됨 -- 이 부분은 문제 없음)
- `attributes` (JSONField), `tags` (ArrayField), `metadata` (JSONField)에 대한 인덱스 전무

---

## 2. 쿼리별 권장 인덱스 전략

### 2.1 상품 이름+설명 텍스트 검색 -- GIN 인덱스 (Full Text Search)

현재 `name`의 B-tree 인덱스는 `LIKE 'keyword%'`(prefix match)에만 유효하다. `icontains`나 full-text search에는 전혀 사용되지 않는다.

PostgreSQL의 `GIN` 인덱스 + `SearchVector`를 활용해야 한다.

```python
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    # 선택: 미리 계산된 search vector 필드 추가
    search_vector = SearchVectorField(null=True)
    # ...

    class Meta:
        indexes = [
            # 방법 A: SearchVectorField에 GIN 인덱스 (권장, 가장 빠름)
            GinIndex(fields=['search_vector']),

            # 방법 B: SearchVectorField 없이 함수 기반 인덱스
            # migration에서 raw SQL로 생성:
            # CREATE INDEX product_name_desc_search_idx
            #   ON product_product USING GIN (
            #     to_tsvector('simple', coalesce(name, '') || ' ' || coalesce(description, ''))
            #   );
        ]
```

**쿼리 예시:**
```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

Product.objects.annotate(
    search=SearchVector('name', 'description', config='simple')
).filter(search=SearchQuery('keyword', config='simple'))
```

> `SearchVectorField` + 트리거/시그널로 자동 업데이트하는 방법 A가 조회 성능이 가장 좋다. 방법 B는 스키마 변경 없이 적용 가능하지만 인덱스 빌드 시점에만 갱신된다.

---

### 2.2 JSON attributes 필터 -- GIN 인덱스

현재 `attributes` JSONField에 인덱스가 없으므로 sequential scan이 발생한다.

```python
from django.contrib.postgres.indexes import GinIndex

class Meta:
    indexes = [
        # 전체 JSON 경로 탐색을 위한 GIN 인덱스
        GinIndex(fields=['attributes']),
    ]
```

이 인덱스는 다음 쿼리들을 모두 커버한다:
```python
# 키 존재 확인
Product.objects.filter(attributes__has_key='color')

# 특정 키-값 필터
Product.objects.filter(attributes__color='red')

# 중첩 경로 필터
Product.objects.filter(attributes__specs__weight__gte=100)  # 주의: __gte 등 비교 연산은 GIN으로 커버 불가
```

**주의:** `__gte`, `__lte` 같은 범위 비교는 GIN으로 커버되지 않는다. 특정 JSON 경로에 대한 범위 쿼리가 빈번하다면 함수 기반 B-tree 인덱스를 추가로 고려해야 한다:

```sql
-- 예: attributes->'specs'->'weight' 에 대한 범위 쿼리용
CREATE INDEX product_attr_weight_idx
  ON product_product (((attributes->'specs'->>'weight')::numeric));
```

---

### 2.3 태그 필터 (ArrayField) -- GIN 인덱스

`tags`에 특정 값이 포함되는지 확인하는 쿼리는 GIN 인덱스가 필수다.

```python
from django.contrib.postgres.indexes import GinIndex

class Meta:
    indexes = [
        GinIndex(fields=['tags']),
    ]
```

**쿼리 예시:**
```python
# 'organic' 태그 포함 상품
Product.objects.filter(tags__contains=['organic'])

# 여러 태그 중 하나라도 포함
Product.objects.filter(tags__overlap=['organic', 'vegan'])
```

GIN 인덱스는 `@>` (contains), `&&` (overlap), `<@` (contained_by) 연산자를 모두 지원한다.

---

### 2.4 활성 상품만 가격순 정렬 -- 조건부 복합 인덱스

현재 `is_active`와 `price`가 별도 인덱스로 존재한다. 이 쿼리 패턴에는 **Partial Index (조건부 인덱스)**가 최적이다.

```python
class Meta:
    indexes = [
        # is_active=True인 행만 price로 인덱싱 (인덱스 크기가 작아 효율적)
        models.Index(
            fields=['price'],
            name='product_active_price_idx',
            condition=models.Q(is_active=True),
        ),
    ]
```

**효과:**
- `is_active=True` 행만 인덱싱하므로 인덱스 크기가 전체 대비 작음
- `Product.objects.filter(is_active=True).order_by('price')` 쿼리에서 Index Only Scan 가능
- 기존 `is_active` 단독 인덱스는 제거 가능

---

### 2.5 최근 6개월 주문 조회 (시계열) -- 조건부 인덱스 또는 BRIN

두 가지 전략이 있다.

**전략 A: Partial Index (추천 -- 핫 데이터가 명확할 때)**

```python
import datetime
from django.utils import timezone

class Meta:
    indexes = [
        models.Index(
            fields=['created_at'],
            name='order_recent_created_idx',
            condition=models.Q(
                created_at__gte=timezone.now() - datetime.timedelta(days=180)
            ),
        ),
    ]
```

> 주의: Partial Index의 condition에 고정 날짜를 쓰면 시간이 지남에 따라 재생성이 필요하다. 주기적 migration이 필요하므로 운영 부담이 있다.

**전략 B: BRIN Index (추천 -- 시계열 데이터가 물리적으로 정렬되어 있을 때)**

주문은 거의 항상 시간순으로 삽입되므로 물리적 저장 순서와 `created_at`의 상관관계가 높다. 이 경우 BRIN이 B-tree보다 훨씬 작은 인덱스 크기로 유사한 성능을 낸다.

```python
from django.contrib.postgres.indexes import BrinIndex

class Meta:
    indexes = [
        BrinIndex(fields=['created_at'], autosummarize=True),
    ]
```

**B-tree vs BRIN 비교 (1억 행 기준 추정):**

| 지표 | B-tree | BRIN |
|------|--------|------|
| 인덱스 크기 | ~2GB | ~50KB |
| 점 쿼리 성능 | O(log n) | 약간 느림 |
| 범위 쿼리 성능 | 우수 | 우수 (물리 정렬 시) |
| INSERT 오버헤드 | 중간 | 매우 낮음 |

> 시계열 범위 조회가 주 패턴이고 데이터가 시간순 삽입이면 BRIN을 권장한다.

**전략 C: 복합 인덱스 (status + created_at)**

`status`별 최근 주문 조회가 빈번하다면:

```python
class Meta:
    indexes = [
        models.Index(fields=['status', 'created_at']),
        # 또는 역순 정렬이 필요하면:
        models.Index(fields=['status', '-created_at']),
    ]
```

---

## 3. 최종 권장 인덱스 구성

### Product 모델

```python
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    attributes = models.JSONField(default=dict)
    tags = ArrayField(models.CharField(max_length=50), default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)  # 추가

    class Meta:
        indexes = [
            # 1. 텍스트 검색용 (이름+설명)
            GinIndex(fields=['search_vector'], name='product_search_gin_idx'),

            # 2. JSON attributes 필터용
            GinIndex(fields=['attributes'], name='product_attrs_gin_idx'),

            # 3. 태그 필터용
            GinIndex(fields=['tags'], name='product_tags_gin_idx'),

            # 4. 활성 상품 가격 정렬용 (Partial Index)
            models.Index(
                fields=['price'],
                name='product_active_price_idx',
                condition=models.Q(is_active=True),
            ),

            # 5. 시간순 조회용 (유지)
            models.Index(fields=['-created_at'], name='product_created_desc_idx'),

            # 6. name B-tree (exact match / prefix search 용도로 유지)
            models.Index(fields=['name'], name='product_name_idx'),
        ]
```

**제거 대상:**
- `Index(fields=['is_active'])` -- Partial Index로 대체됨, 단독 Boolean 인덱스는 비효율
- `Index(fields=['price'])` -- Partial Index로 대체됨

### Order 모델

```python
from django.contrib.postgres.indexes import BrinIndex, GinIndex

class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    status = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        indexes = [
            # 1. 시계열 범위 조회용 (B-tree 대체)
            BrinIndex(fields=['created_at'], autosummarize=True, name='order_created_brin_idx'),

            # 2. 상태별 최근 주문 조회용 복합 인덱스
            models.Index(fields=['status', '-created_at'], name='order_status_created_idx'),

            # 3. 고객별 주문 조회 (FK 기본 인덱스와 별도로, 정렬 포함)
            models.Index(fields=['customer', '-created_at'], name='order_customer_created_idx'),

            # 4. metadata JSON 필터가 필요하다면
            GinIndex(fields=['metadata'], name='order_metadata_gin_idx'),
        ]
```

**제거 대상:**
- `Index(fields=['status'])` -- 복합 인덱스 `(status, -created_at)`로 대체
- `Index(fields=['created_at'])` -- BRIN으로 대체

---

## 4. 요약: PostgreSQL 특화 인덱스 필요 지점

| 필드/쿼리 | 필요한 인덱스 타입 | 이유 |
|-----------|-------------------|------|
| `name` + `description` 텍스트 검색 | **GIN** (tsvector) | B-tree는 full-text search 불가 |
| `attributes` (JSONField) | **GIN** | `@>`, `?`, `?&` 연산자 지원 필요 |
| `tags` (ArrayField) | **GIN** | `@>`, `&&` 배열 연산자 지원 필요 |
| `is_active=True` + `price` 정렬 | **Partial Index** (B-tree + condition) | 불필요한 행 제외로 인덱스 크기/성능 최적화 |
| `created_at` 시계열 범위 (Order) | **BRIN** | 시간순 삽입 데이터에 극소 인덱스 크기로 범위 조회 지원 |
| `metadata` (JSONField) | **GIN** | JSON 키/값 필터 지원 필요 |

총 4종의 PostgreSQL 특화 인덱스(GIN 4개, BRIN 1개, Partial 1개)가 필요하며, 기존 B-tree 단독 인덱스 4개 중 3개(`is_active`, `price`, `status`)는 제거 또는 복합 인덱스로 대체를 권장한다.
