# CSRF, AJAX, Security, And Verification

이 reference는 CSRF, AJAX/HTMX request safety, XSS, secure cookies, middleware, web verification을 다룬다.

## CSRF And AJAX

- 좁고 문서화된 예외가 없으면 `CsrfViewMiddleware`를 유지한다.
- POST form에는 `{% csrf_token %}`을 사용한다.
- State-changing AJAX 또는 HTMX request는 프로젝트의 established header 또는 form pattern으로 CSRF token을 보낸다.
- `@csrf_exempt`는 clear alternative protection이 있는 tightly scoped case에만 사용한다.
- `CSRF_COOKIE_HTTPONLY`는 AJAX token access를 복잡하게 만들 수 있으므로 프로젝트 요구와 Django 문서 caveat를 함께 고려한다.

## XSS And Safe Output

- Django template autoescaping을 기본으로 둔다.
- Content가 trusted/sanitized가 아니면 `|safe`, `mark_safe()`, raw HTML injection을 피한다.
- Untrusted value를 JavaScript context에 넣어야 하면 프로젝트 escaping pattern을 따른다.

## Middleware And Security Settings

- Security, sessions, CSRF, auth, messages, frame options middleware ordering constraint를 보존한다.
- HTTPS redirect, secure cookies, HSTS, content type sniffing, frame options 같은 security setting은 deployment와 맞춘다.
- Security setting을 바꾸고 deploy check가 실용적이면 `check --deploy`를 실행한다.

## SQL Injection And Raw Queries

- View context preparation에는 ORM query API를 선호한다.
- Web view 또는 selector가 `raw()`나 `extra()`를 써야 하면 user input을 SQL string에 보간하지 않는다.
- Raw SQL은 parameterized value를 사용하고, deeper query design, QuerySet/Manager choice, DB performance work는 `implementation-django`로 넘긴다.

## Verification

- Template 변경은 render path와 context variable name을 확인한다.
- Form 또는 HTMX 변경은 GET, valid POST, invalid POST, auth/permission, CSRF behavior, redirect/fragment behavior를 확인한다.
- Security-sensitive 변경은 deploy/security check를 포함하거나 실행하지 않은 이유를 설명한다.
- 실제 실행한 check만 보고한다. Browser, render, `collectstatic`, security check를 증거 없이 통과했다고 말하지 않는다.
