# D05: Cross-Skill Delegation -- implementation-django-ninja -> implementation-django

## Prompt
"Ninja Router에서 쓸 Django 모델이랑 QuerySet Manager를 설계하고 싶은데, 모델 쪽은 어떻게 잡아야 해?"

## Skill
`implementation-django-ninja` (source) -> `implementation-django` (delegated)

## Response

Ninja Router에서 사용할 모델과 QuerySet Manager 설계는 **implementation-django** 스킬의 영역이다. Django Ninja 스킬은 Router/Schema/인증 같은 API 레이어를 다루고, 모델/ORM/QuerySet은 Django 코어 스킬에 위임한다. 아래는 Ninja Router와 잘 맞물리도록 모델 쪽을 잡는 패턴이다.

### 1. 모델 필드 순서 규칙

Django 공식 컨벤션에 따라 필드를 배치한다. Ninja의 `ModelSchema`가 `Meta.fields`로 필드를 참조하므로, 일관된 순서가 Schema 설계와 코드 리뷰를 쉽게 만든다.

```python
class Product(TimeStampedModel):
    # --- DB 필드 ---
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.DRAFT,
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    tags = models.ManyToManyField("tags.Tag", blank=True)

    # --- Managers ---
    objects = ProductQuerySet.as_manager()

    # --- Meta ---
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="product_price_non_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

    # --- __str__ ---
    def __str__(self):
        return self.name

    # --- save/delete ---
    def clean(self):
        if self.status == self.Status.ACTIVE and not self.description:
            raise ValidationError(
                {"description": "Active 상품은 설명이 필수입니다."}
            )

    # --- 커스텀 메서드 (비즈니스 로직) ---
    def archive(self):
        self.status = self.Status.ARCHIVED
        self.save(update_fields=["status", "updated_at"])
```

핵심 포인트:
- `TextChoices`로 상태를 관리한다. BooleanField 남발을 피한다.
- `DecimalField`를 금액에 사용한다. `FloatField`는 피한다.
- `clean()` + `CheckConstraint`로 Python/DB 이중 검증을 건다.
- 비즈니스 로직은 모델 메서드에 둔다 (Fat Model, Thin View).
- `save(update_fields=...)`로 변경된 필드만 업데이트한다.

### 2. Custom QuerySet -- Ninja Router 엔드포인트와 연결

커스텀 QuerySet 메서드를 정의하면 Router 엔드포인트에서 체이닝으로 간결하게 호출할 수 있다.

```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status="active")

    def by_category(self, category_slug):
        return self.filter(category__slug=category_slug)

    def with_review_stats(self):
        return self.annotate(
            review_count=Count("reviews"),
            avg_rating=Avg("reviews__rating"),
        )

    def for_list(self):
        """목록 API에 최적화된 QuerySet."""
        return (
            self.select_related("category")
            .prefetch_related("tags")
            .only(
                "id", "name", "slug", "price", "status",
                "category__id", "category__name",
                "created_at",
            )
        )

    def for_detail(self):
        """상세 API에 최적화된 QuerySet."""
        return (
            self.select_related("category")
            .prefetch_related(
                "tags",
                Prefetch(
                    "reviews",
                    queryset=Review.objects.order_by("-created_at")[:5],
                    to_attr="recent_reviews",
                ),
            )
        )
```

Router 엔드포인트에서의 사용:

```python
# products/api.py
from ninja import Router

router = Router(tags=["products"])

@router.get("/", response=list[ProductListSchema])
@paginate
def list_products(request, filters: Query[ProductFilterSchema]):
    return Product.objects.active().for_list().filter(**filters.dict())

@router.get("/{slug}", response=ProductDetailSchema)
def get_product(request, slug: str):
    return get_object_or_404(Product.objects.for_detail(), slug=slug)
```

핵심 포인트:
- `for_list()`, `for_detail()` 같은 목적별 QuerySet 메서드를 만든다.
- `select_related()`는 FK/O2O, `prefetch_related()`는 M2M/역참조에 사용한다.
- `as_manager()`로 별도 Manager 클래스 없이 QuerySet을 매니저로 승격한다.
- 엔드포인트에서 QuerySet 최적화 로직을 반복하지 않고, 한 곳에서 관리한다.

### 3. Abstract Base Class로 공통 필드 추출

여러 모델이 Ninja Schema에서 동일한 필드를 노출할 때, ABC로 공통 필드를 추출한다.

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
```

- 다중 테이블 상속을 피한다. ABC + 명시적 FK를 선호한다.
- 공통 필드가 있으면 대응하는 Ninja `ModelSchema`에서도 `Meta.fields`를 일관되게 유지할 수 있다.

### 4. ModelSchema와 모델의 연결

모델을 잘 설계하면 Ninja `ModelSchema`가 깔끔하게 따라온다.

```python
from ninja import ModelSchema

class ProductListSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price", "status", "created_at"]

class ProductDetailSchema(ModelSchema):
    category_name: str
    review_count: int = 0
    avg_rating: float = 0.0

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "status", "created_at"]

    @staticmethod
    def resolve_category_name(obj):
        return obj.category.name
```

- `fields = '__all__'`은 사용하지 않는다. 노출할 필드를 명시한다.
- `annotate()`로 추가한 필드는 Schema에서 기본값과 함께 선언한다.
- `resolve_<field>`로 관계 데이터를 계산 필드로 노출한다.

---
> **관련 스킬 참조:**
> - [Router 구성과 엔드포인트 데코레이터 패턴] -> **implementation-django-ninja** 스킬
> - [FilterSchema로 타입 안전한 필터링 구현] -> **implementation-django-ninja** 스킬
> - [고급 ORM 표현식 (Subquery, Window, Case/When)] -> **implementation-django** 스킬
> - [DB 정규화와 인덱스 아키텍처 설계] -> **architecture-db** 스킬
> - [서비스 레이어 분리 시점과 패턴] -> **implementation-django** 스킬
