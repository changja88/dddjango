#!/usr/bin/env python3
"""dddjango 4계층 골격 결정적 백스톱 (구조 — houserules §0-2 집행).

기존 백스톱(mechanism-ownership·error-centralization·response-schema-bypass)이
*행위/계약*을 보는 데 비해, 이건 **구조**를 본다. 표준 레이아웃(`application/<bc>/`)을
적용한 프로젝트에서 각 바운디드 컨텍스트(BC)는 4계층 폴더(`domain_layer`·
`application_layer`·`infra_layer`·`presentation_layer`)를 **내용이 없어도 빈
패키지(`__init__.py`)로라도 모두** 가져야 한다(houserules §0-2). 다섯 위반 형태를 차단한다:
  - **신규 root 앱**: 제공된 G0 boundary state에 기존 root Django 앱 관례가 없는데
    레포 루트 직속 패키지에 실제 Django `AppConfig`/`Model`을 새로 두고
    `application/<bc>/` 기본 구조를 우회. G0에 root 앱이 하나라도 있으면 그 프로젝트의
    확립 관례를 보존한다. state 없는 구 호출은 `application/` 존재+Git HEAD로만 판정한다.
  - **부분 평면**: 일부 계층만 있고 하나를 생략(스모크 SH-2 — HTTP 없이 ACL·
    published_service 로만 소비되는 내부 전용 BC 가 `presentation_layer` 를 생략).
  - **완전 평면**: Django 앱 산출물은 있는데 4계층으로 전혀 분리 안 함
    (`application/<bc>/` 루트에 `models.py`·`views.py` 등을 직접 둔 평면 상태).
  - **종류 폴더 누락**: 4계층은 있으나 고정명 종류 폴더(`presentation_layer/api`·
    `presentation_layer/schema`·`infra_layer/acl`)를 빈 패키지로라도 만들지 않음(§0-4 개정
    2026-06-08: 이들은 표현/통합 내용이 없어도 무조건 생성). 더해 *이미 존재하는*
    `domain_layer/<aggregate>/` 의 코어 종류(`entity`·`value_object`·`repository` + `exception.py`)
    누락도 잡는다(coder 가 `domain_layer/product/` 만들고 `value_object/` 를 빠뜨린 경우).
  - **외래 port/(협력 포트 오배치 — SH-7)**: `application_layer`/`infra_layer` 하위의 `port/`
    디렉터리가 비-`__init__` `.py` 를 담음. 협력 포트(타 BC 소비용 역할 추상 ABC)는
    `domain_layer/<aggregate>/port/` 소유다(houserules §2 — "도메인은 협력 포트로만 의존"·
    §3 표·"command 는 domain port 의존" DIP). application_layer 의 종류 폴더는
    command/query/dto 뿐이고 ACL *구현*은 `infra_layer/acl/` 직속이라, 그 계층들 밑 `port/` 는
    표준 트리에 존재하지 않는 외래 구조다(라이브 형태 N=2·둘 다 Codex: design-spec 이
    포트를 "use-case dependency" 로 재분류해 `application_layer/place_order/port/` 에 배치 —
    reviewer 가 명세-부합을 이유로 권고로 강등해 게이트를 통과했다). **빈 `port/` 패키지는
    면제**(위반의 전조일 뿐·골격 잔재). 경로에 test/tests 가 끼면 스킵. 폴더 개명 변종
    (`contract/`·`ports/` 복수형·평면 `port.py`)과 `presentation_layer` 배치는 안 잡는다
    (저-recall — 채점 결정 레인(`find -type d -name port`)과 동일 사각·reviewer 의미 레인 몫).

*왜 결정적 백스톱인가* — 빈 계층 폴더엔 테스트가 걸리지 않아 TDD Red 로 안 잡힌다(coder 가
누락해도 `manage.py test` 는 Green). discipline-reviewer 의미 게이트 한 점에만 의존하면
LLM 이 프로즈 규칙을 회피하는 표면이 된다 — 이 스크립트가 그 절반을 결정적으로 메운다
(고정밀·저-recall, 거짓 양성 ≈0).

거짓 양성 회피 — AND 합성으로만 차단:
  0) 두 번째 인자로 G0 boundary state가 주어지면 snapshot의 app identity로 생성 시점과
     프로젝트 관례를 판정한다. G0 root 앱이 하나라도 있으면 확립된 root 관례를 보존하고,
     없으면 `application/<bc>/` 기본 위치를 적용한다. 따라서 G0 전 untracked·unborn·non-git
     앱도 기존 brownfield로 grandfather한다. `application/<bc>` 자체가 G0 persistence app이고
     현재도 4계층을 전혀 도입하지 않은 평면 앱이면 touched 여부와 무관하게 골격 이주를
     강요하지 않는다. state가 없는 구 호출만 `application/` 존재와 Git HEAD를 fallback으로
     사용한다. `migrations/`는 앱 marker가 아니다.
  1) 아래 4계층 검사는 프로젝트가 *표준 레이아웃*을 쓸 때만 적용한다 = 레포에
     `application/` 컨테이너 디렉터리가 있다. 없으면 root 신규 앱 위치 검사 외에는 exit 0.
  2) `application/<bc>/` 가 *4계층을 따라야 할 앱* 이다 — 둘 중 하나:
       (a) 4계층 폴더 중 하나라도 이미 디렉터리로 존재(자신을 4계층 앱으로 선언), 또는
       (b) Django 앱 산출물(`models.py`·`models/`·`apps.py`·`views.py`·`admin.py`)을
           BC 루트에 직접 가진 *완전 평면* 앱(계층 0개).
     둘 다 아닌 디렉터리(계층도 Django 산출물도 없는 컨테이너 잡동사니·비-앱 패키지)는
     건너뛴다 → 거짓 양성 0.
  3) (git 레포면) 그 BC 하위에 이번 변경에서 새로 추가/수정/미추적된 *비-migration* 파일이
     있다 = 이번 작업이 건드린 BC. `migrations/` 변화는 외부 release 경계이므로 touched
     신호로 사용하지 않고, 기존에 커밋된 채 안 건드린 BC 는 존중(brownfield) → 건너뜀.
  위 셋이 참인 BC 에서:
    - (b)면 4계층 전부 미분리 = blocker.
    - (a)면 4계층 중 하나라도 (폴더가 없거나 / 폴더는 있으나 `__init__.py` 가 없어 git 에
      존속 안 되면) blocker.
    - 4계층이 다 있어도 고정명 종류 폴더(`presentation_layer/api`·`presentation_layer/schema`·
      `infra_layer/acl`)가 빈 패키지로 없으면 blocker — 고정명이라 거짓 양성 없다(§0-4 무조건).
    - *이미 존재하는* `domain_layer/<aggregate>/` 가 *애그리거트로 보이면*(루트 파일
      `<X>/<X>.py` 또는 `entity/`·`value_object/` 하나라도 보유) 그 안의 코어 종류
      (`entity`·`value_object`·`repository` 폴더 + `exception.py`)가 빠지면 blocker. **ORM 에서
      애그리거트 이름을 추론하지 않는다** — 디스크에 실재하는 `domain_layer/<X>/` 만 검사한다.
      `domain_layer/` 직하에 cross-aggregate 공용 `domain_service/`(final.md §3) 가 와도
      애그리거트 신호(루트 파일/entity/value_object)가 없으면 애그리거트로 보지 않고 스킵한다.
      `[선택]` 종류 폴더(`port`·`domain_service`·`event`·`specification`)는 *존재만* 확인하고
      누락은 잡지 않는다(저-recall — reviewer 의미 레인 몫; 거짓 양성 회피 우선).
    - `application_layer`/`infra_layer` 하위 `port/` 가 비-`__init__` `.py` 를 담으면 blocker
      (외래 port — 위 네 번째 위반 형태. 빈 패키지·test 경로는 면제).
  통과 조건: 4계층 + 고정명 종류 폴더(api/schema/acl)가 빈 패키지로 있고, 존재하는
  애그리거트의 코어 종류가 채워져 있으면 통과. `domain_layer/` 에 애그리거트가 *0개* 면(예:
  데이터소스 골격 미생성) 이 스크립트는 **안 잡고 reviewer 의미 레인에 맡긴다**(저-recall
  수용). `application_layer` 는 feature(`<feature>/`) 0개면 빈 계층 정당이라 검사하지 않는다.
  내용 적정성(채운 게 옳은지)은 항상 discipline-reviewer 의미 체크 몫이다.

사용법: check-layer-skeleton.py TARGET_DIR G0_BOUNDARY_STATE
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import hashlib
import json
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath

try:
    from migration_scope import (
        MigrationScopeError,
        configure_migration_scope,
        is_migration_owned_path as _strict_migration_owned_path,
        iter_non_migration_directories,
        iter_non_migration_files,
    )
except ModuleNotFoundError:
    # importlib로 이 파일만 직접 로드하는 boundary/test 경로도 sibling helper를 찾게 한다.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from migration_scope import (  # type: ignore[no-redef]
        MigrationScopeError,
        configure_migration_scope,
        is_migration_owned_path as _strict_migration_owned_path,
        iter_non_migration_directories,
        iter_non_migration_files,
    )

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
ROOT_APP_SKIP_DIRS = SKIP_DIRS | {
    "application",
}
ROOT_APP_MARKER_FILES = ("apps.py", "models.py")
ROOT_APP_MARKER_DIRS = ("models",)

# 4계층 — houserules §0-2. 순서 고정(보고 가독성).
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")

# "이 디렉터리는 4계층을 따라야 할 Django 앱이다"의 강한 신호(BC 루트에 직접 존재 시).
# 정상 4계층 앱은 이들을 `infra_layer/django_<app>/`에 두므로 루트엔 없다 — 루트에 있으면
# startapp 직후 평면 상태(완전 평면)다. 잡동사니 util 패키지엔 이들이 없어 거짓 양성 0.
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
DJANGO_APP_MARKER_DIRS = ("models",)

# 고정명 종류 폴더 — §0-4 개정(2026-06-08)으로 표현/통합 내용이 없어도 무조건 빈 패키지.
# 고정명이라 거짓 양성 없음(BC 마다 동일 골격). (계층, 종류폴더 상대경로) 쌍.
REQUIRED_KIND_DIRS = (
    ("presentation_layer", "api"),
    ("presentation_layer", "schema"),
    ("infra_layer", "acl"),
)

# 애그리거트 *코어* 종류 — `domain_layer/<aggregate>/` 가 애그리거트로 보일 때 빠지면 잡는다.
# `[선택]`(port/domain_service/event/specification)은 의도적으로 제외(저-recall·거짓 양성 회피).
AGG_CORE_KIND_DIRS = ("entity", "value_object", "repository")
AGG_CORE_FILE = "exception.py"
# 애그리거트 신호 — 이 중 하나라도 있으면 `<X>/` 를 애그리거트로 보고 코어 완비를 검사한다.
# 없으면(예: cross-aggregate 공용 `domain_service/`) 애그리거트가 아니므로 스킵(거짓 양성 회피).
AGG_SIGNAL_KIND_DIRS = ("entity", "value_object")

# 외래 port 검사 대상 계층 — 협력 포트는 domain_layer 소유라 이 계층들 밑 port/ 는 표준 트리에
# 없는 외래 구조다(SH-7·houserules §2·§3 표). presentation_layer 는 채점 결정 레인(SH-7 FAIL =
# application_layer/infra_layer)과 정합하게 제외(관측 0·reviewer 의미 레인 몫).
FOREIGN_PORT_LAYERS = ("application_layer", "infra_layer")
TEST_DIR_NAMES = {"test", "tests"}
BOUNDARY_MANIFEST_FORMAT = "dddjango-migration-boundary-v11"
BOUNDARY_RECEIPT_FORMAT = "dddjango-migration-boundary-receipt-v2"
BOUNDARY_RECEIPT_SUFFIX = ".write-once"


def is_migration_owned_path(root: Path, path: Path) -> bool:
    """Main/boundary는 scope를 먼저 주입한다; 순수 구조 helper 직접 호출만 빈 scope를 허용."""
    try:
        return _strict_migration_owned_path(root, path)
    except MigrationScopeError:
        return False


def _path_resolves_within_root(root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _is_settings_package(directory: Path) -> bool:
    if (directory / "settings.py").is_file():
        return True
    return (directory / "urls.py").is_file() and (
        (directory / "wsgi.py").is_file() or (directory / "asgi.py").is_file()
    )


class _ModuleDjangoSignalCollector(ast.NodeVisitor):
    """모듈 제어 흐름의 import/class만 모으고 함수·클래스 내부는 제외한다."""

    def __init__(self) -> None:
        self.imports: list[ast.Import | ast.ImportFrom] = []
        self.classes: list[ast.ClassDef] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.append(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return


def _expression_path(expression: ast.expr) -> str | None:
    if isinstance(expression, ast.Name):
        return expression.id
    if isinstance(expression, ast.Attribute):
        owner = _expression_path(expression.value)
        if owner is not None:
            return f"{owner}.{expression.attr}"
    return None


def _has_actual_app_config(root: Path, directory: Path) -> bool:
    source = directory / "apps.py"
    if (
        is_migration_owned_path(root, source)
        or not _path_resolves_within_root(root, source)
        or not source.is_file()
    ):
        return False
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (OSError, UnicodeError, SyntaxError):
        return False
    collector = _ModuleDjangoSignalCollector()
    collector.visit(tree)
    direct_aliases: set[str] = set()
    module_aliases: set[str] = set()
    for node in collector.imports:
        if isinstance(node, ast.ImportFrom) and node.module == "django.apps":
            direct_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "AppConfig"
            )
        elif isinstance(node, ast.ImportFrom) and node.module == "django":
            module_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "apps"
            )
        elif isinstance(node, ast.Import):
            for imported in node.names:
                if imported.name == "django.apps":
                    module_aliases.add(imported.asname or imported.name)
                elif imported.name == "django":
                    module_aliases.add(f"{imported.asname or imported.name}.apps")
    return any(
        any(
            (isinstance(base, ast.Name) and base.id in direct_aliases)
            or _expression_path(base)
            in {f"{module}.AppConfig" for module in module_aliases}
            for base in class_node.bases
        )
        for class_node in collector.classes
    )


def _has_actual_django_model(root: Path, directory: Path) -> bool:
    sources: list[Path] = []
    module = directory / "models.py"
    if (
        not is_migration_owned_path(root, module)
        and _path_resolves_within_root(root, module)
        and module.is_file()
    ):
        sources.append(module)
    package = directory / "models"
    if (
        not is_migration_owned_path(root, package)
        and _path_resolves_within_root(root, package)
        and package.is_dir()
    ):
        sources.extend(
            source
            for source in iter_non_migration_files(root, package, "*.py")
            if _path_resolves_within_root(root, source)
        )
    for source in sources:
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, UnicodeError, SyntaxError):
            continue
        collector = _ModuleDjangoSignalCollector()
        collector.visit(tree)
        direct_aliases: set[str] = set()
        module_aliases: set[str] = set()
        for node in collector.imports:
            if isinstance(node, ast.ImportFrom) and node.module == "django.db.models":
                direct_aliases.update(
                    imported.asname or imported.name
                    for imported in node.names
                    if imported.name == "Model"
                )
            elif isinstance(node, ast.ImportFrom) and node.module == "django.db":
                module_aliases.update(
                    imported.asname or imported.name
                    for imported in node.names
                    if imported.name == "models"
                )
            elif isinstance(node, ast.Import):
                for imported in node.names:
                    if imported.name == "django.db.models":
                        module_aliases.add(imported.asname or imported.name)
                    elif imported.name == "django":
                        module_aliases.add(
                            f"{imported.asname or imported.name}.db.models"
                        )
        model_bases = {f"{module_name}.Model" for module_name in module_aliases}
        if any(
            any(
                (isinstance(base, ast.Name) and base.id in direct_aliases)
                or _expression_path(base) in model_bases
                for base in class_node.bases
            )
            for class_node in collector.classes
        ):
            return True
    return False


def _is_django_app_directory(root: Path, directory: Path) -> bool:
    return _has_actual_app_config(root, directory) or _has_actual_django_model(
        root, directory
    )


def _root_app_candidates(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for child in sorted(root.iterdir()):
        if (
            child.name in ROOT_APP_SKIP_DIRS
            or is_migration_owned_path(root, child)
            or not _path_resolves_within_root(root, child)
            or not child.is_dir()
        ):
            continue
        if _is_settings_package(child) or not _is_django_app_directory(root, child):
            continue
        candidates.append(child)
    return candidates


def _git_has_head(root: Path) -> bool | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", "HEAD"],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def _head_has_path(root: Path, relative: Path) -> bool | None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-tree",
                "--name-only",
                "HEAD",
                "--",
                relative.as_posix(),
            ],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def _was_root_app_in_head(root: Path, app_dir: Path) -> bool | None:
    relative = app_dir.relative_to(root)
    marker_states = [
        _head_has_path(root, relative / name)
        for name in (*ROOT_APP_MARKER_FILES, *ROOT_APP_MARKER_DIRS)
    ]
    if any(state is None for state in marker_states):
        return None
    return any(marker_states)


def _new_root_apps(
    root: Path,
    baseline_root_apps: set[str] | None = None,
) -> list[Path]:
    candidates = _root_app_candidates(root)
    if baseline_root_apps is not None:
        return [
            candidate
            for candidate in candidates
            if candidate.relative_to(root).as_posix() not in baseline_root_apps
        ]

    has_head = _git_has_head(root)
    if has_head is None:
        return []  # non-git·Git 판정 실패 — 기존 brownfield 오차단 방지.
    if not has_head:
        return candidates  # unborn HEAD — 현재 앱은 모두 신규.
    new_apps: list[Path] = []
    for candidate in candidates:
        existed = _was_root_app_in_head(root, candidate)
        if existed is False:
            new_apps.append(candidate)
    return new_apps


def _baseline_context(
    root: Path,
    state_file: Path,
) -> tuple[
    set[str],
    set[str],
    bool,
    set[str],
    dict[str, set[str]],
    set[str],
]:
    if state_file.is_symlink() or not state_file.is_file():
        raise ValueError(f"G0 boundary state가 regular file이 아니다: {state_file}")
    if not stat.S_ISREG(state_file.lstat().st_mode):
        raise ValueError(f"G0 boundary state가 regular file이 아니다: {state_file}")
    try:
        serialized = state_file.read_bytes()
        value = json.loads(serialized.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"G0 boundary state를 읽을 수 없다: {state_file}") from error
    if not isinstance(value, dict) or value.get("format") != BOUNDARY_MANIFEST_FORMAT:
        raise ValueError("G0 boundary state format이 지원되지 않는다")
    canonical = (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if serialized != canonical:
        raise ValueError("G0 boundary state가 canonical JSON이 아니다")
    receipt = state_file.with_name(f"{state_file.name}{BOUNDARY_RECEIPT_SUFFIX}")
    if receipt.is_symlink() or not receipt.is_file():
        raise ValueError(f"G0 boundary receipt가 없다: {receipt}")
    try:
        receipt_serialized = receipt.read_text(encoding="utf-8")
        receipt_value = json.loads(receipt_serialized)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"G0 boundary receipt를 읽을 수 없다: {receipt}") from error
    expected_receipt = {
        "format": BOUNDARY_RECEIPT_FORMAT,
        "manifest_sha256": hashlib.sha256(serialized).hexdigest(),
        "state_path": str(state_file),
    }
    canonical_receipt = (
        json.dumps(expected_receipt, ensure_ascii=True, indent=2, sort_keys=True)
        + "\n"
    )
    if receipt_value != expected_receipt or receipt_serialized != canonical_receipt:
        raise ValueError("G0 boundary receipt가 state와 일치하지 않는다")
    if value.get("root") != str(root):
        raise ValueError("G0 boundary state의 root가 TARGET_DIR과 다르다")
    identities = value.get("app_identities")
    if not isinstance(identities, list) or not all(
        isinstance(item, str) for item in identities
    ):
        raise ValueError("G0 boundary state에 app_identities가 없다")
    root_apps: set[str] = set()
    app_directories: set[str] = set()
    for identity in identities:
        path = Path(identity)
        if len(path.parts) >= 2 and path.parts[0] == "application":
            app_directories.add(PurePosixPath(*path.parts[:2]).as_posix())
        elif (
            len(path.parts) >= 3
            and path.parts[0] == "src"
            and path.parts[1] == "application"
        ):
            app_directories.add(PurePosixPath(*path.parts[:3]).as_posix())
        elif path.name in {"apps.py", "models.py", "models"}:
            app_directories.add(path.parent.as_posix())
        if len(path.parts) == 2 and path.name in {"apps.py", "models.py", "models"}:
            root_apps.add(path.parent.as_posix())
    def normalized_paths(field: str) -> set[str]:
        raw_paths = value.get(field)
        if not isinstance(raw_paths, list) or not all(
            isinstance(item, str) and item for item in raw_paths
        ):
            raise ValueError(f"G0 boundary state에 {field}가 없다")
        if raw_paths != sorted(raw_paths) or len(raw_paths) != len(set(raw_paths)):
            raise ValueError(f"G0 boundary state의 {field}가 정렬된 고유 목록이 아니다")
        paths: set[str] = set()
        for item in raw_paths:
            path = PurePosixPath(item)
            if (
                item == "."
                or not path.parts
                or path.is_absolute()
                or path.as_posix() != item
                or any(part in {"", ".", ".."} for part in path.parts)
            ):
                raise ValueError(
                    f"G0 boundary state의 {field} 경로가 올바르지 않다: {item!r}"
                )
            paths.add(item)
        return paths

    migration_roots = normalized_paths("migration_roots")
    migration_roots.update(normalized_paths("migration_alias_targets"))
    external_owned_opaque_paths = normalized_paths(
        "external_owned_opaque_paths"
    )
    raw_containers = value.get("application_containers")
    if not isinstance(raw_containers, list) or any(
        item not in {"application", "src/application"}
        for item in raw_containers
    ):
        raise ValueError("G0 boundary state에 application_containers가 없다")
    raw_layer_issues = value.get("application_layer_issues")
    if not isinstance(raw_layer_issues, dict) or not all(
        isinstance(path, str)
        and isinstance(issues, list)
        and all(isinstance(issue, str) and issue for issue in issues)
        for path, issues in raw_layer_issues.items()
    ):
        raise ValueError("G0 boundary state에 application_layer_issues가 없다")
    application_layer_issues = {
        path: set(issues) for path, issues in raw_layer_issues.items()
    }
    return (
        root_apps,
        migration_roots,
        bool(raw_containers),
        app_directories,
        application_layer_issues,
        external_owned_opaque_paths,
    )


def _find_application_containers(root: Path) -> list[Path]:
    """표준 앱 컨테이너(`application/`) 디렉터리들. 계층 `application_layer` 와 이름이
    달라 자연히 구분된다."""
    return [
        candidate
        for candidate in (root / "application", root / "src" / "application")
        if not is_migration_owned_path(root, candidate)
        and _path_resolves_within_root(root, candidate)
        and candidate.is_dir()
    ]


def _find_bc_dirs(root: Path) -> list[Path]:
    """각 `application/` 컨테이너의 직속 하위 디렉터리(= BC 후보)."""
    out: list[Path] = []
    for container in _find_application_containers(root):
        for child in sorted(container.iterdir()):
            if (
                is_migration_owned_path(root, child)
                or not _path_resolves_within_root(root, child)
                or not child.is_dir()
            ):
                continue
            if child.name in SKIP_DIRS:
                continue
            out.append(child)
    return out


def _has_any_layer(root: Path, bc_dir: Path) -> bool:
    """4계층 폴더 중 하나라도 디렉터리로 존재 = 자신을 4계층 앱으로 선언한 것."""
    return any(
        not is_migration_owned_path(root, bc_dir / layer)
        and _path_resolves_within_root(root, bc_dir / layer)
        and (bc_dir / layer).is_dir()
        for layer in LAYER_DIRS
    )


def _has_django_app_marker(root: Path, bc_dir: Path) -> bool:
    """BC 루트에 Django 앱 산출물이 직접 있는가(완전 평면 앱의 신호)."""
    return _is_django_app_directory(root, bc_dir)


def _is_empty_package_dir(d: Path) -> bool:
    """디렉터리이고 `__init__.py` 를 가진 regular package인가(빈 골격 허용 판정)."""
    return d.is_dir() and (d / "__init__.py").exists()


def _kind_dir_issues(root: Path, bc_dir: Path) -> list[str]:
    """고정명 종류 폴더(api/schema/acl) 누락/비-패키지를 설명 리스트로. 고정명=거짓 양성 0."""
    issues: list[str] = []
    for layer, kind in REQUIRED_KIND_DIRS:
        d = bc_dir / layer / kind
        if (
            is_migration_owned_path(root, d)
            or not _path_resolves_within_root(root, d)
            or not d.is_dir()
        ):
            issues.append(f"{layer}/{kind}/ 폴더 없음")
        elif not _path_resolves_within_root(root, d / "__init__.py"):
            issues.append(f"{layer}/{kind}/ 에 __init__.py 없음(git 미추적·골격 소실)")
    return issues


def _looks_like_aggregate(root: Path, agg_dir: Path) -> bool:
    """`domain_layer/<X>/` 가 애그리거트인가 — 루트 파일 `<X>/<X>.py` 또는 entity/value_object
    하나라도 보유. 신호가 없으면(예: cross-aggregate 공용 `domain_service/`) 애그리거트가
    아니므로 코어 완비 검사에서 제외(거짓 양성 회피)."""
    aggregate_module = agg_dir / f"{agg_dir.name}.py"
    if (
        not is_migration_owned_path(root, aggregate_module)
        and _path_resolves_within_root(root, aggregate_module)
        and aggregate_module.is_file()
    ):
        return True
    return any(
        not is_migration_owned_path(root, agg_dir / kind)
        and _path_resolves_within_root(root, agg_dir / kind)
        and (agg_dir / kind).is_dir()
        for kind in AGG_SIGNAL_KIND_DIRS
    )


def _aggregate_issues(root: Path, bc_dir: Path) -> list[str]:
    """*이미 존재하는* `domain_layer/<X>/`(애그리거트로 보이는) 의 코어 종류 누락을 설명
    리스트로. ORM 에서 이름 추론 안 함 — 디스크 실재 애그리거트만. 코어=entity/value_object/
    repository 폴더 + exception.py. `[선택]` 종류는 잡지 않는다(저-recall)."""
    domain_layer = bc_dir / "domain_layer"
    if (
        is_migration_owned_path(root, domain_layer)
        or not _path_resolves_within_root(root, domain_layer)
        or not domain_layer.is_dir()
    ):
        return []
    issues: list[str] = []
    for agg_dir in sorted(domain_layer.iterdir()):
        if (
            is_migration_owned_path(root, agg_dir)
            or not _path_resolves_within_root(root, agg_dir)
            or not agg_dir.is_dir()
            or agg_dir.name in SKIP_DIRS
        ):
            continue
        if not _looks_like_aggregate(root, agg_dir):
            continue  # 애그리거트 신호 없음(공용 domain_service 등) → 스킵.
        for kind in AGG_CORE_KIND_DIRS:
            d = agg_dir / kind
            if (
                is_migration_owned_path(root, d)
                or not _path_resolves_within_root(root, d)
                or not d.is_dir()
            ):
                issues.append(f"domain_layer/{agg_dir.name}/{kind}/ 폴더 없음")
            elif not _path_resolves_within_root(root, d / "__init__.py"):
                issues.append(
                    f"domain_layer/{agg_dir.name}/{kind}/ 에 __init__.py 없음(골격 소실)"
                )
        core_file = agg_dir / AGG_CORE_FILE
        if (
            is_migration_owned_path(root, core_file)
            or not _path_resolves_within_root(root, core_file)
            or not core_file.is_file()
        ):
            issues.append(f"domain_layer/{agg_dir.name}/{AGG_CORE_FILE} 없음")
    return issues


def _foreign_port_issues(root: Path, bc_dir: Path) -> list[str]:
    """`application_layer`/`infra_layer` 하위 `port/` 의 협력 포트 오배치(SH-7)를 설명 리스트로.

    협력 포트(ABC)는 `domain_layer/<aggregate>/port/` 소유(houserules §2·§3 표) — 호출자가
    application 유스케이스(command)여도 'use-case dependency' 재분류로 위치가 바뀌지 않는다.
    빈 `port/` 패키지(비-`__init__` .py 0개)·test 경로는 면제. 폴더 개명 변종은 안 잡는다(저-recall)."""
    issues: list[str] = []
    for layer in FOREIGN_PORT_LAYERS:
        layer_dir = bc_dir / layer
        if (
            is_migration_owned_path(root, layer_dir)
            or not _path_resolves_within_root(root, layer_dir)
            or not layer_dir.is_dir()
        ):
            continue
        for port_dir in iter_non_migration_directories(root, layer_dir):
            if port_dir.name != "port":
                continue
            if not _path_resolves_within_root(root, port_dir) or not port_dir.is_dir():
                continue
            rel_parts = set(port_dir.relative_to(bc_dir).parts)
            if rel_parts & SKIP_DIRS or rel_parts & TEST_DIR_NAMES:
                continue
            payload = sorted(
                p.name
                for p in iter_non_migration_files(root, port_dir, "*.py")
                if p.name != "__init__.py" and _path_resolves_within_root(root, p)
            )
            if payload:
                rel = port_dir.relative_to(bc_dir)
                issues.append(
                    f"{rel}/ 에 협력 포트 추정 코드({', '.join(payload[:3])}) — "
                    f"협력 포트(ABC)는 domain_layer/<aggregate>/port/ 소유(§2), "
                    f"{layer} 하위 port/ 는 표준 트리에 없는 외래 구조(SH-7)"
                )
    return issues


def _is_bc_to_check(root: Path, bc_dir: Path) -> bool:
    """4계층을 따라야 할 앱: 계층을 하나라도 가졌거나(부분), Django 산출물 평면(완전)."""
    return _has_any_layer(root, bc_dir) or _has_django_app_marker(root, bc_dir)


def _layer_issues(root: Path, bc_dir: Path) -> list[str]:
    """누락/비-패키지 계층 + 고정명 종류 폴더 + 존재 애그리거트 코어 종류를 설명 리스트로."""
    if not _has_any_layer(root, bc_dir):
        # 완전 평면 — 계층이 0개인데 Django 앱 산출물 보유.
        return ["4계층 전부 없음(완전 평면 앱 — `_layer` 분리 안 됨)"]
    issues: list[str] = []
    for layer in LAYER_DIRS:
        d = bc_dir / layer
        if (
            is_migration_owned_path(root, d)
            or not _path_resolves_within_root(root, d)
            or not d.is_dir()
        ):
            issues.append(f"{layer}/ 폴더 없음")
        elif not _path_resolves_within_root(root, d / "__init__.py"):
            issues.append(f"{layer}/ 에 __init__.py 없음(git 미추적·골격 소실)")
    # 고정명 종류 폴더(api/schema/acl) — §0-4 개정 무조건(데이터소스 BC 포함). 고정명=거짓 양성 0.
    issues.extend(_kind_dir_issues(root, bc_dir))
    # 존재하는 애그리거트의 코어 종류 완비 — ORM 추론 없이 디스크 실재만. 부재(0개)는 reviewer 몫.
    issues.extend(_aggregate_issues(root, bc_dir))
    # 외래 port/ — 협력 포트 오배치(SH-7). application_layer/infra_layer 밑 port/ 에 실코드.
    issues.extend(_foreign_port_issues(root, bc_dir))
    return issues


def _porcelain_change_groups(output: str) -> list[tuple[str, ...]]:
    """`git status --porcelain -z`의 단일 변경 또는 rename/copy path pair."""
    records = output.split("\0")
    groups: list[tuple[str, ...]] = []
    index = 0
    while index < len(records):
        record = records[index]
        if len(record) < 4:
            index += 1
            continue
        status_code = record[:2]
        paths = [record[3:]]
        if "R" in status_code or "C" in status_code:
            index += 1
            if index < len(records) and records[index]:
                paths.append(records[index])
        groups.append(tuple(paths))
        index += 1
    return groups


def _is_migration_path(
    root: Path,
    bc_dir: Path,
    changed_path: str,
    baseline_migration_roots: set[str] | None,
) -> bool:
    logical = PurePosixPath(changed_path)
    if baseline_migration_roots is not None and any(
        logical == PurePosixPath(migration_root)
        or logical.is_relative_to(PurePosixPath(migration_root))
        for migration_root in baseline_migration_roots
    ):
        return True
    try:
        bc_relative = bc_dir.relative_to(root)
        within_bc = Path(changed_path).relative_to(bc_relative)
    except ValueError:
        return False
    parts = within_bc.parts
    return (
        len(parts) >= 4
        and baseline_migration_roots is None
        and parts[0] == "infra_layer"
        and parts[1].startswith("django_")
        and parts[2] == "migrations"
    )


def _is_new_or_modified(
    root: Path,
    bc_dir: Path,
    baseline_migration_roots: set[str] | None = None,
) -> bool:
    """git 레포면 BC의 비-migration 변경 여부. migration-only 변화는 외부 경계라 무시."""
    if not (root / ".git").exists():
        return True
    try:
        rel = bc_dir.relative_to(root)
    except ValueError:
        return True
    try:
        res = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain",
                "-z",
                "--untracked-files=all",
                "--",
                str(rel),
            ],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).
        change_groups = _porcelain_change_groups(res.stdout)
        return any(
            not any(
                _is_migration_path(
                    root,
                    bc_dir,
                    path,
                    baseline_migration_roots,
                )
                for path in paths
            )
            for paths in change_groups
        )
    except (OSError, subprocess.SubprocessError):
        return True


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "사용법: check-layer-skeleton.py TARGET_DIR G0_BOUNDARY_STATE",
            file=sys.stderr,
        )
        return 1
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-layer-skeleton] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    try:
        baseline_context = _baseline_context(
            root,
            Path(argv[2]).expanduser().absolute(),
        )
        configure_migration_scope(
            root,
            sorted(baseline_context[1]),
            sorted(baseline_context[5]),
        )
    except ValueError as error:
        print(f"[check-layer-skeleton] 사용 오류: {error}", file=sys.stderr)
        return 1

    uses_standard_layout = bool(_find_application_containers(root))
    baseline_root_apps = baseline_context[0]
    baseline_migration_roots = baseline_context[1] | baseline_context[5]
    baseline_uses_standard_layout = baseline_context[2]
    baseline_app_directories = baseline_context[3]
    baseline_layer_issues = baseline_context[4]
    enforce_default_root_location = (
        uses_standard_layout
        or baseline_uses_standard_layout
        or (
        baseline_root_apps is not None and not baseline_root_apps
        )
    )
    new_root_apps = (
        _new_root_apps(root, baseline_root_apps)
        if enforce_default_root_location
        else []
    )
    findings: list[str] = []
    if uses_standard_layout:
        for bc in _find_bc_dirs(root):
            if not _is_bc_to_check(root, bc):
                continue
            relative_bc = bc.relative_to(root).as_posix()
            if not _is_new_or_modified(root, bc, baseline_migration_roots):
                continue
            issues = _layer_issues(root, bc)
            if relative_bc in baseline_app_directories:
                previous_issues = baseline_layer_issues.get(relative_bc, set())
                issues = [issue for issue in issues if issue not in previous_issues]
            if issues:
                findings.append(f"  - {bc.relative_to(root)}: {'; '.join(issues)}")

    if new_root_apps:
        print(
            "[check-layer-skeleton] BLOCKER — 신규 Django 앱을 레포 root에 만들었다"
            "(신규 앱은 `application/<bc>/` 표준 구조 소유):"
        )
        for app_dir in new_root_apps:
            print(f"  - {app_dir.relative_to(root).as_posix()}/")
        print(
            "  근거: G0 baseline(미제공 시 Git HEAD)에 같은 root 앱 marker가 있던 기존 brownfield 앱은 그대로 "
            "grandfather하지만, 신규 앱은 root 평면에 추가하지 않고 `application/<bc>/` 아래에서 "
            "4계층·종류 골격을 갖춘다. `migrations/` 유무나 변경은 앱 위치 판정에 사용하지 않는다."
        )

    if findings:
        print(
            "[check-layer-skeleton] BLOCKER — 4계층 BC 가 계층/종류 골격을 생략했거나 "
            "협력 포트를 도메인 밖 계층(`application_layer`/`infra_layer` 하위 `port/`)에 두었다"
            "(houserules §0-2·§0-4·§2):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: discipline-houserules §0-2·§0-4·§2. 표현/도메인 관심사가 없다는 판단으로 "
            "계층·종류 폴더 자체를 생략하지 않는다 — 빈 `presentation_layer` 라도 `__init__.py` 만 "
            "둔 빈 패키지로 만든다(예: ACL·published_service 로만 소비되는 내부 전용 BC). "
            "고정명 종류 폴더(`presentation_layer/api`·`presentation_layer/schema`·`infra_layer/acl`)는 "
            "§0-4 개정(2026-06-08)으로 표현/통합이 없어도 무조건 빈 패키지로 둔다 — 데이터소스 BC 도 "
            "예외 없다(`architecture-ddd` §632-(2) 면제는 *판정 실내용(.py)*에 한정). 이미 만든 "
            "`domain_layer/<aggregate>/` 는 코어 종류(`entity`·`value_object`·`repository` + "
            "`exception.py`)를 빠짐없이 갖춘다. 완전 평면 앱은 4계층으로 분리하라. "
            "외래 port 발견이면: 협력 포트(타 BC 소비용 역할 추상 ABC)는 "
            "`domain_layer/<aggregate>/port/` 로 옮긴다 — 포트를 호출하는 것이 application "
            "유스케이스(command)이고 애그리거트가 직접 import 하지 않아도, 'use-case dependency' "
            "재분류로 `application_layer/<feature>/port/` 에 두지 않는다(§2 — command 가 "
            "*domain-owned* port 에 의존하는 것이 DIP 다). ACL *구현*(어댑터)은 `infra_layer/acl/` "
            "직속이다(port/ 하위 아님). 네트워크/시리얼 '포트' 같은 기술 유틸이면 `port/` 는 이 "
            "표준에서 협력 포트 전용 명칭이니 의미에 맞는 다른 폴더명을 쓴다. 접을/옮길 수 없는 "
            "실질 사유가 있으면 코드로 박지 말고 설계(G1 트레이드오프)로 반송하라."
        )
    return 2 if new_root_apps or findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
