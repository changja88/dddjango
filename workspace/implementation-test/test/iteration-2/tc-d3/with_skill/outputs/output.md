# unittest -> pytest 리팩토링

---

## 변경 1: unittest.TestCase 클래스 제거, pytest 함수 스타일로 전환

[Before]
```python
class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.notifier = MagicMock()
        self.manager = TaskManager(self.db, self.notifier)

    def test_create_task(self):
        self.db.save.return_value = { ... }
        result = self.manager.create_task(...)
        self.assertEqual(result['title'], '테스트')
```

[After]
```python
@pytest.fixture
def mock_db():
    return create_autospec(SomeDBProtocol, instance=True)

@pytest.fixture
def mock_notifier():
    return create_autospec(SomeNotifierProtocol, instance=True)

@pytest.fixture
def manager(mock_db, mock_notifier):
    return TaskManager(mock_db, mock_notifier)

def test_create_task(manager, mock_db, mock_notifier):
    mock_db.save.return_value = { ... }
    result = manager.create_task(...)
    assert result['title'] == '테스트'
```

[Reason] Fixtures / AAA -- pytest fixture로 전환하면 setUp/tearDown 대신 yield 기반 리소스 관리가 가능하며, 각 fixture의 스코프를 독립적으로 제어할 수 있다. `self.assert*` 호출이 `assert` 문으로 바뀌어 가독성이 향상된다.

---

## 변경 2: Mock에 spec 추가 (create_autospec)

[Before]
```python
self.db = MagicMock()
self.notifier = MagicMock()
```

[After]
```python
mock_db = create_autospec(AbstractDB, instance=True)
mock_notifier = create_autospec(AbstractNotifier, instance=True)
```

[Reason] Mock Patterns -- spec 없는 MagicMock은 존재하지 않는 메서드 호출도 허용하여 API 변경 시 테스트가 여전히 통과하는 위험이 있다. `create_autospec`으로 실제 인터페이스를 강제하면 API drift를 방지한다. 여기서는 프로토콜 클래스를 정의하여 spec으로 사용한다.

---

## 변경 3: 빈 제목 테스트를 parametrize로 통합

[Before]
```python
def test_create_task_empty_title(self):
    with self.assertRaises(ValueError) as ctx:
        self.manager.create_task('', 'alice', datetime(2024, 12, 31))
    self.assertIn('비어있습니다', str(ctx.exception))

def test_create_task_whitespace_only_title(self):
    with self.assertRaises(ValueError):
        self.manager.create_task('   ', 'alice', datetime(2024, 12, 31))
```

[After]
```python
@pytest.mark.parametrize("invalid_title", [
    "",
    "   ",
])
def test_create_task_rejects_blank_title(manager, mock_db, invalid_title):
    with pytest.raises(ValueError, match="비어있습니다"):
        manager.create_task(invalid_title, "alice", datetime(2024, 12, 31))
```

[Reason] Parametrize -- 동일한 행위(빈 제목 거부)를 검증하는 반복 테스트를 `@pytest.mark.parametrize`로 통합하면 데이터만 다른 케이스를 한 곳에서 관리할 수 있고, 새로운 잘못된 입력 케이스를 추가하기도 쉽다.

---

## 변경 4: time-machine으로 시간 의존성 제거

[Before]
```python
def test_get_overdue_tasks(self):
    self.db.find_all.return_value = [
        {'id': 1, 'title': '과거', 'status': 'open', 'due_date': datetime(2020, 1, 1)},
        {'id': 2, 'title': '미래', 'status': 'open', 'due_date': datetime(2030, 1, 1)},
        ...
    ]
    result = self.manager.get_overdue_tasks()
    self.assertEqual(len(result), 1)
```

[After]
```python
@time_machine.travel("2024-06-15 12:00:00")
def test_get_overdue_tasks(manager, mock_db):
    mock_db.find_all.return_value = [
        {"id": 1, "title": "과거", "status": "open", "due_date": datetime(2020, 1, 1)},
        {"id": 2, "title": "미래", "status": "open", "due_date": datetime(2030, 1, 1)},
        {"id": 3, "title": "완료됨", "status": "completed", "due_date": datetime(2020, 1, 1)},
    ]

    result = manager.get_overdue_tasks()

    assert len(result) == 1
    assert result[0]["title"] == "과거"
```

