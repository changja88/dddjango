# Refactoring: DashboardView / OrderApiView

## Loaded Skills

**Base Skills (always applied):**
- implementation-cleancode (Refactoring mode)
- implementation-python (Refactoring mode)
- implementation-django (Refactoring mode)

**Additional Skills (auto-selected based on code analysis):**
- implementation-django-web -- `TemplateView`, `template_name` 사용 감지
- architecture-api -- `JsonResponse`를 반환하는 API 엔드포인트 감지

---

## Changes

### Change 1: Function-level import to module-level import

```python
# [Before]
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    from orders.models import Order
    orders = Order.objects.filter(user=self.request.user).order_by('-created_at')[:20]
```

```python
# [After]
from orders.models import Order

class DashboardView(LoginRequiredMixin, TemplateView):
    ...
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
```

**[Reason]** Django Coding Style / Clean Code: Naming & Structure -- import는 모듈 최상단에 위치해야 한다. 함수 내부 import는 순환 의존성 해결 같은 특수한 경우에만 허용된다. 여기서는 그런 제약이 없으므로 표준 위치로 이동한다.

---

### Change 2: Add `LoginRequiredMixin` to `DashboardView`

```python
# [Before]
class DashboardView(TemplateView):
    template_name = "dashboard.html"
```

```python
# [After]
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
```

**[Reason]** Django Web View Layer -- `self.request.user`로 사용자별 데이터를 조회하는 뷰는 반드시 인증을 요구해야 한다. `LoginRequiredMixin`을 MRO 순서에 맞게 `TemplateView` 앞에 배치한다. 템플릿 경로도 앱별 네임스페이싱(`dashboard/dashboard.html`)을 적용한다.

---

### Change 3: Extract business logic from view to selectors/services

```python
# [Before]
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    from orders.models import Order
    orders = Order.objects.filter(user=self.request.user).order_by('-created_at')[:20]
    ctx["orders"] = orders
    ctx["total_revenue"] = sum(o.total for o in orders)
    ctx["pending_count"] = len([o for o in orders if o.status == "pending"])
    return ctx
```

```python
# [After]
# orders/selectors.py
from django.db.models import QuerySet, Sum, Count, Q

from orders.models import Order


def order_list_by_user(*, user: "User", limit: int = 20) -> QuerySet[Order]:
    """Return recent orders for the given user."""
    return (
        Order.objects
        .filter(user=user)
        .order_by("-created_at")[:limit]
    )


def order_dashboard_stats(*, user: "User") -> dict:
    """Return aggregated dashboard statistics for the user's orders."""
    return (
        Order.objects
        .filter(user=user)
        .aggregate(
            total_revenue=Sum("total"),
            pending_count=Count("id", filter=Q(status="pending")),
        )
    )
```

```python
# views.py
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    user = self.request.user
    ctx["orders"] = order_list_by_user(user=user)
    ctx |= order_dashboard_stats(user=user)
    return ctx
```

**[Reason]** Django Service Layer / Fat View -- 비즈니스 로직(쿼리, 집계)이 뷰에 직접 들어 있으면 재사용이 불가능하고 테스트하기 어렵다. HackSoft `<entity>_<action>` 네이밍 규칙을 따르는 셀렉터 함수로 추출한다. 또한 `sum(o.total for o in orders)`는 Python에서 모든 객체를 메모리에 로드한 후 합산하는 비효율적 패턴이다. `aggregate(Sum("total"))`로 DB 레벨에서 계산하면 성능이 크게 향상된다.

---

### Change 4: Replace Python-level filtering with DB-level aggregation

```python
# [Before]
ctx["total_revenue"] = sum(o.total for o in orders)
ctx["pending_count"] = len([o for o in orders if o.status == "pending"])
```

```python
# [After]
Order.objects.filter(user=user).aggregate(
    total_revenue=Sum("total"),
    pending_count=Count("id", filter=Q(status="pending")),
)
```

**[Reason]** Django QuerySet Optimization -- `sum(o.total for o in orders)`는 모든 Order 객체를 Python 메모리에 인스턴스화한 후 순회한다. `aggregate(Sum(...))`는 DB에서 단일 SQL `SUM()`으로 계산한다. 마찬가지로 `len([o for o in orders if o.status == "pending"])`는 리스트 컴프리헨션으로 중간 리스트를 생성한 후 `len()`을 호출한다. `Count(..., filter=Q(status="pending"))`은 DB에서 조건부 `COUNT`로 처리한다. 슬라이스(`[:20]`)가 적용된 최근 20건의 합이 아닌 사용자 전체 주문의 통계가 의미상 더 정확하므로, 집계 쿼리는 별도로 실행한다.

---

### Change 5: Replace `TemplateView` misuse with proper API view

