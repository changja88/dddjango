# Code Eval DDD Quality Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `code` eval bucket prove whether `dddjango` produces DDD-shaped Django/Python code according to the repository references, instead of only proving that code artifacts and broad implementation checks exist.

**Architecture:** Keep public `cases` as user-visible task prompts, private `answer` files as evaluator-only scoring authority, fixtures as deliberately imperfect starter workspaces, and Python validators as deterministic hard gates. The plan first upgrades validator gates so weak artifacts cannot score as passing, then tightens existing cases, then adds focused DDD cases that exercise strategic-to-tactical mapping.

**Tech Stack:** Markdown eval packs under `workspace/develop/eval/code`, fixture repos under `workspace/develop/eval/code/fixtures`, Python stdlib validators and runners under `workspace/scripts`, unittest-based script tests, `make eval-all`, and rendered reports under `workspace/develop/eval/code/runs`.

---

## File Structure

- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
  - Enforce `code_expected`, `allowed_paths`, `forbidden_paths`, generated artifact hygiene, and deterministic check evidence.
- Modify: `workspace/scripts/test_validate_eval_code_artifacts.py`
  - Add regression tests proving the new hard gates fail on the current weak spots.
- Create: `workspace/scripts/eval_answer_yaml.py`
  - Provide a restricted, deterministic parser for the answer YAML shapes used by eval validators. Do not add a new dependency unless the project already has one.
- Create: `workspace/scripts/test_eval_answer_yaml.py`
  - Lock scalar, list, list-of-map, and nested-block parsing behavior used by validators.
- Modify: `workspace/scripts/run_initial_eval.py`
  - Ensure the stronger code artifact validator runs in the normal `make eval-one`, `make eval-bucket`, and `make eval-all` path.
- Modify: `workspace/scripts/test_run_initial_eval.py` or the existing runner pipeline tests
  - Prove code bucket validation invokes the hard artifact validator.
- Modify: `workspace/scripts/validate_eval_bucket_pack.py`
  - Require `case_role`, DDD reference linkage, and `ddd_observations` for code cases marked `case_role: ddd_direct`.
- Modify: `workspace/scripts/test_validate_eval_bucket_pack.py`
  - Add schema tests for code DDD oracle fields.
- Modify: `workspace/develop/eval/code/eval_goal.md`
  - Clarify that DDD-shaped code confidence is separate from control/restraint score.
- Modify: `workspace/develop/eval/code/answer/*.yaml`
  - Split code cases into `ddd_direct`, `implementation_supporting`, and `control` roles.
  - Add `ddd_observations` only where the case is supposed to prove DDD behavior.
- Modify: `workspace/develop/eval/code/cases/plugin/public/*.md`
  - Tighten prompts where the current task is too broad or already solved.
- Modify: `workspace/develop/eval/code/cases/plugin/code-capture.json`
  - Register any new DDD cases and their subject fixture repos.
- Modify: `workspace/develop/eval/code/fixtures/django_shop_service/**`
  - Make `case-code-order-api` a real API/DB consistency starter gap instead of an already mostly-correct implementation.
- Create: `workspace/develop/eval/code/cases/plugin/public/case-code-ddd-order-placement.md`
  - Direct DDD-to-code implementation case.
