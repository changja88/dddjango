# Django Ninja API를 위한 QuerySet 최적화와 Custom Manager 패턴

## 1. Custom QuerySet + Manager 정의

QuerySet 메서드를 정의하면 체이닝이 가능한 재사용 가능한 쿼리 단위를 만들 수 있다. Manager는 모델에서 QuerySet으로 진입하는 인터페이스 역할을 한다.

```python
# articles/models.py
from django.db import models
from django.db.models import Count, Prefetch


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")

    def by_author(self, user):
        return self.filter(author=user)

    def recent(self):
        return self.order_by("-published_at")

    def with_author(self):
        return self.select_related("author")

    def with_tags(self):
        return self.prefetch_related("tags")

    def with_top_reviews(self):
        return self.prefetch_related(
            Prefetch(
                "reviews",
                queryset=Review.objects.filter(rating__gte=4).order_by("-created_at"),
                to_attr="top_reviews",
            )
        )

    def with_review_count(self):
        return self.annotate(review_count=Count("reviews"))

    def for_list(self):
        """목록 API에서 사용하는 표준 조합."""
        return self.published().with_author().with_tags().recent()

    def for_detail(self):
        """상세 API에서 사용하는 표준 조합."""
        return self.with_author().with_tags().with_top_reviews()


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=20)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="articles")
    category = models.ForeignKey("categories.Category", on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField("tags.Tag", blank=True)
    published_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ArticleManager()

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
```

두 가지 방식 중 선택한다.

| 방식 | 사용 시점 |
|------|----------|
| `Manager` + `QuerySet` 분리 | Manager에서 `get_queryset()`을 오버라이드해 기본 필터를 적용하거나, Manager 전용 메서드가 필요할 때 |
| `QuerySet.as_manager()` | 별도 Manager 로직 없이 QuerySet 메서드만 노출하면 충분할 때 |

`as_manager()` 방식으로 간결하게 작성하면 다음과 같다.

```python
class Article(models.Model):
    # ...필드 생략...

    objects = ArticleQuerySet.as_manager()
```

## 2. select_related / prefetch_related 선택 기준

| 관계 유형 | 사용할 메서드 | 동작 |
|-----------|-------------|------|
| ForeignKey, OneToOneField | `select_related()` | SQL JOIN으로 한 번에 가져옴 |
| ManyToManyField, 역참조 ForeignKey | `prefetch_related()` | 별도 쿼리 후 Python에서 조인 |
| 조건부 프리페치 (필터, 정렬, 제한) | `Prefetch()` 객체 | 커스텀 QuerySet으로 프리페치 |

```python
# ForeignKey/OneToOne -> select_related (SQL JOIN)
Article.objects.select_related("author", "category")

# ManyToMany/역참조 -> prefetch_related (별도 쿼리)
Article.objects.prefetch_related("tags")

# 조건부 프리페치 -> Prefetch 객체
from django.db.models import Prefetch

Article.objects.prefetch_related(
    Prefetch(
        "reviews",
        queryset=Review.objects.filter(rating__gte=4).order_by("-created_at"),
        to_attr="top_reviews",
    )
)
```

## 3. Django Ninja API에서 최적화된 QuerySet 사용

QuerySet 메서드를 엔드포인트에서 직접 호출하여 N+1 문제를 방지한다.

### Schema 정의

```python
# articles/schemas.py
from ninja import ModelSchema, Schema

from articles.models import Article


class AuthorOut(Schema):
    id: int
    username: str


class TagOut(Schema):
    id: int
    name: str


class ArticleListOut(ModelSchema):
    author: AuthorOut
    tags: list[TagOut]

    class Meta:
        model = Article
        fields = ["id", "title", "status", "published_at"]


class ReviewOut(Schema):
    id: int
    rating: int
    comment: str


class ArticleDetailOut(ModelSchema):
    author: AuthorOut
    tags: list[TagOut]
    top_reviews: list[ReviewOut]

    class Meta:
        model = Article
        fields = ["id", "title", "body", "status", "published_at", "created_at"]

    @staticmethod
    def resolve_top_reviews(obj):
        return getattr(obj, "top_reviews", [])
```

### Router 엔드포인트

```python
# articles/api.py
from ninja import Router
from ninja.pagination import paginate, LimitOffsetPagination

from articles.models import Article
from articles.schemas import ArticleListOut, ArticleDetailOut

router = Router(tags=["articles"])


@router.get("/", response=list[ArticleListOut])
@paginate(LimitOffsetPagination)
def list_articles(request):
    return Article.objects.for_list()


@router.get("/{int:article_id}", response=ArticleDetailOut)
def get_article(request, article_id: int):
    return get_object_or_404(Article.objects.for_detail(), id=article_id)


@router.get("/by-author/{int:author_id}", response=list[ArticleListOut])
@paginate(LimitOffsetPagination)
def list_by_author(request, author_id: int):
    return Article.objects.for_list().by_author_id(author_id)
```

