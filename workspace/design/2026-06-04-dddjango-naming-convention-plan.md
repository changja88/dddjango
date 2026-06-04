# dddjango 네이밍 규약(DR-41) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dddjango 표준에 폴더/파일/클래스 네이밍 규약을 추가하고, §4 포트/어댑터 명명을 헥사고날 정석(확립 패턴명 예외 + 그 외 Port↔Adapter)으로 개정한다(DR-05/37 번복).

**Architecture:** 표준 markdown 문서 개정이다(코드 TDD 아님). 각 task는 claude(`dddjango/`)와 codex(`codex-dddjango/`) **미러를 동시 개정**하고, 끝에 미러 `diff`·자기모순 `grep`으로 검증한다. 단일 출처는 houserules `references/final.md`이고 SKILL.md·에이전트는 이를 인용하므로, **한 곳이라도 옛 명명(`DjangoProductLockPort`)이 남으면 자기모순**이다 — 종료 게이트로 차단.

**Tech Stack:** Markdown 표준 문서, bash(grep/diff), python3(백스톱 12종 회귀).

**정본:** 모든 AFTER 텍스트의 권위는 `workspace/design/2026-06-04-dddjango-naming-convention.md`(spec v2) §2·§3이다. 이 계획은 *어느 파일의 어느 토큰을* 바꾸는지와 검증을 명시한다.

---

## File Structure (영향 파일)

| 파일 | 책임 | 미러 쌍 |
|---|---|---|
| `dddjango/skills/discipline-houserules/references/final.md` | **단일 출처** — §2 트리·§3 표·§4 명명·폴더명 | `codex-dddjango/skills/discipline-houserules/references/final.md` (완전 byte-identical) |
| `dddjango/skills/discipline-houserules/SKILL.md` | §1.2 명명 요약·§3 레드플래그·infra 분할 | `codex-dddjango/.../discipline-houserules/SKILL.md` (frontmatter `user-invocable` 제외 byte-identical) |
| `dddjango/agents/design-architect.md` | 명세에 박을 명명 지시 | `codex-dddjango/skills/dddjango-design-architect/SKILL.md` (frontmatter/intro 제외 본문) |
| `dddjango/agents/discipline-reviewer.md` | 명명 위반 적발 패턴 | `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` (본문) |
| `dddjango/.claude-plugin/plugin.json` + codex `.codex-plugin/plugin.json` | 버전 1.1.0→1.2.0 | 버전만 동기 |
| `workspace/DEVLOG.md` | DR-41 엔트리(DR-05/37 번복 정정노트) | — |
| 메모리(레포 밖) | 세션 회상 | — |

**미러 검증 명령(반복 사용):**
- final.md: `diff dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md` → **빈 출력(exit 0)**.
- SKILL.md: `diff <(tail -n +5 dddjango/skills/discipline-houserules/SKILL.md) <(tail -n +4 codex-dddjango/skills/discipline-houserules/SKILL.md)` → **빈 출력**(claude는 `user-invocable: false` 1줄 더 있어 5/4 스킵).
- 자기모순 게이트: `grep -rn 'DjangoProductLockPort' dddjango/ codex-dddjango/` → **0건**(Repository는 `DjangoOrderRepository`라 무관).

---

## Task 1: houserules `references/final.md` 전면 개정 (단일 출처)

**Files:**
- Modify: `dddjango/skills/discipline-houserules/references/final.md` (§2 트리 L62-110 · §3 표 L167-213 · §4 명명 L219-233)
- Modify: `codex-dddjango/skills/discipline-houserules/references/final.md` (동일 — byte-identical 미러)

> 한 파일 안에서 §4(단일 출처)→§3 표→§2 트리 순으로 일관 개정한다. 부분 개정 금지(중간에 §4와 §3이 어긋나면 자기모순). 한 step으로 다 바꾼 뒤 검증.

- [ ] **Step 1: §4 명명 규약 개정 (claude final.md L219-233)**

