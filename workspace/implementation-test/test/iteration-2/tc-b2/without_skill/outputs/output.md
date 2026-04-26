# 테스트 코드 리뷰 -- 간헐적 실패 원인 분석

## 발견된 문제 요약

| # | 심각도 | 문제 | 해당 테스트 |
|---|--------|------|-------------|
| 1 | **Critical** | 모듈 레벨 공유 상태(`_db_store`)로 인한 테스트 간 간섭 | 거의 모든 테스트 |
| 2 | **Critical** | `test_expired_coupon_is_invalid` -- `timedelta(days=0)`와 `sleep(0.01)`에 의존하는 시간 기반 비결정성 | `test_expired_coupon_is_invalid` |
| 3 | **Medium** | `test_random_discount` -- `random.uniform` 사용으로 인한 비결정성 | `test_random_discount` |
| 4 | **Low** | 시간(clock)을 주입하지 않아 테스트가 실제 시스템 시간에 의존 | 다수 |

---

## 1. [Critical] 모듈 레벨 공유 상태 -- 테스트 간 간섭

### 문제

```python
_db_store = {}  # 모듈 레벨 전역 변수

def setup_module():
    global _db_store
    _db_store = {}  # 모듈 시작 시 한 번만 초기화

class FakeDB:
    def save(self, coupon):
        _db_store[coupon['code']] = coupon  # 모든 FakeDB 인스턴스가 같은 dict를 공유

    def find_by_code(self, code):
        return _db_store.get(code)
```

모든 `FakeDB` 인스턴스가 **동일한 전역 딕셔너리** `_db_store`를 공유한다. 각 테스트에서 `FakeDB()`를 새로 만들어도 실제로는 같은 저장소를 바라본다.

### 왜 간헐적으로 실패하는가

- pytest는 기본적으로 파일 내 정의 순서대로 테스트를 실행하지만, `pytest-randomly` 같은 플러그인이 설치되어 있거나 `--randomly-seed` 옵션이 활성화된 환경에서는 **실행 순서가 매번 달라진다.**
- 순서가 바뀌면, 앞선 테스트가 저장한 쿠폰(예: `'ONCE'`가 이미 `used=True`)이 뒤에 실행되는 테스트에 영향을 줄 수 있다.
- `setup_module`은 모듈 시작 시 한 번만 실행되므로, 테스트 개별 실행 사이에는 초기화가 일어나지 않는다.

### 구체적 시나리오

`test_multiple_coupons`가 먼저 실행되어 코드 `'A'`를 `used=True`로 만든 뒤, 다른 테스트가 같은 코드 `'A'`를 사용하려 하면 실패한다. 현재 코드에서는 쿠폰 코드가 겹치지 않아 직접적 충돌은 적지만, **`find_by_code`가 이전 테스트의 데이터를 반환할 가능성**이 항상 열려 있다.

### 수정 방법

각 테스트가 독립적인 저장소를 가지도록 `FakeDB`를 인스턴스 수준으로 변경한다.

```python
class FakeDB:
    def __init__(self):
        self._store = {}  # 인스턴스별 독립 저장소

    def save(self, coupon):
        self._store[coupon['code']] = coupon

    def find_by_code(self, code):
        return self._store.get(code)
```

또는 `setup_function` (테스트 함수마다 실행)으로 교체한다.

```python
def setup_function():
    global _db_store
    _db_store = {}
```

---

## 2. [Critical] `test_expired_coupon_is_invalid` -- 시간 경쟁 조건

### 문제

```python
def test_expired_coupon_is_invalid():
    db = FakeDB()
    service = CouponService(db)
    coupon = service.create_coupon('EXPIRED', 0.15, 0)  # valid_days=0
    time.sleep(0.01)  # 10ms 대기
    assert service.is_valid('EXPIRED') is False
```

`valid_days=0`이면 `expires_at = now + timedelta(days=0)` = `now`가 된다. 이후 `is_valid`에서:

```python
return self.clock.now() < coupon['expires_at']
```

`create_coupon` 시점의 `now()`와 `is_valid` 시점의 `now()`가 **같은 값**일 수 있다. `datetime.now()`의 해상도는 OS에 따라 다르며, 특히:

