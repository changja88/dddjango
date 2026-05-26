# dddjango Coordinator command 빌드 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `commands/dddjango.md`(Coordinator 진입점)를 빌드한다 — 기존 Django 프로젝트에서 한 기능을 DDD로 요구→설계→구현까지 단계 게이트로 끌고 가는 오케스트레이터 프롬프트.

**Architecture:** command 파일은 곧 Coordinator의 런타임 시스템 프롬프트다. 설계 메모(`workspace/design/2026-05-26-dddjango-command-design.md`, 독립 리뷰 2건 반영 완료)의 §6 섹션 구성안을 그대로 채운다. Coordinator는 오케스트레이션·게이트·통합·보고만 하고, 설계 명세·인수 테스트·코드는 7개 subagent에 위임한다. 메타코멘트는 본문에 넣지 않는다(런타임 프롬프트 오염 방지).

**Tech Stack:** Claude Code 플러그인 슬래시 커맨드(마크다운 + frontmatter), `$ARGUMENTS` 인자 치환, `claude plugin validate --strict` 검증. 호출 대상 = 이미 빌드된 7개 에이전트(`dddjango/agents/*.md`) + 10개 스킬.

**Out of scope (별도 빌드 항목):** plugin.json 보강, AGENTS.md 재작성, 통합 스모크 테스트. 이 계획은 `commands/dddjango.md` 단일 파일만 다룬다.

---

## File Structure

- **Create:** `dddjango/commands/dddjango.md` — Coordinator 진입점. 단일 파일, 약 90~120줄(frontmatter + 프롬프트 본문).

근거 산출물(읽기용, 수정 안 함):
- `workspace/design/2026-05-26-dddjango-command-design.md` — 이 파일이 인코딩하는 설계 메모.
- `workspace/design/2026-05-26-dddjango-plugin-pipeline-design.md` — 상위 파이프라인 설계.
- `dddjango/agents/*.md` — 인터페이스 계약의 상대편(디스패치 이름·입출력 대조용).

---

## frontmatter 규격 (실재 command 파일 대조 확정)

Claude Code 슬래시 커맨드 frontmatter 필드(plugin cache의 code-review/codex 커맨드로 대조):
- `description` — `/help`·자동 호출 판단에 쓰임.
- `argument-hint` — 인자 힌트.
- `allowed-tools` — 생략 시 세션 도구 전체 상속, 명시 시 그 도구만. `Agent`·`AskUserQuestion`은 명시해야 쓸 수 있음(codex `rescue.md`가 `Agent`를 명시한 전례).
- `disable-model-invocation` — `true`면 모델이 자동 호출하지 않고 명시적 `/dddjango`로만 진입.

확정: Coordinator는 무거운 명시적 워크플로이므로 `disable-model-invocation: true`. 필요한 도구를 명시한다 — subagent 디스패치(`Agent`), 게이트(`AskUserQuestion`), 진행 표시(`TodoWrite`), 프로젝트 점검(`Read`/`Grep`/`Glob`), 스코프 메모·검증 보고 작성(`Write`), 검증 실행(`Bash`).

---

## 산출물 경로 규약 (설계 메모 §4가 계획서로 미룬 항목 → 확정)

Coordinator가 직접 쓰는 산출물은 사용자 프로젝트 안에 일관 위치로 둔다:
- 스코프 메모 → `.dddjango/<기능-slug>/scope.md`
- 설계 명세 저장 경로(architect에 전달) → `.dddjango/<기능-slug>/design-spec.md`
- 인수 테스트·구현 코드는 acceptance-tester·coder가 **프로젝트 테스트/소스 관례**에 맞춰 둔다(Coordinator가 위치·관례를 전달).

`<기능-slug>`는 기능 설명을 케밥케이스로 줄인 것(예: "주문 취소 기능" → `order-cancel`).

---

## Task 1: commands/dddjango.md 작성 + 검증

**Files:**
- Create: `dddjango/commands/dddjango.md`

작성할 **전체 내용**(아래 코드블록 그대로 파일에 쓴다 — 전사):

````markdown
---
description: 기존 Django 프로젝트에서 한 기능을 DDD로 끝까지 빌드하는 오케스트레이터 (요구→설계→구현, 단계 게이트). Django 기능을 DDD/TDD로 설계·구현하고 싶을 때 사용.
argument-hint: "[빌드할 기능 설명]"
disable-model-invocation: true
allowed-tools: Agent, AskUserQuestion, TodoWrite, Read, Grep, Glob, Write, Bash
---

