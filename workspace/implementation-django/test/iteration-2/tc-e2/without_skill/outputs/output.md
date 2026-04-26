# Django 상품 카탈로그 - PostgreSQL 기능 활용

## 1. 모델 정의

```python
# catalog/models.py

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex, BrinIndex, OpClass
from django.utils import timezone


class Category(models.Model):
    """상품 카테고리. 카테고리마다 동적 속성 스키마가 다를 수 있다."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    # 이 카테고리에 속하는 상품이 가져야 할 속성 스키마 정의
    # 예: {"color": "string", "size": "string", "weight": "number"}
    attribute_schema = models.JSONField(
        default=dict,
        blank=True,
        help_text="이 카테고리 상품의 동적 속성 스키마 정의",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    상품 모델.
    - attributes: JSONField로 카테고리별 동적 속성 저장
    - tags: ArrayField로 태그 배열 저장
    - search_vector: SearchVectorField로 전문 검색 인덱스 저장
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)

    # --- PostgreSQL 전용 필드 ---

    # 동적 속성: 카테고리마다 다른 속성을 유연하게 저장
    # 예: {"color": "red", "size": "XL", "weight": 1.5}
    attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="카테고리별 동적 속성 (색상, 크기, 무게 등)",
    )

    # 태그 배열
    tags = ArrayField(
        base_field=models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="상품 태그 목록",
    )

    # 전문 검색 벡터 (title + description 기반, 트리거로 자동 갱신)
    search_vector = SearchVectorField(null=True, editable=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # --- GIN 인덱스 ---
            # 전문 검색 벡터에 대한 GIN 인덱스
            GinIndex(
                fields=["search_vector"],
                name="idx_product_search_vector",
            ),
            # JSONField에 대한 GIN 인덱스 (contains, has_key 쿼리 가속)
            GinIndex(
                fields=["attributes"],
                name="idx_product_attributes_gin",
            ),
            # ArrayField에 대한 GIN 인덱스 (overlap, contains 쿼리 가속)
            GinIndex(
                fields=["tags"],
                name="idx_product_tags_gin",
            ),
            # Trigram 검색을 위한 GIN 인덱스 (pg_trgm 확장 필요)
            # 아래 migration에서 별도로 생성
            # --- BRIN 인덱스 ---
            # 시계열 데이터인 created_at에 BRIN 인덱스 (디스크 공간 효율적)
            BrinIndex(
                fields=["created_at"],
                name="idx_product_created_brin",
            ),
            # --- B-tree 인덱스 ---
            models.Index(
                fields=["price"],
                name="idx_product_price",
            ),
            models.Index(
                fields=["category", "is_active"],
                name="idx_product_category_active",
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # search_vector 갱신은 DB 트리거로 처리하는 것이 성능상 유리하지만,
        # 애플리케이션 레벨에서도 갱신 가능 (아래 update_search_vector 참고)

    @classmethod
    def update_search_vector(cls, product_ids=None):
        """search_vector 필드를 수동으로 갱신한다."""
        from django.contrib.postgres.search import SearchVector

        qs = cls.objects.all()
        if product_ids:
            qs = qs.filter(id__in=product_ids)

        qs.update(
            search_vector=(
                SearchVector("title", weight="A", config="simple")
                + SearchVector("description", weight="B", config="simple")
            )
        )
```

## 2. 마이그레이션 - PostgreSQL 확장 및 Trigram 인덱스

