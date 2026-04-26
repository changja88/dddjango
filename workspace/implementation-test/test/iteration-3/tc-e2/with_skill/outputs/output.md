# NotificationService 테스트 코드 리뷰 및 리팩토링

## Review

테스트가 기본적인 AAA 구조를 따르고 있으며, 각 테스트가 하나의 행위를 검증하고, setup_method로 공통 설정을 분리한 점은 잘 되어 있다. send_bulk의 부분 실패, 예외, 전체 성공 시나리오를 나누어 검증하는 구성도 좋다.

다음은 개선이 필요한 항목이다.

```
[Mock without spec] — 모든 Mock 객체에 spec이 없다. spec 없는 Mock은 존재하지 않는 메서드를 호출해도
오류 없이 통과하므로, 프로덕션 코드의 인터페이스가 변경되었을 때 테스트가 여전히 통과하는 거짓 양성이 발생한다.
```

```
[The Inspector / 구현 결합] — test_send_welcome_email_only에서 user_repo.find_by_id.assert_called_once_with(1),
template.render.assert_called_once_with(...) 등 내부 협력 객체의 호출 순서와 인자까지 모두 검증한다.
이는 구현 세부사항에 결합된 통신 기반 검증으로, 내부 리팩토링 시 테스트가 깨진다.
반환값(출력 기반 검증)으로 충분한 부분은 Mock assert를 제거해야 한다.
```

```
[검증 방식 우선순위 위반] — 검증 우선순위는 출력 기반 > 상태 기반 > 통신 기반이다.
test_send_welcome_email_only는 반환값 검증(출력 기반)과 mock.assert_called(통신 기반)을 동시에 사용하는데,
출력 기반 검증으로 행위가 확인되면 내부 호출 검증은 불필요하다.
단, email_client와 sms_client는 외부 의존성이므로 이들의 호출 여부 검증은 적절하다.
```

```
[pytest fixture 미사용] — setup_method(xUnit 스타일)을 사용하고 있다. pytest에서는 @pytest.fixture를
사용하는 것이 권장되며, 의존성 주입 방식으로 테스트 간 격리가 명확해지고 재사용성이 높아진다.
```

```
[parametrize 미활용] — test_send_bulk_partial_failure와 test_send_bulk_all_success는 입력 데이터만
다르고 구조가 유사하다. send_bulk의 다양한 시나리오를 parametrize로 통합할 수 있다.
```

```
[에러 메시지 미검증] — test_send_welcome_user_not_found에서 ValueError 발생은 확인하지만
에러 메시지 내용을 검증하지 않는다. pytest.raises의 match 파라미터로 메시지까지 확인해야 한다.
```

### Review Checklist 확인

- [x] Tests with multiple Act sections that should be separate tests -- 해당 없음
- [x] Shared mutable state between tests -- setup_method이 매 테스트마다 초기화하므로 문제 없음
- [x] Mock overuse -- user_repo, template_engine은 내부 협력자인데 Mock으로 대체함. 외부 의존성(email, sms)만 Mock하는 것이 원칙이나, 이 경우 repo와 template은 인프라 의존성에 가까워 Mock이 허용됨
- [x] Missing spec/autospec on Mock objects -- **발견됨**: 4개 Mock 모두 spec 없음
- [x] Flaky tests depending on time, order, or external services -- 해당 없음
- [x] Missing parametrize for repetitive test cases with different data -- **발견됨**: send_bulk 계열 테스트
- [x] Excessive setup that obscures the test's intent -- 해당 없음
- [x] Assert on implementation details instead of behavior (The Inspector) -- **발견됨**: 내부 호출 순서/인자 과잉 검증
- [x] Tests without meaningful assertions (The Liar / Secret Catcher) -- 해당 없음
- [x] Wrong test level -- 해당 없음

---

## Refactoring

### Change 1: setup_method -> pytest fixture

[Before]
```python
class TestNotificationService:
    def setup_method(self):
        self.user_repo = Mock()
        self.template = Mock()
        self.email = Mock()
        self.sms = Mock()
        self.service = NotificationService(self.user_repo, self.template, self.email, self.sms)
```

[After]
```python
@pytest.fixture
def notification_deps():
    """NotificationService의 의존성 Mock 객체들을 생성한다."""
    user_repo = Mock(spec=["find_by_id"])
    template_engine = Mock(spec=["render"])
    email_client = Mock(spec=["send"])
    sms_client = Mock(spec=["send"])
    return user_repo, template_engine, email_client, sms_client


@pytest.fixture
def notification_service(notification_deps):
    """테스트용 NotificationService 인스턴스를 생성한다."""
    user_repo, template_engine, email_client, sms_client = notification_deps
    return NotificationService(user_repo, template_engine, email_client, sms_client)
```

