# 최종 스모크 — 남은 문제 추적 (2026-05-31 기준)

> 출처: 최종 수동 스모크(Claude 태스크A 재고예약 · Codex 인터랙티브 태스크B 주문생성, clean fixture).
> 인사이트 HTML: `FINAL-SMOKE-INSIGHTS.html` · 메모리: `dddjango-final-smoke-findings`.
> **정직 경계**: 각 N=1 + 태스크 상이 → 런타임차/태스크차 분리 불가. 이 목록은 "표준 보강 대상"이지 "Claude>Codex 입증"이 아님.

## 상태 요약

| ID | 문제 | 런타임 | 상태 | 다음 액션 |
|----|------|--------|------|-----------|
| P1b | 의존성 버전 stale(④f) | Codex | ✅ **라이브 해결** (2026-05-30 smoke2: 양 런타임 `1.6.2` 신선 핀) | N≥5는 별도 |
| P1a | ninja problem+json 처리(operation 품질) | Codex 위반/Claude 준수 | ✅ **집행 백스톱 구현** (2026-05-31: discipline-reviewer "API 오류 응답 중앙화 규율" blocker; 적대 리뷰 3렌즈 + 텍스트-판별 N=9/9) | 라이브-파이어(D)·머지 |
| P2 | 코더 메커니즘-소유권(프로덕션 커스텀 백엔드) 미차단 | Claude | ✅ **라이브 해결** (2026-05-30: 양 런타임 순수 version CAS·백스톱 exit0 발화) | 머지/PR |
| P3 | §9.6 Risky Write 준수 집행(동시성 테스트 실현) | Codex | ✅ **라이브 해결** (2026-05-30: Codex에서 discipline-reviewer catch 라이브 발화·교정) | 머지/PR |
| P4 | ③ 판정-소유 이주 비결정 | 양 런타임 | ⚪ 데이터 부족 | N≥5 블라인드 정량화 후 판단 |

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

