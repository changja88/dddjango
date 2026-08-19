#!/usr/bin/env python3
"""registry_gate 스모크 — 판정 차분 게이트의 계약을 «공격 재현»으로 고정한다.

fixture_matrix 밖에 두는 이유: 그 레인의 hermetic 원칙은 «비-git 임시 사본»인데
이 게이트는 git(앵커)이 재료라 원칙이 상반된다 — 한 도구에 두 원칙을 섞지 않는다.
release 게이트 [2/7] 검증 세트에 등록되어 함께 돈다(Makefile).

케이스(2026-08-12 적대 리뷰 Goodhart·회귀 렌즈 재현 실측의 고정):
  V  공허 차분(앵커=HEAD·clean)          → exit 1 (커밋-후-게이트 우회 차단)
  A  귀속 red(working 신규 위반)          → exit 2 + 그 위반이 귀속 절에
  B  legacy-only(앵커에 이미 있던 위반)    → exit 0 + 잔존 보고(침묵 금지)
  C  A1 공격(위반을 «선커밋»하고 무해 변경) → exit 2 (경로-매칭 게이트가 뚫리던 자리)
  D  A2 공격(골격 칸 «삭제» — 부재 위반)   → exit 2 (부재는 변경 집합에 경로가 없다)
  E  빚 채널(승인 목록 매칭)              → exit 0 + «이관 빚» 절 보고
  U  usage 오류(알 수 없는 flag)          → exit 1 (F3 — 문면 계약 1=usage·2=위반,
                                            argparse 기본 exit 2 로 새지 않는다)

사용: python3 registry_gate_smoke.py
exit 0 = 전 케이스 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import shutil
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
GATE: Path = ROOT / "dddjango" / "scripts" / "registry_gate.py"
BASE_FIXTURE: Path = ROOT / "workspace" / "eval" / "fixtures" / "skeleton" / "good_bc"

_GIT_ID: "list[str]" = ["-c", "user.email=smoke@dddjango", "-c", "user.name=smoke"]

# 위반 재료: driving 잎이 애그리거트를 import(#96 계열 — 앵커 이후 «신규»로 심는다)
_VIOLATION_REL: str = "application/orders/driving_layer/api/order/schema/schema_smoke.py"
_VIOLATION_SRC: str = "from application.orders.domain_layer.order.order import Order\n\n_N: str = Order.__name__\n"



def _scrubbed_env() -> "dict[str, str]":
    """검사기 하위 실행 env — 사용자 DJR_FINDINGS_JSON 오염 차단(T2-1 적대 검증 레인 S 7번 잔여)."""
    env = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    return env

def _git(repo: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(repo), *_GIT_ID, *args], capture_output=True, text=True)


def _make_repo(td: Path, name: str) -> "tuple[Path, str]":
    """good_bc 사본으로 git repo 를 만들고 앵커 커밋 해시를 돌려준다."""
    repo: Path = td / name
    shutil.copytree(BASE_FIXTURE, repo)
    for step in (("init", "-q"), ("add", "-A"), ("commit", "-q", "-m", "anchor")):
        proc = _git(repo, *step)
        if proc.returncode != 0:
            raise RuntimeError(f"git {step[0]} 실패: {proc.stderr.strip()}")
    return repo, _git(repo, "rev-parse", "HEAD").stdout.strip()


def _gate(repo: Path, anchor: str, extra: "list[str] | None" = None) -> "tuple[int, str]":
    proc = subprocess.run(
        [sys.executable, str(GATE), str(repo), "--anchor", anchor] + (extra or []),
        capture_output=True, text=True, env=_scrubbed_env(),
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    if not GATE.is_file() or not BASE_FIXTURE.is_dir():
        print("재료 결손: registry_gate.py 또는 skeleton/good_bc fixture 없음", file=sys.stderr)
        return 1
    rows: "list[tuple[str, int, int, bool, str]]" = []  # (케이스, 기대, 실측, 내용검사, 비고)

    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)

        # V — 공허 차분: 앵커=HEAD·clean → exit 1
        repo, anchor = _make_repo(td, "vacuous")
        code, out = _gate(repo, anchor)
        rows.append(("V 공허 차분", 1, code, "공허" in out, "앵커=HEAD·clean"))

        # A — working tree 신규 위반 → 귀속 red
        repo, anchor = _make_repo(td, "attributed")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("A 귀속 red", 2, code, "schema_smoke" in out.split("legacy 잔존")[0], "신규 위반이 귀속 절에"))

        # B — 앵커에 이미 있던 위반 + 무해 변경 → green + 잔존 보고
        repo, _pre = _make_repo(td, "legacy")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "legacy 포함 앵커")
        anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
        (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("B legacy-only green", 0, code, "잔존" in out and "귀속 0건" in out.replace("(N∖L) 0건", "귀속 0건"), "잔존 보고·귀속 0"))

        # C — A1 공격: 위반을 «선커밋»(앵커 이후) 후 무해 파일만 working 에
        repo, anchor = _make_repo(td, "precommit")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", "위반 선커밋")
        (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")
        code, out = _gate(repo, anchor)
        rows.append(("C 선커밋 공격", 2, code, "schema_smoke" in out, "HEAD 안 위반도 앵커 차분에 잡힘"))

        # D — A2 공격: 골격 고정 칸 삭제(부재 위반 — 경로가 존재하지 않음)
        repo, anchor = _make_repo(td, "absence")
        shutil.rmtree(repo / "application" / "orders" / "composition_root")
        code, out = _gate(repo, anchor)
        rows.append(("D 골격 접힘 공격", 2, code, "composition_root" in out, "부재 위반 귀속"))

        # E — 빚 채널: A 케이스 위반을 승인 목록으로 → green + 빚 절
        repo, anchor = _make_repo(td, "debt")
        (repo / _VIOLATION_REL).parent.mkdir(parents=True, exist_ok=True)
        (repo / _VIOLATION_REL).write_text(_VIOLATION_SRC, encoding="utf-8")
        debt: Path = td / "debt.txt"
        debt.write_text(
            "// 승인: 스모크 빚 — 같은 파일에 발화하는 태그 셋 전부(#95 격리·#96 잎·#490 트리 밖 파일)\n"
            "#95 schema_smoke\n#96 schema_smoke\n#490 schema_smoke\n",
            encoding="utf-8",
        )
        code, out = _gate(repo, anchor, ["--legacy-debt-file", str(debt)])
        rows.append(("E 빚 채널", 0, code, "이관 빚" in out and "schema_smoke" in out, "exit 제외·보고 필수"))

        # U — usage 오류: 알 수 없는 flag → 문면 계약 exit 1(F3 — argparse 기본 2 봉합).
        proc = subprocess.run(
            [sys.executable, str(GATE), str(repo), "--nope"],
            capture_output=True, text=True, env=_scrubbed_env(),
        )
        rows.append((
            "U usage exit 1", 1, proc.returncode,
            "사용 오류" in (proc.stdout + proc.stderr),
            "usage 오류는 exit 1(F3)",
        ))

    print("| 케이스 | 기대 exit | 실측 | 내용 | 판정 |")
    print("|---|---|---|---|---|")
    bad: int = 0
    for name, want, got, content_ok, note in rows:
        ok: bool = want == got and content_ok
        if not ok:
            bad += 1
        print(f"| {name} | {want} | {got} | {'✓' if content_ok else '✗'} | {'✓' if ok else '✗ 불일치'} | {note}")
    print(f"케이스 {len(rows)} · 일치 {len(rows) - bad} · 불일치 {bad}")
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
