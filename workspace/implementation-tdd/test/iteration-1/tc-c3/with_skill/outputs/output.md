# 테스트 냄새 제거 리팩토링

## 식별된 테스트 냄새

| # | 냄새 | 위치 | 유형 |
|---|------|------|------|
| 1 | **Erratic Test** (공유 가변 상태) | `setup_module()` + 전역 `db` | 행위 냄새 |
| 2 | **Eager Test** | `test_user_operations` 하나에 6개 시나리오 | 코드 냄새 |
| 3 | **Assertion Roulette** | `test_user_operations` 내 다수의 단언 | 행위 냄새 |
| 4 | **Conditional Test Logic** | `test_validation` 내 try/except | 코드 냄새 |
| 5 | **Obscure Test** | 테스트 이름이 의도를 드러내지 않음 | 코드 냄새 |
| 6 | **Slow Test / 비기능 테스트 혼재** | `test_performance`가 단위 테스트와 섞임 | 행위 냄새 |
| 7 | AAA 패턴 미준수 | Arrange/Act/Assert 경계가 불분명 | 구조 문제 |
| 8 | 약한 단언 | `assert found is not None` 등 존재만 확인 | 구조 문제 |

---

## 개별 변경 사항

### 1. 공유 가변 상태 제거 -> pytest fixture로 테스트 격리

```
[Before]
db = None

def setup_module():
    global db
    db = {'users': []}

class UserService:
    def register(self, name, email):
        ...
        db['users'].append(user)
        ...
```

```
[After]
class UserService:
    def __init__(self, db):
        self._db = db

    def register(self, name, email):
        ...
        self._db['users'].append(user)
        ...

@pytest.fixture
def db():
    return {'users': []}

@pytest.fixture
def service(db):
    return UserService(db)
```

```
[Reason] 테스트 격리 -- 전역 공유 상태는 Erratic Test의 근본 원인이다.
각 테스트가 독립적인 db를 갖도록 pytest fixture로 분리하면 실행 순서에
의존하지 않는다. UserService가 db를 주입받도록 변경하여 의존성을 명시한다.
```

---

### 2. Eager Test 분해 -> 하나의 행위당 하나의 테스트

```
[Before]
def test_user_operations():
    s = UserService()
    # 등록
    u = s.register('Alice', 'alice@test.com')
    assert u['name'] == 'Alice'
    assert u['email'] == 'alice@test.com'
    assert u['active'] == True
    # 중복 등록 (에러 안 남 - 버그?)
    u2 = s.register('Alice2', 'alice@test.com')
    assert u2 is not None
    # 조회
    found = s.find('alice@test.com')
    assert found is not None
    # 비활성화
    result = s.deactivate('alice@test.com')
    assert result['active'] == False
    # 비활성화 후 조회
    found2 = s.find('alice@test.com')
    assert found2['active'] == False
    # 없는 사용자
    with pytest.raises(ValueError):
        s.deactivate('nobody@test.com')
```

```
[After]
def test_register__valid_input__returns_active_user(service):
    user = service.register('Alice', 'alice@test.com')

    assert user == {'name': 'Alice', 'email': 'alice@test.com', 'active': True}


def test_find__registered_user__returns_user(service):
    service.register('Alice', 'alice@test.com')

    found = service.find('alice@test.com')

    assert found['name'] == 'Alice'
    assert found['email'] == 'alice@test.com'


def test_find__unregistered_email__returns_none(service):
    result = service.find('nobody@test.com')

    assert result is None


def test_deactivate__registered_user__sets_active_false(service):
    service.register('Alice', 'alice@test.com')

    result = service.deactivate('alice@test.com')

    assert result['active'] is False


def test_deactivate__then_find__user_remains_inactive(service):
    service.register('Alice', 'alice@test.com')
    service.deactivate('alice@test.com')

    found = service.find('alice@test.com')

    assert found['active'] is False


def test_deactivate__unregistered_email__raises_value_error(service):
    with pytest.raises(ValueError, match='사용자 없음'):
        service.deactivate('nobody@test.com')
```

