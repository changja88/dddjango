#!/usr/bin/env python3
# dddjango-web 공식 플랫폼 SDK 등재 도구 (값 정본: discipline-web-houserules §9).
#
# 사용:
#   python sdk_vendor.py candidate <루트> --id <id> --version <판> --source-url <https> --docs-url <https>
#          [--from-file <로컬 사본>] [--docs-file <브라우저 저장 문서>] [--members-file <함수 열거 JSON>]
#          --out <산출물 폴더>/sdk-candidates/<id>/
#   python sdk_vendor.py install <루트> <candidate.json> --entry <entry-draft.json> --approval-source "<꼴>"
#          [--source-tokens "<덧붙일 낱말>"] --approved-at "<YYYY-MM-DD HH:MM +ZZZZ>" --gate "G1|G1'|G1(리팩토링)"
#          --build <산출물 폴더> [--replace | --scope-add <원소>… | --register-existing <지금 경로>] [--dry-run]
#   python sdk_vendor.py verify <루트>          # 늘 검사(WV1~WV6·WV13)만 · 시안 증거 검사 없음
#   python sdk_vendor.py restore <루트> <id>    # 승인 불요 복원: 다시 받은 바이트 = 등재 지문 · 목록 재정규화 · 표지
#   python sdk_vendor.py remove <루트> <id>     # 항목 + vendor/<id>/ 디렉터리째(저장소 템플릿 참조가 남으면 거절)
#
# 종료코드: 0 = 통과·완료 / 1 = 사용·입력 오류·판정 불가(미실행 — 통과가 아니다) / 2 = 거절·검사 발견.
# 목록·사본은 이 도구로만 쓴다(정규 바이트 · NFC). 해시·크기·증거·접속 호스트는 candidate 결과에서만, 사람 판단 칸은
# entry-draft 에서만 가져온다. 쓴 뒤 늘 검사를 돌려 실패하면 되돌린다(재실행은 멱등).

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.check_vendor import (JsView, VendorUndecidable, run_vendor, unregistered_units,  # noqa: E402
                              _tracked_vendor)
from src.common import (SDK_REGISTRY, VENDOR_ATTRS, VENDOR_ATTRS_BYTES, VENDOR_DIR, BackstopContext,  # noqa: E402
                        mask_js)
from src.sdk_registry import (AT_RE, DRAFT_FIELDS, FILE_NAME_RE, GATES, ID_RE, IDENT_RE, SCHEMA,  # noqa: E402
                              RegistryError, canonical_bytes, candidate_token, check_source, compute_origins,
                              entry_sha256, https_hosts, lib_cdn_reason, operator_words,
                              parse_scope_item, scope_unit, sri, strict_loads, trap_hits, url_problems,
                              validate_entry)

EXIT_OK, EXIT_ERR, EXIT_RED = 0, 1, 2
CANDIDATE_SCHEMA: str = 'dddjango-web-sdk-candidate/1'
API_PATH_LITERAL = re.compile(r'^/v\d+(?:/[A-Za-z0-9_.\-]+)+$')
SRI_TOKEN = re.compile(r'sha(?:256|384|512)-[A-Za-z0-9+/]{20,}={0,2}')
LOADER_MARKERS: Tuple[str, ...] = ('importScripts(', 'import(', 'eval(', 'new Function', 'document.write')
SECOND_LEVEL: Set[str] = {'co', 'or', 'go', 'ne', 'ac', 're', 'pe', 'com', 'net', 'org'}
UNVERIFIED: str = '출처 검증 없음'


class Refused(Exception):
    """거절 — exit 2."""


class UsageError(Exception):
    """사용·입력 오류 — exit 1."""


# ------------------------------------------------------------------ 공용


def fetch(url: str, timeout: int = 30) -> Tuple[str, str, bytes]:
    """https 로 받는다 — (리다이렉트 최종 URL, Content-Type, 바이트)."""
    request = urllib.request.Request(url, headers={'User-Agent': 'dddjango-web-sdk-vendor/1'})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.geturl(), response.headers.get('Content-Type', ''), response.read()


def registrable(host: str) -> str:
    labels: List[str] = host.lower().rstrip('.').split('.')
    if len(labels) >= 3 and labels[-2] in SECOND_LEVEL and len(labels[-1]) == 2:
        return '.'.join(labels[-3:])
    return '.'.join(labels[-2:])


def load_json(path: Path, label: str) -> dict:
    try:
        data = strict_loads(path.read_bytes())
    except OSError as error:
        raise UsageError('%s 를 읽을 수 없다 — %s' % (label, error))
    except RegistryError as error:
        raise UsageError('%s 엄격 파싱 실패 — %s' % (label, error))
    if not isinstance(data, dict):
        raise UsageError('%s 가 객체가 아니다' % label)
    return data


