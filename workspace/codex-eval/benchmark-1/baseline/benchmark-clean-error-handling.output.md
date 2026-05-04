**표준안**

Django Ninja 프로젝트에서는 `Domain Exception`을 HTTP와 직접 연결하지 않습니다. 도메인은 비즈니스 실패를 자기 언어로 표현하고, API 계층이 그 예외를 RFC 9457 Problem Details 응답으로 변환합니다.

핵심 원칙은 이겁니다.

1. 도메인 계층은 HTTP 상태 코드, Django Ninja, `request`, `JsonResponse`, `HttpError`를 모른다.
2. 애플리케이션 서비스는 도메인 예외를 삼키거나 HTTP 예외로 바꾸지 않는다.
3. API 계층의 exception handler가 도메인 예외를 API 오류 계약으로 변환한다.
4. 모든 API 오류 응답은 RFC 9457 Problem Details 형식을 사용한다.
5. 예외 이름은 기술 오류가 아니라 도메인 실패를 표현한다. 예: `BidTooLow`, `AuctionAlreadyClosed`, `InsufficientBalance`.

**권장 구조**

```text
apps/auctions/
  domain/
    exceptions.py
    models.py
  application/
    services.py
  api/
    schemas.py
    router.py

config/
  api.py
  errors.py
```

**도메인 예외**

```python
# apps/auctions/domain/exceptions.py

class DomainError(Exception):
    code = "domain_error"
    message = "Domain rule violated."

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class AuctionAlreadyClosed(DomainError):
    code = "auction_already_closed"
    message = "Auction is already closed."


class BidTooLow(DomainError):
    code = "bid_too_low"
    message = "Bid amount is too low."

    def __init__(self, minimum_amount: int, actual_amount: int):
        self.minimum_amount = minimum_amount
        self.actual_amount = actual_amount
        super().__init__(self.message)
```

도메인 예외에는 `status_code`를 넣지 않습니다. `409 Conflict`인지 `422 Unprocessable Entity`인지는 API 계약의 문제입니다.

**API 에러 스키마**

```python
# config/errors.py

from typing import Any
from ninja import Schema


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    code: str | None = None
```

**도메인 예외 매핑**

```python
# config/errors.py

from dataclasses import dataclass
from django.http import JsonResponse
from apps.auctions.domain.exceptions import (
    DomainError,
    AuctionAlreadyClosed,
    BidTooLow,
)


@dataclass(frozen=True)
class ErrorMapping:
    status: int
    title: str
    type: str


DOMAIN_ERROR_MAP: dict[type[DomainError], ErrorMapping] = {
    AuctionAlreadyClosed: ErrorMapping(
        status=409,
        title="Auction Already Closed",
        type="https://api.example.com/problems/auction-already-closed",
    ),
    BidTooLow: ErrorMapping(
        status=422,
        title="Bid Too Low",
        type="https://api.example.com/problems/bid-too-low",
    ),
}
```

**Django Ninja 연결**

```python
# config/api.py

from ninja import NinjaAPI
from ninja.errors import ValidationError
from django.http import JsonResponse

from apps.auctions.domain.exceptions import DomainError
from config.errors import DOMAIN_ERROR_MAP


api = NinjaAPI()


@api.exception_handler(DomainError)
def handle_domain_error(request, exc: DomainError):
    mapping = DOMAIN_ERROR_MAP.get(
        type(exc),
        DOMAIN_ERROR_MAP.get(DomainError),
    )

    status = mapping.status if mapping else 400

    payload = {
        "type": mapping.type if mapping else "https://api.example.com/problems/domain-error",
        "title": mapping.title if mapping else "Domain Error",
        "status": status,
        "detail": exc.message,
        "instance": request.path,
        "code": exc.code,
    }

    if hasattr(exc, "minimum_amount"):
        payload["minimum_amount"] = exc.minimum_amount
    if hasattr(exc, "actual_amount"):
        payload["actual_amount"] = exc.actual_amount

    return JsonResponse(
        payload,
        status=status,
        content_type="application/problem+json",
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError):
    return JsonResponse(
        {
            "type": "https://api.example.com/problems/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "code": "validation_error",
            "errors": exc.errors,
        },
        status=422,
        content_type="application/problem+json",
    )
```

**상태 코드 기준**

| 도메인 실패 | HTTP |
|---|---:|
| 리소스 없음 | 404 |
| 인증 필요 | 401 |
| 권한 없음 | 403 |
| 현재 상태와 충돌 | 409 |
| 요청 문법은 맞지만 비즈니스 규칙 위반 | 422 |
| 중복 생성, 낙관적 락 충돌 | 409 |
| 외부 서비스 일시 장애 | 503 |
| 예상하지 못한 서버 오류 | 500 |

**금지 규칙**

```python
# 금지
raise HttpError(409, "Auction already closed")  # 도메인/서비스 내부
raise ValueError("bid too low")                 # 비즈니스 규칙 실패
raise Exception("invalid state")                # 의미 없음
```

```python
# 권장
raise AuctionAlreadyClosed()
raise BidTooLow(minimum_amount=10_000, actual_amount=8_000)
```

이 표준의 핵심은 변환 지점을 하나로 모으는 것입니다. 도메인 예외는 비즈니스 언어를 보존하고, `@api.exception_handler()`만 HTTP 상태 코드와 Problem Details 응답을 책임지게 하면 테스트, 문서화, 변경 관리가 깔끔해집니다.

---
> **관련 스킬 참조:**
> - API 오류 형식/RFC 9457 → **architecture-api** 스킬
> - 도메인 예외/DDD 경계 → **architecture-ddd** 스킬
> - Django Ninja exception handler → **implementation-django-ninja** 스킬