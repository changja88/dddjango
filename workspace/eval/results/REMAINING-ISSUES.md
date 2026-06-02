# 최종 스모크 — 남은 문제 추적 (2026-05-31 기준)

> 출처: 최종 수동 스모크(Claude 태스크A 재고예약 · Codex 인터랙티브 태스크B 주문생성, clean fixture).
> 인사이트 HTML: `FINAL-SMOKE-INSIGHTS.html` · 메모리: `dddjango-final-smoke-findings`.
> **정직 경계**: 각 N=1 + 태스크 상이 → 런타임차/태스크차 분리 불가. 이 목록은 "표준 보강 대상"이지 "Claude>Codex 입증"이 아님.

## 상태 요약

| ID | 문제 | 런타임 | 상태 | 다음 액션 |
|----|------|--------|------|-----------|
| P1b | 의존성 버전 stale(④f) | Codex | ✅ **라이브 해결** (2026-05-30 smoke2: 양 런타임 `1.6.2` 신선 핀) | N≥5는 별도 |
| P1a | ninja problem+json 처리(operation 품질) | Codex 위반/Claude 준수 | 🟡 **재정정(DR-24·C트랙)** — v3 백스톱 결정적 OK(exit2/exit0)이나 **C 트랙 심층감사서 Codex P1a 의미적 변종 발견**(멱등성 크립→`status:int` snapshot이 app 흐름+중앙핸들러 죽은코드, 백스톱이 원리상 못 봄). Claude 준수. | **릴리스 보류 재개**(아래 C 트랙) |
| P2 | 코더 메커니즘-소유권(프로덕션 커스텀 백엔드) 미차단 | Claude | ✅ **라이브 해결** (2026-05-30: 양 런타임 순수 version CAS·백스톱 exit0 발화) | 머지/PR |
| P3 | §9.6 Risky Write 준수 집행(동시성 테스트 실현) | Codex | ✅ **라이브 해결** (2026-05-30: Codex에서 discipline-reviewer catch 라이브 발화·교정) | 머지/PR |
| P4 | ③ 판정-소유 이주 비결정 | 양 런타임 | ⚪ 데이터 부족 | N≥5 블라인드 정량화 후 판단 |
| **NJ-4** | 오류 status를 `openapi_extra`로만 선언(response= 누락) | Codex(poc-codex) | 🔧 **정적 집행(2026-06-02)** — 백스톱 `check-openapi-error-declaration.py` 신설·poc-codex exit2·거짓양성0 검증 | 라이브 발화 N≥1 |
| **SD-7** | ACL *밖*(presentation·application)이 catalog 도메인 예외 직접 import = 번역 ACL 미격리 | Claude(p1a-v3) | 🔧 **정적 집행(2026-06-02)** — 백스톱 `check-context-isolation.py`(ACL 면제) + 루브릭 미스캘리브 교정(바·§E 앵커·`check-structure.py`) | 라이브 발화 N≥1 |

---

## 🧪 라이브 재테스트 결과 (2026-05-30, smoke2 fixtures)

방식: `FINAL-SMOKE-PLAN.md` rev3 + `RETEST-HANDOFF.md`. 캐시 신선화(양 캐시 byte-identical) 후, clean fixture 2개(`~/Desktop/dddjango-smoke2-claudeA`·`-codexB`, Django 5.2.14·py3.12·ninja 미설치·PROMPT 제거)에서 사용자가 실제 `/dddjango` 라이브 런. **태스크A 재고예약=Claude, 태스크B 주문생성=Codex 인터랙티브.** 게이트 전부 미강제(설계자 결정)·무수정 승인.

**결과 요약** (각 fixture 산출물·코드·테스트를 13축으로 직접 채점, 테스트 독립 재실행 green):

| P | Claude/A | Codex/B | 판정 |
|---|---|---|---|
| **P1b** 신선 핀 | `django-ninja==1.6.2` | `1.6.2` (원래 stale 1.4.5 → 교정) | ✅ 양쪽 해결 |
| **P2** 메커니즘 소유권 | 순수 version CAS·커스텀 백엔드 0·백스톱 exit0 | 동일·exit0 | ✅ 양쪽 해결(준수 확인; 위반 미주입이라 *차단*은 미stress) |
| **P3** §9.6+동시성 실현 | §9.6 8행 블록 + CAS-스파이 4테스트 green | §9.6 8행 + catalog CAS-충돌 mock 2테스트; **1차 감사서 "Risky Write 테스트 부족" blocker→coder 교정** | ✅ 양쪽 해결(**Codex에서 catch 라이브 발화 — 최강 증거**) |
| **P1a** problem+json | operation `raise`·중앙 `@api.exception_handler` 5개·수제 0 | ❌ operation `create_order→JsonResponse` 직접·중앙 핸들러 **0**·수제 `_problem()` | 🟡 **갈림** (Claude 준수 / Codex 재발) |

