# Django Notification View Refactoring

## 1. Original Code Issues

### Python (views.py)
- **Lazy import inside method**: `from notifications.services import NotificationService`가 `get_context_data` 내부에 위치해 있어 매 요청마다 불필요한 import lookup이 발생한다.

### JavaScript / Template
- **Inline onclick handler**: `onclick="markRead({{ notif.id }})"` 방식은 HTML과 JS의 관심사 분리가 안 된다.
- **CSRF 토큰 누락**: Django의 PATCH 요청에 CSRF 토큰을 전송하지 않아 403 에러가 발생할 수 있다.
- **에러 처리 없음**: fetch 실패 시 아무 처리가 없다.
- **Template 내 `<script>` 직접 작성**: 별도 static 파일로 분리하는 것이 유지보수에 유리하다.
- **Template literal 미사용**: 문자열 결합(`'/api/notifications/' + notifId + '/read/'`)이 가독성을 떨어뜨린다.
- **`response.ok` 미확인**: HTTP 4xx/5xx 응답도 `.json()`으로 넘어가 오류를 삼킨다.

---

## 2. Refactored Code

### 2-1. views.py

```python
from django.views.generic import TemplateView

from notifications.services import NotificationService


class NotificationView(TemplateView):
    template_name = "notifications/notifications.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["notifications"] = NotificationService.get_unread(self.request.user)
        return ctx
```

**Changes**:
- import를 모듈 최상위로 이동하여 PEP 8 스타일을 준수하고, 매 요청마다 반복되는 import lookup 비용을 제거했다.

---

### 2-2. notifications.js (static file)

```javascript
// static/notifications/js/notifications.js

document.addEventListener("DOMContentLoaded", () => {
  const csrfToken = document
    .querySelector("[name=csrfmiddlewaretoken]")
    ?.value ?? "";

  document.querySelectorAll("[data-notif-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const notifId = button.dataset.notifId;
      markRead(notifId, csrfToken);
    });
  });
});

async function markRead(notifId, csrfToken) {
  const url = `/api/notifications/${notifId}/read/`;

  try {
    const response = await fetch(url, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    const item = document.getElementById(`notif-${notifId}`);
    if (item) {
      item.classList.add("notif-read");
    }
  } catch (error) {
    console.error(`Failed to mark notification ${notifId} as read:`, error);
  }
}
```

**Changes**:
- **별도 static 파일 분리**: template 내 inline `<script>` 제거.
- **Inline handler 제거**: `onclick` 대신 `data-notif-id` attribute + `addEventListener`로 전환.
- **CSRF 토큰 전송**: `X-CSRFToken` 헤더를 통해 Django CSRF 검증을 통과한다.
- **async/await**: Promise chain 대신 async/await로 가독성 향상.
- **response.ok 확인**: 4xx/5xx 응답 시 명시적으로 에러를 throw한다.
- **try/catch 에러 처리**: 네트워크 오류 및 서버 오류를 catch하여 콘솔에 기록한다.
- **CSS class 사용**: `style.opacity` 직접 조작 대신 `.notif-read` 클래스를 추가하여 스타일 변경을 CSS에 위임한다.
- **Template literal**: 문자열 결합 대신 백틱 template literal을 사용하여 URL을 구성한다.

---

### 2-3. notifications.html (template)

```htmldjango
{# notifications/notifications.html #}
{% extends "base.html" %}
{% load static %}

{% block body %}
{% csrf_token %}

<div id="notification-list">
    {% for notif in notifications %}
    <div class="notif-item" id="notif-{{ notif.id }}">
        <p>{{ notif.message }}</p>
        <button type="button" data-notif-id="{{ notif.id }}">읽음</button>
    </div>
    {% empty %}
    <p>읽지 않은 알림이 없습니다.</p>
    {% endfor %}
</div>

<script src="{% static 'notifications/js/notifications.js' %}"></script>
{% endblock %}
```

**Changes**:
- **`{% load static %}` 추가**: static 파일 참조를 위해 필수.
- **`{% csrf_token %}` 추가**: hidden input으로 CSRF 토큰을 DOM에 렌더링하여 JS에서 읽을 수 있게 한다.
- **`onclick` 제거**: `data-notif-id` data attribute로 대체하여 HTML과 JS의 관심사를 분리했다.
- **`{% empty %}` 추가**: 알림이 없을 때 빈 상태 메시지를 표시한다.
- **`type="button"` 추가**: form 내부에서 의도치 않은 submit을 방지한다.
- **외부 JS 파일 로드**: `<script src="...">` 방식으로 별도 파일에서 로드한다.

---

### 2-4. CSS 추가 (optional)

```css
/* static/notifications/css/notifications.css */

.notif-item {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
    transition: opacity 0.3s ease;
}

.notif-read {
    opacity: 0.5;
    pointer-events: none;
}
```

**Changes**:
- JS에서 직접 `style.opacity`를 조작하던 것을 CSS class(`.notif-read`)로 대체했다.
- `transition`을 추가하여 부드러운 시각적 피드백을 제공한다.
- `pointer-events: none`로 이미 읽은 알림의 버튼 중복 클릭을 방지한다.

---

## 3. Summary

| Area | Before | After |
|------|--------|-------|
| Import 위치 | method 내부 lazy import | 모듈 최상위 |
| JS 위치 | template inline `<script>` | 별도 static 파일 |
| Event binding | `onclick` inline handler | `data-*` attribute + `addEventListener` |
| CSRF | 미전송 (403 위험) | `X-CSRFToken` 헤더 전송 |
| Error handling | 없음 | `response.ok` 확인 + try/catch |
| JS syntax | Promise chain + 문자열 결합 | async/await + template literal |
| Style 변경 | `style.opacity` 직접 조작 | CSS class toggle (`.notif-read`) |
| Empty state | 미처리 | `{% empty %}` 빈 상태 메시지 |
