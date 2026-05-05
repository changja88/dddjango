#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MAP_PATH = ROOT / "evals/codex/conformance-map.json"

DRF_PATTERNS = [
    r"\bAPIView\b",
    r"\bViewSet\b",
    r"\bModelViewSet\b",
    r"\bModelSerializer\b",
    r"\bserializers\.Serializer\b",
    r"class\s+\w+Serializer\s*\(",
    r"\bDefaultRouter\b",
    r"\bSimpleRouter\b",
    r"rest_framework",
    r"Django REST Framework",
]

REJECTION_MARKERS = [
    "사용하지",
    "생성하지",
    "권장하지",
    "쓰지",
    "대신",
    "대체",
    "전환",
    "마이그레이션",
    "피하고",
    "avoid",
    "do not",
    "instead",
    "migrate",
    "replace",
]


def load_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def count_hangul(text):
    return len(re.findall(r"[가-힣]", text))


def contains_any(text, values):
    lower = text.lower()
    return any(value.lower() in lower for value in values)


def remove_path_noise(text):
    text = re.sub(r"`?/[^\s`)]+`?", " ", text)
    text = re.sub(r"`?[A-Za-z]:\\[^\s`)]+`?", " ", text)
    return text


def has_regex(text, pattern):
    return bool(re.search(pattern, text, re.IGNORECASE | re.MULTILINE))


def drf_is_endorsed(text):
    matches_drf = any(re.search(pattern, text, re.IGNORECASE) for pattern in DRF_PATTERNS)
    if not matches_drf:
        return False
    lower = text.lower()
    return not any(marker.lower() in lower for marker in REJECTION_MARKERS)


def has_django_contamination(text):
    cleaned = remove_path_noise(text)
    lower = cleaned.lower()
    strong_terms = [
        "django ninja",
        "django orm",
        "django model",
        "django view",
        "bounded context",
        "도메인 계층",
        "클린 아키텍처",
        "rest_framework",
        "modelserializer",
        "viewset",
    ]
    if contains_any(lower, strong_terms) or bool(re.search(r"\bDDD\b", cleaned)):
        return True
    if "django" not in lower:
        return False
    return not contains_any(
        lower,
        [
            "django는 사용하지",
            "django를 사용하지",
            "django 없이",
            "not use django",
            "without django",
        ],
    )


def rule_korean_first(text):
    return count_hangul(text) >= 30


def rule_concise_korean_first(text):
    return count_hangul(text) >= 15


def rule_uses_django_ninja_router(text):
    return contains_any(text, ["django ninja", "ninjaapi", "ninja api", "from ninja import"]) and contains_any(
        text,
        ["router", "api.add_router", "@router", "Router"],
    )


def rule_uses_schema_not_serializer(text):
    return contains_any(text, ["Schema", "schema"]) and not drf_is_endorsed(text)


def rule_has_http_request_type(text):
    return contains_any(text, ["HttpRequest", "request: HttpRequest"])


def rule_has_explicit_return_type(text):
    return has_regex(text, r"def\s+\w+\([^)]*\)\s*->") or has_regex(
        text,
        r"async\s+def\s+\w+\([^)]*\)\s*->",
    )


def rule_uses_items_meta_envelope(text):
    return contains_any(text, ["items"]) and contains_any(text, ["meta"])


def rule_uses_problem_details(text):
    return contains_any(
        text,
        ["Problem Details", "application/problem+json", "RFC 9457", "problem_detail"],
    )


def rule_includes_verification_commands(text):
    return contains_any(
        text,
        [
            "pytest",
            "python manage.py check",
            "manage.py check",
            "makemigrations --check",
            "migrate --plan",
            "sqlmigrate",
            "explain analyze",
            "uvicorn",
            "curl",
            "httpie",
            "검증",
            "테스트",
        ],
    )


def rule_includes_migration_verification(text):
    return contains_any(
        text,
        [
            "makemigrations --check",
            "migrate --plan",
            "sqlmigrate",
            "python manage.py check",
            "manage.py check",
            "migration",
            "마이그레이션",
        ],
    )


