# TDD 관점 테스트 코드 리뷰 및 리팩토링

## 1. 리뷰 요약

### 잘된 점
- 외부 의존성(Repository, EmailSender)을 Mock으로 분리하여 단위 테스트 격리를 달성
- `pytest.raises`로 예외 케이스를 명시적으로 검증
- `match` 파라미터로 예외 메시지까지 검증

### 개선이 필요한 점

#### (A) 테스트 이름이 행위(behavior)를 표현하지 않음
`test_register`, `test_duplicate_email`, `test_short_password`는 **무엇을 테스트하는지**만 암시할 뿐, **기대하는 결과**가 이름에 없다. TDD에서 테스트 이름은 살아 있는 명세(specification) 역할을 해야 한다.

#### (B) Mock 생성이 매 테스트마다 중복
`repo = Mock(); sender = Mock()`이 3개 테스트 모두에서 반복된다. fixture로 추출하면 중복이 사라지고, 테스트 본문이 **Arrange-Act-Assert** 중 본질적인 Arrange에만 집중할 수 있다.

#### (C) 검증 대상이 불충분하거나 과잉
- `test_register`에서 `repo.save.assert_called_once()`는 **어떤 인자로** 호출됐는지 검증하지 않는다. 저장되는 user dict의 구조가 올바른지가 핵심인데 이를 놓치고 있다.
- `sender.send.assert_called_once()`도 마찬가지로 인자를 검증하지 않아, 잘못된 이메일이나 본문이 전달돼도 테스트가 통과한다.
- 반면 `result['name'] == 'Alice'`는 Mock의 return_value를 그대로 돌려받는 것이라 실질적 검증 가치가 낮다. save가 반환한 값을 그대로 리턴하는지를 확인하는 것이 의도라면 `result is saved_user`처럼 identity 검증이 더 명확하다.

#### (D) 실패 경로에서 부작용 미발생 검증 누락
- `test_duplicate_email`에서 `repo.save`가 호출되지 않았는지, `sender.send`가 호출되지 않았는지 검증하지 않는다. 예외가 발생했더라도 부작용이 실행됐을 수 있다.
- `test_short_password`도 동일한 문제.

#### (E) 경계값 테스트 부재
- 비밀번호 길이 검증에서 정확히 8자인 경우(경계값)에 대한 테스트가 없다.

#### (F) `assert_called_once` vs `assert_called_once_with`
`assert_called_once()`는 호출 횟수만 검증한다. 인자까지 검증하려면 `assert_called_once_with(...)`를 사용해야 한다. 인자를 생략하면 잘못된 인자로 호출되어도 테스트가 통과하는 위양성(false positive) 위험이 있다.

---

## 2. 리팩토링 결과

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
            raise ValueError("이미 등록된 이메일")
        if len(password) < 8:
            raise ValueError("비밀번호 8자 이상")
        user = {"name": name, "email": email, "password": password, "active": True}
        saved = self.repo.save(user)
        self.sender.send(email, "가입 환영", f"{name}님 환영합니다")
        return saved


# ---------------------------------------------------------------------------
# Fixtures: 테스트 간 공통 설정을 한 곳에서 관리
# ---------------------------------------------------------------------------

@pytest.fixture
def repo():
    mock = Mock(spec=UserRepository)
    mock.find_by_email.return_value = None  # 기본: 중복 없음
    return mock


@pytest.fixture
def sender():
    return Mock(spec=EmailSender)


@pytest.fixture
def svc(repo, sender):
    return RegistrationService(repo, sender)


# ---------------------------------------------------------------------------
# 성공 경로 (Happy Path)
# ---------------------------------------------------------------------------

class TestRegisterSuccess:
    """신규 사용자가 유효한 정보로 가입하면 정상 등록된다."""

    def test_저장소에_올바른_사용자_정보가_전달된다(self, svc, repo):
        repo.save.return_value = {
            "id": 1, "name": "Alice", "email": "a@t.com",
            "password": "pass1234", "active": True,
        }

        svc.register("Alice", "a@t.com", "pass1234")

        repo.save.assert_called_once_with({
            "name": "Alice",
            "email": "a@t.com",
            "password": "pass1234",
            "active": True,
        })

    def test_저장소_반환값을_그대로_리턴한다(self, svc, repo):
        saved_user = {"id": 1, "name": "Alice", "email": "a@t.com",
                       "password": "pass1234", "active": True}
        repo.save.return_value = saved_user

        result = svc.register("Alice", "a@t.com", "pass1234")

        assert result is saved_user

    def test_환영_이메일이_올바른_수신자와_내용으로_발송된다(self, svc, repo, sender):
        repo.save.return_value = {"id": 1}

        svc.register("Alice", "a@t.com", "pass1234")

        sender.send.assert_called_once_with(
            "a@t.com", "가입 환영", "Alice님 환영합니다"
        )

    def test_이메일_중복_여부를_먼저_확인한다(self, svc, repo):
        repo.save.return_value = {"id": 1}

        svc.register("Alice", "a@t.com", "pass1234")

        repo.find_by_email.assert_called_once_with("a@t.com")


