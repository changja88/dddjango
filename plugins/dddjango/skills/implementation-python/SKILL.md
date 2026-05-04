---
name: implementation-python
description: >
  This skill should be used when the user asks to "write Python code",
  "review Python code", "modernize Python", "add type hints",
  "use dataclasses", "migrate to pydantic v2", "use match/case",
  "refactor to async", or when any Python code generation, review, or
  refactoring task occurs. Covers Python 3.10-3.14 modern features,
  type hints, Protocol, dataclasses, decorators, generators, asyncio,
  pydantic v2, and Ruff. Language-agnostic clean code principles are
  handled by implementation-cleancode; this skill adds the Python layer.
---

# Python 전용 컨벤션과 패턴

이 스킬은 Python 고유의 컨벤션, 패턴, 관용구를 다룬다.
Python 3.10+을 기준선으로 하며, 3.14까지의 기능을 적극 채택한다.
언어 비종속적 원칙(네이밍, 함수, SOLID, 디자인 패턴, 리팩토링)은
implementation-cleancode에 위임한다.

**기준 요구사항 — 모든 모드에 적용:**
- 항상 최신 Python 구문을 사용한다(3.14+ 선호). 현대적 대안이 있을 때
  deprecated typing import나 레거시 패턴을 사용하지 않는다.
- 모든 공개 함수, 메서드, 클래스에 타입 힌트를 작성한다.
  타입 힌트는 선택사항이 아니다.
- 최신 PEP 표준을 따른다. 새 PEP가 기존 PEP를 대체하는 경우
  (예: TypeVar+Generic 대신 PEP 695), 새로운 형식을 사용한다.

아래 섹션에서 다루는 주제에 대해 작업할 때, 상세한 컨벤션과 코드 예제를
위해 연결된 참조 파일을 읽는다.

**참조 파일 로딩 규칙:**
- Writing 모드: 아래 주제와 관련된 코드를 생성하기 전에 해당 참조 파일을 먼저 읽는다.
- Review 모드: 리뷰 결과를 확정하기 전에 인용한 모든 컨벤션의 참조 파일을 읽는다.
- Refactoring 모드: 변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 Python 코드 생성, 구현, 작성을 요청
- **Review**: 사용자가 기존 Python 코드의 리뷰, 검토, 평가를 요청
- **Refactoring**: 사용자가 Python 코드의 리팩토링, 개선, 현대화를 요청

의도가 모호한 경우 Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩토링해줘"), Review를 먼저 적용한 후 같은 코드에 Refactoring을 적용한다.

## 응답 작성 직전 체크리스트 (필수)

### 공통
- [ ] 응답 첫 섹션은 `## [주요 내용]` 헤더로 시작 (한국어)
- [ ] 응답 마지막에 `## [관련 스킬 참조]` 섹션
- [ ] 모든 응답 한국어로

### 작성/리뷰/리팩토링 공통
- [ ] 도메인 카테고리 문자열(genre, status, category 등)은 Enum/StrEnum으로 추출
- [ ] PEP 604 (X | None) 사용, typing.Optional/Union 회피
- [ ] PEP 585 내장 제네릭(list[int], dict[str, X]), typing.List/Dict 회피
- [ ] @dataclass(frozen=True, slots=True) 기본
- [ ] f-string + 포맷 스펙, % / .format() 회피
- [ ] 가변 디폴트 인자 금지 (None + 함수 내부 초기화)

### 작성 모드
- [ ] **PEP 695 제네릭(`class Stack[T]`) 사용 또는 미사용 근거 명시 (Python 3.12+ 환경이면 사용 권장)**
- [ ] **도메인 예외 클래스(`InvalidTrackError`, `EmptyQueueError` 등)를 모듈 루트에 정의하고 `ValueError` 대신 사용**

### 리뷰 모드
- [ ] [Convention: 한 줄] -- 상세 형식