def read_registry(root: Path) -> Optional[dict]:
    path: Path = root / 'web' / SDK_REGISTRY
    if not path.exists():
        return None
    try:
        data = strict_loads(path.read_bytes())
    except RegistryError as error:
        raise Refused('등재 목록을 엄격 규칙으로 읽을 수 없다 — %s(먼저 고친다)' % error)
    if not isinstance(data, dict) or not isinstance(data.get('sdks'), dict):
        raise Refused('등재 목록 꼴이 깨졌다 — 먼저 고친다')
    return data


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def write_bytes(path: Path, data: bytes) -> None:
    if path.is_symlink():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def verify_findings(root: Path) -> Tuple[List[str], List[str]]:
    """늘 검사(WV1~WV6·WV13) — (발견 문자열, 알림). 얕은 이력+미등재 단위면 VendorUndecidable."""
    ctx: BackstopContext = BackstopContext.build(root=root, diff_base=None, all_mode=True)
    findings = run_vendor(ctx, always_only=True)
    return [str(f) for f in findings], list(ctx.notices)


def settings_has(root: Path, name: str) -> bool:
    rx = re.compile(r'^[ \t]*%s[ \t]*(?::[^=\n]*)?=' % re.escape(name), re.M)
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name in ('web', '.git', '.dddjango-web', '.dddjango'):
            continue
        files: List[Path] = []
        if (child / 'settings.py').is_file():
            files.append(child / 'settings.py')
        if (child / 'settings').is_dir():
            files += sorted((child / 'settings').rglob('*.py'))
        if any(rx.search(f.read_text(encoding='utf-8', errors='replace')) for f in files):
            return True
    return False


# ------------------------------------------------------------------ candidate


def _first_comment(text: str) -> str:
    stripped: str = text.lstrip()
    if stripped.startswith('/*'):
        end: int = stripped.find('*/')
        return stripped[:end + 2] if end >= 0 else ''
    return ''


