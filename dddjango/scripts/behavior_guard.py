#!/usr/bin/env python3
"""동작 보존 장치(최소판) — 슬라이스 0 창의 «테스트 고정»과 «마이그레이션 무변»을 결정적으로 판정한다.

왜 있나(설계 정본: workspace/plan/2026-09-26-refactor-path-repair/step4-behavior-guard-design-v4.md · 사용자 결정 8·9):
«기존 테스트가 통과하면 동작이 보존된다»는 두 전제 — 테스트가 창 전과 같다 · 테스트가 그 동작을 덮는다 — 위에서만 참이다.
같은 레인이 코드와 테스트를 함께 고칠 수 있으므로 한 번에 한쪽만 고친다(한쪽 고정 원칙):

  0T(테스트 정리)  제품 코드 고정 — 제품 쪽 무변(루트 pytest 설정 절은 예외) · 수집 케이스 `(경로, 이름)` 다중집합 동일
                                  (G1 입장 표 `remove` 행의 owner/path 칸만 감소 허용)
  0C(코드 정리)    테스트 고정   — 테스트 `.py` 는 창 안 대응표(파일·디렉터리 이동 · 정의 이동 · 이름 대응)의 치환으로만
                                  설명돼야 한다 · 테스트 디렉터리의 비 `.py` 오라클과 pytest 설정은 무변 · 수집 케이스 이름 불변
  공통             마이그레이션 무변 — 정적 `(app_label, 파일)` 내용 해시 + 동적 `makemigrations --check` 변경 목록

비교는 이름 참조를 전체 경로(`⟨pkg.mod.Name⟩`)로 풀어서 한다 — import 로 묶인 이름 · 모듈 속성 사슬 · 패키지 재수출 한 단계.
옛 판에만 대응표를 적용하고, 대응표는 더 늘지 않을 때까지 되풀이해 만든다(구조 쌍 → 정의 대응 → 후속 모듈 → 디렉터리 대응).
이동 쌍은 분류 중립이다(옮긴 파일은 옛 분류를 유지한다). 창 안 머지는 `approved-merges.txt` 에 등재된 것만 유입으로 빼고
(두 부모와 모두 다른 경로는 레인 편집), 유입 경로를 레인도 바꿨으면 판정 불가(exit 1)다. 판정 재료는 git 과 작업 트리뿐이다
(산출은 산출물 폴더 `behavior/` · 동적 측정이 만든 미추적 파일은 지운다).

사용: behavior_guard.py open <산출물 폴더> --kind test|code|follow|change --mode refactor|feature [--repo <저장소 루트, 기본 .>]
                                [--python <인터프리터>]   — 모드는 open 기록에 동결 · 폴더 이름의 `-refactor-` 와 어긋나면 실행 불능
      behavior_guard.py close <산출물 폴더> [--repo …]     — 다음 파견 전까지 몇 번이든 다시 돌린다(마지막 판정이 유효)
      behavior_guard.py rebind <산출물 폴더> [--repo …]    — 열린 follow · change 창의 허용 표만 새 G1 변경판으로(창 기준 그대로)
      behavior_guard.py verify <산출물 폴더> [--repo …]    — G2 배너 `동작 보존:` 행(리팩토링 모드는 `바뀐 것 실행:` · `suite:` 행도)의 기계 출처
      behavior_guard.py support <산출물 폴더> --collect [--repo …] — G0 지원 확인(behavior_support)
      behavior_guard.py suite <산출물 폴더> [--repo …]     — G2 증거 실행(behavior_support)
exit 0 = green(해당 없음 · 감사 요청 포함) · 2 = red · 1 = 실행 불능(앵커 부재 · 열린 창 · 머지 겹침 · rebase 등). 모든 경로가 `요약:` 1행을 낸다.

리팩토링 모드(설계 v15.2 §4 — `follow` · `change` 창 · 처분 · 감사 키)는 시험 쪽 바이트 변화마다 감사 키를 내거나 red 다(자동 초록 0).
기능 모드는 위 0T · 0C 판정 그대로다.

알려진 사각(감수 hunk 대조 몫): 테스트만 import 하는 제품 분류 모듈(운영 CLI 와 구별 불가 — 테스트 settings·pytest 플러그인
모듈 포함) · 재수출 심을 남긴 이동의 `patch("옛.경로")` 헛돎(심만 남은 모듈은 보고) · 모듈 경로가 관찰값인 곳(로거 이름 ·
Celery 기본 태스크 이름 · pickle) · 제품 튜플로 도는 parametrize 케이스 감소와 0T parametrize 리터럴 감소 · conftest 이동으로
autouse 범위가 바뀌는 것 · `.gitignore` 된 테스트 데이터 · 0T 의 같은 이름 재작성·단언 약화 · 메서드 개명(클래스 본문이 바뀌어
red) · 믹스인이 상속한 케이스 · 동적 마이그레이션 미측정(인터프리터 없음 — open 이 미측정이면 close 도 재지 않는다).
"""
from __future__ import annotations

import argparse
import ast
import base64
import collections
import configparser
import difflib
import fnmatch
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tokenize
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, NamedTuple

EXCLUDED_PREFIXES: "tuple[str, ...]" = (".dddjango/", ".git/", ".venv/", "venv/", "node_modules/")
TEST_SEGMENTS: "frozenset[str]" = frozenset({"test", "tests"})
SUPPORT_SEGMENTS: "frozenset[str]" = frozenset({"factories", "fake", "fakes", "fixtures"})
MIGRATION_RE: "re.Pattern[str]" = re.compile(r"(?:^|/)migrations/\d{4}_[^/]+\.py$")
PYTEST_FILES: "tuple[str, ...]" = ("pyproject.toml", "pytest.ini", "setup.cfg", "tox.ini")
DEFAULT_TEST_FILES: "tuple[str, ...]" = ("test_*.py", "*_test.py")
ATTR_CALLS: "frozenset[str]" = frozenset({"getattr", "setattr", "hasattr", "delattr"})
MAX_ROUNDS: int = 8
IDENT: str = r"A-Za-z0-9_"

Reader = Callable[[str], "bytes | None"]


class RunError(Exception):
    """실행 불능(exit 1) — 판정하지 않는다."""


# ── git · 파일 ──────────────────────────────────────────────────────────────────

def _git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", *args], capture_output=True)
    if check and proc.returncode != 0:
        raise RunError(f"git {' '.join(args[:3])} 실패: {proc.stderr.decode('utf-8', 'replace').strip()[:300]}")
    return proc.stdout.decode("utf-8", "surrogateescape")


def _git_bytes(repo: Path, rev: str, path: str) -> "bytes | None":
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def _is_ancestor(repo: Path, older: str, newer: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
                          capture_output=True).returncode == 0


def _excluded(path: str) -> bool:
    return path.startswith(EXCLUDED_PREFIXES) or "/__pycache__/" in f"/{path}"


def _worktree_files(repo: Path) -> "list[str]":
    out: str = _git(repo, "ls-files", "-co", "--exclude-standard", "-z")
    return sorted(p for p in set(out.split("\0")) if p and not _excluded(p) and (repo / p).is_file())


def _untracked(repo: Path) -> "set[str]":
    return {p for p in _git(repo, "ls-files", "-o", "--exclude-standard", "-z").split("\0") if p and not _excluded(p)}


def _tree_files(repo: Path, rev: str) -> "list[str]":
    out: str = _git(repo, "ls-tree", "-r", "--name-only", "-z", rev)
    return sorted(p for p in out.split("\0") if p and not _excluded(p))


def _dirty(repo: Path) -> "list[str]":
    """HEAD 대비 작업 트리 변경 경로(수정·삭제·미추적) — `.dddjango/` 제외."""
    out: str = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    paths: "set[str]" = set()
    tokens: "list[str]" = out.split("\0")
    i: int = 0
    while i < len(tokens):
        tok: str = tokens[i]
        if len(tok) > 3:
            paths.add(tok[3:])
            if tok[0] in "RC":
                i += 1
                if i < len(tokens) and tokens[i]:
                    paths.add(tokens[i])
        i += 1
    return sorted(p for p in paths if not _excluded(p))


def _sha(data: "bytes | None") -> "str | None":
    return None if data is None else hashlib.sha256(data).hexdigest()


def _text(data: "bytes | None") -> "str | None":
    return None if data is None else data.decode("utf-8", "surrogateescape")


def _module(path: str) -> str:
    mod: str = path[:-3].replace("/", ".") if path.endswith(".py") else path.replace("/", ".")
    return mod[: -len(".__init__")] if mod.endswith(".__init__") else mod


def _parent(path: str) -> str:
    return path.rpartition("/")[0]


def _ancestors(path: str) -> "list[str]":
    parts: "list[str]" = path.split("/")[:-1]
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


# ── 분류 ────────────────────────────────────────────────────────────────────

def _test_dirs(paths: "list[str]") -> "set[str]":
    """`test_*.py` 를 품은 `test`/`tests` 디렉터리(전체 경로) — 그 아래 모든 파일이 테스트 쪽(비 `.py` 오라클 포함)."""
    marked: "set[str]" = set()
    for p in paths:
        parts: "tuple[str, ...]" = PurePosixPath(p).parts
        if not parts[-1].startswith("test_") or not parts[-1].endswith(".py"):
            continue
        for i, seg in enumerate(parts[:-1]):
            if seg in TEST_SEGMENTS:
                marked.add("/".join(parts[: i + 1]))
    return marked


def _is_test(path: str, test_dirs: "set[str]") -> bool:
    parts: "tuple[str, ...]" = PurePosixPath(path).parts
    name: str = parts[-1]
    if name.endswith(".py") and (any(s in TEST_SEGMENTS or s in SUPPORT_SEGMENTS for s in parts[:-1])
                                 or name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py"):
        return True
    return any("/".join(parts[: i + 1]) in test_dirs for i in range(len(parts) - 1))


# ── pytest 설정 · 테스트 케이스 · 마이그레이션 ────────────────────────────────────

def _pytest_config(repo: Path) -> "dict[str, str]":
    """pytest 설정 절의 정규형(원천별) — 수집 계약·settings 결합이 여기 있다."""
    out: "dict[str, str]" = {}
    pyproject: Path = repo / "pyproject.toml"
    if pyproject.is_file():
        lines: "list[str]" = pyproject.read_text(encoding="utf-8", errors="replace").splitlines()
        grab: bool = False
        body: "list[str]" = []
        for ln in lines:
            s: str = ln.strip()
            if s.startswith("["):
                grab = s.startswith("[tool.pytest")
            if grab and s and not s.startswith("#"):
                body.append(re.sub(r"\s+", " ", s))
        if body:
            out["pyproject.toml"] = "\n".join(body)
    for name, section in (("pytest.ini", "pytest"), ("setup.cfg", "tool:pytest"), ("tox.ini", "pytest")):
        f: Path = repo / name
        if not f.is_file():
            continue
        cp = configparser.ConfigParser(interpolation=None)
        try:
            cp.read(f, encoding="utf-8")
        except (configparser.Error, UnicodeError) as exc:
            out[name] = f"파싱 불가: {exc}"
            continue
        if cp.has_section(section):
            items: "list[str]" = [k + " = " + re.sub(r"\s+", " ", v.strip()) for k, v in sorted(cp.items(section))]
            out[name] = "\n".join(items)
    return out


def _outside_pytest(name: str, data: "bytes | None") -> str:
    """설정 파일에서 pytest 절을 뺀 나머지(0T 는 이 나머지가 같을 때만 설정 파일 변경을 테스트 쪽으로 본다)."""
    if name == "pytest.ini" or data is None:
        return ""
    keep: "list[str]" = []
    skip: bool = False
    for ln in data.decode("utf-8", "replace").splitlines():
        s: str = ln.strip()
        if s.startswith("["):
            sec: str = s.strip("[]").strip()
            skip = sec.startswith("tool.pytest") if name == "pyproject.toml" else sec in ("tool:pytest", "pytest")
        if not skip:
            keep.append(ln)
    return "\n".join(keep).strip()


def _outside_pytest_section(name: str, data: "bytes | None") -> str:
    """리팩토링 모드 0T 의 루트 설정 예외 — 설정 파일에서 pytest 절을 뺀 나머지. `pytest.ini` 도 `[pytest]` 절 밖을 실제로 본다
    (기능 모드 `_outside_pytest` 는 `pytest.ini` 를 통째로 pytest 절로 본다 — 그 판정은 그대로)."""
    if name != "pytest.ini" or data is None:
        return _outside_pytest(name, data)
    keep: "list[str]" = []
    skip: bool = False
    for ln in data.decode("utf-8", "replace").splitlines():
        s: str = ln.strip()
        if s.startswith("["):
            skip = s.strip("[]").strip() == "pytest"
        if not skip:
            keep.append(ln)
    return "\n".join(keep).strip()


def _config_list(config: "dict[str, str]", key: str) -> "list[str] | None":
    for text in config.values():
        m = re.search(rf"(?m)^{key}\s*=\s*(.*)$", text)
        if m:
            values: "list[str]" = re.findall(r"[^\s\"',\[\]]+", m.group(1))
            if values:
                return values
    return None


def _settings_module(config: "dict[str, str]") -> "str | None":
    for text in config.values():
        m = re.search(r"DJANGO_SETTINGS_MODULE\s*=\s*[\"']?([\w.]+)", text)
        if m:
            return m.group(1)
    return None


def _collectible(path: str, config: "dict[str, str]") -> bool:
    """pytest 가 이 경로를 수집하는가 — `python_files`(기본 test_*.py·*_test.py) ∧ `testpaths` 아래."""
    name: str = PurePosixPath(path).name
    if not name.endswith(".py"):
        return False
    if not any(fnmatch.fnmatchcase(name, pat) for pat in (_config_list(config, "python_files") or DEFAULT_TEST_FILES)):
        return False
    roots: "list[str]" = [r.strip("/") for r in (_config_list(config, "testpaths") or [])]
    return not roots or any(r in ("", ".") or path == r or path.startswith(r + "/") for r in roots)


def _name_match(name: str, patterns: "list[str]") -> bool:
    return any(fnmatch.fnmatchcase(name, p) if any(c in p for c in "*?[") else name.startswith(p) for p in patterns)


def _test_cases(source: "str | None", config: "dict[str, str]") -> "list[str]":
    """정적 테스트 케이스 이름 — `python_functions` 모듈 함수 · `python_classes` 이거나 `…TestCase` 하위 클래스의 메서드."""
    tree = _parse(source)
    if tree is None:
        return []
    fn_pats: "list[str]" = _config_list(config, "python_functions") or ["test"]
    cls_pats: "list[str]" = _config_list(config, "python_classes") or ["Test"]
    names: "list[str]" = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _name_match(node.name, fn_pats):
            names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            unit: bool = any((isinstance(b, ast.Name) and b.id.endswith("TestCase"))
                             or (isinstance(b, ast.Attribute) and b.attr.endswith("TestCase")) for b in node.bases)
            if unit or _name_match(node.name, cls_pats):
                names += [f"{node.name}::{m.name}" for m in node.body
                          if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                          and (m.name.startswith("test") if unit else _name_match(m.name, fn_pats))]
    return names


def _cases(paths: "list[str]", read: Reader, config: "dict[str, str]", is_test) -> "dict[str, list[str]]":
    out: "dict[str, list[str]]" = {}
    for p in paths:
        if is_test(p) and _collectible(p, config):
            names: "list[str]" = _test_cases(_text(read(p)), config)
            if names:
                out[p] = names
    return out


def _app_label(read: Reader, app_dir: str) -> str:
    """앱 라벨 — 같은 앱 `apps.py` 의 `label`(Assign·AnnAssign 리터럴), 없으면 앱 폴더 이름."""
    tree = _parse(_text(read(f"{app_dir}/apps.py")))
    if tree is not None:
        for node in ast.walk(tree):
            target = value = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
            elif isinstance(node, ast.AnnAssign):
                target, value = node.target, node.value
            if isinstance(target, ast.Name) and target.id == "label" and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                return value.value
    return PurePosixPath(app_dir).name


def _migrations_static(paths: "list[str]", read: Reader) -> "dict[str, list[str]]":
    """`(app_label, 파일 이름)` → [내용 해시, 경로]."""
    out: "dict[str, list[str]]" = {}
    for p in paths:
        if MIGRATION_RE.search(p):
            app_dir: str = str(PurePosixPath(p).parent.parent)
            out[f"{_app_label(read, app_dir)}/{PurePosixPath(p).name}"] = [_sha(read(p)) or "-", p]
    return out


PYTHON_OVERRIDE: "list[str]" = []


def _interpreter(repo: Path) -> "list[str] | None":
    """`--python` 이 있으면 그것, 없으면 저장소의 기존 가상환경만 쓴다(환경을 새로 만들지 않는다)."""
    if PYTHON_OVERRIDE:
        return list(PYTHON_OVERRIDE)
    for cand in (repo / ".venv" / "bin" / "python", repo / "venv" / "bin" / "python"):
        if cand.is_file():
            return [str(cand)]
    return None


def _migrations_dynamic(repo: Path, config: "dict[str, str]") -> "dict[str, object]":
    """`makemigrations --check --dry-run --skip-checks` 의 정규화 변경 목록 — 미측정은 사유와 함께(침묵 없음).

    측정이 만든 미추적 파일(sqlite 파일 등 — 이력 점검의 DB 연결)은 지운다: 장치가 자기 부작용으로 판정을 바꾸지 않게.
    """
    settings: "str | None" = _settings_module(config)
    py: "list[str] | None" = _interpreter(repo)
    if not (repo / "manage.py").is_file():
        return {"status": "미측정", "reason": "manage.py 없음"}
    if settings is None:
        return {"status": "미측정", "reason": "pytest 설정에 DJANGO_SETTINGS_MODULE 없음"}
    if py is None:
        return {"status": "미측정", "reason": "인터프리터 없음(.venv/bin/python · venv/bin/python · --python)"}
    env: "dict[str, str]" = {**os.environ, "DJANGO_SETTINGS_MODULE": settings, "PYTHONDONTWRITEBYTECODE": "1"}
    before: "set[str]" = _untracked(repo)
    try:
        proc = subprocess.run([*py, "manage.py", "makemigrations", "--check", "--dry-run", "--skip-checks"],
                              cwd=repo, env=env, capture_output=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "미측정", "reason": f"실행 실패: {exc}"[:200]}
    finally:
        created: "list[str]" = sorted(_untracked(repo) - before)
        for p in created:
            if (repo / p).is_file():
                (repo / p).unlink()
    stdout: str = proc.stdout.decode("utf-8", "replace")
    result: "dict[str, object]"
    if proc.returncode == 0 and "No changes detected" in stdout:
        result = {"status": "측정", "changes": []}
    else:
        changes: "list[str]" = []
        app: str = "?"
        for ln in stdout.splitlines():
            head = re.match(r"\s*Migrations for '([^']+)'", ln)
            if head:
                app = head.group(1)
            elif ln.strip().startswith(("- ", "+ ", "~ ")):
                changes.append(f"{app}: {ln.strip()[2:].strip()}")
        if proc.returncode == 1 and changes:
            result = {"status": "측정", "changes": sorted(changes)}
        else:
            tail: str = (proc.stderr.decode("utf-8", "replace").strip().splitlines() or ["?"])[-1]
            result = {"status": "미측정", "reason": f"exit {proc.returncode}: {tail}"[:200]}
    if created:
        result["cleaned"] = created
    return result


# ── AST 정규형 ──────────────────────────────────────────────────────────────────

def _parse(source: "str | None") -> "ast.Module | None":
    if source is None:
        return None
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None


def _strip_docstrings(tree: ast.AST) -> int:
    """모듈·클래스·함수 docstring 을 걷어낸다(판정 밖 · 보고만) — 걷은 개수."""
    removed: int = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body \
                and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) \
                and isinstance(node.body[0].value.value, str):
            node.body = node.body[1:] or [ast.Pass()]
            removed += 1
    return removed


def _def_name(node: ast.AST) -> "str | None":
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def _rename_def(node: ast.AST, name: str) -> None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        node.name = name
    elif isinstance(node, ast.Assign):
        node.targets[0].id = name  # type: ignore[attr-defined]
    elif isinstance(node, ast.AnnAssign):
        node.target.id = name  # type: ignore[attr-defined]


def _join(base: str, name: str) -> str:
    return f"{base}.{name}" if base else name


def _from_base(package: str, node: ast.ImportFrom) -> str:
    if node.level:
        base: "list[str]" = package.split(".") if package else []
        if node.level > 1:
            base = base[: -(node.level - 1)]
        return ".".join(base + ([node.module] if node.module else []))
    return node.module or ""


