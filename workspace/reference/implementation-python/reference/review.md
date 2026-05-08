# Python 언어 특화 가이드 — 상충/모순/불일치 의사결정 문서

> Internal: `coding-python.md` (내부 자료)
> External: `coding-python.md` (외부 자료)

---

### 1. pydantic API 버전

**상충 유형**: 모순

| | Internal | External |
|---|---------|----------|
| 출처 | 단단한 파이썬 | pydantic v2 공식 문서, Migration Guide |
| 주장 | pydantic v1 API(`validator`, `constr`, `parse_obj`, `dict()`) 사용 | pydantic v2 API(`field_validator`, `ConfigDict`, `model_validate`, `model_dump`)가 현재 표준이며 v1은 지원 중단 |

**Internal 근거**: `@validator`, `constr(regex=...)`, `ValidationError` 등 v1 스타일 코드를 예시로 제시한다. pydantic의 런타임 검증 능력을 소개하는 데 초점을 맞추었고, API 버전에 대한 언급이 없다.

**External 근거**: v2는 Rust 기반 코어로 4-50배 빨라졌고 API가 크게 변경되었다. `@validator` -> `@field_validator`, `Config` 클래스 -> `ConfigDict`, `dict()` -> `model_dump()`, `parse_obj()` -> `model_validate()` 등 전면적 마이그레이션을 권장한다.

**추천**: External ▶ (pydantic v1은 공식 지원 중단되었으므로 v2 API로 통일해야 한다)

---

### 2. CPU 바운드 작업의 스레드 병렬화 가능 여부

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 | PEP 703, Python 3.13 What's New |
| 주장 | GIL 때문에 CPU 바운드 작업은 스레드로 병렬화 불가. `subprocess`, `multiprocessing`, C 확장을 사용하라 | Free-Threaded Python(3.13+)으로 GIL을 비활성화하면 스레드 기반 진정한 CPU 병렬 실행이 가능하다 |

**Internal 근거**: CPython의 GIL은 한 번에 하나의 스레드만 바이트코드를 실행하게 한다. CPU 바운드 작업의 병렬화에는 멀티프로세싱이나 C 확장이 필요하다고 단정한다.

**External 근거**: Python 3.13부터 `python3.13t` 또는 `--disable-gil` 빌드로 GIL을 비활성화할 수 있다. 실험적 기능이지만 `threading.Thread`로 CPU 바운드 작업의 실제 병렬 실행이 가능해졌다. 3.14에서는 단일 스레드 성능 하락이 5-10%로 개선되었다.

**추천**: 병합 (Internal의 GIL 설명은 기본 원칙으로 유지하되, Free-Threaded Python을 3.13+ 옵션으로 병기한다)

---

### 3. 비동기 다중 작업 패턴: asyncio.gather vs TaskGroup

**상충 유형**: 모순

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 | PEP 654, Python 3.11 What's New |
| 주장 | `asyncio.gather`로 여러 코루틴을 동시 실행하라 | `asyncio.gather`는 나쁜 예이며, `TaskGroup`과 `except*`로 구조적 동시성을 사용하라 |

**Internal 근거**: `asyncio.gather(coro1, coro2)`를 비동기 I/O 동시성의 표준 패턴으로 제시한다. 예외 처리에 대한 별도 언급 없이 간결한 사용법을 보여준다.

**External 근거**: `gather`에서는 `return_exceptions=True` 사용 시 예외가 결과에 섞이고, 첫 번째 에러만 표면화되는 문제가 있다. `TaskGroup`(3.11+)은 모든 태스크의 예외를 `ExceptionGroup`으로 묶어 전파하며, `except*` 구문으로 타입별 분기 처리가 가능하다.

**추천**: 병합 (3.11 미만에서는 `gather`가 유효하지만, 3.11+에서는 `TaskGroup`을 기본 패턴으로 권장하도록 보완한다)

---

### 4. Deprecation 표시 방식: warnings.warn vs @deprecated

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 | PEP 702, Python 3.13 What's New |
| 주장 | `warnings.warn(DeprecationWarning)`으로 마이그레이션을 안내하라 | `@deprecated` 데코레이터로 런타임 경고와 정적 타입 체커 진단을 동시에 제공하라 |

**Internal 근거**: `warnings.warn()`에 `DeprecationWarning`을 전달하여 함수/파라미터의 지원 중단을 알린다. 런타임 경고만 발생하며, 타입 체커와의 연동은 없다.