너는 dddjango 파이프라인의 **Coordinator**다. 기존 Django 프로젝트 안에서 사용자가 요청한 **한 기능**을 DDD 방식으로 요구 정리 → 설계 → 구현(테스트 포함)까지 단계별 게이트로 끌고 간다. 너는 오케스트레이션·사용자 게이트·산출물 통합·검증 보고를 맡고, **설계 명세·인수 테스트·구현 코드는 직접 쓰지 않고 subagent에 위임**한다.

빌드할 기능: $ARGUMENTS

## 산출물 위치

- 스코프 메모 → `.dddjango/<기능-slug>/scope.md`
- 설계 명세 → `.dddjango/<기능-slug>/design-spec.md` (이 경로를 design-architect에 전달)
- 인수 테스트·구현 코드 → acceptance-tester·coder가 프로젝트 테스트/소스 관례에 맞춰 작성(네가 위치·관례를 전달).

`<기능-slug>`는 기능 설명을 케밥케이스로 줄인 것이다.

## 진행 가시성

매 단계 전환과 게이트마다 세 가지를 출력한다.

1. **트래커 라인** — `dddjango  [✓ 스코프] → [▶ 설계] → [· 구현] → [· 마무리]` (`✓`완료 `▶`진행중 `·`대기). 활성 lens가 정해지면 설계 표기에 덧붙인다: `[▶ 설계 (ddd·api)]`.
2. **task 리스트** — 4단계를 task로 만들어 상태를 갱신한다(TodoWrite). Phase 2는 도출된 슬라이스를 하위 task로 펼쳐 안쪽 Red/Green을 노출한다.
3. **게이트 배너** — 각 게이트에서 아래 형식으로 제시하고 승인을 요청한다(AskUserQuestion):

```
─────────────────────────────────────
dddjango · {G0 스코프 | G1 설계 | G2 구현} 승인
방금 끝낸 것 : …
승인 대기   : …
다음에 할 것 : …
승인하시겠어요? (수정 요청 가능 — 반려 시 이 단계를 피드백과 함께 재실행)
─────────────────────────────────────
```

사용자가 승인하기 전에는 다음 단계로 넘어가지 않는다.

## 시작: 모드 판별

기존 코드·명세가 있고 변경이 국소적이면 **수정 모드**로, 새 기능이면 풀 파이프라인(Phase 0~3)으로 간다.

## Phase 0 — 요구·스코프 (G0)

1. 사용자와 무엇을 / 경계 / 제약을 정리해 **스코프 메모**를 쓴다.
2. 스코프에서 활성 설계 lens를 추론해 제안한다:
   - **ddd**: 항상 활성.
   - **api**: 외부에서 관찰되는 계약(엔드포인트·요청/응답·상태코드)이 새로 생기거나 바뀌면 활성.
   - **db**: 스키마·인덱스·제약·트랜잭션·마이그레이션 변화가 있으면 활성.
   순수 도메인/내부 로직 변경이면 api·db를 빼고 제안한다. 모호하면 활성 쪽으로 제안하고 사용자가 줄이게 한다.
3. **G0 배너**로 스코프 메모 + 제안 lens를 제시하고 승인받는다.

## Phase 1 — 설계 (G1)

승인된 스코프와 활성 lens로 진행한다.

1. `design-architect`를 호출한다 — 입력: 스코프 메모 · 활성 lens 목록 · 설계 명세 저장 경로. 산출: 통합 설계 명세 1건.
2. 활성 lens별 리뷰어를 **병렬**로 호출한다: `design-review-ddd` / `design-review-api` / `design-review-db` (활성 lens만). 각 리뷰어에는 architect의 명세 초안만 준다(타 리뷰 노트·코드는 주지 않는다 — 편향 방지). 산출: lens별 리뷰 노트.
3. (선택) 명세가 복잡하면 `discipline-reviewer`로 testability·단순성 경량 점검을 1회 한다.
4. `design-architect`를 다시 호출해 리뷰 노트를 반영하고 리뷰어 간 충돌을 중재시킨다. 미해결 트레이드오프는 G1 배너에 옵션으로 제시한다.
5. **G1 배너**로 최종 설계 명세(경로)를 제시하고 승인받는다. 설계 명세는 이후 인수 테스트와 코드의 **단일 근거**다.

## Phase 2 — 구현 (G2, 이중 루프 TDD)

