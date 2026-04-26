# 주문(Order) 목록 페이지 구현

3-tier 상속 구조(`base.html` -> `base_orders.html` -> `order_list.html`)로 구성하며,
Chart.js를 활용한 주문 통계 시각화, 인증 기반 접근 제어, 서비스 레이어 연동을 포함한다.

---

## 파일 구조

```
web/
├── views/
│   └── orders/
│       ├── __init__.py
│       └── views.py
├── view_urls.py
└── templates/
    ├── base.html
    ├── base_orders.html
    └── orders/
        ├── order_list.html
        └── order_stats/
            └── order_stats-scripts.html

orders/
├── services.py
└── static/
    └── orders/
        ├── css/
        │   └── order_list.css
        └── js/
            └── order_stats_chart.js
```

---

## 1. 서비스 레이어

### `orders/services.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from orders.models import Order


@dataclass(frozen=True)
class OrderStats:
    total_count: int
    current_month_revenue: Decimal
    monthly_counts: list[dict]
    monthly_revenues: list[dict]


class OrderService:
    @staticmethod
    def get_list(*, user) -> list[Order]:
        return list(
            Order.objects.filter(user=user)
            .select_related("user")
            .order_by("-created_at")
        )

    @staticmethod
    def get_stats(*, user) -> OrderStats:
        today = date.today()
        qs = Order.objects.filter(user=user)

        total_count = qs.count()

        current_month_revenue = (
            qs.filter(
                created_at__year=today.year,
                created_at__month=today.month,
            ).aggregate(revenue=Sum("amount"))["revenue"]
            or Decimal("0")
        )

        monthly_counts = list(
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")[:12]
        )

        monthly_revenues = list(
            qs.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("amount"))
            .order_by("month")[:12]
        )

        return OrderStats(
            total_count=total_count,
            current_month_revenue=current_month_revenue,
            monthly_counts=monthly_counts,
            monthly_revenues=monthly_revenues,
        )
```

---

## 2. 뷰

### `web/views/orders/views.py`

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from orders.services import OrderService


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_list.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx["orders"] = OrderService.get_list(user=self.request.user)
            stats = OrderService.get_stats(user=self.request.user)
            ctx["stats"] = stats
            ctx["chart_data"] = {
                "labels": [
                    item["month"].strftime("%Y-%m")
                    for item in stats.monthly_counts
                ],
                "counts": [
                    item["count"]
                    for item in stats.monthly_counts
                ],
                "revenues": [
                    float(item["revenue"] or 0)
                    for item in stats.monthly_revenues
                ],
            }
        except Exception:
            ctx["orders"] = []
            ctx["stats"] = None
            ctx["chart_data"] = {"labels": [], "counts": [], "revenues": []}
            ctx["error_message"] = "주문 데이터를 불러올 수 없습니다."
        return ctx
```

### `web/views/orders/__init__.py`

```python
from web.views.orders.views import OrderListView

__all__ = ["OrderListView"]
```

---

## 3. URL 설정

### `web/view_urls.py`

```python
from django.urls import path

from web.views.orders import OrderListView

app_name = "web"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
]
```

---

## 4. 템플릿 (3-tier 상속)

### Tier 1: `web/templates/base.html`

```htmldjango
{# base.html #}
{% load static %}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}서비스명{% endblock title %}</title>
    <meta name="description" content="{% block meta_description %}서비스 기본 설명{% endblock meta_description %}">
    {% block meta_extra %}{% endblock meta_extra %}
    <link rel="stylesheet" href="{% static 'css/tokens.css' %}">
    {% block head_extra %}{% endblock head_extra %}
</head>
<body>
    {% block navbar %}{% include "design_system/navigation/_navbar.html" %}{% endblock navbar %}
    {% block body %}{% endblock body %}
    {% block footer %}{% include "design_system/layout/_footer.html" %}{% endblock footer %}
    {% block scripts %}{% endblock scripts %}
</body>
</html>
```

### Tier 2: `web/templates/base_orders.html`

```htmldjango
{# base_orders.html #}
{% extends "base.html" %}
{% load static %}

{% block title %}주문 관리 - {{ block.super }}{% endblock title %}

{% block meta_description %}주문 목록 및 통계를 관리합니다.{% endblock meta_description %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'orders/css/order_list.css' %}">
{% endblock head_extra %}

{% block body %}
<div class="orders-layout">
    <nav class="orders-nav" aria-label="주문 섹션 탐색">
        <ul class="orders-nav__list">
            <li><a href="{% url 'web:orders' %}" class="orders-nav__link">주문 목록</a></li>
        </ul>
    </nav>
    <main class="orders-main">
        {% block content %}{% endblock content %}
    </main>
</div>
{% endblock body %}
```

### Tier 3: `web/templates/orders/order_list.html`

