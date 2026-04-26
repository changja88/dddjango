# Django Template Refactoring: `orders/order_list.html`

## 원본 코드 문제점 분석

| # | 문제 | 심각도 | 카테고리 |
|---|------|--------|----------|
| 1 | `<style>` 블록이 템플릿 안에 인라인으로 존재 | 중간 | 유지보수성 |
| 2 | inline `onclick` 핸들러 사용 | 높음 | 보안/유지보수성 |
| 3 | 외부 CDN(axios)을 직접 로드 | 중간 | 성능/보안 |
| 4 | CSRF 토큰 없이 POST 요청 수행 | 높음 | 보안 |
| 5 | API 호출 실패 시 에러 처리 없음 | 높음 | 안정성 |
| 6 | `location.reload()`로 전체 페이지 새로고침 | 중간 | UX/성능 |
| 7 | 빈 목록에 대한 `{% empty %}` 처리 없음 | 낮음 | UX |
| 8 | 금액 표시에 `intcomma` 미사용 | 낮음 | UX |
| 9 | `{% block %}` 분리 안 됨 (css/js/body 혼재) | 중간 | 구조 |

---

## 리팩토링 결과

### 1. 템플릿: `orders/order_list.html`

```htmldjango
{# orders/order_list.html #}
{% extends "base.html" %}
{% load humanize %}

{% block title %}주문 관리{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'orders/css/order_list.css' %}">
{% endblock %}

{% block body %}
<div class="container">
    <h1>주문 관리</h1>

    {% for order in orders %}
    <div class="order-card" data-order-id="{{ order.id }}">
        <div class="order-card__header">
            <h3>주문 #{{ order.id }}</h3>
            <span class="order-status-badge status-{{ order.status }}">
                {{ order.get_status_display }}
            </span>
        </div>
        <p class="order-card__detail">
            {{ order.customer_name }} &mdash; {{ order.total|floatformat:0|intcomma }}원
        </p>
        {% if order.status == 'pending' %}
        <button class="btn-action js-confirm-order" data-order-id="{{ order.id }}">
            확정
        </button>
        {% endif %}
    </div>
    {% empty %}
    <p class="empty-state">등록된 주문이 없습니다.</p>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script>
(function() {
    "use strict";

    const CSRF_TOKEN = "{{ csrf_token }}";

    document.addEventListener("click", function(e) {
        const btn = e.target.closest(".js-confirm-order");
        if (!btn) return;

        const orderId = btn.dataset.orderId;
        if (!orderId) return;

        btn.disabled = true;
        btn.textContent = "처리 중...";

        fetch(`/api/orders/${orderId}/confirm/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN,
                "Content-Type": "application/json",
            },
        })
        .then(function(response) {
            if (!response.ok) throw new Error("확정 요청 실패: " + response.status);
            return response.json();
        })
        .then(function(data) {
            const card = btn.closest(".order-card");
            const badge = card.querySelector(".order-status-badge");
            badge.className = "order-status-badge status-confirmed";
            badge.textContent = "확정됨";
            btn.remove();
        })
        .catch(function(err) {
            alert("주문 확정에 실패했습니다. 다시 시도해주세요.");
            btn.disabled = false;
            btn.textContent = "확정";
            console.error(err);
        });
    });
})();
</script>
{% endblock %}
```

### 2. 스타일시트: `static/orders/css/order_list.css`

```css
/* static/orders/css/order_list.css */
.order-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.15s ease;
}

.order-card:hover {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.order-card__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.order-card__detail {
    margin: 8px 0;
    color: #374151;
}

.order-status-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.status-pending {
    background-color: #fef3c7;
    color: #92400e;
}

.status-confirmed {
    background-color: #d1fae5;
    color: #065f46;
}

.btn-action {
    background-color: #3b82f6;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.15s ease;
}

.btn-action:hover {
    background-color: #2563eb;
}

.btn-action:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
}

.empty-state {
    text-align: center;
    color: #6b7280;
    padding: 32px 0;
}
```

### 3. 뷰: `orders/views.py` (참고)

```python
# orders/views.py
from django.views.generic import ListView
from .models import Order


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    ordering = ["-created_at"]
```

### 4. `base.html` 블록 구조 (전제 조건)

리팩토링된 템플릿이 올바르게 동작하려면 `base.html`에 다음 블록이 정의되어 있어야 한다.

```htmldjango
{# base.html - 필요한 블록 구조 #}
{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>{% block title %}{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block body %}{% endblock %}
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 변경 사항 요약

### 보안

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| CSRF | 토큰 미포함 | `X-CSRFToken` 헤더에 `{{ csrf_token }}` 포함 |
| 이벤트 바인딩 | inline `onclick` | 이벤트 위임 (`document.addEventListener`) |
| 외부 의존성 | axios CDN 직접 로드 | 네이티브 `fetch` API 사용 (CDN 제거) |

### 구조

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| CSS | 템플릿 내 `<style>` 인라인 | 별도 정적 파일(`order_list.css`)로 분리 |
| JS | 글로벌 함수 `confirmOrder()` | IIFE로 감싸 스코프 격리 |
| 블록 | `body` 블록 하나에 전부 | `title`, `extra_css`, `body`, `extra_js` 분리 |

### UX / 안정성

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 빈 목록 | 표시 없음 | `{% empty %}` 태그로 안내 메시지 |
| 금액 포맷 | `floatformat:0` | `floatformat:0 + intcomma` (천 단위 구분) |
| 확정 후 동작 | `location.reload()` 전체 새로고침 | DOM 직접 업데이트 (badge 변경, 버튼 제거) |
| 에러 처리 | 없음 | `catch` 블록에서 alert + 버튼 복구 |
| 중복 클릭 | 방지 없음 | `btn.disabled = true` + 텍스트 변경 |
