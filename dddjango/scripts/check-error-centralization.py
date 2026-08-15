#!/usr/bin/env python3
"""dddjango code-profile FrameworkErrorSchema schema contract backstop.

The checker is deliberately profile-gated.  Positional-only, ``auto``, and
``preserve-established`` invocations do not apply schema semantics; preserve
still validates the selectors it supplies.  ``dddjango-code-json`` validates
the canonical common/BC FrameworkErrorSchema modules, project inventory correspondence,
wire-code uniqueness, and narrow direct raw-string discriminator forms.

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

import checker_target
from dataclasses import dataclass
from pathlib import Path

try:
    import anchor_diff
    import standard_tree as _stree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/anchor_diff.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)


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
COMMON_INIT = Path("framework/ninja/__init__.py")
COMMON_ERROR = Path("framework/ninja/framework_error_schema.py")
COMMON_VALIDATION = Path("framework/ninja/framework_validation_error_schema.py")
COMMON_ERROR_MODULE = "framework.ninja.framework_error_schema"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.FrameworkErrorSchema"
NINJA_SCHEMA = "ninja.Schema"
STR_ENUM = "enum.StrEnum"
FIELD_FACTORIES = {
    "ninja.Field",
    "pydantic.Field",
    "pydantic.fields.Field",
}
ALIAS_CHOICES_FACTORIES = {
    "pydantic.AliasChoices",
    "pydantic.aliases.AliasChoices",
}
ALIAS_PATH_FACTORIES = {
    "pydantic.AliasPath",
    "pydantic.aliases.AliasPath",
}
STATIC_CONFIG_FACTORIES = {
    "dict",
    "builtins.dict",
    "pydantic.ConfigDict",
    "pydantic.config.ConfigDict",
}
STATIC_FIELD_CONTRACT_FACTORIES = (
    FIELD_FACTORIES
    | ALIAS_CHOICES_FACTORIES
    | ALIAS_PATH_FACTORIES
)
FIELD_CONTRACT_SYMBOL_PREFIXES = (
    "builtins.",
    "pydantic.",
    "pydantic_core.",
    "typing.",
    "typing_extensions.",
)
STATIC_ALIAS_GENERATORS = {
    "pydantic.alias_generators.to_camel",
    "pydantic.alias_generators.to_pascal",
    "pydantic.alias_generators.to_snake",
}
STATIC_FIELD_DEFAULT_FACTORIES = {
    "bool",
    "builtins.bool",
    "builtins.bytes",
    "builtins.dict",
    "builtins.float",
    "builtins.frozenset",
    "builtins.int",
    "builtins.list",
    "builtins.set",
    "builtins.str",
    "builtins.tuple",
    "bytes",
    "dict",
    "float",
    "frozenset",
    "int",
    "list",
    "set",
    "str",
    "tuple",
}
STATIC_FIELD_SENTINELS = {
    "pydantic.fields.PydanticUndefined",
    "pydantic_core.PydanticUndefined",
    "pydantic_core._pydantic_core.PydanticUndefined",
}
STATIC_LITERAL_PREFIX = "<static-literal>:"
STATIC_AST_PREFIX = "<static-ast>:"
BUILTIN_CONTRACT_SYMBOLS = {
    "None",
    "bool",
    "bytes",
    "complex",
    "dict",
    "float",
    "frozenset",
    "int",
    "list",
    "object",
    "set",
    "str",
    "tuple",
    "type",
}
ENUM_BASES = {
    "enum.Enum",
    "enum.IntEnum",
    "enum.StrEnum",
    "enum.Flag",
    "enum.IntFlag",
    "enum.ReprEnum",
}
SCHEMA_DECORATORS = {
    "pydantic.computed_field",
    "pydantic.field_serializer",
    "pydantic.field_validator",
    "pydantic.model_serializer",
    "pydantic.model_validator",
    "pydantic.root_validator",
    "pydantic.validator",
}
SCHEMA_DECORATOR_TAILS = {
    "computed_field",
    "field_serializer",
    "field_validator",
    "model_serializer",
    "model_validator",
    "root_validator",
    "validator",
}
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
    anchor: str | None
    anchor_debt_file: str | None
    anchor_baseline: bool


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
    # Enum 멤버 «정적» 해석에 종속된 판정 — 동적 error shape 토큰만 남은 실행에서는
    # 억제되어 runtime proof 경로가 대신 검증한다(#15 requires_static_error_shape 동형).
    requires_static_error_shape: bool = False

    def render(self) -> str:
        return f"  - {self.relative_path}:{self.lineno}  {self.category}: {self.shown}"


NodeSignature = tuple[object, ...]


@dataclass(frozen=True)
class CommonFieldContract:
    """Observed common FrameworkErrorSchema field contract; no property name is predefined."""

    annotation: NodeSignature
    discriminator_annotation: NodeSignature | None
    metadata: tuple[NodeSignature, ...]
    required: bool
    default: NodeSignature
    constructor_keys: frozenset[str]
    constructor_paths: frozenset[tuple[str | int, ...]]
    constructor_keys_complete: bool


@dataclass(frozen=True)
class KnownErrorClass:
    discriminator_keys: frozenset[str]
    discriminator_paths: frozenset[tuple[str | int, ...]]
    keys_complete: bool
    wire_values: frozenset[str]
    alias_analysis: list[str]


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
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        raise UsageError(bad_target_reason)
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

    if namespace.anchor is not None and namespace.anchor_baseline:
        issues.append(f"--anchor 와 {anchor_diff.BASELINE_FLAG} 는 함께 전달할 수 없음")
    if namespace.anchor_debt_file is not None and namespace.anchor is None:
        issues.append(f"{anchor_diff.DEBT_FLAG} 는 --anchor 와 함께만 쓸 수 있음(차분 전용 빚 채널)")
    if namespace.anchor_baseline and anchor_diff.is_git_worktree(root):
        issues.append(
            f"{anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용 — git 저장소 TARGET 금지"
        )
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
    if explicit and not controllers and not namespace.anchor_baseline:
        # anchor-baseline 모드에선 앵커 트리에 없는 controller 가 걷혀 빈 집합이 정상이다.
        issues.append("필수 인자 누락: --controller-module")
    if explicit and not scope_bcs:
        issues.append("필수 인자 누락: --scope-bc")
    if code_profile and not code_modules and not namespace.anchor_baseline:
        # anchor-baseline 모드에선 앵커 트리에 없는 inventory module 도 걷힌다(동상).
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
        namespace.anchor,
        namespace.anchor_debt_file,
        namespace.anchor_baseline,
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
    return Path(f"application/{bc}/driving_layer/api/bc_error_schema.py")


def _candidate_bc(path: Path) -> str | None:
    parts = path.parts
    if (
        len(parts) == 5
        and parts[0] == "application"
        and parts[2:] == ("driving_layer", "api", "bc_error_schema.py")
        and BC_NAME_RE.fullmatch(parts[1])
    ):
        return parts[1]
    return None


def _is_schema_candidate(path: Path) -> bool:
    return path == COMMON_ERROR or _candidate_bc(path) is not None


def _skeleton_placeholder_module(root: Path, path: Path) -> bool:
    """내용 없는 골격 파일(#114 «빈 파일»)인가 — inventory 대응 의무 면제 판정.

    렌더 계약(2026-08-15)이 «내용 없는 골격 파일(빈 모듈)»을 project inventory 에서
    제외하므로, 그 파일이 union 에 없는 것은 분석 오류가 아니다(내용이 생긴 뒤부터
    검사한다). 판정은 보수적이다: 읽기·파싱 불능이거나 docstring 밖 문장이 하나라도
    있으면 placeholder 가 아니다(기존 fail-closed 분석 오류 유지).
    """
    try:
        body = ast.parse((root / path).read_text(encoding="utf-8")).body
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return False
    return not body or (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


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
            "code inventory에 framework/ninja/framework_error_schema.py가 필요함"
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
            blockers.append(f"필수 canonical FrameworkErrorSchema artifact 부재: {path}")
    for bc in config.error_bcs:
        path = _bc_error_path(bc)
        if path in inventory_paths and path not in code_paths:
            analysis.append(f"designated error BC module이 code inventory에 없음: {path}")

    for path in sorted(union - discovered, key=Path.as_posix):
        if path not in required_missing:
            analysis.append(f"project error inventory module이 production candidate에 없음: {path}")
    for path in sorted(discovered - union, key=Path.as_posix):
        if _skeleton_placeholder_module(config.root, path):
            continue  # 렌더 계약이 제외한 빈 골격 — _skeleton_placeholder_module docstring
        analysis.append(f"canonical candidate가 project inventory union에 없음: {path}")

    for bc in config.scope_bcs:
        scoped = {path for path in inventory_paths if _path_under_bc(path, bc)}
        if not scoped and not config.anchor_baseline:
            # anchor-baseline 모드에선 앵커 트리에 없는 scope BC 가 정상이다 —
            # 그 표면의 진단은 정의상 전건 신규라 기준선에 있을 수 없다.
            analysis.append(f"scope BC production source 없음: application/{bc}/")
        source_paths.update(scoped)
    # 정본 공용 모듈(#417) — framework/ninja/ 는 공유 <technology> 폴더라 오류 계약 파일만 끌어온다.
    common_files = {COMMON_INIT, COMMON_ERROR, COMMON_VALIDATION}
    source_paths.update(path for path in inventory_paths if path in common_files)
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


def _project_module_prefixes(paths: tuple[Path, ...]) -> set[str]:
    """Return importable project package/module prefixes from inventory paths."""

    prefixes: set[str] = set()
    for path in paths:
        parts = list(path.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        for end in range(1, len(parts) + 1):
            prefixes.add(".".join(parts[:end]))
    return prefixes


def _project_import_nodes(
    parsed: ParsedSource,
    project_module_prefixes: set[str],
    *,
    allowed_modules: frozenset[str] = frozenset(),
    recursive: bool = False,
) -> list[ast.stmt]:
    nodes: list[ast.stmt] = []
    statements = ast.walk(parsed.tree) if recursive else parsed.tree.body
    for statement in statements:
        imported_modules: list[str | None] = []
        if isinstance(statement, ast.Import):
            imported_modules.extend(alias.name for alias in statement.names)
        elif isinstance(statement, ast.ImportFrom):
            imported_modules.append(
                _absolute_from_module(parsed.relative_path, statement)
            )
        if any(
            imported is None
            or (
                imported in project_module_prefixes
                and imported not in allowed_modules
            )
            for imported in imported_modules
        ):
            nodes.append(statement)
    return nodes


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
        else:
            _bind_static_assignment(node, bindings)
    return before


def _resolve(node: ast.AST, bindings: dict[str, str]) -> str | None:
    dotted = _expression_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    imported = bindings.get(first)
    if imported is None:
        return None
    if imported.startswith((STATIC_LITERAL_PREFIX, STATIC_AST_PREFIX)):
        return imported if not rest else None
    return ".".join((imported, *rest))


def _static_literal_binding(value: object) -> str:
    return f"{STATIC_LITERAL_PREFIX}{type(value).__name__}:{value!r}"


def _static_literal_value(binding: str | None) -> object:
    if binding is None or not binding.startswith(STATIC_LITERAL_PREFIX):
        return _NO_STATIC_VALUE
    _prefix, _separator, payload = binding.partition(STATIC_LITERAL_PREFIX)
    type_name, separator, literal = payload.partition(":")
    if not separator:
        return _NO_STATIC_VALUE
    try:
        value = ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return _NO_STATIC_VALUE
    return value if type(value).__name__ == type_name else _NO_STATIC_VALUE


_NO_STATIC_VALUE = object()


def _static_ast_value(binding: str | None) -> ast.AST | None:
    if binding is None or not binding.startswith(STATIC_AST_PREFIX):
        return None
    try:
        return ast.parse(
            binding.removeprefix(STATIC_AST_PREFIX),
            mode="eval",
        ).body
    except SyntaxError:
        return None


def _static_assignment_binding(
    value: ast.AST | None,
    bindings: dict[str, str],
) -> str | None:
    if isinstance(value, ast.Constant):
        return _static_literal_binding(value.value)
    if isinstance(value, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
        try:
            return _static_literal_binding(ast.literal_eval(value))
        except (TypeError, ValueError):
            return f"{STATIC_AST_PREFIX}{ast.unparse(value)}"
    if value is not None:
        return _resolve(value, bindings)
    return None


def _bind_static_assignment(
    statement: ast.stmt,
    bindings: dict[str, str],
) -> None:
    if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
        target = statement.targets[0]
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        target = statement.target
        value = statement.value
    else:
        return
    if not isinstance(target, ast.Name):
        return
    static_binding = _static_assignment_binding(value, bindings)
    if static_binding is not None:
        bindings[target.id] = static_binding


def _classvar(annotation: ast.AST, bindings: dict[str, str]) -> bool:
    target = annotation.value if isinstance(annotation, ast.Subscript) else annotation
    dotted = _expression_name(target)
    resolved = _resolve(target, bindings)
    return dotted in {"ClassVar", "typing.ClassVar"} or resolved == "typing.ClassVar"


def _symbol_name(node: ast.AST, bindings: dict[str, str]) -> str | None:
    dotted = _expression_name(node)
    if dotted is None:
        return None
    return _resolve(node, bindings) or dotted


def _is_field_call(node: ast.AST, bindings: dict[str, str]) -> bool:
    return (
        isinstance(node, ast.Call)
        and _resolve(node.func, bindings) in FIELD_FACTORIES
    )


def _static_string_value(node: ast.AST, bindings: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    value = _static_literal_value(_resolve(node, bindings))
    return value if isinstance(value, str) else None


def _static_path_part(
    node: ast.AST,
    bindings: dict[str, str],
) -> str | int | None:
    value = _static_string_value(node, bindings)
    if value is not None:
        return value
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    resolved = _static_literal_value(_resolve(node, bindings))
    return resolved if isinstance(resolved, int) else None


def _alias_input_paths(
    node: ast.AST,
    bindings: dict[str, str],
) -> set[tuple[str | int, ...]]:
    direct = _static_string_value(node, bindings)
    if direct is not None:
        return {(direct,)}
    if not isinstance(node, ast.Call):
        return set()
    factory = _resolve(node.func, bindings)
    if factory in ALIAS_CHOICES_FACTORIES:
        return {
            path
            for argument in node.args
            for path in _alias_input_paths(argument, bindings)
        }
    if factory in ALIAS_PATH_FACTORIES:
        parts = tuple(_static_path_part(argument, bindings) for argument in node.args)
        if parts and all(part is not None for part in parts):
            return {tuple(part for part in parts if part is not None)}
    return set()


def _field_constructor_paths(
    field: ast.AnnAssign,
    bindings: dict[str, str],
    alias_generator: str | None = None,
) -> frozenset[tuple[str | int, ...]]:
    """Static validation-input paths that may address this field.

    The Python field name is retained even when alias-only validation would reject it:
    a raw discriminator passed through an invalid spelling is still invalid production
    code and must not become a bypass.  Explicit validation aliases, aliases and the
    top-level key of AliasPath/AliasChoices are added when statically knowable.
    """

    paths: set[tuple[str | int, ...]] = (
        {(field.target.id,)} if isinstance(field.target, ast.Name) else set()
    )
    roots = [field.annotation]
    if field.value is not None:
        roots.append(field.value)
    for root in roots:
        for candidate in ast.walk(root):
            if not _is_field_call(candidate, bindings):
                continue
            assert isinstance(candidate, ast.Call)
            for keyword in candidate.keywords:
                if keyword.arg in {"alias", "validation_alias"}:
                    paths.update(_alias_input_paths(keyword.value, bindings))
    if isinstance(field.target, ast.Name):
        generated = _generated_alias(field.target.id, alias_generator)
        if generated is not None:
            paths.add((generated,))
    return frozenset(paths)


def _field_constructor_keys(
    field: ast.AnnAssign,
    bindings: dict[str, str],
    alias_generator: str | None = None,
) -> frozenset[str]:
    return frozenset(
        path[0]
        for path in _field_constructor_paths(field, bindings, alias_generator)
        if path and isinstance(path[0], str)
    )


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


def _common_alias_generator(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, str],
) -> tuple[str | None, bool]:
    before = _class_body_bindings(parsed, node, outer)
    body_candidate: tuple[ast.AST, dict[str, str]] | None = None
    body_config_seen = False
    body_config_complete = True
    nested_config_candidate: tuple[ast.AST, dict[str, str]] | None = None
    nested_config_seen = False
    for statement in node.body:
        bindings = before.get(id(statement), outer)
        value: ast.AST | None = None
        targets: set[str] = set()
        if isinstance(statement, ast.Assign):
            value = statement.value
            targets = {
                name
                for target in statement.targets
                for name in _target_names(target)
            }
        elif isinstance(statement, ast.AnnAssign):
            value = statement.value
            targets = _target_names(statement.target)
        if "model_config" in targets:
            # A later class-body assignment replaces the earlier namespace
            # value; ConfigDict assignments are not merged by Python.
            body_config_seen = True
            body_candidate = None
            body_config_complete = True
            if isinstance(value, ast.Call):
                resolved_factory = _resolve(value.func, bindings)
                if resolved_factory not in {
                    "dict",
                    "pydantic.ConfigDict",
                    "pydantic.config.ConfigDict",
                } or value.args or any(keyword.arg is None for keyword in value.keywords):
                    body_config_complete = False
                for keyword in value.keywords:
                    if keyword.arg == "alias_generator":
                        body_candidate = (keyword.value, bindings)
            elif isinstance(value, ast.Dict):
                for key, item in zip(value.keys, value.values):
                    if key is None:
                        body_config_complete = False
                    elif _static_string_value(key, bindings) == "alias_generator":
                        body_candidate = (item, bindings)
                    elif _static_string_value(key, bindings) is None:
                        body_config_complete = False
            else:
                body_config_complete = False
        if isinstance(statement, ast.ClassDef) and statement.name == "Config":
            nested_config_seen = True
            nested_config_candidate = None
            config_before = _class_body_bindings(parsed, statement, bindings)
            for config_statement in statement.body:
                if not isinstance(config_statement, (ast.Assign, ast.AnnAssign)):
                    continue
                config_targets = (
                    {
                        name
                        for target in config_statement.targets
                        for name in _target_names(target)
                    }
                    if isinstance(config_statement, ast.Assign)
                    else _target_names(config_statement.target)
                )
                if "alias_generator" in config_targets:
                    config_value = config_statement.value
                    if config_value is not None:
                        nested_config_candidate = (
                            config_value,
                            config_before.get(id(config_statement), bindings),
                        )
    if body_config_seen and nested_config_seen:
        return None, False

    candidate = body_candidate if body_config_seen else nested_config_candidate
    complete = body_config_complete if body_config_seen else True

    # Pydantic class-header config kwargs override the body model_config.
    for keyword in node.keywords:
        if keyword.arg == "alias_generator":
            candidate = (keyword.value, outer)
            complete = True

    if candidate is None:
        return None, complete
    value, bindings = candidate
    if isinstance(value, ast.Constant) and value.value is None:
        return None, complete
    resolved = _resolve(value, bindings)
    return resolved, complete and resolved in {
        "pydantic.alias_generators.to_camel",
        "pydantic.alias_generators.to_pascal",
        "pydantic.alias_generators.to_snake",
    }


def _config_expression_requires_runtime_proof(
    node: ast.AST | None,
    bindings: dict[str, str],
    seen_static_bindings: frozenset[str] = frozenset(),
    *,
    field_contract: bool = False,
    config_key: str | None = None,
) -> bool:
    """Whether a config expression can execute project-defined Python.

    This is intentionally a small inert-value recognizer, not a Python
    interpreter.  Pydantic config accepts callables under keys other than
    ``alias_generator`` (for example ``json_schema_extra``), and class-header
    ``**`` expansion can hide any config key.  Anything outside literal
    containers, three alias generators in the exact ``alias_generator`` slot,
    and direct ``dict``/``ConfigDict`` construction is handed to target-pin
    runtime proof. Field annotations separately allow trusted type symbols;
    config values do not, because even a builtin attribute can be an executable
    hook under keys such as ``json_schema_extra``.
    """

    if node is None:
        return True
    if isinstance(node, ast.Constant):
        return False
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if key is not None and _config_expression_requires_runtime_proof(
                key,
                bindings,
                seen_static_bindings,
                field_contract=field_contract,
            ):
                return True
            nested_key = (
                key.value
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
                else None
            )
            if _config_expression_requires_runtime_proof(
                value,
                bindings,
                seen_static_bindings,
                field_contract=field_contract,
                config_key=nested_key,
            ):
                return True
        return False
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return any(
            _config_expression_requires_runtime_proof(
                element,
                bindings,
                seen_static_bindings,
                field_contract=field_contract,
                config_key=config_key,
            )
            for element in node.elts
        )
    if isinstance(node, ast.UnaryOp):
        try:
            ast.literal_eval(node)
        except (TypeError, ValueError):
            return True
        return False
    if isinstance(node, ast.Call):
        factory = _resolve(node.func, bindings) or _expression_name(node.func)
        if factory not in STATIC_CONFIG_FACTORIES:
            return True
        return any(
            _config_expression_requires_runtime_proof(
                argument,
                bindings,
                seen_static_bindings,
                field_contract=field_contract,
                config_key=config_key,
            )
            for argument in node.args
        ) or any(
            _config_expression_requires_runtime_proof(
                keyword.value,
                bindings,
                seen_static_bindings,
                field_contract=field_contract,
                config_key=keyword.arg,
            )
            for keyword in node.keywords
        )
    if isinstance(node, (ast.Name, ast.Attribute)):
        resolved = _resolve(node, bindings)
        if _static_literal_value(resolved) is not _NO_STATIC_VALUE:
            return False
        static_node = _static_ast_value(resolved)
        if static_node is not None:
            assert resolved is not None
            if resolved in seen_static_bindings:
                return True
            return _config_expression_requires_runtime_proof(
                static_node,
                bindings,
                seen_static_bindings | {resolved},
                field_contract=field_contract,
                config_key=config_key,
            )
        if resolved is None:
            return not (
                field_contract
                and (_expression_name(node) or "") in BUILTIN_CONTRACT_SYMBOLS
            )
        if field_contract and resolved.startswith(FIELD_CONTRACT_SYMBOL_PREFIXES):
            return False
        return not (
            config_key == "alias_generator"
            and resolved in STATIC_ALIAS_GENERATORS
        )
    return True


def _field_contract_expression_requires_runtime_proof(
    node: ast.AST | None,
    bindings: dict[str, str],
    *,
    annotation: bool = False,
    default_factory: bool = False,
) -> bool:
    """Recognize declarative field/type expressions without executing Python."""

    if node is None or isinstance(node, ast.Constant):
        return False
    if isinstance(node, ast.Call):
        factory = _resolve(node.func, bindings) or _expression_name(node.func)
        if factory not in STATIC_FIELD_CONTRACT_FACTORIES:
            return True
        if factory in FIELD_FACTORIES:
            return any(
                _field_contract_expression_requires_runtime_proof(
                    argument,
                    bindings,
                )
                for argument in node.args
            ) or any(
                _field_contract_expression_requires_runtime_proof(
                    keyword.value,
                    bindings,
                    default_factory=keyword.arg == "default_factory",
                )
                for keyword in node.keywords
            )
        return any(
            _field_contract_expression_requires_runtime_proof(
                argument,
                bindings,
            )
            for argument in node.args
        ) or any(
            _field_contract_expression_requires_runtime_proof(
                keyword.value,
                bindings,
            )
            for keyword in node.keywords
        )
    if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
        values = (
            [
                candidate
                for key, value in zip(node.keys, node.values)
                for candidate in (key, value)
                if candidate is not None
            ]
            if isinstance(node, ast.Dict)
            else list(node.elts)
        )
        return any(
            _field_contract_expression_requires_runtime_proof(
                value,
                bindings,
                annotation=annotation,
                default_factory=default_factory,
            )
            for value in values
        )
    if isinstance(node, ast.Subscript):
        if not annotation:
            return True
        return _field_contract_expression_requires_runtime_proof(
            node.value,
            bindings,
            annotation=True,
        ) or _field_contract_expression_requires_runtime_proof(
            node.slice,
            bindings,
            annotation=True,
        )
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        if not annotation:
            return True
        return _field_contract_expression_requires_runtime_proof(
            node.left,
            bindings,
            annotation=True,
        ) or _field_contract_expression_requires_runtime_proof(
            node.right,
            bindings,
            annotation=True,
        )
    if isinstance(node, ast.UnaryOp):
        try:
            ast.literal_eval(node)
        except (TypeError, ValueError):
            return True
        return False
    if isinstance(node, (ast.Name, ast.Attribute)):
        resolved = _resolve(node, bindings)
        expression = _expression_name(node) or ""
        if default_factory:
            return (resolved or expression) not in STATIC_FIELD_DEFAULT_FACTORIES
        if not annotation:
            if _static_literal_value(resolved) is not _NO_STATIC_VALUE:
                return False
            return resolved not in STATIC_FIELD_SENTINELS
        return _config_expression_requires_runtime_proof(
            node,
            bindings,
            field_contract=True,
        )
    return True


def _common_config_requires_runtime_proof(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, str],
) -> bool:
    """Conservatively detect dynamic common FrameworkErrorSchema config/decorators."""

    if any(
        _config_expression_requires_runtime_proof(decorator, outer)
        for decorator in node.decorator_list
    ):
        return True
    if any(
        _config_expression_requires_runtime_proof(
            keyword.value,
            outer,
            config_key=keyword.arg,
        )
        for keyword in node.keywords
    ):
        return True

    before = _class_body_bindings(parsed, node, outer)
    for statement in node.body:
        bindings = before.get(id(statement), outer)
        if isinstance(statement, ast.Assign):
            targets = {
                name
                for target in statement.targets
                for name in _target_names(target)
            }
            if "model_config" in targets and _config_expression_requires_runtime_proof(
                statement.value,
                bindings,
            ):
                return True
        elif isinstance(statement, ast.AnnAssign):
            if (
                "model_config" in _target_names(statement.target)
                and _config_expression_requires_runtime_proof(
                    statement.value,
                    bindings,
                )
            ):
                return True
            if (
                isinstance(statement.target, ast.Name)
                and statement.target.id.startswith("_")
                and _config_expression_requires_runtime_proof(
                    statement.value,
                    bindings,
                )
            ):
                return True
            if _classvar(statement.annotation, bindings):
                if _classvar_binding_requires_runtime_proof(statement.value):
                    return True
            elif _field_contract_expression_requires_runtime_proof(
                statement.value,
                bindings,
            ):
                return True
        elif isinstance(statement, ast.ClassDef) and statement.name == "Config":
            if any(
                _config_expression_requires_runtime_proof(base, bindings)
                for base in statement.bases
            ) or any(
                _config_expression_requires_runtime_proof(decorator, bindings)
                for decorator in statement.decorator_list
            ) or any(
                _config_expression_requires_runtime_proof(
                    keyword.value,
                    bindings,
                    config_key=keyword.arg,
                )
                for keyword in statement.keywords
            ):
                return True
            config_before = _class_body_bindings(parsed, statement, bindings)
            for config_statement in statement.body:
                config_bindings = config_before.get(id(config_statement), bindings)
                if isinstance(config_statement, ast.Assign):
                    config_targets = {
                        name
                        for target in config_statement.targets
                        for name in _target_names(target)
                    }
                    if _config_expression_requires_runtime_proof(
                        config_statement.value,
                        config_bindings,
                        config_key=(
                            next(iter(config_targets))
                            if len(config_targets) == 1
                            else None
                        ),
                    ):
                        return True
                elif isinstance(config_statement, ast.AnnAssign):
                    config_targets = _target_names(config_statement.target)
                    if _config_expression_requires_runtime_proof(
                        config_statement.value,
                        config_bindings,
                        config_key=(
                            next(iter(config_targets))
                            if len(config_targets) == 1
                            else None
                        ),
                    ):
                        return True
                elif isinstance(
                    config_statement,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    return True
                elif isinstance(config_statement, ast.Expr):
                    if not (
                        isinstance(config_statement.value, ast.Constant)
                        and isinstance(config_statement.value.value, str)
                    ) and _config_expression_requires_runtime_proof(
                        config_statement.value,
                        config_bindings,
                    ):
                        return True
                elif not isinstance(config_statement, ast.Pass):
                    return True
        if any(
            isinstance(candidate, ast.Name) and candidate.id == "model_config"
            for candidate in ast.walk(statement)
        ):
            direct_assignment = (
                isinstance(statement, ast.Assign)
                and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name)
                and statement.targets[0].id == "model_config"
            ) or (
                isinstance(statement, ast.AnnAssign)
                and isinstance(statement.target, ast.Name)
                and statement.target.id == "model_config"
            )
            if not direct_assignment:
                return True
        if isinstance(statement, ast.Expr):
            if not (
                isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            ):
                return True
        elif isinstance(statement, ast.Assign):
            if any(not isinstance(target, ast.Name) for target in statement.targets):
                return True
            if (
                any(
                    isinstance(target, ast.Name) and target.id.startswith("_")
                    for target in statement.targets
                )
                and _config_expression_requires_runtime_proof(
                    statement.value,
                    bindings,
                )
            ):
                return True
        elif isinstance(statement, ast.AnnAssign):
            if not isinstance(statement.target, ast.Name):
                return True
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return True
        elif not isinstance(
            statement,
            (
                ast.ClassDef,
                ast.Pass,
            ),
        ):
            return True
    return False


def _signature(
    node: ast.AST | None,
    bindings: dict[str, str],
    *,
    replacements: dict[str, str] | None = None,
) -> NodeSignature:
    """Return an import-alias-neutral, deterministic AST signature."""

    if node is None:
        return ("none-node",)
    replacements = replacements or {}
    symbol = _symbol_name(node, bindings)
    if symbol is not None:
        static_value = _static_literal_value(symbol)
        if static_value is not _NO_STATIC_VALUE:
            return (
                "constant",
                type(static_value).__name__,
                repr(static_value),
            )
        return ("symbol", replacements.get(symbol, symbol))
    if isinstance(node, ast.Constant):
        return ("constant", type(node.value).__name__, repr(node.value))
    if isinstance(node, ast.Subscript):
        return (
            "subscript",
            _signature(node.value, bindings, replacements=replacements),
            _signature(node.slice, bindings, replacements=replacements),
        )
    if isinstance(node, ast.BinOp):
        return (
            "binop",
            type(node.op).__name__,
            _signature(node.left, bindings, replacements=replacements),
            _signature(node.right, bindings, replacements=replacements),
        )
    if isinstance(node, ast.UnaryOp):
        return (
            "unary",
            type(node.op).__name__,
            _signature(node.operand, bindings, replacements=replacements),
        )
    if isinstance(node, (ast.Tuple, ast.List)):
        return (
            type(node).__name__.lower(),
            *(
                _signature(item, bindings, replacements=replacements)
                for item in node.elts
            ),
        )
    if isinstance(node, (ast.Set, ast.Dict)):
        if isinstance(node, ast.Set):
            items = [
                _signature(item, bindings, replacements=replacements)
                for item in node.elts
            ]
        else:
            items = [
                (
                    "item",
                    _signature(key, bindings, replacements=replacements),
                    _signature(value, bindings, replacements=replacements),
                )
                for key, value in zip(node.keys, node.values)
            ]
        return (type(node).__name__.lower(), *sorted(items, key=repr))
    if isinstance(node, ast.Call):
        keywords = sorted(
            (
                keyword.arg or "**",
                _signature(keyword.value, bindings, replacements=replacements),
            )
            for keyword in node.keywords
        )
        return (
            "call",
            _signature(node.func, bindings, replacements=replacements),
            tuple(
                _signature(argument, bindings, replacements=replacements)
                for argument in node.args
            ),
            tuple(keywords),
        )
    if isinstance(node, ast.keyword):
        return (
            "keyword",
            node.arg,
            _signature(node.value, bindings, replacements=replacements),
        )
    return ("ast", ast.dump(node, include_attributes=False))


def _unresolved_contract_symbols(
    node: ast.AST,
    bindings: dict[str, str],
) -> set[str]:
    unresolved: set[str] = set()

    def visit(candidate: ast.AST) -> None:
        if isinstance(candidate, (ast.Name, ast.Attribute)):
            dotted = _expression_name(candidate)
            if dotted is None:
                return
            if _resolve(candidate, bindings) is None:
                first = dotted.split(".", 1)[0]
                if first not in BUILTIN_CONTRACT_SYMBOLS:
                    unresolved.add(dotted)
            return
        for child in ast.iter_child_nodes(candidate):
            visit(child)

    visit(node)
    return unresolved


def _record_unresolved_field_contract(
    parsed: ParsedSource,
    field: ast.AnnAssign,
    bindings: dict[str, str],
    analysis: list[str],
) -> None:
    roots = [field.annotation]
    if field.value is not None:
        roots.append(field.value)
    symbols = set().union(
        *(_unresolved_contract_symbols(root, bindings) for root in roots)
    )
    if symbols:
        analysis.append(
            f"{parsed.relative_path}:{field.lineno} field contract symbol provenance 분석 불능: "
            + ", ".join(sorted(symbols))
        )
    default_kind = _field_default_kind(field, bindings)
    if default_kind in {"conflict", "invalid_factory"}:
        analysis.append(
            f"{parsed.relative_path}:{field.lineno} invalid Field default/default_factory contract: "
            f"{default_kind}"
        )


def _annotated_parts(
    node: ast.AST,
    bindings: dict[str, str],
) -> tuple[ast.AST, tuple[ast.AST, ...]] | None:
    if not isinstance(node, ast.Subscript):
        return None
    symbol = _symbol_name(node.value, bindings)
    if symbol not in {
        "Annotated",
        "typing.Annotated",
        "typing_extensions.Annotated",
    }:
        return None
    parts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    if not parts:
        return None
    return parts[0], tuple(parts[1:])


def _ordered_annotation_field_calls(
    node: ast.AST,
    bindings: dict[str, str],
) -> tuple[ast.Call, ...]:
    """Return Field metadata in Pydantic's inner-to-outer merge order."""

    parts = _annotated_parts(node, bindings)
    if parts is None:
        return ()
    inner, metadata = parts
    calls = list(_ordered_annotation_field_calls(inner, bindings))
    calls.extend(
        candidate
        for candidate in metadata
        if _is_field_call(candidate, bindings)
        and isinstance(candidate, ast.Call)
    )
    return tuple(calls)


def _annotation_signature(
    node: ast.AST,
    bindings: dict[str, str],
    *,
    replacements: dict[str, str] | None = None,
) -> NodeSignature:
    annotated = _annotated_parts(node, bindings)
    if annotated is None:
        return _signature(node, bindings, replacements=replacements)
    inner, extras = annotated
    non_field_extras = tuple(
        _signature(extra, bindings, replacements=replacements)
        for extra in extras
        if not _is_field_call(extra, bindings)
    )
    inner_signature = _annotation_signature(
        inner,
        bindings,
        replacements=replacements,
    )
    if not non_field_extras:
        return inner_signature
    return ("annotated", inner_signature, non_field_extras)


def _annotation_symbol_count(
    node: ast.AST,
    bindings: dict[str, str],
    symbols: set[str],
) -> int:
    symbol = _symbol_name(node, bindings)
    if symbol is not None:
        return int(symbol in symbols)
    annotated = _annotated_parts(node, bindings)
    if annotated is not None:
        inner, extras = annotated
        return _annotation_symbol_count(inner, bindings, symbols) + sum(
            _annotation_symbol_count(extra, bindings, symbols)
            for extra in extras
            if not _is_field_call(extra, bindings)
        )
    return sum(
        _annotation_symbol_count(child, bindings, symbols)
        for child in ast.iter_child_nodes(node)
    )


def _is_none_annotation(node: ast.AST, bindings: dict[str, str]) -> bool:
    if isinstance(node, ast.Constant) and node.value is None:
        return True
    return _symbol_name(node, bindings) in {"None", "types.NoneType"}


def _is_scalar_discriminator_annotation(
    node: ast.AST,
    bindings: dict[str, str],
    symbols: set[str],
) -> bool:
    """Accept a scalar identifier and its nullable/Annotated wrappers, not containers."""

    annotated = _annotated_parts(node, bindings)
    if annotated is not None:
        inner, _extras = annotated
        return _is_scalar_discriminator_annotation(inner, bindings, symbols)
    symbol = _symbol_name(node, bindings)
    if symbol is not None:
        return symbol in symbols
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return (
            _is_scalar_discriminator_annotation(node.left, bindings, symbols)
            and _is_none_annotation(node.right, bindings)
        ) or (
            _is_none_annotation(node.left, bindings)
            and _is_scalar_discriminator_annotation(node.right, bindings, symbols)
        )
    if not isinstance(node, ast.Subscript):
        return False
    wrapper = _symbol_name(node.value, bindings)
    if wrapper in {"Optional", "typing.Optional"}:
        return _is_scalar_discriminator_annotation(node.slice, bindings, symbols)
    if wrapper not in {"Union", "typing.Union"}:
        return False
    parts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    return (
        len(parts) == 2
        and sum(_is_none_annotation(part, bindings) for part in parts) == 1
        and any(
            _is_scalar_discriminator_annotation(part, bindings, symbols)
            for part in parts
        )
    )


def _field_metadata_signature(
    field: ast.AnnAssign,
    bindings: dict[str, str],
) -> tuple[NodeSignature, ...]:
    calls: list[NodeSignature] = []
    field_calls = list(_ordered_annotation_field_calls(field.annotation, bindings))
    if _is_field_call(field.value, bindings):
        assert isinstance(field.value, ast.Call)
        field_calls.append(field.value)
    for candidate in field_calls:
        positional_metadata = candidate.args[1:]
        keyword_metadata = [
            keyword
            for keyword in candidate.keywords
            if keyword.arg not in {"default", "default_factory"}
        ]
        calls.append(
            (
                "Field",
                tuple(_signature(argument, bindings) for argument in positional_metadata),
                tuple(
                    sorted(
                        (
                            keyword.arg or "**",
                            _signature(keyword.value, bindings),
                        )
                        for keyword in keyword_metadata
                    )
                ),
            )
        )
    return tuple(calls)


def _default_signature(
    value: ast.AST | None,
    bindings: dict[str, str],
    *,
    enum_full: str | None = None,
    enum_members: dict[str, str] | None = None,
) -> NodeSignature:
    if value is None:
        return ("required",)
    if isinstance(value, ast.Constant):
        return ("value", type(value.value).__name__, repr(value.value))
    resolved = _resolve(value, bindings)
    static_value = _static_literal_value(resolved)
    if static_value is not _NO_STATIC_VALUE:
        return ("value", type(static_value).__name__, repr(static_value))
    if enum_full is not None and enum_members is not None and resolved is not None:
        prefix = f"{enum_full}."
        if resolved.startswith(prefix):
            member = resolved.removeprefix(prefix)
            if member in enum_members:
                wire_value = enum_members[member]
                return ("value", "str", repr(wire_value))
    return ("expression", _signature(value, bindings))


def _field_default_signature(
    field: ast.AnnAssign,
    bindings: dict[str, str],
    *,
    enum_full: str | None = None,
    enum_members: dict[str, str] | None = None,
) -> NodeSignature:
    return (
        _field_default_kind(field, bindings),
        _default_signature(
            _field_default_expression(field, bindings),
            bindings,
            enum_full=enum_full,
            enum_members=enum_members,
        ),
    )


def _enum_member_name(
    value: ast.AST | None,
    bindings: dict[str, str],
    enum_full: str,
    enum_members: dict[str, str],
) -> str | None:
    resolved = _resolve(value, bindings) if value is not None else None
    prefix = f"{enum_full}."
    if resolved is None or not resolved.startswith(prefix):
        return None
    member = resolved.removeprefix(prefix)
    return member if member in enum_members else None


def _default_is_none(value: ast.AST | None, bindings: dict[str, str]) -> bool:
    if isinstance(value, ast.Constant) and value.value is None:
        return True
    return _static_literal_value(
        _resolve(value, bindings) if value is not None else None
    ) is None


def _append_finding(
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    parsed: ParsedSource,
    node: ast.AST,
    category: str,
    *,
    requires_static_error_shape: bool = False,
) -> None:
    lineno = getattr(node, "lineno", 1)
    key = (parsed.relative_path, lineno, category)
    if key in seen:
        return
    seen.add(key)
    lines = parsed.source.splitlines()
    shown = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else category
    findings.append(
        Finding(
            parsed.relative_path,
            lineno,
            category,
            shown,
            requires_static_error_shape=requires_static_error_shape,
        )
    )


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


def _is_required_sentinel(
    value: ast.AST,
    bindings: dict[str, str],
) -> bool:
    if isinstance(value, ast.Constant) and value.value is Ellipsis:
        return True
    return _resolve(value, bindings) in {
        "pydantic_core.PydanticUndefined",
        "pydantic_core._pydantic_core.PydanticUndefined",
        "pydantic.fields.PydanticUndefined",
    }


def _field_call_default_spec(
    call: ast.Call,
    bindings: dict[str, str],
) -> tuple[str, ast.AST | None] | None:

    default_value = call.args[0] if call.args else None
    default_declared = bool(call.args)
    factory_value: ast.AST | None = None
    factory_declared = False
    for keyword in call.keywords:
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
        return "default_factory", factory_value
    if default_is_set:
        return "default", default_value
    if factory_declared and isinstance(factory_value, ast.Constant) and (
        factory_value.value is None
    ):
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


def _field_default_spec(
    field: ast.AnnAssign,
    bindings: dict[str, str],
) -> tuple[str, ast.AST | None]:
    spec: tuple[str, ast.AST | None] = ("required", None)
    for candidate in _ordered_annotation_field_calls(field.annotation, bindings):
        declared = _field_call_default_spec(candidate, bindings)
        spec = _merge_field_default_spec(spec, declared)

    value = field.value
    if value is None:
        return spec
    if not _is_field_call(value, bindings):
        if _is_required_sentinel(value, bindings):
            return spec
        if spec[0] == "default_factory":
            return "conflict", None
        return "default", value
    assert isinstance(value, ast.Call)
    declared = _field_call_default_spec(value, bindings)
    return _merge_field_default_spec(spec, declared)


def _field_default_expression(
    field: ast.AnnAssign,
    bindings: dict[str, str],
) -> ast.AST | None:
    return _field_default_spec(field, bindings)[1]


def _field_default_kind(
    field: ast.AnnAssign,
    bindings: dict[str, str],
) -> str:
    return _field_default_spec(field, bindings)[0]


def _field_is_required(
    field: ast.AnnAssign,
    bindings: dict[str, str],
) -> bool:
    return _field_default_kind(field, bindings) == "required"


def _classvar_binding_requires_runtime_proof(value: ast.AST | None) -> bool:
    """ClassVar references are inert; executed expressions are not."""

    if value is None or isinstance(value, (ast.Constant, ast.Name, ast.Attribute)):
        return False
    if isinstance(value, ast.Lambda):
        defaults = [*value.args.defaults, *value.args.kw_defaults]
        return any(
            _classvar_binding_requires_runtime_proof(default)
            for default in defaults
            if default is not None
        )
    if isinstance(value, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
        values = (
            [
                candidate
                for key, item in zip(value.keys, value.values)
                for candidate in (key, item)
                if candidate is not None
            ]
            if isinstance(value, ast.Dict)
            else list(value.elts)
        )
        return any(_classvar_binding_requires_runtime_proof(item) for item in values)
    if isinstance(value, ast.UnaryOp):
        try:
            ast.literal_eval(value)
        except (TypeError, ValueError):
            return True
        return False
    return True


def _class_member_findings(
    parsed: ParsedSource,
    node: ast.ClassDef,
    initial_bindings: dict[str, str],
    allowed_fields: set[str],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    *,
    allow_model_config: bool = False,
    allow_schema_decorators: bool = False,
) -> None:
    def pydantic_hook(name: str) -> bool:
        return name.startswith(("__get_pydantic_", "__pydantic_")) or name in {
            "__get_validators__",
            "__modify_schema__",
        }

    def contains_schema_decorator_factory(
        value: ast.AST | None,
        bindings: dict[str, str],
    ) -> bool:
        if value is None:
            return False
        for candidate in ast.walk(value):
            if not isinstance(candidate, ast.Call):
                continue
            resolved = _resolve(candidate.func, bindings)
            if resolved in SCHEMA_DECORATORS:
                return True
            if (
                resolved is not None
                and resolved.startswith("pydantic.")
                and resolved.rsplit(".", 1)[-1] in SCHEMA_DECORATOR_TAILS
            ):
                return True
        return False

    if not allow_model_config:
        for decorator in node.decorator_list:
            _append_finding(
                findings,
                seen,
                parsed,
                decorator,
                "class decorator outside common FrameworkErrorSchema",
            )
        for keyword in node.keywords:
            _append_finding(
                findings,
                seen,
                parsed,
                keyword,
                "class keyword config outside common FrameworkErrorSchema",
            )
    field_names: set[str] = set()
    before = _class_body_bindings(parsed, node, initial_bindings)
    for statement in node.body:
        bindings = before.get(id(statement), initial_bindings)
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            name = statement.target.id
            if not allow_model_config and pydantic_hook(name):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "Pydantic hook override outside common FrameworkErrorSchema",
                )
                continue
            if name == "model_config":
                if not allow_model_config:
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "model_config override outside common FrameworkErrorSchema",
                    )
                continue
            if _classvar(statement.annotation, bindings):
                if _classvar_binding_requires_runtime_proof(statement.value):
                    if allow_model_config:
                        analysis.append(
                            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                            f"{parsed.relative_path}:{statement.lineno} "
                            "common FrameworkErrorSchema dynamic ClassVar binding은 "
                            "target-pin runtime proof 필요"
                        )
                    else:
                        _append_finding(
                            findings,
                            seen,
                            parsed,
                            statement,
                            "dynamic ClassVar assignment outside common FrameworkErrorSchema",
                        )
                continue
            if name.startswith("_"):
                if not allow_model_config and contains_schema_decorator_factory(
                    statement.value,
                    bindings,
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "schema decorator proxy outside common FrameworkErrorSchema",
                    )
                elif (
                    not allow_model_config
                    and _static_assignment_binding(statement.value, bindings) is None
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "dynamic private class assignment outside common FrameworkErrorSchema",
                    )
                continue
            if name in field_names:
                _append_finding(findings, seen, parsed, statement, "duplicate public field")
            field_names.add(name)
            if name not in allowed_fields:
                _append_finding(findings, seen, parsed, statement, "additional public field")
        elif isinstance(statement, ast.Assign):
            names = {name for target in statement.targets for name in _target_names(target)}
            if not names and not allow_model_config:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "complex class assignment outside common FrameworkErrorSchema",
                )
            for name in names:
                if not allow_model_config and pydantic_hook(name):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "Pydantic hook override outside common FrameworkErrorSchema",
                    )
                elif name == "model_config":
                    if not allow_model_config:
                        _append_finding(
                            findings,
                            seen,
                            parsed,
                            statement,
                            "model_config override outside common FrameworkErrorSchema",
                        )
                elif not name.startswith("_"):
                    _append_finding(findings, seen, parsed, statement, "public class assignment/helper")
                elif not allow_model_config and contains_schema_decorator_factory(
                    statement.value,
                    bindings,
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "schema decorator proxy outside common FrameworkErrorSchema",
                    )
            if (
                not allow_model_config
                and names
                and all(name.startswith("_") for name in names)
                and _static_assignment_binding(statement.value, bindings) is None
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "dynamic private class assignment outside common FrameworkErrorSchema",
                )
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorated_schema_method = any(
                _resolve(
                    decorator.func if isinstance(decorator, ast.Call) else decorator,
                    bindings,
                )
                in SCHEMA_DECORATORS
                for decorator in statement.decorator_list
            )
            if not allow_schema_decorators or (
                not decorated_schema_method and not statement.name.startswith("_")
            ):
                _append_finding(findings, seen, parsed, statement, "validator/public helper")
        elif (
            isinstance(statement, ast.ClassDef)
            and not statement.name.startswith("_")
            and not (allow_model_config and statement.name == "Config")
        ):
            _append_finding(findings, seen, parsed, statement, "public nested class/helper")
        elif (
            isinstance(statement, ast.ClassDef)
            and allow_model_config
            and statement.name == "Config"
        ) or isinstance(statement, ast.Pass) or (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            continue
        else:
            if allow_model_config:
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{statement.lineno} "
                    "common FrameworkErrorSchema executable class-body statement는 target-pin runtime proof 필요"
                )
            else:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "executable class-body statement outside common FrameworkErrorSchema",
                )


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


