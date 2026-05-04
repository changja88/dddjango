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

DRF_PATTERNS = [
    r"\bAPIView\b",
    r"\bViewSet\b",
    r"\bModelViewSet\b",
    r"\bSerializer\b",
    r"\bModelSerializer\b",
    r"\bDefaultRouter\b",
    r"\bSimpleRouter\b",
    r"rest_framework",
    r"Django REST Framework",
]

REJECTION_MARKERS = [
    "사용하지",
    "생성하지",
    "권장하지",
    "대신",
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
    return contains_any(text, ["pytest", "red", "green", "refactor", "실패 테스트", "tdd"])


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


def expectation_applies(case, name):
    expectations = set(case.get("expectations", []))
    return name in expectations or name in case.get("id", "")


def base_scores(case, text, variant):
    word_count = len(re.findall(r"\S+", text))
    korean_first = count_hangul(text) >= 30
    django_ninja_used = has_django_ninja(text)
    drf_endorsed = drf_is_endorsed(text)
    architecture = has_architecture_terms(text)
    testing = has_pytest_or_tdd(text)
    db = has_db_terms(text)
    actionable = has_actionable_detail(text)

    domain_hits = sum([django_ninja_used, architecture, testing, db, "django" in text.lower()])
    scores = {
        "domain_fit": min(20, 8 + domain_hits * 3),
        "django_ninja_compliance": 15,
        "actionability": 12 if actionable else 7,
        "architecture_quality": 12 if architecture else 7,
        "testing_quality": 8 if testing else 4,
        "korean_first": 10 if korean_first else 3,
        "conciseness": 5 if word_count <= 900 else 3 if word_count <= 1300 else 1,
        "safety": 5 if not drf_endorsed else 1,
    }

    if expectation_applies(case, "django_ninja_compliance") or case.get("category") == "api-design":
        scores["django_ninja_compliance"] = 20 if django_ninja_used and not drf_endorsed else 8
    elif case.get("trigger_type") == "negative":
        scores["django_ninja_compliance"] = 20 if not django_ninja_used else 12
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

    if variant == "dddjango" and case.get("trigger_type") == "positive":
        scores["domain_fit"] = max(scores["domain_fit"], 16)
        if korean_first:
            scores["korean_first"] = 10

    return scores, {
        "korean_first": korean_first,
        "django_ninja_used": django_ninja_used,
        "drf_endorsed": drf_endorsed,
        "negative_control_passed": not drf_endorsed
        and (
            case.get("category") == "negative-control"
            or case.get("trigger_type") in {"negative", "conflict"}
        ),
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
