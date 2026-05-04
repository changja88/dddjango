현재 작업공간이 `read-only`라서 Dockerfile을 직접 생성할 수는 없습니다. 아래 내용을 `/private/tmp/dddjango-codex-eval/Dockerfile`로 만들면 됩니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY script.py .

CMD ["python", "script.py"]
```

예시 `script.py`:

```python
print("Hello from Docker!")
```

실행:

```bash
docker build -t simple-python-script .
docker run --rm simple-python-script
```