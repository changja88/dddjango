"""오류 계열→차단 단 매핑 표 스모크 (T0 A9 — verify-ontology [6]).

workspace/eval/fixtures/ontology_gate/cases/ 의 각 케이스를 임시 트리(사본 — 원본 불변,
registry_gate_smoke 관례)로 조립해 게이트/메타 도구를 실행하고, gate-report/1 의
«단» 필드가 매핑 표(ontology-authoring.md §6 = t0-plan §2 A9)의 기대 차단 단과
일치하는지 단언한다. green 대조군(cons 셀 예외 실증)은 통과를 단언한다.

사용: .venv/bin/python workspace/tools/ontology_gate_smoke.py
exit 0 = 전 케이스 기대 일치 / 1 = 불일치 / 2 = 도구 오류
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from ontology_canon import REPO_ROOT

CASES_DIR = REPO_ROOT / "workspace" / "eval" / "fixtures" / "ontology_gate" / "cases"
TOOLS = REPO_ROOT / "workspace" / "tools"
ONTOLOGY = REPO_ROOT / "ontology"

# (케이스, 도구, 기대 — gate 는 실패 단 이름(None=통과), meta 는 exit 1 기대)
EXPECTATIONS = [
    ("blank-node-rules", "gate", "2-canon"),
    ("blank-node-shape", "gate", "2-canon"),
    ("cons-cell-green", "gate", None),
    ("unregistered-prefix", "gate", "2-canon"),
    ("hash-comment", "gate", "2-canon"),
    ("noncanon-serialization", "gate", "2-canon"),
    ("hash-mutation", "gate-fault", "3-hash"),
    ("expression-iri-compaction", "gate", "1-parse"),
    ("shacl-unwired-norm", "gate-full", "4-shacl"),
    ("closed-nonleaf", "meta", "2층"),
    ("closed-noignore", "meta", "2층"),
]


def build_tree(case: str, tmp: Path, with_corpus: bool) -> Path:
    tree = tmp / case
    shutil.copytree(CASES_DIR / case, tree)
    shutil.copy2(ONTOLOGY / "prefixes.ttl", tree / "prefixes.ttl")
    if with_corpus:
        (tree / "vocab").mkdir(exist_ok=True)
        shutil.copy2(ONTOLOGY / "vocab" / "djr.ttl", tree / "vocab" / "djr.ttl")
        (tree / "shapes").mkdir(exist_ok=True)
        for shp in ("djr-shapes.ttl", "meta-house.ttl"):
            src = ONTOLOGY / "shapes" / shp
            if src.exists():
                shutil.copy2(src, tree / "shapes" / shp)
    return tree


def run_tool(script: str, tree: Path, extra_env: dict | None = None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(TOOLS)
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, str(TOOLS / script), "--root", str(tree)]
        + (["--json"] if script == "ontology_gate.py" else []),
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return proc


def failed_stages(report: dict) -> set[str]:
    stages = set()
    for res in report["results"]:
        for st in res["stages"]:
            if st["status"] == "fail":
                stages.add(st["stage"])
    return stages


def main() -> int:
    mismatches = 0
    with tempfile.TemporaryDirectory(prefix="ontology-gate-smoke-") as td:
        tmp = Path(td)
        for case, mode, expect in EXPECTATIONS:
            if not (CASES_DIR / case).is_dir():
                print(f"[gate-smoke] RED {case}: 케이스 디렉터리 부재")
                mismatches += 1
                continue

            if mode == "meta":
                tree = build_tree(case, tmp, with_corpus=True)
                proc = run_tool("ontology_meta_shacl.py", tree)
                ok = proc.returncode == 1 and "2층(하우스) RED" in proc.stdout
                print(f"[gate-smoke] {'ok ' if ok else 'RED'} {case}: meta 2층 red 기대 → exit {proc.returncode}")
                if not ok:
                    mismatches += 1
                continue

            with_corpus = mode == "gate-full"
            extra_env = {"ONTOLOGY_GATE_FAULT": "hash-mutation"} if mode == "gate-fault" else None
            tree = build_tree(case, tmp, with_corpus=with_corpus)
            proc = run_tool("ontology_gate.py", tree, extra_env)
            try:
                report = json.loads(proc.stdout[: proc.stdout.rfind("}") + 1])
            except (ValueError, AttributeError):
                print(f"[gate-smoke] RED {case}: gate-report JSON 파스 실패\n{proc.stdout[-400:]}")
                mismatches += 1
                continue

            stages = failed_stages(report)
            if expect is None:
                ok = proc.returncode == 0 and not stages
                detail = "통과" if ok else f"실패 단 {sorted(stages)}"
            else:
                ok = expect in stages
                detail = f"실패 단 {sorted(stages)}"
            print(f"[gate-smoke] {'ok ' if ok else 'RED'} {case}: 기대 {expect or '통과(green 대조군)'} → {detail}")
            if not ok:
                mismatches += 1

    print(f"[gate-smoke] {len(EXPECTATIONS)}케이스 — 불일치 {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
