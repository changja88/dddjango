# Walking Skeleton + Double Loop TDD: TODO API 구현

## 프로젝트 구조

```
todo-api/
├── src/
│   ├── __init__.py
│   ├── app.py              # Flask 앱 팩토리
│   ├── todo_service.py     # 비즈니스 로직
│   └── todo_repository.py  # 인메모리 저장소
├── tests/
│   ├── __init__.py
│   ├── acceptance/
│   │   ├── __init__.py
│   │   ├── test_health_check.py
│   │   └── test_create_todo.py
│   └── unit/
│       ├── __init__.py
│       ├── test_todo_service.py
│       └── test_todo_repository.py
└── requirements.txt
```

---

## Phase 1: Walking Skeleton (Health Check)

> 목표: 가장 얇은 수직 슬라이스로 전체 아키텍처가 동작함을 증명한다.
> 빌드 -> 테스트 -> 배포(로컬) 파이프라인이 끝까지 관통하는 최소 기능.

### Step 1-1: Acceptance Test 작성 (RED)

가장 먼저 "시스템이 살아있는가?"를 검증하는 인수 테스트를 작성한다.

**`tests/acceptance/test_health_check.py`**

```python
"""
Walking Skeleton - Health Check 인수 테스트.
시스템의 가장 얇은 수직 슬라이스: GET /health -> 200 OK.
이 테스트가 통과하면 앱 팩토리, 라우팅, HTTP 레이어가 모두 연결된 것이다.
"""
import pytest
from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    def test_health_endpoint_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_status_ok(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "ok"
```

실행 결과: **RED** -- `src.app` 모듈이 존재하지 않으므로 ImportError.

```
E   ModuleNotFoundError: No module named 'src.app'
```

### Step 1-2: 최소 프로덕션 코드 작성 (GREEN)

Walking Skeleton을 세우기 위한 최소한의 코드만 작성한다.

**`src/__init__.py`**

```python
```

**`src/app.py`**

```python
"""
Flask 앱 팩토리.
Walking Skeleton의 뼈대 -- 모든 HTTP 요청이 여기를 통과한다.
"""
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    return app
```

실행 결과: **GREEN**

```
tests/acceptance/test_health_check.py::TestHealthCheck::test_health_endpoint_returns_200 PASSED
tests/acceptance/test_health_check.py::TestHealthCheck::test_health_endpoint_returns_status_ok PASSED
```

### Step 1-3: Walking Skeleton 완성 확인

이 시점에서 확보한 것:
- Flask 앱 팩토리 (`create_app`)
- HTTP 라우팅 동작
- JSON 응답 직렬화
- 테스트 클라이언트를 통한 인수 테스트 인프라

**Walking Skeleton이 서 있다.** 이제 이 뼈대 위에 살을 붙인다.

---

## Phase 2: TODO 생성 -- Double Loop TDD

> 이중 루프 TDD:
> - **바깥 루프 (Acceptance)**: 사용자 관점의 인수 테스트. 기능 완성까지 RED 상태.
> - **안쪽 루프 (Unit)**: 내부 컴포넌트를 하나씩 RED -> GREEN -> REFACTOR.
> - 안쪽 루프가 충분히 돌면 바깥 루프가 GREEN이 된다.

```
바깥 루프:  RED ─────────────────────────────────────────────> GREEN
            │                                                    ^
            v                                                    │
안쪽 루프:  RED -> GREEN -> REFACTOR -> RED -> GREEN -> REFACTOR ┘
            (Repository)                (Service)
```

### Step 2-1: 바깥 루프 -- Acceptance Test 작성 (RED)

사용자 시나리오: "TODO를 POST하면 201과 함께 생성된 TODO가 반환된다."

**`tests/acceptance/test_create_todo.py`**

```python
"""
바깥 루프 인수 테스트: TODO 생성.
POST /todos 로 TODO를 생성하고, 201 응답과 생성된 데이터를 검증한다.
이 테스트는 안쪽 루프(unit tests)가 모두 통과해야 GREEN이 된다.
"""
import pytest
from src.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestCreateTodo:
    def test_create_todo_returns_201(self, client):
        """POST /todos -> 201 Created"""
        response = client.post(
            "/todos",
            json={"title": "Buy milk"},
        )
        assert response.status_code == 201

    def test_create_todo_returns_created_todo(self, client):
        """응답 본문에 id, title, completed 필드가 포함된다."""
        response = client.post(
            "/todos",
            json={"title": "Buy milk"},
        )
        data = response.get_json()
        assert data["title"] == "Buy milk"
        assert data["completed"] is False
        assert "id" in data

    def test_create_todo_without_title_returns_400(self, client):
        """title 없이 요청하면 400 Bad Request."""
        response = client.post(
            "/todos",
            json={},
        )
        assert response.status_code == 400
```

실행 결과: **RED** -- `/todos` 라우트가 없으므로 404.