```python
# catalog/migrations/0002_extensions_and_trigram_index.py

from django.db import migrations


class Migration(migrations.Migration):
    """
    PostgreSQL 확장 활성화 및 Trigram 인덱스 생성.
    pg_trgm: 오타 허용 유사도 검색
    btree_gin: B-tree 타입을 GIN 인덱스에 포함 가능
    """

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        # 필요한 PostgreSQL 확장 활성화
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        ),
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS btree_gin;",
            reverse_sql="DROP EXTENSION IF EXISTS btree_gin;",
        ),
        # title에 Trigram GIN 인덱스 (오타 허용 검색)
        migrations.RunSQL(
            sql="""
                CREATE INDEX idx_product_title_trgm
                ON catalog_product
                USING gin (title gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_product_title_trgm;",
        ),
        # description에 Trigram GIN 인덱스
        migrations.RunSQL(
            sql="""
                CREATE INDEX idx_product_description_trgm
                ON catalog_product
                USING gin (description gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_product_description_trgm;",
        ),
        # search_vector 자동 갱신 트리거
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION product_search_vector_update()
                RETURNS trigger AS $$
                BEGIN
                    NEW.search_vector :=
                        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
                        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'B');
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER trg_product_search_vector_update
                BEFORE INSERT OR UPDATE OF title, description
                ON catalog_product
                FOR EACH ROW
                EXECUTE FUNCTION product_search_vector_update();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS trg_product_search_vector_update ON catalog_product;
                DROP FUNCTION IF EXISTS product_search_vector_update();
            """,
        ),
    ]
```

## 3. 검색 쿼리 (SearchVector + SearchQuery + SearchRank + TrigramSimilarity)

