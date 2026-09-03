# 항목 G ⓪ 증거 수집 — boundary-imports 블록의 «예외 클래스 소비 import» 결손 실측

작성 2026-09-04 · 읽기 전용(spring·kkebi·dddjango 무수정) · 산출물은 이 디렉터리(`fr2/G/`)에만.

## 1. 측정 방법

| # | 측정 | 방법 · 산출 파일 |
|---|---|---|
| 1 | 블록 있는 명세 7건 대조 | `extract_blocks.py` → `blocks.txt`(블록 전행) · `prose_classify.py` → `prose_classify.txt`(블록 밖 산문에서 잎+예외+행위+port 동시 출현 행) · 카탈로그 G1 원본은 spring git `9ee721e`(G1 승인 커밋)에서 `git show`로 복원(`catalog-spec-G1-9ee721e.md`) — 현재 파일은 Phase 2 진화 후 판본(5행·09-04 01:07)이라 G1 판본(6행)과 다르다 |
| 2 | 코드 실측 | `code_survey.py` → `code_survey.txt`(7 BC `driving_layer/**` 의 `application_layer.port` import 전수) + `git log --all -S/-G` 이력 검색 |
| 3 | #93 발화 이력 | spring `.dddjango/**`·`docs/superpowers/orders/lane/**` grep `#93\b` · kkebi 동일 + `context-isolation` 검사기명 grep |
| 4 | 실행기 소비 방식 | `design_pregate.py` 소스 인용 + 격리 복제(`spring/`·`git checkout --detach e1294f5` = 카탈로그 G0/G1 기준선) 위에서 specA(G1 원본)·specB(G1+OHS 예외 import 2행) 실측 → `runA.out`·`runB.out`·`reportA.md`·`reportB.md` |
| 5 | 규범 현황 | `design-architect.md` L87-92 · `agent-design-architect.ttl`(R-3427/s005/b36) · houserules `#92`(final.md L206) · `check-context-isolation.py` L226-237 · architecture-ddd final.md grep |
| 6 | 무손실 | 1·2 결과에서 «블록 밖 예외 소비 import 서술이 있는 명세» 계수 |

## 2. 표 — 명세 7건 (블록 vs 산문 vs 코드)

