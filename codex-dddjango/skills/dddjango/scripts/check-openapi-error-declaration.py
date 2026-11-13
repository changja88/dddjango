#!/usr/bin/env python3
"""dddjango OpenAPI 오류 계약 결정적 백스톱.

positional/auto/preserve 실행은 기존 ``openapi_extra.responses`` 저장소 전수
검사를 보존한다. ``dddjango-code-json`` profile은 선택된 operation이 직접 반환하는
BC 오류와 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·``Union``·명시값 base —
base 뭉뚱그림 금지 · 2026-08-25)의 ``response=`` 선언의 일치를 검증하고, 선택 API
module의 수동 OpenAPI 후처리를 차단한다.

경로 앞 응답(F4-173 · 2026-11-13 — 모든 프로필): API 문서는 그 경로에서 날 수 있는 의도된
오류를 누가 보내든 모두 적는다. 루트 API 모듈의 정해진 클래스 하나(a) · 플러그인 정본과 프로젝트
표(b) · 그 꼴이 없을 때 operation 마다 «경로 앞 오류가 문서에 없다»(c) · 프로젝트 미들웨어 답 ↔
표(d) · `openapi_extra` 머리 보충(e) · 주입 응답 머리 ↔ 머리 보충(f) · 직접 반환하지 않는 4xx·5xx
광고(g, code 레인)를 본다.

종료코드: 0=clean, 1=사용/분석 오류, 2=blocker.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 위반 라인과 레코드는 공용 포매터(출력 계약 v2 — ordered emitter)가
같은 순서로 산출하고, 전 위반의 귀속은 #63 하나다(rule-owner-map). 앵커 실행의
tree↔code 동일 사건 이중 방출은 tree 사이트 선점 억제로 막는다(귀속 매핑표 v2
overlap 절 — U14).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#74 → djr:R-3229.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import stat
import subprocess
import sys

import checker_target
from findings import Candidates, Findings, emit_all, lines, zero_target_guard
from dataclasses import dataclass, field
from http import HTTPStatus
from pathlib import Path
from typing import Callable


try:
    import anchor_diff
    import standard_tree as _stree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/anchor_diff.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
HTTP_STATUS_CONSTANT_RE = re.compile(r"^HTTP_([1-5]\d\d)(?:_|$)")
STATIC_LITERAL_PREFIX = "@static-literal:"
HTTP_METHODS = {"delete", "get", "head", "options", "patch", "post", "put"}
ROOT_API_CONSTRUCTORS = {"ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"}
COMMON_ERROR_MODULE = "framework.ninja.framework_error_schema"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.FrameworkErrorSchema"
COMMON_ERROR_PATH = Path("framework/ninja/framework_error_schema.py")
PRE_ROUTE_SECTION = "implementation-django-ninja §6.2 «경로 앞 응답»"
SUPPLEMENT_SECTION = "implementation-django-ninja §6.2 «머리 보충»"

SKIP_DIRS = {
    ".venv",
    "venv",
    "site-packages",
    "node_modules",
    ".git",
    "__pycache__",
}
TEST_DIR_NAMES = {"test", "tests"}
CODE_SKIP_DIRS = {
    *SKIP_DIRS,
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "migrations",
    "generated",
}
NINJA_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+ninja(?:_extra)?(?:\.\w+)*\s+import|import\s+ninja(?:_extra)?)\b",
    re.MULTILINE,
)
FIELD_FACTORIES = {
    "ninja.Field",
    "pydantic.Field",
    "pydantic.fields.Field",
}
ALIAS_CHOICES_FACTORIES = {
    "pydantic.AliasChoices",
    "pydantic.aliases.AliasChoices",
}

ROUTER_INSTANCE = "@ninja-router-instance"
API_TYPE_PREFIX = "@ninja-api-type:"
API_RECEIVER = "@selected-api-receiver"
API_SCHEMA_METHOD = "@selected-api-schema-method"
BUILTIN_SETATTR = "@builtin-setattr"
AMBIGUOUS_API_SCHEMA_METHOD = "@ambiguous-selected-api-schema-method"
AMBIGUOUS_BINDING = "@ambiguous-binding"
AMBIGUOUS_ERROR_INSTANCE = "@ambiguous-error-instance"
MATCH_NODE = getattr(ast, "Match", None)
MATCH_AS = getattr(ast, "MatchAs", None)
MATCH_OR = getattr(ast, "MatchOr", None)
MATCH_VALUE = getattr(ast, "MatchValue", None)
MATCH_SINGLETON = getattr(ast, "MatchSingleton", None)
MATCH_STAR = getattr(ast, "MatchStar", None)
MATCH_MAPPING = getattr(ast, "MatchMapping", None)
TRY_STAR_NODE = getattr(ast, "TryStar", None)


class UsageError(Exception):
    """CLI, inventory, or required provenance failure."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True)
class Config:
    root: Path
    profile: str | None
    scope: str | None
    api_module: str | None
    controller_modules: tuple[str, ...]
    scope_bcs: tuple[str, ...]
    error_bcs: tuple[str, ...]
    anchor: str | None
    anchor_debt_file: str | None
    anchor_approved_merge_file: str | None = None
    anchor_baseline: bool = False


@dataclass(frozen=True)
class CodeInventory:
    relative_paths: tuple[Path, ...]
    git_root: Path | None


@dataclass(frozen=True)
class ParsedSource:
    relative_path: Path
    source: str
    tree: ast.Module


@dataclass(frozen=True)
class StatusSpec:
    expression: ast.expr | None
    bindings: dict[str, str]
    relative_path: Path


@dataclass(frozen=True)
class ErrorSymbol:
    full_path: str
    bc: str | None
    kind: str
    field_defaults: dict[str, StatusSpec] | None = None
    constructor_fields_by_key: dict[str, str] | None = None
    constructor_keys_complete: bool = True


@dataclass(frozen=True)
class ErrorInstance:
    symbol: ErrorSymbol
    direct_status: int | None = None
    alias_depth: int = 0
    field_values: tuple[tuple[str, StatusSpec], ...] = ()


@dataclass
class ProvenanceState:
    bindings: dict[str, str]
    instances: dict[str, ErrorInstance | str]
    falls_through: bool = True


@dataclass(frozen=True)
class Operation:
    relative_path: Path
    owners: tuple[str, ...]
    function: ast.FunctionDef | ast.AsyncFunctionDef
    decorator: ast.Call
    bindings: dict[str, str]
    body_bindings: dict[str, str]
    annotations_evaluated: bool
    type_aliases: "dict[str, tuple[ast.expr, dict[str, str]]]" = field(default_factory=dict)  # 이름 → (식, 별칭 문장 앞 바인딩)

    @property
    def identity(self) -> str:
        owner = ".".join((*self.owners, self.function.name))
        return f"{self.relative_path}:{self.decorator.lineno}:{owner}"


@dataclass(frozen=True)
class Finding:
    # 라인 판형은 공용 포매터 소유(출력 계약 v2) — 자체 render 를 두지 않는다.
    # symbol 은 확정 재료가 있는 사이트만 채운다(Operation → function.name ·
    # override FunctionDef → .name — 없으면 None · 귀속 매핑표 v2 부속 A-1).
    relative_path: Path
    lineno: int
    category: str
    detail: str
    symbol: str | None = None


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--error-profile", action="append")
    parser.add_argument("--scope", action="append")
    parser.add_argument("--api-module", action="append")
    parser.add_argument("--controller-module", action="append", default=[])
    parser.add_argument("--scope-bc", action="append", default=[])
    parser.add_argument("--error-bc", action="append", default=[])
    # 판정 차분(anchor_diff) — 신규분만 blocker·앵커 기존분은 보고 강등(2026-08-15 r2″).
    parser.add_argument("--anchor", default=None)
    parser.add_argument(anchor_diff.BASELINE_FLAG, action="store_true", dest="anchor_baseline")
    parser.add_argument(anchor_diff.DEBT_FLAG, dest="anchor_debt_file", default=None)
    return parser


def _one(
    option: str,
    values: list[str] | None,
    *,
    required: bool,
    issues: list[str],
) -> str | None:
    actual = values or []
    if required and not actual:
        issues.append(f"필수 인자 누락: {option}")
        return None
    if len(actual) > 1:
        issues.append(f"단일 인자 중복: {option}")
    return actual[0] if actual else None


def _unique(option: str, values: list[str], issues: list[str]) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        issues.append(f"반복 인자 중복: {option}")
    return tuple(values)


def _validate_selected_source(
    root: Path,
    option: str,
    raw: str,
    *,
    strict_content: bool,
    issues: list[str],
) -> Path | None:
    relative = Path(raw)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.as_posix() != raw
        or "/" not in raw
        or relative.suffix != ".py"
    ):
        issues.append(f"잘못된 source path: {option}={raw}")
        return None
    try:
        resolved = (root / relative).resolve()
    except (OSError, RuntimeError) as exc:
        issues.append(f"source path resolve 불능: {option}={raw} ({exc})")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        issues.append(f"root/symlink 탈출: {option}={raw}")
        return None
    if not resolved.is_file():
        issues.append(f"선택 source 없음: {option}={raw}")
        return None
    if strict_content:
        try:
            source = resolved.read_text(encoding="utf-8")
            ast.parse(source, filename=raw)
        except (OSError, UnicodeError, SyntaxError) as exc:
            issues.append(f"선택 source 분석 불능: {option}={raw} ({exc})")
            return None
    return resolved


def _parse_config(argv: list[str]) -> Config:
    approved_merge_file: "str | None" = None
    approved_merge_error: "str | None" = None
    if any(t == anchor_diff.APPROVED_MERGE_FLAG or t.startswith(anchor_diff.APPROVED_MERGE_FLAG + "=") for t in argv):
        # 플래그가 있을 때만 새 함수를 부른다 — 플래그 없는 실행은 2.21.1 과 같은 argv·같은 anchor_diff 이름만 쓴다.
        argv, approved_merge_file, approved_merge_error = anchor_diff.split_approved_merge(argv)
    namespace = _argument_parser().parse_args(argv)
    namespace.anchor_approved_merge_file: str | None = approved_merge_file
    try:
        root = Path(namespace.target).resolve()
        root_is_dir = root.is_dir()
    except (OSError, RuntimeError) as exc:
        raise UsageError(f"TARGET_DIR resolve 불능: {namespace.target} ({exc})") from exc
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        raise UsageError(bad_target_reason)
    if not root_is_dir:
        raise UsageError(f"디렉터리 아님 {root}")

    issues: list[str] = []
    profile = _one(
        "--error-profile", namespace.error_profile, required=False, issues=issues
    )
    selectors_present = any(
        (
            namespace.scope,
            namespace.api_module,
            namespace.controller_module,
            namespace.scope_bc,
            namespace.error_bc,
        )
    )
    if profile is None and selectors_present:
        issues.append("selector 사용 시 --error-profile 필수")
    if profile is not None and profile not in ERROR_PROFILES:
        issues.append(f"지원하지 않는 --error-profile: {profile}")
    if profile == "auto" and selectors_present:
        issues.append("auto profile에는 scope/source/BC selector를 전달하지 않음")

    if namespace.anchor is not None and namespace.anchor_baseline:
        issues.append(f"--anchor 와 {anchor_diff.BASELINE_FLAG} 는 함께 전달할 수 없음")
    if namespace.anchor_debt_file is not None and namespace.anchor is None:
        issues.append(f"{anchor_diff.DEBT_FLAG} 는 --anchor 와 함께만 쓸 수 있음(차분 전용 빚 채널)")
    if namespace.anchor_approved_merge_file is not None and namespace.anchor is None:
        issues.append(f"{anchor_diff.APPROVED_MERGE_FLAG} 는 --anchor 와 함께만 쓸 수 있음(차분 전용 승인 유입 채널)")
    if approved_merge_error is not None:
        issues.append(approved_merge_error)
    if namespace.anchor_baseline and anchor_diff.is_git_worktree(root):
        issues.append(
            f"{anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용 — git 저장소 TARGET 금지"
        )
    explicit = profile in {"dddjango-code-json", "preserve-established"}
    strict_content = profile == "dddjango-code-json"
    scope = _one("--scope", namespace.scope, required=explicit, issues=issues)
    # anchor-baseline 모드에선 앵커 트리에 없는 api 모듈(새 scope 의 API 인스턴스)이 걷혀 없는 것이 정상이다.
    api_module = _one(
        "--api-module", namespace.api_module,
        required=explicit and not namespace.anchor_baseline, issues=issues
    )
    controller_modules = _unique(
        "--controller-module", namespace.controller_module, issues
    )
    scope_bcs = _unique("--scope-bc", namespace.scope_bc, issues)
    error_bcs = _unique("--error-bc", namespace.error_bc, issues)
    if explicit and not controller_modules and not namespace.anchor_baseline:
        # anchor-baseline 모드에선 앵커 트리에 없는 controller 가 걷혀 빈 집합이 정상이다.
        issues.append("필수 인자 누락: --controller-module")
    if explicit and not scope_bcs and not namespace.anchor_baseline:
        issues.append("필수 인자 누락: --scope-bc")
    if scope is not None and not scope.strip():
        issues.append("--scope는 빈 문자열일 수 없음")
    for option, names in (("--scope-bc", scope_bcs), ("--error-bc", error_bcs)):
        for name in names:
            if not BC_NAME_RE.fullmatch(name):
                issues.append(f"잘못된 BC 이름: {option}={name}")
    if not set(error_bcs).issubset(scope_bcs):
        issues.append("--error-bc는 --scope-bc의 부분집합이어야 함")

    resolved_by_role: dict[str, list[Path]] = {"api": [], "controller": []}
    if api_module is not None:
        selected = _validate_selected_source(
            root,
            "--api-module",
            api_module,
            strict_content=strict_content,
            issues=issues,
        )
        if selected is not None:
            resolved_by_role["api"].append(selected)
    for raw in controller_modules:
        selected = _validate_selected_source(
            root,
            "--controller-module",
            raw,
            strict_content=strict_content,
            issues=issues,
        )
        if selected is not None:
            resolved_by_role["controller"].append(selected)
    if set(resolved_by_role["api"]) & set(resolved_by_role["controller"]):
        issues.append("--api-module과 --controller-module 역할 overlap")
    all_selected = resolved_by_role["api"] + resolved_by_role["controller"]
    if len(all_selected) != len(set(all_selected)):
        issues.append("선택 source가 같은 resolved path를 중복 지정함")

    if issues:
        raise UsageError("; ".join(issues))
    return Config(
        root=root,
        profile=profile,
        scope=scope,
        api_module=api_module,
        controller_modules=controller_modules,
        scope_bcs=scope_bcs,
        error_bcs=error_bcs,
        anchor=namespace.anchor,
        anchor_debt_file=namespace.anchor_debt_file,
        anchor_approved_merge_file=namespace.anchor_approved_merge_file,
        anchor_baseline=namespace.anchor_baseline,
    )


def _is_code_production_path(relative_path: Path) -> bool:
    parts = relative_path.parts
    return (
        relative_path.suffix == ".py"
        and not set(parts) & CODE_SKIP_DIRS
        and not set(parts) & TEST_DIR_NAMES
        and not relative_path.name.startswith("test_")
        and not relative_path.name.endswith("_test.py")
        and relative_path.name not in {"test.py", "tests.py", "conftest.py"}
    )


def _filesystem_code_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    walk_errors: list[str] = []

    def record_walk_error(exc: OSError) -> None:
        walk_errors.append(str(exc))

    for directory, names, filenames in os.walk(
        root, topdown=True, followlinks=False, onerror=record_walk_error
    ):
        directory_path = Path(directory)
        try:
            directory_relative = directory_path.relative_to(root)
        except ValueError as exc:
            raise UsageError(f"inventory root 탈출: {directory_path}") from exc
        names[:] = sorted(
            name
            for name in names
            if not set((*directory_relative.parts, name)) & CODE_SKIP_DIRS
            and name not in TEST_DIR_NAMES
        )
        for filename in sorted(filenames):
            relative_path = directory_relative / filename
            if _is_code_production_path(relative_path):
                paths.append(relative_path)
    if walk_errors:
        raise UsageError(f"production inventory 탐색 불능: {'; '.join(walk_errors)}")
    return tuple(sorted(paths, key=Path.as_posix))


def _has_git_marker(root: Path) -> bool:
    for directory in (root, *root.parents):
        marker = directory / ".git"
        try:
            mode = marker.stat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise UsageError(f"Git marker 접근 불능: {marker} ({exc})") from exc
        if stat.S_ISDIR(mode) or stat.S_ISREG(mode):
            return True
    return False


def _code_inventory(root: Path) -> CodeInventory:
    try:
        probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise UsageError(f"Git worktree 판정 불능: {exc}") from exc
    if probe.returncode != 0:
        if _has_git_marker(root):
            detail = probe.stderr.strip() or probe.stdout.strip()
            raise UsageError(f"Git worktree 판정 불능: {detail}")
        return CodeInventory(_filesystem_code_paths(root), None)
    if probe.stdout.strip() != "true":
        return CodeInventory(_filesystem_code_paths(root), None)

    top_level = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if top_level.returncode != 0:
        detail = top_level.stderr.strip() or top_level.stdout.strip()
        raise UsageError(f"Git worktree root 분석 불능: {detail}")
    try:
        git_root = Path(top_level.stdout.strip()).resolve()
        target_prefix = root.relative_to(git_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise UsageError(f"Git worktree root/target 관계 분석 불능: {exc}") from exc

    try:
        listed = subprocess.run(
            [
                "git",
                "-C",
                str(git_root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UsageError(f"Git production inventory 불능: {exc}") from exc
    if listed.returncode != 0:
        detail = os.fsdecode(listed.stderr).strip() or os.fsdecode(listed.stdout).strip()
        raise UsageError(f"Git production inventory 불능: {detail}")

    relative_paths: list[Path] = []
    for encoded in listed.stdout.split(b"\0"):
        if not encoded:
            continue
        git_relative = Path(os.fsdecode(encoded))
        if git_relative.is_absolute() or ".." in git_relative.parts:
            raise UsageError(f"Git inventory 경로 불능: {git_relative}")
        try:
            target_relative = git_relative.relative_to(target_prefix)
        except ValueError:
            continue
        if _is_code_production_path(target_relative):
            relative_paths.append(target_relative)
    if len(relative_paths) != len(set(relative_paths)):
        raise UsageError("Git production inventory에 중복 경로가 있음")
    return CodeInventory(
        tuple(sorted(relative_paths, key=Path.as_posix)), git_root
    )


def _code_source_paths(config: Config) -> tuple[CodeInventory, tuple[Path, ...]]:
    inventory = _code_inventory(config.root)
    inventory_paths = set(inventory.relative_paths)
    required = [Path(config.api_module)] if config.api_module is not None else []
    required.extend(Path(raw) for raw in config.controller_modules)
    required.append(COMMON_ERROR_PATH)
    if config.error_bcs:
        required.extend(
            Path(f"application/{bc}/driving_layer/api/bc_error_schema.py")
            for bc in config.error_bcs
        )
    issues = [
        f"선택/필수 source가 production inventory에 없음: {path}"
        for path in required
        if path not in inventory_paths
    ]
    if issues:
        raise UsageError("; ".join(sorted(set(issues))))
    if len(required) != len(set(required)):
        raise UsageError("선택/필수 source path 중복")
    return inventory, tuple(required)


def _parse_code_sources(config: Config) -> dict[Path, ParsedSource]:
    _, relative_paths = _code_source_paths(config)
    parsed: dict[Path, ParsedSource] = {}
    resolved_paths: dict[Path, Path] = {}
    issues: list[str] = []
    for relative_path in relative_paths:
        lexical = config.root / relative_path
        try:
            resolved = lexical.resolve()
            resolved.relative_to(config.root)
        except ValueError:
            issues.append(f"production source root/symlink 탈출: {relative_path}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(f"production source resolve 불능: {relative_path} ({exc})")
            continue
        previous = resolved_paths.get(resolved)
        if previous is not None:
            issues.append(f"production source resolved path 중복: {previous}, {relative_path}")
            continue
        resolved_paths[resolved] = relative_path
        try:
            source = resolved.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative_path.as_posix())
        except (OSError, UnicodeError, SyntaxError) as exc:
            issues.append(f"production source 분석 불능: {relative_path} ({exc})")
            continue
        parsed[relative_path] = ParsedSource(relative_path, source, tree)
    if issues:
        raise UsageError("; ".join(sorted(set(issues))))
    return parsed


def _scan_is_production_path(relative_path: Path) -> bool:
    return (
        relative_path.suffix == ".py"
        and bool(_TREE_DRIVING_SET & set(relative_path.parts))
        and not set(relative_path.parts) & CODE_SKIP_DIRS
        and not set(relative_path.parts) & TEST_DIR_NAMES
        and not relative_path.name.startswith("test_")
        and relative_path.name not in {"test.py", "tests.py", "conftest.py"}
    )


def _scan_is_ignored_untracked(root: Path, relative_path: Path) -> bool:
    if not (root / ".git").exists():
        return False
    try:
        tracked = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--error-unmatch",
                "--",
                relative_path.as_posix(),
            ],
            capture_output=True,
            check=False,
        )
        if tracked.returncode == 0:
            return False
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "check-ignore",
                "--quiet",
                "--",
                relative_path.as_posix(),
            ],
            capture_output=True,
            check=False,
        )
        return ignored.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _scan_driving_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*.py"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if not _scan_is_production_path(relative):
            continue
        if _scan_is_ignored_untracked(root, relative):
            continue
        paths.append(path)
    return sorted(paths)


def _literal_status(node: ast.AST) -> int | None:
    if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
        return None
    if isinstance(node.value, int):
        return node.value
    if isinstance(node.value, str) and node.value.isdigit():
        return int(node.value)
    return None


def _scan_operations(source: str, relative_path: Path) -> list[str]:
    if not NINJA_IMPORT_RE.search(source):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: list[str] = []
    bindings = _final_module_symbol_bindings(ParsedSource(relative_path, source, tree))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            for keyword in decorator.keywords:
                if keyword.arg != "openapi_extra":
                    continue
                problems = _extra_problems(keyword.value, tree, _declared_response_statuses(node, bindings))
                if problems:
                    findings.append(
                        f"operation '{node.name}' (openapi_extra responses 보충 — {' · '.join(problems)})"
                    )
    return findings


def _scan_is_new_or_modified(root: Path, file_path: Path) -> bool:
    if not (root / ".git").exists():
        return True
    try:
        relative = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        tracked = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--error-unmatch",
                str(relative),
            ],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(relative)]
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True


def _repo_scan_findings(root: Path) -> Findings:
    # repo 스캔 레인도 #63 violation 문법이다(where=경로 성분 · msg=사유) — 방출은
    # 호출측 emit_all 이 한 순서로 수행한다(출력 계약 v2).
    findings = Findings(defer=True)
    for path in _scan_driving_files(root):
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = _scan_operations(source, path.relative_to(root))
        if hits and _scan_is_new_or_modified(root, path):
            findings.add("#63", where=path.relative_to(root), msg="; ".join(hits))
    return findings


def _expression_dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _expression_dotted_name(node.value)
        if owner is not None:
            return f"{owner}.{node.attr}"
    return None


