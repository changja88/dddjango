#!/usr/bin/env python3
import argparse
import json
import subprocess
import time
from pathlib import Path


CASE_SKILLS = {
    "pilot-api-order-create": [
        "architecture-api",
        "architecture-ddd",
        "implementation-django-ninja",
        "implementation-django",
    ],
    "pilot-api-standard": [
        "architecture-api",
        "implementation-django-ninja",
    ],
    "pilot-db-orders": [
        "architecture-db",
        "implementation-django",
    ],
    "pilot-implementation-coupon": [
        "architecture-ddd",
        "implementation-django",
        "implementation-django-ninja",
    ],
    "pilot-negative-drf": [
        "implementation-django-ninja",
    ],
    "pilot-review-fat-model": [
        "architecture-ddd",
        "architecture-implementation-patterns",
        "implementation-cleancode",
        "implementation-django",
    ],
    "pilot-review-view-logic": [
        "architecture-api",
        "architecture-ddd",
        "implementation-django",
        "implementation-django-ninja",
    ],
    "pilot-tdd-coupon": [
        "architecture-ddd",
        "implementation-django",
        "implementation-django-ninja",
        "implementation-tdd",
        "implementation-test",
    ],
}


CASE_DIRECTIVES = {
    "pilot-api-order-create": (
        "Focus on DDD boundaries, transaction boundary, idempotency, payment port, "
        "and concise Django Ninja Schema/Router code. Keep under 900 words; "
        "no full domain model; include only critical code."
    ),
    "pilot-api-standard": (
        "Produce a copyable team standard: pagination shape, error schema, "
        "exception_handler, response={...} examples, and an edge-case checklist."
    ),
    "pilot-db-orders": (
        "Focus on Django models, constraints, indexes, locking, idempotency keys, "
        "transaction strategy, and pytest or migration checks. Keep API discussion brief."
    ),
    "pilot-implementation-coupon": (
        "Provide DDD layers, Django model/repository/service, Django Ninja endpoint, "
        "and at least two pytest/RED checks. Keep under 900 words; Keep under 700 words; "
        "no full domain model; include only critical code."
    ),
    "pilot-negative-drf": (
        "Reject DRF in one sentence, then provide RED tests and Django Ninja "
        "Schema/Router/NinjaAPI.add_router code. Do not output DRF code."
    ),
    "pilot-review-fat-model": (
        "Lead with severity-ranked findings on aggregate boundaries, gateway dependency, "
        "transactions, N+1 queries, assertNumQueries, and minimal refactoring code."
    ),
    "pilot-review-view-logic": (
        "Review the thin Ninja endpoint boundary, application service split, "
        "transaction.on_commit, idempotency, and error contract with a compact code sketch."
    ),
    "pilot-tdd-coupon": (
        "Use RED-GREEN-REFACTOR. Include RED pytest examples, expected failures, "
        "GREEN implementation, Django Ninja API hook, refactor notes, and commands."
    ),
}


CASE_POLICIES = {
    "pilot-api-order-create": ["ninja"],
    "pilot-api-standard": ["ninja"],
    "pilot-db-orders": [],
    "pilot-implementation-coupon": ["ninja"],
    "pilot-negative-drf": ["ninja", "drf"],
    "pilot-review-fat-model": [],
    "pilot-review-view-logic": ["ninja"],
    "pilot-tdd-coupon": ["ninja", "tdd"],
}


SKILLS_BY_CATEGORY = {
    "api-design": [
        "architecture-api",
        "architecture-ddd",
        "implementation-django",
        "implementation-django-ninja",
    ],
    "ddd-architecture": [
        "architecture-ddd",
        "architecture-implementation-patterns",
        "implementation-django",
    ],
    "db-design": [
        "architecture-db",
        "implementation-django",
    ],
    "tdd": [
        "architecture-ddd",
        "implementation-django",
        "implementation-django-ninja",
        "implementation-tdd",
        "implementation-test",
    ],
    "review": [
        "architecture-ddd",
        "architecture-implementation-patterns",
        "implementation-cleancode",
        "implementation-django",
    ],
    "clean-code": [
        "architecture-implementation-patterns",
        "implementation-cleancode",
        "implementation-django",
    ],
}

