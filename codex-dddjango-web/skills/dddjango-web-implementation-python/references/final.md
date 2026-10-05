# Python 표기법 — PEP 8·None 안전·frozen dataclass·패턴 매칭

> **출처:** docs.python.org(PEP 8·PEP 257·PEP 484·PEP 604·PEP 634~636 패턴 매칭·`dataclasses`·`typing` — `Self`·`assert_never`·`TypeVar`·`Generic`) · What's New 3.10~3.14(문법 도입 판) · ruff 규칙 문서(`ANN`) — dddart implementation-dart(2026-06-12 확인)의 web 이식.
> 본문 속 `(규약 §N)`은 **출처 표기**이며 로드 대상이 아니다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"뿐.

---

## 목차

- §1. 버전·전제 — 문법 하한 3.11의 정확한 의미·상한
- §2. PEP 8 선별 — 명명·문서·API 형태·에러 처리 (의도적 일탈 3건)
- §3. None 안전 실전 — 키워드 전용·연산자·좁히기 관용구
- §4. frozen dataclass — 표준 표기 계약
- §5. union 분기 — isinstance 사슬 대신 match 패턴 매칭
- §6. Python 문법 — 튜플·패턴·클래스 장치·컬렉션 합성
- §7. from_json — 직파싱 표기
- §8. Either — 최소 표면·match 분해

---

## §1. 버전·전제 — 문법 하한 3.11의 정확한 의미·상한

**생성 코드의 문법 하한은 Python 3.11이다** — 쓰는 문법은 3.11까지의 누적분이다: 구조적 패턴 매칭·`X | Y` 유니언·dataclass `slots=`·`kw_only=`(3.10), `typing.Self`·`typing.assert_never`·`enum.StrEnum`·`datetime.UTC`(3.11).

- **상한 주의**: 3.12의 PEP 695 제네릭 문법(`class Left[L]:`·`def f[T]() -> T`)·`type X = …` 별칭 문·f-문자열 안 같은 따옴표 재사용(PEP 701), 3.13의 타입 매개변수 기본값(PEP 696)·`warnings.deprecated`, 3.14의 괄호 없는 `except A, B`(PEP 758)·템플릿 문자열 `t"…"`(PEP 750)는 **3.11 프로젝트에서 `SyntaxError`·`ImportError`** — 생성 코드에 쓰지 않는다(호스트가 더 새 판이어도 표기를 하나로 고정한다). 제네릭은 `TypeVar`·`Generic`으로 쓴다(§8). 언어 버전은 호스트 `pyproject.toml`의 `requires-python` 하한(없으면 실행 인터프리터)이 정한다 — 하한이 3.11 미만이면 이 표기가 성립하지 않는다.
- 패키지 기준: Django는 호스트 lock 판(4.2 LTS 이상) / 모델·직렬화는 표준 라이브러리(`dataclasses`·`typing`·`enum`)만 — pydantic·attrs·marshmallow는 쓰지 않는다(Either도 외부 패키지가 아니라 `either.py` 한 파일 — §8).

## §2. PEP 8 선별 — 명명·문서·API 형태·에러 처리 (의도적 일탈 3건)

**명명(케이싱)** — 파일·클래스 명명의 *무엇*은 discipline-houserules §4 소유, 여기는 언어 케이싱 규칙:

| 대상 | 케이싱 |
|---|---|
| 클래스·예외·enum·타입 별칭 | `CapWords` |
| 모듈·패키지(파일·디렉터리) | `lowercase_with_underscores` |
| 함수·메서드·변수·매개변수·속성 | `lowercase_with_underscores` |
| **상수**(모듈 수준 상수·클래스 상수·enum 멤버) | `UPPER_SNAKE` |

- **약어**: CapWords 안의 약어는 전부 대문자(`HTTPServerError` — PEP 8). dddjango-web의 `VM` 접미도 이 부류다(`OrderListVM`). snake 이름 안에서는 전소문자(`http_connection`).
- 비공개는 선행 `_` 하나(이름 맹글링 `__x` 금지) · 공개 식별자에 선행 `_` 금지 · 헝가리안 접두 금지 · 미사용 변수·매개변수는 `_`.
- **import 배치**: 표준 라이브러리 → 서드파티(`django` 등) → 로컬(`web.` 절대 경로), 구획 사이 빈 줄, 각 구획 알파벳순. 상대 import·`import *` 금지(경계 사실은 discipline-houserules §5). import는 모듈 머리에 둔다 — 같은 BC 안 순환 사슬을 끊는 함수 안 import 한 자리만 예외다(implementation-django §2 navigator).

