# 데코레이터

Python 데코레이터의 핵심 패턴과 타입 안전한 작성법을 정리한다.

---

## functools.wraps 필수 사용

데코레이터를 적용하면 원래 함수의 메타데이터(이름, 독스트링)가 사라진다.
`@wraps`로 보존하라.

```python
from functools import wraps

# 나쁜 예: 메타데이터 손실
def trace(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper

# 좋은 예: @wraps로 메타데이터 보존
def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper
```

`@wraps`가 보존하는 속성: `__module__`, `__name__`, `__qualname__`, `__annotations__`, `__type_params__` (3.12+), `__doc__`, `__wrapped__`

---

## 데코레이터에 인자 전달

### 방법 1: 3단 중첩 함수

```python
def with_retry(retries_limit=3, allowed_exceptions=None):
    allowed_exceptions = allowed_exceptions or (Exception,)
    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    last_raised = e
            raise last_raised
        return wrapped
    return retry

@with_retry(retries_limit=5)
def run_operation(): ...
```

### 방법 2: 클래스 데코레이터 (가독성 더 좋음)

```python
class Serialization:
    def __init__(self, **transformations):
        self.serializer = EventSerializer(transformations)

    def __call__(self, event_class):
        def serialize_method(event_instance):
            return self.serializer.serialize(event_instance)
        event_class.serialize = serialize_method
        return event_class

@Serialization(username=show_original, password=hide_field)
@dataclass
class LoginEvent: ...
```

---

## @overload를 활용한 bare/parameterised 데코레이터 통합

`@decorator`와 `@decorator(arg=val)` 두 형태를 모두 지원하는 데코레이터를 작성할 때,
`typing.overload`로 타입 안전성을 확보한다.

### 핵심 원리

- 첫 번째 인자가 `Callable`이면 bare 호출 (`@decorator`)
- 첫 번째 인자가 `None`이면 parameterised 호출 (`@decorator(...)`)
- `function` 이후 인자를 keyword-only(`*`)로 강제하여 혼동을 방지한다

### 방법 1: @overload + 함수

```python
from typing import Callable, ParamSpec, TypeVar, overload
from functools import wraps

P = ParamSpec('P')
R = TypeVar('R')

@overload
def retry(func: Callable[P, R]) -> Callable[P, R]:
    """bare: @retry"""
    ...

@overload
def retry(
    func: None = None,
    *,
    retries: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """parameterised: @retry(retries=5)"""
    ...

def retry(
    func: Callable[P, R] | None = None,
    *,
    retries: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None
            for _ in range(retries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
            raise last_exc  # type: ignore[misc]
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator

# 사용법 1: bare
@retry
def fetch_data() -> str: ...

# 사용법 2: parameterised
@retry(retries=5, exceptions=(TimeoutError,))
def fetch_data_with_retry() -> str: ...
```

### 방법 2: 람다 분기 축약 (클린코드 2nd)

```python
def decorator(function=None, *, x=DEFAULT_X, y=DEFAULT_Y):
    if function is None:
        return lambda f: decorator(f, x=x, y=y)

    @wraps(function)
    def wrapped():
        return function(x, y)
    return wrapped
```

`function is None` 일 때 자기 자신을 재귀적으로 호출하여 중복 코드를 제거한다.

---

## 타입 안전한 데코레이터: ParamSpec

```python
from typing import Callable, ParamSpec, TypeVar
from functools import wraps

P = ParamSpec('P')
R = TypeVar('R')

def timer(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# 타입 체커가 greet(name: str, greeting: str) -> str 시그니처를 정확히 인식
```

---

## Concatenate: 매개변수 추가/제거

데코레이터가 원래 함수에 매개변수를 추가하거나 제거할 때 사용한다.

```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

def with_request(
    func: Callable[P, R]
) -> Callable[Concatenate[Request, P], R]:
    def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"User: {request.user}")
        return func(*args, **kwargs)
    return wrapper

@with_request
def get_data(query: str) -> list[str]:
    return [query]

# get_data의 시그니처: (request: Request, query: str) -> list[str]
```

