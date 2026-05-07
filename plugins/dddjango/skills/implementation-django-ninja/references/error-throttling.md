# 에러 처리와 쓰로틀링 레퍼런스

## 1. 내장 예외 클래스

Django Ninja는 다음 내장 예외를 제공한다.

| 예외 | 기본 상태 코드 | 설명 |
|---|---|---|
| `AuthenticationError` | 401 | 인증 데이터가 유효하지 않을 때 발생 |
| `AuthorizationError` | 403 | 인증은 되었으나 리소스 접근 권한이 없을 때 발생 |
| `ValidationError` | 422 | 요청 데이터가 검증에 실패했을 때 발생 |
| `HttpError` | 지정값 | 코드 어디서든 HTTP 에러를 던질 수 있음 |
| `django.http.Http404` | 404 | Django 표준 404 예외 |

### HttpError 사용

커스텀 핸들러 없이 직접 HTTP 에러를 던진다.

```python
from ninja.errors import HttpError

@api.get("/some/resource")
def some_operation(request):
    if True:
        raise HttpError(503, "Service Unavailable. Please retry later.")
```

## 2. @api.exception_handler() 데코레이터

커스텀 예외 핸들러를 등록한다. 핸들러 함수는 `request`와 `exc` 두 파라미터를 받고, HTTP 응답을 반환해야 한다.

```python
from ninja import NinjaAPI

api = NinjaAPI()

class ServiceUnavailableError(Exception):
    pass

@api.exception_handler(ServiceUnavailableError)
def service_unavailable(request, exc):
    return api.create_response(
        request,
        {"message": "Please retry later"},
        status=503,
    )

@api.get("/service")
def some_operation(request):
    if random.choice([True, False]):
        raise ServiceUnavailableError()
    return {"message": "Hello"}
```

## 3. RFC 9457 Problem Details 에러 응답

모든 API 에러 응답은 RFC 9457 Problem Details 형식을 따른다. Content-Type은 `application/problem+json`.

```python
from ninja import NinjaAPI, Schema
from django.http import JsonResponse


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


@api.exception_handler(Exception)
def problem_details_handler(request, exc):
    """모든 에러를 RFC 9457 형식으로 반환"""
    if isinstance(exc, HttpError):
        return JsonResponse(
            ProblemDetail(
                title=str(exc),
                status=exc.status_code,
                detail=str(exc),
                instance=request.path,
            ).model_dump(),
            status=exc.status_code,
            content_type="application/problem+json",
        )
    return JsonResponse(
        ProblemDetail(
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred.",
            instance=request.path,
        ).model_dump(),
        status=500,
        content_type="application/problem+json",
    )


# 도메인별 Problem Detail 확장
class InsufficientBalanceError(Exception):
    def __init__(self, balance: float, cost: float):
        self.balance = balance
        self.cost = cost


@api.exception_handler(InsufficientBalanceError)
def handle_insufficient_balance(request, exc):
    return JsonResponse(
        {
            "type": "https://api.example.com/probs/insufficient-balance",
            "title": "Insufficient Balance",
            "status": 403,
            "detail": f"Your balance is {exc.balance}, but this costs {exc.cost}.",
            "instance": request.path,
            "balance": exc.balance,
            "cost": exc.cost,
        },
        status=403,
        content_type="application/problem+json",
    )
```

---

## 4. api.create_response()

예외 핸들러 내에서 JSON 응답을 생성하는 헬퍼 메서드이다. `request`, `data`, `status` 파라미터를 받는다.

```python
@api.exception_handler(MyCustomError)
def handle_my_error(request, exc):
    response = api.create_response(
        request,
        {
            "type": "https://api.example.com/probs/custom-error",
            "title": "Custom Error",
            "status": 400,
            "detail": str(exc),
            "instance": request.path,
            "code": "CUSTOM_ERROR",
        },
        status=400,
    )
    response["Content-Type"] = "application/problem+json"
    return response
```

## 5. ValidationError 커스터마이징

기본 422 응답을 커스텀할 수 있다.

```python
from django.http import HttpResponse
from ninja.errors import ValidationError

@api.exception_handler(ValidationError)
def validation_errors(request, exc):
    return HttpResponse("Invalid input", status=422)
```

