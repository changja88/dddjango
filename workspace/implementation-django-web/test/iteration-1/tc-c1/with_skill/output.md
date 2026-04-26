# Refactoring: orders/order_list.html

레거시 Django 템플릿을 프로젝트 컨벤션에 맞게 리팩토링한다. 각 변경 사항을 컨벤션과 연결하여 근거를 명시한다.

---

## 개별 변경 사항

### 1. 인라인 `<style>` 제거 -- 별도 CSS 파일로 분리

[Before]
```htmldjango
{% block body %}
<style>
    .order-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .order-card:hover { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .order-status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .status-confirmed { background-color: #d1fae5; color: #065f46; }
    .btn-action { background-color: #3b82f6; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
    .btn-action:hover { background-color: #2563eb; }
</style>
```

[After]
```htmldjango
{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/order_list.css' %}">
{% endblock head_extra %}
```

[Reason] Asset Management -- CSS 관리 규칙: HTML 템플릿에 `<style>` 인라인 작성 금지. 별도 `.css` 파일로 분리하고 `{% static %}` 태그로 참조한다. `head_extra` 블록에서 `{{ block.super }}`로 부모 콘텐츠를 유지하면서 추가한다.

---

### 2. 하드코딩된 색상/크기 값 -- CSS Custom Property 토큰으로 추출

[Before]
```css
.order-card { border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.order-card:hover { box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.order-status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
.status-pending { background-color: #fef3c7; color: #92400e; }
.status-confirmed { background-color: #d1fae5; color: #065f46; }
.btn-action { background-color: #3b82f6; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-action:hover { background-color: #2563eb; }
```

[After]
```css
/* orders/static/orders/css/order_list.css */

.order-card {
    border: 1px solid var(--card-border, var(--color-border, #e5e7eb));
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    padding: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-sm, 0.75rem);
}

.order-card:hover {
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.order-status-badge {
    display: inline-block;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-size: var(--text-sm, 0.875rem);
}

.status-pending {
    background-color: var(--color-warning-bg, #fef3c7);
    color: var(--color-warning-text, #92400e);
}

.status-confirmed {
    background-color: var(--color-success-bg, #d1fae5);
    color: var(--color-success-text, #065f46);
}

.btn-action {
    background-color: var(--btn-bg, var(--color-primary, #3b82f6));
    color: var(--btn-text, #ffffff);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border: none;
    border-radius: var(--radius-sm, 0.25rem);
    cursor: pointer;
}

.btn-action:hover {
    background-color: var(--btn-bg-hover, var(--color-primary-hover, #2563eb));
}
```

[Reason] Design System -- 디자인 토큰: 하드코딩된 색상, 간격, 크기 값을 CSS Custom Properties로 교체한다. 3계층 토큰(primitive -> semantic -> component)을 참조하고, `var()` 폴백 값을 포함하여 토큰 미정의 시에도 동작을 보장한다.

---

### 3. `{{ order.id }}` in `<script>` -- `json_script` 필터로 변환

[Before]
```htmldjango
<button class="btn-action" onclick="confirmOrder({{ order.id }})">확정</button>
...
<script>
function confirmOrder(orderId) {
    axios.post('/api/orders/' + orderId + '/confirm/')
        .then(function(response) {
            location.reload();
        });
}
</script>
```

[After]
```htmldjango
<button class="btn-action" data-order-id="{{ order.id }}" data-action="confirm">확정</button>
```

```htmldjango
{# 서버 -> JS 데이터 전달: 주문 확정 API 엔드포인트 #}
{{ confirm_api_url_template|json_script:"confirm-api-url-template" }}
```

```javascript
// orders/static/orders/js/order_list.js
(function () {
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

    const urlTemplate = JSON.parse(
        document.getElementById('confirm-api-url-template').textContent
    );

    document.querySelectorAll('[data-action="confirm"]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const orderId = this.dataset.orderId;
            const url = urlTemplate.replace('__ID__', orderId);
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                mode: 'same-origin',
            }).then(function () {
                location.reload();
            });
        });
    });
})();
```

