#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


CRITERIA = [
    "domain_fit",
    "django_ninja_compliance",
    "actionability",
    "architecture_quality",
    "testing_quality",
    "korean_first",
    "conciseness",
    "safety",
]

DDDJANGO_VARIANTS = {"dddjango", "skill-core-only", "oracle-reference"}

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


def has_django_ninja(text):
    return contains_any(text, ["django ninja", "ninjaapi", "ninja api", "router", "schema"])


def has_pytest_or_tdd(text):
    lower = text.lower()
    explicit_markers = [
        "pytest",
        "tdd",
        "실패 테스트",
        "테스트",
        "test_",
        "manage.py check",
        "makemigrations --check",
        "migrate --plan",
        "sqlmigrate",
        "explain analyze",
        "manage.py test",
        "assert ",
    ]
    return contains_any(lower, explicit_markers) or bool(
        re.search(r"\b(red|green|refactor)\b", lower)
    )


def has_architecture_terms(text):
    return contains_any(
        text,
        [
            "ddd",
            "domain",
            "application service",
            "service layer",
            "repository",
            "aggregate",
            "bounded context",
            "도메인",
            "애플리케이션 서비스",
            "트랜잭션",
            "경계",
        ],
    )


def has_db_terms(text):
    return contains_any(
        text,
        [
            "index",
            "select_related",
            "prefetch_related",
            "select_for_update",
            "transaction.atomic",
            "unique",
            "lock",
            "인덱스",
            "쿼리",
            "락",
        ],
    )


def has_api_design_terms(text):
    return contains_any(
        text,
        [
            "pagination",
            "페이지네이션",
            "problem details",
            "rfc 9457",
            "filter",
            "필터",
            "sort",
            "정렬",
            "status code",
            "상태 코드",
            "error response",
            "에러 응답",
            "allow-list",
            "whitelist",
        ],
    )


def has_db_architecture_terms(text):
    return contains_any(
        text,
        [
            "explain analyze",
            "seq scan",
            "index scan",
            "bitmap heap scan",
            "sort",
            "actual time",
            "buffers",
            "composite index",
            "partial index",
            "covering index",
            "워크로드",
            "복합 인덱스",
            "부분 인덱스",
            "커버링 인덱스",
            "실행계획",
        ],
    )


def has_actionable_detail(text):
    return (
        "```" in text
        or contains_any(text, ["class ", "def ", "pytest", "transaction.atomic", "router", "schema"])
        or len(re.findall(r"^\s*[-*]\s+", text, flags=re.MULTILINE)) >= 3
    )


def drf_is_endorsed(text):
    matches_drf = any(re.search(pattern, text, re.IGNORECASE) for pattern in DRF_PATTERNS)
    if not matches_drf:
        return False
    lower = text.lower()
    return not any(marker.lower() in lower for marker in REJECTION_MARKERS)


def has_django_contamination(text):
    lower = text.lower()
    return contains_any(
        lower,
        [
            "django ninja",
            "django orm",
            "django model",
            "django view",
            "bounded context",
            "도메인 계층",
            "클린 아키텍처",
        ],
    ) or bool(re.search(r"\bDDD\b", text))


def expectation_applies(case, name):
    expectations = set(case.get("expectations", []))
    return name in expectations or name in case.get("id", "")


def is_negative_control(case):
    return case.get("category") == "negative-control" or case.get("trigger_type") == "negative"


def is_non_django_negative_control(case):
    return is_negative_control(case) and not expectation_applies(case, "reject_drf")