def _absolute_from_module(relative_path: Path, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module
    package = list(relative_path.parent.parts)
    drop = node.level - 1
    if drop > len(package):
        return None
    if drop:
        package = package[:-drop]
    if node.module:
        package.extend(node.module.split("."))
    return ".".join(package) or None


def _resolve_expression(node: ast.AST, bindings: dict[str, str]) -> str | None:
    dotted = _expression_dotted_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    bound = bindings.get(first)
    if bound is None:
        return None
    if bound.startswith(STATIC_LITERAL_PREFIX):
        return bound if not rest else None
    return ".".join((bound, *rest))


def _static_literal_binding(value: object) -> str:
    return f"{STATIC_LITERAL_PREFIX}{type(value).__name__}:{value!r}"


def _static_literal_value(binding: str | None) -> object:
    if binding is None or not binding.startswith(STATIC_LITERAL_PREFIX):
        return _NO_STATIC_VALUE
    payload = binding.removeprefix(STATIC_LITERAL_PREFIX)
    type_name, separator, literal = payload.partition(":")
    if not separator:
        return _NO_STATIC_VALUE
    try:
        value = ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return _NO_STATIC_VALUE
    return value if type(value).__name__ == type_name else _NO_STATIC_VALUE


_NO_STATIC_VALUE = object()


def _merge_bindings(states: list[dict[str, str]]) -> dict[str, str]:
    """Keep only provenance shared by every possible control-flow outcome."""
    if not states:
        return {}
    missing = object()
    merged: dict[str, str] = {}
    for name in set().union(*(state.keys() for state in states)):
        values = [state.get(name, missing) for state in states]
        first = values[0]
        if first is not missing and all(value == first for value in values[1:]):
            merged[name] = first
        elif any(value is not missing for value in values):
            present = {value for value in values if value is not missing}
            merged[name] = (
                AMBIGUOUS_API_SCHEMA_METHOD
                if API_SCHEMA_METHOD in present
                else AMBIGUOUS_BINDING
            )
    return merged


def _is_ambiguous_resolution(resolved: str | None) -> bool:
    return resolved in {AMBIGUOUS_BINDING, AMBIGUOUS_API_SCHEMA_METHOD} or (
        resolved is not None
        and resolved.startswith(
            (f"{AMBIGUOUS_BINDING}.", f"{AMBIGUOUS_API_SCHEMA_METHOD}.")
        )
    )


def _copy_provenance(state: ProvenanceState) -> ProvenanceState:
    return ProvenanceState(
        dict(state.bindings),
        dict(state.instances),
        state.falls_through,
    )


def _merge_instances(
    states: list[dict[str, ErrorInstance | str]],
) -> dict[str, ErrorInstance | str]:
    if not states:
        return {}
    missing = object()
    merged: dict[str, ErrorInstance | str] = {}
    for name in set().union(*(state.keys() for state in states)):
        values = [state.get(name, missing) for state in states]
        first = values[0]
        if first is not missing and all(value == first for value in values[1:]):
            merged[name] = first
        elif any(value is not missing for value in values):
            merged[name] = AMBIGUOUS_ERROR_INSTANCE
    return merged


def _merge_provenance(states: list[ProvenanceState]) -> ProvenanceState:
    reachable = [state for state in states if state.falls_through]
    merged = reachable or states
    return ProvenanceState(
        _merge_bindings([state.bindings for state in merged]),
        _merge_instances([state.instances for state in merged]),
        bool(reachable),
    )


def _drop_provenance_names(state: ProvenanceState, names: set[str]) -> None:
    for name in names:
        state.bindings.pop(name, None)
        state.instances.pop(name, None)


def _pattern_capture_names(pattern: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(pattern):
        if MATCH_AS is not None and isinstance(node, MATCH_AS) and node.name:
            names.add(node.name)
        elif MATCH_STAR is not None and isinstance(node, MATCH_STAR) and node.name:
            names.add(node.name)
        elif (
            MATCH_MAPPING is not None
            and isinstance(node, MATCH_MAPPING)
            and node.rest
        ):
            names.add(node.rest)
    return names


def _irrefutable_pattern(pattern: ast.AST) -> bool:
    if MATCH_AS is not None and isinstance(pattern, MATCH_AS):
        return pattern.pattern is None or _irrefutable_pattern(pattern.pattern)
    if MATCH_OR is not None and isinstance(pattern, MATCH_OR):
        return any(_irrefutable_pattern(item) for item in pattern.patterns)
    return False


def _literal_pattern_value(pattern: ast.AST) -> tuple[bool, object]:
    if MATCH_VALUE is not None and isinstance(pattern, MATCH_VALUE):
        if isinstance(pattern.value, ast.Constant):
            return True, pattern.value.value
    if MATCH_SINGLETON is not None and isinstance(pattern, MATCH_SINGLETON):
        return True, pattern.value
    return False, None


def _match_outcomes(statement: ast.AST) -> tuple[set[int], bool]:
    cases = statement.cases
    if isinstance(statement.subject, ast.Constant):
        subject = statement.subject.value
        for index, case in enumerate(cases):
            known, value = _literal_pattern_value(case.pattern)
            if case.guard is None and known and value == subject:
                return {index}, False
            if case.guard is None and _irrefutable_pattern(case.pattern):
                return {index}, False
            if not known:
                break
    exhaustive = any(
        case.guard is None and _irrefutable_pattern(case.pattern) for case in cases
    )
    return set(range(len(cases))), not exhaustive


def _is_try_statement(statement: ast.stmt) -> bool:
    return isinstance(statement, ast.Try) or (
        TRY_STAR_NODE is not None and isinstance(statement, TRY_STAR_NODE)
    )


def _evaluate_flow_expression(
    expression: ast.AST,
    state: ProvenanceState,
    *,
    annotations_evaluated: bool,
    on_expression: Callable[[ast.AST, ProvenanceState], None] | None,
) -> None:
    if on_expression is not None:
        on_expression(expression, state)
    wrapper = ast.Expr(value=expression)
    _drop_provenance_names(
        state,
        _evaluated_named_expression_names(
            wrapper,
            annotations_evaluated=annotations_evaluated,
        ),
    )


def _statement_provenance_flow(
    statements: list[ast.stmt],
    incoming: ProvenanceState,
    *,
    annotations_evaluated: bool,
    on_simple: Callable[[ast.stmt, ProvenanceState], None],
    on_function: Callable[[ast.stmt, ProvenanceState], None] | None = None,
    on_class: Callable[[ast.ClassDef, ProvenanceState], None] | None = None,
    on_expression: Callable[[ast.AST, ProvenanceState], None] | None = None,
) -> ProvenanceState:
    state = _copy_provenance(incoming)

    def flow(block: list[ast.stmt], start: ProvenanceState) -> ProvenanceState:
        return _statement_provenance_flow(
            block,
            start,
            annotations_evaluated=annotations_evaluated,
            on_simple=on_simple,
            on_function=on_function,
            on_class=on_class,
            on_expression=on_expression,
        )

    for statement in statements:
        if not state.falls_through:
            break
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if on_function is None:
                on_simple(statement, state)
            else:
                on_function(statement, state)
            continue
        if isinstance(statement, ast.ClassDef):
            if on_class is None:
                on_simple(statement, state)
            else:
                on_class(statement, state)
            continue
        if isinstance(statement, (ast.If, ast.While)):
            branch = _copy_provenance(state)
            _evaluate_flow_expression(
                statement.test,
                branch,
                annotations_evaluated=annotations_evaluated,
                on_expression=on_expression,
            )
            outcomes = [flow(statement.body, branch), flow(statement.orelse, branch)]
            if isinstance(statement, ast.While):
                outcomes.append(branch)
            state = _merge_provenance(outcomes)
            continue
        if isinstance(statement, (ast.For, ast.AsyncFor)):
            branch = _copy_provenance(state)
            _evaluate_flow_expression(
                statement.iter,
                branch,
                annotations_evaluated=annotations_evaluated,
                on_expression=on_expression,
            )
            _drop_provenance_names(branch, _target_names(statement.target))
            body_out = flow(statement.body, branch)
            state = _merge_provenance(
                [flow(statement.orelse, state), flow(statement.orelse, body_out)]
            )
            continue
        if isinstance(statement, (ast.With, ast.AsyncWith)):
            branch = _copy_provenance(state)
            for item in statement.items:
                _evaluate_flow_expression(
                    item.context_expr,
                    branch,
                    annotations_evaluated=annotations_evaluated,
                    on_expression=on_expression,
                )
                if item.optional_vars is not None:
                    _drop_provenance_names(
                        branch, _target_names(item.optional_vars)
                    )
            state = flow(statement.body, branch)
            continue
        if _is_try_statement(statement):
            normal = flow(statement.body, state)
            outcomes = [flow(statement.orelse, normal)]
            for handler in statement.handlers:
                branch = _copy_provenance(state)
                if handler.type is not None:
                    _evaluate_flow_expression(
                        handler.type,
                        branch,
                        annotations_evaluated=annotations_evaluated,
                        on_expression=on_expression,
                    )
                if handler.name:
                    _drop_provenance_names(branch, {handler.name})
                outcomes.append(flow(handler.body, branch))
            pending = _merge_provenance(outcomes)
            pending_falls_through = pending.falls_through
            pending.falls_through = True
            state = flow(statement.finalbody, pending)
            state.falls_through = pending_falls_through and state.falls_through
            continue
        if MATCH_NODE is not None and isinstance(statement, MATCH_NODE):
            base = _copy_provenance(state)
            _evaluate_flow_expression(
                statement.subject,
                base,
                annotations_evaluated=annotations_evaluated,
                on_expression=on_expression,
            )
            reachable, include_unmatched = _match_outcomes(statement)
            outcomes: list[ProvenanceState] = []
            for index, case in enumerate(statement.cases):
                if index not in reachable:
                    continue
                branch = _copy_provenance(base)
                _drop_provenance_names(
                    branch, _pattern_capture_names(case.pattern)
                )
                if case.guard is not None:
                    _evaluate_flow_expression(
                        case.guard,
                        branch,
                        annotations_evaluated=annotations_evaluated,
                        on_expression=on_expression,
                    )
                outcomes.append(flow(case.body, branch))
            if include_unmatched:
                outcomes.append(base)
            state = _merge_provenance(outcomes)
            continue
        on_simple(statement, state)
        if isinstance(statement, ast.Return):
            state.falls_through = False
    return state


def _bindings_after_block(
    statements: list[ast.stmt],
    incoming: dict[str, str],
    relative_path: Path,
    *,
    recognize_router: bool,
    annotations_evaluated: bool,
) -> dict[str, str]:
    def advance(statement: ast.stmt, state: ProvenanceState) -> None:
        _advance_bindings(
            statement,
            relative_path,
            state.bindings,
            recognize_router=recognize_router,
            annotations_evaluated=annotations_evaluated,
        )

    return _statement_provenance_flow(
        statements,
        ProvenanceState(dict(incoming), {}),
        annotations_evaluated=annotations_evaluated,
        on_simple=advance,
    ).bindings


def _target_names(target: ast.AST) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for element in target.elts for name in _target_names(element)}
    return set()


def _direct_bound_names(statement: ast.stmt) -> set[str]:
    if isinstance(statement, ast.Import):
        return {alias.asname or alias.name.split(".", 1)[0] for alias in statement.names}
    if isinstance(statement, ast.ImportFrom):
        return {
            alias.asname or alias.name
            for alias in statement.names
            if alias.name != "*"
        }
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {statement.name}
    if isinstance(statement, ast.Assign):
        return {
            name for target in statement.targets for name in _target_names(target)
        }
    if isinstance(statement, ast.AnnAssign):
        return _target_names(statement.target) if statement.value is not None else set()
    if isinstance(statement, ast.AugAssign):
        return _target_names(statement.target)
    if isinstance(statement, (ast.For, ast.AsyncFor)):
        return _target_names(statement.target)
    if isinstance(statement, (ast.With, ast.AsyncWith)):
        return {
            name
            for item in statement.items
            if item.optional_vars is not None
            for name in _target_names(item.optional_vars)
        }
    if isinstance(statement, ast.Delete):
        return {
            name for target in statement.targets for name in _target_names(target)
        }
    return set()


def _evaluated_named_expression_names(
    statement: ast.stmt, *, annotations_evaluated: bool
) -> set[str]:
    """현재 statement 실행 시 평가되는 ``:=`` 이름(lexical body 제외)."""
    names: set[str] = set()

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    visit(default)
            if annotations_evaluated:
                arguments = [
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                ]
                if node.args.vararg is not None:
                    arguments.append(node.args.vararg)
                if node.args.kwarg is not None:
                    arguments.append(node.args.kwarg)
                for argument in arguments:
                    if argument.annotation is not None:
                        visit(argument.annotation)
                if node.returns is not None:
                    visit(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            for expression in (*node.decorator_list, *node.bases):
                visit(expression)
            for keyword in node.keywords:
                visit(keyword.value)
            return
        if isinstance(node, ast.Lambda):
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    visit(default)
            return
        if isinstance(node, ast.AnnAssign):
            if annotations_evaluated:
                visit(node.annotation)
            if node.value is not None:
                visit(node.value)
            return
        if isinstance(node, ast.NamedExpr):
            names.update(_target_names(node.target))
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(statement)
    return names


def _annotations_are_evaluated(tree: ast.Module) -> bool:
    return not any(
        isinstance(statement, ast.ImportFrom)
        and statement.module == "__future__"
        and any(alias.name == "annotations" for alias in statement.names)
        for statement in tree.body
    )


def _update_imports(
    statement: ast.stmt, relative_path: Path, bindings: dict[str, str]
) -> bool:
    if isinstance(statement, ast.Import):
        for alias in statement.names:
            local = alias.asname or alias.name.split(".", 1)[0]
            bindings[local] = alias.name if alias.asname else local
        return True
    if isinstance(statement, ast.ImportFrom):
        module = _absolute_from_module(relative_path, statement)
        if module is not None:
            for alias in statement.names:
                if alias.name != "*":
                    bindings[alias.asname or alias.name] = f"{module}.{alias.name}"
        return True
    return False


def _assigned_value(
    statement: ast.stmt,
) -> tuple[list[ast.AST], ast.expr | None]:
    if isinstance(statement, ast.Assign):
        return list(statement.targets), statement.value
    if isinstance(statement, ast.AnnAssign) and statement.value is not None:
        return [statement.target], statement.value
    return [], None


def _advance_bindings(
    statement: ast.stmt,
    relative_path: Path,
    bindings: dict[str, str],
    *,
    recognize_router: bool = False,
    annotations_evaluated: bool = True,
) -> None:
    if _update_imports(statement, relative_path, bindings):
        return
    targets, value = _assigned_value(statement)
    names = {name for target in targets for name in _target_names(target)}
    derived: str | None = None
    if value is not None:
        if isinstance(value, ast.Constant):
            derived = _static_literal_binding(value.value)
        elif isinstance(value, ast.Call) and recognize_router:
            constructor = _resolve_expression(value.func, bindings)
            if constructor in {"ninja.Router", "ninja_extra.Router"}:
                derived = ROUTER_INSTANCE
        if derived is None:
            derived = _resolve_expression(value, bindings)
    for name in _evaluated_named_expression_names(
        statement, annotations_evaluated=annotations_evaluated
    ):
        bindings.pop(name, None)
    for name in names:
        bindings.pop(name, None)
    if len(names) == 1 and derived is not None:
        bindings[next(iter(names))] = derived
    if not targets:
        for name in _direct_bound_names(statement):
            bindings.pop(name, None)


def _module_symbol_bindings_before(
    parsed: ParsedSource,
) -> dict[int, dict[str, str]]:
    """Import와 앞선 local class/function 정의의 module provenance."""
    before: dict[int, dict[str, str]] = {}
    bindings: dict[str, str] = {}
    module = _module_name(parsed.relative_path)
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    for statement in parsed.tree.body:
        before[id(statement)] = dict(bindings)
        if isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            bindings[statement.name] = f"{module}.{statement.name}"
        else:
            _advance_bindings(
                statement,
                parsed.relative_path,
                bindings,
                annotations_evaluated=annotations_evaluated,
            )
    return before


def _module_name(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _final_module_symbol_bindings(parsed: ParsedSource) -> dict[str, str]:
    """Runtime-visible final module bindings for project callable proof."""
    bindings: dict[str, str] = {}
    module = _module_name(parsed.relative_path)
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    for statement in parsed.tree.body:
        if isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            bindings[statement.name] = f"{module}.{statement.name}"
        else:
            _advance_bindings(
                statement,
                parsed.relative_path,
                bindings,
                annotations_evaluated=annotations_evaluated,
            )
    return bindings


def _simple_binding_target(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Starred):
        return _simple_binding_target(node.value)
    if isinstance(node, (ast.Tuple, ast.List)):
        return all(_simple_binding_target(item) for item in node.elts)
    return False


STATIC_PROOF_IMPORT_ROOTS = frozenset(
    {"__future__", "builtins", "pydantic", "typing"}
)


def _annotation_is_inert(node: ast.AST | None) -> bool:
    return node is None or isinstance(node, (ast.Name, ast.Constant))


def _function_signature_is_inert(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    if node.decorator_list or getattr(node, "type_params", ()):
        return False
    defaults = (*node.args.defaults, *node.args.kw_defaults)
    if any(default is not None and not _module_value_is_inert(default) for default in defaults):
        return False
    arguments = (
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs,
    )
    if any(not _annotation_is_inert(argument.annotation) for argument in arguments):
        return False
    if node.args.vararg is not None and not _annotation_is_inert(
        node.args.vararg.annotation
    ):
        return False
    if node.args.kwarg is not None and not _annotation_is_inert(
        node.args.kwarg.annotation
    ):
        return False
    return _annotation_is_inert(node.returns)


def _lambda_signature_is_inert(node: ast.Lambda) -> bool:
    defaults = (*node.args.defaults, *node.args.kw_defaults)
    return all(
        default is None or _module_value_is_inert(default)
        for default in defaults
    )


def _module_value_is_inert(node: ast.AST) -> bool:
    if any(isinstance(candidate, ast.Call) for candidate in ast.walk(node)):
        return False
    try:
        ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError):
        pass
    else:
        return True
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Lambda):
        return _lambda_signature_is_inert(node)
    if isinstance(node, (ast.Tuple, ast.List)):
        return all(
            not isinstance(item, ast.Starred) and _module_value_is_inert(item)
            for item in node.elts
        )
    return False


def _trusted_static_import(statement: ast.Import | ast.ImportFrom) -> bool:
    if isinstance(statement, ast.Import):
        modules = [alias.name for alias in statement.names]
    else:
        if (
            statement.level
            or statement.module is None
            or any(alias.name == "*" for alias in statement.names)
        ):
            return False
        modules = [statement.module]
    return all(module.split(".", 1)[0] in STATIC_PROOF_IMPORT_ROOTS for module in modules)


def _module_statement_is_static(statement: ast.stmt) -> bool:
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return _trusted_static_import(statement)
    if isinstance(statement, ast.FunctionDef):
        return _function_signature_is_inert(statement)
    if isinstance(statement, ast.Assign):
        return all(_simple_binding_target(target) for target in statement.targets) and (
            _module_value_is_inert(statement.value)
        )
    if isinstance(statement, ast.AnnAssign):
        return (
            _simple_binding_target(statement.target)
            and _annotation_is_inert(statement.annotation)
            and (
                statement.value is None
                or _module_value_is_inert(statement.value)
            )
        )
    if isinstance(statement, ast.Expr):
        return isinstance(statement.value, ast.Constant) and isinstance(
            statement.value.value, str
        )
    return isinstance(statement, ast.Pass)


def _module_namespace_is_static(parsed: ParsedSource) -> bool:
    return all(_module_statement_is_static(statement) for statement in parsed.tree.body)


def _status_from_expression(
    expression: ast.AST,
    bindings: dict[str, str],
) -> int | None:
    literal = _literal_status(expression)
    if (
        literal is not None
        and isinstance(expression, ast.Constant)
        and isinstance(expression.value, int)
        and not isinstance(expression.value, bool)
    ):
        return literal
    resolved = _resolve_expression(expression, bindings)
    if resolved is None:
        return None
    static_value = _static_literal_value(resolved)
    if (
        isinstance(static_value, int)
        and not isinstance(static_value, bool)
    ):
        return static_value
    if resolved.startswith("ninja.status.") or resolved.startswith("ninja_extra.status."):
        name = resolved.rsplit(".", 1)[-1]
        match = HTTP_STATUS_CONSTANT_RE.match(name)
        return int(match.group(1)) if match is not None else None
    if resolved.startswith("http.HTTPStatus."):
        name = resolved.rsplit(".", 1)[-1]
        member = HTTPStatus.__members__.get(name)
        return int(member) if member is not None else None
    return None


def _field_call_default_expression(
    expression: ast.Call,
    bindings: dict[str, str],
) -> tuple[bool, ast.AST | None]:
    if _resolve_expression(expression.func, bindings) not in FIELD_FACTORIES:
        return False, None
    for keyword in expression.keywords:
        if keyword.arg == "default":
            if isinstance(keyword.value, ast.Constant) and keyword.value.value is Ellipsis:
                return True, None
            return True, keyword.value
        if keyword.arg == "default_factory":
            return True, None
    if expression.args:
        first = expression.args[0]
        if isinstance(first, ast.Constant) and first.value is Ellipsis:
            return True, None
        return True, first
    return False, None


def _is_required_sentinel(node: ast.AST, bindings: dict[str, str]) -> bool:
    if isinstance(node, ast.Constant) and node.value is Ellipsis:
        return True
    return _resolve_expression(node, bindings) in {
        "pydantic_core.PydanticUndefined",
        "pydantic_core._pydantic_core.PydanticUndefined",
        "pydantic.fields.PydanticUndefined",
    }


def _field_call_default_spec(
    expression: ast.Call,
    bindings: dict[str, str],
) -> tuple[str, ast.AST | None] | None:
    if _resolve_expression(expression.func, bindings) not in FIELD_FACTORIES:
        return None
    default_value = expression.args[0] if expression.args else None
    default_declared = bool(expression.args)
    factory_value: ast.AST | None = None
    factory_declared = False
    for keyword in expression.keywords:
        if keyword.arg == "default":
            default_declared = True
            default_value = keyword.value
        elif keyword.arg == "default_factory":
            factory_declared = True
            factory_value = keyword.value
    default_is_set = (
        default_declared
        and default_value is not None
        and not _is_required_sentinel(default_value, bindings)
    )
    factory_is_set = factory_declared and factory_value is not None and not (
        isinstance(factory_value, ast.Constant) and factory_value.value is None
    ) and not _is_required_sentinel(factory_value, bindings)
    if default_is_set and factory_is_set:
        return "conflict", None
    if (
        factory_declared
        and isinstance(factory_value, ast.Constant)
        and factory_value.value is Ellipsis
    ):
        return "invalid_factory", None
    if factory_is_set:
        return "default_factory", None
    if default_is_set:
        return "default", default_value
    if factory_declared and isinstance(factory_value, ast.Constant) and factory_value.value is None:
        return "clear_factory", None
    return None


def _merge_field_default_spec(
    current: tuple[str, ast.AST | None],
    declared: tuple[str, ast.AST | None] | None,
) -> tuple[str, ast.AST | None]:
    if declared is None:
        return current
    if current[0] in {"conflict", "invalid_factory"}:
        return current
    if declared[0] in {"conflict", "invalid_factory"}:
        return declared
    if declared[0] == "clear_factory":
        return current if current[0] == "default" else ("required", None)
    if {current[0], declared[0]} == {"default", "default_factory"}:
        return "conflict", None
    return declared


def _annotated_parts(
    node: ast.AST,
    bindings: dict[str, str],
) -> tuple[ast.AST, tuple[ast.AST, ...]] | None:
    if not isinstance(node, ast.Subscript):
        return None
    wrapper = _resolve_expression(node.value, bindings) or _expression_dotted_name(node.value)
    if wrapper not in {"Annotated", "typing.Annotated", "typing_extensions.Annotated"}:
        return None
    parts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    if not parts:
        return None
    return parts[0], tuple(parts[1:])


def _ordered_annotation_field_calls(
    node: ast.AST,
    bindings: dict[str, str],
) -> tuple[ast.Call, ...]:
    parts = _annotated_parts(node, bindings)
    if parts is None:
        return ()
    inner, metadata = parts
    calls = list(_ordered_annotation_field_calls(inner, bindings))
    calls.extend(
        candidate
        for candidate in metadata
        if isinstance(candidate, ast.Call)
        and _resolve_expression(candidate.func, bindings) in FIELD_FACTORIES
    )
    return tuple(calls)


def _field_default_expression(
    expression: ast.AST | None,
    bindings: dict[str, str],
) -> ast.AST | None:
    if not isinstance(expression, ast.Call):
        return expression
    declared, default = _field_call_default_expression(expression, bindings)
    if declared:
        return default
    if _resolve_expression(expression.func, bindings) in FIELD_FACTORIES:
        return None
    return expression


def _annassign_default_expression(
    statement: ast.AnnAssign,
    bindings: dict[str, str],
) -> ast.AST | None:
    spec: tuple[str, ast.AST | None] = ("required", None)
    for candidate in _ordered_annotation_field_calls(statement.annotation, bindings):
        spec = _merge_field_default_spec(
            spec,
            _field_call_default_spec(candidate, bindings),
        )

    value = statement.value
    if value is None:
        return spec[1]
    if not isinstance(value, ast.Call):
        if _is_required_sentinel(value, bindings):
            return spec[1]
        return None if spec[0] == "default_factory" else value
    if _resolve_expression(value.func, bindings) in FIELD_FACTORIES:
        return _merge_field_default_spec(
            spec,
            _field_call_default_spec(value, bindings),
        )[1]
    return value


def _class_field_specs(
    class_node: ast.ClassDef,
    bindings: dict[str, str],
    relative_path: Path,
    *,
    annotations_evaluated: bool,
) -> dict[str, StatusSpec]:
    fields: dict[str, StatusSpec] = {}
    current_bindings = dict(bindings)
    for statement in class_node.body:
        if isinstance(statement, ast.AnnAssign):
            if isinstance(statement.target, ast.Name) and not statement.target.id.startswith("_"):
                fields[statement.target.id] = StatusSpec(
                    _annassign_default_expression(statement, current_bindings),
                    dict(current_bindings),
                    relative_path,
                )
        elif isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    fields[target.id] = StatusSpec(
                        _field_default_expression(statement.value, current_bindings),
                        dict(current_bindings),
                        relative_path,
                    )
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorator_origins = {
                _resolve_expression(
                    decorator.func if isinstance(decorator, ast.Call) else decorator,
                    current_bindings,
                )
                or _expression_dotted_name(
                    decorator.func if isinstance(decorator, ast.Call) else decorator
                )
                for decorator in statement.decorator_list
            }
            if "pydantic.computed_field" in decorator_origins:
                body = [
                    item
                    for item in statement.body
                    if not (
                        isinstance(item, ast.Expr)
                        and isinstance(item.value, ast.Constant)
                        and isinstance(item.value.value, str)
                    )
                ]
                value = body[0].value if len(body) == 1 and isinstance(body[0], ast.Return) else None
                fields[statement.name] = StatusSpec(
                    value,
                    dict(current_bindings),
                    relative_path,
                )
        _advance_bindings(
            statement,
            relative_path,
            current_bindings,
            annotations_evaluated=annotations_evaluated,
        )
    return fields


def _static_string(
    node: ast.AST,
    bindings: dict[str, str],
) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    value = _static_literal_value(_resolve_expression(node, bindings))
    return value if isinstance(value, str) else None


def _alias_values(
    node: ast.AST,
    bindings: dict[str, str],
) -> set[str]:
    direct = _static_string(node, bindings)
    if direct is not None:
        return {direct}
    if not isinstance(node, ast.Call):
        return set()
    factory = _resolve_expression(node.func, bindings)
    if factory not in ALIAS_CHOICES_FACTORIES:
        return set()
    values = {_static_string(argument, bindings) for argument in node.args}
    return {value for value in values if value is not None}


def _generated_alias(field_name: str, generator: str | None) -> str | None:
    if generator == "pydantic.alias_generators.to_pascal":
        camel = field_name.title()
        return re.sub(r"([0-9A-Za-z])_(?=[0-9A-Z])", lambda match: match.group(1), camel)
    if generator == "pydantic.alias_generators.to_camel":
        if re.match(r"^[a-z]+[A-Za-z0-9]*$", field_name) and not re.search(
            r"\d[a-z]", field_name
        ):
            return field_name
        pascal = _generated_alias(field_name, "pydantic.alias_generators.to_pascal")
        assert pascal is not None
        return re.sub(r"(^_*[A-Z])", lambda match: match.group(1).lower(), pascal)
    if generator == "pydantic.alias_generators.to_snake":
        snake = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", field_name)
        snake = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake)
        snake = re.sub(r"([0-9])([A-Z])", r"\1_\2", snake)
        snake = re.sub(r"([a-z])([0-9])", r"\1_\2", snake)
        return snake.replace("-", "_").lower()
    return None


def _static_alias_expression(
    node: ast.AST,
    parameter: str,
    field_name: str,
) -> str | None:
    if isinstance(node, ast.Name) and node.id == parameter:
        return field_name
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        pieces: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                pieces.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                rendered = _static_alias_expression(value.value, parameter, field_name)
                if (
                    rendered is None
                    or value.format_spec is not None
                    or value.conversion not in {-1, ord("s")}
                ):
                    return None
                pieces.append(rendered)
            else:
                return None
        return "".join(pieces)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_alias_expression(node.left, parameter, field_name)
        right = _static_alias_expression(node.right, parameter, field_name)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.IfExp):
        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            branch = node.body if node.test.value else node.orelse
            return _static_alias_expression(branch, parameter, field_name)
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        owner = _static_alias_expression(node.func.value, parameter, field_name)
        if owner is None or node.keywords:
            return None
        arguments = [
            _static_alias_expression(argument, parameter, field_name)
            for argument in node.args
        ]
        if any(argument is None for argument in arguments):
            return None
        values = [argument for argument in arguments if argument is not None]
        if node.func.attr == "lower" and not values:
            return owner.lower()
        if node.func.attr == "upper" and not values:
            return owner.upper()
        if node.func.attr == "title" and not values:
            return owner.title()
        if node.func.attr == "replace" and len(values) == 2:
            return owner.replace(values[0], values[1])
    return None


