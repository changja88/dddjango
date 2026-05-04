# dddjango Comprehensive Performance Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dddjango 스킬을 Codex와 Claude 양쪽에서 제품화 가능한 수준으로 검증하기 위해 품질, 트리거, 사용성, 성능, 설치/배포, 운영 회귀까지 단계별로 측정한다.

**Architecture:** 기존 `evals/codex`와 `evals/claude` 하네스를 유지하되, 평가 suite를 `smoke`, `benchmark`, `trigger`, `usability`, `real-repo`, `release`로 확장한다. 모든 평가는 with/without dddjango 비교와 HTML 리포트를 기본 산출물로 남기며, `skills/`를 canonical source로 두고 `plugins/dddjango/skills/` mirror 일치를 release gate에 포함한다.

**Tech Stack:** Python stdlib, unittest, Codex CLI, Claude CLI, JSONL/JSON evaluation assets, static HTML report, Makefile release automation.

---

## Progress Dashboard

| Phase | 상태 | 목적 | 주요 산출물 |
| --- | --- | --- | --- |
| Phase 0 | Done | 현재 평가 자산과 완료 상태 정리 | 이 문서, 기존 roadmap 링크 |
| Phase 1 | Done | Codex 8-case smoke 및 1차 gate 통과 | `workspace/codex-eval/iteration-1/report.html` |
| Phase 2 | Blocked | Claude smoke 측정 | `workspace/claude-eval/iteration-1/report.html` |
| Phase 3 | Done | 24-case benchmark suite 확장 | `evals/shared/cases/benchmark.jsonl` |
| Phase 4 | Done | trigger precision/recall suite 확장 | `evals/shared/cases/trigger.jsonl` |
| Phase 5 | Pending | usability/manual review 체계 추가 | `evals/shared/rubrics/usability-checklist.md` |
| Phase 6 | Pending | real repo forward test 구성 | `evals/fixtures/django-*` 또는 외부 fixture |
| Phase 7 | Pending | Codex/Claude full benchmark 반복 측정 | iteration별 HTML dashboard |
| Phase 8 | Pending | marketplace/fresh install 검증 | release install log, README 검증 |
| Phase 9 | Pending | beta 사용자 평가 | feedback summary, regression cases |
| Phase 10 | Pending | 운영 회귀 체계 고정 | smoke/full release gate |

## Current Baseline

- Codex 1차 파일럿은 `docs/superpowers/plans/2026-05-04-dddjango-skill-evaluation-roadmap.md` 기준 완료했다.
- Codex 1차 결과:
  - baseline average: `81.0`
  - dddjango average: `93.25`
  - quality lift: `+15.12%`
  - time increase: `+26.41%`
  - DRF violations: `0`
  - Korean-first rate: `100%`
  - Django Ninja compliance: `100%`
  - TDD quality: `100%`
  - negative-control pass rate: `100%`
- Claude 1차 측정은 CLI 인증/조직 정책으로 blocked 상태다.
  - 관측된 blocker: Claude Code subscription access disabled
  - 필요 조치: `ANTHROPIC_API_KEY` 설정 또는 조직의 Claude Code subscription access 허용

## File Responsibilities

- `evals/codex/cases/pilot.jsonl`: Codex smoke suite의 현재 8개 기준 케이스.
- `evals/codex/scripts/run_prompts.py`: Codex with/without dddjango 실행 하네스.
- `evals/claude/scripts/run_prompts.py`: Claude with/without dddjango 실행 하네스.
- `evals/codex/scripts/grade_outputs.py`: 수동 grade summary 계산기.
- `evals/codex/scripts/render_report.py`: Codex/Claude 공용 HTML report renderer.
- `evals/codex/rubrics/grading-schema.json`: 현재 scoring schema.
- `evals/codex/rubrics/dddjango-rubric.md`: 현재 수동 채점 기준.
- `workspace/codex-eval/iteration-*`: Codex 실행 결과와 HTML report.
- `workspace/claude-eval/iteration-*`: Claude 실행 결과와 HTML report.
- `skills/`: canonical dddjango skill source.
- `plugins/dddjango/skills/`: Codex 배포용 mirror.
- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `.claude-plugin/plugin.json`: Claude plugin manifest.
- `.claude-plugin/marketplace.json`: Claude marketplace manifest.
- `README.md`: 사용자 설치/평가/release 안내.

