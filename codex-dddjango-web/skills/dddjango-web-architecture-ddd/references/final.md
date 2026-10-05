# 도메인 아키텍처 — 간소화 DDD·판정 소유·애그리거트 클라 규율

> **출처:** dddjango `architecture-ddd` final 소스판(2026-06-12 반입 — Evans·Vernon·Millett·Percival&Gregory·Fowler 합성, 서지 전문은 작업장 external.md 말미) · 제1 규약 §3.2·§3.3·§7.1·§9·§10-5 ③ · dddart 파이프라인 본설계(2026-06-12) §5·§8·§9 · dddjango-web 2.0.0 대응 규약(dddart → web).
> 본문 속 `(규약 §N)`·`(본설계 §N)`은 **출처 표기**이며 로드 대상이 아니다 — 규칙 자체는 본문에 자족적으로 서술된다. 로드 가능한 위임은 "스킬명 + §번호(또는 주제)"와 공유 reference(`undecidable.md`)뿐.

---

## 목차

- §1. dddjango-web의 DDD — 간소화의 지도
- §2. 전략 어휘 — 도메인·BC·유비쿼터스 언어
- §3. 값 객체·엔티티 — frozen dataclass·직파싱 하의 형태
- §4. 애그리거트 — 일관성 경계의 클라 번역 (§10-5 ③)
- §5. 판정 소유와 강등 — 1곳째부터 domain
- §6. 도메인 서비스 — 주어 귀속·stateless
- §7. Specification — 재사용·조합되는 판정
- §8. UseCase — Model의 관문
- §9. 빈혈 vs 풍부 — 트랜잭션 스크립트의 함정
- §10. dddjango-web 비채택 패턴 — 음성 지식
- §11. 핵심 요약

---

## §1. dddjango-web의 DDD — 간소화의 지도

DDD의 전술 패턴은 궁극적으로 **시스템의 자유도를 줄여 복잡성을 낮추는 수단**이다 — 복잡한 것을 불변성으로 감싸고, 비즈니스 규칙을 그 규칙의 주인 안에 가둬서 "아무 데서나 아무 값이나 바뀔 수 있는" 상태를 없앤다. dddjango-web은 이 목적은 전부 취하되, 서버·조직 환경을 전제하는 장치는 버린 **간소화 DDD**다. web은 백엔드 API를 소비하는 클라이언트다 — 이 문서의 «클라»는 web을 뜻한다.

| 채택 | 형태 |
|---|---|
| 바운디드 컨텍스트·유비쿼터스 언어 | BC = `web/application/<bc>/`(기능 영역 — area 그루핑 시 `web/application/<area>/<bc>/`, houserules §1 소유), 같은 개념 같은 철자 (§2) |
| 값 객체·엔티티·애그리거트 | frozen dataclass 불변 + 직파싱, 애그리거트(개념) 1차 폴더 (§3·§4) |
| 판정 소유 | **1곳째부터 domain 기본** — dddjango-web 고유 1급 규칙 (§5) |
| 도메인 서비스·Specification | 주어 귀속·공용 위치 없음 (§6·§7) |
| 응용 서비스 | **UseCase**로 치환 — Model의 관문, command+query 통합 (§8) |

| 비채택 | 대체 |
|---|---|
| 도메인 이벤트·Event Sourcing·Saga·CQRS·Repo 인터페이스+UoW·DIP·핵사고날·ACL·컨텍스트 맵·증류·Data Mapper·대규모 구조·마이크로서비스식 BC 분리 | §10 — 각 항목의 *왜*와 dddjango-web의 대체 경로 |

판단이 갈리는 경계(BC 어휘 보유·게이트 입장·판정 귀속)는 공유 reference `undecidable.md`(`${CLAUDE_PLUGIN_ROOT}/skills/discipline-houserules/references/undecidable.md`) §3·§4·§8이 판별 절차를 소유한다 — 이 문서는 규칙 본문을 소유한다.

## §2. 전략 어휘 — 도메인·BC·유비쿼터스 언어

