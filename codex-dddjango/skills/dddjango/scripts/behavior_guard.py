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
뜻 보존 시험 개명(케이스 이름 · parametrize 원소 id — 설계 3.1 §D)은 G1 승인 «개명» 행(입장 표 retain 재조직 · 스냅숏
`retain_rows[].renames`)으로만 0T · 0F 가 받는다: 그 창 기준 판에 옛 이름이 있고 새 판에 없을 때만 옛 → 새 를 기준 판에 먼저 적용하고
(AST 가 가리킨 정의 이름 · id 리터럴 자리만 바꾼 원문) 그 창의 지금 규칙(케이스 이름 · D · 0T 개별 감사 · 0F 정규형 비교)을 그대로
돈다 — 이름 밖 편집은 지금 규칙이 처분한다. 쌍마다 개별 감사 키 «개명 — 이름 뜻»(요구 판정 `기대 의미 그대로` · 감사 요청에 이름 밖
편집 있음/없음과 옛 이름 · 옛 id 글자가 시험 쪽 문자열 상수에 남은 자리)을 내고, 0C 의 개명 · 행 꼴 밖(수집 케이스 아님 — 픽스처 ·
도우미 · 중첩 클래스 메서드 · 클래스 개명 · 하위 클래스가 물려받는 메서드 · 가림(복합문 몸 · 바다코끼리 · match 캡처 · global ·
같은 파일 기반 클래스까지) · 별 import · 파일 밖 기반 클래스 · 맞바꿈 ·
합친 id · 모듈 상수 `pytest.param(id=)`) · 같은 창의 이동과 개명은 red · 어느 창에도 적용되지 않은 개명 행은 verify red 다. 0T 입장
표 update · remove 행이 개명 행의 옛 이름을 가리키면 개명 뒤 새 이름으로도 읽는다.
값 객체 칸 개명(설계 A 4판 A6 — F4-116 남은 것)은 «칸 개명» 행(`재조직 — 칸 개명 <운영 경로>::<클래스>.<옛> → <새>` · owner/path =
그 칸을 쓰는 시험 파일 하나)으로 0F 창만 받는다: 운영 클래스의 옛 칸이 그 창에서 사라졌거나 시험 파일이 그 클래스로 풀리는 옛 자리를
모두 새 이름으로 옮겼을 때 그 창 몫이고, 시험 파일 기준 판에서 그 클래스로 풀리는 호출의 키워드 `옛=` 과 받는 쪽 이름이 그 클래스로
풀리는 속성 `.옛`(지역 변수 · 매개변수 주석 · 그 클래스 호출을 대입한 이름)만 옛 → 새 로 바꾼 뒤 창 규칙을 그대로 돈다(받는 쪽을 못
풀면 그 자리는 그대로 — 기대식이면 D 확정 red). 행 꼴 밖(red): 0T · 0C 창 · 운영 클래스가 밖 계약 · DB 구조(ninja Schema · pydantic
모델 · Django Model)거나 기반을 못 풂(같은 파일 클래스 · object · NamedTuple · Generic · ABC · 가리지 않은 내장 예외 만 — 다른 파일
기반 · Enum · TypedDict · metaclass= 는 못 풂) · 운영 칸이 옛 → 새 로 정확히 바뀌지
않음 · 그 클래스로 풀리는 `.옛` · `옛=` 이 새 판에 남음 · 기준 판에 새 이름. 감사 키 `개명 칸 <클래스>.<옛> → <새>`(파일 전 · 후)를
쌍마다 내고, 케이스 키가 그대로라 G2 유지 대응(`g0_keep_exceptions.renamed`)에는 싣지 않는다 — verify 의 «적용 안 된 개명 행»
대조에는 든다. 변경 창은 개명 행을 받지 않는다(칸 개명은 0F 슬라이스로).
기능 모드는 위 0T · 0C 판정 그대로다.