[Reason] Asset Management -- JavaScript 관리 규칙: `{{ value }}`를 `<script>` 내부에서 직접 사용하면 XSS 위험이 있다. `json_script` 필터로 안전하게 데이터를 전달하고, 인라인 `onclick` 핸들러 대신 data attribute + `addEventListener`로 비즈니스 로직을 별도 `.js` 파일로 분리한다.

---

### 4. AJAX POST에 CSRF 토큰 누락 -- `X-CSRFToken` 헤더 추가

[Before]
```javascript
axios.post('/api/orders/' + orderId + '/confirm/')
    .then(function(response) {
        location.reload();
    });
```

[After]
```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
    },
    mode: 'same-origin',
}).then(function () {
    location.reload();
});
```

[Reason] View Layer -- AJAX CSRF 보호: Django의 CSRF 보호 메커니즘을 준수해야 한다. POST 요청 시 `X-CSRFToken` 헤더에 쿠키에서 가져온 CSRF 토큰을 포함해야 한다. `mode: "same-origin"` 설정도 권장된다.

---

### 5. CDN 스크립트에 SRI 속성 누락 -- `integrity`와 `crossorigin` 추가

[Before]
```htmldjango
<script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
```

[After]
CDN 의존성을 제거하고 네이티브 `fetch` API를 사용한다. 만약 CDN 라이브러리가 필요한 경우 아래 형태를 따른다:

```htmldjango
{# Axios -- HTTP 클라이언트 라이브러리 #}
<script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"
        integrity="sha384-<해시값>"
        crossorigin="anonymous"></script>
```

[Reason] Asset Management -- SRI (Subresource Integrity): CDN에서 외부 스크립트를 로드할 때 `integrity`와 `crossorigin` 속성을 반드시 포함해야 한다. 이 리팩토링에서는 `fetch` API가 충분하므로 CDN 의존성 자체를 제거한다.

---

### 6. 인라인 앱 `<script>` -- 별도 static JS 파일로 분리

[Before]
```htmldjango
<script>
function confirmOrder(orderId) {
    axios.post('/api/orders/' + orderId + '/confirm/')
        .then(function(response) {
            location.reload();
        });
}
</script>
```

[After]
```htmldjango
{% block scripts %}
    {{ block.super }}
    {# 서버 -> JS 데이터 전달: 주문 확정 API 엔드포인트 #}
    {{ confirm_api_url_template|json_script:"confirm-api-url-template" }}
    {# 주문 목록 인터랙션 스크립트 #}
    <script src="{% static 'orders/js/order_list.js' %}"></script>
{% endblock scripts %}
```

[Reason] Asset Management -- JavaScript 관리 규칙: HTML 컴포넌트에 앱 로직을 인라인 `<script>`로 작성하지 않는다. 비즈니스 로직은 `static/<app>/js/<component>.js`에 배치한다. 서버 데이터는 `json_script`로 전달하고, 앱 스크립트는 그 뒤에 로드하여 올바른 순서를 보장한다.

---

### 7. `{% endblock %}` 에 블록명 미표기

[Before]
```htmldjango
{% block body %}
...
{% endblock %}
```

[After]
```htmldjango
{% block body %}
...
{% endblock body %}
```

[Reason] Template Architecture -- 블록 닫기: `{% endblock name %}`에 블록명을 명시하면 가독성이 향상된다. 템플릿이 길어질수록 어떤 블록이 닫히는지 식별하기 쉬워진다.

---

### 8. `{% load static %}` 누락

[Before]
```htmldjango
{% extends "base.html" %}
{% block body %}
```

[After]
```htmldjango
{% extends "base.html" %}
{% load static %}
```