**문서 주석(독스트링)**: `"""` 삼중 큰따옴표 · 첫 줄 한 문장 요약 후 빈 줄 · bool 속성·함수는 "~인지 여부"로 · 공개 API에 우선 작성(PEP 257). 주석의 *언제·왜*는 discipline-cleancode §4 소유 — 여기는 표기.

**API 형태**: 개념상 속성 접근이면 `@property`(무인자·멱등·부작용 없음 — `total_amount` 정합) · bool 이름은 긍정형(`is_connected`) · **bool 인자는 키워드 전용으로**(`def render(*, is_compact: bool)` — 위치 bool 금지) · **공개 API·지역 변수 모두 타입 명시**(`channels: list[Channel] = …`·`def get_channels(self) -> Either[BadRequestResponse, list[Channel]]:` — 일탈3) · setter만 단독 정의 금지(frozen 모델엔 setter 자체가 없다) · 다른 호출의 결과를 그대로 돌려주는 위임은 한 줄(`return safe_api_call(lambda: self._remote.get_channels())`).

**의도적 일탈 3건 (dddjango-web 결정 — 일반 관례보다 방언·정책 우선)**:

1. **조회 메서드의 `get_` 접두**: Python 관례는 단순 속성 접근을 `get_x()`가 아니라 `@property`로 쓰는 것이지만, **dddjango-web의 Repo·UseCase 조회 메서드는 `get_channels()` 형태를 쓴다** — HaffHaff 방언이 기준점이고 기존 코드와의 일관이 우선이다(규약 §1 원칙 1). 그 외 일반 메서드는 관례대로 일을 말하는 동사로.
2. **safe_api_call의 광범위 except**: PEP 8은 "가능하면 구체 예외를 적어라 — 맨 `except:` 금지"지만, **safe_api_call 한 곳만 예외**다(`except Exception` — 전 실패를 Either로 정규화하는 의도적 단일 경계 — architecture-data §2의 *왜*가 근거). **일반 코드에서는 4규칙을 지킨다**: 맨 `except:`·`except Exception:` 금지(처리할 수 있는 구체 예외만) · 버그성 예외(`TypeError`·`AttributeError`·`NameError`)를 잡아 삼키지 않는다(버그는 전파되어 traceback을 남겨야 한다) · 재던질 땐 맨 `raise`(원 traceback 보존), 바꿔 던질 땐 `raise NewError(…) from e`(원인 사슬 보존) · `assert`는 프로그래밍 오류 탐지에만 쓴다(`python -O`에서 사라진다 — 입력·계약 검증에 쓰지 않는다). 단 **safe_api_call의 except 절 *내부*에서 호출하는 파서(`from_json` 등)의 2차 raise는 그 단일 경계가 못 잡는다** — 진입한 except 절 내부의 새 예외는 형제 except 절·말미 `except Exception`으로 가지 않아 safe_api_call 밖으로 샌다. 정규화기 호출은 자체 try/except로 감싸 그 raise도 `Left`로 수렴시킨다(architecture-data §2 골든).
3. **매개변수·반환·모든 이름의 첫 대입 타입 명시**: Python 관례(PEP 484)는 지역 변수 주석을 선택으로 두고 검사기 추론에 맡기지만, **dddjango-web은 지역 변수의 첫 대입까지 타입을 적는다**(`forecasts: list[DailyForecast] = …`) — HaffHaff 방언(지역 변수 ~96% 명시)이 기준점이다. 함수 매개변수·반환은 생성 영역 루트의 국소 `ruff.toml`(`ANN` — discipline-houserules §3)이 **기계 강제**하고, 지역 변수 첫 대입은 ruff에 해당 규칙이 없어 표기 규율 + discipline-reviewer 감사로 강제한다. **lambda 매개변수는 문법상 주석을 달 수 없다** — 받는 쪽 매개변수 타입(`Callable[[Order], Order]`)이 그 자리를 고정하고, 타입을 적어야 할 만큼 길면 `def`로 뺀다. 빈 컬렉션 리터럴은 이름 주석이 타입을 준다(`rows: list[OrderRow] = []`). 튜플 언패킹 대입은 주석을 달 수 없으므로 앞줄에 선언하거나 이름 있는 dataclass로 받는다(§6) — 전면 명시의 비용·장황함은 감수한다.

