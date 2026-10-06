# 공식 플랫폼 SDK 등재 목록 — 엄격 적재 · 정규 바이트 · 스키마(WV1) · 사본 바이트(WV2) · 결속·출처(WV3) ·
# 공식성 덫(WV4) · 함수 이름 바닥·경로 바닥 (값 정본: discipline-houserules §9).
#
# 쓰기는 NFC, 비교는 정규화 뒤 — 공용 정규화 함수 없이 비교하는 자리에서 unicodedata.normalize 를 직접 부른다.
# 등재 목록은 web/ 안 `sdk_registry.json` 하나다. 바이트는 정규 직렬화와 같아야 한다(손 편집·중복 키·병합 잔재가
# 한 번에 드러난다).
# (바탕: dddjango-web v1.3.1 src/sdk_registry.py — 경로·규칙 그대로. 등재 상수는 common 이 아니라 이 모듈이 갖고,
#  백스톱 컨텍스트에 붙이던 등재 상태는 `sdk_state(ctx)` 가 한 번 적재해 둔다)

import base64
import hashlib
import json
import os
import re
import stat
import subprocess
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit

from .common import mask_js

# houserules §9 — 공식 플랫폼 SDK 등재(web-상대 경로)
SDK_REGISTRY: str = 'sdk_registry.json'
VENDOR_DIR: str = 'static/vendor'
VENDOR_ATTRS: str = 'static/vendor/.gitattributes'
VENDOR_ATTRS_BYTES: bytes = b'* -text -diff -filter -ident -eol -working-tree-encoding\n'
# §9 자격 ② — 라이브러리 배포용 공용 CDN(운영자 소유여도 거절) · 공용 호스팅 접미사(단독 운영자 도메인 거절)
LIB_CDN_HOSTS: Set[str] = {'cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'unpkg.com', 'code.jquery.com',
                           'cdn.skypack.dev', 'esm.sh', 'ga.jspm.io', 'cdn.statically.io',
                           'raw.githubusercontent.com', 'rawcdn.githack.com'}
LIB_CDN_HOST_SUFFIXES: Tuple[str, ...] = ('.github.io',)
LIB_CDN_PATHS: Tuple[str, ...] = ('/ajax/libs/',)
HOSTING_SUFFIXES: Set[str] = {'cloudfront.net', 'amazonaws.com', 'vercel.app', 'pages.dev', 'netlify.app',
                              'azureedge.net', 'github.io', 'herokuapp.com', 'appspot.com', 'web.app',
                              'firebaseapp.com'}
# §9 제외 범주의 낱말 덫(영숫자 밖 문자로 자른 정확 토큰 · 구분자를 지운 결합형) — 덫일 뿐 보증이 아니다
TRAP_TOKENS: Set[str] = {'html2canvas', 'domtoimage', 'htmltoimage', 'modernscreenshot', 'jquery', 'react',
                         'reactdom', 'preact', 'vue', 'vuejs', 'angular', 'svelte', 'alpine', 'alpinejs', 'lit',
                         'stimulus', 'bootstrap', 'tailwind', 'tailwindcss', 'htmx', 'hyperscript', 'lodash',
                         'underscore', 'axios', 'moment', 'dayjs', 'chart', 'chartjs', 'echarts', 'd3',
                         'highcharts', 'plotly', 'apexcharts', 'gsap', 'animejs', 'lottie', 'threejs',
                         'swiper', 'polyfill', 'polyfills', 'corejs', 'requirejs', 'systemjs', 'zepto'}
# §9 공개 설정 이름에 쓰지 않는 낱말(공개 흐름으로 HTML 에 나간다 — JavaScript 키만)
SECRET_WORDS: Tuple[str, ...] = ('SECRET', 'PASSWORD', 'PRIVATE', 'TOKEN', 'ADMIN', 'CLIENT_SECRET')
# §9 OS 잡파일 — 미추적이거나 무시된 것만 세지 않는다(추적되면 발견)
OS_JUNK_NAMES: Set[str] = {'.DS_Store', 'Thumbs.db', 'desktop.ini', 'Icon\r'}


def is_os_junk_name(name: str) -> bool:
    return name in OS_JUNK_NAMES or name.startswith('._')


SCHEMA: str = 'dddjango-web-sdk-registry/2'
ID_RE = re.compile(r'^[a-z][a-z0-9_]*$')
FILE_NAME_RE = re.compile(r'^[a-z0-9_]+(\.[a-z0-9]+)+$')          # 소문자·숫자·밑줄 + 점 확장자(.min.js 포함)
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
SRI_RE = re.compile(r'^sha(256|384|512)-[A-Za-z0-9+/]+={0,2}$')
IDENT_RE = re.compile(r'^[A-Za-z_$][A-Za-z0-9_$]*$')
SETTING_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
ATTR_RE = re.compile(r'^data-[a-z0-9]+(?:-[a-z0-9]+)*$')
AT_RE = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2} [+-]\d{4}$')
SELF_RE = re.compile(r'^본인 직접\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4})\)$')
USER_RE = re.compile(r'^사용자 원문 (?P<path>.+)@(?P<commit>[0-9a-f]{7,40}):(?P<line>[1-9][0-9]*)'
                     r'\((?P<time>[^()]+)\)$')
BUILD_RE = re.compile(r'^\.dddjango-web/[^/]+/$')
API_PATH_RE = re.compile(r'^/[A-Za-z0-9_.~\-]+(?:/[A-Za-z0-9_.~\-]+)*$')
GATES: Tuple[str, ...] = ('G1', "G1'", 'G1(리팩토링)')
CLASSES: Tuple[str, ...] = ('call', 'lifecycle', 'data_out', 'gateway', 'sdk_ui')
RANK: Dict[str, int] = {'call': 1, 'lifecycle': 1, 'data_out': 2, 'gateway': 3, 'sdk_ui': 4}
PATH_CLASSES: Tuple[str, ...] = ('read', 'data_out')
CORE_UNIT: str = '(core)'
PUBLIC_SUFFIXES: Set[str] = {
    'com', 'net', 'org', 'io', 'dev', 'app', 'co', 'kr', 'jp', 'cn', 'uk', 'de', 'me', 'xyz', 'cloud',
    'co.kr', 'or.kr', 'go.kr', 'ne.kr', 'ac.kr', 're.kr', 'pe.kr', 'co.jp', 'ne.jp', 'or.jp', 'ac.jp',
    'co.uk', 'org.uk', 'ac.uk', 'com.cn', 'net.cn', 'org.cn', 'com.au', 'com.tw'}

ENTRY_FIELDS: Set[str] = {
    'name', 'operator', 'operator_domains', 'service_api', 'use_scope', 'namespace_words',
    'namespace_members', 'gateway_paths', 'features_in_file', 'lifecycle', 'version', 'file', 'size',
    'sha256', 'upstream_integrity', 'source_url', 'final_url', 'docs_url', 'evidence', 'license',
    'terms_url', 'origins', 'public_config', 'approval'}