- **도메인과 하위 도메인**: 도메인은 소프트웨어로 해결하려는 문제 영역 전체, 하위 도메인은 그 안의 구획이다. 하위 도메인은 **발견**하는 것이고(업무가 이미 그렇게 나뉘어 있다), 바운디드 컨텍스트는 **설계**하는 것이다(우리가 경계를 긋는다).
- **바운디드 컨텍스트(BC)**: 하나의 모델·하나의 언어가 일관되게 통하는 명시적 경계다. 같은 단어도 컨텍스트가 다르면 다른 모델이다 — 마케팅의 '리드'와 영업의 '리드'는 다른 클래스로 산다. dddjango-web에서 BC의 물리 형태는 `web/application/<bc>/`(기능 영역 — 선택적 area 그루핑 시 `web/application/<area>/<bc>/`, area는 순수 시각 네임스페이스라 BC 경계·통신에 무영향·houserules §1 소유)이고, BC 간 통신은 4채널만 허용된다(닫힌 열거는 discipline-houserules §5). 화면이 어느 BC에 속하는지·BC 어휘를 "보유"하는지의 판별은 `undecidable.md` §3.
- **교차 BC 채널 선택 절차** (규약 §9-3 — 각 채널의 정의가 곧 용도다): 타 BC의 **어휘(타입)만** 필요하면 ① 도메인 타입 import, **행위·데이터 접근**이면 ② 그 BC UseCase 호출(단일 관문), **화면 이동**이면 ③ navigator 호출(이름만), **화면 자체를 보여주려면** ④ view 임베드. 반응형으로 "살아 있는" 타 BC 상태가 필요해 보이면 설계를 다시 본다 — architecture-state §7.
- **유비쿼터스 언어**: 도메인 전문가와 코드가 같은 단어를 쓴다 — 코드의 클래스·메서드·파일명이 업무 어휘를 그대로 반영해야 대화와 코드 사이의 번역 비용(과 번역 중 왜곡)이 사라진다. dddjango-web의 집행 형태: **같은 개념은 계층이 달라도 같은 철자**(어순 포함 — discipline-houserules §2), UseCase는 화면이 아니라 도메인 개념 단위 명명(§8). **task가 도메인 표시 라벨을 명시 열거하면**(상태 N종을 정본 문자열로 나열 등) 그 문자열이 권위 어휘다 — 코드가 라벨을 어디 두든(도메인 enum 표시명 프로퍼티·ui_extension §5) 그 문자열을 **verbatim 보유**하고, 다른 언어로 왕복 번역(task 언어→영어→task 언어)·task에 없는 라벨 발명·task 라벨 누락을 하지 않는다(번역 중 왜곡의 한 형태). 같은 이유로 **도메인 enum 식별자는 서버 계약 enum 값을 verbatim 따른다** — enum 값으로 받는 서버값과 의미가 어긋나는 이름으로 재명명하지 않는다(계약 어휘 보존).
- **지식 탐구**: 원전의 워크숍 서사(도메인 전문가와의 반복 대화)는 dddjango-web 파이프라인에선 G0 스코프 메모·G1 설계 리뷰가 그 자리다 — 행위 목록의 어휘를 다듬는 일이 지식 탐구의 실행 형태다.

## §3. 값 객체·엔티티 — frozen dataclass·직파싱 하의 형태

**값 객체(VO)** — 식별자가 없고, 속성 조합이 곧 동등성이며, 불변이다. 원전에서 불변·동등성 구현에 들이는 노력(equals 오버라이드 등)을 **`@dataclass(frozen=True)`가 표준 라이브러리 수준에서 전부 제공한다** — dddjango-web의 VO는 frozen dataclass다(표기법은 implementation-python §4 소유):

```python
# domain_layer/<aggregate>/value_object/money.py
@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    amount: int

    def add(self, other: "Money") -> "Money":
        return Money(amount=self.amount + other.amount)

    def multiply(self, count: int) -> "Money":
        return Money(amount=self.amount * count)
```

- VO에 도메인 연산을 메서드로 담는 것이 핵심이다 — `Money`가 더하기를 알고, 호출부는 `int` 산수를 하지 않는다. "값 객체의 상태 관련 **모든** 비즈니스 로직은 자신의 경계 안에 있다."
- 도메인 분류 값은 `enum/`(예: `ChannelType`) — 분류에 붙는 판정(`is_shippable` 류)은 enum의 프로퍼티·메서드로 담는다.

