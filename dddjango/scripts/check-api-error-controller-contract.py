#!/usr/bin/env python3
"""Enforce direct controller-owned code-profile error mapping.

The checker is deliberately profile- and source-selected.  ``auto`` and
``preserve-established`` validate their generic CLI/source contract and add no
new error-mapping semantics.  ``dddjango-code-json`` analyzes only selected
controllers owned by an ``error-bc``, every declared error BC's canonical
ErrorOut module, and the same-owner presentation modules imported directly by
those controllers.

Exit codes: 0=clean/N/A/help, 2=contract blocker, 1=usage or analysis error.
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
from pathlib import Path
from typing import Iterator


ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
TEST_DIR_NAMES = {"test", "tests"}
CODE_SKIP_DIRS = {
    ".venv",
    "venv",
    "site-packages",
    "node_modules",
    ".git",
    "__pycache__",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "migrations",
    "generated",
}
COMMON_ERROR_PATH = Path("common/ninja/response/error_out.py")
COMMON_ERROR_MODULE = "common.ninja.response.error_out"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.ErrorOut"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
ROUTER_CONSTRUCTORS = {"ninja.Router"}
HANDLER_CONSTRUCTORS = {
    "ninja.Router",
    "ninja.NinjaAPI",
    "ninja_extra.NinjaExtraAPI",
}
NINJA_STATUS = "ninja.Status"
HTTP_RESPONSE = "django.http.HttpResponse"
RAW_RESPONSE_TYPES = {
    "django.http.HttpResponse",
    "django.http.JsonResponse",
    "django.http.FileResponse",
    "django.http.StreamingHttpResponse",
    "ninja.responses.Response",
}
TRY_STAR = getattr(ast, "TryStar", None)
MATCH = getattr(ast, "Match", None)
MATCH_AS = getattr(ast, "MatchAs", None)
MATCH_STAR = getattr(ast, "MatchStar", None)
MATCH_MAPPING = getattr(ast, "MatchMapping", None)


class UsageError(Exception):
    """CLI, inventory, selected-source, or required-provenance failure."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True)
class Config:
    root: Path
    profile: str
    scope: str | None
    api_module: Path | None
    controller_modules: tuple[Path, ...]
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
class Binding:
    origin: str
    kind: str


VALUE_BINDING = Binding("<value>", "value")
AMBIGUOUS_BINDING = Binding("<ambiguous-framework>", "ambiguous")


@dataclass(frozen=True)
class BindingTimeline:
    before: dict[int, dict[str, Binding]]
    final: dict[str, Binding]


@dataclass(frozen=True)
class ErrorLanguage:
    common_fields: frozenset[str]
    bases_by_bc: dict[str, str]
    prepared_by_bc: dict[str, frozenset[str]]

    @property
    def all_types(self) -> frozenset[str]:
        values = {COMMON_ERROR_OUT, *self.bases_by_bc.values()}
        for prepared in self.prepared_by_bc.values():
            values.update(prepared)
        return frozenset(values)


@dataclass
class Operation:
    parsed: ParsedSource
    node: ast.FunctionDef | ast.AsyncFunctionDef
    owner_bc: str
    identity: str
    definition_bindings: dict[str, Binding]
    annotation_bindings: dict[str, Binding]
    body_bindings: dict[str, Binding]
    local_names: set[str]
    response_parameters: set[str]


@dataclass(frozen=True)
class Finding:
    path: Path
    lineno: int
    category: str
    shown: str

    def render(self) -> str:
        return f"  - {self.path}:{self.lineno}  {self.category}: {self.shown}"


@dataclass
class HelperFacts:
    has_prepared: bool = False
    has_error_constructor: bool = False
    has_exception_test: bool = False
    serializer_node: ast.AST | None = None


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
    if len(actual) > 1:
        issues.append(f"단일 인자 중복: {option}")
    return actual[0] if actual else None


def _unique(option: str, values: list[str], issues: list[str]) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        issues.append(f"반복 인자 중복: {option}")
    return tuple(values)


