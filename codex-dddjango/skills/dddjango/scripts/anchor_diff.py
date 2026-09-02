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

import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checker_registry import REGISTRY, checker_argv  # noqa: E402

# 앵커 스냅숏 재실행 모드 flag — 다섯 검사기(registry 2·5·6·15·16번)가 공통 수용한다.
BASELINE_FLAG: str = "--anchor-baseline"
# 사용자 승인 «이관 빚» 목록 flag — registry_gate 와 같은 이름·같은 줄 형식
# (`#<규칙> <부분문자열>`)·같은 의미(신규분 exit 에서 빼되 «빚» 절로 반드시 보고)·
# 같은 매칭 코퍼스(정규화 라인 — `debt_match` 하나를 두 도구가 공유한다).
# 검사기(check-*.py) 소스는 이 리터럴을 직접 쓰지 않고 이 상수만 참조한다(checker_lint ㉢
# 는 check-*.py 만 훑는다 — registry_gate 처럼 이 모듈은 그 낱말 규율 밖이다).
DEBT_FLAG: str = "--legacy-debt-file"
# 발주자 승인 «main→레인 머지» 목록 flag — registry_gate 의 provenance 차분 채널(2026-09-03).
# 줄 형식 `<SHA> [메모]`(`//` 주석·빈 줄 허용). 빚 목록과 같은 «사용자 승인 입력» 부류다 —
# 도구는 소유(누가 썼는가)를 검증하지 않고 형식·git 사실(ⓐ resolve · ⓑ 부모 2 · ⓒ 앵커..HEAD
# first-parent 사슬 위 · ⓓ 앵커 이전이면 판정 불참)만 fail-closed 로 검증한다.
APPROVED_MERGE_FLAG: str = "--approved-merge-file"

_LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")


class AnchorDiffUsage(Exception):
    """--anchor 재료 결손·공허 차분 — 호출 검사기의 사용 오류 경로(exit 1)로 보낸다."""


