# dddjango 폴더·파일·클래스 네이밍 규약 (DR-41 설계 v2)

> 상태: 설계 승인 + **적대 리뷰 4렌즈 반영**(전원 조건부 GO, 조건 해소). 구현 전. 정본 결정 원장 = `workspace/DEVLOG.md` DR-41.
> v2 변경: 포트/어댑터 접미사 기준 **ⓑ(확립 패턴명 예외)** 채택 + 적대 리뷰 조건(자기모순 전수 제거·에이전트 필수 갱신·미러 오프셋·토큰 매핑·DR 번복 정정노트) 반영.
> 핵심: 표준 파일트리(houserules §0~§3)는 폴더 *위치*는 촘촘하나 폴더/파일/클래스 *네이밍*이 비어 있는 슬롯을 채운다. **포트/어댑터는 §4를 헥사고날 정석으로 개정**(DR-05/37 번복 — 큰 변경).

## 배경 — 왜 이 변경을 하나

사용자 점검에서 "파일 트리(폴더 위치) 규칙은 촘촘한데 파일명·클래스명 규칙은 §3 표 임베드 패턴 + §4 약어 금지 1줄뿐"임이 드러났다. 트리는 결정적 백스톱 4종이 집행하나 네이밍은 reviewer 권고에만 의존했다. 이 비대칭을 메우되 "전부 의무화"의 함정(DR-39 교훈)을 피해 **집행 가능·효용 높은 클래스/파일 네이밍은 필수, 의미 판정이 필요한 폴더 도메인명은 권장**으로 차등한다.

조사 중 **ACL/외부서비스 명명이 §4의 추상-구현 명명 철학과 헥사고날 정석 사이에서 어긋나 있음**(ACL 구현을 `Port`라 부름)이 외부 권위 자료로 확증돼, §4를 port↔adapter로 개정한다.

## 결정

### 1. 핵심 규칙 (3줄)

1. **파일명 = 그 안 주 클래스명의 snake_case**(역할 접미사 포함). 폴더는 종류 그룹일 뿐 파일 접미사를 좌우하지 않는다.
2. **도메인 개념 3종(값객체·엔티티·애그리거트)은 bare**, 역할 객체는 역할 접미사. **읽기(조회)는 selector 함수**(예외가 아니라 CQRS 읽기 모델의 정상 형태 — `architecture-ddd` §5.4).
3. **확립 패턴명(PoEAA/GoF: `Repository`·`Gateway` 등)은 추상·구현 동일 접미사 유지, 그 외 일반 협력 포트는 헥사고날 `...Port`(추상) ↔ `...Adapter`(구현) 쌍.**

### 2. 종류별 네이밍 표 (필수 — 집행 대상)

**도메인 계층**

| 종류 | 폴더 | 파일 | 심볼 |
|---|---|---|---|
| 값객체 | `value_object/` | `money.py` | `Money` |
| 엔티티 | `entity/` | `order_line.py` | `OrderLine` |
| 애그리거트 루트 | `<agg>/` | `order.py` | `Order` |
| 도메인 이벤트 | `event/` | `order_placed_event.py` | `OrderPlacedEvent`(과거형) |
| 도메인 서비스 | `domain_service/` | `pricing_service.py` | `PricingService` |
| 명세 | `specification/` | `order_active_specification.py` | `OrderActiveSpecification`(풀네임) |
| 리포지토리(추상) | `repository/` | `order_repository.py` | `OrderRepository` |
| 협력 포트(추상·일반) | `port/` | `product_lock_port.py` | `ProductLockPort` |
| 외부서비스 포트(추상·Gateway 패턴) | `port/` | `payment_gateway.py` | `PaymentGateway` |

**응용 계층**

