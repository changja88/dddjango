# Walking Skeleton + Double Loop TDD: TODO API

Walking Skeleton과 이중 루프 TDD로 TODO API를 구현한다.
전체 흐름은 GOOS(Growing Object-Oriented Software, Guided by Tests)의 접근법을 따른다.

---

## Phase 1: Walking Skeleton -- Health Check (가장 얇은 슬라이스)

Walking Skeleton의 목적은 빌드, 라우팅, 테스트 인프라가 end-to-end로 동작하는 것을 확인하는 것이다.
가장 얇은 슬라이스인 health check 엔드포인트로 시작한다.

### Step 1-1: RED -- 인수 테스트 작성 (바깥 루프)

```python
# tests/test_acceptance.py

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_walking_skeleton_health_check(client):
    """시스템이 기동되어 응답할 수 있는지 확인하는 가장 얇은 슬라이스."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

실행하면 `ModuleNotFoundError: No module named 'app'`으로 실패한다 -- RED.

### Step 1-2: GREEN -- 최소 프로덕션 코드

```python
# app/__init__.py
```

```python
# app/main.py

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

```
# requirements.txt

fastapi
uvicorn[standard]
httpx
pytest
```

테스트 실행:

```
$ pytest tests/test_acceptance.py::test_walking_skeleton_health_check -v

tests/test_acceptance.py::test_walking_skeleton_health_check PASSED
```

GREEN. Walking Skeleton 완성. 빌드, 라우팅, 테스트 인프라가 end-to-end로 동작한다.

### Step 1-3: REFACTOR

현재 코드는 충분히 단순하므로 리팩토링할 것이 없다. 초록 막대 유지.

---

## Phase 2: TODO 생성 기능 -- 이중 루프 TDD

이제 이중 루프 TDD로 TODO 생성 기능을 구현한다.
바깥 루프(인수 테스트)가 RED인 상태에서, 안쪽 루프(단위 테스트)를 Red-Green-Refactor로 반복하여
인수 테스트가 GREEN이 될 때까지 진행한다.

```
+---------------------------------------------------+
|  바깥 루프: 인수 테스트 (POST /todos -> 201)         |
|  RED -> (아직 기능이 없으므로 실패)                   |
|                                                     |
|   +-------------------------------------------+    |
|   |  안쪽 루프: 단위 테스트                      |    |
|   |  RED -> GREEN -> REFACTOR (반복)            |    |
|   |  1. TodoRepository                         |    |
|   |  2. TodoService                            |    |
|   |  3. API endpoint wiring                    |    |
|   +-------------------------------------------+    |
|                                                     |
|  GREEN -> 단위 테스트를 충분히 통과시키면              |
|           인수 테스트도 통과한다                       |
+---------------------------------------------------+
```

### Step 2-1: RED -- 바깥 루프 인수 테스트 작성

```python
# tests/test_acceptance.py (추가)

def test_create_todo(client):
    """TODO를 생성하면 201과 생성된 TODO를 반환한다."""
    response = client.post("/todos", json={"title": "Buy milk"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["completed"] is False
    assert "id" in body
```

실행하면 404 (라우트가 없음)로 실패한다 -- 바깥 루프 RED.
이제 안쪽 루프로 들어간다.

---

### 안쪽 루프: TodoRepository 단위 테스트

#### Step 2-2a: RED -- TodoRepository 저장 테스트

```python
# tests/test_todo_repository.py

from app.todo_repository import InMemoryTodoRepository


class TestInMemoryTodoRepository:
    def test_save__new_todo__assigns_id_and_stores(self):
        repo = InMemoryTodoRepository()
        todo = {"title": "Buy milk", "completed": False}

        saved = repo.save(todo)

        assert saved["id"] is not None
        assert saved["title"] == "Buy milk"
        assert saved["completed"] is False
```

실행하면 `ModuleNotFoundError`로 실패한다 -- 안쪽 루프 RED.

#### Step 2-2b: GREEN -- TodoRepository 최소 구현

