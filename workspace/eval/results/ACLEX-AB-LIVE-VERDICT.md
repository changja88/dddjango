# aclex 테마 A+B 처방 — 라이브 검증 결과 (Claude 완벽화)

> **무엇**: aclex 스코어카드 7결함(maj1~maj4·min1·min2·min3)을 **STANDARD에 처방(커밋 `062a64f`)**하고, 그 처방이 *실제 `/dddjango` 라이브 파이프라인*에서 실현되는지 dual(Claude·Codex) 런으로 검증한 결과.
> **목표**: **Claude(우리 플러그인)를 완벽하게** — 처방이 라이브서 실현/미실현/부분인지 가려, 잔여 흠을 다음 처방으로 잇는다.
> **날짜**: 2026-06-07 · **N=1**(런타임별 1회·우열 단정 아님·P4③ run-variance) · **채점 정본**: `20260607-0412-aclexab-claude.md`·`20260607-0341-aclexab-codex.md`
> **라이브 환경**: 캐시 `062a64f` 신선화(diff IDENTICAL)·픽스처 정석 clone(`dddjango-aclexab-{claude,codex}`)·greenfield(ninja/pytest 미설치·order 테이블 0).

---

## 1. 수정하려 한 문제 + 처방 (커밋 `062a64f`)

직전 라이브 채점지(`20260606-1448-aclex-claude.md`)에서 적출한 7결함을 STANDARD(플러그인) 편집으로 처방했다. 처방 정본 = `ACLEX-CLAUDE-FIX-PLAN.md`.

| # | 수정하려 한 문제 | 처방(062a64f가 STANDARD에 한 수정) | 처방 형태 |
|---|---|---|---|
| **maj1** | ACL이 도메인 예외 3개만 잡음 → raw `OperationalError`/`IntegrityError`가 경계 누수 → **HTTP 500** | presentation **단일 변환점**에 transient `OperationalError`→503·`IntegrityError`/미식별→500 + **Exception catch-all** + `_is_retryable_db_error` 판정 레시피 (`implementation-django-ninja` §6.2) | 텍스트 레시피 + 예방(design-architect)·reviewer |
| **maj2** | 깨진 JSON 본문 → ninja `HttpError(400)` → `application/json`(problem+json 아님) | `@api.exception_handler(HttpError)` → `problem()` 매핑 | 텍스트 레시피 |
| **maj3** | `..._do_not_oversell`이 순차 루프(stale-version·스레드 경합 0)로 위장·항진 단언 | discipline-reviewer **행사 위장 경계**(이름이 약속한 동시성을 순차로 '검증'=vacuous→important) | reviewer 프로즈 |
| **maj4** | `test_stock_constraint`가 named CHECK 아닌 `PositiveIntegerField` 암묵 CHECK 검증(오귀속) | discipline-reviewer **The Liar 변종**(술어 동치 암묵 가드→오귀속·strictly stronger일 때만 구별) | reviewer 프로즈 |
| **min1** | 거대 `product_id` → `OverflowError` → **500** | `architecture-api` §5.1 외부 식별자·수치 입력 **상한**(하한만 X) | 텍스트 |
| **min2** | `InvalidOrderQuantity` 핸들러 부재(schema `ge=1` 뒤 latent) | `implementation-django-ninja` §6.2 베이스 매핑에서 **빠뜨리지 않음** | 텍스트 |
| min3 | write-conflict e2e 미검증 | **무처방**(이미 end-to-end 존재) | — |

---

## 2. 수정이 되었는지 — 라이브 검증 결과

> **읽는 법**: ✅ 실현(처방대로) · 🟡 부분(실현되나 갭) · ❌ 미실현(처방 무시·회귀) · ➖ 해당 없음. **Claude가 완벽화 대상**, Codex는 대조군.

| # | **Claude 결과** | 근거(채점지) | Codex 대조 | 처방 판정 |
|---|---|---|---|---|
| **maj1** | **🟡 부분** | Exception catch-all ✅·OperationalError 핸들러 ✅ — **단 `OperationalError` 전부 503**(transient 판정 부재, `problem_response.py:156`) | **✅** `is_retryable_database_error` 정밀(sqlstate)·**단 catch-all 부재**(비-DB 500 text/plain) | **양쪽 상보적 갭** — 완전 실현 0 |
| **maj2** | **✅** | probe 깨진본문 → 400 `application/problem+json` | **✅** 동일 | **✅ 완전 실현** |
| **maj3** | **✅** | 결정적 CAS 스파이·stale-version 주입(`test_django_product_repository:50`) — vacuous 아님 | 🟡 모킹 CAS miss·실제 경합 테스트 부재 | **✅ Claude 실현** |
| **maj4** | **🟡** | named `CheckConstraint(stock>=0)` 검증·**sqlite라 우연히 구별**(Postgres면 동치 오귀속 잠재) | ➖ named stock constraint 없음 | **🟡 환경 의존** |
| **min1** | **❌ 비대칭** | `quantity` 상한 `le=MAX_QUANTITY` ✅ / **`product_id` 상한 없음**(`schema_in.py:11`) → probe 거대 id **500** | ❌ product_id 상한 없음·거대 id 500 | **❌ 양쪽 미실현** |
| **min2** | **✅** | `InvalidQuantity` 핸들러(`problem_response.py:125` 422) | ⚠️ `InvalidOrderQuantity` 핸들러 없음(latent) | **✅ Claude 실현** |

