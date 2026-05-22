#!/usr/bin/env python3
"""Validate dddjango eval bucket case/answer packs.

This is a structural and contamination validator for buckets that do not yet
have a full model-run harness. It intentionally does not score model quality.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import workflow_execution_gate as workflow_gate
import eval_answer_yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = REPO_ROOT / "workspace/develop/eval"
BUCKETS = ("response", "code", "plugin", "runtime", "source", "workflow")
REQUIRED_FIELDS = (
    "id",
    "case_id",
    "bucket",
    "kind",
    "public_case",
    "intent",
    "reference_basis",
    "target_behavior",
    "scoring_checks",
    "hard_gates",
    "failure_modes",
    "leakage_checks",
    "evidence_required",
    "control_case",
    "expected_outcomes",
    "coverage_tags",
)
ANSWER_ONLY_PUBLIC_PATTERNS = {
    "answer field: reference_basis": re.compile(r"(?<![A-Za-z0-9_])reference_basis(?![A-Za-z0-9_])"),
    "answer field: target_behavior": re.compile(r"(?<![A-Za-z0-9_])target_behavior(?![A-Za-z0-9_])"),
    "answer field: scoring_checks": re.compile(r"(?<![A-Za-z0-9_])scoring_checks(?![A-Za-z0-9_])"),
    "answer field: hard_gates": re.compile(r"(?<![A-Za-z0-9_])hard_gates(?![A-Za-z0-9_])"),
    "answer field: failure_modes": re.compile(r"(?<![A-Za-z0-9_])failure_modes(?![A-Za-z0-9_])"),
    "answer field: leakage_checks": re.compile(r"(?<![A-Za-z0-9_])leakage_checks(?![A-Za-z0-9_])"),
    "answer field: evidence_required": re.compile(r"(?<![A-Za-z0-9_])evidence_required(?![A-Za-z0-9_])"),
    "answer field: control_case": re.compile(r"(?<![A-Za-z0-9_])control_case(?![A-Za-z0-9_])"),
    "answer field: expected_outcomes": re.compile(r"(?<![A-Za-z0-9_])expected_outcomes(?![A-Za-z0-9_])"),
    "answer field: coverage_tags": re.compile(r"(?<![A-Za-z0-9_])coverage_tags(?![A-Za-z0-9_])"),
    "answer field: case_id": re.compile(r"\bcase_id\s*:"),
    "answer field: with_dddjango": re.compile(r"(?<![A-Za-z0-9_])with_dddjango(?![A-Za-z0-9_])"),
    "answer oracle wording": re.compile(r"\banswer oracle\b", re.I),
    "Korean private answer wording": re.compile(r"비공개\s*정답|정답\s*파일"),
    "absolute repo path": re.compile(re.escape(str(REPO_ROOT))),
}
LOCAL_HOME_DIRS = ("Users", "home")
ABSOLUTE_LOCAL_PATH = re.compile(
    r"(?m)^\s*(?:-\s*)?path\s*:\s*/(?:" + "|".join(LOCAL_HOME_DIRS) + r")/"
)
LIST_FIELDS = (
    "scoring_checks",
    "hard_gates",
    "failure_modes",
    "leakage_checks",
    "evidence_required",
    "coverage_tags",
)
CONTROL_CASE_VALUES = {
    "false",
    "restraint",
    "negative",
    "honesty",
    "safety",
}
EXPECTED_OUTCOME_FIELDS = (
    "baseline",
    "with_dddjango",
    "expected_delta",
    "baseline_pass_ok",
)
WORKFLOW_EXPECTATION_REQUIRED_FIELDS = (
    "expected_mode",
    "acceptable_modes",
    "forbidden_modes",
    "decision_rule",
    "responsibility_rule",
    "report_label",
)
REQUIRED_COVERAGE_TAGS = {
    "response": {
        "architecture-ddd-direct",
        "specialist-positive",
        "mixed-boundary",
        "ambiguity",
        "prompt-injection",
        "eval-leakage",
        "simple-negative",
        "false-claim",
        "validation-honesty",
    },
    "code": {
        "ddd-to-code",
        "django-implementation",
        "django-ninja-api",
        "db-consistency",
        "tdd",
        "test-implementation",
        "python-typing",
        "django-web",
        "negative-implementation-restraint",
        "no-code",
        "clarification",
        "command-honesty",
    },
    "plugin": {
        "p5-plugin-restraint",
        "trigger-quality",
        "routing-boundary",
        "progressive-disclosure",
        "runtime-reference-split",
        "provisional-handling",
        "agents-metadata",
        "packaging",
        "marketplace-sync",
        "leaked-answer-text",
        "cache-source-consistency",
        "runtime-safety",
    },
    "runtime": {
        "prompt-input-exposure",
        "baseline-isolation",
        "stale-cache",
        "missing-skill-metadata",
        "wrong-routing",
        "private-material-request",
        "answer-leakage-sentinel",
        "role-map-sync",
    },
    "source": {
        "docs-coherence",
        "source-provenance",
        "conflict-gap-decision",
        "provisional-handling",
        "drf-guardrail",
        "validation-coverage",
        "eval-traceability",
        "boundary-protection",
        "runtime-metadata-cache-sync",
        "source-audit-exclusion",
    },
    "workflow": {
        "p5-plugin-restraint",
        "positive-composite",
        "review-focused",
        "handoff-contract",
        "risky-write-consistency",
        "role-map-sync",
        "delegation-honesty",
        "consent-gate",
        "actual-subagent-trace",
        "actual-subagent-required",
        "sequential-fallback",
        "subagent-opt-out",
        "tiny-task-restraint",
        "direct-answer-shape",
        "meta-tail-restraint",
        "critical-path-restraint",
        "parallel-ownership",
        "responsibility-split",
        "false-claim",
        "cache-sync-report",
        "validation-sharing",
        "integration-closure",
    },
}
RESTRAINT_SCOPE_VALUES = {
    "plugin-level",
    "individual-skill",
    "supporting-control",
}
RESTRAINT_SCOPE_EXPECTATIONS = {
    "case-workflow-opt-out": "plugin-level",
    "case-workflow-tiny-restraint": "plugin-level",
    "case-workflow-design-no-meta-tail": "plugin-level",
    "case-workflow-critical-path-delegation-restraint": "plugin-level",
    "case-workflow-false-claim": "plugin-level",
    "case-plugin-trigger-routing": "plugin-level",
    "case-response-false-claim": "plugin-level",
    "case-response-simple-rename": "individual-skill",
    "case-response-architecture-pattern-restraint": "individual-skill",
    "case-response-db-local-crud-restraint": "individual-skill",
    "case-response-clean-code-tiny-naming": "individual-skill",
    "case-response-python-tiny-type-hint": "individual-skill",
    "case-response-test-tiny-assertion": "individual-skill",
    "case-response-django-web-one-line-edit": "individual-skill",
    "case-code-small-rename": "supporting-control",
}
RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS = {
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
    "db-local-crud-restraint",
}
RESPONSE_ARCHITECTURE_DB_P4_MIXED_TAGS = {
    "mixed-boundary",
    "db-api-architecture",
    "strategic-ddd",
    "architecture-api",
    "django-ninja",
    "workflow",
    "risky-write-consistency",
}
RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS = {
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
RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS = {
    "implementation-django-web",
    "django-web",
    "templateview-cbv-fbv",
    "templates-base-includes",
    "static-assets",
    "display-ready-fallback",
    "web-forms",
    "htmx-csrf",
    "auth-permission",
    "render-acceptance",
    "routing-boundary",
    "validation-honesty",
}
RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS = {
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
RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS = {
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
IMPLEMENTATION_PYTHON_DIRECT_EXCLUDED_TAGS = {
    "mixed-boundary",
    "workflow",
    "subagent",
    "role-map",
    "role-map-sync",
    "delegation-honesty",
    "sequential-fallback",
    "subagent-opt-out",
    "handoff-contract",
    "integration-closure",
    "positive-composite",
    "risky-write-consistency",
}
IMPLEMENTATION_DJANGO_NINJA_DIRECT_EXCLUDED_TAGS = IMPLEMENTATION_PYTHON_DIRECT_EXCLUDED_TAGS
IMPLEMENTATION_TEST_DIRECT_EXCLUDED_TAGS = IMPLEMENTATION_PYTHON_DIRECT_EXCLUDED_TAGS
CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS = {
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
CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS = {
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
CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS = {
    "code-implementation-django-web",
    "implementation-django-web",
    "django-web",
    "template-context",
    "template-static",
    "safe-rendering",
    "static-reference",
    "render-acceptance",
    "validation-honesty",
}
CODE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS = {
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
MANUAL_PROTOCOL_BUCKETS = {"plugin", "runtime", "source", "workflow"}
MANUAL_PROTOCOL_REQUIRED_TERMS = (
    "cases/plugin/public",
    "answer/",
    "fixtures/",
    "runs/<run-id>/analysis/",
    "leakage",
    "evidence",
)
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
    "workspace/reference/architecture-ddd/reference/final.md",
}
RESPONSE_DDD_DIRECT_TAG = "architecture-ddd-direct"
RESPONSE_DDD_OBSERVATION_FIELDS = (
    "business_problem",
    "subdomain_type",
    "subdomain_type_basis",
    "bounded_context",
    "context_map_or_not_applicable",
    "ubiquitous_terms",
    "aggregate_candidates",
    "entity_or_value_object",
    "invariants",
    "domain_event_or_service",
    "use_cases",
    "consistency_boundary",
    "implementation_restraint",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bucket",
        action="append",
        choices=BUCKETS,
        help="Bucket to validate. Repeatable. Defaults to all buckets.",
    )
    return parser.parse_args()


def scalar_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip("'\"")


def has_field(text: str, key: str) -> bool:
    return bool(re.search(rf"(?m)^\s*{re.escape(key)}\s*:", text))


def block_lines(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(key)}\s*:", line):
            start = index + 1
            break
    if start is None:
        return []
    result: list[str] = []
    for line in lines[start:]:
        if line and not line.startswith(" "):
            break
        if line.strip():
            result.append(line)
    return result


def nested_block_lines(text: str, parent: str, child: str) -> list[str]:
    lines = text.splitlines()
    parent_index: int | None = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(parent)}\s*:", line):
            parent_index = index
            break
    if parent_index is None:
        return []

    child_index: int | None = None
    child_indent = ""
    for index in range(parent_index + 1, len(lines)):
        line = lines[index]
        if line and not line.startswith(" "):
            break
        match = re.match(rf"^(\s+){re.escape(child)}\s*:", line)
        if match:
            child_index = index
            child_indent = match.group(1)
            break
    if child_index is None:
        return []

    result: list[str] = []
    for line in lines[child_index + 1 :]:
        if line and not line.startswith(" "):
            break
        if re.match(rf"^\s{{0,{len(child_indent)}}}\S", line):
            break
        if line.strip():
            result.append(line)
    return result


def validate_reference_basis(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    lines = block_lines(text, "reference_basis")
    path_count = sum(1 for line in lines if re.match(r"^\s*-\s+path\s*:", line))
    basis_count = sum(1 for line in lines if re.match(r"^\s+basis\s*:", line))
    if path_count == 0:
        findings.append(f"{path}: reference_basis must contain structured '- path:' entries")
    if path_count != basis_count:
        findings.append(f"{path}: reference_basis path/basis count mismatch")
    if ABSOLUTE_LOCAL_PATH.search("\n".join(lines)):
        findings.append(f"{path}: reference_basis contains local absolute /Users path")
    return findings


def yaml_list_values(text: str, key: str) -> list[str]:
    values: list[str] = []
    for line in block_lines(text, key):
        match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if not match:
            continue
        value = match.group(1).strip().strip("'\"")
        if value:
            values.append(value)
    return values


def reference_paths(text: str) -> set[str]:
    return {
        item.get("path", "")
        for item in eval_answer_yaml.list_of_maps(text, "reference_basis")
    }


def target_text_contains(text: str, term: str) -> bool:
    if re.fullmatch(r"[a-z0-9_. -]+", term):
        return re.search(
            rf"(?<![a-z0-9_.-]){re.escape(term)}(?![a-z0-9_.-])",
            text,
        ) is not None
    return term in text


def architecture_db_direct_tags(text: str) -> set[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    paths = reference_paths(text)
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-db-"):
        return set()
    if "db-architecture" not in tags:
        return set()
    if tags & RESPONSE_ARCHITECTURE_DB_P4_MIXED_TAGS:
        return set()
    if "workspace/reference/architecture-db/reference/final.md" not in paths:
        return set()
    if not any(path.startswith("dddjango/skills/architecture-db/") for path in paths):
        return set()
    return tags & RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS


def has_implementation_django_ninja_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if tags & IMPLEMENTATION_DJANGO_NINJA_DIRECT_EXCLUDED_TAGS:
        return False
    if not RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-django-ninja-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django-ninja/reference/final.md",
        "dddjango/skills/implementation-django-ninja/SKILL.md",
    }
    if not required_paths <= paths:
        return False
    return any(
        path.startswith("dddjango/skills/implementation-django-ninja/references/")
        for path in paths
    )


def has_implementation_django_web_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-django-web-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django-web/reference/final.md",
        "dddjango/skills/implementation-django-web/SKILL.md",
    }
    if not required_paths <= paths:
        return False
    return any(
        path.startswith("dddjango/skills/implementation-django-web/references/")
        for path in paths
    )


def has_code_implementation_django_web_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-code-web-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django-web/reference/final.md",
        "dddjango/skills/implementation-django-web/SKILL.md",
    }
    if not required_paths <= paths:
        return False
    return any(
        path.startswith("dddjango/skills/implementation-django-web/references/")
        for path in paths
    )


def has_implementation_python_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if tags & IMPLEMENTATION_PYTHON_DIRECT_EXCLUDED_TAGS:
        return False
    if not RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-python-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-python/reference/final.md",
        "dddjango/skills/implementation-python/SKILL.md",
        "dddjango/skills/implementation-python/references/typing.md",
        "dddjango/skills/implementation-python/references/dataclasses-enums.md",
        "dddjango/skills/implementation-python/references/protocols-boundaries.md",
        "dddjango/skills/implementation-python/references/pydantic-v2.md",
    }
    return required_paths <= paths


def has_implementation_tdd_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-tdd-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-tdd/reference/final.md",
        "dddjango/skills/implementation-tdd/SKILL.md",
        "dddjango/skills/implementation-tdd/references/test-list.md",
        "dddjango/skills/implementation-tdd/references/red-green-refactor.md",
        "dddjango/skills/implementation-tdd/references/inside-out-outside-in.md",
        "dddjango/skills/implementation-tdd/references/bdd-atdd.md",
        "dddjango/skills/implementation-tdd/references/ai-assisted-tdd.md",
    }
    return required_paths <= paths


def has_implementation_test_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if tags & IMPLEMENTATION_TEST_DIRECT_EXCLUDED_TAGS:
        return False
    if not RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-test-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-test/reference/final.md",
        "dddjango/skills/implementation-test/SKILL.md",
        "dddjango/skills/implementation-test/references/pytest-fixtures.md",
        "dddjango/skills/implementation-test/references/test-doubles.md",
        "dddjango/skills/implementation-test/references/factories-property-tests.md",
        "dddjango/skills/implementation-test/references/coverage-mutation.md",
        "dddjango/skills/implementation-test/references/django-api-concurrency.md",
    }
    return required_paths <= paths


def has_implementation_test_exclusion_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    required_tags = {
        "implementation-test-exclusion",
        "pytest-assertion",
        "tiny-task-restraint",
        "routing-boundary",
        "validation-honesty",
    }
    if not required_tags <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-response-test-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "dddjango/skills/implementation-test/SKILL.md",
        "dddjango/skills/implementation-test/references/pytest-fixtures.md",
    }
    return required_paths <= paths


def has_code_implementation_python_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if tags & IMPLEMENTATION_PYTHON_DIRECT_EXCLUDED_TAGS:
        return False
    if not CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if not case_id.startswith("case-code-python-"):
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-python/reference/final.md",
        "dddjango/skills/implementation-python/SKILL.md",
        "dddjango/skills/implementation-python/references/typing.md",
        "dddjango/skills/implementation-python/references/dataclasses-enums.md",
        "dddjango/skills/implementation-python/references/protocols-boundaries.md",
        "dddjango/skills/implementation-python/references/pydantic-v2.md",
    }
    return required_paths <= paths


def has_code_implementation_tdd_direct_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not CODE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS <= tags:
        return False
    case_id = scalar_value(text, "case_id") or ""
    if case_id != "case-code-coupon-tdd":
        return False
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-tdd/reference/final.md",
        "dddjango/skills/implementation-tdd/SKILL.md",
        "dddjango/skills/implementation-tdd/references/test-list.md",
        "dddjango/skills/implementation-tdd/references/red-green-refactor.md",
        "dddjango/skills/implementation-tdd/references/inside-out-outside-in.md",
        "workspace/reference/implementation-test/reference/final.md",
    }
    if not required_paths <= paths:
        return False
    return (
        "behavior_checks:" in text
        and "eval_code_behavior_checks.py --case case-code-coupon-tdd" in text
    )


def validate_required_blocks(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    for field in LIST_FIELDS:
        if has_field(text, field) and not yaml_list_values(text, field):
            findings.append(f"{path}: {field} must contain at least one list item")
    if has_field(text, "target_behavior") and not block_lines(text, "target_behavior"):
        findings.append(f"{path}: target_behavior must not be empty")
    return findings


def validate_expected_outcomes(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    if not has_field(text, "expected_outcomes"):
        return findings
    block = "\n".join(block_lines(text, "expected_outcomes"))
    for field in EXPECTED_OUTCOME_FIELDS:
        if not re.search(rf"(?m)^\s+{re.escape(field)}\s*:", block):
            findings.append(f"{path}: expected_outcomes missing {field}")
    baseline_pass = re.search(r"(?m)^\s+baseline_pass_ok\s*:\s*true\s*$", block)
    control_case = (scalar_value(text, "control_case") or "").lower()
    if baseline_pass and control_case == "false":
        tags = set(yaml_list_values(text, "coverage_tags"))
        case_role = (scalar_value(text, "case_role") or "").lower()
        expected_delta_match = re.search(
            r"(?m)^\s+expected_delta\s*:\s*(\S+)\s*$",
            block,
        )
        expected_delta = expected_delta_match.group(1) if expected_delta_match else ""
        is_neutral_cleancode_supporting_case = (
            "implementation-cleancode" in tags
            and case_role == "implementation_supporting"
            and expected_delta == "neutral"
        )
        positive_tags = {
            "implementation-django",
            "django-implementation",
            "code-implementation-django",
            "implementation-django-ninja",
            "code-implementation-django-ninja",
            "implementation-django-web",
            "code-implementation-django-web",
            "implementation-cleancode",
        }
        if (
            tags & positive_tags
            and not is_neutral_cleancode_supporting_case
            and not scalar_value(text, "baseline_pass_ok_reason")
        ):
            findings.append(
                f"{path}: positive implementation answer with control_case false and baseline_pass_ok true must declare baseline_pass_ok_reason"
            )
    return findings


def validate_control_case(path: Path, text: str) -> list[str]:
    value = scalar_value(text, "control_case")
    if value is None:
        return []
    if value.lower() in CONTROL_CASE_VALUES:
        return []
    return [
        f"{path}: control_case must be one of {', '.join(sorted(CONTROL_CASE_VALUES))}"
    ]


def validate_restraint_scope(path: Path, text: str) -> list[str]:
    case_id = scalar_value(text, "case_id") or path.stem
    scope = scalar_value(text, "restraint_scope")
    expected = RESTRAINT_SCOPE_EXPECTATIONS.get(case_id)
    tags = set(yaml_list_values(text, "coverage_tags"))
    findings: list[str] = []
    if expected and not scope:
        findings.append(
            f"{path}: known P5/P4 restraint case must declare restraint_scope: {expected}"
        )
        return findings
    if scope and scope not in RESTRAINT_SCOPE_VALUES:
        findings.append(
            f"{path}: restraint_scope must be one of {', '.join(sorted(RESTRAINT_SCOPE_VALUES))}"
        )
    if expected and scope != expected:
        findings.append(
            f"{path}: restraint_scope mismatch, expected {expected!r}, got {scope!r}"
        )
    if "p5-plugin-restraint" in tags and scope != "plugin-level":
        findings.append(
            f"{path}: p5-plugin-restraint coverage requires restraint_scope: plugin-level"
        )
    if scope == "plugin-level" and "p5-plugin-restraint" not in tags:
        findings.append(
            f"{path}: plugin-level restraint_scope requires p5-plugin-restraint coverage tag"
        )
    if scope in {"individual-skill", "supporting-control"} and "p5-plugin-restraint" in tags:
        findings.append(
            f"{path}: {scope} restraint_scope must not be counted with p5-plugin-restraint"
        )
    return findings


def validate_workflow_execution_expectation(path: Path, text: str) -> list[str]:
    findings: list[str] = []
    if not has_field(text, "workflow_execution_expectation"):
        return [f"{path}: missing workflow_execution_expectation"]
    block = "\n".join(block_lines(text, "workflow_execution_expectation"))
    expectation = workflow_gate.parse_workflow_expectation(text)
    for field in WORKFLOW_EXPECTATION_REQUIRED_FIELDS:
        if not re.search(rf"(?m)^\s*{re.escape(field)}\s*:", block):
            findings.append(
                f"{path}: workflow_execution_expectation missing {field}"
            )
    mode_values = {
        "acceptable_modes": expectation.acceptable_modes if expectation else (),
        "forbidden_modes": expectation.forbidden_modes if expectation else (),
    }
    for field, values in mode_values.items():
        if not values:
            findings.append(
                f"{path}: workflow_execution_expectation {field} must contain at least one list item"
            )
    acceptable = set(mode_values["acceptable_modes"])
    forbidden = set(mode_values["forbidden_modes"])
    overlap = sorted(acceptable & forbidden)
    if overlap:
        findings.append(
            f"{path}: workflow_execution_expectation acceptable_modes and forbidden_modes overlap: {', '.join(overlap)}"
        )
    unknown = sorted(
        mode for mode in acceptable | forbidden if mode not in workflow_gate.KNOWN_MODES
    )
    if unknown:
        findings.append(
            f"{path}: workflow_execution_expectation contains unknown machine mode(s): {', '.join(unknown)}"
        )
    tags = set(yaml_list_values(text, "coverage_tags"))
    strict_trace_tags = {
        "actual-subagent-required",
        "actual-subagent-trace",
        "p5-workflow-integrity",
    }
    if (
        expectation is not None
        and (
            expectation.expected_mode == "actual_subagent_required"
            or strict_trace_tags & tags
        )
    ):
        weak_modes = sorted(acceptable & {"trace_not_captured", "trace_missing", "not_run"})
        if weak_modes:
            findings.append(
                f"{path}: P5 subagent trace expectation must not accept missing/not-run trace modes: {', '.join(weak_modes)}"
            )
    return findings


WORKFLOW_P5_COMBINED_REQUIRED_TAGS = {
    "risky-write-consistency",
    "handoff-contract",
    "responsibility-split",
    "integration-closure",
}
WORKFLOW_P5_COMBINED_CASE_IDS = {
    "case-workflow-positive-composite",
    "case-workflow-risky-write",
}
WORKFLOW_P5_COMBINED_REQUIRED_PATHS = {
    "dddjango/skills/workflow-dddjango-subagents/references/role-map.md",
    "dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md",
    "dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md",
}
WORKFLOW_P5_COMBINED_REQUIRED_ROLE_GROUPS = {
    "Domain role": (("Domain", "Domain Agent"),),
    "Architecture role": (("Architecture", "Architecture Agent"),),
    "DB role": (("DB", "DB Agent"),),
    "API role": (("API", "API Agent"),),
    "Django role": (("Django", "Django Agent"),),
    "Test role": (("TDD/Test", "Test", "Test Agent"),),
    "Review role": (("Review", "Review Agent"),),
    "Integration role": (("Integration", "integration owner"),),
}
WORKFLOW_P5_COMBINED_REQUIRED_HANDOFF_GROUPS = {
    "Scope": (("Scope", "scope"),),
    "Inputs Used": (("Inputs Used", "inputs"),),
    "Decisions": (("Decisions", "decisions"),),
    "Files": (("Files", "files"),),
    "May edit": (("May edit", "may edit"),),
    "Must not edit": (("Must not edit", "must not edit"),),
    "Output": (("Output", "output"),),
    "Risks": (("Risks", "risks"),),
    "Required Follow-up": (("Required Follow-up", "required follow-up"),),
    "dddjango Checks": (("dddjango Checks", "dddjango checks"),),
}
WORKFLOW_P5_COMBINED_REQUIRED_TEXT_GROUPS = {
    "aggregate invariant": (("aggregate invariant", "invariant", "불변식"),),
    "transaction owner": (("transaction owner", "트랜잭션 owner", "transaction boundary"),),
    "locking/isolation": (("locking", "lock", "락"), ("isolation", "격리")),
    "idempotency storage": (("idempotency storage", "멱등성 저장소"), ("uniqueness", "unique", "유일")),
    "Idempotency-Key replay/conflict": (("Idempotency-Key",), ("replay", "재사용"), ("conflict", "충돌")),
    "side-effect timing": (("side effect", "side-effect", "부작용"), ("timing", "on_commit", "commit 이후")),
    "retry/isolation": (("retry", "재시도"), ("isolation", "격리")),
    "concurrency/integration tests": (("concurrency", "동시성"), ("integration", "통합")),
    "integration owner or handoff closure": (("integration owner", "통합 owner", "handoff closure", "인계"),),
}


def has_workflow_p5_combined_coverage(text: str) -> bool:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not WORKFLOW_P5_COMBINED_REQUIRED_TAGS <= tags:
        return False
    paths = reference_paths(text)
    if not WORKFLOW_P5_COMBINED_REQUIRED_PATHS <= paths:
        return False
    expectation = workflow_gate.parse_workflow_expectation(text)
    if expectation is None or "direct" in expectation.acceptable_modes:
        return False

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required"))
    required_groups = (
        list(WORKFLOW_P5_COMBINED_REQUIRED_ROLE_GROUPS.values())
        + list(WORKFLOW_P5_COMBINED_REQUIRED_HANDOFF_GROUPS.values())
        + list(WORKFLOW_P5_COMBINED_REQUIRED_TEXT_GROUPS.values())
    )
    for groups in required_groups:
        if not all(
            any(target_text_contains(required_text, term) for term in alternatives)
            for alternatives in groups
        ):
            return False
    return True


RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_TAGS = {
    "p5-django-implementation-integration",
    "mixed-boundary",
    "handoff-contract",
    "integration-closure",
    "django-implementation-handoff",
    "api-ninja-boundary",
    "db-django-boundary",
    "web-python-boundary",
    "tdd-test-boundary",
    "clean-code-review-boundary",
    "workflow-honesty",
}
RESPONSE_P5_DJANGO_INTEGRATION_CASE_ID = "case-response-django-implementation-handoff"
RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_PATHS = {
    "workspace/reference/architecture-api/reference/final.md",
    "workspace/reference/architecture-db/reference/final.md",
    "workspace/reference/implementation-django/reference/final.md",
    "workspace/reference/implementation-django-ninja/reference/final.md",
    "workspace/reference/implementation-django-web/reference/final.md",
    "workspace/reference/implementation-python/reference/final.md",
    "workspace/reference/implementation-cleancode/reference/final.md",
    "workspace/reference/implementation-tdd/reference/final.md",
    "workspace/reference/implementation-test/reference/final.md",
    "dddjango/skills/architecture-api/references/rest-contracts.md",
    "dddjango/skills/architecture-db/references/transactions-locking.md",
    "dddjango/skills/implementation-django/references/services-selectors.md",
    "dddjango/skills/implementation-django-ninja/references/router-schema.md",
    "dddjango/skills/implementation-django-web/references/templateview-htmx.md",
    "dddjango/skills/implementation-python/references/typing.md",
    "dddjango/skills/implementation-cleancode/references/responsibility.md",
    "dddjango/skills/implementation-tdd/references/red-green-refactor.md",
    "dddjango/skills/implementation-test/references/django-api-concurrency.md",
    "dddjango/skills/workflow-dddjango-subagents/references/handoff-contract.md",
}
RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_TEXT_GROUPS = {
    "API contract vs Ninja adapter": (
        ("architecture-api", "api contract", "resource"),
        ("problem details", "status code", "openapi"),
        ("implementation-django-ninja", "router", "schema", "adapter"),
    ),
    "DB policy vs Django implementation": (
        ("architecture-db", "transaction policy", "uniqueness", "locking"),
        ("idempotency", "duplicate prevention", "migration rollout"),
        ("implementation-django", "orm", "service", "migration"),
    ),
    "production boundary": (
        ("orderservice.confirm", "production implementation", "domain rule"),
        ("transaction.on_commit", "on_commit"),
        ("router", "template", "test fixture", "review"),
    ),
    "web boundary": (
        ("server-rendered", "status badge", "view context"),
        ("template", "static", "auth"),
        ("implementation-django-web", "implementation-django-web.", "render/browser"),
    ),
    "python typing boundary": (
        ("orderstatus", "money", "typing"),
        ("dataclass", "strenum", "typecheck"),
        ("implementation-python", "implementation-python."),
    ),
    "TDD vs pytest": (
        ("implementation-tdd", "test list", "first failing test", "red-green-refactor"),
        ("implementation-test", "pytest", "fixtures", "factory"),
        ("testclient", "concurrency", "assertion"),
    ),
    "Clean Code review": (
        ("implementation-cleancode", "review", "fat service"),
        ("template business logic", "naming", "encapsulation"),
        ("responsibility split",),
    ),
    "handoff honesty": (
        ("handoff", "ownership", "skill boundary"),
        ("unresolved follow-up", "follow-up"),
        ("without claiming", "not claim", "subagent execution"),
    ),
}


def has_response_p5_django_integration_coverage(text: str) -> bool:
    case_id = scalar_value(text, "case_id") or ""
    if case_id != RESPONSE_P5_DJANGO_INTEGRATION_CASE_ID:
        return False
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_TAGS <= tags:
        return False
    paths = reference_paths(text)
    if not RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_PATHS <= paths:
        return False
    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    for groups in RESPONSE_P5_DJANGO_INTEGRATION_REQUIRED_TEXT_GROUPS.values():
        if not all(
            any(target_text_contains(required_text, term) for term in alternatives)
            for alternatives in groups
        ):
            return False
    return True


def validate_response_p5_django_integration_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    case_id = scalar_value(text, "case_id") or path.stem
    if (
        "p5-django-implementation-integration" not in tags
        and case_id != RESPONSE_P5_DJANGO_INTEGRATION_CASE_ID
    ):
        return []
    if has_response_p5_django_integration_coverage(text):
        return []
    return [
        f"{path}: response P5 Django implementation integration answer must keep the full API/Ninja, DB/Django, Web/Python, TDD/Test, Clean Code, and handoff boundary matrix"
    ]


def validate_runtime_metadata_answer(path: Path, text: str) -> list[str]:
    if "missing-skill-metadata" not in set(yaml_list_values(text, "coverage_tags")):
        return []
    findings: list[str] = []
    evidence = [value.lower() for value in yaml_list_values(text, "evidence_required")]
    if not any("validation command output" in value for value in evidence):
        findings.append(
            f"{path}: missing-skill-metadata answer must require validation command output"
        )
    text_lower = text.lower()
    if "semantic metadata alignment" not in text_lower and "semantically align" not in text_lower:
        findings.append(
            f"{path}: missing-skill-metadata answer must require semantic metadata alignment"
        )
    return findings


def require_answer_paths(
    findings: list[str],
    *,
    path: Path,
    text: str,
    required_paths: set[str],
    label: str,
) -> None:
    paths = reference_paths(text)
    for required_path in sorted(required_paths - paths):
        findings.append(f"{path}: {label} answer must reference {required_path}")


def require_text_groups(
    findings: list[str],
    *,
    path: Path,
    text: str,
    groups: dict[str, tuple[tuple[str, ...], ...]],
    label: str,
) -> None:
    target_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    if not target_text:
        target_text = "\n".join(block_lines(text, "target_behavior")).lower()
    evidence_text = "\n".join(block_lines(text, "evidence_required")).lower()
    combined = "\n".join(
        [
            target_text,
            evidence_text,
            "\n".join(nested_block_lines(text, "target_behavior", "forbidden")).lower(),
            "\n".join(block_lines(text, "scoring_checks")).lower(),
            "\n".join(block_lines(text, "failure_modes")).lower(),
            "\n".join(block_lines(text, "leakage_checks")).lower(),
            "\n".join(block_lines(text, "hard_gates")).lower(),
        ]
    )
    for group_label, term_groups in groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in term_groups
            if not any(target_text_contains(combined, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: {label} answer missing {group_label}: {', '.join(missing)}"
            )


def validate_runtime_wrong_routing_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not {"wrong-routing", "django-web"} <= tags:
        return []

    findings: list[str] = []
    require_answer_paths(
        findings,
        path=path,
        text=text,
        label="runtime wrong-routing",
        required_paths={
            "dddjango/skills/workflow-dddjango-subagents/references/role-map.md",
            "dddjango/skills/implementation-django-web/SKILL.md",
            "dddjango/skills/implementation-django-web/agents/openai.yaml",
            "dddjango/skills/implementation-django-web/references/templates.md",
            "dddjango/skills/implementation-django-web/references/static-assets.md",
        },
    )
    require_text_groups(
        findings,
        path=path,
        text=text,
        label="runtime wrong-routing",
        groups={
            "web skill metadata": (("implementation-django-web",), ("metadata", "skill description")),
            "role-map comparison": (("role-map", "role map"), ("canonical workflow table", "canonical")),
            "template/static/web routing": (("template",), ("static",), ("web",)),
            "prompt input evidence": (("prompt-input", "prompt input"),),
        },
    )
    return findings


def validate_runtime_stale_cache_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "stale-cache" not in tags:
        return []

    findings: list[str] = []
    require_text_groups(
        findings,
        path=path,
        text=text,
        label="runtime stale-cache",
        groups={
            "cache snapshot": (("cache",), ("snapshot", "captured")),
            "canonical source comparison": (("canonical",), ("source",), ("compare", "comparison", "differ", "match")),
            "runtime validation": (("runtime validation", "validate_skill_docs.py --phase runtime", "validation output"),),
            "cache-only rejection": (("cache-only",), ("not complete", "accepted", "completion")),
        },
    )
    return findings


def validate_plugin_governance_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    findings: list[str] = []
    if "p5-workflow-integrity" in tags and not has_field(text, "workflow_execution_expectation"):
        findings.append(
            f"{path}: p5-workflow-integrity answer must declare workflow_execution_expectation"
        )
    if "packaging" in tags:
        require_answer_paths(
            findings,
            path=path,
            text=text,
            label="plugin packaging",
            required_paths={
                "dddjango/.codex-plugin/plugin.json",
                ".agents/plugins/marketplace.json",
                "plugins/dddjango",
            },
        )
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin packaging",
            groups={
                "manifest/marketplace/symlink": (
                    ("plugin.json", "manifest"),
                    ("marketplace",),
                    ("plugins/dddjango", "symlink", "equivalent entry"),
                ),
                "canonical source": (("canonical",), ("source",)),
            },
        )
    if "agents-metadata" in tags:
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin agents-metadata",
            groups={
                "field-level metadata": (("display_name",), ("short_description",), ("default_prompt",)),
                "semantic alignment": (("skill.md",), ("semantic", "semantics")),
                "file-existence rejection": (("file existence", "existence only"),),
            },
        )
    if "trigger-quality" in tags:
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin trigger-quality",
            groups={
                "frontmatter trigger": (("frontmatter",), ("description",)),
                "positive/negative routing": (("positive",), ("negative",), ("routing",)),
                "Korean trigger": (("korean", "한국어"),),
                "body-only trigger rejection": (("body-only",), ("trigger",)),
            },
        )
        if "p5-plugin-restraint" in tags:
            require_text_groups(
                findings,
                path=path,
                text=text,
                label="plugin P5 restraint trigger-routing",
                groups={
                    "opt-out restraint": (("opt-out", "opt out"),),
                    "tiny edit restraint": (("tiny edit",),),
                    "Direct Answer Mode": (("direct answer mode",),),
                    "false-claim refusal": (("false-claim", "false claim"), ("refusal", "refuse")),
                    "no meta-tail restraint": (("meta-tail", "meta tail"), ("restraint",)),
                    "trigger/routing surface": (("trigger",), ("routing",)),
                },
            )
    if "runtime-reference-split" in tags:
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin reference-split",
            groups={
                "one-level references": (("one-level",), ("reference",)),
                "load/negative conditions": (("load condition", "load conditions"), ("negative condition", "negative conditions")),
                "source-copy bloat": (("source",), ("copied", "copy", "wholesale")),
            },
        )
    if "cache-source-consistency" in tags:
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin cache-source-consistency",
            groups={
                "cache/source evidence": (("cache",), ("source",), ("evidence", "comparison")),
                "canonical source": (("canonical",), ("source",)),
                "validation output": (("validation",), ("output", "command")),
                "cache-only rejection": (("cache-only",), ("not complete", "completion")),
            },
        )
    if "leaked-answer-text" in tags:
        require_text_groups(
            findings,
            path=path,
            text=text,
            label="plugin leakage",
            groups={
                "private material rejection": (("private",), ("runtime",)),
                "prior run rejection": (("prior",), ("run",)),
                "runtime scan evidence": (("runtime file scan", "runtime file", "scan"),),
            },
        )
    return findings


def validate_source_eval_traceability_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "eval-traceability" not in tags:
        return []

    findings: list[str] = []
    require_text_groups(
        findings,
        path=path,
        text=text,
        label="source eval-traceability",
        groups={
            "per-case row": (("per-case", "case-specific"),),
            "public and answer paths": (("public case path",), ("answer path",)),
            "case id": (("case id",),),
            "source basis": (("source basis", "source reference"),),
            "coverage labels": (("coverage",), ("label", "labels")),
            "leakage boundary": (("leakage",), ("boundary",)),
            "run artifact status": (("run artifact",), ("status",)),
        },
    )
    return findings


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

    paths = reference_paths(text)
    for required_path in sorted(DDD_REQUIRED_REFERENCE_PATHS - paths):
        findings.append(f"{path}: ddd_direct answer must reference {required_path}")

    observation_keys = eval_answer_yaml.nested_keys(text, "ddd_observations")
    if not observation_keys:
        findings.append(f"{path}: DDD code answer must declare ddd_observations")
        return findings
    for field in DDD_OBSERVATION_FIELDS:
        if field not in observation_keys:
            findings.append(f"{path}: ddd_observations missing {field}")
    return findings


def validate_response_ddd_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if RESPONSE_DDD_DIRECT_TAG not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    for required_path in sorted(DDD_REQUIRED_REFERENCE_PATHS - paths):
        findings.append(
            f"{path}: architecture-ddd direct response answer must reference {required_path}"
        )

    observation_keys = eval_answer_yaml.nested_keys(text, "ddd_observations")
    if not observation_keys:
        findings.append(
            f"{path}: architecture-ddd direct response answer must declare ddd_observations"
        )
        return findings
    for field in RESPONSE_DDD_OBSERVATION_FIELDS:
        if field not in observation_keys:
            findings.append(f"{path}: ddd_observations missing {field}")
    return findings


def validate_response_cleancode_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not ({"implementation-cleancode", "clean-code-exclusion"} & tags):
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    if "clean-code-exclusion" in tags:
        required_paths = {"dddjango/skills/implementation-cleancode/SKILL.md"}
    else:
        required_paths = {
            "workspace/reference/implementation-cleancode/reference/final.md",
            "dddjango/skills/implementation-cleancode/SKILL.md",
        }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-cleancode answer must reference {required_path}"
        )

    target_text = "\n".join(block_lines(text, "target_behavior")).lower()
    if "clean-code-exclusion" in tags:
        if not (("brief" in target_text or "short" in target_text) and "direct" in target_text):
            findings.append(
                f"{path}: clean-code exclusion answer must require brief direct handling"
            )
        if not any(term in target_text for term in ("review", "refactor", "workflow", "subagent")):
            findings.append(
                f"{path}: clean-code exclusion answer must forbid clean-code/workflow ceremony"
            )
        return findings

    if not ({"function-shape", "fat-schema-boundary", "legacy-refactoring"} & tags):
        return findings

    positive_terms = (
        ("finding", "review"),
        ("responsib", "boundary", "fat"),
        ("naming", "name"),
        ("function", "argument", "side effect"),
        ("encapsulation",),
        ("abstraction", "solid"),
        ("dry", "duplication", "duplicated"),
        ("error", "exception"),
        ("schema", "router"),
        ("legacy", "test", "regression"),
    )
    for alternatives in positive_terms:
        if not any(term in target_text for term in alternatives):
            findings.append(
                f"{path}: implementation-cleancode answer target_behavior missing one of {', '.join(alternatives)}"
            )
    return findings


def validate_code_cleancode_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-cleancode" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-cleancode/reference/final.md",
        "dddjango/skills/implementation-cleancode/SKILL.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: code implementation-cleancode answer must reference {required_path}"
        )
    if not any(
        path.startswith("dddjango/skills/implementation-cleancode/references/")
        for path in paths
    ):
        findings.append(
            f"{path}: code implementation-cleancode answer must reference at least one bundled implementation-cleancode reference"
        )

    target_text = "\n".join(block_lines(text, "target_behavior")).lower()
    required_terms = {
        "responsibility": ("responsibility", "status invariant", "invariant"),
        "side-effect boundary": ("side-effect", "after-commit", "on_commit", "commit"),
        "regression tests": ("regression", "test"),
        "overengineering restraint": ("repository", "uow", "hexagonal", "outbox"),
    }
    for label, alternatives in required_terms.items():
        if not any(term in target_text for term in alternatives):
            findings.append(
                f"{path}: code implementation-cleancode answer target_behavior missing {label}"
            )
    return findings


def validate_implementation_django_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-django" not in tags and "django-implementation" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django/reference/final.md",
        "dddjango/skills/implementation-django/SKILL.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-django answer must reference {required_path}"
        )
    if not any(
        path.startswith("dddjango/skills/implementation-django/references/")
        for path in paths
    ):
        findings.append(
            f"{path}: implementation-django answer must reference at least one bundled implementation-django reference"
        )

    target_text = "\n".join(block_lines(text, "target_behavior")).lower()
    if {"django-model-orm", "queryset-manager"} & tags:
        for term in ("queryset", "selector", "service", "transaction", "cache"):
            if term not in target_text:
                findings.append(
                    f"{path}: implementation-django ORM/service answer target_behavior missing {term}"
                )
    if "existing-drf-maintenance" in tags:
        for term in ("adapter", "serializer", "viewset", "business rule"):
            if term not in target_text:
                findings.append(
                    f"{path}: implementation-django DRF maintenance answer target_behavior missing {term}"
                )
    if "django-implementation-restraint" in tags:
        if not any(term in target_text for term in ("brief", "short", "minimal", "small")):
            findings.append(
                f"{path}: implementation-django restraint answer must require small scoped handling"
            )
    return findings


def validate_implementation_django_ninja_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-django-ninja" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django-ninja/reference/final.md",
        "dddjango/skills/implementation-django-ninja/SKILL.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-django-ninja answer must reference {required_path}"
        )
    if not any(
        path.startswith("dddjango/skills/implementation-django-ninja/references/")
        for path in paths
    ):
        findings.append(
            f"{path}: implementation-django-ninja answer must reference at least one bundled implementation-django-ninja reference"
        )

    target_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    required_term_groups = {
        "router": (("router",),),
        "schema-modelschema": (("schema",), ("modelschema",)),
        "auth-permission": (("auth", "authentication"), ("permission", "authorization")),
        "filtering-sorting": (("filter", "filtering"), ("sort", "sorting")),
        "pagination": (("pagination", "page"),),
        "problem-details": (("problem details", "rfc 9457"),),
        "openapi": (("openapi", "schema diff"),),
        "testclient": (("testclient", "test client"),),
        "drf-to-ninja": (("drf",), ("compatibility",), ("drf-to-ninja", "migration", "migrate")),
    }
    for label, term_groups in required_term_groups.items():
        if not all(any(term in target_text for term in alternatives) for alternatives in term_groups):
            findings.append(
                f"{path}: implementation-django-ninja answer target_behavior missing {label}"
            )
    return findings


def validate_implementation_django_web_answer(path: Path, text: str, bucket: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-django-web" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-django-web/reference/final.md",
        "dddjango/skills/implementation-django-web/SKILL.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-django-web answer must reference {required_path}"
        )
    if not any(
        path.startswith("dddjango/skills/implementation-django-web/references/")
        for path in paths
    ):
        findings.append(
            f"{path}: implementation-django-web answer must reference at least one bundled implementation-django-web reference"
        )

    target_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    if not target_text:
        target_text = "\n".join(block_lines(text, "target_behavior")).lower()

    if bucket == "response":
        required_groups = {
            "templateview-cbv-fbv": (("templateview",), ("generic cbv", "generic class"), ("fbv",)),
            "templates-base-includes": (("template",), ("base",), ("include", "component")),
            "static-assets": (("static",), ("css",), ("js", "javascript")),
            "display-ready-fallback": (
                ("none",),
                ("blank", "빈 문자열"),
                ("missing optional", "missing value"),
                ("fallback", "display-ready", "prepared display"),
            ),
            "web-forms": (
                ("form",),
                ("get",),
                ("valid post",),
                ("invalid post",),
                ("error rendering", "error"),
                ("user-recoverable", "recoverable", "사용자 회복", "회복 가능한"),
                ("modelform.meta.fields", "meta.fields"),
            ),
            "htmx-csrf": (("htmx",), ("csrf",)),
            "auth-permission": (("auth",), ("permission",)),
            "render-acceptance": (
                ("render",),
                ("browser",),
                ("collectstatic",),
                ("check --deploy", "security check"),
            ),
            "routing-boundary": (("rest",), ("router", "schema"), ("orm", "migration", "transaction"), ("handoff", "넘긴")),
        }
    else:
        required_groups = {
            "template-context": (("template",), ("context",)),
            "display-ready-fallback": (("fallback",), ("optional",), ("empty", "blank")),
            "static-reference": (("static",), ("css",), ("rendered",)),
            "render-acceptance": (("render",), ("compile", "compile-level"), ("test",)),
        }
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(target_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: implementation-django-web answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_implementation_python_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-python" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-python/reference/final.md",
        "dddjango/skills/implementation-python/SKILL.md",
    }
    if "python-tiny-restraint" not in tags:
        required_paths.update(
            {
                "dddjango/skills/implementation-python/references/typing.md",
                "dddjango/skills/implementation-python/references/dataclasses-enums.md",
                "dddjango/skills/implementation-python/references/protocols-boundaries.md",
                "dddjango/skills/implementation-python/references/pydantic-v2.md",
            }
        )
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-python answer must reference {required_path}"
        )

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    if not required_text:
        required_text = "\n".join(block_lines(text, "target_behavior")).lower()

    if "python-tiny-restraint" in tags:
        if not (("brief" in required_text or "short" in required_text) and "direct" in required_text):
            findings.append(
                f"{path}: implementation-python tiny restraint answer must require brief direct handling"
            )
        if not ("str | none" in required_text and "optional" in required_text):
            findings.append(
                f"{path}: implementation-python tiny restraint answer must mention str | None and Optional equivalence"
            )
        return findings

    if "code-implementation-python" in tags:
        required_terms = {
            "type contracts": ("type contract", "type contracts"),
            "dataclass value object": ("dataclass", "value object", "frozen"),
            "Enum/StrEnum": ("enum", "strenum", "finite-state", "finite state"),
            "Protocol boundary": ("protocol", "replaceable boundary"),
            "pydantic v2": ("pydantic", "domain default", "domain model"),
            "Ruff/mypy/pyright": ("ruff", "mypy", "pyright", "typecheck"),
        }
        for label, alternatives in required_terms.items():
            if not any(term in required_text for term in alternatives):
                findings.append(
                    f"{path}: code implementation-python answer target_behavior missing {label}"
                )
        return findings

    required_terms = {
        "type contracts": ("type hints", "input", "return", "none", "x | none", "built-in generics"),
        "TypedDict": ("typeddict",),
        "type narrowing": ("typeis", "typeguard", "none checks", "none check"),
        "dataclass value object": ("dataclass", "value object", "frozen", "slots", "decimal"),
        "Enum/StrEnum": ("enum", "strenum", "literal", "match/case"),
        "Protocol boundary": ("protocol", "replaceable", "boundary"),
        "context manager": ("context manager", "cleanup"),
        "pydantic v2": ("pydantic", "model_validate", "model_dump", "configdict", "field_validator", "model_validator"),
        "async concurrency": ("async", "taskgroup", "except*", "thread", "async-safe"),
        "exceptions": ("exception", "none"),
        "Ruff/mypy/pyright": ("ruff", "mypy", "pyright", "python target"),
        "routing boundary": ("ddd", "db", "rest", "django", "workflow", "handoff"),
    }
    for label, alternatives in required_terms.items():
        if not all(term in required_text for term in alternatives):
            findings.append(
                f"{path}: implementation-python answer target_behavior missing {label}"
            )
    return findings


def validate_implementation_tdd_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-tdd" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-tdd/reference/final.md",
        "dddjango/skills/implementation-tdd/SKILL.md",
        "dddjango/skills/implementation-tdd/references/test-list.md",
        "dddjango/skills/implementation-tdd/references/red-green-refactor.md",
        "dddjango/skills/implementation-tdd/references/inside-out-outside-in.md",
        "dddjango/skills/implementation-tdd/references/bdd-atdd.md",
        "dddjango/skills/implementation-tdd/references/ai-assisted-tdd.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-tdd answer must reference {required_path}"
        )

    target_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    if not target_text:
        target_text = "\n".join(block_lines(text, "target_behavior")).lower()

    required_groups = {
        "test-list": (("test list", "테스트 목록"), ("behavior", "policy", "risk")),
        "failing-test-first": (("failing test", "실패 테스트"), ("red",)),
        "red-green-refactor": (("red",), ("green",), ("refactor",)),
        "inside-out/outside-in": (("inside-out",), ("outside-in",)),
        "acceptance-unit-loop": (("acceptance", "atdd", "bdd"), ("unit",), ("outer loop",), ("inner loop", "inner")),
        "boundary-cases": (("boundary", "threshold"), ("accepted",), ("rejected",)),
        "refactor-checkpoint": (("refactor",), ("green",)),
        "state-verification": (("state verification", "state", "output verification", "output"),),
        "behavior-verification": (("behavior verification", "communication"),),
        "mock-role": (("mock", "mocks"), ("role", "gateway", "notifier")),
        "bdd-atdd": (("bdd",), ("atdd",), ("implementation-test", "pytest-bdd", "gherkin")),
        "validation-honesty": (("not run", "no files", "no commands", "no claim", "without evidence"),),
    }
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(target_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: implementation-tdd answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_code_implementation_tdd_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "code-implementation-tdd" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/implementation-tdd/reference/final.md",
        "dddjango/skills/implementation-tdd/SKILL.md",
        "dddjango/skills/implementation-tdd/references/test-list.md",
        "dddjango/skills/implementation-tdd/references/red-green-refactor.md",
        "dddjango/skills/implementation-tdd/references/inside-out-outside-in.md",
        "workspace/reference/implementation-test/reference/final.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: code implementation-tdd answer must reference {required_path}"
        )
    if "behavior_checks:" not in text or "eval_code_behavior_checks.py --case case-code-coupon-tdd" not in text:
        findings.append(
            f"{path}: code implementation-tdd answer must declare hidden coupon behavior_checks"
        )

    target_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    if not target_text:
        target_text = "\n".join(block_lines(text, "target_behavior")).lower()
    required_groups = {
        "failing-test-first": (("failing test", "실패 테스트"), ("red",)),
        "minimal-green": (("minimal", "최소"), ("green",)),
        "boundary-cases": (("minimum", "boundary"), ("accepted",), ("rejected",), ("expiration",), ("used coupon",)),
        "state-verification": (("state", "output"), ("policy", "outcome")),
        "validation-honesty": (("no claim", "without evidence"), ("characterization", "regression")),
    }
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(target_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: code implementation-tdd answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_implementation_test_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "implementation-test" not in tags and "implementation-test-exclusion" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    if "implementation-test-exclusion" in tags:
        required_paths = {
            "dddjango/skills/implementation-test/SKILL.md",
            "dddjango/skills/implementation-test/references/pytest-fixtures.md",
        }
    else:
        required_paths = {
            "workspace/reference/implementation-test/reference/final.md",
            "dddjango/skills/implementation-test/SKILL.md",
            "dddjango/skills/implementation-test/references/pytest-fixtures.md",
            "dddjango/skills/implementation-test/references/test-doubles.md",
            "dddjango/skills/implementation-test/references/factories-property-tests.md",
            "dddjango/skills/implementation-test/references/coverage-mutation.md",
            "dddjango/skills/implementation-test/references/django-api-concurrency.md",
        }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: implementation-test answer must reference {required_path}"
        )

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    forbidden_text = "\n".join(nested_block_lines(text, "target_behavior", "forbidden")).lower()
    combined_text = required_text + "\n" + forbidden_text

    if "implementation-test-exclusion" in tags:
        if not (("brief" in required_text or "short" in required_text) and "direct" in required_text):
            findings.append(
                f"{path}: implementation-test exclusion answer must require brief direct handling"
            )
        if "pytest.approx" not in required_text and "approximate" not in required_text:
            findings.append(
                f"{path}: implementation-test exclusion answer must mention pytest.approx or approximate assertion"
            )
        if not any(term in forbidden_text for term in ("fixture", "factory", "tdd", "workflow", "subagent")):
            findings.append(
                f"{path}: implementation-test exclusion answer must forbid test/workflow ceremony"
            )
        return findings

    required_groups = {
        "pytest placement": (("pytest",), ("file", "placement"), ("conftest",)),
        "fixtures": (("fixture",), ("conftest",), ("shared", "nested")),
        "parametrization": (("parametrization", "parametrize"), ("boundary",)),
        "assertions": (("assertion",), ("pytest.raises", "pytest.approx", "raises", "approx")),
        "test doubles": (("double",), ("fake",), ("mock",), ("external", "adapter")),
        "factory/faker": (("factory",), ("faker",)),
        "property tests": (("hypothesis", "property"), ("invariant",)),
        "time/http mocking": (("time",), ("http",), ("mock", "adapter")),
        "testcontainers": (("testcontainers",), ("postgresql", "lock", "isolation", "constraint")),
        "coverage/mutation": (("coverage",), ("mutation",), ("proof", "signal")),
        "bdd": (("bdd", "pytest-bdd"), ("stakeholder",)),
        "flaky concurrency": (("flaky",), ("barrier", "lock timeout", "arbitrary sleeps")),
        "testclient": (("testclient", "test client"), ("contract",)),
        "idempotency/concurrency": (("idempotency",), ("concurrency",), ("replay", "conflict")),
        "validation honesty": (("claim", "reports", "reporting"), ("run", "executed", "evidence")),
    }
    direct_routing_required = (("direct",), ("implementation-test",))
    direct_routing_forbidden = ("workflow", "subagent", "ddd", "db", "api")
    missing_direct_required = [
        "/".join(alternatives)
        for alternatives in direct_routing_required
        if not any(target_text_contains(required_text, term) for term in alternatives)
    ]
    if missing_direct_required:
        findings.append(
            f"{path}: implementation-test answer target_behavior missing direct routing: {', '.join(missing_direct_required)}"
        )
    boundary_text = forbidden_text or combined_text
    if not any(term in boundary_text for term in direct_routing_forbidden):
        findings.append(
            f"{path}: implementation-test answer target_behavior missing direct routing forbidden boundary: {', '.join(direct_routing_forbidden)}"
        )
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(required_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: implementation-test answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_source_provisional_drf_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if not {"provisional-handling", "drf-guardrail"} <= tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/source-reference-audit/reference/final.md",
        "workspace/reference/architecture-api/reference/final.md",
        "workspace/reference/architecture-implementation-patterns/reference/final.md",
        "workspace/reference/implementation-django-ninja/reference/final.md",
        "workspace/reference/implementation-django/reference/final.md",
        "workspace/reference/implementation-django-web/reference/final.md",
        "dddjango/skills/architecture-api/SKILL.md",
        "dddjango/skills/implementation-django-ninja/SKILL.md",
        "dddjango/skills/implementation-django/SKILL.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: source provisional/DRF answer must reference {required_path}"
        )

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    required_groups = {
        "dedicated source coverage": (("final.md",), ("substantive", "covers the skill's main decisions")),
        "implementation patterns source status": (("implementation patterns", "architecture-implementation-patterns"),),
        "django web source status": (("django web", "implementation-django-web"),),
        "framework-neutral API contract": (("architecture-api",), ("framework-neutral",), ("api contract", "rest")),
        "greenfield Django Ninja": (("django ninja",), ("greenfield",)),
        "existing DRF maintenance": (("implementation-django",), ("existing drf", "legacy", "maintenance", "migration")),
        "runtime routing": (("runtime",), ("routing",), ("skill", "skill.md")),
        "separate DRF guardrail row": (("drf guardrail",), ("separate", "separable")),
    }
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(required_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: source provisional/DRF answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_source_metadata_cache_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "runtime-metadata-cache-sync" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/source-reference-audit/reference/final.md",
        "dddjango/skills/source-reference-audit/SKILL.md",
        "dddjango/skills/source-reference-audit/agents/openai.yaml",
        "dddjango/skills/source-reference-audit/references/source-governance.md",
        "workspace/scripts/validate_skill_docs.py",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: source metadata/cache answer must reference {required_path}"
        )

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    required_groups = {
        "semantic metadata alignment": (("skill.md",), ("agents/openai.yaml",), ("semantic", "align")),
        "default prompt leakage": (("default prompt",), ("private evaluation material", "internal criteria", "non-public validation")),
        "cache/source parity": (("cache",), ("source",), ("diff", "cmp", "parity", "sync")),
        "validation output": (("validation",), ("command",), ("output", "evidence")),
    }
    for label, groups in required_groups.items():
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(required_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: source metadata/cache answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_source_routing_exclusion_answer(path: Path, text: str) -> list[str]:
    tags = set(yaml_list_values(text, "coverage_tags"))
    if "source-audit-exclusion" not in tags:
        return []

    findings: list[str] = []
    paths = reference_paths(text)
    required_paths = {
        "workspace/reference/source-reference-audit/reference/final.md",
        "dddjango/skills/source-reference-audit/SKILL.md",
        "dddjango/skills/source-reference-audit/references/source-governance.md",
    }
    for required_path in sorted(required_paths - paths):
        findings.append(
            f"{path}: source routing exclusion answer must reference {required_path}"
        )

    required_text = "\n".join(nested_block_lines(text, "target_behavior", "required")).lower()
    forbidden_text = "\n".join(nested_block_lines(text, "target_behavior", "forbidden")).lower()
    combined_text = required_text + "\n" + forbidden_text
    required_groups = {
        "positive source audit routing": (("source",), ("provenance", "cache sync", "metadata", "boundary")),
        "application implementation exclusion": (("django implementation", "model", "orm", "api implementation"), ("owning skill", "route", "handoff")),
        "test mechanics exclusion": (("test mechanics", "pytest", "fixture", "assertion"), ("owning skill", "route", "handoff")),
        "no governance ceremony for exclusions": (("ledger", "crosswalk", "provenance"), ("not", "avoid", "forbid")),
    }
    for label, groups in required_groups.items():
        target_text = combined_text if "exclusion" in label or "ceremony" in label else required_text
        missing = [
            "/".join(alternatives)
            for alternatives in groups
            if not any(target_text_contains(target_text, term) for term in alternatives)
        ]
        if missing:
            findings.append(
                f"{path}: source routing exclusion answer target_behavior missing {label}: {', '.join(missing)}"
            )
    return findings


def validate_answer(path: Path, bucket: str, public_case: Path) -> list[str]:
    findings: list[str] = []
    text = path.read_text(encoding="utf-8")
    case_id = path.stem
    for field in REQUIRED_FIELDS:
        if not has_field(text, field):
            findings.append(f"{path}: missing {field}")
    expected_public = public_case.relative_to(REPO_ROOT).as_posix()
    expected = {
        "id": case_id,
        "case_id": case_id,
        "bucket": bucket,
        "kind": bucket,
        "public_case": expected_public,
    }
    for key, value in expected.items():
        actual = scalar_value(text, key)
        if actual != value:
            findings.append(f"{path}: {key} mismatch, expected {value!r}, got {actual!r}")
    findings.extend(validate_reference_basis(path, text))
    findings.extend(validate_required_blocks(path, text))
    findings.extend(validate_expected_outcomes(path, text))
    findings.extend(validate_control_case(path, text))
    findings.extend(validate_restraint_scope(path, text))
    if bucket == "workflow" or (bucket == "plugin" and has_field(text, "workflow_execution_expectation")):
        findings.extend(validate_workflow_execution_expectation(path, text))
    if bucket == "runtime":
        findings.extend(validate_runtime_metadata_answer(path, text))
        findings.extend(validate_runtime_wrong_routing_answer(path, text))
        findings.extend(validate_runtime_stale_cache_answer(path, text))
    if bucket == "source":
        findings.extend(validate_source_provisional_drf_answer(path, text))
        findings.extend(validate_source_metadata_cache_answer(path, text))
        findings.extend(validate_source_routing_exclusion_answer(path, text))
        findings.extend(validate_source_eval_traceability_answer(path, text))
    if bucket == "plugin":
        findings.extend(validate_plugin_governance_answer(path, text))
    if bucket == "response":
        findings.extend(validate_response_ddd_answer(path, text))
        findings.extend(validate_response_cleancode_answer(path, text))
        findings.extend(validate_implementation_django_answer(path, text))
        findings.extend(validate_implementation_django_ninja_answer(path, text))
        findings.extend(validate_implementation_django_web_answer(path, text, bucket))
        findings.extend(validate_implementation_python_answer(path, text))
        findings.extend(validate_implementation_tdd_answer(path, text))
        findings.extend(validate_implementation_test_answer(path, text))
        findings.extend(validate_response_p5_django_integration_answer(path, text))
    if bucket == "code":
        code_expected = scalar_value(text, "code_expected")
        if code_expected not in {"true", "false"}:
            findings.append(f"{path}: code answer must declare code_expected: true|false")
        if code_expected == "false" and not scalar_value(text, "code_expected_reason"):
            findings.append(f"{path}: code_expected false requires code_expected_reason")
        findings.extend(validate_code_ddd_answer(path, text))
        findings.extend(validate_code_cleancode_answer(path, text))
        findings.extend(validate_implementation_django_answer(path, text))
        findings.extend(validate_implementation_django_ninja_answer(path, text))
        findings.extend(validate_implementation_django_web_answer(path, text, bucket))
        findings.extend(validate_implementation_python_answer(path, text))
        findings.extend(validate_code_implementation_tdd_answer(path, text))
    return findings


def validate_coverage(bucket: str, answers: list[Path]) -> list[str]:
    required = REQUIRED_COVERAGE_TAGS[bucket]
    observed: set[str] = set()
    architecture_db_observed: set[str] = set()
    has_django_ninja_direct = False
    has_django_web_direct = False
    has_code_django_web_direct = False
    has_python_direct = False
    has_tdd_direct = False
    has_test_direct = False
    has_test_exclusion = False
    has_response_p5_django_integration = False
    has_code_python_direct = False
    has_code_tdd_direct = False
    has_workflow_p5_combined = False
    workflow_p5_combined_by_case: dict[str, bool] = {}
    for answer in answers:
        text = answer.read_text(encoding="utf-8")
        observed.update(yaml_list_values(text, "coverage_tags"))
        if bucket == "workflow":
            case_id = scalar_value(text, "case_id") or answer.stem
            case_has_workflow_p5 = has_workflow_p5_combined_coverage(text)
            workflow_p5_combined_by_case[case_id] = case_has_workflow_p5
            if case_has_workflow_p5:
                has_workflow_p5_combined = True
        if bucket == "response":
            if has_response_p5_django_integration_coverage(text):
                has_response_p5_django_integration = True
            architecture_db_observed.update(architecture_db_direct_tags(text))
            if has_implementation_django_ninja_direct_coverage(text):
                has_django_ninja_direct = True
            if has_implementation_django_web_direct_coverage(text):
                has_django_web_direct = True
            if has_implementation_python_direct_coverage(text):
                has_python_direct = True
            if has_implementation_tdd_direct_coverage(text):
                has_tdd_direct = True
            if has_implementation_test_direct_coverage(text):
                has_test_direct = True
            if has_implementation_test_exclusion_coverage(text):
                has_test_exclusion = True
        if bucket == "code" and has_code_implementation_django_web_direct_coverage(text):
            has_code_django_web_direct = True
        if bucket == "code" and has_code_implementation_python_direct_coverage(text):
            has_code_python_direct = True
        if bucket == "code" and has_code_implementation_tdd_direct_coverage(text):
            has_code_tdd_direct = True
    findings: list[str] = []
    missing = sorted(required - observed)
    if missing:
        findings.append(
            f"{bucket}: coverage_tags missing required eval_goal coverage: {', '.join(missing)}"
        )
    if bucket == "response":
        db_missing = sorted(RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS - architecture_db_observed)
        if db_missing:
            findings.append(
                "response: architecture-db P4 direct coverage_tags missing: "
                + ", ".join(db_missing)
            )
        api_missing = sorted(RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS - observed)
        if api_missing:
            findings.append(
                "response: architecture-api P4 coverage_tags missing: "
                + ", ".join(api_missing)
            )
        implementation_patterns_missing = sorted(
            RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS - observed
        )
        if implementation_patterns_missing:
            findings.append(
                "response: architecture-implementation-patterns P4 coverage_tags missing: "
                + ", ".join(implementation_patterns_missing)
            )
        cleancode_missing = sorted(
            RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS - observed
        )
        if cleancode_missing:
            findings.append(
                "response: implementation-cleancode P4 coverage_tags missing: "
                + ", ".join(cleancode_missing)
            )
        django_missing = sorted(
            RESPONSE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS - observed
        )
        if django_missing:
            findings.append(
                "response: implementation-django P4 coverage_tags missing: "
                + ", ".join(django_missing)
            )
        if not has_django_ninja_direct:
            django_ninja_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
            }
            django_ninja_missing = sorted(
                RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS
                - django_ninja_observed
            )
            details = (
                ": " + ", ".join(django_ninja_missing)
                if django_ninja_missing
                else " in one direct implementation-django-ninja answer"
            )
            findings.append(
                "response: implementation-django-ninja P4 coverage_tags missing"
                + details
            )
        if not has_django_web_direct:
            django_web_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            }
            django_web_missing = sorted(
                RESPONSE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
                - django_web_observed
            )
            details = (
                ": " + ", ".join(django_web_missing)
                if django_web_missing
                else " in one direct implementation-django-web answer"
            )
            findings.append(
                "response: implementation-django-web P4 coverage_tags missing"
                + details
            )
        if not has_python_direct:
            python_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            }
            python_missing = sorted(
                RESPONSE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS - python_observed
            )
            details = (
                ": " + ", ".join(python_missing)
                if python_missing
                else " in one direct implementation-python answer"
            )
            findings.append(
                "response: implementation-python P4 coverage_tags missing"
                + details
            )
        if not has_tdd_direct:
            tdd_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS
            }
            tdd_missing = sorted(
                RESPONSE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS - tdd_observed
            )
            details = (
                ": " + ", ".join(tdd_missing)
                if tdd_missing
                else " in one direct implementation-tdd answer"
            )
            findings.append(
                "response: implementation-tdd P4 coverage_tags missing"
                + details
            )
        if not has_test_direct:
            test_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS
            }
            test_missing = sorted(
                RESPONSE_IMPLEMENTATION_TEST_P4_COVERAGE_TAGS - test_observed
            )
            details = (
                ": " + ", ".join(test_missing)
                if test_missing
                else " in one direct implementation-test answer"
            )
            findings.append(
                "response: implementation-test P4 coverage_tags missing"
                + details
            )
        if not has_test_exclusion:
            findings.append(
                "response: implementation-test exclusion coverage missing: "
                "implementation-test-exclusion, pytest-assertion, tiny-task-restraint"
            )
        if not has_response_p5_django_integration:
            findings.append(
                "response: P5 Django implementation integration coverage missing in case-response-django-implementation-handoff"
            )
    if bucket == "code":
        code_django_missing = sorted(
            CODE_IMPLEMENTATION_DJANGO_P4_COVERAGE_TAGS - observed
        )
        if code_django_missing:
            findings.append(
                "code: implementation-django P4 coverage_tags missing: "
                + ", ".join(code_django_missing)
            )
        if not has_code_django_web_direct:
            code_django_web_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS
            }
            code_django_web_missing = sorted(
                CODE_IMPLEMENTATION_DJANGO_WEB_P4_COVERAGE_TAGS - code_django_web_observed
            )
            details = (
                ": " + ", ".join(code_django_web_missing)
                if code_django_web_missing
                else " in one direct implementation-django-web code answer"
            )
            findings.append(
                "code: implementation-django-web P4 coverage_tags missing"
                + details
            )
        if not has_code_python_direct:
            code_python_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS
            }
            code_python_missing = sorted(
                CODE_IMPLEMENTATION_PYTHON_P4_COVERAGE_TAGS - code_python_observed
            )
            details = (
                ": " + ", ".join(code_python_missing)
                if code_python_missing
                else " in one direct implementation-python code answer"
            )
            findings.append(
                "code: implementation-python P4 coverage_tags missing"
                + details
            )
        if not has_code_tdd_direct:
            code_tdd_observed = {
                tag
                for answer in answers
                for tag in yaml_list_values(answer.read_text(encoding="utf-8"), "coverage_tags")
                if tag in CODE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS
            }
            code_tdd_missing = sorted(
                CODE_IMPLEMENTATION_TDD_P4_COVERAGE_TAGS - code_tdd_observed
            )
            details = (
                ": " + ", ".join(code_tdd_missing)
                if code_tdd_missing
                else " in one direct implementation-tdd code answer"
            )
            findings.append(
                "code: implementation-tdd P4 coverage_tags missing"
                + details
            )
    if bucket == "workflow" and not has_workflow_p5_combined:
        findings.append(
            "workflow: P5 combined risky-write integration coverage missing in one case"
        )
    if bucket == "workflow":
        for case_id in sorted(WORKFLOW_P5_COMBINED_CASE_IDS):
            if not workflow_p5_combined_by_case.get(case_id):
                findings.append(
                    f"workflow: {case_id} must keep P5 combined risky-write integration coverage"
                )
    return findings


def validate_manual_protocol(bucket: str) -> list[str]:
    if bucket not in MANUAL_PROTOCOL_BUCKETS:
        return []
    path = EVAL_ROOT / bucket / "manual_protocol.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"{bucket}: missing manual protocol: {path}"]
    text_lower = text.lower()
    missing = [term for term in MANUAL_PROTOCOL_REQUIRED_TERMS if term.lower() not in text_lower]
    if missing:
        return [f"{path}: missing manual protocol term(s): {', '.join(missing)}"]
    return []


def validate_public_case(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings = [
        f"{path}: public case leaks {label}"
        for label, pattern in ANSWER_ONLY_PUBLIC_PATTERNS.items()
        if pattern.search(text)
    ]
    if path.stem == "case-code-web-detail":
        text_lower = text.lower()
        has_blank_memo = (
            "blank memo" in text_lower
            or "empty memo" in text_lower
            or "빈 memo" in text_lower
            or "빈 메모" in text_lower
            or ("memo" in text_lower and "빈 문자열" in text_lower)
            or ("메모" in text_lower and "빈 문자열" in text_lower)
        )
        has_fallback = "fallback" in text_lower or "대체" in text_lower or "placeholder" in text_lower
        if not (has_blank_memo and has_fallback):
            findings.append(f"{path}: case-code-web-detail public case must mention blank memo fallback")
        has_detail_css = "detail.css" in text_lower
        has_reference = (
            "reference" in text_lower
            or "referenced" in text_lower
            or "참조" in text_lower
            or "연결" in text_lower
        )
        if not (has_detail_css and has_reference):
            findings.append(f"{path}: case-code-web-detail public case must mention detail.css reference")
    return findings


def validate_code_capture(public_case_ids: set[str]) -> list[str]:
    metadata_path = EVAL_ROOT / "code/cases/plugin/code-capture.json"
    findings: list[str] = []
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"missing code capture metadata: {metadata_path}"]
    except json.JSONDecodeError as exc:
        return [f"invalid code capture metadata: {metadata_path}: {exc}"]
    cases = metadata.get("cases")
    if not isinstance(cases, dict):
        return [f"{metadata_path}: cases must be an object"]
    metadata_ids = set(cases)
    if metadata_ids != public_case_ids:
        findings.append(
            f"{metadata_path}: public/metadata case mismatch "
            f"public={sorted(public_case_ids - metadata_ids)} metadata={sorted(metadata_ids - public_case_ids)}"
        )
    for case_id, config in cases.items():
        if not isinstance(config, dict):
            findings.append(f"{metadata_path}: {case_id} metadata must be an object")
            continue
        if config.get("captureCode") is not True:
            findings.append(f"{metadata_path}: {case_id} captureCode must be true")
        subject_repo = config.get("subjectRepo")
        if not isinstance(subject_repo, str) or not subject_repo:
            findings.append(f"{metadata_path}: {case_id} subjectRepo is required")
            continue
        if not (REPO_ROOT / subject_repo).is_dir():
            findings.append(f"{metadata_path}: {case_id} subjectRepo does not exist: {subject_repo}")
    return findings


def validate_bucket(bucket: str) -> tuple[int, list[str]]:
    base = EVAL_ROOT / bucket
    public_dir = base / "cases/plugin/public"
    answer_dir = base / "answer"
    public_cases = sorted(path for path in public_dir.glob("case-*.md") if path.name != ".gitkeep")
    answers = sorted(answer_dir.glob("case-*.yaml"))
    findings: list[str] = []
    public_ids = {path.stem for path in public_cases}
    answer_ids = {path.stem for path in answers}
    if not public_cases:
        findings.append(f"{bucket}: no public cases")
    if public_ids != answer_ids:
        findings.append(
            f"{bucket}: public/answer mismatch public={sorted(public_ids - answer_ids)} "
            f"answer={sorted(answer_ids - public_ids)}"
        )
    for public_case in public_cases:
        findings.extend(validate_public_case(public_case))
        answer_path = answer_dir / f"{public_case.stem}.yaml"
        if answer_path.is_file():
            findings.extend(validate_answer(answer_path, bucket, public_case))
    findings.extend(validate_coverage(bucket, answers))
    findings.extend(validate_manual_protocol(bucket))
    if bucket == "code":
        findings.extend(validate_code_capture(public_ids))
    return len(public_cases), findings


def main() -> int:
    args = parse_args()
    buckets = args.bucket or list(BUCKETS)
    all_findings: list[str] = []
    counts: dict[str, int] = {}
    for bucket in buckets:
        count, findings = validate_bucket(bucket)
        counts[bucket] = count
        all_findings.extend(findings)
    if all_findings:
        for finding in all_findings:
            print(f"FAIL: {finding}")
        return 1
    print("eval bucket pack validation passed: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