## Release Gates

| Gate | 기준 |
| --- | --- |
| Smoke execution | Codex와 Claude 핵심 smoke case 100% 실행 성공 |
| Quality lift | full benchmark에서 with dddjango가 baseline 대비 `+15%` 이상 |
| Time increase | 평균 실행 시간 증가율 `+30%` 이하 |
| DRF violation | 구현 코드 기준 `0` |
| Django Ninja compliance | API 관련 케이스 `95%` 이상 |
| TDD quality | TDD 관련 케이스 `90%` 이상 |
| Trigger recall | positive trigger `95%` 이상 |
| Trigger precision | negative trigger 오염 `5%` 이하 |
| Korean-first | 한국어 요청 `95%` 이상 |
| Mirror sync | `skills/`와 `plugins/dddjango/skills/` byte-for-byte 일치 |
| Fresh install | Codex/Claude fresh install 성공 |
| HTML report | 각 iteration에 with/without 표와 gate verdict 포함 |

## Phase 0: Current State Lock

**Files:**
- Read: `git status --short`
- Read: `docs/superpowers/plans/2026-05-04-dddjango-skill-evaluation-roadmap.md`
- Read: `workspace/codex-eval/iteration-1/report.html`
- Read: `workspace/claude-eval/iteration-1/report.html`

- [x] **Step 1: 기존 1차 Codex 평가 완료 상태를 확인한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
```

Expected:

```text
baseline average_score = 81.0
dddjango average_score = 93.25
lift.percent >= 15
```

- [x] **Step 2: 현재 Claude blocker를 문서화한다**

Run:

```bash
python3 evals/codex/scripts/render_report.py workspace/claude-eval/iteration-1 --platform Claude
```

Expected:

```text
workspace/claude-eval/iteration-1/report.html 에 Claude 인증 blocker가 표시된다.
```

- [x] **Step 3: 최종 단계까지 추적할 마스터 플랜을 생성한다**

Result:

```text
docs/superpowers/plans/2026-05-04-dddjango-comprehensive-performance-evaluation.md
```

## Phase 1: Codex Smoke Suite

**Files:**
- Read: `evals/codex/cases/pilot.jsonl`
- Write: `workspace/codex-eval/iteration-*/baseline/*.output.md`
- Write: `workspace/codex-eval/iteration-*/dddjango/*.output.md`
- Modify: `workspace/codex-eval/iteration-*/grades.json`
- Modify: `workspace/codex-eval/iteration-*/timing.json`
- Modify: `workspace/codex-eval/iteration-*/report.html`

- [x] **Step 1: Codex smoke iteration을 생성한다**

Run:

```bash
python3 evals/codex/scripts/init_iteration.py --output workspace/codex-eval/iteration-1
```

Expected:

```text
8개 prompt, answer-key, grades.json, timing.json template 생성
```

- [x] **Step 2: baseline과 dddjango를 모두 실행한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant baseline --keep-going
python3 evals/codex/scripts/run_prompts.py --variant dddjango --keep-going
```

Expected:

```text
8 baseline cases returncode=0
8 dddjango cases returncode=0
```

