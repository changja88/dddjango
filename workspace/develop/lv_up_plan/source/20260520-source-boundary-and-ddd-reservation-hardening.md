# Source Boundary And DDD Reservation Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first-class source-reference-audit source reference, align the boundary-protection eval contract with it, and harden the reservation aggregate boundary eval so public mutable aggregate state is caught.

**Architecture:** Keep source decisions in `workspace/reference/**`, keep runtime skills concise, and keep case-specific enforcement in eval answer files and hidden behavior checks. Do not copy private oracle wording into runtime/public skill text.

**Tech Stack:** Markdown source references, dddjango skill Markdown, YAML eval answer packs, Python AST/runtime behavior checks, `unittest`, existing eval validators.

---

## File Map

- Create: `workspace/reference/source-reference-audit/reference/final.md`
  - Dedicated source-of-truth for source/runtime/public/private/run boundary decisions.
- Modify: `workspace/docs/reference-index.md`
  - Register source-reference-audit as a first-class reference area.
- Modify: `dddjango/skills/source-reference-audit/SKILL.md`
  - Point source loading to the new source reference while keeping runtime-facing path restrictions.
- Modify: `dddjango/skills/source-reference-audit/agents/openai.yaml`
  - Keep UI metadata aligned with the tightened boundary/leakage scope if needed.
- Modify: `workspace/develop/eval/source/cases/plugin/public/case-source-boundary-protection.md`
  - Clarify that the answer should distinguish inspected and not-run surfaces without leaking private evaluator material.
- Modify: `workspace/develop/eval/source/answer/case-source-boundary-protection.yaml`
  - Use the new source reference as primary basis and align evidence requirements.
- Modify: `dddjango/skills/architecture-ddd/SKILL.md`
  - Add general aggregate-owned state protection guidance.
- Modify: `workspace/docs/ddd-implementation-standard.md`
  - Add a source-level general rule for externally mutable aggregate state.
- Modify: `workspace/develop/eval/code/answer/case-code-ddd-reservation-boundary.yaml`
  - Align oracle wording with aggregate state protection and fixture restraint.
- Modify: `workspace/scripts/eval_code_behavior_checks.py`
  - Harden reservation hidden checks with AST checks and runtime mutation checks.
- Create: `workspace/scripts/test_eval_code_behavior_checks.py`
  - Regression tests for public mutable `Reservation.status`, private read-only status, and service direct mutation.

---

## Task 1: Source Reference Audit Source

- [x] **Step 1: Create `workspace/reference/source-reference-audit/reference/final.md`**
  - Include role boundary matrix, path boundary matrix, leakage categories, run artifact status, boundary scan evidence contract, and public wording rules.
  - Keep it source-facing; do not phrase workspace paths as runtime-facing allowed refs.

- [x] **Step 2: Update `workspace/docs/reference-index.md`**
  - Add Source Reference Audit under a governance/source section.
  - State it covers source provenance, source/runtime split, leakage boundaries, eval traceability, validation coverage, and boundary scan evidence.

- [x] **Step 3: Update `dddjango/skills/source-reference-audit/SKILL.md`**
  - In Source Loading, instruct agents to read the dedicated final reference for source-boundary and leakage reviews.
  - Preserve existing Runtime-Facing Path Boundary wording.

- [x] **Step 4: Run docs validation**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_validate_skill_docs.py`
  - Expected: all tests pass.
  - Result: `Ran 20 tests in 0.057s`, `OK`.

## Task 2: Source Boundary Eval Contract

- [x] **Step 1: Update public prompt**
  - Clarify artifact/surface distinction, inspected vs not-run reporting, public-facing categories, and source/runtime path context split.

- [x] **Step 2: Update answer YAML**
  - Make `workspace/reference/source-reference-audit/reference/final.md` the primary reference basis.
  - Replace ambiguous `boundary scan report` evidence with concrete evidence: boundary matrix, inspected surfaces list, forbidden-category scan or explicit not-run, source/runtime path decision, unsupported execution claim check.
  - Update required/forbidden behavior to prohibit prior run output as source truth and workspace source paths as runtime-facing allowed refs.

- [x] **Step 3: Validate source bucket pack**
  - Command: `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source`
  - Expected: validation passes.
  - Result: `eval bucket pack validation passed: source=7`.

## Task 3: DDD Aggregate Boundary Guidance

- [x] **Step 1: Update runtime DDD skill**
  - Add general guidance that aggregate-owned lifecycle state must not be externally mutable and must change through aggregate behavior.
  - Add neighboring availability/inventory context guidance as boundary call/event handoff, not aggregate child.
  - Keep fixture restraint explicit.

- [x] **Step 2: Update DDD implementation standard**
  - Add the same principle at source level without reservation-specific terms.

- [x] **Step 3: Update reservation answer YAML**
  - Clarify supporting context with high-risk lifecycle invariants.
  - Require service not to assign `status`/`_status` directly, including `setattr`.
  - Require aggregate invariant tests and service use-case tests.

- [x] **Step 4: Run docs validation**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_validate_skill_docs.py`
  - Expected: all tests pass.
  - Result: `Ran 20 tests in 0.061s`, `OK`; code bucket pack also passed with `code=10`.