# ---------------------------------------------------------------------------
# 실패 경로: 이메일 중복
# ---------------------------------------------------------------------------

class TestDuplicateEmail:
    """이미 등록된 이메일로 가입하면 거부된다."""

    def test_중복_이메일이면_ValueError가_발생한다(self, svc, repo):
        repo.find_by_email.return_value = {"id": 99}

        with pytest.raises(ValueError, match="이미 등록된"):
            svc.register("Bob", "existing@t.com", "pass1234")

    def test_중복_이메일이면_저장소에_저장하지_않는다(self, svc, repo):
        repo.find_by_email.return_value = {"id": 99}

        with pytest.raises(ValueError):
            svc.register("Bob", "existing@t.com", "pass1234")

        repo.save.assert_not_called()

    def test_중복_이메일이면_이메일을_발송하지_않는다(self, svc, repo, sender):
        repo.find_by_email.return_value = {"id": 99}

        with pytest.raises(ValueError):
            svc.register("Bob", "existing@t.com", "pass1234")

        sender.send.assert_not_called()


# ---------------------------------------------------------------------------
# 실패 경로: 비밀번호 유효성
# ---------------------------------------------------------------------------

class TestPasswordValidation:
    """비밀번호가 8자 미만이면 가입이 거부된다."""

    def test_7자_비밀번호는_거부된다(self, svc):
        with pytest.raises(ValueError, match="8자 이상"):
            svc.register("Charlie", "c@t.com", "1234567")

    def test_짧은_비밀번호면_저장소에_저장하지_않는다(self, svc, repo):
        with pytest.raises(ValueError):
            svc.register("Charlie", "c@t.com", "short")

        repo.save.assert_not_called()

    def test_짧은_비밀번호면_이메일을_발송하지_않는다(self, svc, repo, sender):
        with pytest.raises(ValueError):
            svc.register("Charlie", "c@t.com", "short")

        sender.send.assert_not_called()

    def test_정확히_8자_비밀번호는_허용된다(self, svc, repo):
        repo.save.return_value = {"id": 1}

        svc.register("Dave", "d@t.com", "exactly8")

        repo.save.assert_called_once()
```

---

## 3. 변경 사항 정리

| 항목 | Before | After | 이유 |
|------|--------|-------|------|
| **테스트 이름** | `test_register` | `test_저장소에_올바른_사용자_정보가_전달된다` 등 | 테스트가 명세 역할을 하도록 행위 기반 명명 |
| **구조** | 평면적 함수 나열 | `TestRegisterSuccess`, `TestDuplicateEmail`, `TestPasswordValidation` 클래스 | 관련 테스트를 시나리오별로 그룹화하여 가독성 향상 |
| **Mock 생성** | 매 테스트에서 반복 | `@pytest.fixture`로 추출 | DRY 원칙, 테스트 본문이 본질적 설정에만 집중 |
| **Mock spec** | `Mock()` | `Mock(spec=UserRepository)` | 존재하지 않는 메서드 호출 시 즉시 실패하도록 하여 오타/리팩토링 안전성 확보 |
| **인자 검증** | `assert_called_once()` | `assert_called_once_with(...)` | 잘못된 인자로 호출되는 위양성 방지 |
| **반환값 검증** | `result['name'] == 'Alice'` | `result is saved_user` | Mock return_value의 필드를 검증하는 것은 의미가 없으므로, save 반환값을 그대로 전달하는지를 identity로 검증 |
| **부작용 미발생 검증** | 없음 | `assert_not_called()` 추가 | 예외 경로에서 save/send가 실행되지 않음을 명시적으로 보장 |
| **경계값 테스트** | 없음 | `test_정확히_8자_비밀번호는_허용된다` 추가 | 8자 경계에서의 동작을 검증 (off-by-one 방지) |
| **테스트 단위** | 하나의 테스트에서 여러 관심사 검증 | 테스트당 하나의 관심사 | 실패 시 원인을 즉시 특정할 수 있도록 단일 책임 원칙 적용 |
