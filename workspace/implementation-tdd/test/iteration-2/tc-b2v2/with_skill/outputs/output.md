# InventoryService 테스트 코드 리뷰

## 잘된 점

테스트 구조가 전반적으로 깔끔하다. 클래스 단위로 관심사를 분리했고, pytest fixture를 사용하여 테스트 격리를 확보했으며, AAA(Arrange-Act-Assert) 패턴이 잘 드러난다. `check_availability` 테스트는 반환값만 검증하는 출력 기반 테스트로, 리팩토링 내성이 높다. 예외 케이스(`test_raises_for_unknown_product`, `test_unavailable_for_unknown_product`)도 빠지지 않았다.

---

## 개선 사항

### 1. `test_increases_stock` -- Eager Test (하나의 테스트에서 두 가지 관심사를 검증)

```python
def test_increases_stock(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}
    repo.save.return_value = None

    result = service.add_stock('P1', 5)

    assert result['stock'] == 15
    repo.find.assert_called_once_with('P1')   # <-- 문제
    repo.save.assert_called_once()             # <-- 문제
```

[Eager Test + 통신 기반 테스트 혼용] -- 이 테스트의 이름은 "재고가 증가한다"인데, 실제로는 재고 증가(상태 검증)와 repo 호출 여부(통신 기반 검증)를 동시에 확인한다. 테스트가 실패하면 재고 계산이 틀린 것인지, repo 호출 방식이 바뀐 것인지 즉시 알 수 없다(Assertion Roulette). `repo.find.assert_called_once_with('P1')`과 `repo.save.assert_called_once()`는 내부 구현 세부사항에 결합된 검증이므로, 이 테스트의 본래 목적인 "재고가 15가 되었는가"라는 핵심 단언과 분리해야 한다.

---

### 2. `test_increases_stock`에서 `repo.save` 호출에 대한 약한 단언

```python
repo.save.assert_called_once()
```

[약한 단언(Weak Assertion)] -- `save`가 호출되었는지만 확인하고, 어떤 인자로 호출되었는지는 검증하지 않는다. 만약 `save`에 잘못된 데이터가 전달되는 버그가 생겨도 이 테스트는 통과한다. 통신 기반 검증을 하기로 했다면, 최소한 저장되는 데이터의 정합성까지 확인해야 회귀 방지 가치가 있다.

```python
# 개선: 저장 데이터까지 검증
repo.save.assert_called_once_with({'id': 'P1', 'name': '키보드', 'stock': 15})
```

---

### 3. `test_publishes_event` -- 상태 검증이 가능한 곳에서 통신 기반 테스트만 사용

```python
def test_publishes_event(self, service, repo, event_bus):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}

    service.add_stock('P1', 5)

    event_bus.publish.assert_called_once_with(
        'stock_added', {'product_id': 'P1', 'quantity': 5}
    )
```

[통신 기반 테스트의 적절성] -- `event_bus`는 외부 시스템과의 통신 경계이므로 Mock 사용 자체는 적절하다(런던 학파). 다만 이 테스트는 재고가 실제로 올바르게 변경되었는지는 전혀 확인하지 않는다. 이벤트 발행만 검증하므로, 재고 업데이트 없이 이벤트만 발행하는 버그를 잡을 수 없다. `add_stock`의 핵심 행위인 재고 변경 결과를 함께 확인하거나, 최소한 `test_increases_stock`이 그 역할을 온전히 수행하도록 보장해야 한다.

---

### 4. `repo`에 대한 Mock 사용 -- 내부 협력 객체를 Mock으로 대체

[리팩토링 내성 저하 (Mock 과용)] -- `repo`는 외부 시스템(DB)에 대한 추상화이므로 Mock 사용이 정당화될 수 있다. 그러나 현재 `InventoryService`는 `repo.find()` 반환값을 직접 조작하는 dict 기반 로직이다. `repo` 내부 구현이 바뀌면(예: `find` 대신 `get`, 반환 타입이 dict에서 dataclass로 변경) 모든 테스트가 동시에 깨진다. Khorikov의 권고에 따르면, 가능한 경우 인메모리 Fake 구현체를 사용하는 것이 리팩토링 내성을 높인다.

```python
# 개선 방향: 인메모리 Fake Repository
class FakeProductRepo:
    def __init__(self, products=None):
        self.products = {p['id']: p for p in (products or [])}

    def find(self, product_id):
        return self.products.get(product_id)

    def save(self, product):
        self.products[product['id']] = product
```

이렇게 하면 `assert_called_once_with` 같은 구현 결합 검증 없이, 순수하게 상태 기반으로 결과를 확인할 수 있다.

---

### 5. 경계값 테스트 누락

[누락된 경계/엣지 케이스] -- 다음 시나리오에 대한 테스트가 없다:

- **재고가 정확히 요청량과 같을 때** (`stock == requested`): `check_availability`에서 `>=` 연산의 경계값
- **수량 0 또는 음수**: `add_stock('P1', 0)` 또는 `add_stock('P1', -3)`이 호출되면 어떻게 되는가? 현재 구현은 음수 재고를 허용한다
- **재고 0인 상품**: `stock`이 0인 상태에서 `check_availability` 호출

경계값은 버그가 가장 많이 발생하는 지점이므로, 회귀 방지를 위해 반드시 포함해야 한다.

```python
# 경계값 테스트 예시
def test_available_when_stock_equals_requested(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'stock': 5}
    assert service.check_availability('P1', 5) is True

def test_add_stock_with_zero_quantity(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}
    result = service.add_stock('P1', 0)
    assert result['stock'] == 10
```

---

### 6. Hard-Coded Test Data의 의미 불명확

[Hard-Coded Test Data] -- `10`, `5`, `3` 같은 숫자가 반복되지만, 왜 그 값인지 의도가 드러나지 않는다. 테스트 데이터 간의 차이에 의미가 있어야 한다(Testing Patterns: "데이터 간에 차이가 있다면 그 속에 어떤 의미가 있어야 한다").

```python
# 개선: 의미 있는 변수명으로 관계를 드러냄
def test_unavailable_when_insufficient(self, service, repo):
    current_stock = 3
    requested_quantity = 5  # current_stock보다 큰 값
    repo.find.return_value = {'id': 'P1', 'stock': current_stock}

    assert service.check_availability('P1', requested_quantity) is False
```

---

## 리뷰 체크리스트 검증 결과

| 항목 | 판정 |
|------|------|
| 테스트-후-작성 (test-last) | 해당 없음 (코드와 테스트가 함께 제공됨) |
| Red-Green-Refactor 사이클 부재 | 해당 없음 (코드와 테스트가 함께 제공됨) |
| 구현에 결합된 테스트 (낮은 리팩토링 내성) | **발견** -- `test_increases_stock`의 `assert_called_once_with`, `assert_called_once` |
| 내부 협력 객체에 대한 Mock 과용 | **발견** -- `repo`를 Fake로 대체하면 더 나은 리팩토링 내성 확보 가능 |
| 테스트 격리 부재 | 해당 없음 -- fixture 사용으로 격리 양호 |
| 테스트 냄새 | **발견** -- Eager Test (`test_increases_stock`), 약한 Assertion Roulette 가능성 |
| 점진적 개발 부재 | 해당 없음 |
| 출력 기반으로 충분한 곳에서 통신 기반 사용 | **발견** -- `test_increases_stock`에서 상태 검증과 통신 검증 혼재 |
| 경계/엣지 케이스 누락 | **발견** -- 경계값(stock == requested), 비정상 입력(0, 음수) 미검증 |
| 설계를 이끌지 않는 테스트 | 해당 없음 |
