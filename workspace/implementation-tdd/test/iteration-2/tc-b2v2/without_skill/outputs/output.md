# 테스트 코드 리뷰

## 1. 핵심 문제: Mock 객체의 부작용으로 인한 테스트 간 간섭

가장 중요한 구조적 문제가 하나 있다. `repo` fixture가 반환하는 dict 객체가 **mutable**하다는 점이다.

```python
repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}
```

`return_value`에 dict를 할당하면, `repo.find()`를 호출할 때마다 **동일한 dict 인스턴스**가 반환된다. `add_stock`이 `product['stock'] += quantity`로 이 dict를 직접 변경하므로, 같은 테스트 메서드 안에서 `repo.find`를 두 번 호출하면 이미 변경된 값이 돌아온다. 현재 테스트들은 한 메서드 안에서 한 번만 호출하므로 당장 깨지지 않지만, 테스트를 확장하는 순간 함정에 빠진다.

**개선:** `side_effect`로 매 호출마다 새 dict를 반환하거나, 테스트 데이터 팩토리 함수를 쓴다.

```python
def make_product(stock=10):
    return {'id': 'P1', 'name': '키보드', 'stock': stock}

repo.find.side_effect = lambda pid: make_product()
```

---

## 2. `test_increases_stock`에서 save 인자 미검증

```python
repo.save.assert_called_once()
```

`save`가 호출되었는지만 확인하고, **어떤 값으로** 호출되었는지 검증하지 않는다. stock이 15로 바뀐 product가 전달되었는지 확인해야 한다.

**개선:**

```python
repo.save.assert_called_once_with({'id': 'P1', 'name': '키보드', 'stock': 15})
```

---

## 3. 이벤트 미발행 검증 누락 (`test_increases_stock`)

`test_increases_stock`는 stock 증가와 repo 저장만 검증하고, event_bus를 주입받지 않아 이벤트 발행 여부를 확인하지 않는다. 반대로 `test_publishes_event`는 이벤트만 확인하고 repo.save는 검증하지 않는다.

분리 자체는 괜찮은 설계 판단이지만, `test_increases_stock`에서 **event_bus가 불필요하게 호출되지 않았는지**는 확인할 필요가 없더라도, `test_publishes_event`에서 save가 이벤트 발행 **이전에** 호출되었는지(순서 보장)는 비즈니스적으로 중요할 수 있다.

**개선 (호출 순서 검증이 필요한 경우):**

```python
from unittest.mock import call

def test_saves_before_publishing(self, service, repo, event_bus):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}

    service.add_stock('P1', 5)

    # save가 publish보다 먼저 호출되었는지 확인
    manager = Mock()
    manager.attach_mock(repo.save, 'save')
    manager.attach_mock(event_bus.publish, 'publish')
    # ... 또는 호출 시점을 기록하는 side_effect를 사용
```

---

## 4. 경계값 테스트 부재

`check_availability`에서 `stock == requested`인 경우(경계값)에 대한 테스트가 없다.

**개선:**

```python
def test_available_when_exact_stock(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'stock': 5}
    assert service.check_availability('P1', 5) is True
```

---

## 5. `add_stock`에서 quantity가 0이나 음수인 경우 미검증

프로덕션 코드에 음수/0 방어 로직이 없고, 테스트에서도 이 경우를 다루지 않는다. 비즈니스 로직상 음수 수량은 허용되어서는 안 된다.

**개선 (프로덕션 코드에 방어 로직 추가 후):**

```python
def test_raises_for_zero_quantity(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}
    with pytest.raises(ValueError):
        service.add_stock('P1', 0)

def test_raises_for_negative_quantity(self, service, repo):
    repo.find.return_value = {'id': 'P1', 'name': '키보드', 'stock': 10}
    with pytest.raises(ValueError):
        service.add_stock('P1', -3)
```

---

## 6. `raises_for_unknown_product`에서 event_bus 미호출 검증 누락

상품이 없어서 예외가 발생하면, event_bus.publish가 호출되지 **않아야** 한다. 현재 이를 검증하지 않는다.

**개선:**

```python
def test_raises_for_unknown_product(self, service, repo, event_bus):
    repo.find.return_value = None

    with pytest.raises(ValueError, match='상품 P1 없음'):
        service.add_stock('P1', 5)

    event_bus.publish.assert_not_called()
    repo.save.assert_not_called()
```

---

## 7. 테스트 데이터 중복

`{'id': 'P1', 'name': '키보드', 'stock': 10}` 동일한 dict가 여러 테스트에 반복된다. 팩토리 함수나 fixture로 추출하면 유지보수성이 올라간다.

**개선:**

```python
@pytest.fixture
def keyboard_product():
    def _make(stock=10):
        return {'id': 'P1', 'name': '키보드', 'stock': stock}
    return _make
```

---

## 요약 (심각도 순)

| 순위 | 문제 | 심각도 |
|------|------|--------|
| 1 | mutable return_value로 인한 잠재적 테스트 간 간섭 | 높음 |
| 2 | `repo.save` 호출 인자 미검증 | 높음 |
| 3 | 예외 경로에서 save/publish 미호출 미검증 | 중간 |
| 4 | 경계값(stock == requested) 테스트 부재 | 중간 |
| 5 | 음수/0 quantity 방어 테스트 부재 | 중간 |
| 6 | 저장-이벤트 발행 순서 미검증 | 낮음 |
| 7 | 테스트 데이터 중복 | 낮음 |
