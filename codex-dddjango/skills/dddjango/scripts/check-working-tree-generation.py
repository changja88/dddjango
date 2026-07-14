#!/usr/bin/env python3
"""Shared generation fingerprint와 변경 원장 path-state를 결정적으로 계산한다."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath

BUFFER_SIZE = 1024 * 1024
CACHE_DIRECTORIES = {
    ".cache",
    ".mypy_cache",
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
RECEIPT_FORMAT = "dddjango-migration-boundary-receipt-v2"
RECEIPT_SUFFIX = ".write-once"
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{7,127}$")


class GenerationError(ValueError):
    """Fingerprint 입력이나 저장소 상태가 계약을 만족하지 않을 때 발생한다."""


def _add_field(digest: hashlib._Hash, label: bytes, value: bytes) -> None:
    digest.update(len(label).to_bytes(4, "big"))
    digest.update(label)
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def _git(root: Path, *arguments: str, allow_failure: bool = False) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 and not allow_failure:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise GenerationError(f"git {' '.join(arguments)} 실패: {message}")
    return result.stdout if result.returncode == 0 else b"<unavailable>"


def _canonical_receipt(state_file: Path, manifest_sha256: str) -> str:
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


def _load_boundary(
    root: Path,
    state_file: Path,
) -> tuple[list[PurePosixPath], str]:
    receipt = state_file.with_name(f"{state_file.name}{RECEIPT_SUFFIX}")
    if (
        state_file.is_symlink()
        or receipt.is_symlink()
        or not state_file.is_file()
        or not receipt.is_file()
    ):
        raise GenerationError(
            "boundary state/receipt는 non-symlink regular file이어야 한다"
        )
    try:
        state_bytes = state_file.read_bytes()
        state = json.loads(state_bytes)
        receipt_text = receipt.read_text(encoding="utf-8")
        receipt_value = json.loads(receipt_text)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GenerationError("boundary state/receipt를 검증할 수 없다") from error
    if not isinstance(state, dict) or not isinstance(receipt_value, dict):
        raise GenerationError("boundary state/receipt 최상위 형식이 object가 아니다")
    state_hash = hashlib.sha256(state_bytes).hexdigest()
    if receipt_value != json.loads(_canonical_receipt(state_file, state_hash)):
        raise GenerationError("boundary receipt가 state와 일치하지 않는다")
    if receipt_text != _canonical_receipt(state_file, state_hash):
        raise GenerationError("boundary receipt가 canonical 형식이 아니다")
    if state.get("root") != str(root):
        raise GenerationError("boundary root가 TARGET_DIR과 다르다")
    paths: list[PurePosixPath] = []
    for key in (
        "migration_roots",
        "migration_alias_targets",
        "external_owned_opaque_paths",
    ):
        values = state.get(key)
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ):
            raise GenerationError(f"boundary {key} 형식이 올바르지 않다")
        for value in values:
            path = PurePosixPath(value)
            if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
                raise GenerationError(f"boundary path가 상대 정규 경로가 아니다: {value!r}")
            paths.append(path)
    return paths, state_hash


def _relative(root: Path, path: Path, label: str) -> PurePosixPath:
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise GenerationError(f"{label}는 TARGET_DIR 내부여야 한다") from error
    if path.is_symlink():
        raise GenerationError(f"{label} symlink는 허용하지 않는다")
    return PurePosixPath(relative.as_posix())


def _reject_symlink_ancestor(
    lexical_root: Path,
    lexical_path: Path,
    label: str,
    *,
    include_leaf: bool = True,
) -> None:
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise GenerationError(f"{label}는 TARGET_DIR 내부여야 한다") from error
    current = lexical_root
    parts = relative.parts if include_leaf else relative.parts[:-1]
    for part in parts:
        current /= part
        if current.is_symlink():
            raise GenerationError(f"{label} 경로 조상에 symlink를 허용하지 않는다")


def _is_relative_to(path: PurePosixPath, parent: PurePosixPath) -> bool:
    return path == parent or path.is_relative_to(parent)


def _excluded(
    path: PurePosixPath,
    opaque_paths: list[PurePosixPath],
    current_documents: set[PurePosixPath],
) -> bool:
    if path in current_documents:
        return False
    if ".git" in path.parts or any(part in CACHE_DIRECTORIES for part in path.parts):
        return True
    if ".runs" in path.parts:
        return True
    return any(_is_relative_to(path, opaque) for opaque in opaque_paths)


def _split_nul(value: bytes) -> list[bytes]:
    return [item for item in value.split(b"\0") if item]


def _path_from_git(root: Path, raw_path: bytes) -> tuple[PurePosixPath, Path]:
    if raw_path.startswith(b"/") or b"\0" in raw_path:
        raise GenerationError("git이 절대/비정규 경로를 반환했다")
    decoded = os.fsdecode(raw_path)
    pure = PurePosixPath(decoded)
    if any(part in {"", ".", ".."} for part in pure.parts):
        raise GenerationError(f"git 경로가 상대 정규 경로가 아니다: {decoded!r}")
    return pure, root.joinpath(*pure.parts)


def _file_digest(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(BUFFER_SIZE):
            digest.update(chunk)
    return digest.digest()


def _add_path(digest: hashlib._Hash, root: Path, raw_path: bytes) -> None:
    pure, path = _path_from_git(root, raw_path)
    _add_field(digest, b"path", raw_path)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        _add_field(digest, b"kind", b"missing")
        return
    mode = metadata.st_mode
    _add_field(digest, b"mode", mode.to_bytes(8, "big"))
    if stat.S_ISREG(mode):
        _add_field(digest, b"kind", b"file")
        _add_field(digest, b"content-sha256", _file_digest(path))
    elif stat.S_ISLNK(mode):
        _add_field(digest, b"kind", b"symlink")
        _add_field(digest, b"link", os.fsencode(os.readlink(path)))
    elif stat.S_ISDIR(mode):
        _add_field(digest, b"kind", b"directory")
    else:
        _add_field(digest, b"kind", b"special")


def _gitlinks(index: bytes) -> list[bytes]:
    paths: list[bytes] = []
    for entry in _split_nul(index):
        metadata, separator, path = entry.partition(b"\t")
        if not separator:
            raise GenerationError("git index 출력 형식이 올바르지 않다")
        mode = metadata.split(b" ", 1)[0]
        if mode == b"160000":
            paths.append(path)
    return sorted(paths)


def _filtered_index(
    root: Path,
    index: bytes,
    opaque_paths: list[PurePosixPath],
    current_documents: set[PurePosixPath],
) -> bytes:
    entries: list[bytes] = []
    for entry in _split_nul(index):
        metadata, separator, raw_path = entry.partition(b"\t")
        fields = metadata.split(b" ")
        if not separator or len(fields) != 3 or not raw_path:
            raise GenerationError("git index 출력 형식이 올바르지 않다")
        pure, _ = _path_from_git(root, raw_path)
        if _excluded(pure, opaque_paths, current_documents):
            continue
        entries.append(metadata + b"\t" + raw_path + b"\0")
    return b"".join(sorted(entries))


def _fingerprint(root: Path, state_file: Path, run_directory: Path) -> str:
    opaque_paths, state_hash = _load_boundary(root, state_file)
    state_relative = _relative(
        root,
        state_file.resolve(strict=True),
        "BOUNDARY_STATE",
    )
    run_relative = _relative(root, run_directory, "CURRENT_RUN_DIR")
    run_id = run_directory.name
    if (
        RUN_ID.fullmatch(run_id) is None
        or len(run_relative.parts) != 4
        or run_relative.parts[0] != ".dddjango"
        or run_relative.parts[2] != ".runs"
        or not run_directory.is_dir()
    ):
        raise GenerationError(
            "CURRENT_RUN_DIR은 exact .dddjango/<feature>/.runs/<run-id> "
            "실제 directory여야 한다"
        )
    if state_file.resolve(strict=True).parent != run_directory or not (
        state_file.name.startswith("migration-boundary-epoch-")
        and state_file.name.endswith(f"-{run_id}.json")
    ):
        raise GenerationError(
            "BOUNDARY_STATE는 CURRENT_RUN_DIR의 expected run-id exact pair여야 한다"
        )
    feature_directory = run_directory.parent.parent
    feature_relative = _relative(root, feature_directory, "feature directory")
    transaction = run_directory.parent / ".promotion-transaction.json"
    if transaction.exists() or transaction.is_symlink():
        raise GenerationError(
            "미완료 canonical pair transaction이 있어 generation을 시작할 수 없다"
        )
    current_pair = (run_directory / "scope.md", run_directory / "design-spec.md")
    canonical_pair = (
        feature_directory / "scope.md",
        feature_directory / "design-spec.md",
    )
    for path in (*current_pair, *canonical_pair):
        if path.is_symlink() or not path.is_file():
            raise GenerationError(
                "current-run/canonical scope/design은 non-symlink regular file이어야 한다"
            )
    if tuple(path.read_bytes() for path in current_pair) != tuple(
        path.read_bytes() for path in canonical_pair
    ):
        raise GenerationError(
            "current-run pair가 최신 canonical pair와 다르다 — "
            "rebase와 G1 재승인이 필요하다"
        )
    current_documents = {
        run_relative / "scope.md",
        run_relative / "design-spec.md",
        feature_relative / "scope.md",
        feature_relative / "design-spec.md",
    }

    head = _git(root, "rev-parse", "--verify", "HEAD", allow_failure=True)
    raw_index = _git(root, "ls-files", "--stage", "-z")
    dirty = _split_nul(_git(root, "diff", "--name-only", "-z"))
    untracked = _split_nul(
        _git(root, "ls-files", "--others", "--exclude-standard", "-z")
    )
    selected: dict[bytes, PurePosixPath] = {}
    for raw_path in [*dirty, *untracked]:
        pure, _ = _path_from_git(root, raw_path)
        if not _excluded(pure, opaque_paths, current_documents):
            selected[raw_path] = pure
    for document in current_documents:
        selected[os.fsencode(document.as_posix())] = document
    index = _filtered_index(root, raw_index, opaque_paths, current_documents)

    digest = hashlib.sha256()
    _add_field(digest, b"format", b"dddjango-working-tree-generation-v1")
    _add_field(digest, b"boundary-state-path", os.fsencode(state_relative.as_posix()))
    _add_field(digest, b"boundary-state-sha256", state_hash.encode("ascii"))
    _add_field(digest, b"head", head.rstrip(b"\n"))
    _add_field(digest, b"index", index)
    for raw_path in sorted(selected):
        _add_path(digest, root, raw_path)
    for raw_path in _gitlinks(index):
        pure, path = _path_from_git(root, raw_path)
        if _excluded(pure, opaque_paths, current_documents):
            continue
        _add_field(digest, b"submodule-path", raw_path)
        if path.is_dir():
            _add_field(
                digest,
                b"submodule-head",
                _git(path, "rev-parse", "--verify", "HEAD", allow_failure=True).rstrip(b"\n"),
            )
            _add_field(
                digest,
                b"submodule-status",
                _git(path, "status", "--porcelain=v1", "-z", allow_failure=True),
            )
        else:
            _add_field(digest, b"submodule-head", b"<missing>")
    return digest.hexdigest()


def _ledger_path_state(root: Path, relative: PurePosixPath) -> str:
    raw_path = os.fsencode(relative.as_posix())
    _, path = _path_from_git(root, raw_path)
    try:
        path.lstat()
    except FileNotFoundError:
        return "absent"
    digest = hashlib.sha256()
    _add_field(digest, b"format", b"dddjango-path-state-v1")
    _add_path(digest, root, raw_path)
    return digest.hexdigest()


def _path_state_main(argv: list[str]) -> int:
    lexical_root = Path(argv[2]).expanduser().absolute()
    supplied_path = Path(argv[3]).expanduser()
    lexical_path = (
        supplied_path.absolute()
        if supplied_path.is_absolute()
        else lexical_root / supplied_path
    )
    _reject_symlink_ancestor(
        lexical_root,
        lexical_path,
        "PATH",
        include_leaf=False,
    )
    root = lexical_root.resolve(strict=True)
    if not root.is_dir():
        raise GenerationError("TARGET_DIR이 directory가 아니다")
    try:
        relative_path = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise GenerationError("PATH는 TARGET_DIR 내부여야 한다") from error
    relative = PurePosixPath(relative_path.as_posix())
    if not relative.parts or any(
        part in {"", ".", ".."} for part in relative.parts
    ):
        raise GenerationError("PATH는 TARGET_DIR 내부의 상대 정규 경로여야 한다")
    value = _ledger_path_state(root, relative)
    print(f"[check-working-tree-generation] path-state={value}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 4 and argv[1] == "path-state":
        try:
            return _path_state_main(argv)
        except (GenerationError, OSError) as error:
            print(f"[check-working-tree-generation] 오류: {error}", file=sys.stderr)
            return 1
    if len(argv) != 4:
        print(
            "사용법: check-working-tree-generation.py "
            "TARGET_DIR BOUNDARY_STATE CURRENT_RUN_DIR | "
            "path-state TARGET_DIR PATH",
            file=sys.stderr,
        )
        return 1
    try:
        lexical_root = Path(argv[1]).expanduser().absolute()
        state_file = Path(argv[2]).expanduser().absolute()
        lexical_run_directory = Path(argv[3]).expanduser().absolute()
        _reject_symlink_ancestor(lexical_root, state_file, "BOUNDARY_STATE")
        _reject_symlink_ancestor(
            lexical_root,
            lexical_run_directory,
            "CURRENT_RUN_DIR",
        )
        root = lexical_root.resolve(strict=True)
        run_directory = lexical_run_directory.resolve(strict=True)
        if not root.is_dir():
            raise GenerationError("TARGET_DIR이 directory가 아니다")
        value = _fingerprint(root, state_file, run_directory)
    except (GenerationError, OSError) as error:
        print(f"[check-working-tree-generation] 오류: {error}", file=sys.stderr)
        return 1
    print(f"[check-working-tree-generation] sha256={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