```htmldjango
{# orders/order_list.html #}
{% extends "base_orders.html" %}
{% load static %}

{% block title %}주문 목록 - {{ block.super }}{% endblock title %}

{% block content %}
<section class="order-stats" aria-labelledby="stats-heading">
    <h2 id="stats-heading" class="order-stats__heading">주문 통계</h2>

    {% if error_message %}
        <p class="order-stats__error" role="alert">{{ error_message }}</p>
    {% endif %}

    <div class="order-stats__cards">
        {% if stats %}
            {% include "design_system/cards/_stat_card.html" with title="총 주문 수" value=stats.total_count unit="건" only %}
            {% include "design_system/cards/_stat_card.html" with title="이번 달 매출" value=stats.current_month_revenue unit="원" only %}
        {% endif %}
    </div>

    <div class="order-stats__charts">
        <div class="order-stats__chart-wrap">
            <canvas id="order-count-chart" aria-label="월별 주문 수 차트" role="img"></canvas>
        </div>
        <div class="order-stats__chart-wrap">
            <canvas id="order-revenue-chart" aria-label="월별 매출 차트" role="img"></canvas>
        </div>
    </div>
</section>

<section class="order-list" aria-labelledby="list-heading">
    <h2 id="list-heading" class="order-list__heading">주문 목록</h2>

    {% if orders %}
    <table class="order-list__table">
        <thead>
            <tr>
                <th scope="col">주문 번호</th>
                <th scope="col">주문일</th>
                <th scope="col">상태</th>
                <th scope="col">금액</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.id }}</td>
                <td>{{ order.created_at|date:"Y-m-d" }}</td>
                <td>{{ order.get_status_display }}</td>
                <td>{{ order.amount|floatformat:"0" }}원</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="order-list__empty">주문 내역이 없습니다.</p>
    {% endif %}
</section>
{% endblock content %}

{% block scripts %}
    {{ block.super }}
    {% include "orders/order_stats/order_stats-scripts.html" %}
{% endblock scripts %}
```

---

## 5. 스크립트 로드 (scripts.html 패턴)

### `web/templates/orders/order_stats/order_stats-scripts.html`

```htmldjango
{# orders/order_stats/order_stats-scripts.html #}
{% load static %}

{# Chart.js -- 차트 렌더링 라이브러리 #}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"
        integrity="sha384-UPIssOjNMqMfumBMa1sHRzcMDnVJCL0KNIblXXGOClAqMjOYJOWFnY2NxtBn0dEH"
        crossorigin="anonymous"></script>

{# 서버 -> JS 데이터 전달: 주문 통계 차트 데이터 #}
{{ chart_data|json_script:"chart-data" }}

{# 주문 통계 차트 초기화 앱 스크립트 #}
<script src="{% static 'orders/js/order_stats_chart.js' %}"></script>
```

---

## 6. JavaScript

### `orders/static/orders/js/order_stats_chart.js`

```javascript
(function () {
    "use strict";

    var rawData = document.getElementById("chart-data");
    if (!rawData) return;

    var chartData = JSON.parse(rawData.textContent);

    var countCtx = document.getElementById("order-count-chart");
    if (countCtx) {
        new Chart(countCtx, {
            type: "bar",
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: "주문 수",
                    data: chartData.counts,
                    backgroundColor: getComputedStyle(document.documentElement)
                        .getPropertyValue("--color-primary").trim() || "#3b82f6",
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: "월별 주문 수"
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 }
                    }
                }
            }
        });
    }

    var revenueCtx = document.getElementById("order-revenue-chart");
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: "line",
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: "매출 (원)",
                    data: chartData.revenues,
                    borderColor: getComputedStyle(document.documentElement)
                        .getPropertyValue("--color-primary").trim() || "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: "월별 매출"
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
})();
```

---

## 7. CSS

### `orders/static/orders/css/order_list.css`

