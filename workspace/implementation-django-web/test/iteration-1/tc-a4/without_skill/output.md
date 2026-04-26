# Django Dashboard Implementation (Composition-based Root Pattern)

## Task

대시보드 페이지를 Root 패턴(composition 기반)으로 구성한다.
3개 섹션: (1) 매출 요약 차트(Chart.js), (2) 최근 주문 목록, (3) 알림 피드.
각 섹션은 별도 폴더에 HTML과 스크립트를 보유하며, 서버 데이터를 JS로 전달한다.

---

## 1. Project Structure

```
dashboard/
    __init__.py
    urls.py
    views.py
    templatetags/
        __init__.py
        dashboard_tags.py
    sections/
        sales_chart/
            sales_chart.html
            sales_chart.js
        recent_orders/
            recent_orders.html
            recent_orders.js
        notification_feed/
            notification_feed.html
            notification_feed.js
    templates/
        dashboard/
            root.html
```

Root 패턴의 핵심: `root.html`은 레이아웃 껍데기이며, 각 섹션 폴더가 자신의 HTML/JS를 독립적으로 소유한다. Root는 이들을 `{% include %}` 로 합성(compose)한다.

---

## 2. Django App Setup

### `dashboard/__init__.py`

```python
```

(빈 파일)

### `dashboard/apps.py`

```python
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"
```

### Settings (프로젝트 settings.py에 추가)

```python
INSTALLED_APPS = [
    # ...
    "dashboard",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "dashboard_tags": "dashboard.templatetags.dashboard_tags",
            },
        },
    },
]
```

별도 폴더의 HTML을 `{% include %}` 로 불러오려면 Django 템플릿 로더가 `sections/` 경로도 탐색해야 한다. `APP_DIRS = True` 상태에서 `templates/` 안에 있으면 자동 탐색되지만, `sections/`는 `templates/` 밖이므로 커스텀 로더 설정이 필요하다.

```python
import os

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "dashboard", "sections"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

> **Note**: `DIRS`에 `sections/` 경로를 추가하면 `{% include "sales_chart/sales_chart.html" %}` 형태로 참조 가능하다.

---

## 3. URLs

### `dashboard/urls.py`

```python
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_root, name="root"),
]
```

### Project `urls.py`

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path("dashboard/", include("dashboard.urls")),
]
```

---

## 4. Views (Composition Root)

### `dashboard/views.py`

