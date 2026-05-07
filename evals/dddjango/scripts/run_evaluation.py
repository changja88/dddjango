#!/usr/bin/env python3
"""Create dddjango purpose-fit evaluation runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from eval_lib import ROOT, VARIANTS, WORKSPACE_ROOT, load_cases, make_run_id, write_json


def fixture_output(case: dict, variant: str) -> str:
    if variant == "without-dddjango":
        return "\n".join(
            [
                f"# {case['title']} - without dddjango fixture",
                "",
                "이 출력은 평가 파이프라인 검증용 fixture입니다.",
                "일반적인 답변은 핵심 dddjango 규칙 일부를 놓칠 수 있습니다.",
                "",
                "예시:",
                "from rest_framework import serializers",
                "class OrderSerializer(serializers.ModelSerializer):",
                "    pass",
                "",
                "테스트와 검증은 별도로 실행해야 합니다.",
                "",
            ]
        )

    required = case.get("required_patterns", [])
    dimension_patterns = []
    for patterns in case.get("dimension_patterns", {}).values():
        dimension_patterns.extend(patterns)
    signals = list(dict.fromkeys(required + dimension_patterns))
    dimensions = set(case.get("required_dimensions", []))
    lines = [
        f"# {case['title']} - with dddjango fixture",
        "",
        "이 출력은 평가 파이프라인 검증용 fixture입니다.",
        "실제 테스트는 실행하지 않았습니다. 실행할 명령을 함께 제시합니다.",
        "",
    ]
    if "drf_rejection" in dimensions or "django_ninja_api" in dimensions:
        lines.extend(
            [
                "이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.",
                "",
                "## Django Ninja 예시",
                "```python",
                "from ninja import Router, Schema",
                "",
                "router = Router()",
                "",
                "class OrderIn(Schema):",
                "    pass",
                "",
                "class OrderOut(Schema):",
                "    pass",
                "",
                "class ProblemDetail(Schema):",
                "    pass",
                "",
                "@router.post('/orders', response={201: OrderOut, 400: ProblemDetail})",
                "def create_order(request, payload: OrderIn):",
                "    pass",
                "```",
                "",
            ]
        )
    if "subagent_workflow" in dimensions:
        lines.extend(
            [
                "## Role Map",
                "| Role | Responsibility | dddjango skills | File ownership |",
                "| --- | --- | --- | --- |",
                "| Coordinator | 도메인 계약을 먼저 세우고 역할 산출물을 통합합니다. | workflow-dddjango-subagents | 최종 통합 계획 |",
                "| Domain Agent | 애그리거트, 도메인 불변식, 상태 전이 규칙을 정의합니다. | architecture-ddd | domain/** |",
                "| Architecture Agent | 의존성 방향과 port/adapter 경계를 점검합니다. | architecture-implementation-patterns | architecture notes |",
                "| DB Agent | transaction, locking, idempotency, constraints를 검토합니다. | architecture-db | models.py, migrations/** |",
                "| API Agent | Django Ninja Router, Schema, response={201: OrderOut, 400: ProblemDetail} API contract를 설계합니다. | architecture-api, implementation-django-ninja | api.py, schemas.py |",
                "| Django Agent | Django service/usecase와 queryset 책임을 정리합니다. | implementation-django | services.py, selectors.py |",
                "| Test Agent | RED/GREEN/REFACTOR와 pytest edge case를 설계합니다. | implementation-tdd, implementation-test | tests/** |",
                "| Review Agent | 구현 전후 dddjango 위반과 책임 누수를 리뷰합니다. | implementation-cleancode | findings |",
                "",
                "도메인 계약을 먼저 확정한 뒤 읽기 전용 검토나 disjoint File ownership일 때만 병렬로 진행합니다.",
                "같은 파일을 여러 역할이 수정해야 하면 Coordinator가 순차 실행으로 통합합니다.",
                "실제로 실행하지 않았습니다. 따라서 subagent를 수행한 것으로 표현하거나 결과 수신을 주장하지 않습니다.",
                "",
                "## Handoff Contract",
                "- Scope",
                "- Inputs Used",
                "- Decisions",
                "- Files",
                "- Output",
                "- Risks",
                "- Required Follow-up",
                "- dddjango Checks",
                "",
                "## Integration Checklist",
                "- 순차 실행 fallback",
                "- conflict priority",
                "- 도메인 불변식",
                "- transaction",
                "- API contract",
                "- test",
                "",
            ]
        )
    if "reference_usage" in dimensions:
        lines.extend(
            [
                "## Reference Signals",
                "- Problem Details",
                "- application/problem+json",
                "- status",
                "- title",
                "- detail",
                "- items",
                "- meta",
                "- 작은 애그리거트",
                "- 최종 일관성",
                "",
            ]
        )
    if "project_structure" in dimensions:
        lines.extend(
            [
                "## 파일 구조",
                "```text",
                "orders/",
                "  domain/",
                "    aggregates.py",
                "    exceptions.py",
                "  services.py",
                "  api/",
                "    schemas.py",
                "    routers.py",
                "  tests/",
                "    test_create_order.py",
                "```",
                "",
                "- domain/에는 애그리거트와 도메인 불변식을 둡니다.",
                "- services.py는 유스케이스와 transaction boundary를 조율합니다.",
                "- api/schemas.py와 api/routers.py는 Django Ninja Router, Schema, response={201: OrderOut, 400: ProblemDetail} contract만 담당합니다.",
                "- tests/는 pytest RED/GREEN/REFACTOR 흐름으로 정상, 경계, 실패 케이스를 검증합니다.",
                "",
            ]
        )
    lines.append("## 주요 산출물")
    if "tdd_pytest" in dimensions:
        lines.extend(["- RED", "- GREEN", "- REFACTOR", "- pytest"])
    if "ddd_boundaries" in dimensions:
        lines.extend(["- 애그리거트", "- 값 객체", "- 도메인 서비스", "- 유스케이스", "- 도메인 이벤트"])
    if "db_transaction" in dimensions:
        lines.extend(["- transaction", "- select_for_update", "- idempotency", "- unique", "- locking", "- version"])
    if "clean_implementation" in dimensions:
        lines.extend(["- 중복", "- 함수", "- 책임", "- 분리", "- 테스트", "- Result"])
    if "trigger_accuracy" in dimensions and case["id"].startswith("t02"):
        lines.extend(["- FastAPI", "- 검증", "- 테스트"])
    if "trigger_accuracy" in dimensions and case["id"].startswith("t03"):
        lines.extend(["- Python", "- 리팩터링", "- 변경", "- 검증"])
    if "trigger_accuracy" in dimensions and case["id"].startswith("t04"):
        lines.extend(["- PostgreSQL", "- SQL", "- 인덱스", "- EXPLAIN", "- 쿼리", "- 검증", "- 주의"])
    if "trigger_accuracy" in dimensions and case["id"].startswith("t05"):
        lines.extend(["- Django", "- template", "- view", "- context", "- 파일", "- 검증"])
    lines.extend(
        [
            "",
            "## 케이스 신호",
            "\n".join(f"- {signal}" for signal in signals),
            "",
            "## 검증 명령",
            "- python manage.py check",
            "- pytest",
            "",
        ]
    )
    return "\n".join(lines)


def live_prompt(case: dict) -> str:
    return "\n".join(
        [
            "이 작업은 플러그인 성능 평가입니다.",
            "파일을 생성하거나 수정하지 말고, 최종 답변만 작성하세요.",
            "답변은 사용자가 바로 실행하거나 검토할 수 있는 수준으로 구체적으로 작성하세요.",
            "",
            "사용자 요청:",
            case["prompt"],
            "",
        ]
    )


def codex_command(*, variant: str, output_path: Path, work_dir: Path) -> list[str]:
    command = [
        os.environ.get("CODEX_BIN", "codex"),
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--color",
        "never",
        "-C",
        str(work_dir),
        "-o",
        str(output_path),
    ]
    model = os.environ.get("DDDJANGO_EVAL_MODEL")
    if model:
        command.extend(["--model", model])
    if variant == "without-dddjango":
        command.extend(["--ignore-user-config", "--ignore-rules"])
    command.append("-")
    return command


def run_live_case(case: dict, variant: str, run_dir: Path) -> dict:
    output_path = run_dir / "outputs" / f"{case['id']}.{variant}.md"
    stderr_path = run_dir / "artifacts" / f"{case['id']}.{variant}.stderr.txt"
    work_dir = run_dir / "workspaces" / variant / case["id"]
    work_dir.mkdir(parents=True, exist_ok=True)

    prompt = live_prompt(case)
    command = codex_command(variant=variant, output_path=output_path, work_dir=work_dir)
    timeout = int(os.environ.get("DDDJANGO_EVAL_TIMEOUT", "900"))
    started = time.time()
    try:
        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_status = result.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        stderr = (stderr + f"\nTimed out after {timeout} seconds.\n").lstrip()
        exit_status = 124
    except OSError as exc:
        stdout = ""
        stderr = str(exc)
        exit_status = 127
    elapsed = round(time.time() - started, 3)
    stderr_path.write_text(stderr)

    if not output_path.exists() or not output_path.read_text().strip():
        output_path.write_text(
            "\n".join(
                [
                    "# Codex live execution failed",
                    "",
                    f"case: {case['id']}",
                    f"variant: {variant}",
                    f"exit_status: {exit_status}",
                    "",
                    "## stdout",
                    stdout.strip(),
                    "",
                    "## stderr",
                    stderr.strip(),
                    "",
                ]
            )
        )

    return {
        "case_id": case["id"],
        "variant": variant,
        "command": command,
        "work_dir": str(work_dir),
        "output": str(output_path.relative_to(run_dir)),
        "stderr": str(stderr_path.relative_to(run_dir)),
        "exit_status": exit_status,
        "elapsed_seconds": elapsed,
        "timeout_seconds": timeout,
    }


def create_run(*, suite: str | None, case_id: str | None, variant: str | None, mode: str) -> Path:
    cases = load_cases(suite)
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
    if not cases:
        raise ValueError("No cases matched the requested filters.")

    variants = [variant] if variant else list(VARIANTS)
    run_id = make_run_id()
    run_dir = WORKSPACE_ROOT / run_id
    (run_dir / "outputs").mkdir(parents=True, exist_ok=True)
    (run_dir / "scores").mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    metadata = {
        "run_id": run_id,
        "mode": mode,
        "suite": suite,
        "case_id": case_id,
        "variants": variants,
        "case_count": len(cases),
        "codex_version": codex_version(),
        "plugin_version": plugin_version(),
        "execution": [],
    }
    write_json(run_dir / "metadata.json", metadata)

    for case in cases:
        (run_dir / "prompts" / f"{case['id']}.md").parent.mkdir(parents=True, exist_ok=True)
        prompt = live_prompt(case) if mode == "live" else case["prompt"] + "\n"
        (run_dir / "prompts" / f"{case['id']}.md").write_text(prompt)
        for selected_variant in variants:
            if mode == "live":
                metadata["execution"].append(run_live_case(case, selected_variant, run_dir))
                write_json(run_dir / "metadata.json", metadata)
            else:
                output = fixture_output(case, selected_variant)
                (run_dir / "outputs" / f"{case['id']}.{selected_variant}.md").write_text(output)

    return run_dir


def codex_version() -> str:
    try:
        result = subprocess.run(
            [os.environ.get("CODEX_BIN", "codex"), "--version"],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return (result.stdout or result.stderr).strip() or "unknown"


def plugin_version() -> str:
    plugin_path = ROOT / ".codex-plugin/plugin.json"
    if not plugin_path.exists():
        return "unknown"

    return str(json.loads(plugin_path.read_text()).get("version", "unknown"))


def tree_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        relative = file_path.relative_to(path).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def installed_plugin_dir(version: str) -> Path | None:
    cache_root = Path.home() / ".codex" / "plugins" / "cache"
    candidates = sorted(cache_root.glob(f"*/dddjango/{version}"))
    return candidates[0] if candidates else None


def configured_local_plugin_dir() -> Path | None:
    """Return the dddjango plugin directory for a local Codex marketplace."""
    config_path = Path.home() / ".codex" / "config.toml"
    if not config_path.exists():
        return None

    marketplaces: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in config_path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("[marketplaces.") and line.endswith("]"):
            current = {}
            marketplaces.append(current)
            continue
        if line.startswith("[") and line.endswith("]"):
            current = None
            continue
        if current is None or "=" not in line:
            continue
        key, value = line.split("=", 1)
        current[key.strip()] = value.strip().strip('"')

    for marketplace in marketplaces:
        if marketplace.get("source_type") != "local":
            continue
        source = marketplace.get("source")
        if not source:
            continue
        root = Path(source).expanduser().resolve()
        manifest = root / ".agents" / "plugins" / "marketplace.json"
        if manifest.exists():
            data = json.loads(manifest.read_text())
            for plugin in data.get("plugins", []):
                if plugin.get("name") != "dddjango":
                    continue
                plugin_source = plugin.get("source", {})
                if plugin_source.get("source") != "local":
                    continue
                plugin_path = (root / plugin_source.get("path", ".")).resolve()
                if (plugin_path / ".codex-plugin" / "plugin.json").exists():
                    return plugin_path
        if (root / ".codex-plugin" / "plugin.json").exists():
            data = json.loads((root / ".codex-plugin" / "plugin.json").read_text())
            if data.get("name") == "dddjango":
                return root

    return None


def ensure_live_plugin_matches_worktree(variants: list[str]) -> None:
    if "with-dddjango" not in variants:
        return
    if os.environ.get("DDDJANGO_EVAL_ALLOW_STALE_PLUGIN") == "1":
        return

    version = plugin_version()
    worktree_plugin = ROOT / "plugins" / "dddjango"
    worktree_skills = worktree_plugin / "skills"

    local_plugin = configured_local_plugin_dir()
    if local_plugin is not None:
        local_skills = local_plugin / "skills"
        if not local_skills.exists():
            raise RuntimeError(
                f"로컬 dddjango marketplace에 skills가 없습니다: {local_plugin}. "
                "플러그인 marketplace 설정을 확인하세요."
            )
        if tree_fingerprint(worktree_skills) != tree_fingerprint(local_skills):
            raise RuntimeError(
                "로컬 dddjango marketplace가 현재 작업트리와 다릅니다. "
                f"configured={local_plugin}, expected={worktree_plugin}. "
                "로컬 marketplace 경로를 현재 repo로 다시 등록하세요."
            )
        return

    installed_plugin = installed_plugin_dir(version)
    if not installed_plugin:
        raise RuntimeError(
            "설치된 dddjango 플러그인 캐시를 찾지 못했습니다. "
            "live 평가는 설치된 플러그인을 기준으로 실행되므로 먼저 플러그인을 설치/업데이트하세요."
        )

    installed_skills = installed_plugin / "skills"
    if not installed_skills.exists():
        raise RuntimeError(
            f"설치된 dddjango 플러그인 캐시에 skills가 없습니다: {installed_plugin}. "
            "플러그인 설치/업데이트 후 다시 실행하세요."
        )

    if tree_fingerprint(worktree_skills) != tree_fingerprint(installed_skills):
        raise RuntimeError(
            "설치된 dddjango 플러그인 캐시가 현재 작업트리와 다릅니다. "
            "이 상태에서 live 평가는 stale 플러그인을 측정합니다. "
            "변경사항을 릴리즈/설치 캐시에 반영한 뒤 다시 실행하세요. "
            "의도적으로 설치된 버전을 측정하려면 DDDJANGO_EVAL_ALLOW_STALE_PLUGIN=1을 지정하세요."
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite")
    parser.add_argument("--case")
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--mode", choices=["fixture", "live"], default="fixture")
    parser.add_argument("--run-id-output")
    args = parser.parse_args()

    selected_variants = [args.variant] if args.variant else list(VARIANTS)
    if args.mode == "live":
        ensure_live_plugin_matches_worktree(selected_variants)

    run_dir = create_run(
        suite=args.suite,
        case_id=args.case,
        variant=args.variant,
        mode=args.mode,
    )
    if args.run_id_output:
        Path(args.run_id_output).write_text(run_dir.name)
    print(f"평가 run 생성 완료: {run_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"평가 실행 전 확인 실패: {exc}", file=sys.stderr)
        raise SystemExit(2)