알려진 사각(감수 hunk 대조 몫): 테스트만 import 하는 제품 분류 모듈(운영 CLI 와 구별 불가 — 테스트 settings·pytest 플러그인
모듈 포함) · 재수출 심을 남긴 이동의 `patch("옛.경로")` 헛돎(심만 남은 모듈은 보고) · 모듈 경로가 관찰값인 곳(로거 이름 ·
Celery 기본 태스크 이름 · pickle) · 제품 튜플로 도는 parametrize 케이스 감소와 0T parametrize 리터럴 감소 · conftest 이동으로
autouse 범위가 바뀌는 것 · `.gitignore` 된 테스트 데이터 · 0T 의 같은 이름 재작성·단언 약화 · 제품 메서드 개명(클래스 본문이 바뀌어
red — 시험 케이스 개명은 승인 «개명» 행으로만 · 값 객체 칸 개명은 0F «칸 개명» 행으로만) · 칸 개명의 못 푼 자리(받는 쪽이 이름
아닌 식 · 내포 · lambda 대상 · 다른 값도 대입한 이름 · 재수출로 들인 클래스 · 문자열 · `dataclasses.replace(…, 옛=)` · match
클래스 패턴 — 그대로 둬서 지금 규칙이 처분한다) · 믹스인이 상속한 케이스 · 동적 마이그레이션 미측정(인터프리터 없음 — open 이
미측정이면 close 도 재지 않는다).
"""
from __future__ import annotations

import argparse
import ast
import base64
import builtins
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
from typing import Callable, Iterator, NamedTuple

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
    """커밋의 파일 원문 — `path` 는 프로젝트 기준(`<rev>:./<path>` — 하위 폴더 프로젝트에서도 · 검토 B3)."""
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:./{path}"], capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def _prefix(repo: Path) -> str:
    """프로젝트 루트의 git 뿌리 기준 접두(`proj/` · 뿌리면 빈 글). 이 도구는 경로를 프로젝트 기준으로 다루고(git 이 뿌리 기준으로
    내는 status 를 이것으로 깎는다), 창 기록의 `dirty` 키 · `merged_excluded` 만 git 뿌리 기준으로 적는다(`folder_group` 이 접두를
    깎아 읽는 기록 계약 · 검토 B3)."""
    return _git(repo, "rev-parse", "--show-prefix").strip()


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
    """HEAD 대비 작업 트리 변경 경로(수정·삭제·미추적 · 프로젝트 기준 — 프로젝트 밖은 뺀다) — `.dddjango/` 제외."""
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
    pre: str = _prefix(repo)
    return sorted(p[len(pre):] for p in paths if p.startswith(pre) and not _excluded(p[len(pre):]))


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
            unit: bool = _testcase_class(node)
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
    """정의 대응 대상 — 테스트 케이스(test*·Test*)와 dunder 는 밖(테스트는 0C 에서 고정 · 케이스 개명은 대응표 치환이 아니다 —
    리팩토링 모드 0T · 0F 는 승인 «개명» 행만 기준 판에 먼저 적용한다 · `_rename_window`)."""
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
    pre: str = _prefix(repo)
    dirty_entries: "dict[str, dict]" = {}
    for p in dirty:
        data: "bytes | None" = (repo / p).read_bytes() if (repo / p).is_file() else None
        entry: "dict[str, object]" = {"sha": _sha(data)}
        # 리팩토링 모드는 창 기준선의 모든 미커밋 원문을 남긴다(시험 쪽 분류가 비 .py 로 넓다 · 감사 키의 «전»).
        if data is not None and (mode == "refactor" or p.endswith(".py") or _is_test(p, test_dirs) or p in PYTEST_FILES):
            entry["b64"] = base64.b64encode(data).decode("ascii")
        dirty_entries[pre + p] = entry                   # 기록 키는 git 뿌리 기준(`_record_dirty` 가 깎아 읽는다)
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

def _record_dirty(repo: Path, opened: dict) -> "dict[str, dict]":
    """open 기록의 미커밋 원문(키는 git 뿌리 기준)을 프로젝트 기준 경로로 — 프로젝트 밖 키는 뺀다(검토 B3)."""
    pre: str = _prefix(repo)
    return {p[len(pre):]: e for p, e in opened["dirty"].items() if p.startswith(pre)}


def _record_paths(repo: Path, paths: "set[str]") -> "list[str]":
    """기록에 적는 경로(git 뿌리 기준) — `merged_excluded` 계약(`folder_group` 이 접두를 깎아 읽는다 · 검토 B3)."""
    pre: str = _prefix(repo)
    return sorted(pre + p for p in paths)


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
    return {p for p in _git(repo, "diff", "--no-renames", "--relative", "--name-only", "-z", a, b).split("\0") if p}


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
    dirty0: "dict[str, dict]" = _record_dirty(repo, opened)

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
                   "green_files": sorted(green_files), "merged_excluded": _record_paths(repo, merged),
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
    """작업 트리 대 창 기준 커밋의 경로(추적 파일 · 프로젝트 기준)."""
    return {p for p in _git(repo, "diff", "--no-renames", "--relative", "--name-only", "-z", head0).split("\0") if p}


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
FOLLOW_OUTSIDE_KINDS: "frozenset[str]" = frozenset({"프로젝트 합성", "공유 표면", "묶음 import 치환"})
GROUP_IMPORT_KIND: str = "묶음 import 치환"   # 0C 묶음 창에서만 · 그 창의 묶음 이동을 따른 import 치환만(설계 10절 · 검토 B8)
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


# 뜻 보존 시험 개명(설계 3.1 §D · F4-116) — 승인 «개명» 행(입장 표 retain 재조직 · G1 스냅숏 `retain_rows[].renames`)을 0T · 0F 가
# 받는다. 옛 → 새 를 기준 판에 먼저 적용하고(AST 가 가리킨 정의 이름 · id 리터럴 자리만 바꾼 원문) 그 창의 지금 규칙을 그대로 돈다.
# 칸 개명(설계 A 4판 A6)은 항목 {kind 칸, path 시험 파일, source 운영 경로, class, old, new} — 0F 만 받는다(`_field_pair`).

FIELD_KIND: str = "칸"
CONTRACT_ROOTS: "frozenset[str]" = frozenset({"django", "ninja", "pydantic"})    # 밖 계약 · DB 구조 클래스의 뿌리 패키지
PLAIN_BASES: "frozenset[str]" = frozenset({"object", "typing.NamedTuple", "typing.Generic", "abc.ABC"})


def _rename_text(item: dict) -> str:
    if item.get("kind") == "ids":
        return f"{item['case']}[{item['old']}] → [{item['new']}]"
    if item.get("kind") == FIELD_KIND:
        return f"칸 {item['class']}.{item['old']} → {item['new']}"
    return f"{item['class'] + '::' if item.get('class') else ''}{item['old']} → {item['new']}"


def rename_label(item: dict) -> str:
    """개명 행 글자 — `경로::[클래스::]옛 → 새` · `경로::케이스[옛 id] → [새 id]` · `시험 경로::칸 운영 경로::클래스.옛 → 새`
    (close 기록 · verify 대조)."""
    if item.get("kind") == FIELD_KIND:
        return f"{item['path']}::칸 {item['source']}::{item['class']}.{item['old']} → {item['new']}"
    return f"{item['path']}::{_rename_text(item)}"


def _scope_body(tree: ast.Module, chain: "list[str]") -> "list[ast.stmt] | None":
    """모듈(빈 사슬) 또는 클래스 사슬의 본문 — 사슬의 클래스가 그 자리에 정확히 하나일 때만."""
    body: "list[ast.stmt]" = tree.body
    for name in chain:
        found = [n for n in body if isinstance(n, ast.ClassDef) and n.name == name]
        if len(found) != 1:
            return None
        body = found[0].body
    return body


def _target_names(target: ast.AST) -> "list[str]":
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return [x for e in target.elts for x in _target_names(e)]
    return []


_FUNCS: "tuple[type, ...]" = (ast.FunctionDef, ast.AsyncFunctionDef)


def _statements(body: "list[ast.stmt]") -> "Iterator[ast.stmt]":
    """그 자리의 문장 — 복합문(if · try · with · for · while · match)의 몸까지 걷는다(함수 · 클래스 몸은 다른 자리라 들어가지 않는다)."""
    for node in body:
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for field in ("body", "orelse", "finalbody"):
            inner = getattr(node, field, None)
            if isinstance(inner, list):
                yield from _statements(inner)
        for part in [*(getattr(node, "handlers", None) or []), *(getattr(node, "cases", None) or [])]:
            yield from _statements(part.body)


def _bound(body: "list[ast.stmt]") -> "list[tuple[str, ast.stmt]]":
    """그 자리의 이름 묶음(설계 3.1 §D3 «케이스 · 함수 · 대입 · import 묶음 전부» — 복합문 몸 · for 대상 · with … as · except … as
    포함) — (이름, 문장). 별 import 는 이름을 모른다(`_star`)."""
    out: "list[tuple[str, ast.stmt]]" = []
    for node in _statements(body):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append((node.name, node))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            out += [(x, node) for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
                    for x in _target_names(t)]
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            out += [(x, node) for x in _target_names(node.target)]
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            out += [(x, node) for item in node.items if item.optional_vars is not None
                    for x in _target_names(item.optional_vars)]
        elif isinstance(node, ast.Import):
            out += [(a.asname or a.name.split(".")[0], node) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            out += [(a.asname or a.name, node) for a in node.names if a.name != "*"]
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            out += [(x, node) for x in node.names]
        out += [(h.name, node) for h in getattr(node, "handlers", None) or [] if h.name]
        out += [(x, node) for x in _expr_binders(node)]
    return out


def _expr_binders(node: ast.stmt) -> "list[str]":
    """문장 자신의 식(몸 · 중첩 함수 · 클래스 · lambda 밖)이 묶는 이름 — 바다코끼리(`:=` — 내포 안도 그 자리) · match 캡처 이름."""
    out: "list[str]" = []
    stack: "list[ast.AST]" = []
    for field, value in ast.iter_fields(node):
        if field in ("body", "orelse", "finalbody", "handlers"):
            continue
        stack += value if isinstance(value, list) else [value]
    while stack:
        cur = stack.pop()
        if not isinstance(cur, ast.AST) or isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(cur, ast.NamedExpr):
            out += _target_names(cur.target)
        elif isinstance(cur, (ast.MatchAs, ast.MatchStar)) and cur.name:
            out.append(cur.name)
        elif isinstance(cur, ast.MatchMapping) and cur.rest:
            out.append(cur.rest)
        if isinstance(cur, ast.match_case):
            stack += [cur.pattern, *([cur.guard] if cur.guard is not None else [])]   # 몸은 `_statements` 가 걷는다
            continue
        stack += list(ast.iter_child_nodes(cur))
    return out


def _star(body: "list[ast.stmt]") -> bool:
    """그 자리(복합문 몸 포함)에 별 import(`from … import *`)가 있는가 — 들여오는 이름을 몰라 가림을 볼 수 없다."""
    return any(isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names) for n in _statements(body))


def _inherited(tree: ast.Module, name: str) -> "tuple[dict[str, str], str]":
    """클래스가 같은 파일 기반 클래스(사슬 끝까지)에서 물려받는 이름 {이름: 기반 클래스} · 못 푸는 기반의 글자(파일 밖 이름 · 식 ·
    클래스 키워드 — 없으면 빈 글). `object` 는 물려줄 이름이 없다."""
    classes: "dict[str, list[ast.ClassDef]]" = collections.defaultdict(list)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name].append(node)
    names: "dict[str, str]" = {}
    seen: "set[str]" = {name}
    queue: "list[ast.ClassDef]" = classes[name][:1]
    while queue:
        node = queue.pop(0)
        if node.keywords:
            return names, ast.unparse(node.keywords[0])
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "object":
                continue
            if not isinstance(base, ast.Name) or len(classes.get(base.id, [])) != 1:
                return names, ast.unparse(base)
            if base.id in seen:
                continue
            seen.add(base.id)
            parent: ast.ClassDef = classes[base.id][0]
            for x, _n in _bound(parent.body):
                names.setdefault(x, base.id)
            queue.append(parent)
    return names, ""


def _subclasses(tree: ast.Module, name: str) -> "list[str]":
    """같은 파일 최상위 클래스 가운데 `name` 을 (사슬로) 상속하는 것 — 파일 차례."""
    found: "set[str]" = {name}
    grown: bool = True
    while grown:
        grown = False
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name not in found \
                    and any(isinstance(b, ast.Name) and b.id in found for b in node.bases):
                found.add(node.name)
                grown = True
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef) and n.name in found - {name}]


def _testcase_class(node: ast.ClassDef) -> bool:
    """`…TestCase` 하위 클래스(unittest 꼴 — 메서드는 test 접두면 수집)."""
    return any((isinstance(b, ast.Name) and b.id.endswith("TestCase"))
               or (isinstance(b, ast.Attribute) and b.attr.endswith("TestCase")) for b in node.bases)


def _fixture(fn: ast.AST) -> bool:
    for dec in getattr(fn, "decorator_list", []):
        target = dec.func if isinstance(dec, ast.Call) else dec
        if (isinstance(target, ast.Attribute) and target.attr == "fixture") \
                or (isinstance(target, ast.Name) and target.id == "fixture"):
            return True
    return False


def _collected(path: str, tree: ast.Module, owner: "list[str]", name: str, config: "dict[str, str]") -> bool:
    """`_test_cases` 규칙으로 수집되는 케이스 이름인가 — 수집 파일(python_files · testpaths) · 모듈 함수는 python_functions · 최상위
    클래스 메서드는 그 클래스가 python_classes 이거나 `…TestCase` 하위 클래스(그때는 test 접두)."""
    if not _collectible(path, config) or len(owner) > 1:
        return False
    fn_pats: "list[str]" = _config_list(config, "python_functions") or ["test"]
    if not owner:
        return _name_match(name, fn_pats)
    found = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner[0]]
    if len(found) != 1:
        return False
    if _testcase_class(found[0]):
        return name.startswith("test")
    return _name_match(owner[0], _config_list(config, "python_classes") or ["Test"]) and _name_match(name, fn_pats)


def _is_param(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Attribute) and node.func.attr == "param")
        or (isinstance(node.func, ast.Name) and node.func.id == "param"))


def _param_id(call: ast.Call) -> "ast.Constant | None":
    return next((k.value for k in call.keywords if k.arg == "id" and isinstance(k.value, ast.Constant)
                 and isinstance(k.value.value, str)), None)


def _element_ids(fn: ast.AST) -> "list[tuple[int, ast.Constant]]":
    """케이스의 parametrize 원소 id — (데코레이터 차례, id 문자열 상수). 데코레이터 인자 안 리터럴만(`ids=` 목록 · 값 목록 안
    `pytest.param(..., id=)`) — 모듈 상수 목록 안 `pytest.param(id=)` 는 세지 않는다(꼴 밖)."""
    out: "list[tuple[int, ast.Constant]]" = []
    for i, dec in enumerate(getattr(fn, "decorator_list", [])):
        if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == "parametrize"):
            continue
        ids = next((k.value for k in dec.keywords if k.arg == "ids"), None)
        values = dec.args[1] if len(dec.args) > 1 else next((k.value for k in dec.keywords if k.arg == "argvalues"), None)
        if isinstance(ids, (ast.List, ast.Tuple)):
            out += [(i, e) for e in ids.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if isinstance(values, (ast.List, ast.Tuple)):
            out += [(i, c) for e in values.elts if _is_param(e) for c in [_param_id(e)] if c is not None]  # type: ignore[arg-type]
    return out


def _joined_id(fn: ast.AST, text: str) -> bool:
    """`text` 가 겹친 parametrize 원소 id 를 `-` 로 이은 합친 id 인가(데코레이터 차례 · 거꾸로 차례 둘 다 본다)."""
    groups: "dict[int, list[str]]" = collections.defaultdict(list)
    for i, c in _element_ids(fn):
        groups[i].append(c.value)
    lists: "list[list[str]]" = [groups[i] for i in sorted(groups)]

    def fits(rest: str, order: "list[list[str]]") -> bool:
        if len(order) == 1:
            return rest in order[0]
        return any(rest.startswith(x + "-") and fits(rest[len(x) + 1:], order[1:]) for x in order[0])
    return len(lists) > 1 and (fits(text, lists) or fits(text, lists[::-1]))


def _all_param_ids(tree: ast.Module) -> "set[str]":
    return {c.value for n in ast.walk(tree) if _is_param(n) for c in [_param_id(n)] if c is not None}  # type: ignore[arg-type]


def _literal(old: str, new: str) -> str:
    """id 리터럴 새 원문 — 옛 리터럴이 (접두 r · u 와) 따옴표 하나로 감싼 꼴이면 그 접두 · 따옴표 그대로 · 아니면 repr."""
    m = re.fullmatch(r"([rRuU]?)(['\"])(.*)\2", old, re.S)
    if m is not None and not old[len(m.group(1)):].startswith(m.group(2) * 3) \
            and not any(c in new for c in (m.group(2), "\\", "\n", "\r")):
        return m.group(1) + m.group(2) + new + m.group(2)
    return repr(new)


def _top_unit(chain: "list[str]", name: str) -> str:
    """감사 단위(최상위 정의) — 클래스 사슬이 있으면 맨 바깥 클래스 · 없으면 그 함수."""
    return chain[0] if chain else name



def _case_pair(t0: ast.Module, t1: ast.Module, owner: "list[str]", old: str, new: str, path: str,
               configs: "tuple[dict[str, str], dict[str, str]]") -> "tuple[str, ast.stmt] | None":
    """케이스 개명 쌍 하나 — None 이면 이 창 몫이 아니다(기준 판에 옛 없음 · 옛이 새 판에 남음) · 아니면 (꼴 밖 사유 — 빈 글이면 받음,
    옛 정의). 그 자리는 모듈 또는 최상위 클래스이고 이름 묶음은 복합문 몸까지 · 클래스면 같은 파일 기반 클래스가 물려주는 이름까지 본다.
    같은 파일에 그 클래스를 (사슬로) 상속하는 클래스가 있으면 꼴 밖이다(하위 클래스의 수집 키도 함께 바뀐다)."""
    s0, s1 = _scope_body(t0, owner), _scope_body(t1, owner)
    if s0 is None or s1 is None:
        return None
    b0, b1 = _bound(s0), _bound(s1)
    olds: "list[ast.stmt]" = [n for x, n in b0 if x == old]
    if not olds or any(x == old for x, _n in b1):
        return None
    news: "list[ast.stmt]" = [n for x, n in b1 if x == new]
    fn: ast.stmt = olds[0]
    if len(owner) > 1:
        return "중첩 클래스 메서드 개명은 이번 판 밖", fn
    if len(olds) != 1:
        return f"옛 이름이 기준 판 그 자리에 {len(olds)}번(정확히 한 번이어야)", fn
    if isinstance(fn, ast.ClassDef):
        return "클래스 개명은 이번 판 밖", fn
    if not isinstance(fn, _FUNCS):
        return "옛 이름이 함수 정의가 아니다", fn
    if _fixture(fn):
        return "시험 케이스가 아니다(픽스처)", fn
    if not _collected(path, t0, owner, old, configs[0]):
        return "시험 케이스가 아니다(수집 규칙 밖 — python_files · python_functions · python_classes · TestCase)", fn
    heirs: "list[str]" = (_subclasses(t0, owner[0]) or _subclasses(t1, owner[0])) if owner else []
    if heirs:
        return f"하위 클래스 {heirs[0]} 가 물려받는다(하위 클래스의 수집 키도 함께 바뀌어 행이 덮지 못한다)", fn
    if any(x == new for x, _n in b0):
        return "새 이름이 기준 판 그 자리에 있다(가림)", fn
    if not owner and (_star(s0) or _star(s1)):
        return "그 자리에 별 import(`from … import *`)가 있다 — 가림을 볼 수 없다", fn
    for side, tree in (("기준 판", t0), ("새 판", t1)):
        inherited, unresolved = _inherited(tree, owner[0]) if owner else ({}, "")
        if unresolved:
            return f"파일 밖 기반 클래스(또는 못 푸는 기반) `{unresolved[:60]}` — 물려받는 이름을 볼 수 없다", fn
        if new in inherited:
            return f"새 이름이 {side} 그 자리에 있다(가림 — 같은 파일 기반 클래스 {inherited[new]})", fn
    if len(news) != 1:
        return f"새 이름이 새 판 그 자리에 {len(news)}번(정확히 한 번이어야)", fn
    if not isinstance(news[0], _FUNCS):
        return "새 이름이 새 판에서 함수 정의가 아니다", fn
    if _fixture(news[0]) or not _collected(path, t1, owner, new, configs[1]):
        return "새 이름이 수집 케이스 꼴이 아니다", fn
    return "", fn


def _ids_pair(t0: ast.Module, t1: ast.Module, it: dict, case_items: "list[dict]", path: str,
              configs: "tuple[dict[str, str], dict[str, str]]") -> "tuple[str, ast.Constant | None, str, str] | None":
    """ids 개명 쌍 하나 — None 이면 이 창 몫이 아니다 · 아니면 (꼴 밖 사유 — 빈 글이면 받음, 옛 id 상수, 전 단위, 후 단위). 케이스
    이름은 같은 파일 케이스 개명 행의 옛 · 새 이름도 받는다(한 창 · 앞 창 개명). 합친 id · 모듈 상수 목록 안 `pytest.param(id=)` 는
    판정 시점과 무관하게 꼴 밖이다(원소 id 를 쓴다 · 데코레이터 인자 안 리터럴만)."""
    old, new = str(it["old"]), str(it["new"])
    chain: "list[str]" = str(it["case"]).split("::")
    name, owner = chain[-1], chain[:-1]
    scope: str = "::".join(owner)
    aliases: "set[str]" = {name} | {c["new"] for c in case_items if (c.get("class") or "") == scope and c["old"] == name} \
        | {c["old"] for c in case_items if (c.get("class") or "") == scope and c["new"] == name}
    s0, s1 = _scope_body(t0, owner), _scope_body(t1, owner)
    f0 = [n for n in s0 or [] if isinstance(n, _FUNCS) and n.name in aliases]
    f1 = [n for n in s1 or [] if isinstance(n, _FUNCS) and n.name in aliases]
    ids0 = _element_ids(f0[0]) if len(f0) == 1 else []
    ids1 = _element_ids(f1[0]) if len(f1) == 1 else []
    hits = [(i, c) for i, c in ids0 if c.value == old]
    if not hits:
        if len(f0) == 1 and _joined_id(f0[0], old):
            return "합친 id — 원소 id 를 쓴다(`<케이스>[<원소 id>]` · 데코레이터 하나의 id)", None, "", ""
        if old in _all_param_ids(t0) and old not in _all_param_ids(t1):
            return "모듈 상수 목록 안 pytest.param(id=) 는 꼴 밖(데코레이터 인자 안 리터럴만)", None, "", ""
        return None
    if any(c.value == old for _i, c in ids1):
        return None                                     # 옛 id 가 새 판에 남음 — 이 창 몫이 아니다
    fn = f0[0]
    news: int = sum(1 for _i, c in ids1 if c.value == new)
    node: ast.Constant = hits[0][1]
    why: str = (
        "중첩 클래스 메서드 개명은 이번 판 밖" if len(owner) > 1 else
        "시험 케이스가 아니다(픽스처)" if _fixture(fn) else
        "시험 케이스가 아니다(수집 규칙 밖 — python_files · python_functions · python_classes · TestCase)"
        if not _collected(path, t0, owner, fn.name, configs[0]) else
        f"옛 id 가 그 케이스 parametrize 데코레이터 원소에 {len(hits)}번(데코레이터 하나에 정확히 한 번이어야)" if len(hits) != 1 else
        "새 id 가 그 데코레이터의 옛 ids 에 있다(맞바꿈)" if any(i == hits[0][0] and c.value == new for i, c in ids0) else
        "새 판에 그 케이스가 없다" if len(f1) != 1 else
        f"새 id 가 새 판 그 케이스에 {news}번(정확히 한 번이어야)" if news != 1 else
        "id 리터럴이 여러 줄이다" if node.end_lineno != node.lineno else "")
    return why, node, _top_unit(owner, fn.name), _top_unit(owner, f1[0].name) if len(f1) == 1 else ""


class _Scope(NamedTuple):
    """이름 묶음 자리 — 종류(module · func · class · hide = 내포 · lambda 대상) · 이름 → 묶는 자리(문장 · 매개변수 · 내포 식)."""
    kind: str
    names: "dict[str, list[ast.AST]]"


def _scope_names(body: "list[ast.stmt]", params: "list[ast.arg] | None" = None) -> "dict[str, list[ast.AST]]":
    """그 자리 이름 → 묶는 자리 — `_bound`(복합문 몸 · import · 바다코끼리 · match 캡처 · global) · 덧셈 대입(`+=`) 대상 · 매개변수."""
    names: "dict[str, list[ast.AST]]" = collections.defaultdict(list)
    for x, node in _bound(body):
        names[x].append(node)
    for node in _statements(body):
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
            names[node.target.id].append(node)
    for a in params or []:
        names[a.arg].append(a)
    return dict(names)


def _params(args: ast.arguments) -> "list[ast.arg]":
    return [*args.posonlyargs, *args.args, *([args.vararg] if args.vararg else []), *args.kwonlyargs,
            *([args.kwarg] if args.kwarg else [])]


def _lookup(name: str, scopes: "list[_Scope]") -> "tuple[list[ast.AST], list[_Scope]] | None":
    """이름을 묶는 자리(안쪽부터 — 메서드 · 내포 안에서는 클래스 몸을 건너뛴다) — (묶는 자리, 그 자리까지의 사슬) · 없으면 None."""
    for i in range(len(scopes) - 1, -1, -1):
        if scopes[i].kind == "class" and i != len(scopes) - 1:
            continue
        if name in scopes[i].names:
            return scopes[i].names[name], scopes[: i + 1]
    return None


def _import_target(node: ast.AST, name: str, package: str) -> "str | None":
    """import 문이 `name` 에 묶는 대상의 점 경로(`import a.b` → `a` · `import a.b as m` → `a.b` · `from p import x as m` → `p.x` —
    상대 import 는 이 파일 패키지 기준) — import 문이 아니면 None."""
    if isinstance(node, ast.Import):
        for a in node.names:
            if a.asname == name:
                return a.name
            if a.asname is None and a.name.split(".")[0] == name:
                return name
    elif isinstance(node, ast.ImportFrom):
        for a in node.names:
            if a.name != "*" and (a.asname or a.name) == name:
                return _join(_from_base(package, node), a.name)
    return None


def _dotted(expr: ast.AST, scopes: "list[_Scope]", package: str) -> "str | None":
    """식이 가리키는 점 경로 — 이름 · 속성 사슬(문자열 주석은 식으로 풀어서)의 첫 이름이 import 로만 묶였으면 그 대상 + 사슬 · 묶음
    없는 이름 하나(내장)는 글자 그대로 · 그 밖(다른 대입 · 매개변수 · 여러 대상 · 묶음 없는 사슬)은 None."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        try:
            expr = ast.parse(expr.value.strip(), mode="eval").body
        except (SyntaxError, ValueError):
            return None
    rest: "list[str]" = []
    while isinstance(expr, ast.Attribute):
        rest.insert(0, expr.attr)
        expr = expr.value
    if not isinstance(expr, ast.Name):
        return None
    found = _lookup(expr.id, scopes)
    if found is None:
        return None if rest else expr.id
    targets: "set[str | None]" = {_import_target(node, expr.id, package) for node in found[0]}
    if len(targets) != 1 or None in targets:
        return None
    return ".".join([str(targets.pop()), *rest])


