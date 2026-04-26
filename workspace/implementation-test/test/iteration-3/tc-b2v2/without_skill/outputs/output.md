# CacheService 테스트 코드 리뷰

## CI 간헐적 실패 원인 분석

CI에서 가끔 실패하고 로컬에서는 항상 통과하는 패턴은 **시간 의존적 테스트(time-dependent test)** 의 전형적인 증상이다. 이 코드에는 여러 시간 관련 결함이 존재한다.

---

## 1. 핵심 문제: `datetime.now()` 반복 호출로 인한 경쟁 조건 (Race Condition)

### 1-1. `CacheService.set()` 내부의 이중 `datetime.now()` 호출

```python
def set(self, key: str, value: str, ttl: int | None = None) -> None:
    actual_ttl = ttl if ttl is not None else self.default_ttl
    self.store[key] = {
        'value': value,
        'expires_at': datetime.now() + timedelta(seconds=actual_ttl),  # 첫 번째 호출
        'created_at': datetime.now(),                                   # 두 번째 호출
    }
```

`datetime.now()`가 두 번 호출된다. 두 호출 사이에 미세한 시간 차이가 발생하므로, `created_at`이 `expires_at` 계산 시점보다 미세하게 나중이 된다. 이 자체가 논리적 불일치이다. CI 환경에서는 컨텍스트 스위칭이나 부하로 인해 이 간격이 더 벌어질 수 있다.

**수정 방안:**
```python
def set(self, key: str, value: str, ttl: int | None = None) -> None:
    actual_ttl = ttl if ttl is not None else self.default_ttl
    now = datetime.now()
    self.store[key] = {
        'value': value,
        'expires_at': now + timedelta(seconds=actual_ttl),
        'created_at': now,
    }
```

### 1-2. fixture와 테스트 코드 사이의 시간 차이 (CI 실패의 직접 원인)

이것이 **CI 간헐적 실패의 가장 유력한 원인**이다.

```python
@pytest.fixture
def cache_store():
    return {
        'existing': {
            'value': 'hello',
            'expires_at': datetime.now() + timedelta(hours=1),  # fixture 생성 시점
            'created_at': datetime.now(),
        }
    }
```

```python
def test_sets_value_with_default_ttl(self, cache, cache_store):
    cache.set('new_key', 'new_value')
    assert cache_store['new_key']['value'] == 'new_value'
    expected_expiry = datetime.now() + timedelta(seconds=60)  # 검증 시점
    assert abs((cache_store['new_key']['expires_at'] - expected_expiry).total_seconds()) < 1
```

`cache.set()` 내부의 `datetime.now()`와 바로 다음 줄의 `datetime.now()`는 서로 다른 시점이다. 로컬에서는 이 차이가 밀리초 수준이라 `< 1`초 조건을 쉽게 통과하지만, CI 환경에서는 다음과 같은 이유로 차이가 1초를 넘길 수 있다:

- CI 서버의 CPU 부하 (다른 빌드와 리소스 공유)
- 컨테이너 환경에서의 CPU 스로틀링
- GC(가비지 컬렉션) 일시 정지

`test_sets_value_with_custom_ttl`도 동일한 문제를 가진다.

**수정 방안: `freezegun` 또는 수동 시간 주입을 사용하여 시간을 고정한다.**

```python
from unittest.mock import patch
from freezegun import freeze_time

class TestCacheSet:
    @freeze_time("2026-04-04 12:00:00")
    def test_sets_value_with_default_ttl(self, cache, cache_store):
        cache.set('new_key', 'new_value')
        assert cache_store['new_key']['value'] == 'new_value'
        expected_expiry = datetime(2026, 4, 4, 12, 1, 0)  # 정확히 60초 후
        assert cache_store['new_key']['expires_at'] == expected_expiry
```

또는 프로덕션 코드에 시간 소스를 주입할 수 있게 리팩토링한다:

```python
class CacheService:
    def __init__(self, store: dict, default_ttl: int = 300, clock=None):
        self.store = store
        self.default_ttl = default_ttl
        self._clock = clock or datetime.now

    def _now(self):
        return self._clock()
```

---

## 2. `test_handles_concurrent_env_config` 테스트의 결함

```python
def test_handles_concurrent_env_config(self, cache):
    workers = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    if workers != 'master':
        pytest.skip('단일 프로세스에서만 실행')
    cache.set('temp', 'data', ttl=1)
    assert cache.get('temp') == 'data'
```

### 문제점들:

**(a) TTL 1초는 CI에서 만료될 수 있다**