**엔티티** — 고유 식별자를 보유하고, 식별자가 같으면 속성이 달라도 같은 것이다. dddjango-web에서 엔티티는 **애그리거트의 일부로만 사용**한다(독립 엔티티 없음): 애그리거트 루트(`<aggregate>.py` 폴더 직속) 또는 종속 엔티티(`entity/`).

- **직파싱(필수 형태)**: 엔티티·VO는 **`@dataclass(frozen=True, slots=True, kw_only=True)`로 선언**한다 — 서버 JSON을 직파싱하는 모델은 `from_json(cls, data: Mapping[str, object]) -> Self` 클래스메서드 **하나**만 둔다(DTO 없음 — 규약 §9-2). Python에는 codegen이 없으므로 `from_json`이 원시 필드 타입을 직접 확인해야 dddart(생성 fromJson의 cast 실패 = 예외)와 같다 — 그 확인의 단일 출처가 `web/common/util/json_field.py`의 `json_field(data: Mapping[str, object], key: str, kind: type[T]) -> T`다(`value = data[key]` — 없으면 `KeyError` · `type(value) is kind`가 아니면 `TypeError` — `bool`↔`int` 구별 · `int` 자리에 `float` 금지 · `float` 자리에는 `int` 허용). 원시 필드는 `json_field(data, "msg", str)`로 읽고, 중첩은 그 모델의 `from_json`, 목록은 `tuple(X.from_json(i) for i in json_field(data, "items", list))`로 읽는다. domain → common은 `common/util/json_field.py` 하나만 예외다(직파싱 단일 출처 — dddart에서 모델이 json_serializable 패키지를 쓰던 자리 — discipline-houserules §5). **모델 안의 수기 타입 리더 헬퍼(`_read_str`/`_read_int`/`_read_float` 류)·`from_json` 안의 `try/except`·조용한 기본값(`data.get(키, 기본값)`)은 금지**(백스톱 MD2) — 누락·타입 불일치는 그대로 예외(`KeyError`·`TypeError`·`ValueError`)로 올라가고, 파싱 실패 정규화는 safe_api_call의 몫이다(architecture-data §2). *이 금지의 예외*: `enum`은 dataclass 대상이 아니라 `Enum` 값 = 서버 값 매핑을 쓴다(`OrderStatus(json_field(data, "status", str))` — 수기 `parse` 불요) · 날짜 같은 커스텀 변환(그 VO의 `from_api(...)` 클래스메서드 — 그 안의 `ValueError` 등 parse-raise는 safe_api_call이 정규화하므로 허용)과 도메인 `*Exception`(불변식 위반 — §4 3규칙-2)은 금지 대상이 아니다. 유입 경로 계약은 architecture-data §4 소유.
- **송신 직렬화도 도메인 단위 거주**: 도메인 값을 전송 표현으로 바꾸는 *변환 로직*(날짜→API path 문자열·`to_api_path()`·다필드 path 조립 등)은 역직파싱과 대칭으로 **VO 메서드(우선)·VM 변환**에 단일 거주한다 — navigator·view·repo에 `date.strftime(...)`을 인라인·중복하지 않는다(navigator는 VO가 만든 문자열을 경로 인자에 *전달만* — architecture-ui §6). 단순 식별자 전달(`str(id)`·이미 `str`인 값)은 변환 로직이 아니라 navigator가 그대로 실어도 된다. *왜* — 인라인·중복 직렬화는 테스트로 두드리기 어렵고(navigator는 실 urlconf 연결 없이는 단위 테스트로 미경유) 같은 포맷이 두 곳(navigator·repo)에 갈리면 DRY가 깨져 회귀가 샌다.
- **router·navigator의 공개 메서드 인자·router가 view에 넘기는 path-param은 원시값(`str`·`int` — 경로 변환기가 주는 그대로)이다** — 도메인 VO를 *인자 타입*으로 받지 않는다. VO를 받으면 그 파일(`<bc>_navigator.py`·`<bc>_router.py`)이 domain을 import해 백스톱 IM21(navigator)·IM22(router) 위반이다. 호출자(VM)가 `vo.to_api_path()`로 직렬화해 `str`을 넘기고, 수신 view가 `Vo.from_api_path(str)`로 복원한다(복원은 presentation→domain import라 매트릭스 허용). *왜* — router/navigator는 라우팅 배선이라 도메인 어휘를 보유하지 않는 경계다(carrier는 문자열만 흐른다).
- 의도를 드러내는 인터페이스: 메서드 이름은 "무엇을 하는가"(도메인 어휘)를 말하고 "어떻게"를 숨긴다 — `order.cancel()`이지 `order.set_status(OrderStatus.CANCELED)`가 아니다. 부작용 없는 함수(조회는 상태를 바꾸지 않음)는 frozen dataclass 불변이 구조로 보장한다.