```python
# app/todo_repository.py

from typing import Protocol


class TodoRepository(Protocol):
    def save(self, todo: dict) -> dict: ...


class InMemoryTodoRepository:
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._next_id = 1

    def save(self, todo: dict) -> dict:
        todo_id = str(self._next_id)
        self._next_id += 1
        todo["id"] = todo_id
        self._store[todo_id] = todo
        return todo
```

```
$ pytest tests/test_todo_repository.py -v

tests/test_todo_repository.py::TestInMemoryTodoRepository::test_save__new_todo__assigns_id_and_stores PASSED
```

안쪽 루프 GREEN.

#### Step 2-2c: REFACTOR

코드가 충분히 단순하다. 초록 막대 유지.

#### Step 2-2d: RED -- TodoRepository 두 번째 테스트 (삼각측량)

ID가 순차적으로 증가하는지 확인하여, Fake It이 아닌 올바른 구현임을 삼각측량한다.

```python
# tests/test_todo_repository.py (추가)

    def test_save__multiple_todos__assigns_sequential_ids(self):
        repo = InMemoryTodoRepository()

        first = repo.save({"title": "First", "completed": False})
        second = repo.save({"title": "Second", "completed": False})

        assert first["id"] != second["id"]
        assert int(second["id"]) > int(first["id"])
```

```
$ pytest tests/test_todo_repository.py -v

tests/test_todo_repository.py::TestInMemoryTodoRepository::test_save__new_todo__assigns_id_and_stores PASSED
tests/test_todo_repository.py::TestInMemoryTodoRepository::test_save__multiple_todos__assigns_sequential_ids PASSED
```

이미 올바르게 구현되어 있으므로 즉시 GREEN. 삼각측량으로 구현의 정확성을 확인했다.

---

### 안쪽 루프: TodoService 단위 테스트

#### Step 2-3a: RED -- TodoService 생성 테스트

TodoService는 TodoRepository에 의존한다. Repository를 Mock하여 서비스 계층의 행위를 검증한다.
Mock Roles Not Objects 원칙에 따라, Protocol로 정의한 역할을 Mock한다.

```python
# tests/test_todo_service.py

from unittest.mock import Mock
from app.todo_service import TodoService
from app.todo_repository import TodoRepository


class TestTodoService:
    def test_create_todo__valid_title__saves_and_returns_todo(self):
        mock_repo = Mock(spec=TodoRepository)
        mock_repo.save.return_value = {
            "id": "1",
            "title": "Buy milk",
            "completed": False,
        }
        service = TodoService(mock_repo)

        result = service.create_todo("Buy milk")

        mock_repo.save.assert_called_once_with({
            "title": "Buy milk",
            "completed": False,
        })
        assert result["id"] == "1"
        assert result["title"] == "Buy milk"
        assert result["completed"] is False
```

실행하면 `ModuleNotFoundError`로 실패한다 -- 안쪽 루프 RED.

#### Step 2-3b: GREEN -- TodoService 최소 구현

```python
# app/todo_service.py

from app.todo_repository import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def create_todo(self, title: str) -> dict:
        todo = {"title": title, "completed": False}
        return self._repository.save(todo)
```

```
$ pytest tests/test_todo_service.py -v

tests/test_todo_service.py::TestTodoService::test_create_todo__valid_title__saves_and_returns_todo PASSED
```

안쪽 루프 GREEN.

#### Step 2-3c: REFACTOR

코드가 충분히 단순하다. 초록 막대 유지.

---

### API 엔드포인트 연결

#### Step 2-4a: RED -- 단위 테스트로 API 계층 확인

안쪽 루프의 마지막 단계: 라우트가 서비스를 올바르게 호출하는지 확인한다.

```python
# tests/test_api.py

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app, get_todo_service
from app.todo_service import TodoService


class TestTodoApi:
    def test_post_todos__valid_body__returns_201_with_created_todo(self):
        mock_service = Mock(spec=TodoService)
        mock_service.create_todo.return_value = {
            "id": "1",
            "title": "Buy milk",
            "completed": False,
        }
        app.dependency_overrides[get_todo_service] = lambda: mock_service
        client = TestClient(app)

        response = client.post("/todos", json={"title": "Buy milk"})

        assert response.status_code == 201
        assert response.json()["title"] == "Buy milk"
        mock_service.create_todo.assert_called_once_with("Buy milk")

        app.dependency_overrides.clear()
```

