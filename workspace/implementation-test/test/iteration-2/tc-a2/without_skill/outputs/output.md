# Test Code Review: UserService

## 1. 중복 Mock 생성 (가장 심각한 문제)

모든 테스트 함수에서 동일한 5개 Mock 객체 생성과 `UserService` 인스턴스화가 반복된다.

```python
db = Mock()
cache = Mock()
email = Mock()
logger = Mock()
metrics = Mock()
service = UserService(db, cache, email, logger, metrics)
```

이 코드가 5개 테스트 함수 전부에 복붙되어 있다. pytest fixture 또는 클래스 기반 setUp으로 제거해야 한다.

**개선안:**

```python
import pytest

@pytest.fixture
def deps():
    db = Mock()
    cache = Mock()
    email_sender = Mock()
    logger = Mock()
    metrics = Mock()
    service = UserService(db, cache, email_sender, logger, metrics)
    return service, db, cache, email_sender, logger, metrics

def test_register_user(deps):
    service, db, cache, email_sender, logger, metrics = deps
    # ...
```

---

## 2. assert_called_once()만 사용하는 느슨한 검증

`test_register_user`에서 모든 mock 호출을 `assert_called_once()`로만 검증한다.

```python
db.create_user.assert_called_once()
cache.set.assert_called_once()
email.send_welcome.assert_called_once()
logger.info.assert_called_once()
metrics.increment.assert_called_once()
```

"호출되었다"만 확인하고 "올바른 인자로 호출되었는지"는 확인하지 않는다. 예를 들어 `cache.set`이 엉뚱한 key로 호출되어도, `email.send_welcome`이 다른 사람의 이메일로 호출되어도 이 테스트는 통과한다.

**개선안:**

```python
db.create_user.assert_called_once_with('Alice', 'alice@test.com')
cache.set.assert_called_once_with('user:1', {'id': 1, 'name': 'Alice', 'email': 'alice@test.com'})
email.send_welcome.assert_called_once_with('alice@test.com', 'Alice')
metrics.increment.assert_called_once_with('user.registered')
```

---

## 3. 예외 검증에 try/except 사용

`test_register_duplicate_email`에서 예외를 try/except로 잡는 패턴은 pytest에서 안티패턴이다.

```python
try:
    service.register('Alice', 'alice@test.com')
    assert False, 'Should raise'
except ValueError as e:
    assert '이미 등록된' in str(e)
```

문제점:
- 예외가 발생하지 않으면 `assert False` 라인의 에러 메시지가 불명확하다.
- `ValueError`가 아닌 다른 예외가 발생하면 테스트가 실패하는 대신 unhandled exception으로 끝난다.

**개선안:**

```python
def test_register_duplicate_email(deps):
    service, db, *_ = deps
    db.find_by_email.return_value = {'id': 1, 'name': 'Alice'}

    with pytest.raises(ValueError, match='이미 등록된'):
        service.register('Alice', 'alice@test.com')
```

---

## 4. 캐시 히트 시 DB 미호출 검증 누락

`test_get_user_from_cache`에서 캐시에서 데이터를 가져왔을 때 DB가 호출되지 않았음을 검증하지 않는다. 이것이 캐시의 존재 이유인데, 핵심 행위가 검증되지 않는 셈이다.

**개선안:**

```python
def test_get_user_from_cache(deps):
    service, db, cache, *_ = deps
    cache.get.return_value = {'id': 1, 'name': 'Alice'}

    result = service.get_user(1)

    assert result == {'id': 1, 'name': 'Alice'}
    cache.get.assert_called_once_with('user:1')
    db.find_by_id.assert_not_called()  # 핵심: 캐시 히트 시 DB 접근 없음
```

---

## 5. DB 조회 후 캐시 저장 검증 누락

`test_get_user_from_db`에서 DB에서 조회한 뒤 캐시에 저장하는 로직(`cache.set`)을 검증하지 않는다.

**개선안:**

```python
def test_get_user_from_db(deps):
    service, db, cache, *_ = deps
    cache.get.return_value = None
    db.find_by_id.return_value = {'id': 1, 'name': 'Alice'}

    result = service.get_user(1)

    assert result == {'id': 1, 'name': 'Alice'}
    db.find_by_id.assert_called_once_with(1)
    cache.set.assert_called_once_with('user:1', {'id': 1, 'name': 'Alice'})  # 캐시 갱신 검증
```

---

## 6. 존재하지 않는 사용자 조회 시 캐시 미저장 검증 누락

`test_get_nonexistent_user`에서 사용자가 없을 때 `cache.set`이 호출되지 않았음을 검증하지 않는다. 만약 구현 코드가 `None`을 캐시에 저장하는 버그가 있어도 이 테스트는 통과한다.

**개선안:**

```python
def test_get_nonexistent_user(deps):
    service, db, cache, *_ = deps
    cache.get.return_value = None
    db.find_by_id.return_value = None

    result = service.get_user(999)

    assert result is None
    cache.set.assert_not_called()  # None을 캐시에 저장하지 않음
```

---

## 7. 변수명 혼동

Mock 변수명 `email`이 `email_sender` 의존성과 이메일 주소 문자열 `'alice@test.com'` 양쪽 의미로 읽힐 수 있다. `UserService.__init__`의 파라미터명은 `email_sender`이므로 Mock 변수명도 `email_sender`로 맞추는 것이 읽기 좋다.

---

## 8. 누락된 테스트 케이스

- **`register` 시 `db.create_user`가 예외를 던지면?** -- 이메일 발송이나 캐시 저장이 실행되지 않아야 한다.
- **`register` 시 `email_sender.send_welcome`이 실패하면?** -- 사용자는 이미 DB에 생성되었는데 이메일 발송 실패가 전파되는 구조인지 검증이 필요하다. 현재 구현에는 트랜잭션 처리가 없어서 이 시나리오 자체가 설계 결함 가능성이 있다.
- **`cache.get`/`cache.set` 호출 시 전달되는 key 형식 검증** -- `f'user:{user_id}'` 포맷이 올바른지 확인하는 테스트가 없다.

---

## 요약

| 항목 | 심각도 | 내용 |
|------|--------|------|
| Mock 중복 생성 | 중 | fixture로 추출 필요 |
| `assert_called_once()` 인자 미검증 | 상 | `assert_called_once_with()`로 교체 |
| try/except 예외 검증 | 중 | `pytest.raises` 사용 |
| 캐시 히트 시 DB 미호출 미검증 | 상 | `assert_not_called()` 추가 |
| DB 조회 후 캐시 저장 미검증 | 상 | `cache.set` 호출 검증 추가 |
| 미존재 사용자 캐시 미저장 미검증 | 중 | `cache.set.assert_not_called()` 추가 |
| 변수명 혼동 | 하 | `email` -> `email_sender` |
| 실패 시나리오 미검증 | 중 | 의존성 실패 시 동작 테스트 추가 |

테스트가 "호출되었다"는 확인하지만 "올바르게 호출되었다"와 "호출되지 않아야 할 것이 호출되지 않았다"를 검증하지 않는 것이 전반적인 약점이다.