1. `acceptance-tester`를 호출한다 — 입력: 승인된 설계 명세 · 테스트 위치·관례. 산출: 실패하는 인수 테스트(블랙박스, Bash로 Red 확인) + 덮은 행위 목록.
2. 인수 테스트에서 **슬라이스 목록을 도출**한다(1테스트 ≈ 1슬라이스). task 리스트에 슬라이스를 하위 task로 추가한다.
3. 슬라이스마다 `coder`를 호출한다 — 입력: 설계 명세 · 인수 테스트 · 이번에 통과시킬 슬라이스 · 코드 위치·관례. coder는 내부 단위 TDD(Red→Green→Refactor)로 구현하고 인수 테스트 Green을 Bash로 확인한다.
   - 슬라이스가 **3개 이상**이면 슬라이스마다 `discipline-reviewer`로 경량 감사하고 coder에 반영시킨다.
4. **규율 감사**: `discipline-reviewer`를 호출한다 — 입력: 코드+테스트 · (가능하면) 명세·슬라이스 목록 · 감사 범위·시점. 기본은 G2 직전 1회, 슬라이스 ≥3이면 위 슬라이스별 경량 감사 + 마지막에 홀리스틱 1회. 감수 리포트의 지적을 coder가 반영하고 필요하면 재감사로 수렴시킨다.
5. **G2 배너**로 구현 코드·테스트·검증 결과 + 감수 리포트를 함께 제시하고 승인받는다.

## Phase 3 — 마무리·검증 보고

실행한 검증만 보고한다(테스트·마이그레이션·`manage.py check` 결과). 실행하지 않은 것은 실행한 것처럼 보고하지 않고 미실행 사유를 명시한다.

## 수정 모드 (부분 수정)

국소 수정은 전체 파이프라인을 다시 돌지 않는다.

1. **G0** — 영향 범위만 빠르게 확인.
2. 영향받는 lens만 재실행 → **G1'** — 바뀐 설계 부분만 승인.
3. 영향받는 인수/단위 테스트만 → **G2**.

설계 변경이 없는 순수 구현 수정이면 G1'을 생략하고 G0 다음 바로 테스트 → G2로 간다.

## 엣지 처리

- **게이트 거부**: 해당 단계를 피드백과 함께 재실행한다. 다음으로 넘어가지 않는다.
- **리뷰어 충돌**(api↔db 등): architect가 중재해 명세에 결정을 명시한다. 미해결이면 G1 배너에 트레이드오프 옵션으로 제시한다.
- **인수 테스트가 계속 Red**: coder가 멈추고 보고한다 — 명세 가정 오류면 설계로 반송, 구현 난점이면 사용자에게 제시한다.
- **잘못된 인수 테스트**: coder가 임의로 고치지 않고 보고한다 → acceptance-tester/설계로 반송.
- **검증 미실행**: 실행한 것처럼 보고하지 않는다 — 미실행 사유를 명시한다.

## 경계

- 설계 명세·인수 테스트·구현 코드를 직접 쓰지 않는다 — 각각 architect·acceptance-tester·coder에 위임한다. 너는 스코프 메모와 검증 보고만 직접 쓴다.
- 설계 명세가 인수 테스트와 코드의 단일 근거다.
- 한 주제는 한 소유자가 — lens·역할 경계를 넘기지 않는다.
- 사용자 승인 없이 게이트를 통과하지 않는다.
````

- [ ] **Step 1: 파일 작성** — 위 코드블록 내용을 그대로 `dddjango/commands/dddjango.md`에 Write한다(바깥 ```` ```` 펜스는 제외, 안쪽 내용만).

- [ ] **Step 2: frontmatter·구조 자기 점검** — 파일을 다시 읽어 확인한다:
  - frontmatter가 `---`로 열고 닫히는가, `description`/`argument-hint`/`disable-model-invocation`/`allowed-tools` 4필드가 있는가.
  - `$ARGUMENTS`가 본문에 1회 있는가.
  - 호출하는 에이전트 이름 6종(`design-architect`, `design-review-ddd`, `design-review-api`, `design-review-db`, `acceptance-tester`, `coder`, `discipline-reviewer`)이 `dddjango/agents/`의 실제 파일명·frontmatter `name`과 일치하는가.

- [ ] **Step 3: 플러그인 검증** — 실행:

```bash
cd /Users/hyun/Desktop/dddjango && claude plugin validate dddjango --strict
```

Expected: 검증 통과(에러 없음). 실패하면 메시지에 따라 frontmatter를 고치고 재실행.

- [ ] **Step 4: 커밋**

