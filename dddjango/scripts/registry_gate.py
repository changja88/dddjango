#!/usr/bin/env python3
"""registry 27종 «판정 차분» 게이트 — 이번 런이 위반을 «늘렸는가»만 판정한다.

왜 차분인가(2026-08-12 라운드 1′ P3′ · 적대 리뷰 Goodhart 렌즈): brownfield 에선
legacy 위반이 상존해 「루트 registry 전체 green」이 문자 그대로는 영원히 불가능하고,
그 모순이 세션의 자체 귀속 발명을 낳았다(라운드 1′ 실측). 경로 매칭식 귀속(변경 집합
대조)은 다섯 계열 공격에 뚫린다 — base 자기 선택·부재(#488) 위반의 경로 부재·검사기
출력 형식 이질·빈 변경 집합 역이용·.gitignore 은닉(전부 재현 실측). 판정 차분은 그
전부를 한 설계로 닫는다:

  앵커 상태에서 registry 실행 → 위반 라인 집합 L
  현재 상태에서 registry 실행 → 위반 라인 집합 N
  귀속 = N ∖ L  (라인번호·스냅숏 경로만 정규화 — 경로 «파싱»을 하지 않는다)

- **앵커는 actor 가 고르지 않는다** — 라운드에선 대장의 앵커 커밋, 파이프라인에선
  Phase 2 진입 직전 기록되는 build-start 앵커(`commands/dddjango.md` 절차 소유)를
  호출자가 그대로 넘긴다. 앵커=HEAD 이고 working tree 가 clean 이면 차분이 공허하므로
  사용 오류(exit 1)다 — 「커밋 뒤 게이트」로 판정을 비우는 우회를 막는다.
- **귀속 0 ≠ 전체 clean** — legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고한다
  (침묵 금지). BC 하나가 clean 한지는 `bc_registry_run.py`(그림자 전수)가 답한다 —
  두 도구는 같은 로스터(`checker_registry.py`)를 쓰되 묻는 것이 다르다.
- **이관 빚 채널**: `--legacy-debt-file` 의 사용자 승인 목록(줄 형식: `#<규칙> <부분문자열>`)
  에 맞는 귀속은 exit 에서 빼되 «빚» 절로 반드시 보고한다 — 빚은 기록 근거이지 legacy
  모양을 «추가로» 복사할 근거가 아니다.
- 비-git TARGET 은 fail-closed: 차분 불능이므로 현재 위반 전부를 귀속으로 본다.
- 검사기가 red 인데 위반 라인을 못 파싱하면 그 검사기 몫을 합성 귀속으로 남긴다(fail-closed).

사용: python3 registry_gate.py <저장소 루트> --anchor <ref> [--legacy-debt-file <path>]
exit 0 = 귀속 0 / exit 2 = 귀속 존재 / exit 1 = 사용 오류·재료 결손·공허 차분.
"""
from __future__ import annotations

import argparse
import ast
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checker_target  # noqa: E402
from checker_registry import REGISTRY, checker_argv  # noqa: E402

