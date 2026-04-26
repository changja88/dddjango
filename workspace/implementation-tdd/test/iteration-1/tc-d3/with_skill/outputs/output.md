# TDD 리뷰 & 리팩토링: RegistrationService 테스트

---

## Part 1: Review

### 잘 된 점

- 외부 의존성(UserRepository, EmailSender)을 Mock으로 격리하여 London 학파 접근법을 적절히 사용하고 있다. `RegistrationService`는 DB와 이메일이라는 외부 시스템에 의존하므로 Mock이 정당한 경우다.
- 예외 경로(중복 이메일, 짧은 비밀번호)에 대한 테스트가 존재한다.
- `pytest.raises`의 `match` 파라미터를 사용하여 올바른 예외가 발생하는지 구체적으로 검증한다.

### 개선 필요 사항

[Test Code Duplication] -- 세 테스트 모두 `Mock()` 생성과 `RegistrationService` 인스턴스화를 동일하게 반복한다. 테스팅 패턴의 테스트 격리 원칙에 따르면, pytest fixture를 사용하여 테스트별 독립적인 상태를 생성하되 중복은 제거해야 한다.

[Obscure Test / 테스트 명명] -- `test_register`, `test_duplicate_email`, `test_short_password`는 테스트 대상 단위, 조건, 기대 행위가 드러나지 않는다. 테스팅 패턴의 명명 규칙 `[테스트 대상 단위]_[상태/조건]_[기대 행위]`를 따라야 한다.

[Communication-based testing where output-based would suffice] -- `test_register`에서 `repo.save.assert_called_once()`와 `sender.send.assert_called_once()`는 통신 기반 검증이다. `save`의 호출 여부는 반환값(`result`)을 통한 출력 기반 검증으로 이미 간접 확인되므로, 통신 기반 검증은 외부 시스템 부수효과(이메일 발송)에만 한정하는 것이 바람직하다. Khorikov의 권고: 출력 기반 > 상태 기반 > 통신 기반.

[Weak assertions / Assertion Roulette] -- `test_register`에서 `assert result['name'] == 'Alice'`만 검증한다. 반환된 사용자의 핵심 필드(email, active 상태)를 검증하지 않아 회귀 방지력이 약하다. 또한 `repo.save`에 전달된 인자의 내용을 검증하지 않아, 잘못된 데이터가 저장되는 버그를 잡지 못한다.

[Missing boundary/edge case tests] -- 테스트 목록이 불완전하다. 경계값 테스트가 빠져 있다:
- 비밀번호 정확히 8자(경계값)
- 빈 이름, 빈 이메일 등 입력 검증
- 이메일 발송 실패 시 동작

[Mock overuse -- spec 미지정] -- `Mock()`을 `spec` 없이 생성하면 존재하지 않는 메서드를 호출해도 에러가 발생하지 않는다. `Mock(spec=UserRepository)`로 생성해야 오타나 인터페이스 변경을 감지할 수 있다.

[Tests coupled to implementation details] -- `repo.find_by_email.assert_called_once_with('a@t.com')`는 내부 구현(중복 확인 메서드의 정확한 호출)에 결합되어 있다. 리팩토링으로 중복 확인 방식이 바뀌면(예: `repo.exists_by_email`) 테스트가 깨진다. 이는 리팩토링 내성을 낮추는 원인이다.

### Review Checklist 검증

- [x] Tests written after production code -- 프로덕션 코드와 테스트가 같은 파일에 있어 test-first 증거 없음
- [x] No Red-Green-Refactor cycle evidence -- 완성된 구현과 테스트가 한꺼번에 제시됨
- [x] Tests coupled to implementation details -- `find_by_email.assert_called_once_with` 확인
- [ ] Mock overuse for internal collaborators -- 해당 없음 (Repository, EmailSender는 외부 의존성)
- [ ] Missing test isolation -- 공유 상태 없음 (각 테스트가 독립적)
- [x] Test smells -- Obscure Test(명명), Test Code Duplication(Mock 반복), 약한 단언
- [x] No incremental development -- 한 번에 전체 구현 제시
- [x] Communication-based testing where output-based would suffice -- save 호출 검증
- [x] Missing boundary/edge case tests -- 경계값 8자, 빈 입력 등 미검증
- [x] Tests that don't drive design -- 테스트가 설계를 이끌지 않고 사후 검증

---

## Part 2: Refactoring

### Change 1: Test Code Duplication 제거 -- fixture 추출

[Before]
```python
def test_register():
    repo = Mock()
    sender = Mock()
    repo.find_by_email.return_value = None
    repo.save.return_value = {'id': 1, 'name': 'Alice', 'email': 'a@t.com', 'password': 'pass1234', 'active': True}

    svc = RegistrationService(repo, sender)
    # ...


def test_duplicate_email():
    repo = Mock()
    sender = Mock()
    repo.find_by_email.return_value = {'id': 1}

    svc = RegistrationService(repo, sender)
    # ...


def test_short_password():
    repo = Mock()
    sender = Mock()
    repo.find_by_email.return_value = None

    svc = RegistrationService(repo, sender)
    # ...
```

