# 동시성과 병렬성

Python의 동시성 모델과 최신 병렬 실행 기법을 정리한다.

---

## GIL과 스레드 선택 기준

- **GIL**: CPython에서 한 번에 하나의 스레드만 바이트코드 실행
- **스레드 사용**: 블로킹 I/O 시 (파일, 네트워크). GIL은 시스템 콜 전에 해제됨
- **CPU 병렬화**: `multiprocessing`이나 C 확장 사용.
  Free-threaded 빌드(3.13+)에서는 스레드도 가능

```python
# 블로킹 I/O -> 스레드 OK
from threading import Thread
threads = [Thread(target=slow_io_call) for _ in range(5)]
for t in threads: t.start()

# 스레드 간 데이터 경합 -> Lock 필수
from threading import Lock
class LockingCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0
    def increment(self, offset):
        with self.lock:
            self.count += offset
```

---

## 구조적 동시성 (Structured Concurrency) 원칙

구조적 동시성은 Nathaniel J. Smith의 "Notes on structured concurrency, or: Go statement considered harmful" (2018)에서 체계화된 개념으로, Python 3.11의 `asyncio.TaskGroup`으로 표준 라이브러리에 반영되었다.

### 핵심 원칙

1. **생명주기 바운딩**: 모든 동시 실행 경로는 명확한 진입점과 종료점을 가져야 한다.
   스코프를 벗어나기 전에 모든 비동기 작업이 완료되어야 한다
2. **투명한 소유권**: 태스크를 생성한 코드 블록이 해당 태스크의 생명주기를 책임진다.
   "fire-and-forget" 태스크는 허용하지 않는다
3. **예외 전파 보장**: 하위 태스크의 예외가 절대 조용히 삼켜지지 않고 상위로 전파된다
4. **취소 전파**: 부모가 취소되면 자식도 취소된다. 자식이 실패하면 형제도 취소된다

### 비구조적 vs 구조적 동시성

```python
# 나쁜 예: 비구조적 -- fire-and-forget 태스크
async def bad_unstructured():
    task = asyncio.create_task(background_work())  # 소유권 불명확
    await do_something()
    # task가 아직 실행 중일 수 있음 -- 예외가 삼켜질 수 있음

# 좋은 예: 구조적 -- TaskGroup으로 생명주기 관리
async def good_structured():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(background_work())
        await do_something()
    # 여기 도달 시 모든 태스크 완료 보장
    # 예외 발생 시 ExceptionGroup으로 전파
```

### CancelledError 삼킴 금지 (안티패턴)

`asyncio.TaskGroup`과 `asyncio.timeout()`은 내부적으로 취소(cancellation)를 사용하여 구조적 동시성을 구현한다. `CancelledError`를 삼키면 이 메커니즘이 깨진다.

```python
# 나쁜 예: CancelledError를 삼킴
async def bad_coroutine():
    try:
        await some_operation()
    except asyncio.CancelledError:
        pass  # 삼킴 -- TaskGroup/timeout이 오작동할 수 있음

# 좋은 예: CancelledError를 정리 후 재전파
async def good_coroutine():
    try:
        await some_operation()
    except asyncio.CancelledError:
        await cleanup()  # 정리 작업
        raise            # 반드시 재전파

# 불가피하게 억제해야 하는 경우: uncancel() 호출 필수
async def suppress_cancel_carefully():
    try:
        await some_operation()
    except asyncio.CancelledError:
        task = asyncio.current_task()
        task.uncancel()  # 취소 상태를 명시적으로 해제
```

---

## asyncio.TaskGroup: 구조적 동시성 (3.11+)

```python
import asyncio

# 나쁜 예: asyncio.gather에서 첫 번째 에러만 표면화
async def old_style():
    results = await asyncio.gather(
        fetch_user(),
        fetch_orders(),
        return_exceptions=True  # 예외가 결과에 섞임
    )

# 좋은 예: TaskGroup으로 구조적 동시성
async def new_style():
    async with asyncio.TaskGroup() as tg:
        user_task = tg.create_task(fetch_user())
        orders_task = tg.create_task(fetch_orders())
    # 모든 태스크 완료 후 여기에 도달
    # 예외 발생 시 ExceptionGroup으로 묶여서 전파
    return user_task.result(), orders_task.result()
```