**핵심 교훈**: *긍정 레시피 + 집행 게이트(P2 백스톱·P3 discipline-reviewer blocker)*가 있는 항목은 라이브에서 막아냄. **P1a는 긍정 레시피만 깔고 집행 백스톱(Stage 4)을 N≥5까지 보류했는데 — Codex 재발을 못 막음**(라이브 반례). 단 Codex 태스크의 멱등성·content-negotiation 복잡도가 raw-request로 기운 교락 있음.

**P4 ③ 데이터 1점**: 둘 다 새 BC(inventory/orders) 신설했으나 *판정의 집*이 갈림 — Claude=리치 도메인 애그리거트(`Product.reserve()`) / Codex=`catalog/published_service/stock.py` 함수(트랜잭션 스크립트). 둘 다 평면 ORM 모델엔 판정 0(안티패턴 회피). N≥5 정량화 대상.

**정직 경계**: N=1·태스크 상이 → "Claude>Codex" 결론 아님. "이번 라이브 런에서 집행이 작동/실패했다"까지.

---

## ✅ P1b — 의존성 버전 stale (구현 완료)
- **증상**: Codex가 `django-ninja==1.4.5`(PyPI 최신 1.6.2)를 *기억 속 옛 버전*으로 핀. 핀=설치 일치 → 무핀 resolve 안 함.
- **보강(2026-05-30)**: `discipline-houserules` **§6.2 신설**(⚠️ ninja §6.2와 이름만 같고 다른 규칙) = "새 런타임 의존성=무핀 resolve→실제 설치값 핀, '최신'은 기존 프레임워크 핀과 호환되는 최신, 안정 릴리스만, 막힌환경 보고" + `ninja §2.1`→§6.2 교차참조 + `coder.md`(+codex 미러) 집행 불릿. 7파일·byte-identical·`claude plugin validate` ✔.
- **✅ 라이브 검증 완료 (2026-05-30 smoke2)**: 양 런타임 모두 `django-ninja==1.6.2` 신선 핀. **원래 Codex가 stale `1.4.5` 핀하던 게 이번 Codex 런에서 1.6.2로 교정** — §6.2 의존성 규칙이 라이브에서 작동. (N≥5 빈도는 별도.) 커밋 완료(eval/codex-determinism-n2).

---

