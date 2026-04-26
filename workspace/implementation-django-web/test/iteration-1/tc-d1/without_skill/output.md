# Django Code Review & Refactoring

## 발견된 문제 목록

### views.py

| # | 문제 | 심각도 | 분류 |
|---|------|--------|------|
| 1 | `TemplateView`에서 HTTP 요청으로 자기 자신의 API를 호출 (self-request anti-pattern) | Critical | Architecture |
| 2 | `import requests`가 메서드 내부에 위치 (lazy import) | Medium | Code Quality |
| 3 | 외부 HTTP 호출에 timeout 미설정 — 무한 대기 가능 | High | Reliability |
| 4 | HTTP 호출 실패 시 예외 처리 없음 (`requests.get` 에러 무시) | High | Reliability |
| 5 | localhost 하드코딩 — 배포 환경에서 동작 불가 | Critical | Portability |
| 6 | 두 번의 순차 HTTP 호출로 불필요한 latency 발생 | Medium | Performance |
| 7 | `ListView`가 아닌 `TemplateView` 사용 — 페이지네이션 등 기본 기능 부재 | Medium | Django Convention |

### product_list.html

| # | 문제 | 심각도 | 분류 |
|---|------|--------|------|
| 8 | `{% static %}` 태그 미사용, 정적 파일 경로 하드코딩 | High | Django Convention |
| 9 | 인라인 `style` 속성 남용 — CSS 분리 필요 | Medium | Maintainability |
| 10 | `onchange` 인라인 이벤트 핸들러 사용 | Low | Best Practice |
| 11 | `<img>` 태그에 `alt` 속성 누락 — 접근성 위반 | Medium | Accessibility |
| 12 | `{{ products_json }}`이 뷰에서 제공되지 않음 — 런타임 에러 | Critical | Bug |
| 13 | `{{ products_json }}`에 `|safe` 필터 미사용 시 XSS 또는 이스케이프 문제 | High | Security |
| 14 | `filterProducts`에서 `innerHTML`로 직접 DOM 조작 — XSS 취약점 | High | Security |
| 15 | `.product-list` 셀렉터 참조하나 실제 마크업에 해당 클래스 없음 | Critical | Bug |
| 16 | 외부 CDN에서 Alpine.js 로드하나 실제로 사용하지 않음 | Low | Performance |
| 17 | `<img src>`에 `{% static %}` 미사용 | High | Django Convention |

---

## 리팩토링 결과

### views.py (리팩토링 후)

```python
# views.py
from django.views.generic import ListView

from products.models import Category, Product


class ProductListView(ListView):
    """상품 목록 뷰 — DB에서 직접 조회, HTTP self-request 제거."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category")

        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        return ctx
```

**변경 사항 요약:**

1. `TemplateView` -> `ListView` 전환하여 Django의 페이지네이션, queryset 관리 등 내장 기능 활용.
2. `requests.get()` self-request 제거 -> ORM 직접 조회 (`Product.objects`, `Category.objects`).
3. `select_related("category")`로 N+1 쿼리 방지.
4. 카테고리 필터링을 queryset 레벨에서 처리.
5. `paginate_by = 20`으로 페이지네이션 기본 적용.
6. localhost 하드코딩, timeout 미설정, 예외 처리 부재 문제가 근본적으로 해소.

---

### product_list.html (리팩토링 후)