OPTIONAL_FIELDS: Set[str] = {'gateway_paths'}
# 칸의 쓰는 쪽 — 도구(candidate) · Coordinator 판단(entry-draft)
TOOL_FIELDS: Tuple[str, ...] = ('version', 'source_url', 'docs_url', 'file', 'size', 'sha256',
                                'upstream_integrity', 'final_url', 'evidence', 'features_in_file')
DRAFT_FIELDS: Set[str] = {'name', 'operator', 'operator_domains', 'service_api', 'use_scope', 'namespace_words',
                          'namespace_members', 'gateway_paths', 'lifecycle', 'license', 'terms_url',
                          'public_config'}
APPROVAL_FIELDS: Set[str] = {'decision', 'gate', 'at', 'source', 'namespace_sources', 'source_line_sha256',
                             'candidate_token', 'build', 'binds'}

# 함수 이름 바닥(camelCase·`_` 토큰 대조) · 경로 바닥
_DATA_TOKENS: Set[str] = {'upload', 'delete', 'remove', 'store', 'save', 'put', 'unlink', 'revoke'}
_DATA_END: Set[str] = {'image', 'file', 'files', 'photo'}
_UI_END: Set[str] = {'button', 'widget'}
_UI_START: Set[str] = {'render', 'mount', 'draw'}
_LIFE_NAMES: Set[str] = {'cleanup', 'destroy', 'dispose', 'teardown'}
_GATE_NAMES: Set[str] = {'request', 'invoke', 'fetch', 'call', 'ajax'}
_PATH_FLOOR: Set[str] = {'send', 'upload', 'delete', 'unlink', 'revoke', 'scrap', 'update', 'logout', 'signup',
                         'set', 'save', 'store', 'write'}
# 운영자·제품 낱말에서 빼는 일반 낱말(승인 원문이 «그 SDK» 를 가리키려면 운영자·제품 고유 낱말이 있어야 한다)
_STOP_WORDS: Set[str] = {'for', 'the', 'and', 'of', 'by', 'inc', 'corp', 'corporation', 'co', 'ltd', 'llc',
                         'limited', 'company', 'sdk', 'js', 'javascript', 'api', 'client', 'library', 'lib',
                         'web', 'plugin', 'kit'}
_WORD_SPLIT = re.compile(r'[^\w]+')
_HTTPS_HOST_RE = re.compile(r'https:(?:\\?/){2}([A-Za-z0-9](?:[A-Za-z0-9.\-]*[A-Za-z0-9])?)')


class RegistryError(ValueError):
    """목록·입력 JSON 을 엄격 규칙으로 읽을 수 없다."""


# ------------------------------------------------------------------ 엄격 적재 · 정규 바이트


def _no_dup(pairs: List[Tuple[str, object]]) -> dict:
    seen: dict = {}
    for key, value in pairs:
        if key in seen:
            raise RegistryError('중복 키 %r' % key)
        seen[key] = value
    return seen


def _no_constant(token: str) -> object:
    raise RegistryError('비유한 수 %s' % token)


def _no_float(token: str) -> object:
    raise RegistryError('실수 값 %s — 정수·문자열만 쓴다' % token)


def strict_loads(raw: bytes) -> object:
    try:
        text: str = raw.decode('utf-8')
    except UnicodeDecodeError as error:
        raise RegistryError('UTF-8 아님 — %s' % error)
    try:
        return json.loads(text, object_pairs_hook=_no_dup, parse_constant=_no_constant, parse_float=_no_float)
    except RegistryError:
        raise
    except ValueError as error:
        raise RegistryError('JSON 파싱 실패 — %s' % error)


def nfc_value(value: object) -> object:
    """문자열(키 포함)을 NFC 로 — 키가 정규화로 합쳐지면 오류다(두 꼴의 같은 키)."""
    if isinstance(value, str):
        return unicodedata.normalize('NFC', value)
    if isinstance(value, list):
        return [nfc_value(v) for v in value]
    if isinstance(value, dict):
        out: dict = {}
        for k, v in value.items():
            nk = unicodedata.normalize('NFC', k) if isinstance(k, str) else k
            if nk in out:
                raise RegistryError('NFC 로 합쳐지는 키 %r' % k)
            out[nk] = nfc_value(v)
        return out
    return value


def canonical_bytes(data: object) -> bytes:
    return (json.dumps(nfc_value(data), ensure_ascii=False, indent=2, sort_keys=True,
                       separators=(',', ': ')) + '\n').encode('utf-8')


def entry_sha256(entry: dict) -> str:
    """승인 결속 — approval 을 뺀 항목의 정규 JSON(NFC) sha256."""
    body: dict = {k: v for k, v in entry.items() if k != 'approval'}
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sri(data: bytes, algorithm: str = 'sha384') -> str:
    return '%s-%s' % (algorithm, base64.b64encode(hashlib.new(algorithm, data).digest()).decode('ascii'))


def candidate_token(sdk_id: str, version: str, sha256: str) -> str:
    return '%s@%s#%s' % (sdk_id, version, sha256[:12])


# ------------------------------------------------------------------ 도메인


def host_of(url: str) -> Optional[str]:
    try:
        return urlsplit(url).hostname
    except ValueError:
        return None


def under(host: str, domains: List[str]) -> bool:
    """점 경계 하위 — `evilkakaocdn.net` 은 `kakaocdn.net` 아래가 아니다."""
    return any(host == d or host.endswith('.' + d) for d in domains)


def url_problems(url: object, label: str) -> List[str]:
    """https · userinfo/port/대문자/끝점/비ASCII 거절 · 라벨 둘 이상."""
    if not isinstance(url, str) or not url:
        return ['%s 가 문자열이 아니다' % label]
    try:
        parts = urlsplit(url)
    except ValueError as error:
        return ['%s 해석 불가 — %s' % (label, error)]
    out: List[str] = []
    if parts.scheme != 'https':
        out.append('%s 는 https 여야 한다 — %s' % (label, url))
    netloc: str = parts.netloc
    if '@' in netloc:
        out.append('%s 에 userinfo — %s' % (label, url))
    if ':' in netloc.rsplit('@', 1)[-1]:
        out.append('%s 에 포트 — %s' % (label, url))
    host: str = netloc.rsplit('@', 1)[-1].split(':', 1)[0]
    if not host.isascii():
        out.append('%s 호스트가 비ASCII — %s' % (label, url))
    if host != host.lower():
        out.append('%s 호스트에 대문자 — %s' % (label, url))
    if host.endswith('.'):
        out.append('%s 호스트가 점으로 끝난다 — %s' % (label, url))
    if host.count('.') < 1:
        out.append('%s 호스트 라벨이 하나뿐 — %s' % (label, url))
    return out