## 🟢 P1a — ninja problem+json operation 품질 (긍정 레시피 · v2 reviewer · **v3 결정적 백스톱 2026-05-31 해결 → 라이브 배선 발화만**)
- **분석 결론(전제 정정)**: 핵심 증상(operation 본문 수제 응답)은 **공백이 아니라 일탈** — `implementation-django-ninja §6.2`가 이미 3곳에서 금지하고 Claude는 준수했다. (b) OpenAPI 몽키패치는 (a)의 하류 보상 해킹. 근본 원인은 §6.2가 "problem+json 미디어타입 필수"와 "schema 매핑 우회 금지"를 동시 요구하는데 **ninja에선 에러에 대해 둘이 양립 불가**(실증). + 집행 갭(어떤 에이전트도 ninja §6.2 준수를 구현 후 독립 검증 안 함 — discipline-reviewer는 클린코드만·acceptance-tester는 content-type 미검증)도 확인.
- **해법(사용자 선택 = prohibition→positive 레시피)**: 금지를 완성된 긍정 레시피로 흡수 + 양립불가 긴장을 표준이 명시 해소. **실증검증**(ninja 1.6.2 probe ×3: per-status 미디어타입 부재·중앙핸들러=problem+json런타임/json-OpenAPI·tuple deprecated·`create_response` 일괄변환) + **서브에이전트 3리뷰**(ninja기술/정합성/작문) 반영.
- **구현(6파일, byte-identical 유지)**: §2.2 raise+`Status`(deprecated 튜플 예제 제거) / §6.2 전면 재작성 = 중앙 `@api.exception_handler`+단일 헬퍼가 **처방된 기본(A)** + `create_response` 오버라이드 **DRY 대안(B)** + 프레임워크 기본 5종(401/403/404/422/429) + **OpenAPI application/json은 수용된 한계** 명시(금지는 `get_openapi_schema` 사후변형만 — NinjaAPI 상속 자체는 허용; 1차 "상속 금지"안을 리뷰가 정정) + 1.6.x 핀 / §6.1·§8 정합 / SKILL ×2 / FINAL-SMOKE-PLAN 축4 채점기준. `claude plugin validate ./dddjango` ✔.
- **파일명 누수(c) `orders_ninja_api`**: 이번 범위 밖 — §4/houserules 별도 축, N≥2 재발 시 승격(미반영).
- **🟡 라이브 재발 (2026-05-30 smoke2/Codex)**: 긍정 레시피만으론 못 막음. Codex가 `create_order`를 raw `HttpRequest→JsonResponse`로 구현하고 도메인 예외를 operation try/except로 수제 변환, **`@api.exception_handler` 0개**(`api_orders.py:108,150-201`). OpenAPI 몽키패치는 사라짐(정식 `openapi_extra` 사용)이라 **(b) 하류 해킹은 교정·(a) 핵심 안티패턴(중앙 핸들러 미사용·operation 수제 반환)은 잔존**. Claude/A는 중앙 핸들러 5개로 준수. **→ 보류했던 집행 백스톱(Stage 4: discipline-reviewer가 ninja operation 본문 수제 JsonResponse·중앙핸들러 부재 검사, 또는 acceptance-tester content-type 검증)에 라이브 반례.** 단 Codex 태스크의 멱등성·content-negotiation 복잡도가 raw-request로 기운 교락 큼(N=1).
- **✅ 집행 백스톱 구현 (2026-05-31, Stage 4)**: 긍정 레시피만으론 라이브 재발을 못 막아(위), P3와 동형으로 **독립 catch 게이트**를 추가. `discipline-reviewer`에 "**API 오류 응답 중앙화 규율(책임 배치·DRY)**" 점검 항목 신설(+§경계 한 절) — 명세가 채택한 스택이 Ninja면 operation 본문이 예외를 try/except로 잡아 status를 고르거나 수제 `JsonResponse`/`HttpResponse`로 오류 응답을 만들면 **blocker**(중앙 `@api.exception_handler`/`create_response`가 예외→status 매핑 소유). **적대 리뷰 3렌즈**(표준정합·거짓양성·거짓음성+경계)가 핵심 결함 1개로 수렴 → 판정 본질을 "operation이 `JsonResponse`를 직접 만드나"에서 "**예외→status 매핑이 operation 밖 단일 소유자로 모였나**"로 재정의(Codex식 `_problem()` 헬퍼-위임 거짓음성 + 같은-모듈 헬퍼 거짓양성을 *동시* 차단) + 거짓양성 carve-out (a)중앙변환점 하나라도 충족·(b)성공응답/튜플 무관·(c)같은파일 헬퍼 정상. 2미러(plugin `dddjango/agents/discipline-reviewer.md` + codex `…/dddjango-discipline-reviewer/SKILL.md`) byte-identical.
- **검증**: 정적 `claude plugin validate` ✔ · 미러 byte-동일(bullet·§경계) ✔ · **동적 N=9 텍스트-판별 9/9 정확** — known-bad(Codex/B `api_orders.py`) 3/3 **BLOCKER**(3명 모두 "헬퍼 위임이지만 예외→status 매핑이 operation try/except에 남음" 정확 포착)·known-good(Claude/A) 3/3 **PASS**(carve-out a/c)·음성트리거(합성 같은모듈 Ninja 2/2 PASS·plain Django 1/1 적용안함). **레인 검증**: discipline-reviewer 책임배치·DRY 규율(P2 메커니즘-소유권과 동형)이지 ninja 관용구 정확성 판정 아님(Reviewer 3 "진짜 동형, fig leaf 아님" 확인). **잔여**: 캐시 신선화 후 라이브-파이어(P3가 받은 라이브 발화에 상당하는 확인사살)는 D 트랙.
- **🔴 라이브-파이어 결과 (2026-05-31, NEW-1 — 백스톱 약점 발견)**: 캐시 신선화 후 dual-runtime 실제 `/dddjango`(같은 주문생성 태스크). **Codex가 textbook 위반**(operation 본문 수제 `JsonResponse`[`api_orders.py:44,49-59,108-117`] + 오류→status 매핑이 application service[`create_order_app.py:92-166`] + 중앙 핸들러 ValidationError 1개뿐)인데, **discipline-reviewer가 백스톱 텍스트를 로드하고도** "API 오류 응답/Problem Details 생성이 application layer에 섞여 책임 배치 약함"을 **blocker가 아닌 *권고*로 강등** → G2 통과. **Claude는 준수**(operation raise·중앙 핸들러 4종)라 거짓양성0. **진단: 백스톱 정밀도 OK·재현율 약함.** 같은 런에서 **P3 백스톱은 blocker 발화** → catch 메커니즘은 작동, P1a *문구*가 약함. 원인 가설: 위반이 "단일 매퍼(app service)+헬퍼" 모양 → "약함(권고)"으로 읽힘 + carve-out (a) "중앙 변환점 하나라도 충족"(ValidationError 핸들러)이 약화. **N=9 텍스트-판별(고립 체크 적용)은 통과했으나 라이브 홀리스틱 reviewer는 강등 — 텍스트-판별 ≠ 라이브 발화.** 정본=`workspace/eval/LIVEFIRE-RESULTS.md` NEW-1. **→ 릴리스 보류, 문구 강화 필요**(operation/app/domain 어디든 오류→status 생성=확실 blocker, carve-out (a) 조이기, 새 게이트 없이 기존 discipline-reviewer 문구 강화). 강화 후 재-라이브파이어.
- **🔴 강화 v2 + 사전 시뮬 결과 (2026-05-31, DR-22 — 문구 강화 불충분 확인)**: NEW-1 방향대로 백스톱 문구를 강화(carve-out (a) ∃→∀+부분 핸들러 blocker 명시·레드플래그를 operation·application·domain 확장·단일 판별 게이트·"operation 본문 밖"→"operation·application 계층 밖" 5곳 치환; 2미러 byte-identical·`validate` PASS·구현 전 적대 리뷰 3렌즈로 carve-out (d)·옵션 기각). **사전 시뮬(N=3, 강화 reviewer를 저장 Codex 산출물에 적용·캐시 md5 확인): P1a blocker 0/3.** sim-1·2 점검 누락(다른 발견에 주의 쏠림), sim-3 옛 ∃ 논리로 통과(∀ 강화 미적용) — 세 리뷰어 모두 app service의 오류→status 매핑을 읽고도 P1a로 연결 못 함. **bullet 문구 강화만으론 부족 — 적대 리뷰 렌즈3 예언 실증(silent downgrade/누락은 주의 배분·산출 형식 문제), Claude 리뷰어조차 미적용**. → **v3는 구조적 개입**: (가) 명시 판정 강제 (나) 생산자(design-architect) 예방 (다) 결정적 백스톱 (라) 산출 형식 보강. 직감 (가)+(나), 구현 전 적대 리뷰로 우선순위. 정본=`workspace/DEVLOG.md` DR-22·`LIVEFIRE-RESULTS.md`.
- **✅ v3 — 결정적 백스톱 + 생산자 예방 (2026-05-31, DR-23 — actionable 해결)**: 사용자 두 제약(반드시 적용+동작 시간 안 늘림)의 교집합으로 (다)+(나) 선택(결정적 백스톱=coordinator Bash 1회, LLM 라운드 0이라 시간 ~0이면서 결정적). (다) `check-error-centralization.py` 2미러[`/application_layer/` 파일이 HTTP status/응답 직접 생성 시 exit2; AND: 경로·응답신호(`JsonResponse(`/`HttpResponse(`/`status[_code]=[45]\d\d`/`HttpError([45]\d\d`/`from ninja` import)·diff-only; P2 골격(SKIP_DIRS·`_is_new_or_modified`·exit 0/2/1) 차용·`/test/` 제외] + (나) design-architect 명세 2미러[오류→status 변환=presentation 단일 소유, application/domain은 HTTP 안 만듦 §6.2] + coordinator 배선 2미러[G2 직전 백스톱 2종·하나라도 exit2→합쳐 반송·②통과(0)≠reviewer 면제]. **구현 전 적대 리뷰 3렌즈**(거짓양성=하[Claude 준수본 0건 실증]·HttpError/ninja-import 추가·§6.2 스킬명 명시·단락정책·carve-out (d)·옵션 기각). **검증(결정적): `validate`✔·미러 md5·위반본 exit2(`create_order_app.py` 정확 지목)·준수본 exit0·거짓양성 가드(성공status·읽기·import-only→exit0/`JsonResponse status=404`→exit2)·시간0.21s. v2 LLM 사전시뮬 0/3 → v3 스크립트 100% 결정적**(같은 코드→같은 결과). 스크립트는 application_layer HTTP 누수만 고정밀(operation 수제·status맵추출·변수우회는 (나)예방+강화 v2 reviewer 위임 — 적대 리뷰 균형). 라이브 배선 발화 확인은 **아래 ✅ 라이브 검증 참조**(coordinator가 G2서 실제 호출; 스크립트 동작은 결정적 증명 완료, P2보다 강함). 정본=`workspace/DEVLOG.md` DR-23·`LIVEFIRE-RESULTS.md` v3 절.
- **✅ 라이브 검증 (B 트랙, 2026-05-31)**: dual `/dddjango`(`dddjango-p1a-v3-{codex,claude}`, smoke2 태스크 B, 캐시 신선화). **dual 백스톱 exit0** — application_layer HTTP 텍스트 누수0·중앙 `@api.exception_handler`(Codex 12/Claude 7)·operation raise만(*텍스트 수준*). 확인=① coordinator(양 런타임)가 G2서 백스톱 2종 호출=**배선 작동** ② exit0=**거짓양성0**(Claude 준수) ③ **(나) 예방 작동**(이전 Codex 위반[핸들러 1개+app status]→v3 dual). 미관측=exit2→반송(dual exit0이라). **🔴 단 "dual 완전 준수"는 과한 해석 — C 트랙(아래)이 정정**. P4 ③ 재현(Codex `published_service` 함수/Claude `Product.deduct_stock()` 리치 이주).
- **🔴 C 트랙 심층 감사 (2026-05-31, DR-24 — B 트랙 "완전 준수" 정정)**: 사용자 피드백("P1a 여전히 Codex / catalog 선택 의심 / 전수 검토")으로 두 v3 산출물을 **5 병렬 서브에이전트**로 전수 감사(DDD·API·DB·메커니즘·규율+테스트 실행). **핵심: B 트랙 exit0은 백스톱의 *좁은 텍스트 계약* 통과일 뿐 구조적 준수가 아님.** Codex는 옛 P1a(operation 수제 status 선택)는 피했으나 **더 미묘한 변종**: 멱등성 스코프 크립이 부른 `IdempotencySnapshot(status:int)`가 application 흐름(`idempotency_store.py:17-22`)·app이 비즈니스 예외 직접 catch→status-snapshot 변환(`create_order_app.py:70-79`)→중앙 `@api.exception_handler` 비즈니스 핸들러 3개 **죽은 코드**·operation은 raw `JsonResponse`(`api_orders.py:69`). ninja §2.2·§6.2 "오류 raise·성공 return·중앙 단일 변환" 구조 깨짐(Major; 매핑 지식은 presentation이라 Critical 아님). **백스톱 exit0은 자기 계약상 정확**(`status:int`=plain dataclass→텍스트 신호 0) — v3 3중망의 **의미적 커버리지 갭**. → **P1a 릴리스 보류 재개.** 전체 인벤토리는 **§ C 트랙 인벤토리**(맨 아래).

