현재 작업 디렉터리가 읽기 전용이고 `config.toml`도 존재하지 않아 파일을 직접 생성할 수는 없습니다. 아래 내용을 `/private/tmp/dddjango-codex-eval/Dockerfile`로 만들면 됩니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY script.py .

CMD ["python", "script.py"]
```

예시 실행:

```bash
docker build -t simple-python-script .
docker run --rm simple-python-script
```

`script.py`가 다른 이름이면 `COPY`와 `CMD`의 파일명을 맞춰 바꾸면 됩니다.