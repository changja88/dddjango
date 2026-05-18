# dddjango Eval-Driven Plugin Hardening Process Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide whether the dddjango plugin needs more hardening by reviewing eval quality, latest reports, plugin value delta, and repeated failure patterns before changing skill or runtime files.

**Architecture:** Treat evals as the decision gate, not as a score dashboard. Each cycle starts from the canonical latest reports, validates the eval pack and report plumbing, classifies failures by root cause, makes the smallest justified plugin or eval change, then verifies with targeted and full eval runs.

**Tech Stack:** Markdown process checklist, existing eval buckets in `workspace/develop/eval`, lv-up planning files in `workspace/develop/lv_up_plan`, Python stdlib eval scripts in `workspace/scripts`, `make eval-all`, local static report server on `http://127.0.0.1:8765`.

---

## File Structure

- Read: `workspace/develop/eval/<bucket>/eval_goal.md`
  - Confirms the target capability for each bucket.
- Read: `workspace/develop/eval/<bucket>/cases/plugin/public/*.md`
  - Confirms the public prompts and whether they cover the goal.
- Read: `workspace/develop/eval/<bucket>/answer/*.yaml`
  - Confirms oracle hard gates, expected outcomes, control cases, and scoring discrimination.
- Read: `workspace/develop/eval/<bucket>/latest/report.html`
  - Confirms the canonical latest rendered report for each bucket.
- Create before each improvement try: `workspace/develop/lv_up_plan/<bucket>/analysis/YYYYMMDD-HHMMSS-tryNN-<topic>.md`
  - Records the evidence, root cause, and decision.
- Create before each improvement try: `workspace/develop/lv_up_plan/<bucket>/plan/YYYYMMDD-HHMMSS-tryNN-<topic>.md`
  - Records the exact change plan and verification commands.
- Modify only when justified by the analysis:
  - `dddjango/skills/**/SKILL.md`
  - `dddjango/skills/**/references/*.md`
  - `dddjango/skills/**/agents/openai.yaml`
  - `workspace/develop/eval/<bucket>/{eval_goal.md,cases,answer}`
  - `workspace/scripts/*.py`

## Operating Rules

- Do not harden the plugin from one isolated failure unless the failure is a hard gate, a safety issue, or a report/runtime blocker.
- Do not edit skill text from answer oracle wording. Use oracle results to identify the missing behavior, then write general procedural guidance.
- Do not weaken an oracle to make a run pass. If an oracle is wrong, document the oracle defect and fix the eval first.
- Do not tune only against the current public cases. Add or preserve blind/adjacent cases when a change could overfit.
- Do not use generated run artifacts as source files. Recreate `runs/**` and `latest/**` through the eval/render scripts.
- Do not start implementation before the matching `lv_up_plan/<bucket>/analysis` and `plan` files exist, except for report/runtime breakage that blocks reading the eval result.
- Keep each try scoped to one failure family.

## Current Snapshot: 2026-05-18

Latest full regression after `workflow` try02:

| Bucket | Latest run ID | Cases | With avg | Baseline avg | Delta | Hard gates | Reportability |
|---|---|---:|---:|---:|---:|---:|---|
| response | `20260518-131953-response-try02-full-sequential-fallback-mode` | 9 | 5.0 | 4.0 | +1.0 | 0 | reportable |
| code | `20260518-131953-code-try02-full-sequential-fallback-mode` | 8 | 5.0 | 4.0 | +1.0 | 0 | reportable |
| plugin | `20260518-131953-plugin-try02-full-sequential-fallback-mode` | 7 | 4.9 | 3.0 | +1.9 | 0 | reportable |
| runtime | `20260518-134330-runtime-try02-full-sequential-fallback-mode` | 7 | 4.7 | 3.3 | +1.4 | 0 | reportable |
| source | `20260518-135207-source-try02-full-sequential-fallback-mode` | 7 | 5.0 | 3.6 | +1.4 | 0 | reportable |
| workflow | `20260518-141550-workflow-try02-full-sequential-fallback-mode` | 13 | 5.0 | 3.9 | +1.1 | 0 | reportable |

Immediate try:

| Priority | Bucket | Case | Root cause | Action | lv_up_plan |
|---:|---|---|---|---|---|
| P0 | workflow | `case-workflow-sequential-fallback` | `procedure gap` | Require explicit sequential fallback non-execution reporting | `workspace/develop/lv_up_plan/workflow/{analysis,plan}/20260518-124155-try02-sequential-fallback-mode.md` |

Backlog discovered during review:

| Priority | Type | Finding | Next action |
|---:|---|---|---|
| P1 | `runtime/report gap` | Workflow report conclusion can say `0 fail` while blocked and hard-gated cases exist. | Fix renderer/evaluator summary separately. |
| P1 | `eval gap` | `case-workflow-parallel-ownership` acceptable modes may conflict with actual subagent unavailability. | Align oracle and execution gate semantics. |
| P1 | `eval quality` | Source bucket lacks seeded conflict/provenance fixtures, reducing oracle discrimination. | Add deterministic source fixtures and expected rows. |
| P2 | `eval quality` | Some plugin/runtime/source oracles lack concrete validation commands and expected artifacts. | Add command/artifact expectations without leaking oracle text. |
| P2 | `overfit risk` | Several no-delta control cases pass equally under baseline and with-dddjango. | Confirm they are intentional no-harm controls or add adjacent cases. |

## Cycle Checklist

### Task 1: Preflight The Eval System

**Files:**
- Read: `Makefile`
- Read: `workspace/scripts/validate_eval_bucket_pack.py`
- Read: `workspace/scripts/render_eval_review_html.py`
- Read: `workspace/develop/eval/*/latest/report.html`

- [ ] **Step 1: Confirm the working tree is safe**

Run:

```bash
git status --short
```

Expected: either clean output, or only changes that are part of the current try and understood before continuing.

- [ ] **Step 2: Validate the eval pack**

Run:

```bash
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected:

```text
eval bucket pack validation passed: response=9, code=8, plugin=7, runtime=7, source=7, workflow=13
```

If this fails, stop plugin hardening and fix the eval pack first.

- [ ] **Step 3: Refresh latest report aliases**

Run:

```bash
.venv/bin/python workspace/scripts/render_eval_review_html.py --refresh-latest
```

Expected: each bucket has `workspace/develop/eval/<bucket>/latest/report.html`.

- [ ] **Step 4: Verify category navigation is never disabled**

Run:

```bash
.venv/bin/python -c 'import pathlib,re
root=pathlib.Path("workspace/develop/eval")
for bucket in ("response","code","plugin","runtime","source","workflow"):
    alias=root/bucket/"latest/report.html"
    text=alias.read_text(encoding="utf-8")
    m=re.search(r"""url=([^"]+)""", text)
    report=(alias.parent/m.group(1)).resolve() if m else alias.resolve()
    html=report.read_text(encoding="utf-8")
    links=re.findall(r"""<a class="bucket-tab[^"]*" href="([^"]+)"[^>]*>([^<]+)</a>""", html)
    disabled=re.findall(r"is-disabled", html)
    latest_links=[label for href,label in links if "latest/report.html" in href]
    print(f"{bucket}: links={len(links)} latest_links={len(latest_links)} disabled={len(disabled)}")
