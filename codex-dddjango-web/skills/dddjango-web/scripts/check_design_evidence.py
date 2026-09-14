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
import posixpath
import re
import sys
from typing import Any
import unicodedata
from urllib.parse import unquote, urlsplit

from asset_io import image_extension
from archive_design import archive_dependencies, archive_files
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
            if isinstance(current, list):
                if not re.fullmatch(r'(?:0|[1-9][0-9]*)', token):
                    raise ValueError
                current = current[int(token)]
            else:
                current = current[token]
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


def _document_origin(row: dict, aliases: dict, entrypoint: str) -> str:
    """Recover the nearest HTML base after validating the full importer chain."""
    seen = set()
    nearest_html = None
    while True:
        source, parent = row.get('source'), row.get('source_document')
        if (row.get('status') != 'ok' or not isinstance(source, str) or not source
                or not isinstance(parent, str)):
            raise ValueError('invalid document provenance row')
        if source in seen:
            raise ValueError('cyclic document provenance')
        seen.add(source)
        if row.get('kind') == 'html' and nearest_html is None:
            nearest_html = source
        if not parent:
            if row.get('local_path') == entrypoint:
                return nearest_html or source
            raise ValueError('document provenance ends before manifest entrypoint')
        row = aliases.get(parent)
        if row is None:
            raise ValueError('document provenance importer absent from manifest')


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
                    parent = _document_origin(row, aliases, manifest.get('entrypoint', ''))
                resolved = resolve_source(reference, parent, source_root)
            except ValueError as error:
                issues.append(f'{label}: unsupported dependency {reference!r} in {row["local_path"]} ({error})')
                continue
            candidate = aliases.get(resolved)
            if not candidate or candidate.get('status') != 'ok':
                issues.append(f'{label}: dependency absent from manifest: {reference!r} in {row["local_path"]}')


def review_digest(spec: dict, items: list[tuple[str, bytes]]) -> str:
    """Bind the independent review without including that review in its own hash."""
    source_spec = {key: value for key, value in spec.items() if key != 'coverage_review'}
    review_path = spec.get('coverage_review') or {}
    excluded = {'design-input.json', f'evidence/{review_path.get("path", "") }'}
    return canonical_digest([('review-input', json.dumps(source_spec, sort_keys=True, ensure_ascii=False).encode())]
                            + [(name, data) for name, data in items if name not in excluded])


# ---------------------------------------------------------------------------
# K3 상호작용 증거(interactions.json) — 수집기 신뢰 경계·동결 연결·잔여
#
# 잔여 계산은 스니펫(assets/interaction_audit.js)의 pure.residual을 그대로 옮긴 것이다
# (K1 «한 표·두 구현»). 규칙을 고칠 일이 생기면 JS 정본을 먼저 고치고 이 포트를 맞춘다.
# ---------------------------------------------------------------------------

INTERACTION_FIELDS = {'version', 'collector', 'archive_sha256', 'entrypoint', 'url', 'browser_viewport',
                      'content_crop', 'root', 'outside_root', 'excluded_regions', 'served', 'declared',
                      'declared_unmatched', 'observed_at', 'targets', 'initial', 'steps',
                      'discovery_limits', 'partial', 'caps_hit', 'environment_error'}
COLLECTOR_FIELDS = {'name', 'snippet_sha256', 'driver', 'driver_sha256', 'path', 'capabilities'}
TARGET_FIELDS = {'role', 'name', 'input_type', 'owner', 'owner_items_hash', 'dom_path', 'kind',
                 'first_seen_step', 'declared', 'found_by', 'live'}
ENTRY_FIELDS = {'id', 'enabled', 'checked', 'face', 'value_empty', 'surface', 'occluded', 'live'}
STEP_FIELDS = {'n', 'path', 'target', 'action', 'option', 'value', 'context', 'status', 'error',
               'before', 'after', 'changes', 'navigated', 'discovery'}
EXCLUSION_UNIT_FIELDS = {'target', 'action', 'option', 'scope_ref', 'approval_quote'}
EXCLUSION_SURFACE_FIELDS = {'surface', 'scope_ref', 'approval_quote'}
KINDS = {'button', 'link', 'menuitem', 'option', 'tab', 'radio', 'checkbox', 'switch', 'input',
         'textarea', 'select', 'trigger', 'overlay', 'handler', 'declared'}
CHANNELS = {'semantic', 'react_props', 'onclick', 'cdp_listener', 'cursor', 'structure', 'declared'}
STATUSES = {'executed', 'failed', 'unreachable', 'unclickable'}
CAPS = {'max_steps', 'max_minutes', 'max_depth'}
# radio는 CLICK_ONLY다(TOGGLE이 아니다): 선택 뒤 같은 그룹 안에서 되돌릴 수 없어 «관찰된
# before 상태마다 click 1회»가 성립하지 않는다 — 스니펫 주석과 같은 규칙.
CLICK_ONLY_KINDS = {'button', 'link', 'menuitem', 'tab', 'radio', 'handler', 'declared', 'trigger'}
TOGGLE_KINDS = {'checkbox', 'switch'}
TEXT_KINDS = {'input', 'textarea'}
COLLECTOR_ASSETS = {'snippet_sha256': 'interaction_audit.js', 'driver_sha256': 'observe_interactions.pw.js'}


def _collapse(text: str) -> str:
    """NFC·공백 정규화 — 스니펫 collapseText와 같은 규칙(승인 원문 대조용)."""
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text).replace('\u00a0', ' ')).strip()


def _slug(title: str) -> str:
    text = _collapse(title).lower()
    return re.sub(r'\s', '-', re.sub(r'[^\w\s-]', '', text))


def _anchors(text: str) -> set[str]:
    found = set()
    for line in text.splitlines():
        heading = re.match(r'^#{1,6}\s+(.*?)\s*$', line)
        if not heading:
            continue
        title = heading.group(1)
        explicit = re.search(r'\{#([^}\s]+)\}\s*$', title)
        if explicit:
            found.add(explicit.group(1))
            title = title[:explicit.start()]
        found.add(_slug(title))
    found.update(match.group(1) for match in re.finditer(r'<a\s+(?:id|name)="([^"]+)"', text))
    return found


def _unit_key(target: Any, action: Any, option: Any) -> str:
    """스니펫 unitKey와 같은 문자열 — 중복 제거·정렬 기준이 두 구현에서 같아야 한다."""
    return json.dumps([target, action, option], ensure_ascii=False, separators=(',', ':'))


def _unit_order(key: str) -> bytes:
    """JS Array.prototype.sort의 UTF-16 코드 단위 순서."""
    return key.encode('utf-16-be', 'surrogatepass')


def _is_active(entry: Any) -> bool:
    return isinstance(entry, dict) and bool(entry.get('enabled')) and not entry.get('occluded')


