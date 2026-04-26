# d06-django-web: Django -> Django Web 위임 테스트

## 질문

"Django 모델은 다 만들었는데, 이제 관리자용 웹 페이지를 템플릿으로 만들고 싶어. 정적 파일이랑 디자인 시스템은 어떻게 구성해?"

## 트리거 스킬

`implementation-django` -> 웹 페이지(템플릿, 정적 파일, 디자인 시스템)는 `implementation-django-web`에 위임

## 응답 (Writing 모드)

관리자용 웹 페이지의 템플릿 구조, 정적 파일 설정, 디자인 시스템 구성을 아래에 정리한다.

### 1. 프로젝트 구조

템플릿과 정적 파일의 전체 배치부터 잡는다. `web/` 폴더를 프레젠테이션 계층으로 분리하고, 디자인 시스템 컴포넌트는 `design_system/`에서 관리한다.

```
repository_root/
├── config/
│   └── settings/
│       ├── base.py
│       ├── local.py
│       └── production.py
├── apps/
│   └── admin_panel/              # 관리자 도메인 앱 (모델, 서비스)
│       ├── models.py
│       ├── services.py
│       └── selectors.py
├── web/
│   ├── views/
│   │   └── admin_panel/
│   │       ├── __init__.py
│   │       └── views.py
│   ├── view_urls.py
│   └── templates/
│       ├── base.html                         # 1단계: 사이트 전체 레이아웃
│       ├── base_admin.html                   # 2단계: 관리자 섹션 레이아웃
│       ├── admin_panel/
│       │   ├── dashboard/
│       │   │   ├── dashboard.html            # 3단계: 개별 페이지
│       │   │   └── dashboard-scripts.html
│       │   └── user_list/
│       │       └── user_list.html
│       └── design_system/
│           ├── buttons/
│           │   ├── _btn_primary.html
│           │   └── btn-primary.css
│           ├── cards/
│           │   ├── _stat_card.html
│           │   └── stat-card.css
│           ├── navigation/
│           │   └── _navbar.html
│           ├── data-display/
│           │   ├── _data_table.html
│           │   └── data-table.css
│           ├── forms/
│           │   └── _search_input.html
│           └── layout/
│               └── _footer.html
├── static/                                   # STATICFILES_DIRS에 등록
│   ├── css/
│   │   └── tokens.css                        # 디자인 토큰
│   ├── js/
│   │   └── components.js                     # 공유 JS 컴포넌트
│   └── images/
│       └── logo.svg
└── apps/admin_panel/
    └── static/
        └── admin_panel/                      # 앱별 네임스페이싱
            ├── css/
            │   └── dashboard.css
            └── js/
                └── chart.js
```

### 2. 정적 파일 설정

```python
# config/settings/base.py
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    # ...
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
```

