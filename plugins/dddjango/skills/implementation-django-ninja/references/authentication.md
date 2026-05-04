# 인증과 보안 레퍼런스

> Django Ninja 공식 문서 기반 레퍼런스. 내장 인증 클래스, 인증 범위, 다중 인증, 비동기 인증, CSRF 관리를 다룬다.

---

## 1. 인증 기본 개념

Django Ninja에서 인증은 API 작업에 `auth` 객체를 정의하여 동작한다. `auth`가 지정되면 클라이언트는 인증을 통과해야 하며, 실패 시 HTTP 401 에러가 반환된다. `authenticate()` 메서드가 반환하는 값은 `request.auth`를 통해 접근할 수 있다.

---

## 2. 내장 인증 클래스

### APIKeyQuery

쿼리 파라미터에서 API 키를 추출한다:

```python
from ninja.security import APIKeyQuery
from someapp.models import Client

class ApiKey(APIKeyQuery):
    param_name = "api_key"  # 쿼리 파라미터 이름

    def authenticate(self, request, key):
        try:
            return Client.objects.get(key=key)
        except Client.DoesNotExist:
            pass  # None 반환 -> 401

@api.get("/apikey", auth=ApiKey())
def apikey(request):
    return f"Hello {request.auth}"
```

### APIKeyHeader

요청 헤더에서 API 키를 검증한다:

```python
from ninja.security import APIKeyHeader

class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"  # 헤더 이름

    def authenticate(self, request, key):
        if key == "supersecret":
            return key

@api.get("/headerkey", auth=ApiKey())
def apikey(request):
    return f"Token = {request.auth}"
```

### APIKeyCookie

쿠키에서 API 키를 가져온다:

```python
from ninja.security import APIKeyCookie

class CookieKey(APIKeyCookie):
    def authenticate(self, request, key):
        if key == "supersecret":
            return key

@api.get("/cookiekey", auth=CookieKey())
def apikey(request):
    return f"Token = {request.auth}"
```

### HttpBearer

`Authorization: Bearer <token>` 헤더를 통한 토큰 기반 인증:

```python
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "supersecret":
            return token

@api.get("/bearer", auth=AuthBearer())
def bearer(request):
    return {"token": request.auth}
```

### HttpBasicAuth

사용자명/비밀번호 기반 인증:

```python
from ninja.security import HttpBasicAuth

class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        if username == "admin" and password == "secret":
            return username

@api.get("/basic", auth=BasicAuth())
def basic(request):
    return {"httpuser": request.auth}
```

### SessionAuth 계열

Django 세션 기반 인증 클래스 3종:

```python
from ninja.security import SessionAuth, SessionAuthSuperUser, SessionAuthIsStaff

# SessionAuth: 인증된 모든 사용자
@api.get("/protected", auth=SessionAuth())
def protected_view(request):
    return {"user": request.auth.username}

# SessionAuthSuperUser: 슈퍼유저만
@api.get("/admin-only", auth=SessionAuthSuperUser())
def admin_view(request):
    return {"message": "Hello superuser!"}

# SessionAuthIsStaff: 스태프 또는 슈퍼유저
@api.get("/staff-area", auth=SessionAuthIsStaff())
def staff_view(request):
    return {"message": "Hello staff member!"}
```

---

## 3. 인증 범위 (Scope)

### Global 수준 (전체 API)

`NinjaAPI` 생성자에서 설정하면 모든 작업에 인증이 적용된다:

```python
from ninja import NinjaAPI

api = NinjaAPI(auth=GlobalAuth())
```

### Router 수준

라우터의 모든 작업에 인증을 적용한다:

```python
# add_router()에서 지정
api.add_router("/events/", events_router, auth=BasicAuth())

# Router 생성자에서 지정
router = Router(auth=BasicAuth())
```

### Operation 수준 (개별 엔드포인트)

개별 엔드포인트에서 글로벌/라우터 설정을 오버라이드한다:

```python
@api.get("/specific", auth=AuthBearer())
def specific_endpoint(request):
    return {"data": "protected"}
```

---

## 4. auth=None 인증 면제

글로벌 또는 라우터 수준 인증이 설정된 상태에서 특정 엔드포인트를 인증에서 제외할 때 사용한다:

```python
api = NinjaAPI(auth=GlobalAuth())

# 이 엔드포인트는 인증 없이 접근 가능
@api.post("/token", auth=None)
def get_token(request):
    pass
```

