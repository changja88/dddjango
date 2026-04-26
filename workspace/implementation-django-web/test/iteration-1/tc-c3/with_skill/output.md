# Refactoring: NotificationView + Template

---

## 1. `{{ value }}` in `<script>` -> `json_script` filter

[Before]
```htmldjango
<button onclick="markRead({{ notif.id }})">읽음</button>
```

[After]
```htmldjango
<div class="notif-item"
     id="notif-{{ notif.id }}"
     data-notif-id="{{ notif.id }}">
    <p>{{ notif.message }}</p>
    <button class="js-mark-read">읽음</button>
</div>
```

[Reason] `json_script` / XSS-safe data transfer -- `{{ notif.id }}` 를 `<script>` 컨텍스트(`onclick` 핸들러)에 직접 삽입하면 XSS 위험이 있다. `data-*` 속성으로 이동하고 JS에서 `dataset`으로 읽으면 브라우저가 HTML 속성으로 이스케이프 처리한다. 복수 항목이므로 개별 `json_script` 대신 `data-*` 속성이 더 적합하고, 인라인 이벤트 핸들러도 제거된다.

---

## 2. Inline `onclick` handler -> Event delegation

[Before]
```htmldjango
<button onclick="markRead({{ notif.id }})">읽음</button>
```

[After]
```javascript
document.getElementById('notification-list')
    .addEventListener('click', function(e) {
        const btn = e.target.closest('.js-mark-read');
        if (!btn) return;
        const item = btn.closest('.notif-item');
        markRead(item.dataset.notifId);
    });
```

[Reason] Inline event handler removal -- 인라인 `onclick`은 HTML과 JS 로직을 결합하고, CSP `script-src` 정책 위반을 유발한다. 이벤트 위임(event delegation)으로 전환하면 관심사 분리가 이루어지고, 동적으로 추가되는 알림 항목에도 자동 대응된다.

---

## 3. AJAX without CSRF -> ADD `X-CSRFToken` header

[Before]
```javascript
fetch('/api/notifications/' + notifId + '/read/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' }
})
```

[After]
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

fetch('/api/notifications/' + notifId + '/read/', {
    method: 'PATCH',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
    },
    mode: 'same-origin',
})
```

[Reason] CSRF protection -- Django는 POST/PUT/PATCH/DELETE 요청에 CSRF 토큰을 요구한다. `X-CSRFToken` 헤더가 없으면 Django가 403 Forbidden을 반환한다. `mode: "same-origin"`도 추가하여 CORS 정책을 명시한다. (Django 공식 문서 권장 `getCookie` 구현 사용)

---

## 4. Inline app `<script>` -> EXTRACT to `static/` JS file

[Before]
```htmldjango
<script>
function markRead(notifId) {
    fetch('/api/notifications/' + notifId + '/read/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('notif-' + notifId).style.opacity = '0.5';
    });
}
</script>
```

[After]
```
notifications/
└── static/
    └── notifications/
        └── js/
            └── notifications.js    # 앱 스크립트 (분리)
```

```javascript
// notifications/static/notifications/js/notifications.js

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

