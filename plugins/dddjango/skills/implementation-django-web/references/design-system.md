# 디자인 시스템 레퍼런스

> Django 템플릿 기반 디자인 시스템의 구축, 토큰 관리, 컴포넌트 작성 규칙을 다룬다.

---

## 1. 디자인 토큰

디자인 토큰(컬러, 폰트, 간격 등)은 CSS Custom Properties로 정의하고, 모든 스타일에서 `var()`로 참조한다. 하드코딩된 값을 직접 사용하지 않는다.

출처: MDN — Using CSS custom properties (https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties)

### 3계층 토큰 구조

토큰은 primitive → semantic → component 3계층으로 구성한다. 상위 계층은 하위 계층을 참조한다.

출처: Penpot — Developer's Guide to Design Tokens (https://penpot.app/blog/the-developers-guide-to-design-tokens-and-css-variables/)

```css
/* 1계층: Primitive — 원시 값 (색상 팔레트, 크기 등) */
:root {
    --blue-500: #3b82f6;
    --blue-700: #1d4ed8;
    --gray-100: #f3f4f6;
    --gray-500: #6b7280;
    --gray-900: #1f2937;
}

/* 2계층: Semantic — 역할 기반 별칭 (용도를 표현) */
:root {
    --color-primary: var(--blue-500);
    --color-primary-hover: var(--blue-700);
    --color-text: var(--gray-900);
    --color-text-muted: var(--gray-500);
    --color-bg: #ffffff;
    --color-bg-subtle: var(--gray-100);
    --color-border: #e5e7eb;

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
}

/* 3계층: Component — 특정 컴포넌트 전용 (선택적) */
:root {
    --btn-bg: var(--color-primary);
    --btn-bg-hover: var(--color-primary-hover);
    --btn-text: #ffffff;
    --card-border: var(--color-border);
    --card-radius: var(--radius-md);
}
```

### var() 폴백 값

토큰이 정의되지 않은 경우를 대비하여 폴백 값을 지정한다.

```css
.order-card {
    color: var(--color-text, #1f2937);
    padding: var(--spacing-md, 1rem);
    border-radius: var(--radius-md, 0.5rem);
}
```

### 네이밍 규칙

`[카테고리]-[속성]-[요소]-[수식어]-[상태]` 패턴을 따른다.

```css
--color-primary           /* 카테고리-속성 */
--color-primary-hover     /* 카테고리-속성-상태 */
--btn-bg                  /* 요소-속성 (컴포넌트 토큰) */
--btn-bg-hover            /* 요소-속성-상태 */
```

---

## 2. 다크 모드 / 테마

CSS Custom Properties를 재정의하여 테마를 전환한다.

출처: MDN — Using CSS custom properties (https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascading_variables/Using_custom_properties)

### data 속성 기반 테마

```css
/* 다크 테마 — semantic 토큰만 재정의 */
[data-theme="dark"] {
    --color-primary: #60a5fa;
    --color-text: #f9fafb;
    --color-text-muted: #9ca3af;
    --color-bg: #111827;
    --color-bg-subtle: #1f2937;
    --color-border: #374151;
}
```

### 시스템 설정 감지

```css
/* 사용자가 명시적으로 테마를 선택하지 않은 경우 시스템 설정 따름 */
@media (prefers-color-scheme: dark) {
    :root:not([data-theme]) {
        --color-primary: #60a5fa;
        --color-text: #f9fafb;
        --color-bg: #111827;
        --color-border: #374151;
    }
}
```

### 반응형 토큰

미디어 쿼리 내에서 토큰을 재정의하여 반응형 디자인에 활용한다.

```css
@media (max-width: 768px) {
    :root {
        --spacing-lg: 1rem;
        --spacing-xl: 1.5rem;
        --text-lg: 1rem;
    }
}
```

---

## 3. 접근성 토큰

디자인 시스템은 접근성 관련 토큰을 정의하여 WCAG 가이드라인을 준수한다.

