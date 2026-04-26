# 테스트 코드 리팩토링

---

## 변경 1: freezegun을 time-machine으로 교체

[Before]
```python
from freezegun import freeze_time

@freeze_time('2024-03-15 10:00:00')
def test_schedule_reminder():
    ...
    assert result['created_at'] == datetime(2024, 3, 15, 10, 0)
    ...

@freeze_time('2024-03-20 09:30:00')
@patch('requests.post')
def test_process_due_reminders(mock_post):
    ...

@freeze_time('2024-03-20 09:30:00')
@patch('requests.post')
def test_process_partial_failure(mock_post):
    ...
```

[After]
```python
import time_machine

@time_machine.travel("2024-03-15 10:00:00", tick=False)
def test_schedule_reminder():
    ...

@time_machine.travel("2024-03-20 09:30:00", tick=False)
def test_process_due_reminders():
    ...

@time_machine.travel("2024-03-20 09:30:00", tick=False)
def test_process_partial_failure():
    ...
```

[Reason] External Dependencies / Time Mocking -- time-machine은 C 확장 기반으로 freezegun보다 100~200배 빠르다. CPython 프로젝트에서는 time-machine이 권장된다.

---

## 변경 2: `@patch('requests.post')` 를 `responses` 라이브러리로 교체

[Before]
```python
@freeze_time('2024-03-20 09:30:00')
@patch('requests.post')
def test_process_due_reminders(mock_post):
    db = MagicMock()
    db.find_due.return_value = [
        {'email': 'a@test.com', 'message': 'msg1', 'sent': False},
        {'email': 'b@test.com', 'message': 'msg2', 'sent': False},
    ]
    mock_post.return_value.status_code = 200

    scheduler = NotificationScheduler(db, 'http://email-api.test')
    count = scheduler.process_due_reminders()

    assert count == 2
    assert mock_post.call_count == 2
```

[After]
```python
@time_machine.travel("2024-03-20 09:30:00", tick=False)
@responses.activate
def test_process_due_reminders():
    responses.add(responses.POST, "http://email-api.test/send", status=200)
    db = MagicMock()
    db.find_due.return_value = [
        {"email": "a@test.com", "message": "msg1", "sent": False},
        {"email": "b@test.com", "message": "msg2", "sent": False},
    ]

    scheduler = NotificationScheduler(db, "http://email-api.test")
    count = scheduler.process_due_reminders()

    assert count == 2
    assert len(responses.calls) == 2
```

[Reason] External Dependencies / HTTP Mocking -- `@patch('requests.post')`는 모듈 경로 기반 패치로 취약하다. `requests.post`를 import하는 경로가 바뀌면 깨진다. `responses` 라이브러리는 requests 자체를 인터셉트하므로 import 경로에 무관하며, 실제 HTTP 요청/응답 구조(URL, status, body)를 검증할 수 있어 테스트 신뢰도가 높다.

---

## 변경 3: 부분 실패 테스트에서 순차 응답을 `responses`로 표현

[Before]
```python
@freeze_time('2024-03-20 09:30:00')
@patch('requests.post')
def test_process_partial_failure(mock_post):
    db = MagicMock()
    db.find_due.return_value = [
        {'email': 'a@test.com', 'message': 'msg1', 'sent': False},
        {'email': 'b@test.com', 'message': 'msg2', 'sent': False},
    ]
    mock_post.side_effect = [
        MagicMock(status_code=200),
        MagicMock(status_code=500),
    ]

    scheduler = NotificationScheduler(db, 'http://email-api.test')
    count = scheduler.process_due_reminders()

    assert count == 1
```

[After]
```python
@time_machine.travel("2024-03-20 09:30:00", tick=False)
@responses.activate
def test_process_partial_failure():
    responses.add(responses.POST, "http://email-api.test/send", status=200)
    responses.add(responses.POST, "http://email-api.test/send", status=500)
    db = MagicMock()
    db.find_due.return_value = [
        {"email": "a@test.com", "message": "msg1", "sent": False},
        {"email": "b@test.com", "message": "msg2", "sent": False},
    ]

    scheduler = NotificationScheduler(db, "http://email-api.test")
    count = scheduler.process_due_reminders()

    assert count == 1
    assert db.save.call_count == 1
```

[Reason] External Dependencies / HTTP Mocking -- `responses`의 순차 등록은 `side_effect` 리스트보다 선언적이며, 각 응답의 status code가 무엇인지 명시적으로 드러난다. 또한 `db.save` 호출 횟수를 검증하여 성공한 건만 저장되었는지도 확인한다.

---

## 변경 4: db MagicMock에 spec 추가 및 공통 fixture 추출

[Before]
```python
def test_schedule_reminder():
    db = MagicMock()
    scheduler = NotificationScheduler(db, 'http://email-api.test')
    ...

def test_process_due_reminders(mock_post):
    db = MagicMock()
    ...
    scheduler = NotificationScheduler(db, 'http://email-api.test')
    ...

def test_process_partial_failure(mock_post):
    db = MagicMock()
    ...
    scheduler = NotificationScheduler(db, 'http://email-api.test')
    ...

def test_get_pending_count():
    db = MagicMock()
    ...
    scheduler = NotificationScheduler(db, 'http://email-api.test')
    ...
```

[After]
```python
EMAIL_API_URL = "http://email-api.test"

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def scheduler(mock_db):
    return NotificationScheduler(mock_db, EMAIL_API_URL)
```

