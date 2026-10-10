# dddjango-web 백스톱 공통 기반 (판형: dddart scripts/src/common.dart — Python 이식)
#
# 파일 수집 · 주석/문자열 마스킹 · import 파서(Python import + 템플릿 extends/include/static,
# 상대 import 는 web/ 루트 클램핑) · git 게이트(added/touched/added 줄/신규 단위) · 발견 모델.
# 검사 패밀리 8개(ST·MD·IM·NM·CY·TG·PJ·PU)가 전부 이 모듈 하나를 공유한다.
#
# 경로 규약: web/ 내부 파일은 **web-상대 posix 경로**('application/order/…')가 정본.
# 표시할 때만 'web/' 접두를 붙인다. web/ 밖(web_test/·requirements.txt 등)은 root_rel 발견이다.

from __future__ import annotations

import os
import posixpath
import re
import subprocess
import sys
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------- 발견 모델


@dataclass
class Finding:
    check_id: str
    path: str  # web-상대 (root_rel=True면 프로젝트 루트-상대)
    line: Optional[int]
    message: str  # 위반 요지
    rule: str  # 제1 규약 조항
    fix: str  # 교정 안내
    root_rel: bool = False  # path가 web/ 밖(requirements.txt·web_test/ 등) — 'web/' 접두 생략

    def __str__(self) -> str:
        prefix: str = '' if self.root_rel else 'web/'
        loc: str = prefix + self.path if self.line is None else '%s%s:%d' % (prefix, self.path, self.line)
        return '[%s] BLOCKER — %s\n  위반: %s (%s)\n  교정: %s' % (
            self.check_id, loc, self.message, self.rule, self.fix)


# ------------------------------------------------------------ 트리 상수 (제1 규약 §2·§5·§6)

# web/ 직속 — Django 가 정한 자리(main.dart 자리) + 5컨테이너 (+ locale = l10n 자리)
WEB_TOP_FILES: Set[str] = {'__init__.py', 'apps.py', 'urls.py'}
WEB_TOP_DIRS: Set[str] = {'root', 'application', 'common', 'design_system', 'static', 'locale'}
ENTRY_FILES: Set[str] = {'apps.py', 'urls.py'}  # main.dart 자리
# 종류 폴더 화이트리스트 (제1 규약 §5)
APP_KINDS: Set[str] = {'use_case', 'view_model', 'state', 'shared_state', 'service'}
INFRA_KINDS: Set[str] = {'data_source', 'repository', 'service'}
PRES_KINDS: Set[str] = {'view', 'section', 'widget', 'ui_extension'}
DOMAIN_KINDS: Set[str] = {'entity', 'value_object', 'enum', 'domain_service', 'specification'}
LAYER_NAMES: Set[str] = {'domain_layer', 'application_layer', 'infra_layer', 'presentation_layer'}
ROOT_DIRS: Set[str] = {'router', 'scaffold', 'handler', 'initializer'}
SCAFFOLD_DIRS: Set[str] = {'view', 'view_model', 'state'}
COMMON_DIRS: Set[str] = {'enum', 'network', 'service', 'util'}
DS_DIRS: Set[str] = {'foundation', 'theme', 'component', 'util'}
FOUNDATION_TOKENS: List[str] = ['color', 'typography', 'spacing', 'radius', 'shadow', 'duration', 'asset']
FOUNDATION_FILES: Set[str] = {'app_%s.css' % t for t in FOUNDATION_TOKENS}
STATIC_DIRS: Set[str] = {'application', 'root', 'js', 'htmx', 'vendor', 'images', 'fonts'}
LOCAL_LINT: str = 'ruff.toml'  # 국소 타입 명시 lint (dddart analysis_options.yaml 자리)
ROOT_VIEW_TEMPLATE: str = 'root/scaffold/view/root_view.html'
HTMX_CORE: str = 'static/htmx/htmx.min.js'
HTMX_VERSION: str = '2.0.10'
API_CLIENT: str = 'common/network/api_client.py'  # dddart dio_client 자리
JSON_FIELD: str = 'common/util/json_field.py'  # 직파싱 원시 필드 단일 출처(dddart json_serializable 자리) — domain 이 import 하는 유일한 common
BACKEND_TOP_PKGS: Set[str] = {'application', 'framework'}
CODE_EXTS: Set[str] = {'.py', '.html', '.css', '.js', '.mjs', '.cjs'}
JS_EXTS: Set[str] = {'.js', '.mjs', '.cjs'}
OS_JUNK: Set[str] = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}
# 도구 캐시 폴더 — 검사 대상이 아니다(바이트코드 · 스스로 git 무시 표지 `*` 를 두는 캐시라 빚 스캔의 git 우주에도 없다)
TOOL_CACHE_DIRS: Set[str] = {'__pycache__', '.ruff_cache', '.pytest_cache', '.mypy_cache'}
# 코어 검사 목록(단일 출처 — backstop CHECK_IDS 는 이것 + check_vendor.VENDOR_CHECK_IDS). dddart 번호 그대로 ·
# 옮길 수 없는 번호는 비움(NM7 · PU4 · PU5 · PJ3[2.1.0 — vendor 버전 폴더 길이 공식 SDK 등재 절차로 바뀜]).
CORE_FAMILIES: Tuple[str, ...] = ('st', 'md', 'im', 'nm', 'cy', 'tg', 'pj', 'pu')
CORE_CHECK_IDS: Tuple[str, ...] = tuple(
    ['ST%d' % n for n in range(0, 13)]                                  # ST0~ST12
    + ['IM%d' % n for n in range(1, 28)]                                # IM1~IM27
    + ['NM%d' % n for n in range(1, 21) if n != 7]                      # NM1~NM20 · NM7 비움
    + ['CY1', 'TG1', 'TG2', 'TG3', 'MD1', 'MD2', 'PJ1', 'PJ2']                        # PJ3 비움
    + ['PU1', 'PU2', 'PU3', 'PU6', 'PU7', 'PU8'])                       # PU4·PU5 비움
