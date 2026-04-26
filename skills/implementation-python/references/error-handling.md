# Python 예외 처리

Python 특화 예외 처리 패턴과 EAFP 원칙을 정리한다.

---

## try/except/else/finally 각 블록의 역할

```python
try:
    data = read_file(path)        # 예외가 발생할 수 있는 코드
except FileNotFoundError:
    data = default_data            # 예상된 예외 처리
else:
    process(data)                  # try 성공 시에만 실행
finally:
    cleanup()                      # 항상 실행
```

- `try`: 예외가 발생할 수 있는 최소한의 코드만 넣어라
- `except`: 구체적 예외 타입을 잡아라 (bare `except:` 금지)
- `else`: try 성공 후 추가 작업. try 블록을 최소화하는 핵심
- `finally`: 리소스 정리. 예외 발생 여부와 무관하게 실행

---

## 최상위 예외 클래스 정의

API 모듈에는 최상위 Exception을 정의하여 모든 모듈 예외가 이를 상속하게 하라.

```python
# my_module/exceptions.py
class MyModuleError(Exception):
    """모듈의 최상위 예외"""

class InvalidInputError(MyModuleError): ...
class DatabaseError(MyModuleError): ...

# 사용 측
try:
    my_module.do_something()
except my_module.MyModuleError:
    ...  # 모듈의 모든 에러를 한번에 잡을 수 있음
```

**이점**:
- 호출자가 모듈 예외를 포괄적으로 잡을 수 있다
- 미래의 새 예외 추가 시 호출 코드 변경 불필요
- 모듈 내부 구현(서드파티 예외 등)이 외부로 누출되지 않는다

---

## EAFP vs LBYL

Python은 **EAFP** (Easier to Ask Forgiveness than Permission) 스타일을 선호한다.

```python
# LBYL (Look Before You Leap) -- 비파이썬적
if key in dictionary:
    value = dictionary[key]

# EAFP -- 파이썬적
try:
    value = dictionary[key]
except KeyError:
    ...  # 키 없음 처리
```

EAFP가 더 적절한 경우:
- 조건 확인과 사용 사이에 경쟁 조건이 있을 때 (파일, 네트워크)
- 확인 비용이 사용 비용과 비슷할 때
- 예외가 드물게 발생할 때

---

## None 반환 대신 예외 발생

```python
# 나쁜 예: None 반환 - 0과 구분 불가
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

# 좋은 예: 예외 발생 + 타입 힌트
def careful_divide(a: float, b: float) -> float:
    """Raises: ValueError: b가 0일 때"""
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError('잘못된 입력')
```

---

## @deprecated로 지원 중단 표시 (3.13+)

```python
from warnings import deprecated
from typing import overload

# 클래스 지원 중단
@deprecated("Use UserV2 instead")
class UserV1:
    pass

# 함수 지원 중단
@deprecated("Use fetch_data_v2() instead")
def fetch_data(url: str) -> bytes:
    return b""

# 오버로드 일부만 지원 중단
@overload
@deprecated("int 인자는 더 이상 지원하지 않습니다.")
def process(value: int) -> str: ...

@overload
def process(value: str) -> str: ...
```

`__deprecated__` 속성이 자동으로 추가되어 런타임에서도 지원 중단 메시지에
접근할 수 있다. 런타임 `DeprecationWarning` + 타입 체커 경고를 동시에 발생시킨다.

> 3.13 미만에서는 `warnings.warn(DeprecationWarning)`을 사용한다. 단, 이 방법은
> 런타임 경고만 발생하며 타입 체커와 연동되지 않는다.

---

## 독스트링과 문서화

```python
def find_anagrams(word: str) -> list[str]:
    """주어진 단어의 모든 어구전철을 찾는다.

    이 함수는 딕셔너리 파일의 전체 내용을 메모리에
    로드하기 때문에 실행 속도가 느릴 수 있다.

    Args:
        word: 대상 단어. 빈 문자열이면 빈 리스트 반환.

    Returns:
        어구전철 리스트. 매치가 없으면 빈 리스트.
    """
```

- 모듈: 첫 줄에 목적, 이후 공개 함수/클래스 목록
- 클래스: 목적 + 중요 공개 애트리뷰트/메서드
- 함수: 목적 + Args + Returns + Raises
- 타입 어노테이션과 중복되면 둘 중 하나만 유지

---

## 디버깅 기법

### repr 문자열 활용

```python
print(repr(5))    # 5
print(repr('5'))  # '5'
```

### pdb 대화형 디버거

```python
def compute(data):
    result = transform(data)
    breakpoint()  # 여기서 대화형 디버거 시작
    return finalize(result)
```

| 명령 | 설명 |
|-----|------|
| `where` | 현재 호출 스택 출력 |
| `step` | 다음 줄 실행 (함수 내부 진입) |
| `next` | 다음 줄 실행 (함수 호출 건너뜀) |
| `continue` | 다음 중단점까지 계속 |
