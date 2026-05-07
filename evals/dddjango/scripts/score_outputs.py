#!/usr/bin/env python3
"""Score dddjango purpose-fit evaluation outputs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from eval_lib import (
    VARIANTS,
    clamp_score,
    hangul_ratio,
    load_cases,
    load_dimensions,
    load_gates,
    load_reference_matrix,
    load_release_gates,
    ordered,
    prose_text,
    regex_matches,
    run_dir_from_args,
    substring_matches,
    write_json,
)


def strip_legacy_drf_context(text: str) -> str:
    """Remove explicitly marked legacy/before DRF code blocks from DRF detection."""
    legacy_markers = (
        "legacy",
        "before",
        "as-is",
        "기존",
        "레거시",
        "분석 대상",
        "마이그레이션 전",
    )

    def replace_fence(match: Any) -> str:
        prefix = text[max(0, match.start() - 180):match.start()].lower()
        if any(marker in prefix for marker in legacy_markers):
            return "\n[legacy drf context omitted for policy detection]\n"
        return match.group(0)

    return re.sub(r"```[\s\S]*?```", replace_fence, text)


def scoped_text_for_gate(text: str, gate_id: str, case: dict[str, Any] | None) -> str:
    if gate_id == "no_drf" and case and case.get("allow_legacy_drf_context"):
        return strip_legacy_drf_context(text)
    return text


def evaluate_gate(
    text: str,
    gate_id: str,
    gate: dict[str, Any],
    case: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence: list[str] = []
    detection_text = scoped_text_for_gate(text, gate_id, case)

    fail_if_any = substring_matches(gate.get("fail_if_any", []), detection_text)
    fail_if_regex = regex_matches(gate.get("fail_if_regex", []), detection_text)
    if fail_if_any or fail_if_regex:
        evidence.extend(fail_if_any)
        evidence.extend(fail_if_regex)
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": evidence,
            "message": gate.get("message", ""),
        }

    pass_if_all = gate.get("pass_if_all", [])
    missing_all = [pattern for pattern in pass_if_all if pattern.lower() not in detection_text.lower()]
    if missing_all:
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": missing_all,
            "message": gate.get("message", ""),
        }

    pass_if_regex = gate.get("pass_if_regex", [])
    if pass_if_regex and not regex_matches(pass_if_regex, detection_text):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": pass_if_regex,
            "message": gate.get("message", ""),
        }

    pass_if_all_regex = gate.get("pass_if_all_regex", [])
    missing_all_regex = [
        pattern for pattern in pass_if_all_regex
        if not regex_matches([pattern], detection_text)
    ]
    if missing_all_regex:
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": missing_all_regex,
            "message": gate.get("message", ""),
        }

    pass_if_ordered = gate.get("pass_if_ordered", [])
    if pass_if_ordered and not ordered(detection_text, pass_if_ordered):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": pass_if_ordered,
            "message": gate.get("message", ""),
        }

    pass_if_ordered_any = gate.get("pass_if_ordered_any", [])
    if pass_if_ordered_any and not any(ordered(detection_text, sequence) for sequence in pass_if_ordered_any):
        return {
            "gate": gate_id,
            "status": "fail",
            "severity": gate.get("severity", "major"),
            "evidence": [" -> ".join(sequence) for sequence in pass_if_ordered_any],
            "message": gate.get("message", ""),
        }

    min_hangul_ratio = gate.get("min_hangul_ratio")
    if min_hangul_ratio is not None:
        ratio_text = prose_text(text)
        ratio = hangul_ratio(ratio_text)
        if ratio < min_hangul_ratio:
            return {
                "gate": gate_id,
                "status": "fail",
                "severity": gate.get("severity", "major"),
                "evidence": [f"prose_hangul_ratio={ratio:.3f}", f"minimum={min_hangul_ratio}"],
                "message": gate.get("message", ""),
            }

        return {
            "gate": gate_id,
            "status": "pass",
            "severity": gate.get("severity", "major"),
            "evidence": [f"prose_hangul_ratio={ratio:.3f}"],
            "message": gate.get("message", ""),
        }

    return {
        "gate": gate_id,
        "status": "pass",
        "severity": gate.get("severity", "major"),
        "evidence": [],
        "message": gate.get("message", ""),
    }


def signal_results(case: dict[str, Any], text: str) -> dict[str, Any]:
    required_patterns = case.get("required_patterns", [])
    forbidden_patterns = case.get("forbidden_patterns", [])
    penalty_patterns = case.get("critical_forbidden_patterns", forbidden_patterns)
    required_hits = substring_matches(required_patterns, text)
    forbidden_text = strip_legacy_drf_context(text) if case.get("allow_legacy_drf_context") else text
    forbidden_hits = substring_matches(forbidden_patterns, forbidden_text)
    penalty_hits = substring_matches(penalty_patterns, forbidden_text)
    alternative_results = []
    for group in case.get("alternative_pattern_groups", []):
        patterns = group.get("patterns", [])
        hits = substring_matches(patterns, text)
        alternative_results.append({
            "label": group.get("label", ""),
            "status": "pass" if hits else "missing",
            "hits": hits,
            "accepted_patterns": patterns,
        })
    required_score = 100 if not required_patterns else 100 * (len(required_hits) / len(required_patterns))
    return {
        "score_kind": "automatic_signal",
        "required_patterns": {
            "hits": required_hits,
            "missing": [pattern for pattern in required_patterns if pattern not in required_hits],
            "score": clamp_score(required_score),
        },
        "forbidden_patterns": {
            "hits": forbidden_hits,
            "penalty_hits": penalty_hits,
            "score_penalty": min(100, 25 * len(penalty_hits)),
        },
        "alternative_pattern_groups": alternative_results,
        "expected_skills": {
            "values": case.get("expected_skills", []),
            "status": "manual_required",
        },
        "baseline": {
            "path": case.get("baseline"),
            "status": "manual_required",
        },
    }


def reference_rule_patterns(rule: str) -> list[list[str]]:
    groups: dict[str, list[list[str]]] = {
        "problem_details_error_envelope": [
            ["Problem Details", "application/problem+json"],
            ["status", "title", "detail"],
            ["items", "meta"],
        ],
        "aggregate_boundary_uses_invariants_and_ids": [
            ["불변식", "애그리거트"],
            ["ID"],
            ["도메인 이벤트", "최종 일관성"],
        ],
        "list_api_uses_filter_sort_pagination_testclient": [
            ["FilterSchema"],
            ["allow-list", "허용 목록"],
            ["items", "meta"],
            ["TestClient"],
        ],
        "transaction_lock_idempotency_constraint": [
            ["transaction.atomic", "transaction", "트랜잭션"],
            ["select_for_update", "optimistic locking", "낙관적 잠금", "version"],
            ["idempotency", "Idempotency-Key", "멱등"],
            ["UniqueConstraint", "unique", "고유 제약"],
        ],
        "tdd_edge_cases_time_and_factory": [
            ["RED", "실패 테스트", "실패하는 테스트"],
            ["GREEN", "최소 구현", "통과시키"],
            ["REFACTOR", "리팩터링"],
            ["fixture", "factory", "Factory"],
            ["time", "시간", "freezegun", "timezone"],
        ],
        "tdd_cycle_with_edge_failure_tests": [
            ["RED", "실패 테스트", "실패하는 테스트"],
            ["GREEN", "최소 구현", "통과시키"],
            ["REFACTOR", "리팩터링"],
            ["pytest", "test_"],
            ["경계", "실패", "중복"],
        ],
        "role_map_uses_standard_roles": [
            ["Coordinator"],
            ["Domain Agent"],
            ["DB Agent"],
            ["API Agent"],
            ["Test Agent"],
        ],
        "role_map_includes_skill_mapping_and_file_ownership": [
            ["dddjango skills"],
            ["File ownership"],
            ["architecture-ddd", "architecture-db", "implementation-django-ninja"],
        ],
        "handoff_contract_has_required_fields": [
            ["Scope"],
            ["Inputs Used"],
            ["Decisions"],
            ["Files"],
            ["Output"],
            ["Risks"],
            ["Required Follow-up"],
            ["dddjango Checks"],
        ],
        "sequential_fallback_is_explicit": [
            ["순차 실행", "sequential"],
            ["fallback", "충돌", "같은 파일"],
        ],
        "integration_checks_domain_db_api_test_consistency": [
            ["도메인 불변식"],
            ["transaction"],
            ["API contract"],
            ["test", "pytest"],
        ],
        "simple_single_concern_avoids_subagent_ceremony": [
            ["단순", "직접"],
            ["Role Map"],
        ],
        "specialist_skill_used_directly": [
            ["implementation-django", "implementation-cleancode", "필드명", "migration"],
        ],
        "no_false_subagent_claim": [
            ["실제로 실행하지 않았습니다", "완료했다고 말하지 않습니다", "가정"],
        ],
        "domain_contract_precedes_parallel_review": [
            ["도메인 계약", "Domain Agent"],
            ["병렬", "읽기 전용"],
        ],
        "parallelization_is_read_only_or_disjoint": [
            ["읽기 전용", "read-only", "disjoint"],
            ["File ownership"],
        ],
        "review_agent_integrates_findings": [
            ["Review Agent"],
            ["Integration Checklist", "통합"],
        ],
        "same_file_conflict_uses_sequential_integration": [
            ["같은 파일", "orders/api.py"],
            ["순차 실행"],
        ],
        "coordinator_resolves_file_ownership_conflicts": [
            ["Coordinator"],
            ["File ownership"],
            ["conflict", "충돌"],
        ],
        "domain_logic_moves_outside_router": [
            ["도메인", "Domain Agent", "유스케이스", "service"],
            ["router", "Router"],
        ],
        "api_agent_preserves_ninja_contract": [
            ["API Agent"],
            ["Router", "Schema", "response={"],
        ],
        "sequential_fallback_when_subagents_unavailable": [
            ["실제로 실행하지 않았습니다"],
            ["순차", "직접"],
        ],
        "user_request_for_false_claim_is_corrected": [
            ["완료했다고 말하지 않습니다", "허위", "실제로 실행하지 않았습니다"],
        ],
        "conflict_priority_prefers_domain_invariant": [
            ["conflict priority"],
            ["도메인 불변식"],
        ],
        "api_contract_does_not_bypass_state_transition": [
            ["API contract"],
            ["상태 전이", "불변식"],
        ],
        "tests_cover_integrated_business_rule": [
            ["test", "pytest"],
            ["비즈니스 규칙", "불변식", "상태 전이"],
        ],
        "django_app_tree_separates_domain_api_tests": [
            ["domain/", "domain/**"],
            ["api/", "routers.py", "router.py", "schemas.py"],
            ["services.py", "usecases.py"],
            ["tests/", "test_"],
        ],
        "code_uses_typed_domain_result_not_dict_error": [
            ["Result", "도메인 예외"],
            ["type hint", "타입", "->"],
            ["dict로 에러", "{\"error\""],
        ],
    }
    return groups.get(rule, [])


def rule_passed(rule: str, text: str) -> bool:
    groups = reference_rule_patterns(rule)
    if not groups:
        return False
    passed_groups = 0
    for patterns in groups:
        if substring_matches(patterns, text):
            passed_groups += 1
    if rule == "simple_single_concern_avoids_subagent_ceremony":
        return passed_groups >= 1 and not substring_matches(["Role Map", "Handoff Contract"], text)
    if rule == "code_uses_typed_domain_result_not_dict_error":
        return passed_groups >= 2 and not substring_matches(["dict로 에러", "{\"error\""], text)
    return passed_groups == len(groups)


def structural_checks(case: dict[str, Any], text: str) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    dimensions = set(case.get("required_dimensions", []))

    if "django_ninja_api" in dimensions:
        if case.get("id") == "s06-integration-conflict-resolution":
            patterns = {
                "router_decorator": r"@router\.(post|patch)",
                "response_mapping": r"response\s*=\s*\{",
                "command_endpoint": r"/orders/\{order_id\}/confirm|/orders/\{id\}/confirm|command endpoint|명령형 endpoint",
                "no_status_patch_contract": r"status.*(제외|없음|금지)|PATCH[\s\S]{0,160}status[\s\S]{0,160}(거부|제외|금지)",
            }
        else:
            patterns = {
                "router_instance": r"\bRouter\s*\(",
                "schema_class": r"\bclass\s+\w+\s*\(\s*Schema\s*\)",
                "router_decorator": r"@router\.(get|post|put|patch|delete)",
                "response_mapping": r"response\s*=\s*\{",
            }
        passed = [name for name, pattern in patterns.items() if regex_matches([pattern], text)]
        checks["django_ninja_api"] = {
            "status": "pass" if len(passed) == len(patterns) else "needs_review",
            "passed": passed,
            "missing": [name for name in patterns if name not in passed],
        }

    if "tdd_pytest" in dimensions:
        has_cycle = any(
            ordered(text, sequence)
            for sequence in [
                ["RED", "GREEN", "REFACTOR"],
                ["실패 테스트", "최소 구현", "리팩터링"],
                ["실패하는 테스트", "통과시키", "리팩터링"],
            ]
        )
        patterns = {
            "pytest": r"\bpytest\b|def\s+test_",
            "tdd_cycle": has_cycle,
            "failure_or_boundary": r"실패|경계|중복|idempot",
        }
        passed = [
            name for name, pattern in patterns.items()
            if (pattern is True) or (isinstance(pattern, str) and regex_matches([pattern], text))
        ]
        checks["tdd_pytest"] = {
            "status": "pass" if len(passed) == len(patterns) else "needs_review",
            "passed": passed,
            "missing": [name for name in patterns if name not in passed],
        }

    if "ddd_boundaries" in dimensions:
        terms = ["애그리거트", "값 객체", "도메인 서비스", "유스케이스", "도메인 이벤트", "불변식"]
        hits = substring_matches(terms, text)
        checks["ddd_boundaries"] = {
            "status": "pass" if len(hits) >= 2 else "needs_review",
            "passed": hits,
            "missing": [term for term in terms if term not in hits],
        }

    if "db_transaction" in dimensions:
        terms = ["transaction", "select_for_update", "idempotency", "unique", "locking", "version", "트랜잭션"]
        hits = substring_matches(terms, text)
        checks["db_transaction"] = {
            "status": "pass" if len(hits) >= 2 else "needs_review",
            "passed": hits,
            "missing": [term for term in terms if term not in hits],
        }

    if "clean_implementation" in dimensions:
        if case.get("id") == "t05-django-template-view":
            groups = {
                "view_context": ["TemplateView", "get_context_data", "context"],
                "template_composition": ["{% extends", "{% include", "only", "{% static"],
                "access_and_query": ["LoginRequiredMixin", "selector", "select_related", "prefetch_related", "N+1"],
                "pagination_and_tests": ["Paginator", "pagination", "테스트", "검증"],
            }
            passed = [
                name for name, patterns in groups.items()
                if substring_matches(patterns, text)
            ]
            forbidden_hits = substring_matches(["from ninja import", "Router(", "APIView", "Django Ninja API"], text)
            checks["clean_implementation"] = {
                "status": "pass" if len(passed) >= 3 and not forbidden_hits else "needs_review",
                "passed": passed,
                "missing": [name for name in groups if name not in passed],
                "forbidden_hits": forbidden_hits,
            }
        else:
            terms = ["Result", "도메인 예외", "타입", "Enum", "책임", "분리", "함수", "테스트"]
            forbidden = ["dict로 에러", "{\"error\"", "bool을 반환", "router에서 상태 변경"]
            hits = substring_matches(terms, text)
            forbidden_hits = substring_matches(forbidden, text)
            checks["clean_implementation"] = {
                "status": "pass" if len(hits) >= 3 and not forbidden_hits else "needs_review",
                "passed": hits,
                "missing": [term for term in terms if term not in hits],
                "forbidden_hits": forbidden_hits,
            }

    if "project_structure" in dimensions:
        groups = {
            "domain_layer": ["domain/", "domain/**", "domain.py", "aggregates.py", "entities.py"],
            "application_layer": ["services.py", "usecases.py", "application/"],
            "api_layer": ["api/", "routers.py", "router.py", "schemas.py"],
            "test_layer": ["tests/", "test_", "pytest"],
        }
        passed = [
            name for name, patterns in groups.items()
            if substring_matches(patterns, text)
        ]
        forbidden_hits = substring_matches(["views.py에 비즈니스 로직", "router에서 상태 변경", "하나의 파일"], text)
        checks["project_structure"] = {
            "status": "pass" if len(passed) == len(groups) and not forbidden_hits else "needs_review",
            "passed": passed,
            "missing": [name for name in groups if name not in passed],
            "forbidden_hits": forbidden_hits,
        }

    if "reference_usage" in dimensions:
        entry = load_reference_matrix().get("cases", {}).get(case["id"], {})
        rules = entry.get("reference_rules", [])
        passed = [rule for rule in rules if rule_passed(rule, text)]
        checks["reference_usage"] = {
            "status": "pass" if rules and len(passed) == len(rules) else "needs_review",
            "passed": passed,
            "missing": [rule for rule in rules if rule not in passed],
        }

    if "subagent_role_decomposition" in dimensions:
        roles = [
            "Coordinator",
            "Domain Agent",
            "Architecture Agent",
            "DB Agent",
            "API Agent",
            "Django Agent",
            "Test Agent",
            "Review Agent",
        ]
        hits = substring_matches(roles, text)
        checks["subagent_role_decomposition"] = {
            "status": "pass" if "Coordinator" in hits and len(hits) >= 5 else "needs_review",
            "passed": hits,
            "missing": [role for role in roles if role not in hits],
        }

    if "subagent_skill_mapping" in dimensions:
        skills = [
            "workflow-dddjango-subagents",
            "architecture-ddd",
            "architecture-db",
            "architecture-api",
            "implementation-django-ninja",
            "implementation-django",
            "implementation-tdd",
            "implementation-test",
            "implementation-cleancode",
        ]
        hits = substring_matches(skills, text)
        checks["subagent_skill_mapping"] = {
            "status": "pass" if "workflow-dddjango-subagents" in hits and len(hits) >= 4 else "needs_review",
            "passed": hits,
            "missing": [skill for skill in skills if skill not in hits],
        }

    if "subagent_handoff_contract" in dimensions:
        fields = [
            "Scope",
            "Inputs Used",
            "Decisions",
            "Files",
            "Output",
            "Risks",
            "Required Follow-up",
            "dddjango Checks",
        ]
        hits = substring_matches(fields, text)
        checks["subagent_handoff_contract"] = {
            "status": "pass" if len(hits) == len(fields) else "needs_review",
            "passed": hits,
            "missing": [field for field in fields if field not in hits],
        }

    if "subagent_execution_planning" in dimensions:
        if "subagent_workflow" not in dimensions:
            no_ceremony_terms = ["Role Map", "Handoff Contract", "Integration Checklist"]
            forbidden_hits = substring_matches(no_ceremony_terms, text)
            positive_terms = ["단순", "직접", "subagent 계획은 필요 없어", "실행하지 않았습니다"]
            hits = substring_matches(positive_terms, text)
            checks["subagent_execution_planning"] = {
                "status": "pass" if hits and not forbidden_hits else "needs_review",
                "passed": hits,
                "missing": [term for term in positive_terms if term not in hits],
                "forbidden_hits": forbidden_hits,
            }
        else:
            terms = ["File ownership", "순차 실행", "병렬", "도메인 계약", "Domain Agent", "Coordinator"]
            hits = substring_matches(terms, text)
            has_execution_choice = "순차 실행" in hits or "병렬" in hits
            checks["subagent_execution_planning"] = {
                "status": "pass" if "File ownership" in hits and has_execution_choice and len(hits) >= 3 else "needs_review",
                "passed": hits,
                "missing": [term for term in terms if term not in hits],
            }

    if "subagent_integration_verification" in dimensions:
        terms = ["도메인 불변식", "transaction", "API contract", "test", "conflict priority"]
        hits = substring_matches(terms, text)
        checks["subagent_integration_verification"] = {
            "status": "pass" if len(hits) >= 4 else "needs_review",
            "passed": hits,
            "missing": [term for term in terms if term not in hits],
        }

    if "subagent_claim_integrity" in dimensions:
        false_claims = regex_matches([
            r"subagent(를)?\s*(실행|호출|사용).*완료",
            r"서브\s*에이전트(를)?\s*(실행|호출|사용).*완료",
            r"(Domain|Architecture|DB|API|Django|Test|Review) Agent(에게|가|는)?\s*(맡겼|검토했|확인했|완료했|결과를\s*받)",
            r"에이전트(들)?(이|가)?\s*(병렬\s*)?(검토했|확인했|완료했|결과를\s*반환)",
            r"subagent(들)?(이|가)?\s*(검토했|확인했|완료했|결과를\s*반환)",
        ], text)
        integrity_terms = ["실제로 실행하지 않았습니다", "완료했다고 말하지 않습니다", "순차 실행", "가정"]
        hits = substring_matches(integrity_terms, text)
        checks["subagent_claim_integrity"] = {
            "status": "pass" if not false_claims and hits else "needs_review",
            "passed": hits,
            "missing": [term for term in integrity_terms if term not in hits],
            "forbidden_hits": false_claims,
        }

    return checks


def structural_cap(check: dict[str, Any]) -> int:
    passed = len(check.get("passed", []))
    missing = len(check.get("missing", []))
    total = passed + missing
    if total == 0:
        return 79
    return min(79, clamp_score(100 * (passed / total)))


def substance_cap(text: str) -> int | None:
    prose = prose_text(text).strip()
    if len(prose) < 160:
        return 59
    if len(prose) < 320:
        return 79
    return None


def dimension_scores(
    case: dict[str, Any],
    text: str,
    gate_results: list[dict[str, Any]],
    gates: dict[str, Any],
    structures: dict[str, dict[str, Any]],
) -> dict[str, int]:
    scores: dict[str, int] = {}
    dimension_patterns = case.get("dimension_patterns", {})

    failed_dimensions: set[str] = set()
    for result in gate_results:
        if result["status"] != "fail":
            continue
        gate = gates.get(result["gate"], {})
        if result.get("severity") == "critical":
            failed_dimensions.update(gate.get("dimensions", []))

    for dimension in case.get("required_dimensions", []):
        patterns = dimension_patterns.get(dimension, [])
        relevant_groups = [
            group for group in case.get("alternative_pattern_groups", [])
            if group.get("dimension") == dimension
        ]
        hits = substring_matches(patterns, text)
        group_hits = [
            group for group in relevant_groups
            if substring_matches(group.get("patterns", []), text)
        ]
        denominator = len(patterns) + len(relevant_groups)
        if denominator:
            score = 100 * ((len(hits) + len(group_hits)) / denominator)
        else:
            score = 100

        if dimension in failed_dimensions:
            score = 0

        structure = structures.get(dimension)
        if structure and structure.get("status") != "pass":
            score = min(score, structural_cap(structure))

        if case.get("anti_keyword_stuffing"):
            minimum_substance = substance_cap(text)
            if minimum_substance is not None:
                score = min(score, minimum_substance)

        score_penalty = signal_results(case, text)["forbidden_patterns"]["score_penalty"]
        if score_penalty:
            score -= score_penalty

        scores[dimension] = clamp_score(score)

    return scores


def weighted_total(scores: dict[str, int], dimensions: dict[str, Any]) -> int:
    if not scores:
        return 0
    total_weight = 0
    weighted = 0.0
    for dimension, score in scores.items():
        weight = dimensions.get(dimension, {}).get("weight", 1)
        total_weight += weight
        weighted += score * weight
    return clamp_score(weighted / total_weight)


def has_critical_failure(score: dict[str, Any]) -> bool:
    gate_results = score.get("gate_results", [])
    if not gate_results:
        return score.get("gate_status") == "fail"
    return any(
        result.get("status") == "fail"
        and result.get("severity", "critical") == "critical"
        for result in gate_results
    )


def score_text(case: dict[str, Any], variant: str, text: str) -> dict[str, Any]:
    dimensions = load_dimensions()
    gates = load_gates()
    gate_results = [
        evaluate_gate(text, gate_id, gates[gate_id], case=case)
        for gate_id in case.get("critical_gates", [])
    ]
    signals = signal_results(case, text)
    critical_forbidden_patterns = case.get("critical_forbidden_patterns", case.get("forbidden_patterns", []))
    critical_forbidden_text = strip_legacy_drf_context(text) if case.get("allow_legacy_drf_context") else text
    critical_forbidden_hits = substring_matches(critical_forbidden_patterns, critical_forbidden_text)
    if case.get("forbidden_is_critical") and critical_forbidden_hits:
        gate_results.append({
            "gate": "case_forbidden_patterns",
            "status": "fail",
            "severity": "critical",
            "evidence": critical_forbidden_hits,
            "message": "이 케이스에서는 forbidden pattern이 trigger 오염 또는 정책 위반을 의미한다.",
        })
    structures = structural_checks(case, text)
    scores = dimension_scores(case, text, gate_results, gates, structures)
    total = weighted_total(scores, dimensions)
    failed = [result for result in gate_results if result["status"] == "fail"]
    gate_status = "fail" if failed else "pass"
    if gate_status == "fail":
        total = min(total, 59)

    rationale = "Critical gate 통과" if gate_status == "pass" else "Critical gate 실패: " + ", ".join(result["gate"] for result in failed)
    return {
        "case_id": case["id"],
        "variant": variant,
        "total_score": total,
        "score_kind": "automatic_signal",
        "automatic_confidence": "low",
        "manual_required": True,
        "gate_status": gate_status,
        "dimension_scores": scores,
        "signal_results": signals,
        "structural_checks": structures,
        "gate_results": gate_results,
        "rationale": rationale,
        "artifact": f"outputs/{case['id']}.{variant}.md",
    }


def missing_score(case: dict[str, Any], variant: str) -> dict[str, Any]:
    scores = {dimension: 0 for dimension in case.get("required_dimensions", [])}
    return {
        "case_id": case["id"],
        "variant": variant,
        "total_score": 0,
        "score_kind": "missing_output",
        "automatic_confidence": "high",
        "manual_required": False,
        "gate_status": "fail",
        "dimension_scores": scores,
        "signal_results": {
            "score_kind": "missing_output",
            "required_patterns": {"hits": [], "missing": case.get("required_patterns", []), "score": 0},
            "forbidden_patterns": {"hits": [], "score_penalty": 0},
            "alternative_pattern_groups": [],
            "expected_skills": {"values": case.get("expected_skills", []), "status": "not_evaluated"},
            "baseline": {"path": case.get("baseline"), "status": "not_evaluated"},
        },
        "structural_checks": {},
        "gate_results": [
            {
                "gate": "missing_output",
                "status": "fail",
                "severity": "critical",
                "evidence": [f"outputs/{case['id']}.{variant}.md"],
                "message": "평가 output 파일이 누락되면 실패로 처리한다.",
            }
        ],
        "rationale": "Output 누락",
        "artifact": f"outputs/{case['id']}.{variant}.md",
    }


def release_gate_status(
    summary: dict[str, Any],
    *,
    mode: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    release_gates = load_release_gates()
    if mode != "live":
        return {
            "status": "not_applicable",
            "mode": mode,
            "message": "fixture/smoke run에는 release gate를 적용하지 않는다.",
            "results": [],
        }

    if metadata and not is_full_live_run(metadata):
        return {
            "status": "not_applicable",
            "mode": mode,
            "message": "부분 live run에는 release gate를 적용하지 않는다.",
            "results": [],
        }

    results: list[dict[str, Any]] = []
    by_variant = summary.get("by_variant", {})
    scores = summary.get("scores", [])
    unresolved_review = [
        score["case_id"]
        for score in scores
        if score.get("variant") == "with-dddjango"
        and score.get("manual_required")
        and score.get("automatic_confidence") == "low"
    ]

    for gate_id, gate in release_gates.items():
        if "max_failures" in gate:
            critical_failures = len(by_variant.get("with-dddjango", {}).get("critical_failures", []))
            max_failures = gate["max_failures"]
            results.append({
                "gate": gate_id,
                "status": "pass" if critical_failures <= max_failures else "fail",
                "actual": critical_failures,
                "expected": f"<= {max_failures}",
            })
            continue

        if gate_id == "skill_value_delta":
            delta = summary.get("skill_value_delta")
            min_delta = gate["minimum_delta"]
            results.append({
                "gate": gate_id,
                "status": "pass" if delta is not None and delta >= min_delta else "fail",
                "actual": delta,
                "expected": f">= {min_delta}",
            })
            continue

        variant = gate.get("variant", "with-dddjango")
        minimum = gate.get("minimum_average")
        if "dimension" in gate:
            actual = dimension_average(scores, variant=variant, dimensions=[gate["dimension"]])
        elif "dimensions" in gate:
            actual = dimension_average(scores, variant=variant, dimensions=gate["dimensions"])
        else:
            actual = by_variant.get(variant, {}).get("average")

        results.append({
            "gate": gate_id,
            "status": "pass" if actual is not None and minimum is not None and actual >= minimum else "fail",
            "actual": actual,
            "expected": f">= {minimum}",
            })

    if unresolved_review:
        results.append({
            "gate": "manual_review_required",
            "status": "needs_review",
            "actual": len(unresolved_review),
            "expected": "0 low-confidence automatic-only scores",
            "cases": unresolved_review,
        })

    if any(result["status"] == "fail" for result in results):
        status = "fail"
    elif any(result["status"] == "needs_review" for result in results):
        status = "needs_review"
    else:
        status = "pass"

    return {
        "status": status,
        "mode": mode,
        "message": (
            "자동 signal만으로는 release gate를 통과시키지 않는다."
            if status == "needs_review" else ""
        ),
        "results": results,
    }


def is_full_live_run(metadata: dict[str, Any]) -> bool:
    if metadata.get("suite") is not None or metadata.get("case_id") is not None:
        return False
    if tuple(metadata.get("variants", [])) != VARIANTS:
        return False
    return metadata.get("case_count") == len(load_cases())


def dimension_average(
    scores: list[dict[str, Any]],
    *,
    variant: str,
    dimensions: list[str],
) -> int | None:
    values: list[int] = []
    for score in scores:
        if score.get("variant") != variant:
            continue
        dimension_scores = score.get("dimension_scores", {})
        for dimension in dimensions:
            if dimension in dimension_scores:
                values.append(dimension_scores[dimension])
    if not values:
        return None
    return clamp_score(sum(values) / len(values))


def summarize(scores: list[dict[str, Any]], *, mode: str = "unknown") -> dict[str, Any]:
    variants: dict[str, list[dict[str, Any]]] = {}
    for score in scores:
        variants.setdefault(score["variant"], []).append(score)

    by_variant: dict[str, Any] = {}
    for variant, items in variants.items():
        average = sum(item["total_score"] for item in items) / len(items) if items else 0
        failures = [
            {"case_id": item["case_id"], "rationale": item["rationale"]}
            for item in items
            if has_critical_failure(item)
        ]
        by_variant[variant] = {
            "average": clamp_score(average),
            "case_count": len(items),
            "critical_failures": failures,
        }

    delta = None
    if mode == "live" and "with-dddjango" in by_variant and "without-dddjango" in by_variant:
        delta = by_variant["with-dddjango"]["average"] - by_variant["without-dddjango"]["average"]

    summary = {
        "by_variant": by_variant,
        "skill_value_delta": delta,
        "score_interpretation": (
            "plugin_performance" if mode == "live"
            else "pipeline_smoke_only"
        ),
        "scores": scores,
    }
    summary["release_gate_status"] = release_gate_status(summary, mode=mode)
    return summary


def score_run(run_dir: Path, suite: str | None = None, case_id: str | None = None) -> dict[str, Any]:
    cases = load_cases(suite)
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
    metadata_path = run_dir / "metadata.json"
    mode = "unknown"
    metadata: dict[str, Any] | None = None
    if metadata_path.exists():
        import json

        metadata = json.loads(metadata_path.read_text())
        mode = metadata.get("mode", "unknown")
    scores: list[dict[str, Any]] = []
    for case in cases:
        for variant in VARIANTS:
            output_path = run_dir / "outputs" / f"{case['id']}.{variant}.md"
            if not output_path.exists():
                result = missing_score(case, variant)
            else:
                result = score_text(case, variant, output_path.read_text())
            scores.append(result)
            write_json(run_dir / "scores" / f"{case['id']}.{variant}.score.json", result)

    summary = summarize(scores, mode=mode)
    summary["release_gate_status"] = release_gate_status(summary, mode=mode, metadata=metadata)
    write_json(run_dir / "scores/summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--suite")
    parser.add_argument("--case")
    args = parser.parse_args()

    run_dir = run_dir_from_args(args.run_id, args.latest)
    summary = score_run(run_dir, args.suite, args.case)
    print(f"채점 완료: {run_dir}")
    print(f"결과 수: {len(summary['scores'])}")
    release_status = summary.get("release_gate_status", {})
    if release_status.get("mode") == "live" and release_status.get("status") in {"fail", "needs_review"}:
        if release_status.get("status") == "needs_review":
            print("live release gate 수동 검토 필요")
        else:
            print("live release gate 실패")
        return 2
    if release_status.get("mode") == "live" and release_status.get("status") == "not_applicable":
        selected_variants = set()
        metadata_path = run_dir / "metadata.json"
        if metadata_path.exists():
            import json

            run_metadata = json.loads(metadata_path.read_text())
            selected_variants = set(run_metadata.get("variants", []))
        failed_scores = [
            score for score in summary.get("scores", [])
            if score.get("variant") == "with-dddjango" and score.get("gate_status") == "fail"
            and (not selected_variants or score.get("variant") in selected_variants)
        ]
        if failed_scores:
            print("live subset gate 실패")
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
