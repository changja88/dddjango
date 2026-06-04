# dddjango 평가지 v3 — 규칙 준수 + 기능 정확성 (평가 항목)

> **상태**: v3 (2026-06-02) — **동결-전-결정 5개 해소 완료**(아래 §동결 전 결정 + `EVAL-METHOD.md §0.1`). *사용자 "동결됨" 최종 확인 후 채점 착수*(미동결 채점 = §과적합 위반). `EVAL-METHOD.md` v3과 정합.
> **목적(사용자 확정)**: 산출물이 ① **우리 플러그인의 규칙(DDD·houserules·django-ninja)을 얼마나 잘 지키는가** + ② **요청 기능을 올바르게 구현했는가**를 측정한다. *baseline 대비 차별가치는 안 잰다 — 규칙 준수가 핵심.* 기능 정확성은 잰다(형태만 보면 "재고 늘어나는 주문 API"도 통과하므로).
> **PASS 바 = 표준 규칙(앵커 아님)**: 판정 기준은 각 항목 §근거의 *표준 조항*이다. §E 앵커는 *규칙 충족/위반의 예시*일 뿐 임계값이 아니다 — "플러그인이 실제로 낸 수준"을 바로 두지 않는다(순환 방지). 새 산출물은 표준 조항으로 채점하고 앵커는 참고.
> **명시적 비측정(과대주장 제거)**: baseline 대비 가치(절대 준수만 봄) · 미시 가독성·복잡도(유지보수성은 구조 대리까지만) · 보안(단 *에러 응답에 스택트레이스·내부경로·SQL 누출 0*은 항상 치명) · 명세 내적 품질(후순위). 이들은 평가지 밖/위임/후속.
> **범위**: 이 문서=평가 *항목*. 채점/집계/bisect/완료=`EVAL-METHOD.md`.
> **산출 형식**: 채점 결과지(`results/*.md`)의 섹션 순서·칼럼·필수 단서는 `EVAL-METHOD.md §6` 표준 템플릿을 따른다. 결과지 차원-섹션 순서 = 이 문서 **A→B→NINJA→FC→C→D**(E 앵커는 루브릭 전용·결과지 미포함).
> **레인 표기**: 결정=구조-인지 스크립트/grep, 의미=서브에이전트 grader. 치명=치명 게이트(이진 PASS/FAIL, WEAK 금지).

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)
표준: `dddjango/skills/architecture-ddd/references/final.md`

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | 핵심 비즈 규칙·불변식이 도메인(애그리거트/도메인서비스)에 메서드로 존재 | §3.2·§3.1 | spec 핵심 규칙이 domain_layer 코드에 구현 | 판정이 도메인에 없고 응용/인프라/스키마에만 | 의미(+grep) | ✅ |
| **SD-2** 빈혈: 프로덕션 호출 | 응용서비스가 *조회→도메인메서드→저장*으로 그 판정을 실제 호출 | §3.2·§3.6 | 프로덕션 쓰기 경로가 도메인 판정 메서드를 호출 | 도메인 메서드가 있어도 응용이 안 부르고 `.update()`/raw SQL로 우회(죽은 도메인 메서드) | 의미(호출추적) | ✅ |
| **SD-3** 빈혈: 무복제 | 비즈 판정이 인프라 SQL/ORM에 복제 안 됨(경합 가드 version/CAS만) | §3.2 | 인프라엔 version/CAS만, 판정 복제 0 | `stock__gte=` 등 비즈 조건이 WHERE/필터/F-식에 복제 | 결정+의미 | ✅ |
| **SD-4** 애그리거트 경계 | 1트랜잭션 1애그리거트(또는 동일DB 예외 명시)·최소 크기·타 애그리거트 ID 참조·일관성 방식 적정 | §3.3 규칙1~4 | 작은 경계·ID 참조·일관성 선택 근거 있음 | 거대 애그리거트 / 객체 직접 참조(도메인 FK 결합) / 근거 없는 복수 애그리거트 수정 | 결정(ID)+의미 | ✅ |
| **SD-5** 모델 표현력 | 값객체 불변·도메인서비스 무상태(애그리거트 비의존)·식별자가 유비쿼터스 언어 | §3.1·§3.5·§2.3 | frozen 값객체 / 무상태 서비스 / 비즈 용어 네이밍 | 가변 값객체(setter) / 애그리거트가 서비스 주입받음 / CRUD·매직 네이밍 | 결정+의미 | ✅ |
| **SD-6** 계층 순수성(P1a 포함) | domain이 HTTP/ORM/프레임워크 import 0; 예외→status 변환이 presentation 단일점 | §5.1·§6.1; ninja §2.2·§6.2 | domain import 깨끗 + operation 성공 schema만 return + 예외 중앙 raise + 중앙핸들러 발화 | domain이 HTTP/프레임워크 import / operation이 raw 응답 생성 / status 객체가 app 계층 흐름 / 중앙핸들러 죽은코드 | 결정+의미 | ✅ |
| **SD-7** 컨텍스트 통신 | 타 BC는 `published_service`(OHS)/ACL로만; 교차 결합(모델·예외)은 ACL에 격리 | §3.2(3)·§2.5 | OHS 소비, 또는 OHS 미이주 시 `infra_layer/acl/` ACL이 업스트림 import·번역(모델·**예외**까지 ACL 격리·도메인은 포트 ABC 의존) | **ACL 밖**(도메인/응용/presentation)이 타 BC `domain_layer`/`infra_layer`(예외 포함) 직접 import / OHS 존재하는데 미경유 / ACL이 번역 안 하고 누수 | 결정+의미 | ✅ |