## §3. None 안전 실전 — 키워드 전용·연산자·좁히기 관용구

- **필수 키워드 인자**: 기본값 없는 키워드 전용 매개변수(`*, order_id: str`)·`kw_only` dataclass의 기본값 없는 필드가 필수 인자의 유일한 형태 — 빠뜨리면 생성·호출 시 `TypeError`.
- **None 단락 연산자는 없다**: `if x is None: return` 조기 반환으로 좁힌 뒤 쓴다. `getattr(x, "y", None)`으로 흉내내지 않는다(속성 이름이 문자열로 숨어 검사기·검색을 피한다).
- **None 병합**: `value if value is not None else default` — **`value or default`는 쓰지 않는다**(`0`·`""`·`()`도 거짓이라 정상 값을 기본값으로 바꾼다). None이 될 수 있는 이름은 `X | None`으로 선언하고 `None`으로 명시 초기화한다.
- **None 아님 단언**: `assert x is not None`(검사기 좁히기 + 실패 시 `AssertionError`) — **마지막 수단**: 지역 변수 좁히기·조기 반환·패턴으로 대부분 대체된다. `typing.cast`는 실행 검사가 없으므로 None 제거에 쓰지 않는다.
- **나중에 채우는 속성**: 값 없이 선언만 해 둔 속성(클래스 본문 `x: int`만)은 두지 않는다 — 대입 전에 읽으면 `AttributeError`. frozen dataclass는 생성 때 모든 필드가 채워진다. 나중에 정해지는 값은 `X | None = None`.
- **좁히기 관용구**: 검사기(mypy·pyright)는 `state.error` 같은 속성 체인도 좁히지만, **지역 변수로 한 번 꺼내 좁히는 것을 표준 관용구로 둔다** — 읽기가 한 번이고 이름에 타입이 붙어(§2 일탈3) 좁혀진 뒤의 타입이 코드에 드러난다:

```python
def should_show(state: ChannelSummaryState) -> bool:
    error: BadRequestResponse | None = state.error  # State 필드 → 지역 변수 복사(타입 명시·일탈3)
    if error is None:
        return False
    return error.is_show                            # 여기서 error는 BadRequestResponse로 좁혀졌다
```

`assert state.error is not None` 뒤 `state.error.is_show` 같은 단언 연쇄는 이 관용구의 열화 형태다 — 쓰지 않는다.

## §4. frozen dataclass — 표준 표기 계약

```python
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Self


@dataclass(frozen=True, slots=True, kw_only=True)  # ① 모델·State 전부 이 한 줄
class Order:
    id: str
    lines: tuple[OrderLineItem, ...] = ()  # ③ 기본값은 불변 값만 — 컬렉션은 tuple
    status: OrderStatus | None = None

    @property
    def total_amount(self) -> Money:  # ② 계산 속성·도메인 메서드는 본문에 바로
        ...

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> Self:  # ④ 직파싱 — §7
        ...
```