```python
import json
from datetime import datetime, timedelta

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def dashboard_root(request: HttpRequest) -> HttpResponse:
    """
    Dashboard composition root.
    각 섹션에 필요한 데이터를 수집하고 root 템플릿에 합성한다.
    """
    sales_data = _get_sales_data()
    recent_orders = _get_recent_orders()
    notifications = _get_notifications()

    context = {
        "sales_data": sales_data,
        "sales_data_json": json.dumps(sales_data),
        "recent_orders": recent_orders,
        "notifications": notifications,
    }
    return render(request, "dashboard/root.html", context)


def _get_sales_data() -> dict:
    """
    매출 요약 데이터를 수집한다.
    실제로는 DB 쿼리를 사용하지만, 여기서는 예시 데이터를 반환한다.
    """
    today = datetime.now()
    labels = []
    revenue = []
    order_counts = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime("%m/%d"))
        # 실제로는 Order.objects.filter(created_at__date=day.date()).aggregate(...)
        revenue.append(150000 + (i * 23000) + ((7 - i) * 15000))
        order_counts.append(12 + i * 3)

    return {
        "labels": labels,
        "revenue": revenue,
        "order_counts": order_counts,
        "total_revenue": sum(revenue),
        "total_orders": sum(order_counts),
        "avg_order_value": round(sum(revenue) / max(sum(order_counts), 1)),
    }


def _get_recent_orders() -> list[dict]:
    """
    최근 주문 목록을 반환한다.
    실제로는 Order.objects.select_related('customer').order_by('-created_at')[:10]
    """
    return [
        {
            "id": "ORD-2026-0401",
            "customer": "Kim Minjun",
            "items": "Premium Widget x2",
            "total": 89000,
            "status": "delivered",
            "created_at": "2026-04-05 14:23",
        },
        {
            "id": "ORD-2026-0400",
            "customer": "Lee Soojin",
            "items": "Standard Pack x1, Addon x3",
            "total": 142000,
            "status": "shipped",
            "created_at": "2026-04-05 11:07",
        },
        {
            "id": "ORD-2026-0399",
            "customer": "Park Jiyeon",
            "items": "Deluxe Bundle x1",
            "total": 315000,
            "status": "processing",
            "created_at": "2026-04-04 22:45",
        },
        {
            "id": "ORD-2026-0398",
            "customer": "Choi Dongwook",
            "items": "Basic Widget x5",
            "total": 175000,
            "status": "pending",
            "created_at": "2026-04-04 18:30",
        },
        {
            "id": "ORD-2026-0397",
            "customer": "Jung Haeun",
            "items": "Premium Widget x1, Standard Pack x2",
            "total": 267000,
            "status": "delivered",
            "created_at": "2026-04-04 09:15",
        },
    ]


def _get_notifications() -> list[dict]:
    """
    알림 피드 데이터를 반환한다.
    실제로는 Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    """
    return [
        {
            "id": 1,
            "type": "order",
            "message": "새 주문이 접수되었습니다 (ORD-2026-0401)",
            "is_read": False,
            "created_at": "5분 전",
        },
        {
            "id": 2,
            "type": "stock",
            "message": "Premium Widget 재고가 10개 이하입니다",
            "is_read": False,
            "created_at": "23분 전",
        },
        {
            "id": 3,
            "type": "payment",
            "message": "결제 확인: ORD-2026-0400 (142,000원)",
            "is_read": True,
            "created_at": "1시간 전",
        },
        {
            "id": 4,
            "type": "shipping",
            "message": "배송 완료: ORD-2026-0395",
            "is_read": True,
            "created_at": "3시간 전",
        },
        {
            "id": 5,
            "type": "system",
            "message": "시스템 점검 예정: 2026-04-06 02:00-04:00",
            "is_read": True,
            "created_at": "5시간 전",
        },
    ]
```

---

## 5. Template Tags

### `dashboard/templatetags/__init__.py`

```python
```

(빈 파일)

### `dashboard/templatetags/dashboard_tags.py`

```python
from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter
def currency(value: int | float) -> str:
    """숫자를 한국 원화 형식으로 표시한다."""
    try:
        return f"{number_format(value, 0)}원"
    except (ValueError, TypeError):
        return str(value)


@register.filter
def status_badge_class(status: str) -> str:
    """주문 상태에 맞는 CSS 클래스를 반환한다."""
    mapping = {
        "pending": "badge-warning",
        "processing": "badge-info",
        "shipped": "badge-primary",
        "delivered": "badge-success",
        "cancelled": "badge-danger",
    }
    return mapping.get(status, "badge-secondary")


@register.filter
def status_display(status: str) -> str:
    """주문 상태를 한국어로 표시한다."""
    mapping = {
        "pending": "대기",
        "processing": "처리중",
        "shipped": "배송중",
        "delivered": "배송완료",
        "cancelled": "취소됨",
    }
    return mapping.get(status, status)


@register.filter
def notification_icon(ntype: str) -> str:
    """알림 유형에 맞는 아이콘 클래스를 반환한다."""
    mapping = {
        "order": "bi-cart-check",
        "stock": "bi-box-seam",
        "payment": "bi-credit-card",
        "shipping": "bi-truck",
        "system": "bi-gear",
    }
    return mapping.get(ntype, "bi-bell")
```

---

## 6. Templates

### `dashboard/templates/dashboard/root.html` (Composition Root)