class Maps:
    """창 안 대응표 — 모듈(mm) · 같은 이름 정의 이동(dm) · 이름 대응(rn · 결정 9) · 파일·디렉터리 경로(fm) · 이동 쌍 · 디렉터리."""

    def __init__(self) -> None:
        self.mm: "dict[str, str]" = {}
        self.dm: "dict[str, str]" = {}
        self.rn: "dict[str, str]" = {}
        self.fm: "dict[str, str]" = {}
        self.pairs: "dict[str, str]" = {}  # 옛 경로 → 새 경로(이동 쌍 — 분류 중립)
        self.dirs: "dict[str, str]" = {}
        self.functions: "set[str]" = set()  # dm·rn 가운데 def·class 정의(후속 모듈 과반은 이것만 센다 — 상수 묶음이 끌지 않게)
        self._cache: "tuple[int, re.Pattern[str] | None, re.Pattern[str] | None] | None" = None

    def size(self) -> int:
        return sum(map(len, (self.mm, self.dm, self.rn, self.fm, self.pairs, self.dirs)))

    def pair(self, old: str, new: str) -> None:
        self.pairs[old] = new
        self.fm[old] = new
        if old.endswith(".py") and new.endswith(".py"):
            self.mm.setdefault(_module(old), _module(new))

    def add_dir(self, old: str, new: str) -> None:
        self.dirs[old] = new
        self.fm.setdefault(old, new)
        self.mm.setdefault(old.replace("/", "."), new.replace("/", "."))

    def fq(self, dotted: str) -> str:
        """최장 접두 치환 한 번(정의 → 모듈 순)."""
        parts: "list[str]" = dotted.split(".")
        for i in range(len(parts), 0, -1):
            key: str = ".".join(parts[:i])
            hit: "str | None" = self.rn.get(key) or self.dm.get(key) or self.mm.get(key)
            if hit is not None:
                return hit + "".join("." + x for x in parts[i:])
        return dotted

    def patterns(self) -> "tuple[re.Pattern[str] | None, re.Pattern[str] | None]":
        if self._cache is None or self._cache[0] != self.size():
            dotted = sorted({*self.mm, *self.dm, *self.rn}, key=len, reverse=True)
            files = sorted(self.fm, key=len, reverse=True)
            self._cache = (
                self.size(),
                re.compile(rf"(?<![{IDENT}.])(" + "|".join(map(re.escape, dotted)) + rf")(?![{IDENT}])") if dotted else None,
                re.compile(rf"(?<![{IDENT}.-])(" + "|".join(map(re.escape, files)) + rf")(?![{IDENT}-])") if files else None)
        return self._cache[1], self._cache[2]


def _sub_string(text: str, maps: Maps) -> str:
    """문자열 치환 — 전체 경로 dotted 최장 키 한 번(식별자 경계) · 파일·디렉터리 경로(경로 경계). 짧은 이름만인 문자열은 그대로."""
    dotted_re, file_re = maps.patterns()
    if dotted_re is not None:
        text = dotted_re.sub(lambda m: maps.fq(m.group(1)), text)
    if file_re is not None:
        text = file_re.sub(lambda m: maps.fm[m.group(1)], text)
    return text


class _Exports:
    """패키지 `__init__` 의 재수출(`from X import Y`) — 한 판(옛 트리 · 작업 트리)의 것."""

    def __init__(self, read: Reader, files: "set[str]") -> None:
        self.read: Reader = read
        self.files: "set[str]" = files
        self.cache: "dict[str, dict[str, str]]" = {}

    def table(self, package: str) -> "dict[str, str]":
        if package not in self.cache:
            path: str = package.replace(".", "/") + "/__init__.py"
            out: "dict[str, str]" = {}
            tree = _parse(_text(self.read(path))) if path in self.files else None
            for node in (tree.body if tree is not None else []):
                if isinstance(node, ast.ImportFrom):
                    base: str = _from_base(package, node)
                    for a in node.names:
                        if a.name != "*":
                            out[a.asname or a.name] = _join(base, a.name)
            self.cache[package] = out
        return self.cache[package]

    def resolve(self, dotted: str) -> str:
        for _ in range(4):
            parts: "list[str]" = dotted.split(".")
            for i in range(1, len(parts)):
                target: "str | None" = self.table(".".join(parts[:i])).get(parts[i])
                if target and target != ".".join(parts[: i + 1]):
                    dotted = target + "".join("." + x for x in parts[i + 1:])
                    break
            else:
                return dotted
        return dotted


def _dotted_text(node: ast.AST) -> "str | None":
    if isinstance(node, ast.Name):
        return node.id.strip("⟨⟩")
    if isinstance(node, ast.Attribute):
        head: "str | None" = _dotted_text(node.value)
        return f"{head}.{node.attr}" if head else None
    return None


class _Canon(ast.NodeTransformer):
    """이름 참조를 전체 경로로 푸는 정규형 — 옛 판(maps 있음)에는 대응표를 적용한다.

    import 로 묶인 이름과 그 속성 사슬 → `⟨전체.경로⟩` · 이 모듈의 최상위 정의 → 짧은 이름(대응표가 다른 모듈로 옮겼으면
    전체 경로) · 문자열 → 경로 치환 · 문자열 어노테이션 → 식으로 풀어서 같은 규칙 · `patch.object`/`setattr` 류의 (대상, "이름")
    → 합쳐서 한 전체 경로로.
    """

    def __init__(self, path: str, tree: ast.Module, maps: "Maps | None", exports: "_Exports | None") -> None:
        self.maps: "Maps | None" = maps
        self.exports: "_Exports | None" = exports
        self.module: str = _module(path)
        self.package: str = self.module if path.endswith("__init__.py") else self.module.rpartition(".")[0]
        self.bind: "dict[str, str]" = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.asname:
                        self.bind[a.asname] = a.name
                    else:
                        self.bind[a.name.split(".")[0]] = a.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom):
                base: str = _from_base(self.package, node)
                for a in node.names:
                    if a.name != "*":
                        self.bind[a.asname or a.name] = _join(base, a.name)
        self.own: "dict[str, tuple[str | None, str | None]]" = {}
        for node in tree.body:
            name = _def_name(node)
            if name and name not in self.bind:
                self.own[name] = self._own(name)
        self.loaded: "set[str]" = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}

    def _own(self, name: str) -> "tuple[str | None, str | None]":
        """(짧은 이름, None) 또는 (None, 옛 전체 경로 — 대응표가 다른 모듈로 옮겼다)."""
        if self.maps is None:
            return name, None
        raw: str = f"{self.module}.{name}"
        moved: str = self.maps.fq(raw)
        if moved == raw:
            return name, None
        mod, _, new_name = moved.rpartition(".")
        if mod == self.maps.fq(self.module):
            return new_name, None
        return None, raw

    def map(self, raw: str) -> str:
        resolved: str = self.exports.resolve(raw) if self.exports is not None else raw
        return self.maps.fq(resolved) if self.maps is not None else resolved

    def _fq(self, raw: str, ctx: ast.expr_context) -> ast.Name:
        node = ast.Name(id=f"⟨{self.map(raw)}⟩", ctx=ctx)
        node._raw = raw  # type: ignore[attr-defined]
        return node

    def targets(self, node: "ast.Import | ast.ImportFrom", side_effect_only: bool) -> "list[str]":
        """import 대상의 전체 경로 — side_effect_only 면 본문에서 쓰이지 않는 바인딩(부수 효과 import)만."""
        out: "list[str]" = []
        if isinstance(node, ast.Import):
            for a in node.names:
                local: str = a.asname or a.name.split(".")[0]
                if not side_effect_only or local not in self.loaded:
                    out.append(self.map(a.name))
            return out
        base: str = _from_base(self.package, node)
        for a in node.names:
            if a.name == "*":
                out.append(self.map(base) + ".*")
            elif not side_effect_only or (a.asname or a.name) not in self.loaded:
                out.append(self.map(_join(base, a.name)))
        return out

    def visit_Import(self, node: ast.Import) -> ast.AST:
        return ast.Expr(ast.Constant("IMPORT:" + repr(sorted(self.targets(node, True)))))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        return ast.Expr(ast.Constant("IMPORT:" + repr(sorted(self.targets(node, True)))))

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.bind:
            return self._fq(self.bind[node.id], node.ctx)
        rep = self.own.get(node.id)
        if rep is not None:
            short, raw = rep
            return ast.Name(id=short, ctx=node.ctx) if raw is None else self._fq(raw, node.ctx)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        chain: "list[str]" = []
        cur: ast.AST = node
        while isinstance(cur, ast.Attribute):
            chain.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            raw: "str | None" = self.bind.get(cur.id)
            if raw is None and cur.id in self.own:
                raw = self.own[cur.id][1]
            if raw is not None:
                return self._fq(raw + "".join("." + a for a in reversed(chain)), node.ctx)
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str) and self.maps is not None:
            return ast.Constant(_sub_string(node.value, self.maps))
        return node

    def _annotation(self, ann: "ast.expr | None") -> "ast.expr | None":
        if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
            try:
                return self.visit(ast.parse(ann.value, mode="eval").body)
            except (SyntaxError, ValueError, RecursionError):
                return ann
        return ann

    def visit_arg(self, node: ast.arg) -> ast.AST:
        self.generic_visit(node)
        node.annotation = self._annotation(node.annotation)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.returns = self._annotation(node.returns)
        return node

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST:
        self.generic_visit(node)
        node.annotation = self._annotation(node.annotation)  # type: ignore[assignment]
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        attr_name: "str | None" = None
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
            attr_name = node.args[1].value
        self.generic_visit(node)
        func: "str | None" = _dotted_text(node.func)
        if attr_name is None or func is None or not (func.endswith("patch.object") or func in ATTR_CALLS
                                                    or func.endswith(("monkeypatch.setattr", "monkeypatch.delattr"))):
            return node
        raw: "str | None" = getattr(node.args[0], "_raw", None)
        if raw is None:
            return node
        full: str = self.map(f"{raw}.{attr_name}")
        prefix, _, last = full.rpartition(".")
        node.args[0] = ast.Name(id=f"⟨{prefix}⟩", ctx=ast.Load())
        node.args[1] = ast.Constant(last)
        return node


def canonical(source: "str | None", path: str, maps: "Maps | None", exports: "_Exports | None") -> "dict | None":
    """{imports: 부수 효과 import 대상, body: 문장 dump, stripped: 걷은 docstring, defs/nameless: 최상위 정의 dump}."""
    tree = _parse(source)
    if tree is None:
        return None
    try:
        stripped: int = _strip_docstrings(tree)
        canon = _Canon(path, tree, maps, exports)
        imports: "set[str]" = set()
        body: "list[str]" = []
        defs: "dict[str, str]" = {}
        nameless: "dict[str, str]" = {}
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.update(canon.targets(node, True))
                continue
            name: "str | None" = _def_name(node)
            short: "str | None" = name
            if name is not None and name in canon.own and canon.own[name][1] is None:
                short = canon.own[name][0]
                _rename_def(node, short)  # type: ignore[arg-type]
            dump: str = ast.dump(canon.visit(node))
            body.append(dump)
            if name is not None and short is not None:
                defs[name] = dump
                # 이름 뺀 dump — 정의 자신의 이름(선언·짧은 자기 참조)만 비운다. 문자열 상수는 그대로다(결정 9: 이름 말고 같을 때만).
                nameless[name] = dump.replace(f"name='{short}'", "name=''", 1).replace(f"id='{short}'", "id=''")
        return {"imports": tuple(sorted(imports)), "body": tuple(body), "stripped": stripped,
                "defs": defs, "nameless": nameless}
    except (RecursionError, MemoryError):
        return None


_STR_RE: "re.Pattern[str]" = re.compile(r"""value=b?(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")""")
_FQ_RE: "re.Pattern[str]" = re.compile(r"⟨(?:[^⟩]*\.)?([^⟩.]*)⟩")


def _skeleton(canon: "dict | None") -> "str | None":
    """구조 쌍 열쇠 — 문자열을 비우고 전체 경로를 마지막 이름으로 줄인 본문(import 제외). 본문이 없으면 없음."""
    if not canon or not canon["body"]:
        return None
    text: str = _FQ_RE.sub(r"⟨\1⟩", _STR_RE.sub("value=''", "\n".join(canon["body"])))
    return hashlib.sha1(text.encode("utf-8", "surrogateescape")).hexdigest()


def _fq_tokens(canon: dict) -> "collections.Counter[str]":
    return collections.Counter(re.findall(r"⟨[^⟩]*⟩", "\n".join(canon["body"])))


def _first_difference(a: dict, b: dict) -> str:
    if a["imports"] != b["imports"]:
        gone, came = sorted(set(a["imports"]) - set(b["imports"])), sorted(set(b["imports"]) - set(a["imports"]))
        return f"부수 효과 import −{gone[:2]} +{came[:2]}"
    ta, tb = _fq_tokens(a), _fq_tokens(b)
    if ta != tb:
        return f"참조 −{sorted(ta - tb)[:2]} +{sorted(tb - ta)[:2]}"
    for i, (x, y) in enumerate(zip(a["body"], b["body"])):
        if x != y:
            return f"본문 문장 {i + 1} 이 다르다"
    return f"본문 문장 수 {len(a['body'])} → {len(b['body'])}"


# ── 대응표 ────────────────────────────────────────────────────────────────────

def _detectable(path: str, name: str, is_test) -> bool:
    """정의 대응 대상 — 테스트 케이스(test*·Test*)와 dunder 는 밖(테스트는 0C 에서 고정 · 케이스 개명은 치환이 아니다)."""
    if name.startswith("__"):
        return False
    return not (is_test(path) and (name.startswith("test") or name.startswith("Test")))


def _match_defs(maps: Maps, old_canon: "dict[str, dict | None]", new_canon: "dict[str, dict | None]", is_test) -> None:
    new_index: "dict[str, list[tuple[str, str]]]" = collections.defaultdict(list)
    new_nameless: "dict[str, list[tuple[str, str]]]" = collections.defaultdict(list)
    for q, c in new_canon.items():
        if c is None:
            continue
        for n, dump in c["defs"].items():
            if _detectable(q, n, is_test):
                new_index[dump].append((q, n))
                new_nameless[c["nameless"][n]].append((q, n))
    claimed: "set[tuple[str, str]]" = set()
    pending: "list[tuple[str, str]]" = []
    for p, c in old_canon.items():
        if c is None:
            continue
        home: str = maps.fq(_module(p))
        still: "dict | None" = new_canon.get(p)
        for n, dump in c["defs"].items():
            if not _detectable(p, n, is_test):
                continue
            raw: str = f"{_module(p)}.{n}"
            hits: "list[tuple[str, str]]" = new_index.get(dump, [])
            in_place = [h for h in hits if _module(h[0]) == home]
            if in_place:
                claimed.update(in_place)
                continue
            if raw in maps.dm or raw in maps.rn:
                claimed.update(h for h in hits if f"{_module(h[0])}.{h[1]}" in (maps.dm.get(raw), maps.rn.get(raw)))
                continue
            if len(hits) == 1:
                q, m = hits[0]
                (maps.dm if m == n else maps.rn)[raw] = f"{_module(q)}.{m}"
                claimed.add(hits[0])
                if not dump.startswith(("Assign(", "AnnAssign(")):
                    maps.functions.add(raw)
                continue
            if hits or (still is not None and n in still["defs"]):
                continue  # 모호하거나 같은 이름이 제자리에 남았다(본문 변경 — 이름 대응이 아니다)
            pending.append((raw, c["nameless"][n]))
            if not dump.startswith(("Assign(", "AnnAssign(")):
                maps.functions.add(raw)
    counts = collections.Counter(nl for _raw, nl in pending)
    for raw, nl in pending:
        cands = [h for h in new_nameless.get(nl, []) if h not in claimed]
        if counts[nl] == 1 and len(cands) == 1 and cands[0][1] != raw.rpartition(".")[2]:
            q, m = cands[0]
            maps.rn[raw] = f"{_module(q)}.{m}"
            claimed.add(cands[0])


def _map_dirs(maps: Maps, deleted: "list[str]", added: "list[str]", live_now: "set[str]") -> None:
    """디렉터리 대응 — 사라진 옛 디렉터리의 이동 쌍 과반이 가리키는 새 디렉터리 · 부모·자식 대응에서 번진다."""
    vanished: "set[str]" = {d for p in deleted for d in _ancestors(p)} - live_now
    added_dirs: "set[str]" = {d for q in added for d in _ancestors(q)}
    votes: "dict[str, collections.Counter[str]]" = collections.defaultdict(collections.Counter)
    for p, q in maps.pairs.items():
        votes[_parent(p)][_parent(q)] += 1
    for d, counter in votes.items():
        if d in vanished and d not in maps.dirs:
            target, count = counter.most_common(1)[0]
            if count * 2 > sum(counter.values()) and target != d:
                maps.add_dir(d, target)
    grown: bool = True
    while grown:
        grown = False
        for d in sorted(vanished - set(maps.dirs), key=lambda x: x.count("/")):
            parent, _, base = d.rpartition("/")
            if parent in maps.dirs and f"{maps.dirs[parent]}/{base}" in added_dirs:
                maps.add_dir(d, f"{maps.dirs[parent]}/{base}")
                grown = True
                continue
            kids = [(c, t) for c, t in maps.dirs.items() if _parent(c) == d and c.rpartition("/")[2] == t.rpartition("/")[2]]
            heads = {_parent(t) for _c, t in kids}
            if kids and len(heads) == 1:
                head: str = heads.pop()
                if head and head != d and (head in added_dirs or head in live_now):
                    maps.add_dir(d, head)
                    grown = True


def build_maps(changed: "dict[str, tuple[bytes | None, bytes | None]]", is_test, live_now: "set[str]",
               old_ex: _Exports, new_ex: _Exports) -> "tuple[Maps, dict[str, dict | None], dict[str, dict | None]]":
    """바뀐 경로의 옛/새 판에서 대응표를 만든다 — 더 늘지 않을 때까지 되풀이(유일 일치만 · 동률이면 대응 없음)."""
    maps = Maps()
    deleted: "list[str]" = sorted(p for p, (a, b) in changed.items() if a is not None and b is None)
    added: "list[str]" = sorted(p for p, (a, b) in changed.items() if a is None and b is not None)
    old_src: "dict[str, str | None]" = {p: _text(a) for p, (a, _b) in changed.items() if p.endswith(".py") and a is not None}
    new_canon: "dict[str, dict | None]" = {p: canonical(_text(b), p, None, new_ex)
                                           for p, (_a, b) in changed.items() if p.endswith(".py") and b is not None}
    by_content: "dict[bytes, list[str]]" = collections.defaultdict(list)
    for q in added:
        if not q.endswith(".py") and changed[q][1]:
            by_content[changed[q][1]].append(q)  # type: ignore[index]
    old_content = collections.Counter(changed[p][0] for p in deleted if not p.endswith(".py") and changed[p][0])
    for p in deleted:
        content = changed[p][0]
        if not p.endswith(".py") and content and old_content[content] == 1 and len(by_content.get(content, [])) == 1:
            maps.pair(p, by_content[content][0])
    old_canon: "dict[str, dict | None]" = {}
    for _round in range(MAX_ROUNDS):
        size: int = maps.size()
        old_canon = {p: canonical(s, p, maps, old_ex) for p, s in old_src.items()}
        taken: "set[str]" = set(maps.pairs.values())
        sk_new: "dict[str, list[str]]" = collections.defaultdict(list)
        for q in added:
            s = _skeleton(new_canon.get(q)) if q.endswith(".py") and q not in taken else None
            if s:
                sk_new[s].append(q)
        sk_old: "dict[str, list[str]]" = collections.defaultdict(list)
        for p in deleted:
            s = _skeleton(old_canon.get(p)) if p.endswith(".py") and p not in maps.pairs else None
            if s:
                sk_old[s].append(p)
        for s, ps in sk_old.items():
            if len(ps) == 1 and len(sk_new.get(s, [])) == 1:
                maps.pair(ps[0], sk_new[s][0])
        _match_defs(maps, old_canon, new_canon, is_test)
        successors: "dict[str, collections.Counter[str]]" = collections.defaultdict(collections.Counter)
        for key, target in {**maps.dm, **maps.rn}.items():
            if key not in maps.functions:
                continue
            successors[key.rpartition(".")[0]][target.rpartition(".")[0]] += 1
        taken = set(maps.pairs.values())
        for p in deleted:
            mod: str = _module(p)
            if p.endswith(".py") and p not in maps.pairs and mod in successors:
                target_mod: str = successors[mod].most_common(1)[0][0]
                maps.mm.setdefault(mod, target_mod)
                q = next((x for x in added if x.endswith(".py") and _module(x) == target_mod and x not in taken), None)
                if q is not None:
                    maps.pair(p, q)
                    taken.add(q)
        _map_dirs(maps, deleted, added, live_now)
        taken = set(maps.pairs.values())
        for p in deleted:
            if p not in maps.pairs and _parent(p) in maps.dirs:
                q = f"{maps.dirs[_parent(p)]}/{p.rpartition('/')[2]}"
                if q in changed and changed[q][0] is None and q not in taken:
                    maps.pair(p, q)
                    taken.add(q)
        if maps.size() == size:
            break
    else:
        old_canon = {p: canonical(s, p, maps, old_ex) for p, s in old_src.items()}
    return maps, old_canon, new_canon


# ── 창 상태 ──────────────────────────────────────────────────────────────────

def _run_value(folder: Path) -> str:
    scope: Path = folder / "refactor-scope.md"
    if not scope.is_file():
        raise RunError(f"refactor-scope.md 없음 — {scope} (G0 승인 실행 줄이 창의 실행 식별자다)")
    for ln in scope.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*실행 · G0 승인 ([^·\s]+)", ln)
        if m:
            return m.group(1)
    raise RunError("refactor-scope.md 에 실행 줄(`실행 · G0 승인 <값>`)이 없다")


def _anchor(folder: Path) -> str:
    anchor: Path = folder / "build_anchor"
    if not anchor.is_file() or not anchor.read_text(encoding="utf-8").strip():
        raise RunError("build_anchor 없음 — 창은 Phase 2 첫 파견 직전 앵커 기록 «뒤»에 연다")
    return anchor.read_text(encoding="utf-8").strip()


def _run_dir(folder: Path) -> Path:
    return folder / "behavior" / re.sub(r"[^\w.-]", "_", _run_value(folder))


def _windows(run_dir: Path) -> "list[tuple[int, dict, list[dict]]]":
    out: "list[tuple[int, dict, list[dict]]]" = []
    if not run_dir.is_dir():
        return out
    for f in sorted(run_dir.glob("w*-open.json"), key=lambda p: int(re.sub(r"\D", "", p.name.split("-")[0]) or 0)):
        n: int = int(f.name[1:].split("-")[0])
        close_f: Path = run_dir / f"w{n}-close.json"
        closes: "list[dict]" = json.loads(close_f.read_text(encoding="utf-8")) if close_f.is_file() else []
        out.append((n, json.loads(f.read_text(encoding="utf-8")), closes))
    return out


