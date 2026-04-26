# 테스트 코드 리뷰

## 총평

전반적으로 잘 작성된 테스트 코드입니다. `create_autospec` 사용, fixture 분리, 클래스 기반 테스트 그룹핑, 에러 메시지 매칭 등 좋은 관행을 따르고 있습니다. 아래에 더 나아질 수 있는 개선점을 정리했습니다.

---

## 잘한 점

1. **`create_autospec` 사용** -- 일반 `Mock()` 대신 `create_autospec`을 써서 실제 인터페이스와 시그니처가 맞지 않으면 테스트가 실패합니다. Mock의 가장 큰 함정(인터페이스 변경 시 테스트가 여전히 통과하는 문제)을 방지하는 좋은 선택입니다.
2. **테스트 클래스 그룹핑** -- `TestPlaceOrder`와 `TestConfirmOrder`로 관심사를 분리했습니다.
3. **에러 메시지 매칭** -- `pytest.raises(ValueError, match='...')`로 단순 예외 타입뿐 아니라 메시지까지 검증합니다.
4. **부수효과 미발생 검증** -- `test_does_not_save_on_payment_failure`에서 결제 실패 시 `save`가 호출되지 않음을 명시적으로 확인합니다.

---

## 개선 제안

### 1. 빈 리스트 입력에 대한 테스트 누락

현재 프로덕션 코드에서 `place_order([])`를 호출하면 `total`이 0이 되어 `ValueError`가 발생합니다. 이 경우를 명시적으로 테스트하는 것이 좋습니다. 빈 주문은 "금액이 0"과는 다른 의미이므로 별도 테스트 케이스로 분리하면 의도가 명확해집니다.

```python
def test_rejects_empty_items(self, service):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order([])
```

### 2. 테스트 이름에서 행위를 더 구체적으로 표현

일부 테스트 이름이 "무엇을 하는가"보다 "어떤 상황인가"에 초점이 맞춰져 있습니다. 테스트 이름은 `test_<상황>_<기대결과>` 형식이면 실패 시 원인 파악이 빨라집니다.

```python
# 현재
def test_rejects_zero_total(self, service):

# 개선 -- 좀 더 구체적
def test_place_order_with_zero_total_raises_value_error(self, service):
```

모든 이름을 바꿀 필요는 없지만, `test_confirms_and_charges` 같은 이름은 두 가지를 동시에 설명하려 해서 약간 모호합니다. 하나의 테스트가 하나의 행위를 검증한다는 원칙과 이름을 맞추면 좋습니다.

### 3. `test_confirms_and_charges`가 너무 많은 것을 검증

이 테스트는 하나의 메서드 안에서 네 가지를 동시에 assert합니다:
- `find_by_id` 호출 여부
- `charge` 호출 여부 및 인자
- `save` 호출 여부
- `status` 변경 확인

하나가 실패하면 나머지 assert는 실행되지 않아 디버깅이 어려워질 수 있습니다. 역할별로 분리하는 것을 고려해 보세요.

```python
def test_confirm_order_charges_correct_amount(self, service, repo, payment):
    repo.find_by_id.return_value = {'id': 1, 'total': 5000, 'status': 'pending'}
    payment.charge.return_value = True
    repo.save.side_effect = lambda o: o

    service.confirm_order(1)

    payment.charge.assert_called_once_with(5000)

def test_confirm_order_updates_status_to_confirmed(self, service, repo, payment):
    repo.find_by_id.return_value = {'id': 1, 'total': 5000, 'status': 'pending'}
    payment.charge.return_value = True
    repo.save.side_effect = lambda o: o

    result = service.confirm_order(1)

    assert result['status'] == 'confirmed'
```

다만, 이것은 트레이드오프입니다. 테스트 수가 늘어나고 setup 중복이 생기므로, 팀의 선호에 따라 현재 방식을 유지해도 괜찮습니다.

### 4. `side_effect = lambda o: o` 대신 `return_value` 활용 고려

