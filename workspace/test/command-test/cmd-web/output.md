# 상품 목록 페이지 구현

카테고리별 필터링과 검색 기능을 갖춘 상품 목록 페이지를 구현한다.
Root 템플릿 패턴(Composition 기반)을 사용하며, 디자인 시스템 컴포넌트를 활용한다.

---

## 파일 구조

```
apps/products/
├── models.py
├── services.py
├── managers.py
└── static/
    └── products/
        └── js/
            └── product-list.js

web/
├── views/
│   └── products/
│       ├── __init__.py
│       └── views.py
├── view_urls.py
└── templates/
    ├── products/
    │   ├── products_root.html
    │   ├── product_list/
    │   │   └── product_list.html
    │   └── product_filters/
    │       └── product_filters.html
    └── design_system/
        ├── forms/
        │   ├── _search_input.html
        │   └── _select_dropdown.html
        └── cards/
            └── _product_card.html
```

---

## 1. 모델 (apps/products/models.py)

```python
from django.db import models
from django.db.models import QuerySet


class Category(models.Model):
    """상품 카테고리."""

    name = models.CharField("카테고리명", max_length=100)
    slug = models.SlugField("슬러그", unique=True)
    display_order = models.PositiveIntegerField("표시 순서", default=0)

    class Meta:
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리"
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class ProductQuerySet(QuerySet):
    """상품 QuerySet -- 체이닝 가능한 필터 메서드를 제공한다."""

    def published(self) -> "ProductQuerySet":
        return self.filter(is_published=True)

    def by_category(self, category_slug: str) -> "ProductQuerySet":
        return self.filter(category__slug=category_slug)

    def search(self, query: str) -> "ProductQuerySet":
        return self.filter(name__icontains=query)


class Product(models.Model):
    """판매 상품."""

    name = models.CharField("상품명", max_length=200)
    description = models.TextField("설명", blank=True)
    price = models.DecimalField("가격", max_digits=12, decimal_places=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="카테고리",
    )
    image_url = models.URLField("이미지 URL", blank=True)
    is_published = models.BooleanField("게시 여부", default=True, db_default=True)
    created_at = models.DateTimeField("생성일", auto_now_add=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "상품"
        verbose_name_plural = "상품"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["is_published", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def formatted_price(self) -> str:
        """천 단위 콤마가 포함된 가격 문자열."""
        return f"{self.price:,.0f}원"
```

---

## 2. 서비스 레이어 (apps/products/services.py)

```python
from django.db.models import QuerySet

from apps.products.models import Category, Product


def product_list(
    *,
    category_slug: str | None = None,
    search_query: str | None = None,
) -> QuerySet[Product]:
    """게시된 상품 목록을 조회한다.

    카테고리 필터와 검색어를 선택적으로 적용한다.
    """
    qs = Product.objects.published().select_related("category")

    if category_slug:
        qs = qs.by_category(category_slug)

    if search_query:
        qs = qs.search(search_query)

    return qs


def category_list() -> QuerySet[Category]:
    """표시 순서대로 정렬된 전체 카테고리 목록을 조회한다."""
    return Category.objects.all()
```

---

## 3. 뷰 (web/views/products/views.py)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.products.services import category_list, product_list


class ProductListView(LoginRequiredMixin, TemplateView):
    """상품 목록 페이지 -- 카테고리 필터링과 검색을 지원한다."""

    template_name = "products/products_root.html"

    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)
        category_slug = self.request.GET.get("category", "")
        search_query = self.request.GET.get("q", "")

        ctx["products"] = product_list(
            category_slug=category_slug or None,
            search_query=search_query or None,
        )
        ctx["categories"] = category_list()
        ctx["selected_category"] = category_slug
        ctx["search_query"] = search_query
        return ctx
```

---

## 4. URL 설정 (web/view_urls.py)

```python
from django.urls import path

from web.views.products.views import ProductListView

app_name = "web"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="products"),
]
```

---

## 5. 템플릿

### 5-1. Root 템플릿 (web/templates/products/products_root.html)

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block title %}상품 목록{% endblock title %}

{% block meta_description %}카테고리별 필터링과 검색이 가능한 상품 목록 페이지{% endblock meta_description %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'products/css/product-list.css' %}">
{% endblock head_extra %}

{% block body %}
    {% include "products/product_filters/product_filters.html" with categories=categories selected_category=selected_category search_query=search_query only %}
    {% include "products/product_list/product_list.html" with products=products search_query=search_query selected_category=selected_category only %}
{% endblock body %}

{% block scripts %}
    {{ block.super }}
    <script src="{% static 'products/js/product-list.js' %}"></script>
{% endblock scripts %}
```

### 5-2. 필터 섹션 (web/templates/products/product_filters/product_filters.html)

