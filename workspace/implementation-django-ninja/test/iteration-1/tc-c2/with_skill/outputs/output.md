# RFC 9457 Problem Details 리팩토링

## 구조 변경 요약

원본 코드는 `HttpError`를 직접 던져 Django Ninja의 기본 에러 응답 형식에 의존한다.
이를 다음과 같이 변경한다:

1. RFC 9457 `ProblemDetail` Schema를 정의한다.
2. 도메인별 예외 클래스(`UserNotFoundError`, `DuplicateEmailError`, `InsufficientStockError`)를 분리한다.
3. 글로벌 `@api.exception_handler(Exception)`으로 모든 에러를 `application/problem+json` 형식으로 통일한다.
4. 도메인별 예외 핸들러에서 확장 필드를 포함한 Problem Details를 반환한다.

---

[Before]
```python
from ninja import NinjaAPI
from ninja.errors import HttpError

api = NinjaAPI()

@api.get('/users/{user_id}')
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, 'User not found')
    return {'id': user.id, 'name': user.name}

@api.post('/users')
def create_user(request, payload: UserIn):
    if User.objects.filter(email=payload.email).exists():
        raise HttpError(409, 'Email already exists')
    user = User.objects.create(**payload.dict())
    return {'id': user.id}

@api.post('/orders')
def create_order(request, payload: OrderIn):
    product = Product.objects.get(id=payload.product_id)
    if product.stock < payload.quantity:
        raise HttpError(400, 'Insufficient stock')
    order = Order.objects.create(product=product, quantity=payload.quantity)
    return {'order_id': order.id}
```

[After]
```python
from ninja import NinjaAPI, Schema, Router
from ninja.errors import HttpError, ValidationError
from django.http import JsonResponse


# ── RFC 9457 Problem Detail Schema ──────────────────────────────

class ProblemDetail(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""


# ── Domain Exceptions ───────────────────────────────────────────

class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id


class DuplicateEmailError(Exception):
    def __init__(self, email: str):
        self.email = email


class InsufficientStockError(Exception):
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested


# ── API Setup ───────────────────────────────────────────────────

api = NinjaAPI()


# ── Global Exception Handlers ──────────────────────────────────

@api.exception_handler(Exception)
def handle_generic_error(request, exc: Exception) -> JsonResponse:
    if isinstance(exc, HttpError):
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


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc: ValidationError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": "Request validation failed.",
            "instance": request.path,
            "errors": exc.errors,
        },
        status=422,
        content_type="application/problem+json",
    )


@api.exception_handler(UserNotFoundError)
def handle_user_not_found(request, exc: UserNotFoundError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "User Not Found",
            "status": 404,
            "detail": f"User with id {exc.user_id} does not exist.",
            "instance": request.path,
        },
        status=404,
        content_type="application/problem+json",
    )


@api.exception_handler(DuplicateEmailError)
def handle_duplicate_email(request, exc: DuplicateEmailError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Duplicate Email",
            "status": 409,
            "detail": f"A user with email '{exc.email}' already exists.",
            "instance": request.path,
        },
        status=409,
        content_type="application/problem+json",
    )


@api.exception_handler(InsufficientStockError)
def handle_insufficient_stock(request, exc: InsufficientStockError) -> JsonResponse:
    return JsonResponse(
        {
            "type": "about:blank",
            "title": "Insufficient Stock",
            "status": 422,
            "detail": (
                f"Product {exc.product_id} has {exc.available} units available, "
                f"but {exc.requested} were requested."
            ),
            "instance": request.path,
            "product_id": exc.product_id,
            "available": exc.available,
            "requested": exc.requested,
        },
        status=422,
        content_type="application/problem+json",
    )


# ── Response Schemas ────────────────────────────────────────────

class UserOut(Schema):
    id: int
    name: str


class UserCreateOut(Schema):
    id: int


class OrderCreateOut(Schema):
    order_id: int


# ── Endpoints ───────────────────────────────────────────────────

@api.get("/users/{user_id}", response=UserOut)
def get_user(request, user_id: int) -> UserOut:
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise UserNotFoundError(user_id)
    return UserOut(id=user.id, name=user.name)


@api.post("/users", response={201: UserCreateOut})
def create_user(request, payload: UserIn) -> tuple[int, UserCreateOut]:
    if User.objects.filter(email=payload.email).exists():
        raise DuplicateEmailError(payload.email)
    user = User.objects.create(**payload.dict())
    return 201, UserCreateOut(id=user.id)


@api.post("/orders", response={201: OrderCreateOut})
def create_order(request, payload: OrderIn) -> tuple[int, OrderCreateOut]:
    try:
        product = Product.objects.get(id=payload.product_id)
    except Product.DoesNotExist:
        raise HttpError(404, "Product not found")
    if product.stock < payload.quantity:
        raise InsufficientStockError(
            product_id=product.id,
            available=product.stock,
            requested=payload.quantity,
        )
    order = Order.objects.create(product=product, quantity=payload.quantity)
    return 201, OrderCreateOut(order_id=order.id)
```

[Reason]

각 변경 사항과 적용된 컨벤션:

1. **Custom error format -> CONVERT to RFC 9457 Problem Details** -- `HttpError`를 직접 던지는 방식을 도메인별 예외 클래스 + `@api.exception_handler()`로 전환했다. 모든 에러 응답이 `application/problem+json` Content-Type과 RFC 9457 필수 필드(`type`, `title`, `status`, `detail`, `instance`)를 포함한다. `InsufficientStockError`처럼 도메인 맥락이 필요한 경우 확장 필드(`product_id`, `available`, `requested`)를 추가하여 클라이언트가 에러를 프로그래밍 방식으로 처리할 수 있도록 했다.

2. **Missing type hints -> ADD to all parameters and returns** -- 모든 엔드포인트에 반환 타입 힌트(`UserOut`, `tuple[int, UserCreateOut]` 등)를 추가했다. 예외 핸들러에도 `JsonResponse` 반환 타입을 명시했다.

3. **Schema 사용** -- 응답에 `dict`를 직접 반환하는 대신 `UserOut`, `UserCreateOut`, `OrderCreateOut` Schema를 정의하여 응답 직렬화를 명시적으로 제어한다. `response=` 파라미터로 엔드포인트의 응답 스키마를 선언했다.

4. **create_order에 Product.DoesNotExist 처리 추가** -- 원본 코드에서 `Product.objects.get()`이 실패할 경우 처리되지 않은 예외가 발생하는 문제를 수정했다. 글로벌 핸들러가 이를 500으로 잡지만, 404로 명시적 처리하는 것이 올바르다.

5. **201 상태 코드** -- `create_user`, `create_order`는 리소스 생성이므로 `response={201: Schema}`와 `return 201, data` 패턴을 적용했다.