def _instance(name: str, scopes: "list[_Scope]", package: str, target: str) -> bool:
    """이름이 그 클래스(`target`) 값으로 풀리는가 — 그 자리의 묶음이 모두 그 클래스 주석(지역 변수 · 매개변수)이거나 그 클래스
    호출을 그 이름 하나에 대입한 것일 때만(다른 대입 · for · with · 내포 · global 이 하나라도 있으면 못 푼다)."""
    found = _lookup(name, scopes)
    if found is None:
        return False
    binds, chain = found
    for node in binds:
        if isinstance(node, ast.arg):
            ok: bool = node.annotation is not None and _dotted(node.annotation, chain, package) == target
        elif isinstance(node, ast.AnnAssign):
            ok = isinstance(node.target, ast.Name) and node.target.id == name \
                and _dotted(node.annotation, chain, package) == target
        elif isinstance(node, ast.Assign):
            ok = len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name \
                and isinstance(node.value, ast.Call) and _dotted(node.value.func, chain, package) == target
        else:
            ok = False
        if not ok:
            return False
    return bool(binds)


def _field_sites(tree: ast.Module, path: str, target: str, field: str) -> "list[tuple[int, int, int]]":
    """시험 파일에서 그 클래스(`target` = 모듈.클래스)로 풀리는 칸 `field` 자리 — 그 클래스 호출의 키워드 `field=` · 받는 쪽 이름이
    그 클래스 값으로 풀리는 속성 `.field` — (줄, 시작 열, 끝 열 — UTF-8 바이트) · 원문 차례."""
    module: str = _module(path)
    package: str = module if path.endswith("__init__.py") else module.rpartition(".")[0]
    width: int = len(field.encode("utf-8"))
    out: "list[tuple[int, int, int]]" = []

    def visit(node: ast.AST, scopes: "list[_Scope]") -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            params: "list[ast.arg]" = _params(node.args)
            for child in [*getattr(node, "decorator_list", []), *node.args.defaults,
                          *[d for d in node.args.kw_defaults if d is not None],
                          *[a.annotation for a in params if a.annotation is not None],
                          *([node.returns] if getattr(node, "returns", None) is not None else [])]:
                visit(child, scopes)                      # 장식자 · 기본값 · 주석은 바깥 자리에서 푼다
            if isinstance(node, ast.Lambda):
                visit(node.body, [*scopes, _Scope("hide", {a.arg: [node] for a in params})])
            else:
                inner: "list[_Scope]" = [*scopes, _Scope("func", _scope_names(node.body, params))]
                for stmt in node.body:
                    visit(stmt, inner)
            return
        if isinstance(node, ast.ClassDef):
            for child in [*node.decorator_list, *node.bases, *[k.value for k in node.keywords]]:
                visit(child, scopes)
            inner = [*scopes, _Scope("class", _scope_names(node.body))]
            for stmt in node.body:
                visit(stmt, inner)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            scopes = [*scopes, _Scope("hide", {x: [node] for g in node.generators for x in _target_names(g.target)})]
        elif isinstance(node, ast.Call) and _dotted(node.func, scopes, package) == target:
            out.extend((k.lineno, k.col_offset, k.col_offset + width) for k in node.keywords if k.arg == field)
        elif isinstance(node, ast.Attribute) and node.attr == field and isinstance(node.value, ast.Name) \
                and _instance(node.value.id, scopes, package, target):
            end: int = node.end_col_offset or 0
            out.append((node.end_lineno or node.lineno, end - width, end))
        for child in ast.iter_child_nodes(node):
            visit(child, scopes)

    visit(tree, [_Scope("module", _scope_names(tree.body))])
    return sorted(out)