def cmd_candidate(ns: argparse.Namespace) -> int:
    root: Path = Path(ns.root).resolve()
    sid: str = ns.id
    if not ID_RE.match(sid):
        raise UsageError('id 꼴 `[a-z][a-z0-9_]*` 위반 — %s' % sid)
    if not ns.version or re.search(r'[\s/#@]', ns.version):
        raise UsageError('판 문자열 꼴 위반 — %r' % ns.version)
    for label, url in (('source-url', ns.source_url), ('docs-url', ns.docs_url)):
        problems = url_problems(url, label)
        if problems:
            raise UsageError(' · '.join(problems))
    reason = lib_cdn_reason(ns.source_url)
    if reason:
        raise Refused('원본이 %s — 공식 SDK 원본은 운영자 공식 도메인에서만 받는다' % reason)
    out: Path = Path(ns.out).resolve()
    allowed_sites: Set[str] = {registrable(urlsplit(ns.source_url).hostname or ''),
                               registrable(urlsplit(ns.docs_url).hostname or '')}
    notes: List[str] = []
    provenance: str = 'network'
    final_url: str = ns.source_url
    if ns.from_file:
        data: bytes = Path(ns.from_file).read_bytes()
        provenance = 'file-unverified'
        try:
            final_url, _ctype, again = fetch(ns.source_url)
            if again != data:
                raise Refused('사용자 제공 파일이 원본(%s)에서 다시 받은 바이트와 다르다' % ns.source_url)
            provenance = 'file-refetched'
        except (urllib.error.URLError, OSError, ValueError) as error:
            final_url = ns.source_url
            notes.append('원본을 다시 받지 못했다(%s) — 바이트 대조 없음' % error)
    else:
        try:
            final_url, ctype, data = fetch(ns.source_url)
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise UsageError('원본을 받을 수 없다 — %s' % error)
        if 'html' in ctype.lower():
            raise Refused('원본 응답이 HTML 이다(Content-Type %s)' % ctype)
    if not data:
        raise Refused('원본 응답이 비었다')
    if data.lstrip()[:15].lower().startswith((b'<!doctype', b'<html')):
        raise Refused('원본 응답이 HTML 이다')
    final_problems = url_problems(final_url, 'final_url')
    if final_problems:
        raise Refused(' · '.join(final_problems))
    final_host: str = urlsplit(final_url).hostname or ''
    if lib_cdn_reason(final_url):
        raise Refused('리다이렉트 최종 주소가 %s' % lib_cdn_reason(final_url))
    if registrable(final_host) not in allowed_sites:
        raise Refused('리다이렉트 최종 주소 %s 가 원본·문서의 운영자 도메인 밖' % final_url)
    # 운영자 문서
    if ns.docs_file:
        docs: bytes = Path(ns.docs_file).read_bytes()
        fetched_from: str = 'file'
    else:
        try:
            _durl, _dtype, docs = fetch(ns.docs_url)
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise UsageError('운영자 문서를 받을 수 없다 — %s(JS 렌더 문서면 --docs-file)' % error)
        fetched_from = 'network'
    doc_text: str = html.unescape(docs.decode('utf-8', 'replace')).replace('\\/', '/')
    source_parts = urlsplit(ns.source_url)
    needle: str = (source_parts.hostname or '') + source_parts.path
    spots: List[Tuple[int, int]] = [(m.start(), m.end()) for m in re.finditer(re.escape(needle), doc_text)]
    if not spots:
        raise Refused('운영자 문서(%s)가 원본 경로 %s 를 인용하지 않는다' % (ns.docs_url, needle))
    near: Set[str] = set()
    for a, b in spots:
        near.update(SRI_TOKEN.findall(doc_text[max(0, a - 100):b + 400]))
    upstream: Optional[str] = None
    if near:
        mine: Dict[str, str] = {alg: sri(data, alg) for alg in ('sha384', 'sha256', 'sha512')}
        matched = [v for v in mine.values() if v in near]
        if not matched:
            raise Refused('운영자 문서의 공개 무결성(%s)과 받은 바이트가 다르다' % ', '.join(sorted(near)))
        upstream = mine['sha384'] if mine['sha384'] in near else matched[0]
    text: str = data.decode('utf-8', 'replace')
    masked: str = mask_js(text).no_comments
    view: JsView = JsView(masked)
    api_paths: List[str] = sorted({v for _a, _b, q, v in view.literals if q != '`' and API_PATH_LITERAL.match(v)})
    features: List[str] = sorted(set(re.findall(r'\bthis\.([A-Z][A-Za-z0-9_$]*)\s*=(?!=)', view.code_text)))
    members: Optional[Dict[str, List[str]]] = None
    blocked: Optional[int] = None
    members_source: str = '문서'
    if ns.members_file:
        enumerated = load_json(Path(ns.members_file), '--members-file')
        raw_members = enumerated.get('members')
        blocked = enumerated.get('blocked_requests')
        if (not isinstance(raw_members, dict) or not all(isinstance(v, list) for v in raw_members.values())
                or type(blocked) is not int):
            raise UsageError('--members-file 꼴은 {"members": {이름공간: [함수…]}, "blocked_requests": 정수}')
        members = {}
        for nsname, fns in raw_members.items():
            names = sorted({f for f in fns if isinstance(f, str)})
            missing = [f for f in names if not IDENT_RE.match(f) or not re.search(r'\b%s\b' % re.escape(f), masked)]
            if missing or not IDENT_RE.match(nsname):
                raise Refused('열거 함수 이름이 사본 코드에 없다 — %s.%s' % (nsname, ', '.join(missing)))
            members[nsname] = names
        members_source = '실행 열거'
    name: str = Path(urlsplit(final_url).path).name
    if not name or '.' not in name or not FILE_NAME_RE.match(name):
        name = '%s.js' % sid
    sha256: str = hashlib.sha256(data).hexdigest()
    candidate: dict = {
        'schema': CANDIDATE_SCHEMA, 'id': sid, 'version': ns.version, 'source_url': ns.source_url,
        'final_url': final_url, 'docs_url': ns.docs_url, 'file': '%s/%s/%s' % (VENDOR_DIR, sid, name),
        'size': len(data), 'sha256': sha256, 'upstream_integrity': upstream,
        'evidence': {'docs_sha256': hashlib.sha256(docs).hexdigest(), 'cites_source': True,
                     'integrity_from_docs': upstream is not None, 'fetched_from': fetched_from},
        'features_in_file': features, 'hosts': sorted(https_hosts(text)), 'hosts_in_code': sorted(https_hosts(masked)),
        'api_paths': api_paths, 'members': members, 'members_source': members_source, 'blocked_requests': blocked,
        'loader_markers': sum(view.code_text.count(m) for m in LOADER_MARKERS),
        'fetched_at': now_iso(), 'candidate_token': candidate_token(sid, ns.version, sha256),
        'provenance': provenance, 'copy': name, 'notes': notes}
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_bytes(data)
    (out / 'docs.html').write_bytes(docs)
    (out / 'license-header.txt').write_text(_first_comment(text) + '\n', encoding='utf-8')
    (out / 'api-paths.txt').write_text(''.join(p + '\n' for p in api_paths), encoding='utf-8')
    (out / 'candidate.json').write_bytes(canonical_bytes(candidate))
    print('[sdk] 후보 %s · %d B · sha256 %s · 무결성 %s · 문서 인용 확인(%s) · 이름공간 %s · api 경로 %d · 함수 표 출처 %s%s'
          % (candidate['candidate_token'], len(data), sha256[:12],
             '운영자 문서 공개 값과 일치' if upstream else '운영자 공개 값 없음/문서 인용 미확인',
             fetched_from, ','.join(features) or '없음', len(api_paths), members_source,
             '' if provenance != 'file-unverified' else ' · %s(사용자 제공 파일)' % UNVERIFIED))
    for n in notes:
        print('[sdk] 알림 — %s' % n)
    print('[sdk] 후보 → %s' % out)
    return EXIT_OK


# ------------------------------------------------------------------ install


def _build_rel(root: Path, build: str) -> str:
    path: Path = Path(build).resolve()
    records: Path = (root / '.dddjango-web').resolve()
    if not path.is_relative_to(records) or path == records:
        raise UsageError('--build 는 %s/<폴더> 여야 한다 — %s' % (records, build))
    return '.dddjango-web/%s/' % path.relative_to(records).parts[0]


def _gate(value: str) -> str:
    gate: str = value.replace('′', "'")
    if gate not in GATES:
        raise UsageError('--gate 꼴 위반 — %r(G1 · G1′ · G1(리팩토링))' % value)
    return gate


