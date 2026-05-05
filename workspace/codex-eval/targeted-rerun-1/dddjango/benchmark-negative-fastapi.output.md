현재 세션이 읽기 전용이라 파일은 직접 생성되지 않았습니다. 아래처럼 만들면 FastAPI health check API가 동작합니다.

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

실행:

```bash
pip install -r requirements.txt
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