- ① `frozen=True`(속성 재대입 시 `FrozenInstanceError`)·`slots=True`(오타 속성 대입 차단)·`kw_only=True`(생성은 이름 인자로만 — `Order(id=…, lines=…)`)가 한 묶음이다. `NamedTuple`·`attrs`·`pydantic` 같은 다른 모델 장치는 쓰지 않는다.
- ② 본문 메서드·`@property`·`@classmethod`를 두는 데 별도 장치가 필요 없다 — 도메인 메서드(`cancel()` 류)·계산 속성이 그대로 산다. 단 `slots=True`라 `functools.cached_property`는 쓸 수 없다(`__dict__`가 없다) — 계산 속성은 `@property`로 매번 계산한다.
- **`replace`의 None 의미론**: `replace(state, error=None)`은 **실제로 None을 대입한다** — 액션 실패의 표시·소비(architecture-state §4)의 성립 근거. `replace`는 생성자를 다시 지나므로 kw_only·기본값 규칙이 그대로 적용된다.
- **컬렉션은 tuple**: frozen은 *속성 재대입*만 막는다 — `list` 필드는 `order.lines.append(…)`로 제자리 변경이 그대로 된다. 컬렉션 필드는 `tuple[X, ...]`로 두고, 갱신은 항상 새 컬렉션 합성 + replace: `replace(order, lines=(*order.lines, new_line))`(§6). 가변 기본값(`[]`)은 dataclass가 `ValueError`로 거부한다 — tuple 기본값 `()`은 허용된다.
- 서버 키 대응은 `from_json` 안의 `json_field(data, "…", …)` 키 문자열이 한다(§7) — 필드 선언 자리에 별도 표지를 붙이지 않는다.
- **정렬·정규화가 필요한 컬렉션 루트도 plain class로 빠지지 않는다**: 기본 생성자를 그대로 열어두고 `@classmethod` 정규화 진입점(`from_days(...)`)이 정렬·중복 제거해 반환한다(예제·*무엇*은 architecture-ddd §4). `__post_init__`에서 `object.__setattr__`로 값을 고쳐 넣는 우회는 쓰지 않는다 — `from_json`·`replace`가 모두 기본 생성자를 지나므로 봉인은 무의미하고 서버 데이터 유입 길을 막는다. "비정렬을 타입 수준에서 봉인"하려 plain class로 가면 백스톱 MD1 위반이다(plain 금지 스코프 = entity·VO·루트·State; enum·`exception.py`는 비대상).
- 모델·State의 *무엇*(어떤 클래스를 어디에)은 architecture-ddd §3·§4·architecture-state §3 소유 — 여기는 표기.

## §5. union 분기 — isinstance 사슬 대신 match 패턴 매칭

union(합 타입)은 **frozen dataclass 변종들 + 파일명과 같은 이름의 유니언 별칭**으로 선언한다 — 변종과 별칭을 한 파일(`payment_result.py`)에 둔다(한 파일 한 클래스의 합 타입 예외 — 백스톱 NM3). 분기는 `if isinstance` 사슬이 아니라 **`match` 클래스 패턴**이다:

```python
# payment_result.py — union 선언: 변종마다 frozen dataclass + 파일명과 같은 별칭
@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentSuccess:
    receipt_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentDeclined:
    reason: str


PaymentResult = PaymentSuccess | PaymentDeclined


# 소비 — 키워드 패턴, 마지막은 소진성 자리
def payment_message(result: PaymentResult) -> str:
    match result:
        case PaymentSuccess(receipt_id=receipt_id):
            return f"완료 {receipt_id}"
        case PaymentDeclined(reason=reason):
            return f"거절 {reason}"
        case _:
            assert_never(result)  # 빠진 변종 — 검사기는 오류로, 실행 중엔 AssertionError
```

- Python에는 컴파일 단계 소진성 검사가 없다 — **마지막 `case _: assert_never(x)`가 그 자리다**: 타입 검사기는 빠진 변종을 오류로 보고, 실행 중 새 변종이 오면 `AssertionError`로 멈춘다(조용히 `None`을 돌려주지 않는다). `case _:`에서 기본값을 돌려주는 분기는 쓰지 않는다.
- **kw_only 모델은 키워드 패턴만** 쓴다: dataclass는 `kw_only` 필드를 `__match_args__`에 넣지 않으므로 `PaymentSuccess(r)` 위치 패턴은 `TypeError`다.
- 조회 실패의 오류 분기(implementation-htmx §5)는 union이 아니라 예외 채널이다 — 별개다.
- **Either도 이 표준을 따른다** — 분해는 `match`로 한다(§8).

## §6. Python 문법 — 튜플·패턴·클래스 장치·컬렉션 합성

