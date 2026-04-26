# Django Ninja 비동기 결제 API 엔드포인트

외부 결제 API를 호출하는 비동기 Django Ninja 엔드포인트 구현.

---

## 1. 프로젝트 구조

```
payments/
    __init__.py
    models.py
    schemas.py
    api.py
    throttling.py
    auth.py
    external_client.py
```

---

## 2. 모델 정의 (`payments/models.py`)

```python
import uuid
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KRW")
    description = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    external_transaction_id = models.CharField(
        max_length=255, blank=True, default=""
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.amount} {self.currency}"
```

---

## 3. RFC 9457 Problem Details 스키마 (`payments/schemas.py`)

```python
import uuid
from decimal import Decimal
from datetime import datetime
from typing import Optional

from ninja import Schema


# ── Request ────────────────────────────────────────────────

class PaymentCreateRequest(Schema):
    amount: Decimal
    currency: str = "KRW"
    description: str = ""


# ── Response ───────────────────────────────────────────────

class PaymentResponse(Schema):
    id: uuid.UUID
    amount: Decimal
    currency: str
    description: str
    status: str
    external_transaction_id: str
    created_at: datetime
    updated_at: datetime


# ── RFC 9457 Problem Details ──────────────────────────────
# https://www.rfc-editor.org/rfc/rfc9457

class ProblemDetail(Schema):
    """RFC 9457 Problem Details for HTTP APIs."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
```

---

## 4. Bearer Token 인증 (`payments/auth.py`)

```python
import os
from ninja.security import HttpBearer


class BearerTokenAuth(HttpBearer):
    """
    Bearer Token 인증.
    실제 운영에서는 DB 조회 또는 JWT 검증으로 교체한다.
    """

    def authenticate(self, request, token: str):
        valid_token = os.environ.get("API_BEARER_TOKEN", "")
        if token and token == valid_token:
            return token
        return None
```

---

## 5. 쓰로틀링 미들웨어 (`payments/throttling.py`)

```python
import time
from collections import defaultdict
from threading import Lock

from ninja.errors import HttpError


class RateLimiter:
    """
    슬라이딩 윈도우 기반 분당 요청 제한기.
    단일 프로세스 환경용이다. 멀티 프로세스/분산 환경에서는
    Redis 기반(django-ratelimit 등)으로 교체해야 한다.
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _get_client_key(self, request) -> str:
        """인증 토큰 기반으로 클라이언트를 식별한다."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"token:{auth_header[7:]}"
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.META.get('REMOTE_ADDR', 'unknown')}"

    def check(self, request) -> None:
        """요청 허용 여부를 확인한다. 초과 시 HttpError(429)를 발생시킨다."""
        client_key = self._get_client_key(request)
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            timestamps = self._requests[client_key]
            # 윈도우 밖의 오래된 기록 제거
            self._requests[client_key] = [
                ts for ts in timestamps if ts > cutoff
            ]
            if len(self._requests[client_key]) >= self.max_requests:
                raise HttpError(
                    429, "Rate limit exceeded. Max 30 requests per minute."
                )
            self._requests[client_key].append(now)


# 모듈 수준 싱글턴
rate_limiter = RateLimiter(max_requests=30, window_seconds=60)
```

---

## 6. 외부 결제 API 클라이언트 (`payments/external_client.py`)

