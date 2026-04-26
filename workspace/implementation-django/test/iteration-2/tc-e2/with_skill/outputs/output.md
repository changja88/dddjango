# 상품 카탈로그 -- Django 모델 및 PostgreSQL 쿼리

## 사전 요구사항

```sql
-- PostgreSQL 확장 설치 (마이그레이션 또는 직접 실행)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

```python
# 마이그레이션에서 확장 설치
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):
    operations = [
        TrigramExtension(),
    ]
```

---

## 1. 모델 정의

```python
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models import Q
from django.db.models.functions import Now


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    required_attributes = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="이 카테고리의 상품이 가져야 할 속성 키 목록",
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Product.Status.ACTIVE)

    def in_price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)

    def with_tags(self, tags):
        """주어진 태그를 모두 포함하는 상품."""
        return self.filter(tags__contains=tags)

    def with_any_tags(self, tags):
        """주어진 태그 중 하나라도 포함하는 상품."""
        return self.filter(tags__overlap=tags)

    def with_attribute(self, key, value):
        """동적 속성에서 특정 키-값 쌍을 가진 상품."""
        return self.filter(**{f"attributes__{key}": value})

    def has_attribute(self, key):
        """동적 속성에서 특정 키가 존재하는 상품."""
        return self.filter(attributes__has_key=key)


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    # --- 기본 필드 ---
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.DRAFT,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    # --- PostgreSQL 전용 필드 ---
    attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="동적 속성 (색상, 크기, 무게 등 카테고리마다 다름)",
    )
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
    )
    search_vector = SearchVectorField(null=True, editable=False)

    # --- 타임스탬프 ---
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    # --- Manager ---
    objects = ProductQuerySet.as_manager()

    class Meta:
        indexes = [
            # B-tree 복합 인덱스: 상태 + 가격 범위 필터
            models.Index(
                fields=["status", "price"],
                name="idx_product_status_price",
            ),
            # B-tree 부분 인덱스: 활성 상품의 가격 정렬
            models.Index(
                fields=["price"],
                name="idx_product_active_price",
                condition=Q(status="active"),
            ),
            # GIN: JSONField 쿼리 (contains, has_key 등)
            GinIndex(
                fields=["attributes"],
                name="idx_product_attrs_gin",
            ),
            # GIN: ArrayField 쿼리 (contains, overlap 등)
            GinIndex(
                fields=["tags"],
                name="idx_product_tags_gin",
            ),
            # GIN: SearchVectorField Full-Text Search
            GinIndex(
                fields=["search_vector"],
                name="idx_product_search_gin",
            ),
            # GIN + gin_trgm_ops: Trigram 유사도 검색 (오타 허용)
            GinIndex(
                fields=["name"],
                name="idx_product_name_trgm",
                opclasses=["gin_trgm_ops"],
            ),
            # BRIN: 시계열 created_at (물리적 삽입 순서와 일치)
            BrinIndex(
                fields=["created_at"],
                name="idx_product_created_brin",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(price__gte=0),
                name="product_price_non_negative",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.price is not None and self.price < 0:
            raise ValidationError({"price": "가격은 0 이상이어야 합니다."})
```

---

## 2. 인덱스 설계 요약

| 인덱스 | 유형 | 대상 필드 | 용도 |
|--------|------|-----------|------|
| `idx_product_status_price` | B-tree (복합) | `status`, `price` | 상태별 가격 범위 필터 |
| `idx_product_active_price` | B-tree (부분) | `price` WHERE `status='active'` | 활성 상품 가격 정렬/필터 |
| `idx_product_attrs_gin` | GIN | `attributes` (JSONField) | `contains`, `has_key` 조회 |
| `idx_product_tags_gin` | GIN | `tags` (ArrayField) | `contains`, `overlap` 조회 |
| `idx_product_search_gin` | GIN | `search_vector` | Full-Text Search |
| `idx_product_name_trgm` | GIN (gin_trgm_ops) | `name` | Trigram 유사도 검색 (오타 허용) |
| `idx_product_created_brin` | BRIN | `created_at` | 시계열 범위 스캔, 매우 작은 크기 |

---

## 3. SearchVector 업데이트

```python
from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Product)
def update_product_search_vector(sender, instance, **kwargs):
    """상품 저장 시 search_vector 자동 갱신."""
    Product.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector("name", weight="A")
            + SearchVector("description", weight="B")
        ),
    )