`set()`에서 `datetime.now()`로 만료 시간을 설정하고, 바로 다음 줄 `get()`에서 다시 `datetime.now()`로 비교한다. TTL이 1초이므로, CI에서 `set()`과 `get()` 사이에 1초 이상이 걸리면 이미 만료되어 `None`이 반환된다. 이것이 **CI에서 간헐적 실패의 두 번째 원인**이다.

**(b) 테스트 이름과 내용의 불일치**

`test_handles_concurrent_env_config`라는 이름이지만 실제로 동시성을 테스트하지 않는다. 환경 변수를 읽어서 `xdist` 워커인지 확인하는 것은 동시성 테스트가 아니라 단순한 실행 환경 필터링이다. 테스트가 무엇을 검증하려는지 의도가 불명확하다.

**(c) `pytest.skip`보다 `@pytest.mark.skipif` 데코레이터를 사용하는 것이 관례적으로 더 낫다**

```python
@pytest.mark.skipif(
    os.environ.get('PYTEST_XDIST_WORKER', 'master') != 'master',
    reason='단일 프로세스에서만 실행'
)
def test_handles_concurrent_env_config(self, cache):
    ...
```

---

## 3. fixture의 `datetime.now()` 이중 호출

```python
@pytest.fixture
def cache_store():
    return {
        'existing': {
            'value': 'hello',
            'expires_at': datetime.now() + timedelta(hours=1),  # 호출 1
            'created_at': datetime.now(),                        # 호출 2
        }
    }
```

`set()` 메서드와 동일한 문제이다. 두 `datetime.now()` 호출 사이에 시간 차이가 발생한다. fixture에서도 `now`를 한 번만 캡처해야 한다.

---

## 4. `test_returns_none_for_expired_entry`의 경계 조건 취약성

```python
cache_store['expired'] = {
    'value': 'old',
    'expires_at': datetime.now() - timedelta(seconds=1),
    ...
}
assert cache.get('expired') is None
```

`datetime.now() - timedelta(seconds=1)`로 설정하고, `get()` 내부에서 다시 `datetime.now()`를 호출한다. 현재는 1초 전이므로 거의 확실히 만료 판정이 되지만, 만약 누군가 이 값을 `timedelta(milliseconds=1)`처럼 줄이면 CI에서 깨질 수 있다. 충분한 마진(예: `timedelta(hours=1)`)을 사용하거나 시간을 고정하는 것이 안전하다.

---

## 5. 프로덕션 코드(`CacheService`) 자체의 문제

테스트 리뷰를 요청받았지만, 프로덕션 코드의 결함이 테스트 실패에 직접 기여하므로 함께 지적한다.

### 5-1. `get()`의 만료 비교 연산자

```python
if datetime.now() > entry['expires_at']:
```

`>`(초과)를 사용하고 있으므로 정확히 만료 시간과 같은 시점에는 만료되지 않는다. `>=`(이상)이 더 일반적이고 올바르다. 이것이 CI에서 경계 조건 테스트 실패에 기여할 수 있다.

### 5-2. 스레드 안전성 없음

`clear_expired()`에서 딕셔너리를 순회하면서 삭제하는데, 멀티스레드 환경에서는 `RuntimeError: dictionary changed size during iteration`이 발생할 수 있다. 현재 테스트에서는 단일 스레드이므로 문제가 없지만, `test_handles_concurrent_env_config`라는 이름이 동시성을 암시하고 있어 혼란을 준다.

---

## 요약: CI 간헐적 실패의 원인 순위

| 우선순위 | 원인 | 관련 테스트 |
|---------|------|------------|
| 1 | `set()` 후 `datetime.now()`로 검증 시 시간 차이가 1초 임계값 초과 | `test_sets_value_with_default_ttl`, `test_sets_value_with_custom_ttl` |
| 2 | TTL 1초 설정 후 즉시 `get()` 호출 시 만료 | `test_handles_concurrent_env_config` |
| 3 | `datetime.now()` 이중 호출로 인한 미세 불일치 | `CacheService.set()`, `cache_store` fixture |

## 권장 수정 방향

1. `freezegun` 라이브러리를 도입하여 모든 시간 의존 테스트에서 시간을 고정한다.
2. 또는 `CacheService`에 clock 인터페이스를 주입 가능하게 리팩토링하여 테스트에서 고정 시간을 사용한다.
3. `test_handles_concurrent_env_config`의 목적을 재정의하고, TTL을 충분히 크게 설정하거나 시간을 고정한다.
4. `datetime.now()` 이중 호출을 단일 변수 캡처로 수정한다.
5. 만료 비교 연산자를 `>` 에서 `>=`로 변경하는 것을 검토한다.