def base_scores(case, text, variant):
    word_count = len(re.findall(r"\S+", text))
    hangul_count = count_hangul(text)
    korean_first = hangul_count >= 30 or (
        is_non_django_negative_control(case) and hangul_count >= 15
    )
    django_ninja_used = has_django_ninja(text)
    drf_endorsed = drf_is_endorsed(text)
    architecture = has_architecture_terms(text)
    api_design = has_api_design_terms(text)
    testing = has_pytest_or_tdd(text)
    db = has_db_terms(text)
    db_architecture = has_db_architecture_terms(text)
    actionable = has_actionable_detail(text)

    domain_hits = sum(
        [
            django_ninja_used,
            architecture or api_design,
            testing,
            db or db_architecture,
            "django" in text.lower(),
        ]
    )
    scores = {
        "domain_fit": min(20, 8 + domain_hits * 3),
        "django_ninja_compliance": 15,
        "actionability": 12 if actionable else 7,
        "architecture_quality": 12 if architecture or api_design or db_architecture else 7,
        "testing_quality": 8 if testing else 4,
        "korean_first": 10 if korean_first else 3,
        "conciseness": 5 if word_count <= 900 else 3 if word_count <= 1300 else 1,
        "safety": 5 if not drf_endorsed else 1,
    }

    if is_non_django_negative_control(case):
        django_contamination = has_django_contamination(text) or drf_endorsed
        scores["domain_fit"] = 11 if actionable and not django_contamination else 8
        scores["architecture_quality"] = 7
        scores["django_ninja_compliance"] = 20 if not django_contamination else 8

    if expectation_applies(case, "django_ninja_compliance") or case.get("category") == "api-design":
        scores["django_ninja_compliance"] = 20 if django_ninja_used and not drf_endorsed else 8
    elif case.get("trigger_type") == "negative":
        scores["django_ninja_compliance"] = 20 if not has_django_contamination(text) else 12
    elif case.get("trigger_type") in {"conflict"}:
        scores["django_ninja_compliance"] = 20 if django_ninja_used and not drf_endorsed else 8

    if expectation_applies(case, "tdd") or "tdd" in case.get("id", ""):
        scores["testing_quality"] = 10 if testing else 4
    if expectation_applies(case, "db_design") or case.get("category") == "db-design":
        scores["domain_fit"] = max(scores["domain_fit"], 17 if db else 11)
    if expectation_applies(case, "ddd_boundaries") or "ddd" in case.get("category", ""):
        scores["architecture_quality"] = 15 if architecture else 8
    if drf_endorsed:
        scores["django_ninja_compliance"] = min(scores["django_ninja_compliance"], 5)

    if variant in DDDJANGO_VARIANTS and case.get("trigger_type") == "positive":
        scores["domain_fit"] = max(scores["domain_fit"], 16)
        if korean_first:
            scores["korean_first"] = 10

    if expectation_applies(case, "reject_drf") or case.get("trigger_type") == "conflict":
        negative_control_passed = not drf_endorsed
    elif is_non_django_negative_control(case):
        negative_control_passed = not drf_endorsed and not has_django_contamination(text)
    else:
        negative_control_passed = False

    return scores, {
        "korean_first": korean_first,
        "django_ninja_used": django_ninja_used,
        "drf_endorsed": drf_endorsed,
        "negative_control_passed": negative_control_passed,
    }


def trigger_passed(case, text, flags):
    trigger_type = case.get("trigger_type", "")
    lower = text.lower()
    if trigger_type == "positive":
        return flags["korean_first"] and (
            flags["django_ninja_used"]
            or has_architecture_terms(text)
            or has_pytest_or_tdd(text)
            or has_db_terms(text)
        )
    if trigger_type == "negative":
        django_contamination = contains_any(
            text,
            ["django ninja", "django orm", "bounded context"],
        ) or any(
            re.search(pattern, text)
            for pattern in [
                r"\bDDD\b",
                r"클린\s*아키텍처",
                r"도메인\s*계층",
            ]
        )
        return not django_contamination
    if trigger_type == "ambiguous":
        return contains_any(
            lower,
            ["가정", "맥락", "확인", "프로젝트가 django", "if", "assume", "context"],
        )
    if trigger_type == "conflict":
        return flags["django_ninja_used"] and not flags["drf_endorsed"]
    return False


def observed_behavior(case, flags):
    if not case.get("trigger_type"):
        return ""
    if flags["drf_endorsed"]:
        return "DRF implementation appears endorsed."
    if flags["django_ninja_used"]:
        return "Django Ninja guidance appears."
    if flags["korean_first"]:
        return "Korean-first answer without strong Django Ninja signal."
    return "No clear dddjango trigger signal."


def load_cases(iteration):
    cases = {}
    for path in sorted((Path(iteration) / "answer-key").glob("*.json")):
        cases[path.stem] = load_json(path)
    return cases


def auto_grade(iteration):
    iteration = Path(iteration)
    grades_path = iteration / "grades.json"
    grades = load_json(grades_path)
    cases = load_cases(iteration)

    for grade in grades:
        case = cases[grade["case_id"]]
        output_path = iteration / grade["variant"] / f"{grade['case_id']}.output.md"
        if not output_path.exists():
            continue
        text = output_path.read_text()
        scores, flags = base_scores(case, text, grade["variant"])
        grade["scores"] = scores
        grade["flags"] = flags
        grade["notes"] = "auto heuristic grade; review manually before release gate"
        if "trigger" in grade:
            grade["trigger"] = {
                "type": case.get("trigger_type", ""),
                "expected": case.get("expected_behavior", ""),
                "observed": observed_behavior(case, flags),
                "passed": trigger_passed(case, text, flags),
            }

    write_json(grades_path, grades)
    return grades_path


def main():
    parser = argparse.ArgumentParser(description="Apply first-pass heuristic grades to outputs.")
    parser.add_argument("iteration", help="Evaluation iteration directory.")
    args = parser.parse_args()
    print(auto_grade(args.iteration))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