## ✅ P2 — 코더 메커니즘-소유권 집행 (구현 완료 2026-05-30)
- **증상**: Claude 코더가 `config/db_backends/sqlite3_immediate`(`DatabaseWrapper` 상속·BEGIN IMMEDIATE)를 `settings.py` **프로덕션 DATABASES ENGINE에 배선**(테스트 race 관찰성용). `§16.4` 가드레일이 스모크 3일 전부터 그 안티패턴을 금지했는데 코더가 **알고도 위반**.
- **재특성화(적대검증으로 방향 2번 뒤집힘)**: 본질은 "settings 관리법 부재"가 아니라 **"명시 금지를 코더가 무시 + 그걸 잡는 집행 부재"**. ① 첫 가설(implementation-django §3.3 settings 긍정 가이드)을 3렌즈 적대검증이 기각 — §3.3 "설정 분리"가 *이미 존재*·금지가 *이미 무시*됨(텍스트→준수 실패)·코드 보는 유일 게이트 discipline-reviewer가 "Django 기술 정확성"을 *명시 제외*(45줄, 집행 구멍). ② 결정적 grep도 신기루(좁으면 7회피 중 2개만, 넓으면 eval 9/10 정당런 오탐 — 해악이 *의미적*). + 픽스처가 **오프타깃 Django 4.2.30**(타깃 5.2)이라 stock `transaction_mode` 부재가 발생조건.
- **구현(4 합성 수 — Ultraplan 원격 실행, 4커밋 `af306a4..58660a0`·origin 푸시·로컬 ff)**:
  - **① 픽스처 5.2** — baseline `4.2.30→5.2.14`(stock `transaction_mode` 경로 부여, 발생조건 제거).
  - **② 표준 출처-불문 정합** — `architecture-db §9.5` "stock OPTIONS만, ENGINE 교체 아님" 경계절 + `implementation-django §16.4`·`coder.md` **출처-불문**(상속·런타임몽키패치·`connection_created`·`init_command`·`isolation_level`·미들웨어·테스트패치 *어떤 형태든* 동일 위반) + 안전-PRAGMA 화이트리스트(`foreign_keys`/`busy_timeout`/`synchronous`/`cache_size`; WAL·isolation_level은 밖=설계승인).
  - **③ discipline-reviewer 의미체크** — "메커니즘-소유권 규율" blocker 항목 + 경계에 "소유권이지 정확성 아님" 명시(흘림 모호함 해소). diff-only·test격리·명세승인 예외.
  - **④ 좁은 결정적 백스톱** — `scripts/check-mechanism-ownership.py`(AND-합성: diff-only ∧ 레포-로컬 ∧ 프로덕션배선 ∧ 트랜잭션/락 의미변경 ∧ stock/gis 제외) + coordinator G2 Bash 배선(exit2→설계반송). 고정밀·저-recall(7회피는 ②③ 위임).
