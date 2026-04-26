# /web 커맨드 실행 결과

**사용자 요청:** "주문 내역 조회 페이지를 만들어줘. 주문 목록이랑 상세 페이지가 필요해."

---

## 1단계: 스킬 로드

### 기본 스킬 (항상 적용):
1. **implementation-cleancode** -- 클린 코드 원칙 (네이밍, 함수, 추상화, SOLID, 리팩토링)
2. **implementation-python** -- Python 3.10+ 컨벤션 (타입 힌트, dataclasses, Protocol, match/case)
3. **implementation-django** -- Django 5.x 컨벤션 (모델, QuerySet, CBV, 서비스 레이어)

### 커맨드 전용 스킬:
4. **implementation-django-web** -- Django 웹 프론트엔드 (템플릿 상속, 컴포넌트, 정적 파일, 디자인 시스템, TemplateView)

### 로드된 레퍼런스 파일:
- `implementation-cleancode/references/naming.md` -- 네이밍 원칙
- `implementation-django-web/references/template-architecture.md` -- 템플릿 아키텍처
- `implementation-django-web/references/view-layer.md` -- 뷰 레이어
- `implementation-django-web/references/design-system.md` -- 디자인 시스템
- `implementation-django-web/references/asset-management.md` -- 에셋 관리

---

## 2단계: 모드 판단

사용자 요청: "**만들어줘**" --> **Writing** 모드

---

## 3단계: 실행

Writing 모드에 따라 `implementation-django-web` 스킬의 Writing 모드 지침을 따른다.
기본 스킬의 규칙(Python 관례, Django 관례, 클린코드 원칙)을 동시 적용한다.

---

## 주요 내용

### 프로젝트 구조

```
web/
├── views/
│   └── orders/
│       ├── __init__.py
│       └── views.py                    # OrderListView, OrderDetailView
├── view_urls.py                        # URL 패턴
└── templates/
    └── orders/
        ├── orders_root.html            # 주문 목록 페이지 (Root 패턴)
        ├── order_detail_root.html      # 주문 상세 페이지 (Root 패턴)
        ├── order_list/
        │   └── order_list.html         # 주문 목록 컴포넌트
        ├── order_card/
        │   └── order_card.html         # 주문 카드 컴포넌트
        └── order_detail/
            ├── order_info.html         # 주문 기본 정보 컴포넌트
            └── order_items.html        # 주문 항목 목록 컴포넌트

orders/
├── models.py                           # Order, OrderItem 모델
└── services.py                         # 서비스 레이어

web/templates/design_system/
├── cards/
│   └── _stat_card.html                 # 통계 카드 컴포넌트
└── data-display/
    └── _status_badge.html              # 상태 배지 컴포넌트
```

---

### 1. 모델 (orders/models.py)

```python
from django.db import models
from django.urls import reverse


class Order(models.Model):
    """주문 정보를 담는 모델."""

    class Status(models.TextChoices):
        PENDING = "pending", "대기중"
        CONFIRMED = "confirmed", "확인됨"
        SHIPPED = "shipped", "배송중"
        DELIVERED = "delivered", "배송완료"
        CANCELLED = "cancelled", "취소됨"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_default=Status.PENDING,
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    def get_absolute_url(self) -> str:
        return reverse("web:order-detail", kwargs={"order_id": self.pk})

    @property
    def item_count(self) -> int:
        """주문에 포함된 상품 수."""
        return self.items.count()


class OrderItem(models.Model):
    """주문에 포함된 개별 상품 항목."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return f"{self.product_name} x {self.quantity}"

    @property
    def subtotal(self) -> "Decimal":
        """항목별 소계."""
        return self.unit_price * self.quantity
```

---

### 2. 서비스 레이어 (orders/services.py)

```python
from django.db.models import Count, QuerySet, Sum

from orders.models import Order


class OrderService:
    """주문 조회를 위한 읽기 전용 서비스(셀렉터)."""

    @staticmethod
    def get_user_orders(*, user_id: int) -> QuerySet[Order]:
        """사용자의 주문 목록을 최신순으로 반환한다."""
        return (
            Order.objects
            .filter(user_id=user_id)
            .select_related("user")
            .annotate(item_count_annotation=Count("items"))
            .order_by("-created_at")
        )

    @staticmethod
    def get_order_detail(*, order_id: int, user_id: int) -> Order:
        """주문 상세 정보를 항목과 함께 반환한다."""
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("items")
            .get(pk=order_id, user_id=user_id)
        )

    @staticmethod
    def get_order_summary(*, user_id: int) -> dict:
        """주문 통계 요약을 반환한다."""
        return (
            Order.objects
            .filter(user_id=user_id)
            .aggregate(
                total_order_count=Count("id"),
                total_spent=Sum("total_amount"),
            )
        )
```

