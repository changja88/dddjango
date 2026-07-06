# 발행 이벤트 discriminator 규약 설계 — birth-enum: 1종째부터 StrEnum + Literal 파생

- 작성: 2026-07-07 · 상태: **확정 (2026-07-07 사용자 승인·구현 완료)** — 계획 `workspace/plan/2026-07-07-event-discriminator-birth-enum-plan.md`
- 범위: 우리 BC가 **발행하는 이벤트 봉투(태그드 유니온)의 discriminator 필드** 표기 규약. DR-60 상수 승격 규약의 "분기·판정할 때만 승격" 판정을 이 위치에 한해 탄생 시점으로 앞당긴다. 결정적 백스톱 비채택(§5) — **게이트 수 18 유지**.
- 발단: 적용 프로젝트의 `event_type: Literal["parent_safe_alert"] = "parent_safe_alert"`가 DR-60 비대상(§3.3 Literal 허용 + §3.5 경계-로컬 고정)임을 확인 → "확장이 구조적으로 전제된 discriminator 축은 1종째부터 enum" 논의로 A안(birth-enum) 확정.
- 조사: 코퍼스 전수 조사 + 외부 권위 8건 + 기술 검증 4건 실측(pydantic 2.13.4 · django-ninja 1.6.2/Django 6.0.6 · mypy --strict). 대화 추천 대비 조정 1건: enum 배치를 "봉투 union 모듈 동거"에서 **domain_layer 이벤트 슬롯 소유**로 변경(§3.1 — outbox가 infra라 경계-로컬 배치는 infra→presentation 역방향 import를 강제, 계층 규칙 위반).

---

## §1 배경·문제

DR-60 체계에서 단일 멤버 Literal discriminator는 규약상 정답이었다(오타는 mypy가 정적으로 잡고, 경계-로컬 Literal은 §3.5가 처방). 남는 문제는 세 가지다:

1. **확장 시점 승격은 판단형 규칙이다.** "분기가 생겼나? 승격할 때인가?"를 확장하는 코더에게 요구하는데, 판단형 규칙은 LLM 준수율이 낮다는 것이 이 코퍼스의 자체 결론(DR-60 §5 — 2곳 임계 채택 근거와 동일). 승격을 안 해도 아무것도 안 깨져 조용히 표류하고, 이벤트가 늘수록 승격 비용이 커져 계속 미뤄진다.
2. **운영 요구: 발행 이벤트 종류의 단일 등록부.** "이 BC가 발행하는 이벤트가 전부 몇 종인가"를 한 곳에서 답할 수 있어야 한다(§3.1 집합 단위 타입 원칙의 동형).
3. **이 코퍼스의 아키텍처에서 조건은 사실상 항상 참이다.** outbox 패턴(implementation-django §16.5)이 `event_type` DB 컬럼 저장을 표준으로 깔고 있어, 발행 이벤트의 event_type은 기본적으로 §3.1 앵커(저장·계약 노출, 이어서 릴레이 필터)에 도달한다. "분기 생기면 승격"은 판정만 확장 시점으로 미뤄둔 것이었다.

**실패 모드 비교(A안 채택 논거).** birth-enum의 실패(확장 시 enum 갱신 누락)는 ① 덜 일어나고(확장은 1호 이벤트 클래스 복제로 진행 — 템플릿에 파생 표기가 박혀 있음) ② 기계적으로 잡히고(§3.3 동기 계약 테스트) ③ 싸게 고쳐진다(멤버 1줄). 조건부 승격의 실패(승격 누락)는 판단을 요구하고, 신호가 없고, 비용이 누적된다. 덜 일어나고·기계적으로 잡히고·싸게 고쳐지는 실패를 고른다. 부수 이득: "이 값이 나중에 판단 재료로 쓰일까"라는 **예측 문제**가 "쓰이는 순간 기존 규칙(§3.2 소비 규율·18번 게이트)이 잡는다"는 **반응 문제**로 바뀐다.

