# Test Code Review: OrderService

전반적으로 잘 작성된 테스트 코드다. 먼저 잘한 점을 짚고, 이후 개선 사항을 다룬다.

## 잘한 점

- **`create_autospec` 사용**: `OrderRepository`와 `PaymentGateway`에 `create_autospec`을 사용하여 존재하지 않는 메서드 호출이나 잘못된 시그니처를 컴파일 타임에 잡아낸다. spec 없는 Mock 사용의 대표적 함정을 피한 점이 좋다.
- **AAA 패턴 준수**: 모든 테스트가 Arrange-Act-Assert 구조를 명확히 따르며, Act 섹션이 단일 호출로 깔끔하다.
- **테스트 독립성**: fixture를 function scope로 사용하여 테스트 간 상태 공유가 없다. 어떤 순서로 실행해도 결과가 동일하다.
- **클래스 기반 그룹화**: `TestPlaceOrder`와 `TestConfirmOrder`로 관련 테스트를 논리적으로 묶었다.
- **부정 경로 테스트**: 0 금액, 음수 금액, 주문 미존재, 결제 실패 등 예외 경로를 빠짐없이 다루고 있다.
- **`test_does_not_save_on_payment_failure`**: 결제 실패 시 저장이 호출되지 않음을 검증하는 것은 중요한 비즈니스 규칙이다. 이것은 외부 시스템과의 통신을 검증하는 것이므로 communication-based 검증이 적절하다.

## 개선 사항

### 1. 검증 방식 우선순위 개선 -- 출력 기반 검증을 우선하라

[Test Doubles - 검증 방식 우선순위] -- 출력 기반 > 상태 기반 > 통신 기반 순서로 검증해야 한다. 통신 기반 검증(mock.assert_called)은 구현 세부사항에 결합되어, 내부 리팩토링 시 테스트가 깨질 수 있다.

`test_creates_order_with_correct_total`에서 `repo.save.assert_called_once()`와 `repo.save.call_args[0][0]`을 통한 검증은 save의 호출 방식(위치 인자 vs 키워드 인자)에 결합되어 있다. 반환값인 `result`에 이미 필요한 정보가 모두 담겨 있으므로, 출력 기반 검증으로 전환할 수 있다.

```
[Before]
repo.save.assert_called_once()
saved_order = repo.save.call_args[0][0]
assert saved_order['total'] == 3500
assert saved_order['status'] == 'pending'
assert result['id'] == 1

[After]
assert result['id'] == 1
assert result['total'] == 3500
assert result['status'] == 'pending'

[Reason] 검증 방식 우선순위 -- 출력 기반 검증이 통신 기반보다 리팩토링 내성이 높다.
save의 호출 여부는 반환값이 존재하는 것 자체로 간접 검증된다.
```

### 2. 반복되는 테스트 케이스에 parametrize 적용

[pytest Fixtures - 파라미터화] -- 동일한 행위를 다른 데이터로 반복 검증하는 테스트는 `parametrize`로 통합하면 의도가 더 명확하고, 새 케이스 추가가 쉬워진다.

`test_rejects_zero_total`과 `test_rejects_negative_total`은 동일한 로직(금액이 0 이하면 ValueError)을 다른 입력으로 검증한다.

```
[Before]
def test_rejects_zero_total(self, service):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order([{'price': 0, 'quantity': 1}])

def test_rejects_negative_total(self, service):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order([{'price': -100, 'quantity': 1}])

[After]
@pytest.mark.parametrize("items, desc", [
    ([{'price': 0, 'quantity': 1}], "zero total"),
    ([{'price': -100, 'quantity': 1}], "negative total"),
])
def test_rejects_invalid_total(self, service, items, desc):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order(items)

[Reason] 파라미터화 -- 동일 행위에 대한 반복 테스트를 통합하여 의도를 명확히 하고,
경계값 케이스를 추가하기 쉬운 구조로 만든다.
```

### 3. 경계값 테스트 추가 -- 뮤테이션에 강한 테스트로

[Mutation Testing - 경계값] -- 비교 연산자(`<=`)가 `<`로 변형되면 현재 테스트는 이를 잡지 못한다. 경계값(total이 정확히 0인 경우와 아주 작은 양수)을 추가해야 뮤턴트를 죽일 수 있다.

`place_order`에서 `total <= 0` 조건을 사용하는데, 현재 테스트에는 `total > 0`인 정상 케이스(3500)와 `total == 0`, `total < 0`인 예외 케이스만 있다. `total`이 매우 작은 양수(예: 1)인 경우를 추가하면 `<= 0`이 `< 0`으로 변형될 때 잡아낼 수 있다.