def _source_path(option: str, raw: str, issues: list[str]) -> Path | None:
    path = Path(raw)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != raw
        or "/" not in raw
        or path.suffix != ".py"
    ):
        issues.append(f"잘못된 source path: {option}={raw}")
        return None
    return path


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
        "--error-profile", namespace.error_profile, required=True, issues=issues
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
    if profile is not None and profile not in ERROR_PROFILES:
        issues.append(f"지원하지 않는 --error-profile: {profile}")
    if profile == "auto" and selectors_present:
        issues.append("auto profile에는 selector를 전달하지 않음")

    explicit = profile in {"dddjango-code-json", "preserve-established"}
    scope = _one("--scope", namespace.scope, required=explicit, issues=issues)
    api_raw = _one(
        "--api-module", namespace.api_module, required=explicit, issues=issues
    )
    controller_raw = _unique(
        "--controller-module", namespace.controller_module, issues
    )
    scope_bcs = _unique("--scope-bc", namespace.scope_bc, issues)
    error_bcs = _unique("--error-bc", namespace.error_bc, issues)
    if explicit and not controller_raw:
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

    lexical: list[tuple[str, Path]] = []
    if api_raw is not None:
        path = _source_path("--api-module", api_raw, issues)
        if path is not None:
            lexical.append(("--api-module", path))
    for raw in controller_raw:
        path = _source_path("--controller-module", raw, issues)
        if path is not None:
            lexical.append(("--controller-module", path))

    resolved: list[tuple[str, Path, Path]] = []
    for role, relative in lexical:
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
        except ValueError:
            issues.append(f"root/symlink 탈출: {role}={relative.as_posix()}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(f"source path resolve 불능: {role}={relative} ({exc})")
            continue
        resolved.append((role, relative, candidate))
    for index, (left_role, left_rel, left_path) in enumerate(resolved):
        for right_role, right_rel, right_path in resolved[index + 1 :]:
            if left_path == right_path:
                issues.append(
                    "선택 source role/resolved path overlap: "
                    f"{left_role}={left_rel}, {right_role}={right_rel}"
                )

    if issues:
        raise UsageError("; ".join(issues))
    api_module = Path(api_raw) if api_raw is not None else None
    return Config(
        root=root,
        profile=profile or "",
        scope=scope,
        api_module=api_module,
        controller_modules=tuple(Path(raw) for raw in controller_raw),
        scope_bcs=scope_bcs,
        error_bcs=error_bcs,
    )


def _is_production_path(relative_path: Path) -> bool:
    parts = relative_path.parts
    return (
        relative_path.suffix == ".py"
        and not set(parts) & CODE_SKIP_DIRS
        and not set(parts) & TEST_DIR_NAMES
        and not relative_path.name.startswith("test_")
        and not relative_path.name.endswith("_test.py")
        and relative_path.name not in {"test.py", "tests.py", "conftest.py"}
    )


def _filesystem_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    errors: list[str] = []

    def record_error(exc: OSError) -> None:
        errors.append(str(exc))

    for directory, names, filenames in os.walk(
        root, topdown=True, followlinks=False, onerror=record_error
    ):
        relative_dir = Path(directory).relative_to(root)
        names[:] = sorted(
            name
            for name in names
            if not set((*relative_dir.parts, name)) & CODE_SKIP_DIRS
            and name not in TEST_DIR_NAMES
        )
        for filename in sorted(filenames):
            relative = relative_dir / filename
            if _is_production_path(relative):
                paths.append(relative)
    if errors:
        raise UsageError(f"production inventory 탐색 불능: {'; '.join(sorted(errors))}")
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


def _production_inventory(root: Path) -> CodeInventory:
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
        return CodeInventory(_filesystem_paths(root), None)
    if probe.stdout.strip() != "true":
        return CodeInventory(_filesystem_paths(root), None)

    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise UsageError(f"Git worktree root 분석 불능: {exc}") from exc
    if top.returncode != 0:
        raise UsageError(
            f"Git worktree root 분석 불능: {top.stderr.strip() or top.stdout.strip()}"
        )
    try:
        git_root = Path(top.stdout.strip()).resolve()
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
    paths: list[Path] = []
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
        if _is_production_path(target_relative):
            paths.append(target_relative)
    if len(paths) != len(set(paths)):
        raise UsageError("Git production inventory에 중복 경로가 있음")
    return CodeInventory(tuple(sorted(paths, key=Path.as_posix)), git_root)


def _load_sources(
    root: Path, source_paths: set[Path]
) -> tuple[dict[Path, ParsedSource], list[str]]:
    parsed: dict[Path, ParsedSource] = {}
    issues: list[str] = []
    resolved_paths: dict[Path, Path] = {}
    for relative in sorted(source_paths, key=Path.as_posix):
        lexical = root / relative
        try:
            resolved = lexical.resolve()
            resolved.relative_to(root)
        except ValueError:
            issues.append(f"production source root/symlink 탈출: {relative}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(f"production source resolve 불능: {relative} ({exc})")
            continue
        previous = resolved_paths.get(resolved)
        if previous is not None and previous != relative:
            issues.append(f"production source resolved path 중복: {previous}, {relative}")
            continue
        resolved_paths[resolved] = relative
        try:
            if not resolved.is_file():
                issues.append(f"production source 없음: {relative}")
                continue
            source = resolved.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative.as_posix())
        except (OSError, UnicodeError, SyntaxError) as exc:
            issues.append(f"production source 분석 불능: {relative} ({exc})")
            continue
        parsed[relative] = ParsedSource(relative, source, tree)
    return parsed, issues


def _module_name(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _absolute_from_module(path: Path, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module
    package = list(path.parent.parts)
    drop = node.level - 1
    if drop > len(package):
        return None
    if drop:
        package = package[:-drop]
    if node.module:
        package.extend(node.module.split("."))
    return ".".join(package) or None


def _expression_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _expression_name(node.value)
        if owner is not None:
            return f"{owner}.{node.attr}"
    return None


def _target_names(target: ast.AST) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for item in target.elts for name in _target_names(item)}
    return set()


def _statement_bound_names(node: ast.stmt) -> set[str]:
    if isinstance(node, ast.Import):
        return {alias.asname or alias.name.split(".", 1)[0] for alias in node.names}
    if isinstance(node, ast.ImportFrom):
        return {alias.asname or alias.name for alias in node.names if alias.name != "*"}
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return {node.name}
    if isinstance(node, ast.Assign):
        return {name for target in node.targets for name in _target_names(target)}
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return _target_names(node.target)
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _target_names(node.target)
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return {
            name
            for item in node.items
            if item.optional_vars is not None
            for name in _target_names(item.optional_vars)
        }
    if isinstance(node, ast.Delete):
        return {name for target in node.targets for name in _target_names(target)}
    return set()


def _import_bindings(path: Path, node: ast.stmt) -> dict[str, Binding]:
    bindings: dict[str, Binding] = {}
    if isinstance(node, ast.Import):
        for alias in node.names:
            local = alias.asname or alias.name.split(".", 1)[0]
            origin = alias.name if alias.asname else local
            bindings[local] = Binding(origin, "module_import")
    elif isinstance(node, ast.ImportFrom):
        module = _absolute_from_module(path, node)
        if module is not None:
            for alias in node.names:
                if alias.name != "*":
                    bindings[alias.asname or alias.name] = Binding(
                        f"{module}.{alias.name}", "symbol_import"
                    )
    return bindings


def _resolve_binding(
    node: ast.AST, bindings: dict[str, Binding], *, direct_symbol: bool = False
) -> Binding | None:
    if direct_symbol and not isinstance(node, ast.Name):
        return None
    dotted = _expression_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    binding = bindings.get(first)
    if binding is None:
        return None
    if direct_symbol and binding.kind != "symbol_import":
        return None
    origin = ".".join((binding.origin, *rest)) if rest else binding.origin
    return Binding(origin, binding.kind)


def _assignment_binding(
    statement: ast.Assign | ast.AnnAssign,
    bindings: dict[str, Binding],
) -> Binding | None:
    value = statement.value
    if value is None or not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
        return None
    constructor = _resolve_binding(value.func, bindings, direct_symbol=True)
    if constructor is None or constructor.origin not in HANDLER_CONSTRUCTORS:
        return None
    return Binding(constructor.origin, "framework_instance")


def _assignment_state(
    statement: ast.Assign | ast.AnnAssign,
    bindings: dict[str, Binding],
) -> Binding:
    framework = _assignment_binding(statement, bindings)
    if framework is not None:
        return framework
    value = statement.value
    if isinstance(value, ast.Name):
        return bindings.get(value.id, VALUE_BINDING)
    return VALUE_BINDING


def _join_binding_states(states: list[dict[str, Binding]]) -> dict[str, Binding]:
    """Join the small absent/known/ambiguous binding lattice."""
    if not states:
        return {}
    joined: dict[str, Binding] = {}
    names = {name for state in states for name in state}
    for name in names:
        values = [state.get(name) for state in states]
        if all(value == values[0] for value in values):
            if values[0] is not None:
                joined[name] = values[0]
            continue
        present = [value for value in values if value is not None]
        if present and all(
            value.kind == "framework_instance"
            and value.origin in HANDLER_CONSTRUCTORS
            for value in present
        ) and len(present) == len(values):
            joined[name] = Binding("<framework-handler>", "framework_instance")
        elif any(
            value.kind in {"framework_instance", "ambiguous"}
            for value in present
        ):
            joined[name] = AMBIGUOUS_BINDING
        else:
            joined[name] = VALUE_BINDING
    return joined


def _advance_binding_state(
    parsed: ParsedSource,
    statement: ast.stmt,
    bindings: dict[str, Binding],
    *,
    definition_prefix: str,
) -> None:
    imported = _import_bindings(parsed.relative_path, statement)
    if imported:
        bindings.update(imported)
        return
    assigned = (
        _assignment_state(statement, bindings)
        if isinstance(statement, (ast.Assign, ast.AnnAssign))
        else None
    )
    names = _statement_bound_names(statement)
    for name in names:
        bindings.pop(name, None)
    if assigned is not None:
        for name in names:
            bindings[name] = assigned
    elif isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        bindings[statement.name] = Binding(
            f"{definition_prefix}.{statement.name}", "local_definition"
        )


def _literal_truth(node: ast.AST) -> bool | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _binding_branch_exit(
    parsed: ParsedSource,
    statements: list[ast.stmt],
    incoming: dict[str, Binding],
    *,
    definition_prefix: str,
) -> dict[str, Binding]:
    bindings = dict(incoming)
    for statement in statements:
        if isinstance(statement, ast.If):
            truth = _literal_truth(statement.test)
            if truth is True:
                bindings = _binding_branch_exit(
                    parsed,
                    statement.body,
                    bindings,
                    definition_prefix=definition_prefix,
                )
            elif truth is False:
                bindings = _binding_branch_exit(
                    parsed,
                    statement.orelse,
                    bindings,
                    definition_prefix=definition_prefix,
                )
            else:
                bindings = _join_binding_states(
                    [
                        _binding_branch_exit(
                            parsed,
                            statement.body,
                            bindings,
                            definition_prefix=definition_prefix,
                        ),
                        _binding_branch_exit(
                            parsed,
                            statement.orelse,
                            bindings,
                            definition_prefix=definition_prefix,
                        ),
                    ]
                )
            continue
        _advance_binding_state(
            parsed,
            statement,
            bindings,
            definition_prefix=definition_prefix,
        )
    return bindings


def _binding_timeline(parsed: ParsedSource) -> BindingTimeline:
    bindings: dict[str, Binding] = {}
    before: dict[int, dict[str, Binding]] = {}
    module = _module_name(parsed.relative_path)
    for node in parsed.tree.body:
        before[id(node)] = dict(bindings)
        if isinstance(node, ast.If):
            bindings = _binding_branch_exit(
                parsed, [node], bindings, definition_prefix=module
            )
        else:
            _advance_binding_state(
                parsed, node, bindings, definition_prefix=module
            )
    return BindingTimeline(before, dict(bindings))


def _class_body_bindings(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, Binding],
) -> dict[int, dict[str, Binding]]:
    bindings = dict(outer)
    before: dict[int, dict[str, Binding]] = {}
    module = _module_name(parsed.relative_path)
    for statement in node.body:
        before[id(statement)] = dict(bindings)
        imported = _import_bindings(parsed.relative_path, statement)
        if imported:
            bindings.update(imported)
            continue
        assigned = (
            _assignment_binding(statement, bindings)
            if isinstance(statement, (ast.Assign, ast.AnnAssign))
            else None
        )
        names = _statement_bound_names(statement)
        for name in names:
            bindings.pop(name, None)
        if assigned is not None:
            for name in names:
                bindings[name] = assigned
        elif isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            bindings[statement.name] = Binding(
                f"{module}.{node.name}.{statement.name}", "local_definition"
            )
    return before


def _future_annotations(parsed: ParsedSource) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in parsed.tree.body
    )


def _owner_bc(path: Path, scope_bcs: set[str]) -> str | None:
    parts = path.parts
    if (
        len(parts) >= 4
        and parts[0] == "application"
        and parts[2] == "presentation_layer"
        and parts[1] in scope_bcs
    ):
        return parts[1]
    return None


def _bc_error_path(bc: str) -> Path:
    return Path(f"application/{bc}/presentation_layer/schema/error_out.py")


def _snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _classvar(annotation: ast.AST, bindings: dict[str, Binding]) -> bool:
    target = annotation.value if isinstance(annotation, ast.Subscript) else annotation
    raw = _expression_name(target)
    resolved = _resolve_binding(target, bindings)
    return raw in {"ClassVar", "typing.ClassVar"} or (
        resolved is not None and resolved.origin == "typing.ClassVar"
    )


def _public_fields(
    parsed: ParsedSource,
    node: ast.ClassDef,
    bindings: dict[str, Binding],
) -> set[str]:
    fields: set[str] = set()
    before = _class_body_bindings(parsed, node, bindings)
    for statement in node.body:
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
            continue
        name = statement.target.id
        statement_bindings = before.get(id(statement), bindings)
        if (
            name.startswith("_")
            or name == "model_config"
            or _classvar(statement.annotation, statement_bindings)
        ):
            continue
        fields.add(name)
    return fields