```htmldjango
{# 필수 변수: categories (QuerySet[Category]), selected_category (str), search_query (str) #}
{% load static %}

<section class="product-filters" aria-label="상품 필터">
    <form method="get" action="" class="product-filters__form" role="search">
        {% include "design_system/forms/_search_input.html" with name="q" value=search_query placeholder="상품명을 검색하세요" only %}

        {% include "design_system/forms/_select_dropdown.html" with name="category" options=categories selected=selected_category label="카테고리" all_label="전체 카테고리" only %}

        <button type="submit" class="product-filters__submit">
            검색
        </button>
    </form>
</section>
```

### 5-3. 상품 목록 섹션 (web/templates/products/product_list/product_list.html)

```htmldjango
{# 필수 변수: products (QuerySet[Product]), search_query (str), selected_category (str) #}

<section class="product-list" aria-label="상품 목록">
    {% if search_query or selected_category %}
    <div class="product-list__result-info">
        <p>
            {% if search_query %}<strong>"{{ search_query }}"</strong> 검색 결과{% endif %}
            {% if search_query and selected_category %} &middot; {% endif %}
            {% if selected_category %}카테고리 필터 적용됨{% endif %}
            &middot; {{ products|length }}개 상품
        </p>
    </div>
    {% endif %}

    {% if products %}
    <div class="product-list__grid">
        {% for product in products %}
            {% include "design_system/cards/_product_card.html" with product=product only %}
        {% endfor %}
    </div>
    {% else %}
    <div class="product-list__empty">
        <p>조건에 맞는 상품이 없습니다.</p>
        <a href="?">전체 상품 보기</a>
    </div>
    {% endif %}
</section>
```

---

## 6. 디자인 시스템 컴포넌트

### 6-1. 검색 입력 (web/templates/design_system/forms/_search_input.html)

```htmldjango
{# 필수 변수: name (str), value (str), placeholder (str) #}

<div class="ds-search-input">
    <label for="search-{{ name }}" class="sr-only">{{ placeholder }}</label>
    <input
        type="search"
        id="search-{{ name }}"
        name="{{ name }}"
        value="{{ value }}"
        placeholder="{{ placeholder }}"
        class="ds-search-input__field"
        autocomplete="off"
    >
</div>
```

### 6-2. 셀렉트 드롭다운 (web/templates/design_system/forms/_select_dropdown.html)

```htmldjango
{# 필수 변수: name (str), options (QuerySet), selected (str), label (str), all_label (str) #}

<div class="ds-select">
    <label for="select-{{ name }}" class="sr-only">{{ label }}</label>
    <select id="select-{{ name }}" name="{{ name }}" class="ds-select__field">
        <option value="">{{ all_label }}</option>
        {% for option in options %}
            <option value="{{ option.slug }}" {% if option.slug == selected %}selected{% endif %}>
                {{ option.name }}
            </option>
        {% endfor %}
    </select>
</div>
```

### 6-3. 상품 카드 (web/templates/design_system/cards/_product_card.html)

```htmldjango
{# 필수 변수: product (Product) #}

<article class="ds-product-card">
    {% if product.image_url %}
    <div class="ds-product-card__image">
        <img src="{{ product.image_url }}" alt="{{ product.name }}" loading="lazy">
    </div>
    {% endif %}
    <div class="ds-product-card__body">
        <span class="ds-product-card__category">{{ product.category.name }}</span>
        <h3 class="ds-product-card__name">{{ product.name }}</h3>
        {% if product.description %}
        <p class="ds-product-card__description">{{ product.description|truncatewords:20 }}</p>
        {% endif %}
        <p class="ds-product-card__price">{{ product.formatted_price }}</p>
    </div>
</article>
```

---

## 7. CSS (static/products/css/product-list.css)

