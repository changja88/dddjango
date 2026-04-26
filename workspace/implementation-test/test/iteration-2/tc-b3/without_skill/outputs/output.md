# 테스트 코드 리팩토링 분석

## 현재 코드의 문제점

### 1. `freezegun` 외부 의존성이 불필요하다
Python 3.3 이상에서는 `unittest.mock.patch`로 `datetime.now()`를 직접 모킹할 수 있고, Python 3.10 이상에서는 `datetime`이 서브클래싱 없이도 직접 mock 가능하다. `freezegun`은 강력한 라이브러리이지만 이 정도 수준의 시간 고정에는 과하다.

### 2. 프로덕션 코드에서 `import requests`가 함수 내부에 있다
`process_due_reminders` 메서드 안에서 `import requests`를 하고 있어서 `@patch('requests.post')`의 패치 대상이 모듈 레벨의 `requests`가 된다. 이것은 동작하긴 하지만, 패치 대상 경로가 불명확하고 깨지기 쉬운 구조다.

### 3. 의존성 주입을 충분히 활용하지 않는다
`db`는 이미 생성자 주입을 하고 있으면서, HTTP 클라이언트(`requests`)는 하드코딩되어 있다. HTTP 호출도 주입하면 `@patch` 데코레이터가 필요 없어진다.

### 4. `datetime.now()` 직접 호출은 테스트하기 어려운 패턴이다
시간을 외부에서 주입하거나 clock 함수를 주입하면 `freezegun` 없이도 깔끔하게 테스트할 수 있다.

### 5. MagicMock 남용
`db`가 어떤 인터페이스를 가져야 하는지 테스트 코드만 봐서는 알 수 없다. `spec`을 지정하지 않은 `MagicMock`은 존재하지 않는 메서드를 호출해도 에러가 나지 않아서 오탈자 버그를 잡지 못한다.

---

## 리팩토링 결과

### 프로덕션 코드 개선

```python
from datetime import datetime
from typing import Protocol, Callable


class ReminderDB(Protocol):
    """DB 인터페이스를 명시적으로 정의한다."""
    def save(self, reminder: dict) -> None: ...
    def find_due(self, now: datetime) -> list[dict]: ...
    def find_pending(self) -> list[dict]: ...


class EmailClient(Protocol):
    """HTTP 호출을 추상화하여 주입 가능하게 만든다."""
    def send(self, to: str, body: str) -> bool: ...


class RequestsEmailClient:
    """requests 기반 실제 구현체."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def send(self, to: str, body: str) -> bool:
        import requests
        resp = requests.post(
            f'{self.base_url}/send',
            json={'to': to, 'body': body},
        )
        return resp.status_code == 200


class NotificationScheduler:
    def __init__(
        self,
        db: ReminderDB,
        email_client: EmailClient,
        clock: Callable[[], datetime] = datetime.now,
    ):
        self.db = db
        self.email_client = email_client
        self.clock = clock

    def schedule_reminder(self, user_email: str, message: str, send_at: datetime) -> dict:
        reminder = {
            'email': user_email,
            'message': message,
            'send_at': send_at,
            'created_at': self.clock(),
            'sent': False,
        }
        self.db.save(reminder)
        return reminder

    def process_due_reminders(self) -> int:
        due = self.db.find_due(self.clock())
        sent_count = 0
        for reminder in due:
            if self.email_client.send(reminder['email'], reminder['message']):
                reminder['sent'] = True
                self.db.save(reminder)
                sent_count += 1
        return sent_count

    def get_pending_count(self) -> int:
        return len(self.db.find_pending())
```

### 테스트 코드 개선