- Create: `workspace/develop/eval/code/answer/case-code-ddd-order-placement.yaml`
  - Private oracle requiring bounded context, aggregate, invariant, application service, transaction, API, and tests.
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/**`
  - Small pure-Python DDD fixture with deliberately misplaced domain rules. This proves tactical aggregate/application-service shape, not full Django ORM mapping.

## Current Problems To Preserve As Regression Tests

- `case-code-order-api` with-ddjango generated `db.sqlite3` outside the oracle allowed paths but still scored 5/5.
- `code_expected: false` currently allows a non-empty production diff unless the LLM evaluator catches it.
- `allowed_paths` and `forbidden_paths` are present in answer YAML but not enforced by `validate_eval_code_artifacts.py`.
- DDD reference compliance is named in `code/eval_goal.md` but direct code answer files do not require `workspace/reference/architecture-ddd/reference/final.md`.
- `case-code-order-api` fixture already has request fingerprint, transaction, `select_for_update`, unique idempotency key, replay/conflict tests, so the case is not discriminative enough.
- Control cases such as small rename and clarify-external can score 5/5 but should not increase DDD-shaped implementation confidence.

## Agent Review Decisions Incorporated

- Use `case_role: ddd_direct` as the only deterministic trigger for DDD observation requirements. Do not trigger DDD hard gates from `domain-policy`, because supporting cases such as coupon TDD legitimately use that tag without proving bounded context or aggregate shape.
- Treat `case-code-order-api` as API/DB consistency support, not direct DDD proof. Direct DDD confidence comes from dedicated aggregate/application-service cases.
- Integrate hard artifact validation into the normal `make eval-*` pipeline, not only as a manual standalone command.
- Validate answer YAML through structured restricted parsing of the known eval schema, not by checking whether reference paths appear anywhere in raw text.
- Run evaluator-owned behavior checks from repo root with `--workspace <isolated subject workspace>` appended by the runner. Never copy hidden check scripts into public fixtures or prompt inputs.
- Behavior checks for DDD direct cases must include source-shape checks such as aggregate behavior methods and service direct-state-mutation bans, not only final state assertions.

## Task 1: Add Deterministic Code Artifact Hard Gates

**Files:**
- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
- Modify: `workspace/scripts/test_validate_eval_code_artifacts.py`

- [x] **Step 1: Add failing tests for path policy**

First extend the test helper so tests can write `code_expected: false` without duplicating the field:

```python
    def write_answer(self, *, code_expected: bool = True, checks: str | None = None) -> None:
        ...
        expected_text = "true" if code_expected else "false"
        reason_text = "" if code_expected else "code_expected_reason: missing external integration contract\n"
        (self.answer_dir / f"{CASE_ID}.yaml").write_text(
            f"id: {CASE_ID}\n"
            f"case_id: {CASE_ID}\n"
            "bucket: code\n"
            "kind: code\n"
            f"code_expected: {expected_text}\n"
            f"{reason_text}"
            f"{checks_text}",
            encoding="utf-8",
        )
```

Then add these tests to `ValidateEvalCodeArtifactsTests`:

```python
    def test_forbidden_path_in_manifest_fails(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/**\n"
            "forbidden_paths:\n"
            "  - db.sqlite3\n"
        )
        self.write_variant_artifacts("with-dddjango")
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "db.sqlite3"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "forbidden path changed: db.sqlite3"):
            self.validator.main(self.validator_argv())

    def test_path_outside_allowed_paths_fails(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/orders/**\n"
            "forbidden_paths:\n"
            "  - workspace/develop/eval/**\n"
        )

        with self.assertRaisesRegex(AssertionError, "changed path is not allowed: app.py"):
            self.validator.main(self.validator_argv())

    def test_generated_artifact_fails_even_without_forbidden_paths(self) -> None:
        self.write_answer(
            checks="deterministic_checks: []\n"
            "allowed_paths:\n"
            "  - apps/**\n"
            "forbidden_paths: []\n"
        )
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"][0]["path"] = "db.sqlite3"
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "generated artifact changed: db.sqlite3"):
            self.validator.main(self.validator_argv())

    def test_code_expected_false_forbids_code_changes(self) -> None:
        self.write_answer(
            code_expected=False,
            checks="deterministic_checks: []\n"
            "allowed_paths: []\n"
            "forbidden_paths:\n"
            "  - apps/**\n"
        )

        with self.assertRaisesRegex(AssertionError, "code_expected=false forbids code changes"):
            self.validator.main(self.validator_argv())

    def test_no_code_produced_requires_empty_files(self) -> None:
        self.write_answer(
            code_expected=False,
            checks="deterministic_checks: []\n"
            "allowed_paths: []\n"
            "forbidden_paths:\n"
            "  - apps/**\n"
        )
        manifest_path = (
            self.run_dir
            / "code"
            / CASE_ID
            / "with-dddjango"
            / "changed-files.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["noCodeProduced"] = True
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(AssertionError, "noCodeProduced=true requires empty files"):
            self.validator.main(self.validator_argv())
```

- [x] **Step 2: Run the failing tests**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_code_artifacts.py
```

Expected: the new tests fail because `validate_eval_code_artifacts.py` does not parse or enforce path policy, generated artifact hygiene, or no-code policy yet.

- [x] **Step 3: Add a restricted answer YAML parser**

Do not depend on substring checks for core policy. Create `workspace/scripts/eval_answer_yaml.py` with restricted parsers for the answer YAML shapes this repo already uses. The parser does not need full YAML coverage, but it must return structured values for scalar fields, list fields, list-of-map fields such as `reference_basis`, and nested mapping/list fields such as `ddd_observations`.

```python
def scalar_value(text: str, key: str) -> str | None:
    ...


def list_values(text: str, key: str) -> list[str]:
    ...


def list_of_maps(text: str, key: str) -> list[dict[str, str]]:
    ...


def nested_keys(text: str, key: str) -> set[str]:
    ...
```

Add `workspace/scripts/test_eval_answer_yaml.py` with examples for:

```yaml
allowed_paths:
  - apps/orders/**
reference_basis:
  - path: workspace/docs/ddd-implementation-standard.md
    basis: DDD implementation order
ddd_observations:
  aggregate_root: Order
  invariants:
    - An order cannot be placed without items.
```

Expected: parser tests pass before wiring the parser into validators.

- [x] **Step 4: Enforce `allowed_paths` and `forbidden_paths`**

Change `validate_manifest` signature to accept the answer text:

```python
def validate_manifest(
    run_dir: Path,
    case_id: str,
    variant: str,
    *,
    answer_text: str,
    code_expected: bool,
) -> None:
```

After loading `files`, compute:

```python
allowed_paths = eval_answer_yaml.list_values(answer_text, "allowed_paths")
forbidden_paths = eval_answer_yaml.list_values(answer_text, "forbidden_paths")
changed_paths = [
    str(entry.get("path") or "")
    for entry in files
    if isinstance(entry, dict)
]
for changed_path in changed_paths:
    if any(path_matches(pattern, changed_path) for pattern in forbidden_paths):
        raise AssertionError(f"{case_id} {variant} forbidden path changed: {changed_path}")
    if allowed_paths and not any(path_matches(pattern, changed_path) for pattern in allowed_paths):
        raise AssertionError(f"{case_id} {variant} changed path is not allowed: {changed_path}")
```

- [x] **Step 5: Add hard generated-artifact denylist**

Add a constant:

```python
GENERATED_ARTIFACT_PATTERNS = (
    "*.sqlite3",
    "db.sqlite3",
    "**/__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
)
```

Then reject these paths before allowed-path checks:

```python
for changed_path in changed_paths:
    if any(path_matches(pattern, changed_path) for pattern in GENERATED_ARTIFACT_PATTERNS):
        raise AssertionError(f"{case_id} {variant} generated artifact changed: {changed_path}")
