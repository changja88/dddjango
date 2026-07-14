#!/usr/bin/env python3
"""Run 문서 pair의 짧은 feature-local seed/CAS promotion을 수행한다."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path

ABSENT = "absent"
PROMOTION_RECEIPT_FORMAT = "dddjango-canonical-pair-receipt-v1"
PROMOTION_TRANSACTION_FORMAT = "dddjango-canonical-pair-transaction-v1"
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{7,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class PromotionError(ValueError):
    """Promotion 입력·경로·후조건이 계약을 만족하지 않을 때 발생한다."""


class PromotionConflict(PromotionError):
    """G0 canonical anchor 이후 다른 run이 canonical을 변경했을 때 발생한다."""


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise PromotionError(f"{label}은 non-symlink regular file이어야 한다: {path}")
    if not stat.S_ISREG(path.lstat().st_mode):
        raise PromotionError(f"{label}은 regular file이어야 한다: {path}")


def _actual_anchor(path: Path) -> str:
    if path.is_symlink():
        raise PromotionError(f"canonical symlink는 허용하지 않는다: {path}")
    if not path.exists():
        return ABSENT
    _validate_regular(path, "canonical artifact")
    return _digest(path)


def _validate_anchor(value: str) -> None:
    if value != ABSENT and SHA256.fullmatch(value) is None:
        raise PromotionError("EXPECTED anchor는 'absent' 또는 lowercase SHA-256이어야 한다")


def _replace(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".promotion",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists() or temporary.is_symlink():
            temporary.unlink()


def _restore(path: Path, original: bytes | None) -> None:
    if original is None:
        if path.exists() or path.is_symlink():
            path.unlink()
            directory_descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        return
    _replace(path, original)


def _unlink_sync(path: Path) -> None:
    path.unlink()
    directory_descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_descriptor)
    finally:
        os.close(directory_descriptor)


def _canonical_json(value: dict[str, object]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _receipt_bytes(anchors: tuple[str, str]) -> bytes:
    return _canonical_json(
        {
            "design_sha256": anchors[1],
            "format": PROMOTION_RECEIPT_FORMAT,
            "scope_sha256": anchors[0],
        }
    )


def _transaction_bytes(
    previous: tuple[str, str],
    intended: tuple[str, str],
) -> bytes:
    return _canonical_json(
        {
            "format": PROMOTION_TRANSACTION_FORMAT,
            "intended_design_sha256": intended[1],
            "intended_scope_sha256": intended[0],
            "previous_design_sha256": previous[1],
            "previous_scope_sha256": previous[0],
        }
    )


def _read_canonical_json(path: Path, label: str) -> tuple[dict[str, object], bytes]:
    _validate_regular(path, label)
    content = path.read_bytes()
    try:
        value = json.loads(content)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PromotionError(f"{label} JSON을 검증할 수 없다") from error
    if not isinstance(value, dict) or content != _canonical_json(value):
        raise PromotionError(f"{label}가 canonical JSON object가 아니다")
    return value, content


def _validate_receipt(receipt: Path, actual: tuple[str, str]) -> bytes | None:
    if receipt.is_symlink():
        raise PromotionError("promotion receipt symlink는 허용하지 않는다")
    if not receipt.exists():
        return None
    value, content = _read_canonical_json(receipt, "promotion receipt")
    expected = {
        "design_sha256": actual[1],
        "format": PROMOTION_RECEIPT_FORMAT,
        "scope_sha256": actual[0],
    }
    if value != expected:
        raise PromotionError(
            "canonical pair가 promotion receipt와 다르다 — incomplete/torn pair"
        )
    return content


def _canonical_state(
    feature_directory: Path,
) -> tuple[tuple[str, str], bytes | None]:
    targets = (feature_directory / "scope.md", feature_directory / "design-spec.md")
    actual = tuple(_actual_anchor(target) for target in targets)
    receipt = feature_directory / ".runs" / ".promotion-receipt.json"
    transaction = feature_directory / ".runs" / ".promotion-transaction.json"
    if transaction.is_symlink():
        raise PromotionError("promotion transaction symlink는 허용하지 않는다")
    if transaction.exists():
        value, _ = _read_canonical_json(transaction, "promotion transaction")
        previous = (
            value.get("previous_scope_sha256"),
            value.get("previous_design_sha256"),
        )
        intended = (
            value.get("intended_scope_sha256"),
            value.get("intended_design_sha256"),
        )
        valid_transaction = (
            value.get("format") == PROMOTION_TRANSACTION_FORMAT
            and all(isinstance(anchor, str) for anchor in previous)
            and all(isinstance(anchor, str) for anchor in intended)
            and all(
                anchor == ABSENT or SHA256.fullmatch(anchor) is not None
                for anchor in (*previous, *intended)
            )
        )
        if valid_transaction and actual == previous:
            _unlink_sync(transaction)
        elif valid_transaction and actual == intended:
            receipt_content = _validate_receipt(receipt, actual)
            if receipt_content is not None:
                _unlink_sync(transaction)
                return actual, receipt_content
            raise PromotionError(
                "canonical pair 교체 receipt가 없어 transaction 완료를 증명할 수 없다"
            )
        else:
            raise PromotionError(
                "미완료 canonical pair transaction이 남아 있다 — torn pair를 사용하지 않는다"
            )
    if receipt.is_symlink():
        raise PromotionError("promotion receipt symlink는 허용하지 않는다")
    if not receipt.exists():
        return actual, None
    _validate_regular(receipt, "promotion receipt")
    return actual, receipt.read_bytes()


def _open_lock(lock_path: Path) -> int:
    flags = os.O_CREAT | os.O_RDWR
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise PromotionError("promotion lock은 regular file이어야 한다")
    return descriptor


def _validate_run_directory(root: Path, run_directory: Path) -> Path:
    try:
        relative = run_directory.relative_to(root)
    except ValueError as error:
        raise PromotionError("RUN_DIR은 TARGET_DIR 내부여야 한다") from error
    run_id = run_directory.name
    if (
        RUN_ID.fullmatch(run_id) is None
        or len(relative.parts) != 4
        or relative.parts[0] != ".dddjango"
        or relative.parts[2] != ".runs"
        or run_directory.is_symlink()
        or not run_directory.is_dir()
    ):
        raise PromotionError("RUN_DIR은 <feature>/.runs/<portable-run-id> 실제 directory여야 한다")
    return run_directory.parent.parent


def _reject_symlink_ancestor(
    lexical_root: Path,
    lexical_path: Path,
    label: str,
) -> None:
    try:
        relative = lexical_path.relative_to(lexical_root)
    except ValueError as error:
        raise PromotionError(f"{label}은 TARGET_DIR 내부여야 한다") from error
    current = lexical_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise PromotionError(f"{label} 경로 조상에 symlink를 허용하지 않는다")


def _locked_stream(run_directory: Path):
    lock_path = run_directory.parent / ".promotion.lock"
    return os.fdopen(_open_lock(lock_path), "a+b", closefd=True)


def _seed(root: Path, run_directory: Path, *, for_rebase: bool = False) -> int:
    feature_directory = _validate_run_directory(root, run_directory)
    sources = (feature_directory / "scope.md", feature_directory / "design-spec.md")
    target_names = (
        (".canonical-base-scope.md", ".canonical-base-design-spec.md")
        if for_rebase
        else ("scope.md", "design-spec.md")
    )
    targets = tuple(run_directory / name for name in target_names)
    with _locked_stream(run_directory) as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        anchors, _ = _canonical_state(feature_directory)
        source_bytes = tuple(
            source.read_bytes() if anchor != ABSENT else None
            for source, anchor in zip(sources, anchors, strict=True)
        )
        originals = tuple(
            target.read_bytes() if target.exists() and not target.is_symlink() else None
            for target in targets
        )
        if any(target.is_symlink() for target in targets):
            raise PromotionError("run artifact symlink는 허용하지 않는다")
        try:
            for target, content in zip(targets, source_bytes, strict=True):
                _restore(target, content)
            actual = tuple(
                target.read_bytes() if target.exists() else None for target in targets
            )
            if actual != source_bytes:
                raise PromotionError("seed destination bytes가 canonical source와 다르다")
        except (OSError, PromotionError):
            for target, original in zip(targets, originals, strict=True):
                _restore(target, original)
            raise
    print(
        f"[promote-run-artifacts] {'rebase-base' if for_rebase else 'seeded'}: "
        f"scope={anchors[0]} design={anchors[1]}"
    )
    return 0


def _promote(
    root: Path,
    run_directory: Path,
    expected_scope: str,
    expected_design: str,
) -> int:
    _validate_anchor(expected_scope)
    _validate_anchor(expected_design)
    feature_directory = _validate_run_directory(root, run_directory)
    sources = (run_directory / "scope.md", run_directory / "design-spec.md")
    targets = (feature_directory / "scope.md", feature_directory / "design-spec.md")
    receipt = feature_directory / ".runs" / ".promotion-receipt.json"
    transaction = feature_directory / ".runs" / ".promotion-transaction.json"

    try:
        with _locked_stream(run_directory) as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            actual, original_receipt = _canonical_state(feature_directory)
            expected = (expected_scope, expected_design)
            if actual != expected:
                raise PromotionConflict(
                    "canonical anchor conflict — rebase와 G1 재승인이 필요하다: "
                    f"expected={expected!r}, actual={actual!r}"
                )
            for source in sources:
                _validate_regular(source, "run artifact")
            source_bytes = tuple(source.read_bytes() for source in sources)
            intended = tuple(
                hashlib.sha256(content).hexdigest() for content in source_bytes
            )
            originals = tuple(
                target.read_bytes() if target.exists() else None for target in targets
            )
            _replace(transaction, _transaction_bytes(actual, intended))
            try:
                _replace(targets[0], source_bytes[0])
                _replace(targets[1], source_bytes[1])
                current_sources = tuple(source.read_bytes() for source in sources)
                current_targets = tuple(target.read_bytes() for target in targets)
                if current_sources != source_bytes or current_targets != source_bytes:
                    raise PromotionError(
                        "promotion 동안 current-run/canonical bytes가 변경됐다"
                    )
                _replace(receipt, _receipt_bytes(intended))
                _unlink_sync(transaction)
            except (OSError, PromotionError):
                try:
                    _restore(targets[0], originals[0])
                    _restore(targets[1], originals[1])
                    _restore(receipt, original_receipt)
                    _unlink_sync(transaction)
                except OSError as rollback_error:
                    raise PromotionError(
                        "promotion rollback이 완료되지 않아 transaction marker를 보존했다"
                    ) from rollback_error
                raise
    except PromotionConflict:
        raise
    print(
        "[promote-run-artifacts] promoted: "
        f"{targets[0].relative_to(root)} + {targets[1].relative_to(root)}"
    )
    return 0


def _check(root: Path, run_directory: Path) -> int:
    feature_directory = _validate_run_directory(root, run_directory)
    sources = (run_directory / "scope.md", run_directory / "design-spec.md")
    targets = (feature_directory / "scope.md", feature_directory / "design-spec.md")
    with _locked_stream(run_directory) as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        actual, _ = _canonical_state(feature_directory)
        for source in sources:
            _validate_regular(source, "run artifact")
        source_bytes = tuple(source.read_bytes() for source in sources)
        source_anchors = tuple(
            hashlib.sha256(content).hexdigest() for content in source_bytes
        )
        if actual != source_anchors or tuple(
            target.read_bytes() if target.exists() else None for target in targets
        ) != source_bytes:
            raise PromotionConflict(
                "current-run pair가 최신 canonical pair와 다르다 — "
                "rebase와 G1 재승인이 필요하다"
            )
    print(
        "[promote-run-artifacts] checked: "
        f"scope={source_anchors[0]} design={source_anchors[1]}"
    )
    return 0


def main(argv: list[str]) -> int:
    if (
        len(argv) not in {4, 6}
        or argv[1] not in {"seed", "rebase", "check", "commit"}
        or (argv[1] in {"seed", "rebase", "check"}) != (len(argv) == 4)
    ):
        print(
            "사용법: promote-run-artifacts.py {seed|rebase|check} TARGET_DIR RUN_DIR | "
            "commit TARGET_DIR RUN_DIR EXPECTED_SCOPE_SHA256 EXPECTED_DESIGN_SHA256",
            file=sys.stderr,
        )
        return 1
    try:
        lexical_root = Path(argv[2]).expanduser().absolute()
        lexical_run_directory = Path(argv[3]).expanduser().absolute()
        _reject_symlink_ancestor(
            lexical_root,
            lexical_run_directory,
            "RUN_DIR",
        )
        root = lexical_root.resolve(strict=True)
        run_directory = lexical_run_directory.resolve(strict=True)
        if not root.is_dir():
            raise PromotionError("TARGET_DIR이 directory가 아니다")
        if argv[1] in {"seed", "rebase"}:
            return _seed(root, run_directory, for_rebase=argv[1] == "rebase")
        if argv[1] == "check":
            return _check(root, run_directory)
        return _promote(root, run_directory, argv[4], argv[5])
    except PromotionConflict as error:
        print(f"[promote-run-artifacts] CONFLICT: {error}", file=sys.stderr)
        return 2
    except (PromotionError, OSError) as error:
        print(f"[promote-run-artifacts] 오류: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