- **검증(로컬)**: 미러 plugin==codex byte-identical(양 skill+스크립트 md5 일치)·source 본문드리프트 0·`claude plugin validate` ✔ · **④ 스크립트 합성 실증 5/5**(claude-3형 차단 / stock+transaction_mode·third-party·test전용·정당 서브클래스 통과).
- **대조**: Codex/B는 `select_for_update`+CAS+CHECK로 백엔드 없이 깨끗(단 동시성 테스트 없어 안 부딪힘 — confound = P3).
- **✅ 라이브 검증 (2026-05-30 smoke2)**: 양 런타임 순수 version CAS·커스텀 백엔드 0·`check-mechanism-ownership.py` exit0 **실제 실행**(coordinator G2 배선 확인). **원래 Claude가 커스텀 BEGIN IMMEDIATE 백엔드를 프로덕션 배선하던 게, 5.2.14+보강표준에서 순수 CAS로 깨끗 착지.** 단 위반을 주입 안 해서 *차단 행위*는 미stress(준수만 확인). ④ 저-recall·머지/PR 잔여.

## ✅ P3 — §9.6 Risky Write 블록 준수 집행 (구현 완료 2026-05-30)
- **재특성화(사용자 reframe, 적대검증)**: 본질은 "동시성 테스트 누락"이 아니라 **"우리 규칙(§9.6 Risky Write Consistency Block) 준수 집행"**. 두 산출물 감사로 **P2·P3 = 한 집행 공백의 양면** 확정 — 같은 Risky Write(재고)에서 **Claude/A는 §9.6·테스트는 지켰으나 §16.4 위반(=P2)**, **Codex/B는 §16.4는 지켰으나 §9.6·테스트 위반(=P3)**. 둘 다 전 게이트 통과.
- **근본(3중 집행 구멍 + 1 표준 공백)**: §9.6은 8행 블록을 "명시한다"(필수)지만 — (a) `design-architect`가 §9.6을 *개념*으로만 참조(8행 표 미언급) → Codex가 인용만 하고 블록 누락, (b) G1 `design-review-db`가 블록 완전성 미점검, (c) 선언된 동시성 기준이 실제 테스트로 실현됐는지 G2에서 미점검 → Codex가 가드만·oversell 테스트 0으로 통과. + 표준에 **§16.4-호환 *결정적* 동시성-테스트 레시피 부재**(Claude/A가 그래서 커스텀 백엔드=P2를 만듦 — §9.6 준수가 §16.4 위반을 *강요*).
- **구현(4스테이지 prevent→catch 체인, 적대 리뷰 4회로 블로커 3·중요 다수 교정):**
  - **① 안전장치** `implementation-test §20.5` **결정적 CAS-충돌 스파이** 레시피(stale-`version` 1회 주입→재시도 수렴, 실 스레드·커스텀 백엔드 없이 — Claude/A `ConflictOnceRepository` 실증) + `architecture-db §9.6` 포인터. §9.6↔§16.4 인과 차단. **스킬 3-미러**(plugin/codex/source).
  - **② prevent@G1** `design-architect`: Risky Write면 §9.6 8행 블록을 *표로* 산출(번호 인용 금지).
  - **③ catch@G1** `design-review-db`: §9.6 블록 *존재·8행 다뤄짐* 점검(데이터-렌즈; 의미 분류+under-framed 직접 재분류+비-Risky 탈출구; 테스트 *적정성*은 제외).
  - **④ catch@G2** `discipline-reviewer`: 선언된 동시성 기준(명세 어디서든)이 실제 테스트로 *실현*됐는지(TDD 커버리지; CAS-스파이/ThreadPool/동등 테스트). 가드만·미실현=**blocker**.