```python
import pytest
from datetime import datetime
from unittest.mock import create_autospec


# --- Fakes ---

class FakeDB:
    """실제 동작하는 가짜 DB. MagicMock보다 의도가 명확하다."""
    def __init__(self):
        self.saved: list[dict] = []
        self._due: list[dict] = []
        self._pending: list[dict] = []

    def save(self, reminder: dict) -> None:
        self.saved.append(reminder)

    def find_due(self, now: datetime) -> list[dict]:
        return self._due

    def find_pending(self) -> list[dict]:
        return self._pending


class FakeEmailClient:
    """성공/실패 시나리오를 시퀀스로 제어할 수 있는 가짜 이메일 클라이언트."""
    def __init__(self, results: list[bool] | None = None):
        self.calls: list[tuple[str, str]] = []
        self._results = results or []
        self._index = 0

    def send(self, to: str, body: str) -> bool:
        self.calls.append((to, body))
        if self._results:
            result = self._results[self._index]
            self._index += 1
            return result
        return True  # 기본: 성공


# --- 공통 fixture ---

FIXED_NOW = datetime(2024, 3, 15, 10, 0, 0)
SEND_AT = datetime(2024, 3, 20, 9, 0, 0)


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def email_client():
    return FakeEmailClient()


@pytest.fixture
def scheduler(db, email_client):
    return NotificationScheduler(
        db=db,
        email_client=email_client,
        clock=lambda: FIXED_NOW,
    )


# --- 테스트 ---

class TestScheduleReminder:
    def test_saves_reminder_with_correct_fields(self, scheduler, db):
        result = scheduler.schedule_reminder('user@test.com', '결제일 알림', SEND_AT)

        assert result['email'] == 'user@test.com'
        assert result['message'] == '결제일 알림'
        assert result['send_at'] == SEND_AT
        assert result['created_at'] == FIXED_NOW
        assert result['sent'] is False

    def test_persists_to_db(self, scheduler, db):
        scheduler.schedule_reminder('user@test.com', '결제일 알림', SEND_AT)

        assert len(db.saved) == 1
        assert db.saved[0]['email'] == 'user@test.com'


class TestProcessDueReminders:
    def test_sends_all_due_reminders(self, db, email_client):
        db._due = [
            {'email': 'a@test.com', 'message': 'msg1', 'sent': False},
            {'email': 'b@test.com', 'message': 'msg2', 'sent': False},
        ]
        scheduler = NotificationScheduler(
            db=db,
            email_client=email_client,
            clock=lambda: datetime(2024, 3, 20, 9, 30),
        )

        count = scheduler.process_due_reminders()

        assert count == 2
        assert len(email_client.calls) == 2
        assert email_client.calls[0] == ('a@test.com', 'msg1')
        assert email_client.calls[1] == ('b@test.com', 'msg2')

    def test_marks_sent_reminders(self, db, email_client):
        db._due = [
            {'email': 'a@test.com', 'message': 'msg1', 'sent': False},
        ]
        scheduler = NotificationScheduler(
            db=db, email_client=email_client, clock=lambda: FIXED_NOW,
        )

        scheduler.process_due_reminders()

        assert db._due[0]['sent'] is True

    def test_partial_failure_counts_only_successes(self, db):
        db._due = [
            {'email': 'a@test.com', 'message': 'msg1', 'sent': False},
            {'email': 'b@test.com', 'message': 'msg2', 'sent': False},
        ]
        email_client = FakeEmailClient(results=[True, False])
        scheduler = NotificationScheduler(
            db=db, email_client=email_client, clock=lambda: FIXED_NOW,
        )

        count = scheduler.process_due_reminders()

        assert count == 1
        assert db._due[0]['sent'] is True
        assert db._due[1]['sent'] is False  # 실패한 건은 그대로

    def test_no_due_reminders(self, db, email_client):
        db._due = []
        scheduler = NotificationScheduler(
            db=db, email_client=email_client, clock=lambda: FIXED_NOW,
        )

        count = scheduler.process_due_reminders()

        assert count == 0
        assert len(email_client.calls) == 0


class TestGetPendingCount:
    def test_returns_count(self, db, email_client):
        db._pending = [1, 2, 3]
        scheduler = NotificationScheduler(
            db=db, email_client=email_client, clock=lambda: FIXED_NOW,
        )

        assert scheduler.get_pending_count() == 3

    def test_returns_zero_when_empty(self, db, email_client):
        db._pending = []
        scheduler = NotificationScheduler(
            db=db, email_client=email_client, clock=lambda: FIXED_NOW,
        )

        assert scheduler.get_pending_count() == 0
```

---

## 변경 사항 요약

| 항목 | Before | After |
|---|---|---|
| 시간 제어 | `@freeze_time` (외부 라이브러리) | `clock` 함수 주입 (의존성 제거) |
| HTTP 모킹 | `@patch('requests.post')` + `MagicMock` | `EmailClient` Protocol + `FakeEmailClient` |
| DB 모킹 | `MagicMock()` (spec 없음) | `FakeDB` (명시적 인터페이스 구현) |
| 인터페이스 정의 | 암묵적 | `Protocol`로 명시적 선언 |
| 테스트 구조 | 독립 함수 4개 | 클래스별 그룹핑 + fixture |
| 테스트 커버리지 | 4개 케이스 | 8개 케이스 (경계 조건 추가) |
| 외부 의존성 | `freezegun`, `requests` (테스트 시) | 없음 (표준 라이브러리만 사용) |

## 핵심 원칙

### 1. Mock보다 Fake를 선호한다
`MagicMock`은 편리하지만 실수로 존재하지 않는 메서드를 호출해도 통과시킨다. `FakeDB`처럼 직접 구현한 Fake 객체는 인터페이스를 명시적으로 준수하므로 더 안전하다.

### 2. 패치보다 주입을 선호한다
`@patch`는 문자열 경로로 대상을 지정하므로 리팩토링 시 깨지기 쉽다. 생성자 주입은 타입 시스템과 IDE의 지원을 받을 수 있고, 테스트 의도가 명확해진다.

### 3. 시간은 clock 함수로 주입한다
`datetime.now()`를 직접 호출하는 대신 `clock: Callable[[], datetime]`을 주입하면, `freezegun` 없이도 시간을 완전히 제어할 수 있다. 프로덕션에서는 기본값 `datetime.now`가 사용되므로 호출부 변경도 불필요하다.

### 4. Protocol을 사용하여 인터페이스를 문서화한다
`ReminderDB`와 `EmailClient` Protocol은 코드를 읽는 사람에게 "이 객체가 무엇을 할 수 있어야 하는지"를 명확히 전달한다. 런타임 오버헤드 없이 타입 체커의 검증도 받을 수 있다.