def _project_alias(
    generator: str | None,
    field_name: str,
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
) -> str | None:
    if generator is None or "." not in generator:
        return None
    module, function_name = generator.rsplit(".", 1)
    candidates = (
        Path(*module.split(".")).with_suffix(".py"),
        Path(*module.split(".")) / "__init__.py",
    )
    source = next((parsed_sources.get(path) for path in candidates if path in parsed_sources), None)
    if source is None:
        for path in candidates:
            try:
                resolved = (root / path).resolve()
                resolved.relative_to(root)
                text = resolved.read_text(encoding="utf-8")
                source = ParsedSource(path, text, ast.parse(text, filename=path.as_posix()))
                break
            except (FileNotFoundError, OSError, UnicodeError, SyntaxError, ValueError):
                continue
    if source is None:
        return None
    if not _module_namespace_is_static(source):
        return None
    functions = [
        node
        for node in source.tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    if len(functions) != 1:
        return None
    function = functions[0]
    if (
        function.decorator_list
        or function.args.posonlyargs
        or len(function.args.args) != 1
        or function.args.vararg is not None
        or function.args.kwarg is not None
        or function.args.kwonlyargs
    ):
        return None
    body = [
        statement
        for statement in function.body
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
    ]
    if len(body) != 1 or not isinstance(body[0], ast.Return) or body[0].value is None:
        return None
    final_bindings = _final_module_symbol_bindings(source)
    if final_bindings.get(function_name) != (
        f"{_module_name(source.relative_path)}.{function_name}"
    ):
        return None
    return _static_alias_expression(
        body[0].value,
        function.args.args[0].arg,
        field_name,
    )


def _project_config_alias_generator(
    value: ast.AST,
    bindings: dict[str, str],
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
) -> tuple[bool, str | None]:
    if not isinstance(value, ast.Call) or value.args or value.keywords:
        return False, None
    resolved = _resolve_expression(value.func, bindings)
    if resolved is None or "." not in resolved:
        return False, None
    module, function_name = resolved.rsplit(".", 1)
    candidates = (
        Path(*module.split(".")).with_suffix(".py"),
        Path(*module.split(".")) / "__init__.py",
    )
    source = next((parsed_sources.get(path) for path in candidates if path in parsed_sources), None)
    if source is None:
        for path in candidates:
            try:
                candidate = (root / path).resolve()
                candidate.relative_to(root)
                text = candidate.read_text(encoding="utf-8")
                source = ParsedSource(path, text, ast.parse(text, filename=path.as_posix()))
                break
            except (FileNotFoundError, OSError, UnicodeError, SyntaxError, ValueError):
                continue
    if source is None:
        return False, None
    if not _module_namespace_is_static(source):
        return False, None
    functions = [
        node
        for node in source.tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    if len(functions) != 1:
        return False, None
    function = functions[0]
    if (
        function.decorator_list
        or function.args.posonlyargs
        or function.args.args
        or function.args.vararg is not None
        or function.args.kwarg is not None
        or function.args.kwonlyargs
    ):
        return False, None
    body = [
        statement
        for statement in function.body
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
    ]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return False, None
    returned = body[0].value
    if not isinstance(returned, ast.Call):
        return False, None
    function_bindings = _final_module_symbol_bindings(source)
    if function_bindings.get(function_name) != (
        f"{_module_name(source.relative_path)}.{function_name}"
    ):
        return False, None
    if _resolve_expression(returned.func, function_bindings) not in {
        "dict",
        "pydantic.ConfigDict",
        "pydantic.config.ConfigDict",
    } or returned.args or any(keyword.arg is None for keyword in returned.keywords):
        return False, None
    for keyword in returned.keywords:
        if keyword.arg == "alias_generator":
            if isinstance(keyword.value, ast.Constant) and keyword.value.value is None:
                return True, None
            generator = _resolve_expression(keyword.value, function_bindings)
            return (True, generator) if generator is not None else (False, None)
    return True, None


def _class_alias_generator(
    class_node: ast.ClassDef,
    bindings: dict[str, str],
    relative_path: Path,
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
    *,
    annotations_evaluated: bool,
) -> tuple[str | None, bool]:
    current = dict(bindings)
    body_generator: str | None = None
    body_config_seen = False
    body_config_complete = True
    nested_config_generator: str | None = None
    nested_config_seen = False
    for statement in class_node.body:
        targets, value = _assigned_value(statement)
        names = {name for target in targets for name in _target_names(target)}
        if "model_config" in names:
            body_config_seen = True
            body_generator = None
            body_config_complete = True
            if isinstance(value, ast.Call):
                direct_factory = _resolve_expression(value.func, current)
                if direct_factory not in {
                    "dict",
                    "pydantic.ConfigDict",
                    "pydantic.config.ConfigDict",
                }:
                    found, project_generator = _project_config_alias_generator(
                        value,
                        current,
                        parsed_sources,
                        root,
                    )
                    body_config_complete = found
                    body_generator = project_generator
                else:
                    if value.args or any(keyword.arg is None for keyword in value.keywords):
                        body_config_complete = False
                    for keyword in value.keywords:
                        if keyword.arg == "alias_generator":
                            body_generator = _resolve_expression(keyword.value, current)
            elif isinstance(value, ast.Dict):
                for key, item in zip(value.keys, value.values):
                    if key is None:
                        body_config_complete = False
                    elif _static_string(key, current) == "alias_generator":
                        body_generator = _resolve_expression(item, current)
                    elif _static_string(key, current) is None:
                        body_config_complete = False
            else:
                body_config_complete = False
        if isinstance(statement, ast.ClassDef) and statement.name == "Config":
            nested_config_seen = True
            nested_config_generator = None
            config_current = dict(current)
            for config_statement in statement.body:
                config_targets, config_value = _assigned_value(config_statement)
                config_names = {
                    name
                    for target in config_targets
                    for name in _target_names(target)
                }
                if "alias_generator" in config_names and config_value is not None:
                    nested_config_generator = _resolve_expression(config_value, config_current)
                _advance_bindings(
                    config_statement,
                    relative_path,
                    config_current,
                    annotations_evaluated=annotations_evaluated,
                )
        _advance_bindings(
            statement,
            relative_path,
            current,
            annotations_evaluated=annotations_evaluated,
        )
    generator = body_generator if body_config_seen else nested_config_generator
    config_complete = (
        body_config_complete if body_config_seen else True
    ) and not (body_config_seen and nested_config_seen)

    # Pydantic class-header kwargs override body model_config values.
    for keyword in class_node.keywords:
        if keyword.arg == "alias_generator":
            generator = (
                None
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is None
                else _resolve_expression(keyword.value, bindings)
            )
            config_complete = True
    return generator, config_complete


def _class_constructor_fields_by_key(
    class_node: ast.ClassDef,
    bindings: dict[str, str],
    relative_path: Path,
    parsed_sources: dict[Path, ParsedSource],
    project_root: Path,
    *,
    annotations_evaluated: bool,
) -> tuple[dict[str, str], bool]:
    mapping: dict[str, str] = {}
    current = dict(bindings)
    generator, keys_complete = _class_alias_generator(
        class_node,
        bindings,
        relative_path,
        parsed_sources,
        project_root,
        annotations_evaluated=annotations_evaluated,
    )
    for statement in class_node.body:
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            field_name = statement.target.id
            if not field_name.startswith("_") and field_name != "model_config":
                keys = {field_name}
                roots = [statement.annotation]
                if statement.value is not None:
                    roots.append(statement.value)
                for root in roots:
                    for candidate in ast.walk(root):
                        if not isinstance(candidate, ast.Call):
                            continue
                        if _resolve_expression(candidate.func, current) not in FIELD_FACTORIES:
                            continue
                        for keyword in candidate.keywords:
                            if keyword.arg in {"alias", "validation_alias"}:
                                keys.update(_alias_values(keyword.value, current))
                generated = _generated_alias(field_name, generator) or _project_alias(
                    generator,
                    field_name,
                    parsed_sources,
                    project_root,
                )
                if generated is not None:
                    keys.add(generated)
                elif generator is not None:
                    keys_complete = False
                for key in keys:
                    previous = mapping.get(key)
                    if previous is not None and previous != field_name:
                        raise UsageError(
                            f"constructor alias collision 분석 불능: {relative_path}:{statement.lineno} {key}"
                        )
                    mapping[key] = field_name
        _advance_bindings(
            statement,
            relative_path,
            current,
            annotations_evaluated=annotations_evaluated,
        )
    return mapping, keys_complete


def _error_catalog(
    config: Config, parsed_by_path: dict[Path, ParsedSource]
) -> dict[str, ErrorSymbol]:
    common = parsed_by_path[COMMON_ERROR_PATH]
    common_class = next(
        (
            node
            for node in common.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FrameworkErrorSchema"
        ),
        None,
    )
    if common_class is None:
        raise UsageError("canonical common FrameworkErrorSchema provenance 분석 불능")
    common_relative = COMMON_ERROR_PATH
    common_before = _module_symbol_bindings_before(common)
    common_annotations_evaluated = _annotations_are_evaluated(common.tree)
    common_fields = _class_field_specs(
        common_class,
        common_before[id(common_class)],
        common_relative,
        annotations_evaluated=common_annotations_evaluated,
    )
    (
        common_constructor_fields,
        common_constructor_keys_complete,
    ) = _class_constructor_fields_by_key(
        common_class,
        common_before[id(common_class)],
        common_relative,
        parsed_by_path,
        config.root,
        annotations_evaluated=common_annotations_evaluated,
    )
    catalog: dict[str, ErrorSymbol] = {
        COMMON_ERROR_OUT: ErrorSymbol(
            COMMON_ERROR_OUT,
            None,
            "common",
            common_fields,
            common_constructor_fields,
            common_constructor_keys_complete,
        )
    }
    if not config.error_bcs:
        return catalog

    for bc in config.error_bcs:
        relative = Path(f"application/{bc}/driving_layer/api/bc_error_schema.py")
        parsed = parsed_by_path[relative]
        before = _module_symbol_bindings_before(parsed)
        annotations_evaluated = _annotations_are_evaluated(parsed.tree)
        module = ".".join(relative.with_suffix("").parts)
        base_nodes: list[ast.ClassDef] = []
        for node in parsed.tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bindings = before[id(node)]
            bases = {_resolve_expression(base, bindings) for base in node.bases}
            if COMMON_ERROR_OUT in bases:
                base_nodes.append(node)
        if len(base_nodes) != 1:
            raise UsageError(
                f"canonical BC FrameworkErrorSchema provenance 분석 불능: {relative}"
            )
        base_node = base_nodes[0]
        base_path = f"{module}.{base_node.name}"
        base_fields = {
            **common_fields,
            **_class_field_specs(
                base_node,
                before[id(base_node)],
                relative,
                annotations_evaluated=annotations_evaluated,
            ),
        }
        (
            own_base_constructor_fields,
            own_base_constructor_keys_complete,
        ) = _class_constructor_fields_by_key(
                base_node,
                before[id(base_node)],
                relative,
                parsed_by_path,
                config.root,
                annotations_evaluated=annotations_evaluated,
            )
        base_constructor_fields = {
            **common_constructor_fields,
            **own_base_constructor_fields,
        }
        catalog[base_path] = ErrorSymbol(
            base_path,
            bc,
            "base",
            base_fields,
            base_constructor_fields,
            common_constructor_keys_complete
            and own_base_constructor_keys_complete,
        )
        for node in parsed.tree.body:
            if not isinstance(node, ast.ClassDef) or node is base_node:
                continue
            bindings = before[id(node)]
            bases = {_resolve_expression(base, bindings) for base in node.bases}
            if base_path not in bases:
                continue
            full_path = f"{module}.{node.name}"
            concrete_fields = {
                **base_fields,
                **_class_field_specs(
                    node,
                    bindings,
                    relative,
                    annotations_evaluated=annotations_evaluated,
                ),
            }
            (
                own_concrete_constructor_fields,
                own_concrete_constructor_keys_complete,
            ) = _class_constructor_fields_by_key(
                    node,
                    bindings,
                    relative,
                    parsed_by_path,
                    config.root,
                    annotations_evaluated=annotations_evaluated,
                )
            concrete_constructor_fields = {
                **base_constructor_fields,
                **own_concrete_constructor_fields,
            }
            catalog[full_path] = ErrorSymbol(
                full_path,
                bc,
                "concrete",
                concrete_fields,
                concrete_constructor_fields,
                common_constructor_keys_complete
                and own_base_constructor_keys_complete
                and own_concrete_constructor_keys_complete,
            )
    return catalog


def _operation_decorator(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, str],
) -> ast.Call | None:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        resolved = _resolve_expression(decorator.func, bindings)
        if resolved is None:
            continue
        owner, separator, method = resolved.rpartition(".")
        if separator and method in HTTP_METHODS and _is_ambiguous_resolution(owner):
            raise UsageError(
                f"operation decorator receiver provenance 분석 불능: line {decorator.lineno}"
            )
        if separator and method in HTTP_METHODS and owner in {
            ROUTER_INSTANCE,
            "ninja_extra.route",
        }:
            return decorator
    return None


_TYPE_ALIAS_ANNOTATIONS: "frozenset[str]" = frozenset({"typing.TypeAlias", "typing_extensions.TypeAlias"})


def _bound_name_count(tree: ast.Module, name: str) -> int:
    """모듈 어디서든(함수 · 클래스 몸통 · 조건 · 반복 · 컴프리헨션 포함) `name` 을 묶는 자리 수 — `import *` 가 있으면 2."""
    count: int = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            count += int(node.id == name and isinstance(node.ctx, (ast.Store, ast.Del)))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            count += int(node.name == name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    return 2
                count += int((alias.asname or alias.name.split(".", 1)[0]) == name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            count += int(name in node.names)
        elif isinstance(node, ast.ExceptHandler):
            count += int(node.name == name)
        elif isinstance(node, ast.arg):
            count += int(node.arg == name)
        else:
            for attr in ("name", "rest"):  # match 패턴 · PEP 695 형 매개변수
                value = getattr(node, attr, None)
                if isinstance(value, str) and not isinstance(node, ast.alias):
                    count += int(value == name)
    return count


def _module_type_aliases(
    tree: ast.Module, before: "dict[int, dict[str, str]]"
) -> "dict[str, tuple[ast.expr, dict[str, str]]]":
    """F4-96 — 모듈 최상위 별칭 문장(`type X = 식`(형 매개변수 없음) · `X = 식` · `X: TypeAlias = 식`) 가운데
    그 이름을 묶는 자리가 모듈 전체에서 그 문장 하나뿐인 것 → (식, 그 문장 앞 바인딩)."""
    type_alias = getattr(ast, "TypeAlias", None)
    found: "dict[str, tuple[ast.expr, dict[str, str]]]" = {}
    for statement in tree.body:
        bindings: "dict[str, str]" = before.get(id(statement), {})
        name: "str | None" = None
        value: "ast.expr | None" = None
        if type_alias is not None and isinstance(statement, type_alias) and not getattr(statement, "type_params", None):
            name, value = statement.name.id, statement.value
        elif isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            name, value = statement.targets[0].id, statement.value
        elif (isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
              and statement.value is not None
              and _resolve_expression(statement.annotation, bindings) in _TYPE_ALIAS_ANNOTATIONS):
            name, value = statement.target.id, statement.value
        if name is not None and value is not None and _bound_name_count(tree, name) == 1:
            found[name] = (value, dict(bindings))
    return found


def _collect_operations(parsed: ParsedSource) -> list[Operation]:
    operations: list[Operation] = []
    module_aliases = _module_type_aliases(parsed.tree, _module_symbol_bindings_before(parsed))
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    final_module_bindings = _bindings_after_block(
        parsed.tree.body,
        {},
        parsed.relative_path,
        recognize_router=True,
        annotations_evaluated=annotations_evaluated,
    )

    def visit_block(
        statements: list[ast.stmt],
        incoming: dict[str, str],
        owners: tuple[str, ...],
    ) -> dict[str, str]:
        def advance(statement: ast.stmt, state: ProvenanceState) -> None:
            _advance_bindings(
                statement,
                parsed.relative_path,
                state.bindings,
                recognize_router=True,
                annotations_evaluated=annotations_evaluated,
            )

        def visit_function(statement: ast.stmt, state: ProvenanceState) -> None:
            decorator = _operation_decorator(statement, state.bindings)
            if decorator is not None:
                operations.append(
                    Operation(
                        parsed.relative_path,
                        owners,
                        statement,
                        decorator,
                        dict(state.bindings),
                        dict(final_module_bindings),
                        annotations_evaluated,
                        module_aliases,
                    )
                )
            _drop_provenance_names(
                state,
                _evaluated_named_expression_names(
                    statement,
                    annotations_evaluated=annotations_evaluated,
                )
                | {statement.name},
            )

        def visit_class(statement: ast.ClassDef, state: ProvenanceState) -> None:
            class_state = _copy_provenance(state)
            evaluated = _evaluated_named_expression_names(
                statement,
                annotations_evaluated=annotations_evaluated,
            )
            _drop_provenance_names(state, evaluated | {statement.name})
            _drop_provenance_names(class_state, evaluated)
            visit_block(
                statement.body,
                class_state.bindings,
                (*owners, statement.name),
            )

        return _statement_provenance_flow(
            statements,
            ProvenanceState(dict(incoming), {}),
            annotations_evaluated=annotations_evaluated,
            on_simple=advance,
            on_function=visit_function,
            on_class=visit_class,
        ).bindings

    visit_block(parsed.tree.body, {}, ())
    return operations


def _resolved_error_status(instance: ErrorInstance) -> int:
    if instance.direct_status is not None:
        return instance.direct_status
    raise UsageError(
        f"returned error status provenance 분석 불능: {instance.symbol.full_path}"
    )


def _constructed_error(
    value: ast.expr,
    bindings: dict[str, str],
    catalog: dict[str, ErrorSymbol],
    relative_path: Path,
) -> ErrorInstance | None:
    if not isinstance(value, ast.Call):
        return None
    resolved = _resolve_expression(value.func, bindings)
    if _is_ambiguous_resolution(resolved):
        raise UsageError(
            f"returned FrameworkErrorSchema provenance 분석 불능: line {value.lineno}"
        )
    symbol = catalog.get(resolved or "")
    if symbol is None or symbol.kind not in {"base", "concrete"}:
        return None
    if symbol.kind == "concrete":
        return ErrorInstance(symbol)
    constructor_fields = symbol.constructor_fields_by_key or {}
    if not symbol.constructor_keys_complete and any(
        keyword.arg is not None and keyword.arg not in constructor_fields
        for keyword in value.keywords
    ):
        raise UsageError(
            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
            f"custom alias_generator constructor-key 분석 불능: line {value.lineno}"
        )
    field_values = tuple(
        (
            (
                constructor_fields.get(keyword.arg, keyword.arg)
                if symbol.constructor_fields_by_key is not None
                else keyword.arg
            ),
            StatusSpec(keyword.value, dict(bindings), relative_path),
        )
        for keyword in value.keywords
        if keyword.arg is not None
    )
    return ErrorInstance(symbol, field_values=field_values)


def _status_return_instance(
    statement: ast.Return,
    bindings: dict[str, str],
    instances: dict[str, ErrorInstance | str],
) -> ErrorInstance | None:
    value = statement.value
    if not isinstance(value, ast.Call):
        return None
    resolved = _resolve_expression(value.func, bindings)
    if _is_ambiguous_resolution(resolved):
        raise UsageError(
            f"returned Status provenance 분석 불능: line {statement.lineno}"
        )
    if resolved != "ninja.Status":
        return None
    if len(value.args) < 2:
        return None
    status_arg, body_arg = value.args[:2]
    if not isinstance(body_arg, ast.Name):
        return None
    instance = instances.get(body_arg.id)
    if instance == AMBIGUOUS_ERROR_INSTANCE:
        raise UsageError(
            f"returned FrameworkErrorSchema instance provenance 분석 불능: line {statement.lineno}"
        )
    if not isinstance(instance, ErrorInstance):
        return None
    status = _status_from_expression(status_arg, bindings)
    if status is None and (
        isinstance(status_arg, ast.Attribute)
        and isinstance(status_arg.value, ast.Name)
        and status_arg.value.id == body_arg.id
    ):
        field_name = status_arg.attr
        spec = dict(instance.field_values).get(field_name)
        if spec is None and instance.symbol.field_defaults is not None:
            spec = instance.symbol.field_defaults.get(field_name)
        if spec is not None and spec.expression is not None:
            status = _status_from_expression(spec.expression, spec.bindings)
    if status is None:
        raise UsageError(
            f"returned error HTTP status provenance 분석 불능: line {statement.lineno}"
        )
    return ErrorInstance(
        instance.symbol,
        direct_status=status,
        alias_depth=instance.alias_depth,
        field_values=instance.field_values,
    )


def _operation_requirements(
    operation: Operation,
    catalog: dict[str, ErrorSymbol],
) -> dict[int, set[str]]:
    requirements: dict[int, set[str]] = {}
    annotations_evaluated = operation.annotations_evaluated
    initial_bindings = dict(operation.body_bindings)
    argument_names = {
        argument.arg
        for argument in (
            *operation.function.args.posonlyargs,
            *operation.function.args.args,
            *operation.function.args.kwonlyargs,
        )
    }
    if operation.function.args.vararg is not None:
        argument_names.add(operation.function.args.vararg.arg)
    if operation.function.args.kwarg is not None:
        argument_names.add(operation.function.args.kwarg.arg)
    for name in argument_names:
        initial_bindings.pop(name, None)

    def advance(statement: ast.stmt, state: ProvenanceState) -> None:
        if isinstance(statement, ast.Return):
            instance = _status_return_instance(
                statement, state.bindings, state.instances
            )
            if instance is not None and instance.symbol.bc is not None:
                status = _resolved_error_status(instance)
                requirements.setdefault(status, set()).add(instance.symbol.full_path)
            return
        targets, value = _assigned_value(statement)
        names = {name for target in targets for name in _target_names(target)}
        instance: ErrorInstance | str | None = None
        if value is not None:
            instance = _constructed_error(
                value,
                state.bindings,
                catalog,
                operation.relative_path,
            )
            if instance is None and isinstance(value, ast.Name):
                previous = state.instances.get(value.id)
                if isinstance(previous, ErrorInstance) and previous.alias_depth == 0:
                    instance = ErrorInstance(
                        previous.symbol,
                        previous.direct_status,
                        alias_depth=1,
                        field_values=previous.field_values,
                    )
                elif previous == AMBIGUOUS_ERROR_INSTANCE:
                    instance = previous
        _advance_bindings(
            statement,
            operation.relative_path,
            state.bindings,
            annotations_evaluated=annotations_evaluated,
        )
        invalidated = (
            names
            | _direct_bound_names(statement)
            | _evaluated_named_expression_names(
                statement,
                annotations_evaluated=annotations_evaluated,
            )
        )
        for name in invalidated:
            state.instances.pop(name, None)
        if len(names) == 1 and instance is not None:
            state.instances[next(iter(names))] = instance

    _statement_provenance_flow(
        operation.function.body,
        ProvenanceState(initial_bindings, {}),
        annotations_evaluated=annotations_evaluated,
        on_simple=advance,
    )
    return requirements


def _keyword(call: ast.Call, name: str) -> ast.expr | None:
    values = [keyword.value for keyword in call.keywords if keyword.arg == name]
    if len(values) > 1:
        raise UsageError(f"operation decorator keyword 중복: {name}")
    return values[0] if values else None


def _schema_symbol(
    expression: ast.expr,
    bindings: dict[str, str],
    catalog: dict[str, ErrorSymbol],
) -> ErrorSymbol | str | None:
    if isinstance(expression, ast.Name) and expression.id == "dict":
        return "builtins.dict"
    resolved = _resolve_expression(expression, bindings)
    if resolved == COMMON_ERROR_OUT:
        return catalog.get(COMMON_ERROR_OUT)
    if resolved in catalog:
        return catalog[resolved]
    return None


def _declared_schema_symbols(
    expression: ast.expr,
    bindings: dict[str, str],
    catalog: dict[str, ErrorSymbol],
    operation: "Operation | None" = None,
    depth: int = 0,
) -> list[ErrorSymbol | str] | None:
    """`response=` 값 하나가 선언하는 schema 집합 — `Union[A, B]`·`A | B` 는 원소로 편다. 해석 불능이면 None.

    `operation` 을 주면 모듈 별칭 이름(`Operation.type_aliases`)도 편다 — 별칭 식을 «별칭 문장 앞» · «오퍼레이션
    자리» · «모듈 끝» 세 바인딩으로 풀어 셋이 같을 때만(평가 시점에 흔들리지 않을 때만) 쓰고, 3단까지만."""
    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.BitOr):
        left = _declared_schema_symbols(expression.left, bindings, catalog, operation, depth)
        right = _declared_schema_symbols(expression.right, bindings, catalog, operation, depth)
        return None if left is None or right is None else [*left, *right]
    if isinstance(expression, ast.Subscript) and _resolve_expression(
        expression.value, bindings
    ) == "typing.Union":
        members = (
            expression.slice.elts if isinstance(expression.slice, ast.Tuple) else [expression.slice]
        )
        symbols: list[ErrorSymbol | str] = []
        for member in members:
            resolved = _declared_schema_symbols(member, bindings, catalog, operation, depth)
            if resolved is None:
                return None
            symbols.extend(resolved)
        return symbols
    symbol = _schema_symbol(expression, bindings, catalog)
    if (symbol is None and operation is not None and depth < 3 and isinstance(expression, ast.Name)
            and expression.id not in bindings and expression.id in operation.type_aliases):
        value, at_alias = operation.type_aliases[expression.id]
        readings = [_declared_schema_symbols(value, scope, catalog, operation, depth + 1)
                    for scope in (at_alias, operation.bindings, operation.body_bindings)]
        if any(reading is None for reading in readings):
            return None
        keys = [sorted(s.full_path if isinstance(s, ErrorSymbol) else s for s in reading) for reading in readings]
        return readings[0] if keys[0] == keys[1] == keys[2] else None
    return None if symbol is None else [symbol]


def _schema_set_text(paths: set[str]) -> str:
    return " | ".join(sorted(paths))


def _response_findings(
    operation: Operation,
    requirements: dict[int, set[str]],
    catalog: dict[str, ErrorSymbol],
) -> list[Finding]:
    response = _keyword(operation.decorator, "response")
    if not isinstance(response, ast.Dict):
        if not requirements:
            return []
        raise UsageError(
            f"required response mapping 분석 불능: {operation.identity}"
        )

    required_statuses = set(requirements)
    final_values: dict[int, ast.expr] = {}
    uncertain: set[int] = set()
    saw_dynamic = False
    for key, value in zip(response.keys, response.values):
        if key is None:
            saw_dynamic = True
            uncertain.update(required_statuses)
            uncertain.update(final_values)
            continue
        status = _status_from_expression(key, operation.bindings)
        if status is None:
            saw_dynamic = True
            uncertain.update(required_statuses)
            uncertain.update(final_values)
            continue
        final_values[status] = value
        uncertain.discard(status)

    findings: list[Finding] = []
    for status, returned in sorted(requirements.items()):
        if status in uncertain:
            raise UsageError(
                "required response mapping overwrite 분석 불능: "
                f"{operation.identity} status {status}"
            )
        value = final_values.get(status)
        if value is None:
            if saw_dynamic:
                raise UsageError(
                    f"required response mapping 분석 불능: {operation.identity} status {status}"
                )
            findings.append(
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "missing-response",
                    f"{operation.identity} 직접 반환 오류 status {status}가 "
                    "response=에서 누락",
                    symbol=operation.function.name,
                )
            )
            continue
        declared = _declared_schema_symbols(value, operation.bindings, catalog, operation)
        if declared is None:
            raise UsageError(
                "required response schema provenance 분석 불능: "
                f"{operation.identity} status {status}"
            )
        declared_paths = {
            symbol.full_path if isinstance(symbol, ErrorSymbol) else symbol
            for symbol in declared
        }
        if declared_paths != returned:
            # #63 — 선언은 그 status 에서 직접 반환하는 오류 타입 집합 «그대로» 다(단일이면 그
            # concrete, 복수면 Union). base 로 뭉뚱그리면 OpenAPI 가 endpoint 별 code 를 잃고,
            # 다른 타입을 적으면 문서가 거짓말한다(2026-08-25 개정 — concrete 선언 의무화).
            findings.append(
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "wrong-response-schema",
                    f"{operation.identity} status {status}는 직접 반환하는 오류 타입 그대로 "
                    f"{_schema_set_text(returned)} 선언 필요 (현재 {_schema_set_text(declared_paths)})",
                    symbol=operation.function.name,
                )
            )

    for status, value in sorted(final_values.items()):
        if status in uncertain or not 400 <= status <= 599 or requirements.get(status):
            continue
        declared = _declared_schema_symbols(value, operation.bindings, catalog, operation) or []
        schema = next((schema for schema in declared if isinstance(schema, ErrorSymbol)), None)
        if schema is not None:
            findings.append(
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "extra-bc-advertisement",
                    f"{operation.identity} status {status}의 {schema.full_path} "
                    "선언에 직접 BC 오류 반환 없음",
                    symbol=operation.function.name,
                )
            )
            continue
        # g — 직접 반환하지 않는 4xx · 5xx 는 Schema 가 무엇이든(`dict` · framework 예외 · 모르는 타입) 광고하지 않는다.
        shown = ast.unparse(value) if hasattr(ast, "unparse") else "Schema"
        findings.append(
            Finding(
                operation.relative_path,
                operation.decorator.lineno,
                "extra-error-advertisement",
                f"{operation.identity} status {status}의 `{shown}` 선언에 직접 BC 오류 반환 없음 — "
                f"경로 앞에서 나는 오류는 `response=` 가 아니라 경로 앞 응답으로 문서에 붙는다({PRE_ROUTE_SECTION})",
                symbol=operation.function.name,
            )
        )
    return findings


