#!/usr/bin/env python3
"""dddjango 컴포지션 루트(DI 배선) 위치 결정적 백스톱 (discipline-houserules §0 집행).

표준 트리에서 DI 조립(컴포지션 루트)은 BC 루트의 *단일 파일* `application/<app>/composition_root.py`가
소유한다(houserules §0 트리·파일표; `implementation-django-ninja` "컴포지션 루트" 절). presentation은
그 `build_<usecase>_command()` 팩토리를 매요청 호출만 하고, operation 본문에서
`Django…Repository()`/`…Adapter()`를 직접 생성하지 않는다(Q-7). 이 백스톱은 배선이 그 단일 파일을
벗어나거나 부재인 *구조적* 변종 셋을 차단한다:
  - **off-tree `composition/` 폴더(V1)**: `application/<app>/composition/`에 배선 코드(provider 등)를
    폴더로 둠 = 정본 트리에 없는 노드(루트가 폴더로 분열). 라이브 관측 변종(Codex `composition/
    place_order_provider.py`).
  - **`composition_root.py` 오배치(V2)**: `composition_root.py`가 BC 루트가 아니라 계층/하위 폴더
    (`presentation_layer/`·`infra_layer/` 등)에 묻힘 = 위치 위반(BC 루트 소유여야).
  - **정본 부재(V3)**: application 로직(command/query/service 등)을 가진 BC인데 BC 루트
    `composition_root.py`가 *아예 없음* = 배선이 `di/`·`wiring/`·라우터·config 등으로 흩어졌거나
    미생성(긍정 의무 미이행). 정본 파일의 존재를 무조건이 아니라 *application 로직이 있을 때* 요구해
    데이터소스 BC(빈 `application_layer`)는 면제한다.

*왜 결정적 백스톱인가* — 배선 위치는 코더 구현 결정이고 테스트가 안 걸려 TDD Red로 안 잡힌다.
discipline-reviewer 의미 게이트 한 점에만 의존하면 off-tree 폴더가 'Q-7 준수(어댑터를 operation
밖으로 뺌)'로 *칭찬*받아 통과할 수 있다 — 이 스크립트가 그 구조 절반을 결정적으로 메운다
(고정밀·저-recall, 거짓 양성 ≈0). `config/api.py` 내장·`<app>_api_router.py` 접힘 같은 *in-tree
파일 내장* 변종은 그 파일이 적법히 존재해 형태로 못 가르므로 discipline-reviewer 의미 레인 몫이다.

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 *표준 레이아웃*을 쓴다 = 레포에 `application/` 컨테이너가 있다. 없으면 기존
     확립 규약(§1.1)이라 적용 대상이 아니다 → exit 0.
  2) `application/<bc>/`가 *4계층 앱*이다(계층 폴더 하나라도 보유) — 비-앱 잡동사니 패키지 제외.
  3) (git 레포면) 그 BC 하위에 이번 변경(신규/수정/미추적)이 있다 = 이번 작업이 건드린 BC.
     기존 커밋된 채 안 건드린 BC는 존중(brownfield) → 건너뜀.
  위 셋이 참인 BC에서:
    - BC 루트 직속 `composition/`(`<bc>/composition/`)가 비-`__init__` `.py`를 담으면 blocker
      (off-tree 폴더·V1). 빈 패키지·test 경로는 면제. 도메인 애그리거트 `domain_layer/composition/`은
      BC 루트 직속이 아니라 애초에 대상이 아니다(거짓 양성 0).
    - `composition_root.py`가 BC 루트(`<bc>/composition_root.py`)가 아닌 계층/하위 폴더에 있으면
      blocker(오배치·V2). test 경로·`composition/` 안의 것(위 V1이 이미 잡음)은 면제. BC 루트의 것은 정상.
    - `application_layer`에 실 application 로직(비-`__init__` `.py`; `dto/`·test 제외)이 있는데 BC 루트
      `composition_root.py`가 없으면 blocker(부재·V3). command/query 만이 아니라 `service/`·`handler/`
      등 application_layer 실 로직 전체가 신호다(빈 `command/` 만 남기고 `service/` 로 fold 하는 우회
      봉쇄). 데이터소스 BC(§632 상 `application_layer` 가 빈 계층)는 로직이 없어 면제(거짓 양성 0).
      정본이 존재하되 *비어 있고 실배선이 딴 곳에* fold 된 알리바이는 형태로 못 가르므로
      discipline-reviewer 의미 레인 몫이다(이 V3는 *부재*만 결정적으로 잡는다).

명시적 `dddjango-code-json` lane은 선택 API object, canonical BC registrar, project URLconf의
직접 import provenance와 exactly-once 호출 관계를 함께 검사한다. preserve/auto에서는 이 의미
검사를 적용하지 않되, preserve가 공급한 source selector의 일반 경로·inventory·parse 계약은 검증한다.

사용법: check-composition-root.py [TARGET_DIR] [--error-profile PROFILE ...]
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
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

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
CODE_SKIP_DIRS = {
    *SKIP_DIRS,
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "migrations",
    "generated",
}

# 4계층 — houserules §0-2. "이 BC가 4계층 앱인가"의 신호(하나라도 폴더면 검사 대상).
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")

TEST_DIR_NAMES = {"test", "tests"}

ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
ROOT_API_CONSTRUCTORS = {"ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"}

# 정본 배선 노드 — BC 루트의 단일 파일. 폴더 변종(아래)은 off-tree.
COMPOSITION_FILE = "composition_root.py"
COMPOSITION_DIR = "composition"


class UsageError(Exception):
    """CLI, inventory, or selected-source analysis error."""


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


@dataclass(frozen=True)
class Config:
    root: Path
    profile: str | None
    scope: str | None
    api_module: str | None
    urlconf_module: str | None
    registrar_modules: tuple[str, ...]


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
        return (
            f"  - {self.relative_path}:{self.lineno}  {self.category}"
            f" — {self.shown}"
        )


@dataclass(frozen=True)
class ImportFact:
    module: str
    full_path: str
    local_name: str
    binding: str
    lineno: int


@dataclass(frozen=True)
class RegistrarSpec:
    relative_path: Path
    bc: str
    function_name: str
    full_path: str


def _find_application_containers(root: Path) -> list[Path]:
    """표준 앱 컨테이너(`application/`) 디렉터리들."""
    out: list[Path] = []
    for path in root.rglob("application"):
        if not path.is_dir():
            continue
        if set(path.parts) & SKIP_DIRS:
            continue
        out.append(path)
    return out


def _find_bc_dirs(root: Path) -> list[Path]:
    """각 `application/` 컨테이너의 직속 하위 디렉터리(= BC 후보)."""
    out: list[Path] = []
    for container in _find_application_containers(root):
        for child in sorted(container.iterdir()):
            if not child.is_dir() or child.name in SKIP_DIRS:
                continue
            out.append(child)
    return out


def _has_any_layer(bc_dir: Path) -> bool:
    """4계층 폴더 중 하나라도 있으면 4계층 앱(이 백스톱 검사 대상)."""
    return any((bc_dir / layer).is_dir() for layer in LAYER_DIRS)


def _argument_parser() -> _UsageParser:
    parser = _UsageParser(add_help=True)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--error-profile", action="append")
    parser.add_argument("--scope", action="append")
    parser.add_argument("--api-module", action="append")
    parser.add_argument("--urlconf-module", action="append")
    parser.add_argument("--registrar-module", action="append", default=[])
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
        "--error-profile", namespace.error_profile, required=False, issues=issues
    )
    selectors_present = any(
        (
            namespace.scope,
            namespace.api_module,
            namespace.urlconf_module,
            namespace.registrar_module,
        )
    )
    if profile is None and selectors_present:
        issues.append("selector 사용 시 --error-profile 필수")
    if profile is not None and profile not in ERROR_PROFILES:
        issues.append(f"지원하지 않는 --error-profile: {profile}")
    if profile == "auto" and selectors_present:
        issues.append("auto profile에는 scope/source selector를 전달하지 않음")

    code_profile = profile == "dddjango-code-json"
    preserve_profile = profile == "preserve-established"
    scope = _one(
        "--scope",
        namespace.scope,
        required=code_profile or preserve_profile,
        issues=issues,
    )
    api_module = _one(
        "--api-module",
        namespace.api_module,
        required=code_profile or preserve_profile,
        issues=issues,
    )
    urlconf_module = _one(
        "--urlconf-module",
        namespace.urlconf_module,
        required=code_profile,
        issues=issues,
    )
    registrar_modules = tuple(namespace.registrar_module)
    if len(registrar_modules) != len(set(registrar_modules)):
        issues.append("반복 인자 중복: --registrar-module")
    if code_profile and not registrar_modules:
        issues.append("필수 인자 누락: --registrar-module")
    if preserve_profile and bool(urlconf_module) != bool(registrar_modules):
        issues.append(
            "preserve-established의 --urlconf-module/--registrar-module은 함께 전달해야 함"
        )
    if scope is not None and not scope.strip():
        issues.append("--scope는 빈 문자열일 수 없음")

    raw_roles: list[tuple[str, str]] = []
    if api_module is not None:
        raw_roles.append(("--api-module", api_module))
    if urlconf_module is not None:
        raw_roles.append(("--urlconf-module", urlconf_module))
    raw_roles.extend(("--registrar-module", raw) for raw in registrar_modules)
    lexical_roles: list[tuple[str, Path]] = []
    for option, raw in raw_roles:
        path = _source_path(option, raw, issues)
        if path is not None:
            lexical_roles.append((option, path))

    for index, (left_role, left_path) in enumerate(lexical_roles):
        for right_role, right_path in lexical_roles[index + 1 :]:
            if left_path != right_path:
                continue
            if left_role == right_role == "--registrar-module":
                continue
            issues.append(f"{left_role}과 {right_role} 역할 overlap")

    resolved_roles: list[tuple[str, Path, Path]] = []
    for option, relative in lexical_roles:
        try:
            resolved = (root / relative).resolve()
            resolved.relative_to(root)
        except ValueError:
            issues.append(f"root/symlink 탈출: {option}={relative.as_posix()}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(
                f"source path resolve 불능: {option}={relative.as_posix()} ({exc})"
            )
            continue
        resolved_roles.append((option, relative, resolved))
    for index, (left_role, left_rel, left_resolved) in enumerate(resolved_roles):
        for right_role, right_rel, right_resolved in resolved_roles[index + 1 :]:
            if left_resolved != right_resolved:
                continue
            if left_role == right_role == "--registrar-module" and left_rel == right_rel:
                continue
            issues.append(
                "선택 source가 같은 resolved path를 중복 지정함: "
                f"{left_rel}, {right_rel}"
            )

    if issues:
        raise UsageError("; ".join(issues))
    return Config(
        root=root,
        profile=profile,
        scope=scope,
        api_module=api_module,
        urlconf_module=urlconf_module,
        registrar_modules=registrar_modules,
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
        raise UsageError(f"production inventory 탐색 불능: {'; '.join(sorted(walk_errors))}")
    return tuple(sorted(paths, key=Path.as_posix))


def _has_git_marker(root: Path) -> bool:
    for directory in (root, *root.parents):
        marker = directory / ".git"
        try:
            marker_mode = marker.stat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise UsageError(f"Git marker 접근 불능: {marker} ({exc})") from exc
        if stat.S_ISDIR(marker_mode) or stat.S_ISREG(marker_mode):
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

    try:
        top_level = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
        raise UsageError(f"Git worktree root 분석 불능: {exc}") from exc
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


def _selected_sources(
    config: Config, inventory: CodeInventory
) -> dict[Path, ParsedSource]:
    selected = [Path(config.api_module)] if config.api_module else []
    if config.urlconf_module:
        selected.append(Path(config.urlconf_module))
    selected.extend(Path(raw) for raw in config.registrar_modules)
    inventory_paths = set(inventory.relative_paths)
    issues: list[str] = []
    parsed: dict[Path, ParsedSource] = {}
    resolved_paths: dict[Path, Path] = {}
    for relative_path in sorted(set(selected), key=Path.as_posix):
        if relative_path not in inventory_paths:
            issues.append(f"선택 source가 production inventory에 없음: {relative_path}")
        lexical_path = config.root / relative_path
        try:
            file_path = lexical_path.resolve()
            file_path.relative_to(config.root)
        except ValueError:
            issues.append(f"production source root/symlink 탈출: {relative_path}")
            continue
        except (OSError, RuntimeError) as exc:
            issues.append(f"production source resolve 불능: {relative_path} ({exc})")
            continue
        previous = resolved_paths.get(file_path)
        if previous is not None:
            issues.append(f"production source resolved path 중복: {previous}, {relative_path}")
            continue
        resolved_paths[file_path] = relative_path
        try:
            if not file_path.is_file():
                issues.append(f"production source 없음: {relative_path}")
                continue
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=relative_path.as_posix())
        except (OSError, UnicodeError, SyntaxError) as exc:
            issues.append(f"production source 분석 불능: {relative_path} ({exc})")
            continue
        parsed[relative_path] = ParsedSource(relative_path, source, tree)
    if issues:
        raise UsageError("; ".join(sorted(set(issues))))
    return parsed


def _git_path_is_touched(git_root: Path, file_path: Path) -> bool:
    try:
        git_relative = file_path.relative_to(git_root)
    except ValueError as exc:
        raise UsageError(f"touched source가 Git root 밖임: {file_path}") from exc
    try:
        tracked = subprocess.run(
            ["git", "-C", str(git_root), "ls-files", "--error-unmatch", "--", git_relative.as_posix()],
            capture_output=True,
            check=False,
        )
        if tracked.returncode != 0:
            return True
        head = subprocess.run(
            ["git", "-C", str(git_root), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            check=False,
        )
        if head.returncode != 0:
            return True
        changed = subprocess.run(
            ["git", "-C", str(git_root), "diff", "--quiet", "HEAD", "--", git_relative.as_posix()],
            capture_output=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UsageError(f"touched source 비교 불능: {git_relative} ({exc})") from exc
    if changed.returncode not in {0, 1}:
        detail = os.fsdecode(changed.stderr).strip() or os.fsdecode(changed.stdout).strip()
        raise UsageError(f"touched source 비교 불능: {git_relative} ({detail})")
    return changed.returncode == 1


def _git_tree_has_tracked_changes(git_root: Path, directory: Path) -> bool:
    """HEAD 대비 디렉터리 변경 — 현재 inventory에서 사라진 staged deletion도 포함."""
    try:
        git_relative = directory.relative_to(git_root)
    except ValueError as exc:
        raise UsageError(f"touched directory가 Git root 밖임: {directory}") from exc
    try:
        head = subprocess.run(
            ["git", "-C", str(git_root), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            check=False,
        )
        if head.returncode != 0:
            return True
        changed = subprocess.run(
            ["git", "-C", str(git_root), "diff", "--quiet", "HEAD", "--", git_relative.as_posix()],
            capture_output=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UsageError(f"touched directory 비교 불능: {git_relative} ({exc})") from exc
    if changed.returncode not in {0, 1}:
        detail = os.fsdecode(changed.stderr).strip() or os.fsdecode(changed.stdout).strip()
        raise UsageError(f"touched directory 비교 불능: {git_relative} ({detail})")
    return changed.returncode == 1


def _path_is_under(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _filtered_di_findings(root: Path, inventory: CodeInventory) -> list[str]:
    eligible = set(inventory.relative_paths)
    findings: list[str] = []
    for bc in _find_bc_dirs(root):
        if not _has_any_layer(bc):
            continue
        bc_relative = bc.relative_to(root)
        bc_paths = sorted(
            (path for path in eligible if _path_is_under(path, bc_relative)),
            key=Path.as_posix,
        )
        if inventory.git_root is not None:
            current_path_touched = any(
                _git_path_is_touched(inventory.git_root, root / path) for path in bc_paths
            )
            tracked_tree_changed = _git_tree_has_tracked_changes(
                inventory.git_root, root / bc_relative
            )
            if not current_path_touched and not tracked_tree_changed:
                continue

        issues: list[str] = []
        composition_relative = bc_relative / COMPOSITION_DIR
        payload = sorted(
            path.name
            for path in bc_paths
            if _path_is_under(path, composition_relative)
            and path.name != "__init__.py"
            and (root / path).is_file()
        )
        if payload:
            issues.append(
                f"{COMPOSITION_DIR}/ 폴더에 배선 코드({', '.join(payload[:3])}) — DI 조립은 "
                f"BC 루트 단일 파일 `{COMPOSITION_FILE}`가 소유(폴더로 분열 금지)"
            )

        for path in bc_paths:
            if path.name != COMPOSITION_FILE or not (root / path).is_file():
                continue
            local = path.relative_to(bc_relative)
            if _path_is_under(path, composition_relative) or len(local.parts) == 1:
                continue
            issues.append(
                f"{local.as_posix()} — `{COMPOSITION_FILE}`는 BC 루트"
                f"(`<app>/{COMPOSITION_FILE}`)가 소유, 계층/하위 폴더에 두지 않는다"
            )

        application_relative = bc_relative / "application_layer"
        needs_root = any(
            _path_is_under(path, application_relative)
            and path.name != "__init__.py"
            and "dto" not in path.relative_to(application_relative).parts
            and (root / path).is_file()
            for path in bc_paths
        )
        canonical_root = root / bc_relative / COMPOSITION_FILE
        if needs_root and not canonical_root.is_file():
            issues.insert(
                0,
                f"`{COMPOSITION_FILE}` 부재 — application 로직(command/query/service 등)을 가진 BC는 "
                f"DI 조립을 BC 루트 단일 파일 `{COMPOSITION_FILE}`가 소유한다(배선을 `di/`·`wiring/`·"
                f"라우터·config 에 두지 말고 정본 파일을 만들어 `build_<usecase>_command()` 팩토리를 둬라)",
            )
        findings.extend(f"  - {bc_relative}: {issue}" for issue in issues)
    return findings


def _module_name(relative_path: Path) -> str:
    return ".".join(relative_path.with_suffix("").parts)


def _expression_dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _expression_dotted_name(node.value)
        if owner is not None:
            return f"{owner}.{node.attr}"
    return None


def _target_names(target: ast.AST) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, ast.Attribute):
        dotted = _expression_dotted_name(target)
        return {dotted.split(".", 1)[0]} if dotted is not None else set()
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for item in target.elts for name in _target_names(item)}
    return set()


def _statement_bound_names(node: ast.stmt) -> set[str]:
    if isinstance(node, ast.Import):
        return {alias.asname or alias.name.split(".", 1)[0] for alias in node.names}
    if isinstance(node, ast.ImportFrom):
        return {
            alias.asname or alias.name for alias in node.names if alias.name != "*"
        }
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, ast.Assign):
        return {name for target in node.targets for name in _target_names(target)}
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return _target_names(node.target)
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _target_names(node.target) | {
            name
            for statement in (*node.body, *node.orelse)
            for name in _statement_bound_names(statement)
        }
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return {
            name
            for item in node.items
            if item.optional_vars is not None
            for name in _target_names(item.optional_vars)
        } | {
            name for statement in node.body for name in _statement_bound_names(statement)
        }
    if isinstance(node, (ast.If, ast.While)):
        return {
            name
            for statement in (*node.body, *node.orelse)
            for name in _statement_bound_names(statement)
        }
    if isinstance(node, ast.Try):
        statements = [*node.body, *node.orelse, *node.finalbody]
        names = {
            name for statement in statements for name in _statement_bound_names(statement)
        }
        for handler in node.handlers:
            if handler.name:
                names.add(handler.name)
            for statement in handler.body:
                names.update(_statement_bound_names(statement))
        return names
    if isinstance(node, ast.Delete):
        return {name for target in node.targets for name in _target_names(target)}
    return set()


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


def _import_state(
    parsed: ParsedSource,
) -> tuple[dict[int, dict[str, str]], list[ImportFact], dict[str, set[str]]]:
    bindings: dict[str, str] = {}
    before: dict[int, dict[str, str]] = {}
    facts: list[ImportFact] = []
    historical: dict[str, set[str]] = {}
    for node in parsed.tree.body:
        before[id(node)] = dict(bindings)
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                binding = alias.name if alias.asname else local
                bindings[local] = binding
                historical.setdefault(local, set()).add(binding)
                facts.append(
                    ImportFact(alias.name, alias.name, local, binding, node.lineno)
                )
            continue
        if isinstance(node, ast.ImportFrom):
            module = _absolute_from_module(parsed.relative_path, node)
            if module is not None:
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name
                    full_path = f"{module}.{alias.name}"
                    bindings[local] = full_path
                    historical.setdefault(local, set()).add(full_path)
                    facts.append(
                        ImportFact(module, full_path, local, full_path, node.lineno)
                    )
                continue
        for name in _statement_bound_names(node):
            bindings.pop(name, None)
    return before, facts, historical


def _all_import_facts(parsed: ParsedSource) -> list[ImportFact]:
    facts: list[ImportFact] = []
    for node in ast.walk(parsed.tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                binding = alias.name if alias.asname else local
                facts.append(ImportFact(alias.name, alias.name, local, binding, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = _absolute_from_module(parsed.relative_path, node)
            if module is None:
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                full_path = f"{module}.{alias.name}"
                facts.append(ImportFact(module, full_path, local, full_path, node.lineno))
    return facts


def _resolve_imported_expression(
    node: ast.AST, bindings: dict[str, str]
) -> str | None:
    dotted = _expression_dotted_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    imported = bindings.get(first)
    if imported is None:
        return None
    return ".".join((imported, *rest))


def _fact_covers(fact: ImportFact, target: str) -> bool:
    target_module, _, _ = target.rpartition(".")
    return target == fact.full_path or target_module == fact.full_path


def _assignment_target_names(target: ast.AST) -> list[str | None]:
    if isinstance(target, (ast.Tuple, ast.List)):
        return [
            name for element in target.elts for name in _assignment_target_names(element)
        ]
    return [_expression_dotted_name(target)]


def _required_root_api_object(parsed: ParsedSource) -> str:
    bindings_before, _, _ = _import_state(parsed)
    assigned_objects: set[str] = set()
    constructor_events = 0
    for node in parsed.tree.body:
        value: ast.AST | None = None
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            value = node.value
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            value = node.value
            targets = [node.target]
        target_names = [
            name
            for target in targets
            for name in _assignment_target_names(target)
            if name is not None
        ]
        assigned_objects.difference_update(_statement_bound_names(node))
        assigned_objects.difference_update(target_names)
        if not isinstance(value, ast.Call):
            continue
        constructor = _resolve_imported_expression(
            value.func, bindings_before.get(id(node), {})
        )
        if constructor not in ROOT_API_CONSTRUCTORS:
            continue
        constructor_events += 1
        assigned_objects.update(target_names)
    if constructor_events != 1 or len(assigned_objects) != 1:
        raise UsageError(
            "selected API object correspondence 분석 불능: proven Ninja API "
            "constructor event와 최종 object binding이 각각 정확히 하나여야 함 "
            f"(event {constructor_events}개, binding {len(assigned_objects)}개)"
        )
    return f"{_module_name(parsed.relative_path)}.{next(iter(assigned_objects))}"


def _parent_map(tree: ast.AST) -> dict[int, ast.AST]:
    return {
        id(child): parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }


def _top_statement(
    node: ast.AST, tree: ast.Module, parents: dict[int, ast.AST]
) -> ast.stmt | None:
    current = node
    while id(current) in parents:
        parent = parents[id(current)]
        if parent is tree:
            return current if isinstance(current, ast.stmt) else None
        current = parent
    return None


def _is_module_direct_call(
    call: ast.Call, tree: ast.Module, parents: dict[int, ast.AST]
) -> bool:
    parent = parents.get(id(call))
    return (
        isinstance(parent, ast.Expr)
        and parent.value is call
        and parents.get(id(parent)) is tree
    )


def _canonical_lexical_owner(
    call: ast.Call,
    canonical: ast.FunctionDef,
    tree: ast.Module,
    parents: dict[int, ast.AST],
) -> bool:
    current: ast.AST = call
    owners: list[ast.AST] = []
    special_expression = False
    while id(current) in parents:
        parent = parents[id(current)]
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if current in parent.body:
                owners.append(parent)
            else:
                special_expression = True
        elif isinstance(parent, ast.Lambda):
            owners.append(parent)
        current = parent
        if current is tree:
            break
    return not special_expression and owners == [canonical]


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


def _direct_registration_calls(parsed: ParsedSource) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(parsed.tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "register_controllers"
    ]


def _bare_registration_decorators(parsed: ParsedSource) -> list[ast.Attribute]:
    decorators: list[ast.Attribute] = []
    for node in ast.walk(parsed.tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        decorators.extend(
            decorator
            for decorator in node.decorator_list
            if isinstance(decorator, ast.Attribute)
            and decorator.attr == "register_controllers"
        )
    return decorators


def _registrar_spec(relative_path: Path) -> RegistrarSpec:
    parts = relative_path.parts
    if (
        len(parts) != 4
        or parts[0] != "application"
        or parts[2:] != ("presentation_layer", "registrar.py")
        or not parts[1].isidentifier()
    ):
        raise UsageError(
            "canonical registrar placement 분석 불능: "
            f"{relative_path} (application/<bc>/presentation_layer/registrar.py 필요)"
        )
    bc = parts[1]
    function_name = f"register_{bc}_api"
    return RegistrarSpec(
        relative_path, bc, function_name, f"{_module_name(relative_path)}.{function_name}"
    )


def _analyze_registrar(
    parsed: ParsedSource,
    spec: RegistrarSpec,
    selected_api_module: str,
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    facts = _all_import_facts(parsed)
    for fact in facts:
        if (
            fact.module == selected_api_module
            or fact.module.startswith(f"{selected_api_module}.")
            or fact.full_path == selected_api_module
            or fact.full_path.startswith(f"{selected_api_module}.")
        ):
            node = next(
                (item for item in ast.walk(parsed.tree) if getattr(item, "lineno", None) == fact.lineno),
                parsed.tree,
            )
            _append_finding(findings, seen, parsed, node, "registrar imports selected project API")

    public_functions = [
        node
        for node in parsed.tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    ]
    canonical_nodes = [node for node in public_functions if node.name == spec.function_name]
    for node in public_functions:
        if node.name != spec.function_name:
            _append_finding(
                findings, seen, parsed, node, "additional public registrar function"
            )
    canonical: ast.FunctionDef | None = None
    if len(canonical_nodes) != 1 or not isinstance(canonical_nodes[0], ast.FunctionDef):
        anchor: ast.AST = canonical_nodes[0] if canonical_nodes else parsed.tree
        _append_finding(
            findings,
            seen,
            parsed,
            anchor,
            f"exactly one sync {spec.function_name} function required",
        )
    else:
        canonical = canonical_nodes[0]

    parents = _parent_map(parsed.tree)
    allowed_calls: list[ast.Call] = []
    parameter_name: str | None = None
    if canonical is not None:
        arguments = canonical.args
        positional = [*arguments.posonlyargs, *arguments.args]
        valid_signature = (
            len(positional) == 1
            and not arguments.defaults
            and not arguments.kwonlyargs
            and arguments.vararg is None
            and arguments.kwarg is None
        )
        if valid_signature:
            parameter_name = positional[0].arg
        else:
            _append_finding(
                findings, seen, parsed, canonical, "registrar signature must be one required positional parameter"
            )

    for call in _direct_registration_calls(parsed):
        direct_owner = _expression_dotted_name(call.func.value)
        allowed = (
            canonical is not None
            and parameter_name is not None
            and direct_owner == parameter_name
            and _canonical_lexical_owner(call, canonical, parsed.tree, parents)
        )
        if allowed:
            allowed_calls.append(call)
        else:
            _append_finding(
                findings, seen, parsed, call, "register_controllers outside canonical registrar owner"
            )
    for decorator in _bare_registration_decorators(parsed):
        _append_finding(
            findings, seen, parsed, decorator, "register_controllers decorator side effect"
        )
    if canonical is not None and parameter_name is not None and not allowed_calls:
        _append_finding(
            findings, seen, parsed, canonical, "canonical registrar has no direct register_controllers call"
        )


def _previous_import_resolves(
    node: ast.AST, facts: list[ImportFact], expected: str, before_line: int
) -> bool:
    dotted = _expression_dotted_name(node)
    if dotted is None:
        return False
    first, *rest = dotted.split(".")
    return any(
        fact.local_name == first
        and fact.lineno < before_line
        and ".".join((fact.binding, *rest)) == expected
        for fact in facts
    )


def _analyze_urlconf(
    parsed: ParsedSource,
    specs: list[RegistrarSpec],
    selected_api_object: str,
    analysis: list[str],
    findings: list[Finding],
    seen: set[tuple[Path, int, str]],
) -> None:
    before, facts, _ = _import_state(parsed)
    required = [selected_api_object, *(spec.full_path for spec in specs)]
    for target in required:
        if not any(_fact_covers(fact, target) for fact in facts):
            analysis.append(f"URLconf required import provenance 분석 불능: {target}")

    parents = _parent_map(parsed.tree)
    events: dict[str, list[ast.Call]] = {spec.full_path: [] for spec in specs}
    expected_paths = set(events)
    for call in (node for node in ast.walk(parsed.tree) if isinstance(node, ast.Call)):
        top = _top_statement(call, parsed.tree, parents)
        bindings = before.get(id(top), {}) if top is not None else {}
        resolved = _resolve_imported_expression(call.func, bindings)
        if resolved not in expected_paths:
            for expected in expected_paths:
                if _previous_import_resolves(call.func, facts, expected, call.lineno):
                    analysis.append(
                        f"URLconf registrar provenance shadow/rebinding 분석 불능: {expected}:{call.lineno}"
                    )
            continue
        if not _is_module_direct_call(call, parsed.tree, parents):
            _append_finding(
                findings, seen, parsed, call, "registrar call must be a module-level direct event"
            )
            continue
        events[resolved].append(call)
        if len(call.args) != 1 or call.keywords or isinstance(call.args[0], ast.Starred):
            _append_finding(
                findings, seen, parsed, call, "registrar URLconf call has wrong arity"
            )
            continue
        resolved_argument = _resolve_imported_expression(call.args[0], bindings)
        if resolved_argument != selected_api_object:
            analysis.append(
                "URLconf registrar-call API object identity 분석 불능: "
                f"{resolved}:{call.lineno}"
            )

    for spec in specs:
        count = len(events[spec.full_path])
        if count != 1:
            anchor: ast.AST = events[spec.full_path][0] if events[spec.full_path] else parsed.tree
            _append_finding(
                findings,
                seen,
                parsed,
                anchor,
                f"{spec.function_name} must be called exactly once (actual {count})",
            )


def _composition_semantics(
    config: Config, parsed: dict[Path, ParsedSource]
) -> tuple[list[str], list[Finding]]:
    analysis: list[str] = []
    findings: list[Finding] = []
    seen: set[tuple[Path, int, str]] = set()
    specs: list[RegistrarSpec] = []
    for raw in config.registrar_modules:
        try:
            specs.append(_registrar_spec(Path(raw)))
        except UsageError as exc:
            analysis.append(str(exc))

    api_path = Path(config.api_module or "")
    api_source = parsed.get(api_path)
    selected_api_object: str | None = None
    if api_source is not None:
        try:
            selected_api_object = _required_root_api_object(api_source)
        except UsageError as exc:
            analysis.append(str(exc))
        for call in _direct_registration_calls(api_source):
            _append_finding(
                findings, seen, api_source, call, "register_controllers outside canonical registrar owner"
            )
        for decorator in _bare_registration_decorators(api_source):
            _append_finding(
                findings, seen, api_source, decorator, "register_controllers decorator side effect"
            )

    selected_api_module = _module_name(api_path)
    for spec in specs:
        source = parsed.get(spec.relative_path)
        if source is not None:
            _analyze_registrar(
                source, spec, selected_api_module, findings, seen
            )

    urlconf = parsed.get(Path(config.urlconf_module or ""))
    if urlconf is not None:
        for call in _direct_registration_calls(urlconf):
            _append_finding(
                findings, seen, urlconf, call, "register_controllers outside canonical registrar owner"
            )
        for decorator in _bare_registration_decorators(urlconf):
            _append_finding(
                findings, seen, urlconf, decorator, "register_controllers decorator side effect"
            )
        if selected_api_object is not None and len(specs) == len(config.registrar_modules):
            _analyze_urlconf(
                urlconf, specs, selected_api_object, analysis, findings, seen
            )
    return sorted(set(analysis)), sorted(
        findings, key=lambda item: (item.relative_path.as_posix(), item.lineno, item.category)
    )


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
        inventory = _code_inventory(config.root)
        parsed: dict[Path, ParsedSource] = {}
        if config.profile in {"dddjango-code-json", "preserve-established"}:
            parsed = _selected_sources(config, inventory)
        composition_findings: list[Finding] = []
        if config.profile == "dddjango-code-json":
            analysis, composition_findings = _composition_semantics(config, parsed)
            if analysis:
                raise UsageError("; ".join(analysis))
        di_findings = _filtered_di_findings(config.root, inventory)
    except UsageError as exc:
        print(f"[check-composition-root] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:  # argparse --help
        return int(exc.code)

    if composition_findings or di_findings:
        print(
            "[check-composition-root] BLOCKER — DI/API 조립 소유권 또는 registrar/URLconf "
            "composition 계약 위반:"
        )
        for finding in composition_findings:
            print(finding.render())
        for finding in di_findings:
            print(finding)
        if composition_findings:
            print(
                "  API 근거: implementation-django-ninja §2.2·discipline-houserules §1. "
                "각 BC의 canonical `presentation_layer/registrar.py`가 "
                "`register_<bc>_api(api)` 안에서만 controller를 등록하고, 선택 URLconf가 "
                "선택 API object를 각 registrar에 정확히 한 번 전달한다. 위 finding의 "
                "signature/provenance/owner/count를 그 직접 계약에 맞춰라."
            )
        if di_findings:
            print(
            "  근거: discipline-houserules §0(트리·파일표). DI 조립은 BC 루트 "
            "`application/<app>/composition_root.py` 단일 파일이 소유하고, presentation은 "
            "`build_<usecase>_command()` 팩토리를 매요청 호출만 한다 — feature별 `composition/` "
            "폴더로 쪼개(루트 분열)거나 계층 하위에 묻지 않는다(operation 본문에서 "
            "`Django…Repository()`/`…Adapter()`를 직접 생성하지 않는 Q-7의 짝). `composition/` "
            "폴더의 provider들을 BC 루트 `composition_root.py` 한 파일로 합치거나, 묻힌 "
            "`composition_root.py`를 BC 루트로 올려라. application 로직(command/query/service 등)을 "
            "가졌는데 정본이 아예 없으면(부재) BC 루트에 `composition_root.py`를 만들어 "
            "`build_<usecase>_command()` 팩토리를 둬라(데이터소스 BC는 해당 없음)."
            )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