STDLIB: Set[str] = set(getattr(sys, 'stdlib_module_names', ())) | {'__future__', 'typing', 'dataclasses'}

# ------------------------------------------------------------ 경로 술어


def segs_of(rel: str) -> List[str]:
    return rel.split('/')


def base_name_of(rel: str) -> str:
    return rel.rsplit('/', 1)[-1]


def parent_dir_of(rel: str) -> str:
    s: List[str] = segs_of(rel)
    return s[-2] if len(s) >= 2 else ''


def ext_of(rel: str) -> str:
    b: str = base_name_of(rel)
    i: int = b.rfind('.')
    return b[i:].lower() if i > 0 else ''


def stem_of(rel: str) -> str:
    b: str = base_name_of(rel)
    i: int = b.rfind('.')
    return b[:i] if i > 0 else b


def has_seg(rel: str, seg: str) -> bool:
    """세그먼트 정확 일치 — `/view/`가 `view_model/`·`overview/`에 비매칭."""
    return seg in segs_of(rel)


def casefold(s: str) -> str:
    return s.lower().replace('_', '')


def is_python_path(rel: str) -> bool:
    """web/ 아래 Python 경로 — design_system·static 은 CSS·템플릿·자산 자리라 제외(§2 빈 폴더 표지)."""
    return segs_of(rel)[0] not in ('design_system', 'static')


def is_standard_path(rel: str) -> bool:
    """표준 트리 안 경로인가 — web/ 직속 진입 3파일 또는 표준 컨테이너(root·application·common·design_system·static·locale).
    밖이면 옛 배치(층 판정 불가 레거시)다."""
    s: List[str] = segs_of(rel)
    return (len(s) == 1 and s[0] in WEB_TOP_FILES) or (len(s) > 1 and s[0] in WEB_TOP_DIRS)


def is_marker(rel: str) -> bool:
    """빈 폴더 표지 겸 패키지 표지 — Python 경로의 `__init__.py` 는 «직속 파일 금지»의 명시 예외."""
    return base_name_of(rel) == '__init__.py' and is_python_path(rel)


def bc_of(rel: str, areas: Set[str]) -> Optional[str]:
    """BC 판별 — `application/` 다음 경로 성분 비교(접두 문자열 비교 금지).
    [areas]가 주어지면 s[1]이 area일 때 그 다음 성분이 BC다."""
    s: List[str] = segs_of(rel)
    if len(s) < 2 or s[0] != 'application':
        return None
    if s[1] in areas:
        return s[2] if len(s) > 2 else None
    return s[1]


def bc_index(s: List[str], areas: Set[str]) -> int:
    return 2 if (len(s) > 2 and s[1] in areas) else 1


def is_bc_root_path(rel: str, areas: Set[str]) -> bool:
    """BC 루트 직속 파일 경로인가 — `application/<bc>/<file>` 또는 `application/<area>/<bc>/<file>`."""
    s: List[str] = segs_of(rel)
    if s[0] != 'application':
        return False
    return len(s) == bc_index(s, areas) + 2


def bc_dir_of(rel: str, areas: Set[str]) -> Optional[str]:
    s: List[str] = segs_of(rel)
    if len(s) < 2 or s[0] != 'application':
        return None
    bi: int = bc_index(s, areas)
    return '/'.join(s[:bi + 1]) if len(s) > bi else None


# ------------------------------------------------------------ 마스킹 스캐너


class MaskedSource:
    """한 파일의 두 가지 뷰.
    - no_comments: 주석만 공백 마스킹(개행 보존) — 태그·문자열 리터럴 검사용.
    - tokens_view: 주석 + 문자열 *내용* 마스킹(따옴표 문자는 보존 — NM13의 «첫 인자가
      문자열 리터럴» 판별에 필요) — import·토큰 검사용.
    """

    def __init__(self, original: str, no_comments: str, tokens_view: str,
                 line_starts: List[int]) -> None:
        self.original: str = original
        self.no_comments: str = no_comments
        self.tokens_view: str = tokens_view
        self.line_starts: List[int] = line_starts

    def line_of(self, offset: int) -> int:
        return bisect_right(self.line_starts, offset)  # 1-based


def _views(src: str, is_comment: List[bool], is_str: List[bool]) -> MaskedSource:
    no_c: List[str] = []
    tok: List[str] = []
    line_starts: List[int] = [0]
    for k, c in enumerate(src):
        if c == '\n':
            line_starts.append(k + 1)
        keep: str = '\n' if c == '\n' else ' '
        no_c.append(keep if is_comment[k] else c)
        tok.append(keep if (is_comment[k] or is_str[k]) else c)
    return MaskedSource(src, ''.join(no_c), ''.join(tok), line_starts)