[Reason] Time Mocking / FIRST-Repeatable -- 원본 테스트는 `datetime.now()`가 2020년 이후이고 2030년 이전이라는 암묵적 가정에 의존한다. time-machine으로 시간을 고정하면 언제 실행하든 동일한 결과를 보장한다.

---

## 변경 5: complete_task 테스트에 시간 고정 적용

[Before]
```python
def test_complete_task(self):
    self.db.find_by_id.return_value = { ... }
    self.db.save.side_effect = lambda t: t
    result = self.manager.complete_task(1)
    self.assertEqual(result['status'], 'completed')
    self.assertIsNotNone(result.get('completed_at'))
```

[After]
```python
@time_machine.travel("2024-06-15 12:00:00")
def test_complete_task(manager, mock_db):
    mock_db.find_by_id.return_value = { ... }
    mock_db.save.side_effect = lambda t: t

    result = manager.complete_task(1)

    assert result["status"] == "completed"
    assert result["completed_at"] == datetime(2024, 6, 15, 12, 0, 0)
```

[Reason] Time Mocking / Weak Assertion -- `assertIsNotNone`는 약한 검증이다(Secret Catcher에 가까움). 시간을 고정하고 정확한 값으로 비교하면 `completed_at`이 실제로 현재 시각으로 설정되는지 확인할 수 있다.

---

## 변경 6: 검증 방식 우선순위 적용 -- 불필요한 통신 기반 검증 제거

[Before]
```python
self.db.save.assert_called_once()
self.notifier.notify.assert_called_once()
```

[After]
```python
assert result["id"] == 1
assert result["title"] == "테스트"
assert result["status"] == "open"
mock_notifier.notify.assert_called_once_with("alice", "새 작업이 할당되었습니다: 테스트")
```

[Reason] Verification Priority -- `db.save`는 내부 구현 세부사항이므로 출력 기반 검증(반환값)으로 충분하다. 반면 `notifier.notify`는 외부 사이드이펙트(알림 발송)이므로 통신 기반 검증이 적절하며, 인자까지 검증하여 올바른 메시지가 전달되는지 확인한다.

---

## 완성된 리팩토링 코드