### ParamSpec + Concatenate 고급 패턴

PEP 612에서 정의한 규칙과 실전 활용 패턴을 정리한다.

**규칙:**
- `*args: P.args`와 `**kwargs: P.kwargs`는 반드시 함께 사용해야 한다
- `Concatenate`로 추가할 수 있는 매개변수는 positional-only뿐이다
- `Concatenate`의 마지막 인자는 반드시 `ParamSpec`이어야 한다

**인증 컨텍스트 주입 패턴:**

```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

class AuthContext:
    user_id: str
    permissions: set[str]

def require_auth(
    permission: str,
) -> Callable[
    [Callable[Concatenate[AuthContext, P], R]],
    Callable[P, R],
]:
    """인증 컨텍스트를 소비하고 권한을 검증하는 데코레이터."""
    def decorator(
        func: Callable[Concatenate[AuthContext, P], R],
    ) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ctx = get_current_auth_context()
            if permission not in ctx.permissions:
                raise PermissionError(f"'{permission}' 권한 필요")
            return func(ctx, *args, **kwargs)
        return wrapper
    return decorator

@require_auth("admin:read")
def get_admin_data(ctx: AuthContext, resource_id: str) -> dict:
    return {"user": ctx.user_id, "resource": resource_id}

# 호출자 시그니처: get_admin_data(resource_id: str) -> dict
# ctx는 데코레이터가 자동 주입
```

**매개변수 제거 패턴 (Concatenate의 역방향 활용):**

```python
def inject_db(
    func: Callable[Concatenate[DBSession, P], R],
) -> Callable[P, R]:
    """DBSession을 자동 주입하고 호출자에게서 숨긴다."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with create_session() as session:
            return func(session, *args, **kwargs)
    return wrapper

@inject_db
def create_user(db: DBSession, name: str, email: str) -> User:
    return db.add(User(name=name, email=email))

# 호출자 시그니처: create_user(name: str, email: str) -> User
```

---

## 예외 경로 관측 후 re-raise 패턴

프로덕션 데코레이터에서 메트릭/로깅을 위해 예외를 관측하되, 반드시 re-raise하여
호출자의 예외 처리를 방해하지 않아야 한다.

### 왜 BaseException인가?

- `except Exception`은 `KeyboardInterrupt`, `SystemExit` 등을 놓친다
- 관측(observability) 목적이면 모든 종료 경로를 포착해야 하므로 `BaseException`을 사용한다
- 단, 예외를 삼키면 안 되므로 **반드시 re-raise**한다

### 기본 패턴: try/except/else/finally 구조

```python
import time
import logging
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')
logger = logging.getLogger(__name__)

def observe(func: Callable[P, R]) -> Callable[P, R]:
    """실행 시간과 성공/실패를 관측한다. 예외는 항상 re-raise."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        exc_info: BaseException | None = None
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            exc_info = e
            raise  # 반드시 re-raise
        else:
            return result
        finally:
            elapsed = time.perf_counter() - start
            status = "ERROR" if exc_info else "OK"
            logger.info(
                "%s | %s | %.4fs | %s",
                func.__qualname__,
                status,
                elapsed,
                type(exc_info).__name__ if exc_info else "",
            )
            # 메트릭 전송 (예: Prometheus, Datadog)
            # metrics.histogram("func.duration", elapsed, tags=[...])
    return wrapper
```

### 핵심 규칙

| 규칙 | 설명 |
|------|------|
| `except BaseException` | `KeyboardInterrupt`, `SystemExit` 포함 모든 종료 경로 포착 |
| `raise` (bare) | 원본 traceback 보존. `raise e`는 traceback을 리셋하므로 피한다 |
| `finally` 블록 | 성공/실패 무관하게 메트릭 전송을 보장 |
| `else` 블록 | 정상 경로에서만 `return` 수행 (except 후 코드 실행 방지) |

### 메트릭 통합 패턴 (Prometheus 스타일)

