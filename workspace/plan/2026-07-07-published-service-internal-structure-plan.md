# published_service 내부 구조 규약 구현 계획 (적대 리뷰 반영판 v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.
> v1 대비: 3축 적대 리뷰(모순 14건 A~N·과적합 8건·실효성 8건) 중재 반영 — 백스톱 **동시 채택 번복**(v1의 "라이브 관측 후 후속"은 db_table·choices 전례 인용 오류 — 둘 다 규약과 같은 커밋 채택, DR-60이 정확히 이 초안 형태를 번복한 전례), birth-enum 카브아웃 3곳(모순-H), transient 짝 조항(모순-I), §0 오귀속 제거(모순-E·과적합-3), design-architect 레인(실효-2), 이주 조문(실효-5), 데이터소스 BC 경로(과적합-1e), reviewer 불릿 보수(과적합-8·실효-4), :144 개정 편입(모순-C), §4 개정(모순-M·과적합-4), 응용 반환 DTO 슬롯(실효-6), codex SKILL 미러(모순-A·실효-8).

**Goal:** ① dddjango 표준에 published_service **내부 구조 규약**(서비스 1차·contract 3파일·시그니처 3연조·제공 측 예외 번역·contract 무의존·이주)을 신설하고 구 `read.py`/`write.py` 규약을 대체. ② `check-context-isolation.py` 2슬라이스 확장(동시 채택). ③ 외부 프로젝트(delivery 앱) 적용 스펙.

**Architecture:** 정본 `dddjango/` 수정 → final.md는 `corpus_mirror_sync --write` 자동 전파, SKILL.md·agents·scripts는 수동 미러(byte-id). 집행 4층: 표준(final.md) + 생산자(design-architect) + reviewer 의미 레인 + 백스톱 확장(FP≈0 직접형 2슬라이스).

## Global Constraints

- 기존 문체·`§` 상호참조 준수. 개정 일자(2026-07-07) 명기.
- 백스톱은 **신설 아닌 확장**(DR-55/56 "확장>신설") — 게이트 카운트 18종 불변, README/commands 카운트 갱신 불요.
- 커밋은 전체 검증 후 단일 feat 커밋(사용자 확인 후).

---

## Part A — 플러그인 표준 개정

### Task A1: discipline-houserules final.md — published_service 절 전면 개정

**Files:** `dddjango/skills/discipline-houserules/references/final.md`

- [ ] Step 1: :72 트리 한 줄 교체 → `├── published_service/                  # 컨텍스트 간 OHS — 서비스(개념) 1차·contract 계약 패키지 (아래 "컨텍스트 간 통신")`
- [ ] Step 2: :139-142 코드 블록 교체

```
application/<app>/published_service/     # 이 앱이 외부 컨텍스트에 노출하는 OHS
└── <service>_service/                   # 서비스(개념) 1차 — 무조건 폴더 (예: sms_service/)
    ├── <service>_service.py             # 행위 — 공개 모듈 함수만 (application_layer command/query에 위임)
    └── contract/                        # 계약 — 소비자가 타입으로 결합하는 전부
        ├── request_contract.py          # 입력 DTO
        ├── response_contract.py         # 결과 DTO
        └── exception_contract.py        # published 예외 — 서비스 base + 도메인 예외 번역 타깃
```

- [ ] Step 3: :144 말미 개정 — "…Published Language(DTO)를 권장한다(…)" → "…Published Language(DTO)로 한다 — 반환 계약은 아래 OHS 시그니처 계약(3연조)이 규정한다(presentation `schema_out`과 동일한 모델 누수 방어)." (모순-C: 권장↔강제 수위 충돌 해소)
- [ ] Step 4: :144 문단 뒤 신설 조문 5개 삽입 (아래 확정 문안 — 리뷰 반영 완료본)

