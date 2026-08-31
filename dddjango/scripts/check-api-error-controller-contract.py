#!/usr/bin/env python3
"""Enforce direct controller-owned code-profile error mapping.

The checker is deliberately profile- and source-selected.  ``auto`` and
``preserve-established`` validate their generic CLI/source contract and add no
new error-mapping semantics.  ``dddjango-code-json`` analyzes only selected
controllers owned by an ``error-bc``, every declared error BC's canonical
FrameworkErrorSchema module, and the same-owner presentation modules imported directly by
those controllers.

Exit codes: 0=clean/N/A/help, 2=contract blocker, 1=usage or analysis error.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 방출은 공용 ordered emitter(emit_all) 경유 — stdout 위반 라인 순서와
레코드 순서가 같고, 라인은 레코드 필드의 순수 함수다(출력 계약 v2). code-profile
category 의 #N 귀속/계약 잔류 판정은 귀속 매핑표 v2 가 정본이다
(정본 문서명: 2026-08-19-ontology-t2-1-attribution-map).
tree↔code 동일 사건 이중 방출은 tree 사이트 선점 억제로 막는다(귀속 매핑표 v2
overlap 절 — #62·#474 는 handler 행, ⓓ#125 는 route 함수 def 행 좌표).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: 없음(대장 미등재 — #74 소유자
  checker_lint(rule-owner-map) — 자기 조인 없음).
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

import anchor_diff
import checker_target
from findings import Candidates, ContractFindings, Findings, emit_all, lines, zero_target_guard
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Iterator


# code-profile 레인은 08-04 API-error 선행 계약 레인이다(registry #15). rule-owner-map
# 소유 5규칙(#59 «전역 예외 핸들러 금지» · #62 «except Exception 금지» · #125 «입구
# 로직 금지» · #126 «매핑을 helper 로 옮기지 않는다» · #474 «도메인 예외는 타입으로만»)
# 의 술어에 포섭되는 category 는 해당 #N violation 으로 방출하고(귀속 매핑표 v2 —
# 2026-08-19-ontology-t2-1-attribution-map §1: 원자 술어 23 = #N 12 · 계약 11),
# 그 밖의 category 만 08-04 선행 계약(rule=null + contract_ref)로 남는다.
CONTRACT_REF = "선행 계약(08-04 API-error) 소유"

ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
BC_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
HTTP_STATUS_CONSTANT_RE = re.compile(r"(?:^|\.)HTTP_[45]\d\d(?:_|$)")
STATIC_LITERAL_PREFIX = "<static-literal>:"
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
COMMON_ERROR_PATH = Path("framework/ninja/framework_error_schema.py")
COMMON_ERROR_MODULE = "framework.ninja.framework_error_schema"
COMMON_ERROR_OUT = f"{COMMON_ERROR_MODULE}.FrameworkErrorSchema"
COMMON_ERROR_BASENAME = "framework_error_schema"
COMMON_ERROR_PACKAGE = "framework.ninja"
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
TRY_STAR = getattr(ast, "TryStar", None)
MATCH = getattr(ast, "Match", None)
MATCH_AS = getattr(ast, "MatchAs", None)
MATCH_STAR = getattr(ast, "MatchStar", None)
MATCH_MAPPING = getattr(ast, "MatchMapping", None)
# 2026-08-26 리비전 7호 — 12-slot 의 두 번째 갈래는 «조회의 `None` path» 뿐이다. 실패를
# Result variant/outcome 값으로 돌려받아 분기하는 controller 는 exception path 위반(#571).
RESULT_VARIANT_BRANCH_FORBIDDEN = (
    "Result variant/outcome failure branch forbidden — known failures take the "
    "exception path; a use-case result carries only the success shape (#571)"
)


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
class ConstructorTarget:
    field: str
    path: tuple[str | int, ...]
    certain: bool


@dataclass(frozen=True)
class ErrorLanguage:
    common_fields: frozenset[str]
    required_common_fields: frozenset[str]
    integer_common_fields: frozenset[str]
    constructor_targets_by_key: dict[str, tuple[ConstructorTarget, ...]]
    certain_constructor_keys: frozenset[str]
    constructor_key_issues: tuple[str, ...]
    discriminator_fields_by_bc: dict[str, str]
    discriminator_default_is_member_by_bc: dict[str, bool]
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
    # 귀속 매핑표 v2 — category 가 소유 규칙 문면의 술어에 포섭되면 "#N"(violation 방출),
    # 08-04 선행 계약 잔류면 None(계약 방출 · rule=null + contract_ref).
    rule: str | None = None
    # 위반 심볼(U17) — 생성 지점 node 가 이름을 아는 경우만(FunctionDef/ClassDef 이름·
    # AnnAssign 대상), 불명이면 null.
    symbol: str | None = None
    # tree↔code 동일 사건 선점 억제 좌표(귀속 매핑표 v2 overlap 절) — #62/#474 는
    # handler 행, #125 는 route 함수 def 행. None 이면 억제 대상 아님.
    overlap_line: int | None = None
    requires_static_error_shape: bool = False


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

    if namespace.anchor is not None and namespace.anchor_baseline:
        issues.append(f"--anchor 와 {anchor_diff.BASELINE_FLAG} 는 함께 전달할 수 없음")
    if namespace.anchor_debt_file is not None and namespace.anchor is None:
        issues.append(f"{anchor_diff.DEBT_FLAG} 는 --anchor 와 함께만 쓸 수 있음(차분 전용 빚 채널)")
    if namespace.anchor_baseline and anchor_diff.is_git_worktree(root):
        issues.append(
            f"{anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용 — git 저장소 TARGET 금지"
        )
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
    if explicit and not controller_raw and not namespace.anchor_baseline:
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
        anchor=namespace.anchor,
        anchor_debt_file=namespace.anchor_debt_file,
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


def _static_literal_binding(value: object) -> Binding:
    return Binding(
        f"{STATIC_LITERAL_PREFIX}{type(value).__name__}:{value!r}",
        "static_literal",
    )


def _static_literal_value(binding: Binding | None) -> object:
    if binding is None or not binding.origin.startswith(STATIC_LITERAL_PREFIX):
        return _NO_STATIC_VALUE
    payload = binding.origin.removeprefix(STATIC_LITERAL_PREFIX)
    type_name, separator, literal = payload.partition(":")
    if not separator:
        return _NO_STATIC_VALUE
    try:
        value = ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return _NO_STATIC_VALUE
    return value if type(value).__name__ == type_name else _NO_STATIC_VALUE


_NO_STATIC_VALUE = object()


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
    if isinstance(value, ast.Constant):
        return _static_literal_binding(value.value)
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
    try:
        value = ast.literal_eval(node)
    except (SyntaxError, ValueError, TypeError):
        return None
    if isinstance(
        value,
        (type(None), bool, int, float, complex, str, bytes, tuple, list, set, dict),
    ):
        return bool(value)
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
        and parts[2] == "driving_layer"
        and parts[1] in scope_bcs
    ):
        return parts[1]
    return None


def _bc_error_path(bc: str) -> Path:
    return Path(f"application/{bc}/driving_layer/api/bc_error_schema.py")


def _snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def _classvar(annotation: ast.AST, bindings: dict[str, Binding]) -> bool:
    target = annotation.value if isinstance(annotation, ast.Subscript) else annotation
    raw = _expression_name(target)
    resolved = _resolve_binding(target, bindings)
    return raw in {"ClassVar", "typing.ClassVar"} or (
        resolved is not None and resolved.origin == "typing.ClassVar"
    )


def _scalar_int_annotation(
    annotation: ast.AST,
    bindings: dict[str, Binding],
) -> bool:
    current = annotation
    while isinstance(current, ast.Subscript):
        resolved_wrapper = _resolve_binding(current.value, bindings)
        wrapper = resolved_wrapper.origin if resolved_wrapper is not None else _expression_name(current.value)
        if wrapper not in {"Annotated", "typing.Annotated", "typing_extensions.Annotated"}:
            break
        current = current.slice.elts[0] if isinstance(current.slice, ast.Tuple) else current.slice
    raw = _expression_name(current)
    resolved = _resolve_binding(current, bindings)
    if raw in {"int", "builtins.int"} or (
        resolved is not None
        and resolved.origin
        in {
            "int",
            "builtins.int",
            "pydantic.StrictInt",
            "pydantic.types.StrictInt",
            "pydantic.PositiveInt",
            "pydantic.types.PositiveInt",
            "pydantic.NonNegativeInt",
            "pydantic.types.NonNegativeInt",
            "http.HTTPStatus",
        }
    ):
        return True

    def is_none(candidate: ast.AST) -> bool:
        name = _expression_name(candidate)
        resolved_candidate = _resolve_binding(candidate, bindings)
        return (
            isinstance(candidate, ast.Constant)
            and candidate.value is None
        ) or name in {"None", "NoneType", "types.NoneType"} or (
            resolved_candidate is not None
            and resolved_candidate.origin in {"None", "NoneType", "types.NoneType"}
        )

    if isinstance(current, ast.BinOp) and isinstance(current.op, ast.BitOr):
        return (
            _scalar_int_annotation(current.left, bindings) and is_none(current.right)
        ) or (
            is_none(current.left) and _scalar_int_annotation(current.right, bindings)
        )
    if isinstance(current, ast.Subscript):
        resolved_wrapper = _resolve_binding(current.value, bindings)
        wrapper = resolved_wrapper.origin if resolved_wrapper is not None else _expression_name(current.value)
        if wrapper in {"Optional", "typing.Optional"}:
            return _scalar_int_annotation(current.slice, bindings)
        if wrapper in {"Literal", "typing.Literal"}:
            parts = current.slice.elts if isinstance(current.slice, ast.Tuple) else [current.slice]
            values = [_static_value(part, bindings) for part in parts]
            return bool(values) and all(
                isinstance(value, int)
                and not isinstance(value, bool)
                and 400 <= value <= 599
                for value in values
            )
        if wrapper in {"Union", "typing.Union"}:
            parts = current.slice.elts if isinstance(current.slice, ast.Tuple) else [current.slice]
            return (
                len(parts) == 2
                and sum(is_none(part) for part in parts) == 1
                and any(_scalar_int_annotation(part, bindings) for part in parts)
            )
    return False


def _is_required_sentinel(
    value: ast.AST,
    bindings: dict[str, Binding],
) -> bool:
    if isinstance(value, ast.Constant) and value.value is Ellipsis:
        return True
    resolved_value = _resolve_binding(value, bindings)
    return resolved_value is not None and resolved_value.origin in {
        "pydantic_core.PydanticUndefined",
        "pydantic_core._pydantic_core.PydanticUndefined",
        "pydantic.fields.PydanticUndefined",
    }


def _annotated_parts(
    node: ast.AST,
    bindings: dict[str, Binding],
) -> tuple[ast.AST, tuple[ast.AST, ...]] | None:
    if not isinstance(node, ast.Subscript):
        return None
    resolved = _resolve_binding(node.value, bindings)
    wrapper = resolved.origin if resolved is not None else _expression_name(node.value)
    if wrapper not in {"Annotated", "typing.Annotated", "typing_extensions.Annotated"}:
        return None
    parts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    if not parts:
        return None
    return parts[0], tuple(parts[1:])


def _ordered_annotation_field_calls(
    node: ast.AST,
    bindings: dict[str, Binding],
) -> tuple[ast.Call, ...]:
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


def _field_call_default_kind(
    call: ast.Call,
    bindings: dict[str, Binding],
) -> str | None:
    resolved = _resolve_binding(call.func, bindings)
    if resolved is None or resolved.origin not in {
        "ninja.Field",
        "pydantic.Field",
        "pydantic.fields.Field",
    }:
        return None

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
        return "conflict"
    if (
        factory_declared
        and isinstance(factory_value, ast.Constant)
        and factory_value.value is Ellipsis
    ):
        return "invalid_factory"
    if factory_is_set:
        return "default_factory"
    if default_is_set:
        return "default"
    if factory_declared and isinstance(factory_value, ast.Constant) and (
        factory_value.value is None
    ):
        return "clear_factory"
    return "unspecified"


def _merge_field_default_kind(current: str, declared: str | None) -> str:
    if declared in {None, "unspecified"}:
        return current
    if current in {"conflict", "invalid_factory"}:
        return current
    if declared in {"conflict", "invalid_factory"}:
        return declared
    if declared == "clear_factory":
        return current if current == "default" else "required"
    if {current, declared} == {"default", "default_factory"}:
        return "conflict"
    return declared


def _field_default_kind(
    statement: ast.AnnAssign,
    bindings: dict[str, Binding],
) -> str:
    kind = "required"
    for candidate in _ordered_annotation_field_calls(statement.annotation, bindings):
        declared = _field_call_default_kind(candidate, bindings)
        kind = _merge_field_default_kind(kind, declared)
    value = statement.value
    if value is None:
        return kind
    if not isinstance(value, ast.Call):
        if _is_required_sentinel(value, bindings):
            return kind
        return "conflict" if kind == "default_factory" else "default"
    declared = _field_call_default_kind(value, bindings)
    return _merge_field_default_kind(kind, declared)


def _field_is_required(
    statement: ast.AnnAssign,
    bindings: dict[str, Binding],
) -> bool:
    return _field_default_kind(statement, bindings) == "required"


def _field_call_default_expression(
    call: ast.Call,
    bindings: dict[str, Binding],
) -> tuple[bool, ast.AST | None]:
    if not _is_field_call(call, bindings):
        return False, None
    for keyword in call.keywords:
        if keyword.arg == "default":
            if isinstance(keyword.value, ast.Constant) and keyword.value.value is Ellipsis:
                return True, None
            return True, keyword.value
        if keyword.arg == "default_factory":
            return True, None
    if call.args:
        first = call.args[0]
        if isinstance(first, ast.Constant) and first.value is Ellipsis:
            return True, None
        return True, first
    return False, None


def _field_default_expression(
    statement: ast.AnnAssign,
    bindings: dict[str, Binding],
) -> ast.AST | None:
    annotated_default: ast.AST | None = None
    for candidate in _ordered_annotation_field_calls(statement.annotation, bindings):
        declared, value = _field_call_default_expression(candidate, bindings)
        if declared:
            annotated_default = value
    if statement.value is None:
        return annotated_default
    if isinstance(statement.value, ast.Call):
        declared, value = _field_call_default_expression(statement.value, bindings)
        if declared:
            return value
        if _is_field_call(statement.value, bindings):
            return annotated_default
    return statement.value


def _is_field_call(node: ast.AST, bindings: dict[str, Binding]) -> bool:
    resolved = _resolve_binding(node.func, bindings) if isinstance(node, ast.Call) else None
    return resolved is not None and resolved.origin in FIELD_FACTORIES


def _static_value(node: ast.AST, bindings: dict[str, Binding]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, (ast.UAdd, ast.USub))
        and isinstance(node.operand, ast.Constant)
        and isinstance(node.operand.value, (int, float))
        and not isinstance(node.operand.value, bool)
    ):
        return (
            node.operand.value
            if isinstance(node.op, ast.UAdd)
            else -node.operand.value
        )
    return _static_literal_value(_resolve_binding(node, bindings))


def _static_string(node: ast.AST, bindings: dict[str, Binding]) -> str | None:
    value = _static_value(node, bindings)
    return value if isinstance(value, str) else None


def _alias_paths(
    node: ast.AST,
    bindings: dict[str, Binding],
) -> frozenset[tuple[str | int, ...]] | None:
    direct = _static_string(node, bindings)
    if direct is not None:
        return frozenset({(direct,)})
    if not isinstance(node, ast.Call):
        return None
    resolved = _resolve_binding(node.func, bindings)
    factory = resolved.origin if resolved is not None else None
    if factory in ALIAS_CHOICES_FACTORIES:
        choices = [_alias_paths(argument, bindings) for argument in node.args]
        if not choices or any(choice is None for choice in choices):
            return None
        return frozenset(path for choice in choices for path in (choice or ()))
    if factory in ALIAS_PATH_FACTORIES:
        parts: list[str | int] = []
        for argument in node.args:
            value = _static_value(argument, bindings)
            if isinstance(value, bool) or not isinstance(value, (str, int)):
                return None
            parts.append(value)
        return frozenset({tuple(parts)}) if parts else None
    return None


def _config_entries(
    value: ast.AST,
    bindings: dict[str, Binding],
) -> list[tuple[str, ast.AST]] | None:
    if isinstance(value, ast.Dict):
        entries: list[tuple[str, ast.AST]] = []
        for key, item in zip(value.keys, value.values):
            if key is None:
                return None
            name = _static_string(key, bindings)
            if name is None:
                return None
            entries.append((name, item))
        return entries
    if not isinstance(value, ast.Call):
        return None
    resolved = _resolve_binding(value.func, bindings)
    if resolved is None or resolved.origin not in {
        "pydantic.ConfigDict",
        "pydantic.config.ConfigDict",
        "dict",
    }:
        return None
    if value.args or any(keyword.arg is None for keyword in value.keywords):
        return None
    return [(keyword.arg, keyword.value) for keyword in value.keywords if keyword.arg]


def _project_config_entries(
    value: ast.AST,
    bindings: dict[str, Binding],
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
) -> list[tuple[str, ast.AST, dict[str, Binding]]] | None:
    if not isinstance(value, ast.Call) or value.args or value.keywords:
        return None
    resolved = _resolve_binding(value.func, bindings)
    if resolved is None or "." not in resolved.origin:
        return None
    module, function_name = resolved.origin.rsplit(".", 1)
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
        or function.args.args
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
    timeline = _binding_timeline(source)
    expected_binding = Binding(
        f"{_module_name(source.relative_path)}.{function_name}",
        "local_definition",
    )
    if timeline.final.get(function_name) != expected_binding:
        return None
    # Python resolves function globals when the function is called, not when
    # it is defined.  Final module bindings therefore own ConfigDict and every
    # symbol referenced by the returned configuration.
    function_bindings = timeline.final
    entries = _config_entries(body[0].value, function_bindings)
    if entries is None:
        return None
    return [(name, item, function_bindings) for name, item in entries]


def _common_validation_config(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, Binding],
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
    analysis: list[str],
) -> tuple[bool, bool, str | None, bool, bool, bool]:
    validate_by_name = False
    validate_by_alias = True
    alias_generator: str | None = None
    body_options: dict[str, tuple[ast.AST, dict[str, Binding]]] = {}
    body_config_seen = False
    body_config_known = True
    nested_config_options: dict[str, tuple[ast.AST, dict[str, Binding]]] = {}
    nested_config_seen = False
    before = _class_body_bindings(parsed, node, outer)
    for statement in node.body:
        bindings = before.get(id(statement), outer)
        targets: set[str] = set()
        value: ast.AST | None = None
        if isinstance(statement, ast.Assign):
            targets = {
                name
                for target in statement.targets
                for name in _target_names(target)
            }
            value = statement.value
        elif isinstance(statement, ast.AnnAssign):
            targets = _target_names(statement.target)
            value = statement.value
        if "model_config" in targets and value is not None:
            # The class namespace retains only the final assignment.  Treating
            # several ConfigDict values as an option merge would accept keys
            # that Pydantic rejects at runtime.
            body_config_seen = True
            body_options = {}
            entries = _config_entries(value, bindings)
            if entries is None:
                project_entries = _project_config_entries(
                    value,
                    bindings,
                    parsed_sources,
                    root,
                )
                if project_entries is None:
                    body_config_known = False
                else:
                    body_config_known = True
                    body_options = {
                        name: (item, item_bindings)
                        for name, item, item_bindings in project_entries
                    }
            else:
                body_config_known = True
                body_options = {name: (item, bindings) for name, item in entries}
        if isinstance(statement, ast.ClassDef) and statement.name == "Config":
            # Duplicate nested Config definitions follow normal Python binding
            # semantics too: only the final class is visible to the metaclass.
            nested_config_seen = True
            nested_config_options = {}
            config_before = _class_body_bindings(parsed, statement, bindings)
            for config_statement in statement.body:
                config_bindings = config_before.get(id(config_statement), bindings)
                names: set[str] = set()
                config_value: ast.AST | None = None
                if isinstance(config_statement, ast.Assign):
                    names = {
                        name
                        for target in config_statement.targets
                        for name in _target_names(target)
                    }
                    config_value = config_statement.value
                elif isinstance(config_statement, ast.AnnAssign):
                    names = _target_names(config_statement.target)
                    config_value = config_statement.value
                if config_value is not None:
                    for name in names:
                        nested_config_options[name] = (config_value, config_bindings)

    config_ambiguous = body_config_seen and nested_config_seen
    if config_ambiguous:
        analysis.append(
            f"{parsed.relative_path}:{node.lineno} common model_config/Config 동시 선언 분석 불능"
        )
    effective = dict(body_options if body_config_seen else nested_config_options)
    unknown_body = (body_config_seen and not body_config_known) or config_ambiguous

    # Pydantic metaclass class-header kwargs override body model_config keys.
    header_names: set[str] = set()
    for keyword in node.keywords:
        if keyword.arg is not None:
            header_names.add(keyword.arg)
            effective[keyword.arg] = (keyword.value, outer)

    validate_by_name_known = not unknown_body or "validate_by_name" in header_names
    validate_by_alias_known = not unknown_body or "validate_by_alias" in header_names
    alias_generator_known = not unknown_body or "alias_generator" in header_names

    def static_bool_option(name: str, default: bool) -> tuple[bool, bool, bool]:
        entry = effective.get(name)
        if entry is None:
            return default, True, False
        value, bindings = entry
        actual = _static_value(value, bindings)
        if actual is None:
            return default, True, False
        if isinstance(actual, bool):
            return actual, True, True
        analysis.append(
            f"{parsed.relative_path}:{getattr(value, 'lineno', node.lineno)} dynamic {name} 분석 불능"
        )
        return default, False, True

    explicit_name, explicit_name_known, explicit_name_declared = static_bool_option(
        "validate_by_name", False
    )
    populate_name, populate_name_known, populate_name_declared = static_bool_option(
        "populate_by_name", False
    )
    if explicit_name_declared:
        validate_by_name = explicit_name
        validate_by_name_known = validate_by_name_known and explicit_name_known
    elif populate_name_declared:
        validate_by_name = populate_name
        validate_by_name_known = validate_by_name_known and populate_name_known

    validate_by_alias, alias_value_known, _ = static_bool_option(
        "validate_by_alias", True
    )
    validate_by_alias_known = validate_by_alias_known and alias_value_known

    generator_entry = effective.get("alias_generator")
    if generator_entry is not None:
        value, bindings = generator_entry
        if isinstance(value, ast.Constant) and value.value is None:
            alias_generator = None
        else:
            resolved = _resolve_binding(value, bindings)
            if resolved is None:
                alias_generator = "<dynamic>"
                alias_generator_known = False
                analysis.append(
                    "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED "
                    f"{parsed.relative_path}:{getattr(value, 'lineno', node.lineno)} "
                    "dynamic alias_generator 분석 불능"
                )
            else:
                alias_generator = resolved.origin

    if unknown_body:
        analysis.append(
            f"DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED {parsed.relative_path}:{node.lineno} "
            "common model_config validation-key 분석 불능"
        )

    # Pydantic v2 enables name validation when alias validation alone is
    # explicitly disabled.  Model the effective pinned-runtime contract so a
    # valid ConfigDict(validate_by_alias=False) shape is not rejected.
    if (
        validate_by_alias_known
        and not validate_by_alias
        and not explicit_name_declared
    ):
        validate_by_name = True
    return (
        validate_by_name,
        validate_by_alias,
        alias_generator,
        validate_by_name_known,
        validate_by_alias_known,
        alias_generator_known,
    )


def _generated_alias(field_name: str, generator: str | None) -> str | None:
    if generator is None:
        return None
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
        # A condition depending on project runtime is intentionally not guessed.
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
    timeline = _binding_timeline(source)
    expected_binding = Binding(
        f"{_module_name(source.relative_path)}.{function_name}",
        "local_definition",
    )
    if timeline.final.get(function_name) != expected_binding:
        return None
    return _static_alias_expression(
        body[0].value,
        function.args.args[0].arg,
        field_name,
    )


def _constructor_fields_by_key(
    parsed: ParsedSource,
    node: ast.ClassDef,
    outer: dict[str, Binding],
    fields: set[str],
    parsed_sources: dict[Path, ParsedSource],
    root: Path,
    analysis: list[str],
) -> tuple[dict[str, tuple[ConstructorTarget, ...]], frozenset[str]]:
    (
        validate_by_name,
        validate_by_alias,
        alias_generator,
        validate_by_name_known,
        validate_by_alias_known,
        alias_generator_known,
    ) = _common_validation_config(
        parsed,
        node,
        outer,
        parsed_sources,
        root,
        analysis,
    )
    before = _class_body_bindings(parsed, node, outer)
    targets: dict[str, list[ConstructorTarget]] = {}
    for statement in node.body:
        if (
            not isinstance(statement, ast.AnnAssign)
            or not isinstance(statement.target, ast.Name)
            or statement.target.id not in fields
        ):
            continue
        field_name = statement.target.id
        bindings = before.get(id(statement), outer)
        if not validate_by_alias:
            if not validate_by_name:
                analysis.append(
                    f"{parsed.relative_path}:{statement.lineno} both validate_by_alias and validate_by_name are false"
                )
            target = ConstructorTarget(
                field_name,
                (field_name,),
                validate_by_name and validate_by_name_known and validate_by_alias_known,
            )
            targets.setdefault(field_name, []).append(target)
            continue
        validation_paths: frozenset[tuple[str | int, ...]] | None = None
        alias_priority: int | float | None = None
        alias_priority_known = True
        alias_paths_known = True
        field_calls = list(
            _ordered_annotation_field_calls(statement.annotation, bindings)
        )
        if _is_field_call(statement.value, bindings):
            assert isinstance(statement.value, ast.Call)
            field_calls.append(statement.value)
        for candidate in field_calls:
                keywords = {
                    keyword.arg: keyword.value
                    for keyword in candidate.keywords
                    if keyword.arg is not None
                }
                for keyword in candidate.keywords:
                    if keyword.arg == "alias_priority":
                        priority = _static_value(keyword.value, bindings)
                        if priority is None or isinstance(
                            priority,
                            (bool, int, float),
                        ):
                            alias_priority = priority
                        else:
                            alias_priority_known = False
                            analysis.append(
                                f"{parsed.relative_path}:{keyword.value.lineno} dynamic alias_priority 분석 불능: {field_name}"
                            )
                alias_node = keywords.get("alias")
                validation_node = keywords.get("validation_alias")
                alias_was_set = alias_node is not None
                if alias_was_set:
                    if isinstance(alias_node, ast.Constant) and alias_node.value is None:
                        # Field(alias=None) explicitly clears both alias and the
                        # validation alias derived from the previous FieldInfo.
                        validation_paths = None
                    else:
                        parsed_alias = _alias_paths(alias_node, bindings)
                        if parsed_alias is None or any(len(path) != 1 for path in parsed_alias):
                            alias_paths_known = False
                            analysis.append(
                                f"{parsed.relative_path}:{alias_node.lineno} alias constructor-key 분석 불능: {field_name}"
                            )
                            validation_paths = None
                        else:
                            validation_paths = parsed_alias
                if validation_node is not None and not (
                    isinstance(validation_node, ast.Constant)
                    and validation_node.value is None
                ):
                    parsed_validation = _alias_paths(validation_node, bindings)
                    if parsed_validation is None:
                        alias_paths_known = False
                        analysis.append(
                            f"{parsed.relative_path}:{validation_node.lineno} validation_alias constructor-key 분석 불능: {field_name}"
                        )
                        validation_paths = None
                    else:
                        validation_paths = parsed_validation

        priority_lets_generator_win = (
            alias_priority is not None
            and alias_priority != 0
            and alias_priority <= 1
        )
        generator_wins = alias_generator is not None and (
            validation_paths is None or priority_lets_generator_win
        )
        if generator_wins:
            generated = _generated_alias(field_name, alias_generator) or _project_alias(
                alias_generator,
                field_name,
                parsed_sources,
                root,
            )
            if generated is None:
                alias_generator_known = False
                analysis.append(
                    f"DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED {parsed.relative_path}:{statement.lineno} "
                    f"dynamic alias_generator constructor-key 분석 불능: {field_name}"
                )
                accepted_paths: set[tuple[str | int, ...]] = set()
            else:
                accepted_paths = {(generated,)}
        elif validation_paths is not None:
            accepted_paths = set(validation_paths)
        else:
            accepted_paths = {(field_name,)}

        if not validate_by_alias:
            accepted_paths = set()
        if validate_by_name:
            accepted_paths.add((field_name,))

        for path in accepted_paths:
            if not path or not isinstance(path[0], str):
                alias_paths_known = False
                analysis.append(
                    f"{parsed.relative_path}:{statement.lineno} invalid constructor path 분석 불능: {field_name}"
                )
                continue
            is_name_path = path == (field_name,)
            path_is_certain = (
                alias_paths_known
                and alias_priority_known
                and validate_by_alias_known
                and (
                    (is_name_path and validate_by_name and validate_by_name_known)
                    or (
                        validate_by_alias
                        and (not generator_wins or alias_generator_known)
                    )
                )
            )
            targets.setdefault(path[0], []).append(
                ConstructorTarget(field_name, path, path_is_certain)
            )

    frozen_targets = {
        key: tuple(dict.fromkeys(values))
        for key, values in targets.items()
    }
    certain = frozenset(
        key
        for key, values in frozen_targets.items()
        if values and all(value.certain for value in values)
    )
    return frozen_targets, certain


def _is_direct_enum_member(
    binding: Binding | None,
    enum_origin: str,
) -> bool:
    if binding is None:
        return False
    prefix = f"{enum_origin}."
    if not binding.origin.startswith(prefix):
        return False
    suffix = binding.origin.removeprefix(prefix)
    return bool(suffix) and "." not in suffix


def _public_fields(
    parsed: ParsedSource,
    node: ast.ClassDef,
    bindings: dict[str, Binding],
) -> tuple[set[str], set[str], set[str], list[str]]:
    fields: set[str] = set()
    required: set[str] = set()
    integer_fields: set[str] = set()
    issues: list[str] = []
    before = _class_body_bindings(parsed, node, bindings)
    for statement in node.body:
        statement_bindings = before.get(id(statement), bindings)
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorator_origins: set[str] = set()
            for decorator in statement.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                resolved = _resolve_binding(target, statement_bindings)
                decorator_origins.add(
                    resolved.origin
                    if resolved is not None
                    else (_expression_name(target) or "")
                )
            if (
                "pydantic.computed_field" in decorator_origins
                and statement.returns is not None
            ):
                fields.add(statement.name)
                if _scalar_int_annotation(statement.returns, statement_bindings):
                    integer_fields.add(statement.name)
            continue
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
            continue
        name = statement.target.id
        if (
            name.startswith("_")
            or name == "model_config"
            or _classvar(statement.annotation, statement_bindings)
        ):
            continue
        fields.add(name)
        if _scalar_int_annotation(statement.annotation, statement_bindings):
            integer_fields.add(name)
        default_kind = _field_default_kind(statement, statement_bindings)
        if default_kind == "required":
            required.add(name)
        elif default_kind in {"conflict", "invalid_factory"}:
            issues.append(
                f"{parsed.relative_path}:{statement.lineno} invalid Field default/default_factory contract: {default_kind}"
            )
    return fields, required, integer_fields, issues


def _error_language(
    parsed: dict[Path, ParsedSource],
    error_bcs: tuple[str, ...],
    root: Path,
    analysis: list[str],
) -> ErrorLanguage:
    common = parsed.get(COMMON_ERROR_PATH)
    common_fields: set[str] = set()
    required_common_fields: set[str] = set()
    integer_common_fields: set[str] = set()
    constructor_targets_by_key: dict[str, tuple[ConstructorTarget, ...]] = {}
    certain_constructor_keys: frozenset[str] = frozenset()
    constructor_key_issues: list[str] = []
    if common is None:
        analysis.append(f"필수 common FrameworkErrorSchema source 없음: {COMMON_ERROR_PATH}")
    else:
        timeline = _binding_timeline(common)
        classes = [
            node
            for node in common.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FrameworkErrorSchema"
        ]
        if len(classes) != 1:
            analysis.append(f"{COMMON_ERROR_PATH}: common FrameworkErrorSchema provenance 분석 불능")
        else:
            common_node = classes[0]
            common_bindings = timeline.before.get(id(common_node), {})
            (
                common_fields,
                required_common_fields,
                integer_common_fields,
                field_issues,
            ) = _public_fields(
                common,
                common_node,
                common_bindings,
            )
            analysis.extend(field_issues)
            if not common_fields:
                analysis.append(f"{COMMON_ERROR_PATH}: common public field set 분석 불능")
            (
                constructor_targets_by_key,
                certain_constructor_keys,
            ) = _constructor_fields_by_key(
                common,
                common_node,
                common_bindings,
                common_fields,
                parsed,
                root,
                constructor_key_issues,
            )

    bases: dict[str, str] = {}
    prepared: dict[str, frozenset[str]] = {}
    discriminator_fields: dict[str, str] = {}
    discriminator_defaults: dict[str, bool] = {}
    for bc in error_bcs:
        path = _bc_error_path(bc)
        source = parsed.get(path)
        if source is None:
            analysis.append(f"필수 canonical FrameworkErrorSchema source 없음: {path}")
            continue
        timeline = _binding_timeline(source)
        prefix = _snake_to_pascal(bc)
        base_name = f"{prefix}ErrorSchema"
        module = _module_name(path)
        base_origin = f"{module}.{base_name}"
        classes = [node for node in source.tree.body if isinstance(node, ast.ClassDef)]
        base_nodes = [node for node in classes if node.name == base_name]
        if len(base_nodes) != 1:
            analysis.append(f"{path}: {base_name} provenance 분석 불능")
            continue
        bases[bc] = base_origin
        base_node = base_nodes[0]
        base_bindings = timeline.before.get(id(base_node), {})
        base_before = _class_body_bindings(source, base_node, base_bindings)
        enum_origin = f"{module}.{prefix}ErrorCode"
        discriminator_candidates: list[tuple[str, ast.AnnAssign, dict[str, Binding]]] = []
        for statement in base_node.body:
            if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
                continue
            statement_bindings = base_before.get(id(statement), base_bindings)
            contains_enum = any(
                (
                    resolved := _resolve_binding(candidate, statement_bindings)
                ) is not None
                and (
                    resolved.origin == enum_origin
                    or resolved.origin.startswith(f"{enum_origin}.")
                )
                for candidate in ast.walk(statement.annotation)
                if isinstance(candidate, (ast.Name, ast.Attribute))
            )
            if contains_enum:
                discriminator_candidates.append(
                    (statement.target.id, statement, statement_bindings)
                )
        if len(discriminator_candidates) != 1:
            analysis.append(
                f"{path}: {base_name} discriminator provenance 분석 불능"
            )
        else:
            discriminator_name, discriminator_statement, discriminator_bindings = (
                discriminator_candidates[0]
            )
            discriminator_fields[bc] = discriminator_name
            default = _field_default_expression(
                discriminator_statement,
                discriminator_bindings,
            )
            resolved_default = (
                _resolve_binding(default, discriminator_bindings)
                if default is not None
                else None
            )
            discriminator_defaults[bc] = _is_direct_enum_member(
                resolved_default,
                enum_origin,
            )
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
                analysis.append(f"{path}:{node.lineno} prepared FrameworkErrorSchema base provenance 분석 불능")
        prepared[bc] = frozenset(known)
    return ErrorLanguage(
        frozenset(common_fields),
        frozenset(required_common_fields),
        frozenset(integer_common_fields),
        constructor_targets_by_key,
        certain_constructor_keys,
        tuple(sorted(set(constructor_key_issues))),
        discriminator_fields,
        discriminator_defaults,
        bases,
        prepared,
    )


def _node_symbol(node: ast.AST) -> str | None:
    """위반 심볼(U17) — node 가 안정 이름을 가진 경우만 채우고, 그 밖은 null."""
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return node.name
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def _append_finding(
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    parsed: ParsedSource,
    node: ast.AST,
    category: str,
    *,
    rule: str | None = None,
    overlap_line: int | None = None,
    requires_static_error_shape: bool = False,
) -> None:
    lineno = getattr(node, "lineno", 1)
    key = (parsed.relative_path, lineno, category)
    if key in seen:
        return
    seen.add(key)
    source_lines = parsed.source.splitlines()
    shown = (
        source_lines[lineno - 1].strip()
        if 0 < lineno <= len(source_lines)
        else category
    )
    findings.append(
        Finding(
            parsed.relative_path,
            lineno,
            category,
            shown,
            rule=rule,
            symbol=_node_symbol(node),
            overlap_line=overlap_line,
            requires_static_error_shape=requires_static_error_shape,
        )
    )


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
    prefix = f"application.{owner_bc}.driving_layer"
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


def _api_one_hop_paths(
    parsed: ParsedSource,
    module_paths: dict[str, Path],
) -> set[Path]:
    """Select direct helper modules in the configured API module's package."""

    selected: set[Path] = set()
    api_module = _module_name(parsed.relative_path)
    package = api_module.rsplit(".", 1)[0] if "." in api_module else api_module

    def select(module: str) -> None:
        if module != package and not module.startswith(f"{package}."):
            return
        path = module_paths.get(module)
        if path is not None and path != parsed.relative_path:
            selected.add(path)

    for statement in parsed.tree.body:
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                select(alias.name)
            continue
        if not isinstance(statement, ast.ImportFrom):
            continue
        module = _absolute_from_module(parsed.relative_path, statement)
        if module is None:
            continue
        select(module)
        for alias in statement.names:
            if alias.name != "*":
                select(f"{module}.{alias.name}")
    return selected