출처: W3C WCAG 2.1 SC 1.4.3 — Contrast (Minimum) (https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)

```css
:root {
    /* 포커스 링 — 키보드 네비게이션 시 가시성 */
    --color-focus-ring: #2563eb;
    --focus-ring: 0 0 0 3px var(--color-focus-ring);

    /* 트랜지션 기본 시간 */
    --transition-duration: 200ms;
}

/* 모션 감소 선호 사용자 */
@media (prefers-reduced-motion: reduce) {
    :root {
        --transition-duration: 0ms;
    }
}
```

- 텍스트 색상은 배경 대비 **4.5:1 이상** (WCAG AA 기준)
- 큰 텍스트(18px+ 또는 14px+ bold)는 **3:1 이상**
- 포커스 표시기는 모든 인터랙티브 요소에 가시적이어야 한다

---

## 4. 디자인 시스템 폴더 구조

여러 페이지에서 재사용되는 UI 컴포넌트는 `design_system/` 하위 카테고리 폴더에 Django 템플릿 파트셜로 관리한다. 동일한 컴포넌트를 각 페이지 템플릿에 중복 작성하지 않는다.

```
web/templates/design_system/
├── buttons/           # 버튼, 토글, 칩 등
├── cards/             # 카드 레이아웃
├── forms/             # 입력 폼, 드롭다운, 검색 등
├── navigation/        # 네비게이션 바, 탭, 브레드크럼
├── feedback/          # 스피너, 토스트, 알림
├── layout/            # 푸터, 구분선, 컨테이너
└── data-display/      # 테이블, 목록, 아바타
```

- 새 컴포넌트를 만들기 전에 기존 컴포넌트를 먼저 확인하여 중복을 방지한다
- 카테고리는 UI 기능 기준으로 분류한다

### Atomic Design과의 관계

Brad Frost의 Atomic Design은 atoms → molecules → organisms → templates → pages 5단계 분류를 제시한다. 위 구조는 기능 기반 분류를 사용하지만, Atomic Design의 원칙(작은 단위부터 조합)은 동일하게 적용된다.