```markdown
**OHS 내부 구조 — 서비스(개념) 1차·계약 3파일 (2026-07-07 개정: 구 `read.py`/`write.py` 종류 1차 폐지).** `published_service/` 바로 아래에는 서비스 폴더(`<service>_service/`)만 온다 — 평면 `.py` 모듈을 두지 않는다(`__init__.py` 제외). 각 서비스는 행위 모듈(`<service>_service.py`)과 계약 패키지(`contract/`)로 구성하고, contract 안은 `request_contract.py`·`response_contract.py`·`exception_contract.py` 3파일로 고정한다. 이 3파일 고정은 §0 골격 불변식(폴더·`__init__.py` 규율)의 연장이 아니라 **OHS 고유 규칙**이다 — 계약 표면을 결정적 형태로 고정해 presence 점검과 소비자의 예측 가능한 import를 성립시키고, 빈 `exception_contract.py`는 "선언된 예외만 던진다"(아래 3연조)와 결합해 도메인 예외 무번역 전파를 형태로 막는다. 서비스 폴더를 만들 때 3파일을 함께 생성하며 내용 없는 request/response는 빈 모듈로 둔다(published 예외를 노출하는 서비스의 exception_contract는 base 포함 최소 구성 — 아래 예외 번역). 구 read/write 축은 위임 대상(application_layer의 command/query)이 이미 표현하므로 표면에서 중복하지 않는다. 서비스 폴더 자체는 개념이므로 실제 노출할 서비스가 있을 때만 만들고(§0-3 '개념 1차는 개념 식별 시'와 동형), 계약 모듈이 비대해지면 같은 이름의 디렉터리로 승격한다. `__init__.py`는 전부 빈 패키지로 유지하고 재노출 큐레이션을 하지 않는다 — 공개 표면의 단일 출처는 각 모듈 자신이다(소비자는 `…published_service.<service>_service.<service>_service`의 함수와 `…contract.<kind>_contract`의 타입을 모듈 경로로 직접 import). 비동기 통합(이벤트 구독·outbox)은 이 규약 밖이다 — 통합 스타일 선택(§2 설계 선택)대로 도메인 이벤트 채널로 라우팅한다.

**OHS 시그니처 계약(3연조).** `<service>_service.py`의 공개 표면은 모듈 수준 함수만이다(공개 클래스 금지 — 조립은 composition_root 위임이라 상태가 없다). 각 공개 함수는 ① 인자로 그 연산의 request contract **1개**만 받고(0개는 위임 대상이 입력 없는 Query 인터랙터일 때만 — 커맨드 위임은 항상 1개; 맨 스칼라·다중 인자 금지, 앞선 호출의 response contract가 후속 입력에 필요하면 request contract의 필드로 품는다) ② response contract(또는 `None`)만 반환하며 ③ exception_contract에 선언된 예외만 던진다(transient 인프라 예외는 예외 — 아래 번역 조문). 단일-요청-객체 형태는 인터랙터 `execute(request)` 규약(§2 설계 선택·§3 표)의 OHS 판이다 — published 경계는 진화 압력이 가장 큰 표면이라 필드 추가로 흡수 가능한 계약 객체를 1개째부터 강제한다(확장-시점 승격은 판단형 규칙이라 표류 — birth-enum과 동형 논리). 함수 본문은 composition_root 팩토리를 호출해 application_layer 인터랙터에 위임하고 계약↔응용 DTO 변환(경계 언랩)만 한다 — 판정·비즈니스 로직·ORM 직접 질의 금지. **published 계약 타입을 application_layer 안으로 관통시키지 않는다**(응용 계층은 domain에만 의존 — §3 표 응용 계층 헤더·`architecture-ddd` §6.1). OHS가 필드 단위로 언랩·재조립하며, 응용의 반환 DTO는 `<feature>/dto/<usecase>_result.py`에 둔다(§3 표 dto/ 항목 개정 참조). 데이터소스 BC가 OHS를 노출하면 그 연산은 이 BC가 소유하는 조회 유스케이스가 된 것이다 — 그 시점에 Query 인터랙터와 composition_root를 만든다(§0-3 '개념 1차는 개념 식별 시'·조립 규칙 'application 로직 가진 BC는 반드시'의 적용이지 면제 신설이 아니다). 공개 함수 docstring은 그 함수가 던질 수 있는 exception_contract 예외 전수 목록의 앵커다(`discipline-cleancode` §4.2 공개 API 독스트링 필수의 OHS 적용 — ACL 협력 포트 앵커(아래 소비 측)와 대칭).

**제공 측 예외 번역 — exception_contract가 단일 출처.** OHS 함수는 도메인·응용 예외를 exception_contract에 선언된 published 예외로 번역해 던진다 — 도메인 예외의 raw 전파·재노출(`__all__` 포함) 금지. 재노출하면 소비 BC가 우리 `domain_layer` 타입 정체성에 결합해 §2.5 published language 경계가 무력화된다(소비 측 ACL 조문의 "동일 의미면 명시적 재노출"은 소비 측 ACL이 *업스트림 예외*를 포트 선언에 명시하고 그대로 통과시키는 허용이지, 제공 측이 자기 도메인 타입을 공개 계약에 올리는 면허가 아니다). exception_contract의 모든 예외는 서비스당 1개의 published base 예외를 상속한다(base 자신 제외·중간층 경유 전이 상속 허용 — `implementation-python` §15.2 최상위 예외, 소비자의 가족 단위 catch). 번역은 알려진 구체 예외의 전수 명시 매핑으로 하고, 폴백을 둘 경우 도메인·응용 예외 base 단위 catch에 한정하며(`except Exception` 광범위 포괄 금지 — 프로그래밍 오류는 published로 위장하지 않고 raw 전파가 정상) 폴백 published 타입은 retryable 의미로 위장하지 않는 중립 타입으로 정한다(`implementation-django-ninja` §6.2 동방향). **transient 짝 조항**: transient 인프라 예외(`OperationalError` 등 재시도성 변종)는 published 예외로 감싸지 않는다 — raw 통과시켜 소비 측 경계의 단일 변환점(recognizer)이 처리하게 한다(위 소비 측 ACL의 transient 위장 금지와 동형; published로 감싸면 실 메시지·`__cause__` recognizer 사각 → 영구장애 오분류·500 누수). 재시도 소진을 스스로 판정한 경우의 규율(도메인 transient-마커 타입·`raise … from` 보존)은 소비 측 조문을 따른다.

**contract 무의존 — import 방향.** contract 모듈은 domain·application·infra 어느 계층도 import하지 않는다(표준 라이브러리·같은 서비스 contract만) — 소비 BC의 계약 import가 무거운 그래프(Django 앱 로딩)를 끌고 오지 않게 하는 격리이고, 도메인 enum을 계약 필드 타입으로 노출하면 소비 BC가 우리 내부 enum에 결합한다(`architecture-ddd` §2.5 — BC 간 연결은 계약 타입 또는 wire value). **birth-enum 짝**: 우리 BC가 발행하는 이벤트 봉투를 OHS 계약으로도 노출할 때의 discriminator 자리는 이 격리가 우선한다 — domain enum 파생(`Literal[EventType.X]`) 대신 wire `Literal["…"]`을 유지하고 union-enum 동기 테스트(`implementation-test` §15.5)로 드리프트를 방어한다(`discipline-cleancode` §2.14 허용 목록 짝 조항의 명시 예외 — cleancode 쪽 카브아웃과 세트). contract 내부는 `request_contract → response_contract` 단방향만 허용(영수증류 response를 후속 request가 필드로 품는 경우), `exception_contract`는 계약 내 어느 모듈도 import하지 않는다 — 멱등 재생이 기존 결과를 알려야 하면 예외에 결과 객체를 싣지 말고 response contract의 재생 표기(`replayed` 류)로 반환한다. 같은 격리 이유로 `<service>_service.py`의 composition_root import는 함수 내부 지연 import를 허용한다(사유 주석 1줄).

**이주 — 구 read/write·평면 OHS.** 구 구조는 '확립된 규약'으로서 신 규약 적용을 영구 면제하지 않는다: **새 서비스·새 공개 함수는 신 구조로만 추가한다**(구 `read.py`/`write.py`에 표면을 늘리지 않는다). 기존 함수의 국소 수정은 미이주로 허용한다 — OHS 이주는 타 BC 소비자의 import 경로를 깨는 파괴적 변경이므로 전면 이주는 별도 스코프(G1 트레이드오프)로 올리고, 이주 시 구 모듈은 신 구조를 재노출하는 호환 심(deprecation 주석 명기)으로 1단계 유지한 뒤 소비자 갱신과 함께 제거한다(재노출 금지 조문의 유일한 한시 예외).
```

