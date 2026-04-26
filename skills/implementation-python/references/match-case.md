# 구조적 패턴 매칭 (match/case) -- Python 3.10+

`match/case`는 단순 switch문이 아니라 **구조적 분해(destructuring)**를 핵심으로 하는
제어 흐름이다. isinstance 체인이나 복잡한 if/elif 트리를 선언적으로 대체한다.

---

## 7가지 패턴 유형

```python
@dataclass
class Point:
    x: float
    y: float

def describe(obj):
    match obj:
        # 1. 리터럴 패턴: 정확한 값 매칭
        case 0:
            return "영"

        # 2. OR 패턴: | 로 여러 패턴 결합
        case 401 | 403 | 404:
            return "HTTP 에러"

        # 3. 캡처 패턴: 변수에 값 바인딩
        case int(n) if n < 0:      # 가드와 결합
            return f"음수: {n}"

        # 4. 시퀀스 패턴: 리스트/튜플 분해 + 별표 캡처
        case [first, *rest]:
            return f"첫 번째: {first}, 나머지 {len(rest)}개"

        # 5. 매핑 패턴: 딕셔너리 키-값 매칭
        case {"action": "move", "direction": d}:
            return f"이동: {d}"

        # 6. 클래스 패턴: 타입 + 속성 분해
        case Point(x=0, y=y_val):
            return f"Y축 위: y={y_val}"

        # 7. 와일드카드: 모든 것에 매칭
        case _:
            return "알 수 없음"
```

---

## 클래스 패턴과 __match_args__

`__match_args__`를 정의하면 위치 인자로 클래스 패턴을 사용할 수 있다.
`@dataclass`는 이를 자동 생성한다.

```python
# 나쁜 예: isinstance 체인
def process(cmd):
    if isinstance(cmd, MoveCommand):
        if cmd.direction == "north":
            ...
    elif isinstance(cmd, QuitCommand):
        ...

# 좋은 예: match/case로 선언적 분기
def process(cmd):
    match cmd:
        case MoveCommand(direction="north", steps=n):
            move_north(n)
        case MoveCommand(direction=d, steps=n) if n > 10:
            print(f"너무 먼 거리: {d} {n}칸")
        case QuitCommand():
            sys.exit(0)
```

---

## 매핑 패턴과 REST 캡처

매핑 패턴은 딕셔너리에서 필요한 키만 추출하며, 나머지 키는 무시된다.
`**rest`로 나머지를 명시적으로 캡처할 수 있다.

```python
def handle_config(config: dict):
    match config:
        case {"database": {"host": host, "port": int(port)}, **rest}:
            print(f"DB: {host}:{port}, 추가 설정: {rest.keys()}")
        case {"database": {"host": host}}:
            print(f"DB: {host}, 기본 포트 사용")
```

---

## 실전 활용: 상태 머신

데이터 클래스 + match/case + 튜플 매칭으로 상태 전이를 선언적으로 표현한다.

```python
@dataclass
class Event:
    kind: str
    payload: dict

def handle_event(event: Event, state: str) -> str:
    match (state, event):
        case ("idle", Event(kind="start", payload={"task": task})):
            print(f"작업 시작: {task}")
            return "running"
        case ("running", Event(kind="complete")):
            return "idle"
        case ("running", Event(kind="error", payload={"code": code})):
            print(f"에러 코드: {code}")
            return "failed"
        case (_, Event(kind="reset")):
            return "idle"
        case _:
            raise ValueError(f"예기치 않은 상태 전이: {state}")
```

---

## match/case에서의 타입 좁히기

패턴 매칭은 타입 체커(mypy/pyright)와 연동되어 분기별 타입을 좁힌다.

```python
def handle(event: str | int | None) -> str:
    match event:
        case str(s):
            return s.upper()    # s: str
        case int(n):
            return str(n)       # n: int
        case None:
            return "none"
```

---

## dataclass + match_args 통합 (3.10+)

```python
@dataclass
class Command:
    action: str
    target: str
    count: int = 1
    # 자동 생성: __match_args__ = ('action', 'target', 'count')

match cmd:
    case Command("move", direction, n) if n > 0:
        print(f"{direction}로 {n}칸 이동")
    case Command("attack", target):
        print(f"{target} 공격")
```