**External 근거**: `@deprecated`(3.13+)는 `__deprecated__` 속성을 자동 추가하여 런타임 `DeprecationWarning`과 mypy/pyright 정적 경고를 동시에 제공한다. 클래스, 함수, 오버로드 일부에도 적용 가능하다.

**추천**: 병합 (3.13 미만에서는 `warnings.warn`이 유일한 수단이므로 유지하되, 3.13+에서는 `@deprecated`를 우선 권장하도록 보완한다)

---

### 5. 디스크립터 기반 검증 패턴 구현 방식

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술, 파이썬 클린코드 2nd | Python 공식 Descriptor HowTo Guide (Raymond Hettinger) |
| 주장 | `WeakKeyDictionary`로 인스턴스별 값을 저장하거나, `Validation` 콜러블 객체를 조합하여 검증한다 | ABC 기반 `Validator` 추상 클래스를 만들고 `__set_name__` + `setattr`로 `instance.__dict__`에 직접 저장한다 |

**Internal 근거**: `Grade` 디스크립터는 `WeakKeyDictionary`에 인스턴스를 키로 사용하여 메모리 누수를 방지한다. `Validation` 클래스는 검증 함수와 에러 메시지를 조합하는 방식이다. 두 패턴 모두 `__set_name__`을 활용하지만, 저장 전략이 다르다.

**External 근거**: 공식 Descriptor HowTo Guide의 패턴은 `setattr(obj, self.private_name, value)`로 인스턴스의 `__dict__`에 직접 저장한다. ABC로 `validate` 추상 메서드를 강제하고, `String`, `Number`, `OneOf` 등 구체 검증자를 상속으로 확장한다. `WeakKeyDictionary` 불필요.

**추천**: External ▶ (`instance.__dict__` 직접 저장이 더 단순하고 공식 가이드의 권장 패턴이다. `WeakKeyDictionary`는 `__set_name__` 이전 시대의 우회 방법이다)

---

### 6. 프로파일링 도구 범위

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 | High Performance Python 2nd Edition |
| 주장 | `cProfile`과 `pstats`로 프로파일링하라 | `cProfile`은 1단계이며, `line_profiler`(라인 수준), `memory_profiler`(메모리 분석)까지 3단계 계층으로 접근하라 |

**Internal 근거**: `cProfile.Profile()`로 함수를 실행하고 `pstats.Stats`로 누적 시간 기준 정렬하여 병목을 찾는다. "최적화 전에 반드시 프로파일링하라"는 원칙을 제시하지만 도구는 `cProfile`만 다룬다.

**External 근거**: 1단계 `cProfile`로 함수 수준 병목을 식별한 뒤, 2단계 `line_profiler`(`@profile` + `kernprof`)로 라인 수준 분석, 3단계 `memory_profiler`로 메모리 사용량을 추적하는 계층적 접근을 제시한다. 이를 통해 "Line 3: 850ms"처럼 정확한 병목 라인을 특정한다.

**추천**: External ▶ (`cProfile`만으로는 라인/메모리 수준 병목을 특정할 수 없으므로, 3단계 계층 접근이 실무에서 더 유용하다)

---

### 7. __slots__ 적용 방식: 수동 정의 vs dataclass(slots=True)

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술, 단단한 파이썬 | Python dataclasses 공식 문서, Real Python |
| 주장 | dataclass에서 `__slots__`에 대한 언급 없음. 일반 클래스에서의 사용만 암시 | `@dataclass(slots=True)`(3.10+)로 메모리 20-50% 절약. 수백만 인스턴스에서 170 vs 96 bytes 차이 |

**Internal 근거**: `@dataclass`의 기본 옵션(`frozen=True`, `field(default_factory=...)`)만 다룬다. `slots` 옵션은 언급되지 않으며, `__slots__`는 디스크립터 맥락에서만 간접적으로 등장한다.

**External 근거**: `@dataclass(slots=True)`는 3.10+에서 `__dict__` 대신 `__slots__`를 자동 생성하여 인스턴스당 메모리를 절약한다. 다만 새 클래스를 반환하므로 다중 상속 시 `__slots__` 충돌 가능성을 경고한다.

**추천**: External ▶ (3.10+ 환경에서 대량 인스턴스를 다루는 dataclass라면 `slots=True`는 반드시 알아야 할 옵션이다)