- [ ] Step 5: :194 dto/ 행 ※주 개정 — `※응답 DTO 아님(응답=presentation schema_out)` → `※HTTP 응답 DTO 아님(응답=presentation schema_out); OHS 등 presentation 밖 반환이 필요한 유스케이스의 반환 DTO는 <usecase>_result.py로 여기 둔다` (실효-6(3): 응용 반환 DTO 슬롯)
- [ ] Step 6: :217 §3 표 행 교체 → `| <app>/published_service/ | 컨텍스트 간 **OHS**(다른 앱에 노출, §2.5/§6.7) | <service>_service/(서비스 1차) → <service>_service.py(공개 함수)·contract/{request,response,exception}_contract.py. 다른 앱은 **이것만** import(모듈 경로 직접 — __init__ 재노출 없음) |`
- [ ] Step 7: §4 개정 2건 — (a) :253 `'_service.py'는 오케스트레이션 service/에만` → `'_service.py'는 오케스트레이션 service/와 published_service의 서비스 모듈(<service>_service.py)에만` (과적합-4) (b) §4에 OHS 명명 항목 추가: 폴더 `<service>_service/`·모듈 `<service>_service.py`·계약 3파일 고정명·published base `<Service>PublishedError`; 계약 클래스의 버전 접미(V1 등)는 프로젝트 재량(표준 비강제 — 모순-M V1 무근거 해소)
- [ ] Step 8: 검증 — `grep -n "read\.py\|write\.py" final.md` 잔존이 폐지 표기·이주 조문뿐(모순-N 단서); `grep -n "3연조\|exception_contract\|transient 짝" final.md`

