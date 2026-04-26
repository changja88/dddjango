# 외부 결제 API 비동기 엔드포인트

## 프로젝트 구조

```
payments/
├── __init__.py
├── models.py
├── schemas.py
├── api.py
├── services.py
└── exceptions.py
```

## models.py

```python
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    external_id = models.CharField(max_length=255, unique=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="KRW")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    description = models.TextField(blank=True)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.amount} {self.currency}"
```

## schemas.py

```python
from datetime import datetime
from decimal import Decimal

from ninja import ModelSchema, Schema

from .models import Payment


class PaymentCreateIn(Schema):
    amount: Decimal
    currency: str = "KRW"
    description: str = ""
    customer_email: str


class PaymentOut(ModelSchema):
    class Meta:
        model = Payment
        fields = [
            "id",
            "external_id",
            "amount",
            "currency",
            "status",
            "description",
            "customer_email",
            "created_at",
            "updated_at",
        ]


class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""
```

## exceptions.py

```python
class PaymentGatewayError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class PaymentNotFoundError(Exception):
    def __init__(self, payment_id: int):
        self.payment_id = payment_id
```

## services.py

외부 결제 API 호출 로직을 서비스 레이어로 분리한다. 엔드포인트가 비대해지는 것을 방지한다.

```python
import httpx

from .exceptions import PaymentGatewayError

PAYMENT_GATEWAY_URL = "https://api.payment-gateway.example.com/v1"
GATEWAY_API_KEY = "gw_secret_key"  # 실제로는 settings 또는 환경 변수에서 로드


async def create_external_payment(
    amount: float,
    currency: str,
    description: str,
    customer_email: str,
) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{PAYMENT_GATEWAY_URL}/charges",
            json={
                "amount": float(amount),
                "currency": currency,
                "description": description,
                "receipt_email": customer_email,
            },
            headers={"Authorization": f"Bearer {GATEWAY_API_KEY}"},
        )

    if response.status_code != 200:
        raise PaymentGatewayError(
            status_code=response.status_code,
            detail=response.text,
        )

    return response.json()


async def fetch_external_payment(external_id: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{PAYMENT_GATEWAY_URL}/charges/{external_id}",
            headers={"Authorization": f"Bearer {GATEWAY_API_KEY}"},
        )

    if response.status_code != 200:
        raise PaymentGatewayError(
            status_code=response.status_code,
            detail=response.text,
        )

    return response.json()
```

## api.py

```python
from django.http import JsonResponse
from ninja import Router
from ninja.errors import HttpError, ValidationError
from ninja.security import HttpBearer
from ninja.throttling import AuthRateThrottle

from .exceptions import PaymentGatewayError, PaymentNotFoundError
from .models import Payment
from .schemas import PaymentCreateIn, PaymentOut, ProblemDetail
from .services import create_external_payment, fetch_external_payment

router = Router(tags=["payments"])


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
class BearerAuth(HttpBearer):
    def authenticate(self, request, token: str):
        # 실제 구현에서는 DB 또는 외부 인증 서버로 토큰 검증
        if token == "valid-token":
            return token
        return None


# ---------------------------------------------------------------------------
# Throttling -- 분당 30회
# ---------------------------------------------------------------------------
payment_throttle = AuthRateThrottle("30/m")


# ---------------------------------------------------------------------------
# Exception Handlers (RFC 9457 Problem Details)
# ---------------------------------------------------------------------------
# NOTE: exception_handler는 NinjaAPI 인스턴스에 등록해야 한다.
#       아래 함수들은 메인 api.py에서 NinjaAPI 인스턴스에 등록한다.
#       여기서는 참조용으로 함께 기술한다.


def register_exception_handlers(api):
    """메인 NinjaAPI 인스턴스에 RFC 9457 예외 핸들러를 등록한다."""

    @api.exception_handler(PaymentGatewayError)
    def handle_gateway_error(request, exc: PaymentGatewayError):
        return JsonResponse(
            ProblemDetail(
                type="https://api.example.com/probs/payment-gateway-error",
                title="Payment Gateway Error",
                status=502,
                detail=f"External payment service returned an error: {exc.detail}",
                instance=request.path,
            ).dict(),
            status=502,
            content_type="application/problem+json",
        )

    @api.exception_handler(PaymentNotFoundError)
    def handle_not_found(request, exc: PaymentNotFoundError):
        return JsonResponse(
            ProblemDetail(
                type="https://api.example.com/probs/payment-not-found",
                title="Payment Not Found",
                status=404,
                detail=f"Payment with id {exc.payment_id} does not exist.",
                instance=request.path,
            ).dict(),
            status=404,
            content_type="application/problem+json",
        )

    @api.exception_handler(ValidationError)
    def handle_validation_error(request, exc: ValidationError):
        return JsonResponse(
            {
                "type": "https://api.example.com/probs/validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": "The request body failed validation.",
                "instance": request.path,
                "errors": exc.errors,
            },
            status=422,
            content_type="application/problem+json",
        )

    @api.exception_handler(HttpError)
    def handle_http_error(request, exc: HttpError):
        return JsonResponse(
            ProblemDetail(
                title=str(exc),
                status=exc.status_code,
                detail=str(exc),
                instance=request.path,
            ).dict(),
            status=exc.status_code,
            content_type="application/problem+json",
        )

    @api.exception_handler(Exception)
    def handle_unexpected_error(request, exc: Exception):
        return JsonResponse(
            ProblemDetail(
                title="Internal Server Error",
                status=500,
                detail="An unexpected error occurred.",
                instance=request.path,
            ).dict(),
            status=500,
            content_type="application/problem+json",
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response={201: PaymentOut},
    auth=BearerAuth(),
    throttle=[payment_throttle],
)
async def create_payment(request, payload: PaymentCreateIn) -> Payment:
    # 1. 외부 결제 게이트웨이 호출 (httpx.AsyncClient)
    gateway_response = await create_external_payment(
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        customer_email=payload.customer_email,
    )

    # 2. ORM 저장 -- async 뷰에서는 aget/acreate 등 async ORM 메서드 사용 (Django 4.1+)
    #    sync_to_async로 감싸는 방식도 가능하나 네이티브 async ORM 권장
    payment = await Payment.objects.acreate(
        external_id=gateway_response["id"],
        amount=payload.amount,
        currency=payload.currency,
        status=Payment.Status.COMPLETED,
        description=payload.description,
        customer_email=payload.customer_email,
    )

    return payment


@router.get(
    "/{payment_id}",
    response=PaymentOut,
    auth=BearerAuth(),
    throttle=[payment_throttle],
)
async def get_payment(request, payment_id: int) -> Payment:
    # async 뷰에서 ORM 단건 조회 -- aget 사용 (Django 4.1+)
    try:
        payment = await Payment.objects.aget(id=payment_id)
    except Payment.DoesNotExist:
        raise PaymentNotFoundError(payment_id=payment_id)

    return payment
```

