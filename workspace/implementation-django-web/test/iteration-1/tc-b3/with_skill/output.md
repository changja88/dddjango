# Review: Dashboard & Order Detail Views

## What the code does right

- Both views correctly use `TemplateView` with `get_context_data` for page rendering, which is the standard Django page view pattern.
- `DashboardView` uses the Internal API Client pattern consistently, calling multiple API endpoints through a single `InternalAPIClient` instance.
- `OrderDetailView` uses the direct service call pattern via `OrderService`, which is the standard approach for monolithic Django projects.
- Both views call `super().get_context_data(**kwargs)` before adding custom context, preserving the parent context chain.

---

## Findings

### F1. Missing `LoginRequiredMixin` on `DashboardView`

```
[TemplateView missing LoginRequiredMixin for authenticated pages]
-- DashboardView renders revenue, orders, and notifications -- data that is inherently user-specific and sensitive. The view must require authentication. LoginRequiredMixin should be placed before TemplateView in the MRO.
```

### F2. Missing `LoginRequiredMixin` on `OrderDetailView`

```
[TemplateView missing LoginRequiredMixin for authenticated pages]
-- OrderDetailView displays order details and history, which are private data tied to a specific order/user. Without LoginRequiredMixin, unauthenticated users can access this page.
```

### F3. Missing error handling in `DashboardView` (Internal API Client calls)

```
[Missing error handling when view calls external services/APIs]
-- DashboardView makes three HTTP calls via InternalAPIClient (revenue, orders, notifications). Any of these can raise requests.HTTPError or connection errors. If one fails, the entire page breaks with a 500 error. Each call should be wrapped in try/except to provide graceful degradation with fallback values and an error message for the user.
```

### F4. Missing error handling in `OrderDetailView` (service calls)

```
[Missing error handling when view calls external services/APIs]
-- OrderDetailView calls OrderService.get_detail() and OrderService.get_history(). If the order does not exist or the service raises an exception, the user sees a raw 500 error instead of a meaningful error page. These calls should be wrapped in try/except.
```

### F5. Missing `InternalAPIClient` import in `DashboardView`

```
[Convention] -- DashboardView uses InternalAPIClient but does not import it. The import should be at module level (e.g., from web.api_client import InternalAPIClient). This is not just a linting issue; the view will raise a NameError at runtime.
```

### F6. Inline import in `OrderDetailView`

```
[Convention] -- OrderDetailView imports OrderService inside get_context_data with a function-level "from orders.services import OrderService". Per the reference pattern, service imports should be at the top of the module, not inside a method. Function-level imports obscure dependencies and make the module harder to understand at a glance.
```

---

## Review Checklist Verification

| # | Check Item | Result |
|---|-----------|--------|
| 1 | Hardcoded static file paths instead of `{% static %}` | N/A -- no templates in scope |
| 2 | `{{ value }}` inside `<script>` without `json_script` (XSS risk) | N/A -- no templates in scope |
| 3 | CDN scripts without `integrity` and `crossorigin` attributes (SRI) | N/A -- no templates in scope |
| 4 | Missing CSRF token in AJAX POST/PUT/PATCH/DELETE requests | N/A -- no AJAX in scope |
| 5 | `{% include %}` without `only` keyword | N/A -- no templates in scope |
| 6 | Hardcoded color/spacing values instead of design tokens | N/A -- no CSS in scope |
| 7 | External CSS overriding design system component styles | N/A -- no CSS in scope |
| 8 | Inline `<style>` in templates | N/A -- no templates in scope |
| 9 | Inline app logic in `<script>` | N/A -- no templates in scope |
| 10 | Missing `{{ block.super }}` where parent block content should be preserved | N/A -- no templates in scope |
| 11 | `{% load %}` missing in child template | N/A -- no templates in scope |
| 12 | TemplateView missing `LoginRequiredMixin` for authenticated pages | **FOUND** -- F1, F2 |
| 13 | Missing error handling when view calls external services/APIs | **FOUND** -- F3, F4 |
| 14 | No `{% block %}` name in closing `{% endblock %}` tag | N/A -- no templates in scope |
| 15 | Design token without `var()` fallback value | N/A -- no CSS in scope |

---

## Summary

The code has two high-impact issues that apply to both views:

1. **No access control** -- Both views serve authenticated user data but lack `LoginRequiredMixin`, leaving them accessible to anonymous users.
2. **No error handling** -- `DashboardView` makes three HTTP calls and `OrderDetailView` makes two service calls, all without try/except. Any failure results in an unhandled 500 error.

Additionally, there are two code hygiene issues: a missing import (`InternalAPIClient`) that will cause a runtime `NameError`, and a function-level import (`OrderService`) that should be at module level.