## §4. 애그리거트 — 일관성 경계의 클라 번역 (§10-5 ③)

애그리거트는 연관된 엔티티·VO를 하나로 묶은 **일관성 관리의 단위**다. 루트 엔티티가 경계의 문이고, 폴더 형태는 애그리거트(개념) 1차다(트리 사실은 discipline-houserules §1·§3).

원전(Vernon 4규칙)은 가변 객체·DB 트랜잭션 전제라 클라에 그대로 못 쓴다 — dddjango-web 번역(클라엔 트랜잭션이 없고, frozen dataclass라 이미 불변이며, **서버가 진실원천**이다):

| Vernon 규칙 | dddjango-web 번역 |
|---|---|
| 1. 진짜 불변식을 경계 안에서 보호 | 불변식 검증은 **루트의 변경 메서드 안에서** (아래 3규칙-2) |
| 2. 작은 애그리거트 | 유지 — 일관성 유지에 필요한 만큼만, 그 이상은 별도 애그리거트(리뷰 수천 건을 상품에 넣지 않는다) |
| 3. 타 애그리거트는 ID 참조 | 서버 응답 모양 우선 (아래 3규칙-3) — ORM FK 금지 확장은 서버 관심사라 해당 없음 |
| 4. 경계 밖은 결과적 일관성 | 클라의 애그리거트 간 동기화는 **서버 재조회(VM 재조립)·SharedState**(architecture-state §5)가 그 자리 — 도메인 이벤트는 비채택(§10) |

**§10-5 ③ 확정 3규칙 (2026-06-12 사용자 확정 — 안 A)**:

1. **루트 경유 변경**: 조건·계산·상태 전이가 걸린 갱신은 **애그리거트 루트의 메서드가 새 인스턴스를 반환**하는 형태로만 한다. `dataclasses.replace`는 누구나 부를 수 있는 만능 문이라 불변만으로는 규칙 산개를 못 막는다 — VM·UseCase의 `replace` 직접 호출은 **도메인 의미 없는 단순 복제에만** 허용하고, 분기·계산·전이 조건이 붙는 순간 루트 메서드로 옮긴다.
2. **불변식은 변경 메서드 안에서 검증**: 전이 조건 위반은 도메인 예외(`exception.py`의 `*Exception`)를 raise한다. **생성 시점 검증은 강제하지 않는다** — 직파싱 전제에서 생성자 검증(`__post_init__`)은 서버 데이터가 들어오는 길을 막는다. 클라가 책임질 것은 사용자가 일으키는 변경뿐이다.
3. **타 애그리거트 참조**: 서버 응답이 중첩 객체면 중첩 그대로 직파싱한다. **클라가 새로 조립하는 관계만 ID 참조 우선**이다.

```python
# domain_layer/order/order.py — 애그리거트 루트
@dataclass(frozen=True, slots=True, kw_only=True)
class Order:
    id: str
    orderer_id: str                      # 클라 조립 관계 — ID 참조 (3규칙-3)
    lines: tuple[OrderLineItem, ...]     # 종속 — 서버 중첩 그대로
    status: OrderStatus

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> Self:  # 직파싱 — 생성 검증 없음 (3규칙-2)
        return cls(
            id=json_field(data, "id", str),            # 원시 필드 — 타입이 다르면 TypeError (§3)
            orderer_id=json_field(data, "orderer_id", str),
            lines=tuple(OrderLineItem.from_json(line) for line in json_field(data, "lines", list)),
            status=OrderStatus(json_field(data, "status", str)),
        )

    @property
    def total_amount(self) -> Money:
        return reduce(lambda total, line: total.add(line.amount), self.lines, Money(amount=0))

    def cancel(self) -> Self:            # 루트 경유 변경 (3규칙-1)
        if not self.status.is_cancelable:
            raise OrderNotCancelableException()
        return replace(self, status=OrderStatus.CANCELED)
```

