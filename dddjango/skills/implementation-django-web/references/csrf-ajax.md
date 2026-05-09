# CSRF, AJAX, Security, And Verification

Use this reference for CSRF, AJAX/HTMX request safety, XSS, secure cookies, middleware, and web verification.

## CSRF And AJAX

- Keep `CsrfViewMiddleware` enabled unless there is a narrow, documented exception.
- Use `{% csrf_token %}` in POST forms.
- For AJAX or HTMX requests that mutate state, send the CSRF token using the project’s established header or form pattern.
- Use `@csrf_exempt` only for tightly scoped cases with a clear alternative protection.
- Be careful with `CSRF_COOKIE_HTTPONLY`: Django notes it has limited practical CSRF protection value and can complicate AJAX token access.

## XSS And Safe Output

- Rely on Django template autoescaping.
- Avoid `|safe`, `mark_safe()`, and raw HTML injection unless the content is trusted and sanitized.
- Do not put untrusted values into JavaScript contexts without the project’s escaping pattern.

## Middleware And Security Settings

- Preserve middleware ordering constraints for security, sessions, CSRF, auth, messages, and frame options.
- Keep security settings aligned with deployment: HTTPS redirect, secure cookies, HSTS, content type sniffing, and frame options.
- Use `check --deploy` when security settings are changed and a deploy check is practical.

## Verification

- For template changes, check render paths and context variable names.
- For form or HTMX changes, check GET, valid POST, invalid POST, auth/permission, CSRF behavior, and redirect/fragment behavior.
- For security-sensitive changes, include a deploy/security check or explain why it was not run.
- Report only checks actually executed. Do not claim browser, render, `collectstatic`, or security checks passed without evidence.