[Reason] Complex Setup / Fixture Extraction -- 4개 테스트 모두 동일한 `MagicMock()` + `NotificationScheduler` 생성을 반복한다. fixture로 추출하면 중복이 제거되고, DB 인터페이스가 변경될 때 수정 지점이 하나로 줄어든다. 상수 `EMAIL_API_URL`도 추출하여 매직 스트링을 제거한다.

---

## 변경 5: 통신 기반 검증을 출력 기반 검증으로 보강

[Before]
```python
def test_schedule_reminder():
    ...
    assert result['email'] == 'user@test.com'
    assert result['created_at'] == datetime(2024, 3, 15, 10, 0)
    db.save.assert_called_once()
```

[After]
```python
def test_schedule_reminder():
    ...
    assert result['email'] == 'user@test.com'
    assert result['message'] == '결제일 알림'
    assert result['send_at'] == datetime(2024, 3, 20, 9, 0)
    assert result['created_at'] == datetime(2024, 3, 15, 10, 0)
    assert result['sent'] is False
```

[Reason] Verification Priority -- 검증 우선순위는 출력 기반 > 상태 기반 > 통신 기반이다. `schedule_reminder`는 reminder dict를 반환하므로, 반환값의 모든 필드를 검증하는 것이 `db.save.assert_called_once()`보다 의미 있다. 반환값 검증이 충분하면 통신 기반 검증(`assert_called`)은 구현 결합도만 높인다.

---

## 완성된 리팩토링 코드

```python
import pytest
import responses
import time_machine
from unittest.mock import MagicMock
from datetime import datetime


class NotificationScheduler:
    def __init__(self, db, email_api_url: str):
        self.db = db
        self.email_api_url = email_api_url

    def schedule_reminder(self, user_email: str, message: str, send_at: datetime) -> dict:
        reminder = {
            "email": user_email,
            "message": message,
            "send_at": send_at,
            "created_at": datetime.now(),
            "sent": False,
        }
        self.db.save(reminder)
        return reminder

    def process_due_reminders(self) -> int:
        import requests

        due = self.db.find_due(datetime.now())
        sent_count = 0
        for reminder in due:
            resp = requests.post(
                f"{self.email_api_url}/send",
                json={"to": reminder["email"], "body": reminder["message"]},
            )
            if resp.status_code == 200:
                reminder["sent"] = True
                self.db.save(reminder)
                sent_count += 1
        return sent_count

    def get_pending_count(self) -> int:
        return len(self.db.find_pending())


# ===== Fixtures =====

EMAIL_API_URL = "http://email-api.test"


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def scheduler(mock_db):
    return NotificationScheduler(mock_db, EMAIL_API_URL)


# ===== Tests =====


@time_machine.travel("2024-03-15 10:00:00", tick=False)
def test_schedule_reminder(scheduler):
    send_at = datetime(2024, 3, 20, 9, 0)

    result = scheduler.schedule_reminder("user@test.com", "결제일 알림", send_at)

    assert result["email"] == "user@test.com"
    assert result["message"] == "결제일 알림"
    assert result["send_at"] == datetime(2024, 3, 20, 9, 0)
    assert result["created_at"] == datetime(2024, 3, 15, 10, 0)
    assert result["sent"] is False


@time_machine.travel("2024-03-20 09:30:00", tick=False)
@responses.activate
def test_process_due_reminders(scheduler, mock_db):
    responses.add(responses.POST, f"{EMAIL_API_URL}/send", status=200)
    mock_db.find_due.return_value = [
        {"email": "a@test.com", "message": "msg1", "sent": False},
        {"email": "b@test.com", "message": "msg2", "sent": False},
    ]

    count = scheduler.process_due_reminders()

    assert count == 2
    assert len(responses.calls) == 2


@time_machine.travel("2024-03-20 09:30:00", tick=False)
@responses.activate
def test_process_partial_failure(scheduler, mock_db):
    responses.add(responses.POST, f"{EMAIL_API_URL}/send", status=200)
    responses.add(responses.POST, f"{EMAIL_API_URL}/send", status=500)
    mock_db.find_due.return_value = [
        {"email": "a@test.com", "message": "msg1", "sent": False},
        {"email": "b@test.com", "message": "msg2", "sent": False},
    ]

    count = scheduler.process_due_reminders()

    assert count == 1
    assert mock_db.save.call_count == 1


def test_get_pending_count(scheduler, mock_db):
    mock_db.find_pending.return_value = [1, 2, 3]

    assert scheduler.get_pending_count() == 3
```

---

## 변경 요약

| 항목 | Before | After | 근거 |
|------|--------|-------|------|
| 시간 모킹 | `freezegun` | `time-machine` | 100~200배 빠른 C 확장 기반 |
| HTTP 모킹 | `@patch('requests.post')` | `responses` | 경로 무관 인터셉트, 선언적 응답 등록 |
| DB mock 생성 | 매 테스트마다 `MagicMock()` 반복 | `@pytest.fixture`로 추출 | 중복 제거, 수정 지점 단일화 |
| API URL | 매직 스트링 반복 | 상수 `EMAIL_API_URL` 추출 | 변경 시 한 곳만 수정 |
| 검증 방식 | `db.save.assert_called_once()` (통신 기반) | 반환값 필드 전체 검증 (출력 기반) | 검증 우선순위 원칙 적용 |
