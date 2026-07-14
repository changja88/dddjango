#!/usr/bin/env python3
"""dddjango migration 무변경 경계 결정적 백스톱.

이 스크립트는 migration의 Python 내용, operation, 의도, 안전성을 해석하지 않는다. 지정한
TARGET_DIR에서 정적 등록 또는 실제 Django ``AppConfig`` 상속으로 식별한 로컬 앱의
``migrations`` 디렉터리 아래 directory·regular file·symlink를 상대 경로·종류·SHA-256으로
기록하고, 같은 baseline과 이후 상태가 byte-level로 같은지 비교한다. 저장소 안을 가리키는
symlink만 target 내용을 읽으며, 저장소 밖 target은 link 자체와 ``outside-root`` scope만
opaque hash에 포함하고 target 내용은 읽지 않는다. Python interpreter가
재생성하는 ``__pycache__/`` subtree만 비교에서 제외한다. 그 밖의 위치에 놓인
``.pyc``·``.pyo``는 opaque artifact로 추적한다. 디렉터리는 빈 바이트의
고정 SHA-256을 구조 sentinel로 쓴다. 제한된 정적 문법으로 완전히 해석되는
``MIGRATION_MODULES`` 대입의 원문 line 범위와 repo-root/``src`` 아래 custom package도 opaque
entry로 포함하고, 동적·mutable alias 구성은 fail-closed한다.
permission·owner·xattr metadata는 포함하지 않는다. 테스트의 migration lifecycle 소유 여부는 파일명으로 판정할 수 없으므로 의미
감사로 추정하지 않고 외부가 선언한 exact file만 별도 opaque 경계로 받는다. 기존 Django app의 marker 경로는 내용이 아니라 위치 identity만 기록해 물리
이동을 막고 새 app 추가는 허용한다. 기존 dirty 상태도 snapshot
시점 그대로 baseline에 포함하며, 안정된 endpoint를 확인하려고 각 scan을 연속 두 번 수행한다.
정적 ``INSTALLED_APPS`` 등록 없이 symlink 디렉터리 아래 중첩된 AppConfig 앱은 순회하지
않는다(그 symlink 자체가 식별된 app root인 경우는 추적한다).
STATE_FILE은 run별 write-once baseline이며 동명 ``.write-once`` receipt가 절대 경로와 SHA-256을
고정한다. 어느 한쪽이라도 이미 존재하거나 누락·변조되면 재기준화하지 않고 사용 오류로 중단한다.

사용법:
  check-migration-boundary.py preflight TARGET_DIR STATE_PATH
  check-migration-boundary.py snapshot TARGET_DIR STATE_FILE
  check-migration-boundary.py verify TARGET_DIR STATE_FILE
  check-migration-boundary.py cleanup TARGET_DIR STATE_FILE RUN_ID
  check-migration-boundary.py recover TARGET_DIR STATE_DIR

``recover``는 다른 coordinator가 실행 중이지 않은 정지 상태에서만 쓰는 호환성·유지보수
진단이다. 정상 run은 고유 STATE_FILE을 직접 snapshot/verify/cleanup하며 다른 run의 pair를
순회하지 않는다. 종료코드: 0=snapshot/clean/cleanup, 2=추가·수정·삭제 발견,
1=사용·baseline·I/O 오류.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import tokenize
from pathlib import Path, PurePosixPath
from typing import Iterable, Protocol

MANIFEST_FORMAT = "dddjango-migration-boundary-v11"
ENTRY_KINDS = {"configuration", "directory", "file", "missing", "symlink"}
SKIP_DIRS = {
    ".cache",
    ".eggs",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "htmlcov",
    "node_modules",
    "site-packages",
    "venv",
}
BUFFER_SIZE = 1024 * 1024
DIRECTORY_DIGEST = hashlib.sha256(b"").hexdigest()
MISSING_DIGEST = hashlib.sha256(b"missing").hexdigest()
EPOCH_STATE_FILE = re.compile(r"^migration-boundary-epoch-[^/]+\.json$")
EPOCH_RECEIPT_SUFFIX = ".write-once"
RECEIPT_FORMAT = "dddjango-migration-boundary-receipt-v2"
SETTINGS_ENTRYPOINT_NAMES = {"asgi.py", "manage.py", "wsgi.py"}
PYTHON_CACHE_DIRECTORIES = {"__pycache__"}
EXTERNAL_OWNED_PATHS_ENV = "DDDJANGO_EXTERNAL_OWNED_OPAQUE_PATHS_JSON"
SAFE_EXTERNAL_OWNED_PATH = re.compile(r"^[A-Za-z0-9_./@+\-]+$")
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{7,127}$")
_SEMANTIC_EXCLUSIONS: dict[Path, tuple[PurePosixPath, ...]] = {}


class ManifestError(ValueError):
    """Baseline manifest가 경계 계약을 만족하지 않을 때 발생한다."""


def _normalize_relative_paths(raw_paths: object, label: str) -> list[str]:
    if not isinstance(raw_paths, list) or not all(
        isinstance(item, str) and item for item in raw_paths
    ):
        raise ManifestError(f"{label}가 문자열 목록이 아니다")
    paths = list(raw_paths)
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ManifestError(f"{label}가 정렬된 고유 목록이 아니다")
    for item in paths:
        path = PurePosixPath(item)
        if (
            item == "."
            or not path.parts
            or path.is_absolute()
            or path.as_posix() != item
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise ManifestError(f"{label} 항목이 상대 정규 경로가 아니다: {item!r}")
    return paths


def _external_owned_paths_from_environment(root: Path) -> list[str]:
    raw = os.environ.get(EXTERNAL_OWNED_PATHS_ENV)
    if raw is None:
        raise ManifestError(
            f"snapshot에는 {EXTERNAL_OWNED_PATHS_ENV} canonical JSON 배열이 필요하다"
        )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ManifestError(
            f"{EXTERNAL_OWNED_PATHS_ENV}가 올바른 JSON이 아니다"
        ) from error
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(
            f"{EXTERNAL_OWNED_PATHS_ENV}가 문자열 JSON 배열이 아니다"
        )
    normalized = sorted(set(value))
    paths = _normalize_relative_paths(normalized, "external-owned opaque paths")
    for item in paths:
        if SAFE_EXTERNAL_OWNED_PATH.fullmatch(item) is None:
            raise ManifestError(
                "external-owned opaque path에는 shell-safe portable 문자만 허용한다 "
                f"([A-Za-z0-9_./@+-]): {item!r}"
            )
        candidate = root / item
        current = root
        for part in PurePosixPath(item).parts:
            current = current / part
            if current.is_symlink():
                raise ManifestError(
                    "external-owned opaque path와 그 조상에는 symlink를 허용하지 "
                    f"않는다: {item!r}"
                )
        try:
            candidate.resolve(strict=True).relative_to(root)
            metadata = candidate.lstat()
            mode = metadata.st_mode
        except (OSError, RuntimeError, ValueError) as error:
            raise ManifestError(
                "external-owned opaque path는 G0에 존재하는 file이어야 한다: "
                f"{item!r}"
            ) from error
        if not stat.S_ISREG(mode):
            raise ManifestError(
                "external-owned opaque path는 exact file이어야 하며 directory/special "
                f"path는 허용하지 않는다: {item!r}"
            )
        _reject_hardlinked_regular(candidate, metadata)
    structural_names = SETTINGS_ENTRYPOINT_NAMES | {
        "apps.py",
        "models.py",
        "settings.py",
    }
    for item in paths:
        if PurePosixPath(item).name in structural_names:
            raise ManifestError(
                "external-owned opaque path가 Django structural discovery source와 "
                f"겹친다: {item!r}"
            )
    declared_settings = _static_settings_module_paths(root)
    for item in paths:
        if _is_settings_source(Path(item), declared_settings):
            raise ManifestError(
                "external-owned opaque path가 선언된 Django settings source와 "
                f"겹친다: {item!r}"
            )
    registered_config_sources = {
        source.relative_to(root).as_posix()
        for source in _registered_app_config_sources(root)
    }
    overlap = sorted(set(paths) & registered_config_sources)
    if overlap:
        raise ManifestError(
            "external-owned opaque path가 등록된 AppConfig source와 겹친다: "
            + ", ".join(overlap)
        )
    return paths


def _add_semantic_exclusions(root: Path, paths: Iterable[str]) -> None:
    existing = set(_SEMANTIC_EXCLUSIONS.get(root, ()))
    for path in paths:
        existing.add(PurePosixPath(path))
        try:
            resolved = (root / path).resolve(strict=False)
            relative = PurePosixPath(resolved.relative_to(root).as_posix())
        except (OSError, RuntimeError, ValueError):
            continue
        if relative.parts and relative.as_posix() != ".":
            existing.add(relative)
    _SEMANTIC_EXCLUSIONS[root] = tuple(
        sorted(existing, key=lambda item: item.as_posix())
    )


def _is_semantic_excluded_path(root: Path, path: Path) -> bool:
    prefixes = _SEMANTIC_EXCLUSIONS.get(root, ())
    if not prefixes:
        return False
    candidates: list[PurePosixPath] = []
    try:
        candidates.append(PurePosixPath(path.relative_to(root).as_posix()))
    except ValueError:
        return True
    try:
        resolved = path.resolve(strict=False)
        candidates.append(PurePosixPath(resolved.relative_to(root).as_posix()))
    except (OSError, RuntimeError, ValueError):
        return True
    return any(
        candidate == prefix or candidate.is_relative_to(prefix)
        for candidate in candidates
        for prefix in prefixes
    )


class _Digest(Protocol):
    """hashlib 구현 세부 타입에 기대지 않는 최소 digest 쓰기 계약."""

    def update(self, data: bytes) -> None: ...


def _sha256_file(path: Path) -> str:
    before = path.stat(follow_symlinks=False)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(BUFFER_SIZE):
            digest.update(chunk)
    after = path.stat(follow_symlinks=False)
    before_identity = (
        before.st_dev,
        before.st_ino,
        before.st_mode,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    after_identity = (
        after.st_dev,
        after.st_ino,
        after.st_mode,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    )
    if before_identity != after_identity:
        raise ManifestError(f"scan 도중 파일이 변경됐다: {path}")
    return digest.hexdigest()


def _reject_hardlinked_regular(path: Path, metadata: os.stat_result) -> None:
    if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1:
        raise ManifestError(
            "opaque-owned file의 hardlink alias는 안전하게 prune할 수 없다: "
            f"{path} (links={metadata.st_nlink})"
        )


def _digest_token(digest: _Digest, *parts: object) -> None:
    payload = json.dumps(parts, ensure_ascii=True, separators=(",", ":")).encode()
    digest.update(len(payload).to_bytes(8, byteorder="big"))
    digest.update(payload)


def _is_within_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolved_target_marker(root: Path, path: Path) -> str:
    """절대 경로를 노출하지 않는 symlink target scope marker."""
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        try:
            resolved = path.resolve(strict=False)
        except (OSError, RuntimeError):
            return f"unavailable:{type(error).__name__}"
    if not _is_within_root(root, resolved):
        return "outside-root"
    relative = resolved.relative_to(root).as_posix()
    return f"inside:{relative or '.'}"


def _first_external_symlink(root: Path, path: Path) -> Path | None:
    """root부터 path까지 처음으로 저장소 밖을 가리키는 lexical symlink."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    current = root
    for part in relative.parts:
        current = current / part
        try:
            is_link = current.is_symlink()
        except OSError:
            return current
        if not is_link:
            continue
        marker = _resolved_target_marker(root, current)
        if not marker.startswith("inside:"):
            return current
    return None


def _path_resolves_within_root(root: Path, path: Path) -> bool:
    if _first_external_symlink(root, path) is not None:
        return False
    try:
        return _is_within_root(root, path.resolve(strict=True))
    except (OSError, RuntimeError):
        return False