def _is_open(closes: "list[dict]") -> bool:
    """마지막 close 가 red 거나 close 가 없으면 열린 창 — 리팩토링 모드의 `audit`(red 0 · 감사 요청)은 닫힌 창이다."""
    return not closes or closes[-1].get("verdict") not in ("green", "audit")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _closable(run_dir: Path) -> "list[tuple[int, dict, list[dict]]]":
    """close · rebind 대상 — 열린 창. 리팩토링 모드의 마지막 창은 닫힌 뒤(red 0)에도 다음 창을 열기 전까지 다시 판정한다
    (감사 뒤 편집 · G1′ 뒤에 close 를 다시 돌려 키를 새로 낸다 — 설계 §4-4). 기능 모드는 열린 창만이다."""
    every = _windows(run_dir)
    windows = [w for w in every if _is_open(w[2])]
    if not windows and every and every[-1][1].get("mode") == "refactor":
        return every[-1:]
    return windows


def _dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


# ── open ─────────────────────────────────────────────────────────────────────

def cmd_open(folder: Path, repo: Path, kind: str, mode: str) -> int:
    if mode not in MODES:
        raise RunError("open 은 --mode refactor|feature 가 필요하다(모드는 open 기록에 동결된다)")
    if (mode == "refactor") != _folder_is_refactor(folder):
        raise RunError(f"모드 {mode} 와 폴더 이름 `{folder.resolve().name}` 의 `{REFACTOR_MARK}` 표지가 어긋난다")
    if kind in ("follow", "change") and mode != "refactor":
        raise RunError(f"--kind {kind} 는 리팩토링 모드 창이다(--mode refactor)")
    anchor: str = _anchor(folder)
    run_dir: Path = _run_dir(folder)
    windows = _windows(run_dir)
    for n, _o, closes in windows:
        if _is_open(closes):
            raise RunError(f"열린 창 w{n} 이 있다 — close 가 green 이 된 뒤에 새 창을 연다")
    n = (windows[-1][0] + 1) if windows else 1
    binding: "tuple[str, dict] | None" = _g1_binding(folder, repo) if kind in ("follow", "change") else None
    head: str = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()
    dirty: "list[str]" = _dirty(repo)
    files: "list[str]" = _worktree_files(repo)
    test_dirs: "set[str]" = _test_dirs(files)
    dirty_entries: "dict[str, dict]" = {}
    for p in dirty:
        data: "bytes | None" = (repo / p).read_bytes() if (repo / p).is_file() else None
        entry: "dict[str, object]" = {"sha": _sha(data)}
        # 리팩토링 모드는 창 기준선의 모든 미커밋 원문을 남긴다(시험 쪽 분류가 비 .py 로 넓다 · 감사 키의 «전»).
        if data is not None and (mode == "refactor" or p.endswith(".py") or _is_test(p, test_dirs) or p in PYTEST_FILES):
            entry["b64"] = base64.b64encode(data).decode("ascii")
        dirty_entries[p] = entry
    read = lambda q: (repo / q).read_bytes() if (repo / q).is_file() else None  # noqa: E731
    config: "dict[str, str]" = _pytest_config(repo)
    cases: "dict[str, list[str]]" = _cases(files, read, config, lambda q: _is_test(q, test_dirs))
    static = _migrations_static(files, read)
    dynamic = _migrations_dynamic(repo, config)
    record: "dict[str, object]" = {
        "window": n, "kind": kind, "run": _run_value(folder), "anchor": anchor, "head": head, "opened": _now(),
        "dirty": dirty_entries, "cases": cases, "pytest": config,
        "migrations_static": static, "migrations_dynamic": dynamic, "mode": mode,
    }
    if binding is not None:
        record.update({"g1_digest": binding[0], "allow": binding[1], "rebinds": []})
    run_dir.mkdir(parents=True, exist_ok=True)
    _dump(run_dir / f"w{n}-open.json", record)
    dyn: str = (f"동적 기준 {len(dynamic['changes'])}건" if dynamic["status"] == "측정"  # type: ignore[arg-type]
                else f"동적 미측정({dynamic.get('reason')})")
    n_cases: int = sum(map(len, cases.values()))
    warn: str = " · 경고: 테스트 파일은 있는데 수집 케이스 0" if not n_cases and any(
        _is_test(p, test_dirs) and p.endswith(".py") for p in files) else ""
    tail: str = ""
    if mode == "refactor":
        tail = " · 모드 리팩토링" + (f" · G1 digest {binding[0]}" if binding is not None else "") + \
            f" · open 기록 {run_dir / f'w{n}-open.json'}"   # 받은 폴더 인자에 이어 붙인 꼴(절대화 안 함 — `changes --baseline` 에 그대로)
    print(f"요약: 창 w{n} open · 종류 {KIND_LABELS[kind]} · HEAD {head[:12]} · dirty {len(dirty)} · "
          f"수집 테스트 {len(cases)}파일 · 케이스 {n_cases} · 마이그레이션 정적 {len(static)} · {dyn}{warn}{tail}")
    return 0


# ── close ────────────────────────────────────────────────────────────────────

def _approved_merges(repo: Path, folder: Path) -> "set[str]":
    """발주자 승인 머지 목록(`approved-merges.txt` — `<SHA> [메모]` · `//` 주석)의 전체 SHA."""
    listed: Path = folder / "approved-merges.txt"
    out: "set[str]" = set()
    if not listed.is_file():
        return out
    for raw in listed.read_text(encoding="utf-8").splitlines():
        token: str = raw.strip().partition(" ")[0]
        if token and not token.startswith("//") and re.fullmatch(r"[0-9a-fA-F]{7,40}", token):
            sha: str = _git(repo, "rev-parse", "--verify", "-q", f"{token}^{{commit}}", check=False).strip()
            if sha:
                out.add(sha)
    return out


def _diff_names(repo: Path, a: str, b: str) -> "set[str]":
    return {p for p in _git(repo, "diff", "--no-renames", "--name-only", "-z", a, b).split("\0") if p}


def _merge_paths(repo: Path, folder: Path, head0: str) -> "tuple[set[str], set[str], list[str]]":
    """창 안 first-parent 사슬의 승인 머지가 들여온 경로 · 레인 편집 경로 · 미승인 머지(레인 편집으로 판정).

    승인 머지 M(부모 P1 · P2)의 유입 = `P1..M` 가운데 상류가 바꾼 경로(`merge-base(P1,P2)..P2`). 그 경로를 레인도 바꿨으면
    유입에 넣어 겹침(판정 불가)으로 올린다. 레인이 안 바꿨는데 M 이 P2 와도 다르면 끼운 편집이라 레인 편집이다.
    상류가 안 바꾼 경로의 `P1..M` 변화(끼운 편집 · 충돌 해소)도 레인 편집이다. 미승인 머지는 들여온 경로 전부가 레인 편집이다.
    """
    approved: "set[str]" = _approved_merges(repo, folder)
    merged: "set[str]" = set()
    lane: "set[str]" = set(_dirty(repo))
    unapproved: "list[str]" = []
    merges: "list[tuple[str, list[str], set[str]]]" = []
    for sha in _git(repo, "rev-list", "--first-parent", f"{head0}..HEAD").split():
        parents: "list[str]" = _git(repo, "rev-list", "--parents", "-n", "1", sha).split()[1:]
        from_lane: "set[str]" = _diff_names(repo, parents[0], sha)
        if len(parents) == 2 and sha in approved:
            merges.append((sha, parents, from_lane))
            continue
        if len(parents) > 1:
            unapproved.append(sha[:12])
        lane |= from_lane
    for sha, (p1, p2), from_lane in merges:
        base: str = _git(repo, "merge-base", p1, p2).strip()
        upstream: "set[str]" = from_lane & _diff_names(repo, base, p2)
        inserted: "set[str]" = (upstream - lane) & _diff_names(repo, p2, sha)
        merged |= upstream - inserted
        lane |= (from_lane - upstream) | inserted
    return merged, lane, unapproved


def _compare_py(p: str, target: str, maps: Maps, old_canon: dict, new_canon: dict) -> "tuple[str, str]":
    """(판정 green|red|note, 사유) — 옛 판(대응표 적용)과 새 판의 정규형 비교."""
    before, after = old_canon.get(p), new_canon.get(target)
    if before is None or after is None:
        return "red", f"{target} — 파싱 불가(판정 불능은 red)"
    if (before["imports"], before["body"]) != (after["imports"], after["body"]):
        return "red", f"{target} — 치환으로 설명되지 않는 변경: {_first_difference(before, after)}"
    if before["stripped"] != after["stripped"]:
        return "note", f"{target} — docstring 변경(판정 밖 · 보고)"
    return "green", ""


def _compare_bytes(a: bytes, b: bytes, maps: Maps) -> bool:
    if a == b:
        return True
    try:
        return _sub_string(a.decode("utf-8"), maps) == b.decode("utf-8")
    except UnicodeDecodeError:
        return False


def cmd_close(folder: Path, repo: Path) -> int:
    _anchor(folder)
    run_dir: Path = _run_dir(folder)
    windows = _closable(run_dir)
    if not windows:
        raise RunError("열린 창이 없다 — open 뒤에 close 한다")
    n, opened, closes = windows[-1]
    if _window_mode(folder, opened) == "refactor":
        return _close_refactor(folder, repo, run_dir, n, opened, closes)
    head0: str = opened["head"]
    kind: str = opened["kind"]
    head: str = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()
    if not _is_ancestor(repo, head0, head):
        raise RunError(f"판정 불가(창 기준 {head0[:12]} 이 HEAD 의 조상이 아니다 — rebase·reset 뒤에는 철회하거나 STOP 한다)")
    merged, lane, unapproved = _merge_paths(repo, folder, head0)
    overlap: "set[str]" = merged & lane
    if overlap:
        raise RunError("판정 불가(머지 겹침) — 승인 머지가 들여온 경로를 레인도 바꿨다: " + ", ".join(sorted(overlap)[:5]))
    dirty0: "dict[str, dict]" = opened["dirty"]

    def read_then(p: str) -> "bytes | None":
        if p in dirty0:
            b64 = dirty0[p].get("b64")
            return base64.b64decode(b64) if b64 is not None else None
        return _git_bytes(repo, head0, p)

    def sha_then(p: str) -> "str | None":
        return dirty0[p]["sha"] if p in dirty0 else _sha(_git_bytes(repo, head0, p))

    def read_now(p: str) -> "bytes | None":
        return (repo / p).read_bytes() if (repo / p).is_file() else None

    files_now: "list[str]" = _worktree_files(repo)
    files_then: "list[str]" = sorted((set(_tree_files(repo, head0)) | {p for p, e in dirty0.items() if e["sha"]})
                                     - {p for p, e in dirty0.items() if not e["sha"]})
    test_dirs: "set[str]" = _test_dirs(files_now) | _test_dirs(files_then)
    is_test = lambda p: _is_test(p, test_dirs)  # noqa: E731
    candidates: "set[str]" = (_diff_names(repo, head0, "HEAD") | _git_worktree_changes(repo, head0)
                              | set(_dirty(repo)) | set(dirty0))
    changed: "dict[str, tuple[bytes | None, bytes | None]]" = {}
    for p in sorted(candidates - merged):
        if _excluded(p):
            continue
        now: "bytes | None" = read_now(p)
        if _sha(now) != sha_then(p):
            changed[p] = (read_then(p), now)
    live_now: "set[str]" = {d for p in files_now for d in _ancestors(p)}
    maps, old_canon, new_canon = build_maps(changed, is_test, live_now, _Exports(read_then, set(files_then)),
                                            _Exports(read_now, set(files_now)))
    pair_targets: "set[str]" = set(maps.pairs.values())
    cfg_then: "dict[str, str]" = {k: v for k, v in opened["pytest"].items() if k not in merged}
    cfg_now_all: "dict[str, str]" = _pytest_config(repo)
    cfg_now: "dict[str, str]" = {k: v for k, v in cfg_now_all.items() if k not in merged}
    reds: "list[str]" = []
    notes: "list[str]" = [f"미승인 머지 {s} — 들여온 경로를 레인 편집으로 판정(approved-merges.txt 밖)" for s in unapproved]
    green_files: "list[str]" = []
    cases_then: "dict[str, list[str]]" = {p: v for p, v in opened["cases"].items() if p not in merged}
    cases_now: "dict[str, list[str]]" = {p: v for p, v in _cases(files_now, read_now, cfg_now_all, is_test).items()
                                         if p not in merged}
    if kind == "code":
        for p, (a, b) in sorted(changed.items()):
            if not is_test(p) or p in pair_targets:
                continue
            if b is None and p in maps.pairs:
                target: str = maps.pairs[p]
                new_b: "bytes | None" = changed[target][1] if target in changed else read_now(target)
            elif a is None:
                if not (_text(b) or "").strip():
                    notes.append(f"{p} — 빈 파일 추가(패키지 골격 · 판정 밖)")
                else:
                    reds.append(f"{p} — 테스트 파일 추가(0C 는 테스트 고정 — 새 테스트는 별도 슬라이스)")
                continue
            elif b is None:
                if not (_text(a) or "").strip():
                    notes.append(f"{p} — 빈 파일 삭제(패키지 골격 · 판정 밖)")
                else:
                    reds.append(f"{p} — 테스트 파일 삭제(이동 쌍 없음)")
                continue
            else:
                target, new_b = p, b
            if _collectible(p, opened["pytest"]) and not _collectible(target, cfg_now_all):
                reds.append(f"{p} → {target} — 테스트 파일이 수집 밖으로 옮겨졌다(python_files·testpaths)")
                continue
            if p.endswith(".py"):
                verdict, why = _compare_py(p, target, maps, old_canon, new_canon)
                if verdict == "red":
                    reds.append(why)
                    continue
                if verdict == "note":
                    notes.append(why)
                green_files.append(target)
            elif new_b is not None and _compare_bytes(a or b"", new_b, maps):
                green_files.append(target)  # 경로 치환만 있는 비 .py 테스트 파일(스크립트 경로 문자열 등) · 같은 내용 이동
            else:
                reds.append(f"{target} — 테스트 디렉터리의 비 .py 오라클 변경(golden·fixture 데이터는 0C 에서 고정)")
        if cfg_then != cfg_now:
            reds.append("pytest 설정 변경(수집 계약·settings 결합은 0C 에서 고정)")
        names_then = collections.Counter(x for v in cases_then.values() for x in v)
        names_now = collections.Counter(x for v in cases_now.values() for x in v)
        if names_then != names_now:
            gone, came = sorted((names_then - names_now).elements()), sorted((names_now - names_then).elements())
            reds.append(f"수집 테스트 케이스 변화 −{len(gone)} {gone[:3]} +{len(came)} {came[:3]}(0C 는 테스트 고정)")
    else:
        for p, (a, b) in sorted(changed.items()):
            if is_test(p) or p in pair_targets:
                continue  # 테스트 쪽 편집은 0T 의 일 · 이동 쌍의 새 자리는 옛 분류를 따른다(분류 중립)
            if p in PYTEST_FILES and _outside_pytest(p, a) == _outside_pytest(p, b):
                notes.append(f"{p} — pytest 설정 절 변경(0T 허용 · testpaths·python_files·addopts 변경은 감수 hunk 대조)")
                continue
            reds.append(f"{p} — 제품 쪽 변경(0T 는 제품 코드 고정)")
        before_c = collections.Counter(f"{maps.pairs.get(p, p)}::{x}" for p, v in cases_then.items() for x in v)
        after_c = collections.Counter(f"{p}::{x}" for p, v in cases_now.items() for x in v)
        allowed: "collections.Counter[str]" = _removed_cases(folder)
        for key, count in ((before_c - after_c) - allowed).items():
            reds.append(f"테스트 케이스 감소 `{key}` ×{count}(G1 입장 표 remove 행 owner/path 밖)")
        for key, count in (after_c - before_c).items():
            reds.append(f"테스트 케이스 추가 `{key}` ×{count}(0T 는 새 case 없이 — 재조직 규범)")
    static_then: "dict[str, list[str]]" = opened["migrations_static"]
    static_now = _migrations_static(files_now, read_now)
    for key in sorted(set(static_then) | set(static_now)):
        then, now_ = static_then.get(key), static_now.get(key)
        if (then or [None])[0] == (now_ or [None])[0] or (then and then[1] in merged) or (now_ and now_[1] in merged):
            continue
        if kind == "code" and then and now_:
            before = canonical(_text(read_then(then[1])), then[1], maps, None)
            after = canonical(_text(read_now(now_[1])), now_[1], None, None)
            if before and after and (before["imports"], before["body"]) == (after["imports"], after["body"]):
                notes.append(f"마이그레이션 `{key}` — 옮긴 코드를 따라간 경로 치환만(판정 밖)")
                continue
        state = "추가" if then is None else "삭제" if now_ is None else "수정"
        reds.append(f"마이그레이션 {state} `{key}`(정적 — 리팩터는 스키마 이력을 바꾸지 않는다)")
    dyn_then: "dict[str, object]" = opened["migrations_dynamic"]
    dyn_note: str
    if dyn_then["status"] != "측정":
        dyn_note = f"동적 미측정(open 미측정 — close 도 재지 않는다: {dyn_then.get('reason')})"
        notes.append(dyn_note)
    else:
        dyn_now = _migrations_dynamic(repo, cfg_now_all)
        if dyn_now.get("cleaned"):
            notes.append(f"동적 측정이 만든 미추적 파일 제거: {', '.join(dyn_now['cleaned'][:3])}")  # type: ignore[index]
        if dyn_now["status"] == "측정":
            extra = sorted(set(dyn_now["changes"]) - set(dyn_then["changes"]))  # type: ignore[arg-type]
            lost = sorted(set(dyn_then["changes"]) - set(dyn_now["changes"]))  # type: ignore[arg-type]
            for c in extra:
                reds.append(f"마이그레이션 변경 생김 `{c}`(동적 — 모델 상태가 마이그레이션과 어긋났다)")
            for c in lost:
                reds.append(f"마이그레이션 변경 사라짐 `{c}`(동적 — 창 안에서 모델 상태가 바뀌었다)")
            dyn_note = "동적 무변" if not extra and not lost else "동적 red"
        else:
            reds.append(f"마이그레이션 동적 측정 실패(open 은 측정됐다 — {dyn_now.get('reason')})")
            dyn_note = "동적 red(측정 실패)"
    for old_mod in sorted(maps.mm):
        old_path: str = old_mod.replace(".", "/") + ".py"
        if old_path in changed and changed[old_path][1] is not None:
            tree = _parse(_text(changed[old_path][1]))
            if tree is not None and all(isinstance(nd, (ast.Import, ast.ImportFrom)) for nd in tree.body):
                notes.append(f"{old_path} — 재수출만 남은 모듈(patch(\"{old_mod}.…\") 는 헛돈다 — 사각)")
    verdict: str = "red" if reds else "green"
    closes.append({"closed": _now(), "verdict": verdict, "range": f"{head0}..{head}", "reds": reds, "notes": notes,
                   "green_files": sorted(green_files), "merged_excluded": sorted(merged),
                   "maps": {"pairs": len(maps.pairs), "dirs": len(maps.dirs), "modules": len(maps.mm),
                            "definitions": len(maps.dm), "renames": len(maps.rn)},
                   # 대응 원소(옛 경로 → 새 경로) — 리팩토링 모드 G2 잔존 판정·5번 감사가 옮긴 자리를 읽는다.
                   "map_items": {"pairs": dict(sorted(maps.pairs.items())), "dirs": dict(sorted(maps.dirs.items())),
                                 "fm": dict(sorted(maps.fm.items()))}})
    _dump(run_dir / f"w{n}-close.json", closes)
    for r in reds:
        print(f"  red: {r}")
    for note in notes:
        print(f"  보고: {note}")
    label: str = "0T" if kind == "test" else "0C"
    print(f"요약: 창 w{n} close {'green' if not reds else f'red {len(reds)}건'} · 종류 {label} · 바뀐 경로 {len(changed)} · "
          f"치환 green {len(green_files)} · 대응(쌍 {len(maps.pairs)} · 디렉터리 {len(maps.dirs)} · 모듈 {len(maps.mm)} · "
          f"정의 {len(maps.dm)} · 개명 {len(maps.rn)}) · "
          f"마이그레이션 정적 {'무변' if not any('정적' in r for r in reds) else 'red'} · {dyn_note} · "
          f"머지 제외 {len(merged)}경로 · 판정 {len(closes)}회째")
    return 2 if reds else 0


def _git_worktree_changes(repo: Path, head0: str) -> "set[str]":
    """작업 트리 대 창 기준 커밋의 경로(추적 파일)."""
    return {p for p in _git(repo, "diff", "--no-renames", "--name-only", "-z", head0).split("\0") if p}