def _openapi_extra_findings(operation: Operation, tree: ast.Module | None = None) -> list[Finding]:
    """e — `openapi_extra` 의 responses 보충은 3.4 머리 보충(정수 키 · 오류 status 는 `headers` 만)만 받는다."""
    raw = _keyword(operation.decorator, "openapi_extra")
    extra = _resolved_extra(raw, tree) if raw is not None else None
    if extra is None or not isinstance(_top_level_responses(extra), ast.Dict):
        return []  # 글자 Dict 가 아닌 responses · 중첩 responses 는 tree 레인 몫(사건 하나 — 대표 줄은 tree)
    problems = _supplement_problems(
        extra, _declared_response_statuses(operation.function, operation.bindings)
    )
    if not problems:
        return []
    return [
        Finding(
            operation.relative_path,
            operation.decorator.lineno,
            "openapi-extra",
            f"{operation.identity} openapi_extra responses 보충 — {' · '.join(problems)}"
            f"({SUPPLEMENT_SECTION})",
            symbol=operation.function.name,
        )
    ]


def _api_schema_call_state(
    expression: ast.AST,
    bindings: dict[str, str],
) -> tuple[int | None, int | None]:
    selected: list[int] = []
    ambiguous: list[int] = []

    def visit(node: ast.AST, current: dict[str, str]) -> None:
        if isinstance(node, ast.Lambda):
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    visit(default, current)
            local = dict(current)
            arguments = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg is not None:
                arguments.append(node.args.vararg)
            if node.args.kwarg is not None:
                arguments.append(node.args.kwarg)
            for argument in arguments:
                local.pop(argument.arg, None)
            visit(node.body, local)
            return
        if isinstance(
            node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
        ):
            local = dict(current)
            for generator in node.generators:
                visit(generator.iter, local)
                for name in _target_names(generator.target):
                    local.pop(name, None)
                for condition in generator.ifs:
                    visit(condition, local)
            if isinstance(node, ast.DictComp):
                visit(node.key, local)
                visit(node.value, local)
            else:
                visit(node.elt, local)
            return
        if isinstance(node, ast.Call):
            resolved = _resolve_expression(node.func, current)
            if resolved in {
                API_SCHEMA_METHOD,
                f"{API_RECEIVER}.get_openapi_schema",
            }:
                selected.append(node.lineno)
            elif resolved == AMBIGUOUS_API_SCHEMA_METHOD or (
                _is_ambiguous_resolution(resolved)
                and resolved.endswith(".get_openapi_schema")
            ):
                ambiguous.append(node.lineno)
        for child in ast.iter_child_nodes(node):
            visit(child, current)

    visit(expression, bindings)
    return (
        min(selected) if selected else None,
        min(ambiguous) if ambiguous else None,
    )


def _function_local_names(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    names: set[str] = set()
    global_names: set[str] = set()
    nonlocal_names: set[str] = set()

    class Collector(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            names.add(node.name)
            for expression in (*node.decorator_list, *node.args.defaults):
                self.visit(expression)
            for default in node.args.kw_defaults:
                if default is not None:
                    self.visit(default)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            names.add(node.name)
            for expression in (*node.decorator_list, *node.bases):
                self.visit(expression)
            for keyword in node.keywords:
                self.visit(keyword.value)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                names.add(node.id)

        def visit_Import(self, node: ast.Import) -> None:
            names.update(
                alias.asname or alias.name.split(".", 1)[0] for alias in node.names
            )

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            names.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name != "*"
            )

        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
            if node.name:
                names.add(node.name)
            if node.type is not None:
                self.visit(node.type)
            for statement in node.body:
                self.visit(statement)

        def visit_MatchAs(self, node: ast.AST) -> None:
            name = getattr(node, "name", None)
            if name:
                names.add(name)
            pattern = getattr(node, "pattern", None)
            if pattern is not None:
                self.visit(pattern)

        def visit_MatchStar(self, node: ast.AST) -> None:
            name = getattr(node, "name", None)
            if name:
                names.add(name)

        def visit_MatchMapping(self, node: ast.AST) -> None:
            rest = getattr(node, "rest", None)
            if rest:
                names.add(rest)
            for pattern in getattr(node, "patterns", ()):
                self.visit(pattern)

        def visit_Global(self, node: ast.Global) -> None:
            global_names.update(node.names)

        def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
            nonlocal_names.update(node.names)

        def visit_comprehension(self, node: ast.comprehension) -> None:
            self.visit(node.iter)
            for condition in node.ifs:
                self.visit(condition)

    collector = Collector()
    for statement in function.body:
        collector.visit(statement)
    return names - global_names - nonlocal_names


def _attribute_assignment_targets(statement: ast.stmt) -> list[ast.Attribute]:
    targets: list[ast.AST] = []
    if isinstance(statement, ast.Assign):
        targets.extend(statement.targets)
    elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
        targets.append(statement.target)
    elif isinstance(statement, ast.AugAssign):
        targets.append(statement.target)

    attributes: list[ast.Attribute] = []

    def collect(target: ast.AST) -> None:
        if isinstance(target, ast.Attribute):
            attributes.append(target)
        elif isinstance(target, ast.Starred):
            collect(target.value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                collect(element)

    for target in targets:
        collect(target)
    return attributes


def _api_module_findings(
    parsed: ParsedSource,
    *,
    selected_imports: frozenset[str] = frozenset(),
    require_constructor: bool = True,
) -> tuple[list[Finding], frozenset[str]]:
    findings: list[Finding] = []
    receiver_events = 0
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    final_module_bindings = _final_module_symbol_bindings(parsed)
    documented_nodes: set[int] = set()  # 3.2 꼴 클래스 안 — 그 몸통의 `super().get_openapi_schema(...)` 는 후처리가 아니다
    deferred_functions: list[
        tuple[ast.FunctionDef | ast.AsyncFunctionDef, dict[str, str]]
    ] = []

    def scan_expression(expression: ast.AST, bindings: dict[str, str]) -> None:
        if id(expression) in documented_nodes:
            return
        selected_line, ambiguous_line = _api_schema_call_state(expression, bindings)
        if ambiguous_line is not None:
            raise UsageError(
                "selected API receiver provenance 분석 불능: "
                f"{parsed.relative_path}:{ambiguous_line} get_openapi_schema"
            )
        if selected_line is not None:
            findings.append(
                Finding(
                    parsed.relative_path,
                    selected_line,
                    "openapi-postprocess",
                    "선택 API receiver의 get_openapi_schema 직접 호출/후처리",
                )
            )

    def scan_definition_expressions(
        definition: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        bindings: dict[str, str],
    ) -> None:
        expressions: list[ast.AST] = list(definition.decorator_list)
        if isinstance(definition, ast.ClassDef):
            expressions.extend(definition.bases)
            expressions.extend(keyword.value for keyword in definition.keywords)
        else:
            expressions.extend(definition.args.defaults)
            expressions.extend(
                default
                for default in definition.args.kw_defaults
                if default is not None
            )
            if annotations_evaluated:
                arguments = [
                    *definition.args.posonlyargs,
                    *definition.args.args,
                    *definition.args.kwonlyargs,
                ]
                if definition.args.vararg is not None:
                    arguments.append(definition.args.vararg)
                if definition.args.kwarg is not None:
                    arguments.append(definition.args.kwarg)
                expressions.extend(
                    argument.annotation
                    for argument in arguments
                    if argument.annotation is not None
                )
                if definition.returns is not None:
                    expressions.append(definition.returns)
        for expression in expressions:
            scan_expression(expression, bindings)

    def scan_monkeypatch(
        statement: ast.stmt, bindings: dict[str, str]
    ) -> None:
        for target in _attribute_assignment_targets(statement):
            if target.attr != "get_openapi_schema":
                continue
            receiver = _resolve_expression(target.value, bindings)
            if _is_ambiguous_resolution(receiver):
                raise UsageError(
                    "selected API receiver provenance 분석 불능: "
                    f"{parsed.relative_path}:{target.lineno} get_openapi_schema assignment"
                )
            if receiver == API_RECEIVER:
                findings.append(
                    Finding(
                        parsed.relative_path,
                        target.lineno,
                        "openapi-monkeypatch",
                        "선택 API receiver의 get_openapi_schema assignment/monkeypatch",
                    )
                )
        for call in ast.walk(statement):
            if not (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "setattr"
                and _resolve_expression(call.func, bindings) == BUILTIN_SETATTR
                and len(call.args) >= 2
                and isinstance(call.args[1], ast.Constant)
                and call.args[1].value == "get_openapi_schema"
            ):
                continue
            receiver = _resolve_expression(call.args[0], bindings)
            if _is_ambiguous_resolution(receiver):
                raise UsageError(
                    "selected API receiver provenance 분석 불능: "
                    f"{parsed.relative_path}:{call.lineno} setattr"
                )
            if receiver == API_RECEIVER:
                findings.append(
                    Finding(
                        parsed.relative_path,
                        call.lineno,
                        "openapi-monkeypatch",
                        "선택 API receiver의 literal setattr monkeypatch",
                    )
                )

    def scan_block(
        statements: list[ast.stmt],
        incoming: dict[str, str],
        *,
        scope_kind: str,
        deferred: list[
            tuple[ast.FunctionDef | ast.AsyncFunctionDef, dict[str, str]]
        ],
    ) -> dict[str, str]:
        nonlocal receiver_events
        def visit_expression(node: ast.AST, state: ProvenanceState) -> None:
            scan_expression(node, state.bindings)

        def visit_function(statement: ast.stmt, state: ProvenanceState) -> None:
            scan_definition_expressions(statement, state.bindings)
            deferred.append((statement, dict(state.bindings)))
            _drop_provenance_names(
                state,
                _evaluated_named_expression_names(
                    statement,
                    annotations_evaluated=annotations_evaluated,
                )
                | {statement.name},
            )

        def visit_class(statement: ast.ClassDef, state: ProvenanceState) -> None:
            scan_definition_expressions(statement, state.bindings)
            bases = {
                _resolve_expression(base, state.bindings) for base in statement.bases
            }
            if require_constructor and any(
                _is_ambiguous_resolution(base) for base in bases
            ):
                raise UsageError(
                    "Ninja API subclass provenance 분석 불능: "
                    f"{parsed.relative_path}:{statement.lineno} {statement.name}"
                )
            api_subclass = require_constructor and any(
                base in ROOT_API_CONSTRUCTORS
                or (base is not None and base.startswith(API_TYPE_PREFIX))
                for base in bases
            )
            documented_class = (
                api_subclass
                and scope_kind == "module"
                and _is_documented_api_class(statement, state.bindings, final_module_bindings)
            )
            if documented_class:
                documented_nodes.update(id(node) for node in ast.walk(statement))
            if api_subclass and not documented_class:
                for member in statement.body:
                    if (
                        isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and member.name == "get_openapi_schema"
                    ):
                        findings.append(
                            Finding(
                                parsed.relative_path,
                                member.lineno,
                                "openapi-override",
                                f"Ninja API subclass {statement.name}의 "
                                "get_openapi_schema override",
                                symbol=member.name,
                            )
                        )
            class_bindings = dict(state.bindings)
            scan_block(
                statement.body,
                class_bindings,
                scope_kind="class",
                deferred=deferred,
            )
            _drop_provenance_names(
                state,
                _evaluated_named_expression_names(
                    statement,
                    annotations_evaluated=annotations_evaluated,
                )
                | {statement.name},
            )
            if api_subclass:
                state.bindings[statement.name] = (
                    f"{API_TYPE_PREFIX}{statement.name}"
                )

        def visit_simple(statement: ast.stmt, state: ProvenanceState) -> None:
            nonlocal receiver_events
            bindings = state.bindings
            scan_expression(statement, bindings)
            scan_monkeypatch(statement, bindings)
            targets, value = _assigned_value(statement)
            names = {name for target in targets for name in _target_names(target)}
            derived: str | None = None
            if value is not None:
                if (
                    require_constructor
                    and isinstance(value, ast.Call)
                    and scope_kind == "module"
                ):
                    constructor = _resolve_expression(value.func, bindings)
                    if _is_ambiguous_resolution(constructor):
                        raise UsageError(
                            "selected API constructor provenance 분석 불능: "
                            f"{parsed.relative_path}:{value.lineno}"
                        )
                    if constructor in ROOT_API_CONSTRUCTORS or (
                        constructor is not None
                        and constructor.startswith(API_TYPE_PREFIX)
                    ):
                        derived = API_RECEIVER
                        receiver_events += 1
                if derived is None:
                    resolved_value = _resolve_expression(value, bindings)
                    if resolved_value in {
                        API_RECEIVER,
                        API_SCHEMA_METHOD,
                        AMBIGUOUS_BINDING,
                        AMBIGUOUS_API_SCHEMA_METHOD,
                        f"{API_RECEIVER}.get_openapi_schema",
                    }:
                        derived = resolved_value
                        if derived == f"{API_RECEIVER}.get_openapi_schema":
                            derived = API_SCHEMA_METHOD
            if _update_imports(statement, parsed.relative_path, bindings):
                for name, origin in tuple(bindings.items()):
                    if origin in selected_imports:
                        bindings[name] = API_RECEIVER
                return
            _drop_provenance_names(
                state,
                _evaluated_named_expression_names(
                    statement,
                    annotations_evaluated=annotations_evaluated,
                ),
            )
            for name in names:
                bindings.pop(name, None)
            if len(names) == 1 and derived is not None:
                bindings[next(iter(names))] = derived
            if not targets:
                _drop_provenance_names(state, _direct_bound_names(statement))

        return _statement_provenance_flow(
            statements,
            ProvenanceState(dict(incoming), {}),
            annotations_evaluated=annotations_evaluated,
            on_simple=visit_simple,
            on_function=visit_function,
            on_class=visit_class,
            on_expression=visit_expression,
        ).bindings

    def scan_function(
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        outer_bindings: dict[str, str],
    ) -> None:
        local = dict(outer_bindings)
        arguments = {
            argument.arg
            for argument in (
                *function.args.posonlyargs,
                *function.args.args,
                *function.args.kwonlyargs,
            )
        }
        if function.args.vararg is not None:
            arguments.add(function.args.vararg.arg)
        if function.args.kwarg is not None:
            arguments.add(function.args.kwarg.arg)
        for name in arguments | _function_local_names(function):
            local.pop(name, None)
        nested: list[
            tuple[ast.FunctionDef | ast.AsyncFunctionDef, dict[str, str]]
        ] = []
        final_local = scan_block(
            function.body,
            local,
            scope_kind="function",
            deferred=nested,
        )
        for nested_function, definition_bindings in nested:
            scan_function(
                nested_function,
                _merge_bindings([definition_bindings, final_local]),
            )

    bindings = scan_block(
        parsed.tree.body,
        {"setattr": BUILTIN_SETATTR},
        scope_kind="module",
        deferred=deferred_functions,
    )
    final_receivers = {
        name for name, value in bindings.items() if value == API_RECEIVER
    }
    if require_constructor and (receiver_events != 1 or not final_receivers):
        raise UsageError(
            "selected API receiver provenance 분석 불능: proven constructor event와 "
            "final receiver 필요"
        )
    for function, _ in deferred_functions:
        scan_function(function, bindings)
    module = ".".join(parsed.relative_path.with_suffix("").parts)
    exports = frozenset(f"{module}.{name}" for name in final_receivers)
    return findings, exports


def _deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    unique: dict[tuple[Path, int, str, str], Finding] = {}
    for finding in findings:
        key = (
            finding.relative_path,
            finding.lineno,
            finding.category,
            finding.detail,
        )
        unique[key] = finding
    return sorted(
        unique.values(),
        key=lambda item: (
            item.relative_path.as_posix(),
            item.lineno,
            item.category,
            item.detail,
        ),
    )


def _module_overlap_keys(findings: list[Finding]) -> set[tuple[str, str, int]]:
    """module-scan 계열 code 사건의 tree 대응 좌표(앵커 레인 선점 억제 키 — 귀속
    매핑표 v2 overlap 절): override 는 같은 def 행, monkeypatch 는 같은 대입 행.
    (openapi-extra 는 function 행이 필요해 _code_findings 의 operation 루프가 채운다.)"""
    keys: set[tuple[str, str, int]] = set()
    for finding in findings:
        if finding.category == "openapi-override":
            keys.add(("override", finding.relative_path.as_posix(), finding.lineno))
        elif finding.category == "openapi-monkeypatch":
            keys.add(("monkeypatch", finding.relative_path.as_posix(), finding.lineno))
        elif finding.category == "openapi-postprocess":
            keys.add(("postprocess", finding.relative_path.as_posix(), finding.lineno))
    return keys


def _catalog_status_resolver(catalog: dict[str, ErrorSymbol]) -> "StatusResolver":
    """code 레인 f — branch 마지막 `Status` 의 status 를 오류 카탈로그로 푼다(`Status(error.status, error)` 포함)."""

    def resolve(call: ast.Call, block: list[ast.stmt], operation: Operation) -> int | None:
        status = _plain_status(call, block, operation)
        if status is not None:
            return status
        bindings = dict(operation.body_bindings)
        instances: dict[str, ErrorInstance | str] = {}
        for statement in block[:-1]:
            targets, value = _assigned_value(statement)
            names = {name for target in targets for name in _target_names(target)}
            if value is None or len(names) != 1:
                continue
            try:
                instance = _constructed_error(value, bindings, catalog, operation.relative_path)
            except UsageError:
                instance = None
            if instance is not None:
                instances[next(iter(names))] = instance
        last = block[-1]
        if not isinstance(last, ast.Return):
            return None
        try:
            found = _status_return_instance(last, bindings, instances)
        except UsageError:
            return None
        return found.direct_status if found is not None else None

    return resolve


def _code_findings(
    config: Config,
) -> tuple[list[str], list[Finding], set[tuple[str, str, int]], "dict[Path, StatusResolver]"]:
    parsed_by_path = _parse_code_sources(config)
    findings: list[Finding] = []
    selected_imports: frozenset[str] = frozenset()
    if config.api_module is not None:
        findings, selected_imports = _api_module_findings(parsed_by_path[Path(config.api_module)])
    controller_operations: list[Operation] = []
    for raw in config.controller_modules:
        controller = parsed_by_path[Path(raw)]
        controller_findings, _ = _api_module_findings(
            controller,
            selected_imports=selected_imports,
            require_constructor=False,
        )
        findings.extend(controller_findings)
        controller_operations.extend(_collect_operations(controller))
    analysis: list[str] = []
    overlap_keys: set[tuple[str, str, int]] = set()
    try:
        catalog = _error_catalog(config, parsed_by_path)
    except UsageError as exc:
        issue = str(exc)
        if issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "):
            analysis.append(issue)
            deduplicated = _deduplicate_findings(findings)
            return analysis, deduplicated, _module_overlap_keys(deduplicated), {}
        raise
    resolver = _catalog_status_resolver(catalog)
    resolvers: dict[Path, StatusResolver] = {Path(raw): resolver for raw in config.controller_modules}
    for operation in controller_operations:
        try:
            requirements = _operation_requirements(operation, catalog)
            findings.extend(_response_findings(operation, requirements, catalog))
            parsed_source = parsed_by_path.get(operation.relative_path)
            extra_findings = _openapi_extra_findings(operation, parsed_source.tree if parsed_source is not None else None)
            if extra_findings:
                overlap_keys.add(
                    (
                        "openapi-extra",
                        operation.relative_path.as_posix(),
                        operation.function.lineno,
                    )
                )
            findings.extend(extra_findings)
        except UsageError as exc:
            issue = str(exc)
            if not config.anchor_baseline and not issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "):
                raise
            analysis.append(issue)  # 기준선 재실행은 첫 못 읽음에서 끊지 않고 모은다(F4-59 ①)
    deduplicated = _deduplicate_findings(findings)
    return sorted(set(analysis)), deduplicated, overlap_keys | _module_overlap_keys(deduplicated), resolvers


def _print_repo_scan_findings(findings: Findings) -> None:
    print(
        "[check-openapi-error-declaration] BLOCKER — openapi_extra 의 responses 보충이 "
        "머리 보충 꼴이 아니다(정수 키 · response= 에 선언된 status · 오류 status 는 headers 만):"
    )
    emit_all(findings, printer=print)
    print(
        f"  근거: {SUPPLEMENT_SECTION}. 경로 코드가 직접 반환하는 오류는 "
        "response={...} 에 그 status 의 실제 오류 타입 그대로 선언하고, 그 오류의 머리만 "
        "openapi_extra 의 정수 키 headers 로 보충한다 — 경로 앞에서 나는 오류는 "
        f"경로 앞 응답이 붙인다({PRE_ROUTE_SECTION}). 설계로 반송하라."
    )


def _code_findings_records(findings: list[Finding]) -> Findings:
    # msg 는 `{category}: {detail}` — stdout 라인과 record message 가 같은 문면이다
    # (출력 계약 v2 «openapi 행» 확정 · 귀속 매핑표 v2 부속 A-1).
    records = Findings(defer=True)
    for finding in findings:
        records.add(
            "#63",
            where=f"{finding.relative_path}:{finding.lineno}",
            msg=f"{finding.category}: {finding.detail}",
            symbol=finding.symbol,
        )
    return records


def _print_code_findings(records: Findings) -> None:
    print(
        "[check-openapi-error-declaration] BLOCKER — 직접 반환 BC 오류와 response= "
        "선언 계약 불일치(그 status 의 실제 오류 타입 그대로 — base 뭉뚱그림 금지) 또는 수동 OpenAPI 후처리:"
    )
    emit_all(records, printer=print)
    print(
        "  조치: 각 직접 반환 status를 그 status에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base — base 뭉뚱그림 금지) 선언하고, "
        "직접 반환하지 않는 4xx·5xx 광고(Schema 무관)와 "
        "정해진 꼴 밖의 openapi_extra/get_openapi_schema 후처리를 "
        "제거한다 — 경로 앞 오류는 경로 앞 응답이, 오류의 머리는 정수 키 머리 보충이 문서에 싣는다"
        f"({PRE_ROUTE_SECTION} · {SUPPLEMENT_SECTION})."
    )


# ── 표준 트리 슬라이스 — #63 (D27 «OpenAPI 도 같다») ────────────────────────
#
# 오류 응답은 operation 이 `response={status: 그 status 의 실제 오류 타입}` 로 «직접 선언»한다 —
# driving 층의 `get_openapi_schema` override · `openapi_schema` monkeypatch 는 사후 변형이라 위반이고,
# openapi_extra 의 responses 보충은 3.4 머리 보충(정수 키 · `response=` 에 선언된 status · 오류
# status 는 `headers` 만)만 받는다. 모든 프로필에서 돈다.

_TREE_DRIVING_SET = frozenset({"driving_layer"})
_TREE_LAYERS63 = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
_TREE_APP_MARKERS63 = ("models.py", "apps.py", "views.py", "admin.py")


def _tree_bcs63(root: Path) -> list[Path]:
    out: list[Path] = []
    for c in (root / "application",):
        if not c.is_dir() or set(c.parts) & CODE_SKIP_DIRS:
            continue
        out.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return out


def _tree_adopted63(bcs: list[Path]) -> bool:
    for bc in bcs:
        if any((bc / n).is_dir() for n in _TREE_LAYERS63):
            return True
        if any((bc / m).is_file() for m in _TREE_APP_MARKERS63):
            return True
        if any(p.is_dir() and p.name.startswith("django_") for p in bc.iterdir()):
            return True
    return False


def _dict_has_key(node: ast.AST, key: str) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Dict):
            for k in sub.keys:
                if isinstance(k, ast.Constant) and k.value == key:
                    return True
    return False


def _resolved_extra(node: ast.AST, tree: ast.Module | None) -> ast.Dict | None:
    """`openapi_extra=` 값 — 글자 Dict 그대로, 같은 모듈 맨 위에서 한 번만 묶인 이름이면 그 글자 Dict(못 풀면 None)."""
    if isinstance(node, ast.Dict):
        return node
    if not isinstance(node, ast.Name) or tree is None:
        return None
    stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == node.id and isinstance(n.ctx, ast.Store)]
    values = [
        value
        for statement in tree.body
        for targets, value in [_assigned_value(statement)]
        if value is not None and any(isinstance(target, ast.Name) and target.id == node.id for target in targets)
    ]
    other_bindings = any(
        (isinstance(n, (ast.Import, ast.ImportFrom)) and any((a.asname or a.name.split(".")[0]) == node.id for a in n.names))
        or (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == node.id)
        or (isinstance(n, (ast.Global, ast.Nonlocal)) and node.id in n.names)
        for n in ast.walk(tree)
    )
    if len(stores) == 1 and len(values) == 1 and not other_bindings and isinstance(values[0], ast.Dict):
        return values[0]
    return None


