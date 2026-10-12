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
- 앵커 재실행은 `--anchor-baseline` 모드다: 앵커에 없는 경로 selector 와
  BC 뿌리의 부재가 확인된 `--scope-bc`·`--error-bc` 이름 selector 를 argv 에서
  걷는다. 검사기는 이 모드에서 path-repeat selector 의 필수 개수를 완화하고
  빈 scope BC 집합을 허용하되 분석은 계속한다. 앵커에 없는 정규화 진단문은
  신규로 남는다. 이 모드는 비-git 스냅숏 전용이다(git 저장소 TARGET 에선 사용
  오류 — 실전 렌더 계약 완화로의 오용 차단).
- 앵커 재실행이 사용/분석 오류(exit 1)면 빈 골격 --error-bc 를 걷고 그 영역 아래 줄을 제외하여
  재실행한다. 그래도 서지 않으면 로스터 positional 기준선(`checker_registry.
  checker_argv` — registry_gate 가 내부 실행하는 그 호출)으로 한 번 강등하고,
  그마저 오류면 fail-closed(전량 신규 취급 = blocker 유지)한다. 기준선 오류는 별도 줄로 보고한다.
- 승인 머지 목록이 있으면 주어 판정·두 부모 차분·병합 결과부터 HEAD까지 줄 이어짐을
  증명한 줄만 승인 유입으로 분리한다. 증명 불능은 신규에 남기고 사유를 보고한다.
- 라인 대조는 registry_gate 와 같은 정규화만 한다: 절대 경로 echo 제거·라인번호
  `:N` 치환 — 경로 «파싱»을 하지 않는다.
