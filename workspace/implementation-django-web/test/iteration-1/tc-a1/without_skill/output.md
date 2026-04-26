# Django Order List Page Implementation

## Task
주문(Order) 목록 페이지 구현
- 3-tier 템플릿 상속: `base.html` -> `base_orders.html` -> `order_list.html`
- Chart.js를 활용한 주문 통계 시각화 (총 주문 수, 이번 달 매출)
- 인증된 사용자만 접근 가능
- 서비스 레이어에서 주문 데이터 조회

---

## 1. Model (`orders/models.py`)

```python
from django.db import models
from django.conf import settings


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "대기"
        CONFIRMED = "confirmed", "확인"
        SHIPPED = "shipped", "배송중"
        DELIVERED = "delivered", "배송완료"
        CANCELLED = "cancelled", "취소"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    order_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"
```

---

## 2. Service Layer (`orders/services.py`)

```python
from datetime import date
from decimal import Decimal
from typing import TypedDict

from django.db.models import Count, Sum, QuerySet
from django.db.models.functions import TruncMonth
from django.contrib.auth import get_user_model

from .models import Order

User = get_user_model()


class MonthlyStats(TypedDict):
    month: str
    count: int
    revenue: Decimal


class OrderStatistics(TypedDict):
    total_orders: int
    current_month_revenue: Decimal
    monthly_stats: list[MonthlyStats]


class OrderService:
    """주문 관련 비즈니스 로직을 담당하는 서비스 레이어."""

    @staticmethod
    def get_order_list(user: User) -> QuerySet[Order]:
        """사용자의 주문 목록을 반환한다."""
        return Order.objects.filter(user=user).select_related("user")

    @staticmethod
    def get_order_statistics(user: User) -> OrderStatistics:
        """주문 통계 데이터를 반환한다."""
        orders = Order.objects.filter(user=user)

        total_orders = orders.count()

        today = date.today()
        current_month_revenue = (
            orders.filter(
                created_at__year=today.year,
                created_at__month=today.month,
            )
            .exclude(status=Order.Status.CANCELLED)
            .aggregate(revenue=Sum("total_amount"))["revenue"]
            or Decimal("0")
        )

        monthly_stats = list(
            orders.exclude(status=Order.Status.CANCELLED)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"), revenue=Sum("total_amount"))
            .order_by("month")[:6]
        )

        return OrderStatistics(
            total_orders=total_orders,
            current_month_revenue=current_month_revenue,
            monthly_stats=[
                MonthlyStats(
                    month=s["month"].strftime("%Y-%m"),
                    count=s["count"],
                    revenue=s["revenue"],
                )
                for s in monthly_stats
            ],
        )
```

---

## 3. View (`orders/views.py`)

```python
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Order
from .services import OrderService


class OrderListView(LoginRequiredMixin, ListView):
    """인증된 사용자의 주문 목록 + 통계 차트 페이지."""

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20
    login_url = "/accounts/login/"

    def get_queryset(self):
        return OrderService.get_order_list(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = OrderService.get_order_statistics(self.request.user)

        context["total_orders"] = stats["total_orders"]
        context["current_month_revenue"] = stats["current_month_revenue"]

        # Chart.js에 전달할 JSON 데이터
        context["chart_labels"] = json.dumps(
            [s["month"] for s in stats["monthly_stats"]]
        )
        context["chart_order_counts"] = json.dumps(
            [s["count"] for s in stats["monthly_stats"]]
        )
        context["chart_revenues"] = json.dumps(
            [str(s["revenue"]) for s in stats["monthly_stats"]]
        )
        return context
```

---

## 4. URL Configuration (`orders/urls.py`)

```python
from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order_list"),
]
```

프로젝트 루트 `urls.py`에 포함:

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("orders/", include("orders.urls")),
]
```

---

## 5. Templates

### 5-1. `templates/base.html` (1단계)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Shop{% endblock %}</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .site-header {
            background: #1a1a2e;
            color: #fff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .site-header h1 { font-size: 1.25rem; }
        .site-header nav a {
            color: #ccc;
            text-decoration: none;
            margin-left: 1.5rem;
            font-size: 0.9rem;
        }
        .site-header nav a:hover { color: #fff; }
        .site-content { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .site-footer {
            text-align: center;
            padding: 1.5rem;
            color: #888;
            font-size: 0.85rem;
            border-top: 1px solid #e0e0e0;
            margin-top: 3rem;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header class="site-header">
        <h1>My Shop</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/orders/">Orders</a>
            {% if user.is_authenticated %}
                <a href="/accounts/logout/">Logout</a>
            {% else %}
                <a href="/accounts/login/">Login</a>
            {% endif %}
        </nav>
    </header>

    <main class="site-content">
        {% block content %}{% endblock %}
    </main>

    <footer class="site-footer">
        &copy; 2026 My Shop. All rights reserved.
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 5-2. `templates/orders/base_orders.html` (2단계)

```html
{% extends "base.html" %}

{% block title %}Orders - {% block orders_title %}{% endblock %}{% endblock %}

