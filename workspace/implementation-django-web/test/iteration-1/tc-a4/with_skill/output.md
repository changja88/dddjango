# Dashboard Page Implementation (Root Pattern, Composition 기반)

## 폴더 구조

```
web/
├── views/
│   └── dashboard/
│       ├── __init__.py
│       └── views.py
├── templates/
│   └── dashboard/
│       ├── dashboard_root.html
│       ├── sales_summary/
│       │   ├── sales_summary.html
│       │   └── sales_summary-scripts.html
│       ├── recent_orders/
│       │   └── recent_orders.html
│       └── notification_feed/
│           └── notification_feed.html
├── static/
│   └── dashboard/
│       ├── css/
│       │   ├── sales-summary.css
│       │   ├── recent-orders.css
│       │   └── notification-feed.css
│       └── js/
│           └── sales-chart.js
└── view_urls.py
```

---

## 1. View

### `web/views/dashboard/__init__.py`

```python
from .views import DashboardView

__all__ = ["DashboardView"]
```

### `web/views/dashboard/views.py`

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from orders.services import OrderService
from dashboard.services import DashboardService
from notifications.services import NotificationService


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            ctx["sales_chart_data"] = DashboardService.get_sales_summary(user=user)
        except Exception:
            ctx["sales_chart_data"] = {"labels": [], "datasets": []}
            ctx["sales_error"] = "매출 데이터를 불러올 수 없습니다."

        try:
            ctx["recent_orders"] = OrderService.get_recent(user=user, limit=10)
        except Exception:
            ctx["recent_orders"] = []
            ctx["orders_error"] = "최근 주문을 불러올 수 없습니다."

        try:
            ctx["notifications"] = NotificationService.get_feed(user=user, limit=20)
        except Exception:
            ctx["notifications"] = []
            ctx["notifications_error"] = "알림을 불러올 수 없습니다."

        return ctx
```

---

## 2. URL 등록

### `web/view_urls.py` (추가)

```python
from web.views.dashboard import DashboardView

app_name = "web"