def _bc_module_artifact_findings(
    parsed: ParsedSource,
    allowed_classes: set[ast.ClassDef],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    """Keep the canonical BC error module declarative and mutation-free."""

    before = _module_bindings(parsed)
    for statement in parsed.tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(statement, ast.ClassDef):
            if statement not in allowed_classes:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "BC error module extra class/helper forbidden",
                )
            continue
        if (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        ):
            continue
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            value = statement.value
        elif isinstance(statement, ast.AnnAssign):
            target = statement.target
            value = statement.value
        else:
            target = None
            value = None
        bindings = before.get(id(statement), {})
        if (
            isinstance(target, ast.Name)
            and target.id.startswith("_")
            and _static_assignment_binding(value, bindings) is not None
        ):
            continue
        _append_finding(
            findings,
            seen,
            parsed,
            statement,
            "BC error module helper/mutation/side effect forbidden",
        )


COMMON_CONFIG_MUTATION_METHODS = {
    "__delitem__",
    "__init__",
    "__ior__",
    "__setitem__",
    "clear",
    "pop",
    "popitem",
    "setdefault",
    "update",
}


def _executed_expression_calls(node: ast.AST) -> list[ast.Call]:
    """Return calls executed by an expression without entering deferred lambdas."""

    calls: list[ast.Call] = []
    if isinstance(node, ast.Lambda):
        for default in node.args.defaults:
            calls.extend(_executed_expression_calls(default))
        for default in node.args.kw_defaults:
            if default is not None:
                calls.extend(_executed_expression_calls(default))
        return calls
    if isinstance(node, ast.Call):
        calls.append(node)
        if isinstance(node.func, ast.Lambda):
            for default in node.func.args.defaults:
                calls.extend(_executed_expression_calls(default))
            for default in node.func.args.kw_defaults:
                if default is not None:
                    calls.extend(_executed_expression_calls(default))
            calls.extend(_executed_expression_calls(node.func.body))
        else:
            calls.extend(_executed_expression_calls(node.func))
        for argument in node.args:
            calls.extend(_executed_expression_calls(argument))
        for keyword in node.keywords:
            calls.extend(_executed_expression_calls(keyword.value))
        return calls
    for child in ast.iter_child_nodes(node):
        calls.extend(_executed_expression_calls(child))
    return calls