def rule_no_drf_code(text):
    return not drf_is_endorsed(text)


def rule_has_red_green_refactor(text):
    return contains_any(text, ["RED", "GREEN", "REFACTOR"]) or contains_any(
        text,
        ["실패 테스트", "최소 구현", "리팩터"],
    )


def rule_has_expected_failure(text):
    return contains_any(
        text,
        ["예상 실패", "실패 이유", "expected failure", "먼저 실패", "실패해야"],
    )


def rule_has_pytest_tests(text):
    return contains_any(text, ["pytest", "test_", "assert "])


def rule_has_value_object(text):
    return contains_any(
        text,
        [
            "Value Object",
            "값 객체",
            "@dataclass(frozen=True)",
            "dataclass(frozen=True)",
            "OrderTotal",
            "Money",
        ],
    )


def rule_has_domain_exception(text):
    return contains_any(
        text,
        ["Domain Exception", "도메인 예외", "DomainError", "PolicyViolation", "Exception"],
    ) or has_regex(text, r"class\s+\w+Error\b")


def rule_has_result_type(text):
    return contains_any(
        text,
        ["Result Type", "결과 타입", "Result[", "ReserveResult", "ApplyResult", "CancelResult"],
    )


def rule_has_edge_cases(text):
    return contains_any(
        text,
        [
            "edge case",
            "경계",
            "재고 부족",
            "중복",
            "만료",
            "최소 주문",
            "최대 할인",
            "멱등",
        ],
    )


def rule_separates_domain_application_infrastructure(text):
    buckets = [
        contains_any(text, ["domain", "도메인", "aggregate", "bounded context"]),
        contains_any(
            text,
            [
                "application service",
                "애플리케이션 서비스",
                "use case",
                "유스케이스",
                "services.py",
                "service에",
                "service layer",
            ],
        ),
        contains_any(text, ["repository", "infrastructure", "port", "gateway", "저장소", "인프라"]),
        contains_any(
            text,
            [
                "별도 aggregate",
                "별도 애그리거트",
                "context",
                "컨텍스트",
                "view는",
                "HTTP 변환",
            ],
        ),
    ]
    return sum(buckets) >= 2


def rule_has_db_constraints_indexes(text):
    return contains_any(
        text,
        [
            "UniqueConstraint",
            "CheckConstraint",
            "models.Index",
            "index",
            "인덱스",
            "제약조건",
            "unique",
            "constraint",
        ],
    )


def rule_has_transaction_locking(text):
    return contains_any(
        text,
        [
            "transaction.atomic",
            "select_for_update",
            "locking",
            "lock",
            "트랜잭션",
            "락",
            "원자",
        ],
    )


def rule_has_query_pattern_first(text):
    return contains_any(
        text,
        [
            "쿼리 패턴",
            "조회 패턴",
            "대표 쿼리",
            "filter() + order_by()",
            "filter + order_by",
            "관리자 목록",
            "목록 조회",
            "목록성 조회",
            "status = ?",
            "EXPLAIN",
            "workload",
            "워크로드",
        ],
    )


def rule_has_before_after_or_diff(text):
    return contains_any(text, ["Before", "After", "diff --git", "unified diff", "[Before]", "[After]"])


def rule_uses_policy_or_service_extraction(text):
    return contains_any(
        text,
        [
            "Policy",
            "정책 객체",
            "application service",
            "애플리케이션 서비스",
            "Protocol",
            "port",
            "gateway",
        ],
    )


def rule_has_severity_ranked_findings(text):
    return contains_any(
        text,
        [
            "P0",
            "P1",
            "P2",
            "Severity",
            "심각도",
            "치명",
            "높음",
            "High:",
            "Medium:",
            "Low:",
            "High --",
            "Medium --",
            "Low --",
        ],
    )


def rule_no_django_contamination(text):
    return not has_django_contamination(text)


def rule_honors_requested_non_django_framework(text):
    return contains_any(text, ["FastAPI", "fastapi"]) and not has_django_contamination(text)