def _top_class(tree: "ast.Module | None", name: str) -> "ast.ClassDef | None":
    """모듈 최상위에 정확히 하나인 그 이름의 클래스."""
    found = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name] if tree is not None else []
    return found[0] if len(found) == 1 else None


def _contract_class(tree: ast.Module, cls: ast.ClassDef, package: str) -> str:
    """운영 클래스가 밖 계약 · DB 구조이거나 그런지 모르면 그 사유(빈 글이면 아님) — 장식자 · 기반 · 클래스 키워드가 django · ninja ·
    pydantic 으로 풀리면 밖 계약(칸 개명이 밖 계약 · DB 구조 변경 — retain 재조직이 아니다) · 기반은 같은 파일 최상위 클래스(사슬) ·
    object · typing.NamedTuple · typing.Generic · abc.ABC · 내장 예외(모듈이 가리지 않은 `builtins` 의 BaseException 하위 클래스 —
    `*` import 가 있으면 못 가린다고 못 본다)만 받는다."""
    scopes: "list[_Scope]" = [_Scope("module", _scope_names(tree.body))]
    star: bool = any(isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names) for n in ast.walk(tree))
    seen: "set[str]" = set()
    queue: "list[ast.ClassDef]" = [cls]
    while queue:
        node: ast.ClassDef = queue.pop()
        if node.name in seen:
            continue
        seen.add(node.name)
        for dec in node.decorator_list:
            got: "str | None" = _dotted(dec.func if isinstance(dec, ast.Call) else dec, scopes, package)
            if got is not None and got.split(".")[0] in CONTRACT_ROOTS:
                return f"운영 클래스 `{cls.name}` 가 밖 계약 · DB 구조다(ninja Schema · pydantic 모델 · Django Model — 장식자 `{got}`)"
        for base in [*node.bases, *[k.value for k in node.keywords]]:
            expr: ast.AST = base.value if isinstance(base, ast.Subscript) else base
            found = _lookup(expr.id, scopes) if isinstance(expr, ast.Name) else None
            if found is not None and len(found[0]) == 1 and isinstance(found[0][0], ast.ClassDef):
                queue.append(found[0][0])                 # 같은 파일 최상위 기반 클래스 — 사슬로 본다
                continue
            got = _dotted(expr, scopes, package)
            if got is not None and got.split(".")[0] in CONTRACT_ROOTS:
                return f"운영 클래스 `{cls.name}` 가 밖 계약 · DB 구조다(ninja Schema · pydantic 모델 · Django Model — 기반 `{got}`)"
            if got not in PLAIN_BASES and (star or not _builtin_error(got)):
                return (f"운영 클래스 `{cls.name}` 의 기반 클래스 `{ast.unparse(base)[:60]}` 를 풀지 못했다(밖 계약 · DB 구조인지 "
                        "모른다 — 같은 파일 클래스 · object · NamedTuple · Generic · ABC · 내장 예외 만)")
    return ""


def _builtin_error(name: "str | None") -> bool:
    """`_dotted` 가 글자 그대로 준 이름(모듈에 묶음 없음)이 `builtins` 의 BaseException 하위 클래스인가 — 내장 예외."""
    found: object = getattr(builtins, name, None) if name and "." not in name else None
    return isinstance(found, type) and issubclass(found, BaseException)


def _field_renamed(c0: ast.ClassDef, c1: ast.ClassDef, old: str, new: str) -> bool:
    """운영 클래스 몸에서 칸 `old` 가 `new` 로 정확히 바뀌었나 — 기준 판에 `old` 주석 칸 하나 · `new` 묶음 없음, 새 판에 `new` 주석
    칸 하나 · `old` 묶음 없음, 두 칸의 주석 · 기본값이 같다."""
    b0, b1 = _scope_names(c0.body), _scope_names(c1.body)
    o, n = b0.get(old, []), b1.get(new, [])
    if new in b0 or old in b1 or len(o) != 1 or len(n) != 1:
        return False
    a, b = o[0], n[0]
    return isinstance(a, ast.AnnAssign) and isinstance(b, ast.AnnAssign) \
        and (_dump_node(a.annotation), _dump_node(a.value)) == (_dump_node(b.annotation), _dump_node(b.value))


def _lines_of(sites: "list[tuple[int, int, int]]") -> str:
    return " · ".join(str(x) for x in sorted({s[0] for s in sites}))


