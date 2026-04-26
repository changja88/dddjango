# ProductListView 코드 리뷰 및 리팩토링

---

## Part 1. Review

### 코드 요약

`ProductListView`는 `TemplateView`를 상속하여 상품 목록 페이지를 렌더링한다. 뷰에서 내부 API를 HTTP로 호출하여 상품/카테고리 데이터를 가져오고, 템플릿에서 카테고리 필터와 상품 카드를 표시한다.

### 리뷰 결과

**[View Layer: Missing error handling]** -- `get_context_data` 안에서 `requests.get()`을 두 번 호출하지만 `try/except`가 없다. API 서버가 응답하지 않거나 에러를 반환하면 뷰 전체가 500 에러로 실패한다.

**[View Layer: import inside method]** -- `import requests`가 `get_context_data` 메서드 안에 있다. 모듈 최상단에서 임포트하는 것이 Python 컨벤션이다.

**[View Layer: Hardcoded API base URL]** -- `http://localhost:8000`이 뷰 코드에 직접 하드코딩되어 있다. `settings.INTERNAL_API_BASE_URL` 또는 `InternalAPIClient` 패턴을 사용해야 한다.

**[View Layer: No InternalAPIClient]** -- 내부 API를 호출할 때 인증 정보(쿠키, Authorization 헤더)를 전달하지 않고 raw `requests.get`을 사용한다. `InternalAPIClient` 패턴을 사용해야 일관성과 인증 전파가 보장된다.

**[Asset Management: Hardcoded static path - CSS]** -- `<link rel="stylesheet" href="/static/products/css/products.css">`에서 정적 파일 경로를 하드코딩했다. `{% static %}` 태그를 사용해야 `ManifestStaticFilesStorage` 캐시 버스팅이 적용된다.

**[Asset Management: Hardcoded static path - image]** -- `<img src="/static/products/images/{{ product.image }}">`에서 정적 파일 경로를 하드코딩했다. `{% static %}` 태그를 사용해야 한다.

**[Asset Management: Missing {% load static %}]** -- `{% static %}` 태그를 사용하려면 자식 템플릿에서 `{% load static %}`을 선언해야 한다. `{% load %}` 태그는 부모 템플릿으로부터 상속되지 않는다.

**[Asset Management: json_script not used - XSS risk]** -- `window.__PRODUCTS__ = {{ products_json }};`에서 서버 데이터를 `<script>` 태그 안에 `{{ }}` 변수 치환으로 직접 삽입하고 있다. 이는 XSS 취약점이다. `json_script` 필터를 사용해야 한다.

**[Asset Management: CDN without SRI]** -- `<script src="https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js"></script>`에 `integrity`와 `crossorigin` 속성이 없다. CDN이 변조될 경우 악성 스크립트가 실행될 수 있다.

**[Asset Management: Inline app logic in script]** -- `filterProducts()` 함수가 템플릿 내 인라인 `<script>`에 작성되어 있다. 앱 로직은 별도 `.js` 파일로 분리해야 한다.

**[Asset Management: Missing script/style comment]** -- `<script>` 태그에 Django 템플릿 주석(`{# ... #}`)으로 용도가 설명되어 있지 않다.

**[Template Architecture: Missing {{ block.super }} in head_extra]** -- `{% block head_extra %}`에서 `{{ block.super }}`를 호출하지 않아 부모 템플릿의 `head_extra` 블록 내용이 완전히 대체된다. 부모에 기존 CSS가 있다면 사라진다.

**[Template Architecture: Missing endblock name]** -- `{% endblock %}`에 블록명이 명시되지 않아 가독성이 떨어진다. `{% endblock head_extra %}`, `{% endblock body %}` 형태로 닫아야 한다.

**[Template Architecture: include without only]** -- `{% include "products/components/add_to_cart_btn.html" %}`에 `only` 키워드가 없어 부모 컨텍스트의 모든 변수가 컴포넌트에 암묵적으로 전달된다.

**[Design System: Hardcoded inline styles]** -- `.product-card`에 `style="border: 1px solid #e5e7eb; padding: 16px; margin: 8px; border-radius: 8px;"`이 인라인으로 작성되어 있다. 색상(`#e5e7eb`)과 간격(`16px`, `8px`)은 디자인 토큰 CSS Custom Properties로 추출해야 한다.