---

## TaskGroup 결과 수집 패턴

### 좋은 예: task.result()로 결과 수집

`async with` 블록이 끝난 후 `task.result()`를 호출하는 것이 정석이다. 블록 종료 시점에 모든 태스크의 완료가 보장되므로 안전하다.

```python
# 좋은 예 1: 개별 변수에 할당
async def fetch_user_data(user_id: int):
    async with asyncio.TaskGroup() as tg:
        profile_task = tg.create_task(fetch_profile(user_id))
        orders_task = tg.create_task(fetch_orders(user_id))
        prefs_task = tg.create_task(fetch_preferences(user_id))
    # async with 종료 -> 모든 태스크 완료 보장
    return {
        "profile": profile_task.result(),
        "orders": orders_task.result(),
        "preferences": prefs_task.result(),
    }

# 좋은 예 2: 리스트로 동적 수집
async def fetch_all_urls(urls: list[str]):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_url(url)) for url in urls]
    # 입력 순서와 동일한 순서로 결과 반환
    return [task.result() for task in tasks]
```

### 나쁜 예: 공유 변수 mutation

공유 리스트에 결과를 append하면 순서가 보장되지 않고, 의도를 파악하기 어렵다.

```python
# 나쁜 예: 공유 변수 mutation
async def bad_fetch_all(urls: list[str]):
    results = []  # 공유 가변 상태

    async def _fetch_and_append(url: str):
        data = await fetch_url(url)
        results.append(data)  # 완료 순서에 따라 결과 순서가 달라짐

    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(_fetch_and_append(url))
    return results  # 순서 비결정적, 디버깅 어려움
```

### 결과 순서 보장

- `task.result()` 패턴: `tasks` 리스트의 인덱스가 곧 입력 순서이므로 **순서 보장**
- 공유 변수 mutation 패턴: 태스크 완료 순서에 의존하므로 **순서 비결정적**
- `asyncio.gather()`: 입력 코루틴 순서대로 결과 반환 (순서 보장, 그러나 다른 문제 있음)

---

## ExceptionGroup 처리: except* 필수 패턴 (3.11+)

### 기본: 다중 except* 절

각 `except*` 절은 ExceptionGroup 내에서 해당 타입에 매칭되는 예외만 추출하여 처리한다. 하나의 리프 예외는 최대 하나의 `except*` 절에서만 처리된다. 여러 `except*` 절이 각각 독립적으로 실행될 수 있다.

```python
# 좋은 예: 예외 유형별 분기 처리
async def handle_errors():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(might_fail_with_value_error())
            tg.create_task(might_fail_with_os_error())
            tg.create_task(might_fail_with_timeout())
    except* ValueError as eg:
        # eg.exceptions: 매칭된 ValueError들의 튜플
        for exc in eg.exceptions:
            logger.warning(f"입력값 에러: {exc}")
    except* OSError as eg:
        for exc in eg.exceptions:
            logger.error(f"OS 에러: {exc}")
    except* TimeoutError as eg:
        for exc in eg.exceptions:
            logger.error(f"타임아웃: {exc}")
    # 위 절에서 처리되지 않은 예외는 자동으로 재전파됨
```

### 나쁜 예: 광범위한 예외 잡기

```python
# 나쁜 예: except*에서 Exception을 잡으면 모든 예외를 삼킴
async def bad_handle_errors():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task_a())
            tg.create_task(task_b())
    except* Exception as eg:  # 너무 광범위 -- 모든 예외를 삼킴
        print("에러 발생")     # 어떤 에러인지 구분 불가
```

### except* 절의 제약사항 (PEP 654)

`except*` 블록 내에서 **`break`, `continue`, `return` 사용 불가** (SyntaxError). ExceptionGroup 내의 예외들은 독립적이므로, 하나의 예외가 다른 예외의 처리 흐름에 영향을 주면 안 된다는 원칙이다.

```python
# 컴파일 에러: except* 내에서 return 불가
async def invalid_pattern():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(work())
    except* ValueError:
        return None  # SyntaxError!
```

