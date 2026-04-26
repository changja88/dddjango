# TC-C2: 디자인 시스템 규칙에 맞는 리팩토링

## 문제 분석

기존 코드의 디자인 시스템 위반 사항:

1. **커스텀 CSS에서 디자인 토큰 미사용** -- 하드코딩된 색상(`#1a56db`, `#6b7280`, `#ddd`), 폰트 크기(`12px`, `14px`, `32px`), 간격(`4px`, `8px`, `20px`) 사용
2. **버튼 컴포넌트 중복 정의** -- `_btn_primary.html` 파티얼을 include하면서 동시에 `.btn-primary` CSS를 별도로 재정의
3. **stat-card가 재사용 가능한 컴포넌트로 분리되지 않음** -- 동일 구조가 반복되지만 파티얼 없이 인라인 HTML로 작성

## 리팩토링 결과

### 1. 디자인 토큰 정의 (CSS Custom Properties)

```css
/* design_system/css/tokens.css */
:root {
    /* Colors */
    --color-primary: #1a56db;
    --color-text-secondary: #6b7280;
    --color-border: #d1d5db;
    --color-surface: #ffffff;

    /* Font Sizes */
    --font-size-sm: 0.875rem;   /* 14px */
    --font-size-base: 1rem;     /* 16px */
    --font-size-3xl: 2rem;      /* 32px */

    /* Spacing */
    --spacing-1: 0.25rem;  /* 4px */
    --spacing-2: 0.5rem;   /* 8px */
    --spacing-5: 1.25rem;  /* 20px */

    /* Border Radius */
    --radius-lg: 0.5rem;   /* 8px */

    /* Font Weight */
    --font-weight-bold: 700;
}
```

### 2. stat-card 컴포넌트 파티얼

```htmldjango
{# design_system/components/_stat_card.html #}
{# @param value: 표시할 값 (필수) #}
{# @param label: 설명 레이블 (필수) #}
{# @param suffix: 값 뒤에 붙는 단위 (선택) #}
<div class="ds-stat-card">
    <div class="ds-stat-card__value">{{ value }}{{ suffix }}</div>
    <div class="ds-stat-card__label">{{ label }}</div>
</div>
```

### 3. 컴포넌트 CSS (토큰 기반)

```css
/* design_system/css/components/stat_card.css */
.ds-stat-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-5);
}

.ds-stat-card__value {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
}

.ds-stat-card__label {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin-top: var(--spacing-1);
}
```

### 4. orders 앱 CSS (리팩토링 후)

```css
/* orders/css/orders.css */
/*
 * 버튼 스타일 제거: design_system/_btn_primary.html 파티얼이
 * 디자인 시스템 버튼 스타일을 포함하므로 앱 레벨 재정의 불필요.
 *
 * stat-card 스타일 제거: design_system/components/_stat_card.html 및
 * stat_card.css로 이관.
 *
 * 이 파일에는 orders 앱 고유의 레이아웃만 남긴다.
 */

.dashboard {
    display: grid;
    gap: var(--spacing-5);
}

.dashboard__stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-5);
}
```

### 5. 템플릿 (리팩토링 후)

```htmldjango
{# orders/order_dashboard.html #}
{% extends "base.html" %}
{% block body %}
<div class="dashboard">
    {% include "design_system/buttons/_btn_primary.html" with label="새 주문" %}

    <div class="dashboard__stats">
        {% include "design_system/components/_stat_card.html" with value=total_orders label="총 주문" %}
        {% include "design_system/components/_stat_card.html" with value=revenue suffix="원" label="이번 달 매출" %}
    </div>
</div>
{% endblock %}
```

## 변경 요약

| 항목 | Before | After |
|---|---|---|
| 색상 값 | 하드코딩 (`#1a56db`) | 토큰 (`var(--color-primary)`) |
| 폰트/간격 | 하드코딩 (`32px`, `20px`) | 토큰 (`var(--font-size-3xl)`, `var(--spacing-5)`) |
| 버튼 CSS | 앱 CSS에서 재정의 | 디자인 시스템 파티얼에 위임, 앱 CSS에서 제거 |
| stat-card HTML | 인라인 반복 | `_stat_card.html` 파티얼로 추출 |
| stat-card CSS | `orders.css`에 혼재 | `design_system/css/components/stat_card.css`로 분리 |
| CSS 네이밍 | `.stat-card .value` (후손 셀렉터) | `.ds-stat-card__value` (BEM, `ds-` 네임스페이스) |
| 대시보드 레이아웃 | 없음 | `.dashboard__stats` 그리드 레이아웃 추가 |

## 적용된 디자인 시스템 원칙

1. **디자인 토큰** -- 모든 시각적 값(색상, 크기, 간격)을 CSS Custom Properties로 중앙 관리
2. **컴포넌트 파티얼** -- 반복되는 UI 패턴을 Django 템플릿 파티얼로 추출하여 재사용
3. **BEM + 네임스페이스** -- `ds-stat-card__value` 형태로 디자인 시스템 컴포넌트 스코프 명확화
4. **관심사 분리** -- 디자인 시스템 CSS는 `design_system/css/`에, 앱 고유 레이아웃은 앱 CSS에 배치
5. **단일 책임** -- 앱 CSS에서 디자인 시스템 컴포넌트 스타일 재정의 제거