[After]
```python
@pytest.fixture
def repo():
    return Mock(spec=UserRepository)


@pytest.fixture
def sender():
    return Mock(spec=EmailSender)


@pytest.fixture
def svc(repo, sender):
    return RegistrationService(repo, sender)
```

[Reason] Test Code Duplication / 테스트 격리 패턴 -- 세 테스트에서 반복되는 Mock 생성과 서비스 인스턴스화를 fixture로 추출한다. `spec`을 지정하여 인터페이스 불일치를 감지할 수 있게 한다. 각 fixture는 function 스코프이므로 테스트 간 독립성이 유지된다.

---

### Change 2: Obscure Test -- 의도를 드러내는 테스트 명명

[Before]
```python
def test_register():
def test_duplicate_email():
def test_short_password():
```

[After]
```python
def test_register__valid_input__saves_user_and_sends_welcome_email():
def test_register__duplicate_email__raises_already_registered():
def test_register__password_shorter_than_8__raises_validation_error():
def test_register__password_exactly_8_chars__succeeds():
```

[Reason] Obscure Test / 테스팅 패턴 명명 규칙 -- `[대상]__[조건]__[기대 행위]` 형식으로 변경하여, 테스트 이름만으로도 무엇을 검증하는지 즉시 파악할 수 있게 한다.

---

### Change 3: Communication-based 검증을 Output/State-based로 전환 + 약한 단언 강화

[Before]
```python
result = svc.register('Alice', 'a@t.com', 'pass1234')

assert result['name'] == 'Alice'
repo.find_by_email.assert_called_once_with('a@t.com')
repo.save.assert_called_once()
sender.send.assert_called_once()
```

[After]
```python
repo.find_by_email.return_value = None
repo.save.return_value = {
    'id': 1, 'name': 'Alice', 'email': 'alice@test.com',
    'password': 'secure99', 'active': True,
}

result = svc.register('Alice', 'alice@test.com', 'secure99')

assert result == {
    'id': 1, 'name': 'Alice', 'email': 'alice@test.com',
    'password': 'secure99', 'active': True,
}
saved_user = repo.save.call_args[0][0]
assert saved_user == {
    'name': 'Alice', 'email': 'alice@test.com',
    'password': 'secure99', 'active': True,
}
sender.send.assert_called_once_with(
    'alice@test.com', '가입 환영', 'Alice님 환영합니다',
)
```

[Reason] Four Pillars (회귀 방지 + 리팩토링 내성) / 테스트 스타일 우선순위 -- (1) `result` 반환값 전체를 출력 기반으로 검증하여 회귀 방지력을 높인다. (2) `repo.save`에 전달된 인자의 내용을 구체적으로 검증하여 잘못된 데이터 저장 버그를 잡는다. (3) `find_by_email.assert_called_once_with`를 제거하여 내부 구현 결합을 줄이고 리팩토링 내성을 높인다. (4) 이메일 발송은 외부 부수효과이므로 통신 기반 검증이 정당하며, 인자까지 구체적으로 검증한다.

---

### Change 4: Missing edge cases -- 경계값 테스트 추가

[Before]
```python
# 비밀번호 경계값 테스트 없음
```

[After]
```python
def test_register__password_exactly_8_chars__succeeds(svc, repo):
    repo.find_by_email.return_value = None
    repo.save.return_value = {
        'id': 2, 'name': 'Dana', 'email': 'dana@test.com',
        'password': '12345678', 'active': True,
    }

    result = svc.register('Dana', 'dana@test.com', '12345678')

    assert result['id'] == 2


def test_register__password_7_chars__raises_validation_error(svc, repo):
    repo.find_by_email.return_value = None

    with pytest.raises(ValueError, match='8자 이상'):
        svc.register('Eve', 'eve@test.com', '1234567')
```

[Reason] Red Bar 패턴 (경계값 테스트) / 회귀 방지 -- 비밀번호 길이의 경계값(7자, 8자)을 명시적으로 테스트한다. 기존 `test_short_password`는 4자로 테스트하여 경계에서의 off-by-one 버그를 잡지 못한다.

---

### Change 5: 이메일 발송 실패 시 예외 전파 미검증 부수효과 테스트

[Before]
```python
# 이메일 발송 실패 시나리오 없음
```

[After]
```python
def test_register__email_send_fails__propagates_exception(svc, repo, sender):
    repo.find_by_email.return_value = None
    repo.save.return_value = {
        'id': 3, 'name': 'Frank', 'email': 'frank@test.com',
        'password': 'secure99', 'active': True,
    }
    sender.send.side_effect = ConnectionError('SMTP 서버 연결 실패')

    with pytest.raises(ConnectionError, match='SMTP'):
        svc.register('Frank', 'frank@test.com', 'secure99')
```

[Reason] Crash Test Dummy 패턴 / 회귀 방지 -- 외부 시스템(이메일)의 장애 상황을 시뮬레이션하여 서비스의 에러 전파 동작을 검증한다. 현재 구현은 예외를 그대로 전파하는데, 이 동작이 의도된 것인지 테스트로 고정해둬야 향후 에러 처리 로직 추가 시 회귀를 감지할 수 있다.

