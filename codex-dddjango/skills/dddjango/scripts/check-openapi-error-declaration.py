#!/usr/bin/env python3
"""dddjango OpenAPI 오류 계약 결정적 백스톱.

positional/auto/preserve 실행은 기존 ``openapi_extra.responses`` brownfield
검사를 보존한다. ``dddjango-code-json`` profile은 선택된 operation이 직접 반환하는
BC 오류와 ``response={status: <Bc>ErrorOut}`` 선언의 일치를 검증하고, 선택 API
module의 수동 OpenAPI 후처리를 차단한다.

종료코드: 0=clean, 1=사용/분석 오류, 2=blocker.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path


ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
HTTP_STATUS_CONSTANT_RE = re.compile(r"^HTTP_([1-5]\d\d)(?:_|$)")
HTTP_METHODS = {"delete", "get", "head", "options", "patch", "post", "put"}
ROOT_API_CONSTRUCTORS = {"ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"}
COMMON_ERROR_MODULE = "common.ninja.response.error_out"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.ErrorOut"

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

ROUTER_INSTANCE = "@ninja-router-instance"
API_TYPE_PREFIX = "@ninja-api-type:"
API_RECEIVER = "@selected-api-receiver"


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
    status: StatusSpec | None = None


@dataclass(frozen=True)
class ErrorInstance:
    symbol: ErrorSymbol
    direct_status: int | None = None


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
    relative_path: Path
    lineno: int
    category: str
    detail: str

    def render(self) -> str:
        return f"  - {self.relative_path}:{self.lineno}  {self.detail}"


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--error-profile", action="append")
    parser.add_argument("--scope", action="append")
    parser.add_argument("--api-module", action="append")
    parser.add_argument("--controller-module", action="append", default=[])
    parser.add_argument("--scope-bc", action="append", default=[])
    parser.add_argument("--error-bc", action="append", default=[])
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
    if explicit and not controller_modules:
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
    if config.error_bcs:
        required.append(Path("common/ninja/response/error_out.py"))
        required.extend(
            Path(f"application/{bc}/presentation_layer/schema/error_out.py")
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


def _legacy_is_production_path(relative_path: Path) -> bool:
    return (
        relative_path.suffix == ".py"
        and "presentation_layer" in relative_path.parts
        and not set(relative_path.parts) & CODE_SKIP_DIRS
        and not set(relative_path.parts) & TEST_DIR_NAMES
        and not relative_path.name.startswith("test_")
        and relative_path.name not in {"test.py", "tests.py", "conftest.py"}
    )


def _legacy_is_ignored_untracked(root: Path, relative_path: Path) -> bool:
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


def _legacy_presentation_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*.py"):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if not _legacy_is_production_path(relative):
            continue
        if _legacy_is_ignored_untracked(root, relative):
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


def _legacy_response_statuses(
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


def _legacy_openapi_extra_statuses(
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


def _legacy_scan(source: str) -> list[str]:
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
            _legacy_openapi_extra_statuses(node) - _legacy_response_statuses(node)
        )
        if missing:
            findings.append(
                f"operation '{node.name}' "
                f"(오류 {missing} 가 openapi_extra 에만·response= 누락)"
            )
    return findings


def _legacy_is_new_or_modified(root: Path, file_path: Path) -> bool:
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


def _legacy_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for path in _legacy_presentation_files(root):
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = _legacy_scan(source)
        if hits and _legacy_is_new_or_modified(root, path):
            findings.append(f"  - {path.relative_to(root)}: {'; '.join(hits)}")
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
    return ".".join((bound, *rest))


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
        if isinstance(value, ast.Call) and recognize_router:
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
    module = ".".join(parsed.relative_path.with_suffix("").parts)
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


def _status_from_expression(
    expression: ast.AST,
    bindings: dict[str, str],
) -> int | None:
    literal = _literal_status(expression)
    if literal is not None:
        return literal
    resolved = _resolve_expression(expression, bindings)
    if resolved is None:
        return None
    if resolved.startswith("ninja.status.") or resolved.startswith("ninja_extra.status."):
        name = resolved.rsplit(".", 1)[-1]
        match = HTTP_STATUS_CONSTANT_RE.match(name)
        return int(match.group(1)) if match is not None else None
    if resolved.startswith("http.HTTPStatus."):
        name = resolved.rsplit(".", 1)[-1]
        member = HTTPStatus.__members__.get(name)
        return int(member) if member is not None else None
    return None


def _class_status_spec(
    class_node: ast.ClassDef,
    bindings: dict[str, str],
    relative_path: Path,
) -> StatusSpec:
    for statement in class_node.body:
        if isinstance(statement, ast.AnnAssign):
            if isinstance(statement.target, ast.Name) and statement.target.id == "status":
                return StatusSpec(statement.value, dict(bindings), relative_path)
        elif isinstance(statement, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "status"
                for target in statement.targets
            ):
                return StatusSpec(statement.value, dict(bindings), relative_path)
    return StatusSpec(None, dict(bindings), relative_path)


def _error_catalog(
    config: Config, parsed_by_path: dict[Path, ParsedSource]
) -> dict[str, ErrorSymbol]:
    if not config.error_bcs:
        return {}
    common = parsed_by_path[Path("common/ninja/response/error_out.py")]
    common_class = next(
        (
            node
            for node in common.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ErrorOut"
        ),
        None,
    )
    if common_class is None:
        raise UsageError("canonical common ErrorOut provenance 분석 불능")
    catalog: dict[str, ErrorSymbol] = {
        COMMON_ERROR_OUT: ErrorSymbol(COMMON_ERROR_OUT, None, "common")
    }

    for bc in config.error_bcs:
        relative = Path(f"application/{bc}/presentation_layer/schema/error_out.py")
        parsed = parsed_by_path[relative]
        before = _module_symbol_bindings_before(parsed)
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
                f"canonical BC ErrorOut provenance 분석 불능: {relative}"
            )
        base_node = base_nodes[0]
        base_path = f"{module}.{base_node.name}"
        catalog[base_path] = ErrorSymbol(base_path, bc, "base")
        for node in parsed.tree.body:
            if not isinstance(node, ast.ClassDef) or node is base_node:
                continue
            bindings = before[id(node)]
            bases = {_resolve_expression(base, bindings) for base in node.bases}
            if base_path not in bases:
                continue
            full_path = f"{module}.{node.name}"
            catalog[full_path] = ErrorSymbol(
                full_path,
                bc,
                "concrete",
                _class_status_spec(node, bindings, relative),
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
        if separator and method in HTTP_METHODS and owner in {
            ROUTER_INSTANCE,
            "ninja_extra.route",
        }:
            return decorator
    return None


def _collect_operations(parsed: ParsedSource) -> list[Operation]:
    operations: list[Operation] = []
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    final_module_bindings: dict[str, str] = {}
    for statement in parsed.tree.body:
        _advance_bindings(
            statement,
            parsed.relative_path,
            final_module_bindings,
            recognize_router=True,
            annotations_evaluated=annotations_evaluated,
        )

    def visit_block(
        statements: list[ast.stmt],
        incoming: dict[str, str],
        owners: tuple[str, ...],
    ) -> None:
        bindings = dict(incoming)
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorator = _operation_decorator(statement, bindings)
                if decorator is not None:
                    operations.append(
                        Operation(
                            parsed.relative_path,
                            owners,
                            statement,
                            decorator,
                            dict(bindings),
                            dict(final_module_bindings),
                            annotations_evaluated,
                        )
                    )
                for name in _evaluated_named_expression_names(
                    statement, annotations_evaluated=annotations_evaluated
                ):
                    bindings.pop(name, None)
                bindings.pop(statement.name, None)
                continue
            if isinstance(statement, ast.ClassDef):
                class_bindings = dict(bindings)
                for name in _evaluated_named_expression_names(
                    statement, annotations_evaluated=annotations_evaluated
                ):
                    bindings.pop(name, None)
                    class_bindings.pop(name, None)
                visit_block(
                    statement.body,
                    class_bindings,
                    (*owners, statement.name),
                )
                bindings.pop(statement.name, None)
                continue
            if isinstance(statement, (ast.If, ast.While)):
                visit_block(statement.body, dict(bindings), owners)
                visit_block(statement.orelse, dict(bindings), owners)
            elif isinstance(statement, (ast.For, ast.AsyncFor)):
                branch = dict(bindings)
                for name in _target_names(statement.target):
                    branch.pop(name, None)
                visit_block(statement.body, branch, owners)
                visit_block(statement.orelse, dict(bindings), owners)
            elif isinstance(statement, ast.Try):
                visit_block(statement.body, dict(bindings), owners)
                visit_block(statement.orelse, dict(bindings), owners)
                visit_block(statement.finalbody, dict(bindings), owners)
                for handler in statement.handlers:
                    branch = dict(bindings)
                    if handler.name:
                        branch.pop(handler.name, None)
                    visit_block(handler.body, branch, owners)
            _advance_bindings(
                statement,
                parsed.relative_path,
                bindings,
                recognize_router=True,
                annotations_evaluated=annotations_evaluated,
            )

    visit_block(parsed.tree.body, {}, ())
    return operations


def _resolved_error_status(instance: ErrorInstance) -> int:
    if instance.direct_status is not None:
        return instance.direct_status
    spec = instance.symbol.status
    if spec is None or spec.expression is None:
        raise UsageError(
            f"returned error status provenance 분석 불능: {instance.symbol.full_path}"
        )
    status = _status_from_expression(spec.expression, spec.bindings)
    if status is None:
        raise UsageError(
            f"returned error status provenance 분석 불능: {instance.symbol.full_path}"
        )
    return status


def _constructed_error(
    value: ast.expr,
    bindings: dict[str, str],
    catalog: dict[str, ErrorSymbol],
) -> ErrorInstance | None:
    if not isinstance(value, ast.Call):
        return None
    resolved = _resolve_expression(value.func, bindings)
    symbol = catalog.get(resolved or "")
    if symbol is None or symbol.kind not in {"base", "concrete"}:
        return None
    if symbol.kind == "concrete":
        return ErrorInstance(symbol)
    status_keyword = next(
        (keyword.value for keyword in value.keywords if keyword.arg == "status"), None
    )
    if status_keyword is None:
        return ErrorInstance(symbol)
    status = _status_from_expression(status_keyword, bindings)
    if status is None:
        raise UsageError(
            f"direct BC ErrorOut status provenance 분석 불능: {resolved}"
        )
    return ErrorInstance(symbol, status)


def _status_return_instance(
    statement: ast.Return,
    bindings: dict[str, str],
    instances: dict[str, ErrorInstance],
) -> ErrorInstance | None:
    value = statement.value
    if not isinstance(value, ast.Call):
        return None
    if _resolve_expression(value.func, bindings) != "ninja.Status":
        return None
    if len(value.args) < 2:
        return None
    status_arg, body_arg = value.args[:2]
    if not (
        isinstance(status_arg, ast.Attribute)
        and status_arg.attr == "status"
        and isinstance(status_arg.value, ast.Name)
        and isinstance(body_arg, ast.Name)
        and status_arg.value.id == body_arg.id
    ):
        return None
    return instances.get(body_arg.id)


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

    def visit_block(
        statements: list[ast.stmt],
        incoming_bindings: dict[str, str],
        incoming_instances: dict[str, ErrorInstance],
    ) -> None:
        bindings = dict(incoming_bindings)
        instances = dict(incoming_instances)
        for statement in statements:
            if isinstance(statement, ast.Return):
                instance = _status_return_instance(statement, bindings, instances)
                if instance is not None and instance.symbol.bc is not None:
                    status = _resolved_error_status(instance)
                    requirements.setdefault(status, set()).add(instance.symbol.bc)
                continue
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                bindings.pop(statement.name, None)
                instances.pop(statement.name, None)
                continue
            if isinstance(statement, (ast.If, ast.While)):
                visit_block(statement.body, bindings, instances)
                visit_block(statement.orelse, bindings, instances)
                continue
            if isinstance(statement, (ast.For, ast.AsyncFor)):
                branch_bindings = dict(bindings)
                branch_instances = dict(instances)
                for name in _target_names(statement.target):
                    branch_bindings.pop(name, None)
                    branch_instances.pop(name, None)
                visit_block(statement.body, branch_bindings, branch_instances)
                visit_block(statement.orelse, bindings, instances)
                continue
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                branch_bindings = dict(bindings)
                branch_instances = dict(instances)
                for item in statement.items:
                    if item.optional_vars is not None:
                        for name in _target_names(item.optional_vars):
                            branch_bindings.pop(name, None)
                            branch_instances.pop(name, None)
                visit_block(statement.body, branch_bindings, branch_instances)
                continue
            if isinstance(statement, ast.Try):
                visit_block(statement.body, bindings, instances)
                visit_block(statement.orelse, bindings, instances)
                visit_block(statement.finalbody, bindings, instances)
                for handler in statement.handlers:
                    branch_bindings = dict(bindings)
                    branch_instances = dict(instances)
                    if handler.name:
                        branch_bindings.pop(handler.name, None)
                        branch_instances.pop(handler.name, None)
                    visit_block(handler.body, branch_bindings, branch_instances)
                continue

            targets, value = _assigned_value(statement)
            names = {name for target in targets for name in _target_names(target)}
            instance = (
                _constructed_error(value, bindings, catalog)
                if value is not None
                else None
            )
            _advance_bindings(
                statement,
                operation.relative_path,
                bindings,
                annotations_evaluated=annotations_evaluated,
            )
            for name in names | _direct_bound_names(statement):
                instances.pop(name, None)
            if len(names) == 1 and instance is not None:
                instances[next(iter(names))] = instance

    visit_block(operation.function.body, initial_bindings, {})
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
                raise UsageError(f"required BC ErrorOut base 분석 불능: {bc}")
            if not isinstance(schema, ErrorSymbol) or schema.full_path != expected.full_path:
                shown = schema.full_path if isinstance(schema, ErrorSymbol) else schema
                findings.append(
                    Finding(
                        operation.relative_path,
                        operation.decorator.lineno,
                        "wrong-response-schema",
                        f"{operation.identity} status {status}는 "
                        f"{expected.full_path} 필요 (현재 {shown})",
                    )
                )

    for status, value in sorted(final_values.items()):
        if status in uncertain or not 400 <= status <= 599:
            continue
        schema = _schema_symbol(value, operation.bindings, catalog)
        if not isinstance(schema, ErrorSymbol) or schema.kind != "base" or schema.bc is None:
            continue
        if schema.bc not in requirements.get(status, set()):
            findings.append(
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "extra-bc-advertisement",
                    f"{operation.identity} status {status}의 {schema.full_path} "
                    "선언에 직접 BC 오류 반환 없음",
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
        statuses = sorted(
            status
            for status_key in value.keys
            if status_key is not None
            for status in [_literal_status(status_key)]
            if status is not None and 400 <= status <= 599
        )
        if statuses:
            return [
                Finding(
                    operation.relative_path,
                    operation.decorator.lineno,
                    "openapi-extra",
                    f"{operation.identity} 오류 responses {statuses}를 "
                    "openapi_extra로 수동 선언",
                )
            ]
    return []


def _api_expression_has_schema_call(
    expression: ast.AST,
    bindings: dict[str, str],
) -> bool:
    for node in ast.walk(expression):
        if isinstance(node, ast.Lambda) and node is not expression:
            continue
        if not isinstance(node, ast.Call):
            continue
        resolved = _resolve_expression(node.func, bindings)
        if resolved == f"{API_RECEIVER}.get_openapi_schema":
            return True
    return False


def _api_module_findings(parsed: ParsedSource) -> list[Finding]:
    findings: list[Finding] = []
    bindings: dict[str, str] = {}
    receiver_events = 0
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    deferred_functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

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
        for name in arguments:
            local.pop(name, None)

        def visit_block(statements: list[ast.stmt], incoming: dict[str, str]) -> None:
            current = dict(incoming)
            for statement in statements:
                if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    current.pop(statement.name, None)
                    continue
                if _api_expression_has_schema_call(statement, current):
                    findings.append(
                        Finding(
                            parsed.relative_path,
                            statement.lineno,
                            "openapi-postprocess",
                            "선택 API receiver의 get_openapi_schema 직접 호출/후처리",
                        )
                    )
                if isinstance(statement, (ast.If, ast.While)):
                    visit_block(statement.body, current)
                    visit_block(statement.orelse, current)
                elif isinstance(statement, ast.Try):
                    visit_block(statement.body, current)
                    visit_block(statement.orelse, current)
                    visit_block(statement.finalbody, current)
                    for handler in statement.handlers:
                        visit_block(handler.body, current)
                _advance_bindings(
                    statement,
                    parsed.relative_path,
                    current,
                    annotations_evaluated=annotations_evaluated,
                )

        visit_block(function.body, local)

    for statement in parsed.tree.body:
        current = dict(bindings)
        if isinstance(statement, ast.ClassDef):
            bases = {_resolve_expression(base, current) for base in statement.bases}
            api_subclass = any(
                base in ROOT_API_CONSTRUCTORS
                or (base is not None and base.startswith(API_TYPE_PREFIX))
                for base in bases
            )
            if api_subclass:
                for member in statement.body:
                    if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    deferred_functions.append(member)
                    if member.name == "get_openapi_schema":
                        findings.append(
                            Finding(
                                parsed.relative_path,
                                member.lineno,
                                "openapi-override",
                                f"Ninja API subclass {statement.name}의 "
                                "get_openapi_schema override",
                            )
                        )
                derived_class = f"{API_TYPE_PREFIX}{statement.name}"
            else:
                derived_class = None
            for name in _evaluated_named_expression_names(
                statement, annotations_evaluated=annotations_evaluated
            ):
                bindings.pop(name, None)
            bindings.pop(statement.name, None)
            if derived_class is not None:
                bindings[statement.name] = derived_class
            continue

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            deferred_functions.append(statement)
            for name in _evaluated_named_expression_names(
                statement, annotations_evaluated=annotations_evaluated
            ):
                bindings.pop(name, None)
            bindings.pop(statement.name, None)
            continue

        if _api_expression_has_schema_call(statement, current):
            findings.append(
                Finding(
                    parsed.relative_path,
                    statement.lineno,
                    "openapi-postprocess",
                    "선택 API receiver의 get_openapi_schema 직접 호출/후처리",
                )
            )
        for node in ast.walk(statement):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets, _ = _assigned_value(node)
            for target in targets:
                if not isinstance(target, ast.Attribute) or target.attr != "get_openapi_schema":
                    continue
                if _resolve_expression(target.value, current) == API_RECEIVER:
                    findings.append(
                        Finding(
                            parsed.relative_path,
                            target.lineno,
                            "openapi-monkeypatch",
                            "선택 API receiver의 get_openapi_schema assignment/monkeypatch",
                        )
                    )

        targets, value = _assigned_value(statement)
        names = {name for target in targets for name in _target_names(target)}
        derived: str | None = None
        if value is not None:
            if isinstance(value, ast.Call):
                constructor = _resolve_expression(value.func, current)
                if constructor in ROOT_API_CONSTRUCTORS or (
                    constructor is not None and constructor.startswith(API_TYPE_PREFIX)
                ):
                    derived = API_RECEIVER
                    receiver_events += 1
            if derived is None and _resolve_expression(value, current) == API_RECEIVER:
                derived = API_RECEIVER
        if _update_imports(statement, parsed.relative_path, bindings):
            continue
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

    final_receivers = {name for name, value in bindings.items() if value == API_RECEIVER}
    if receiver_events != 1 or not final_receivers:
        raise UsageError(
            "selected API receiver provenance 분석 불능: proven constructor event와 "
            "final receiver 필요"
        )
    for function in deferred_functions:
        scan_function(function, bindings)
    return findings


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


def _code_findings(config: Config) -> list[Finding]:
    parsed_by_path = _parse_code_sources(config)
    catalog = _error_catalog(config, parsed_by_path)
    api = parsed_by_path[Path(config.api_module or "")]
    findings = _api_module_findings(api)
    controller_operations: list[Operation] = []
    for raw in config.controller_modules:
        controller_operations.extend(_collect_operations(parsed_by_path[Path(raw)]))
    for operation in controller_operations:
        requirements = _operation_requirements(operation, catalog)
        findings.extend(_response_findings(operation, requirements, catalog))
        findings.extend(_openapi_extra_findings(operation))
    return _deduplicate_findings(findings)


def _print_legacy_findings(findings: list[str]) -> None:
    print(
        "[check-openapi-error-declaration] BLOCKER — 오류 status 를 openapi_extra 로만 "
        "선언하고 "
        "response={...} 엔 누락함(ninja 가 타입으로 미인지 = 선언 계약 밖):"
    )
    for finding in findings:
        print(finding)
    print(
        "  근거: implementation-django-ninja §2.2 line111. 가능한 모든 status"
        "(404·409·422 등)를 response={...} 에 선언한다 — "
        "openapi_extra/get_openapi_schema 수동 선언은 Swagger 가시성만 달성하고 "
        "ninja 응답 타입엔 안 들어간다. 오류 schema 를 response= 로 옮겨라. "
        "설계로 반송하라."
    )


def _print_code_findings(findings: list[Finding]) -> None:
    print(
        "[check-openapi-error-declaration] BLOCKER — 직접 반환 BC 오류와 response= "
        "ErrorOut 계약 불일치 또는 수동 OpenAPI 후처리:"
    )
    for finding in findings:
        print(finding.render())
    print(
        "  조치: 각 직접 반환 status를 같은 BC의 <Bc>ErrorOut base로 선언하고, "
        "직접 반환하지 않는 BC 오류 광고와 "
        "openapi_extra/get_openapi_schema 후처리를 "
        "제거한다."
    )


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
        if config.profile == "dddjango-code-json":
            findings = _code_findings(config)
            if findings:
                _print_code_findings(findings)
                return 2
            return 0
        legacy = _legacy_findings(config.root)
        if legacy:
            _print_legacy_findings(legacy)
            return 2
        return 0
    except UsageError as exc:
        print(f"[check-openapi-error-declaration] 사용 오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