**[Design System: Hardcoded color in price]** -- `<p class="price" style="color: #1d4ed8; font-weight: bold;">`에서 색상이 하드코딩되어 있다. 디자인 토큰을 사용해야 한다.

**[View Layer: AJAX without CSRF]** -- `filterProducts()` 내의 `fetch('/api/products/?category=' + categoryId)`는 GET 요청이므로 CSRF가 필수는 아니지만, 향후 POST로 변경될 가능성을 대비하여 CSRF 유틸리티 함수를 준비해두는 것이 좋다.

**[Template: innerHTML XSS risk]** -- `document.querySelector('.product-list').innerHTML = data.map(...)...`에서 서버 응답 데이터를 `innerHTML`로 직접 삽입하고 있다. 서버 렌더 HTML 조각(HTMX) 패턴을 고려해야 한다.

### 리뷰 체크리스트 검증

- [x] Hardcoded static file paths instead of `{% static %}` -- **발견됨** (CSS, image)
- [x] `{{ value }}` inside `<script>` without `json_script` (XSS risk) -- **발견됨** (`{{ products_json }}`)
- [x] CDN scripts without `integrity` and `crossorigin` attributes (SRI) -- **발견됨** (Alpine.js)
- [x] Missing CSRF token in AJAX POST/PUT/PATCH/DELETE requests -- **해당 없음** (현재 GET만 사용)
- [x] `{% include %}` without `only` keyword (implicit context leaking) -- **발견됨** (add_to_cart_btn)
- [x] Hardcoded color/spacing values instead of design tokens (`var()`) -- **발견됨** (inline styles)
- [x] External CSS overriding design system component styles -- **해당 없음**
- [x] Inline `<style>` in templates -- **해당 없음** (inline `style` 속성은 있으나 `<style>` 태그는 없음)
- [x] Inline app logic in `<script>` -- **발견됨** (`filterProducts`)
- [x] Missing `{{ block.super }}` where parent block content should be preserved -- **발견됨** (head_extra)
- [x] `{% load %}` missing in child template -- **발견됨** (`{% load static %}` 누락)
- [x] TemplateView missing `LoginRequiredMixin` for authenticated pages -- **판단 보류** (공개 상품 목록이면 불필요할 수 있음, 주석 필요)
- [x] Missing error handling when view calls external services/APIs -- **발견됨**
- [x] No `{% block %}` name in closing `{% endblock %}` tag -- **발견됨**
- [x] Design token without `var()` fallback value -- **확인 대상** (리팩토링에서 반영)

---

## Part 2. Refactoring

### Change 1: Import를 모듈 최상단으로 이동 + InternalAPIClient 패턴 적용

[Before]
```python
from django.views.generic import TemplateView

class ProductListView(TemplateView):
    template_name = "products/product_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        import requests
        resp = requests.get("http://localhost:8000/api/products/")
        ctx["products"] = resp.json()
        ctx["categories"] = requests.get("http://localhost:8000/api/categories/").json()
        return ctx
```

[After]
```python
import requests
from django.views.generic import TemplateView

from web.api_client import InternalAPIClient


class ProductListView(TemplateView):
    template_name = "products/product_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        try:
            ctx["products"] = api.get("products/")
        except requests.HTTPError:
            ctx["products"] = []
            ctx["error_message"] = "상품 목록을 불러올 수 없습니다."
        try:
            ctx["categories"] = api.get("categories/")
        except requests.HTTPError:
            ctx["categories"] = []
        return ctx
```

[Reason] View Layer -- `import`는 모듈 최상단에 배치한다. 하드코딩된 URL 대신 `InternalAPIClient`를 사용하여 `settings.INTERNAL_API_BASE_URL`을 참조하고 인증 정보를 자동 전파한다. 외부 서비스 호출에는 `try/except`로 에러를 처리하여 뷰가 500 에러로 실패하지 않도록 한다.

---

### Change 2: `{% load static %}` 추가 + `{% static %}` 태그로 CSS 경로 변환 + `{{ block.super }}` 추가