def _observed_state(entry: dict) -> Any:
    for key in ('checked', 'surface', 'face'):
        if entry.get(key) is not None:
            return entry[key]
    return None


def _inventories(document: dict) -> list[list]:
    found = []
    initial = document.get('initial')
    if isinstance(initial, dict) and isinstance(initial.get('inventory'), list):
        found.append(initial['inventory'])
    for step in document.get('steps') or []:
        if not isinstance(step, dict):
            continue
        for side in ('before', 'after'):
            block = step.get(side)
            if isinstance(block, dict) and isinstance(block.get('inventory'), list):
                found.append(block['inventory'])
    return found


def _has_target_descendant(target: dict, targets: dict) -> bool:
    """dom_path가 자기 경로의 진부분 접두인 다른 대상이 있는가 — 스니펫 hasTargetDescendant."""
    path = target.get('dom_path')
    if not isinstance(path, str) or path == '':
        return False
    prefix = path + '/'
    return any(other is not target and isinstance(other, dict)
               and isinstance(other.get('dom_path'), str) and other['dom_path'].startswith(prefix)
               for other in targets.values())


def _is_named_handler(target: dict, targets: dict) -> bool:
    """토글형 = checkbox·switch·radio + 이름이 있고 대상 후손이 없는 handler(K1 D-H).

    이름이 빈 handler는 D-A로 이미 컨테이너이고, aria-label을 단 컨테이너는 이름이 남으므로
    후손까지 본다 — 스니펫 isNamedHandler와 같은 규칙(두 구현 동일성).
    """
    name = target.get('name')
    return (target.get('kind') == 'handler' and isinstance(name, str) and name != ''
            and not _has_target_descendant(target, targets))


def _toggle_units(states: list) -> list[tuple[str, Any]]:
    """관찰된 상태마다 click 1단위 — 중복은 첫 관찰 순서로 접는다(스니펫 dedupeBy)."""
    seen, units = set(), []
    for state in states:
        key = json.dumps(state, ensure_ascii=False, separators=(',', ':'))
        if key not in seen:
            seen.add(key)
            units.append(('click', state))
    return units


def _required_units(target: dict, states: list, targets: dict) -> list[tuple[str, Any]]:
    """스니펫 requiredActions의 포트 — K1 필요 조작 표 + K2 토글·select·오버레이 규칙."""
    kind = target.get('kind')
    if _is_named_handler(target, targets):  # D-H — CLICK_ONLY보다 먼저 본다(스니펫과 같은 순서)
        return _toggle_units(states)
    if kind in CLICK_ONLY_KINDS:
        return [('click', None)]
    if kind == 'option':
        owner = targets.get(target.get('owner'))
        if isinstance(owner, dict) and owner.get('kind') == 'select':
            value = target.get('value')
            return [('select', value if value is not None else None)]
        return [('click', None)]
    if kind in TOGGLE_KINDS:
        return _toggle_units(states)
    if kind in TEXT_KINDS:
        return [('focus', None), ('fill', None), ('blur', None)]
    if kind == 'select':
        return []
    if kind == 'overlay':
        if target.get('scrim') is True:
            return [('click', None), ('key', 'Escape')]
        return [('click', 'outside'), ('key', 'Escape')]
    return []


def interaction_residual(document: dict) -> list[tuple[str, str, Any]]:
    """어느 상태에서든 활성으로 관찰된 (identity, action, option) 중 executed 없는 것(K1)."""
    targets = document.get('targets') or {}
    observed: dict[str, list] = {}
    for inventory in _inventories(document):
        for entry in inventory:
            if not _is_active(entry) or not isinstance(entry.get('id'), str):
                continue
            observed.setdefault(entry['id'], []).append(_observed_state(entry))
    required: dict[str, tuple[str, str, Any]] = {}

    def add(target_id: str, action: str, option: Any) -> None:
        required[_unit_key(target_id, action, option)] = (target_id, action, option)

    for target_id, states in observed.items():
        target = targets.get(target_id)
        if not isinstance(target, dict):
            continue
        for action, option in _required_units(target, states, targets):
            add(target_id, action, option)
    for target_id, target in targets.items():  # 네이티브 select 옵션은 관측과 무관하게 요구된다
        if not isinstance(target, dict) or target.get('kind') != 'option':
            continue
        owner = targets.get(target.get('owner'))
        if not isinstance(owner, dict) or owner.get('kind') != 'select':
            continue
        for action, option in _required_units(target, [], targets):
            add(target_id, action, option)
    for step in document.get('steps') or []:
        if not isinstance(step, dict) or step.get('status') != 'executed':
            continue  # failed·unreachable·unclickable은 세지 않는다(K1)
        option = step.get('option')
        required.pop(_unit_key(step.get('target'), step.get('action'), option if option is not None else None), None)
    return [required[key] for key in sorted(required, key=_unit_order)]


def linked_surfaces(document: dict) -> set[str]:
    """changes.added ≠ ∅ step이 만든 표면 키(K3 동결 연결)."""
    found = set()
    for step in document.get('steps') or []:
        if not isinstance(step, dict):
            continue
        changes = step.get('changes')
        added = changes.get('added') if isinstance(changes, dict) else None
        after = step.get('after')
        if isinstance(added, list) and added and isinstance(after, dict) and after.get('surface_key') is not None:
            found.add(after['surface_key'])
    return found


def collector_assets_ok(document: dict, assets_dir: Path) -> bool:
    """수집기 바이트가 이 플러그인의 assets/와 같은가(K3 신뢰 경계)."""
    collector = document.get('collector')
    if not isinstance(collector, dict):
        return False
    for field, name in COLLECTOR_ASSETS.items():
        try:
            if collector.get(field) != sha((assets_dir / name).read_bytes()):
                return False
        except OSError:
            return False
    return True


