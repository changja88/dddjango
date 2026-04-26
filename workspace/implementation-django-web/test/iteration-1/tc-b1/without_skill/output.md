# Django Template Code Review: `orders/order_list.html`

## 1. `{% load static %}` 누락 (BUG)

`{% static %}` 태그를 사용하고 있으나 템플릿 상단에 `{% load static %}` 선언이 없다. 이 상태로 렌더링하면 `TemplateSyntaxError`가 발생한다.

```htmldjango
{% extends "base_orders.html" %}
{% load static %}
```

`{% extends %}` 바로 아래에 `{% load static %}`을 추가해야 한다. 단, `base_orders.html`에서 이미 로드했더라도 Django 템플릿 상속에서 `{% load %}`는 자식 템플릿에 전파되지 않으므로 반드시 각 템플릿에서 개별 선언이 필요하다.

---

## 2. XSS 취약점 — `{{ orders_json }}` (SECURITY)

`{{ orders_json }}`이 `<script>` 블록 안에서 이스케이프 없이 직접 출력되고 있다. Django의 기본 자동 이스케이프는 HTML 컨텍스트용이며, JavaScript 컨텍스트에서는 XSS를 방지하지 못한다.

주문 데이터에 공격자가 제어할 수 있는 문자열(예: 주문 메모, 고객 이름)이 포함되어 있다면, `</script><script>alert('xss')</script>` 같은 페이로드로 스크립트 삽입이 가능하다.

**수정 방법:** Django의 `json_script` 필터를 사용한다.

```htmldjango
{{ orders_json|json_script:"orders-data" }}
<script>
    const orders = JSON.parse(document.getElementById('orders-data').textContent);
</script>
```

`json_script` 필터는 `<`, `>`, `&` 등의 문자를 유니코드 이스케이프로 변환하여 XSS를 방지한다.

---

## 3. CSRF 토큰 누락 (SECURITY)

`fetch`로 POST 요청을 보내면서 CSRF 토큰을 포함하지 않고 있다. Django의 `CsrfViewMiddleware`가 활성화되어 있다면 이 요청은 403 Forbidden으로 거부된다.

```javascript
fetch('/api/orders/reorder/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')  // 추가 필요
    },
    body: JSON.stringify({ order: orders.map(o => o.id) })
});
```

CSRF 토큰을 쿠키에서 읽는 헬퍼 함수가 필요하다.

```javascript
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
```

또는 템플릿에서 `{% csrf_token %}`을 렌더링한 뒤 해당 hidden input의 값을 참조하는 방법도 있다.

---

## 4. SortableJS `onEnd` 콜백의 로직 오류 (BUG)

현재 코드에서 `orders`는 페이지 로드 시점에 `{{ orders_json }}`으로 할당된 정적 배열이다. 사용자가 드래그 앤 드롭으로 순서를 변경해도 이 `orders` 배열은 갱신되지 않는다. 따라서 `orders.map(o => o.id)`는 항상 원래 순서의 ID 배열을 전송하게 되어 재정렬이 실제로 반영되지 않는다.

**수정 방법:** DOM의 현재 순서를 기반으로 ID를 추출해야 한다.

```javascript
onEnd: function(evt) {
    const items = container.querySelectorAll('[data-order-id]');
    const orderedIds = Array.from(items).map(el => el.dataset.orderId);
    fetch('/api/orders/reorder/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ order: orderedIds })
    });
}
```

이를 위해 `order_card.html`의 루트 요소에 `data-order-id="{{ order.id }}"` 속성이 있어야 한다.

---

## 5. 빈 목록 처리 누락 (UX)

`orders`가 빈 QuerySet일 때 `{% for %}` 루프가 아무것도 렌더링하지 않아 사용자에게 빈 페이지가 보인다. `{% empty %}` 태그로 안내 메시지를 제공해야 한다.

```htmldjango
{% for order in orders %}
    {% include "orders/order_card/order_card.html" with order=order %}
{% empty %}
    <p>주문이 없습니다.</p>
{% endfor %}
```

---

## 6. 외부 CDN 스크립트의 무결성 검증 부재 (SECURITY)

SortableJS를 CDN에서 로드하면서 `integrity` 속성과 `crossorigin` 속성이 없다. CDN이 침해당하면 악성 스크립트가 삽입될 수 있다.

```html
<script
    src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"
    integrity="sha384-..."
    crossorigin="anonymous">
</script>
```

또는 SortableJS를 프로젝트의 `static` 디렉토리에 포함시켜 CDN 의존성을 제거하는 방법을 고려한다.

---

## 7. fetch 에러 처리 누락 (RELIABILITY)

`fetch` 호출의 응답을 확인하지 않고 있다. 네트워크 오류나 서버 에러 발생 시 사용자에게 아무런 피드백이 없다.

```javascript
fetch('/api/orders/reorder/', { ... })
    .then(response => {
        if (!response.ok) {
            throw new Error('서버 오류: ' + response.status);
        }
        return response.json();
    })
    .catch(error => {
        console.error('재정렬 실패:', error);
        // 사용자에게 에러 알림 또는 원래 순서로 복원
    });
```

---

## 8. `<h1>` 태그가 Sortable 컨테이너 내부에 위치 (BUG)

`container`가 `.order-list` div를 가리키는데, 이 div 안에 `<h1>` 태그가 포함되어 있다. SortableJS는 컨테이너의 모든 직접 자식 요소를 드래그 가능한 항목으로 취급하므로, `<h1>` 태그도 드래그 대상이 된다.

**수정 방법:** SortableJS의 `draggable` 옵션으로 드래그 대상을 제한하거나, 구조를 변경한다.

```javascript
new Sortable(container, {
    animation: 150,
    draggable: '.order-card',  // order_card의 루트 클래스에 맞게 지정
    onEnd: function(evt) { ... }
});
```

---

## 요약

| # | 유형 | 심각도 | 항목 |
|---|------|--------|------|
| 1 | BUG | High | `{% load static %}` 누락 - 렌더링 실패 |
| 2 | SECURITY | Critical | `{{ orders_json }}` XSS 취약점 |
| 3 | SECURITY | High | CSRF 토큰 누락 - POST 요청 거부 |
| 4 | BUG | High | 드래그 후에도 원래 순서가 전송되는 로직 오류 |
| 5 | UX | Low | 빈 주문 목록에 대한 안내 없음 |
| 6 | SECURITY | Medium | CDN 스크립트 무결성 검증 없음 |
| 7 | RELIABILITY | Medium | fetch 에러 처리 없음 |
| 8 | BUG | Medium | `<h1>`이 드래그 대상에 포함됨 |