EXTRA_NOT_LITERAL: str = "`openapi_extra` 가 글자 Dict 가 아니다(같은 모듈에서 한 번 묶인 글자 Dict 이름도 아니다)"


def _extra_problems(node: ast.AST, tree: ast.Module | None, declared: set[int]) -> list[str]:
    """e 의 판정 입구 — 글자 Dict 로 풀리면 responses 보충 판정, 못 풀면 막는다(보충을 가릴 수 없다)."""
    extra = _resolved_extra(node, tree)
    if extra is None:
        return [EXTRA_NOT_LITERAL]
    if not _dict_has_key(extra, "responses"):
        return []
    return _supplement_problems(extra, declared)


def _top_level_responses(extra: ast.AST) -> ast.AST | None:
    if not isinstance(extra, ast.Dict):
        return None
    for key, value in zip(extra.keys, extra.values):
        if isinstance(key, ast.Constant) and key.value == "responses":
            return value
    return None


def _int_status_key(node: ast.AST | None) -> int | None:
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int)
        and not isinstance(node.value, bool)
    ):
        return node.value
    return None


def _supplement_problems(extra: ast.AST, declared: set[int]) -> list[str]:
    """`openapi_extra` 의 responses 보충 판정(e) — 빈 목록이면 받는 꼴.

    받는 꼴은 정확히 이것뿐이다: top-level Dict 의 "responses" 값이 Dict 이고, 키 전부가
    **정수 글자**이며 그 status 가 operation `response=` 에 선언돼 있고, 오류 status(400–599)의
    값은 `headers` 칸 하나만 가진 Dict 일 때(성공 status 는 메타데이터 보충). 숫자 문자열 키는
    Ninja 가 정수 키 항목과 따로 남겨 문서에서 몸통 · `description` 이 사라지므로 성공 · 오류
    모두 위반이고, 변수 · 상수 표현식 키 · `**` · 중첩 responses · 비-Dict 도 위반이다."""
    responses = _top_level_responses(extra)
    if responses is None:
        return ["responses 가 top-level 칸이 아니다"]
    if not isinstance(responses, ast.Dict):
        return ["responses 값이 글자 Dict 가 아니다"]
    problems: list[str] = []
    if not responses.keys:
        problems.append("빈 responses")
    for status_key, value in zip(responses.keys, responses.values):
        if status_key is None:
            problems.append("`**` 펼침")
            continue
        status = _int_status_key(status_key)
        if status is None:
            if (
                isinstance(status_key, ast.Constant)
                and isinstance(status_key.value, str)
                and status_key.value.isdigit()
            ):
                problems.append(f'숫자 문자열 키 "{status_key.value}" — 정수 키 {status_key.value} 로 쓴다')
            else:
                problems.append("변수 · 표현식 키 — 정수 글자로 쓴다")
            continue
        if not 100 <= status <= 599:
            problems.append(f"status {status} — 100–599 밖")
            continue
        if status not in declared:
            problems.append(f"status {status} — `response=` 에 선언되지 않았다")
            continue
        if 400 <= status <= 599 and not (
            isinstance(value, ast.Dict)
            and len(value.keys) == 1
            and isinstance(value.keys[0], ast.Constant)
            and value.keys[0].value == "headers"
        ):
            problems.append(f"오류 status {status} 에는 `headers` 칸 하나만 보충한다")
    return problems


def _declared_response_statuses(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, str],
) -> set[int]:
    statuses: set[int] = set()
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if keyword.arg != "response" or not isinstance(keyword.value, ast.Dict):
                continue
            for key in keyword.value.keys:
                if key is None:
                    continue
                status = _status_from_expression(key, bindings)
                if status is not None:
                    statuses.add(status)
    return statuses


def _header_supplement(extra: ast.AST | None, tree: ast.Module | None = None) -> dict[int, set[str]] | None:
    """머리 보충 — status → 머리 이름(소문자). `headers` 값이 같은 모듈 맨 위에서 한 번 묶인 글자 Dict 이름이면 푼다.
    글자로 읽지 못하면 None."""
    if extra is None:
        return {}
    if not isinstance(extra, ast.Dict):
        return None
    if not _dict_has_key(extra, "responses"):
        return {}
    responses = _top_level_responses(extra)
    if not isinstance(responses, ast.Dict):
        return None
    supplement: dict[int, set[str]] = {}
    for status_key, value in zip(responses.keys, responses.values):
        status = _int_status_key(status_key)
        if status is None or not isinstance(value, ast.Dict):
            return None
        names: set[str] = set()
        for key, item in zip(value.keys, value.values):
            if not (isinstance(key, ast.Constant) and key.value == "headers"):
                continue
            item = _resolved_extra(item, tree)
            if item is None:
                return None
            for header in item.keys:
                if not (isinstance(header, ast.Constant) and isinstance(header.value, str)):
                    return None
                names.add(header.value.lower())
        supplement[status] = names
    return supplement


def _tree_slice63(root: Path) -> tuple[Findings, list[tuple[str, str, int]]]:
    """tree 3사이트 — 공용 포매터 violation 문법(B형 locator `{rel}:{lineno}` 정형화).

    엔트리와 같은 순서의 keys 는 앵커 레인 tree↔code 동일 사건 선점 억제의 좌표다
    (귀속 매핑표 v2 overlap 절 — override/monkeypatch 는 같은 행, openapi_extra 는
    같은 function def 행에서 code 레인과 만난다)."""
    findings = Findings(defer=True)
    keys: list[tuple[str, str, int]] = []
    for rel, mod in sorted(_parsed_driving_modules(root).items(), key=lambda item: item[0].as_posix()):
        bindings = _final_module_symbol_bindings(ParsedSource(rel, "", mod))
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "get_openapi_schema":
                    where = f"{rel}:{node.lineno}"
                    msg = ("`get_openapi_schema` override — 문서 재정의는 루트 API 모듈의 정해진 클래스 하나뿐이다"
                           f"(경로 앞 오류는 그 클래스가 붙인다 · {PRE_ROUTE_SECTION})")
                    findings.add("#63", where=where, msg=msg)
                    keys.append(("override", rel.as_posix(), node.lineno))
                for deco in node.decorator_list:
                    if not isinstance(deco, ast.Call):
                        continue
                    for kw in deco.keywords:
                        if kw.arg == "openapi_extra":
                            problems = _extra_problems(kw.value, mod, _declared_response_statuses(node, bindings))
                            if not problems:
                                continue  # 머리 보충 · 성공 메타데이터 보충 — 받는 꼴(방출·overlap key 함께 생략)
                            where = f"{rel}:{node.lineno}"
                            msg = (f"`openapi_extra` 의 responses 보충 — {' · '.join(problems)} "
                                   "(보충은 `response=` 에 선언된 status 의 정수 키뿐 — 오류 status 는 `headers` 만 · "
                                   f"오류 응답 몸통은 `response=` 에 그 status 의 실제 오류 타입 그대로 · {SUPPLEMENT_SECTION})")
                            findings.add("#63", where=where, msg=msg)
                            keys.append(("openapi-extra", rel.as_posix(), node.lineno))
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Attribute) and t.attr in ("openapi_schema", "get_openapi_schema"):
                        where = f"{rel}:{node.lineno}"
                        msg = f"`{t.attr}` monkeypatch — OpenAPI 를 사후 변형하지 않는다"
                        findings.add("#63", where=where, msg=msg)
                        keys.append(("monkeypatch", rel.as_posix(), node.lineno))
    return findings, keys


# ── 경로 앞 응답 — #63 (F4-173 · 2026-11-13) ─────────────────────────────────
#
# API 문서는 그 경로에서 날 수 있는 의도된 오류를 누가 보내든 모두 적는다. 경로 앞(Ninja 인증 ·
# CSRF · 권한 · throttle · 입력 해석 · Django 상한 · 미들웨어(서드파티 포함) · 앞단)에서 나는 답은 루트 API
# 모듈의 정해진 클래스 하나(a)가 플러그인 정본 `framework/ninja/pre_route_responses.py`(b — 이 검사기
# 옆 자산과 AST 대조)와 프로젝트 표 `framework/ninja/pre_route_response_table.py`(b 정적 검증 ·
# d 미들웨어 답 대조 — d 가 기계로 대조하는 것은 프로젝트 안 미들웨어뿐이고 서드파티 답은 리뷰어 몫)로 붙인다. 그 꼴이 서지 않으면 operation 마다 c 줄이 서고, 주입 응답에 싣는
# 머리는 그 뒤 반환하는 status 의 머리 보충에 있어야 한다(f). 모든 프로필에서 돈다.

PRE_ROUTE_PATH: Path = Path("framework/ninja/pre_route_responses.py")
PRE_ROUTE_TABLE_PATH: Path = Path("framework/ninja/pre_route_response_table.py")
PRE_ROUTE_FUNCTION: str = "framework.ninja.pre_route_responses.add_pre_route_responses"
OPENAPI_SCHEMA_TYPE: str = "ninja.openapi.schema.OpenAPISchema"
# 받는 정본 — 이 검사기와 같은 폴더의 자산 파일. 정본 판이 바뀌어 옛 판도 받을 때는 그 판 자산을
# 파일로 더하고 여기 이름을 잇는다(지문 = 그 자산의 AST 대조 꼴 — 실행 Python 이 같은 꼴로 읽는다).
PRE_ROUTE_CANONICAL_ASSETS: tuple[str, ...] = ("pre_route_responses_canonical.py",)
DOCUMENTED_API_METHOD: str = (
    "def get_openapi_schema(\n"
    "    self, *, path_prefix: str | None = None, path_params: dict[str, object] | None = None\n"
    ") -> OpenAPISchema:\n"
    "    return add_pre_route_responses(self, super().get_openapi_schema(path_prefix=path_prefix, path_params=path_params))\n"
)
PRE_ROUTE_TABLE_NAMES: tuple[str, ...] = ("PRE_ROUTE_RESPONSES", "BAD_REQUEST_RESPONSE", "NOT_API_MIDDLEWARE")
PROJECT_ROW_WHEN: frozenset[str] = frozenset({"all", "auth", "body", "input"})
DEFAULT_BAD_REQUEST: dict[str, str] = {"media_type": "text/html"}
DOTTED_PATH_RE: re.Pattern[str] = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")
HTTP_RESPONSE_TYPES: frozenset[str] = frozenset({"django.http.HttpResponse", "django.http.response.HttpResponse"})
MIDDLEWARE_HOOKS: frozenset[str] = frozenset(
    {
        "__call__",
        "__acall__",
        "process_request",
        "process_view",
        "process_exception",
        "process_response",
        "process_template_response",
    }
)
# 응답 생성자 → `status` 위치 인자 자리(없으면 키워드만).
MIDDLEWARE_RESPONSE_CALLS: dict[str, int | None] = {
    "django.http.HttpResponse": 2,
    "django.http.response.HttpResponse": 2,
    "django.http.JsonResponse": None,
    "django.http.response.JsonResponse": None,
    "django.shortcuts.render": 4,
    "django.template.response.TemplateResponse": 4,
}
MIDDLEWARE_FIXED_STATUS: dict[str, int] = {
    f"{module}.{name}": status
    for module in ("django.http", "django.http.response")
    for name, status in (
        ("HttpResponseBadRequest", 400),
        ("HttpResponseForbidden", 403),
        ("HttpResponseNotFound", 404),
        ("HttpResponseNotAllowed", 405),
        ("HttpResponseGone", 410),
        ("HttpResponseServerError", 500),
    )
}
MIDDLEWARE_RAISED_STATUS: dict[str, int] = {
    "django.core.exceptions.PermissionDenied": 403,
    "django.core.exceptions.BadRequest": 400,
    "django.core.exceptions.SuspiciousOperation": 400,
    "django.core.exceptions.DisallowedHost": 400,
    "django.core.exceptions.DisallowedRedirect": 400,
    "django.core.exceptions.SuspiciousFileOperation": 400,
    "django.core.exceptions.SuspiciousMultipartForm": 400,
    "django.core.exceptions.RequestDataTooBig": 400,
    "django.core.exceptions.TooManyFieldsSent": 400,
    "django.core.exceptions.TooManyFilesSent": 400,
    "django.contrib.sessions.exceptions.SuspiciousSession": 400,
    "django.http.Http404": 404,
    "django.http.response.Http404": 404,
}

# 캐시 지시 머리 — 오류 문서 대조 밖(2026-11-13 사용자 결정). f · d 의 머리 대조가 이 이름(소문자)은 보지 않는다.
CACHE_DIRECTIVE_HEADERS: frozenset[str] = frozenset({"cache-control", "pragma", "expires"})

_SOURCES: "dict[tuple[Path, Path], str | None]" = {}
_PARSED: "dict[tuple[Path, Path], ast.Module | None]" = {}
_DRIVING: "dict[Path, dict[Path, ast.Module]]" = {}


def _project_source(root: Path, relative_path: Path) -> str | None:
    key = (root, relative_path)
    if key not in _SOURCES:
        try:
            _SOURCES[key] = (root / relative_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            _SOURCES[key] = None
    return _SOURCES[key]


def _parse_project_file(root: Path, relative_path: Path) -> ast.Module | None:
    key = (root, relative_path)
    if key not in _PARSED:
        source = _project_source(root, relative_path)
        try:
            _PARSED[key] = ast.parse(source, filename=relative_path.as_posix()) if source is not None else None
        except (SyntaxError, ValueError):
            _PARSED[key] = None
    return _PARSED[key]


def _parsed_driving_modules(root: Path) -> dict[Path, ast.Module]:
    """tree 레인 대상(경로에 `driving_layer` 가 든 운영 파일) — 한 실행에 한 번 읽는다."""
    if root not in _DRIVING:
        modules: dict[Path, ast.Module] = {}
        for path in sorted(root.rglob("*.py")):
            relative = path.relative_to(root)
            if not _scan_is_production_path(relative):
                continue
            tree = _parse_project_file(root, relative)
            if tree is not None:
                modules[relative] = tree
        _DRIVING[root] = modules
    return _DRIVING[root]


def _project_python_files(root: Path) -> list[Path]:
    """루트 API · settings · URLconf · registrar · 미들웨어를 찾는 운영 파일(숨김 폴더 = 도구 영역은 뺀다)."""
    found: list[Path] = []
    for directory, names, filenames in os.walk(root):
        relative_directory = Path(directory).relative_to(root)
        names[:] = sorted(
            name
            for name in names
            if name not in CODE_SKIP_DIRS and name not in TEST_DIR_NAMES and not name.startswith(".")
        )
        for filename in sorted(filenames):
            relative = relative_directory / filename
            if _is_code_production_path(relative):
                found.append(relative)
    return found


def _module_path(root: Path, module: str) -> Path | None:
    base = Path(*module.split("."))
    for candidate in (base.with_suffix(".py"), base / "__init__.py"):
        if (root / candidate).is_file():
            return candidate
    return None


def _module_statements(statements: list[ast.stmt]) -> "list[ast.stmt]":
    """모듈 실행 문장 — 함수 · 클래스 몸통 밖(조건 · try · with · 반복 안 포함)."""
    out: list[ast.stmt] = []
    for statement in statements:
        out.append(statement)
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for name in ("body", "orelse", "finalbody"):
            block = getattr(statement, name, None)
            if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                out.extend(_module_statements(block))
        for handler in getattr(statement, "handlers", ()):
            out.extend(_module_statements(handler.body))
    return out


def _documented_method_dump() -> str:
    return ast.dump(ast.parse(DOCUMENTED_API_METHOD).body[0], include_attributes=False)


def _is_documented_api_class(
    node: ast.ClassDef,
    bindings: dict[str, str],
    final: dict[str, str],
) -> bool:
    """3.2 꼴 — 루트 API 기저 하나의 하위 클래스 · 메서드 `get_openapi_schema` 하나(서명 · 몸통 글자 그대로)."""
    if node.decorator_list or node.keywords or len(node.bases) != 1 or getattr(node, "type_params", None):
        return False
    if _resolve_expression(node.bases[0], bindings) not in ROOT_API_CONSTRUCTORS:
        return False
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], ast.FunctionDef):
        return False
    if ast.dump(body[0], include_attributes=False) != _documented_method_dump():
        return False
    schema_name = ast.Name(id="OpenAPISchema", ctx=ast.Load())
    function_name = ast.Name(id="add_pre_route_responses", ctx=ast.Load())
    return (
        _resolve_expression(schema_name, bindings) == OPENAPI_SCHEMA_TYPE
        and _resolve_expression(schema_name, final) == OPENAPI_SCHEMA_TYPE
        and _resolve_expression(function_name, final) == PRE_ROUTE_FUNCTION
    )


@dataclass(frozen=True)
class _RootApi:
    relative_path: Path
    receivers: tuple[str, ...]  # 모듈.이름
    namespaces: tuple[str | None, ...]
    documented: bool


@dataclass(frozen=True)
class _PreRouteSite:
    kind: str  # 겹침 키 종류(override · monkeypatch · postprocess · f) — 그 밖은 ""
    relative_path: Path
    lineno: int
    msg: str
    symbol: str | None = None


def _api_namespace(call: ast.Call) -> str | None:
    """루트 API 의 URL 이름공간 — `urls_namespace=` 글자, 없으면 Ninja 기본 `api-<version>`(못 읽으면 None)."""
    keywords = {keyword.arg: keyword.value for keyword in call.keywords}
    if None in keywords:
        return None
    for name, default in (("urls_namespace", None), ("version", "1.0.0")):
        node = keywords.get(name)
        if node is None:
            if default is None:
                continue
            return f"api-{default}"
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            return None
        if node.value:
            return node.value if name == "urls_namespace" else f"api-{node.value}"
    return None


def _api_class_names(root: Path, files: list[Path]) -> dict[str, tuple[Path, ast.ClassDef]]:
    """프로젝트 안 루트 API 하위 클래스(모듈.이름 → 자리) — 다른 모듈의 하위 클래스까지 고정점으로 모은다."""
    classes: dict[str, tuple[Path, ast.ClassDef]] = {}
    while True:
        markers = {"NinjaAPI", "NinjaExtraAPI"} | {name.rsplit(".", 1)[-1] for name in classes}
        before_count = len(classes)
        for relative in files:
            source = _project_source(root, relative)
            if source is None or not any(marker in source for marker in markers):
                continue
            tree = _parse_project_file(root, relative)
            if tree is None or not any(isinstance(node, ast.ClassDef) and node.bases for node in tree.body):
                continue
            module = _module_name(relative)
            before = _module_symbol_bindings_before(ParsedSource(relative, "", tree))
            for statement in tree.body:
                if not isinstance(statement, ast.ClassDef):
                    continue
                bindings = before.get(id(statement), {})
                for base in statement.bases:
                    resolved = _resolve_expression(base, bindings)
                    if resolved in ROOT_API_CONSTRUCTORS or resolved in classes:
                        classes[f"{module}.{statement.name}"] = (relative, statement)
                        break
        if len(classes) == before_count:
            return classes


def _passthrough_subclass(node: ast.ClassDef) -> bool:
    """몸통이 `pass` · docstring · `...` 뿐인 하위 클래스(기저 하나 · 데코레이터 · 키워드 없음) — 문서는 상속으로 정해진다."""
    if node.decorator_list or node.keywords or len(node.bases) != 1 or getattr(node, "type_params", None):
        return False
    return all(
        isinstance(member, ast.Pass)
        or (isinstance(member, ast.Expr) and isinstance(member.value, ast.Constant)
            and (isinstance(member.value.value, str) or member.value.value is Ellipsis))
        for member in node.body
    )


def _root_api_site(kind: str, relative: Path, lineno: int, attribute: str = "get_openapi_schema") -> _PreRouteSite:
    if kind == "monkeypatch":
        message = (f"루트 API 의 `{attribute}` monkeypatch — OpenAPI 를 사후 변형하지 않는다"
                   f"(경로 앞 오류는 정해진 클래스가 붙인다 · {PRE_ROUTE_SECTION})")
    else:
        message = ("루트 API 의 `get_openapi_schema` 직접 호출 · 후처리 — 생성 문서를 사후 변형하지 않는다"
                   f"({PRE_ROUTE_SECTION})")
    return _PreRouteSite(kind, relative, lineno, message)


def _syntactic_root_sites(
    relative: Path,
    tree: ast.Module,
    local_receivers: set[str],
    final: dict[str, str],
    documented_nodes: set[int],
) -> list[_PreRouteSite]:
    """루트 API 이름(그 모듈이 지은 이름)에 대한 monkeypatch · setattr · 후처리 — 출처 판독이 흔들릴 때의 글자 꼴."""
    sites: list[_PreRouteSite] = []
    assigned_attributes: set[int] = set()
    for node in ast.walk(tree):
        for target in _attribute_assignment_targets(node) if isinstance(node, ast.stmt) else ():
            assigned_attributes.add(id(target))
            if (
                target.attr in {"get_openapi_schema", "openapi_schema"}
                and isinstance(target.value, ast.Name)
                and target.value.id in local_receivers
            ):
                sites.append(_root_api_site("monkeypatch", relative, target.lineno, target.attr))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "setattr"
            and "setattr" not in final
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in local_receivers
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in {"get_openapi_schema", "openapi_schema"}
        ):
            sites.append(_root_api_site("monkeypatch", relative, node.lineno, str(node.args[1].value)))
        elif (
            isinstance(node, ast.Attribute)
            and node.attr == "get_openapi_schema"
            and id(node) not in assigned_attributes
            and isinstance(node.value, ast.Name)
            and node.value.id in local_receivers
            and id(node) not in documented_nodes
        ):
            sites.append(_root_api_site("postprocess", relative, node.lineno))
    return sites


def _class_patch_sites(
    root: Path,
    files: list[Path],
    classes: dict[str, tuple[Path, ast.ClassDef]],
) -> list[_PreRouteSite]:
    """루트 API 클래스 · 기저(`NinjaAPI` · `NinjaExtraAPI`) 수준의 `get_openapi_schema` monkeypatch — 대입 · `setattr`."""
    patched_names = {"get_openapi_schema", "openapi_schema"}
    targets_of_interest = ROOT_API_CONSTRUCTORS | set(classes)
    sites: list[_PreRouteSite] = []
    for relative in files:
        source = _project_source(root, relative)
        if source is None or not any(name in source for name in patched_names):
            continue
        tree = _parse_project_file(root, relative)
        if tree is None:
            continue
        final = _final_module_symbol_bindings(ParsedSource(relative, "", tree))
        for node in ast.walk(tree):
            if isinstance(node, ast.stmt):
                for target in _attribute_assignment_targets(node):
                    if target.attr in patched_names and _resolve_expression(target.value, final) in targets_of_interest:
                        sites.append(_root_api_site("monkeypatch", relative, target.lineno, target.attr))
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "setattr"
                and "setattr" not in final
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value in patched_names
                and _resolve_expression(node.args[0], final) in targets_of_interest
            ):
                sites.append(_root_api_site("monkeypatch", relative, node.lineno, str(node.args[1].value)))
    return sites


def _root_api_lane(
    root: Path,
    files: list[Path],
) -> tuple[list[_RootApi], list[_PreRouteSite]]:
    """루트 API 레인(a) — 루트 API 를 짓는 모듈과 문서 재정의 · monkeypatch · 후처리.

    정해진 클래스인지는 그 클래스를 정의한 모듈에서 판정하고(다른 프로젝트 모듈에서 import 해 지어도 같다), 같은 모듈의
    생성은 그 문장 앞에 묶인 정의로 판정한다."""
    classes = _api_class_names(root, files)
    class_tails = {name.rsplit(".", 1)[-1] for name in classes}
    roots: list[_RootApi] = []
    sites: list[_PreRouteSite] = []
    markers = {"NinjaAPI", "NinjaExtraAPI"} | class_tails
    node_documented: dict[int, bool] = {}
    entries: list[tuple[Path, ast.ClassDef, dict[str, str]]] = []
    module_root_classes: dict[Path, list[ast.ClassDef]] = {}
    contexts: dict[Path, tuple[str, ast.Module]] = {}
    for relative in files:
        source = _project_source(root, relative)
        if source is None or not any(marker in source for marker in markers):
            continue
        tree = _parse_project_file(root, relative)
        if tree is None:
            continue
        contexts[relative] = (source, tree)
        before = _module_symbol_bindings_before(ParsedSource(relative, "", tree))
        final = _final_module_symbol_bindings(ParsedSource(relative, "", tree))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bindings = before.get(id(node), {})
            if not any(
                _resolve_expression(base, bindings) in ROOT_API_CONSTRUCTORS or _resolve_expression(base, bindings) in classes
                for base in node.bases
            ):
                continue
            module_root_classes.setdefault(relative, []).append(node)
            entries.append((relative, node, bindings))
            node_documented[id(node)] = _is_documented_api_class(node, bindings, final)
    # 정해진 클래스의 하위 클래스가 몸통 없이(pass · docstring) 물려받으면 문서는 상속으로 맞다 — 고정점까지.
    changed = True
    while changed:
        changed = False
        documented_names = {name for name, (_, node) in classes.items() if node_documented.get(id(node))}
        for relative, node, bindings in entries:
            if (
                not node_documented[id(node)]
                and _passthrough_subclass(node)
                and _resolve_expression(node.bases[0], bindings) in documented_names
            ):
                node_documented[id(node)] = changed = True
    for relative, node, bindings in entries:
        if node_documented[id(node)]:
            continue
        for member in node.body:
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == "get_openapi_schema":
                sites.append(
                    _PreRouteSite(
                        "override",
                        relative,
                        member.lineno,
                        f"루트 API 클래스 `{node.name}` 의 `get_openapi_schema` 재정의가 정해진 꼴이 아니다 — "
                        "문서 재정의는 서명 · 몸통 글자 그대로의 그 클래스 하나뿐이다"
                        f"({PRE_ROUTE_SECTION})",
                        member.name,
                    )
                )
    class_documented: dict[str, bool] = {name: node_documented.get(id(node), False) for name, (_, node) in classes.items()}
    class_sites = _class_patch_sites(root, files, classes)
    sites.extend(class_sites)
    for relative, (source, tree) in contexts.items():
        parsed = ParsedSource(relative, "", tree)
        module = _module_name(relative)
        before = _module_symbol_bindings_before(parsed)
        final = _final_module_symbol_bindings(parsed)
        documented_nodes: set[int] = set()
        for node in module_root_classes.get(relative, []):
            if node_documented.get(id(node)):
                documented_nodes.update(id(child) for child in ast.walk(node.body[-1]))
        receivers: list[str] = []
        namespaces: list[str | None] = []
        bound_documented: list[bool] = []
        for statement in _module_statements(tree.body):
            targets, value = _assigned_value(statement)
            if not isinstance(value, ast.Call):
                continue
            constructor = _resolve_expression(value.func, before.get(id(statement), final))
            if constructor not in ROOT_API_CONSTRUCTORS and constructor not in classes:
                continue
            constructor_module, _, constructor_name = (constructor or "").rpartition(".")
            if constructor in ROOT_API_CONSTRUCTORS:
                bound_documented.append(False)
            elif constructor_module == module:
                bound = [
                    node
                    for node in module_root_classes.get(relative, [])
                    if node.name == constructor_name and node.lineno < statement.lineno
                ]
                bound_documented.append(bool(bound) and node_documented.get(id(bound[-1]), False))
            else:
                bound_documented.append(class_documented.get(constructor or "", False))
            for target in targets:
                for name in sorted(_target_names(target)):
                    receivers.append(f"{module}.{name}")
            namespaces.append(_api_namespace(value))
        if not bound_documented:
            continue
        try:
            # 고른 API 모듈과 같은 출처 판독(재대입 · 닿지 않는 갈래 · 가린 setattr) — 판독이 흔들리면 글자 꼴로 본다.
            module_findings, _ = _api_module_findings(ParsedSource(relative, source, tree))
            local_sites = [
                _root_api_site(
                    "monkeypatch" if finding.category == "openapi-monkeypatch" else "postprocess", relative, finding.lineno
                )
                for finding in module_findings
                if finding.category in {"openapi-monkeypatch", "openapi-postprocess"}
            ]
        except UsageError:
            local_sites = _syntactic_root_sites(
                relative, tree, {receiver.rsplit(".", 1)[-1] for receiver in receivers}, final, documented_nodes
            )
        known = {(site.kind, site.relative_path, site.lineno) for site in sites}
        sites.extend(site for site in local_sites if (site.kind, site.relative_path, site.lineno) not in known)
        own = module_root_classes.get(relative, [])
        documented = (
            all(bound_documented)
            and len(own) <= 1
            and all(node_documented.get(id(node), False) for node in own)
            and not any(site.relative_path == relative for site in sites)
        )
        roots.append(_RootApi(relative, tuple(receivers), tuple(namespaces), documented))
    sites.sort(key=lambda site: (site.relative_path.as_posix(), site.lineno, site.msg))
    return roots, sites