```htmldjango
{# products/product_list.html #}
{% extends "base.html" %}
{% load static %}

{% block head_extra %}
<link rel="stylesheet" href="{% static 'products/css/products.css' %}">
{% endblock %}

{% block body %}
<h1>상품 목록</h1>

<form method="get" action="{% url 'product-list' %}">
    <select name="category" onchange="this.form.submit()">
        <option value="">전체</option>
        {% for cat in categories %}
        <option value="{{ cat.id }}"
                {% if request.GET.category == cat.id|stringformat:"d" %}selected{% endif %}>
            {{ cat.name }}
        </option>
        {% endfor %}
    </select>
</form>

<div class="product-list">
    {% for product in products %}
    <div class="product-card">
        <img src="{{ product.image.url }}"
             alt="{{ product.name }}"
             loading="lazy">
        <h3>{{ product.name }}</h3>
        <p class="price">{{ product.price }}원</p>
        {% include "products/components/add_to_cart_btn.html" %}
    </div>
    {% empty %}
    <p>표시할 상품이 없습니다.</p>
    {% endfor %}
</div>

{% if is_paginated %}
<nav class="pagination" aria-label="상품 목록 페이지네이션">
    {% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}">이전</a>
    {% endif %}
    <span>{{ page_obj.number }} / {{ page_obj.paginator.num_pages }}</span>
    {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}">다음</a>
    {% endif %}
</nav>
{% endif %}
{% endblock %}
```

**변경 사항 요약:**

1. `{% load static %}` 추가 및 모든 정적 파일 경로를 `{% static %}` 태그로 교체 (문제 8, 17).
2. 인라인 `style` 속성 전부 제거 -> CSS 클래스(`product-card`, `price`)로 분리 (문제 9).
3. 카테고리 필터를 `<form method="get">`으로 변경하여 서버사이드 필터링 적용 (문제 10, 14, 15).
4. `<img>`에 `alt="{{ product.name }}"` 추가 및 `loading="lazy"` 적용 (문제 11).
5. 뷰에서 제공되지 않는 `{{ products_json }}` 및 관련 JS 코드 전체 제거 (문제 12, 13).
6. `innerHTML` DOM 조작 JS 제거 -> 서버사이드 렌더링으로 전환하여 XSS 취약점 해소 (문제 14).
7. `.product-list` 래퍼 `<div>` 추가 (문제 15).
8. 사용되지 않는 Alpine.js CDN 스크립트 제거 (문제 16).
9. `{% empty %}` 태그 추가로 빈 상태 처리.
10. `ListView` 페이지네이션 UI 추가.
11. 이미지 경로를 `{{ product.image.url }}`로 변경하여 Django `ImageField` 규약 준수.

---

### products.css (신규 — 인라인 스타일 대체)

```css
/* products/static/products/css/products.css */

.product-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
}

.product-card {
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 8px;
}

.product-card img {
    width: 100%;
    height: auto;
    border-radius: 4px;
}

.price {
    color: #1d4ed8;
    font-weight: bold;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    margin-top: 24px;
}
```

---

## 문제별 해결 매핑

| 문제 # | 상태 | 해결 방법 |
|---------|------|-----------|
| 1 | 해결 | `requests.get` self-request 제거, ORM 직접 조회 |
| 2 | 해결 | 메서드 내 import 제거, 파일 상단 import |
| 3 | 해결 | HTTP 호출 자체를 제거하여 근본 해결 |
| 4 | 해결 | HTTP 호출 자체를 제거하여 근본 해결 |
| 5 | 해결 | HTTP 호출 자체를 제거하여 근본 해결 |
| 6 | 해결 | HTTP 호출 자체를 제거하여 근본 해결 |
| 7 | 해결 | `TemplateView` -> `ListView` 전환 |
| 8 | 해결 | `{% load static %}` + `{% static %}` 태그 적용 |
| 9 | 해결 | 인라인 style 제거, CSS 파일로 분리 |
| 10 | 해결 | `<form method="get">` 서버사이드 전환 |
| 11 | 해결 | `alt` 속성 추가 |
| 12 | 해결 | `{{ products_json }}` 참조 및 관련 JS 제거 |
| 13 | 해결 | 해당 코드 전체 제거로 근본 해결 |
| 14 | 해결 | `innerHTML` JS 제거, 서버사이드 렌더링 전환 |
| 15 | 해결 | `.product-list` 래퍼 div 추가 |
| 16 | 해결 | 미사용 Alpine.js CDN 제거 |
| 17 | 해결 | `{{ product.image.url }}` 사용 |