SKILLS_BY_EXPECTATION = {
    "api_standard": ["architecture-api", "implementation-django-ninja"],
    "architecture_review": [
        "architecture-ddd",
        "architecture-implementation-patterns",
        "implementation-cleancode",
    ],
    "clean_code": ["architecture-implementation-patterns", "implementation-cleancode"],
    "db_design": ["architecture-db", "implementation-django"],
    "ddd_boundaries": ["architecture-ddd", "architecture-implementation-patterns"],
    "django_ninja_compliance": ["architecture-api", "implementation-django-ninja"],
    "pytest_quality": ["implementation-test"],
    "reject_drf": ["architecture-api", "implementation-django-ninja"],
    "tdd_first": ["implementation-tdd", "implementation-test"],
    "transaction_boundary": ["architecture-db", "implementation-django"],
}


def extract_prompt(text):
    marker = "## Prompt"
    if marker not in text:
        return text.strip()
    return text.split(marker, 1)[1].strip()


def case_id_from_prompt_file(path):
    name = Path(path).name
    if not name.endswith(".prompt.md"):
        raise ValueError(f"not a prompt file: {path}")
    return name.removesuffix(".prompt.md")


def build_codex_command(
    *,
    prompt_file,
    output_file,
    cwd,
    variant,
    model,
    profile,
    ignore_user_config,
    developer_instructions="",
):
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--cd",
        str(cwd),
        "--output-last-message",
        str(output_file),
    ]
    if ignore_user_config:
        command.append("--ignore-user-config")
    if model:
        command.extend(["-m", model])
    if profile:
        command.extend(["--profile", profile])
    if developer_instructions:
        command.extend(
            [
                "-c",
                f"developer_instructions={json.dumps(developer_instructions)}",
            ]
        )
    command.append(extract_prompt(Path(prompt_file).read_text()))
    return command


def broad_dddjango_developer_instructions(root):
    skills_root = root / "skills"
    return (
        "You are evaluating the local dddjango Codex skill package. "
        f"The dddjango skill root is {skills_root}. "
        "Before answering any Python, Django, Django Ninja, API design, DDD, "
        "database, pytest, TDD, clean code, review, or refactoring request, "
        "inspect the relevant dddjango SKILL.md files under that root and follow them. "
        "For DRF, Django REST Framework, Serializer, ViewSet, APIView, rest_framework, "
        "DefaultRouter, or SimpleRouter requests, do not produce DRF code; convert the "
        "answer to Django Ninja Schema/Router and state that this project uses Django Ninja. "
        "For pytest/TDD requests in an empty workspace or read-only sandbox, do not stop "
        "after asking for a project path. State that execution was not possible, then still "
        "provide RED pytest examples, expected failure reasons, GREEN minimal implementation, "
        "REFACTOR direction, and pytest commands."
    )


def unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def case_requests_drf(case):
    prompt = case.get("prompt", "")
    expectations = set(case.get("expectations", []))
    return "reject_drf" in expectations or any(
        token in prompt
        for token in [
            "DRF",
            "Django REST Framework",
            "Serializer",
            "ViewSet",
            "APIView",
            "rest_framework",
        ]
    )


def inferred_skill_names_for_case(case_id, case=None):
    if case_id in CASE_SKILLS:
        return CASE_SKILLS[case_id]
    if not case:
        return []

    trigger_type = case.get("trigger_type", "")
    if trigger_type == "negative":
        return []

    skill_names = []
    category = case.get("category", "")
    skill_names.extend(SKILLS_BY_CATEGORY.get(category, []))

    for expectation in case.get("expectations", []):
        skill_names.extend(SKILLS_BY_EXPECTATION.get(expectation, []))

    prompt = case.get("prompt", "").lower()
    if "django ninja" in prompt or "ninja" in prompt:
        skill_names.extend(["architecture-api", "implementation-django-ninja"])
    if "pytest" in prompt or "tdd" in prompt or "실패 테스트" in prompt:
        skill_names.extend(["implementation-tdd", "implementation-test"])
    if "db" in prompt or "queryset" in prompt or "인덱스" in prompt:
        skill_names.extend(["architecture-db", "implementation-django"])
    if "clean" in prompt or "클린" in prompt:
        skill_names.extend(["architecture-implementation-patterns", "implementation-cleancode"])
    if case_requests_drf(case):
        skill_names.extend(["architecture-api", "implementation-django-ninja"])

    return unique(skill_names)