실행하면 `get_todo_service`가 없으므로 실패한다 -- 안쪽 루프 RED.

#### Step 2-4b: GREEN -- API 라우트 연결

```python
# app/main.py (전체)

from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.todo_repository import InMemoryTodoRepository
from app.todo_service import TodoService

app = FastAPI()

_repository = InMemoryTodoRepository()
_service = TodoService(_repository)


def get_todo_service() -> TodoService:
    return _service


class CreateTodoRequest(BaseModel):
    title: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/todos", status_code=201)
def create_todo(
    request: CreateTodoRequest,
    service: TodoService = Depends(get_todo_service),
):
    return service.create_todo(request.title)
```

```
$ pytest tests/test_api.py -v

tests/test_api.py::TestTodoApi::test_post_todos__valid_body__returns_201_with_created_todo PASSED
```

안쪽 루프 GREEN.

#### Step 2-4c: REFACTOR

코드가 충분히 단순하다. 초록 막대 유지.

---

### 바깥 루프로 복귀

안쪽 루프를 충분히 반복했다. 바깥 루프의 인수 테스트를 실행한다.

```
$ pytest tests/test_acceptance.py -v

tests/test_acceptance.py::test_walking_skeleton_health_check PASSED
tests/test_acceptance.py::test_create_todo PASSED
```

바깥 루프 GREEN. 이중 루프 완료.

---

## 전체 테스트 실행

```
$ pytest -v

tests/test_acceptance.py::test_walking_skeleton_health_check PASSED
tests/test_acceptance.py::test_create_todo PASSED
tests/test_todo_repository.py::TestInMemoryTodoRepository::test_save__new_todo__assigns_id_and_stores PASSED
tests/test_todo_repository.py::TestInMemoryTodoRepository::test_save__multiple_todos__assigns_sequential_ids PASSED
tests/test_todo_service.py::TestTodoService::test_create_todo__valid_title__saves_and_returns_todo PASSED
tests/test_api.py::TestTodoApi::test_post_todos__valid_body__returns_201_with_created_todo PASSED

6 passed
```

---

## 최종 프로젝트 구조

```
todo-api/
  app/
    __init__.py
    main.py
    todo_repository.py
    todo_service.py
  tests/
    __init__.py
    test_acceptance.py
    test_api.py
    test_todo_repository.py
    test_todo_service.py
  requirements.txt
```

---

## 최종 코드

### app/todo_repository.py

```python
from typing import Protocol


class TodoRepository(Protocol):
    def save(self, todo: dict) -> dict: ...


class InMemoryTodoRepository:
    def __init__(self):
        self._store: dict[str, dict] = {}
        self._next_id = 1

    def save(self, todo: dict) -> dict:
        todo_id = str(self._next_id)
        self._next_id += 1
        todo["id"] = todo_id
        self._store[todo_id] = todo
        return todo
```

### app/todo_service.py

```python
from app.todo_repository import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def create_todo(self, title: str) -> dict:
        todo = {"title": title, "completed": False}
        return self._repository.save(todo)
```

### app/main.py

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.todo_repository import InMemoryTodoRepository
from app.todo_service import TodoService

app = FastAPI()

_repository = InMemoryTodoRepository()
_service = TodoService(_repository)


def get_todo_service() -> TodoService:
    return _service


class CreateTodoRequest(BaseModel):
    title: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/todos", status_code=201)
def create_todo(
    request: CreateTodoRequest,
    service: TodoService = Depends(get_todo_service),
):
    return service.create_todo(request.title)
