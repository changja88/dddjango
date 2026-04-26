# Django 템플릿 코드 리뷰

## 발견된 문제

### 1. `{% load static %}` 누락 (심각)

`{% static %}` 태그를 사용하고 있지만 템플릿 상단에 `{% load static %}`이 없다. 이 상태로는 `TemplateSyntaxError`가 발생한다.

```htmldjango
{% extends "base_orders.html" %}
{% load static %}
```

`{% extends %}`는 반드시 첫 번째 태그여야 하므로 `{% load static %}`은 그 바로 다음에 위치해야 한다. 단, `base_orders.html`에서 이미 로드했더라도 자식 템플릿에는 전파되지 않으므로 반드시 각 템플릿마다 명시해야 한다.

### 2. `{{ orders_json }}` XSS 취약점 (심각)

`{{ orders_json }}`을 `<script>` 태그 안에서 직접 출력하고 있다. Django의 기본 자동 이스케이프는 HTML 컨텍스트 기준이므로 JavaScript 컨텍스트에서는 XSS 공격에 노출된다.

안전한 방법:

```htmldjango
{# 방법 1: json_script 필터 사용 (Django 2.1+, 권장) #}
{{ orders_json|json_script:"orders-data" }}
<script>
    const orders = JSON.parse(document.getElementById('orders-data').textContent);
</script>
```

`json_script` 필터는 `<`, `>`, `&` 등을 올바르게 이스케이프하여 스크립트 삽입 공격을 방지한다.

### 3. CSRF 토큰 누락 (심각)

`fetch`로 POST 요청을 보내면서 CSRF 토큰을 포함하지 않고 있다. Django의 CSRF 미들웨어가 활성화되어 있다면 403 Forbidden 응답이 반환된다.

```javascript
fetch('/api/orders/reorder/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({ order: orders.map(o => o.id) })
});
```

또는 쿠키에서 토큰을 읽는 유틸리티 함수를 사용한다:

```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

headers: { 'X-CSRFToken': getCookie('csrftoken') }
```

### 4. 페이지 로드 즉시 POST 요청 발생 (논리 오류)

현재 코드는 페이지가 로드될 때마다 무조건 reorder API를 호출한다. SortableJS를 로드하고 있으므로 드래그 앤 드롭으로 순서를 변경한 후에만 호출하는 것이 의도된 동작일 것이다.

```javascript
const el = document.querySelector('.order-list');
Sortable.create(el, {
    onEnd: function () {
        const ids = [...el.querySelectorAll('[data-order-id]')]
            .map(card => card.dataset.orderId);
        fetch('/api/orders/reorder/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ order: ids })
        });
    }
});
```

### 5. 외부 CDN 스크립트에 무결성 해시 없음 (보안)

외부 CDN에서 스크립트를 로드할 때는 `integrity` 속성과 `crossorigin` 속성을 추가하여 변조된 스크립트 실행을 방지해야 한다.

```html
<script
    src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    integrity="sha256-..."
    crossorigin="anonymous"></script>
```

또는 `{% static %}` 경로로 로컬에서 제공하는 방식도 고려할 수 있다.

### 6. fetch 에러 처리 없음

네트워크 실패나 서버 오류에 대한 처리가 전혀 없다.

```javascript
fetch('/api/orders/reorder/', { ... })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .catch(error => {
        console.error('순서 변경 실패:', error);
        // 사용자에게 오류를 알리거나 원래 순서로 복원
    });
```

### 7. 빈 목록에 대한 처리 없음 (사소)

`orders`가 빈 QuerySet일 때 빈 `<div>`만 렌더링된다. `{% empty %}` 태그로 안내 메시지를 표시하는 것이 좋다.

```htmldjango
{% for order in orders %}
    {% include "orders/order_card/order_card.html" with order=order %}
{% empty %}
    <p class="no-orders">주문 내역이 없습니다.</p>
{% endfor %}
```

## 수정된 전체 코드

```htmldjango
{% extends "base_orders.html" %}
{% load static %}

{% block title %}주문 목록{% endblock %}

{% block head_extra %}
    <link rel="stylesheet" href="{% static 'orders/css/orders.css' %}">
{% endblock %}

{% block body %}
<div class="order-list">
    {% for order in orders %}
        {% include "orders/order_card/order_card.html" with order=order %}
    {% empty %}
        <p class="no-orders">주문 내역이 없습니다.</p>
    {% endfor %}
</div>

<script
    src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    integrity="sha256-ipiJrswvAR4VAx/th+6zWsdeYmVae0iJuiR+6OqHJHQ="
    crossorigin="anonymous"></script>

{{ orders_json|json_script:"orders-data" }}

<script>
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    const el = document.querySelector('.order-list');
    if (el && el.children.length > 0) {
        Sortable.create(el, {
            onEnd: function () {
                const ids = [...el.querySelectorAll('[data-order-id]')]
                    .map(card => card.dataset.orderId);
                fetch('/api/orders/reorder/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ order: ids })
                })
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                })
                .catch(error => {
                    console.error('순서 변경 실패:', error);
                });
            }
        });
    }
</script>
{% endblock %}
```

## 요약

| # | 문제 | 심각도 |
|---|------|--------|
| 1 | `{% load static %}` 누락 | 심각 - 런타임 에러 |
| 2 | `{{ orders_json }}` XSS 취약점 | 심각 - 보안 |
| 3 | CSRF 토큰 누락 | 심각 - 요청 실패 |
| 4 | 페이지 로드 시 무조건 POST | 논리 오류 |
| 5 | CDN integrity 해시 없음 | 보안 |
| 6 | fetch 에러 처리 없음 | 개선 |
| 7 | 빈 목록 안내 없음 | 개선 |
