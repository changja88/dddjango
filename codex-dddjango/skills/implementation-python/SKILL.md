---
name: implementation-python
description: Python 언어 특화 구현 지식 — 타입 힌트·타입 시스템, 구조적 패턴 매칭, 컬렉션·데이터 구조, 함수 설계, 데코레이터, 디스크립터, @property, 클래스 설계, Protocol 심화, Enum/dataclass/NamedTuple, 연산자 오버로딩, pydantic v2, 이터레이터·제너레이터, 컨텍스트 매니저, 예외 처리, 동시성·병렬성, 성능 프로파일링, f-문자열, Python 관용 표현, 디자인 패턴, Ruff, mypy/pyright, 디버깅, 독스트링, 정밀 연산, Python 3.14 변경사항. Python 관용구·타입·Protocol/ABC·경계 도구 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. 기술무관 클린코드 원칙은 dddjango-discipline-cleancode, Django 프레임워크는 implementation-django, 구조 패턴 선택은 dddjango-architecture-ddd, 테스트 코드 작성은 implementation-test로 위임.
---

# Python 언어 특화 구현

## 언제 쓰나

Python 언어 관용구·타입 시스템·Protocol/ABC·dataclass·제너레이터·동시성·Ruff·mypy 등 Python 특화 구현 결정이 주 작업일 때 로드한다. 경계:

- 네이밍·함수 설계·SOLID 등 기술무관 클린코드 원칙 → `dddjango-discipline-cleancode`
- Django 모델·ORM·서비스·트랜잭션·설정 구현 → `implementation-django`
- repository/UoW/핵사고날/CQRS/outbox 구조 패턴 선택 → `dddjango-architecture-ddd`
- 테스트 코드 작성(pytest·픽스처·mock·더블) → `dddjango-implementation-test`

## 핵심 운영 원칙

- 타입 어노테이션은 전 코드베이스에 일관 적용, Optional→X | None, 최신 PEP 695 문법 우선 (§1)
- Union/Literal/NewType으로 상태 공간을 좁혀 잘못된 상태를 타입 레벨에서 차단 (§1.3–§1.4)
- Protocol로 구조적 서브타이핑, ABC는 런타임 등록이 필요할 때만 (§9)
- dataclass(slots, frozen, kw_only)로 불변 값 객체를 표현, NamedTuple은 불변 레코드에 (§10)
- 디스크립터·@property는 검증과 지연 계산에만; 단순 필드는 평범한 애트리뷰트로 (§6–§7)
- 제너레이터로 지연 평가, send/throw 금지 (§13.2, §13.5)
- 커스텀 컨텍스트 매니저로 리소스 해제를 with문으로 명확히 (§14)
- 예외는 도메인 최상위 클래스 정의 후 계층화; None 반환 대신 예외 발생 (§15)
- I/O 병목엔 asyncio.TaskGroup(3.11+), CPU 병목엔 멀티프로세싱 (§16)
- pydantic v2는 경계(입력 검증) 전용, 도메인 진리값으로 사용 금지 (§12.0)
- Ruff로 린트·포맷 통합, mypy/pyright strict 모드로 타입 보장 (§22–§23)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 타입 힌트와 타입 시스템 | §1 |
| 구조적 패턴 매칭 (match/case) | §2 |
| 컬렉션 선택과 데이터 구조 | §3 |
| 함수 설계: Python 특화 기법 | §4 |
| 데코레이터 | §5 |
| 디스크립터 | §6 |
| @property와 애트리뷰트 접근 | §7 |
| 클래스 설계: Python 특화 패턴 | §8 |
| Protocol 심화 | §9 |
| Enum, dataclass, NamedTuple | §10 |
| 연산자 오버로딩과 Python 데이터 모델 심화 | §11 |
| pydantic v2 | §12 |
| 이터레이터, 제너레이터, 컴프리헨션 | §13 |
| 컨텍스트 매니저와 with문 | §14 |
| 예외 처리 | §15 |
| 동시성과 병렬성 | §16 |
| 성능 프로파일링과 최적화 | §17 |
| f-문자열 개선과 PEG 파서 | §18 |
| 파이썬다운 관용 표현 | §19 |
| 디자인 패턴 (Python 고유 구현) | §20 |
| Ruff — 통합 린터/포매터 | §22 |
| mypy/pyright 최신 기능 | §23 |
| 디버깅 기법 | §25 |
| 독스트링과 문서화 | §26 |
| 정밀 연산 | §27 |
| Python 3.14 주요 변경사항 | §28 |
| Python 3.10–3.14 변경사항 요약 (치트시트) | 부록 A |
| 타입 시스템 진화 요약 (치트시트) | 부록 B |
| 주요 매직 메서드 요약 (치트시트) | 부록 C |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
