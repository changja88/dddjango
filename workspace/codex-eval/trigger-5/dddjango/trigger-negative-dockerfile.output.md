현재 작업 디렉터리가 읽기 전용이고 `config.toml`도 존재하지 않아 파일을 직접 생성하지는 못했습니다. 아래 내용을 `Dockerfile`로 두면 간단한 `app.py`를 실행할 수 있습니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
```

예시 `app.py`:

```python
print("Hello from Docker!")
```

실행 명령:

```bash
docker build -t simple-python-app .
docker run --rm simple-python-app
```