# 뷰 레이어 레퍼런스

> Django 웹 페이지의 뷰 계층 구조, API 클라이언트 패턴, 뷰 분류 규칙을 다룬다.

---

## 1. 뷰 아키텍처 패턴

### 직접 서비스 호출 (기본)

모놀리식 Django 프로젝트에서 뷰는 서비스 레이어를 직접 호출하는 것이 표준 패턴이다.

```python
from django.views.generic import TemplateView
from orders.services import OrderService


class OrderListView(TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = OrderService.get_list(user=self.request.user)
        ctx["stats"] = OrderService.get_stats()
        return ctx
```

### Internal API Client 패턴

웹 프론트엔드와 도메인 로직의 결합을 끊기 위해, 뷰가 서비스 대신 내부 API를 HTTP로 호출하는 패턴이다. API와 웹이 동일한 인터페이스로 데이터를 소비하게 되어 일관성이 높아진다.

이 패턴은 Sam Newman이 정의한 BFF(Backends for Frontends) 패턴에서 영감을 받았지만, 원래 BFF는 마이크로서비스 아키텍처에서 프론트엔드 유형별(웹, 모바일 등) 별도의 백엔드 서비스를 두는 패턴이다. 모놀리스 내부에서 자기 자신에게 HTTP 호출을 하는 것은 BFF의 축소 적용이며, 네트워크 오버헤드와 실패 지점이 추가되는 트레이드오프가 있다.