RULES = {
    "korean_first": rule_korean_first,
    "concise_korean_first": rule_concise_korean_first,
    "uses_django_ninja_router": rule_uses_django_ninja_router,
    "uses_schema_not_serializer": rule_uses_schema_not_serializer,
    "has_http_request_type": rule_has_http_request_type,
    "has_explicit_return_type": rule_has_explicit_return_type,
    "uses_items_meta_envelope": rule_uses_items_meta_envelope,
    "uses_problem_details": rule_uses_problem_details,
    "includes_verification_commands": rule_includes_verification_commands,
    "includes_migration_verification": rule_includes_migration_verification,
    "no_drf_code": rule_no_drf_code,
    "has_red_green_refactor": rule_has_red_green_refactor,
    "has_expected_failure": rule_has_expected_failure,
    "has_pytest_tests": rule_has_pytest_tests,
    "has_value_object": rule_has_value_object,
    "has_domain_exception": rule_has_domain_exception,
    "has_result_type": rule_has_result_type,
    "has_edge_cases": rule_has_edge_cases,
    "separates_domain_application_infrastructure": rule_separates_domain_application_infrastructure,
    "has_db_constraints_indexes": rule_has_db_constraints_indexes,
    "has_transaction_locking": rule_has_transaction_locking,
    "has_query_pattern_first": rule_has_query_pattern_first,
    "has_before_after_or_diff": rule_has_before_after_or_diff,
    "uses_policy_or_service_extraction": rule_uses_policy_or_service_extraction,
    "has_severity_ranked_findings": rule_has_severity_ranked_findings,
    "no_django_contamination": rule_no_django_contamination,
    "honors_requested_non_django_framework": rule_honors_requested_non_django_framework,
}

FORBIDDEN_PATTERNS = {
    "drf_endorsed": drf_is_endorsed,
    "django_contamination": has_django_contamination,
}


