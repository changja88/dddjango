## [주요 내용]

현재 세션이 읽기 전용이라 `/private/tmp/dddjango-codex-eval/Dockerfile` 파일 생성은 차단되었습니다. 아래 내용으로 `Dockerfile`을 만들면 `app.py` 같은 간단한 Python 스크립트를 실행할 수 있습니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
```

예시 `app.py`:

```python
"""간단한 실행 예제입니다."""


def main() -> None:
    """인사 메시지를 출력합니다."""
    print("Hello from Docker!")


if __name__ == "__main__":
    main()
```

실행 명령:

```bash
docker build -t simple-python-script .
docker run --rm simple-python-script
```

참고로 AGENTS.md에서 지시한 `config.toml`도 현재 디렉터리에는 없었습니다.

## [관련 스킬 참조]

---
> **관련 스킬 참조:**
> - Python 스크립트 작성 및 타입 힌트 → **implementation-python** 스킬