def _docs_counts(folder: Path, words: Dict[str, List[str]]) -> List[str]:
    texts: List[str] = []
    for doc in sorted(folder.glob('docs*.html')):
        texts.append(unicodedata.normalize('NFC', html.unescape(doc.read_text(encoding='utf-8', errors='replace'))))
    rows: List[str] = []
    for unit, values in sorted(words.items()):
        parts: List[str] = []
        for w in values:
            n: int = sum(t.count(unicodedata.normalize('NFC', w)) for t in texts)
            parts.append('%s(%d%s)' % (w, n, ' — 운영자 문서에 없는 낱말' if n == 0 else ''))
        rows.append('%s=%s' % (unit, '·'.join(parts)))
    return rows


def _scope_groups(entry: dict, units: List[Tuple[str, str, str, str]], source_kind: str) -> List[Tuple[str, List[str]]]:
    groups: List[Tuple[str, List[str]]] = [('운영자·제품 낱말', operator_words(entry))]
    words: dict = entry.get('namespace_words') or {}
    for kind, ns, fn, path in units:
        if kind == 'gateway':
            groups.append(('gateway 경로 %s' % path, [path]))
        else:
            key: str = ns if kind == 'bundle' else '%s.%s' % (ns, fn)
            values = words.get(key)
            if not values and source_kind == 'user':
                raise Refused('낱말 표에 %s 가 없다 — 사용자 원문 대조 불가(G1 에서 본인 직접으로 받는다)' % key)
            groups.append(('%s 낱말' % key, list(values or [])))
    return groups


