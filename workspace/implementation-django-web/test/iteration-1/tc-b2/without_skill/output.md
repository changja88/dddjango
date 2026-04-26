# Design System CSS & Component Code Review

## 1. 리뷰 대상 파일

| 파일 | 역할 |
|------|------|
| `design_system/buttons/btn-primary.css` | Primary 버튼 스타일 정의 |
| `design_system/buttons/_btn_primary.html` | Primary 버튼 Django 템플릿 컴포넌트 |
| `orders/order_list.html` | 버튼 컴포넌트 사용처 |

---

## 2. CSS 리뷰 (`btn-primary.css`)

### 잘된 점

- **transition 적용**: `background-color 0.2s ease`로 호버 시 부드러운 전환 효과를 제공한다.
- **:focus 스타일 존재**: `outline`과 `outline-offset`를 명시하여 키보드 접근성을 기본적으로 확보했다.
- **단일 책임**: 하나의 파일이 하나의 컴포넌트 스타일만 담당한다.

### 문제점 및 개선 사항

#### P1 (높음) -- 하드코딩된 색상값

```css
/* 현재 */
background-color: #3b82f6;

/* 개선: CSS Custom Properties 사용 */
:root {
    --color-primary: #3b82f6;
    --color-primary-dark: #1d4ed8;
}
.btn-primary {
    background-color: var(--color-primary);
}
.btn-primary:hover {
    background-color: var(--color-primary-dark);
}
```

디자인 시스템이라면 색상, 간격, 폰트 크기 등을 CSS Custom Properties(변수)로 관리해야 한다. 현재 `#3b82f6`이 배경과 포커스 아웃라인에 중복 사용되고 있어, 색상 변경 시 여러 곳을 수정해야 하는 유지보수 부담이 생긴다.

#### P1 (높음) -- disabled 상태 스타일 누락

템플릿에서 `disabled` 속성을 지원하지만, CSS에 `.btn-primary:disabled` 또는 `.btn-primary[disabled]` 스타일이 없다. 비활성 버튼이 활성 버튼과 동일하게 보이는 UX 문제가 발생한다.

```css
/* 추가 필요 */
.btn-primary:disabled {
    background-color: var(--color-gray-300, #d1d5db);
    color: var(--color-gray-500, #6b7280);
    cursor: not-allowed;
    pointer-events: none;
}
```

#### P2 (중간) -- border 초기화 누락

브라우저 기본 `<button>` 스타일에는 border가 포함되어 있다. 명시적으로 `border: none;`을 선언하지 않으면 브라우저마다 다른 기본 테두리가 표시될 수 있다.

```css
.btn-primary {
    border: none;
    cursor: pointer;
    /* ... */
}
```

#### P2 (중간) -- cursor 속성 누락

버튼에 `cursor: pointer;`가 없다. 사용자에게 클릭 가능한 요소임을 시각적으로 알려주지 못한다.

#### P3 (낮음) -- :active 상태 누락

hover, focus는 있지만 클릭 중 시각 피드백(:active)이 없다.

```css
.btn-primary:active {
    background-color: var(--color-primary-darker, #1e40af);
    transform: translateY(1px);
}
```

---

## 3. Django 템플릿 컴포넌트 리뷰 (`_btn_primary.html`)

### 잘된 점

- **언더스코어 접두사 컨벤션**: `_btn_primary.html`로 partial 템플릿임을 명시한다.
- **include용 설계**: `{% include %}` + `with`로 사용하도록 설계되어 재사용성이 좋다.

### 문제점 및 개선 사항

#### P1 (높음) -- type 속성 누락

`<button>`에 `type` 속성이 없으면 기본값이 `type="submit"`이다. `<form>` 안에서 사용할 경우 의도치 않은 폼 제출이 발생할 수 있다.

```htmldjango
{# 개선 #}
<button type="{{ type|default:'button' }}" class="btn-primary" {% if disabled %}disabled{% endif %}>
    {{ label }}
</button>
```

#### P1 (높음) -- 확장성 부족

현재 컴포넌트는 `label`과 `disabled`만 지원한다. 실제 사용에서 필요한 아이콘, 추가 CSS 클래스, data 속성, onclick 핸들러 등을 전달할 수 없다.

```htmldjango
{# 개선된 버전 #}
<button
    type="{{ type|default:'button' }}"
    class="btn-primary{% if extra_class %} {{ extra_class }}{% endif %}{% if size %} btn-{{ size }}{% endif %}"
    {% if disabled %}disabled{% endif %}
    {% if attrs %}{{ attrs }}{% endif %}
>
    {% if icon_left %}<span class="btn-icon btn-icon--left">{{ icon_left }}</span>{% endif %}
    {{ label }}
    {% if icon_right %}<span class="btn-icon btn-icon--right">{{ icon_right }}</span>{% endif %}
</button>
```

#### P2 (중간) -- XSS 방어 확인 필요

