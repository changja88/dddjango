# Test Code Review: CacheService

## What the tests do right

테스트가 AAA 패턴을 일관되게 따르고 있고, 각 테스트가 하나의 행위를 검증한다. fixture를 통해 공통 설정을 추출한 점, `CacheService`를 실제 객체(dict)로 테스트하는 점(mock 남용 없음), 그리고 만료된 엔트리가 store에서 삭제되는 부수효과까지 검증하는 점이 좋다.

---

## Findings

### 1. Flaky: `datetime.now()` 직접 호출으로 인한 시간 의존성 (CI 실패의 핵심 원인)

[FIRST - Repeatable] -- `datetime.now()`를 fixture와 테스트 코드 양쪽에서 독립적으로 호출하기 때문에 두 호출 사이에 시간이 흐를 수 있다. CI 환경은 로컬보다 CPU 경합이 심해서 이 gap이 커지며, 이것이 "CI에서 가끔 실패하는" 직접적 원인이다.

**영향받는 위치 3곳:**

**(a) `cache_store` fixture**

```python
@pytest.fixture
def cache_store():
    return {
        'existing': {
            'value': 'hello',
            'expires_at': datetime.now() + timedelta(hours=1),  # 시점 A
            'created_at': datetime.now(),  # 시점 B (A와 다를 수 있음)
        }
    }
```

fixture 내에서 `datetime.now()`를 두 번 호출하므로 `created_at`이 `expires_at` 계산 시점과 미세하게 다르다. 더 중요한 것은, 이 시점이 프로덕션 코드(`CacheService.get`)가 호출하는 `datetime.now()`와도 다르다는 점이다.

**(b) `TestCacheSet`의 만료 시간 검증**

```python
def test_sets_value_with_default_ttl(self, cache, cache_store):
    cache.set('new_key', 'new_value')  # datetime.now() 호출 (시점 1)
    # ...
    expected_expiry = datetime.now() + timedelta(seconds=60)  # datetime.now() 호출 (시점 2)
    assert abs((cache_store['new_key']['expires_at'] - expected_expiry).total_seconds()) < 1
```

`cache.set()` 내부의 `datetime.now()`와 assertion의 `datetime.now()` 사이에 시간차가 발생한다. CI에서 GC pause나 CPU throttling이 발생하면 1초 tolerance를 초과할 수 있다. `test_sets_value_with_custom_ttl`도 동일한 문제를 가진다.

**(c) `CacheService.set` 메서드 자체**

```python
def set(self, key: str, value: str, ttl: int | None = None) -> None:
    actual_ttl = ttl if ttl is not None else self.default_ttl
    self.store[key] = {
        'value': value,
        'expires_at': datetime.now() + timedelta(seconds=actual_ttl),  # 호출 1
        'created_at': datetime.now(),  # 호출 2 -- 미세하게 다른 시점
    }
```

이것은 프로덕션 코드의 문제이지만 테스트의 flakiness에 기여한다. `expires_at`과 `created_at`이 서로 다른 시점의 `datetime.now()`를 사용한다.

**해결: time-machine으로 시간 고정**

```python
import time_machine
from datetime import datetime, timedelta

@pytest.fixture
def frozen_now():
    with time_machine.travel("2024-06-15 12:00:00", tick=False) as traveller:
        yield traveller

@pytest.fixture
def cache_store(frozen_now):
    return {
        'existing': {
            'value': 'hello',
            'expires_at': datetime.now() + timedelta(hours=1),
            'created_at': datetime.now(),
        }
    }

@pytest.fixture
def cache(cache_store):
    return CacheService(cache_store, default_ttl=60)
```

time-machine은 C 확장 기반으로 freezegun보다 100-200배 빠르며, `tick=False`로 시간을 완전히 고정하면 모든 `datetime.now()` 호출이 동일한 값을 반환한다. 이렇게 하면 fixture, 프로덕션 코드, assertion 사이의 시간차가 완전히 제거된다.

---

### 2. Flaky: `test_handles_concurrent_env_config`의 시간 의존성

[FIRST - Repeatable] -- 이 테스트는 `ttl=1`로 설정한 뒤 즉시 `get`을 호출하는데, CI에서 1초 이상 지연이 발생하면 엔트리가 만료되어 실패한다.

```python
def test_handles_concurrent_env_config(self, cache):
    workers = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    if workers != 'master':
        pytest.skip('단일 프로세스에서만 실행')
    cache.set('temp', 'data', ttl=1)       # 1초 TTL
    assert cache.get('temp') == 'data'      # CI에서 1초 넘으면 실패
```

time-machine으로 시간을 고정하면 이 문제도 해결된다.

---

### 3. 테스트 이름과 의도의 불일치: `test_handles_concurrent_env_config`

[AAA - Single Behavior] -- 테스트 이름은 "concurrent env config"를 다루는 것처럼 보이지만, 실제로는 set/get 왕복을 검증한다. `PYTEST_XDIST_WORKER` 환경변수 확인과 `pytest.skip`은 이 테스트가 xdist 환경에서의 동시성 문제를 다루려는 것 같지만, 실제 검증은 단순한 set-then-get이다.