def cmd_install(ns: argparse.Namespace) -> int:
    root: Path = Path(ns.root).resolve()
    if not (root / 'web').is_dir():
        raise UsageError('web/ 없음 — %s' % root)
    candidate_path: Path = Path(ns.candidate).resolve()
    candidate: dict = load_json(candidate_path, 'candidate.json')
    draft: dict = load_json(Path(ns.entry), 'entry-draft.json')
    if candidate.get('schema') != CANDIDATE_SCHEMA:
        raise UsageError('candidate.json schema 가 %s 가 아니다' % CANDIDATE_SCHEMA)
    unknown = sorted(set(draft) - DRAFT_FIELDS)
    if unknown:
        raise UsageError('entry-draft 의 모르는 칸 %s — 해시·크기·증거·호스트는 도구만 쓴다' % unknown)
    if not AT_RE.match(ns.approved_at or ''):
        raise UsageError('--approved-at 꼴 «YYYY-MM-DD HH:MM +ZZZZ»(시간대 포함) — %r' % ns.approved_at)
    gate: str = _gate(ns.gate)
    build: str = _build_rel(root, ns.build)
    sid: str = candidate['id']
    registry: Optional[dict] = read_registry(root)
    sdks: dict = dict(registry['sdks']) if registry else {}
    previous: Optional[dict] = sdks.get(sid)
    extra_groups: List[Tuple[str, List[str]]] = [('덧붙인 낱말 %s' % w, [w])
                                                 for w in re.split(r'[\s,]+', ns.source_tokens or '') if w]
    notes: List[str] = []
    banner: List[str] = []

    if ns.scope_add:
        if previous is None:
            raise Refused('%s 가 등재되지 않았다 — 범위 넓힘은 등재된 SDK 에만' % sid)
        if candidate.get('sha256') != previous.get('sha256'):
            raise Refused('범위 넓힘은 바이트가 그대로여야 한다 — 후보 지문이 등재와 다르다(판 올림은 --replace)')
        entry: dict = json.loads(json.dumps(previous))
        approval: dict = entry.pop('approval')
        g: str = entry['lifecycle']['global']
        members: dict = entry.setdefault('namespace_members', {})
        for nsname, table in (draft.get('namespace_members') or {}).items():
            if nsname in members and members[nsname] != table:
                raise Refused('이미 승인된 분류표(%s)는 바꿀 수 없다 — 재승인' % nsname)
            members[nsname] = table
        gateways: dict = entry.setdefault('gateway_paths', {})
        for key, table in (draft.get('gateway_paths') or {}).items():
            if key in gateways and gateways[key] != table:
                raise Refused('이미 승인된 경로표(%s)는 바꿀 수 없다 — 재승인' % key)
            gateways[key] = table
        if not gateways:
            entry.pop('gateway_paths')
        api_paths: Set[str] = set(candidate.get('api_paths') or [])
        for key, table in gateways.items():
            stray = sorted(set(table) - api_paths)
            if stray:
                raise Refused('gateway_paths[%s] 경로가 api-paths 밖 — %s' % (key, stray))
        words: dict = entry.setdefault('namespace_words', {})
        for key, values in (draft.get('namespace_words') or {}).items():
            if key in words and words[key] != values:
                raise Refused('이미 승인된 낱말 표(%s)는 바꿀 수 없다 — 재승인' % key)
            words.setdefault(key, values)
        units: List[Tuple[str, str, str, str]] = []
        for item in ns.scope_add:
            parsed = parse_scope_item(item, g)
            if parsed is None or parsed[0] == 'core':
                raise UsageError('--scope-add 원소 꼴 위반 — %r' % item)
            kind, nsname, fn, path = parsed
            table = members.get(nsname) or {}
            if kind == 'named' and table.get(fn) == 'sdk_ui':
                raise Refused('SDK 가 그리는 UI 함수(%s)는 어떤 승인으로도 쓰지 않는다' % item)
            if kind == 'named' and table.get(fn) == 'call':
                notes.append('같은 묶음 안 기능 %s.%s — 묶음이 이미 덮는다(정보 줄)' % (nsname, fn))
            if item in entry['use_scope']:
                raise Refused('이미 use_scope 에 있다 — %s' % item)
            units.append(parsed)
            entry['use_scope'].append(item)
        entry['use_scope'] = sorted(entry['use_scope'])
        info_kind: str = 'user' if ns.approval_source.startswith('사용자 원문') else 'self'
        groups = _scope_groups(entry, units, info_kind) + extra_groups
        line_sha, problems, more = check_source(root, ns.approval_source, groups)
        notes += more
        if problems:
            raise UsageError('승인 출처 거절 — ' + ' · '.join(problems))
        for parsed in units:
            approval['namespace_sources'][scope_unit(*parsed)] = ns.approval_source
        if line_sha:
            approval['source_line_sha256'][ns.approval_source] = line_sha
        approval.update({'gate': gate, 'at': ns.approved_at, 'build': build})
        data_bytes: Optional[bytes] = None
        banner.append('범위 넓힘: %s · %s' % (sid, ' · '.join(ns.scope_add)))
    else:
        if ns.replace and previous is None:
            raise Refused('%s 가 등재되지 않았다 — 판 올림(--replace)은 등재된 SDK 에만' % sid)
        if ns.register_existing:
            data_bytes = Path(ns.register_existing).read_bytes()
        else:
            copy: Path = candidate_path.parent / str(candidate.get('copy', ''))
            if not copy.is_file():
                raise UsageError('후보 임시 사본이 없다 — %s' % copy)
            data_bytes = copy.read_bytes()
        if hashlib.sha256(data_bytes).hexdigest() != candidate.get('sha256'):
            raise Refused('사본 재해시가 후보 지문과 다르다')
        entry = {k: v for k, v in draft.items()}
        for key in ('version', 'source_url', 'final_url', 'docs_url', 'file', 'size', 'sha256', 'upstream_integrity',
                    'evidence', 'features_in_file'):
            entry[key] = candidate.get(key)
        entry['origins'] = compute_origins(data_bytes, entry.get('operator_domains') or [])
        members = entry.get('namespace_members') or {}
        enumerated = candidate.get('members')
        masked: str = mask_js(data_bytes.decode('utf-8', 'replace')).no_comments
        for nsname, table in members.items():
            if not isinstance(table, dict):
                continue
            for fn in table:
                if not IDENT_RE.match(fn) or not re.search(r'\b%s\b' % re.escape(fn), masked):
                    raise Refused('분류표 함수 %s.%s 가 사본 코드에 없다' % (nsname, fn))
            if isinstance(enumerated, dict) and nsname in enumerated and sorted(table) != sorted(enumerated[nsname]):
                raise Refused('분류표 %s 의 함수가 실행 열거와 다르다 — 표 %s · 열거 %s'
                              % (nsname, sorted(table), sorted(enumerated[nsname])))
        api_paths = set(candidate.get('api_paths') or [])
        if ns.replace and isinstance(previous, dict):
            pg: str = (previous.get('lifecycle') or {}).get('global', '')
            old_paths: Set[str] = {u[3] for u in (parse_scope_item(s, pg) for s in previous.get('use_scope') or [])
                                   if u and u[0] == 'gateway'}
            prev_api: Set[str] = {p for t in (previous.get('gateway_paths') or {}).values() for p in t}
            gone = sorted(p for p in old_paths if p not in api_paths)
            fresh = sorted(api_paths - prev_api) if prev_api else []
            print('[sdk] 판 올림 gateway 경로표 다시 뽑음: 승인 경로 중 사라진 경로 %s · 새 경로(승인 밖) %s'
                  % (', '.join(gone) or '없음', ', '.join(fresh) or '없음'))
        for key, table in (entry.get('gateway_paths') or {}).items():
            stray = sorted(set(table) - api_paths)
            if stray:
                raise Refused('gateway_paths[%s] 경로가 api-paths 밖 — %s' % (key, stray))
        if gate == 'G1(리팩토링)':
            missing = [c.get('setting') for c in entry.get('public_config') or [] if isinstance(c, dict)
                       and isinstance(c.get('setting'), str) and not settings_has(root, c['setting'])]
            if missing:
                raise Refused('리팩토링 등록은 공개 설정 배선을 하지 않는다 — settings 에 %s 없음 → ⓐ 재상정 '
                              '«기능 요청 — 공개 설정 배선»' % ', '.join(missing))
        groups = [('운영자·제품 낱말', operator_words(entry)),
                  ('판 또는 표지', [str(candidate.get('version')), str(candidate.get('candidate_token'))])]
        if candidate.get('provenance') == 'file-unverified':
            groups.append(('«%s» 확인' % UNVERIFIED, [UNVERIFIED]))
        prev_source: Optional[str] = previous['approval']['source'] if ns.replace else None
        line_sha, problems, more = check_source(root, ns.approval_source, groups + extra_groups, prev_source,
                                                candidate.get('fetched_at'))
        notes += more
        if problems:
            raise UsageError('승인 출처 거절 — ' + ' · '.join(problems))
        g = (entry.get('lifecycle') or {}).get('global', '') if isinstance(entry.get('lifecycle'), dict) else ''
        units = [p for p in (parse_scope_item(s, g) for s in entry.get('use_scope') or []) if p]
        if ns.replace:
            old_sources: dict = dict(previous['approval']['namespace_sources'])
            new_units = [scope_unit(*u) for u in units if scope_unit(*u) not in old_sources]
            if new_units:
                raise Refused('판 올림은 범위를 넓히지 않는다 — 새 단위 %s 는 --scope-add' % new_units)
            sources: dict = {scope_unit(*u): old_sources[scope_unit(*u)] for u in units}
            line_shas: dict = {s: h for s, h in previous['approval']['source_line_sha256'].items()
                               if s in sources.values()}
        else:
            sources = {scope_unit(*u): ns.approval_source for u in units}
            line_shas = {}
        if line_sha:
            line_shas[ns.approval_source] = line_sha
        approval = {'decision': 'approved', 'gate': gate, 'at': ns.approved_at, 'source': ns.approval_source,
                    'namespace_sources': sources, 'source_line_sha256': line_shas,
                    'candidate_token': candidate.get('candidate_token'), 'build': build}
        kind_label: str = '판 올림' if ns.replace else ('기존 SDK 등록' if ns.register_existing else '새 SDK 채택')
        banner.append('%s: %s %s · 표지 %s · 운영자 %s(%s)' % (
            kind_label, sid, candidate.get('version'), candidate.get('candidate_token'), entry.get('operator'),
            '·'.join(entry.get('operator_domains') or [])))
        banner.append('  · 원본 %s · 운영자 문서 인용 확인(docs.html sha256 %s · %s)' % (
            candidate.get('source_url'), str(candidate['evidence']['docs_sha256'])[:12],
            candidate['evidence']['fetched_from']))
        banner.append('  · 무결성: %s · 지문 sha256 %s · %s B · %s' % (
            '운영자 문서 공개 %s 와 일치' % str(candidate.get('upstream_integrity')).split('-')[0]
            if candidate.get('upstream_integrity') else '운영자 공개 값 없음/문서 인용 미확인 — 다시 받은 바이트와 대조함'
            if candidate.get('provenance') != 'file-unverified' else '대조 못 함(%s)' % UNVERIFIED,
            str(candidate.get('sha256'))[:12], candidate.get('size'), entry.get('license')))
    entry['approval'] = dict(approval, binds={'entry_sha256': entry_sha256({k: v for k, v in entry.items()
                                                                              if k != 'approval'})})
    problems = validate_entry(sid, {k: v for k, v in entry.items() if k != 'approval'}, with_approval=False)
    for key in ('source_url', 'final_url'):
        reason = lib_cdn_reason(entry.get(key) or '')
        if reason:
            problems.append('%s 가 %s' % (key, reason))
    traps = trap_hits(sid, str(entry.get('name', '')), str(entry.get('file', '')).rsplit('/', 1)[-1],
                      str(entry.get('source_url', '')))
    if traps:
        problems.append('제외 범주 낱말 %s' % ', '.join(traps))
    own = {urlsplit(str(entry.get('source_url'))).hostname, urlsplit(str(entry.get('docs_url'))).hostname}
    if not [h for h in (entry.get('origins') or {}).get('operator_in_code', []) if h not in own]:
        problems.append('주석 밖 코드가 운영자 서비스 호스트를 부르지 않는다(O7)')
    if problems:
        raise Refused('항목 거절 — ' + ' · '.join(problems))
    if previous is not None and not ns.replace and not ns.scope_add:
        if canonical_bytes(entry) != canonical_bytes(previous):
            raise Refused('%s 는 이미 등재됐다 — 판 올림은 --replace · 범위 넓힘은 --scope-add' % sid)
        findings, _notes = verify_findings(root)
        for f in findings:
            print(f)
        print('[sdk] 이미 같은 항목 — %s(재실행 멱등 · 쓰기 0)' % sid)
        return EXIT_RED if findings else EXIT_OK
    # 배너 사실
    words_rows = _docs_counts(candidate_path.parent, entry.get('namespace_words') or {})
    if words_rows:
        banner.append('  · 낱말 표(운영자 문서 등장 수): ' + ' · '.join(words_rows))
    members = entry.get('namespace_members') or {}
    for nsname, table in sorted(members.items()):
        by: Dict[str, List[str]] = {}
        for fn, cls in sorted(table.items()):
            by.setdefault(cls, []).append(fn)
        banner.append('  · 분류 %s: %s' % (nsname, ' · '.join('%s %s' % (k, ','.join(v)) for k, v in sorted(by.items()))))
    banner.append('  · 함수 표 출처: %s%s' % (candidate.get('members_source'),
                                         '' if candidate.get('blocked_requests') is None
                                         else '(로컬 밖 요청 차단 %d건)' % candidate['blocked_requests']))
    tracked = _tracked_vendor(root)
    ids = set(sdks) | {sid}
    others = unregistered_units(root, ids, tracked)
    banner.append('  · 미등재 벤더 디렉터리: %s' % ('없음' if not others else '%d개 %s(이관 항목 — 입구 '
                                                  '/dddjango-web:refactor web/static/vendor)' % (len(others), ' · '.join(others))))
    for line in banner:
        print('[sdk] ' + line)
    for n in notes:
        print('[sdk] 알림 — %s' % n)
    if ns.dry_run:
        print('[sdk] dry-run — 쓰지 않았다 · 결속 %s' % entry['approval']['binds']['entry_sha256'][:12])
        return EXIT_OK
    # 쓰기 + 자가 검사(실패면 되돌림)
    sdks[sid] = entry
    new_registry: bytes = canonical_bytes({'schema': SCHEMA, 'sdks': sdks})
    web: Path = root / 'web'
    id_dir: Path = web / VENDOR_DIR / sid
    with tempfile.TemporaryDirectory() as tmp:
        saved: Dict[Path, Optional[bytes]] = {p: (p.read_bytes() if p.is_file() and not p.is_symlink() else None)
                                              for p in (web / SDK_REGISTRY, web / VENDOR_ATTRS)}
        id_link: Optional[str] = os.readlink(id_dir) if id_dir.is_symlink() else None
        id_copy: Optional[Path] = None
        if id_link is None and id_dir.is_dir():
            id_copy = Path(tmp) / 'id'
            shutil.copytree(id_dir, id_copy, symlinks=True)
        try:
            write_bytes(web / SDK_REGISTRY, new_registry)
            write_bytes(web / VENDOR_ATTRS, VENDOR_ATTRS_BYTES)
            if data_bytes is not None:
                if id_dir.is_symlink():
                    id_dir.unlink()
                write_bytes(web / entry['file'], data_bytes)
                if ns.replace:
                    for child in sorted(id_dir.iterdir()):
                        if child.name != Path(entry['file']).name:
                            if child.is_dir() and not child.is_symlink():
                                shutil.rmtree(child)
                            else:
                                child.unlink()
            findings, verify_notes = verify_findings(root)
        except VendorUndecidable as error:
            findings, verify_notes = ['판정 불가 — %s' % error], []
        if findings:
            for p, data in saved.items():
                if data is None:
                    if p.exists() or p.is_symlink():
                        p.unlink()
                else:
                    write_bytes(p, data)
            if id_dir.is_symlink():
                id_dir.unlink()
            elif id_dir.is_dir():
                shutil.rmtree(id_dir)
            if id_link is not None:
                os.symlink(id_link, id_dir)
            elif id_copy is not None:
                shutil.copytree(id_copy, id_dir, symlinks=True)
            vendor: Path = web / VENDOR_DIR
            if vendor.is_dir() and not any(vendor.iterdir()):
                vendor.rmdir()
            for f in findings:
                print(f)
            print('[sdk] install 되돌림 — 자가 verify 실패(%d건)' % len(findings))
            return EXIT_RED
    for n in verify_notes:
        print(n)
    print('[sdk] 설치 %s · 결속 %s · 격리 커밋 `chore(web-sdk): %s %s 설치 — %s %s` 에 목록·vendor/%s/·vendor/.gitattributes 만'
          % (sid, entry['approval']['binds']['entry_sha256'][:12], sid, entry.get('version'), gate, ns.approved_at, sid))
    return EXIT_OK