`{{ label }}`은 Django 기본 auto-escaping이 적용되므로 일반적으로 안전하다. 다만 `{{ attrs }}`처럼 raw HTML 속성을 전달하는 패턴을 도입할 경우, `mark_safe` 사용에 주의해야 한다.

#### P2 (중간) -- 접근성(a11y) 속성 지원 부족

`aria-label`, `aria-disabled`, `aria-busy` 등의 접근성 속성을 전달할 방법이 없다.

```htmldjango
{% if aria_label %}aria-label="{{ aria_label }}"{% endif %}
```

---

## 4. 사용처 리뷰 (`orders/order_list.html`)

### 문제점 및 개선 사항

#### P0 (심각) -- 디자인 시스템 일관성 파괴

```html
<style>
.order-page .btn-primary {
    font-size: 12px;
    padding: 4px 8px;
}
</style>
```

이것은 디자인 시스템의 핵심 원칙을 위반하는 안티패턴이다. 개별 페이지에서 디자인 시스템 컴포넌트의 스타일을 직접 오버라이드하면 다음 문제가 발생한다.

1. **일관성 상실**: 페이지마다 같은 버튼이 다르게 보인다.
2. **유지보수 비용 증가**: 디자인 시스템을 업데이트해도 오버라이드된 곳은 반영되지 않는다.
3. **추적 불가**: 어느 페이지에서 어떤 스타일을 오버라이드했는지 파악하기 어렵다.

**올바른 해결 방법**: 디자인 시스템에 size variant를 추가한다.

```css
/* design_system/buttons/btn-primary.css */
.btn-primary--sm {
    font-size: 12px;
    padding: 4px 8px;
}
.btn-primary--lg {
    font-size: 18px;
    padding: 12px 24px;
}
```

```htmldjango
{# 사용 시 #}
{% include "design_system/buttons/_btn_primary.html" with label="새 주문" size="sm" %}
```

#### P2 (중간) -- 인라인 `<style>` 태그 사용

페이지 내 `<style>` 태그는 CSP(Content Security Policy) 위반 가능성이 있고, 스타일 로딩 순서에 따른 FOUC(Flash of Unstyled Content) 문제를 유발할 수 있다.

---

## 5. 구조적 개선 제안

### 5.1 디자인 토큰 체계 도입

```css
/* design_system/tokens.css */
:root {
    /* Colors */
    --ds-color-primary: #3b82f6;
    --ds-color-primary-hover: #1d4ed8;
    --ds-color-primary-active: #1e40af;

    /* Spacing */
    --ds-spacing-xs: 4px;
    --ds-spacing-sm: 8px;
    --ds-spacing-md: 16px;

    /* Typography */
    --ds-font-size-sm: 12px;
    --ds-font-size-md: 14px;
    --ds-font-size-lg: 18px;

    /* Border Radius */
    --ds-radius-sm: 4px;
    --ds-radius-md: 8px;
}
```

### 5.2 파일 네이밍 통일

현재 CSS는 케밥 케이스(`btn-primary.css`), 템플릿은 스네이크 케이스(`_btn_primary.html`)를 혼용하고 있다. 하나의 컨벤션으로 통일하는 것을 권장한다. Django 템플릿은 관례상 스네이크 케이스를 따르므로, CSS 파일도 `btn_primary.css`로 맞추거나, 명확한 네이밍 규칙을 문서화해야 한다.

### 5.3 Django 컴포넌트 라이브러리 고려

`{% include %}` 기반 컴포넌트는 타입 안전성, 필수 파라미터 검증, 기본값 관리 등에 한계가 있다. 프로젝트 규모가 커진다면 다음 대안을 고려할 수 있다.

- **django-components**: 컴포넌트 단위로 HTML/CSS/JS를 캡슐화
- **Custom template tags**: 파라미터 검증과 기본값을 Python 코드에서 관리

```python
# templatetags/design_system.py
@register.inclusion_tag("design_system/buttons/_btn_primary.html")
def btn_primary(label, type="button", size="md", disabled=False):
    return {
        "label": label,
        "type": type,
        "size": size,
        "disabled": disabled,
    }
```

```htmldjango
{# 사용 시 -- 파라미터 검증이 Python 레벨에서 이루어짐 #}
{% load design_system %}
{% btn_primary label="새 주문" size="sm" %}
```

---

## 6. 요약

| 우선순위 | 항목 | 위치 |
|----------|------|------|
| P0 | 디자인 시스템 스타일 오버라이드 제거, size variant 도입 | `order_list.html` |
| P1 | CSS Custom Properties로 색상 관리 | `btn-primary.css` |
| P1 | disabled 상태 CSS 추가 | `btn-primary.css` |
| P1 | button type 속성 기본값 설정 | `_btn_primary.html` |
| P1 | 컴포넌트 확장성 개선 (size, class, icon 등) | `_btn_primary.html` |
| P2 | border 초기화, cursor 추가 | `btn-primary.css` |
| P2 | 접근성 속성 지원 | `_btn_primary.html` |
| P2 | 인라인 style 태그 제거 | `order_list.html` |
| P3 | :active 상태 추가 | `btn-primary.css` |
