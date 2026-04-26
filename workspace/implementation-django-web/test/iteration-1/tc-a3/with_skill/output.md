# 주문 상세 페이지 -- HTMX 상태 변경 구현

주문 상세 페이지에서 HTMX를 사용하여 주문 상태를 변경(대기 -> 확정)하고,
서버 렌더링 HTML 조각으로 해당 주문 카드만 교체하는 구현이다.

---

## 폴더 구조

```
web/
├── views/
│   └── orders/
│       ├── __init__.py
│       └── views.py
├── view_urls.py
└── templates/
    └── orders/
        ├── order_detail_root.html
        ├── order_card/
        │   └── order_card.html
        └── order_detail/
            ├── order_detail.html
            └── order_detail-scripts.html

orders/
└── services.py
```

---

## 1. 서비스 레이어

```python
# orders/services.py
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    title: str
    status: str
    total_amount: int
    created_at: str


class OrderService:
    @staticmethod
    def get_detail(order_id: int, user) -> Order:
        """주문 상세 정보를 반환한다."""
        # 실제 구현에서는 Repository를 통해 DB에서 조회
        ...

    @staticmethod
    def confirm(order_id: int, user) -> Order:
        """주문 상태를 대기에서 확정으로 변경한다."""
        # 실제 구현에서는 상태 검증 후 업데이트
        ...
```

---

## 2. 뷰

```python
# web/views/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import TemplateView

from orders.services import OrderService


class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_detail_root.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_id = self.kwargs["order_id"]
        try:
            ctx["order"] = OrderService.get_detail(
                order_id=order_id, user=self.request.user
            )
        except Exception:
            ctx["order"] = None
            ctx["error_message"] = "주문 정보를 불러올 수 없습니다."
        return ctx


class ConfirmOrderView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, order_id):
        try:
            order = OrderService.confirm(order_id=order_id, user=request.user)
        except Exception:
            return HttpResponseBadRequest("주문 상태를 변경할 수 없습니다.")

        if request.headers.get("HX-Request"):
            return TemplateResponse(
                request,
                "orders/order_card/order_card.html",
                {"order": order},
            )
        return redirect("web:order-detail", order_id=order_id)
```

`LoginRequiredMixin`이 `TemplateView`/`View` 앞에 위치하여 MRO 순서를 준수한다.
`ConfirmOrderView`는 HTMX 요청 여부(`HX-Request` 헤더)에 따라 HTML 조각 또는
전체 페이지 리다이렉트를 반환한다. 서비스 호출 실패 시 에러 처리가 포함되어 있다.

---

## 3. URL 설정

```python
# web/view_urls.py
from django.urls import path

from web.views.orders.views import ConfirmOrderView, OrderDetailView

app_name = "web"

urlpatterns = [
    path(
        "orders/<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
    path(
        "orders/<int:order_id>/confirm/",
        ConfirmOrderView.as_view(),
        name="confirm-order",
    ),
]
```

---

## 4. 템플릿

### 4-1. Root 템플릿

```htmldjango
{# orders/order_detail_root.html #}
{% extends "base.html" %}

{% block title %}주문 상세{% endblock title %}

{% block body %}
  {% include "orders/order_detail/order_detail.html" with order=order error_message=error_message only %}
{% endblock body %}

{% block scripts %}
  {{ block.super }}
  {% include "orders/order_detail/order_detail-scripts.html" %}
{% endblock scripts %}
```

`{% extends %}`가 첫 번째 태그이다. `{% include %}`에 `only` 키워드를 사용하여
컨텍스트를 명시적으로 제한한다. `{{ block.super }}`로 부모의 scripts 블록을
유지하면서 페이지 스크립트를 추가한다.

### 4-2. 주문 상세 섹션

```htmldjango
{# orders/order_detail/order_detail.html #}
{# 필수 변수: order (Order 객체 또는 None), error_message (str, 선택적) #}
{% load static %}

<div class="order-detail">
  <h1 class="order-detail__title">주문 상세</h1>

  {% if error_message %}
    <div class="order-detail__error" role="alert">
      {{ error_message }}
    </div>
  {% elif order %}
    {% include "orders/order_card/order_card.html" with order=order only %}
  {% endif %}
</div>
```

### 4-3. 주문 카드 컴포넌트 (HTMX 교체 대상)

```htmldjango
{# orders/order_card/order_card.html #}
{# 필수 변수: order (Order 객체) #}
{% load static %}

<div id="order-{{ order.id }}" class="order-card">
  <div class="order-card__header">
    <h2 class="order-card__number">주문 #{{ order.id }}</h2>
    <span class="order-card__status order-card__status--{{ order.status }}">
      {{ order.get_status_display }}
    </span>
  </div>

  <dl class="order-card__details">
    <dt class="order-card__label">주문명</dt>
    <dd class="order-card__value">{{ order.title }}</dd>

    <dt class="order-card__label">총 금액</dt>
    <dd class="order-card__value">{{ order.total_amount|floatformat:"0" }}원</dd>

    <dt class="order-card__label">주문일</dt>
    <dd class="order-card__value">{{ order.created_at }}</dd>
  </dl>

  {% if order.status == "pending" %}
    <div class="order-card__actions">
      <button hx-post="{% url 'web:confirm-order' order.id %}"
              hx-target="#order-{{ order.id }}"
              hx-swap="outerHTML"
              hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'
              class="order-card__confirm-btn">
        주문 확정
      </button>
    </div>
  {% endif %}
</div>
```

