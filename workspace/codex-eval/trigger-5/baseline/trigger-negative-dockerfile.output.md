현재 작업공간이 읽기 전용이라 `Dockerfile`을 직접 생성하지 못했습니다. 추가하려던 내용은 아래와 같습니다.

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY main.py .

CMD ["python", "main.py"]
```

이 Dockerfile은 같은 디렉터리의 `main.py`를 컨테이너 안 `/app`으로 복사한 뒤 실행합니다.  
예시 실행:

```bash
docker build -t simple-python .
docker run --rm simple-python
```