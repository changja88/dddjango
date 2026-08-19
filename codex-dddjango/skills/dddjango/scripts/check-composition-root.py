#!/usr/bin/env python3
"""dddjango 컴포지션 루트(DI 배선) 위치 결정적 백스톱 (discipline-houserules §0 집행).

표준 트리에서 DI 조립(컴포지션 루트)은 BC 루트의 `composition_root/`(결선은 `dependency_wiring.py`
— 트리 2~4행·#84·#85)가 소유한다(정본). driving 층은 `build_<use_case>()` 팩토리를
매요청 호출만 하고, operation 본문에서 `Django…Repository()`/`…Adapter()`를 직접 생성하지
않는다(Q-7). 이 백스톱의 DI 레인은 정본 밖 구조 변종 중 **단일 파일 `composition_root.py`
모양**만 차단한다(#497 «파일이 아니라 폴더» — tree-revision-spec): 어디에 있든 트리에 없는
모양이고, 폴더 부재 상태라 tree 레인이 못 닿는 사건이다. 한때 이 레인이 함께 잡던 두 변종은
check-layer-skeleton 소유로 이관해 여기서는 검사·방출하지 않는다(귀속 매핑표 v2 §3.2 —
이중 계수 제거·소유자 실발화 실증 완료):
  - off-tree `composition/` 폴더 = #81 «BC 루트 바로 아래 일곱 가지만» 사건.
  - application 로직 보유 BC 의 `composition_root/` 부재 = #488 «고정 이름 칸» 사건.

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
     기존 커밋된 채 안 건드린 BC는 존중(§1.1) → 건너뜀.
  위 셋이 참인 BC에서(정본 = BC 루트 «폴더» `composition_root/` — 결선은 `dependency_wiring.py`,
  트리 2~4행):
    - `composition_root.py` «단일 파일» 모양은 어디에 있든 blocker(#497) — 그 모양 자체가 트리에
      없다. test 경로·off-tree `composition/` 안의 것(#81 사건의 일부 — layer-skeleton 소유)은 면제.
      정본이 존재하되 *비어 있고 실배선이 딴 곳에* fold 된 알리바이는 형태로 못 가르므로
      discipline-reviewer 의미 레인 몫이다.

명시적 `dddjango-code-json` lane은 선택 API object, canonical BC registrar, project URLconf의
직접 import provenance와 exactly-once 호출 관계를 함께 검사한다. preserve/auto에서는 이 의미
검사를 적용하지 않되, preserve가 공급한 source selector의 일반 경로·inventory·parse 계약은 검증한다.

사용법: check-composition-root.py [TARGET_DIR] [--error-profile PROFILE ...]
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 방출은 공용 ordered emitter(emit_all) 경유 — stdout 위반 라인 순서와
레코드 순서가 같고, 라인은 레코드 필드의 순수 함수다(출력 계약 v2). code-profile
category 의 #N 귀속/계약 잔류 판정과 tree↔code 동일 사건 선점 억제(#107·#108·#109·#440)는
귀속 매핑표 v2 가 정본이다(정본 문서명: 2026-08-19-ontology-t2-1-attribution-map).
"""
from __future__ import annotations

import argparse
import ast
import os
import stat
import subprocess
import sys

import checker_target
from findings import Candidates, ContractFindings, Findings, emit_all, lines
from dataclasses import dataclass
from pathlib import Path

try:
    import anchor_diff
    import standard_tree as _tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/anchor_diff.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

# code-profile 레인(URLconf/registrar)의 category 는 귀속 매핑표 v2 §3.1 에 따라 소유
# 규칙 문면의 술어에 포섭되면 "#N" violation 으로(#107·#108·#109·#111·#437·#440),
# 08-03 선행 계약 고유 술어면 rule=null + contract_ref 계약으로 방출한다. DI 레인의
# 단일 파일 모양은 #497 violation 이고, off-tree composition/(#81)·composition_root/
# 부재(#488)는 layer-skeleton 소유라 방출하지 않는다(타 소유자 이관 — §3.2).
CONTRACT_REF = "선행 계약(08-03 composition-root code-profile — URLconf/registrar) 소유"

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
CODE_SKIP_DIRS = {
    *SKIP_DIRS,
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "migrations",
    "generated",
}

# 4계층 — "이 BC가 4계층 앱인가"의 신호(하나라도 폴더면 검사 대상).
LAYER_DIRS = (
    "domain_layer", "application_layer", "driving_layer", "driven_layer",
)

TEST_DIR_NAMES = {"test", "tests"}

ERROR_PROFILES = {"auto", "dddjango-code-json", "preserve-established"}
ROOT_API_CONSTRUCTORS = {"ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"}

# 옛 단일 파일 모양(#497 검출용) — 정본은 `composition_root/` 폴더다. COMPOSITION_DIR 는
# off-tree `composition/`(#81 — layer-skeleton 소유) 안 파일을 단일 파일 검사에서 면제하는
# 경계 표지로만 남는다(그 폴더 자체는 여기서 검사하지 않는다 — 귀속 매핑표 v2 §3.2).
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
class Finding:
    relative_path: Path
    lineno: int
    category: str
    shown: str
    # 귀속 매핑표 v2 §3.1 — category 가 소유 규칙 문면의 술어에 포섭되면 "#N"(violation
    # 방출), 08-03 선행 계약 잔류면 None(계약 방출 · rule=null + contract_ref).
    rule: str | None = None
    # 위반 심볼(U17) — 생성 지점 node 가 안정 이름을 아는 경우만 채우고, 불명이면 null.
    symbol: str | None = None
    # #440 선점 억제 키 재료(귀속 매핑표 v2 §5 · MEDIATION-3 M1/R2 — 사건 식별자 =
    # registrar fn 이름). 방출 지점이 그 사건의 registrar 를 아는 경우(행8·9·10ⓐ)만
    # 채우고, 그 밖(행6ⓒ decorator 등)은 None — 키를 만들지 않는다.
    overlap_fn: str | None = None


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
    if namespace.anchor is not None and namespace.anchor_baseline:
        issues.append(f"--anchor 와 {anchor_diff.BASELINE_FLAG} 는 함께 전달할 수 없음")
    if namespace.anchor_debt_file is not None and namespace.anchor is None:
        issues.append(f"{anchor_diff.DEBT_FLAG} 는 --anchor 와 함께만 쓸 수 있음(차분 전용 빚 채널)")
    if namespace.anchor_baseline and anchor_diff.is_git_worktree(root):
        issues.append(
            f"{anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용 — git 저장소 TARGET 금지"
        )
    registrar_modules = tuple(namespace.registrar_module)
    if len(registrar_modules) != len(set(registrar_modules)):
        issues.append("반복 인자 중복: --registrar-module")
    if code_profile and not registrar_modules and not namespace.anchor_baseline:
        # anchor-baseline 모드에선 앵커 트리에 없는 registrar 가 걷혀 빈 집합이 정상이다.
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