def _visible_common_schema_mutation(
    value: ast.AST | None,
    bindings: dict[str, str],
    named_lambdas: dict[str, ast.Lambda] | None = None,
) -> bool:
    """Detect a visible import-time mutation hidden inside an expression."""

    if value is None:
        return False

    schema_kind = "schema"
    config_kind = "config"
    rebuild_kind = "rebuild"
    mutator_kind = "config_mutator"
    getter_kind = "getattr"
    setter_kind = "setattr"
    deleter_kind = "delattr"
    schema_symbols = {NINJA_SCHEMA, COMMON_ERROR_OUT, "Schema", "FrameworkErrorSchema"}
    config_symbols = {f"{symbol}.model_config" for symbol in schema_symbols}
    rebuild_symbols = {f"{symbol}.model_rebuild" for symbol in schema_symbols}
    named_lambdas = named_lambdas or {}

    def resolved_kinds(resolved: str | None) -> set[str]:
        if resolved is None:
            return set()
        if resolved in schema_symbols:
            return {schema_kind}
        if resolved in config_symbols:
            return {config_kind}
        if resolved in rebuild_symbols:
            return {rebuild_kind}
        if any(
            resolved == f"{symbol}.{method}"
            for symbol in config_symbols
            for method in COMMON_CONFIG_MUTATION_METHODS
        ):
            return {mutator_kind}
        if resolved in {"getattr", "builtins.getattr"}:
            return {getter_kind}
        if resolved in {
            "setattr",
            "builtins.setattr",
            "type.__setattr__",
            "builtins.type.__setattr__",
        }:
            return {setter_kind}
        if resolved in {
            "delattr",
            "builtins.delattr",
            "type.__delattr__",
            "builtins.type.__delattr__",
        }:
            return {deleter_kind}
        return set()

    def value_kinds(node: ast.AST | None, local: dict[str, set[str]]) -> set[str]:
        if node is None:
            return set()
        if isinstance(node, ast.Name) and node.id in local:
            return set(local[node.id])
        resolved = _resolve(node, bindings) or _expression_name(node)
        kinds = resolved_kinds(resolved)
        if kinds:
            return kinds
        if isinstance(node, ast.Attribute):
            owner = value_kinds(node.value, local)
            if schema_kind in owner and node.attr == "model_config":
                return {config_kind}
            if schema_kind in owner and node.attr == "model_rebuild":
                return {rebuild_kind}
            if config_kind in owner and node.attr in COMMON_CONFIG_MUTATION_METHODS:
                return {mutator_kind}
            return set()
        if isinstance(node, ast.Call):
            callee = value_kinds(node.func, local)
            if getter_kind not in callee or len(node.args) < 2:
                return set()
            attribute = (
                node.args[1].value
                if isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
                else None
            )
            target = value_kinds(node.args[0], local)
            if schema_kind in target and attribute == "model_config":
                return {config_kind}
            if schema_kind in target and attribute == "model_rebuild":
                return {rebuild_kind}
            if config_kind in target and attribute in COMMON_CONFIG_MUTATION_METHODS:
                return {mutator_kind}
            return set()
        if isinstance(node, ast.IfExp):
            return value_kinds(node.body, local) | value_kinds(node.orelse, local)
        if isinstance(node, ast.BoolOp):
            return set().union(*(value_kinds(item, local) for item in node.values))
        if isinstance(node, ast.NamedExpr):
            return value_kinds(node.value, local)
        return set()

    def call_mutates(call: ast.Call, local: dict[str, set[str]]) -> bool:
        callee = value_kinds(call.func, local)
        if rebuild_kind in callee or mutator_kind in callee:
            return True
        if not callee & {setter_kind, deleter_kind} or len(call.args) < 2:
            return False
        attribute = (
            call.args[1].value
            if isinstance(call.args[1], ast.Constant)
            and isinstance(call.args[1].value, str)
            else None
        )
        return (
            schema_kind in value_kinds(call.args[0], local)
            and attribute in {"model_config", "model_rebuild"}
        )

    def expression_mutates(node: ast.AST, local: dict[str, set[str]]) -> bool:
        if isinstance(node, ast.Lambda):
            defaults = [*node.args.defaults, *node.args.kw_defaults]
            return any(
                expression_mutates(default, local)
                for default in defaults
                if default is not None
            )
        if isinstance(node, ast.Call):
            if any(expression_mutates(argument, local) for argument in node.args):
                return True
            if any(expression_mutates(keyword.value, local) for keyword in node.keywords):
                return True
            if isinstance(node.func, ast.Lambda):
                child = {name: set(kinds) for name, kinds in local.items()}
                positional = [*node.func.args.posonlyargs, *node.func.args.args]
                default_offset = len(positional) - len(node.func.args.defaults)
                for index, default in enumerate(node.func.args.defaults, default_offset):
                    child[positional[index].arg] = value_kinds(default, local)
                for parameter, argument in zip(positional, node.args):
                    child[parameter.arg] = value_kinds(argument, local)
                for parameter, default in zip(
                    node.func.args.kwonlyargs,
                    node.func.args.kw_defaults,
                ):
                    if default is not None:
                        child[parameter.arg] = value_kinds(default, local)
                for keyword in node.keywords:
                    if keyword.arg is not None:
                        child[keyword.arg] = value_kinds(keyword.value, local)
                return expression_mutates(node.func.body, child)
            if isinstance(node.func, ast.Name) and node.func.id in named_lambdas:
                lambda_ = named_lambdas[node.func.id]
                child = {name: set(kinds) for name, kinds in local.items()}
                positional = [*lambda_.args.posonlyargs, *lambda_.args.args]
                default_offset = len(positional) - len(lambda_.args.defaults)
                for index, default in enumerate(lambda_.args.defaults, default_offset):
                    child[positional[index].arg] = value_kinds(default, local)
                for parameter, argument in zip(positional, node.args):
                    child[parameter.arg] = value_kinds(argument, local)
                for parameter, default in zip(
                    lambda_.args.kwonlyargs,
                    lambda_.args.kw_defaults,
                ):
                    if default is not None:
                        child[parameter.arg] = value_kinds(default, local)
                for keyword in node.keywords:
                    if keyword.arg is not None:
                        child[keyword.arg] = value_kinds(keyword.value, local)
                return expression_mutates(lambda_.body, child)
            return call_mutates(node, local) or expression_mutates(node.func, local)
        return any(expression_mutates(child, local) for child in ast.iter_child_nodes(node))

    return expression_mutates(value, {})


