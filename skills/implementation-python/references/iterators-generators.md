# 이터레이터, 제너레이터, 컴프리헨션

지연 평가와 효율적 반복을 위한 Python 핵심 기법을 정리한다.

---

## 이터레이터 프로토콜

`for x in obj`는 내부적으로 `iter(obj)` -> `__iter__()` 호출 후
`next()` -> `__next__()` 반복이다.

```python
class BoundedRepeater:
    def __init__(self, value, max_repeats):
        self.value = value
        self.max_repeats = max_repeats
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.max_repeats:
            raise StopIteration
        self.count += 1
        return self.value
```

---

## 리스트 대신 제너레이터

```python
# 나쁜 예: 전체를 메모리에 적재
def load_purchases(filename):
    purchases = []
    with open(filename) as f:
        for line in f:
            purchases.append(float(line))
    return purchases

# 좋은 예: 제너레이터로 지연 평가
def load_purchases(filename):
    with open(filename) as f:
        for line in f:
            yield float(line)
```

---

## 제너레이터 식

```python
# 리스트 컴프리헨션 -> 메모리 전부 사용
total = sum([x ** 2 for x in range(10)])

# 제너레이터 식 -> 메모리 절약
total = sum(x ** 2 for x in range(10))

# 제너레이터 식 합성
it = (len(x) for x in open('file.txt'))
roots = ((x, x ** 0.5) for x in it)
```

---

## yield from으로 제너레이터 합성

```python
# 나쁜 예: 반복적인 for + yield
def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta

# 좋은 예: yield from
def animate():
    yield from move(4, 5.0)
    yield from pause(3)
```

---

## send, throw 사용 금지

제너레이터의 `send()`와 `throw()`는 양방향 통신을 제공하지만 가독성이 매우 나쁘다.
대신 이터레이터를 입력으로 전달하거나 상태를 가진 클래스를 사용하라.

---

## itertools 활용

```python
import itertools

# 연결
itertools.chain([1,2], [3,4])        # 1,2,3,4
itertools.zip_longest([1,2], [3])    # (1,3), (2,None)

# 필터
itertools.islice(values, 2, 8, 2)    # 슬라이싱 (복사 없음)
itertools.takewhile(lambda x: x<7, values)

# 조합
itertools.product([1,2], ['a','b'])  # 데카르트 곱
itertools.combinations([1,2,3], 2)   # 조합

# 누적
itertools.accumulate([1,2,3,4])      # 1,3,6,10
```

---

## 컴프리헨션 인라이닝 (Python 3.12+)

Python 3.12부터 컴프리헨션이 인라인으로 실행된다. 별도의 함수 객체와 프레임을
생성하지 않아 최대 2배 빠르다.

```python
# Python 3.12+: 인라인 실행
squares = [x**2 for x in range(1000)]
data = {k: v for k, v in zip(keys, values)}
```

반복 변수의 격리는 여전히 유지된다 (외부 동명 변수를 덮어쓰지 않음).

```python
x = "outer"
result = [x for x in range(3)]
print(x)  # "outer" -- 격리 유지
```

---

## 컴프리헨션 사용 가이드

- **1단계**: 간단한 변환/필터 -> 컴프리헨션 사용
- **2단계 중첩**: 허용하되, 복잡해지면 헬퍼 함수로 추출
- **3단계 이상 중첩**: 금지. 명시적 루프나 헬퍼 함수로 분리

```python
# 좋은 예: 2단계 중첩
matrix = [[1,2,3], [4,5,6]]
flat = [x for row in matrix for x in row]

# 나쁜 예: 3단계 이상 중첩 -> 헬퍼로 분리
# flat = [x for grid in grids for row in grid for x in row]
def flatten_grids(grids):
    for grid in grids:
        for row in grid:
            yield from row
```