### 리팩토링 모드
- [ ] [Before] / [After] / [Reason] 형식
- [ ] 카테고리 문자열 → Enum 추출을 발견하면 반드시 적용

### Writing 모드

모든 Python 컨벤션을 묵시적으로 적용한다. 컨벤션을 설명하는 인라인 주석
없이 관용적인 Python 코드를 작성한다. 코드가 스스로 말하게 한다.
모든 공개 함수, 클래스, 모듈에 독스트링을 작성한다.
독스트링은 호출자를 위해 코드가 *무엇을* 하는지 설명한다 — 컨벤션 주석이
아니며 생략해서는 안 된다.

적용할 핵심 컨벤션:

**타입 힌트.** 타입 힌트는 프로덕션에서만 발견될 버그를 작성 시점에 잡아낸다. 모든 함수 시그니처와 중요한 변수에 어노테이션을 작성한다.
`Optional[X]` 대신 `X | None`을 사용한다(3.10+). 내장 제네릭을 사용한다
(`List[int]` 대신 `list[int]`). 3.12+ 코드에서는 제네릭에 PEP 695 구문
(`def f[T]()`)을 사용한다. 구조적 서브타이핑이 충분하면 ABC 대신
`Protocol`을 사용한다.

**데이터 모델링.** 타입이 있는 데이터 구조는 어떤 도구도 검증할 수 없는 암묵적 dict 스키마를 대체한다. 데이터 홀더에는 일반 클래스보다 `@dataclass`를 선호한다.
값 객체에는 `frozen=True`, 성능을 위해 `slots=True`를 사용한다.
고정된 상수 그룹에는 `Enum`을 사용한다 — 순수 문자열이나 매직 정수를
사용하지 않는다. 외부 데이터 검증에는 `pydantic.BaseModel`(v2 API)을
사용한다.

**함수.** 명시적 매개변수 계약은 미묘한 변이 및 순서 버그의 전체 클래스를 방지한다. 가변 매개변수의 기본값으로 `None`을 사용한다.
위치 전용(`/`) 및 키워드 전용(`*`) 매개변수 마커를 사용한다.
에러 신호로 `None` 반환보다 예외를 선호한다. 명확성을 높이는 곳에서
언패킹과 월러스 연산자(`:=`)를 사용한다.

**이터레이터와 제너레이터.** 지연 평가는 데이터셋 크기에 관계없이 메모리를 일정하게 유지한다. 지연 시퀀스에는 제너레이터(`yield`)를 사용한다.
결과가 한 번만 소비되는 경우 리스트 컴프리헨션보다 제너레이터 표현식을
선호한다. 제너레이터를 합성하려면 `yield from`을 사용한다.
복잡한 이터레이션에는 `itertools`를 사용한다.

**컨텍스트 매니저.** 결정적 정리는 조용히 남아 장애를 유발하는 리소스 누수를 방지한다. 모든 acquire/release 패턴(파일, 락, 연결, 임시 상태)에 `with`를
사용한다. 단순한 경우에는 `@contextmanager`를, 상태가 있는 경우에는
`__enter__`/`__exit__`를 사용한다.

**패턴 매칭.** 구조적 패턴 매칭은 디스패치 로직을 선언적이고 완전성 검사가 가능하게 만든다. isinstance 체인이나 복잡한 if/elif 트리 대신
`match/case`(3.10+)를 사용한다. dataclasses와 결합하여 선언적
디스패치를 구현한다.

**데코레이터.** 잘 타입이 지정된 데코레이터는 호출자와 타입 체커를 위해 원래 함수의 계약을 보존한다. 항상 functools의 `@wraps`를 사용한다. 타입 안전한
데코레이터 시그니처를 위해 `ParamSpec`을 사용한다. 데코레이터가 bare
(`@deco`)와 매개변수화된(`@deco(...)`) 사용을 모두 지원하면,
하나의 이름 아래 `@overload`로 통합한다 — 두 개의 별도 함수 이름을
노출하지 않는다. 교차 관심사(타이밍, 트레이싱, 로깅)가 예외 경로에서도
bare `raise`로 재발생 전에 실행되도록 내부 함수 호출을
`try/except BaseException`으로 감싼다. 클래스 수준 동작에는
메타클래스보다 클래스 데코레이터를 선호한다.