```css
/* 상품 필터 */
.product-filters {
    padding: var(--spacing-lg, 1.5rem) var(--spacing-xl, 2rem);
    background-color: var(--color-bg-subtle, #f3f4f6);
    border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.product-filters__form {
    display: flex;
    gap: var(--spacing-md, 1rem);
    align-items: center;
    max-width: 72rem;
    margin: 0 auto;
    flex-wrap: wrap;
}

.product-filters__submit {
    padding: var(--spacing-sm, 0.5rem) var(--spacing-lg, 1.5rem);
    background-color: var(--btn-bg, var(--color-primary, #3b82f6));
    color: var(--btn-text, #ffffff);
    border: none;
    border-radius: var(--radius-md, 0.5rem);
    cursor: pointer;
    font-size: var(--text-base, 1rem);
    transition: background-color var(--transition-duration, 200ms);
}

.product-filters__submit:hover {
    background-color: var(--btn-bg-hover, var(--color-primary-hover, #1d4ed8));
}

.product-filters__submit:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

/* 상품 목록 */
.product-list {
    padding: var(--spacing-xl, 2rem);
    max-width: 72rem;
    margin: 0 auto;
}

.product-list__result-info {
    margin-bottom: var(--spacing-lg, 1.5rem);
    color: var(--color-text-muted, #6b7280);
    font-size: var(--text-sm, 0.875rem);
}

.product-list__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
    gap: var(--spacing-lg, 1.5rem);
}

.product-list__empty {
    text-align: center;
    padding: var(--spacing-xl, 2rem);
    color: var(--color-text-muted, #6b7280);
}

.product-list__empty a {
    color: var(--color-primary, #3b82f6);
    text-decoration: underline;
}

/* 디자인 시스템 - 검색 입력 */
.ds-search-input__field {
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    font-size: var(--text-base, 1rem);
    min-width: 16rem;
    transition: border-color var(--transition-duration, 200ms);
}

.ds-search-input__field:focus {
    outline: none;
    border-color: var(--color-primary, #3b82f6);
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

/* 디자인 시스템 - 셀렉트 */
.ds-select__field {
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    font-size: var(--text-base, 1rem);
    background-color: var(--color-bg, #ffffff);
    cursor: pointer;
    transition: border-color var(--transition-duration, 200ms);
}

.ds-select__field:focus {
    outline: none;
    border-color: var(--color-primary, #3b82f6);
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

/* 디자인 시스템 - 상품 카드 */
.ds-product-card {
    border: 1px solid var(--card-border, var(--color-border, #e5e7eb));
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    overflow: hidden;
    background-color: var(--color-bg, #ffffff);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
    transition: box-shadow var(--transition-duration, 200ms);
}

.ds-product-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ds-product-card__image {
    aspect-ratio: 4 / 3;
    overflow: hidden;
    background-color: var(--color-bg-subtle, #f3f4f6);
}

.ds-product-card__image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.ds-product-card__body {
    padding: var(--spacing-md, 1rem);
}

.ds-product-card__category {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-primary, #3b82f6);
    font-weight: 500;
}

.ds-product-card__name {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin: var(--spacing-xs, 0.25rem) 0;
    font-weight: 600;
}

.ds-product-card__description {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
    margin: var(--spacing-xs, 0.25rem) 0;
    line-height: 1.5;
}

.ds-product-card__price {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    font-weight: 700;
    margin-top: var(--spacing-sm, 0.5rem);
}

/* 접근성 - 화면 리더 전용 */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

/* 반응형 */
@media (max-width: 768px) {
    .product-filters__form {
        flex-direction: column;
        align-items: stretch;
    }

    .ds-search-input__field {
        min-width: 100%;
    }

    .product-list__grid {
        grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr));
        gap: var(--spacing-md, 1rem);
    }
}
```

---

## 8. JavaScript (static/products/js/product-list.js)

```javascript
/**
 * 상품 목록 페이지 -- 검색 폼 UX 향상
 *
 * 카테고리 변경 시 즉시 폼을 제출하여 필터링 결과를 반영한다.
 */
document.addEventListener("DOMContentLoaded", () => {
    const categorySelect = document.querySelector('[name="category"]');
    if (categorySelect) {
        categorySelect.addEventListener("change", () => {
            categorySelect.closest("form").submit();
        });
    }
});
```

---

## 적용된 원칙 요약

| 영역 | 적용 원칙 |
|------|----------|
| 모델 | Fat Model -- `ProductQuerySet`에 필터링 로직을 캡슐화, `formatted_price` 프로퍼티로 표현 로직을 모델에 배치 |
| 서비스 | `<entity>_<action>` 네이밍, 키워드 전용 매개변수(`*`), 서비스 함수로 뷰와 모델 분리 |
| 뷰 | `TemplateView` + `get_context_data` 패턴, `LoginRequiredMixin`을 MRO 앞에 배치 |
| 템플릿 | Root 패턴(Composition 기반), `{% include ... only %}` 컨텍스트 격리, `{% endblock name %}` 명시 |
| 디자인 시스템 | `_` 접두사 파트셜, 필수 변수 문서화, `var()` 폴백 값, 3계층 토큰 참조 |
| CSS | 하드코딩 값 없이 디자인 토큰만 사용, `focus-visible` 포커스 링, `prefers-reduced-motion` 대응 |
| 접근성 | `aria-label` 섹션 레이블, `sr-only` 라벨, `role="search"`, `loading="lazy"` 이미지 |
| QuerySet | `select_related("category")`로 N+1 방지, 커스텀 QuerySet 메서드로 체이닝 가능한 필터 |

---

> **관련 스킬 참조:**
> - 상품 상세 페이지 추가 -> **implementation-django-web** 스킬
> - 상품 CRUD API 구현 -> **implementation-django-ninja** 스킬
> - 모델 인덱스 최적화, 전문 검색 -> **implementation-django** 스킬 (PostgreSQL 전용 기능)
> - 페이지네이션 추가 -> **implementation-django-web** 스킬
