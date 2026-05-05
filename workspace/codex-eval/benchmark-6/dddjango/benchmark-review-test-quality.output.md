지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않고, 현재 작업 디렉터리 `/private/tmp/dddjango-codex-eval`도 비어 있습니다. 그래서 실제 fixture 파일/테스트 파일 기반의 라인 단위 리뷰와 `pytest` 실행은 불가능했습니다.

**주요 Findings**

P1 — [Fixture Overuse] -- DB fixture 전체 로딩에 의존하는 테스트는 실패 원인을 흐립니다.  
`loaddata`, 대형 JSON fixture, 전역 `db` fixture에 기대면 테스트가 “이 동작에 필요한 최소 데이터”를 말하지 못합니다. 도메인 규칙 테스트는 DB 없이 값 객체/도메인 서비스로 검증하고, Django ORM은 repository/selector 통합 테스트에서만 다뤄야 합니다.

P1 — [Weak Assertion] -- `assert response.status_code == 200`, `assert obj.exists()`만으로는 회귀를 못 잡습니다.  
상태 코드와 존재 여부는 “무언가 됐다”만 보장합니다. 할인액, 상태 전이, 재고 차감량, 생성된 row 수, 응답 schema, 예외 메시지처럼 도메인 결과를 직접 검증해야 합니다. mutation testing 관점에서 `>= 0`, `is not None`, `exists()` 위주의 assert는 대부분 살아남습니다.

P2 — [Slow Test Boundary] -- 단위 테스트로 가능한 규칙까지 `django_db`로 돌리면 피드백이 느려집니다.  
`pytest.mark.django_db`는 ORM, transaction, constraint, selector query, API integration에만 붙이고, 쿠폰/주문/재고 같은 계산·상태 전이 규칙은 `tests/isolated/unit/`에서 DB 없이 실행하는 편이 낫습니다.

P2 — [Unclear Fixture Intent] -- `user`, `order`, `product` 같은 범용 fixture가 많아지면 Arrange가 숨습니다.  
fixture 이름은 역할을 드러내야 합니다. 예: `paid_order`, `expired_coupon`, `out_of_stock_product`. 여러 테스트에서 공유할 값은 factory로 만들고, 각 테스트는 필요한 차이만 명시하세요.

**개선 기준**

```text
tests/
  isolated/
    unit/          # DB 없음: domain policy, value object, pure service
    integration/   # test DB 사용: ORM constraint, selector, repository
  real/
    integration/   # 실제/stage 인프라 검증, CI 기본 제외
```

`tests/isolated`는 `config.settings.test`로 실행하고 locmem cache/email, eager celery, 빠른 password hasher, 테스트 DB를 강제하세요. 운영 settings로 isolated 테스트를 돌리는 것은 회귀입니다.

**RED 테스트 예시**

```python
# tests/isolated/unit/orders/test_apply_coupon.py
import pytest

from orders.domain import Coupon, OrderTotal, apply_coupon
from orders.exceptions import CouponExpired


def test_apply_coupon_valid_percent_coupon_returns_discounted_total():
    coupon = Coupon.percent(code="WELCOME10", rate=10, expired=False)
    total = OrderTotal(amount=10_000)

    result = apply_coupon(total, coupon)

    assert result.original_amount == 10_000
    assert result.discount_amount == 1_000
    assert result.payable_amount == 9_000
    assert result.applied_coupon_code == "WELCOME10"


def test_apply_coupon_expired_coupon_raises_domain_error():
    coupon = Coupon.percent(code="OLD10", rate=10, expired=True)

    with pytest.raises(CouponExpired, match="OLD10"):
        apply_coupon(OrderTotal(amount=10_000), coupon)
```

예상 실패: `orders.domain`, `Coupon`, `OrderTotal`, `apply_coupon`, `CouponExpired`가 아직 없으면 import 실패 또는 예외 미정의로 RED가 됩니다.

**GREEN 최소 구현 스케치**

```python
from dataclasses import dataclass


class CouponExpired(Exception):
    pass


@dataclass(frozen=True)
class OrderTotal:
    amount: int


@dataclass(frozen=True)
class Coupon:
    code: str
    rate: int
    expired: bool = False

    @classmethod
    def percent(cls, code: str, rate: int, expired: bool = False):
        return cls(code=code, rate=rate, expired=expired)


@dataclass(frozen=True)
class CouponResult:
    original_amount: int
    discount_amount: int
    payable_amount: int
    applied_coupon_code: str


def apply_coupon(total: OrderTotal, coupon: Coupon) -> CouponResult:
    if coupon.expired:
        raise CouponExpired(coupon.code)

    discount = total.amount * coupon.rate // 100
    return CouponResult(
        original_amount=total.amount,
        discount_amount=discount,
        payable_amount=total.amount - discount,
        applied_coupon_code=coupon.code,
    )
```

**REFACTOR Notes**

DB fixture는 “기본 세계”를 만드는 용도로 쓰지 말고, integration test에서 factory로 필요한 row만 생성하세요. 외부 의존성은 `MagicMock` 남발보다 `InMemoryCouponRepository` 같은 Fake가 낫습니다. API/selector 테스트에는 `assertNumQueries`를 추가해 N+1을 회귀로 잡고, 반복 케이스는 `pytest.mark.parametrize`로 경계값을 명시하세요.

실행 명령:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/unit -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/integration -q
pytest --randomly-seed=last tests/isolated -q
```

---
> **관련 스킬 참조:**
> - pytest fixture/assertion 품질 개선 → **implementation-test** 스킬
> - Red-Green-Refactor로 테스트 재구성 → **implementation-tdd** 스킬
> - Django ORM/API 통합 테스트 경계 설정 → **implementation-django** 스킬