### except* 실전 패턴: HTTP 요청 에러 분류

```python
import httpx

async def fetch_many(urls: list[str]):
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(httpx.AsyncClient().get(url)) for url in urls]
    except* httpx.HTTPStatusError as eg:
        for exc in eg.exceptions:
            logger.error(f"HTTP {exc.response.status_code}: {exc.request.url}")
    except* httpx.ConnectError as eg:
        for exc in eg.exceptions:
            logger.error(f"연결 실패: {exc}")
    except* httpx.TimeoutException as eg:
        for exc in eg.exceptions:
            logger.warning(f"타임아웃: {exc}")
    else:
        return [t.result() for t in tasks]
```

### ExceptionGroup의 split()과 subgroup()

프로그래밍적으로 ExceptionGroup을 분리해야 할 때 사용한다.

```python
# split(): 매칭/비매칭 그룹으로 분할 (재시도 vs 실패 결정 시)
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(work_a())
        tg.create_task(work_b())
except* Exception as eg:
    retryable, fatal = eg.split(lambda e: isinstance(e, TimeoutError))
    if retryable:
        # TimeoutError만 재시도
        pass
    if fatal:
        raise fatal  # 나머지는 재전파

# subgroup(): 매칭 그룹만 추출 (로깅/검사 시)
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(work())
except* Exception as eg:
    warnings = eg.subgroup(lambda e: isinstance(e, UserWarning))
    if warnings:
        for w in warnings.exceptions:
            logger.info(f"경고: {w}")
    raise  # 전체 ExceptionGroup 재전파
```

---

## gather -> TaskGroup 마이그레이션: Semantic Change 경고

`asyncio.gather()`에서 `asyncio.TaskGroup`으로 전환 시 **동작이 근본적으로 다르다**. 단순 치환이 아님을 반드시 인지해야 한다.

### 핵심 차이: Partial Success vs Fail-Fast

| 동작 | `gather(return_exceptions=True)` | `TaskGroup` |
|------|----------------------------------|-------------|
| 태스크 하나 실패 시 | 나머지 태스크 **계속 실행** | 나머지 태스크 **즉시 취소** |
| 예외 처리 | 결과 리스트에 예외 섞임 | `ExceptionGroup`으로 전파 |
| 부분 성공 | 가능 (성공 결과 + 예외 혼재) | 불가 (하나 실패 = 전체 취소) |
| 결과 접근 | 리스트 인덱스로 직접 접근 | `task.result()`로 접근 |
| 안전성 | 낮음 (댕글링 태스크 가능) | 높음 (구조적 동시성 보장) |

### gather의 문제점

```python
# gather의 함정 1: return_exceptions=False (기본값)
async def gather_pitfall_1():
    results = await asyncio.gather(task_a(), task_b(), task_c())
    # task_a()가 실패해도 task_b(), task_c()는 계속 실행됨 (댕글링)
    # 첫 번째 예외만 전파, 나머지 태스크의 예외는 caller에게 전파되지 않음

# gather의 함정 2: return_exceptions=True
async def gather_pitfall_2():
    results = await asyncio.gather(
        task_a(), task_b(), task_c(),
        return_exceptions=True
    )
    # results = [결과A, ValueError("실패"), 결과C] -- 타입 혼재
    # 예외를 수동으로 걸러내야 함
    for r in results:
        if isinstance(r, Exception):  # 이 패턴 자체가 안티패턴
            handle_error(r)
```

### 마이그레이션 패턴

```python
# Before: gather (partial success 허용)
async def old_code():
    results = await asyncio.gather(
        fetch(url1), fetch(url2), fetch(url3),
        return_exceptions=True
    )
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

# After: TaskGroup (fail-fast, 구조적)
async def new_code():
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch(url)) for url in [url1, url2, url3]]
        return [t.result() for t in tasks]
    except* Exception as eg:
        for exc in eg.exceptions:
            logger.error(f"실패: {exc}")
        raise  # 또는 적절한 처리
```

### Partial Success가 필요한 경우: 래퍼 패턴

