# Test Code Review: UserService

## 잘된 점

- 모든 테스트가 **AAA 패턴**을 따르며, Act 섹션이 단일 호출로 명확하다.
- 각 테스트가 **독립적**이다. 테스트 간 공유 상태가 없고, 각 테스트가 자체적으로 Mock을 생성한다.
- 테스트 이름이 검증 대상 행위를 잘 설명한다 (`test_register_user`, `test_get_user_from_cache`, `test_get_nonexistent_user`).
- 캐시 히트/미스, 정상/중복/미존재 등 주요 시나리오를 빠짐없이 커버한다.

---

## 개선 사항

### 1. Mock 과다 사용 (Mockery)

[Mockery 안티패턴] -- 5개의 의존성을 모두 `Mock()`으로 대체하여, 테스트가 실제 시스템을 검증하는 것이 아니라 Mock 간의 배선만 검증하고 있다. `logger`와 `metrics`는 테스트 대상 행위와 무관한 **Dummy**이지만, `Mock()`으로 생성되어 통신 기반 검증(`assert_called_once`)까지 수행하고 있다. 테스트의 본질적 관심사가 아닌 부수적 호출을 검증하면, 로깅 형식 변경이나 메트릭 이름 변경 같은 무관한 리팩토링에도 테스트가 깨진다.

```python
# 현재: logger, metrics도 Mock으로 만들고 호출까지 검증
logger.info.assert_called_once()
metrics.increment.assert_called_once()
```

외부 부수효과(email)만 Mock으로 검증하고, logger와 metrics 같은 관찰용 의존성은 Dummy(`Mock()` 생성만 하고 assert 없음) 또는 실제 NullLogger로 대체하는 것이 적절하다.

---

### 2. Mock에 spec 미지정

[Mock spec 누락] -- 모든 Mock 객체가 `spec` 없이 생성되어 있다. `spec`이 없는 `Mock()`은 존재하지 않는 메서드를 호출해도 에러를 발생시키지 않으므로, 프로덕션 코드의 인터페이스가 변경되었을 때 테스트가 여전히 통과하는 거짓 안전(false positive)을 초래한다. 예를 들어 `db.find_by_email`이 `db.get_by_email`로 이름이 바뀌어도, spec 없는 Mock은 `find_by_email` 호출을 묵인한다.

```python
# 현재: spec 없는 Mock
db = Mock()

# 권장: spec 또는 create_autospec 사용
from unittest.mock import create_autospec
db = create_autospec(DatabaseInterface)
```

실제 인터페이스 클래스가 없다면 최소한 `spec` 파라미터에 클래스를 지정하고, `seal()`로 봉인하면 미설정 속성 접근까지 차단할 수 있다.

---

### 3. 통신 기반 검증 과다 (The Inspector)

[The Inspector 안티패턴 / 검증 우선순위 위반] -- `test_register_user`에서 반환값 검증(`assert result['name'] == 'Alice'`)은 적절하지만, 이후 5개의 `assert_called_once()` 호출은 구현 세부사항에 결합된 검증이다. `register` 메서드의 내부 호출 순서나 횟수가 바뀌면 행위가 동일해도 테스트가 깨진다. 검증 우선순위(출력 기반 > 상태 기반 > 통신 기반)에 따라, 외부 부수효과(이메일 발송)만 통신 기반으로 검증하고, 나머지는 출력이나 상태로 검증하는 것이 바람직하다.

```python
# 현재: 모든 내부 협력 객체 호출을 일일이 검증
db.create_user.assert_called_once()
cache.set.assert_called_once()
email.send_welcome.assert_called_once()
logger.info.assert_called_once()
metrics.increment.assert_called_once()

# 권장: 행위 결과와 외부 부수효과만 검증
assert result == {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'}
email.send_welcome.assert_called_once_with('alice@test.com', 'Alice')
```

---

### 4. 반복되는 설정 코드 (Excessive Setup)

[Excessive Setup 안티패턴] -- 5개의 Mock 객체 생성과 `UserService` 인스턴스화가 모든 테스트 함수에서 동일하게 반복된다 (5회). 이는 테스트의 핵심 의도를 설정 코드 속에 매몰시키고, 의존성이 추가될 때마다 모든 테스트를 수정해야 하는 유지보수 부담을 만든다. pytest fixture로 추출하면 각 테스트가 검증 대상 행위에만 집중할 수 있다.

```python
# 현재: 매 테스트마다 반복
def test_register_user():
    db = Mock()
    cache = Mock()
    email = Mock()
    logger = Mock()
    metrics = Mock()
    service = UserService(db, cache, email, logger, metrics)
    ...

# 권장: fixture로 추출
@pytest.fixture
def deps():
    return {
        'db': create_autospec(DB),
        'cache': create_autospec(Cache),
        'email': create_autospec(EmailSender),
        'logger': Mock(),
        'metrics': Mock(),
    }

@pytest.fixture
def service(deps):
    return UserService(**deps)

def test_register_user(service, deps):
    deps['db'].find_by_email.return_value = None
    deps['db'].create_user.return_value = {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'}
    result = service.register('Alice', 'alice@test.com')
    assert result == {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'}
```