function markRead(notifId) {
    fetch('/api/notifications/' + notifId + '/read/', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
    })
    .then(function(response) {
        if (!response.ok) throw new Error('Request failed');
        return response.json();
    })
    .then(function() {
        var item = document.getElementById('notif-' + notifId);
        if (item) item.style.opacity = '0.5';
    })
    .catch(function(err) {
        console.error('Failed to mark notification as read:', err);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var list = document.getElementById('notification-list');
    if (!list) return;

    list.addEventListener('click', function(e) {
        var btn = e.target.closest('.js-mark-read');
        if (!btn) return;
        var item = btn.closest('.notif-item');
        if (item && item.dataset.notifId) {
            markRead(item.dataset.notifId);
        }
    });
});
```

[Reason] Inline script extraction -- 스킬 규칙: "HTML 컴포넌트에 앱 로직을 인라인 `<script>`로 작성하지 않는다." 별도 JS 파일로 분리하면 CSP 호환성, 브라우저 캐싱, 테스트 용이성이 향상된다. 앱별 네임스페이싱(`notifications/static/notifications/js/`)으로 파일명 충돌도 방지된다. 에러 핸들링(`.catch`)과 응답 상태 검증(`response.ok`)도 추가하였다.

---

## 5. Missing `{% load static %}` in child template

[Before]
```htmldjango
{% extends "base.html" %}
{% block body %}
...
{% endblock %}
```

[After]
```htmldjango
{% extends "base.html" %}
{% load static %}
...
```

[Reason] `{% load %}` inheritance -- `{% load %}` 태그는 부모 템플릿에서 자식으로 상속되지 않는다. `{% static %}` 태그를 사용하려면 자식 템플릿에서 별도로 `{% load static %}`을 선언해야 한다.

---

## 6. No `{% block %}` name in closing `{% endblock %}` tag

[Before]
```htmldjango
{% block body %}
...
{% endblock %}
```

[After]
```htmldjango
{% block body %}
...
{% endblock body %}
```

[Reason] Block name in `endblock` -- `{% endblock body %}`처럼 닫는 태그에 블록명을 명시하면 중첩된 블록 구조에서 가독성이 향상된다.

---

## 7. No access control -> ADD `LoginRequiredMixin`

[Before]
```python
from django.views.generic import TemplateView

class NotificationView(TemplateView):
    template_name = "notifications/notifications.html"
```

[After]
```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class NotificationView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/notifications.html"
```

[Reason] Access control -- 알림은 인증된 사용자의 데이터이다(`self.request.user`를 사용하고 있음). `LoginRequiredMixin`이 없으면 미인증 사용자가 접근 시 `AnonymousUser` 관련 에러가 발생하거나 데이터가 노출될 수 있다. MRO 순서에 따라 `LoginRequiredMixin`을 `TemplateView` 앞에 배치한다.

---

## 8. No error handling in view -> ADD try/except for service call

[Before]
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    from notifications.services import NotificationService
    ctx["notifications"] = NotificationService.get_unread(self.request.user)
    return ctx
```

[After]
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    try:
        ctx["notifications"] = NotificationService.get_unread(self.request.user)
    except Exception:
        ctx["notifications"] = []
        ctx["error_message"] = "알림을 불러올 수 없습니다."
    return ctx
```

[Reason] Error handling -- 서비스 호출이 실패할 경우(DB 장애, 네트워크 오류 등) 500 에러 대신 빈 목록과 사용자 친화적 에러 메시지를 표시한다. import도 모듈 상단으로 이동하여 표준 Python 관행을 따른다.

---

## 9. Import inside method -> Move to module top-level

[Before]
```python
def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    from notifications.services import NotificationService
    ...
```

[After]
```python
from notifications.services import NotificationService

class NotificationView(LoginRequiredMixin, TemplateView):
    ...
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ...
```

[Reason] Top-level imports -- PEP 8: "Imports are always put at the top of the file." 메서드 내부 import는 순환 참조 회피 시에만 사용하고, 일반적인 경우 모듈 상단에 배치한다.

---

## 10. Raw `fetch()` AJAX -> CONSIDER HTMX for HTML fragment updates

[Before]
```javascript
fetch('/api/notifications/' + notifId + '/read/', {
    method: 'PATCH',
    ...
})
.then(response => response.json())
.then(data => {
    document.getElementById('notif-' + notifId).style.opacity = '0.5';
});
```

[After -- HTMX alternative]
```htmldjango
<div class="notif-item" id="notif-{{ notif.id }}">
    <p>{{ notif.message }}</p>
    <button hx-patch="{% url 'notifications:mark-read' notif.id %}"
            hx-target="#notif-{{ notif.id }}"
            hx-swap="outerHTML">
        읽음
    </button>
</div>
```

[Reason] HTMX consideration -- 현재 "읽음" 처리는 단순 DOM 상태 변경이므로 HTMX로 전환하면 JavaScript를 완전히 제거할 수 있다. 서버가 읽음 처리된 알림의 HTML 조각을 반환하면 HTMX가 자동으로 DOM을 교체한다. 다만, 이는 서버 측 엔드포인트 변경(JSON -> HTML 조각 반환)이 필요하므로 참고 사항으로 제시한다.

---

## Complete Refactored Code

### views.py

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from notifications.services import NotificationService


class NotificationView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/notifications.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx["notifications"] = NotificationService.get_unread(self.request.user)
        except Exception:
            ctx["notifications"] = []
            ctx["error_message"] = "알림을 불러올 수 없습니다."
        return ctx
```