```

- [x] **Step 6: Enforce `code_expected: false`**

Replace the current `allow_no_code` boolean handling with:

```python
if manifest["noCodeProduced"]:
    if code_expected:
        raise AssertionError(f"{manifest_path} noCodeProduced=true is not allowed for this case")
    if files:
        raise AssertionError(f"{manifest_path} noCodeProduced=true requires empty files")
    return
if not code_expected:
    raise AssertionError(f"{manifest_path} code_expected=false forbids code changes")
```

- [x] **Step 7: Update caller**

In `main`, calculate `code_expected = answer_code_expected(answer_text, case_id)`, then call:

```python
validate_manifest(
    run_dir,
    case_id,
    variant,
    answer_text=answer_text,
    code_expected=code_expected,
)
```

- [x] **Step 8: Verify deterministic hard gates**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_code_artifacts.py
```

Expected: all tests pass.

- [x] **Step 9: Verify current latest code run now exposes the known problem**

Run:

```bash
.venv/bin/python workspace/scripts/validate_eval_code_artifacts.py \
  --run-dir workspace/develop/eval/code/runs/20260518-131953-code-try02-full-sequential-fallback-mode \
  --metadata workspace/develop/eval/code/cases/plugin/code-capture.json \
  --variant baseline \
  --variant=with-dddjango \
  --case case-code-order-api
```

Expected: FAIL with `generated artifact changed: db.sqlite3` or `changed path is not allowed: db.sqlite3`. This confirms the new validator catches the previously over-generous 5/5 artifact.

## Task 2: Wire Hard Gates Into The Normal Eval Pipeline

**Files:**
- Modify: `workspace/scripts/run_initial_eval.py`
- Modify: `workspace/scripts/validate_eval_run.py` or reuse `workspace/scripts/validate_eval_code_artifacts.py`
- Modify: `workspace/scripts/test_validate_eval_run.py`
- Modify: `workspace/scripts/test_run_initial_eval.py` if present, otherwise the closest existing pipeline test file

- [x] **Step 1: Add failing pipeline-level test**

Add a test that builds a fake code run with `db.sqlite3` in `changed-files.json`, then invokes the same validation path used by `run_initial_eval.py`. The expected result must fail before implementation.

The assertion text should include:

```text
generated artifact changed: db.sqlite3
```

- [x] **Step 2: Choose one integration point**

Use one of these approaches, preferring the first if it keeps duplication low:

```text
Preferred: validate_eval_run.py imports validate_eval_code_artifacts and calls the hard code artifact validation for bucket == "code".
Fallback: run_initial_eval.py appends a standalone validate_eval_code_artifacts.py command after validate_eval_run.py for bucket == "code".
```

Do not leave the hard validator as an optional manual check only. `make eval-one BUCKET=code`, `make eval-bucket BUCKET=code`, and `make eval-all` must fail when code artifact hard gates fail.

- [x] **Step 3: Pass selected cases and variants**

The integrated validator must validate both variants for selected cases:

```text
--variant baseline --variant=with-dddjango
--case <case-id> for each selected case
```

If a full code bucket run has no explicit cases, resolve the public cases the same way existing eval scripts do.

- [x] **Step 4: Verify the known bad latest run fails through pipeline validation**

Run the integrated validation path against:

```text
workspace/develop/eval/code/runs/20260518-131953-code-try02-full-sequential-fallback-mode
```

Expected: FAIL because `case-code-order-api/with-dddjango` includes `db.sqlite3`.