def rebuild_all_search_vectors():
    """전체 상품의 search_vector를 일괄 재구축 (관리 커맨드용)."""
    Product.objects.update(
        search_vector=(
            SearchVector("name", weight="A")
            + SearchVector("description", weight="B")
        ),
    )
```

---

## 4. 검색 쿼리 (Full-Text Search + Trigram)

```python
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F, Q, Value
from django.db.models.functions import Greatest


def search_products(query_text, min_rank=0.1, min_similarity=0.3):
    """Full-Text Search + Trigram을 결합한 상품 검색.

    1단계: SearchVector + SearchQuery + SearchRank로 정규 검색
    2단계: TrigramSimilarity로 오타 허용 퍼지 매칭
    3단계: 두 점수를 결합하여 최종 랭킹
    """
    search_query = SearchQuery(query_text, search_type="websearch")

    return (
        Product.objects
        .active()
        .annotate(
            # Full-Text Search 랭킹
            rank=SearchRank(F("search_vector"), search_query),
            # Trigram 유사도 (name 필드 대상, 오타 허용)
            similarity=TrigramSimilarity("name", query_text),
            # 검색 결과 하이라이트
            headline=SearchHeadline(
                "description",
                search_query,
                start_sel="<mark>",
                stop_sel="</mark>",
                max_words=35,
                min_words=15,
            ),
        )
        .filter(Q(rank__gte=min_rank) | Q(similarity__gte=min_similarity))
        .annotate(
            # 두 점수 중 높은 값을 최종 스코어로 사용
            final_score=Greatest("rank", "similarity"),
        )
        .order_by("-final_score")
    )


def fulltext_search(query_text):
    """미리 계산된 search_vector를 사용하는 기본 Full-Text Search."""
    search_query = SearchQuery(query_text, search_type="plain")

    return (
        Product.objects
        .active()
        .annotate(rank=SearchRank(F("search_vector"), search_query))
        .filter(rank__gte=0.1)
        .order_by("-rank")
    )


def weighted_search(query_text):
    """가중치를 부여한 멀티필드 검색 (search_vector 미사용 시)."""
    vector = (
        SearchVector("name", weight="A")
        + SearchVector("description", weight="B")
    )
    query = SearchQuery(query_text, search_type="websearch")

    return (
        Product.objects
        .active()
        .annotate(
            rank=SearchRank(vector, query, weights=[0.1, 0.2, 0.4, 1.0]),
        )
        .filter(rank__gte=0.1)
        .order_by("-rank")
    )


def fuzzy_search(query_text, threshold=0.3):
    """Trigram 기반 퍼지 검색 (오타 허용)."""
    return (
        Product.objects
        .active()
        .annotate(similarity=TrigramSimilarity("name", query_text))
        .filter(similarity__gt=threshold)
        .order_by("-similarity")
    )
```

---

## 5. JSON 필터 쿼리

```python
def filter_by_attribute_value(key, value):
    """동적 속성에서 특정 키-값 매칭.

    예: filter_by_attribute_value("color", "black")
    SQL: WHERE attributes->>'color' = 'black'
    """
    return Product.objects.active().filter(**{f"attributes__{key}": value})


def filter_by_nested_attribute(path, value):
    """중첩 JSON 경로 조회.

    예: filter_by_nested_attribute("specs__weight__lt", 500)
    SQL: WHERE (attributes->'specs'->>'weight')::numeric < 500
    """
    return Product.objects.active().filter(**{f"attributes__{path}": value})


def filter_by_attribute_contains(partial_attrs):
    """JSON 구조 포함 검색 (GIN 인덱스 활용).

    예: filter_by_attribute_contains({"color": "black", "specs": {"weight": 200}})
    SQL: WHERE attributes @> '{"color":"black","specs":{"weight":200}}'
    """
    return Product.objects.active().filter(attributes__contains=partial_attrs)


def filter_by_has_key(key):
    """특정 속성 키가 존재하는 상품.

    예: filter_by_has_key("warranty")
    SQL: WHERE attributes ? 'warranty'
    """
    return Product.objects.active().filter(attributes__has_key=key)


