**검토 범위**

현재 `/private/tmp/dddjango-codex-eval`은 비어 있고 `config.toml`도 없어서 실제 테스트 파일을 읽거나 `pytest`를 실행할 수는 없었습니다. 따라서 아래는 “DB fixture 과의존 + 약한 assert”라는 증상에 대한 pytest/Django 품질 리뷰 기준입니다.

**주요 이슈**

[Independent / Repeatable] -- DB fixture에 지나치게 의존하면 테스트가 데이터셋의 암묵적 상태에 묶입니다. 어떤 레코드가 왜 필요한지 테스트 안에서 보이지 않고, fixture가 바뀌면 관련 없어 보이는 테스트가 깨집니다. JSON dump나 대형 seed fixture는 `tests/real/` 또는 좁은 통합 테스트로 제한하고, 대부분은 `factory_boy` 또는 명시적 pytest fixture로 필요한 데이터만 생성해야 합니다.

[AAA / Obscure Test] -- fixture가 테스트의 Arrange를 숨기면 테스트가 무엇을 검증하는지 읽기 어렵습니다. 테스트 본문에서 “이 조건 때문에 이 결과가 나온다”가 보여야 합니다. 공통 객체 생성은 fixture/factory로 빼되, 상태 변형은 테스트 안에서 명시하세요.

[Self-Validating / The Liar] -- `assert response.status_code == 200`, `assert obj is not None`, `assert len(items) > 0` 수준은 약합니다. 정상 응답 여부만 확인하고 비즈니스 결과, DB 상태 변화, 응답 schema, 권한 필터링, 부수효과를 검증하지 못합니다.

[Mutation Testing] -- 경계값이 없으면 `>`가 `>=`로 바뀌거나 조건이 반전돼도 테스트가 통과할 수 있습니다. 할인, 상태 전이, 권한, 수량, 날짜 범위 같은 조건은 `boundary - 1`, `boundary`, `boundary + 1`을 `parametrize`로 검증해야 합니다.

[Django Testing] -- DB가 필요 없는 도메인/서비스 테스트까지 `@pytest.mark.django_db`를 붙이면 피드백이 느려지고 설계 결합이 커집니다. 순수 로직은 `tests/isolated/unit/`에서 DB 없이 테스트하고, ORM query, constraint, transaction, `select_related/prefetch_related` 동작만 DB 테스트로 둡니다.

**개선 기준**

1. DB fixture는 “대형 공통 fixture”가 아니라 “테스트별 최소 데이터”로 바꿉니다.  
   기준: 테스트 하나가 필요한 모델 인스턴스를 1분 안에 설명할 수 있어야 합니다.

2. `factory_boy`를 기본 데이터 생성 방식으로 사용합니다.  
   기준: 상태별 객체는 `Trait`로 표현합니다. 예: `OrderFactory(paid=True)`, `UserFactory(is_staff=True)`.

3. DB 접근은 명시적으로 제한합니다.  
   기준: `@pytest.mark.django_db`가 붙은 테스트는 ORM 동작, constraint, transaction, queryset, view/API 통합 중 하나를 검증해야 합니다.

4. assertion은 결과 중심으로 강화합니다.  
   우선순위: 반환값 검증 > 상태 검증 > 외부 협력자 호출 검증.  
   기준: `status_code`만 확인하는 API 테스트는 실패입니다. 응답 body, DB 변화, 권한 필터링, 에러 메시지를 함께 검증해야 합니다.

5. 테스트 이름은 조건과 기대 결과를 포함합니다.  
   기준: `test_create_order`보다 `test_order_create_with_valid_items_persists_pending_order`처럼 읽혀야 합니다.

6. 성능 경로는 쿼리 수를 고정합니다.  
   기준: list/detail endpoint나 selector 테스트에는 `assertNumQueries` 또는 `django_assert_num_queries`를 사용합니다.

7. 외부 의존성은 실제 호출하지 않습니다.  
   기준: HTTP는 `responses`, 시간은 `time-machine`, Repository/Gateway는 `InMemoryFake` 또는 `create_autospec` 기반 double을 사용합니다.

**RED 예시**

```python
import pytest

from orders.models import Order
from orders.tests.factories import OrderFactory, UserFactory


@pytest.mark.django_db
def test_order_cancel_when_paid_marks_cancelled_and_restores_stock():
    user = UserFactory()
    order = OrderFactory(paid=True, user=user, item_count=2)

    result = cancel_order(order_id=order.id, requested_by=user)

    order.refresh_from_db()
    assert result.cancelled is True
    assert order.status == Order.Status.CANCELLED
    assert order.cancelled_by == user
    assert order.items.count() == 2
    assert all(item.stock_restored for item in order.items.all())
```

예상 실패 이유: 기존 테스트가 fixture의 주문 데이터 존재 여부나 `status_code == 200`만 확인하고 있다면, `cancel_order`의 반환 타입, 상태 전이, `cancelled_by`, 재고 복구 같은 실제 동작이 구현되어 있지 않아 실패해야 합니다.

**GREEN 최소 구현 방향**

```python
from dataclasses import dataclass
from django.db import transaction

@dataclass(frozen=True)
class CancelOrderResult:
    cancelled: bool


@transaction.atomic
def cancel_order(*, order_id: int, requested_by) -> CancelOrderResult:
    order = Order.objects.select_for_update().get(id=order_id, user=requested_by)
    order.status = Order.Status.CANCELLED
    order.cancelled_by = requested_by
    order.save(update_fields=["status", "cancelled_by"])

    for item in order.items.select_related("product"):
        item.restore_stock()

    return CancelOrderResult(cancelled=True)
```

**REFACTOR 방향**

DB fixture dump를 제거하고 `tests/isolated/factories.py` 또는 앱별 `tests/factories.py`로 옮기세요. 테스트는 `OrderFactory(paid=True)`처럼 필요한 상태만 선언하게 만들고, 공통 fixture는 `conftest.py`에서 function scope로 제공합니다. 약한 assertion은 mutation testing 관점으로 보강하고, 경계값은 `pytest.mark.parametrize`로 분리합니다.

실행 명령은 실제 프로젝트에서 다음처럼 나누는 것이 좋습니다.

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ -q
DJANGO_SETTINGS_MODULE=config.settings.test pytest tests/isolated/ --randomly-seed=last -q
mutmut run --paths-to-mutate "apps/" --tests-dir "tests/isolated/"
```

---
> **관련 스킬 참조:**
> - pytest 품질/fixture/assertion 개선 → **implementation-test** 스킬
> - Django 테스트 settings, ORM 테스트, Factory Boy → **implementation-django** 스킬
> - RED/GREEN/REFACTOR 기준 정리 → **implementation-tdd** 스킬