def _removed_cases(folder: Path) -> "collections.Counter[str]":
    """G1 입장 표 `remove` 행의 owner/path 칸(마지막 칸) `경로::케이스` — 0T 에서 빠질 수 있는 유일한 케이스.

    대체 보장으로 인용된 coverage 칸의 테스트는 허용 목록에 넣지 않는다.
    """
    spec: Path = folder / "design-spec.md"
    out: "collections.Counter[str]" = collections.Counter()
    if not spec.is_file():
        return out
    for ln in spec.read_text(encoding="utf-8").splitlines():
        if not ln.lstrip().startswith("|"):
            continue
        cells: "list[str]" = [c.strip().strip("`").strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2 or "remove" not in cells[:-1]:
            continue
        for m in re.finditer(r"([\w./-]+\.py)::([\w:]+)", cells[-1]):
            out[f"{m.group(1)}::{m.group(2)}"] += 1
    return out


# ── 리팩토링 모드: 분류 · 감사 단위 · D · 처분(설계 v15.2 §4-1 ~ §4-4) ──────────────────────────
#
# 리팩토링 모드의 모든 창(test · code · follow · change)에서 시험 쪽 바이트 변화는 감사 키를 내거나 red 다(자동 초록 없음).
# 처분은 창마다 우선순위 하나(§4-3) · 감사 키는 원문 줄 분할과 배치 결속(§4-4) · D 는 원문 AST 만(§4-2).
# 아래 공개 함수(audit_split · audit_join · audit_keys · d_changes · dispose_test_file · judge_test_side)는 바이트 · 경로 ·
# 읽기 함수만 받는다 — 저장소 밖(과거 커밋 재생 · 역변환 속성 시험)에서도 그대로 부른다.

REFACTOR_MARK: str = "-refactor-"
MODES: "tuple[str, ...]" = ("refactor", "feature")
KINDS: "tuple[str, ...]" = ("test", "code", "follow", "change")
KIND_LABELS: "dict[str, str]" = {"test": "0T", "code": "0C", "follow": "0F", "change": "변경"}
NO_FILE: str = "없음"
BUNDLE_AUDIT: str = "묶음 감사"
SINGLE_AUDIT: str = "개별 감사"
APPROVED_AUDIT: str = "승인 변경 감사"
RED: str = "red"
MEANING_SAME: str = "기대 의미 그대로"
APPROVED_SAME: str = "승인 후와 같음"
AUDIT_VERDICTS: "tuple[str, ...]" = (MEANING_SAME, APPROVED_SAME, "다름")
MIGRATION_OPS: "frozenset[str]" = frozenset({
    "CreateModel", "DeleteModel", "RenameModel", "AlterModelTable", "AlterModelOptions", "AlterModelManagers",
    "AddField", "RemoveField", "AlterField", "RenameField", "AddIndex", "RemoveIndex", "RenameIndex",
    "AddConstraint", "RemoveConstraint", "AlterUniqueTogether", "AlterIndexTogether"})
FOLLOW_OUTSIDE_KINDS: "frozenset[str]" = frozenset({"프로젝트 합성", "공유 표면"})
D_FIXED: "frozenset[str]" = frozenset({"확정 변화", "확정 변화(지역 정의)", "삭제", "추가"})
D_KINDS: "tuple[str, ...]" = ("기대식", "맥락만", "지역 정의", "추가", "삭제", "공유 정의 변화")
SPOT_LIMIT: int = 300
_MOCK_ASSERT: "re.Pattern[str]" = re.compile(r"^assert_(called|not_called|has_calls|any_call|awaited|not_awaited)")
_EXPR_PART: "re.Pattern[str]" = re.compile(r"^(.*?)#?((?:cmp|bare|raises|except|mock|param):.*)$", re.S)
_LINE_BYTES: "re.Pattern[bytes]" = re.compile(rb"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z")   # ast 와 같은 줄 끝만
_LINE_TEXT: "re.Pattern[str]" = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z")


def _folder_is_refactor(folder: Path) -> bool:
    return REFACTOR_MARK in folder.resolve().name


def _window_mode(folder: Path, opened: dict) -> str:
    """창의 동결 모드 — 모드 칸 없는 옛 기록은 `-refactor-` 없는 폴더에서만 기능 모드로 읽는다(있으면 실행 불능)."""
    mode: "str | None" = opened.get("mode")
    refactor_folder: bool = _folder_is_refactor(folder)
    if mode is None:
        if refactor_folder:
            raise RunError(f"창 w{opened.get('window')} open 기록에 모드 칸이 없다 — 리팩토링 폴더의 옛 창은 이 판으로 판정하지 "
                           "않는다(새 실행으로 다시 연다)")
        return "feature"
    if mode not in MODES or (mode == "refactor") != refactor_folder:
        raise RunError(f"창 w{opened.get('window')} 모드 {mode} 와 폴더 이름의 `{REFACTOR_MARK}` 표지가 어긋난다")
    return mode


def _is_test_refactor(path: str, test_dirs: "set[str]") -> bool:
    """리팩토링 모드 시험 쪽(설계 §4-1 · v6) — 지금 `_is_test` ∪ 경로 조각이 여섯(test · tests · factories · fake · fakes ·
    fixtures) 가운데 하나인 비 `.py`(인정 경로의 시험 자료). 기능 모드 분류(`_is_test`)는 그대로다."""
    if _is_test(path, test_dirs):
        return True
    return any(s in TEST_SEGMENTS or s in SUPPORT_SEGMENTS for s in PurePosixPath(path).parts[:-1])


def _digest(data: "bytes | None") -> str:
    """감사 키 digest — sha256 앞 12자 · 파일(단위) 없음은 `없음`(빈 파일 `e3b0c44298fc` 와 가른다)."""
    return NO_FILE if data is None else hashlib.sha256(data).hexdigest()[:12]


def _canon_json(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8", "surrogateescape")


def _py_source(data: "bytes | None") -> "str | None":
    """PEP 263 표지를 따른 원문(ast 의 열 위치와 같은 판) — 못 풀면 None."""
    if data is None:
        return None
    try:
        encoding, _first = tokenize.detect_encoding(io.BytesIO(data).readline)
        return data.decode(encoding)
    except (SyntaxError, LookupError, UnicodeDecodeError):
        return None


def _span(text: str, line1: int, col1: int, line2: int, col2: int) -> str:
    """ast 위치(줄 1 기반 · 열 = 그 줄 UTF-8 바이트) 사이 원문 — 줄은 ast 와 같은 줄 끝으로만 나눈다."""
    lines: "list[bytes]" = [ln.encode("utf-8", "surrogateescape") for ln in _LINE_TEXT.findall(text)]
    if not lines or line1 > len(lines):
        return ""
    if line1 == line2:
        return lines[line1 - 1][col1:col2].decode("utf-8", "replace")
    chunk: "list[bytes]" = [lines[line1 - 1][col1:], *lines[line1:line2 - 1]]
    if line2 <= len(lines):
        chunk.append(lines[line2 - 1][:col2])
    return b"".join(chunk).decode("utf-8", "replace")


class AuditSplit(NamedTuple):
    """감사 단위 분할(§4-4) — 최상위 정의 원문(decorator 줄부터) · `<module>` 배열(정의 밖 줄 + 정의 자리 표시) · 배치 서열."""
    defs: "dict[str, bytes]"
    module: "list[str | dict[str, str]]"
    layout: "list[str]"


def audit_split(data: bytes) -> "tuple[AuditSplit | None, str]":
    """(분할, `<file>` 갈래) — 파싱 불가 · 같은 이름 최상위 정의 둘 이상이면 (None, 갈래)."""
    text: "str | None" = _py_source(data)
    tree = _parse(text)
    if tree is None or text is None:
        return None, "파싱 불가"
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    names: "list[str]" = [n.name for n in nodes]
    if len(names) != len(set(names)):
        return None, "같은 이름 최상위 정의가 둘 이상"
    lines: "list[bytes]" = _LINE_BYTES.findall(data)
    defs: "dict[str, bytes]" = {}
    starts: "dict[int, str]" = {}
    covered: "set[int]" = set()
    for node in nodes:
        start: int = min([node.lineno] + [d.lineno for d in node.decorator_list])
        end: int = node.end_lineno or node.lineno
        defs[node.name] = b"".join(lines[start - 1:end])
        starts[start] = node.name
        covered.update(range(start, end + 1))
    module: "list[str | dict[str, str]]" = []
    for no, line in enumerate(lines, 1):
        if no in starts:
            module.append({"정의": starts[no]})
        if no not in covered:
            module.append(line.decode("utf-8", "surrogateescape"))
    layout: "list[str]" = []
    seen: "collections.Counter[str]" = collections.Counter()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            layout.append("def:" + node.name)
            continue
        segment: str = ast.get_source_segment(text, node) or ast.dump(node)
        seen[segment] += 1
        layout.append(f"stmt:{segment}#{seen[segment]}")
    return AuditSplit(defs, module, layout), ""


def audit_join(split: AuditSplit) -> bytes:
    """역변환 — `<module>` 배열의 정의 자리 표시를 단위 원문으로 바꿔 이은 바이트(배치 결속: 원래 파일과 같다)."""
    return b"".join(split.defs[part["정의"]] if isinstance(part, dict) else part.encode("utf-8", "surrogateescape")
                    for part in split.module)


def _unit_bytes(split: AuditSplit) -> "dict[str, bytes]":
    out: "dict[str, bytes]" = dict(split.defs)
    out["<module>"] = _canon_json(split.module)
    return out


def _order_changed(before: "list[str]", after: "list[str]") -> bool:
    common: "set[str]" = set(before) & set(after)
    return [x for x in before if x in common] != [x for x in after if x in common]


def audit_keys(a: "bytes | None", b: "bytes | None", py: bool) -> "tuple[list[tuple[str, str, str]], str]":
    """([(단위, 전 digest, 후 digest)], `<file>` 갈래) — 바이트가 같으면 빈 목록. `<file>` 갈래(§4-4): 같은 이름 최상위 정의 둘
    이상 · 파싱 불가 · 비 .py · 새 파일 · 짝 없는 삭제 · 배치 순서 변화 · 바뀐 단위 0(지킴 줄). 바이트 그대로 옮긴 파일은 처분이 정한다."""
    if a == b:
        return [], ""
    whole: "list[tuple[str, str, str]]" = [("<file>", _digest(a), _digest(b))]
    if a is None or b is None:
        return whole, "새 파일 · 짝 없는 삭제(§4-3)"
    if not py:
        return whole, "비 `.py`"
    split_a, why_a = audit_split(a)
    split_b, why_b = audit_split(b)
    if split_a is None or split_b is None:
        return whole, why_a or why_b
    if _order_changed(split_a.layout, split_b.layout):
        return whole, "배치 순서 변화"
    units_a, units_b = _unit_bytes(split_a), _unit_bytes(split_b)
    names: "list[str]" = [k for k in sorted(set(units_a) | set(units_b)) if units_a.get(k) != units_b.get(k)]
    if not names:
        return whole, "바이트는 바뀌었는데 바뀐 단위가 0 — 배치 결속 뒤로는 도달하지 않는 지킴 줄"
    return [(k, _digest(units_a.get(k)), _digest(units_b.get(k))) for k in names], ""


# D — 확정 기대 변화와 공유 정의 변화(§4-2 · 원문 AST 만 · 정규화 · 대응표 없음)

def _dump_node(node: "ast.AST | None") -> str:
    return "" if node is None else ast.dump(node, annotate_fields=False, include_attributes=False)


def _names_in(node: "ast.AST | None") -> "set[str]":
    return {x.id for x in ast.walk(node) if isinstance(x, ast.Name)} if node is not None else set()


def _is_raises(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("raises", "warns") \
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytest"


class DElement(NamedTuple):
    """D 원소 — 키 `(감싼 제어 흐름 머리)#(종류 · 기대 쪽 식)` · 확정(지역) 정의 · 공유 정의 · 노드 · 함수 이름(발생 순번 뺌)."""
    key: str
    fixed: str
    shared: str
    node: ast.AST
    func: str


class DChange(NamedTuple):
    """D 변화 — 상태(확정 변화 · 확정 변화(지역 정의) · 공유 정의 변화 · 삭제 · 추가)와 사유 갈래(D_KINDS)."""
    func: str
    state: str
    kind: str
    old: "DElement | None"
    new: "DElement | None"


class _DModule:
    """D 의 모듈 — 모듈 대입(공유 정의) · 함수(최상위 · 클래스 메서드 · 중첩 클래스 메서드 `바깥.안.메서드`)를 발생 순번
    `이름#k` 로 둔다(§4-2 같은 이름 정의 · «시험 쪽 모든 함수 — 중첩»). 함수 안 중첩 함수 · 클래스는 그 함수의 원소다."""

    def __init__(self, tree: ast.Module) -> None:
        self.mod_defs: "dict[str, list[str]]" = {}
        self.funcs: "dict[str, tuple[str, ast.AST]]" = {}
        seen: "collections.Counter[str]" = collections.Counter()
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and getattr(node, "value", None) is not None:
                for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                    for name in _names_in(target):
                        self.mod_defs.setdefault(name, []).append(_dump_node(node.value))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add(node.name, node, seen)
            elif isinstance(node, ast.ClassDef):
                self._add_class(node.name, node, seen)

    def _add_class(self, prefix: str, node: ast.ClassDef, seen: "collections.Counter[str]") -> None:
        for member in node.body:
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add(f"{prefix}.{member.name}", member, seen)
            elif isinstance(member, ast.ClassDef):
                self._add_class(f"{prefix}.{member.name}", member, seen)

    def _add(self, name: str, node: ast.AST, seen: "collections.Counter[str]") -> None:
        seen[name] += 1
        self.funcs[f"{name}#{seen[name]}"] = (name, node)

    def returns_of(self, name: str) -> "list[str]":
        return [_dump_node(r.value) for base, fn in self.funcs.values() if base == name
                for r in ast.walk(fn) if isinstance(r, ast.Return)]


def _d_parents(fn: ast.AST) -> "dict[int, ast.AST]":
    out: "dict[int, ast.AST]" = {}
    for parent in ast.walk(fn):
        for child in ast.iter_child_nodes(parent):
            out[id(child)] = parent
    return out


def _d_context(node: ast.AST, parents: "dict[int, ast.AST]", fn: ast.AST) -> "tuple[str, list[ast.AST]]":
    chain: "list[str]" = []
    loops: "list[ast.AST]" = []
    cur: "ast.AST | None" = parents.get(id(node))
    while cur is not None and cur is not fn:
        if isinstance(cur, ast.If):
            chain.append("if:" + _dump_node(cur.test))
        elif isinstance(cur, (ast.For, ast.AsyncFor)):
            chain.append("for:" + _dump_node(cur.target) + _dump_node(cur.iter))
            loops.append(cur)
        elif isinstance(cur, ast.While):
            chain.append("while:" + _dump_node(cur.test))
            loops.append(cur)
        elif isinstance(cur, (ast.With, ast.AsyncWith)):
            chain.append("with:" + "|".join(_dump_node(i.context_expr) for i in cur.items))
        elif isinstance(cur, ast.Try):
            chain.append("try")
        elif isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            chain.append("def:" + getattr(cur, "name", "lambda"))
        cur = parents.get(id(cur))
    return "/".join(reversed(chain)), loops


def _d_assigns(scope: ast.AST) -> "list[tuple[int, str, str, bool]]":
    """(행, 이름, 값 dump, 중첩 함수 안인가) — scope 안 모든 대입 · for 대상 · with … as."""
    out: "list[tuple[int, str, str, bool]]" = []
    nested: "set[int]" = set()
    for node in ast.walk(scope):
        if node is not scope and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            nested.update(id(m) for m in ast.walk(node))
    for node in ast.walk(scope):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and getattr(node, "value", None) is not None:
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target]):
                out += [(node.lineno, x, _dump_node(node.value), id(node) in nested) for x in _names_in(target)]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            out += [(node.lineno, x, "for:" + _dump_node(node.iter), id(node) in nested) for x in _names_in(node.target)]
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    out += [(node.lineno, x, "with:" + _dump_node(item.context_expr), id(node) in nested)
                            for x in _names_in(item.optional_vars)]
    return out


def _d_elements(func: str, fn: ast.AST, mod: _DModule) -> "list[DElement]":
    parents = _d_parents(fn)
    params: "set[str]" = {a.arg for a in fn.args.args} if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) else set()
    declared: "set[str]" = set()
    for node in ast.walk(fn):
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            declared.update(node.names)
    assigns = _d_assigns(fn)
    out: "list[DElement]" = []

    def defs(names: "set[str]", line: int, loops: "list[ast.AST]") -> "tuple[str, str]":
        fixed: "list[str]" = []
        shared: "list[str]" = []
        spans: "set[tuple[int, int]]" = {(lp.lineno, getattr(lp, "end_lineno", lp.lineno)) for lp in loops}
        for name in sorted(names):
            local = [a for a in assigns if a[1] == name]
            if name in declared or any(a[3] for a in local):
                shared.append(f"{name}=G{[a[2] for a in local]}{mod.mod_defs.get(name, [])}")
                continue
            before = [a[2] for a in local if a[0] < line]
            carried = [a[2] for a in local if a[0] >= line and any(s <= a[0] <= e for s, e in spans)]
            if before:
                fixed.append(f"{name}=L{before}")
            if carried:
                shared.append(f"{name}=C{carried}")
            if not local:
                if name in params:
                    shared.append(f"{name}=F{mod.returns_of(name)}")
                elif name in mod.mod_defs:
                    shared.append(f"{name}=M{mod.mod_defs[name]}")
        return "|".join(fixed), "|".join(shared)

    for dec in getattr(fn, "decorator_list", []):
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "parametrize":
            fixed, shared = defs(_names_in(dec), getattr(fn, "lineno", 0), [])
            out.append(DElement("param:" + _dump_node(dec), fixed, shared, dec, func))
    for node in ast.walk(fn):
        key: "str | None" = None
        used: "set[str]" = set()
        if isinstance(node, ast.Assert):
            test = node.test
            if isinstance(test, ast.Compare):
                key = "cmp:" + repr([type(o).__name__ for o in test.ops]) + "|" + "|".join(
                    _dump_node(c) for c in test.comparators)
                used = set().union(*(_names_in(c) for c in test.comparators))
            else:
                key, used = "bare:" + _dump_node(test), _names_in(test)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if _is_raises(item.context_expr):
                    key, used = "raises:" + _dump_node(item.context_expr), _names_in(item.context_expr)
        elif isinstance(node, ast.ExceptHandler):
            key, used = "except:" + _dump_node(node.type), _names_in(node.type)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and _MOCK_ASSERT.match(node.func.attr):
            args = list(node.args) + [k.value for k in node.keywords]
            key = f"mock:{node.func.attr}|" + "|".join(_dump_node(a) for a in args)
            used = set().union(*(_names_in(a) for a in args)) if args else set()
        if key is not None:
            ctx, loops = _d_context(node, parents, fn)
            fixed, shared = defs(used, getattr(node, "lineno", 0), loops)
            out.append(DElement(ctx + "#" + key, fixed, shared, node, func))
    return out


def _expr_part(key: str) -> str:
    m = _EXPR_PART.match(key)
    return m.group(2) if m else key


