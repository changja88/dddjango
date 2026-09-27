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

사용: behavior_guard.py open <산출물 폴더> --kind test|code [--repo <저장소 루트, 기본 .>] [--python <인터프리터>]
      behavior_guard.py close <산출물 폴더> [--repo …]     — 다음 파견 전까지 몇 번이든 다시 돌린다(마지막 판정이 유효)
      behavior_guard.py verify <산출물 폴더> [--repo …]    — G2 배너 `동작 보존:` 행의 기계 출처
exit 0 = green(해당 없음 포함) · 2 = red · 1 = 실행 불능(앵커 부재 · 열린 창 · 머지 겹침 · rebase 등). 모든 경로가 `요약:` 1행을 낸다.

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
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable

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
    return not closes or closes[-1].get("verdict") != "green"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


# ── open ─────────────────────────────────────────────────────────────────────

def cmd_open(folder: Path, repo: Path, kind: str) -> int:
    anchor: str = _anchor(folder)
    run_dir: Path = _run_dir(folder)
    windows = _windows(run_dir)
    for n, _o, closes in windows:
        if _is_open(closes):
            raise RunError(f"열린 창 w{n} 이 있다 — close 가 green 이 된 뒤에 새 창을 연다")
    n = (windows[-1][0] + 1) if windows else 1
    head: str = _git(repo, "rev-parse", "--verify", "HEAD^{commit}").strip()
    dirty: "list[str]" = _dirty(repo)
    files: "list[str]" = _worktree_files(repo)
    test_dirs: "set[str]" = _test_dirs(files)
    dirty_entries: "dict[str, dict]" = {}
    for p in dirty:
        data: "bytes | None" = (repo / p).read_bytes() if (repo / p).is_file() else None
        entry: "dict[str, object]" = {"sha": _sha(data)}
        if data is not None and (p.endswith(".py") or _is_test(p, test_dirs) or p in PYTEST_FILES):
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
        "migrations_static": static, "migrations_dynamic": dynamic,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    _dump(run_dir / f"w{n}-open.json", record)
    dyn: str = (f"동적 기준 {len(dynamic['changes'])}건" if dynamic["status"] == "측정"  # type: ignore[arg-type]
                else f"동적 미측정({dynamic.get('reason')})")
    n_cases: int = sum(map(len, cases.values()))
    warn: str = " · 경고: 테스트 파일은 있는데 수집 케이스 0" if not n_cases and any(
        _is_test(p, test_dirs) and p.endswith(".py") for p in files) else ""
    print(f"요약: 창 w{n} open · 종류 {'0T' if kind == 'test' else '0C'} · HEAD {head[:12]} · dirty {len(dirty)} · "
          f"수집 테스트 {len(cases)}파일 · 케이스 {n_cases} · 마이그레이션 정적 {len(static)} · {dyn}{warn}")
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
    windows = [w for w in _windows(run_dir) if _is_open(w[2])]
    if not windows:
        raise RunError("열린 창이 없다 — open 뒤에 close 한다")
    n, opened, closes = windows[-1]
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


# ── verify ───────────────────────────────────────────────────────────────────

def cmd_verify(folder: Path, repo: Path) -> int:
    if not folder.is_dir():
        raise RunError(f"산출물 폴더가 없다 — {folder}")
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


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(prog="behavior_guard.py", description="슬라이스 0 창의 테스트 고정·마이그레이션 무변 판정")
    ap.add_argument("command", choices=("open", "close", "verify"))
    ap.add_argument("folder", help="산출물 폴더(.dddjango/<prefix>-<slug>)")
    ap.add_argument("--kind", choices=("test", "code"), help="open 전용 — 0T(test) | 0C(code)")
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
                raise RunError("open 은 --kind test|code 가 필요하다")
            return cmd_open(folder, repo, ns.kind)
        if ns.command == "close":
            return cmd_close(folder, repo)
        return cmd_verify(folder, repo)
    except (RunError, OSError, ValueError, KeyError, RecursionError, MemoryError) as exc:
        print(f"실행 불능: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"요약: 동작 보존 {ns.command} 실행 불능 — {str(exc)[:120]}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