def _analyze_common(
    parsed: ParsedSource | None,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    project_module_prefixes: set[str],
) -> dict[str, CommonFieldContract]:
    if parsed is None:
        return {}
    before = _module_bindings(parsed)
    for statement in _project_import_nodes(
        parsed,
        project_module_prefixes,
        recursive=True,
    ):
        analysis.append(
            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
            f"{parsed.relative_path}:{statement.lineno} "
            "common FrameworkErrorSchema의 project/relative import는 target-pin runtime proof 필요"
        )
    error_outs = [
        node for node in parsed.tree.body if isinstance(node, ast.ClassDef) and node.name == "FrameworkErrorSchema"
    ]
    if len(error_outs) != 1:
        anchor: ast.AST = error_outs[0] if error_outs else parsed.tree
        _append_finding(findings, seen, parsed, anchor, "exactly one common FrameworkErrorSchema required")
    contracts: dict[str, CommonFieldContract] = {}
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
            "common FrameworkErrorSchema must directly inherit ninja.Schema",
        )
        fields = _public_annassigns(parsed, error_out, bindings)
        field_bindings = _class_body_bindings(parsed, error_out, bindings)
        for statement in error_out.body:
            statement_value = (
                statement.value
                if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Expr))
                else None
            )
            statement_bindings = field_bindings.get(id(statement), bindings)
            standalone_expression = isinstance(statement, ast.Expr) and not (
                isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            )
            dynamic_classvar = (
                isinstance(statement, ast.AnnAssign)
                and _classvar(statement.annotation, statement_bindings)
            )
            if (standalone_expression or dynamic_classvar) and _visible_common_schema_mutation(
                statement_value,
                statement_bindings,
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "common FrameworkErrorSchema direct mutation/side effect forbidden",
                )
        alias_generator, alias_generator_known = _common_alias_generator(
            parsed,
            error_out,
            bindings,
        )
        if not alias_generator_known or _common_config_requires_runtime_proof(
            parsed,
            error_out,
            bindings,
        ):
            analysis.append(
                "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                f"{parsed.relative_path}:{error_out.lineno} "
                "project custom FrameworkErrorSchema config/decorator는 target-pin runtime proof 필요"
            )
        for name, field in fields.items():
            bindings_at_field = field_bindings.get(id(field), bindings)
            if _field_contract_expression_requires_runtime_proof(
                field.annotation,
                bindings_at_field,
                annotation=True,
            ) or _field_contract_expression_requires_runtime_proof(
                field.value,
                bindings_at_field,
            ):
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{field.lineno} "
                    "common FrameworkErrorSchema dynamic field contract는 target-pin runtime proof 필요"
                )
            _record_unresolved_field_contract(
                parsed,
                field,
                bindings_at_field,
                analysis,
            )
            discriminator_annotation = None
            if _is_scalar_discriminator_annotation(
                field.annotation,
                bindings_at_field,
                {"str", "builtins.str"},
            ):
                discriminator_annotation = _annotation_signature(
                    field.annotation,
                    bindings_at_field,
                    replacements={
                        "str": "<bc-error-code>",
                        "builtins.str": "<bc-error-code>",
                    },
                )
            contracts[name] = CommonFieldContract(
                annotation=_annotation_signature(
                    field.annotation,
                    bindings_at_field,
                ),
                discriminator_annotation=discriminator_annotation,
                metadata=_field_metadata_signature(field, bindings_at_field),
                required=_field_is_required(field, bindings_at_field),
                default=_field_default_signature(field, bindings_at_field),
                constructor_keys=_field_constructor_keys(
                    field,
                    bindings_at_field,
                    alias_generator,
                ),
                constructor_paths=_field_constructor_paths(
                    field,
                    bindings_at_field,
                    alias_generator,
                ),
                constructor_keys_complete=alias_generator_known,
            )
        _class_member_findings(
            parsed,
            error_out,
            bindings,
            set(contracts),
            analysis,
            findings,
            seen,
            allow_model_config=True,
            allow_schema_decorators=True,
        )
    named_lambdas: dict[str, ast.Lambda] = {}

    def assigned_lambdas(node: ast.Assign | ast.AnnAssign) -> dict[str, ast.Lambda]:
        assigned: dict[str, ast.Lambda] = {}

        def collect(target: ast.AST, value: ast.AST | None) -> None:
            if isinstance(target, ast.Name):
                lambda_ = (
                    value
                    if isinstance(value, ast.Lambda)
                    else named_lambdas.get(value.id)
                    if isinstance(value, ast.Name)
                    else None
                )
                if lambda_ is not None:
                    assigned[target.id] = lambda_
                return
            if (
                isinstance(target, (ast.Tuple, ast.List))
                and isinstance(value, (ast.Tuple, ast.List))
                and len(target.elts) == len(value.elts)
            ):
                for child_target, child_value in zip(target.elts, value.elts):
                    collect(child_target, child_value)

        value = _assignment_value(node)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                collect(target, value)
        else:
            collect(node.target, value)
        return assigned

    for node in parsed.tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)) or node in error_outs:
            continue
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        if isinstance(node, ast.ClassDef):
            bindings = before.get(id(node), {})
            inherits_error = any(
                _resolve(base, bindings) == COMMON_ERROR_OUT
                or (_expression_name(base) or "") == "FrameworkErrorSchema"
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
            if not targets or any(not name.startswith("_") for name in targets):
                _append_finding(findings, seen, parsed, node, "common module public artifact forbidden")
            elif _visible_common_schema_mutation(
                _assignment_value(node),
                bindings,
                named_lambdas,
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    node,
                    "common module helper/mutation/side effect forbidden",
                )
            elif _static_assignment_binding(_assignment_value(node), bindings) is None:
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{node.lineno} "
                    "common FrameworkErrorSchema module의 dynamic private binding은 target-pin runtime proof 필요"
                )
            lambda_bindings = assigned_lambdas(node)
            for target in targets:
                named_lambdas.pop(target, None)
                if target in lambda_bindings:
                    named_lambdas[target] = lambda_bindings[target]
        else:
            _append_finding(
                findings,
                seen,
                parsed,
                node,
                "common module helper/mutation/side effect forbidden",
            )
    return contracts


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
) -> tuple[set[str], bool]:
    ignored: set[str] = set()
    dynamic = False
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
            # canonical BC ErrorCode 컨테이너의 dynamic 멤버 집합 — 일반 분석 오류가
            # 아니라 «동적 error shape» 유형이다(2026-08-15 r2″ 토큰 커버리지 확장):
            # wire 멤버 목록이 정적으로 안 서므로 2-리뷰어 runtime proof 경로에 태운다.
            dynamic = True
            analysis.append(
                "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                f"{parsed.relative_path}:{statement.lineno} "
                "dynamic Enum _ignore_ 정적 분석 불능 — target-pin runtime proof 필요"
            )
        else:
            ignored.update(names)
    return ignored, dynamic