```python
import os
import logging
from dataclasses import dataclass
from decimal import Decimal

import httpx

logger = logging.getLogger(__name__)

EXTERNAL_API_BASE_URL = os.environ.get(
    "PAYMENT_GATEWAY_URL", "https://api.payment-gateway.example.com"
)
EXTERNAL_API_KEY = os.environ.get("PAYMENT_GATEWAY_API_KEY", "")

# 타임아웃 설정: connect 5s, read 30s, write 10s, pool 5s
TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


@dataclass
class ExternalPaymentResult:
    success: bool
    transaction_id: str = ""
    error_message: str = ""


async def create_external_payment(
    amount: Decimal,
    currency: str,
    description: str,
) -> ExternalPaymentResult:
    """
    외부 결제 게이트웨이에 결제를 요청한다.

    httpx.AsyncClient를 async with로 사용하여
    요청 완료 후 커넥션이 반드시 정리되도록 한다.
    """
    payload = {
        "amount": str(amount),
        "currency": currency,
        "description": description,
    }

    try:
        async with httpx.AsyncClient(
            base_url=EXTERNAL_API_BASE_URL,
            timeout=TIMEOUT,
        ) as client:
            response = await client.post(
                "/v1/charges",
                json=payload,
                headers={
                    "Authorization": f"Bearer {EXTERNAL_API_KEY}",
                    "Content-Type": "application/json",
                },
            )

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return ExternalPaymentResult(
                success=True,
                transaction_id=data.get("transaction_id", ""),
            )

        logger.error(
            "External payment API error: status=%d body=%s",
            response.status_code,
            response.text,
        )
        return ExternalPaymentResult(
            success=False,
            error_message=f"Gateway returned HTTP {response.status_code}",
        )

    except httpx.TimeoutException:
        logger.exception("External payment API timeout")
        return ExternalPaymentResult(
            success=False,
            error_message="Payment gateway timeout",
        )
    except httpx.RequestError as exc:
        logger.exception("External payment API request error")
        return ExternalPaymentResult(
            success=False,
            error_message=f"Payment gateway connection error: {exc}",
        )
```

---

## 7. API 엔드포인트 (`payments/api.py`)

```python
import uuid
import logging

from django.http import HttpRequest, JsonResponse
from ninja import Router

# ── ORM 비동기 호출 주의사항 ──────────────────────────────
# Django ORM은 기본적으로 동기(synchronous)이다.
# async view 내에서 ORM을 직접 호출하면
# SynchronousOnlyOperation 예외가 발생한다.
#
# 해결 방법 (택 1):
#   1. sync_to_async 래핑  (아래 코드에서 사용)
#   2. QuerySet의 .aget(), .acreate(), .afilter() 등
#      Django 4.1+ 에서 제공하는 async ORM 메서드 사용
#
# Django 4.1+ async ORM 메서드를 사용하면 sync_to_async 없이
# 직접 await 할 수 있다. 이 구현에서는 Django 4.1+ async ORM을 사용한다.
# ──────────────────────────────────────────────────────────

from .models import Payment
from .schemas import PaymentCreateRequest, PaymentResponse, ProblemDetail
from .auth import BearerTokenAuth
from .throttling import rate_limiter
from .external_client import create_external_payment

logger = logging.getLogger(__name__)

router = Router(tags=["payments"])


def problem_response(
    status: int,
    title: str,
    detail: str | None = None,
    instance: str | None = None,
    problem_type: str = "about:blank",
) -> JsonResponse:
    """RFC 9457 Problem Details 형식의 에러 응답을 생성한다."""
    body = {
        "type": problem_type,
        "title": title,
        "status": status,
    }
    if detail is not None:
        body["detail"] = detail
    if instance is not None:
        body["instance"] = instance

    return JsonResponse(
        body,
        status=status,
        content_type="application/problem+json",
    )


# ── POST /api/v1/payments ─────────────────────────────────

@router.post(
    "/",
    response={201: PaymentResponse},
    auth=BearerTokenAuth(),
    summary="결제 생성",
)
async def create_payment(
    request: HttpRequest,
    payload: PaymentCreateRequest,
):
    """
    결제를 생성하고 외부 결제 게이트웨이에 요청을 전달한다.
    """
    # 쓰로틀링 체크
    try:
        rate_limiter.check(request)
    except Exception:
        return problem_response(
            status=429,
            title="Too Many Requests",
            detail="Rate limit exceeded. Maximum 30 requests per minute.",
            instance=request.path,
            problem_type="https://api.example.com/problems/rate-limit-exceeded",
        )

    # 입력값 검증
    if payload.amount <= 0:
        return problem_response(
            status=422,
            title="Unprocessable Content",
            detail="Amount must be greater than zero.",
            instance=request.path,
            problem_type="https://api.example.com/problems/invalid-amount",
        )

    if len(payload.currency) != 3:
        return problem_response(
            status=422,
            title="Unprocessable Content",
            detail="Currency must be a 3-letter ISO 4217 code.",
            instance=request.path,
            problem_type="https://api.example.com/problems/invalid-currency",
        )

    # ── ORM: Django 4.1+ async 메서드 사용 ──────────────
    # Payment.objects.acreate()는 내부적으로 sync_to_async를 사용하여
    # 동기 ORM 호출을 비동기로 래핑한다.
    # 주의: select_for_update(), bulk_create() 등 일부 메서드는
    # async 버전이 아직 제공되지 않을 수 있으므로 확인이 필요하다.
    payment = await Payment.objects.acreate(
        amount=payload.amount,
        currency=payload.currency.upper(),
        description=payload.description,
        status=Payment.Status.PENDING,
    )

    # 외부 결제 API 호출 (httpx.AsyncClient)
    result = await create_external_payment(
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
    )

    if result.success:
        # ── ORM: async 업데이트 ──────────────────────────
        payment.status = Payment.Status.COMPLETED
        payment.external_transaction_id = result.transaction_id
        await payment.asave(update_fields=["status", "external_transaction_id", "updated_at"])
    else:
        payment.status = Payment.Status.FAILED
        await payment.asave(update_fields=["status", "updated_at"])

        logger.error(
            "Payment %s failed: %s", payment.id, result.error_message
        )
        return problem_response(
            status=502,
            title="Bad Gateway",
            detail=f"External payment processing failed: {result.error_message}",
            instance=request.path,
            problem_type="https://api.example.com/problems/payment-gateway-error",
        )

    return 201, PaymentResponse.from_orm(payment)


# ── GET /api/v1/payments/{id} ─────────────────────────────

@router.get(
    "/{payment_id}",
    response=PaymentResponse,
    auth=BearerTokenAuth(),
    summary="결제 조회",
)
async def get_payment(
    request: HttpRequest,
    payment_id: uuid.UUID,
):
    """
    결제 ID로 결제 정보를 조회한다.
    """
    # 쓰로틀링 체크
    try:
        rate_limiter.check(request)
    except Exception:
        return problem_response(
            status=429,
            title="Too Many Requests",
            detail="Rate limit exceeded. Maximum 30 requests per minute.",
            instance=request.path,
            problem_type="https://api.example.com/problems/rate-limit-exceeded",
        )

    # ── ORM: async 조회 ──────────────────────────────────
    # .aget()은 Django 4.1+에서 제공하는 비동기 단건 조회 메서드이다.
    # DoesNotExist 예외는 동기 버전과 동일하게 발생한다.
    try:
        payment = await Payment.objects.aget(id=payment_id)
    except Payment.DoesNotExist:
        return problem_response(
            status=404,
            title="Not Found",
            detail=f"Payment with id '{payment_id}' does not exist.",
            instance=request.path,
            problem_type="https://api.example.com/problems/payment-not-found",
        )

    return PaymentResponse.from_orm(payment)
```

