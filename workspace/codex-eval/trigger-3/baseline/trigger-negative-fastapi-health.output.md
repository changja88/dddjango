작업 디렉터리 `/private/tmp/dddjango-codex-eval`가 비어 있고, 참조된 `config.toml`도 없습니다. 현재 세션은 `read-only`라 파일을 생성할 수 없어서 직접 추가는 못 했습니다.

FastAPI health check만 필요하면 아래처럼 구성하면 됩니다.

`main.py`
```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

`requirements.txt`
```txt
fastapi
uvicorn
```

실행:
```bash
uvicorn main:app --reload
```

확인:
```bash
curl http://127.0.0.1:8000/health
```

응답:
```json
{"status":"ok"}
```