- **튜플·언패킹**: `name, age = user_info(data)` — 언패킹 대입은 이름 주석을 달 수 없어(§2 일탈3) 앞줄에 `name: str`·`age: int`를 선언해 두거나 이름 있는 dataclass로 받는다. **공개 계약(Repo·UseCase 반환)은 이름 있는 frozen dataclass·Either가 표준** — 튜플은 지역적·사적 묶음에 한정한다(타입 명시·의도 공개 원칙).
- **객체 패턴**: `match order: case Order(status=OrderStatus.CANCELED): …` — 값 비교는 점 붙은 이름(`OrderStatus.CANCELED`)만이다(맨 이름 `case CANCELED:`는 무엇이든 잡는 캡처 패턴이다 — 흔한 함정).
- **guard·`|` 패턴·매핑 패턴**: `case Order(status=status) if status.is_cancelable:` · `case OrderStatus.PAID | OrderStatus.SHIPPED:` · `case {"user": [str() as name, *_]}:` 가용.
- **클래스 장치**: `typing.final`(상속 금지 — 검사기만 강제) · `typing.Protocol`(구조 인터페이스) · `abc.ABC`(상속 계약). 닫힌 변종 집합은 유니언 별칭으로 선언한다(§5). 확장을 통제할 의도가 있을 때만 쓴다(계층 패턴의 base 공통화 금지는 discipline-cleancode §18).
- **컬렉션 합성**: `(*defaults, *items, *(channel.name for channel in channels), *((extra,) if flag else ()))` — 튜플 컬렉션이 불변이므로 **이 언패킹 합성이 컬렉션 갱신의 표준 형태**다. 목록 변환은 컴프리헨션(`[channel.name for channel in channels]`), 결과 이름에는 타입을 단다(§2 일탈3).

## §7. from_json — 직파싱 표기

서버 JSON을 직파싱하는 모델은 `from_json(cls, data: Mapping[str, object]) -> Self` 클래스메서드 **하나**만 둔다(규율·금지의 *무엇*은 architecture-ddd §3 소유). Python에는 codegen이 없고 dataclass는 필드 타입을 실행 중 검사하지 않으므로, **원시 필드는 `json_field`로 타입을 확인하며 읽는다** — 생성된 fromJson의 cast 실패가 예외가 되던 것과 같게, 계약 타입이 다르면 파싱 시점에 실패한다:

```python
# web/common/util/json_field.py — 직파싱 원시 필드 타입 확인의 단일 출처
from collections.abc import Mapping
from typing import TypeVar, cast

T = TypeVar("T")


def json_field(data: Mapping[str, object], key: str, kind: type[T]) -> T:
    """data[key]를 kind로 읽는다 — 없으면 KeyError, 타입이 다르면 TypeError."""
    value: object = data[key]
    if kind is float and type(value) is int:
        return cast(T, float(value))  # float 자리는 int를 받는다(JSON의 1.0이 1로 올 수 있다)
    if type(value) is not kind:
        raise TypeError(f"{key}: {kind.__name__} 자리에 {type(value).__name__}")
    return cast(T, value)  # 위에서 실제 타입을 확인했다
```

```python
# common/network/bad_request_response.py
@dataclass(frozen=True, slots=True, kw_only=True)
class BadRequestResponse(Exception):  # 조회 실패 채널에서 그대로 raise되므로 Exception을 잇는다(architecture-data §2)
    error_type: str
    msg: str
    is_show: bool  # 실물 철자(HaffHaff) — 대상 서버 봉투에 맞춘다(architecture-data §2)

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> Self:
        return cls(
            error_type=json_field(data, "error_type", str),  # 서버 키가 코드에 보인다 — 계약 대조(architecture-data §7)에 유리
            msg=json_field(data, "msg", str),
            is_show=json_field(data, "is_show", bool),  # "false"·0이 오면 TypeError — 참으로 새지 않는다
        )
```

- **누락은 `KeyError`, 원시 필드의 타입 불일치는 `json_field`의 `TypeError`**(`type(value) is kind` — `bool`↔`int`를 가른다 · `int` 자리에 `float` 금지 · `float` 자리에만 `int` 허용), enum·중첩 변환의 형태 불일치는 `ValueError`·`TypeError`가 그대로 올라간다 — 정규화는 safe_api_call의 몫이다(architecture-data §2).
- **domain → common 예외 하나**: domain_layer는 common을 import하지 않지만 `common/util/json_field.py` 하나만 예외다(백스톱 IM19 예외 — 모델이 json_serializable 패키지를 쓰던 자리 · discipline-houserules §5·architecture-ddd §3).
- **쓰지 않는 것(백스톱 MD2)**: 모델 안의 `from_json` 속 `try/except` · `data.get(키, 기본값)` 조용한 기본값 · `_read_*` 수기 타입 리더(타입 확인은 `json_field` 한 곳) · `cls(**data)` 일괄 대입(키가 코드에 안 보이고 여분 키에 `TypeError`).
- enum 값 매핑: `class OrderStatus(StrEnum): PAID = "paid"` → `OrderStatus(json_field(data, "status", str))` — 미지 값은 `ValueError`로 그대로 실패한다(조용히 대체하는 자리를 두지 않는다 — 서버 enum 확장 내성이 계약이면 명세가 그 멤버를 정한다).
- 중첩 모델은 그 모델의 `from_json`, 목록은 `lines=tuple(OrderLineItem.from_json(line) for line in json_field(data, "lines", list))`.
- 계약이 `null`을 허용하는 원시 필드는 `None if data["memo"] is None else json_field(data, "memo", str)`로 읽는다 — `json_field`는 `None`을 받지 않는다(`NoneType` 자리가 아니다).
- 서버로 보낼 때는 그 모델에 `to_json(self) -> dict[str, object]`를 두고 키 문자열을 명시하며 중첩 모델의 `to_json`을 명시 호출한다 — `dataclasses.asdict` 일괄 변환은 필드 이름이 곧 서버 키가 되어 계약 대조가 흐려진다.
- **표시 변환 헬퍼는 별 파일**: 표시용 변환 헬퍼(`*_display_text`·포매터) 클래스는 모델/VO 파일에 동거시키지 않는다 — 한 파일 한 클래스(백스톱 NM3). 날짜처럼 VO 고유 변환은 그 VO의 `from_api(…)` 클래스메서드(architecture-ddd §3)로 둔다 — 추가 public 클래스가 아니다.