[Reason] pytest Fixtures (Section 2) -- pytest fixture는 의존성 주입 방식으로 테스트 간 격리를 보장하고, conftest.py를 통한 공유가 가능하다. setup_method의 self 참조 대신 명시적 파라미터 전달로 테스트 의도가 명확해진다.

### Change 2: Mock에 spec 추가

[Before]
```python
self.user_repo = Mock()
self.template = Mock()
self.email = Mock()
self.sms = Mock()
```

[After]
```python
user_repo = Mock(spec=["find_by_id"])
template_engine = Mock(spec=["render"])
email_client = Mock(spec=["send"])
sms_client = Mock(spec=["send"])
```

[Reason] Mock Patterns (Section 1, 4) -- spec 없는 Mock은 존재하지 않는 메서드 호출을 허용하여 거짓 양성을 유발한다. spec을 지정하면 인터페이스가 변경될 때 테스트가 올바르게 실패한다.

### Change 3: 과잉 통신 기반 검증 제거

[Before]
```python
def test_send_welcome_email_only(self):
    self.user_repo.find_by_id.return_value = {'name': 'Alice', 'email': 'alice@test.com'}
    self.template.render.return_value = '<h1>Welcome Alice</h1>'

    result = self.service.send_welcome(1)

    self.user_repo.find_by_id.assert_called_once_with(1)
    self.template.render.assert_called_once_with('welcome', {'name': 'Alice'})
    self.email.send.assert_called_once_with('alice@test.com', '환영합니다', '<h1>Welcome Alice</h1>')
    self.sms.send.assert_not_called()
    assert result['status'] == 'sent'
    assert result['channels'] == ['email']
```

[After]
```python
def test_send_welcome_email_only(notification_service, notification_deps):
    user_repo, _, email_client, sms_client = notification_deps
    user_repo.find_by_id.return_value = {"name": "Alice", "email": "alice@test.com"}

    result = notification_service.send_welcome(1)

    assert result == {"status": "sent", "channels": ["email"]}
    email_client.send.assert_called_once()
    sms_client.send.assert_not_called()
```

[Reason] 검증 방식 우선순위 (Test Doubles Section 2) + The Inspector 안티패턴 (Test Quality Section 4) -- 반환값으로 행위를 검증할 수 있으면 출력 기반 검증을 우선한다. user_repo.find_by_id와 template.render는 내부 구현 세부사항이므로 호출 인자 검증을 제거한다. email_client와 sms_client는 외부 의존성이므로 호출 여부 검증은 유지하되, 정확한 인자 검증은 제거하여 구현 변경에 대한 내성을 높인다.

### Change 4: 에러 메시지 match 검증 추가

[Before]
```python
def test_send_welcome_user_not_found(self):
    self.user_repo.find_by_id.return_value = None
    with pytest.raises(ValueError):
        self.service.send_welcome(999)
```

[After]
```python
def test_send_welcome_user_not_found(notification_service, notification_deps):
    user_repo, _, _, _ = notification_deps
    user_repo.find_by_id.return_value = None

    with pytest.raises(ValueError, match="999"):
        notification_service.send_welcome(999)
```

[Reason] pytest Fixtures (Section 5) -- pytest.raises의 match 파라미터로 에러 메시지를 검증하면, 다른 ValueError가 우연히 발생해 테스트가 거짓 통과하는 것을 방지한다.

### Change 5: send_bulk 테스트 parametrize 적용

[Before]
```python
def test_send_bulk_all_success(self):
    self.user_repo.find_by_id.side_effect = [
        {'name': 'Alice', 'email': 'a@t.com'},
        {'name': 'Bob', 'email': 'b@t.com'},
    ]
    self.template.render.return_value = '<p>content</p>'

    result = self.service.send_bulk([1, 2], 'promo', {'subject': '세일'})

    assert result['sent'] == 2
    assert result['failed'] == 0
    assert self.email.send.call_count == 2

def test_send_bulk_partial_failure(self):
    self.user_repo.find_by_id.side_effect = [
        {'name': 'Alice', 'email': 'a@t.com'},
        None,
        {'name': 'Charlie', 'email': 'c@t.com'},
    ]
    self.template.render.return_value = '<p>hi</p>'

    result = self.service.send_bulk([1, 2, 3], 'info', {'subject': '공지'})

    assert result['sent'] == 2
    assert result['failed'] == 1
    assert '사용자 2 없음' in result['errors']
```

