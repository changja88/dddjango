# CouponService 테스트 코드 리뷰

## 잘 된 점

테스트 전반적으로 CouponService의 핵심 행위(생성, 유효성 검증, 적용, 중복 사용 방지)를 빠짐없이 다루고 있다. Fake 패턴(`FakeDB`)을 사용하여 실제 DB 없이 핵심 비즈니스 로직을 검증하는 접근은 올바르다. `pytest.raises`를 사용한 예외 검증도 적절하다.

---

## 발견된 문제

### 1. 공유 가변 상태 -- 간헐적 실패의 핵심 원인

```
[FIRST - Independent] -- 테스트 간 전역 변수 `_db_store`를 공유하여 테스트 격리가 깨진다
```

`_db_store`가 모듈 수준 전역 딕셔너리이며, `FakeDB`의 모든 인스턴스가 이 동일한 딕셔너리를 읽고 쓴다. `setup_module()`이 모듈 시작 시 한 번만 초기화하므로, 개별 테스트가 남긴 데이터가 이후 테스트에 누적된다.

**가끔 실패하는 직접적인 메커니즘:**

- `pytest-randomly` 등으로 실행 순서가 바뀌면, 이전 테스트가 남긴 쿠폰 데이터가 다음 테스트의 `FakeDB`에 존재하게 된다.
- 예: `test_apply_coupon`이 `test_multiple_coupons`보다 먼저 실행되면, `_db_store`에 `'APPLY20'` 쿠폰이 `used=True` 상태로 남는다. 같은 코드를 쓰는 다른 테스트가 뒤에 온다면 예기치 않은 상태를 만난다.
- 특히 `test_expired_coupon_is_invalid`에서 `'EXPIRED'` 코드가 `_db_store`에 남고, 다른 테스트에서 우연히 같은 코드를 사용하면 충돌한다.

이것이 "가끔 실패"하는 가장 큰 원인이다. 실행 순서에 따라 통과하기도 하고 실패하기도 한다 (Generous Leftovers 안티패턴).

---

### 2. 시간 의존 테스트 -- 두 번째 간헐적 실패 원인

```
[FIRST - Repeatable] -- `time.sleep()`과 `timedelta(days=0)`에 의존한 만료 테스트는 타이밍에 따라 실패한다
```

`test_expired_coupon_is_invalid`는 `valid_days=0`으로 쿠폰을 생성한 뒤 `time.sleep(0.01)`로 만료를 기대한다. 그러나 `timedelta(days=0)`은 만료 시각이 생성 시각과 **정확히 동일**하게 설정됨을 의미한다. `is_valid()`의 조건은 `self.clock.now() < coupon['expires_at']`이므로:

- `create_coupon` 호출 시점의 `now()`와 `is_valid` 호출 시점의 `now()`가 같은 초(second) 안에 있으면 `now() < expires_at`이 `False`가 되어 통과하지만, 극히 드물게 `datetime.now()` 해상도 안에서 동일한 값이 반환되면 경계 조건에 걸린다.
- CI 서버 부하에 따라 `sleep(0.01)` 후에도 OS 스케줄링 지연으로 시간이 충분히 흐르지 않을 수 있다.
- 근본적으로 `sleep()`에 의존하는 테스트는 비결정적이다.

올바른 접근은 `CouponService`에 이미 주입 가능한 `clock` 파라미터를 활용하여 시간을 제어하거나, `time-machine`/`freezegun` 같은 시간 모킹 라이브러리를 사용하는 것이다.

---

### 3. 테스트에서 난수 사용

```
[FIRST - Repeatable] -- `random.uniform()`을 사용한 테스트는 실행할 때마다 다른 입력으로 동작한다
```

`test_random_discount`에서 `random.uniform(0.05, 0.5)`로 할인율을 생성한다. 이 테스트는 현재 `assert result == 10000 * (1 - discount)`로 동일한 변수를 사용하므로 항상 통과하지만, 근본적으로 두 가지 문제가 있다:

- 실패 시 재현이 불가능하다 -- 어떤 입력값으로 실패했는지 알 수 없다.
- 부동소수점 연산에서 특정 값 조합이 정밀도 오차를 유발할 수 있다 (예: `10000 * (1 - 0.1)` vs `10000 * 0.9`가 부동소수점에서 다를 수 있음).