- [x] **Step 5: Verify static tests**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_run.py
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_code_artifacts.py
```

Expected: all tests pass after the integrated hard gate is implemented.

## Task 3: Require DDD Oracle Shape For Direct DDD Code Cases

**Files:**
- Modify: `workspace/scripts/validate_eval_bucket_pack.py`
- Modify: `workspace/scripts/test_validate_eval_bucket_pack.py`
- Modify: `workspace/develop/eval/code/eval_goal.md`

- [x] **Step 1: Add failing pack-validator tests**

Add a test that writes a code answer with `case_role: ddd_direct` but no `ddd_observations`, and assert a validation finding:

```python
    def test_code_ddd_case_requires_ddd_observations(self) -> None:
        self.write_case_pair("code", "case-code-ddd", coverage_tags=["ddd-to-code"])
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-ddd.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("code_expected: true\n", "code_expected: true\ncase_role: ddd_direct\n")
        answer_path.write_text(text, encoding="utf-8")
        public_path = self.validator.EVAL_ROOT / "code/cases/plugin/public/case-code-ddd.md"

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(any("ddd_observations" in finding for finding in findings))
```

Add two more tests:

- missing `workspace/reference/architecture-ddd/reference/final.md` under `reference_basis[].path` fails when `case_role: ddd_direct`.
- missing `workspace/docs/ddd-implementation-standard.md` under `reference_basis[].path` fails when `case_role: ddd_direct`.

Also add a test proving `case_role: implementation_supporting` with `coverage_tags: [domain-policy]` does not require `ddd_observations`.

- [x] **Step 2: Run the failing tests**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_bucket_pack.py
```

Expected: new tests fail because the schema is not enforced yet.

- [x] **Step 3: Define required DDD observation fields**

Add to `validate_eval_bucket_pack.py`:

```python
CODE_CASE_ROLE_VALUES = {"ddd_direct", "implementation_supporting", "control"}
DDD_OBSERVATION_FIELDS = (
    "business_problem",
    "subdomain_type",
    "subdomain_type_basis",
    "bounded_context",
    "context_map_or_not_applicable",
    "ubiquitous_terms",
    "aggregate_root",
    "aggregate_behavior",
    "invariants",
    "application_service_boundary",
    "transaction_boundary",
    "django_mapping",
    "test_evidence",
)
DDD_REQUIRED_REFERENCE_PATHS = {
    "workspace/docs/ddd-implementation-standard.md",
    "workspace/reference/architecture-ddd/reference/final.md",
}
```

- [x] **Step 4: Validate DDD observation blocks**

Add:

```python
def validate_code_ddd_answer(path: Path, text: str) -> list[str]:
    role = eval_answer_yaml.scalar_value(text, "case_role")
    findings: list[str] = []
    if role not in CODE_CASE_ROLE_VALUES:
        findings.append(
            f"{path}: code answer case_role must be one of {', '.join(sorted(CODE_CASE_ROLE_VALUES))}"
        )
        return findings
    if role != "ddd_direct":
        return []
    reference_paths = {
        item.get("path", "")
        for item in eval_answer_yaml.list_of_maps(text, "reference_basis")
    }
    for required_path in sorted(DDD_REQUIRED_REFERENCE_PATHS - reference_paths):
        findings.append(f"{path}: ddd_direct answer must reference {required_path}")
    observation_keys = eval_answer_yaml.nested_keys(text, "ddd_observations")
    if not observation_keys:
        findings.append(f"{path}: DDD code answer must declare ddd_observations")
        return findings
    for field in DDD_OBSERVATION_FIELDS:
        if field not in observation_keys:
            findings.append(f"{path}: ddd_observations missing {field}")
    return findings
```

Call it from `validate_answer` when `bucket == "code"`.

- [x] **Step 5: Clarify code eval goal**

Update `workspace/develop/eval/code/eval_goal.md` under `Answer Oracle`:

```markdown
- Direct DDD code cases must declare `case_role: ddd_direct` and include `ddd_observations` with business problem, subdomain type and basis, bounded context, context-map or not-applicable decision, ubiquitous terms, aggregate root, aggregate behavior, invariants, application-service boundary, transaction boundary, Django/API mapping or limitation, and test evidence. Supporting implementation and control/restraint cases must use `case_role: implementation_supporting` or `case_role: control` and must not be counted as DDD-shaped implementation confidence.
```

- [x] **Step 6: Verify pack schema**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_bucket_pack.py
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected before updating answers: `validate_eval_bucket_pack.py` fails on current code answers that lack `case_role`, and later fails on any `ddd_direct` answer without structured DDD references and observations. This is the intended transition failure.

## Task 4: Tighten Existing Code Answers And Classify Control Cases

**Files:**
- Modify: `workspace/develop/eval/code/answer/case-code-order-api.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-python-state.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-coupon-tdd.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-status-migration.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-web-detail.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-small-rename.yaml`
- Modify: `workspace/develop/eval/code/answer/case-code-clarify-external.yaml`

- [x] **Step 1: Add `case_role` to all code answers**

Use these exact roles:

```yaml
case_role: implementation_supporting
```

Use this role for `case-code-order-api`, `case-code-fat-model`, `case-code-python-state`, `case-code-coupon-tdd`, `case-code-status-migration`, and `case-code-web-detail`. These cases test API/DB consistency, migration safety, web rendering boundaries, TDD, typing, or clean-code behavior that supports DDD quality but does not directly prove DDD aggregate/context shape.

```yaml
case_role: control
```

for `case-code-small-rename` and `case-code-clarify-external`.

- [x] **Step 2: Add artifact hard gates to every code answer**

Append this hard gate to every code answer:

```yaml
  - generated runtime artifacts such as db.sqlite3, __pycache__, .pyc, or .pytest_cache must not appear in changed-files.json.
```

