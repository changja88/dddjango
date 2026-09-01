#!/usr/bin/env python3
"""pre-gate 픽스처 자가검증 러너 — green/red 미니 설계의 기대 판정을 고정한다.

무엇을 하나: `workspace/eval/fixtures/pregate/mini_repo/` 를 임시 git 저장소로
합성하고(커밋 1개), `design_pregate.py` 로 두 스펙을 돌린다.

  green-spec.md — 신규 BC 골격 전량·화이트리스트·5채널 전사가 오탐 0 임을 고정: exit 0.
  red-spec.md   — 의도 위반 3건(#81 트리 밖 칸 · #267 2클래스 1파일 · #472 contract
                  pydantic import)이 «정확히 그 귀속»으로 나옴을 고정: exit 2 +
                  귀속 규칙 집합 일치 + 귀속 건수 일치.

불일치면 exit 1(실행 출력 첨부). 검사기·트리 개정이 pre-gate 스텁 오탐을 새로 만들면
green 이 깨져 여기서 드러난다(설계 §9-3 드리프트 하네스의 픽스처 축).

사용: python3 workspace/tools/pregate_fixture_run.py [--keep]
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURES: Path = REPO_ROOT / "workspace" / "eval" / "fixtures" / "pregate"
EXECUTOR: Path = REPO_ROOT / "dddjango" / "scripts" / "design_pregate.py"

# red-spec.md 의 의도 위반 — 규칙 집합·건수가 이와 다르면 회귀다.
EXPECTED_RED_RULES: "frozenset[str]" = frozenset({"#81", "#267", "#472"})
EXPECTED_RED_COUNT: int = 3

_FORECAST_RULE_RE: "re.Pattern[str]" = re.compile(r"^\s*`[0-9a-f]{12}` .*?\[#([\w-]+)\]", re.M)


def _git(cwd: Path, *args: str) -> None:
    argv: "list[str]" = ["git", "-C", str(cwd), "-c", "core.hooksPath=",
                         "-c", "commit.gpgsign=false",
                         "-c", "user.email=fixture@local", "-c", "user.name=fixture"] + list(args)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} 실패: {proc.stderr.strip()}")


def _run_pregate(spec: Path, repo: Path, report: Path) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        [sys.executable, str(EXECUTOR), str(spec), str(repo), "--report", str(report)],
        capture_output=True, text=True)


def _dump(label: str, proc: "subprocess.CompletedProcess[str]") -> None:
    print(f"---- {label} stdout ----")
    print(proc.stdout)
    if proc.stderr.strip():
        print(f"---- {label} stderr ----")
        print(proc.stderr)


def main(argv: "list[str]") -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description="pre-gate 픽스처 러너")
    ap.add_argument("--keep", action="store_true", help="합성 저장소 보존(디버그)")
    ns: argparse.Namespace = ap.parse_args(argv)

    scratch: Path = Path(tempfile.mkdtemp(prefix="pregate-fixture-"))
    repo: Path = scratch / "repo"
    report: Path = scratch / "pregate-report.md"
    failures: "list[str]" = []
    try:
        shutil.copytree(FIXTURES / "mini_repo", repo)
        _git(repo, "init", "-q")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "fixture-baseline")

        green: "subprocess.CompletedProcess[str]" = _run_pregate(
            FIXTURES / "green-spec.md", repo, report)
        if green.returncode != 0:
            failures.append(f"green-spec 기대 exit 0 ≠ 실측 {green.returncode}")
            _dump("green", green)
        else:
            print("green-spec: exit 0 (예보 0) — 기대 일치")

        red: "subprocess.CompletedProcess[str]" = _run_pregate(
            FIXTURES / "red-spec.md", repo, report)
        rules: "list[str]" = [f"#{r}" for r in _FORECAST_RULE_RE.findall(red.stdout)]
        if red.returncode != 2:
            failures.append(f"red-spec 기대 exit 2 ≠ 실측 {red.returncode}")
        if set(rules) != EXPECTED_RED_RULES:
            failures.append(f"red-spec 귀속 규칙 집합 {sorted(set(rules))} ≠ 기대 {sorted(EXPECTED_RED_RULES)}")
        if len(rules) != EXPECTED_RED_COUNT:
            failures.append(f"red-spec 귀속 건수 {len(rules)} ≠ 기대 {EXPECTED_RED_COUNT}")
        if any(f.startswith("red-spec") for f in failures):
            _dump("red", red)
        else:
            print(f"red-spec: exit 2 · 귀속 {sorted(rules)} — 기대 일치")

        header_count: int = report.read_text(encoding="utf-8").count("## pre-gate 예보") \
            if report.is_file() else 0
        if header_count != 2:
            failures.append(f"리포트 append 횟수 {header_count} ≠ 기대 2 ({report})")

        if failures:
            print("\nFAIL — pre-gate 픽스처 기대 불일치:")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("\nPASS — pre-gate 픽스처 2종 기대 일치 (green 예보 0 · red 귀속 3건 정합)")
        return 0
    finally:
        if ns.keep:
            print(f"(--keep) 합성 저장소 보존: {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
