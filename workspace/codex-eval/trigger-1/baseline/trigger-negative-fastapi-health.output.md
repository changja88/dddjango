현재 세션이 `read-only`라 파일 생성은 차단됐습니다. 적용하려던 최소 구성은 아래와 같습니다.

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

실행은 프로젝트 루트에서:

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