def run_git(root: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    """git 실행 공용 헬퍼 — registry_gate 도 이것을 import 한다(복제 금지)."""
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def is_git_worktree(root: Path) -> bool:
    """`--anchor-baseline` 의 비-git 전용 가드와 앵커 재료 검증이 함께 쓴다."""
    return run_git(root, "rev-parse", "--is-inside-work-tree").returncode == 0


def resolve_anchor(root: Path, anchor: str) -> str:
    """앵커 재료 검증 — 비-git·resolve 불능·공허 차분(앵커=HEAD·clean)은 사용 오류."""
    if not is_git_worktree(root):
        raise AnchorDiffUsage(
            "--anchor 는 git 저장소 TARGET 에서만 쓸 수 있다 — 차분 재료가 없다"
        )
    rev: "subprocess.CompletedProcess[str]" = run_git(root, "rev-parse", "--verify", f"{anchor}^{{commit}}")
    if rev.returncode != 0:
        raise AnchorDiffUsage(f"앵커 {anchor!r} resolve 불능 — {rev.stderr.strip()}")
    sha: str = rev.stdout.strip()
    head: str = run_git(root, "rev-parse", "HEAD").stdout.strip()
    dirty: bool = bool(run_git(root, "status", "--porcelain").stdout.strip())
    if sha == head and not dirty:
        raise AnchorDiffUsage(
            "앵커=HEAD 이고 working tree 가 clean — 차분이 공허하다. 검사는 구현 커밋 "
            "«전»에 돌리거나 런 시작점 앵커를 지정하라(«커밋 뒤 검사» 세탁 차단)"
        )
    return sha


def snapshot_anchor(root: Path, sha: str, dest: Path) -> None:
    """앵커 커밋의 트리를 dest 에 푼다 — registry_gate 도 이것을 import 한다(복제 금지)."""
    dest.mkdir(parents=True)
    archive: "subprocess.Popen[bytes]" = subprocess.Popen(
        ["git", "-C", str(root), "archive", sha],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    untar: "subprocess.CompletedProcess[bytes]" = subprocess.run(
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
    # 기준선 재실행은 «측정 도구의 내부 호출»이라 구조화 레코드 채널을 상속하면 안 된다 —
    # 부모 stdout 에 나오지 않는 앵커 진단이 레코드 파일에만 별도 run_id 로 쌓여
    # «출력 없는 유령 레코드»가 된다(T2-1 적대 검증 레인 P 6번·R 2번 — 기존분-only 에서 정확히 2배).
    env: "dict[str, str]" = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).splitlines()


def load_debt(path: Path) -> "list[tuple[str, str]]":
    """이관 빚 승인 목록 로더 — registry_gate 도 이것을 import 한다(복제 금지).

    줄 형식 `#<규칙번호> <부분문자열>`(빈 줄·`//` 주석 허용). tag 는 `#<숫자>` 만 받는다 —
    숫자 없는 tag(`#`·`##` 류)는 어떤 진단의 `[#N]` 과도 일치할 수 없는 «발화 불능 규칙»
    이라 조용히 수용하지 않고 형식 오류로 거절한다(fail-closed).
    """
    out: "list[tuple[str, str]]" = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line: str = raw.strip()
        if not line or line.startswith("//"):
            continue
        parts: "list[str]" = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"#\d+", parts[0]) is None:
            raise AnchorDiffUsage(
                f"빚 목록 줄 형식 오류: {raw!r} — `#<규칙번호> <부분문자열>`(규칙번호는 숫자)"
            )
        out.append((parts[0], parts[1]))
    return out


@dataclass(frozen=True)
class ChainCommit:
    """HEAD first-parent 사슬의 한 커밋 — 부모 순서(첫째=레인 측·둘째=incoming)와 subject."""

    sha: str
    parents: "tuple[str, ...]"
    subject: str

    @property
    def is_merge(self) -> bool:
        return len(self.parents) == 2


@dataclass(frozen=True)
class ApprovedMerge:
    """승인 목록의 한 줄 — 검증 통과분. position 은 사슬 안 1-based 서수(앵커 다음 = 1 · 오래된 순)이고
    None 이면 ⓓ «앵커 이전 — 판정 불참»(epoch 을 넘긴 목록 허용 — 목록 자체는 유효하되 이 런의 판정에 안 쓴다)."""

    sha: str
    parent1: str
    parent2: str
    subject: str
    position: "int | None"
    memo: str
    parent2_ref: str  # `git name-rev --refs='refs/*'` — ^2 의 ref 도달성(역방향 머지 오기입 가시화 재료)
    # `git for-each-ref --contains ^2` 가 HEAD 브랜치 ref 뿐(또는 0)이면 참 — incoming 측이 상류(main) 이력에 없다는
    # 뜻이라 역방향/합성 머지 의심 진단(exit 무변 · 발주자 확인)의 재료다. HEAD=lane 역방향은 사슬 검증이 exit 1 로
    # 잡지만, 발주자가 합성 머지를 레인 사슬에 올린 잔여 경로는 이 신호로만 표면화된다.
    parent2_only_head: bool = False

    @property
    def participates(self) -> bool:
        return self.position is not None


def first_parent_chain(root: Path, anchor_sha: str, head_sha: str) -> "list[ChainCommit] | None":
    """HEAD 의 first-parent 사슬에서 앵커(제외)..HEAD(포함) 구간을 **오래된 순**으로 돌려준다.

    앵커가 그 사슬 위에 없으면 None — «조상이지만 ^2 경유»(레인 시작점이 다른 가지에서 머지돼
    들어온 경우)·«조상 아님» 둘 다 None 이다. 이 구간의 2-부모 커밋만이 «레인이 받은 머지»이고,
    승인 목록의 SHA 는 이 구간 안에 있어야 한다(역방향 머지 — 레인을 main 으로 합친 커밋 — 는
    이 사슬에 없으므로 형식 오류로 잡힌다).
    """
    log: "subprocess.CompletedProcess[str]" = run_git(
        root, "log", "--first-parent", "--format=%H%x1f%P%x1f%s", head_sha)
    if log.returncode != 0:
        return None
    out: "list[ChainCommit]" = []
    for raw in log.stdout.splitlines():
        sha, _, rest = raw.partition("\x1f")
        parents, _, subject = rest.partition("\x1f")
        if sha == anchor_sha:
            return list(reversed(out))
        out.append(ChainCommit(sha, tuple(parents.split()), subject))
    return None


def load_approved_merges(path: Path, root: Path, anchor_sha: str,
                         head_sha: str) -> "tuple[list[ApprovedMerge], list[ChainCommit]]":
    """승인 머지 목록 로더 — registry_gate 가 import 한다(빚 로더와 같은 자리·같은 fail-closed).

    줄 형식 `<SHA> [메모]`(빈 줄·`//` 주석 허용 — `load_debt` 동형). 검증(전부 AnchorDiffUsage → 호출측 exit 1):
      ⓐ `rev-parse --verify <sha>^{commit}` 성공  ⓑ 부모 정확히 2(비머지·옥토퍼스 거절)
      ⓒ 앵커가 HEAD first-parent 사슬 위(도달 필수 — 아니면 목록이 비어 있어도 판정 불가)
         ∧ 머지가 앵커..HEAD 구간 안(역방향 합성·타 가지 머지 거절)
      ⓓ 예외: `merge-base --is-ancestor M anchor` 참(앵커 이전 머지)이면 거절하지 않고 «판정 불참»으로 표시
    진단 재료(exit 무변): `parent2_ref`(name-rev) · `parent2_only_head`(`for-each-ref --contains ^2` 가 HEAD 브랜치
    ref 뿐 — 역방향/합성 머지 의심 · 발주자는 등재 전 `^2` 가 main(상류) 이력에 있는지 확인한다).
    반환 = (목록, 사슬). 중복 SHA 는 첫 줄만 남긴다.
    """
    chain: "list[ChainCommit] | None" = first_parent_chain(root, anchor_sha, head_sha)
    if chain is None:
        raise AnchorDiffUsage(
            f"앵커 {anchor_sha[:12]} 가 HEAD first-parent 사슬 밖 — 승인 목록 판정 불가"
            "(앵커가 조상이어도 ^2 경유면 사슬 밖이다 · 레인 시작점 앵커를 확인하라)"
        )
    position_of: "dict[str, int]" = {c.sha: i + 1 for i, c in enumerate(chain)}
    by_sha: "dict[str, ChainCommit]" = {c.sha: c for c in chain}
    head_ref: str = run_git(root, "symbolic-ref", "-q", "HEAD").stdout.strip()  # detached 면 ""
    out: "list[ApprovedMerge]" = []
    seen: "set[str]" = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line: str = raw.strip()
        if not line or line.startswith("//"):
            continue
        token, _, memo = line.partition(" ")
        if re.fullmatch(r"[0-9a-fA-F]{7,40}", token) is None:
            raise AnchorDiffUsage(
                f"승인 머지 목록 줄 형식 오류: {raw!r} — `<SHA> [메모]`(SHA 는 7~40 hex)"
            )
        rev: "subprocess.CompletedProcess[str]" = run_git(root, "rev-parse", "--verify", f"{token}^{{commit}}")
        if rev.returncode != 0:
            raise AnchorDiffUsage(f"승인 머지 {token!r} resolve 불능 — {rev.stderr.strip()}")
        sha: str = rev.stdout.strip()
        if sha in seen:
            continue
        seen.add(sha)
        show: "subprocess.CompletedProcess[str]" = run_git(root, "show", "-s", "--format=%P%x1f%s", sha)
        parents_raw, _, subject = show.stdout.rstrip("\n").partition("\x1f")
        parents: "list[str]" = parents_raw.split()
        if len(parents) != 2:
            raise AnchorDiffUsage(
                f"승인 머지 {sha[:12]} 의 부모가 {len(parents)}개 — 승인 목록은 2-부모 머지만 받는다"
                "(비머지 커밋·squash·rebase 결과·옥토퍼스는 등재 대상이 아니다)"
            )
        name_rev: "subprocess.CompletedProcess[str]" = run_git(
            root, "name-rev", "--refs=refs/*", "--name-only", parents[1])
        parent2_ref: str = name_rev.stdout.strip() or "undefined"
        containing: "set[str]" = set(
            run_git(root, "for-each-ref", "--contains", parents[1], "--format=%(refname)").stdout.split())
        only_head: bool = not (containing - {head_ref})
        if run_git(root, "merge-base", "--is-ancestor", sha, anchor_sha).returncode == 0:
            out.append(ApprovedMerge(sha, parents[0], parents[1], subject, None, memo.strip(), parent2_ref, only_head))
            continue  # ⓓ 앵커 이전 — 판정 불참(목록은 유효)
        if sha not in by_sha:
            raise AnchorDiffUsage(
                f"승인 머지 {sha[:12]} 가 앵커 {anchor_sha[:12]}..HEAD first-parent 사슬 밖 — "
                "레인이 받은 머지가 아니다(역방향 머지·타 가지 머지는 등재 대상이 아니다)"
            )
        out.append(ApprovedMerge(sha, parents[0], parents[1], subject, position_of[sha], memo.strip(), parent2_ref,
                                 only_head))
    return out, chain


def debt_match(normalized_line: str, debt_rules: "list[tuple[str, str]]") -> bool:
    """빚 매칭 술어 — 두 도구(직접 계열·registry_gate)가 같은 코퍼스로 판정한다.

    코퍼스는 «정규화 라인»(절대 경로 echo 제거·라인번호 `:N` 치환)이다 — 같은 빚 파일이
    도구에 따라 다르게 읽히지 않는다. 레인 실물 형식(`#12 application.pairing` 류
    dotted-module 부분문자열)은 정규화가 건드리지 않으므로 그대로 매칭된다(하위 호환).
    """
    return any(f"[{tag}]" in normalized_line and sub in normalized_line for tag, sub in debt_rules)


def validate_materials(target: Path, anchor: str, debt_file: "str | None") -> None:
    """`--anchor` 재료 선검증 — findings 유무와 무관하게 parse 직후 호출한다.

    무발견 clean 실행에서도 resolve 불능 앵커·부재/형식 오류 빚 파일·공허 차분
    (앵커=HEAD·clean)이 침묵 exit 0 으로 새지 않게 AnchorDiffUsage(호출측 사용 오류
    exit 1)로 보낸다(fail-closed). partition_exit 의 재검증과 중복이지만 그쪽은
    findings 가 있을 때만 도달한다."""
    resolve_anchor(target.resolve(), anchor)
    if debt_file is not None:
        debt_path: Path = Path(debt_file)
        if not debt_path.is_file():
            raise AnchorDiffUsage(f"빚 목록 {debt_path} 없음")
        load_debt(debt_path)


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
    analysis_pending: bool = False,
) -> int:
    """현재 findings 를 앵커 기준선과 대조해 차분 절을 출력하고 exit 를 정한다.

    반환 2 = 신규분 존재(현행대로 blocker) · 0 = 전건 앵커 기존분(강등 + 보고).
    debt_file(사용자 승인 목록)에 맞는 신규분은 exit 에서 빼되 «빚» 절로 보고한다
    (registry_gate 와 동일 — 빚은 기록 근거이지 모양 복사 근거가 아니다). 빚 매칭은
    분류와 같은 «정규화 라인» 코퍼스에 건다(debt_match — registry_gate 동일 판정).
    재료 결손·공허 차분은 AnchorDiffUsage — 호출측 사용 오류 경로(exit 1)가 받는다.
    호출측은 findings 를 이미 전량 출력한 «뒤» 이 함수를 부른다(정보 손실 0).
    analysis_pending=True 는 호출측에 강등으로 소거되지 않는 잔여 분석/토큰 진단이
    남아 있다는 표식이다 — 판정 문구만 그 사실에 맞춘다(exit 계산 무변).
    """
    debt_rules: "list[tuple[str, str]]" = []
    if debt_file is not None:
        debt_path: Path = Path(debt_file)
        if not debt_path.is_file():
            raise AnchorDiffUsage(f"빚 목록 {debt_path} 없음")
        debt_rules = load_debt(debt_path)
    resolved_target: Path = target.resolve()
    sha: str = resolve_anchor(resolved_target, anchor)
    with tempfile.TemporaryDirectory() as td:
        snap: Path = Path(td) / "anchor"
        snapshot_anchor(resolved_target, sha, snap)
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
            # 분류와 같은 정규화 라인에 매칭 — registry_gate 와 같은 빚 파일을 같은 판정으로 읽는다.
            hit: bool = debt_match(_normalize(line, roots), debt_rules)
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
    if analysis_pending:
        # 잔여 분석/토큰 진단이 남은 호출측 — «exit 0» 을 단정하면 실제 exit(proof 경로
        # exit 1)와 어긋난다. 차분 몫의 판정만 말한다(동작 무변·문구 조건화).
        print(
            f"판정: 신규분 0건 → 차분 계열 강등 — 잔여 분석/토큰 진단의 exit 가 우선한다"
            f"(앵커 기존분 {len(existing)}건과 빚 {len(debt)}건은 위 보고 채널로만 남긴다)"
        )
        return 0
    print(
        f"판정: 신규분 0건 → exit 0 (신규 0 ≠ 전체 clean — 앵커 기존분 {len(existing)}건과 "
        f"빚 {len(debt)}건은 위 보고 채널로만 남긴다)"
    )
    return 0
