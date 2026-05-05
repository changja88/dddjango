FastAPI 기준 최소 health check API 예시입니다.

```text
.
├── main.py
└── requirements.txt
```

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