- **컬렉션 불변식은 정규화 클래스메서드가 정규화한다 — frozen dataclass를 유지한다**: 정렬·중복 제거·필터 같은 *컬렉션 불변식*은 기본 생성자를 그대로 열어두고 **정규화 클래스메서드**(`from_days`·`from_unordered…`)가 정규화해 반환한다. "비정렬 인스턴스를 *타입 수준에서 생성 불가*하게" 봉인하려고 `__post_init__` 검증이나 비공개 생성자 흉내로 가지 않는다 — 3규칙-2(생성 검증 비강제)대로 정규화 진입점이면 충분하고, 직파싱(`from_json`)과 `replace`가 모두 기본 생성자를 지나므로 봉인은 무의미하거나 서버 데이터 유입 길을 막는다. **entity·VO·애그리거트 루트·State를 frozen dataclass가 아닌 class로 쓰면 백스톱 MD1 위반**이다(enum·`exception.py`·common util은 MD1 비대상이라 plain 정상).

```python
# domain_layer/weekly_forecast/weekly_forecast.py — 정렬 불변식을 가진 루트
@dataclass(frozen=True, slots=True, kw_only=True)
class WeeklyForecast:
    days: tuple[DailyForecast, ...]

    @classmethod
    def from_days(cls, days: Iterable[DailyForecast]) -> Self:   # 정규화 진입점 — 생성 시 정렬
        return cls(days=tuple(sorted(days, key=lambda day: day.date)))

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> Self:
        return cls(days=tuple(DailyForecast.from_json(day) for day in json_field(data, "days", list)))
```

- **애그리거트를 팩토리로**: 새 객체 생성에 도메인 규칙이 걸리면(차단된 상점은 상품 등록 불가) 그 규칙을 아는 애그리거트의 메서드가 생성을 소유한다 — `store.create_product(...)`.
- 갱신된 애그리거트의 서버 반영은 UseCase→Repo의 일(architecture-data §3), 화면 반영은 VM의 일(architecture-state §2) — 루트 메서드는 새 인스턴스를 돌려줄 뿐 저장·표시를 모른다.

## §5. 판정 소유와 강등 — 1곳째부터 domain

dddjango-web 고유의 1급 규칙이다 (규약 §3.3 — HaffHaff 실측 drift(판정·에러 표시의 Model 밖 거주)의 직접 처방):

- **도메인 어휘로 진술되는 판정·계산은 1곳째부터 domain이 기본**이다 — "신규 기능의 판정은 항상 소비처가 1곳"이라 복제 시점 강등 규칙만으로는 빈혈에 집행자가 없다. 설계 명세는 행위 목록의 모든 수치·비교·자격 판정에 소유자(애그리거트 메서드·domain_service·specification vs VM 변환)를 항목별로 라벨링하고, **VM 소유를 주장하려면 *왜*를 적는다** (본설계 §5-2).
- **VM의 일은 변환이지 판정이 아니다**: 도메인 결과를 화면 State로 바꾸는 것(포맷·정렬·표시 여부 조립)이 변환이고, "~할 수 있는가"·"~은 얼마인가"를 계산하는 것이 판정이다. specification의 평가·조합도 Model(UseCase 이하)에서만 한다 (규약 §7.1-5).
- **강등 규칙**: 같은 도메인 판정이 **Model 밖 2곳**(VM·view·section·ui_extension·State 프로퍼티 포함)에 복제되면 `domain_service/` 또는 `specification/`으로 강등한다. 선택 기준은 규약 §3.2 문면 그대로 — **재사용·조합되는 판정 규칙이면 specification**(§7), **단발 판정·계산이면 domain_service**(§6) 또는 애그리거트 메서드 복귀.
- **시간 의존 판정은 '지금'을 인자로 받는 순수 함수다**: `def is_stale(self, now: datetime) -> bool`처럼 기준일을 *주입*받고 도메인 안에서 `datetime.now()`를 직접 부르지 않는다(domain_layer는 순수 — `django`뿐 아니라 비결정 시각도 들이지 않는다). '지금'이 실제로 필요한 자리는 application 계층의 바꿔 끼울 수 있는 인자로 격리한다. *왜* — 시각을 직접 읽는 판정은 테스트가 수행 시각에 따라 통과 여부가 달라져 회귀 안전망을 무력화하고 pre-commit에서 무관한 날 깨진다(테스트의 고정 날짜 주입은 implementation-test §5·테스트 규율은 discipline-test).
- 판정 귀속(어느 애그리거트의 일인가)의 판별 절차·반송 인용 조문은 `undecidable.md` §8 소유 — 1차 결정자(architect)와 검증자(ddd 리뷰어·discipline-reviewer)가 같은 파일을 적재한다.

