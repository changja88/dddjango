# C02: Django 프로젝트에서 웹 페이지와 REST API를 동시에 구현하는 방법

**Skill:** implementation-django (Writing mode)
**Cross-skill references loaded:** implementation-django-ninja (API), implementation-django-web (웹 페이지)

## [주요 내용]

### 프로젝트 구조: 서비스 레이어 공유

```
config/
├── api.py              # NinjaAPI 인스턴스
├── urls.py             # API + Web URL 통합
└── settings/
    └── base.py
apps/
└── orders/
    ├── models.py       # Fat Model
    ├── services.py     # 서비스 레이어 (API + Web 공유)
    ├── api.py          # Django Ninja Router
    └── selectors.py    # 읽기 전용 쿼리
web/
├── view_urls.py        # 웹 페이지 URL
└── views/
    └── orders/
        └── views.py    # TemplateView
```

### 서비스 레이어 (공유)

```python
# apps/orders/services.py
from django.db import transaction

def order_create(*, orderer_id: int, items: list[dict]) -> Order:
    with transaction.atomic():
        order = Order.objects.create(orderer_id=orderer_id)
        for item in items:
            OrderLine.objects.create(order=order, **item)
        return order
```

### REST API (implementation-django-ninja 위임)

```python
# apps/orders/api.py
from ninja import Router
router = Router(tags=["orders"])

@router.post("/", response={201: OrderOut})
def create_order(request, payload: OrderIn):
    order = order_create(orderer_id=request.user.id, items=payload.items)
    return 201, order
```

### 웹 페이지 (implementation-django-web 위임)

```python
# web/views/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from orders.selectors import order_list

class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = order_list(user=self.request.user)
        return ctx
```

### URL 통합

```python
# config/urls.py
urlpatterns = [
    path("api/", api.urls),
    path("", include("web.view_urls")),
]
```

핵심: 서비스 레이어가 API와 웹 뷰의 공통 로직을 캡슐화하여 DRY를 유지한다.

---
> **관련 스킬 참조:**
> - [Django Ninja Schema, Router] → **implementation-django-ninja** 스킬
> - [TemplateView, 템플릿 상속, HTMX] → **implementation-django-web** 스킬
> - [서비스 레이어 패턴] → 이 스킬 `references/service-layer.md`