def skill_paths_for_case(root, case_id, case=None):
    skill_names = inferred_skill_names_for_case(case_id, case=case)
    return [root / "skills" / skill_name / "SKILL.md" for skill_name in skill_names]


def case_policy_names(case_id, case=None):
    policies = list(CASE_POLICIES.get(case_id, []))
    if not case:
        return policies

    if case.get("trigger_type") == "negative":
        return []
    if (
        "django_ninja_compliance" in case.get("expectations", [])
        or case.get("category") == "api-design"
        or "django ninja" in case.get("prompt", "").lower()
    ):
        policies.append("ninja")
    if case_requests_drf(case):
        policies.extend(["ninja", "drf"])
    if (
        case.get("category") == "tdd"
        or "tdd_first" in case.get("expectations", [])
        or "pytest" in case.get("prompt", "").lower()
    ):
        policies.append("tdd")
    return unique(policies)


def case_directive(case_id, case=None):
    if case_id in CASE_DIRECTIVES:
        return CASE_DIRECTIVES[case_id]
    if not case:
        return ""

    trigger_type = case.get("trigger_type", "")
    if trigger_type == "ambiguous":
        return (
            "The request is intentionally ambiguous. Ask one concise clarification or state "
            "conditional assumptions before applying Django or DDD guidance. Keep under 500 words."
        )
    if trigger_type == "conflict":
        return (
            "Explain the policy conflict in one sentence, then provide the Django Ninja alternative. "
            "Do not output DRF implementation code. Keep under 650 words."
        )
    if case.get("category") == "negative-control" and not case_requests_drf(case):
        return ""

    focus = " ".join(case.get("scoring_focus", []))
    return (
        f"Focus on: {focus} "
        "Keep under 750 words; include only task-critical code and verification steps."
    )


def scoped_dddjango_developer_instructions(root, case_id, case=None):
    if case and case.get("trigger_type") == "negative":
        return ""
    if case and case.get("category") == "negative-control" and not case_requests_drf(case):
        return ""

    skill_paths = skill_paths_for_case(root, case_id, case=case)
    if not skill_paths:
        return ""
    paths = "\n".join(f"- {path}" for path in skill_paths)
    policies = []
    policy_names = case_policy_names(case_id, case=case)
    if "ninja" in policy_names:
        policies.append("Use Django Ninja Schema/Router for API guidance.")
    if "drf" in policy_names:
        policies.append(
            "If the prompt asks for DRF, Serializer, ViewSet, APIView, "
            "rest_framework, DefaultRouter, or SimpleRouter, produce no DRF code; "
            "convert to Django Ninja."
        )
    if "tdd" in policy_names:
        policies.append(
            "For pytest/TDD in empty or read-only workspaces, state execution was "
            "not possible, then still provide RED tests, expected failures, GREEN "
            "implementation, REFACTOR notes, and pytest commands."
        )
    policy_text = " ".join(policies)
    directive = case_directive(case_id, case=case)
    return (
        "Use local dddjango skills. Read only:\n"
        f"{paths}\n"
        f"{policy_text} {directive} Keep the answer focused and avoid generic filler."
    )


def dddjango_developer_instructions(root, case_id=None, case=None):
    if case_id:
        scoped = scoped_dddjango_developer_instructions(root, case_id, case=case)
        if scoped:
            return scoped
        if case:
            return ""
    return broad_dddjango_developer_instructions(root)


def load_answer_keys(iteration):
    answer_key_dir = Path(iteration) / "answer-key"
    cases = {}
    for path in answer_key_dir.glob("*.json"):
        cases[path.stem] = json.loads(path.read_text())
    return cases


def load_timing(path):
    if not Path(path).exists():
        return []
    return json.loads(Path(path).read_text())


