# 테스트 냄새 제거 리팩토링

## 식별된 테스트 냄새

| # | 테스트 냄새 | 위치 | 설명 |
|---|-----------|------|------|
| 1 | **Eager Test** | `test_user_operations` | 하나의 테스트에서 등록, 조회, 비활성화, 예외 등 여러 동작을 한꺼번에 검증한다. 실패 시 어떤 동작이 문제인지 파악이 어렵다. |
| 2 | **Obscure Test (Global Fixture)** | `setup_module`, `global db` | 모듈 수준 전역 변수를 fixture로 사용하여 테스트 간 상태가 공유된다. 테스트 실행 순서에 따라 결과가 달라질 수 있다. |
| 3 | **Shared State / Erratic Test** | `db` 전역 변수 | 모든 테스트가 같은 `db` 딕셔너리를 공유하므로, 한 테스트에서 추가한 데이터가 다른 테스트에 영향을 준다. |
| 4 | **Exception Handling with try/except** | `test_validation` | `pytest.raises`를 쓰지 않고 `try/except + assert False` 패턴을 사용한다. pytest의 관용적 방식이 아니며 가독성이 떨어진다. |
| 5 | **Slow Test / 불필요한 성능 테스트** | `test_performance` | 단위 테스트에 `time.time()` 기반 성능 측정이 섞여 있다. 실행 환경에 따라 결과가 불안정(flaky)하며, 단위 테스트의 목적에 맞지 않는다. |
| 6 | **Mystery Guest** | `import os` | 사용하지 않는 `os` 모듈이 임포트되어 있어 테스트 의도를 흐린다. |
| 7 | **Production Logic in Test File** | `UserService` 클래스 | 프로덕션 코드(SUT)가 테스트 파일 안에 정의되어 있어 역할 분리가 되지 않는다. |

## 리팩토링된 코드

### `user_service.py` -- 프로덕션 코드 분리

```python
class UserService:
    def __init__(self, db=None):
        self.db = db if db is not None else {"users": []}

    def register(self, name, email):
        if not name:
            raise ValueError("이름 필수")
        if "@" not in email:
            raise ValueError("이메일 형식 오류")
        user = {"name": name, "email": email, "active": True}
        self.db["users"].append(user)
        return user

    def deactivate(self, email):
        for u in self.db["users"]:
            if u["email"] == email:
                u["active"] = False
                return u
        raise ValueError("사용자 없음")

    def find(self, email):
        for u in self.db["users"]:
            if u["email"] == email:
                return u
        return None
```

### `test_user_service.py` -- 리팩토링된 테스트

```python
import pytest

from user_service import UserService


@pytest.fixture
def db():
    return {"users": []}


@pytest.fixture
def service(db):
    return UserService(db)


class TestRegister:
    def test_register_returns_user_with_correct_name(self, service):
        user = service.register("Alice", "alice@test.com")
        assert user["name"] == "Alice"

    def test_register_returns_user_with_correct_email(self, service):
        user = service.register("Alice", "alice@test.com")
        assert user["email"] == "alice@test.com"

    def test_register_returns_active_user(self, service):
        user = service.register("Alice", "alice@test.com")
        assert user["active"] is True

    def test_register_raises_on_empty_name(self, service):
        with pytest.raises(ValueError, match="이름 필수"):
            service.register("", "test@test.com")

    def test_register_raises_on_invalid_email(self, service):
        with pytest.raises(ValueError, match="이메일 형식 오류"):
            service.register("Bob", "invalid-email")


class TestFind:
    def test_find_returns_registered_user(self, service):
        service.register("Alice", "alice@test.com")
        found = service.find("alice@test.com")
        assert found is not None
        assert found["name"] == "Alice"

    def test_find_returns_none_for_unknown_email(self, service):
        result = service.find("nobody@test.com")
        assert result is None


class TestDeactivate:
    def test_deactivate_sets_user_inactive(self, service):
        service.register("Alice", "alice@test.com")
        result = service.deactivate("alice@test.com")
        assert result["active"] is False

    def test_deactivated_user_stays_inactive_on_find(self, service):
        service.register("Alice", "alice@test.com")
        service.deactivate("alice@test.com")
        found = service.find("alice@test.com")
        assert found["active"] is False

    def test_deactivate_raises_for_unknown_user(self, service):
        with pytest.raises(ValueError, match="사용자 없음"):
            service.deactivate("nobody@test.com")
```

## 리팩토링 요약

| 테스트 냄새 | 적용한 해결책 |
|-----------|------------|
| **Eager Test** | `test_user_operations`를 단일 관심사별로 분리했다. 각 테스트 메서드는 하나의 동작만 검증한다. |
| **Global Fixture / Shared State** | `setup_module`과 전역 `db`를 제거하고, `@pytest.fixture`로 테스트마다 독립된 `db`와 `service` 인스턴스를 주입한다. |
| **try/except 패턴** | `pytest.raises(ValueError, match=...)`로 교체하여 예외 타입과 메시지를 한 번에 검증한다. |
| **Slow Test** | `test_performance`를 제거했다. 성능 측정은 별도 벤치마크 도구(예: `pytest-benchmark`)로 수행해야 한다. |
| **Mystery Guest** | 사용하지 않는 `os`, `time` 임포트를 제거했다. |
| **Production Logic in Test** | `UserService`를 `user_service.py`로 분리하고, `db`를 생성자 주입 방식으로 변경하여 테스트에서 fixture를 통해 제어할 수 있게 했다. |