[Before]
```htmldjango
{% block head_extra %}
<link rel="stylesheet" href="/static/products/css/products.css">
{% endblock %}
```

[After]
```htmldjango
{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'products/css/products.css' %}">
{% endblock head_extra %}
```

[Reason] Asset Management + Template Architecture -- `{% load static %}`는 자식 템플릿에서 별도로 로드해야 한다(상속되지 않음). 하드코딩된 `/static/...` 경로를 `{% static %}` 태그로 변환하면 `ManifestStaticFilesStorage` 캐시 버스팅이 적용된다. `{{ block.super }}`를 추가하여 부모 블록 내용을 보존하고, `{% endblock head_extra %}`에 블록명을 명시하여 가독성을 높인다.

---

### Change 3: 이미지 경로를 `{% static %}` 태그로 변환

[Before]
```htmldjango
<img src="/static/products/images/{{ product.image }}">
```

[After]
```htmldjango
<img src="{% static 'products/images/' %}{{ product.image }}" alt="{{ product.name }}">
```

[Reason] Asset Management -- 정적 파일 경로는 `{% static %}` 태그를 사용해야 한다. `alt` 속성을 추가하여 접근성도 개선한다. 참고: 동적 파일명을 `{% static %}` 안에 직접 결합할 수 없으므로 base path까지만 `{% static %}`으로 처리한다. 만약 상품 이미지가 사용자 업로드 파일이라면 `{{ product.image.url }}`(ImageField) 패턴이 더 적합하다.

---

### Change 4: `{% include %}` 에 `only` 키워드 추가

[Before]
```htmldjango
{% include "products/components/add_to_cart_btn.html" %}
```

[After]
```htmldjango
{% include "products/components/add_to_cart_btn.html" with product=product only %}
```

[Reason] Template Architecture -- `only` 키워드로 컨텍스트를 격리하면 컴포넌트에 전달되는 변수가 명시적으로 드러나고, 부모 컨텍스트의 암묵적 의존을 방지한다.

---

### Change 5: 인라인 스타일을 CSS Custom Property 토큰으로 추출

[Before]
```htmldjango
<div class="product-card" style="border: 1px solid #e5e7eb; padding: 16px; margin: 8px; border-radius: 8px;">
    ...
    <p class="price" style="color: #1d4ed8; font-weight: bold;">{{ product.price }}원</p>
```

[After]
```htmldjango
<div class="product-card">
    ...
    <p class="product-card__price">{{ product.price }}원</p>
```

```css
/* products/css/products.css */
.product-card {
    border: 1px solid var(--color-border, #e5e7eb);
    padding: var(--spacing-md, 1rem);
    margin: var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-md, 0.5rem);
}

.product-card__price {
    color: var(--color-primary, #1d4ed8);
    font-weight: bold;
}
```

[Reason] Design System -- 하드코딩된 색상/간격 값을 CSS Custom Property 디자인 토큰으로 추출한다. `var()` 폴백 값을 포함하여 토큰이 정의되지 않은 환경에서도 안전하게 렌더링된다. 인라인 `style` 속성을 제거하고 별도 CSS 파일에서 관리한다.

---

### Change 6: `{{ products_json }}`을 `json_script` 필터로 변환

[Before]
```htmldjango
<script>
    window.__PRODUCTS__ = {{ products_json }};
    function filterProducts(categoryId) { ... }
</script>
```

[After]
```htmldjango
{# 서버 -> JS 데이터 전달: 상품 목록 #}
{{ products_json|json_script:"products-data" }}
```

```javascript
// static/products/js/product_filter.js
const products = JSON.parse(
    document.getElementById('products-data').textContent
);
// ... filterProducts 로직
```

[Reason] Asset Management -- `{{ value }}`를 `<script>` 안에 직접 삽입하면 XSS 취약점이 발생한다. `json_script` 필터는 `<`, `>`, `&` 등을 안전하게 이스케이프한 `type="application/json"` 스크립트 태그를 생성한다. `window.__` 전역 변수 패턴도 함께 제거한다. 인라인 앱 로직은 별도 `.js` 파일로 분리한다.