'
```

Expected:

```text
response: links=6 latest_links=6 disabled=0
code: links=6 latest_links=6 disabled=0
plugin: links=6 latest_links=6 disabled=0
runtime: links=6 latest_links=6 disabled=0
source: links=6 latest_links=6 disabled=0
workflow: links=6 latest_links=6 disabled=0
```

If any bucket fails this check, stop plugin hardening and fix the report renderer or latest alias logic first.

### Task 2: Capture The Current Latest Baseline

**Files:**
- Read: `workspace/develop/eval/<bucket>/latest/report.html`
- Read: `workspace/develop/eval/<bucket>/runs/<run-id>/RUN_META.json`
- Read: `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html`

- [ ] **Step 1: Start or reuse the local report server**

Run only if port `8765` is not already serving the eval directory:

```bash
.venv/bin/python -m http.server 8765 --directory workspace/develop/eval
```

Expected browser entrypoint:

```text
http://127.0.0.1:8765/plugin/latest/report.html
```

- [ ] **Step 2: Record latest run identity for all buckets**

Fill this table from each latest report and `RUN_META.json`:

| Bucket | Latest run ID | Try | Scope | Topic | Cases | Pass | Partial | Fail | Blocked | Avg | Hard-gate failures |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| response |  |  |  |  |  |  |  |  |  |  |  |
| code |  |  |  |  |  |  |  |  |  |  |  |
| plugin |  |  |  |  |  |  |  |  |  |  |  |
| runtime |  |  |  |  |  |  |  |  |  |  |  |
| source |  |  |  |  |  |  |  |  |  |  |  |
| workflow |  |  |  |  |  |  |  |  |  |  |  |

- [ ] **Step 3: Mark reportability blockers**

For each bucket, answer:

| Bucket | Latest alias works | Six category links work | Report has oracle output | Report has raw response links | Blocker |
|---|---|---|---|---|---|
| response |  |  |  |  |  |
| code |  |  |  |  |  |
| plugin |  |  |  |  |  |
| runtime |  |  |  |  |  |
| source |  |  |  |  |  |
| workflow |  |  |  |  |  |

If any blocker exists, classify it as `runtime/report gap` and fix it before evaluating plugin value.

### Task 3: Review Eval Quality Before Plugin Quality

**Files:**
- Read: `workspace/develop/eval/<bucket>/eval_goal.md`
- Read: `workspace/develop/eval/<bucket>/cases/plugin/public/*.md`
- Read: `workspace/develop/eval/<bucket>/answer/*.yaml`

- [ ] **Step 1: Check goal alignment**

For each bucket, record whether the cases collectively test the goal:

| Bucket | Goal is clear | Cases cover goal | Missing capability area | Notes |
|---|---|---|---|---|
| response |  |  |  |  |
| code |  |  |  |  |
| plugin |  |  |  |  |
| runtime |  |  |  |  |
| source |  |  |  |  |
| workflow |  |  |  |  |

- [ ] **Step 2: Check oracle discrimination**

For each answer oracle, verify it has all of:

```text
hard_gates
control_case
expected_outcomes
score guidance or equivalent verdict criteria
```

Record weak oracle findings:

| Bucket | Case | Weakness | Why it could mis-score | Fix eval before plugin? |
|---|---|---|---|---|
|  |  |  |  |  |

- [ ] **Step 3: Check leakage resistance**

For each public case, confirm it does not expose answer-only criteria:

```bash
rg -n "hard_gates|expected_outcomes|control_case|answer oracle|oracle" workspace/develop/eval/*/cases/plugin/public
```

Expected: no public case leaks oracle-only structure or answer criteria.

- [ ] **Step 4: Decide eval-first versus plugin-first**

Use this rule:

| Finding | Next action |
|---|---|
| Oracle is vague, too permissive, or leaks into public case | Fix eval first |
| Public cases do not cover `eval_goal.md` | Add or revise cases first |
| Report/latest/category navigation is broken | Fix runtime/report first |
| Eval is credible and plugin still underperforms | Harden plugin |

### Task 4: Measure Plugin Value Delta

**Files:**
- Read: `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html`
- Read: raw response/evaluation JSON files linked from the report

- [ ] **Step 1: Compare `with-dddjango` against baseline**

For every non-passing case, record:

| Bucket | Case | Baseline score | With-dddjango score | Direction | Hard gate failed | Evidence |
|---|---|---:|---:|---|---|---|
|  |  |  |  |  |  |  |

- [ ] **Step 2: Identify no-value cases**

Mark cases where `with-dddjango` is not meaningfully better than baseline:

| Bucket | Case | Expected plugin value | Actual behavior | Suspected reason |
|---|---|---|---|---|
|  |  |  |  |  |

- [ ] **Step 3: Identify overfit or accidental pass cases**

Mark cases where the output passes but the reasoning is brittle:

| Bucket | Case | Passing score | Fragile behavior | Needs adjacent case? |
|---|---|---:|---|---|
|  |  |  |  |  |

### Task 5: Classify Root Causes

**Files:**
- Read: affected `SKILL.md`
- Read: affected `references/*.md`
- Read: affected `agents/openai.yaml`
- Read: affected eval cases and answers

- [ ] **Step 1: Assign exactly one primary root cause per finding**

Use this taxonomy:

| Root cause | Meaning | Typical fix |
|---|---|---|
| `trigger failure` | Correct skill did not load | Tighten frontmatter description or metadata |
| `routing failure` | Wrong skill loaded or similar skills confused selection | Clarify trigger boundaries across skills |
| `procedure gap` | Skill loaded but did not instruct the needed workflow | Add concise procedural step to `SKILL.md` |
| `reference gap` | Needed domain/project fact was missing or hard to find | Add or reorganize `references/*.md` |
| `script/tool gap` | Repeated fragile work should be deterministic | Add or update script and tests |
| `eval gap` | Case/oracle does not measure the intended behavior | Fix eval goal, case, or oracle |
| `runtime/report gap` | Harness, latest, report, or navigation is broken | Fix `workspace/scripts` or Makefile |
| `overfit risk` | Current public cases can be gamed | Add adjacent/blind case before tuning |

Record findings:

| Bucket | Case | Root cause | Confidence | Evidence path | Next action |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

- [ ] **Step 2: Escalate only repeated or severe findings**

Use this decision rule:

| Pattern | Priority |
|---|---|
| Safety, leakage, false claim, or hard-gate failure | P0 |
| Same root cause appears in two or more cases | P1 |
| One case blocks a bucket goal | P1 |
| One isolated partial with no repeated pattern | P2 |
| Cosmetic or wording-only issue with passing behavior | P3 |

### Task 6: Write The lv-up Analysis And Plan

**Files:**
- Create: `workspace/develop/lv_up_plan/<bucket>/analysis/YYYYMMDD-HHMMSS-tryNN-<topic>.md`
- Create: `workspace/develop/lv_up_plan/<bucket>/plan/YYYYMMDD-HHMMSS-tryNN-<topic>.md`

- [ ] **Step 1: Create the analysis document before editing source**

Use this exact structure:

```markdown
# <bucket> tryNN <topic> Analysis

## Evidence

- Latest run: `<run-id>`
- Report: `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/report.html`
- Cases reviewed:
  - `<case-id>`: `<score/verdict and hard-gate result>`

## Root Cause

- Primary root cause: `<trigger failure | routing failure | procedure gap | reference gap | script/tool gap | eval gap | runtime/report gap | overfit risk>`
- Why this is not an eval-only artifact: `<evidence>`
- Why this is not a one-off: `<repeat pattern or hard-gate severity>`

## Decision

- Action: `<harden plugin | fix eval | fix runtime/report | add adjacent case | no change>`
- Target files:
  - `<path>`
- Non-goals:
  - `<what not to change>`
```

- [ ] **Step 2: Create the implementation plan document before editing source**

Use this exact structure:

```markdown
# <bucket> tryNN <topic> Plan

## Scope

- Change type: `<skill | reference | metadata | script | eval | report>`
- Target files:
  - `<path>`
- Expected behavior after change:
  - `<observable behavior>`

## Steps

- [ ] Add or update focused test/validator coverage when the change touches scripts or eval contracts.
- [ ] Make the smallest source change that addresses the documented root cause.
- [ ] Run deterministic validation.
- [ ] Run targeted eval for the affected bucket or case.
- [ ] Refresh latest reports.
- [ ] Record result in a review note if the change affects plugin value.

## Verification Commands

```bash
.venv/bin/python -m unittest discover -s workspace/scripts -p 'test_*.py'
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
.venv/bin/python workspace/scripts/render_eval_review_html.py --refresh-latest
```
```

### Task 7: Implement The Smallest Justified Change

**Files:**
- Modify only the files listed in the matching lv-up plan.

- [ ] **Step 1: For script or report changes, write the failing test first**

Expected test command pattern:

```bash
.venv/bin/python -m unittest workspace/scripts/test_<target>.py
```

Expected before implementation: the new test fails for the documented reason.

- [ ] **Step 2: For skill or reference changes, keep SKILL.md concise**

Check:

```bash
wc -l dddjango/skills/<skill>/SKILL.md
```

Expected: `SKILL.md` stays focused. If it approaches excessive length, move detailed material to `references/*.md` and link it from `SKILL.md`.

- [ ] **Step 3: For metadata changes, keep trigger boundaries explicit**

Inspect:

```bash
sed -n '1,120p' dddjango/skills/<skill>/agents/openai.yaml
```

Expected: `short_description` and `default_prompt` match the updated `SKILL.md` behavior without broadening the skill into unrelated tasks.

- [ ] **Step 4: For eval changes, validate no oracle leakage**

Run:

```bash
rg -n "hard_gates|expected_outcomes|control_case|answer oracle|oracle" workspace/develop/eval/*/cases/plugin/public
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected: public cases do not leak oracle criteria, and pack validation passes.

