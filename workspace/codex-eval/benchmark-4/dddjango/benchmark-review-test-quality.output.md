실제 파일 리뷰는 못 했습니다. `/private/tmp/dddjango-codex-eval`에는 `rg --files` 기준으로 읽을 수 있는 프로젝트 파일이 없고, 워크스페이스도 read-only라 pytest 실행도 불가능합니다. 따라서 아래는 현재 증상 기준의 pytest 품질 리뷰와 적용 기준입니다.

**주요 이슈**

[Fixture 남용] -- DB fixture가 도메인 규칙 테스트까지 떠받치면 테스트가 느리고 깨지기 쉽습니다. `@pytest.mark.django_db`, `client`, 모델 factory가 모든 테스트에 기본으로 깔려 있다면 단위 테스트가 아니라 통합 테스트입니다. 비즈니스 규칙은 Django ORM 없이 순수 도메인 객체로 검증하고, ORM 매핑/쿼리/트랜잭션만 DB 테스트로 남겨야 합니다.

[약한 Assert] -- `assert response.status_code == 200`, `assert obj is not None`, `assert count == 1`만 있는 테스트는 회귀 보호가 약합니다. “성공했다”가 아니라 “어떤 상태가 어떻게 바뀌었고, 어떤 값이 반환/저장/발행되었는지”를 검증해야 합니다. 예: 주문 확정이면 `status`, `confirmed_at`, 재고 차감, 도메인 이벤트, 권한 실패 상태까지 assert합니다.

[Slow Test] -- 모든 테스트가 DB를 쓰면 피드백 루프가 무너집니다. 기본 CI 스위트는 `tests/isolated/` 중심으로 빠르게 돌리고, Django DB 통합 테스트는 `tests/isolated/integration/`에서 명시적으로 분리합니다. 외부 DB/실서비스 검증은 `tests/real/`로 격리해 별도 게이트에서 실행합니다.

**개선 기준**

`tests/isolated/unit/domain/`: ORM, client, DB fixture 금지. 순수 객체, 값 객체, 도메인 서비스 테스트.

`tests/isolated/integration/django/`: `pytest.mark.django_db` 허용. Repository, selector, model constraint, transaction, query count 검증.

`tests/real/`: 실제 DB/외부 서비스 연결. 기본 CI에서 제외.

fixture는 “테스트 의도를 숨기는 데이터 덩어리”가 되면 제거 대상입니다. 공통 fixture는 인증 사용자, 고정 시간, fake repository처럼 의미가 명확한 것만 남기고, 케이스별 핵심 데이터는 테스트 안에서 직접 드러내세요.

**RED 테스트 예시**

```python
# tests/isolated/unit/domain/test_order_confirm.py
import pytest

from apps.orders.domain import InvalidOrderState, Order, OrderStatus


def test_order_confirm_paid_order_marks_confirmed_and_records_event():
    order = Order.paid(order_id="order-1")

    event = order.confirm()

    assert order.status is OrderStatus.CONFIRMED
    assert event.order_id == "order-1"
    assert event.name == "OrderConfirmed"


def test_order_confirm_draft_order_raises_without_state_change():
    order = Order.draft(order_id="order-1")

    with pytest.raises(InvalidOrderState):
        order.confirm()

    assert order.status is OrderStatus.DRAFT
```

**예상 실패 이유**

현재 구조가 Django model/DB fixture에 로직을 묻어두고 있다면 `apps.orders.domain` 자체가 없거나, `Order.confirm()`이 DB 저장과 섞여 있어 위 테스트가 실패해야 정상입니다.

**GREEN 최소 구현 스케치**

```python
from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    DRAFT = "draft"
    PAID = "paid"
    CONFIRMED = "confirmed"


class InvalidOrderState(Exception):
    pass


@dataclass(frozen=True)
class OrderConfirmed:
    order_id: str
    name: str = "OrderConfirmed"


@dataclass
class Order:
    order_id: str
    status: OrderStatus

    @classmethod
    def draft(cls, order_id: str):
        return cls(order_id, OrderStatus.DRAFT)

    @classmethod
    def paid(cls, order_id: str):
        return cls(order_id, OrderStatus.PAID)

    def confirm(self) -> OrderConfirmed:
        if self.status is not OrderStatus.PAID:
            raise InvalidOrderState
        self.status = OrderStatus.CONFIRMED
        return OrderConfirmed(order_id=self.order_id)
```

**REFACTOR 방향**

Django model은 persistence adapter로 낮추고, 상태 전이와 불변식은 domain 객체로 옮깁니다. DB 통합 테스트는 “model field/constraint/repository가 domain 결과를 올바르게 저장하는가”만 검증합니다. 느린 경로에는 `django_assert_num_queries` 또는 `assertNumQueries`를 넣어 N+1 회귀를 잡습니다.

**실행 명령**

```bash
pytest tests/isolated/unit/domain -q
pytest tests/isolated/integration/django -q
pytest tests/isolated -q --durations=20
pytest tests/isolated/integration/django -q -m django_db
```

---
> **관련 스킬 참조:**
> - pytest 품질 개선과 fixture 정리 → **implementation-test** 스킬
> - RED/GREEN/REFACTOR 단계화 → **implementation-tdd** 스킬
> - Django DB 통합 테스트 경계 설정 → **implementation-django** 스킬