def lib_cdn_reason(url: str) -> Optional[str]:
    host: str = (host_of(url) or '').lower()
    path: str = urlsplit(url).path if isinstance(url, str) else ''
    if host in LIB_CDN_HOSTS or any(host.endswith(s) for s in LIB_CDN_HOST_SUFFIXES):
        return '라이브러리 공용 CDN 호스트 %s' % host
    if any(p in path for p in LIB_CDN_PATHS):
        return '라이브러리 공용 CDN 경로 %s' % path
    return None


def https_hosts(text: str) -> Set[str]:
    return {m.group(1).lower().rstrip('.') for m in _HTTPS_HOST_RE.finditer(text)}


def compute_origins(data: bytes, domains: List[str]) -> dict:
    """사본 안 https 호스트 전수 — 운영자 도메인 하위면 operator, 아니면 other · 주석 밖 코드의 운영자 호스트."""
    text: str = data.decode('utf-8', 'replace')
    every: Set[str] = https_hosts(text)
    code: Set[str] = https_hosts(mask_js(text).no_comments)
    operator: List[str] = sorted(h for h in every if under(h, domains))
    return {'operator': operator, 'operator_in_code': sorted(h for h in code if under(h, domains)),
            'other': sorted(every - set(operator))}


_HTTPS_URL_RE = re.compile(r'https:(?:\\?/){2}([A-Za-z0-9](?:[A-Za-z0-9.\-]*[A-Za-z0-9])?)((?:\\?/[\w.~%!$&*+,;=:@\-]*)*)')


def _own_prefixes(entry: dict) -> Dict[str, List[str]]:
    """배포·문서 자원의 경로 접두 — 호스트 → [그 자원 경로 · 경로/ · 자원 폴더/(루트 폴더 제외)]."""
    out: Dict[str, List[str]] = {}
    for key in ('source_url', 'final_url', 'docs_url'):
        value = entry.get(key)
        if not isinstance(value, str):
            continue
        host: str = (host_of(value) or '').lower()
        path: str = urlsplit(value).path
        folder: str = path.rsplit('/', 1)[0] + '/'
        out.setdefault(host, []).extend([path, path.rstrip('/') + '/'] + ([folder] if folder != '/' else []))
    return out


def service_hosts(entry: dict, data: Optional[bytes]) -> List[str]:
    """O7 — 주석 밖 코드가 부르는 운영자 서비스 호스트. 배포·문서 자원의 호스트라도 그 자원 경로·폴더 밖의 경로를 부르면
    서비스다(같은 호스트에 사본·문서·서비스 API 가 함께 있는 운영자). 그 호스트의 경로 없는 주소(`https://<호스트>`)는 자원과
    서비스를 가를 수 없어 세지 않는다. data 가 없으면(사본을 읽지 못함) 배포·문서 밖 호스트만 센다."""
    origins = entry.get('origins') if isinstance(entry.get('origins'), dict) else {}
    in_code: Set[str] = {h for h in origins.get('operator_in_code') or [] if isinstance(h, str)}
    own: Dict[str, List[str]] = _own_prefixes(entry)
    found: Set[str] = {h for h in in_code if h not in own}
    if data is not None:
        code: str = mask_js(data.decode('utf-8', 'replace')).no_comments
        for m in _HTTPS_URL_RE.finditer(code):
            host: str = m.group(1).lower().rstrip('.')
            path: str = m.group(2).replace('\\/', '/')
            if host not in own or host not in in_code:
                continue
            resource: bool = path in ('', '/') or any(path == p or (p.endswith('/') and path.startswith(p))
                                                      for p in own[host])
            if not resource:
                found.add(host)
    return sorted(found)


# ------------------------------------------------------------------ 바닥 · 낱말


def name_tokens(name: str) -> List[str]:
    return [t.lower() for t in re.split(r'(?<=[a-z0-9])(?=[A-Z])|_', name) if t]


def name_floor(name: str) -> str:
    tokens: List[str] = name_tokens(name) or [name.lower()]
    if tokens[-1] in _UI_END or tokens[0] in _UI_START:
        return 'sdk_ui'
    if name in _GATE_NAMES:
        return 'gateway'
    if set(tokens) & _DATA_TOKENS or tokens[-1] in _DATA_END:
        return 'data_out'
    if name in _LIFE_NAMES:
        return 'lifecycle'
    return 'call'


def path_floor(path: str) -> str:
    return 'data_out' if set(t.lower() for t in re.split(r'[/_]', path)) & _PATH_FLOOR else 'read'


def word_tokens(text: str) -> List[str]:
    return [t for t in _WORD_SPLIT.split(unicodedata.normalize('NFC', text).casefold()) if t]


def product_tokens(entry: dict) -> Set[str]:
    out: Set[str] = set()
    for key in ('operator', 'name'):
        value = entry.get(key)
        if isinstance(value, str):
            out.update(word_tokens(value))
    return out


def operator_words(entry: dict) -> List[str]:
    """승인 원문이 담아야 할 운영자·제품 낱말 — operator·name 의 고유 낱말(일반 낱말·한 글자·숫자 제외)."""
    return sorted(t for t in product_tokens(entry)
                  if len(t) >= 2 and not t.isdigit() and t not in _STOP_WORDS)


def trap_hits(*texts: str) -> List[str]:
    """제외 범주 낱말 덫 — 정확 토큰과 이웃 토큰을 이어 붙인 결합형(2~4)."""
    hits: Set[str] = set()
    for text in texts:
        tokens: List[str] = [t for t in re.split(r'[^a-z0-9]+', text.lower()) if t]
        for n in range(1, 5):
            for i in range(len(tokens) - n + 1):
                joined: str = ''.join(tokens[i:i + n])
                if joined in TRAP_TOKENS:
                    hits.add(joined)
    return sorted(hits)


# ------------------------------------------------------------------ 범위 원소


def parse_scope_item(item: str, global_name: str) -> Optional[Tuple[str, str, str, str]]:
    """use_scope 원소 → (종류, 이름공간, 함수, 경로) — 종류 core|bundle|named|gateway. 꼴이 아니면 None."""
    if not isinstance(item, str) or not item.startswith(global_name + '.'):
        return None
    rest: str = item[len(global_name) + 1:]
    path: str = ''
    if ':' in rest:
        rest, path = rest.split(':', 1)
        if not path:
            return None
    parts: List[str] = rest.split('.')
    if len(parts) == 1 and not path and IDENT_RE.match(parts[0]):
        return ('core', '', parts[0], '')
    if len(parts) == 2 and IDENT_RE.match(parts[0]):
        if parts[1] == '*' and not path:
            return ('bundle', parts[0], '*', '')
        if IDENT_RE.match(parts[1]):
            return ('gateway' if path else 'named', parts[0], parts[1], path)
    return None


def scope_unit(kind: str, ns: str, fn: str, path: str) -> str:
    """namespace_sources 의 단위 이름."""
    if kind == 'core':
        return CORE_UNIT
    if kind == 'bundle':
        return ns
    if kind == 'named':
        return '%s.%s' % (ns, fn)
    return '%s.%s:%s' % (ns, fn, path)