---

### Change 7: CDN 스크립트에 SRI 속성 추가

[Before]
```htmldjango
<script src="https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js"></script>
```

[After]
```htmldjango
{# Alpine.js -- 선언적 UI 인터랙션 #}
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

[Reason] Asset Management -- CDN 스크립트에는 `integrity`(SRI)와 `crossorigin="anonymous"` 속성을 반드시 포함해야 한다. CDN이 변조되더라도 브라우저가 무결성 검증에 실패하여 스크립트 실행을 차단한다. `defer` 속성을 추가하여 파싱 차단을 방지하고, Django 템플릿 주석으로 용도를 명시한다. 참고: `integrity` 해시값은 실제 배포 시 해당 파일의 SHA-384 해시로 교체해야 한다.

---

### Change 8: 인라인 JS 앱 로직을 별도 파일로 분리 + HTMX 고려

[Before]
```htmldjango
<script>
    function filterProducts(categoryId) {
        fetch('/api/products/?category=' + categoryId)
            .then(r => r.json())
            .then(data => {
                document.querySelector('.product-list').innerHTML =
                    data.map(p => '<div class="product-card">' + p.name + '</div>').join('');
            });
    }
</script>
```

[After]
```javascript
// static/products/js/product_filter.js
const products = JSON.parse(
    document.getElementById('products-data').textContent
);

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function filterProducts(categoryId) {
    fetch('/api/products/?category=' + encodeURIComponent(categoryId), {
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
    })
        .then(r => r.json())
        .then(data => {
            // HTMX 패턴으로 전환 시 이 로직은 서버 측 HTML 조각으로 대체 가능
            const container = document.getElementById('product-list');
            container.textContent = '';
            data.forEach(p => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.textContent = p.name;
                container.appendChild(card);
            });
        });
}
```

[Reason] Asset Management + View Layer -- 인라인 앱 로직은 별도 JS 파일(`static/products/js/product_filter.js`)로 분리한다. `innerHTML` 대신 DOM API(`createElement`, `textContent`)를 사용하여 XSS 위험을 제거한다. CSRF 유틸리티 함수를 준비하고, 향후 HTMX 패턴으로의 전환을 권장한다. `encodeURIComponent`로 쿼리 파라미터를 인코딩하여 URL injection을 방지한다.

---

### Change 9: `{% endblock %}`에 블록명 명시

[Before]
```htmldjango
{% block head_extra %}
...
{% endblock %}

{% block body %}
...
{% endblock %}
```

[After]
```htmldjango
{% block head_extra %}
...
{% endblock head_extra %}

{% block body %}
...
{% endblock body %}
```

[Reason] Template Architecture -- 닫는 `{% endblock name %}` 태그에 블록명을 명시하면 중첩된 블록 구조에서 가독성이 향상된다.

---

### Change 10: `onchange` 인라인 이벤트 핸들러 제거

[Before]
```htmldjango
<select id="category-filter" onchange="filterProducts(this.value)">
```

[After]
```htmldjango
<select id="category-filter">
```

```javascript
// static/products/js/product_filter.js 에 추가
document.addEventListener('DOMContentLoaded', () => {
    const filter = document.getElementById('category-filter');
    if (filter) {
        filter.addEventListener('change', (e) => filterProducts(e.target.value));
    }
});
```

[Reason] Asset Management -- 인라인 이벤트 핸들러(`onchange`)는 CSP(Content Security Policy) 정책과 충돌하며, JS 로직이 HTML에 혼재된다. JS 파일에서 이벤트를 바인딩하여 관심사를 분리한다.

---

## 완성된 리팩토링 코드

### views.py

```python
import requests
from django.views.generic import TemplateView

from web.api_client import InternalAPIClient


class ProductListView(TemplateView):
    template_name = "products/product_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        try:
            ctx["products"] = api.get("products/")
        except requests.HTTPError:
            ctx["products"] = []
            ctx["error_message"] = "상품 목록을 불러올 수 없습니다."
        try:
            ctx["categories"] = api.get("categories/")
        except requests.HTTPError:
            ctx["categories"] = []
        return ctx