def d_changes(old_text: "str | None", new_text: "str | None") -> "list[DChange] | None":
    """D(§4-2) — 함수마다 옛 · 새 원소 순서열을 가장 긴 공통 부분열로 짝짓는다. 함수는 발생 순번(`이름#k`)으로 짝짓는다.
    원문이 없거나(None) 파싱 못 하면 None(빈 파일 · 없는 파일은 빈 글 `""` 로 넘긴다)."""
    old_tree, new_tree = _parse(old_text), _parse(new_text)
    if old_tree is None or new_tree is None:
        return None
    old_mod, new_mod = _DModule(old_tree), _DModule(new_tree)
    out: "list[DChange]" = []
    for key in sorted(set(old_mod.funcs) | set(new_mod.funcs)):
        old_els = _d_elements(*old_mod.funcs[key], old_mod) if key in old_mod.funcs else []
        new_els = _d_elements(*new_mod.funcs[key], new_mod) if key in new_mod.funcs else []
        matcher = difflib.SequenceMatcher(a=[e.key for e in old_els], b=[e.key for e in new_els], autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                for k in range(i2 - i1):
                    x, y = old_els[i1 + k], new_els[j1 + k]
                    if x.fixed != y.fixed:
                        out.append(DChange(x.func, "확정 변화(지역 정의)", "지역 정의", x, y))
                    elif x.shared != y.shared:
                        out.append(DChange(x.func, "공유 정의 변화", "공유 정의 변화", x, y))
            elif op == "replace":
                for k in range(i2 - i1):
                    x = old_els[i1 + k]
                    y = new_els[j1 + k] if j1 + k < j2 else None
                    kind = "삭제" if y is None else ("맥락만" if _expr_part(x.key) == _expr_part(y.key) else "기대식")
                    out.append(DChange(x.func, "확정 변화", kind, x, y))
                out += [DChange(y.func, "추가", "추가", None, y) for y in new_els[j1 + (i2 - i1):j2]]
            elif op == "delete":
                out += [DChange(x.func, "삭제", "삭제", x, None) for x in old_els[i1:i2]]
            elif op == "insert":
                out += [DChange(y.func, "추가", "추가", None, y) for y in new_els[j1:j2]]
    return out


def d_reason_counts(changes: "list[DChange] | None") -> "dict[str, int]":
    counts: "collections.Counter[str]" = collections.Counter(c.kind for c in changes or [])
    return {k: counts[k] for k in D_KINDS if counts[k]}


def _d_note(changes: "list[DChange] | None") -> str:
    if changes is None:
        return "D 계산 불가(파싱 불가)"
    counts = d_reason_counts(changes)
    return ("D " + " · ".join(f"{k} {v}" for k, v in counts.items())) if counts else ""


def element_texts(text: str, element: DElement) -> "set[str]":
    """승인 원소 대조용 옛 문장 원문(앞뒤 공백 걷음 · k0 §4-4) — assert · mock 단언 = 그 문장 · raises · except = 머리(`:` 까지) ·
    parametrize = 데코레이터 식(`@` 붙인 꼴도)."""
    node = element.node
    if isinstance(node, (ast.With, ast.AsyncWith, ast.ExceptHandler)) and node.body:
        first = node.body[0]
        return {_span(text, node.lineno, node.col_offset, first.lineno, first.col_offset).strip()}
    segment: str = _span(text, node.lineno, node.col_offset, node.end_lineno or node.lineno,  # type: ignore[attr-defined]
                         node.end_col_offset or 0).strip()  # type: ignore[attr-defined]
    return {segment, "@" + segment} if element.key.startswith("param:") else {segment}


def _case_of(func: str, paths: "tuple[str, ...]", approved: "dict[str, object]") -> "str | None":
    for path in paths:
        case: str = f"{path}::{func.replace('.', '::')}"
        if case in approved:
            return case
    return None


def approved_change(changes: "list[DChange]", old_text: str, paths: "tuple[str, ...]",
                    approved: "dict[str, dict]") -> "tuple[list[str], dict[str, dict]]":
    """(승인 밖 확정 변화, 승인 원소 실행 흔적 {케이스: {old: [옛 원문], add: k}}) — 확정 변화마다 그 케이스가 승인 케이스이고
    바뀐 옛 원소의 원문이 «바뀌는 기대»와 정확히 같은가 · 추가는 `기대 추가 k` 수 안인가(설계 §4-3 ① · k0 §4-4)."""
    problems: "list[str]" = []
    hits: "dict[str, dict]" = {}
    adds: "collections.Counter[str]" = collections.Counter()
    for change in changes:
        if change.state not in D_FIXED:
            continue
        case: "str | None" = _case_of(change.func, paths, approved)
        if case is None:
            problems.append(f"승인 케이스 밖 확정 변화 `{change.func}`({change.kind})")
            continue
        if change.old is None:
            adds[case] += 1
            continue
        texts: "set[str]" = element_texts(old_text, change.old)
        match: "str | None" = next((t for t in approved[case].get("expect_old", []) if t in texts), None)
        if match is None:
            problems.append(f"`{case}` 의 바뀐 옛 원소가 «바뀌는 기대» 밖 — «{min(texts, key=len)[:120]}»")
            continue
        entry = hits.setdefault(case, {"old": [], "add": 0})
        if match not in entry["old"]:
            entry["old"].append(match)
    for case, count in adds.items():
        limit: int = int(approved[case].get("expect_add", 0))
        if count > limit:
            problems.append(f"`{case}` 기대 추가 {count} > 승인 `기대 추가 {limit}`")
        hits.setdefault(case, {"old": [], "add": 0})["add"] = min(count, limit)
    return problems, hits


def zero_t_fixed(changes: "list[DChange]", new_text: "str | None", paths: "tuple[str, ...]",
                 update_rows: "dict[str, list[str]]", removable: "dict[str, dict]") -> "tuple[list[str], list[str], bool]":
    """0T 의 D 확정 처분 자료(k0 §4-4 `update_rows` · 설계 정오 4) — (밖인 케이스, 걸린 update 행 원문, remove 행 삭제가 있었나).

    확정 변화마다 ① V 에 딸리지 않은 입장 표 `update` 행의 `경로::케이스`(클래스 메서드는 `경로::클래스::메서드`)와 글자 그대로
    같은 케이스 안이거나 ② `remove` 행이 승인한 케이스를 통째로 지운 삭제(그 함수가 새 판에 없다)여야 한다 — 접두 · 부분 일치 없음."""
    new_tree = _parse(new_text)
    alive: "set[str]" = {name for name, _fn in _DModule(new_tree).funcs.values()} if new_tree is not None else set()
    outside: "list[str]" = []
    rows: "list[str]" = []
    removed: bool = False
    for change in changes:
        if change.state not in D_FIXED:
            continue
        case: "str | None" = _case_of(change.func, paths, update_rows)
        if case is not None:
            rows += [r for r in update_rows[case] if r not in rows]
        elif change.state == "삭제" and change.func not in alive and _case_of(change.func, paths, removable) is not None:
            removed = True
        else:
            label: str = f"`{paths[0]}::{change.func.replace('.', '::')}`({change.kind})"
            if label not in outside:
                outside.append(label)
    return outside, rows, removed


def _approved_unseen(changes: "list[DChange] | None", paths: "tuple[str, ...]", approved: "dict[str, dict]") -> "list[str]":
    """승인 케이스인데 그 케이스에 확정 변화가 하나도 없음 — «승인 변경 미검출»(V 로 감사 우회 금지 · §4-3)."""
    hit_cases: "set[str | None]" = {_case_of(c.func, paths, approved) for c in changes or [] if c.state in D_FIXED}
    return [f"승인 변경 미검출 `{case}`" for case in sorted(approved)
            if case.partition("::")[0] in paths and case not in hit_cases]


# 묶음 자료(§4-6 — 표시 · 자료일 뿐 판정에 쓰지 않는다)

def _touched(source: "str | None", path: str, maps: Maps, exports: "_Exports | None") -> "tuple[str, ...]":
    """옛 판 정규화 중 실제로 치환된 대응표 항목(식별자 · 문자열) + 원문에 나오는 파일 경로 항목 — 묶음 열쇠."""
    hits: "set[str]" = set()
    original = maps.fq

    def recording(dotted: str) -> str:
        result: str = original(dotted)
        if result != dotted:
            parts: "list[str]" = dotted.split(".")
            for i in range(len(parts), 0, -1):
                key: str = ".".join(parts[:i])
                hit: "str | None" = maps.rn.get(key) or maps.dm.get(key) or maps.mm.get(key)
                if hit is not None:
                    hits.add(f"{key} → {hit}")
                    break
        return result

    maps.fq = recording  # type: ignore[method-assign] — 이 정규화 한 번 동안만 기록(인스턴스 속성 · 끝에 지운다)
    try:
        canonical(source, path, maps, exports)
    finally:
        del maps.fq
    for old, new in maps.fm.items():
        if source is not None and old in source:
            hits.add(f"{old} → {new}")
    return tuple(sorted(hits))


def _touched_bytes(data: bytes, maps: Maps) -> "tuple[str, ...]":
    try:
        text: str = data.decode("utf-8")
    except UnicodeDecodeError:
        return ()
    return tuple(sorted({f"{k} → {v}" for k, v in {**maps.mm, **maps.dm, **maps.rn, **maps.fm}.items() if k in text}))


def bundle_rules(touched: "tuple[str, ...]") -> "tuple[str, ...]":
    """대응표 항목 → «앞뒤 공통 부분을 걷은 A → B» 규칙(모듈 여럿 이동이 규칙 하나로 준다 · §4-6)."""
    out: "set[str]" = set()
    for item in touched:
        old, _sep, new = item.partition(" → ")
        a = old.replace("/", ".").removesuffix(".py").split(".")
        b = new.replace("/", ".").removesuffix(".py").split(".")
        i: int = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        j: int = 0
        while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]:
            j += 1
        out.add(".".join(a[i:len(a) - j] or ["∅"]) + " → " + ".".join(b[i:len(b) - j] or ["∅"]))
    return tuple(sorted(out))


def _text_only(old_text: "str | None", new_text: "str | None") -> bool:
    """글 묶음 — 원문 AST(정규화 · 대응표 없음)가 docstring 을 걷으면 같다(docstring · `#` 주석 · 빈 줄만 바뀜)."""
    old_tree, new_tree = _parse(old_text), _parse(new_text)
    if old_tree is None or new_tree is None:
        return False
    _strip_docstrings(old_tree)
    _strip_docstrings(new_tree)
    return ast.dump(old_tree) == ast.dump(new_tree)


def _join_reason(*parts: str) -> str:
    return " · ".join(p for p in parts if p)


class Disposition(NamedTuple):
    """시험 쪽 바뀐 파일 하나의 처분(§4-3) — red 면 키가 없다(키 낸 파일 + red 파일 = 바뀐 시험 쪽 파일)."""
    path: str                                  # 키의 파일(옮겼으면 새 경로)
    source: str                                # 옛 경로
    change: str                                # 수정 · 새 파일 · 짝 없는 삭제 · 옮김
    disposition: str                           # 묶음 감사 · 개별 감사 · 승인 변경 감사 · red
    reason: str
    keys: "tuple[tuple[str, str, str], ...]"   # (단위, 전 digest, 후 digest)
    file_reason: str                           # `<file>` 갈래(단위 키면 빈 글)
    touched: "tuple[str, ...]"                 # 닿은 대응표 항목(묶음 열쇠)
    text_only: bool                            # 글 묶음
    hits: "dict[str, dict]"                    # 승인 원소 실행 흔적
    d_reasons: "dict[str, int]"
    update_rows: "tuple[str, ...]" = ()        # 0T — D 확정을 승인한 입장 표 update 행 원문(«update 행 승인» 표시)


def dispose_test_file(kind: str, path: str, target: str, a: "bytes | None", b: "bytes | None", maps: Maps,
                      old_canon: "dict[str, dict | None]", new_canon: "dict[str, dict | None]",
                      exports_then: "_Exports | None", allowed: "set[str]", approved: "dict[str, dict]",
                      update_rows: "dict[str, list[str]] | None" = None) -> "Disposition | None":
    """창 하나의 시험 쪽 파일 처분 — 우선순위 하나(§4-3). 바이트가 같고 자리도 같으면 None.

    새 파일 · 짝 없는 삭제는 표보다 먼저(케이스 규칙은 close 가 따로 본다) `<file>` 개별 감사 · 바이트 그대로 옮긴 파일은 `<file>`
    묶음 감사 · ① (change) D 확정이 전부 승인 원소 → 승인 변경 감사 · ② 기존 0C 검사 합격 → 감사(닿은 항목이 있으면 묶음 ·
    D 는 사유) · ③ D 확정 → red · ④ (follow · change) 허용 파일 → 개별 감사 · 그 밖 red. `test` 창은 D 확정이 전부
    «V 에 딸리지 않은 입장 표 `update` 행의 케이스 안» 또는 «`remove` 행이 승인한 케이스 통째 삭제»일 때만 개별 감사(그 파일의
    바뀐 단위 전부 키 · `approved` = remove 행 케이스) · 하나라도 밖이면 red · D 확정이 없으면 개별 감사. 비 .py 는 ② · ④ 만
    (0T 는 개별 감사)."""
    py: bool = target.endswith(".py")
    keys, file_reason = audit_keys(a, b, py)
    if not keys and path != target:
        keys, file_reason = [("<file>", _digest(a), _digest(b))], "바이트 그대로 옮긴 파일"
    if not keys:
        return None
    change: str = "새 파일" if a is None else "짝 없는 삭제" if b is None else "옮김" if path != target else "수정"
    hits: "dict[str, dict]" = {}
    d_counts: "dict[str, int]" = {}
    rows: "list[str]" = []
    paths: "tuple[str, ...]" = tuple(dict.fromkeys((target, path)))

    def made(disposition: str, reason: str, touched: "tuple[str, ...]" = (), text_only: bool = False) -> Disposition:
        return Disposition(target, path, change, disposition, reason, () if disposition == RED else tuple(keys),
                           file_reason, touched, text_only, hits, d_counts, () if disposition == RED else tuple(rows))

    if a is None or b is None:
        if kind == "change" and py:
            old_text: "str | None" = "" if a is None else _py_source(a)
            new_text: "str | None" = "" if b is None else _py_source(b)
            found = d_changes(old_text, new_text)
            if found:
                hits.update(approved_change(found, old_text or "", paths, approved)[1])
        return made(SINGLE_AUDIT, "새 파일 — 케이스 규칙 먼저" if a is None else "짝 없는 삭제 — 케이스 규칙 먼저")
    if a == b:
        return made(BUNDLE_AUDIT, "바이트 그대로 옮김(conftest · 패키지 자리가 바뀐다)", (f"{path} → {target}",))
    allowed_file: bool = path in allowed or target in allowed
    not_allowed: str = "" if kind not in ("follow", "change") else \
        ("승인 케이스 파일이 아니고 " if kind == "change" else "") + "`retain` 재조직 행(0F 허용 파일)에 없는 파일"
    if not py:
        if _compare_bytes(a, b, maps):
            touched = _touched_bytes(a, maps)
            return made(BUNDLE_AUDIT if touched else SINGLE_AUDIT,
                        "대응표 문자열 치환으로 설명됨" + ("" if touched else "(닿은 항목 없음)"), touched)
        if kind == "test":
            return made(SINGLE_AUDIT, "0T 시험 자료 변경")
        if kind in ("follow", "change") and allowed_file:
            return made(SINGLE_AUDIT, "허용 파일")
        return made(RED, _join_reason("비 .py 시험 쪽 파일 변경 — 대응표 치환으로 설명되지 않음", not_allowed))
    old_text, new_text = _py_source(a), _py_source(b)
    changes: "list[DChange] | None" = d_changes(old_text, new_text)
    d_counts.update(d_reason_counts(changes))
    d_fixed: bool = bool(changes) and any(c.state in D_FIXED for c in changes or [])
    d_note: str = _d_note(changes)
    unseen: "list[str]" = _approved_unseen(changes, paths, approved) if kind == "change" else []
    if kind == "test":
        if not d_fixed:
            return made(SINGLE_AUDIT, _join_reason("0T", d_note))
        outside_cases, matched_rows, removed = zero_t_fixed(changes or [], new_text, paths, update_rows or {}, approved)
        rows.extend(matched_rows)
        if outside_cases:
            return made(RED, _join_reason("D 확정 — 0T 는 V 에 딸리지 않은 입장 표 update 행의 케이스와 remove 행이 승인한 케이스 삭제만 "
                                          "감사한다 · 밖: " + " · ".join(outside_cases), d_note))
        return made(SINGLE_AUDIT, _join_reason("0T", *[f"0T update 행 — {r}" for r in rows],
                                               "입장 표 remove 행 케이스 삭제" if removed else "", d_note))
    problems: "list[str]" = []
    if kind == "change" and d_fixed:
        problems, found_hits = approved_change(changes or [], old_text or "", paths, approved)
        if not problems:
            hits.update(found_hits)
            return made(APPROVED_AUDIT, _join_reason("D 확정 전부 승인 원소", d_note))
    verdict, why = _compare_py(path, target, maps, old_canon, new_canon)
    if verdict in ("green", "note"):
        touched = _touched(_text(a), path, maps, exports_then)
        text_only: bool = not touched and _text_only(old_text, new_text)
        return made(BUNDLE_AUDIT if touched else SINGLE_AUDIT,
                    _join_reason("0C 검사 합격" + ("" if touched else "(닿은 항목 없음)"), d_note, *unseen), touched, text_only)
    if d_fixed:
        return made(RED, _join_reason(f"D 확정({d_note})", *problems))
    if kind in ("follow", "change") and allowed_file:
        return made(SINGLE_AUDIT, _join_reason("허용 파일", d_note, *unseen))
    return made(RED, _join_reason("0C 검사 불합격 · " + why, not_allowed))


class Judgement(NamedTuple):
    dispositions: "list[Disposition]"
    maps: Maps
    is_test: "Callable[[str], bool]"


def judge_test_side(kind: str, changed: "dict[str, tuple[bytes | None, bytes | None]]", files_then: "set[str]",
                    files_now: "set[str]", read_then: Reader, read_now: Reader, allow: "dict | None" = None) -> Judgement:
    """창의 시험 쪽 처분 전부 — 바뀐 경로(옛 · 새 바이트) · 두 판의 파일 목록 · 읽기 함수 · 허용 표(follow · change · 0T 는
    `{"remove_cases": [G1 확정판 remove_rows(v 없음)의 경로::케이스], "update_rows": [스냅숏 update_rows 그대로]}`)만 받는다.

    이동 전 · 후 어느 쪽이든 시험 쪽이면 처분한다(설계 :99 — 기능 모드의 분류 중립과 다르다): 시험 → 시험 이동은 옛 경로로 한 번
    (옮긴 파일) · 제품 → 시험 이동은 새 시험 쪽 파일(`<file>` · 전 없음) · 시험 → 제품 이동은 짝 없는 삭제(`<file>` · 후 없음).
    저장소 밖(과거 커밋 재생)에서도 그대로 부른다."""
    test_dirs: "set[str]" = _test_dirs(sorted(files_now)) | _test_dirs(sorted(files_then))
    is_test: "Callable[[str], bool]" = lambda p: _is_test_refactor(p, test_dirs)  # noqa: E731
    live_now: "set[str]" = {d for p in files_now for d in _ancestors(p)}
    exports_then = _Exports(read_then, set(files_then))
    maps, old_canon, new_canon = build_maps(changed, is_test, live_now, exports_then, _Exports(read_now, set(files_now)))
    allowed: "set[str]" = set()
    approved: "dict[str, dict]" = {}
    if allow is not None and kind in ("follow", "change"):
        allowed = set(allow.get("retain_files", []))
        if kind == "change":
            approved = allow.get("approved_cases", {})
            allowed |= {case.partition("::")[0] for case in approved}
    update_rows: "dict[str, list[str]]" = {}
    if allow is not None and kind == "test":
        approved = {case: {} for case in allow.get("remove_cases", [])}   # 0T: G1 확정판 remove 행(v 없음 · k0 §4-4)
        for row in allow.get("update_rows", []):                          # 0T 몫은 V 에 딸리지 않은 update 행만(k0 §4-4)
            if row.get("v") is None:
                update_rows.setdefault(row["case"], []).append(str(row.get("row", "")))
    sources: "dict[str, str]" = {new: old for old, new in maps.pairs.items()}
    out: "list[Disposition]" = []
    for p, (a, b) in sorted(changed.items()):
        target: str = p
        old_b: "bytes | None" = a
        new_b: "bytes | None" = b
        if p in sources:                                  # 이동의 새 자리
            if not is_test(p) or is_test(sources[p]):
                continue                                  # 시험 → 시험 은 옛 경로에서 · 시험 → 제품 의 새 자리는 제품 쪽
            old_b = None                                  # 제품 → 시험: 새 시험 쪽 파일
        elif not is_test(p):
            continue
        elif b is None and p in maps.pairs and is_test(maps.pairs[p]):
            target = maps.pairs[p]                        # 시험 → 시험 이동(시험 → 제품 은 짝 없는 삭제로 둔다)
            new_b = changed[target][1] if target in changed else read_now(target)
        disposition = dispose_test_file(kind, p, target, old_b, new_b, maps, old_canon, new_canon, exports_then, allowed,
                                        approved, update_rows)
        if disposition is not None:
            out.append(disposition)
    return Judgement(out, maps, is_test)


# G1 결속 · 허용 표 · 마이그레이션 연산(설계 §3-4 · §4-5 · k0 §4-4)

def op_key(app: str, call: str) -> str:
    """마이그레이션 연산 키(k0 §4-4) — `<앱 라벨> · <호출식 AST dump>`(키워드 순서 · 인자 값까지 · 위치 정보 없음)."""
    try:
        body = ast.parse(call, mode="eval").body
    except SyntaxError as exc:
        raise RunError(f"V 연산 호출식을 읽지 못했다 — {call[:120]}") from exc
    return f"{app} · " + ast.dump(body, annotate_fields=True, include_attributes=False)


def allow_table(snap: dict) -> dict:
    """G1 후보 스냅숏(k0 §4-4) → 창 허용 표 — `retain` 재조직 파일 · 승인 케이스와 «바뀌는 기대» · V 연산 다중집합 · 다른 BC
    편집 목록 · `add`/`remove` 케이스."""
    approved: "dict[str, dict]" = {}
    adds: "list[str]" = []
    removes: "list[str]" = []
    ops: "list[str]" = []
    for v in snap.get("V", []):
        for test in v.get("tests", []):
            case: str = test["case"]
            entry = approved.setdefault(case, {"expect_old": [], "expect_add": 0, "V": []})
            entry["expect_old"] += [t for t in test.get("expect_old", []) if t not in entry["expect_old"]]
            entry["expect_add"] += int(test.get("expect_add", 0) or 0)
            if v["id"] not in entry["V"]:
                entry["V"].append(v["id"])
            if test.get("verb") == "add":
                adds.append(case)
            elif test.get("verb") == "remove":
                removes.append(case)
        ops += [op_key(op["app"], op["call"]) for op in v.get("ops", [])]
    return {"retain_files": sorted({r["path"] for r in snap.get("retain_rows", [])}), "approved_cases": approved,
            "ops": ops, "other_bc_edits": list(snap.get("other_bc_edits", [])), "add_cases": adds, "remove_cases": removes,
            "V": [v["id"] for v in snap.get("V", [])]}


def migration_ops(data: "bytes | None") -> "tuple[list[tuple[str | None, str]], list[str]]":
    """새 마이그레이션 파일의 `Migration.operations` 원소마다 (연산 이름, AST dump) — 정적으로 못 읽으면 문제 목록."""
    tree = _parse(_py_source(data))
    if tree is None:
        return [], ["파싱 불가"]
    found: "ast.expr | None" = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Migration":
            for stmt in node.body:
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target] if isinstance(stmt, ast.AnnAssign) else []
                if any(isinstance(t, ast.Name) and t.id == "operations" for t in targets):
                    found = stmt.value  # type: ignore[union-attr]
    if not isinstance(found, (ast.List, ast.Tuple)):
        return [], ["`Migration.operations` 목록을 정적으로 읽지 못함"]
    out: "list[tuple[str | None, str]]" = []
    for element in found.elts:
        name: "str | None" = None
        if isinstance(element, ast.Call):
            name = element.func.attr if isinstance(element.func, ast.Attribute) else \
                element.func.id if isinstance(element.func, ast.Name) else None
        out.append((name, ast.dump(element, annotate_fields=True, include_attributes=False)))
    return out, []