def mask_python(src: str) -> MaskedSource:
    """Python 소스 상태 머신 — `#` 주석, 단/삼중 따옴표(f/r/b 접두 포함) 추적.
    주석·docstring 속 `import application…` 줄의 directive 오인, 교정 주석의 토큰이
    재차 blocker가 되는 루프를 여기서 차단한다(dddart maskSource 판형)."""
    n: int = len(src)
    is_comment: List[bool] = [False] * n
    is_str: List[bool] = [False] * n
    i: int = 0
    while i < n:
        c: str = src[i]
        if c == '#':
            start: int = i
            while i < n and src[i] != '\n':
                i += 1
            for k in range(start, i):
                is_comment[k] = True
            continue
        if c in ('"', "'"):
            triple: bool = src[i:i + 3] == c * 3
            q: str = c
            i += 3 if triple else 1
            while i < n:
                s: str = src[i]
                if s == '\\' and i + 1 < n:
                    is_str[i] = True
                    is_str[i + 1] = True
                    i += 2
                    continue
                if s == q and (not triple or src[i:i + 3] == q * 3):
                    i += 3 if triple else 1
                    break
                if s == '\n' and not triple:
                    i += 1  # 비종결 단일행 문자열(문법 오류) 방어 — 강제 종료
                    break
                is_str[i] = True
                i += 1
            continue
        i += 1
    return _views(src, is_comment, is_str)


def _mask_block_comments(src: str, open_tok: str, close_tok: str) -> MaskedSource:
    n: int = len(src)
    is_comment: List[bool] = [False] * n
    i: int = 0
    while i < n:
        if src.startswith(open_tok, i):
            start: int = i
            end: int = src.find(close_tok, i + len(open_tok))
            i = n if end < 0 else end + len(close_tok)
            for k in range(start, i):
                if src[k] != '\n':
                    is_comment[k] = True
            continue
        i += 1
    return _views(src, is_comment, [False] * n)


VERBATIM_RE = re.compile(
    r'\{%\s*verbatim(?P<name>\s+[^%\s]+)?\s*%\}.*?'
    r'\{%\s*endverbatim(?(name)(?P=name))\s*%\}', re.DOTALL)


def mask_html(src: str) -> MaskedSource:
    """Django 템플릿 — `<!-- -->`·`{% comment %}…{% endcomment %}`·한 줄 `{# #}`만 주석.
    다중줄 {# #}는 출력되는 텍스트이므로 마스킹하지 않는다(PU6이 따로 본다)."""
    pattern = re.compile(r'<!--.*?(?:-->|$)|\{%\s*comment\b.*?%\}.*?'
                         r'\{%\s*endcomment\s*%\}|\{#[^\r\n]*?#\}', re.DOTALL)
    flags: List[bool] = [False] * len(src)
    verbatim = list(VERBATIM_RE.finditer(src))
    for match in pattern.finditer(src):
        if not match.group().startswith('<!--') and any(
                block.start() <= match.start() < block.end() for block in verbatim):
            continue
        for k in range(match.start(), match.end()):
            if src[k] != '\n':
                flags[k] = True
    return _views(src, flags, [False] * len(src))


def mask_css(src: str) -> MaskedSource:
    return _mask_block_comments(src, '/*', '*/')


# 정규식 리터럴이 올 수 있는 앞 문자·낱말(그 밖의 `/` 는 나눗셈)
_JS_REGEX_PREV: str = '(,=:[!&|?{};+-*%<>~^'
_JS_REGEX_WORDS: Set[str] = {'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw',
                             'case', 'do', 'else', 'yield', 'await'}


def mask_js(src: str) -> MaskedSource:
    """JS 주석(`//`·`/* */`)만 공백 마스킹(개행 보존) — 문자열·템플릿·정규식 리터럴은 그대로 둔다.
    정규식 리터럴 안의 `//`·따옴표를 주석·문자열로 오인하지 않게 앞 문자로 리터럴 자리를 가른다."""
    n: int = len(src)
    is_comment: List[bool] = [False] * n
    i: int = 0
    prev: str = ''
    word: str = ''
    while i < n:
        c: str = src[i]
        if c in ('"', "'", '`'):
            q: str = c
            i += 1
            while i < n:
                s: str = src[i]
                if s == '\\':
                    i += 2
                    continue
                if s == q:
                    i += 1
                    break
                if s == '\n' and q != '`':
                    break
                i += 1
            prev, word = q, ''
            continue
        if src.startswith('//', i):
            start: int = i
            while i < n and src[i] != '\n':
                i += 1
            for k in range(start, i):
                is_comment[k] = True
            continue
        if src.startswith('/*', i):
            start = i
            end: int = src.find('*/', i + 2)
            i = n if end < 0 else end + 2
            for k in range(start, i):
                if src[k] != '\n':
                    is_comment[k] = True
            continue
        if c == '/' and (prev == '' or prev in _JS_REGEX_PREV or word in _JS_REGEX_WORDS):
            i += 1
            in_class: bool = False
            while i < n and src[i] != '\n':
                s = src[i]
                if s == '\\':
                    i += 2
                    continue
                if s == '[':
                    in_class = True
                elif s == ']':
                    in_class = False
                elif s == '/' and not in_class:
                    i += 1
                    break
                i += 1
            prev, word = '/', ''
            continue
        if c.isspace():
            i += 1
            continue
        if c.isalnum() or c in '_$':
            j: int = i
            while j < n and (src[j].isalnum() or src[j] in '_$'):
                j += 1
            word = src[i:j]
            prev = src[j - 1]
            i = j
            continue
        prev, word = c, ''
        i += 1
    return _views(src, is_comment, [False] * n)


