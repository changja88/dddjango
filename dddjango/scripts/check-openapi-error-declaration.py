#!/usr/bin/env python3
"""dddjango OpenAPI 오류 계약 결정적 백스톱.

positional/auto/preserve 실행은 기존 ``openapi_extra.responses`` 저장소 전수
검사를 보존한다. ``dddjango-code-json`` profile은 선택된 operation이 직접 반환하는
BC 오류와 ``response={status: <Bc>ErrorSchema}`` 선언의 일치를 검증하고, 선택 API
module의 수동 OpenAPI 후처리를 차단한다.

종료코드: 0=clean, 1=사용/분석 오류, 2=blocker.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 위반 라인과 레코드는 공용 포매터(출력 계약 v2 — ordered emitter)가
같은 순서로 산출하고, 전 위반의 귀속은 #63 하나다(rule-owner-map). 앵커 실행의
tree↔code 동일 사건 이중 방출은 tree 사이트 선점 억제로 막는다(귀속 매핑표 v2
overlap 절 — U14).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: 없음(대장 미등재 — T3 이월).
  미확정 #N 은 T3 이관에서 해소한다(현행 조인 3종 — 판단표
  `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md` §2·§5).
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
from findings import Findings, emit_all, lines, zero_target_guard
from dataclasses import dataclass
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
    namespace = _argument_parser().parse_args(argv)
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
    if namespace.anchor_baseline and anchor_diff.is_git_worktree(root):
        issues.append(
            f"{anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용 — git 저장소 TARGET 금지"
        )
    explicit = profile in {"dddjango-code-json", "preserve-established"}
    strict_content = profile == "dddjango-code-json"
    scope = _one("--scope", namespace.scope, required=explicit, issues=issues)
    api_module = _one(
        "--api-module", namespace.api_module, required=explicit, issues=issues
    )
    controller_modules = _unique(
        "--controller-module", namespace.controller_module, issues
    )
    scope_bcs = _unique("--scope-bc", namespace.scope_bc, issues)
    error_bcs = _unique("--error-bc", namespace.error_bc, issues)
    if explicit and not controller_modules and not namespace.anchor_baseline:
        # anchor-baseline 모드에선 앵커 트리에 없는 controller 가 걷혀 빈 집합이 정상이다.
        issues.append("필수 인자 누락: --controller-module")
    if explicit and not scope_bcs:
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
    required = [Path(config.api_module or "")]
    required.extend(Path(raw) for raw in config.controller_modules)
    required.append(Path("framework/ninja/framework_error_schema.py"))
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


def _scan_response_statuses(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[int]:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if keyword.arg != "response":
                continue
            if not isinstance(keyword.value, ast.Dict):
                return set()
            return {
                status
                for key in keyword.value.keys
                if key is not None
                for status in [_literal_status(key)]
                if status is not None
            }
    return set()


def _scan_openapi_extra_statuses(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[int]:
    statuses: set[int] = set()
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        for keyword in decorator.keywords:
            if keyword.arg != "openapi_extra" or not isinstance(keyword.value, ast.Dict):
                continue
            for key, value in zip(keyword.value.keys, keyword.value.values):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == "responses"
                    and isinstance(value, ast.Dict)
                ):
                    for status_key in value.keys:
                        status = (
                            _literal_status(status_key)
                            if status_key is not None
                            else None
                        )
                        if status is not None and 400 <= status <= 599:
                            statuses.add(status)
    return statuses


def _scan_operations(source: str) -> list[str]:
    if not NINJA_IMPORT_RE.search(source):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        missing = sorted(
            _scan_openapi_extra_statuses(node) - _scan_response_statuses(node)
        )
        if missing:
            findings.append(
                f"operation '{node.name}' "
                f"(오류 {missing} 가 openapi_extra 에만·response= 누락)"
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
        hits = _scan_operations(source)
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
    common = parsed_by_path[Path("framework/ninja/framework_error_schema.py")]
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
    common_relative = Path("framework/ninja/framework_error_schema.py")
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


def _collect_operations(parsed: ParsedSource) -> list[Operation]:
    operations: list[Operation] = []
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
                requirements.setdefault(status, set()).add(instance.symbol.bc)
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
    base_by_bc = {
        symbol.bc: symbol
        for symbol in catalog.values()
        if symbol.kind == "base" and symbol.bc is not None
    }
    for status, required_bcs in sorted(requirements.items()):
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
        schema = _schema_symbol(value, operation.bindings, catalog)
        if schema is None:
            raise UsageError(
                "required response schema provenance 분석 불능: "
                f"{operation.identity} status {status}"
            )
        for bc in sorted(required_bcs):
            expected = base_by_bc.get(bc)
            if expected is None:
                raise UsageError(f"required BC FrameworkErrorSchema base 분석 불능: {bc}")
            if not isinstance(schema, ErrorSymbol) or schema.full_path != expected.full_path:
                shown = schema.full_path if isinstance(schema, ErrorSymbol) else schema
                findings.append(
                    Finding(
                        operation.relative_path,
                        operation.decorator.lineno,
                        "wrong-response-schema",
                        f"{operation.identity} status {status}는 "
                        f"{expected.full_path} 필요 (현재 {shown})",
                        symbol=operation.function.name,
                    )
                )

    for status, value in sorted(final_values.items()):
        if status in uncertain or not 400 <= status <= 599:
            continue
        schema = _schema_symbol(value, operation.bindings, catalog)
        if not isinstance(schema, ErrorSymbol):
            continue
        if not requirements.get(status):
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
    return findings


def _openapi_extra_findings(operation: Operation) -> list[Finding]:
    extra = _keyword(operation.decorator, "openapi_extra")
    if not isinstance(extra, ast.Dict):
        return []
    for key, value in zip(extra.keys, extra.values):
        if not (
            isinstance(key, ast.Constant)
            and key.value == "responses"
            and isinstance(value, ast.Dict)
        ):
            continue
        statuses: list[int] = []
        for status_key in value.keys:
            if status_key is None:
                continue
            text = _static_string(status_key, operation.bindings)
            status = (
                int(text)
                if text is not None and text.isdigit()
                else _status_from_expression(status_key, operation.bindings)
            )
            if status is not None and 400 <= status <= 599:
                statuses.append(status)
        statuses.sort()
        if statuses:
            return [
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "openapi-extra",
                    f"{operation.identity} 오류 responses {statuses}를 "
                    "openapi_extra로 수동 선언",
                    symbol=operation.function.name,
                )
            ]
    return []


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
    deferred_functions: list[
        tuple[ast.FunctionDef | ast.AsyncFunctionDef, dict[str, str]]
    ] = []

    def scan_expression(expression: ast.AST, bindings: dict[str, str]) -> None:
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
            if api_subclass:
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
    return keys


def _code_findings(
    config: Config,
) -> tuple[list[str], list[Finding], set[tuple[str, str, int]]]:
    parsed_by_path = _parse_code_sources(config)
    api = parsed_by_path[Path(config.api_module or "")]
    findings, selected_imports = _api_module_findings(api)
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
            return analysis, deduplicated, _module_overlap_keys(deduplicated)
        raise
    for operation in controller_operations:
        try:
            requirements = _operation_requirements(operation, catalog)
            findings.extend(_response_findings(operation, requirements, catalog))
            extra_findings = _openapi_extra_findings(operation)
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
            if not issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "):
                raise
            analysis.append(issue)
    deduplicated = _deduplicate_findings(findings)
    return sorted(set(analysis)), deduplicated, overlap_keys | _module_overlap_keys(deduplicated)


def _print_repo_scan_findings(findings: Findings) -> None:
    print(
        "[check-openapi-error-declaration] BLOCKER — 오류 status 를 openapi_extra 로만 "
        "선언하고 "
        "response={...} 엔 누락함(ninja 가 타입으로 미인지 = 선언 계약 밖):"
    )
    emit_all(findings, printer=print)
    print(
        "  근거: implementation-django-ninja §2.2 line111. 가능한 모든 status"
        "(404·409·422 등)를 response={...} 에 선언한다 — "
        "openapi_extra/get_openapi_schema 수동 선언은 Swagger 가시성만 달성하고 "
        "ninja 응답 타입엔 안 들어간다. 오류 schema 를 response= 로 옮겨라. "
        "설계로 반송하라."
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
        "<Bc>ErrorSchema 계약 불일치 또는 수동 OpenAPI 후처리:"
    )
    emit_all(records, printer=print)
    print(
        "  조치: 각 직접 반환 status를 같은 BC의 <Bc>ErrorSchema base로 선언하고, "
        "직접 반환하지 않는 BC 오류 광고와 "
        "openapi_extra/get_openapi_schema 후처리를 "
        "제거한다."
    )


# ── 표준 트리 슬라이스 — #63 (D27 «OpenAPI 도 같다») ────────────────────────
#
# 오류 응답은 operation 이 `response={status: <Bc>ErrorSchema}` 로 «직접 선언»한다 —
# openapi_extra 의 responses 보충 · `get_openapi_schema` override · `openapi_schema`
# monkeypatch/postprocessor 는 사후 변형이라 위반이다. 모든 프로필에서 돈다.

_TREE_DRIVING_SET = frozenset({"driving_layer"})
_TREE_LAYERS63 = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
_TREE_APP_MARKERS63 = ("models.py", "apps.py", "views.py", "admin.py")


def _tree_bcs63(root: Path) -> list[Path]:
    out: list[Path] = []
    for c in root.rglob("application"):
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


def _tree_slice63(root: Path) -> tuple[Findings, list[tuple[str, str, int]]]:
    """tree 3사이트 — 공용 포매터 violation 문법(B형 locator `{rel}:{lineno}` 정형화).

    엔트리와 같은 순서의 keys 는 앵커 레인 tree↔code 동일 사건 선점 억제의 좌표다
    (귀속 매핑표 v2 overlap 절 — override/monkeypatch 는 같은 행, openapi_extra 는
    같은 function def 행에서 code 레인과 만난다)."""
    findings = Findings(defer=True)
    keys: list[tuple[str, str, int]] = []
    files: list[Path] = []
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root)
        if _scan_is_production_path(rel):
            files.append(p)
    for f in files:
        rel = f.relative_to(root)
        try:
            mod = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "get_openapi_schema":
                    where = f"{rel}:{node.lineno}"
                    msg = "`get_openapi_schema` override — 오류 응답은 operation 의 `response=` 직접 선언으로만 문서화한다"
                    findings.add("#63", where=where, msg=msg)
                    keys.append(("override", rel.as_posix(), node.lineno))
                for deco in node.decorator_list:
                    if not isinstance(deco, ast.Call):
                        continue
                    for kw in deco.keywords:
                        if kw.arg == "openapi_extra" and _dict_has_key(kw.value, "responses"):
                            where = f"{rel}:{node.lineno}"
                            msg = "`openapi_extra` 의 responses 보충 — 오류 응답은 `response={status: <Bc>ErrorSchema}` 로 직접 선언한다"
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


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
        if config.anchor is not None:
            # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚
            # 파일·공허 차분이 침묵 exit 0 되지 않게 parse 직후 막는다(fail-closed).
            anchor_diff.validate_materials(config.root, config.anchor, config.anchor_debt_file)
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
        # --anchor 미지정이면 현행 그대로 각 슬라이스에서 즉시 exit 2 — 지정 시에만
        # 슬라이스 진단을 모아 마지막에 판정 차분(anchor_diff)으로 exit 를 정한다.
        collected: list[str] = []
        pending_analysis: list[str] = []
        tree_findings, tree_keys = _tree_slice63(config.root)
        if tree_findings and config.anchor is None:
            _print_tree_findings(tree_findings)
            return 2
        if config.profile == "dddjango-code-json":
            # 앵커 레인의 tree↔code 동일 사건 선점 억제를 위해 code 레인을 먼저
            # 계산한다 — 분석 불능(UsageError)이어도 확정 tree 진단은 exit 1 전에
            # 그대로 인쇄한다(현행 stdout 순서 보존 · 억제는 code 실발화 시에만).
            try:
                analysis, findings, code_keys = _code_findings(config)
            except UsageError:
                if tree_findings:
                    _print_tree_findings(tree_findings)
                raise
            dynamic_proof_only = bool(analysis) and all(
                issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED ")
                for issue in analysis
            )
            emit_code = bool(findings) and (not analysis or dynamic_proof_only)
            if emit_code and tree_findings:
                tree_findings = _suppress_overlapped_tree(tree_findings, tree_keys, code_keys)
            if tree_findings:
                _print_tree_findings(tree_findings)
                collected.extend(lines(tree_findings))
            if emit_code:
                records = _code_findings_records(findings)
                _print_code_findings(records)
                if config.anchor is None:
                    return 2
                collected.extend(lines(records))
                # 토큰-only analysis 는 차분 강등으로 소거되지 않는다 — findings 가
                # 전건 앵커 기존분이어도 proof 경로(exit 1)로 남긴다(fail-open 차단).
                pending_analysis = analysis
            elif analysis:
                raise UsageError("; ".join(analysis))
        else:
            if tree_findings:
                _print_tree_findings(tree_findings)
                collected.extend(lines(tree_findings))
            repo_scan = _repo_scan_findings(config.root)
            if repo_scan:
                _print_repo_scan_findings(repo_scan)
                if config.anchor is None:
                    return 2
                collected.extend(lines(repo_scan))
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
