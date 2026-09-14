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
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
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
    manifest['dependencies'] = archive_dependencies(out, out / manifest['entrypoint'])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_verified(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode())
    return manifest


def _reference_context(build: Path) -> tuple[Path, Path]:
    """design-input.json에서 reference_root와 기준(base) manifest 경로를 읽는다(K4).

    manifests[0]은 인자로 고르지 않는다 — design-input.json이 유일한 출처다.
    """
    spec = json.loads((build / 'design-input.json').read_text(encoding='utf-8-sig'))
    manifests = spec.get('manifests')
    if not isinstance(manifests, list) or not manifests or not isinstance(manifests[0], str):
        raise ValueError('design-input.json manifests[0] missing')
    reference_value = spec.get('reference_root')
    reference_root = (build / reference_value).resolve() if isinstance(reference_value, str) else build.resolve()
    base_manifest_path = (build / manifests[0]).resolve()
    if not base_manifest_path.is_file():
        raise ValueError(f'base manifest not found: {manifests[0]}')
    return reference_root, base_manifest_path


def compare_manifests(new: dict, base: dict, carried: set[str], build: Path, out: Path) -> dict:
    """재동결 staging manifest(new)를 기준 manifest(base)와 local_path 단위로 대조한다(K4).

    carried로 분류된 파일은 기준 바이트와 비교하지 않고 '미확인'으로만 센다 — 같은 바이트라도
    same이 아니라 carried다. 자동 carried = staging 파일 행의 source가 reference_root ·
    BUILD/_history · (현재 --out의 상위 _staging-<ts>를 제외한) BUILD/_staging-* 아래일 때.
    명시 carried는 entrypoint 의존성 closure 밖 파일에만 허용하며, closure 안이면
    ValueError('carried dependency: ...')를 낸다 — 호출부가 exit 1로 옮긴다. staging에도
    기준에도 없는 경로(오타)는 ValueError('carried target not in staging: ...')다 — 아무
    행도 소비하지 않는 인자가 성공 종료로 지나가지 않는다.
    반환: {rows:[{local_path,status,size_bytes,sha12,mtime,carried_from?}], summary, exit:0|3|4}.
    """
    build = build.resolve(strict=True)
    out = out.resolve()
    reference_root, base_manifest_path = _reference_context(build)
    base_manifest_sha256 = hashlib.sha256(base_manifest_path.read_bytes()).hexdigest()

    closure = {row['local_path'] for row in new.get('dependencies', [])
               if row.get('status') == 'ok' and row.get('local_path')}
    entrypoint = new.get('entrypoint')
    if isinstance(entrypoint, str):
        closure.add(entrypoint)
    for local in carried:
        if local in closure:
            raise ValueError(f'carried dependency: {local}')

    history_root = build / '_history'
    current_staging = out.parent if out.parent.name.startswith('_staging-') else None
    other_staging = [path for path in sorted(build.glob('_staging-*'))
                      if path.is_dir() and (current_staging is None or path.resolve() != current_staging.resolve())]

    def is_auto_carried(source: str) -> bool:
        if not source:
            return False
        try:
            source_path = Path(source).resolve()
        except (OSError, RuntimeError, ValueError):
            return False
        if source_path.is_relative_to(reference_root) or source_path.is_relative_to(history_root):
            return True
        return any(source_path.is_relative_to(staging_dir) for staging_dir in other_staging)

    def source_mtime(source: str) -> float | None:
        if not source:
            return None
        try:
            return Path(source).stat().st_mtime
        except OSError:
            return None

    base_files = {row['local_path']: row for row in base.get('files', []) if row.get('local_path')}
    new_files = {row['local_path']: row for row in new.get('files', []) if row.get('local_path')}
    for local in sorted(carried):
        if local not in new_files and local not in base_files:
            raise ValueError(f'carried target not in staging: {local}')

    rows = []
    summary = {'same': 0, 'changed': 0, 'added': 0, 'removed': 0, 'carried': 0}
    for local in sorted(set(base_files) | set(new_files)):
        base_row = base_files.get(local)
        new_row = new_files.get(local)
        if new_row is None:
            summary['removed'] += 1
            rows.append({'local_path': local, 'status': 'removed',
                         'size_bytes': base_row.get('size_bytes'),
                         'sha12': (base_row.get('sha256') or '')[:12], 'mtime': None})
            continue
        size_bytes, sha12 = new_row.get('size_bytes'), (new_row.get('sha256') or '')[:12]
        mtime = source_mtime(new_row.get('source'))
        if local in carried or is_auto_carried(new_row.get('source', '')):
            summary['carried'] += 1
            rows.append({'local_path': local, 'status': 'carried', 'size_bytes': size_bytes,
                         'sha12': sha12, 'mtime': mtime, 'carried_from': base_manifest_sha256})
        elif base_row is None:
            summary['added'] += 1
            rows.append({'local_path': local, 'status': 'added', 'size_bytes': size_bytes,
                         'sha12': sha12, 'mtime': mtime})
        elif base_row.get('sha256') == new_row.get('sha256') and base_row.get('size_bytes') == new_row.get('size_bytes'):
            summary['same'] += 1
            rows.append({'local_path': local, 'status': 'same', 'size_bytes': size_bytes,
                         'sha12': sha12, 'mtime': mtime})
        else:
            summary['changed'] += 1
            rows.append({'local_path': local, 'status': 'changed', 'size_bytes': size_bytes,
                         'sha12': sha12, 'mtime': mtime})

    if summary['changed'] or summary['added'] or summary['removed']:
        exit_code = 3
    elif summary['carried']:
        exit_code = 4
    else:
        exit_code = 0
    return {'rows': rows, 'summary': summary, 'exit': exit_code}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entry', type=Path)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--compare-build', type=Path, default=None,
                         help='재동결 대조(K4): BUILD/design-input.json의 manifests[0]을 기준으로 삼는다')
    parser.add_argument('--compare-out', type=Path, default=None, help='refreeze-diff.json 출력 경로')
    parser.add_argument('--carried', action='append', default=[], metavar='LOCAL_PATH',
                         help='entrypoint 의존성 closure 밖 파일만 명시적으로 carried 처리')
    args = parser.parse_args()
    if bool(args.compare_build) != bool(args.compare_out):
        parser.error('--compare-build and --compare-out must be given together')
    if args.carried and not args.compare_build:
        parser.error('--carried requires --compare-build')
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
    if missing:
        return 1
    if not args.compare_build:
        return 0
    try:
        build = args.compare_build.resolve(strict=True)
        base_manifest_path = _reference_context(build)[1]
        base = json.loads(base_manifest_path.read_text(encoding='utf-8-sig'))
        result = compare_manifests(manifest, base, set(args.carried), build, args.out)
    except (OSError, ValueError) as error:
        print(f'[design-archive] compare failed: {error}', file=sys.stderr)
        return 1
    by_local = {row['local_path']: row for row in manifest['files']}
    for row in result['rows']:
        if row['status'] == 'carried' and row['local_path'] in by_local:
            by_local[row['local_path']]['carried_from'] = row['carried_from']
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    payload = {'version': 1, 'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'base_manifest_sha256': hashlib.sha256(base_manifest_path.read_bytes()).hexdigest(),
               'rows': result['rows'], 'summary': result['summary']}
    args.compare_out.parent.mkdir(parents=True, exist_ok=True)
    args.compare_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'[design-archive] compare: {result["summary"]}; exit={result["exit"]}', file=sys.stderr)
    return result['exit']


if __name__ == '__main__':
    sys.exit(main())