```html
{% load dashboard_tags %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>

    <!-- Bootstrap 5 CSS -->
    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
    >
    <!-- Bootstrap Icons -->
    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
        rel="stylesheet"
    >

    <style>
        body {
            background-color: #f4f6f9;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 100%);
            color: #fff;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
        }
        .section-card {
            background: #fff;
            border-radius: 0.75rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .section-card h2 {
            font-size: 1.15rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #e9ecef;
        }
        .summary-stat {
            text-align: center;
            padding: 1rem;
        }
        .summary-stat .value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #1e3a5f;
        }
        .summary-stat .label {
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 0.25rem;
        }
    </style>
</head>
<body>
    <header class="dashboard-header">
        <div class="container">
            <h1 class="mb-0"><i class="bi bi-speedometer2"></i> Dashboard</h1>
        </div>
    </header>

    <main class="container">
        <!-- Section 1: Sales Chart -->
        <div class="row">
            <div class="col-12">
                <div class="section-card">
                    {% include "sales_chart/sales_chart.html" %}
                </div>
            </div>
        </div>

        <!-- Section 2 & 3: Recent Orders + Notification Feed -->
        <div class="row">
            <div class="col-lg-7">
                <div class="section-card">
                    {% include "recent_orders/recent_orders.html" %}
                </div>
            </div>
            <div class="col-lg-5">
                <div class="section-card">
                    {% include "notification_feed/notification_feed.html" %}
                </div>
            </div>
        </div>
    </main>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>

    <!--
        Server -> JS data bridge.
        json_script 필터는 Django 내장이며 XSS-safe JSON을 <script> 태그로 출력한다.
    -->
    {{ sales_data_json|json_script:"sales-data" }}

    <!-- Section scripts (각 섹션 폴더의 JS를 순서대로 로드) -->
    {% include "sales_chart/sales_chart.js" %}
    {% include "recent_orders/recent_orders.js" %}
    {% include "notification_feed/notification_feed.js" %}
</body>
</html>
```

---

## 7. Section Files

### Section 1: Sales Chart

#### `dashboard/sections/sales_chart/sales_chart.html`

```html
{% load dashboard_tags %}

<h2><i class="bi bi-bar-chart-line"></i> 매출 요약</h2>

<!-- Summary Stats Row -->
<div class="row mb-3">
    <div class="col-md-4">
        <div class="summary-stat">
            <div class="value">{{ sales_data.total_revenue|currency }}</div>
            <div class="label">7일 총 매출</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="summary-stat">
            <div class="value">{{ sales_data.total_orders }}건</div>
            <div class="label">7일 총 주문</div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="summary-stat">
            <div class="value">{{ sales_data.avg_order_value|currency }}</div>
            <div class="label">평균 주문 금액</div>
        </div>
    </div>
</div>

<!-- Chart Canvas -->
<div style="position: relative; height: 300px;">
    <canvas id="salesChart"></canvas>
</div>
```

#### `dashboard/sections/sales_chart/sales_chart.js`

```html
<script>
(function () {
    "use strict";

    // Django json_script로 전달된 서버 데이터 파싱
    const rawData = JSON.parse(
        document.getElementById("sales-data").textContent
    );

    const ctx = document.getElementById("salesChart").getContext("2d");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: rawData.labels,
            datasets: [
                {
                    label: "매출 (원)",
                    data: rawData.revenue,
                    backgroundColor: "rgba(30, 58, 95, 0.7)",
                    borderColor: "rgba(30, 58, 95, 1)",
                    borderWidth: 1,
                    borderRadius: 4,
                    yAxisID: "y",
                },
                {
                    label: "주문 수",
                    data: rawData.order_counts,
                    type: "line",
                    borderColor: "rgba(220, 53, 69, 0.9)",
                    backgroundColor: "rgba(220, 53, 69, 0.1)",
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: "rgba(220, 53, 69, 1)",
                    fill: true,
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            if (context.dataset.yAxisID === "y") {
                                return (
                                    context.dataset.label +
                                    ": " +
                                    context.parsed.y.toLocaleString("ko-KR") +
                                    "원"
                                );
                            }
                            return (
                                context.dataset.label +
                                ": " +
                                context.parsed.y +
                                "건"
                            );
                        },
                    },
                },
            },
            scales: {
                y: {
                    type: "linear",
                    position: "left",
                    title: {
                        display: true,
                        text: "매출 (원)",
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString("ko-KR");
                        },
                    },
                },
                y1: {
                    type: "linear",
                    position: "right",
                    title: {
                        display: true,
                        text: "주문 수",
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
            },
        },
    });
})();
</script>
```