---

### 3. 뷰 (web/views/orders/views.py)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from orders.models import Order
from orders.services import OrderService


class OrderListView(LoginRequiredMixin, TemplateView):
    """주문 목록 페이지."""

    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)
        user_id = self.request.user.pk
        ctx["orders"] = OrderService.get_user_orders(user_id=user_id)
        ctx["summary"] = OrderService.get_order_summary(user_id=user_id)
        return ctx


class OrderDetailView(LoginRequiredMixin, TemplateView):
    """주문 상세 페이지."""

    template_name = "orders/order_detail_root.html"

    def get_context_data(self, **kwargs) -> dict:
        ctx = super().get_context_data(**kwargs)
        order_id = self.kwargs["order_id"]
        try:
            ctx["order"] = OrderService.get_order_detail(
                order_id=order_id,
                user_id=self.request.user.pk,
            )
        except Order.DoesNotExist:
            raise Http404("주문을 찾을 수 없습니다.")
        return ctx
```

---

### 4. URL 패턴 (web/view_urls.py)

```python
from django.urls import path

from web.views.orders.views import OrderDetailView, OrderListView

app_name = "web"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path(
        "orders/<int:order_id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
]
```

---

### 5. 템플릿

#### 5-1. 주문 목록 루트 (orders/orders_root.html)

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block title %}주문 내역{% endblock title %}
{% block meta_description %}내 주문 내역을 확인합니다.{% endblock meta_description %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/orders.css' %}">
{% endblock head_extra %}

{% block body %}
    {% include "orders/order_list/order_list.html" with orders=orders summary=summary only %}
{% endblock body %}
```

#### 5-2. 주문 목록 컴포넌트 (orders/order_list/order_list.html)

```htmldjango
{# 필수 변수: orders (QuerySet[Order]), summary (dict) #}
{% load static %}

<div class="order-list-page">
    <header class="order-list-page__header">
        <h1>주문 내역</h1>
        <div class="order-list-page__summary">
            {% include "design_system/cards/_stat_card.html" with title="총 주문" value=summary.total_order_count unit="건" only %}
            {% include "design_system/cards/_stat_card.html" with title="총 결제액" value=summary.total_spent unit="원" only %}
        </div>
    </header>

    {% if orders %}
        <ul class="order-list">
            {% for order in orders %}
                {% include "orders/order_card/order_card.html" with order=order only %}
            {% endfor %}
        </ul>
    {% else %}
        <div class="order-list-page__empty">
            <p>주문 내역이 없습니다.</p>
        </div>
    {% endif %}
</div>
```

#### 5-3. 주문 카드 컴포넌트 (orders/order_card/order_card.html)

```htmldjango
{# 필수 변수: order (Order 객체) #}
<li class="order-card">
    <a href="{{ order.get_absolute_url }}" class="order-card__link">
        <div class="order-card__header">
            <span class="order-card__number">{{ order.order_number }}</span>
            <time class="order-card__date" datetime="{{ order.created_at|date:'Y-m-d' }}">
                {{ order.created_at|date:"Y년 n월 j일" }}
            </time>
        </div>
        <div class="order-card__body">
            <span class="order-card__amount">{{ order.total_amount|floatformat:"0" }}원</span>
            {% include "design_system/data-display/_status_badge.html" with status=order.status label=order.get_status_display only %}
        </div>
    </a>
</li>
```