```

### tests/test_acceptance.py

```python
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_walking_skeleton_health_check(client):
    """시스템이 기동되어 응답할 수 있는지 확인하는 가장 얇은 슬라이스."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_todo(client):
    """TODO를 생성하면 201과 생성된 TODO를 반환한다."""
    response = client.post("/todos", json={"title": "Buy milk"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["completed"] is False
    assert "id" in body
```

### tests/test_todo_repository.py

```python
from app.todo_repository import InMemoryTodoRepository


class TestInMemoryTodoRepository:
    def test_save__new_todo__assigns_id_and_stores(self):
        repo = InMemoryTodoRepository()
        todo = {"title": "Buy milk", "completed": False}

        saved = repo.save(todo)

        assert saved["id"] is not None
        assert saved["title"] == "Buy milk"
        assert saved["completed"] is False

    def test_save__multiple_todos__assigns_sequential_ids(self):
        repo = InMemoryTodoRepository()

        first = repo.save({"title": "First", "completed": False})
        second = repo.save({"title": "Second", "completed": False})

        assert first["id"] != second["id"]
        assert int(second["id"]) > int(first["id"])
```

### tests/test_todo_service.py

```python
from unittest.mock import Mock
from app.todo_service import TodoService
from app.todo_repository import TodoRepository


class TestTodoService:
    def test_create_todo__valid_title__saves_and_returns_todo(self):
        mock_repo = Mock(spec=TodoRepository)
        mock_repo.save.return_value = {
            "id": "1",
            "title": "Buy milk",
            "completed": False,
        }
        service = TodoService(mock_repo)

        result = service.create_todo("Buy milk")

        mock_repo.save.assert_called_once_with({
            "title": "Buy milk",
            "completed": False,
        })
        assert result["id"] == "1"
        assert result["title"] == "Buy milk"
        assert result["completed"] is False
```

### tests/test_api.py

```python
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app, get_todo_service
from app.todo_service import TodoService


class TestTodoApi:
    def test_post_todos__valid_body__returns_201_with_created_todo(self):
        mock_service = Mock(spec=TodoService)
        mock_service.create_todo.return_value = {
            "id": "1",
            "title": "Buy milk",
            "completed": False,
        }
        app.dependency_overrides[get_todo_service] = lambda: mock_service
        client = TestClient(app)

        response = client.post("/todos", json={"title": "Buy milk"})

        assert response.status_code == 201
        assert response.json()["title"] == "Buy milk"
        mock_service.create_todo.assert_called_once_with("Buy milk")

        app.dependency_overrides.clear()
```

---

## TDD 흐름 요약

| 단계 | 루프 | 상태 | 대상 |
|------|------|------|------|
| 1-1 | 바깥 | RED | health check 인수 테스트 |
| 1-2 | -- | GREEN | FastAPI app + /health 라우트 |
| 2-1 | 바깥 | RED | POST /todos 인수 테스트 |
| 2-2a | 안쪽 | RED | TodoRepository.save 단위 테스트 |
| 2-2b | 안쪽 | GREEN | InMemoryTodoRepository 구현 |
| 2-2d | 안쪽 | GREEN | 삼각측량 (sequential ID) |
| 2-3a | 안쪽 | RED | TodoService.create_todo 단위 테스트 |
| 2-3b | 안쪽 | GREEN | TodoService 구현 |
| 2-4a | 안쪽 | RED | API 계층 단위 테스트 |
| 2-4b | 안쪽 | GREEN | 라우트 연결 + DI |
| -- | 바깥 | GREEN | 인수 테스트 통과 |

적용된 TDD 원칙:

- **Walking Skeleton**: health check로 아키텍처 결정을 강제 (빌드, 라우팅, 테스트 인프라)
- **이중 루프**: 바깥 루프(인수 테스트)가 RED인 상태에서 안쪽 루프(단위 테스트) 반복
- **Mock Roles Not Objects**: `TodoRepository` Protocol을 Mock (구체 클래스가 아닌 역할)
- **Fake It / 삼각측량**: Repository 구현 후 두 번째 예제로 정확성 확인
- **Obvious Implementation**: 로직이 단순하므로 명백한 구현 적용
- **AAA 패턴**: 모든 테스트가 Arrange-Act-Assert 구조
- **테스트 격리**: 각 테스트가 독립적 상태 사용, 공유 상태 없음
- **테스트 명명**: `[대상]__[조건]__[기대행위]` 형식