- **미러**: 스킬(§20.5·§9.6)=3사본 byte-identical, 에이전트(architect·review-db·discipline-reviewer)=plugin+codex 2사본 본문 동일. `claude plugin validate` ✔.
- **동적검증(저장 산출물·Sonnet 보수 하한·N≥2~3)**: **G1(③)** precision 5/5(claudeA 3/3·neg-읽기 2/2 PASS)·**under-framing recall 2/2 BLOCKER**(라벨·인용 없는 명세도 재분류해 잡음). **G2(④)** **codexB recall 3/3 BLOCKER**(가드만·oversell 0 — *실제 발생 닫힘*)·claudeA precision 2/2 PASS. → **P3 양면(설계-선언 G1 + 테스트-실현 G2) 닫힘.**
- **✅ 라이브 검증 (2026-05-30 smoke2)**: 양 런타임 §9.6 8행 블록 + 동시성 테스트 실현(Claude=CAS-스파이 4테스트, Codex=catalog CAS-충돌 mock 2테스트, 독립 재실행 green). **결정적: Codex 1차 규율 감사에서 discipline-reviewer가 "Risky Write 테스트 부족"을 blocker로 라이브 발화→coder 보강** — *원래 P3를 위반했던 Codex에서 catch 층이 실제로 작동*(P3 양면 닫힘의 라이브 증거). N=1 태스크-레벨(우열결론 아님)·머지/PR 잔여.

