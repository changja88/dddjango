확인 결과, 지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고 `/private/tmp/dddjango-codex-eval`도 비어 있었습니다. 그래서 실제 파일/라인 기준 리뷰나 unified diff는 만들 수 없고, 사용자가 설명한 “Django Ninja router 함수 안에서 재고 차감, 쿠폰 계산, 결제 준비를 모두 처리”하는 구조에 대한 리뷰 findings로 정리합니다.

**주요 내용**
좋은 점부터 보면, 흐름 자체는 “주문 준비”라는 하나의 유스케이스로 묶여 있어 application service 후보가 명확합니다. 문제는 그 흐름이 router 함수에 직접 들어가 있다는 점입니다.

**Findings**

`High` [Django Ninja Convention] -- Router가 transport layer를 넘어 유스케이스 조율과 도메인 규칙을 직접 수행합니다.  
Router는 `HttpRequest`, Schema 검증, 인증, status code, 응답 변환까지만 담당해야 합니다. 재고 차감, 쿠폰 적용, 결제 준비는 HTTP와 무관한 application service로 옮겨야 테스트와 재사용이 쉬워집니다.

`High` [Transaction Boundary] -- 재고 차감과 결제 준비가 한 함수에 섞이면 실패 시 일관성이 깨질 수 있습니다.  
예를 들어 재고를 먼저 차감한 뒤 결제 준비가 실패하면 보상 로직이 필요합니다. 반대로 외부 결제 API를 DB transaction 안에서 호출하면 transaction 시간이 길어지고 retry 시 중복 결제 준비 위험이 생깁니다. “재고 예약/쿠폰 확정/결제 준비”의 트랜잭션 경계를 application service에서 명시해야 합니다.

`Medium` [Domain Policy] -- 쿠폰 계산이 router에 있으면 할인 규칙이 transport 세부사항에 누출됩니다.  
쿠폰 중복 사용 가능 여부, 최소 주문 금액, 상품별 제외, 회원 등급 할인 같은 규칙은 `CouponPolicy` 또는 `DiscountPolicy` 같은 domain policy로 분리하는 편이 맞습니다.

`Medium` [Concurrency & Idempotency] -- 재고 차감과 결제 준비 POST에는 동시성 제어와 멱등성이 필요합니다.  
재고는 `F()` update + affected row 확인, 또는 핫 아이템이면 근거 있는 `select_for_update()`를 고려합니다. 결제 준비는 `Idempotency-Key` 또는 주문 준비 요청 ID로 중복 요청을 방어해야 합니다.

`Medium` [Error Response] -- 도메인 실패가 ad hoc dict나 일반 예외로 흘러가면 API 계약이 불안정해집니다.  
`OutOfStock`, `InvalidCoupon`, `PaymentPreparationFailed` 같은 도메인/애플리케이션 예외를 정의하고, Django Ninja exception handler에서 RFC 9457 Problem Details 형태로 변환하는 방향이 좋습니다.

**개선 방향**

작은 기능이면 헥사고날/UoW를 크게 도입하지 않아도 됩니다. 기준은 단순합니다.

- router: 요청/응답 변환만
- application service: 유스케이스 순서, transaction, repository/adapter 호출 조율
- domain policy: 할인/재고 가능 여부 같은 순수 비즈니스 판단
- infrastructure adapter: Django ORM, 결제 SDK 호출

핵심 형태는 이렇게 잡으면 됩니다.

```python
# schemas.py
from ninja import Schema


class PrepareCheckoutIn(Schema):
    order_id: int
    coupon_code: str | None = None


class PrepareCheckoutOut(Schema):
    checkout_id: int
    payable_amount: int
    payment_token: str
```

```python
# api.py
from django.http import HttpRequest
from ninja import Router

from .schemas import PrepareCheckoutIn, PrepareCheckoutOut
from .services import PrepareCheckoutCommand, prepare_checkout

router = Router()


@router.post("/checkouts", response={201: PrepareCheckoutOut})
def create_checkout(
    request: HttpRequest,
    payload: PrepareCheckoutIn,
) -> tuple[int, PrepareCheckoutOut]:
    result = prepare_checkout(
        PrepareCheckoutCommand(
            order_id=payload.order_id,
            coupon_code=payload.coupon_code,
            user_id=request.user.id,
        )
    )
    return 201, PrepareCheckoutOut(
        checkout_id=result.checkout_id,
        payable_amount=result.payable_amount,
        payment_token=result.payment_token,
    )
```

```python
# services.py
from dataclasses import dataclass
from django.db import transaction

from .policies import CouponPolicy


@dataclass(frozen=True)
class PrepareCheckoutCommand:
    order_id: int
    coupon_code: str | None
    user_id: int


@dataclass(frozen=True)
class PrepareCheckoutResult:
    checkout_id: int
    payable_amount: int
    payment_token: str


def prepare_checkout(cmd: PrepareCheckoutCommand) -> PrepareCheckoutResult:
    with transaction.atomic():
        order = order_repository.get_for_update(cmd.order_id, cmd.user_id)
        discount = CouponPolicy().calculate(order, cmd.coupon_code)
        order.reserve_stock()
        order.apply_discount(discount)
        checkout = checkout_repository.create_from(order)

    payment_token = payment_gateway.prepare(checkout.id, checkout.payable_amount)
    return PrepareCheckoutResult(checkout.id, checkout.payable_amount, payment_token)
```

검증은 최소한 다음을 권합니다.

```bash
python manage.py check
pytest
pytest path/to/tests/test_checkout_api.py
```

테스트 포인트는 재고 부족, 쿠폰 무효, 결제 준비 실패, 동일 요청 재시도, 동시 재고 차감 경쟁 조건입니다.

---
> **관련 스킬 참조:**
> - Django Ninja API 리팩터링 → **implementation-django-ninja** 스킬
> - application service / domain policy 분리 → **architecture-implementation-patterns** 스킬