#!/usr/bin/env python3
"""Freeze a source document and its statically referenced files without rewriting bytes.

Usage: freeze_design.py <local file|http(s) URL> --out <design-ref>
       [--source-root <local allowed root>] [--manifest <source-manifest.json>]
Local default root is the entry file's parent; ../ escapes require an explicit
broader --source-root. Existing matching files are verified, conflicting files
are retained with a failed entry. Running on a manually collected design-ref is
supported. Exit 0 means all statically discovered files were acquired, not that
the source can render: JSX/dynamic resources and remote absolute references still
require the original rendering environment and browser evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import urllib.parse

from asset_io import digest_fields, read_resource, validate_payload, write_verified
from design_sources import dependencies, resource_kind

MAX_FILES = 256


def resolve_source(reference: str, parent: str, local_root: Path | None) -> str:
    if '{' in reference or '}' in reference:
        raise ValueError('dynamic reference requires source rendering or explicit acquisition')
    if reference.startswith('data:'):
        return reference
    if parent.startswith(('http://', 'https://')):
        resolved = urllib.parse.urljoin(parent, reference)
        if not resolved.startswith(('http://', 'https://')):
            raise ValueError('unsupported dependency scheme')
        return urllib.parse.urldefrag(resolved)[0]
    if reference.startswith(('http://', 'https://')):
        return urllib.parse.urldefrag(reference)[0]
    parsed = urllib.parse.urlsplit(reference)
    if parsed.scheme not in ('', 'file') or parsed.netloc:
        raise ValueError('unsupported local dependency scheme')
    path = Path(urllib.parse.unquote(parsed.path))
    if not path.is_absolute():
        path = Path(parent).parent / path
    path = path.resolve()
    if local_root is None or not path.is_relative_to(local_root):
        raise ValueError('source escapes --source-root')
    return str(path)


def target_path(source: str, local_root: Path | None) -> Path:
    if source.startswith('data:'):
        return Path('_inline') / hashlib.sha256(source.encode()).hexdigest()
    if source.startswith(('http://', 'https://')):
        parsed = urllib.parse.urlsplit(source)
        # Schemes/ports are part of origin; URL query variants must never overwrite.
        host = re.sub(r'[^A-Za-z0-9._-]', '_', parsed.netloc)
        parts = [urllib.parse.unquote(part) for part in parsed.path.split('/') if part]
        if any(part in ('.', '..') or '/' in part or '\\' in part for part in parts):
            raise ValueError('unsafe URL path')
        path = Path('_remote') / parsed.scheme / host / Path(*parts or ['index.html'])
        if parsed.query:
            path = path.with_name(path.stem + '_' + hashlib.sha256(parsed.query.encode()).hexdigest()[:12] + path.suffix)
        return path
    assert local_root is not None
    return Path(source).relative_to(local_root)


def freeze(source: str, out: Path, local_root: Path | None) -> dict:
    manifest = {'version': 1, 'entrypoint': '', 'source_root': str(local_root) if local_root else None, 'source_ready': False, 'files': []}
    pending = [(source, resource_kind(source, 'html'), '', source)]
    seen = set()
    while pending:
        current, kind, parent, document_origin = pending.pop(0)
        if current in seen:
            continue
        seen.add(current)
        entry = {'source': current, 'source_document': parent, 'local_path': '', 'kind': kind,
                 'status': 'failed', 'sha256': '', 'size_bytes': 0, 'reason': ''}
        manifest['files'].append(entry)
        if len(seen) > MAX_FILES:
            entry['reason'] = 'dependency limit exceeded (256); split the source explicitly'
            break
        try:
            resolved = resolve_source(current, parent, local_root) if parent else current
            if resolved != current and resolved in seen:
                manifest['files'].pop()
                continue
            seen.add(resolved)
            entry['source'] = resolved
            metadata = {}
            data, _mime = read_resource(resolved, str(local_root) if not resolved.startswith(('http://', 'https://', 'data:')) else None, metadata)
            if metadata.get('final_url') and metadata['final_url'] != resolved:
                entry['requested_source'] = resolved
                resolved = metadata['final_url']
                entry['source'] = resolved
                seen.add(resolved)
                if kind == 'html':
                    document_origin = resolved
            relative = target_path(resolved, local_root)
            if relative.as_posix() == 'source-manifest.json':
                raise ValueError('source conflicts with reserved manifest filename')
            destination = out / relative
            if not destination.resolve().is_relative_to(out.resolve()):
                raise ValueError('destination escapes output root')
            validate_payload(data, kind, _mime)
            write_verified(destination, data)
            entry.update(local_path=relative.as_posix(), status='ok', **digest_fields(data))
            if not parent:
                manifest['entrypoint'] = relative.as_posix()
            if kind in ('html', 'css', 'script', 'component'):
                for reference, dep_kind, base_kind in dependencies(data.decode('utf-8-sig'), kind):
                    try:
                        base_source = document_origin if kind in ('component', 'script') and base_kind == 'document' else resolved
                        child = resolve_source(reference, base_source, local_root)
                    except ValueError as error:
                        manifest['files'].append({'source': reference, 'source_document': resolved, 'local_path': '', 'kind': dep_kind,
                                                  'status': 'failed', 'sha256': '', 'size_bytes': 0, 'reason': str(error)})
                        continue
                    pending.append((child, dep_kind, resolved, child if dep_kind == 'html' else document_origin))
        except Exception as error:  # File, HTTP and format failures remain inspectable and retryable.
            entry['reason'] = f'{type(error).__name__}: {error}'
            print(f"[freeze-design] failed: {current}: {entry['reason']}", file=sys.stderr)
    manifest['source_ready'] = bool(manifest['entrypoint']) and all(row['status'] == 'ok' for row in manifest['files'])
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    remote = args.source.startswith(('http://', 'https://'))
    source = args.source if remote else str(Path(args.source).resolve())
    local_root = None if remote else (args.source_root or Path(source).parent).resolve()
    if local_root is not None and not Path(source).is_relative_to(local_root):
        parser.error('entry source escapes --source-root')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest or out / 'source-manifest.json'
    if manifest_path.is_symlink() or not manifest_path.resolve().is_relative_to(out.parent):
        parser.error('--manifest must be a regular file inside --out or its parent')
    manifest = freeze(source, out, local_root)
    if any((out / row['local_path']).resolve() == manifest_path.resolve() for row in manifest['files'] if row['local_path']):
        parser.error('--manifest conflicts with an acquired source file')
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"[freeze-design] {len(manifest['files'])} files; source_ready={manifest['source_ready']} → {manifest_path}")
    return 0 if manifest['source_ready'] else 1


if __name__ == '__main__':
    sys.exit(main())