## ⚪ P4 — ③ 판정-소유 이주 비결정 (데이터 부족)
- **증상**: Claude=catalog 완전 이주+Product 애그리거트 승격 / Codex=catalog 평면+published_service 함수(트랜잭션 스크립트). 정반대 착지지만 **둘 다 DR-16 허용 범위**(스코프 escape). 편차 큼(풀 DDD↔함수).
- **판단 보류**: 의도된 여지 vs 조여야 할 비결정 → **같은 태스크 N≥5 블라인드**로 빈도 정량화 후 결정. 지금 표준 손대는 건 시기상조.
- **DR-24 보강**: P4 ③의 더 날카로운 진단 = 단순 "다른 선택"이 아니라 **G1 에스컬레이션 비결정**. Codex는 고-blast catalog 트레이드오프를 §9 Open Questions 사후기록만(G1 미상정), Claude는 §5.4로 G1에 올려 사용자 승인. 표준 텍스트(houserules §1.1+§1.2·ddd §3.2:632)는 *이관*(Claude) 쪽으로 기움.

---

## 🔴 C 트랙 인벤토리 — dual v3 산출물 전수 감사 (2026-05-31, DR-24)

> 트리거: 사용자 "P1a 여전히 Codex / catalog 처리 다름·Codex 잘못 의심 / 우리 플러그인이 정한 대로 안 한 모든 것 면밀 검토". 5 병렬 서브에이전트(DDD·API/P1a·DB/§9.6·메커니즘·규율/TDD+테스트). 산출물=`~/Desktop/dddjango-p1a-v3-{codex,claude}`. **N=1·태스크 1회** — 표준 위반 여부는 텍스트로 성립하나 "런타임 성향" 일반화 보류. 미수정·미커밋.
> **테스트 실증**: 둘 다 그린바(Codex 27/27·Claude 62/62)·`manage.py check` 클린·결정적 CAS 스파이 보유(실스레드 의존 탈피=P3 핵심 충족, 커스텀 백엔드 0).

### Codex 일탈
| # | 심각도 | 문제 | 증거 | 표준 |
|---|---|---|---|---|
| C1 | ~~Critical~~ → **스킵** | 명세 §7.369 약속한 `test_stock_concurrency.py` 부재 + 재시도 소진→`StockConflict`(409) 미테스트 → **⚠️ DR-32 재검증=과대평가**: (a)파일명 차이 무해(`test_stock_published_service.py`가 CAS-retry[line34]·oversell[line54] 커버, P3='닫힌 목록 아님'이라 충족) (b)소진→409 엣지만 미테스트=Minor·명세 Test criteria(§274)도 미선언 | 명세 §7.369 vs 트리 / `create_order_app.py:103` | §9.6 Test criteria |
| C2 | **Major** | **P1a 의미적 변종** — status-bearing snapshot이 app 흐름 + 중앙 핸들러 죽은 코드(백스톱 미포착) | `create_order_app.py:70-79`·`idempotency_store.py:17-22`·`api_orders.py:69` | ninja §2.2·§6.2 |
| C3 | **Major** | 멱등성 스코프 크립 — `Idempotency-Key` **필수(400)**·전용 테이블·replay, task/scope 미지시·G0=확장금지 위반(**P1a 뿌리**) | scope.md(무언급)·명세 §4·§5 | 설계원칙 05/스코프 |
| C4 | **Major** | SQL 판정 복제 `stock__gte=quantity`(design-architect.md:36이 동일 예시로 금지; 단 `can_decrement_stock` 살아있어 빈혈 해악 부분적) | `published_service/stock.py:42` | ddd §3.2 → **✅ C형 집행 DR-32**(백스톱 ⑪ `check-anemic-sql-guard`: 도메인 메서드 부재 빈혈만; B형 atomic 관용구=나-3 보류) |
| C5 | **Major** | 고-blast catalog 트레이드오프 **G1 미상정**(§9 Open Questions 사후기록만) | 명세 §9.404 | design-architect.md:38/51 |
| C6 | **Major** → **reviewer 명확화** | ACL 협력 포트가 `application_layer/`(표준=`domain_layer/order/port/`) → **⚠️ DR-33: 진짜 §2 위반이나 N=1**(p1a-v3만, 다른 5 픽스처 준수) → 백스톱 과함, reviewer 파일트리 항목 명확화(`1.0.8`) | `application_layer/create_order/port/` | houserules §2·§3 |
| C7 | **Major** | 죽은 예외 핸들러 5/12(비즈니스+Invalid* 도메인 예외) | `orders_api_router.py:87-124` | cleancode 죽은코드 |
| C8 | Minor | 레이아웃 비일관(orders=표준/catalog=평면) — C5 증상 | settings INSTALLED_APPS | houserules §1.4 |
| C9 | Minor | 평면 catalog startapp stub 잔존(`views.py`/`tests.py`) + `tests.py`↔`test/` 이원화 | `catalog/views.py·tests.py` | houserules §1.3 |

