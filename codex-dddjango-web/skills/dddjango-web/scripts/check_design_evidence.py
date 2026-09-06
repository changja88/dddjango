#!/usr/bin/env python3
"""Validate frozen design inputs and visual evidence using local bytes only.

Exit 0 means the declared phase is internally consistent, 1 means usage or an
internal error prevented the check, and 2 means a defect or missing evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

from asset_io import image_extension
from design_sources import dependencies, resource_kind
from freeze_design import resolve_source

EXCLUDED_DIRS = {'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
EXCLUDED_FILES = {'.DS_Store'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}


class Defects(Exception):
    def __init__(self, messages: list[str]):
        self.messages = messages


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def confined(root: Path, value: Any, label: str, issues: list[str]) -> Path | None:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        issues.append(f'{label}: nonempty relative path required')
        return None
    path = root / value
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        issues.append(f'{label}: missing path ({error})')
        return None
    if not resolved.is_relative_to(root.resolve()):
        issues.append(f'{label}: path escapes root')
        return None
    if not resolved.is_file():
        issues.append(f'{label}: regular file required')
        return None
    return resolved


def pointer(root: Path, value: Any, label: str, issues: list[str], *, image: bool = False) -> tuple[Path, bytes] | None:
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'}:
        issues.append(f'{label}: exact path/sha256 object required')
        return None
    path = confined(root, value.get('path'), f'{label}.path', issues)
    if path is None:
        return None
    data = path.read_bytes()
    if value.get('sha256') != sha(data):
        issues.append(f'{label}: sha256 mismatch')
    if image:
        try:
            image_extension(data)
        except ValueError as error:
            issues.append(f'{label}: invalid image ({error})')
    return path, data


def valid_viewport(value: Any) -> bool:
    return (isinstance(value, list) and len(value) == 2
            and all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in value))


def canonical_digest(items: list[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for name, data in sorted(items):
        encoded = name.encode('utf-8')
        digest.update(len(encoded).to_bytes(8, 'big'))
        digest.update(encoded)
        digest.update(len(data).to_bytes(8, 'big'))
        digest.update(data)
    return digest.hexdigest()


def json_pointer(document: Any, value: Any, label: str, issues: list[str]) -> Any:
    if not isinstance(value, str) or not value.startswith('/'):
        issues.append(f'{label}: JSON Pointer must start with /')
        return None
    current = document
    try:
        for raw in value[1:].split('/'):
            if re.search(r'~(?:[^01]|$)', raw):
                raise ValueError
            token = raw.replace('~1', '/').replace('~0', '~')
            current = current[int(token)] if isinstance(current, list) else current[token]
    except (KeyError, IndexError, TypeError, ValueError):
        issues.append(f'{label}: pointer does not resolve')
        return None
    return current


def check_media_requirements(value: Any, label: str, issues: list[str]) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        issues.append(f'{label}: list required')
        return []
    required = {'id', 'kind', 'environment', 'endpoint', 'identity_pointer', 'source_pointer'}
    rows = []
    ids = set()
    for index, row in enumerate(value):
        here = f'{label}[{index}]'
        if not isinstance(row, dict) or set(row) != required:
            issues.append(f'{here}: exact media requirement fields required')
            continue
        if not all(isinstance(row[key], str) and row[key] for key in required - {'kind'}):
            issues.append(f'{here}: nonempty string fields required')
        if row['kind'] not in ('image', 'video'):
            issues.append(f'{here}.kind: image or video required')
        if row['id'] in ids:
            issues.append(f'{here}.id: duplicate')
        ids.add(row['id'])
        rows.append(row)
    return rows


def _manifest_closure(root: Path, manifest: dict, rows: list[dict], label: str, issues: list[str]) -> None:
    aliases = {}
    for row in rows:
        aliases[row.get('source')] = row
        if row.get('requested_source'):
            aliases[row['requested_source']] = row
    source_root = Path(manifest['source_root']).resolve() if manifest.get('source_root') else None
    for row in rows:
        if row.get('status') != 'ok' or row.get('kind') not in ('html', 'css', 'script', 'component'):
            continue
        file_path = root / row['local_path']
        try:
            found = dependencies(file_path.read_text(encoding='utf-8-sig'), row['kind'])
        except (OSError, UnicodeError) as error:
            issues.append(f'{label}: cannot scan {row.get("local_path")} ({error})')
            continue
        for reference, _kind, base_kind in found:
            try:
                parent = row.get('source', '')
                if base_kind == 'document' and row['kind'] in ('script', 'component'):
                    parent = row.get('source_document') or parent
                resolved = resolve_source(reference, parent, source_root)
            except ValueError as error:
                issues.append(f'{label}: unsupported dependency {reference!r} in {row["local_path"]} ({error})')
                continue
            candidate = aliases.get(resolved)
            if not candidate or candidate.get('status') != 'ok':
                issues.append(f'{label}: dependency absent from manifest: {reference!r} in {row["local_path"]}')


def validate_inputs(build: Path, project: Path) -> tuple[dict, str, list[tuple[str, bytes]]]:
    issues: list[str] = []
    input_path = build / 'design-input.json'
    try:
        spec = load_json(input_path)
    except (OSError, ValueError) as error:
        raise Defects([f'design-input.json: unreadable ({error})'])
    required = {'version', 'reference_root', 'manifests', 'scope', 'coverage_review', 'cases'}
    allowed = required | {'host_files'}
    if not isinstance(spec, dict) or not required <= set(spec) or set(spec) - allowed:
        raise Defects(['design-input.json: invalid top-level fields'])
    if spec.get('version') != 1:
        issues.append('design-input.json.version: must be 1')
    reference_value = spec.get('reference_root')
    reference_root = build / reference_value if isinstance(reference_value, str) else build
    try:
        reference_root = reference_root.resolve(strict=True)
        if not reference_root.is_dir() or not reference_root.is_relative_to(build.resolve()):
            raise OSError('must be a directory inside build')
    except OSError as error:
        issues.append(f'reference_root: invalid ({error})')
        reference_root = build
    digest_items: list[tuple[str, bytes]] = [('design-input.json', input_path.read_bytes())]
    for name in ('scope', 'coverage_review'):
        item = pointer(build, spec.get(name), name, issues)
        if item:
            digest_items.append((f'evidence/{spec[name]["path"]}', item[1]))
    manifests = spec.get('manifests')
    if not isinstance(manifests, list) or not manifests:
        issues.append('manifests: nonempty list required')
        manifests = []
    elif not all(isinstance(value, str) for value in manifests) or len(set(manifests)) != len(manifests):
        issues.append('manifests: unique path strings required')
    manifest_records: list[tuple[Path, dict, list[dict]]] = []
    for index, value in enumerate(manifests):
        path = confined(build, value, f'manifests[{index}]', issues)
        if path is None:
            continue
        try:
            manifest = load_json(path)
        except ValueError as error:
            issues.append(f'manifests[{index}]: invalid JSON ({error})')
            continue
        digest_items.append((f'manifest/{value}', path.read_bytes()))
        if not isinstance(manifest, dict) or manifest.get('version') != 1 or manifest.get('source_ready') is not True:
            issues.append(f'manifests[{index}]: version=1 and source_ready=true required')
            continue
        rows = manifest.get('files')
        if not isinstance(rows, list) or not rows:
            issues.append(f'manifests[{index}].files: nonempty list required')
            continue
        locals_seen = set()
        for row_index, row in enumerate(rows):
            here = f'manifests[{index}].files[{row_index}]'
            required_row = {'source', 'source_document', 'local_path', 'kind', 'status', 'sha256', 'size_bytes', 'reason'}
            if not isinstance(row, dict) or not required_row <= set(row) or set(row) - required_row - {'requested_source'}:
                issues.append(f'{here}: invalid source-manifest row fields')
                continue
            if row.get('status') != 'ok':
                issues.append(f'{here}: successful row required')
                continue
            if not all(isinstance(row.get(key), str) for key in ('source', 'source_document', 'local_path', 'kind', 'sha256', 'reason')):
                issues.append(f'{here}: invalid source-manifest row types')
                continue
            if (not isinstance(row.get('size_bytes'), int) or isinstance(row.get('size_bytes'), bool)
                    or row['size_bytes'] < 1 or ('requested_source' in row and not isinstance(row['requested_source'], str))):
                issues.append(f'{here}: invalid source-manifest size/requested_source')
                continue
            inferred = resource_kind(row['source'], row['kind'])
            if inferred != row['kind']:
                issues.append(f'{here}.kind: contradicts source suffix')
            local = row.get('local_path')
            frozen = confined(reference_root, local, f'{here}.local_path', issues)
            if local in locals_seen:
                issues.append(f'{here}.local_path: duplicate')
            locals_seen.add(local)
            if frozen:
                data = frozen.read_bytes()
                if row.get('size_bytes') != len(data) or row.get('sha256') != sha(data):
                    issues.append(f'{here}: byte size/hash mismatch')
                digest_items.append((f'source/{local}', data))
        if manifest.get('entrypoint') not in locals_seen:
            issues.append(f'manifests[{index}].entrypoint: missing successful file row')
        _manifest_closure(reference_root, manifest, rows, f'manifests[{index}]', issues)
        manifest_records.append((path, manifest, rows))
    cases = spec.get('cases')
    if not isinstance(cases, list) or not cases:
        issues.append('cases: nonempty list required')
        cases = []
    ids = set()
    case_required = {'id', 'screen', 'state', 'viewport', 'scope_refs', 'entrypoint', 'reference_capture'}
    case_allowed = case_required | {'media'}
    all_entries = {(manifest.get('entrypoint', ''), row.get('sha256'))
                   for _, manifest, rows in manifest_records for row in rows
                   if row.get('status') == 'ok' and row.get('local_path') == manifest.get('entrypoint')}
    for index, case in enumerate(cases):
        here = f'cases[{index}]'
        if not isinstance(case, dict) or not case_required <= set(case) or set(case) - case_allowed:
            issues.append(f'{here}: invalid fields')
            continue
        for key in ('id', 'screen', 'state'):
            if not isinstance(case.get(key), str) or not case[key]:
                issues.append(f'{here}.{key}: nonempty string required')
        if case.get('id') in ids:
            issues.append(f'{here}.id: duplicate')
        ids.add(case.get('id'))
        if not valid_viewport(case.get('viewport')):
            issues.append(f'{here}.viewport: [positive width, positive height] required')
        if not isinstance(case.get('scope_refs'), list) or not case['scope_refs'] or not all(isinstance(x, str) and x for x in case['scope_refs']):
            issues.append(f'{here}.scope_refs: nonempty string list required')
        entry = case.get('entrypoint')
        if not isinstance(entry, dict) or set(entry) != {'path', 'sha256'} or (entry.get('path'), entry.get('sha256')) not in all_entries:
            issues.append(f'{here}.entrypoint: must match a successful manifest file')
        capture = pointer(build, case.get('reference_capture'), f'{here}.reference_capture', issues, image=True)
        if capture:
            digest_items.append((f'reference-capture/{case["reference_capture"]["path"]}', capture[1]))
        check_media_requirements(case.get('media'), f'{here}.media', issues)
    host_files = spec.get('host_files', [])
    if not isinstance(host_files, list) or not all(isinstance(item, str) and item for item in host_files):
        issues.append('host_files: string list required')
    elif len(set(host_files)) != len(host_files):
        issues.append('host_files: duplicates forbidden')
    else:
        for index, value in enumerate(host_files):
            path = confined(project, value, f'host_files[{index}]', issues)
            if path:
                digest_items.append((f'host/{value}', path.read_bytes()))
    if issues:
        raise Defects(issues)
    return spec, canonical_digest(digest_items), digest_items


def implementation_digest(project: Path, spec: dict) -> str:
    web = project / 'web'
    if not web.is_dir():
        raise Defects(['project-root/web: directory required'])
    items = []
    for path in web.rglob('*'):
        relative = path.relative_to(project)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_file() and path.name not in EXCLUDED_FILES and path.suffix not in EXCLUDED_SUFFIXES:
            resolved = path.resolve()
            if not resolved.is_relative_to(web.resolve()):
                raise Defects([f'web path escapes through symlink: {relative.as_posix()}'])
            items.append((relative.as_posix(), path.read_bytes()))
    for value in spec.get('host_files', []):
        path = (project / value).resolve(strict=True)
        items.append((f'host/{value}', path.read_bytes()))
    return canonical_digest(items)


def validate_visual(build: Path, project: Path, spec: dict, input_digest: str, impl_digest: str) -> None:
    issues: list[str] = []
    path = build / 'visual-evidence.json'
    try:
        evidence = load_json(path)
    except (OSError, ValueError) as error:
        raise Defects([f'visual-evidence.json: unreadable ({error})'])
    required = {'version', 'input_digest', 'implementation_digest', 'visual_check', 'cases'}
    if not isinstance(evidence, dict) or set(evidence) != required or evidence.get('version') != 1:
        raise Defects(['visual-evidence.json: exact version 1 schema required'])
    if evidence.get('input_digest') != input_digest:
        issues.append('input_digest: stale or incorrect')
    if evidence.get('implementation_digest') != impl_digest:
        issues.append('implementation_digest: stale or incorrect')
    pointer(build, evidence.get('visual_check'), 'visual_check', issues)
    expected = {case['id']: case for case in spec['cases']}
    rows = evidence.get('cases')
    if not isinstance(rows, list):
        issues.append('visual cases: list required')
        rows = []
    actual_ids = [row.get('id') for row in rows if isinstance(row, dict)]
    if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != set(expected):
        issues.append('visual cases: exact unique design case set required')
    for index, row in enumerate(rows):
        here = f'visual cases[{index}]'
        required_case = {'id', 'url', 'viewport', 'capture', 'result'}
        allowed_case = required_case | {'media'}
        if not isinstance(row, dict) or not required_case <= set(row) or set(row) - allowed_case:
            issues.append(f'{here}: invalid fields')
            continue
        source = expected.get(row['id'])
        if source is None:
            continue
        if not isinstance(row.get('url'), str) or not row['url']:
            issues.append(f'{here}.url: nonempty string required')
        if row.get('viewport') != source['viewport']:
            issues.append(f'{here}.viewport: does not match input')
        captured = pointer(build, row.get('capture'), f'{here}.capture', issues, image=True)
        original = confined(build, source['reference_capture']['path'], f'{here}.original', issues)
        if captured and original:
            try:
                if captured[0].samefile(original):
                    issues.append(f'{here}.capture: original file/hardlink reuse forbidden')
            except OSError as error:
                issues.append(f'{here}.capture: identity check failed ({error})')
        if row.get('result') != 'pass':
            issues.append(f'{here}.result: pass required')
        _validate_media(build, source.get('media', []), row.get('media'), here, issues)
    if issues:
        raise Defects(issues)


def _validate_media(build: Path, requirements: list[dict], observations: Any, label: str, issues: list[str]) -> None:
    if observations is None:
        observations = []
    if not isinstance(observations, list):
        issues.append(f'{label}.media: list required')
        return
    expected = {row['id']: row for row in requirements}
    ids = [row.get('requirement_id') for row in observations if isinstance(row, dict)]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        issues.append(f'{label}.media: exact unique requirement set required')
    for index, row in enumerate(observations):
        here = f'{label}.media[{index}]'
        if not isinstance(row, dict) or set(row) != {'requirement_id', 'response', 'browser'}:
            issues.append(f'{here}: exact fields required')
            continue
        requirement = expected.get(row['requirement_id'])
        if not requirement:
            continue
        response_item = pointer(build, row['response'], f'{here}.response', issues)
        browser_item = pointer(build, row['browser'], f'{here}.browser', issues)
        if not response_item or not browser_item:
            continue
        try:
            response = json.loads(response_item[1])
            browser = json.loads(browser_item[1])
        except (ValueError, UnicodeError) as error:
            issues.append(f'{here}: invalid observation JSON ({error})')
            continue
        response_fields = {'observed_at', 'environment', 'endpoint', 'status', 'body'}
        browser_fields = {'observed_at', 'current_src', 'status', 'loaded'}
        if not isinstance(response, dict) or set(response) != response_fields:
            issues.append(f'{here}.response: exact observation fields required')
            continue
        required_browser = browser_fields | ({'playback_start', 'playback_end'} if requirement['kind'] == 'video' else set())
        if not isinstance(browser, dict) or set(browser) != required_browser:
            issues.append(f'{here}.browser: exact observation fields required')
            continue
        for owner, observed in (('response', response['observed_at']), ('browser', browser['observed_at'])):
            try:
                parsed = datetime.fromisoformat(observed.replace('Z', '+00:00'))
                if parsed.tzinfo is None:
                    raise ValueError
            except (AttributeError, ValueError):
                issues.append(f'{here}.{owner}.observed_at: timezone-aware ISO 8601 required')
        if response['environment'] != requirement['environment'] or response['endpoint'] != requirement['endpoint']:
            issues.append(f'{here}: environment/endpoint mismatch')
        if not isinstance(response['status'], int) or not 200 <= response['status'] < 300:
            issues.append(f'{here}.response.status: 2xx required')
        if not isinstance(browser['status'], int) or not 200 <= browser['status'] < 300 or browser['loaded'] is not True:
            issues.append(f'{here}.browser: 2xx and loaded=true required')
        identity = json_pointer(response['body'], requirement['identity_pointer'], f'{here}.identity_pointer', issues)
        source = json_pointer(response['body'], requirement['source_pointer'], f'{here}.source_pointer', issues)
        if (not isinstance(identity, (str, int, float)) or isinstance(identity, bool)
                or identity == '' or isinstance(identity, float) and not math.isfinite(identity)):
            issues.append(f'{here}: nonempty asset identity required')
        if not isinstance(source, str) or not source or source != browser['current_src']:
            issues.append(f'{here}: response source/current_src mismatch')
        if requirement['kind'] == 'video':
            start, end = browser.get('playback_start'), browser.get('playback_end')
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (start, end)) or end <= start:
                issues.append(f'{here}: finite increasing video playback required')


def run(args: argparse.Namespace) -> dict[str, str]:
    build = args.build.resolve()
    project = args.project_root.resolve()
    if not build.is_dir() or not project.is_dir():
        raise ValueError('--build and --project-root must be directories')
    spec, input_value, _items = validate_inputs(build, project)
    result = {'input_digest': input_value}
    if args.phase == 'visual' or args.fingerprint:
        result['implementation_digest'] = implementation_digest(project, spec)
    if not args.fingerprint and args.phase == 'visual':
        validate_visual(build, project, spec, input_value, result['implementation_digest'])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--phase', required=True, choices=('inputs', 'visual'))
    parser.add_argument('--fingerprint', action='store_true')
    try:
        args = parser.parse_args(argv)
        result = run(args)
    except Defects as error:
        for message in error.messages:
            print(f'[design-evidence] defect: {message}', file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f'[design-evidence] usage/error: {error}', file=sys.stderr)
        return 1
    except Exception as error:
        print(f'[design-evidence] internal error: {type(error).__name__}: {error}', file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
