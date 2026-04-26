# Django + HTMX 주문 상태 변경 구현

주문 상세 페이지에서 HTMX를 사용하여 주문 상태를 변경(대기 -> 확정)하는 기능 구현.
상태 변경 버튼 클릭 시 서버에서 렌더링한 HTML 조각으로 해당 주문 카드만 교체한다.

---

## 프로젝트 구조

```
orders/
    __init__.py
    models.py
    services.py
    views.py
    urls.py
    templates/
        orders/
            order_detail.html
            _order_card.html       # HTMX partial (HTML 조각)
```

---

## 1. Model (`orders/models.py`)

```python
from django.db import models
from django.conf import settings


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        CONFIRMED = "confirmed", "확정"
        CANCELLED = "cancelled", "취소"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"
```

---

## 2. Service Layer (`orders/services.py`)

```python
from django.shortcuts import get_object_or_404
from orders.models import Order


class OrderService:
    @staticmethod
    def get_order(order_id: int, user) -> Order:
        """인증된 사용자의 주문을 조회한다."""
        return get_object_or_404(Order, pk=order_id, user=user)

    @staticmethod
    def confirm_order(order_id: int, user) -> Order:
        """대기 상태의 주문을 확정으로 변경한다.

        현재 상태가 PENDING이 아니면 ValueError를 발생시킨다.
        """
        order = get_object_or_404(Order, pk=order_id, user=user)
        if order.status != Order.Status.PENDING:
            raise ValueError(
                f"상태가 '{order.get_status_display()}'인 주문은 확정할 수 없습니다."
            )
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=["status", "updated_at"])
        return order
```

---

## 3. Views (`orders/views.py`)

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from orders.services import OrderService


@login_required
def order_detail(request, order_id):
    """주문 상세 페이지 (전체 HTML)."""
    order = OrderService.get_order(order_id, request.user)
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_confirm(request, order_id):
    """HTMX 요청: 주문 상태를 확정으로 변경하고 HTML 조각을 반환한다."""
    if request.method != "POST":
        return HttpResponseBadRequest("POST 요청만 허용됩니다.")

    try:
        order = OrderService.confirm_order(order_id, request.user)
    except ValueError as e:
        return HttpResponseBadRequest(str(e))

    return render(request, "orders/_order_card.html", {"order": order})
```

---

## 4. URL Configuration (`orders/urls.py`)

```python
from django.urls import path
from orders import views

app_name = "orders"

urlpatterns = [
    path("<int:order_id>/", views.order_detail, name="detail"),
    path("<int:order_id>/confirm/", views.order_confirm, name="confirm"),
]
```

프로젝트 루트 `urls.py`에 포함:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("orders/", include("orders.urls")),
]
```

---

## 5. Templates

### 5-1. 주문 상세 페이지 (`orders/templates/orders/order_detail.html`)

```html
{% extends "base.html" %}

{% block title %}주문 #{{ order.pk }}{% endblock %}

{% block extra_head %}
<script src="https://unpkg.com/htmx.org@2.0.4"
        integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+"
        crossorigin="anonymous"></script>
{% endblock %}

{% block content %}
<h1>주문 상세</h1>

<div id="order-card-{{ order.pk }}">
    {% include "orders/_order_card.html" with order=order %}
</div>
{% endblock %}
```

### 5-2. 주문 카드 HTML 조각 (`orders/templates/orders/_order_card.html`)

HTMX 응답으로도 사용되는 partial 템플릿이다.

```html
<div class="order-card" id="order-card-{{ order.pk }}">
    <h2>주문 #{{ order.pk }}</h2>
    <p>금액: {{ order.total_amount|floatformat:0 }}원</p>
    <p>상태:
        <span class="badge
            {% if order.status == 'pending' %}badge-pending
            {% elif order.status == 'confirmed' %}badge-confirmed
            {% endif %}">
            {{ order.get_status_display }}
        </span>
    </p>
    <p>주문일시: {{ order.created_at|date:"Y-m-d H:i" }}</p>

    {% if order.status == "pending" %}
    <button hx-post="{% url 'orders:confirm' order.pk %}"
            hx-target="#order-card-{{ order.pk }}"
            hx-swap="outerHTML"
            hx-confirm="주문을 확정하시겠습니까?"
            class="btn btn-confirm">
        주문 확정
    </button>
    {% else %}
    <span class="status-done">확정 완료</span>
    {% endif %}
</div>
```

---

## 6. 동작 흐름

```
1. 사용자가 /orders/<id>/ 에 접근
2. login_required 데코레이터가 인증 확인
3. OrderService.get_order()로 주문 조회 -> order_detail.html 렌더링
4. HTMX CDN 스크립트가 로드됨
5. "주문 확정" 버튼 클릭
   -> hx-confirm 으로 확인 다이얼로그 표시
   -> POST /orders/<id>/confirm/ 으로 HTMX 요청
6. order_confirm 뷰에서 OrderService.confirm_order() 호출
   -> 상태를 pending -> confirmed 으로 변경
   -> _order_card.html 조각 렌더링하여 응답
7. HTMX가 hx-target으로 지정된 #order-card-<id> 요소를
   hx-swap="outerHTML" 방식으로 교체
8. 교체된 카드에는 버튼 대신 "확정 완료" 텍스트가 표시됨
```

---

## 7. CSRF 처리

Django는 POST 요청에 CSRF 토큰을 요구한다. HTMX가 자동으로 CSRF 토큰을 포함하도록 `base.html`의 `<body>` 태그에 다음 속성을 추가한다.

```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

또는 `<meta>` 태그와 JavaScript 조합을 사용할 수도 있다:

```html
<head>
    <meta name="csrf-token" content="{{ csrf_token }}">
</head>
```

```javascript
document.body.addEventListener("htmx:configRequest", function (event) {
    event.detail.headers["X-CSRFToken"] =
        document.querySelector('meta[name="csrf-token"]').content;
});
```

---

## 8. 핵심 포인트 정리

| 항목 | 구현 방식 |
|---|---|
| HTMX 로드 | CDN (`unpkg.com/htmx.org@2.0.4`) |
| 주문 데이터 조회 | `OrderService.get_order()` (서비스 레이어) |
| 상태 변경 로직 | `OrderService.confirm_order()` (서비스 레이어) |
| 인증 | `@login_required` 데코레이터 |
| 부분 교체 | `hx-post` + `hx-target` + `hx-swap="outerHTML"` |
| HTML 조각 | `_order_card.html` partial 템플릿 |
| CSRF | `hx-headers` 속성으로 토큰 전송 |
| 상태 검증 | 서비스 레이어에서 PENDING 상태만 확정 허용 |