---

## 8. URL 등록 (`config/urls.py` 또는 프로젝트 `urls.py`)

```python
from ninja import NinjaAPI
from payments.api import router as payments_router

api = NinjaAPI(
    title="Payments API",
    version="1.0.0",
)

api.add_router("/v1/payments", payments_router)

# Django urlpatterns
urlpatterns = [
    # ...
    path("api/", api.urls),
]
```

---

## 9. async view에서 ORM 호출 시 주의사항

### 9-1. 핵심 원칙

| 항목 | 설명 |
|------|------|
| **SynchronousOnlyOperation** | `async def` 뷰 안에서 동기 ORM 메서드(`objects.get()`, `objects.create()` 등)를 직접 호출하면 이 예외가 발생한다. Django는 이벤트 루프 안에서 동기 DB 호출을 차단한다. |
| **Django 4.1+ async ORM** | `aget()`, `acreate()`, `afilter()`, `asave()`, `adelete()` 등의 메서드를 사용하면 `await`로 직접 호출할 수 있다. 내부적으로 `sync_to_async`를 사용한다. |
| **sync_to_async 수동 래핑** | async ORM 메서드가 없는 경우 `asgiref.sync.sync_to_async`로 직접 래핑해야 한다. |

### 9-2. Django 4.1+ async ORM 메서드 사용 (권장)

```python
# 단건 조회
payment = await Payment.objects.aget(id=payment_id)

# 생성
payment = await Payment.objects.acreate(amount=100, currency="KRW")

# 저장
payment.status = "completed"
await payment.asave(update_fields=["status"])

# 삭제
await payment.adelete()

# 필터 조회 (주의: afilter()는 async iterator를 반환)
async for p in Payment.objects.filter(status="pending"):
    ...
```

