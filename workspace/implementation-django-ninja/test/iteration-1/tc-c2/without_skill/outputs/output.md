# Django Ninja RFC 9457 Problem Details Refactoring

## Refactored Code

```python
from http import HTTPStatus
from typing import Any, Optional

from django.http import JsonResponse
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError


# ----------------------------------------------------------------------
# 1. RFC 9457 Problem Details Schema
# ----------------------------------------------------------------------

class ProblemDetail(Schema):
    """RFC 9457 (Problem Details for HTTP APIs) response body."""
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None


# ----------------------------------------------------------------------
# 2. Custom Exception
# ----------------------------------------------------------------------

class ProblemDetailError(Exception):
    """Raise this instead of HttpError to return RFC 9457 responses."""

    def __init__(
        self,
        status: int,
        detail: str,
        *,
        type: str = "about:blank",
        title: Optional[str] = None,
        instance: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ):
        self.status = status
        self.detail = detail
        self.type = type
        self.title = title or HTTPStatus(status).phrase
        self.instance = instance
        self.extra = extra or {}

    def to_response_body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }
        if self.instance:
            body["instance"] = self.instance
        body.update(self.extra)
        return body


# ----------------------------------------------------------------------
# 3. API setup & global exception handler
# ----------------------------------------------------------------------

api = NinjaAPI()


@api.exception_handler(ProblemDetailError)
def handle_problem_detail(request, exc: ProblemDetailError):
    return JsonResponse(
        exc.to_response_body(),
        status=exc.status,
        content_type="application/problem+json",
    )


# ----------------------------------------------------------------------
# 4. Refactored endpoints
# ----------------------------------------------------------------------

@api.get("/users/{user_id}")
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ProblemDetailError(
            status=404,
            detail=f"User with id {user_id} does not exist.",
            type="https://example.com/problems/user-not-found",
            instance=f"/users/{user_id}",
        )
    return {"id": user.id, "name": user.name}


@api.post("/users")
def create_user(request, payload: UserIn):
    if User.objects.filter(email=payload.email).exists():
        raise ProblemDetailError(
            status=409,
            detail=f"A user with email '{payload.email}' already exists.",
            type="https://example.com/problems/duplicate-email",
            instance="/users",
        )
    user = User.objects.create(**payload.dict())
    return {"id": user.id}


@api.post("/orders")
def create_order(request, payload: OrderIn):
    product = Product.objects.get(id=payload.product_id)
    if product.stock < payload.quantity:
        raise ProblemDetailError(
            status=422,
            detail=(
                f"Product '{product.id}' has {product.stock} units in stock, "
                f"but {payload.quantity} were requested."
            ),
            type="https://example.com/problems/insufficient-stock",
            instance="/orders",
            extra={
                "product_id": product.id,
                "available_stock": product.stock,
                "requested_quantity": payload.quantity,
            },
        )
    order = Order.objects.create(product=product, quantity=payload.quantity)
    return {"order_id": order.id}
```

## Key Changes

### ProblemDetail Schema

RFC 9457 defines five standard members. `ProblemDetail` schema models them all:

| Member     | Type   | Required | Description                              |
|------------|--------|----------|------------------------------------------|
| `type`     | string | yes      | URI reference identifying the problem type. Defaults to `"about:blank"`. |
| `title`    | string | yes      | Short human-readable summary (derived from HTTP status phrase when omitted). |
| `status`   | int    | yes      | HTTP status code.                        |
| `detail`   | string | no       | Human-readable explanation specific to this occurrence. |
| `instance` | string | no       | URI reference identifying this specific occurrence. |

### ProblemDetailError Exception

Replaces `HttpError`. Carries all RFC 9457 fields plus an `extra` dict for extension members (e.g., `product_id`, `available_stock` in the stock example).

### Global Exception Handler

`handle_problem_detail` catches every `ProblemDetailError`, serializes it with `to_response_body()`, and returns a `JsonResponse` with:

- The correct HTTP status code
- `Content-Type: application/problem+json` as required by RFC 9457

### Status Code Adjustment

The insufficient-stock error was changed from `400 Bad Request` to `422 Unprocessable Content`. The request syntax is valid; the server understands it but cannot process it due to a business rule violation. `422` communicates this distinction more precisely per RFC 9110.

### Extension Members

The `extra` parameter on `ProblemDetailError` allows adding domain-specific fields alongside the standard members. The stock error demonstrates this by including `product_id`, `available_stock`, and `requested_quantity` -- giving API consumers machine-readable data to act on.

## Example Response

`POST /orders` with insufficient stock returns:

```json
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
    "type": "https://example.com/problems/insufficient-stock",
    "title": "Unprocessable Entity",
    "status": 422,
    "detail": "Product '42' has 3 units in stock, but 10 were requested.",
    "instance": "/orders",
    "product_id": 42,
    "available_stock": 3,
    "requested_quantity": 10
}
```