## 메인 프로젝트 연결

### myproject/api.py

```python
from ninja import NinjaAPI

from payments.api import register_exception_handlers
from payments.api import router as payments_router

api = NinjaAPI(version="1.0.0")

register_exception_handlers(api)

api.add_router("/payments", payments_router)
```

### myproject/urls.py

```python
from django.urls import path

from .api import api

urlpatterns = [
    path("api/v1/", api.urls),
]
```

최종 URL:
- `POST /api/v1/payments` -- 결제 생성
- `GET /api/v1/payments/{payment_id}` -- 결제 조회

## async 뷰에서 ORM 호출 시 주의사항

### 1. SynchronousOnlyOperation 예외

async 뷰에서 동기 ORM 메서드(`objects.get()`, `objects.create()`, `objects.filter()` 등)를 직접 호출하면 `SynchronousOnlyOperation` 예외가 발생한다. Django ORM은 기본적으로 "async-unsafe"이다.

### 2. Django 4.1+ 네이티브 async ORM 메서드 사용 (권장)

```python
# aget, acreate, aupdate, adelete, afirst, alast, acount, aexists 등
payment = await Payment.objects.aget(id=payment_id)
payment = await Payment.objects.acreate(amount=10000, currency="KRW", ...)
await Payment.objects.filter(id=payment_id).aupdate(status="refunded")
await payment.adelete()
exists = await Payment.objects.filter(external_id="ext_123").aexists()
```

### 3. Django 4.0 이하에서는 sync_to_async 래퍼 사용

```python
from asgiref.sync import sync_to_async

payment = await sync_to_async(Payment.objects.get)(id=payment_id)
payment = await sync_to_async(Payment.objects.create)(amount=10000, ...)
```

### 4. Lazy QuerySet 주의

QuerySet은 지연 평가(lazily evaluated)된다. async 뷰에서 직접 반복하면 동기 실행이 시도되어 예외가 발생한다.

```python
# 잘못된 방법 -- SynchronousOnlyOperation 발생
@router.get("/")
async def list_payments(request):
    payments = Payment.objects.all()
    return [p for p in payments]  # 여기서 동기 실행 시도

# 올바른 방법 1: sync_to_async로 리스트 강제 평가
@router.get("/")
async def list_payments(request):
    payments = await sync_to_async(list)(Payment.objects.all())
    return payments

# 올바른 방법 2: async for 반복 (Django 4.1+)
@router.get("/")
async def list_payments(request):
    return [payment async for payment in Payment.objects.all()]
```

### 5. ASGI 서버 필수

async 뷰를 실행하려면 ASGI 서버가 필요하다. WSGI 서버(gunicorn 기본 모드 등)에서는 async 뷰가 정상 동작하지 않는다.

```bash
pip install uvicorn
uvicorn myproject.asgi:application --reload
```