def _filtered_di_findings(root: Path, inventory: CodeInventory) -> Findings:
    """DI 레인 — 단일 파일 `composition_root.py` 모양만 #497 violation 으로 방출한다.

    off-tree `composition/` 폴더(#81)·application 로직 BC 의 `composition_root/`
    부재(#488)는 check-layer-skeleton 소유라 여기서는 검사·방출하지 않는다
    (귀속 매핑표 v2 §3.2 — 타 소유자 이관·소유자 실발화 실증 완료). 라인·레코드는
    호출측 emit_all 이 한 순서로 방출한다(출력 계약 v2)."""
    eligible = set(inventory.relative_paths)
    findings: Findings = Findings(defer=True)
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

        composition_relative = bc_relative / COMPOSITION_DIR
        for path in bc_paths:
            if path.name != COMPOSITION_FILE or not (root / path).is_file():
                continue
            local = path.relative_to(bc_relative)
            if _path_is_under(path, composition_relative):
                continue  # off-tree composition/ 안 — #81 사건의 일부(layer-skeleton 소유)
            findings.add(
                "#497",
                bc_relative,
                f"{local.as_posix()} — 단일 파일 `{COMPOSITION_FILE}` 모양은 트리에 없다 — "
                "정본은 BC 루트 «폴더» `composition_root/`(트리 2행)다",
            )
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
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    if isinstance(target, (ast.Tuple, ast.List)):
        return {name for item in target.elts for name in _target_names(item)}
    return set()


def _direct_statement_bound_names(
    node: ast.stmt, *, annotations_evaluated: bool
) -> set[str]:
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
    if isinstance(node, ast.AnnAssign):
        return _target_names(node.target) if node.value is not None else set()
    if isinstance(node, ast.AugAssign):
        return _target_names(node.target)
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _target_names(node.target) | {
            name
            for statement in (*node.body, *node.orelse)
            for name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            )
        }
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return {
            name
            for item in node.items
            if item.optional_vars is not None
            for name in _target_names(item.optional_vars)
        } | {
            name
            for statement in node.body
            for name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            )
        }
    if isinstance(node, (ast.If, ast.While)):
        return {
            name
            for statement in (*node.body, *node.orelse)
            for name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            )
        }
    if isinstance(node, ast.Try):
        statements = [*node.body, *node.orelse, *node.finalbody]
        names = {
            name
            for statement in statements
            for name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            )
        }
        for handler in node.handlers:
            if handler.name:
                names.add(handler.name)
            for statement in handler.body:
                names.update(
                    _statement_bound_names(
                        statement, annotations_evaluated=annotations_evaluated
                    )
                )
        return names
    if isinstance(node, ast.Delete):
        return {name for target in node.targets for name in _target_names(target)}
    return set()


def _named_expression_bound_names(
    node: ast.stmt, *, annotations_evaluated: bool
) -> set[str]:
    """현재 module statement에서 실제 평가되는 `:=` 이름(중첩 lexical body 제외)."""
    names: set[str] = set()

    def visit(current: ast.AST) -> None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in current.decorator_list:
                visit(decorator)
            for default in (*current.args.defaults, *current.args.kw_defaults):
                if default is not None:
                    visit(default)
            if annotations_evaluated:
                arguments = [
                    *current.args.posonlyargs,
                    *current.args.args,
                    *current.args.kwonlyargs,
                ]
                if current.args.vararg is not None:
                    arguments.append(current.args.vararg)
                if current.args.kwarg is not None:
                    arguments.append(current.args.kwarg)
                for argument in arguments:
                    if argument.annotation is not None:
                        visit(argument.annotation)
                if current.returns is not None:
                    visit(current.returns)
            return
        if isinstance(current, ast.ClassDef):
            for expression in (*current.decorator_list, *current.bases):
                visit(expression)
            for keyword in current.keywords:
                visit(keyword.value)
            return
        if isinstance(current, ast.Lambda):
            for default in (*current.args.defaults, *current.args.kw_defaults):
                if default is not None:
                    visit(default)
            return
        if isinstance(current, ast.AnnAssign):
            visit(current.target)
            if annotations_evaluated:
                visit(current.annotation)
            if current.value is not None:
                visit(current.value)
            return
        if isinstance(current, ast.NamedExpr):
            names.update(_target_names(current.target))
        for child in ast.iter_child_nodes(current):
            visit(child)

    visit(node)
    return names


def _statement_bound_names(
    node: ast.stmt, *, annotations_evaluated: bool
) -> set[str]:
    return _direct_statement_bound_names(
        node, annotations_evaluated=annotations_evaluated
    ) | _named_expression_bound_names(
        node, annotations_evaluated=annotations_evaluated
    )


