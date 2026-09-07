#!/usr/bin/env python3
"""Preserve an original design export, including files used only by its runtime.

Usage: archive_design.py ENTRY --source-root EXPORT --out BUILD/design-ref
       --manifest BUILD/source-manifest.json

This byte archive is NOT a successful static dependency closure. It requires
case-bound original browser observations and independent coverage review before
check_design_evidence accepts it. Never rewrite source/runtime/CSS to make it pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from asset_io import MAX_BYTES, digest_fields, write_verified
from design_sources import resource_kind


def archive_files(root: Path) -> list[Path]:
    """Inventory the whole supplied tree, not just statically reachable files."""
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'symlink in source archive: {path.relative_to(root)}')
        if path.is_file() and path.name != '.DS_Store':
            files.append(path)
    if not files or len(files) > 4096:
        raise ValueError('source archive requires 1..4096 files')
    return files


def archive(entry: Path, source_root: Path, out: Path, manifest_path: Path) -> dict:
    source_root, entry = source_root.resolve(strict=True), entry.resolve(strict=True)
    out, manifest_path = out.resolve(), manifest_path.absolute()
    if not source_root.is_dir() or not entry.is_file() or not entry.is_relative_to(source_root):
        raise ValueError('entry must be a file inside --source-root')
    if resource_kind(entry.as_uri()) not in ('html', 'component'):
        raise ValueError('archive entry must be original HTML/JSX; image-only designs use freeze_design.py')
    if out.is_relative_to(source_root) or source_root.is_relative_to(out):
        raise ValueError('--out and --source-root must be disjoint')
    if (manifest_path.is_symlink() or manifest_path.resolve().is_relative_to(out)
            or not manifest_path.resolve().is_relative_to(out.parent)):
        raise ValueError('--manifest must be a sibling of --out, outside the archive tree')
    manifest = {'version': 1, 'collection': 'archive', 'source_root': str(source_root),
                'entrypoint': entry.relative_to(source_root).as_posix(),
                'source_ready': False, 'archive_ready': False, 'files': []}
    files = archive_files(source_root)
    for source in files:
        relative = source.relative_to(source_root)
        destination = out / relative
        if not destination.resolve().is_relative_to(out):
            raise ValueError('archive destination escapes output root')
        with source.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError(f'archive file exceeds 32 MiB: {relative}')
        if source == entry:
            if not data:
                raise ValueError('empty original entrypoint')
            data.decode('utf-8-sig')
        kind = resource_kind(source.as_uri())
        write_verified(destination, data)
        manifest['files'].append({'source': str(source), 'source_document': '',
            'local_path': relative.as_posix(), 'kind': kind, 'status': 'ok',
            'reason': '', **digest_fields(data)})
    # Reusing a directory with stale/unrecorded files is not a complete archive.
    if {p.relative_to(out).as_posix() for p in archive_files(out)} != {r['local_path'] for r in manifest['files']}:
        raise ValueError('output inventory differs; use a fresh output directory')
    manifest['archive_ready'] = True
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_verified(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entry', type=Path)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = archive(args.entry, args.source_root, args.out, args.manifest)
    except (OSError, ValueError) as error:
        print(f'[design-archive] failed: {error}', file=sys.stderr)
        return 1
    print(f'[design-archive] {len(manifest["files"])} files preserved; source_ready=false; original browser observations required')
    return 0


if __name__ == '__main__':
    sys.exit(main())