| 종류 | 폴더 | 파일 | 심볼 |
|---|---|---|---|
| 커맨드 DTO | `dto/` | `place_order_command.py` | `PlaceOrderCommand` |
| 응용 서비스(쓰기) | `command/` | `place_order_service.py` | `PlaceOrderService` |
| 조회(읽기) | `query/` | `list_orders_query.py` | `def list_orders(...)` selector 함수 |
| 오케스트레이션 | `service/` | `checkout_service.py` | `CheckoutService` |
| 이벤트 핸들러 | `handler/` | `order_placed_handler.py` | `OrderPlacedHandler` |

**인프라 계층**

| 종류 | 폴더 | 파일 | 심볼 |
|---|---|---|---|
| ORM 모델 | `django_<app>/models/` | `order_model.py` | `OrderModel` |
| 리포지토리(구현) | `repository/` | `order_repository.py` | `DjangoOrderRepository` |
| ACL 어댑터(구현·일반 포트) | `acl/` | `product_lock_adapter.py` | `DjangoProductLockAdapter` |
| 외부서비스 어댑터(구현·Gateway 패턴) | `adapter/` | `stripe_payment_gateway.py` | `StripePaymentGateway` |

**표현 계층**

| 종류 | 폴더 | 파일 | 심볼 |
|---|---|---|---|
| 스키마 입력 | `schema/` | `schema_in.py` | `OrderIn` |
| 스키마 출력 | `schema/` | `schema_out.py` | `OrderOut` |
| 스키마 에러 | `schema/` | `error_out.py` | `ErrorOut` |

> 근거: 접미사 정책 = §4 "역할 접미사 OK / 타입 표식(`Interface`/`Impl`) 금지"의 확장. 도메인 3종 bare = 유비쿼터스 언어. 이벤트 과거형·명세 풀네임(약어 금지 §4 준수)·조회 selector·스키마 In/Out = reference 코퍼스 + ninja 공식 문서. `_app` 접미사 폐기(근거 없는 군더더기 — `application_layer`와 중복).

### 3. 포트/어댑터 — §4 헥사고날 개정 (⚠️ 큰 변경 · DR-05/37 번복)

**BEFORE(§4 현행):** 구현 = 추상화 base명 유지 + 기술 접두(`ProductLockPort`→`DjangoProductLockPort`) — 모든 포트 구현에 `Port` 보존.

**AFTER(ⓑ 기준):**

| 구분 | 판정 | 추상 | 구현 |
|---|---|---|---|
| 확립 패턴명(PoEAA/GoF) | `Repository`·`Gateway`·`Mapper` 등 GoF/PoEAA 등재명 | `OrderRepository`·`PaymentGateway` | `DjangoOrderRepository`·`StripePaymentGateway`(**패턴명 유지**) |
| 일반 협력 포트 | 위에 없는 추상 — 다른 BC 협력(ACL) 등 | `ProductLockPort` | `DjangoProductLockAdapter`(**헥사고날 쌍**) |

- **판정 기준:** 외부 시스템/인프라 자원 관문(결제·푸시·SMS·인증)은 PoEAA **`Gateway`** 패턴 → 추상·구현 다 `Gateway`. 다른 BC 협력(ACL)·도메인 역할 추상은 일반 **`Port`** → 구현은 `Adapter`. `Repository`는 PoEAA 패턴명 → 구현도 `Repository`.
- **근본 교정:** §4 현행이 `Repository`/`Port`/`Gateway`를 "역할 접미사" 한 묶음으로 봤으나 — `Repository`/`Gateway`는 *확립 패턴명*(구현 유지), `Port`는 *헥사고날 위치 표식*(구현은 `Adapter`). Repository 예외는 단독이 아니라 "확립 패턴명 유지" 원칙의 한 사례다.
- **폴더:** ACL = `infra/acl/`(DDD 패턴명 유지), 외부서비스 = `infra/service/` → **`infra/adapter/`**(개명 — infra `service/`만; `service` 단어가 domain_service·app service·infra 3겹쳤던 것 중 infra 1겹을 떼어 외부 어댑터임을 명확화. 남는 domain_service는 접두로, app `service/`(오케스트레이션)는 계층으로 구분 유지). `adapter/` 폴더 = 외부 연동 어댑터 위치이며 그 안 클래스는 Gateway 패턴이면 `Gateway`, 일반이면 `Adapter`.
- **추적성(정직):** BEFORE는 `grep ProductLockPort`로 추상+구현을 한 패턴에 잡았다. AFTER는 접미사가 `Port`/`Adapter`로 갈려 일괄 grep이 약화되나, base 개념명(`ProductLock`) 공유로 쌍 추적은 유지되고 **백스톱·reviewer가 보완**한다(grep 친화성 의존을 줄이는 DR-20~32 코어 철학과 정합).

