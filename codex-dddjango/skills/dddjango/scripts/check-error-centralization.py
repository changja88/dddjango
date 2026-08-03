#!/usr/bin/env python3
"""dddjango code-profile ErrorOut schema contract backstop.

The checker is deliberately profile-gated.  Positional-only, ``auto``, and
``preserve-established`` invocations do not apply schema semantics; preserve
still validates the selectors it supplies.  ``dddjango-code-json`` validates
the canonical common/BC ErrorOut modules, project inventory correspondence,
wire-code uniqueness, and narrow direct raw-string ``code`` forms.

Exit codes: 0=clean/N/A, 2=contract blocker, 1=usage or analysis error.
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


ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
WIRE_CODE_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
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
COMMON_INIT = Path("common/ninja/response/__init__.py")
COMMON_ERROR = Path("common/ninja/response/error_out.py")
COMMON_ERROR_MODULE = "common.ninja.response.error_out"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.ErrorOut"
NINJA_SCHEMA = "ninja.Schema"
STR_ENUM = "enum.StrEnum"
FIELD_FACTORIES = {
    "ninja.Field",
    "pydantic.Field",
    "pydantic.fields.Field",
}
ENUM_BASES = {
    "enum.Enum",
    "enum.IntEnum",
    "enum.StrEnum",
    "enum.Flag",
    "enum.IntFlag",
    "enum.ReprEnum",
}
VALIDATOR_DECORATORS = {
    "pydantic.field_validator",
    "pydantic.model_validator",
    "pydantic.root_validator",
    "pydantic.validator",
}
FIELD_ALIAS_OPTIONS = {
    "alias",
    "validation_alias",
    "serialization_alias",
}
MODEL_CONFIG_ALIAS_OPTIONS = {"alias_generator"}
MATCH_NODES = tuple(
    node_type
    for node_type in (getattr(ast, "Match", None),)
    if node_type is not None
)
MATCH_AS_NODES = tuple(
    node_type
    for node_type in (getattr(ast, "MatchAs", None),)
    if node_type is not None
)
MATCH_STAR_NODES = tuple(
    node_type
    for node_type in (getattr(ast, "MatchStar", None),)
    if node_type is not None
)
MATCH_MAPPING_NODES = tuple(
    node_type
    for node_type in (getattr(ast, "MatchMapping", None),)
    if node_type is not None
)
TRY_NODES = (ast.Try,) + tuple(
    node_type
    for node_type in (getattr(ast, "TryStar", None),)
    if node_type is not None
)


class UsageError(Exception):
    """CLI, inventory, selected-source, or provenance analysis failure."""


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
    code_error_modules: tuple[str, ...]
    preserve_error_modules: tuple[str, ...]


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
class Finding:
    relative_path: Path
    lineno: int
    category: str
    shown: str

    def render(self) -> str:
        return f"  - {self.relative_path}:{self.lineno}  {self.category}: {self.shown}"


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--error-profile", action="append")
    parser.add_argument("--scope", action="append")
    parser.add_argument("--api-module", action="append")
    parser.add_argument("--controller-module", action="append", default=[])
    parser.add_argument("--scope-bc", action="append", default=[])
    parser.add_argument("--error-bc", action="append", default=[])
    parser.add_argument("--project-code-error-module", action="append", default=[])
    parser.add_argument("--project-preserve-error-module", action="append", default=[])
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
    profile = _one("--error-profile", namespace.error_profile, required=False, issues=issues)
    selectors_present = any(
        (
            namespace.scope,
            namespace.api_module,
            namespace.controller_module,
            namespace.scope_bc,
            namespace.error_bc,
            namespace.project_code_error_module,
            namespace.project_preserve_error_module,
        )
    )
    if profile is None and selectors_present:
        issues.append("selector 사용 시 --error-profile 필수")
    if profile is not None and profile not in ERROR_PROFILES:
        issues.append(f"지원하지 않는 --error-profile: {profile}")
    if profile == "auto" and selectors_present:
        issues.append("auto profile에는 selector를 전달하지 않음")

    explicit = profile in {"dddjango-code-json", "preserve-established"}
    code_profile = profile == "dddjango-code-json"
    scope = _one("--scope", namespace.scope, required=explicit, issues=issues)
    api_module = _one(
        "--api-module", namespace.api_module, required=explicit, issues=issues
    )
    controllers = _unique("--controller-module", namespace.controller_module, issues)
    scope_bcs = _unique("--scope-bc", namespace.scope_bc, issues)
    error_bcs = _unique("--error-bc", namespace.error_bc, issues)
    code_modules = _unique(
        "--project-code-error-module", namespace.project_code_error_module, issues
    )
    preserve_modules = _unique(
        "--project-preserve-error-module",
        namespace.project_preserve_error_module,
        issues,
    )
    if explicit and not controllers:
        issues.append("필수 인자 누락: --controller-module")
    if explicit and not scope_bcs:
        issues.append("필수 인자 누락: --scope-bc")
    if code_profile and not code_modules:
        issues.append("필수 인자 누락: --project-code-error-module")
    if scope is not None and not scope.strip():
        issues.append("--scope는 빈 문자열일 수 없음")
    for option, names in (("--scope-bc", scope_bcs), ("--error-bc", error_bcs)):
        for name in names:
            if not BC_NAME_RE.fullmatch(name):
                issues.append(f"잘못된 BC 이름: {option}={name}")
    if not set(error_bcs).issubset(scope_bcs):
        issues.append("--error-bc는 --scope-bc의 부분집합이어야 함")
    if set(code_modules) & set(preserve_modules):
        issues.append("project code/preserve error inventory overlap")

    role_values: list[tuple[str, str]] = []
    if api_module is not None:
        role_values.append(("--api-module", api_module))
    role_values.extend(("--controller-module", raw) for raw in controllers)
    role_values.extend(("--project-code-error-module", raw) for raw in code_modules)
    role_values.extend(
        ("--project-preserve-error-module", raw) for raw in preserve_modules
    )
    lexical: list[tuple[str, Path]] = []
    for option, raw in role_values:
        path = _source_path(option, raw, issues)
        if path is not None:
            lexical.append((option, path))

    resolved: list[tuple[str, Path, Path]] = []
    for option, relative in lexical:
        try:
            candidate = (root / relative).resolve()
            candidate.relative_to(root)
        except ValueError:
            issues.append(f"root/symlink 탈출: {option}={relative.as_posix()}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(f"source path resolve 불능: {option}={relative} ({exc})")
            continue
        resolved.append((option, relative, candidate))

    for index, (left_role, left_rel, left_path) in enumerate(resolved):
        for right_role, right_rel, right_path in resolved[index + 1 :]:
            if left_path != right_path:
                continue
            same_inventory_role = left_role == right_role and left_role.startswith("--project-")
            if same_inventory_role and left_rel == right_rel:
                continue
            issues.append(
                "선택 source role/resolved path overlap: "
                f"{left_role}={left_rel}, {right_role}={right_rel}"
            )

    if issues:
        raise UsageError("; ".join(issues))
    return Config(
        root,
        profile,
        scope,
        api_module,
        controllers,
        scope_bcs,
        error_bcs,
        code_modules,
        preserve_modules,
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


def _bc_error_path(bc: str) -> Path:
    return Path(f"application/{bc}/presentation_layer/schema/error_out.py")


def _candidate_bc(path: Path) -> str | None:
    parts = path.parts
    if (
        len(parts) == 5
        and parts[0] == "application"
        and parts[2:] == ("presentation_layer", "schema", "error_out.py")
        and BC_NAME_RE.fullmatch(parts[1])
    ):
        return parts[1]
    return None


def _is_schema_candidate(path: Path) -> bool:
    return path == COMMON_ERROR or _candidate_bc(path) is not None


def _path_under_bc(path: Path, bc: str) -> bool:
    return len(path.parts) >= 2 and path.parts[:2] == ("application", bc)


def _source_plan(
    config: Config, inventory: CodeInventory
) -> tuple[set[Path], set[Path], set[Path], list[str], list[str]]:
    inventory_paths = set(inventory.relative_paths)
    analysis: list[str] = []
    blockers: list[str] = []
    code_paths = {Path(raw) for raw in config.code_error_modules}
    preserve_paths = {Path(raw) for raw in config.preserve_error_modules}
    source_paths: set[Path] = set()

    common_selected = [Path(config.api_module or "")]
    common_selected.extend(Path(raw) for raw in config.controller_modules)
    common_selected.extend(code_paths)
    common_selected.extend(preserve_paths)
    for path in common_selected:
        if path in inventory_paths:
            source_paths.add(path)
        elif config.profile == "preserve-established" or path not in code_paths:
            analysis.append(f"선택 source가 production inventory에 없음: {path}")

    if config.profile != "dddjango-code-json":
        return source_paths, code_paths, preserve_paths, analysis, blockers

    discovered = {path for path in inventory_paths if _is_schema_candidate(path)}
    union = code_paths | preserve_paths
    if COMMON_ERROR not in code_paths:
        analysis.append(
            "code inventory에 common/ninja/response/error_out.py가 필요함"
        )
    for path in union:
        if not _is_schema_candidate(path):
            analysis.append(f"project error inventory의 noncanonical module: {path}")
    if code_paths & preserve_paths:
        analysis.append("project code/preserve error inventory overlap")

    required_missing = {COMMON_ERROR}
    required_missing.update(_bc_error_path(bc) for bc in config.error_bcs)
    for path in sorted(required_missing, key=Path.as_posix):
        if path not in inventory_paths:
            blockers.append(f"필수 canonical ErrorOut artifact 부재: {path}")
    for bc in config.error_bcs:
        path = _bc_error_path(bc)
        if path in inventory_paths and path not in code_paths:
            analysis.append(f"designated error BC module이 code inventory에 없음: {path}")

    for path in sorted(union - discovered, key=Path.as_posix):
        if path not in required_missing:
            analysis.append(f"project error inventory module이 production candidate에 없음: {path}")
    for path in sorted(discovered - union, key=Path.as_posix):
        analysis.append(f"canonical candidate가 project inventory union에 없음: {path}")

    for bc in config.scope_bcs:
        scoped = {path for path in inventory_paths if _path_under_bc(path, bc)}
        if not scoped:
            analysis.append(f"scope BC production source 없음: application/{bc}/")
        source_paths.update(scoped)
    response_prefix = Path("common/ninja/response")
    source_paths.update(
        path
        for path in inventory_paths
        if path.parent == response_prefix or response_prefix in path.parents
    )
    source_paths.update(discovered)
    return source_paths, code_paths, preserve_paths, analysis, blockers


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
    return ".".join(path.with_suffix("").parts)


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


def _bound_names(node: ast.stmt) -> set[str]:
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
    if isinstance(node, ast.Delete):
        return {name for target in node.targets for name in _target_names(target)}
    return set()


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


def _module_bindings(parsed: ParsedSource) -> dict[int, dict[str, str]]:
    bindings: dict[str, str] = {}
    before: dict[int, dict[str, str]] = {}
    module = _module_name(parsed.relative_path)
    for node in parsed.tree.body:
        before[id(node)] = dict(bindings)
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                bindings[local] = alias.name if alias.asname else local
            continue
        if isinstance(node, ast.ImportFrom):
            imported_module = _absolute_from_module(parsed.relative_path, node)
            if imported_module is not None:
                for alias in node.names:
                    if alias.name != "*":
                        bindings[alias.asname or alias.name] = (
                            f"{imported_module}.{alias.name}"
                        )
                continue
        for name in _bound_names(node):
            bindings.pop(name, None)
        if isinstance(node, ast.ClassDef):
            bindings[node.name] = f"{module}.{node.name}"
    return before


def _resolve(node: ast.AST, bindings: dict[str, str]) -> str | None:
    dotted = _expression_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    imported = bindings.get(first)
    if imported is None:
        return None
    return ".".join((imported, *rest))


def _classvar(annotation: ast.AST, bindings: dict[str, str]) -> bool:
    target = annotation.value if isinstance(annotation, ast.Subscript) else annotation
    dotted = _expression_name(target)
    resolved = _resolve(target, bindings)
    return dotted in {"ClassVar", "typing.ClassVar"} or resolved == "typing.ClassVar"


def _explicit_alias_option(keyword: ast.keyword) -> bool:
    return (
        keyword.arg is not None
        and keyword.arg in FIELD_ALIAS_OPTIONS
        and not (
            isinstance(keyword.value, ast.Constant)
            and keyword.value.value is None
        )
    )


def _contains_field_alias(
    node: ast.AST, bindings: dict[str, str]
) -> bool:
    return any(
        isinstance(candidate, ast.Call)
        and _resolve(candidate.func, bindings) in FIELD_FACTORIES
        and any(_explicit_alias_option(keyword) for keyword in candidate.keywords)
        for candidate in ast.walk(node)
    )


def _model_config_has_alias(node: ast.AST) -> bool:
    def is_alias_entry(key: ast.AST | None, value: ast.AST) -> bool:
        return (
            isinstance(key, ast.Constant)
            and key.value in MODEL_CONFIG_ALIAS_OPTIONS
            and not (isinstance(value, ast.Constant) and value.value is None)
        )

    if isinstance(node, ast.Dict):
        return any(
            is_alias_entry(key, value)
            for key, value in zip(node.keys, node.values)
        )
    if isinstance(node, ast.Call):
        if any(
            keyword.arg in MODEL_CONFIG_ALIAS_OPTIONS
            and not (
                isinstance(keyword.value, ast.Constant)
                and keyword.value.value is None
            )
            for keyword in node.keywords
            if keyword.arg is not None
        ):
            return True
        return any(
            isinstance(argument, ast.Dict) and _model_config_has_alias(argument)
            for argument in node.args
        )
    return False


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


def _base_contract(
    parsed: ParsedSource,
    node: ast.ClassDef,
    bindings: dict[str, str],
    expected: str,
    expected_tail: str,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    category: str,
) -> bool:
    resolved = [_resolve(base, bindings) for base in node.bases]
    if len(node.bases) == 1 and resolved == [expected]:
        return True
    if expected in resolved:
        _append_finding(findings, seen, parsed, node, category)
        return False
    raw_tails = [(_expression_name(base) or "").rsplit(".", 1)[-1] for base in node.bases]
    resolved_tails = [(name or "").rsplit(".", 1)[-1] for name in resolved]
    if expected_tail in raw_tails or expected_tail in resolved_tails:
        analysis.append(
            f"{parsed.relative_path}:{node.lineno} required base provenance 분석 불능: {expected}"
        )
    else:
        _append_finding(findings, seen, parsed, node, category)
    return False


def _class_body_bindings(
    parsed: ParsedSource,
    node: ast.ClassDef,
    initial_bindings: dict[str, str],
) -> dict[int, dict[str, str]]:
    bindings = dict(initial_bindings)
    before: dict[int, dict[str, str]] = {}
    for statement in node.body:
        before[id(statement)] = dict(bindings)
        _update_bindings(parsed, statement, bindings, module_scope=False)
    return before


def _public_annassigns(
    parsed: ParsedSource,
    node: ast.ClassDef,
    initial_bindings: dict[str, str],
) -> dict[str, ast.AnnAssign]:
    fields: dict[str, ast.AnnAssign] = {}
    before = _class_body_bindings(parsed, node, initial_bindings)
    for statement in node.body:
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
            continue
        name = statement.target.id
        bindings = before.get(id(statement), initial_bindings)
        if name.startswith("_") or name == "model_config" or _classvar(statement.annotation, bindings):
            continue
        fields[name] = statement
    return fields


def _class_member_findings(
    parsed: ParsedSource,
    node: ast.ClassDef,
    initial_bindings: dict[str, str],
    allowed_fields: set[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    field_names: set[str] = set()
    before = _class_body_bindings(parsed, node, initial_bindings)
    for statement in node.body:
        bindings = before.get(id(statement), initial_bindings)
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            name = statement.target.id
            if name == "model_config":
                if statement.value is not None and _model_config_has_alias(statement.value):
                    _append_finding(findings, seen, parsed, statement, "model config alias")
                continue
            if name.startswith("_") or _classvar(statement.annotation, bindings):
                continue
            if name in field_names:
                _append_finding(findings, seen, parsed, statement, "duplicate public field")
            field_names.add(name)
            if name not in allowed_fields:
                _append_finding(findings, seen, parsed, statement, "additional public field")
            if (
                statement.value is not None
                and _contains_field_alias(statement.value, bindings)
            ) or _contains_field_alias(statement.annotation, bindings):
                _append_finding(findings, seen, parsed, statement, "field alias")
        elif isinstance(statement, ast.Assign):
            names = {name for target in statement.targets for name in _target_names(target)}
            for name in names:
                if name == "model_config":
                    if _model_config_has_alias(statement.value):
                        _append_finding(findings, seen, parsed, statement, "model config alias")
                elif not name.startswith("_"):
                    _append_finding(findings, seen, parsed, statement, "public class assignment/helper")
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorated_validator = any(
                _resolve(
                    decorator.func if isinstance(decorator, ast.Call) else decorator,
                    bindings,
                )
                in VALIDATOR_DECORATORS
                for decorator in statement.decorator_list
            )
            if decorated_validator or not statement.name.startswith("_"):
                _append_finding(findings, seen, parsed, statement, "validator/public helper")
        elif isinstance(statement, ast.ClassDef) and not statement.name.startswith("_"):
            _append_finding(findings, seen, parsed, statement, "public nested class/helper")


def _assignment_value(statement: ast.stmt) -> ast.AST | None:
    if isinstance(statement, ast.Assign):
        return statement.value
    if isinstance(statement, ast.AnnAssign):
        return statement.value
    return None


def _is_functional_enum(
    statement: ast.stmt, bindings: dict[str, str]
) -> bool:
    value = _assignment_value(statement)
    return (
        isinstance(value, ast.Call)
        and _resolve(value.func, bindings) in ENUM_BASES
    )


def _analyze_common(
    parsed: ParsedSource | None,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> set[str]:
    if parsed is None:
        return set()
    before = _module_bindings(parsed)
    error_outs = [
        node for node in parsed.tree.body if isinstance(node, ast.ClassDef) and node.name == "ErrorOut"
    ]
    if len(error_outs) != 1:
        anchor: ast.AST = error_outs[0] if error_outs else parsed.tree
        _append_finding(findings, seen, parsed, anchor, "exactly one common ErrorOut required")
    required_fields: set[str] = set()
    if len(error_outs) == 1:
        error_out = error_outs[0]
        bindings = before.get(id(error_out), {})
        _base_contract(
            parsed,
            error_out,
            bindings,
            NINJA_SCHEMA,
            "Schema",
            analysis,
            findings,
            seen,
            "common ErrorOut must directly inherit ninja.Schema",
        )
        fields = _public_annassigns(parsed, error_out, bindings)
        for name, field in fields.items():
            if field.value is None:
                required_fields.add(name)
            else:
                _append_finding(findings, seen, parsed, field, "common ErrorOut field must be required")
        _class_member_findings(
            parsed, error_out, bindings, set(fields), findings, seen
        )
        if "code" not in required_fields:
            _append_finding(findings, seen, parsed, error_out, "common ErrorOut requires public code field")

    for node in parsed.tree.body:
        if isinstance(node, ast.ClassDef) and node not in error_outs:
            bindings = before.get(id(node), {})
            inherits_error = any(
                _resolve(base, bindings) == COMMON_ERROR_OUT
                or (_expression_name(base) or "") == "ErrorOut"
                for base in node.bases
            )
            inherits_enum = any(
                _resolve(base, bindings) in ENUM_BASES for base in node.bases
            )
            if inherits_enum or inherits_error or not node.name.startswith("_"):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    node,
                    "common module Enum/public/derived class forbidden",
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _append_finding(findings, seen, parsed, node, "common module helper/function forbidden")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            bindings = before.get(id(node), {})
            if _is_functional_enum(node, bindings):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    node,
                    "common module functional Enum forbidden",
                )
            targets = (
                {name for target in node.targets for name in _target_names(target)}
                if isinstance(node, ast.Assign)
                else _target_names(node.target)
            )
            if any(not name.startswith("_") and name != "model_config" for name in targets):
                _append_finding(findings, seen, parsed, node, "common module public artifact forbidden")
    return required_fields


def _snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _enum_reserved_name(name: str) -> bool:
    if name.startswith("__"):
        return True
    return len(name) > 2 and name.startswith("_") and name.endswith("_")


def _static_enum_ignore_names(value: ast.AST | None) -> set[str] | None:
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return set(value.value.replace(",", " ").split())
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)) and all(
        isinstance(item, ast.Constant) and isinstance(item.value, str)
        for item in value.elts
    ):
        return {item.value for item in value.elts}
    return None


def _enum_ignored_names(
    parsed: ParsedSource,
    node: ast.ClassDef,
    analysis: list[str],
) -> set[str]:
    ignored: set[str] = set()
    for statement in node.body:
        targets: set[str] = set()
        if isinstance(statement, ast.Assign):
            targets = {
                name
                for target in statement.targets
                for name in _target_names(target)
            }
        elif isinstance(statement, ast.AnnAssign):
            targets = _target_names(statement.target)
        if "_ignore_" not in targets:
            continue
        names = _static_enum_ignore_names(_assignment_value(statement))
        if names is None:
            analysis.append(
                f"{parsed.relative_path}:{statement.lineno} dynamic Enum _ignore_ 분석 불능"
            )
        else:
            ignored.update(names)
    return ignored


def _enum_members(
    parsed: ParsedSource,
    node: ast.ClassDef,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> dict[str, str]:
    members: dict[str, str] = {}
    member_names: set[str] = set()
    ignored_names = _enum_ignored_names(parsed, node, analysis)
    for statement in node.body:
        names: list[str] = []
        value: ast.AST | None = None
        if isinstance(statement, ast.Assign):
            if all(isinstance(target, ast.Name) for target in statement.targets):
                names = [target.id for target in statement.targets]
            elif any(
                not _enum_reserved_name(name) and name not in ignored_names
                for target in statement.targets
                for name in _target_names(target)
            ):
                analysis.append(
                    f"{parsed.relative_path}:{statement.lineno} dynamic Enum member shape 분석 불능"
                )
            value = statement.value
        elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            names = [statement.target.id]
            value = statement.value
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not statement.name.startswith("_"):
                _append_finding(findings, seen, parsed, statement, "Enum public helper forbidden")
            continue
        elif isinstance(statement, ast.ClassDef):
            if not statement.name.startswith("_"):
                _append_finding(findings, seen, parsed, statement, "Enum public helper forbidden")
            continue
        enum_names = [
            name
            for name in names
            if not _enum_reserved_name(name) and name not in ignored_names
        ]
        for name in enum_names:
            if value is None:
                continue
            if name in member_names:
                _append_finding(findings, seen, parsed, statement, "duplicate Enum member")
            member_names.add(name)
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                analysis.append(
                    f"{parsed.relative_path}:{statement.lineno} dynamic Enum value 분석 불능: {name}"
                )
                continue
            members[name] = value.value
            if not WIRE_CODE_RE.fullmatch(value.value):
                _append_finding(findings, seen, parsed, statement, "wire code must be snake_case")
    if not member_names:
        _append_finding(findings, seen, parsed, node, "ErrorCode requires a wire-code member")
    counts: dict[str, int] = {}
    for value in members.values():
        counts[value] = counts.get(value, 0) + 1
    for value, count in counts.items():
        if count > 1:
            _append_finding(findings, seen, parsed, node, f"duplicate wire code in Enum: {value}")
    return members


def _analyze_bc_module(
    parsed: ParsedSource,
    bc: str,
    required_fields: set[str],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> tuple[dict[str, str], set[str], str]:
    before = _module_bindings(parsed)
    prefix = _snake_to_pascal(bc)
    enum_name = f"{prefix}ErrorCode"
    base_name = f"{prefix}ErrorOut"
    module = _module_name(parsed.relative_path)
    enum_full = f"{module}.{enum_name}"
    base_full = f"{module}.{base_name}"
    classes = [node for node in parsed.tree.body if isinstance(node, ast.ClassDef)]

    enums = [node for node in classes if node.name == enum_name]
    if len(enums) != 1:
        _append_finding(
            findings,
            seen,
            parsed,
            enums[0] if enums else parsed.tree,
            f"exactly one {enum_name} required",
        )
    for node in classes:
        bindings = before.get(id(node), {})
        is_str_enum = any(_resolve(base, bindings) == STR_ENUM for base in node.bases)
        if node not in enums and (node.name.endswith("ErrorCode") or is_str_enum):
            _append_finding(findings, seen, parsed, node, "second ErrorCode/StrEnum container")
    for node in parsed.tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            bindings = before.get(id(node), {})
            if _is_functional_enum(node, bindings):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    node,
                    "second ErrorCode/StrEnum container",
                )

    members: dict[str, str] = {}
    if len(enums) == 1:
        enum = enums[0]
        bindings = before.get(id(enum), {})
        _base_contract(
            parsed,
            enum,
            bindings,
            STR_ENUM,
            "StrEnum",
            analysis,
            findings,
            seen,
            f"{enum_name} must directly inherit enum.StrEnum",
        )
        members = _enum_members(parsed, enum, analysis, findings, seen)

    bases = [node for node in classes if node.name == base_name]
    if len(bases) != 1:
        _append_finding(
            findings,
            seen,
            parsed,
            bases[0] if bases else parsed.tree,
            f"exactly one {base_name} required",
        )
    for node in classes:
        bindings = before.get(id(node), {})
        direct_common = any(_resolve(base, bindings) == COMMON_ERROR_OUT for base in node.bases)
        if node not in bases and (node.name.endswith("ErrorOut") or direct_common):
            _append_finding(findings, seen, parsed, node, "second BC ErrorOut base")

    if len(bases) == 1:
        base = bases[0]
        bindings = before.get(id(base), {})
        _base_contract(
            parsed,
            base,
            bindings,
            COMMON_ERROR_OUT,
            "ErrorOut",
            analysis,
            findings,
            seen,
            f"{base_name} must directly inherit common ErrorOut",
        )
        fields = _public_annassigns(parsed, base, bindings)
        field_bindings = _class_body_bindings(parsed, base, bindings)
        if set(fields) != {"code"}:
            _append_finding(findings, seen, parsed, base, "BC ErrorOut base may expose only code")
        code_field = fields.get("code")
        if code_field is not None:
            if code_field.value is not None:
                _append_finding(findings, seen, parsed, code_field, "BC base code must have no default")
            code_bindings = field_bindings.get(id(code_field), bindings)
            if _resolve(code_field.annotation, code_bindings) != enum_full:
                _append_finding(findings, seen, parsed, code_field, "BC base code type must be own ErrorCode")
        _class_member_findings(parsed, base, bindings, {"code"}, findings, seen)

    known_concrete: set[str] = set()
    for node in classes:
        bindings = before.get(id(node), {})
        is_str_enum = any(_resolve(base, bindings) == STR_ENUM for base in node.bases)
        direct_common = any(_resolve(base, bindings) == COMMON_ERROR_OUT for base in node.bases)
        invalid_container = (
            node.name.endswith("ErrorCode")
            or is_str_enum
            or node.name.endswith("ErrorOut")
            or direct_common
        )
        raw_base_names = {
            (_expression_name(base) or "").rsplit(".", 1)[-1] for base in node.bases
        }
        prepared_by_base = any(
            _resolve(base, bindings) == base_full for base in node.bases
        ) or base_name in raw_base_names
        if node in enums or node in bases or invalid_container:
            continue
        if node.name.startswith("_") and not prepared_by_base:
            continue
        if not _base_contract(
            parsed,
            node,
            bindings,
            base_full,
            base_name,
            analysis,
            findings,
            seen,
            f"{node.name} must directly inherit {base_name}",
        ):
            continue
        known_concrete.add(f"{module}.{node.name}")
        fields = _public_annassigns(parsed, node, bindings)
        field_bindings = _class_body_bindings(parsed, node, bindings)
        for field_name in set(fields) - required_fields:
            _append_finding(findings, seen, parsed, fields[field_name], "concrete adds field outside common shape")
        for required in required_fields:
            field = fields.get(required)
            if field is None or field.value is None:
                _append_finding(findings, seen, parsed, node, f"concrete missing required default: {required}")
        code_field = fields.get("code")
        if code_field is not None and code_field.value is not None:
            if isinstance(code_field.value, ast.Constant) and isinstance(code_field.value.value, str):
                _append_finding(findings, seen, parsed, code_field, "raw string ErrorOut code")
            code_bindings = field_bindings.get(id(code_field), bindings)
            resolved_default = _resolve(code_field.value, code_bindings)
            valid_values = {f"{enum_full}.{name}" for name in members}
            if resolved_default not in valid_values:
                _append_finding(findings, seen, parsed, code_field, "concrete code default must use own ErrorCode member")
        _class_member_findings(parsed, node, bindings, required_fields, findings, seen)
    return members, known_concrete, base_full


def _function_argument_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    positional = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    names = {argument.arg for argument in positional}
    if node.args.vararg is not None:
        names.add(node.args.vararg.arg)
    if node.args.kwarg is not None:
        names.add(node.args.kwarg.arg)
    return names


def _pattern_bound_names(pattern: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(pattern):
        if isinstance(node, MATCH_AS_NODES) and node.name is not None:
            names.add(node.name)
        elif isinstance(node, MATCH_STAR_NODES) and node.name is not None:
            names.add(node.name)
        elif isinstance(node, MATCH_MAPPING_NODES) and node.rest is not None:
            names.add(node.rest)
    return names


class _FunctionLocalCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.bound: set[str] = set()
        self.globals: set[str] = set()
        self.nonlocals: set[str] = set()

    def visit_Global(self, node: ast.Global) -> None:
        self.globals.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.nonlocals.update(node.names)

    def visit_Import(self, node: ast.Import) -> None:
        self.bound.update(_bound_names(node))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.bound.update(_bound_names(node))

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self.bound.update(_target_names(target))
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.bound.update(_target_names(node.target))
        self.visit(node.annotation)
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.bound.update(_target_names(node.target))
        self.visit(node.value)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self.bound.update(_target_names(target))

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.bound.update(_target_names(node.target))
        self.visit(node.value)

    def visit_For(self, node: ast.For) -> None:
        self.bound.update(_target_names(node.target))
        self.visit(node.iter)
        for statement in (*node.body, *node.orelse):
            self.visit(statement)

    visit_AsyncFor = visit_For

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                self.bound.update(_target_names(item.optional_vars))
        for statement in node.body:
            self.visit(statement)

    visit_AsyncWith = visit_With

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.bound.add(node.name)
        if node.type is not None:
            self.visit(node.type)
        for statement in node.body:
            self.visit(statement)

    def visit_Match(self, node: ast.AST) -> None:
        self.visit(node.subject)
        for case in node.cases:
            self.bound.update(_pattern_bound_names(case.pattern))
            if case.guard is not None:
                self.visit(case.guard)
            for statement in case.body:
                self.visit(statement)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.bound.add(node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.bound.add(node.name)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.visit(node.iter)
        for condition in node.ifs:
            self.visit(condition)


def _function_local_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    collector = _FunctionLocalCollector()
    collector.bound.update(_function_argument_names(node))
    for statement in node.body:
        collector.visit(statement)
    return (collector.bound - collector.globals) | collector.nonlocals


def _statement_expression_roots(statement: ast.stmt) -> list[ast.AST]:
    if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return [statement.value] if statement.value is not None else []
    if isinstance(statement, ast.Expr):
        return [statement.value]
    if isinstance(statement, ast.Return):
        return [statement.value] if statement.value is not None else []
    if isinstance(statement, ast.Raise):
        return [node for node in (statement.exc, statement.cause) if node is not None]
    if isinstance(statement, ast.Assert):
        return [node for node in (statement.test, statement.msg) if node is not None]
    if isinstance(statement, (ast.If, ast.While)):
        return [statement.test]
    if isinstance(statement, (ast.For, ast.AsyncFor)):
        return [statement.iter]
    if isinstance(statement, (ast.With, ast.AsyncWith)):
        return [item.context_expr for item in statement.items]
    if isinstance(statement, MATCH_NODES):
        return [statement.subject]
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
        defaults = [*statement.args.defaults]
        defaults.extend(
            default for default in statement.args.kw_defaults if default is not None
        )
        return [*statement.decorator_list, *defaults]
    if isinstance(statement, ast.ClassDef):
        return [
            *statement.decorator_list,
            *statement.bases,
            *(keyword.value for keyword in statement.keywords),
        ]
    return []


def _statement_shadow_names(statement: ast.stmt) -> set[str]:
    names = _bound_names(statement)
    if isinstance(statement, (ast.For, ast.AsyncFor)):
        names.update(_target_names(statement.target))
    elif isinstance(statement, (ast.With, ast.AsyncWith)):
        for item in statement.items:
            if item.optional_vars is not None:
                names.update(_target_names(item.optional_vars))
    elif isinstance(statement, MATCH_NODES):
        for case in statement.cases:
            names.update(_pattern_bound_names(case.pattern))
    return names


def _raw_constructor_calls(
    parsed: ParsedSource,
    roots: list[ast.AST],
    bindings: dict[str, str],
    known_classes: set[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    for root in roots:
        for call in (node for node in ast.walk(root) if isinstance(node, ast.Call)):
            if _resolve(call.func, bindings) not in known_classes:
                continue
            for keyword in call.keywords:
                if (
                    keyword.arg == "code"
                    and isinstance(keyword.value, ast.Constant)
                    and isinstance(keyword.value.value, str)
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        keyword,
                        "raw string code constructor argument",
                    )


def _update_bindings(
    parsed: ParsedSource,
    statement: ast.stmt,
    bindings: dict[str, str],
    *,
    module_scope: bool,
) -> None:
    if isinstance(statement, ast.Import):
        for alias in statement.names:
            local = alias.asname or alias.name.split(".", 1)[0]
            bindings[local] = alias.name if alias.asname else local
        return
    if isinstance(statement, ast.ImportFrom):
        imported_module = _absolute_from_module(parsed.relative_path, statement)
        if imported_module is not None:
            for alias in statement.names:
                if alias.name != "*":
                    bindings[alias.asname or alias.name] = (
                        f"{imported_module}.{alias.name}"
                    )
        return
    for name in _statement_shadow_names(statement):
        bindings.pop(name, None)
    if module_scope and isinstance(statement, ast.ClassDef):
        bindings[statement.name] = f"{_module_name(parsed.relative_path)}.{statement.name}"


def _final_module_bindings(parsed: ParsedSource) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for statement in parsed.tree.body:
        _update_bindings(parsed, statement, bindings, module_scope=True)
    return bindings


def _merge_object_bindings(
    *states: dict[str, str],
) -> dict[str, str]:
    merged: dict[str, str] = {}
    for state in states:
        for name, constructor in state.items():
            merged.setdefault(name, constructor)
    return merged


def _suite_may_break_current_loop(statements: list[ast.stmt]) -> bool:
    def may_break(node: ast.AST) -> bool:
        if isinstance(node, ast.Break):
            return True
        if isinstance(
            node,
            (
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Lambda,
            ),
        ):
            return False
        return any(may_break(child) for child in ast.iter_child_nodes(node))

    return any(may_break(statement) for statement in statements)


def _raw_code_suite(
    parsed: ParsedSource,
    statements: list[ast.stmt],
    initial_bindings: dict[str, str],
    initial_objects: dict[str, str],
    known_classes: set[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    *,
    module_scope: bool,
    function_globals: dict[str, str],
) -> dict[str, str]:
    bindings = dict(initial_bindings)
    local_objects = dict(initial_objects)
    for statement in statements:
        _raw_constructor_calls(
            parsed,
            _statement_expression_roots(statement),
            bindings,
            known_classes,
            findings,
            seen,
        )

        value: ast.AST | None = None
        targets: list[ast.AST] = []
        if isinstance(statement, ast.Assign):
            value = statement.value
            targets = statement.targets
        elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
            value = statement.value
            targets = [statement.target]
        shadow_names = _statement_shadow_names(statement)
        for name in shadow_names:
            local_objects.pop(name, None)
        target_names = {name for target in targets for name in _target_names(target)}
        if isinstance(value, ast.Call):
            constructor = _resolve(value.func, bindings)
            if constructor in known_classes:
                for name in target_names:
                    local_objects[name] = constructor
        if isinstance(statement, (ast.Assign, ast.AnnAssign)) and isinstance(
            statement.value, ast.Constant
        ) and isinstance(statement.value.value, str):
            assignment_targets = (
                statement.targets
                if isinstance(statement, ast.Assign)
                else [statement.target]
            )
            for target in assignment_targets:
                if (
                    isinstance(target, ast.Attribute)
                    and target.attr == "code"
                    and isinstance(target.value, ast.Name)
                    and target.value.id in local_objects
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "raw string one-step object.code assignment",
                    )

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            child_bindings = dict(function_globals)
            for name in _function_local_names(statement):
                child_bindings.pop(name, None)
            _raw_code_suite(
                parsed,
                statement.body,
                child_bindings,
                {},
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
        elif isinstance(statement, ast.ClassDef):
            _raw_code_suite(
                parsed,
                statement.body,
                bindings,
                {},
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
        elif isinstance(statement, ast.If):
            body_objects = _raw_code_suite(
                parsed,
                statement.body,
                bindings,
                local_objects,
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
            if statement.orelse:
                else_objects = _raw_code_suite(
                    parsed,
                    statement.orelse,
                    bindings,
                    local_objects,
                    known_classes,
                    findings,
                    seen,
                    module_scope=False,
                    function_globals=function_globals,
                )
            else:
                else_objects = dict(local_objects)
            local_objects = _merge_object_bindings(body_objects, else_objects)
        elif isinstance(statement, (ast.For, ast.AsyncFor, ast.While)):
            child_bindings = dict(bindings)
            child_objects = dict(local_objects)
            for name in shadow_names:
                child_bindings.pop(name, None)
                child_objects.pop(name, None)
            body_objects = _raw_code_suite(
                parsed,
                statement.body,
                child_bindings,
                child_objects,
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
            loop_objects = _merge_object_bindings(child_objects, body_objects)
            if statement.orelse:
                else_objects = _raw_code_suite(
                    parsed,
                    statement.orelse,
                    child_bindings,
                    loop_objects,
                    known_classes,
                    findings,
                    seen,
                    module_scope=False,
                    function_globals=function_globals,
                )
            else:
                else_objects = loop_objects
            if statement.orelse and not _suite_may_break_current_loop(
                statement.body
            ):
                local_objects = else_objects
            else:
                local_objects = _merge_object_bindings(
                    loop_objects, else_objects
                )
        elif isinstance(statement, (ast.With, ast.AsyncWith)):
            child_bindings = dict(bindings)
            child_objects = dict(local_objects)
            for name in shadow_names:
                child_bindings.pop(name, None)
                child_objects.pop(name, None)
            local_objects = _raw_code_suite(
                parsed,
                statement.body,
                child_bindings,
                child_objects,
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
        elif isinstance(statement, MATCH_NODES):
            path_objects = [dict(local_objects)]
            for case in statement.cases:
                case_bindings = dict(bindings)
                case_objects = dict(local_objects)
                for name in _pattern_bound_names(case.pattern):
                    case_bindings.pop(name, None)
                    case_objects.pop(name, None)
                if case.guard is not None:
                    _raw_constructor_calls(
                        parsed,
                        [case.guard],
                        case_bindings,
                        known_classes,
                        findings,
                        seen,
                    )
                path_objects.append(
                    _raw_code_suite(
                        parsed,
                        case.body,
                        case_bindings,
                        case_objects,
                        known_classes,
                        findings,
                        seen,
                        module_scope=False,
                        function_globals=function_globals,
                    )
                )
            local_objects = _merge_object_bindings(*path_objects)
        elif isinstance(statement, TRY_NODES):
            body_objects = _raw_code_suite(
                parsed,
                statement.body,
                bindings,
                local_objects,
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
            normal_objects = _raw_code_suite(
                parsed,
                statement.orelse,
                bindings,
                body_objects,
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )
            path_objects = [normal_objects]
            for handler in statement.handlers:
                handler_bindings = dict(bindings)
                handler_objects = dict(local_objects)
                if handler.name is not None:
                    handler_bindings.pop(handler.name, None)
                    handler_objects.pop(handler.name, None)
                path_objects.append(
                    _raw_code_suite(
                        parsed,
                        handler.body,
                        handler_bindings,
                        handler_objects,
                        known_classes,
                        findings,
                        seen,
                        module_scope=False,
                        function_globals=function_globals,
                    )
                )
            local_objects = _raw_code_suite(
                parsed,
                statement.finalbody,
                bindings,
                _merge_object_bindings(*path_objects),
                known_classes,
                findings,
                seen,
                module_scope=False,
                function_globals=function_globals,
            )

        _update_bindings(
            parsed, statement, bindings, module_scope=module_scope
        )
    return local_objects


def _raw_code_findings(
    parsed: ParsedSource,
    known_classes: set[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    function_globals = _final_module_bindings(parsed)
    _raw_code_suite(
        parsed,
        parsed.tree.body,
        {},
        {},
        known_classes,
        findings,
        seen,
        module_scope=True,
        function_globals=function_globals,
    )


def _schema_findings(
    config: Config,
    inventory: CodeInventory,
    parsed: dict[Path, ParsedSource],
    code_paths: set[Path],
    preserve_paths: set[Path],
    initial_blockers: list[str],
) -> tuple[list[str], list[Finding], list[str]]:
    analysis: list[str] = []
    findings: list[Finding] = []
    seen: set[tuple[Path, int, str]] = set()
    structural_blockers = list(initial_blockers)

    inventory_paths = set(inventory.relative_paths)
    response_files = {
        path
        for path in inventory_paths
        if path.parent == Path("common/ninja/response")
        or Path("common/ninja/response") in path.parents
    }
    if COMMON_INIT not in inventory_paths:
        structural_blockers.append(f"필수 common artifact 부재: {COMMON_INIT}")
    else:
        init_source = parsed.get(COMMON_INIT)
        if init_source is not None and init_source.source.encode("utf-8") != b"":
            structural_blockers.append(f"common response __init__.py는 byte-empty여야 함: {COMMON_INIT}")
    if COMMON_ERROR not in inventory_paths:
        structural_blockers.append(f"필수 common artifact 부재: {COMMON_ERROR}")
    for extra in sorted(response_files - {COMMON_INIT, COMMON_ERROR}, key=Path.as_posix):
        structural_blockers.append(f"common response extra production module 금지: {extra}")

    required_fields = _analyze_common(
        parsed.get(COMMON_ERROR), analysis, findings, seen
    )
    all_wire_values: dict[str, list[tuple[Path, str]]] = {}
    known_classes = {COMMON_ERROR_OUT}
    known_bases: set[str] = set()
    for path in sorted(code_paths, key=Path.as_posix):
        bc = _candidate_bc(path)
        source = parsed.get(path)
        if bc is None or source is None:
            continue
        members, concretes, base_full = _analyze_bc_module(
            source, bc, required_fields, analysis, findings, seen
        )
        known_classes.add(base_full)
        known_classes.update(concretes)
        known_bases.add(base_full)
        for member, value in members.items():
            all_wire_values.setdefault(value, []).append((path, member))
    for value, owners in all_wire_values.items():
        if len(owners) > 1:
            path, _ = owners[0]
            source = parsed.get(path)
            if source is not None:
                _append_finding(
                    findings,
                    seen,
                    source,
                    source.tree,
                    f"duplicate project code wire value: {value}",
                )

    for path, source in parsed.items():
        if path in code_paths or path in preserve_paths:
            continue
        if not any(_path_under_bc(path, bc) for bc in config.scope_bcs):
            continue
        before = _module_bindings(source)
        for node in source.tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bindings = before.get(id(node), {})
            if any(_resolve(base, bindings) in known_bases for base in node.bases):
                _append_finding(findings, seen, source, node, "concrete ErrorOut outside canonical module")

    raw_paths = {Path(raw) for raw in config.controller_modules}
    raw_paths.update(code_paths)
    for path in sorted(raw_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is not None:
            _raw_code_findings(source, known_classes, findings, seen)
    return sorted(set(analysis)), sorted(
        findings, key=lambda item: (item.relative_path.as_posix(), item.lineno, item.category)
    ), sorted(set(structural_blockers))


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
    except UsageError as exc:
        print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        return int(exc.code)

    if config.profile in {None, "auto"}:
        return 0
    try:
        inventory = _production_inventory(config.root)
        source_paths, code_paths, preserve_paths, plan_analysis, blockers = _source_plan(
            config, inventory
        )
        parsed, source_analysis = _load_sources(config.root, source_paths)
        analysis = [*plan_analysis, *source_analysis]
        findings: list[Finding] = []
        if config.profile == "dddjango-code-json":
            semantic_analysis, findings, blockers = _schema_findings(
                config,
                inventory,
                parsed,
                code_paths,
                preserve_paths,
                blockers,
            )
            analysis.extend(semantic_analysis)
        if analysis:
            raise UsageError("; ".join(sorted(set(analysis))))
    except UsageError as exc:
        print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
        return 1

    if findings or blockers:
        print(
            "[check-error-centralization] BLOCKER — code-profile ErrorOut schema, "
            "inventory, or raw code contract violation:"
        )
        for blocker in blockers:
            print(f"  - {blocker}")
        for finding in findings:
            print(finding.render())
        print(
            "  근거: common ErrorOut는 동적 required wire shape의 단일 기반이고, 각 BC는 "
            "canonical ErrorCode/ErrorOut hierarchy와 project-wide unique wire code를 소유한다."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
