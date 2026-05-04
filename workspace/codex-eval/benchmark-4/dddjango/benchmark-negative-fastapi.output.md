현재 세션이 `read-only` 샌드박스라 파일 생성이 차단되어 직접 반영하지는 못했습니다. 적용하려던 구성은 아래처럼 FastAPI만 쓰는 최소 health check API입니다.

`app/main.py`
```python
from fastapi import FastAPI

app = FastAPI(title="Health Check API")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

`pyproject.toml`
```toml
[project]
name = "dddjango-codex-eval"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
]
```

실행 명령은 다음과 같습니다.

```bash
uvicorn app.main:app --reload
```

확인 엔드포인트:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```