블록 = `<!-- machine: boundary-imports -->` ```imports 펜스. «port 예외행» = 블록 안에서 driving 잎(controller/OHS)이 `application_layer/port/**` 를 import 하는 행.

| 레인(명세 판본) | 블록 행수 | 블록 안 driving잎→port 행 | 산문의 driving잎 port-예외 소비 서술 | 분류 | 현재 코드 driving잎→port import |
|---|---:|---:|---|---|---:|
| fortune-record (G1 quintuple-prime 09-02) | 27 | 0 | 없음(잎은 `bc_error_schema.FortuneRecordNotFoundError` 만 — driving 내부) | 언급 없음 | 0 |
| notification-email-template (G1 09-02) | 48 | 0 (port 행 5 = 전부 driven adapter·test) | L168 «OHS `send_email_notice` 사슬 불변» — 신규 소비 0 | 언급 없음(불변) | 0 |
| notification-bc (G1 09-02) | 22 | 0 (port 행 6 = accounts ACL adapter·test/fake) | L41·L43·L50·L108: OHS가 port 예외 `EmailNoticeTransportError/RenderingError` 를 **use_case 모듈 `__all__` 재수출 경유**로 import·catch — «#93 안 걸림» 명시 설계(`query_translation` 선례) | **블록에 있음**(재수출 경로 행 L397: `email_notice_service.py from …send_email_notice_use_case import SendEmailNoticeUseCase, EmailNoticeTransportError, EmailNoticeRenderingError`) | 0 (현재 코드 `email_notice_service.py:6-8` 동일 경로 실증) |
| fortune-reading **P4 판본 @919440c**(STOP-149 시점) | 15 | 0 | §5.10 L649-653 + L284·L327·L663: controller/OHS가 `failure.cause` 를 «exact ten concrete exception» 타입으로 분기 — 그 안에 port 예외(`ReadingBundleContractMismatch`·`TranslationContractMismatch`·`RetrievalContractMismatch`·`InvalidTranslationRequest`; `port/query_translation/exception.py` L2182) 포함 → port import 함의 | **산문에만 있음(암묵 — 타입 분기 서술)** | — (P4 WIP 미커밋: `git grep 919440c` 0건·`-G` 이력 0건) |
| fortune-reading 현재(09-03) | 17 | 0 | L337 «cause type을 import/inspect하지 않는다»·L1185 수리표 `#93/#96 controller 3/3·OHS 3/3 = 6/6 → port exception import 0` | 언급 없음(수리 후) | 0 |
| chat-relay-2a (G1 09-03) | 1 | 0 | 없음 | 언급 없음 | 0 |
| media-library (G1 09-02) | 28 | 0 | 없음 | 언급 없음 | 0 |
| fortune-catalog **G1 판본 @9ee721e** | **6** | 0 | **L167**(브리프의 §167): «각 함수는 `ActiveServiceBundleContractMismatch`·`RelationTableContractMismatch`를 잡아 `_CatalogUnavailable` variant로 접는다» · L117 «use case는 잡지 않고 전파 … OHS 서비스가 이를 잡아» · L501 동일 — **동시에 L57**: «`catalog_inquiry_service.py`는 … `application_layer/port/**`를 import하지 않는다(#96)» (명세 내부 모순 — 블록은 L57 쪽과 일치) | **산문에만 있음(명시)** | — (S4 커밋 전 수리 · 이력 0건) |
| fortune-catalog 현재(09-04) | 5 | 0 | L100·L186·L511: use case 번역 · OHS port import 0 · «#93 관련 import는 전부 intra-BC라 경계 import 블록에 없다(fail-closed 부재가 정답)» | 언급 없음(수리 후) | 0 |

카탈로그 G1 블록 6행 원문(`catalog-spec-G1-9ee721e.md` L489-497): `composition_root/dependency_wiring.py` ×3(`ontology_canonical`·`service_runtime`·`rdflib Graph`) · `driven_layer/adapter/relation_table/rag_runtime_adapter.py from rdflib import Graph` · `test/unit/test_pack_query_equivalence.py`·`test_relation_table_adapter_synthetic.py from rdflib import Graph`. (현재 5행 = composition의 rdflib 행 제거 — #85 교정.)

코드 대조 계수: 현재 7 BC(accounts 포함 8 디렉터리) driving 잎의 `application_layer.port` import **0건**(예외행 0) — «블록에 선언 안 된 실코드 import» 현재 0. spring 전 ref 이력에서도 driving_layer 에 `application_layer.port` 문자열이 들어간 커밋 **0건** → 카탈로그 S4·리딩 P4 의 위반 코드는 커밋 전 수리됐고, 문서(REPORT·STOP)만이 증거.

## 3. 표 — #93 발화 이력

spring(26런): `#93` 문자열 보유 파일 12 중 pregate-report 6건은 전부 S3 사각 상용구(«BC 내부 계층 의존 오설계(#92/#93류) … 원리적 예보 불가» — 리딩 33회 등 합계 51회) = 발화 아님. 실제 발화/처리:

| 런 | 시점 | 발화 형태 | 처리 | 블록 채널 |
|---|---|---|---|---|
| openai-rag-generation | 08-27, S4 Green 후 registry_gate(2.17.9) | `design-loopback-g1-doubleprime.md` L25 «#93 … driving leaf가 application port를 import» + L26 «#96 driving leaf가 port exception을 import» | G1″ loopback: «application이 port failure를 domain-owned capability exception으로 번역 · OHS는 그 concrete exception만» | 블록 없음(구형) |
| fortune-reading P4 | 09-02 21:50 STOP-149(P4 R4 audit 뒤 §6.3 registry gate 149건) | `#93·#96 = 6+6`: «HTTP controller·evidence OHS service가 `application_layer/port/**/exception` 모듈을 import(carrier cause 타입 분기 때문)» | 발주자 결정 A(09-02 21:59) → G1′: carrier에 category StrEnum 4종·잎은 exhaustive 분기·port exception import 0 (현재 명세 L1185) | 블록 있음·port 행 0 → 산문 암묵 |
| fortune-catalog | 09-03~04, Phase 2 S4(854ba47) | REPORT-fortune-catalog «설계 진화 3»: «#93 driving 잎 OHS가 `application_layer/port/` import 금지 → use case가 port 예외를 app-layer 실패로 번역» | STOP 없이 architect/coder 역할로 집행 · 승격 부품 `<use_case>_source_unavailable.py` | 블록 있음·port 행 0 → 산문 명시(L167) |
| service-policy(참고) | 08-30 | `scope-evidence-accounts-branch.md` L642 규범 서술: «포트 예외를 잡지 않는다 — 잡으려면 `application_layer/port/`를 import 해야 하고 그것이 곧 blocker» | 발화 아님(선행 인지) | — |

kkebi(21런 · 명세 20건 전부 machine 블록 0 → 블록 대조 불가, 발화 이력만): `#93` 은 design-spec 7건에만 등장(STOP/REPORT 0).