```python
def test_handles_concurrent_env_config(self, cache):
    workers = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    if workers != 'master':
        pytest.skip('단일 프로세스에서만 실행')
    cache.set('temp', 'data', ttl=1)
    assert cache.get('temp') == 'data'
```

이 테스트는 두 가지 중 하나로 정리해야 한다:
- 실제로 동시성 시나리오를 테스트하려면 그에 맞는 검증을 추가
- 단순 set/get 왕복이 목적이라면 환경변수 체크를 제거하고 이름을 `test_get_returns_recently_set_value`로 변경

---

### 4. `TestCacheSet`에서 tolerance 기반 비교의 불안정성

[FIRST - Repeatable] -- finding #1과 직접 연결되는 문제다. 시간을 고정하면 tolerance 비교 자체가 불필요해진다.

```python
# 현재: tolerance 기반 (CI에서 불안정)
expected_expiry = datetime.now() + timedelta(seconds=60)
assert abs((cache_store['new_key']['expires_at'] - expected_expiry).total_seconds()) < 1

# time-machine 적용 후: 정확한 비교 가능
assert cache_store['new_key']['expires_at'] == datetime(2024, 6, 15, 12, 1, 0)
```

시간이 고정되면 정확한 값을 비교할 수 있으므로 테스트의 의도가 더 명확해지고, flakiness가 제거된다.

---

### 5. `TestClearExpired`에서 만료 엔트리의 경계값 누락

[Mutation Testing - Boundary] -- `clear_expired`에서 `now > v['expires_at']` 비교를 사용하는데, 정확히 `now == expires_at`인 경계 케이스를 테스트하지 않는다. mutmut이 `>`를 `>=`로 변경하면 현재 테스트로는 감지할 수 없다.

```python
# 현재: 경계값 테스트 없음
cache_store['expired1'] = {
    'value': 'a', 'expires_at': datetime.now() - timedelta(hours=1),  # 확실히 만료
    ...
}

# 보강: 정확히 만료 시점인 경계 케이스 추가
def test_entry_at_exact_expiry_is_not_cleared(self, cache, cache_store, frozen_now):
    """expires_at이 정확히 현재 시간과 같으면 만료되지 않은 것으로 취급"""
    cache_store['boundary'] = {
        'value': 'edge',
        'expires_at': datetime.now(),  # 정확히 현재 시간
        'created_at': datetime.now() - timedelta(minutes=5),
    }
    count = cache.clear_expired()
    assert count == 0
    assert 'boundary' in cache_store
```

같은 경계값 문제가 `CacheService.get`에도 존재한다. `datetime.now() > entry['expires_at']`에서 `>`와 `>=`를 구분하는 테스트가 없다.

---

### 6. `test_sets_value_with_default_ttl`에 다중 Act 경향

[AAA - Multiple Acts] -- 이 테스트는 set 동작 후 값 확인과 만료 시간 확인을 하나의 테스트에서 수행한다. 두 검증이 동일한 Act(`cache.set`)에 대한 관련 assertion이므로 심각한 위반은 아니지만, 값 저장 검증과 TTL 검증을 분리하면 실패 시 원인 파악이 더 쉬워진다.

---

## Review Checklist

| 항목 | 결과 |
|------|------|
| 다중 Act 섹션 분리 필요 | 경미 -- `test_sets_value_with_default_ttl`에서 값/TTL 검증이 같은 Act |
| 공유 가변 상태 | 해당 없음 -- fixture가 function scope로 격리됨 |
| Mock 남용 | 해당 없음 -- 실제 dict 사용, mock 없음 |
| Mock에 spec 누락 | 해당 없음 -- mock 미사용 |
| Flaky: 시간/순서/외부 서비스 의존 | **핵심 문제** -- `datetime.now()` 직접 호출이 CI flakiness의 원인 |
| parametrize 누락 | 해당 없음 -- 반복 패턴 미관찰 |
| 과도한 setup | 해당 없음 -- fixture가 간결 |
| 구현 세부사항 검증 (The Inspector) | 해당 없음 |
| 의미 없는 assertion (The Liar) | 해당 없음 |
| 잘못된 테스트 수준 | 해당 없음 |

---

## Summary

CI flakiness의 근본 원인은 `datetime.now()`를 테스트 코드와 프로덕션 코드에서 독립적으로 호출하여 발생하는 시간차다. **time-machine을 사용하여 시간을 고정하는 것이 가장 효과적인 해결책**이다. 이렇게 하면:

1. fixture와 프로덕션 코드 사이의 시간차 제거
2. tolerance 기반 근사 비교를 정확한 값 비교로 전환
3. 짧은 TTL(1초) 테스트의 race condition 제거
4. 경계값 테스트 추가 가능

부수적으로, `test_handles_concurrent_env_config`의 이름과 의도를 정리하고, `>`/`>=` 경계값 케이스를 추가하면 테스트 스위트의 품질이 한 단계 올라간다.