```

### products/product_list.html

```htmldjango
{# products/product_list.html #}
{% extends "base.html" %}
{% load static %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'products/css/products.css' %}">
{% endblock head_extra %}

{% block body %}
<h1>상품 목록</h1>

<select id="category-filter">
    {% for cat in categories %}
    <option value="{{ cat.id }}">{{ cat.name }}</option>
    {% endfor %}
</select>

<div id="product-list">
{% for product in products %}
<div class="product-card">
    <img src="{% static 'products/images/' %}{{ product.image }}" alt="{{ product.name }}">
    <h3>{{ product.name }}</h3>
    <p class="product-card__price">{{ product.price }}원</p>
    {% include "products/components/add_to_cart_btn.html" with product=product only %}
</div>
{% endfor %}
</div>
{% endblock body %}

{% block scripts %}
    {{ block.super }}
    {# Alpine.js -- 선언적 UI 인터랙션 #}
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"
            integrity="sha384-..." crossorigin="anonymous"></script>
    {# 서버 -> JS 데이터 전달: 상품 목록 #}
    {{ products_json|json_script:"products-data" }}
    {# 상품 필터링 앱 스크립트 #}
    <script src="{% static 'products/js/product_filter.js' %}"></script>
{% endblock scripts %}
```

### static/products/css/products.css

```css
.product-card {
    border: 1px solid var(--color-border, #e5e7eb);
    padding: var(--spacing-md, 1rem);
    margin: var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-md, 0.5rem);
}

.product-card__price {
    color: var(--color-primary, #1d4ed8);
    font-weight: bold;
}
```

### static/products/js/product_filter.js

```javascript
const products = JSON.parse(
    document.getElementById('products-data').textContent
);

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function filterProducts(categoryId) {
    fetch('/api/products/?category=' + encodeURIComponent(categoryId), {
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
    })
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('product-list');
            container.textContent = '';
            data.forEach(p => {
                const card = document.createElement('div');
                card.className = 'product-card';
                card.textContent = p.name;
                container.appendChild(card);
            });
        });
}

document.addEventListener('DOMContentLoaded', () => {
    const filter = document.getElementById('category-filter');
    if (filter) {
        filter.addEventListener('change', (e) => filterProducts(e.target.value));
    }
});
```

---

## 변경 사항 요약

| # | 변경 | 적용 컨벤션 |
|---|------|-------------|
| 1 | import 최상단 이동 + InternalAPIClient + 에러 처리 | View Layer |
| 2 | `{% load static %}` + `{% static %}` CSS + `{{ block.super }}` | Asset Management + Template Architecture |
| 3 | 이미지 경로 `{% static %}` 변환 + `alt` 추가 | Asset Management |
| 4 | `{% include %}` + `only` 키워드 | Template Architecture |
| 5 | 인라인 스타일 -> CSS Custom Property 토큰 | Design System |
| 6 | `{{ products_json }}` -> `json_script` 필터 | Asset Management (XSS 방지) |
| 7 | CDN SRI 속성 + `defer` + Django 주석 | Asset Management |
| 8 | 인라인 JS -> 별도 파일 + DOM API + CSRF 준비 | Asset Management + View Layer |
| 9 | `{% endblock %}` 블록명 명시 | Template Architecture |
| 10 | `onchange` 인라인 핸들러 -> JS 이벤트 바인딩 | Asset Management (CSP 호환) |

### 추가 권장 사항

- **HTMX 전환 검토**: `filterProducts`의 `fetch` + DOM 조작 패턴은 HTMX로 대체하면 JS 코드 없이 서버 렌더 HTML 조각으로 상품 목록을 업데이트할 수 있다. `<select hx-get="/products/filtered/" hx-target="#product-list" hx-swap="innerHTML">` 패턴을 고려하라.
- **LoginRequiredMixin**: 상품 목록이 인증된 사용자만 접근해야 하는 페이지라면 `LoginRequiredMixin`을 `TemplateView` 앞에 추가한다.
- **상품 이미지 처리**: 상품 이미지가 사용자 업로드 파일이라면 `{% static %}`이 아닌 `{{ product.image.url }}`(Django `ImageField`)을 사용해야 한다.
