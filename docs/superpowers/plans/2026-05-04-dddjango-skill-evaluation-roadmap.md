# dddjango Skill Evaluation Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dddjango Codex 스킬을 감으로 수정하지 않고, baseline/with-plugin 평가, 원인 분석, 스킬 개선, 재측정, release gate 통과 순서로 안정화한다.

**Architecture:** `skills/`를 canonical source로 유지하고 `plugins/dddjango/skills/`는 Codex 배포 mirror로 동기화한다. 평가는 `evals/codex`의 케이스, 루브릭, 실행 스크립트, HTML 리포트를 단일 기준으로 삼고, release는 평가 gate 통과 후에만 실행한다.

**Tech Stack:** Python stdlib, unittest, Codex CLI `codex exec`, JSONL/JSON evaluation assets, Makefile release automation.

---

## 현재 상태

- 최신 기준 baseline 평균은 `81.0`이다.
- 현재 부분 재측정 기준 dddjango 평균은 `89.25`, lift는 `+10.19%`이다.
- pilot gate는 `+15%` 이상이므로 아직 release 조건을 만족하지 못한다.
- DRF/TDD 실패 케이스는 최근 수정 후 개별 출력 기준으로 개선되었지만, 전체 8개 케이스를 같은 하네스로 다시 측정하지 않았다.
- 현재 workspace에는 평가 하네스, 스킬, 테스트, 평가 산출물 변경이 섞여 있다.

## Phase Gates

| Phase | 목적 | 통과 기준 | 다음 단계 |
| --- | --- | --- | --- |
| Phase 0 | 현재 변경 분류 | 코드/스킬 변경과 raw 평가 산출물 분리 방침 확정 | Phase 1 |
| Phase 1 | 평가 하네스 고정 | dddjango variant가 실제 dddjango 스킬을 사용한다는 테스트 통과 | Phase 2 |
| Phase 2 | 깨끗한 전체 재측정 | 8개 dddjango 케이스를 같은 조건으로 재실행 | Phase 3 |
| Phase 3 | 원인 분석 | 실패/정체/느린 케이스가 case별로 분류됨 | Phase 4 |
| Phase 4 | 스킬 개선 | 각 수정마다 trigger, body, mirror sync, 테스트가 함께 변경됨 | Phase 5 |
| Phase 5 | 회귀 측정 | 전체 pilot gate 통과 또는 다음 개선 backlog 확정 | Phase 6 또는 반복 |
| Phase 6 | release | `make test-release`, `git diff --check`, 평가 report 확인 후 `make release` | 완료 |

## 파일 책임

- `skills/*/SKILL.md`: dddjango 스킬의 canonical source.
- `plugins/dddjango/skills/*/SKILL.md`: Codex plugin 배포용 mirror. canonical과 byte-for-byte 동일해야 한다.
- `evals/codex/cases/pilot.jsonl`: pilot 평가 케이스. phase 중간에 케이스를 바꾸지 않는다.
- `evals/codex/rubrics/grading-schema.json`: scoring weight와 success threshold.
- `evals/codex/rubrics/dddjango-rubric.md`: 수동 채점 규칙과 gate 정의.
- `evals/codex/scripts/run_prompts.py`: baseline/dddjango 실행 하네스.
- `evals/codex/scripts/grade_outputs.py`: 수동 grade 요약.
- `evals/codex/scripts/render_report.py`: HTML 비교 리포트 생성.
- `tests/test_codex_evaluation.py`: 평가 자산, mirror sync, 주요 policy regression 테스트.
- `workspace/codex-eval/iteration-*/`: 실행 출력, 로그, timing, report 산출물. 큰 raw log는 기본적으로 release commit에 포함하지 않는다.

## Phase 0: 변경 분류와 기준선 잠금

**Files:**
- Read: `git status --short`
- Read: `git diff --stat`
- Read: `workspace/codex-eval/iteration-1/grades.json`
- Read: `workspace/codex-eval/iteration-1/timing.json`

- [x] **Step 1: 현재 변경을 분류한다**

Run:

```bash
git status --short
git diff --stat
```

Expected:

```text
evals/codex/scripts/run_prompts.py, skills/*, plugins/dddjango/skills/*, tests/* 변경은 코드/스킬 변경으로 분류한다.
workspace/codex-eval/iteration-1/**/*.codex.log, *.output.md, report.html, grades.json, timing.json 변경은 평가 산출물로 분류한다.
```

- [x] **Step 2: raw 산출물 커밋 정책을 적용한다**

Decision:

```text
커밋 포함: 평가 하네스, 스킬, mirror, 테스트
커밋 제외 기본값: 큰 raw transcript인 *.codex.log
커밋 포함 가능: grades.json, timing.json, report.html, 대표 output.md. 단, release 판단 증거로 필요한 경우에만 포함한다.
```