```python
# [Before]
class OrderApiView(TemplateView):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all().values('id', 'status', 'total')
        return JsonResponse({'orders': list(orders)})
```

```python
# [After]
from django.http import JsonResponse
from django.views import View


class OrderApiView(View):
    """Temporary JSON endpoint -- migrate to Django Ninja Router."""

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.values("id", "status", "total")
        return JsonResponse({"orders": list(orders)})
```

**[Reason]** Django View Pattern / Architecture API -- `TemplateView`는 템플릿을 렌더링하는 뷰를 위한 클래스다. JSON을 반환하는 API 엔드포인트에 `TemplateView`를 사용하면 불필요한 `template_name` 요구사항과 `get_context_data` 메커니즘이 포함된다. `View`로 변경하여 의도를 명확히 한다. 장기적으로는 Django Ninja `Router`로 마이그레이션하는 것이 권장된다. 또한 `Order`가 import 없이 사용되고 있어 `NameError`가 발생하는 버그도 수정한다.

---

### Change 6: Add type hints to all public methods

```python
# [Before]
def get_context_data(self, **kwargs):
    ...
def get(self, request, *args, **kwargs):
    ...
```

```python
# [After]
def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    ...
def get(self, request: HttpRequest) -> JsonResponse:
    ...
```

**[Reason]** Python Type Hints -- 모든 공개 메서드에 타입 어노테이션을 추가한다. 이는 코드의 계약을 명시적으로 만들고, mypy/pyright가 정적 분석으로 버그를 잡을 수 있게 한다. `*args, **kwargs`는 실제로 사용하지 않으므로 제거하여 시그니처를 간결하게 한다.

---

### Change 7: Add missing `Order` import and use `"pending"` magic string as constant

```python
# [Before]
ctx["pending_count"] = len([o for o in orders if o.status == "pending"])
```

```python
# [After]
# orders/models.py (assumed TextChoices on Order model)
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ...

# orders/selectors.py
pending_count=Count("id", filter=Q(status=Order.Status.PENDING)),
```

**[Reason]** Clean Code: Magic String / Django TextChoices -- `"pending"` 같은 매직 문자열은 오타에 취약하고 검색이 어렵다. Django의 `TextChoices`를 사용하면 타입 안전한 상수가 되며, IDE 자동완성과 리팩토링 도구의 지원을 받을 수 있다.

---

## Full Refactored Code

```python
# orders/selectors.py
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q, QuerySet, Sum

from orders.models import Order

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


def order_list_by_user(*, user: AbstractBaseUser, limit: int = 20) -> QuerySet[Order]:
    """Return the most recent orders for the given user."""
    return (
        Order.objects
        .filter(user=user)
        .order_by("-created_at")[:limit]
    )


def order_dashboard_stats(*, user: AbstractBaseUser) -> dict[str, int]:
    """Return aggregated revenue and pending count for the user."""
    return (
        Order.objects
        .filter(user=user)
        .aggregate(
            total_revenue=Sum("total"),
            pending_count=Count("id", filter=Q(status=Order.Status.PENDING)),
        )
    )
```

```python
# dashboard/views.py
from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from orders.selectors import order_dashboard_stats, order_list_by_user


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard showing recent orders and summary statistics."""

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["orders"] = order_list_by_user(user=user)
        ctx |= order_dashboard_stats(user=user)
        return ctx
```

```python
# orders/views_api.py
from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views import View

from orders.models import Order


class OrderApiView(View):
    """Temporary JSON endpoint for orders -- migrate to Django Ninja Router.

    This view returns a flat list of all orders. In production, add
    authentication, pagination, and filtering. See implementation-django-ninja
    skill for the recommended approach.
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.values("id", "status", "total")
        return JsonResponse({"orders": list(orders)})
```

---

## Behavioral Changes

| Item | Before | After | Migration Note |
|------|--------|-------|----------------|
| `total_revenue` scope | Top 20 orders only | All user orders | If top-20 revenue was intentional, add `[:20]` slice before `aggregate()` or compute in Python after fetching |
| `pending_count` scope | Top 20 orders only | All user orders | Same as above |
| Authentication | None (anonymous access possible) | `LoginRequiredMixin` redirects to login | Unauthenticated users will be redirected to `settings.LOGIN_URL` |
| `OrderApiView` base class | `TemplateView` | `View` | No template rendering; callers relying on `TemplateView` behavior must update |

---

> **Related Skills:**
> - [Django Ninja API migration] -> **implementation-django-ninja** skill
> - [Order model TextChoices design] -> **implementation-django** skill
> - [DB query optimization / indexing] -> **architecture-db** skill
> - [API pagination / error format] -> **architecture-api** skill
> - [Test coverage for selectors] -> **implementation-test** skill