---

### 5. 예외 테스트에 pytest.raises 미사용

[pytest 관용구 위반] -- `test_register_duplicate_email`에서 `try/except`와 `assert False, 'Should raise'` 패턴을 사용하고 있다. 이는 pytest의 표준 관용구인 `pytest.raises`보다 장황하고, 예외가 발생하지 않았을 때의 실패 메시지도 불명확하다.

```python
# 현재: try/except 패턴
try:
    service.register('Alice', 'alice@test.com')
    assert False, 'Should raise'
except ValueError as e:
    assert '이미 등록된' in str(e)

# 권장: pytest.raises 사용
with pytest.raises(ValueError, match='이미 등록된'):
    service.register('Alice', 'alice@test.com')
```

---

### 6. assert_called_once()에 인자 검증 누락

[약한 단언 / The Liar 경향] -- `assert_called_once()`는 호출 횟수만 검증하고, 올바른 인자로 호출되었는지는 검증하지 않는다. 예를 들어 `cache.set.assert_called_once()`는 cache에 잘못된 키나 잘못된 데이터가 저장되어도 통과한다. 통신 기반 검증을 유지할 경우, `assert_called_once_with()`로 인자까지 검증해야 의미 있는 단언이 된다.

```python
# 현재: 호출 여부만 검증
cache.set.assert_called_once()

# 권장: 인자까지 검증 (통신 기반 검증을 유지할 경우)
cache.set.assert_called_once_with('user:1', {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
```

---

### 7. get_user 테스트에서 캐시 미스 시 DB 조회 후 캐시 저장 미검증

[누락된 행위 검증] -- `test_get_user_from_db`에서 DB로부터 사용자를 조회한 후 캐시에 저장하는 행위(`cache.set` 호출)를 검증하지 않는다. 이는 `get_user`의 핵심 행위(캐시 미스 시 DB 조회 후 캐시에 저장)의 절반만 검증하는 것이다. 반대로, `test_get_user_from_cache`에서 DB가 호출되지 않았음을 검증하지 않아, 캐시 히트 시에도 불필요한 DB 조회가 발생하는 버그를 잡지 못한다.

```python
# test_get_user_from_db에 추가 필요:
cache.set.assert_called_once_with('user:1', {'id': 1, 'name': 'Alice'})

# test_get_user_from_cache에 추가 필요:
db.find_by_id.assert_not_called()
```

---

### 8. parametrize로 통합 가능한 반복 테스트

[parametrize 미활용] -- `test_get_user_from_cache`, `test_get_user_from_db`, `test_get_nonexistent_user`는 유사한 구조(캐시 반환값 설정 -> DB 반환값 설정 -> 결과 검증)를 반복한다. 세 테스트의 시나리오가 각각 고유한 행위를 검증하므로 반드시 parametrize로 합쳐야 하는 것은 아니지만, 설정 코드의 중복은 fixture로 해소할 수 있다.

---

## Review Checklist 결과

| 항목 | 결과 |
|------|------|
| 여러 Act 섹션이 있는 테스트 | 해당 없음 -- 모든 테스트가 단일 Act |
| 테스트 간 공유 변경 상태 | 해당 없음 -- 각 테스트가 독립적 |
| Mock 과다 -- 핵심 로직을 Mock으로 대체 | **해당** -- 5개 의존성 전부 Mock, 항목 1 참조 |
| Mock에 spec/autospec 누락 | **해당** -- 모든 Mock이 spec 없음, 항목 2 참조 |
| 시간/순서/외부 서비스 의존 Flaky 테스트 | 해당 없음 |
| parametrize 미활용 반복 테스트 | **경미** -- fixture로 해소 가능, 항목 8 참조 |
| 의도를 가리는 과도한 설정 | **해당** -- 5회 반복되는 동일 설정, 항목 4 참조 |
| 구현 세부사항 검증 (The Inspector) | **해당** -- 내부 호출 전수 검증, 항목 3 참조 |
| 의미 없는 단언 (The Liar / Secret Catcher) | **경미** -- assert_called_once()의 인자 미검증, 항목 6 참조 |
| 잘못된 테스트 레벨 | 해당 없음 -- 단위 테스트로 적절 |

---

## 요약

테스트의 구조(AAA, 독립성, 시나리오 커버리지)는 양호하다. 가장 큰 개선점은 세 가지다:

1. **Mock 과다 사용을 줄이고**, 외부 부수효과(email)만 통신 기반으로 검증할 것
2. **spec/autospec을 적용하여** 인터페이스 변경 시 거짓 통과를 방지할 것
3. **반복 설정을 pytest fixture로 추출하여** 각 테스트가 검증 대상 행위에 집중하도록 할 것
