# 미들웨어

## 미들웨어 실행 순서 [DDoc]

```
요청 -> SecurityMiddleware -> SessionMiddleware -> CommonMiddleware
     -> CsrfViewMiddleware -> AuthenticationMiddleware -> MessageMiddleware
     -> XFrameOptionsMiddleware -> 뷰
응답 <- (역순)
```

- 요청은 `MIDDLEWARE` 리스트의 **위에서 아래**로, 응답은 **아래에서 위로** 흐른다.
- `SecurityMiddleware`는 반드시 첫 번째, `SessionMiddleware`는 `AuthenticationMiddleware` 앞에 위치한다.

## 커스텀 미들웨어 작성 [DDoc]

```python
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    """각 요청의 처리 시간을 로깅하는 미들웨어."""

    def __init__(self, get_response):
        self.get_response = get_response
        # 서버 시작 시 한 번만 실행

    def __call__(self, request):
        # 요청 처리 전 (process_request에 해당)
        start_time = time.monotonic()

        response = self.get_response(request)

        # 응답 처리 후 (process_response에 해당)
        duration = time.monotonic() - start_time
        logger.info(
            "method=%s path=%s status=%s duration=%.3fs",
            request.method,
            request.path,
            response.status_code,
            duration,
        )
        return response

    def process_exception(self, request, exception):
        """뷰에서 예외 발생 시 호출."""
        logger.exception("Unhandled exception in %s", request.path)
        return None  # None 반환 시 기본 예외 처리 계속
```

- 미들웨어는 **모든 요청**에 실행되므로 가볍게 유지한다.
- 하나의 미들웨어는 하나의 관심사만 담당한다.
- `get_response` 호출 전 코드는 요청 경로, 호출 후 코드는 응답 경로에서 실행된다.
