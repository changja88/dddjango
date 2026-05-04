현재 작업공간이 `read-only`라 파일 생성이 차단되어 직접 추가하지는 못했습니다. 프로젝트는 비어 있고 `config.toml`도 없습니다.

추가하면 되는 최소 구성은 아래입니다.

`main.py`
```python
from fastapi import FastAPI

app = FastAPI(title="Health Check API")


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