```python
from __future__ import annotations

from datetime import datetime
from typing import Protocol
from unittest.mock import create_autospec

import pytest
import time_machine


# ---------------------------------------------------------------------------
# Production Code (테스트 대상)
# ---------------------------------------------------------------------------

class TaskManager:
    def __init__(self, db, notifier):
        self.db = db
        self.notifier = notifier

    def create_task(self, title: str, assignee: str, due_date: datetime) -> dict:
        if not title.strip():
            raise ValueError("제목이 비어있습니다")
        task = {
            "id": None,
            "title": title.strip(),
            "assignee": assignee,
            "due_date": due_date,
            "status": "open",
            "created_at": datetime.now(),
        }
        saved = self.db.save(task)
        self.notifier.notify(assignee, f"새 작업이 할당되었습니다: {title}")
        return saved

    def complete_task(self, task_id: int) -> dict:
        task = self.db.find_by_id(task_id)
        if not task:
            raise ValueError(f"작업 {task_id}을 찾을 수 없습니다")
        if task["status"] == "completed":
            raise ValueError("이미 완료된 작업입니다")
        task["status"] = "completed"
        task["completed_at"] = datetime.now()
        return self.db.save(task)

    def get_overdue_tasks(self) -> list[dict]:
        all_tasks = self.db.find_all()
        now = datetime.now()
        return [t for t in all_tasks if t["status"] == "open" and t["due_date"] < now]


# ---------------------------------------------------------------------------
# Protocol definitions (Mock spec으로 사용)
# ---------------------------------------------------------------------------

class DBProtocol(Protocol):
    def save(self, task: dict) -> dict: ...
    def find_by_id(self, task_id: int) -> dict | None: ...
    def find_all(self) -> list[dict]: ...


class NotifierProtocol(Protocol):
    def notify(self, recipient: str, message: str) -> None: ...


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    return create_autospec(DBProtocol, instance=True)


@pytest.fixture
def mock_notifier():
    return create_autospec(NotifierProtocol, instance=True)


@pytest.fixture
def manager(mock_db, mock_notifier):
    return TaskManager(mock_db, mock_notifier)


# ---------------------------------------------------------------------------
# Tests: create_task
# ---------------------------------------------------------------------------

class TestCreateTask:

    def test_returns_saved_task(self, manager, mock_db, mock_notifier):
        mock_db.save.return_value = {
            "id": 1,
            "title": "테스트",
            "assignee": "alice",
            "due_date": datetime(2024, 12, 31),
            "status": "open",
            "created_at": datetime(2024, 1, 1),
        }

        result = manager.create_task("테스트", "alice", datetime(2024, 12, 31))

        assert result["id"] == 1
        assert result["title"] == "테스트"
        assert result["status"] == "open"
        mock_notifier.notify.assert_called_once_with(
            "alice", "새 작업이 할당되었습니다: 테스트"
        )

    def test_strips_whitespace_from_title(self, manager, mock_db):
        mock_db.save.side_effect = lambda t: {**t, "id": 1}

        result = manager.create_task("  공백 제거  ", "bob", datetime(2024, 12, 31))

        assert result["title"] == "공백 제거"

    @pytest.mark.parametrize("invalid_title", [
        "",
        "   ",
    ])
    def test_rejects_blank_title(self, manager, invalid_title):
        with pytest.raises(ValueError, match="비어있습니다"):
            manager.create_task(invalid_title, "alice", datetime(2024, 12, 31))


# ---------------------------------------------------------------------------
# Tests: complete_task
# ---------------------------------------------------------------------------

class TestCompleteTask:

    @time_machine.travel("2024-06-15 12:00:00")
    def test_marks_task_as_completed(self, manager, mock_db):
        mock_db.find_by_id.return_value = {
            "id": 1,
            "title": "완료할 작업",
            "status": "open",
            "due_date": datetime(2024, 12, 31),
        }
        mock_db.save.side_effect = lambda t: t

        result = manager.complete_task(1)

        assert result["status"] == "completed"
        assert result["completed_at"] == datetime(2024, 6, 15, 12, 0, 0)

    def test_raises_on_nonexistent_task(self, manager, mock_db):
        mock_db.find_by_id.return_value = None

        with pytest.raises(ValueError, match="찾을 수 없습니다"):
            manager.complete_task(999)

    def test_raises_on_already_completed_task(self, manager, mock_db):
        mock_db.find_by_id.return_value = {
            "id": 1,
            "title": "이미 완료",
            "status": "completed",
        }

        with pytest.raises(ValueError, match="이미 완료"):
            manager.complete_task(1)


# ---------------------------------------------------------------------------
# Tests: get_overdue_tasks
# ---------------------------------------------------------------------------

class TestGetOverdueTasks:

    @time_machine.travel("2024-06-15 12:00:00")
    def test_returns_only_open_past_due_tasks(self, manager, mock_db):
        mock_db.find_all.return_value = [
            {"id": 1, "title": "과거", "status": "open", "due_date": datetime(2020, 1, 1)},
            {"id": 2, "title": "미래", "status": "open", "due_date": datetime(2030, 1, 1)},
            {"id": 3, "title": "완료됨", "status": "completed", "due_date": datetime(2020, 1, 1)},
        ]

        result = manager.get_overdue_tasks()

        assert len(result) == 1
        assert result[0]["title"] == "과거"
```

---

## 적용된 원칙 요약

| 체크리스트 항목 | 적용 여부 | 설명 |
|---|---|---|
| Multiple Act sections -> SPLIT | 해당 없음 | 원본에 다중 Act 없음 |
| Shared mutable state -> ISOLATE | 적용 | `setUp`의 `self.*` -> pytest fixture로 격리 |
| Over-mocked tests -> REPLACE | 일부 적용 | `db.save.assert_called_once()` 제거, 출력 기반 검증으로 대체 |
| Mock without spec -> ADD spec | 적용 | `MagicMock()` -> `create_autospec(Protocol)` |
| Time-dependent tests -> APPLY time-machine | 적용 | `get_overdue_tasks`, `complete_task`에 `time_machine.travel` 적용 |
| Repetitive test cases -> EXTRACT to parametrize | 적용 | 빈 제목/공백 제목 테스트를 `parametrize`로 통합 |
| Complex setup -> EXTRACT to fixture | 적용 | `setUp` -> 3개의 pytest fixture로 분리 |
| Implementation-coupled assertions -> REWRITE | 적용 | `db.save.assert_called_once()` 제거, `assertIsNotNone` -> 정확한 시간 비교 |
| Empty/weak assertions -> ADD meaningful verification | 적용 | `assertIsNotNone(completed_at)` -> 정확한 datetime 비교 |
| Misplaced test level -> MOVE | 해당 없음 | 테스트 레벨 적절 |