```
[Reason] Eager Test / Assertion Roulette -- 하나의 테스트에서 6가지 시나리오를
검증하면 실패 시 어느 행위가 원인인지 알기 어렵다. 각 행위를 독립된 테스트로 분리하여
실패 지점을 즉시 식별할 수 있게 한다.
```

---

### 3. Conditional Test Logic 제거 -> pytest.raises 사용

```
[Before]
def test_validation():
    s = UserService()
    try:
        s.register('', 'test@test.com')
        assert False
    except ValueError:
        pass
    try:
        s.register('Bob', 'invalid-email')
        assert False
    except ValueError:
        pass
```

```
[After]
def test_register__empty_name__raises_value_error(service):
    with pytest.raises(ValueError, match='이름 필수'):
        service.register('', 'test@test.com')


def test_register__invalid_email_format__raises_value_error(service):
    with pytest.raises(ValueError, match='이메일 형식 오류'):
        service.register('Bob', 'invalid-email')
```

```
[Reason] Conditional Test Logic -- 테스트 안에 try/except 분기가 있으면
테스트 자체에 버그가 숨을 수 있다. pytest.raises는 예외가 발생하지 않으면
자동으로 실패하므로 분기 로직이 불필요해진다. match 파라미터로 예외 메시지까지
검증하여 단언을 강화한다.
```

---

### 4. Obscure Test -> 의도를 드러내는 테스트 명명

```
[Before]
def test_user_operations():
def test_validation():
def test_performance():
```

```
[After]
def test_register__valid_input__returns_active_user(service):
def test_find__registered_user__returns_user(service):
def test_find__unregistered_email__returns_none(service):
def test_deactivate__registered_user__sets_active_false(service):
def test_deactivate__then_find__user_remains_inactive(service):
def test_deactivate__unregistered_email__raises_value_error(service):
def test_register__empty_name__raises_value_error(service):
def test_register__invalid_email_format__raises_value_error(service):
```

```
[Reason] Obscure Test / 테스트 명명 규칙 -- [대상]__[조건]__[기대 행위] 형식으로
이름만 읽어도 무엇을 테스트하는지 즉시 파악할 수 있다.
```

---

### 5. 비기능 테스트 제거

```
[Before]
def test_performance():
    s = UserService()
    start = time.time()
    for i in range(100):
        s.register(f'User{i}', f'user{i}@test.com')
    elapsed = time.time() - start
    assert elapsed < 1.0
```

```
[After]
# 삭제 -- 단위 테스트 스위트에서 제거
```

```
[Reason] Slow Test / 테스트 격리 -- 성능 테스트는 단위 테스트와 성격이 다르다.
실행 환경(CPU, 부하)에 따라 결과가 달라지는 Erratic Test가 되며, 인메모리
딕셔너리 100회 append의 시간을 측정하는 것은 의미 있는 성능 검증도 아니다.
성능 테스트가 필요하면 별도의 벤치마크 스위트로 분리한다.
```

---

### 6. 약한 단언 강화

```
[Before]
u2 = s.register('Alice2', 'alice@test.com')
assert u2 is not None

found = s.find('alice@test.com')
assert found is not None
```

```
[After]
def test_find__registered_user__returns_user(service):
    service.register('Alice', 'alice@test.com')

    found = service.find('alice@test.com')

    assert found['name'] == 'Alice'
    assert found['email'] == 'alice@test.com'
```

```
[Reason] 약한 단언 -- `is not None`은 거의 모든 반환값에 통과하므로 회귀 보호가
약하다. 반환된 객체의 필드를 구체적으로 검증하여 실질적인 회귀 보호를 제공한다.
기존 중복 등록 테스트(`u2 is not None`)는 주석에서 "버그?"로 표시된 것처럼
요구사항이 불분명하므로 제거하고, 필요하다면 중복 방지 요구사항이 확정된 후
별도로 추가한다.
```

---

### 7. AAA 패턴 명확화