# ------------------------------------------------------------ import 파서


@dataclass
class ImportEdge:
    kind: str  # 'py' | 'extends' | 'include' | 'static'
    uri: str  # 원문 요지 — py: 점 모듈 경로(상대는 점 접두 그대로), 템플릿: 이름 그대로
    line: int
    internal: bool
    target: Optional[str]  # internal일 때 web-상대 정규화 경로
    module: Optional[str] = None  # py 절대 import 의 점 모듈 경로
    names: List[str] = field(default_factory=list)
    relative: bool = False

    @property
    def top(self) -> str:
        """외부 py import 의 최상위 패키지명."""
        return (self.module or '').split('.')[0]


_IMPORT_RE = re.compile(r'(?m)^[ \t]*import[ \t]+([^\n]+)')
_FROM_RE = re.compile(r'(?m)^[ \t]*from[ \t]+([.\w]+)[ \t]*import\b')
_TPL_RE = re.compile(r'''\{%-?\s*(extends|include)\s+(["'])([^"'\n]+)\2''')
_STATIC_RE = re.compile(r'''\{%-?\s*static\s+(["'])([^"'\n]+)\1''')


def _names_after(tv: str, offset: int) -> List[str]:
    """`import` 키워드 뒤 이름 목록 — 괄호 묶음이면 닫힘까지 스캔(멀티라인 대응)."""
    j: int = offset
    while j < len(tv) and tv[j] in ' \t':
        j += 1
    if j < len(tv) and tv[j] == '(':
        end: int = tv.find(')', j)
        body: str = tv[j + 1:end if end >= 0 else j + 400]
    else:
        e: int = tv.find('\n', j)
        body = tv[j:e if e >= 0 else len(tv)]
    out: List[str] = []
    for piece in body.split(','):
        name: str = piece.strip().split(' as ')[0].strip().rstrip('\\').strip()
        if re.fullmatch(r'\w+', name):
            out.append(name)
    return out


def _resolve(parts: List[str], names: List[str], files: Set[str], dirs: Set[str]) -> List[str]:
    """모듈 성분 → web-상대 파일. 패키지면 from-import 이름별로 하위 모듈을 찾는다."""
    base: str = '/'.join(parts)
    pre: str = base + '/' if base else ''
    if base and base + '.py' in files:
        return [base + '.py']
    if base == '' or base in dirs:
        out: List[str] = []
        for n in names or ['']:
            p: str = pre + n
            if n and p + '.py' in files:
                out.append(p + '.py')
            elif n and p in dirs:
                out.append(p + '/__init__.py')
            elif n:
                out.append(p + '.py')  # 아직 없는 하위 모듈 — 이름 그대로(빈 __init__.py 표지 트리)
            else:
                out.append(pre + '__init__.py')
        return sorted(set(out))
    return [base + '.py']


def parse_py_imports(ms: MaskedSource, file_rel: str, files: Set[str], dirs: Set[str]) -> List[ImportEdge]:
    """tokens_view에서 import/from 문을 수집한다. 상대 import는 **web/ 루트 클램핑**으로
    해소한다(잉여 `.`는 web/에서 멈춘다 — 나이브 join의 우회 벡터 차단, dddart _clampSegs 판형)."""
    edges: List[ImportEdge] = []
    tv: str = ms.tokens_view
    for m in _IMPORT_RE.finditer(tv):
        line: int = ms.line_of(m.start())
        for piece in m.group(1).split(','):
            mod: str = piece.strip().split(' as ')[0].strip().rstrip('\\').strip()
            if not re.fullmatch(r'[\w.]+', mod):
                continue
            parts: List[str] = [p for p in mod.split('.') if p]
            if parts and parts[0] == 'web':
                for t in _resolve(parts[1:], [], files, dirs):
                    edges.append(ImportEdge('py', mod, line, True, t, mod))
            elif parts:
                edges.append(ImportEdge('py', mod, line, False, None, mod))
    pkg_base: List[str] = segs_of(file_rel)[:-1]
    for m in _FROM_RE.finditer(tv):
        line = ms.line_of(m.start())
        mod = m.group(1)
        names: List[str] = _names_after(tv, m.end())
        dots: int = len(mod) - len(mod.lstrip('.'))
        parts = [p for p in mod.lstrip('.').split('.') if p]
        if dots:
            base: List[str] = pkg_base[:max(0, len(pkg_base) - (dots - 1))]
            for t in _resolve(base + parts, names, files, dirs):
                edges.append(ImportEdge('py', mod, line, True, t, None, names, True))
        elif parts and parts[0] == 'web':
            for t in _resolve(parts[1:], names, files, dirs):
                edges.append(ImportEdge('py', mod, line, True, t, mod, names))
        elif parts:
            edges.append(ImportEdge('py', mod, line, False, None, mod, names))
    return edges


def static_target(arg: str) -> Optional[str]:
    """`{% static %}` 인자 → web-상대 경로. STATICFILES_DIRS 접두 튜플
    ("web", web/static) · ("design_system", web/design_system) 둘만 안다."""
    a: str = arg.strip().lstrip('/')
    if a.startswith('web/'):
        return 'static/' + a[len('web/'):]
    if a.startswith('design_system/'):
        return a
    return None


_CSS_REF_RE = re.compile(r'''@import\s+(?:url\(\s*)?["']?([^"')\s;]+)|url\(\s*["']?([^"')\s]+)''')