@dataclass(frozen=True)
class _CanonicalSpec:
    forms: tuple[tuple[frozenset[str], tuple[str, ...]], ...]
    names: tuple[tuple[str, ...], ...]
    row_required: frozenset[str]
    row_optional: frozenset[str]
    bad_request_required: frozenset[str]
    bad_request_optional: frozenset[str]
    http_methods: frozenset[str]
    operation_key: re.Pattern[str]


_SPEC: "list[_CanonicalSpec]" = []


def _statement_name(statement: ast.stmt) -> str:
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return statement.name
    type_alias = getattr(ast, "TypeAlias", None)
    if type_alias is not None and isinstance(statement, type_alias):
        return statement.name.id
    targets, _ = _assigned_value(statement)
    names = sorted(name for target in targets for name in _target_names(target))
    return names[0] if names else type(statement).__name__


def _canonical_form(tree: ast.Module) -> tuple[frozenset[str], tuple[str, ...], tuple[str, ...]]:
    """AST 대조 꼴 — import 는 집합(`__future__` 뺌) · 그 밖 문장은 차례대로(모듈 docstring 뺌)."""
    imports: set[str] = set()
    definitions: list[str] = []
    names: list[str] = []
    for index, statement in enumerate(tree.body):
        if (
            index == 0
            and isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            continue
        if isinstance(statement, ast.Import):
            imports.update(f"import {alias.name} as {alias.asname}" for alias in statement.names)
        elif isinstance(statement, ast.ImportFrom):
            if statement.level == 0 and statement.module == "__future__":
                continue
            module = "." * statement.level + (statement.module or "")
            imports.update(f"from {module} import {alias.name} as {alias.asname}" for alias in statement.names)
        else:
            definitions.append(ast.dump(statement, include_attributes=False))
            names.append(_statement_name(statement))
    return frozenset(imports), tuple(definitions), tuple(names)


def _asset_constant(tree: ast.Module, name: str) -> ast.expr | None:
    for statement in tree.body:
        targets, value = _assigned_value(statement)
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return value
    return None


def _typed_dict_keys(tree: ast.Module, name: str) -> tuple[frozenset[str], frozenset[str]]:
    for statement in tree.body:
        if isinstance(statement, ast.ClassDef) and statement.name == name:
            required: set[str] = set()
            optional: set[str] = set()
            for member in statement.body:
                if isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                    annotation = member.annotation
                    is_optional = (
                        isinstance(annotation, ast.Subscript)
                        and isinstance(annotation.value, ast.Name)
                        and annotation.value.id == "NotRequired"
                    )
                    (optional if is_optional else required).add(member.target.id)
            return frozenset(required), frozenset(optional)
    raise UsageError(f"정본 자산 분석 불능: `{name}` TypedDict 를 찾지 못했다")


def _canonical_spec() -> _CanonicalSpec:
    """이 검사기 옆 정본 자산 — 받는 꼴 · 표 칸 이름 · 메서드 낱말 · operation 꼴의 단일 출처."""
    if _SPEC:
        return _SPEC[0]
    forms: list[tuple[frozenset[str], tuple[str, ...]]] = []
    names: list[tuple[str, ...]] = []
    current: ast.Module | None = None
    for asset in PRE_ROUTE_CANONICAL_ASSETS:
        path = Path(__file__).resolve().with_name(asset)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=asset)
        except (OSError, UnicodeError, SyntaxError) as exc:
            raise UsageError(f"정본 자산 분석 불능: {asset} ({exc}) — 검사기와 같은 폴더에 있어야 한다") from exc
        imports, definitions, definition_names = _canonical_form(tree)
        forms.append((imports, definitions))
        names.append(definition_names)
        if current is None:
            current = tree
    assert current is not None
    row_required, row_optional = _typed_dict_keys(current, "PreRouteResponse")
    bad_required, bad_optional = _typed_dict_keys(current, "BadRequestResponse")
    methods_node = _asset_constant(current, "HTTP_METHODS")
    methods = frozenset(
        node.value
        for node in (ast.walk(methods_node) if methods_node is not None else ())
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    key_node = _asset_constant(current, "OPERATION_KEY")
    pattern: str | None = None
    if isinstance(key_node, ast.Call) and key_node.args and isinstance(key_node.args[0], ast.Constant):
        pattern = key_node.args[0].value if isinstance(key_node.args[0].value, str) else None
    if not methods or pattern is None:
        raise UsageError("정본 자산 분석 불능: HTTP_METHODS · OPERATION_KEY 를 읽지 못했다")
    spec = _CanonicalSpec(
        tuple(forms),
        tuple(names),
        row_required,
        row_optional,
        bad_required,
        bad_optional,
        methods,
        re.compile(pattern),
    )
    _SPEC.append(spec)
    return spec


def _canonical_findings(relative: Path, tree: ast.Module) -> list[_PreRouteSite]:
    """b — 프로젝트 정본 파일 ↔ 받는 정본(자산)의 AST 대조."""
    spec = _canonical_spec()
    imports, definitions, names = _canonical_form(tree)
    if (imports, definitions) in spec.forms:
        return []
    want_imports, want_definitions = spec.forms[0]
    want_names = spec.names[0]
    detail: list[str] = []
    if imports != want_imports:
        missing = sorted(want_imports - imports)
        extra = sorted(imports - want_imports)
        if missing:
            detail.append(f"빠진 import {len(missing)}")
        if extra:
            detail.append(f"더한 import {len(extra)}")
    if definitions != want_definitions:
        differing = next(
            (
                index
                for index in range(max(len(definitions), len(want_definitions)))
                if index >= len(definitions)
                or index >= len(want_definitions)
                or definitions[index] != want_definitions[index]
            ),
            None,
        )
        if differing is not None:
            shown = names[differing] if differing < len(names) else want_names[differing]
            detail.append(f"{differing + 1}번째 정의(`{shown}`)부터 다름")
    lineno = 1
    return [
        _PreRouteSite(
            "",
            relative,
            lineno,
            f"경로 앞 응답 정본이 플러그인 정본과 글자 그대로가 아니다({' · '.join(detail) or '꼴 다름'}) — "
            f"정본은 고치지 않는다 · 참조 글의 정본 코드를 글자 그대로 둔다({PRE_ROUTE_SECTION})",
        )
    ]


@dataclass(frozen=True)
class _TableRow:
    lineno: int
    status: int | None
    headers: frozenset[str]  # 소문자
    narrowing: frozenset[str] = frozenset()  # 단 좁힘 칸(operations · methods · namespaces · exempt · `all` 밖 when)
    namespaces: tuple[str, ...] = ()


@dataclass(frozen=True)
class _ProjectSettings:
    middleware: tuple[tuple[str, Path, int], ...]  # (점 경로, settings 파일, 행)
    names: frozenset[str]  # 모든 settings 진입 모듈의 `*` import 닫힘에 있는 이름(exempt 대조)
    root_urlconfs: frozenset[str]
    found: bool
    unread: tuple[tuple[Path, int], ...] = ()  # `MIDDLEWARE` 값에서 글자로 풀지 못한 조각의 자리
    urlconf_unread: bool = False  # `ROOT_URLCONF` 를 글자 아닌 값으로 대입했다


def _string_constants(
    node: ast.AST,
    constants: "dict[str, list[ast.expr]] | None" = None,
    unread: "list[ast.AST] | None" = None,
    _seen: "frozenset[str]" = frozenset(),
) -> list[str]:
    """글자 · 목록 · `+` · 별표 펼침 · settings 목록 상수 이름(`constants`)을 글자로 푼다 — 못 푼 조각은 `unread` 에."""
    out: list[str] = []
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value)
    elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        for element in node.elts:
            out.extend(_string_constants(element, constants, unread, _seen))
    elif isinstance(node, ast.Starred):
        out.extend(_string_constants(node.value, constants, unread, _seen))
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        out.extend(_string_constants(node.left, constants, unread, _seen))
        out.extend(_string_constants(node.right, constants, unread, _seen))
    elif isinstance(node, ast.Name) and constants is not None and node.id in constants and node.id not in _seen:
        for value in constants[node.id]:
            out.extend(_string_constants(value, constants, unread, _seen | {node.id}))
    elif unread is not None:
        unread.append(node)
    return out


def _star_import_targets(relative: Path, tree: ast.Module) -> set[str]:
    """그 모듈이 `from X import *` 하는 모듈 이름(상대 import 는 그 파일 패키지 기준)."""
    package = _module_name(relative).split(".")
    if relative.name != "__init__.py":
        package = package[:-1]
    targets: set[str] = set()
    for statement in _module_statements(tree.body):
        if not (isinstance(statement, ast.ImportFrom) and any(alias.name == "*" for alias in statement.names)):
            continue
        if statement.level:
            anchor = package[: len(package) - (statement.level - 1)] if statement.level > 1 else package
            targets.add(".".join([*anchor, *([statement.module] if statement.module else [])]))
        elif statement.module:
            targets.add(statement.module)
    return targets


def _project_settings(root: Path, files: list[Path]) -> _ProjectSettings:
    """settings 모든 모듈의 합 — `MIDDLEWARE`(대입 · `+=` · `append` · `insert` · `extend` · 목록 상수 이름 · 별표 펼침) ·
    이름(뿌리 settings 의 것 — exempt 대조) · ROOT_URLCONF."""
    middleware: list[tuple[str, Path, int]] = []
    module_names: dict[str, set[str]] = {}
    star_of: dict[str, set[str]] = {}
    star_targets: set[str] = set()
    urlconf_unread = False
    urlconfs: set[str] = set()
    constants: dict[str, list[ast.expr]] = {}
    trees: list[tuple[Path, ast.Module]] = []
    unread: list[tuple[Path, int]] = []
    for relative in files:
        if relative.parts[:1] == ("application",) or not (
            relative.name == "settings.py" or relative.parent.name == "settings"
        ):
            continue
        tree = _parse_project_file(root, relative)
        if tree is None:
            continue
        trees.append((relative, tree))
        names = module_names.setdefault(_module_name(relative), set())
        stars = _star_import_targets(relative, tree)
        star_of[_module_name(relative)] = stars
        star_targets.update(stars)
        for statement in _module_statements(tree.body):
            targets, value = _assigned_value(statement)
            for target in targets:
                names.update(_target_names(target))
            if isinstance(statement, ast.AugAssign):
                names.update(_target_names(statement.target))
            target_names = {name for target in targets for name in _target_names(target)}
            if "ROOT_URLCONF" in target_names:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    urlconfs.add(value.value)
                else:
                    urlconf_unread = True
            if (
                value is not None
                and len(targets) == 1
                and isinstance(targets[0], ast.Name)
                and targets[0].id != "MIDDLEWARE"
                and isinstance(value, (ast.List, ast.Tuple, ast.BinOp, ast.Name))
            ):
                constants.setdefault(targets[0].id, []).append(value)
    for relative, tree in trees:
        for node in ast.walk(tree):
            values: list[ast.AST] = []
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets, value = _assigned_value(node)
                if value is not None and any(isinstance(t, ast.Name) and t.id == "MIDDLEWARE" for t in targets):
                    values.append(value)
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "MIDDLEWARE":
                    values.append(node.value)
            elif isinstance(node, ast.Call):
                func = node.func
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr in {"append", "insert", "extend"}
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "MIDDLEWARE"
                ):
                    values.extend(node.args[1:] if func.attr == "insert" else node.args)
            for value in values:
                missed: list[ast.AST] = []
                for entry in _string_constants(value, constants, missed):
                    middleware.append((entry, relative, getattr(node, "lineno", 1)))
                unread.extend((relative, getattr(piece, "lineno", getattr(node, "lineno", 1))) for piece in missed)
    # exempt 대조 이름 = settings 진입 모듈(다른 settings 가 `*` import 하지 않는 모듈 — 이름도 `*` import 도 없는 빈 모듈은
    # 뺀다)마다 그 `*` import 닫힘 안의 이름 — 모든 진입에 있는 이름만(진입이 하나면 그 모듈 닫힘).
    def closure(module: str) -> set[str]:
        seen: set[str] = set()
        stack = [module]
        while stack:
            current = stack.pop()
            if current in seen or current not in module_names:
                continue
            seen.add(current)
            stack.extend(star_of.get(current, set()))
        return seen

    entries = [
        module
        for module in module_names
        if module not in star_targets and (module_names[module] or star_of.get(module))
    ]
    entry_names = [set().union(*(module_names[member] for member in closure(module))) for module in entries]
    root_names = set.intersection(*entry_names) if entry_names else set().union(*module_names.values()) if module_names else set()
    return _ProjectSettings(
        tuple(middleware),
        frozenset(root_names),
        frozenset(urlconfs),
        bool(trees),
        tuple(dict.fromkeys(unread)),
        urlconf_unread,
    )


HANDLER400_HTML_CALLS: frozenset[str] = frozenset(
    {
        "django.shortcuts.render",
        "django.template.response.TemplateResponse",
        "django.views.defaults.bad_request",
        "django.http.HttpResponseBadRequest",
        "django.http.response.HttpResponseBadRequest",
    }
)


def _handler400_kind(root: Path, dotted: str | None) -> str | None:
    """처리기 점 경로 → "json" · "html" · "other" · 못 읽으면 None."""
    if dotted == "django.views.defaults.bad_request":
        return "html"
    module, _, name = (dotted or "").rpartition(".")
    view_relative = _module_path(root, module) if module else None
    view_tree = _parse_project_file(root, view_relative) if view_relative is not None else None
    function = next(
        (
            node
            for node in (view_tree.body if view_tree is not None else [])
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        ),
        None,
    )
    if function is None or view_relative is None or view_tree is None:
        return None
    view_bindings = _final_module_symbol_bindings(ParsedSource(view_relative, "", view_tree))
    kinds: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        resolved = _resolve_expression(node.func, view_bindings)
        if resolved in {"django.http.JsonResponse", "django.http.response.JsonResponse"}:
            kinds.add("json")
        elif resolved in HANDLER400_HTML_CALLS:
            content_type = next((k.value for k in node.keywords if k.arg == "content_type"), None)
            if content_type is None:
                kinds.add("html")
            elif isinstance(content_type, ast.Constant) and isinstance(content_type.value, str):
                kinds.add("json" if "json" in content_type.value.lower() else "html")
            else:
                kinds.add("other")
    if "json" in kinds:
        return "json"
    return "html" if kinds == {"html"} else "other"


def _handler400_view(root: Path, settings: _ProjectSettings) -> tuple[bool | None, str | None]:
    """루트 URLconf 의 `handler400` → (있음 — 루트 URLconf 를 못 읽으면 None, 그 처리기가 만드는 꼴 — "json"(JsonResponse 를
    만든다 · `content_type=` 이 JSON) · "html"(HTML 만 그린다 · Django 기본 처리기) · "other"(읽었지만 가르지 못함) · 못 읽으면
    None). `from … import … as handler400` 도 읽는다."""
    if not settings.root_urlconfs or settings.urlconf_unread:
        return None, None
    for urlconf in sorted(settings.root_urlconfs):
        relative = _module_path(root, urlconf)
        tree = _parse_project_file(root, relative) if relative is not None else None
        if tree is None or relative is None:
            return None, None
        bindings = _final_module_symbol_bindings(ParsedSource(relative, "", tree))
        for statement in _module_statements(tree.body):
            if isinstance(statement, ast.ImportFrom):
                for alias in statement.names:
                    if (alias.asname or alias.name) == "handler400" and statement.module and not statement.level:
                        return True, _handler400_kind(root, f"{statement.module}.{alias.name}")
                continue
            targets, value = _assigned_value(statement)
            if not any("handler400" in _target_names(target) for target in targets):
                continue
            dotted: str | None = None
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                dotted = value.value
            elif value is not None:
                dotted = _resolve_expression(value, bindings)
            return True, _handler400_kind(root, dotted)
    return False, None


def _literal_value(node: ast.AST) -> object:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return _NO_STATIC_VALUE


def _string_tuple(node: ast.AST) -> tuple[str, ...] | None:
    if not isinstance(node, ast.Tuple):
        return None
    values: list[str] = []
    for element in node.elts:
        if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
            return None
        values.append(element.value)
    return tuple(values)


def _table_row_problems(
    row: ast.Dict,
    spec: _CanonicalSpec,
    schemas: set[str],
    namespaces: set[str],
    settings: _ProjectSettings,
) -> tuple[list[str], _TableRow]:
    problems: list[str] = []
    values: dict[str, ast.AST] = {}
    for key, value in zip(row.keys, row.values):
        if key is None:
            problems.append("`**` 펼침")
            continue
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            problems.append("칸 이름이 글자가 아니다")
            continue
        if key.value in values:
            problems.append(f"칸 `{key.value}` 가 두 번")
        values[key.value] = value
    allowed = spec.row_required | spec.row_optional
    for name in sorted(set(values) - allowed):
        problems.append(f"모르는 칸 `{name}`")
    for name in sorted(spec.row_required - set(values)):
        problems.append(f"필수 칸 `{name}` 없음")
    status: int | None = None
    if "status" in values:
        status = _int_status_key(values["status"])
        if status is None:
            problems.append("`status` 가 정수 글자가 아니다")
        elif not 400 <= status <= 599:
            problems.append(f"`status` {status} — 400–599 밖")
    if "when" in values:
        when = values["when"]
        if not (isinstance(when, ast.Constant) and isinstance(when.value, str) and when.value in PROJECT_ROW_WHEN):
            problems.append(f"`when` 은 {' · '.join(sorted(PROJECT_ROW_WHEN))} 가운데 하나")
    for name in ("description", "media_type"):
        if name in values and not (
            isinstance(values[name], ast.Constant) and isinstance(values[name].value, str)
        ):
            problems.append(f"`{name}` 가 글자가 아니다")
    if "body" in values:
        body = values["body"]
        if not (isinstance(body, ast.Name) and body.id in schemas):
            problems.append("`body` 는 같은 파일 Schema 이름")
    narrowing: dict[str, tuple[str, ...]] = {}
    for name in ("methods", "namespaces", "operations"):
        if name not in values:
            continue
        items = _string_tuple(values[name])
        if items is None:
            problems.append(f"`{name}` 가 글자 튜플이 아니다")
            continue
        if not items:
            problems.append(f"`{name}` 빈 튜플")
        narrowing[name] = items
    for method in narrowing.get("methods", ()):
        if method not in spec.http_methods:
            problems.append(f"`methods` 의 `{method}` — 대문자 HTTP 메서드만")
    for namespace in narrowing.get("namespaces", ()):
        if namespace not in namespaces:
            shown = " · ".join(sorted(namespaces)) or "없음"
            problems.append(f"`namespaces` 의 `{namespace}` 가 루트 API `urls_namespace=` 글자 안이 아니다(있는 것: {shown})")
    if "operations" in values:
        for target in narrowing.get("operations", ()):
            if spec.operation_key.fullmatch(target) is None:
                problems.append(f"`operations` 의 `{target}` — `METHOD /경로` 꼴")
        if len(narrowing.get("namespaces", ())) != 1:
            problems.append("`operations` 행은 `namespaces` 하나가 필수")
    if "exempt" in values:
        exempt = values["exempt"]
        shape = (
            isinstance(exempt, ast.Tuple)
            and len(exempt.elts) == 2
            and isinstance(exempt.elts[0], ast.Constant)
            and (exempt.elts[0].value is None or exempt.elts[0].value in spec.http_methods)
            and isinstance(exempt.elts[1], ast.Constant)
            and isinstance(exempt.elts[1].value, str)
        )
        if not shape:
            problems.append("`exempt` 는 `(메서드 | None, \"<settings 이름>\")` 글자 튜플")
        elif settings.found and exempt.elts[1].value not in settings.names:
            problems.append(
                f"`exempt` 의 settings 이름 `{exempt.elts[1].value}` 가 settings 에 없다"
                "(목록은 모든 settings 진입 모듈이 `*` import 로 받는 base settings 에 둔다)"
            )
    headers: set[str] = set()
    if "headers" in values:
        header_node = values["headers"]
        if not isinstance(header_node, ast.Dict) or _literal_value(header_node) is _NO_STATIC_VALUE:
            problems.append("`headers` 가 글자 Dict 가 아니다")
        else:
            for key in header_node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    headers.add(key.value.lower())
                else:
                    problems.append("`headers` 의 머리 이름이 글자가 아니다")
    for name, value in values.items():
        if name in {"body", "headers"} or name not in allowed:
            continue
        if _literal_value(value) is _NO_STATIC_VALUE:
            problems.append(f"`{name}` 가 글자 값이 아니다")
    present = frozenset(name for name in ("operations", "methods", "namespaces", "exempt") if name in values) | (
        frozenset({"when"})
        if "when" in values and not (isinstance(values["when"], ast.Constant) and values["when"].value == "all")
        else frozenset()
    )
    return problems, _TableRow(row.lineno, status, frozenset(headers), present, narrowing.get("namespaces", ()))


