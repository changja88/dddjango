#!/usr/bin/env python3
"""Preserve an original design export, including files used only by its runtime.

Usage: archive_design.py ENTRY --source-root EXPORT --out BUILD/design-ref
       --manifest BUILD/source-manifest.json

This byte archive is NOT a successful static dependency closure. It requires
case-bound original browser observations and independent coverage review before
check_design_evidence accepts it. Never rewrite source/runtime/CSS to make it pass.
The manifest includes a dependency report for ENTRY. Missing literal local files
return exit 1 after preserving the archive/report; runtime and remote edges stay
explicitly unresolved for browser observation. Exit 0 is not rendering approval.
Archived names (entrypoint, local_path, files under --out) are Unicode NFC; each
row's source keeps the original path. References inside files are not rewritten,
so this assumes a filesystem that opens either form of a name (APFS, HFS+).
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import json
from pathlib import Path
import sys
import unicodedata
import urllib.parse

from asset_io import MAX_BYTES, digest_fields, write_verified
from design_sources import Dependencies, dependencies, resource_kind


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


def archive_url(root: Path, reference: str, base: str) -> str:
    """Resolve a local URL with the export directory as its web root."""
    if reference.startswith('/'):
        return urllib.parse.urljoin(root.as_uri() + '/', reference.lstrip('/'))
    return urllib.parse.urljoin(base, reference)


def archive_dependencies(root: Path, entry: Path) -> list[dict]:
    """Locate literal local dependencies; leave runtime/remote edges for observation.

    Document-relative JSX resources keep their importing HTML base. Only the
    selected entry's reachable files are scanned; unrelated archived screens
    are checked when they become a case entrypoint. No code or network executes.
    """
    root, entry = root.resolve(), entry.resolve()
    if not entry.is_relative_to(root) or not entry.is_file():
        raise ValueError('dependency entry must be a file inside the archive')
    pending = deque([(entry, (entry.as_uri(), 'local'), resource_kind(entry.as_uri()))])
    seen = set()
    rows = []
    while pending:
        path, document, kind = pending.popleft()
        context = (path, document, kind)
        if context in seen or kind not in ('html', 'component', 'css', 'script'):
            continue
        seen.add(context)
        if len(seen) > 4096:
            raise ValueError('archive dependency contexts exceed 4096')
        source = path.read_text(encoding='utf-8-sig')
        if kind == 'html':
            parser = Dependencies()
            parser.feed(source)
            found = list(dict.fromkeys(parser.rows))
            document = (path.as_uri(), 'local')
            if parser.base_href is not None:
                href = parser.base_href
                parsed_base = urllib.parse.urlsplit(href)
                if '{' in href or '}' in href:
                    document = (href, 'runtime')
                elif parsed_base.scheme or parsed_base.netloc:
                    document = (href, 'external')
                else:
                    document = (archive_url(root, href, path.as_uri()), 'local')
        else:
            found = dependencies(source, kind)
        for reference, child_kind, base_kind in found:
            row = {'source_document': path.relative_to(root).as_posix(), 'source': reference,
                   'kind': child_kind, 'local_path': '', 'status': '', 'reason': ''}
            rows.append(row)
            if '{' in reference or '}' in reference:
                row.update(status='runtime', reason='original runtime observation required')
                continue
            if reference.startswith(('data:', '#')):
                row['status'] = 'inline'
                continue
            parsed = urllib.parse.urlsplit(reference)
            if parsed.scheme or parsed.netloc:
                row.update(status='external', reason='original browser response required; not acquired by archive')
                continue
            value = urllib.parse.unquote(parsed.path)
            if not value:
                row['status'] = 'inline'
                continue
            base, base_status = document if kind == 'html' or base_kind == 'document' else (path.as_uri(), 'local')
            if base_status != 'local':
                row.update(status=base_status, reason='original document base requires browser observation')
                continue
            resolved = urllib.parse.urlsplit(archive_url(root, reference, base))
            target = Path(urllib.parse.unquote(resolved.path)).resolve()
            if not target.is_relative_to(root):
                row.update(status='missing', reason='local dependency escapes archive root')
            elif not target.is_file():
                row.update(local_path=target.relative_to(root).as_posix(), status='missing',
                           reason='local dependency absent from archive')
            else:
                row.update(local_path=target.relative_to(root).as_posix(), status='ok')
                pending.append((target, (target.as_uri(), 'local') if child_kind == 'html' else document, child_kind))
    return rows


def archive(entry: Path, source_root: Path, out: Path, manifest_path: Path) -> dict:
    source_root, entry = source_root.resolve(strict=True), entry.resolve(strict=True)
    out, manifest_path = out.resolve(), manifest_path.absolute()
    if not source_root.is_dir() or not entry.is_file() or not entry.is_relative_to(source_root):
        hint = ''
        if entry.is_file() and Path(unicodedata.normalize('NFC', str(entry))).is_relative_to(
                unicodedata.normalize('NFC', str(source_root))):
            hint = '; ENTRY and --source-root spell a folder in different Unicode forms (NFC/NFD)'
        raise ValueError('entry must be a file inside --source-root' + hint)
    if resource_kind(entry.as_uri()) not in ('html', 'component'):
        raise ValueError('archive entry must be original HTML/JSX; image-only designs use freeze_design.py')
    if out.is_relative_to(source_root) or source_root.is_relative_to(out):
        raise ValueError('--out and --source-root must be disjoint')
    if (manifest_path.is_symlink() or manifest_path.resolve().is_relative_to(out)
            or not manifest_path.resolve().is_relative_to(out.parent)):
        raise ValueError('--manifest must be a sibling of --out, outside the archive tree')
    # macOS unzip writes Korean names as NFD and git checks them out as NFC. NFC names keep
    # the manifest, the ENTRY argument (either form) and every checkout of --out in agreement.
    manifest = {'version': 1, 'collection': 'archive', 'source_root': str(source_root),
                'entrypoint': unicodedata.normalize('NFC', entry.relative_to(source_root).as_posix()),
                'source_ready': False, 'archive_ready': False, 'files': []}
    files = archive_files(source_root)
    relatives = [unicodedata.normalize('NFC', source.relative_to(source_root).as_posix()) for source in files]
    collided = [name for name, count in Counter(relatives).items() if count > 1]
    if collided:
        raise ValueError(f'source names collide after Unicode NFC normalization: {", ".join(collided)}')
    if manifest['entrypoint'] not in relatives:  # e.g. letter case typed unlike the stored name
        raise ValueError(f'entry {manifest["entrypoint"]!r} is spelled unlike its listed file name; '
                         'pass the name as listed in --source-root')
    for source, relative in zip(files, relatives):
        destination = out / relative
        if not destination.resolve().is_relative_to(out):
            raise ValueError('archive destination escapes output root')
        with source.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError(f'archive file exceeds 32 MiB: {relative}')
        if relative == manifest['entrypoint']:
            if not data:
                raise ValueError('empty original entrypoint')
            data.decode('utf-8-sig')
        kind = resource_kind(source.as_uri())
        write_verified(destination, data)
        manifest['files'].append({'source': str(source), 'source_document': '',
            'local_path': relative, 'kind': kind, 'status': 'ok',
            'reason': '', **digest_fields(data)})
    # Reusing a directory with stale/unrecorded files is not a complete archive. A filesystem
    # may store NFD (HFS+) or keep an older twin in the other form, so compare NFC lists.
    written = sorted(unicodedata.normalize('NFC', p.relative_to(out).as_posix()) for p in archive_files(out))
    if written != sorted(r['local_path'] for r in manifest['files']):
        raise ValueError('output inventory differs; use a fresh output directory')
    manifest['archive_ready'] = True
    manifest['dependencies'] = archive_dependencies(out, out / manifest['entrypoint'])
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
    missing = [row for row in manifest['dependencies'] if row['status'] == 'missing']
    for row in missing:
        print(f'[design-archive] missing: {row["source"]!r} in {row["source_document"]}: {row["reason"]}', file=sys.stderr)
    print(f'[design-archive] {len(manifest["files"])} files preserved; {len(missing)} missing local dependencies; '
          'source_ready=false; original browser observations required')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