### 4. 폴더명 (A 그룹 — 권장 수위, 백스톱 없음)

- **앱 `<app>`** = 핵심 애그리거트명과 **동일**(단일 BC·단일 애그리거트). 여러 애그리거트면 대표/컨텍스트명. snake_case. (placeholder `<app>`·`<aggregate>`는 §0-1 범례상 의미는 별개 — "동일 권장"은 단일 BC 한정)
- **애그리거트 `<aggregate>`** = **단수** 개념명. snake_case.
- **feature `<feature>`** = 유스케이스 단위. 보통 앱당 1개(앱·애그리거트명과 같아도 됨), 여러 유스케이스 그룹이면 분리.
- **금지:** 앱명과 애그리거트명의 유사 변형(`ordering` vs `order`) — 같게 하거나 명확히 다른 컨텍스트명으로.

## 적대 리뷰 4렌즈 반영 (전원 조건부 GO → 조건 해소)

- **렌즈1(houserules 정합):** §0 불변식 구조 위반 없음(전부 이름 레벨). `service/`→`adapter/` 줄 단위 선택 치환(app/domain `service` 오염 금지)·`_app` 6토큰 매핑·`_spec`/`_event` 토큰 교정 명시(아래 변경범위).
- **렌즈2(미러 무결성):** final.md는 완전 byte-identical(검증됨). SKILL.md는 `user-invocable: false`로 **1줄 오프셋** — frontmatter 스킵 후 `diff`=0 검증(줄번호 패치 금지). 변경범위 "byte-identical" → "frontmatter 제외 byte-identical" 정정.
- **렌즈3(헥사고날 정합):** `PaymentPort` 통일이 코퍼스 §5.3 `PaymentGateway`와 충돌·자기모순 → **ⓑ 채택으로 해소**(Gateway 패턴명 유지). ACL `Adapter` 근거를 코퍼스 §5.3 어댑터 분류(`:1499`)에 앵커 — 코퍼스 ACL *예시*(`Translator`/`ACL`/`AntiCorruptionLayer`, `:301·335·1956`)와는 다른 의도적 선택임을 명시(쌍 추적성·헥사고날 일관 우선). 핵심규칙2 "(예외)" → "CQRS 읽기 정상 형태"로 명확화.
- **렌즈4(devil's advocate):** 백스톱 12~13종 영향 0(실측)·fixture 레포 내 부재 확인. 자기모순(표준 자신 예시가 위반화)은 **전수 제거 종료조건**으로 차단. DR-05/37 번복 정정노트 필수.

## 외부 자료 근거 (포트/어댑터)

ACL 구현 명명을 외부 권위 자료로 검증: **`Port`를 구현에 쓰는 사례 없음**, `Adapter`/`Translator`/`Facade`가 표준(헥사고날: "ACL = 어댑터들의 집합"). 포트는 도메인 역할명(`PaymentGateway` 등).

- [Anti-Corruption Layer — Microsoft Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Anti-corruption layer — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/acl.html)
- [Anti-Corruption Layer in Java — Java Design Patterns](https://java-design-patterns.com/patterns/anti-corruption-layer/)
- [Hexagonal Architecture IG — J.M. Garrido Paz](https://jmgarridopaz.github.io/content/hexagonalarchitecture-ig/chapter2.html)
- 내부 이론 코퍼스 `architecture-ddd/references/final.md:1493·1499`(포트=역할/어댑터=구현 분류)·`:1956`·`:335`(ACL 예시).

## 변경 범위 (writing-plans 대상)

**필수(표준 — claude + codex 미러 동시):**
1. `dddjango/skills/discipline-houserules/references/final.md` — §2 트리·§3 표·§4 명명 규약 전면 개정: 포트/어댑터 ⓑ 기준 재서술·`_app` 6토큰(`:86·87·89·186·187·190`) 매핑·`_spec`(`:179`)→`_specification`·`_event`(`:178`) 교정·이벤트 과거형/명세/스키마/조회 명명 신규·`service/`(`:100·122·203`)→`adapter/` 줄 단위·폴더명 권장 절.
2. `dddjango/skills/discipline-houserules/SKILL.md` — §4 요약(`:35`)·위반 항목(`:55`)·infra 분할(`:29`) 갱신.
3. `codex-dddjango/skills/discipline-houserules/references/final.md` + `SKILL.md` — 위 byte-identical 미러(SKILL.md는 frontmatter 제외).
4. **에이전트(필수 — "검토 필요"에서 승격):** `dddjango/agents/design-architect.md`(`:38` 옛 명명 지시)·`discipline-reviewer.md`(`:40` 옛 위반패턴) + codex 미러 `codex-dddjango/skills/dddjango-design-architect/SKILL.md`·`dddjango-discipline-reviewer/SKILL.md`.

**검토(영향 확인):**
- `workspace/eval/rubric/RUBRIC.md` — 명명 채점 항목이 옛 명명을 박았는지.
- 백스톱 12~13종 — 무변경(실측 영향 0), 구현 후 전수 재실행으로 거짓양성 0 확인.

## 구현 완결성 조건 (종료 게이트 — 부분 갱신 금지)

1. **자기모순 전수 제거:** `DjangoProductLockPort` grep **0건**(claude+codex 전체; `Repository`만 잔존 허용). §4 "역할 접미사 한 묶음" 분류 산문 통째 재서술.
2. **에이전트 동시 갱신:** 표준과 같은 커밋에서 4종(claude 2 + codex 2) 갱신. 미루면 표준-에이전트 분기 → 라이브서 옛 명명 생성·통과.
3. **미러 검증:** final.md 전체 `diff` exit 0. SKILL.md는 claude 5줄/codex 4줄 스킵 후 `diff` 0.
4. **DEVLOG DR-41:** DR-05/37 번복임을 정정노트로 명기(역사 보존).

## 적대 리뷰 (완료) → 다음: writing-plans

4렌즈 적대 서브에이전트 리뷰 완료(전원 조건부 GO, NO-GO 없음). 조건은 위 "구현 완결성"에 반영. 다음은 writing-plans로 task 분해.

## 백로그 (이번 범위 밖)

- **command/dto 폴더 구조 정렬:** 거주 객체와 어긋난 구조. CQRS 해석 결정이 필요한 §0 불변식 변경이라 분리. 이번엔 "파일=거주 객체 반영" 네이밍으로 우회.

## 범위 밖 (명시)

- 함수 지역 변수·내부 구현 명명(implementation-python PEP8 위임).
- command/dto 폴더 재배치(백로그).
- 폴더명(A) 결정적 백스톱(의미 판정 — reviewer 권고).
- 커밋·push — 사용자 명시 승인 시에만.

## 정본 포인터

- 결정 원장: `workspace/DEVLOG.md` DR-41
- 이 설계: 본 문서 / 구현 계획: writing-plans 산출 예정
- 적대 리뷰: 4렌즈 리포트(houserules 정합·미러 무결성·헥사고날 정합·devil's advocate)
- 영향 파일: houserules `references/final.md`·`SKILL.md`(미러) + agents 4종(미러) + (검토)RUBRIC·백스톱