def _sha256_followed_target(
    root: Path,
    path: Path,
    seen: set[tuple[int, int]],
) -> str:
    marker = _resolved_target_marker(root, path)
    if not marker.startswith("inside:"):
        return hashlib.sha256(marker.encode()).hexdigest()
    try:
        followed = path.stat()
    except (OSError, RuntimeError) as error:
        return hashlib.sha256(
            f"unavailable:{type(error).__name__}".encode()
        ).hexdigest()

    inode = (followed.st_dev, followed.st_ino)
    if inode in seen:
        return hashlib.sha256(b"cycle").hexdigest()
    next_seen = seen | {inode}

    if stat.S_ISREG(followed.st_mode):
        _reject_hardlinked_regular(path.resolve(strict=True), followed)
        return _sha256_file(path.resolve(strict=True))
    if not stat.S_ISDIR(followed.st_mode):
        return hashlib.sha256(f"special:{followed.st_mode}".encode()).hexdigest()

    digest = hashlib.sha256()
    for current_raw, dir_names, file_names in os.walk(
        path,
        topdown=True,
        onerror=_raise_walk_error,
        followlinks=False,
    ):
        current = Path(current_raw)
        relative_current = current.relative_to(path)
        traversable: list[str] = []
        for name in sorted(dir_names):
            if name in PYTHON_CACHE_DIRECTORIES:
                continue
            child = current / name
            relative = (relative_current / name).as_posix()
            if child.is_symlink():
                _digest_token(
                    digest,
                    "symlink",
                    relative,
                    _sha256_symlink(root, child, next_seen),
                )
                continue
            _digest_token(digest, "directory", relative)
            traversable.append(name)
        dir_names[:] = traversable
        for name in sorted(file_names):
            child = current / name
            relative = (relative_current / name).as_posix()
            if child.is_symlink():
                _digest_token(
                    digest,
                    "symlink",
                    relative,
                    _sha256_symlink(root, child, next_seen),
                )
                continue
            metadata = child.lstat()
            mode = metadata.st_mode
            if stat.S_ISREG(mode):
                _reject_hardlinked_regular(child, metadata)
                _digest_token(digest, "file", relative, _sha256_file(child))
            else:
                _digest_token(digest, "special", relative, mode)
    return digest.hexdigest()


def _sha256_symlink(
    root: Path,
    path: Path,
    seen: set[tuple[int, int]] | None = None,
) -> str:
    target = os.readlink(path)
    digest = hashlib.sha256()
    _digest_token(digest, "target", os.fsdecode(target))
    _digest_token(digest, "resolved", _resolved_target_marker(root, path))
    _digest_token(
        digest,
        "followed",
        _sha256_followed_target(root, path, seen or set()),
    )
    return digest.hexdigest()


def _symlink_payload(root: Path, path: Path) -> str:
    return json.dumps(
        {
            "resolved": _resolved_target_marker(root, path),
            "target": os.fsdecode(os.readlink(path)),
        },
        ensure_ascii=True,
        separators=(",", ":"),
    )


def _relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _entry(root: Path, path: Path, kind: str) -> dict[str, str]:
    if kind == "symlink":
        digest = _sha256_symlink(root, path)
    elif kind == "file":
        _reject_hardlinked_regular(path, path.lstat())
        digest = _sha256_file(path)
    else:
        digest = DIRECTORY_DIGEST
    return {"path": _relative_path(root, path), "kind": kind, "sha256": digest}