§4 본문을 spec v2 §3(포트/어댑터 ⓑ 기준)으로 재서술한다. 핵심 변경:
- "추상화 ↔ 구현" 절(현 L228-231)의 "구현 = base명 유지(`DjangoProductLockPort`)"를 **삭제**하고 ⓑ 기준으로 교체:
  - **확립 패턴명(PoEAA/GoF: `Repository`·`Gateway` 등)**: 추상·구현 동일 접미사 유지 — `OrderRepository`/`DjangoOrderRepository`, `PaymentGateway`/`StripePaymentGateway`.
  - **일반 협력 포트(`...Port`)**: 헥사고날 쌍 — `ProductLockPort`/`DjangoProductLockAdapter`.
  - 판정: 외부 시스템 관문(결제·푸시·인증) = `Gateway`, BC 협력(ACL)·도메인 역할 추상 = `Port`.
- "파일명" 절(현 L233)에 클래스/파일 종류별 규칙 추가: 파일명 = 주 클래스 snake_case, `_app` 폐기, 이벤트 과거형 `<event>_event.py`→`<Name>Event`, 명세 `<name>_specification.py`→`<Name>Specification`, 스키마 `schema_in/out.py`→`<R>In`/`<R>Out`, 조회 selector 함수.
- `Interface`/`Impl` 금지는 유지. `Port`도 *구현*에선 위치 표식이라 안 쓴다는 1줄 추가.

AFTER 전문 권위 = spec v2 §1 핵심규칙·§2 표·§3.

- [ ] **Step 2: §3 표 정합 (claude final.md L167-213)**

§3 표의 명명 칼럼을 §4와 일치시킨다. 바꿀 토큰:
- L178 이벤트 `<event>.py` → `<event>_event.py` (`OrderPlacedEvent`)
- L179 명세 `<name>_spec.py` → `<name>_specification.py` (`OrderActiveSpecification`)
- L186 command `<usecase>_app.py` → `<usecase>_service.py` (`PlaceOrderService`)
- L187 query `<usecase>_query_app.py` → `<usecase>_query.py` (selector 함수 `def list_orders(...)`)
- L190 오케스트레이션 `<usecase>_service_app.py` → `<flow>_service.py` (`CheckoutService`)
- L176 포트 `<collaborator>_port.py` → `class ProductLockPort` 유지; 외부서비스 포트 행 추가 `payment_gateway.py`→`PaymentGateway`
- L202 ACL `<context>_acl.py → class DjangoProductLockPort` → `product_lock_adapter.py → class DjangoProductLockAdapter`
- L203 외부서비스 `service/ ... <external>_service.py` → `adapter/ ... <external>_<pattern>.py`(Gateway면 `stripe_payment_gateway.py → StripePaymentGateway`)

- [ ] **Step 3: §2 트리 정합 (claude final.md L62-110)**

§2 트리 주석의 파일명을 §3과 일치:
- L81 `exception.py` 인근 event 주석·L79 `event/` 주석에 `<event>_event.py`
- L85 `command/ ... <usecase>_app.py` → `<usecase>_service.py`
- L86 `query/ ... <usecase>_query_app.py` → `<usecase>_query.py` selector
- L89 `service/ ... <usecase>_service_app.py` → `<flow>_service.py`
- L99 `acl/ ... ` 주석 어댑터 명명·L100 `service/` → `adapter/`(외부서비스 어댑터)

- [ ] **Step 4: 폴더명 권장 절 추가 (claude final.md §3 끝 또는 §4 뒤)**

spec v2 §4(폴더명) 내용을 권장 절로 추가: 앱=핵심 애그리거트명 동일(단일 BC)/여러면 대표명, 애그리거트=단수, feature=유스케이스 단위, 유사 변형(`ordering`/`order`) 금지. "권장 수위(백스톱 없음, reviewer 점검)" 명시.

- [ ] **Step 5: claude final.md 자기모순·잔존 토큰 검증**

```bash
cd /Users/hyun/Desktop/dddjango
grep -n 'DjangoProductLockPort' dddjango/skills/discipline-houserules/references/final.md   # 기대: 0건
grep -nE '_app\.py|_query_app|_service_app' dddjango/skills/discipline-houserules/references/final.md  # 기대: 0건
grep -nE '<event>\.py|<name>_spec\.py' dddjango/skills/discipline-houserules/references/final.md  # 기대: 0건
```
Expected: 세 grep 모두 0건.

- [ ] **Step 6: codex final.md 미러 동기 + 검증**