def _field_pair(t0: ast.Module, t1: ast.Module, it: dict, path: str,
                sources: "Callable[[str], tuple[bytes | None, bytes | None]] | None"
                ) -> "tuple[str, list[tuple[int, int, int]]] | None":
    """칸 개명 쌍 하나 — None 이면 이 창 몫이 아니다 · 아니면 (꼴 밖 사유 — 빈 글이면 받음, 기준 판에서 바꿀 자리).

    이 창 몫 = 운영 클래스(`source_at` — 앞 창 이동을 따라간 운영 경로)의 옛 칸이 이 창에서 사라졌다 · 또는 시험 파일이 그 클래스로
    풀리는 옛 자리를 모두 새 이름으로 옮겼다(기준 판에 있고 · 새 판에 없고 · 새 판에 새 자리). 몫이면 운영 클래스(밖 계약 · DB 구조
    아님 · 칸이 옛 → 새 로 정확히)와 시험 파일(새 판에 옛 자리 없음 · 기준 판에 새 자리 없음 · 기준 판에 바꿀 자리 있음)을 본다."""
    source: str = str(it.get("source_at") or it["source"])
    cls, old, new = str(it["class"]), str(it["old"]), str(it["new"])
    module: str = _module(source)
    target: str = f"{module}.{cls}"
    then, now = sources(source) if sources is not None else (None, None)
    p0, p1 = _parse(_py_source(then)), _parse(_py_source(now))
    c0, c1 = _top_class(p0, cls), _top_class(p1, cls)
    try:
        olds, left = _field_sites(t0, path, target, old), _field_sites(t1, path, target, old)
        news, ahead = _field_sites(t1, path, target, new), _field_sites(t0, path, target, new)
    except RecursionError:
        return "시험 파일 AST 가 너무 깊어 칸 자리를 셀 수 없다", []
    gone: bool = c0 is not None and c1 is not None and old in _scope_names(c0.body) and old not in _scope_names(c1.body)
    if not gone and not (olds and not left and news):
        return None
    package: str = module if source.endswith("__init__.py") else module.rpartition(".")[0]
    if sources is None:
        return "운영 파일을 읽을 수 없다 — judge_test_side 가 운영 파일 읽기를 넘긴다", olds
    if p0 is None or p1 is None or c0 is None or c1 is None:
        return f"운영 클래스 `{cls}` 가 `{source}` 기준 판 · 새 판 최상위에 정확히 하나가 아니다(같은 창 이동이면 창을 나눈다)", olds
    contract: str = _contract_class(p0, c0, package) or _contract_class(p1, c1, package)
    checks: "list[tuple[bool, str]]" = [            # 차례대로 — 첫 어긋남이 사유
        (bool(contract), contract),
        (not _field_renamed(c0, c1, old, new),
         f"운영 클래스 칸이 이 창에서 옛 → 새 로 정확히 바뀌지 않았다(`{cls}` — 기준 판 `{old}` 주석 칸 하나 · 새 판 `{new}` 주석 칸 하나 · "
         "주석 · 기본값 같음)"),
        (bool(left), f"받는 쪽이 그 클래스인 `.{old}` · `{old}=` 이 새 판에 남았다(줄 {_lines_of(left)})"),
        (bool(ahead), f"기준 판에 그 클래스로 풀리는 `.{new}` · `{new}=` 이 이미 있다(가림 — 줄 {_lines_of(ahead)})"),
        (not olds, f"기준 판에 바꿀 자리가 없다(그 클래스로 풀리는 `{old}=` · `.{old}` 0 — 받는 쪽을 못 푼 자리는 바꾸지 않는다)")]
    return next((why for bad, why in checks if bad), ""), olds


def _rename_window(kind: str, items: "list[dict]", a: bytes, b: bytes, path: str = "",
                   configs: "tuple[dict[str, str], dict[str, str]] | None" = None,
                   sources: "Callable[[str], tuple[bytes | None, bytes | None]] | None" = None
                   ) -> "tuple[list[dict], list[str], bytes]":
    """한 창 · 한 시험 쪽 파일의 개명 행(설계 3.1 §D3 · 구현 검토 고침) — (적용 쌍, red 사유, 옛 → 새 를 먼저 적용한 기준 판 원문).

    쌍은 «기준 판에 옛 있음 ∧ 새 판에 옛 없음»일 때만 이 창 몫이다 — 옛 이름이 새 판에 남으면 건너뛴다(red 아님 · 0C 도). 몫인 쌍은
    0C 면 red(시험 고정)이고, 0T · 0F 면 `_case_pair` · `_ids_pair` 의 확인(수집 케이스만 · 가림은 복합문 몸 · 별 import · 같은 파일
    기반 클래스까지 · 새 판 한 번 · ids 원소 id · 맞바꿈 · 합친 id · 모듈 상수)이 어긋나면 «개명 행 꼴 밖»이다. 칸 개명은 몫이
    `_field_pair` 로 정해지고 0F 만 받는다(0T 도 red). 확인은 모두 원래 기준 판에 대고, 적용은 그 뒤 한꺼번에 한다(정의 이름 · id
    리터럴 · 칸 자리만 — id 접두 · 따옴표 보존). 쌍마다 감사 키(`개명 …` · 전 = 옛 단위 · 후 = 새 단위 digest — 칸은 파일 전 · 후)를
    만든다. `configs` = (기준 판 · 새 판 pytest 설정 — 수집 규칙) · `sources` = 운영 경로 → (창 기준 판 · 새 판 바이트 — 칸 개명)."""
    old_text, new_text = _py_source(a), _py_source(b)
    t0, t1 = _parse(old_text), _parse(new_text)
    if t0 is None or t1 is None or old_text is None:
        return [], [], a                                    # 파싱 불가 — 그 창 규칙이 처분한다
    configs = configs or ({}, {})
    pending: "list[tuple[dict, str, str, list[tuple[int, int, int, str]]]]" = []   # (항목, 전 단위, 후 단위, 편집들)
    reds: "list[str]" = []
    lines: "list[str]" = _LINE_TEXT.findall(old_text)
    case_items: "list[dict]" = [it for it in items if it.get("kind") not in ("ids", FIELD_KIND)]
    for it in items:
        label: str = rename_label(it)
        old, new = str(it["old"]), str(it["new"])
        field: bool = it.get("kind") == FIELD_KIND
        edits: "list[tuple[int, int, int, str]]" = []
        if it.get("kind") == "ids":
            got = _ids_pair(t0, t1, it, case_items, path, configs)
            if got is None:
                continue
            why, node, before, after = got
            if not why and node is not None:
                raw: bytes = lines[node.lineno - 1].encode("utf-8", "surrogateescape")
                literal: str = raw[node.col_offset:node.end_col_offset].decode("utf-8", "surrogateescape")
                edits = [(node.lineno, node.col_offset, node.end_col_offset or 0, _literal(literal, new))]
        elif field:
            spots = _field_pair(t0, t1, it, path, sources)
            if spots is None:
                continue
            why, sites = spots
            before = after = "<file>"                       # 칸 개명은 여러 단위에 걸친다 — 파일 전 · 후
            for line, start, end in [] if why else sites:
                if lines[line - 1].encode("utf-8", "surrogateescape")[start:end] != old.encode("utf-8"):
                    why = f"칸 자리(줄 {line})를 원문에서 못 찾았다"
                    break
                edits.append((line, start, end, new))
        else:
            owner: "list[str]" = [c for c in str(it.get("class") or "").split("::") if c]
            pair = _case_pair(t0, t1, owner, old, new, path, configs)
            if pair is None:
                continue
            why, fn = pair
            before, after = _top_unit(owner, old), _top_unit(owner, new)
            found = None if why else re.compile(rb"(?:async\s+)?def\s+(" + re.escape(old.encode("utf-8")) + rb")(?=\s*[(\[])").match(
                lines[fn.lineno - 1].encode("utf-8", "surrogateescape"), fn.col_offset)
            if found is not None:
                edits = [(fn.lineno, found.start(1), found.end(1), new)]
            elif not why:
                why = "정의 이름 자리를 원문에서 못 찾았다"
        if kind == "code":
            reds.append(f"0C 창은 개명 행을 받지 않는다(시험 고정 — {'칸 개명은 0F' if field else '개명은 0T · 0F'}) — {label}")
        elif field and kind != "follow":
            reds.append(f"0T 창은 칸 개명 행을 받지 않는다(제품 고정 — 칸 개명은 0F) — {label}")
        elif why or not edits:
            reds.append(f"개명 행 꼴 밖 — {label}: {why}")
        else:
            pending.append((it, before, after, edits))
    if reds or not pending:
        return [], reds, a
    for line, start, end, text in sorted((e for p in pending for e in p[3]), reverse=True):
        raw = lines[line - 1].encode("utf-8", "surrogateescape")
        lines[line - 1] = (raw[:start] + text.encode("utf-8", "surrogateescape") + raw[end:]).decode("utf-8", "surrogateescape")
    try:
        encoding: str = tokenize.detect_encoding(io.BytesIO(a).readline)[0]
        renamed: bytes = "".join(lines).encode(encoding)
        same: bool = old_text.encode(encoding) == a and "".join(_LINE_TEXT.findall(old_text)) == old_text  # 원문 되살림
    except (SyntaxError, LookupError, UnicodeError):
        renamed, same = a, False
    if not same or _parse(_py_source(renamed)) is None:
        return [], [f"개명 행 꼴 밖 — {rename_label(p[0])}: 옛 → 새 를 적용한 기준 판 원문을 만들지 못했다" for p in pending], a
    split_a, split_b = audit_split(a)[0], audit_split(b)[0]
    uses: "list[dict]" = []
    for it, before, after, done_edits in pending:
        unit: str = f"개명 {_rename_text(it)}"
        old_unit = split_a.defs.get(before) if split_a is not None else None
        new_unit = split_b.defs.get(after) if split_b is not None else None
        key = (unit, _digest(old_unit if old_unit is not None else a), _digest(new_unit if new_unit is not None else b))
        use: dict = {"item": it, "label": rename_label(it), "unit": unit, "key": key, "before": before, "after": after,
                     "outside": renamed != b}
        if it.get("kind") == FIELD_KIND:
            use["sites"] = sorted(e[0] for e in done_edits)  # 바꾼 자리 줄(감사 요청 자료)
        uses.append(use)
    return uses, [], renamed


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
    renames: "tuple[dict, ...]" = ()           # 0T · 0F — 이 파일에 적용한 개명 쌍(감사 키 `개명 …` · 전 · 후 단위 · 이름 밖 편집)
    base: "bytes | None" = None                # 개명 쌍이 있으면 옛 → 새 를 먼저 적용한 기준 판(감사 요청 자료 «단위 전»)