```
[Before]
def test_user_operations():
    s = UserService()
    u = s.register('Alice', 'alice@test.com')
    assert u['name'] == 'Alice'
    assert u['email'] == 'alice@test.com'
    assert u['active'] == True
    u2 = s.register('Alice2', 'alice@test.com')
    assert u2 is not None
    found = s.find('alice@test.com')
    ...
```

```
[After]
def test_register__valid_input__returns_active_user(service):
    # Arrange: fixture가 service를 제공

    user = service.register('Alice', 'alice@test.com')  # Act

    assert user == {'name': 'Alice', 'email': 'alice@test.com', 'active': True}  # Assert
```

```
[Reason] AAA 패턴 -- 모든 테스트가 Arrange/Act/Assert 세 구간으로 명확히
나뉘어야 읽는 사람이 테스트의 구조를 즉시 파악할 수 있다. 빈 줄로 구간을
구분하여 가독성을 높인다.
```

---

## 리팩토링 체크리스트 적용 결과

- [x] Missing test isolation -> EXTRACT fixtures, eliminate shared state
- [x] Test smells -> APPLY corresponding remedy (Eager Test, Assertion Roulette, Conditional Test Logic, Obscure Test, Erratic Test)
- [x] Obscure tests -> RENAME and restructure for clarity (AAA pattern)
- [x] Weak assertions -> STRENGTHEN to catch regressions
- [x] Communication-based tests -> CONVERT to output-based where possible (해당 없음, 이미 상태 기반)
- [x] Implementation-coupled tests -> REWRITE to verify behavior, not implementation (해당 없음)
- [x] Mock overuse -> REPLACE with real objects (해당 없음, Mock 미사용)
- [x] Missing edge cases -> ADD boundary tests from test list (빈 이름, 잘못된 이메일, 미등록 사용자 조회/비활성화 포함)

---

## 완성된 리팩토링 코드

```python
import pytest


class UserService:
    def __init__(self, db):
        self._db = db

    def register(self, name, email):
        if not name:
            raise ValueError('이름 필수')
        if '@' not in email:
            raise ValueError('이메일 형식 오류')
        user = {'name': name, 'email': email, 'active': True}
        self._db['users'].append(user)
        return user

    def deactivate(self, email):
        for u in self._db['users']:
            if u['email'] == email:
                u['active'] = False
                return u
        raise ValueError('사용자 없음')

    def find(self, email):
        for u in self._db['users']:
            if u['email'] == email:
                return u
        return None


@pytest.fixture
def db():
    return {'users': []}


@pytest.fixture
def service(db):
    return UserService(db)


class TestRegister:
    def test_register__valid_input__returns_active_user(self, service):
        user = service.register('Alice', 'alice@test.com')

        assert user == {'name': 'Alice', 'email': 'alice@test.com', 'active': True}

    def test_register__empty_name__raises_value_error(self, service):
        with pytest.raises(ValueError, match='이름 필수'):
            service.register('', 'test@test.com')

    def test_register__invalid_email_format__raises_value_error(self, service):
        with pytest.raises(ValueError, match='이메일 형식 오류'):
            service.register('Bob', 'invalid-email')


class TestFind:
    def test_find__registered_user__returns_user(self, service):
        service.register('Alice', 'alice@test.com')

        found = service.find('alice@test.com')

        assert found['name'] == 'Alice'
        assert found['email'] == 'alice@test.com'

    def test_find__unregistered_email__returns_none(self, service):
        result = service.find('nobody@test.com')

        assert result is None


class TestDeactivate:
    def test_deactivate__registered_user__sets_active_false(self, service):
        service.register('Alice', 'alice@test.com')

        result = service.deactivate('alice@test.com')

        assert result['active'] is False

    def test_deactivate__then_find__user_remains_inactive(self, service):
        service.register('Alice', 'alice@test.com')
        service.deactivate('alice@test.com')

        found = service.find('alice@test.com')

        assert found['active'] is False

    def test_deactivate__unregistered_email__raises_value_error(self, service):
        with pytest.raises(ValueError, match='사용자 없음'):
            service.deactivate('nobody@test.com')
```