def ref_path(rel: str) -> str:
    """참조 분류용 경로 — 조각 CSS 는 그 소유자의 presentation 자리로 센다(§5).
    `static/application/[<area>/]<bc>/<f>.css` → `application/[<area>/]<bc>/presentation_layer/<f>.css`,
    `static/root/<f>.css` → `root/scaffold/view/<f>.css`. 그 밖은 그대로."""
    s: List[str] = segs_of(rel)
    if len(s) >= 4 and s[:2] == ['static', 'application']:
        return '/'.join(s[1:-1] + ['presentation_layer', s[-1]])
    if len(s) == 3 and s[:2] == ['static', 'root']:
        return 'root/scaffold/view/' + s[-1]
    return rel


def parse_css_edges(ms: MaskedSource, file_rel: str) -> List[ImportEdge]:
    """CSS 참조 — `@import`·`url()` 의 정적 경로(`/static/…` 절대 또는 이 CSS 의 정적 URL 기준 상대)."""
    if file_rel.startswith('static/'):
        served: str = '/static/web/' + file_rel[len('static/'):]
    elif file_rel.startswith('design_system/'):
        served = '/static/' + file_rel
    else:
        return []
    edges: List[ImportEdge] = []
    for m in _CSS_REF_RE.finditer(ms.no_comments):
        u: str = (m.group(1) or m.group(2) or '').strip()
        if not u or u.startswith(('#', 'data:', '//')) or re.match(r'^[A-Za-z][\w+.-]*:', u):
            continue
        full: str = posixpath.normpath(u if u.startswith('/') else posixpath.join(posixpath.dirname(served), u))
        if not full.startswith('/static/'):
            continue
        t: Optional[str] = static_target(full[len('/static/'):])
        if t is not None:
            edges.append(ImportEdge('css', u, ms.line_of(m.start()), True, t))
    return edges


def parse_template_edges(ms: MaskedSource) -> List[ImportEdge]:
    """템플릿 참조 — `{% extends %}`·`{% include %}`(TEMPLATES DIRS = web/ 뿌리)·`{% static %}`."""
    edges: List[ImportEdge] = []
    text: str = ms.no_comments
    for m in _TPL_RE.finditer(text):
        name: str = m.group(3).strip().lstrip('/')
        edges.append(ImportEdge(m.group(1), name, ms.line_of(m.start()), True, name))
    for m in _STATIC_RE.finditer(text):
        t: Optional[str] = static_target(m.group(2))
        edges.append(ImportEdge('static', m.group(2), ms.line_of(m.start()), t is not None, t))
    return edges


# ---- 실제로 실리는 정적 파일(제품 판정 전용 — import edge 와 따로다)
# import edge 의 target 은 참조 원문 전체를 접은 경로다(위 parse_css_edges · static_target — 다른 IM · Finding 경로 · 빚 키가
# 그 글자에 기대므로 바꾸지 않는다). 어느 파일이 실리는가는 그것과 다를 수 있다 — 꼬리(query · fragment) 안의 경로 꼴
# (`a.css?v=/../x`)이 원문 전체를 접을 때 대상을 지우거나 다른 파일로 바꾼다. 제품 혼입 판정은 아래 한 술어만 쓴다.

_URL_TAIL_RE = re.compile(r'[?#]')


def loaded_file(ref: str, base: str = '/static') -> Optional[str]:
    """정적 참조 원문 → 실제로 실리는 파일(web-상대 · 정적 뿌리나 STATICFILES 접두 둘 밖이면 None).
    원문에서 query · fragment 꼬리를 **먼저** 떼고, base(그 참조가 풀리는 정적 URL 폴더) 기준으로 상대 경로를 푼 뒤
    `.` · `..` 를 접는다. `{% static %}` 인자 · CSS `@import` · 정적 경로 `url()` 이 모두 이 술어를 지난다."""
    path: str = _URL_TAIL_RE.split(ref.strip(), 1)[0]
    if not path:
        return None
    full: str = posixpath.normpath(path if path.startswith('/') else posixpath.join(base, path))
    if not full.startswith('/static/'):
        return None
    return static_target(full[len('/static/'):])


def parse_css_loads(ms: MaskedSource, file_rel: str) -> List[Tuple[int, str]]:
    """CSS 가 직접 싣는 정적 파일 — (행, 실제로 실리는 web-상대 경로). 보는 참조와 걸러내는 꼴은 parse_css_edges 와 같다
    (`@import`·`url()` 의 정적 경로 — 걸러내는 꼴을 바꾸면 둘 다 바꾼다). 대상만 loaded_file 로 푼다 — 원문 전체를 접으면
    정적 뿌리 밖으로 나가 edge 가 서지 않는 참조도 여기서는 선다."""
    if file_rel.startswith('static/'):
        served: str = '/static/web/' + file_rel[len('static/'):]
    elif file_rel.startswith('design_system/'):
        served = '/static/' + file_rel
    else:
        return []
    loads: List[Tuple[int, str]] = []
    for m in _CSS_REF_RE.finditer(ms.no_comments):
        u: str = (m.group(1) or m.group(2) or '').strip()
        if not u or u.startswith(('#', 'data:', '//')) or re.match(r'^[A-Za-z][\w+.-]*:', u):
            continue
        t: Optional[str] = loaded_file(u, posixpath.dirname(served))
        if t is not None:
            loads.append((ms.line_of(m.start()), t))
    return loads