```python
from contextlib import contextmanager

@contextmanager
def _track(name: str):
    """성공/실패/소요시간을 자동 기록하는 컨텍스트 매니저."""
    start = time.perf_counter()
    status = "ok"
    try:
        yield
    except BaseException:
        status = "error"
        raise
    finally:
        elapsed = time.perf_counter() - start
        HISTOGRAM.labels(func=name, status=status).observe(elapsed)
        COUNTER.labels(func=name, status=status).inc()

def observed(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with _track(func.__qualname__):
            return func(*args, **kwargs)
    return wrapper
```

### 안티패턴: 절대 하지 말 것

```python
# BAD: 예외를 삼키고 None 반환 -> 호출자가 실패를 모름
def bad_observe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Error: %s", e)
            return None  # 예외를 삼킴!
    return wrapper

# BAD: raise e -> traceback 리셋
def bad_reraise(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            logger.error(e)
            raise e  # raise (bare) 대신 raise e -> traceback이 여기서 시작
    return wrapper
```

---

## 클래스 데코레이터: 메타클래스 대안

합성 가능한 클래스 확장이 필요하면 메타클래스보다 클래스 데코레이터를 사용하라.

```python
def trace(kclass):
    for key in dir(kclass):
        value = getattr(kclass, key)
        if isinstance(value, trace_types):
            setattr(kclass, key, trace_func(value))
    return kclass

@trace
class TraceDict(dict):
    ...
```

---

## 디스크립터를 활용한 범용 데코레이터

함수와 메서드 모두에서 동작하려면 디스크립터 프로토콜(`__get__`)을 구현한다.

```python
from types import MethodType
from functools import wraps

class inject_db_driver:
    """문자열을 DBDriver 인스턴스로 변환하여 래핑된 함수에 전달."""

    def __init__(self, function) -> None:
        self.function = function
        wraps(self.function)(self)

    def __call__(self, dbstring):
        return self.function(DBDriver(dbstring))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.__class__(MethodType(self.function, instance))

# 함수에도, 메서드에도 동작
@inject_db_driver
def run_query(driver):
    return driver.execute("test")

class DataHandler:
    @inject_db_driver
    def run_query(self, driver):
        return driver.execute(self.__class__.__name__)
```

---

## 데코레이터 부작용 처리

### 부작용은 반드시 래핑 함수 내부에 위치해야 한다

```python
# BAD: 임포트 시점에 start_time이 고정됨
def traced_function_wrong(function):
    logger.info("%s 함수 실행", function)
    start_time = time.time()  # 임포트 시점의 시간!

    @wraps(function)
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        logger.info("실행시간: %.2fs", time.time() - start_time)
        return result
    return wrapped

# GOOD: 매 호출마다 측정
def traced_function(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        logger.info("%s 함수 실행", function.__qualname__)
        start_time = time.time()
        result = function(*args, **kwargs)
        logger.info("실행시간: %.2fs", time.time() - start_time)
        return result
    return wrapped
```

### 의도적 부작용: 레지스트리 패턴

임포트 시점 부작용이 유용한 경우도 있다. 웹 프레임워크의 라우터 등록이 대표적이다.

```python
EVENTS_REGISTRY = {}

def register_event(event_cls):
    """임포트 시점에 이벤트 클래스를 레지스트리에 등록."""
    EVENTS_REGISTRY[event_cls.__name__] = event_cls
    return event_cls

@register_event
class UserLoginEvent(UserEvent):
    """사용자 로그인 이벤트"""
```

---

## 데코레이터 작성 실전 체크리스트

프로덕션 레벨 데코레이터를 작성할 때 확인해야 할 항목이다.

### 필수 항목

| # | 항목 | 설명 |
|---|------|------|
| 1 | `@wraps(func)` | 메타데이터 보존. `__name__`, `__doc__`, `__wrapped__` 등 |
| 2 | `*args: P.args, **kwargs: P.kwargs` | ParamSpec으로 시그니처 타입 안전성 확보 |
| 3 | bare `raise` | re-raise 시 `raise e` 대신 `raise`로 traceback 보존 |
| 4 | docstring | 데코레이터 자체에 사용법과 부작용을 명시 |
| 5 | 반환 타입 일치 | `Callable[P, R] -> Callable[P, R]` 시그니처 유지 |