def dispose_test_file(kind: str, path: str, target: str, a: "bytes | None", b: "bytes | None", maps: Maps,
                      old_canon: "dict[str, dict | None]", new_canon: "dict[str, dict | None]",
                      exports_then: "_Exports | None", allowed: "set[str]", approved: "dict[str, dict]",
                      update_rows: "dict[str, list[str]] | None" = None, renames: "list[dict] | None" = None,
                      rename_reds: "list[str] | None" = None) -> "Disposition | None":
    """창 하나의 시험 쪽 파일 처분 — 우선순위 하나(§4-3). 바이트가 같고 자리도 같으면 None.

    새 파일 · 짝 없는 삭제는 표보다 먼저(케이스 규칙은 close 가 따로 본다) `<file>` 개별 감사 · 바이트 그대로 옮긴 파일은 `<file>`
    묶음 감사 · ① (change) D 확정이 전부 승인 원소 → 승인 변경 감사 · ② 기존 0C 검사 합격 → 감사(닿은 항목이 있으면 묶음 ·
    D 는 사유) · ③ D 확정 → red · ④ (follow · change) 허용 파일 → 개별 감사 · 그 밖 red. `test` 창은 D 확정이 전부
    «V 에 딸리지 않은 입장 표 `update` 행의 케이스 안» 또는 «`remove` 행이 승인한 케이스 통째 삭제»일 때만 개별 감사(그 파일의
    바뀐 단위 전부 키 · `approved` = remove 행 케이스) · 하나라도 밖이면 red · D 확정이 없으면 개별 감사. 비 .py 는 ② · ④ 만
    (0T 는 개별 감사).

    개명 쌍(`renames` — `a` 는 이미 옛 → 새 를 먼저 적용한 기준 판)은 쌍마다 감사 키 `개명 …` 를 더한다(기계가 혼자 통과시키지
    않는다) · 개명 말고 바뀐 것이 없으면 개별 감사 · 개명 행 꼴 밖 · 0C 의 개명(`rename_reds`)은 무엇보다 먼저 red."""
    py: bool = target.endswith(".py")
    keys, file_reason = audit_keys(a, b, py)
    if not keys and path != target:
        keys, file_reason = [("<file>", _digest(a), _digest(b))], "바이트 그대로 옮긴 파일"
    keys = keys + [u["key"] for u in renames or []]     # 개명 쌍마다 개별 감사 키(«개명 — 이름 뜻»)
    if not keys:
        return None
    change: str = "새 파일" if a is None else "짝 없는 삭제" if b is None else "옮김" if path != target else "수정"
    hits: "dict[str, dict]" = {}
    d_counts: "dict[str, int]" = {}
    rows: "list[str]" = []
    paths: "tuple[str, ...]" = tuple(dict.fromkeys((target, path)))

    def made(disposition: str, reason: str, touched: "tuple[str, ...]" = (), text_only: bool = False) -> Disposition:
        return Disposition(target, path, change, disposition, reason, () if disposition == RED else tuple(keys),
                           file_reason, touched, text_only, hits, d_counts, () if disposition == RED else tuple(rows),
                           () if disposition == RED else tuple(renames or ()), a if renames else None)

    if rename_reds:
        return made(RED, _join_reason(*rename_reds))
    if renames and a == b:
        return made(SINGLE_AUDIT, "개명 행 — 이름 밖 편집 없음")
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


def alias_renamed(rows: dict, renamed: "list[dict]") -> None:
    """0T 입장 표 update · remove 행(`경로::[클래스::]케이스` 열쇠)이 적용된 케이스 개명 행의 옛 이름(G1 트리 이름)을 가리키면 새 이름
    열쇠로도 읽는다(같은 값 · 새 이름으로 적은 행은 그대로 — 운영자 결정 10-24). ids · 칸 개명은 케이스 이름이 그대로다."""
    for it in renamed:
        if it.get("kind") in ("ids", FIELD_KIND):
            continue
        scope: str = f"{it['class']}::" if it.get("class") else ""
        old, new = f"{it['path']}::{scope}{it['old']}", f"{it['path']}::{scope}{it['new']}"
        if old in rows and new not in rows:
            rows[new] = rows[old]


class Judgement(NamedTuple):
    dispositions: "list[Disposition]"
    maps: Maps
    is_test: "Callable[[str], bool]"
    renamed: "tuple[dict, ...]" = ()       # 이 창이 적용한 개명 쌍(`_rename_window` 항목 + `path` = 창 당시 경로)


