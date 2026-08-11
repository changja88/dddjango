#!/usr/bin/env python3
"""Block direct raw 200-203 returns that bypass a declared Ninja schema.

The selector-free invocation preserves the historical touched-file gate.  An
explicit ``--controller-module`` invocation instead validates and analyzes the
exact selected set, including unchanged tracked files.

Exit codes: 0=clean/help, 2=contract blocker, 1=usage or analysis error.
"""
from __future__ import annotations

import argparse
import ast
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import standard_tree as _tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
OPERATION_CONSTRUCTORS = {
    "ninja.Router",
    "ninja.NinjaAPI",
    "ninja_extra.NinjaExtraAPI",
}
RAW_RESPONSE_ORIGINS = {
    "django.http.HttpResponse",
    "django.http.JsonResponse",
}
SUCCESS_BODY_STATUSES = {200, 201, 202, 203}
TEST_DIR_NAMES = {"test", "tests"}
SKIP_DIR_NAMES = {
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
    ".dddjango",
}
DRIVING_DIR_NAMES = frozenset({"driving_layer"})
_ADOPTION_LAYERS = frozenset(
    {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
)
_DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")


def _adopted(root: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    for c in root.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIR_NAMES:
            continue
        for bc in sorted(c.iterdir()):
            if not bc.is_dir() or bc.name.startswith("."):
                continue
            if any((bc / n).is_dir() for n in _ADOPTION_LAYERS):
                return True
            if any((bc / m).is_file() for m in _DJANGO_APP_MARKERS):
                return True
            if any(p.is_dir() and p.name.startswith("django_") for p in bc.iterdir()):
                return True
    return False


class UsageError(Exception):
    """CLI, inventory, or selected-source analysis failure."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True)
class Config:
    root: Path
    controller_modules: tuple[Path, ...]

    @property
    def selected(self) -> bool:
        return bool(self.controller_modules)


@dataclass(frozen=True)
class Inventory:
    paths: tuple[Path, ...]
    tracked: frozenset[Path]
    changed: frozenset[Path]
    git_root: Path | None


@dataclass(frozen=True)
class ParsedSource:
    path: Path
    source: str
    tree: ast.Module


@dataclass(frozen=True)
class Binding:
    origin: str
    kind: str


@dataclass(frozen=True)
class BindingTimeline:
    before: dict[int, dict[str, Binding]]
    final: dict[str, Binding]


@dataclass(frozen=True)
class Operation:
    parsed: ParsedSource
    node: ast.FunctionDef | ast.AsyncFunctionDef
    identity: str
    body_bindings: dict[str, Binding]
    local_names: frozenset[str]


@dataclass(frozen=True)
class Finding:
    path: Path
    operation: str
    lineno: int

    def render(self) -> str:
        return (
            f"  - {self.path}: operation '{self.operation}' "
            f"(:{self.lineno} direct raw 200-203 response)"
        )


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--controller-module", action="append", default=[])
    return parser


def _source_path(raw: str, issues: list[str]) -> Path | None:
    path = Path(raw)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != raw
        or "/" not in raw
        or path.suffix != ".py"
    ):
        issues.append(f"잘못된 --controller-module path: {raw}")
        return None
    return path


def _parse_config(argv: list[str]) -> Config:
    namespace = _argument_parser().parse_args(argv)
    try:
        root = Path(namespace.target).resolve()
        is_directory = root.is_dir()
    except (OSError, RuntimeError) as exc:
        raise UsageError(f"TARGET_DIR resolve 불능: {namespace.target} ({exc})") from exc
    if not is_directory:
        raise UsageError(f"디렉터리 아님 {root}")

    issues: list[str] = []
    raw_modules: list[str] = namespace.controller_module
    if len(raw_modules) != len(set(raw_modules)):
        issues.append("반복 인자 중복: --controller-module")
    modules = [
        path
        for raw in raw_modules
        for path in [_source_path(raw, issues)]
        if path is not None
    ]

    resolved: dict[Path, Path] = {}
    for relative in modules:
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
        except ValueError:
            issues.append(f"root/symlink 탈출: --controller-module={relative}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(
                f"source path resolve 불능: --controller-module={relative} ({exc})"
            )
            continue
        previous = resolved.get(candidate)
        if previous is not None and previous != relative:
            issues.append(
                "선택 source resolved path 중복: "
                f"{previous.as_posix()}, {relative.as_posix()}"
            )
        else:
            resolved[candidate] = relative
    if issues:
        raise UsageError("; ".join(issues))
    return Config(root, tuple(modules))


def _eligible_presentation_path(path: Path) -> bool:
    parts = path.parts
    return (
        path.suffix == ".py"
        and bool(DRIVING_DIR_NAMES & set(parts))
        and not set(parts) & SKIP_DIR_NAMES
        and not set(parts) & TEST_DIR_NAMES
        and not path.name.startswith("test_")
        and not path.name.endswith("_test.py")
        and path.name not in {"test.py", "tests.py", "conftest.py"}
    )


def _filesystem_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    errors: list[str] = []

    def record_error(exc: OSError) -> None:
        errors.append(str(exc))

    for directory, names, filenames in os.walk(
        root, topdown=True, followlinks=False, onerror=record_error
    ):
        relative_directory = Path(directory).relative_to(root)
        names[:] = sorted(
            name
            for name in names
            if not set((*relative_directory.parts, name)) & SKIP_DIR_NAMES
            and name not in TEST_DIR_NAMES
        )
        for filename in sorted(filenames):
            relative = relative_directory / filename
            if _eligible_presentation_path(relative):
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


def _run_git(
    directory: Path,
    arguments: list[str],
    *,
    text: bool,
    context: str,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            capture_output=True,
            text=text,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise UsageError(f"{context} 불능: {exc}") from exc
    return completed


def _git_error(
    completed: subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes],
) -> str:
    if isinstance(completed.stderr, bytes):
        stderr = os.fsdecode(completed.stderr)
        stdout = os.fsdecode(completed.stdout)
    else:
        stderr = completed.stderr
        stdout = completed.stdout
    return stderr.strip() or stdout.strip()


def _git_paths(
    payload: bytes,
    *,
    target_prefix: Path,
    context: str,
) -> set[Path]:
    paths: set[Path] = set()
    for encoded in payload.split(b"\0"):
        if not encoded:
            continue
        git_relative = Path(os.fsdecode(encoded))
        if git_relative.is_absolute() or ".." in git_relative.parts:
            raise UsageError(f"{context} 경로 불능: {git_relative}")
        try:
            target_relative = git_relative.relative_to(target_prefix)
        except ValueError:
            continue
        if _eligible_presentation_path(target_relative):
            paths.add(target_relative)
    return paths


def _production_inventory(root: Path) -> Inventory:
    probe = _run_git(
        root,
        ["rev-parse", "--is-inside-work-tree"],
        text=True,
        context="Git worktree 판정",
    )
    if probe.returncode != 0:
        if _has_git_marker(root):
            raise UsageError(f"Git worktree 판정 불능: {_git_error(probe)}")
        paths = _filesystem_paths(root)
        return Inventory(paths, frozenset(), frozenset(paths), None)
    if probe.stdout.strip() != "true":
        paths = _filesystem_paths(root)
        return Inventory(paths, frozenset(), frozenset(paths), None)

    top = _run_git(
        root,
        ["rev-parse", "--show-toplevel"],
        text=True,
        context="Git worktree root 분석",
    )
    if top.returncode != 0:
        raise UsageError(f"Git worktree root 분석 불능: {_git_error(top)}")
    try:
        git_root = Path(top.stdout.strip()).resolve()
        target_prefix = root.relative_to(git_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise UsageError(f"Git worktree root/target 관계 분석 불능: {exc}") from exc

    listed = _run_git(
        git_root,
        ["ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        text=False,
        context="Git production inventory",
    )
    if listed.returncode != 0:
        raise UsageError(f"Git production inventory 불능: {_git_error(listed)}")
    tracked_result = _run_git(
        git_root,
        ["ls-files", "--cached", "-z"],
        text=False,
        context="Git tracked inventory",
    )
    if tracked_result.returncode != 0:
        raise UsageError(f"Git tracked inventory 불능: {_git_error(tracked_result)}")
    changed_result = _run_git(
        git_root,
        ["diff", "--name-only", "-z", "HEAD", "--"],
        text=False,
        context="Git touched inventory",
    )
    if changed_result.returncode != 0:
        raise UsageError(f"Git touched inventory 불능: {_git_error(changed_result)}")

    paths = _git_paths(
        listed.stdout, target_prefix=target_prefix, context="Git production inventory"
    )
    tracked = _git_paths(
        tracked_result.stdout,
        target_prefix=target_prefix,
        context="Git tracked inventory",
    )
    changed_tracked = _git_paths(
        changed_result.stdout,
        target_prefix=target_prefix,
        context="Git touched inventory",
    )
    changed = changed_tracked | (paths - tracked)
    return Inventory(
        tuple(sorted(paths, key=Path.as_posix)),
        frozenset(tracked),
        frozenset(changed),
        git_root,
    )


def _load_source(root: Path, relative: Path) -> ParsedSource:
    lexical = root / relative
    try:
        resolved = lexical.resolve()
        resolved.relative_to(root)
    except ValueError as exc:
        raise UsageError(f"production source root/symlink 탈출: {relative}") from exc
    except (OSError, RuntimeError) as exc:
        raise UsageError(f"production source resolve 불능: {relative} ({exc})") from exc
    try:
        if not resolved.is_file():
            raise UsageError(f"production source 없음: {relative}")
        source = resolved.read_text(encoding="utf-8")
        compile(source, relative.as_posix(), "exec", dont_inherit=True)
        tree = ast.parse(source, filename=relative.as_posix())
    except UsageError:
        raise
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise UsageError(f"production source 분석 불능: {relative} ({exc})") from exc
    return ParsedSource(relative, source, tree)


def _selected_sources(config: Config, inventory: Inventory) -> list[ParsedSource]:
    inventory_paths = set(inventory.paths)
    issues: list[str] = []
    for path in config.controller_modules:
        if not _eligible_presentation_path(path):
            issues.append(f"선택 source가 eligible production presentation source 아님: {path}")
        elif path not in inventory_paths:
            issues.append(f"선택 source가 production inventory에 없음: {path}")

    parsed: list[ParsedSource] = []
    for path in config.controller_modules:
        try:
            parsed.append(_load_source(config.root, path))
        except UsageError as exc:
            issues.append(str(exc))
    if issues:
        raise UsageError("; ".join(sorted(set(issues))))
    return parsed


def _positional_sources(config: Config, inventory: Inventory) -> list[ParsedSource]:
    candidate_paths = (
        set(inventory.paths)
        if inventory.git_root is None
        else set(inventory.paths) & set(inventory.changed)
    )
    parsed: list[ParsedSource] = []
    for path in sorted(candidate_paths, key=Path.as_posix):
        try:
            parsed.append(_load_source(config.root, path))
        except UsageError:
            # positional 호환 — inventory 실패는 치명이고, 개별 기존 source
            # 파일의 로드 실패는 건너뛴다.
            continue
    return parsed


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
    node: ast.AST,
    bindings: dict[str, Binding],
    *,
    direct_symbol: bool = False,
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
    if isinstance(statement, ast.Assign):
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
            return None
    elif not isinstance(statement.target, ast.Name):
        return None
    value = statement.value
    if value is None or not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name):
        return None
    constructor = _resolve_binding(value.func, bindings, direct_symbol=True)
    if constructor is None or constructor.origin not in OPERATION_CONSTRUCTORS:
        return None
    return Binding(constructor.origin, "framework_instance")


def _join_conditional_bindings(
    alternatives: tuple[dict[str, Binding], ...],
) -> dict[str, Binding]:
    joined: dict[str, Binding] = {}
    names = {name for bindings in alternatives for name in bindings}
    for name in names:
        possible = {bindings.get(name) for bindings in alternatives}
        if len(possible) == 1:
            binding = possible.pop()
            if binding is not None:
                joined[name] = binding
            continue
        proven = [
            binding
            for binding in possible
            if binding is not None
            and (
                binding.kind == "ambiguous"
                or binding.origin in RAW_RESPONSE_ORIGINS
                or (
                    binding.kind == "framework_instance"
                    and binding.origin in OPERATION_CONSTRUCTORS
                )
                or (
                    binding.kind == "symbol_import"
                    and binding.origin == "ninja_extra.route"
                )
            )
        ]
        if proven:
            joined[name] = Binding(proven[0].origin, "ambiguous")
    return joined


def _advance_module_bindings(
    parsed: ParsedSource,
    statements: list[ast.stmt],
    initial: dict[str, Binding],
) -> dict[str, Binding]:
    bindings = dict(initial)
    module = _module_name(parsed.path)
    for statement in statements:
        if isinstance(statement, ast.If):
            body = _advance_module_bindings(parsed, statement.body, bindings)
            orelse = _advance_module_bindings(parsed, statement.orelse, bindings)
            bindings = _join_conditional_bindings((body, orelse))
            continue
        imported = _import_bindings(parsed.path, statement)
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
                f"{module}.{statement.name}", "local_definition"
            )
    return bindings


def _binding_timeline(parsed: ParsedSource) -> BindingTimeline:
    bindings: dict[str, Binding] = {}
    before: dict[int, dict[str, Binding]] = {}
    for node in parsed.tree.body:
        before[id(node)] = dict(bindings)
        bindings = _advance_module_bindings(parsed, [node], bindings)
    return BindingTimeline(before, dict(bindings))


def _class_body_bindings(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, Binding],
) -> dict[int, dict[str, Binding]]:
    bindings = dict(outer)
    before: dict[int, dict[str, Binding]] = {}
    module = _module_name(parsed.path)
    for statement in node.body:
        before[id(statement)] = dict(bindings)
        imported = _import_bindings(parsed.path, statement)
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


def _iter_lexical_nodes(statements: list[ast.stmt]) -> Iterator[ast.AST]:
    stack: list[ast.AST] = list(reversed(statements))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        children = list(ast.iter_child_nodes(node))
        stack.extend(reversed(children))


def _function_arguments(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.arg]:
    arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg is not None:
        arguments.append(node.args.vararg)
    if node.args.kwarg is not None:
        arguments.append(node.args.kwarg)
    return arguments


def _function_local_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> frozenset[str]:
    names = {argument.arg for argument in _function_arguments(node)}
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
        match_as_type = getattr(ast, "MatchAs", None)
        if match_as_type is not None and isinstance(candidate, match_as_type):
            if candidate.name:
                names.add(candidate.name)
        match_star_type = getattr(ast, "MatchStar", None)
        if match_star_type is not None and isinstance(candidate, match_star_type):
            if candidate.name:
                names.add(candidate.name)
        match_mapping_type = getattr(ast, "MatchMapping", None)
        if match_mapping_type is not None and isinstance(candidate, match_mapping_type):
            if candidate.rest:
                names.add(candidate.rest)
        if isinstance(candidate, ast.stmt):
            names.update(_statement_bound_names(candidate))
    return frozenset(names - globals_ - nonlocals)


def _operation_decorator(
    decorator: ast.AST,
    bindings: dict[str, Binding],
    *,
    fail_on_ambiguity: bool,
) -> bool:
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return False
    if decorator.func.attr not in HTTP_METHODS or not isinstance(
        decorator.func.value, ast.Name
    ):
        return False
    receiver = bindings.get(decorator.func.value.id)
    if receiver is None:
        return False
    if receiver.kind == "ambiguous":
        if fail_on_ambiguity:
            raise UsageError(
                "selected operation receiver provenance ambiguous: "
                f"{decorator.func.value.id}"
            )
        return False
    return (
        receiver.kind == "framework_instance"
        and receiver.origin in OPERATION_CONSTRUCTORS
    ) or (
        receiver.kind == "symbol_import" and receiver.origin == "ninja_extra.route"
    )


def _schema_expression(node: ast.AST, bindings: dict[str, Binding]) -> bool:
    if isinstance(node, ast.Name):
        if node.id in {"bool", "bytes", "dict", "float", "int", "list", "str"}:
            return True
        binding = bindings.get(node.id)
        return binding is not None and binding.kind in {
            "local_definition",
            "symbol_import",
        }
    if isinstance(node, ast.Attribute):
        binding = _resolve_binding(node, bindings)
        return binding is not None
    if isinstance(node, ast.Subscript):
        return _schema_expression(node.value, bindings)
    return False


def _body_bearing_response(
    node: ast.AST,
    bindings: dict[str, Binding],
) -> bool:
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if (
                isinstance(key, ast.Constant)
                and isinstance(key.value, int)
                and not isinstance(key.value, bool)
                and key.value in SUCCESS_BODY_STATUSES
                and not (isinstance(value, ast.Constant) and value.value is None)
            ):
                return True
        return False
    if isinstance(node, ast.Constant) and node.value is None:
        return False
    return _schema_expression(node, bindings)


def _decorator_activates(
    decorator: ast.Call,
    bindings: dict[str, Binding],
) -> bool:
    return any(
        keyword.arg == "response"
        and _body_bearing_response(keyword.value, bindings)
        for keyword in decorator.keywords
    )


def _discover_operations(
    parsed: ParsedSource,
    *,
    fail_on_ambiguity: bool,
) -> list[Operation]:
    timeline = _binding_timeline(parsed)
    operations: list[Operation] = []

    def add_operation(
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        definition_bindings: dict[str, Binding],
        enclosure: str,
    ) -> None:
        activating = [
            decorator
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Call)
            and _decorator_activates(decorator, definition_bindings)
            and _operation_decorator(
                decorator,
                definition_bindings,
                fail_on_ambiguity=fail_on_ambiguity,
            )
        ]
        if not activating:
            return
        decorator_line = min(
            getattr(decorator, "lineno", node.lineno) for decorator in activating
        )
        operations.append(
            Operation(
                parsed=parsed,
                node=node,
                identity=f"{enclosure}{node.name}@{decorator_line}",
                body_bindings=dict(timeline.final),
                local_names=_function_local_names(node),
            )
        )

    for statement in parsed.tree.body:
        definition_bindings = timeline.before.get(id(statement), {})
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add_operation(statement, definition_bindings, "")
        elif isinstance(statement, ast.ClassDef):
            class_bindings = _class_body_bindings(
                parsed, statement, definition_bindings
            )
            for member in statement.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add_operation(
                        member,
                        class_bindings.get(id(member), definition_bindings),
                        f"{statement.name}.",
                    )
    return operations


def _raw_success_call(
    operation: Operation,
    node: ast.AST,
    *,
    fail_on_ambiguity: bool,
) -> ast.Call | None:
    if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Call):
        return None
    call = node.value
    if not isinstance(call.func, ast.Name) or call.func.id in operation.local_names:
        return None
    if any(keyword.arg is None for keyword in call.keywords):
        return None
    statuses = [keyword.value for keyword in call.keywords if keyword.arg == "status"]
    if statuses:
        if len(statuses) != 1:
            return None
        status = statuses[0]
        if not (
            isinstance(status, ast.Constant)
            and isinstance(status.value, int)
            and not isinstance(status.value, bool)
            and status.value in SUCCESS_BODY_STATUSES
        ):
            return None
    binding = operation.body_bindings.get(call.func.id)
    if binding is not None and binding.kind == "ambiguous":
        if fail_on_ambiguity:
            raise UsageError(
                "selected raw response provenance ambiguous: " f"{call.func.id}"
            )
        return None
    if (
        binding is None
        or binding.kind != "symbol_import"
        or binding.origin not in RAW_RESPONSE_ORIGINS
    ):
        return None
    return call


def _findings(
    parsed_sources: list[ParsedSource],
    *,
    fail_on_ambiguity: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    for parsed in sorted(parsed_sources, key=lambda source: source.path.as_posix()):
        for operation in _discover_operations(
            parsed,
            fail_on_ambiguity=fail_on_ambiguity,
        ):
            for node in _iter_lexical_nodes(operation.node.body):
                call = _raw_success_call(
                    operation,
                    node,
                    fail_on_ambiguity=fail_on_ambiguity,
                )
                if call is not None:
                    findings.append(
                        Finding(
                            path=parsed.path,
                            operation=operation.identity,
                            lineno=call.lineno,
                        )
                    )
    return sorted(
        findings,
        key=lambda finding: (
            finding.path.as_posix(),
            finding.operation,
            finding.lineno,
        ),
    )


def _run(config: Config) -> tuple[list[Finding], int]:
    inventory = _production_inventory(config.root)
    parsed = (
        _selected_sources(config, inventory)
        if config.selected
        else _positional_sources(config, inventory)
    )
    return _findings(parsed, fail_on_ambiguity=config.selected), len(inventory.paths)


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
    except UsageError as exc:
        print(f"[check-response-schema-bypass] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        return int(exc.code)

    try:
        findings, eligible_count = _run(config)
    except UsageError as exc:
        print(f"[check-response-schema-bypass] 사용 오류: {exc}", file=sys.stderr)
        return 1

    # 대상 0건 가드(#74 · 명세 조각 ⓐ) — 채택 신호는 있는데 driving 층 파일이 0건이면
    # 경로 계약이 어긋난 것이다. touched 공집합(정상)과 달리 «경로 불일치 0건»만 잡는다.
    if eligible_count == 0 and _adopted(config.root):
        print(
            "[check-response-schema-bypass] blocker: 채택 신호는 있는데 driving 층 파일이 "
            "0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        return 2

    if findings:
        print(
            "[check-response-schema-bypass] BLOCKER — an ordinary JSON success "
            "operation declares a body-bearing 200-203 schema but directly "
            "returns raw Django HttpResponse/JsonResponse:"
        )
        for finding in findings:
            print(finding.render())
        print(
            "  근거: a declared Ninja success schema must own validation and "
            "serialization; direct raw 200-203 Django responses bypass that "
            "contract. File/stream/redirect and schema-less 204 paths remain "
            "framework-native carve-outs."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