"""
from __future__ import annotations

import os
import ast
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checker_registry import REGISTRY, checker_argv  # noqa: E402
import checker_target  # noqa: E402  — 빈 골격 술어(skeleton_placeholder) 단일 출처

# 앵커 스냅숏 재실행 모드 flag — 다섯 검사기(registry 2·5·6·15·16번)가 공통 수용한다.
BASELINE_FLAG: str = "--anchor-baseline"
# 사용자 승인 «이관 빚» 목록 flag — registry_gate 와 같은 이름·같은 줄 형식
# (`#<규칙> <부분문자열>` · 번호 없는 줄은 `= <검사기 파일> :: <줄>`)·같은 의미(신규분 exit 에서
# 빼되 «빚» 절로 반드시 보고)·같은 매칭 코퍼스(정규화 라인 — `debt_match` 하나를 두 도구가 공유한다).
# 검사기(check-*.py) 소스는 이 리터럴을 직접 쓰지 않고 이 상수만 참조한다(checker_lint ㉢
# 는 check-*.py 만 훑는다 — registry_gate 처럼 이 모듈은 그 낱말 규율 밖이다).
DEBT_FLAG: str = "--legacy-debt-file"
# 발주자 승인 «main→레인 머지» 목록 flag — registry_gate 의 provenance 차분 채널(2026-09-03).
# 줄 형식 `<SHA> [메모]`(`//` 주석·빈 줄 허용). 빚 목록과 같은 «사용자 승인 입력» 부류다 —
# 도구는 소유(누가 썼는가)를 검증하지 않고 형식·git 사실(ⓐ resolve · ⓑ 부모 2 · ⓒ 앵커..HEAD
# first-parent 사슬 위 · ⓓ 앵커 이전이면 판정 불참)만 fail-closed 로 검증한다.
APPROVED_MERGE_FLAG: str = "--approved-merge-file"

# pre-gate 사본에서도 원 TARGET의 소유 조건을 쓰기 위한 내부 전달 채널.
SISTER_SOURCE_ENV: str = "DJR_SISTER_SOURCE_ROOT"
SISTER_TITLE: str = "자매 플러그인 영역(dddjango-web 소유 — 서버 판정 밖 · 보고만)"
_SISTER_ROOTS: "tuple[str, ...]" = ("web", "web_test", ".dddjango-web")


def sister_owned(target: Path) -> bool:
    """원 TARGET의 명확한 채택·프로젝트 실경로만으로 한 번 판정한다."""
    try:
        root: Path = target.resolve(strict=True)
        marker: Path = root / ".dddjango-web"
        if marker.is_symlink() or not marker.is_dir():
            return False
        siblings: "list[Path]" = []
        for name in _SISTER_ROOTS:
            path: Path = root / name
            if path.is_symlink():
                return False
            if path.exists():
                if not path.is_dir():
                    return False
                siblings.append(path)
        module: ast.Module = ast.parse((root / "manage.py").read_text(encoding="utf-8"))
        def is_environ(node: ast.AST) -> bool:
            return (isinstance(node, ast.Attribute) and node.attr == "environ"
                    and isinstance(node.value, ast.Name) and node.value.id == "os")

        mentions: "list[ast.AST]" = [node for node in ast.walk(module)
            if (isinstance(node, ast.Constant) and node.value == "DJANGO_SETTINGS_MODULE")
            or (isinstance(node, ast.Name) and node.id == "DJANGO_SETTINGS_MODULE")
            or (isinstance(node, ast.Attribute) and node.attr == "DJANGO_SETTINGS_MODULE")
            or (isinstance(node, ast.keyword) and node.arg == "DJANGO_SETTINGS_MODULE")]
        if len(mentions) != 1:
            return False
        values: "list[ast.expr]" = []
        for node in ast.walk(module):
            # 동적 키·mapping은 settings를 덮는지 알 수 없다. 단일 리터럴과 함께 있어도 거절한다.
            if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store) \
                    and is_environ(node.value) and not (isinstance(node.slice, ast.Constant)
                    and isinstance(node.slice.value, str)):
                return False
            if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store) and is_environ(node):
                return False
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and is_environ(node.func.value):
                if node.func.attr == "update" and (any(kw.arg is None for kw in node.keywords)
                        or any(not isinstance(arg, ast.Dict) or any(
                            not isinstance(key, ast.Constant) or not isinstance(key.value, str)
                            for key in arg.keys) for arg in node.args)):
                    return False
                if node.func.attr in ("setdefault", "__setitem__") and (not node.args
                        or not isinstance(node.args[0], ast.Constant)
                        or not isinstance(node.args[0].value, str)):
                    return False
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "os" \
                    and node.func.attr == "putenv" and (not node.args
                    or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str)):
                return False
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and is_environ(node.func.value) \
                    and node.func.attr == "setdefault" and len(node.args) == 2 \
                    and node.args[0] is mentions[0] and not node.keywords:
                values.append(node.args[1])
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets: "list[ast.expr]" = node.targets if isinstance(node, ast.Assign) else [node.target]
                if node.value is not None and len(targets) == 1 \
                        and isinstance(targets[0], ast.Subscript) and is_environ(targets[0].value) \
                        and targets[0].slice is mentions[0]:
                    values.append(node.value)
        if len(values) != 1 or not isinstance(values[0], ast.Constant) \
                or not isinstance(values[0].value, str):
            return False
        settings: str = values[0].value
        if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+", settings):
            return False
        project: Path = (root / settings.split(".", 1)[0]).resolve(strict=True)
        if not project.is_dir():
            return False
        # samefile은 대소문자 무구별 파일시스템의 별칭도 해소한다.
        return not any(os.path.samefile(parent, sister)
                       for parent in (project, *project.parents) for sister in siblings)
    except (OSError, ValueError, SyntaxError, UnicodeError, RuntimeError):
        return False


def sister_path(path: "str | None") -> bool:
    """주어의 저장소 상대 첫 성분만 본다. 부재 locator도 허용하며 모호한 꼴은 남긴다."""
    if path is None:
        return False
    plain: str = re.sub(r"(?::(?:\d+|N))+$", "", path)
    if not plain or re.search(r"[\s,;|<>\\\[\]:]", plain) or plain.startswith("/"):
        return False
    parts: "list[str]" = plain.split("/")
    if ".." in parts or "" in parts:
        return False
    if parts[0] == ".":
        parts = parts[1:]
    return bool(parts) and parts[0] in _SISTER_ROOTS


def subject_path(line: str) -> "str | None":
    """정상 숫자 진단·계약 행의 주어 칸만 읽는다. 메시지 안 경로는 읽지 않는다."""
    match: "re.Match[str] | None" = re.fullmatch(r"(?:\[#\d+\]|-) (.+?): (.*)", line.strip())
    return match.group(1) if match is not None else None


def measurement_failed(lines: "list[str] | set[str]") -> bool:
    return any("[진단 미파싱" in line or "[분석]" in line for line in lines)

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


def _bc_root_absent(snapshot: Path, name: str) -> bool:
    """실제 application 디렉터리 아래에서 lstat로 확인된 BC 부재만 참이다."""
    application: Path = snapshot / "application"
    try:
        parent: os.stat_result = os.lstat(application)
    except OSError:
        return False
    if not stat.S_ISDIR(parent.st_mode):
        return False  # lstat이므로 링크도 실제 디렉터리가 아니다.
    try:
        os.lstat(application / name)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False  # 빈 폴더·동명 파일·정상/끊어진/순환 링크 모두 유지한다.


def _baseline_argv(
    script: Path, snapshot: Path, argv: "list[str]", path_flags: "frozenset[str]",
    *, drop_error_bcs: "frozenset[str]" = frozenset(),
) -> "list[str]":
    """앵커 재실행 argv — 원 argv 에서 --anchor 를 걷고 target 을 스냅숏으로 바꾼다.

    앵커에 없는 경로 selector와 BC 뿌리의 부재가 확인된 이름 selector를 걷는다.
    BC 이름은 그대로 application/<이름>에 대입하며, 실제 application 디렉터리
    아래 자식의 lstat가 FileNotFoundError일 때만 부재다. 같은 판정을 두 이름
    플래그의 각 출현에 적용하고 중복은 보존한다. 검사기는 baseline에서 빈 scope
    BC 집합을 받아 분석을 계속한다. 앵커에 없는 정규화 진단문은 신규로 남는다.
    전제: 다섯 검사기의 모든 `--flag` 는 값 1개를 받는다(store_true 없음 — 이
    모듈이 주입하는 BASELINE_FLAG 만 예외이고 그것은 원 argv 에 오지 않는다).
    """
    out: "list[str]" = [sys.executable, str(script), str(snapshot)]
    absent_bcs: "dict[str, bool]" = {}
    i: int = 0
    while i < len(argv):
        token: str = argv[i]
        if token in ("--anchor", DEBT_FLAG, APPROVED_MERGE_FLAG):
            i += 2
            continue
        if token.startswith(("--anchor=", DEBT_FLAG + "=", APPROVED_MERGE_FLAG + "=")) or token == BASELINE_FLAG:
            i += 1
            continue
        if token.startswith("--"):
            name, eq, inline = token.partition("=")
            value: "str | None" = inline if eq else (argv[i + 1] if i + 1 < len(argv) else None)
            step: int = 1 if eq or value is None else 2
            if name in path_flags and value is not None and not (snapshot / value).exists():
                i += step
                continue
            if name == "--error-bc" and value in drop_error_bcs:
                i += step  # (나) 빈 골격 오류 영역 — 호출측이 고른 것만 걷는다
                continue
            if name in ("--scope-bc", "--error-bc") and value is not None:
                if value not in absent_bcs:
                    absent_bcs[value] = _bc_root_absent(snapshot, value)
                if absent_bcs[value]:
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


_ERROR_MODULE: str = "application/{bc}/driving_layer/api/bc_error_schema.py"
_SUBJECT_LINENO_RE: "re.Pattern[str]" = re.compile(r"(?::(?:\d+|N))+$")


def _skeleton_error_bcs(snapshot: Path, argv: "list[str]") -> "list[str]":
    """argv 의 `--error-bc` 값 가운데 스냅숏에서 오류 모듈이 «빈 골격»인 BC(출현 순 · 중복 제거)."""
    out: "list[str]" = []
    i: int = 0
    while i < len(argv):
        token: str = argv[i]
        value: "str | None" = None
        if token == "--error-bc" and i + 1 < len(argv):
            value = argv[i + 1]
            i += 1
        elif token.startswith("--error-bc="):
            value = token.partition("=")[2]
        i += 1
        if value and value not in out and re.fullmatch(r"[a-z][a-z0-9_]*", value) \
                and checker_target.skeleton_placeholder(snapshot / _ERROR_MODULE.format(bc=value)):
            out.append(value)
    return out


def _subject_file(normalized_line: str) -> "str | None":
    """정규화 진단 줄의 주어 경로(끝 `:N` 제거 · 깨끗한 상대 경로만). 아니면 None."""
    subject: "str | None" = subject_path(normalized_line)
    if subject is None:
        return None
    plain: str = _SUBJECT_LINENO_RE.sub("", subject)
    if plain.startswith("./"):
        plain = plain[2:]
    parts: "list[str]" = plain.split("/")
    if not plain or plain.startswith("/") or "" in parts or "." in parts or ".." in parts \
            or re.search(r"[\s,;|<>\\\[\]:]", plain):
        return None
    return plain


@dataclass
class _Baseline:
    code: int                 # 기준선으로 쓴 실행의 exit(불능이면 마지막 실패 exit)
    lines: "list[str]"
    used: str
    error: "str | None" = None          # selector 렌더가 서지 않았을 때 그 실행의 마지막 줄
    dropped: "tuple[str, ...]" = ()     # (나) 로 --error-bc 를 걷은 BC


def _baseline_lines(script: Path, snap: Path, argv: "list[str]", path_flags: "frozenset[str]") -> _Baseline:
    """한 스냅숏의 기준선 사다리 — ① selector 렌더 ② (서지 않을 때만) 빈 골격 --error-bc 를 걷은 selector 렌더
    ∪ positional ③ positional ④ 불능. ①이 서면 2.21.1 과 같은 실행·같은 문구다."""
    code: int
    lines: "list[str]"
    code, lines = _run_lines(_baseline_argv(script, snap, argv, path_flags))
    if code in (0, 2):
        return _Baseline(code, lines, "selector 렌더 재실행")
    error: "str | None" = next((l.strip() for l in reversed(lines) if l.strip()), None)
    auto: bool = dict(REGISTRY).get(script.name, False)
    pcode: int
    plines: "list[str]"
    pcode, plines = _run_lines(checker_argv(sys.executable, script.name, str(snap), auto))
    skeleton: "list[str]" = _skeleton_error_bcs(snap, argv)
    if skeleton:
        acode: int
        alines: "list[str]"
        acode, alines = _run_lines(_baseline_argv(script, snap, argv, path_flags,
                                                  drop_error_bcs=frozenset(skeleton)))
        if acode in (0, 2):
            roots: "tuple[str, ...]" = (str(snap) + "/", str(snap))
            kept: "list[str]" = []
            for line in alines:
                subject: "str | None" = _subject_file(_normalize(line, roots))
                if subject is None:
                    continue  # 주어를 못 읽는 줄은 조정 기준선에 싣지 않는다(fail-closed)
                if any(subject == f"application/{bc}" or subject.startswith(f"application/{bc}/")
                       for bc in skeleton):
                    continue  # 걷은 영역 아래 줄 — 걷어서 생긴 줄일 수 있다(오퍼레이션→helper 재분류)
                kept.append(line)
            names: str = ", ".join(skeleton)
            if pcode in (0, 2):
                return _Baseline(acode, plines + kept,
                                 f"selector 렌더 재실행(빈 골격 --error-bc 걷음: {names} · 그 영역 아래 줄 제외) + positional 기준선",
                                 None, tuple(skeleton))
            return _Baseline(acode, kept,
                             f"selector 렌더 재실행(빈 골격 --error-bc 걷음: {names} · 그 영역 아래 줄 제외)",
                             None, tuple(skeleton))
    if pcode in (0, 2):
        return _Baseline(pcode, plines,
                         "positional 기준선(selector 렌더 불능 강등 — selector-lane 진단은 전량 신규 취급)", error)
    return _Baseline(pcode, [], "기준선 불능(fail-closed — 전량 신규 취급)", error)


def tree_blobs(root: Path, sha: str) -> "dict[str, str]":
    """커밋 트리의 경로→blob SHA(`git ls-tree -r -z` 1회) — 폴더·서브모듈은 들어가지 않는다."""
    proc: "subprocess.CompletedProcess[str]" = run_git(root, "ls-tree", "-r", "-z", sha)
    out: "dict[str, str]" = {}
    if proc.returncode != 0:
        return out
    for entry in proc.stdout.split("\0"):
        if not entry:
            continue
        meta: str
        separator: str
        path: str
        meta, separator, path = entry.partition("\t")
        parts: "list[str]" = meta.split()
        if len(parts) == 3 and parts[1] == "blob" and parts[0] != "120000":
            out[path] = parts[2]  # 일반 파일만 — 심링크(120000)는 주어로 받지 않는다(내용이 다른 경로에 있다)
    return out


def snapshot_escape(dest: Path) -> "str | None":
    """스냅숏 사본 안의 심링크 가운데 실경로가 사본 «밖» 인 첫 항목(사본 상대 경로). 없으면 None.

    그런 심링크가 있는 사본에서 돌린 검사는 사본 밖(예: 레인의 작업 트리)을 읽을 수 있다 —
    그 실행은 «레인 내용이 한 글자도 없다» 를 보장하지 못하므로 감산 증거로 쓰지 않는다."""
    base: str = os.path.realpath(dest)
    for current, dirs, files in os.walk(dest):
        for name in sorted(dirs + files):
            path: str = os.path.join(current, name)
            if os.path.islink(path):
                real: str = os.path.realpath(path)
                if real != base and not real.startswith(base + os.sep):
                    return os.path.relpath(path, dest)
    return None


def _run_lines(cmd: "list[str]") -> "tuple[int, list[str]]":
    # 기준선 재실행은 «측정 도구의 내부 호출»이라 구조화 레코드 채널을 상속하면 안 된다 —
    # 부모 stdout 에 나오지 않는 앵커 진단이 레코드 파일에만 별도 run_id 로 쌓여
    # «출력 없는 유령 레코드»가 된다(T2-1 적대 검증 레인 P 6번·R 2번 — 기존분-only 에서 정확히 2배).
    env: "dict[str, str]" = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).splitlines()


# 번호 없는 빚 줄(`= <검사기 파일> :: - <주어>: <메시지>`)이 맞을 수 있는 검사기 — `partition_exit` 를
# 부르는 scope 렌더 다섯(registry #2·#5·#6·#15·#16)뿐이다. registry_gate 의 차분 집합은 `[#N]` 줄뿐이라
# 번호 없는 줄이 거기 들어가지 않는다 — 다른 이름은 어떤 줄과도 맞을 수 없어 형식 오류로 거절한다.
_DEBT_LINE_CHECKERS: "frozenset[str]" = frozenset({
    "check-error-centralization.py", "check-openapi-error-declaration.py", "check-context-isolation.py",
    "check-api-error-controller-contract.py", "check-composition-root.py",
})
_DEBT_LINE_RE: "re.Pattern[str]" = re.compile(r"=\s+(\S+) :: (- (?!/)\S.*?: .+)")


def load_debt(path: Path) -> "list[tuple[str, str]]":
    """이관 빚 승인 목록 로더 — registry_gate 도 이것을 import 한다(복제 금지).

    줄 형식 둘(빈 줄·`//` 주석 허용):
      `#<규칙번호> <부분문자열>` — 번호 있는 줄(`[#N]`)에 부분 일치. tag 는 `#<숫자>` 만 받는다 —
        숫자 없는 tag(`#`·`##` 류)는 어떤 진단의 `[#N]` 과도 일치할 수 없는 «발화 불능 규칙»
        이라 조용히 수용하지 않고 형식 오류로 거절한다(fail-closed).
      `= <검사기 파일> :: - <주어>: <메시지>` — 번호 없는 줄 하나와 **줄 전체 일치**. 줄은 검사기가
        찍은 그대로 옮겨도 되고(`:<숫자>` 는 읽을 때 `:N` 으로 바꾼다 — 대조 코퍼스와 같은 치환)
        검사기는 scope 렌더 다섯 가운데 하나이며, 주어가 / 로 시작하는 꼴 등은 형식 오류로 거절한다.
        반환 원소는 `("=", "<검사기 파일> :: <정규화 줄>")` — registry_gate 귀속 줄과 같은 모양이다.
    """
    out: "list[tuple[str, str]]" = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line: str = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line.startswith("="):
            match: "re.Match[str] | None" = _DEBT_LINE_RE.fullmatch(line)
            if match is None:
                raise AnchorDiffUsage(
                    f"빚 목록 줄 형식 오류: {raw!r} — 번호 없는 줄은 "
                    "`= <검사기 파일> :: - <주어>: <메시지>`(검사기가 찍은 줄 전체 · 주어는 상대 경로)"
                )
            if match.group(1) not in _DEBT_LINE_CHECKERS:
                raise AnchorDiffUsage(
                    f"빚 목록 줄 형식 오류: {raw!r} — 번호 없는 줄의 검사기는 "
                    f"{' · '.join(sorted(_DEBT_LINE_CHECKERS))} 가운데 하나"
                )
            out.append(("=", f"{match.group(1)} :: {_LINENO_RE.sub(':N', match.group(2))}"))
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
    # `git for-each-ref --contains ^2` 가 HEAD 브랜치 자신(heads ref·`refs/remotes/*/<브랜치명>`·태그)뿐(또는 0)이면 참 —
    # incoming 측이 상류(main) 이력에 없다는 뜻이라 역방향/합성 머지 의심 진단(exit 무변 · 발주자 확인)의 재료다. HEAD=lane 역방향은 사슬 검증이 exit 1 로
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


def _counts_as_other_ref(ref: str, head_ref: str, head_branch: str) -> bool:
    """`^2` 를 포함하는 ref 중 «HEAD 브랜치 자신»으로 세지 않을 것만 참 — HEAD 브랜치 ref·그 remote-tracking
    (`refs/remotes/*/<HEAD 브랜치명>`)·태그(`refs/tags/*` — 레인 위 태그는 레인 자신)는 제외한다. 푸시된 실전 레인에서
    `origin/<lane>` 이 늘 `^2` 를 포함해 진단이 침묵하던 사각의 수리(6단계 재검 MAJOR-2)."""
    if ref == head_ref or ref.startswith("refs/tags/"):
        return False
    if head_branch and ref.startswith("refs/remotes/"):
        remote_rest: str = ref[len("refs/remotes/"):]  # `<remote>/<branch>` — remote 이름은 첫 세그먼트
        if remote_rest.partition("/")[2] == head_branch:
            return False
    return True


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
    head_branch: str = head_ref.removeprefix("refs/heads/") if head_ref.startswith("refs/heads/") else ""
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
        only_head: bool = not {r for r in containing if _counts_as_other_ref(r, head_ref, head_branch)}
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


def split_approved_merge(argv: "list[str]") -> "tuple[list[str], str | None, str | None]":
    """검사기 다섯의 `--approved-merge-file` 을 argparse «앞에서» 걷는다 → (나머지 argv, 값, 사용 오류 글).

    argparse 에 등록하지 않는 까닭: 줄임 옵션(`--ap` = `--api-module`)의 뜻이 바뀌지 않게 — 플래그 없는 실행의
    argv 해석이 2.21.1 과 같다. 받는 꼴은 정확한 두 꼴(`--approved-merge-file <v>` · `--approved-merge-file=<v>`)뿐이다."""
    rest: "list[str]" = []
    values: "list[str]" = []
    error: "str | None" = None
    i: int = 0
    while i < len(argv):
        token: str = argv[i]
        if token == APPROVED_MERGE_FLAG:
            if i + 1 >= len(argv):
                error = f"{APPROVED_MERGE_FLAG} 에 값이 없다"
                i += 1
                continue
            values.append(argv[i + 1])
            i += 2
            continue
        if token.startswith(APPROVED_MERGE_FLAG + "="):
            values.append(token.partition("=")[2])
            i += 1
            continue
        rest.append(token)
        i += 1
    if len(values) > 1:
        error = f"{APPROVED_MERGE_FLAG} 는 한 번만 준다"
    if values and not values[0]:
        error = f"{APPROVED_MERGE_FLAG} 에 값이 없다"
    return rest, (values[0] if values else None), error



def merge_hints(root: Path, anchor_sha: str, head_sha: str) -> "list[tuple[str, str, bool]]":
    """앵커..HEAD first-parent 사슬의 2-부모 머지 → (sha, ^2 의 name-rev, ^2 를 담은 ref 가 HEAD 브랜치뿐인가).

    registry_gate 의 U2 안내 줄 재료(판정 무접촉). 사슬 밖 앵커면 빈 목록."""
    chain: "list[ChainCommit] | None" = first_parent_chain(root, anchor_sha, head_sha)
    if chain is None:
        return []
    head_ref: str = run_git(root, "symbolic-ref", "-q", "HEAD").stdout.strip()
    head_branch: str = head_ref.removeprefix("refs/heads/") if head_ref.startswith("refs/heads/") else ""
    out: "list[tuple[str, str, bool]]" = []
    for c in chain:
        if not c.is_merge:
            continue
        ref: str = run_git(root, "name-rev", "--refs=refs/*", "--name-only", c.parents[1]).stdout.strip() or "undefined"
        containing: "set[str]" = set(
            run_git(root, "for-each-ref", "--contains", c.parents[1], "--format=%(refname)").stdout.split())
        only_head: bool = not {r for r in containing if _counts_as_other_ref(r, head_ref, head_branch)}
        out.append((c.sha, ref, only_head))
    return out


def debt_match(normalized_line: str, debt_rules: "list[tuple[str, str]]", *,
               checker: "str | None" = None) -> bool:
    """빚 매칭 술어 — 두 도구(직접 계열·registry_gate)가 같은 코퍼스로 판정한다.

    코퍼스는 «정규화 라인»(절대 경로 echo 제거·라인번호 `:N` 치환)이다 — 같은 빚 파일이
    도구에 따라 다르게 읽히지 않는다. 레인 실물 형식(`#12 application.pairing` 류
    dotted-module 부분문자열)은 정규화가 건드리지 않으므로 그대로 매칭된다(하위 호환).
    번호 없는 줄 항목(`=`)은 `<검사기 파일> :: <정규화 라인>` 과 글자 전체가 같을 때만 맞는다 —
    registry_gate 의 줄은 이미 그 모양이고(checker 없음), scope 렌더는 자기 검사기 파일 이름을 준다.
    """
    keyed: str = normalized_line if checker is None else f"{checker} :: {normalized_line}"
    return any(keyed == sub if tag == "=" else (f"[{tag}]" in normalized_line and sub in normalized_line)
               for tag, sub in debt_rules)


def validate_materials(target: Path, anchor: str, debt_file: "str | None",
                       approved_merge_file: "str | None" = None) -> None:
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
    if approved_merge_file is not None:
        merge_path: Path = Path(approved_merge_file)
        if not merge_path.is_file():
            raise AnchorDiffUsage(f"승인 머지 목록 {merge_path} 없음")
        root: Path = target.resolve()
        load_approved_merges(merge_path, root, run_git(root, "rev-parse", "--verify", f"{anchor}^{{commit}}").stdout.strip(),
                             run_git(root, "rev-parse", "HEAD").stdout.strip())


def _normalize(line: str, roots: "tuple[str, ...]") -> str:
    out: str = line.strip()
    for prefix in roots:  # 절대 경로 echo 정규화(registry_gate A3 동형)
        out = out.replace(prefix, "")
    return _LINENO_RE.sub(":N", out)  # 라인번호 정규화(상하 이동 오탐 방지)



# 증명 머지 뒤 조건(ⓒ 미승인 머지 · ⓑ 뒤 승인 머지의 ^2 · ⓓ 사슬 이어짐)이 렌더하는 사슬 커밋(서로 다른 트리)의 최대 수.
# 넘으면 그 머지로는 증명하지 않는다(`측정 생략(…)` — fail-closed). 결정적 판정을 위해 시간이 아니라 수로 묶는다.
CHAIN_LIMIT: int = 64


@dataclass(frozen=True)
class Sample:
    """한 커밋의 측정 — lines None = 증거로 못 씀 · partial = 끝까지 잰 렌더가 아님(«없다» 를 말할 수 없음)."""

    lines: "frozenset[str] | None"
    partial: bool = False


def _prefetch_workers() -> int:
    """사슬 렌더 병렬 수 — registry_gate 의 `DJR_REGISTRY_WORKERS` 와 같은 손잡이(없으면 4)."""
    raw: str = os.environ.get("DJR_REGISTRY_WORKERS", "").strip()
    return int(raw) if raw.isdigit() and int(raw) > 0 else 4


def tree_id(root: Path, sha: str) -> str:
    return run_git(root, "rev-parse", f"{sha}^{{tree}}").stdout.strip() or sha


def after_merge_check(*, key: str, m: "ApprovedMerge", active: "list[ApprovedMerge]", chain: "list[ChainCommit]",
                      sample: "Callable[[str], Sample]", tree_of: "Callable[[str], str]",
                      limit: int = CHAIN_LIMIT,
                      prefetch: "Callable[[list[str]], None] | None" = None) -> "str | None":
    """증명 머지 m 이 L(ℓ ∈ R(m^2) ∖ R(m^1))을 통과한 뒤의 조건 — None 이면 통과, 아니면 귀속 유지 사유.

    ⓒ m 뒤 first-parent 사슬에 승인 목록 밖의 머지(부모 ≥ 2)가 없다
    ⓑ m 뒤의 모든 참여 승인 머지 m′ 에서 ℓ ∈ R(m′^2)          (상류가 뒤에서 고친 줄을 옛 머지로 증명하지 않는다)
    ⓓ m(병합 결과 — ⓐ) 부터 HEAD 커밋까지 사슬 커밋마다 ℓ ∈ R(c)  (레인이 없앴다 되살린 줄을 증명하지 않는다)
    sample(sha) 는 호출측 측정(registry_gate = positional 단일 검사기 · scope 렌더 = 기준선 사다리)."""
    position: "dict[str, int]" = {c.sha: i for i, c in enumerate(chain)}
    start: "int | None" = position.get(m.sha)
    if start is None:
        return f"유입 증명 실패(승인 머지 {m.sha[:12]} 가 사슬 밖)"
    approved: "set[str]" = {a.sha for a in active}
    for c in chain[start + 1:]:
        if len(c.parents) >= 2 and c.sha not in approved:
            return f"유입 증명 실패(승인 머지 {m.sha[:12]} 뒤 미승인 머지 {c.sha[:12]})"
    for later in active:
        if position.get(later.sha, -1) <= start:
            continue
        got: Sample = sample(later.parent2)
        if got.lines is None or (key not in got.lines and got.partial):
            return f"측정 무효(뒤 승인 머지 {later.sha[:12]} 의 ^2) — {m.sha[:12]}"
        if key not in got.lines:
            return f"유입 증명 실패(뒤 승인 머지 {later.sha[:12]} 의 ^2 에 없음)"
    commits: "list[ChainCommit]" = chain[start:]
    trees: "list[str]" = []
    for c in commits:
        t: str = tree_of(c.sha)
        if not trees or trees[-1] != t:
            trees.append(t)
    if len(trees) > limit:
        return f"측정 생략(사슬 커밋 {len(trees)} > 한도 {limit}) — {m.sha[:12]}"
    if prefetch is not None:
        prefetch([c.sha for c in commits])  # 사슬 커밋 렌더를 한꺼번에(병렬로) — 판정은 아래 순차 대조가 한다
    for c in commits:
        got = sample(c.sha)
        if got.lines is None or (key not in got.lines and got.partial):
            return f"측정 무효(사슬 {c.sha[:12]}) — {m.sha[:12]}"
        if key not in got.lines:
            if c.sha == m.sha:
                return f"유입 증명 실패(승인 머지 {m.sha[:12]} 결과에 없음)"
            return f"유입 증명 실패(승인 머지 {m.sha[:12]} 뒤 사슬 {c.sha[:12]} 에 없음)"
    return None



class PathFacts:
    """한 실행의 git 사실로 주어 파일 p 를 가른다 — registry_gate `_provenance_split` 의 (i)(ii) 와 같은 판정·같은 사유 글자.

    classify(p) = ("파일", 전달 머지) | ("상호작용", None) | 귀속 유지 사유(str)
      비-blob 경로 — HEAD 의 일반 파일(blob · 심링크 아님)이 아니다
      worktree 수정 중 — 작업 트리의 p 가 HEAD 와 다르다(미추적·수정·삭제)
      파일 = F1 · 상호작용 = F2 · 그 밖 = last_toucher 사유(충돌 해소분 · 미승인 머지 경유 · 레인 커밋 수정 · 비머지 커밋 경유)"""

    def __init__(self, root: Path, anchor_sha: str, head_sha: str,
                 chain: "list[ChainCommit]", active: "list[ApprovedMerge]") -> None:
        self.root: Path = root
        self.chain: "list[ChainCommit]" = chain
        self.active: "list[ApprovedMerge]" = active
        self._cache: "dict[str, dict[str, str]]" = {}
        self.head: "dict[str, str]" = self.blobs(head_sha)
        self.anchor: "dict[str, str]" = self.blobs(anchor_sha)
        self.dirty: "set[str]" = {entry[3:] for entry in run_git(
            root, "status", "--porcelain", "--untracked-files=all", "-z").stdout.split("\0") if len(entry) > 3}
        self.position: "dict[str, int]" = {c.sha: i for i, c in enumerate(chain)}

    def blobs(self, sha: str) -> "dict[str, str]":
        if sha not in self._cache:
            self._cache[sha] = tree_blobs(self.root, sha)
        return self._cache[sha]

    def classify(self, p: str) -> "tuple[str, ApprovedMerge | None] | str":
        if p not in self.head:
            return "비-blob 경로"
        if p in self.dirty:
            return "worktree 수정 중"
        deliver: "ApprovedMerge | None" = next(
            (m for m in self.active if self.blobs(m.parent1).get(p) != self.blobs(m.sha).get(p)
             and self.blobs(m.sha).get(p) == self.blobs(m.parent2).get(p) == self.head[p]), None)
        if deliver is not None:
            return ("파일", deliver)
        if self.head[p] == self.anchor.get(p):
            return ("상호작용", None)
        return self.retained_reason(p)

    def retained_reason(self, p: str) -> str:
        last: "ChainCommit | None" = next(
            (c for c in reversed(self.chain)
             if self.blobs(c.sha).get(p) != (self.blobs(c.parents[0]).get(p) if c.parents else None)), None)
        if last is None:
            return "유입 증명 실패(경로 추적 불능)"
        approved: "set[str]" = {m.sha for m in self.active}
        if last.is_merge and last.sha in approved:
            return f"충돌 해소분(M≠M^2) — {last.sha[:12]}"
        if last.is_merge:
            return f"미승인 머지 경유 {last.sha[:12]}"
        before: "ApprovedMerge | None" = next(
            (m for m in self.active if self.position.get(m.sha, 1 << 30) < self.position[last.sha]
             and self.blobs(m.sha).get(p) != self.blobs(m.parent1).get(p)), None)
        if before is not None:
            return f"레인 커밋 수정 {last.sha[:12]}(승인 머지 {before.sha[:12]} 이후)"
        return f"비머지 커밋 경유 {last.sha[:12]}"


@dataclass
class _InflowSplit:
    """scope 렌더의 승인 유입 분할 결과 — inflow(줄, 증명 머지, 종류, 비고) · retained(줄 → 귀속 유지 사유)."""

    inflow: "list[tuple[str, str, str, str | None]]"
    retained: "dict[str, str]"
    measured: "dict[str, _Baseline | None]" = field(default_factory=dict)   # 커밋 sha → 기준선(증거로 못 쓰면 None)
    failures: "dict[str, str]" = field(default_factory=dict)                # 커밋 sha → 왜 못 쓰는가
    renders: int = 0                                                        # 서로 다른 트리를 잰 수


def _approved_inflow_split(
    *, root: Path, anchor_sha: str, head_sha: str, merges: "list[ApprovedMerge]", new: "list[str]",
    roots: "tuple[str, ...]", td: Path, script: Path, argv: "list[str]", path_flags: "frozenset[str]",
    baseline_collects_all: bool, chain: "list[ChainCommit]",
) -> _InflowSplit:
    """빚 매칭 뒤 남은 «신규» 줄을 «승인 유입 ⊔ 신규(귀속 유지)» 로 가른다 — 어떤 줄도 버리지 않는다.

    승인 유입(ℓ) ⟺ PathFacts.classify(p) ∈ {파일, 상호작용} ∧ ∃M: L(ℓ, M) ∧ after_merge_check(ℓ, M) 통과
      L = ℓ ∈ R(M^2) ∧ ( [파일 ∧ M^1 에 p 항목 없음] ∨ [M^1 렌더가 완결 ∧ ℓ ∉ R(M^1)] )
      R(S) = 커밋 S 의 git archive 사본(사본 밖 심링크 없음)에서 같은 검사기·같은 argv 로 돌린 기준선 사다리 줄 집합
      완결 = 사다리 1칸(조정 없는 selector 렌더)이 섰고 ∧ (exit 0 ∨ baseline_collects_all)"""
    out: _InflowSplit = _InflowSplit([], {})
    active: "list[ApprovedMerge]" = sorted((m for m in merges if m.participates), key=lambda m: m.position or 0)
    by_tree: "dict[str, tuple[Sample, _Baseline | None, str | None]]" = {}
    tree_cache: "dict[str, str]" = {}

    def tree_of(sha: str) -> str:
        if sha not in tree_cache:
            tree_cache[sha] = tree_id(root, sha)
        return tree_cache[sha]

    def measure(sha: str) -> "tuple[Sample, _Baseline | None]":
        t: str = tree_of(sha)
        if t not in by_tree:
            dest: Path = td / f"tree-{t[:12]}"
            failure: "str | None" = None
            base: "_Baseline | None" = None
            got: Sample = Sample(None)
            try:
                snapshot_anchor(root, sha, dest)
                escape: "str | None" = snapshot_escape(dest)
            except (AnchorDiffUsage, OSError) as exc:
                failure = f"스냅숏 실패 — {type(exc).__name__}: {str(exc).strip()}"
            else:
                if escape is not None:
                    failure = f"사본 밖을 가리키는 심링크 {escape}"
                else:
                    base = _baseline_lines(script, dest, argv, path_flags)
                    r: "tuple[str, ...]" = (str(dest) + "/", str(dest))
                    if base.error is not None:
                        base.error = base.error.replace(str(dest) + "/", "").replace(str(dest), "")
                    if base.code in (0, 2) and not measurement_failed(base.lines):
                        # «없다» 를 말할 수 있는 렌더 = 사다리 1칸 ∧ (exit 0 ∨ 기준선 모드에서 모든 슬라이스를 모으는 검사기)
                        got = Sample(frozenset(_normalize(line, r) for line in base.lines),
                                     partial=(base.used != "selector 렌더 재실행"
                                              or (base.code == 2 and not baseline_collects_all)))
            finally:
                shutil.rmtree(dest, ignore_errors=True)  # 실패한 사본도 바로 지운다(사슬 길이만큼 디스크가 늘지 않게)
            by_tree[t] = (got, base, failure)
            out.renders += 1
        got, base, failure = by_tree[t]
        out.measured.setdefault(sha, base)
        if failure is not None:
            out.failures.setdefault(sha, failure)
        return got, base

    def sample(sha: str) -> Sample:
        return measure(sha)[0]

    def prefetch(shas: "list[str]") -> None:
        todo: "dict[str, str]" = {}
        for sha in shas:
            t: str = tree_of(sha)
            if t not in by_tree and t not in todo:
                todo[t] = sha
        if len(todo) > 1:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=_prefetch_workers()) as pool:
                list(pool.map(measure, todo.values()))

    def exists_at(sha: str, path: str) -> bool:
        """커밋 sha 의 트리에 path 라는 항목(파일·폴더·링크 무엇이든)이 있는가."""
        return run_git(root, "cat-file", "-e", f"{sha}:{path}").returncode == 0

    facts: PathFacts = PathFacts(root, anchor_sha, head_sha, chain, active)
    for line in new:
        key: str = _normalize(line, roots)
        p: "str | None" = _subject_file(key)
        if p is None:
            out.retained[line] = "주어 경로 없음"
            continue
        judged: "tuple[str, ApprovedMerge | None] | str" = facts.classify(p)
        if isinstance(judged, str):
            out.retained[line] = judged   # registry_gate 와 같은 사유 글자(같은 함수)
            continue
        kind: str
        deliver: "ApprovedMerge | None"
        kind, deliver = judged
        order: "list[ApprovedMerge]" = ([deliver] + [m for m in active if m is not deliver]
                                        if deliver is not None else list(active))
        proven: "tuple[str, str | None] | None" = None
        invalid: "str | None" = None
        after: "str | None" = None
        for m in order:
            incoming: Sample
            incoming_base: "_Baseline | None"
            incoming, incoming_base = measure(m.parent2)
            if incoming.lines is None or (key not in incoming.lines and incoming.partial):
                invalid = invalid or f"측정 무효(M^2) — {m.sha[:12]}"
                continue
            if key not in incoming.lines:
                continue
            note: "str | None" = None
            if kind == "파일" and not exists_at(m.parent1, p):
                note = "^1 에 주어 파일 없음"   # 주어 파일이 레인 쪽 직전 트리에 없었다 — 그 파일 주어의 같은 줄은 거기서 날 수 없다
            else:
                lane: Sample
                _lane_base: "_Baseline | None"
                lane, _lane_base = measure(m.parent1)
                if lane.lines is None or lane.partial:
                    invalid = invalid or f"측정 무효(M^1) — {m.sha[:12]}"
                    continue
                if key in lane.lines:  # type: ignore[operator]
                    continue  # 레인 쪽 직전에도 있던 줄 — 이 머지가 들인 줄이 아니다(이중 원인)
                note = ""
            reason: "str | None" = after_merge_check(key=key, m=m, active=active, chain=chain,
                                                     sample=sample, tree_of=tree_of, prefetch=prefetch)
            if reason is None:
                proven = (m.sha, note)
                break
            after = after or reason
        if proven is not None:
            out.inflow.append((line, proven[0], kind, proven[1]))
        elif after is not None:
            out.retained[line] = after
        elif invalid is not None:
            out.retained[line] = invalid
        else:
            out.retained[line] = "유입 증명 실패(이중 원인)" if kind == "파일" else "상호작용 미증명"
    return out


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
    approved_merge_file: "str | None" = None,
    baseline_collects_all: bool = False,
) -> int:
    """현재 진단을 앵커 기준선·승인 빚·증명한 승인 유입으로 나누어 보고하고 신규분의 exit를 정한다."""
    debt_rules: "list[tuple[str, str]]" = []
    if debt_file is not None:
        debt_path: Path = Path(debt_file)
        if not debt_path.is_file():
            raise AnchorDiffUsage(f"빚 목록 {debt_path} 없음")
        debt_rules = load_debt(debt_path)
    resolved_target: Path = target.resolve()
    has_sister: bool = sister_owned(resolved_target)
    sha: str = resolve_anchor(resolved_target, anchor)
    merges: "list[ApprovedMerge]" = []
    chain: "list[ChainCommit]" = []
    head_sha: str = ""
    if approved_merge_file is not None:
        merge_path: Path = Path(approved_merge_file)
        if not merge_path.is_file():
            raise AnchorDiffUsage(f"승인 머지 목록 {merge_path} 없음")
        head_sha = run_git(resolved_target, "rev-parse", "HEAD").stdout.strip()
        merges, chain = load_approved_merges(merge_path, resolved_target, sha, head_sha)
    split: "_InflowSplit | None" = None
    with tempfile.TemporaryDirectory() as td:
        snap: Path = Path(td) / "anchor"
        snapshot_anchor(resolved_target, sha, snap)
        base: _Baseline = _baseline_lines(script, snap, argv, path_flags)
        if base.error is not None:
            base.error = base.error.replace(str(snap) + "/", "").replace(str(snap), "")
        code, lines, used = base.code, base.lines, base.used
        normal_measurement: bool = (code in (0, 2) and not analysis_pending
                                    and not measurement_failed(lines) and not measurement_failed(findings))
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
                hit: bool = debt_match(_normalize(line, roots), debt_rules, checker=script.name)
                (debt if hit else rest).append(line)
            new = rest

        if approved_merge_file is not None:
            # 순서: 신규 → 빚 분리 → 승인 유입 분리(빚 우선) → 자매 → 잔여 = exit 근거(registry_gate 와 같은 순서).
            if new and not measurement_failed(findings):
                split = _approved_inflow_split(
                    root=resolved_target, anchor_sha=sha, head_sha=head_sha, merges=merges, new=new,
                    roots=roots, td=Path(td), script=script, argv=argv, path_flags=path_flags,
                    baseline_collects_all=baseline_collects_all, chain=chain)
                proven: "set[str]" = {line for line, _m, _k, _n in split.inflow}
                new = [line for line in new if line not in proven]
            else:
                split = _InflowSplit([], {})

    sister: "list[str]" = []
    if has_sister and normal_measurement:
        rest = []
        for line in new:
            invalid: bool = split is not None and split.retained.get(line, "").startswith(("측정 무효(", "측정 생략("))
            (sister if not invalid and sister_path(subject_path(line)) else rest).append(line)
        new = rest

    print(f"{label} 앵커 차분(--anchor {sha[:12]} · 기준선={used}):")
    counts: str = f"  신규분(앵커 이후) {len(new)}건 · 앵커 기존분(잔존) {len(existing)}건 · 이관 빚 {len(debt)}건"
    if split is not None:
        counts += f" · 승인 유입 {len(split.inflow)}건"
    print(counts)
    if base.error is not None:
        print(f"  기준선 오류: {base.error}")
    if new:
        print("  == 신규분 — 차분에 종속되지 않는 직접 blocker ==")
        for line in new:
            print(f"  {line.strip()}")
            if split is not None:
                print(f"    ↳ 귀속 유지: {split.retained.get(line, '판정 미도달')}")
    if debt:
        print("  == 이관 빚(사용자 승인 목록 매칭 — exit 제외·기록 의무) ==")
        for line in debt:
            print(f"  {line.strip()}")
    if split is not None:
        print(f"  == 승인 유입(발주자 승인 머지 경유 · provenance 증명 — exit 제외·기록 의무) {len(split.inflow)}건 ==")
        for m in merges:
            if not m.participates:
                print(f"  [M {m.sha[:12]}] {m.subject} · 앵커 이전 — 판정 불참")
                continue
            files: int = sum(1 for _l, s, k, _n in split.inflow if s == m.sha and k == "파일")
            inter: int = sum(1 for _l, s, k, _n in split.inflow if s == m.sha and k == "상호작용")
            print(f"  [M {m.sha[:12]}] {m.subject} · ^1 {m.parent1[:12]} · ^2 {m.parent2[:12]}({m.parent2_ref}) · "
                  f"파일 {files} · 상호작용 {inter}")
            if m.parent2_only_head:
                print(f"    ↳ 주의: ^2 {m.parent2[:12]} 를 포함하는 ref 가 HEAD 브랜치뿐 — 역방향/합성 머지 의심"
                      "(발주자 확인 — 등재 전 `^2` 가 main(상류) 이력에 있는지 확인 · exit 무변)")
            for side, commit in (("^2", m.parent2), ("^1", m.parent1)):
                if commit not in split.measured:
                    continue
                measured: "_Baseline | None" = split.measured[commit]
                if measured is None:
                    print(f"    ↳ {side} 기준선: 측정 무효 — {split.failures.get(commit, '스냅숏 실패')}")
                else:
                    print(f"    ↳ {side} 기준선: {measured.used}"
                          + (f" — 오류: {measured.error}" if measured.error is not None else ""))
        for line, m_sha, kind, note in split.inflow:
            print(f"  {line.strip()}")
            print(f"    ↳ 유입: {m_sha[:12]}(L 증명{' · ' + note if note else ''}) · "
                  f"{'파일 verbatim' if kind == '파일' else '상호작용'}")
    if sister:
        print(f"  == {SISTER_TITLE} {len(sister)}건 ==")
        for line in sister:
            print(f"  {line.strip()}")
    if existing:
        print("  == 앵커 기존분 — blocker 아님·보고 의무(침묵 금지)·이 빌드에서 즉석 수리하지 않는다 ==")
        for line in existing:
            print(f"  {line.strip()}")
    tail: str = ""
    if split is not None:
        approved: "set[str]" = {m.sha for m in merges if m.participates}
        in_chain: "list[ChainCommit]" = [c for c in chain if c.is_merge]
        unapproved: "list[str]" = [c.sha[:12] for c in in_chain if c.sha not in approved]
        print(f"  provenance: first-parent 사슬 {sha[:12]}..HEAD 머지 {len(in_chain)}"
              f"(승인 {len(in_chain) - len(unapproved)} · 미승인 {len(unapproved)}"
              + (": " + " ".join(unapproved) if unapproved else "") + f") · 스냅숏 기준선 실행 {split.renders}")
        tail = f"(승인 유입 {len(split.inflow)}건 제외)"
    if new:
        print(f"판정: 신규분 {len(new)}건 → blocker(exit 2) — 기존분 {len(existing)}건은 별도 보고{tail}")
        return 2
    if analysis_pending:
        print(
            f"판정: 신규분 0건 → 차분 계열 강등 — 잔여 분석/토큰 진단의 exit 가 우선한다"
            f"(앵커 기존분 {len(existing)}건과 빚 {len(debt)}건은 위 보고 채널로만 남긴다){tail}"
        )
        return 0
    print(
        f"판정: 신규분 0건 → exit 0 (신규 0 ≠ 전체 clean — 앵커 기존분 {len(existing)}건과 "
        f"빚 {len(debt)}건은 위 보고 채널로만 남긴다){tail}"
    )
    return 0
