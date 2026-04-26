# Design System Review: btn-primary

## Positive Aspects

- Component file naming follows convention: `_btn_primary.html` (underscore prefix for partial), `btn-primary.css` (kebab-case for CSS).
- File co-location is correct: CSS and HTML partial reside in the same `design_system/buttons/` folder.
- Focus state is defined on the button, supporting keyboard navigation accessibility.
- Transition on hover provides visual feedback.

---

## Findings

### F1. Hardcoded color/spacing values instead of design tokens (`var()`)

```
[Convention] Hardcoded color/spacing values instead of design tokens
```

`btn-primary.css` uses raw hex values and pixel sizes throughout instead of referencing CSS Custom Property tokens. The design system reference defines a 3-layer token structure (primitive, semantic, component) and states: "all styles must reference tokens via `var()`; never use hardcoded values directly."

**Affected code:**

```css
.btn-primary {
    background-color: #3b82f6;        /* should be var(--btn-bg, #3b82f6) */
    color: white;                      /* should be var(--btn-text, #ffffff) */
    padding: 8px 16px;                /* should use spacing tokens */
    border-radius: 4px;              /* should use radius tokens */
    font-size: 14px;                  /* should use text size tokens */
}
.btn-primary:hover {
    background-color: #1d4ed8;        /* should be var(--btn-bg-hover, #1d4ed8) */
}
.btn-primary:focus {
    outline: 2px solid #3b82f6;       /* should use focus ring token */
}
```

All values should use component-layer tokens that reference semantic-layer tokens, with hardcoded fallbacks in `var()`. For example: `background-color: var(--btn-bg, #3b82f6);`.

> Reference: design-system.md, Section 1 (3-layer token structure, var() fallback values)

---

### F2. Design token without `var()` fallback value

```
[Convention] Design token without var() fallback value
```

This finding is preemptive: when the code is updated to use tokens, each `var()` call must include a fallback value. For example `var(--btn-bg, #3b82f6)` rather than just `var(--btn-bg)`. This ensures the component renders correctly even if the token layer has not been loaded.

> Reference: design-system.md, Section 1 (var() fallback values)

---

### F3. `{% include %}` without `only` keyword (implicit context leaking)

```
[Convention] {% include %} without "only" keyword — implicit context leaking
```

In `order_list.html`:

```htmldjango
{% include "design_system/buttons/_btn_primary.html" with label="new order" %}
```

The `only` keyword is missing. Without it, the entire parent template context is passed into the component, creating implicit dependencies and making the component interface opaque. Design system components must use `only` to restrict context to explicitly passed variables.

**Should be:**

```htmldjango
{% include "design_system/buttons/_btn_primary.html" with label="new order" only %}
```

> Reference: design-system.md, Section 6 (only keyword); template-architecture.md, Section 4 (context isolation)

---

### F4. External CSS overriding design system component styles

```
[Convention] External CSS overriding design system component styles
```

In `order_list.html`:

```html
<style>
.order-page .btn-primary {
    font-size: 12px;
    padding: 4px 8px;
}
</style>
```

The design system reference explicitly prohibits overriding component styles from external CSS. This exact pattern (`.order-page .btn-primary { ... }`) is listed as the "bad example" in the reference. When a size or color variant is needed, a modifier class should be created inside the design system itself (e.g., `.btn-primary-sm`), not overridden from consuming pages.

**Should be replaced with a design system modifier:**

```css
/* design_system/buttons/btn-primary.css */
.btn-primary-sm {
    font-size: var(--text-sm, 0.875rem);
    padding: var(--spacing-xs, 0.25rem) var(--spacing-sm, 0.5rem);
}
```

```htmldjango
{% include "design_system/buttons/_btn_primary.html" with label="new order" size="sm" only %}
```

> Reference: design-system.md, Section 6 (style override prohibition, modifier pattern)

---

### F5. Inline `<style>` in template (should be separate CSS file)

```
[Convention] Inline <style> in template — should be a separate CSS file
```

In `order_list.html`, styles are written inline with a `<style>` tag. The asset management reference states: "Writing `<style>` inline in HTML templates is prohibited -- separate into a dedicated `.css` file." Even if the style override in F4 is removed, any page-specific CSS should live in a separate file such as `orders/static/orders/css/order_list.css` and be loaded via `{% static %}`.

> Reference: asset-management.md, Section 4 (CSS management rules); Section 6 (`<style>` comment rules)

---

### F6. Missing required-variable documentation in component partial

```
[Convention] Component partial missing required-variable documentation
```

`_btn_primary.html` does not document its required variables at the top. The template architecture reference requires components to declare their dependencies using a Django comment:

```htmldjango
{# Required variables: label (str), disabled (bool, optional) #}
<button class="btn-primary" {% if disabled %}disabled{% endif %}>
    {{ label }}
</button>
```

> Reference: template-architecture.md, Section 4 (component required-variable documentation)

---

## Checklist Verification

The following is the complete review checklist with each item verified:

| # | Check Item | Result |
|---|-----------|--------|
| 1 | Hardcoded static file paths instead of `{% static %}` | Not applicable (no static file references in provided code) |
| 2 | `{{ value }}` inside `<script>` without `json_script` (XSS risk) | Not applicable (no script tags with template variables) |
| 3 | CDN scripts without `integrity` and `crossorigin` attributes (SRI) | Not applicable (no CDN scripts) |
| 4 | Missing CSRF token in AJAX POST/PUT/PATCH/DELETE requests | Not applicable (no AJAX requests) |
| 5 | `{% include %}` without `only` keyword | **FOUND** -- F3 |
| 6 | Hardcoded color/spacing values instead of design tokens (`var()`) | **FOUND** -- F1 |
| 7 | External CSS overriding design system component styles | **FOUND** -- F4 |
| 8 | Inline `<style>` in templates | **FOUND** -- F5 |
| 9 | Inline app logic in `<script>` | Not applicable (no script tags) |
| 10 | Missing `{{ block.super }}` where parent block content should be preserved | Not applicable (no block extension in provided code) |
| 11 | `{% load %}` missing in child template | Not applicable (no template tags requiring load) |
| 12 | TemplateView missing `LoginRequiredMixin` for authenticated pages | Not applicable (no view code provided) |
| 13 | Missing error handling when view calls external services/APIs | Not applicable (no view code provided) |
| 14 | No `{% block %}` name in closing `{% endblock %}` tag | Not applicable (no block definitions in provided code) |
| 15 | Design token without `var()` fallback value | **FOUND** (preemptive) -- F2 |

---

## Summary

Six findings identified, four of which are actionable issues in the current code:

1. **F1 (High)** -- All CSS values are hardcoded instead of using design tokens via `var()`.
2. **F3 (Medium)** -- `{% include %}` missing `only` keyword, leaking parent context into the component.
3. **F4 (High)** -- Page-level CSS overrides design system component styles directly, violating the modifier pattern.
4. **F5 (Medium)** -- Inline `<style>` tag in template instead of a separate CSS file.
5. **F2 (Low)** -- Preemptive: ensure `var()` calls include fallback values when tokens are adopted.
6. **F6 (Low)** -- Component partial lacks required-variable documentation comment.

The most impactful changes are adopting design tokens in the button CSS (F1) and replacing the external style override with a proper design system modifier (F4). These two changes together enforce the principle that design system components own their own styles and all visual values flow from a single token source.