def unique_ordered(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def case_config(case, conformance_map):
    expectations = set(case.get("expectations", []))
    category = case.get("category", "")
    if category == "negative-control" and "reject_drf" in expectations:
        category = "api-design"
    config = {
        "required_rules": [],
        "critical_rules": [],
        "forbidden_patterns": [],
    }
    defaults = conformance_map.get("category_defaults", {}).get(category, {})
    for key in config:
        config[key].extend(defaults.get(key, []))

    expectation_rules = conformance_map.get("expectation_rules", {})
    for expectation in expectations:
        config["required_rules"].extend(expectation_rules.get(expectation, []))

    override = conformance_map.get("cases", {}).get(case.get("id", "") or case.get("case_id", ""), {})
    for key in config:
        if key in override:
            config[key] = list(override[key])

    return {key: unique_ordered(values) for key, values in config.items()}


def evaluate_record(case, variant, text, conformance_map):
    config = case_config(case, conformance_map)
    required_rules = config["required_rules"]
    passed_rules = []
    failed_rules = []

    for rule_name in required_rules:
        detector = RULES.get(rule_name)
        if detector is None:
            failed_rules.append(rule_name)
            continue
        if detector(text):
            passed_rules.append(rule_name)
        else:
            failed_rules.append(rule_name)

    critical_violations = [
        rule_name
        for rule_name in config["critical_rules"]
        if rule_name in failed_rules
    ]
    forbidden_patterns = [
        pattern_name
        for pattern_name in config["forbidden_patterns"]
        if FORBIDDEN_PATTERNS[pattern_name](text)
    ]

    pass_rate = round((len(passed_rules) / len(required_rules)) * 100, 2) if required_rules else 100.0
    penalty = (len(critical_violations) + len(forbidden_patterns)) * 15
    conformance_score = max(0, round(pass_rate - penalty, 2))

    return {
        "case_id": case.get("id", "") or case.get("case_id", ""),
        "variant": variant,
        "category": case.get("category", ""),
        "conformance_score": conformance_score,
        "required_rule_pass_rate": pass_rate,
        "required_rules": required_rules,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "critical_violations": critical_violations,
        "forbidden_patterns": forbidden_patterns,
        "notes": (
            "critical or forbidden rule failed"
            if critical_violations or forbidden_patterns
            else "conformance heuristics; review manually before release gate"
        ),
    }


def load_cases(iteration):
    cases = {}
    for path in sorted((Path(iteration) / "answer-key").glob("*.json")):
        data = load_json(path)
        case_id = data.get("id", path.stem)
        data["id"] = case_id
        cases[case_id] = data
    return cases


def output_variants(iteration):
    ignored = {"answer-key", "artifacts"}
    return sorted(
        path.name
        for path in Path(iteration).iterdir()
        if path.is_dir() and path.name not in ignored and list(path.glob("*.output.md"))
    )


def average(values):
    return round(sum(values) / len(values), 2) if values else 0.0


def summarize(records, gate):
    variants = {}
    for variant in sorted({record["variant"] for record in records}):
        selected = [record for record in records if record["variant"] == variant]
        variants[variant] = {
            "average_conformance": average([record["conformance_score"] for record in selected]),
            "average_required_rule_pass_rate": average(
                [record["required_rule_pass_rate"] for record in selected]
            ),
            "critical_violations": sum(len(record["critical_violations"]) for record in selected),
            "forbidden_pattern_count": sum(len(record["forbidden_patterns"]) for record in selected),
            "case_count": len(selected),
        }

    baseline = variants.get("baseline", {})
    dddjango = variants.get("dddjango", {})
    delta = round(
        dddjango.get("average_conformance", 0.0)
        - baseline.get("average_conformance", 0.0),
        2,
    )
    dddjango_score = dddjango.get("average_conformance", 0.0)
    dddjango_pass_rate = dddjango.get("average_required_rule_pass_rate", 0.0)
    critical_violations = dddjango.get("critical_violations", 0)
    forbidden_pattern_count = dddjango.get("forbidden_pattern_count", 0)

    gate_results = {
        "dddjango_conformance_score": {
            "passed": dddjango_score >= gate["minimum_dddjango_conformance_score"],
            "value": dddjango_score,
            "required": gate["minimum_dddjango_conformance_score"],
        },
        "dddjango_required_rule_pass_rate": {
            "passed": dddjango_pass_rate >= gate["minimum_dddjango_required_rule_pass_rate"],
            "value": dddjango_pass_rate,
            "required": gate["minimum_dddjango_required_rule_pass_rate"],
        },
        "critical_violations": {
            "passed": critical_violations <= gate["maximum_critical_violations"],
            "value": critical_violations,
            "required": gate["maximum_critical_violations"],
        },
        "forbidden_pattern_count": {
            "passed": forbidden_pattern_count <= gate["maximum_forbidden_pattern_count"],
            "value": forbidden_pattern_count,
            "required": gate["maximum_forbidden_pattern_count"],
        },
    }

    return {
        "variants": variants,
        "baseline_avg_conformance": baseline.get("average_conformance", 0.0),
        "dddjango_avg_conformance": dddjango_score,
        "delta": delta,
        "dddjango_required_rule_pass_rate": dddjango_pass_rate,
        "critical_violations": critical_violations,
        "forbidden_pattern_count": forbidden_pattern_count,
        "release_gate": gate_results,
    }


def grade_conformance(iteration, *, map_path=DEFAULT_MAP_PATH):
    iteration = Path(iteration)
    conformance_map = load_json(map_path)
    cases = load_cases(iteration)
    records = []
    for variant in output_variants(iteration):
        for case_id, case in cases.items():
            output_path = iteration / variant / f"{case_id}.output.md"
            if not output_path.exists():
                continue
            records.append(
                evaluate_record(
                    case,
                    variant,
                    output_path.read_text(),
                    conformance_map,
                )
            )

    result = {
        "version": 1,
        "summary": summarize(records, conformance_map["release_gate"]),
        "cases": records,
    }
    output_path = iteration / "conformance.json"
    write_json(output_path, result)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Grade dddjango convention conformance.")
    parser.add_argument("iteration", help="Evaluation iteration directory.")
    parser.add_argument(
        "--map",
        default=DEFAULT_MAP_PATH,
        help="Path to conformance-map.json.",
    )
    args = parser.parse_args()
    print(grade_conformance(args.iteration, map_path=Path(args.map)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