def update_timing(path, *, case_id, variant, duration_sec, model, profile, returncode):
    records = load_timing(path)
    updated = False
    for record in records:
        if record.get("case_id") == case_id and record.get("variant") == variant:
            record["duration_sec"] = round(duration_sec, 2)
            record["model"] = model or record.get("model", "")
            record["profile"] = profile
            record["returncode"] = returncode
            updated = True
            break
    if not updated:
        records.append(
            {
                "case_id": case_id,
                "variant": variant,
                "duration_sec": round(duration_sec, 2),
                "approx_tokens_in": None,
                "approx_tokens_out": None,
                "tool_calls": None,
                "model": model,
                "profile": profile,
                "returncode": returncode,
                "notes": "",
            }
        )
    Path(path).write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def run_variant(args):
    iteration = Path(args.iteration)
    prompt_dir = iteration / args.variant
    output_dir = prompt_dir
    timing_path = iteration / "timing.json"
    eval_cwd = Path(args.cwd)
    eval_cwd.mkdir(parents=True, exist_ok=True)
    cases = load_answer_keys(iteration)

    prompt_files = sorted(prompt_dir.glob("*.prompt.md"))
    if args.case:
        prompt_files = [path for path in prompt_files if case_id_from_prompt_file(path) == args.case]
    if not prompt_files:
        raise RuntimeError(f"no prompt files found for variant {args.variant}")

    ignore_user_config = args.ignore_user_config
    if args.variant == "baseline" and not args.allow_user_config:
        ignore_user_config = True

    for prompt_file in prompt_files:
        case_id = case_id_from_prompt_file(prompt_file)
        output_file = output_dir / f"{case_id}.output.md"
        developer_instructions = ""
        if args.variant == "dddjango" and args.use_local_dddjango_skills:
            developer_instructions = dddjango_developer_instructions(
                Path(args.root).resolve(),
                case_id=case_id,
                case=cases.get(case_id),
            )
        command = build_codex_command(
            prompt_file=prompt_file,
            output_file=output_file,
            cwd=eval_cwd,
            variant=args.variant,
            model=args.model,
            profile=args.profile,
            ignore_user_config=ignore_user_config,
            developer_instructions=developer_instructions,
        )

        if args.dry_run:
            print(" ".join(command))
            continue

        started = time.perf_counter()
        result = subprocess.run(command, text=True, capture_output=True)
        duration = time.perf_counter() - started
        log_file = output_dir / f"{case_id}.codex.log"
        log_file.write_text(
            "STDOUT\n"
            "======\n"
            f"{result.stdout}\n\n"
            "STDERR\n"
            "======\n"
            f"{result.stderr}\n"
        )
        update_timing(
            timing_path,
            case_id=case_id,
            variant=args.variant,
            duration_sec=duration,
            model=args.model,
            profile=args.profile,
            returncode=result.returncode,
        )
        print(f"{args.variant}/{case_id}: returncode={result.returncode}")
        if result.returncode != 0 and not args.keep_going:
            raise RuntimeError(f"codex exec failed for {args.variant}/{case_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Run generated Codex evaluation prompts and capture outputs."
    )
    parser.add_argument("--iteration", default="workspace/codex-eval/iteration-1")
    parser.add_argument("--root", default=".")
    parser.add_argument("--variant", choices=["baseline", "dddjango"], required=True)
    parser.add_argument("--case", help="Run only one case id.")
    parser.add_argument(
        "--cwd",
        default="/private/tmp/dddjango-codex-eval",
        help="Clean cwd for codex exec. Keep it outside this repo to avoid AGENTS.md leakage.",
    )
    parser.add_argument("--model", default="")
    parser.add_argument("--profile", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument(
        "--ignore-user-config",
        action="store_true",
        help="Ignore user config for this run.",
    )
    parser.add_argument(
        "--allow-user-config",
        action="store_true",
        help="Allow user config for baseline. Not recommended for clean baseline runs.",
    )
    parser.add_argument(
        "--no-local-dddjango-skills",
        action="store_false",
        dest="use_local_dddjango_skills",
        help="Do not inject local dddjango skill instructions for dddjango runs.",
    )
    parser.set_defaults(use_local_dddjango_skills=True)
    args = parser.parse_args()

    run_variant(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