def _external(what: str, fn: "Callable[..., object]", *args: object) -> object:
    """다른 갈래 모듈(refactor_audit · behavior_support) 호출 — 그 모듈의 예외는 종류와 무관하게 실행 불능(판정하지 않는다)."""
    try:
        return fn(*args)
    except RunError:
        raise
    except Exception as exc:  # noqa: BLE001 — 경계 밖 모듈 실패
        raise RunError(f"{what} 실패: {type(exc).__name__}: {exc}") from exc


def _audit_module():  # noqa: ANN202
    try:
        import refactor_audit  # noqa: PLC0415 — 함수 안 import(k0 §4-1)
    except Exception as exc:  # noqa: BLE001
        raise RunError(f"refactor_audit 를 불러오지 못했다 — {type(exc).__name__}: {exc}") from exc
    return refactor_audit


def _support_module():  # noqa: ANN202
    try:
        import behavior_support  # noqa: PLC0415 — 함수 안 import(k0 §4-1)
    except Exception as exc:  # noqa: BLE001
        raise RunError(f"behavior_support 를 불러오지 못했다 — {type(exc).__name__}: {exc}") from exc
    return behavior_support


def _g1_state(folder: Path, repo: Path) -> "tuple[str, dict, tuple[str, str, str] | None]":
    """(현재 명세 승인판 digest, 그 스냅숏, 마지막 `G1 변경판 확정` (시각, digest, 후보) — 없으면 None)."""
    ra = _audit_module()
    snap = _external("refactor_audit.changes_snapshot", ra.changes_snapshot, folder, repo)
    digest: str = str(_external("refactor_audit.snapshot_digest", ra.snapshot_digest, snap))
    confirmed = _external("refactor_audit.g1_confirmed", ra.g1_confirmed, folder)
    return digest, snap, confirmed  # type: ignore[return-value]


def _g1_binding(folder: Path, repo: Path) -> "tuple[str, dict]":
    """(현재 명세 승인판 digest, 허용 표) — 마지막 `G1 변경판 확정` digest 와 다르면 실행 불능(창을 열지 · 바꾸지 않는다)."""
    digest, snap, confirmed = _g1_state(folder, repo)
    if confirmed is None:
        raise RunError("`G1 변경판 확정` 줄이 없다 — follow · change 창은 G1 변경판 확정 뒤에 연다")
    if confirmed[1] != digest:
        raise RunError(f"현재 명세 승인판 digest {digest} ≠ 마지막 `G1 변경판 확정` digest {confirmed[1]} — "
                       "창을 열지(허용 표를 바꾸지) 않는다")
    return digest, allow_table(snap)


def _confirmed_snapshot(folder: Path, repo: Path, label: str) -> dict:
    """리팩토링 모드 0T · 0C close 가 읽는 G1 확정판 스냅숏(입장 표 update 행 · «다른 BC 편집 목록») — 이 두 창은 허용 표를 open 에
    동결하지 않으므로 close 때 읽는다. `G1 변경판 확정` 이 없거나 승인판이 G1 확정과 다르면 실행 불능이다."""
    digest, snap, confirmed = _g1_state(folder, repo)
    if confirmed is None:
        raise RunError(f"`G1 변경판 확정` 줄이 없다 — 리팩토링 모드 {label} close 는 G1 확정판(입장 표 update 행 · «다른 BC 편집 "
                       "목록»)을 읽는다")
    if confirmed[1] != digest:
        raise RunError(f"승인판이 G1 확정과 다르다 — 현재 명세 승인판 digest {digest} ≠ 마지막 `G1 변경판 확정` digest "
                       f"{confirmed[1]}({label} close 는 G1 확정판에서만 읽는다)")
    return snap


def _outside_allowed(kind: str, edits: "list[dict]") -> "set[str]":
    """대상 BC 밖에서 이 창이 고쳐도 되는 경로(§3-5 · §4-5 «창 종류가 허락한 갈래만») — 0T 는 없음(루트 pytest 설정 절은
    `_side_rules` 가 따로 받는다) · 0C · 0F 는 «다른 BC 편집 목록»의 프로젝트 합성 · 공유 표면 줄 · 변경 창은 목록 전부."""
    if kind == "test":
        return set()
    return {e["path"] for e in edits if kind == "change" or e.get("kind") in FOLLOW_OUTSIDE_KINDS}


def _target_bc(folder: Path) -> str:
    """대상 BC — 이번 실행 줄(`… · 모드 리팩토링 · audit <시각>`)의 `audit/<시각>/plan.md` `- BC:` 줄(refactor_audit plan 산출)."""
    scope: Path = folder / "refactor-scope.md"
    text: str = re.split(r"(?m)^#+\s*앞 실행", scope.read_text(encoding="utf-8") if scope.is_file() else "")[0]
    m = re.search(r"^\s*실행 · G0 승인 \S+ · 모드 리팩토링 · audit (\S+)", text, re.M)
    if not m:
        raise RunError("refactor-scope.md 에 리팩토링 실행 줄(`… · 모드 리팩토링 · audit <시각>`)이 없다 — 대상 BC 를 모른다")
    plan: Path = folder / "audit" / m.group(1) / "plan.md"
    found = re.search(r"^- BC: `([^`]+)`", plan.read_text(encoding="utf-8"), re.M) if plan.is_file() else None
    if not found:
        raise RunError(f"{plan} 에 `- BC:` 줄이 없다 — 대상 BC 를 모른다")
    return found.group(1)


# close(리팩토링 모드)

class _CloseWindow(NamedTuple):
    """리팩토링 close 한 번이 나눠 쓰는 창 자료 — 창 기록 · 허용 표 · 대상 BC 안쪽 접두와 그 밖 허용 경로 · 바뀐 경로 · 대응표 ·
    분류 · 앞 창들의 마지막 close."""
    folder: Path
    repo: Path
    kind: str
    opened: dict
    allow: "dict | None"
    inside: str
    listed: "set[str]"
    removable: "collections.Counter[str]"    # 0T — G1 확정판 remove_rows(v 없음)의 케이스(감소 허용 · 통째 삭제 예외)
    merged: "set[str]"
    changed: "dict[str, tuple[bytes | None, bytes | None]]"
    maps: Maps
    is_test: "Callable[[str], bool]"
    files_now: "list[str]"
    read_then: Reader
    read_now: Reader
    config_now: "dict[str, str]"
    prior: "list[tuple[dict, dict]]"


def _prior_sum(w: _CloseWindow, key: str) -> "collections.Counter[str]":
    """앞 변경 창들의 마지막 close 가 남긴 누계(연산 · 케이스 증감)."""
    return collections.Counter(x for o, last in w.prior if o.get("kind") == "change" for x in last.get(key, []))


def _side_rules(w: _CloseWindow) -> "tuple[list[str], list[str], list[str], list[str], list[str]]":
    """(red, 보고, 승인된 케이스 감소, 케이스 추가, 허용 밖 대상 BC 밖 경로) — 제품 쪽(0T 고정) · pytest 설정 · 수집 케이스 ·
    대상 BC 밖 경로(0T 는 루트 pytest 설정 절만 · 0C · 0F · 변경은 ⊆ 다른 BC 편집 목록 — 창 종류가 허락한 갈래만)."""
    kind, opened, maps, label = w.kind, w.opened, w.maps, KIND_LABELS[w.kind]
    reds: "list[str]" = []
    notes: "list[str]" = []
    cases_then: "dict[str, list[str]]" = {p: v for p, v in opened["cases"].items() if p not in w.merged}
    cases_now: "dict[str, list[str]]" = {p: v for p, v in _cases(w.files_now, w.read_now, w.config_now, w.is_test).items()
                                         if p not in w.merged}
    before_c = collections.Counter(f"{maps.pairs.get(p, p)}::{x}" for p, v in cases_then.items() for x in v)
    after_c = collections.Counter(f"{p}::{x}" for p, v in cases_now.items() for x in v)
    gone, came = before_c - after_c, after_c - before_c
    removed_ok: "list[str]" = []
    outside: "list[str]" = []
    if kind == "test":
        for p, (a, b) in sorted(w.changed.items()):
            product_side: bool = not w.is_test(p)             # 리팩토링 모드: 시험 → 제품 이동의 새 자리도 제품 쪽 변경
            if product_side and p in PYTEST_FILES and _outside_pytest_section(p, a) == _outside_pytest_section(p, b):
                notes.append(f"{p} — pytest 설정 절 변경(0T 허용 · testpaths·python_files·addopts 변경은 감수 hunk 대조)")
                continue
            if not p.startswith(w.inside):
                outside.append(p)
                reds.append(f"{p} — 0T 는 대상 BC(`{w.inside}`) 밖 편집 없음(루트 pytest 설정 절만)")
            elif product_side:
                reds.append(f"{p} — 제품 쪽 변경(0T 는 제품 코드 고정)")
        allowed_rm: "collections.Counter[str]" = w.removable
        reds += [f"테스트 케이스 감소 `{k}` ×{c}(G1 확정판 입장 표 remove 행 밖)" for k, c in (gone - allowed_rm).items()]
        reds += [f"테스트 케이스 추가 `{k}` ×{c}(0T 는 새 case 없이 — 재조직 규범)" for k, c in came.items()]
        return reds, notes, sorted((gone & allowed_rm).elements()), [], outside
    cfg_then: "dict[str, str]" = {k: v for k, v in opened["pytest"].items() if k not in w.merged}
    if cfg_then != {k: v for k, v in w.config_now.items() if k not in w.merged}:
        reds.append(f"pytest 설정 변경(리팩토링 모드 {label} 창은 pytest 설정 무변)")
    for p, q in sorted(maps.pairs.items()):
        if w.is_test(p) and p.endswith(".py") and _collectible(p, opened["pytest"]) and not _collectible(q, w.config_now):
            reds.append(f"{p} → {q} — 테스트 파일이 수집 밖으로 옮겨졌다(python_files·testpaths)")
    if kind in ("code", "follow"):
        names_then = collections.Counter(x for v in cases_then.values() for x in v)
        names_now = collections.Counter(x for v in cases_now.values() for x in v)
        if names_then != names_now:
            lost, new = sorted((names_then - names_now).elements()), sorted((names_now - names_then).elements())
            reds.append(f"수집 테스트 케이스 변화 −{len(lost)} {lost[:3]} +{len(new)} {new[:3]}({label} 창은 케이스 이름 불변)")
    if kind == "change":
        assert w.allow is not None
        room_rm = collections.Counter(w.allow.get("remove_cases", [])) - _prior_sum(w, "cases_removed")
        room_add = collections.Counter(w.allow.get("add_cases", [])) - _prior_sum(w, "cases_added")
        reds += [f"테스트 케이스 감소 `{k}` ×{c}(승인판 remove 행 밖)" for k, c in (gone - room_rm).items()]
        reds += [f"테스트 케이스 추가 `{k}` ×{c}(승인판 add 행 밖)" for k, c in (came - room_add).items()]
        removed_ok = sorted((gone & room_rm).elements())
    outside = [p for p in sorted(w.changed) if not p.startswith(w.inside) and p not in w.listed]
    allowed_kinds: str = "목록 전부" if kind == "change" else " · ".join(sorted(FOLLOW_OUTSIDE_KINDS))
    reds += [f"{p} — 대상 BC(`{w.inside}`) 밖 경로가 다른 BC 편집 목록 밖(창 {label} 허용 갈래: {allowed_kinds})" for p in outside]
    return reds, notes, removed_ok, sorted(came.elements()) if kind == "change" else [], outside


def _migration_rules(w: _CloseWindow) -> "tuple[list[str], list[str], list[str], list[str], str]":
    """(red, 보고, 생성 연산 키, 바뀐 기존 마이그레이션, 요약 구) — 0T · 0C · 0F 는 정적 · 동적 무변(지금 규칙) · 변경 창은 기존 파일
    수정 · 삭제 red · 새 파일의 연산 다중집합 ⊆ «승인 V 연산 − 앞 창 생성분» · `makemigrations` 산출 밖 연산 red(§4-5)."""
    kind, opened, maps = w.kind, w.opened, w.maps
    reds: "list[str]" = []
    notes: "list[str]" = []
    static_then: "dict[str, list[str]]" = opened["migrations_static"]
    static_now = _migrations_static(w.files_now, w.read_now)
    generated: "list[str]" = []
    existing: "list[str]" = []
    for key in sorted(set(static_then) | set(static_now)):
        then, now_ = static_then.get(key), static_now.get(key)
        if (then or [None])[0] == (now_ or [None])[0] or (then and then[1] in w.merged) or (now_ and now_[1] in w.merged):
            continue
        if kind == "change" and then is None and now_ is not None:
            ops, problems = migration_ops(w.read_now(now_[1]))
            reds += [f"마이그레이션 `{key}` — {x}" for x in problems]
            for name, dumped in ops:
                if name not in MIGRATION_OPS:
                    reds.append(f"마이그레이션 `{key}` — makemigrations 산출 밖 연산 {name or '(호출 아님)'}(#593)")
                    continue
                generated.append(f"{key.rpartition('/')[0]} · {dumped}")
            continue
        if kind in ("code", "follow") and then and now_:
            before = canonical(_text(w.read_then(then[1])), then[1], maps, None)
            after = canonical(_text(w.read_now(now_[1])), now_[1], None, None)
            if before and after and (before["imports"], before["body"]) == (after["imports"], after["body"]):
                notes.append(f"마이그레이션 `{key}` — 옮긴 코드를 따라간 경로 치환만(판정 밖)")
                continue
        state: str = "추가" if then is None else "삭제" if now_ is None else "수정"
        if kind == "change":
            existing.append(key)
            reds.append(f"기존 마이그레이션 {state} `{key}`(지원 안 함 — 리팩토링 모드도 기존 마이그레이션은 고치지 않는다)")
        else:
            reds.append(f"마이그레이션 {state} `{key}`(정적 — 리팩터는 스키마 이력을 바꾸지 않는다)")
    if kind == "change":
        assert w.allow is not None
        room_ops = collections.Counter(w.allow.get("ops", [])) - _prior_sum(w, "ops")
        reds += [f"승인 밖 연산 ×{c} — {op[:240]}(승인 V 연산 − 앞 창 생성분 밖)"
                 for op, c in (collections.Counter(generated) - room_ops).items()]
    static: str = "마이그레이션 정적 " + ("red" if reds else f"승인 연산 {len(generated)}" if generated else "무변")
    dyn_then: "dict[str, object]" = opened["migrations_dynamic"]
    if dyn_then["status"] != "측정":
        dyn_note: str = f"동적 미측정(open 미측정 — close 도 재지 않는다: {dyn_then.get('reason')})"
        notes.append(dyn_note)
        return reds, notes, generated, existing, f"{static} · {dyn_note}"
    dyn_now = _migrations_dynamic(w.repo, w.config_now)
    if dyn_now.get("cleaned"):
        notes.append(f"동적 측정이 만든 미추적 파일 제거: {', '.join(dyn_now['cleaned'][:3])}")  # type: ignore[index]
    if dyn_now["status"] != "측정":
        reds.append(f"마이그레이션 동적 측정 실패(open 은 측정됐다 — {dyn_now.get('reason')})")
        return reds, notes, generated, existing, f"{static} · 동적 red(측정 실패)"
    extra = sorted(set(dyn_now["changes"]) - set(dyn_then["changes"]))  # type: ignore[arg-type]
    lost = sorted(set(dyn_then["changes"]) - set(dyn_now["changes"]))  # type: ignore[arg-type]
    reds += [f"마이그레이션 변경 생김 `{c}`(동적 — 모델 상태가 마이그레이션과 어긋났다)" for c in extra]
    reds += [f"마이그레이션 변경 사라짐 `{c}`(동적 — 창 안에서 모델 상태가 바뀌었다)" for c in lost]
    return reds, notes, generated, existing, f"{static} · 동적 {'무변' if not extra and not lost else 'red'}"


def _close_refactor(folder: Path, repo: Path, run_dir: Path, n: int, opened: dict, closes: "list[dict]") -> int:
    """리팩토링 모드 close(§4-3 · §4-5) — 시험 쪽 처분 · 감사 요청 · 케이스 · 설정 · 마이그레이션 · 대상 BC 밖 경로 · 끝 지문.
    대상 BC 를 못 읽으면 어느 창이든 실행 불능이다(창마다 대상 BC 밖 경로를 본다). 0T · 0C 는 허용 표를 동결하지 않아 close 때
    G1 확정판 스냅숏을 읽고(승인판이 G1 확정과 다르면 실행 불능 · 0T 의 remove · update 예외는 이 스냅숏에서만), 0F · 변경은
    open · rebind 때 동결한 허용 표를 쓴다."""
    kind: str = opened["kind"]
    label: str = KIND_LABELS[kind]
    head0: str = opened["head"]
    head: str = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()
    if not _is_ancestor(repo, head0, head):
        raise RunError(f"판정 불가(창 기준 {head0[:12]} 이 HEAD 의 조상이 아니다 — rebase·reset 뒤에는 철회하거나 STOP 한다)")
    merged, lane, unapproved = _merge_paths(repo, folder, head0)
    overlap: "set[str]" = merged & lane
    if overlap:
        raise RunError("판정 불가(머지 겹침) — 승인 머지가 들여온 경로를 레인도 바꿨다: " + ", ".join(sorted(overlap)[:5]))
    inside: str = f"application/{_target_bc(folder)}/"
    allow: "dict | None" = None
    judge_allow: "dict | None"
    if kind in ("follow", "change"):
        current: str = _g1_state(folder, repo)[0]
        if current != opened.get("g1_digest"):
            raise RunError(f"명세 승인판 digest {current} ≠ 창 결속 {opened.get('g1_digest')} — 승인판이 바뀌었으면 "
                           "G1 변경판 확정 · rebind 뒤에 close 한다")
        allow = judge_allow = opened["allow"]
        listed: "set[str]" = _outside_allowed(kind, list(opened["allow"].get("other_bc_edits", [])))
        removable: "collections.Counter[str]" = collections.Counter()
    else:
        snap: dict = _confirmed_snapshot(folder, repo, label)
        listed = _outside_allowed(kind, list(snap.get("other_bc_edits", [])))
        removable = collections.Counter(str(r["case"]) for r in snap.get("remove_rows", []) if r.get("v") is None)
        judge_allow = {"remove_cases": sorted(removable),
                       "update_rows": list(snap.get("update_rows", []))} if kind == "test" else None
    dirty0: "dict[str, dict]" = opened["dirty"]

    def read_then(p: str) -> "bytes | None":
        if p in dirty0:
            b64 = dirty0[p].get("b64")
            return base64.b64decode(b64) if b64 is not None else None
        return _git_bytes(repo, head0, p)

    def sha_then(p: str) -> "str | None":
        return dirty0[p]["sha"] if p in dirty0 else _sha(_git_bytes(repo, head0, p))

    def read_now(p: str) -> "bytes | None":
        return (repo / p).read_bytes() if (repo / p).is_file() else None

    files_now: "list[str]" = _worktree_files(repo)
    files_then: "list[str]" = sorted((set(_tree_files(repo, head0)) | {p for p, e in dirty0.items() if e["sha"]})
                                     - {p for p, e in dirty0.items() if not e["sha"]})
    candidates: "set[str]" = (_diff_names(repo, head0, "HEAD") | _git_worktree_changes(repo, head0)
                              | set(_dirty(repo)) | set(dirty0))
    changed: "dict[str, tuple[bytes | None, bytes | None]]" = {}
    for p in sorted(candidates - merged):
        if _excluded(p):
            continue
        now: "bytes | None" = read_now(p)
        if _sha(now) != sha_then(p):
            changed[p] = (read_then(p), now)
    judged: Judgement = judge_test_side(kind, changed, set(files_then), set(files_now), read_then, read_now, judge_allow)
    maps, disps = judged.maps, judged.dispositions
    window = _CloseWindow(folder, repo, kind, opened, allow, inside, listed, removable, merged, changed, maps, judged.is_test,
                          files_now,
                          read_then, read_now, _pytest_config(repo),
                          [(o, c[-1]) for m, o, c in _windows(run_dir) if m < n and c])
    reds: "list[str]" = [f"{d.path} — {d.reason}" for d in disps if d.disposition == RED]
    notes: "list[str]" = [f"미승인 머지 {s} — 들여온 경로를 레인 편집으로 판정(approved-merges.txt 밖)" for s in unapproved]
    side_reds, side_notes, removed_ok, cases_added, outside = _side_rules(window)
    migration_reds, migration_notes, generated, existing_changed, migration_text = _migration_rules(window)
    reds += side_reds + migration_reds
    notes += side_notes + migration_notes
    for old_mod in sorted(maps.mm):
        old_path: str = old_mod.replace(".", "/") + ".py"
        if old_path in changed and changed[old_path][1] is not None:
            tree = _parse(_text(changed[old_path][1]))
            if tree is not None and all(isinstance(nd, (ast.Import, ast.ImportFrom)) for nd in tree.body):
                notes.append(f"{old_path} — 재수출만 남은 모듈(patch(\"{old_mod}.…\") 는 헛돈다 — 사각)")
    notes += [f"{d.path} — {u}" for d in disps if d.disposition != RED for u in _approved_unseen_notes(d)]
    run: str = opened["run"]
    key_of = lambda d, unit: f"{run}/w{n} · {d.path} · {unit[0]} · 전 {unit[1]} · 후 {unit[2]}"  # noqa: E731
    keys: "list[str]" = [key_of(d, unit) for d in disps for unit in d.keys]
    hits: "dict[str, dict]" = {}
    for d in disps:
        for case, h in d.hits.items():
            entry = hits.setdefault(case, {"old": [], "add": 0})
            entry["old"] += [t for t in h["old"] if t not in entry["old"]]
            entry["add"] += h["add"]
    request: "str | None" = None
    for stale in run_dir.glob(f"w{n}-audit-spots-B*.txt") if run_dir.is_dir() else []:
        stale.unlink()                                    # 앞 close 의 곁 파일 — 이번 요청과 어긋나지 않게
    if keys:
        request = f"w{n}-audit-request.md"
        run_dir.mkdir(parents=True, exist_ok=True)
        text, side = _audit_request_text(run, n, label, len(closes) + 1, disps, key_of, read_then, read_now, files_now,
                                         judged.is_test, (allow or {}).get("approved_cases", {}))
        (run_dir / request).write_text(text, encoding="utf-8")
        for name, body in side.items():
            (run_dir / name).write_text(body, encoding="utf-8")
    fingerprint_end = _external("behavior_support.fingerprint", _support_module().fingerprint, repo)
    deleted_ok: "set[str]" = {d.source for d in disps if d.disposition != RED and d.change == "짝 없는 삭제"}
    verdict: str = "red" if reds else ("audit" if keys else "green")
    count = collections.Counter(d.disposition for d in disps)
    closes.append({"closed": _now(), "verdict": verdict, "range": f"{head0}..{head}", "reds": reds, "notes": notes,
                   "green_files": [], "merged_excluded": sorted(merged),
                   "maps": {"pairs": len(maps.pairs), "dirs": len(maps.dirs), "modules": len(maps.mm),
                            "definitions": len(maps.dm), "renames": len(maps.rn)},
                   "map_items": {"pairs": dict(sorted(maps.pairs.items())), "dirs": dict(sorted(maps.dirs.items())),
                                 "fm": dict(sorted(maps.fm.items()))},
                   "mode": "refactor", "keys": keys,
                   "dispositions": [{"path": d.path, "처분": d.disposition, "사유": d.reason, "묶음": list(bundle_rules(d.touched)),
                                     "from": d.source, "change": d.change, "file_reason": d.file_reason,
                                     "touched": list(d.touched), "text_only": d.text_only, "update_rows": list(d.update_rows),
                                     "keys": [key_of(d, unit) for unit in d.keys],
                                     "요구 판정": [" · ".join(v) for v in required_verdicts(d)]} for d in disps],
                   "audit_request": request, "fingerprint_end": fingerprint_end,
                   "g0_keep_exceptions": {"moved": dict(sorted(maps.pairs.items())),
                                          "removed": sorted({structure_key(c) for c in removed_ok} | deleted_ok)},
                   "approved_hits": hits, "ops": generated, "cases_added": cases_added, "cases_removed": removed_ok,
                   "outside_bc": outside, "existing_migrations": existing_changed,
                   "test_changed": sorted(p for p in changed if judged.is_test(p))})
    _dump(run_dir / f"w{n}-close.json", closes)
    for r in reds:
        print(f"  red: {r}")
    for note in notes:
        print(f"  보고: {note}")
    state_text: str = f"red {len(reds)}건" if reds else f"감사 요청 키 {len(keys)}" if keys else "시험 쪽 무변"
    print(f"요약: 창 w{n} close {state_text} · 종류 {label} · 모드 리팩토링 · 시험 쪽 바뀐 파일 {len(disps)}"
          f"(묶음 감사 {count[BUNDLE_AUDIT]} · 개별 감사 {count[SINGLE_AUDIT]} · 승인 변경 감사 {count[APPROVED_AUDIT]} · "
          f"red {count[RED]}) · 자동 초록 0 · 바뀐 경로 {len(changed)} · 대응(쌍 {len(maps.pairs)} · 디렉터리 {len(maps.dirs)} · "
          f"모듈 {len(maps.mm)} · 정의 {len(maps.dm)} · 개명 {len(maps.rn)}) · {migration_text} · "
          f"머지 제외 {len(merged)}경로 · 판정 {len(closes)}회째")
    return 2 if reds else 0