def filter_by_has_all_keys(keys):
    """주어진 키가 모두 존재하는 상품.

    예: filter_by_has_all_keys(["color", "size", "weight"])
    SQL: WHERE attributes ?& ARRAY['color','size','weight']
    """
    return Product.objects.active().filter(attributes__has_keys=keys)


def filter_by_has_any_keys(keys):
    """주어진 키 중 하나라도 존재하는 상품.

    예: filter_by_has_any_keys(["discount", "promotion"])
    SQL: WHERE attributes ?| ARRAY['discount','promotion']
    """
    return Product.objects.active().filter(attributes__has_any_keys=keys)
```

---

## 6. 태그 필터 쿼리

```python
def filter_by_all_tags(tags):
    """주어진 태그를 모두 포함하는 상품 (AND 조건).

    예: filter_by_all_tags(["신상품", "할인"])
    SQL: WHERE tags @> ARRAY['신상품','할인']
    """
    return Product.objects.active().filter(tags__contains=tags)


def filter_by_any_tags(tags):
    """주어진 태그 중 하나라도 포함하는 상품 (OR 조건).

    예: filter_by_any_tags(["봄신상", "여름신상", "겨울신상"])
    SQL: WHERE tags && ARRAY['봄신상','여름신상','겨울신상']
    """
    return Product.objects.active().filter(tags__overlap=tags)


def filter_by_exact_tags(tags):
    """태그가 주어진 집합에 완전히 포함되는 상품.

    예: filter_by_exact_tags(["신상품", "할인", "추천", "베스트"])
    SQL: WHERE tags <@ ARRAY['신상품','할인','추천','베스트']
    """
    return Product.objects.active().filter(tags__contained_by=tags)


def filter_by_tag_count(min_count):
    """최소 N개 이상의 태그를 가진 상품.

    예: filter_by_tag_count(3)
    SQL: WHERE array_length(tags, 1) >= 3
    """
    return Product.objects.active().filter(tags__len__gte=min_count)
```

---

## 7. 복합 검색 서비스 함수

```python
from decimal import Decimal

from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F, Q
from django.db.models.functions import Greatest


def product_catalog_search(
    *,
    query_text: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    tags: list[str] | None = None,
    required_attrs: dict | None = None,
    attr_key_exists: str | None = None,
):
    """상품 카탈로그 통합 검색.

    Full-Text Search, Trigram, JSON 필터, 태그 필터, 가격 범위를
    하나의 QuerySet 체인으로 결합한다.
    """
    qs = Product.objects.active().select_related("category")

    # Full-Text Search + Trigram
    if query_text:
        search_query = SearchQuery(query_text, search_type="websearch")
        qs = (
            qs
            .annotate(
                rank=SearchRank(F("search_vector"), search_query),
                similarity=TrigramSimilarity("name", query_text),
                final_score=Greatest("rank", "similarity"),
            )
            .filter(Q(rank__gte=0.1) | Q(similarity__gte=0.3))
        )

    # 카테고리 필터
    if category_id is not None:
        qs = qs.filter(category_id=category_id)

    # 가격 범위 필터 (idx_product_status_price, idx_product_active_price 활용)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    # 태그 필터 (idx_product_tags_gin 활용)
    if tags:
        qs = qs.filter(tags__overlap=tags)

    # JSON 속성 포함 필터 (idx_product_attrs_gin 활용)
    if required_attrs:
        qs = qs.filter(attributes__contains=required_attrs)

    # JSON 키 존재 필터
    if attr_key_exists:
        qs = qs.filter(attributes__has_key=attr_key_exists)

    # 정렬: 검색어가 있으면 관련성 순, 없으면 최신순
    if query_text:
        qs = qs.order_by("-final_score")
    else:
        qs = qs.order_by("-created_at")

    return qs
```

### 사용 예시

```python
# "삼성 갤럭시" 검색, 가격 50만~150만, 검정색, "신상품" 태그 포함
results = product_catalog_search(
    query_text="삼성 갤럭시",
    min_price=Decimal("500000"),
    max_price=Decimal("1500000"),
    tags=["신상품"],
    required_attrs={"color": "black"},
)

# 전자제품 카테고리에서 무게 속성이 있는 상품
results = product_catalog_search(
    category_id=1,
    attr_key_exists="weight",
)

# 태그 기반 추천 상품 조회
results = product_catalog_search(
    tags=["추천", "베스트"],
    max_price=Decimal("100000"),
)
```