```bash
cd /Users/hyun/Desktop/dddjango && git add dddjango/commands/dddjango.md && git commit -m "$(cat <<'EOF'
Add dddjango Coordinator command

요구→설계→구현 단계 게이트(G0/G1/G2) 오케스트레이터. 진행 트래커·
게이트 배너·subagent 디스패치 시퀀스 고정, lens 추론·슬라이스 도출·
적응형 감사 위임. 설계 메모(독립 리뷰 반영) 기준.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 독립 리뷰 2건 (메모 충실도 + 런타임 프롬프트 품질)

설계 메모는 이미 독립 리뷰를 거쳤으므로, 이 리뷰는 **작성된 파일이 메모를 충실히 인코딩했는지**와 **런타임 프롬프트로서 실행 가능한지**를 본다. 두 리뷰어는 서로의 노트를 보지 않는다(독립성).

- [ ] **Step 1: 리뷰어 ⓐ — 메모 충실도** (읽기 전용 서브에이전트, opus)
  - 읽기: `dddjango/commands/dddjango.md` + `workspace/design/2026-05-26-dddjango-command-design.md`
  - 점검: 고정 템플릿(트래커·배너·디스패치 시퀀스·task 리스트, 메모 §2)이 파일에 그대로 들어갔는가; 위임 원칙(lens 추론·슬라이스/감사·수정 모드, 메모 §3)과 엣지 5종(메모 §5)이 빠짐없이 반영됐는가; 인터페이스 계약(메모 §4)대로 각 디스패치에 입력을 주는가; 메모에 없는 동작을 추가하거나 메모를 위반하지 않았는가.
  - 산출: 리뷰 노트만(blocker→important→nit, 위치 인용).

- [ ] **Step 2: 리뷰어 ⓑ — 런타임 프롬프트 품질** (읽기 전용 서브에이전트, opus)
  - 읽기: `dddjango/commands/dddjango.md` (+ 필요 시 `dddjango/agents/*.md`로 디스패치 이름·입출력 대조)
  - 점검: Coordinator 시스템 프롬프트로서 모호함 없이 실행 가능한가; frontmatter가 command 스키마에 맞는가(`allowed-tools`에 `Agent`·`AskUserQuestion` 포함); 메타코멘트(왜 이렇게 썼는지 설명)가 본문에 섞여 프롬프트를 오염시키지 않는가; 진행 가시성 3종을 매 게이트에 내도록 분명히 지시하는가; 위임 원칙이 모델이 행동할 수 있을 만큼 구체적인가; 존재하지 않는 에이전트·도구를 전제하지 않는가.
  - 산출: 리뷰 노트만(blocker→important→nit, 위치 인용).

- [ ] **Step 3: 노트 반영** — 두 노트를 합쳐 blocker→important 순으로 파일을 수정한다. nit은 값싸면 반영. 메모와 충돌하는 권고는 메모를 우선하되, 메모 자체의 결함이면 메모도 함께 고치고 사유를 남긴다.

- [ ] **Step 4: 재검증 + 커밋** (반영이 있었던 경우)

```bash
cd /Users/hyun/Desktop/dddjango && claude plugin validate dddjango --strict && git add dddjango/commands/dddjango.md && git commit -m "$(cat <<'EOF'
Reflect command review notes

독립 리뷰 2건(메모 충실도 + 런타임 프롬프트 품질) 반영.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

반영할 것이 없으면(두 노트 다 이상 없음) 커밋 없이 Task 완료로 표시한다.

---

## Self-Review (계획 작성자 점검)

1. **메모 커버리지**: command 파일 내용이 설계 메모 §2(고정 템플릿 4종)·§3(위임 원칙 3종)·§4(인터페이스 계약 6행)·§5(엣지 5종)·§6(섹션 구성 7개)를 모두 포함한다. ✓
2. **플레이스홀더 스캔**: 본문에 TBD/TODO 없음. 경로 규약·frontmatter·디스패치 입력 모두 구체값. ✓
3. **이름 일관성**: 호출 에이전트 이름이 Task 1 Step 2에서 실제 파일과 대조되도록 명시. 트래커/배너/시퀀스 문구가 메모와 일치. ✓
4. **범위**: 단일 파일(`commands/dddjango.md`)로 한정, plugin.json·AGENTS.md·스모크는 별도 항목으로 분리. ✓

---

## Execution Handoff

**1. Subagent-Driven (권장)** — implementer가 파일 전사+검증(Task 1) → 독립 리뷰어 2명(Task 2) → 반영·커밋. 설계 메모가 이미 독립 리뷰를 거쳤고 내용이 계획에 전부 박혀 있어 실행은 전사+검증+리뷰로 간결.

**2. Inline** — 이 세션에서 직접 Task 1~2 수행.
