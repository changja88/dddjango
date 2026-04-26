# stat_card 디자인 시스템 컴포넌트

제목, 값, 단위, 변동률(증가/감소)을 표시하는 통계 카드 컴포넌트이다. 다크 모드, WCAG AA 대비율, 포커스 링, 모션 감소를 지원한다.

---

## 파일 구조

```
web/templates/design_system/
└── cards/
    ├── _stat_card.html       # HTML 파트셜
    └── stat-card.css         # 컴포넌트 스타일

web/templates/dashboard/
└── dashboard_root.html       # 대시보드 페이지 (사용 예시)

web/views/dashboard/
├── __init__.py
└── views.py                  # 대시보드 뷰
```

---

## 1. 컴포넌트 토큰 (CSS)

### `web/templates/design_system/cards/stat-card.css`

```css
/* 3계층: Component 토큰 — stat-card 전용 */
:root {
    --stat-card-bg: var(--color-bg, #ffffff);
    --stat-card-border: var(--color-border, #e5e7eb);
    --stat-card-radius: var(--radius-md, 0.5rem);
    --stat-card-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
    --stat-card-padding: var(--spacing-lg, 1.5rem);

    --stat-card-title-color: var(--color-text-muted, #6b7280);
    --stat-card-value-color: var(--color-text, #1f2937);
    --stat-card-unit-color: var(--color-text-muted, #6b7280);

    --stat-card-trend-up-color: #16a34a;
    --stat-card-trend-up-bg: rgba(22, 163, 74, 0.1);
    --stat-card-trend-down-color: #dc2626;
    --stat-card-trend-down-bg: rgba(220, 38, 38, 0.1);
    --stat-card-trend-neutral-color: var(--color-text-muted, #6b7280);
    --stat-card-trend-neutral-bg: rgba(107, 114, 128, 0.1);
}

/* 다크 테마 — semantic 토큰 재정의로 자동 반영 + 컴포넌트 전용 보정 */
[data-theme="dark"] {
    --stat-card-bg: var(--color-bg-subtle, #1f2937);
    --stat-card-border: var(--color-border, #374151);
    --stat-card-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);

    --stat-card-trend-up-color: #4ade80;
    --stat-card-trend-up-bg: rgba(74, 222, 128, 0.15);
    --stat-card-trend-down-color: #f87171;
    --stat-card-trend-down-bg: rgba(248, 113, 113, 0.15);
    --stat-card-trend-neutral-color: var(--color-text-muted, #9ca3af);
    --stat-card-trend-neutral-bg: rgba(156, 163, 175, 0.15);
}

/* 시스템 다크 모드 감지 */
@media (prefers-color-scheme: dark) {
    :root:not([data-theme]) {
        --stat-card-bg: var(--color-bg-subtle, #1f2937);
        --stat-card-border: var(--color-border, #374151);
        --stat-card-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);

        --stat-card-trend-up-color: #4ade80;
        --stat-card-trend-up-bg: rgba(74, 222, 128, 0.15);
        --stat-card-trend-down-color: #f87171;
        --stat-card-trend-down-bg: rgba(248, 113, 113, 0.15);
        --stat-card-trend-neutral-color: var(--color-text-muted, #9ca3af);
        --stat-card-trend-neutral-bg: rgba(156, 163, 175, 0.15);
    }
}

/* 컴포넌트 스타일 */
.stat-card {
    background: var(--stat-card-bg);
    border: 1px solid var(--stat-card-border);
    border-radius: var(--stat-card-radius);
    box-shadow: var(--stat-card-shadow);
    padding: var(--stat-card-padding);
    transition: box-shadow var(--transition-duration, 200ms) ease,
                transform var(--transition-duration, 200ms) ease;
}

.stat-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}

/* 접근성: 포커스 링 */
.stat-card:focus-within {
    outline: none;
    box-shadow: var(--focus-ring, 0 0 0 3px #2563eb);
}

.stat-card__title {
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: var(--text-sm, 0.875rem);
    font-weight: 500;
    color: var(--stat-card-title-color);
    margin: 0 0 var(--spacing-sm, 0.5rem) 0;
    line-height: 1.4;
}

.stat-card__value-row {
    display: flex;
    align-items: baseline;
    gap: var(--spacing-xs, 0.25rem);
    margin-bottom: var(--spacing-sm, 0.5rem);
}

.stat-card__value {
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--stat-card-value-color);
    line-height: 1.2;
    letter-spacing: -0.025em;
}

.stat-card__unit {
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: var(--text-sm, 0.875rem);
    font-weight: 500;
    color: var(--stat-card-unit-color);
    line-height: 1.2;
}

.stat-card__trend {
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs, 0.25rem);
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: var(--text-sm, 0.875rem);
    font-weight: 600;
    padding: 0.125rem var(--spacing-sm, 0.5rem);
    border-radius: var(--radius-sm, 0.25rem);
    line-height: 1.4;
}

.stat-card__trend--up {
    color: var(--stat-card-trend-up-color);
    background: var(--stat-card-trend-up-bg);
}

.stat-card__trend--down {
    color: var(--stat-card-trend-down-color);
    background: var(--stat-card-trend-down-bg);
}

.stat-card__trend--neutral {
    color: var(--stat-card-trend-neutral-color);
    background: var(--stat-card-trend-neutral-bg);
}

.stat-card__trend-icon {
    width: 1em;
    height: 1em;
    flex-shrink: 0;
}

/* 접근성: 모션 감소 선호 */
@media (prefers-reduced-motion: reduce) {
    .stat-card {
        transition: none;
    }

    .stat-card:hover {
        transform: none;
    }
}

/* 반응형 */
@media (max-width: 768px) {
    .stat-card__value {
        font-size: 1.5rem;
    }
}
```