### Task A2: discipline-houserules SKILL.md — 상시 캐리어 (codex 미러 포함)

**Files:** `dddjango/skills/discipline-houserules/SKILL.md`, `codex-dddjango/skills/discipline-houserules/SKILL.md` (모순-A·실효-8)

- [ ] Step 1: :29 요약 병기 — `…OHS(published_service/) 우선` 뒤: `(내부는 서비스 1차 <service>_service/·contract 3파일 — 공개 함수는 request contract 1개→response contract(또는 None)·exception_contract 번역 예외만(3연조), 도메인 예외 재노출·published 계약 타입의 application_layer 관통 금지)` (실효-1: 관통 금지를 상시 캐리어에)
- [ ] Step 2: §1.1 단서 추가(데이터소스 전례 동형) — `이번 작업이 touched한 published_service의 구 read/write·평면 구조는 새 표면 추가에 대한 '확립된 규약'으로 보지 않는다(기존 함수 국소 수정은 미이주 허용 — references/final.md §2 이주 조문)` (실효-1·5)
- [ ] Step 3: 안티패턴 불릿 추가 — `**published_service 평면 .py·도메인 예외 재노출·계약 관통** — OHS는 서비스 폴더 없이 평면 모듈을 두지 않고(__init__.py 제외), 도메인 예외를 번역 없이 전파·재노출하지 않으며, published 계약 타입을 application_layer로 관통시키지 않는다(references/final.md §2).`
- [ ] Step 4: codex 쪽 SKILL.md에 동일 반영, 검증 양쪽 body diff 0

### Task A3: discipline-reviewer 불릿 신설 + 기존 렌즈 카브아웃 (codex 미러 포함)

