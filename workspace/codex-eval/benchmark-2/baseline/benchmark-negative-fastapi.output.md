현재 환경이 `read-only`라 파일 생성이 차단되어 직접 반영하지 못했습니다. 적용하려던 내용은 아래와 같습니다.

`main.py`
```python
from fastapi import FastAPI

app = FastAPI(title="Health Check API")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

`requirements.txt`
```txt
fastapi
uvicorn[standard]
```

실행 명령:
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