```css
.orders-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.orders-nav {
    border-bottom: 1px solid var(--color-border, #e5e7eb);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-lg, 1.5rem);
}

.orders-nav__list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    gap: var(--spacing-md, 1rem);
}

.orders-nav__link {
    color: var(--color-primary, #3b82f6);
    text-decoration: none;
    font-size: var(--text-sm, 0.875rem);
}

.orders-nav__link:focus-visible {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
    border-radius: var(--radius-sm, 0.25rem);
}

.orders-main {
    flex: 1;
    padding: var(--spacing-lg, 1.5rem);
    max-width: 72rem;
    margin: 0 auto;
    width: 100%;
}

/* -- 통계 섹션 -- */

.order-stats {
    margin-bottom: var(--spacing-xl, 2rem);
}

.order-stats__heading {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin-bottom: var(--spacing-md, 1rem);
}

.order-stats__error {
    color: var(--color-danger, #dc2626);
    background-color: var(--color-danger-bg, #fef2f2);
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border-radius: var(--radius-md, 0.5rem);
    margin-bottom: var(--spacing-md, 1rem);
}

.order-stats__cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
    gap: var(--spacing-md, 1rem);
    margin-bottom: var(--spacing-lg, 1.5rem);
}

.order-stats__charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr));
    gap: var(--spacing-lg, 1.5rem);
}

.order-stats__chart-wrap {
    background-color: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    padding: var(--spacing-md, 1rem);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

/* -- 목록 섹션 -- */

.order-list {
    margin-top: var(--spacing-xl, 2rem);
}

.order-list__heading {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin-bottom: var(--spacing-md, 1rem);
}

.order-list__table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-sm, 0.875rem);
}

.order-list__table thead {
    background-color: var(--color-bg-subtle, #f3f4f6);
}

.order-list__table th,
.order-list__table td {
    text-align: left;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border-bottom: 1px solid var(--color-border, #e5e7eb);
    color: var(--color-text, #1f2937);
}

.order-list__table th {
    font-weight: 600;
    color: var(--color-text-muted, #6b7280);
}

.order-list__table tbody tr:hover {
    background-color: var(--color-bg-subtle, #f3f4f6);
}

.order-list__empty {
    color: var(--color-text-muted, #6b7280);
    text-align: center;
    padding: var(--spacing-xl, 2rem);
}

/* -- 반응형 -- */

@media (max-width: 768px) {
    .orders-main {
        padding: var(--spacing-md, 1rem);
    }

    .order-stats__charts {
        grid-template-columns: 1fr;
    }

    .order-list__table {
        font-size: var(--text-sm, 0.875rem);
    }
}
```

---

## 8. 디자인 시스템 컴포넌트 (참조)

### `web/templates/design_system/cards/_stat_card.html`

```htmldjango
{# design_system/cards/_stat_card.html #}
{# 필수 변수: title (str), value (number|str), unit (str) #}
<div class="stat-card">
    <p class="stat-card__title">{{ title }}</p>
    <p class="stat-card__value">{{ value }}<span class="stat-card__unit">{{ unit }}</span></p>
</div>
```

### `design_system/cards/stat-card.css`

```css
.stat-card {
    background-color: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    padding: var(--spacing-md, 1rem) var(--spacing-lg, 1.5rem);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.stat-card__title {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
    margin: 0 0 var(--spacing-xs, 0.25rem);
}

.stat-card__value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text, #1f2937);
    margin: 0;
}

.stat-card__unit {
    font-size: var(--text-sm, 0.875rem);
    font-weight: 400;
    color: var(--color-text-muted, #6b7280);
    margin-left: var(--spacing-xs, 0.25rem);
}
```

---

## 적용된 규칙 요약

| 규칙 | 적용 위치 |
|------|-----------|
| 3-tier 상속 (`base.html` -> `base_orders.html` -> `order_list.html`) | 템플릿 전체 |
| `{% extends %}`는 템플릿 첫 번째 태그 | 모든 자식 템플릿 |
| `{% endblock name %}` 닫는 태그에 블록명 명시 | 모든 템플릿 |
| `{{ block.super }}`로 부모 블록 확장 | `base_orders.html`의 `head_extra`, `order_list.html`의 `title`/`scripts` |
| `{% load static %}`을 자식 템플릿마다 별도 로드 | `base_orders.html`, `order_list.html`, `order_stats-scripts.html` |
| `{% static %}` 태그로 정적 파일 참조 (하드코딩 금지) | CSS/JS 로드 전체 |
| `{% include ... only %}` 컨텍스트 격리 | `_stat_card.html` include |
| `json_script` 필터로 서버 -> JS 데이터 전달 (XSS 방지) | `order_stats-scripts.html` |
| CDN 스크립트에 SRI (`integrity`, `crossorigin`) 포함 | Chart.js 로드 |
| 인라인 `<script>` 금지 -- 별도 JS 파일로 분리 | `order_stats_chart.js` |
| 인라인 `<style>` 금지 -- 별도 CSS 파일로 분리 | `order_list.css`, `stat-card.css` |
| CSS Custom Properties(디자인 토큰) + `var()` 폴백 값 | CSS 전체 |
| `LoginRequiredMixin`을 `TemplateView` 앞에 배치 (MRO) | `OrderListView` |
| 서비스 레이어 호출 시 에러 처리 (`try/except`) | `OrderListView.get_context_data` |
| 앱별 정적 파일 네임스페이싱 (`orders/static/orders/`) | 정적 파일 구조 |
| scripts.html 패턴으로 CDN + json_script + 앱 스크립트 분리 | `order_stats-scripts.html` |
| 컴포넌트 필수 변수 문서화 (`{# 필수 변수: ... #}`) | `_stat_card.html` |
| `<script>` / `<style>` 태그에 Django 주석으로 용도 설명 | `order_stats-scripts.html` |