출처: Sam Newman — Backends For Frontends (https://samnewman.io/patterns/architectural/bff/), Microsoft Azure — BFF pattern (https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)

```
웹 브라우저
    │
    ▼
Django View (TemplateView)
    │
    ▼ HTTP 호출
내부 API (Django Ninja 등)
    │
    ▼
도메인 서비스 / Repository
```

```python
# web/api_client.py
import requests
from django.conf import settings


class InternalAPIClient:
    """내부 API를 HTTP로 호출하는 클라이언트."""

    def __init__(self, request):
        self.base_url = settings.INTERNAL_API_BASE_URL
        self.session = requests.Session()
        # 원본 요청의 인증 정보 전달
        if "Authorization" in request.headers:
            self.session.headers["Authorization"] = request.headers["Authorization"]
        self.session.cookies = request.COOKIES

    def get(self, path: str, params: dict = None) -> dict:
        response = self.session.get(f"{self.base_url}/{path}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: dict = None) -> dict:
        response = self.session.post(f"{self.base_url}/{path}", json=data)
        response.raise_for_status()
        return response.json()
```

```python
# 뷰에서 사용
class OrderListView(TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        ctx["orders"] = api.get("orders/")
        ctx["stats"] = api.get("orders/stats/")
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

---

## 2. 접근 제어

뷰에 인증/인가를 적용할 때 Django의 내장 믹스인을 사용한다. 믹스인은 `TemplateView` 앞에 위치해야 한다 (MRO 순서).

출처: Django 공식 문서 — Authentication views (https://docs.djangoproject.com/en/5.2/topics/auth/default/#the-loginrequiredmixin-mixin)

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView


# 로그인 필수
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard_root.html"
    login_url = "/login/"              # 미인증 시 리다이렉트 (선택적)


# 로그인 + 특정 권한 필수
class AdminReportView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "admin/report.html"
    permission_required = "reports.view_report"
```

- `LoginRequiredMixin`: 미인증 사용자를 로그인 페이지로 리다이렉트
- `PermissionRequiredMixin`: 특정 권한이 없으면 403 응답
- 믹스인 순서: `LoginRequiredMixin` → `PermissionRequiredMixin` → `TemplateView`

---

## 3. 뷰 분류

### 페이지 뷰

일반 웹 페이지를 렌더링하는 뷰. `TemplateView`를 상속하고 `get_context_data`에서 데이터를 가져온다.

출처: Django 공식 문서 — TemplateView (https://docs.djangoproject.com/en/5.2/ref/class-based-views/base/#templateview)

```python
class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = OrderService.get_list(user=self.request.user)
        return ctx
```

### 웹 전용 플로우 뷰

OAuth 리다이렉트/콜백 등 웹에서만 필요한 플로우. 서비스 직접 호출이 허용된다.

```python
from django.shortcuts import redirect
from django.views import View


class OAuthCallbackView(View):
    """OAuth 콜백 — 웹 전용 플로우이므로 서비스 직접 호출 허용."""

    def get(self, request):
        code = request.GET.get("code")
        user = auth_service.complete_oauth(code)
        login(request, user)
        return redirect("dashboard")
```

### DEBUG 전용 뷰

개발 환경에서만 사용하는 테스트/디버그 페이지.

```python
from django.conf import settings
from django.views.generic import TemplateView


class DesignSystemPreview(TemplateView):
    """디자인 시스템 컴포넌트 미리보기 — DEBUG 전용."""
    template_name = "dev/design_system_preview.html"
```

```python
# web/view_urls.py
urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += [
        path("dev/design-system/", DesignSystemPreview.as_view()),
    ]
```

---

## 4. 에러 처리

뷰에서 발생하는 예외를 적절히 처리하여 사용자에게 의미 있는 에러 페이지를 보여준다.

출처: Django 공식 문서 — Error reporting (https://docs.djangoproject.com/en/5.2/howto/error-reporting/)

### API 호출 실패 처리 (Internal API Client 사용 시)

```python
import requests
from django.views.generic import TemplateView


class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/orders_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        try:
            ctx["orders"] = api.get("orders/")
        except requests.HTTPError as e:
            ctx["orders"] = []
            ctx["error_message"] = "주문 목록을 불러올 수 없습니다."
        return ctx
```

### 커스텀 에러 페이지

```python
# 프로젝트 templates/ 에 배치
# templates/404.html, templates/500.html
```

```python
# urls.py
handler404 = "web.views.errors.page_not_found"
handler500 = "web.views.errors.server_error"
```

---

## 5. 뷰 폴더 구조

```
web/
├── api_client.py              # 내부 API 클라이언트 (선택적)
├── view_urls.py               # 웹 뷰 URL 패턴
└── views/
    ├── __init__.py
    ├── <page>/                # 페이지별 뷰 모듈
    │   ├── __init__.py
    │   └── views.py
    ├── auth/                  # OAuth 등 웹 전용 플로우
    │   ├── __init__.py
    │   └── views.py
    └── dev/                   # DEBUG 전용 뷰
        ├── __init__.py
        └── views.py
```

- 뷰 파일은 페이지 단위로 폴더를 나눈다
- URL 패턴은 `view_urls.py`에 통합 관리
- `web/` 폴더는 DDD 도메인 밖에 위치한다 (프레젠테이션 계층)

### URL 네임스페이싱

출처: Django 공식 문서 — URL namespaces (https://docs.djangoproject.com/en/5.2/topics/http/urls/#url-namespaces)

```python
# web/view_urls.py
app_name = "web"

urlpatterns = [
    path("orders/", OrderListView.as_view(), name="orders"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
```

```htmldjango
{# 템플릿에서 URL 참조 #}
<a href="{% url 'web:orders' %}">주문 목록</a>
```

---

## 6. 페이지 렌더링 흐름

### SSR (Server-Side Rendering) — 페이지 로드

```
[브라우저] GET /orders/
    → [OrderListView.get_context_data()]
        → [서비스/API 호출] → [DB]
    ← 템플릿 렌더링 (orders_root.html + 컨텍스트)
← HTML 응답
```

### AJAX — 유저 인터랙션

브라우저에서 JavaScript로 API를 직접 호출한다. Django의 CSRF 보호 메커니즘을 반드시 준수해야 한다.

출처: Django 공식 문서 — CSRF protection (https://docs.djangoproject.com/en/5.2/howto/csrf/)

```javascript
// CSRF 토큰 가져오기 (Django 공식 문서 권장 방법)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// POST 요청 시 CSRF 토큰 포함
fetch("/api/orders/1/complete/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),    // CSRF 토큰 필수
    },
    mode: "same-origin",                          // CORS 설정
    body: JSON.stringify({ status: "completed" }),
});
```

- POST/PUT/PATCH/DELETE 요청에 `X-CSRFToken` 헤더 필수
- CSRF 토큰은 `csrftoken` 쿠키에서 가져온다
- 뷰에서 `@ensure_csrf_cookie` 데코레이터로 쿠키 발급을 보장할 수 있다
- `mode: "same-origin"` 설정 권장

### HTMX — 서버 렌더 HTML 조각

HTMX를 사용하면 JavaScript를 작성하지 않고도 서버에서 렌더링한 HTML 조각으로 DOM을 업데이트할 수 있다. Django의 템플릿 시스템과 자연스럽게 결합된다.

출처: django-htmx-patterns (https://github.com/spookylukey/django-htmx-patterns), HTMX (https://htmx.org/)

```htmldjango
{# 주문 목록에서 완료 버튼 #}
<button hx-post="{% url 'web:complete-order' order.id %}"
        hx-target="#order-{{ order.id }}"
        hx-swap="outerHTML">
    완료
</button>
```

```python
from django.views import View
from django.template.response import TemplateResponse


class CompleteOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = OrderService.complete(order_id)
        # HTMX 요청이면 부분 HTML만, 아니면 전체 페이지 리다이렉트
        if request.headers.get("HX-Request"):
            return TemplateResponse(request, "orders/order_card/order_card.html", {"order": order})
        return redirect("web:orders")
```

- 초기 페이지 로드: SSR (View → 서비스 → 템플릿)
- 이후 인터랙션: HTMX (HTML 조각) 또는 AJAX (JSON)
- HTMX는 Django 6.0 `{% partialdef %}` / `{% partial %}`과 함께 사용하면 더 효과적이다

---

## 7. Context Processors

모든 템플릿에서 공통으로 사용하는 데이터는 context processor로 제공한다.

출처: Django 공식 문서 — Context processors (https://docs.djangoproject.com/en/5.2/ref/templates/api/#writing-your-own-context-processors)

```python
# web/context_processors.py
def navigation(request):
    """네비게이션에 필요한 공통 데이터."""
    return {
        "nav_items": [
            {"url": "/orders/", "label": "주문", "active": request.path.startswith("/orders/")},
            {"url": "/dashboard/", "label": "대시보드", "active": request.path.startswith("/dashboard/")},
        ],
    }
```

```python
# settings.py
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                # Django 기본 + 커스텀
                "web.context_processors.navigation",
            ],
        },
    },
]
```

- 모든 뷰에서 중복되는 컨텍스트 데이터에 사용한다
- 무거운 쿼리는 context processor에 넣지 않는다 (모든 페이지에서 실행됨)