이 패턴은 로그인/토큰 발급 엔드포인트에서 자주 사용된다.

---

## 5. 다중 인증

리스트로 여러 인증기를 전달하면 순차적으로 검증하여 하나라도 성공하면 통과한다:

```python
from ninja.security import APIKeyQuery, APIKeyHeader

class QueryKey(APIKeyQuery):
    param_name = "api_key"
    def authenticate(self, request, key):
        if key == "supersecret":
            return key

class HeaderKey(APIKeyHeader):
    param_name = "X-API-Key"
    def authenticate(self, request, key):
        if key == "supersecret":
            return key

@api.get("/multiple", auth=[QueryKey(), HeaderKey()])
def multiple(request):
    return f"Token = {request.auth}"
```

Ninja는 인증기를 순서대로 확인하며, 첫 번째로 성공한 인증기의 반환값이 `request.auth`에 설정된다.

---

## 6. 커스텀 인증 함수

클래스 대신 일반 함수를 인증기로 사용할 수 있다. truthy 값을 반환하면 인증 성공이다:

```python
def ip_whitelist(request):
    if request.META["REMOTE_ADDR"] == "8.8.8.8":
        return "8.8.8.8"

@api.get("/ipwhitelist", auth=ip_whitelist)
def ipwhitelist(request):
    return f"Authenticated client, IP = {request.auth}"
```

---

## 7. Async 인증

비동기 인증 함수를 사용할 수 있다:

```python
async def async_auth(request):
    # 비동기 인증 로직
    ...

@api.get("/pets", auth=async_auth)
def pets(request):
    ...
```

비동기 인증기는 동기 뷰와 비동기 뷰 모두에서 사용할 수 있다.

---

## 8. 커스텀 예외 처리

인증 실패 시 커스텀 응답을 반환할 수 있다:

```python
class InvalidToken(Exception):
    pass

@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(
        request,
        {"detail": "Invalid token supplied"},
        status=401
    )

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token != "supersecret":
            raise InvalidToken
        return token
```

---

## 9. CSRF 자동 관리

### 기본 동작

Django Ninja는 기본적으로 모든 작업에서 CSRF 보호가 **비활성화**되어 있다. 단, 쿠키 기반 인증을 사용하면 **자동으로 CSRF 보호가 활성화**된다.

### 쿠키 기반 인증에서의 자동 CSRF

```python
from ninja import NinjaAPI
from ninja.security import APIKeyCookie

class CookieAuth(APIKeyCookie):
    def authenticate(self, request, key):
        return key == "test"

api = NinjaAPI(auth=CookieAuth())  # CSRF 자동 활성화
```

Django 기본 인증(세션 기반)에서도 자동 활성화된다:

```python
from ninja import NinjaAPI
from ninja.security import django_auth

api = NinjaAPI(auth=django_auth)  # CSRF 자동 활성화
```

### 비쿠키 인증에서의 CSRF 불필요

`Authorization: Bearer` 헤더 같은 비쿠키 인증 방식은 요청에 자동으로 포함되지 않으므로 CSRF 공격에 본질적으로 안전하다.

### CSRF 토큰 설정 엔드포인트

프론트엔드에 CSRF 토큰을 제공하는 엔드포인트:

```python
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

@api.post("/csrf", auth=None)  # 글로벌 쿠키 인증 사용 시 auth=None 필요
@ensure_csrf_cookie
@csrf_exempt
def get_csrf_token(request):
    return HttpResponse()
```

주의사항:
- 라우트 데코레이터가 `ensure_csrf_cookie` **앞에** 위치해야 한다
- `csrf_exempt` 데코레이션이 필요하다
- Django `HttpResponse` 객체만 사용 가능하다
- 글로벌 쿠키 인증 사용 시 `auth=None`으로 면제해야 한다

### CORS 고려사항

프론트엔드와 API가 분리 배포된 경우 [django-cors-headers](https://github.com/adamchainz/django-cors-headers)를 사용하여 크로스 오리진 CSRF 쿠키 요구사항을 처리한다.

---

## 10. OpenAPI 통합

인증 클래스는 자동으로 Swagger UI 문서에 적절한 인증 프롬프트를 생성하여, API 테스트 시 인증 정보를 입력할 수 있는 인터페이스를 제공한다.