```python
# catalog/queries.py

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
    TrigramWordSimilarity,
)
from django.db.models import F, Q, Value
from django.db.models.functions import Greatest

from .models import Product


# ──────────────────────────────────────────────
# 3-1. 기본 Full-Text Search (SearchVector + SearchQuery + SearchRank)
# ──────────────────────────────────────────────

def fulltext_search(query_text: str, min_rank: float = 0.1):
    """
    title(가중치 A)과 description(가중치 B)을 대상으로 전문 검색한다.
    search_vector 필드에 미리 저장된 인덱스를 활용한다.

    사용 예: fulltext_search("무선 이어폰")
    """
    search_query = SearchQuery(query_text, config="simple")

    return (
        Product.objects
        .filter(search_vector=search_query)
        .annotate(rank=SearchRank(F("search_vector"), search_query))
        .filter(rank__gte=min_rank)
        .order_by("-rank")
    )


# ──────────────────────────────────────────────
# 3-2. Trigram 유사도 검색 (오타 허용)
# ──────────────────────────────────────────────

def trigram_search(query_text: str, min_similarity: float = 0.3):
    """
    Trigram 유사도를 사용한 오타 허용 검색.
    사용자가 "이어폰" 대신 "이어본"을 입력해도 결과를 반환한다.

    사용 예: trigram_search("이어본")  # 오타 허용
    """
    return (
        Product.objects
        .annotate(
            title_similarity=TrigramSimilarity("title", query_text),
            desc_similarity=TrigramSimilarity("description", query_text),
            similarity=Greatest(
                "title_similarity",
                "desc_similarity",
            ),
        )
        .filter(similarity__gte=min_similarity)
        .order_by("-similarity")
    )


def trigram_word_search(query_text: str, min_similarity: float = 0.3):
    """
    TrigramWordSimilarity는 긴 텍스트 내 단어 단위 유사도를 측정한다.
    description처럼 긴 텍스트에서 부분 매칭에 유리하다.

    사용 예: trigram_word_search("블루투스 스피커")
    """
    return (
        Product.objects
        .annotate(
            similarity=TrigramWordSimilarity(query_text, "title"),
        )
        .filter(similarity__gte=min_similarity)
        .order_by("-similarity")
    )


# ──────────────────────────────────────────────
# 3-3. 하이브리드 검색 (Full-Text + Trigram 결합)
# ──────────────────────────────────────────────

def hybrid_search(
    query_text: str,
    min_rank: float = 0.05,
    min_similarity: float = 0.2,
    rank_weight: float = 0.7,
    similarity_weight: float = 0.3,
):
    """
    Full-Text Search와 Trigram을 결합한 하이브리드 검색.
    - 정확한 키워드 매칭은 SearchRank로 처리
    - 오타/유사어는 TrigramSimilarity로 처리
    - 두 점수를 가중 합산하여 최종 순위 결정

    사용 예: hybrid_search("무선 이어본")  # 정확 매칭 + 오타 허용
    """
    search_query = SearchQuery(query_text, config="simple")

    return (
        Product.objects
        .annotate(
            rank=SearchRank(F("search_vector"), search_query),
            similarity=Greatest(
                TrigramSimilarity("title", query_text),
                TrigramSimilarity("description", query_text),
            ),
            # 가중 합산 점수
            combined_score=(
                Value(rank_weight) * F("rank")
                + Value(similarity_weight) * F("similarity")
            ),
        )
        .filter(
            Q(rank__gte=min_rank) | Q(similarity__gte=min_similarity)
        )
        .order_by("-combined_score")
    )


# ──────────────────────────────────────────────
# 3-4. 가격 범위 필터
# ──────────────────────────────────────────────

def filter_by_price(queryset=None, min_price=None, max_price=None):
    """
    가격 범위로 필터링한다. B-tree 인덱스를 활용한다.

    사용 예:
        filter_by_price(min_price=10000, max_price=50000)
        filter_by_price(queryset=some_qs, min_price=10000)
    """
    if queryset is None:
        queryset = Product.objects.all()

    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)
    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)

    return queryset


# ──────────────────────────────────────────────
# 4. JSON 필터 쿼리 (contains, has_key)
# ──────────────────────────────────────────────

def filter_by_attributes_contains(attributes_filter: dict):
    """
    JSONField의 contains 조회. GIN 인덱스를 활용한다.
    주어진 key-value 쌍이 모두 포함된 상품을 반환한다.

    사용 예:
        # 색상이 red이고 크기가 XL인 상품
        filter_by_attributes_contains({"color": "red", "size": "XL"})
    """
    return Product.objects.filter(attributes__contains=attributes_filter)


def filter_by_attribute_has_key(key: str):
    """
    JSONField에 특정 key가 존재하는 상품을 필터링한다.

    사용 예:
        # 'weight' 속성이 존재하는 상품
        filter_by_attribute_has_key("weight")
    """
    return Product.objects.filter(attributes__has_key=key)


def filter_by_attribute_has_keys(keys: list[str]):
    """
    JSONField에 지정된 key가 모두 존재하는 상품을 필터링한다.

    사용 예:
        # 'color'와 'size' 속성이 모두 존재하는 상품
        filter_by_attribute_has_keys(["color", "size"])
    """
    return Product.objects.filter(attributes__has_keys=keys)


def filter_by_attribute_has_any_keys(keys: list[str]):
    """
    JSONField에 지정된 key 중 하나라도 존재하는 상품을 필터링한다.

    사용 예:
        # 'color' 또는 'material' 속성 중 하나라도 있는 상품
        filter_by_attribute_has_any_keys(["color", "material"])
    """
    return Product.objects.filter(attributes__has_any_keys=keys)


def filter_by_attribute_value(key: str, value):
    """
    JSONField의 중첩 키 조회. Django의 __ 룩업을 사용한다.

    사용 예:
        # 색상이 "red"인 상품
        filter_by_attribute_value("color", "red")

        # 무게가 1.5 이하인 상품 (숫자 비교는 RawSQL 필요)
        filter_by_attribute_value("color", "blue")
    """
    lookup = f"attributes__{key}"
    return Product.objects.filter(**{lookup: value})


def filter_by_nested_attribute(path: list[str], value):
    """
    JSONField의 깊은 중첩 경로를 조회한다.

    사용 예:
        # attributes = {"dimensions": {"width": 10, "height": 20}}
        # width가 10인 상품 조회
        filter_by_nested_attribute(["dimensions", "width"], 10)
    """
    lookup = "attributes__" + "__".join(path)
    return Product.objects.filter(**{lookup: value})


# ──────────────────────────────────────────────
# 5. 태그 필터 쿼리 (overlap, contains)
# ──────────────────────────────────────────────

def filter_by_tags_contains(tags: list[str]):
    """
    ArrayField의 contains 조회. 지정된 태그를 모두 포함하는 상품을 반환한다.
    GIN 인덱스를 활용한다.

    사용 예:
        # "신상품"과 "할인" 태그가 모두 있는 상품
        filter_by_tags_contains(["신상품", "할인"])
    """
    return Product.objects.filter(tags__contains=tags)


def filter_by_tags_overlap(tags: list[str]):
    """
    ArrayField의 overlap 조회. 지정된 태그 중 하나라도 포함하는 상품을 반환한다.
    GIN 인덱스를 활용한다.

    사용 예:
        # "신상품" 또는 "인기" 태그 중 하나라도 있는 상품
        filter_by_tags_overlap(["신상품", "인기"])
    """
    return Product.objects.filter(tags__overlap=tags)


def filter_by_tags_contained_by(tags: list[str]):
    """
    ArrayField의 contained_by 조회. 상품의 태그가 주어진 목록의 부분집합인 경우 반환.

    사용 예:
        # 태그가 ["신상품", "할인", "인기"] 중에서만 구성된 상품
        filter_by_tags_contained_by(["신상품", "할인", "인기"])
    """
    return Product.objects.filter(tags__contained_by=tags)


def filter_by_tag_length(min_count: int = None, max_count: int = None):
    """
    태그 개수로 필터링한다.

    사용 예:
        # 태그가 3개 이상인 상품
        filter_by_tag_length(min_count=3)
    """
    from django.db.models.functions import Coalesce
    from django.contrib.postgres.fields import ArrayField

    qs = Product.objects.annotate(tag_count=models.Func(F("tags"), function="array_length", template="%(function)s(%(expressions)s, 1)"))
    if min_count is not None:
        qs = qs.filter(tag_count__gte=min_count)
    if max_count is not None:
        qs = qs.filter(tag_count__lte=max_count)
    return qs


# ──────────────────────────────────────────────
# 종합 검색 함수: 모든 필터를 조합
# ──────────────────────────────────────────────

def catalog_search(
    query_text: str = None,
    category_slug: str = None,
    min_price=None,
    max_price=None,
    attributes_filter: dict = None,
    required_attribute_keys: list[str] = None,
    tags_all: list[str] = None,
    tags_any: list[str] = None,
    use_trigram: bool = True,
    min_rank: float = 0.05,
    min_similarity: float = 0.2,
    only_active: bool = True,
):
    """
    여러 필터를 조합한 종합 검색 함수.

    사용 예:
        results = catalog_search(
            query_text="무선 이어본",          # 오타 허용 검색
            category_slug="electronics",
            min_price=10000,
            max_price=100000,
            attributes_filter={"color": "black"},
            tags_any=["신상품", "인기"],
            use_trigram=True,
        )
    """
    qs = Product.objects.all()

    # 활성 상품만
    if only_active:
        qs = qs.filter(is_active=True)

    # 카테고리 필터
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    # 가격 범위 필터 (B-tree 인덱스 활용)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)

    # JSON 속성 필터 (GIN 인덱스 활용)
    if attributes_filter:
        qs = qs.filter(attributes__contains=attributes_filter)
    if required_attribute_keys:
        qs = qs.filter(attributes__has_keys=required_attribute_keys)

    # 태그 필터 (GIN 인덱스 활용)
    if tags_all:
        qs = qs.filter(tags__contains=tags_all)
    if tags_any:
        qs = qs.filter(tags__overlap=tags_any)

    # 텍스트 검색 (Full-Text + Trigram)
    if query_text:
        search_query = SearchQuery(query_text, config="simple")
        qs = qs.annotate(
            rank=SearchRank(F("search_vector"), search_query),
        )
        if use_trigram:
            qs = qs.annotate(
                similarity=Greatest(
                    TrigramSimilarity("title", query_text),
                    TrigramSimilarity("description", query_text),
                ),
                combined_score=(
                    Value(0.7) * F("rank") + Value(0.3) * F("similarity")
                ),
            )
            qs = qs.filter(
                Q(rank__gte=min_rank) | Q(similarity__gte=min_similarity)
            )
            qs = qs.order_by("-combined_score")
        else:
            qs = qs.filter(rank__gte=min_rank)
            qs = qs.order_by("-rank")

    return qs
```