## §6. 도메인 서비스 — 주어 귀속·stateless

여러 애그리거트에 걸친 도메인 로직의 자리다. **상태 없이(stateless) 로직만** 구현하며, 애그리거트는 도메인 서비스를 모른다(원전 의사결정 채택 유지):

- **애그리거트가 도메인 서비스를 파라미터로 받지 않는다** — UseCase가 도메인 서비스를 호출하고 그 **결과 값만** 애그리거트 메서드에 전달한다(`order.apply_discount(discount)` — `Order`는 `DiscountService`를 모른다).
- **주어 귀속** (규약 §3.2 — 원전에 더한 배치 규칙): 여러 애그리거트에 걸치는 순수 판정·계산은 **규칙의 주어 애그리거트의 `domain_service/`에 귀속**한다. 주어는 **그 규칙이 누구의 속성·정책인가**로 식별한다 — 등급별 할인율이면 (할인을 받는 주문이 아니라) 할인 정책의 주체인 등급·멤버십 쪽. 판정형("X가 ~할 수 있는가")과 계산형("X의 ~은 얼마인가") 모두 동일하다. **공용 위치는 없다**(`common/`에 도메인 로직 금지 — discipline-houserules §6).
- **흐름 조율은 UseCase의 일**이다 — 여러 판정·호출의 순서를 엮는 것은 도메인 서비스가 아니라 §8의 관문이 한다.
- 응용 서비스 vs 도메인 서비스 구분(원전 [A]): 애그리거트의 상태를 변경하거나 상태 값을 계산하는가 → 도메인 서비스 / 조회·저장·흐름의 조율인가 → UseCase.

## §7. Specification — 재사용·조합되는 판정

비즈니스 규칙을 독립 객체로 캡슐화하고 논리 연산으로 조합하는 패턴이다. dddjango-web 용도는 원전 3용도 중 **검증**(객체가 규칙을 만족하는가)과 **선택**(컬렉션 필터링) — 생성(빌더 전달)은 클라 수요가 없어 비강조.

```python
# domain_layer/lounge_post/specification/visible_lounge_post_specification.py
class VisibleLoungePostSpecification:
    def is_satisfied_by(self, post: LoungePost) -> bool:
        return not post.is_blinded and not post.is_deleted and post.author.is_active
```

- **풀네임 강제**: `<규칙>_specification.py` → `<규칙>Specification` — `_spec` 축약 금지(명명 사실은 discipline-houserules §4).
- 조합이 필요하면 명시 메서드로 — 연산자 오버로드(`__and__`·`__or__`·`__invert__`의 `&`·`|`·`~`)를 쓰지 않고 `and_(other)`·`or_(other)`·`not_()` 메서드 또는 단순 bool 합성으로 충분하다. 조합 계층(AndSpecification 류)은 **조합 수요가 실재할 때만** 만든다 — 규칙 하나에 추상 기반 클래스부터 깔지 않는다.
- **평가·조합은 Model(UseCase 이하)에서만** 한다 — VM이 specification을 import해 직접 평가하면 §5 위반이다.
- 강등 도착지로서의 역할: §5의 강등에서 "재사용·조합되는 판정"이 이리로 온다.

## §8. UseCase — Model의 관문