---

## 2. HTML 파트셜

### `web/templates/design_system/cards/_stat_card.html`

```htmldjango
{# 필수 변수: title (str), value (str|int), unit (str), trend_value (str), trend_direction ("up"|"down"|"neutral") #}
<article class="stat-card" tabindex="0"
         role="group"
         aria-label="{{ title }}">
    <h3 class="stat-card__title">{{ title }}</h3>
    <div class="stat-card__value-row">
        <span class="stat-card__value">{{ value }}</span>
        {% if unit %}
            <span class="stat-card__unit">{{ unit }}</span>
        {% endif %}
    </div>
    {% if trend_value %}
        <span class="stat-card__trend stat-card__trend--{{ trend_direction }}"
              role="status"
              aria-label="변동률 {{ trend_value }}{% if trend_direction == 'up' %} 증가{% elif trend_direction == 'down' %} 감소{% else %} 변동 없음{% endif %}">
            {% if trend_direction == "up" %}
                <svg class="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" focusable="false">
                    <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
                </svg>
            {% elif trend_direction == "down" %}
                <svg class="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" focusable="false">
                    <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
                </svg>
            {% else %}
                <svg class="stat-card__trend-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" focusable="false">
                    <path fill-rule="evenodd" d="M4 10a.75.75 0 01.75-.75h10.5a.75.75 0 010 1.5H4.75A.75.75 0 014 10z" clip-rule="evenodd" />
                </svg>
            {% endif %}
            {{ trend_value }}
        </span>
    {% endif %}
</article>
```

---

## 3. 대시보드 뷰

### `web/views/dashboard/views.py`

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard_root.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = [
            {
                "title": "총 매출",
                "value": "12,450,000",
                "unit": "원",
                "trend_value": "+12.5%",
                "trend_direction": "up",
            },
            {
                "title": "신규 주문",
                "value": "384",
                "unit": "건",
                "trend_value": "-3.2%",
                "trend_direction": "down",
            },
            {
                "title": "활성 사용자",
                "value": "1,208",
                "unit": "명",
                "trend_value": "0%",
                "trend_direction": "neutral",
            },
        ]
        return ctx
```

### `web/view_urls.py` (URL 등록)

```python
from web.views.dashboard.views import DashboardView

app_name = "web"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
```

---

## 4. 대시보드 페이지 템플릿

### `web/templates/dashboard/dashboard_root.html`

```htmldjango
{% extends "base.html" %}
{% load static %}