def _exact(value: Any, required: set, optional: set, label: str, issues: list[str]) -> bool:
    if not isinstance(value, dict):
        issues.append(f'{label}: object with exact fields required')
        return False
    missing, unknown = sorted(required - set(value)), sorted(set(value) - required - optional)
    if missing or unknown:
        issues.append(f'{label}: exact fields required (missing={missing} · unknown={unknown})')
        return False
    return True


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _is_int(value: Any, minimum: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _check_targets(document: dict, label: str, issues: list[str]) -> dict:
    targets = document.get('targets')
    if not isinstance(targets, dict):
        issues.append(f'{label}.targets: object required')
        return {}
    for target_id, row in targets.items():
        here = f'{label}.targets[{target_id!r}]'
        kind = row.get('kind') if isinstance(row, dict) else None
        # 선택 필드는 둘뿐이다 — native select 옵션의 value, overlay의 scrim(K7).
        optional = {'value'} if _native_option(targets, target_id) else set()
        if kind == 'overlay':
            optional = optional | {'scrim'}
        if not _exact(row, TARGET_FIELDS, optional, here, issues):
            continue
        if kind not in KINDS:
            issues.append(f'{here}.kind: {sorted(KINDS)} 중 하나여야 한다 ({kind!r})')
        # owner는 조상 owner 요소의 identity다 — 그 조상이 스스로 대상이 아닐 수 있어
        # targets 안에 있으라고 요구하지 않는다(A8 실측 4건).
        if not all(isinstance(row[key], str) for key in
                   ('role', 'name', 'input_type', 'owner', 'owner_items_hash', 'dom_path')):
            issues.append(f'{here}: string identity fields required')
        if not _is_int(row['first_seen_step'], 0):
            issues.append(f'{here}.first_seen_step: non-negative integer required')
        if not isinstance(row['declared'], bool) or not isinstance(row['live'], bool):
            issues.append(f'{here}: declared/live booleans required')
        if (not _strings(row['found_by']) or not row['found_by']
                or set(row['found_by']) - CHANNELS or len(set(row['found_by'])) != len(row['found_by'])):
            issues.append(f'{here}.found_by: unique discovery channels required ({row["found_by"]!r})')
        if 'value' in row and not isinstance(row['value'], str):
            issues.append(f'{here}.value: option value string required')
        if 'scrim' in row and not isinstance(row['scrim'], bool):
            issues.append(f'{here}.scrim: boolean required')
    return targets


def _check_inventory(inventory: Any, targets: dict, label: str, issues: list[str]) -> None:
    if not isinstance(inventory, list):
        issues.append(f'{label}: inventory list required')
        return
    seen = set()
    for index, row in enumerate(inventory):
        here = f'{label}[{index}]'
        if not _exact(row, ENTRY_FIELDS, set(), here, issues):
            continue
        if not isinstance(row['id'], str) or row['id'] not in targets:
            issues.append(f'{here}.id: unknown target ({row["id"]!r})')
        elif row['id'] in seen:
            issues.append(f'{here}.id: duplicate ({row["id"]!r})')
        seen.add(row['id'] if isinstance(row['id'], str) else None)
        if not all(isinstance(row[key], bool) for key in ('enabled', 'occluded', 'live')):
            issues.append(f'{here}: enabled/occluded/live booleans required')
        # checked는 true|false|"mixed"|null — 스니펫 checkedOf가 aria-checked="mixed"(3상태
        # 체크박스)를 'mixed'로 내고, 잔여는 그 값을 하나의 관찰 상태로 센다(두 구현 동일성).
        if row['checked'] is not None and not isinstance(row['checked'], bool) and row['checked'] != 'mixed':
            issues.append(f'{here}.checked: boolean, "mixed" or null required')
        if row['value_empty'] is not None and not isinstance(row['value_empty'], bool):
            issues.append(f'{here}.value_empty: boolean or null required')
        for key in ('face', 'surface'):
            if row[key] is not None and not isinstance(row[key], str):
                issues.append(f'{here}.{key}: string or null required')


def _capture_item(build: Path, value: Any, label: str, issues: list[str],
                  items: list[tuple[str, bytes]]) -> None:
    item = pointer(build, value, label, issues, image=True)
    if item is None:
        return
    name = f'interaction-capture/{value["path"]}'
    if all(existing != name for existing, _data in items):
        items.append((name, item[1]))


def _check_steps(build: Path, document: dict, targets: dict, label: str, issues: list[str],
                 items: list[tuple[str, bytes]]) -> None:
    steps = document.get('steps')
    if not isinstance(steps, list):
        issues.append(f'{label}.steps: list required')
        return
    numbers = set()
    for index, step in enumerate(steps):
        here = f'{label}.steps[{index}]'
        if not _exact(step, STEP_FIELDS, set(), here, issues):
            continue
        if not _is_int(step['n'], 1):
            issues.append(f'{here}.n: positive integer required')
        elif step['n'] in numbers:
            issues.append(f'{here}.n: duplicate step number ({step["n"]})')
        numbers.add(step['n'] if _is_int(step['n'], 1) else None)
        status, target_id = step['status'], step['target']
        if status not in STATUSES:
            issues.append(f'{here}.status: {sorted(STATUSES)} 중 하나여야 한다 ({status!r})')
        if not isinstance(target_id, str) or target_id not in targets:
            issues.append(f'{here}.target: unknown target ({target_id!r})')
        route = step['path']
        if (not _strings(route) or not route or route[-1] != target_id
                or any(node not in targets for node in route)):
            issues.append(f'{here}.path: 알려진 대상 열이어야 하고 마지막이 target이어야 한다 ({route!r})')
        if not isinstance(step['action'], str) or not step['action']:
            issues.append(f'{here}.action: nonempty string required')
        if not isinstance(step['context'], str) or not step['context']:
            issues.append(f'{here}.context: nonempty string required')
        if step['option'] is not None and not isinstance(step['option'], (str, bool)):
            issues.append(f'{here}.option: string, boolean or null required')
        if step['value'] is not None and not isinstance(step['value'], str):
            issues.append(f'{here}.value: string or null required')
        if not isinstance(step['discovery'], bool):
            issues.append(f'{here}.discovery: boolean required')
        if status == 'executed' and step['error'] is not None:
            issues.append(f'{here}.error: executed step은 error가 null이어야 한다 ({step["error"]!r})')
        if status != 'executed' and step['error'] is not None and not isinstance(step['error'], str):
            issues.append(f'{here}.error: string or null required')
        if step['navigated'] is not None and (not isinstance(step['navigated'], str) or not step['navigated']):
            issues.append(f'{here}.navigated: URL string or null required')
        before = step['before']
        if _exact(before, {'inventory', 'state_hash'}, set(), f'{here}.before', issues):
            _check_inventory(before['inventory'], targets, f'{here}.before.inventory', issues)
            if before['state_hash'] is not None and not isinstance(before['state_hash'], str):
                issues.append(f'{here}.before.state_hash: string or null required')
            if status == 'executed' and not isinstance(before['state_hash'], str):
                issues.append(f'{here}.before.state_hash: executed step은 재생 종점 해시가 필요하다')
            if status == 'executed' and isinstance(target_id, str) and isinstance(before['inventory'], list):
                entry = next((row for row in before['inventory']
                              if isinstance(row, dict) and row.get('id') == target_id), None)
                # 네이티브 select 옵션은 서브트리 인벤토리에 없을 수 있다(잔여 규칙의 같은 예외).
                native = entry is None and _native_option(targets, target_id)
                if not native and not _is_active(entry):
                    issues.append(f'{here}: 비활성·가림 대상({target_id!r})은 executed일 수 없다')
        added = _check_changes(step['changes'], targets, here, issues)
        after = step['after']
        if status != 'executed' or step['navigated'] is not None:
            if after is not None:
                issues.append(f'{here}.after: 실행되지 않았거나 이탈(navigated)한 step은 after가 null이다')
            continue
        if not _exact(after, {'inventory', 'state_hash', 'surface_key'}, {'capture'}, f'{here}.after', issues):
            continue
        _check_inventory(after['inventory'], targets, f'{here}.after.inventory', issues)
        if not isinstance(after['state_hash'], str) or not isinstance(after['surface_key'], str):
            issues.append(f'{here}.after: state_hash/surface_key strings required')
        if added and 'capture' not in after:
            issues.append(f'{here}.after.capture: 새 표면(changes.added ≠ ∅)은 루트 크롭 PNG가 필요하다')
        if not added and 'capture' in after:
            issues.append(f'{here}.after.capture: added가 빈 step은 PNG를 남기지 않는다(K3)')
        if 'capture' in after:
            _capture_item(build, after['capture'], f'{here}.after.capture', issues, items)


def _native_option(targets: dict, target_id: str) -> bool:
    target = targets.get(target_id)
    if not isinstance(target, dict) or target.get('kind') != 'option':
        return False
    owner = targets.get(target.get('owner'))
    return isinstance(owner, dict) and owner.get('kind') == 'select'


def _check_changes(changes: Any, targets: dict, label: str, issues: list[str]) -> bool:
    if not _exact(changes, {'added', 'removed', 'values'}, set(), f'{label}.changes', issues):
        return False
    for key in ('added', 'removed'):
        if not _strings(changes[key]) or any(item not in targets for item in changes[key]):
            issues.append(f'{label}.changes.{key}: 알려진 대상 목록이어야 한다 ({changes[key]!r})')
    rows = changes['values']
    if not isinstance(rows, list):
        issues.append(f'{label}.changes.values: list required')
        return bool(changes['added']) if isinstance(changes['added'], list) else False
    for index, row in enumerate(rows):
        here = f'{label}.changes.values[{index}]'
        if not _exact(row, {'target', 'before', 'after'}, set(), here, issues):
            continue
        if row['target'] not in targets:
            issues.append(f'{here}.target: unknown target ({row["target"]!r})')
        if not isinstance(row['before'], str) or not isinstance(row['after'], str):
            issues.append(f'{here}: before/after value strings required')
    return bool(changes['added']) if isinstance(changes['added'], list) else False


def _check_document(document: dict, label: str, issues: list[str]) -> dict | None:
    """K7 블록의 필드 집합을 중첩 객체까지 재귀로 고정한다(exact-field)."""
    if not _exact(document, INTERACTION_FIELDS, set(), label, issues):
        return None
    if document['version'] != 1:
        issues.append(f'{label}.version: must be 1')
    collector = document['collector']
    if _exact(collector, COLLECTOR_FIELDS, set(), f'{label}.collector', issues):
        if collector['name'] != 'interaction_audit' or collector['driver'] != 'observe_interactions.pw.js':
            issues.append(f'{label}.collector: this plugin의 수집기 이름이어야 한다')
        if collector['path'] not in ('node', 'mcp'):
            issues.append(f'{label}.collector.path: node or mcp required')
        if not _is_sha(collector['snippet_sha256']) or not _is_sha(collector['driver_sha256']):
            issues.append(f'{label}.collector: sha256 hex digests required')
        if _exact(collector['capabilities'], {'react_props', 'cdp_listeners'}, set(),
                  f'{label}.collector.capabilities', issues):
            if not all(isinstance(value, bool) for value in collector['capabilities'].values()):
                issues.append(f'{label}.collector.capabilities: booleans required')
    if not _is_sha(document['archive_sha256']):
        issues.append(f'{label}.archive_sha256: sha256 hex digest required')
    _exact(document['entrypoint'], {'path', 'sha256'}, set(), f'{label}.entrypoint', issues)
    if not valid_viewport(document['browser_viewport']):
        issues.append(f'{label}.browser_viewport: [positive width, positive height] required')
    crop = document['content_crop']
    if _exact(crop, {'x', 'y', 'w', 'h'}, set(), f'{label}.content_crop', issues):
        if not all(_is_int(crop[key], 0) for key in ('x', 'y', 'w', 'h')):
            issues.append(f'{label}.content_crop: integer rect required')
    root = document['root']
    if _exact(root, {'selector', 'found', 'fingerprint'}, set(), f'{label}.root', issues):
        if not isinstance(root['selector'], str) or not root['selector']:
            issues.append(f'{label}.root.selector: nonempty string required')
        if root['found'] is not True:
            issues.append(f'{label}.root.found: 루트 미발견은 실패다(K2)')
        if _exact(root['fingerprint'], {'tag', 'label', 'descendants', 'rect'}, set(),
                  f'{label}.root.fingerprint', issues):
            if not isinstance(root['fingerprint']['tag'], str) or not _is_int(root['fingerprint']['descendants'], 0):
                issues.append(f'{label}.root.fingerprint: tag/descendants required')
            if root['fingerprint']['label'] is not None and not isinstance(root['fingerprint']['label'], str):
                issues.append(f'{label}.root.fingerprint.label: string or null required')
            _exact(root['fingerprint']['rect'], {'x', 'y', 'w', 'h'}, set(),
                   f'{label}.root.fingerprint.rect', issues)
    outside = document['outside_root']
    if _exact(outside, {'count', 'sample'}, set(), f'{label}.outside_root', issues):
        if not _is_int(outside['count'], 0) or not _strings(outside['sample']):
            issues.append(f'{label}.outside_root: count/sample shape required')
        elif outside['count'] > 0:
            # 스니펫 scanOutsideRoot는 excluded_regions에 매칭된 요소를 이미 count에서 뺀다 — 문서의
            # count는 «선언으로 닫히지 않은 잔여 루트 밖 대상 수»이므로 선언 유무와 무관하게 결함이다.
            declared = document['excluded_regions'] if isinstance(document['excluded_regions'], list) else []
            issues.append(f'{label}.outside_root: 루트 밖 대상 {outside["count"]}개가 선언으로 닫히지 않았다'
                          f'(excluded_regions 선언 {len(declared)}행 · 표본 {outside["sample"]!r})(K3)')
    for name, fields in (('excluded_regions', {'selector', 'reason'}),
                         ('declared', {'selector', 'reason'}),
                         ('declared_unmatched', {'selector', 'reason'})):
        rows = document[name]
        if not isinstance(rows, list):
            issues.append(f'{label}.{name}: list required')
            continue
        for index, row in enumerate(rows):
            here = f'{label}.{name}[{index}]'
            optional = {'value'} if name == 'declared' else set()
            if not _exact(row, fields, optional, here, issues):
                continue
            if not isinstance(row['selector'], str) or not row['selector']:
                issues.append(f'{here}.selector: nonempty string required')
            if row['reason'] is not None and not isinstance(row['reason'], str):
                issues.append(f'{here}.reason: string or null required')
            if 'value' in row and not isinstance(row['value'], str):
                issues.append(f'{here}.value: string required')
    served = document['served']
    if (not isinstance(served, dict) or not served
            or not all(isinstance(key, str) and key and _is_sha(value) for key, value in served.items())):
        issues.append(f'{label}.served: {{local_path: sha256}} required')
    try:
        when = datetime.fromisoformat(str(document['observed_at']).replace('Z', '+00:00'))
        if when.tzinfo is None:
            raise ValueError('timezone absent')
    except (AttributeError, TypeError, ValueError):
        issues.append(f'{label}.observed_at: timestamp with timezone required')
    rows = document['discovery_limits']
    if not isinstance(rows, list):
        issues.append(f'{label}.discovery_limits: list required')
    else:
        for index, row in enumerate(rows):
            here = f'{label}.discovery_limits[{index}]'
            if _exact(row, {'kind', 'dom_path', 'reason'}, set(), here, issues):
                if not all(isinstance(row[key], str) and row[key] for key in ('kind', 'dom_path', 'reason')):
                    issues.append(f'{here}: nonempty string fields required')
    caps = document['caps_hit']
    if not isinstance(document['partial'], bool):
        issues.append(f'{label}.partial: boolean required')
    if not _strings(caps) or set(caps) - CAPS or len(set(caps)) != len(caps):
        issues.append(f'{label}.caps_hit: unique {sorted(CAPS)} required ({caps!r})')
    elif document['partial'] is False and caps:
        issues.append(f'{label}: partial:false인데 caps_hit={caps} — 상한에 걸린 수집은 완주가 아니다')
    if document['environment_error'] is not None and not isinstance(document['environment_error'], str):
        issues.append(f'{label}.environment_error: string or null required')
    targets = _check_targets(document, label, issues)
    initial = document['initial']
    if _exact(initial, {'inventory', 'state_hash', 'surface_key', 'capture'}, set(), f'{label}.initial', issues):
        _check_inventory(initial['inventory'], targets, f'{label}.initial.inventory', issues)
        if not isinstance(initial['state_hash'], str) or not isinstance(initial['surface_key'], str):
            issues.append(f'{label}.initial: state_hash/surface_key strings required')
    return targets


def _check_bindings(build: Path, document: dict, case: dict, archive_path: Path,
                    label: str, issues: list[str]) -> None:
    """동결 바이트·루트·크롭·entrypoint 응답을 **case마다** 묶는다(K3).

    한 interactions.json을 여러 case가 공유하는 것은 정상 운용이므로 이 검사는 문서
    dedupe 밖에서 case별로 돈다(수정 라운드 1 I-1).
    """
    entry = case.get('entrypoint') if isinstance(case.get('entrypoint'), dict) else {}
    try:
        archive_sha = sha(archive_path.read_bytes())
    except OSError as error:
        issues.append(f'{label}: cannot read archive manifest ({error})')
        return
    if document.get('archive_sha256') != archive_sha:
        issues.append(f'{label}.archive_sha256: stale source archive '
                      f'({document.get("archive_sha256")} ≠ {archive_sha})')
    if document.get('entrypoint') != entry:
        issues.append(f'{label}.entrypoint: does not match case ({document.get("entrypoint")!r})')
    entry_path = entry.get('path') if isinstance(entry.get('path'), str) else ''
    url = document.get('url')
    if not isinstance(url, str) or not re.match(r'^https?://[^/\s]+', url):
        issues.append(f'{label}.url: original browser HTTP(S) URL required')
    elif unquote(urlsplit(url).path).rsplit('/', 1)[-1] != posixpath.basename(entry_path):
        issues.append(f'{label}.url: percent-decode한 basename이 entrypoint와 다르다 ({url})')
    crop = document.get('content_crop')
    if isinstance(crop, dict) and [crop.get('w'), crop.get('h')] != case.get('viewport'):
        issues.append(f'{label}.content_crop: 루트 크롭 {crop.get("w")}x{crop.get("h")}이 '
                      f'case viewport {case.get("viewport")}와 다르다')
    root = document.get('root')
    meta = build / 'screen-meta.json'
    if isinstance(root, dict) and meta.is_file():
        try:
            selected = load_json(meta)
        except (OSError, ValueError) as error:
            issues.append(f'screen-meta.json: unreadable ({error})')
            selected = None
        if isinstance(selected, dict) and selected.get('source_sha256') == entry.get('sha256'):
            expected = f'[data-screen-label="{selected.get("screen_label")}"]'
            if root.get('selector') != expected:
                issues.append(f'{label}.root.selector: {expected}이어야 한다 ({root.get("selector")!r})')
    served = document.get('served')
    if isinstance(served, dict):
        entry_key = posixpath.basename(entry_path)
        if entry_key not in served:
            issues.append(f'{label}.served: entrypoint 응답 바이트가 없다 ({entry_key!r})')
        elif served[entry_key] != entry.get('sha256'):
            issues.append(f'{label}.served[{entry_key!r}]: 동결 entrypoint와 다른 바이트가 서빙됐다 '
                          f'({served[entry_key]} ≠ {entry.get("sha256")})')


def _check_served_rows(document: dict, archive_path: Path, reference_root: Path,
                       label: str, issues: list[str]) -> None:
    """서빙된 경로마다 manifest 행·sha·동결 파일이 있는가(문서 단위 — K3)."""
    served = document.get('served')
    if not isinstance(served, dict):
        return
    try:
        manifest = load_json(archive_path)
        rows = {row.get('local_path'): row for row in manifest.get('files') or [] if isinstance(row, dict)}
    except (OSError, ValueError) as error:
        issues.append(f'{label}.served: cannot read archive manifest ({error})')
        return
    entry = document.get('entrypoint') if isinstance(document.get('entrypoint'), dict) else {}
    directory = posixpath.dirname(entry.get('path') if isinstance(entry.get('path'), str) else '')
    for key in sorted(served):
        local = posixpath.normpath(posixpath.join(directory, key))
        row = rows.get(local)
        if local.startswith('..') or row is None:
            issues.append(f'{label}.served[{key!r}]: manifest 행이 없다 ({local!r})')
            continue
        if served[key] != row.get('sha256'):
            issues.append(f'{label}.served[{key!r}]: manifest sha와 다르다 '
                          f'({served[key]} ≠ {row.get("sha256")})')
        confined(reference_root, local, f'{label}.served[{key!r}]', issues)


def _check_initial(build: Path, document: dict, label: str, issues: list[str],
                   items: list[tuple[str, bytes]]) -> None:
    """initial 캡처도 step 캡처와 같은 모양·실재·digest 검사를 받는다(수정 라운드 1 M-3)."""
    initial = document.get('initial')
    if isinstance(initial, dict) and 'capture' in initial:
        _capture_item(build, initial['capture'], f'{label}.initial.capture', issues, items)


def _exclusion_rows(spec: dict) -> tuple[set[str], set[str]]:
    """형식이 맞는 예외 행만 (단위 키, 표면 키)로 돌려준다 — 형식 결함은 _check_exclusions가 낸다."""
    units, surfaces = set(), set()
    for row in spec.get('interaction_exclusions') or []:
        if not isinstance(row, dict):
            continue
        if set(row) == EXCLUSION_UNIT_FIELDS:
            units.add(_unit_key(row['target'], row['action'], row['option']))
        elif set(row) == EXCLUSION_SURFACE_FIELDS:
            surfaces.add(row['surface'])
    return units, surfaces


def _interaction_documents(items: list[tuple[str, bytes]]) -> list[tuple[str, dict]]:
    found = []
    for name, data in items:
        if not name.startswith('interactions/'):
            continue
        try:
            document = json.loads(data)
        except ValueError:
            continue
        if isinstance(document, dict):
            found.append((name, document))
    return found


def _active_targets(items: list[tuple[str, bytes]]) -> int:
    """예외 상한의 분모 — build 전체 활성 identity의 합집합(수정 라운드 1 M-1)."""
    found: set[str] = set()
    for _name, document in _interaction_documents(items):
        found |= {entry['id'] for inventory in _inventories(document) for entry in inventory
                  if _is_active(entry) and isinstance(entry.get('id'), str)}
    return len(found)


def _check_exclusions(build: Path, spec: dict, items: list[tuple[str, bytes]], issues: list[str]) -> None:
    """작성자 면제는 없다 — 사용자 승인 원문·앵커·10% 상한만이 예외를 연다(K3)."""
    rows = spec.get('interaction_exclusions')
    if rows is None:
        return
    if not isinstance(rows, list):
        issues.append('interaction_exclusions: list required')
        return
    scope = spec.get('scope')
    approved = ''
    if isinstance(scope, dict) and isinstance(scope.get('path'), str):
        try:
            approved = _collapse((build / scope['path']).read_text(encoding='utf-8'))
        except (OSError, UnicodeError):
            approved = ''
    for index, row in enumerate(rows):
        here = f'interaction_exclusions[{index}]'
        if not isinstance(row, dict) or set(row) not in (EXCLUSION_UNIT_FIELDS, EXCLUSION_SURFACE_FIELDS):
            issues.append(f'{here}: exact unit or surface exception fields required')
            continue
        if not all(isinstance(row[key], str) and row[key] for key in set(row) - {'option'}):
            issues.append(f'{here}: nonempty string fields required')
            continue
        if 'option' in row and row['option'] is not None and not isinstance(row['option'], (str, bool)):
            issues.append(f'{here}.option: string, boolean or null required')
            continue
        quote = _collapse(row['approval_quote'])
        if len(quote) < 10:
            issues.append(f'{here}.approval_quote: 10자 이상의 사용자 승인 원문이 필요하다 ({quote!r})')
        elif quote not in approved:
            issues.append(f'{here}.approval_quote: scope 원문에 없다 ({quote!r})')
        reference = row['scope_ref']
        document, _, anchor = reference.partition('#')
        if not document or not anchor:
            issues.append(f'{here}.scope_ref: "<경로>#<앵커>" 형식이어야 한다 ({reference!r})')
            continue
        resolved = confined(build, document, f'{here}.scope_ref', issues)
        if resolved is None:
            continue
        try:
            text = resolved.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            issues.append(f'{here}.scope_ref: 원문을 읽을 수 없다 ({error})')
            continue
        if anchor not in _anchors(text):
            issues.append(f'{here}.scope_ref: 앵커가 실제로 없다 ({reference!r})')
    active = _active_targets(items)
    if len(rows) * 10 > active:
        issues.append(f'interaction_exclusions: 예외 {len(rows)}행은 활성 대상 {active}개의 10% 상한을 넘는다')


def _surface_at(document: dict, step: Any) -> str | None:
    block = document.get('initial') if step == 'initial' else _step_at(document, step)
    if step != 'initial' and isinstance(block, dict):
        block = block.get('after')
    return block.get('surface_key') if isinstance(block, dict) else None


def _step_at(document: dict, number: Any) -> dict | None:
    for step in document.get('steps') or []:
        if isinstance(step, dict) and step.get('n') == number and step.get('status') == 'executed':
            return step
    return None


def _capture_at(document: dict, step: Any) -> dict | None:
    if step == 'initial':
        initial = document.get('initial')
        capture = initial.get('capture') if isinstance(initial, dict) else None
        return capture if isinstance(capture, dict) else None
    found = _step_at(document, step)
    after = found.get('after') if isinstance(found, dict) else None
    capture = after.get('capture') if isinstance(after, dict) else None
    return capture if isinstance(capture, dict) else None


def _check_reached_by(case: dict, document: dict, path: str, label: str, issues: list[str]) -> None:
    row = case.get('reached_by')
    if not isinstance(row, dict) or set(row) != {'interactions', 'step'}:
        issues.append(f'{label}: archive case는 reached_by {{interactions, step}}이 필요하다 ({row!r})')
        return
    if row['interactions'] != path:
        issues.append(f'{label}: reached_by.interactions는 이 case의 관찰 문서여야 한다 ({row["interactions"]!r})')
        return
    if row['step'] != 'initial' and not _is_int(row['step'], 1):
        issues.append(f'{label}: reached_by.step은 "initial" 또는 step 번호여야 한다 ({row["step"]!r})')
        return
    capture = _capture_at(document, row['step'])
    if capture is None:
        issues.append(f'{label}: reached_by.step {row["step"]!r}에 해당하는 실행 step·캡처가 없다')
        return
    reference = case.get('reference_capture')
    expected = reference.get('sha256') if isinstance(reference, dict) else None
    if capture.get('sha256') != expected:
        issues.append(f'{label}: reference_capture sha가 reached_by step의 캡처와 다르다 '
                      f'({expected} ≠ {capture.get("sha256")})')


def _check_surfaces(document: dict, path: str, spec: dict, label: str, issues: list[str]) -> None:
    reached = set()
    for case in spec.get('cases') or []:
        row = case.get('reached_by') if isinstance(case, dict) else None
        if not isinstance(row, dict) or row.get('interactions') != path:
            continue
        surface = _surface_at(document, row.get('step'))
        if surface is not None:
            reached.add(surface)
    _units, exempt = _exclusion_rows(spec)
    for surface in sorted(linked_surfaces(document)):
        if surface in reached or surface in exempt:
            continue
        issues.append(f'{label}: 새 표면 {surface!r}에 도달한 case reached_by도 승인 예외도 없다')


def _check_residual(document: dict, spec: dict, label: str, issues: list[str]) -> None:
    excluded, _surfaces = _exclusion_rows(spec)
    remaining = [unit for unit in interaction_residual(document)
                 if _unit_key(*unit) not in excluded]
    if not remaining:
        return
    shown = ', '.join(repr(unit) for unit in remaining[:20])
    if len(remaining) > 20:
        shown += f' 외 {len(remaining) - 20}건'
    caps = ','.join(document.get('caps_hit') or []) if document.get('partial') is True else ''
    prefix = f'partial(caps_hit={caps}) 수집인데 ' if caps else ''
    issues.append(f'{label}: {prefix}잔여 {len(remaining)}건 — {shown}')


def validate_interactions(build: Path, case: dict, observed: dict, archive_path: Path,
                          reference_root: Path, spec: dict, issues: list[str],
                          items: list[tuple[str, bytes]]) -> None:
    """v2 관찰이 가리키는 interactions.json을 K3대로 검사한다(문서당 한 번 + case별 연결)."""
    label = f'cases[{case.get("id")}].interactions'
    item = pointer(build, observed.get('interactions'), label, issues)
    if item is None:
        return
    path = observed['interactions']['path']
    label = f'{label}({path})'
    try:
        document = json.loads(item[1])
    except ValueError:
        issues.append(f'{label}: invalid JSON')
        return
    if not isinstance(document, dict):
        issues.append(f'{label}: object required')
        return
    if document.get('environment_error') is not None:
        # 미실행은 결함(2)이 아니라 검사 불가(1)다 — partial과 구별한다(K2).
        raise ValueError(f'{label}: environment_error — {document["environment_error"]}')
    name = f'interactions/{path}'
    if all(existing != name for existing, _data in items):  # 문서 단위 검사는 문서당 한 번
        items.append((name, item[1]))
        targets = _check_document(document, label, issues)
        if targets is not None:
            _check_steps(build, document, targets, label, issues, items)
            _check_initial(build, document, label, issues, items)
        _check_served_rows(document, archive_path, reference_root, label, issues)
        if not collector_assets_ok(document, Path(__file__).resolve().parents[1] / 'assets'):
            collector = document.get('collector') if isinstance(document.get('collector'), dict) else {}
            issues.append(f'{label}.collector: 이 플러그인의 수집기 바이트가 아니다 '
                          f'(snippet_sha256={collector.get("snippet_sha256")} · '
                          f'driver_sha256={collector.get("driver_sha256")})')
        _check_residual(document, spec, label, issues)
        _check_surfaces(document, path, spec, label, issues)
    _check_bindings(build, document, case, archive_path, label, issues)  # case 결속은 case마다
    _check_reached_by(case, document, path, label, issues)


def _notices(spec: dict, items: list[tuple[str, bytes]]) -> list[str]:
    """성공 출력에 남기는 1급 통지 — 예외 전량과 partial 수집 사실(K3)."""
    lines = []
    for index, row in enumerate(spec.get('interaction_exclusions') or []):
        lines.append(f'[design-evidence] interaction_exclusions[{index}]: '
                     + json.dumps(row, sort_keys=True, ensure_ascii=False))
    for name, document in _interaction_documents(items):
        if document.get('partial') is True:
            caps = ','.join(document.get('caps_hit') or [])
            lines.append(f'[design-evidence] {name}: partial(caps_hit={caps})·잔여 0')
    return lines


def _source_observation(build: Path, case: dict, archive_path: Path, label: str, issues: list[str],
                        items: list[tuple[str, bytes]], *, legacy_v1: bool = False) -> dict | None:
    """Return the parsed original observation; version 2 also carries interaction evidence."""
    item = pointer(build, case.get('source_observation'), f'{label}.source_observation', issues)
    if item is None:
        return None
    items.append((f'observation/{case["source_observation"]["path"]}', item[1]))
    try:
        observed = json.loads(item[1])
    except ValueError:
        issues.append(f'{label}.source_observation: invalid JSON')
        return None
    required = {'version', 'archive_sha256', 'entrypoint', 'case_id', 'screen', 'state',
                'viewport', 'url', 'observed_at', 'capture', 'trace'}
    version = observed.get('version') if isinstance(observed, dict) else None
    if version == 2:
        required = required | {'interactions'}
    if not isinstance(observed, dict) or set(observed) != required or version not in (1, 2):
        issues.append(f'{label}.source_observation: exact version 1 or 2 fields required')
        return None
    if version == 1 and not legacy_v1:
        issues.append(f'{label}.source_observation: interaction evidence required '
                      '(version 2 with interactions)')
        return None
    if observed['archive_sha256'] != sha(archive_path.read_bytes()):
        issues.append(f'{label}.source_observation.archive_sha256: stale source archive')
    for key, case_key in (('entrypoint', 'entrypoint'), ('case_id', 'id'), ('screen', 'screen'),
                          ('state', 'state'), ('viewport', 'viewport'), ('capture', 'reference_capture')):
        if observed[key] != case[case_key]:
            issues.append(f'{label}.source_observation.{key}: does not match case')
    if not isinstance(observed['url'], str) or not re.match(r'^https?://[^/\s]+', observed['url']):
        issues.append(f'{label}.source_observation.url: original browser HTTP(S) URL required')
    try:
        when = datetime.fromisoformat(observed['observed_at'].replace('Z', '+00:00'))
        if when.tzinfo is None:
            raise ValueError('timezone absent')
    except (AttributeError, TypeError, ValueError):
        issues.append(f'{label}.source_observation.observed_at: timestamp with timezone required')
    trace = pointer(build, observed['trace'], f'{label}.source_observation.trace', issues)
    if trace:
        if not trace[1].strip():
            issues.append(f'{label}.source_observation.trace: empty browser evidence')
        items.append((f'original-trace/{observed["trace"]["path"]}', trace[1]))
    return observed


def validate_inputs(build: Path, project: Path, *, require_review: bool = True,
                    legacy_v1: bool = False) -> tuple[dict, str, list[tuple[str, bytes]]]:
    issues: list[str] = []
    input_path = build / 'design-input.json'
    try:
        spec = load_json(input_path)
    except (OSError, ValueError) as error:
        raise Defects([f'design-input.json: unreadable ({error})'])
    required = {'version', 'reference_root', 'manifests', 'scope', 'coverage_review', 'cases'}
    allowed = required | {'host_files', 'interaction_exclusions'}
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
        if name == 'coverage_review' and not require_review:
            continue
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
        is_archive = isinstance(manifest, dict) and manifest.get('collection') == 'archive'
        if is_archive and len(manifests) != 1:
            issues.append('manifests: exactly one full-tree archive manifest required for all archive cases')
        ready = (manifest.get('archive_ready') is True and manifest.get('source_ready') is False
                 if is_archive else isinstance(manifest, dict) and manifest.get('source_ready') is True)
        if not isinstance(manifest, dict) or manifest.get('version') != 1 or not ready:
            issues.append(f'manifests[{index}]: version=1 and source_ready=true required')
            continue
        if manifest.get('collection', 'static') not in ('static', 'archive'):
            issues.append(f'manifests[{index}].collection: static or archive required')
        rows = manifest.get('files')
        if not isinstance(rows, list) or not rows:
            issues.append(f'manifests[{index}].files: nonempty list required')
            continue
        locals_seen = set()
        for row_index, row in enumerate(rows):
            here = f'manifests[{index}].files[{row_index}]'
            required_row = {'source', 'source_document', 'local_path', 'kind', 'status', 'sha256', 'size_bytes', 'reason'}
            if not isinstance(row, dict) or not required_row <= set(row) or set(row) - required_row - {'requested_source', 'carried_from'}:
                issues.append(f'{here}: invalid source-manifest row fields')
                continue
            if 'carried_from' in row and not _is_sha(row['carried_from']):
                issues.append(f'{here}.carried_from: base manifest sha256 required')
                continue
            if row.get('status') != 'ok':
                issues.append(f'{here}: successful row required')
                continue
            if not all(isinstance(row.get(key), str) for key in ('source', 'source_document', 'local_path', 'kind', 'sha256', 'reason')):
                issues.append(f'{here}: invalid source-manifest row types')
                continue
            if (not isinstance(row.get('size_bytes'), int) or isinstance(row.get('size_bytes'), bool)
                    or row['size_bytes'] < (0 if is_archive else 1)
                    or ('requested_source' in row and not isinstance(row['requested_source'], str))):
                issues.append(f'{here}: invalid source-manifest size/requested_source')
                continue
            local = row.get('local_path')
            frozen = confined(reference_root, local, f'{here}.local_path', issues)
            if local in locals_seen:
                issues.append(f'{here}.local_path: duplicate')
            locals_seen.add(local)
            if frozen:
                inferred = resource_kind(frozen.as_uri() if is_archive else row['source'], row['kind'])
                if inferred != row['kind']:
                    issues.append(f'{here}.kind: contradicts source suffix')
                data = frozen.read_bytes()
                if row.get('size_bytes') != len(data) or row.get('sha256') != sha(data):
                    issues.append(f'{here}: byte size/hash mismatch')
                digest_items.append((f'source/{local}', data))
        if manifest.get('entrypoint') not in locals_seen:
            issues.append(f'manifests[{index}].entrypoint: missing successful file row')
        if is_archive:
            try:
                actual = {p.relative_to(reference_root).as_posix() for p in archive_files(reference_root)}
                if actual != locals_seen:
                    issues.append(f'manifests[{index}]: archive inventory differs from frozen tree')
            except (OSError, ValueError) as error:
                issues.append(f'manifests[{index}]: invalid archive inventory ({error})')
        else:
            _manifest_closure(reference_root, manifest, rows, f'manifests[{index}]', issues)
        manifest_records.append((path, manifest, rows))
    cases = spec.get('cases')
    if not isinstance(cases, list) or not cases:
        issues.append('cases: nonempty list required')
        cases = []
    ids = set()
    case_required = {'id', 'screen', 'state', 'viewport', 'scope_refs', 'entrypoint', 'reference_capture'}
    case_allowed = case_required | {'media', 'source_observation', 'reached_by'}
    all_entries = {(manifest.get('entrypoint', ''), row.get('sha256'))
                   for _, manifest, rows in manifest_records for row in rows
                   if manifest.get('collection') != 'archive' and row.get('status') == 'ok'
                   and row.get('local_path') == manifest.get('entrypoint')}
    archive_entries = {(row.get('local_path'), row.get('sha256')): path
                       for path, manifest, rows in manifest_records if manifest.get('collection') == 'archive'
                       for row in rows if row.get('status') == 'ok' and row.get('kind') in ('html', 'component')}
    all_entries.update(archive_entries)
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
        archive_path = archive_entries.get((entry.get('path'), entry.get('sha256'))) if isinstance(entry, dict) else None
        if archive_path:
            # Recompute from frozen bytes: a self-consistent partial inventory or
            # an old manifest without a dependency report cannot hide missing files.
            try:
                for row in archive_dependencies(reference_root, reference_root / entry['path']):
                    if row['status'] == 'missing':
                        issues.append(f'{here}: {row["reason"]}: {row["source"]!r} in {row["source_document"]}')
            except (OSError, ValueError) as error:
                issues.append(f'{here}: cannot inspect archive dependencies ({error})')
            observed = _source_observation(build, case, archive_path, here, issues, digest_items,
                                           legacy_v1=legacy_v1)
            if observed is not None and observed.get('version') == 2:
                validate_interactions(build, case, observed, archive_path, reference_root, spec,
                                      issues, digest_items)
        else:
            for name in ('source_observation', 'reached_by'):
                if name in case:
                    issues.append(f'{here}.{name}: requires an archive HTML/component entrypoint')
        check_media_requirements(case.get('media'), f'{here}.media', issues)
    _check_exclusions(build, spec, digest_items, issues)
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
    if any(manifest.get('collection') == 'archive' for _, manifest, _ in manifest_records) and require_review:
        expected = review_digest(spec, digest_items)
        review = spec.get('coverage_review')
        review_file = confined(build, review.get('path'), 'coverage_review', issues) if isinstance(review, dict) else None
        if review_file:
            report = review_file.read_text(encoding='utf-8')
            if re.findall(r'^reviewed-input: ([0-9a-f]{64})$', report, re.M) != [expected]:
                issues.append('coverage_review: reviewed-input does not match current source/cases/observations')
            if re.findall(r'^review-result: (\S+)$', report, re.M) != ['pass']:
                issues.append('coverage_review: independent review-result: pass required')
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
        if path.is_symlink() and path.is_dir():
            raise Defects([f'directory symlink is unsupported in implementation tree: {relative.as_posix()}'])
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
    originals = [confined(build, case['reference_capture']['path'], f'cases[{index}].original', issues)
                 for index, case in enumerate(spec['cases'])]
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
        if captured:
            try:
                if any(captured[0].samefile(original) for original in originals if original is not None):
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
    spec, input_value, items = validate_inputs(build, project, require_review=args.phase != 'prepare')
    if args.phase in ('prepare', 'inputs'):
        # 예외 전량·partial 사실은 사람이 보는 로그로 낸다 — stdout은 결과 JSON 전용이다.
        for line in _notices(spec, items):
            print(line, file=sys.stderr)
    if args.phase == 'prepare':
        return {'review_digest': review_digest(spec, items)}
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
    parser.add_argument('--phase', required=True, choices=('prepare', 'inputs', 'visual'))
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