```python
# config/settings/production.py
from .base import *  # noqa: F401,F403

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

- `ManifestStaticFilesStorage` 또는 WhiteNoise의 `CompressedManifestStaticFilesStorage`로 캐시 버스팅을 자동화한다
- 앱별 정적 파일은 `admin_panel/static/admin_panel/`처럼 네임스페이싱하여 파일명 충돌을 방지한다
- 프로덕션 배포 전 `python manage.py collectstatic`을 실행한다

### 3. 베이스 템플릿 (3-tier 상속)

```htmldjango
{# base.html -- 사이트 전체 레이아웃 #}
{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <title>{% block title %}서비스명{% endblock title %}</title>
    <meta name="description" content="{% block meta_description %}서비스 설명{% endblock meta_description %}">
    {% block head_extra %}{% endblock head_extra %}
    <link rel="stylesheet" href="{% static 'css/tokens.css' %}">
</head>
<body>
    {% block navbar %}{% include "design_system/navigation/_navbar.html" %}{% endblock navbar %}
    {% block body %}{% endblock body %}
    {% block footer %}{% include "design_system/layout/_footer.html" %}{% endblock footer %}
    <script src="{% static 'js/components.js' %}"></script>
    {% block scripts %}{% endblock scripts %}
</body>
</html>
```

```htmldjango
{# base_admin.html -- 관리자 섹션 공통 #}
{% extends "base.html" %}
{% load static %}

{% block title %}관리자 | {{ block.super }}{% endblock title %}

{% block body %}
<div class="admin-layout">
    <aside class="admin-sidebar">
        {% include "design_system/navigation/_admin_sidebar.html" with nav_items=nav_items only %}
    </aside>
    <main class="admin-content">
        {% block content %}{% endblock content %}
    </main>
</div>
{% endblock body %}
```

```htmldjango
{# admin_panel/dashboard/dashboard.html -- 개별 페이지 #}
{% extends "base_admin.html" %}
{% load static %}

{% block title %}대시보드 | {{ block.super }}{% endblock title %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'admin_panel/css/dashboard.css' %}">
{% endblock head_extra %}

{% block content %}
<h1>관리자 대시보드</h1>

<section class="stats-grid">
    {% include "design_system/cards/_stat_card.html" with title="총 사용자" value=total_users only %}
    {% include "design_system/cards/_stat_card.html" with title="신규 가입" value=new_users only %}
    {% include "design_system/cards/_stat_card.html" with title="활성 세션" value=active_sessions only %}
</section>

<section class="recent-users">
    {% include "design_system/data-display/_data_table.html" with headers=table_headers rows=recent_users only %}
</section>
{% endblock content %}

{% block scripts %}
    {{ block.super }}
    {% include "admin_panel/dashboard/dashboard-scripts.html" %}
{% endblock scripts %}
```

```htmldjango
{# admin_panel/dashboard/dashboard-scripts.html #}
{% load static %}

{# Chart.js -- 대시보드 차트 렌더링 #}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>

{# 서버 -> JS 데이터 전달: 가입 추이 #}
{{ signup_trend|json_script:"signup-trend" }}

{# 대시보드 차트 초기화 #}
<script src="{% static 'admin_panel/js/chart.js' %}"></script>
```

### 4. 디자인 토큰 (3계층)

```css
/* static/css/tokens.css */

/* 1계층: Primitive -- 원시 값 */
:root {
    --blue-500: #3b82f6;
    --blue-700: #1d4ed8;
    --gray-100: #f3f4f6;
    --gray-500: #6b7280;
    --gray-900: #1f2937;
    --red-500: #ef4444;
    --green-500: #22c55e;
}

/* 2계층: Semantic -- 역할 기반 별칭 */
:root {
    --color-primary: var(--blue-500);
    --color-primary-hover: var(--blue-700);
    --color-text: var(--gray-900);
    --color-text-muted: var(--gray-500);
    --color-bg: #ffffff;
    --color-bg-subtle: var(--gray-100);
    --color-border: #e5e7eb;
    --color-danger: var(--red-500);
    --color-success: var(--green-500);

    --font-sans: 'Inter', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;

    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);

    --color-focus-ring: #2563eb;
    --focus-ring: 0 0 0 3px var(--color-focus-ring);
    --transition-duration: 200ms;
}

/* 3계층: Component -- 컴포넌트 전용 */
:root {
    --btn-bg: var(--color-primary);
    --btn-bg-hover: var(--color-primary-hover);
    --btn-text: #ffffff;
    --card-border: var(--color-border);
    --card-radius: var(--radius-md);
    --table-header-bg: var(--color-bg-subtle);
    --sidebar-bg: var(--gray-900);
    --sidebar-text: #ffffff;
}

/* 다크 모드 -- semantic 토큰만 재정의 */
[data-theme="dark"] {
    --color-primary: #60a5fa;
    --color-text: #f9fafb;
    --color-text-muted: #9ca3af;
    --color-bg: #111827;
    --color-bg-subtle: #1f2937;
    --color-border: #374151;
}

/* 시스템 설정 감지 */
@media (prefers-color-scheme: dark) {
    :root:not([data-theme]) {
        --color-primary: #60a5fa;
        --color-text: #f9fafb;
        --color-bg: #111827;
        --color-border: #374151;
    }
}

/* 모션 감소 선호 사용자 */
@media (prefers-reduced-motion: reduce) {
    :root {
        --transition-duration: 0ms;
    }
}
```

### 5. 디자인 시스템 컴포넌트 예시

```htmldjango
{# design_system/cards/_stat_card.html #}
{# 필수 변수: title (str), value (int|str) #}
<div class="stat-card">
    <span class="stat-card__title">{{ title }}</span>
    <span class="stat-card__value">{{ value }}</span>
</div>
```

```css
/* design_system/cards/stat-card.css */
.stat-card {
    display: flex;
    flex-direction: column;
    padding: var(--spacing-lg, 1.5rem);
    border: 1px solid var(--card-border, #e5e7eb);
    border-radius: var(--card-radius, 0.5rem);
    background: var(--color-bg, #ffffff);
    box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.stat-card__title {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
}

.stat-card__value {
    font-size: var(--text-lg, 1.125rem);
    font-weight: 600;
    color: var(--color-text, #1f2937);
}
```

```htmldjango
{# design_system/data-display/_data_table.html #}
{# 필수 변수: headers (list[str]), rows (list[dict]) #}
<table class="data-table">
    <thead>
        <tr>
            {% for header in headers %}
                <th>{{ header }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in rows %}
            <tr>
                {% for value in row.values %}
                    <td>{{ value }}</td>
                {% endfor %}
            </tr>
        {% endfor %}
    </tbody>
</table>
```

### 6. 뷰 레이어

```python
# web/views/admin_panel/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView

from apps.admin_panel.selectors import UserSelector


class AdminDashboardView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    TemplateView,
):
    template_name = "admin_panel/dashboard/dashboard.html"
    permission_required = "admin_panel.view_dashboard"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_users"] = UserSelector.count_all()
        ctx["new_users"] = UserSelector.count_recent(days=7)
        ctx["active_sessions"] = UserSelector.count_active_sessions()
        ctx["recent_users"] = UserSelector.get_recent(limit=10)
        ctx["signup_trend"] = UserSelector.get_signup_trend(days=30)
        ctx["table_headers"] = ["이름", "이메일", "가입일", "상태"]
        return ctx
```

```python
# web/view_urls.py
from django.urls import path

from web.views.admin_panel.views import AdminDashboardView

app_name = "web"

urlpatterns = [
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
```

### 7. 핵심 규칙 요약

| 항목 | 규칙 |
|------|------|
| 정적 파일 경로 | `{% static %}` 태그만 사용, 하드코딩 금지 |
| 앱별 정적 파일 | `myapp/static/myapp/` 네임스페이싱 |
| 캐시 버스팅 | `ManifestStaticFilesStorage` 또는 WhiteNoise |
| 디자인 토큰 | CSS Custom Properties 3계층(primitive -> semantic -> component) |
| 색상/간격 값 | `var()` + 폴백 값 사용, 하드코딩 금지 |
| 컴포넌트 사용 | `{% include "..." with var=val only %}` |
| 서버 데이터 전달 | `json_script` 필터 (XSS-safe) |
| CDN 스크립트 | `integrity` + `crossorigin` SRI 속성 필수 |
| 인라인 스크립트/스타일 | 별도 파일로 분리 (예외는 사유 명시) |
| 다크 모드 | `[data-theme="dark"]` + `prefers-color-scheme` |
| 접근성 | 포커스 링, 대비 4.5:1, 모션 감소 대응 |
| 접근 제어 | `LoginRequiredMixin` + `PermissionRequiredMixin` (MRO 순서 준수) |

---
> **관련 스킬 참조:**
> - 모델 설계, QuerySet 최적화, 서비스 레이어 패턴 -> **implementation-django** 스킬
> - API 엔드포인트를 함께 제공해야 하는 경우 -> **implementation-django-ninja** 스킬
> - Python 타입 힌트, dataclasses 컨벤션 -> **implementation-python** 스킬
> - 네이밍, SOLID 원칙 등 언어 비종속 클린코드 -> **implementation-cleancode** 스킬
> - 헥사고날 아키텍처, CQRS 패턴 적용 -> **architecture-implementation-patterns** 스킬