- [x] **Step 3: 기준선 summary를 기록한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
```

Expected:

```text
baseline average_score = 81.0
dddjango average_score = 현재 측정값
lift.percent = 현재 측정값
```

## Phase 1: 평가 하네스 신뢰성 고정

**Files:**
- Modify: `evals/codex/scripts/run_prompts.py`
- Modify: `tests/test_codex_evaluation.py`

- [x] **Step 1: dddjango variant가 스킬 경로를 주입하는지 테스트한다**

Test expectations:

```python
command = build_codex_command(..., developer_instructions="...")
assert "-c" in command
assert "developer_instructions=" in " ".join(command)
assert "Django Ninja Schema/Router" in dddjango_developer_instructions(ROOT)
assert "RED pytest examples" in dddjango_developer_instructions(ROOT)
```

Run:

```bash
python3 -m unittest tests.test_codex_evaluation -v
```

Expected:

```text
OK
```

- [x] **Step 2: baseline 오염 방지 조건을 확인한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant baseline --case pilot-negative-drf --dry-run
```

Expected:

```text
출력 command에 --ignore-user-config가 포함된다.
출력 command에 dddjango developer_instructions가 포함되지 않는다.
```

- [x] **Step 3: dddjango 실행 조건을 확인한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant dddjango --case pilot-negative-drf --dry-run
```

Expected:

```text
출력 command에 developer_instructions가 포함된다.
developer_instructions 안에 repo의 skills 경로가 포함된다.
```

## Phase 2: 전체 재측정

**Files:**
- Write: `workspace/codex-eval/iteration-1/dddjango/*.output.md`
- Write: `workspace/codex-eval/iteration-1/dddjango/*.codex.log`
- Modify: `workspace/codex-eval/iteration-1/timing.json`

- [x] **Step 1: 같은 하네스로 dddjango 8개 케이스를 모두 재실행한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant dddjango --keep-going
```

Expected:

```text
dddjango/pilot-api-order-create: returncode=0
dddjango/pilot-implementation-coupon: returncode=0
dddjango/pilot-review-fat-model: returncode=0
dddjango/pilot-tdd-coupon: returncode=0
dddjango/pilot-db-orders: returncode=0
dddjango/pilot-review-view-logic: returncode=0
dddjango/pilot-api-standard: returncode=0
dddjango/pilot-negative-drf: returncode=0
```

- [x] **Step 2: DRF 금지어가 구현 코드로 나왔는지 스캔한다**

Run:

```bash
rg -n "from rest_framework|rest_framework|ModelViewSet|ViewSet|APIView|DefaultRouter|SimpleRouter|ModelSerializer|Serializer" workspace/codex-eval/iteration-1/dddjango/*.output.md
```

Expected:

```text
DRF 단어가 정책 설명이나 변환 설명에만 등장해야 한다.
DRF import, DRF class 상속, DRF router 코드가 있으면 Phase 3에서 DRF violation으로 분류한다.
```

- [x] **Step 3: timing 증가율을 계산한다**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path("workspace/codex-eval/iteration-1/timing.json").read_text())
by_variant = {}
for row in rows:
    if row.get("returncode") == 0:
        by_variant.setdefault(row["variant"], []).append(row["duration_sec"])
for variant, values in sorted(by_variant.items()):
    print(variant, round(sum(values) / len(values), 2), "sec", "count", len(values))
if "baseline" in by_variant and "dddjango" in by_variant:
    baseline = sum(by_variant["baseline"]) / len(by_variant["baseline"])
    dddjango = sum(by_variant["dddjango"]) / len(by_variant["dddjango"])
    print("duration_increase_percent", round(((dddjango / baseline) - 1) * 100, 2))
PY
```

Expected:

```text
baseline count = 8
dddjango count = 8
duration_increase_percent가 30 이하이면 gate 통과 후보이다.
30 초과이면 Phase 3에서 비용/속도 문제로 분류한다.
```

## Phase 3: 원인 분석과 채점

**Files:**
- Modify: `workspace/codex-eval/iteration-1/grades.json`
- Write: `workspace/codex-eval/iteration-1/SUMMARY.md` if a concise iteration note is needed

- [x] **Step 1: 각 output을 루브릭 기준으로 채점한다**

Use:

```text
evals/codex/rubrics/dddjango-rubric.md
evals/codex/rubrics/grading-schema.json
workspace/codex-eval/iteration-1/dddjango/*.output.md
```

Scoring rules:

```text
scores 합계는 100점 만점이다.
DRF 구현 코드가 있으면 drf_endorsed=true로 기록한다.
한국어가 주가 아니면 korean_first=false로 기록한다.
API 구현 요청에서 Django Ninja가 없으면 django_ninja_used=false로 기록한다.
TDD 케이스에서 RED 테스트, 예상 실패, GREEN 구현 연결이 약하면 testing_quality를 감점한다.
```

- [x] **Step 2: summary를 생성한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
python3 evals/codex/scripts/render_report.py workspace/codex-eval/iteration-1
```

Expected:

```text
workspace/codex-eval/iteration-1/report.html 이 갱신된다.
summary에 baseline, dddjango 평균과 lift.percent가 표시된다.
```

- [x] **Step 3: failure bucket을 작성한다**

Classification:

```text
A. Policy violation: DRF 코드 생성, Korean-first 실패, Django Ninja 누락
B. Low actionability: 파일 배치/코드/명령이 부족함
C. Architecture weakness: domain/application/infrastructure 경계가 흐림
D. TDD weakness: RED-GREEN-REFACTOR 연결이 약함
E. Cost issue: 품질 상승 대비 실행 시간이 과도함
```

## Phase 4: 스킬 개선

**Files:**
- Modify: `skills/<target-skill>/SKILL.md`
- Modify: `plugins/dddjango/skills/<target-skill>/SKILL.md`
- Modify: `tests/test_codex_evaluation.py`

Current Phase 3 result:

```text
Quality lift: +15.12% (pass; required >= +15%)
Time/cost increase: +26.41% (pass; required <= +30%)
DRF violations: 0 (pass)
Korean-first rate: 100% (pass)
Django Ninja compliance on API-relevant cases: 100% (pass)
TDD quality on TDD cases: 100% (pass)
Negative-control pass rate: 100% (pass)
```

- [x] **Step 1: 하나의 failure bucket만 선택한다**

Decision rule:

```text
Policy violation > TDD weakness > Low actionability > Architecture weakness > Cost issue 순서로 처리한다.
한 번에 여러 스킬을 넓게 고치지 않는다.
현재 선택: Cost issue를 먼저 줄였고 scoped injection 및 대형 케이스 word budget으로 시간 증가율을 약 +153%에서 +26.41%까지 낮췄다. fallback 스킬에 올바른 `api.add_router()` 예시를 고정해 negative-control 품질 회귀도 회복했다. 낮은 lift 케이스에 edge-case checklist, migration/pytest checks, severity-ranked findings를 추가해 quality lift도 +15.12%로 gate를 통과했다.
```

- [x] **Step 2: 스킬 description을 먼저 점검한다**

Check:

```text
트리거되어야 하는 사용자 표현이 YAML description에 들어 있는가?
description 길이가 Codex platform limit인 1024자를 넘지 않는가?
본문에만 "when to use"가 들어가 있지 않은가?
```

Run:

```bash
python3 -m unittest tests.test_codex_evaluation.CodexEvaluationAssetTests.test_codex_skill_descriptions_stay_within_platform_limit -v
```

Expected:

```text
OK
```

Result:

```text
tests/test_codex_evaluation.py에 description platform limit 회귀 테스트가 유지되어 있으며, `make test-release`에서 함께 통과했다.
```

- [x] **Step 3: SKILL.md 본문을 최소 수정한다**

Edit rule:

```text
Codex가 이미 아는 Django 일반론은 추가하지 않는다.
실패를 막는 짧은 절차, 금지 규칙, fallback, output contract만 추가한다.
예시는 길게 늘리지 않고 성공 조건을 명확히 만든다.
```

Result:

```text
`implementation-django-ninja`에 Django Ninja router object fallback만 최소 추가했다.
하네스 쪽은 case별 instruction scoping과 concise output directive로 cost issue를 줄였다.
```

- [x] **Step 4: mirror를 동기화한다**

Run:

```bash
cp skills/<target-skill>/SKILL.md plugins/dddjango/skills/<target-skill>/SKILL.md
python3 -m unittest tests.test_codex_evaluation.CodexEvaluationAssetTests.test_skills_are_synced_to_codex_plugin_mirror -v
```

Expected:

```text
OK
```

Result:

```text
`skills/implementation-django-ninja/SKILL.md`와 `plugins/dddjango/skills/implementation-django-ninja/SKILL.md`가 동일하게 갱신되었고 mirror sync 테스트가 `make test-release`에서 통과했다.
```

- [x] **Step 5: regression test를 추가한다**

Test requirement:

```text
정책성 실패는 tests/test_codex_evaluation.py에 문자열/명령 구성 테스트로 고정한다.
평가 하네스 실패는 build_codex_command 또는 dddjango_developer_instructions 단위 테스트로 고정한다.
```

Run:

```bash
python3 -m unittest tests.test_codex_evaluation -v
```

Expected:

```text
OK
```

Result:

```text
case별 scoped instruction, DRF override, TDD policy, report metadata/release gate 표시, large-case concise directive 회귀 테스트를 추가했다.
```

## Phase 5: 회귀 측정과 gate 판정

**Files:**
- Modify: `workspace/codex-eval/iteration-1/grades.json`
- Modify: `workspace/codex-eval/iteration-1/timing.json`
- Modify: `workspace/codex-eval/iteration-1/report.html`

- [x] **Step 1: 수정한 failure bucket 관련 케이스를 먼저 재측정한다**

Examples:

```bash
python3 evals/codex/scripts/run_prompts.py --variant dddjango --case pilot-negative-drf --keep-going
python3 evals/codex/scripts/run_prompts.py --variant dddjango --case pilot-tdd-coupon --keep-going
```

Expected:

```text
관련 케이스 returncode=0
해당 failure bucket이 재발하지 않는다.
```

- [x] **Step 2: 부분 재측정이 통과하면 전체 dddjango를 재측정한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant dddjango --keep-going
```

Expected:

```text
8개 케이스 returncode=0
```

- [x] **Step 3: gate를 판정한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
```

Gate:

```text
average dddjango score >= baseline보다 15% 높음
DRF violations = 0
Korean-first rate >= 95%
Django Ninja compliance >= 90%
TDD quality >= 80% on TDD cases
average time/cost increase <= 30% 또는 품질 상승으로 명시적 정당화 가능
negative-control pass rate >= 80%
```

- [x] **Step 4: gate 실패 시 다음 반복 범위를 줄인다**

Decision:

```text
품질 실패이면 Phase 3 bucket으로 돌아간다.
속도 실패이면 긴 skill body, 과도한 developer_instructions, 중복 guidance를 줄인다.
부분 케이스만 좋아지고 전체 평균이 낮으면 케이스별 delta가 작은 항목부터 개선한다.
```

Result:

```text
Gate가 통과했으므로 추가 반복 범위 축소는 필요하지 않다.
```

## Phase 6: 커밋과 release

**Files:**
- Read: `Makefile`
- Run: `make test-release`
- Run: `git diff --check`
- Run: `make release`

- [x] **Step 1: release 전 검증을 실행한다**

Run:

```bash
make test-release
git diff --check
```

Expected:

```text
unittest OK
git diff --check 출력 없음
```

Result:

```text
`make test-release`: 24 tests OK
`git diff --check`: 출력 없음
```

- [x] **Step 2: 커밋 대상을 stage한다**

Default include:

```bash
git add evals/codex/scripts/run_prompts.py
git add tests/test_codex_evaluation.py
git add skills
git add plugins/dddjango/skills
git add docs/superpowers/plans/2026-05-04-dddjango-skill-evaluation-roadmap.md
```

Optional include after review:

```bash
git add workspace/codex-eval/iteration-1/grades.json
git add workspace/codex-eval/iteration-1/timing.json
git add workspace/codex-eval/iteration-1/report.html
```

Default exclude:

```text
workspace/codex-eval/iteration-1/**/*.codex.log
```

Result:

```text
하네스, 스킬, 테스트, 계획 문서, 재현 가능한 평가 산출물만 stage했다.
원시 `.codex.log`는 커밋에서 제외했고 이후 HEAD 상태로 정리했다.
```

- [x] **Step 3: 평가 개선 커밋을 만든다**

Run:

```bash
git commit -m "fix: stabilize dddjango skill evaluation"
```

Expected:

```text
commit created
```

Result:

```text
873dd4e test: stabilize dddjango codex evaluation gate
```

- [x] **Step 4: gate 통과 후 release한다**

Run:

```bash
make release
```

Expected:

```text
새 버전 선택
release commit 생성
tag 생성
현재 브랜치와 tag가 원격으로 push됨
```

Result:

```text
`make release`에서 patch를 선택해 v0.1.7 릴리즈를 완료했다.
릴리즈 커밋과 태그를 생성했고 `origin/main`, `origin/v0.1.7` push가 통과했다.
```

## 운영 원칙

- 평가 케이스를 수정한 날에는 같은 iteration의 이전 점수와 직접 비교하지 않는다.
- 스킬을 수정한 뒤에는 최소 관련 케이스 1개, 가능하면 전체 8개 케이스를 재측정한다.
- release는 측정 전에 하지 않는다.
- 큰 raw transcript는 기본 커밋 대상이 아니다.
- `skills/`와 `plugins/dddjango/skills/`가 다르면 release하지 않는다.
- baseline은 개인 Codex 설정이나 로컬 dddjango 설치에 오염되면 안 된다.
- dddjango variant는 어떤 방식으로 스킬이 활성화되는지 명시적으로 검증되어야 한다.