## §2 조사 근거 (요약)

1. **Pydantic이 정확히 이 표기를 테스트로 보증한다.** 공식 테스트 스위트의 `test_discriminated_union_model_dump_with_nested_class`가 `type: Literal[SomeEnum.DOG] = SomeEnum.DOG` 형태를 검증하고 JSON dump 시 plain str 반환을 고정한다([tests/test_discriminated_union.py](https://github.com/pydantic/pydantic/blob/main/tests/test_discriminated_union.py)). 평(non-Literal) Enum 필드는 discriminator로 쓸 수 없다([#10614](https://github.com/pydantic/pydantic/issues/10614) — "just use Literal on the type in the child classes") — **enum을 쓰려면 Literal 파생이 유일 경로**. [PEP 586](https://peps.python.org/pep-0586/)이 enum 멤버를 Literal의 적법 매개변수로 명시("Literal may be parameterized with … Enum values").
2. **wire 계약은 바뀌지 않는다.** Pydantic `GenerateJsonSchema.literal_schema`는 enum 멤버를 `.value`로 평탄화해 단일 값을 `const`로 렌더 — `Literal[EventType.X]`와 `Literal["x"]`의 JSON schema가 동일하다([json_schema.py](https://github.com/pydantic/pydantic/blob/main/pydantic/json_schema.py)). **실측 확인**(ninja 1.6.2/Django 6.0.6): OpenAPI에 `oneOf` + `discriminator.mapping` + `const` 정상 렌더, enum 파생 전후 동일. 주의 1건: 페이지네이션 응답에 discriminated union을 직접 조합하면 OpenAPI 렌더 버그([ninja #1308](https://github.com/vitalik/django-ninja/issues/1308) open).
3. **이벤트 타입 문자열은 계약이다.** [CloudEvents](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md) `type`: producer 정의·라우팅/정책 판단에 사용("used for routing, observability, policy enforcement")·비호환 변경 시 값 수정이 아니라 **새 type 발행**([Primer](https://github.com/cloudevents/spec/blob/main/cloudevents/primer.md) — "should generally change"; 명세의 MUST가 아니라 소비자 기대 서술임을 구분). Greg Young 이벤트 버저닝: "A new version of an event must be convertible from the old version. If not, it is not a new version but a new event", rename 금지([노트](https://github.com/benatespina/book-notes/blob/master/versioning_in_an_event_sourced_system.md)·[InfoQ](https://www.infoq.com/news/2017/07/versioning-event-sourcing/); 1차 출전 leanpub 본문은 접근 실패).
4. **append-only는 생태계 교차 규범이다.** [protobuf](https://protobuf.dev/programming-guides/proto3/): "Adding additional values to an enum is safe", 삭제·번호 재사용은 "data corruption, privacy bugs"급 위험(reserved 규정). 부가 발견: 발행자의 멤버 추가는 소비자의 완전 match를 깨므로("a compilation break for any code with an exhaustive switch") 소비자 미지 값 정책을 짝으로 규정한다(§3.4).
5. **완전성 검사는 양쪽 동등.** mypy(`--enable-error-code exhaustive-match`)·pyright(`reportMatchNotExhaustive`) 모두 enum과 union의 완전성 검사를 나란히 지원 — StrEnum 채택이 불리하지 않고, 봉투 union(클래스 match) + enum(값 match) 두 층 모두 검사 가능.
6. **반대 관점 검토(TS 진영).** TS의 enum 회피 논거는 컴파일 모델 고유 사정(enum이 런타임 산물·TS 5.8 `--erasableSyntaxOnly` 금지 목록·const enum 인라이닝 충돌)이다. Python에 이식되는 유일 논거인 nominal 타이핑(같은 값이라도 다른 enum과 비호환)은 발행 계약에서 오히려 **원하는 속성**(단일 출처 강제·임의 문자열 유입 차단) — 원용 불가로 판정.
7. **기술 검증 4/4 통과(실측).** ① `Literal[EventType.X]` 디스패치·직렬화(평문 str)·오타 입력 ValidationError 거부 ② ninja OpenAPI 노출 ③ 동기 계약 테스트 표준형의 드리프트 검출(enum에만 멤버 추가 시 정확히 검출) ④ mypy --strict: enum 파생 기본값 불일치·str 오타·assert_never 누락 3오류 전부 정적 검출. **정직한 한계**: 오타 방어력은 맨 Literal도 동일하다 — 이 규약의 순증 가치는 오타가 아니라 **등록부 단일화·소비 규율 접속(outbox filter 등)·파생 방향 고정**이다.
8. **코퍼스 정합.** houserules: BC 내부 enum은 domain_layer 소유, 도메인 이벤트 슬롯 `domain_layer/<aggregate>/event/` 기존재. 개정 대상: architecture-ddd IntegrationEvent 예제의 `event_type: str`, implementation-django §16.5 outbox `event_type = CharField(...)`. 기존 규약과 충돌 없음 — DR-60 계층 소유·published language·§15.4와 전부 접속 가능.

## §3 규칙 (확정)

### §3.0 판정 기준 — 위치 기반, 이름 비대상

> **우리 BC가 발행하는 이벤트 봉투(태그드 유니온)의 discriminator 필드는 이벤트 종류가 1종일 때부터 domain StrEnum으로 선언하고, 각 이벤트 클래스의 태그는 `Literal[EventType.X] = EventType.X`로 파생한다.**

- 트리거는 **위치(발행 봉투의 discriminator)**다. "이름이 type/kind"는 여전히 비트리거(DR-60 §3.1 유지) — pass-through 상류 type 필드·데이터소스 BC 면제 그대로.
- DR-60 "분기·판정할 때만"과의 관계: 예외 신설이 아니라 **판정의 선행 확정**이다. 이 코퍼스의 발행 이벤트는 outbox 저장(§3.1 저장·계약 노출 앵커)에 기본 도달하므로, 조건 판정을 확장 시점으로 미루지 않고 탄생 시점에 확정한다. 이후 filter·라우팅·비교가 생기면 기존 §3.2 소비 규율과 18번 게이트가 자동 적용된다.

### §3.1 표기·배치

- **enum 배치**: 발행 BC **domain_layer의 이벤트 슬롯**(`domain_layer/<aggregate>/event/event_type.py`; BC 수준 봉투가 여러 애그리거트 이벤트를 묶으면 domain_layer 공용 event 슬롯). BC 내부 소유 — 다른 BC의 직접 import 금지(published language 수용, DR-60 §3.4 그대로). 경계-로컬 배치를 쓰지 않는 이유: outbox 리포지토리(infra)가 enum을 소비해야 하는데 enum이 presentation 봉투 모듈에 있으면 infra→presentation 역방향 import가 강제된다(houserules 계층 규칙 위반). domain 배치면 infra/presentation→domain 허용 방향으로 전원 접근 가능.
- **필드 파생**: `event_type: Literal[EventType.PARENT_SAFE_ALERT] = EventType.PARENT_SAFE_ALERT`. 평 Enum 필드는 discriminator 불가(§2-1) — Literal 파생이 유일 경로.
- **봉투 union**: `Event = Annotated[Union[...], Field(discriminator="event_type")]` — 봉투 Schema가 사는 경계 모듈에 union alias를 함께 정의.
- **발견 가능성 3장치**: ① 1호 이벤트 클래스의 파생 표기 자체가 템플릿(확장은 복제로 진행되므로 enum 패턴이 전파됨) ② union alias — 갱신 없으면 디스패치가 동작하지 않음(런타임 강제 발견) ③ §3.3 동기 계약 테스트(결정적 검출).
- **OpenAPI**: enum 파생 전후 `const` 렌더 동일(§2-2 실측) — "계약 안정성 때문에 맨 Literal"이라는 논거는 이 위치에서 성립하지 않는다. 단 봉투 union을 페이지네이션 응답에 직접 조합하지 않는다(ninja #1308 open).

### §3.2 제외 — 버전 태그 (짝 조항)

- `payload_schema_version` 등 **스키마 버전 태그는 discriminator와 형태가 동일하지만(단일 멤버 Literal + 같은 기본값) 리터럴 동결을 유지한다.** 근거: 버전 태그는 발행 순간 동결되는 계약 표식이다 — 비호환 변경은 기존 값 수정이 아니라 **새 버전 리터럴 추가 + upcasting**(Greg Young, §2-3)이고, enum화는 "수정 가능한 중앙 등록부"라는 잘못된 어포던스를 만든다.
- 유사 제외: 상류 소유 이벤트를 중계만 하는 **소비 측** 스키마의 태그(소비 BC는 published language 수용으로 자기 값을 따로 정의 — 발행 BC의 enum을 import하지 않는다).

### §3.3 동기 계약 테스트 (세트 — 선택 아님)

- **"봉투 union 멤버들의 태그 집합 == EventType 멤버 집합"** 단언 테스트 1개를 발행 BC의 계약 테스트에 포함한다. birth-enum의 유일한 실패 모드(확장 시 enum·union 드리프트)를 결정적 검출로 바꾸는 장치다(실측: enum에만 멤버를 추가한 드리프트를 정확히 검출).
- 표준형(검증 완료): `typing.get_args`로 union 멤버 각각의 discriminator annotation에서 태그를 수집해 `{str(m) for m in EventType}`와 비교.
- 이 테스트는 **구조 동기 검증**이지 외부 계약 검증이 아니므로 implementation-test §15.4(자기참조 오라클 금지)와 충돌하지 않는다 — 발행 payload의 실제 문자열을 검증하는 외부 계약 테스트의 기댓값은 여전히 리터럴로 고정한다.

### §3.4 수명 — append-only

- EventType 멤버는 **추가만 허용. 값 변경·삭제 금지**(발행된 메시지·outbox 행·소비자 계약에 옛 값이 살아 있다 — protobuf reserved·마이그레이션 historical value 규율과 동형). 이벤트 폐기는 멤버 삭제가 아니라 발행 중단 + 주석 표기.
- 스키마 비호환 변경은 새 버전 리터럴(필요시 새 event_type 멤버) 추가로 처리한다. 폐기된 값의 재사용 금지.
- **소비자 측 짝 규칙**: 미지 event_type 처리 방침(UNKNOWN 폴백 또는 명시적 거부)을 함께 정한다(DR-60 §3.1 열린 집합 조항 준용) — 발행자의 멤버 추가가 소비자의 완전 match를 깨는 문제(§2-4)의 대응.

### §3.5 소비 규율 접속

enum이 태어나는 순간 DR-60 §3.2가 그대로 적용된다: outbox filter·라우팅·비교는 심볼로, ORM `default=`·마이그레이션 경계는 `.value` 평탄화, 테스트 assert의 외부 계약 기댓값은 리터럴(arrange는 심볼). 신설 판정 없음 — 기존 규율에 접속만 한다.

## §4 반영 위치 (구현 개요)

정본 `dddjango/` 수정 후 `codex-dddjango/` 미러 동기(final.md는 corpus_mirror_sync `--write` 자동, SKILL.md·agents 수동). 집행은 **reviewer 의미 점검 + 문서 규약 + 프로젝트 내 동기 계약 테스트** — 결정적 백스톱 없음(§5).

| # | 대상 | 변경 |
|---|---|---|
| 1 | `architecture-ddd` references/final.md §3.7 | birth-enum 규칙 본문(§3.0 판정·§3.4 수명) 신설 + IntegrationEvent 예제 `event_type: str` → StrEnum+Literal 파생으로 교체. §2.5 말미에 "발행 봉투 discriminator enum도 BC 내부 소유·published language 동일 원리" 1항 |
| 2 | `implementation-django-ninja` references/final.md §3.1 | 봉투 union 표기(`Annotated[Union, Field(discriminator=)]`)·`Literal[EventType.X]` 파생 예제·버전 태그 제외·페이지네이션 조합 주의(#1308) |
| 3 | `discipline-cleancode` references/final.md §2.14 | 승격 기준에 위치 기반 1불릿("발행 이벤트 discriminator는 1종째부터 — §3.0") + 허용 목록 `Literal[...]` 항목에 경계 병기(발행 봉투 discriminator는 enum 파생이 규율·버전 태그는 리터럴 동결) |
| 4 | `implementation-test` references/final.md §15.4 인근 | 동기 계약 테스트 표준형 신설 + §15.4와의 경계(구조 동기 vs 외부 계약) 명시 |
| 5 | `implementation-django` references/final.md §16.5 | outbox `event_type` 컬럼에 "domain EventType에서 파생·filter는 심볼·`.value` 평탄화" 보강 |
| 6 | `discipline-houserules` references/final.md | domain_layer event 슬롯에 `event_type.py` 배치 관례 1줄 |
| 7 | `dddjango/agents/discipline-reviewer.md` + codex 미러 | 상수 승격 불릿에 ⑤ 신설: 발행 봉투 discriminator가 맨 문자열 Literal이면 **important**(버전 태그·소비측 중계 스키마·상류 pass-through는 제외). 거짓지적 방지 "Literal로 잠긴 인자 자리" 항목에 이 예외를 명시(발행 봉투 discriminator만 예외적으로 잡는다) |
| 8 | SKILL.md 라우팅 | architecture-ddd·implementation-django-ninja·discipline-cleancode·implementation-test 4종 |
| 9 | `codex-dddjango/` 미러 동기 | final.md 자동(`--write`)·SKILL.md/agents 수동 후 diff 검증 |

검증: `corpus_mirror_sync --check` + `claude plugin validate dddjango --strict` + 변경 diff 리뷰. 백스톱 신설이 없으므로 발화 매트릭스 불요. reviewer 신설 항목의 라이브 발화 관측은 후속(DEVLOG 열린 항목 — DR-60과 동형).

## §5 집행 설계와 비채택 결정

- **결정적 백스톱 비채택.** discriminator와 버전 태그는 AST 형태가 동일하다(단일 멤버 str Literal + 동일 기본값) — 형태 판정으로는 FP가 불가피해 이 저장소의 백스톱 채택 기준(FP≈0)에 미달. "발행 봉투인가"는 의미 판정이므로 reviewer가 전담한다(db_table "존재는 백스톱·값 형태는 reviewer" 분업과 동형). **게이트 수 18 유지.**
- **이름 기반 트리거 비채택(재확인).** DR-60 §3.1 "이름이 type/kind라는 이유로 승격하지 않는다" 유지 — 본 규약은 발행 봉투라는 위치로만 판정한다.
- **값 형식 규정 비채택.** CloudEvents는 reverse-DNS 접두를 SHOULD로 권고하나 값 형식은 프로젝트 계약 소관 — 이 규약은 표기(enum vs 리터럴)만 소유한다. 기존 프로젝트의 짧은 값(`parent_safe_alert`)은 grandfather.
- **소급 적용 비채택.** touched-only/grandfather 관례 그대로 — 기존 코드는 해당 봉투를 만지는 슬라이스에서 전환한다.

## §6 스코프 확인

단일 구현 단위로 적절: 스킬 문서 6종 + SKILL.md 라우팅 4종 + reviewer + 미러 동기. 백스톱·게이트 카운트 변경 없음(README·commands 카운트 갱신 불요 — DR-60과의 차이점).