### 권장 항목

| # | 항목 | 설명 |
|---|------|------|
| 6 | 사용 예시 | docstring에 `Examples:` 섹션 추가 |
| 7 | 단일 책임 | 로깅과 타이밍을 하나에 넣지 말고 분리 |
| 8 | bare/param 통합 | `@deco`와 `@deco(...)` 양쪽 지원 시 `@overload` 사용 |
| 9 | 비동기 호환 | `asyncio.iscoroutinefunction` 검사 후 분기 |
| 10 | 테스트 용이성 | `__wrapped__`로 원본 함수 직접 테스트 가능 확인 |

### 금지 항목

| # | 항목 | 이유 |
|---|------|------|
| 1 | 예외 삼키기 | `except ... : return None` -- 호출자가 실패를 인지 불가 |
| 2 | 래핑 외부 부작용 | 임포트 시점에 의도치 않은 코드 실행 |
| 3 | 과도한 중첩 | 4단 이상 중첩 시 클래스 데코레이터로 전환 |
| 4 | 가변 기본값 | `allowed_exceptions=[]` 같은 mutable default 사용 금지 |

### 프로덕션 데코레이터 완성 예시

```python
import time
import logging
from functools import wraps
from typing import Callable, ParamSpec, TypeVar, overload

P = ParamSpec('P')
R = TypeVar('R')
logger = logging.getLogger(__name__)

@overload
def timed(func: Callable[P, R]) -> Callable[P, R]: ...
@overload
def timed(
    func: None = None,
    *,
    name: str | None = None,
    log_level: int = logging.DEBUG,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def timed(
    func: Callable[P, R] | None = None,
    *,
    name: str | None = None,
    log_level: int = logging.DEBUG,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """함수 실행 시간을 측정하여 로깅한다.

    bare 형태와 parameterised 형태 모두 지원한다.

    Examples:
        @timed
        def fast(): ...

        @timed(name="slow-op", log_level=logging.WARNING)
        def slow(): ...
    """
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        label = name or fn.__qualname__

        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            exc_info: BaseException | None = None
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                exc_info = e
                raise
            else:
                return result
            finally:
                elapsed = time.perf_counter() - start
                status = "ERROR" if exc_info else "OK"
                logger.log(
                    log_level,
                    "[%s] %s | %.4fs",
                    status, label, elapsed,
                )
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
```

---

## 데코레이터 설계 원칙 요약

1. **관심사 분리** -- 로깅/타이밍/인증을 하나의 데코레이터에 모두 넣지 않는다
2. **상속보다 컴포지션** -- 메타클래스 대신 클래스 데코레이터, 믹스인 대신 함수 데코레이터
3. **3회 규칙** -- 3번 이상 반복될 때만 데코레이터로 추출한다 (GLASS 01)
4. **최소 코드** -- 데코레이터 내부 로직을 최소화하고, 복잡한 로직은 별도 함수로 분리한다
5. **블랙박스 원칙** -- 클라이언트는 데코레이터 내부 구현을 알 필요 없어야 한다

### 참고 자료

- [PEP 318](https://peps.python.org/pep-0318/) -- 함수/메서드 데코레이터
- [PEP 3129](https://peps.python.org/pep-3129/) -- 클래스 데코레이터
- [PEP 612](https://peps.python.org/pep-0612/) -- ParamSpec (Parameter Specification Variables)
- [PEP 614](https://peps.python.org/pep-0614/) -- 데코레이터 확장 문법 (Relaxing Grammar Restrictions)
- [typing.overload 공식 문서](https://typing.python.org/en/latest/spec/overload.html)
- [functools.wraps 공식 문서](https://docs.python.org/3/library/functools.html#functools.wraps)
- [Atlassian @observe 패턴](https://github.com/atlassian-labs/observe)