---

### Section 2: Recent Orders

#### `dashboard/sections/recent_orders/recent_orders.html`

```html
{% load dashboard_tags %}

<h2><i class="bi bi-receipt"></i> 최근 주문</h2>

<div class="table-responsive">
    <table class="table table-hover align-middle mb-0" id="recentOrdersTable">
        <thead class="table-light">
            <tr>
                <th>주문번호</th>
                <th>고객</th>
                <th>상품</th>
                <th class="text-end">금액</th>
                <th class="text-center">상태</th>
                <th>일시</th>
            </tr>
        </thead>
        <tbody>
            {% for order in recent_orders %}
            <tr data-order-id="{{ order.id }}">
                <td>
                    <a href="#" class="text-decoration-none fw-semibold">
                        {{ order.id }}
                    </a>
                </td>
                <td>{{ order.customer }}</td>
                <td class="text-muted" style="max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    {{ order.items }}
                </td>
                <td class="text-end fw-semibold">
                    {{ order.total|currency }}
                </td>
                <td class="text-center">
                    <span class="badge {{ order.status|status_badge_class }}">
                        {{ order.status|status_display }}
                    </span>
                </td>
                <td class="text-muted" style="font-size: 0.85rem;">
                    {{ order.created_at }}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="6" class="text-center text-muted py-4">
                    최근 주문이 없습니다.
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="text-end mt-3">
    <a href="#" class="btn btn-sm btn-outline-primary">
        전체 주문 보기 <i class="bi bi-arrow-right"></i>
    </a>
</div>
```

#### `dashboard/sections/recent_orders/recent_orders.js`

```html
<script>
(function () {
    "use strict";

    const table = document.getElementById("recentOrdersTable");
    if (!table) return;

    // 주문 행 클릭 시 상세 페이지 이동 (placeholder)
    table.querySelector("tbody").addEventListener("click", function (e) {
        const row = e.target.closest("tr[data-order-id]");
        if (!row) return;

        const orderId = row.dataset.orderId;
        console.log("Navigate to order detail:", orderId);
        // window.location.href = `/orders/${orderId}/`;
    });

    // Badge 색상 적용 (Bootstrap 클래스 매핑)
    const badgeColorMap = {
        "badge-warning": "bg-warning text-dark",
        "badge-info": "bg-info text-white",
        "badge-primary": "bg-primary",
        "badge-success": "bg-success",
        "badge-danger": "bg-danger",
    };

    table.querySelectorAll(".badge").forEach(function (badge) {
        for (const [key, value] of Object.entries(badgeColorMap)) {
            if (badge.classList.contains(key)) {
                badge.classList.remove(key);
                value.split(" ").forEach(function (cls) {
                    badge.classList.add(cls);
                });
                break;
            }
        }
    });
})();
</script>
```

---

### Section 3: Notification Feed

#### `dashboard/sections/notification_feed/notification_feed.html`