def scope_units(entry: dict) -> List[str]:
    global_name: str = (entry.get('lifecycle') or {}).get('global', '') if isinstance(entry.get('lifecycle'), dict) else ''
    units: List[str] = []
    for item in entry.get('use_scope') or []:
        parsed = parse_scope_item(item, global_name)
        if parsed is not None:
            unit: str = scope_unit(*parsed)
            if unit not in units:
                units.append(unit)
    return units


_GW_SCHEME = re.compile(r'^[A-Za-z][A-Za-z0-9+.\-]*:')
_GW_HOST = re.compile(r'[a-z0-9.\-]+')
_GW_PCT = re.compile(r'%([0-9A-Fa-f]{2})')
_GW_UNRESERVED: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'


def normalize_gateway_url(url: str, domains: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """gateway url 정규형 — (정규 경로, 문제). 브라우저 스니펫(assets/sdk_boundary.js `normPath`)과 글자 단위로 같은
    규칙이다(URL 파서의 해석 차이 — 앞 공백·역슬래시·점 조각 — 에 기대지 않는다):
    ① 문자열 전체가 출력 가능한 ASCII(`!`~`~`)이고 역슬래시가 없다(공백·제어문자·비ASCII·`\\` 는 거절)
    ② 스킴이 있거나 `//` 로 시작하면 `https://<호스트>` 꼴만 — 호스트는 소문자로 바꾼 뒤 `[a-z0-9.-]` 만(userinfo·포트
       거절)이고 운영자 도메인의 점 경계 하위여야 한다. 그 뒤가 경로다(비면 `/`)
    ③ 그 밖은 `/` 로 시작하는 상대 경로만
    ④ 쿼리·조각(`?`·`#` 뒤)을 떼고 `%XX` 를 푼다 — 비예약 문자(영숫자·`-._~`)로 풀리는 것만 받는다
    ⑤ 끝 `/` 를 떼고(비면 `/`) 빈 조각·`.`·`..` 조각은 거절 ⑥ 소문자."""
    if not isinstance(url, str) or not url:
        return None, 'url 이 문자열이 아니다'
    if any(not ('!' <= c <= '~') or c == '\\' for c in url):
        return None, '공백·제어문자·비ASCII·역슬래시가 든 url %r' % url
    rest: str = url
    if _GW_SCHEME.match(url) or url.startswith('//'):
        if url[:8].lower() != 'https://':
            return None, '운영자 호스트가 아닌 절대 주소 %s(https 가 아니다)' % url
        after: str = url[8:]
        cut: int = len(after)
        for ch in '/?#':
            k: int = after.find(ch)
            if k >= 0:
                cut = min(cut, k)
        host: str = after[:cut].lower()
        if not _GW_HOST.fullmatch(host) or not under(host, domains):
            return None, '운영자 호스트가 아닌 절대 주소 %s' % url
        rest = after[cut:]
        if not rest.startswith('/'):
            rest = '/' + rest
    elif not url.startswith('/'):
        return None, '경로가 `/` 로 시작하지 않는다 — %s' % url
    path: str = re.split(r'[?#]', rest, maxsplit=1)[0]
    if re.search(r'%(?![0-9A-Fa-f]{2})', path) or any(
            chr(int(m.group(1), 16)) not in _GW_UNRESERVED for m in _GW_PCT.finditer(path)):
        return None, '퍼센트 인코딩이 비예약 문자(영숫자·-._~)가 아니다 — %s' % url
    path = _GW_PCT.sub(lambda m: chr(int(m.group(1), 16)), path).rstrip('/')
    if any(seg in ('', '.', '..') for seg in path.split('/')[1:]):
        return None, '빈 조각·점 조각(. ..)이 든 경로 — %s' % url
    return (path or '/').lower(), None


# ------------------------------------------------------------------ WV1 스키마


def _is_str_list(value: object, nonempty: bool = False) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) for x in value) and (bool(value) or not nonempty)


def validate_registry(data: object) -> List[Tuple[str, str]]:
    """목록 전체 스키마 — [(항목 id 또는 '', 문제)]."""
    out: List[Tuple[str, str]] = []
    if not isinstance(data, dict):
        return [('', '최상위가 객체가 아니다')]
    unknown = sorted(set(data) - {'schema', 'sdks'})
    if unknown:
        out.append(('', '모르는 최상위 칸 %s' % unknown))
    if data.get('schema') != SCHEMA:
        out.append(('', 'schema 가 %s 가 아니다 — %r' % (SCHEMA, data.get('schema'))))
    sdks = data.get('sdks')
    if not isinstance(sdks, dict) or not sdks:
        out.append(('', 'sdks 가 비지 않은 객체가 아니다'))
        return out
    files: Dict[str, str] = {}
    for sdk_id, entry in sdks.items():
        for problem in validate_entry(sdk_id, entry):
            out.append((sdk_id, problem))
        if isinstance(entry, dict) and isinstance(entry.get('file'), str):
            other = files.get(entry['file'])
            if other is not None:
                out.append((sdk_id, '두 항목이 같은 file — %s·%s' % (other, sdk_id)))
            files[entry['file']] = sdk_id
    return out


