파일 생성을 시도했지만 현재 세션이 `read-only`라 쓰기가 차단되었습니다. 또한 `/private/tmp/dddjango-codex-eval`에는 `config.toml`도 없고 디렉터리가 비어 있습니다.

생성하려던 내용은 아래와 같습니다.

`main.py`
```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

`requirements.txt`
```txt
fastapi
uvicorn[standard]
```

실행은 다음처럼 하면 됩니다.

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```