def _table_findings(
    relative: Path,
    tree: ast.Module,
    namespaces: set[str],
    settings: _ProjectSettings,
    handler400: tuple[bool | None, str | None],
) -> tuple[list[_PreRouteSite], list[_TableRow], frozenset[str], list[tuple[_PreRouteSite, str]]]:
    """b — 표 파일 정적 검증(글자 값 · 닫힌 칸 · 값) → (위반, 행, `NOT_API_MIDDLEWARE`, ⓓ 후보)."""
    spec = _canonical_spec()
    sites: list[_PreRouteSite] = []
    candidates: list[tuple[_PreRouteSite, str]] = []
    schemas: set[str] = {statement.name for statement in tree.body if isinstance(statement, ast.ClassDef)}
    assigned: dict[str, tuple[ast.stmt, ast.expr]] = {}

    def add(lineno: int, message: str) -> None:
        sites.append(_PreRouteSite("", relative, lineno, f"경로 앞 응답 표 — {message}({PRE_ROUTE_SECTION})"))

    for index, statement in enumerate(tree.body):
        if isinstance(statement, (ast.Import, ast.ImportFrom, ast.ClassDef)):
            continue
        if (
            index == 0
            and isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            continue
        targets, value = _assigned_value(statement)
        names = {name for target in targets for name in _target_names(target)}
        if (
            value is not None
            and len(targets) == 1
            and isinstance(targets[0], ast.Name)
            and targets[0].id in PRE_ROUTE_TABLE_NAMES
        ):
            if targets[0].id in assigned:
                add(statement.lineno, f"`{targets[0].id}` 를 두 번 대입했다 — 한 번 글자 값으로 둔다")
            assigned[targets[0].id] = (statement, value)
            continue
        shown = ", ".join(f"`{name}`" for name in sorted(names)) or f"`{type(statement).__name__}` 문장"
        add(
            statement.lineno,
            f"{shown} — 표 파일에는 몸통 Schema 와 `PRE_ROUTE_RESPONSES` · `BAD_REQUEST_RESPONSE` · "
            "`NOT_API_MIDDLEWARE` 글자 값만 둔다",
        )
    for name in PRE_ROUTE_TABLE_NAMES:
        if name not in assigned:
            add(1, f"`{name}` 이 없다")
    rows: list[_TableRow] = []
    if "PRE_ROUTE_RESPONSES" in assigned:
        statement, value = assigned["PRE_ROUTE_RESPONSES"]
        if not isinstance(value, ast.Tuple):
            add(statement.lineno, "`PRE_ROUTE_RESPONSES` 는 행 Dict 의 글자 튜플")
        else:
            for element in value.elts:
                if not isinstance(element, ast.Dict):
                    add(getattr(element, "lineno", statement.lineno), "행이 글자 Dict 가 아니다")
                    continue
                problems, row = _table_row_problems(element, spec, schemas, namespaces, settings)
                rows.append(row)
                if problems:
                    add(element.lineno, "행: " + " · ".join(problems))
    if "BAD_REQUEST_RESPONSE" in assigned:
        statement, value = assigned["BAD_REQUEST_RESPONSE"]
        problems: list[str] = []
        keys: dict[str, ast.AST] = {}
        if not isinstance(value, ast.Dict):
            problems.append("글자 Dict 가 아니다")
        else:
            for key, item in zip(value.keys, value.values):
                if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                    problems.append("칸 이름이 글자가 아니다")
                    continue
                keys[key.value] = item
            allowed = spec.bad_request_required | spec.bad_request_optional
            problems.extend(f"모르는 칸 `{name}`" for name in sorted(set(keys) - allowed))
            problems.extend(f"필수 칸 `{name}` 없음" for name in sorted(spec.bad_request_required - set(keys)))
            if "media_type" in keys and not (
                isinstance(keys["media_type"], ast.Constant) and isinstance(keys["media_type"].value, str)
            ):
                problems.append("`media_type` 이 글자가 아니다")
            if "body" in keys and not (isinstance(keys["body"], ast.Name) and keys["body"].id in schemas):
                problems.append("`body` 는 같은 파일 Schema 이름")
            default = _literal_value(value) == DEFAULT_BAD_REQUEST
            if not default and handler400[0] is False:
                problems.append(
                    "기본값(`text/html`)이 아닌데 루트 URLconf 에 `handler400` 이 없다 — Django 기본 처리기는 상한 400 을 "
                    "HTML 로 그리므로 기본값으로 적거나 그 꼴로 그리는 `handler400` 을 둔다"
                )
            elif not default and handler400[1] == "html":
                problems.append("기본값(`text/html`)이 아닌데 루트 URLconf 의 `handler400` 이 HTML 로 그린다 — 기본값으로 적는다")
            elif not default and handler400[1] != "json":
                candidates.append(
                    (
                        _PreRouteSite(
                            "",
                            relative,
                            statement.lineno,
                            "`BAD_REQUEST_RESPONSE` 이 기본값이 아닌데 루트 URLconf 의 `handler400` 이 그리는 꼴을 가르지 못했다",
                        ),
                        "그 처리기가 그리는 Django 상한 400 의 꼴이 표에 적은 꼴인가",
                    )
                )
            if handler400[0] is True and default:
                if handler400[1] == "json":
                    problems.append(
                        "루트 URLconf 의 `handler400` 이 JSON 으로 답한다 — Django 상한 400 을 그 처리기가 그리므로 "
                        "기본값(`text/html`)이 아니라 그 꼴로 적는다"
                    )
                else:
                    candidates.append(
                        (
                            _PreRouteSite(
                                "",
                                relative,
                                statement.lineno,
                                "`BAD_REQUEST_RESPONSE` 이 기본값(`text/html`)인데 루트 URLconf 에 `handler400` 이 있다",
                            ),
                            "그 처리기가 그리는 Django 상한 400 의 꼴이 `text/html` 인가(JSON 이면 그 꼴로 적는다)",
                        )
                    )
        if problems:
            add(statement.lineno, "`BAD_REQUEST_RESPONSE`: " + " · ".join(problems))
    not_api: frozenset[str] = frozenset()
    if "NOT_API_MIDDLEWARE" in assigned:
        statement, value = assigned["NOT_API_MIDDLEWARE"]
        items = _string_tuple(value)
        if items is None or any(DOTTED_PATH_RE.fullmatch(item) is None for item in items):
            add(statement.lineno, "`NOT_API_MIDDLEWARE` 는 미들웨어 점 경로 글자 튜플")
        else:
            not_api = frozenset(items)
    return sites, rows, not_api, candidates


@dataclass
class _MiddlewareAnswer:
    lineno: int
    status: int
    headers: set[str]


def _middleware_status(node: ast.AST | None, bindings: dict[str, str]) -> int | None:
    if node is None:
        return None
    if isinstance(node, ast.Attribute) and node.attr == "value":
        node = node.value
    return _status_from_expression(node, bindings)


def _response_call_status(call: ast.Call, resolved: str, bindings: dict[str, str]) -> tuple[bool, int | None]:
    """응답 생성 호출의 status → (읽음, 값). `status` 가 없으면 200."""
    if resolved in MIDDLEWARE_FIXED_STATUS:
        return True, MIDDLEWARE_FIXED_STATUS[resolved]
    status_node: ast.AST | None = next((k.value for k in call.keywords if k.arg == "status"), None)
    position = MIDDLEWARE_RESPONSE_CALLS[resolved]
    if status_node is None and position is not None and len(call.args) > position:
        status_node = call.args[position]
    if status_node is None:
        if any(k.arg is None for k in call.keywords) or any(isinstance(a, ast.Starred) for a in call.args):
            return False, None
        return True, 200
    status = _middleware_status(status_node, bindings)
    return status is not None, status


def _middleware_answers(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, str],
) -> tuple[list[_MiddlewareAnswer], list[tuple[int, str]]]:
    """미들웨어 자리 한 곳이 직접 내는 답 · 싣는 글자 머리 — 읽지 못한 꼴은 (행, 까닭)."""
    answers: list[_MiddlewareAnswer] = []
    unread: list[tuple[int, str]] = []
    tracked: dict[str, _MiddlewareAnswer] = {}
    assigned_to: dict[int, str] = {}
    for node in ast.walk(function):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets, value = _assigned_value(node)
            if isinstance(value, ast.Call) and len(targets) == 1 and isinstance(targets[0], ast.Name):
                assigned_to[id(value)] = targets[0].id
    nodes = sorted(
        (node for node in ast.walk(function) if hasattr(node, "lineno") and node is not function),
        key=lambda node: (node.lineno, node.col_offset),
    )
    for node in nodes:
        if isinstance(node, ast.Call):
            resolved = _resolve_expression(node.func, bindings)
            if resolved not in MIDDLEWARE_RESPONSE_CALLS and resolved not in MIDDLEWARE_FIXED_STATUS:
                continue
            readable, status = _response_call_status(node, resolved, bindings)
            if not readable or status is None:
                unread.append((node.lineno, f"`{resolved.rsplit('.', 1)[-1]}` 의 status 를 글자로 읽지 못했다"))
                continue
            answer = _MiddlewareAnswer(node.lineno, status, set())
            header_node = next((k.value for k in node.keywords if k.arg == "headers"), None)
            if header_node is not None:
                if isinstance(header_node, ast.Dict) and all(
                    isinstance(key, ast.Constant) and isinstance(key.value, str) for key in header_node.keys
                ):
                    answer.headers.update(key.value.lower() for key in header_node.keys)
                else:
                    unread.append((node.lineno, "응답 `headers=` 머리 이름을 글자로 읽지 못했다"))
            answers.append(answer)
            if id(node) in assigned_to:
                tracked[assigned_to[id(node)]] = answer
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets, value = _assigned_value(node)
            for target in targets:
                if isinstance(target, ast.Name):
                    tracked.pop(target.id, None)  # 다시 묶임 — 응답 생성이면 그 호출이 곧 다시 잇는다
                elif isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                    owner = tracked.get(target.value.id)
                    if owner is None:
                        continue  # 지나가는 응답(get_response 결과 등)에 붙인 머리 — 이 미들웨어의 답이 아니다
                    name = _static_string(target.slice, bindings)
                    if name is None:
                        unread.append((node.lineno, "답에 싣는 머리 이름을 글자로 읽지 못했다"))
                    else:
                        owner.headers.add(name.lower())
                elif isinstance(target, ast.Attribute) and target.attr == "status_code":
                    status = _middleware_status(value, bindings)
                    if status is None:
                        unread.append((node.lineno, "`status_code` 값을 글자로 읽지 못했다"))
                        continue
                    owner = tracked.get(target.value.id) if isinstance(target.value, ast.Name) else None
                    if owner is not None:
                        owner.status = status
                        owner.lineno = node.lineno
                    else:
                        answers.append(_MiddlewareAnswer(node.lineno, status, set()))
        elif isinstance(node, ast.Raise) and node.exc is not None:
            raised = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            status = MIDDLEWARE_RAISED_STATUS.get(_resolve_expression(raised, bindings) or "")
            if status is not None:
                answers.append(_MiddlewareAnswer(node.lineno, status, set()))
    return answers, unread


MIDDLEWARE_PASSING_CALLS: frozenset[str] = frozenset(
    f"{module}.{name}"
    for module, names in (
        ("django.shortcuts", ("redirect",)),
        ("django.http", ("HttpResponseRedirect", "HttpResponsePermanentRedirect", "HttpResponseNotModified")),
        ("django.http.response", ("HttpResponseRedirect", "HttpResponsePermanentRedirect", "HttpResponseNotModified")),
    )
    for name in names
)  # 오류 답이 아닌 응답 생성(3xx) — hook 이 돌려줘도 d 몫이 아니다


@dataclass(frozen=True)
class _MiddlewareCode:
    relative: Path
    tree: ast.Module
    bindings: dict[str, str]


def _top_level_definition(tree: ast.Module | None, name: str) -> ast.stmt | None:
    return next(
        (
            statement
            for statement in (tree.body if tree is not None else [])
            if isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and statement.name == name
        ),
        None,
    )


def _middleware_code(root: Path, relative: Path, tree: ast.Module) -> _MiddlewareCode:
    return _MiddlewareCode(relative, tree, _final_module_symbol_bindings(ParsedSource(relative, "", tree)))


def _project_base_classes(
    root: Path, code: _MiddlewareCode, cls: ast.ClassDef
) -> list[tuple[_MiddlewareCode, ast.ClassDef]]:
    """프로젝트 안 기저 클래스(MRO 한 단계 — 같은 모듈 · 프로젝트 모듈)."""
    out: list[tuple[_MiddlewareCode, ast.ClassDef]] = []
    for base in cls.bases:
        resolved = _resolve_expression(base, code.bindings)
        module, _, name = (resolved or "").rpartition(".")
        if not module:
            continue
        if module == _module_name(code.relative):
            base_code: _MiddlewareCode | None = code
        else:
            base_relative = _module_path(root, module)
            base_tree = _parse_project_file(root, base_relative) if base_relative is not None else None
            base_code = _middleware_code(root, base_relative, base_tree) if base_relative and base_tree else None
        node = _top_level_definition(base_code.tree, name) if base_code is not None else None
        if base_code is not None and isinstance(node, ast.ClassDef) and node is not cls:
            out.append((base_code, node))
    return out


def _function_parameters(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    arguments = function.args
    names = {a.arg for a in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs)}
    names.update(a.arg for a in (arguments.vararg, arguments.kwarg) if a is not None)
    return names


def _returned_calls(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.Call]:
    """그 함수 몸통(안쪽 함수 · 클래스 밖)의 `return <호출>` · `return await <호출>`."""
    calls: list[ast.Call] = []
    stack: list[ast.AST] = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Return) and node.value is not None:
            value = node.value.value if isinstance(node.value, ast.Await) else node.value
            if isinstance(value, ast.Call):
                calls.append(value)
        stack.extend(ast.iter_child_nodes(node))
    return sorted(calls, key=lambda call: (call.lineno, call.col_offset))


def _body_calls(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.Call]:
    """그 함수 몸통(안쪽 함수 · 클래스 · lambda 밖)의 모든 호출 — 대입 값 · 문장 호출 · 조건식 · 불 연산 갈래 포함."""
    calls: list[ast.Call] = []
    stack: list[ast.AST] = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.Call):
            calls.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return sorted(calls, key=lambda call: (call.lineno, call.col_offset))


def _body_statements(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
    """그 함수 몸통(안쪽 함수 · 클래스 밖)의 모든 문장."""
    out: list[ast.stmt] = []
    stack: list[ast.AST] = list(function.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        if isinstance(node, ast.stmt):
            out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return sorted(out, key=lambda statement: (statement.lineno, statement.col_offset))


def _call_bound_names(function: ast.FunctionDef | ast.AsyncFunctionDef, call: ast.Call) -> set[str]:
    """`<이름> = <그 호출>` · `<이름> = await <그 호출>` 의 이름."""
    names: set[str] = set()
    for statement in _body_statements(function):
        targets, value = _assigned_value(statement)
        value = value.value if isinstance(value, ast.Await) else value
        if value is call and len(targets) == 1 and isinstance(targets[0], ast.Name):
            names.add(targets[0].id)
    return names


def _returned_call_ids(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[int]:
    """돌려주는 호출 — `return <호출>` · `return await <호출>` 과, `return <이름>` 의 이름에 묶인 호출(`<이름> = <호출>`)."""
    ids = {id(call) for call in _returned_calls(function)}
    returned_names = {
        statement.value.id
        for statement in _body_statements(function)
        if isinstance(statement, ast.Return) and isinstance(statement.value, ast.Name)
    }
    for statement in _body_statements(function):
        targets, value = _assigned_value(statement)
        value = value.value if isinstance(value, ast.Await) else value
        if (
            isinstance(value, ast.Call)
            and len(targets) == 1
            and isinstance(targets[0], ast.Name)
            and targets[0].id in returned_names
        ):
            ids.add(id(value))
    return ids


def _middleware_findings(
    root: Path,
    settings: _ProjectSettings,
    rows: list[_TableRow],
    not_api: frozenset[str],
    api_namespaces: "set[str] | frozenset[str] | None" = frozenset(),
) -> tuple[list[_PreRouteSite], list[tuple[_PreRouteSite, str]]]:
    """d — 프로젝트 미들웨어가 내는 오류 답 ↔ 표 행. hook(같은 클래스 · 프로젝트 기저 클래스 한 단계)과 그 hook 이 돌려주는
    도움 메서드 · 같은 모듈 함수 한 단계까지 읽는다. 같은 status 행이 좁힌 행(`operations` · `methods` · `exempt` · `all` 밖
    `when` · 모든 루트 API 이름공간을 덮지 않는 `namespaces` — 이름공간을 글자로 못 읽은 루트가 있으면(`api_namespaces` 가
    None) `namespaces` 는 늘 좁힘)뿐이면 그 행이 이 미들웨어의 행인지 기계가 가를 수 없으므로 ⓓ 후보로 둔다."""
    sites: list[_PreRouteSite] = []
    candidates: list[tuple[_PreRouteSite, str]] = []
    counted = [row for row in rows if row.status is not None]

    def narrowed(row: _TableRow) -> bool:
        if row.narrowing & {"operations", "methods", "exempt", "when"}:
            return True
        return "namespaces" in row.narrowing and (
            api_namespaces is None or not set(api_namespaces) <= set(row.namespaces)
        )

    for path, lineno in settings.unread:
        candidates.append(
            (
                _PreRouteSite("", path, lineno, "settings `MIDDLEWARE` 의 조각을 글자 · 목록 상수로 풀지 못했다"),
                "그 조각의 프로젝트 미들웨어가 API 경로에 내는 오류 답이 경로 앞 응답 표에 있는가",
            )
        )
    seen: set[str] = set()
    for dotted, settings_path, settings_line in settings.middleware:
        if dotted in seen or dotted in not_api:
            continue
        seen.add(dotted)
        module, _, attribute = dotted.rpartition(".")
        relative = _module_path(root, module) if module else None
        if relative is None:
            continue  # 프로젝트 밖(서드파티 · Django) — 리뷰어 몫
        tree = _parse_project_file(root, relative)
        target = _top_level_definition(tree, attribute)
        if tree is None or target is None:
            candidates.append(
                (
                    _PreRouteSite("", settings_path, settings_line, f"미들웨어 `{dotted}` 의 정의를 읽지 못했다"),
                    "이 미들웨어가 API 경로에 내는 오류 답이 경로 앞 응답 표에 있는가",
                )
            )
            continue
        code = _middleware_code(root, relative, tree)
        hooks: list[tuple[_MiddlewareCode, ast.FunctionDef | ast.AsyncFunctionDef]] = []
        classes: list[tuple[_MiddlewareCode, ast.ClassDef]] = []
        outer: set[str] = set()
        if isinstance(target, ast.ClassDef):
            classes = [(code, target), *_project_base_classes(root, code, target)]
            taken: set[str] = set()
            for owner_code, owner in classes:
                for member in owner.body:
                    if (
                        isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and member.name in MIDDLEWARE_HOOKS
                        and member.name not in taken
                    ):
                        taken.add(member.name)
                        hooks.append((owner_code, member))
        elif isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef)):
            outer = _function_parameters(target)
            hooks = [
                (code, node)
                for node in ast.walk(target)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not target
            ]
        answers: list[tuple[Path, _MiddlewareAnswer]] = []
        answers_of: dict[int, list[_MiddlewareAnswer]] = {}
        unread_reported: set[int] = set()

        def unread_candidate(path: Path, lineno: int, reason: str) -> None:
            candidates.append(
                (
                    _PreRouteSite("", path, lineno, f"미들웨어 `{dotted}` — {reason}"),
                    "이 답이 API 경로에 나는가 · 나면 그 status · 머리가 경로 앞 응답 표에 있는가",
                )
            )

        def passing_call(call: ast.Call, function_code: _MiddlewareCode, passing: set[str]) -> bool:
            resolved = _resolve_expression(call.func, function_code.bindings)
            func = call.func
            return (
                resolved in MIDDLEWARE_RESPONSE_CALLS
                or resolved in MIDDLEWARE_FIXED_STATUS
                or resolved in MIDDLEWARE_PASSING_CALLS
                or (isinstance(func, ast.Attribute) and func.attr.endswith("get_response"))
                or (isinstance(func, ast.Name) and func.id in passing)
                or (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Call)
                    and isinstance(func.value.func, ast.Name)
                    and func.value.func.id == "super"
                )
            )  # 읽은 응답 생성 · 지나가는 응답(get_response · 받은 view) · 기저 hook(위에서 따로 읽음)

        def helper_of(
            call: ast.Call, function_code: _MiddlewareCode
        ) -> tuple[_MiddlewareCode, ast.FunctionDef | ast.AsyncFunctionDef] | None:
            func = call.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id in {"self", "cls"}:
                for owner_code, owner in classes:
                    member = next(
                        (
                            m
                            for m in owner.body
                            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == func.attr
                        ),
                        None,
                    )
                    if member is not None:
                        return owner_code, member
                return None
            if isinstance(func, ast.Name):
                definition = _top_level_definition(function_code.tree, func.id)
                module_name = _module_name(function_code.relative)
                if (
                    isinstance(definition, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and function_code.bindings.get(func.id) == f"{module_name}.{func.id}"
                ):
                    return function_code, definition
            return None

        def read_function(
            function_code: _MiddlewareCode,
            function: ast.FunctionDef | ast.AsyncFunctionDef,
            *,
            follow: bool,
            returned_by_caller: bool,
        ) -> list[_MiddlewareAnswer]:
            """그 함수가 내는 답을 읽는다(한 번). `follow` 면 몸통 어디서든 부른 도움 함수 · 메서드를 한 단계 따른다.
            돌려주는 호출(`return <호출>` · `<이름> = <호출>` 뒤 `return <이름>`)을 따르지 못하면 — 그 함수 결과가 미들웨어 답으로
            돌아갈 때만(`returned_by_caller`) — ⓓ 다."""
            passing = _function_parameters(function) | outer
            returned = _returned_call_ids(function)
            if id(function) not in answers_of:
                found, unread = _middleware_answers(function, function_code.bindings)
                answers_of[id(function)] = list(found)
                answers.extend((function_code.relative, answer) for answer in found)
                for lineno, reason in unread:
                    unread_candidate(function_code.relative, lineno, reason)
                if follow:
                    bound: dict[str, list[_MiddlewareAnswer]] = {}
                    for call in _body_calls(function):
                        if passing_call(call, function_code, passing):
                            continue
                        helper = helper_of(call, function_code)
                        if helper is None:
                            continue
                        helper_answers = read_function(
                            helper[0], helper[1], follow=False, returned_by_caller=id(call) in returned
                        )
                        for name in _call_bound_names(function, call):
                            bound.setdefault(name, []).extend(helper_answers)
                    # 따른 호출에서 받은 이름에 이 함수가 더 싣는 머리 — 그 답의 머리다.
                    for node in _body_statements(function):
                        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                            continue
                        target = node.targets[0]
                        if not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)):
                            continue
                        owners = bound.get(target.value.id)
                        if not owners:
                            continue
                        header_name = _static_string(target.slice, function_code.bindings)
                        if header_name is None:
                            unread_candidate(function_code.relative, node.lineno, "답에 싣는 머리 이름을 글자로 읽지 못했다")
                            continue
                        for owner in owners:
                            owner.headers.add(header_name.lower())
            if returned_by_caller and id(function) not in unread_reported:
                unread_reported.add(id(function))
                for call in _body_calls(function):
                    if id(call) not in returned or passing_call(call, function_code, passing):
                        continue
                    if follow and helper_of(call, function_code) is not None:
                        continue
                    unread_candidate(function_code.relative, call.lineno, "이 hook 이 돌려주는 응답의 status 를 읽지 못했다")
            return answers_of[id(function)]

        for hook_code, hook in hooks:
            read_function(hook_code, hook, follow=True, returned_by_caller=True)
        for answer_path, answer in answers:
            if not 400 <= answer.status <= 599:
                continue
            matching = [row for row in counted if row.status == answer.status]
            if not matching:
                sites.append(
                    _PreRouteSite(
                        "",
                        answer_path,
                        answer.lineno,
                        f"미들웨어 `{dotted}` 가 내는 {answer.status} 응답이 경로 앞 응답 표에 없다 — 표에 그 status "
                        "행을 근거(이 줄)와 함께 더하거나, API 경로를 빼는 미들웨어면 그 빼는 줄을 근거로 "
                        f"`NOT_API_MIDDLEWARE` 에 적는다({PRE_ROUTE_SECTION})",
                    )
                )
                continue
            documented = set().union(*(row.headers for row in matching))  # 좁힌 행 포함 — 어느 행에도 없으면 어느 경로 문서에도 없다
            for header in sorted(answer.headers - documented - CACHE_DIRECTIVE_HEADERS):
                sites.append(
                    _PreRouteSite(
                        "",
                        answer_path,
                        answer.lineno,
                        f"미들웨어 `{dotted}` 가 {answer.status} 에 싣는 머리 `{header}` 가 그 표 행 `headers` 에 없다"
                        f"({PRE_ROUTE_SECTION})",
                    )
                )
            if all(narrowed(row) for row in matching):
                candidates.append(
                    (
                        _PreRouteSite(
                            "",
                            answer_path,
                            answer.lineno,
                            f"미들웨어 `{dotted}` 가 내는 {answer.status} 응답 — 표의 같은 status 행이 좁힌 행"
                            f"(표 {' · '.join(str(row.lineno) for row in matching)}행)뿐이다",
                        ),
                        "이 미들웨어 답이 그 행이 좁힌 경로 · 메서드에만 나는가 — 그 행의 G1 근거가 이 미들웨어 줄인가",
                    )
                )
    return sites, candidates


@dataclass(frozen=True)
class _RouteIndex:
    mounts: dict[str, str | None]  # 루트 API(모듈.이름) → URLconf 마운트 글자(여럿 · 못 읽음 = None)
    routers: dict[str, tuple[str, str] | None]  # Router(모듈.이름) → (루트 API, add_router 앞머리)
    controllers: dict[str, str | None]  # ninja_extra 컨트롤러(모듈.클래스) → 루트 API


def _route_index(root: Path, files: list[Path], roots: list[_RootApi]) -> _RouteIndex:
    """operation 식별 글의 `METHOD 경로` 재료 — URLconf 마운트 · registrar 등록(읽히는 꼴만)."""
    receivers: set[str] = {receiver for api in roots for receiver in api.receivers}
    local_receivers: dict[Path, dict[str, str]] = {
        api.relative_path: {receiver.rsplit(".", 1)[-1]: receiver for receiver in api.receivers} for api in roots
    }
    mounts: dict[str, list[str]] = {}
    registrar_calls: dict[str, list[str]] = {}
    direct: list[tuple[str, str, ast.Call, dict[str, str], Path]] = []  # (루트 API, 메서드, 호출, 바인딩, 파일)

    def resolve(node: ast.AST, bindings: dict[str, str], relative: Path) -> str | None:
        if isinstance(node, ast.Name) and node.id in local_receivers.get(relative, {}):
            return local_receivers[relative][node.id]
        return _resolve_expression(node, bindings)

    scanned = {relative for relative in files if relative.name == "urls.py"} | set(local_receivers)
    for relative in sorted(scanned, key=Path.as_posix):
        tree = _parse_project_file(root, relative)
        if tree is None:
            continue
        bindings = _final_module_symbol_bindings(ParsedSource(relative, "", tree))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = resolve(node.func, bindings, relative)
            if (
                func == "django.urls.path"
                and len(node.args) >= 2
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and isinstance(node.args[1], ast.Attribute)
                and node.args[1].attr == "urls"
            ):
                api = resolve(node.args[1].value, bindings, relative)
                if api in receivers:
                    mounts.setdefault(api, []).append(node.args[0].value)
                continue
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"add_router", "register_controllers"}:
                api = resolve(node.func.value, bindings, relative)
                if api in receivers:
                    direct.append((api, node.func.attr, node, bindings, relative))
                continue
            if func and func.rsplit(".", 1)[-1].startswith("register_") and len(node.args) == 1 and not node.keywords:
                api = resolve(node.args[0], bindings, relative)
                if api in receivers:
                    registrar_calls.setdefault(func, []).append(api)
    for registrar, apis in sorted(registrar_calls.items()):
        if len(set(apis)) != 1:
            continue
        module, _, function_name = registrar.rpartition(".")
        relative = _module_path(root, module)
        tree = _parse_project_file(root, relative) if relative is not None else None
        function = next(
            (
                statement
                for statement in (tree.body if tree is not None else [])
                if isinstance(statement, ast.FunctionDef) and statement.name == function_name
            ),
            None,
        )
        if function is None or not function.args.args or relative is None or tree is None:
            continue
        parameter = function.args.args[0].arg
        bindings = _final_module_symbol_bindings(ParsedSource(relative, "", tree))
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"add_router", "register_controllers"}
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == parameter
            ):
                direct.append((apis[0], node.func.attr, node, bindings, relative))
    routers: dict[str, list[tuple[str, str]]] = {}
    controllers: dict[str, list[str]] = {}
    for api, method, call, bindings, relative in direct:
        if method == "add_router":
            prefix_node = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "prefix"), None)
            router_node = call.args[1] if len(call.args) > 1 else next((k.value for k in call.keywords if k.arg == "router"), None)
            if not (isinstance(prefix_node, ast.Constant) and isinstance(prefix_node.value, str)) or router_node is None:
                continue
            router = resolve(router_node, bindings, relative)
            if router is not None:
                routers.setdefault(router, []).append((api, prefix_node.value))
        else:
            for argument in call.args:
                controller = resolve(argument, bindings, relative)
                if controller is not None:
                    controllers.setdefault(controller, []).append(api)
    return _RouteIndex(
        {api: values[0] if len(values) == 1 else None for api, values in mounts.items()},
        {router: values[0] if len(values) == 1 else None for router, values in routers.items()},
        {controller: values[0] if len(values) == 1 else None for controller, values in controllers.items()},
    )