claude final.md는 codex와 완전 byte-identical이므로, claude 개정 후 codex로 복사하거나 동일 편집 적용 후 검증:
```bash
diff dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md
```
Expected: 빈 출력(exit 0).

- [ ] **Step 7: Commit**

```bash
git add dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md
git commit -m "feat(standard): 네이밍 규약 §4 헥사고날 개정 + 종류별 명명 (DR-41)"
```

---

## Task 2: houserules `SKILL.md` 명명 요약·레드플래그 (claude+codex)

**Files:**
- Modify: `dddjango/skills/discipline-houserules/SKILL.md` (L29 infra 분할 · L34 §1.2 명명 · L55 §3 레드플래그)
- Modify: `codex-dddjango/skills/discipline-houserules/SKILL.md` (동일, frontmatter 제외)

- [ ] **Step 1: L34 §1.2 리포지토리·포트 명명 개정 (claude)**

BEFORE(L34): `구현은 기술 한정자 접두로 base 일치(`DjangoOrderRepository`·`DjangoProductLockPort`).`
AFTER: 확립 패턴명(`Repository`/`Gateway`)은 추상·구현 동일(`DjangoOrderRepository`·`StripePaymentGateway`), 일반 포트는 `...Port`(추상)↔`...Adapter`(구현)(`ProductLockPort`→`DjangoProductLockAdapter`). 상세 `references/final.md` §4. (파일명 약어 금지 유지)

- [ ] **Step 2: L55 §3 레드플래그 개정 (claude)**

BEFORE(L55): `...추상화 base명과 어긋나게(역할 접미사 탈락: `ProductLockPort`→`DjangoProductLock`)...`
AFTER: 위반 패턴을 재서술 — "일반 포트 구현이 `...Adapter`가 아니거나 개념 base명 불일치, 확립 패턴명(`Repository`/`Gateway`) 구현이 패턴명을 잃거나 기술 접두 누락, `Interface`/`Impl` 타입표식, 파일명 약어(`order_repo.py`)". `DjangoProductLockPort`를 정답으로 든 표현 제거.

- [ ] **Step 3: L29 infra 분할 개정 (claude)**