def judge_test_side(kind: str, changed: "dict[str, tuple[bytes | None, bytes | None]]", files_then: "set[str]",
                    files_now: "set[str]", read_then: Reader, read_now: Reader, allow: "dict | None" = None,
                    pytest_config: "tuple[dict[str, str], dict[str, str]] | None" = None) -> Judgement:
    """창의 시험 쪽 처분 전부 — 바뀐 경로(옛 · 새 바이트) · 두 판의 파일 목록 · 읽기 함수 · 허용 표(follow · change · 0T 는
    `{"remove_cases": [G1 확정판 remove_rows(v 없음)의 경로::케이스], "update_rows": [스냅숏 update_rows 그대로]}`)만 받는다.
    허용 표의 `renames`(스냅숏 개명 행 항목 · `at` = 앞 창 이동을 따라간 그 창 기준 판 경로 · `done` = 앞 창이 이미 적용)는 0T · 0F 가
    받고 0C 는 red 로 본다 — 수집 규칙은 `pytest_config`(기준 판 · 새 판 pytest 설정)로 본다. 칸 개명 항목(`source_at` = 앞 창 이동을
    따라간 운영 경로)은 0F 만 받고 운영 파일 두 판은 바뀐 경로 · 읽기 함수로 읽는다. 0T 입장 표 update · remove 행이 개명 행의
    옛 이름(G1 트리 이름)을 가리키면 개명 뒤(앞 창 · 이 창) 새 이름으로도 읽는다(운영자 결정 10-24).

    이동 전 · 후 어느 쪽이든 시험 쪽이면 처분한다(설계 :99 — 기능 모드의 분류 중립과 다르다): 시험 → 시험 이동은 옛 경로로 한 번
    (옮긴 파일) · 제품 → 시험 이동은 새 시험 쪽 파일(`<file>` · 전 없음) · 시험 → 제품 이동은 짝 없는 삭제(`<file>` · 후 없음).
    개명 쌍은 제자리에서 바뀐 시험 쪽 `.py` 에만 적용한다 — 옛 → 새 를 기준 판에 먼저 적용한 원문으로 대응표 · 처분을 돈다.
    저장소 밖(과거 커밋 재생)에서도 그대로 부른다."""
    test_dirs: "set[str]" = _test_dirs(sorted(files_now)) | _test_dirs(sorted(files_then))
    is_test: "Callable[[str], bool]" = lambda p: _is_test_refactor(p, test_dirs)  # noqa: E731
    live_now: "set[str]" = {d for p in files_now for d in _ancestors(p)}
    exports_then = _Exports(read_then, set(files_then))
    items: "list[dict]" = list((allow or {}).get("renames", [])) if kind in ("test", "code", "follow") else []
    uses_of: "dict[str, list[dict]]" = {}
    reds_of: "dict[str, list[str]]" = {}
    if items:
        given: "dict[str, tuple[bytes | None, bytes | None]]" = changed

        def sources(source: str) -> "tuple[bytes | None, bytes | None]":
            """운영 파일 두 판(칸 개명) — 바뀐 경로면 그 바이트 · 아니면 읽기 함수."""
            return given[source] if source in given else (read_then(source), read_now(source))
        changed = dict(changed)
        for p, (a, b) in sorted(changed.items()):
            mine: "list[dict]" = [it for it in items if it.get("at", it["path"]) == p and not it.get("done")]
            if not mine or a is None or b is None or not p.endswith(".py") or not is_test(p):
                continue                                    # 앞 창이 적용한 개명 행(done)은 다시 판정하지 않는다
            if pytest_config is None:
                reds_of[p] = [f"개명 행 꼴 밖 — {rename_label(it)}: 수집 규칙(pytest 설정)을 모른다 — judge_test_side 에 "
                              "pytest_config 를 넘긴다" for it in mine]
                continue
            uses, reds, renamed = _rename_window(kind, mine, a, b, p, pytest_config, sources)
            if reds:
                reds_of[p] = reds
            if uses:
                uses_of[p] = uses
                changed[p] = (renamed, b)                   # 옛 → 새 를 먼저 적용한 기준 판으로 대응표 · 처분을 돈다
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
        renamed_items: "list[dict]" = [it for it in items if it.get("done")] + [u["item"] for p in sorted(uses_of)
                                                                                for u in uses_of[p]]
        alias_renamed(approved, renamed_items)
        alias_renamed(update_rows, renamed_items)
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
                                        approved, update_rows, uses_of.get(p), reds_of.get(p))
        if disposition is not None:
            out.append(disposition)
    return Judgement(out, maps, is_test, tuple(dict(u, path=p) for p, uses in sorted(uses_of.items()) for u in uses))


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
    편집 목록 · `add`/`remove` 케이스 · «개명» 행 항목(`renames` — 개명 행이 있을 때만 칸을 둔다: 개명 행 없는 승인판의 표는 그대로)."""
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
    table: dict = {"retain_files": sorted({r["path"] for r in snap.get("retain_rows", [])}), "approved_cases": approved,
                   "ops": ops, "other_bc_edits": list(snap.get("other_bc_edits", [])), "add_cases": adds,
                   "remove_cases": removes, "V": [v["id"] for v in snap.get("V", [])]}
    renames: "list[dict]" = snap_renames(snap)
    if renames:
        table["renames"] = renames
    return table


def snap_renames(snap: dict) -> "list[dict]":
    """스냅숏의 «개명» 행 항목 전부(`retain_rows[].renames` · 표 차례)."""
    return [dict(it) for r in snap.get("retain_rows", []) for it in r.get("renames", [])]


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


def _outside_kinds(kind: str) -> str:
    """창 종류가 받는 «다른 BC 편집 목록» 갈래(보고 글) — 갈래 `묶음 import 치환` 은 0C 만 받는다(설계 10절 :478 · 검토 B8)."""
    if kind == "change":
        return f"목록 전부({GROUP_IMPORT_KIND} 빼고)"
    return " · ".join(sorted(FOLLOW_OUTSIDE_KINDS if kind == "code" else FOLLOW_OUTSIDE_KINDS - {GROUP_IMPORT_KIND}))


def _outside_allowed(kind: str, edits: "list[dict]") -> "tuple[set[str], set[str]]":
    """(대상 BC 밖에서 이 창이 고쳐도 되는 경로, 그 가운데 갈래 `묶음 import 치환` 줄로만 받은 경로)(§3-5 · §4-5 «창 종류가 허락한
    갈래만») — 0T 는 없음(루트 pytest 설정 절은 `_side_rules` 가 따로 받는다) · 0C 는 «다른 BC 편집 목록»의 프로젝트 합성 · 공유 표면 ·
    묶음 import 치환 줄 · 0F 는 프로젝트 합성 · 공유 표면 줄 · 변경 창은 묶음 import 치환 밖 목록 전부. 묶음 import 치환 줄로만 받은
    경로의 내용은 `_group_import_reds` 가 본다(그 창의 묶음 이동을 따른 import 치환만)."""
    if kind == "test":
        return set(), set()
    plain: "set[str]" = {e["path"] for e in edits if e.get("kind") != GROUP_IMPORT_KIND
                         and (kind == "change" or e.get("kind") in FOLLOW_OUTSIDE_KINDS)}
    group: "set[str]" = ({e["path"] for e in edits if e.get("kind") == GROUP_IMPORT_KIND and GROUP_IMPORT_KIND
                          in FOLLOW_OUTSIDE_KINDS} - plain) if kind == "code" else set()
    return plain | group, group


def _group_import_reds(w: "_CloseWindow") -> "list[str]":
    """갈래 `묶음 import 치환` 줄로만 받은 대상 BC 밖 경로 — 지금 글이 창 기준 글에 이 창의 묶음 이동(`folder_group.actual_moves` ·
    같은 묶음 부모 · 같은 이름 · 칸만 다름)을 따른 import 치환(`folder_group.rewrite_source` — apply · verify --window 와 같은 함수)일
    때만 받는다(설계 10절 :478 · 검토 B8). 이 창에 묶음 이동이 없으면(묶음 창이 아니면) 받을 치환이 없어 어떤 편집도 red 다."""
    touched: "list[str]" = sorted(p for p in w.group_listed if p in w.changed and not p.startswith(w.inside))
    if not touched:
        return []
    import folder_group  # noqa: PLC0415 — 묶음 이동 판정 함수(같은 스크립트 폴더)
    then: "dict[str, str]" = {p: folder_group.blob_oid(a) for p, (a, _b) in w.changed.items() if a is not None}
    now: "dict[str, str]" = {p: folder_group.blob_oid(b) for p, (_a, b) in w.changed.items() if b is not None}
    pairs: "list[tuple[str, str]]" = sorted(folder_group.actual_moves(then, now).items())
    moves: "dict[str, str]" = folder_group.module_moves(pairs)
    sub: "Callable[[str], str] | None" = folder_group.string_substituter(pairs) if pairs else None
    reds: "list[str]" = []
    for p in touched:
        before, after = (_text(x) for x in w.changed[p])
        if before is not None and after is not None and sub is not None:
            want: str = folder_group.rewrite_source(before, p, p, moves, sub) if p.endswith(".py") else sub(before)
            if after == want:
                continue
        reds.append(f"{p} — 갈래 `{GROUP_IMPORT_KIND}` 은 이 창의 묶음 이동을 따른 import 치환만 받는다(0C 묶음 창 · 이 창의 "
                    f"묶음 이동 {len(pairs)}쌍 · 설계 10절)")
    return reds


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
    renamed: "tuple[dict, ...]" = ()          # 이 창이 적용한 개명 쌍(창 기준 케이스 이름을 옛 → 새 로 읽는다)
    rename_items: "tuple[dict, ...]" = ()     # 이 창이 받은 개명 행 항목(`at` · `done` — 같은 창 이동 + 개명 알림)
    group_listed: "frozenset[str]" = frozenset()  # 갈래 `묶음 import 치환` 줄로만 받은 대상 BC 밖 경로(0C — 내용 대조)


def _renamed_cases(path: str, names: "list[str]", renamed: "tuple[dict, ...]") -> "list[str]":
    """창 기준(open) 수집 케이스 이름에 이 창이 적용한 케이스 개명(옛 → 새)을 먼저 적용한다(설계 3.1 §D3 — 그 뒤 지금 규칙)."""
    swap: "dict[str, str]" = {}
    for u in renamed:
        it: dict = u["item"]
        if u["path"] == path and it.get("kind") not in ("ids", FIELD_KIND):
            scope: str = f"{it['class']}::" if it.get("class") else ""
            swap[scope + it["old"]] = scope + it["new"]
    return [swap.get(x, x) for x in names] if swap else names


def _moved_rename_reds(w: "_CloseWindow", names_now: "set[str]") -> "list[str]":
    """같은 창의 이동과 개명 — 이 창에서 적용되지 않은 케이스 개명 행 가운데 그 파일(이 창 기준 경로)이 지금 트리에 없고(옮겼다) 옛
    이름이 창 기준 케이스 · 새 이름이 지금 케이스에 있는 것(개명은 옮긴 파일에 적용하지 않는다 — 창을 나눈다)."""
    applied: "set[str]" = {u["label"] for u in w.renamed}
    now: "set[str]" = set(w.files_now)
    out: "list[str]" = []
    for it in w.rename_items:
        at: str = str(it.get("at", it["path"]))
        scope: str = f"{it['class']}::" if it.get("class") else ""
        if it.get("kind") in ("ids", FIELD_KIND) or rename_label(it) in applied or at in now:
            continue
        if scope + it["old"] in w.opened["cases"].get(at, []) and scope + it["new"] in names_now:
            out.append(f"개명 행 `{rename_label(it)}` — 같은 창의 이동과 개명은 받지 않는다 — 창을 나눈다(이동한 창을 닫은 뒤 "
                       "다음 창에서 개명)")
    return out


def _moved_path(path: str, prior: "list[tuple[dict, dict]]") -> str:
    """개명 행 경로(G1 때)를 앞 창들의 이동(마지막 close `map_items.pairs`)을 차례로 따라가 이 창 기준 판 경로로."""
    for _opened, last in prior:
        path = (last.get("map_items") or {}).get("pairs", {}).get(path, path)
    return path


def _prior_sum(w: _CloseWindow, key: str) -> "collections.Counter[str]":
    """앞 변경 창들의 마지막 close 가 남긴 누계(연산 · 케이스 증감)."""
    return collections.Counter(x for o, last in w.prior if o.get("kind") == "change" for x in last.get(key, []))


def _side_rules(w: _CloseWindow) -> "tuple[list[str], list[str], list[str], list[str], list[str]]":
    """(red, 보고, 승인된 케이스 감소, 케이스 추가, 허용 밖 대상 BC 밖 경로) — 제품 쪽(0T 고정) · pytest 설정 · 수집 케이스 ·
    대상 BC 밖 경로(0T 는 루트 pytest 설정 절만 · 0C · 0F · 변경은 ⊆ 다른 BC 편집 목록 — 창 종류가 허락한 갈래만)."""
    kind, opened, maps, label = w.kind, w.opened, w.maps, KIND_LABELS[w.kind]
    reds: "list[str]" = []
    notes: "list[str]" = []
    cases_then: "dict[str, list[str]]" = {p: _renamed_cases(p, v, w.renamed) for p, v in opened["cases"].items()
                                          if p not in w.merged}
    cases_now: "dict[str, list[str]]" = {p: v for p, v in _cases(w.files_now, w.read_now, w.config_now, w.is_test).items()
                                         if p not in w.merged}
    before_c = collections.Counter(f"{maps.pairs.get(p, p)}::{x}" for p, v in cases_then.items() for x in v)
    after_c = collections.Counter(f"{p}::{x}" for p, v in cases_now.items() for x in v)
    gone, came = before_c - after_c, after_c - before_c
    removed_ok: "list[str]" = []
    outside: "list[str]" = []
    reds += _moved_rename_reds(w, {x for v in cases_now.values() for x in v})
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
    allowed_kinds: str = _outside_kinds(kind)
    reds += [f"{p} — 대상 BC(`{w.inside}`) 밖 경로가 다른 BC 편집 목록 밖(창 {label} 허용 갈래: {allowed_kinds})" for p in outside]
    reds += _group_import_reds(w)
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
    listed: "set[str]"
    group_listed: "set[str]"
    prior: "list[tuple[dict, dict]]" = [(o, c[-1]) for m, o, c in _windows(run_dir) if m < n and c]
    if kind in ("follow", "change"):
        current: str = _g1_state(folder, repo)[0]
        if current != opened.get("g1_digest"):
            raise RunError(f"명세 승인판 digest {current} ≠ 창 결속 {opened.get('g1_digest')} — 승인판이 바뀌었으면 "
                           "G1 변경판 확정 · rebind 뒤에 close 한다")
        allow = judge_allow = opened["allow"]
        listed, group_listed = _outside_allowed(kind, list(opened["allow"].get("other_bc_edits", [])))
        removable: "collections.Counter[str]" = collections.Counter()
        rename_items: "list[dict]" = list(opened["allow"].get("renames", [])) if kind == "follow" else []
    else:
        snap: dict = _confirmed_snapshot(folder, repo, label)
        listed, group_listed = _outside_allowed(kind, list(snap.get("other_bc_edits", [])))
        removable = collections.Counter(str(r["case"]) for r in snap.get("remove_rows", []) if r.get("v") is None)
        judge_allow = {"remove_cases": sorted(removable),
                       "update_rows": list(snap.get("update_rows", []))} if kind == "test" else None
        rename_items = snap_renames(snap)
    done: "set[str]" = {str(r.get("label")) for _o, last in prior for r in last.get("renames", [])}
    rename_items = [dict(it, at=_moved_path(it["path"], prior), done=rename_label(it) in done,
                         **({"source_at": _moved_path(str(it["source"]), prior)} if it.get("kind") == FIELD_KIND else {}))
                    for it in rename_items]
    if rename_items:                                      # 개명 행 — 0T · 0F 가 받고 0C 는 red 로 본다(변경 창 밖 · 칸은 0F 만)
        judge_allow = dict(judge_allow or {}, renames=rename_items)
    config_now: "dict[str, str]" = _pytest_config(repo)
    dirty0: "dict[str, dict]" = _record_dirty(repo, opened)

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
    judged: Judgement = judge_test_side(kind, changed, set(files_then), set(files_now), read_then, read_now, judge_allow,
                                        (opened["pytest"], config_now))
    maps, disps = judged.maps, judged.dispositions
    if kind == "test":                                    # remove 행 옛 이름 → 개명 뒤 새 이름으로도(운영자 결정 10-24)
        alias_renamed(removable, [it for it in rename_items if it["done"]] + [u["item"] for u in judged.renamed])
    window = _CloseWindow(folder, repo, kind, opened, allow, inside, listed, removable, merged, changed, maps, judged.is_test,
                          files_now,
                          read_then, read_now, config_now, prior, judged.renamed, tuple(rename_items), frozenset(group_listed))
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
    exceptions: dict = {"moved": dict(sorted(maps.pairs.items())),
                        "removed": sorted({structure_key(c) for c in removed_ok} | deleted_ok)}
    renamed: "list[dict]" = [{"path": u["path"], "class": u["item"].get("class") or None, "old": u["item"]["old"],
                              "new": u["item"]["new"]} for u in judged.renamed
                             if u["item"].get("kind") not in ("ids", FIELD_KIND)]   # ids · 칸 개명은 케이스 키 그대로
    if renamed:
        exceptions["renamed"] = renamed                   # 창 당시 경로 · 클래스 · 옛 → 새(G2 유지 대응 — behavior_support)
    closes.append({"closed": _now(), "verdict": verdict, "range": f"{head0}..{head}", "reds": reds, "notes": notes,
                   "green_files": [], "merged_excluded": _record_paths(repo, merged),
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
                   "g0_keep_exceptions": exceptions,
                   "approved_hits": hits, "ops": generated, "cases_added": cases_added, "cases_removed": removed_ok,
                   "outside_bc": outside, "existing_migrations": existing_changed,
                   "test_changed": sorted(p for p in changed if judged.is_test(p))})
    if judged.renamed:                                    # 이 창이 적용한 개명 행(verify «개명 행인데 개명 없음» 대조)
        closes[-1]["renames"] = [{"label": u["label"], **{k: v for k, v in u["item"].items() if k not in ("at", "source_at")},
                                  "path": u["path"], "unit": u["unit"], "outside": u["outside"]} for u in judged.renamed]
    _dump(run_dir / f"w{n}-close.json", closes)
    for r in reds:
        print(f"  red: {r}")
    for note in notes:
        print(f"  보고: {note}")
    state_text: str = f"red {len(reds)}건" if reds else f"감사 요청 키 {len(keys)}" if keys else "시험 쪽 무변"
    print(f"요약: 창 w{n} close {state_text} · 종류 {label} · 모드 리팩토링 · 시험 쪽 바뀐 파일 {len(disps)}"
          f"(묶음 감사 {count[BUNDLE_AUDIT]} · 개별 감사 {count[SINGLE_AUDIT]} · 승인 변경 감사 {count[APPROVED_AUDIT]} · "
          f"red {count[RED]}) · 자동 초록 0 · 바뀐 경로 {len(changed)} · 대응(쌍 {len(maps.pairs)} · 디렉터리 {len(maps.dirs)} · "
          f"모듈 {len(maps.mm)} · 정의 {len(maps.dm)} · 개명 {len(maps.rn)}) · "
          f"{f'개명 행 적용 {len(judged.renamed)} · ' if judged.renamed else ''}{migration_text} · "
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
    그 밖 단위 = `기대 의미 그대로` 만(설계 :577 · :598). 개명 키(«개명 — 이름 뜻»)는 언제나 `기대 의미 그대로` 만(설계 3.1 §D3)."""
    renamed: "set[str]" = {u["unit"] for u in d.renames}
    if d.update_rows:
        return [(MEANING_SAME,) if unit in renamed else (APPROVED_SAME, MEANING_SAME) for unit, _b, _a in d.keys]
    units: "set[str]" = {case.split("::")[1] for case, hit in d.hits.items()
                         if (hit.get("old") or hit.get("add")) and case.partition("::")[0] in (d.path, d.source)}
    return [(MEANING_SAME,) if unit in renamed else (APPROVED_SAME,) if units and (unit in units or unit == "<file>")
            else (MEANING_SAME,) for unit, _b, _a in d.keys]


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
    constants: "list[tuple[str, int, str]]" = (_string_constants(files_now, read_now, is_test)
                                               if bundles or any(d.renames for d in audited) else [])
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
        renamed: "dict[str, dict]" = {u["unit"]: u for u in d.renames}
        for unit, allowed_verdicts in zip(d.keys, required_verdicts(d)):
            note: str = ""
            spots: "list[str]" = []
            if unit[0] in renamed:                    # 옛 이름 · 옛 id 와 같은 글자가 시험 쪽 새 판 문자열 상수에 남은 자리(판정 밖)
                pair: dict = renamed[unit[0]]
                needle: str = str(pair["item"]["old"])
                spots = sorted({f"{f}:{line} «{needle}»" for f, line, value in constants if _mentions(value, needle)})
                sites: "list[int]" = pair.get("sites") or []  # 칸 개명 — 바꾼 자리 줄
                note = (f"(개명 — 이름 뜻 · 이름 밖 편집 {'있음' if pair['outside'] else '없음'} · 옛 글자 {len(spots)}자리"
                        + (f" · 바꾼 자리 {len(sites)}(줄 {' · '.join(str(x) for x in sorted(set(sites)))})" if sites else "") + ")")
            elif d.update_rows:
                note = "(0T update 행이 승인한 범위 안이면 승인 후와 같음) — " + " ; ".join(f"0T update 행 — {r}" for r in d.update_rows)
            elif allowed_verdicts == (APPROVED_SAME,):
                vs: "list[str]" = sorted({v for u, ids in vs_of.items() if u == unit[0] or unit[0] == "<file>" for v in ids})
                note = f"(후 = {' · '.join(vs)})" if vs else "(후 = 승인 V)"
            out.append(f"  - `{key_of(d, unit)}` — 요구 판정: {' · '.join(allowed_verdicts)}{note}")
            out += [f"    - 옛 글자 자리 {x}" for x in spots[:SPOT_LIMIT]] \
                + ([f"    - 옛 글자 자리 생략 {len(spots) - SPOT_LIMIT}곳"] if len(spots) > SPOT_LIMIT else [])
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
        renamed: "dict[str, dict]" = {u["unit"]: u for u in d.renames}
        for unit, _b, _a in d.keys:
            if unit in renamed:                           # 개명 키 — 옛 이름 단위(원래 기준 판) · 새 이름 단위
                pair: dict = renamed[unit]
                shown_before, shown_after = _show_unit(before, pair["before"]), _show_unit(after, pair["after"])
            else:                                         # `<file>` 은 파일 원문 전체 · 개명 쌍이 있으면 «전»은 옛 → 새 를 적용한 기준 판
                shown_before, shown_after = _show_unit(d.base if d.renames else before, unit), _show_unit(after, unit)
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
        unchanged: int = counts["observer_unchanged"]   # 실행 관찰 API 가운데 이번 실행이 바꾸지 않은 파일(설계 3판 §C2)
        split: "str | None" = record.get("observer_split")   # 갈래 판정 불능(앵커 · 이력을 못 읽음) — red 그대로 · 갈래만 모름
        if split:
            reds.append(f"suite 실행 관찰 API — 이번 실행 편집 갈래 {split}(레인 편집 여부를 가르지 못했다)")
        if unchanged:
            reds.append(f"suite 실행 관찰 API — 이번 실행이 바꾸지 않은 파일 {unchanged}: 레인이 고치지 않는다(정지 보고 · 재개 = 그 파일을 "
                        "고친 커밋을 승인 머지로 받음 → 마지막 창 close 다시 → suite → verify)")
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
        f"실행 관찰 API {counts['observer_hits']}(실린 범위 {counts['observer_files']} 파일 · "
        + (f"이번 실행 편집 갈래 {split}" if split else f"그중 이번 실행이 바꾸지 않은 파일 {unchanged}") + ") · "
        f"허용 목록 밖 {counts['nolist']}(프로젝트 훅 {counts['hooks']} 개 모두 목록 안) · 원본 못 찾음 {counts['unresolved']} · "
        f"확정 뒤 등록 {counts['late']} · 시험 기계 파일 {counts['M']} ⊆ 시험 쪽 · xdist 일꾼 출력 {outputs}/{ready} · "
        f"G0 유지(구조 키 — 파일 · 바이트 같은 항목 · 바뀐 파일 함수마다 처분 수{f' — 어긋남 {len(g0_keep)}' if g0_keep else ''}) · "
        + (f"개명 케이스 skip {counts['renamed_skip']}(보고 — 개명된 새 키가 G2 에서 skip · xfail) · " if "renamed_skip" in counts else "")
        + f"지문 마지막 close {eq(same)} 시작 = 명령 사이 = 끝 = 지금")
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
        rename_rows: "list[dict]" = list(allow.get("renames", []))
        applied: "set[str]" = {str(r.get("label")) for _n, _o, closes in windows if closes
                               for r in closes[-1].get("renames", [])}
        unapplied: "list[str]" = [rename_label(it) for it in rename_rows if rename_label(it) not in applied]
        reds += [f"개명 행인데 개명 없음 — {x}(어느 창의 마지막 close 에도 적용되지 않았다)" for x in unapplied]
        line_change = (f"바뀐 것 실행: 승인 V {len(allow['V'])}건 · 연산 승인 {sum(approved_ops.values())} "
                       f"{'=' if generated == approved_ops else '≠'} 생성 {sum(generated.values())}(다중집합) · "
                       f"기존 마이그레이션 변경 {existing} · 승인 기대 원소 {expected} 중 변경 {changed_count} · "
                       f"목록 밖 다른 BC 파일 {outside} · digest {confirmed[1]} {'=' if digest_ok else '≠'} G1 변경판 확정"
                       + (f" · 개명 행 {len(rename_rows)} 중 적용 {len(rename_rows) - len(unapplied)}" if rename_rows else ""))
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