[After]
```python
@pytest.mark.parametrize(
    "user_lookup_results, user_ids, expected_sent, expected_failed",
    [
        pytest.param(
            [{"name": "Alice", "email": "a@t.com"}, {"name": "Bob", "email": "b@t.com"}],
            [1, 2],
            2,
            0,
            id="all-success",
        ),
        pytest.param(
            [{"name": "Alice", "email": "a@t.com"}, None, {"name": "Charlie", "email": "c@t.com"}],
            [1, 2, 3],
            2,
            1,
            id="partial-failure-user-not-found",
        ),
    ],
)
def test_send_bulk_results(
    notification_service, notification_deps,
    user_lookup_results, user_ids, expected_sent, expected_failed,
):
    user_repo, template_engine, _, _ = notification_deps
    user_repo.find_by_id.side_effect = user_lookup_results
    template_engine.render.return_value = "<p>content</p>"

    result = notification_service.send_bulk(user_ids, "promo", {"subject": "알림"})

    assert result["sent"] == expected_sent
    assert result["failed"] == expected_failed
```

[Reason] pytest Fixtures (Section 6) -- 동일한 Act(send_bulk 호출)에 대해 입력 데이터만 다른 테스트는 parametrize로 통합하여 중복을 제거한다. pytest.param의 id로 각 케이스의 의미를 명확히 한다.

### Change 6: partial failure의 에러 메시지 검증을 별도 테스트로 분리

[Before]
```python
# test_send_bulk_partial_failure 안에 에러 메시지 검증이 포함됨
assert '사용자 2 없음' in result['errors']
```

[After]
```python
def test_send_bulk_records_missing_user_error(notification_service, notification_deps):
    user_repo, template_engine, _, _ = notification_deps
    user_repo.find_by_id.side_effect = [
        {"name": "Alice", "email": "a@t.com"},
        None,
    ]
    template_engine.render.return_value = "<p>content</p>"

    result = notification_service.send_bulk([1, 2], "promo", {"subject": "알림"})

    assert "사용자 2 없음" in result["errors"]
```

[Reason] AAA 패턴 (Test Quality Section 2) -- 에러 메시지의 내용 검증은 sent/failed 카운트 검증과 다른 관심사다. parametrize된 테스트에서는 카운트만 검증하고, 에러 메시지 형식은 별도 테스트로 분리하여 각 테스트의 의도를 명확히 한다.

### Change 7: send_welcome with SMS 테스트의 구현 결합 완화

[Before]
```python
def test_send_welcome_with_sms(self):
    self.user_repo.find_by_id.return_value = {'name': 'Bob', 'email': 'bob@test.com', 'phone': '010-1234-5678'}
    self.template.render.return_value = '<h1>Welcome Bob</h1>'

    result = self.service.send_welcome(2)

    self.email.send.assert_called_once()
    self.sms.send.assert_called_once_with('010-1234-5678', 'Bob님, 가입을 환영합니다!')
    assert 'sms' in result['channels']
```

[After]
```python
def test_send_welcome_with_phone_sends_sms(notification_service, notification_deps):
    user_repo, _, email_client, sms_client = notification_deps
    user_repo.find_by_id.return_value = {
        "name": "Bob", "email": "bob@test.com", "phone": "010-1234-5678",
    }

    result = notification_service.send_welcome(2)

    assert result == {"status": "sent", "channels": ["email", "sms"]}
    email_client.send.assert_called_once()
    sms_client.send.assert_called_once()
```

[Reason] 검증 방식 우선순위 (Test Doubles Section 2) -- 반환값의 channels 리스트가 이미 SMS 발송 여부를 나타내므로 출력 기반 검증으로 충분하다. sms_client.send의 정확한 인자(메시지 문구)를 검증하면 메시지 포맷 변경 시 테스트가 깨지므로, 호출 여부만 확인한다.

---

## Complete Refactored Code