def validate_entry(sdk_id: str, entry: object, with_approval: bool = True) -> List[str]:
    out: List[str] = []
    if not ID_RE.match(sdk_id or ''):
        out.append('id 꼴 `[a-z][a-z0-9_]*` 위반 — %r' % sdk_id)
    if not isinstance(entry, dict):
        return out + ['항목이 객체가 아니다']
    fields: Set[str] = ENTRY_FIELDS if with_approval else ENTRY_FIELDS - {'approval'}
    unknown = sorted(set(entry) - fields)
    if unknown:
        out.append('모르는 칸 %s' % unknown)
    missing = sorted(fields - OPTIONAL_FIELDS - set(entry))
    if missing:
        out.append('필수 칸 없음 %s' % missing)
        return out
    for key in ('name', 'operator', 'service_api', 'version', 'license'):
        if not isinstance(entry[key], str) or not entry[key].strip():
            out.append('%s 가 비지 않은 문자열이 아니다' % key)
    # 파일
    file_value = entry['file']
    if not isinstance(file_value, str):
        out.append('file 이 문자열이 아니다')
    else:
        parts = file_value.split('/')
        if len(parts) != 4 or '/'.join(parts[:2]) != VENDOR_DIR or parts[2] != sdk_id:
            out.append('file 은 `static/vendor/<id>/<파일>` 이고 디렉터리가 id 여야 한다 — %s' % file_value)
        elif not FILE_NAME_RE.match(parts[3]):
            out.append('file 이름 꼴 위반(소문자·숫자·밑줄 + 점 확장자 — houserules §4 파일명 snake_case) — %s'
                       % parts[3])
    if type(entry['size']) is not int or entry['size'] <= 0:
        out.append('size 가 양의 정수가 아니다')
    if not isinstance(entry['sha256'], str) or not SHA256_RE.match(entry['sha256']):
        out.append('sha256 꼴 위반')
    integrity = entry['upstream_integrity']
    if integrity is not None and (not isinstance(integrity, str) or not SRI_RE.match(integrity)):
        out.append('upstream_integrity 꼴 위반(sha256/384/512-base64 또는 null)')
    # 운영자 도메인 · 주소
    domains = entry['operator_domains']
    if not _is_str_list(domains, nonempty=True):
        out.append('operator_domains 가 비지 않은 문자열 목록이 아니다')
        domains = []
    for d in domains:
        if d != d.lower() or not d.isascii() or d.startswith('.') or d.endswith('.') or d.count('.') < 1:
            out.append('operator_domains 꼴 위반(소문자 ASCII · 라벨 둘 이상 · 끝점 없음) — %s' % d)
        elif d in PUBLIC_SUFFIXES:
            out.append('operator_domains 가 공용 접미사 — %s' % d)
    for key in ('source_url', 'final_url', 'docs_url', 'terms_url'):
        problems = url_problems(entry[key], key)
        out.extend(problems)
        if key != 'terms_url' and not problems and domains:
            host = host_of(entry[key]) or ''
            if not under(host, domains):
                out.append('%s 호스트 %s 가 operator_domains 의 점 경계 하위가 아니다' % (key, host))
    # 증거
    evidence = entry['evidence']
    if not isinstance(evidence, dict) or set(evidence) != {'docs_sha256', 'cites_source', 'integrity_from_docs',
                                                           'fetched_from'}:
        out.append('evidence 칸 꼴 위반(docs_sha256·cites_source·integrity_from_docs·fetched_from)')
    else:
        if not isinstance(evidence['docs_sha256'], str) or not SHA256_RE.match(evidence['docs_sha256']):
            out.append('evidence.docs_sha256 꼴 위반')
        if evidence['cites_source'] is not True:
            out.append('evidence.cites_source 가 true 가 아니다 — 운영자 문서가 원본을 인용해야 한다')
        if not isinstance(evidence['integrity_from_docs'], bool):
            out.append('evidence.integrity_from_docs 가 bool 이 아니다')
        elif (integrity is not None) != evidence['integrity_from_docs']:
            out.append('upstream_integrity 는 운영자 문서에서 왔을 때만(integrity_from_docs) 채운다')
        if evidence['fetched_from'] not in ('network', 'file'):
            out.append('evidence.fetched_from 은 network|file')
    origins = entry['origins']
    if (not isinstance(origins, dict) or set(origins) != {'operator', 'operator_in_code', 'other'}
            or not all(_is_str_list(origins[k]) for k in origins)):
        out.append('origins 꼴 위반(operator·operator_in_code·other 문자열 목록)')
    elif not set(origins['operator_in_code']) <= set(origins['operator']):
        out.append('origins.operator_in_code 가 operator 의 부분이 아니다')
    # 기능 · 수명
    features = entry['features_in_file']
    if not _is_str_list(features) or not all(IDENT_RE.match(x) for x in features):
        out.append('features_in_file 이 식별자 목록이 아니다')
        features = []
    life = entry['lifecycle']
    global_name: str = ''
    if (not isinstance(life, dict) or set(life) != {'global', 'init', 'created_by_init'}
            or not isinstance(life.get('global'), str) or not IDENT_RE.match(life['global'])
            or not isinstance(life.get('init'), str) or not IDENT_RE.match(life['init'])
            or not _is_str_list(life.get('created_by_init'))):
        out.append('lifecycle 꼴 위반(global·init 식별자 · created_by_init 목록)')
    else:
        global_name = life['global']
        stray = sorted(set(life['created_by_init']) - set(features))
        if stray:
            out.append('lifecycle.created_by_init 이 features_in_file 밖 — %s' % stray)
    # 공개 설정
    config = entry['public_config']
    if not isinstance(config, list) or not all(isinstance(c, dict) for c in config):
        out.append('public_config 가 객체 목록이 아니다')
    else:
        for c in config:
            if set(c) != {'setting', 'attr', 'call'} or not all(isinstance(c[k], str) for k in c):
                out.append('public_config 원소 꼴 위반(setting·attr·call)')
                continue
            setting: str = c['setting']
            if not SETTING_RE.match(setting):
                out.append('public_config.setting 꼴 위반 — %s' % setting)
            words = setting.split('_')
            if any(w in SECRET_WORDS for w in words) or 'CLIENT_SECRET' in setting:
                out.append('public_config.setting 에 비밀 낱말 — %s(공개 흐름으로 HTML 에 나간다 · JavaScript 키만)'
                           % setting)
            if not ATTR_RE.match(c['attr']):
                out.append('public_config.attr 꼴 위반(data-<kebab>) — %s' % c['attr'])
            if global_name and life and c['call'] != '%s.%s' % (global_name, life['init']):
                out.append('public_config.call 은 `<global>.<init>` 이다 — %s' % c['call'])
    # 함수 분류 · 경로 분류
    members = entry['namespace_members']
    if not isinstance(members, dict) or not all(isinstance(t, dict) for t in members.values()):
        out.append('namespace_members 꼴 위반(이름공간 → {함수: 분류})')
        members = {}
    for ns, table in members.items():
        if ns not in features:
            out.append('namespace_members 이름공간 %s 가 features_in_file 밖' % ns)
        for fn, cls in table.items():
            if not IDENT_RE.match(fn) or cls not in CLASSES:
                out.append('namespace_members[%s] 원소 꼴 위반 — %s: %r' % (ns, fn, cls))
            elif RANK[cls] < RANK[name_floor(fn)]:
                out.append('namespace_members[%s].%s = %s — 이름 바닥 %s 보다 느슨하다' % (ns, fn, cls, name_floor(fn)))
    gateway_paths = entry.get('gateway_paths', {})
    if not isinstance(gateway_paths, dict) or not all(isinstance(t, dict) for t in gateway_paths.values()):
        out.append('gateway_paths 꼴 위반(<이름공간>.<함수> → {경로: read|data_out})')
        gateway_paths = {}
    for key, table in gateway_paths.items():
        ns, _dot, fn = key.partition('.')
        if (members.get(ns) or {}).get(fn) != 'gateway':
            out.append('gateway_paths 키 %s 가 분류표의 gateway 함수가 아니다' % key)
        for path, cls in table.items():
            if not isinstance(path, str) or not API_PATH_RE.match(path) or cls not in PATH_CLASSES:
                out.append('gateway_paths[%s] 원소 꼴 위반 — %r: %r' % (key, path, cls))
            elif cls == 'read' and path_floor(path) == 'data_out':
                out.append('gateway_paths[%s] %s = read — 경로 바닥 data_out 보다 느슨하다' % (key, path))
    # 범위
    scope = entry['use_scope']
    if not _is_str_list(scope, nonempty=True):
        out.append('use_scope 가 비지 않은 문자열 목록이 아니다')
        scope = []
    if len(set(scope)) != len(scope):
        out.append('use_scope 원소 중복')
    for item in scope:
        parsed = parse_scope_item(item, global_name) if global_name else None
        if parsed is None:
            out.append('use_scope 원소 꼴 위반 — %r(핵심 함수 · `<global>.<이름공간>.*` · data_out 이름 · '
                       'gateway `<함수>:<경로>`)' % item)
            continue
        kind, ns, fn, path = parsed
        if kind == 'core':
            if fn in features:
                out.append('use_scope %s — 이름공간은 `<global>.<이름공간>.*` 로 적는다' % item)
            continue
        if ns not in features:
            out.append('use_scope %s — 이름공간 %s 가 features_in_file 밖' % (item, ns))
            continue
        table = members.get(ns)
        if not isinstance(table, dict):
            out.append('use_scope %s — 이름공간 %s 의 분류표(namespace_members)가 없다' % (item, ns))
            continue
        if kind == 'bundle':
            classes = set(table.values())
            if 'gateway' in classes and 'call' not in classes:
                out.append('use_scope %s — gateway 이름공간 묶음 · gateway 는 `<함수>:<경로>` 원소로만 적는다' % item)
        elif kind == 'named':
            cls = table.get(fn)
            if cls == 'gateway':
                out.append('use_scope %s — gateway 함수는 `<함수>:<경로>` 원소로만 적는다' % item)
            elif cls == 'sdk_ui':
                out.append('use_scope %s — SDK 가 그리는 UI 함수는 어떤 승인으로도 쓰지 않는다' % item)
            elif cls != 'data_out':
                out.append('use_scope %s — 이름 지정 원소는 분류표의 data_out 함수만(지금 %s)' % (item, cls))
        else:
            if table.get(fn) != 'gateway':
                out.append('use_scope %s — %s 는 분류표의 gateway 함수가 아니다' % (item, fn))
            elif path not in (gateway_paths.get('%s.%s' % (ns, fn)) or {}):
                out.append('use_scope %s — 경로가 gateway_paths(api-paths) 밖' % item)
    # 낱말 표
    words = entry['namespace_words']
    if not isinstance(words, dict) or not all(_is_str_list(v, nonempty=True) for v in words.values()):
        out.append('namespace_words 꼴 위반(단위 → 비지 않은 낱말 목록)')
    else:
        uncovered = sorted(set(features) - set(words))
        if uncovered:
            out.append('namespace_words 가 features_in_file 을 다 덮지 않는다 — %s' % uncovered)
        product: Set[str] = product_tokens(entry)
        removable: Set[str] = product | _STOP_WORDS
        owner: Dict[str, str] = {}
        for unit, values in words.items():
            ns, _dot, fn = unit.partition('.')
            if ns not in features or (fn and (members.get(ns) or {}).get(fn) != 'data_out'):
                out.append('namespace_words 키 %s 는 이름공간 또는 이름 지정 data_out 단위여야 한다' % unit)
            for raw in values:
                w: str = unicodedata.normalize('NFC', raw).strip()
                low: str = w.casefold()
                if len(w) < 2:
                    out.append('namespace_words[%s] 낱말 %r 가 두 글자 미만' % (unit, raw))
                elif any(low == t or low in t for t in product):
                    out.append('namespace_words[%s] 낱말 %r 가 운영자·제품 낱말과 같거나 그 부분이다' % (unit, raw))
                elif not [t for t in word_tokens(low) if t not in removable]:
                    out.append('namespace_words[%s] 낱말 %r 에서 운영자·제품 낱말을 지우면 빈다' % (unit, raw))
                if low in owner and owner[low] != unit:
                    out.append('namespace_words 낱말 %r 가 두 단위(%s·%s)에 있다' % (raw, owner[low], unit))
                owner.setdefault(low, unit)
    return out