def _stored_attribute_targets(node: ast.stmt) -> list[ast.Attribute]:
    """현재 module statement 실행이 덮어쓰는 provable dotted target."""
    targets: list[ast.Attribute] = []

    def definitely_bound_names(statement: ast.stmt) -> set[str]:
        if isinstance(statement, ast.Import):
            return {
                alias.asname or alias.name.split(".", 1)[0]
                for alias in statement.names
            }
        if isinstance(statement, ast.ImportFrom):
            return {
                alias.asname or alias.name
                for alias in statement.names
                if alias.name != "*"
            }
        if isinstance(
            statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            return {statement.name}
        if isinstance(statement, ast.Assign):
            return {
                name
                for target in statement.targets
                for name in _target_names(target)
            }
        if isinstance(statement, ast.AnnAssign) and statement.value is not None:
            return _target_names(statement.target)
        if isinstance(statement, ast.AugAssign):
            return _target_names(statement.target)
        if isinstance(statement, (ast.With, ast.AsyncWith)):
            return {
                name
                for item in statement.items
                if item.optional_vars is not None
                for name in _target_names(item.optional_vars)
            }
        return set()

    def visit_block(statements: list[ast.stmt], bound_names: set[str]) -> None:
        for statement in statements:
            visit(statement, frozenset(bound_names))
            if isinstance(statement, ast.Delete):
                bound_names.difference_update(
                    name
                    for target in statement.targets
                    for name in _target_names(target)
                )
            else:
                bound_names.update(definitely_bound_names(statement))

    def visit(current: ast.AST, bound_names: frozenset[str]) -> None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        if isinstance(current, ast.ClassDef):
            visit_block(current.body, set())
            return
        if isinstance(current, (ast.If, ast.While)):
            visit(current.test, bound_names)
            visit_block(current.body, set(bound_names))
            visit_block(current.orelse, set(bound_names))
            return
        if isinstance(current, (ast.For, ast.AsyncFor)):
            visit(current.iter, bound_names)
            visit(current.target, bound_names)
            body_bound_names = set(bound_names) | _target_names(current.target)
            visit_block(current.body, body_bound_names)
            visit_block(current.orelse, set(bound_names))
            return
        if isinstance(current, (ast.With, ast.AsyncWith)):
            body_bound_names = set(bound_names)
            for item in current.items:
                visit(item.context_expr, bound_names)
                if item.optional_vars is not None:
                    visit(item.optional_vars, bound_names)
                    body_bound_names.update(_target_names(item.optional_vars))
            visit_block(current.body, body_bound_names)
            return
        if isinstance(current, ast.Try):
            visit_block(current.body, set(bound_names))
            visit_block(current.orelse, set(bound_names))
            visit_block(current.finalbody, set(bound_names))
            for handler in current.handlers:
                handler_bound_names = set(bound_names)
                if handler.name:
                    handler_bound_names.add(handler.name)
                visit_block(handler.body, handler_bound_names)
            return
        if isinstance(current, ast.AnnAssign) and current.value is None:
            return
        if isinstance(current, ast.Attribute) and isinstance(current.ctx, (ast.Store, ast.Del)):
            dotted = _expression_dotted_name(current)
            if dotted is not None and dotted.split(".", 1)[0] not in bound_names:
                targets.append(current)
            return
        for child in ast.iter_child_nodes(current):
            visit(child, bound_names)

    visit(node, frozenset())
    return targets


def _annotations_are_evaluated(tree: ast.Module) -> bool:
    return not any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


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
) -> tuple[dict[int, dict[str, str]], dict[int, frozenset[str]], list[ImportFact]]:
    bindings: dict[str, str] = {}
    before: dict[int, dict[str, str]] = {}
    invalidated_before: dict[int, frozenset[str]] = {}
    invalidated: set[str] = set()
    facts: list[ImportFact] = []
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    for node in parsed.tree.body:
        before[id(node)] = dict(bindings)
        invalidated_before[id(node)] = frozenset(invalidated)
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                binding = alias.name if alias.asname else local
                bindings[local] = binding
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
                    facts.append(
                        ImportFact(module, full_path, local, full_path, node.lineno)
                    )
                continue
        for target in _stored_attribute_targets(node):
            resolved = _resolve_imported_expression(target, bindings, frozenset(invalidated))
            if resolved is not None:
                invalidated.add(resolved)
        for name in _statement_bound_names(
            node, annotations_evaluated=annotations_evaluated
        ):
            bindings.pop(name, None)
    return before, invalidated_before, facts


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
    node: ast.AST,
    bindings: dict[str, str],
    invalidated: frozenset[str] = frozenset(),
) -> str | None:
    dotted = _expression_dotted_name(node)
    if dotted is None:
        return None
    first, *rest = dotted.split(".")
    imported = bindings.get(first)
    if imported is None:
        return None
    resolved = ".".join((imported, *rest))
    if any(resolved == path or resolved.startswith(f"{path}.") for path in invalidated):
        return None
    return resolved


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
    bindings_before, invalidated_before, _ = _import_state(parsed)
    annotations_evaluated = _annotations_are_evaluated(parsed.tree)
    assigned_objects: set[str] = set()
    local_root_subclasses: set[str] = set()
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
        bound_names = _statement_bound_names(
            node, annotations_evaluated=annotations_evaluated
        )
        assigned_objects.difference_update(bound_names)
        assigned_objects.difference_update(target_names)
        # 같은 모듈에서 ROOT_API_CONSTRUCTORS 를 직접(또는 인정 사슬로) 상속해 정의한
        # 클래스의 생성도 proven constructor event 다 — provenance 사슬이 모듈 안에서
        # 닫힌다. 동명 재정의·침범은 인정을 취소한다(닫힌 허용 목록 규율 유지).
        # (2026-08-15 S3-r2′ 실증: 중앙 api.py 의 `api = BroccoliNinjaAPI(...)` 가
        #  event 0 으로 분석 불능 — subclass 정의 자체의 시비는 #437 이 따로 판정한다.)
        local_root_subclasses.difference_update(bound_names)
        local_root_subclasses.difference_update(target_names)
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                resolved_base = _resolve_imported_expression(
                    base,
                    bindings_before.get(id(node), {}),
                    invalidated_before.get(id(node), frozenset()),
                )
                if resolved_base in ROOT_API_CONSTRUCTORS or (
                    resolved_base is None
                    and isinstance(base, ast.Name)
                    and base.id in local_root_subclasses
                ):
                    local_root_subclasses.add(node.name)
                    break
        if not isinstance(value, ast.Call):
            continue
        constructor = _resolve_imported_expression(
            value.func,
            bindings_before.get(id(node), {}),
            invalidated_before.get(id(node), frozenset()),
        )
        if constructor not in ROOT_API_CONSTRUCTORS and not (
            constructor is None
            and isinstance(value.func, ast.Name)
            and value.func.id in local_root_subclasses
        ):
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


def _registrar_parameter_states(
    function: ast.FunctionDef,
    parameter_name: str,
    *,
    annotations_evaluated: bool,
) -> dict[int, str]:
    """Incoming API parameter identity immediately before each direct call."""
    call_states: dict[int, str] = {}

    def record_calls(node: ast.AST, state: str) -> None:
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Attribute)
                and child.func.attr == "register_controllers"
            ):
                call_states[id(child)] = state

    def merge(*states: str) -> str:
        return states[0] if states and len(set(states)) == 1 else "ambiguous"

    def explicit_raise_states(
        statements: list[ast.stmt], incoming: str
    ) -> list[str]:
        """Parameter states at explicit raises; implicit exceptions stay unknown."""
        active = {incoming}
        raised: list[str] = []
        for statement in statements:
            if not active:
                break
            if isinstance(statement, ast.Raise):
                raised.extend(active)
                active.clear()
                continue
            if isinstance(statement, ast.If):
                next_active: set[str] = set()
                for state in active:
                    raised.extend(explicit_raise_states(statement.body, state))
                    raised.extend(explicit_raise_states(statement.orelse, state))
                    body_state = flow(statement.body, state)
                    else_state = flow(statement.orelse, state)
                    next_active.update((body_state, else_state))
                active = next_active
                continue
            if parameter_name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            ):
                active = {"rebound"}
        return raised

    def flow(statements: list[ast.stmt], incoming: str) -> str:
        state = incoming
        for statement in statements:
            if isinstance(statement, ast.If):
                record_calls(statement.test, state)
                body_state = flow(statement.body, state)
                else_state = flow(statement.orelse, state)
                state = merge(body_state, else_state)
                continue
            if isinstance(statement, ast.While):
                record_calls(statement.test, state)
                body_state = flow(statement.body, state)
                else_state = flow(statement.orelse, state)
                state = merge(state, body_state, else_state)
                continue
            if isinstance(statement, (ast.For, ast.AsyncFor)):
                record_calls(statement.iter, state)
                body_start = (
                    "rebound"
                    if parameter_name in _target_names(statement.target)
                    else state
                )
                body_state = flow(statement.body, body_start)
                else_state = flow(statement.orelse, merge(state, body_state))
                state = merge(state, body_state, else_state)
                continue
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                for item in statement.items:
                    record_calls(item.context_expr, state)
                    if (
                        item.optional_vars is not None
                        and parameter_name in _target_names(item.optional_vars)
                    ):
                        state = "rebound"
                state = flow(statement.body, state)
                continue
            if isinstance(statement, ast.Try):
                normal = flow(statement.orelse, flow(statement.body, state))
                outcomes = [normal]
                raised_states = explicit_raise_states(statement.body, state)
                handler_base = merge(*raised_states) if raised_states else state
                for handler in statement.handlers:
                    handler_state = (
                        "rebound"
                        if handler.name == parameter_name
                        else handler_base
                    )
                    outcomes.append(flow(handler.body, handler_state))
                state = flow(statement.finalbody, merge(*outcomes))
                continue
            record_calls(statement, state)
            if parameter_name in _statement_bound_names(
                statement, annotations_evaluated=annotations_evaluated
            ):
                state = "rebound"
        return state

    flow(function.body, "incoming")
    return call_states


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
    overlap_fn: str | None = None,
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
            overlap_fn=overlap_fn,
        )
    )