**Files:** `dddjango/agents/discipline-reviewer.md`, `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`

- [ ] Step 1: 신설 불릿(확정 문안 — 절차·배타·carve-out 반영: 실효-4·과적합-8)

```markdown
- **published_service 표면(3연조·예외 번역·관통)**: ①②③⑤는 이번 작업이 touched한 OHS(`published_service/` 하위)를 보고, ④는 touched한 그 BC의 `application_layer`·`domain_layer`·`infra_layer`를 본다(§1.1 — 구 read/write의 untouched 잔존은 면제, 새 표면 추가는 신 구조 강제). ① `published_service/` 직하 평면 `.py`(`__init__.py` 제외)·서비스 폴더 부재·contract 3파일 미비 → **important**(houserules §2 OHS 내부 구조; 구조 이주 사안이면 위 파일트리 렌즈와 이중 계상 금지, OHS `contract/`는 협력 포트 개명 변종이 아니다). ② 공개 함수가 request contract 1개 외의 인자(맨 스칼라·다중)나 response contract 외 반환 → **important**(통지형 함수의 `None` 반환·입력 없는 Query 위임의 0-인자는 정상). ③ 도메인·응용 예외의 raw 전파·재노출(`__all__` 포함)·published base 미상속·`except Exception` 광범위 폴백 → **important**(transient 인프라 예외(`OperationalError` 등)의 raw 통과는 정상 — published 포장이 오히려 위반(recognizer 사각); 판정이 OHS 평면 함수에 사는 사안이면 위 빈혈 불릿과 이중 계상 금지). ④ published 계약 타입의 application_layer 관통 — touched한 그 BC의 응용·도메인·인프라에서 자기 `published_service` import를 grep으로 확인하라(백스톱 `check-context-isolation` 확장 슬라이스가 직접 import형을 잡으므로 네가 보는 건 변수 우회·간접 재수출 변종) → **blocker**(응용은 domain에만 의존 — houserules §3 표·architecture-ddd §6.1). ⑤ `<service>_service.py` 공개 함수의 docstring 부재(발행 예외 전수 목록 앵커) → **important**(`discipline-cleancode` §4.2 공개 API 독스트링 필수). **명세가 houserules §2 OHS 내부 구조를 어긴 채 통과했으면 발견으로 올린다**(spec-override — 명세 부합을 사면으로 읽지 마라).
```

- [ ] Step 2: 기존 렌즈 카브아웃 2건 — (a) birth-enum 렌즈(⑤ 맨 문자열 discriminator)의 제외 목록에 `OHS published contract의 discriminator wire Literal(§2.14 허용 목록 짝 조항의 OHS 예외 — houserules §2 contract 무의존)` 추가 (모순-H) (b) 협력 포트 개명 변종 열거(`contract/`)에 `(OHS published_service/*/contract/는 제외 — houserules §2)` 병기 (모순-K)
- [ ] Step 3: codex 쪽 동일 반영, 양쪽 diff 0

### Task A4: design-architect 생산자 레인 (codex 미러 포함) — 실효-2

**Files:** `dddjango/agents/design-architect.md`, `codex-dddjango/skills/dddjango-design-architect/SKILL.md`

- [ ] Step 1: 컨텍스트 통신 결정 항목에 추가 — `OHS를 노출·수정하는 스코프면 published_service 내부 구조를 명세 1급 결정으로 박는다: 서비스 폴더(<service>_service/·contract 3파일), 각 공개 함수의 request/response contract 시그니처(request 1개 규칙), 예외 번역표(도메인→published 매핑·폴백·transient raw 통과), 응용 반환 DTO(<usecase>_result.py). 근거는 houserules references/final.md §2 OHS 절 — LLM 일반지식으로 재분류하지 않는다.`
- [ ] Step 2: codex 동일 반영, diff 0

### Task A5: check-context-isolation.py 2슬라이스 확장 + 발화 매트릭스 (실효-3 — 동시 채택)