def _synthetic_entry(path: str, kind: str, payload: str) -> dict[str, str]:
    return {
        "path": path,
        "kind": kind,
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def _raise_walk_error(error: OSError) -> None:
    raise error


def _read_python_text(root: Path, path: Path) -> str:
    """Opaque 경계를 넘지 않는 regular Python structural source만 읽는다."""
    try:
        lexical = path.relative_to(root)
        resolved = path.resolve(strict=True)
        resolved_relative = resolved.relative_to(root)
        metadata = resolved.stat()
    except (OSError, RuntimeError, ValueError) as error:
        raise ManifestError(f"Python structural source를 안전하게 읽을 수 없다: {path}") from error
    if (
        "migrations" in lexical.parts
        or "migrations" in resolved_relative.parts
        or _is_semantic_excluded_path(root, path)
    ):
        raise ManifestError(
            "Python structural source가 opaque migration 경계와 겹친다: "
            f"{lexical.as_posix()}"
        )
    if not stat.S_ISREG(metadata.st_mode):
        raise ManifestError(
            "Python structural source는 regular file이어야 한다: "
            f"{lexical.as_posix()}"
        )
    _reject_hardlinked_regular(resolved, metadata)
    with tokenize.open(path) as stream:
        return stream.read()


def _linked_python_sources(
    root: Path,
    link: Path,
) -> list[tuple[Path, Path, str]]:
    """symlink directory chain을 따라 Python source와 논리 경로·link chain을 반환한다."""
    sources: list[tuple[Path, Path, str]] = []
    if _is_semantic_excluded_path(root, link) or not _path_resolves_within_root(
        root, link
    ):
        return sources

    def visit(
        directory: Path,
        logical: PurePosixPath,
        seen: set[tuple[int, int]],
        links: tuple[tuple[str, str, str], ...],
    ) -> None:
        if _is_semantic_excluded_path(
            root, directory
        ) or not _path_resolves_within_root(root, directory):
            return
        try:
            followed = directory.stat()
        except (OSError, RuntimeError):
            return
        if not stat.S_ISDIR(followed.st_mode):
            return
        inode = (followed.st_dev, followed.st_ino)
        if inode in seen:
            return
        next_seen = seen | {inode}
        next_links = links
        if directory.is_symlink():
            next_links = links + (
                (
                    logical.as_posix(),
                    os.readlink(directory),
                    _resolved_target_marker(root, directory),
                ),
            )
        for child in sorted(directory.iterdir(), key=lambda item: item.name):
            child_logical = logical / child.name
            if _is_semantic_excluded_path(root, child):
                continue
            if child.is_symlink() and not _path_resolves_within_root(root, child):
                continue
            try:
                is_directory = child.is_dir()
            except (OSError, RuntimeError):
                continue
            if is_directory:
                if child.name not in SKIP_DIRS:
                    visit(child, child_logical, next_seen, next_links)
                continue
            if child.suffix != ".py":
                continue
            file_links = next_links
            if child.is_symlink():
                file_links = next_links + (
                    (
                        child_logical.as_posix(),
                        os.readlink(child),
                        _resolved_target_marker(root, child),
                    ),
                )
            sources.append(
                (
                    child,
                    Path(child_logical.as_posix()),
                    json.dumps(file_links, ensure_ascii=True, separators=(",", ":")),
                )
            )

    visit(link, PurePosixPath(link.relative_to(root).as_posix()), set(), ())
    return sorted(sources, key=lambda item: item[1].as_posix())


def _scan_named_migration_tree(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for directory in sorted(_candidate_app_directories(root)):
        migration_root = directory / "migrations"
        if migration_root.exists() or migration_root.is_symlink():
            entries.extend(_scan_explicit_root(root, migration_root))
    return entries


def _assignment_value(node: ast.AST, variable_name: str) -> ast.AST | None:
    if isinstance(node, ast.Assign):
        if any(
            isinstance(target, ast.Name) and target.id == variable_name
            for target in node.targets
        ):
            return node.value
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == variable_name:
            return node.value
    return None


class _ModuleAssignmentCollector(ast.NodeVisitor):
    """모듈 실행 흐름의 MIGRATION_MODULES만 모으고 함수·클래스 로컬은 제외한다."""

    def __init__(self, variable_name: str) -> None:
        self.variable_name = variable_name
        self.records: list[tuple[ast.stmt, ast.AST]] = []
        self.values: list[ast.AST] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        value = _assignment_value(node, self.variable_name)
        if value is not None:
            self.records.append((node, value))
            self.values.append(value)
        self.generic_visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        value = _assignment_value(node, self.variable_name)
        if value is not None:
            self.records.append((node, value))
            self.values.append(value)
        if node.value is not None:
            self.generic_visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if (
            isinstance(node.op, (ast.Add, ast.BitOr))
            and isinstance(node.target, ast.Name)
            and node.target.id == self.variable_name
        ):
            self.records.append((node, node.value))
            self.values.append(node.value)
        self.generic_visit(node.value)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return


def _module_assignment_values(
    tree: ast.Module,
    variable_name: str = "MIGRATION_MODULES",
) -> list[ast.AST]:
    collector = _ModuleAssignmentCollector(variable_name)
    collector.visit(tree)
    return collector.values


def _module_assignment_records(
    tree: ast.Module,
    variable_name: str = "MIGRATION_MODULES",
) -> list[tuple[ast.stmt, ast.AST]]:
    collector = _ModuleAssignmentCollector(variable_name)
    collector.visit(tree)
    return collector.records


def _statement_source_lines(text: str, statement: ast.stmt) -> str:
    """assignment가 점유한 원문 line 전체(후행 주석 포함)를 반환한다."""
    end_lineno = getattr(statement, "end_lineno", None)
    if not isinstance(statement.lineno, int) or not isinstance(end_lineno, int):
        return ast.dump(statement, annotate_fields=True, include_attributes=False)
    lines = text.splitlines(keepends=True)
    return "".join(lines[statement.lineno - 1 : end_lineno])


def _module_static_assignments_before(
    tree: ast.Module,
    before_lineno: int,
) -> dict[str, ast.AST]:
    assignments: dict[str, ast.AST] = {}
    for statement in tree.body:
        if statement.lineno >= before_lineno:
            break
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            assignments[statement.target.id] = statement.value
    return assignments


def _module_assignment_counts_before(
    tree: ast.Module,
    before_lineno: int,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for statement in tree.body:
        if statement.lineno >= before_lineno:
            break
        targets: list[ast.AST] = []
        if isinstance(statement, ast.Assign):
            targets.extend(statement.targets)
        elif isinstance(statement, ast.AnnAssign):
            targets.append(statement.target)
        elif isinstance(statement, ast.AugAssign):
            targets.append(statement.target)
        for target in targets:
            if isinstance(target, ast.Name):
                counts[target.id] = counts.get(target.id, 0) + 1
    return counts


def _static_dependency_names(
    value: ast.AST,
    assignments: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> set[str]:
    names = {
        node.id
        for node in ast.walk(value)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    dependencies = set(names)
    for name in names - set(seen):
        assigned = assignments.get(name)
        if assigned is not None:
            dependencies.update(
                _static_dependency_names(
                    assigned,
                    assignments,
                    seen | {name},
                )
            )
    return dependencies


def _module_mutated_names(
    tree: ast.Module,
    include_augmented_names: bool = True,
) -> set[str]:
    mutated: set[str] = set()

    class Collector(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute):
                owner = self._root_name(node.func.value)
                if owner is not None:
                    mutated.add(owner)
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                self._record_target(target)
            self.generic_visit(node.value)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            self._record_target(node.target)
            if node.value is not None:
                self.generic_visit(node.value)

        def visit_AugAssign(self, node: ast.AugAssign) -> None:
            self._record_target(
                node.target,
                include_name=include_augmented_names,
            )
            self.generic_visit(node.value)

        def visit_Delete(self, node: ast.Delete) -> None:
            for target in node.targets:
                self._record_target(target, include_name=True)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            return

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            return

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return

        def _record_target(
            self,
            target: ast.AST,
            include_name: bool = False,
        ) -> None:
            if isinstance(target, ast.Name) and include_name:
                mutated.add(target.id)
            elif isinstance(target, ast.Subscript) and isinstance(
                self._root_name(target.value),
                str,
            ):
                owner = self._root_name(target.value)
                if owner is not None:
                    mutated.add(owner)
            elif isinstance(target, ast.Attribute):
                owner = self._root_name(target.value)
                if owner is not None:
                    mutated.add(owner)

        def _root_name(self, expression: ast.AST) -> str | None:
            current = expression
            while isinstance(current, (ast.Attribute, ast.Subscript)):
                current = current.value
            return current.id if isinstance(current, ast.Name) else None

    collector = Collector()
    for statement in tree.body:
        collector.visit(statement)

    class ControlAssignmentCollector(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                mutated.add(node.id)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            return

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            return

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            return

        def visit_Lambda(self, node: ast.Lambda) -> None:
            return

    control_collector = ControlAssignmentCollector()
    control_statements = (
        ast.AsyncFor,
        ast.AsyncWith,
        ast.For,
        ast.If,
        ast.Match,
        ast.Try,
        ast.While,
        ast.With,
    )
    for statement in tree.body:
        if isinstance(statement, control_statements):
            control_collector.visit(statement)

    bindings: dict[str, list[ast.AST]] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    bindings.setdefault(target.id, []).append(statement.value)
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            bindings.setdefault(statement.target.id, []).append(statement.value)
    changed = True
    while changed:
        changed = False
        for name in tuple(mutated):
            for value in bindings.get(name, []):
                dependencies = {
                    node.id
                    for node in ast.walk(value)
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                }
                before = len(mutated)
                mutated.update(dependencies)
                changed = changed or len(mutated) != before
    return mutated


def _static_string_value(
    value: ast.AST,
    assignments: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> tuple[bool, str | None]:
    if isinstance(value, ast.Constant) and (
        isinstance(value.value, str) or value.value is None
    ):
        return True, value.value
    if isinstance(value, ast.Name):
        if value.id in seen or value.id not in assignments:
            return False, None
        return _static_string_value(
            assignments[value.id],
            assignments,
            seen | {value.id},
        )
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
        left_complete, left = _static_string_value(value.left, assignments, seen)
        right_complete, right = _static_string_value(value.right, assignments, seen)
        if (
            left_complete
            and right_complete
            and isinstance(left, str)
            and isinstance(right, str)
        ):
            return True, left + right
    return False, None


def _static_migration_module_strings(
    value: ast.AST,
    assignments: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> set[str] | None:
    """완전히 정적인 dict/union의 module 문자열만 반환한다."""
    if isinstance(value, ast.Name):
        if value.id in seen or value.id not in assignments:
            return None
        return _static_migration_module_strings(
            assignments[value.id],
            assignments,
            seen | {value.id},
        )
    if isinstance(value, ast.Dict):
        modules: set[str] = set()
        for key, item in zip(value.keys, value.values, strict=True):
            key_complete, key_value = (
                (False, None)
                if key is None
                else _static_string_value(key, assignments, seen)
            )
            item_complete, item_value = _static_string_value(
                item,
                assignments,
                seen,
            )
            if not key_complete or not isinstance(key_value, str) or not item_complete:
                return None
            if isinstance(item_value, str):
                modules.add(item_value)
        return modules
    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr):
        left = _static_migration_module_strings(value.left, assignments, seen)
        right = _static_migration_module_strings(value.right, assignments, seen)
        if left is None or right is None:
            return None
        return left | right
    return None


def _static_string_items(
    value: ast.AST,
    assignments: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> tuple[bool, set[str]]:
    """직접 list/tuple/set 및 정적 `+`/`|` 결합에서 문자열 원소를 수집한다."""
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return True, {value.value}
    if isinstance(value, ast.Name):
        if value.id in seen or value.id not in assignments:
            return False, set()
        return _static_string_items(
            assignments[value.id],
            assignments,
            seen | {value.id},
        )
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        items: set[str] = set()
        for element in value.elts:
            complete, nested = _static_string_items(element, assignments, seen)
            if not complete:
                return False, set()
            items.update(nested)
        return True, items
    if isinstance(value, ast.BinOp) and isinstance(value.op, (ast.Add, ast.BitOr)):
        left_complete, left = _static_string_items(value.left, assignments, seen)
        right_complete, right = _static_string_items(value.right, assignments, seen)
        return left_complete and right_complete, left | right
    return False, set()


def _settings_entrypoint_candidates(root: Path) -> list[Path]:
    """Path shape만으로 Django project entrypoint 후보를 제한한다."""
    candidates = {
        root / "manage.py",
        root / "asgi.py",
        root / "wsgi.py",
        root / "src" / "manage.py",
        root / "src" / "asgi.py",
        root / "src" / "wsgi.py",
    }
    for source_root in _lexical_source_roots(root):
        if not source_root.is_dir() or source_root.is_symlink():
            continue
        try:
            children = sorted(source_root.iterdir(), key=lambda path: path.name)
        except OSError as error:
            raise ManifestError(f"entrypoint 후보를 나열할 수 없다: {source_root}") from error
        for child in children:
            if (
                child.name in SKIP_DIRS
                or child.name == "migrations"
                or child.is_symlink()
                or not child.is_dir()
            ):
                continue
            candidates.add(child / "asgi.py")
            candidates.add(child / "wsgi.py")
    return sorted(
        candidates,
        key=lambda path: (path.name != "manage.py", path.as_posix()),
    )


def _static_settings_module_paths(root: Path) -> set[str]:
    """구조적으로 한정한 Django entrypoint의 literal settings 경로를 찾는다."""
    paths: set[str] = set()
    for source in _settings_entrypoint_candidates(root):
        if source.is_symlink():
            raise ManifestError(
                "Django settings entrypoint symlink는 안전하게 추적할 수 없어 "
                f"지원하지 않는다: {source.relative_to(root).as_posix()}"
            )
        if (
            "migrations" in source.relative_to(root).parts[:-1]
            or _is_semantic_excluded_path(root, source)
            or not source.is_file()
        ):
            continue
        try:
            tree = ast.parse(_read_python_text(root, source), filename=str(source))
        except (OSError, UnicodeError, SyntaxError) as error:
            raise ManifestError(
                "Django settings entrypoint를 정적으로 해석할 수 없다: "
                f"{source.relative_to(root).as_posix()}"
            ) from error
        mutated_names = _module_mutated_names(tree)
        os_aliases: set[str] = set()
        environ_aliases: set[str] = set()
        for imported_node in ast.walk(tree):
            if isinstance(imported_node, ast.Import):
                for imported in imported_node.names:
                    if imported.name == "os":
                        os_aliases.add(imported.asname or "os")
            elif (
                isinstance(imported_node, ast.ImportFrom)
                and imported_node.module == "os"
            ):
                for imported in imported_node.names:
                    if imported.name == "environ":
                        environ_aliases.add(imported.asname or "environ")
        declared_modules: set[str] = set()
        for node in ast.walk(tree):
            key: ast.AST | None = None
            value: ast.AST | None = None
            if isinstance(node, ast.Call) and len(node.args) >= 2:
                function = node.func
                if (
                    isinstance(function, ast.Attribute)
                    and function.attr == "setdefault"
                    and _is_environ_expression(
                        function.value,
                        os_aliases,
                        environ_aliases,
                    )
                ):
                    key, value = node.args[:2]
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    subscript_key = _environ_subscript_key(
                        target,
                        os_aliases,
                        environ_aliases,
                    )
                    if subscript_key is not None:
                        key, value = subscript_key, node.value
                        break
            elif isinstance(node, ast.AnnAssign):
                subscript_key = _environ_subscript_key(
                    node.target,
                    os_aliases,
                    environ_aliases,
                )
                if subscript_key is not None:
                    key, value = subscript_key, node.value
            if not (
                isinstance(key, ast.Constant)
                and key.value == "DJANGO_SETTINGS_MODULE"
            ):
                continue
            if value is None:
                complete, settings_module = False, None
            else:
                assignments = _module_static_assignments_before(
                    tree,
                    node.lineno,
                )
                dependencies = _static_dependency_names(value, assignments)
                assignment_counts = _module_assignment_counts_before(
                    tree,
                    node.lineno,
                )
                if dependencies & mutated_names or any(
                    assignment_counts.get(name, 0) > 1
                    for name in dependencies
                ):
                    raise ManifestError(
                        "DJANGO_SETTINGS_MODULE이 재할당·변이된 module-level alias에 "
                        "의존해 opaque migration scope를 정적으로 확정할 수 없다: "
                        f"{source.relative_to(root).as_posix()}"
                    )
                complete, settings_module = _static_string_value(
                    value,
                    assignments,
                )
            if not complete or not isinstance(settings_module, str):
                raise ManifestError(
                    "DJANGO_SETTINGS_MODULE은 opaque migration scope를 확정할 수 "
                    f"있도록 정적 문자열이어야 한다: {source.relative_to(root).as_posix()}"
                )
            declared_modules.add(settings_module)
        for module in declared_modules:
            parts = module.split(".")
            if not parts or not all(part.isidentifier() for part in parts):
                continue
            if "migrations" in parts:
                raise ManifestError(
                    "Django settings source와 standard migration 경로를 겸용할 수 "
                    f"없다: {module!r}"
                )
            module_path = Path(*parts)
            for source_root in _lexical_source_roots(root):
                prefix = source_root.relative_to(root)
                logical_module = prefix / module_path
                paths.add(logical_module.with_suffix(".py").as_posix())
                paths.add((logical_module / "__init__.py").as_posix())
    return paths


def _is_environ_expression(
    expression: ast.AST,
    os_aliases: set[str],
    environ_aliases: set[str],
) -> bool:
    return (
        isinstance(expression, ast.Name)
        and expression.id in environ_aliases
    ) or (
        isinstance(expression, ast.Attribute)
        and expression.attr == "environ"
        and isinstance(expression.value, ast.Name)
        and expression.value.id in os_aliases
    )


def _environ_subscript_key(
    expression: ast.AST,
    os_aliases: set[str],
    environ_aliases: set[str],
) -> ast.AST | None:
    if not isinstance(expression, ast.Subscript) or not _is_environ_expression(
        expression.value,
        os_aliases,
        environ_aliases,
    ):
        return None
    return expression.slice


def _is_settings_source(logical_path: Path, declared_paths: set[str]) -> bool:
    """정적 entrypoint가 지목한 모듈·패키지 또는 root settings.py만 인정한다."""
    logical = PurePosixPath(logical_path.as_posix())
    if logical.as_posix() == "settings.py" or logical.as_posix() in declared_paths:
        return True
    return any(
        logical.parent == PurePosixPath(declared).parent
        and logical.parent.name == "settings"
        for declared in declared_paths
    )


def _settings_sources(root: Path) -> list[tuple[Path, Path, str | None]]:
    """(실제 읽을 path, root 기준 논리 path, symlink marker)를 반환한다."""
    sources: dict[str, tuple[Path, Path, str | None]] = {}
    declared_paths = _static_settings_module_paths(root)
    for current_raw, dir_names, file_names in os.walk(
        root,
        topdown=True,
        onerror=_raise_walk_error,
        followlinks=False,
    ):
        current = Path(current_raw)
        if _is_semantic_excluded_path(root, current):
            dir_names[:] = []
            continue
        traversable: list[str] = []
        for name in sorted(dir_names):
            if name in PYTHON_CACHE_DIRECTORIES:
                continue
            child = current / name
            if name in SKIP_DIRS:
                continue
            if _is_semantic_excluded_path(root, child):
                continue
            if child.is_symlink():
                logical_prefix = PurePosixPath(child.relative_to(root).as_posix())
                if not any(
                    PurePosixPath(declared).is_relative_to(logical_prefix)
                    for declared in declared_paths
                ):
                    continue
                for source, logical, link_marker in _linked_python_sources(
                    root, child
                ):
                    if _is_settings_source(logical, declared_paths):
                        sources[logical.as_posix()] = (
                            source,
                            logical,
                            f"ancestors:{link_marker}",
                        )
                continue
            traversable.append(name)
        dir_names[:] = traversable
        for name in sorted(file_names):
            source = current / name
            if _is_semantic_excluded_path(root, source):
                continue
            logical = source.relative_to(root)
            if source.suffix != ".py" or not _is_settings_source(
                logical, declared_paths
            ):
                continue
            if source.is_symlink() and not _path_resolves_within_root(root, source):
                continue
            marker = (
                f"file:{_symlink_payload(root, source)}"
                if source.is_symlink()
                else None
            )
            sources[logical.as_posix()] = (source, logical, marker)
    return [sources[path] for path in sorted(sources)]


def _external_settings_link_entries(root: Path) -> list[dict[str, str]]:
    """정적 settings 경로의 repo-side external link만 동결하고 target은 읽지 않는다."""
    logical_paths = set(_static_settings_module_paths(root)) | {"settings.py"}
    entries: dict[str, dict[str, str]] = {}
    for logical in sorted(logical_paths):
        link = _first_external_symlink(root, root / logical)
        if link is None:
            continue
        relative = link.relative_to(root).as_posix()
        path = f".dddjango-settings-link/{relative}"
        entries[path] = _synthetic_entry(
            path,
            "configuration",
            _symlink_payload(root, link),
        )
    return [entries[path] for path in sorted(entries)]


def _declared_app_registrations(root: Path) -> list[str]:
    registrations: set[str] = set()
    for source, logical, link_marker in _settings_sources(root):
        try:
            text = _read_python_text(root, source)
        except (OSError, SyntaxError, UnicodeError) as error:
            raise ManifestError(
                f"Django settings source를 읽을 수 없다: {logical.as_posix()}"
            ) from error
        if "INSTALLED_APPS" not in text:
            continue
        try:
            tree = ast.parse(text, filename=str(source))
        except SyntaxError as error:
            raise ManifestError(
                f"Django settings source를 해석할 수 없다: {logical.as_posix()}"
            ) from error
        records = _module_assignment_records(tree, "INSTALLED_APPS")
        mutated_names = _module_mutated_names(tree)
        unsafe_mutated_names = _module_mutated_names(
            tree,
            include_augmented_names=False,
        )
        if "INSTALLED_APPS" in unsafe_mutated_names:
            raise ManifestError(
                "INSTALLED_APPS의 method/subscript mutation은 opaque migration "
                f"scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
            )
        for statement, value in records:
            if statement not in tree.body:
                raise ManifestError(
                    "INSTALLED_APPS의 조건부·중첩 대입은 opaque migration scope를 "
                    f"정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            if isinstance(value, ast.Name):
                raise ManifestError(
                    "INSTALLED_APPS의 mutable Name alias 직접 대입은 opaque migration "
                    f"scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            assignments = _module_static_assignments_before(
                tree,
                statement.lineno,
            )
            dependencies = _static_dependency_names(value, assignments)
            assignment_counts = _module_assignment_counts_before(
                tree,
                statement.lineno,
            )
            if dependencies & mutated_names or any(
                assignment_counts.get(name, 0) > 1 for name in dependencies
            ):
                raise ManifestError(
                    "INSTALLED_APPS가 재할당·변이된 module-level alias에 의존해 opaque "
                    f"migration scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            complete, app_names = _static_string_items(value, assignments)
            if not complete:
                raise ManifestError(
                    "INSTALLED_APPS는 opaque migration scope를 확정할 수 있도록 "
                    f"정적 문자열 collection이어야 한다: {logical.as_posix()}"
                )
            for app_name in app_names:
                registration = f"{logical.as_posix()}::{app_name}"
                if link_marker is not None:
                    marker_digest = hashlib.sha256(link_marker.encode()).hexdigest()
                    registration = f"{registration}::link-sha256:{marker_digest}"
                registrations.add(registration)
    return sorted(registrations)


def _lexical_source_roots(root: Path) -> tuple[Path, Path]:
    """읽기 여부와 무관한 Django import 후보 root."""
    return root, root / "src"


def _source_roots(root: Path) -> list[Path]:
    """저장소 안에서 실제로 읽어도 되는 Django import root."""
    roots = [root]
    source_root = root / "src"
    if (
        not _is_semantic_excluded_path(root, source_root)
        and _path_resolves_within_root(root, source_root)
        and source_root.is_dir()
    ):
        roots.append(source_root)
    return roots


def _module_migration_roots(root: Path, module: str) -> set[Path]:
    parts = module.split(".")
    if not parts or not all(part.isidentifier() for part in parts):
        return set()
    candidates = {
        source_root.joinpath(*parts)
        for source_root in _lexical_source_roots(root)
    }
    existing: set[Path] = set()
    for candidate in candidates:
        if _first_external_symlink(root, candidate) is not None:
            existing.add(candidate)
        elif candidate.exists() or candidate.is_symlink():
            existing.add(candidate)
    return existing or {root.joinpath(*parts)}


def _app_directory_for_registration(root: Path, registration: str) -> Path | None:
    parts = registration.split("::", 2)
    if len(parts) < 2:
        return None
    module_parts = parts[1].split(".")
    if not module_parts or not all(part.isidentifier() for part in module_parts):
        return None
    for source_root in _source_roots(root):
        for length in range(len(module_parts), 0, -1):
            candidate = source_root.joinpath(*module_parts[:length])
            if _is_semantic_excluded_path(root, candidate):
                continue
            if _first_external_symlink(root, candidate) is not None:
                continue
            if not candidate.is_dir():
                continue
            if (
                _app_identity_markers(candidate)
                or (candidate / "migrations").is_dir()
                or _app_config_signature(root, candidate / "apps.py") is not None
            ):
                return candidate
    return None


def _external_app_links_for_registration(
    root: Path,
    registration: str,
) -> set[Path]:
    parts = registration.split("::", 2)
    if len(parts) < 2:
        return set()
    module_parts = parts[1].split(".")
    if not module_parts or not all(part.isidentifier() for part in module_parts):
        return set()
    links: set[Path] = set()
    for source_root in _lexical_source_roots(root):
        link = _first_external_symlink(
            root,
            source_root.joinpath(*module_parts),
        )
        if link is not None:
            links.add(link)
    return links


def _installed_app_registrations(root: Path) -> list[str]:
    return [
        registration
        for registration in _declared_app_registrations(root)
        if _app_directory_for_registration(root, registration) is not None
        or _external_app_links_for_registration(root, registration)
    ]


def _stable_installed_app_registrations(root: Path) -> list[str]:
    first = _installed_app_registrations(root)
    second = _installed_app_registrations(root)
    if first != second:
        raise ManifestError(
            "static INSTALLED_APPS가 두 번의 연속 scan 사이에 변경됐다; 외부 작업을 "
            "멈춘 뒤 재시도하라"
        )
    return second


def _migration_module_config(root: Path) -> tuple[list[dict[str, str]], set[Path]]:
    entries: list[dict[str, str]] = []
    roots: set[Path] = set()
    settings_sources = _settings_sources(root)
    for source, logical, link_marker in settings_sources:
        try:
            text = _read_python_text(root, source)
        except (OSError, SyntaxError, UnicodeError) as error:
            raise ManifestError(
                f"Django settings source를 읽을 수 없다: {logical.as_posix()}"
            ) from error
        if "MIGRATION_MODULES" not in text:
            continue
        try:
            tree = ast.parse(text, filename=str(source))
        except SyntaxError as error:
            raise ManifestError(
                f"Django settings source를 해석할 수 없다: {logical.as_posix()}"
            ) from error
        records = _module_assignment_records(tree)
        if not records:
            continue
        mutated_names = _module_mutated_names(tree)
        unsafe_mutated_names = _module_mutated_names(
            tree,
            include_augmented_names=False,
        )
        if "MIGRATION_MODULES" in unsafe_mutated_names:
            raise ManifestError(
                "MIGRATION_MODULES의 method/subscript mutation은 opaque migration "
                f"scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
            )
        payload_parts: list[str] = []
        if link_marker is not None:
            payload_parts.append(link_marker)
        payload_parts.extend(
            _statement_source_lines(text, statement)
            for statement, _ in records
        )
        entries.append(
            _synthetic_entry(
                f".dddjango-migration-config/{logical.as_posix()}",
                "configuration",
                "\n".join(payload_parts),
            )
        )
        for statement, value in records:
            if statement not in tree.body:
                raise ManifestError(
                    "MIGRATION_MODULES의 조건부·중첩 대입은 opaque migration scope를 "
                    f"정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            if isinstance(value, ast.Name):
                raise ManifestError(
                    "MIGRATION_MODULES의 mutable Name alias 직접 대입은 opaque "
                    f"migration scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            assignments = _module_static_assignments_before(
                tree,
                statement.lineno,
            )
            dependencies = _static_dependency_names(value, assignments)
            assignment_counts = _module_assignment_counts_before(
                tree,
                statement.lineno,
            )
            if dependencies & mutated_names or any(
                assignment_counts.get(name, 0) > 1 for name in dependencies
            ):
                raise ManifestError(
                    "MIGRATION_MODULES가 재할당·변이된 module-level alias에 의존해 opaque "
                    f"migration scope를 정적으로 확정할 수 없다: {logical.as_posix()}"
                )
            modules = _static_migration_module_strings(value, assignments)
            if modules is None:
                raise ManifestError(
                    "MIGRATION_MODULES는 opaque migration scope를 확정할 수 있도록 "
                    f"정적 str/None dict 또는 정적 dict union이어야 한다: {logical.as_posix()}"
                )
            for module in modules:
                roots.update(_module_migration_roots(root, module))
    structural_sources = {
        root / logical for _, logical, _ in settings_sources
    }
    structural_sources.update(
        source
        for source in _settings_entrypoint_candidates(root)
        if source.exists() or source.is_symlink()
    )
    for migration_root in roots:
        for name in ("apps.py", "models.py", "models"):
            marker = migration_root / name
            if marker.exists() or marker.is_symlink():
                structural_sources.add(marker)
    for registration in _declared_app_registrations(root):
        parts = registration.split("::", 2)
        if len(parts) < 2:
            continue
        module_parts = parts[1].split(".")
        if not module_parts or not all(part.isidentifier() for part in module_parts):
            continue
        for source_root in _lexical_source_roots(root):
            for length in range(1, len(module_parts) + 1):
                candidate = source_root.joinpath(*module_parts[:length])
                if candidate.is_dir() and not candidate.is_symlink():
                    structural_sources.add(candidate)
    overlaps = sorted({
        source.relative_to(root).as_posix()
        for migration_root in roots
        for source in structural_sources
        if source == migration_root or source.is_relative_to(migration_root)
    })
    if overlaps:
        raise ManifestError(
            "Django structural discovery source와 custom migration root를 겸용할 "
            "수 없다: " + ", ".join(overlaps)
        )
    return entries, roots


def _app_identity_markers(directory: Path) -> list[str]:
    markers: list[str] = []
    if (directory / "apps.py").is_file():
        markers.append("apps.py")
    if (directory / "models.py").is_file():
        markers.append("models.py")
    if (directory / "models").is_dir():
        markers.append("models")
    return markers


class _ModuleStructureCollector(ast.NodeVisitor):
    """모듈 제어 흐름의 import/class만 모으고 지역 scope에는 들어가지 않는다."""

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


def _module_structure(
    tree: ast.Module,
) -> tuple[list[ast.Import | ast.ImportFrom], list[ast.ClassDef]]:
    collector = _ModuleStructureCollector()
    collector.visit(tree)
    return collector.imports, collector.classes


def _app_config_aliases(
    imports: list[ast.Import | ast.ImportFrom],
) -> tuple[set[str], set[str]]:
    direct_aliases: set[str] = set()
    module_aliases: set[str] = set()
    for node in imports:
        if isinstance(node, ast.ImportFrom) and node.module == "django.apps":
            for imported in node.names:
                if imported.name == "AppConfig":
                    direct_aliases.add(imported.asname or imported.name)
        elif isinstance(node, ast.ImportFrom) and node.module == "django":
            for imported in node.names:
                if imported.name == "apps":
                    module_aliases.add(imported.asname or imported.name)
        elif isinstance(node, ast.Import):
            for imported in node.names:
                if imported.name == "django.apps":
                    module_aliases.add(imported.asname or imported.name)
                elif imported.name == "django":
                    root_alias = imported.asname or imported.name
                    module_aliases.add(f"{root_alias}.apps")
    return direct_aliases, module_aliases


def _expression_path(expression: ast.expr) -> str | None:
    if isinstance(expression, ast.Name):
        return expression.id
    if isinstance(expression, ast.Attribute):
        owner = _expression_path(expression.value)
        if owner is not None:
            return f"{owner}.{expression.attr}"
    return None


def _is_app_config_base(
    base: ast.expr,
    direct_aliases: set[str],
    module_aliases: set[str],
) -> bool:
    if isinstance(base, ast.Name):
        return base.id in direct_aliases
    path = _expression_path(base)
    return path in {f"{module}.AppConfig" for module in module_aliases}


def _app_config_signature(
    root: Path,
    source: Path,
    ancestor_link: str | None = None,
    forced_classes: set[str] | None = None,
) -> str | None:
    if _is_semantic_excluded_path(root, source) or not _path_resolves_within_root(
        root, source
    ):
        return None
    if not source.exists() and not source.is_symlink():
        return None
    try:
        text = _read_python_text(root, source)
    except (OSError, SyntaxError, UnicodeError) as error:
        raise ManifestError(
            "Django AppConfig source를 읽을 수 없다: "
            f"{source.relative_to(root).as_posix()}"
        ) from error
    try:
        tree = ast.parse(text, filename=str(source))
    except SyntaxError as error:
        raise ManifestError(
            "Django AppConfig source를 해석할 수 없다: "
            f"{source.relative_to(root).as_posix()}"
        ) from error

    imports, class_nodes = _module_structure(tree)
    direct_aliases, module_aliases = _app_config_aliases(imports)
    derived: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in class_nodes:
            if node.name in derived:
                continue
            if any(
                _is_app_config_base(base, direct_aliases, module_aliases)
                or (isinstance(base, ast.Name) and base.id in derived)
                for base in node.bases
            ):
                derived.add(node.name)
                changed = True

    tracked_classes = derived | (forced_classes or set())
    records: list[tuple[str, list[tuple[str, list[str]]]]] = []
    for node in class_nodes:
        if node.name not in tracked_classes:
            continue
        field_values: dict[str, list[str]] = {}
        for statement in node.body:
            for field_name in ("name", "label"):
                value = _assignment_value(statement, field_name)
                if value is not None:
                    field_values.setdefault(field_name, []).append(
                        ast.dump(
                            value,
                            annotate_fields=True,
                            include_attributes=False,
                        )
                    )
        fields = [(name, field_values[name]) for name in sorted(field_values)]
        records.append((node.name, fields))
    records.sort(key=lambda record: record[0])
    if not records:
        return None

    payload: dict[str, object] = {"records": records}
    if ancestor_link is not None:
        payload["ancestor_link"] = ancestor_link
    if source.is_symlink():
        payload["file_link"] = _symlink_payload(root, source)
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))


def _candidate_app_directories(root: Path) -> set[Path]:
    candidates: set[Path] = set()
    for registration in _installed_app_registrations(root):
        directory = _app_directory_for_registration(root, registration)
        if directory is not None:
            candidates.add(directory)

    for current_raw, dir_names, _ in os.walk(
        root,
        topdown=True,
        onerror=_raise_walk_error,
        followlinks=False,
    ):
        current = Path(current_raw)
        if _is_semantic_excluded_path(root, current):
            dir_names[:] = []
            continue
        markers = _app_identity_markers(current)
        identified_app = current in candidates
        if markers and _app_config_signature(root, current / "apps.py") is not None:
            candidates.add(current)
            identified_app = True

        traversable: list[str] = []
        for name in sorted(dir_names):
            child = current / name
            if name in SKIP_DIRS:
                continue
            if name == "migrations" and (identified_app or markers):
                continue
            if _is_semantic_excluded_path(root, child):
                continue
            if child.is_symlink():
                if not _path_resolves_within_root(root, child):
                    continue
                markers = _app_identity_markers(child)
                if markers and _app_config_signature(root, child / "apps.py") is not None:
                    candidates.add(child)
                continue
            traversable.append(name)
        dir_names[:] = traversable
    return candidates


def _registered_app_config_sources(root: Path) -> dict[Path, set[str]]:
    sources: dict[Path, set[str]] = {}
    for registration in _installed_app_registrations(root):
        parts = registration.split("::", 2)
        if len(parts) < 2:
            continue
        module_parts = parts[1].split(".")
        if len(module_parts) < 2 or not all(
            part.isidentifier() for part in module_parts
        ):
            continue
        config_module = module_parts[:-1]
        config_class = module_parts[-1]
        for source_root in _source_roots(root):
            module_path = source_root.joinpath(*config_module)
            candidates = (module_path.with_suffix(".py"), module_path / "__init__.py")
            for candidate in candidates:
                if (
                    not _is_semantic_excluded_path(root, candidate)
                    and _path_resolves_within_root(root, candidate)
                    and candidate.is_file()
                ):
                    sources.setdefault(candidate, set()).add(config_class)
    return sources


def _app_config_entries(root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    sources = _registered_app_config_sources(root)
    for directory in sorted(_candidate_app_directories(root)):
        source = directory / "apps.py"
        if not _is_semantic_excluded_path(root, source) and source.is_file():
            sources.setdefault(source, set())
    for source in sorted(sources):
        if _is_semantic_excluded_path(root, source):
            continue
        directory = source.parent
        ancestor_link = os.readlink(directory) if directory.is_symlink() else None
        signature = _app_config_signature(
            root,
            source,
            ancestor_link=ancestor_link,
            forced_classes=sources[source],
        )
        if signature is None:
            continue
        relative = source.relative_to(root).as_posix()
        entries.append(
            _synthetic_entry(
                f".dddjango-app-config/{relative}",
                "configuration",
                signature,
            )
        )
    return entries


def _app_directory_link_entries(root: Path) -> list[dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for directory in sorted(_candidate_app_directories(root)):
        current = root
        for part in directory.relative_to(root).parts:
            current = current / part
            if not current.is_symlink():
                continue
            relative = current.relative_to(root).as_posix()
            path = f".dddjango-app-directory-link/{relative}"
            entries[path] = _synthetic_entry(
                path,
                "configuration",
                _symlink_payload(root, current),
            )
    return [entries[path] for path in sorted(entries)]


def _external_app_directory_link_entries(root: Path) -> list[dict[str, str]]:
    """등록된 repo-external app의 repo-side link만 추적한다."""
    entries: dict[str, dict[str, str]] = {}
    for registration in _declared_app_registrations(root):
        for link in _external_app_links_for_registration(root, registration):
            relative = link.relative_to(root).as_posix()
            path = f".dddjango-app-directory-link/{relative}"
            entries[path] = _synthetic_entry(
                path,
                "configuration",
                _symlink_payload(root, link),
            )
    return [entries[path] for path in sorted(entries)]


def _scan_app_identities(root: Path) -> list[str]:
    identities: set[str] = set()
    for directory in _candidate_app_directories(root):
        for marker in _app_identity_markers(directory):
            identities.add((directory / marker).relative_to(root).as_posix())
    return sorted(identities)


def _stable_scan_app_identities(root: Path) -> list[str]:
    first = _scan_app_identities(root)
    second = _scan_app_identities(root)
    if first != second:
        raise ManifestError(
            "Django app identity가 두 번의 연속 scan 사이에 변경됐다; 외부 작업을 "
            "멈춘 뒤 재시도하라"
        )
    return second


def _scan_explicit_root(root: Path, migration_root: Path) -> list[dict[str, str]]:
    ancestor_links: list[dict[str, str]] = []
    relative_root = migration_root.relative_to(root)
    current = root
    for part in relative_root.parts[:-1]:
        current = current / part
        if current.is_symlink():
            relative = current.relative_to(root).as_posix()
            ancestor_links.append(
                _synthetic_entry(
                    f".dddjango-explicit-root-link/{relative}",
                    "configuration",
                    _symlink_payload(root, current),
                )
            )
            if not _path_resolves_within_root(root, current):
                return ancestor_links
    if not migration_root.exists() and not migration_root.is_symlink():
        relative = migration_root.relative_to(root).as_posix()
        return ancestor_links + [
            {
                "path": relative,
                "kind": "missing",
                "sha256": MISSING_DIGEST,
            }
        ]
    if migration_root.is_symlink():
        return ancestor_links + [_entry(root, migration_root, "symlink")]
    if migration_root.is_file():
        return ancestor_links + [_entry(root, migration_root, "file")]

    entries = ancestor_links + [_entry(root, migration_root, "directory")]
    for current_raw, dir_names, file_names in os.walk(
        migration_root,
        topdown=True,
        onerror=_raise_walk_error,
        followlinks=False,
    ):
        current = Path(current_raw)
        traversable: list[str] = []
        for name in sorted(dir_names):
            if name in PYTHON_CACHE_DIRECTORIES:
                continue
            child = current / name
            if child.is_symlink():
                entries.append(_entry(root, child, "symlink"))
                continue
            entries.append(_entry(root, child, "directory"))
            traversable.append(name)
        dir_names[:] = traversable
        for name in sorted(file_names):
            child = current / name
            if child.is_symlink():
                entries.append(_entry(root, child, "symlink"))
            elif stat.S_ISREG(child.lstat().st_mode):
                entries.append(_entry(root, child, "file"))
    return entries


def _scan_migration_tree(root: Path) -> list[dict[str, str]]:
    entries = _scan_named_migration_tree(root)
    config_entries, configured_roots = _migration_module_config(root)
    entries.extend(config_entries)
    entries.extend(_external_settings_link_entries(root))
    entries.extend(_app_config_entries(root))
    entries.extend(_app_directory_link_entries(root))
    entries.extend(_external_app_directory_link_entries(root))
    for migration_root in sorted(configured_roots):
        entries.extend(_scan_explicit_root(root, migration_root))

    unique: dict[str, dict[str, str]] = {}
    for entry in entries:
        previous = unique.get(entry["path"])
        if previous is not None and previous != entry:
            raise ManifestError(f"migration boundary entry 충돌: {entry['path']}")
        unique[entry["path"]] = entry
    return [unique[path] for path in sorted(unique)]


def _stable_scan_migration_tree(root: Path) -> list[dict[str, str]]:
    first = _scan_migration_tree(root)
    second = _scan_migration_tree(root)
    if first != second:
        raise ManifestError(
            "migration opaque boundary가 두 번의 연속 scan 사이에 변경됐다; 외부 작업을 멈춘 뒤 재시도하라"
        )
    return second


def _external_owned_opaque_entries(
    root: Path,
    external_owned_opaque_paths: list[str],
) -> list[dict[str, str]]:
    """외부 소유 exact file을 해석하지 않고 경로·종류·byte digest만 동결한다."""
    entries: list[dict[str, str]] = []
    for relative in external_owned_opaque_paths:
        source = root / relative
        synthetic_path = f".dddjango-external-owned-opaque/{relative}"
        try:
            mode = source.lstat().st_mode
        except OSError:
            payload = "missing"
        else:
            if stat.S_ISLNK(mode):
                try:
                    target = os.fsdecode(os.readlink(source))
                except OSError as error:
                    target = f"unavailable:{type(error).__name__}"
                payload = f"symlink:{target}"
            elif stat.S_ISREG(mode):
                _reject_hardlinked_regular(source, source.lstat())
                payload = f"regular:{_sha256_file(source)}"
            elif stat.S_ISDIR(mode):
                payload = "directory"
            else:
                payload = f"special:{mode}"
        entries.append(
            _synthetic_entry(
                synthetic_path,
                "configuration",
                payload,
            )
        )
    return entries


def _stable_external_owned_opaque_entries(
    root: Path,
    external_owned_opaque_paths: list[str],
) -> list[dict[str, str]]:
    first = _external_owned_opaque_entries(root, external_owned_opaque_paths)
    second = _external_owned_opaque_entries(root, external_owned_opaque_paths)
    if first != second:
        raise ManifestError(
            "external-owned opaque file이 두 번의 연속 hash 사이에 변경됐다; "
            "외부 작업을 멈춘 뒤 재시도하라"
        )
    return second


def _stable_boundary_entries(
    root: Path,
    external_owned_opaque_paths: list[str],
) -> list[dict[str, str]]:
    entries = [
        *_stable_scan_migration_tree(root),
        *_stable_external_owned_opaque_entries(
            root,
            external_owned_opaque_paths,
        ),
    ]
    return sorted(entries, key=lambda item: item["path"])


def _migration_roots(root: Path) -> list[str]:
    """Layer checker가 migration-only change를 제외할 정확한 논리 root 목록."""
    _, configured_roots = _migration_module_config(root)
    _add_semantic_exclusions(
        root,
        (path.relative_to(root).as_posix() for path in configured_roots),
    )
    roots = {
        directory / "migrations" for directory in _candidate_app_directories(root)
    }
    roots.update(configured_roots)
    return sorted(path.relative_to(root).as_posix() for path in roots)


def _stable_migration_roots(root: Path) -> list[str]:
    first = _migration_roots(root)
    second = _migration_roots(root)
    if first != second:
        raise ManifestError(
            "migration root가 두 번의 연속 scan 사이에 변경됐다; 외부 작업을 "
            "멈춘 뒤 재시도하라"
        )
    return second


def _migration_alias_targets(root: Path, migration_roots: list[str]) -> list[str]:
    """Opaque hash가 따라가는 repo-internal symlink target의 canonical 경로/prefix."""
    targets: set[str] = set()
    visited_directories: set[tuple[int, int]] = set()

    def record_target(resolved: Path) -> None:
        try:
            relative_name = resolved.relative_to(root).as_posix()
        except ValueError:
            return
        relative = PurePosixPath(relative_name)
        if not relative.parts or relative_name == ".":
            raise ManifestError(
                "migration symlink가 저장소 root를 가리켜 opaque 범위를 전체 "
                "프로젝트로 확장한다"
            )
        if any(
            PurePosixPath(migration_root).is_relative_to(relative)
            for migration_root in migration_roots
        ):
            raise ManifestError(
                "migration symlink target이 migration root의 상위 경로라 opaque "
                f"범위를 과도하게 확장한다: {relative_name}"
            )
        targets.add(relative_name)

    def visit(path: Path) -> None:
        is_link = path.is_symlink()
        if is_link:
            try:
                resolved = path.resolve(strict=False)
                resolved.relative_to(root)
            except (OSError, RuntimeError, ValueError):
                return
            record_target(resolved)
            try:
                followed = resolved.stat()
                directory = resolved
            except (OSError, RuntimeError):
                return
        else:
            try:
                followed = path.stat()
                directory = path
            except (OSError, RuntimeError, ValueError):
                return
        if not stat.S_ISDIR(followed.st_mode):
            return
        inode = (followed.st_dev, followed.st_ino)
        if inode in visited_directories:
            return
        visited_directories.add(inode)
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError:
            return
        for child in children:
            if child.name in PYTHON_CACHE_DIRECTORIES:
                continue
            if child.is_symlink():
                visit(child)
                continue
            try:
                if child.is_dir():
                    visit(child)
            except (OSError, RuntimeError):
                continue

    for relative_name in migration_roots:
        migration_root = root / relative_name
        try:
            resolved = migration_root.resolve(strict=True)
            resolved_relative = resolved.relative_to(root).as_posix()
        except (OSError, RuntimeError, ValueError):
            resolved_relative = relative_name
        if resolved_relative != relative_name:
            record_target(resolved)
        visit(migration_root)
    return sorted(targets)


def _stable_migration_alias_targets(
    root: Path,
    migration_roots: list[str],
) -> list[str]:
    first = _migration_alias_targets(root, migration_roots)
    second = _migration_alias_targets(root, migration_roots)
    if first != second:
        raise ManifestError(
            "migration symlink target가 두 번의 연속 scan 사이에 변경됐다; "
            "외부 작업을 멈춘 뒤 재시도하라"
        )
    return second


def _application_containers(root: Path) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for path in (root / "application", root / "src" / "application")
        if not _is_semantic_excluded_path(root, path)
        and _path_resolves_within_root(root, path)
        and path.is_dir()
    ]


def _stable_application_containers(root: Path) -> list[str]:
    first = _application_containers(root)
    second = _application_containers(root)
    if first != second:
        raise ManifestError(
            "application container가 두 번의 연속 scan 사이에 변경됐다; 외부 작업을 "
            "멈춘 뒤 재시도하라"
        )
    return second


def _application_layer_issues(
    root: Path,
    migration_roots: list[str],
    migration_alias_targets: list[str],
    external_owned_opaque_paths: list[str],
) -> dict[str, list[str]]:
    """Sibling layer checker의 issue vocabulary로 G0 brownfield 구조를 기록한다."""
    checker_path = Path(__file__).with_name("check-layer-skeleton.py")
    spec = importlib.util.spec_from_file_location(
        "dddjango_layer_skeleton_baseline",
        checker_path,
    )
    if spec is None or spec.loader is None:
        raise ManifestError(f"layer checker를 로드할 수 없다: {checker_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        find_bc_dirs = getattr(module, "_find_bc_dirs")
        is_bc_to_check = getattr(module, "_is_bc_to_check")
        layer_issues = getattr(module, "_layer_issues")
        configure_migration_scope = getattr(module, "configure_migration_scope")
    except (AttributeError, ImportError, OSError, SyntaxError) as error:
        raise ManifestError(f"layer checker를 로드할 수 없다: {checker_path}") from error
    configure_migration_scope(
        root,
        sorted(set([*migration_roots, *migration_alias_targets])),
        external_owned_opaque_paths,
    )
    issues: dict[str, list[str]] = {}
    for bc in find_bc_dirs(root):
        relative = bc.relative_to(root).as_posix()
        issues[relative] = (
            layer_issues(root, bc) if is_bc_to_check(root, bc) else []
        )
    return dict(sorted(issues.items()))


def _stable_application_layer_issues(
    root: Path,
    migration_roots: list[str],
    migration_alias_targets: list[str],
    external_owned_opaque_paths: list[str],
) -> dict[str, list[str]]:
    first = _application_layer_issues(
        root,
        migration_roots,
        migration_alias_targets,
        external_owned_opaque_paths,
    )
    second = _application_layer_issues(
        root,
        migration_roots,
        migration_alias_targets,
        external_owned_opaque_paths,
    )
    if first != second:
        raise ManifestError(
            "application layer issue baseline이 두 번의 연속 scan 사이에 변경됐다; "
            "외부 작업을 멈춘 뒤 재시도하라"
        )
    return second


def _manifest(
    root: Path,
    external_owned_opaque_paths: list[str],
    boundary_paths: Iterable[Path] = (),
) -> dict[str, object]:
    _add_semantic_exclusions(root, external_owned_opaque_paths)
    migration_roots = _stable_migration_roots(root)
    migration_alias_targets = _stable_migration_alias_targets(root, migration_roots)
    _add_semantic_exclusions(
        root,
        [*migration_roots, *migration_alias_targets],
    )
    owned_paths = [
        *migration_roots,
        *migration_alias_targets,
        *external_owned_opaque_paths,
    ]
    for boundary_path in boundary_paths:
        if _state_path_is_in_exact_migration_root(
            root,
            boundary_path,
            owned_paths,
        ):
            raise ManifestError(
                "STATE_FILE/receipt는 G0 opaque-owned path 밖에 둬야 한다"
            )
    return {
        "application_containers": _stable_application_containers(root),
        "application_layer_issues": _stable_application_layer_issues(
            root,
            migration_roots,
            migration_alias_targets,
            external_owned_opaque_paths,
        ),
        "app_identities": _stable_scan_app_identities(root),
        "app_registrations": _stable_installed_app_registrations(root),
        "entries": _stable_boundary_entries(root, external_owned_opaque_paths),
        "external_owned_opaque_paths": external_owned_opaque_paths,
        "format": MANIFEST_FORMAT,
        "migration_alias_targets": migration_alias_targets,
        "migration_roots": migration_roots,
        "root": str(root),
    }


def _receipt_file(state_file: Path) -> Path:
    return state_file.with_name(f"{state_file.name}{EPOCH_RECEIPT_SUFFIX}")


def _serialized_receipt(state_file: Path, manifest_sha256: str) -> str:
    return json.dumps(
        {
            "format": RECEIPT_FORMAT,
            "manifest_sha256": manifest_sha256,
            "state_path": str(state_file),
        },
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _write_receipt(state_file: Path, manifest_sha256: str) -> None:
    receipt = _receipt_file(state_file)
    serialized = _serialized_receipt(state_file, manifest_sha256)
    with receipt.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def _write_manifest(state_file: Path, manifest: dict[str, object]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    _write_receipt(
        state_file,
        hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    )
    with state_file.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def _validate_receipt(
    state_file: Path,
    manifest_sha256: str,
) -> None:
    receipt = _receipt_file(state_file)
    if not receipt.is_file() or receipt.is_symlink():
        raise ManifestError(f"write-once receipt가 없다: {receipt}")
    try:
        serialized = receipt.read_text(encoding="utf-8")
        value = json.loads(serialized)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ManifestError(f"write-once receipt를 읽을 수 없다: {receipt}") from error
    expected = {
        "format": RECEIPT_FORMAT,
        "manifest_sha256": manifest_sha256,
        "state_path": str(state_file),
    }
    if value != expected or serialized != _serialized_receipt(
        state_file, manifest_sha256
    ):
        raise ManifestError(f"write-once receipt가 baseline과 일치하지 않는다: {receipt}")


def _validate_entry(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "kind", "sha256"}:
        raise ManifestError("baseline entry 형식이 올바르지 않다")
    path = value.get("path")
    kind = value.get("kind")
    digest = value.get("sha256")
    if not isinstance(path, str) or not path:
        raise ManifestError("baseline entry path가 올바르지 않다")
    pure_path = PurePosixPath(path)
    if (
        pure_path.is_absolute()
        or pure_path.as_posix() != path
        or any(part in {"", ".", ".."} for part in pure_path.parts)
    ):
        raise ManifestError(f"baseline entry path가 상대 정규 경로가 아니다: {path!r}")
    if not isinstance(kind, str) or kind not in ENTRY_KINDS:
        raise ManifestError(f"baseline entry kind가 올바르지 않다: {path!r}")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ManifestError(f"baseline SHA-256이 올바르지 않다: {path!r}")
    if any(character not in "0123456789abcdef" for character in digest):
        raise ManifestError(f"baseline SHA-256이 올바르지 않다: {path!r}")
    return {"path": path, "kind": kind, "sha256": digest}


def _load_manifest(
    state_file: Path,
) -> tuple[
    str,
    list[dict[str, str]],
    list[str],
    list[str],
    list[str],
    list[str],
    list[str],
    list[str],
    dict[str, list[str]],
]:
    if state_file.is_symlink():
        raise ManifestError(f"baseline symlink는 허용하지 않는다: {state_file}")
    if not state_file.is_file() or not stat.S_ISREG(state_file.lstat().st_mode):
        raise ManifestError(f"baseline 파일이 없다: {state_file}")
    try:
        serialized = state_file.read_bytes()
        value = json.loads(serialized.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ManifestError(f"baseline JSON을 읽을 수 없다: {state_file}") from error
    if not isinstance(value, dict) or set(value) != {
        "application_containers",
        "application_layer_issues",
        "app_identities",
        "app_registrations",
        "entries",
        "external_owned_opaque_paths",
        "format",
        "migration_alias_targets",
        "migration_roots",
        "root",
    }:
        raise ManifestError("baseline 최상위 형식이 올바르지 않다")
    if value.get("format") != MANIFEST_FORMAT:
        raise ManifestError("baseline format이 지원되지 않는다")
    _validate_receipt(state_file, hashlib.sha256(serialized).hexdigest())
    manifest_root = value.get("root")
    if not isinstance(manifest_root, str) or not Path(manifest_root).is_absolute():
        raise ManifestError("baseline root가 절대 경로가 아니다")
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list):
        raise ManifestError("baseline entries가 리스트가 아니다")
    entries = [_validate_entry(item) for item in raw_entries]
    paths = [item["path"] for item in entries]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ManifestError("baseline entries가 경로순으로 정렬된 고유 목록이 아니다")
    raw_identities = value.get("app_identities")
    if not isinstance(raw_identities, list) or not all(
        isinstance(item, str) and item for item in raw_identities
    ):
        raise ManifestError("baseline app_identities 형식이 올바르지 않다")
    identities = list(raw_identities)
    if identities != sorted(identities) or len(identities) != len(set(identities)):
        raise ManifestError("baseline app_identities가 경로순으로 정렬된 고유 목록이 아니다")
    for identity in identities:
        pure_path = PurePosixPath(identity)
        if (
            pure_path.is_absolute()
            or pure_path.as_posix() != identity
            or any(part in {"", ".", ".."} for part in pure_path.parts)
        ):
            raise ManifestError(f"baseline app identity가 상대 정규 경로가 아니다: {identity!r}")
    raw_registrations = value.get("app_registrations")
    if not isinstance(raw_registrations, list) or not all(
        isinstance(item, str) and item for item in raw_registrations
    ):
        raise ManifestError("baseline app_registrations 형식이 올바르지 않다")
    registrations = list(raw_registrations)
    if registrations != sorted(registrations) or len(registrations) != len(
        set(registrations)
    ):
        raise ManifestError(
            "baseline app_registrations가 정렬된 고유 목록이 아니다"
        )
    raw_migration_roots = value.get("migration_roots")
    if not isinstance(raw_migration_roots, list) or not all(
        isinstance(item, str) and item for item in raw_migration_roots
    ):
        raise ManifestError("baseline migration_roots 형식이 올바르지 않다")
    migration_roots = list(raw_migration_roots)
    if migration_roots != sorted(migration_roots) or len(migration_roots) != len(
        set(migration_roots)
    ):
        raise ManifestError("baseline migration_roots가 정렬된 고유 목록이 아니다")
    for migration_root in migration_roots:
        pure_path = PurePosixPath(migration_root)
        if (
            pure_path.is_absolute()
            or pure_path.as_posix() != migration_root
            or any(part in {"", ".", ".."} for part in pure_path.parts)
        ):
            raise ManifestError(
                "baseline migration root가 상대 정규 경로가 아니다: "
                f"{migration_root!r}"
            )
    migration_alias_targets = _normalize_relative_paths(
        value.get("migration_alias_targets"),
        "baseline migration_alias_targets",
    )
    external_owned_opaque_paths = _normalize_relative_paths(
        value.get("external_owned_opaque_paths"),
        "baseline external_owned_opaque_paths",
    )
    raw_containers = value.get("application_containers")
    if not isinstance(raw_containers, list) or not all(
        isinstance(item, str) for item in raw_containers
    ):
        raise ManifestError("baseline application_containers 형식이 올바르지 않다")
    containers = list(raw_containers)
    allowed_containers = {"application", "src/application"}
    if (
        containers != sorted(containers)
        or len(containers) != len(set(containers))
        or any(item not in allowed_containers for item in containers)
    ):
        raise ManifestError(
            "baseline application_containers가 정렬된 표준 컨테이너 목록이 아니다"
        )
    raw_layer_issues = value.get("application_layer_issues")
    if not isinstance(raw_layer_issues, dict) or not all(
        isinstance(path, str)
        and isinstance(issues, list)
        and all(isinstance(issue, str) and issue for issue in issues)
        for path, issues in raw_layer_issues.items()
    ):
        raise ManifestError("baseline application_layer_issues 형식이 올바르지 않다")
    application_layer_issues: dict[str, list[str]] = {}
    for path, raw_issues in raw_layer_issues.items():
        pure_path = PurePosixPath(path)
        valid_parent = (
            len(pure_path.parts) == 2 and pure_path.parts[0] == "application"
        ) or (
            len(pure_path.parts) == 3
            and pure_path.parts[:2] == ("src", "application")
        )
        issues = list(raw_issues)
        if not valid_parent or pure_path.as_posix() != path or len(issues) != len(
            set(issues)
        ):
            raise ManifestError(
                "baseline application_layer_issues가 정규화된 BC issue 목록이 아니다: "
                f"{path!r}"
            )
        application_layer_issues[path] = issues
    if list(raw_layer_issues) != sorted(raw_layer_issues):
        raise ManifestError("baseline application_layer_issues key가 정렬되지 않았다")
    return (
        manifest_root,
        entries,
        identities,
        registrations,
        migration_roots,
        migration_alias_targets,
        external_owned_opaque_paths,
        containers,
        application_layer_issues,
    )


def _entry_map(entries: list[dict[str, str]]) -> dict[str, tuple[str, str]]:
    return {item["path"]: (item["kind"], item["sha256"]) for item in entries}


def _changes(
    baseline: list[dict[str, str]],
    current: list[dict[str, str]],
    baseline_identities: list[str],
    current_identities: list[str],
) -> list[tuple[str, str]]:
    before = _entry_map(baseline)
    after = _entry_map(current)
    findings: list[tuple[str, str]] = []
    baseline_app_directories = {
        PurePosixPath(identity).parent.as_posix() for identity in baseline_identities
    }
    current_app_directories = {
        PurePosixPath(identity).parent.as_posix() for identity in current_identities
    }
    new_app_directories = current_app_directories - baseline_app_directories
    for path in sorted(before.keys() | after.keys()):
        if path not in before:
            prefix = ".dddjango-app-config/"
            if path.startswith(prefix) and after[path][0] == "configuration":
                config_path = PurePosixPath(path.removeprefix(prefix))
                config_directory = config_path.parent.as_posix()
                if config_directory in new_app_directories:
                    # 새 app은 기존 app 아래 중첩됐더라도 그 자체의 AppConfig를 가질 수 있다.
                    continue
            link_prefix = ".dddjango-app-directory-link/"
            if path.startswith(link_prefix) and after[path][0] == "configuration":
                link_path = PurePosixPath(path.removeprefix(link_prefix))
                contains_existing_app = any(
                    PurePosixPath(directory).is_relative_to(link_path)
                    for directory in baseline_app_directories
                )
                contains_new_app = any(
                    PurePosixPath(directory).is_relative_to(link_path)
                    for directory in new_app_directories
                )
                if contains_new_app and not contains_existing_app:
                    continue
                if not contains_existing_app:
                    continue
            findings.append((path, "ADDED"))
        elif path not in after:
            findings.append((path, "DELETED"))
        elif before[path] != after[path]:
            findings.append((path, "MODIFIED"))
    return findings


def _state_path_has_symlink_ancestor(root: Path, state_file: Path) -> bool:
    try:
        relative = state_file.relative_to(root)
    except ValueError:
        return False
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            return True
    return False


def _state_path_is_in_exact_migration_root(
    root: Path,
    boundary_path: Path,
    owned_paths: list[str],
    include_owned_descendants: bool = False,
) -> bool:
    """State/receipt가 G0 opaque-owned path 안에 기록되는 자기위반을 막는다."""
    try:
        resolved_path = boundary_path.resolve(strict=False)
        relative = PurePosixPath(resolved_path.relative_to(root).as_posix())
    except (OSError, RuntimeError, ValueError):
        return False
    for item in owned_paths:
        owned = PurePosixPath(item)
        if relative == owned or relative.is_relative_to(owned):
            return True
        if include_owned_descendants and owned.is_relative_to(relative):
            return True
    return False


def _snapshot(
    root: Path,
    state_file: Path,
    external_owned_opaque_paths: list[str],
) -> int:
    receipt = _receipt_file(state_file)
    if (
        state_file.exists()
        or state_file.is_symlink()
        or receipt.exists()
        or receipt.is_symlink()
    ):
        raise ManifestError(
            "STATE_FILE 또는 write-once receipt가 이미 있어 snapshot 재기준화를 "
            f"거부한다: {state_file}"
        )
    manifest = _manifest(
        root,
        external_owned_opaque_paths,
        boundary_paths=(state_file, receipt),
    )
    owned_paths = [
        *manifest["migration_roots"],
        *manifest["migration_alias_targets"],
        *manifest["external_owned_opaque_paths"],
    ]
    for boundary_path in (state_file, receipt):
        if _state_path_is_in_exact_migration_root(
            root,
            boundary_path,
            owned_paths,
        ):
            raise ManifestError(
                "STATE_FILE/receipt는 G0 opaque-owned path 밖에 둬야 한다"
            )
    _write_manifest(state_file, manifest)
    entries = manifest["entries"]
    count = len(entries) if isinstance(entries, list) else 0
    print(f"[check-migration-boundary] snapshot: {count} entries -> {state_file}")
    return 0


def _preflight(
    root: Path,
    boundary_path: Path,
    external_owned_opaque_paths: list[str],
) -> int:
    """Artifact write 전에 current opaque scope와 경로 안전성만 읽기 전용 확인한다."""
    _add_semantic_exclusions(root, external_owned_opaque_paths)
    migration_roots = _stable_migration_roots(root)
    migration_alias_targets = _stable_migration_alias_targets(root, migration_roots)
    owned_paths = [
        *migration_roots,
        *migration_alias_targets,
        *external_owned_opaque_paths,
    ]
    _add_semantic_exclusions(root, owned_paths)
    if _state_path_is_in_exact_migration_root(
        root,
        boundary_path,
        owned_paths,
        include_owned_descendants=True,
    ):
        raise ManifestError(
            "STATE_PATH는 current opaque-owned path 밖에 둬야 한다"
        )
    scope = {
        "external_owned_opaque_paths": external_owned_opaque_paths,
        "migration_alias_targets": migration_alias_targets,
        "migration_roots": migration_roots,
    }
    print(
        "[check-migration-boundary] preflight clean — scope="
        + json.dumps(scope, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    )
    return 0


def _verify(root: Path, state_file: Path) -> int:
    loaded = _load_manifest(state_file)
    manifest_root = loaded[0]
    if manifest_root != str(root):
        raise ManifestError(
            f"baseline root 불일치: recorded={manifest_root!r}, target={str(root)!r}"
        )
    owned_paths = [*loaded[4], *loaded[5], *loaded[6]]
    _add_semantic_exclusions(root, owned_paths)
    for boundary_path in (
        state_file,
        _receipt_file(state_file),
    ):
        if _state_path_is_in_exact_migration_root(
            root,
            boundary_path,
            owned_paths,
        ):
            raise ManifestError(
                "STATE_FILE/receipt는 G0 opaque-owned path 밖에 둬야 한다"
            )
    findings = _findings_for_state(
        root,
        state_file,
        _stable_boundary_entries(root, loaded[6]),
        _stable_scan_app_identities(root),
        _stable_installed_app_registrations(root),
    )
    if not findings:
        print("[check-migration-boundary] clean — opaque boundary matches snapshot")
        return 0

    print("[check-migration-boundary] BLOCKER — snapshot 이후 migration opaque boundary가 변경됐다:")
    for path, status_name in findings:
        print(f"  - {status_name}: {path}")
    print(
        "  변경 주체를 단정할 수 없다. 동시 작업이나 외부 release pipeline 변경일 수 있으므로 "
        "중단한 뒤 변경 귀속과 다음 진행을 확인하라."
    )
    return 2


def _cleanup(root: Path, state_file: Path, run_id: str) -> int:
    """Expected run-id에 결박된 exact write-once pair만 검증하고 삭제한다."""
    if SAFE_RUN_ID.fullmatch(run_id) is None:
        raise ManifestError(
            "RUN_ID에는 8~128자의 portable 문자([A-Za-z0-9_-])만 허용한다"
        )
    expected_suffix = f"-{run_id}.json"
    if (
        EPOCH_STATE_FILE.fullmatch(state_file.name) is None
        or not state_file.name.endswith(expected_suffix)
    ):
        raise ManifestError(
            "STATE_FILE 이름이 expected RUN_ID와 결박되지 않았다: "
            f"state={state_file.name!r}, run_id={run_id!r}"
        )
    try:
        state_relative = state_file.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise ManifestError("cleanup STATE_FILE은 TARGET_DIR 내부여야 한다") from error
    if (
        len(state_relative.parts) != 5
        or state_relative.parts[0] != ".dddjango"
        or state_relative.parts[2] != ".runs"
        or state_relative.parts[3] != run_id
    ):
        raise ManifestError(
            "cleanup STATE_FILE은 exact .dddjango/<feature>/.runs/<RUN_ID>/의 "
            "직접 자식이어야 한다"
        )
    receipt = _receipt_file(state_file)
    if state_file.is_symlink() or receipt.is_symlink():
        raise ManifestError("cleanup 대상 baseline/receipt symlink는 허용하지 않는다")
    manifest_root = _load_manifest(state_file)[0]
    if manifest_root != str(root):
        raise ManifestError(
            f"baseline root 불일치: recorded={manifest_root!r}, target={str(root)!r}"
        )

    receipt_bytes = receipt.read_bytes()
    receipt.unlink()
    try:
        state_file.unlink()
    except OSError as unlink_error:
        try:
            with receipt.open("xb") as stream:
                stream.write(receipt_bytes)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as rollback_error:
            raise ManifestError(
                "cleanup 중 baseline 삭제가 실패했고 receipt rollback도 실패했다: "
                f"unlink={unlink_error}, rollback={rollback_error}"
            ) from rollback_error
        raise ManifestError(
            f"cleanup 중 baseline 삭제가 실패해 receipt를 복원했다: {unlink_error}"
        ) from unlink_error
    for path in (state_file, receipt):
        if path.exists() or path.is_symlink():
            raise ManifestError(f"cleanup 뒤 exact pair가 남아 있다: {path}")
    print(f"[check-migration-boundary] cleanup: exact run pair removed -> {state_file}")
    return 0


def _findings_for_state(
    root: Path,
    state_file: Path,
    current_entries: list[dict[str, str]],
    current_identities: list[str],
    current_registrations: list[str],
) -> list[tuple[str, str]]:
    (
        manifest_root,
        baseline,
        baseline_identities,
        baseline_registrations,
        _,
        _,
        _,
        _,
        _,
    ) = (
        _load_manifest(state_file)
    )
    if manifest_root != str(root):
        raise ManifestError(
            f"baseline root 불일치: recorded={manifest_root!r}, target={str(root)!r}"
        )
    findings = _changes(
        baseline,
        current_entries,
        baseline_identities,
        current_identities,
    )
    current_identity_set = set(current_identities)
    findings.extend(
        (path, "APP_IDENTITY_DELETED")
        for path in baseline_identities
        if path not in current_identity_set
    )
    current_registration_set = set(current_registrations)
    findings.extend(
        (registration, "APP_REGISTRATION_DELETED")
        for registration in baseline_registrations
        if registration not in current_registration_set
    )
    findings.sort()
    return findings


def _epoch_state_files(state_directory: Path) -> list[Path]:
    state_files: list[Path] = []
    receipt_states: set[Path] = set()
    for current_raw, dir_names, file_names in os.walk(
        state_directory,
        topdown=True,
        onerror=_raise_walk_error,
        followlinks=False,
    ):
        current = Path(current_raw)
        traversable: list[str] = []
        for name in sorted(dir_names):
            child = current / name
            if child.is_symlink():
                if EPOCH_STATE_FILE.fullmatch(name) or name.endswith(
                    EPOCH_RECEIPT_SUFFIX
                ):
                    raise ManifestError(
                        "recovery epoch 파일 이름을 symlink directory가 점유한다: "
                        f"{child}"
                    )
                continue
            traversable.append(name)
        dir_names[:] = traversable
        for name in sorted(file_names):
            candidate = current / name
            recorded_name: str | None = None
            if not candidate.is_symlink():
                try:
                    if candidate.stat().st_size <= 8192:
                        value = json.loads(candidate.read_text(encoding="utf-8"))
                        if isinstance(value, dict) and value.get("format") == RECEIPT_FORMAT:
                            receipt_state = value.get("state_path")
                            if isinstance(receipt_state, str):
                                recorded_path = Path(receipt_state)
                                if (
                                    recorded_path.is_absolute()
                                    and EPOCH_STATE_FILE.fullmatch(recorded_path.name)
                                ):
                                    expected_receipt = recorded_path.with_name(
                                        f"{recorded_path.name}{EPOCH_RECEIPT_SUFFIX}"
                                    )
                                    if candidate != expected_receipt:
                                        if candidate.parent == expected_receipt.parent:
                                            raise ManifestError(
                                                "epoch write-once receipt 이름이 변경됐다: "
                                                f"recorded={expected_receipt.name!r}, "
                                                f"actual={candidate.name!r}"
                                            )
                                        raise ManifestError(
                                            "epoch write-once pair 위치가 변경됐다: "
                                            f"recorded={expected_receipt}, actual={candidate}"
                                        )
                                    recorded_name = recorded_path.name
                except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                    pass
            if recorded_name is not None:
                expected_name = f"{recorded_name}{EPOCH_RECEIPT_SUFFIX}"
                if name != expected_name:
                    raise ManifestError(
                        "epoch write-once receipt 이름이 변경됐다: "
                        f"recorded={recorded_name!r}, actual={name!r}"
                    )
                receipt_states.add(Path(receipt_state))
                continue
            if name.endswith(EPOCH_RECEIPT_SUFFIX):
                receipt = current / name
                if receipt.is_symlink() or not receipt.is_file():
                    raise ManifestError(
                        f"epoch write-once receipt가 실제 파일이 아니다: {receipt}"
                    )
                state_name = name.removesuffix(EPOCH_RECEIPT_SUFFIX)
                if EPOCH_STATE_FILE.fullmatch(state_name):
                    receipt_states.add(current / state_name)
                    continue
                continue
            if not EPOCH_STATE_FILE.fullmatch(name):
                continue
            state_file = current / name
            if state_file.is_symlink():
                raise ManifestError(f"epoch baseline symlink는 허용하지 않는다: {state_file}")
            if state_file.is_file():
                state_files.append(state_file)
    for state_file in sorted(receipt_states):
        if state_file.is_symlink() or not state_file.is_file():
            raise ManifestError(
                "epoch write-once receipt의 baseline 파일이 없다: "
                f"{state_file}"
            )
    return sorted(state_files)


def _recover(
    root: Path,
    state_directory: Path,
    external_owned_opaque_paths: list[str],
) -> int:
    if not state_directory.is_dir() or state_directory.is_symlink():
        raise ManifestError(f"recovery STATE_DIR이 실제 디렉터리가 아니다: {state_directory}")
    _add_semantic_exclusions(root, external_owned_opaque_paths)
    current_migration_roots = _stable_migration_roots(root)
    current_alias_targets = _stable_migration_alias_targets(
        root,
        current_migration_roots,
    )
    preliminary_owned_paths = [
        *current_migration_roots,
        *current_alias_targets,
        *external_owned_opaque_paths,
    ]
    _add_semantic_exclusions(root, preliminary_owned_paths)
    if _state_path_is_in_exact_migration_root(
        root,
        state_directory,
        preliminary_owned_paths,
        include_owned_descendants=True,
    ):
        raise ManifestError(
            "recovery STATE_DIR은 current opaque-owned path 밖에 둬야 한다"
        )
    state_files = _epoch_state_files(state_directory)
    if not state_files:
        print("[check-migration-boundary] recovery clean — orphan epoch 없음")
        return 0

    loaded_states = [(state_file, _load_manifest(state_file)) for state_file in state_files]
    for _, loaded in loaded_states:
        if loaded[0] != str(root):
            raise ManifestError(
                "orphan baseline root가 TARGET_DIR과 다르다: "
                f"recorded={loaded[0]!r}, target={str(root)!r}"
            )
    owned_paths = sorted(
        {
            path
            for _, loaded in loaded_states
            for path in (*loaded[4], *loaded[5], *loaded[6])
        }
    )
    _add_semantic_exclusions(root, owned_paths)
    if _state_path_is_in_exact_migration_root(
        root,
        state_directory,
        owned_paths,
        include_owned_descendants=True,
    ):
        raise ManifestError(
            "recovery STATE_DIR은 G0 opaque-owned path 밖에 둬야 한다"
        )

    current_migration_entries = _stable_scan_migration_tree(root)
    current_identities = _stable_scan_app_identities(root)
    current_registrations = _stable_installed_app_registrations(root)
    changed: list[tuple[Path, list[tuple[str, str]]]] = []
    for state_file, loaded in loaded_states:
        current_entries = sorted(
            [
                *current_migration_entries,
                *_stable_external_owned_opaque_entries(root, loaded[6]),
            ],
            key=lambda item: item["path"],
        )
        findings = _findings_for_state(
            root,
            state_file,
            current_entries,
            current_identities,
            current_registrations,
        )
        if findings:
            changed.append((state_file, findings))

    if not changed:
        print(
            "[check-migration-boundary] recovery clean — "
            f"{len(state_files)} orphan epoch baseline 일치"
        )
        return 0

    print(
        "[check-migration-boundary] BLOCKER — 중단된 이전 실행의 orphan epoch와 "
        "현재 migration opaque boundary가 다르다:"
    )
    for state_file, findings in changed:
        print(f"  epoch: {state_file}")
        for path, status_name in findings:
            print(f"    - {status_name}: {path}")
    print(
        "  변경 주체를 단정할 수 없다. 새 snapshot을 만들지 말고 변경 귀속과 외부 "
        "migration 생명주기 정지를 확인하라."
    )
    return 2


def _usage() -> None:
    print(
        "사용법: check-migration-boundary.py "
        "preflight TARGET_DIR STATE_PATH | {snapshot|verify} TARGET_DIR STATE_FILE | "
        "cleanup TARGET_DIR STATE_FILE RUN_ID | recover TARGET_DIR STATE_DIR",
        file=sys.stderr,
    )


def main(argv: list[str]) -> int:
    if (
        len(argv) not in {4, 5}
        or argv[1] not in {
        "preflight",
        "snapshot",
        "verify",
        "cleanup",
        "recover",
        }
        or (argv[1] == "cleanup") != (len(argv) == 5)
    ):
        _usage()
        return 1

    action = argv[1]
    try:
        lexical_root = Path(argv[2]).expanduser().absolute()
        root = lexical_root.resolve()
        boundary_path = Path(argv[3]).expanduser().absolute()
    except (OSError, RuntimeError) as error:
        print(f"[check-migration-boundary] 사용 오류: {error}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(
            f"[check-migration-boundary] 사용 오류: 디렉터리 아님 {root}",
            file=sys.stderr,
        )
        return 1
    if _state_path_has_symlink_ancestor(
        lexical_root, boundary_path
    ):
        print(
            "[check-migration-boundary] 사용 오류: STATE_FILE/STATE_DIR의 TARGET_DIR 내부 조상에 "
            "symlink를 허용하지 않는다",
            file=sys.stderr,
        )
        return 1

    try:
        if action == "preflight":
            external_owned_opaque_paths = _external_owned_paths_from_environment(root)
            return _preflight(
                root,
                boundary_path,
                external_owned_opaque_paths,
            )
        if action == "snapshot":
            external_owned_opaque_paths = _external_owned_paths_from_environment(root)
            _add_semantic_exclusions(root, external_owned_opaque_paths)
            return _snapshot(
                root,
                boundary_path,
                external_owned_opaque_paths,
            )
        if action == "verify":
            return _verify(root, boundary_path)
        if action == "cleanup":
            return _cleanup(root, boundary_path, argv[4])
        external_owned_opaque_paths = _external_owned_paths_from_environment(root)
        return _recover(
            root,
            boundary_path,
            external_owned_opaque_paths,
        )
    except (ManifestError, OSError, UnicodeError) as error:
        print(f"[check-migration-boundary] 오류: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