## 인덱스 설계 요약

| 인덱스 | 타입 | 대상 필드 | 용도 |
|---|---|---|---|
| `idx_product_search_vector` | GIN | `search_vector` | Full-Text Search (`tsvector` 매칭) |
| `idx_product_attributes_gin` | GIN | `attributes` | JSON `contains`, `has_key` 조회 |
| `idx_product_tags_gin` | GIN | `tags` | 배열 `overlap`, `contains` 조회 |
| `idx_product_title_trgm` | GIN (trgm) | `title` | Trigram 유사도 검색 (오타 허용) |
| `idx_product_description_trgm` | GIN (trgm) | `description` | Trigram 유사도 검색 (오타 허용) |
| `idx_product_created_brin` | BRIN | `created_at` | 시간순 범위 스캔 (공간 효율적) |
| `idx_product_price` | B-tree | `price` | 가격 범위 필터 |
| `idx_product_category_active` | B-tree | `category`, `is_active` | 카테고리 + 활성 상태 복합 필터 |

## settings.py 설정

```python
# settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "catalog_db",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

INSTALLED_APPS = [
    # ...
    "django.contrib.postgres",  # PostgreSQL 전용 필드/함수 사용에 필요
    "catalog",
]
```

## 사용 예시

```python
from catalog.queries import (
    fulltext_search,
    trigram_search,
    hybrid_search,
    filter_by_price,
    filter_by_attributes_contains,
    filter_by_attribute_has_key,
    filter_by_tags_contains,
    filter_by_tags_overlap,
    catalog_search,
)

# ---- Full-Text Search ----
results = fulltext_search("무선 블루투스 이어폰")
# SQL: WHERE search_vector @@ plainto_tsquery('simple', '무선 블루투스 이어폰')
#      ORDER BY ts_rank(search_vector, ...) DESC

# ---- Trigram 오타 허용 검색 ----
results = trigram_search("이어본")  # "이어폰"의 오타
# SQL: WHERE similarity(title, '이어본') >= 0.3
#         OR similarity(description, '이어본') >= 0.3

# ---- 하이브리드 검색 ----
results = hybrid_search("무선 이어본")
# Full-Text rank + Trigram similarity 가중 합산

# ---- 가격 범위 필터 ----
results = filter_by_price(min_price=10000, max_price=50000)
# SQL: WHERE price >= 10000 AND price <= 50000

# ---- JSON 필터: contains ----
results = filter_by_attributes_contains({"color": "red", "size": "XL"})
# SQL: WHERE attributes @> '{"color": "red", "size": "XL"}'::jsonb

# ---- JSON 필터: has_key ----
results = filter_by_attribute_has_key("weight")
# SQL: WHERE attributes ? 'weight'

# ---- 태그 필터: contains (모두 포함) ----
results = filter_by_tags_contains(["신상품", "할인"])
# SQL: WHERE tags @> ARRAY['신상품', '할인']

# ---- 태그 필터: overlap (하나라도 포함) ----
results = filter_by_tags_overlap(["신상품", "인기"])
# SQL: WHERE tags && ARRAY['신상품', '인기']

# ---- 종합 검색 ----
results = catalog_search(
    query_text="무선 이어본",
    category_slug="electronics",
    min_price=10000,
    max_price=100000,
    attributes_filter={"color": "black"},
    tags_any=["신상품", "인기"],
    use_trigram=True,
)
```