BEFORE(L29 일부): `infra_layer` 분할(`django_<app>`/`repository`/`service`; ...)`
AFTER: `...(`django_<app>`/`repository`/`adapter`; 외부 컨텍스트 직접 통합 시 `acl/`)` — 외부서비스 어댑터 폴더 `service`→`adapter`. (단 application `service/` 오케스트레이션·`domain_service/`는 무관 — 이 줄은 infra 분할만)

- [ ] **Step 4: L56 ACL 레드플래그 명명 점검 (claude)**

L56은 `acl/` 분리 규칙(유지). 명명 토큰이 있으면 어댑터명으로 정합, 없으면 무변경.

- [ ] **Step 5: 검증 + codex 동기**

```bash
grep -n 'DjangoProductLockPort' dddjango/skills/discipline-houserules/SKILL.md   # 기대: 0건
# codex 동일 편집 후:
diff <(tail -n +5 dddjango/skills/discipline-houserules/SKILL.md) <(tail -n +4 codex-dddjango/skills/discipline-houserules/SKILL.md)
```
Expected: grep 0건, diff 빈 출력.

- [ ] **Step 6: Commit**

```bash
git add dddjango/skills/discipline-houserules/SKILL.md codex-dddjango/skills/discipline-houserules/SKILL.md
git commit -m "feat(standard): houserules SKILL 명명 요약·레드플래그 헥사고날 정합 (DR-41)"
```

---

## Task 3: design-architect 에이전트 (claude+codex)

**Files:**
- Modify: `dddjango/agents/design-architect.md` (L38)
- Modify: `codex-dddjango/skills/dddjango-design-architect/SKILL.md` (본문 대응 줄)

- [ ] **Step 1: L38 명명 지시 개정 (claude)**

BEFORE(L38 일부): `구현=기술 한정자 접두로 base명 일치(`DjangoProductLockPort`)`
AFTER: `구현=확립 패턴명(`Repository`/`Gateway`)은 패턴명 유지(`DjangoOrderRepository`·`StripePaymentGateway`), 일반 포트는 `...Adapter`(`ProductLockPort`→`DjangoProductLockAdapter`)`. `Interface`/`Impl` 금지·파일명 약어 금지 유지. 외부 시스템 관문=`Gateway`/BC 협력=`Port` 판정 1줄.

- [ ] **Step 2: codex design-architect 동기**

`codex-dddjango/skills/dddjango-design-architect/SKILL.md`의 본문 대응 줄을 동일 텍스트로 개정(frontmatter/intro는 codex 고유).
```bash
grep -n 'DjangoProductLockPort' dddjango/agents/design-architect.md codex-dddjango/skills/dddjango-design-architect/SKILL.md  # 기대: 0건
# 본문 명명 단락 diff(줄 위치는 grep으로 재확인 후):
```
Expected: grep 0건, 본문 명명 단락 byte-identical.

- [ ] **Step 3: Commit**

```bash
git add dddjango/agents/design-architect.md codex-dddjango/skills/dddjango-design-architect/SKILL.md
git commit -m "feat(standard): design-architect 명명 지시 헥사고날 정합 (DR-41)"
```

---

## Task 4: discipline-reviewer 에이전트 (claude+codex)

**Files:**
- Modify: `dddjango/agents/discipline-reviewer.md` (L40)
- Modify: `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` (본문 대응 줄)

- [ ] **Step 1: L40 위반 적발 패턴 개정 (claude)**

BEFORE(L40 일부): `...추상화 base명 불일치(역할 접미사 탈락: `ProductLockPort`→`DjangoProductLock`)...`
AFTER: Task 2 Step 2와 동일 위반 패턴(일반 포트 구현이 `...Adapter` 아님/개념 base 불일치, 확립 패턴명 구현이 패턴명 상실, `Interface`/`Impl`, 파일명 약어). `DjangoProductLockPort` 정답 표현 제거 — 개정 후엔 그 자체가 위반(일반 포트 구현인데 `Port` 유지).

- [ ] **Step 2: codex discipline-reviewer 동기 + 검증**

```bash
grep -n 'DjangoProductLockPort' dddjango/agents/discipline-reviewer.md codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md  # 기대: 0건
```
Expected: grep 0건, 본문 명명 단락 byte-identical.

- [ ] **Step 3: Commit**

```bash
git add dddjango/agents/discipline-reviewer.md codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md
git commit -m "feat(standard): discipline-reviewer 명명 위반 패턴 헥사고날 정합 (DR-41)"
```

---

## Task 5: 종료 게이트 + 버전 + DEVLOG + 메모리

**Files:**
- Modify: `dddjango/.claude-plugin/plugin.json` + `codex-dddjango/.codex-plugin/plugin.json` (version)
- Modify: `workspace/DEVLOG.md` (DR-41 엔트리)
- Modify: 메모리 신규 슬러그 + `MEMORY.md`

- [ ] **Step 1: 전역 자기모순 게이트 (전체 레포)**

```bash
cd /Users/hyun/Desktop/dddjango
grep -rn 'DjangoProductLockPort' dddjango/ codex-dddjango/   # 기대: 0건 (Repository 무관)
grep -rnE '_app\.py|_query_app|_service_app' dddjango/ codex-dddjango/   # 기대: 0건
```
Expected: 모두 0건. 1건이라도 남으면 해당 파일로 돌아가 개정(자기모순 잔존 = NO-GO).

- [ ] **Step 2: 전체 미러 diff**

```bash
diff dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md
diff <(tail -n +5 dddjango/skills/discipline-houserules/SKILL.md) <(tail -n +4 codex-dddjango/skills/discipline-houserules/SKILL.md)
```
Expected: 둘 다 빈 출력.

- [ ] **Step 3: 백스톱 12종 회귀 (영향 0 확인)**

정상 트리 픽스처(또는 기존 합성 픽스처)에 백스톱 12종을 돌려 exit 0(거짓양성 0) 확인. 네이밍 미검사라 `service/`→`adapter/`·명명 개정이 백스톱을 깨지 않아야 한다.
```bash
for s in dddjango/scripts/check-*.py; do echo "== $s =="; python3 "$s" <정상-픽스처-경로> ; echo "exit=$?"; done
```
Expected: 전부 exit 0(또는 기존과 동일). 변화 있으면 조사.

- [ ] **Step 4: plugin.json 버전 1.1.0→1.2.0 (양쪽)**

```bash
# dddjango/.claude-plugin/plugin.json 과 codex-dddjango/.codex-plugin/plugin.json 의 "version" 을 1.2.0 으로
grep -n '"version"' dddjango/.claude-plugin/plugin.json codex-dddjango/.codex-plugin/plugin.json
```
명명 규약 = 사용자 가시(생성 코드 명명 변경) → minor bump.

- [ ] **Step 5: DEVLOG DR-41 엔트리 (DR-05/37 번복 정정노트)**

`workspace/DEVLOG.md`에 DR-41 추가: 네이밍 규약 추가 + §4 포트/어댑터 헥사고날 개정이 **DR-05/37의 `Port`-유지 명명을 번복**함을 명기(역사 보존). 적대 리뷰 4렌즈·외부 자료 근거·종료 게이트 결과 요약. "마지막 갱신" 날짜 갱신.

- [ ] **Step 6: 메모리 신규 + MEMORY.md 인덱스**

`~/.claude/projects/-Users-hyun-Desktop-dddjango/memory/` 에 `dddjango-naming-convention.md`(type:project) 생성: ⓑ 기준·미러 4종·종료 게이트·command/dto 백로그·DR-05/37 번복. `MEMORY.md`에 인덱스 1줄(DR-40 뒤).

- [ ] **Step 7: Commit**

```bash
git add dddjango/.claude-plugin/plugin.json codex-dddjango/.codex-plugin/plugin.json workspace/DEVLOG.md workspace/design/2026-06-04-dddjango-naming-convention*.md
git commit -m "eval(devlog): DR-41 네이밍 규약 추적 + 버전 1.2.0 + 게이트 (DR-05/37 번복)"
```

---

## Self-Review

**1. Spec coverage:**
- spec §1 핵심규칙 3줄 → Task 1 Step 1·2. ✓
- spec §2 종류별 표(도메인·응용·인프라·표현) → Task 1 Step 1-3. ✓
- spec §3 포트/어댑터 ⓑ → Task 1 Step 1, Task 2-4(SKILL·에이전트). ✓
- spec §4 폴더명 → Task 1 Step 4. ✓
- spec "구현 완결성 조건" 4건(자기모순 grep 0·에이전트 동시·미러 오프셋·DR 정정노트) → Task 3-4(에이전트)·Task 5 Step 1·2·5. ✓
- spec "변경 범위" RUBRIC 검토 → **갭**: RUBRIC 명명 항목 확인이 task에 없음 → Task 5에 step 추가 필요.

**2. Placeholder scan:** AFTER 전문을 spec 참조로 둔 곳이 있으나 바뀌는 토큰은 명시했다. "spec §X대로"는 정본 위임이라 허용(spec이 완성된 권위). 단 Task 1 Step 1의 §4 본문 재서술은 큰 단락이라 구현자가 spec v2 §3을 그대로 표준 문체로 옮긴다.

**3. Type consistency:** 명명 토큰이 task 간 일치 — `DjangoProductLockAdapter`(일반 포트 구현)·`StripePaymentGateway`(Gateway 패턴)·`PlaceOrderService`(응용)·`OrderPlacedEvent`(이벤트)가 Task 1·2·3·4에서 동일. ✓

**갭 보완:** Task 5에 RUBRIC 확인 step 추가 →

- [ ] **Task 5 Step 0(선): RUBRIC 명명 항목 확인** — `grep -niE '명명|naming|_app|Port|Repository' workspace/eval/rubric/RUBRIC.md` 로 옛 명명을 채점 기준에 박았는지 확인. 있으면 영향 파일에 추가·갱신, 없으면 무변경 기록.

---

## Execution Handoff

계획 저장: `workspace/design/2026-06-04-dddjango-naming-convention-plan.md`. 두 실행 옵션:

1. **Subagent-Driven (권장)** — task별 fresh 서브에이전트 + task 간 리뷰. 미러 동기·자기모순 게이트가 섬세해 task 경계에서 검증하기 좋음.
2. **Inline 실행** — 이 세션에서 executing-plans로 배치 실행(체크포인트). 미러 일관성을 한 곳에서 관리.

어느 방식으로 진행할까요?