**클래스 설계.** 일반 속성으로 시작하고, 로직이 필요할 때만 `@property`를
추가한다. `__private` 이름 맹글링 대신 `_protected` 컨벤션을 사용한다.
모든 클래스에 `__repr__`을 구현한다. 대안 생성자에 `@classmethod`를
사용한다. 메타클래스 대신 `__init_subclass__`를 사용한다.

**동시성.** `asyncio.gather` 대신 `asyncio.TaskGroup`(3.11+)을 사용한다.
TaskGroup 블록이 종료된 후 `task.result()`로 결과를 수집한다 —
`create_task()`의 `Task` 참조를 리스트나 딕셔너리에 저장한 후
`async with` 블록 이후에 순회한다. 동시 태스크 내부에서 공유 컬렉션을
변이하지 않는다. 여러 `except*` 절로 `ExceptionGroup`을 처리한다 —
예외 타입을 구분하고, 단일 광범위한 `Exception`을 잡지 않는다.
블로킹 I/O에는 스레드, CPU 바운드 작업에는 멀티프로세싱을 사용한다.

**도구.** 린팅과 포매팅에 Ruff를 사용한다. 타입 체킹에 mypy 또는 pyright를
strict 모드로 사용한다.

> Reference: see `references/` for detailed conventions with examples.

### Review 모드

잘 구조화된 Python 코드를 리뷰할 때는 개선 사항을 나열하기 전에 코드의
잘된 점을 인정한다. 품질이 낮은 코드를 리뷰할 때는 가장 영향력 있는
문제부터 집중한다.

각 발견 사항을 다음 형식으로 작성한다:

```
[Convention] -- 이것이 관용적 Python이 아닌 이유 설명
```

리뷰를 확정하기 전에 이 체크리스트의 모든 항목을 확인한다:

- [ ] 3.10+ 구문 누락: `Optional[X]` 대신 `X | None`, `Union[X, Y]` 대신
      `X | Y`
- [ ] 레거시 typing import: 내장 `list`, `dict`, `tuple` 대신
      `typing.List`, `typing.Dict`, `typing.Tuple` 사용
- [ ] pydantic v1 API: v2 대안 대신 `@validator`, `class Config`, `.dict()`,
      `.parse_obj()` 사용
- [ ] `@dataclass`나 `BaseModel`이 더 적합한 곳에서 일반 dict/NamedTuple 사용
- [ ] `Protocol`(구조적 서브타이핑)이 충분한 곳에서 ABC 상속
- [ ] acquire/release 리소스에 대한 컨텍스트 매니저 누락
- [ ] 제너레이터가 메모리를 절약할 수 있는 곳에서 eager 리스트 생성
- [ ] `Enum`이 의도를 표현하는 곳에서 순수 문자열/정수 상수 사용
- [ ] f-strings 대신 문자열 연결 또는 `%`/`.format()` 사용
- [ ] 컴프리헨션 과용(2단계 초과 중첩) 또는 미활용(리스트를 만드는 명시적 루프)
- [ ] 데코레이터 래퍼에서 `@wraps` 누락
- [ ] 가변 기본 인수(`def f(items=[])`)
- [ ] `match/case`여야 할 isinstance 체인
- [ ] 공개 API에서 타입 어노테이션 누락
- [ ] `TaskGroup`이 적합한 곳에서 `asyncio.gather` 사용(3.11+)

### Refactoring 모드

리팩토링 시 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 Python 컨벤션에 연결하여 근거를 추적 가능하게 한다.
각 변경을 다음 형식으로 작성한다:

```
[Before]
<원본 코드>

[After]
<개선된 코드>

[Reason] Convention -- 이 변경이 더 Pythonic인 이유 설명
```

변경 사항을 제시하기 전에 아래의 모든 적용 가능한 개선을 적용한다:

- [ ] 레거시 `Optional[X]` / `Union[X, Y]` -> `X | None` / `X | Y`로 대체
- [ ] `typing.List` / `typing.Dict` -> 내장 제네릭으로 대체
- [ ] pydantic v1 API -> v2로 마이그레이션(`field_validator`, `model_config`,
  `model_dump`, `model_validate`)
- [ ] 구조화된 데이터를 위한 일반 dict -> `@dataclass` 또는 `BaseModel`로 변환
- [ ] 단일 메서드의 ABC -> `Protocol`로 변환
- [ ] 수동 리소스 정리 -> 컨텍스트 매니저로 래핑
- [ ] 단일 패스 소비에서의 eager 리스트 -> 제너레이터로 변환
- [ ] 매직 문자열/정수 -> `Enum`으로 추출
- [ ] 문자열 연결 -> f-strings로 변환
- [ ] 과도하게 중첩된 컴프리헨션 -> 헬퍼 추출 또는 평탄화
- [ ] isinstance 체인 -> `match/case`로 재작성
- [ ] 누락된 어노테이션 -> 공개 API에 타입 힌트 추가
- [ ] `asyncio.gather` -> `TaskGroup`으로 대체(3.11+)

리팩토링이 관찰 가능한 동작을 변경하는 경우(예: 부분 성공 시맨틱에서
fail-fast로, 또는 무시되는 에러에서 예외 전파로), 동작 차이를 명시적으로
기술하고 이전 동작에 의존하는 호출자를 위한 마이그레이션 경로 또는
래퍼 패턴을 제공한다.

개별 변경 후에는 **전체 리팩토링된 코드**를 제공하여 사용자가
모든 것이 어떻게 맞아떨어지는지 볼 수 있게 한다.

---

## 1. 타입 힌트와 타입 시스템

모든 공개 함수와 클래스에 어노테이션을 작성한다. 현대적 구문을 사용한다:

| Legacy (avoid)            | Modern (prefer)           | Since |
|---------------------------|---------------------------|-------|
| `Optional[X]`            | `X \| None`               | 3.10  |
| `Union[X, Y]`            | `X \| Y`                  | 3.10  |
| `typing.List[int]`       | `list[int]`               | 3.9   |
| `TypeVar('T')` + Generic | `def f[T]()`, `class C[T]`| 3.12  |
| `TypeGuard`              | `TypeIs` (both branches)  | 3.13  |

구조적 서브타이핑에 `Protocol`을 사용한다 — 상속이 필요 없다. 여러
프로토콜을 상속하여 프로토콜을 합성한다. 타입 안전한 데코레이터에
`ParamSpec`과 `Concatenate`를 사용한다.

> Reference: `references/type-hints.md`

## 2. 패턴 매칭 (match/case)

구조적 분해에 `match/case`(3.10+)를 사용한다. dataclasses, 가드,
중첩 패턴과 결합한다. 7가지 패턴 유형: literal, OR, capture, sequence,
mapping, class, wildcard.

> Reference: `references/match-case.md`

## 3. 데이터 모델링

**dataclass**: 데이터 보유 클래스의 기본. 불변성에 `frozen=True`,
메모리에 `slots=True`, 안전성에 `kw_only=True`를 사용한다.

**Enum**: 매직 문자열/정수를 타입 있는 상수로 대체한다. 불투명 값에
`auto()`, 문자열 열거형에 `str, Enum`을 사용한다.

**pydantic v2**: 외부 데이터 검증에 사용한다. `field_validator`
(`@validator` 아님), `ConfigDict`(`class Config` 아님), `model_dump`
(`.dict()` 아님), `model_validate`(`.parse_obj()` 아님)를 사용한다.
타입 강제 변환이 바람직하지 않을 때 strict 모드를 사용한다.

