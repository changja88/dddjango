#!/usr/bin/env python3
"""git touched 판정 스모크 — composition-root · idempotency-scope-creep 의 «git 질의 순서»(속도 개선 C1⑴)를
경계 사례 git 저장소에서 고정한다.

C1⑴ 은 두 검사기가 «후보·신호가 있는 파일에만» git 을 묻게 바꿨다(composition-root 는 후보 0 BC 에도 BC
단위 트리 질의 1회를 남겨 저장소 결손 exit 1 을 지킨다). 이 스모크의 기대값은 **바꾸기 전 코드로 `--emit`**
한 골든(`workspace/eval/fixtures/git_touched/expected.json` · `emitted_from` 에 커밋)이다 — 현행 코드가 골든과
같으면 «옛 == 새»다. fixture_matrix 밖에 두는 이유는 registry_gate_smoke 와 같다(hermetic 비-git 원칙과 상반).

시나리오(× 호출 셋: composition-root · composition-root `--error-profile auto` · idempotency):
  ① clean                     깨끗한 트리
  ② untracked_candidate       미추적 후보 + 미추적 멱등 산출물
  ③ modified_other            커밋된 후보 + 같은 BC 다른 파일 수정 · 멱등 산출물 수정
  ④ staged_delete             staged 삭제(인벤토리에서 사라진 경로)
  ⑤ unstaged_delete_candidate 미스테이징 삭제된 후보
  ⑥ rename_across_bc          BC 를 넘는 staged rename(멱등 산출물 포함)
  ⑦ rename_candidate_across_bc 커밋된 후보를 다른 BC 로 git mv(원 BC 는 후보 0)
  ⑧ no_head · no_head_unstaged HEAD 없음(스테이징 있음·없음)
  ⑨ subdir_target             하위 폴더 TARGET + TARGET 밖 변경
  ⑩ special_names · special_only_glob  글롭 메타문자·공백·한글·`*.py` 이름 · 글롭이 인벤토리 밖 시험 파일만 잡는 경우
  ⑪ non_git                   비-git TARGET
  ⑫ submodule_bc · submodule_in_bc · submodule_bc_dirty · application_is_submodule(_nocand)  서브모듈 넷
  ⑬ symlinks                  심볼릭 링크 BC · 링크 후보(대상만 변경)
  ⑭ gitignored_candidate      `.gitignore` 된 후보·멱등 산출물
  ⑮ case_change               대소문자만 바꾼 후보(APFS 대소문자 무시)
  ⑯ linked_worktree           linked worktree(`.git` 파일)
  ⑰ staged_then_modified      staged 뒤 재수정 후보
  ⑱ composition_dir           off-tree `composition/` 안 파일(후보 아님)
  ⑲ idem_adopted              멱등: 미요청 scope + 신규 산출물 + G1 채택 배너(면제)
  ⑳ corrupt_root_tree(_mixed)  루트 트리 결손(후보 무/다른 BC 후보) — exit 1(«분석 불능» 보존)
     corrupt_subtree_nocand · corrupt_subtree_cand  하위 트리 결손 + cache-tree 유효 — 옛·새 같은 exit(트리를 안 읽어 0)
     corrupt_subtree_staged      하위 트리 결손 + 같은 폴더 스테이징(cache-tree 무효) — 옛·새 같은 exit(1)

비교: exit · stdout · 레코드(`DJR_FINDINGS_JSON` · 휘발 필드 제외)는 전부, stderr 는 ⑧·⑳ 밖에서만(옛 코드의 파일별
git 잡음·«비교 불능» 문구의 경로가 다르다 — stdout·exit·레코드 밖). 임시 경로는 `<TMP>` 로 정규화한다.
git 은 전역·시스템 설정을 끄고(`GIT_CONFIG_GLOBAL=/dev/null` · `GIT_CONFIG_NOSYSTEM=1`) 시각을 고정해 돈다.
⑮ 는 대소문자 무시 파일 시스템(macOS 기본) 기준 골든이다.

골든 출처 가드: 비교 모드는 `emitted_from` 이 커밋 SHA 가 아닌 골든(`--from-commit` 없이 뜬 «working-tree» 등)을
재료 결손(exit 1)으로 거절한다 — red 를 재기록 한 번으로 지우면 «옛 == 새» 보증이 소리 없이 사라지기 때문이다
(대조 전에 `GoldenSourceGuard` 단위 시험이 이 가드를 먼저 고정한다).
유지 규칙: 두 검사기의 출력을 일부러 바꾸는 개정(규칙·문구)은 그 개정 커밋으로 `--emit --from-commit <그 커밋>` 해
골든을 다시 뜨고, 그때부터 골든은 «C1⑴ 옛 == 새»가 아니라 그 커밋 기준 회귀 골든임을 커밋 메시지에 적는다.

사용: python3 git_touched_smoke.py                          # 현행 scripts ↔ 골든 대조
      python3 git_touched_smoke.py --emit --from-commit <sha> # 그 커밋의 dddjango/scripts 로 골든 기록
      python3 git_touched_smoke.py --emit --out <path>        # 현행 scripts 결과를 다른 파일로(A/B 용 · 골든 아님)
      python3 git_touched_smoke.py --scripts <dir>            # 다른 scripts 폴더 ↔ 골든(변이 시험용)
exit 0 = 전 케이스 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import re
import tempfile
import unittest
from pathlib import Path
from typing import Callable

ROOT: Path = Path(__file__).resolve().parents[2]
SCRIPTS: Path = ROOT / "dddjango" / "scripts"
GOLDEN: Path = ROOT / "workspace" / "eval" / "fixtures" / "git_touched" / "expected.json"
SCHEMA: str = "git-touched-smoke/1"
_COMMIT_SHA: "re.Pattern[str]" = re.compile(r"[0-9a-f]{7,40}")

_GIT_DATE: str = "2026-10-01T00:00:00+0900"
_GIT_CONFIG: "list[str]" = ["-c", "user.name=smoke", "-c", "user.email=smoke@dddjango",
                            "-c", "init.defaultBranch=main", "-c", "protocol.file.allow=always"]
_VOLATILE: "tuple[str, ...]" = ("run_id", "ts", "record_id", "experiment_run_id")
CALLS: "list[tuple[str, str, list[str]]]" = [
    ("composition-root", "check-composition-root.py", []),
    ("composition-root-auto", "check-composition-root.py", ["--error-profile", "auto"]),
    ("idempotency", "check-idempotency-scope-creep.py", []),
]
# stderr 를 비교하지 않는 시나리오(⑧·⑳) — 옛 코드의 파일별 git 잡음·«비교 불능» 문구 경로만 다르다.
_STDERR_FREE: "frozenset[str]" = frozenset({
    "no_head", "no_head_unstaged", "corrupt_root_tree", "corrupt_root_tree_mixed",
    "corrupt_subtree_nocand", "corrupt_subtree_cand", "corrupt_subtree_staged",
})


def _git_env() -> "dict[str, str]":
    env: "dict[str, str]" = {k: v for k, v in os.environ.items() if not k.startswith(("DJR_", "GIT_"))}
    env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
               GIT_AUTHOR_DATE=_GIT_DATE, GIT_COMMITTER_DATE=_GIT_DATE)
    return env


def _git(repo: Path, *args: str) -> str:
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(
        ["git", *_GIT_CONFIG, "-C", str(repo), *args], capture_output=True, text=True, env=_git_env())
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 실패: {proc.stderr.strip()}")
    return proc.stdout


def _write(path: Path, text: str = "x = 1\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _layout(base: Path) -> None:
    """BC 셋 — alpha(커밋 후보) · beta(커밋 후보 + 커밋 멱등 산출물) · gamma(후보 없음 + 멱등 헤더) + 미요청 scope."""
    _write(base / "application/__init__.py", "")
    _write(base / "application/alpha/domain_layer/model.py")
    _write(base / "application/alpha/composition_root.py", "WIRED = True\n")
    _write(base / "application/beta/domain_layer/model.py")
    _write(base / "application/beta/application_layer/svc.py", "def f():\n    return 1\n")
    _write(base / "application/beta/composition_root.py", "WIRED = True\n")
    _write(base / "application/beta/driven_layer/idempotency_store.py", "class IdempotencyStore:\n    pass\n")
    _write(base / "application/gamma/domain_layer/model.py")
    _write(base / "application/gamma/driving_layer/headers.py", "H = 'Idempotency-Key'\n")
    _write(base / "application/gamma/application_layer/svc2.py", "def g():\n    return 2\n")
    _write(base / ".dddjango/20260101-x/scope.md", "- 멱등성은 이번 요청에 명시되지 않았다\n")


def _fresh(td: Path, name: str) -> Path:
    repo: Path = td / name
    repo.mkdir(parents=True)
    return repo


def _committed(td: Path, name: str, sub: str = "") -> "tuple[Path, Path]":
    repo: Path = _fresh(td, name)
    _git(repo, "init", "-q")
    base: Path = repo / sub if sub else repo
    _layout(base)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo, base


def _drop_object(repo: Path, rev: str) -> None:
    """객체 하나를 지워 저장소 결손을 만든다(새 저장소라 loose 객체다)."""
    sha: str = _git(repo, "rev-parse", rev).strip()
    obj: Path = repo / ".git" / "objects" / sha[:2] / sha[2:]
    obj.chmod(0o644)
    obj.unlink()


# ── 시나리오 ────────────────────────────────────────────────────────────────────

def s_clean(td: Path) -> Path:
    return _committed(td, "clean")[1]


def s_untracked_candidate(td: Path) -> Path:
    _, b = _committed(td, "untracked_candidate")
    _write(b / "application/gamma/composition_root.py", "NEW = 1\n")
    _write(b / "application/gamma/driven_layer/idempotency_new.py", "class IdempotencyRecord:\n    pass\n")
    return b


def s_modified_other(td: Path) -> Path:
    _, b = _committed(td, "modified_other")
    _write(b / "application/alpha/domain_layer/model.py", "x = 2\n")
    _write(b / "application/gamma/driving_layer/headers.py", "H = 'Idempotency-Key'  # 수정\n")
    return b


def s_staged_delete(td: Path) -> Path:
    repo, b = _committed(td, "staged_delete")
    _git(repo, "rm", "-q", "application/beta/application_layer/svc.py")
    return b


def s_unstaged_delete_candidate(td: Path) -> Path:
    _, b = _committed(td, "unstaged_delete_candidate")
    (b / "application/alpha/composition_root.py").unlink()
    return b


def s_rename_across_bc(td: Path) -> Path:
    repo, b = _committed(td, "rename_across_bc")
    (b / "application/gamma/driven_layer").mkdir(parents=True, exist_ok=True)
    _git(repo, "mv", "application/beta/driven_layer/idempotency_store.py",
         "application/gamma/driven_layer/moved_idem.py")
    _git(repo, "mv", "application/beta/application_layer/svc.py", "application/gamma/application_layer/svc.py")
    return b


def s_rename_candidate_across_bc(td: Path) -> Path:
    repo, b = _committed(td, "rename_candidate_across_bc")
    _git(repo, "mv", "application/beta/composition_root.py", "application/gamma/composition_root.py")
    return b


def s_no_head(td: Path) -> Path:
    repo: Path = _fresh(td, "no_head")
    _git(repo, "init", "-q")
    _layout(repo)
    _git(repo, "add", "-A")
    return repo


def s_no_head_unstaged(td: Path) -> Path:
    repo: Path = _fresh(td, "no_head_unstaged")
    _git(repo, "init", "-q")
    _layout(repo)
    return repo


def s_subdir_target(td: Path) -> Path:
    repo, b = _committed(td, "subdir_target", sub="proj")
    _write(b / "application/alpha/domain_layer/model.py", "x = 3\n")
    _write(repo / "other/application/omega/domain_layer/m.py")  # TARGET 밖 변경
    return b


def s_special_names(td: Path) -> Path:
    repo, b = _committed(td, "special_names")
    _write(b / "application/delta/domain_layer/m[o]del.py")
    _write(b / "application/delta/domain_layer/한글 모듈.py")
    _write(b / "application/delta/domain_layer/*.py", "star = 1\n")
    _write(b / "application/delta/composition_root.py", "WIRED = 1\n")
    _write(b / "application/delta/driven_layer/idem[1].py", "class IdempotencyX:\n    pass\n")
    _write(b / "application/delta/driven_layer/멱등 idempotency.py", "pass\n")
    _write(b / "application/de lta/domain_layer/model.py")
    _write(b / "application/de lta/composition_root.py", "WIRED = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "special")
    _write(b / "application/delta/domain_layer/model.py", "changed = 1\n")  # `m[o]del.py` 글롭이 잡는 파일
    return b


def s_special_only_glob(td: Path) -> Path:
    repo, b = _committed(td, "special_only_glob")
    _write(b / "application/delta/domain_layer/m[o]del.py")
    _write(b / "application/delta/composition_root.py", "WIRED = 1\n")
    _write(b / "application/delta/domain_layer/tests/test_x.py", "def test():\n    pass\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "special")
    _write(b / "application/delta/domain_layer/tests/test_x.py", "def test():\n    assert 1\n")
    return b


def s_non_git(td: Path) -> Path:
    repo: Path = _fresh(td, "non_git")
    _layout(repo)
    return repo


def _sub_source(td: Path, name: str, files: "dict[str, str]") -> Path:
    sub: Path = _fresh(td, name)
    _git(sub, "init", "-q")
    for rel, text in files.items():
        _write(sub / rel, text)
    _git(sub, "add", "-A")
    _git(sub, "commit", "-qm", "sub")
    return sub


def s_submodule_bc(td: Path) -> Path:
    sub: Path = _sub_source(td, "submodule_src", {
        "domain_layer/model.py": "x = 1\n", "composition_root.py": "WIRED = 1\n",
        "driven_layer/idempotency_store.py": "class S:\n    pass\n"})
    repo, b = _committed(td, "submodule_bc")
    _git(repo, "submodule", "add", "-q", str(sub), "application/epsilon")
    _git(repo, "commit", "-qm", "add sub")
    return b


def s_submodule_in_bc(td: Path) -> Path:
    sub: Path = _sub_source(td, "submodule_src2", {"vendor_mod.py": "x = 1\n"})
    repo, b = _committed(td, "submodule_in_bc")
    _git(repo, "submodule", "add", "-q", str(sub), "application/gamma/driven_layer/vendor")
    _git(repo, "commit", "-qm", "add sub")
    return b


def s_submodule_bc_dirty(td: Path) -> Path:
    sub: Path = _sub_source(td, "submodule_src3", {"domain_layer/model.py": "x = 1\n"})
    repo, b = _committed(td, "submodule_bc_dirty")
    _git(repo, "submodule", "add", "-q", str(sub), "application/epsilon")
    _git(repo, "commit", "-qm", "add sub")
    _write(b / "application/epsilon/domain_layer/model.py", "x = 9\n")  # 서브모듈 안 수정
    _write(b / "application/epsilon/composition_root.py", "WIRED = 1\n")  # 서브모듈 안 미추적 후보
    return b


def _application_submodule(td: Path, name: str, files: "dict[str, str]") -> Path:
    sub: Path = _sub_source(td, f"{name}_src", files)
    repo: Path = _fresh(td, name)
    _git(repo, "init", "-q")
    _write(repo / "README.md", "r\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    _git(repo, "submodule", "add", "-q", str(sub), "application")
    _git(repo, "commit", "-qm", "add sub")
    return repo


def s_application_is_submodule(td: Path) -> Path:
    return _application_submodule(td, "application_is_submodule", {
        "__init__.py": "", "gamma/domain_layer/model.py": "x = 1\n",
        "zeta/domain_layer/model.py": "x = 1\n", "zeta/composition_root.py": "W = 1\n"})


def s_application_is_submodule_nocand(td: Path) -> Path:
    return _application_submodule(td, "application_is_submodule_nocand", {
        "__init__.py": "", "gamma/domain_layer/model.py": "x = 1\n"})


def s_symlinks(td: Path) -> Path:
    repo, b = _committed(td, "symlinks")
    _write(repo / "elsewhere/eta/domain_layer/model.py")
    _write(repo / "elsewhere/eta/composition_root.py", "WIRED = 1\n")
    os.symlink("../elsewhere/eta", b / "application/eta")
    _write(repo / "elsewhere/real_cr.py", "WIRED = 1\n")
    os.symlink("../../elsewhere/real_cr.py", b / "application/gamma/composition_root.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "links")
    _write(repo / "elsewhere/real_cr.py", "WIRED = 2\n")  # 링크 대상만 변경
    return b


def s_gitignored_candidate(td: Path) -> Path:
    repo, b = _committed(td, "gitignored_candidate")
    _write(b / ".gitignore", "application/gamma/composition_root.py\n"
                             "application/gamma/driven_layer/idempotency_ign.py\n")
    _git(repo, "add", ".gitignore")
    _git(repo, "commit", "-qm", "ign")
    _write(b / "application/gamma/composition_root.py", "IGN = 1\n")
    _write(b / "application/gamma/driven_layer/idempotency_ign.py", "IGN = 1\n")
    _write(b / "application/gamma/domain_layer/model.py", "x = 5\n")
    return b


def s_case_change(td: Path) -> Path:
    repo, b = _committed(td, "case_change")
    _git(repo, "mv", "application/alpha/composition_root.py", "application/alpha/Composition_root.py")
    _git(repo, "commit", "-qm", "case")
    os.rename(b / "application/alpha/Composition_root.py", b / "application/alpha/composition_root.py")
    return b


def s_linked_worktree(td: Path) -> Path:
    repo, _b = _committed(td, "linked_main")
    wt: Path = td / "linked_wt"
    _git(repo, "worktree", "add", "-q", str(wt))
    _write(wt / "application/beta/domain_layer/model.py", "x = 7\n")
    _write(wt / "application/gamma/driven_layer/idempotency_wt.py", "class IdempotencyW:\n    pass\n")
    return wt


def s_staged_then_modified(td: Path) -> Path:
    repo, b = _committed(td, "staged_then_modified")
    _write(b / "application/gamma/composition_root.py", "A = 1\n")
    _git(repo, "add", "application/gamma/composition_root.py")
    _write(b / "application/gamma/composition_root.py", "A = 2\n")
    return b


def s_composition_dir(td: Path) -> Path:
    _, b = _committed(td, "composition_dir")
    _write(b / "application/gamma/composition/composition_root.py", "OFF = 1\n")
    return b


def s_idem_adopted(td: Path) -> Path:
    _, b = _committed(td, "idem_adopted")
    _write(b / "application/gamma/driven_layer/idempotency_new.py", "class IdempotencyRecord:\n    pass\n")
    _write(b / ".dddjango/20260101-x/design-spec.md", "- 멱등성 도입 — 사용자 승인(G1 결정)\n")
    return b


def _gamma_only_repo(td: Path, name: str, candidate: bool) -> Path:
    repo: Path = _fresh(td, name)
    _git(repo, "init", "-q")
    _write(repo / "application/__init__.py", "")
    _write(repo / "application/gamma/domain_layer/model.py")
    if candidate:
        _write(repo / "application/gamma/composition_root.py", "W = 1\n")
    _write(repo / ".dddjango/20260101-x/scope.md", "- 멱등성은 이번 요청에 명시되지 않았다\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo


def s_corrupt_root_tree(td: Path) -> Path:
    repo: Path = _gamma_only_repo(td, "corrupt_root_tree", candidate=False)
    _drop_object(repo, "HEAD^{tree}")
    return repo


def s_corrupt_root_tree_mixed(td: Path) -> Path:
    repo: Path = _fresh(td, "corrupt_root_tree_mixed")
    _git(repo, "init", "-q")
    _write(repo / "application/__init__.py", "")
    _write(repo / "application/gamma/domain_layer/model.py")
    _write(repo / "application/zeta/domain_layer/model.py")
    _write(repo / "application/zeta/composition_root.py", "W = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    _drop_object(repo, "HEAD^{tree}")
    return repo


def s_corrupt_subtree_nocand(td: Path) -> Path:
    repo: Path = _gamma_only_repo(td, "corrupt_subtree_nocand", candidate=False)
    _drop_object(repo, "HEAD:application/gamma")
    return repo


def s_corrupt_subtree_cand(td: Path) -> Path:
    repo: Path = _gamma_only_repo(td, "corrupt_subtree_cand", candidate=True)
    _drop_object(repo, "HEAD:application/gamma")
    return repo


def s_corrupt_subtree_staged(td: Path) -> Path:
    repo: Path = _gamma_only_repo(td, "corrupt_subtree_staged", candidate=True)
    _drop_object(repo, "HEAD:application/gamma")
    _write(repo / "application/gamma/domain_layer/fresh.py", "y = 1\n")
    _git(repo, "add", "application/gamma/domain_layer/fresh.py")  # 같은 폴더 cache-tree 무효화
    return repo


SCENARIOS: "dict[str, Callable[[Path], Path]]" = {
    name[2:]: fn for name, fn in list(globals().items()) if name.startswith("s_") and callable(fn)
}


# ── 실행·정규화 ──────────────────────────────────────────────────────────────────

def _normalize(text: str, td: Path) -> str:
    for prefix in sorted({str(td.resolve()), str(td)}, key=len, reverse=True):
        text = text.replace(prefix, "<TMP>")
    return text


def _run_call(scripts: Path, script: str, extra: "list[str]", target: Path, td: Path) -> "dict[str, object]":
    sink: Path = td / "sink.jsonl"
    sink.unlink(missing_ok=True)
    env: "dict[str, str]" = _git_env()
    env.update(DJR_FINDINGS_JSON=str(sink), PYTHONDONTWRITEBYTECODE="1")
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(
        [sys.executable, str(scripts / script), str(target), *extra],
        capture_output=True, text=True, env=env, cwd=str(td))
    records: "list[dict]" = []
    if sink.is_file():
        for raw in sink.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            rec: dict = json.loads(_normalize(raw, td))
            for key in _VOLATILE:
                rec.pop(key, None)
            records.append(rec)
    return {"exit": proc.returncode, "stdout": _normalize(proc.stdout, td),
            "stderr": _normalize(proc.stderr, td), "records": records}


def measure(scripts: Path) -> "dict[str, dict[str, object]]":
    """시나리오 × 호출 결과 — 시나리오마다 새 임시 루트(경로 정규화 단위)."""
    cases: "dict[str, dict[str, object]]" = {}
    for name, build in SCENARIOS.items():
        with tempfile.TemporaryDirectory(prefix="git-touched-") as tmp:
            td: Path = Path(tmp)
            target: Path = build(td / "w")
            for label, script, extra in CALLS:
                got: "dict[str, object]" = _run_call(scripts, script, extra, target, td)
                got["compare_stderr"] = name not in _STDERR_FREE
                cases[f"{name}/{label}"] = got
    return cases


def _scripts_from_commit(commit: str, dest: Path) -> Path:
    archive: "subprocess.CompletedProcess[bytes]" = subprocess.run(
        ["git", "-C", str(ROOT), "archive", commit, "dddjango/scripts"], capture_output=True)
    if archive.returncode != 0:
        raise RuntimeError(f"git archive {commit} 실패: {archive.stderr.decode(errors='replace').strip()}")
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
    return dest / "dddjango" / "scripts"


def _mark(same: "bool | None") -> str:
    return "—" if same is None else ("✓" if same else "✗")


def _compare(golden: "dict[str, dict]", got: "dict[str, dict]") -> int:
    print("| 시나리오/호출 | exit(골든→현행) | stdout | stderr | 레코드 | 판정 |")
    print("|---|---|---|---|---|---|")
    bad: int = 0
    for key in sorted(set(golden) | set(got)):
        want: "dict | None" = golden.get(key)
        have: "dict | None" = got.get(key)
        if want is None or have is None:
            bad += 1
            print(f"| {key} | — | — | — | — | ✗ {'골든에 없음' if want is None else '현행에 없음'} |")
            continue
        same_exit: bool = want["exit"] == have["exit"]
        same_out: bool = want["stdout"] == have["stdout"]
        same_rec: bool = want["records"] == have["records"]
        same_err: "bool | None" = (want["stderr"] == have["stderr"]) if want["compare_stderr"] else None
        ok: bool = same_exit and same_out and same_rec and same_err is not False
        bad += 0 if ok else 1
        print(f"| {key} | {want['exit']}→{have['exit']} | {_mark(same_out)} | {_mark(same_err)} | "
              f"{_mark(same_rec)}({len(have['records'])}) | {'✓' if ok else '✗ 불일치'} |")
        if not ok:
            for field in ("stdout", "stderr"):
                if want[field] != have[field]:
                    print(f"    {field} 골든: {want[field][-400:]!r}")
                    print(f"    {field} 현행: {have[field][-400:]!r}")
    print(f"케이스 {len(set(golden) | set(got))} · 일치 {len(set(golden) | set(got)) - bad} · 불일치 {bad}")
    return 0 if bad == 0 else 2


def _load_golden(path: Path) -> "tuple[dict | None, str | None]":
    """골든을 읽는다 — 출처가 커밋 SHA 가 아니면 거절한다(«옛 == 새» 보증의 근거가 커밋이다).

    `--emit` 을 `--from-commit` 없이 부르면 현행 코드 결과가 `emitted_from: "working-tree"` 로 기록된다.
    그 골든과 대조하면 red 가 «재기록 한 번»으로 사라지므로, 비교 모드는 그런 골든을 재료 결손으로 본다."""
    if not path.is_file():
        return None, f"골든 {path} 없음 — `--emit --from-commit <바꾸기 전 커밋>`"
    golden: dict = json.loads(path.read_text(encoding="utf-8"))
    if golden.get("schema") != SCHEMA:
        return None, f"골든 schema {golden.get('schema')!r} ≠ {SCHEMA!r}"
    source: object = golden.get("emitted_from")
    if not isinstance(source, str) or not _COMMIT_SHA.fullmatch(source):
        return None, (f"골든 출처 {source!r} 가 커밋 SHA 가 아니다 — 현행 코드로 뜬 골든은 «옛 == 새»를 보증하지 "
                      "못한다(`--emit --from-commit <sha>` 로 다시 뜬다)")
    return golden, None


class GoldenSourceGuard(unittest.TestCase):
    def _write(self, td: Path, payload: "dict[str, object]") -> Path:
        path: Path = td / "expected.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_rejects_golden_not_emitted_from_a_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            td: Path = Path(tmp)
            for source in ("working-tree", "HEAD", "", None):
                golden, error = _load_golden(self._write(td, {"schema": SCHEMA, "emitted_from": source, "cases": {}}))
                self.assertIsNone(golden, source)
                self.assertIn("커밋 SHA 가 아니다", error or "", source)
            golden, error = _load_golden(self._write(td, {"schema": SCHEMA, "emitted_from": "86fc3c24", "cases": {}}))
            self.assertIsNone(error)
            golden, error = _load_golden(td / "absent.json")
            self.assertIsNone(golden)
            self.assertIn("없음", error or "")

    def test_committed_golden_names_its_commit(self) -> None:
        golden, error = _load_golden(GOLDEN)
        self.assertIsNone(error, error)


def main(argv: "list[str]") -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--emit", action="store_true", help="결과를 골든(또는 --out)으로 기록")
    ap.add_argument("--from-commit", default=None, help="--emit 에서 이 커밋의 dddjango/scripts 로 돈다")
    ap.add_argument("--out", default=None, help="--emit 기록 경로(기본: 골든)")
    ap.add_argument("--scripts", default=None, help="현행 대신 이 scripts 폴더로 돈다(변이 시험용)")
    ns: argparse.Namespace = ap.parse_args(argv)
    if shutil.which("git") is None:
        print("재료 결손: git 없음", file=sys.stderr)
        return 1
    current: Path = Path(ns.scripts).resolve() if ns.scripts else SCRIPTS
    if not ns.emit:
        guard: unittest.TestResult = unittest.TextTestRunner(verbosity=1).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(GoldenSourceGuard))
        if not guard.wasSuccessful():
            return 2
        golden, error = _load_golden(GOLDEN)
        if golden is None:
            print(f"재료 결손: {error}", file=sys.stderr)
            return 1
        return _compare(golden["cases"], measure(current))
    with tempfile.TemporaryDirectory(prefix="git-touched-scripts-") as tmp:
        scripts: Path = _scripts_from_commit(ns.from_commit, Path(tmp)) if ns.from_commit else current
        payload: "dict[str, object]" = {
            "schema": SCHEMA,
            "emitted_from": ns.from_commit or "working-tree",
            "cases": measure(scripts),
        }
    out: Path = Path(ns.out) if ns.out else GOLDEN
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"기록 {out} · 케이스 {len(payload['cases'])}(scripts {payload['emitted_from']})")  # type: ignore[arg-type]
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
