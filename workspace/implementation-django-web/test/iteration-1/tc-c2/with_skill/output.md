# Refactoring: orders/order_dashboard.html + orders/css/orders.css

---

## Change 1: Hardcoded color/size values -> CSS Custom Property tokens

[Before]
```css
/* orders/css/orders.css */
.btn-primary {
    font-size: 12px;
    padding: 4px 8px;
}

.stat-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
}

.stat-card .value {
    font-size: 32px;
    font-weight: bold;
    color: #1a56db;
}

.stat-card .label {
    font-size: 14px;
    color: #6b7280;
    margin-top: 4px;
}
```

[After]
```css
/* orders/css/orders.css */
/* btn-primary 스타일 오버라이드 제거됨 -- Change 2 참고 */

/* stat-card 스타일은 디자인 시스템 컴포넌트로 이동됨 -- Change 3 참고 */
```

[Reason] Hardcoded color/size values -> EXTRACT to CSS Custom Property tokens -- 모든 색상(`#ddd`, `#1a56db`, `#6b7280`, `white`), 크기(`12px`, `14px`, `32px`, `8px`, `20px`, `4px 8px`, `4px`) 값이 디자인 토큰(`var()`) 없이 하드코딩되어 있다. 디자인 시스템의 3계층 토큰(primitive -> semantic -> component)을 `var()` 폴백과 함께 사용해야 한다.

---

## Change 2: External component style override -> MOVE to design system modifier

[Before]
```css
/* orders/css/orders.css */
.btn-primary {
    font-size: 12px;
    padding: 4px 8px;
}
```

```htmldjango
{% include "design_system/buttons/_btn_primary.html" with label="새 주문" %}
```

[After]

`orders/css/orders.css`에서 `.btn-primary` 오버라이드를 완전히 제거한다.

디자인 시스템 내부에 `sm` modifier 컴포넌트를 추가한다:

```css
/* design_system/buttons/btn-primary-sm.css */
.btn-primary-sm {
    font-size: var(--text-sm, 0.875rem);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}
```

```htmldjango
{# design_system/buttons/_btn_primary_sm.html #}
{# 필수 변수: label (str) #}
<button type="button" class="btn-primary-sm">{{ label }}</button>
```

```htmldjango
{# 사용처 변경 #}
{% include "design_system/buttons/_btn_primary_sm.html" with label="새 주문" only %}
```

[Reason] External component style override -> MOVE to design system modifier -- 외부 CSS(`orders/css/orders.css`)에서 디자인 시스템 컴포넌트(`.btn-primary`)의 스타일을 오버라이드하고 있다. 디자인 시스템 컴포넌트의 스타일을 외부에서 변경하는 것은 금지이며, 크기/색상 변형이 필요하면 디자인 시스템 안에 modifier를 만들어야 한다.

---

## Change 3: Flat template -> RESTRUCTURE with component folders (stat-card를 디자인 시스템 컴포넌트로 추출)

[Before]
```css
/* orders/css/orders.css */
.stat-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
}

.stat-card .value {
    font-size: 32px;
    font-weight: bold;
    color: #1a56db;
}

.stat-card .label {
    font-size: 14px;
    color: #6b7280;
    margin-top: 4px;
}
```

```htmldjango
<div class="stat-card">
    <div class="value">{{ total_orders }}</div>
    <div class="label">총 주문</div>
</div>
<div class="stat-card">
    <div class="value">{{ revenue }}원</div>
    <div class="label">이번 달 매출</div>
</div>
```

[After]

디자인 시스템 컴포넌트로 추출한다:

```css
/* design_system/cards/stat-card.css */
.stat-card {
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    padding: var(--spacing-xl, 2rem);
}

.stat-card__value {
    font-size: var(--text-2xl, 2rem);
    font-weight: bold;
    color: var(--color-primary, #3b82f6);
}

.stat-card__label {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
    margin-top: var(--spacing-xs, 0.25rem);
}
```

```htmldjango
{# design_system/cards/_stat_card.html #}
{# 필수 변수: value (str), label (str) #}
<div class="stat-card">
    <div class="stat-card__value">{{ value }}</div>
    <div class="stat-card__label">{{ label }}</div>
</div>
```

```htmldjango
{# 사용처 변경 #}
{% include "design_system/cards/_stat_card.html" with value=total_orders label="총 주문" only %}
{% include "design_system/cards/_stat_card.html" with value=revenue|stringformat:"s원" label="이번 달 매출" only %}
```