```python
import pytest
from unittest.mock import Mock
from datetime import datetime


class NotificationService:
    def __init__(self, user_repo, template_engine, email_client, sms_client):
        self.user_repo = user_repo
        self.template_engine = template_engine
        self.email_client = email_client
        self.sms_client = sms_client

    def send_welcome(self, user_id: int) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"사용자 {user_id}을 찾을 수 없습니다")
        html = self.template_engine.render("welcome", {"name": user["name"]})
        self.email_client.send(user["email"], "환영합니다", html)
        if user.get("phone"):
            self.sms_client.send(user["phone"], f'{user["name"]}님, 가입을 환영합니다!')
        return {
            "status": "sent",
            "channels": ["email"] + (["sms"] if user.get("phone") else []),
        }

    def send_bulk(self, user_ids: list[int], template_name: str, context: dict) -> dict:
        results = {"sent": 0, "failed": 0, "errors": []}
        for uid in user_ids:
            try:
                user = self.user_repo.find_by_id(uid)
                if not user:
                    results["failed"] += 1
                    results["errors"].append(f"사용자 {uid} 없음")
                    continue
                html = self.template_engine.render(
                    template_name, {**context, "name": user["name"]}
                )
                self.email_client.send(user["email"], context.get("subject", "알림"), html)
                results["sent"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
        return results


# ===== Fixtures =====


@pytest.fixture
def notification_deps():
    """NotificationService의 의존성 Mock 객체들을 생성한다."""
    user_repo = Mock(spec=["find_by_id"])
    template_engine = Mock(spec=["render"])
    email_client = Mock(spec=["send"])
    sms_client = Mock(spec=["send"])
    return user_repo, template_engine, email_client, sms_client


@pytest.fixture
def notification_service(notification_deps):
    """테스트용 NotificationService 인스턴스를 생성한다."""
    user_repo, template_engine, email_client, sms_client = notification_deps
    return NotificationService(user_repo, template_engine, email_client, sms_client)


# ===== send_welcome Tests =====


class TestSendWelcome:

    def test_email_only(self, notification_service, notification_deps):
        user_repo, _, email_client, sms_client = notification_deps
        user_repo.find_by_id.return_value = {"name": "Alice", "email": "alice@test.com"}

        result = notification_service.send_welcome(1)

        assert result == {"status": "sent", "channels": ["email"]}
        email_client.send.assert_called_once()
        sms_client.send.assert_not_called()

    def test_with_phone_sends_sms(self, notification_service, notification_deps):
        user_repo, _, email_client, sms_client = notification_deps
        user_repo.find_by_id.return_value = {
            "name": "Bob",
            "email": "bob@test.com",
            "phone": "010-1234-5678",
        }

        result = notification_service.send_welcome(2)

        assert result == {"status": "sent", "channels": ["email", "sms"]}
        email_client.send.assert_called_once()
        sms_client.send.assert_called_once()

    def test_user_not_found_raises(self, notification_service, notification_deps):
        user_repo, _, _, _ = notification_deps
        user_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="999"):
            notification_service.send_welcome(999)


# ===== send_bulk Tests =====


class TestSendBulk:

    @pytest.mark.parametrize(
        "user_lookup_results, user_ids, expected_sent, expected_failed",
        [
            pytest.param(
                [
                    {"name": "Alice", "email": "a@t.com"},
                    {"name": "Bob", "email": "b@t.com"},
                ],
                [1, 2],
                2,
                0,
                id="all-success",
            ),
            pytest.param(
                [
                    {"name": "Alice", "email": "a@t.com"},
                    None,
                    {"name": "Charlie", "email": "c@t.com"},
                ],
                [1, 2, 3],
                2,
                1,
                id="partial-failure-user-not-found",
            ),
        ],
    )
    def test_bulk_send_results(
        self,
        notification_service,
        notification_deps,
        user_lookup_results,
        user_ids,
        expected_sent,
        expected_failed,
    ):
        user_repo, template_engine, _, _ = notification_deps
        user_repo.find_by_id.side_effect = user_lookup_results
        template_engine.render.return_value = "<p>content</p>"

        result = notification_service.send_bulk(user_ids, "promo", {"subject": "알림"})

        assert result["sent"] == expected_sent
        assert result["failed"] == expected_failed

    def test_records_missing_user_error(self, notification_service, notification_deps):
        user_repo, template_engine, _, _ = notification_deps
        user_repo.find_by_id.side_effect = [
            {"name": "Alice", "email": "a@t.com"},
            None,
        ]
        template_engine.render.return_value = "<p>content</p>"

        result = notification_service.send_bulk([1, 2], "promo", {"subject": "알림"})

        assert "사용자 2 없음" in result["errors"]

    def test_email_exception_is_captured(self, notification_service, notification_deps):
        user_repo, template_engine, email_client, _ = notification_deps
        user_repo.find_by_id.return_value = {"name": "Alice", "email": "a@t.com"}
        template_engine.render.return_value = "<p>hi</p>"
        email_client.send.side_effect = ConnectionError("SMTP 연결 실패")

        result = notification_service.send_bulk([1], "alert", {"subject": "긴급"})

        assert result["failed"] == 1
        assert "SMTP 연결 실패" in result["errors"][0]
```

---

## Summary of Changes

| # | 변경 | 적용 원칙 |
|---|------|-----------|
| 1 | `setup_method` -> `@pytest.fixture` | pytest Fixtures |
| 2 | 모든 Mock에 `spec` 추가 | Mock Patterns -- spec/autospec |
| 3 | 내부 협력자(user_repo, template)의 호출 인자 검증 제거 | 검증 우선순위, The Inspector 안티패턴 |
| 4 | `pytest.raises`에 `match` 추가 | pytest 예외 테스트 |
| 5 | send_bulk 성공/부분실패를 `parametrize`로 통합 | pytest parametrize |
| 6 | 에러 메시지 검증을 별도 테스트로 분리 | AAA 패턴 -- 하나의 행위 검증 |
| 7 | SMS 테스트의 인자 검증 완화 | 검증 우선순위 -- 출력 기반 우선 |