# ------------------------------------------------------------------ 출처(WV3 · install)


def parse_source(source: object) -> Optional[dict]:
    if not isinstance(source, str):
        return None
    m = SELF_RE.match(source)
    if m:
        return {'kind': 'self', 'time': m.group(1)}
    m = USER_RE.match(source)
    if m:
        return {'kind': 'user', 'path': m.group('path'), 'commit': m.group('commit'),
                'line': int(m.group('line')), 'time': m.group('time')}
    return None


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True)


def is_shallow(root: Path) -> bool:
    r = _git(root, 'rev-parse', '--is-shallow-repository')
    return r.returncode == 0 and r.stdout.decode().strip() == 'true'


def source_line(root: Path, info: dict) -> Tuple[Optional[bytes], List[str], List[str]]:
    """사용자 원문 출처의 그 행 원바이트(줄바꿈 제외) · 문제 · 알림.

    ① 커밋이 HEAD 의 조상 ② 경로가 저장소 상대 · web/·.dddjango-web/ 밖. 경로는 원문 그대로 기록하고 조회만 NFC."""
    problems: List[str] = []
    notes: List[str] = []
    raw_path: str = info['path']
    path: str = unicodedata.normalize('NFC', raw_path)
    parts: List[str] = path.split('/')
    if path.startswith('/') or '\\' in path or '..' in parts or not path:
        problems.append('원문 경로가 저장소 상대 경로가 아니다 — %s' % raw_path)
        return None, problems, notes
    if parts[0] in ('web', '.dddjango-web'):
        problems.append('원문 경로가 web/·.dddjango-web/ 안 — 화면 코드·빌드 기록 안 문장은 출처가 아니다(%s)'
                        % raw_path)
        return None, problems, notes
    r = _git(root, 'rev-parse', '--verify', '-q', info['commit'] + '^{commit}')
    if r.returncode != 0:
        problems.append('원문 커밋 %s 를 풀 수 없다' % info['commit'])
        return None, problems, notes
    commit: str = r.stdout.decode().strip()
    r = _git(root, 'merge-base', '--is-ancestor', commit, 'HEAD')
    if r.returncode == 1:
        if is_shallow(root):
            notes.append('원문 커밋 %s 조상 판정 불가 — 얕은 이력' % commit[:12])
        else:
            problems.append('원문 커밋 %s 가 HEAD 의 조상이 아니다(버린 가지·다른 가지)' % commit[:12])
    elif r.returncode != 0:
        problems.append('원문 커밋 조상 판정 실패 — %s' % r.stderr.decode('utf-8', 'replace').strip())
    r = _git(root, 'show', '%s:%s' % (commit, path))
    if r.returncode != 0:
        problems.append('원문 파일 %s 가 커밋 %s 에 없다' % (raw_path, commit[:12]))
        return None, problems, notes
    lines: List[bytes] = r.stdout.split(b'\n')
    if info['line'] > len(lines) or (info['line'] == len(lines) and lines[-1] == b''):
        problems.append('원문 %s 에 %d행이 없다' % (raw_path, info['line']))
        return None, problems, notes
    return lines[info['line'] - 1], problems, notes