- macOS에서는 마이크로초 단위이므로 `sleep(0.01)` 후에는 대부분 다른 값이 나오지만, **시스템 부하가 높을 때** `sleep`이 예상보다 짧게 끝나거나, 타이밍이 미묘하게 겹칠 수 있다.
- `<` 비교이므로 `now() == expires_at`인 경우 `False`를 반환하여 테스트는 통과하지만, 이 동작이 의도한 것인지 불명확하다.

실제 간헐적 실패의 **핵심 원인**: `timedelta(days=0)`은 실제로는 "0초 후 만료"가 아니라 "생성 시점과 동일한 시각에 만료"를 의미한다. `sleep(0.01)`이 실제로 0.01초를 보장하지 않으며, `datetime.now()`의 해상도와 시스템 부하에 따라 결과가 달라진다.

### 수정 방법

`CouponService`에 이미 `clock` 파라미터가 있으므로, 이를 활용하여 시간을 제어한다.

```python
from unittest.mock import Mock

def test_expired_coupon_is_invalid():
    db = FakeDB()
    fake_clock = Mock()
    now = datetime(2024, 1, 1, 12, 0, 0)
    # create_coupon에서는 now를 반환, is_valid에서는 1일 후를 반환
    fake_clock.now.side_effect = [now, now + timedelta(days=1)]

    service = CouponService(db, clock=fake_clock)
    service.create_coupon('EXPIRED', 0.15, 0)
    assert service.is_valid('EXPIRED') is False
```

이렇게 하면 `time.sleep`이 필요 없고, 결과가 항상 결정적이다.

---

## 3. [Medium] `test_random_discount` -- 비결정적 테스트 데이터

### 문제

```python
def test_random_discount():
    db = FakeDB()
    service = CouponService(db)
    discount = random.uniform(0.05, 0.5)
    service.create_coupon('RANDOM', discount, 30)
    result = service.apply_coupon('RANDOM', 10000)
    assert result == 10000 * (1 - discount)
```

이 테스트 자체는 현재 동일한 `discount` 변수를 사용하므로 산술적으로는 항상 통과해야 한다. 그러나:

- **부동소수점 비교**: `==`로 float를 비교하고 있다. 현재 구현에서는 같은 `discount` 값으로 같은 연산을 수행하므로 결과가 동일하겠지만, 향후 로직이 바뀌면 (예: 반올림 추가) 즉시 깨진다.
- **재현 불가**: 실패 시 어떤 `discount` 값으로 실패했는지 로그에 남지 않아 디버깅이 어렵다.
- **테스트 원칙 위반**: 테스트는 결정적(deterministic)이어야 한다. `random`을 사용하면 같은 코드로 다른 결과를 낼 수 있다.

### 수정 방법

고정된 값을 사용하거나, 여러 케이스를 `@pytest.parametrize`로 명시한다.

```python
@pytest.parametrize("discount,expected", [
    (0.1, 9000),
    (0.2, 8000),
    (0.5, 5000),
])
def test_discount_calculation(discount, expected):
    db = FakeDB()
    service = CouponService(db, clock=...)
    service.create_coupon('DISC', discount, 30)
    result = service.apply_coupon('DISC', 10000)
    assert result == expected
```

---

## 4. [Low] 시간(clock) 미주입 -- 시스템 시간 의존

### 문제

```python
def test_create_coupon():
    ...
    assert coupon['expires_at'] > datetime.now()  # 시스템 시간에 의존
```

`CouponService`는 `clock` 파라미터를 받을 수 있도록 설계되어 있지만, 대부분의 테스트에서 이를 활용하지 않고 기본값 `datetime`을 사용한다. 이는:

- `create_coupon` 내부의 `datetime.now()`와 assert 내부의 `datetime.now()` 사이에 **극히 드물게** 날짜가 바뀔 수 있다 (자정 경계).
- 테스트가 시스템 시간에 의존하므로 재현성이 떨어진다.

### 수정 방법

모든 테스트에서 `clock`을 Mock으로 주입한다.

