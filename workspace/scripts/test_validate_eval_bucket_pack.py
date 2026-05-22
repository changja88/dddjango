#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_eval_bucket_pack.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_eval_bucket_pack", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalBucketPackValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.validator.REPO_ROOT = self.root
        self.validator.EVAL_ROOT = self.root / "workspace/develop/eval"

    def write_case_pair(
        self,
        bucket: str,
        case_id: str,
        *,
        public_text: str = "사용자 요청처럼 작성된 공개 문제입니다.\n",
        coverage_tags: list[str] | None = None,
        extra_answer: str = "",
    ) -> None:
        public_path = (
            self.validator.EVAL_ROOT
            / bucket
            / "cases/plugin/public"
            / f"{case_id}.md"
        )
        answer_path = self.validator.EVAL_ROOT / bucket / "answer" / f"{case_id}.yaml"
        public_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        public_path.write_text(public_text, encoding="utf-8")
        tags = coverage_tags if coverage_tags is not None else [case_id.removeprefix("case-")]
        tag_lines = "".join(f"  - {tag}\n" for tag in tags)
        answer_path.write_text(
            f"""id: {case_id}
case_id: {case_id}
bucket: {bucket}
kind: {bucket}
public_case: workspace/develop/eval/{bucket}/cases/plugin/public/{case_id}.md
intent: Validate one behavior.
reference_basis:
  - path: workspace/develop/eval/{bucket}/eval_goal.md
    basis: test basis
target_behavior:
  required:
    - Required behavior.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
{tag_lines}{extra_answer}""",
            encoding="utf-8",
        )

    def test_public_case_rejects_oracle_schema_terms(self) -> None:
        public_path = self.root / "case.md"
        public_path.write_text(
            "reference_basis와 coverage_tags를 공개 문제에서 설명해줘.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_public_case(public_path)

        self.assertTrue(findings)

    def test_public_case_rejects_remaining_answer_only_schema_terms(self) -> None:
        public_path = self.root / "case.md"
        public_path.write_text(
            "hard_gates, expected_outcomes, control_case, with_dddjango 값을 공개 문제에서 설명해줘.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_public_case(public_path)

        self.assertTrue(any("hard_gates" in finding for finding in findings), findings)
        self.assertTrue(any("expected_outcomes" in finding for finding in findings), findings)
        self.assertTrue(any("control_case" in finding for finding in findings), findings)
        self.assertTrue(any("with_dddjango" in finding for finding in findings), findings)

    def test_workflow_p5_combined_coverage_rejects_direct_risky_write_fragment(self) -> None:
        text = """id: case-workflow-risky-write
case_id: case-workflow-risky-write
bucket: workflow
kind: workflow
public_case: workspace/develop/eval/workflow/cases/plugin/public/case-workflow-risky-write.md
intent: Validate risky write.
reference_basis:
  - path: dddjango/skills/workflow-dddjango-subagents/references/role-map.md
    basis: role map
  - path: dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md
    basis: handoff
  - path: dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md
    basis: integration
target_behavior:
  required:
    - Includes aggregate invariant, transaction owner, locking/isolation, uniqueness, idempotency storage, Idempotency-Key replay/conflict, side effect timing, retry and isolation decisions, concurrency/integration tests, integration owner, and handoff closure.
  forbidden:
    - Missing Domain, Architecture, DB, API, Django, TDD/Test, Review, Integration role split.
    - Missing Scope, Inputs Used, Decisions, Files, May edit, Must not edit, Output, Risks, Required Follow-up, and dddjango Checks.
workflow_execution_expectation:
  expected_mode: direct_risky_write
  acceptable_modes:
    - direct
  forbidden_modes:
    - false_actual_claim
  decision_rule: direct advice is allowed.
  responsibility_rule: risky write fields are present.
  report_label: direct
coverage_tags:
  - risky-write-consistency
  - handoff-contract
  - responsibility-split
  - integration-closure
"""

        self.assertFalse(self.validator.has_workflow_p5_combined_coverage(text))

    def test_workflow_p5_combined_coverage_rejects_forbidden_only_terms(self) -> None:
        text = """id: case-workflow-risky-write
case_id: case-workflow-risky-write
bucket: workflow
kind: workflow
public_case: workspace/develop/eval/workflow/cases/plugin/public/case-workflow-risky-write.md
intent: Validate P5 risky write.
reference_basis:
  - path: dddjango/skills/workflow-dddjango-subagents/references/role-map.md
    basis: role map
  - path: dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md
    basis: handoff
  - path: dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md
    basis: integration
target_behavior:
  required:
    - Uses Domain, Architecture, DB, API, Django, TDD/Test, Review, and Integration roles.
    - Includes Scope, Inputs Used, Decisions, Files, May edit, Must not edit, Output, Risks, Required Follow-up, and dddjango Checks.
  forbidden:
    - Missing aggregate invariant, transaction owner, locking/isolation, uniqueness, idempotency storage, Idempotency-Key replay/conflict, side effect timing, retry and isolation decisions, concurrency/integration tests, integration owner, and handoff closure.
workflow_execution_expectation:
  expected_mode: p5_workflow
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - direct
    - false_actual_claim
  decision_rule: workflow handoff is required.
  responsibility_rule: risky write fields are owned by roles.
  report_label: P5
coverage_tags:
  - risky-write-consistency
  - handoff-contract
  - responsibility-split
  - integration-closure
"""

        self.assertFalse(self.validator.has_workflow_p5_combined_coverage(text))

    def test_workflow_p5_combined_coverage_accepts_handoff_risky_write_case(self) -> None:
        text = """id: case-workflow-risky-write
case_id: case-workflow-risky-write
bucket: workflow
kind: workflow
public_case: workspace/develop/eval/workflow/cases/plugin/public/case-workflow-risky-write.md
intent: Validate P5 risky write.
reference_basis:
  - path: dddjango/skills/workflow-dddjango-subagents/references/role-map.md
    basis: role map
  - path: dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md
    basis: handoff
  - path: dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md
    basis: integration
target_behavior:
  required:
    - Uses Domain, Architecture, DB, API, Django, TDD/Test, Review, and Integration roles.
    - Includes Scope, Inputs Used, Decisions, Files, May edit, Must not edit, Output, Risks, Required Follow-up, and dddjango Checks.
    - Includes aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, Idempotency-Key replay/conflict, side effect timing, retry and isolation decisions, concurrency/integration tests, integration owner, and handoff closure.
workflow_execution_expectation:
  expected_mode: p5_workflow
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - direct
    - false_actual_claim
  decision_rule: workflow handoff is required.
  responsibility_rule: risky write fields are owned by roles.
  report_label: P5
coverage_tags:
  - risky-write-consistency
  - handoff-contract
  - responsibility-split
  - integration-closure
"""

        self.assertTrue(self.validator.has_workflow_p5_combined_coverage(text))

    def test_response_p5_django_integration_rejects_fragmented_boundary_tags(self) -> None:
        text = """id: case-response-django-implementation-handoff
case_id: case-response-django-implementation-handoff
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-django-implementation-handoff.md
intent: Validate P5 handoff.
reference_basis:
  - path: workspace/reference/implementation-django/reference/final.md
    basis: Django service
target_behavior:
  required:
    - Mentions Django service, API adapter, pytest, and handoff.
scoring_checks:
  - pass if generic.
hard_gates:
  - no leakage.
failure_modes:
  - generic list only
leakage_checks:
  - no private material
evidence_required:
  - transcript
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - p5-django-implementation-integration
  - mixed-boundary
"""

        self.assertFalse(self.validator.has_response_p5_django_integration_coverage(text))

    def test_response_p5_django_integration_accepts_full_boundary_matrix(self) -> None:
        text = """id: case-response-django-implementation-handoff
case_id: case-response-django-implementation-handoff
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-django-implementation-handoff.md
intent: Validate P5 Django implementation handoff.
reference_basis:
  - path: workspace/reference/architecture-api/reference/final.md
    basis: API contract
  - path: workspace/reference/architecture-db/reference/final.md
    basis: DB policy
  - path: workspace/reference/implementation-django/reference/final.md
    basis: Django implementation
  - path: workspace/reference/implementation-django-ninja/reference/final.md
    basis: Ninja adapter
  - path: workspace/reference/implementation-django-web/reference/final.md
    basis: Django Web
  - path: workspace/reference/implementation-python/reference/final.md
    basis: Python typing
  - path: workspace/reference/implementation-cleancode/reference/final.md
    basis: Clean Code review
  - path: workspace/reference/implementation-tdd/reference/final.md
    basis: TDD procedure
  - path: workspace/reference/implementation-test/reference/final.md
    basis: pytest mechanics
  - path: dddjango/skills/architecture-api/references/rest-contracts.md
    basis: API contract
  - path: dddjango/skills/architecture-db/references/transactions-locking.md
    basis: transaction policy
  - path: dddjango/skills/implementation-django/references/services-selectors.md
    basis: service boundary
  - path: dddjango/skills/implementation-django-ninja/references/router-schema.md
    basis: Router Schema adapter
  - path: dddjango/skills/implementation-django-web/references/templateview-htmx.md
    basis: web boundary
  - path: dddjango/skills/implementation-python/references/typing.md
    basis: typing boundary
  - path: dddjango/skills/implementation-cleancode/references/responsibility.md
    basis: review boundary
  - path: dddjango/skills/implementation-tdd/references/red-green-refactor.md
    basis: TDD procedure
  - path: dddjango/skills/implementation-test/references/django-api-concurrency.md
    basis: pytest mechanics
  - path: dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md
    basis: handoff
target_behavior:
  required:
    - Separates architecture-api ownership of resource method status code Problem Details OpenAPI API contract from implementation-django-ninja ownership of thin Router Schema adapter mapping.
    - Separates architecture-db transaction policy uniqueness locking retry idempotency duplicate prevention migration rollout risk from implementation-django concrete ORM service migration transaction implementation.
    - Keeps OrderService.confirm production implementation boundary and transaction.on_commit timing; Router template test fixture and review notes must not own the domain rule.
    - Routes server-rendered status badge view context template static auth and render honesty to implementation-django-web.
    - Routes OrderStatus money display typing dataclass StrEnum typecheck honesty to implementation-python.
    - Separates implementation-tdd test list first failing test red-green-refactor boundary cases from implementation-test pytest fixtures factory TestClient concurrency assertions.
    - Uses implementation-cleancode review responsibility for fat service template business logic naming encapsulation responsibility split without replacing production implementation or tests.
    - Gives a handoff ownership table naming each skill boundary and unresolved follow-up without claiming file edits tests browser migrations type checks or subagent execution.
scoring_checks:
  - pass if full matrix is present.
hard_gates:
  - no leakage.
failure_modes:
  - boundary missing
leakage_checks:
  - no private material
evidence_required:
  - transcript
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - p5-django-implementation-integration
  - mixed-boundary
  - handoff-contract
  - integration-closure
  - django-implementation-handoff
  - api-ninja-boundary
  - db-django-boundary
  - web-python-boundary
  - tdd-test-boundary
  - clean-code-review-boundary
  - workflow-honesty
"""

        self.assertTrue(self.validator.has_response_p5_django_integration_coverage(text))

    def test_web_detail_public_case_requires_blank_memo_fallback(self) -> None:
        public_path = self.root / "case-code-web-detail.md"
        public_path.write_text(
            "주문 상세 페이지 관련 코드를 정리해줘.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_public_case(public_path)

        self.assertTrue(
            any("blank memo fallback" in finding for finding in findings),
            findings,
        )

    def test_web_detail_public_case_requires_static_css_reference_guidance(self) -> None:
        public_path = self.root / "case-code-web-detail.md"
        public_path.write_text(
            "주문 상세 페이지 관련 코드를 정리해줘.\n"
            "- blank memo fallback을 처리해.\n",
            encoding="utf-8",
        )

        findings = self.validator.validate_public_case(public_path)

        self.assertTrue(
            any("detail.css reference" in finding for finding in findings),
            findings,
        )

    def test_implementation_django_web_answer_requires_source_refs(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django-web-missing-source",
            coverage_tags=["implementation-django-web"],
        )
        answer_path = (
            self.validator.EVAL_ROOT
            / "response/answer/case-response-django-web-missing-source.yaml"
        )
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django-web-missing-source.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("implementation-django-web answer must reference" in finding for finding in findings),
            findings,
        )

    def test_response_direct_django_web_coverage_requires_direct_case(self) -> None:
        tags = sorted(
            self.validator.REQUIRED_COVERAGE_TAGS["response"]
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
        )
        self.write_case_pair(
            "response",
            "case-response-web-typing",
            coverage_tags=tags,
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("implementation-django-web P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )

    def test_response_direct_django_web_coverage_accepts_source_backed_case(self) -> None:
        text = """id: case-response-django-web-page
case_id: case-response-django-web-page
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-django-web-page.md
intent: Validate Django Web direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-django-web/reference/final.md
    basis: Django Web source basis
  - path: dddjango/skills/implementation-django-web/SKILL.md
    basis: Django Web runtime basis
  - path: dddjango/skills/implementation-django-web/references/templateview-htmx.md
    basis: Django Web bundled basis
target_behavior:
  required:
    - TemplateView, Generic CBV, and FBV selection are separated.
    - template base include boundaries are covered.
    - static CSS and JS are linked from rendered templates.
    - None, blank, missing optional, display-ready fallback values are prepared before templates.
    - form GET, valid POST, invalid POST, user-recoverable error rendering, and ModelForm.Meta.fields handling is covered.
    - HTMX CSRF behavior is covered.
    - auth permission checks happen before render.
    - render browser collectstatic and check --deploy reporting is honest.
    - REST Router ORM handoff boundaries are stated.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-django-web
  - django-web
  - templateview-cbv-fbv
  - templates-base-includes
  - static-assets
  - display-ready-fallback
  - web-forms
  - htmx-csrf
  - auth-permission
  - render-acceptance
  - routing-boundary
  - validation-honesty
"""

        self.assertTrue(self.validator.has_implementation_django_web_direct_coverage(text))
        findings = self.validator.validate_implementation_django_web_answer(
            self.root / "answer.yaml",
            text,
            "response",
        )

        self.assertEqual([], findings)

    def test_django_web_answer_requires_each_group_not_one_loose_term(self) -> None:
        text = """id: case-response-django-web-page
case_id: case-response-django-web-page
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-django-web-page.md
intent: Validate Django Web direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-django-web/reference/final.md
    basis: Django Web source basis
  - path: dddjango/skills/implementation-django-web/SKILL.md
    basis: Django Web runtime basis
  - path: dddjango/skills/implementation-django-web/references/templateview-htmx.md
    basis: Django Web bundled basis
target_behavior:
  required:
    - TemplateView is mentioned, but the answer omits other view choices.
    - template base include boundaries are covered.
    - static CSS and JS are linked from rendered templates.
    - None, blank, missing optional values use fallback values.
    - form POST invalid handling is covered.
    - HTMX CSRF behavior is covered.
    - auth permission checks happen before render.
    - render browser collectstatic and check --deploy reporting is honest.
    - REST Router ORM handoff boundaries are stated.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-django-web
"""

        findings = self.validator.validate_implementation_django_web_answer(
            self.root / "answer.yaml",
            text,
            "response",
        )

        self.assertTrue(
            any("templateview-cbv-fbv" in finding and "generic cbv" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("web-forms" in finding and "valid post" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("web-forms" in finding and "recoverable" in finding for finding in findings),
            findings,
        )

    def test_code_bucket_requires_direct_django_web_source_backed_case(self) -> None:
        tags = sorted(
            self.validator.REQUIRED_COVERAGE_TAGS["code"]
            | self.validator.CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
        )
        self.write_case_pair("code", "case-code-small-web-tags", coverage_tags=tags)
        answer = self.validator.EVAL_ROOT / "code/answer/case-code-small-web-tags.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8").replace(
                "coverage_tags:\n",
                "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
            ),
            encoding="utf-8",
        )
        metadata_path = self.validator.EVAL_ROOT / "code/cases/plugin/code-capture.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        fixture = self.validator.EVAL_ROOT / "code/fixtures/shop_service"
        fixture.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            '{"cases":{"case-code-small-web-tags":{"captureCode":true,"subjectRepo":"workspace/develop/eval/code/fixtures/shop_service"}}}',
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("code")

        self.assertTrue(
            any("code: implementation-django-web P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )

    def test_response_bucket_requires_implementation_python_p4_coverage_tags(self) -> None:
        expected_python_tags = {
            "implementation-python",
            "python-type-contracts",
            "none-union",
            "built-in-generics",
            "typeddict",
            "type-narrowing",
            "dataclass-value-object",
            "enum-strenum",
            "protocol-boundary",
            "context-manager",
            "pydantic-v2-boundary",
            "async-concurrency",
            "exceptions",
            "ruff-typecheck",
            "python-version-gate",
            "routing-boundary",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS,
            expected_python_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | (expected_python_tags - {"typeddict"})
        )
        self.write_case_pair("response", "case-response-python-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("implementation-python P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("typeddict" in finding for finding in findings), findings)

    def test_implementation_python_answer_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-python-boundaries",
            coverage_tags=["implementation-python"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-python-boundaries.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-python-boundaries.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-python/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-python/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-python/references/typing.md" in finding for finding in findings),
            findings,
        )

    def test_response_direct_implementation_python_coverage_accepts_source_backed_case(self) -> None:
        text = """id: case-response-python-boundaries
case_id: case-response-python-boundaries
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-python-boundaries.md
intent: Validate Python implementation direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-python/reference/final.md
    basis: Python source basis
  - path: dddjango/skills/implementation-python/SKILL.md
    basis: Python runtime basis
  - path: dddjango/skills/implementation-python/references/typing.md
    basis: typing
  - path: dddjango/skills/implementation-python/references/dataclasses-enums.md
    basis: dataclasses and enums
  - path: dddjango/skills/implementation-python/references/protocols-boundaries.md
    basis: protocols and boundaries
  - path: dddjango/skills/implementation-python/references/pydantic-v2.md
    basis: pydantic v2
target_behavior:
  required:
    - Public type hints show input return None behavior with X | None and built-in generics.
    - TypedDict captures external JSON shape.
    - TypeIs TypeGuard and ordinary None checks are version gated.
    - dataclass value object uses frozen slots and Decimal.
    - Enum StrEnum Literal and match/case are selected by state meaning.
    - Protocol is limited to a replaceable boundary.
    - context manager handles cleanup.
    - pydantic uses model_validate model_dump ConfigDict field_validator model_validator.
    - async TaskGroup except* thread fallback and async-safe checks are explained.
    - exception paths do not return None for exceptional failures.
    - Ruff mypy pyright and Python target verification are honest.
    - DDD DB REST Django workflow handoff boundaries are stated.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-python
  - python-type-contracts
  - none-union
  - built-in-generics
  - typeddict
  - type-narrowing
  - dataclass-value-object
  - enum-strenum
  - protocol-boundary
  - context-manager
  - pydantic-v2-boundary
  - async-concurrency
  - exceptions
  - ruff-typecheck
  - python-version-gate
  - routing-boundary
  - validation-honesty
"""

        self.assertTrue(self.validator.has_implementation_python_direct_coverage(text))
        findings = self.validator.validate_implementation_python_answer(
            self.root / "answer.yaml",
            text,
        )

        self.assertEqual([], findings)

    def test_response_direct_implementation_python_coverage_rejects_mixed_workflow_tags(self) -> None:
        for excluded_tag in ("mixed-boundary", "role-map-sync", "subagent-opt-out"):
            with self.subTest(excluded_tag=excluded_tag):
                self.assertFalse(
                    self.validator.has_implementation_python_direct_coverage(
                        self.implementation_python_direct_answer_text(extra_tag=excluded_tag)
                    )
                )

    def implementation_python_direct_answer_text(self, *, extra_tag: str | None = None) -> str:
        extra_line = f"  - {extra_tag}\n" if extra_tag else ""
        return f"""id: case-response-python-boundaries
case_id: case-response-python-boundaries
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-python-boundaries.md
intent: Validate Python implementation direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-python/reference/final.md
    basis: Python source basis
  - path: dddjango/skills/implementation-python/SKILL.md
    basis: Python runtime basis
  - path: dddjango/skills/implementation-python/references/typing.md
    basis: typing
  - path: dddjango/skills/implementation-python/references/dataclasses-enums.md
    basis: dataclasses and enums
  - path: dddjango/skills/implementation-python/references/protocols-boundaries.md
    basis: protocols and boundaries
  - path: dddjango/skills/implementation-python/references/pydantic-v2.md
    basis: pydantic v2
target_behavior:
  required:
    - Required behavior.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-python
  - python-type-contracts
  - none-union
  - built-in-generics
  - typeddict
  - type-narrowing
  - dataclass-value-object
  - enum-strenum
  - protocol-boundary
  - context-manager
  - pydantic-v2-boundary
  - async-concurrency
  - exceptions
  - ruff-typecheck
  - python-version-gate
  - routing-boundary
  - validation-honesty
{extra_line}"""

    def test_code_bucket_requires_implementation_python_p4_coverage_tags(self) -> None:
        expected_python_tags = {
            "code-implementation-python",
            "implementation-python",
            "python-type-contracts",
            "dataclass-value-object",
            "enum-strenum",
            "protocol-boundary",
            "pydantic-v2-boundary",
            "ruff-typecheck",
            "python-version-gate",
            "command-honesty",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS,
            expected_python_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["code"] - {"python-typing"})
            | self.validator.CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | (expected_python_tags - {"enum-strenum"})
        )
        self.write_case_pair("code", "case-code-python-state", coverage_tags=tags)
        answer = self.validator.EVAL_ROOT / "code/answer/case-code-python-state.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8").replace(
                "coverage_tags:\n",
                "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
            ),
            encoding="utf-8",
        )
        metadata_path = self.validator.EVAL_ROOT / "code/cases/plugin/code-capture.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        fixture = self.validator.EVAL_ROOT / "code/fixtures/shop_service"
        fixture.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            '{"cases":{"case-code-python-state":{"captureCode":true,"subjectRepo":"workspace/develop/eval/code/fixtures/shop_service"}}}',
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("code")

        self.assertTrue(
            any("implementation-python P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("enum-strenum" in finding for finding in findings), findings)

    def test_code_implementation_python_answer_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-python-state",
            coverage_tags=["code-implementation-python", "implementation-python"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-python-state.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-python-state.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-python/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-python/SKILL.md" in finding for finding in findings),
            findings,
        )

    def test_answer_rejects_empty_required_list_blocks(self) -> None:
        self.write_case_pair("source", "case-source-empty", coverage_tags=[])
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-empty.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-empty.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("coverage_tags" in finding for finding in findings))

    def test_answer_requires_expected_outcomes_and_hard_gates(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("hard_gates:\n  - no evaluator-only material leaks.\n", "")
        text = text.replace(
            "expected_outcomes:\n"
            "  baseline: partial\n"
            "  with_dddjango: pass\n"
            "  expected_delta: positive\n"
            "  baseline_pass_ok: false\n",
            "",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("missing hard_gates" in finding for finding in findings))
        self.assertTrue(any("missing expected_outcomes" in finding for finding in findings))

    def test_answer_requires_expected_outcome_fields(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("  expected_delta: positive\n", "")
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )
        answer_path.write_text(text, encoding="utf-8")

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("expected_outcomes missing expected_delta" in finding for finding in findings))

    def test_source_provisional_drf_answer_requires_guardrail_axes(self) -> None:
        self.write_case_pair(
            "source",
            "case-source-provisional-drf",
            coverage_tags=["provisional-handling", "drf-guardrail", "source-gap"],
        )
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-provisional-drf.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-provisional-drf.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(
            any("source provisional/DRF answer must reference workspace/reference/architecture-api/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source provisional/DRF answer target_behavior missing runtime routing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source provisional/DRF answer must reference workspace/reference/architecture-implementation-patterns/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source provisional/DRF answer must reference workspace/reference/implementation-django-web/reference/final.md" in finding for finding in findings),
            findings,
        )

    def test_source_metadata_cache_answer_requires_runtime_metadata_and_cache_axes(self) -> None:
        self.write_case_pair(
            "source",
            "case-source-metadata-cache-sync",
            coverage_tags=["runtime-metadata-cache-sync"],
        )
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-metadata-cache-sync.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-metadata-cache-sync.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(
            any("source metadata/cache answer must reference dddjango/skills/source-reference-audit/agents/openai.yaml" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source metadata/cache answer target_behavior missing semantic metadata alignment" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source metadata/cache answer target_behavior missing cache/source parity" in finding for finding in findings),
            findings,
        )

    def test_source_routing_exclusion_answer_requires_positive_and_negative_routing(self) -> None:
        self.write_case_pair(
            "source",
            "case-source-routing-exclusion",
            coverage_tags=["source-audit-exclusion"],
        )
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-routing-exclusion.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-routing-exclusion.md"
        )

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(
            any("source routing exclusion answer target_behavior missing positive source audit routing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source routing exclusion answer target_behavior missing application implementation exclusion" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("source routing exclusion answer target_behavior missing test mechanics exclusion" in finding for finding in findings),
            findings,
        )

    def test_positive_implementation_answer_rejects_baseline_pass_ok_true(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-django-positive",
            coverage_tags=["implementation-django"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-django-positive.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        text = text.replace("  baseline_pass_ok: false\n", "  baseline_pass_ok: true\n")
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-django-positive.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(
            any("baseline_pass_ok_reason" in finding for finding in findings),
            findings,
        )

    def test_positive_implementation_answer_allows_baseline_pass_ok_with_reason(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-django-positive",
            coverage_tags=["implementation-django"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-django-positive.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\n"
            "case_role: implementation_supporting\n"
            "baseline_pass_ok_reason: baseline may satisfy reference-backed implementation behavior; delta is assessed as non-negative.\n"
            "coverage_tags:\n",
        )
        text = text.replace("  baseline_pass_ok: false\n", "  baseline_pass_ok: true\n")
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-django-positive.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertFalse(any("baseline_pass_ok_reason" in finding for finding in findings), findings)

    def test_answer_rejects_unknown_control_case_value(self) -> None:
        self.write_case_pair("source", "case-source-quality")
        answer_path = self.validator.EVAL_ROOT / "source/answer/case-source-quality.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "control_case: false",
            "control_case: maybe",
        )
        public_path = (
            self.validator.EVAL_ROOT
            / "source/cases/plugin/public/case-source-quality.md"
        )
        answer_path.write_text(text, encoding="utf-8")

        findings = self.validator.validate_answer(answer_path, "source", public_path)

        self.assertTrue(any("control_case must be one of" in finding for finding in findings))

    def test_bucket_requires_minimum_coverage_tags(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-only-one",
            coverage_tags=["specialist-positive"],
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(any("coverage_tags" in finding for finding in findings))

    def test_response_bucket_requires_architecture_db_p4_coverage_tags(self) -> None:
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | {
                "schema-modeling",
                "keys-cardinality-optionality",
                "constraints-indexes",
                "transaction-locking",
                "isolation-retry",
                "idempotency-storage",
                "duplicate-prevention",
                "query-performance",
                "operational-rollout",
                "migration-safety",
            }
        )
        self.write_case_pair("response", "case-response-db-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("architecture-db P4 direct coverage_tags missing" in finding for finding in findings),
            findings,
        )

    def test_response_bucket_excludes_mixed_answer_from_architecture_db_p4_coverage(self) -> None:
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | {"db-architecture", "mixed-boundary"}
        )
        self.write_case_pair("response", "case-response-order-create", coverage_tags=tags)
        answer = self.validator.EVAL_ROOT / "response/answer/case-response-order-create.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-db/reference/final.md\n"
                "    basis: DB architecture basis\n"
                "  - path: dddjango/skills/architecture-db/SKILL.md\n"
                "    basis: DB runtime basis\n",
            ),
            encoding="utf-8",
        )
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("architecture-db P4 direct coverage_tags missing" in finding for finding in findings),
            findings,
        )

    def test_response_bucket_requires_architecture_api_p4_coverage_tags(self) -> None:
        expected_api_tags = {
            "architecture-api",
            "rest-contract",
            "resource-url",
            "method-status",
            "problem-details",
            "auth-authz",
            "content-negotiation",
            "pagination",
            "versioning-deprecation",
            "rate-limit",
            "idempotency",
            "openapi-impact",
            "negative-architecture-api-boundary",
            "grpc-soap-boundary",
            "routing-boundary",
        }
        self.assertEqual(
            self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS,
            expected_api_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
        )
        self.write_case_pair("response", "case-response-db-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("architecture-api P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        for tag in expected_api_tags:
            self.assertTrue(any(tag in finding for finding in findings), tag)

    def test_response_bucket_requires_architecture_implementation_patterns_p4_coverage_tags(self) -> None:
        expected_pattern_tags = {
            "architecture-pattern-selection",
            "architecture-pattern-restraint",
            "implementation-patterns",
            "dependency-direction",
            "ports-adapters",
            "repository-uow",
            "cqrs-event-sourcing",
            "saga-outbox-acl",
            "service-layer",
            "risky-write-consistency",
            "overapplication-restraint",
            "routing-boundary",
        }
        self.assertEqual(
            self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS,
            expected_pattern_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | (expected_pattern_tags - {"service-layer"})
        )
        self.write_case_pair("response", "case-response-architecture-patterns", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any(
                "architecture-implementation-patterns P4 coverage_tags missing" in finding
                for finding in findings
            ),
            findings,
        )
        self.assertTrue(any("service-layer" in finding for finding in findings), findings)

    def test_response_bucket_requires_implementation_cleancode_p4_coverage_tags(self) -> None:
        expected_cleancode_tags = {
            "implementation-cleancode",
            "clean-code",
            "clean-code-exclusion",
            "maintainability",
            "review-refactor",
            "responsibility-separation",
            "naming",
            "function-shape",
            "encapsulation",
            "abstraction",
            "solid",
            "duplication-dry",
            "error-handling",
            "fat-model-review",
            "view-router-boundary",
            "fat-schema-boundary",
            "legacy-refactoring",
            "overapplication-restraint",
            "routing-boundary",
            "tiny-task-restraint",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS,
            expected_cleancode_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | (expected_cleancode_tags - {"function-shape"})
        )
        self.write_case_pair("response", "case-response-cleancode-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any(
                "implementation-cleancode P4 coverage_tags missing" in finding
                for finding in findings
            ),
            findings,
        )
        self.assertTrue(any("function-shape" in finding for finding in findings), findings)

    def test_response_bucket_requires_implementation_django_p4_coverage_tags(self) -> None:
        expected_django_tags = {
            "implementation-django",
            "django-model-orm",
            "queryset-manager",
            "service-selector",
            "django-transaction",
            "query-performance",
            "django-caching",
            "settings-security",
            "existing-drf-maintenance",
            "drf-adapter-boundary",
            "django-migration",
            "migration-safety",
            "django-implementation-restraint",
            "routing-boundary",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS,
            expected_django_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | (expected_django_tags - {"django-caching"})
        )
        self.write_case_pair("response", "case-response-django-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any(
                "implementation-django P4 coverage_tags missing" in finding
                for finding in findings
            ),
            findings,
        )
        self.assertTrue(any("django-caching" in finding for finding in findings), findings)

    def test_code_bucket_requires_implementation_django_p4_coverage_tags(self) -> None:
        expected_django_tags = {
            "code-implementation-django",
            "implementation-django",
            "django-model-orm",
            "queryset-manager",
            "service-selector",
            "django-transaction",
            "query-performance",
            "django-caching",
            "command-honesty",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS,
            expected_django_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["code"] - {"django-implementation"})
            | (expected_django_tags - {"query-performance"})
        )
        self.write_case_pair("code", "case-code-django-p4", coverage_tags=tags)

        _count, findings = self.validator.validate_bucket("code")

        self.assertTrue(
            any("implementation-django P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("query-performance" in finding for finding in findings), findings)

    def test_code_implementation_cleancode_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-fat-model",
            coverage_tags=["implementation-cleancode", "clean-code"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-fat-model.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT / "code/cases/plugin/public/case-code-fat-model.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-cleancode/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-cleancode/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("bundled implementation-cleancode reference" in finding for finding in findings),
            findings,
        )

    def test_code_implementation_cleancode_requires_semantic_terms(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-fat-model",
            coverage_tags=["implementation-cleancode", "clean-code"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-fat-model.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/code/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: workspace/reference/implementation-cleancode/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-cleancode/SKILL.md\n"
            "    basis: runtime\n"
            "  - path: dddjango/skills/implementation-cleancode/references/responsibility.md\n"
            "    basis: bundled\n",
        )
        text = text.replace(
            "target_behavior:\n"
            "  required:\n"
            "    - Required behavior.\n",
            "target_behavior:\n"
            "  required:\n"
            "    - Keeps status invariant local and understandable.\n",
        )
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT / "code/cases/plugin/public/case-code-fat-model.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(any("side-effect boundary" in finding for finding in findings), findings)
        self.assertTrue(any("regression tests" in finding for finding in findings), findings)
        self.assertTrue(any("overengineering restraint" in finding for finding in findings), findings)

    def test_neutral_code_cleancode_supporting_case_allows_baseline_pass(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-fat-model",
            coverage_tags=["implementation-cleancode", "clean-code"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-fat-model.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "reference_basis:\n"
            "  - path: workspace/develop/eval/code/eval_goal.md\n"
            "    basis: test basis\n",
            "reference_basis:\n"
            "  - path: workspace/reference/implementation-cleancode/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-cleancode/SKILL.md\n"
            "    basis: runtime\n"
            "  - path: dddjango/skills/implementation-cleancode/references/responsibility.md\n"
            "    basis: bundled\n",
        )
        text = text.replace(
            "target_behavior:\n"
            "  required:\n"
            "    - Required behavior.\n",
            "target_behavior:\n"
            "  required:\n"
            "    - Keeps status invariant local and understandable.\n"
            "    - Introduces a small side-effect boundary.\n"
            "    - Adds regression test coverage.\n"
            "    - Avoids repository/UoW/hexagonal overengineering.\n",
        )
        text = text.replace(
            "expected_outcomes:\n"
            "  baseline: partial\n"
            "  with_dddjango: pass\n"
            "  expected_delta: positive\n"
            "  baseline_pass_ok: false\n",
            "expected_outcomes:\n"
            "  baseline: pass\n"
            "  with_dddjango: pass\n"
            "  expected_delta: neutral\n"
            "  baseline_pass_ok: true\n",
        )
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT / "code/cases/plugin/public/case-code-fat-model.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertFalse(
            any("baseline_pass_ok true" in finding for finding in findings),
            findings,
        )

    def test_response_bucket_requires_implementation_django_ninja_p4_coverage_tags(self) -> None:
        expected_ninja_tags = {
            "implementation-django-ninja",
            "django-ninja-router",
            "schema-modelschema",
            "endpoint-adapter",
            "auth-permission",
            "filtering-sorting",
            "pagination",
            "problem-details",
            "openapi-impact",
            "testclient",
            "drf-to-ninja",
            "routing-boundary",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS,
            expected_ninja_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | (expected_ninja_tags - {"testclient"})
        )
        self.write_case_pair("response", "case-response-django-ninja-p4", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any(
                "implementation-django-ninja P4 coverage_tags missing" in finding
                for finding in findings
            ),
            findings,
        )
        self.assertTrue(any("testclient" in finding for finding in findings), findings)

    def test_response_bucket_requires_implementation_tdd_p4_direct_coverage(self) -> None:
        expected_tdd_tags = {
            "implementation-tdd",
            "tdd",
            "test-list",
            "failing-test-first",
            "red-green-refactor",
            "inside-out",
            "outside-in",
            "acceptance-unit-loop",
            "boundary-cases",
            "refactor-checkpoint",
            "state-verification",
            "behavior-verification",
            "mock-role",
            "bdd-atdd",
            "ai-assisted-tdd",
            "routing-boundary",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS,
            expected_tdd_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            | (expected_tdd_tags - {"mock-role"})
        )
        self.write_case_pair("response", "case-response-general-tags", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("implementation-tdd P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("mock-role" in finding for finding in findings), findings)

    def test_implementation_tdd_answer_requires_source_runtime_and_bundled_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-tdd-loop",
            coverage_tags=["implementation-tdd"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-tdd-loop.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-tdd-loop.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-tdd/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-tdd/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("red-green-refactor.md" in finding for finding in findings), findings)

    def test_implementation_tdd_direct_answer_accepts_source_backed_case(self) -> None:
        text = """id: case-response-tdd-loop-selection
case_id: case-response-tdd-loop-selection
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-tdd-loop-selection.md
intent: Validate implementation-tdd direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-tdd/reference/final.md
    basis: TDD source basis
  - path: dddjango/skills/implementation-tdd/SKILL.md
    basis: TDD runtime basis
  - path: dddjango/skills/implementation-tdd/references/test-list.md
    basis: test list bundled basis
  - path: dddjango/skills/implementation-tdd/references/red-green-refactor.md
    basis: Red-Green-Refactor bundled basis
  - path: dddjango/skills/implementation-tdd/references/inside-out-outside-in.md
    basis: approach and verification bundled basis
  - path: dddjango/skills/implementation-tdd/references/bdd-atdd.md
    basis: BDD ATDD bundled basis
  - path: dddjango/skills/implementation-tdd/references/ai-assisted-tdd.md
    basis: honesty bundled basis
target_behavior:
  required:
    - Starts with a test list covering behavior, policy, and risk.
    - Writes or proposes the first failing test and Red step before implementation.
    - Explains Red, Green, and Refactor order.
    - Chooses Inside-Out and Outside-In where appropriate.
    - Uses acceptance BDD ATDD outer loop and unit inner loop.
    - Covers boundary accepted and rejected examples.
    - Places a refactor checkpoint only while Green.
    - Uses state verification and output verification for domain results.
    - Uses behavior verification or communication checks for external roles.
    - Mocks gateway role or notifier role.
    - Hands BDD, ATDD, pytest-bdd, Gherkin, and implementation-test mechanics to the right owner.
    - Says no files, no commands, and tests were not run unless evidence exists.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-tdd
  - tdd
  - test-list
  - failing-test-first
  - red-green-refactor
  - inside-out
  - outside-in
  - acceptance-unit-loop
  - boundary-cases
  - refactor-checkpoint
  - state-verification
  - behavior-verification
  - mock-role
  - bdd-atdd
  - ai-assisted-tdd
  - routing-boundary
  - validation-honesty
"""

        self.assertTrue(self.validator.has_implementation_tdd_direct_coverage(text))
        findings = self.validator.validate_implementation_tdd_answer(self.root / "answer.yaml", text)

        self.assertEqual([], findings)

    def test_implementation_tdd_answer_rejects_required_term_omission(self) -> None:
        text = """id: case-response-tdd-loop-selection
case_id: case-response-tdd-loop-selection
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-tdd-loop-selection.md
intent: Validate implementation-tdd direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-tdd/reference/final.md
    basis: TDD source basis
  - path: dddjango/skills/implementation-tdd/SKILL.md
    basis: TDD runtime basis
  - path: dddjango/skills/implementation-tdd/references/test-list.md
    basis: test list bundled basis
  - path: dddjango/skills/implementation-tdd/references/red-green-refactor.md
    basis: Red-Green-Refactor bundled basis
  - path: dddjango/skills/implementation-tdd/references/inside-out-outside-in.md
    basis: approach and verification bundled basis
  - path: dddjango/skills/implementation-tdd/references/bdd-atdd.md
    basis: BDD ATDD bundled basis
  - path: dddjango/skills/implementation-tdd/references/ai-assisted-tdd.md
    basis: honesty bundled basis
target_behavior:
  required:
    - Starts with a test list covering behavior, policy, and risk.
    - Writes or proposes the first failing test and Red step before implementation.
    - Explains Red, Green, and Refactor order.
    - Chooses Inside-Out and Outside-In where appropriate.
    - Uses acceptance BDD ATDD outer loop and unit inner loop.
    - Covers boundary accepted and rejected examples.
    - Places a refactor checkpoint only while Green.
    - Uses state verification and output verification for domain results.
    - Uses behavior verification or communication checks for external roles.
    - Hands BDD, ATDD, pytest-bdd, Gherkin, and implementation-test mechanics to the right owner.
    - Says no files, no commands, and tests were not run unless evidence exists.
coverage_tags:
  - implementation-tdd
"""

        findings = self.validator.validate_implementation_tdd_answer(self.root / "answer.yaml", text)

        self.assertTrue(any("mock-role" in finding for finding in findings), findings)

    def test_code_bucket_requires_implementation_tdd_p4_coverage_tags(self) -> None:
        expected_tdd_tags = {
            "code-implementation-tdd",
            "implementation-tdd",
            "tdd",
            "test-implementation",
            "failing-test-first",
            "red-green-refactor",
            "boundary-cases",
            "state-verification",
            "domain-policy",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.CODE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS,
            expected_tdd_tags,
        )
        tags = sorted(
            self.validator.REQUIRED_COVERAGE_TAGS["code"]
            | self.validator.CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | self.validator.CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            | (expected_tdd_tags - {"failing-test-first"})
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-coupon-tdd.yaml"
        answer_path.parent.mkdir(parents=True, exist_ok=True)
        answer_path.write_text(
            "id: case-code-coupon-tdd\ncase_id: case-code-coupon-tdd\ncoverage_tags:\n"
            + "".join(f"  - {tag}\n" for tag in tags),
            encoding="utf-8",
        )

        findings = self.validator.validate_coverage("code", [answer_path])

        self.assertTrue(
            any("implementation-tdd P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("failing-test-first" in finding for finding in findings), findings)

    def test_code_implementation_tdd_answer_requires_hidden_behavior_check(self) -> None:
        self.write_case_pair(
            "code",
            "case-code-coupon-tdd",
            coverage_tags=["code-implementation-tdd", "implementation-tdd"],
        )
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-coupon-tdd.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-coupon-tdd.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(any("hidden coupon behavior_checks" in finding for finding in findings), findings)

    def test_response_bucket_requires_implementation_test_p4_direct_coverage(self) -> None:
        expected_test_tags = {
            "implementation-test",
            "pytest",
            "fixtures-conftest",
            "parametrization",
            "assertions",
            "test-doubles",
            "factory-boy-faker",
            "hypothesis-property",
            "time-http-mocking",
            "testcontainers",
            "coverage-mutation",
            "bdd",
            "flaky-tests",
            "django-ninja-testclient",
            "idempotency-concurrency",
            "routing-boundary",
            "validation-honesty",
        }
        self.assertEqual(
            self.validator.RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS,
            expected_test_tags,
        )
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS
            | (expected_test_tags - {"factory-boy-faker"})
        )
        self.write_case_pair("response", "case-response-general-tags", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("implementation-test P4 coverage_tags missing" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("factory-boy-faker" in finding for finding in findings), findings)

    def test_implementation_test_answer_requires_source_runtime_and_bundled_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-test-suite",
            coverage_tags=["implementation-test"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-test-suite.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-test-suite.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-test/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-test/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("django-api-concurrency.md" in finding for finding in findings), findings)

    def test_implementation_test_direct_answer_accepts_source_backed_case(self) -> None:
        text = self.implementation_test_direct_answer_text()

        self.assertTrue(self.validator.has_implementation_test_direct_coverage(text))
        findings = self.validator.validate_implementation_test_answer(self.root / "answer.yaml", text)

        self.assertEqual([], findings)

    def test_implementation_test_direct_answer_rejects_mixed_workflow_tags(self) -> None:
        for excluded_tag in ("mixed-boundary", "role-map-sync", "subagent-opt-out"):
            with self.subTest(excluded_tag=excluded_tag):
                self.assertFalse(
                    self.validator.has_implementation_test_direct_coverage(
                        self.implementation_test_direct_answer_text(extra_tag=excluded_tag)
                    )
                )

    def test_response_bucket_requires_implementation_test_exclusion_case(self) -> None:
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS
        )
        self.write_case_pair("response", "case-response-test-suite-strategy", coverage_tags=tags)
        answer = self.validator.EVAL_ROOT / "response/answer/case-response-test-suite-strategy.yaml"
        answer.write_text(
            answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/reference/implementation-test/reference/final.md\n"
                "    basis: test implementation source basis\n"
                "  - path: dddjango/skills/implementation-test/SKILL.md\n"
                "    basis: runtime basis\n"
                "  - path: dddjango/skills/implementation-test/references/pytest-fixtures.md\n"
                "    basis: pytest and fixtures\n"
                "  - path: dddjango/skills/implementation-test/references/test-doubles.md\n"
                "    basis: doubles\n"
                "  - path: dddjango/skills/implementation-test/references/factories-property-tests.md\n"
                "    basis: factories and property tests\n"
                "  - path: dddjango/skills/implementation-test/references/coverage-mutation.md\n"
                "    basis: coverage and mutation\n"
                "  - path: dddjango/skills/implementation-test/references/django-api-concurrency.md\n"
                "    basis: API and concurrency tests\n",
            ).replace(
                "target_behavior:\n  required:\n    - Required behavior.\n",
                "target_behavior:\n"
                "  required:\n"
                "    - Routes as direct implementation-test guidance.\n"
                "    - Pytest file placement and conftest setup are covered.\n"
                "    - Shared and nested fixture choices are explicit.\n"
                "    - Parametrization covers boundary examples.\n"
                "    - Assertion choices include pytest.raises and pytest.approx.\n"
                "    - Test double selection uses fake and mock for external adapter roles.\n"
                "    - Factory and Faker setup are used only when they clarify data.\n"
                "    - Hypothesis property tests protect invariant behavior.\n"
                "    - Time and HTTP mocking happen at adapter boundaries.\n"
                "    - Testcontainers are justified for PostgreSQL lock isolation and constraint behavior.\n"
                "    - Coverage and mutation are treated as signal rather than proof.\n"
                "    - BDD pytest-bdd is limited to stakeholder readable scenarios.\n"
                "    - Flaky concurrency tests use barrier lock timeout and avoid arbitrary sleeps.\n"
                "    - TestClient covers public API contract behavior.\n"
                "    - Idempotency concurrency replay and conflict checks are required.\n"
                "    - Reporting claims only executed runs with evidence.\n"
                "  forbidden:\n"
                "    - Replacing the testing answer with workflow, subagent, DDD, DB, or API ownership.\n",
            ),
            encoding="utf-8",
        )
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("implementation-test exclusion coverage missing" in finding for finding in findings),
            findings,
        )

    def test_implementation_test_exclusion_coverage_accepts_tiny_case(self) -> None:
        text = """id: case-response-test-tiny-assertion
case_id: case-response-test-tiny-assertion
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-test-tiny-assertion.md
intent: Validate implementation-test exclusion.
reference_basis:
  - path: dddjango/skills/implementation-test/SKILL.md
    basis: runtime basis
  - path: dddjango/skills/implementation-test/references/pytest-fixtures.md
    basis: assertion basis
coverage_tags:
  - implementation-test-exclusion
  - pytest-assertion
  - tiny-task-restraint
  - routing-boundary
  - validation-honesty
"""

        self.assertTrue(self.validator.has_implementation_test_exclusion_coverage(text))

    def test_implementation_test_answer_does_not_count_forbidden_text_as_required(self) -> None:
        text = self.implementation_test_direct_answer_text().replace(
            "    - Factory and Faker setup are used only when they clarify data.\n",
            "",
        )

        findings = self.validator.validate_implementation_test_answer(self.root / "answer.yaml", text)

        self.assertTrue(
            any("factory/faker" in finding and "factory" in finding for finding in findings),
            findings,
        )

    def test_implementation_test_exclusion_requires_ceremony_terms_in_forbidden_block(self) -> None:
        text = """id: case-response-test-tiny-assertion
case_id: case-response-test-tiny-assertion
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-test-tiny-assertion.md
intent: Validate implementation-test exclusion.
reference_basis:
  - path: dddjango/skills/implementation-test/SKILL.md
    basis: runtime basis
  - path: dddjango/skills/implementation-test/references/pytest-fixtures.md
    basis: assertion basis
target_behavior:
  required:
    - Answers briefly and directly with pytest.approx approximate assertion guidance while saying fixture and workflow are unnecessary.
  forbidden:
    - Giving a broad response.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: negative
expected_outcomes:
  baseline: pass
  with_dddjango: pass
  expected_delta: non-negative
  baseline_pass_ok: true
coverage_tags:
  - implementation-test-exclusion
"""

        findings = self.validator.validate_implementation_test_answer(self.root / "answer.yaml", text)

        self.assertTrue(
            any("forbid test/workflow ceremony" in finding for finding in findings),
            findings,
        )

    def implementation_test_direct_answer_text(self, *, extra_tag: str | None = None) -> str:
        extra_line = f"  - {extra_tag}\n" if extra_tag else ""
        return f"""id: case-response-test-suite-strategy
case_id: case-response-test-suite-strategy
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-test-suite-strategy.md
intent: Validate implementation-test direct response coverage.
reference_basis:
  - path: workspace/reference/implementation-test/reference/final.md
    basis: test implementation source basis
  - path: dddjango/skills/implementation-test/SKILL.md
    basis: runtime basis
  - path: dddjango/skills/implementation-test/references/pytest-fixtures.md
    basis: pytest and fixtures
  - path: dddjango/skills/implementation-test/references/test-doubles.md
    basis: doubles
  - path: dddjango/skills/implementation-test/references/factories-property-tests.md
    basis: factories and property tests
  - path: dddjango/skills/implementation-test/references/coverage-mutation.md
    basis: coverage and mutation
  - path: dddjango/skills/implementation-test/references/django-api-concurrency.md
    basis: API and concurrency tests
target_behavior:
  required:
    - Routes as direct implementation-test guidance and rejects workflow subagent DDD DB API ownership.
    - Pytest file placement and conftest setup are covered.
    - Shared and nested fixture choices are explicit.
    - Parametrization covers boundary examples.
    - Assertion choices include pytest.raises and pytest.approx.
    - Test double selection uses fake and mock for external adapter roles.
    - Factory and Faker setup are used only when they clarify data.
    - Hypothesis property tests protect invariant behavior.
    - Time and HTTP mocking happen at adapter boundaries.
    - Testcontainers are justified for PostgreSQL lock isolation and constraint behavior.
    - Coverage and mutation are treated as signal rather than proof.
    - BDD pytest-bdd is limited to stakeholder readable scenarios.
    - Flaky concurrency tests use barrier lock timeout and avoid arbitrary sleeps.
    - TestClient covers public API contract behavior.
    - Idempotency concurrency replay and conflict checks are required.
    - Reporting claims only executed runs with evidence.
  forbidden:
    - Replacing the testing answer with workflow, subagent, DDD, DB, or API ownership.
scoring_checks:
  - pass if checked.
hard_gates:
  - no evaluator-only material leaks.
failure_modes:
  - missing behavior
leakage_checks:
  - no private material
evidence_required:
  - evaluation notes
control_case: false
expected_outcomes:
  baseline: partial
  with_dddjango: pass
  expected_delta: positive
  baseline_pass_ok: false
coverage_tags:
  - implementation-test
  - pytest
  - fixtures-conftest
  - parametrization
  - assertions
  - test-doubles
  - factory-boy-faker
  - hypothesis-property
  - time-http-mocking
  - testcontainers
  - coverage-mutation
  - bdd
  - flaky-tests
  - django-ninja-testclient
  - idempotency-concurrency
  - routing-boundary
  - validation-honesty
{extra_line}"""

    def test_implementation_django_ninja_answer_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django-ninja",
            coverage_tags=["implementation-django-ninja"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-django-ninja.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django-ninja.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-django-ninja/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-django-ninja/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("bundled implementation-django-ninja reference" in finding for finding in findings),
            findings,
        )
        self.assertTrue(any("router" in finding for finding in findings), findings)

    def test_implementation_django_ninja_required_terms_ignore_forbidden_text(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django-ninja",
            coverage_tags=["implementation-django-ninja"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-django-ninja.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: workspace/reference/implementation-django-ninja/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-django-ninja/SKILL.md\n"
            "    basis: runtime\n"
            "  - path: dddjango/skills/implementation-django-ninja/references/router-schema.md\n"
            "    basis: bundled\n",
        )
        text = text.replace(
            "target_behavior:\n"
            "  required:\n"
            "    - Required behavior.\n",
            "target_behavior:\n"
            "  required:\n"
            "    - Router and Schema behavior is required.\n"
            "  forbidden:\n"
            "    - Do not treat DRF compatibility, OpenAPI, Problem Details, TestClient, filtering, sorting, pagination, auth, or permission as optional.\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django-ninja.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("auth" in finding for finding in findings), findings)
        self.assertTrue(any("filtering" in finding for finding in findings), findings)
        self.assertTrue(any("pagination" in finding for finding in findings), findings)
        self.assertTrue(any("openapi" in finding for finding in findings), findings)

    def test_response_bucket_requires_single_direct_implementation_django_ninja_case(self) -> None:
        tags = sorted(
            (self.validator.REQUIRED_COVERAGE_TAGS["response"] - {"architecture-ddd-direct"})
            | self.validator.RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS
            | self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
        )
        self.write_case_pair("response", "case-response-general-tags", coverage_tags=tags)
        self.write_case_pair(
            "response",
            "case-response-ddd-direct",
            coverage_tags=["architecture-ddd-direct"],
        )
        ddd_answer = self.validator.EVAL_ROOT / "response/answer/case-response-ddd-direct.yaml"
        ddd_answer.write_text(
            ddd_answer.read_text(encoding="utf-8").replace(
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n",
                "  - path: workspace/develop/eval/response/eval_goal.md\n"
                "    basis: test basis\n"
                "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
                "    basis: DDD direct response basis\n",
            )
            + """ddd_observations:
  business_problem: order consistency
  subdomain_type: core
  subdomain_type_basis: central business rule
  bounded_context: orders
  context_map_or_not_applicable: not applicable
  ubiquitous_terms: order
  aggregate_candidates: Order
  entity_or_value_object: Order entity
  invariants: protect order consistency
  domain_event_or_service: domain service not required
  use_cases: place order
  consistency_boundary: one aggregate
  implementation_restraint: no code required
""",
            encoding="utf-8",
        )

        _count, findings = self.validator.validate_bucket("response")

        self.assertTrue(
            any("one direct implementation-django-ninja answer" in finding for finding in findings),
            findings,
        )

    def test_django_ninja_direct_coverage_requires_case_id_prefix(self) -> None:
        tag_lines = "".join(
            f"  - {tag}\n"
            for tag in sorted(
                self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            )
        )
        text = f"""id: case-response-general-tags
case_id: case-response-general-tags
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-general-tags.md
intent: Validate Django Ninja tags are not enough without direct case identity.
reference_basis:
  - path: workspace/reference/implementation-django-ninja/reference/final.md
    basis: source
  - path: dddjango/skills/implementation-django-ninja/SKILL.md
    basis: runtime
  - path: dddjango/skills/implementation-django-ninja/references/router-schema.md
    basis: bundled
target_behavior:
  required:
    - Router, Schema, auth, filtering, pagination, Problem Details, OpenAPI, TestClient, DRF migration, and compatibility are covered.
coverage_tags:
{tag_lines}"""

        self.assertFalse(self.validator.has_implementation_django_ninja_direct_coverage(text))
        self.assertTrue(
            self.validator.has_implementation_django_ninja_direct_coverage(
                text.replace(
                    "case-response-general-tags",
                    "case-response-django-ninja-endpoint",
                )
            )
        )

    def test_django_ninja_direct_coverage_rejects_p5_workflow_tags(self) -> None:
        tag_lines = "".join(
            f"  - {tag}\n"
            for tag in sorted(
                self.validator.RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            )
        )
        text = f"""id: case-response-django-ninja-endpoint
case_id: case-response-django-ninja-endpoint
bucket: response
kind: response
public_case: workspace/develop/eval/response/cases/plugin/public/case-response-django-ninja-endpoint.md
intent: Validate Django Ninja direct coverage excludes workflow and subagent scenarios.
reference_basis:
  - path: workspace/reference/implementation-django-ninja/reference/final.md
    basis: source
  - path: dddjango/skills/implementation-django-ninja/SKILL.md
    basis: runtime
  - path: dddjango/skills/implementation-django-ninja/references/router-schema.md
    basis: bundled
target_behavior:
  required:
    - Router, Schema, ModelSchema, auth, permission, filtering, sorting, pagination, Problem Details, OpenAPI, TestClient, DRF migration, and compatibility are covered.
coverage_tags:
{tag_lines}  - workflow
"""

        self.assertFalse(self.validator.has_implementation_django_ninja_direct_coverage(text))

    def test_implementation_django_ninja_required_terms_require_paired_dimensions(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django-ninja",
            coverage_tags=["implementation-django-ninja"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-django-ninja.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: workspace/reference/implementation-django-ninja/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-django-ninja/SKILL.md\n"
            "    basis: runtime\n"
            "  - path: dddjango/skills/implementation-django-ninja/references/router-schema.md\n"
            "    basis: bundled\n",
        )
        text = text.replace(
            "target_behavior:\n"
            "  required:\n"
            "    - Required behavior.\n",
            "target_behavior:\n"
            "  required:\n"
            "    - Router Schema auth filter pagination Problem Details OpenAPI TestClient DRF migration compatibility are covered.\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django-ninja.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("schema-modelschema" in finding for finding in findings), findings)
        self.assertTrue(any("auth-permission" in finding for finding in findings), findings)
        self.assertTrue(any("filtering-sorting" in finding for finding in findings), findings)

    def test_implementation_django_answer_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django",
            coverage_tags=["implementation-django"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-django.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-django/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-django/SKILL.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("bundled implementation-django reference" in finding for finding in findings),
            findings,
        )

    def test_implementation_django_drf_answer_requires_adapter_terms(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-django-drf",
            coverage_tags=["implementation-django", "existing-drf-maintenance"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-django-drf.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: workspace/reference/implementation-django/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-django/SKILL.md\n"
            "    basis: runtime\n"
            "  - path: dddjango/skills/implementation-django/references/coding-style-drf-maintenance.md\n"
            "    basis: bundled\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-django-drf.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("adapter" in finding for finding in findings), findings)
        self.assertTrue(any("serializer" in finding for finding in findings), findings)

    def test_response_cleancode_answer_requires_source_and_runtime_basis(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-cleancode",
            coverage_tags=["implementation-cleancode"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-cleancode.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-cleancode.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/implementation-cleancode/reference/final.md" in finding for finding in findings),
            findings,
        )
        self.assertTrue(
            any("dddjango/skills/implementation-cleancode/SKILL.md" in finding for finding in findings),
            findings,
        )

    def test_response_broad_cleancode_answer_requires_semantic_breadth(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-cleancode-broad",
            coverage_tags=["implementation-cleancode", "function-shape"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-cleancode-broad.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: workspace/reference/implementation-cleancode/reference/final.md\n"
            "    basis: source\n"
            "  - path: dddjango/skills/implementation-cleancode/SKILL.md\n"
            "    basis: runtime\n",
        )
        text = text.replace(
            "target_behavior:\n"
            "  required:\n"
            "    - Required behavior.\n",
            "target_behavior:\n"
            "  required:\n"
            "    - Leads with review findings and responsibility boundary comments.\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-cleancode-broad.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("naming, name" in finding for finding in findings), findings)
        self.assertTrue(any("function, argument, side effect" in finding for finding in findings), findings)

    def test_response_cleancode_exclusion_requires_direct_handling(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-cleancode-exclusion",
            coverage_tags=["clean-code-exclusion"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-cleancode-exclusion.yaml"
        text = answer_path.read_text(encoding="utf-8").replace(
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "  - path: dddjango/skills/implementation-cleancode/SKILL.md\n"
            "    basis: exclusion basis\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-cleancode-exclusion.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("brief direct handling" in finding for finding in findings),
            findings,
        )

    def test_workflow_answer_requires_execution_expectation(self) -> None:
        self.write_case_pair(
            "workflow",
            "case-workflow-one",
            coverage_tags=[
                "positive-composite",
                "review-focused",
                "handoff-contract",
                "risky-write-consistency",
                "role-map-sync",
                "delegation-honesty",
                "sequential-fallback",
                "subagent-opt-out",
                "tiny-task-restraint",
                "false-claim",
                "integration-closure",
            ],
        )
        answer_path = self.validator.EVAL_ROOT / "workflow/answer/case-workflow-one.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "workflow/cases/plugin/public/case-workflow-one.md"
        )

        findings = self.validator.validate_answer(answer_path, "workflow", public_path)

        self.assertTrue(
            any("workflow_execution_expectation" in finding for finding in findings)
        )

    def test_workflow_execution_expectation_rejects_mode_overlap(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - sequential_fallback
  decision_rule: Use fallback.
  responsibility_rule: Preserve role order.
  report_label: fallback required
"""

        findings = self.validator.validate_workflow_execution_expectation(path, text)

        self.assertTrue(any("overlap" in finding for finding in findings))

    def test_workflow_execution_expectation_rejects_unknown_machine_modes(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
workflow_execution_expectation:
  expected_mode: sequential_fallback_required
  acceptable_modes:
    - sequential_fallback
  forbidden_modes:
    - actual_subagent
    - wrong_order
  decision_rule: Use fallback.
  responsibility_rule: Preserve role order.
  report_label: fallback required
"""

        findings = self.validator.validate_workflow_execution_expectation(path, text)

        self.assertTrue(any("unknown machine mode" in finding for finding in findings))

    def test_p5_subagent_trace_expectation_rejects_missing_or_not_run_modes(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
workflow_execution_expectation:
  expected_mode: actual_subagent_required
  acceptable_modes:
    - actual_subagent
    - trace_missing
    - not_run
  forbidden_modes:
    - false_actual_claim
  decision_rule: Use real subagents.
  responsibility_rule: Preserve result collection evidence.
  report_label: actual subagents
coverage_tags:
  - actual-subagent-required
  - actual-subagent-trace
"""

        findings = self.validator.validate_workflow_execution_expectation(path, text)

        self.assertTrue(
            any("must not accept missing/not-run trace modes" in finding for finding in findings),
            findings,
        )

    def test_known_p5_restraint_case_requires_scope(self) -> None:
        self.write_case_pair(
            "workflow",
            "case-workflow-tiny-restraint",
            coverage_tags=["p5-plugin-restraint", "tiny-task-restraint"],
        )
        answer_path = (
            self.validator.EVAL_ROOT
            / "workflow/answer/case-workflow-tiny-restraint.yaml"
        )

        findings = self.validator.validate_restraint_scope(
            answer_path,
            answer_path.read_text(encoding="utf-8"),
        )

        self.assertTrue(any("restraint_scope" in finding for finding in findings), findings)

    def test_p5_restraint_tag_requires_plugin_level_scope(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
case_id: case-response-simple-rename
restraint_scope: individual-skill
coverage_tags:
  - p5-plugin-restraint
  - simple-negative
"""

        findings = self.validator.validate_restraint_scope(path, text)

        self.assertTrue(
            any("p5-plugin-restraint coverage requires" in finding for finding in findings),
            findings,
        )

    def test_individual_skill_restraint_scope_accepts_p4_case(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
case_id: case-response-simple-rename
restraint_scope: individual-skill
coverage_tags:
  - simple-negative
  - overapplication-restraint
"""

        findings = self.validator.validate_restraint_scope(path, text)

        self.assertEqual([], findings)

    def test_plugin_answer_validates_optional_workflow_execution_expectation(self) -> None:
        self.write_case_pair(
            "plugin",
            "case-plugin-one",
            coverage_tags=["trigger-quality"],
            extra_answer=(
                "workflow_execution_expectation:\n"
                "  expected_mode: sequential_fallback_required\n"
                "  acceptable_modes:\n"
                "    - sequential_fallback\n"
                "  forbidden_modes:\n"
                "    - sequential_fallback\n"
                "  decision_rule: Use fallback.\n"
                "  responsibility_rule: Preserve result honesty.\n"
                "  report_label: fallback required\n"
            ),
        )
        answer_path = self.validator.EVAL_ROOT / "plugin/answer/case-plugin-one.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "plugin/cases/plugin/public/case-plugin-one.md"
        )

        findings = self.validator.validate_answer(answer_path, "plugin", public_path)

        self.assertTrue(any("overlap" in finding for finding in findings))

    def test_plugin_p5_workflow_integrity_requires_execution_expectation(self) -> None:
        self.write_case_pair(
            "plugin",
            "case-plugin-p5-workflow",
            coverage_tags=["p5-workflow-integrity"],
        )
        answer_path = self.validator.EVAL_ROOT / "plugin/answer/case-plugin-p5-workflow.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "plugin/cases/plugin/public/case-plugin-p5-workflow.md"
        )

        findings = self.validator.validate_answer(answer_path, "plugin", public_path)

        self.assertTrue(
            any("must declare workflow_execution_expectation" in finding for finding in findings)
        )

    def test_plugin_p5_restraint_trigger_routing_requires_specific_dimensions(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
case_id: case-plugin-trigger-routing
restraint_scope: plugin-level
target_behavior:
  required:
    - Reviews frontmatter description and positive/negative routing.
coverage_tags:
  - p5-plugin-restraint
  - trigger-quality
"""

        findings = self.validator.validate_plugin_governance_answer(path, text)

        self.assertTrue(any("opt-out restraint" in finding for finding in findings), findings)
        self.assertTrue(any("Direct Answer Mode" in finding for finding in findings), findings)
        self.assertTrue(any("no meta-tail restraint" in finding for finding in findings), findings)

    def test_plugin_p5_restraint_trigger_routing_accepts_specific_dimensions(self) -> None:
        path = self.root / "answer.yaml"
        text = """\
case_id: case-plugin-trigger-routing
restraint_scope: plugin-level
target_behavior:
  required:
    - Reviews frontmatter description, positive and negative routing, Korean trigger terms, and body-only trigger rules.
    - Checks opt-out restraint, tiny edit restraint, Direct Answer Mode, false-claim refusal, no meta-tail restraint, and trigger/routing surface visibility.
coverage_tags:
  - p5-plugin-restraint
  - trigger-quality
"""

        findings = self.validator.validate_plugin_governance_answer(path, text)

        self.assertEqual([], findings)

    def test_runtime_missing_metadata_requires_validation_output_evidence(self) -> None:
        self.write_case_pair(
            "runtime",
            "case-runtime-missing-metadata",
            coverage_tags=["missing-skill-metadata"],
        )
        answer_path = self.validator.EVAL_ROOT / "runtime/answer/case-runtime-missing-metadata.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "runtime/cases/plugin/public/case-runtime-missing-metadata.md"
        )

        findings = self.validator.validate_answer(answer_path, "runtime", public_path)

        self.assertTrue(
            any("validation command output" in finding for finding in findings)
        )
        self.assertTrue(any("semantic metadata alignment" in finding for finding in findings))

    def test_code_ddd_case_requires_ddd_observations(self) -> None:
        self.write_case_pair("code", "case-code-ddd", coverage_tags=["ddd-to-code"])
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-ddd.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace("coverage_tags:\n", "code_expected: true\ncase_role: ddd_direct\ncoverage_tags:\n")
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-ddd.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(any("ddd_observations" in finding for finding in findings))

    def test_code_ddd_case_requires_architecture_reference(self) -> None:
        self.write_case_pair("code", "case-code-ddd", coverage_tags=["ddd-to-code"])
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-ddd.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "reference_basis:\n"
            "  - path: workspace/develop/eval/code/eval_goal.md\n"
            "    basis: test basis\n",
            "reference_basis:\n"
            "  - path: workspace/reference/source-reference-audit/reference/final.md\n"
            "    basis: source governance\n",
        )
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\n"
            "case_role: ddd_direct\n"
            "ddd_observations:\n"
            "  business_problem: place orders\n"
            "  subdomain_type: core\n"
            "  subdomain_type_basis: order placement owns business rules\n"
            "  bounded_context: ordering\n"
            "  context_map_or_not_applicable: not applicable for single context\n"
            "  ubiquitous_terms: Order, OrderLine\n"
            "  aggregate_root: Order\n"
            "  aggregate_behavior: place and confirm\n"
            "  invariants:\n"
            "    - an order cannot be placed without items\n"
            "  application_service_boundary: service coordinates repository and transaction\n"
            "  transaction_boundary: application service owns transaction\n"
            "  django_mapping: pure Python fixture\n"
            "  test_evidence: unit tests cover invariants\n"
            "coverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-ddd.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertTrue(
            any("workspace/reference/architecture-ddd/reference/final.md" in finding for finding in findings)
        )

    def test_code_supporting_domain_policy_case_does_not_require_ddd_observations(self) -> None:
        self.write_case_pair("code", "case-code-coupon", coverage_tags=["domain-policy"])
        answer_path = self.validator.EVAL_ROOT / "code/answer/case-code-coupon.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "coverage_tags:\n",
            "code_expected: true\ncase_role: implementation_supporting\ncoverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "code/cases/plugin/public/case-code-coupon.md"
        )

        findings = self.validator.validate_answer(answer_path, "code", public_path)

        self.assertFalse(any("ddd_observations" in finding for finding in findings))

    def test_response_ddd_direct_case_requires_ddd_observations(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-ddd",
            coverage_tags=["architecture-ddd-direct"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-ddd.yaml"
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-ddd.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("ddd_observations" in finding for finding in findings))

    def test_response_ddd_direct_case_requires_architecture_reference(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-ddd",
            coverage_tags=["architecture-ddd-direct"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-ddd.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "reference_basis:\n"
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "reference_basis:\n"
            "  - path: workspace/reference/source-reference-audit/reference/final.md\n"
            "    basis: source governance\n",
        )
        text = text.replace(
            "coverage_tags:\n",
            "ddd_observations:\n"
            "  business_problem: subscription lifecycle\n"
            "  subdomain_type: core\n"
            "  subdomain_type_basis: lifecycle rules affect revenue\n"
            "  bounded_context: subscription\n"
            "  context_map_or_not_applicable: billing is upstream boundary\n"
            "  ubiquitous_terms: Subscription, Entitlement\n"
            "  aggregate_candidates: Subscription\n"
            "  entity_or_value_object: Subscription entity and TrialPeriod value object\n"
            "  invariants: paid conversion requires payment success\n"
            "  domain_event_or_service: SubscriptionConvertedToPaid event\n"
            "  use_cases: start trial\n"
            "  consistency_boundary: subscription aggregate boundary\n"
            "  implementation_restraint: no Django/API implementation in DDD-only answer\n"
            "coverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-ddd.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(
            any("workspace/reference/architecture-ddd/reference/final.md" in finding for finding in findings)
        )

    def test_response_ddd_direct_case_requires_each_observation_field(self) -> None:
        self.write_case_pair(
            "response",
            "case-response-ddd",
            coverage_tags=["architecture-ddd-direct"],
        )
        answer_path = self.validator.EVAL_ROOT / "response/answer/case-response-ddd.yaml"
        text = answer_path.read_text(encoding="utf-8")
        text = text.replace(
            "reference_basis:\n"
            "  - path: workspace/develop/eval/response/eval_goal.md\n"
            "    basis: test basis\n",
            "reference_basis:\n"
            "  - path: workspace/reference/architecture-ddd/reference/final.md\n"
            "    basis: DDD source\n",
        )
        text = text.replace(
            "coverage_tags:\n",
            "ddd_observations:\n"
            "  business_problem: subscription lifecycle\n"
            "  subdomain_type: core\n"
            "  subdomain_type_basis: lifecycle rules affect revenue\n"
            "  bounded_context: subscription\n"
            "  context_map_or_not_applicable: billing is upstream boundary\n"
            "  ubiquitous_terms: Subscription, Entitlement\n"
            "  aggregate_candidates: Subscription\n"
            "  entity_or_value_object: Subscription entity and TrialPeriod value object\n"
            "  invariants: paid conversion requires payment success\n"
            "  use_cases: start trial\n"
            "  consistency_boundary: subscription aggregate boundary\n"
            "  implementation_restraint: no Django/API implementation in DDD-only answer\n"
            "coverage_tags:\n",
        )
        answer_path.write_text(text, encoding="utf-8")
        public_path = (
            self.validator.EVAL_ROOT
            / "response/cases/plugin/public/case-response-ddd.md"
        )

        findings = self.validator.validate_answer(answer_path, "response", public_path)

        self.assertTrue(any("domain_event_or_service" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