## §8. Either — 최소 표면·match 분해

dddjango-web의 Either는 외부 패키지가 아니라 `web/common/util/either.py`에 둔 두 frozen dataclass다. **사용 표면을 좁게 고정한다** — `Either`·`Left`·`Right`·`map`(·연쇄가 필요하면 `flat_map`)만 쓴다:

```python
# web/common/util/either.py — 변종 둘 + 파일명과 같은 별칭(합 타입 파일 — §5)
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

L = TypeVar("L")
R = TypeVar("R")
T = TypeVar("T")


@dataclass(frozen=True, slots=True, kw_only=True)
class Left(Generic[L]):
    value: L

    def map(self, f: Callable[..., object]) -> "Left[L]":
        return self  # 실패 갈래는 f를 부르지 않고 그대로 통과한다

    def flat_map(self, f: Callable[..., object]) -> "Left[L]":
        return self


@dataclass(frozen=True, slots=True, kw_only=True)
class Right(Generic[R]):
    value: R

    def map(self, f: Callable[[R], T]) -> "Right[T]":
        return Right(value=f(self.value))

    def flat_map(self, f: Callable[[R], "Left[L] | Right[T]"]) -> "Left[L] | Right[T]":
        return f(self.value)


Either = Left[L] | Right[R]
```

| 멤버 | 형태 요지 | 용도 |
|---|---|---|
| `match` + `case Left(value=…)` / `case Right(value=…)` | 두 갈래 분해 | **유일한 종단 분해** |
| `map(f)` | Right만 변환·Left 통과 | UseCase의 Either 통과(architecture-ddd §8) |
| `flat_map(f)` | Either 반환 연산 연쇄 | Repo 조합 |
| `Left(value=…)`·`Right(value=…)` | 생성(키워드 — kw_only) | Right=성공은 dddjango-web 계약(architecture-data §3 — 타입 자체는 방향을 강제하지 않는다) |

- **분해는 `match`로 통일한다**: Python lambda는 문장(`raise`·대입)을 담지 못해 "조회 실패면 raise"(architecture-state §4)를 두 핸들러 인자 형태로 쓸 수 없다 — 두 갈래를 `match`로 풀고 `case Left(value=error): raise error`처럼 갈래 안에 문장을 둔다. `fold` 메서드·`isinstance` 사슬·`.value` 직접 읽기(갈래 확인 없이)는 쓰지 않는다. `Either` 별칭은 닫힌 유니언이라 §5의 `assert_never` 소진성도 그대로 붙는다.
- `map`은 예외를 잡지 않는다 — 도메인 예외(`order.cancel()`의 raise)는 Either 밖으로 전파된다. 의도된 동작이다: Either는 *서버 실패* 채널이고 도메인 불변식 위반은 예외 채널(architecture-ddd §4).
- **유지보수 사실**: 파일 하나·표준 라이브러리만이라 외부 판 갱신이 없다. 함수형 라이브러리(`returns` 등 — 호출면·모나드 표면이 넓다)는 **비채택** — 기존 프로젝트에 확립된 Either가 있으면 그것을 따른다.