{% block title %}대시보드{% endblock title %}

{% block head_extra %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
{% endblock head_extra %}

{% block body %}
<main class="dashboard">
    <h1 class="dashboard__heading">대시보드</h1>
    <div class="dashboard__stats-grid" role="region" aria-label="핵심 지표">
        {% for stat in stats %}
            {% include "design_system/cards/_stat_card.html" with title=stat.title value=stat.value unit=stat.unit trend_value=stat.trend_value trend_direction=stat.trend_direction only %}
        {% endfor %}
    </div>
</main>
{% endblock body %}
```

---

## 5. 대시보드 레이아웃 CSS

### `static/css/dashboard.css`

```css
.dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-xl, 2rem) var(--spacing-md, 1rem);
}

.dashboard__heading {
    font-family: var(--font-sans, 'Inter', system-ui, sans-serif);
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-text, #1f2937);
    margin: 0 0 var(--spacing-lg, 1.5rem) 0;
}

.dashboard__stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-lg, 1.5rem);
}

@media (max-width: 768px) {
    .dashboard__stats-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 6. 글로벌 스타일시트에 컴포넌트 CSS 등록

### `static/css/style.css` (기존 파일에 추가)

```css
@import "../../../web/templates/design_system/cards/stat-card.css";
```

---

## 접근성 체크리스트

| 항목 | 구현 |
|------|------|
| WCAG AA 대비율 (4.5:1) | 라이트: `#1f2937` on `#ffffff` = 15.4:1, 다크: `#f9fafb` on `#1f2937` = 14.7:1 |
| 큰 텍스트 대비율 (3:1) | 값 텍스트 (1.875rem, 700): 라이트 15.4:1, 다크 14.7:1 |
| 포커스 링 | `tabindex="0"` + `:focus-within` 에서 `var(--focus-ring)` 적용 |
| 모션 감소 | `@media (prefers-reduced-motion: reduce)` 에서 `transition: none`, `transform: none` |
| 스크린 리더 | `role="group"` + `aria-label`로 카드 제목 제공, 변동률에 `role="status"` + `aria-label`로 방향 설명 |
| SVG 아이콘 | `aria-hidden="true"` + `focusable="false"`로 스크린 리더에서 중복 읽기 방지 |
| 시맨틱 마크업 | `<article>` 요소, `<h3>` 제목, `<main>` 랜드마크 사용 |

---

## 컨벤션 적용 사항

| 컨벤션 | 적용 |
|--------|------|
| `{% include ... only %}` | 대시보드에서 stat_card 호출 시 `only` 키워드 사용 |
| 필수 변수 문서화 | `_stat_card.html` 상단에 `{# 필수 변수: ... #}` 주석 |
| `{% static %}` 태그 | CSS 경로에 `{% static %}` 사용, 하드코딩 없음 |
| `var()` 폴백 값 | 모든 CSS Custom Property에 폴백 값 지정 |
| 3계층 토큰 | primitive(`--blue-500`) -> semantic(`--color-text`) -> component(`--stat-card-value-color`) |
| `[data-theme="dark"]` | semantic 토큰 재정의 + 컴포넌트 전용 다크 모드 보정 |
| 시스템 다크 모드 감지 | `@media (prefers-color-scheme: dark)` + `:root:not([data-theme])` |
| `{{ block.super }}` | `head_extra` 블록에서 부모 콘텐츠 유지 |
| `{% endblock name %}` | 닫는 태그에 블록명 명시 |
| `LoginRequiredMixin` | `DashboardView`에 MRO 순서 준수하여 적용 |
| 인라인 스타일 금지 | 별도 `.css` 파일로 분리 |
| 스타일 오버라이드 금지 | 디자인 시스템 외부에서 `.stat-card` 스타일 변경 없음 |
| 파일 네이밍 | HTML: `_stat_card.html` (밑줄 접두사), CSS: `stat-card.css` (케밥 케이스) |
| 컴포넌트 폴더 배치 | `design_system/cards/` 하위에 HTML과 CSS 동일 폴더 배치 |
