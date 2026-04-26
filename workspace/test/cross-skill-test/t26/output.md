# T26: Django Ninja API 외에 관리용 웹 페이지를 추가하려면?

**Skill:** implementation-django-ninja (Writing mode)
**Cross-skill references loaded:** implementation-django-web (뷰 레이어, 템플릿 아키텍처)

## [주요 내용]

Django Ninja는 API 전용이다. 관리용 웹 페이지는 **implementation-django-web** 스킬의 영역이며, TemplateView + 템플릿 상속 패턴을 사용한다.

### 프로젝트 구조: API + 웹 공존

```
myproject/
├── config/
│   ├── api.py           # NinjaAPI 인스턴스
│   ├── urls.py          # api.urls + web URLs
│   └── settings.py
├── orders/
│   ├── api.py           # Router() -- Django Ninja API
│   ├── models.py
│   └── services.py      # 비즈니스 로직 (공유)
└── web/
    ├── view_urls.py     # 웹 페이지 URL 패턴
    └── views/
        └── orders/
            └── views.py # TemplateView -- 웹 페이지
```

### API 엔드포인트 (Django Ninja)

```python
# orders/api.py
from ninja import Router

router = Router(tags=["orders"])

@router.get("/", response=list[OrderOut])
def list_orders(request):
    return Order.objects.select_related("customer").all()
```

### 관리용 웹 페이지 (implementation-django-web 위임)

```python
# web/views/orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from orders.services import OrderService

class OrderAdminView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = OrderService.get_list(user=self.request.user)
        return ctx
```

### URL 통합

```python
# config/urls.py
from django.urls import path, include
from config.api import api

urlpatterns = [
    path("api/", api.urls),                    # Django Ninja API
    path("", include("web.view_urls")),         # 웹 페이지
]
```

핵심: 서비스 레이어를 API와 웹 뷰가 공유하여 로직 중복을 방지한다.

---
> **관련 스킬 참조:**
> - [TemplateView, 템플릿 상속, 디자인 시스템] → **implementation-django-web** 스킬
> - [서비스 레이어 아키텍처] → **implementation-django** 스킬
> - [HTMX 인터랙션, AJAX CSRF] → **implementation-django-web** 스킬