핵심 포인트:

- **QuerySet 메서드를 엔드포인트에서 직접 호출한다.** `for_list()`, `for_detail()` 같은 조합 메서드를 QuerySet에 정의하면, 엔드포인트 코드에서 최적화 로직을 반복하지 않는다.
- **Schema의 중첩 객체는 `select_related`/`prefetch_related`로 미리 로드한다.** `AuthorOut`을 중첩 Schema로 선언했으면, QuerySet에서 `select_related("author")`가 반드시 필요하다. 그렇지 않으면 각 객체마다 추가 쿼리가 발생하는 N+1 문제가 생긴다.
- **`Prefetch(to_attr=...)`로 가져온 데이터는 `resolve_` 메서드로 연결한다.** `to_attr`은 일반 역참조 매니저가 아닌 Python 리스트를 모델 인스턴스에 직접 붙이므로, Schema에서 `resolve_top_reviews`로 접근한다.

## 4. 용도별 QuerySet 조합 메서드 패턴

같은 모델이라도 API 엔드포인트마다 필요한 관련 데이터가 다르다. QuerySet에 용도별 조합 메서드를 정의하면 각 엔드포인트에서 최적의 쿼리를 일관되게 사용할 수 있다.

```python
class ArticleQuerySet(models.QuerySet):
    # --- 기본 필터 ---
    def published(self):
        return self.filter(status="published")

    def by_author(self, user):
        return self.filter(author=user)

    # --- 관계 로딩 ---
    def with_author(self):
        return self.select_related("author")

    def with_category(self):
        return self.select_related("category")

    def with_tags(self):
        return self.prefetch_related("tags")

    def with_top_reviews(self):
        return self.prefetch_related(
            Prefetch(
                "reviews",
                queryset=Review.objects.filter(rating__gte=4).order_by("-created_at"),
                to_attr="top_reviews",
            )
        )

    # --- 용도별 조합 ---
    def for_list(self):
        return self.published().with_author().with_tags().order_by("-published_at")

    def for_detail(self):
        return self.with_author().with_category().with_tags().with_top_reviews()

    def for_admin(self):
        return self.with_author().with_category().with_tags().annotate(
            review_count=Count("reviews")
        )
```

이 패턴의 장점:

- **엔드포인트 코드가 간결해진다.** `Article.objects.for_list()`만 호출하면 필터링, 관계 로딩, 정렬이 모두 적용된다.
- **최적화가 한 곳에 집중된다.** 새로운 관계가 추가되면 QuerySet 메서드만 수정하면 모든 엔드포인트에 반영된다.
- **체이닝이 가능하다.** `Article.objects.for_list().by_author(user)`처럼 추가 필터를 자유롭게 조합할 수 있다.

## 5. annotate와 Schema resolver 연동

DB 수준에서 계산한 값을 Schema에 노출할 때는 `annotate()`와 `resolve_` 메서드를 조합한다.

```python
# models.py QuerySet 메서드
class ArticleQuerySet(models.QuerySet):
    def with_stats(self):
        return self.annotate(
            review_count=Count("reviews"),
            avg_rating=Avg("reviews__rating"),
        )
```

```python
# schemas.py
class ArticleStatsOut(ModelSchema):
    review_count: int
    avg_rating: float | None

    class Meta:
        model = Article
        fields = ["id", "title"]

    @staticmethod
    def resolve_review_count(obj):
        return getattr(obj, "review_count", 0)

    @staticmethod
    def resolve_avg_rating(obj):
        return getattr(obj, "avg_rating", None)
```

```python
# api.py
@router.get("/stats", response=list[ArticleStatsOut])
@paginate(LimitOffsetPagination)
def list_article_stats(request):
    return Article.objects.published().with_stats()
```

---

Django 모델 설계, 필드 순서, 검증 패턴에 대한 자세한 안내는 **implementation-django** 스킬을 참조하세요.

Schema 정의, ModelSchema, resolver 메서드, PatchDict 등 Django Ninja Schema 관련 상세 패턴은 **implementation-django-ninja** 스킬을 참조하세요.

페이지네이션 전략, FilterSchema를 사용한 타입 안전한 필터링에 대한 자세한 안내는 **implementation-django-ninja** 스킬을 참조하세요.

데이터베이스 인덱스 설계, 정규화 원칙 등 일반 RDB 설계에 대한 자세한 안내는 **architecture-db** 스킬을 참조하세요.