{% block extra_css %}
<style>
    .orders-layout {
        display: grid;
        grid-template-columns: 220px 1fr;
        gap: 2rem;
    }
    .orders-sidebar {
        background: #fff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        height: fit-content;
    }
    .orders-sidebar h3 {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #888;
        margin-bottom: 1rem;
    }
    .orders-sidebar a {
        display: block;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.25rem;
        color: #555;
        text-decoration: none;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .orders-sidebar a:hover,
    .orders-sidebar a.active {
        background: #e8f0fe;
        color: #1a73e8;
    }
    .orders-main { min-width: 0; }

    @media (max-width: 768px) {
        .orders-layout {
            grid-template-columns: 1fr;
        }
    }
</style>
{% block orders_extra_css %}{% endblock %}
{% endblock %}

{% block content %}
<div class="orders-layout">
    <aside class="orders-sidebar">
        <h3>Orders Menu</h3>
        <a href="/orders/" class="{% block sidebar_list_active %}{% endblock %}">Order List</a>
        <a href="/orders/stats/">Statistics</a>
        <a href="/orders/returns/">Returns</a>
    </aside>
    <div class="orders-main">
        {% block orders_content %}{% endblock %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
{% block orders_extra_js %}{% endblock %}
{% endblock %}
```

### 5-3. `templates/orders/order_list.html` (3단계)

```html
{% extends "orders/base_orders.html" %}

{% block orders_title %}Order List{% endblock %}
{% block sidebar_list_active %}active{% endblock %}

{% block orders_extra_css %}
<style>
    .stats-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: #fff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .stat-card .label {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 0.25rem;
    }
    .stat-card .value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .chart-section {
        background: #fff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
    }
    .chart-section h2 {
        font-size: 1.1rem;
        margin-bottom: 1rem;
        color: #333;
    }
    .chart-container {
        position: relative;
        height: 300px;
    }
    .order-table-section {
        background: #fff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .order-table-section h2 {
        font-size: 1.1rem;
        margin-bottom: 1rem;
        color: #333;
    }
    .order-table {
        width: 100%;
        border-collapse: collapse;
    }
    .order-table th,
    .order-table td {
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 1px solid #eee;
        font-size: 0.9rem;
    }
    .order-table th {
        background: #f8f9fa;
        font-weight: 600;
        color: #555;
    }
    .order-table tr:hover { background: #fafbfc; }
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-pending   { background: #fff3cd; color: #856404; }
    .status-confirmed { background: #d1ecf1; color: #0c5460; }
    .status-shipped   { background: #cce5ff; color: #004085; }
    .status-delivered  { background: #d4edda; color: #155724; }
    .status-cancelled  { background: #f8d7da; color: #721c24; }
    .pagination-nav {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
    }
    .pagination-nav a,
    .pagination-nav span {
        padding: 0.4rem 0.8rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        text-decoration: none;
        color: #555;
        font-size: 0.85rem;
    }
    .pagination-nav span.current {
        background: #1a73e8;
        color: #fff;
        border-color: #1a73e8;
    }
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #888;
    }
</style>
{% endblock %}

{% block orders_content %}
<!-- Statistics Cards -->
<div class="stats-cards">
    <div class="stat-card">
        <div class="label">Total Orders</div>
        <div class="value">{{ total_orders }}</div>
    </div>
    <div class="stat-card">
        <div class="label">This Month Revenue</div>
        <div class="value">{{ current_month_revenue|floatformat:0 }} won</div>
    </div>
</div>

<!-- Chart Section -->
<div class="chart-section">
    <h2>Monthly Order Statistics</h2>
    <div class="chart-container">
        <canvas id="orderChart"></canvas>
    </div>
</div>

<!-- Order Table -->
<div class="order-table-section">
    <h2>Order List</h2>
    {% if orders %}
    <table class="order-table">
        <thead>
            <tr>
                <th>Order Number</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.order_number }}</td>
                <td>
                    <span class="status-badge status-{{ order.status }}">
                        {{ order.get_status_display }}
                    </span>
                </td>
                <td>{{ order.total_amount|floatformat:0 }} won</td>
                <td>{{ order.created_at|date:"Y-m-d H:i" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- Pagination -->
    {% if is_paginated %}
    <nav class="pagination-nav">
        {% if page_obj.has_previous %}
            <a href="?page=1">First</a>
            <a href="?page={{ page_obj.previous_page_number }}">Prev</a>
        {% endif %}

        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}
                <span class="current">{{ num }}</span>
            {% elif num > page_obj.number|add:"-3" and num < page_obj.number|add:"3" %}
                <a href="?page={{ num }}">{{ num }}</a>
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}">Next</a>
            <a href="?page={{ page_obj.paginator.num_pages }}">Last</a>
        {% endif %}
    </nav>
    {% endif %}

    {% else %}
    <div class="empty-state">
        <p>No orders yet.</p>
    </div>
    {% endif %}
</div>
{% endblock %}

{% block orders_extra_js %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById("orderChart").getContext("2d");

    const labels = JSON.parse('{{ chart_labels|escapejs }}');
    const orderCounts = JSON.parse('{{ chart_order_counts|escapejs }}');
    const revenues = JSON.parse('{{ chart_revenues|escapejs }}').map(Number);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Orders",
                    data: orderCounts,
                    backgroundColor: "rgba(26, 115, 232, 0.7)",
                    borderColor: "rgba(26, 115, 232, 1)",
                    borderWidth: 1,
                    yAxisID: "y",
                    order: 2
                },
                {
                    label: "Revenue (won)",
                    data: revenues,
                    type: "line",
                    borderColor: "rgba(234, 67, 53, 1)",
                    backgroundColor: "rgba(234, 67, 53, 0.1)",
                    borderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    yAxisID: "y1",
                    order: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            scales: {
                y: {
                    type: "linear",
                    position: "left",
                    title: { display: true, text: "Orders" },
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                },
                y1: {
                    type: "linear",
                    position: "right",
                    title: { display: true, text: "Revenue (won)" },
                    beginAtZero: true,
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: { position: "top" }
            }
        }
    });
});
</script>
{% endblock %}
```

---

## 6. Tests (`orders/tests.py`)

```python
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.urls import reverse

from .models import Order
from .services import OrderService

User = get_user_model()


class OrderServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        Order.objects.create(
            user=self.user,
            order_number="ORD-001",
            status=Order.Status.DELIVERED,
            total_amount=Decimal("50000"),
        )
        Order.objects.create(
            user=self.user,
            order_number="ORD-002",
            status=Order.Status.PENDING,
            total_amount=Decimal("30000"),
        )
        Order.objects.create(
            user=self.user,
            order_number="ORD-003",
            status=Order.Status.CANCELLED,
            total_amount=Decimal("10000"),
        )

    def test_get_order_list_returns_user_orders(self):
        orders = OrderService.get_order_list(self.user)
        self.assertEqual(orders.count(), 3)

    def test_get_order_list_excludes_other_users(self):
        other = User.objects.create_user(
            username="other", password="pass123"
        )
        orders = OrderService.get_order_list(other)
        self.assertEqual(orders.count(), 0)

    def test_get_order_statistics_total(self):
        stats = OrderService.get_order_statistics(self.user)
        self.assertEqual(stats["total_orders"], 3)

    def test_get_order_statistics_excludes_cancelled_from_revenue(self):
        stats = OrderService.get_order_statistics(self.user)
        # cancelled order (10000) should be excluded from revenue
        self.assertEqual(
            stats["current_month_revenue"], Decimal("80000")
        )


class OrderListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        for i in range(5):
            Order.objects.create(
                user=self.user,
                order_number=f"ORD-{i:03d}",
                status=Order.Status.PENDING,
                total_amount=Decimal("10000"),
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_logged_in_user_can_access(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:order_list"))
        self.assertTemplateUsed(response, "orders/order_list.html")
        self.assertTemplateUsed(response, "orders/base_orders.html")
        self.assertTemplateUsed(response, "base.html")

    def test_context_contains_statistics(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:order_list"))
        self.assertIn("total_orders", response.context)
        self.assertIn("current_month_revenue", response.context)
        self.assertIn("chart_labels", response.context)
        self.assertIn("chart_order_counts", response.context)
        self.assertIn("chart_revenues", response.context)

    def test_only_own_orders_displayed(self):
        other = User.objects.create_user(
            username="other", password="pass123"
        )
        Order.objects.create(
            user=other,
            order_number="OTHER-001",
            status=Order.Status.PENDING,
            total_amount=Decimal("99999"),
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(len(response.context["orders"]), 5)
```

---

## File Structure Summary

```
project/
  urls.py                          # include("orders.urls")
  templates/
    base.html                      # Tier 1 - site-wide base
    orders/
      base_orders.html             # Tier 2 - orders section layout
      order_list.html              # Tier 3 - order list page
orders/
  __init__.py
  models.py                        # Order model
  services.py                      # OrderService (service layer)
  views.py                         # OrderListView (LoginRequiredMixin)
  urls.py                          # app_name = "orders"
  tests.py                         # unit + integration tests
```

## Key Design Decisions

| Concern | Decision |
|---|---|
| Authentication | `LoginRequiredMixin` on the CBV; unauthenticated users redirect to `/accounts/login/` |
| Service layer | `OrderService` class with `@staticmethod` methods keeps business logic out of views |
| Chart data | Serialized to JSON in the view via `json.dumps`, passed to Chart.js through Django template variables with `escapejs` filter |
| Chart type | Combined bar (order count) + line (revenue) chart with dual Y-axes for clear visual comparison |
| Cancelled orders | Excluded from revenue calculations but included in total order count |
| Pagination | 20 items per page via `ListView.paginate_by` |
| Template inheritance | 3-tier: `base.html` (site chrome) -> `base_orders.html` (orders sidebar layout) -> `order_list.html` (page content) |
| Monthly stats | Last 6 months aggregated via `TruncMonth`, used for chart data |