def _direct_registration_calls(parsed: ParsedSource) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(parsed.tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "register_controllers"
    ]


def _bare_registration_decorators(parsed: ParsedSource) -> list[tuple[ast.Attribute, bool]]:
    """bare `X.register_controllers` decorator 수집 — 장식된 정의가 함수 본문 안인지의
    discriminant 를 함께 돌려준다(귀속 매핑표 v2 §3.1 행6 분할: 모듈층 decorator 는
    import 시 부작용, 함수 내부 정의의 decorator 는 호출 시 평가라 세 규칙 문면의
    주어 밖·계약)."""
    decorators: list[tuple[ast.Attribute, bool]] = []

    def visit(node: ast.AST, in_function: bool) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            decorators.extend(
                (decorator, in_function)
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Attribute)
                and decorator.attr == "register_controllers"
            )
        nested: bool = in_function or isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        )
        for child in ast.iter_child_nodes(node):
            visit(child, nested)

    visit(parsed.tree, False)
    return decorators


def _registrar_spec(relative_path: Path) -> RegistrarSpec:
    parts = relative_path.parts
    if (
        len(parts) != 5
        or parts[0] != "application"
        or parts[2:] != ("driving_layer", "api", "api_router.py")
        or not parts[1].isidentifier()
    ):
        raise UsageError(
            "canonical registrar placement 분석 불능: "
            f"{relative_path} (application/<bc>/driving_layer/api/api_router.py 필요)"
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
    analysis: list[str],
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
            # #108 «전역 API 객체를 import 하지 않고 인자로 받는다» — 귀속 매핑표 v2 §3.1 행1.
            _append_finding(
                findings, seen, parsed, node,
                "registrar imports selected project API", rule="#108",
            )

    public_functions = [
        node
        for node in parsed.tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    ]
    canonical_nodes = [node for node in public_functions if node.name == spec.function_name]
    for node in public_functions:
        if node.name != spec.function_name:
            # #107 «등록 함수 하나만 갖는다» — 행2.
            _append_finding(
                findings, seen, parsed, node,
                "additional public registrar function", rule="#107",
            )
    canonical: ast.FunctionDef | None = None
    if len(canonical_nodes) != 1 or not isinstance(canonical_nodes[0], ast.FunctionDef):
        anchor: ast.AST = canonical_nodes[0] if canonical_nodes else parsed.tree
        # #107 — 부재·중복·async 전부 «하나만» 위반(행3).
        _append_finding(
            findings,
            seen,
            parsed,
            anchor,
            f"exactly one sync {spec.function_name} function required",
            rule="#107",
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
            # #107 — 문면이 시그니처를 축자로 적는다(«def register_<bc>_api(api)» · 행4).
            _append_finding(
                findings, seen, parsed, canonical,
                "registrar signature must be one required positional parameter",
                rule="#107",
            )

    parameter_states = (
        _registrar_parameter_states(
            canonical,
            parameter_name,
            annotations_evaluated=_annotations_are_evaluated(parsed.tree),
        )
        if canonical is not None and parameter_name is not None
        else {}
    )
    for call in _direct_registration_calls(parsed):
        direct_owner = _expression_dotted_name(call.func.value)
        parameter_state = parameter_states.get(id(call))
        inside_canonical = canonical is not None and _canonical_lexical_owner(
            call, canonical, parsed.tree, parents
        )
        allowed = (
            inside_canonical
            and parameter_name is not None
            and direct_owner == parameter_name
            and parameter_state == "incoming"
        )
        if allowed:
            allowed_calls.append(call)
        elif (
            inside_canonical
            and parameter_name is not None
            and direct_owner == parameter_name
            and parameter_state == "ambiguous"
        ):
            analysis.append(
                "canonical registrar API parameter provenance 분석 불능: "
                f"{spec.function_name}:{call.lineno}"
            )
        elif inside_canonical:
            # 행5ⓑ(U4 분할) — 함수 «안»이지만 receiver 가 incoming parameter 아님/
            # rebound: #109 문면 밖 술어라 08-03 계약 유지.
            _append_finding(
                findings, seen, parsed, call,
                "registrar call on wrong receiver or rebound parameter",
            )
        else:
            # 행5ⓐ — #109 «등록은 그 함수 안에서만 하고 module top-level 에서 부르지
            # 않는다(부작용 등록 금지)».
            _append_finding(
                findings, seen, parsed, call,
                "register_controllers outside canonical registrar owner", rule="#109",
            )
    for decorator, in_function in _bare_registration_decorators(parsed):
        if in_function:
            # 행6ⓓ(U5 분할) — 중첩 함수 정의의 decorator 는 세 문면 어느 주어도 아님 — 계약.
            _append_finding(
                findings, seen, parsed, decorator,
                "register_controllers decorator inside function body",
            )
        else:
            # 행6ⓐ — registrar 모듈층 decorator = import 시 부작용 등록(#109).
            _append_finding(
                findings, seen, parsed, decorator,
                "register_controllers decorator side effect", rule="#109",
            )
    if canonical is not None and parameter_name is not None and not allowed_calls:
        # #111 «…를 부르고 …뿐이다» — 직접 호출 부재는 «하는 일» 불이행(행7).
        _append_finding(
            findings, seen, parsed, canonical,
            "canonical registrar has no direct register_controllers call", rule="#111",
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
    before, invalidated_before, facts = _import_state(parsed)
    required = [selected_api_object, *(spec.full_path for spec in specs)]
    for target in required:
        if not any(_fact_covers(fact, target) for fact in facts):
            analysis.append(f"URLconf required import provenance 분석 불능: {target}")

    parents = _parent_map(parsed.tree)
    events: dict[str, list[ast.Call]] = {spec.full_path: [] for spec in specs}
    function_by_path: dict[str, str] = {
        spec.full_path: spec.function_name for spec in specs
    }
    expected_paths = set(events)
    for call in (node for node in ast.walk(parsed.tree) if isinstance(node, ast.Call)):
        top = _top_statement(call, parsed.tree, parents)
        bindings = before.get(id(top), {}) if top is not None else {}
        invalidated = (
            invalidated_before.get(id(top), frozenset()) if top is not None else frozenset()
        )
        resolved = _resolve_imported_expression(call.func, bindings, invalidated)
        if resolved not in expected_paths:
            for expected in expected_paths:
                if _previous_import_resolves(call.func, facts, expected, call.lineno):
                    analysis.append(
                        f"URLconf registrar provenance shadow/rebinding 분석 불능: {expected}:{call.lineno}"
                    )
            continue
        if not _is_module_direct_call(call, parsed.tree, parents):
            # #440 «명시적으로 부른다» — 조건부·간접 호출 위반(행8).
            _append_finding(
                findings, seen, parsed, call,
                "registrar call must be a module-level direct event", rule="#440",
                overlap_fn=function_by_path[resolved],
            )
            continue
        events[resolved].append(call)
        if len(call.args) != 1 or call.keywords or isinstance(call.args[0], ast.Starred):
            # #440 — 호출 형태 «register_<bc>_api(api)» 축자(행9).
            _append_finding(
                findings, seen, parsed, call,
                "registrar URLconf call has wrong arity", rule="#440",
                overlap_fn=function_by_path[resolved],
            )
            continue
        resolved_argument = _resolve_imported_expression(call.args[0], bindings, invalidated)
        if resolved_argument != selected_api_object:
            analysis.append(
                "URLconf registrar-call API object identity 분석 불능: "
                f"{resolved}:{call.lineno}"
            )

    for spec in specs:
        count = len(events[spec.full_path])
        if count == 0:
            # 행10ⓐ(U6 분할) — 0회는 #440 «각 BC 의 register_<bc>_api(api) 를 명시적으로
            # 부른다» 축자 포섭. category 에 대상 함수명을 남긴다(등록 함수별 사건이
            # 구분되어야 incident multiset 이 보존된다 — 출력 계약 v2 보존 표면).
            _append_finding(
                findings,
                seen,
                parsed,
                parsed.tree,
                f"registrar call missing: {spec.function_name}",
                rule="#440",
                overlap_fn=spec.function_name,
            )
        elif count > 1:
            # 행10ⓑ — «정확히 한 번»은 #440 문면이 아니라 08-03 계약 문면에만 있다(V6).
            _append_finding(
                findings,
                seen,
                parsed,
                events[spec.full_path][0],
                f"duplicate registrar call: {spec.function_name} (actual {count})",
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
            # 행5ⓐ — canonical 밖 파일의 등록 호출도 #109 «함수 안에서만» 위반.
            _append_finding(
                findings, seen, api_source, call,
                "register_controllers outside canonical registrar owner", rule="#109",
            )
        for decorator, in_function in _bare_registration_decorators(api_source):
            if in_function:
                _append_finding(
                    findings, seen, api_source, decorator,
                    "register_controllers decorator inside function body",
                )
            else:
                # 행6ⓑ — api.py 모듈층 사건의 주어는 #437 «닫힌 허용 목록».
                _append_finding(
                    findings, seen, api_source, decorator,
                    "register_controllers decorator side effect in project api module",
                    rule="#437",
                )

    selected_api_module = _module_name(api_path)
    for spec in specs:
        source = parsed.get(spec.relative_path)
        if source is not None:
            _analyze_registrar(
                source, spec, selected_api_module, analysis, findings, seen
            )

    urlconf = parsed.get(Path(config.urlconf_module or ""))
    if urlconf is not None:
        for call in _direct_registration_calls(urlconf):
            # 행5ⓐ — canonical 밖 파일의 등록 호출도 #109 «함수 안에서만» 위반.
            _append_finding(
                findings, seen, urlconf, call,
                "register_controllers outside canonical registrar owner", rule="#109",
            )
        for decorator, in_function in _bare_registration_decorators(urlconf):
            if in_function:
                _append_finding(
                    findings, seen, urlconf, decorator,
                    "register_controllers decorator inside function body",
                )
            else:
                # 행6ⓒ — URLconf 모듈층 사건의 주어는 #440 «라우터 등록만 한다».
                _append_finding(
                    findings, seen, urlconf, decorator,
                    "register_controllers decorator side effect in URLconf module",
                    rule="#440",
                )
        if selected_api_object is not None and len(specs) == len(config.registrar_modules):
            _analyze_urlconf(
                urlconf, specs, selected_api_object, analysis, findings, seen
            )
    return sorted(set(analysis)), sorted(
        findings, key=lambda item: (item.relative_path.as_posix(), item.lineno, item.category)
    )


# tree↔code 선점 억제 키의 rule 공간(귀속 매핑표 v2 §5 overlap 표 — CR 4행).
_OVERLAP_RULES: frozenset[str] = frozenset({"#107", "#108", "#109", "#440"})
# 양 레인 locator 가 rel:lineno 동축인 rule — discriminant = lineno.
_LINE_KEY_RULES: frozenset[str] = frozenset({"#108", "#109"})


def _code_overlap_keys(
    findings: list[Finding],
) -> frozenset[tuple[str, str, int | str | None]]:
    """code 레인 «실발화» finding → tree 선점 억제 키(귀속 매핑표 v2 §5 · M1/R2).

    파일 단위 활성이 아니라 사건 단위다 — code 가 실제 방출한 finding 만 키가 되고,
    tree 는 정확히 대응하는 엔트리만 억제한다(code 미발화 사건의 tree 위반은 잃지
    않는다). 키 판형 (rule, rel, discriminant):
      #108/#109 — 양 레인 locator 동축: discriminant = lineno.
      #107      — tree 는 파일 단위·code 는 행 단위: 파일×category 대응이라
                  discriminant = None(그 파일에서 #107 계열 사건(행2·3·4) 실발화
                  여부만 본다).
      #440      — 사건 식별자 = registrar fn 이름: discriminant = overlap_fn.
                  overlap_fn 미채움 #440(행6ⓒ decorator)은 대응 tree 사이트가 없어
                  키를 만들지 않는다.
    """
    keys: set[tuple[str, str, int | str | None]] = set()
    for finding in findings:
        if finding.rule not in _OVERLAP_RULES:
            continue
        rel: str = finding.relative_path.as_posix()
        if finding.rule in _LINE_KEY_RULES:
            keys.add((finding.rule, rel, finding.lineno))
        elif finding.rule == "#107":
            keys.add(("#107", rel, None))
        elif finding.overlap_fn is not None:
            keys.add(("#440", rel, finding.overlap_fn))
    return frozenset(keys)


# ── 표준 트리 슬라이스 — 트리 개정 명세 몫 18규칙 (트리 2~4·8·9·136·137행) ──
#
# 새 트리 모양(composition_root/ 폴더 · api/api_router.py · <project>/{api,urls}.py)에
# 대한 기계 규칙. 변종(단일 composition_root.py · off-tree composition/)은
# 위 V1~V3·registrar 검사가 담당한다.
#   #84/#497 composition_root/ 는 BC 루트의 «폴더»·결선 하나=파일 하나
#   #85/#86(ⓓ) dependency_wiring.py 는 build_* 팩토리만 · 조건/계산은 후보
#   #498/#500/#501 event_wiring.py 는 꽂기만(표 금지·이름 있는 최상단 함수만·DB 금지)
#   #101 BC 안쪽·composition_root 은 driving 층을 import 하지 않는다
#   #105/#112 api/ 직계 파일 둘뿐 · 등록 파일 이름은 api_router.py(접두 금지)
#   #107/#108/#109/#111 api_router.py 의 등록 함수 하나·전역 API import 금지·
#        top-level 부작용 등록 금지·등록 밖 일 금지
#   #437 <project>/api.py 닫힌 허용 목록 · #440/#441 <project>/urls.py 등록만
#   #511(ⓓ) api/ 2차 축 — 계약 소유(OAuth 콜백은 webhook/<provider>/) 후보
#
# tree↔code 동일 사건 선점 억제(귀속 매핑표 v2 §5 overlap · MEDIATION-3 M1/R2): code
# 레인이 «실발화한» finding 에서 사건 단위 키를 만들고(_code_overlap_keys — #108/#109
# = rel:lineno · #107 = 파일×category 대응 · #440 = URLconf×registrar fn 이름), 정확히
# 대응하는 tree 엔트리만 억제한다(정밀 레인이 이긴다 — 그 대상에 대해 겹치는 tree
# 술어만 선점 억제). code 가 포착하지 않는 사건(사설 함수·임의 import·spec 밖
# registrar 미호출·add_router 등)은 code-profile 활성 파일이라도 tree 단독 그대로
# 방출한다(#437 은 겹침 미등재 — 관찰 대상이라 억제하지 않는다).

_DRIVING_SEGMENTS = frozenset(
    {"driving_layer"}
)
_INNER_SEGMENTS = ("application_layer", "domain_layer", "driven_layer", "composition_root")
_WIRING_FILES = {"dependency_wiring.py", "event_wiring.py"}
_STDLIB_OK = {
    "__future__", "typing", "collections", "functools", "itertools", "dataclasses",
    "enum", "abc", "datetime", "decimal", "uuid", "logging",
}
_API_ROUTER_IMPORT_OK = _STDLIB_OK | {"django", "ninja", "application", "framework"}
_PROVIDERISH_TOKENS = ("oauth", "callback", "sso")


def _slice_imports(mod: ast.Module) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            out.extend((node.lineno, a.name) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.append((node.lineno, node.module))
    return out


def _slice_parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _check_dependency_wiring(f: Path, rel: Path, findings: Findings, candidates: Candidates) -> None:
    mod = _slice_parse(f)
    if mod is None:
        return
    for node in mod.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # docstring
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("build_"):
                findings.add(
                    "#85",
                    rel,
                    f"`{node.name}()` — dependency_wiring.py 에는 `build_<use_case>()` 팩토리만 온다(«만들기»와 «꽂기» 둘뿐)",
                )
            for sub in ast.walk(node):
                if isinstance(sub, (ast.If, ast.IfExp)):
                    candidates.add(
                        "#86",
                        f"{rel}:{sub.lineno}",
                        "결선 함수 안 조건문",
                        "이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다)?",
                    )
                    break
            continue
        findings.add(
            "#85",
            f"{rel}:{node.lineno}",
            "dependency_wiring.py 최상단에는 import 와 build_* 팩토리만 온다",
        )


def _check_event_wiring(f: Path, rel: Path, findings: Findings) -> None:
    mod = _slice_parse(f)
    if mod is None:
        return
    for node in ast.walk(mod):
        if isinstance(node, ast.Dict):
            findings.add(
                "#498",
                f"{rel}:{node.lineno}",
                "event_wiring.py 에서 표(dict)를 만들었다 — 표는 event_subscription/event_router.py 소유, 여기는 브로커에 «꽂는» 것만 한다",
            )
        elif isinstance(node, ast.Lambda):
            findings.add(
                "#500",
                f"{rel}:{node.lineno}",
                "구독으로 람다를 넘겼다 — 모듈 최상단 이름 있는 함수만(매번 다른 객체라 멱등이 깨진다)",
            )
        elif isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if nm == "partial":
                findings.add(
                    "#500",
                    f"{rel}:{node.lineno}",
                    "`functools.partial` 을 구독으로 넘겼다 — 모듈 최상단 이름 있는 함수만",
                )
        elif isinstance(node, ast.Attribute) and node.attr == "objects":
            findings.add(
                "#501",
                f"{rel}:{node.lineno}",
                "event_wiring.py 에서 DB 를 만졌다 — 모든 관리 명령에서 도는 자리다",
            )


def _check_composition_dir(bc: Path, bc_rel: Path, findings: Findings, candidates: Candidates) -> None:
    comp = bc / "composition_root"
    if not comp.is_dir():
        # 오배치(#84) — 층 폴더 안 composition_root/ 를 찾는다
        for layer in LAYER_DIRS:
            nested = bc / layer
            if not nested.is_dir():
                continue
            for p in nested.rglob("composition_root"):
                if p.is_dir():
                    findings.add(
                        "#84",
                        bc_rel / p.relative_to(bc),
                        "`composition_root/` 는 BC 루트에 둔다 — 네 층 폴더 어디에도 두지 않는다",
                    )
        return
    for p in sorted(comp.iterdir()):
        if p.name.startswith(".") or p.name == "__pycache__":
            continue
        if p.is_dir():
            findings.add(
                "#497",
                f"{bc_rel}/composition_root/{p.name}",
                "폴더 금지 — «결선 하나 = 파일 하나»(지금은 dependency_wiring.py 와 event_wiring.py 둘)",
            )
        elif p.suffix == ".py" and p.name != "__init__.py" and p.name not in _WIRING_FILES:
            findings.add(
                "#497",
                f"{bc_rel}/composition_root/{p.name}",
                "결선 파일은 dependency_wiring.py·event_wiring.py 둘이다",
            )
    dep = comp / "dependency_wiring.py"
    if dep.is_file():
        _check_dependency_wiring(dep, bc_rel / "composition_root/dependency_wiring.py", findings, candidates)
    ev = comp / "event_wiring.py"
    if ev.is_file():
        _check_event_wiring(ev, bc_rel / "composition_root/event_wiring.py", findings)


def _check_inner_driving_imports(bc: Path, bc_rel: Path, findings: Findings) -> None:
    for seg in _INNER_SEGMENTS:
        base = bc / seg
        files: list[Path] = []
        if base.is_dir():
            files = [p for p in base.rglob("*.py") if not (set(p.parts) & CODE_SKIP_DIRS) and "test" not in p.parts]
        elif seg == "composition_root" and (bc / "composition_root.py").is_file():
            files = [bc / "composition_root.py"]
        for f in files:
            mod = _slice_parse(f)
            if mod is None:
                continue
            for lineno, path_str in _slice_imports(mod):
                if set(path_str.split(".")) & _DRIVING_SEGMENTS:
                    findings.add(
                        "#101",
                        f"{bc_rel / f.relative_to(bc)}:{lineno}",
                        f"`{path_str}` — BC 안쪽과 composition_root 은 driving 층을 import 하지 않는다(예외 없음 · rd-2)",
                    )


def _check_api_dir(
    bc: Path,
    bc_rel: Path,
    findings: Findings,
    candidates: Candidates,
    code_keys: frozenset[tuple[str, str, int | str | None]],
) -> None:
    for driving_name in _DRIVING_SEGMENTS:
        api = bc / driving_name / "api"
        if not api.is_dir():
            continue
        api_rel = bc_rel / driving_name / "api"
        for p in sorted(api.iterdir()):
            if p.name.startswith(".") or p.name == "__pycache__":
                continue
            if p.is_file() and p.suffix == ".py":
                entry_rel: Path = api_rel / p.name
                if p.name != "api_router.py" and ("api_router" in p.name or p.name.endswith("_router.py")):
                    findings.add(
                        "#112",
                        entry_rel,
                        "등록 파일 이름은 `api_router.py` 다 — `<bounded_context>_` 접두를 붙이지 않는다",
                    )
                elif p.name not in ("api_router.py", "bc_error_schema.py", "__init__.py"):
                    findings.add(
                        "#105",
                        entry_rel,
                        "`api/` 직계 파일은 `api_router.py` 와 `bc_error_schema.py` 둘뿐이다",
                    )
            elif p.is_dir() and any(tok in p.name.lower() for tok in _PROVIDERISH_TOKENS):
                # ⓓ#511 확정 튜플(귀속 매핑표 v2 부속 A-3) — msg 신규 저작·question 은
                # «물음: » 접두 없이(공용 candidate 판형이 접두를 생성한다).
                dir_rel: Path = api_rel / p.name
                candidates.add(
                    "#511",
                    f"{dir_rel}/",
                    "외부 소유 계약 입구 후보(provider 성 디렉터리)",
                    "이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 `webhook/<provider>/` 자리다",
                )
        router = api / "api_router.py"
        if router.is_file():
            router_rel: Path = api_rel / "api_router.py"
            _check_api_router(
                router, router_rel, bc.name, findings, code_keys=code_keys
            )


def _check_api_router(
    f: Path,
    rel: Path,
    bc_name: str,
    findings: Findings,
    *,
    code_keys: frozenset[tuple[str, str, int | str | None]],
) -> None:
    """tree #107·#108·#109 사이트의 선점 억제는 code 레인 «실발화 사건 키»로만 한다
    (귀속 매핑표 v2 §5 · MEDIATION-3 M1/R2 — 파일 단위 활성 폐기): #108/#109 는
    (rule, rel, lineno) 동일 좌표 키, #107 은 code 가 이 파일에서 #107 계열 사건을
    실발화했을 때만 파일 단위 tree #107 억제. code 미발화 사건(사설 함수·임의
    import·add_router 등)의 tree 위반은 그대로 방출한다(#111 은 겹침 미등재라 항상
    그대로)."""
    mod = _slice_parse(f)
    if mod is None:
        return
    rel_key: str = rel.as_posix()
    file_107_covered: bool = ("#107", rel_key, None) in code_keys
    reg_fns = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    named = [n for n in reg_fns if n.name.startswith("register_") and n.name.endswith("_api")]
    if len(named) != 1 or len(reg_fns) != len(named):
        if not file_107_covered:
            findings.add(
                "#107",
                rel,
                f"`def register_{bc_name}_api(api)` 등록 함수 «하나»만 갖는다(지금 함수 {len(reg_fns)}개)",
            )
    elif len(named[0].args.args) != 1:
        if not file_107_covered:
            findings.add(
                "#107",
                rel,
                f"등록 함수는 전역 API 를 «인자 하나»로 받는다 — `register_{bc_name}_api(api)`",
            )
    for node in mod.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            fn = node.value.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if nm in ("register_controllers", "add_router"):
                if ("#109", rel_key, node.lineno) not in code_keys:
                    findings.add(
                        "#109",
                        f"{rel}:{node.lineno}",
                        "module top-level 등록 호출 — 등록은 `register_<bc>_api(api)` 함수 «안»에서만 한다(부작용 등록 금지)",
                    )
            else:
                findings.add(
                    "#111",
                    f"{rel}:{node.lineno}",
                    "api_router.py 의 일은 컨트롤러 import·`api.register_controllers(...)`·접두사/태그뿐이다",
                )
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.ClassDef)):
            findings.add(
                "#111",
                f"{rel}:{getattr(node, 'lineno', 0)}",
                "api_router.py 에 등록 밖 정의가 있다 — 컨트롤러 import 와 등록 함수만 둔다",
            )
    for lineno, path_str in _slice_imports(mod):
        top = path_str.split(".")[0]
        if top not in _API_ROUTER_IMPORT_OK and ("#108", rel_key, lineno) not in code_keys:
            findings.add(
                "#108",
                f"{rel}:{lineno}",
                f"`{path_str}` import — 전역 API 객체는 import 하지 않고 인자로 받는다(BC 가 프로젝트를 import 하지 않는다)",
            )


def _find_project_dirs(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(root.rglob("urls.py")):
        d = p.parent
        if set(d.parts) & CODE_SKIP_DIRS or "application" in d.parts:
            continue
        if (d / "settings").is_dir() or (d / "settings.py").is_file() or (d / "api.py").is_file():
            out.append(d)
    return out


def _check_project_api(f: Path, rel: Path, findings: Findings) -> None:
    mod = _slice_parse(f)
    if mod is None:
        return
    for lineno, path_str in _slice_imports(mod):
        if path_str.split(".")[0] == "application":
            findings.add(
                "#437",
                f"{rel}:{lineno}",
                f"`{path_str}` import — `<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다(BC import 금지)",
            )
    for node in mod.body:
        if isinstance(node, ast.ClassDef):
            findings.add(
                "#437",
                f"{rel}:{node.lineno}",
                f"`{node.name}` 정의 — ErrorSchema·예외 목록·매핑은 전부 위반이다(닫힌 허용 목록)",
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            deco_names = set()
            for d in node.decorator_list:
                fn = d.func if isinstance(d, ast.Call) else d
                deco_names.add(fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", ""))
            if "exception_handler" not in deco_names:
                findings.add(
                    "#437",
                    f"{rel}:{node.lineno}",
                    f"`{node.name}()` — 프레임워크 오류 핸들러 밖의 함수는 이 파일에 오지 않는다",
                )


def _check_project_urls(
    f: Path,
    rel: Path,
    findings: Findings,
    *,
    code_keys: frozenset[tuple[str, str, int | str | None]],
) -> None:
    """tree #440 사이트의 선점 억제는 code 레인 «실발화 사건 키»로만 한다(귀속
    매핑표 v2 §5 · MEDIATION-3 M1/R2 — 파일 단위 활성 폐기): 사건 식별자는 registrar
    fn 이름이다 — code 가 같은 URLconf 에서 같은 fn 의 #440 사건을 실발화했을 때만
    그 fn 의 tree #440 을 억제한다. spec 밖 registrar 의 미호출 등 code 미발화
    사건은 그대로 방출한다(#441 은 겹침 미등재라 항상 그대로)."""
    mod = _slice_parse(f)
    if mod is None:
        return
    imported_regs: dict[str, tuple[int, str]] = {}
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module.split(".")[0] != "application":
                continue
            for a in node.names:
                name = a.asname or a.name
                if a.name.startswith("register_") and a.name.endswith("_api"):
                    imported_regs[name] = (node.lineno, a.name)
                else:
                    findings.add(
                        "#441",
                        f"{rel}:{node.lineno}",
                        f"`{node.module}.{a.name}` import — urls.py 가 BC 심볼을 쓰는 예외는 `register_<bc>_api` 명시 호출 하나뿐이다",
                    )
    called = {
        (n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", ""))
        for n in ast.walk(mod) if isinstance(n, ast.Call)
    }
    rel_key: str = rel.as_posix()
    for name, (lineno, imported_symbol) in imported_regs.items():
        if name in called or ("#440", rel_key, imported_symbol) in code_keys:
            continue
        findings.add(
            "#440",
            f"{rel}:{lineno}",
            f"`{name}` 을 import 하고 부르지 않았다 — urls.py 는 각 BC 의 `register_<bc>_api(api)` 를 «명시적으로 부른다»",
        )


def _standard_tree_slice(
    root: Path,
    code_keys: frozenset[tuple[str, str, int | str | None]],
) -> tuple[Findings, Candidates]:
    """구조화 엔트리 수집 — 라인은 공용 포매터(violation `[{rule}] {where}: {msg}` ·
    candidate `[ⓓ{rule}] {where}: {msg} — 물음: {q}`)로 emit_all 이 생성한다(출력 계약 v2).
    code_keys 는 code 레인 실발화 사건의 선점 억제 키(_code_overlap_keys) — 겹침 등재
    tree 사이트(#107·#108·#109·#440)는 정확히 대응하는 키가 있을 때만 엔트리 단위로
    억제한다(귀속 매핑표 v2 §5 · MEDIATION-3 M1/R2 — 파일 단위 활성 폐기)."""
    findings: Findings = Findings(defer=True)
    candidates: Candidates = Candidates(defer=True)
    for bc in _find_bc_dirs(root):
        if not _has_any_layer(bc):
            continue
        bc_rel = bc.relative_to(root)
        _check_composition_dir(bc, bc_rel, findings, candidates)
        _check_inner_driving_imports(bc, bc_rel, findings)
        _check_api_dir(bc, bc_rel, findings, candidates, code_keys)
    for d in _find_project_dirs(root):
        api_py = d / "api.py"
        if api_py.is_file():
            _check_project_api(api_py, api_py.relative_to(root), findings)
        urls_py = d / "urls.py"
        if urls_py.is_file():
            urls_rel: Path = urls_py.relative_to(root)
            _check_project_urls(urls_py, urls_rel, findings, code_keys=code_keys)
    return findings, candidates


def main(argv: list[str]) -> int:
    try:
        config = _parse_config(argv[1:])
        if config.anchor is not None:
            # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚
            # 파일·공허 차분이 침묵 exit 0 되지 않게 parse 직후 막는다(fail-closed).
            anchor_diff.validate_materials(config.root, config.anchor, config.anchor_debt_file)
        inventory = _code_inventory(config.root)
        parsed: dict[Path, ParsedSource] = {}
        if config.profile in {"dddjango-code-json", "preserve-established"}:
            parsed = _selected_sources(config, inventory)
        composition_findings: list[Finding] = []
        if config.profile == "dddjango-code-json":
            analysis, composition_findings = _composition_semantics(config, parsed)
            if analysis:
                raise UsageError("; ".join(analysis))
        di_findings: Findings = _filtered_di_findings(config.root, inventory)
        # tree↔code 동일 사건 선점 억제(귀속 매핑표 v2 §5 · MEDIATION-3 M1/R2) — 키는
        # code 레인이 «실발화한» finding 에서만 나온다(파일 단위 활성 폐기). 비-code
        # 프로필은 composition_findings 가 비어 키도 공집합 = tree 단독 그대로.
        code_overlap_keys: frozenset[tuple[str, str, int | str | None]] = (
            _code_overlap_keys(composition_findings)
        )
        tree_findings, tree_candidates = _standard_tree_slice(
            config.root, code_overlap_keys
        )
    except (UsageError, anchor_diff.AnchorDiffUsage) as exc:
        print(f"[check-composition-root] 사용 오류: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:  # argparse --help
        return int(exc.code)

    code_surfaces: list[Findings | ContractFindings] = []
    if composition_findings:
        # 방출 표면 — 라인은 레코드 필드의 순수 함수(violation `[#N] {where}: {msg}` ·
        # 계약 `- {where}: {msg}`)이고, stdout 인쇄 순서 = 레코드 순서(emit_all 불변식).
        # 판정(#N/계약)이 갈릴 때마다 defer 컬렉션을 이어 붙여 현행 인쇄 순서를 보존한다.
        def _violation_surface() -> Findings:
            tail = code_surfaces[-1] if code_surfaces else None
            if not isinstance(tail, Findings):
                tail = Findings(defer=True)
                code_surfaces.append(tail)
            return tail

        def _contract_surface() -> ContractFindings:
            tail = code_surfaces[-1] if code_surfaces else None
            if not isinstance(tail, ContractFindings):
                tail = ContractFindings(CONTRACT_REF, defer=True)
                code_surfaces.append(tail)
            return tail

        for finding in composition_findings:
            finding_where: str = f"{finding.relative_path}:{finding.lineno}"
            finding_msg: str = f"{finding.category} — {finding.shown}"
            if finding.rule is not None:
                _violation_surface().add(
                    finding.rule, finding_where, finding_msg, symbol=finding.symbol
                )
            else:
                _contract_surface().add(
                    where=finding_where, msg=finding_msg, symbol=finding.symbol
                )
        print("[check-composition-root] BLOCKER — API registrar/URLconf 조립 계약 위반:")
        emit_all(*code_surfaces, printer=print)
        print(
            "  API 근거: implementation-django-ninja §2.2·discipline-houserules final.md §1. "
            "각 BC의 canonical `driving_layer/api/api_router.py`가 "
            "`register_<bc>_api(api)` 안에서만 controller를 등록하고, 선택 URLconf가 "
            "선택 API object를 각 registrar에 정확히 한 번 전달한다. 위 finding의 "
            "signature/provenance/owner/count를 그 직접 계약에 맞춰라."
        )
    if di_findings:
        print(
            "[check-composition-root] BLOCKER — DI 조립(컴포지션 루트)이 트리에 없는 "
            "단일 파일 `composition_root.py` 모양이다(#497 — 정본은 BC 루트 «폴더» `composition_root/`):"
        )
        emit_all(di_findings, printer=print)
        print(
            "  근거: discipline-houserules final.md §1(트리 2~4행). DI 조립은 BC 루트 «폴더» "
            "`application/<bc>/composition_root/`가 소유하고(결선은 `dependency_wiring.py` · "
            "사실 결선은 `event_wiring.py`), driving 쪽은 `build_<use_case>()` 팩토리를 "
            "매요청 호출만 한다 — feature별 `composition/` 폴더로 쪼개거나 계층 하위에 묻거나 "
            "단일 파일 `composition_root.py` 모양으로 두지 않는다(operation 본문에서 "
            "`Django…Repository()`/`…Adapter()`를 직접 생성하지 않는 Q-7의 짝). `composition/` "
            "폴더의 provider들과 단일 파일의 배선은 `composition_root/dependency_wiring.py`로 "
            "옮겨라. application 로직(command/query/service 등)을 가졌는데 정본이 아예 없으면(부재) "
            "BC 루트에 `composition_root/` 폴더를 만들어 배선을 둬라(데이터소스 BC는 해당 없음)."
        )
    if tree_findings:
        print("[check-composition-root] BLOCKER — 표준 트리 결선·등록 규율 위반 (트리 2~4·8·9·136·137행):")
        emit_all(tree_findings, printer=print)
    if tree_candidates:
        print("[check-composition-root] ⓓ 후보 — 기계가 후보를 좁혔다 · 마무리 물음은 discipline-reviewer 몫(exit 불산입):")
        emit_all(tree_candidates, printer=print)
    if composition_findings or di_findings or tree_findings:
        if config.anchor is not None:
            all_findings: list[str] = []
            for surface in code_surfaces:
                all_findings.extend(lines(surface))
            all_findings.extend(lines(di_findings))
            all_findings.extend(lines(tree_findings))
            try:
                return anchor_diff.partition_exit(
                    script=Path(__file__).resolve(),
                    label="[check-composition-root]",
                    target=config.root,
                    anchor=config.anchor,
                    argv=argv[1:],
                    findings=all_findings,
                    path_flags=frozenset(
                        {"--api-module", "--urlconf-module", "--registrar-module"}
                    ),
                    debt_file=config.anchor_debt_file,
                )
            except anchor_diff.AnchorDiffUsage as exc:
                print(f"[check-composition-root] 사용 오류: {exc}", file=sys.stderr)
                return 1
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