### 9-3. sync_to_async 수동 래핑 (대체 방법)

```python
from asgiref.sync import sync_to_async

# 방법 1: 데코레이터
@sync_to_async
def get_payment_sync(payment_id):
    return Payment.objects.select_related("user").get(id=payment_id)

payment = await get_payment_sync(payment_id)

# 방법 2: 인라인 래핑
payment = await sync_to_async(
    Payment.objects.get, thread_sensitive=True
)(id=payment_id)
```

### 9-4. Lazy QuerySet 평가 주의

```python
# WRONG: QuerySet은 lazy하므로 async 컨텍스트에서 list()로 평가하면 에러 발생
payments = list(Payment.objects.filter(status="pending"))  # SynchronousOnlyOperation

# CORRECT: async for 사용
payments = []
async for p in Payment.objects.filter(status="pending"):
    payments.append(p)

# CORRECT: sync_to_async로 래핑
payments = await sync_to_async(
    lambda: list(Payment.objects.filter(status="pending"))
)()
```

### 9-5. 트랜잭션 처리

```python
from django.db import transaction
from asgiref.sync import sync_to_async

# async view 내에서 트랜잭션 사용 시 sync_to_async로 래핑한다.
@sync_to_async
def create_payment_with_log(amount, currency):
    with transaction.atomic():
        payment = Payment.objects.create(amount=amount, currency=currency)
        PaymentLog.objects.create(payment=payment, action="created")
        return payment

payment = await create_payment_with_log(10000, "KRW")
```

### 9-6. N+1 쿼리와 select_related / prefetch_related

```python
# select_related, prefetch_related는 async 메서드가 없으므로
# sync_to_async로 래핑하거나 async for와 함께 사용한다.

@sync_to_async
def get_payments_with_user():
    return list(
        Payment.objects.select_related("user")
        .filter(status="completed")
        .order_by("-created_at")[:20]
    )

payments = await get_payments_with_user()
```

---

## 10. 실행 환경 설정

### ASGI 서버 필수

비동기 뷰를 사용하려면 ASGI 서버로 실행해야 한다.

```bash
# uvicorn 사용 (권장)
pip install uvicorn
uvicorn config.asgi:application --host 0.0.0.0 --port 8000

# daphne 사용
pip install daphne
daphne config.asgi:application -b 0.0.0.0 -p 8000
```

### 환경 변수

```bash
export API_BEARER_TOKEN="your-secure-bearer-token"
export PAYMENT_GATEWAY_URL="https://api.payment-gateway.example.com"
export PAYMENT_GATEWAY_API_KEY="your-gateway-api-key"
```

### 의존성

```
django>=4.1
django-ninja>=1.0
httpx>=0.27
uvicorn>=0.30
```

---

## 11. 요청/응답 예시

### 결제 생성 (성공)

```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Authorization: Bearer your-secure-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50000, "currency": "KRW", "description": "Test payment"}'
```

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "amount": 50000,
  "currency": "KRW",
  "description": "Test payment",
  "status": "completed",
  "external_transaction_id": "txn_abc123",
  "created_at": "2026-04-04T10:30:00Z",
  "updated_at": "2026-04-04T10:30:01Z"
}
```

### 결제 조회

```bash
curl http://localhost:8000/api/v1/payments/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Authorization: Bearer your-secure-bearer-token"
```

### 에러 응답 (RFC 9457 Problem Details)

```json
{
  "type": "https://api.example.com/problems/payment-not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "Payment with id 'a1b2c3d4-0000-0000-0000-000000000000' does not exist.",
  "instance": "/api/v1/payments/a1b2c3d4-0000-0000-0000-000000000000"
}
```

### 쓰로틀링 초과

```json
{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Maximum 30 requests per minute.",
  "instance": "/api/v1/payments/"
}
```

### 외부 게이트웨이 장애

```json
{
  "type": "https://api.example.com/problems/payment-gateway-error",
  "title": "Bad Gateway",
  "status": 502,
  "detail": "External payment processing failed: Payment gateway timeout",
  "instance": "/api/v1/payments/"
}
```
