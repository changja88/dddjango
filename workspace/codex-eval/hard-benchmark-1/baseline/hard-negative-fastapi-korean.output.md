현재 세션이 `read-only`라 파일은 직접 생성할 수 없지만, 최소 구성은 아래면 됩니다. Django는 사용하지 않습니다.

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