고급 제어가 필요하면 `NinjaAPI`를 서브클래싱하여 `validation_error_from_error_contexts()` 메서드를 오버라이드한다.

```python
from ninja import NinjaAPI

class CustomAPI(NinjaAPI):
    def validation_error_from_error_contexts(self, error_contexts):
        # 커스텀 검증 에러 로직
        return super().validation_error_from_error_contexts(error_contexts)
```

## 6. Debug vs Production 모드

| 모드 | 동작 |
|---|---|
| `settings.DEBUG = True` | 처리되지 않은 예외의 트레이스백을 plain text로 반환 |
| `settings.DEBUG = False` | Django 표준 예외 처리 메커니즘 적용 (로깅, 관리자 알림) |

## 7. 쓰로틀링 (Throttling)

요청 속도 제한 기능이다. Django REST Framework의 쓰로틀링과 유사한 방식으로 동작한다.

### 6.1 Rate 형식

`요청수/시간단위` 패턴을 사용한다.

| 시간 단위 | 약어 |
|---|---|
| 초 | `s`, `sec` |
| 분 | `m`, `min` |
| 시간 | `h`, `hour` |
| 일 | `d`, `day` |

예시: `100/5m`, `100/300s`, `100/300`은 모두 "5분당 100 요청"을 의미한다.

### 6.2 3가지 내장 Throttler

| 클래스 | 식별 기준 | 설명 |
|---|---|---|
| `AnonRateThrottle` | IP 주소 | 비인증 사용자를 IP로 식별하여 제한 |
| `AuthRateThrottle` | `sha256(str(request.auth))` | Django Ninja 인증 기반, 비인증 시 IP 폴백 |
| `UserRateThrottle` | User ID | Django 인증 사용자를 ID로 식별, 비인증 시 IP 폴백 |

### 6.3 Global 쓰로틀링

NinjaAPI 인스턴스 레벨에서 전역 설정한다.

```python
from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

api = NinjaAPI(
    throttle=[
        AnonRateThrottle('10/s'),
        AuthRateThrottle('100/s'),
    ],
)
```

### 6.4 Router 쓰로틀링

라우터 단위로 설정한다.

```python
from ninja.throttling import AnonRateThrottle
from ninja import Router

# add_router 방식
api.add_router(
    '/sensitive',
    'myapp.api.router',
    throttle=AnonRateThrottle('100/m'),
)

# Router 인스턴스 방식
router = Router(throttle=[AnonRateThrottle('1000/h')])
```

### 6.5 Operation 쓰로틀링

개별 엔드포인트에 설정한다.

```python
from ninja.throttling import UserRateThrottle

@api.get('/some', throttle=[UserRateThrottle('10000/d')])
def some(request):
    ...
```

### 6.6 커스텀 Throttle

`BaseThrottle`을 상속하여 `allow_request()` 메서드를 구현한다. `True`이면 허용, `False`이면 거부이다.

```python
from ninja.throttling import AnonRateThrottle

class NoReadsThrottle(AnonRateThrottle):
    """GET 요청은 쓰로틀링하지 않는다"""

    def allow_request(self, request):
        if request.method == "GET":
            return True
        return super().allow_request(request)
```

## 8. 에러 처리 + 쓰로틀링 통합 패턴

```python
from ninja import NinjaAPI
from ninja.errors import HttpError, ValidationError
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

api = NinjaAPI(
    throttle=[
        AnonRateThrottle('100/m'),
        AuthRateThrottle('1000/m'),
    ],
)

class BusinessLogicError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

@api.exception_handler(BusinessLogicError)
def handle_business_error(request, exc):
    response = api.create_response(
        request,
        {
            "type": f"https://api.example.com/probs/{exc.code.lower()}",
            "title": "Business Rule Violation",
            "status": 400,
            "detail": exc.message,
            "instance": request.path,
            "code": exc.code,
        },
        status=400,
    )
    response["Content-Type"] = "application/problem+json"
    return response

@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    response = api.create_response(
        request,
        {
            "type": "https://api.example.com/probs/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "items": exc.errors,
            "meta": {"code": "VALIDATION_ERROR"},
        },
        status=422,
    )
    response["Content-Type"] = "application/problem+json"
    return response
```
