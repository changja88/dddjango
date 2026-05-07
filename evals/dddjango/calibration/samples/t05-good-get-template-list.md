# Django 주문 목록 페이지 파일 설계

GET 기반 주문 목록 페이지입니다. JavaScript 데이터 주입이나 상태 변경 form이 없으므로
json_script와 CSRF는 필수 구현이 아니라 검토 항목입니다.

```python
class OrderListView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = order_list_for_user(user=self.request.user)
        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        context.update({"orders": page_obj.object_list, "page_obj": page_obj})
        return context
```

```python
def order_list_for_user(*, user):
    return (
        Order.objects
        .filter(user=user)
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
```

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block head_extra %}
  <link rel="stylesheet" href="{% static 'orders/css/order-list.css' %}">
{% endblock head_extra %}

{% block body %}
  {% include "orders/_filters.html" with q=q only %}
  {% include "orders/_table.html" with orders=orders only %}
{% endblock body %}
```

검증은 로그인 리다이렉트, 사용자별 조회 제한, pagination, N+1 쿼리 회귀, 템플릿 include only를 테스트한다.