출처: Brad Frost — Atomic Design Chapter 2 (https://atomicdesign.bradfrost.com/chapter-2/)

| Atomic Design | 기능 기반 구조 (위 구조) |
|----------------|--------------------------|
| Atoms (버튼, 입력 등) | `buttons/`, `forms/` 내 개별 요소 |
| Molecules (검색 폼 등) | `forms/` 내 복합 컴포넌트 |
| Organisms (내비게이션 등) | `navigation/`, `cards/` |

---

## 5. 컴포넌트 파일 컨벤션

### 네이밍 규칙

| 파일 종류 | 규칙 | 예시 |
|-----------|------|------|
| HTML 파트셜 | `_` 접두사 | `_btn_primary.html` |
| CSS | 케밥 케이스, 접두사 없음 | `btn-primary.css` |
| JS | 케밥 케이스 | `dropdown.js` |

- CSS가 불필요한 컴포넌트(CSS 프레임워크 클래스만으로 충분)는 HTML만 생성
- 각 컴포넌트의 CSS는 HTML과 동일 폴더에 배치

### 파일 구조 예시

```
design_system/buttons/
├── _btn_primary.html          # HTML 파트셜
├── btn-primary.css            # 스타일
├── _btn_secondary.html
└── btn-secondary.css
```

---

## 6. 컴포넌트 사용 규칙

### 기본 사용 (only 키워드)

`only` 키워드를 사용하여 컴포넌트에 전달되는 변수를 명시적으로 제한한다.

출처: Django 공식 문서 — include tag (https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#include)

```htmldjango
{# only 사용 — 명시적으로 전달한 변수만 접근 가능 #}
{% include "design_system/buttons/_btn_primary.html" with label="저장" only %}
{% include "design_system/cards/_stat_card.html" with title="총 주문" value=order_count only %}
```

### 스타일 오버라이드 금지

디자인 시스템 컴포넌트의 스타일을 외부 CSS에서 오버라이드하지 않는다.

```css
/* 나쁜 예: 외부에서 디자인 시스템 컴포넌트 스타일 변경 */
.order-page .btn-primary {
    font-size: 0.75rem;
    padding: 0.25rem;
}
```

크기/색상 등 변형이 필요하면 디자인 시스템 안에 modifier를 만든다.

```css
/* 좋은 예: 디자인 시스템 내부에 modifier 추가 */
.btn-primary-sm {
    font-size: var(--text-sm, 0.875rem);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}
```

```htmldjango
{% include "design_system/buttons/_btn_primary_sm.html" with label="저장" only %}
```

### CSS 로드

디자인 시스템 CSS는 글로벌 스타일시트에서 `@import`로 로드한다.

```css
/* style.css */
@import "../../../web/templates/design_system/buttons/btn-primary.css";
@import "../../../web/templates/design_system/cards/stat-card.css";
```

### 대안: django-components

`{% include %}` 방식보다 풍부한 기능(슬롯, 타입 안전 인자, CSS/JS 격리)이 필요하면 django-components를 검토할 수 있다.

출처: django-components (https://github.com/django-components/django-components), TestDriven.io — Building Reusable Components in Django (https://testdriven.io/blog/django-reusable-components/)

---

## 7. 동적 동작

### 데이터 전달

`{% include ... with ... only %}` 패턴으로 컴포넌트에 데이터를 전달한다.

```htmldjango
{% include "design_system/cards/_stat_card.html" with title="총 매출" value=revenue unit="원" only %}
```

### 인터랙션 (JS 프레임워크 사용 시)

경량 JS 프레임워크(Alpine.js 등)를 사용하는 경우, 컴포넌트에 디렉티브를 포함한다.

```htmldjango
{# design_system/forms/_dropdown.html #}
{# 필수 변수: items (list), placeholder (str) #}
<div x-data="{ open: false, selected: '' }">
    <button @click="open = !open">
        <span x-text="selected || '{{ placeholder|escapejs }}'"></span>
    </button>
    <ul x-show="open" @click.outside="open = false">
        {% for item in items %}
            <li @click="selected = '{{ item|escapejs }}'; open = false">{{ item }}</li>
        {% endfor %}
    </ul>
</div>
```

- Django 변수를 JS 문자열에 삽입할 때 반드시 `|escapejs` 필터를 사용한다 (XSS 방지)
- 복잡한 데이터는 `json_script`로 전달한다

### 공유 JS 컴포넌트

여러 디자인 시스템 컴포넌트에서 재사용하는 JS 로직은 공유 파일에 정의한다.

```javascript
// static/js/components.js — base.html에서 글로벌 로드
function dropdown(options = {}) {
    return {
        open: false,
        selected: options.default || '',
        toggle() { this.open = !this.open },
        select(value) { this.selected = value; this.open = false }
    }
}
```

```htmldjango
{# 컴포넌트에서 공유 로직 사용 #}
<div x-data="dropdown({ default: '전체' })">
    ...
</div>
```

### 부모 스코프 의존

컴포넌트가 부모의 JS 스코프 변수에 의존할 경우, HTML 주석으로 필수 변수를 명시한다.

```htmldjango
{# design_system/feedback/_loading_overlay.html #}
{# 부모 x-data 필수 변수: isLoading (boolean) #}
<div x-show="isLoading" class="loading-overlay">
    {% include "design_system/feedback/_spinner.html" %}
</div>
```

---

## 8. 컴포넌트 문서화 도구

디자인 시스템 컴포넌트를 독립적으로 미리보고 테스트하는 도구이다.

출처: django-pattern-library (https://torchbox.github.io/django-pattern-library/)

- **django-pattern-library**: YAML 기반 목 데이터로 컴포넌트를 독립 렌더링, Storybook과 유사
- **storybook-django**: Storybook UI에서 Django 템플릿 컴포넌트를 미리보기

DEBUG 전용 뷰에서 간단한 컴포넌트 미리보기 페이지를 제공하는 것도 대안이다.