### notifications/notifications.html

```htmldjango
{# notifications/notifications.html #}
{% extends "base.html" %}
{% load static %}

{% block body %}
<div id="notification-list">
    {% if error_message %}
    <p class="error-message">{{ error_message }}</p>
    {% endif %}

    {% for notif in notifications %}
    <div class="notif-item" id="notif-{{ notif.id }}" data-notif-id="{{ notif.id }}">
        <p>{{ notif.message }}</p>
        <button class="js-mark-read">읽음</button>
    </div>
    {% empty %}
    <p>새로운 알림이 없습니다.</p>
    {% endfor %}
</div>
{% endblock body %}

{% block scripts %}
{{ block.super }}
{# 알림 읽음 처리 스크립트 #}
<script src="{% static 'notifications/js/notifications.js' %}"></script>
{% endblock scripts %}
```

### notifications/static/notifications/js/notifications.js

```javascript
// notifications/static/notifications/js/notifications.js

/**
 * CSRF 토큰을 쿠키에서 읽어오는 헬퍼 (Django 공식 문서 권장 구현).
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 알림을 읽음 처리하고 UI를 업데이트한다.
 */
function markRead(notifId) {
    fetch('/api/notifications/' + notifId + '/read/', {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
    })
    .then(function(response) {
        if (!response.ok) throw new Error('Request failed');
        return response.json();
    })
    .then(function() {
        var item = document.getElementById('notif-' + notifId);
        if (item) item.style.opacity = '0.5';
    })
    .catch(function(err) {
        console.error('Failed to mark notification as read:', err);
    });
}

/**
 * 이벤트 위임으로 읽음 버튼 클릭을 처리한다.
 */
document.addEventListener('DOMContentLoaded', function() {
    var list = document.getElementById('notification-list');
    if (!list) return;

    list.addEventListener('click', function(e) {
        var btn = e.target.closest('.js-mark-read');
        if (!btn) return;
        var item = btn.closest('.notif-item');
        if (item && item.dataset.notifId) {
            markRead(item.dataset.notifId);
        }
    });
});
```

### File Structure

```
notifications/
├── static/
│   └── notifications/
│       └── js/
│           └── notifications.js       # 앱 스크립트 (CSRF + 이벤트 위임)
├── templates/
│   └── notifications/
│       └── notifications.html         # 페이지 템플릿
├── services.py                        # NotificationService
└── views.py                           # NotificationView
```

---

## Refactoring Checklist

| # | 항목 | 적용 |
|---|------|------|
| 1 | Hardcoded static path -> `{% static %}` | N/A (원본에 정적 경로 없음) |
| 2 | `{{ value }}` in script -> `json_script` / `data-*` | Applied (#1) |
| 3 | CDN without SRI -> ADD SRI | N/A (CDN 사용 없음) |
| 4 | AJAX without CSRF -> ADD `X-CSRFToken` | Applied (#3) |
| 5 | `{% include %}` without `only` | N/A (`{% include %}` 미사용) |
| 6 | Hardcoded color/size -> CSS Custom Property | N/A (CSS 미포함) |
| 7 | External component style override | N/A |
| 8 | Inline `<style>` -> separate CSS file | N/A (인라인 스타일 없음) |
| 9 | Inline app `<script>` -> `static/` JS file | Applied (#4) |
| 10 | Missing `{{ block.super }}` | Applied (scripts 블록) |
| 11 | Flat template -> component folders | Partial (단일 페이지이므로 파일 분리까지만) |
| 12 | No access control -> `LoginRequiredMixin` | Applied (#7) |
| 13 | No error handling -> try/except | Applied (#8) |
| 14 | Raw `fetch()` -> CONSIDER HTMX | Noted (#10, 참고 사항으로 제시) |