def _operation_one_hop_paths(
    parsed: ParsedSource,
    operations: list[Operation],
    owner_bc: str,
    module_paths: dict[str, Path],
) -> set[Path]:
    """Select presentation-local modules imported on executable operation paths."""

    selected: set[Path] = set()

    def select(module: str) -> None:
        if not _presentation_module(module, owner_bc):
            return
        path = module_paths.get(module)
        if path is not None:
            selected.add(path)

    def literal_iteration(node: ast.AST) -> bool | None:
        try:
            value = ast.literal_eval(node)
        except (SyntaxError, ValueError, TypeError):
            return None
        if isinstance(value, (tuple, list, set, frozenset, dict, str, bytes)):
            return bool(value)
        return None

    def literal_only(node: ast.AST | None) -> bool:
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return all(literal_only(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return all(
                (key is None or literal_only(key)) and literal_only(value)
                for key, value in zip(node.keys, node.values)
            )
        return False

    def statement_may_raise(statement: ast.stmt) -> bool:
        if isinstance(statement, (ast.Pass, ast.Global, ast.Nonlocal)):
            return False
        if isinstance(statement, ast.Expr):
            return not literal_only(statement.value)
        if isinstance(statement, ast.Assign):
            return not literal_only(statement.value)
        if isinstance(statement, ast.AnnAssign):
            return statement.value is not None and not literal_only(statement.value)
        return True

    def suite_may_raise(suite: list[ast.stmt]) -> bool:
        return any(statement_may_raise(statement) for statement in suite)

    def pattern_matches(pattern: ast.AST, value: object) -> bool | None:
        if MATCH_AS is not None and isinstance(pattern, MATCH_AS):
            if pattern.pattern is None:
                return True
            return pattern_matches(pattern.pattern, value)
        if isinstance(pattern, ast.MatchValue):
            try:
                expected = ast.literal_eval(pattern.value)
            except (SyntaxError, ValueError, TypeError):
                return None
            return expected == value
        if isinstance(pattern, ast.MatchSingleton):
            return pattern.value is value
        if isinstance(pattern, ast.MatchOr):
            results = [pattern_matches(item, value) for item in pattern.patterns]
            if True in results:
                return True
            if all(result is False for result in results):
                return False
        return None

    def scan_statement(statement: ast.stmt) -> set[str]:
        if isinstance(statement, ast.If):
            truth = _literal_truth(statement.test)
            if truth is True:
                return scan(statement.body)
            if truth is False:
                return scan(statement.orelse)
            return scan(statement.body) | scan(statement.orelse)
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                select(alias.name)
        elif isinstance(statement, ast.ImportFrom):
            module = _absolute_from_module(parsed.relative_path, statement)
            if module is not None:
                select(module)
                for alias in statement.names:
                    if alias.name != "*":
                        select(f"{module}.{alias.name}")
        elif isinstance(statement, (ast.Try, TRY_STAR or ast.Try)):
            body_controls = scan(statement.body)
            outcomes = {
                control for control in body_controls if control != "normal"
            }
            if "normal" in body_controls:
                outcomes.update(scan(statement.orelse))
            if suite_may_raise(statement.body):
                for handler in statement.handlers:
                    outcomes.update(scan(handler.body))
            if not outcomes:
                outcomes.add("normal")
            if statement.finalbody:
                final_controls = scan(statement.finalbody)
                if final_controls != {"normal"}:
                    outcomes = {
                        control
                        for control in final_controls
                        if control != "normal"
                    } | (
                        outcomes if "normal" in final_controls else set()
                    )
            return outcomes
        elif isinstance(statement, (ast.For, ast.AsyncFor)):
            iteration = literal_iteration(statement.iter)
            if iteration is False:
                return scan(statement.orelse)
            body_controls = scan(statement.body)
            outcomes: set[str] = set()
            if iteration is None:
                outcomes.update(scan(statement.orelse))
            if "break" in body_controls:
                outcomes.add("normal")
            if body_controls & {"normal", "continue"}:
                outcomes.update(scan(statement.orelse))
            outcomes.update(body_controls & {"return", "raise"})
            return outcomes
        elif isinstance(statement, ast.While):
            truth = _literal_truth(statement.test)
            if truth is False:
                return scan(statement.orelse)
            body_controls = scan(statement.body)
            outcomes = set(body_controls & {"return", "raise"})
            if "break" in body_controls:
                outcomes.add("normal")
            if truth is None:
                outcomes.update(scan(statement.orelse))
                if body_controls & {"normal", "continue"}:
                    outcomes.update(scan(statement.orelse))
            return outcomes
        elif isinstance(statement, (ast.With, ast.AsyncWith)):
            return scan(statement.body)
        elif MATCH is not None and isinstance(statement, MATCH):
            try:
                subject = ast.literal_eval(statement.subject)
            except (SyntaxError, ValueError, TypeError):
                subject = _NO_STATIC_VALUE
            outcomes: set[str] = set()
            exhaustive = False
            for case in statement.cases:
                match = (
                    pattern_matches(case.pattern, subject)
                    if subject is not _NO_STATIC_VALUE
                    else (
                        True
                        if MATCH_AS is not None
                        and isinstance(case.pattern, MATCH_AS)
                        and case.pattern.pattern is None
                        else None
                    )
                )
                guard_truth = (
                    True if case.guard is None else _literal_truth(case.guard)
                )
                if match is False or guard_truth is False:
                    continue
                outcomes.update(scan(case.body))
                if match is True and guard_truth is True:
                    exhaustive = True
                    break
            if not exhaustive:
                outcomes.add("normal")
            return outcomes
        if isinstance(statement, ast.Return):
            return {"return"}
        if isinstance(statement, ast.Raise):
            return {"raise"}
        if isinstance(statement, ast.Break):
            return {"break"}
        if isinstance(statement, ast.Continue):
            return {"continue"}
        return {"normal"}

    def scan(suite: list[ast.stmt]) -> set[str]:
        outcomes = {"normal"}
        for statement in suite:
            if "normal" not in outcomes:
                break
            outcomes.remove("normal")
            outcomes.update(scan_statement(statement))
        return outcomes

    for operation in operations:
        scan(operation.node.body)
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
                    "(application/<scope-bc>/driving_layer/... 필요)"
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
                f"{operation.parsed.relative_path}:{call.lineno} FrameworkErrorSchema function-local binding provenance 분석 불능: {name}"
            )
        return None
    binding = operation.body_bindings.get(name)
    if binding is None:
        if name in known_tails or definition_was_known:
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} FrameworkErrorSchema canonical provenance 분석 불능: {name}"
            )
        return None
    if binding.origin not in known:
        if (
            name in known_tails
            or definition_was_known
            or binding.origin.rsplit(".", 1)[-1] in known_tails
        ):
            analysis.append(
                f"{operation.parsed.relative_path}:{call.lineno} FrameworkErrorSchema re-export provenance 분석 불능: {binding.origin}"
            )
        return None
    if binding.kind not in {"symbol_import", "local_definition"}:
        analysis.append(
            f"{operation.parsed.relative_path}:{call.lineno} FrameworkErrorSchema direct provenance 분석 불능: {name}"
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


_PATH_MISSING = object()
_PATH_UNKNOWN = object()


def _constructor_path_value(
    value: ast.AST,
    path: tuple[str | int, ...],
    bindings: dict[str, Binding],
) -> ast.AST | object:
    """Resolve a statically visible AliasPath leaf without executing project code."""

    current: ast.AST | object = value
    for part in path:
        if not isinstance(current, ast.AST):
            return current
        if isinstance(current, ast.Dict):
            selected: ast.AST | object = _PATH_MISSING
            for key, item in zip(current.keys, current.values):
                if key is None:
                    nested = _constructor_path_value(item, (part,), bindings)
                    if nested is _PATH_UNKNOWN:
                        selected = _PATH_UNKNOWN
                    elif nested is not _PATH_MISSING:
                        selected = nested
                    continue
                static_key = _static_value(key, bindings)
                if static_key is _NO_STATIC_VALUE:
                    selected = _PATH_UNKNOWN
                elif static_key == part:
                    selected = item
            current = selected
            continue
        if (
            isinstance(part, int)
            and not isinstance(part, bool)
            and isinstance(current, (ast.List, ast.Tuple))
        ):
            index = part if part >= 0 else len(current.elts) + part
            current = (
                current.elts[index]
                if 0 <= index < len(current.elts)
                else _PATH_MISSING
            )
            continue
        return _PATH_UNKNOWN
    return current


def _constructor_arguments_valid(
    kind: str,
    constructor_origin: str,
    call: ast.Call,
    language: ErrorLanguage,
    operation: Operation,
    analysis: list[str],
) -> bool:
    if kind == "prepared":
        return not call.args and not call.keywords
    if kind != "base" or call.args:
        return False
    names = [keyword.arg for keyword in call.keywords]
    if not all(name is not None for name in names) or len(names) != len(set(names)):
        return False
    actual_names = {name for name in names if name is not None}
    if language.constructor_key_issues and not actual_names <= set(
        language.certain_constructor_keys
    ):
        analysis.extend(language.constructor_key_issues)
        return False
    supplied: list[tuple[str, ast.keyword, ast.AST]] = []
    for keyword in call.keywords:
        assert keyword.arg is not None
        targets = language.constructor_targets_by_key.get(keyword.arg)
        if not targets:
            analysis.extend(language.constructor_key_issues)
            return False
        matched = False
        for target in targets:
            leaf = _constructor_path_value(
                keyword.value,
                target.path[1:],
                operation.body_bindings,
            )
            if leaf is _PATH_UNKNOWN:
                analysis.append(
                    f"{operation.parsed.relative_path}:{keyword.value.lineno} "
                    f"constructor AliasPath value 분석 불능: {target.path!r}"
                )
                return False
            if leaf is _PATH_MISSING:
                continue
            assert isinstance(leaf, ast.AST)
            supplied.append((target.field, keyword, leaf))
            matched = True
        if not matched:
            return False

    actual_fields = {field for field, _, _ in supplied}
    if len(actual_fields) != len(supplied):
        return False
    if not language.required_common_fields <= actual_fields <= language.common_fields:
        return False

    bc = next(
        (
            owner
            for owner, base_origin in language.bases_by_bc.items()
            if base_origin == constructor_origin
        ),
        None,
    )
    if bc is None:
        return False
    discriminator = language.discriminator_fields_by_bc.get(bc)
    if discriminator is None:
        return False
    discriminator_values = [
        value
        for field, _, value in supplied
        if field == discriminator
    ]
    if not discriminator_values:
        return language.discriminator_default_is_member_by_bc.get(bc, False)
    if len(discriminator_values) != 1:
        return False
    value = discriminator_values[0]
    root = _expression_name(value)
    if root is not None and root.split(".", 1)[0] in operation.local_names:
        return False
    resolved = _resolve_binding(value, operation.body_bindings)
    enum_origin = (
        f"application.{bc}.driving_layer.api.bc_error_schema."
        f"{_snake_to_pascal(bc)}ErrorCode"
    )
    return _is_direct_enum_member(resolved, enum_origin)


def _exact_status_return(
    operation: Operation,
    statement: ast.Return,
    error_name: str,
    language: ErrorLanguage,
    analysis: list[str],
) -> ast.Call | None:
    call = statement.value
    if not isinstance(call, ast.Call) or not _status_call(operation, call, analysis):
        return None
    if call.keywords or len(call.args) != 2:
        return None
    first, second = call.args
    same_error_field = (
        isinstance(first, ast.Attribute)
        and not first.attr.startswith("_")
        and first.attr in language.integer_common_fields
        and isinstance(first.value, ast.Name)
        and first.value.id == error_name
    )
    literal_status = (
        isinstance(first, ast.Constant)
        and isinstance(first.value, int)
        and not isinstance(first.value, bool)
        and 400 <= first.value <= 599
    )
    first_root = (_expression_name(first) or "").split(".", 1)[0]
    resolved_status = (
        None
        if first_root in operation.local_names
        else _resolve_binding(first, operation.body_bindings)
    )
    named_status = False
    if resolved_status is not None:
        origin = resolved_status.origin
        static_status = _static_literal_value(resolved_status)
        if (
            isinstance(static_status, int)
            and not isinstance(static_status, bool)
            and 400 <= static_status <= 599
        ):
            named_status = True
        elif origin.startswith(("ninja.status.", "ninja_extra.status.")):
            match = HTTP_STATUS_CONSTANT_RE.search(origin)
            named_status = match is not None
        elif origin.startswith("http.HTTPStatus."):
            member_name = origin.rsplit(".", 1)[-1]
            member = HTTPStatus.__members__.get(member_name)
            named_status = member is not None and 400 <= int(member) <= 599
    if not (
        (same_error_field or literal_status or named_status)
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
    delegated_category: str,
) -> bool:
    body = _without_docstrings(statements)
    if len(body) < 2:
        anchor = body[0] if body else operation.node
        _append_finding(
            findings,
            seen,
            operation.parsed,
            anchor,
            category,
            requires_static_error_shape=True,
        )
        return False
    assignment = body[0]
    error_name = _simple_assignment_target(assignment)
    value = _statement_value(assignment)
    constructor = (
        _known_constructor(operation, value, language, analysis)
        if isinstance(value, ast.Call)
        else None
    )
    # 행19ⓐ/20ⓐ(귀속 매핑표 v2 — U3 분할): 오류 «생성»이 canonical constructor 가
    # 아닌 호출(helper/factory/serializer)에 위임된 실패만 #126 «helper·factory·
    # serializer 로 옮기지 않는다» 축자 포섭 — 그 밖의 본문 형태 오류(본문 길이·
    # constructor 인자·중간 문장·Status 반환)는 08-04 계약 잔류(ⓑ 기존 문면 유지).
    delegated: bool = (
        error_name is not None
        and isinstance(value, ast.Call)
        and constructor is None
    )
    valid = True
    if error_name is None or not isinstance(value, ast.Call) or constructor is None:
        valid = False
    elif not _constructor_arguments_valid(
        constructor[0],
        constructor[1],
        value,
        language,
        operation,
        analysis,
    ):
        valid = False
    elif constructor[0] == "common":
        valid = False

    for statement in body[1:-1]:
        if not _header_assignment_valid(operation, statement, analysis):
            valid = False
    final = body[-1]
    status_call = (
        _exact_status_return(operation, final, error_name, language, analysis)
        if isinstance(final, ast.Return) and error_name is not None
        else None
    )
    if status_call is None:
        valid = False
    if valid and isinstance(value, ast.Call) and status_call is not None:
        allowed_error_calls.add(id(value))
        allowed_status_calls.add(id(status_call))
        return True
    _append_finding(
        findings,
        seen,
        operation.parsed,
        body[0],
        delegated_category if delegated else category,
        rule="#126" if delegated else None,  # 행19ⓐ/20ⓐ — «helper·factory 로 옮기지 않는다» 축자
        requires_static_error_shape=True,
    )
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


def _exception_origin_layer(operation: Operation, node: ast.AST) -> str | None:
    """catch type 의 층 판별(행7 분할 재료 — 귀속 매핑표 v2 U1·V5).

    _exception_origin_valid 와 같은 binding 해석으로 자기 BC 의 domain_layer/
    application_layer 만 확정하고, 그 밖(로컬 섀도잉·비 symbol_import·타 출처)은
    None(층 미확정)으로 둔다."""
    if not isinstance(node, ast.Name):
        return None
    if node.id in operation.local_names:
        return None
    binding = operation.body_bindings.get(node.id)
    if binding is None or binding.kind != "symbol_import":
        return None
    prefix = f"application.{operation.owner_bc}."
    if not binding.origin.startswith(prefix):
        return None
    remainder = binding.origin[len(prefix) :]
    if remainder.startswith("domain_layer."):
        return "domain"
    if remainder.startswith("application_layer."):
        return "application"
    return None


def _handler_forwarding_attribution(
    operation: Operation,
    handler: ast.ExceptHandler,
) -> tuple[str, str | None]:
    """행7 분할(귀속 매핑표 v2 — U1·V5): catch 출처(provenance)로 category 를 나눈다.

    ⓐ 도메인 예외 전달 = #474 «입구 파일은 도메인 예외를 타입으로만 쓴다» ·
    ⓑ 응용 예외 전달 = 08-04 계약(managed catch 규율 고유) ·
    층 미확정 잔여(혼합 tuple catch 등)는 계약 보수(기존 문면 유지 — U3 준용)."""
    layers: set[str] = set()
    for type_node in _handler_type_names(handler.type) or []:
        layer = _exception_origin_layer(operation, type_node)
        if layer is None:
            return "caught exception forwarding forbidden", None
        layers.add(layer)
    if layers == {"domain"}:
        return "caught domain exception forwarding forbidden", "#474"
    if layers == {"application"}:
        return "caught application exception forwarding forbidden", None
    return "caught exception forwarding forbidden", None


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
        # 행3(#125) — «입구에 로직을 두지 않는다» 확정 위반. tree ⓓ#125 겹침은
        # route 함수 def 행 좌표로 선점 억제(overlap 절).
        _append_finding(
            findings,
            seen,
            operation.parsed,
            node,
            "raise inside managed try",
            rule="#125",
            overlap_line=operation.node.lineno,
        )
    for handler in node.handlers:
        type_nodes = _handler_type_names(handler.type)
        if type_nodes is None:
            # 행4(#62) — bare `except:` 는 catch-all 의 극단형.
            _append_finding(
                findings,
                seen,
                operation.parsed,
                handler,
                "bare catch forbidden",
                rule="#62",
                overlap_line=handler.lineno,
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
                    # 행5(#62) — 자기 BC 도메인·응용 예외 밖 catch = «한정» 위반.
                    _append_finding(
                        findings,
                        seen,
                        operation.parsed,
                        type_node,
                        "catch must be direct own-BC application/domain exception",
                        rule="#62",
                        overlap_line=handler.lineno,
                    )
        if any(
            isinstance(candidate, ast.Raise)
            for candidate in _iter_lexical_nodes(handler.body)
        ):
            # 행6(#125) — catch arm 안 `raise` 도 «입구 로직 금지» 밖 동작.
            _append_finding(
                findings,
                seen,
                operation.parsed,
                handler,
                "raise inside managed catch",
                rule="#125",
                overlap_line=operation.node.lineno,
            )
        if _caught_exception_forwarded(handler):
            # 행7 분할(U1·V5) — 도메인 전달 = #474 / 응용 전달·층 미확정 = 계약.
            forward_category, forward_rule = _handler_forwarding_attribution(
                operation, handler
            )
            _append_finding(
                findings,
                seen,
                operation.parsed,
                handler,
                forward_category,
                rule=forward_rule,
                overlap_line=handler.lineno if forward_rule == "#474" else None,
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
            "managed catch must directly construct FrameworkErrorSchema and return Status",
            "managed catch delegates error construction to helper/factory/serializer",
        )


def _result_compare_kind(test: ast.AST) -> str | None:
    """Result predicate 의 비교 형태 — `is None` → "none" · `== "<literal>"` → "literal"."""
    if not (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
    ):
        return None
    constant = test.comparators[0].value
    if isinstance(test.ops[0], ast.Is) and constant is None:
        return "none"
    if isinstance(test.ops[0], ast.Eq) and isinstance(constant, str):
        return "literal"
    return None


def _subject_root_name(node: ast.AST) -> str | None:
    """분기 주어(subject)의 뿌리 이름 — `result` · `result.<field>` · 별칭 이름."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id
    return None


def _result_test_name(test: ast.AST) -> str | None:
    if _result_compare_kind(test) is not None:
        return _subject_root_name(test.left)
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


def _result_subject_name(
    node: ast.AST, result_name: str, alias: str | None
) -> str | None:
    """분기 주어가 `result` · `result.<field>` · call 직후 별칭이면 그 뿌리 이름, 아니면 None."""
    root = _subject_root_name(node)
    if root is None:
        return None
    if isinstance(node, ast.Name):
        if root == result_name or (alias is not None and root == alias):
            return root
        return None
    return root if root == result_name else None


def _direct_type_origin_valid(operation: Operation, node: ast.AST) -> bool | None:
    """Result variant/exception 타입 노드의 own-BC 직접 import 판정 — `Name` 또는
    `<Result>.<Variant>`(단일 top-level result 의 nested variant — #571) 한 단계만 본다."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return _exception_origin_valid(operation, node.value)
    return _exception_origin_valid(operation, node)


def _supported_result_test(
    operation: Operation,
    test: ast.AST,
    result_name: str,
    analysis: list[str],
    alias: str | None = None,
) -> bool:
    # (a) `<subject> is None` · (c)/(d) `<subject> == "<literal>"` — subject 는 result ·
    # result.<field> · call 직후 별칭(2026-08-26 A-1: 규범 «call 직후 직접 branch» 는
    # predicate 형태를 `is None`/`isinstance` 둘로 좁히지 않는다).
    if _result_compare_kind(test) is not None:
        return _result_subject_name(test.left, result_name, alias) is not None
    # (b) `isinstance(result, <DirectOwnBcType>)` — 타입은 Name 또는 `<Result>.<Variant>`.
    if (
        isinstance(test, ast.Call)
        and len(test.args) == 2
        and not test.keywords
        and isinstance(test.args[0], ast.Name)
        and test.args[0].id == result_name
        and isinstance(test.args[1], (ast.Name, ast.Attribute))
    ):
        if not _builtin_isinstance_call(operation, test, analysis):
            return False
        validity = _direct_type_origin_valid(operation, test.args[1])
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


def _result_alias(statement: ast.stmt, result_name: str) -> str | None:
    """call 직후 한 문장의 단순 field 별칭 `outcome = result.<field>` (A-1 (d))."""
    alias = _simple_assignment_target(statement)
    value = _statement_value(statement)
    if (
        alias is None
        or alias == result_name
        or not isinstance(value, ast.Attribute)
        or not isinstance(value.value, ast.Name)
        or value.value.id != result_name
    ):
        return None
    return alias


def _analyze_result_if_chain(
    operation: Operation,
    node: ast.If,
    result_name: str,
    alias: str | None,
    language: ErrorLanguage,
    error_assignments: dict[str, set[int]],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    allowed_error_calls: set[int],
    allowed_status_calls: set[int],
    categories: tuple[str, str],
) -> bool:
    """`if/elif/…` 체인 하나를 Result 직접 branch 로 검사한다.

    모든 arm 의 predicate 가 지원 형태여야 하고, 오류 동작이 있는 arm 은 mapping 본문
    검증을 받는다. 성공 arm 은 success bypass 검사기 소유라 보지 않는다. 승인 predicate
    가 없는 `else` arm 의 오류 mapping 은 «approved arm 소유 아님» 판정(아래 마지막 루프)
    에 맡긴다."""
    current: ast.stmt = node
    while isinstance(current, ast.If):
        if not _supported_result_test(operation, current.test, result_name, analysis, alias):
            analysis.append(
                f"{operation.parsed.relative_path}:{current.lineno} Result candidate predicate 분석 불능"
            )
            return False
        if _branch_has_error_behavior(
            operation, current.body, language, error_assignments, analysis
        ):
            if _result_compare_kind(current.test) != "none":
                _append_finding(
                    findings,
                    seen,
                    operation.parsed,
                    current,
                    RESULT_VARIANT_BRANCH_FORBIDDEN,
                    requires_static_error_shape=True,
                )
            _validate_mapping_body(
                operation,
                current.body,
                language,
                analysis,
                findings,
                seen,
                allowed_error_calls,
                allowed_status_calls,
                *categories,
            )
        orelse = current.orelse
        if len(orelse) == 1 and isinstance(orelse[0], ast.If):
            current = orelse[0]
            continue
        return True
    return True


def _match_exhaustive_wildcard(
    operation: Operation, case: ast.AST, subject_names: set[str]
) -> bool:
    """`case _: assert_never(<subject>)` · `case _ as x: assert_never(x)` — 소진 증명 arm."""
    pattern = case.pattern
    if MATCH_AS is None or not isinstance(pattern, MATCH_AS):
        return False
    # `case _ as x` 는 MatchAs(pattern=MatchAs(_), name="x") 로 중첩 파싱된다.
    inner = pattern.pattern
    if inner is not None and not (
        isinstance(inner, MATCH_AS) and inner.pattern is None and inner.name is None
    ):
        return False
    if case.guard is not None:
        return False
    body = _without_docstrings(case.body)
    if len(body) != 1 or not isinstance(body[0], ast.Expr):
        return False
    call = body[0].value
    if not (
        isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "assert_never"
        and len(call.args) == 1
        and not call.keywords
        and isinstance(call.args[0], ast.Name)
    ):
        return False
    if "assert_never" in operation.local_names:
        return False
    binding = operation.body_bindings.get("assert_never")
    if (
        binding is None
        or binding.kind != "symbol_import"
        or binding.origin not in {"typing.assert_never", "typing_extensions.assert_never"}
    ):
        return False
    expected = {pattern.name} if pattern.name else subject_names
    return call.args[0].id in expected


def _supported_match_pattern(operation: Operation, pattern: ast.AST) -> bool | None:
    """지원 case 패턴 — `"<literal>"` · `None` · `<DirectOwnBcType>()`(하위 패턴 없음).

    None 은 타입 provenance 분석 불능(로컬 섀도잉·재바인딩)."""
    if isinstance(pattern, ast.MatchValue):
        return isinstance(pattern.value, ast.Constant) and isinstance(pattern.value.value, str)
    if isinstance(pattern, ast.MatchSingleton):
        return pattern.value is None
    if isinstance(pattern, ast.MatchClass):
        if pattern.patterns or pattern.kwd_attrs or pattern.kwd_patterns:
            return False
        return _direct_type_origin_valid(operation, pattern.cls)
    return False


def _analyze_result_match(
    operation: Operation,
    node: ast.AST,
    result_name: str,
    alias: str | None,
    language: ErrorLanguage,
    error_assignments: dict[str, set[int]],
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
    allowed_error_calls: set[int],
    allowed_status_calls: set[int],
    categories: tuple[str, str],
) -> bool:
    """`match` 직접 branch(A-1) — subject 는 result · result.<field> · 별칭, case 는
    literal · None · `<DirectOwnBcType>()` 만, 마지막 `case _[ as x]: assert_never(…)` 는
    소진 증명으로 매핑 arm 에 세지 않는다. 형태 밖이면 분석 불능을 적재하고 False."""
    subject_names = {result_name} | ({alias} if alias is not None else set())
    cases = list(node.cases)
    if cases and _match_exhaustive_wildcard(operation, cases[-1], subject_names):
        cases.pop()
    supported = bool(cases)
    for case in cases:
        if case.guard is not None:
            supported = False
            break
        if (
            MATCH_AS is not None
            and isinstance(case.pattern, MATCH_AS)
            and case.pattern.pattern is None
        ):
            # `case _:` / `case x:` — 오류 동작이 없는 성공 arm 만 허용(오류 mapping 은
            # 승인 predicate 가 없어 분석 불능).
            if _branch_has_error_behavior(
                operation, case.body, language, error_assignments, analysis
            ):
                supported = False
                break
            continue
        validity = _supported_match_pattern(operation, case.pattern)
        if validity is None:
            analysis.append(
                f"{operation.parsed.relative_path}:{case.pattern.lineno} Result failure variant provenance 분석 불능"
            )
            return False
        if not validity:
            supported = False
            break
    if not supported:
        analysis.append(
            f"{operation.parsed.relative_path}:{node.lineno} unsupported Result/error match candidate"
        )
        return False
    for case in cases:
        if _branch_has_error_behavior(
            operation, case.body, language, error_assignments, analysis
        ):
            if not isinstance(case.pattern, ast.MatchSingleton):
                _append_finding(
                    findings,
                    seen,
                    operation.parsed,
                    case.pattern,
                    RESULT_VARIANT_BRANCH_FORBIDDEN,
                    requires_static_error_shape=True,
                )
            _validate_mapping_body(
                operation,
                case.body,
                language,
                analysis,
                findings,
                seen,
                allowed_error_calls,
                allowed_status_calls,
                *categories,
            )
    return True


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
    examined_matches: set[int] = set()
    categories = (
        "Result arm must directly construct FrameworkErrorSchema and return Status",
        "Result arm delegates error construction to helper/factory/serializer",
    )

    # 규범 «call 직후 직접 branch»(2026-08-26 A-1): 단일 `if` 한 개가 아니라 call 바로
    # 다음의 연속 `if/elif` 체인 여러 개, 또는 `match` 하나(소진 증명 `case _` 포함)다.
    # 그 사이에 올 수 있는 문장은 `outcome = result.<field>` 별칭 한 줄뿐이다.
    index = 0
    while index < len(body) - 1:
        assignment = _call_assignment(body[index])
        if assignment is None or _known_constructor(
            operation, assignment[1], language, analysis
        ) is not None:
            # A local FrameworkErrorSchema construction is mapping behavior, not the
            # application-call assignment that can causally own a Result arm.
            index += 1
            continue
        result_name, _ = assignment
        cursor = index + 1
        alias = _result_alias(body[cursor], result_name)
        if alias is not None:
            cursor += 1
        while cursor < len(body):
            branch = body[cursor]
            if isinstance(branch, ast.If):
                if not _candidate_branch(
                    operation, branch, language, error_assignments, analysis
                ):
                    break
                test_name = _result_test_name(branch.test)
                if test_name is not None and test_name != result_name and test_name != alias:
                    break
                if not _analyze_result_if_chain(
                    operation,
                    branch,
                    result_name,
                    alias,
                    language,
                    error_assignments,
                    analysis,
                    findings,
                    seen,
                    allowed_error_calls,
                    allowed_status_calls,
                    categories,
                ):
                    break
                approved_branches.add(id(branch))
                cursor += 1
                continue
            if MATCH is not None and isinstance(branch, MATCH):
                if _result_subject_name(branch.subject, result_name, alias) is None:
                    break
                if not _candidate_branch(
                    operation, branch, language, error_assignments, analysis
                ):
                    break
                examined_matches.add(id(branch))
                if _analyze_result_match(
                    operation,
                    branch,
                    result_name,
                    alias,
                    language,
                    error_assignments,
                    analysis,
                    findings,
                    seen,
                    allowed_error_calls,
                    allowed_status_calls,
                    categories,
                ):
                    approved_branches.add(id(branch))
                    cursor += 1
                break
            break
        index = max(cursor, index + 1)

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
                requires_static_error_shape=True,
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
                    requires_static_error_shape=True,
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
            requires_static_error_shape=True,
        )

    for node in _iter_lexical_nodes(operation.node.body):
        if MATCH is not None and isinstance(node, MATCH):
            if id(node) in examined_matches:
                continue
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
                "FrameworkErrorSchema construction is not owned by an approved catch/Result arm",
                requires_static_error_shape=True,
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
                requires_static_error_shape=True,
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
    """Prove one direct FrameworkErrorSchema argument hop into a managed helper.

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
                        truth = _literal_truth(statement.test)
                        if truth is True:
                            error_names = scan_suite(statement.body, error_names)
                        elif truth is False:
                            error_names = scan_suite(statement.orelse, error_names)
                        else:
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
            # 행13(#59 유지) — «전역 예외 핸들러로 가로채지 않는다».
            _append_finding(
                findings,
                seen,
                parsed,
                call,
                "custom Ninja exception_handler forbidden",
                rule="#59",
            )
        elif call.func.attr == "add_exception_handler":
            # 행14(#59 유지) — 행13 동일.
            _append_finding(
                findings,
                seen,
                parsed,
                call,
                "custom Ninja add_exception_handler forbidden",
                rule="#59",
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
                truth = _literal_truth(statement.test)
                if truth is True:
                    error_names = scan_suite(statement.body, error_names)
                elif truth is False:
                    error_names = scan_suite(statement.orelse, error_names)
                else:
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
            # 행15(#126) — «helper·factory 로 옮기지 않는다» 축자.
            _append_finding(
                findings,
                seen,
                parsed,
                function.node,
                "prepared FrameworkErrorSchema factory/helper forbidden",
                rule="#126",
            )
        if facts.serializer_node is not None:
            # 행16(#126) — «serializer 로 옮기지 않는다» 축자(Call node — symbol null).
            _append_finding(
                findings,
                seen,
                parsed,
                facts.serializer_node,
                "FrameworkErrorSchema raw HTTP serializer helper forbidden",
                rule="#126",
            )
        if facts.has_exception_test and facts.has_error_constructor:
            # 행17(#126) — «매핑을 helper 로 옮기지 않는다» 축자.
            _append_finding(
                findings,
                seen,
                parsed,
                function.node,
                "exception-to-FrameworkErrorSchema mapping helper forbidden",
                rule="#126",
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


CONFIG_MUTATION_METHODS = {
    "__init__",
    "__ior__",
    "update",
    "setdefault",
    "pop",
    "popitem",
    "clear",
    "__setitem__",
    "__delitem__",
}


def _schema_contract_mutation_nodes(
    statements: list[ast.stmt],
    *,
    entry_function_ids: set[int] | None = None,
    entry_invocations: dict[int, tuple[dict[str, set[str]], ...]] | None = None,
) -> list[ast.AST]:
    """Find executed FrameworkErrorSchema contract mutation outside the schema owner."""

    config_aliases: set[str] = set()
    config_mutator_aliases: set[str] = set()
    rebuild_aliases: set[str] = set()
    schema_aliases: set[str] = set()
    error_schema_modules: set[str] = set()
    builtin_modules: set[str] = {"builtins"}
    builtin_type_aliases: set[str] = {"type"}
    builtin_dict_aliases: set[str] = {"dict"}
    eager_consumer_aliases: set[str] = {
        "all",
        "any",
        "dict",
        "frozenset",
        "list",
        "max",
        "min",
        "next",
        "set",
        "sorted",
        "sum",
        "tuple",
    }
    operator_modules: set[str] = set()
    operator_mutator_aliases: set[str] = set()
    getattr_aliases: set[str] = {"getattr"}
    setattr_aliases: set[str] = {"setattr"}
    delattr_aliases: set[str] = {"delattr"}
    local_functions: dict[
        str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
    ] = {}
    local_lambdas: dict[str, tuple[ast.Lambda, ...]] = {}
    local_class_methods: dict[
        str,
        dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
    ] = {}
    active_callables: set[int] = set()
    entry_nodes: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    mutations: list[ast.AST] = []
    entry_function_ids = entry_function_ids or set()
    entry_invocations = entry_invocations or {}

    alias_groups = (
        config_aliases,
        config_mutator_aliases,
        rebuild_aliases,
        schema_aliases,
        error_schema_modules,
        builtin_modules,
        builtin_type_aliases,
        builtin_dict_aliases,
        eager_consumer_aliases,
        operator_modules,
        operator_mutator_aliases,
        getattr_aliases,
        setattr_aliases,
        delattr_aliases,
    )

    def literal_attribute_name(node: ast.AST | None) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def canonical_error_module(module: str, *, relative: bool = False) -> bool:
        return module == COMMON_ERROR_MODULE or module.endswith(
            "driving_layer.api.bc_error_schema"
        ) or (relative and module == "bc_error_schema")

    def schema_expression(value: ast.AST | None) -> bool:
        if isinstance(value, ast.Name):
            return value.id in schema_aliases
        if not isinstance(value, ast.Attribute):
            return False
        dotted = _expression_name(value) or ""
        root = dotted.split(".", 1)[0]
        return value.attr.endswith(("ErrorOut", "ErrorSchema", "Error")) and (
            root in error_schema_modules
            or ".driving_layer.api.bc_error_schema." in f".{dotted}."
            or f".{COMMON_ERROR_MODULE}." in f".{dotted}."
        )

    def builtin_module_expression(value: ast.AST | None) -> bool:
        return isinstance(value, ast.Name) and value.id in builtin_modules

    def builtin_type_expression(value: ast.AST | None) -> bool:
        return (
            isinstance(value, ast.Name) and value.id in builtin_type_aliases
        ) or (
            isinstance(value, ast.Attribute)
            and value.attr == "type"
            and builtin_module_expression(value.value)
        )

    def builtin_dict_expression(value: ast.AST | None) -> bool:
        return (
            isinstance(value, ast.Name) and value.id in builtin_dict_aliases
        ) or (
            isinstance(value, ast.Attribute)
            and value.attr == "dict"
            and builtin_module_expression(value.value)
        )

    def eager_consumer_expression(value: ast.AST | None) -> bool:
        return (
            isinstance(value, ast.Name) and value.id in eager_consumer_aliases
        ) or (
            isinstance(value, ast.Attribute)
            and value.attr
            in {
                "all",
                "any",
                "dict",
                "frozenset",
                "list",
                "max",
                "min",
                "next",
                "set",
                "sorted",
                "sum",
                "tuple",
            }
            and builtin_module_expression(value.value)
        )

    def builtin_call_kinds(value: ast.AST | None) -> set[str]:
        if isinstance(value, ast.Name):
            kinds: set[str] = set()
            if value.id in getattr_aliases:
                kinds.add("getattr")
            if value.id in setattr_aliases:
                kinds.add("setattr")
            if value.id in delattr_aliases:
                kinds.add("delattr")
            return kinds
        if not isinstance(value, ast.Attribute):
            return set()
        if (
            builtin_module_expression(value.value)
            and value.attr in {"getattr", "setattr", "delattr"}
        ):
            return {value.attr}
        if builtin_type_expression(value.value) and value.attr in {
            "__setattr__",
            "__delattr__",
        }:
            return {"setattr" if value.attr == "__setattr__" else "delattr"}
        return set()

    def builtin_call_kind(value: ast.AST | None) -> str | None:
        kinds = builtin_call_kinds(value)
        for kind in ("getattr", "setattr", "delattr"):
            if kind in kinds:
                return kind
        return None

    def alias_kind(value: ast.AST | None) -> str | None:
        builtin_kind = builtin_call_kind(value)
        if builtin_kind is not None:
            return builtin_kind
        if isinstance(value, ast.Attribute):
            if value.attr == "model_config" and schema_expression(value.value):
                return "config"
            if value.attr == "model_rebuild" and schema_expression(value.value):
                return "rebuild"
            if (
                value.attr in CONFIG_MUTATION_METHODS
                and alias_kind(value.value) == "config"
            ):
                return "config_mutator"
            if schema_expression(value):
                return "schema"
        if isinstance(value, ast.Name):
            if value.id in config_aliases:
                return "config"
            if value.id in rebuild_aliases:
                return "rebuild"
            if value.id in config_mutator_aliases:
                return "config_mutator"
            if schema_expression(value):
                return "schema"
            return builtin_call_kind(value)
        if isinstance(value, ast.Call) and builtin_call_kind(value.func) == "getattr":
            if len(value.args) < 2:
                return None
            attribute = literal_attribute_name(value.args[1])
            if builtin_module_expression(value.args[0]) and attribute in {
                "getattr",
                "setattr",
                "delattr",
            }:
                return attribute
            if (
                alias_kind(value.args[0]) == "config"
                and attribute in CONFIG_MUTATION_METHODS
            ):
                return "config_mutator"
            if not schema_expression(value.args[0]):
                return None
            if attribute == "model_config":
                return "config"
            if attribute == "model_rebuild":
                return "rebuild"
        if isinstance(value, ast.IfExp):
            truth = _literal_truth(value.test)
            if truth is True:
                return alias_kind(value.body)
            if truth is False:
                return alias_kind(value.orelse)
            kinds = {alias_kind(value.body), alias_kind(value.orelse)} - {None}
            for kind in ("config", "rebuild", "config_mutator", "schema"):
                if kind in kinds:
                    return kind
        if isinstance(value, ast.BoolOp):
            kinds = {alias_kind(item) for item in value.values} - {None}
            for kind in ("config", "rebuild", "config_mutator", "schema"):
                if kind in kinds:
                    return kind
        return None

    def possible_alias_kinds(value: ast.AST | None) -> set[str]:
        if isinstance(value, ast.Name):
            kinds: set[str] = set()
            memberships = (
                (config_aliases, "config"),
                (config_mutator_aliases, "config_mutator"),
                (rebuild_aliases, "rebuild"),
                (schema_aliases, "schema"),
                (getattr_aliases, "getattr"),
                (setattr_aliases, "setattr"),
                (delattr_aliases, "delattr"),
            )
            for aliases, kind in memberships:
                if value.id in aliases:
                    kinds.add(kind)
            return kinds
        if isinstance(value, ast.IfExp):
            truth = _literal_truth(value.test)
            if truth is True:
                return possible_alias_kinds(value.body)
            if truth is False:
                return possible_alias_kinds(value.orelse)
            return possible_alias_kinds(value.body) | possible_alias_kinds(
                value.orelse
            )
        if isinstance(value, ast.BoolOp):
            kinds: set[str] = set()
            for item in value.values:
                kinds.update(possible_alias_kinds(item))
                truth = _literal_truth(item)
                if isinstance(value.op, ast.And) and truth is False:
                    break
                if isinstance(value.op, ast.Or) and truth is True:
                    break
            return kinds
        kind = alias_kind(value)
        return {kind} if kind is not None else set()

    def clear_name(name: str) -> None:
        for aliases in alias_groups:
            aliases.discard(name)
        local_functions.pop(name, None)
        local_lambdas.pop(name, None)
        local_class_methods.pop(name, None)

    def set_name_kind(name: str, kind: str | None) -> None:
        set_name_kinds(name, {kind} if kind is not None else set())

    def set_name_kinds(name: str, kinds: set[str]) -> None:
        clear_name(name)
        targets = {
            "config": config_aliases,
            "config_mutator": config_mutator_aliases,
            "rebuild": rebuild_aliases,
            "schema": schema_aliases,
            "getattr": getattr_aliases,
            "setattr": setattr_aliases,
            "delattr": delattr_aliases,
        }
        for kind in kinds:
            target = targets.get(kind)
            if target is not None:
                target.add(name)

    def bind_kind(target: ast.AST, kind: str | None) -> None:
        if isinstance(target, ast.Name):
            set_name_kind(target.id, kind)
            return
        for name in _target_names(target):
            set_name_kind(name, kind)

    def bind(target: ast.AST, value: ast.AST | None) -> None:
        if (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            for child_target, child_value in zip(target.elts, value.elts):
                bind(child_target, child_value)
            return
        kinds = possible_alias_kinds(value)
        if isinstance(target, ast.Name):
            set_name_kinds(target.id, kinds)
            return
        for name in _target_names(target):
            set_name_kinds(name, kinds)

    def target_mutates(target: ast.AST) -> bool:
        if isinstance(target, ast.Name):
            return False
        return any(
            (
                isinstance(candidate, ast.Attribute)
                and candidate.attr == "model_config"
                and schema_expression(candidate.value)
            )
            or (
                isinstance(candidate, ast.Name)
                and candidate.id in config_aliases
            )
            for candidate in ast.walk(target)
        )

    def alias_state() -> tuple[set[str], ...]:
        return tuple(values.copy() for values in alias_groups)

    def restore_alias_state(snapshot: tuple[set[str], ...]) -> None:
        for values, saved in zip(alias_groups, snapshot):
            values.clear()
            values.update(saved)

    def merged_alias_state(
        snapshots: list[tuple[set[str], ...]],
    ) -> tuple[set[str], ...]:
        return tuple(
            set().union(*(snapshot[index] for snapshot in snapshots))
            for index in range(len(alias_groups))
        )

    def scope_state() -> tuple[
        tuple[set[str], ...],
        dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
        dict[str, tuple[ast.Lambda, ...]],
        dict[
            str,
            dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
        ],
    ]:
        return (
            alias_state(),
            local_functions.copy(),
            local_lambdas.copy(),
            {name: methods.copy() for name, methods in local_class_methods.items()},
        )

    def restore_scope_state(
        snapshot: tuple[
            tuple[set[str], ...],
            dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
            dict[str, tuple[ast.Lambda, ...]],
            dict[
                str,
                dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
            ],
        ],
    ) -> None:
        aliases, functions, lambdas, classes = snapshot
        restore_alias_state(aliases)
        local_functions.clear()
        local_functions.update(functions)
        local_lambdas.clear()
        local_lambdas.update(lambdas)
        local_class_methods.clear()
        local_class_methods.update(classes)

    def merge_scope_states(
        snapshots: list[
            tuple[
                tuple[set[str], ...],
                dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
                dict[str, tuple[ast.Lambda, ...]],
                dict[
                    str,
                    dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
                ],
            ]
        ],
    ) -> None:
        restore_alias_state(merged_alias_state([item[0] for item in snapshots]))
        local_functions.clear()
        local_lambdas.clear()
        local_class_methods.clear()
        for _, functions, lambdas, classes in snapshots:
            for name, candidates in functions.items():
                current = local_functions.get(name, ())
                local_functions[name] = tuple(
                    dict.fromkeys((*current, *candidates))
                )
            for name, candidates in lambdas.items():
                current = local_lambdas.get(name, ())
                local_lambdas[name] = tuple(
                    dict.fromkeys((*current, *candidates))
                )
            for class_name, methods in classes.items():
                current_methods = local_class_methods.setdefault(class_name, {})
                for method_name, candidates in methods.items():
                    current = current_methods.get(method_name, ())
                    current_methods[method_name] = tuple(
                        dict.fromkeys((*current, *candidates))
                    )

    def iterable_kind(value: ast.AST | None) -> str | None:
        if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
            kinds = {alias_kind(item) for item in value.elts} - {None}
            for kind in ("config", "rebuild", "config_mutator", "schema"):
                if kind in kinds:
                    return kind
        return alias_kind(value)

    def literal_iteration(value: ast.AST) -> bool | None:
        try:
            literal = ast.literal_eval(value)
        except (SyntaxError, ValueError, TypeError):
            return None
        if isinstance(
            literal,
            (tuple, list, set, frozenset, dict, str, bytes),
        ):
            return bool(literal)
        return None

    def call_mutates(call: ast.Call) -> bool:
        builtin_kinds = builtin_call_kinds(call.func)
        if builtin_kinds & {"setattr", "delattr"}:
            return (
                len(call.args) >= 2
                and schema_expression(call.args[0])
                and literal_attribute_name(call.args[1])
                in {"model_config", "model_rebuild"}
            )
        if isinstance(call.func, ast.Name):
            if call.func.id in operator_mutator_aliases:
                return bool(call.args) and alias_kind(call.args[0]) == "config"
            return (
                call.func.id in rebuild_aliases
                or call.func.id in config_mutator_aliases
            )
        if not isinstance(call.func, ast.Attribute):
            return False
        if call.func.attr == "model_rebuild" and schema_expression(call.func.value):
            return True
        if (
            builtin_dict_expression(call.func.value)
            and call.func.attr in CONFIG_MUTATION_METHODS
        ):
            return bool(call.args) and alias_kind(call.args[0]) == "config"
        if (
            isinstance(call.func.value, ast.Name)
            and call.func.value.id in operator_modules
            and call.func.attr in {"setitem", "delitem", "ior"}
        ):
            return bool(call.args) and alias_kind(call.args[0]) == "config"
        return (
            call.func.attr in CONFIG_MUTATION_METHODS
            and alias_kind(call.func.value) == "config"
        )

    def argument_kinds(
        arguments: ast.arguments,
        call: ast.Call | None,
    ) -> dict[str, set[str]]:
        positional = [*arguments.posonlyargs, *arguments.args]
        result: dict[str, set[str]] = {}
        default_offset = len(positional) - len(arguments.defaults)
        for index, default in enumerate(arguments.defaults, default_offset):
            result[positional[index].arg] = possible_alias_kinds(default)
        for parameter, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
            if default is not None:
                result[parameter.arg] = possible_alias_kinds(default)
        if call is None:
            return result
        expanded_args: list[ast.AST] = []
        for value in call.args:
            if isinstance(value, ast.Starred) and isinstance(
                value.value, (ast.Tuple, ast.List)
            ):
                expanded_args.extend(value.value.elts)
            else:
                expanded_args.append(value)
        for parameter, value in zip(positional, expanded_args):
            result[parameter.arg] = possible_alias_kinds(value)
        known = {parameter.arg for parameter in [*positional, *arguments.kwonlyargs]}
        for keyword in call.keywords:
            if keyword.arg in known:
                result[keyword.arg] = possible_alias_kinds(keyword.value)
        return result

    def invoke_function(
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        call: ast.Call | None,
        supplied_bindings: dict[str, set[str]] | None = None,
    ) -> None:
        if id(function) in active_callables:
            return
        bindings = argument_kinds(function.args, call)
        if supplied_bindings is not None:
            bindings.update(supplied_bindings)
        snapshot = scope_state()
        active_callables.add(id(function))
        try:
            for name in _function_local_names(function):
                clear_name(name)
            for name, kinds in bindings.items():
                set_name_kinds(name, kinds)
            scan_suite(function.body)
        finally:
            active_callables.discard(id(function))
            restore_scope_state(snapshot)

    def invoke_lambda(function: ast.Lambda, call: ast.Call) -> None:
        if id(function) in active_callables:
            return
        bindings = argument_kinds(function.args, call)
        snapshot = scope_state()
        active_callables.add(id(function))
        try:
            for parameter in [
                *function.args.posonlyargs,
                *function.args.args,
                *function.args.kwonlyargs,
            ]:
                clear_name(parameter.arg)
            for name, kinds in bindings.items():
                set_name_kinds(name, kinds)
            process_expression(function.body)
        finally:
            active_callables.discard(id(function))
            restore_scope_state(snapshot)

    def process_call(call: ast.Call) -> None:
        if call_mutates(call):
            mutations.append(call)
        if isinstance(call.func, ast.Lambda):
            invoke_lambda(call.func, call)
        elif isinstance(call.func, ast.Name):
            for function in local_functions.get(call.func.id, ()):
                invoke_function(function, call)
            for lambda_ in local_lambdas.get(call.func.id, ()):
                invoke_lambda(lambda_, call)
        elif (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
        ):
            methods = local_class_methods.get(call.func.value.id, {})
            for function in methods.get(call.func.attr, ()):
                invoke_function(function, call)

    def process_comprehension(
        generators: list[ast.comprehension],
        values: list[ast.AST],
    ) -> None:
        snapshot = scope_state()
        try:
            for generator in generators:
                process_expression(generator.iter)
                if literal_iteration(generator.iter) is False:
                    return
                bind_kind(generator.target, iterable_kind(generator.iter))
                for condition in generator.ifs:
                    process_expression(condition)
                    if _literal_truth(condition) is False:
                        return
            for value in values:
                process_expression(value)
        finally:
            restore_scope_state(snapshot)

    def process_expression(node: ast.AST | None) -> None:
        if node is None:
            return
        if isinstance(node, ast.Lambda):
            for expression in _definition_expressions(node):
                process_expression(expression)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp)):
            process_comprehension(node.generators, [node.elt])
            return
        if isinstance(node, ast.DictComp):
            process_comprehension(node.generators, [node.key, node.value])
            return
        if isinstance(node, ast.GeneratorExp):
            # Its body is deferred. Only the first iterable is evaluated now.
            if node.generators:
                process_expression(node.generators[0].iter)
            return
        if isinstance(node, ast.Starred) and isinstance(node.value, ast.GeneratorExp):
            process_comprehension(node.value.generators, [node.value.elt])
            return
        if isinstance(node, ast.NamedExpr):
            process_expression(node.value)
            if target_mutates(node.target):
                mutations.append(node)
            bind(node.target, node.value)
            return
        if isinstance(node, ast.IfExp):
            process_expression(node.test)
            truth = _literal_truth(node.test)
            if truth is True:
                process_expression(node.body)
            elif truth is False:
                process_expression(node.orelse)
            else:
                process_expression(node.body)
                process_expression(node.orelse)
            return
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                process_expression(value)
                truth = _literal_truth(value)
                if isinstance(node.op, ast.And) and truth is False:
                    break
                if isinstance(node.op, ast.Or) and truth is True:
                    break
            return
        if isinstance(node, ast.Call):
            process_expression(node.func)
            for argument in node.args:
                if isinstance(argument, ast.GeneratorExp) and eager_consumer_expression(
                    node.func
                ):
                    process_comprehension(argument.generators, [argument.elt])
                else:
                    process_expression(argument)
            for keyword in node.keywords:
                process_expression(keyword.value)
            process_call(node)
            return
        for child in ast.iter_child_nodes(node):
            process_expression(child)

    def scan_branches(
        branches: list[list[ast.stmt]],
        *,
        include_baseline: bool = False,
    ) -> None:
        baseline = scope_state()
        outcomes = [baseline] if include_baseline else []
        for branch in branches:
            restore_scope_state(baseline)
            scan_suite(branch)
            outcomes.append(scope_state())
        merge_scope_states(outcomes)

    def callable_candidates(
        value: ast.AST | None,
    ) -> tuple[
        tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...],
        tuple[ast.Lambda, ...],
    ]:
        if isinstance(value, ast.Lambda):
            return (), (value,)
        if isinstance(value, ast.Name):
            return (
                local_functions.get(value.id, ()),
                local_lambdas.get(value.id, ()),
            )
        if (
            isinstance(value, ast.Attribute)
            and isinstance(value.value, ast.Name)
        ):
            methods = local_class_methods.get(value.value.id, {})
            return methods.get(value.attr, ()), ()
        if isinstance(value, ast.IfExp):
            truth = _literal_truth(value.test)
            choices = (
                [value.body]
                if truth is True
                else [value.orelse]
                if truth is False
                else [value.body, value.orelse]
            )
        elif isinstance(value, ast.BoolOp):
            choices = list(value.values)
        else:
            return (), ()
        functions: tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...] = ()
        lambdas: tuple[ast.Lambda, ...] = ()
        for choice in choices:
            child_functions, child_lambdas = callable_candidates(choice)
            functions = tuple(dict.fromkeys((*functions, *child_functions)))
            lambdas = tuple(dict.fromkeys((*lambdas, *child_lambdas)))
        return functions, lambdas

    def class_candidates(
        value: ast.AST | None,
    ) -> dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]]:
        if isinstance(value, ast.Name):
            return local_class_methods.get(value.id, {})
        if isinstance(value, ast.IfExp):
            truth = _literal_truth(value.test)
            choices = (
                [value.body]
                if truth is True
                else [value.orelse]
                if truth is False
                else [value.body, value.orelse]
            )
        elif isinstance(value, ast.BoolOp):
            choices = list(value.values)
        else:
            return {}
        methods: dict[
            str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
        ] = {}
        for choice in choices:
            for name, candidates in class_candidates(choice).items():
                current = methods.get(name, ())
                methods[name] = tuple(dict.fromkeys((*current, *candidates)))
        return methods

    def callable_assignment_bindings(
        target: ast.AST,
        value: ast.AST | None,
    ) -> tuple[
        dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
        dict[str, tuple[ast.Lambda, ...]],
    ]:
        functions: dict[
            str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
        ] = {}
        lambdas: dict[str, tuple[ast.Lambda, ...]] = {}
        if isinstance(target, ast.Name):
            function_candidates, lambda_candidates = callable_candidates(value)
            if function_candidates:
                functions[target.id] = function_candidates
            if lambda_candidates:
                lambdas[target.id] = lambda_candidates
        elif (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            for child_target, child_value in zip(target.elts, value.elts):
                child_functions, child_lambdas = callable_assignment_bindings(
                    child_target,
                    child_value,
                )
                functions.update(child_functions)
                lambdas.update(child_lambdas)
        return functions, lambdas

    def class_assignment_bindings(
        target: ast.AST,
        value: ast.AST | None,
    ) -> dict[
        str,
        dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
    ]:
        if isinstance(target, ast.Name):
            candidates = class_candidates(value)
            return {target.id: candidates} if candidates else {}
        if (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            result: dict[
                str,
                dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
            ] = {}
            for child_target, child_value in zip(target.elts, value.elts):
                result.update(class_assignment_bindings(child_target, child_value))
            return result
        return {}

    def literal_only(node: ast.AST | None) -> bool:
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return all(literal_only(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return all(
                (key is None or literal_only(key)) and literal_only(value)
                for key, value in zip(node.keys, node.values)
            )
        return False

    def statement_may_raise(statement: ast.stmt) -> bool:
        if isinstance(statement, (ast.Pass, ast.Global, ast.Nonlocal)):
            return False
        if isinstance(statement, ast.Expr):
            return not literal_only(statement.value)
        if isinstance(statement, ast.Assign):
            return not literal_only(statement.value)
        if isinstance(statement, ast.AnnAssign):
            return statement.value is not None and not literal_only(statement.value)
        return True

    def pattern_matches(pattern: ast.AST, value: object) -> bool | None:
        if MATCH_AS is not None and isinstance(pattern, MATCH_AS):
            if pattern.pattern is None:
                return True
            return pattern_matches(pattern.pattern, value)
        if isinstance(pattern, ast.MatchValue):
            try:
                expected = ast.literal_eval(pattern.value)
            except (SyntaxError, ValueError, TypeError):
                return None
            return expected == value
        if isinstance(pattern, ast.MatchSingleton):
            return pattern.value is value
        if isinstance(pattern, ast.MatchOr):
            results = [pattern_matches(item, value) for item in pattern.patterns]
            if True in results:
                return True
            if all(result is False for result in results):
                return False
        return None

    def statement_controls(statement: ast.stmt) -> set[str]:
        if isinstance(statement, ast.Return):
            return {"return"}
        if isinstance(statement, ast.Raise):
            return {"raise"}
        if isinstance(statement, ast.Break):
            return {"break"}
        if isinstance(statement, ast.Continue):
            return {"continue"}
        if isinstance(statement, ast.If):
            truth = _literal_truth(statement.test)
            if truth is True:
                return suite_controls(statement.body)
            if truth is False:
                return suite_controls(statement.orelse)
            return suite_controls(statement.body) | suite_controls(
                statement.orelse
            )
        return {"normal"}

    def suite_controls(statements: list[ast.stmt]) -> set[str]:
        outcomes = {"normal"}
        for statement in statements:
            if "normal" not in outcomes:
                break
            outcomes.remove("normal")
            outcomes.update(statement_controls(statement))
        return outcomes

    def scan_statement(node: ast.stmt) -> None:
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname or alias.name
                clear_name(local)
                if module == "builtins":
                    if alias.name == "getattr":
                        getattr_aliases.add(local)
                    elif alias.name == "setattr":
                        setattr_aliases.add(local)
                    elif alias.name == "delattr":
                        delattr_aliases.add(local)
                    elif alias.name == "type":
                        builtin_type_aliases.add(local)
                    elif alias.name == "dict":
                        builtin_dict_aliases.add(local)
                    if alias.name in {
                        "all",
                        "any",
                        "dict",
                        "frozenset",
                        "list",
                        "max",
                        "min",
                        "next",
                        "set",
                        "sorted",
                        "sum",
                        "tuple",
                    }:
                        eager_consumer_aliases.add(local)
                elif module == "operator" and alias.name in {
                    "setitem",
                    "delitem",
                    "ior",
                }:
                    operator_mutator_aliases.add(local)
                if canonical_error_module(
                    module,
                    relative=node.level > 0,
                ) and alias.name.endswith(
                    ("ErrorOut", "ErrorSchema", "Error")
                ):
                    schema_aliases.add(local)
                if (
                    alias.name == "bc_error_schema"
                    and (module.endswith("driving_layer.api") or (node.level > 0 and not module))
                ) or (alias.name == COMMON_ERROR_BASENAME and module == COMMON_ERROR_PACKAGE):
                    error_schema_modules.add(local)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                clear_name(local)
                if alias.name == "builtins":
                    builtin_modules.add(local)
                elif alias.name == "operator":
                    operator_modules.add(local)
                if canonical_error_module(alias.name):
                    error_schema_modules.add(local)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for expression in _definition_expressions(node):
                process_expression(expression)
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    for function in local_functions.get(decorator.id, ()):
                        invoke_function(function, None)
                    for lambda_ in local_lambdas.get(decorator.id, ()):
                        synthetic = ast.Call(
                            func=decorator,
                            args=[],
                            keywords=[],
                        )
                        ast.copy_location(synthetic, decorator)
                        invoke_lambda(lambda_, synthetic)
                elif (
                    isinstance(decorator, ast.Attribute)
                    and isinstance(decorator.value, ast.Name)
                ):
                    methods = local_class_methods.get(decorator.value.id, {})
                    for function in methods.get(decorator.attr, ()):
                        invoke_function(function, None)
            clear_name(node.name)
            local_functions[node.name] = (node,)
            if id(node) in entry_function_ids or id(node) in entry_invocations:
                entry_nodes.append(node)
            return
        if isinstance(node, ast.ClassDef):
            for expression in _definition_expressions(node):
                process_expression(expression)
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    for function in local_functions.get(decorator.id, ()):
                        invoke_function(function, None)
                    for lambda_ in local_lambdas.get(decorator.id, ()):
                        synthetic = ast.Call(
                            func=decorator,
                            args=[],
                            keywords=[],
                        )
                        ast.copy_location(synthetic, decorator)
                        invoke_lambda(lambda_, synthetic)
                elif (
                    isinstance(decorator, ast.Attribute)
                    and isinstance(decorator.value, ast.Name)
                ):
                    methods = local_class_methods.get(decorator.value.id, {})
                    for function in methods.get(decorator.attr, ()):
                        invoke_function(function, None)
            clear_name(node.name)
            snapshot = scope_state()
            try:
                scan_suite(node.body)
            finally:
                restore_scope_state(snapshot)
            methods: dict[
                str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
            ] = {}
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods[member.name] = (member,)
            local_class_methods[node.name] = methods
            return
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.GeneratorExp) and any(
                any(isinstance(candidate, ast.Starred) for candidate in ast.walk(target))
                for target in node.targets
            ):
                process_comprehension(node.value.generators, [node.value.elt])
            process_expression(node.value)
            if any(target_mutates(target) for target in node.targets):
                mutations.append(node)
            for target in node.targets:
                function_bindings, lambda_bindings = callable_assignment_bindings(
                    target,
                    node.value,
                )
                class_bindings = class_assignment_bindings(target, node.value)
                bind(target, node.value)
                local_functions.update(function_bindings)
                local_lambdas.update(lambda_bindings)
                local_class_methods.update(class_bindings)
            return
        if isinstance(node, ast.AnnAssign):
            process_expression(node.annotation)
            process_expression(node.value)
            if target_mutates(node.target):
                mutations.append(node)
            function_bindings, lambda_bindings = callable_assignment_bindings(
                node.target,
                node.value,
            )
            class_bindings = class_assignment_bindings(node.target, node.value)
            bind(node.target, node.value)
            local_functions.update(function_bindings)
            local_lambdas.update(lambda_bindings)
            local_class_methods.update(class_bindings)
            return
        if isinstance(node, ast.AugAssign):
            process_expression(node.value)
            if (
                isinstance(node.target, ast.Name)
                and node.target.id in config_aliases
            ) or target_mutates(node.target):
                mutations.append(node)
            return
        if isinstance(node, ast.Delete):
            for target in node.targets:
                if target_mutates(target):
                    mutations.append(node)
                else:
                    for name in _target_names(target):
                        clear_name(name)
            return
        if isinstance(node, ast.If):
            process_expression(node.test)
            truth = _literal_truth(node.test)
            if truth is True:
                scan_suite(node.body)
            elif truth is False:
                scan_suite(node.orelse)
            else:
                scan_branches([node.body, node.orelse])
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            if isinstance(node.iter, ast.GeneratorExp):
                process_comprehension(node.iter.generators, [node.iter.elt])
            else:
                process_expression(node.iter)
            iteration = literal_iteration(node.iter)
            if iteration is False:
                scan_suite(node.orelse)
                return
            baseline = scope_state()
            bind_kind(node.target, iterable_kind(node.iter))
            scan_suite(node.body)
            body_state = scope_state()
            controls = suite_controls(node.body)
            outcomes = []
            if iteration is None:
                restore_scope_state(baseline)
                scan_suite(node.orelse)
                outcomes.append(scope_state())
            if "break" in controls:
                outcomes.append(body_state)
            if controls & {"normal", "continue"}:
                restore_scope_state(body_state)
                scan_suite(node.orelse)
                outcomes.append(scope_state())
            if outcomes:
                merge_scope_states(outcomes)
            else:
                restore_scope_state(body_state)
            return
        if isinstance(node, ast.While):
            process_expression(node.test)
            truth = _literal_truth(node.test)
            if truth is True:
                scan_suite(node.body)
            elif truth is False:
                scan_suite(node.orelse)
            else:
                scan_branches([node.body, node.orelse], include_baseline=True)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                process_expression(item.context_expr)
                if item.optional_vars is not None:
                    bind(item.optional_vars, item.context_expr)
            scan_suite(node.body)
            return
        if isinstance(node, (ast.Try, TRY_STAR or ast.Try)):
            baseline = scope_state()
            outcomes: list[
                tuple[
                    tuple[set[str], ...],
                    dict[str, tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]],
                    dict[str, tuple[ast.Lambda, ...]],
                    dict[
                        str,
                        dict[
                            str,
                            tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...],
                        ],
                    ],
                ]
            ] = []
            prefix_states = []
            body_completed = True
            for statement in node.body:
                if statement_may_raise(statement):
                    prefix_states.append(scope_state())
                scan_statement(statement)
                if isinstance(
                    statement,
                    (ast.Return, ast.Raise, ast.Break, ast.Continue),
                ):
                    body_completed = False
                    break
            body_state = scope_state()
            if body_completed:
                scan_suite(node.orelse)
                outcomes.append(scope_state())
            for handler in node.handlers:
                for prefix_state in prefix_states:
                    restore_scope_state(prefix_state)
                    process_expression(handler.type)
                    if handler.name:
                        clear_name(handler.name)
                    scan_suite(handler.body)
                    outcomes.append(scope_state())
            if outcomes:
                merge_scope_states(outcomes)
            else:
                restore_scope_state(body_state)
            scan_suite(node.finalbody)
            return
        if MATCH is not None and isinstance(node, MATCH):
            process_expression(node.subject)
            baseline = scope_state()
            outcomes = []
            exhaustive = False
            try:
                subject = ast.literal_eval(node.subject)
            except (SyntaxError, ValueError, TypeError):
                subject = _NO_STATIC_VALUE
            for case in node.cases:
                match = (
                    pattern_matches(case.pattern, subject)
                    if subject is not _NO_STATIC_VALUE
                    else (
                        True
                        if MATCH_AS is not None
                        and isinstance(case.pattern, MATCH_AS)
                        and case.pattern.pattern is None
                        else None
                    )
                )
                guard_truth = (
                    True if case.guard is None else _literal_truth(case.guard)
                )
                if match is False or guard_truth is False:
                    continue
                restore_scope_state(baseline)
                for candidate in ast.walk(case.pattern):
                    if (
                        MATCH_AS is not None
                        and isinstance(candidate, MATCH_AS)
                        and candidate.name
                    ):
                        clear_name(candidate.name)
                    elif (
                        MATCH_STAR is not None
                        and isinstance(candidate, MATCH_STAR)
                        and candidate.name
                    ):
                        clear_name(candidate.name)
                    elif (
                        MATCH_MAPPING is not None
                        and isinstance(candidate, MATCH_MAPPING)
                        and candidate.rest
                    ):
                        clear_name(candidate.rest)
                if match is True and guard_truth is True:
                    exhaustive = True
                process_expression(case.guard)
                scan_suite(case.body)
                outcomes.append(scope_state())
                if exhaustive:
                    break
            if not exhaustive:
                outcomes.append(baseline)
            merge_scope_states(outcomes)
            return
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                process_expression(child)

    def statement_definitely_terminates(statement: ast.stmt) -> bool:
        if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
            return True
        if isinstance(statement, ast.If):
            truth = _literal_truth(statement.test)
            if truth is True:
                return suite_definitely_terminates(statement.body)
            if truth is False:
                return suite_definitely_terminates(statement.orelse)
            return bool(statement.orelse) and suite_definitely_terminates(
                statement.body
            ) and suite_definitely_terminates(statement.orelse)
        if isinstance(statement, (ast.Try, TRY_STAR or ast.Try)):
            if suite_definitely_terminates(statement.finalbody):
                return True
            return suite_definitely_terminates(statement.body) and all(
                suite_definitely_terminates(handler.body)
                for handler in statement.handlers
            )
        return False

    def suite_definitely_terminates(suite: list[ast.stmt]) -> bool:
        return any(statement_definitely_terminates(statement) for statement in suite)

    def scan_suite(suite: list[ast.stmt]) -> bool:
        for statement in suite:
            scan_statement(statement)
            if statement_definitely_terminates(statement):
                return False
        return True

    scan_suite(statements)
    for entry in dict.fromkeys(entry_nodes):
        invocations = entry_invocations.get(id(entry))
        if invocations is None:
            invoke_function(entry, None)
        else:
            for bindings in invocations:
                invoke_function(entry, None, bindings)
    return mutations


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


def _direct_external_entry_invocations(
    parsed: dict[Path, ParsedSource],
    caller_paths: set[Path],
    target_paths: set[Path],
    operations_by_path: dict[Path, list[Operation]],
) -> dict[Path, dict[int, tuple[dict[str, set[str]], ...]]]:
    """Link actually reachable direct calls to selected one-hop functions."""

    targets: dict[str, tuple[Path, ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    for path in target_paths:
        source = parsed.get(path)
        if source is None:
            continue
        module = _module_name(path)
        for statement in source.tree.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                targets[f"{module}.{statement.name}"] = (path, statement)

    entries: dict[Path, dict[int, list[dict[str, set[str]]]]] = {}

    CandidateState = dict[str, frozenset[Binding]]

    def expression_candidates(
        node: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> frozenset[Binding]:
        if isinstance(node, ast.Name):
            if node.id in candidates:
                return candidates[node.id]
            binding = bindings.get(node.id)
            return frozenset({binding}) if binding is not None else frozenset()
        if isinstance(node, ast.Attribute):
            return frozenset(
                Binding(f"{binding.origin}.{node.attr}", binding.kind)
                for binding in expression_candidates(node.value, bindings, candidates)
            )
        if isinstance(node, ast.IfExp):
            truth = _literal_truth(node.test)
            if truth is True:
                return expression_candidates(node.body, bindings, candidates)
            if truth is False:
                return expression_candidates(node.orelse, bindings, candidates)
            return expression_candidates(
                node.body, bindings, candidates
            ) | expression_candidates(node.orelse, bindings, candidates)
        if isinstance(node, ast.BoolOp):
            possible: frozenset[Binding] = frozenset()
            for value in node.values:
                possible |= expression_candidates(value, bindings, candidates)
                truth = _literal_truth(value)
                if isinstance(node.op, ast.And) and truth is False:
                    break
                if isinstance(node.op, ast.Or) and truth is True:
                    break
            return possible
        resolved = _resolve_binding(node, bindings)
        return frozenset({resolved}) if resolved is not None else frozenset()

    def expression_kinds(
        node: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> set[str]:
        kinds: set[str] = set()
        for resolved in expression_candidates(node, bindings, candidates):
            origin = resolved.origin
            canonical = (
                ".driving_layer.api.bc_error_schema." in f".{origin}."
                or f".{COMMON_ERROR_MODULE}." in f".{origin}."
            )
            if canonical and origin.endswith(".model_config"):
                kinds.add("config")
            elif canonical and origin.endswith(".model_rebuild"):
                kinds.add("rebuild")
            elif canonical and origin.rsplit(".", 1)[-1].endswith(
                ("ErrorOut", "ErrorSchema", "Error")
            ):
                kinds.add("schema")
        return kinds

    def iterable_candidates(
        node: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> frozenset[Binding]:
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            possible: frozenset[Binding] = frozenset()
            for item in node.elts:
                possible |= expression_candidates(item, bindings, candidates)
            return possible
        return expression_candidates(node, bindings, candidates)

    def bind_runtime_names(
        target: ast.AST,
        possible: frozenset[Binding],
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        useful = frozenset(
            binding
            for binding in possible
            if binding not in {VALUE_BINDING, AMBIGUOUS_BINDING}
            and binding.kind != "static_literal"
        )
        for name in _target_names(target):
            if len(useful) == 1:
                bindings[name] = next(iter(useful))
            elif useful:
                bindings[name] = VALUE_BINDING
            else:
                bindings.pop(name, None)
            if useful:
                candidates[name] = useful
            else:
                candidates.pop(name, None)

    def invocation_bindings(
        function: ast.FunctionDef | ast.AsyncFunctionDef,
        call: ast.Call,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> dict[str, set[str]]:
        positional = [*function.args.posonlyargs, *function.args.args]
        values: list[ast.AST] = []
        for value in call.args:
            if isinstance(value, ast.Starred) and isinstance(
                value.value, (ast.Tuple, ast.List)
            ):
                values.extend(value.value.elts)
            else:
                values.append(value)
        result = {
            parameter.arg: expression_kinds(value, bindings, candidates)
            for parameter, value in zip(positional, values)
        }
        known = {parameter.arg for parameter in [*positional, *function.args.kwonlyargs]}
        for keyword in call.keywords:
            if keyword.arg in known:
                result[keyword.arg] = expression_kinds(
                    keyword.value, bindings, candidates
                )
        return result

    def record_call(
        call: ast.Call,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        for resolved in expression_candidates(call.func, bindings, candidates):
            target = targets.get(resolved.origin)
            if target is None:
                continue
            path, function = target
            entries.setdefault(path, {}).setdefault(id(function), []).append(
                invocation_bindings(function, call, bindings, candidates)
            )

    def record_implicit_decorator_call(
        decorator: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        if isinstance(decorator, ast.Call):
            return
        for resolved in expression_candidates(decorator, bindings, candidates):
            target = targets.get(resolved.origin)
            if target is None:
                continue
            path, function = target
            entries.setdefault(path, {}).setdefault(id(function), []).append({})

    def eager_consumer(
        node: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> bool:
        names = {
            "all",
            "any",
            "dict",
            "frozenset",
            "list",
            "max",
            "min",
            "next",
            "set",
            "sorted",
            "sum",
            "tuple",
        }
        if isinstance(node, ast.Name) and node.id in names:
            possible = expression_candidates(node, bindings, candidates)
            return not possible or any(
                binding.origin == f"builtins.{node.id}" for binding in possible
            )
        return isinstance(node, ast.Attribute) and node.attr in names and any(
            binding.origin == "builtins"
            for binding in expression_candidates(node.value, bindings, candidates)
        )

    def inspect_comprehension(
        generators: list[ast.comprehension],
        values: list[ast.AST],
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        local_bindings = dict(bindings)
        local_candidates = dict(candidates)
        for generator in generators:
            inspect_expression(
                generator.iter,
                local_bindings,
                local_candidates,
                consume_generator=True,
            )
            if literal_iteration(generator.iter) is False:
                return
            bind_runtime_names(
                generator.target,
                iterable_candidates(
                    generator.iter, local_bindings, local_candidates
                ),
                local_bindings,
                local_candidates,
            )
            for condition in generator.ifs:
                inspect_expression(condition, local_bindings, local_candidates)
                if _literal_truth(condition) is False:
                    return
        for value in values:
            inspect_expression(value, local_bindings, local_candidates)

    def inspect_expression(
        node: ast.AST,
        bindings: dict[str, Binding],
        candidates: CandidateState,
        *,
        consume_generator: bool = False,
    ) -> None:
        if isinstance(node, ast.Lambda):
            for expression in _definition_expressions(node):
                inspect_expression(expression, bindings, candidates)
            return
        if isinstance(node, ast.GeneratorExp):
            if consume_generator:
                inspect_comprehension(
                    node.generators, [node.elt], bindings, candidates
                )
            elif node.generators:
                inspect_expression(node.generators[0].iter, bindings, candidates)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp)):
            inspect_comprehension(node.generators, [node.elt], bindings, candidates)
            return
        if isinstance(node, ast.DictComp):
            inspect_comprehension(
                node.generators, [node.key, node.value], bindings, candidates
            )
            return
        if isinstance(node, ast.Starred):
            inspect_expression(
                node.value,
                bindings,
                candidates,
                consume_generator=isinstance(node.value, ast.GeneratorExp),
            )
            return
        if isinstance(node, ast.NamedExpr):
            inspect_expression(node.value, bindings, candidates)
            bind_runtime_names(
                node.target,
                expression_candidates(node.value, bindings, candidates),
                bindings,
                candidates,
            )
            return
        if isinstance(node, ast.IfExp):
            inspect_expression(node.test, bindings, candidates)
            truth = _literal_truth(node.test)
            if truth is True:
                inspect_expression(node.body, bindings, candidates)
            elif truth is False:
                inspect_expression(node.orelse, bindings, candidates)
            else:
                inspect_expression(node.body, bindings, candidates)
                inspect_expression(node.orelse, bindings, candidates)
            return
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                inspect_expression(value, bindings, candidates)
                truth = _literal_truth(value)
                if isinstance(node.op, ast.And) and truth is False:
                    break
                if isinstance(node.op, ast.Or) and truth is True:
                    break
            return
        if isinstance(node, ast.Call):
            direct_generator_consumer = (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"__next__", "send"}
                and isinstance(node.func.value, ast.GeneratorExp)
            )
            if direct_generator_consumer:
                inspect_expression(
                    node.func.value,
                    bindings,
                    candidates,
                    consume_generator=True,
                )
            else:
                inspect_expression(node.func, bindings, candidates)
            consumes = eager_consumer(node.func, bindings, candidates)
            for argument in node.args:
                inspect_expression(
                    argument,
                    bindings,
                    candidates,
                    consume_generator=consumes
                    and isinstance(argument, ast.GeneratorExp),
                )
            for keyword in node.keywords:
                inspect_expression(keyword.value, bindings, candidates)
            record_call(node, bindings, candidates)
            return
        for child in ast.iter_child_nodes(node):
            inspect_expression(child, bindings, candidates)

    def literal_iteration(node: ast.AST) -> bool | None:
        try:
            value = ast.literal_eval(node)
        except (SyntaxError, ValueError, TypeError):
            return None
        if isinstance(value, (tuple, list, set, frozenset, dict, str, bytes)):
            return bool(value)
        return None

    def merge_states(
        states: list[tuple[dict[str, Binding], CandidateState]],
    ) -> tuple[dict[str, Binding], CandidateState]:
        if not states:
            return {}, {}
        joined_bindings = _join_binding_states([state[0] for state in states])
        joined_candidates: CandidateState = {}
        names = {
            name
            for bindings, possibilities in states
            for name in {*bindings, *possibilities}
        }
        for name in names:
            possible: frozenset[Binding] = frozenset()
            for bindings, possibilities in states:
                if name in possibilities:
                    possible |= possibilities[name]
                elif name in bindings:
                    possible |= frozenset({bindings[name]})
            possible = frozenset(
                binding
                for binding in possible
                if binding not in {VALUE_BINDING, AMBIGUOUS_BINDING}
                and binding.kind != "static_literal"
            )
            if possible:
                joined_candidates[name] = possible
        return joined_bindings, joined_candidates

    def bind_candidates(
        target: ast.AST,
        value: ast.AST | None,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        if (
            isinstance(target, (ast.Tuple, ast.List))
            and isinstance(value, (ast.Tuple, ast.List))
            and len(target.elts) == len(value.elts)
        ):
            for child_target, child_value in zip(target.elts, value.elts):
                bind_candidates(
                    child_target, child_value, bindings, candidates
                )
            return
        possible = (
            expression_candidates(value, bindings, candidates)
            if value is not None
            else frozenset()
        )
        possible = frozenset(
            binding
            for binding in possible
            if binding not in {VALUE_BINDING, AMBIGUOUS_BINDING}
            and binding.kind != "static_literal"
        )
        for name in _target_names(target):
            if possible:
                candidates[name] = possible
            else:
                candidates.pop(name, None)

    def advance_state(
        source: ParsedSource,
        statement: ast.stmt,
        bindings: dict[str, Binding],
        candidates: CandidateState,
    ) -> None:
        assignment_values: list[tuple[ast.AST, ast.AST | None]] = []
        if isinstance(statement, ast.Assign):
            assignment_values = [
                (target, statement.value) for target in statement.targets
            ]
        elif isinstance(statement, ast.AnnAssign):
            assignment_values = [(statement.target, statement.value)]
        saved = dict(candidates)
        for name in _statement_bound_names(statement):
            candidates.pop(name, None)
        imported = _import_bindings(source.relative_path, statement)
        if imported:
            for name, binding in imported.items():
                candidates[name] = frozenset({binding})
        else:
            for target, value in assignment_values:
                bind_candidates(target, value, bindings, saved)
                for name in _target_names(target):
                    if name in saved:
                        candidates[name] = saved[name]
        _advance_binding_state(
            source,
            statement,
            bindings,
            definition_prefix=_module_name(source.relative_path),
        )

    def pattern_matches(pattern: ast.AST, value: object) -> bool | None:
        if MATCH_AS is not None and isinstance(pattern, MATCH_AS):
            if pattern.pattern is None:
                return True
            return pattern_matches(pattern.pattern, value)
        if isinstance(pattern, ast.MatchValue):
            try:
                expected = ast.literal_eval(pattern.value)
            except (SyntaxError, ValueError, TypeError):
                return None
            return expected == value
        if isinstance(pattern, ast.MatchSingleton):
            return pattern.value is value
        if isinstance(pattern, ast.MatchOr):
            results = [pattern_matches(item, value) for item in pattern.patterns]
            if True in results:
                return True
            if all(result is False for result in results):
                return False
        return None

    Outcome = tuple[dict[str, Binding], CandidateState, str]

    def coalesce_outcomes(outcomes: list[Outcome]) -> list[Outcome]:
        grouped: dict[str, list[tuple[dict[str, Binding], CandidateState]]] = {}
        for bindings, candidates, control in outcomes:
            grouped.setdefault(control, []).append((bindings, candidates))
        return [
            (*merge_states(states), control)
            for control, states in grouped.items()
        ]

    def literal_only(node: ast.AST | None) -> bool:
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            return all(literal_only(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return all(
                (key is None or literal_only(key)) and literal_only(value)
                for key, value in zip(node.keys, node.values)
            )
        return False

    def statement_may_raise(statement: ast.stmt) -> bool:
        if isinstance(statement, (ast.Pass, ast.Global, ast.Nonlocal)):
            return False
        if isinstance(statement, ast.Expr):
            return not literal_only(statement.value)
        if isinstance(statement, ast.Assign):
            return not literal_only(statement.value)
        if isinstance(statement, ast.AnnAssign):
            return statement.value is not None and not literal_only(statement.value)
        return True

    def scan_statement(
        source: ParsedSource,
        statement: ast.stmt,
        incoming: dict[str, Binding],
        incoming_candidates: CandidateState,
    ) -> list[Outcome]:
        bindings = dict(incoming)
        candidates = dict(incoming_candidates)
        if isinstance(statement, ast.If):
            inspect_expression(statement.test, bindings, candidates)
            truth = _literal_truth(statement.test)
            branches = (
                [statement.body]
                if truth is True
                else [statement.orelse]
                if truth is False
                else [statement.body, statement.orelse]
            )
            return coalesce_outcomes(
                [
                    outcome
                    for branch in branches
                    for outcome in scan_suite(
                        source, branch, bindings, candidates
                    )
                ]
            )
        if isinstance(statement, (ast.For, ast.AsyncFor)):
            inspect_expression(
                statement.iter,
                bindings,
                candidates,
                consume_generator=isinstance(statement.iter, ast.GeneratorExp),
            )
            iteration = literal_iteration(statement.iter)
            if iteration is False:
                return scan_suite(
                    source, statement.orelse, bindings, candidates
                )
            body_bindings = dict(bindings)
            body_candidates = dict(candidates)
            bind_runtime_names(
                statement.target,
                iterable_candidates(
                    statement.iter, body_bindings, body_candidates
                ),
                body_bindings,
                body_candidates,
            )
            body_outcomes = scan_suite(
                source, statement.body, body_bindings, body_candidates
            )
            outcomes: list[Outcome] = []
            if iteration is None:
                outcomes.extend(
                    scan_suite(
                        source, statement.orelse, bindings, candidates
                    )
                )
            for body_bindings, body_candidates, control in body_outcomes:
                if control == "break":
                    outcomes.append((body_bindings, body_candidates, "normal"))
                elif control in {"return", "raise"}:
                    outcomes.append((body_bindings, body_candidates, control))
                else:
                    outcomes.extend(
                        scan_suite(
                            source,
                            statement.orelse,
                            body_bindings,
                            body_candidates,
                        )
                    )
            return coalesce_outcomes(outcomes)
        if isinstance(statement, ast.While):
            inspect_expression(statement.test, bindings, candidates)
            truth = _literal_truth(statement.test)
            if truth is False:
                return scan_suite(
                    source, statement.orelse, bindings, candidates
                )
            body_outcomes = scan_suite(
                source, statement.body, bindings, candidates
            )
            outcomes = []
            if truth is None:
                outcomes.extend(
                    scan_suite(
                        source, statement.orelse, bindings, candidates
                    )
                )
            for body_bindings, body_candidates, control in body_outcomes:
                if control == "break":
                    outcomes.append((body_bindings, body_candidates, "normal"))
                elif control in {"return", "raise"}:
                    outcomes.append((body_bindings, body_candidates, control))
                elif truth is None:
                    outcomes.extend(
                        scan_suite(
                            source,
                            statement.orelse,
                            body_bindings,
                            body_candidates,
                        )
                    )
            return coalesce_outcomes(outcomes)
        if isinstance(statement, (ast.With, ast.AsyncWith)):
            for item in statement.items:
                inspect_expression(item.context_expr, bindings, candidates)
                if item.optional_vars is not None:
                    bind_runtime_names(
                        item.optional_vars,
                        frozenset(),
                        bindings,
                        candidates,
                    )
            return scan_suite(source, statement.body, bindings, candidates)
        if isinstance(statement, (ast.Try, TRY_STAR or ast.Try)):
            active: list[Outcome] = [(bindings, candidates, "normal")]
            completed: list[Outcome] = []
            exception_states: list[
                tuple[dict[str, Binding], CandidateState]
            ] = []
            for child in statement.body:
                next_active: list[Outcome] = []
                for child_bindings, child_candidates, control in active:
                    if control != "normal":
                        completed.append(
                            (child_bindings, child_candidates, control)
                        )
                        continue
                    if statement_may_raise(child):
                        exception_states.append(
                            (dict(child_bindings), dict(child_candidates))
                        )
                    for outcome in scan_statement(
                        source,
                        child,
                        child_bindings,
                        child_candidates,
                    ):
                        if outcome[2] == "raise":
                            if not statement.handlers:
                                completed.append(outcome)
                        else:
                            next_active.append(outcome)
                active = coalesce_outcomes(next_active)
            for child_bindings, child_candidates, control in active:
                if control == "normal":
                    completed.extend(
                        scan_suite(
                            source,
                            statement.orelse,
                            child_bindings,
                            child_candidates,
                        )
                    )
                else:
                    completed.append(
                        (child_bindings, child_candidates, control)
                    )
            for handler in statement.handlers:
                for handler_bindings, handler_candidates in exception_states:
                    handler_bindings = dict(handler_bindings)
                    handler_candidates = dict(handler_candidates)
                    if handler.type is not None:
                        inspect_expression(
                            handler.type,
                            handler_bindings,
                            handler_candidates,
                        )
                    if handler.name:
                        handler_bindings.pop(handler.name, None)
                        handler_candidates.pop(handler.name, None)
                    completed.extend(
                        scan_suite(
                            source,
                            handler.body,
                            handler_bindings,
                            handler_candidates,
                        )
                    )
            completed = coalesce_outcomes(completed)
            if not statement.finalbody:
                return completed
            finalized: list[Outcome] = []
            for final_bindings, final_candidates, prior_control in completed:
                for outcome in scan_suite(
                    source,
                    statement.finalbody,
                    final_bindings,
                    final_candidates,
                ):
                    if outcome[2] == "normal":
                        finalized.append((*outcome[:2], prior_control))
                    else:
                        finalized.append(outcome)
            return coalesce_outcomes(finalized)
        if MATCH is not None and isinstance(statement, MATCH):
            inspect_expression(statement.subject, bindings, candidates)
            try:
                subject = ast.literal_eval(statement.subject)
            except (SyntaxError, ValueError, TypeError):
                subject = _NO_STATIC_VALUE
            outcomes: list[Outcome] = []
            exhaustive = False
            for case in statement.cases:
                match = (
                    pattern_matches(case.pattern, subject)
                    if subject is not _NO_STATIC_VALUE
                    else (
                        True
                        if MATCH_AS is not None
                        and isinstance(case.pattern, MATCH_AS)
                        and case.pattern.pattern is None
                        else None
                    )
                )
                guard_truth = (
                    True if case.guard is None else _literal_truth(case.guard)
                )
                if match is False or guard_truth is False:
                    continue
                case_bindings = dict(bindings)
                case_candidates = dict(candidates)
                for candidate in ast.walk(case.pattern):
                    name = getattr(candidate, "name", None)
                    if isinstance(name, str):
                        case_bindings.pop(name, None)
                        case_candidates.pop(name, None)
                if case.guard is not None:
                    inspect_expression(
                        case.guard, case_bindings, case_candidates
                    )
                outcomes.extend(
                    scan_suite(
                        source,
                        case.body,
                        case_bindings,
                        case_candidates,
                    )
                )
                if match is True and guard_truth is True:
                    exhaustive = True
                    break
            if not exhaustive:
                outcomes.append((bindings, candidates, "normal"))
            return coalesce_outcomes(outcomes)
        if isinstance(
            statement,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ):
            for expression in _definition_expressions(statement):
                inspect_expression(expression, bindings, candidates)
            for decorator in statement.decorator_list:
                record_implicit_decorator_call(
                    decorator, bindings, candidates
                )
        else:
            value = _statement_value(statement)
            if value is not None:
                consume = isinstance(value, ast.GeneratorExp) and any(
                    isinstance(statement, ast.Assign)
                    and isinstance(target, (ast.Tuple, ast.List))
                    for target in getattr(statement, "targets", ())
                )
                inspect_expression(
                    value,
                    bindings,
                    candidates,
                    consume_generator=consume,
                )
            elif not isinstance(
                statement, (ast.Pass, ast.Global, ast.Nonlocal)
            ):
                inspect_expression(statement, bindings, candidates)
        advance_state(source, statement, bindings, candidates)
        control = (
            "return"
            if isinstance(statement, ast.Return)
            else "raise"
            if isinstance(statement, ast.Raise)
            else "break"
            if isinstance(statement, ast.Break)
            else "continue"
            if isinstance(statement, ast.Continue)
            else "normal"
        )
        return [(bindings, candidates, control)]

    def scan_suite(
        source: ParsedSource,
        statements: list[ast.stmt],
        incoming: dict[str, Binding],
        incoming_candidates: CandidateState,
    ) -> list[Outcome]:
        outcomes: list[Outcome] = [
            (dict(incoming), dict(incoming_candidates), "normal")
        ]
        for statement in statements:
            updated: list[Outcome] = []
            for bindings, candidates, control in outcomes:
                if control != "normal":
                    updated.append((bindings, candidates, control))
                    continue
                updated.extend(
                    scan_statement(
                        source,
                        statement,
                        bindings,
                        candidates,
                    )
                )
            outcomes = coalesce_outcomes(updated)
            if not any(control == "normal" for _, _, control in outcomes):
                break
        return outcomes

    for path in caller_paths:
        source = parsed.get(path)
        if source is None:
            continue
        module_outcomes = scan_suite(source, source.tree.body, {}, {})
        module_states = [
            (bindings, candidates)
            for bindings, candidates, control in module_outcomes
            if control == "normal"
        ]
        if not module_states:
            module_states = [
                (bindings, candidates)
                for bindings, candidates, _ in module_outcomes
            ]
        module_bindings, module_candidates = merge_states(module_states)
        for operation in operations_by_path.get(path, []):
            function_bindings = dict(module_bindings)
            function_candidates = dict(module_candidates)
            for name in _function_local_names(operation.node):
                function_bindings.pop(name, None)
                function_candidates.pop(name, None)
            scan_suite(
                source,
                operation.node.body,
                function_bindings,
                function_candidates,
            )
    return {
        path: {
            function_id: tuple(invocations)
            for function_id, invocations in functions.items()
        }
        for path, functions in entries.items()
    }


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

    canonical_error_paths = {_bc_error_path(bc) for bc in config.error_bcs}
    mutation_paths = {*managed_paths}
    if config.api_module is not None:
        mutation_paths.add(config.api_module)
    mutation_paths.difference_update(canonical_error_paths)
    caller_paths = {*active_controllers}
    if config.api_module is not None:
        caller_paths.add(config.api_module)
    external_invocations = _direct_external_entry_invocations(
        parsed,
        caller_paths,
        mutation_paths - caller_paths,
        operations_by_path,
    )
    for path in sorted(mutation_paths, key=Path.as_posix):
        source = parsed.get(path)
        if source is None:
            continue
        entry_ids = {
            id(operation.node) for operation in operations_by_path.get(path, [])
        }
        path_invocations = external_invocations.get(path, {})
        entry_ids.update(path_invocations)
        for node in _schema_contract_mutation_nodes(
            source.tree.body,
            entry_function_ids=entry_ids,
            entry_invocations=path_invocations,
        ):
            _append_finding(
                findings,
                seen,
                source,
                node,
                "FrameworkErrorSchema/model config mutation in controller forbidden",
            )

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
            one_hop.update(
                _operation_one_hop_paths(
                    source,
                    _discover_operations(source, owner, analysis),
                    owner,
                    module_paths,
                )
            )
    if config.api_module is not None:
        api_source = selected.get(config.api_module)
        if api_source is not None:
            one_hop.update(_api_one_hop_paths(api_source, module_paths))
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
    language = _error_language(parsed, config.error_bcs, config.root, analysis)
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


# ── 표준 트리 슬라이스 — 트리 개정 명세 몫 11규칙 (트리 8·11·12행 · D7·D11·D27) ──
#
# 모든 프로필(auto 포함)에서 돈다 — 옛 판은 auto 에서 완전 무동작(fail-open)이었다.
#   #120 api/ 1차 축은 <area>/ — 기술 폴더(ninja/ 등) 금지
#   #121 api/<area>/ 이름 = application_layer/<area>/ 와 글자까지 동일
#   #123 api/<area>/ 진입점은 <area>_controller.py 하나
#   #124 요청 하나 = 메서드 하나(한 메서드에 라우트 데코 여럿 금지)
#   #125(ⓓ) 컨트롤러 메서드 = 변환·1회 호출·변환만 — 분기·루프는 후보
#   #126 도메인 예외 매핑은 메서드 «안» 직접 — handler 등록 decorator 금지
#   #131 기술 이름은 파일이 아니라 클래스에(ninja_*.py 금지)
#   #132 라우트 데코·인증·상태 코드는 «컨트롤러 파일»에만
#   #474 입구 파일은 도메인 예외를 «타입»으로만 — except … as e 의 e 참조 금지
#   #59·#62 는 전역 핸들러·except Exception — 입구 파일의 catch-all 을 #62 로 잡고,
#        전역(project) 쪽은 기존 code-profile 기계가 담당한다.

import ast as _ast

try:
    import standard_tree as _stree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

_TREE_DRIVING = ("driving_layer",)
_TREE_OHS = ("open_host_service",)
_TREE_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
_TREE_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
_TECH_DIR_TOKENS = {"ninja", "drf", "rest", "http", "views", "controllers", "handlers", "endpoints"}
_TECH_FILE_TOKENS = ("ninja", "drf")
_HTTP_DECO_NAMES = {"get", "post", "put", "patch", "delete", "head", "options", "api_operation", "route"}
_CATCH_ALL_NAMES = {"Exception", "BaseException"}


def _tree_bcs2(root: Path) -> list[Path]:
    out: list[Path] = []
    for c in root.rglob("application"):
        if not c.is_dir() or set(c.parts) & CODE_SKIP_DIRS:
            continue
        out.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return out


def _tree_adopted2(bcs: list[Path]) -> bool:
    for bc in bcs:
        if any((bc / n).is_dir() for n in _TREE_LAYERS):
            return True
        if any((bc / m).is_file() for m in _TREE_APP_MARKERS):
            return True
        if any(p.is_dir() and p.name.startswith("django_") for p in bc.iterdir()):
            return True
    return False


def _deco_route_name(deco: _ast.expr) -> str | None:
    """라우트 데코레이터인가 — `@router.get(...)`·`@api.post(...)`·`@http_get(...)`."""
    target = deco.func if isinstance(deco, _ast.Call) else deco
    name = target.attr if isinstance(target, _ast.Attribute) else getattr(target, "id", "")
    if not name:
        return None
    if name in _HTTP_DECO_NAMES or name.startswith("http_"):
        return name
    return None


def _slice_check_controller_ast(
    f: Path,
    rel: Path,
    findings: Findings,
    candidates: Candidates,
    finding_keys: "list[tuple[str, str, int] | None]",
    candidate_keys: "list[tuple[str, str, int] | None]",
    is_controller: bool,
) -> None:
    # 라인은 공용 포매터의 violation/candidate 문법으로 emit_all 이 생성한다(B형
    # locator 콜론 정형화 — 출력 계약 v2). keys 는 엔트리와 같은 순서의 tree↔code
    # 동일 사건 좌표다(#62·#474 = handler 행 · ⓓ#125 = route 함수 def 행 — overlap 절).
    try:
        mod = _ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return
    domain_names: set[str] = set()
    for node in _ast.walk(mod):
        if isinstance(node, _ast.ImportFrom) and node.level == 0 and node.module:
            if "domain_layer" in node.module.split("."):
                domain_names.update(a.asname or a.name for a in node.names)
    for node in _ast.walk(mod):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            routes = [d for d in node.decorator_list if _deco_route_name(d)]
            deco_names = set()
            for d in node.decorator_list:
                t = d.func if isinstance(d, _ast.Call) else d
                deco_names.add(t.attr if isinstance(t, _ast.Attribute) else getattr(t, "id", ""))
            where = f"{rel}:{node.lineno}"
            if "exception_handler" in deco_names:
                msg = "handler 등록 decorator — 도메인 예외→ErrorSchema 매핑은 컨트롤러 메서드 «안»에 직접 쓴다(helper·factory·global mapper 금지)"
                findings.add("#126", where, msg)
                finding_keys.append(None)
            if len(routes) >= 2:
                msg = f"`{node.name}()` 에 라우트 데코가 {len(routes)}개 — 요청 하나당 메서드 하나다"
                findings.add("#124", where, msg)
                finding_keys.append(None)
            if routes and not is_controller:
                msg = "라우트 데코레이터가 컨트롤러 파일 밖에 있다 — 라우트·인증·상태 코드는 `<area>_controller.py` 에 온다"
                findings.add("#132", where, msg)
                finding_keys.append(None)
            if routes and is_controller:
                question = "입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다)?"
                for sub in node.body:
                    if isinstance(sub, (_ast.For, _ast.While)):
                        sub_where = f"{rel}:{sub.lineno}"
                        candidates.add("#125", sub_where, "라우트 메서드 안 루프", question)
                        candidate_keys.append(("#125", rel.as_posix(), node.lineno))
                        break
                    if isinstance(sub, _ast.If) and not _is_exc_mapping_if(sub, domain_names):
                        sub_where = f"{rel}:{sub.lineno}"
                        candidates.add("#125", sub_where, "라우트 메서드 안 분기", question)
                        candidate_keys.append(("#125", rel.as_posix(), node.lineno))
                        break
        elif isinstance(node, _ast.ExceptHandler):
            caught = node.type
            caught_names: list[str] = []
            if isinstance(caught, _ast.Tuple):
                caught_names = [getattr(e, "id", getattr(e, "attr", "")) for e in caught.elts]
            elif caught is not None:
                caught_names = [getattr(caught, "id", getattr(caught, "attr", ""))]
            if caught is None or set(caught_names) & _CATCH_ALL_NAMES:
                where = f"{rel}:{node.lineno}"
                msg = "`except Exception`/bare — 폴백은 도메인·응용 base 단위 catch 로 한정한다(base 는 상한이다 — code-json managed controller 는 concrete/구체 tuple 만 catch 한다: ninja §6.2)"
                findings.add("#62", where, msg)
                finding_keys.append(("#62", rel.as_posix(), node.lineno))
            if node.name and set(caught_names) & domain_names:
                for sub in _ast.walk(node):
                    if isinstance(sub, _ast.Name) and sub.id == node.name and isinstance(sub.ctx, _ast.Load):
                        sub_where = f"{rel}:{sub.lineno}"
                        msg = f"도메인 예외를 `as {node.name}` 로 묶어 참조했다 — 입구 파일은 도메인 예외를 «타입»으로만 쓴다"
                        # locator 는 참조 행이지만 사건 좌표는 handler 행이다
                        # (overlap 절 — locator 가 달라도 같은 incident).
                        findings.add("#474", sub_where, msg)
                        finding_keys.append(("#474", rel.as_posix(), node.lineno))
                        break


def _is_exc_mapping_if(node: _ast.If, domain_names: set[str]) -> bool:
    """`if isinstance(exc, DomainError):` 꼴 매핑 분기는 #126 의 정상 형태라 후보에서 뺀다."""
    for sub in _ast.walk(node.test):
        if isinstance(sub, _ast.Call) and getattr(sub.func, "id", "") == "isinstance":
            return True
    return False


def _tree_slice2(
    root: Path, bcs: list[Path]
) -> "tuple[Findings, Candidates, list[tuple[str, str, int] | None], list[tuple[str, str, int] | None]]":
    # 구조화 엔트리 수집 — 방출은 호출측 emit_all 이 한 순서로 수행한다(출력 계약 v2).
    # keys 두 목록은 엔트리와 같은 순서·같은 길이다(선점 억제 zip 좌표 — 억제 비대상
    # 사이트는 None).
    findings: Findings = Findings(defer=True)
    candidates: Candidates = Candidates(defer=True)
    finding_keys: "list[tuple[str, str, int] | None]" = []
    candidate_keys: "list[tuple[str, str, int] | None]" = []
    for bc in bcs:
        app_layer = bc / "application_layer"
        app_areas = (
            {p.name for p in app_layer.iterdir() if p.is_dir() and p.name not in ("port", "domain_bypass_query", "unit_of_work")}
            if app_layer.is_dir()
            else None
        )
        for driving in _TREE_DRIVING:
            api = bc / driving / "api"
            if api.is_dir():
                for area in sorted(p for p in api.iterdir() if p.is_dir()):
                    if area.name in ("webhook", "__pycache__") or area.name.startswith("."):
                        continue
                    if area.name in ("api_router", "bc_error_schema"):
                        continue  # api 직계 «파일 칸»의 동명 폴더 — 배제 칸 승격 red 는 registry #4 소유(area 오인·이중 발화 방지)
                    area_rel = area.relative_to(root)
                    area_where = f"{area_rel}/"
                    if area.name.lower() in _TECH_DIR_TOKENS:
                        msg = f"`api/` 의 1차 축은 `<area>/` 다 — 기술 폴더(`{area.name}/`)를 만들지 않는다"
                        findings.add("#120", area_where, msg)
                        finding_keys.append(None)
                        continue
                    if app_areas is not None and area.name not in app_areas:
                        msg = "`api/<area>/` 이름은 안쪽 `application_layer/<area>/` 와 글자까지 같아야 한다"
                        findings.add("#121", area_where, msg)
                        finding_keys.append(None)
                    # 진입점 칸은 동명 폴더 승격 가능 — entry 는 실현(파일 또는 승격 본체)이다.
                    entry = checker_target.slot_file(area / f"{area.name}_controller.py")
                    if entry is None:
                        msg = f"진입점 `{area.name}_controller.py` 파일 하나가 온다"
                        findings.add("#123", area_where, msg)
                        finding_keys.append(None)
                    for p in checker_target.slot_glob(area, "*_controller.py"):
                        if p != entry:
                            where = f"{p.relative_to(root)}"
                            msg = f"`api/<area>/` 의 진입점은 `{area.name}_controller.py` «하나»다"
                            findings.add("#123", where, msg)
                            finding_keys.append(None)
                # api/** 파일 규칙 — #131(기술 파일명) · 컨트롤러/비컨트롤러 AST
                for p in sorted(api.rglob("*.py")):
                    if set(p.relative_to(api).parts) & {"__pycache__"}:
                        continue
                    rel = p.relative_to(root)
                    if any(tok in p.name.lower() for tok in _TECH_FILE_TOKENS):
                        msg = "기술 이름은 파일이 아니라 «클래스»에 붙는다 — `NinjaTurnController` 처럼"
                        findings.add("#131", rel, msg)
                        finding_keys.append(None)
                    _slice_check_controller_ast(
                        p, rel, findings, candidates, finding_keys, candidate_keys,
                        p.name.endswith("_controller.py"),
                    )
            for ohs_name in _TREE_OHS:
                ohs = bc / driving / ohs_name
                if not ohs.is_dir():
                    continue
                for p in sorted(ohs.rglob("*_service.py")):
                    _slice_check_controller_ast(
                        p, p.relative_to(root), findings, candidates,
                        finding_keys, candidate_keys, True,
                    )
    return findings, candidates, finding_keys, candidate_keys


_OVERLAP_RULES: "frozenset[str]" = frozenset({"#62", "#474", "#125"})


def _code_overlap_keys(findings: "list[Finding]") -> "set[tuple[str, str, int]]":
    """code 레인 실발화 사건의 tree 대응 좌표(귀속 매핑표 v2 overlap 절) —
    Finding.overlap_line 이 채워진 #62/#474/#125 만 억제 키가 된다."""
    keys: "set[tuple[str, str, int]]" = set()
    for finding in findings:
        if finding.rule in _OVERLAP_RULES and finding.overlap_line is not None:
            keys.add((finding.rule, finding.path.as_posix(), finding.overlap_line))
    return keys


def _suppress_overlapped_tree(
    tree: "Findings | Candidates",
    tree_keys: "list[tuple[str, str, int] | None]",
    code_keys: "set[tuple[str, str, int]]",
) -> "Findings | Candidates":
    """tree↔code 동일 사건 선점 억제(귀속 매핑표 v2 overlap 절 — U13·U14).

    code 레인이 같은 사건(#62·#474 handler 행 · ⓓ#125 route 함수 def 행)을 적중한
    대상의 tree 사이트는 라인·레코드 모두 방출하지 않는다(1건 대표 — 더 정밀한
    판정이 이긴다. 대상 밖·code 미발화에서는 tree 단독 그대로)."""
    kept = type(tree)(tree.checker, defer=True)
    for entry, key in zip(tree.entries, tree_keys):
        if key is not None and key in code_keys:
            continue
        kept.entries.append(entry)
        kept.append(entry.line)
    return kept


def _print_tree_blocks(tree_findings: Findings, tree_candidates: Candidates) -> None:
    if tree_findings:
        print("[check-api-error-controller-contract] BLOCKER — 입구(컨트롤러) 계약 규율 위반 (트리 8·11·12행):")
        emit_all(tree_findings, printer=print)
    if tree_candidates:
        print("[check-api-error-controller-contract] ⓓ 후보 — 기계가 후보를 좁혔다 · 마무리 물음은 discipline-reviewer 몫(exit 불산입):")
        emit_all(tree_candidates, printer=print)


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

    if config.anchor is not None:
        # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚 파일·
        # 공허 차분이 침묵 exit 0 되지 않게 parse 직후 막는다(fail-closed).
        try:
            anchor_diff.validate_materials(config.root, config.anchor, config.anchor_debt_file)
        except anchor_diff.AnchorDiffUsage as exc:
            print(
                f"[check-api-error-controller-contract] 사용 오류: {exc}",
                file=sys.stderr,
            )
            return 1

    # 표준 트리 슬라이스 — 프로필과 무관하게 먼저 본다(옛 auto 무동작 = fail-open 차단).
    bcs = _tree_bcs2(config.root)
    if not any((bc / d).is_dir() for bc in bcs for d in _TREE_DRIVING) and _tree_adopted2(bcs):
        # 대상-0 가드 — 라인 = msg 원문(무들여쓰기 byte 보존) + rule=«대상0» 센티널
        # 레코드. #74 는 달지 않는다(소유자 checker_lint — rule-owner-map).
        guard: Findings = zero_target_guard(
            "[check-api-error-controller-contract] blocker: 채택 신호는 있는데 driving 층이 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2
    # --anchor 미지정이면 현행 그대로 각 슬라이스에서 즉시 exit 2 — 지정 시에만
    # 슬라이스 진단을 모아 마지막에 판정 차분(anchor_diff)으로 exit 를 정한다.
    collected: list[str] = []
    pending_analysis: list[str] = []
    tree_findings, tree_candidates, tree_keys, candidate_keys = _tree_slice2(config.root, bcs)
    if tree_findings and config.anchor is None:
        # tree 위반이 code 레인 전에 exit 2 를 선점한다(현행) — code 미실행이라
        # 선점 억제 없음(tree 단독 그대로).
        _print_tree_blocks(tree_findings, tree_candidates)
        return 2

    if config.profile != "auto":
        try:
            # tree↔code 동일 사건 선점 억제를 위해 code 레인을 먼저 계산한다 —
            # 분석 불능(UsageError)이어도 확정 tree 진단·후보는 exit 1 전에 그대로
            # 인쇄한다(현행 stdout 순서 보존 · 억제는 code 실발화 시에만).
            try:
                analysis, findings = _run(config)
            except UsageError:
                _print_tree_blocks(tree_findings, tree_candidates)
                raise
            dynamic_proof_only = bool(analysis) and all(
                issue.startswith("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED ")
                for issue in analysis
            )
            reported_findings = findings
            if dynamic_proof_only:
                reported_findings = [
                    finding
                    for finding in findings
                    if not finding.requires_static_error_shape
                ]
            emit_code = bool(reported_findings) and (not analysis or dynamic_proof_only)
            if emit_code and (tree_findings or tree_candidates):
                code_keys = _code_overlap_keys(reported_findings)
                tree_findings = _suppress_overlapped_tree(tree_findings, tree_keys, code_keys)
                tree_candidates = _suppress_overlapped_tree(tree_candidates, candidate_keys, code_keys)
            _print_tree_blocks(tree_findings, tree_candidates)
            if tree_findings:
                collected.extend(lines(tree_findings))
            if emit_code:
                print(
                    "[check-api-error-controller-contract] BLOCKER — code-profile "
                    "controller error mapping contract violation:"
                )
                # 방출 표면 — 라인은 레코드 필드의 순수 함수(violation `[#N] {where}:
                # {msg}` · 계약 `- {where}: {msg}`)이고, stdout 인쇄 순서 = 레코드
                # 순서(emit_all 불변식). 판정(#N/계약)이 갈릴 때마다 defer 컬렉션을
                # 이어 붙여 현행 인쇄 순서를 보존한다.
                surfaces: "list[Findings | ContractFindings]" = []

                def _violation_surface() -> Findings:
                    tail = surfaces[-1] if surfaces else None
                    if not isinstance(tail, Findings):
                        tail = Findings(defer=True)
                        surfaces.append(tail)
                    return tail

                def _contract_surface() -> ContractFindings:
                    tail = surfaces[-1] if surfaces else None
                    if not isinstance(tail, ContractFindings):
                        tail = ContractFindings(CONTRACT_REF, defer=True)
                        surfaces.append(tail)
                    return tail

                for finding in reported_findings:
                    finding_where: str = f"{finding.path}:{finding.lineno}"
                    finding_msg: str = f"{finding.category}: {finding.shown}"
                    if finding.rule is not None:
                        _violation_surface().add(
                            finding.rule, finding_where, finding_msg, symbol=finding.symbol
                        )
                    else:
                        _contract_surface().add(
                            where=finding_where, msg=finding_msg, symbol=finding.symbol
                        )
                emit_all(*surfaces, printer=print)
                print(
                    "  근거: known BC failures are mapped directly by their selected "
                    "owner controller through one narrow exception or try-free None "
                    "path and direct two-argument Status(<approved HTTP status>, error); helper/handler/raw "
                    "detours are not part of this contract."
                )
                if config.anchor is None:
                    return 2
                for surface in surfaces:
                    collected.extend(lines(surface))
                # 토큰-only analysis 는 차분 강등으로 소거되지 않는다 — findings 가
                # 전건 앵커 기존분이어도 proof 경로(exit 1)로 남긴다(fail-open 차단).
                pending_analysis = analysis
            elif analysis:
                raise UsageError("; ".join(analysis))
        except UsageError as exc:
            print(
                f"[check-api-error-controller-contract] 사용 오류: {exc}",
                file=sys.stderr,
            )
            return 1
    else:
        _print_tree_blocks(tree_findings, tree_candidates)
        if tree_findings:
            collected.extend(lines(tree_findings))

    if collected:
        try:
            verdict = anchor_diff.partition_exit(
                script=Path(__file__).resolve(),
                label="[check-api-error-controller-contract]",
                target=config.root,
                anchor=config.anchor or "",
                argv=argv[1:],
                findings=collected,
                path_flags=frozenset({"--api-module", "--controller-module"}),
                debt_file=config.anchor_debt_file,
                analysis_pending=bool(pending_analysis),
            )
        except anchor_diff.AnchorDiffUsage as exc:
            print(
                f"[check-api-error-controller-contract] 사용 오류: {exc}",
                file=sys.stderr,
            )
            return 1
        if verdict == 0 and pending_analysis:
            # 토큰-only analysis 는 강등으로 소거되지 않는다 — proof 경로(exit 1).
            print(
                "[check-api-error-controller-contract] 사용 오류: "
                + "; ".join(pending_analysis),
                file=sys.stderr,
            )
            return 1
        return verdict
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