- [x] **Step 3: Tighten `case-code-order-api` answer without counting it as direct DDD confidence**

Keep `case-code-order-api` as `case_role: implementation_supporting`. Its primary purpose is API/DB consistency and idempotency behavior. Do not label it `ddd_direct` unless a later revision adds real aggregate state-transition behavior to the fixture and oracle.

Add an explicit interpretation:

```yaml
score_interpretation: API/DB consistency support score; do not count this as direct DDD-shaped aggregate implementation confidence.
consistency_observations:
  application_service_boundary: Order creation and idempotency decisions live in the service/usecase layer; the Ninja router validates input, reads headers, calls the service, and maps errors to Problem Details.
  transaction_boundary: The service owns the atomic section around idempotency lookup/create and unique constraint conflict handling.
  idempotency_storage: Persistence stores idempotency key, request fingerprint, and replay snapshot.
  problem_details: Missing key and payload conflict return Problem Details shaped responses.
  tests:
    - same key and same payload replays same response.
    - same key and different payload returns conflict.
    - API remains a thin adapter.
    - DB race fallback does not create duplicate orders.
```

- [x] **Step 4: Mark control cases as excluded from DDD confidence**

Add to `case-code-small-rename.yaml` and `case-code-clarify-external.yaml`:

```yaml
score_interpretation: Control/restraint score; do not count this as DDD-shaped implementation confidence.
```

- [x] **Step 5: Verify pack validation**

Run:

```bash
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected: pass after all code answers have `case_role`, and only `ddd_direct` answers have required DDD references and observations.

## Task 5: Make `case-code-order-api` Discriminative Again

**Files:**
- Modify: `workspace/develop/eval/code/fixtures/django_shop_service/apps/orders/models.py`
- Modify: `workspace/develop/eval/code/fixtures/django_shop_service/apps/orders/services.py`
- Modify: `workspace/develop/eval/code/fixtures/django_shop_service/apps/orders/api.py`
- Modify: `workspace/develop/eval/code/fixtures/django_shop_service/apps/orders/tests/test_order_api.py`
- Modify: `workspace/develop/eval/code/cases/plugin/public/case-code-order-api.md`
- Modify: `workspace/develop/eval/code/answer/case-code-order-api.yaml`

- [x] **Step 1: Choose the starter gap deliberately**

Do not claim the starter creates duplicate rows while `models.UniqueConstraint(fields=["idempotency_key"])` remains in place. Choose one of these two routes and keep the public case, answer, and fixture consistent:

```text
Preferred route: keep the DB unique constraint, but make the service fail to map IntegrityError and same-key replay into domain/API semantics.
Alternate route: remove the unique constraint and request_fingerprint from starter model/migration so the starter really can create duplicate rows.
```

The preferred route is smaller and better for this cycle. The service starter should keep a weak create-only path and let same-key requests surface as DB integrity errors or generic failures until the evaluated agent implements replay/conflict handling:

```python
@dataclass(frozen=True)
class OrderCreateResult:
    order: Order
    replayed: bool


def order_create(
    *,
    idempotency_key: str,
    customer_email: str,
    total_amount: Decimal,
    note: str = "",
) -> OrderCreateResult:
    with transaction.atomic():
        order = Order.objects.create(
            customer_email=customer_email.strip().lower(),
            total_amount=total_amount,
            idempotency_key=idempotency_key.strip(),
            request_fingerprint="",
            note=note,
        )
        return OrderCreateResult(order=order, replayed=False)
```

Keep `request_fingerprint` helper only if the case expects the agent to use it; otherwise remove it from starter tests so the model must introduce it.

- [x] **Step 2: Weaken the starter API**

Keep only the thin endpoint shell and a simple error schema:

```python
class ErrorOut(Schema):
    detail: str


@api.post("/orders", response={201: OrderOut, 409: ErrorOut})
def create_order(request, payload: OrderCreateIn):
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return 409, {"detail": "Idempotency-Key header is required"}
    result = order_create(
        idempotency_key=idempotency_key,
        customer_email=payload.customer_email,
        total_amount=payload.total_amount,
        note=payload.note,
    )
    order = result.order
    return 201, {
        "id": order.id,
        "customer_email": order.customer_email,
        "total_amount": str(order.total_amount),
        "status": order.status,
        "replayed": result.replayed,
    }
```

- [x] **Step 3: Keep starter tests minimal and failing for target behavior**

Starter tests should verify only the current simple create path. Remove existing replay/conflict tests from the fixture and let the evaluated agent add them.

- [x] **Step 4: Tighten public case wording**

Update `case-code-order-api.md` to say:

```markdown
Fixture repo에서 주문 생성 API의 멱등성과 충돌 처리를 개선해줘.

요구사항:
- 주문 생성 결정은 service/usecase 책임으로 두고, Ninja Router는 얇은 adapter로 남겨줘.
- 같은 `Idempotency-Key`와 같은 payload는 새 주문을 만들지 않고 같은 응답 snapshot을 replay해야 해.
- 같은 `Idempotency-Key`와 다른 payload는 Problem Details conflict로 구분해야 해.
- 중복 방지는 DB unique constraint와 service transaction boundary에서 보장해야 해.
- 관련 서비스/API 테스트를 추가해.

