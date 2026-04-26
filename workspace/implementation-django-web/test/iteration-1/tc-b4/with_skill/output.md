# Review: dashboard/chart_section/chart_section.html

## Review Checklist

- [ ] Hardcoded static file paths instead of `{% static %}` -- N/A (no static file references in this template)
- [x] `{{ value }}` inside `<script>` without `json_script` (XSS risk) -- **FOUND**
- [x] CDN scripts without `integrity` and `crossorigin` attributes (SRI) -- **FOUND**
- [x] Missing CSRF token in AJAX POST/PUT/PATCH/DELETE requests -- **FOUND**
- [ ] `{% include %}` without `only` keyword (implicit context leaking) -- N/A (no includes)
- [ ] Hardcoded color/spacing values instead of design tokens (`var()`) -- N/A (no CSS in this template)
- [ ] External CSS overriding design system component styles -- N/A
- [ ] Inline `<style>` in templates (should be separate CSS file) -- N/A (no inline styles)
- [x] Inline app logic in `<script>` (should be separate JS file) -- **FOUND**
- [ ] Missing `{{ block.super }}` where parent block content should be preserved -- N/A (no block inheritance visible)
- [ ] `{% load %}` missing in child template (not inherited from parent) -- N/A (no template tags used)
- [ ] TemplateView missing `LoginRequiredMixin` for authenticated pages -- N/A (view not provided, but `user.profile` access implies authentication required)
- [ ] Missing error handling when view calls external services/APIs -- N/A (view not provided)
- [ ] No `{% block %}` name in closing `{% endblock %}` tag -- N/A (no blocks in this template)
- [ ] Design token without `var()` fallback value -- N/A (no CSS)

---

## Findings

### 1. XSS: `{{ chart_data|safe }}` inside `<script>` -- use `json_script` instead

```
[Convention] {{ value }} inside <script> without json_script (XSS risk) -- chart_data is rendered
directly into a JavaScript assignment using the |safe filter. If chart_data contains user-controlled
content (e.g., dataset labels from user input), an attacker can inject arbitrary JavaScript. The |safe
filter explicitly disables Django's auto-escaping, making this especially dangerous. The Django-idiomatic
approach is to use the json_script filter, which outputs the data into a separate
<script type="application/json"> tag with proper escaping of <, >, & characters.
```

Affected code:
```javascript
window.__CHART_DATA__ = {{ chart_data|safe }};
```

The `window.__` global variable assignment pattern combined with `|safe` is explicitly warned against in the asset management reference: "window.__ 전역 변수에 직접 할당하는 패턴은 XSS 취약점이 있으므로 사용하지 않는다."

---

### 2. XSS: `{{ user.profile.theme }}` and `{{ user.profile.locale }}` inside `<script>` -- use `json_script` or `escapejs`

```
[Convention] {{ value }} inside <script> without json_script (XSS risk) -- Django template variables
are interpolated directly into JavaScript string literals. If user.profile.theme contains a value like
'); maliciousCode(); // the attacker can break out of the string and execute arbitrary code.
At minimum, |escapejs must be used for string interpolation. For structured data, json_script is
preferred as it eliminates the entire class of injection vulnerabilities.
```

Affected code:
```javascript
window.__USER_PREFS__ = {
    theme: '{{ user.profile.theme }}',
    locale: '{{ user.profile.locale }}'
};
```

---

### 3. CDN script missing SRI attributes (`integrity`, `crossorigin`)

```
[Convention] CDN scripts without integrity and crossorigin attributes (SRI) -- The Chart.js CDN script
tag has no integrity or crossorigin attributes. If the CDN is compromised or serves a tampered file,
malicious code will execute in the user's browser. Subresource Integrity (SRI) ensures the browser
verifies the file's hash before execution, preventing supply-chain attacks.
```

Affected code:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
```

---

### 4. AJAX POST request missing CSRF token

```
[Convention] Missing CSRF token in AJAX POST/PUT/PATCH/DELETE requests -- The fetch() call to
/api/stats/revenue/ uses method POST but does not include an X-CSRFToken header. Django's CSRF
middleware will reject this request with a 403 Forbidden response. The CSRF token must be read from
the csrftoken cookie and sent as the X-CSRFToken header. Additionally, mode: "same-origin" should be
set as recommended by Django's documentation.
```

Affected code:
```javascript
fetch('/api/stats/revenue/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ period: 'monthly' })
})
```

---

### 5. Inline app logic in `<script>` -- should be a separate JS file

```
[Convention] Inline app logic in <script> (should be separate JS file) -- The template contains
substantial application logic: Chart.js initialization, configuration, event listener binding, and
a fetch() call with response handling. This violates the separation of concerns rule. App scripts
belong in static/<app>/js/<component>.js files. The only JavaScript that should appear inline in
templates is server data transfer via json_script. Extracting the logic to a static JS file also
enables browser caching, linting, testing, and CSP compliance without unsafe-inline.
```

Affected code: the entire second `<script>` block (lines 8-25 of the script section).

---

### 6. `updateChart` function referenced but not defined

```
[Convention] -- The .then(data => updateChart(data)) callback references an updateChart function that
is not defined anywhere in this template. This will cause a ReferenceError at runtime when the refresh
button is clicked. This is likely a symptom of the inline script problem: if the chart logic were in
a dedicated JS file, the function would be defined alongside the chart initialization.
```

---

### 7. `refresh-btn` element referenced but not present in the template

```
[Convention] -- document.getElementById('refresh-btn') targets an element that does not exist in
this template's HTML. This will cause a TypeError (Cannot read properties of null) when attempting
to call addEventListener on null. The element is presumably defined in a parent or sibling template,
which creates a fragile implicit coupling. If this component is included via {% include %}, the
dependency on an external DOM element should be documented or the button should be part of this
component.
```

---

## Summary

This template has three security vulnerabilities (XSS via `|safe` and unescaped template variables in JavaScript, missing SRI on CDN, missing CSRF token on POST) and one structural issue (inline application logic). The XSS issues are the highest priority -- the `{{ chart_data|safe }}` pattern is the most dangerous because `|safe` explicitly disables all escaping, and `chart_data` likely contains strings (labels, tooltips) that could be user-influenced. The missing CSRF token will cause the refresh functionality to fail entirely in any Django project with default middleware.