def _error_language(
    parsed: dict[Path, ParsedSource], error_bcs: tuple[str, ...], analysis: list[str]
) -> ErrorLanguage:
    common = parsed.get(COMMON_ERROR_PATH)
    common_fields: set[str] = set()
    if common is None:
        analysis.append(f"필수 common ErrorOut source 없음: {COMMON_ERROR_PATH}")
    else:
        timeline = _binding_timeline(common)
        classes = [
            node
            for node in common.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "ErrorOut"
        ]
        if len(classes) != 1:
            analysis.append(f"{COMMON_ERROR_PATH}: common ErrorOut provenance 분석 불능")
        else:
            common_fields = _public_fields(
                common,
                classes[0],
                timeline.before.get(id(classes[0]), {}),
            )
            if not common_fields:
                analysis.append(f"{COMMON_ERROR_PATH}: common public field set 분석 불능")

    bases: dict[str, str] = {}
    prepared: dict[str, frozenset[str]] = {}
    for bc in error_bcs:
        path = _bc_error_path(bc)
        source = parsed.get(path)
        if source is None:
            analysis.append(f"필수 canonical ErrorOut source 없음: {path}")
            continue
        timeline = _binding_timeline(source)
        prefix = _snake_to_pascal(bc)
        base_name = f"{prefix}ErrorOut"
        module = _module_name(path)
        base_origin = f"{module}.{base_name}"
        classes = [node for node in source.tree.body if isinstance(node, ast.ClassDef)]
        base_nodes = [node for node in classes if node.name == base_name]
        if len(base_nodes) != 1:
            analysis.append(f"{path}: {base_name} provenance 분석 불능")
            continue
        bases[bc] = base_origin
        known: set[str] = set()
        for node in classes:
            if node in base_nodes:
                continue
            bindings = timeline.before.get(id(node), {})
            direct = [
                _resolve_binding(base, bindings)
                for base in node.bases
            ]
            if len(node.bases) == 1 and direct[0] is not None and direct[0].origin == base_origin:
                known.add(f"{module}.{node.name}")
            elif any((_expression_name(base) or "").rsplit(".", 1)[-1] == base_name for base in node.bases):
                analysis.append(f"{path}:{node.lineno} prepared ErrorOut base provenance 분석 불능")
        prepared[bc] = frozenset(known)
    return ErrorLanguage(frozenset(common_fields), bases, prepared)


def _append_finding(
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    parsed: ParsedSource,
    node: ast.AST,
    category: str,
) -> None:
    lineno = getattr(node, "lineno", 1)
    key = (parsed.relative_path, lineno, category)
    if key in seen:
        return
    seen.add(key)
    lines = parsed.source.splitlines()
    shown = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else category
    findings.append(Finding(parsed.relative_path, lineno, category, shown))


def _iter_lexical_nodes(statements: list[ast.stmt]) -> Iterator[ast.AST]:
    """Yield one suite's nodes without entering a nested Python scope."""
    stack: list[ast.AST] = list(reversed(statements))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        children = list(ast.iter_child_nodes(node))
        stack.extend(reversed(children))


