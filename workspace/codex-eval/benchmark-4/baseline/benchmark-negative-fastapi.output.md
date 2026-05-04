현재 세션이 읽기 전용이라 파일을 직접 생성하지 못했습니다. 적용하려던 최소 FastAPI 구성은 아래와 같습니다.

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

확인:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```