# ------------------------------------------------------------------ verify · restore · remove


def cmd_verify(ns: argparse.Namespace) -> int:
    root: Path = Path(ns.root).resolve()
    if not (root / 'web').is_dir():
        raise UsageError('web/ 없음 — %s' % root)
    try:
        findings, notes = verify_findings(root)
    except VendorUndecidable as error:
        print('[sdk] verify 판정 불가(미실행 — 통과가 아니다) — %s' % error)
        return EXIT_ERR
    for n in notes:
        print(n)
    for f in findings:
        print(f)
        print()
    print('[sdk] verify — 늘 검사 WV1~WV6·WV13 발견 %d건' % len(findings))
    return EXIT_RED if findings else EXIT_OK


def cmd_restore(ns: argparse.Namespace) -> int:
    root: Path = Path(ns.root).resolve()
    path: Path = root / 'web' / SDK_REGISTRY
    registry = read_registry(root)
    if registry is None or ns.id not in registry['sdks']:
        raise Refused('%s 가 등재되지 않았다' % ns.id)
    entry: dict = registry['sdks'][ns.id]
    canonical: bytes = canonical_bytes(registry)
    if path.read_bytes() != canonical:
        write_bytes(path, canonical)
        print('[sdk] ⓡ2 목록 재정규화(내용 같음 · 바이트 꼴만)')
    attrs: Path = root / 'web' / VENDOR_ATTRS
    if attrs.is_symlink() or not attrs.is_file() or attrs.read_bytes() != VENDOR_ATTRS_BYTES:
        write_bytes(attrs, VENDOR_ATTRS_BYTES)
        print('[sdk] ⓡ3 vendor 표지 재기록')
    target: Path = root / 'web' / str(entry.get('file'))
    current_ok: bool = (target.is_file() and not target.is_symlink() and not target.parent.is_symlink()
                        and hashlib.sha256(target.read_bytes()).hexdigest() == entry.get('sha256'))
    if not current_ok:
        try:
            _final, _ctype, data = fetch(str(entry.get('source_url')))
        except (urllib.error.URLError, OSError, ValueError) as error:
            raise Refused('원본을 다시 받을 수 없다 — %s(판 올림(G1)·제거·정지)' % error)
        integrity = entry.get('upstream_integrity')
        if hashlib.sha256(data).hexdigest() != entry.get('sha256') or (
                isinstance(integrity, str) and sri(data, integrity.split('-', 1)[0]) != integrity):
            raise Refused('다시 받은 바이트가 등재 지문과 다르다 — 승인 불요 복원 불가(판 올림(G1)·제거·정지)')
        if target.parent.is_symlink():
            target.parent.unlink()
        write_bytes(target, data)
        print('[sdk] ⓡ1 등재 바이트 복원 — %s' % entry.get('file'))
    try:
        findings, notes = verify_findings(root)
    except VendorUndecidable as error:
        print('[sdk] 복원 뒤 verify 판정 불가 — %s' % error)
        return EXIT_ERR
    for f in findings:
        print(f)
    print('[sdk] restore %s — 남은 늘 검사 발견 %d건' % (ns.id, len(findings)))
    return EXIT_RED if findings else EXIT_OK


