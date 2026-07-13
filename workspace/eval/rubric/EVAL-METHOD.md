# dddjango 평가 방법론 v4 — 채점·집계·완료·과적합 (집행 사양)

> **상태**: v4 동결(2026-07-13). 평가 *항목*은 `RUBRIC.md`, 제품 정책 정본은 `workspace/reference/spec.md`다. v3 이하 결과는 당시 기준의 역사적 기록이며 v4로 소급 재판정하지 않는다.
> **측정 대상(사용자 확정)**: 산출물의 *규칙 준수 수준(절대값)* + *기능 정확성*. **baseline 통제 arm 없음.** 판정 바=표준 규칙(§근거 조항), 앵커(RUBRIC §E)=예시.
> **인과 한계(과대주장 차단)**: 이 평가는 산출물이 규칙을 *지킨 수준인가*를 측정한다 — *플러그인이 규칙을 지키게 야기했는가*(baseline 대비 인과 기여)는 측정 범위 밖이고 본 방법으론 주장 불가(§3 N=1·차별가치 비측정과 정합).
> **표준 버전 시점(소급 FAIL 금지)**: fixture는 *그 산출 시점의 플러그인 표준 버전*으로 채점한다. 특히 v3의 touched-app 물리 이주·state-only migration 보정 규칙은 v4에서 폐기됐으며, v4의 migration 비소유·현재 계약 테스트 원칙을 과거 fixture에 소급하지 않는다.

---

## 0. v4 동결 상태 게이트 (채점 착수 전 필수)

**v4 기준은 채점 전에 동결한다.** 채점 도중 발견한 결과로 판정 기준을 바꾸지 않으며, 변경이 필요하면 다음 버전으로 올리고 소급하지 않는다.