[Reason] Template Architecture -- 템플릿 상속 규칙: `{% load %}` 태그는 상속되지 않는다. `{% static %}` 태그를 사용하는 자식 템플릿에서는 반드시 `{% load static %}` 을 별도로 선언해야 한다.

---

### 9. HTMX 고려 -- `fetch()` AJAX를 HTMX로 대체 가능

[Before]
```htmldjango
<button class="btn-action" onclick="confirmOrder({{ order.id }})">확정</button>
```

[After (HTMX alternative)]
```htmldjango
<button class="btn-action"
        hx-post="{% url 'web:confirm-order' order.id %}"
        hx-target="#order-{{ order.id }}"
        hx-swap="outerHTML">
    확정
</button>
```

[Reason] View Layer -- HTMX: HTMX를 사용하면 JavaScript를 작성하지 않고도 서버 렌더링 HTML 조각으로 DOM을 업데이트할 수 있다. 주문 확정 후 해당 카드만 교체하면 되므로 `location.reload()` 대신 부분 업데이트가 적합하다. HTMX가 프로젝트에 도입된 경우 이 방식을 권장한다. 아래 완성 코드에서는 범용성을 위해 `fetch` 기반으로 제시하되, HTMX 버전도 함께 포함한다.

---

## 완성 리팩토링 코드

### 파일 구조

```
orders/
├── static/
│   └── orders/
│       ├── css/
│       │   └── order_list.css
│       └── js/
│           └── order_list.js
└── templates/
    └── orders/
        └── order_list.html
```

### orders/templates/orders/order_list.html

```htmldjango
{# orders/order_list.html #}
{% extends "base.html" %}
{% load static %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/order_list.css' %}">
{% endblock head_extra %}

{% block body %}
<div class="container">
    <h1>주문 관리</h1>
    {% for order in orders %}
    <div class="order-card" id="order-{{ order.id }}">
        <h3>주문 #{{ order.id }}</h3>
        <p>{{ order.customer_name }} - {{ order.total|floatformat:0 }}원</p>
        <span class="order-status-badge status-{{ order.status }}">
            {{ order.get_status_display }}
        </span>
        {% if order.status == 'pending' %}
        <button class="btn-action"
                data-order-id="{{ order.id }}"
                data-action="confirm">
            확정
        </button>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock body %}

{% block scripts %}
    {{ block.super }}
    {# 서버 -> JS 데이터 전달: 주문 확정 API URL 템플릿 #}
    {{ confirm_api_url_template|json_script:"confirm-api-url-template" }}
    {# 주문 목록 인터랙션 스크립트 #}
    <script src="{% static 'orders/js/order_list.js' %}"></script>
{% endblock scripts %}
```

### orders/static/orders/css/order_list.css

```css
/* order_list.css -- 주문 목록 페이지 스타일 */

.order-card {
    border: 1px solid var(--card-border, var(--color-border, #e5e7eb));
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    padding: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-sm, 0.75rem);
}

.order-card:hover {
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.order-status-badge {
    display: inline-block;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-size: var(--text-sm, 0.875rem);
}

.status-pending {
    background-color: var(--color-warning-bg, #fef3c7);
    color: var(--color-warning-text, #92400e);
}

.status-confirmed {
    background-color: var(--color-success-bg, #d1fae5);
    color: var(--color-success-text, #065f46);
}

.btn-action {
    background-color: var(--btn-bg, var(--color-primary, #3b82f6));
    color: var(--btn-text, #ffffff);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border: none;
    border-radius: var(--radius-sm, 0.25rem);
    cursor: pointer;
    transition: background-color var(--transition-duration, 200ms);
}

.btn-action:hover {
    background-color: var(--btn-bg-hover, var(--color-primary-hover, #2563eb));
}

.btn-action:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px var(--color-focus-ring, #2563eb));
}
```

### orders/static/orders/js/order_list.js