def cmd_remove(ns: argparse.Namespace) -> int:
    root: Path = Path(ns.root).resolve()
    registry = read_registry(root)
    if registry is None or ns.id not in registry['sdks']:
        raise Refused('%s 가 등재되지 않았다' % ns.id)
    needle: str = 'vendor/%s/' % ns.id
    result = subprocess.run(['git', '-C', str(root), 'grep', '--untracked', '-n', '-F', '-e', needle, '--', '*.html'],
                            capture_output=True)
    if result.returncode not in (0, 1):
        raise UsageError('저장소 템플릿 참조 조회 실패 — %s' % result.stderr.decode('utf-8', 'replace').strip())
    hits: List[str] = [h for h in result.stdout.decode('utf-8', 'replace').splitlines() if h]
    if hits:
        for h in hits[:20]:
            print('  참조: %s' % h)
        raise Refused('저장소 템플릿이 아직 %s 를 가리킨다(%d줄) — 참조를 먼저 없앤다' % (ns.id, len(hits)))
    del registry['sdks'][ns.id]
    web: Path = root / 'web'
    id_dir: Path = web / VENDOR_DIR / ns.id
    if id_dir.is_symlink():
        id_dir.unlink()
    elif id_dir.is_dir():
        shutil.rmtree(id_dir)
    if registry['sdks']:
        write_bytes(web / SDK_REGISTRY, canonical_bytes(registry))
    else:
        (web / SDK_REGISTRY).unlink()
        attrs: Path = web / VENDOR_ATTRS
        if attrs.exists() or attrs.is_symlink():
            attrs.unlink()
        vendor: Path = web / VENDOR_DIR
        if vendor.is_dir() and not any(vendor.iterdir()):
            vendor.rmdir()
    print('[sdk] 제거 %s — 항목과 vendor/%s/ 를 함께 지웠다%s' % (ns.id, ns.id, '' if registry['sdks'] else
                                                              ' · 마지막 항목이라 목록·표지도 지웠다'))
    return EXIT_OK