- [x] **Step 3: 수동 채점과 HTML report를 갱신한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
python3 evals/codex/scripts/render_report.py workspace/codex-eval/iteration-1
```

Expected:

```text
quality lift >= 15%
time increase <= 30%
DRF violations = 0
workspace/codex-eval/iteration-1/report.html 생성
```

## Phase 2: Claude Smoke Suite

**Files:**
- Read: `evals/claude/scripts/init_iteration.py`
- Read: `evals/claude/scripts/run_prompts.py`
- Write: `workspace/claude-eval/iteration-*/baseline/*.output.md`
- Write: `workspace/claude-eval/iteration-*/dddjango/*.output.md`
- Modify: `workspace/claude-eval/iteration-*/grades.json`
- Modify: `workspace/claude-eval/iteration-*/timing.json`
- Modify: `workspace/claude-eval/iteration-*/report.html`

- [x] **Step 1: Claude smoke iteration을 생성한다**

Run:

```bash
python3 evals/claude/scripts/init_iteration.py --output workspace/claude-eval/iteration-1
```

Expected:

```text
Codex pilot과 같은 8개 prompt, answer-key, grades.json, timing.json template 생성
```

- [x] **Step 2: blocker pilot을 먼저 실행한다**

Run:

```bash
python3 evals/claude/scripts/run_prompts.py --variant baseline --case pilot-negative-drf --iteration workspace/claude-eval/iteration-1 --keep-going
```

Observed:

```text
Claude Code subscription access disabled
ANTHROPIC_API_KEY unset
```

- [ ] **Step 3: Claude 인증을 준비한다**

Required:

```bash
export ANTHROPIC_API_KEY=...
```

or:

```text
조직 설정에서 Claude Code subscription access 허용
```

- [ ] **Step 4: Claude baseline과 dddjango smoke를 실행한다**

Run:

```bash
python3 evals/claude/scripts/run_prompts.py --variant baseline --iteration workspace/claude-eval/iteration-1 --keep-going
python3 evals/claude/scripts/run_prompts.py --variant dddjango --iteration workspace/claude-eval/iteration-1 --keep-going
python3 evals/codex/scripts/render_report.py workspace/claude-eval/iteration-1 --platform Claude
```

Expected:

```text
8 baseline cases returncode=0
8 dddjango cases returncode=0
workspace/claude-eval/iteration-1/report.html 생성
```

## Phase 3: Shared Benchmark Suite

**Files:**
- Create: `evals/shared/cases/benchmark.jsonl`
- Create: `evals/shared/cases/README.md` only if needed for evaluator-facing docs outside skill packages
- Modify: `evals/codex/scripts/init_iteration.py`
- Modify: `evals/claude/scripts/init_iteration.py`
- Modify: `tests/test_codex_evaluation.py`
- Modify: `tests/test_claude_evaluation.py`

- [x] **Step 1: 24-case benchmark taxonomy를 고정한다**

Cases:

```text
Django Ninja API: 4
DDD architecture: 4
DB design/performance: 3
TDD/pytest: 4
Code review: 4
Clean code/refactoring: 3
Negative control: 2
```

- [x] **Step 2: benchmark JSONL을 작성한다**

Schema:

```json
{
  "id": "benchmark-api-order-status",
  "category": "django-ninja-api",
  "prompt": "주문 상태 변경 API를 Django Ninja와 DDD 기준으로 설계하고 구현 예시를 보여줘.",
  "expectations": [
    "Django Ninja router and Schema usage",
    "application service boundary",
    "transaction or concurrency note",
    "pytest example"
  ],
  "forbidden": [
    "DRF ModelViewSet",
    "rest_framework imports"
  ]
}
```

- [x] **Step 3: init_iteration에서 suite 선택을 지원한다**

Command:

```bash
python3 evals/codex/scripts/init_iteration.py --suite benchmark --output workspace/codex-eval/iteration-2
python3 evals/claude/scripts/init_iteration.py --suite benchmark --output workspace/claude-eval/iteration-2
```

Expected:

```text
24개 benchmark prompt가 생성된다.
```

- [x] **Step 4: suite 선택 테스트를 추가한다**

Run:

```bash
python3 -m unittest tests.test_codex_evaluation tests.test_claude_evaluation -v
```

Expected:

```text
benchmark suite count = 24
pilot/smoke suite count = 8
```

## Phase 4: Trigger Precision/Recall Suite

**Files:**
- Create: `evals/shared/cases/trigger.jsonl`
- Modify: `evals/codex/scripts/render_report.py`
- Modify: `evals/codex/rubrics/grading-schema.json`
- Modify: `tests/test_codex_evaluation.py`

- [x] **Step 1: trigger case taxonomy를 작성한다**

Cases:

```text
Positive trigger: 10
Negative trigger: 10
Ambiguous trigger: 6
Conflict trigger: 4
```

- [x] **Step 2: positive trigger 케이스를 작성한다**

Examples:

```text
Django Ninja로 주문 생성 API를 DDD 구조로 설계해줘.
pytest로 쿠폰 적용 기능을 TDD 방식으로 구현해줘.
이 Django 모델이 fat model인지 리뷰해줘.
```

- [x] **Step 3: negative trigger 케이스를 작성한다**

Examples:

```text
FastAPI로 health check API를 만들어줘.
Python으로 CSV 파일을 파싱하는 스크립트를 작성해줘.
React 컴포넌트의 props 구조를 정리해줘.
```

- [x] **Step 4: trigger report matrix를 추가한다**

HTML table:

```text
Case | Trigger Type | Expected Behavior | Observed Behavior | Precision/Recall Impact | Pass/Fail
```

- [x] **Step 5: trigger gate를 계산한다**

Gate:

```text
positive recall >= 95%
negative pollution <= 5%
ambiguous handling >= 80%
conflict handling >= 80%
```

## Phase 5: Usability and Manual Review

**Files:**
- Create: `evals/shared/rubrics/usability-checklist.md`
- Modify: `evals/codex/rubrics/grading-schema.json`
- Modify: `evals/codex/scripts/grade_outputs.py`
- Modify: `evals/codex/scripts/render_report.py`

- [ ] **Step 1: usability checklist를 작성한다**

Checklist:

```text
1. 실행 가능한 Django/Ninja 문법인가
2. 파일 구조와 import가 현실적인가
3. migration, transaction, test 고려가 있는가
4. 한국어 요청에 자연스럽게 답하는가
5. 정책 설명이 과하게 반복되지 않는가
6. 사용자가 바로 적용 가능한 수준인가
```

- [ ] **Step 2: manual review score를 grades.json에 추가한다**

Fields:

```json
{
  "usability": {
    "actionable": 5,
    "concise": 4,
    "realistic_file_layout": 5,
    "korean_quality": 5,
    "notes": "바로 적용 가능"
  }
}
```

- [ ] **Step 3: HTML에 usability summary를 추가한다**

HTML table:

```text
Case | Actionable | Concise | Realistic Layout | Korean Quality | Notes
```

## Phase 6: Real Repo Forward Test

**Files:**
- Create: `evals/fixtures/` or document external fixture repo path
- Create: `evals/shared/cases/real-repo.jsonl`
- Modify: `evals/codex/scripts/run_prompts.py`
- Modify: `evals/claude/scripts/run_prompts.py`

- [ ] **Step 1: fixture 전략을 선택한다**

Preferred:

```text
작고 공개 가능한 Django fixture repo를 `evals/fixtures/`에 둔다.
```

Alternative:

```text
private fixture repo를 사용하되 report에는 anonymized summary만 남긴다.
```

- [ ] **Step 2: real-repo task를 작성한다**

Tasks:

```text
fat model 리팩터링
Django Ninja API 추가
pytest 테스트 추가
DB index/migration 리뷰
view logic service layer 이동
DRF endpoint를 Django Ninja로 전환
```

- [ ] **Step 3: diff 기반 평가를 추가한다**

Measure:

```text
tests pass 여부
diff 적용 가능성
reviewer 수정 요청 수
architecture violation 감소율
```

Gate:

```text
실제 코드 적용 가능성 >= 80%
테스트 통과율 >= 90%
reviewer 수정 요청 baseline 대비 20% 이상 감소
architecture violation baseline 대비 30% 이상 감소
```

## Phase 7: Full Benchmark Execution

**Files:**
- Write: `workspace/codex-eval/iteration-*/`
- Write: `workspace/claude-eval/iteration-*/`

- [ ] **Step 1: Codex benchmark를 3회 반복 실행한다**

Run:

```bash
python3 evals/codex/scripts/init_iteration.py --suite benchmark --output workspace/codex-eval/iteration-2
python3 evals/codex/scripts/run_prompts.py --variant baseline --iteration workspace/codex-eval/iteration-2 --keep-going
python3 evals/codex/scripts/run_prompts.py --variant dddjango --iteration workspace/codex-eval/iteration-2 --keep-going
```

Repeat:

```text
iteration-2
iteration-3
iteration-4
```

- [ ] **Step 2: Claude benchmark를 3회 반복 실행한다**

Run:

```bash
python3 evals/claude/scripts/init_iteration.py --suite benchmark --output workspace/claude-eval/iteration-2
python3 evals/claude/scripts/run_prompts.py --variant baseline --iteration workspace/claude-eval/iteration-2 --keep-going
python3 evals/claude/scripts/run_prompts.py --variant dddjango --iteration workspace/claude-eval/iteration-2 --keep-going
```

Repeat:

```text
iteration-2
iteration-3
iteration-4
```

- [ ] **Step 3: 반복 결과의 평균과 분산을 report에 표시한다**

Summary:

```text
platform | suite | average_score | lift | duration_increase | stddev | gate
```

## Phase 8: Marketplace and Fresh Install Verification

**Files:**
- Read: `.codex-plugin/plugin.json`
- Read: `.claude-plugin/plugin.json`
- Read: `.claude-plugin/marketplace.json`
- Read: `README.md`

- [ ] **Step 1: Codex fresh install을 검증한다**

Run from a disposable profile:

```bash
codex plugin marketplace add changja88/dddjango
```

Expected:

```text
dddjango marketplace가 추가되고 설치 가능해야 한다.
```

- [ ] **Step 2: Claude fresh install을 검증한다**

Run:

```bash
claude plugin validate .
claude plugin marketplace add changja88/dddjango
claude plugin install dddjango@dddjango
```

Expected:

```text
manifest validation 통과, marketplace 추가, install 성공
```

- [ ] **Step 3: README 설치 명령을 실제 명령과 맞춘다**

Check:

```text
README의 설치 명령이 현재 marketplace와 tag 정책에 맞는가
```

## Phase 9: Beta User Evaluation

**Files:**
- Create: `docs/superpowers/plans/2026-05-04-dddjango-beta-feedback.md`
- Modify: `evals/shared/cases/regression.jsonl`

- [ ] **Step 1: beta 사용자 그룹을 정한다**

Targets:

```text
Django 실무자 1명
Django 초급자 1명
DDD 관심자 1명
테스트/TDD 중심 사용자 1명
```

- [ ] **Step 2: feedback template을 작성한다**

Questions:

```text
어떤 prompt에서 유용했는가
어떤 prompt에서 과하게 개입했는가
답변이 너무 길거나 짧았는가
DRF/Ninja 정책이 명확했는가
실제 코드에 적용했는가
재사용 의향이 있는가
```

- [ ] **Step 3: 실패 prompt를 regression suite에 추가한다**

Rule:

```text
사용자가 불만을 제기한 prompt는 원인 분석 후 `evals/shared/cases/regression.jsonl`에 추가한다.
```

## Phase 10: Operating Regression System

**Files:**
- Modify: `Makefile`
- Modify: `README.md`
- Modify: `evals/shared/cases/regression.jsonl`
- Modify: `docs/superpowers/plans/2026-05-04-dddjango-comprehensive-performance-evaluation.md`

- [ ] **Step 1: make smoke-eval을 추가한다**

Command:

```bash
make smoke-eval
```

Expected:

```text
Codex smoke 실행, grade summary, HTML report 생성
```

- [ ] **Step 2: make full-eval을 추가한다**

Command:

```bash
make full-eval
```

Expected:

```text
Codex/Claude full benchmark 실행 또는 Claude auth blocker를 명확히 표시
```

- [ ] **Step 3: release gate에 평가 확인을 연결한다**

Rule:

```text
make release 전 `make test-release`, `git diff --check`, latest smoke report 확인을 수행한다.
```

- [ ] **Step 4: 운영 주기를 README에 기록한다**

Cadence:

```text
매 커밋: smoke
매 release: smoke + benchmark
월 1회: trigger/negative control 확장
큰 스킬 수정 후: full benchmark 3회 반복
사용자 이슈 발생 시: regression case 추가
```

## Next Action Queue

1. Claude 인증 blocker를 해결한다.
2. Phase 2 Step 4를 실행해서 Claude smoke report를 실제 점수로 채운다.
3. usability checklist와 manual score 필드를 `grades.json`/report에 추가한다.
4. real repo fixture 전략을 확정한다.
5. Codex/Claude full benchmark를 3회 반복 측정한다.
6. fresh install 검증 후 release gate를 확정한다.

## Tracking Rules

- 새 평가 suite를 추가할 때마다 이 문서의 해당 Phase checkbox를 갱신한다.
- 평가 실행마다 `workspace/<platform>-eval/iteration-N/report.html`을 생성한다.
- 실패 케이스는 수정하기 전에 failure bucket에 먼저 분류한다.
- 스킬을 수정하면 반드시 `skills/`와 `plugins/dddjango/skills/` mirror sync를 확인한다.
- raw `.codex.log`와 `.claude.log`는 기본적으로 커밋하지 않는다.
- release 판단에는 HTML report와 `make test-release` 결과를 함께 사용한다.