### Task 8: Verify The Change

**Files:**
- Read: affected latest report
- Read: affected run `RUN_META.json`
- Read: affected raw response and oracle evaluation files

- [ ] **Step 1: Run deterministic tests**

Run:

```bash
.venv/bin/python -m unittest discover -s workspace/scripts -p 'test_*.py'
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected: all tests pass and eval bucket pack validation passes.

- [ ] **Step 2: Run targeted eval first**

Use the existing Makefile target or runner for the affected bucket:

```bash
make eval-one BUCKET=<bucket>
```

Expected: a new canonical run under `workspace/develop/eval/<bucket>/runs/YYYYMMDD-HHMMSS-<bucket>-tryNN-<scope>-<topic>`.

- [ ] **Step 3: Refresh latest reports**

Run:

```bash
.venv/bin/python workspace/scripts/render_eval_review_html.py --refresh-latest
```

Expected: the affected bucket `latest/report.html` points to the new valid scored run.

- [ ] **Step 4: Recheck value delta**

Record:

| Bucket | Case | Before score | After score | Hard gate before | Hard gate after | Decision |
|---|---|---:|---:|---|---|---|
|  |  |  |  |  |  |  |

If the targeted eval improves by weakening behavior, revert the change and fix the plan.

### Task 9: Run Full Regression When Needed

**Files:**
- Read: `Makefile`
- Read: `workspace/develop/eval/*/latest/report.html`

- [ ] **Step 1: Decide whether full eval is required**

Run full eval when any of these are true:

| Condition | Full eval required |
|---|---|
| Skill frontmatter or trigger metadata changed | Yes |
| Shared workflow/source/runtime behavior changed | Yes |
| Eval report/latest selection changed | Yes |
| Only one narrow answer oracle changed | No, targeted plus pack validation is enough |
| Only documentation analysis/plan changed | No |

- [ ] **Step 2: Run full eval**

Run:

```bash
make eval-all
```

Expected: all six buckets produce current latest reports, and `--refresh-latest` runs after the bucket evals.

- [ ] **Step 3: Inspect the report in the browser**

Open:

```text
http://127.0.0.1:8765/plugin/latest/report.html
```

Click every category tab:

```text
plugin -> response -> code -> runtime -> source -> workflow
```

Expected: every tab navigates to `/<bucket>/latest/report.html` and lands on the latest valid report.

### Task 10: Close The Try

**Files:**
- Create when useful: `workspace/develop/lv_up_plan/<bucket>/review/YYYYMMDD-HHMMSS-tryNN-<kind>.md`
- Read: `git diff`
- Read: `git status --short`

- [ ] **Step 1: Write a review note for non-trivial changes**

Use this structure:

```markdown
# <bucket> tryNN <topic> Review

## Result

- Targeted eval: `<pass | partial | fail | blocked>`
- Full eval: `<not run | pass | partial | fail | blocked>`
- Latest report: `<path or URL>`

## What Improved

- `<case or behavior>`

## Remaining Risk

- `<risk>`

## Next Candidate

- `<next bucket/root cause or no immediate follow-up>`
```

- [ ] **Step 2: Verify final state before commit**

Run:

```bash
git diff --check
.venv/bin/python -m unittest discover -s workspace/scripts -p 'test_*.py'
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
git status --short
```

Expected: whitespace check passes, deterministic tests pass, pack validation passes, and only intended files are modified.

- [ ] **Step 3: Commit the try**

Run:

```bash
git add <intended-files>
git commit -m "<type>: <concise eval-driven hardening summary>"
```

Expected: the commit contains the source/eval change plus the matching lv-up analysis and plan documents.

## Decision Matrix

Use this table to decide the next move after every full eval:

| Observation | Interpretation | Next move |
|---|---|---|
| All buckets pass, with-dddjango clearly beats baseline, no hard-gate failures | Plugin is currently strong enough | Stop hardening; monitor future regressions |
| All buckets pass, but with-dddjango barely differs from baseline | Eval may be too weak or plugin value is not visible | Add discriminating adjacent cases before plugin changes |
| One bucket has repeated hard-gate failure | Real gap or strict oracle | Review oracle first, then harden one failure family |
| Runtime/report/latest is broken | Result is not decision-grade | Fix harness before plugin work |
| Public cases leak answer criteria | Eval contaminated | Fix eval cases and rerun |
| Skill is triggered but behavior is shallow | Procedure gap | Tighten `SKILL.md` with concise operational steps |
| Correct behavior requires project-specific facts | Reference gap | Add or reorganize `references/*.md` |
| Same fragile command or parsing appears repeatedly | Script/tool gap | Add deterministic script and tests |
| Failures only happen in broad composite tasks | Workflow gap | Strengthen workflow skill or subagent handoff contract |

## Definition Of Done

- [ ] Latest reports for all six buckets are reachable from `/<bucket>/latest/report.html`.
- [ ] Every latest report has six clickable category tabs and zero disabled category tabs.
- [ ] Eval pack validation passes.
- [ ] The current decision is based on `eval_goal.md`, public cases, answer oracles, raw outputs, and rendered reports.
- [ ] Every non-trivial plugin change has matching `lv_up_plan` analysis and plan documents.
- [ ] Each improvement try targets one failure family.
- [ ] The final review says whether the plugin needs more hardening, the eval needs hardening, or no immediate change is justified.