### 0.1 동결 결정표 (v4 확정)
| # | 결정 | 확정값(2026-07-13) |
|---|---|---|
| 치명 게이트 목록 | **SD 전부 · FC 전부 · SH-1·2·3·4·7 · (조건부)NJ-1·2 · Q-4·Q-5·Q-6** |
| Q-4 메커니즘 치명? | **치명** (커스텀 DB백엔드·`DatabaseWrapper`·PRAGMA·몽키패치 = SD-6 계층순수·메커니즘소유권과 직결) |
| N 정책 | **전 항목 N_grader≥3 blind + 적대 1명**(정본 full). 비용 인지는 §4.4·부록 |
| FC 측정 범위 | **FC-1 골든오라클 8벌 전수 · FC-2 mutation 8벌 전수**(full) |
| 라이브 발화(§4 #4) | **완료 필수 아님 — 정적/라이브 분리 보고**(§4.3). P1a·P2·P3 게이트 정의는 §4.1 |
| brownfield 분류 | **baseline에 존재한 persistence app은 touched 여부와 무관하게 위치·migration tree를 보존**. baseline 불명은 자동 FAIL 대신 보류·의미 레인으로 보냄(§1.1.M) |
| FC-1 등록 주체·시점 | **§1.4 확정**(적대 grader·프롬프트 직후·코드 열람 전) |
| S-NINJA 치명 배치 | **NJ-1·2 조건부 치명, NJ-3·4=비치명 '강'(§2.4 Q-편입), NJ-5·6=경미** |
| 빠지거나 과한 항목 | **현 차원 집합 동결**(추가/삭제 없음). **개정 2026-06-07·DR-47: NJ-7(오류 변환 완전성·catch-all) 1회 추가**(§6.2 선재·33항목 측정 차원 부재 빈틈·비치명 '강'·동기 정직표기 §5.2). **동결 해제 2건째 2026-06-08: NJ-1 *판정기준* 개정**(차원 수 불변·신설 아님 — 함수형 `NinjaAPI`+`Router`만 합격이던 결정 레인을 `NinjaExtraAPI`+`@api_controller`/`register_controllers` 허용으로 확장; 판정기준은 사전등록 동결 대상이라 명시 해제. 근거: ninja-extra 클래스 컨트롤러 도입). **동결 해제 3건째 2026-06-08: SH-3 치명 격상 + §632-(2) 면제 폐지**(차원 수 불변·치명 배정+판정기준 변경 — 데이터소스 골격 무조건·종류 폴더 부재 FAIL. 근거: 표준 개정 `architecture-ddd:632`·`houserules:21`, fixture 동기 아님). **동결 해제 4건째 2026-07-13: 기존 Q-6을 치명으로 격상**(차원 수 불변; 제품의 현재 계약 테스트 완료 전제를 집계에 실제 연결하고 고정 oracle을 추가). 발견1 SH-1/4 마스크 C 정정은 기준 불변·적용 교정이라 해제 불요. |

### 0.2 고정 입력 규율
런 리셋·고정 게이트 답(BC배치·렌즈·API스택·G1/G2 승인 기준·thinking)은 **각 태스크 CRIB**(fixture *밖*)에 둔다. CRIB에는 사용자 입력·게이트 답·runner/environment만 두고 기대 inventory·조정표·판정은 별도 evaluator-only oracle로 분리한다. runtime에는 선택 fixture를 control tree 밖의 fresh workspace로 복사한 뒤 CRIB 값만 전달하며, CRIB 파일·oracle·builder/doc source 자체는 노출하지 않는다. **표준 기능 태스크 프롬프트(라이브 `/dddjango` 입력 정본·verbatim)는 `tools/FC-GOLDEN.md`, 현재 계약 테스트 수명 시나리오와 판정 oracle은 `tools/Q6-CURRENT-CONTRACT.md`에 박제**한다. coordinator 정리본 `scope.md`(Phase 0 "무엇/경계" 확장)가 아니라 사용자 입력 원문과 사전등록 oracle이 정본이다. *(구 `RETEST-HANDOFF.md`는 폴더 재구조화로 제거됨 — 고정 게이트 답의 정본은 태스크별 CRIB이며, 본 문서 §1.4 골든표 동결과 함께 freeze 산출물에 포함한다.)*

### 0.3 v3 역사적 선결 작업 (보존 기록; v4 blocker 아님)
> 아래 항목은 v3 평가 프로그램의 미완 기록이다. v4 기준의 동결·채점 자격에는 영향을 주지 않는다.
1. **8벌 실경로 박제** — ✅ §5.1에 실재 디렉터리명으로 교정 완료(livefire·p1a-v3=`-codex/-claude`).
2. **6벌 CRIB 정본** — `smoke2-{codexB,claudeA}`·`p1a-livefire-{codex,claude}`·`p1a-v3-{codex,claude}` CRIB 부재(현재 `final-*`만 존재). 고정 게이트 답 동결에 필요. ⚠️ p1a 계열은 이미 런이 돌아 *사후 재구성*이라 "채점 기준이 아닌 *런 당시 입력 기록*"으로 한정 명시(§5.4 "결과 본 뒤 기준 변경 금지"와 긴장 회피).
3. **FC 사전등록 산출물** — 태스크-독립 골든 행위표(재고10·주문3→201∧잔7 / 재고2·주문5→409∧불변) + mutation 3종 논리 정의 + 픽스처별 실행 어댑터(조정자 작성). 코드 열람 전 타임스탬프·미열람 선언 동봉(§1.4).
4. **결정 스크립트(선택)** — SH·NJ·Q-4·SD-7(FAIL방향)은 수작업 grep로 갈음 가능했다. v4 Q-5는 migration 내용을 해석하지 않고 baseline↔head 경로·바이트 fingerprint 불변만 판정한다.

---

## 1. 채점 프로토콜 (결정 레인 ∥ 의미 레인)

### 1.0 역할 분리 (blind 집행 메커니즘)
blind는 *설계 의도*가 아니라 *집행*이어야 한다. 행위자를 분리한다:
- **조정자(coordinator)** 1명: 결정 레인(스크립트/grep)을 실행하고 결과를 **봉인**한다. 산출물 출처(런타임·디렉터리명·앵커 라벨)를 보유하되 grader에게 넘기지 않는다.
- **grader N_grader≥3**(조정자와 *별개 세션/인격*): 봉인된 결정 결과·앵커 출처라벨·런타임명을 **받지 못한 채** 의미 채점만 한다. 중 **1명은 적대 grader**("이 산출을 통과시키지 마라").
- **사후 대조(§1.3)**: 조정자가 봉인 해제 후 결정 ∥ 의미를 나란히 놓는다.
- 한 행위자가 결정·의미를 겸하면 blind가 깨지므로 금지. FC-2 mutation·Q-6 테스트 실행(결정 레인)도 조정자가 수행, grader는 결과만 의미 해석.

### 1.1 결정 레인
- **구조-인지 grep/스크립트** (경로 고정 금지 — `orders`vs`order`·포트 위치 이동에 강건).
- 산출 = `{신호 有/無}` + 줄 인용. **각 항목에 "원리상 못 보는 것" blind-spot 카드** 동봉.
- 플러그인 runtime backstop과 평가 도구는 역할이 다르다. runtime backstop은 저자유도 금지선을 막고, 평가는 아래 결정 레인과 의미 레인을 함께 집행한다. grep로 닫히지 않는 부분은 의미 레인이 1차 판정한다.

#### 항목별 결정-판정 표 (치명 결정 항목 우선; 구조-인지 명령)
| 항목 | 명령(개념) | PASS 신호 | FAIL 신호 | blind-spot 카드 |
|---|---|---|---|---|
| **SH-1** 컨테이너 | baseline에 확립된 앱 위치 규약이 있는가; 없으면 신규 앱의 부모가 `application/`인가 | 확립 규약을 따름, 없으면 `application/<app>/` | 확립 규약과도 다르고 기본 위치도 아님 | baseline 기존 app은 grandfather 대상. baseline root app이 있고 표준 컨테이너가 없으면 root 관례를 보존하며, 혼합 프로젝트의 기존 `application/`이 우선(§1.1.M) |
| **SH-2** 4계층 | baseline에 없던 신규 BC 아래 `{domain,application,infra,presentation}_layer/` 존재 | 신규 BC 4계층 물리분리 | 신규 BC의 누락/평면 | 기존 app을 맞추기 위해 물리 이주하지 않는다. 새 domain/application 계층이 기존 ORM을 adapter/repository로 감쌀 수 있다 |
| **SH-4** Django앱 위치 | 확립 규약이 없을 때 신규 Django app owner가 `infra_layer/django_<app>/`인가 | 확립 규약을 따름, 없으면 표준 위치 | 확립 규약과도 다르고 표준 위치도 아님 | `models.py`와 `models/*.py` package형을 함께 본다. baseline 기존 persistence app의 위치·AppConfig·ORM·`migrations/`는 보존하며, 이주하면 FAIL |
| **SH-7** 포트 위치 | `find -type d -name port`의 부모가 `domain_layer`인가 | `domain_layer/<agg>/port/` | `application_layer`/`infra_layer` | — |
| **SD-3** 무복제 | infra 리포의 CAS `update/filter`에 비즈조건(`stock__gte=`·`F()` 판정)이 있나(grep) | version/CAS 가드만 | `stock__gte=` 등 판정 SQL 복제 | helper 경유·동적 조건문은 의미 레인 |
| **SD-6** 계층순수성 | `check-error-centralization.py`(application_layer **한정**) + grep `from ninja`/`JsonResponse(` in domain | application HTTP변환 0 | application이 status 변환 | **스크립트는 application_layer만 봄** — presentation 수제응답·domain HTTP import·status:int 객체 흐름은 **못 봄**(의미 레인 필수) |
| **SD-7** 컨텍스트 통신 | 타 BC `domain_layer`/`infra_layer` 직접 import 있나(grep import 경로) | (의미) OHS/ACL 포트만 소비 | (결정) 타 BC 구체구현 직접 import | **비대칭**: FAIL 방향(구체 infra/domain 경로 import)은 grep로 *완전히 닫힘*; PASS 방향("그게 OHS 표면인가 concrete impl인가")은 catalog 공개표면 정의 의존 = **의미 레인 필수**. published_service 빈 패키지=OHS 부재도 FAIL |
| **SH-9** 단일 레이아웃 | 한 앱에 `test`+`tests`·`src`+`apps` 공존하나(`find`) | 단일 레이아웃 | 공존 | — |
| **NJ-1** 스택 | 신규 JSON API가 `NinjaAPI`/`NinjaExtraAPI` + (`Router` ∨ `@api_controller`/`register_controllers`)인가 vs `JsonResponse`/DRF(grep) | ninja Router operation **또는** ninja-extra `@api_controller` 컨트롤러 | plain view·DRF(greenfield) | 기존 확립 스택 존중은 houserules §1; 신규 표준=클래스 컨트롤러, 함수형 Router=레거시/415 격리 예외(둘 다 PASS) |
| **NJ-4** status 선언 | operation `response={...}` dict에 다중 status schema(grep `response=`) — **`openapi_extra`/`get_openapi_schema` 선언은 불충족**(§2.2 line111) | 오류 status가 `response={...}`에 | `response=`에 201(성공)만, 오류는 `openapi_extra`/핸들러에만 | **`openapi_extra`로 오류를 OpenAPI에 넣어도 NJ-4 FAIL**(가시성≠`response=` 선언); 진짜 미선언(핸들러-only·OpenAPI 부재)만 Q-2 |
| **Q-4** 메커니즘(치명) | `check-mechanism-ownership.py` + grep `DatabaseWrapper`/PRAGMA/monkeypatch | 표준 ORM만 | 커스텀 백엔드/PRAGMA/몽키패치 | 명세 승인된 메커니즘은 면제(의미 확인) |
| **Q-5** migration 비소유 | 작업 epoch별 migration opaque fingerprint, 전체 command transcript, 파일 변경 원장, G0→최종 전체 test path/hash delta와 변경 test diff를 의미 검토 | 모든 plugin 작업 epoch clean·전용 명령/테스트 개입 0·schema 영향 정직 보고 | plugin 귀속 migration add/edit/delete/move·전용 명령/테스트 개입·검증 인프라 오류 무시·schema 영향인데 배포 완료 주장 | user가 외부 owner의 귀속·완료·정지를 명시 확인한 epoch 간 delta는 중립 pause/rebaseline 증거다. fingerprint는 endpoint만 보며 명령 실행·중간 원복·DB side effect를 증명하지 못하므로 transcript·원장 부재나 dirty/untracked test delta 불일치를 PASS로 추정하지 않는다 |

> 나머지 항목(SD-1·2·4·5, SH-3·5·6·8·10, NJ-2·3·5·6, FC-1·2·3, Q-1·2·3·7)은 RUBRIC '레인' 칸대로 의미 레인(+해당 grep)으로 판정. Q-6은 아래 §1.1.T의 결정+의미 치명 판정을 적용한다. 결정-판정 표는 *치명+grep로 닫히는* 항목을 우선 명문화한 것이고, 미수록 항목은 의미 레인이 1차다.

#### §1.1.M brownfield grandfather 판정 (치명 게이트 입력)
RUBRIC §C의 적용은 baseline 존재 여부로 결정한다.
- **런 변경 집합** = baseline commit 대비 tracked 변경과 untracked 신규 파일의 합집합이다.
- **baseline existing**: baseline에 실제 `AppConfig`/Django ORM 모델 identity 또는 정적 등록이 지목한 로컬 app이 있으면 기존 persistence app으로 분류한다. migration package 존재만으로 app identity나 규약을 추정하지 않으며 migration 내용을 읽지 않는다. touched 여부와 무관하게 기존 위치·identity·migration tree를 보존한다. 표준 구조로 물리 이주·복제하면 SH-4/Q-5 FAIL이다.
- **결정 리포터의 저-recall 경계**: `check-structure.py`는 직접 `AppConfig`/Django ORM `Model` 상속만 기계 식별한다. 정적 `INSTALLED_APPS` 등록만 있는 app, 프로젝트 custom base를 통한 간접 상속은 여기서 existing/new를 확정하지 않고 의미 레인이 baseline 증거로 보정한다. 그런 근거가 있으면 리포터의 FAIL 신호만으로 최종 FAIL을 확정하지 않는다.
- **new app/BC**: baseline에 존재하지 않고 런이 새로 만든 app/BC에는 먼저 baseline의 확립 레이아웃 규약을 적용하고, 그런 규약이 없을 때만 SH-1·2·3·4 표준 구조를 적용한다. baseline root app이 하나 이상이고 `application/`/`src/application/` 표준 컨테이너가 없으면 root app 관례를 확립 규약으로 본다. 둘이 공존하면 표준 컨테이너를 우선한다. framework/external owner가 G0 전에 만든 빈 `migrations/__init__.py` scaffold는 존재할 수 있지만 dddjango가 scaffold나 numbered migration을 추가하면 Q-5 FAIL이다.
- **baseline unavailable**: 비-git·불완전 fixture처럼 baseline 분류가 불가능하면 기존 위치만으로 FAIL을 만들지 않는다. `보류`로 표시하고 의미 레인에서 증거를 보강한다.
- **도메인 책임**: 기존 persistence app을 보존하는 것은 도메인 판정을 ORM에 넣으라는 뜻이 아니다. 새 domain/application 코드가 repository/adapter를 통해 기존 ORM을 사용하며 SD-1~3으로 책임을 판정한다.
- **경합 규칙**: baseline 증거가 충돌하면 치명 FAIL을 추정하지 말고 인간 큐로 보낸다. migration fingerprint의 `exit 2`는 변경 주체를 단정하지 않고 즉시 pause한다. plugin 작업 epoch 안의 미해소 delta는 Q-5 FAIL이고, user가 외부 owner의 귀속·완료·정지를 명시 확인한 epoch 전환은 중립이다. baseline/I/O `exit 1`을 무시하면 Q-5 FAIL이다.

#### §1.1.T Q-6 현재 계약 테스트 판정
- **권위 순서**: 사용자 승인 요구와 G1 설계, 현재 공개·도메인·영속·지원·보안·규제 의무가 오라클이다. 기존 테스트·구현·변경 이력은 증거이지 권위가 아니다.
- **필수 inventory**: `surface/version`, `consumer/support`, `persisted data/event`, `deprecation window`, `security/privacy/regulatory`, `negative/absence`, `근거 경로`, `retain/end/unknown`을 조사한다. `unknown`을 G1 전에 해소하지 않으면 FAIL이다. 지원 종료와 관찰 가능한 부재 보장은 별도 칸이다.
- **변경 집합 대조**: 요구 변경마다 영향 테스트를 `retain/update/delete/add`로 분류하고 같은 변경에서 반영한다. 명시적 제거 승인 없는 침묵은 제거 근거가 아니다.
- **현재 의무 예외**: 구 API 버전·지원 소비자·deprecation 기간·기존 저장 데이터/이벤트·보안/규제·명시적 부재 계약은 현재 의무일 수 있으므로 “옛것”이라는 이유로 삭제하지 않는다.
- **history-only 금지**: 종료된 과거 스펙만 증명하는 영구 테스트를 추가·유지하거나, 그 테스트를 통과시키려고 옛 동작을 복원하면 FAIL이다. 회귀 witness는 현재 의무/속성을 계속 증명할 때만 유지한다.
- **characterization**: 조사·안전 리팩터링 중 임시 characterization test는 허용하지만 G2 전에 현재 계약 테스트로 승격하거나 제거한다.
- **runner**: 프로젝트가 선언한 테스트 명령·설정을 그대로 사용한다. `pytest`, `manage.py test` 등 특정 러너를 강제하거나 `--no-migrations`를 주입하지 않는다. 테스트 DB 구성 중 framework가 migration을 우연히 적용하는 것은 migration 검증으로 세지 않는다.
- **migration tests**: 외부 owner가 migration lifecycle 전용으로 식별한 테스트는 외부 소유다. 플러그인은 그 의미를 검토하거나 작성·수정·삭제하지 않으며 평가도 내용을 요구하지 않는다. 조정자는 G0→최종 전체 test path/hash delta·변경 원장·변경 test diff로 plugin 개입 여부만 확인한다.
- **실행 폐합**: 두 조정표의 모든 `retain`·`update`·`add` 경로와 프로젝트 전체 suite를 실제 실행해 command/result/count를 1:1로 연결한다. 현재 의무 누락·미실행·실패를 두고 완료를 주장하면 FAIL이다.
- **고정 추적**: `tools/Q6-CURRENT-CONTRACT.md`의 일곱 시나리오를 Claude/Codex 양 runtime에 같은 입력으로 적용한다. 하나라도 oracle과 다르면 Q-6 치명 FAIL이며 WEAK로 낮출 수 없다.

### 1.2 의미 레인 (결정 결과에 **blind**)
- **이진 하위질문**으로 분해("잘 지켰나?" 금지). 예 SD-6: "오류→status를 *고르거나 만드는* 줄이 operation·application·domain에 있나? (Y/N)+줄".
- **🔴 에러 경로 정독 의무(NJ-1·3·4·SD-6 — `poc-codex` miss 반영)**: operation 본문·backstop exit0만으로 NJ/SD-6 판정 **금지**. 모든 `@api.exception_handler`·problem 헬퍼·content-negotiation 데코레이터를 읽어 §6.2 대조한다. 이진질문: (Q-a) 에러 응답이 `ninja.responses.Response` 아닌 `django.http.JsonResponse`로 나가나?(Y=🟡 NJ-1 경미) (Q-b) 오류 status가 `response={}` 아닌 `openapi_extra`/핸들러에만 있나?(Y=NJ-4 FAIL). **양방향 보정**: §6.2가 *중앙 핸들러의 dict 빌드+`ninja.responses.Response` 반환*을 처방하므로 그 형태는 **준수**(SD-6 'raw 응답'·NJ-1 'plain leak'으로 over-call 금지·죽은 schema 아님).
- **필수 줄 인용** — 인용 없는 PASS 무효.
- **판정 바=표준 §근거 조항**; 앵커=예시로만 대조(임계값 아님).
- **grader 배포본 = 익명 스니펫 + 표준 §근거만**. fixture명·줄번호·런타임은 조정자 보유(grader 미수령) — 앵커 줄번호 노출과 마스킹의 모순(C-F4)을 *출처 비공개*로 해소.
- **N 표기 분리**: `N_grader`=*채점 grader 수*(≥3, 블라인드·런타임 마스킹). `N_run`(§4)=*완료 선언용 블라인드 런 샘플 수*(≥5). 둘은 다른 축이다.
- **치명 보수 판정**: *치명 항목*은 2:1 split이어도 1명이라도 줄인용 동반 FAIL이면 인간 큐 + 보수 FAIL. 비-치명만 2:1→WEAK. 차원별 일치율(κ) 보고(N_grader≥2일 때만 정의; Q를 N=1로 운용하면 κ 미보고).

### 1.3 대조 — 측정의 주 산출물
- 결정 ∥ 의미를 나란히. **`[결정 PASS ∧ 의미 FAIL]` = "의미적 변종"** 별도 플래그(라우팅은 §2.2).
- "결정 PASS면 의미 생략" 절대 금지 — 의미 레인은 *항상* 수행.

### 1.4 기능 정확성 측정 (FC)
- **FC-1 골든 오라클**: **(주체)** 적대 grader가 **(시점)** 프롬프트 수령 직후·코드 *열람 전*에 **(형식)** *태스크-독립 행위표*(입력상태,요청)→(기대 status,부작용) + 타임스탬프 + "코드 미열람" 선언을 freeze 산출물에 커밋(열람 후 수정 금지·git diff 검증). **행위표 ⊥ 실행 어댑터**(실측 교정): 행위표는 코드 미열람으로 8벌 공통 작성 가능하나 *실제 두드릴 route+요청 schema*는 픽스처마다 달라(동일 태스크라도 BC 분해 분기) **조정자가 코드 열람 후 어댑터를 짠다** — "미열람"은 행위표에만. **작성자 ⊥ 채점자**(골든표 작성한 적대 grader는 그 fixture 의미 grader 제외 → 그 픽스처 N_grader를 1 늘려 유효 3 유지). 실행=인수 테스트와 독립한 호출 스크립트로 `.venv` 실측. **명세·기존 테스트는 오라클 불인정**.
  - **러너**: FC-1 골든 행위 검증과 Q-6 스위트는 프로젝트가 선언한 명령·설정으로 실행한다. pytest 프로젝트면 pytest, Django test runner 프로젝트면 `manage.py test`를 사용한다. 수집 누락 위험은 러너 교체가 아니라 수집 목록·실행 개수와 대상 테스트의 실제 발화로 확인한다. 채점 편의를 위해 의존성을 설치하거나 `--no-migrations`를 주입해 fixture 환경을 바꾸지 않는다.
- **FC-2 mutation**: *논리 mutation 3종*(①차감 부호 ②핵심 판정 경계 `<`/`>=` ③핵심 status 값)을 fixture 열람 전 동결하되, **주입 사이트 = FC-1 골든이 두드리는 경로상의 핵심 판정 메서드 1곳**(조정자가 행위표 동결 후 코드 열람해 식별; **DB CHECK constraint는 도메인 판정 아니므로 제외**). 현재 계약 테스트가 프로젝트 선언 러너에서 red면 PASS, green이면 FAIL(vacuous). 수동 또는 프로젝트에 이미 채택된 mutation 도구를 사용한다.
- **FC-3 도메인 정합**: 의미 grader가 골든 결과+코드 정독으로 명백한 도메인 오류(음수 재고·차감 역전·인과 역전) 판정.

### 1.5 채점 결정성 가드 — 부정 단정·수집 오라클·런-정지 (2026-06-10 신설 · lastlive-claude 오채점 박제)

lastlive-claude 사건 교훈: 채점이 "테스트 0·테스트도구 0·pytest 미설치"로 **보류(미완성)** 판정했으나 실제로는 테스트 33개·Tier-1 4종이 채점 1시간 전부터 존재했다(런-정지 상태). 부재 단정을 뒷받침하는 측정 명령이 transcript에 없었다 — **"자기보고 불신"은 채점자 자신의 부정 단정에도 적용해야 한다.** 유력 혼동 = 직전 픽스처의 `test_*.py` 접두 관례를 다음 픽스처(`*_test.py` 접미)에 가정 + `requirements.txt`(불변)만 보고 `requirements-dev.txt` 누락. 세 가드는 결정 레인의 측정 무결성 절(freeze 밖·RUBRIC 라벨 무변).

1. **수집 오라클 의무**: 테스트 존재·개수 판정은 프로젝트 선언 러너의 수집/목록 기능 또는 실제 실행 출력으로 확인한다. pytest 프로젝트는 `pytest --collect-only -q`를 쓸 수 있고, 다른 러너는 해당 러너의 발견 결과를 사용한다. 파일명 관례만 보고 0건을 단정하지 않는다.
2. **부정 단정 = 출력 인용 의무**: "0건·부재·미설치·미작성" 류 단정은 그것을 산출한 **명령+출력 첨부 없이는 기재 금지**(§1.2 "인용 없는 PASS 무효"의 대칭 — 인용 없는 *부재 단정*도 무효). 도구 부재 단정은 `pip list`(또는 site-packages 목록)와 **매니페스트 전수**(`requirements*.txt`·`pyproject.toml`) 둘 다 인용.
3. **런-정지 확인**: 채점 착수 전 픽스처 최신 mtime(`.git`/`.venv`/캐시 제외)을 기록하고 채점 시작 시각과 대조해 헤더(§6.2)에 박제. 미래 mtime·채점 중 변화 감지 = 진행 중 런(움직이는 표적) → **채점 보류**.

**소급 미적용**: 신설 이후 채점분만 구속(§1.1.T 패턴 정합). 당사자인 lastlive-claude 채점지는 in-place 사후정정 완료.

---

## 2. 집계 (사전식 lexicographic — 가중 평균 금지)

```
1) 마스크 C(§1.1.M) 적용.
2) 치명 게이트(치명=SD 전부·FC 전부·SH-1·2·3·4·7·(HTTP operation 존재 시)NJ-1·2·Q-4·Q-5·Q-6):
   하나라도 FAIL → 픽스처 전체 FAIL, 종료.
   ※ 치명 항목의 [결정PASS∧의미FAIL]도 여기서 FAIL(§2.2).
2.5) 실질성 관문(§2.3): degenerate면 치명 FAIL.
3) 비-치명 항목의 의미적 변종 ≥1 → "준수" 라벨 금지(상한 WEAK).
4) 통과 시에만 TIER-Q 등급(§2.4).
```

### 2.1 치명 집합·조건부·강 (정본 = §0.1; 세 곳이 한 목록)
- **치명 정본 목록**(§0.1·§2 step2 의사코드와 *동일 집합*): SD-1~7 · FC-1~3 · SH-1·2·3·4·7 · **(조건부)NJ-1·2** · Q-4 · Q-5 · Q-6. Q-5는 migration lifecycle 비소유 경계, Q-6은 현재 의무의 거짓 삭제·history-only 영구화·임시 characterization 잔존을 막는 완료 전제이므로 v4에서 치명이다.
- **NJ 조건부**: HTTP/JSON operation이 **하나라도 있을 때만** NJ-1·2가 치명. 순수 도메인/CLI/배치/서버렌더 픽스처 → S-NINJA 차원 전체 **N/A**(FAIL 아님, 게이트 미적용).
- **NJ-3·4·7 ('강')**: 비-치명이나 §2.4 Q 카운트에 *정규 항목으로 편입*(현재 사문화 해소) — '강' 항목 FAIL은 품질 상한을 '중'으로 강등. NJ-5·6=경미(정규 카운트, 강등 없음). **NJ-7**(오류 변환 완전성·catch-all, DR-47 추가)=강 — catch-all 부재/되던지기로 미식별·비-retryable이 problem+json 단일변환점 우회 시 FAIL(결정 레인 grep `@api.exception_handler(Exception)`+bare `raise exc`; §6.2:368/469/477). status는 정당(500)이라 치명 아님.

### 2.2 의미적 변종 라우팅 (일반 규칙)
- **치명 항목의 의미 레인 FAIL은 결정 레인 PASS와 무관하게 step2 치명 FAIL**이다. SD-6은 그 *한 사례*(스크립트 exit0이어도 의미 FAIL이면 치명) — 일반 규칙의 인스턴스다.
- **비-치명 항목**의 의미적 변종만 step3(WEAK 상한)으로 간다.
- → "리터럴만 피하면 녹색"(Goodhart)이 *모든 치명 항목*에서 차단된다(SD-6 한정 특례가 누수시키던 구멍 닫힘).

### 2.3 실질성 관문 (측정 — ①②는 FC 게이트가 이미 집행, ③만 독립)
degenerate/vacuous 차단. ①② 중복판정(N3) 제거 — **③(빈 골격)만 본 관문의 독립 기능**:
- ① 도메인 메서드 non-trivial / ② 테스트 non-vacuous = **FC-1·FC-2 치명 게이트(step2)가 이미 집행**(FAIL이면 픽스처는 step2.5 도달 전 이미 FAIL). 본 관문서 재판정 없음(사문화 방지).
- ③ 종류폴더·4계층 *빈 골격* = 그 폴더 내 `.py`가 **프로덕션 import 그래프에 0**(grep 추적). **귀속(N4·2026-06-08 개정 정합)**: (i) **데이터소스 BC가 §632-(2)대로 만든 빈 골격은 실질성 FAIL이 아니다**(개정으로 *의무 골격* — 비었다고 degenerate 아님); (ii) *판정 유스케이스가 있어야 할 BC*가 빈 골격이면 **step2.5 치명 FAIL**; (iii) **종류 2차 폴더 자체의 부재**(평면 `.py`로 접음·골격 미생성)는 **SH-3 치명 FAIL**(WEAK 아님 — SH-3 치명 격상). 구 "*비치명 종류폴더* 미사용→SH-3 WEAK" 문구는 폐기.

### 2.4 TIER-Q 등급 (카운트 기반 — '가중평균 금지'와 정합)
"가중치 수치"는 정의된 바 없으므로 **카운트 기반 순위**로 산출(용어 모순 해소):
- Q-1·2·3·7 + NJ-3·4·7(강) 각각 PASS/WEAK/FAIL(Q-4·Q-5·Q-6 제외 — 치명이라 §2 step2 처리).
- **품질 상** = WEAK ≤2 ∧ FAIL 0; **중** = WEAK ≤4 ∧ FAIL ≤1; **하** = 그 외. **단 '강'(NJ-3·4) 항목 FAIL 시 상한 '중'**(사문화 해소).
- *완료(§4) 판정엔 Q 등급 불산입* — Q는 치명 통과 후 "품질" 보고용.

---

## 3. 회귀 bisect 인과 규칙 (진단 전용 — 채점 라벨 비영향)
- **§3은 진단/내러티브 전용이며 §2 집계 라벨·§4 완료 판정에 직접 영향을 주지 않는다**(증거 단위 §2.5 목록에 bisect 분류 비포함). 단 예외: **변위(c) 분류가 치명 항목에 닿으면**(예: P1a operation try/except → app service catch 이동 = SD-6 "status 객체 app 흐름") 그 변위는 §1.3 의미적 변종으로 승격돼 집계에 들어간다.
- **인과 1차 증거 = 같은 태스크·같은 런타임 timeline만**. dual=런타임 효과 분리. **태스크A↔B 직접 차분 금지**.
- **3분류**: (a)패치前 이미 있던 행위=성향(패치 책임 아님) (b)패치前 없고 後 신규=사이드이펙트 후보 (c)위치만 이동=변위.
- **N=1 한계 박제**: 각 시점 N=1 → "이 timeline에서 관측됨"까지만, "패치가 야기" 단정 금지. 강한 인과는 same-task A/B(N≥3) 별도.
- 가설 H1(§9.6 8행 압력→멱등성 발명)·H2(누적게이트→속도회귀)·H3(migration lifecycle 비소유 경계 위반)·H4(게이트↑→비결정↑)는 진단 대상.

---

## 4. 결승선(완료) 정의

### 4.1 게이트 정의 (P1a·P2·P3)
완료 #4가 요구하는 "게이트 라이브 발화"의 게이트:
- **P1a** = *API 오류 응답 중앙화 규율*(discipline-reviewer + `check-error-centralization.py`): application/domain이 오류→HTTP status 변환을 직접 하면 blocker. (DR-20·22·23, ninja §2.2·§6.2)
- **P2** = *메커니즘 소유권 백스톱*(`check-mechanism-ownership.py`): 프로덕션 DB 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체하면 blocker. (architecture-db §9.5·§16.4 = Q-4 라이브판)
- **P3** = *Risky Write §9.6 규율*(discipline-reviewer 4스테이지): 동시성 민감 쓰기의 §9.6 6요소·동시성 테스트 누락 시 blocker. (architecture-db §9.6)
- *(셋 다 `commands/dddjango.md`·discipline-reviewer에 배선된 실재 게이트. 정의 정본=각 worklog + DEVLOG DR 항목 교차참조.)*

### 4.2 정적 준수 조건 (저장 fixture로 측정 가능 — '완료' 어휘는 §4.4 플러그인 축 전용)
다음 **모두**(픽스처가 정적 "준수" 라벨을 받는 조건; 플러그인 "완료"는 §4.4):
1. **척추 치명 FAIL 0건** — SD·FC·SH·Q-4·Q-5·Q-6 치명 전부 통과(의미적 변종 포함).
2. **의미적 변종 0건** — `[결정PASS∧의미FAIL]` 칸이 빔.
3. **FC** — 골든 오라클 전 케이스 통과 + mutation red율 100%.

### 4.3 라이브 완료 (별도 fresh 런 트랙 — 완료 *분리 보고*)
4. **핵심 게이트 라이브 발화** — P1a·P2·P3가 *위반 주입* 조건에서 실제 blocker 발화.
   - **위반주입 프로토콜**: 게이트별 known-violation ≥1 카탈로그(P1a=application이 status 매핑; P2=커스텀 sqlite immediate 백엔드; P3=§9.6 미충족 동시성 쓰기) → fresh `/dddjango` 런에 주입 → **발화 PASS 기준 = 3회 주입 중 3회 blocker**(준수만 보는 exit0은 차단 미stress라 불인정). 운영=조정자.
- **N_run≥5 블라인드 런** + 태스크 형태 **2종 이상**(N=1·단일태스크는 완료 자격 없음).
- 정적 채점은 "라이브 발화"의 대리로 **무효**(DR-21: 텍스트판별 통과≠라이브 발화) → 4.2(정적)와 4.3(라이브)을 **분리 보고**.
- **산출물 폴더 동작 관측 (DR-40 — 별도 트랙, 완료 비산입)**: P1a·P2·P3와 달리 백스톱이 없어 *위반 주입→blocker 발화*가 아니라 *정상 재빌드 시나리오에서 코디가 폴더 규약을 따르나*를 관측한다. **시나리오**: fresh `/dddjango`로 기능 A 빌드(신규) → 같은 A를 재빌드(또는 수정 모드)로 재호출. **관측 PASS(전부 충족)**: ① 신규 시 `.dddjango/<YYYYMMDD-HHMM>-<slug>/`에 `scope.md`·`design-spec.md` 생성(date prefix 형식) ② 재빌드 시 코디가 `ls .dddjango/` 목록을 G0에 제시·사용자 선택(ⓐ/ⓑ) ③ ⓐ 선택 시 새 폴더 미생성·기존 폴더 재사용(폴더 수 불변·생성일 prefix 유지). **별도 라벨 `폴더 동작: 관측 / 미관측 / 미검증`로 분리 보고**하고 — **§4.4 "완료" 정의(아래)에는 산입하지 않는다**(프로세스 편의 동작이라 치명 안전속성 P1a/P2/P3과 무게가 다름). 근거 = `commands/dddjango.md` 「산출물 위치」·Phase 0(DR-40).

#### 4.3.1 에러 경로 라이브 관측 매트릭스 (별도 트랙, 완료 비산입 — DR-40 폴더 관측과 동급 무게; aclex 라운드 산물)
P1a·P2·P3 게이트(*위반주입→blocker*)와 달리, **정상 산출물의 에러 경로 계약**을 *매 라이브 런마다 균일하게* probe해 회귀(예: ACL-EX2 transient→500 누수)를 ad-hoc이 아닌 **사전등록 커버리지**로 잡는다. 이 트랙의 가치는 *균일·전수성*에 있다(매번 같은 계약을 같은 방식으로 확인).
> ⚠️ **이 트랙은 탐지(관측)이지 예방이 아니다**(적대 3렌즈 합의·P1a가 4번 증명: 채점기준 명시 ≠ 라이브 차단). probe FAIL은 *코드를 고치지 않으며*, **RUBRIC 차원/치명 게이트를 신설·소급변경하지 않는다(freeze 유지)**. 별도 라벨 `에러경로 계약: 관측 / 부분 / 미검증`로 보고하고, 결과는 **2차원 라벨의 라이브 축(§4.4)** + **잔여-흠 원장**에만 입력한다. **EP probe는 치명 게이트가 아니므로 FAIL이어도 픽스처 종합 라벨(§2)을 자동 FAIL시키지 않는다.** (예방은 별 트랙 = 표준 텍스트/백스톱.)

- **2층 분리(FC-1 골든과 동형)**: ⓐ **계약 속성표(균일·코드 미열람)** — 모든 픽스처에 참인 에러 계약(내부 BC 분해 무관)을 코드 열람 전 동결. ⓑ **픽스처별 어댑터(조정자·코드 열람 후)** — 실제 두드릴 route+payload는 픽스처마다 다르므로(동일 태스크라도 BC 분해 분기) **§1.4 FC 실행 어댑터 기계를 재사용**해 조정자가 코드 열람 후 작성. "미열람" 선언은 ⓐ에만 적용.
- **probe 실행 환경(미실측 방지·DR-50 정정)**: probe는 `setup_test_environment()` 또는 `settings.ALLOWED_HOSTS` override 후 두드린다(미적용 시 `DisallowedHost` 400 위양성·실측 불가). **미실측 시 status 추론 금지** — 추론은 ninja 파싱/검증 2단계를 혼동한다(dslive-claude EP-1: 절단 JSON을 422로 추론했으나 사후 실측 400; ninja `params/models.py`는 스키마검증 전 파싱단계에서 `HttpError(400)`을 raise). pytest 통합 테스트는 testserver 자동 허용이라 깨진-본문 케이스를 1건 포함하면 라이브 대리로 충분.
- **status는 단일강제 금지·화이트리스트**(표준이 열어둔 자유도라 단일강제 시 거짓양성 — DR-44 D1 "retryable 503\|409 둘다 정당"·DR-38 신호동형 함정).

| 키 | 계약 속성 (ⓐ 균일·미열람) | status 화이트리스트 | N/A·어댑터 규칙 (ⓑ) |
|---|---|---|---|
| **EP-1 깨진 본문** | 비-JSON/절단 본문 POST → problem+json 클라이언트 오류 | **{400}** + `application/problem+json` | HTTP operation 없으면 차원 N/A |
| **EP-2 무효 입력** | 도메인/스키마 위반(수량 0·음수) → problem+json 클라이언트 오류 | **{422, 400}** | 수량 필드 없으면 픽스처의 다른 필수검증 필드로 대체 |
| **EP-3 transient 소진** | transient 인프라 경합(락 경합·CAS 재시도 소진) → **retryable, 절대 500 아님** | **{503, 409}** | **종단 유형별 어댑터**: (i) ACL이 raw transient를 경계 핸들러로 전파→경계 직접 주입(락/소진); (ii) ACL이 *도메인 예외로 번역*(raw 종단 없음·Codex 대안 B)→raw probe **N/A**, 도메인경로(소진→도메인예외→핸들러)로 *동일 계약* 검증 |
| **EP-4 재고 부족** | 재고<주문 → 충돌 | **{409}** | FC-1 골든과 중복 — 골든이 1차, 여기선 라이브 축 교차확인만 |

> **C 정책 무충돌(415 EP 항목 부재 → 무변경)**: 이 EP-1~4 매트릭스에는 **415/406 협상 항목이 없으므로** Q-1 415/406 C 정책(RUBRIC E 앵커)과 **무충돌** — EP 표는 **바꾸지 않는다**.

- **정적 대응물(거대 식별자 — 라이브서 제외)**: 외부 식별자에 거대값을 라이브로 던지는 probe는 422\|500이 **둘 다 방어 가능**(vacuous·underdetermined)이라 라이브 매트릭스에서 **뺀다**. 대신 *정적 스키마 검사*로 관측: 외부 식별자 수치 필드가 상한(`le=`/`lt=`/범위 validator)을 **선언**하나(min1/architecture-api §5.1). 라이브 발화가 아닌 **정적 관측**이며 RUBRIC min 차원 판정을 바꾸지 않는다.
- **EP-3 균일불가 해소(N/A 규칙의 핵심 사례)**: 순진안은 "raw OperationalError 종단" probe를 모든 런에 강제하려다 **균일 불가**였다(Claude=ACL raw raise 1종단·Codex=ACL 도메인번역·OperationalError 종단 없음·app 2곳 분산). EP-3은 *계약*("소진→retryable, 500 아님")만 균일 고정하고 *probe 종단*은 어댑터가 픽스처별로 고른다 → 균일 적용 가능. **maj1과 반대축**(maj1=과잉매핑[transient를 과하게 retryable]·EP-3=과소매핑[진짜 transient를 500으로]·ACL-EX2가 그 인스턴스).
- **소급 차단(freeze 정합)**: 이 매트릭스는 *신설 라이브 관측 트랙*이다. **신설 이전 산출 fixture를 EP probe FAIL로 소급 FAIL시키지 않는다**(헤더 line6 소급-FAIL-금지 + §5.4 "결과 본 뒤 기준 변경 금지"). 신설 이후 라이브 런부터 균일 적용한다.
- 근거 = `ACLEX-CLAUDE-FIX-PLAN.md` probe 매트릭스 검토(적대 3렌즈 FIX-THEN-GO)·`ACLEX-AB-HANDOFF.md` probe 표·DR-44/45(ACL 전수성 #1 미해결).
- **RUBRIC 정합(SSOT·DR-47)**: 관측 *항목*(EP-1~4 이름)은 `RUBRIC.md` **TIER-OBS**에 스텁 등재(라벨 무영향·freeze 밖)하고, *계약 속성·status 화이트리스트·N/A·어댑터*는 **여기 §4.3.1이 단일 정본**(RUBRIC은 status 미복제). 매 라이브 채점지 **표 섹션 필수화** 집행은 §6.1 #9.5.

### 4.4 최종 라벨 격자 (모순 라벨 차단)
한 픽스처 = **2차원 라벨**: `(정적: 준수 / WEAK / FAIL) × (라이브: 발화 / 미발화 / 미검증)`.
- **"준수"**(픽스처·정적, §2 산출) ≠ **"완료"**(플러그인·정적+라이브). 어휘 분리로 동일 산출물에 모순 라벨 불가.
- **"완료"(플러그인 축)** = 전 픽스처 정적 준수 ∧ 핵심 게이트 라이브 발화 ∧ N_run≥5·태스크 2종. 하나라도 미달 = **"보류"**.
- **현 fixture(N=1·단일태스크 timeline)로는 4.3 충족 불가 → 최대 "정적 준수"까지 보고, "완료" 선언 금지**(정직).

### 4.5 비용 정직 인지
full 정본(N_grader≥3 전수)은 대략 *치명·비치명 ~33항목 × 8벌 × N≥3 ≈ 1,500+ grader 판정*이다(큼). 결정 레인(grep)은 거의 무비용, **인적 비용은 의미 레인**에 집중. 비용 절감 변형(치명만 N≥3 등)은 **부록**으로만 두고 기본은 full.

> **완료 한계 명시**: 이 완료는 "규칙 준수+기능 정확"까지다 — baseline 인과·미시 유지보수성·보안(누출 제외)·명세 내적 품질은 *별도/후속*(과대주장 금지).

---

## 5. 과적합 방지 (사전등록·홀드아웃·관찰집합 동결)

### 5.1 관찰집합 열거 동결 + 누수 차단
- **"8벌"을 *실경로*로 열거 박제**(수사적 "8" 금지; 실측 교정): 채점 모집단 = `~/Desktop/`의 `dddjango-final-codexB`·`dddjango-final-claudeA`·`dddjango-smoke2-codexB`·`dddjango-smoke2-claudeA`·`dddjango-p1a-livefire-codex`·`dddjango-p1a-livefire-claude`·`dddjango-p1a-v3-codex`·`dddjango-p1a-v3-claude`. ⚠️ livefire·p1a-v3는 `-codex/-claude` 접미사(A/B 없음), final·smoke2만 `-codexB/-claudeA` — 규약 혼재이나 *실재 디렉터리명*이 정본.
- **criteria/갭 도출에 *영향을 준* 모든 fixture(8벌 밖 smoke3/4 포함)는 홀드아웃에서 영구 제외** — 순환 방지 울타리의 구멍(8벌 밖을 보고 조정) 차단. STANDARD-GAP-LEDGER가 smoke3/4로 승격한 갭은 "관찰집합 내 재확인" 전까지 speculative. **따라서 smoke3/4를 채점하면 그것은 *방법 리허설*일 뿐 — 라벨은 8벌 평가에 비반영**(criteria-영향 fixture라 홀드아웃 자격 없음).

### 5.2 criteria 내용 vs 가중·치명배정 분리 (순환 정직화)
- **criteria *내용*은 표준 §근거에 선재**(검증됨: SD-3=ddd `final.md:630`, SD-6=ninja `:112`, Q-3=db `:406`, §9.6 8행=db `:391-408`) → "표준서 독립 도출"은 내용 층위 참.
- **그러나 criteria의 *가중·치명배정*(FC tier 신설·SD-6/Q-4 치명화)은 8벌 관찰의 산물일 수 있다** — 이를 정직 표기. 치명화 동기가 *표준 동기*인지 *fixture 동기*인지 각 항목 §근거에 명시.

### 5.3 앵커 = 예시 (임계값 아님)·재좌표화
- 앵커는 *규칙 충족/위반의 구체 예시*일 뿐(바=표준 조항). **홀드아웃 격리 불요**.
- **앵커 출처는 *현존 fixture 직접경로*로 재좌표**(예: `~/Desktop/dddjango-p1a-v3-codex/.../api_orders.py:41-49`) — *삭제된 채점기록(EVAL-*.md) 인용 금지*(2차 자료 의존·검증불가 차단, C-F1). grader 배포본엔 익명 스니펫만(§1.2).

### 5.4 사전등록·홀드아웃
- **사전등록**: 차원·판정기준·FC 골든표·mutation 목록을 채점 *전* 동결(§0 게이트). 결과 본 뒤 기준 변경 금지.
- **새 태스크 홀드아웃(형태 다양)**: 8벌 전부 '생성+재고차감'이라 형태 편향. 완료 전 *형태축이 다른* 태스크 ≥2종(쓰기-생성 / 조회-무거운 read model / 다중 애그리거트 트랜잭션)으로 sanity. 형태별 *어느 차원 N/A*인지 사전 매핑.

---

## 6. 채점 결과지 표준 형식 (산출 템플릿 — 형식 동결)

> 모든 신규 채점 결과지(`results/<YYYYMMDD-HHMM>-<라운드>-<런타임>.md`)는 아래 골격·순서·칼럼을 그대로 유지한다. **형식 표류 차단**: 기존 결과지가 두 형식(`smoke4`=per-tier 표 / `p1a-v3`=치명군 grouping)으로 갈려 있던 것을 단일 템플릿으로 동결한다. *기존 파일 소급 개편은 별건*(요청 시).

### 6.1 섹션 순서 (RUBRIC 레터링 그대로 — 어기면 형식 위반)
1. **헤더 블록**(§6.2)
2. **종합 판정 (사전식 집계)**(§6.3) — verdict-first
3. **A. TIER-S 척추 — S-DDD**(SD-1~7)
4. **B. TIER-S 척추 — S-HR**(SH-1~10)
5. **TIER-S(조건부) — S-NINJA**(NJ-1~6; HTTP operation 없으면 차원 전체 N/A 명시)
6. **TIER-S(핵심) — FC**(FC-1~3)
7. **C. 기존규약 마스크 (적용 메모)** — §1.1.M의 baseline existing/new/unavailable 분류와 근거를 명시한다. *순수 greenfield면 "N/A — 신규 앱뿐, §0 표준 적용" 한 줄이라도 섹션 유지*한다.
8. **D. TIER-Q 품질**(Q-1~7)
9. **의미적 변종 / backstop-blind 메타** — §1.3 *측정의 주 산출물*이므로 조정자 노트보다 **앞**
9.5. **에러 경로 라이브 관측 (§4.3.1)** — *라이브 런 한정*(의미변종 메타 뒤·조정자 노트 앞 배치·RUBRIC TIER-OBS 대응). EP-1~4 관측 표(칼럼: 키·관측 status·content-type·화이트리스트·판정 — maj1live 템플릿). **§4.3.1이 채점지에 처음 적용된 maj1live(2026-06-07) 이후** 라이브 채점지에 **표 섹션 필수**(§6.3 한 줄 라벨 병기로 갈음 불가). **소급 미적용**: 그 이전 산출 채점지(nj2live·fklive·rcqlive·aclex·aclexab·c4live 등)는 면제(§4.3.1 소급금지 정합). 정적 채점(라이브 미수행) 결과지는 차원 N/A.
10. **조정자 노트**
11. **부록**(선택) — 런 고유 맥락(PoC 가설·C트랙 재현 등)은 여기로 격리, 본 채점 골격 침범 금지

> 차원 표(3~8)는 `RUBRIC`의 **A→B→NINJA→FC→C→D** 레터링을 그대로 따른다. *C 누락 = 레터링 끊김 = 형식 위반*. E(앵커)는 루브릭 전용(결과지 미포함).

### 6.2 헤더 블록 (인용블록 `>`, 필수 필드)
방법(v4) · 채점일 · 픽스처(절대경로+기존규약 상태) · 런타임·N · 태스크 요지 · 게이트(BC/렌즈/스택/G1·G2/thinking 고정값) · **범례**(✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류 · ➖ N/A) · **필수 ⚠️ 단서**(해당 시): 리허설(관찰집합 밖=라벨 비구속) · `N_grader`(<3이면 명시) · FC 전수 미실행 · **자기보고 불신**(코디네이터 보고 대신 조정자 직접 검증) · schema 영향과 외부 배포 준비 상태.
- **fixture 도구 환경**(필수 필드 — 2026-06-09 신설·**라이브/재채점분 한정·기존 산출분 면제**, §4.3.1 소급금지 패턴 정합): 채점 *착수 전* venv 도구 스냅샷(`pip freeze`/site-packages 테스트도구 목록) + `requirements.txt`·`pyproject.toml` 테스트도구 핀 유무를 박제(§1.1.T `env`). **조정자가 채점 위해 추가한 도구는 `(조정자 추가)` 태그**로 표기해 코디 산출물(`produced`)과 분리. 이 필드 부재로 신설 *이전* 채점지를 형식 위반/재작성 대상으로 삼지 않는다.

### 6.3 종합 판정 표 (사전식 — §2 의사코드 그대로)
`| 단계 | 결과 |`: ① 마스크 C → ② 치명 게이트(FAIL n건) → ②.5 실질성 관문 → ③ 비치명·의미변종(WEAK 상한) → ④ TIER-Q 등급. 뒤에 **한 줄 요지** + **2차원 라벨**(§4.4: (정적: 준수/WEAK/FAIL)×(라이브: 발화/미발화/미검증); "완료"는 §4.4 충족 시만). **라이브 런 채점 시** 라이브 축 줄에 `폴더 동작`·`에러경로 계약`(§4.3.1: 관측/부분/미검증) 관측 라벨을 병기한다(둘 다 완료 비산입·치명 게이트 아님) — `에러경로 계약`의 **상세 EP-1~4 표는 별도 섹션(§6.1 #9.5)**에 둔다(한 줄 병기와 별개·maj1live 이후 라이브 런 필수).

### 6.4 차원 표 칼럼 스키마 (TIER-S 공통)
`| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |`
- **Result** = **줄 인용 필수**(`file:line`) — 인용 없는 PASS 무효(§1.2). **자기보고 아닌 조정자 직접 검증**.
- 결정/의미 = 레인별(➖=해당 레인 없음), 종합 = 두 레인 종합 글리프, 치명 = 게이트 여부(✅통과/❌/⏸️).
- **전 차원 전수 채점**(결정 PASS여도 의미 생략 금지 §1.3).
- D.TIER-Q는 '치명' 칼럼 생략(Q-4·Q-5·Q-6를 인라인 **[🔴치명]**으로 표시).

### 6.5 형식 금지 (표류 방지)
- ❌ per-tier 차원 표를 "타 런 델타" 또는 "치명/비치명 2군"으로 **대체** 금지(보조 표는 가능, per-tier 표 제거 불가).
- ❌ 채점 *과정 서사*(v1→v2 수정 이력 등) 본문 박제 금지 — 최종 판정만. 방법 판단(severity 보정 근거 등)은 조정자 노트의 *결론*으로.
- ❌ 마스크 C 섹션 생략·종합 한 줄 대체 금지.
- ❌ 런 고유 연구물로 채점 골격 대체 금지(부록 격리).

---

## v4 변경 요약 (2026-07-13)
- **migration lifecycle 비소유**: migration 파일·명령·전용 테스트·운영 절차를 제품 범위 밖으로 두고, G0↔G2 opaque fingerprint 불변과 보고 정직성만 Q-5 치명 게이트로 확인한다.
- **brownfield grandfather**: baseline 기존 persistence app은 touched 여부와 무관하게 물리 위치·identity·migration tree를 보존하고, 새 domain/application 코드가 adapter/repository로 감싼다.
- **현재 계약 테스트**: 승인된 현재 의무를 오라클로 삼아 spec 변경과 같은 변경에서 테스트를 retain/update/delete/add하며, history-only 영구 테스트를 금지한다. 현재 호환·보안·규제 의무와 임시 characterization은 별도로 판정한다.
- **Q-6 집행 보완**: 현재 의무 inventory·retain/update/add 실제 실행·고정 7시나리오 oracle을 추가하고 Q-6을 치명 게이트로 닫았다. v4 이전 결과에는 소급하지 않는다.
- **러너 중립성**: 프로젝트가 선언한 테스트 명령·설정을 존중하며 특정 러너나 `--no-migrations`를 강제하지 않는다.
- **소급 금지**: v3 이하 fixture·채점 결과는 당시 기준의 역사적 기록으로 보존한다.

## v3 변경 요약 (역사적 기록)
- **§0 동결 게이트 + 동결-전-결정 9개 확정**(미동결 채점 = §5 자기위반 차단; C-F5).
- **판정 레인 집행**: 항목별 결정-판정 표(A-F3)·마스크 C 이진질문(A-F4)·조정자/grader 역할 분리(A-F7)·FC-1 등록 주체·시점(A-F6).
- **집계 폐합**: 치명 항목 의미변종 일반 라우팅(A-F5·B-F4)·Q-4 치명 승격(B-F3)·NJ 조건부/강 편입(B-F2)·Q 카운트 기반(B-F7)·실질성 측정화(B-F6)·N_grader/N_run 분리(B-F8).
- **완료 폐합**: P1a/P2/P3 정의(B-F9)·라이브 위반주입 프로토콜·2차원 라벨 격자(B-F10)·정적/라이브 분리·bisect 비영향 명시(B-F11).
- **과적합 인프라**: 관찰집합 열거 동결+누수차단(C-F2)·criteria 내용/가중 분리(C-F3)·앵커 재좌표+마스킹 해소(C-F1·F4)·표제 인과함의 제거(C-F8).
- **산출 형식 동결(§6 신설, 2026-06-02)**: 채점 결과지 표준 템플릿(섹션 순서 A→B→NINJA→FC→C→D·칼럼 스키마·필수 단서·형식 금지)으로 기존 결과지 형식 혼재(per-tier vs 치명군) 단일화. `poc-codex-3b` 형식 정합 작업 산물.

(평가 항목 = `RUBRIC.md`)
