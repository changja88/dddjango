# D11 Cross-Skill: implementation-django-web + implementation-django-ninja

**Prompt:** "웹 페이지에서 주문 목록을 보여주는데, 같은 데이터를 REST API로도 제공해야 해. 서비스 레이어를 공유하는 방법이 있을까?"

**Activated Skill:** implementation-django-web (Writing 모드)

**Loaded References:** `references/view-layer.md` (뷰 아키텍처 패턴 섹션)

---

## 응답

서비스 레이어를 웹 뷰와 REST API에서 공유하는 방법은 두 가지 패턴이 있다. 프로젝트 상황에 맞는 패턴을 선택한다.

### 패턴 1: 직접 서비스 호출 (기본 -- 대부분의 프로젝트에 적합)

웹 뷰와 API 엔드포인트가 동일한 서비스 레이어를 각각 직접 호출한다. 모놀리식 Django 프로젝트에서 가장 단순하고 성능 오버헤드가 없는 표준 패턴이다.

```
[브라우저] GET /orders/           [클라이언트] GET /api/orders/
    │                                  │
    ▼                                  ▼
Django TemplateView              Django Ninja Router
    │                                  │
    └──────────┐    ┌──────────────────┘
               ▼    ▼
          OrderService.get_list()
               │
               ▼
              DB
```

```python
# orders/services.py -- 공유 서비스 레이어
from orders.models import Order


class OrderService:
    @staticmethod
    def get_list(user) -> list[Order]:
        return list(Order.objects.filter(user=user).select_related("product"))

    @staticmethod
    def get_stats() -> dict:
        return Order.objects.aggregate(...)
```

```python
# web/views/orders/views.py -- 웹 뷰에서 서비스 직접 호출
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from orders.services import OrderService


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = OrderService.get_list(user=self.request.user)
        ctx["stats"] = OrderService.get_stats()
        return ctx
```

```python
# api/routers/orders.py -- API 엔드포인트에서 동일한 서비스 호출
from ninja import Router
from orders.services import OrderService
from api.schemas.orders import OrderOut

router = Router(tags=["orders"])


@router.get("/", response=list[OrderOut])
def list_orders(request):
    return OrderService.get_list(user=request.user)
```

핵심은 도메인 로직을 `orders/services.py`에 집중시키고, 웹 뷰(`TemplateView`)와 API 엔드포인트(`Router`)는 각각 서비스를 호출한 뒤 자기 포맷(HTML 템플릿 / JSON Schema)으로 변환만 담당하는 것이다.

### 패턴 2: Internal API Client (웹/API 일관성이 핵심인 경우)

웹 뷰가 서비스를 직접 호출하지 않고, 내부 API를 HTTP로 호출하는 패턴이다. API가 유일한 데이터 접근 경로가 되어 웹과 API의 응답 형태가 항상 동일해진다. 단, HTTP 왕복에 의한 네트워크 오버헤드와 실패 지점이 추가되는 트레이드오프가 있다.

```python
# web/api_client.py
import requests
from django.conf import settings


class InternalAPIClient:
    """내부 API를 HTTP로 호출하는 클라이언트."""

    def __init__(self, request):
        self.base_url = settings.INTERNAL_API_BASE_URL
        self.session = requests.Session()
        if "Authorization" in request.headers:
            self.session.headers["Authorization"] = request.headers["Authorization"]
        self.session.cookies = request.COOKIES

    def get(self, path: str, params: dict = None) -> dict:
        response = self.session.get(f"{self.base_url}/{path}", params=params)
        response.raise_for_status()
        return response.json()
```

```python
# web/views/orders/views.py -- Internal API Client 사용
class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        try:
            ctx["orders"] = api.get("orders/")
            ctx["stats"] = api.get("orders/stats/")
        except requests.HTTPError:
            ctx["orders"] = []
            ctx["error_message"] = "주문 목록을 불러올 수 없습니다."
        return ctx
```

### 패턴 선택 기준

| 기준 | 직접 서비스 호출 | Internal API Client |
|------|------------------|---------------------|
| 아키텍처 | 모놀리스 | 모놀리스 + API 분리, 마이크로서비스 |
| 성능 | 함수 호출 (오버헤드 없음) | HTTP 왕복 (네트워크 오버헤드) |
| 일관성 | 웹/API가 다른 경로로 데이터 접근 | 웹/API 동일 인터페이스 |
| 복잡도 | 단순 | API 클라이언트 유지보수 필요 |
| 적합한 경우 | 대부분의 Django 프로젝트 | API가 별도 서비스이거나 웹/API 일관성이 핵심인 경우 |

대부분의 경우 **패턴 1(직접 서비스 호출)**을 권장한다. 서비스 레이어(`OrderService`)를 단일 진실 공급원(single source of truth)으로 유지하면, 웹 뷰와 API 엔드포인트가 동일한 비즈니스 로직을 공유하면서도 각자의 프레젠테이션 형태(HTML/JSON)에 집중할 수 있다.

---
> **관련 스킬 참조:**
> - API 엔드포인트 구현 (Schema, Router, 인증, 페이지네이션) -> **implementation-django-ninja** 스킬
> - REST API 설계 원칙 (URL 구조, 상태 코드, 에러 형식) -> **architecture-api** 스킬
> - 서비스 레이어의 모델/ORM 설계 -> **implementation-django** 스킬