urlpatterns = [
    # ... 기존 패턴 ...
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
```

---

## 3. Root Template

### `web/templates/dashboard/dashboard_root.html`

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block title %}대시보드{% endblock title %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'dashboard/css/sales-summary.css' %}">
    <link rel="stylesheet" href="{% static 'dashboard/css/recent-orders.css' %}">
    <link rel="stylesheet" href="{% static 'dashboard/css/notification-feed.css' %}">
{% endblock head_extra %}

{% block body %}
    <main class="dashboard">
        <h1 class="dashboard__title">대시보드</h1>

        <div class="dashboard__grid">
            {% include "dashboard/sales_summary/sales_summary.html" with sales_chart_data=sales_chart_data sales_error=sales_error only %}

            {% include "dashboard/recent_orders/recent_orders.html" with recent_orders=recent_orders orders_error=orders_error only %}

            {% include "dashboard/notification_feed/notification_feed.html" with notifications=notifications notifications_error=notifications_error only %}
        </div>
    </main>

    {% include "dashboard/sales_summary/sales_summary-scripts.html" with sales_chart_data=sales_chart_data only %}
{% endblock body %}
```

---

## 4. Section Templates

### `web/templates/dashboard/sales_summary/sales_summary.html`

```htmldjango
{# 필수 변수: sales_chart_data (dict), sales_error (str|None) #}
<section class="sales-summary">
    <h2 class="sales-summary__heading">매출 요약</h2>

    {% if sales_error %}
        <p class="sales-summary__error">{{ sales_error }}</p>
    {% endif %}

    <div class="sales-summary__chart-wrapper">
        <canvas id="sales-chart" aria-label="월별 매출 요약 차트" role="img"></canvas>
    </div>
</section>
```

### `web/templates/dashboard/sales_summary/sales_summary-scripts.html`

```htmldjango
{# 필수 변수: sales_chart_data (dict) #}
{% load static %}

{# Chart.js — 차트 렌더링 라이브러리 #}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"
        integrity="sha384-E0FlMafrVIHbLC3bOBl49KMFOz7YVGF+hSbHOZhkrm/1FwUbBMmRQ+VNBJyB1xT"
        crossorigin="anonymous"></script>

{# 서버 → JS 데이터 전달: 매출 차트 데이터 #}
{{ sales_chart_data|json_script:"sales-chart-data" }}

{# 매출 차트 초기화 스크립트 #}
<script src="{% static 'dashboard/js/sales-chart.js' %}"></script>
```

### `web/templates/dashboard/recent_orders/recent_orders.html`

```htmldjango
{# 필수 변수: recent_orders (list[Order]), orders_error (str|None) #}
<section class="recent-orders">
    <h2 class="recent-orders__heading">최근 주문</h2>

    {% if orders_error %}
        <p class="recent-orders__error">{{ orders_error }}</p>
    {% endif %}

    {% if recent_orders %}
        <table class="recent-orders__table">
            <thead>
                <tr>
                    <th>주문번호</th>
                    <th>고객명</th>
                    <th>금액</th>
                    <th>상태</th>
                    <th>일시</th>
                </tr>
            </thead>
            <tbody>
                {% for order in recent_orders %}
                    <tr>
                        <td>{{ order.order_number }}</td>
                        <td>{{ order.customer_name }}</td>
                        <td>{{ order.amount|floatformat:0 }}원</td>
                        <td>
                            <span class="recent-orders__status recent-orders__status--{{ order.status }}">
                                {{ order.get_status_display }}
                            </span>
                        </td>
                        <td>{{ order.created_at|date:"Y-m-d H:i" }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        {% if not orders_error %}
            <p class="recent-orders__empty">최근 주문이 없습니다.</p>
        {% endif %}
    {% endif %}
</section>
```

### `web/templates/dashboard/notification_feed/notification_feed.html`

```htmldjango
{# 필수 변수: notifications (list[Notification]), notifications_error (str|None) #}
<section class="notification-feed">
    <h2 class="notification-feed__heading">알림</h2>

    {% if notifications_error %}
        <p class="notification-feed__error">{{ notifications_error }}</p>
    {% endif %}

    {% if notifications %}
        <ul class="notification-feed__list">
            {% for notification in notifications %}
                <li class="notification-feed__item notification-feed__item--{{ notification.level }}{% if not notification.is_read %} notification-feed__item--unread{% endif %}">
                    <span class="notification-feed__icon" aria-hidden="true"></span>
                    <div class="notification-feed__content">
                        <p class="notification-feed__message">{{ notification.message }}</p>
                        <time class="notification-feed__time" datetime="{{ notification.created_at|date:'c' }}">
                            {{ notification.created_at|timesince }} 전
                        </time>
                    </div>
                </li>
            {% endfor %}
        </ul>
    {% else %}
        {% if not notifications_error %}
            <p class="notification-feed__empty">새로운 알림이 없습니다.</p>
        {% endif %}
    {% endif %}
</section>
```

---

## 5. JavaScript

### `web/static/dashboard/js/sales-chart.js`

```javascript
document.addEventListener("DOMContentLoaded", function () {
    const chartDataEl = document.getElementById("sales-chart-data");
    if (!chartDataEl) {
        return;
    }

    const chartData = JSON.parse(chartDataEl.textContent);
    const canvas = document.getElementById("sales-chart");
    if (!canvas) {
        return;
    }

    const style = getComputedStyle(document.documentElement);
    const primaryColor = style.getPropertyValue("--color-primary").trim() || "#3b82f6";
    const textColor = style.getPropertyValue("--color-text").trim() || "#1f2937";
    const textMutedColor = style.getPropertyValue("--color-text-muted").trim() || "#6b7280";
    const borderColor = style.getPropertyValue("--color-border").trim() || "#e5e7eb";

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: chartData.datasets.map(function (dataset) {
                return Object.assign({}, dataset, {
                    backgroundColor: dataset.backgroundColor || primaryColor,
                    borderColor: dataset.borderColor || primaryColor,
                    borderWidth: dataset.borderWidth || 1,
                });
            }),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: textColor,
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: textMutedColor },
                    grid: { color: borderColor },
                },
                y: {
                    ticks: { color: textMutedColor },
                    grid: { color: borderColor },
                    beginAtZero: true,
                },
            },
        },
    });
});
```

---

## 6. CSS

### `web/static/dashboard/css/sales-summary.css`

```css
.sales-summary {
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
}

.sales-summary__heading {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin: 0 0 var(--spacing-md, 1rem);
}

.sales-summary__error {
    color: var(--color-danger, #ef4444);
    font-size: var(--text-sm, 0.875rem);
    margin-bottom: var(--spacing-sm, 0.5rem);
}

.sales-summary__chart-wrapper {
    position: relative;
    height: 300px;
}
```

### `web/static/dashboard/css/recent-orders.css`

```css
.recent-orders {
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
}

.recent-orders__heading {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin: 0 0 var(--spacing-md, 1rem);
}

.recent-orders__error {
    color: var(--color-danger, #ef4444);
    font-size: var(--text-sm, 0.875rem);
    margin-bottom: var(--spacing-sm, 0.5rem);
}

.recent-orders__table {
    width: 100%;
    border-collapse: collapse;
}

.recent-orders__table th,
.recent-orders__table td {
    text-align: left;
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    border-bottom: 1px solid var(--color-border, #e5e7eb);
    font-size: var(--text-sm, 0.875rem);
}

.recent-orders__table th {
    color: var(--color-text-muted, #6b7280);
    font-weight: 600;
}

.recent-orders__table td {
    color: var(--color-text, #1f2937);
}

.recent-orders__status {
    display: inline-block;
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    font-size: var(--text-sm, 0.875rem);
    font-weight: 500;
}

.recent-orders__status--pending {
    background: var(--color-warning-bg, #fef3c7);
    color: var(--color-warning-text, #92400e);
}

.recent-orders__status--completed {
    background: var(--color-success-bg, #d1fae5);
    color: var(--color-success-text, #065f46);
}

.recent-orders__status--cancelled {
    background: var(--color-danger-bg, #fee2e2);
    color: var(--color-danger-text, #991b1b);
}

.recent-orders__empty {
    color: var(--color-text-muted, #6b7280);
    font-size: var(--text-sm, 0.875rem);
    text-align: center;
    padding: var(--spacing-xl, 2rem);
}
```

### `web/static/dashboard/css/notification-feed.css`

```css
.notification-feed {
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--radius-md, 0.5rem);
    padding: var(--spacing-lg, 1.5rem);
}

.notification-feed__heading {
    font-size: var(--text-lg, 1.125rem);
    color: var(--color-text, #1f2937);
    margin: 0 0 var(--spacing-md, 1rem);
}

.notification-feed__error {
    color: var(--color-danger, #ef4444);
    font-size: var(--text-sm, 0.875rem);
    margin-bottom: var(--spacing-sm, 0.5rem);
}

.notification-feed__list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.notification-feed__item {
    display: flex;
    align-items: flex-start;
    gap: var(--spacing-sm, 0.5rem);
    padding: var(--spacing-sm, 0.5rem) 0;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.notification-feed__item:last-child {
    border-bottom: none;
}

.notification-feed__item--unread {
    background: var(--color-bg-subtle, #f3f4f6);
    border-radius: var(--radius-sm, 0.25rem);
    padding: var(--spacing-sm, 0.5rem);
}

.notification-feed__icon {
    flex-shrink: 0;
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 50%;
    margin-top: var(--spacing-sm, 0.5rem);
    background: var(--color-text-muted, #6b7280);
}

.notification-feed__item--info .notification-feed__icon {
    background: var(--color-primary, #3b82f6);
}

.notification-feed__item--warning .notification-feed__icon {
    background: var(--color-warning, #f59e0b);
}

.notification-feed__item--error .notification-feed__icon {
    background: var(--color-danger, #ef4444);
}

.notification-feed__item--success .notification-feed__icon {
    background: var(--color-success, #10b981);
}

.notification-feed__content {
    flex: 1;
    min-width: 0;
}

.notification-feed__message {
    color: var(--color-text, #1f2937);
    font-size: var(--text-sm, 0.875rem);
    margin: 0;
    line-height: 1.5;
}

.notification-feed__time {
    color: var(--color-text-muted, #6b7280);
    font-size: var(--text-sm, 0.875rem);
}

.notification-feed__empty {
    color: var(--color-text-muted, #6b7280);
    font-size: var(--text-sm, 0.875rem);
    text-align: center;
    padding: var(--spacing-xl, 2rem);
}
```

---

## 7. View에서 전달하는 Context 데이터 구조

### `sales_chart_data` (dict) -- `json_script`로 JS에 전달

```python
{
    "labels": ["1월", "2월", "3월", "4월", "5월", "6월"],
    "datasets": [
        {
            "label": "매출",
            "data": [1200000, 1900000, 3000000, 5000000, 2300000, 4100000],
        }
    ],
}
```

### `recent_orders` (list[Order])

뷰에서 `OrderService.get_recent()`가 반환하는 Order 객체 리스트. 템플릿에서 사용하는 속성: `order_number`, `customer_name`, `amount`, `status`, `get_status_display`, `created_at`.

### `notifications` (list[Notification])

뷰에서 `NotificationService.get_feed()`가 반환하는 Notification 객체 리스트. 템플릿에서 사용하는 속성: `level` (info/warning/error/success), `is_read`, `message`, `created_at`.

---

## 적용된 Convention 요약

| Convention | 적용 내용 |
|---|---|
| Root Pattern (Composition) | `dashboard_root.html`이 `{% extends %}` + `{% include %}`만으로 구성 |
| 섹션별 폴더 분리 | `sales_summary/`, `recent_orders/`, `notification_feed/` 각각 HTML + scripts 분리 |
| `{% include ... only %}` | 모든 include에 `only` 키워드 적용, 명시적 변수 전달 |
| 필수 변수 문서화 | 각 컴포넌트 상단에 `{# 필수 변수: ... #}` 주석 |
| `json_script` | `sales_chart_data`를 `json_script` 필터로 안전하게 JS에 전달 |
| SRI (CDN) | Chart.js CDN에 `integrity`, `crossorigin` 속성 포함 |
| `{% static %}` | 모든 정적 파일 참조에 `{% static %}` 태그 사용 |
| `{% load static %}` | 필요한 템플릿마다 별도로 `{% load static %}` 선언 |
| `{{ block.super }}` | `head_extra` 블록에서 부모 콘텐츠 유지 |
| `{% endblock name %}` | 모든 `endblock`에 블록명 명시 |
| 디자인 토큰 (`var()`) | CSS에서 모든 색상/간격/크기를 `var(--token, fallback)` 형태로 참조 |
| JS 분리 | 앱 로직을 `static/dashboard/js/sales-chart.js`로 분리, 인라인 스크립트 없음 |
| CSS 분리 | 섹션별 CSS를 별도 파일로 분리, 인라인 `<style>` 없음 |
| 앱 네임스페이싱 | `static/dashboard/css/`, `static/dashboard/js/` 구조 |
| `<script>` 주석 | CDN, `json_script`, 앱 스크립트 각각에 Django 주석으로 용도 설명 |
| `LoginRequiredMixin` | `DashboardView`에 인증 필수 적용 (MRO 순서 준수) |
| 에러 처리 | `get_context_data`에서 각 서비스 호출을 `try/except`로 감싸서 부분 실패 허용 |
| 스크립트 로드 순서 | CDN -> `json_script` -> 앱 스크립트 순서 준수 |