def parse_template_loads(ms: MaskedSource) -> List[Tuple[int, str]]:
    """템플릿이 `{% static %}` 으로 직접 싣는 정적 파일 — (행, 실제로 실리는 web-상대 경로). 인자는 정적 뿌리 기준이다
    (앞머리 `/` 는 뗀다 — static_target 과 같다)."""
    loads: List[Tuple[int, str]] = []
    for m in _STATIC_RE.finditer(ms.no_comments):
        t: Optional[str] = loaded_file(m.group(2).strip().lstrip('/'))
        if t is not None:
            loads.append((ms.line_of(m.start()), t))
    return loads


# ------------------------------------------------------------ 컨텍스트(게이트)


class BackstopContext:
    """대상 프로젝트 web/의 파일·디렉터리 인벤토리와 git diff 게이트.
    게이트: 구조·명명=added 파일/디렉터리, import=touched 파일의 added 줄,
    골격 완비=신규 단위 → 레거시(기존 drift) 불발화."""

    def __init__(self, root: Path, git_repo: bool, diff_base: Optional[str], all_mode: bool,
                 all_files: List[str], dirs: Set[str], areas: Set[str], project_pkgs: Set[str],
                 touched: Set[str], added: Set[str], base_files: Set[str],
                 added_spans: Dict[str, List[Tuple[int, int]]]) -> None:
        self.root: Path = root
        self.web: Path = root / 'web'
        self.git_repo: bool = git_repo
        self.diff_base: Optional[str] = diff_base
        self.all_mode: bool = all_mode
        self.all_files: List[str] = all_files  # web-상대 전 파일(자산 포함), 정렬
        self.files: List[str] = [f for f in all_files if ext_of(f) in CODE_EXTS]  # 코드 파일
        self.files_set: Set[str] = set(all_files)
        self.py_files: Set[str] = {f for f in all_files if ext_of(f) == '.py'}
        self.dirs: Set[str] = dirs  # web-상대 디렉터리 전체
        self.areas: Set[str] = areas  # application/ 직속 area 폴더(적극 증명분만)
        self.project_pkgs: Set[str] = project_pkgs  # settings 실측 — IM25 deny 대상
        self.touched: Set[str] = touched
        self.added: Set[str] = added
        self.base_files: Set[str] = base_files  # diff-base 시점 web-상대 파일(ls-tree)
        self.added_spans: Dict[str, List[Tuple[int, int]]] = added_spans
        self.notices: List[str] = []
        self._mask_cache: Dict[str, MaskedSource] = {}
        self._edge_cache: Dict[str, List[ImportEdge]] = {}

    # ---- 게이트

    @property
    def gated(self) -> bool:
        """게이트가 살아 있는가 (비git·--all이면 전역 퇴화)."""
        return self.git_repo and self.diff_base is not None and not self.all_mode

    @property
    def can_detect_new_units(self) -> bool:
        """신규 단위 판별 가능 여부 (ls-tree 기준점 필요)."""
        return self.git_repo and self.diff_base is not None

    def is_added(self, f: str) -> bool:
        return (not self.gated) or f in self.added

    def is_touched(self, f: str) -> bool:
        return (not self.gated) or f in self.touched

    def is_added_dir(self, d: str) -> bool:
        """added 디렉터리 = diff-base에 그 경로 하위 파일이 0개(added 파일 포함 여부가
        아님 — 레거시 폴더에 새 파일을 넣어도 그 폴더는 added가 아니다)."""
        if not self.gated:
            return True
        prefix: str = d + '/'
        return not any(f.startswith(prefix) for f in self.base_files)

    def line_is_added(self, f: str, line: int) -> bool:
        """IM 게이트 — touched 파일의 added 줄. 미추적/신규 파일은 전 줄."""
        if not self.gated:
            return True
        if f in self.added:
            return True
        spans: Optional[List[Tuple[int, int]]] = self.added_spans.get(f)
        if not spans:
            return False
        return any(a <= line <= b for (a, b) in spans)

    # ---- 파일 뷰

    def mask_of(self, f: str) -> MaskedSource:
        ms: Optional[MaskedSource] = self._mask_cache.get(f)
        if ms is None:
            text: str = (self.web / f).read_text(encoding='utf-8', errors='replace')
            ext: str = ext_of(f)
            if ext == '.py':
                ms = mask_python(text)
            elif ext == '.css':
                ms = mask_css(text)
            elif ext in JS_EXTS:
                ms = mask_js(text)
            else:
                ms = mask_html(text)
            self._mask_cache[f] = ms
        return ms

    def edges_of(self, f: str) -> List[ImportEdge]:
        edges: Optional[List[ImportEdge]] = self._edge_cache.get(f)
        if edges is None:
            ext: str = ext_of(f)
            if ext == '.py':
                edges = parse_py_imports(self.mask_of(f), f, self.py_files, self.dirs)
            elif ext == '.html':
                edges = parse_template_edges(self.mask_of(f))
            elif ext == '.css':
                edges = parse_css_edges(self.mask_of(f), f)
            else:
                edges = []
            self._edge_cache[f] = edges
        return edges

    def loads_of(self, f: str) -> List[Tuple[int, str]]:
        """문서가 직접 싣는 정적 파일 — (행, 실제로 실리는 web-상대 경로). 제품 혼입 판정 전용이다(edges_of 와 따로 —
        import edge 는 참조 원문 전체를 접은 대상 그대로다)."""
        ext: str = ext_of(f)
        if ext == '.html':
            return parse_template_loads(self.mask_of(f))
        if ext == '.css':
            return parse_css_loads(self.mask_of(f), f)
        return []

    # ---- 빌드

    @staticmethod
    def build(root: Path, diff_base: Optional[str], all_mode: bool) -> 'BackstopContext':
        web: Path = root / 'web'
        if not web.is_dir():
            print('[backstop] 사용 오류: web/ 없음 — %s' % root, file=sys.stderr)
            sys.exit(1)

        files: List[str] = []
        dirs: Set[str] = set()
        for cur, dnames, fnames in os.walk(web):
            dnames[:] = [d for d in dnames if d not in TOOL_CACHE_DIRS and d != '.git']
            rel_dir: str = os.path.relpath(cur, web).replace(os.sep, '/')
            for d in dnames:
                dirs.add(d if rel_dir == '.' else rel_dir + '/' + d)
            for fn in fnames:
                if fn.endswith('.pyc') or fn in OS_JUNK or fn.startswith('._'):
                    continue
                files.append(fn if rel_dir == '.' else rel_dir + '/' + fn)
        files.sort()

        areas: Set[str] = _areas(files, dirs)

        git_repo: bool = _git(root, ['rev-parse', '--is-inside-work-tree']) == 'true'
        touched: Set[str] = set()
        added: Set[str] = set()
        base_files: Set[str] = set()
        added_spans: Dict[str, List[Tuple[int, int]]] = {}

        if git_repo and diff_base is not None:
            repo_top: str = os.path.realpath(_git(root, ['rev-parse', '--show-toplevel']) or '')
            root_abs: str = os.path.realpath(str(root))
            repo_prefix: str = ''
            if root_abs != repo_top:
                repo_prefix = os.path.relpath(root_abs, repo_top).replace(os.sep, '/') + '/'

            def to_web_rel(repo_path: str) -> Optional[str]:
                if not repo_path.startswith(repo_prefix):
                    return None
                p: str = repo_path[len(repo_prefix):]
                return p[4:] if p.startswith('web/') else None

            # 1) diff: 작업 트리 vs 기준점 (미커밋 포함, -z NUL 구분)
            diff_out: Optional[str] = _git_raw(root, ['diff', '--name-status', '-z', diff_base])
            if diff_out is None:
                print('[backstop] 사용 오류: --diff-base %s 해석 불가' % diff_base, file=sys.stderr)
                sys.exit(1)
            tok: List[str] = diff_out.split('\x00')
            i: int = 0
            while i < len(tok) - 1:
                st: str = tok[i]
                if not st:
                    i += 1
                    continue
                if st.startswith('R') or st.startswith('C'):
                    # old, new 두 필드 — 새 경로만 added/touched(old는 비현존 취급)
                    new_path: Optional[str] = tok[i + 2] if i + 2 < len(tok) else None
                    wr: Optional[str] = to_web_rel(new_path) if new_path else None
                    if wr is not None:
                        touched.add(wr)
                        added.add(wr)
                    i += 3
                    continue
                path: Optional[str] = tok[i + 1] if i + 1 < len(tok) else None
                wr = to_web_rel(path) if path else None
                if wr is not None and st[0] != 'D':
                    touched.add(wr)
                    if st[0] == 'A':
                        added.add(wr)
                i += 2
            # 2) porcelain — 미추적 파일(-uall 필수: 기본값은 신규 디렉터리를 한 줄로 접어
            #    신규 BC 전체가 누락된다 — dddart 적대 점검 P0)
            p_out: Optional[str] = _git_raw(root, ['status', '--porcelain', '-z', '--untracked-files=all'])
            if p_out is None:
                if not all_mode:
                    print('[backstop] 사용 오류: git status 수집 실패 — 미추적 파일을 볼 수 없다(미실행)', file=sys.stderr)
                    sys.exit(1)
                p_out = ''
            pt: List[str] = p_out.split('\x00')
            i = 0
            while i < len(pt):
                entry: str = pt[i]
                if len(entry) < 4:
                    i += 1
                    continue
                xy: str = entry[:2]
                wr = to_web_rel(entry[3:])
                is_rename: bool = xy[0] in ('R', 'C')
                if wr is not None and 'D' not in xy:
                    touched.add(wr)
                    if xy == '??' or xy[0] == 'A' or is_rename:
                        added.add(wr)
                i += 2 if is_rename else 1  # 리네임은 다음 필드가 old 경로
            # 3) 기준점 트리 (added 디렉터리·신규 단위 판별)
            ls: str = _git_raw(root, ['ls-tree', '-r', '--name-only', '-z', diff_base]) or ''
            for p in ls.split('\x00'):
                wr = to_web_rel(p)
                if wr is not None:
                    base_files.add(wr)
            # 4) 수정 파일의 added 줄 범위 (IM·PU 게이트)
            hunk_re = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', re.M)
            for f in sorted(touched - added):
                # pathspec은 -C(=대상 루트) 기준 — repo 접두를 붙이지 않는다
                d: str = _git_raw(root, ['diff', '-U0', diff_base, '--', 'web/' + f]) or ''
                spans: List[Tuple[int, int]] = []
                for m in hunk_re.finditer(d):
                    start: int = int(m.group(1))
                    length: int = 1 if m.group(2) is None else int(m.group(2))
                    if length > 0:
                        spans.append((start, start + length - 1))
                added_spans[f] = spans

        return BackstopContext(root, git_repo, diff_base, all_mode, files, dirs, areas,
                               _project_pkgs(root), touched, added, base_files, added_spans)

    @staticmethod
    def from_files(root: Path, files: List[str]) -> 'BackstopContext':
        """주어진 web-상대 파일 목록을 전부 added 로 보는 컨텍스트(빚 스캔 전용 — `--debt-scan`).
        dirs = 파일 조상 전부 · base_files = 같은 목록(브라운필드 legacy core 소비 판정은 이 트리 기준) ·
        기준점이 없으므로 ST4 · TG 는 생략 notice 를 낸다(리팩토링 스캔은 골격을 따로 돈다)."""
        ordered: List[str] = sorted({f for f in files if base_name_of(f) not in OS_JUNK
                                     and not base_name_of(f).startswith('._')})
        dirs: Set[str] = set()
        for f in ordered:
            s: List[str] = segs_of(f)
            for k in range(1, len(s)):
                dirs.add('/'.join(s[:k]))
        git_repo: bool = _git(root, ['rev-parse', '--is-inside-work-tree']) == 'true'
        return BackstopContext(root, git_repo, None, True, ordered, dirs, _areas(ordered, dirs),
                               _project_pkgs(root), set(ordered), set(ordered), set(ordered), {})


