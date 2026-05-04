# 컨텍스트 매니저와 with문

리소스의 acquire/release 패턴을 안전하게 관리하는 컨텍스트 매니저를 정리한다.

---

## 커스텀 컨텍스트 매니저

### 방법 1: 클래스 기반 (__enter__, __exit__)

```python
class ManagedFile:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.file = open(self.name, 'w')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
```

### 방법 2: @contextmanager 데코레이터 (더 간결)

```python
from contextlib import contextmanager

@contextmanager
def managed_file(name):
    try:
        f = open(name, 'w')
        yield f
    finally:
        f.close()

with managed_file('test.txt') as f:
    f.write('hello')
```

**선택 기준**:
- 간단한 설정/해제 -> `@contextmanager`
- 상태가 복잡하거나 재사용성이 높은 경우 -> 클래스 기반

---

## with문 활용 패턴

### Lock 관리

```python
import threading

with threading.Lock():
    ...  # 자동 acquire/release
```

### 임시 상태 변경

```python
@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)

with debug_logging(logging.DEBUG):
    my_function()  # 임시로 DEBUG 레벨
```

---

## 컨텍스트 매니저를 사용해야 하는 경우

| 상황 | 예시 |
|------|------|
| 파일 I/O | `with open(path) as f:` |
| 락 관리 | `with threading.Lock():` |
| DB 연결/트랜잭션 | `with connection:` |
| 임시 디렉토리 | `with tempfile.TemporaryDirectory() as d:` |
| 임시 환경 변수/설정 변경 | 커스텀 `@contextmanager` |
| 타이밍/프로파일링 | 커스텀 `@contextmanager` |
| 에러 억제 | `with contextlib.suppress(FileNotFoundError):` |

리소스의 acquire와 release가 쌍을 이루는 모든 곳에 `with`를 사용하라.
`try/finally`로 직접 관리하는 것보다 의도가 명확하고 실수가 줄어든다.