HTMX 속성 설명:
- `hx-post`: `ConfirmOrderView`로 POST 요청을 전송한다.
- `hx-target`: 교체할 DOM 요소를 `#order-{{ order.id }}`로 지정한다.
- `hx-swap="outerHTML"`: 대상 요소 전체를 서버 응답 HTML로 교체한다.
- `hx-headers`: CSRF 토큰을 `X-CSRFToken` 헤더로 포함하여 Django CSRF 보호를 준수한다.

상태가 `pending`일 때만 확정 버튼이 노출된다. 서버에서 상태 변경 후 렌더링된
카드에는 버튼이 사라지므로 중복 클릭이 방지된다.

### 4-4. 스크립트 로드

```htmldjango
{# orders/order_detail/order_detail-scripts.html #}

{# HTMX -- 서버 렌더 HTML 조각으로 DOM 업데이트 #}
<script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"
        integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+"
        crossorigin="anonymous"></script>
```

CDN에서 HTMX를 로드하며, `integrity`와 `crossorigin` 속성을 포함하여 SRI를 준수한다.

---

## 5. CSS

```css
/* orders/static/orders/css/order_detail.css */

.order-detail {
  max-width: 40rem;
  margin: var(--spacing-xl, 2rem) auto;
  padding: 0 var(--spacing-md, 1rem);
}

.order-detail__title {
  font-size: var(--text-lg, 1.125rem);
  font-weight: 600;
  color: var(--color-text, #1f2937);
  margin-bottom: var(--spacing-lg, 1.5rem);
}

.order-detail__error {
  padding: var(--spacing-md, 1rem);
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md, 0.5rem);
}
```

```css
/* orders/static/orders/css/order_card.css */

.order-card {
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--card-radius, var(--radius-md, 0.5rem));
  padding: var(--spacing-lg, 1.5rem);
  background-color: var(--color-bg, #ffffff);
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.order-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md, 1rem);
}

.order-card__number {
  font-size: var(--text-lg, 1.125rem);
  font-weight: 600;
  color: var(--color-text, #1f2937);
  margin: 0;
}

.order-card__status {
  display: inline-block;
  padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
  border-radius: var(--radius-sm, 0.25rem);
  font-size: var(--text-sm, 0.875rem);
  font-weight: 500;
}

.order-card__status--pending {
  background-color: #fef3c7;
  color: #92400e;
}

.order-card__status--confirmed {
  background-color: #d1fae5;
  color: #065f46;
}

.order-card__details {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--spacing-xs, 0.25rem) var(--spacing-md, 1rem);
  margin: 0 0 var(--spacing-lg, 1.5rem) 0;
}

.order-card__label {
  font-size: var(--text-sm, 0.875rem);
  color: var(--color-text-muted, #6b7280);
}

.order-card__value {
  font-size: var(--text-sm, 0.875rem);
  color: var(--color-text, #1f2937);
  margin: 0;
}

.order-card__actions {
  padding-top: var(--spacing-md, 1rem);
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.order-card__confirm-btn {
  display: inline-block;
  padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
  background-color: var(--btn-bg, var(--color-primary, #3b82f6));
  color: var(--btn-text, #ffffff);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  font-size: var(--text-sm, 0.875rem);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-duration, 200ms) ease;
}

.order-card__confirm-btn:hover {
  background-color: var(--btn-bg-hover, var(--color-primary-hover, #1d4ed8));
}

.order-card__confirm-btn:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

@media (prefers-reduced-motion: reduce) {
  .order-card__confirm-btn {
    transition: none;
  }
}
```

모든 색상, 간격, 크기 값은 CSS Custom Properties로 참조하며 `var()` 폴백을
포함한다. 포커스 링과 `prefers-reduced-motion` 접근성 토큰을 적용하였다.

---

## 동작 흐름

```
1. [브라우저] GET /orders/42/
   -> OrderDetailView.get_context_data()
      -> OrderService.get_detail(42, user)
   <- order_detail_root.html 렌더링 (order_card 포함, 상태=pending, 확정 버튼 노출)

2. [사용자] "주문 확정" 버튼 클릭
   -> [HTMX] POST /orders/42/confirm/  (HX-Request: true, X-CSRFToken 포함)
   -> ConfirmOrderView.post()
      -> OrderService.confirm(42, user)
   <- order_card.html 조각 렌더링 (상태=confirmed, 확정 버튼 없음)

3. [HTMX] #order-42 요소를 응답 HTML로 outerHTML 교체
   -> 주문 카드가 확정 상태로 갱신, 전체 페이지 리로드 없음
```