def _literal_path_argument(call: ast.Call, *, default: str | None) -> str | None:
    node: ast.AST | None = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "path"), None)
    if node is None:
        return default
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _operation_route(
    operation: Operation,
    tree: ast.Module,
    index: _RouteIndex,
) -> str | None:
    """operation 의 `METHOD 생성 문서 경로` — Ninja `get_paths` 와 같은 식으로 읽히는 꼴만(아니면 None)."""
    decorator = operation.decorator
    if not isinstance(decorator.func, ast.Attribute):
        return None
    method = decorator.func.attr.upper()
    module = _module_name(operation.relative_path)
    if operation.owners:
        if len(operation.owners) != 1:
            return None
        cls = next(
            (s for s in tree.body if isinstance(s, ast.ClassDef) and s.name == operation.owners[0]),
            None,
        )
        if cls is None:
            return None
        before = _module_symbol_bindings_before(ParsedSource(operation.relative_path, "", tree)).get(id(cls), {})
        prefix: str | None = None
        for item in cls.decorator_list:
            call = item if isinstance(item, ast.Call) else None
            resolved = _resolve_expression(call.func if call is not None else item, before)
            if resolved not in {"ninja_extra.api_controller", "ninja_extra.controllers.api_controller"}:
                continue
            if call is None or not (call.args or any(k.arg == "prefix_or_class" for k in call.keywords)):
                prefix = ""
            else:
                node = call.args[0] if call.args else next(k.value for k in call.keywords if k.arg == "prefix_or_class")
                prefix = node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None
        api = index.controllers.get(f"{module}.{cls.name}")
        route_path = _literal_path_argument(decorator, default="")
    else:
        receiver = decorator.func.value
        if not isinstance(receiver, ast.Name):
            return None
        bound = index.routers.get(f"{module}.{receiver.id}")
        api, prefix = bound if bound is not None else (None, None)
        route_path = _literal_path_argument(decorator, default=None)
    mount = index.mounts.get(api) if api is not None else None
    if prefix is None or route_path is None or mount is None:
        return None
    path = "/" + mount + "/" + "/".join(part for part in (prefix, route_path) if part)
    while "//" in path:
        path = path.replace("//", "/")
    return f"{method} {re.sub(r'{[^}:]+:', '{', path)}"


def _operations_in(relative: Path, tree: ast.Module) -> list[Operation] | None:
    try:
        return _collect_operations(ParsedSource(relative, "", tree))
    except UsageError:
        return None


def _operation_name(operation: Operation) -> str:
    return ".".join((*operation.owners, operation.function.name))


def _operation_identity(operation: Operation) -> str:
    """c 식별 글 — `<클래스>.<메서드>` · 모듈 함수 operation 은 `<Router 이름>.<함수>`(같은 파일에서 유일하게)."""
    receiver = operation.decorator.func.value if isinstance(operation.decorator.func, ast.Attribute) else None
    if not operation.owners and isinstance(receiver, ast.Name):
        return f"{receiver.id}.{operation.function.name}"
    return _operation_name(operation)


def _in_schema(operation: Operation) -> bool:
    flag = next((k.value for k in operation.decorator.keywords if k.arg == "include_in_schema"), None)
    return not (isinstance(flag, ast.Constant) and flag.value is False)


def _response_parameter_names(operation: Operation) -> set[str]:
    """주입 응답 매개변수 — 주석이 `django.http.HttpResponse` 로 풀리는 것(이름 무관 · Ninja 와 같은 기준)."""
    bindings = operation.bindings if operation.annotations_evaluated else operation.body_bindings
    names: set[str] = set()
    arguments = operation.function.args
    for argument in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs):
        annotation = argument.annotation
        if annotation is None:
            continue
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            try:
                annotation = ast.parse(annotation.value, mode="eval").body
            except SyntaxError:
                continue
        if _resolve_expression(annotation, bindings) in HTTP_RESPONSE_TYPES:
            names.add(argument.arg)
    return names


def _statement_blocks(statements: list[ast.stmt]) -> "list[list[ast.stmt]]":
    blocks: list[list[ast.stmt]] = [statements]
    for statement in statements:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for name in ("body", "orelse", "finalbody"):
            block = getattr(statement, name, None)
            if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                blocks.extend(_statement_blocks(block))
        for handler in getattr(statement, "handlers", ()):
            blocks.extend(_statement_blocks(handler.body))
        for case in getattr(statement, "cases", ()):
            blocks.extend(_statement_blocks(case.body))
    return blocks


StatusResolver = Callable[[ast.Call, "list[ast.stmt]", Operation], "int | None"]


def _plain_status(call: ast.Call, block: "list[ast.stmt]", operation: Operation) -> int | None:
    return _status_from_expression(call.args[0], operation.body_bindings) if call.args else None


def _header_findings(
    operation: Operation,
    resolve_status: StatusResolver,
    tree: ast.Module | None = None,
) -> tuple[list[_PreRouteSite], list[tuple[_PreRouteSite, str]]]:
    """f — 오류 branch(마지막 문장이 `return Status(<4xx · 5xx>, …)`)에서 주입 응답에 싣는 글자 머리 ↔ 그 status 의 머리 보충."""
    parameters = _response_parameter_names(operation)
    if not parameters:
        return [], []
    name = _operation_name(operation)
    relative = operation.relative_path
    raw_extra = _keyword(operation.decorator, "openapi_extra")
    supplement = _header_supplement(_resolved_extra(raw_extra, tree) if raw_extra is not None else None, tree)
    if raw_extra is not None and _resolved_extra(raw_extra, tree) is None:
        supplement = None
    sites: list[_PreRouteSite] = []
    candidates: list[tuple[_PreRouteSite, str]] = []
    question = "그 머리가 실리는 응답 status 의 머리 보충(`openapi_extra` responses `headers`)에 적혔는가"

    def candidate(lineno: int, message: str) -> None:
        candidates.append(
            (_PreRouteSite("f", relative, lineno, f"`{name}` — {message}", operation.function.name), question)
        )

    def header_of(statement: ast.stmt) -> tuple[ast.Assign, str | None] | None:
        if not (isinstance(statement, ast.Assign) and len(statement.targets) == 1):
            return None
        target = statement.targets[0]
        if not isinstance(target, ast.Subscript):
            return None
        if isinstance(target.value, ast.Name) and target.value.id in parameters:
            return statement, _static_string(target.slice, operation.body_bindings)
        return None

    reported: set[tuple[int, str]] = set()
    Header = tuple[ast.Assign, "str | None", bool]  # (대입, 머리 이름, 그 return 에 늘 실림)

    def check(last: ast.Return, block: "list[ast.stmt]", headers: "list[Header]") -> None:
        status = resolve_status(last.value, block, operation)  # type: ignore[arg-type]
        if status is not None and not 400 <= status <= 599:
            return  # 성공 쪽 머리는 f 밖
        for statement, header, definite in headers:
            if header is not None and header.lower() in CACHE_DIRECTIVE_HEADERS:
                continue
            if header is None:
                message = "주입 응답에 싣는 머리 이름을 글자로 읽지 못했다"
            elif status is None:
                message = f"머리 `{header}` — 그 branch 마지막 `Status` 의 status 를 글자로 읽지 못했다"
            elif supplement is None:
                message = f"머리 `{header}` — `openapi_extra` 머리 보충을 글자로 읽지 못했다"
            elif header.lower() in supplement.get(status, set()):
                continue
            elif not definite:
                message = (
                    f"머리 `{header}` — 앞 블록에서 실릴 수 있는 머리가 그 뒤 반환하는 {status} 에 실리는지 "
                    "기계가 가르지 못했다(흐름에 따라 다르다)"
                )
            else:
                key = (statement.lineno, f"{header.lower()}:{status}")
                if key in reported:
                    continue
                reported.add(key)
                sites.append(
                    _PreRouteSite(
                        "f",
                        relative,
                        statement.lineno,
                        f"`{name}` 가 주입 응답에 싣는 머리 `{header}` 가 그 뒤 반환하는 {status} 의 머리 보충에 없다 — "
                        f"`openapi_extra` 의 responses 에 정수 키 {status} 의 `headers` 로 적는다({SUPPLEMENT_SECTION})",
                        operation.function.name,
                    )
                )
                continue
            if (statement.lineno, message) not in reported:
                reported.add((statement.lineno, message))
                candidate(statement.lineno, message)

    def nested_blocks(statement: ast.stmt) -> "list[list[ast.stmt]]":
        blocks: list[list[ast.stmt]] = []
        for field_name in ("body", "orelse", "finalbody"):
            block = getattr(statement, field_name, None)
            if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
                blocks.append(block)
        blocks.extend(handler.body for handler in getattr(statement, "handlers", ()))
        blocks.extend(case.body for case in getattr(statement, "cases", ()))
        return blocks

    def always_ends(block: "list[ast.stmt]") -> bool:
        """그 블록이 늘 `return` · `raise` 로 끝나는가 — 분명히 가를 수 있는 꼴만(반복 · `while True` 는 지나감으로 둔다)."""
        if not block:
            return False
        last = block[-1]
        if isinstance(last, (ast.Return, ast.Raise)):
            return True
        if isinstance(last, ast.If):
            return bool(last.orelse) and always_ends(last.body) and always_ends(last.orelse)
        if isinstance(last, ast.Try):
            if last.finalbody and always_ends(last.finalbody):
                return True
            body_ends = always_ends(last.body) or (bool(last.orelse) and always_ends(last.orelse))
            return body_ends and all(always_ends(handler.body) for handler in last.handlers)
        if isinstance(last, (ast.With, ast.AsyncWith)):
            return always_ends(last.body)
        if isinstance(last, ast.Match):
            wildcard = any(
                isinstance(case.pattern, ast.MatchAs) and case.pattern.pattern is None and case.guard is None
                for case in last.cases
            )
            return wildcard and all(always_ends(case.body) for case in last.cases)
        return False

    def runs_code(expression: ast.AST) -> bool:
        """`return` 값 식 안에 `Status(…)` · 클래스(Schema) 생성 밖의 호출 · `await` 이 있는가 — 머리 뒤 실행이 터질 수 있다."""
        for node in ast.walk(expression):
            if isinstance(node, ast.Await):
                return True
            if not isinstance(node, ast.Call):
                continue
            if _resolve_expression(node.func, operation.body_bindings) == "ninja.Status":
                continue
            callee = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ""
            if callee[:1].isupper():
                continue
            return True
        return False

    def runs_after(later: "list[ast.stmt]") -> bool:
        for statement in later:
            if isinstance(statement, ast.Return):
                return statement.value is not None and runs_code(statement.value)
            return True
        return False

    def try_carried(statements: "list[ast.stmt]", tail: bool, loop: bool) -> "list[Header]":
        """try 몸통 머리 가운데 그 뒤에 실행이 있는 것 — 뒤 문장(`return` 이면 그 값 식 안 호출) · 바깥 꼬리 · 반복의 다음 차례.
        except · finally 로 물린다."""
        carried: list[Header] = []
        for index, statement in enumerate(statements):
            more = loop or runs_after(statements[index + 1:]) or (not always_ends(statements) and tail)
            header = header_of(statement)
            if header is not None:
                if more:
                    carried.append((header[0], header[1], True))
                continue
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            in_loop = loop or isinstance(statement, (ast.For, ast.AsyncFor, ast.While))
            for block in nested_blocks(statement):
                carried.extend(try_carried(block, more, in_loop))
        return carried

    def possible(headers: "list[Header]") -> "list[Header]":
        return [(statement, header, False) for statement, header, _ in headers]

    def visit(block: "list[ast.stmt]", inherited: "list[Header]") -> "list[Header]":
        """블록을 내려가며 앞선 바깥 블록의 머리(그 문장보다 앞 줄)를 «늘 실림» 으로 물려준다. 늘 끝나지 않는 안쪽 블록의
        머리는 뒤 형제 문장에 «실릴 수 있음»(ⓓ)으로 간다. `try` 몸통의 머리는 `else` 에, `except` · `finally` 에는 그 머리 뒤에
        실행이 있을 때만 «늘 실림» 으로 간다. 돌려주는 값 = 이 블록을 나가며 실려 있을 수 있는 머리."""
        local: list[Header] = []

        def merge(escaped: "list[Header]") -> None:
            for statement, header, _ in escaped:
                if all(statement is not known for known, _, _ in local):
                    local.append((statement, header, False))

        for statement in block:
            header = header_of(statement)
            if header is not None:
                local.append((header[0], header[1], True))
                continue
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target = statement.targets[0]
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and target.value.attr == "headers"
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id in parameters
                ):
                    candidate(statement.lineno, "주입 응답 `.headers[...]` 머리 — 이 꼴은 기계가 머리 보충과 잇지 않는다")
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            prefix = inherited + local
            escaped: list[Header] = []
            if isinstance(statement, ast.Try):
                body_left = visit(statement.body, prefix)
                escaped.extend(body_left)
                carried = try_carried(statement.body, False, False)
                to_handlers = prefix + carried
                for handler in statement.handlers:
                    escaped.extend(visit(handler.body, to_handlers))
                    if not always_ends(handler.body):
                        escaped.extend(carried)  # 지나가는 except — 몸통 머리가 try 뒤로 간다
                if statement.orelse:
                    escaped.extend(visit(statement.orelse, prefix + body_left))
                if statement.finalbody:
                    escaped.extend(visit(statement.finalbody, to_handlers))
            else:
                for nested in nested_blocks(statement):
                    escaped.extend(visit(nested, prefix))
            merge(escaped)
        last = block[-1] if block else None
        applicable = inherited + local
        if (
            applicable
            and isinstance(last, ast.Return)
            and isinstance(last.value, ast.Call)
            and _resolve_expression(last.value.func, operation.body_bindings) == "ninja.Status"
        ):
            check(last, block, applicable)
        return [] if always_ends(block) else local

    visit(operation.function.body, [])
    for node in ast.walk(operation.function):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and (
                (isinstance(func.value, ast.Name) and func.value.id in parameters and func.attr in {"setdefault", "__setitem__"})
                or (
                    isinstance(func.value, ast.Attribute)
                    and func.value.attr == "headers"
                    and isinstance(func.value.value, ast.Name)
                    and func.value.value.id in parameters
                )
            )
        ):
            candidate(node.lineno, f"주입 응답 머리를 `{func.attr}` 로 싣는다 — 이 꼴은 기계가 머리 보충과 잇지 않는다")
        elif any(keyword.arg == "headers" for keyword in node.keywords) and (
            _resolve_expression(func, operation.body_bindings) in MIDDLEWARE_RESPONSE_CALLS
        ):
            candidate(node.lineno, "raw 응답 `headers=` 머리 — 이 꼴은 기계가 머리 보충과 잇지 않는다")
    return sites, candidates


@dataclass
class _PreRouteResult:
    findings: Findings
    candidates: Candidates
    reasons: list[str]


def _pre_route_slice(
    root: Path,
    covered: "set[tuple[str, str, int]] | frozenset[tuple[str, str, int]]" = frozenset(),
    resolvers: "dict[Path, StatusResolver] | None" = None,
) -> _PreRouteResult:
    """a · b · c · d · f — 공용 포매터 violation · candidate 문법으로 모은다.

    `covered` 는 tree · code 레인이 이미 낸 같은 사건(override · monkeypatch · postprocess 행)의
    좌표다 — 루트 API 레인은 그 자리를 다시 내지 않는다. `resolvers` 는 code 레인이 고른
    controller 의 branch status 해석(오류 카탈로그)이다 — 없으면 글자 · 상수만 읽는다."""
    files = _project_python_files(root)
    roots, root_sites = _root_api_lane(root, files)
    sites: list[_PreRouteSite] = [
        site for site in root_sites if (site.kind, site.relative_path.as_posix(), site.lineno) not in covered
    ]
    candidate_sites: list[tuple[_PreRouteSite, str]] = []
    canonical_tree = _parse_project_file(root, PRE_ROUTE_PATH) if (root / PRE_ROUTE_PATH).is_file() else None
    table_tree = _parse_project_file(root, PRE_ROUTE_TABLE_PATH) if (root / PRE_ROUTE_TABLE_PATH).is_file() else None
    reasons: list[str] = []
    if not (root / PRE_ROUTE_PATH).is_file():
        reasons.append(f"`{PRE_ROUTE_PATH.as_posix()}` 없음")
    elif canonical_tree is None:
        sites.append(_PreRouteSite("", PRE_ROUTE_PATH, 1, f"경로 앞 응답 정본을 읽지 못했다(문법 오류)({PRE_ROUTE_SECTION})"))
    else:
        sites.extend(_canonical_findings(PRE_ROUTE_PATH, canonical_tree))
    if not (root / PRE_ROUTE_TABLE_PATH).is_file():
        reasons.append(f"`{PRE_ROUTE_TABLE_PATH.as_posix()}` 없음")
    elif table_tree is None:
        sites.append(_PreRouteSite("", PRE_ROUTE_TABLE_PATH, 1, f"경로 앞 응답 표를 읽지 못했다(문법 오류)({PRE_ROUTE_SECTION})"))
    else:
        settings = _project_settings(root, files)
        namespaces = {namespace for api in roots for namespace in api.namespaces if namespace is not None}
        table_sites, rows, not_api, table_candidates = _table_findings(
            PRE_ROUTE_TABLE_PATH, table_tree, namespaces, settings, _handler400_view(root, settings)
        )
        sites.extend(table_sites)
        candidate_sites.extend(table_candidates)
        readable = all(namespace is not None for api in roots for namespace in api.namespaces)
        middleware_sites, middleware_candidates = _middleware_findings(
            root, settings, rows, not_api, namespaces if readable else None
        )
        sites.extend(middleware_sites)
        candidate_sites.extend(middleware_candidates)
    reasons.extend(
        f"`{api.relative_path.as_posix()}` 의 루트 API 가 정해진 클래스로 지어지지 않았다" for api in roots if not api.documented
    )
    modules: list[tuple[Path, ast.Module, list[Operation]]] = []
    for relative, tree in sorted(_parsed_driving_modules(root).items(), key=lambda item: item[0].as_posix()):
        operations = _operations_in(relative, tree)
        if operations is None:
            candidate_sites.append(
                (
                    _PreRouteSite("", relative, 1, "operation 을 읽지 못했다(데코레이터 receiver 출처가 흔들린다)"),
                    "이 파일의 operation 이 경로 앞 오류 · 주입 응답 머리 규칙을 지키는가",
                )
            )
            continue
        modules.append((relative, tree, [operation for operation in operations if _in_schema(operation)]))
    if not roots and any(operations for _, _, operations in modules):
        reasons.append("루트 API(`NinjaAPI` · `NinjaExtraAPI` 또는 그 정해진 클래스로 짓는 모듈 이름)를 찾지 못했다")
    index = _route_index(root, files, roots) if reasons else None
    for relative, tree, operations in modules:
        for operation in operations:
            if index is not None:
                route = _operation_route(operation, tree, index)
                shown = f"`{_operation_identity(operation)}`" + (f"(`{route}`)" if route else "")
                sites.append(
                    _PreRouteSite(
                        "",
                        relative,
                        operation.decorator.lineno,
                        f"operation {shown} 의 경로 앞 오류(인증 · CSRF · 권한 · throttle · 입력 · 미들웨어 · 앞단 답)가 "
                        "생성 문서에 없다 — 루트 API 를 정해진 클래스로 짓고 framework/ninja/ 에 정본 · 표 파일을 둔다"
                        f"({PRE_ROUTE_SECTION})",
                        operation.function.name,
                    )
                )
            header_sites, header_candidates = _header_findings(
                operation, (resolvers or {}).get(relative, _plain_status), tree
            )
            sites.extend(header_sites)
            candidate_sites.extend(header_candidates)
    findings = Findings(defer=True)
    for site in sites:
        findings.add("#63", where=f"{site.relative_path}:{site.lineno}", msg=site.msg, symbol=site.symbol)
    candidates = Candidates(defer=True)
    for site, question in candidate_sites:
        candidates.add("#63", where=f"{site.relative_path}:{site.lineno}", msg=site.msg, question=question, symbol=site.symbol)
    return _PreRouteResult(findings, candidates, reasons)


def _suppress_overlapped_tree(
    tree_findings: Findings,
    tree_keys: list[tuple[str, str, int]],
    code_keys: set[tuple[str, str, int]],
) -> Findings:
    """앵커 레인 tree↔code 동일 사건 선점 억제(귀속 매핑표 v2 overlap 절 — U14).

    code 레인이 같은 사건(openapi_extra·override·monkeypatch)을 적중한 대상의
    tree 사이트는 라인·레코드 모두 방출하지 않는다(1건 대표 — 더 정밀한 판정이
    이긴다. 대상 밖·code 미발화에서는 tree 단독 그대로)."""
    kept = Findings(tree_findings.checker, defer=True)
    for entry, key in zip(tree_findings.entries, tree_keys):
        if key in code_keys:
            continue
        kept.add(entry.rule, entry.where, entry.msg, entry.symbol)
    return kept


def _print_tree_findings(findings: Findings) -> None:
    print("[check-openapi-error-declaration] BLOCKER — OpenAPI 오류 선언 규율 위반 (#63 · D27):")
    emit_all(findings, printer=print)


def _print_pre_route(result: _PreRouteResult) -> None:
    if result.findings:
        print(
            "[check-openapi-error-declaration] BLOCKER — 경로 앞 응답 · 머리 보충 위반 "
            f"(#63 · {PRE_ROUTE_SECTION}):"
        )
        if result.reasons:
            print(f"  경로 앞 응답이 서지 않은 까닭: {' · '.join(result.reasons)}")
        emit_all(result.findings, printer=print)
    if result.candidates:
        print(
            "[check-openapi-error-declaration] ⓓ 후보 — 기계가 후보를 좁혔다 · 마무리 물음은 "
            "리뷰어 몫(exit 불산입):"
        )
        emit_all(result.candidates, printer=print)


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
        if config.anchor is not None:
            # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚
            # 파일·공허 차분이 침묵 exit 0 되지 않게 parse 직후 막는다(fail-closed).
            anchor_diff.validate_materials(config.root, config.anchor, config.anchor_debt_file,
                **({"approved_merge_file": config.anchor_approved_merge_file}
                   if config.anchor_approved_merge_file is not None else {}))
        bcs = _tree_bcs63(config.root)
        if not any(
            (bc / d).is_dir() for bc in bcs for d in _TREE_DRIVING_SET
        ) and _tree_adopted63(bcs):
            emit_all(
                zero_target_guard("[check-openapi-error-declaration] blocker: 채택 신호는 있는데 driving 층이 0건이다 — 조용한 무동작을 금지한다(#74)"),
                printer=print,
                indent="",
            )
            return 2
        # 일반 실행은 슬라이스 선점 계약을 유지한다. 앵커 및 그 기준선 재실행은
        # 같은 전 슬라이스 진단을 수집해야 기존 code 진단이 신규로 오분류되지 않는다.
        # 경로 앞 응답 레인(a · b · c · d · f)은 모든 프로필에서 돌고 다른 레인을 선점하지 않는다.
        collected: list[str] = []
        pending_analysis: list[str] = []
        tree_findings, tree_keys = _tree_slice63(config.root)
        covered: set[tuple[str, str, int]] = set(tree_keys)
        if tree_findings and config.anchor is None and not config.anchor_baseline:
            _print_tree_findings(tree_findings)
            _print_pre_route(_pre_route_slice(config.root, covered))
            return 2
        if config.profile == "dddjango-code-json":
            # 앵커 레인의 tree↔code 동일 사건 선점 억제를 위해 code 레인을 먼저
            # 계산한다 — 분석 불능(UsageError)이어도 확정 tree 진단은 exit 1 전에
            # 그대로 인쇄한다(현행 stdout 순서 보존 · 억제는 code 실발화 시에만).
            try:
                analysis, findings, code_keys, resolvers = _code_findings(config)
            except UsageError:
                if tree_findings:
                    _print_tree_findings(tree_findings)
                raise
            if config.anchor_baseline:
                analysis = anchor_diff.settle_baseline_analysis(analysis)
            dynamic_proof_only = bool(analysis) and all(
                issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED ")
                for issue in analysis
            )
            emit_code = bool(findings) and (not analysis or dynamic_proof_only)
            if emit_code and tree_findings:
                tree_findings = _suppress_overlapped_tree(tree_findings, tree_keys, code_keys)
            pre_route = _pre_route_slice(
                config.root, covered | (code_keys if emit_code else set()), resolvers
            )
            if tree_findings:
                _print_tree_findings(tree_findings)
                collected.extend(lines(tree_findings))
            if emit_code:
                records = _code_findings_records(findings)
                _print_code_findings(records)
                collected.extend(lines(records))
                # 토큰-only analysis 는 차분 강등으로 소거되지 않는다 — findings 가
                # 전건 앵커 기존분이어도 proof 경로(exit 1)로 남긴다(fail-open 차단).
                pending_analysis = analysis
            _print_pre_route(pre_route)
            collected.extend(lines(pre_route.findings))
            if emit_code and config.anchor is None:
                return 2
            if not emit_code and analysis:
                raise UsageError("; ".join(analysis))
        else:
            if tree_findings:
                _print_tree_findings(tree_findings)
                collected.extend(lines(tree_findings))
            pre_route = _pre_route_slice(config.root, covered)
            _print_pre_route(pre_route)
            collected.extend(lines(pre_route.findings))
            repo_scan = _repo_scan_findings(config.root)
            if repo_scan:
                _print_repo_scan_findings(repo_scan)
                if config.anchor is None:
                    return 2
                collected.extend(lines(repo_scan))
        if config.anchor_baseline:
            # 기준선 재실행은 차분 재귀 없이 모은 결과로 끝낸다(registry #15 와 같은 끝).
            return 2 if collected else 0
        if collected and config.anchor is None:
            return 2
        if collected:
            verdict = anchor_diff.partition_exit(
                script=Path(__file__).resolve(),
                label="[check-openapi-error-declaration]",
                target=config.root,
                anchor=config.anchor or "",
                argv=argv[1:],
                findings=collected,
                path_flags=frozenset({"--api-module", "--controller-module"}),
                debt_file=config.anchor_debt_file,
                # 기준선 재실행(--anchor-baseline)은 tree · code · 경로 앞 응답 레인을 끝까지 모은 뒤에만 exit 2 로 끝난다 —
                # 승인 머지 ^1 렌더의 c 줄(operation 마다)이 «완결 안 됨» 으로 읽혀 상호작용 유입 증명을 깨지 않게 한다(registry 의 context-isolation · composition-root · api-error-controller-contract 와 같은 꼴).
                **({"approved_merge_file": config.anchor_approved_merge_file, "baseline_collects_all": True}
                   if config.anchor_approved_merge_file is not None else {}),
                analysis_pending=bool(pending_analysis),
            )
            if verdict == 0 and pending_analysis:
                raise UsageError("; ".join(pending_analysis))
            return verdict
        return 0
    except anchor_diff.AnchorDiffUsage as exc:
        print(f"[check-openapi-error-declaration] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except UsageError as exc:
        print(f"[check-openapi-error-declaration] 사용 오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