def _enum_members(
    parsed: ParsedSource,
    node: ast.ClassDef,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> tuple[dict[str, str], bool]:
    """(멤버 사전, 사전이 동적 해석 불능으로 «불완전»한가) — 둘째 값이 참이면
    멤버 사전 종속 판정(discriminator default 대조)은 파생 오탐이 되므로
    requires_static_error_shape 로 억제하고 runtime proof 가 대신 검증한다."""
    members: dict[str, str] = {}
    member_names: set[str] = set()
    ignored_names, dynamic = _enum_ignored_names(parsed, node, analysis)
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
                # canonical BC ErrorCode 의 비정형 멤버 대입 — «동적 error shape» 유형
                # (wire 멤버 모양이 정적으로 안 섬 · r2″ 토큰 커버리지 확장).
                dynamic = True
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{statement.lineno} "
                    "dynamic Enum member shape 정적 분석 불능 — target-pin runtime proof 필요"
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
                # canonical BC ErrorCode 멤버의 비-리터럴 wire 값(f-string·상수 참조 등) —
                # 일반 분석 오류로 죽지 않고 «동적 error shape» 토큰을 발화해 2-리뷰어
                # runtime proof 경로에 태운다(2026-08-15 r2″ — 이 케이스가 exit 1 로
                # 죽어 proof 경로가 막혔던 토큰 커버리지 구멍의 실증 축).
                dynamic = True
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{statement.lineno} "
                    f"dynamic Enum value 정적 분석 불능({name}) — target-pin runtime proof 필요"
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
    return members, dynamic


def _analyze_bc_module(
    parsed: ParsedSource,
    bc: str,
    common_contracts: dict[str, CommonFieldContract],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    project_module_prefixes: set[str],
) -> tuple[
    dict[str, str],
    set[str],
    str,
    str | None,
    frozenset[str],
    frozenset[tuple[str | int, ...]],
    bool,
]:
    before = _module_bindings(parsed)
    for statement in _project_import_nodes(
        parsed,
        project_module_prefixes,
        allowed_modules=frozenset({COMMON_ERROR_MODULE}),
        recursive=True,
    ):
        analysis.append(
            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
            f"{parsed.relative_path}:{statement.lineno} "
            "BC ErrorSchema의 추가 project/relative import는 target-pin runtime proof 필요"
        )
    prefix = _snake_to_pascal(bc)
    enum_name = f"{prefix}ErrorCode"
    base_name = f"{prefix}ErrorSchema"
    module = _module_name(parsed.relative_path)
    enum_full = f"{module}.{enum_name}"
    base_full = f"{module}.{base_name}"
    common_fields = set(common_contracts)
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
    members_dynamic: bool = False
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
        members, members_dynamic = _enum_members(parsed, enum, analysis, findings, seen)

    bases = [node for node in classes if node.name == base_name]
    allowed_class_nodes: set[ast.ClassDef] = {*enums, *bases}
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
        if node not in bases and direct_common:
            _append_finding(findings, seen, parsed, node, "second BC FrameworkErrorSchema base")

    discriminator_field_name: str | None = None
    discriminator_constructor_keys: frozenset[str] = frozenset()
    discriminator_constructor_paths: frozenset[tuple[str | int, ...]] = (
        frozenset()
    )
    discriminator_constructor_keys_complete = True
    base_discriminator_default_member: str | None = None
    if len(bases) == 1:
        base = bases[0]
        bindings = before.get(id(base), {})
        _base_contract(
            parsed,
            base,
            bindings,
            COMMON_ERROR_OUT,
            "FrameworkErrorSchema",
            analysis,
            findings,
            seen,
            f"{base_name} must directly inherit common FrameworkErrorSchema",
        )
        fields = _public_annassigns(parsed, base, bindings)
        field_bindings = _class_body_bindings(parsed, base, bindings)
        discriminator_fields = []
        for field_name, field in fields.items():
            bindings_at_field = field_bindings.get(id(field), bindings)
            if _is_scalar_discriminator_annotation(
                field.annotation,
                bindings_at_field,
                {enum_full},
            ):
                discriminator_fields.append((field_name, field))
        if len(fields) != 1 or len(discriminator_fields) != 1:
            _append_finding(
                findings,
                seen,
                parsed,
                base,
                "BC FrameworkErrorSchema base must narrow exactly one common field to own ErrorCode",
            )
        if len(discriminator_fields) == 1:
            discriminator_field_name, discriminator_field = discriminator_fields[0]
            discriminator_bindings = field_bindings.get(
                id(discriminator_field), bindings
            )
            discriminator_constructor_keys = _field_constructor_keys(
                discriminator_field,
                discriminator_bindings,
            )
            discriminator_constructor_paths = _field_constructor_paths(
                discriminator_field,
                discriminator_bindings,
            )
            _record_unresolved_field_contract(
                parsed,
                discriminator_field,
                discriminator_bindings,
                analysis,
            )
            if discriminator_field_name not in common_fields:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    discriminator_field,
                    "BC FrameworkErrorSchema discriminator must override common field",
                )
            else:
                contract = common_contracts[discriminator_field_name]
                discriminator_constructor_keys_complete = (
                    contract.constructor_keys_complete
                )
                discriminator_constructor_keys = frozenset(
                    set(discriminator_constructor_keys)
                    | set(contract.constructor_keys)
                )
                discriminator_constructor_paths = frozenset(
                    set(discriminator_constructor_paths)
                    | set(contract.constructor_paths)
                )
                narrowed_signature = _annotation_signature(
                    discriminator_field.annotation,
                    discriminator_bindings,
                    replacements={enum_full: "<bc-error-code>"},
                )
                if (
                    contract.discriminator_annotation is None
                    or narrowed_signature != contract.discriminator_annotation
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        discriminator_field,
                        "BC base must preserve common annotation/nullability while narrowing str to own ErrorCode",
                    )
                if (
                    _field_metadata_signature(
                        discriminator_field,
                        discriminator_bindings,
                    )
                    != contract.metadata
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        discriminator_field,
                        "BC base field metadata must match common FrameworkErrorSchema",
                    )
                discriminator_default = _field_default_expression(
                    discriminator_field,
                    discriminator_bindings,
                )
                # 승인 canon(2026-08-15): 식별자 field 를 자기 ErrorCode 로 «정확히»
                # 좁히면서 공통의 default 를 잃어 required 가 되는 모양은 위반이 아니다.
                # 면제는 세 조건 동시 충족일 때만 — ① 이 field 가 공통 식별자 field 이고
                # ② annotation 좁힘이 공통 계약과 정확히 일치하며(ErrorCode 좁힘 동반)
                # ③ 공통엔 default 가 있고 base 는 default 없이 required 다. 그 밖의
                # required/default 의미 변화(default 값·kind 드리프트, 역방향 default
                # 추가)는 계속 위반이다.
                narrowed_required_canon: bool = (
                    contract.discriminator_annotation is not None
                    and narrowed_signature == contract.discriminator_annotation
                    and not contract.required
                    and _field_default_kind(
                        discriminator_field,
                        discriminator_bindings,
                    )
                    == "required"
                )
                if (
                    _field_default_signature(
                        discriminator_field,
                        discriminator_bindings,
                        enum_full=enum_full,
                        enum_members=members,
                    )
                    != contract.default
                    and not narrowed_required_canon
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        discriminator_field,
                        "BC base must preserve common required/default semantics",
                    )
                if isinstance(discriminator_default, ast.Constant) and isinstance(
                    discriminator_default.value,
                    str,
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        discriminator_field,
                        "raw string FrameworkErrorSchema discriminator",
                    )
                base_discriminator_default_member = _enum_member_name(
                    discriminator_default,
                    discriminator_bindings,
                    enum_full,
                    members,
                )
                if (
                    _field_default_kind(
                        discriminator_field,
                        discriminator_bindings,
                    )
                    != "required"
                    and not _default_is_none(
                        discriminator_default,
                        discriminator_bindings,
                    )
                    and base_discriminator_default_member is None
                ):
                    # 멤버 사전(members) 종속 판정 — 사전이 동적으로 «불완전»할 때만
                    # 파생 오탐이 되므로 그때만 proof 위임(정적 사전에선 진짜 위반).
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        discriminator_field,
                        "BC base discriminator default must be own ErrorCode member or None",
                        requires_static_error_shape=members_dynamic,
                    )
        _class_member_findings(
            parsed,
            base,
            bindings,
            {discriminator_field_name} if discriminator_field_name is not None else set(),
            analysis,
            findings,
            seen,
        )

    known_concrete: set[str] = set()
    for node in classes:
        bindings = before.get(id(node), {})
        is_str_enum = any(_resolve(base, bindings) == STR_ENUM for base in node.bases)
        direct_common = any(_resolve(base, bindings) == COMMON_ERROR_OUT for base in node.bases)
        invalid_container = (
            node.name.endswith("ErrorCode")
            or is_str_enum
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
        if prepared_by_base:
            allowed_class_nodes.add(node)
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
        for field_name in set(fields) - common_fields:
            _append_finding(findings, seen, parsed, fields[field_name], "concrete adds field outside common shape")
        for field_name in set(fields) & common_fields:
            field = fields[field_name]
            bindings_at_field = field_bindings.get(id(field), bindings)
            _record_unresolved_field_contract(
                parsed,
                field,
                bindings_at_field,
                analysis,
            )
            contract = common_contracts[field_name]
            if (
                _field_metadata_signature(field, bindings_at_field)
                != contract.metadata
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    field,
                    "concrete field metadata must match common FrameworkErrorSchema",
                )
            if field_name == discriminator_field_name:
                actual_annotation = _annotation_signature(
                    field.annotation,
                    bindings_at_field,
                    replacements={enum_full: "<bc-error-code>"},
                )
                expected_annotation = contract.discriminator_annotation
                category = (
                    "concrete discriminator must preserve common annotation/nullability "
                    "while using own ErrorCode"
                )
            else:
                actual_annotation = _annotation_signature(
                    field.annotation,
                    bindings_at_field,
                )
                expected_annotation = contract.annotation
                category = "concrete field annotation/nullability must match common FrameworkErrorSchema"
            if actual_annotation != expected_annotation:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    field,
                    category,
                )
            if _field_is_required(field, bindings_at_field):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    field,
                    f"concrete field must have a no-arg default: {field_name}",
                )
        for field_name, contract in common_contracts.items():
            if not contract.required:
                continue
            if field_name == discriminator_field_name:
                inherited_default = base_discriminator_default_member is not None
            else:
                inherited_default = False
            if field_name not in fields and not inherited_default:
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    node,
                    f"concrete missing required default: {field_name}",
                )
        discriminator_field = (
            fields.get(discriminator_field_name)
            if discriminator_field_name is not None
            else None
        )
        if discriminator_field is not None:
            discriminator_bindings = field_bindings.get(
                id(discriminator_field), bindings
            )
            discriminator_default = _field_default_expression(
                discriminator_field,
                discriminator_bindings,
            )
            if isinstance(discriminator_default, ast.Constant) and isinstance(
                discriminator_default.value, str
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    discriminator_field,
                    "raw string FrameworkErrorSchema discriminator",
                )
            if (
                _enum_member_name(
                    discriminator_default,
                    discriminator_bindings,
                    enum_full,
                    members,
                )
                is None
            ):
                # 멤버 사전(members) 종속 판정 — 사전이 동적으로 «불완전»할 때만
                # 파생 오탐이 되므로 그때만 proof 위임(정적 사전에선 진짜 위반).
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    discriminator_field,
                    "concrete discriminator default must use own ErrorCode member",
                    requires_static_error_shape=members_dynamic,
                )
        elif base_discriminator_default_member is None:
            _append_finding(
                findings,
                seen,
                parsed,
                node,
                "concrete discriminator requires own ErrorCode default",
            )
        _class_member_findings(
            parsed,
            node,
            bindings,
            common_fields,
            analysis,
            findings,
            seen,
        )
    _bc_module_artifact_findings(
        parsed,
        allowed_class_nodes,
        findings,
        seen,
    )
    return (
        members,
        known_concrete,
        base_full,
        discriminator_field_name,
        discriminator_constructor_keys,
        discriminator_constructor_paths,
        discriminator_constructor_keys_complete,
    )