> **SD-6 주의(DR-24·Goodhart 차단)**: `check-error-centralization.py`는 텍스트 신호(`JsonResponse(`/`from ninja`)만 본다 — **status:int 든 plain 객체가 계층을 흐르는 의미적 변종은 못 봄**. 의미 레인은 스크립트 exit0과 *무관하게* operation 본문·중앙핸들러 발화 여부를 줄 인용으로 확인해야 PASS. **의미 레인 FAIL이면 스크립트 exit0이어도 SD-6 *치명 FAIL*(WEAK 강등 금지)** — "리터럴만 피하면 녹색"이라는 metric 게이밍을 차단(method §2 의미적 변종 처리).

> **SD-7 주의(미스캘리브 교정 2026-06-02)**: 결정 레인(`check-structure.py`)은 타 BC 내부 import를 신호로 내나 **`infra_layer/acl/` 미이주 ACL이 업스트림(catalog) 모델·리포·예외를 import·번역하는 건 표준 §2(houserules `final.md:128`/`:141`) 명시 허용 = FAIL 아님**(주의신호로만 분리; 도메인은 포트 ABC 의존·번역이 ACL 격리 시). **진짜 FAIL = ACL *밖*(도메인/응용/presentation)이 타 BC 내부를 직접 import**(예: 예외 번역이 ACL에 안 갇혀 누수) / OHS 존재하는데 미경유 / ACL 도메인누수. *근거*: smoke4-claude(catalog 결합이 ACL에 격리 → **PASS**) ↔ p1a-v3-claude(catalog 예외가 presentation·application으로 누수 `order_api_router.py:26`·`create_order_app.py:17` → **FAIL**)로 갈린다 — 과거 "Claude ACL infra import=FAIL" 앵커는 미스캘리브 오판이었다.