# ------------------------------------------------------------------ main


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog='sdk_vendor.py', description='dddjango-web 공식 플랫폼 SDK 등재 도구')
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('candidate')
    p.add_argument('root')
    p.add_argument('--id', required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--source-url', required=True)
    p.add_argument('--docs-url', required=True)
    p.add_argument('--from-file')
    p.add_argument('--docs-file')
    p.add_argument('--members-file')
    p.add_argument('--out', required=True)
    p = sub.add_parser('install')
    p.add_argument('root')
    p.add_argument('candidate')
    p.add_argument('--entry', required=True)
    p.add_argument('--approval-source', required=True)
    p.add_argument('--source-tokens')
    p.add_argument('--approved-at', required=True)
    p.add_argument('--gate', required=True)
    p.add_argument('--build', required=True)
    group = p.add_mutually_exclusive_group()
    group.add_argument('--replace', action='store_true')
    group.add_argument('--scope-add', nargs='+')
    group.add_argument('--register-existing')
    p.add_argument('--dry-run', action='store_true')
    for name in ('verify',):
        sub.add_parser(name).add_argument('root')
    for name in ('restore', 'remove'):
        p = sub.add_parser(name)
        p.add_argument('root')
        p.add_argument('id')
    try:
        ns = ap.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if exc.code == 0 else EXIT_ERR
    handlers = {'candidate': cmd_candidate, 'install': cmd_install, 'verify': cmd_verify,
                'restore': cmd_restore, 'remove': cmd_remove}
    try:
        return handlers[ns.command](ns)
    except UsageError as error:
        print('[sdk] 사용·입력 오류 — %s' % error)
        return EXIT_ERR
    except Refused as error:
        print('[sdk] 거절 — %s' % error)
        return EXIT_RED
    except (OSError, RegistryError, KeyError, TypeError) as error:
        print('[sdk] 실행 불능 — %s: %s' % (type(error).__name__, error))
        return EXIT_ERR


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