난수 기반 테스트가 필요하다면 Hypothesis의 property-based testing을 사용하고, 그렇지 않으면 고정된 parametrize 데이터를 사용해야 한다.

---

### 4. `clock` 의존성 주입을 활용하지 않음

```
[Test Doubles - Fake] -- CouponService가 이미 clock 주입을 지원하지만 테스트에서 활용하지 않는다
```

`CouponService.__init__`에 `clock=datetime` 매개변수가 있어 시간을 제어할 수 있는 설계가 이미 되어 있다. 그러나 모든 테스트가 기본값(`datetime`)을 그대로 사용하여 실제 시스템 시간에 의존한다. `test_create_coupon`의 `assert coupon['expires_at'] > datetime.now()`도 실행 시점에 따라 달라질 수 있는 검증이다.

---

### 5. `unittest.mock.Mock` import 미사용

```
[Test Quality] -- 사용하지 않는 import가 존재하여 코드 의도를 혼란스럽게 한다
```

`from unittest.mock import Mock`이 import되어 있지만 어디에서도 사용되지 않는다. FakeDB를 사용하는 현재 접근이 더 적절하므로, 불필요한 import는 제거해야 한다.

---

### 6. Missing spec on FakeDB

```
[Mock Patterns - spec] -- FakeDB가 실제 DB 인터페이스와의 계약을 보장하지 않는다
```

`FakeDB`는 `save`와 `find_by_code` 두 메서드를 직접 구현했지만, 실제 DB 클래스(혹은 Protocol/ABC)에 대한 spec이 없다. 실제 DB 인터페이스에 메서드가 추가/변경되어도 `FakeDB`가 이를 감지하지 못한다. Protocol이나 ABC를 정의하고 FakeDB가 이를 구현하도록 해야 API 드리프트를 방지할 수 있다.

---

### 7. `test_create_coupon`에서 부동소수점 비교 누락

```
[pytest Fixtures - Assertion] -- 부동소수점 할인율 비교 시 `pytest.approx` 미사용
```

현재는 `0.2`처럼 정확한 값이라 문제가 없지만, 할인 계산이 복잡해지면 부동소수점 비교에서 문제가 생길 수 있다. `test_apply_coupon`의 `assert result == 8000`도 마찬가지다.

---

## 리뷰 체크리스트 검증

| 항목 | 결과 |
|------|------|
| 여러 Act 섹션이 있는 테스트 분리 필요 | `test_multiple_coupons`에 여러 Act-Assert 쌍이 있으나, 하나의 시나리오(복수 쿠폰 중 하나만 사용)를 검증하는 것이므로 허용 범위 |
| 테스트 간 공유 가변 상태 | **문제 발견** -- 전역 `_db_store` (항목 1) |
| Mock 남용 | 해당 없음 -- FakeDB 사용은 적절 |
| Mock에 spec/autospec 누락 | **문제 발견** -- FakeDB에 인터페이스 계약 없음 (항목 6) |
| 시간/순서/외부 서비스 의존 flaky 테스트 | **문제 발견** -- `time.sleep` 의존, `random` 사용 (항목 2, 3) |
| parametrize 누락 | 해당 가능 -- 할인율별 테스트를 parametrize로 통합 가능하나 현 수준에서는 경미 |
| 의도를 가리는 과도한 setup | 해당 없음 |
| 구현 세부사항 검증 | 해당 없음 |
| 의미 없는 assertion | 해당 없음 |
| 잘못된 테스트 레벨 | 해당 없음 |

---

## 요약: 간헐적 실패 원인

1. **전역 `_db_store` 공유** (가장 큰 원인) -- 테스트 실행 순서가 바뀌면 이전 테스트의 데이터가 남아 예기치 않은 결과를 유발한다.
2. **`time.sleep(0.01)`에 의존하는 만료 테스트** -- 시스템 부하에 따라 타이밍이 달라져 경계 조건에서 실패한다.
3. **`random.uniform()` 사용** -- 부동소수점 정밀도 문제가 특정 값에서 발생할 가능성이 있다.

해결의 핵심은 각 테스트가 자체적인 FakeDB 인스턴스(독립된 저장소)를 사용하고, 시간 제어에는 `clock` 의존성 주입 또는 `time-machine`을 활용하는 것이다.