```python
def make_fixed_clock(fixed_time):
    clock = Mock()
    clock.now.return_value = fixed_time
    return clock

def test_create_coupon():
    db = FakeDB()
    now = datetime(2024, 6, 1, 12, 0, 0)
    service = CouponService(db, clock=make_fixed_clock(now))
    coupon = service.create_coupon('SUMMER2024', 0.2, 30)
    assert coupon['expires_at'] == now + timedelta(days=30)
```

---

## 전체 수정 제안 코드

```python
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta


class FakeDB:
    """각 인스턴스가 독립적인 저장소를 가진다."""
    def __init__(self):
        self._store = {}

    def save(self, coupon):
        self._store[coupon['code']] = coupon

    def find_by_code(self, code):
        return self._store.get(code)


def make_fixed_clock(fixed_time: datetime):
    """고정된 시간을 반환하는 clock Mock을 생성한다."""
    clock = Mock()
    clock.now.return_value = fixed_time
    return clock


FIXED_NOW = datetime(2024, 6, 1, 12, 0, 0)


def test_create_coupon():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    coupon = service.create_coupon('SUMMER2024', 0.2, 30)
    assert coupon['code'] == 'SUMMER2024'
    assert coupon['discount'] == 0.2
    assert coupon['expires_at'] == FIXED_NOW + timedelta(days=30)


def test_coupon_is_valid():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    service.create_coupon('VALID10', 0.1, 30)
    assert service.is_valid('VALID10') is True


def test_expired_coupon_is_invalid():
    db = FakeDB()
    create_time = FIXED_NOW
    check_time = FIXED_NOW + timedelta(days=1)
    clock = Mock()
    clock.now.side_effect = [create_time, check_time]
    service = CouponService(db, clock=clock)
    service.create_coupon('EXPIRED', 0.15, 0)
    assert service.is_valid('EXPIRED') is False


def test_apply_coupon():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    service.create_coupon('APPLY20', 0.2, 30)
    result = service.apply_coupon('APPLY20', 10000)
    assert result == 8000


def test_apply_used_coupon():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    service.create_coupon('ONCE', 0.1, 30)
    service.apply_coupon('ONCE', 5000)
    with pytest.raises(ValueError, match='유효하지 않은 쿠폰'):
        service.apply_coupon('ONCE', 3000)


def test_nonexistent_coupon():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    assert service.is_valid('NONEXIST') is False


@pytest.parametrize("discount,expected", [
    (0.1, 9000.0),
    (0.2, 8000.0),
    (0.5, 5000.0),
])
def test_discount_calculation(discount, expected):
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    service.create_coupon('DISC', discount, 30)
    result = service.apply_coupon('DISC', 10000)
    assert result == expected


def test_multiple_coupons():
    db = FakeDB()
    clock = make_fixed_clock(FIXED_NOW)
    service = CouponService(db, clock=clock)
    service.create_coupon('A', 0.1, 30)
    service.create_coupon('B', 0.2, 30)
    service.create_coupon('C', 0.3, 30)

    assert service.is_valid('A')
    assert service.is_valid('B')
    assert service.is_valid('C')

    service.apply_coupon('A', 1000)
    assert not service.is_valid('A')
    assert service.is_valid('B')
    assert service.is_valid('C')
```

---

## 결론

간헐적 실패의 **가장 유력한 원인 두 가지**:

1. **전역 `_db_store` 공유** -- 테스트 실행 순서가 바뀌면(pytest-randomly 등) 이전 테스트의 데이터가 남아 다른 테스트에 영향을 준다. `setup_module`은 모듈 시작 시 한 번만 초기화하므로 테스트 간 격리가 안 된다.

2. **`test_expired_coupon_is_invalid`의 `time.sleep(0.01)` + `timedelta(days=0)`** -- 시스템 부하에 따라 타이밍이 달라지는 비결정적 테스트. `CouponService`에 이미 존재하는 `clock` 의존성 주입을 활용하면 완전히 해결된다.

핵심 원칙: **테스트는 실행 순서와 시스템 상태에 무관하게 항상 같은 결과를 내야 한다.** 전역 상태 제거, 시간 Mock 주입, 랜덤 값 제거로 이 원칙을 달성할 수 있다.
