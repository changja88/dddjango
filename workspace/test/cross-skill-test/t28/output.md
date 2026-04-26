# T28: 웹 페이지 AJAX용 Django Ninja API Schema와 Router 구현

**Skill:** implementation-django-web (Writing mode)
**Cross-skill references loaded:** implementation-django-ninja (Schema, Router)

## [주요 내용]

웹 페이지에서 AJAX 인터랙션이 필요할 때, JSON 응답은 Django Ninja API로 제공한다. CSRF 토큰 처리가 핵심이다.

### Django Ninja Schema/Router (implementation-django-ninja 위임)

```python
# orders/schemas.py
from ninja import Schema

class OrderStatusOut(Schema):
    id: int
    status: str
    updated_at: datetime

class OrderCompleteIn(Schema):
    note: str = ""
```

```python
# orders/api.py
from ninja import Router
from .schemas import OrderStatusOut, OrderCompleteIn

router = Router(tags=["orders"])

@router.post("/{order_id}/complete", response=OrderStatusOut)
def complete_order(request, order_id: int, payload: OrderCompleteIn):
    order = get_object_or_404(Order, id=order_id)
    order.status = Order.Status.DELIVERED
    order.save(update_fields=["status", "updated_at"])
    return order
```

### 웹 페이지에서 AJAX 호출 (CSRF 필수)

```javascript
// static/js/orders.js
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

fetch(`/api/orders/${orderId}/complete/`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
    },
    mode: "same-origin",
    body: JSON.stringify({ note: "배송 완료 확인" }),
});
```

### 템플릿에서 서버 데이터 전달 (json_script)

```htmldjango
{{ order.id|json_script:"order-id" }}
<script src="{% static 'js/orders.js' %}"></script>
```

---
> **관련 스킬 참조:**
> - [Schema, Router, 인증 패턴] → **implementation-django-ninja** 스킬
> - [CSRF 토큰, SRI, json_script] → 이 스킬 `references/asset-management.md`
> - [REST 상태 코드, 에러 형식] → **architecture-api** 스킬