가능하면 `python3 manage.py check`와 `python3 manage.py test`를 실행하고 결과를 보고해줘.
```

- [x] **Step 5: Verify starter fixture still runs its minimal tests**

Run:

```bash
cd workspace/develop/eval/code/fixtures/django_shop_service
python3 manage.py check
python3 manage.py test
```

Expected: passes only if local environment has Django installed. If Django is unavailable in the current environment, record `ModuleNotFoundError: No module named 'django'` as environment limitation and rely on eval runner environment.

## Task 6: Add Direct DDD-To-Code Case

**Files:**
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/README.md`
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/pyproject.toml`
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/apps/orders/models.py`
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/apps/orders/services.py`
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/apps/orders/api.py`
- Create: `workspace/develop/eval/code/fixtures/ddd_order_service/tests/test_orders.py`
- Create: `workspace/develop/eval/code/cases/plugin/public/case-code-ddd-order-placement.md`
- Create: `workspace/develop/eval/code/answer/case-code-ddd-order-placement.yaml`
- Modify: `workspace/develop/eval/code/cases/plugin/code-capture.json`

- [x] **Step 1: Create a small non-Django dependency-free fixture**

Use a pure Python fixture first so hidden behavior can run in the local test environment. Starter `apps/orders/models.py` should intentionally be anemic:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class OrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    customer_id: str
    items: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.DRAFT
```

Starter `apps/orders/services.py` should put domain rules in the service:

```python
from __future__ import annotations

from apps.orders.models import Order, OrderStatus


_ORDERS: dict[str, Order] = {}


def place_order(customer_id: str, items: list[str]) -> Order:
    order = Order(customer_id=customer_id, items=items)
    if not items:
        raise ValueError("empty order")
    order.status = OrderStatus.PENDING_PAYMENT
    _ORDERS[order.id] = order
    return order


def confirm_order(order_id: str) -> Order:
    order = _ORDERS[order_id]
    order.status = OrderStatus.CONFIRMED
    return order
```

- [x] **Step 2: Add public case**

Create `case-code-ddd-order-placement.md`:

```markdown
주문 배치/확정 흐름을 DDD 기준에 맞게 리팩터링해줘.

요구사항:
- Ordering bounded context 안에서 사용하는 유비쿼터스 언어가 코드 이름에 드러나야 해.
- `Order`는 aggregate root로서 빈 주문 배치 금지와 결제 대기 상태에서만 확정 가능하다는 불변식을 보호해야 해.
- application service는 유스케이스 흐름을 조정하되 핵심 상태 전이 규칙을 소유하지 않게 해.
- 외부 결제/알림 연동은 실제 호출하지 말고 필요한 event/after-commit 경계만 코드나 테스트로 표현해.
- 과한 repository/UoW/hexagonal 구조는 만들지 마.
- 관련 단위 테스트를 추가하고 `python3 -m unittest discover -s tests` 결과를 보고해줘.
```

- [x] **Step 3: Add private answer oracle**

Create `case-code-ddd-order-placement.yaml` with:

```yaml
id: case-code-ddd-order-placement
case_id: case-code-ddd-order-placement
bucket: code
kind: code
public_case: workspace/develop/eval/code/cases/plugin/public/case-code-ddd-order-placement.md
intent: Directly verify DDD-to-code mapping for order placement and confirmation.
case_role: ddd_direct
reference_basis:
  - path: workspace/develop/eval/code/eval_goal.md
    basis: DDD-to-code mapping
  - path: workspace/docs/ddd-implementation-standard.md
    basis: DDD implementation order and aggregate/application service boundaries
  - path: workspace/reference/architecture-ddd/reference/final.md
    basis: strategic before tactical and aggregate/invariant guidance
code_expected: true
deterministic_checks:
  - id: unit-tests
    command: python3 -m unittest discover -s tests
    expected_exit: 0
    evidence: command-artifact
target_behavior:
  required:
    - Names Ordering bounded context or keeps ordering language explicit in code and tests.
    - Moves empty-order and confirm-only-from-pending-payment invariants into Order behavior.
    - Keeps application service as orchestration rather than rule owner.
    - Adds behavior tests for empty order rejection, placement status, confirmation transition, and invalid confirmation transition.
  forbidden:
    - Repository/UoW/hexagonal rewrite for this small in-memory fixture.
    - Router/API owning state transition rules.
