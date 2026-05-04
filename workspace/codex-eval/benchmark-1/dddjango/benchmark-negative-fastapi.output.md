## [주요 내용]

현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고, 샌드박스가 읽기 전용이라 파일 생성이나 `pytest` 실행은 불가능했습니다. Django는 사용하지 않고 FastAPI만 쓰는 최소 health check API 구성은 아래처럼 만들면 됩니다.

RED 테스트:

```python
# tests/test_health.py
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

예상 실패 이유: 아직 `app.main` 또는 `/health` 엔드포인트가 없어서 `ModuleNotFoundError`, import 실패, 또는 `404 Not Found`가 납니다.

GREEN 구현:

```python
# app/main.py
from enum import StrEnum

from fastapi import FastAPI
from pydantic import BaseModel


class HealthStatus(StrEnum):
    """Service health 상태 값이다."""

    OK = "ok"


class HealthResponse(BaseModel):
    """Health check API 응답이다."""

    status: HealthStatus


app = FastAPI(title="Health Check API")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def get_health() -> HealthResponse:
    """서비스가 요청을 받을 수 있는 상태인지 반환한다."""
    return HealthResponse(status=HealthStatus.OK)
```

패키지 파일:

```python
# app/__init__.py
```

의존성 예시:

```toml
# pyproject.toml
[project]
name = "health-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 88
```

실행 명령:

```bash
uv sync
uv run pytest
uv run uvicorn app.main:app --reload
```

확인:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

REFACTOR 방향은 지금 단계에서는 불필요합니다. 이후 DB, 외부 의존성, readiness/liveness 분리가 필요해지면 `/health`, `/ready`, `/live`처럼 목적별 엔드포인트를 분리하는 정도가 적절합니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - FastAPI 구현 품질 → **implementation-python** 스킬
> - API 경로와 상태 코드 설계 → **architecture-api** 스킬
> - 테스트 우선 구현 → **implementation-tdd** 스킬