```html
{% load dashboard_tags %}

<h2><i class="bi bi-bell"></i> 알림 피드</h2>

<ul class="list-group list-group-flush" id="notificationFeed">
    {% for notif in notifications %}
    <li class="list-group-item d-flex align-items-start px-0 {% if not notif.is_read %}bg-light{% endif %}"
        data-notification-id="{{ notif.id }}"
        data-is-read="{{ notif.is_read|yesno:'true,false' }}">
        <div class="me-3 mt-1">
            <i class="bi {{ notif.type|notification_icon }} fs-5
                {% if not notif.is_read %}text-primary{% else %}text-muted{% endif %}">
            </i>
        </div>
        <div class="flex-grow-1">
            <div class="{% if not notif.is_read %}fw-semibold{% endif %}">
                {{ notif.message }}
            </div>
            <small class="text-muted">{{ notif.created_at }}</small>
        </div>
        {% if not notif.is_read %}
        <button class="btn btn-sm btn-link text-muted mark-read-btn" title="읽음 처리">
            <i class="bi bi-check2"></i>
        </button>
        {% endif %}
    </li>
    {% empty %}
    <li class="list-group-item text-center text-muted py-4 px-0">
        새로운 알림이 없습니다.
    </li>
    {% endfor %}
</ul>

<div class="text-end mt-3">
    <a href="#" class="btn btn-sm btn-outline-secondary" id="markAllReadBtn">
        모두 읽음 처리
    </a>
</div>
```

#### `dashboard/sections/notification_feed/notification_feed.js`

```html
<script>
(function () {
    "use strict";

    const feed = document.getElementById("notificationFeed");
    const markAllBtn = document.getElementById("markAllReadBtn");

    if (!feed) return;

    /**
     * 단일 알림을 읽음 처리한다.
     * 실제로는 fetch()로 서버에 PATCH 요청을 보낸다.
     */
    function markAsRead(listItem) {
        const notifId = listItem.dataset.notificationId;

        // 서버 호출 (placeholder)
        // fetch(`/api/notifications/${notifId}/read/`, {
        //     method: 'PATCH',
        //     headers: {
        //         'X-CSRFToken': getCookie('csrftoken'),
        //         'Content-Type': 'application/json',
        //     },
        // });

        listItem.dataset.isRead = "true";
        listItem.classList.remove("bg-light");

        const icon = listItem.querySelector(".bi");
        if (icon) {
            icon.classList.remove("text-primary");
            icon.classList.add("text-muted");
        }

        const textDiv = listItem.querySelector(".flex-grow-1 > div");
        if (textDiv) {
            textDiv.classList.remove("fw-semibold");
        }

        const btn = listItem.querySelector(".mark-read-btn");
        if (btn) {
            btn.remove();
        }

        console.log("Marked notification as read:", notifId);
    }

    // 개별 읽음 버튼 클릭
    feed.addEventListener("click", function (e) {
        const btn = e.target.closest(".mark-read-btn");
        if (!btn) return;

        e.preventDefault();
        const listItem = btn.closest("li[data-notification-id]");
        if (listItem) {
            markAsRead(listItem);
        }
    });

    // 모두 읽음 처리
    if (markAllBtn) {
        markAllBtn.addEventListener("click", function (e) {
            e.preventDefault();
            feed.querySelectorAll('li[data-is-read="false"]').forEach(markAsRead);
        });
    }
})();
</script>
```

---

## 8. Server Data to JS Transfer Strategy

Django에서 서버 데이터를 JavaScript로 전달하는 방식은 `json_script` 필터를 사용한다.

### 방식: `json_script` Template Filter (권장)

```html
<!-- root.html 안에서 -->
{{ sales_data_json|json_script:"sales-data" }}
```

이것은 다음과 같은 HTML을 생성한다:

```html
<script id="sales-data" type="application/json">
{"labels": ["03/30", "03/31", ...], "revenue": [150000, ...], "order_counts": [12, ...]}
</script>
```

JavaScript에서 읽는 방법:

```javascript
const data = JSON.parse(
    document.getElementById("sales-data").textContent
);
```