def _areas(files: List[str], dirs: Set[str]) -> Set[str]:
    """area 판별(build · from_files 공통)."""
    # area 판별 — 적극 증명될 때만: `application/` 직속 <x>의 직속에 코드 파일이 없고
    # (`__init__.py` 표지 제외), 직속 디렉터리가 1개 이상이며 전부 BC꼴(각각 4계층 폴더 중
    # 하나 이상을 직속 보유)일 때만 x=area. 그 외 전부 s[1]=BC 폴백(보수 — 레거시·drift
    # 형상의 분류 불변 → CY 베이스라인·IM 분류 무회귀).
    areas: Set[str] = set()
    child_dirs: Dict[str, Set[str]] = {}
    child_has_file: Set[str] = set()
    for d in dirs:
        s: List[str] = d.split('/')
        if s[0] != 'application':
            continue
        if len(s) == 2:
            child_dirs.setdefault(s[1], set())
        if len(s) == 3:
            child_dirs.setdefault(s[1], set()).add(s[2])
    for f in files:
        s = f.split('/')
        if len(s) == 3 and s[0] == 'application' and ext_of(f) in CODE_EXTS and s[2] != '__init__.py':
            child_has_file.add(s[1])
    for x, children in child_dirs.items():
        if x in child_has_file or x in LAYER_NAMES or not children:
            continue
        if any(c in LAYER_NAMES for c in children):
            continue  # x 자신이 BC(계층 직속 보유)
        if all(any('application/%s/%s/%s' % (x, y, ly) in dirs for ly in LAYER_NAMES) for y in children):
            areas.add(x)
    return areas


