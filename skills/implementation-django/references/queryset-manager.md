# QuerySet과 Manager 패턴

## Custom Manager와 QuerySet [DDoc] [TSD]

```python
class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")

    def by_author(self, user):
        return self.filter(author=user)

    def recent(self):
        return self.order_by("-published_at")


class ArticleManager(models.Manager):
    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True)

    # 방법 1: Manager + QuerySet 분리
    objects = ArticleManager()

    # 방법 2: QuerySet.as_manager() 사용 (더 간결)
    # objects = PublishedQuerySet.as_manager()
```

- **QuerySet 메서드로 체이닝을 가능하게 한다**: `Article.objects.published().by_author(user).recent()`
- `as_manager()`를 사용하면 별도의 Manager 클래스 없이 QuerySet을 매니저로 승격시킬 수 있다.
- Manager에서 `get_queryset()`을 오버라이드하여 기본 필터를 적용할 때는 주의한다 -- 관리자 페이지에서 예상과 다르게 동작할 수 있다.

## QuerySet 최적화 필수 패턴 [DDoc]

```python
# 나쁜 예: N+1 문제 -- 각 book마다 author를 별도 쿼리
books = Book.objects.all()
for book in books:
    print(book.author.name)  # N번의 추가 쿼리

# 좋은 예: select_related -- ForeignKey/OneToOne에 SQL JOIN 사용
books = Book.objects.select_related("author").all()
for book in books:
    print(book.author.name)  # 추가 쿼리 없음 (1번의 JOIN 쿼리)

# 좋은 예: prefetch_related -- ManyToMany/역참조에 별도 쿼리 + Python 조인
books = Book.objects.prefetch_related("tags").all()
for book in books:
    print(list(book.tags.all()))  # 2번의 쿼리 (books + tags IN (...))

# 좋은 예: Prefetch 객체로 커스텀 쿼리셋 사용
from django.db.models import Prefetch

books = Book.objects.prefetch_related(
    Prefetch(
        "reviews",
        queryset=Review.objects.filter(rating__gte=4).order_by("-created_at"),
        to_attr="top_reviews",  # list로 캐싱
    )
)
```

**선택 기준:**
| 관계 유형 | 사용할 메서드 |
|-----------|--------------|
| ForeignKey, OneToOneField | `select_related()` |
| ManyToManyField, 역참조 ForeignKey | `prefetch_related()` |
| 조건부 프리페치 | `Prefetch()` 객체 |

## only(), defer(), values() [DDoc]

```python
# only(): 지정한 필드만 로드 (나머지는 지연 로드)
users = User.objects.only("id", "username", "email")

# defer(): 지정한 필드를 지연 로드 (나머지는 즉시 로드)
articles = Article.objects.defer("body")  # 큰 텍스트 필드 지연

# values(): 딕셔너리 리스트 반환 (모델 인스턴스가 아님)
stats = Order.objects.values("status").annotate(count=Count("id"))

# values_list(): 튜플 리스트 반환
emails = User.objects.values_list("email", flat=True)
```

- `only()`/`defer()`는 대용량 텍스트나 변환 비용이 큰 필드에 효과적이다.
- **프로파일링 없이 공격적으로 사용하지 않는다** -- DB는 대부분의 비텍스트 데이터를 어차피 디스크에서 읽는다. [DDoc]

## annotate()와 aggregate() [DDoc]

```python
from django.db.models import Count, Avg, F, Q

# aggregate(): 전체 QuerySet에 대한 집계값 반환 (딕셔너리)
result = Book.objects.aggregate(
    avg_price=Avg("price"),
    total=Count("id"),
)

# annotate(): 각 객체에 계산 필드 추가
authors = Author.objects.annotate(
    book_count=Count("book"),
    avg_rating=Avg("book__reviews__rating"),
).filter(book_count__gte=5)

# alias(): 최종 결과에 포함하지 않으면서 필터/정렬에 사용 (Django 3.2+)
authors = Author.objects.alias(
    book_count=Count("book"),
).filter(book_count__gte=5)
```

- `annotate()`와 `filter()`의 순서가 결과에 영향을 준다 -- 교환 법칙이 성립하지 않는다.
- 최종 결과에 불필요한 계산 필드가 있으면 `alias()`를 사용하여 DB 부담을 줄인다.

## bulk 연산 [DDoc]

```python
# 나쁜 예: 루프 내에서 개별 save()
for item in items:
    item.price *= 1.1
    item.save()  # N번의 UPDATE

# 좋은 예: bulk_update()
for item in items:
    item.price *= 1.1
Product.objects.bulk_update(items, ["price"], batch_size=500)

# 좋은 예: bulk_create()
Product.objects.bulk_create(
    [Product(name=name) for name in product_names],
    batch_size=500,
)

# 좋은 예: update()로 DB 레벨 일괄 수정
Product.objects.filter(category="books").update(
    price=F("price") * 1.1
)
```