```javascript
/* order_list.js -- 주문 목록 인터랙션 */
(function () {
    'use strict';

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

    const urlTemplate = JSON.parse(
        document.getElementById('confirm-api-url-template').textContent
    );

    document.querySelectorAll('[data-action="confirm"]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const orderId = this.dataset.orderId;
            const url = urlTemplate.replace('__ID__', orderId);

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                mode: 'same-origin',
            }).then(function (response) {
                if (response.ok) {
                    location.reload();
                }
            });
        });
    });
})();
```

### 뷰 컨텍스트 예시 (참고)

뷰의 `get_context_data`에서 URL 템플릿을 전달해야 한다:

```python
class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = OrderService.get_list(user=self.request.user)
        ctx["confirm_api_url_template"] = "/api/orders/__ID__/confirm/"
        return ctx
```

### HTMX 대안 (참고)

프로젝트에 HTMX가 도입된 경우, JavaScript 파일과 `json_script` 없이 더 간결하게 구현할 수 있다:

```htmldjango
{# orders/order_list.html -- HTMX 버전 #}
{% extends "base.html" %}
{% load static %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/order_list.css' %}">
{% endblock head_extra %}

{% block body %}
<div class="container">
    <h1>주문 관리</h1>
    {% for order in orders %}
    <div class="order-card" id="order-{{ order.id }}">
        <h3>주문 #{{ order.id }}</h3>
        <p>{{ order.customer_name }} - {{ order.total|floatformat:0 }}원</p>
        <span class="order-status-badge status-{{ order.status }}">
            {{ order.get_status_display }}
        </span>
        {% if order.status == 'pending' %}
        <button class="btn-action"
                hx-post="{% url 'web:confirm-order' order.id %}"
                hx-target="#order-{{ order.id }}"
                hx-swap="outerHTML">
            확정
        </button>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock body %}
```

---

## 적용 체크리스트

| # | 항목 | 적용 |
|---|------|------|
| 1 | 하드코딩된 static path -> `{% static %}` | O -- CSS, JS 파일을 `{% static %}` 태그로 참조 |
| 2 | `{{ value }}` in script -> `json_script` | O -- `order.id`를 인라인 삽입하던 패턴을 `json_script` + data attribute로 전환 |
| 3 | CDN without SRI -> `integrity` + `crossorigin` 추가 | O -- CDN 의존성(axios)을 제거하고 네이티브 `fetch`로 대체 |
| 4 | AJAX without CSRF -> `X-CSRFToken` 헤더 추가 | O -- `getCookie('csrftoken')` 패턴으로 CSRF 토큰 포함 |
| 5 | `{% include %}` without `only` -> `only` 추가 | N/A -- 이 템플릿에 `{% include %}` 사용 없음 |
| 6 | 하드코딩된 색상/크기 -> CSS Custom Property 토큰 | O -- 모든 값을 `var()` + 폴백으로 교체 |
| 7 | 외부 컴포넌트 스타일 오버라이드 -> 디자인 시스템 modifier | N/A -- 외부 오버라이드 없음 |
| 8 | 인라인 `<style>` -> 별도 CSS 파일 | O -- `orders/static/orders/css/order_list.css`로 분리 |
| 9 | 인라인 app `<script>` -> `static/` JS 파일 | O -- `orders/static/orders/js/order_list.js`로 분리 |
| 10 | Missing `{{ block.super }}` -> 추가 | O -- `head_extra`, `scripts` 블록에 `{{ block.super }}` 추가 |
| 11 | Flat 템플릿 -> 컴포넌트 폴더 | N/A -- 단일 페이지 수준이므로 예외 허용 |
| 12 | No access control -> `LoginRequiredMixin` 추가 | O -- 뷰 예시에 `LoginRequiredMixin` 적용 |
| 13 | No error handling in view -> try/except 추가 | N/A -- 직접 서비스 호출 패턴이므로 Internal API Client 에러 처리 불필요 |
| 14 | Raw `fetch()` AJAX -> HTMX 고려 | O -- HTMX 대안 코드 별도 제시 |