```
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_201 FAILED
    assert 404 == 201
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_created_todo FAILED
    assert 404 == 201  (implicit -- get_json() returns None)
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_without_title_returns_400 FAILED
    assert 404 == 400
```

**바깥 루프는 RED 상태. 이제 안쪽 루프로 들어간다.**

---

### Step 2-2: 안쪽 루프 (1) -- TodoRepository 단위 테스트 (RED)

가장 안쪽부터 시작한다. 저장소가 TODO를 저장하고 ID를 부여하는지 검증.

**`tests/unit/test_todo_repository.py`**

```python
"""
안쪽 루프 단위 테스트: TodoRepository.
인메모리 저장소가 TODO를 올바르게 저장하고 ID를 부여하는지 검증한다.
"""
from src.todo_repository import TodoRepository


class TestTodoRepository:
    def test_save_returns_todo_with_id(self):
        """저장하면 ID가 부여된 TODO dict를 반환한다."""
        repo = TodoRepository()
        todo = repo.save({"title": "Buy milk", "completed": False})

        assert "id" in todo
        assert todo["title"] == "Buy milk"
        assert todo["completed"] is False

    def test_save_assigns_incremental_ids(self):
        """ID는 1부터 순차 증가한다."""
        repo = TodoRepository()
        todo1 = repo.save({"title": "First", "completed": False})
        todo2 = repo.save({"title": "Second", "completed": False})

        assert todo1["id"] == 1
        assert todo2["id"] == 2

    def test_save_does_not_mutate_original(self):
        """원본 dict를 변경하지 않는다."""
        repo = TodoRepository()
        original = {"title": "Buy milk", "completed": False}
        repo.save(original)

        assert "id" not in original
```

실행 결과: **RED** -- `src.todo_repository` 모듈 없음.

```
E   ModuleNotFoundError: No module named 'src.todo_repository'
```

### Step 2-3: 안쪽 루프 (1) -- TodoRepository 구현 (GREEN)

**`src/todo_repository.py`**

```python
"""
인메모리 TODO 저장소.
프로덕션에서는 DB로 교체하지만, 지금은 dict로 충분하다.
"""


class TodoRepository:
    def __init__(self):
        self._store: dict[int, dict] = {}
        self._next_id: int = 1

    def save(self, todo_data: dict) -> dict:
        """TODO를 저장하고 ID가 부여된 새 dict를 반환한다."""
        todo = {**todo_data, "id": self._next_id}
        self._store[self._next_id] = todo
        self._next_id += 1
        return todo
```

실행 결과: **GREEN**

```
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_returns_todo_with_id PASSED
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_assigns_incremental_ids PASSED
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_does_not_mutate_original PASSED
```

### Step 2-4: 안쪽 루프 (1) -- REFACTOR

현재 코드가 충분히 단순하므로 리팩토링 없이 다음으로 넘어간다.

---

### Step 2-5: 안쪽 루프 (2) -- TodoService 단위 테스트 (RED)

서비스 레이어는 검증 로직을 담당한다. Repository를 모킹하여 격리 테스트.

**`tests/unit/test_todo_service.py`**

```python
"""
안쪽 루프 단위 테스트: TodoService.
비즈니스 로직(검증, 기본값 설정)을 검증한다.
Repository는 모킹하여 서비스 로직만 격리 테스트한다.
"""
from unittest.mock import MagicMock
from src.todo_service import TodoService


class TestTodoServiceCreate:
    def setup_method(self):
        self.mock_repo = MagicMock()
        self.mock_repo.save.return_value = {
            "id": 1,
            "title": "Buy milk",
            "completed": False,
        }
        self.service = TodoService(self.mock_repo)

    def test_create_todo_calls_repository_save(self):
        """서비스는 repository.save()를 호출한다."""
        self.service.create_todo("Buy milk")
        self.mock_repo.save.assert_called_once_with(
            {"title": "Buy milk", "completed": False}
        )

    def test_create_todo_returns_saved_todo(self):
        """repository가 반환한 TODO를 그대로 반환한다."""
        result = self.service.create_todo("Buy milk")
        assert result == {
            "id": 1,
            "title": "Buy milk",
            "completed": False,
        }

    def test_create_todo_sets_completed_to_false(self):
        """새 TODO의 completed는 항상 False."""
        self.service.create_todo("Buy milk")
        call_args = self.mock_repo.save.call_args[0][0]
        assert call_args["completed"] is False

    def test_create_todo_without_title_raises_error(self):
        """title이 비어있으면 ValueError."""
        import pytest

        with pytest.raises(ValueError, match="title is required"):
            self.service.create_todo("")

    def test_create_todo_with_none_title_raises_error(self):
        """title이 None이면 ValueError."""
        import pytest

        with pytest.raises(ValueError, match="title is required"):
            self.service.create_todo(None)
```