def check_source(root: Path, source: str, groups: List[Tuple[str, List[str]]],
                 previous: Optional[str] = None, fetched_at: Optional[str] = None) -> Tuple[Optional[str], List[str], List[str]]:
    """승인 출처 검사 — (그 행 sha256(사용자 원문만) · 문제 · 알림). groups = [(이름, 낱말 후보…)] — 각 묶음에서
    낱말 하나 이상이 그 행에 있어야 한다(양쪽 NFC · 대소문자 무시). 본인 직접은 꼴만 본다."""
    info = parse_source(source)
    if info is None:
        return None, ['출처 꼴 위반 — «본인 직접(<YYYY-MM-DD HH:MM:SS +ZZZZ>)» 또는 «사용자 원문 <경로>@<커밋>:'
                      '<행>(<시각>)» 뿐이다(발주 고정·대리 답·게이트 위임·추론은 출처가 아니다): %s' % source], []
    problems: List[str] = []
    if previous is not None and unicodedata.normalize('NFC', source) == unicodedata.normalize('NFC', previous):
        problems.append('직전 승인과 같은 출처 — 판 올림은 새 판을 담은 새 원문이 필요하다')
    if info['kind'] == 'self':
        return None, problems, []
    raw, more, notes = source_line(root, info)
    problems += more
    if raw is None:
        return None, problems, notes
    text: str = unicodedata.normalize('NFC', raw.decode('utf-8', 'replace'))
    low: str = text.casefold()
    if unicodedata.normalize('NFC', info['time']) not in text:
        problems.append('원문 행에 시각 %r 가 없다' % info['time'])
    for label, candidates in groups:
        wanted = [unicodedata.normalize('NFC', c).casefold() for c in candidates if c]
        if not wanted or not any(w in low for w in wanted):
            problems.append('원문 행에 %s 가 없다(후보 %s)' % (label, ', '.join(candidates) or '없음'))
    stamp = re.match(r'(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})', info['time'])
    fetched = re.match(r'(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})', fetched_at or '')
    if stamp and fetched and stamp.groups() < fetched.groups():
        notes.append('원문이 후보 수집보다 이르다(%s < %s) — 판·표지를 담은 문장이라 거절하지 않는다'
                     % (info['time'], fetched_at))
    return hashlib.sha256(raw).hexdigest(), problems, notes


def approval_problems(root: Path, sdk_id: str, entry: dict) -> Tuple[List[str], List[str]]:
    """WV3 — 승인 꼴 · 결속 재계산 · 단위별 출처 · 사용자 원문 행 해시 대조. (문제, 알림)."""
    problems: List[str] = []
    notes: List[str] = []
    approval = entry.get('approval')
    if not isinstance(approval, dict) or set(approval) != APPROVAL_FIELDS:
        return ['approval 칸 꼴 위반(%s)' % ', '.join(sorted(APPROVAL_FIELDS))], notes
    if approval['decision'] != 'approved':
        problems.append('approval.decision 이 approved 가 아니다')
    if approval['gate'] not in GATES:
        problems.append('approval.gate 꼴 위반 — %r(G1 · G1\' · G1(리팩토링))' % approval['gate'])
    if not isinstance(approval['at'], str) or not AT_RE.match(approval['at']):
        problems.append('approval.at 꼴 위반 — «YYYY-MM-DD HH:MM +ZZZZ»(시간대 포함): %r' % approval['at'])
    if not isinstance(approval['build'], str) or not BUILD_RE.match(approval['build']):
        problems.append('approval.build 꼴 위반 — .dddjango-web/<폴더>/')
    if isinstance(entry.get('version'), str) and isinstance(entry.get('sha256'), str):
        if approval['candidate_token'] != candidate_token(sdk_id, entry['version'], entry['sha256']):
            problems.append('approval.candidate_token 이 항목(판·지문)과 다르다')
    binds = approval['binds']
    if not isinstance(binds, dict) or set(binds) != {'entry_sha256'}:
        problems.append('approval.binds 꼴 위반')
    else:
        try:
            current = entry_sha256(entry)
        except RegistryError as error:
            current = 'x'
            problems.append(str(error))
        if binds['entry_sha256'] != current:
            problems.append('승인 결속 불일치 — 승인 뒤 항목 칸이 바뀌었다(다시 승인한다)')
    sources = approval['namespace_sources']
    line_shas = approval['source_line_sha256']
    if not isinstance(sources, dict) or not all(isinstance(v, str) for v in sources.values()):
        return problems + ['approval.namespace_sources 꼴 위반'], notes
    if not isinstance(line_shas, dict):
        return problems + ['approval.source_line_sha256 꼴 위반'], notes
    missing = [u for u in scope_units(entry) if u not in sources]
    if missing:
        problems.append('use_scope 단위의 승인 출처(namespace_sources)가 없다 — %s' % missing)
    stray = sorted(set(sources) - set(scope_units(entry)))
    if stray:
        problems.append('use_scope 밖 단위의 승인 출처 — %s' % stray)
    used: Set[str] = set()
    for source in [approval['source']] + list(sources.values()):
        info = parse_source(source)
        if info is None:
            problems.append('출처 꼴 위반 — %r' % source)
            continue
        if info['kind'] != 'user' or source in used:
            continue
        used.add(source)
        raw, more, more_notes = source_line(root, info)
        problems += more
        notes += more_notes
        if raw is not None and line_shas.get(source) != hashlib.sha256(raw).hexdigest():
            problems.append('원문 행 해시 불일치 — %s' % source)
    stale = sorted(set(line_shas) - used)
    if stale:
        problems.append('쓰이지 않는 source_line_sha256 칸 — %s' % stale)
    return problems, notes


# ------------------------------------------------------------------ WV2 사본 바이트


def _lstat_link(path: Path) -> bool:
    try:
        return stat.S_ISLNK(os.lstat(path).st_mode)
    except FileNotFoundError:
        return False


def git_blob_id(data: bytes, width: int) -> str:
    header: bytes = b'blob %d\0' % len(data)
    return (hashlib.sha256 if width == 64 else hashlib.sha1)(header + data).hexdigest()


