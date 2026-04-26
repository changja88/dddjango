# 보안

## Django 내장 보안 기능 [DDoc] [OWASP]

| 공격 유형 | Django 방어 | 주의사항 |
|-----------|------------|----------|
| **CSRF** | `CsrfViewMiddleware` + `{% csrf_token %}` | `@csrf_exempt`는 극히 제한적으로 사용 |
| **XSS** | 템플릿 자동 이스케이핑 | `|safe`, `mark_safe()` 사용 시 주의 |
| **SQL Injection** | ORM이 파라미터화 쿼리 사용 | `raw()`, `extra()`에서 직접 문자열 보간 금지 |
| **Clickjacking** | `XFrameOptionsMiddleware` | `X_FRAME_OPTIONS = "DENY"` 설정 |

## 보안 설정 체크리스트 [DDoc] [OWASP]

```python
# config/settings/production.py

# HTTPS 강제
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 쿠키 보안
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True  # 주의: Django 공식 문서는 CSRF에 대한 실질적 보호 효과가 없다고 명시. 보안 감사 요구사항이 있을 때만 사용. AJAX 사용 시 문제 발생 가능

# 콘텐츠 보안
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Django 보안 체크 실행
# python manage.py check --deploy
```

## Raw SQL 안전하게 사용 [DDoc]

```python
# 나쁜 예: 문자열 보간으로 SQL Injection 취약
Model.objects.raw(f"SELECT * FROM app_model WHERE name = '{user_input}'")

# 좋은 예: 파라미터화 쿼리
Model.objects.raw("SELECT * FROM app_model WHERE name = %s", [user_input])

# 나쁜 예: extra()에서 직접 보간
queryset.extra(where=[f"name = '{user_input}'"])

# 좋은 예: extra()에서 파라미터 사용
queryset.extra(where=["name = %s"], params=[user_input])
```

## 인증과 인가 [DDoc]

```python
# 뷰 레벨 인증 (FBV)
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required("articles.change_article", raise_exception=True)
def edit_article(request, pk):
    ...

# 뷰 레벨 인증 (CBV)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class EditArticleView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "articles.change_article"
    ...
```