def _argument_names(arguments: ast.arguments) -> set[str]:
    positional = [
        *arguments.posonlyargs,
        *arguments.args,
        *arguments.kwonlyargs,
    ]
    names = {argument.arg for argument in positional}
    if arguments.vararg is not None:
        names.add(arguments.vararg.arg)
    if arguments.kwarg is not None:
        names.add(arguments.kwarg.arg)
    return names


def _function_argument_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    return _argument_names(node.args)


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
    known_classes: dict[str, KnownErrorClass],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> dict[str, str]:
    named_objects: dict[str, str] = {}

    def visit(
        node: ast.AST,
        scope_bindings: dict[str, str],
        exported_objects: dict[str, str],
    ) -> None:
        if isinstance(node, ast.Lambda):
            for default in node.args.defaults:
                visit(default, scope_bindings, exported_objects)
            for default in node.args.kw_defaults:
                if default is not None:
                    visit(default, scope_bindings, exported_objects)
            child_bindings = dict(scope_bindings)
            for name in _argument_names(node.args):
                child_bindings.pop(name, None)
            visit(node.body, child_bindings, {})
            return

        if isinstance(
            node,
            (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp),
        ):
            child_bindings = dict(scope_bindings)
            for generator in node.generators:
                visit(generator.iter, child_bindings, exported_objects)
                for name in _target_names(generator.target):
                    child_bindings.pop(name, None)
                for condition in generator.ifs:
                    visit(condition, child_bindings, exported_objects)
            if isinstance(node, ast.DictComp):
                visit(node.key, child_bindings, exported_objects)
                visit(node.value, child_bindings, exported_objects)
            else:
                visit(node.elt, child_bindings, exported_objects)
            return

        if isinstance(node, ast.NamedExpr):
            visit(node.value, scope_bindings, exported_objects)
            if isinstance(node.target, ast.Name) and isinstance(node.value, ast.Call):
                constructor = _resolve(node.value.func, scope_bindings)
                if constructor in known_classes:
                    exported_objects[node.target.id] = constructor
            return

        if isinstance(node, ast.Call):
            constructor = _resolve(node.func, scope_bindings)
            error_contract = known_classes.get(constructor or "")
            if error_contract is not None:
                entries: list[tuple[str, ast.AST, ast.AST]] = []
                for keyword in node.keywords:
                    if keyword.arg is not None:
                        entries.append((keyword.arg, keyword.value, keyword))
                        continue
                    if isinstance(keyword.value, ast.Dict) and all(
                        key is not None
                        and _static_string_value(key, scope_bindings) is not None
                        for key in keyword.value.keys
                    ):
                        entries.extend(
                            (
                                _static_string_value(key, scope_bindings) or "",
                                item,
                                keyword,
                            )
                            for key, item in zip(
                                keyword.value.keys,
                                keyword.value.values,
                            )
                            if key is not None
                        )
                    else:
                        error_contract.alias_analysis.append(
                            f"{parsed.relative_path}:{keyword.lineno} dynamic FrameworkErrorSchema **constructor argument 분석 불능"
                        )

                def value_at_path(
                    value: ast.AST,
                    tail: tuple[str | int, ...],
                ) -> tuple[str, ast.AST | None]:
                    if not tail:
                        return "found", value

                    static_container = _static_literal_value(
                        _resolve(value, scope_bindings)
                    )
                    if static_container is not _NO_STATIC_VALUE:
                        current: object = static_container
                        try:
                            for part in tail:
                                current = current[part]  # type: ignore[index]
                        except (IndexError, KeyError, TypeError):
                            return "missing", None
                        return "found", ast.Constant(current)

                    static_ast = _static_ast_value(
                        _resolve(value, scope_bindings)
                    )
                    if static_ast is not None:
                        return value_at_path(static_ast, tail)

                    part, remaining = tail[0], tail[1:]
                    if isinstance(value, ast.Dict):
                        state = "missing"
                        selected: ast.AST | None = None
                        for key, item in zip(value.keys, value.values):
                            if key is None:
                                unpack_state, unpack_value = value_at_path(
                                    item,
                                    (part,),
                                )
                                if unpack_state == "found":
                                    state, selected = "found", unpack_value
                                elif unpack_state == "uncertain":
                                    state, selected = "uncertain", None
                            elif _static_path_part(key, scope_bindings) == part:
                                state, selected = "found", item
                        if state != "found" or selected is None:
                            return state, None
                        return value_at_path(selected, remaining)
                    if (
                        isinstance(part, int)
                        and isinstance(value, (ast.List, ast.Tuple))
                    ):
                        if -len(value.elts) <= part < len(value.elts):
                            return value_at_path(value.elts[part], remaining)
                        return "missing", None
                    return "uncertain", None

                for key, value, anchor in entries:
                    discriminator_results = [
                        value_at_path(value, path[1:])
                        for path in error_contract.discriminator_paths
                        if path and path[0] == key
                    ]
                    if any(
                        _static_string_value(leaf, scope_bindings) is not None
                        for state, leaf in discriminator_results
                        if state == "found" and leaf is not None
                    ):
                        _append_finding(
                            findings,
                            seen,
                            parsed,
                            anchor,
                            "raw string discriminator constructor argument",
                        )
                    elif any(
                        state == "uncertain"
                        for state, _leaf in discriminator_results
                    ):
                        error_contract.alias_analysis.append(
                            f"{parsed.relative_path}:{anchor.lineno} discriminator validation path 분석 불능"
                        )
                    elif (
                        not error_contract.keys_complete
                        and key not in error_contract.discriminator_keys
                        and any(
                            _static_string_value(candidate, scope_bindings)
                            is not None
                            for candidate in ast.walk(value)
                        )
                    ):
                        error_contract.alias_analysis.append(
                            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                            f"{parsed.relative_path}:{anchor.lineno} custom alias_generator constructor-key 분석 불능"
                        )

        for child in ast.iter_child_nodes(node):
            visit(child, scope_bindings, exported_objects)

    for root in roots:
        visit(root, bindings, named_objects)
    return named_objects


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
    else:
        _bind_static_assignment(statement, bindings)


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
    known_classes: dict[str, KnownErrorClass],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    *,
    module_scope: bool,
    function_globals: dict[str, str],
    outside_bases: set[str] | None = None,
) -> dict[str, str]:
    bindings = dict(initial_bindings)
    local_objects = dict(initial_objects)
    for statement in statements:
        expression_objects = _raw_constructor_calls(
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
        local_objects.update(expression_objects)
        target_names = {name for target in targets for name in _target_names(target)}
        if isinstance(value, ast.Call):
            constructor = _resolve(value.func, bindings)
            if constructor in known_classes:
                for name in target_names:
                    local_objects[name] = constructor
        if (
            isinstance(statement, (ast.Assign, ast.AnnAssign))
            and _static_string_value(statement.value, bindings) is not None
        ):
            assignment_targets = (
                statement.targets
                if isinstance(statement, ast.Assign)
                else [statement.target]
            )
            for target in assignment_targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id in local_objects
                    and target.attr
                    in known_classes[
                        local_objects[target.value.id]
                    ].discriminator_keys
                ):
                    _append_finding(
                        findings,
                        seen,
                        parsed,
                        statement,
                        "raw string one-step discriminator assignment",
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
                outside_bases=outside_bases,
            )
        elif isinstance(statement, ast.ClassDef):
            if outside_bases and any(
                _resolve(base, bindings) in outside_bases
                for base in statement.bases
            ):
                _append_finding(
                    findings,
                    seen,
                    parsed,
                    statement,
                    "concrete FrameworkErrorSchema outside canonical module",
                )
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
                outside_bases=outside_bases,
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
                outside_bases=outside_bases,
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
                    outside_bases=outside_bases,
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
                outside_bases=outside_bases,
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
                    outside_bases=outside_bases,
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
                outside_bases=outside_bases,
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
                        outside_bases=outside_bases,
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
                outside_bases=outside_bases,
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
                outside_bases=outside_bases,
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
                        outside_bases=outside_bases,
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
                outside_bases=outside_bases,
            )

        _update_bindings(
            parsed, statement, bindings, module_scope=module_scope
        )
    return local_objects