[Reason] Flat template -> RESTRUCTURE with component folders + Hardcoded color/size values -> EXTRACT to CSS Custom Property tokens -- `stat-card`는 재사용 가능한 UI 컴포넌트이므로 `design_system/cards/`로 이동하여 여러 페이지에서 중복 없이 재사용할 수 있도록 한다. 하드코딩된 모든 값은 디자인 토큰으로 교체하고, CSS 클래스명은 BEM 네이밍(`stat-card__value`, `stat-card__label`)으로 변경하여 `.value`, `.label` 같은 범용 클래스명과의 충돌을 방지한다.

---

## Change 4: `{% include %}` without `only` -> ADD `only` keyword

[Before]
```htmldjango
{% include "design_system/buttons/_btn_primary.html" with label="새 주문" %}
```

[After]
```htmldjango
{% include "design_system/buttons/_btn_primary_sm.html" with label="새 주문" only %}
```

[Reason] `{% include %}` without `only` -> ADD `only` keyword -- 디자인 시스템 컴포넌트에서는 `only` 키워드를 사용하여 명시적으로 전달한 변수만 접근 가능하게 해야 한다. `only` 없이 include하면 부모 컨텍스트의 모든 변수가 암묵적으로 전달되어 의도치 않은 의존성이 생긴다.

---

## Change 5: `{% endblock %}` without block name -> ADD block name

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

[Reason] No `{% block %}` name in closing `{% endblock %}` tag -- 닫는 `{% endblock %}` 태그에 블록명을 명시하면 가독성이 향상된다. 특히 블록 내용이 길어질 때 어떤 블록이 닫히는지 명확히 알 수 있다.

---

## Complete Refactored Code

### 1. design_system/buttons/btn-primary-sm.css (NEW)

```css
/* design_system/buttons/btn-primary-sm.css */
.btn-primary-sm {
    font-size: var(--text-sm, 0.875rem);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}
```

### 2. design_system/buttons/_btn_primary_sm.html (NEW)

```htmldjango
{# design_system/buttons/_btn_primary_sm.html #}
{# 필수 변수: label (str) #}
<button type="button" class="btn-primary-sm">{{ label }}</button>
```

### 3. design_system/cards/stat-card.css (NEW)

```css
/* design_system/cards/stat-card.css */
.stat-card {
    background: var(--color-bg, #ffffff);
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: var(--card-radius, var(--radius-md, 0.5rem));
    padding: var(--spacing-xl, 2rem);
}

.stat-card__value {
    font-size: var(--text-2xl, 2rem);
    font-weight: bold;
    color: var(--color-primary, #3b82f6);
}

.stat-card__label {
    font-size: var(--text-sm, 0.875rem);
    color: var(--color-text-muted, #6b7280);
    margin-top: var(--spacing-xs, 0.25rem);
}
```

### 4. design_system/cards/_stat_card.html (NEW)

```htmldjango
{# design_system/cards/_stat_card.html #}
{# 필수 변수: value (str), label (str) #}
<div class="stat-card">
    <div class="stat-card__value">{{ value }}</div>
    <div class="stat-card__label">{{ label }}</div>
</div>
```

### 5. orders/css/orders.css (UPDATED)

```css
/* orders/css/orders.css */
/* stat-card, btn-primary 스타일은 디자인 시스템으로 이동됨 */
/* design_system/cards/stat-card.css */
/* design_system/buttons/btn-primary-sm.css */
```

### 6. style.css (UPDATE -- @import 추가)

```css
/* style.css -- 기존 import에 추가 */
@import "../../../web/templates/design_system/buttons/btn-primary-sm.css";
@import "../../../web/templates/design_system/cards/stat-card.css";
```

### 7. orders/order_dashboard.html (UPDATED)

```htmldjango
{# orders/order_dashboard.html #}
{% extends "base.html" %}
{% block body %}
<div class="dashboard">
    {% include "design_system/buttons/_btn_primary_sm.html" with label="새 주문" only %}

    {% include "design_system/cards/_stat_card.html" with value=total_orders label="총 주문" only %}
    {% include "design_system/cards/_stat_card.html" with value=revenue|stringformat:"s원" label="이번 달 매출" only %}
</div>
{% endblock body %}
```

---

## Summary of Changes

| # | Convention | What Changed |
|---|-----------|-------------|
| 1 | Hardcoded values -> CSS Custom Property tokens | 모든 하드코딩된 색상/크기 값을 `var()` 폴백이 포함된 디자인 토큰으로 교체 |
| 2 | External style override -> Design system modifier | `orders.css`의 `.btn-primary` 오버라이드를 제거하고 `_btn_primary_sm.html` modifier 생성 |
| 3 | Flat template -> Component folders | `stat-card`를 `design_system/cards/`로 추출, BEM 네이밍 적용 |
| 4 | `{% include %}` without `only` -> ADD `only` | 모든 디자인 시스템 include에 `only` 키워드 추가 |
| 5 | `{% endblock %}` -> `{% endblock body %}` | 닫는 endblock에 블록명 명시 |