---

### Change 6: 의미 없는 테스트 데이터 개선

[Before]
```python
repo.save.return_value = {'id': 1, 'name': 'Alice', 'email': 'a@t.com', 'password': 'pass1234', 'active': True}
```

[After]
```python
repo.save.return_value = {
    'id': 1, 'name': 'Alice', 'email': 'alice@test.com',
    'password': 'secure99', 'active': True,
}
```

[Reason] 테스팅 패턴 (명백한 데이터) -- `a@t.com`은 축약되어 가독성이 떨어진다. `alice@test.com`으로 변경하여 데이터의 의미를 명확히 한다. `pass1234`도 `secure99`로 변경하여 비밀번호 검증(8자 이상)과의 관계가 드러나게 한다.

---

## Complete Refactored Code

```python
import pytest
from unittest.mock import Mock


class EmailSender:
    def send(self, to, subject, body): ...


class UserRepository:
    def save(self, user): ...
    def find_by_email(self, email): ...


class RegistrationService:
    def __init__(self, repo, sender):
        self.repo = repo
        self.sender = sender

    def register(self, name, email, password):
        if self.repo.find_by_email(email):
            raise ValueError('이미 등록된 이메일')
        if len(password) < 8:
            raise ValueError('비밀번호 8자 이상')
        user = {'name': name, 'email': email, 'password': password, 'active': True}
        saved = self.repo.save(user)
        self.sender.send(email, '가입 환영', f'{name}님 환영합니다')
        return saved


# --- Fixtures ---

@pytest.fixture
def repo():
    return Mock(spec=UserRepository)


@pytest.fixture
def sender():
    return Mock(spec=EmailSender)


@pytest.fixture
def svc(repo, sender):
    return RegistrationService(repo, sender)


# --- Success path ---

def test_register__valid_input__saves_user_and_sends_welcome_email(svc, repo, sender):
    repo.find_by_email.return_value = None
    repo.save.return_value = {
        'id': 1, 'name': 'Alice', 'email': 'alice@test.com',
        'password': 'secure99', 'active': True,
    }

    result = svc.register('Alice', 'alice@test.com', 'secure99')

    assert result == {
        'id': 1, 'name': 'Alice', 'email': 'alice@test.com',
        'password': 'secure99', 'active': True,
    }
    saved_user = repo.save.call_args[0][0]
    assert saved_user == {
        'name': 'Alice', 'email': 'alice@test.com',
        'password': 'secure99', 'active': True,
    }
    sender.send.assert_called_once_with(
        'alice@test.com', '가입 환영', 'Alice님 환영합니다',
    )


def test_register__password_exactly_8_chars__succeeds(svc, repo):
    repo.find_by_email.return_value = None
    repo.save.return_value = {
        'id': 2, 'name': 'Dana', 'email': 'dana@test.com',
        'password': '12345678', 'active': True,
    }

    result = svc.register('Dana', 'dana@test.com', '12345678')

    assert result['id'] == 2


# --- Validation errors ---

def test_register__duplicate_email__raises_already_registered(svc, repo, sender):
    repo.find_by_email.return_value = {'id': 1}

    with pytest.raises(ValueError, match='이미 등록된'):
        svc.register('Bob', 'existing@test.com', 'secure99')

    sender.send.assert_not_called()


def test_register__password_shorter_than_8__raises_validation_error(svc, repo, sender):
    repo.find_by_email.return_value = None

    with pytest.raises(ValueError, match='8자 이상'):
        svc.register('Charlie', 'charlie@test.com', '1234567')

    repo.save.assert_not_called()
    sender.send.assert_not_called()


# --- Edge cases ---

def test_register__email_send_fails__propagates_exception(svc, repo, sender):
    repo.find_by_email.return_value = None
    repo.save.return_value = {
        'id': 3, 'name': 'Frank', 'email': 'frank@test.com',
        'password': 'secure99', 'active': True,
    }
    sender.send.side_effect = ConnectionError('SMTP 서버 연결 실패')

    with pytest.raises(ConnectionError, match='SMTP'):
        svc.register('Frank', 'frank@test.com', 'secure99')
```

### Refactoring Checklist 검증

- [x] Implementation-coupled tests -- `find_by_email.assert_called_once_with` 제거, 행위 결과로 검증 전환
- [x] Missing test isolation -- fixture로 추출하여 중복 제거, 각 테스트 독립성 유지
- [x] Test smells (Obscure Test) -- `[대상]__[조건]__[기대 행위]` 명명 적용
- [x] Test smells (Test Code Duplication) -- fixture로 Mock 생성 공통화
- [x] Missing edge cases -- 경계값(7자, 8자), 이메일 발송 실패 추가
- [x] Communication-based tests -- save 결과를 출력 기반으로 전환, 이메일만 통신 기반 유지
- [x] Weak assertions -- 반환값 전체 검증, save 인자 내용 검증, 실패 시 부수효과 미발생 검증
- [ ] Mock overuse -- 해당 없음 (외부 의존성에 대한 Mock 사용은 정당)
- [ ] Big-bang implementation -- 리팩토링 모드에서는 해당 없음