def structure_key(case: str) -> str:
    """입장 행 `경로::케이스` → G0 유지 구조 키 `rel::cls::func` — 늘 세 조각(모듈 함수의 cls 는 빈 글 — behavior_support 가
    None 으로 읽는다 · 중첩 클래스는 점으로 잇는다)."""
    rel, _sep, rest = case.partition("::")
    parts: "list[str]" = rest.split("::")
    return f"{rel}::{'.'.join(parts[:-1])}::{parts[-1]}"


def required_verdicts(d: Disposition) -> "list[tuple[str, ...]]":
    """키마다 받는 판정(`다름` 은 언제나 red) — 0T update 행 승인 키 = `승인 후와 같음` · `기대 의미 그대로` 둘 다(정오 4) ·
    승인 원소가 든 단위(승인 원소 실행 흔적이 있는 케이스의 최상위 단위 · 그런 파일의 `<file>`) = `승인 후와 같음` 만 ·
    그 밖 단위 = `기대 의미 그대로` 만(설계 :577 · :598)."""
    if d.update_rows:
        return [(APPROVED_SAME, MEANING_SAME)] * len(d.keys)
    units: "set[str]" = {case.split("::")[1] for case, hit in d.hits.items()
                         if (hit.get("old") or hit.get("add")) and case.partition("::")[0] in (d.path, d.source)}
    return [(APPROVED_SAME,) if units and (unit in units or unit == "<file>") else (MEANING_SAME,) for unit, _b, _a in d.keys]


def _approved_unseen_notes(d: Disposition) -> "list[str]":
    return [part for part in d.reason.split(" · ") if part.startswith("승인 변경 미검출")]


# 감사 요청 파일(§4-4 요구 키 · §4-6 묶음과 자료 — 기계 기록)

def _fence(*texts: str) -> str:
    longest: int = max([len(m) for t in texts for m in re.findall(r"`+", t)] or [0])
    return "`" * max(3, longest + 1)


def _show_unit(data: "bytes | None", unit: str) -> str:
    """감사자에게 보이는 단위 원문 — `<module>` 은 정의 자리 표시를 `⟪def 이름⟫` 줄로."""
    if data is None:
        return "(없음)"
    if unit == "<file>":
        return data.decode("utf-8", "surrogateescape")
    split, _why = audit_split(data)
    if split is None:
        return data.decode("utf-8", "surrogateescape")
    if unit == "<module>":
        return "".join(f"⟪def {part['정의']}⟫\n" if isinstance(part, dict) else part for part in split.module)
    body: "bytes | None" = split.defs.get(unit)
    return "(없음)" if body is None else body.decode("utf-8", "surrogateescape")


def _mentions(text: str, needle: str) -> bool:
    if needle.isidentifier():
        return re.search(rf"(?<![{IDENT}]){re.escape(needle)}(?![{IDENT}])", text) is not None
    return needle in text


