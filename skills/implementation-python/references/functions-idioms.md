# 함수 설계와 파이썬 관용 표현

Python 특화 함수 설계 기법과 관용적 표현을 정리한다.

---

## 가변 디폴트 인자의 함정: None 사용

디폴트 인자는 함수 정의 시 단 한 번만 평가된다. 가변 객체를 디폴트로 쓰면 호출
간에 공유된다.

```python
# 나쁜 예: 가변 디폴트 인자
def append_to(element, target=[]):
    target.append(element)
    return target

# 좋은 예: None + 독스트링
def append_to(element, target=None):
    """target의 디폴트 값은 빈 리스트이다."""
    if target is None:
        target = []
    target.append(element)
    return target
```

---

## 위치 전용(/), 키워드 전용(*) 인자

```python
# / 왼쪽: 위치 전용, * 오른쪽: 키워드 전용
def safe_division(numerator, denominator, /, *,
                  ignore_overflow=False,
                  ignore_zero_division=False):
    ...

safe_division(2, 5)                          # OK
safe_division(2, 5, ignore_overflow=True)     # OK
safe_division(numerator=2, denominator=5)     # 에러: 위치 전용
safe_division(2, 5, True)                     # 에러: 키워드 전용
```

---

## 왈러스 연산자(:=)로 반복 제거

```python
# 나쁜 예: 변수 할당과 조건 분리
count = fresh_fruit.get('lemon', 0)
if count:
    make_lemonade(count)

# 좋은 예: 대입식으로 통합 (3.8+)
if count := fresh_fruit.get('lemon', 0):
    make_lemonade(count)

# 컴프리헨션 안에서도 사용
found = {
    name: batches
    for name in order
    if (batches := get_batches(stock.get(name, 0), 8))
}
```

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

## 언패킹 활용

```python
# 인덱스 대신 언패킹
first, second = item

# 스왑
a[i-1], a[i] = a[i], a[i-1]

# 별표 식(starred expression)
oldest, second, *others = sorted_ages

# 반환값 4개 이상이면 클래스/namedtuple 사용
stats = get_stats(lengths)  # Stats 객체 반환
```

---

## enumerate, zip 활용

```python
# 나쁜 예
for i in range(len(names)):
    name = names[i]

# 좋은 예
for i, name in enumerate(names, 1):  # 시작 인덱스 지정 가능
    ...

for name, count in zip(names, counts):
    ...

# 길이 다른 경우
from itertools import zip_longest
for name, count in zip_longest(names, counts, fillvalue=0):
    ...
```

---

## 빈 컨테이너 검사

```python
# 나쁜 예
if len(container) == 0: ...
if len(container) > 0: ...

# 좋은 예: 암묵적 불리언 평가
if not container: ...   # 비어 있음
if container: ...       # 비어 있지 않음
```

---

## f-문자열 사용

```python
# 나쁜 예: % 포매팅, str.format()
print('결과: %d' % value)
print('결과: {}'.format(value))

# 좋은 예: f-문자열 (3.6+)
print(f'결과: {value}')
print(f'{number:.{places}f}')
```

---

## bytes와 str 분리 (유니코드 샌드위치)

인코딩/디코딩은 인터페이스의 가장 먼 경계에서 수행하라.

```python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode('utf-8')
    return bytes_or_str
```

---

## for/while 뒤 else 금지

루프 뒤 else 블록은 루프가 완료되면 실행된다. 직관에 반하므로 사용하지 마라.

---

## 밑줄 관례

| 패턴 | 의미 |
|------|------|
| `_var` | 관례적 보호(protected). 와일드카드 import에서 제외 |
| `var_` | 파이썬 키워드와 이름 충돌 회피 (`class_`) |
| `__var` | 네임 맹글링. 하위 클래스 충돌 방지 전용 |
| `__var__` | 매직 메서드/던더. 파이썬 예약 |
| `_` | 임시/무시 변수 (`for _ in range(10)`) |

---

## 정밀 연산: Decimal

```python
from decimal import Decimal, ROUND_UP

# 나쁜 예: IEEE 754 부동소수점 오차
rate = 1.45
cost = rate * 222 / 60  # 5.364999999...

# 좋은 예: Decimal (str 생성자 필수)
rate = Decimal('1.45')
cost = rate * Decimal('222') / Decimal('60')
rounded = cost.quantize(Decimal('0.01'), rounding=ROUND_UP)
```

---

## 딕셔너리 키 접근 패턴

```python
# 나쁜 예: KeyError 처리 or in 검사
if key in votes:
    names = votes[key]
else:
    votes[key] = names = []
names.append(who)

# 좋은 예: defaultdict
from collections import defaultdict
votes = defaultdict(list)
votes[key].append(who)
```

---

## 정렬: key 파라미터와 튜플 비교

```python
# 단일 기준
tools.sort(key=lambda x: x.name)

# 다중 기준: 튜플 사용, -로 내림차순 (숫자만)
power_tools.sort(key=lambda x: (-x.weight, x.name))
```

---

## 성능 특화 자료구조

```python
from collections import deque
from bisect import bisect_left
from heapq import heappush, heappop

# deque: FIFO 큐에 list 대신 사용 (양방향 O(1))
queue = deque()
queue.append(item)
queue.popleft()  # list.pop(0)은 O(n)

# bisect: 정렬된 시퀀스에서 이진 검색
index = bisect_left(sorted_data, target)

# heapq: 우선순위 큐 - O(log n) 삽입/삭제
heap = []
heappush(heap, (priority, item))
_, item = heappop(heap)
```