**Files:** `dddjango/scripts/check-context-isolation.py`, `codex-dddjango/skills/dddjango/scripts/check-context-isolation.py` (byte-id 미러)

- [ ] Step 1: 슬라이스 2 — **contract 무의존**: `published_service/*/contract/*.py`(prod)가 `application.<any>.(domain_layer|application_layer|infra_layer)` import → blocker (FP≈0: contract가 계층을 import할 정당 사례 없음)
- [ ] Step 2: 슬라이스 3 — **관통**: `application/<bc>/(domain_layer|application_layer|infra_layer)/` 하위 prod 파일이 자기 BC `application.<bc>.published_service` import → blocker (타 BC 소비는 허용이므로 own-BC 매칭만 — FP≈0)
- [ ] Step 3: docstring 갱신 — 신 슬라이스 서술 + 기존 `final.md:128/:141` 라인 인용을 §앵커로 교체(모순-B)
- [ ] Step 4: 발화 매트릭스(scratchpad 합성 픽스처 6종) — contract→domain import=2 / 자기 BC app_layer→published=2 / 타 BC 소비 published import=0 / 자기 presentation→published=0 / 기존 cross-BC domain import=2(회귀) / clean=0
- [ ] Step 5: codex 미러 byte-id 복사, `diff` 0

### Task A6: 파생 정본 정합 — cleancode 카브아웃·RUBRIC 라인 인용

**Files:** `dddjango/skills/discipline-cleancode/references/final.md`(:318 허용 목록 짝 조항), `workspace/eval/rubric/RUBRIC.md`(:28)

- [ ] Step 1: cleancode :318 문장 말미에 birth-enum OHS 카브아웃 병기 — `…버전 태그(payload_schema_version)는 같은 형태라도 리터럴 동결이 정답(짝 조항). 단 OHS published contract(published_service/*/contract/)의 discriminator 자리는 반대로 wire Literal["…"]을 유지한다 — contract 무의존(houserules §2)이 우선하고 union-enum 동기 테스트(implementation-test §15.5)가 드리프트를 방어한다.` (모순-H 3곳 세트의 2곳째)
- [ ] Step 2: RUBRIC.md :28 `final.md:128/:141` 라인 인용 → §앵커 교체 + SD-7 관측 지점에 `published_service 내부(3연조·관통)는 houserules §2 OHS 절` 1구 (실효-7 최소 이행)
- [ ] Step 3: 검증 `grep -rn "final.md:141\|final.md:128" dddjango/ workspace/eval/` 잔존 0

### Task A7: 미러 동기·검증·기록

- [ ] Step 1: `python3 workspace/tools/corpus_mirror_sync.py --write` → `--check` exit 0 (houserules·cleancode final.md 자동 전파)
- [ ] Step 2: `claude plugin validate dddjango --strict` pass
- [ ] Step 3: DEVLOG §2 DR 신설 — 발단(실사용 OHS 리뷰→적대 검증 4에이전트→공백 확인), 조문 5개·백스톱 2슬라이스 동시 채택(v1 연기안은 전례 인용 오류로 번복 — DR-60 동형), birth-enum·transient 카브아웃, DEVLOG:366 "향후 OHS→PL 전환" 부분 회수 표기 + §0 최근 작업 1줄
- [ ] Step 4: `git diff --stat` 전수 확인 → 사용자 확인 후 단일 feat 커밋

---

## Part B — 외부 프로젝트(delivery 앱) 적용 스펙 (v2)

> 이 저장소 밖 — 스펙만 산출, 적용은 해당 프로젝트 세션에서.

### Task B0 (신설 — 실효-6(1)): 소비처 전수 조사

- [ ] `grep -rn "published_service" --include="*.py"`로 소비 BC 전수 목록 + import 이름·except 절 매핑표 작성(예외 base 변경은 catch 행동 변화이므로 선행 필수)

### Task B1: 새 트리 이주 (호환 심 단계 포함)