def _string_constants(files_now: "list[str]", read_now: Reader,
                      is_test: "Callable[[str], bool]") -> "list[tuple[str, int, str]]":
    """시험 쪽 모든 .py(바뀌지 않은 파일 · conftest 포함)의 문자열 상수 (파일, 줄, 값)."""
    out: "list[tuple[str, int, str]]" = []
    for p in files_now:
        if not (p.endswith(".py") and is_test(p)):
            continue
        tree = _parse(_py_source(read_now(p)))
        out += [(p, node.lineno, node.value) for node in (ast.walk(tree) if tree is not None else [])
                if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    return out


def _old_name_spots(items: "tuple[str, ...]", constants: "list[tuple[str, int, str]]") -> "list[str]":
    """옛 이름 · 옛 점 경로 · 옛 파일 경로가 시험 쪽 문자열 상수에 나오는 `파일:줄`.
    판정에 쓰지 않는다 — 동적으로 만든 이름은 빠질 수 있다(감사자가 볼 자리를 좁히는 자료)."""
    needles: "set[str]" = set()
    for item in items:
        old: str = item.partition(" → ")[0]
        stem: str = old.removesuffix(".py")
        if "/" in old:
            needles |= {old, stem.replace("/", "."), stem.rpartition("/")[2]}
        else:
            needles |= {old, old.rpartition(".")[2], old.replace(".", "/")}
    ordered: "list[str]" = sorted(x for x in needles if x)
    out: "set[str]" = {f"{p}:{line} «{needle}»" for p, line, value in constants for needle in ordered
                       if _mentions(value, needle)}
    return sorted(out)


def _audit_request_text(run: str, n: int, label: str, round_no: int, disps: "list[Disposition]",
                        key_of: "Callable[[Disposition, tuple[str, str, str]], str]", read_then: Reader, read_now: Reader,
                        files_now: "list[str]", is_test: "Callable[[str], bool]",
                        approved: "dict[str, dict]") -> "tuple[str, dict[str, str]]":
    """(감사 요청 본문, 곁 파일 {이름: 본문}) — 옛 이름 문자열 자리가 SPOT_LIMIT 를 넘으면 전체 목록을 곁 파일로."""
    audited: "list[Disposition]" = [d for d in disps if d.disposition != RED]
    side: "dict[str, str]" = {}
    bundles: "dict[tuple[str, ...], list[Disposition]]" = collections.defaultdict(list)
    texts: "list[Disposition]" = []
    singles: "list[Disposition]" = []
    approved_files: "list[Disposition]" = []
    for d in audited:
        if d.disposition == APPROVED_AUDIT:
            approved_files.append(d)
        elif d.disposition == BUNDLE_AUDIT:
            bundles[bundle_rules(d.touched)].append(d)
        elif d.text_only:
            texts.append(d)
        else:
            singles.append(d)
    count = collections.Counter(d.disposition for d in disps)
    constants: "list[tuple[str, int, str]]" = _string_constants(files_now, read_now, is_test) if bundles else []
    lines: "list[str]" = [
        f"# 감사 요청 w{n} · 실행 {run} · 창 {label} · close {round_no}회째(기계 기록 — behavior_guard.py close)", "",
        f"- 요구 키 {sum(len(d.keys) for d in audited)} · 파일 묶음 감사 {count[BUNDLE_AUDIT]} · 개별 감사 {count[SINGLE_AUDIT]} · "
        f"승인 변경 감사 {count[APPROVED_AUDIT]} · red {count[RED]}",
        f"- 감사 기록 판형: `<산출물 폴더>/audit-tests-w{n}-<회차>.md` — 요구 키마다 정확히 한 행 "
        "`<키 그대로> | 판정 = <값> | <근거 한 구>` — `<값>` 은 그 키 줄의 «요구 판정» 가운데 하나 또는 `다름`, 판정 칸은 하나만"
        "(키 행 생략 불가 · 묶음 안 키 행은 근거 칸에 `묶음 B<k> 근거` 를 쓸 수 있다 · 다시 close 해 키가 바뀌면 그 키만 다시 감사한다)",
        "- 묶음은 표시 순서일 뿐 판정이 아니다. 체크리스트: ⓐ 개명 · 이동된 이름이 관찰되는 자리(아래 «옛 이름 · 경로 문자열 자리»부터) · "
        "ⓑ import 바인딩 · ⓒ 옮긴 파일(conftest · 패키지 자리) · ⓓ D 사유 단위 · ⓕ `<file>` 키의 순서 의미 · ⓔ v4 체크리스트", ""]

    def key_lines(d: Disposition) -> "list[str]":
        head: str = f"- 파일 `{d.path}`" + (f" ← `{d.source}`" if d.source != d.path else "") + \
            f" · {d.disposition} · {d.reason}" + (f" · `<file>` 갈래 {d.file_reason}" if d.file_reason else "")
        vs_of: "dict[str, list[str]]" = {}
        for case, entry in approved.items():
            if case.partition("::")[0] in (d.path, d.source):
                vs_of.setdefault(case.split("::")[1], []).extend(entry.get("V", []))
        out: "list[str]" = [head]
        for unit, allowed_verdicts in zip(d.keys, required_verdicts(d)):
            note: str = ""
            if d.update_rows:
                note = "(0T update 행이 승인한 범위 안이면 승인 후와 같음) — " + " ; ".join(f"0T update 행 — {r}" for r in d.update_rows)
            elif allowed_verdicts == (APPROVED_SAME,):
                vs: "list[str]" = sorted({v for u, ids in vs_of.items() if u == unit[0] or unit[0] == "<file>" for v in ids})
                note = f"(후 = {' · '.join(vs)})" if vs else "(후 = 승인 V)"
            out.append(f"  - `{key_of(d, unit)}` — 요구 판정: {' · '.join(allowed_verdicts)}{note}")
        return out

    for k, (rules, group) in enumerate(sorted(bundles.items()), 1):
        items: "list[str]" = sorted({t for d in group for t in d.touched})
        d_total: int = sum(sum(d.d_reasons.values()) for d in group)
        lines += [f"## 대응표 묶음 B{k} — {' ; '.join(rules)}", "",
                  f"- 줄인 대응표 항목: {' · '.join(items)}",
                  f"- 파일 {len(group)} · 단위 {sum(len(d.keys) for d in group)} · D 사유 {d_total}", ""]
        for d in group:
            lines += key_lines(d)
        spots: "list[str]" = _old_name_spots(tuple(items), constants)
        shown: "list[str]" = spots[:SPOT_LIMIT]
        lines += ["", f"### 옛 이름 · 경로 문자열 자리(묶음 B{k} · 판정에 쓰지 않음 · 총 {len(spots)}곳"
                  + (f" · 여기 {len(shown)}곳 · 생략 {len(spots) - len(shown)}곳 — 전체 목록 `w{n}-audit-spots-B{k}.txt`"
                     "(이 파일 곁)" if len(spots) > len(shown) else "") + ")", ""]
        lines += [f"- {s}" for s in shown] or ["- (없음)"]
        if len(spots) > len(shown):
            side[f"w{n}-audit-spots-B{k}.txt"] = "\n".join(spots) + "\n"
        lines.append("")
    if texts:
        lines += ["## 글 묶음(docstring · `#` 주석 · 빈 줄만)", ""]
        for d in texts:
            lines += key_lines(d)
        lines.append("")
    if singles:
        lines += ["## 개별", ""]
        for d in singles:
            lines += key_lines(d)
        lines.append("")
    if approved_files:
        lines += ["## 승인 변경(승인 원소 단위는 «승인 후와 같음» 만 — «기대 의미 그대로»면 승인 변경 미검출(V 를 지우고 0F 로 · G1′) · "
                  "그 밖 단위는 «기대 의미 그대로» 만)", ""]
        for d in approved_files:
            lines += key_lines(d)
        lines.append("")
    lines += ["# 자료", ""]
    for d in audited:
        before: "bytes | None" = read_then(d.source)
        after: "bytes | None" = read_now(d.path)
        old_lines: "list[str]" = _LINE_TEXT.findall((before or b"").decode("utf-8", "surrogateescape"))
        new_lines: "list[str]" = _LINE_TEXT.findall((after or b"").decode("utf-8", "surrogateescape"))
        diff: str = "".join(ln if ln.endswith(("\n", "\r")) else ln + "\n" for ln in difflib.unified_diff(
            old_lines, new_lines, fromfile=f"a/{d.source}", tofile=f"b/{d.path}"))
        fence: str = _fence(diff)
        lines += [f"## `{d.path}`" + (f" ← `{d.source}`" if d.source != d.path else ""), "", "### diff", "",
                  f"{fence}diff", diff.rstrip("\n") or "(바이트 차이만 — 줄 diff 없음)", fence, ""]
        for unit, _b, _a in d.keys:
            shown_before, shown_after = _show_unit(before, unit), _show_unit(after, unit)   # `<file>` 은 파일 원문 전체
            fence = _fence(shown_before, shown_after)
            lines += [f"### 단위 `{unit}` 전", "", fence, shown_before.rstrip("\n"), fence, "",
                      f"### 단위 `{unit}` 후", "", fence, shown_after.rstrip("\n"), fence, ""]
    return "\n".join(lines).rstrip() + "\n", side


# 감사 기록 일대일 대조(§4-4 · verify)

class AuditRow(NamedTuple):
    prefix: str
    file: str
    unit: str
    before: str
    after: str
    verdict: str
    problem: str = ""      # 판정 형식 밖(판정 값 칸이 둘 이상 — 판형 줄을 베낀 행) — 비어 있으면 형식 안


_KEY_IN_LINE: "re.Pattern[str]" = re.compile(
    r"([^\s`|]+/w\d+) · (.+?) · ([^·|`]+?) · 전 ([0-9a-f]{12}|없음) · 후 ([0-9a-f]{12}|없음)(?![0-9a-f])")


def parse_audit_key(text: str) -> "tuple[str, str, str, str, str] | None":
    """`<실행 값>/w<n> · <파일> · <단위> · 전 <digest> · 후 <digest>` → (접두, 파일, 단위, 전, 후) — digest 는 12자 hex 또는
    `없음`(뒤에 다른 글이 붙으면 키가 아니다)."""
    parts: "list[str]" = text.strip().strip("`").strip().split(" · ")
    if len(parts) < 5 or not re.fullmatch(r"\S+/w\d+", parts[0]) or not parts[-2].startswith("전 ") \
            or not parts[-1].startswith("후 "):
        return None
    before, after = parts[-2][2:].strip(), parts[-1][2:].strip()
    if not all(re.fullmatch(r"[0-9a-f]{12}|없음", d) for d in (before, after)):
        return None
    return parts[0], " · ".join(parts[1:-3]), parts[-3], before, after


def audit_rows(text: str) -> "list[AuditRow]":
    """감사 기록 한 회차의 키 행 — `<키 그대로> | 판정 = <값> | <근거>`(앞 `- ` · `| ` 허용 · 키는 백틱 허용).

    `<값>` 은 닫힌 셋 가운데 정확히 하나다. 판정 칸 밖에 닫힌 셋 값과 글자가 같은 칸(앞뒤 공백 · 꾸밈 글자 걷음)이나 `판정 =` 칸이
    또 있으면 «판정 형식 밖»이다 — 판형 줄 `… | 판정 = 기대 의미 그대로 | 승인 후와 같음 | 다름 | 근거` 를 그대로 베낀 행이 첫 값으로
    통과하지 않게 한다. 근거 글 안에 판정 낱말이 섞인 것은 형식 안이다.

    키 행이 아닌 줄(구분자 `|` 가 없거나 첫 칸이 키 그대로가 아님)에 감사 키가 들어 있으면 그 키의 미판정 행으로 남긴다 — 최신
    회차의 미판정 줄이 앞 회차의 정상 판정을 되살리지 않게(형식 밖과 같은 «다름»)."""
    rows: "list[AuditRow]" = []
    for raw in text.splitlines():
        line: str = re.sub(r"^(?:[-*]\s+|\|\s*)", "", raw.strip())
        cells: "list[str]" = [c.strip() for c in line.split("|")]
        key = parse_audit_key(cells[0]) if "|" in line else None
        if key is None:
            rows += [AuditRow(*m.groups(), "", "판정 칸 · 구분자 없는 키 줄(미판정)") for m in _KEY_IN_LINE.finditer(line)]
            continue
        rest: "list[str]" = cells[1:]
        at: "int | None" = next((i for i, c in enumerate(rest) if re.match(r"판정\s*=", c)), None)
        verdict: str = "" if at is None else re.sub(r"^판정\s*=\s*", "", rest[at]).strip()
        extra: "list[str]" = [c for i, c in enumerate(rest)
                              if i != at and (c.strip("`*_ ") in AUDIT_VERDICTS or re.match(r"판정\s*=", c))]
        problem: str = "판정 값 칸이 둘 이상(" + " | ".join(extra) + ")" if extra else "" if at is not None else "판정 칸 없음(미판정)"
        rows.append(AuditRow(*key, verdict, problem))
    return rows


def match_audit(required: "list[str]", rounds: "list[list[AuditRow]]", prefix: str,
                allowed: "dict[str, tuple[str, ...]]") -> "tuple[int, collections.Counter[str], list[str]]":
    """(일치 수, 어긋남 갈래 수, 상세) — 갈래: 중복(한 회차에 같은 파일 · 단위 둘 이상) · 누락 · 추가(마지막 회차의 요구 밖 키) ·
    낡음(같은 파일 · 단위인데 전/후 digest 다름) · 다름(판정 `다름` · 닫힌 셋 밖 · 판정 형식 밖 · 미판정 · 그 키의 요구 판정 밖 —
    `allowed` = 키 → 받는 판정(없으면 `기대 의미 그대로` 만) · 승인 원소 단위의 `기대 의미 그대로` 는 승인 변경 미검출).
    파일 · 단위마다 그것을 적은 가장 늦은 회차의 행이 유효하다(다시 close 해 바뀐 키만 다시 감사한다)."""
    counts: "collections.Counter[str]" = collections.Counter({k: 0 for k in ("중복", "누락", "추가", "낡음", "다름")})
    details: "list[str]" = []
    req: "dict[tuple[str, str], tuple[str, str, str]]" = {}
    for key in required:
        parsed = parse_audit_key(key)
        if parsed is not None:
            req[(parsed[1], parsed[2])] = (parsed[3], parsed[4], key)
    effective: "dict[tuple[str, str], AuditRow]" = {}
    for rows in rounds:
        seen = collections.Counter((r.file, r.unit) for r in rows)
        for (f, u), k in seen.items():
            if k > 1:
                counts["중복"] += k - 1
                details.append(f"중복 {f} · {u} ×{k}")
        for r in rows:
            effective[(r.file, r.unit)] = r
    for r in (rounds[-1] if rounds else []):
        if (r.file, r.unit) not in req or r.prefix != prefix:
            counts["추가"] += 1
            details.append(f"추가 {r.prefix} · {r.file} · {r.unit}")
    matched: int = 0
    for (f, u), (before, after, key) in req.items():
        row = effective.get((f, u))
        if row is None or row.prefix != prefix:
            counts["누락"] += 1
            details.append(f"누락 {key}")
        elif (row.before, row.after) != (before, after):
            counts["낡음"] += 1
            details.append(f"낡음 {f} · {u}(기록 전 {row.before} · 후 {row.after} ≠ 요구 전 {before} · 후 {after})")
        elif row.problem or row.verdict not in AUDIT_VERDICTS or row.verdict == "다름":
            counts["다름"] += 1
            details.append(f"다름 {f} · {u}(" + (f"판정 형식 밖 — {row.problem}" if row.problem
                                               else f"판정 = {row.verdict or '없음'}") + ")")
        elif row.verdict not in allowed.get(key, (MEANING_SAME,)):
            counts["다름"] += 1
            wanted: "tuple[str, ...]" = allowed.get(key, (MEANING_SAME,))
            details.append(f"다름 {f} · {u}(" + ("승인 변경 미검출 — 승인 원소 단위가 «기대 의미 그대로»: V 를 지우고 0F 로(G1′)"
                                               if wanted == (APPROVED_SAME,) and row.verdict == MEANING_SAME
                                               else f"판정 = {row.verdict} · 요구 판정 {' · '.join(wanted)}") + ")")
        else:
            matched += 1
    return matched, counts, details


def _audit_rounds(folder: Path, n: int) -> "list[list[AuditRow]]":
    files: "list[tuple[int, Path]]" = []
    for f in folder.glob(f"audit-tests-w{n}-*.md"):
        m = re.fullmatch(rf"audit-tests-w{n}-(\d+)\.md", f.name)
        if m:
            files.append((int(m.group(1)), f))
    return [audit_rows(f.read_text(encoding="utf-8")) for _r, f in sorted(files)]


# ── verify ───────────────────────────────────────────────────────────────────

def cmd_verify(folder: Path, repo: Path) -> int:
    if not folder.is_dir():
        raise RunError(f"산출물 폴더가 없다 — {folder}")
    if _folder_is_refactor(folder):
        return _verify_refactor(folder, repo)
    scope: Path = folder / "refactor-scope.md"
    text: str = scope.read_text(encoding="utf-8") if scope.is_file() else ""
    current: str = re.split(r"(?m)^#+\s*앞 실행", text)[0]
    has_a: bool = bool(re.search(r"결정 = ⓐ(?!′)", current))
    reconsidered: bool = "ⓐ 재상정" in current
    windows = _windows(_run_dir(folder)) if scope.is_file() else []
    opened_now = [n for n, _o, c in windows if _is_open(c)]
    kinds = collections.Counter("0T" if o["kind"] == "test" else "0C" for _n, o, _c in windows)
    detail: str = f"창 {len(windows)}(0T {kinds['0T']} · 0C {kinds['0C']}) · 열린 창 {len(opened_now)}"
    if opened_now:
        print(f"  red: 열린 창 {', '.join(f'w{n}' for n in opened_now)} — close 가 green 이 아니다(철회 뒤 close 재실행)")
        print(f"요약: 동작 보존 red · {detail}")
        return 2
    if has_a and not windows and not reconsidered:
        print("  red: 창 누락 — 이번 실행에 `결정 = ⓐ` 줄이 있는데 동작 보존 창이 하나도 없다")
        print(f"요약: 동작 보존 red · {detail}")
        return 2
    if not windows:
        print(f"요약: 동작 보존 해당 없음 · 슬라이스 0 창 없음{'(ⓐ 재상정)' if has_a else ''}")
        return 0
    print(f"요약: 동작 보존 green · {detail}")
    return 0


def _suite_lines(record: "dict | None", confirmed: "tuple[str, str, str] | None", last_close_fp: "str | None",
                 now_fp: str) -> "tuple[list[str], str]":
    """(red 사유, `suite:` 행) — 마지막 suite 기록(behavior_support · k0 §4-4)의 판정 · exit · 양 확인 · G1 결속 · 지문 다섯."""
    if record is None:
        return ["suite 기록 없음 — `behavior_guard.py suite <폴더>` 를 마지막 close 뒤에 돈다"], "suite: 기록 없음"
    try:
        counts: dict = record["counts"]
        commands: "list[dict]" = record["commands"]
        prints: dict = record["fingerprints"]
        g1: dict = record["g1"]
        run_digest: str = record["run_definition_digest"]
        reds: "list[str]" = []
        if record.get("verdict") != "green":
            reds.append(f"suite 판정 {record.get('verdict')}")
        reds += [f"suite 사유: {r}" for r in record.get("reasons", [])]
        bound: bool = run_digest == g1.get("run_definition_digest") and (
            confirmed is None or (g1.get("digest"), g1.get("candidate")) == (confirmed[1], confirmed[2]))
        if not bound:
            reds.append(f"suite 의 실행 정의 {run_digest} · G1 {g1.get('digest')}/{g1.get('candidate')} 이 G1 결속"
                        f"({confirmed[1] if confirmed else '없음'}/{confirmed[2] if confirmed else '없음'})과 다르다")
        exits_ok: bool = bool(commands) and all(c.get("exit") == 0 and c.get("probe_exit") == c.get("exit") for c in commands)
        if not exits_ok or counts["commands"] != len(commands):
            reds.append("suite 명령 exit · 탐침 exit · 명령 수가 맞지 않는다")
        ready: int = sum(int(c.get("workers_ready", 0)) for c in commands)
        outputs: int = sum(int(c.get("worker_outputs", 0)) for c in commands)
        zero: "dict[str, str]" = {"failed": "실패 보고", "optimize": "최적화", "reentry": "감시 구간 재진입", "anchor": "정의 자리 밖",
                                  "suspend": "일시 중단 본문", "observer_hits": "실행 관찰 API", "nolist": "허용 목록 밖",
                                  "unresolved": "원본 못 찾음", "late": "확정 뒤 등록"}
        reds += [f"suite {label} {counts[k]}" for k, label in zero.items() if counts[k] != 0]
        selected, collected = counts["selected"], counts["collected"]
        if selected != collected:
            reds.append(f"suite 선택 합 {selected} ≠ 수집 합 {collected}")
        if counts["calls"] + counts["skips"] < selected or counts["complete"] < selected:
            reds.append(f"suite 처분(call {counts['calls']} · skip {counts['skips']}) · 완료 {counts['complete']} 가 선택 {selected} 를 "
                        "덮지 못한다")
        if counts["proof_ok"] != counts["proof_total"]:
            reds.append(f"suite 결과 증거 {counts['proof_ok']}/{counts['proof_total']}")
        if ready != outputs:
            reds.append(f"suite xdist 일꾼 출력 {outputs}/{ready}")
        g0_keep: "list[str]" = list(record.get("g0_keep", []))
        reds += [f"suite G0 유지: {x}" for x in g0_keep]
        chain: "list[str | None]" = [prints["start"], *prints["between"], prints["end"], now_fp]
        if last_close_fp is not None:
            chain.insert(0, last_close_fp)
        same: bool = len(set(chain)) == 1 and None not in chain
        if not same:
            only_close: bool = last_close_fp is not None and None not in chain and len(set(chain[1:])) == 1
            reds.append(f"지문 다름(마지막 close {last_close_fp} · 시작 {prints['start']} · 명령 사이 {prints['between']} · "
                        f"끝 {prints['end']} · 지금 {now_fp}) — 그 suite 기록은 폐기다(다시 돈다)"
                        + (" — 마지막 창 close 뒤에 커밋 · 편집이 있었다: 그 창 close 를 다시 돌린 뒤 suite 를 다시 돈다"
                           if only_close else ""))
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        return [f"suite 기록 판형 어긋남 — {type(exc).__name__}: {exc}"], "suite: 기록 판형 어긋남"
    eq = lambda ok: "=" if ok else "≠"  # noqa: E731
    line: str = (
        f"suite: 실행 정의 {run_digest} {eq(bound)} G1 결속 · 명령 {len(commands)} 모두 exit 0 {eq(exits_ok)} 탐침 exit · "
        f"실패 보고 {counts['failed']}(일꾼 포함 합) · 최적화 {counts['optimize']} · "
        f"선택 합 {eq(selected == collected)} 수집 합 {collected} · 선택 {selected} ⊆ 처분(call {counts['calls']} · "
        f"skip {counts['skips']}) · 완료 {counts['complete']} · 결과 증거 {counts['proof_ok']}/{counts['proof_total']}(passed call "
        "마다 call 실행 맥락의 시작 = 정상 반환 ≥ 1 · 맥락 밖 사건 0) · "
        f"감시 구간 재진입 {counts['reentry']}(보고 무관) · 정의 자리 밖 {counts['anchor']} · 일시 중단 본문 {counts['suspend']} · "
        f"실행 관찰 API {counts['observer_hits']}(정적 · 위험 모듈 허용 목록 · 파일 {counts['observer_files']}) · "
        f"허용 목록 밖 {counts['nolist']}(프로젝트 훅 {counts['hooks']} 개 모두 목록 안) · 원본 못 찾음 {counts['unresolved']} · "
        f"확정 뒤 등록 {counts['late']} · 시험 기계 파일 {counts['M']} ⊆ 시험 쪽 · xdist 일꾼 출력 {outputs}/{ready} · "
        f"G0 유지(구조 키 — 파일 · 바이트 같은 항목 · 바뀐 파일 함수마다 처분 수{f' — 어긋남 {len(g0_keep)}' if g0_keep else ''}) · "
        f"지문 마지막 close {eq(same)} 시작 = 명령 사이 = 끝 = 지금")
    return reds, line


def _verify_refactor(folder: Path, repo: Path) -> int:
    """리팩토링 모드 verify(§3-6 · §4-5) — `동작 보존:` · `바뀐 것 실행:` · `suite:` 세 줄과 `요약:`. 하나라도 어긋나면 red."""
    scope: Path = folder / "refactor-scope.md"
    text: str = scope.read_text(encoding="utf-8") if scope.is_file() else ""
    current: str = re.split(r"(?m)^#+\s*앞 실행", text)[0]
    has_a: bool = bool(re.search(r"결정 = ⓐ(?!′)", current))
    reconsidered: bool = "ⓐ 재상정" in current
    windows = _windows(_run_dir(folder)) if scope.is_file() else []
    for _n, o, _c in windows:
        _window_mode(folder, o)
    reds: "list[str]" = []
    open_now: "list[int]" = [n for n, _o, c in windows if _is_open(c)]
    if open_now:
        reds.append(f"열린 창 {', '.join(f'w{n}' for n in open_now)} — 마지막 close 가 red 거나 없다")
    if has_a and not windows and not reconsidered:
        reds.append("창 누락 — 이번 실행에 `결정 = ⓐ` 줄이 있는데 동작 보존 창이 하나도 없다")
    kinds = collections.Counter(o["kind"] for _n, o, _c in windows)
    units: "collections.Counter[str]" = collections.Counter()
    bundles: "set[tuple[int, tuple[str, ...]]]" = set()
    auto_green: int = 0
    red_items: int = 0
    matched_total: int = 0
    required_total: int = 0
    mismatch: "collections.Counter[str]" = collections.Counter({k: 0 for k in ("중복", "누락", "추가", "낡음", "다름")})
    last_close_fp: "str | None" = None
    for n, o, closes in windows:
        if not closes:
            continue
        last: dict = closes[-1]
        last_close_fp = last.get("fingerprint_end")
        red_items += len(last.get("reds", []))
        allowed: "dict[str, tuple[str, ...]]" = {}
        covered: "set[str]" = set()
        for d in last.get("dispositions", []):
            covered |= {d["path"], d.get("from") or d["path"]}
            if d["처분"] == RED:
                continue
            if not d.get("keys"):
                auto_green += 1
                continue
            units[d["처분"]] += len(d["keys"])
            if d["처분"] == BUNDLE_AUDIT and d.get("묶음"):
                bundles.add((n, tuple(d["묶음"])))
            for key, wanted in zip(d["keys"], d.get("요구 판정", [])):          # 키마다 받는 판정(close 가 남김)
                allowed[key] = tuple(wanted.split(" · "))
        bare: "list[str]" = sorted(set(last.get("test_changed", [])) - covered)  # 처분 없이 지나간 바뀐 시험 쪽 경로
        auto_green += len(bare)
        reds += [f"w{n} 처분 없는 바뀐 시험 쪽 경로 {p}" for p in bare]
        required: "list[str]" = list(last.get("keys", []))
        matched, counts, details = match_audit(required, _audit_rounds(folder, n), f"{o['run']}/w{n}", allowed)
        matched_total += matched
        required_total += len(required)
        mismatch.update(counts)
        reds += [f"감사 키 w{n} {x}" for x in details]
    if auto_green:
        reds.append(f"자동 초록 {auto_green} — 키 없이 처분됐거나 처분 없이 지나간 시험 쪽 파일")
    line_keep: str = (
        f"동작 보존: 창 {len(windows)}(0T {kinds['test']} · 0C {kinds['code']} · 0F {kinds['follow']} · 변경 {kinds['change']}) · "
        f"열린 창 {len(open_now)} · 시험 쪽 바뀐 단위 — 묶음 감사 {units[BUNDLE_AUDIT]}(묶음 {len(bundles)}) · "
        f"개별 감사 {units[SINGLE_AUDIT]} · 승인 변경 {units[APPROVED_AUDIT]} · red {red_items} · 자동 초록 {auto_green} · "
        f"감사 키 일치 {matched_total}/{required_total}(" + " · ".join(f"{k} {mismatch[k]}" for k in ("중복", "누락", "추가", "낡음", "다름"))
        + ")")
    ra = _audit_module()
    confirmed = _external("refactor_audit.g1_confirmed", ra.g1_confirmed, folder)
    if confirmed is None:
        reds.append("`G1 변경판 확정` 줄 없음 — 바뀐 것 실행을 대조할 기준이 없다")
        line_change: str = "바뀐 것 실행: G1 변경판 확정 없음"
    else:
        snap = _external("refactor_audit.changes_snapshot", ra.changes_snapshot, folder, repo)
        digest: str = str(_external("refactor_audit.snapshot_digest", ra.snapshot_digest, snap))
        bound = [o.get("g1_digest") for _n, o, _c in windows if o["kind"] in ("follow", "change")]
        digest_ok: bool = digest == confirmed[1] and (not bound or bound[-1] == confirmed[1])
        if not digest_ok:
            reds.append(f"명세 승인판 digest {digest} · 마지막 창 결속 {bound[-1] if bound else '없음'} ≠ G1 변경판 확정 {confirmed[1]}")
        allow: dict = allow_table(snap)  # type: ignore[arg-type]
        approved_ops = collections.Counter(allow["ops"])
        generated: "collections.Counter[str]" = collections.Counter()
        seen_old: "dict[str, set[str]]" = collections.defaultdict(set)
        seen_add: "collections.Counter[str]" = collections.Counter()
        existing: int = 0
        outside: int = 0
        for _n, o, closes in windows:
            if not closes:
                continue
            last = closes[-1]
            existing += len(last.get("existing_migrations", []))
            outside += len(last.get("outside_bc", []))
            if o["kind"] == "change":
                generated.update(last.get("ops", []))
            for case, hit in last.get("approved_hits", {}).items():
                seen_old[case].update(hit.get("old", []))
                seen_add[case] += int(hit.get("add", 0))
        expected: int = 0
        changed_count: int = 0
        for case, entry in allow["approved_cases"].items():
            olds: "list[str]" = entry.get("expect_old", [])
            adds: int = int(entry.get("expect_add", 0))
            expected += len(olds) + adds
            changed_count += sum(1 for t in olds if t in seen_old.get(case, set())) + min(adds, seen_add[case])
        if generated != approved_ops:
            missing, extra = approved_ops - generated, generated - approved_ops
            reds.append(f"연산 승인 {sum(approved_ops.values())} ≠ 생성 {sum(generated.values())}(다중집합 — 실행 흔적 없음 "
                        f"{sum(missing.values())} · 승인 밖 {sum(extra.values())})")
        if changed_count < expected:
            reds.append(f"승인 기대 원소 {expected} 중 변경 {changed_count} — 실행 흔적 없음 {expected - changed_count}")
        line_change = (f"바뀐 것 실행: 승인 V {len(allow['V'])}건 · 연산 승인 {sum(approved_ops.values())} "
                       f"{'=' if generated == approved_ops else '≠'} 생성 {sum(generated.values())}(다중집합) · "
                       f"기존 마이그레이션 변경 {existing} · 승인 기대 원소 {expected} 중 변경 {changed_count} · "
                       f"목록 밖 다른 BC 파일 {outside} · digest {confirmed[1]} {'=' if digest_ok else '≠'} G1 변경판 확정")
    bs = _support_module()
    record = _external("behavior_support.latest_suite_record", bs.latest_suite_record, folder)
    now_fp: str = str(_external("behavior_support.fingerprint", bs.fingerprint, repo))
    suite_reds, line_suite = _suite_lines(record, confirmed, last_close_fp, now_fp)  # type: ignore[arg-type]
    reds += suite_reds
    for r in reds:
        print(f"  red: {r}")
    print(line_keep)
    print(line_change)
    print(line_suite)
    print(f"요약: 동작 보존 {'red' if reds else 'green'} · {line_keep.removeprefix('동작 보존: ')}")
    return 2 if reds else 0


# ── rebind · support · suite ─────────────────────────────────────────────────

def cmd_rebind(folder: Path, repo: Path) -> int:
    """열린 follow · change 창의 허용 표만 새 G1 변경판으로 — 창 기준(head0 · dirty0 · 케이스 · 마이그레이션 측정)은 그대로."""
    _anchor(folder)
    run_dir: Path = _run_dir(folder)
    windows = _closable(run_dir)
    if not windows:
        raise RunError("열린 창이 없다 — rebind 는 열린 follow · change 창에서만 쓴다")
    n, opened, _closes = windows[-1]
    if _window_mode(folder, opened) != "refactor" or opened["kind"] not in ("follow", "change"):
        raise RunError(f"창 w{n} 은 follow · change 창이 아니다 — rebind 할 허용 표가 없다")
    digest, allow = _g1_binding(folder, repo)
    previous: str = opened["g1_digest"]
    if digest == previous:
        raise RunError(f"새 `G1 변경판 확정` 이 없다 — 창 결속 digest {previous} 와 같다")
    opened.setdefault("rebinds", []).append({"at": _now(), "from": previous, "to": digest})
    opened["g1_digest"] = digest
    opened["allow"] = allow
    _dump(run_dir / f"w{n}-open.json", opened)
    print(f"요약: 창 w{n} rebind · 종류 {KIND_LABELS[opened['kind']]} · G1 digest {previous} → {digest} · 창 기준(HEAD "
          f"{opened['head'][:12]} · dirty {len(opened['dirty'])}) 그대로 · rebind {len(opened['rebinds'])}회째")
    return 0


def cmd_support(folder: Path, repo: Path) -> int:
    """G0 지원 확인(설계 §4-5 · 정오 3) — 본체는 behavior_support.cmd_support."""
    bs = _support_module()
    return int(_external("behavior_support.cmd_support", bs.cmd_support, folder, repo))  # type: ignore[arg-type]


def cmd_suite(folder: Path, repo: Path) -> int:
    """G2 증거 실행(설계 §4-5) — 본체는 behavior_support.cmd_suite."""
    bs = _support_module()
    return int(_external("behavior_support.cmd_suite", bs.cmd_suite, folder, repo))  # type: ignore[arg-type]


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(prog="behavior_guard.py", description="동작 보존 창 판정 — 기능 모드 0T·0C(테스트 고정·마이그레이션 무변) · 리팩토링 모드 0T·0C·0F·변경(시험 쪽 처분·감사 키)")
    ap.add_argument("command", choices=("open", "close", "verify", "rebind", "support", "suite"))
    ap.add_argument("folder", help="산출물 폴더(.dddjango/<prefix>-<slug>)")
    ap.add_argument("--kind", choices=KINDS, help="open 전용 — 0T(test) | 0C(code) | 0F(follow) | 변경 슬라이스(change)")
    ap.add_argument("--mode", choices=MODES, help="open 전용 · 필수 — refactor | feature(open 기록에 동결)")
    ap.add_argument("--collect", action="store_true", help="support 전용 — G0 수집 지원 확인")
    ap.add_argument("--repo", default=".", help="저장소 루트(기본 .)")
    ap.add_argument("--python", default=None, help="마이그레이션 동적 측정 인터프리터(기본: 저장소 .venv/venv)")
    try:
        ns = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return 0
        print("요약: 동작 보존 실행 불능 — 인자 오류(위 사용법)")
        return 1
    if ns.python:
        PYTHON_OVERRIDE[:] = [ns.python]
    folder: Path = Path(ns.folder)
    repo: Path = Path(ns.repo).resolve()
    try:
        if ns.command == "open":
            if ns.kind is None:
                raise RunError("open 은 --kind test|code|follow|change 가 필요하다")
            return cmd_open(folder, repo, ns.kind, ns.mode or "")   # 모드가 빠지면 cmd_open 이 실행 불능으로 낸다(필수)
        if ns.command == "close":
            return cmd_close(folder, repo)
        if ns.command == "rebind":
            return cmd_rebind(folder, repo)
        if ns.command == "support":
            if not ns.collect:
                raise RunError("support 는 --collect 가 필요하다(G0 수집 지원 확인)")
            return cmd_support(folder, repo)
        if ns.command == "suite":
            return cmd_suite(folder, repo)
        return cmd_verify(folder, repo)
    except (RunError, OSError, ValueError, KeyError, RecursionError, MemoryError) as exc:
        print(f"실행 불능: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"요약: 동작 보존 {ns.command} 실행 불능 — {str(exc)[:120]}")
        return 1


if __name__ == "__main__":
    # 스크립트로 돌 때 behavior_support 의 `import behavior_guard` 가 같은 모듈을 받게 한다(두 벌 적재 — 예외 클래스 · 상태 갈림 방지).
    sys.modules.setdefault("behavior_guard", sys.modules[__name__])
    sys.exit(main(sys.argv[1:]))
