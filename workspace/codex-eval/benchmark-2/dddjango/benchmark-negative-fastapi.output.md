현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, 지시된 `config.toml`도 없습니다. 또한 이 세션의 파일시스템이 `read-only`라서 `main.py`, `requirements.txt`, 테스트 파일 등을 실제로 생성할 수 없습니다.

제가 만들 설계는 다음처럼 아주 단순하게 잡겠습니다.

1. Django는 전혀 사용하지 않음
2. FastAPI 앱 하나 생성
3. `GET /health`가 `200 OK`와 JSON 응답 반환
4. 테스트는 `TestClient`로 먼저 작성
5. 최소 파일 구성:
   - `main.py`
   - `requirements.txt`
   - `tests/test_health.py`

예상 구현 형태는 이렇습니다.

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

```python
# tests/test_health.py
from fastapi.testclient import TestClient

from main import app


def test_health_check_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

```txt
# requirements.txt
fastapi
uvicorn
pytest
httpx
```

쓰기 가능한 워크스페이스로 다시 실행되면, 위 구조로 테스트부터 추가하고 실패 확인 후 FastAPI 구현까지 바로 적용하겠습니다.