def wv2_problems(root: Path, entries: Dict[str, dict]) -> Dict[str, List[str]]:
    """등재 사본 바이트 — ① 정확 이름 ② 링크 성분 0 ③ 무시 아님 ④ 인덱스 모드·blob ⑤ 변환 속성 없음 ⑥ 재계산 일치."""
    web: Path = root / 'web'
    files: Dict[str, str] = {sid: e['file'] for sid, e in entries.items()
                             if isinstance(e, dict) and isinstance(e.get('file'), str)
                             and e['file'].startswith(VENDOR_DIR + '/') and '..' not in e['file'].split('/')}
    rels: List[str] = ['web/' + f for f in files.values()]
    index: Dict[str, Tuple[str, str]] = {}
    attrs: Dict[str, Dict[str, str]] = {}
    ignored: Set[str] = set()
    stored: Dict[str, str] = {}
    if rels:
        r = _git(root, 'ls-files', '-s', '-z', '--', *rels)
        for rec in r.stdout.decode('utf-8', 'surrogateescape').split('\0'):
            if '\t' in rec:
                meta, name = rec.split('\t', 1)
                mode, blob = meta.split()[:2]
                index[name] = (mode, blob)
        r = subprocess.run(['git', '-C', str(root), 'check-attr', '-z', '--stdin', 'text', 'eol', 'filter',
                            'ident', 'working-tree-encoding'], input=('\0'.join(rels) + '\0').encode('utf-8'),
                           capture_output=True)
        fields = r.stdout.decode('utf-8', 'surrogateescape').split('\0')
        for i in range(0, len(fields) - 2, 3):
            attrs.setdefault(fields[i], {})[fields[i + 1]] = fields[i + 2]
        r = subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '-z', '--stdin'],
                           input=('\0'.join(rels) + '\0').encode('utf-8'), capture_output=True)
        ignored = {p for p in r.stdout.decode('utf-8', 'surrogateescape').split('\0') if p}
        present: List[str] = [r_ for r_ in rels if (root / r_).is_file()]
        if present:
            r = subprocess.run(['git', '-C', str(root), 'hash-object', '--stdin-paths'],
                               input=('\n'.join(present) + '\n').encode('utf-8'), capture_output=True)
            ids: List[str] = r.stdout.decode('ascii', 'replace').split()
            if r.returncode == 0 and len(ids) == len(present):
                stored = dict(zip(present, ids))
    out: Dict[str, List[str]] = {}
    for sid, rel in files.items():
        entry: dict = entries[sid]
        problems: List[str] = []
        path: Path = web / rel
        cur: Path = root
        for part in ['web'] + rel.split('/'):
            cur = cur / part
            if _lstat_link(cur):
                problems.append('심볼릭 링크 성분 %s — 사본은 일반 파일이어야 한다'
                                % cur.relative_to(root).as_posix())
                break
        try:
            listed: List[str] = os.listdir(path.parent)
        except OSError:
            listed = []
        if path.name not in listed:
            problems.append('정확한 이름의 등재 파일이 없다(대소문자·누락) — web/%s' % rel)
            out[sid] = problems
            continue
        if not path.is_file():
            problems.append('등재 파일이 일반 파일이 아니다 — web/%s' % rel)
            out[sid] = problems
            continue
        git_rel: str = 'web/' + rel
        if git_rel in ignored:
            problems.append('등재 파일이 git 무시 규칙에 걸린다 — clone·배포에 사본이 없다')
        data: bytes = path.read_bytes()
        if git_rel in index and index[git_rel][0] != '100644':
            problems.append('인덱스 모드 %s — 일반 파일(100644)이 아니다' % index[git_rel][0])
        if git_rel in stored and git_blob_id(data, len(stored[git_rel])) != stored[git_rel]:
            problems.append('git 저장 바이트가 작업 트리 바이트와 다르다(eol·filter 변환)')
        for name, value in sorted(attrs.get(git_rel, {}).items()):
            if value not in ('unspecified', 'unset'):
                problems.append('변환 속성 %s=%s — vendor 표지(.gitattributes)가 막아야 한다' % (name, value))
        if type(entry.get('size')) is int and len(data) != entry['size']:
            problems.append('크기 불일치 %d ≠ 등재 %d' % (len(data), entry['size']))
        if hashlib.sha256(data).hexdigest() != entry.get('sha256'):
            problems.append('sha256 불일치 — 등재 지문과 다른 바이트')
        integrity = entry.get('upstream_integrity')
        if isinstance(integrity, str) and SRI_RE.match(integrity):
            algorithm: str = integrity.split('-', 1)[0]
            if sri(data, algorithm) != integrity:
                problems.append('운영자 공개 무결성(%s) 불일치' % algorithm)
        domains = entry.get('operator_domains')
        if _is_str_list(domains) and isinstance(entry.get('origins'), dict):
            if compute_origins(data, domains) != entry['origins']:
                problems.append('origins 재계산 불일치 — 접속 호스트가 등재와 다르다')
        out[sid] = problems
    for sid, e in entries.items():
        if sid not in files:
            out[sid] = ['file 칸이 static/vendor/ 아래 경로가 아니다 — 사본 검사 불가']
    return out


# ------------------------------------------------------------------ 상태


class SdkState:
    """한 프로젝트의 등재 목록 상태 — 백스톱 실행마다 `sdk_state(ctx)` 가 한 번 적재한다."""

    def __init__(self, root: Path) -> None:
        self.root: Path = root
        self.path: Path = root / 'web' / SDK_REGISTRY
        self.exists: bool = self.path.exists() or _lstat_link(self.path)
        self.raw: Optional[bytes] = None
        self.data: Optional[object] = None
        self.error: Optional[str] = None
        self.entries: Dict[str, dict] = {}
        self._wv2: Optional[Dict[str, List[str]]] = None

    @classmethod
    def load(cls, root: Path) -> 'SdkState':
        state = cls(root)
        if not state.exists:
            return state
        try:
            state.raw = state.path.read_bytes()
            state.data = strict_loads(state.raw)
        except (OSError, RegistryError) as error:
            state.error = str(error)
            return state
        sdks = state.data.get('sdks') if isinstance(state.data, dict) else None
        if isinstance(sdks, dict):
            state.entries = {k: v for k, v in sdks.items() if isinstance(v, dict)}
        return state

    def files(self) -> Dict[str, str]:
        """등재 id → file(web-상대) — 꼴이 맞는 것만."""
        out: Dict[str, str] = {}
        for sid, entry in self.entries.items():
            value = entry.get('file')
            if isinstance(value, str) and value.split('/')[:3] == ['static', 'vendor', sid] \
                    and value.count('/') == 3:
                out[sid] = value
        return out

    def wv2(self) -> Dict[str, List[str]]:
        if self._wv2 is None:
            self._wv2 = wv2_problems(self.root, self.entries)
        return self._wv2

    def passed(self) -> Set[str]:
        """WV2 를 통과한 등재 파일(web-상대) — PU2 벤더 분기가 받는 집합."""
        problems = self.wv2()
        return {f for sid, f in self.files().items() if not problems.get(sid)}


def sdk_state(ctx: object) -> SdkState:
    """백스톱 컨텍스트의 등재 상태 — 한 실행에 한 번 적재해 컨텍스트에 붙여 둔다(ST12 · PU1 · PU2 · WV 가 같이 쓴다)."""
    state: Optional[SdkState] = getattr(ctx, '_sdk_state', None)
    if state is None:
        state = SdkState.load(getattr(ctx, 'root'))
        setattr(ctx, '_sdk_state', state)
    return state