def _definition_expressions(node: ast.AST) -> list[ast.AST]:
    """Expressions evaluated outside a newly defined function/class body."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        expressions: list[ast.AST] = [*node.decorator_list]
        expressions.extend(node.args.defaults)
        expressions.extend(
            default for default in node.args.kw_defaults if default is not None
        )
        expressions.extend(
            argument.annotation
            for argument in _function_argument_nodes(node)
            if argument.annotation is not None
        )
        if node.returns is not None:
            expressions.append(node.returns)
        expressions.extend(getattr(node, "type_params", ()))
        return expressions
    if isinstance(node, ast.Lambda):
        expressions = [*node.args.defaults]
        expressions.extend(
            default for default in node.args.kw_defaults if default is not None
        )
        return expressions
    if isinstance(node, ast.ClassDef):
        return [
            *node.decorator_list,
            *node.bases,
            *(keyword.value for keyword in node.keywords),
            *getattr(node, "type_params", ()),
        ]
    return []


def _iter_evaluated_nodes(root: ast.AST) -> Iterator[ast.AST]:
    """Walk runtime-evaluated expressions without crossing a new body scope."""
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(reversed(_definition_expressions(node)))
            continue
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _function_argument_nodes(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.arg]:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg is not None:
        arguments.append(node.args.vararg)
    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)
    return arguments


def _function_local_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names = {argument.arg for argument in _function_argument_nodes(node)}
    globals_: set[str] = set()
    nonlocals: set[str] = set()
    for candidate in _iter_lexical_nodes(node.body):
        if isinstance(candidate, ast.Global):
            globals_.update(candidate.names)
            continue
        if isinstance(candidate, ast.Nonlocal):
            nonlocals.update(candidate.names)
            continue
        if isinstance(candidate, ast.ExceptHandler) and candidate.name:
            names.add(candidate.name)
        if isinstance(candidate, ast.NamedExpr):
            names.update(_target_names(candidate.target))
        if MATCH_AS is not None and isinstance(candidate, MATCH_AS) and candidate.name:
            names.add(candidate.name)
        if (
            MATCH_STAR is not None
            and isinstance(candidate, MATCH_STAR)
            and candidate.name
        ):
            names.add(candidate.name)
        if (
            MATCH_MAPPING is not None
            and isinstance(candidate, MATCH_MAPPING)
            and candidate.rest
        ):
            names.add(candidate.rest)
        if isinstance(candidate, ast.stmt):
            names.update(_statement_bound_names(candidate))
    return names - globals_ - nonlocals


def _definition_binding(
    node: ast.AST,
    bindings: dict[str, Binding],
    *,
    expected_tail: str,
) -> Binding | None:
    if not isinstance(node, ast.Name):
        return None
    binding = bindings.get(node.id)
    if binding is None or binding.kind != "symbol_import":
        return None
    if binding.origin.rsplit(".", 1)[-1] != expected_tail:
        return None
    return binding


def _is_operation_decorator(
    decorator: ast.AST, bindings: dict[str, Binding]
) -> bool:
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return False
    if decorator.func.attr not in HTTP_METHODS or not isinstance(decorator.func.value, ast.Name):
        return False
    receiver = bindings.get(decorator.func.value.id)
    if receiver is None:
        return False
    return (
        receiver.kind == "framework_instance" and receiver.origin in ROUTER_CONSTRUCTORS
    ) or (
        receiver.kind == "symbol_import" and receiver.origin == "ninja_extra.route"
    )


def _response_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    bindings: dict[str, Binding],
) -> set[str]:
    response: set[str] = set()
    for argument in _function_argument_nodes(node):
        if argument.annotation is None:
            continue
        binding = _definition_binding(
            argument.annotation, bindings, expected_tail="HttpResponse"
        )
        if binding is not None and binding.origin == HTTP_RESPONSE:
            response.add(argument.arg)
    return response


def _discover_operations(
    parsed: ParsedSource,
    owner_bc: str,
    analysis: list[str],
) -> list[Operation]:
    timeline = _binding_timeline(parsed)
    postponed = _future_annotations(parsed)
    operations: list[Operation] = []

    def add_operation(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        definition_bindings: dict[str, Binding],
        enclosure: str,
    ) -> None:
        decorators = [
            decorator
            for decorator in node.decorator_list
            if _is_operation_decorator(decorator, definition_bindings)
        ]
        if not decorators:
            return
        annotation_bindings = timeline.final if postponed else definition_bindings
        decorator_line = min(getattr(item, "lineno", node.lineno) for item in decorators)
        operations.append(
            Operation(
                parsed=parsed,
                node=node,
                owner_bc=owner_bc,
                identity=(
                    f"{parsed.relative_path}:{enclosure}{node.name}@{decorator_line}"
                ),
                definition_bindings=dict(definition_bindings),
                annotation_bindings=dict(annotation_bindings),
                body_bindings=dict(timeline.final),
                local_names=_function_local_names(node),
                response_parameters=_response_parameters(node, annotation_bindings),
            )
        )

    for statement in parsed.tree.body:
        definition_bindings = timeline.before.get(id(statement), {})
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_operation(statement, definition_bindings, "")
        elif isinstance(statement, ast.ClassDef):
            class_before = _class_body_bindings(parsed, statement, definition_bindings)
            for member in statement.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add_operation(
                        member,
                        class_before.get(id(member), definition_bindings),
                        f"{statement.name}.",
                    )
    return operations


def _module_path_index(inventory: CodeInventory) -> dict[str, Path]:
    return {_module_name(path): path for path in inventory.relative_paths}


def _presentation_module(module: str, owner_bc: str) -> bool:
    prefix = f"application.{owner_bc}.presentation_layer"
    return module == prefix or module.startswith(f"{prefix}.")


def _one_hop_paths(
    root: Path,
    parsed: ParsedSource,
    owner_bc: str,
    module_paths: dict[str, Path],
    analysis: list[str],
) -> set[Path]:
    selected: set[Path] = set()
    package_names: dict[Path, set[str] | None] = {}

    def package_defines(path: Path, name: str) -> bool:
        if path not in package_names:
            try:
                source = (root / path).read_text(encoding="utf-8")
                tree = ast.parse(source, filename=path.as_posix())
            except (OSError, UnicodeError, SyntaxError):
                package_names[path] = None
            else:
                names: set[str] = set()
                for node in tree.body:
                    names.update(_statement_bound_names(node))
                package_names[path] = names
        names = package_names[path]
        return names is not None and name in names

    def select_module(module: str, lineno: int) -> bool:
        if not _presentation_module(module, owner_bc):
            return False
        path = module_paths.get(module)
        if path is None:
            analysis.append(
                f"{parsed.relative_path}:{lineno} local one-hop import resolve 불능: {module}"
            )
            return False
        selected.add(path)
        return True

    for statement in parsed.tree.body:
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                select_module(alias.name, statement.lineno)
            continue
        if not isinstance(statement, ast.ImportFrom):
            continue
        module = _absolute_from_module(parsed.relative_path, statement)
        if module is None or not _presentation_module(module, owner_bc):
            continue

        module_path = module_paths.get(module)
        child_selected = False
        for alias in statement.names:
            if alias.name == "*":
                continue
            child = f"{module}.{alias.name}"
            child_path = module_paths.get(child)
            if child_path is not None:
                selected.add(child_path)
                child_selected = True
                continue
            # ``from package import helper`` imports a sibling submodule when
            # helper is not an attribute.  An existing package initializer must
            # therefore not mask a missing direct one-hop target.  For a normal
            # module, the imported name is a symbol and the module itself is the
            # one-hop source.
            if module_path is None or (
                module_path.name == "__init__.py"
                and not package_defines(module_path, alias.name)
            ):
                analysis.append(
                    f"{parsed.relative_path}:{statement.lineno} "
                    f"local one-hop import resolve 불능: {child}"
                )
        if module_path is not None:
            selected.add(module_path)
        elif not child_selected and any(alias.name == "*" for alias in statement.names):
            select_module(module, statement.lineno)
    return selected


def _selected_source_plan(
    config: Config,
    inventory: CodeInventory,
) -> tuple[
    dict[Path, ParsedSource],
    dict[Path, str],
    set[Path],
    list[str],
]:
    inventory_paths = set(inventory.relative_paths)
    selected_paths = {*(config.controller_modules)}
    if config.api_module is not None:
        selected_paths.add(config.api_module)
    analysis = [
        f"선택 source가 production inventory에 없음: {path}"
        for path in sorted(selected_paths - inventory_paths, key=Path.as_posix)
    ]
    selected_parsed, load_analysis = _load_sources(config.root, selected_paths)
    analysis.extend(load_analysis)
    owners: dict[Path, str] = {}
    if config.profile == "dddjango-code-json":
        scope = set(config.scope_bcs)
        for path in config.controller_modules:
            owner = _owner_bc(path, scope)
            if owner is None:
                analysis.append(
                    f"selected controller owner 분석 불능: {path} "
                    "(application/<scope-bc>/presentation_layer/... 필요)"
                )
            else:
                owners[path] = owner
    active = {
        path
        for path, owner in owners.items()
        if owner in set(config.error_bcs)
    }
    return selected_parsed, owners, active, analysis


def _without_docstrings(statements: list[ast.stmt]) -> list[ast.stmt]:
    return [
        statement
        for statement in statements
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
    ]


def _statement_value(statement: ast.stmt) -> ast.AST | None:
    value: ast.AST | None = None
    if isinstance(statement, ast.Assign):
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        value = statement.value
    elif isinstance(statement, ast.Expr):
        value = statement.value
    if isinstance(value, ast.Await):
        value = value.value
    return value


def _simple_assignment_target(statement: ast.stmt) -> str | None:
    if isinstance(statement, ast.Assign):
        if len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            return statement.targets[0].id
    elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        return statement.target.id
    return None


def _known_constructor(
    operation: Operation,
    call: ast.Call,
    language: ErrorLanguage,
    analysis: list[str],
) -> tuple[str, str] | None:
    if not isinstance(call.func, ast.Name):
        return None
    name = call.func.id
    known = language.all_types
    known_tails = {origin.rsplit(".", 1)[-1] for origin in known}
    definition_binding = operation.definition_bindings.get(name)
    definition_was_known = (
        definition_binding is not None
        and definition_binding.kind == "symbol_import"
        and definition_binding.origin in known
    )
    if name in operation.local_names:
        if name in known_tails or definition_was_known:
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} ErrorOut function-local binding provenance 분석 불능: {name}"
            )
        return None
    binding = operation.body_bindings.get(name)
    if binding is None:
        if name in known_tails or definition_was_known:
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} ErrorOut canonical provenance 분석 불능: {name}"
            )
        return None
    if binding.origin not in known:
        if (
            name in known_tails
            or definition_was_known
            or binding.origin.rsplit(".", 1)[-1] in known_tails
        ):
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} ErrorOut re-export provenance 분석 불능: {binding.origin}"
            )
        return None
    if binding.kind not in {"symbol_import", "local_definition"}:
        analysis.append(
            f"{operation.parsed.relative_path}:{call.lineno} ErrorOut direct provenance 분석 불능: {name}"
        )
        return None
    if binding.origin == COMMON_ERROR_OUT:
        return "common", binding.origin
    if binding.origin in language.bases_by_bc.values():
        return "base", binding.origin
    return "prepared", binding.origin


def _status_call(
    operation: Operation,
    call: ast.Call,
    analysis: list[str],
) -> bool:
    if not isinstance(call.func, ast.Name):
        if (_expression_name(call.func) or "").rsplit(".", 1)[-1] == "Status":
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} Status direct provenance 분석 불능"
            )
        return False
    name = call.func.id
    definition_binding = operation.definition_bindings.get(name)
    definition_was_status = (
        definition_binding is not None
        and definition_binding.kind == "symbol_import"
        and definition_binding.origin == NINJA_STATUS
    )
    if name in operation.local_names:
        if name == "Status" or definition_was_status:
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} Status function-local binding provenance 분석 불능"
            )
        return False
    binding = operation.body_bindings.get(name)
    if binding is not None and binding.kind == "symbol_import" and binding.origin == NINJA_STATUS:
        return True
    if name == "Status" or definition_was_status or (
        binding is not None and binding.origin.rsplit(".", 1)[-1] == "Status"
    ):
        analysis.append(
            f"{operation.parsed.relative_path}:{call.lineno} Status canonical provenance 분석 불능: {name}"
        )
    return False


def _constructor_arguments_valid(
    kind: str,
    call: ast.Call,
    language: ErrorLanguage,
) -> bool:
    if kind == "prepared":
        return not call.args and not call.keywords
    if kind != "base" or call.args:
        return False
    names = [keyword.arg for keyword in call.keywords]
    return (
        all(name is not None for name in names)
        and len(names) == len(set(names))
        and set(names) == set(language.common_fields)
    )


def _exact_status_return(
    operation: Operation,
    statement: ast.Return,
    error_name: str,
    analysis: list[str],
) -> ast.Call | None:
    call = statement.value
    if not isinstance(call, ast.Call) or not _status_call(operation, call, analysis):
        return None
    if call.keywords or len(call.args) != 2:
        return None
    first, second = call.args
    if not (
        isinstance(first, ast.Attribute)
        and first.attr == "status"
        and isinstance(first.value, ast.Name)
        and first.value.id == error_name
        and isinstance(second, ast.Name)
        and second.id == error_name
    ):
        return None
    return call


def _header_assignment_valid(
    operation: Operation,
    statement: ast.stmt,
    analysis: list[str],
) -> bool:
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        return False
    target = statement.targets[0]
    if not (
        isinstance(target, ast.Subscript)
        and isinstance(target.value, ast.Name)
        and target.value.id in operation.response_parameters
    ):
        return False
    if any(isinstance(node, ast.Call) for node in ast.walk(statement)):
        return False
    return True


def _validate_mapping_body(
    operation: Operation,
    statements: list[ast.stmt],
    language: ErrorLanguage,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    allowed_error_calls: set[int],
    allowed_status_calls: set[int],
    category: str,
) -> bool:
    body = _without_docstrings(statements)
    if len(body) < 2:
        anchor = body[0] if body else operation.node
        _append_finding(findings, seen, operation.parsed, anchor, category)
        return False
    assignment = body[0]
    error_name = _simple_assignment_target(assignment)
    value = _statement_value(assignment)
    constructor = (
        _known_constructor(operation, value, language, analysis)
        if isinstance(value, ast.Call)
        else None
    )
    valid = True
    if error_name is None or not isinstance(value, ast.Call) or constructor is None:
        valid = False
    elif not _constructor_arguments_valid(constructor[0], value, language):
        valid = False
    elif constructor[0] == "common":
        valid = False

    for statement in body[1:-1]:
        if not _header_assignment_valid(operation, statement, analysis):
            valid = False
    final = body[-1]
    status_call = (
        _exact_status_return(operation, final, error_name, analysis)
        if isinstance(final, ast.Return) and error_name is not None
        else None
    )
    if status_call is None:
        valid = False
    if valid and isinstance(value, ast.Call) and status_call is not None:
        allowed_error_calls.add(id(value))
        allowed_status_calls.add(id(status_call))
        return True
    _append_finding(findings, seen, operation.parsed, body[0], category)
    return False


def _handler_type_names(node: ast.AST | None) -> list[ast.AST] | None:
    if node is None:
        return None
    if isinstance(node, ast.Tuple):
        return list(node.elts)
    return [node]


def _exception_origin_valid(operation: Operation, node: ast.AST) -> bool | None:
    if not isinstance(node, ast.Name):
        return False
    if node.id in {"Exception", "BaseException"}:
        return False
    if node.id in operation.local_names:
        return None
    binding = operation.body_bindings.get(node.id)
    definition_binding = operation.definition_bindings.get(node.id)
    prefix = f"application.{operation.owner_bc}."
    definition_was_own = (
        definition_binding is not None
        and definition_binding.kind == "symbol_import"
        and definition_binding.origin.startswith(prefix)
        and definition_binding.origin[len(prefix) :].startswith(
            ("application_layer.", "domain_layer.")
        )
    )
    if (
        definition_was_own
        and (
            binding is None
            or binding.kind != "symbol_import"
            or binding.origin != definition_binding.origin
        )
    ):
        # A body executes against the final module namespace.  If a name that
        # was directly imported when the function was defined is rebound later,
        # its runtime exception provenance can no longer be certified.
        return None
    if binding is None or binding.kind != "symbol_import":
        return False
    if not binding.origin.startswith(prefix):
        return False
    remainder = binding.origin[len(prefix) :]
    return remainder.startswith("application_layer.") or remainder.startswith("domain_layer.")


def _caught_exception_forwarded(handler: ast.ExceptHandler) -> bool:
    if not handler.name:
        return False

    def contains_caught_name(root: ast.AST) -> bool:
        return any(
            isinstance(candidate, ast.Name) and candidate.id == handler.name
            for candidate in _iter_evaluated_nodes(root)
        )

    for statement in handler.body:
        for node in _iter_evaluated_nodes(statement):
            if not isinstance(node, ast.Call):
                continue
            values = [*node.args, *(keyword.value for keyword in node.keywords)]
            if any(contains_caught_name(value) for value in values):
                return True
    return False


def _try_root_call(statement: ast.stmt) -> ast.Call | None:
    if not isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Expr)):
        return None
    value = _statement_value(statement)
    return value if isinstance(value, ast.Call) else None


def _analyze_try(
    operation: Operation,
    node: ast.Try,
    language: ErrorLanguage,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    allowed_error_calls: set[int],
    allowed_status_calls: set[int],
) -> None:
    if node.orelse or node.finalbody:
        _append_finding(
            findings,
            seen,
            operation.parsed,
            node,
            "managed try cannot have else/finally",
        )
    if len(node.body) != 1 or _try_root_call(node.body[0]) is None:
        _append_finding(
            findings,
            seen,
            operation.parsed,
            node,
            "managed try body must be one root-call statement",
        )
    if any(isinstance(candidate, ast.Raise) for candidate in _iter_lexical_nodes(node.body)):
        _append_finding(
            findings, seen, operation.parsed, node, "raise inside managed try"
        )
    for handler in node.handlers:
        type_nodes = _handler_type_names(handler.type)
        if type_nodes is None:
            _append_finding(
                findings, seen, operation.parsed, handler, "bare catch forbidden"
            )
        else:
            for type_node in type_nodes:
                validity = _exception_origin_valid(operation, type_node)
                if validity is None:
                    analysis.append(
                        f"{operation.parsed.relative_path}:{getattr(type_node, 'lineno', handler.lineno)} "
                        "caught exception runtime provenance 분석 불능"
                    )
                elif not validity:
                    _append_finding(
                        findings,
                        seen,
                        operation.parsed,
                        type_node,
                        "catch must be direct own-BC application/domain exception",
                    )
        if any(
            isinstance(candidate, ast.Raise)
            for candidate in _iter_lexical_nodes(handler.body)
        ):
            _append_finding(
                findings, seen, operation.parsed, handler, "raise inside managed catch"
            )
        if _caught_exception_forwarded(handler):
            _append_finding(
                findings,
                seen,
                operation.parsed,
                handler,
                "caught exception forwarding forbidden",
            )
        _validate_mapping_body(
            operation,
            handler.body,
            language,
            analysis,
            findings,
            seen,
            allowed_error_calls,
            allowed_status_calls,
            "managed catch must directly construct ErrorOut and return Status",
        )


def _result_test_name(test: ast.AST) -> str | None:
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Is)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value is None
        and isinstance(test.left, ast.Name)
    ):
        return test.left.id
    if (
        isinstance(test, ast.Call)
        and isinstance(test.func, ast.Name)
        and test.func.id == "isinstance"
        and len(test.args) == 2
        and not test.keywords
        and isinstance(test.args[0], ast.Name)
    ):
        return test.args[0].id
    return None


def _builtin_isinstance_call(
    function: Operation,
    node: ast.AST,
    analysis: list[str],
) -> bool:
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "isinstance"
    ):
        return False
    binding = function.body_bindings.get("isinstance")
    if "isinstance" in function.local_names or binding is not None:
        analysis.append(
            f"{function.parsed.relative_path}:{node.lineno} "
            "isinstance builtin provenance 분석 불능"
        )
        return False
    return True


def _supported_result_test(
    operation: Operation,
    test: ast.AST,
    result_name: str,
    analysis: list[str],
) -> bool:
    if (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Is)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value is None
        and isinstance(test.left, ast.Name)
        and test.left.id == result_name
    ):
        return True
    if (
        isinstance(test, ast.Call)
        and len(test.args) == 2
        and not test.keywords
        and isinstance(test.args[0], ast.Name)
        and test.args[0].id == result_name
        and isinstance(test.args[1], ast.Name)
    ):
        if not _builtin_isinstance_call(operation, test, analysis):
            return False
        validity = _exception_origin_valid(operation, test.args[1])
        if validity is None:
            analysis.append(
                f"{operation.parsed.relative_path}:{test.lineno} Result failure variant provenance 분석 불능"
            )
            return False
        return validity
    return False


def _raw_error_terminal(operation: Operation, node: ast.AST) -> bool:
    if not isinstance(node, ast.Return) or node.value is None:
        return False
    value = node.value
    if (
        isinstance(value, (ast.Tuple, ast.List))
        and value.elts
        and isinstance(value.elts[0], ast.Constant)
        and isinstance(value.elts[0].value, int)
        and 400 <= value.elts[0].value <= 599
    ):
        return True
    if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
        return False
    if value.func.id in operation.local_names:
        return False
    binding = operation.body_bindings.get(value.func.id)
    if binding is None or binding.kind != "symbol_import" or binding.origin not in RAW_RESPONSE_TYPES:
        return False
    for keyword in value.keywords:
        if (
            keyword.arg in {"status", "status_code"}
            and isinstance(keyword.value, ast.Constant)
            and isinstance(keyword.value.value, int)
            and 400 <= keyword.value.value <= 599
        ):
            return True
    return False


def _known_error_assignments(
    operation: Operation,
    language: ErrorLanguage,
    analysis: list[str],
) -> dict[str, set[int]]:
    assignments: dict[str, set[int]] = {
        name: set() for name in _annotated_error_parameters(operation, language)
    }
    for node in _iter_lexical_nodes(operation.node.body):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        name = _simple_assignment_target(node)
        value = _statement_value(node)
        if name is None or not isinstance(value, ast.Call):
            continue
        if _known_constructor(operation, value, language, analysis) is not None:
            assignments.setdefault(name, set()).add(id(value))
    return assignments


def _status_is_error_mapping(
    operation: Operation,
    call: ast.Call,
    error_assignments: dict[str, set[int]],
    language: ErrorLanguage,
    analysis: list[str],
) -> bool:
    if not _status_call(operation, call, analysis) or len(call.args) < 2:
        return False
    second = call.args[1]
    if isinstance(second, ast.Name) and second.id in error_assignments:
        return True
    return isinstance(second, ast.Call) and _known_constructor(
        operation, second, language, analysis
    ) is not None


def _literal_error_status_call(
    operation: Operation,
    call: ast.Call,
    analysis: list[str],
) -> bool:
    if not _status_call(operation, call, analysis) or len(call.args) < 2:
        return False
    status = call.args[0]
    return (
        isinstance(status, ast.Constant)
        and isinstance(status.value, int)
        and 400 <= status.value <= 599
    )


def _branch_has_error_behavior(
    operation: Operation,
    statements: list[ast.stmt],
    language: ErrorLanguage,
    error_assignments: dict[str, set[int]],
    analysis: list[str],
) -> bool:
    for node in _iter_lexical_nodes(statements):
        if isinstance(node, ast.Raise) or _raw_error_terminal(operation, node):
            return True
        if isinstance(node, ast.Call):
            if _known_constructor(operation, node, language, analysis) is not None:
                return True
            if _status_is_error_mapping(
                operation, node, error_assignments, language, analysis
            ):
                return True
            if _literal_error_status_call(operation, node, analysis):
                return True
    return False


def _candidate_branch(
    operation: Operation,
    node: ast.AST,
    language: ErrorLanguage,
    error_assignments: dict[str, set[int]],
    analysis: list[str],
) -> bool:
    if isinstance(node, ast.If):
        if _result_test_name(node.test) is not None:
            return True
        return _branch_has_error_behavior(
            operation,
            [*node.body, *node.orelse],
            language,
            error_assignments,
            analysis,
        )
    if MATCH is not None and isinstance(node, MATCH):
        bodies = [statement for case in node.cases for statement in case.body]
        return _branch_has_error_behavior(
            operation, bodies, language, error_assignments, analysis
        )
    return False


def _call_assignment(statement: ast.stmt) -> tuple[str, ast.Call] | None:
    name = _simple_assignment_target(statement)
    value = _statement_value(statement)
    if name is None or not isinstance(value, ast.Call):
        return None
    return name, value


def _try_assignment(statement: ast.stmt) -> tuple[str, ast.Call] | None:
    if not isinstance(statement, ast.Try) or len(statement.body) != 1:
        return None
    return _call_assignment(statement.body[0])


def _analyze_results(
    operation: Operation,
    language: ErrorLanguage,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    allowed_error_calls: set[int],
    allowed_status_calls: set[int],
) -> None:
    body = _without_docstrings(operation.node.body)
    error_assignments = _known_error_assignments(operation, language, analysis)
    approved_branches: set[int] = set()

    for index in range(len(body) - 1):
        assignment = _call_assignment(body[index])
        branch = body[index + 1]
        if assignment is None or not isinstance(branch, ast.If):
            continue
        if _known_constructor(operation, assignment[1], language, analysis) is not None:
            # A local ErrorOut construction is mapping behavior, not the
            # application-call assignment that can causally own a Result arm.
            continue
        result_name, _ = assignment
        if not _candidate_branch(
            operation, branch, language, error_assignments, analysis
        ):
            continue
        if not _supported_result_test(operation, branch.test, result_name, analysis):
            analysis.append(
                f"{operation.parsed.relative_path}:{branch.lineno} Result candidate predicate 분석 불능"
            )
            continue
        approved_branches.add(id(branch))
        _validate_mapping_body(
            operation,
            branch.body,
            language,
            analysis,
            findings,
            seen,
            allowed_error_calls,
            allowed_status_calls,
            "Result arm must directly construct ErrorOut and return Status",
        )

    for index, statement in enumerate(body):
        if not isinstance(statement, ast.If):
            continue
        if id(statement) in approved_branches:
            continue
        if not _candidate_branch(
            operation, statement, language, error_assignments, analysis
        ):
            continue
        test_name = _result_test_name(statement.test)
        if test_name is None:
            analysis.append(
                f"{operation.parsed.relative_path}:{statement.lineno} unsupported Result/error candidate predicate"
            )
            continue
        previous = body[index - 1] if index else None
        dual = _try_assignment(previous) if previous is not None else None
        if dual is not None and dual[0] == test_name:
            _append_finding(
                findings,
                seen,
                operation.parsed,
                statement,
                "same call cannot use exception and Result mapping",
            )
            continue
        direct = _call_assignment(previous) if previous is not None else None
        if direct is not None and direct[0] != test_name:
            if _known_constructor(operation, direct[1], language, analysis) is not None:
                _append_finding(
                    findings,
                    seen,
                    operation.parsed,
                    statement,
                    "orphan/pre-call error mapping is not causally owned by an application call",
                )
            else:
                analysis.append(
                    f"{operation.parsed.relative_path}:{statement.lineno} Result candidate references another variable"
                )
            continue
        _append_finding(
            findings,
            seen,
            operation.parsed,
            statement,
            "Result/error mapping must immediately follow its try-free call assignment",
        )

    for node in _iter_lexical_nodes(operation.node.body):
        if MATCH is not None and isinstance(node, MATCH):
            if _candidate_branch(
                operation, node, language, error_assignments, analysis
            ):
                analysis.append(
                    f"{operation.parsed.relative_path}:{node.lineno} unsupported Result/error match candidate"
                )

    for node in _iter_lexical_nodes(operation.node.body):
        if not isinstance(node, ast.Call):
            continue
        constructor = _known_constructor(operation, node, language, analysis)
        if constructor is not None and id(node) not in allowed_error_calls:
            _append_finding(
                findings,
                seen,
                operation.parsed,
                node,
                "ErrorOut construction is not owned by an approved catch/Result arm",
            )
        error_status = _status_is_error_mapping(
            operation, node, error_assignments, language, analysis
        ) or _literal_error_status_call(operation, node, analysis)
        if error_status and id(node) not in allowed_status_calls:
            _append_finding(
                findings,
                seen,
                operation.parsed,
                node,
                "error Status mapping is not owned by an approved catch/Result arm",
            )


def _function_context(
    parsed: ParsedSource,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    owner_bc: str,
    definition_bindings: dict[str, Binding],
    final_bindings: dict[str, Binding],
) -> Operation:
    annotation_bindings = (
        final_bindings if _future_annotations(parsed) else definition_bindings
    )
    return Operation(
        parsed=parsed,
        node=node,
        owner_bc=owner_bc,
        identity=f"{parsed.relative_path}:{node.name}@{node.lineno}",
        definition_bindings=dict(definition_bindings),
        annotation_bindings=dict(annotation_bindings),
        body_bindings=dict(final_bindings),
        local_names=_function_local_names(node),
        response_parameters=_response_parameters(node, annotation_bindings),
    )


def _module_functions(
    parsed: ParsedSource,
    owner_bc: str,
) -> list[tuple[Operation, dict[str, Binding]]]:
    timeline = _binding_timeline(parsed)
    functions: list[tuple[Operation, dict[str, Binding]]] = []
    for statement in parsed.tree.body:
        definition = timeline.before.get(id(statement), {})
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(
                (
                    _function_context(
                        parsed, statement, owner_bc, definition, timeline.final
                    ),
                    definition,
                )
            )
        elif isinstance(statement, ast.ClassDef):
            class_before = _class_body_bindings(parsed, statement, definition)
            for member in statement.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    member_definition = class_before.get(id(member), definition)
                    functions.append(
                        (
                            _function_context(
                                parsed,
                                member,
                                owner_bc,
                                member_definition,
                                timeline.final,
                            ),
                            member_definition,
                        )
                    )
    return functions


def _annotated_error_parameters(
    function: Operation,
    language: ErrorLanguage,
) -> set[str]:
    names: set[str] = set()
    for argument in _function_argument_nodes(function.node):
        annotation = argument.annotation
        if not isinstance(annotation, ast.Name):
            continue
        binding = function.annotation_bindings.get(annotation.id)
        if (
            binding is not None
            and binding.kind == "symbol_import"
            and binding.origin in language.all_types
        ):
            names.add(argument.arg)
    return names


def _raw_response_call(function: Operation, call: ast.Call) -> bool:
    if not isinstance(call.func, ast.Name) or call.func.id in function.local_names:
        return False
    binding = function.body_bindings.get(call.func.id)
    return (
        binding is not None
        and binding.kind == "symbol_import"
        and binding.origin in RAW_RESPONSE_TYPES
    )


def _model_dump_receivers(node: ast.AST) -> set[str]:
    receivers: set[str] = set()
    for candidate in ast.walk(node):
        if (
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Attribute)
            and candidate.func.attr == "model_dump"
            and isinstance(candidate.func.value, ast.Name)
        ):
            receivers.add(candidate.func.value.id)
    return receivers


def _exception_identification(
    function: Operation,
    node: ast.AST,
    analysis: list[str],
) -> bool:
    return (
        _builtin_isinstance_call(function, node, analysis)
        and len(node.args) == 2
        and not node.keywords
        and _exception_origin_valid(function, node.args[1]) is True
    )


def _one_step_error_parameters(
    parsed: dict[Path, ParsedSource],
    managed_paths: set[Path],
    language: ErrorLanguage,
    analysis: list[str],
) -> dict[tuple[Path, int], set[str]]:
    """Prove one direct ErrorOut argument hop into a managed helper.

    The provenance deliberately does not propagate again from the callee, so a
    serializer reached only through a two-hop forwarding chain remains outside
    this checker's behavior-managed horizon.
    """
    targets: dict[
        str,
        tuple[
            Path,
            ast.FunctionDef | ast.AsyncFunctionDef,
            tuple[str, ...],
            frozenset[str],
        ],
    ] = {}
    ambiguous: set[str] = set()
    for path in sorted(managed_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is None:
            continue
        module = _module_name(path)
        for statement in source.tree.body:
            if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            origin = f"{module}.{statement.name}"
            positional = tuple(
                argument.arg
                for argument in (*statement.args.posonlyargs, *statement.args.args)
            )
            keywords = frozenset(
                argument.arg for argument in _function_argument_nodes(statement)
            )
            target = (path, statement, positional, keywords)
            if origin in targets:
                ambiguous.add(origin)
            else:
                targets[origin] = target
    for origin in ambiguous:
        targets.pop(origin, None)

    proven: dict[tuple[Path, int], set[str]] = {}
    for path in sorted(managed_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is None:
            continue
        parts = path.parts
        owner = parts[1] if len(parts) > 2 and parts[0] == "application" else ""
        for caller, _ in _module_functions(source, owner):
            def inspect_call(call: ast.Call, error_names: set[str]) -> None:
                if (
                    not isinstance(call.func, ast.Name)
                    or call.func.id in caller.local_names
                    or any(isinstance(argument, ast.Starred) for argument in call.args)
                ):
                    return
                binding = caller.body_bindings.get(call.func.id)
                if binding is None or binding.kind not in {
                    "symbol_import",
                    "local_definition",
                }:
                    return
                target = targets.get(binding.origin)
                if target is None:
                    return
                target_path, target_node, positional, keywords = target

                def error_value(value: ast.AST) -> bool:
                    if isinstance(value, ast.Name) and value.id in error_names:
                        return True
                    return isinstance(value, ast.Call) and _known_constructor(
                        caller, value, language, analysis
                    ) is not None

                target_key = (target_path, id(target_node))
                for index, argument in enumerate(call.args):
                    if index < len(positional) and error_value(argument):
                        proven.setdefault(target_key, set()).add(positional[index])
                for keyword in call.keywords:
                    if (
                        keyword.arg is not None
                        and keyword.arg in keywords
                        and error_value(keyword.value)
                    ):
                        proven.setdefault(target_key, set()).add(keyword.arg)

            def inspect_expression(root: ast.AST, error_names: set[str]) -> None:
                for node in _iter_evaluated_nodes(root):
                    if isinstance(node, ast.Call):
                        inspect_call(node, error_names)

            def merge_error_names(states: list[set[str]]) -> set[str]:
                return {name for state in states for name in state}

            def scan_simple(statement: ast.stmt, incoming: set[str]) -> set[str]:
                error_names = set(incoming)
                inspect_expression(statement, error_names)
                error_names.difference_update(_statement_bound_names(statement))
                target = _simple_assignment_target(statement)
                value = _statement_value(statement)
                if target is not None and isinstance(value, ast.Call):
                    if _known_constructor(caller, value, language, analysis) is not None:
                        error_names.add(target)
                return error_names

            def scan_suite(
                statements: list[ast.stmt], incoming: set[str]
            ) -> set[str]:
                error_names = set(incoming)
                for statement in statements:
                    if isinstance(
                        statement,
                        (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
                    ):
                        error_names.difference_update(
                            _statement_bound_names(statement)
                        )
                        continue
                    if isinstance(statement, ast.If):
                        inspect_expression(statement.test, error_names)
                        error_names = merge_error_names(
                            [
                                scan_suite(statement.body, error_names),
                                scan_suite(statement.orelse, error_names),
                            ]
                        )
                        continue
                    if isinstance(statement, ast.While):
                        inspect_expression(statement.test, error_names)
                        body_out = scan_suite(statement.body, error_names)
                        error_names = merge_error_names(
                            [
                                error_names,
                                scan_suite(statement.orelse, error_names),
                                scan_suite(statement.orelse, body_out),
                            ]
                        )
                        continue
                    if isinstance(statement, (ast.For, ast.AsyncFor)):
                        inspect_expression(statement.iter, error_names)
                        body_in = set(error_names)
                        body_in.difference_update(_target_names(statement.target))
                        body_out = scan_suite(statement.body, body_in)
                        error_names = merge_error_names(
                            [
                                scan_suite(statement.orelse, error_names),
                                scan_suite(statement.orelse, body_out),
                            ]
                        )
                        continue
                    if isinstance(statement, (ast.With, ast.AsyncWith)):
                        body_in = set(error_names)
                        for item in statement.items:
                            inspect_expression(item.context_expr, body_in)
                            if item.optional_vars is not None:
                                body_in.difference_update(
                                    _target_names(item.optional_vars)
                                )
                        error_names = scan_suite(statement.body, body_in)
                        continue
                    if isinstance(statement, ast.Try):
                        normal = scan_suite(statement.body, error_names)
                        outcomes = [scan_suite(statement.orelse, normal)]
                        for handler in statement.handlers:
                            handler_in = set(error_names)
                            if handler.type is not None:
                                inspect_expression(handler.type, handler_in)
                            if handler.name:
                                handler_in.discard(handler.name)
                            outcomes.append(scan_suite(handler.body, handler_in))
                        error_names = scan_suite(
                            statement.finalbody,
                            merge_error_names(outcomes),
                        )
                        continue
                    error_names = scan_simple(statement, error_names)
                return error_names

            scan_suite(
                caller.node.body,
                _annotated_error_parameters(caller, language),
            )
    return proven


def _handler_receiver(
    node: ast.AST, bindings: dict[str, Binding]
) -> bool:
    if not isinstance(node, ast.Name):
        return False
    binding = bindings.get(node.id)
    return (
        binding is not None
        and binding.kind == "framework_instance"
        and binding.origin in {*HANDLER_CONSTRUCTORS, "<framework-handler>"}
    )


def _handler_registration_findings(
    parsed: ParsedSource,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    timeline = _binding_timeline(parsed)
    module = _module_name(parsed.relative_path)

    def inspect_call(call: ast.Call, bindings: dict[str, Binding]) -> None:
        if (
            not isinstance(call.func, ast.Attribute)
            or call.func.attr not in {"exception_handler", "add_exception_handler"}
            or not isinstance(call.func.value, ast.Name)
        ):
            return
        receiver = bindings.get(call.func.value.id)
        if receiver == AMBIGUOUS_BINDING:
            analysis.append(
                f"{parsed.relative_path}:{call.lineno} "
                "Ninja handler receiver provenance 분석 불능"
            )
            return
        if not _handler_receiver(call.func.value, bindings):
            return
        if call.func.attr == "exception_handler":
            _append_finding(
                findings,
                seen,
                parsed,
                call,
                "custom Ninja exception_handler forbidden",
            )
        elif call.func.attr == "add_exception_handler":
            _append_finding(
                findings,
                seen,
                parsed,
                call,
                "custom Ninja add_exception_handler forbidden",
            )

    def inspect_expression(root: ast.AST, bindings: dict[str, Binding]) -> None:
        for candidate in _iter_evaluated_nodes(root):
            if isinstance(candidate, ast.Call):
                inspect_call(candidate, bindings)

    def nested_bound_names(statement: ast.stmt) -> set[str]:
        return {
            name
            for candidate in _iter_lexical_nodes([statement])
            if isinstance(candidate, ast.stmt)
            for name in _statement_bound_names(candidate)
        }

    def scan_suite(
        statements: list[ast.stmt],
        incoming: dict[str, Binding],
        *,
        scope_kind: str,
    ) -> dict[str, Binding]:
        bindings = dict(incoming)
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for expression in _definition_expressions(statement):
                    inspect_expression(expression, bindings)
                body_bindings = dict(timeline.final)
                if scope_kind == "function":
                    body_bindings.update(bindings)
                for name in _function_local_names(statement):
                    body_bindings.pop(name, None)
                scan_suite(statement.body, body_bindings, scope_kind="function")
                _advance_binding_state(
                    parsed,
                    statement,
                    bindings,
                    definition_prefix=module,
                )
                continue
            if isinstance(statement, ast.ClassDef):
                for expression in _definition_expressions(statement):
                    inspect_expression(expression, bindings)
                scan_suite(statement.body, bindings, scope_kind="class")
                _advance_binding_state(
                    parsed,
                    statement,
                    bindings,
                    definition_prefix=module,
                )
                continue
            if isinstance(statement, ast.If):
                inspect_expression(statement.test, bindings)
                truth = _literal_truth(statement.test)
                if truth is True:
                    bindings = scan_suite(
                        statement.body, bindings, scope_kind=scope_kind
                    )
                elif truth is False:
                    bindings = scan_suite(
                        statement.orelse, bindings, scope_kind=scope_kind
                    )
                else:
                    bindings = _join_binding_states(
                        [
                            scan_suite(
                                statement.body, bindings, scope_kind=scope_kind
                            ),
                            scan_suite(
                                statement.orelse, bindings, scope_kind=scope_kind
                            ),
                        ]
                    )
                continue
            if isinstance(statement, ast.While):
                inspect_expression(statement.test, bindings)
                scan_suite(statement.body, bindings, scope_kind=scope_kind)
                scan_suite(statement.orelse, bindings, scope_kind=scope_kind)
            elif isinstance(statement, (ast.For, ast.AsyncFor)):
                inspect_expression(statement.iter, bindings)
                branch = dict(bindings)
                for name in _target_names(statement.target):
                    branch.pop(name, None)
                scan_suite(statement.body, branch, scope_kind=scope_kind)
                scan_suite(statement.orelse, bindings, scope_kind=scope_kind)
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                branch = dict(bindings)
                for item in statement.items:
                    inspect_expression(item.context_expr, branch)
                    if item.optional_vars is not None:
                        for name in _target_names(item.optional_vars):
                            branch.pop(name, None)
                scan_suite(statement.body, branch, scope_kind=scope_kind)
            elif isinstance(statement, ast.Try):
                scan_suite(statement.body, bindings, scope_kind=scope_kind)
                scan_suite(statement.orelse, bindings, scope_kind=scope_kind)
                scan_suite(statement.finalbody, bindings, scope_kind=scope_kind)
                for handler in statement.handlers:
                    branch = dict(bindings)
                    if handler.type is not None:
                        inspect_expression(handler.type, branch)
                    if handler.name:
                        branch.pop(handler.name, None)
                    scan_suite(handler.body, branch, scope_kind=scope_kind)
            else:
                inspect_expression(statement, bindings)
                _advance_binding_state(
                    parsed,
                    statement,
                    bindings,
                    definition_prefix=module,
                )
                continue
            for name in nested_bound_names(statement):
                bindings.pop(name, None)
        return bindings

    scan_suite(parsed.tree.body, {}, scope_kind="module")


def _helper_function_facts(
    function: Operation,
    language: ErrorLanguage,
    initial_error_names: set[str],
    analysis: list[str],
) -> HelperFacts:
    facts = HelperFacts()

    def inspect_expression(root: ast.AST, error_names: set[str]) -> None:
        for node in _iter_evaluated_nodes(root):
            if isinstance(node, ast.Call):
                constructor = _known_constructor(function, node, language, analysis)
                if constructor is not None:
                    facts.has_error_constructor = True
                    if constructor[0] == "prepared":
                        facts.has_prepared = True
                if _exception_identification(function, node, analysis):
                    facts.has_exception_test = True
                if _raw_response_call(function, node) and (
                    _model_dump_receivers(node) & error_names
                ):
                    facts.serializer_node = node

    def merge_error_names(states: list[set[str]]) -> set[str]:
        return {name for state in states for name in state}

    def scan_simple(statement: ast.stmt, incoming: set[str]) -> set[str]:
        error_names = set(incoming)
        value = _statement_value(statement)
        if value is not None:
            inspect_expression(value, error_names)
        elif not isinstance(
            statement,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            inspect_expression(statement, error_names)

        bound = _statement_bound_names(statement)
        error_names.difference_update(bound)
        target = _simple_assignment_target(statement)
        if target is not None and isinstance(value, ast.Call):
            if _known_constructor(function, value, language, analysis) is not None:
                error_names.add(target)
        return error_names

    def scan_suite(statements: list[ast.stmt], incoming: set[str]) -> set[str]:
        error_names = set(incoming)
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                error_names.difference_update(_statement_bound_names(statement))
                continue
            if isinstance(statement, ast.If):
                inspect_expression(statement.test, error_names)
                error_names = merge_error_names(
                    [
                        scan_suite(statement.body, error_names),
                        scan_suite(statement.orelse, error_names),
                    ]
                )
                continue
            if isinstance(statement, ast.While):
                inspect_expression(statement.test, error_names)
                body_out = scan_suite(statement.body, error_names)
                error_names = merge_error_names(
                    [
                        error_names,
                        scan_suite(statement.orelse, error_names),
                        scan_suite(statement.orelse, body_out),
                    ]
                )
                continue
            if isinstance(statement, (ast.For, ast.AsyncFor)):
                inspect_expression(statement.iter, error_names)
                body_in = set(error_names)
                body_in.difference_update(_target_names(statement.target))
                body_out = scan_suite(statement.body, body_in)
                error_names = merge_error_names(
                    [
                        scan_suite(statement.orelse, error_names),
                        scan_suite(statement.orelse, body_out),
                    ]
                )
                continue
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                body_in = set(error_names)
                for item in statement.items:
                    inspect_expression(item.context_expr, body_in)
                    if item.optional_vars is not None:
                        body_in.difference_update(_target_names(item.optional_vars))
                error_names = scan_suite(statement.body, body_in)
                continue
            if isinstance(statement, ast.Try):
                normal = scan_suite(statement.body, error_names)
                outcomes = [scan_suite(statement.orelse, normal)]
                for handler in statement.handlers:
                    handler_in = set(error_names)
                    if handler.type is not None:
                        inspect_expression(handler.type, handler_in)
                    if handler.name:
                        handler_in.discard(handler.name)
                    outcomes.append(scan_suite(handler.body, handler_in))
                error_names = scan_suite(
                    statement.finalbody,
                    merge_error_names(outcomes),
                )
                continue
            error_names = scan_simple(statement, error_names)
        return error_names

    scan_suite(function.node.body, initial_error_names)
    return facts


def _nested_functions(
    statements: list[ast.stmt],
) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    stack: list[ast.stmt] = list(reversed(statements))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node
            continue
        for _, value in ast.iter_fields(node):
            if isinstance(value, list):
                stack.extend(
                    reversed([item for item in value if isinstance(item, ast.stmt)])
                )
            elif isinstance(value, ast.stmt):
                stack.append(value)


def _helper_findings(
    parsed: ParsedSource,
    owner_bc: str,
    language: ErrorLanguage,
    operation_ids: set[int],
    one_step_parameters: dict[tuple[Path, int], set[str]],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    _handler_registration_findings(parsed, analysis, findings, seen)

    def analyze_helper(function: Operation) -> None:
        initial_error_names = (
            _annotated_error_parameters(function, language)
            | one_step_parameters.get(
                (parsed.relative_path, id(function.node)), set()
            )
        )
        facts = _helper_function_facts(
            function,
            language,
            set(initial_error_names),
            analysis,
        )
        if facts.has_prepared:
            _append_finding(
                findings,
                seen,
                parsed,
                function.node,
                "prepared ErrorOut factory/helper forbidden",
            )
        if facts.serializer_node is not None:
            _append_finding(
                findings,
                seen,
                parsed,
                facts.serializer_node,
                "ErrorOut raw HTTP serializer helper forbidden",
            )
        if facts.has_exception_test and facts.has_error_constructor:
            _append_finding(
                findings,
                seen,
                parsed,
                function.node,
                "exception-to-ErrorOut mapping helper forbidden",
            )

        for nested in _nested_functions(function.node.body):
            nested_context = _function_context(
                parsed,
                nested,
                owner_bc,
                function.body_bindings,
                function.body_bindings,
            )
            analyze_helper(nested_context)

    for function, _ in _module_functions(parsed, owner_bc):
        if id(function.node) in operation_ids:
            for nested in _nested_functions(function.node.body):
                analyze_helper(
                    _function_context(
                        parsed,
                        nested,
                        owner_bc,
                        function.body_bindings,
                        function.body_bindings,
                    )
                )
            continue
        analyze_helper(function)


def _analyze_operation(
    operation: Operation,
    language: ErrorLanguage,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    allowed_error_calls: set[int] = set()
    allowed_status_calls: set[int] = set()
    for node in _iter_lexical_nodes(operation.node.body):
        if TRY_STAR is not None and isinstance(node, TRY_STAR):
            analysis.append(
                f"{operation.parsed.relative_path}:{node.lineno} except* direct grammar unsupported"
            )
        elif isinstance(node, ast.Try):
            _analyze_try(
                operation,
                node,
                language,
                analysis,
                findings,
                seen,
                allowed_error_calls,
                allowed_status_calls,
            )
    _analyze_results(
        operation,
        language,
        analysis,
        findings,
        seen,
        allowed_error_calls,
        allowed_status_calls,
    )


def _semantic_findings(
    config: Config,
    parsed: dict[Path, ParsedSource],
    owners: dict[Path, str],
    active_controllers: set[Path],
    managed_paths: set[Path],
    language: ErrorLanguage,
) -> tuple[list[str], list[Finding]]:
    analysis: list[str] = []
    findings: list[Finding] = []
    seen: set[tuple[Path, int, str]] = set()
    one_step_parameters = _one_step_error_parameters(
        parsed, managed_paths, language, analysis
    )
    operations_by_path: dict[Path, list[Operation]] = {}
    for path in sorted(active_controllers, key=Path.as_posix):
        source = parsed.get(path)
        owner = owners.get(path)
        if source is None or owner is None:
            continue
        operations = _discover_operations(source, owner, analysis)
        operations_by_path[path] = operations
        for operation in operations:
            _analyze_operation(operation, language, analysis, findings, seen)

    for path in sorted(managed_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is None:
            continue
        owner = owners.get(path)
        if owner is None:
            parts = path.parts
            owner = parts[1] if len(parts) > 2 and parts[0] == "application" else ""
        operation_ids = {
            id(operation.node) for operation in operations_by_path.get(path, [])
        }
        _helper_findings(
            source,
            owner,
            language,
            operation_ids,
            one_step_parameters,
            analysis,
            findings,
            seen,
        )
    return sorted(set(analysis)), sorted(
        findings,
        key=lambda item: (item.path.as_posix(), item.lineno, item.category),
    )


def _run(config: Config) -> tuple[list[str], list[Finding]]:
    inventory = _production_inventory(config.root)
    selected, owners, active, analysis = _selected_source_plan(config, inventory)
    if config.profile == "preserve-established":
        return sorted(set(analysis)), []
    if not config.error_bcs:
        return sorted(set(analysis)), []

    module_paths = _module_path_index(inventory)
    one_hop: set[Path] = set()
    for path in sorted(active, key=Path.as_posix):
        source = selected.get(path)
        owner = owners.get(path)
        if source is not None and owner is not None:
            one_hop.update(
                _one_hop_paths(config.root, source, owner, module_paths, analysis)
            )
    canonical = {_bc_error_path(bc) for bc in config.error_bcs}
    managed = {*active, *canonical, *one_hop}
    required = {
        *(config.controller_modules),
        *(canonical),
        *(one_hop),
        COMMON_ERROR_PATH,
    }
    if config.api_module is not None:
        required.add(config.api_module)
    parsed, load_analysis = _load_sources(config.root, required)
    analysis.extend(load_analysis)
    language = _error_language(parsed, config.error_bcs, analysis)
    semantic_analysis, findings = _semantic_findings(
        config,
        parsed,
        owners,
        active,
        managed,
        language,
    )
    analysis.extend(semantic_analysis)
    return sorted(set(analysis)), findings


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
    except UsageError as exc:
        print(
            f"[check-api-error-controller-contract] 사용 오류: {exc}",
            file=sys.stderr,
        )
        return 1
    except SystemExit as exc:
        return int(exc.code)

    if config.profile == "auto":
        return 0
    try:
        analysis, findings = _run(config)
        if analysis:
            raise UsageError("; ".join(analysis))
    except UsageError as exc:
        print(
            f"[check-api-error-controller-contract] 사용 오류: {exc}",
            file=sys.stderr,
        )
        return 1

    if findings:
        print(
            "[check-api-error-controller-contract] BLOCKER — code-profile "
            "controller error mapping contract violation:"
        )
        for finding in findings:
            print(finding.render())
        print(
            "  근거: known BC failures are mapped directly by their selected "
            "owner controller through one narrow exception or try-free Result "
            "path and exact Status(error.status, error); helper/handler/raw "
            "detours are not part of this contract."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