def _project_pkgs(root: Path) -> Set[str]:
    """프로젝트 패키지 실측 — settings.py(또는 settings/) 보유 루트 직속 패키지(IM25 대상)."""
    pkgs: Set[str] = set()
    for child in root.iterdir():
        if child.is_dir() and child.name not in ('web', 'web_test', '.git'):
            if (child / 'settings.py').is_file() or (child / 'settings').is_dir():
                pkgs.add(child.name)
    return pkgs


def _git(root: Path, args: List[str]) -> Optional[str]:
    out: Optional[str] = _git_raw(root, args)
    return out.strip() if out is not None else None


def _git_raw(root: Path, args: List[str]) -> Optional[str]:
    r = subprocess.run(['git', '-C', str(root)] + args,
                       capture_output=True, text=True, errors='replace')
    return r.stdout if r.returncode == 0 else None


# ------------------------------------------------------------ 토큰 스캔 보조


def scan_tokens(ms: MaskedSource, regex: 're.Pattern[str]', view: str = 'tokens') -> List[Tuple[int, int]]:
    """마스킹 본문에서 정규식 매치를 찾아 (line, 매치 끝 오프셋) 목록 반환."""
    text: str = ms.tokens_view if view == 'tokens' else ms.no_comments
    return [(ms.line_of(m.start()), m.end()) for m in regex.finditer(text)]


def first_arg_of(text: str, open_paren_end: int) -> str:
    """호출 괄호의 첫 인자를 균형 스캔으로 추출(멀티라인 호출 대응).
    [open_paren_end]는 여는 괄호 *다음* 오프셋."""
    depth: int = 0
    buf: List[str] = []
    i: int = open_paren_end
    while i < len(text) and len(buf) < 400:
        c: str = text[i]
        if c in '([{':
            depth += 1
        if c in ')]}':
            if depth == 0:
                break
            depth -= 1
        if c == ',' and depth == 0:
            break
        buf.append(c)
        i += 1
    return ''.join(buf).strip()


def is_string_literal(arg: str) -> bool:
    """첫 인자가 문자열 리터럴인가 — 접두(f·r·b·u) 허용."""
    return re.match(r'''^[rRbBfFuU]{0,2}["']''', arg) is not None


_TOP_DECL_RE = re.compile(r'(?m)^(class|def|async[ \t]+def)[ \t]+([A-Za-z_]\w*)')


def top_level_decls(ms: MaskedSource) -> List[Tuple[str, str, int, int]]:
    """Python top-level 선언 (종류 class|def, 이름, 줄, 오프셋) — 0열 선언만."""
    return [(m.group(1).split()[-1], m.group(2), ms.line_of(m.start()), m.start())
            for m in _TOP_DECL_RE.finditer(ms.tokens_view)]

