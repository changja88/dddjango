현재 세션이 `read-only` 샌드박스이고 승인도 비활성화되어 있어서 파일 생성이 차단되었습니다. 레포도 현재 비어 있습니다.

추가하려던 구성은 아래와 같습니다.

```toml
# pyproject.toml
[project]
name = "dddjango-codex-eval"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
]

[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]
```

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Health Check API")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

```python
# tests/test_health.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

실행은 다음처럼 하면 됩니다.

```bash
uvicorn app.main:app --reload
```

Health check는 `GET /health`에서 `{"status":"ok"}`를 반환합니다.