```python
# 경계값: 최소 양수 금액은 주문 가능해야 한다
def test_accepts_minimal_positive_total(self, service, repo):
    repo.save.side_effect = lambda o: {**o, 'id': 2}
    items = [{'price': 1, 'quantity': 1}]

    result = service.place_order(items)

    assert result['total'] == 1
```

위 parametrize와 결합하면 아래처럼도 가능하다:

```python
@pytest.mark.parametrize("items, desc", [
    ([{'price': 0, 'quantity': 1}], "zero total"),
    ([{'price': -100, 'quantity': 1}], "negative total"),
    ([{'price': -1, 'quantity': 1}], "boundary: -1"),
])
def test_rejects_invalid_total(self, service, items, desc):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order(items)
```

### 4. `confirm_order`에서 통신 기반 검증 재고

[Test Doubles - 검증 방식 우선순위] -- `test_confirms_and_charges`에서 `repo.find_by_id.assert_called_once_with(1)`와 `payment.charge.assert_called_once_with(5000)`은 내부 호출 순서에 결합된다. `payment.charge`는 외부 의존성이므로 통신 기반 검증이 적절하지만, `repo.find_by_id`는 내부 구현 상세에 해당한다.

```
[Before]
repo.find_by_id.assert_called_once_with(1)
payment.charge.assert_called_once_with(5000)
repo.save.assert_called_once()
assert result['status'] == 'confirmed'

[After]
payment.charge.assert_called_once_with(5000)
assert result['status'] == 'confirmed'
assert result['id'] == 1

[Reason] 검증 방식 우선순위 -- repo.find_by_id 호출 검증은 The Inspector 안티패턴이다.
find_by_id가 올바르게 작동하지 않으면 result 자체가 잘못되므로 출력 기반 검증으로 충분하다.
payment.charge는 외부 결제 시스템이므로 통신 기반 검증이 적절하다.
```

### 5. Fake Repository 도입 고려

[Test Doubles - Fake] -- OrderRepository는 핵심 비즈니스 로직의 내부 협력자에 해당한다. 모든 테스트에서 `repo.save.side_effect = lambda o: ...`로 동작을 직접 구성하는 것은, Repository가 복잡해질수록 유지보수 부담이 커진다. 간단한 Fake를 만들면 더 자연스러운 테스트가 된다.

```python
class FakeOrderRepository:
    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id = 1

    def save(self, order: dict) -> dict:
        if 'id' not in order:
            order['id'] = self._next_id
            self._next_id += 1
        self._store[order['id']] = order
        return order

    def find_by_id(self, order_id: int) -> dict | None:
        return self._store.get(order_id)
```

이를 사용하면 `test_confirms_and_charges` 같은 테스트에서 place_order -> confirm_order 흐름을 자연스럽게 테스트할 수 있고, Mock의 세부 설정 없이도 실제 동작을 검증할 수 있다. 다만 현재 테스트 규모에서는 mock이 충분히 관리 가능하므로, Repository 인터페이스가 커질 때 전환을 검토하면 된다.

## Review Checklist

| 항목 | 결과 |
|------|------|
| 여러 Act 섹션이 있는 테스트 | 해당 없음 -- 모두 단일 Act |
| 테스트 간 공유 가변 상태 | 해당 없음 -- fixture가 function scope |
| Mock 과용 | 경미 -- repo는 Fake 전환 고려 가능 (항목 5) |
| spec/autospec 누락 | 해당 없음 -- create_autospec 사용 |
| Flaky 테스트 | 해당 없음 -- 외부 의존 없음 |
| parametrize 누락 | 해당 -- zero/negative total 테스트 통합 가능 (항목 2) |
| 과도한 setup | 해당 없음 -- 간결한 fixture |
| 구현 상세 결합 (The Inspector) | 해당 -- call_args, find_by_id 검증 (항목 1, 4) |
| 의미 없는 assertion (The Liar) | 해당 없음 -- 모든 assert가 구체적 |
| 잘못된 테스트 레벨 | 해당 없음 -- 단위 테스트가 적절 |

## 요약

잘 구조화된 테스트다. `create_autospec` 사용, 명확한 AAA 구조, 예외 경로 커버리지 모두 좋다. 가장 영향력 있는 개선은 (1) 통신 기반 검증을 출력 기반으로 전환하여 리팩토링 내성을 높이는 것과 (2) 경계값 테스트를 추가하여 뮤테이션 테스트에 강하게 만드는 것이다.
