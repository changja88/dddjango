# B02: TemplateView 코드 리뷰 (implementation-django 스킬)

**Skill:** implementation-django (Review mode)
**Code under review:**
```python
class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'
    def get_context_data:
        context['orders'] = Order.objects.filter(
            user=self.request.user
        ).select_related('product')[:20]
```

## [주요 내용]

### 리뷰: 잘된 점

- `select_related('product')`로 ForeignKey N+1 방지
- `[:20]`으로 결과 수 제한하여 성능 관리
- `TemplateView` 사용으로 CBV 패턴 준수

### 리뷰: 개선 사항

[Convention: LoginRequiredMixin 누락] -- 대시보드는 인증된 사용자만 접근해야 한다. `LoginRequiredMixin`이 MRO에서 `TemplateView` 앞에 위치해야 한다.

[Convention: get_context_data 시그니처 오류] -- `def get_context_data`에 `(self, **kwargs)` 파라미터와 `super().get_context_data(**kwargs)` 호출이 누락되었다.

[Convention: 에러 처리 누락] -- `get_context_data`에서 외부 서비스/DB 호출 시 예외 처리가 없다. 쿼리 실패 시 500 에러 대신 사용자에게 의미 있는 메시지를 보여야 한다.

[Convention: 서비스 레이어 미사용] -- 뷰에서 직접 QuerySet을 호출하고 있다. 비즈니스 로직이 복잡해지면 서비스 레이어나 셀렉터로 추출해야 한다.

### 개선된 코드

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx["orders"] = (
                Order.objects
                .filter(user=self.request.user)
                .select_related("product")
                .order_by("-created_at")[:20]
            )
        except Exception:
            ctx["orders"] = []
            ctx["error_message"] = "주문 데이터를 불러올 수 없습니다."
        return ctx
```

---
> **관련 스킬 참조:**
> - [TemplateView, 접근 제어, context processor] → **implementation-django-web** 스킬
> - [QuerySet select_related/prefetch_related] → 이 스킬 `references/queryset-manager.md`
> - [서비스 레이어 추출 기준] → 이 스킬 `references/service-layer.md`