def _raw_code_findings(
    parsed: ParsedSource,
    known_classes: dict[str, KnownErrorClass],
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


def _outside_canonical_class_findings(
    parsed: ParsedSource,
    known_bases: set[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    function_globals = _final_module_bindings(parsed)
    _raw_code_suite(
        parsed,
        parsed.tree.body,
        {},
        {},
        {},
        findings,
        seen,
        module_scope=True,
        function_globals=function_globals,
        outside_bases=known_bases,
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
    # #417·#414 — framework/ninja/ 는 공유 <technology> 폴더다: 오류 계약은 정본 모듈 하나
    # (framework_error_schema.py)에만 살고, 다른 <module>.py 는 이 계약의 대상이 아니다.
    # (옛 response/ 전용 패키지의 byte-empty·extra 금지 검사는 패키지 소멸과 함께 걷었다 —
    #  숨은 오류 스키마 모듈은 아래 noncanonical inventory 분석이 문다.)
    if COMMON_INIT not in inventory_paths:
        structural_blockers.append(f"필수 common artifact 부재: {COMMON_INIT}")
    if COMMON_ERROR not in inventory_paths:
        structural_blockers.append(f"필수 common artifact 부재: {COMMON_ERROR}")

    project_modules = _project_module_prefixes(inventory.relative_paths)
    common_contracts = _analyze_common(
        parsed.get(COMMON_ERROR),
        analysis,
        findings,
        seen,
        project_modules,
    )
    all_wire_values: dict[str, list[tuple[Path, str]]] = {}
    known_classes: dict[str, KnownErrorClass] = {}
    known_bases: set[str] = set()
    for path in sorted(code_paths, key=Path.as_posix):
        bc = _candidate_bc(path)
        source = parsed.get(path)
        if bc is None or source is None:
            continue
        (
            members,
            concretes,
            base_full,
            discriminator_field,
            discriminator_constructor_keys,
            discriminator_constructor_paths,
            discriminator_constructor_keys_complete,
        ) = _analyze_bc_module(
            source,
            bc,
            common_contracts,
            analysis,
            findings,
            seen,
            project_modules,
        )
        if discriminator_field is not None:
            error_contract = KnownErrorClass(
                discriminator_constructor_keys,
                discriminator_constructor_paths,
                discriminator_constructor_keys_complete,
                frozenset(members.values()),
                analysis,
            )
            known_classes[base_full] = error_contract
            known_classes.update(
                {
                    concrete: error_contract
                    for concrete in concretes
                }
            )
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
        _outside_canonical_class_findings(
            source,
            known_bases,
            findings,
            seen,
        )

    raw_paths = {Path(raw) for raw in config.controller_modules}
    raw_paths.update(code_paths)
    for path in sorted(raw_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is not None:
            _raw_code_findings(source, known_classes, findings, seen)
    return sorted(set(analysis)), sorted(
        findings, key=lambda item: (item.relative_path.as_posix(), item.lineno, item.category)
    ), sorted(set(structural_blockers))


# ── 표준 트리 슬라이스 — 트리 개정 명세 몫 4규칙 (트리 10행 · D27·D55) ──────
#
# 모든 프로필(auto 포함)에서 돈다 — 옛 판은 auto 에서 완전 무동작(fail-open)이었다.
#   #114 `driving_layer/api/bc_error_schema.py` 는 BC 당 정확히 한 파일 · api/ 가
#        있으면 «항상» 있다(HTTP 오류를 안 여는 BC 에도 빈 파일로).
#   #568 이름의 자는 «폴더 안이면 접두, 밖이면 접미» — api/ 직계의 error·schema
#        조합 딴 이름, schema/ 안의 error 파일이 위반.
#   #572 `<Bc>ErrorSchema` 와 `<Bc>ErrorCode` 는 함께 온다(코드는 스키마 code 필드의 타입).
#   #636 `<Bc>ErrorCode` 는 `StrEnum` 이다 — Literal·맨 문자열 상수 모음 금지.

_TREE_DRIVING = ("driving_layer",)
_TREE_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
_TREE_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")


def _tree_bcs(root: Path) -> list[Path]:
    out: list[Path] = []
    for c in root.rglob("application"):
        if not c.is_dir() or set(c.parts) & CODE_SKIP_DIRS:
            continue
        out.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return out


def _tree_adopted(bcs: list[Path]) -> bool:
    for bc in bcs:
        if any((bc / n).is_dir() for n in _TREE_LAYERS):
            return True
        if any((bc / m).is_file() for m in _TREE_APP_MARKERS):
            return True
        if any(p.is_dir() and p.name.startswith("django_") for p in bc.iterdir()):
            return True
    return False


def _tree_camel(bc_name: str) -> str:
    return "".join(part.capitalize() for part in bc_name.split("_"))


def _tree_slice(root: Path, bcs: list[Path]) -> list[str]:
    findings: list[str] = []
    for bc in bcs:
        expected_prefix = _tree_camel(bc.name)
        schema_files: list[Path] = []
        for driving in _TREE_DRIVING:
            api = bc / driving / "api"
            if not api.is_dir():
                continue
            api_rel = api.relative_to(root)
            schema_file = api / "bc_error_schema.py"
            if schema_file.is_file():
                schema_files.append(schema_file)
            else:
                findings.append(f"  [#114] {api_rel}: `bc_error_schema.py` 가 없다 — HTTP 오류를 아직 안 여는 BC 에도 «빈 파일»로 항상 있다(부모 api/ 가 항상이라)")
            for p in sorted(api.glob("*.py")):
                low = p.name.lower()
                if p.name != "bc_error_schema.py" and "error" in low and "schema" in low:
                    findings.append(f"  [#568] {p.relative_to(root)}: 폴더 밖 이름은 «접미» 자다 — BC 오류 스키마 파일은 `bc_error_schema.py` 하나다")
            for schema_dir in api.rglob("schema"):
                if not schema_dir.is_dir():
                    continue
                for p in sorted(schema_dir.glob("*error*.py")):
                    findings.append(f"  [#568] {p.relative_to(root)}: `schema/` 안 이름은 «접두» 자(schema_in/schema_out)다 — 오류 스키마는 `api/bc_error_schema.py` 로")
        if len(schema_files) > 1:
            findings.append(f"  [#114] {bc.relative_to(root)}: `bc_error_schema.py` 가 {len(schema_files)}개다 — BC 당 정확히 하나다")
        for schema_file in schema_files:
            rel = schema_file.relative_to(root)
            try:
                mod = ast.parse(schema_file.read_text(encoding="utf-8"))
            except (SyntaxError, OSError, UnicodeDecodeError):
                findings.append(f"  [분석] {rel}: bc_error_schema.py 를 파싱하지 못했다")
                continue
            classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
            schemas = [c for c in classes if c.name.endswith("ErrorSchema")]
            codes = [c for c in classes if c.name.endswith("ErrorCode")]
            strenum_names = {"StrEnum"}  # `from enum import StrEnum as X` 별칭도 StrEnum 이다
            for n in mod.body:
                if isinstance(n, ast.ImportFrom) and n.module == "enum":
                    strenum_names.update(a.asname or a.name for a in n.names if a.name == "StrEnum")
            if not schemas and not codes:
                continue  # 빈 파일 — HTTP 오류를 안 여는 BC(#114 문면)
            expected_schema = f"{expected_prefix}ErrorSchema"
            expected_code = f"{expected_prefix}ErrorCode"
            if not any(c.name == expected_schema for c in schemas):
                findings.append(f"  [#572] {rel}: 응답 본문 클래스 `{expected_schema}` 가 없다 — `<Bc>ErrorCode` 와 함께 온다(코드는 스키마 code 필드의 «타입»)")
            if not any(c.name == expected_code for c in codes):
                findings.append(f"  [#572] {rel}: 오류 코드 `{expected_code}` 가 없다 — `<Bc>ErrorSchema` 와 함께 온다(떼면 둘이 따로 는다)")
            for code_cls in codes:
                base_names = {b.attr if isinstance(b, ast.Attribute) else getattr(b, "id", "") for b in code_cls.bases}
                if not (base_names & strenum_names):
                    findings.append(f"  [#636] {rel}: `{code_cls.name}` 는 `StrEnum` 이어야 한다 — Literal·맨 문자열 상수 모음으로 대신하지 않는다")
    return findings


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
    except UsageError as exc:
        print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        return int(exc.code)

    if config.anchor is not None:
        # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚 파일·
        # 공허 차분이 침묵 exit 0 되지 않게 parse 직후 막는다(fail-closed).
        try:
            anchor_diff.validate_materials(config.root, config.anchor, config.anchor_debt_file)
        except anchor_diff.AnchorDiffUsage as exc:
            print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
            return 1

    # 표준 트리 슬라이스 — 프로필과 무관하게 먼저 본다(옛 auto 무동작 = fail-open 차단).
    bcs = _tree_bcs(config.root)
    if not any(
        (bc / d).is_dir() for bc in bcs for d in _TREE_DRIVING
    ) and _tree_adopted(bcs):
        print("[check-error-centralization] blocker: 채택 신호는 있는데 driving 층이 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2
    # --anchor 미지정이면 현행 그대로 각 슬라이스에서 즉시 exit 2 — 지정 시에만
    # 슬라이스 진단을 모아 마지막에 판정 차분(anchor_diff)으로 exit 를 정한다.
    collected: list[str] = []
    pending_analysis: list[str] = []
    tree_findings = _tree_slice(config.root, bcs)
    if tree_findings:
        print("[check-error-centralization] BLOCKER — BC 오류 스키마 동거 규율 위반 (트리 10행):")
        for f in tree_findings:
            print(f)
        if config.anchor is None:
            return 2
        collected.extend(tree_findings)

    if config.profile not in {None, "auto"}:
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
            dynamic_proof_only = bool(analysis) and all(
                issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED ")
                for issue in analysis
            )
            reported_findings = findings
            if dynamic_proof_only:
                # 정적 error shape 해석에 종속된 판정은 토큰-only 실행에서 억제하고
                # runtime proof 가 대신 검증한다(#15 requires_static_error_shape 동형).
                reported_findings = [
                    finding
                    for finding in findings
                    if not finding.requires_static_error_shape
                ]
            if (reported_findings or blockers) and (not analysis or dynamic_proof_only):
                print(
                    "[check-error-centralization] BLOCKER — code-profile FrameworkErrorSchema schema, "
                    "inventory, or raw code contract violation:"
                )
                for blocker in blockers:
                    print(f"  - {blocker}")
                for finding in reported_findings:
                    print(finding.render())
                if dynamic_proof_only:
                    # 토큰 진단을 삼키지 않는다(정보 손실 0) — exit 는 findings 가 정하되,
                    # 남은 정적 해석 불능이 «동적 error shape» 유형임을 함께 보고한다.
                    print(
                        "  (참고 — findings 해소 후 잔여 진단이 아래 토큰뿐이면 exit 1 "
                        "runtime proof 경로가 적용된다:)"
                    )
                    for issue in sorted(set(analysis)):
                        print(f"  - {issue}")
                print(
                    "  근거: common FrameworkErrorSchema는 프로젝트에서 승인한 exact wire shape의 단일 기반이고, 각 BC는 "
                    "canonical ErrorCode/FrameworkErrorSchema hierarchy와 project-wide unique wire code를 소유한다."
                )
                if config.anchor is None:
                    return 2
                collected.extend(f"  - {blocker}" for blocker in blockers)
                collected.extend(finding.render() for finding in reported_findings)
                if dynamic_proof_only:
                    # 토큰-only analysis 는 차분 강등으로 소거되지 않는다 — findings 가
                    # 전건 앵커 기존분이어도 proof 경로(exit 1)로 남긴다(fail-open 차단).
                    pending_analysis = sorted(set(analysis))
            elif analysis:
                raise UsageError("; ".join(sorted(set(analysis))))
        except UsageError as exc:
            print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
            return 1

    if collected:
        try:
            verdict = anchor_diff.partition_exit(
                script=Path(__file__).resolve(),
                label="[check-error-centralization]",
                target=config.root,
                anchor=config.anchor or "",
                argv=argv[1:],
                findings=collected,
                path_flags=frozenset(
                    {
                        "--api-module",
                        "--controller-module",
                        "--project-code-error-module",
                        "--project-preserve-error-module",
                    }
                ),
                debt_file=config.anchor_debt_file,
                analysis_pending=bool(pending_analysis),
            )
        except anchor_diff.AnchorDiffUsage as exc:
            print(f"[check-error-centralization] 사용 오류: {exc}", file=sys.stderr)
            return 1
        if verdict == 0 and pending_analysis:
            # 토큰-only analysis 는 강등으로 소거되지 않는다 — proof 경로(exit 1).
            print(
                "[check-error-centralization] 사용 오류: " + "; ".join(pending_analysis),
                file=sys.stderr,
            )
            return 1
        return verdict
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