_FINDING_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[#\d+\].*)$")
_LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")
_IGNORE_COPY: "tuple[str, ...]" = (
    ".git", ".venv", "venv", "__pycache__", "*.pyc", "node_modules",
    "graphify-out", ".mypy_cache", ".pytest_cache", ".ruff_cache", "staticfiles",
    # F-C(2026-08-14): 숨김 디렉터리 전부 = 도구·하네스 영역(`.codex/`·`.dddjango/` 등) —
    # 검사 표면이 아니다(라운드 3 실측: `.codex/cleanroom-guard.py` #493×4 오탐 귀속).
    ".*", "site-packages", "build", "dist",
)


def _git(root: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def _snapshot_anchor(root: Path, anchor: str, dest: Path) -> "str | None":
    """앵커 커밋의 트리를 dest 에 푼다. 실패 사유 문자열 또는 None."""
    dest.mkdir(parents=True)
    archive = subprocess.Popen(
        ["git", "-C", str(root), "archive", anchor], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    untar = subprocess.run(["tar", "-x", "-C", str(dest)], stdin=archive.stdout, capture_output=True)
    archive.stdout.close()  # type: ignore[union-attr]
    _, arch_err = archive.communicate()
    if archive.returncode != 0:
        return f"git archive 실패: {arch_err.decode(errors='replace').strip()}"
    if untar.returncode != 0:
        return f"tar 실패: {untar.stderr.decode(errors='replace').strip()}"
    return None


def _snapshot_current(root: Path, dest: Path) -> None:
    """working tree 를 비-git 사본으로 복사한다(무거운 비-소스 디렉터리 제외)."""
    shutil.copytree(root, dest, ignore=shutil.ignore_patterns(*_IGNORE_COPY))


def _parse_fail_findings(target: Path) -> "set[str]":
    """이 인터프리터로 파싱 불가한 검사 대상 — fail-open(침묵 스킵) 방지 합성 귀속(F-A 2026-08-14).

    앵커·현재 «양쪽» 스냅숏에 같은 스캔을 걸어 차분 원리를 태운다 — 앵커에도 있던
    깨진 파일은 legacy(L∩N), 새로 생긴 것만 귀속(N∖L). 고의 투입으로 red 를
    «판정 불능(exit 1)»으로 바꾸는 우회(적대 리뷰 A1)가 성립하지 않는다.
    """
    out: "set[str]" = set()
    for p in sorted(target.rglob("*.py")):
        if any(seg.startswith(".") for seg in p.relative_to(target).parts[:-1]):
            continue  # 숨김 디렉터리 = 도구·하네스 영역(F-C)
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            out.add(f"(pre-scan) :: [#parse-fail] {p.relative_to(target)}: 이 인터프리터"
                    f"({sys.version_info[0]}.{sys.version_info[1]})로 파싱 불가 — 검사기가 침묵 스킵하는 파일")
    return out


def _run_registry(target: Path) -> "tuple[dict[str, int], set[str]]":
    """로스터 전체를 돌려 (검사기별 exit, 정규화 위반 라인 집합)을 낸다."""
    exits: "dict[str, int]" = {}
    findings: "set[str]" = set()
    prefixes: "tuple[str, ...]" = (str(target) + "/", str(target))
    for script, auto in REGISTRY:
        proc = subprocess.run(
            checker_argv(sys.executable, script, str(target), auto),
            capture_output=True, text=True,
        )
        exits[script] = proc.returncode
        parsed: int = 0
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            m = _FINDING_RE.match(raw)
            if m is None:
                continue
            line: str = m.group(1)
            for p in prefixes:  # 스냅숏 절대 경로 echo 정규화(A3)
                line = line.replace(p, "")
            line = _LINENO_RE.sub(":N", line)  # 라인번호 정규화(상하 이동 오탐 방지)
            findings.add(f"{script} :: {line}")
            parsed += 1
        if proc.returncode != 0 and parsed == 0:
            findings.add(f"{script} :: [진단 미파싱 · exit {proc.returncode}] fail-closed 귀속")
    return exits, findings


def _load_debt(path: Path) -> "list[tuple[str, str]]":
    """이관 빚 승인 목록 — 줄 형식 `#<규칙번호> <부분문자열>` (빈 줄·`//` 주석 허용)."""
    out: "list[tuple[str, str]]" = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line: str = raw.strip()
        if not line or line.startswith("//"):
            continue
        parts: "list[str]" = line.split(None, 1)
        if len(parts) != 2 or not parts[0].startswith("#"):
            raise ValueError(f"빚 목록 줄 형식 오류: {raw!r} — `#<규칙> <부분문자열>`")
        out.append((parts[0], parts[1]))
    return out


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("target")
    ap.add_argument("--anchor", required=False, default=None,
                    help="차분 기준(대장 앵커 또는 build-start 앵커) — actor 가 임의로 고르지 않는다")
    ap.add_argument("--legacy-debt-file", default=None)
    ns = ap.parse_args(argv)

    root: Path = Path(ns.target).resolve()
    if not root.is_dir():
        print(f"사용 오류: TARGET {root} 이 디렉터리가 아니다", file=sys.stderr)
        return 1
    bad: "str | None" = checker_target.bc_shaped_target_reason(str(root))
    if bad is not None:
        print(f"사용 오류: {bad}", file=sys.stderr)
        return 1

    debt_rules: "list[tuple[str, str]]" = []
    if ns.legacy_debt_file is not None:
        debt_path: Path = Path(ns.legacy_debt_file)
        if not debt_path.is_file():
            print(f"재료 결손: 빚 목록 {debt_path} 없음", file=sys.stderr)
            return 1
        debt_rules = _load_debt(debt_path)

    is_git: bool = _git(root, "rev-parse", "--is-inside-work-tree").returncode == 0

    with tempfile.TemporaryDirectory() as td:
        cur: Path = Path(td) / "current"
        _snapshot_current(root, cur)

        if not is_git:
            print("주의: 비-git TARGET — 차분 불능이라 fail-closed(현재 위반 전량 귀속)")
            exits_n, n_set = _run_registry(cur)
            n_set |= _parse_fail_findings(cur)
            l_set: "set[str]" = set()
            exits_l: "dict[str, int]" = {}
            anchor_sha: str = "(비-git)"
        else:
            if ns.anchor is None:
                print("사용 오류: git 저장소에는 --anchor <ref> 가 필수다 — 라운드=대장 앵커 · "
                      "파이프라인=Phase 2 진입 직전 기록된 build-start 앵커", file=sys.stderr)
                return 1
            rev = _git(root, "rev-parse", "--verify", f"{ns.anchor}^{{commit}}")
            if rev.returncode != 0:
                print(f"사용 오류: 앵커 {ns.anchor!r} resolve 불능 — {rev.stderr.strip()}", file=sys.stderr)
                return 1
            anchor_sha = rev.stdout.strip()
            head = _git(root, "rev-parse", "HEAD").stdout.strip()
            dirty: bool = bool(_git(root, "status", "--porcelain").stdout.strip())
            if anchor_sha == head and not dirty:
                print("사용 오류: 앵커=HEAD 이고 working tree 가 clean — 차분이 공허하다. "
                      "게이트는 구현 커밋 «전»에 돌리거나, 런 시작점 앵커를 지정하라(공허 green 차단).",
                      file=sys.stderr)
                return 1
            anc: Path = Path(td) / "anchor"
            err: "str | None" = _snapshot_anchor(root, anchor_sha, anc)
            if err is not None:
                print(f"재료 결손: {err}", file=sys.stderr)
                return 1
            exits_l, l_set = _run_registry(anc)
            l_set |= _parse_fail_findings(anc)
            exits_n, n_set = _run_registry(cur)
            n_set |= _parse_fail_findings(cur)

    attributed: "list[str]" = sorted(n_set - l_set)
    resolved: "list[str]" = sorted(l_set - n_set)
    residual: "list[str]" = sorted(l_set & n_set)

    debt: "list[str]" = []
    if debt_rules:
        rest: "list[str]" = []
        for line in attributed:
            hit: bool = any(f"[{tag}]" in line and sub in line for tag, sub in debt_rules)
            (debt if hit else rest).append(line)
        attributed = rest

    print(f"# registry_gate — 판정 차분 · {root.name} · 앵커 {anchor_sha[:12]}")
    print("**귀속 0 ≠ 전체 clean** — 이 게이트는 «이번 런이 위반을 늘렸나»만 판정한다(legacy 격리).")
    print("| 검사기 | anchor | current |")
    print("|---|---|---|")
    for script, _auto in REGISTRY:
        print(f"| `{script}` | {exits_l.get(script, '—')} | {exits_n.get(script, '—')} |")
    print(f"\n== 귀속(N∖L) {len(attributed)}건 ==")
    for line in attributed:
        print(f"  {line}")
    if debt:
        print(f"\n== 이관 빚(승인 목록 매칭 — exit 제외·기록 의무) {len(debt)}건 ==")
        for line in debt:
            print(f"  {line}")
    by_checker: "dict[str, int]" = {}
    for line in residual:
        by_checker[line.split(" :: ", 1)[0]] = by_checker.get(line.split(" :: ", 1)[0], 0) + 1
    print(f"\n== legacy 잔존(L∩N) {len(residual)}건 · 해소(L∖N) {len(resolved)}건 ==")
    for script in sorted(by_checker):
        print(f"  {script}: {by_checker[script]}")
    print(f"\n판정: 귀속 {len(attributed)}건 → {'green(신규 위반 없음)' if not attributed else 'red'}")
    return 0 if not attributed else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
