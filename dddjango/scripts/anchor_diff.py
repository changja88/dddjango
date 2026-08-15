#!/usr/bin/env python3
"""scope-render 직접 실행 검사기용 «판정 차분» 공용 모듈 — registry_gate 와 같은 원리(N∖L).

왜 검사기 안에도 차분이 필요한가(2026-08-15 S3-r2″ 레인 B 유효 정지 실측):
scope-렌더 계열(registry 2·5·6·15·16번)의 full-tree/전역 슬라이스는 앵커 이전부터 있던
잔존 위반까지 exit 2 로 «직접» 차단해, brownfield 대상에선 어떤 신규 산출물도
G2 를 통과할 수 없었다(같은 게이트를 다른 레인은 «해석»으로 통과 — 규정 비결정이
두 레인 판정 분기로 실증됐다). registry_gate(차분 계열)와 같은 판정 차분을
직접 실행 계열에도 제공한다(2번은 2026-08-15 재료 축 확정 후속 결선 — 다섯 계열이
같은 차분을 쓴다):

  앵커 상태(git archive 스냅숏)에서 같은 검사기 재실행 → 진단 라인 집합 L
  현재 실행(이 프로세스)이 출력한 진단               → 집합 N
  신규분 = N ∖ L — 신규분이 있으면 현행대로 exit 2(blocker),
  전건 앵커 기존분이면 exit 0 + 기존분 «전량 보고»(침묵 금지 — 정보 손실 0).

- `--anchor` 미지정이면 이 모듈은 관여하지 않는다(현행 동작 완전 보존).
- 앵커는 actor 가 고르지 않는다 — 라운드=대장 앵커 · 파이프라인=build_anchor
  (`commands/dddjango.md` Phase 2 step 6 절차 소유 · registry_gate 와 동일 관례).
- 앵커=HEAD 이고 working tree 가 clean 이면 차분이 공허하므로 사용 오류다
  (「커밋 뒤 검사」로 위반 전량을 기존분으로 세탁하는 우회 차단 — registry_gate 동형).
- 앵커 재실행은 `--anchor-baseline` 모드다: 앵커 트리에 없는 selected source 는
  호출측(여기)이 argv 에서 걷어내고(그 표면은 앵커에 없었으므로 그 진단은 정의상
  전건 신규다), 검사기는 그 모드에서 path-repeat selector 의 필수 개수 검사만
  완화한다. 이 모드는 비-git 스냅숏 전용이다(git 저장소 TARGET 에선 사용 오류 —
  실전 렌더 계약 완화로의 오용 차단).
- 앵커 재실행이 사용/분석 오류(exit 1)면 로스터 positional 기준선(`checker_registry.
  checker_argv` — registry_gate 가 내부 실행하는 그 호출)으로 한 번 강등하고,
  그마저 오류면 fail-closed(전량 신규 취급 = blocker 유지)한다.
- 라인 대조는 registry_gate 와 같은 정규화만 한다: 절대 경로 echo 제거·라인번호
  `:N` 치환 — 경로 «파싱»을 하지 않는다.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checker_registry import REGISTRY, checker_argv  # noqa: E402

# 앵커 스냅숏 재실행 모드 flag — 다섯 검사기(registry 2·5·6·15·16번)가 공통 수용한다.
BASELINE_FLAG: str = "--anchor-baseline"
# 사용자 승인 «이관 빚» 목록 flag — registry_gate 와 같은 이름·같은 줄 형식
# (`#<규칙> <부분문자열>`)·같은 의미(신규분 exit 에서 빼되 «빚» 절로 반드시 보고).
# 검사기(check-*.py) 소스는 이 리터럴을 직접 쓰지 않고 이 상수만 참조한다(checker_lint ㉢
# 는 check-*.py 만 훑는다 — registry_gate 처럼 이 모듈은 그 낱말 규율 밖이다).
DEBT_FLAG: str = "--legacy-debt-file"

_LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")


class AnchorDiffUsage(Exception):
    """--anchor 재료 결손·공허 차분 — 호출 검사기의 사용 오류 경로(exit 1)로 보낸다."""


def _git(root: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def is_git_worktree(root: Path) -> bool:
    """`--anchor-baseline` 의 비-git 전용 가드와 앵커 재료 검증이 함께 쓴다."""
    return _git(root, "rev-parse", "--is-inside-work-tree").returncode == 0


def resolve_anchor(root: Path, anchor: str) -> str:
    """앵커 재료 검증 — 비-git·resolve 불능·공허 차분(앵커=HEAD·clean)은 사용 오류."""
    if not is_git_worktree(root):
        raise AnchorDiffUsage(
            "--anchor 는 git 저장소 TARGET 에서만 쓸 수 있다 — 차분 재료가 없다"
        )
    rev = _git(root, "rev-parse", "--verify", f"{anchor}^{{commit}}")
    if rev.returncode != 0:
        raise AnchorDiffUsage(f"앵커 {anchor!r} resolve 불능 — {rev.stderr.strip()}")
    sha: str = rev.stdout.strip()
    head: str = _git(root, "rev-parse", "HEAD").stdout.strip()
    dirty: bool = bool(_git(root, "status", "--porcelain").stdout.strip())
    if sha == head and not dirty:
        raise AnchorDiffUsage(
            "앵커=HEAD 이고 working tree 가 clean — 차분이 공허하다. 검사는 구현 커밋 "
            "«전»에 돌리거나 런 시작점 앵커를 지정하라(«커밋 뒤 검사» 세탁 차단)"
        )
    return sha


def _snapshot_anchor(root: Path, sha: str, dest: Path) -> None:
    """앵커 커밋의 트리를 dest 에 푼다(registry_gate `_snapshot_anchor` 동형)."""
    dest.mkdir(parents=True)
    archive = subprocess.Popen(
        ["git", "-C", str(root), "archive", sha],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    untar = subprocess.run(
        ["tar", "-x", "-C", str(dest)], stdin=archive.stdout, capture_output=True
    )
    archive.stdout.close()  # type: ignore[union-attr]
    _, arch_err = archive.communicate()
    if archive.returncode != 0:
        raise AnchorDiffUsage(
            f"git archive 실패: {arch_err.decode(errors='replace').strip()}"
        )
    if untar.returncode != 0:
        raise AnchorDiffUsage(
            f"tar 실패: {untar.stderr.decode(errors='replace').strip()}"
        )


def _baseline_argv(
    script: Path, snapshot: Path, argv: "list[str]", path_flags: "frozenset[str]"
) -> "list[str]":
    """앵커 재실행 argv — 원 argv 에서 --anchor 를 걷고 target 을 스냅숏으로 바꾼다.

    앵커 트리에 없는 path-selector 값은 걷는다(그 표면의 진단은 정의상 전건 신규).
    전제: 다섯 검사기의 모든 `--flag` 는 값 1개를 받는다(store_true 없음 — 이
    모듈이 주입하는 BASELINE_FLAG 만 예외이고 그것은 원 argv 에 오지 않는다).
    """
    out: "list[str]" = [sys.executable, str(script), str(snapshot)]
    i: int = 0
    while i < len(argv):
        token: str = argv[i]
        if token in ("--anchor", DEBT_FLAG):
            i += 2
            continue
        if token.startswith(("--anchor=", DEBT_FLAG + "=")) or token == BASELINE_FLAG:
            i += 1
            continue
        if token.startswith("--"):
            name, eq, inline = token.partition("=")
            value: "str | None" = inline if eq else (argv[i + 1] if i + 1 < len(argv) else None)
            step: int = 1 if eq or value is None else 2
            if name in path_flags and value is not None and not (snapshot / value).exists():
                i += step
                continue
            out.append(token)
            if not eq and value is not None:
                out.append(value)
            i += step
            continue
        i += 1  # positional TARGET — 스냅숏 경로로 대체됨
    out.append(BASELINE_FLAG)
    return out


def _run_lines(cmd: "list[str]") -> "tuple[int, list[str]]":
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).splitlines()


def _load_debt(path: Path) -> "list[tuple[str, str]]":
    """이관 빚 승인 목록 — registry_gate `_load_debt` 동형(`#<규칙> <부분문자열>`)."""
    out: "list[tuple[str, str]]" = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line: str = raw.strip()
        if not line or line.startswith("//"):
            continue
        parts: "list[str]" = line.split(None, 1)
        if len(parts) != 2 or not parts[0].startswith("#"):
            raise AnchorDiffUsage(f"빚 목록 줄 형식 오류: {raw!r} — `#<규칙> <부분문자열>`")
        out.append((parts[0], parts[1]))
    return out


def _normalize(line: str, roots: "tuple[str, ...]") -> str:
    out: str = line.strip()
    for prefix in roots:  # 절대 경로 echo 정규화(registry_gate A3 동형)
        out = out.replace(prefix, "")
    return _LINENO_RE.sub(":N", out)  # 라인번호 정규화(상하 이동 오탐 방지)


def partition_exit(
    *,
    script: Path,
    label: str,
    target: Path,
    anchor: str,
    argv: "list[str]",
    findings: "list[str]",
    path_flags: "frozenset[str]" = frozenset(),
    debt_file: "str | None" = None,
) -> int:
    """현재 findings 를 앵커 기준선과 대조해 차분 절을 출력하고 exit 를 정한다.

    반환 2 = 신규분 존재(현행대로 blocker) · 0 = 전건 앵커 기존분(강등 + 보고).
    debt_file(사용자 승인 목록)에 맞는 신규분은 exit 에서 빼되 «빚» 절로 보고한다
    (registry_gate 와 동일 — 빚은 기록 근거이지 모양 복사 근거가 아니다).
    재료 결손·공허 차분은 AnchorDiffUsage — 호출측 사용 오류 경로(exit 1)가 받는다.
    호출측은 findings 를 이미 전량 출력한 «뒤» 이 함수를 부른다(정보 손실 0).
    """
    debt_rules: "list[tuple[str, str]]" = []
    if debt_file is not None:
        debt_path: Path = Path(debt_file)
        if not debt_path.is_file():
            raise AnchorDiffUsage(f"빚 목록 {debt_path} 없음")
        debt_rules = _load_debt(debt_path)
    resolved_target: Path = target.resolve()
    sha: str = resolve_anchor(resolved_target, anchor)
    with tempfile.TemporaryDirectory() as td:
        snap: Path = Path(td) / "anchor"
        _snapshot_anchor(resolved_target, sha, snap)
        code, lines = _run_lines(_baseline_argv(script, snap, argv, path_flags))
        used: str = "selector 렌더 재실행"
        if code not in (0, 2):
            # 앵커에서 렌더가 성립하지 않음(예: 필수 단일 selector 부재) —
            # 로스터 positional 기준선으로 강등(registry_gate 내부 실행과 같은 호출).
            auto: bool = dict(REGISTRY).get(script.name, False)
            code, lines = _run_lines(checker_argv(sys.executable, script.name, str(snap), auto))
            used = "positional 기준선(selector 렌더 불능 강등 — selector-lane 진단은 전량 신규 취급)"
        if code not in (0, 2):
            lines = []
            used = "기준선 불능(fail-closed — 전량 신규 취급)"
        roots: "tuple[str, ...]" = (
            str(snap) + "/", str(snap), str(resolved_target) + "/", str(resolved_target),
        )
        anchor_set: "set[str]" = {_normalize(line, roots) for line in lines}
        new: "list[str]" = []
        existing: "list[str]" = []
        for finding in findings:
            (existing if _normalize(finding, roots) in anchor_set else new).append(finding)

    debt: "list[str]" = []
    if debt_rules:  # 빚 매칭은 «신규분»에만 건다(registry_gate 동형 — 기존분은 이미 비-blocker).
        rest: "list[str]" = []
        for line in new:
            hit: bool = any(f"[{tag}]" in line and sub in line for tag, sub in debt_rules)
            (debt if hit else rest).append(line)
        new = rest

    print(f"{label} 앵커 차분(--anchor {sha[:12]} · 기준선={used}):")
    print(f"  신규분(앵커 이후) {len(new)}건 · 앵커 기존분(잔존) {len(existing)}건 · 이관 빚 {len(debt)}건")
    if new:
        print("  == 신규분 — 차분에 종속되지 않는 직접 blocker ==")
        for line in new:
            print(f"  {line.strip()}")
    if debt:
        print("  == 이관 빚(사용자 승인 목록 매칭 — exit 제외·기록 의무) ==")
        for line in debt:
            print(f"  {line.strip()}")
    if existing:
        print("  == 앵커 기존분 — blocker 아님·보고 의무(침묵 금지)·이 빌드에서 즉석 수리하지 않는다 ==")
        for line in existing:
            print(f"  {line.strip()}")
    if new:
        print(f"판정: 신규분 {len(new)}건 → blocker(exit 2) — 기존분 {len(existing)}건은 별도 보고")
        return 2
    print(
        f"판정: 신규분 0건 → exit 0 (신규 0 ≠ 전체 clean — 앵커 기존분 {len(existing)}건과 "
        f"빚 {len(debt)}건은 위 보고 채널로만 남긴다)"
    )
    return 0