- [ ] v1 트리(delivery_service/·parent_phone_verification_sms_service/ + contract 3파일) 그대로 + **구 모듈은 신 구조 재노출 호환 심으로 1단계 유지**(deprecation 주석), B0 매핑표 기반 소비자 갱신 후 제거
- [ ] `__init__.py` 전부 빈 패키지(재노출 없음) — 소비자 import 경로: `…published_service.<service>_service.<service>_service`(함수)·`…contract.<kind>_contract`(타입)

### Task B2: #1a 계약↔응용 경계 언랩

- [ ] `application_layer/phone_verification_sms/dto/send_parent_phone_verification_sms_request.py` 신설(평면 필드) — 커맨드는 published V1 import 금지
- [ ] **(모순-L) mark 계열 응용 request DTO 2개 신설**: `mark_parent_phone_verification_sms_accepted_request.py`·`mark_parent_phone_verification_sms_failed_request.py`(receipt 필드들 평면 + 후자는 sanitized_failure_reason)
- [ ] 커맨드 반환은 `dto/<usecase>_result.py`(A1 Step 5 슬롯) — OHS가 ResultV1로 재조립
- [ ] delivery: `SendDeliveryRequest.request` 통째 필드 → 평면 필드 교체(현 우회가 Any/TYPE_CHECKING 어느 쪽인지 확인 후 동일 수정)

### Task B3: #4 예외 base 2층 + #7c docstring

- [ ] v1 스펙 유지(root `…PublishedError` + `…TerminalError` 중간층 + 7예외 전부 base 하위) — B0 catch 감사 결과 반영 후 적용
- [ ] 전 공개 함수 docstring: 동작·인자·반환 + raise 예외 전수 목록(앵커)
- [ ] delivery도 신 규약 준수: `DeliveryPublishedError` base + `DeliveryAlreadyProcessingV1`·`DeliveryIdempotencyConflictV1` 번역(+`deliver()` try/except). **transient 짝**: `OperationalError`류는 감싸지 않고 raw 통과

### Task B4: #6 finalize 인터랙터 규약화

- [ ] v1 스펙 유지(Mark…AcceptedCommand·Mark…FailedCommand 2분할 + composition_root 빌더 2개) — 입력은 B2의 응용 request DTO 2개

### Task B5: 권고(선택)

- [ ] v1 목록 유지(폴백 중립화+`__subclasses__()` 동기 테스트·except 순서·TypedDict) + **폴백은 조건부**: 도메인 base 단위 catch 한정, `except Exception` 금지

## Self-Review (v2)

- 모순 A~N 전건 반영 확인: A(A2 codex)·B(A5 Step 3+A6 Step 2)·C(A1 Step 3)·D(조문3 재서술)·E(조문1 자립 서술)·F(조문1 빈 모듈 한정)·G(조문2 앵커 교체)·H(조문4+A3 Step 2a+A6 Step 1)·I(조문3 transient 짝+A3 불릿 ③)·J(A3 불릿 배타 2건)·K(A3 Step 2b)·L(B2)·M(A1 Step 7)·N(A1 Step 8 단서).
- 과적합 채택 7건 반영: 1e(조문2)·reviewer carve-out(A3 ①②③)·폴백 조건부(조문3)·§4(A1 Step 7)·exception 무-import 방향(조문4 replayed 규정)·0-인자 Query 앵커(조문2)·V1 재량(A1 Step 7b). base 자기제외 nit(조문3).
- 실효성 채택 8건 반영: 백스톱 동시 채택(A5)·architect 레인(A4)·불릿 보수(A3)·§1.1 단서+이주 조문(A2 Step 2+조문5)·__init__/반환 DTO 슬롯(조문1·A1 Step 5)·codex 미러(A2·A3·A4)·RUBRIC(A6)·DEVLOG 회수 표기(A7).
- 유지 판정 존중: request 1개 규칙·3파일 고정·<service>_service 명명·공개 클래스 금지(과적합 리뷰 "그대로" 목록).