## Task 4: Reservation Hidden Behavior Checks

- [x] **Step 1: Add failing tests**
  - Create `workspace/scripts/test_eval_code_behavior_checks.py`.
  - Test that public mutable `Reservation.status` fails.
  - Test that private `_status` plus read-only `status` property passes.
  - Test that service direct `status`/`_status` assignment or `setattr` fails.

- [x] **Step 2: Verify RED**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_eval_code_behavior_checks.py`
  - Expected: at least the public mutable status and service `setattr` tests fail before implementation.
  - Result: RED confirmed with failures for public mutable status and service mutation detection after fixing a test fixture indentation error.

- [x] **Step 3: Harden `workspace/scripts/eval_code_behavior_checks.py`**
  - Add AST helpers for `status`/`_status` assignment detection.
  - Add runtime check that external `reservation.status = ...` cannot silently mutate lifecycle state.
  - Add direct aggregate transition checks independent of service orchestration.
  - Keep small fixture support and avoid requiring repository/UoW/outbox.

- [x] **Step 4: Verify GREEN**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_eval_code_behavior_checks.py`
  - Expected: all tests pass.
  - Result: `Ran 3 tests in 0.021s`, `OK`.

- [x] **Step 5: Run adjacent unit tests**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_validate_eval_bucket_pack.py workspace/scripts/test_validate_skill_docs.py`
  - Expected: all tests pass.
  - Result: `Ran 39 tests in 0.162s`, `OK`; source/code bucket pack validation also passed.

## Task 5: Final Verification

- [x] **Step 1: Validate skill docs**
  - Command: `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --runtime-skills /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills`
  - Expected: validation passes with 0 warnings.
  - Result: initially failed due runtime cache/source parity for three changed skill files; synced cache and reran successfully with `OK: validation passed with 0 warning(s)`.

- [x] **Step 2: Validate source/code eval packs**
  - Command: `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source --bucket code`
  - Expected: validation passes.
  - Result: `eval bucket pack validation passed: source=7, code=10`.

- [x] **Step 3: Run focused script tests**
  - Command: `.venv/bin/python -m unittest workspace/scripts/test_eval_code_behavior_checks.py workspace/scripts/test_validate_eval_bucket_pack.py workspace/scripts/test_validate_skill_docs.py`
  - Expected: all tests pass.
  - Result: `Ran 39 tests in 0.157s`, `OK`.

- [x] **Step 4: Optional targeted evals**
  - Source: `make eval-one BUCKET=source CASE=case-source-boundary-protection TRY_NUMBER=1 SCOPE=targeted TOPIC=source-boundary-reference-hardening EXTRA_ARGS=--rerun JOBS=1`
  - Code: `make eval-one BUCKET=code CASE=case-code-ddd-reservation-boundary TRY_NUMBER=1 SCOPE=targeted TOPIC=ddd-reservation-boundary-hardening EXTRA_ARGS=--rerun JOBS=1`
  - Expected: both pass; run only after local validators pass.
  - Result: source targeted eval was attempted in the sandbox and failed before scoring because Codex app-server client initialization returned `Operation not permitted`. Unsandboxed rerun was rejected by approval review because eval-one may invoke external model/evaluator execution over private eval artifacts. No workaround attempted.
  - User-run result: source targeted eval passed as `source/20260520-214835-source-try01-targeted-source-boundary-reference-hardening`; oracle scored baseline `4 / 5 partial`, with-dddjango `5 / 5 pass`; `RUN_VALIDATION.status=passed`.
  - User-run result: code targeted eval passed as `code/20260520-214838-code-try01-targeted-ddd-reservation-boundary-hardening`; oracle scored baseline `3 / 5 partial`, with-dddjango `5 / 5 pass`; `RUN_VALIDATION.status=passed`.

---

## Progress Log

- 2026-05-20: Plan created from latest full eval regressions, local artifact review, and three read-only explorer agent recommendations.
- 2026-05-20: Completed source-reference-audit source reference, source eval contract alignment, and source bucket validation.
- 2026-05-20: Completed DDD aggregate state guidance and reservation answer oracle wording alignment; docs and code bucket pack validation passed.
- 2026-05-20: Completed reservation hidden behavior check hardening. Latest captured baseline artifact passes the new check; latest captured with-dddjango artifact fails with `Reservation lifecycle status must not be externally mutable`, matching the reviewed regression.
- 2026-05-20: Synced changed runtime skill files into the local dddjango plugin cache and completed local validators.
- 2026-05-20: Attempted source targeted eval; blocked before scoring by sandbox/app-server permissions, and unsandboxed rerun was not allowed by approval review.
- 2026-05-20: User ran targeted source/code evals successfully. Both targeted runs passed validation and with-dddjango scored `5 / 5 pass` in the two regression cases.