| 런 | 시점 | 발화 형태 | 처리 |
|---|---|---|---|
| tarot-reading | 08-25(브라운필드 이관) | spec L241/L667 code-only 표: `#93(3)+#96(3)+#108(1)` — `catalog_controller.py`·`deck_controller.py`·`paid_reading_entry_service.py` 의 `application_layer/port/**` import | 설계 개정: use case result/operation failure 로 정규 |
| billing-payment-http | 08-26 | refactor-scope L17 `check-context-isolation` exit **2** · spec §3.7(L112-116): `payment_controller` 만 driving_layer 전체에서 port 예외 import(실측 grep) | §3.7 «port→domain 예외 번역(use case boundary) · 컨트롤러 port import 0» |
| identity-bc·restore-purchase·review-bc·consultation-bc·saju-remainder | 08-23~25 | 규범 인용만(«컨트롤러는 port 예외를 import·catch할 수 없다(#93/#95)») | 발화 아님 |

## 4. 실행기 소비 방식 + 격리 실측

- 문법(`design_pregate.py` L48-58): boundary-imports 1행 = `<소비 파일 경로><탭|2+공백><import 문 그대로>` — 행 종류(경계/intra-BC) 제한 없음.
- `_parse_imports`(L495-521): 행 전부 `plan.import_rows`(실존 판정) + 소비자가 file-plan `add` 면 `entry.imports` 에 결합. `render_stub`(L785-810): `entry.imports` 를 스텁 최상단에 **원문 그대로 방출**. 이어 `registry_gate.py <사본>` 이 스텁을 검사(L27-29).
- 사각 목록 S3(L1527-1528, 현재 문면): «유도 삽입은 규약 준수형이라 예보 불가 · **블록에 기재된 경계 import 는 스텁에 방출되어 예보된다 — 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖이다**». 이 후반 절은 `2fbc111`(09-03 21:53) 추가 — 카탈로그 G1 pre-gate(09-03 13:24 KST) **이후**. 카탈로그 리포트의 S3 는 전반 절만.
- **격리 실측**(복제 `spring/` @ `e1294f5` = 리포트 기준선 SHA · `--base HEAD` · 실행기 = 현재 저장소 `design_pregate.py`):
  - specA(G1 원본, `--block-hash` = `6cf8e2ffdfc3` = 실제 pregate-report 4번째 런 해시와 **일치**): exit 0 · 귀속 0 · green (실제 G1 결과 재현 · 1:18).
  - specB(= specA + OHS 2행 `catalog_inquiry_service.py from …application_layer.port.{active_service_bundle,relation_table}.exception import …`): exit 2 · **귀속 3건 = `#93` ×2(check-context-isolation · 두 port exception 모듈) + `#96` ×1(check-event-publish «driving 잎이 포트 선언을 import»)**.
  - ⇒ «블록에 적혔다면 #93 이 pre-gate 에서 예보됐을 것» **성립**(측정됨).

## 5. 규범 현황

- `design-architect.md` L90 = 온톨로지 `s005/b36` → **R-3427**(Obligation · rev3 `@2026-09-03b` · prefLabel «경계 import 표 — 검사기 판정 관련 경계 import 전부(테스트 파일 포함) · 3단 실존 판정 입력 …»). 문면: «검사기 판정에 관련되는 **경계 import 전부**를 … 성문한다 — 타 BC OHS/contract·framework 공통만이 아니라, domain/contract 칸의 서드파티 라이브러리와 **테스트 파일의 경계 import 전부**(factories/타 급·타 BC OHS/published 계약 소비)까지. 파일별 전체 import 를 강제하는 것은 아니다 — **경계만 성문한다(그 밖의 import 는 구현 재량)**.» 열거 예시는 전부 BC 밖(타 BC·framework·서드파티·테스트). 같은 절 L87(b33 → R-3424·R-3431): «채널에 없으면 «부재»로 전사(fail-closed)». L91(R-3428) 물리 신호 어노테이션은 테스트 입장 표 전용 — 예외 import 와 무관.
- 문면 해석 재료: 두 독법이 공존. ⓐ 머리절 «검사기 판정에 관련되는 … 전부» → #93 이 판정하는 잎→port import 도 포함. ⓑ «경계» + 열거 + «그 밖의 import 는 구현 재량» → intra-BC 계층 횡단은 경계 아님. 카탈로그 architect 는 ⓑ로 읽었고 이를 명문화(현재 명세 L511 «#93 관련 import는 전부 intra-BC라 경계 import 블록에 없다 … 이 셋은 «타 BC/framework/서드파티» 경계가 아니므로 아래 블록에 넣지 않는다»). 리딩 P4 도 port 행 0. → 현재 문면은 «예외 클래스 import 포함»으로 **단정 못 읽는다**(ⓑ가 실전 2회 선택됨).
- #93 정의(`check-context-isolation.py` L226-237): loc ∈ {api, driving, cron_job, event_subscription, ohs} 가 tgt == `app_port` 이면 발화 — **예외 모듈에 한정되지 않고 `application_layer/port/**` 전체**. 근거 houserule `#92`(final.md L206): «driving_layer 의 잎은 `application_layer/<area>/` 아래만 의존 — 예외는 넷: 도메인 exception·값 객체(#95) · `composition_root` `build_`(#97) · 남의 `published_event/`(#507) · framework 계약·스키마».
- architecture-ddd final.md: «port 예외를 잎이 잡는가/use case 가 번역하는가»의 **직접 성문 없음**(grep: 포트 예외·예외 번역·응용 서비스+예외 → L644 판정 소유 절·L365 ACL 절만). 번역 방향은 #92/#93/#95 의 귀결로 현장 명세가 도출(kkebi identity-bc L255 «use case 소유 번역» · spring service-policy L642 · 카탈로그 진화 3). ⇒ «설계 진화 3»은 규범(#92/#93)과 정합 방향이나, 성문 규칙이 아닌 검사기 귀결.
- 부기: notification-bc 의 «use_case `__all__` 재수출 경유 catch»는 #93 을 텍스트로 우회(재수출 모듈 경로가 `application_layer/<area>/`). openai-rag loopback L25 는 «alias/re-export는 만들지 않는다»고 적어 규범 긴장 가능 — 본 항목 범위 밖, 기록만.

## 6. 판단 재료

- **≥2 레인 여부**: 블록 보유 7건 중 «산문 서술 ↔ 블록 부재 ↔ 코드 #93 발화» 동형 **2건**(fortune-catalog G1 명시 · fortune-reading P4 암묵). 블록 없는 레인까지 넓히면 spring +1(openai-rag G1″) · kkebi +2(tarot·billing) = driving 잎 port 예외 import 로 #93 이 실제 발화한 레인 **5**(spring 3·kkebi 2).
- **채널 전사 결손 vs 사각**: 실행기는 블록 행을 원문 방출·검사(specB 실측 #93 ×2 예보) → 실행기 사각 아님. 결손은 (i) architect 가 R-3427 «경계»를 BC 밖으로 읽어 행을 안 쓴 **채널 전사 결손**, (ii) 카탈로그 G1 명세의 내부 모순(L57 «port import 0» vs L167 «port 예외 catch») — S2 ④형 사각(의미 모순 미검출)이 겹침. S3 후반 절(2fbc111)은 이미 «산문에만 적힌 경계 import 는 표면 밖»을 성문했으나 «예외 소비 import 를 블록에 적어라»는 architect 측 의무 문면은 없음.
- **규범 문면**: R-3427 은 «경계» 열거가 BC 밖뿐 → 후보 처방(«검사기가 판정하는 intra-BC 계층 횡단 import — 특히 driving 잎의 port 예외 소비 — 도 기재») 1줄은 문면 공백을 메우는 성격. 대안 독법 ⓐ만으로는 실전 2회 모두 ⓑ로 흘렀다.
- **무손실**: 조항 추가 시 «형식 red»(블록 밖 예외 소비 import 서술 보유)가 되는 명세 — **현재 7 판본 기준 0건**(카탈로그·리딩 모두 수리 후) · G1/P4 당시 판본 기준 **2건**(카탈로그 G1 명시 1 · 리딩 P4 암묵 1 — 암묵은 «타입 분기» 서술을 import 로 읽어야 하므로 형식 검사기가 기계 판정하긴 어렵고 architect 자기 점검용). notification-bc 는 재수출 경로 행이 이미 블록에 있어 무영향. 기존 블록 행 파싱·실존 판정 문법 변경 0.
- **미측정**: 리딩 P4 위반 코드 원문(미커밋) · kkebi 5건의 블록 대조(구형 명세) · 조항 추가 뒤 architect 형식 반송 증가율(실전 레인 필요).