### 요약
- **완전 실현**(Claude·처방대로): **maj2 · maj3 · min2** (3/6)
- **부분/잔여 갭**: **maj1**(transient 판정 부재) · **min1**(product_id 상한 누락) · **maj4**(환경 의존)
- **Claude 종합 채점**: **정적 준수**(치명 FAIL 0) — catalog 4계층 이주·pytest 44 passed·version CAS만으로 Codex(정적 FAIL: SH-1·4 평면)보다 깨끗.

---

## 3. Claude 완벽화 — 잔여 과제 (다음 처방 후보)

> DR-24식 심층 감사가 자기보고("44 passed·blocker 0") *너머*에서 적출. 이게 "Claude를 완벽하게"의 실제 작업 목록.

| ID | 잔여 흠 | 근본 | 처방 접근(가설) | 우선 |
|---|---|---|---|---|
| **H1** | **maj1 transient 판정 부재** — `handle_operational_error`가 `OperationalError` 전부 503(design-spec:136 "transient 변종만"과 불일치). 영구 장애 retryable 오분류 | 062a64f 레시피에 `_is_retryable_db_error`가 **있는데 Claude coder가 미준수·단순화**(Codex는 준수) = **집행/salience** 문제(텍스트만으론 비결정 — DR-22류) | 레시피 salience↑ / discipline-reviewer "Operational 무판정 503=transient 누락" 렌즈 / 결정적 백스톱(무판정 503 매핑 탐지) | **높음** |
| **H2** | **min1 상한 비대칭** — `quantity` 상한 두면서 `product_id` 상한 누락 → 거대 id 500 | `architecture-api` §5.1 "외부 식별자·수치 입력 상한"이 *수량*엔 먹혔으나 *식별자*엔 적용 안 됨 = **적용 범위** 문제 | §5.1 salience("식별자도 포함") / reviewer 입력-경계 렌즈 | **높음** |
| H3 | **graphify 스코프 외 오염** — `CLAUDE.md`·`graphify-out/`·`.claude/` 생성(태스크 무관 graphify 스킬 실행) | dddjango 파이프라인 밖(graphify 별도 스킬)·라이브 위생 | dddjango 표준 밖 — 환경/스킬 격리 사안(별건) | 낮음(별건) |
| H4 | **maj4 환경 의존 구별** — named constraint가 sqlite라서 우연히 PositiveIntegerField와 구별(Postgres면 오귀속) | 테스트가 DB 엔진 특성에 의존 | maj4 reviewer 렌즈에 "엔진-독립 구별 단언"(예: 명시 raw SQL bypass) 보강 | 중 |

### 핵심 통찰 (H1)
H1은 **처방 텍스트가 있는데 라이브서 미준수**된 사례다 — DR-22(문구-only 0/3)·DR-21(reviewer 권고 강등) 계열의 *집행력 부재*. maj1 레시피(`_is_retryable_db_error`)가 final.md에 있으나 Claude coder가 "OperationalError=전부 503"으로 단순화해도 막는 장치가 없다. **Codex는 같은 표준에서 준수**했으므로 텍스트 자체는 충분 — 갭은 **결정성/집행**(salience·reviewer·백스톱)이다. (H2는 반대로 *텍스트 적용 범위*가 product_id를 안 짚은 내용 갭.)

---

## 4. 결론

- **처방 6건 중 3건(maj2·maj3·min2) 완전 실현**, 2건(maj1·min1) 부분/미실현, 1건(maj4) 환경 의존.
- **Claude는 정적 준수**(Codex보다 우수) — 테마 A+B 처방의 골격(catalog 이주·중앙 problem 변환·version CAS·결정적 동시성 스파이)은 라이브서 작동.
- **완벽화 잔여 = H1(maj1 transient 판정)·H2(min1 product_id 상한)** — 다음 처방 라운드 대상. H1=집행 문제, H2=적용 범위 문제로 접근이 다르다.
- **정직 경계**: N=1·단일 태스크. H1·H2는 *이 timeline에서 관측*이지 "항상 그렇다"가 아니다(P4③). 처방 후 재라이브로 확인 필요.
