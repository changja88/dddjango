현재 작업공간이 읽기 전용이라 `Dockerfile`을 직접 생성할 수는 없습니다. 아래 내용으로 `Dockerfile`을 만들면 간단한 `script.py`를 실행합니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY script.py .

CMD ["python", "script.py"]
```

예시 `script.py`:

```python
print("Hello from Docker")
```

실행:

```bash
docker build -t simple-python .
docker run --rm simple-python
```