> Reference: `references/data-modeling.md`

## 4. 함수와 관용구

가변 매개변수의 기본값으로 `None`을 사용한다. API에 `/`(위치 전용)와
`*`(키워드 전용)를 표시한다. 언패킹, 월러스 `:=`, `enumerate`, `zip`,
암묵적 불리언 평가를 사용한다. 에러 시 `None` 반환 대신 예외를 발생시킨다.

> Reference: `references/functions-idioms.md`

## 5. 데코레이터

항상 `@functools.wraps`를 적용한다. 시그니처 보존에 `ParamSpec`을
사용한다. 클래스 수준 확장에는 메타클래스보다 클래스 데코레이터를
선호한다. 매개변수화된 데코레이터에는 3단계 중첩 또는 `__call__`이
있는 클래스를 사용한다.

> Reference: `references/decorators.md`

## 6. 디스크립터와 Property

일반 속성으로 시작한다. 계산된 접근이나 검증이 필요할 때 `@property`를
추가한다. 재사용 가능한 검증 로직에는 `__set_name__` +
`instance.__dict__` 저장소를 사용하는 디스크립터를 사용한다.
지연 로딩에 `__getattr__`를 사용한다.

> Reference: `references/descriptors.md`

## 7. 클래스 설계

대안 생성자에 `@classmethod`를 사용한다. 모든 클래스에 `__repr__`을
구현한다. `__private` 대신 `_protected`를 사용한다. 서브클래스 훅과
플러그인 레지스트리에 `__init_subclass__`를 사용한다. 교차 관심사
동작에 믹스인을 사용한다. 커스텀 컨테이너에 `collections.abc`를 상속한다.

> Reference: `references/class-design.md`

## 8. 이터레이터, 제너레이터, 컴프리헨션

지연 평가에 제너레이터를 사용한다. 단일 패스 소비에 제너레이터 표현식을
선호한다. `yield from`으로 합성한다. `send()`/`throw()`를 피한다.
복잡한 이터레이션에 `itertools`를 사용한다. 컴프리헨션은 최대 2단계
중첩으로 유지한다.

> Reference: `references/iterators-generators.md`

## 9. 컨텍스트 매니저

모든 acquire/release 패턴에 `with`를 사용한다. 단순한 경우에는
`@contextmanager`를, 상태가 있는 경우에는 클래스 기반을 사용한다.
락, 파일, 연결, 임시 상태 변경에 적용한다.

> Reference: `references/context-managers.md`

## 10. 에러 처리

`try/except/else/finally`를 사용한다 — 각 블록에는 목적이 있다.
모듈 수준 루트 예외 클래스를 정의한다. 타입 체커 통합이 있는
deprecation 경고에 `@deprecated`(3.13+)를 사용한다.

> Reference: `references/error-handling.md`

## 11. 동시성

구조적 동시성에 `asyncio.TaskGroup`(3.11+)과 `except*`를 사용한다.
블로킹 I/O에는 스레드, CPU 작업에는 멀티프로세싱을 사용한다.
Free-threaded Python(3.13+)과 subinterpreters(3.14+)를 인지한다.

> Reference: `references/concurrency.md`

## 12. 도구

린팅(flake8, isort, pyupgrade 대체)과 포매팅(Black 대체)에 Ruff를
사용한다. mypy 또는 pyright를 strict 모드로 사용한다.
cProfile -> line_profiler -> memory_profiler로 프로파일링한다.

> Reference: `references/tooling.md`

## 13. 모던 Python (3.12-3.14)

PEP 695 타입 매개변수 구문(3.12+)을 사용한다. f-string 개선(3.12+)을
사용한다. `@deprecated`(3.13+)를 사용한다. 지연된 어노테이션 평가(3.14)와
템플릿 문자열(3.14)을 인지한다.

> Reference: `references/modern-python.md`
