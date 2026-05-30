# 최종 스모크 — 남은 문제 추적 (2026-05-30 기준)

> 출처: 최종 수동 스모크(Claude 태스크A 재고예약 · Codex 인터랙티브 태스크B 주문생성, clean fixture).
> 인사이트 HTML: `FINAL-SMOKE-INSIGHTS.html` · 메모리: `dddjango-final-smoke-findings`.
> **정직 경계**: 각 N=1 + 태스크 상이 → 런타임차/태스크차 분리 불가. 이 목록은 "표준 보강 대상"이지 "Claude>Codex 입증"이 아님.

## 상태 요약

| ID | 문제 | 런타임 | 상태 | 다음 액션 |
|----|------|--------|------|-----------|
| P1b | 의존성 버전 stale(④f) | Codex | ✅ **구현 완료** (커밋됨·동적검증 대기) | 라이브 검증 |
| P1a | ninja problem+json 처리(operation 품질) | Codex 위반/Claude 준수 | ✅ **구현 완료** (2026-05-30, 커밋) | 동적검증·집행 백스톱(Stage 4) 잔여 |
| P2 | 코더 메커니즘-소유권(프로덕션 커스텀 백엔드) 미차단 | Claude | ✅ **구현 완료** (2026-05-30, 4커밋·origin 푸시·검증) | 동적검증(라이브 ④ 발화)·머지/PR 결정 |
| P3 | §9.6 Risky Write 준수 집행(동시성 테스트 실현) | Codex | ✅ **구현 완료** (2026-05-30, 4스테이지·동적검증) | 라이브 런 동적검증·머지 |
| P4 | ③ 판정-소유 이주 비결정 | 양 런타임 | ⚪ 데이터 부족 | N≥5 블라인드 정량화 후 판단 |

---

## ✅ P1b — 의존성 버전 stale (구현 완료)
- **증상**: Codex가 `django-ninja==1.4.5`(PyPI 최신 1.6.2)를 *기억 속 옛 버전*으로 핀. 핀=설치 일치 → 무핀 resolve 안 함.
- **보강(2026-05-30)**: `discipline-houserules` **§6.2 신설**(⚠️ ninja §6.2와 이름만 같고 다른 규칙) = "새 런타임 의존성=무핀 resolve→실제 설치값 핀, '최신'은 기존 프레임워크 핀과 호환되는 최신, 안정 릴리스만, 막힌환경 보고" + `ninja §2.1`→§6.2 교차참조 + `coder.md`(+codex 미러) 집행 불릿. 7파일·byte-identical·`claude plugin validate` ✔.
- **남은 것**: **동적검증**(다음 의존성-추가 런에서 무핀 resolve→핀+호환한계 처리 — 캐시 신선화 선행, LLM 행동이라 결정 보장 아닌 완화책). 커밋 완료(eval/codex-determinism-n2).

---

## ✅ P1a — ninja problem+json operation 품질 (구현 완료 2026-05-30)
- **분석 결론(전제 정정)**: 핵심 증상(operation 본문 수제 응답)은 **공백이 아니라 일탈** — `implementation-django-ninja §6.2`가 이미 3곳에서 금지하고 Claude는 준수했다. (b) OpenAPI 몽키패치는 (a)의 하류 보상 해킹. 근본 원인은 §6.2가 "problem+json 미디어타입 필수"와 "schema 매핑 우회 금지"를 동시 요구하는데 **ninja에선 에러에 대해 둘이 양립 불가**(실증). + 집행 갭(어떤 에이전트도 ninja §6.2 준수를 구현 후 독립 검증 안 함 — discipline-reviewer는 클린코드만·acceptance-tester는 content-type 미검증)도 확인.
- **해법(사용자 선택 = prohibition→positive 레시피)**: 금지를 완성된 긍정 레시피로 흡수 + 양립불가 긴장을 표준이 명시 해소. **실증검증**(ninja 1.6.2 probe ×3: per-status 미디어타입 부재·중앙핸들러=problem+json런타임/json-OpenAPI·tuple deprecated·`create_response` 일괄변환) + **서브에이전트 3리뷰**(ninja기술/정합성/작문) 반영.
- **구현(6파일, byte-identical 유지)**: §2.2 raise+`Status`(deprecated 튜플 예제 제거) / §6.2 전면 재작성 = 중앙 `@api.exception_handler`+단일 헬퍼가 **처방된 기본(A)** + `create_response` 오버라이드 **DRY 대안(B)** + 프레임워크 기본 5종(401/403/404/422/429) + **OpenAPI application/json은 수용된 한계** 명시(금지는 `get_openapi_schema` 사후변형만 — NinjaAPI 상속 자체는 허용; 1차 "상속 금지"안을 리뷰가 정정) + 1.6.x 핀 / §6.1·§8 정합 / SKILL ×2 / FINAL-SMOKE-PLAN 축4 채점기준. `claude plugin validate ./dddjango` ✔.
- **파일명 누수(c) `orders_ninja_api`**: 이번 범위 밖 — §4/houserules 별도 축, N≥2 재발 시 승격(미반영).
- **잔여**: 동적검증(다음 라이브 API 런에서 coder가 raise+중앙변환 하는지) · 집행 백스톱(Stage 4)은 레시피가 실패모델 뿌리를 쳐서 N≥5까지 보류.

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
- **잔여**: 동적검증(라이브 런에서 coordinator가 ④ 호출·반송하는지) · ④ 저-recall(7회피 형태는 확률적 ②③ 의존) · 머지/PR 결정.

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
- **잔여**: 라이브 파이프라인 런 동적검증(실제 Codex CLI 미실행 — codex 미러 본문 byte-동일로 갈음) · N=1 태스크-레벨(우열결론 아님) · 머지/PR.

## ⚪ P4 — ③ 판정-소유 이주 비결정 (데이터 부족)
- **증상**: Claude=catalog 완전 이주+Product 애그리거트 승격 / Codex=catalog 평면+published_service 함수(트랜잭션 스크립트). 정반대 착지지만 **둘 다 DR-16 허용 범위**(스코프 escape). 편차 큼(풀 DDD↔함수).
- **판단 보류**: 의도된 여지 vs 조여야 할 비결정 → **같은 태스크 N≥5 블라인드**로 빈도 정량화 후 결정. 지금 표준 손대는 건 시기상조.

---

## 방법론·운영 이연 (별도 트랙)
- **N≥5 블라인드 측정**: codex vs claude 우열 결론 + ③ 비결정 정량화(P4)의 전제. 같은 태스크·블라인드·루브릭 필요.
- **크로스-메모리 갱신**(P 분석 시): `dddjango-standard-hardening-verification`(가드레일 항목=P2) · `dddjango-stdgap-3-4`(축9 결판·P4) — 각 문제 분석할 때 그 메모리에 반영.
- **P1b 동적검증**: ~/.claude·~/.codex 캐시 신선화 후 의존성-추가 라이브 런.
- **릴리스 결정**: eval 브랜치 `eval/codex-determinism-n2`(DR-14~17 + P1b·P1a·P2·**P3**)의 main 머지/PR(v1.0.1?). 동적검증(P1a·P1b·P2는 라이브 런, P3는 저장 산출물로 완료) 선행 권장.