실행 결과: **RED** -- `src.todo_service` 모듈 없음.

```
E   ModuleNotFoundError: No module named 'src.todo_service'
```

### Step 2-6: 안쪽 루프 (2) -- TodoService 구현 (GREEN)

**`src/todo_service.py`**

```python
"""
TODO 비즈니스 로직.
검증과 기본값 설정을 담당한다. 저장은 Repository에 위임.
"""
from src.todo_repository import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def create_todo(self, title: str | None) -> dict:
        """TODO를 생성한다. title이 없으면 ValueError."""
        if not title:
            raise ValueError("title is required")

        todo_data = {"title": title, "completed": False}
        return self._repository.save(todo_data)
```

실행 결과: **GREEN**

```
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_calls_repository_save PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_returns_saved_todo PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_sets_completed_to_false PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_without_title_raises_error PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_with_none_title_raises_error PASSED
```

### Step 2-7: 안쪽 루프 (2) -- REFACTOR

서비스 코드도 충분히 단순하다. 넘어간다.

---

### Step 2-8: 바깥 루프 -- 앱에 라우트 연결 (GREEN)

안쪽 루프가 모두 GREEN이다. 이제 컴포넌트를 조립하여 바깥 루프를 GREEN으로 만든다.

**`src/app.py`** (최종)

```python
"""
Flask 앱 팩토리.
Walking Skeleton의 뼈대에 TODO 생성 기능을 연결한다.
"""
from flask import Flask, jsonify, request
from src.todo_repository import TodoRepository
from src.todo_service import TodoService


def create_app():
    app = Flask(__name__)

    # 의존성 조립
    repository = TodoRepository()
    service = TodoService(repository)

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.route("/todos", methods=["POST"])
    def create_todo():
        body = request.get_json(silent=True) or {}
        title = body.get("title")

        try:
            todo = service.create_todo(title)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify(todo), 201

    return app
```

실행 결과: **GREEN** -- 바깥 루프 통과!

```
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_201 PASSED
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_created_todo PASSED
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_without_title_returns_400 PASSED
```

---

## 전체 테스트 실행 결과

```
============================= test session starts ==============================
tests/acceptance/test_health_check.py::TestHealthCheck::test_health_endpoint_returns_200 PASSED
tests/acceptance/test_health_check.py::TestHealthCheck::test_health_endpoint_returns_status_ok PASSED
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_201 PASSED
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_returns_created_todo PASSED
tests/acceptance/test_create_todo.py::TestCreateTodo::test_create_todo_without_title_returns_400 PASSED
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_returns_todo_with_id PASSED
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_assigns_incremental_ids PASSED
tests/unit/test_todo_repository.py::TestTodoRepository::test_save_does_not_mutate_original PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_calls_repository_save PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_returns_saved_todo PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_sets_completed_to_false PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_without_title_raises_error PASSED
tests/unit/test_todo_service.py::TestTodoServiceCreate::test_create_todo_with_none_title_raises_error PASSED
============================== 13 passed =======================================
```

---

## TDD 흐름 요약

| 단계 | 루프 | 상태 | 행위 |
|------|------|------|------|
| 1-1 | Walking Skeleton | RED | Health check 인수 테스트 작성 |
| 1-2 | Walking Skeleton | GREEN | `create_app` + `/health` 라우트 구현 |
| 2-1 | 바깥 루프 | RED | `POST /todos -> 201` 인수 테스트 작성 |
| 2-2 | 안쪽 루프 (Repository) | RED | `TodoRepository` 단위 테스트 작성 |
| 2-3 | 안쪽 루프 (Repository) | GREEN | 인메모리 `TodoRepository` 구현 |
| 2-4 | 안쪽 루프 (Repository) | REFACTOR | (불필요 -- skip) |
| 2-5 | 안쪽 루프 (Service) | RED | `TodoService` 단위 테스트 작성 (mock repo) |
| 2-6 | 안쪽 루프 (Service) | GREEN | `TodoService` 구현 |
| 2-7 | 안쪽 루프 (Service) | REFACTOR | (불필요 -- skip) |
| 2-8 | 바깥 루프 | GREEN | `app.py`에서 조립 -> 인수 테스트 통과 |

## 핵심 설계 결정

1. **앱 팩토리 패턴**: `create_app()`으로 매 테스트마다 독립된 앱 인스턴스 생성. 테스트 격리 보장.
2. **의존성 주입**: `TodoService`는 생성자로 `TodoRepository`를 받는다. 단위 테스트에서 mock 주입 가능.
3. **인메모리 저장소**: `dict` 기반. DB 교체 시 `TodoRepository` 인터페이스만 맞추면 된다.
4. **검증은 서비스에서**: HTTP 레이어는 서비스의 `ValueError`를 400으로 변환할 뿐, 검증 로직 자체는 서비스가 소유.
