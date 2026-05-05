현재 작업공간이 읽기 전용이라 파일 생성은 차단되었습니다. 저장소도 비어 있어서, 아래 두 파일만 만들면 FastAPI health check API가 됩니다.

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

확인은 `GET http://127.0.0.1:8000/health`로 하면 `{"status":"ok"}`가 반환됩니다.