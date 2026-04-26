# Django View Code Review

## 대상 코드

```python
from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = "dashboard/dashboard_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        api = InternalAPIClient(self.request)
        ctx["revenue"] = api.get("stats/revenue/")
        ctx["orders"] = api.get("orders/recent/")
        ctx["notifications"] = api.get("notifications/")
        return ctx


class OrderDetailView(TemplateView):
    template_name = "orders/order_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_id = self.kwargs["order_id"]
        from orders.services import OrderService
        ctx["order"] = OrderService.get_detail(order_id)
        ctx["history"] = OrderService.get_history(order_id)
        return ctx
```

---

## 1. 누락된 import 문

### `InternalAPIClient` import 누락

`DashboardView`에서 `InternalAPIClient`를 사용하고 있지만 파일 상단에 import 문이 없다. 런타임에 `NameError`가 발생한다.

```python
# 수정: 파일 상단에 import 추가
from yourapp.clients import InternalAPIClient  # 실제 모듈 경로에 맞게 수정
```

### `OrderService` 함수 내부 import

`OrderDetailView`에서 `from orders.services import OrderService`를 `get_context_data` 메서드 내부에서 수행하고 있다. 순환 import를 회피하기 위한 의도적 패턴일 수 있지만, 순환 의존이 없다면 파일 상단으로 이동하는 것이 표준적이다.

```python
# 권장: 파일 상단으로 이동
from orders.services import OrderService
```

---

## 2. 성능 문제 -- DashboardView의 직렬 API 호출

`DashboardView.get_context_data`에서 3개의 API 호출(`revenue`, `orders`, `notifications`)이 순차적으로 실행된다. 각 호출이 네트워크 I/O를 수반하므로, 총 응답 시간은 세 호출의 합산이 된다.

### 권장 개선안

**방안 A -- `concurrent.futures`를 사용한 병렬 호출:**

```python
from concurrent.futures import ThreadPoolExecutor

def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    api = InternalAPIClient(self.request)

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_revenue = executor.submit(api.get, "stats/revenue/")
        future_orders = executor.submit(api.get, "orders/recent/")
        future_notifications = executor.submit(api.get, "notifications/")

    ctx["revenue"] = future_revenue.result()
    ctx["orders"] = future_orders.result()
    ctx["notifications"] = future_notifications.result()
    return ctx
```

**방안 B -- Django 비동기 뷰 (Django 4.1+):**

비동기 뷰로 전환하고 `asyncio.gather`를 사용하면 더 자연스러운 병렬 처리가 가능하다. 단, `InternalAPIClient`가 async를 지원해야 한다.

---

## 3. 에러 처리 부재

두 뷰 모두 외부 서비스 호출에 대한 예외 처리가 없다. API 서버 장애, 타임아웃, 잘못된 응답 등이 발생하면 500 에러가 사용자에게 그대로 노출된다.

### 권장 개선안

```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    api = InternalAPIClient(self.request)

    try:
        ctx["revenue"] = api.get("stats/revenue/")
    except Exception:
        ctx["revenue"] = None  # 또는 기본값, 로깅 추가

    try:
        ctx["orders"] = api.get("orders/recent/")
    except Exception:
        ctx["orders"] = []

    try:
        ctx["notifications"] = api.get("notifications/")
    except Exception:
        ctx["notifications"] = []

    return ctx
```

- 대시보드처럼 여러 독립 데이터를 모아 보여주는 화면은 부분 실패를 허용하는 것이 사용자 경험상 유리하다.
- `OrderDetailView`의 경우 핵심 데이터 조회 실패 시 `Http404` 또는 적절한 에러 페이지로 전환하는 것이 맞다.

---

## 4. 인증/권한 처리 누락

두 뷰 모두 `LoginRequiredMixin` 등의 접근 제어가 없다. 대시보드와 주문 상세 페이지는 일반적으로 인증된 사용자만 접근해야 한다.

### 권장 개선안

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, TemplateView):
    ...

class OrderDetailView(LoginRequiredMixin, TemplateView):
    ...
```

- `LoginRequiredMixin`은 MRO(Method Resolution Order) 상 `TemplateView`보다 앞에 위치해야 한다.
- 필요에 따라 `PermissionRequiredMixin` 또는 `UserPassesTestMixin`도 고려한다.

---

## 5. 뷰 클래스 선택 검토

### `OrderDetailView` -- `DetailView` 고려

`OrderDetailView`는 단일 객체(주문)의 상세 정보를 보여주는 패턴이다. 현재 `TemplateView`를 사용하고 서비스 레이어에서 직접 데이터를 가져오고 있는데, 만약 `Order`가 Django 모델이라면 `DetailView`가 더 관용적이다.

```python
from django.views.generic import DetailView
from orders.models import Order

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    pk_url_kwarg = "order_id"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["history"] = OrderService.get_history(self.object.pk)
        return ctx
```

다만, 서비스 레이어 패턴을 의도적으로 사용하는 아키텍처라면 현재 구조를 유지하되 위의 다른 개선 사항들을 적용하면 된다.

---

## 6. 기타 개선 사항

| 항목 | 현재 | 권장 |
|------|------|------|
| `order_id` 검증 | `self.kwargs["order_id"]` -- 존재하지 않는 ID에 대한 처리 없음 | `get_object_or_404` 패턴 또는 서비스 레이어에서 `ObjectDoesNotExist` 처리 |
| 캐싱 | 없음 | 대시보드 통계 데이터는 `django.views.decorators.cache` 또는 `cache_page` 적용 고려 |
| 타임아웃 | `InternalAPIClient`의 타임아웃 설정 확인 불가 | 클라이언트 레벨에서 적절한 타임아웃(예: 5초) 설정 필수 |
| 테스트 용이성 | `InternalAPIClient`를 메서드 내부에서 직접 생성 | 의존성 주입 또는 팩토리 패턴으로 변경하면 mock 테스트가 용이 |

---

## 요약

| 심각도 | 항목 | 설명 |
|--------|------|------|
| **Critical** | import 누락 | `InternalAPIClient` import가 없어 `NameError` 발생 |
| **High** | 인증 미적용 | `LoginRequiredMixin` 누락으로 비인증 사용자 접근 가능 |
| **High** | 에러 처리 부재 | 외부 서비스 장애 시 500 에러 직접 노출 |
| **Medium** | 직렬 API 호출 | 3건의 순차 호출로 인한 응답 지연 |
| **Low** | 함수 내부 import | 순환 참조가 아니라면 파일 상단으로 이동 |
| **Low** | 뷰 클래스 선택 | `OrderDetailView`에 `DetailView` 사용 검토 |
| **Low** | 캐싱/타임아웃 | 대시보드 데이터 캐싱 및 API 타임아웃 설정 고려 |