#### 5-4. 주문 상세 루트 (orders/order_detail_root.html)

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block title %}주문 {{ order.order_number }}{% endblock title %}
{% block meta_description %}주문 {{ order.order_number }}의 상세 정보를 확인합니다.{% endblock meta_description %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/order-detail.css' %}">
{% endblock head_extra %}

{% block body %}
    {% include "orders/order_detail/order_info.html" with order=order only %}
    {% include "orders/order_detail/order_items.html" with items=order.items.all only %}
{% endblock body %}
```

#### 5-5. 주문 기본 정보 (orders/order_detail/order_info.html)

```htmldjango
{# 필수 변수: order (Order 객체) #}
<section class="order-info">
    <div class="order-info__header">
        <h1>주문 상세</h1>
        <a href="{% url 'web:orders' %}" class="order-info__back-link">목록으로</a>
    </div>

    <dl class="order-info__details">
        <div class="order-info__row">
            <dt>주문번호</dt>
            <dd>{{ order.order_number }}</dd>
        </div>
        <div class="order-info__row">
            <dt>주문일시</dt>
            <dd>
                <time datetime="{{ order.created_at|date:'Y-m-d\TH:i:s' }}">
                    {{ order.created_at|date:"Y년 n월 j일 H:i" }}
                </time>
            </dd>
        </div>
        <div class="order-info__row">
            <dt>상태</dt>
            <dd>
                {% include "design_system/data-display/_status_badge.html" with status=order.status label=order.get_status_display only %}
            </dd>
        </div>
        <div class="order-info__row">
            <dt>배송지</dt>
            <dd>{{ order.shipping_address }}</dd>
        </div>
        <div class="order-info__row order-info__row--total">
            <dt>결제 금액</dt>
            <dd>{{ order.total_amount|floatformat:"0" }}원</dd>
        </div>
    </dl>
</section>
```

#### 5-6. 주문 항목 목록 (orders/order_detail/order_items.html)

```htmldjango
{# 필수 변수: items (QuerySet[OrderItem]) #}
<section class="order-items">
    <h2>주문 상품</h2>

    {% if items %}
        <table class="order-items__table">
            <thead>
                <tr>
                    <th>상품명</th>
                    <th>수량</th>
                    <th>단가</th>
                    <th>소계</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                    <tr class="order-items__row">
                        <td>{{ item.product_name }}</td>
                        <td>{{ item.quantity }}개</td>
                        <td>{{ item.unit_price|floatformat:"0" }}원</td>
                        <td>{{ item.subtotal|floatformat:"0" }}원</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p class="order-items__empty">주문 상품이 없습니다.</p>
    {% endif %}
</section>
```

---

### 6. 디자인 시스템 컴포넌트

#### 6-1. 통계 카드 (design_system/cards/_stat_card.html)

```htmldjango
{# 필수 변수: title (str), value (number|str), unit (str, 선택) #}
<div class="stat-card">
    <span class="stat-card__title">{{ title }}</span>
    <span class="stat-card__value">
        {{ value|default:"0" }}{% if unit %}<span class="stat-card__unit">{{ unit }}</span>{% endif %}
    </span>
</div>
```

#### 6-2. 상태 배지 (design_system/data-display/_status_badge.html)

```htmldjango
{# 필수 변수: status (str - CSS modifier), label (str - 표시 텍스트) #}
<span class="status-badge status-badge--{{ status }}">{{ label }}</span>
```

---

### 7. CSS (orders/static/orders/css/orders.css)

```css
/* 주문 목록 페이지 */
.order-list-page {
    max-width: 48rem;
    margin: 0 auto;
    padding: var(--spacing-lg, 1.5rem);
}

.order-list-page__header {
    margin-bottom: var(--spacing-xl, 2rem);
}

.order-list-page__header h1 {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin-bottom: var(--spacing-md, 1rem);
}

.order-list-page__summary {
    display: flex;
    gap: var(--spacing-md, 1rem);
}

.order-list {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
}

.order-list-page__empty {
    text-align: center;
    padding: var(--spacing-xl, 2rem);
    color: var(--color-text-muted, #6b7280);
}

/* 주문 카드 */
.order-card__link {
    display: block;
    padding: var(--spacing-md, 1rem);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    text-decoration: none;
    color: inherit;
    transition: box-shadow var(--transition-duration, 200ms) ease;
}

.order-card__link:hover {
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.order-card__link:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

.order-card__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-xs, 0.25rem);
}

.order-card__number {
    font-weight: 600;
    color: var(--color-text, #1f2937);
}

.order-card__date {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
}

.order-card__body {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.order-card__amount {
    font-weight: 600;
    color: var(--color-text, #1f2937);
}
```

### 8. CSS (orders/static/orders/css/order-detail.css)

```css
/* 주문 상세 정보 */
.order-info {
    max-width: 48rem;
    margin: 0 auto;
    padding: var(--spacing-lg, 1.5rem);
}

.order-info__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.order-info__header h1 {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
}

.order-info__back-link {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-primary, #3b82f6);
    text-decoration: none;
}

.order-info__back-link:hover {
    text-decoration: underline;
}

.order-info__back-link:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
    border-radius: var(--radius-sm, 0.25rem);
}

.order-info__details {
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    overflow: hidden;
}

.order-info__row {
    display: flex;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.order-info__row:last-child {
    border-bottom: none;
}

.order-info__row dt {
    flex: 0 0 8rem;
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
}

.order-info__row dd {
    flex: 1;
    color: var(--color-text, #1f2937);
}

.order-info__row--total {
    background-color: var(--color-bg-subtle, #f3f4f6);
    font-weight: 600;
}

/* 주문 항목 테이블 */
.order-items {
    max-width: 48rem;
    margin: 0 auto;
    padding: 0 var(--spacing-lg, 1.5rem) var(--spacing-lg, 1.5rem);
}

.order-items h2 {
    font-size: var(--text-base, 1rem);
    color: var(--color-text, #1f2937);
    margin-bottom: var(--spacing-md, 1rem);
}

.order-items__table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    overflow: hidden;
}

.order-items__table th {
    background-color: var(--color-bg-subtle, #f3f4f6);
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    text-align: left;
}

.order-items__table td {
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border-top: 1px solid var(--color-border, #e5e7eb);
    color: var(--color-text, #1f2937);
}

.order-items__empty {
    text-align: center;
    padding: var(--spacing-lg, 1.5rem);
    color: var(--color-text-muted, #6b7280);
}

/* 상태 배지 */
.status-badge {
    display: inline-block;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    font-size: var(--text-sm, 0.875rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-weight: 500;
}

.status-badge--pending {
    background-color: #fef3c7;
    color: #92400e;
}

.status-badge--confirmed {
    background-color: #dbeafe;
    color: #1e40af;
}

.status-badge--shipped {
    background-color: #e0e7ff;
    color: #3730a3;
}

.status-badge--delivered {
    background-color: #d1fae5;
    color: #065f46;
}

.status-badge--cancelled {
    background-color: #fee2e2;
    color: #991b1b;
}

/* 통계 카드 */
.stat-card {
    display: flex;
    flex-direction: column;
    padding: var(--spacing-md, 1rem);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    min-width: 8rem;
}

.stat-card__title {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
}

.stat-card__value {
    font-size: var(--text-lg, 1.125rem);
    font-weight: 600;
    color: var(--color-text, #1f2937);
}

.stat-card__unit {
    font-size: var(--text-sm, 0.875rem);
    font-weight: 400;
    margin-left: var(--spacing-xs, 0.25rem);
}
```

---

### 적용된 스킬 규칙 요약

| 스킬 | 적용 사항 |
|------|-----------|
| **cleancode** | 의도를 드러내는 네이밍 (`order_number`, `item_count`, `total_spent`), 함수는 하나의 일만 수행, 모듈은 단순 인터페이스 뒤에 설계 결정을 숨김 |
| **python** | 타입 힌트 (`-> str`, `-> dict`, `-> QuerySet[Order]`), `TextChoices` 열거형, `@property` 사용, `@staticmethod`로 서비스 메서드 정의 |
| **django** | Fat Model/Thin View, `TextChoices` 상태 관리, `select_related`/`prefetch_related`로 N+1 방지, 서비스 레이어(`<entity>_<action>` 네이밍 대신 셀렉터 패턴), `db_default` (Django 5.x), `LoginRequiredMixin` |
| **django-web** | Root 템플릿 패턴 (`{% extends %}` + `{% include %}` 합성), `{% include ... only %}` 컨텍스트 격리, `{% static %}` 태그 사용, `{{ block.super }}`로 head_extra 확장, `{% endblock name %}` 닫는 태그에 블록명, CSS Custom Properties로 디자인 토큰 사용 (`var()` + 폴백), 디자인 시스템 컴포넌트 분리 (`_stat_card.html`, `_status_badge.html`), 접근성 토큰 (포커스 링, 트랜지션), 컴포넌트 필수 변수 문서화 (`{# 필수 변수: ... #}`) |

---

> **관련 스킬 참조:**
> - 주문 모델에 복잡한 비즈니스 로직 추가 시 --> **implementation-django** 스킬 (서비스 레이어, 모델 설계)
> - 주문 API 엔드포인트 구현 시 --> **implementation-django-ninja** 스킬
> - 주문 목록에 필터링/검색/페이지네이션 추가 시 --> **implementation-django** 스킬 (QuerySet 패턴)
> - HTMX로 동적 상태 변경(주문 취소 등) 구현 시 --> **implementation-django-web** 스킬 (HTMX 패턴)
> - 주문 관련 테스트 작성 시 --> **implementation-django** 스킬 (테스팅)