## B. TIER-S 척추 — houserules 충실도 (S-HR)
표준: `dddjango/skills/discipline-houserules/references/final.md` + `SKILL.md`

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 앱이 `application/<app>/` 하위 | §0-1 | 신규 앱이 `application/` 하위 | 신규 앱이 루트(마스크 C 적용) | 결정 | ✅ |
| **SH-2** 4계층 | `{domain,application,infra,presentation}_layer/` 물리 분리 | §0-2 | 4계층 존재 | 누락/평면 | 결정 | ✅ |
| **SH-3** 종류 폴더 | 종류 2차 폴더(빈 패키지 허용), ORM/포트/리포가 평면 `.py` 아님 | §0-3·§0-4 | 종류 폴더 구조 | ORM/포트/리포가 평면 `.py` (WEAK: 일부 빈폴더 누락) | 결정 | — |
| **SH-4** Django앱 위치 | `models.py`·`migrations/`가 `infra_layer/django_<app>/`; AppConfig `name`=점경로·`label` | §0-5 | 모델/마이그가 `infra_layer/django_` | 루트/앱루트/도메인에 `models.py`(마스크 C 적용) | 결정 | ✅ |
| **SH-5** ORM 명명 | ORM `<Name>Model`, 도메인 bare | §0-6·§4 | 명명 분리 | 혼동(도메인에 Model접미사·ORM이 bare) | 결정 | — |
| **SH-6** 포트/구현 명명 | 추상=개념+역할접미사; 구현=기술접두+base명 일치; `Interface`/`Impl`·파일명 약어 0 | §4 | 규약 준수 | `Interface`/`Impl` / `*_repo.py` / base명 불일치 | 결정 | — |
| **SH-7** 협력 포트 위치 | 협력 포트가 `domain_layer/<agg>/port/` | §2 | `domain_layer/.../port/` | `application_layer`/`infra_layer`에 위치 | 결정 | ✅ |
| **SH-8** ACL 분리 | ACL이 `infra_layer/acl/`(+domain `port/`), `repository/`에 안 섞임 | §2·§3 | acl 분리 | repository에 번역 어댑터 혼합 | 결정+의미 | — |
| **SH-9** 단일 레이아웃 | 한 앱이 두 레이아웃 안 가짐 | §1.4 | 단일 레이아웃 | `test`+`tests` 공존·`src`+`apps` 혼용 | 결정 | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}` 분리; HTTP=integration; 평면나열 0 | §1.3 | 의미군 분리·올바른 배치 | 평면 나열 / 의미 오배치 | 결정+의미 | — |

---

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)
표준: `dddjango/skills/implementation-django-ninja/references/final.md` + `SKILL.md`
> **조건부**: 기능에 HTTP/JSON API operation이 하나라도 있을 때만 채점. 없으면(서버렌더·CLI·배치·순수도메인) 차원 **N/A**(점수 산입 0, FAIL 아님).
> **비중복 보증**: 오류→status 중앙화=**SD-6 소유** / problem 형식·status 의미·버전 *정책*=**Q-2 소유** / 일반 의존성 핀=**Q-7 소유** → S-NINJA는 재채점 안 함(교차참조만). NJ-2는 SD-6과 **직교**(SD-6="오류를 operation이 만드나" / NJ-2="비즈로직·ORM·수동파싱을 operation이 하나").

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명(조건부) |
|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 HTTP/JSON API를 Ninja(`NinjaAPI`+`Router`)로; plain view·`JsonResponse`·DRF로 안 샘; 기존 스택 존중 | §1.1·§10 | 신규 JSON API가 ninja Router operation으로 등록 | 신규 JSON API가 plain `django.views`/`JsonResponse`·DRF로 구현(greenfield인데) | 결정 | ✅ |
| **NJ-2** operation 얇음(비-오류) | operation 본문에 비즈로직·상태전이·ORM·수동 본문파싱·수동 필드검증 0; service 호출 + schema 매핑만 | §1.3·§2.2 | schema 바인딩→service 호출→응답 매핑만 | operation에 `json.loads`/수동검증/ORM/비즈 분기 | 의미(+grep) | ✅ |
| **NJ-3** Schema 입출력 분리 | 요청·응답을 `Schema`/`ModelSchema`로 분리, 도메인 엔티티 직접 직렬화 0 | §2.2·§3.1 | 입·출력 별도 Schema, 도메인→DTO 매핑 | 도메인 객체 직접 `response=` / 내부필드 누출 | 결정+의미 | — (강) |
| **NJ-4** status별 response 선언 | 가능한 모든 status를 **`response={...}`에** schema 선언(§2.2 line111) — `openapi_extra`/`get_openapi_schema` 수동 선언은 **불충족**(ninja 미인지) | §2.2·§8 | 오류 status가 `response={...}`에 선언(201/404/409/422…) | `response=`엔 성공(201)만·오류는 `openapi_extra`/핸들러에만 | 결정 | — (강) |
| **NJ-5** operation 문서화 | `summary`(+`tags`) 부여, 무정보 반환타입(`-> object`) 금지 | §2.2 | summary/tags + 의미있는 반환타입 | summary 없음 / `-> object`·어댑터 누수형 | 결정 | — (경미) |
| **NJ-6** ninja 버전 핀 표기 | 신규 도입 시 매니페스트에 버전 핀, 기존 관례와 일치 | §2.1 | `django-ninja==<버전>` 관례 일치 | 매니페스트 부재/무핀/표기 불일치 | 결정 | — (경미) |

> **의도적 제외(표준이 강제 안 함·거짓양성 원천)**: operationId 명시(§8 "확인"일 뿐·자동생성)·OpenAPI error media-type `problem+json` 표기(§6.2 "수용된 한계, 사후변형 금지" — 항목화 시 표준 위반)·Idempotency/인증/페이지네이션 *정책*(architecture-api 위임=Q-2).
> **앵커 한계(거짓양성 직결)**: NJ-2만 강한 양극 앵커(smoke2-codexB 극단 ↔ 준수 다수). **NJ-1·3·6은 8벌 전부 준수라 known-bad 부재** → 준수 강제 게이트로는 약함(동결 전 합성 반례/baseline plain-view 참조 결정).
> **🔴 에러 경로 정독·양방향 보정(NJ-1·3·4·SD-6 — `poc-codex` 2026-06-02 miss 반영)**: operation(성공 schema 반환)·G3 backstop exit0만 보고 NJ를 PASS 주지 마라 — **에러 경로 전체**(`@api.exception_handler`·problem 헬퍼·협상 데코레이터)를 줄 인용으로 읽는다. **과교정 차단(false-positive)**: §6.2는 *중앙 핸들러가 problem dict를 만들어 `ninja.responses.Response`로 반환*함을 **처방**하므로 그 형태 자체는 **준수** — "핸들러가 dict/Response 반환"을 SD-6 'operation raw 응답'·NJ-1 'plain leak'으로 오판 금지(죽은 schema 아님: §6.2도 dict 손수 빌드). **진짜 일탈(채점 대상)**: (a) `ninja.responses.Response` 아닌 **`django.http.JsonResponse`** = 경미(🟡 NJ-1) · (b) 오류를 `response={}` 아닌 **`openapi_extra`로** 선언 = **NJ-4 FAIL**(OpenAPI 가시성 달성해도 §2.2 line111 위반). G3 backstop은 `response={}` 선언분만 보므로 (a)(b) 둘 다 **exit0 통과** = 의미 레인 전담.

## TIER-S(핵심) — 기능 정확성 (FC)
> 형태가 아무리 맞아도 *동작이 틀리면* 무가치다. FC는 코드가 **요청 기능을 실제로 올바르게** 하는지를 *명세와 독립된 외부 기준*으로 잰다 — 명세·코드·테스트가 같은 방향으로 틀린 순환(그린바 통과인데 기능 오류)을 차단. **치명 게이트.**

| ID | 항목 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 평가자가 *명세 무관* 외부 행위표를 사전등록(예: 재고10·주문3→201∧남은7 / 재고2·주문5→409∧재고불변∧주문0)하고 코드를 그 표로 직접 두드림 | 모든 골든 케이스 일치 | 하나라도 불일치(차감 방향·status·부작용) | 의미(외부 오라클 실행) | ✅ |
| **FC-2** 테스트 비-vacuous | 핵심 로직에 mutation 주입(차감 부호·`>=`→`>`·status 값) 후 테스트 red 확인 | mutation마다 테스트 red | mutation에도 green(테스트가 헛것) | 결정(주입 실행) | ✅ |
| **FC-3** 도메인 정합(negative gate) | 명백한 도메인 오류 부재 — 음수 재고 허용·차감 방향 역전·주문↔재고 인과 역전 등 | 명백 오류 0 | 명백 도메인 오류 1+ | 의미 | ✅ |

> **FC vs SD 구분**: SD는 "*비빈혈 형태*"(판정이 도메인에 있나), FC는 "*그 판정이 맞나*"(동작이 정답인가). 비빈혈인데 *틀린* 모델(잘못된 불변식)은 SD PASS·FC FAIL로 갈린다 — 적대리뷰 CF-2(틀린 도메인 모델) 차단.
> **조건/사전등록**: 골든 표(FC-1)는 태스크별로 *채점 전에* 사전등록(method §과적합). FC-1·2는 fixture에 `.venv`·실행 가능 코드가 있을 때 실측.

---

## C. 기존규약 마스크 (S-HR 항목 판정 조건 — §1.1↔§1.2)
> 8벌 전부 `catalog/`가 평면 `startapp`으로 **시드**돼 있어, 평면 유지가 §1.1 존중인지 §1.2 위반인지로 SH 판정이 뒤집힌다. SH 항목(특히 SH-1·SH-4) 채점 시 다음을 **곱한다**:

- **신규 앱**(baseline에 없던, 런이 생성) → **§0 전부 강제**(존중 면제 없음).
- **기존 앱**(baseline에 있던) →
  - 런이 그 앱에 **새 판정·불변식을 얹었으면**(예: 재고 차감 판정) → §1.2 + ddd §3.2 "판정 소유→구조 이주" 발동. *그 판정 코드*는 표준 트리 대상(평면 유지 시 SH FAIL) + SD-1~3와 교차.
  - **판정은 안 얹었으나 *런이 건드렸으면*(diff에 새 마이그레이션·필드·제약)** → §632-(2)로 *4계층 전개*는 면제(데이터소스라 애그리거트 골격 불요)지만 **위치는 면제 안 됨**: `application/<app>/`(`infra_layer/django_<app>/`)여야 하고 루트 평면이면 **SH-1·4 FAIL**(houserules §0-1).
  - **판정도 안 얹고 *런이 안 건드린* 무관 기존 앱** → §1.1 존중 → 평면 유지 = **위반 아님**(SH 면제).

> **조작화(v3)**: 이 "판정 적재" 판단은 `EVAL-METHOD.md §1.1.M`의 이진 하위질문(MQ1=런 diff에 핵심규칙 분기 추가? / MQ2=단순 상류 데이터소스?)으로 집행한다 — `MQ1=Y ∧ MQ2=N`이면 §1.2 발동. N_grader 경합 시 **보수적으로 *적재됨*(엄격)** + 인간 큐(치명 게이트 입력이므로).
>
> **위치 vs 깊이 분리(정정 2026-06-02 — smoke6 채점 오류 교정)**: MQ1/MQ2는 *4계층 전개 의무*(애그리거트 골격)만 가른다 — **위치(`application/<app>/` vs 루트)는 별도 축이고 면제가 없다**. *런이 건드린(diff 포함)* 기존 앱은 MQ1=N(순수 데이터소스)이어도 위치는 `application/<app>/`여야 하며 루트 평면이면 **SH-1·4 FAIL**. SH 위치 면제 = 그 앱이 **런 diff에 없음(untouched)**일 때만. 결정 레인 백스톱 `check-app-container.py`(7번째)가 동일 판정을 결정적으로 낸다(touched 루트 앱→exit 2; 빈 껍데기 `application/<app>/` 토큰엔 안 속음). **smoke6-claude(catalog touched·MQ1=N·루트 평면)를 이전에 SH PASS로 오판했으나 SH-1·4 FAIL이 맞다** — §632-(2) "평면 유지=깊이 면제, 위치 비면제"를 위치 면제로 오독한 채점 오류.

---

## D. TIER-Q 품질 (카운트 순위 — `EVAL-METHOD.md §2.4`; '가중치 수치' 미정의라 v3에서 카운트 기반 전환)

| ID | 항목 | §근거 | PASS | FAIL/WEAK | 레인 |
|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 요청 외 기능 발명 0(멱등성·멀티라인·합산이 task 요구였나); 양방향(과소=빈혈은 SD / 과잉=무거운 패턴 미도입 §6.8); 고-blast 트레이드오프를 G1 상정(사후기록≠상정) | ddd §6.8·houserules §6.1 | 요청 범위 내·미선택 패턴 근거 기록 | 요청 외 발명 / 무거운 패턴 남용 / 고-blast를 §Open Questions에만 | 의미(spec) |
| **Q-2** API 계약 | status/problem(RFC 9457) 일관·버전 정책 일관·콘텐츠협상 근거 | architecture-api §4~14 | 일관·근거 있음 | 비일관/근거 없음 | 의미 |
| **Q-3** §9.6 형식+테스트 실현 | Risky Write 8행 다뤄짐(N/A 근거); 선언 동시성 기준이 **실제 테스트로 실현**·소진→409 경로·결정적 CAS 스파이 | architecture-db §9.6·implementation-test §20.5 | 8행 + 동시성 전 분기 결정적 테스트 | 8행 누락 / 약속 테스트 부재 / 소진 경로 미테스트 | grep+의미 |
| **Q-4** 메커니즘 소유권 **[🔴 치명 — v3 승격]** | 커스텀 DB 백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 0 | architecture-db §9.5·§16.4 | 표준 ORM만 | 커스텀 백엔드/PRAGMA/몽키패치 | 결정 |
| **Q-5** 마이그레이션 안전 | 기존 0001 불변·`db_table`/`label` 보존·expand 단계·backfill | architecture-db §11 | 이력 불변·호환 변경 | 기존 0001 재작성 / 테이블 rename 위험 | 결정+의미 |
| **Q-6** 테스트/TDD | `check`+`test` 그린바·인수가 명세 행위 덮음·의미군 분리 | implementation-test·discipline-tdd | 그린바+커버리지 | 실패/에러 / 행위 누락 | 결정(실행)+의미 |
| **Q-7** 경미 | 빈 종류폴더 누락·**공개 표면 변수 어노테이션**(§4 — 모듈/클래스 변수 리터럴 상수 첫 대입 필수·함수 지역변수 권장·면제는 §4 참조)·주석 언어 일관(§5)·의존성 핀(§6.2) | houserules §4·§4.1·§5·§6.2 | 준수 | 경미 흠(WEAK) | 결정(check-public-surface-annotation)+의미 |

> **Q-4 치명 처리(v3)**: Q-4는 TIER-Q에 배치돼 있으나 **치명 게이트**다 — `EVAL-METHOD.md §2 step2`에서 처리(FAIL→픽스처 전체 FAIL)하고 §2.4 Q 등급(카운트)에는 **불산입**. 나머지 Q-1·2·3·5·6·7만 품질 등급에 들어간다.

---

## E. 앵커 (항목별 예시 — *임계값 아님*; 판정 바=표준 규칙)

> 앵커는 *규칙이 충족/위반된 구체 예시*일 뿐 PASS 임계값이 아니다(바=각 항목 §근거 표준 조항). 8벌서 뽑되 "플러그인이 낸 수준"을 기준으로 굳히지 않는다(순환 방지). 앵커가 예시일 뿐이므로 *홀드아웃 격리 불요* — 단 채점 *기준(criteria) 자체를 8벌 보고 조정*하지는 않는다(method §과적합).
> **출처·마스킹(v3)**: 아래 앵커는 *현존 fixture 직접경로*(`~/Desktop/dddjango-<run>/...`)로 좌표한다 — 삭제된 채점기록(`EVAL-*.md`)을 인용하지 않는다(2차 자료 의존·검증불가 차단). **grader 배포본에는 fixture명·줄번호를 제거한 익명 스니펫+표준 §근거만** 노출하고 출처 라벨은 조정자가 보유한다(`EVAL-METHOD.md §1.2` — 줄번호 노출과 blind 마스킹의 모순 해소).

| 항목 | FAIL 예시 | PASS 예시 |
|---|---|---|
| SD-3 빈혈 무복제 | Codex `catalog/published_service/stock.py:42` `stock__gte=quantity` | Claude `catalog/.../product.py:35-46` `Product.deduct_stock()` |
| SD-6 계층순수성/P1a | Codex `create_order_app.py:70-79`(app이 비즈예외 catch→status snapshot) + `orders_api_router.py:87-124`(죽은 핸들러) | Claude `api_order.py:61-63` `Status(201, OrderOut)` 성공만 + 중앙핸들러 발화 |
| SD-7 컨텍스트 통신 | Claude `p1a-v3 order_api_router.py:26`·`create_order_app.py:17`(ACL 밖 presentation·application이 catalog 도메인 **예외** 직접 import = 번역 ACL 미격리) | Codex `catalog_acl.py`(OHS만) · Claude `smoke4 product_stock_acl.py`(catalog 결합이 ACL에만 격리 — 미이주 직접통합은 표준 §2 허용) |
| SH-4 Django앱 위치 | Codex `catalog/models.py`·`catalog/migrations/` 루트(마스크 C: 기존앱·판정적재면 위반) | Claude `application/catalog/infra_layer/django_catalog/models/` |
| SH-7 협력포트 위치 | Codex `application_layer/create_order/port/` | Claude `domain_layer/order/port/` |
| SH-9 단일 레이아웃 | Codex `catalog/test/`+`catalog/tests/` 공존 | (단일 test 디렉터리) |
| SH-6 명명 | (8벌 위반 0) | 전 픽스처 `Interface`/`Impl`/`_repo.py` 0건 |
| Q-1 스코프 | Codex 멱등성 `Idempotency-Key` 필수(task 미요구) / **Codex 협상 레이어 발명**: **406** Accept 협상(`fklive-codex api_orders.py:43-86` `_parse_media_range` q파싱; §6.3:443-444 'single repr이면 406 불필요' escape-valve **직격**) + **415** Content-Type(발명 범위이나 본문검증이라 *literal 위반 아님*·§7.2 계약·Codex 구현은 §6.3 레시피 아닌 post-hoc=**underdetermined**); 뿌리=`design-spec.md:123-126` architect 협상 레이어 전체 / Claude 합산 정규화 | 요청 범위 내 모델 / **Claude 406/415 의도적 공백**(`fklive-claude design-spec.md:81` 명시 배제 — 406은 단일표현이라 escape-valve 정합·415는 표준상 선택적 미구현) |
| Q-4 메커니즘 | final-claudeA `config/db_backends/sqlite3_immediate/base.py` | p1a-v3 양쪽 순수 version CAS |
| Q-5 마이그레이션 | Claude `django_catalog/migrations/0001_initial.py:14-25`(기존 0001 재작성) | 신규 앱 0001 + 별도 0002 expand |
| NJ-2 operation 얇음 | Codex `smoke2-codexB/.../create_order/api_orders.py:108-213`(operation이 `json.loads(request.body)` 수동파싱+수동검증+7 except status 분기) | Claude `p1a-v3-claude/.../api_order.py:61-63`(schema 바인딩→service→`Status(201,…)` 매핑만) |
| NJ-4 status 선언 | `poc-codex/.../api_orders.py:209,211`(`response={201}`만·오류 6종은 `openapi_extra`로 → 가시성O·`response=` 위반) | Codex `p1a-v3-codex/.../api_orders.py:41-49`(`201/400/404/406/409/415/422` 전부 `response={}` 선언) |
| NJ-5 문서화 | Codex `final-codexB/.../api_orders.py:31` 반환타입 `Union[...,HttpResponse]`(어댑터 누수) | p1a-v3 양쪽 `operation_id`+`summary`(+Claude `tags`) |
| FC-3 도메인 정합 | (반례) 차감 부호 역전·음수 재고 허용·인과 역전 | 8벌 모두 재고 차감 방향 정상 |
| Q-3 동시성 결정성 | Codex `test_..._api.py` `Barrier(2)`+ThreadPool 실스레드 레이스(스케줄러 의존=비결정·flaky) | 결정적 CAS-스파이(stale `version` 1회 주입→수렴) |

> NJ-1·3·6·FC-1은 8벌 known-bad 부재(전부 준수/미관측) — FAIL은 *표준 위반 정의*로 채점(앵커 없이도). 외부 baseline·합성 반례는 선택적 보강.

---

## v2 변경 요약 (적대 리뷰 반영)
- **북극성 정직화**: "DDD·houserules 실현" → "**규칙 준수 + 기능 정확성**"; baseline 차별가치·미시 유지보수성·보안(누출 제외)·명세 품질을 *명시적 비측정*으로 선언(과대주장 제거).
- **FC(기능 정확성) 신설**(치명) — 골든 오라클·mutation·도메인 정합. "재고 늘어나는 API 全PASS"(CF-1)·"틀린 도메인 모델"(CF-2) 차단.
- **PASS 바=표준 규칙, 앵커=예시**(임계값 아님) — 순환(C2)·홀드아웃 오염(C1) 해소.
- **SD-6 의미변종=치명 FAIL** — 스크립트 텍스트 게이밍(C3 Goodhart) 차단.
- **Q-3 Barrier 레이스=비결정 FAIL 앵커**(CF-7).

## 동결 전 결정 (항목 차원) — **v3 해소(2026-06-02)**
> 전부 `EVAL-METHOD.md §0.1` 해소표로 확정. 아래는 항목-차원 5개의 결과.
1. **치명 게이트 목록** — SD 전부 + FC 전부 + SH-1·2·4·7 + (조건부)NJ-1·2 + **Q-4(치명 승격 확정)**.
2. **마스크 C "판정 적재"** — `EVAL-METHOD §1.1.M` 이진 하위질문으로 조작화 + 경합 보수=*적재됨*.
3. **FC-1 골든 오라클** — **적대 grader가 프롬프트 직후·코드 열람 전** 작성, 작성자⊥채점자(§1.4).
4. **S-NINJA 배치** — NJ-1·2 조건부 치명, NJ-3·4=비치명 '강'(Q 카운트 정규 편입, 강-FAIL 시 상한 '중'), NJ-5·6 경미(§2.1·§2.4).
5. **빠지거나 과한 항목** — 현 차원 집합 동결(추가/삭제 없음).

(채점 절차·집계·bisect·결승선·과적합 방지·**산출 형식(§6)** = `EVAL-METHOD.md`)