### Claude 일탈
| # | 심각도 | 문제 | 증거 | 표준 |
|---|---|---|---|---|
| L1 | **Major** | 기존 `0001_initial` **재작성**(이력 불변 위반·자기명세 §3.5:181 위반; db_table=catalog_product 일치로 실DB 호환·데이터유실 없음) | `django_catalog/migrations/0001_initial.py:14-25` | db §11 |
| L2 | **Major** | 컨텍스트 경계 누수 — ACL이 catalog **구체 infra**(`DjangoProductRepository`) 직접 import + catalog **OHS 부재** | `product_stock_acl.py:17` | houserules §2·ddd §3.2:632 |
| L3 | Minor | 합산 정규화 불변식+UniqueConstraint 과설계(멀티라인 자체는 방어가능·합산이 task 미요구) | 명세 §1.2·§2.3 / `order.py` | 설계원칙 05 |
| L4 | Minor | `OrderLine.__eq__` product_id만 비교(quantity 무시) | `order_line.py:20-23` | ddd §3.1 |
| — | **Clean** | P1a 완전 준수(operation 성공만 return·중앙 핸들러 단일·HTTP 누수0·백스톱 exit0 거짓양성0) / §9.6 8행 / 메커니즘 / CAS 3계층 테스트 | — | — |

### catalog 직답 (사용자 Q2)
Codex 미이관 *결정 자체*는 방어가능/underdetermined(표준 텍스트는 오히려 *이관* 쪽으로 기움). 진짜 잘못 = **C4(SQL 판정 복제) + C5(G1 미상정)**이지 "평면 유지" 그 자체 아님. Claude 이관은 표준 정합(§3.2:632 직접 지지)이나 집행 디테일(L1·L2) 흠.

### 메타 (플러그인 갭)
1. **P1a 새 변종 백스톱 미포착**(의미적 갭) — v3 3중망 보강 필요(C2). 2. **스코프 규율 갭**(양쪽 반대방향 과설계, G0 확장금지 무력 — C3·L3). 3. **G1 에스컬레이션 비결정**(P4 ③ 날카로운 진단 — C5). 4. **§9.6 Test criteria 집행 갭**(Codex 약속파일 누락·미테스트를 reviewer 미포착 — C1, P3 영역 재발). C2·C3는 coder 아닌 **design-spec(architect) 단계** 유입.

### 다음 액션 (우선순위)
1. **C2/C3** (Codex P1a 변종 + 멱등성 크립) — v3 방어망 의미적 갭, 보강 설계 필요. 2. **C1** (§9.6 테스트 누락) — P3 영역 재발. 3. C4~C9·L1~L4 백로그. (커밋·릴리스는 사용자 명시 승인 전 보류.)

---

## 방법론·운영 이연 (별도 트랙)
- **N≥5 블라인드 측정**: codex vs claude 우열 결론 + ③ 비결정 정량화(P4)의 전제. 같은 태스크·블라인드·루브릭 필요.
- **크로스-메모리 갱신**(P 분석 시): `dddjango-standard-hardening-verification`(가드레일 항목=P2) · `dddjango-stdgap-3-4`(축9 결판·P4) — 각 문제 분석할 때 그 메모리에 반영.
- **P1b 동적검증**: ~/.claude·~/.codex 캐시 신선화 후 의존성-추가 라이브 런.
- **릴리스 결정**: eval 브랜치 `eval/codex-determinism-n2`(DR-14~17 + P1b·P1a·P2·**P3**·**P1a 백스톱**)의 main 머지/PR. **라이브 재테스트(2026-05-30 smoke2): P1b·P2·P3 집행 확정 · P1a Codex 재발 → 집행 백스톱(2026-05-31, N=9/9) 구현.** **그러나 P1a 백스톱 라이브-파이어(2026-05-31, `dddjango-p1a-livefire-{codex,claude}`)에서 재현율 약함 확인(Codex 위반→권고 강등) → 릴리스 보류, 백스톱 문구 강화 후 재검증. 강화 v2+사전시뮬(DR-22)도 0/3. v3 결정적 백스톱(DR-23)으로 P1a actionable 해결. ✅ 라이브 검증(B, 2026-05-31): dual `/dddjango` 백스톱 exit0·배선 작동·거짓양성0·(나) 예방 작동. **🔴 그러나 C 트랙 심층 감사(DR-24)가 'dual 완전 준수'를 정정 — Codex에 백스톱 못 보는 P1a 의미적 변종(C2, 멱등성 크립 C3) 잔존 → P1a 릴리스 보류 *재개*.** P1b·P2·P3는 라이브 견고(릴리스 가능 수준; P1a만 보류). ⚠️ eval 브랜치는 **로컬 전용**(origin에 없음); main 대비 **ff 가능**(직계 후손). 머지/PR 시 P3 246ccfc·P1a 백스톱 990efb9 포함 전체가 origin에 푸시됨.