원전의 응용 서비스를 dddjango-web은 `use_case/`의 **UseCase**로 치환한다 (규약 §3.3 — dddjango의 command+query 통합). 도메인과 ViewModel 계층을 잇는 매개체이며, **비즈니스 로직을 직접 구현하지 않고 도메인 객체에 위임**한다.

**UseCase의 책임** (원전 목록의 클라 번역):
- Repo·infra service를 호출해 애그리거트를 얻는다 (트랜잭션 관리 항목은 클라에 없음 — 삭제)
- 애그리거트·도메인 서비스의 도메인 기능을 실행하고 흐름을 조율한다 (§6)
- Repo의 `Either`를 통과·조합해 반환한다 — **새 raise를 만들지 않는다** (architecture-data §3)

**UseCase가 하면 안 되는 것**:
- 도메인 로직 직접 구현(판정·계산 — §5) · 상태 보유(무상태 plain class — DI 없이 사용처가 직접 생성, 규약 §9-13)
- **UI 호출** — `django.shortcuts`·`django.http`·`django.template`·presentation·design_system import 금지. 에러 표시는 ViewModel 계층의 일(architecture-state §4). HaffHaff 실측: App(=UseCase 전신) 44개 중 36개가 ErrorDialog를 직접 호출했다 — Model→View 역류의 대표 drift.
- **도메인 개념 단위 명명** (규약 §7.1-4): UseCase는 화면이 아니라 도메인 개념으로 짓는다 — 여러 VM이 하나의 UseCase를 공유한다. `<화면>_use_case.py`가 생기면 오판 신호(판별 절차는 `undecidable.md` §8). 위임 한 줄짜리 UseCase도 정상이다 — 관문의 일관성이 우선(architecture-state §1).

```python
# application_layer/use_case/order_use_case.py — 개념 단위 (화면명 아님)
class OrderUseCase:
    def __init__(self) -> None:
        self._repo: OrderRepo = OrderRepo()  # 직접 생성 — DI 없음

    def cancel_order(self, order_id: str) -> Either[BadRequestResponse, Order]:
        found: Either[BadRequestResponse, Order] = self._repo.get_order(order_id)
        return found.map(lambda order: order.cancel())  # 도메인 위임 + Either 통과
```

## §9. 빈혈 vs 풍부 — 트랜잭션 스크립트의 함정

**빈혈 도메인 모델**(Fowler 명명 안티패턴): 데이터 클래스는 필드만 갖고, 모든 로직이 서비스(클라에선 VM·UseCase)에 사는 형태. 객체 지향의 모양에 절차적 본질 — 같은 판정이 서비스마다 복제되고, 데이터와 규칙의 거리 때문에 불변식이 새는 곳을 추적할 수 없게 된다.

- dddjango-web의 빈혈 신호: **새 판정이 그 BC의 domain에 0개이고 VM·view·State 프로퍼티·ui_extension에만 산다** — discipline-reviewer의 홀리스틱 점검이 이것을 blocker로 본다(본설계 §6-3). §4 루트 경유·§5 판정 소유가 사전 차단 장치다.
- **단, 모든 로직을 억지로 도메인에 넣지 않는다** — 원전(6.6 단순 비즈니스 로직 패턴)의 균형: 분기 한두 개의 단순 흐름에 도메인 모델 의식(ritual)을 강요하면 그것대로 과잉이다. 기준은 §5의 정의다 — **도메인 어휘로 진술되는** 판정·계산이 domain의 것이고, 단순 입출력 변환·화면 조립은 VM의 것이다. 도메인이 비어 있는 BC(다수 BC 투영 화면 등)는 골격 그대로 정상이다(discipline-houserules §3).

## §10. dddjango-web 비채택 패턴 — 음성 지식

full-DDD 관행을 들고 오는 것을 막는 명시 목록이다. **아래 패턴을 제안·도입하지 않는다** — 각각 dddjango-web의 대체 경로가 있다:

| 비채택 | *왜* | dddjango-web의 대체 |
|---|---|---|
| **도메인 이벤트** (`event/`·`*Event`·핸들러·디스패처) | 클라는 도메인 이벤트를 생성하지 않고 구독한다. HaffHaff 실물 0건, 클라엔 트랜잭션·프로세스 경계 없음 (규약 §9-15) | 교차 BC 통지는 4채널(discipline-houserules §5), 화면 동기화는 SharedState(architecture-state §5), 서버 이벤트 수신은 그 BC의 `application_layer/service/`(architecture-state §6). 이벤트형 요구가 진짜면 설계 반송 — shared_state로 위장하지 않는다 |
| **Event Sourcing·Saga** | 분산 트랜잭션·이벤트 저장은 서버 관심사 | 서버가 진실원천 — 클라는 재조회 |
| **CQRS** (Command/Query 모델 분리) | 클라 규모에서 분리 비용 > 이득 | UseCase가 command+query 통합 (규약 §3.3) |
| **Repository 인터페이스 + UoW** | 구체 Repo 직접 생성 결정에서 추상 계층은 무의미 — 행위 테스트는 Repo 인터페이스 DI가 아니라 VM 직접 생성·api_client 목으로 격리한다 (규약 §9-1) | Repo는 구체 1개 — architecture-data §1 |
| **DIP·DI 컨테이너** | 직접 생성 결정 (규약 §9-13) | UseCase·Repo·DataSource는 사용처가 직접 생성 |
| **핵사고날(포트·어댑터)** | `port/` 없음 (규약 §9-0) | 계층 import 매트릭스(discipline-houserules §5)가 경계 |
| **ACL·컨텍스트 맵(OHS 등)** | 조직 간 패턴 — 클라 단일 팀, `acl/` 없음 (규약 §9-3) | 교차 BC는 4채널 |
| **Data Mapper·DTO** | 직파싱 결정 (규약 §9-2) | 엔티티가 서버 JSON 직접 파싱 — architecture-data §4 |
| **증류·Event Storming·팀 토폴로지** | 조직 전략·워크숍 기법 — 기능 추가 파이프라인 범위 밖 | G0 스코프·G1 설계가 그 자리 |
| **대규모 구조** (Evans Large-Scale Structure — 시스템 은유·책임 계층 등) | 전사 시스템 조직 패턴 — 단일 web 범위 밖 | 표준 트리·BC 골격(discipline-houserules §1)이 dddjango-web의 전체 구조 |
| **마이크로서비스식 BC 분리** (BC별 패키지·배포 분리) | 클라 단일 Django 앱 — 배포 경계가 없다 | BC는 `application/<bc>/`(또는 `application/<area>/<bc>/`) 폴더 경계 + 4채널로 충분 |

- 이 표는 "몰라서 안 쓰는 것"과 "알고 안 쓰는 것"을 가르는 음성 지식이다 — 리뷰에서 위 패턴이 제안되면 이 절을 인용해 반송한다.

## §11. 핵심 요약

| 구분 | 규칙 | 한 줄 |
|---|---|---|
| 전략 | BC·유비쿼터스 언어 | BC = `application/<bc>/`(area 그루핑 시 `application/<area>/<bc>/`), 같은 개념 같은 철자, 교차 BC는 4채널 (§2) |
| 전술 | 값 객체 | frozen dataclass 불변 + 도메인 연산 메서드 — 호출부가 원시값 산수를 하지 않는다 (§3) |
| 전술 | 엔티티 | 애그리거트의 일부로만, 서버 JSON 직파싱 (§3) |
| 전술 | 애그리거트 | 조건·계산·전이는 루트 메서드(새 인스턴스 반환), 검증은 변경 메서드 안, 생성 검증 비강제 (§4) |
| 전술 | 판정 소유 | 도메인 어휘 판정은 1곳째부터 domain — VM은 변환만, Model 밖 2곳 복제 시 강등 (§5) |
| 전술 | 도메인 서비스 | 주어 애그리거트에 귀속·stateless·애그리거트는 서비스를 모름 (§6) |
| 전술 | Specification | 재사용·조합 판정, 풀네임, Model에서만 평가 (§7) |
| 전술 | UseCase | Model의 관문 — 도메인 위임·Either 통과·UI 금지·개념 단위 명명 (§8) |
| 경계 | 빈혈 차단 | 새 판정이 domain 0개 + VM·view에만 = blocker (§9) |
| 경계 | 비채택 | 이벤트·CQRS·ES·Saga·Repo 인터페이스·DIP·핵사고날·ACL·DTO — 제안하지 않는다 (§10) |