TaskGroup의 fail-fast 동작을 우회하여 부분 성공을 허용해야 하는 경우, 개별 태스크를 래핑한다.

```python
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")

@dataclass
class TaskResult(Generic[T]):
    """성공/실패를 구분하는 결과 래퍼"""
    value: T | None = None
    error: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

async def safe_task(coro) -> TaskResult:
    """개별 태스크의 예외를 잡아 TaskResult로 변환"""
    try:
        result = await coro
        return TaskResult(value=result)
    except Exception as e:
        return TaskResult(error=e)

# 사용: 부분 성공 허용 + 구조적 동시성
async def fetch_with_partial_success(urls: list[str]):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(safe_task(fetch(url))) for url in urls]
    # 모든 태스크가 TaskResult를 반환하므로 ExceptionGroup 발생 안 함
    results = [t.result() for t in tasks]
    successes = [r.value for r in results if r.ok]
    failures = [r.error for r in results if not r.ok]
    return successes, failures
```

> **주의**: 래퍼 패턴은 구조적 동시성의 "예외 전파 보장" 원칙을 우회하는 것이다.
> 정말로 부분 성공이 필요한 경우에만 제한적으로 사용할 것.

---

## Free-Threaded Python (3.13+)

GIL을 비활성화하여 스레드 기반 진정한 병렬 실행을 가능하게 하는 실험적 기능이다.

```python
import sys
import threading

# GIL 상태 확인
print(f"GIL 활성화 여부: {sys._is_gil_enabled()}")

# CPU 바운드 작업 -- free-threaded 빌드에서는 실제 병렬 실행
def cpu_intensive(n: int) -> int:
    return sum(i * i for i in range(n))

threads = [
    threading.Thread(target=cpu_intensive, args=(10_000_000,))
    for _ in range(4)
]
for t in threads: t.start()
for t in threads: t.join()
```

**현재 상태 (3.13)**:
- 실험적: `python3.13t` 별도 실행 파일 또는 `--disable-gil` 빌드 옵션
- 단일 스레드 성능 다소 하락 (3.14에서 5-10%로 개선)
- `PYTHON_GIL=0` 환경 변수 또는 `-X gil=0` 옵션으로 제어
- 모든 C 확장이 호환되는 것은 아님

---

## Subinterpreters (Python 3.14+)

GIL 없이 진정한 멀티코어 병렬성을 제공하는 공식 API.

```python
import concurrent.interpreters as interpreters

# 각 인터프리터는 독립된 GIL을 가짐
# multiprocessing과 달리 같은 프로세스 내에서 실행
interp = interpreters.create()
interp.exec("print('별도 인터프리터에서 실행')")
```

---

## ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as pool:
    future = pool.submit(task_function, *args)
    result = future.result()  # 예외도 자동 전파
```

---

## Queue로 스레드 간 작업 조율

```python
from queue import Queue

queue = Queue(maxsize=10)  # 버퍼 크기 제한 -> 메모리 폭발 방지
queue.put(item)            # 가득 차면 블록
queue.get()                # 비어 있으면 블록
```

---

## 동시성 모델 선택 가이드

| 상황 | 권장 모델 |
|------|----------|
| I/O 바운드 (HTTP, DB, 파일) | `asyncio` 또는 `threading` |
| CPU 바운드 (수치 연산) | `multiprocessing` 또는 C 확장 |
| CPU 바운드 + Free-threaded | `threading` (3.13+ 실험적) |
| 구조적 동시성 | `asyncio.TaskGroup` (3.11+) |
| 프로세스 격리 + 가벼운 통신 | `subinterpreters` (3.14+) |

---

## 참고 자료

- [Python 공식 문서: Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- [PEP 654: Exception Groups and except*](https://peps.python.org/pep-0654/)
- [Notes on structured concurrency (Nathaniel J. Smith)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)
- [Python 3.11 Preview: Task and Exception Groups (Real Python)](https://realpython.com/python311-exception-groups/)
- [CPython Issue #90908: Task groups and cancellation semantics](https://github.com/python/cpython/issues/90908)
- [PEP 789: Preventing task-cancellation bugs](https://peps.python.org/pep-0789/)
