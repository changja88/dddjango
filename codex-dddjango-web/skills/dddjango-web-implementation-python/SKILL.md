---
name: dddjango-web-implementation-python
description: Python 언어 표기법 — PEP 8 선별(dddjango-web 의도적 일탈 3건 포함), None 안전 관용구(좁히기·지역 변수 복사), frozen dataclass 표기 계약, union의 match 패턴 매칭, from_json 직파싱, Either 최소 표면. Python 코드의 이름·형태·모델 선언을 쓸 때 로드한다.
user-invocable: false
---

# Python 표기법

## 언제 쓰나

클래스·함수·상수의 이름과 형태를 정할 때, `None`이 될 수 있는 값을 다룰 때, frozen dataclass 모델·State를 선언할 때, union을 분기할 때, JSON 직파싱·Either를 쓸 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일·클래스 명명의 **무엇**(어떤 이름이 와야 하나) → `dddjango-web-discipline-houserules`
- 도메인 모델 규율(애그리거트·VO)·State 계약 → `dddjango-web-architecture-ddd`·`dddjango-web-architecture-state`
- Either의 계약 의미(Right=성공) → `dddjango-web-architecture-data`
- VM·hx-*·urls·api_client·템플릿 표기 → `dddjango-web-implementation-htmx`·`dddjango-web-implementation-django`

## 핵심 운영 원칙

- 클래스는 CapWords·함수/변수/모듈은 snake_case·상수는 UPPER_SNAKE, CapWords 안 약어는 전부 대문자(`HTTPServerError`·`OrderListVM`), import는 표준 라이브러리→서드파티→`web.` 절대 경로 순 (§2)
- **의도적 일탈 3건**: Repo·UseCase 조회 메서드의 `get_` 접두는 dddjango-web 방언으로 유지 / 광범위 `except Exception`은 safe_api_call 한 곳만 — 일반 코드는 에러 4규칙(구체 예외만·버그성 예외 삼키기 금지·맨 `raise`/`raise … from`·`assert`는 프로그래밍 오류만) / 매개변수·반환·**모든 이름의 첫 대입**에 타입 명시(시그니처는 국소 `ruff.toml` ANN이 기계 강제) (§2)
- bool 인자는 키워드 전용(`*` 뒤)으로, 공개 API·지역 변수 모두 타입 명시 — lambda 매개변수는 주석 불가라 받는 쪽 `Callable[…]`이 타입을 고정 (§2)
- `X | None`은 **지역 변수로 꺼내 `is None` 조기 반환으로 좁히는 것이 표준 관용구** — `assert x is not None` 연쇄는 열화 형태, 기본값은 `or`가 아니라 `is None` 비교 (§3)
- 모델·State는 `@dataclass(frozen=True, slots=True, kw_only=True)` 한 줄 — 메서드·`@property`는 본문에 바로, 컬렉션 필드는 `tuple` (§4)
- 컬렉션 갱신은 `replace(order, lines=(*order.lines, item))` 언패킹 합성으로 (§4·§6)
- `replace(state, error=None)`은 실제 None 대입(액션 실패 소비의 근거) (§4)
- 직파싱 `from_json(cls, data: Mapping[str, object]) -> Self`는 원시 필드를 **`json_field(data, "key", kind)`**(`web/common/util/json_field.py` — 없으면 `KeyError`·타입이 다르면 `TypeError`·`bool`↔`int` 구별)로 읽는다 — domain → common의 유일한 예외 (§7)
- union 분기는 `isinstance` 사슬이 아니라 **`match` 클래스 패턴** — 마지막 `case _: assert_never(x)`가 소진성 자리(검사기 오류·실행 중 `AssertionError`) (§5)
- 문법 하한 **3.11** — 3.12 PEP 695 제네릭(`class X[T]`)·`type` 별칭 문·3.13+ 기능은 생성 코드에 쓰지 않는다, 제네릭은 `TypeVar`·`Generic` (§1)
- Either는 `web/common/util/either.py`의 `Left(value=…)`·`Right(value=…)`·`map`·`flat_map`만 — **분해는 `match`로 통일**(lambda가 `raise`를 담지 못해 조회 실패 raise가 분해 안에 있어야 한다) (§8)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 문법 하한이 허용하는 문법 범위 | [`references/final.md`](references/final.md) §1 |
| 케이싱·import 배치·독스트링·API 형태·에러 처리 | final.md §2 |
| None을 어떻게 다루나 — 좁히기 관용구 | final.md §3 |
| frozen dataclass 모델 선언 표기 | final.md §4 |
| union을 어떻게 분기하나 | final.md §5 |
| 튜플·패턴·클래스 장치·컬렉션 합성 | final.md §6 |
| from_json·JSON 직파싱 | final.md §7 |
| Either 표기·분해 | final.md §8 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