allowed_paths:
  - apps/orders/**
  - tests/**
forbidden_paths:
  - workspace/develop/eval/**
  - dddjango/**
ddd_observations:
  business_problem: Customers can place orders and confirm payment only through valid order state transitions.
  subdomain_type: Ordering is treated as core/high-risk supporting because state transitions and duplicate business decisions are central to order correctness.
  subdomain_type_basis: Order state correctness directly affects customer-facing fulfillment and payment consistency in the fixture.
  bounded_context: Ordering
  context_map_or_not_applicable: No external bounded context is integrated in this pure Python fixture; payment/notification is represented only as a boundary to avoid fake external calls.
  ubiquitous_terms:
    - Order
    - place order
    - pending payment
    - confirm order
  aggregate_root: Order
  aggregate_behavior:
    - Order.place or equivalent aggregate behavior protects empty-order placement.
    - Order.confirm or equivalent aggregate behavior protects confirmation state transition.
  invariants:
    - An order cannot be placed without items.
    - An order can be confirmed only from pending payment.
  application_service_boundary: Service functions orchestrate creation/loading and call aggregate behavior; they do not own the invariant checks.
  transaction_boundary: In-memory fixture has no DB transaction; final answer must state this limitation rather than inventing database verification.
  domain_events: If side effects are discussed, they must be modeled as post-transition event/after-commit boundary, not direct external calls.
  django_mapping:
    - Pure Python fixture maps the aggregate and application service responsibilities before Django persistence.
  test_evidence:
    - empty order rejection
    - placement moves to pending payment
    - confirmation moves to confirmed
    - invalid confirmation raises
scoring_checks:
  - pass if aggregate behavior protects invariants and tests prove the behavior.
  - fail if service-only procedural rules remain the only protection.
hard_gates:
  - no evaluator-only answer material, private scoring notes, or prior run findings leak into public/runtime output.
  - claimed command execution, file inspection, tests, or subagent execution must be supported by run artifacts or explicit response evidence.
  - generated runtime artifacts such as db.sqlite3, __pycache__, .pyc, or .pytest_cache must not appear in changed-files.json.
failure_modes:
  - anemic aggregate
  - tactical-pattern overengineering
  - false verification claim
leakage_checks:
  - no private answer references.
evidence_required:
  - changed-files.json
  - diff.patch
  - unit test output
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - ddd-to-code
  - domain-policy
  - test-implementation
```

- [x] **Step 4: Register code capture metadata**

Add:

```json
"case-code-ddd-order-placement": {
  "captureCode": true,
  "subjectRepo": "workspace/develop/eval/code/fixtures/ddd_order_service"
}
```

to `workspace/develop/eval/code/cases/plugin/code-capture.json`.

- [x] **Step 5: Verify fixture tests before model runs**

Run:

```bash
cd workspace/develop/eval/code/fixtures/ddd_order_service
python3 -m unittest discover -s tests
```

Expected: existing starter tests pass. The starter tests should not already assert the target DDD behavior; target behavior is checked by answer oracle and model-added tests.

## Task 7: Add Evaluator-Owned Behavior And Source-Shape Checks Without Leaking Them

**Files:**
- Create: `workspace/scripts/eval_code_behavior_checks.py`
- Modify: `workspace/scripts/run_eval_bucket.py`
- Modify: `workspace/scripts/test_run_eval_bucket.py`
- Modify: `workspace/scripts/validate_eval_code_artifacts.py`
- Modify: `workspace/scripts/test_validate_eval_code_artifacts.py`
- Modify: `workspace/develop/eval/code/answer/*.yaml`

- [x] **Step 1: Add evaluator-owned behavior and source-shape check script**

Create a script that accepts `case_id` and an isolated workspace path. This script lives in the evaluator repository, not inside the copied subject fixture. It must be run from repo root and inspect the modified isolated workspace passed by `--workspace`.

The check must fail on the starter fixture. It should verify both behavior and source shape so service-only procedural code cannot pass as DDD-shaped aggregate code.

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import importlib
import sys
from pathlib import Path


def require_order_behavior(workspace: Path) -> None:
    model_path = workspace / "apps/orders/models.py"
    tree = ast.parse(model_path.read_text(encoding="utf-8"))
    order_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Order"
        ),
        None,
    )
    if order_class is None:
        raise AssertionError("Order aggregate root is missing")
    method_names = {
        node.name
        for node in order_class.body
        if isinstance(node, ast.FunctionDef)
    }
    missing = {"place", "confirm"} - method_names
    if missing:
        raise AssertionError(f"Order aggregate behavior missing: {', '.join(sorted(missing))}")


def require_service_does_not_mutate_status_directly(workspace: Path) -> None:
    service_text = (workspace / "apps/orders/services.py").read_text(encoding="utf-8")
    if ".status =" in service_text:
        raise AssertionError("application service must call aggregate behavior instead of assigning status")


def run_ddd_order_placement(workspace: Path) -> None:
    sys.path.insert(0, str(workspace))
    require_order_behavior(workspace)
    require_service_does_not_mutate_status_directly(workspace)

    models = importlib.import_module("apps.orders.models")
    services = importlib.import_module("apps.orders.services")

    order = services.place_order("customer-1", ["sku-1"])
    assert order.status == models.OrderStatus.PENDING_PAYMENT
    confirmed = services.confirm_order(order.id)
    assert confirmed.status == models.OrderStatus.CONFIRMED
    try:
        services.confirm_order(order.id)
    except ValueError:
        pass
    else:
        raise AssertionError("confirmed order must not be confirmed twice")
    try:
        services.place_order("customer-1", [])
    except ValueError:
        pass
    else:
        raise AssertionError("empty order must fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.case == "case-code-ddd-order-placement":
        run_ddd_order_placement(args.workspace.resolve())
    else:
        raise SystemExit(f"unknown behavior check case: {args.case}")
    print(f"behavior checks passed: {args.case}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [x] **Step 2: Add answer support for behavior checks**

Extend `case_role: ddd_direct` answers with:

```yaml
behavior_checks:
  - id: hidden-ddd-order-placement
    command: python3 workspace/scripts/eval_code_behavior_checks.py --case case-code-ddd-order-placement
    expected_exit: 0
```

The answer command intentionally omits `--workspace`. The runner must append `--workspace <isolated subject workspace>` and execute the command from `REPO_ROOT`, not from the fixture workspace. Do not copy `eval_code_behavior_checks.py` into the subject workspace or expose it in the public prompt.

- [x] **Step 3: Wire runner support**

Modify `run_eval_bucket.py` so behavior checks are loaded from answer YAML, executed after deterministic checks, and recorded under:

```text
code/<case>/<variant>/behavior-checks/<id>-command.txt
code/<case>/<variant>/behavior-checks/<id>-exit.txt
code/<case>/<variant>/behavior-checks/<id>-stdout.txt
code/<case>/<variant>/behavior-checks/<id>-stderr.txt
```

Runner behavior:

```python
command = shlex.split(command_text)
command.extend(["--workspace", str(workspace)])
result = run_command(command, prompt=None, cwd=REPO_ROOT, timeout_seconds=timeout_seconds)
```

- [x] **Step 4: Wire validator support**

Modify `validate_eval_code_artifacts.py` to require behavior check artifacts and expected exit for any `behavior_checks` block.

- [x] **Step 5: Verify runner and validator tests**

Run:

```bash
.venv/bin/python -m unittest workspace/scripts/test_run_eval_bucket.py
.venv/bin/python -m unittest workspace/scripts/test_validate_eval_code_artifacts.py
```

Expected: both pass.

## Task 8: Re-run Targeted And Full Eval

**Files:**
- Generated: `workspace/develop/eval/code/runs/<new-run-id>/**`
- Generated: `workspace/develop/eval/*/latest/report.html`

- [x] **Step 1: Run static validation**

Run:

```bash
.venv/bin/python -m unittest discover -s workspace/scripts -p 'test_*.py'
.venv/bin/python workspace/scripts/validate_eval_bucket_pack.py
```

Expected: all tests pass and bucket pack validation passes with updated code case count.

- [ ] **Step 2: Run targeted DDD code eval**

Run:

```bash
make eval-one BUCKET=code TRY_NUMBER=3 SCOPE=targeted TOPIC=ddd-code-quality CASE=case-code-ddd-order-placement EXTRA_ARGS=--rerun
```

Expected: run completes, code artifact validation passes, and report shows a scored answer-oracle evaluation.

- [ ] **Step 3: Run targeted order API eval**

Run:

```bash
make eval-one BUCKET=code TRY_NUMBER=3 SCOPE=targeted TOPIC=order-api-consistency-quality CASE=case-code-order-api EXTRA_ARGS=--rerun
```

Expected: run completes without `db.sqlite3` or generated artifacts in changed-files, and with-ddjango improves over baseline for real missing behavior.

- [ ] **Step 4: Refresh latest reports**

Run:

```bash
.venv/bin/python workspace/scripts/render_eval_review_html.py --refresh-latest
```

Expected: `workspace/develop/eval/code/latest/report.html` points to the latest reportable code run.

- [ ] **Step 5: Run full regression only after targeted runs are clean**

Run:

```bash
make eval-all TRY_NUMBER=3 SCOPE=full TOPIC=ddd-code-quality EXTRA_ARGS=--rerun JOBS=3
```

Expected: all buckets finish, `code` shows higher-quality DDD evidence, and control cases are not interpreted as DDD implementation confidence.

## Review Checklist For Agent Review

- [ ] Does this plan preserve public/private eval separation?
- [ ] Does any public case leak answer-only expected behavior?
- [ ] Are DDD criteria concrete enough to distinguish terminology from implementation?
- [ ] Are deterministic validators strong enough to catch the previous `db.sqlite3` false positive?
- [ ] Is `case-code-order-api` now a genuine starter problem?
- [ ] Are control cases excluded from DDD confidence?
- [ ] Are new behavior checks private enough and recorded as artifacts?
- [ ] Is the plan scoped so implementation can be committed task by task?

## Execution Notes

- Do not delete historical run folders as part of this plan.
- Do not use current run artifacts as source-of-truth expected answers.
- Do not weaken answer oracles to preserve the current 5/5 score.
- Do not copy this plan file into eval workspaces, public cases, prompt-input artifacts, runtime skill references, or subject fixtures. The plan contains private oracle examples for implementation clarity.
- Do not count `case_role: control` or `case_role: implementation_supporting` scores as direct DDD-shaped implementation confidence.
- Keep commits small:
  - commit validator gates first,
  - commit pipeline hard-gate integration second,
  - commit answer schema changes third,
  - commit fixture/case changes fourth,
  - commit new DDD case fifth,
  - commit runner behavior checks only if Task 7 is implemented in this cycle.