## ✅ P1a — ninja problem+json operation 품질 (긍정 레시피 2026-05-30 · **집행 백스톱 2026-05-31**)
- **분석 결론(전제 정정)**: 핵심 증상(operation 본문 수제 응답)은 **공백이 아니라 일탈** — `implementation-django-ninja §6.2`가 이미 3곳에서 금지하고 Claude는 준수했다. (b) OpenAPI 몽키패치는 (a)의 하류 보상 해킹. 근본 원인은 §6.2가 "problem+json 미디어타입 필수"와 "schema 매핑 우회 금지"를 동시 요구하는데 **ninja에선 에러에 대해 둘이 양립 불가**(실증). + 집행 갭(어떤 에이전트도 ninja §6.2 준수를 구현 후 독립 검증 안 함 — discipline-reviewer는 클린코드만·acceptance-tester는 content-type 미검증)도 확인.
- **해법(사용자 선택 = prohibition→positive 레시피)**: 금지를 완성된 긍정 레시피로 흡수 + 양립불가 긴장을 표준이 명시 해소. **실증검증**(ninja 1.6.2 probe ×3: per-status 미디어타입 부재·중앙핸들러=problem+json런타임/json-OpenAPI·tuple deprecated·`create_response` 일괄변환) + **서브에이전트 3리뷰**(ninja기술/정합성/작문) 반영.
- **구현(6파일, byte-identical 유지)**: §2.2 raise+`Status`(deprecated 튜플 예제 제거) / §6.2 전면 재작성 = 중앙 `@api.exception_handler`+단일 헬퍼가 **처방된 기본(A)** + `create_response` 오버라이드 **DRY 대안(B)** + 프레임워크 기본 5종(401/403/404/422/429) + **OpenAPI application/json은 수용된 한계** 명시(금지는 `get_openapi_schema` 사후변형만 — NinjaAPI 상속 자체는 허용; 1차 "상속 금지"안을 리뷰가 정정) + 1.6.x 핀 / §6.1·§8 정합 / SKILL ×2 / FINAL-SMOKE-PLAN 축4 채점기준. `claude plugin validate ./dddjango` ✔.
- **파일명 누수(c) `orders_ninja_api`**: 이번 범위 밖 — §4/houserules 별도 축, N≥2 재발 시 승격(미반영).
- **🟡 라이브 재발 (2026-05-30 smoke2/Codex)**: 긍정 레시피만으론 못 막음. Codex가 `create_order`를 raw `HttpRequest→JsonResponse`로 구현하고 도메인 예외를 operation try/except로 수제 변환, **`@api.exception_handler` 0개**(`api_orders.py:108,150-201`). OpenAPI 몽키패치는 사라짐(정식 `openapi_extra` 사용)이라 **(b) 하류 해킹은 교정·(a) 핵심 안티패턴(중앙 핸들러 미사용·operation 수제 반환)은 잔존**. Claude/A는 중앙 핸들러 5개로 준수. **→ 보류했던 집행 백스톱(Stage 4: discipline-reviewer가 ninja operation 본문 수제 JsonResponse·중앙핸들러 부재 검사, 또는 acceptance-tester content-type 검증)에 라이브 반례.** 단 Codex 태스크의 멱등성·content-negotiation 복잡도가 raw-request로 기운 교락 큼(N=1).
- **✅ 집행 백스톱 구현 (2026-05-31, Stage 4)**: 긍정 레시피만으론 라이브 재발을 못 막아(위), P3와 동형으로 **독립 catch 게이트**를 추가. `discipline-reviewer`에 "**API 오류 응답 중앙화 규율(책임 배치·DRY)**" 점검 항목 신설(+§경계 한 절) — 명세가 채택한 스택이 Ninja면 operation 본문이 예외를 try/except로 잡아 status를 고르거나 수제 `JsonResponse`/`HttpResponse`로 오류 응답을 만들면 **blocker**(중앙 `@api.exception_handler`/`create_response`가 예외→status 매핑 소유). **적대 리뷰 3렌즈**(표준정합·거짓양성·거짓음성+경계)가 핵심 결함 1개로 수렴 → 판정 본질을 "operation이 `JsonResponse`를 직접 만드나"에서 "**예외→status 매핑이 operation 밖 단일 소유자로 모였나**"로 재정의(Codex식 `_problem()` 헬퍼-위임 거짓음성 + 같은-모듈 헬퍼 거짓양성을 *동시* 차단) + 거짓양성 carve-out (a)중앙변환점 하나라도 충족·(b)성공응답/튜플 무관·(c)같은파일 헬퍼 정상. 2미러(plugin `dddjango/agents/discipline-reviewer.md` + codex `…/dddjango-discipline-reviewer/SKILL.md`) byte-identical.
- **검증**: 정적 `claude plugin validate` ✔ · 미러 byte-동일(bullet·§경계) ✔ · **동적 N=9 텍스트-판별 9/9 정확** — known-bad(Codex/B `api_orders.py`) 3/3 **BLOCKER**(3명 모두 "헬퍼 위임이지만 예외→status 매핑이 operation try/except에 남음" 정확 포착)·known-good(Claude/A) 3/3 **PASS**(carve-out a/c)·음성트리거(합성 같은모듈 Ninja 2/2 PASS·plain Django 1/1 적용안함). **레인 검증**: discipline-reviewer 책임배치·DRY 규율(P2 메커니즘-소유권과 동형)이지 ninja 관용구 정확성 판정 아님(Reviewer 3 "진짜 동형, fig leaf 아님" 확인). **잔여**: 캐시 신선화 후 라이브-파이어(P3가 받은 라이브 발화에 상당하는 확인사살)는 D 트랙.

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

---

## 방법론·운영 이연 (별도 트랙)
- **N≥5 블라인드 측정**: codex vs claude 우열 결론 + ③ 비결정 정량화(P4)의 전제. 같은 태스크·블라인드·루브릭 필요.
- **크로스-메모리 갱신**(P 분석 시): `dddjango-standard-hardening-verification`(가드레일 항목=P2) · `dddjango-stdgap-3-4`(축9 결판·P4) — 각 문제 분석할 때 그 메모리에 반영.
- **P1b 동적검증**: ~/.claude·~/.codex 캐시 신선화 후 의존성-추가 라이브 런.
- **릴리스 결정**: eval 브랜치 `eval/codex-determinism-n2`(DR-14~17 + P1b·P1a·P2·**P3**·**P1a 백스톱**)의 main 머지/PR. **라이브 재테스트(2026-05-30 smoke2): P1b·P2·P3 집행 확정 · P1a Codex 재발 → 집행 백스톱(2026-05-31, N=9/9) 구현·머지 전 포함 확정.** ⚠️ eval 브랜치는 **로컬 전용**(origin에 없음); main 대비 **ff 가능**(직계 후손). 머지/PR 시 P3 246ccfc 포함 전체가 origin에 푸시됨.