`repo.save.side_effect = lambda o: {**o, 'id': 1}` 패턴은 입력을 변환해서 반환하는 것이라 `side_effect`가 적절합니다. 그러나 `test_confirms_and_charges`에서 `lambda o: o`는 입력을 그대로 돌려주는 것인데, 이 경우 테스트에서 실제로 `save`의 반환값을 사용하지 않으므로 불필요한 설정입니다. 제거해도 테스트 결과에 영향이 없습니다.

```python
# 현재 -- save의 반환값을 사용하지 않으므로 불필요
repo.save.side_effect = lambda o: o

# 개선 -- 제거하거나, 반환값이 필요하다면 명시적으로
# (confirm_order는 save 반환값을 사용하지 않고 order를 직접 반환)
```

### 5. `@pytest.mark.parametrize`로 유사 케이스 통합

`test_rejects_zero_total`과 `test_rejects_negative_total`은 같은 로직을 다른 입력으로 검증합니다. parametrize로 통합하면 새로운 엣지 케이스 추가가 쉬워집니다.

```python
@pytest.mark.parametrize("items, description", [
    ([{'price': 0, 'quantity': 1}], "zero total"),
    ([{'price': -100, 'quantity': 1}], "negative total"),
    ([], "empty items"),
])
def test_rejects_invalid_order_total(self, service, items, description):
    with pytest.raises(ValueError, match='유효하지 않습니다'):
        service.place_order(items)
```

### 6. 결제 실패 시 상태가 변경되지 않았는지 검증 누락

`test_raises_on_payment_failure`에서 예외 발생은 확인하지만, order 딕셔너리의 `status`가 여전히 `'pending'`인지는 검증하지 않습니다. 현재 프로덕션 코드는 `charge` 실패 시 바로 예외를 던지므로 문제가 없지만, 향후 코드 변경 시 상태가 실수로 바뀌는 것을 방어할 수 있습니다.

```python
def test_status_remains_pending_on_payment_failure(self, service, repo, payment):
    order = {'id': 1, 'total': 5000, 'status': 'pending'}
    repo.find_by_id.return_value = order
    payment.charge.return_value = False

    with pytest.raises(RuntimeError):
        service.confirm_order(1)

    assert order['status'] == 'pending'
```

### 7. `import Mock`이 사용되지 않음

파일 상단에서 `Mock`을 import하지만 실제로 사용하지 않습니다. 불필요한 import는 제거하는 것이 깔끔합니다.

```python
# 현재
from unittest.mock import Mock, create_autospec

# 개선
from unittest.mock import create_autospec
```

### 8. `place_order`에서 `save` 호출 인자 검증 방식 개선

현재 `call_args[0][0]`으로 위치 인자를 꺼내는 방식은 동작하지만, 인덱스 기반 접근이라 가독성이 떨어집니다. `call_args.args` (Python 3.8+) 또는 직접 기대값을 `assert_called_once_with`로 검증하는 것이 더 읽기 좋습니다.

```python
# 현재
saved_order = repo.save.call_args[0][0]
assert saved_order['total'] == 3500

# 대안 1: call_args.args 사용 (더 명시적)
saved_order = repo.save.call_args.args[0]

# 대안 2: assert_called_once_with 사용 (전체 인자를 한번에 검증)
repo.save.assert_called_once_with({
    'items': items,
    'total': 3500,
    'status': 'pending',
})
```

대안 2는 전체 딕셔너리를 비교하므로 예상치 못한 필드가 추가되었을 때도 잡아냅니다.

---

## 요약

| 구분 | 항목 |
|------|------|
| 우선순위 높음 | 빈 리스트 엣지 케이스 추가, 미사용 import 제거 |
| 우선순위 중간 | parametrize 활용, 결제 실패 시 상태 불변 검증, 불필요한 side_effect 제거 |
| 우선순위 낮음 | 테스트 이름 구체화, 하나의 테스트에서 다중 assert 분리, call_args 접근 방식 개선 |

전체적으로 mock 사용, 예외 검증, 구조화 등의 기본기가 잘 갖춰진 테스트입니다. 위 개선점은 "나쁘다"가 아니라 "더 좋아질 수 있다"의 관점입니다.