이 방식의 장점:
- XSS 공격에 안전하다. Django가 `<`, `>`, `&` 등을 자동 이스케이프한다.
- `type="application/json"`이므로 브라우저가 스크립트로 실행하지 않는다.
- 별도의 API 엔드포인트 없이 초기 페이지 로드에 데이터를 포함할 수 있다.
- Django 공식 문서에서 권장하는 패턴이다.

### View에서의 데이터 직렬화

```python
import json

def dashboard_root(request):
    sales_data = _get_sales_data()  # dict 반환
    context = {
        "sales_data": sales_data,                  # 템플릿에서 직접 접근용
        "sales_data_json": json.dumps(sales_data),  # json_script용
    }
    return render(request, "dashboard/root.html", context)
```

`json.dumps()`를 View에서 미리 호출하는 이유: `json_script` 필터는 입력 문자열을 그대로 JSON-safe하게 이스케이프하므로, dict를 JSON 문자열로 먼저 변환해야 한다.

---

## 9. Composition Pattern Explanation

### Root Pattern 구조

```
root.html (Composition Root)
    |
    +-- {% include "sales_chart/sales_chart.html" %}      --> Section 1
    +-- {% include "recent_orders/recent_orders.html" %}   --> Section 2
    +-- {% include "notification_feed/notification_feed.html" %} --> Section 3
    |
    +-- {{ sales_data_json|json_script:"sales-data" }}     --> Data Bridge
    |
    +-- {% include "sales_chart/sales_chart.js" %}         --> Section 1 Script
    +-- {% include "recent_orders/recent_orders.js" %}     --> Section 2 Script
    +-- {% include "notification_feed/notification_feed.js" %} --> Section 3 Script
```

핵심 원칙:
1. **Root는 레이아웃만 담당** -- 비즈니스 로직이 없다.
2. **각 섹션은 독립적** -- 자기 폴더 안에 HTML과 JS를 소유한다.
3. **데이터 흐름은 단방향** -- View가 모든 데이터를 수집하고, root가 각 섹션에 context를 전달한다.
4. **JS 파일은 IIFE로 격리** -- 각 섹션의 JS가 전역 스코프를 오염시키지 않는다.
5. **HTML이 먼저, Script가 나중에** -- DOM이 준비된 후 스크립트가 실행되도록 `<body>` 끝에 배치한다.

### 섹션 추가 절차

새 섹션을 추가하려면:

1. `sections/` 아래에 새 폴더를 만든다 (e.g., `sections/inventory_status/`).
2. 폴더 안에 `.html`과 `.js` 파일을 생성한다.
3. `views.py`의 `dashboard_root`에서 필요한 데이터를 context에 추가한다.
4. `root.html`에서 `{% include %}` 두 줄을 추가한다 (HTML 위치 + JS 위치).

---

## 10. Complete File Listing

| File | Purpose |
|------|---------|
| `dashboard/__init__.py` | App 패키지 초기화 |
| `dashboard/apps.py` | App 설정 |
| `dashboard/urls.py` | URL 라우팅 |
| `dashboard/views.py` | Composition root view + 데이터 수집 함수 |
| `dashboard/templatetags/__init__.py` | Templatetags 패키지 초기화 |
| `dashboard/templatetags/dashboard_tags.py` | 커스텀 필터 (currency, status, icon) |
| `dashboard/templates/dashboard/root.html` | Composition root 템플릿 |
| `dashboard/sections/sales_chart/sales_chart.html` | 매출 차트 섹션 HTML |
| `dashboard/sections/sales_chart/sales_chart.js` | 매출 차트 Chart.js 초기화 |
| `dashboard/sections/recent_orders/recent_orders.html` | 최근 주문 섹션 HTML |
| `dashboard/sections/recent_orders/recent_orders.js` | 주문 테이블 인터랙션 |
| `dashboard/sections/notification_feed/notification_feed.html` | 알림 피드 섹션 HTML |
| `dashboard/sections/notification_feed/notification_feed.js` | 알림 읽음 처리 로직 |
