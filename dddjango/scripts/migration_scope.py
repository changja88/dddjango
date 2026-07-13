"""Non-migration backstops에서 external-owned migration 경로를 열지 않는 공통 경계."""
from __future__ import annotations

import json
import hashlib
import os
import stat
import sys
from fnmatch import fnmatch
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Iterable

BOUNDARY_STATE_ENV = "DDDJANGO_G0_BOUNDARY_STATE"
BOUNDARY_MANIFEST_FORMAT = "dddjango-migration-boundary-v11"
BOUNDARY_RECEIPT_FORMAT = "dddjango-migration-boundary-receipt-v2"
BOUNDARY_RECEIPT_SUFFIX = ".write-once"


class MigrationScopeError(ValueError):
    """공유된 G0 boundary state가 안전한 경로 집합을 제공하지 못할 때 발생한다."""


_IN_MEMORY_SCOPES: dict[
    Path,
    tuple[tuple[PurePosixPath, ...], tuple[PurePosixPath, ...]],
] = {}


def _normalize_paths(
    raw_paths: Iterable[str],
    label: str,
) -> tuple[PurePosixPath, ...]:
    items = list(raw_paths)
    if not all(isinstance(item, str) and item for item in items):
        raise MigrationScopeError(f"G0 {label}가 문자열 목록이 아니다")
    roots: list[PurePosixPath] = []
    for item in items:
        path = PurePosixPath(item)
        if (
            item == "."
            or not path.parts
            or path.is_absolute()
            or path.as_posix() != item
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise MigrationScopeError(
                f"G0 {label} 항목이 상대 정규 경로가 아니다: {item!r}"
            )
        roots.append(path)
    if roots != sorted(roots, key=lambda item: item.as_posix()) or len(roots) != len(
        set(roots)
    ):
        raise MigrationScopeError(f"G0 {label}가 정렬된 고유 목록이 아니다")
    return tuple(roots)


@lru_cache(maxsize=8)
def _configured_scope(
    root: Path,
    state_name: str,
) -> tuple[tuple[PurePosixPath, ...], tuple[PurePosixPath, ...]]:
    if not state_name:
        raise MigrationScopeError(
            f"{BOUNDARY_STATE_ENV}가 없다 — non-migration 백스톱은 "
            "정확한 G0 migration_roots 없이 실행하지 않는다"
        )
    state_file = Path(state_name).expanduser().absolute()
    if state_file.is_symlink() or not state_file.is_file():
        raise MigrationScopeError(
            f"G0 migration boundary state가 regular file이 아니다: {state_file}"
        )
    if not stat.S_ISREG(state_file.lstat().st_mode):
        raise MigrationScopeError(
            f"G0 migration boundary state가 regular file이 아니다: {state_file}"
        )
    try:
        serialized = state_file.read_bytes()
        value = json.loads(serialized.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MigrationScopeError(
            f"G0 migration boundary state를 읽을 수 없다: {state_file}"
        ) from error
    if not isinstance(value, dict) or value.get("format") != BOUNDARY_MANIFEST_FORMAT:
        raise MigrationScopeError("G0 migration boundary state format이 지원되지 않는다")
    canonical = (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if serialized != canonical:
        raise MigrationScopeError("G0 migration boundary state가 canonical JSON이 아니다")
    receipt = state_file.with_name(f"{state_file.name}{BOUNDARY_RECEIPT_SUFFIX}")
    if receipt.is_symlink() or not receipt.is_file():
        raise MigrationScopeError(f"G0 migration boundary receipt가 없다: {receipt}")
    try:
        receipt_serialized = receipt.read_text(encoding="utf-8")
        receipt_value = json.loads(receipt_serialized)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise MigrationScopeError(
            f"G0 migration boundary receipt를 읽을 수 없다: {receipt}"
        ) from error
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
        raise MigrationScopeError("G0 migration boundary receipt가 state와 일치하지 않는다")
    if value.get("root") != str(root):
        raise MigrationScopeError("G0 migration boundary state root가 TARGET_DIR과 다르다")
    raw_roots = value.get("migration_roots")
    if not isinstance(raw_roots, list):
        raise MigrationScopeError("G0 migration boundary state에 migration_roots가 없다")
    raw_alias_targets = value.get("migration_alias_targets")
    if not isinstance(raw_alias_targets, list):
        raise MigrationScopeError(
            "G0 migration boundary state에 migration_alias_targets가 없다"
        )
    raw_opaque = value.get("external_owned_opaque_paths")
    if not isinstance(raw_opaque, list):
        raise MigrationScopeError(
            "G0 migration boundary state에 external_owned_opaque_paths가 없다"
        )
    migration_roots = _normalize_paths(raw_roots, "migration_roots")
    alias_targets = _normalize_paths(
        raw_alias_targets,
        "migration_alias_targets",
    )
    owned_paths = tuple(
        sorted(
            set((*migration_roots, *alias_targets)),
            key=lambda item: item.as_posix(),
        )
    )
    return owned_paths, _normalize_paths(
        raw_opaque,
        "external_owned_opaque_paths",
    )


def configure_migration_scope(
    root: Path,
    raw_roots: Iterable[str],
    external_owned_opaque_paths: Iterable[str] = (),
) -> None:
    """G0 manifest를 만드는 boundary 내부 호출처럼 파일 전 상태의 exact roots를 주입한다."""
    _IN_MEMORY_SCOPES[root] = (
        _normalize_paths(raw_roots, "migration_roots"),
        _normalize_paths(
            external_owned_opaque_paths,
            "external_owned_opaque_paths",
        ),
    )


def require_migration_scope(root: Path) -> tuple[PurePosixPath, ...]:
    """현재 TARGET_DIR에 대응하는 정확한 G0 migration root 집합을 검증해 반환한다."""
    configured = _IN_MEMORY_SCOPES.get(root)
    if configured is not None:
        return configured[0]
    state_name = os.environ.get(BOUNDARY_STATE_ENV, "")
    return _configured_scope(root, state_name)[0]


def require_external_owned_opaque_paths(root: Path) -> tuple[PurePosixPath, ...]:
    """현재 G0에서 명시된 lifecycle-test 등 exact opaque 경로 집합."""
    configured = _IN_MEMORY_SCOPES.get(root)
    if configured is not None:
        return configured[1]
    state_name = os.environ.get(BOUNDARY_STATE_ENV, "")
    return _configured_scope(root, state_name)[1]


def validate_migration_scope(root: Path, checker: str) -> bool:
    """검사 시작 전에 scope를 fail-closed로 확인하고 사용 오류를 일관되게 보고한다."""
    try:
        require_migration_scope(root)
        require_external_owned_opaque_paths(root)
    except MigrationScopeError as error:
        print(f"[{checker}] 사용 오류: {error}", file=sys.stderr)
        return False
    return True


def is_migration_owned_path(root: Path, path: Path) -> bool:
    """정확한 migration root(내부 alias 포함) 또는 repo-external opaque 경로인가.

    일반 백스톱이 symlink를 따라 migration 내용이나 저장소 밖 내용을 여는 것도 막는다.
    경로 이름 자체는 추론 신호로 쓰지 않는다.
    """
    declared_paths = (
        *require_migration_scope(root),
        *require_external_owned_opaque_paths(root),
    )
    roots = list(declared_paths)
    for declared in declared_paths:
        try:
            resolved_root = (root / declared.as_posix()).resolve(strict=False)
            resolved_relative = PurePosixPath(
                resolved_root.relative_to(root).as_posix()
            )
        except (OSError, RuntimeError, ValueError):
            continue
        if resolved_relative not in roots:
            roots.append(resolved_relative)
    try:
        relative = PurePosixPath(path.relative_to(root).as_posix())
    except ValueError:
        return True

    def matches(candidate: PurePosixPath) -> bool:
        return any(
            candidate == migration_root or candidate.is_relative_to(migration_root)
            for migration_root in roots
        )

    if matches(relative):
        return True
    try:
        resolved = path.resolve(strict=False)
        resolved_relative = PurePosixPath(resolved.relative_to(root).as_posix())
    except (OSError, RuntimeError, ValueError):
        return True
    return matches(resolved_relative)


def iter_non_migration_files(
    root: Path,
    start: Path | None = None,
    name_pattern: str = "*",
) -> Iterable[Path]:
    """Exact migration roots를 진입 전에 prune하는 결정적 파일 walker."""
    require_migration_scope(root)
    start_dir = start or root
    if is_migration_owned_path(root, start_dir) or not start_dir.is_dir():
        return
    for current_name, directory_names, file_names in os.walk(
        start_dir,
        topdown=True,
        followlinks=False,
    ):
        current = Path(current_name)
        directory_names[:] = sorted(
            name
            for name in directory_names
            if not is_migration_owned_path(root, current / name)
        )
        for name in sorted(file_names):
            path = current / name
            if fnmatch(name, name_pattern) and not is_migration_owned_path(root, path):
                yield path


def iter_non_migration_directories(
    root: Path,
    start: Path | None = None,
) -> Iterable[Path]:
    """Exact migration roots를 진입 전에 prune하며 디렉터리를 깊이순회한다."""
    require_migration_scope(root)
    start_dir = start or root
    if is_migration_owned_path(root, start_dir) or not start_dir.is_dir():
        return
    for current_name, directory_names, _ in os.walk(
        start_dir,
        topdown=True,
        followlinks=False,
    ):
        current = Path(current_name)
        kept = sorted(
            name
            for name in directory_names
            if not is_migration_owned_path(root, current / name)
        )
        directory_names[:] = kept
        for name in kept:
            yield current / name
