# dddjango-web 백스톱 공통 기반 (판형: dddart scripts/src/common.dart — Python 이식)
#
# 파일 수집 · 주석/문자열 마스킹 · import 파서(상대 import 루트 클램핑) · git 게이트
# (added/touched/added 줄/신규 단위) · 발견 모델 · 트리 데이터 사본.
# 검사 패밀리 4개(WS·WI·WN·WP)가 전부 이 모듈 하나를 공유한다.
#
# 경로 규약: web/ 내부 파일은 **web-상대 posix 경로**('orders/order_list/…')가 정본.
# 표시할 때만 'web/' 접두를 붙인다.
#
# 규범 값의 정본은 discipline-web-houserules/references/final.md 다 — 이 파일의
# 트리·명명 상수는 그 사본이며 각 상수에 출처 절을 표기한다(§7: 검사 의미가
# 바뀌면 러너가 단일 출처, 값이 바뀌면 houserules가 단일 출처).

import os
import re
import subprocess
import sys
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------- 발견 모델


@dataclass
class Finding:
    check_id: str  # WS1·WI2 … (패밀리+번호)
    path: str  # web-상대 posix 경로 (''=web/ 컨테이너 자신)
    line: Optional[int]
    message: str  # 위반 요지
    fix: str  # 교정 안내
    section: str  # houserules 출처 절 — '§1'·'§5⑤' 류

    def __str__(self) -> str:
        loc: str = 'web/' + self.path
        if self.line is not None:
            loc += ':%d' % self.line
        return (
            '[%s] BLOCKER — %s\n  위반: %s\n  교정: %s (houserules %s)'
            % (self.check_id, loc, self.message, self.fix, self.section)
        )


# ------------------------------------------------- 트리 데이터 사본 (값 정본: houserules)

# houserules §1 트리 v3.1 — web/ 직속 고정 파일·컨테이너(공식 SDK 등재 목록은 §9 — 있을 때만)
WEB_TOP_FILES: Set[str] = {'urls.py', 'apps.py', 'sdk_registry.json'}
CONTAINER_DIRS: Set[str] = {'base', 'client', 'design_system', 'static'}
# houserules §3 — 마커 파일은 «직속 파일 금지»의 명시 예외
MARKER_FILES: Set[str] = {'__init__.py', '.gitkeep'}
# houserules §1·§2 — 화면 개념 종류 폴더 5종 (form은 조건 생성)
KIND_DIRS: Set[str] = {'view', 'view_model', 'state', 'form', 'section'}
PY_KIND_DIRS: Set[str] = {'view', 'view_model', 'state', 'form'}  # §3 마커=__init__.py
HTML_KIND_DIRS: Set[str] = {'section', 'widget'}  # §3 마커=.gitkeep
# houserules §1 — 영역·화면 이름 deny(컨테이너명·종류명)
RESERVED_NAMES: Set[str] = CONTAINER_DIRS | KIND_DIRS | {'web', 'widget'}
# houserules §1·§3 — static/ 직속 4종 + 조건부 3종(vendor/ 는 승인된 공식 SDK 가 있을 때만 — §9)
STATIC_DIRS: Set[str] = {'css', 'js', 'htmx', 'images', 'fonts', 'files', 'vendor'}
# houserules §4 — component 정크드로어 군 금지
JUNK_GROUPS: Set[str] = {'widget', 'etc'}
# houserules §5⑤·§4 — HTMX core는 신규 canonical 1경로. legacy 2경로는
# diff-base에 실재하던 브라운필드 설치만 소비한다.
HTMX_CANONICAL: str = 'static/htmx/htmx.min.js'
HTMX_LEGACY: Set[str] = {'static/js/htmx.min.js', 'static/js/htmx.js'}
HTMX_ALLOWED: Set[str] = {HTMX_CANONICAL} | HTMX_LEGACY
MOTION_JS: str = 'static/js/motion.js'
# houserules §4 총괄표 — 종류 폴더 ↔ py 접미사
KIND_PY_SUFFIX: Dict[str, str] = {
    'view': '_view.py',
    'view_model': '_view_model.py',
    'state': '_state.py',
    'form': '_form.py',
}
# houserules §5① — web/**에서 금지되는 내부 세계 최상위 패키지(+ 프로젝트 패키지는 실측)
BACKEND_TOP_PKGS: Set[str] = {'application', 'framework'}

TEXT_EXTS: Set[str] = {'.py', '.html', '.css', '.js'}

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
    return b[i:] if i >= 0 else ''


def stem_of(rel: str) -> str:
    b: str = base_name_of(rel)
    i: int = b.rfind('.')
    return b[:i] if i >= 0 else b


def tokens_contain(hay: str, needle: str) -> bool:
    """`_` 토큰열 연속 부분열 포함 — `order_list`는 `order_list_badge`에 포함,
    `order_status_badge`에는 비포함(§4-4 view 이름 금지 판별)."""
    h: List[str] = hay.split('_')
    n: List[str] = needle.split('_')
    if not n or len(n) > len(h):
        return False
    return any(h[i:i + len(n)] == n for i in range(len(h) - len(n) + 1))


# ------------------------------------------------------------ 마스킹 스캐너


class MaskedSource:
    """한 파일의 세 가지 뷰.
    - no_comments: 주석만 공백 마스킹(개행 보존) — 문자열 리터럴 검사(WI3)·태그 검사용.
    - tokens_view: 주석+문자열 *내용* 마스킹 — import 파싱 등 토큰 검사용.
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
    주석 속 `import application…` 줄의 directive 오인, 문자열 속 토큰의 재발화를
    차단한다(dddart maskSource 판형)."""
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
    is_str: List[bool] = [False] * n
    i: int = 0
    while i < n:
        if src.startswith(open_tok, i):
            start: int = i
            end: int = src.find(close_tok, i + len(open_tok))
            i = n if end < 0 else end + len(close_tok)
            for k in range(start, i):
                is_comment[k] = True
            continue
        i += 1
    return _views(src, is_comment, is_str)


VERBATIM_RE = re.compile(
    r'\{%\s*verbatim(?P<name>\s+[^%\s]+)?\s*%\}.*?'
    r'\{%\s*endverbatim(?(name)(?P=name))\s*%\}', re.DOTALL)


def mask_html(src: str) -> MaskedSource:
    # Django의 짧은 주석은 한 줄만이다. 다중줄 {# #}는 출력되는 텍스트이므로
    # 마스킹하지 않는다. verbatim 안은 WP6에서 별도로 제외한다(HTML은 실행된다).
    pattern = re.compile(r'<!--.*?(?:-->|$)|\{%\s*comment\b.*?%\}.*?'
                         r'\{%\s*endcomment\s*%\}|\{#[^\r\n]*?#\}', re.DOTALL)
    flags: List[bool] = [False] * len(src)
    verbatim = list(VERBATIM_RE.finditer(src))
    for match in pattern.finditer(src):
        if not match.group().startswith('<!--') and any(
                block.start() <= match.start() < block.end() for block in verbatim):
            continue
        flags[match.start():match.end()] = [True] * (match.end() - match.start())
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
    prev: str = ''      # 마지막 의미 문자(공백·주석 제외)
    word: str = ''      # 마지막 식별자 낱말
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
    raw: str  # 원문 요지
    line: int
    module: Optional[List[str]]  # 절대 import의 모듈 경로 성분(상대는 None)
    names: List[str]  # from-import의 대상 이름들
    candidates: List[List[str]]  # 격리 판정용 최상위 후보 경로(상대는 해소·클램핑 후)
    relative: bool


_IMPORT_RE = re.compile(r'(?m)^[ \t]*import[ \t]+([^\n]+)')
_FROM_RE = re.compile(r'(?m)^[ \t]*from[ \t]+([.\w]+)[ \t]*import\b')


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


def parse_imports(ms: MaskedSource, file_rel: str) -> List[ImportEdge]:
    """tokens_view에서 import/from 문을 수집한다. 상대 import는 **루트 클램핑**으로
    해소한다(잉여 `..`는 프로젝트 루트에서 멈춘다 — 나이브 join의 우회 벡터 차단,
    dddart _clampSegs 판형). web 최상위 패키지 기준 base = ['web'] + 파일 디렉터리."""
    edges: List[ImportEdge] = []
    tv: str = ms.tokens_view
    pkg_base: List[str] = ['web'] + segs_of(file_rel)[:-1]

    for m in _IMPORT_RE.finditer(tv):
        line: int = ms.line_of(m.start())
        for piece in m.group(1).split(','):
            mod: str = piece.strip().split(' as ')[0].strip().rstrip('\\').strip()
            if not re.fullmatch(r'[\w.]+', mod):
                continue
            parts: List[str] = [p for p in mod.split('.') if p]
            if parts:
                edges.append(ImportEdge('import %s' % mod, line, parts, [], [parts], False))

    for m in _FROM_RE.finditer(tv):
        line = ms.line_of(m.start())
        mod = m.group(1)
        names: List[str] = _names_after(tv, m.end())
        dots: int = len(mod) - len(mod.lstrip('.'))
        parts = [p for p in mod.lstrip('.').split('.') if p]
        if dots == 0:
            edges.append(ImportEdge('from %s import …' % mod, line, parts, names,
                                    [parts] if parts else [], False))
        else:
            base: List[str] = pkg_base[:max(0, len(pkg_base) - (dots - 1))]
            if parts:
                cands: List[List[str]] = [base + parts]
            else:
                cands = [base + [n] for n in names]
            edges.append(ImportEdge('from %s import …' % mod, line, None, names, cands, True))
    return edges


# ------------------------------------------------------------ 컨텍스트(게이트)


class BackstopContext:
    """대상 프로젝트 web/의 파일·디렉터리 인벤토리와 git diff 게이트.
    게이트 의미론(houserules §7): 구조·명명=added 파일/디렉터리, 격리·순수성=touched
    파일의 added 줄, 골격 완비=신규 단위 → 레거시(기존 drift) 불발화."""

    def __init__(self, root: Path, git_repo: bool, diff_base: Optional[str],
                 all_mode: bool, files: List[str], dirs: Set[str],
                 project_pkgs: Set[str], touched: Set[str], added: Set[str],
                 base_files: Set[str],
                 added_spans: Dict[str, List[Tuple[int, int]]]) -> None:
        self.root: Path = root
        self.web: Path = root / 'web'
        self.git_repo: bool = git_repo
        self.diff_base: Optional[str] = diff_base
        self.all_mode: bool = all_mode
        self.files: List[str] = files  # web-상대, 정렬
        self.files_set: Set[str] = set(files)
        self.dirs: Set[str] = dirs  # web-상대 디렉터리 전체
        self.project_pkgs: Set[str] = project_pkgs  # settings 실측 — WI1 deny 대상
        self.touched: Set[str] = touched
        self.added: Set[str] = added
        self.base_files: Set[str] = base_files  # diff-base 시점 파일(ls-tree)
        self.added_spans: Dict[str, List[Tuple[int, int]]] = added_spans
        self.notices: List[str] = []
        self._mask_cache: Dict[str, MaskedSource] = {}
        self._edge_cache: Dict[str, List[ImportEdge]] = {}
        self._sdk: Optional[object] = None
        # 영역 = web/ 직속 비컨테이너 디렉터리 (§1 — 트리 고정이라 적극 증명 불요)
        self.areas: Set[str] = {d for d in dirs if '/' not in d and d not in CONTAINER_DIRS}

    # ---- 게이트

    @property
    def gated(self) -> bool:
        return self.git_repo and self.diff_base is not None and not self.all_mode

    @property
    def can_detect_new_units(self) -> bool:
        return self.git_repo and self.diff_base is not None

    def is_added(self, f: str) -> bool:
        return (not self.gated) or f in self.added

    def is_touched(self, f: str) -> bool:
        return (not self.gated) or f in self.touched

    def is_added_dir(self, d: str) -> bool:
        """added 디렉터리 = diff-base에 그 경로 하위 파일이 0개(added 파일 포함 여부가
        아님 — 레거시 폴더에 새 파일을 넣어도 그 폴더는 added가 아니다). d=''는 web/."""
        if not self.gated:
            return True
        if d == '':
            return not self.base_files
        prefix: str = d + '/'
        return not any(f.startswith(prefix) for f in self.base_files)

    def line_is_added(self, f: str, line: int) -> bool:
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
            elif ext in ('.js', '.mjs', '.cjs'):
                ms = mask_js(text)
            else:
                ms = mask_html(text)
            self._mask_cache[f] = ms
        return ms

    def edges_of(self, f: str) -> List[ImportEdge]:
        edges: Optional[List[ImportEdge]] = self._edge_cache.get(f)
        if edges is None:
            edges = parse_imports(self.mask_of(f), f)
            self._edge_cache[f] = edges
        return edges

    @property
    def sdk(self):  # -> src.sdk_registry.SdkState (지연 적재 — 순환 import 회피)
        """등재 목록 상태와 WV2 통과 등재 파일 집합(houserules §9) — 한 실행에 한 번 계산한다."""
        if self._sdk is None:
            from .sdk_registry import SdkState
            self._sdk = SdkState.load(self.root)
        return self._sdk

    # ---- 빌드

    @staticmethod
    def build(root: Path, diff_base: Optional[str], all_mode: bool) -> 'BackstopContext':
        web: Path = root / 'web'
        if not web.is_dir():
            print('[backstop] 사용 오류: web/ 없음 — %s' % root, file=sys.stderr)
            sys.exit(1)

        # web 순회 (web-상대 posix 경로)
        files: List[str] = []
        dirs: Set[str] = set()
        for cur, dnames, fnames in os.walk(web):
            dnames[:] = [d for d in dnames if d not in ('__pycache__', '.git')]
            rel_dir: str = os.path.relpath(cur, web).replace(os.sep, '/')
            for d in dnames:
                dirs.add(d if rel_dir == '.' else rel_dir + '/' + d)
            for fn in fnames:
                if fn.endswith('.pyc'):
                    continue
                files.append(fn if rel_dir == '.' else rel_dir + '/' + fn)
        files.sort()

        project_pkgs: Set[str] = _project_pkgs(root)

        git_repo: bool = _git(root, ['rev-parse', '--is-inside-work-tree']) == 'true'
        touched: Set[str] = set()
        added: Set[str] = set()
        base_files: Set[str] = set()
        added_spans: Dict[str, List[Tuple[int, int]]] = {}

        if git_repo and diff_base is not None:
            repo_top: str = _git(root, ['rev-parse', '--show-toplevel']) or ''
            root_abs: str = os.path.realpath(str(root))
            repo_prefix: str = ''
            if root_abs != repo_top:
                repo_prefix = os.path.relpath(root_abs, repo_top).replace(os.sep, '/') + '/'

            def to_web_rel(repo_path: str) -> Optional[str]:
                if repo_prefix and not repo_path.startswith(repo_prefix):
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
                    # old, new 두 필드 — 새 경로만 added/touched
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
            # 2) porcelain — 미추적 파일(-uall 필수: 기본값은 신규 디렉터리를 한 줄로
            #    접어 신규 단위 전체가 누락된다 — dddart 적대 점검 P0 판형)
            p_out: str = _git_raw(root, ['status', '--porcelain', '-z', '--untracked-files=all']) or ''
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
            # 4) 수정 파일의 added 줄 범위 (WI·WP 게이트)
            hunk_re = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', re.M)
            for f in sorted(touched - added):
                d: str = _git_raw(root, ['diff', '-U0', diff_base, '--', 'web/' + f]) or ''
                spans: List[Tuple[int, int]] = []
                for m in hunk_re.finditer(d):
                    start: int = int(m.group(1))
                    length: int = 1 if m.group(2) is None else int(m.group(2))
                    if length > 0:
                        spans.append((start, start + length - 1))
                added_spans[f] = spans

        return BackstopContext(root, git_repo, diff_base, all_mode, files, dirs,
                               project_pkgs, touched, added, base_files, added_spans)

    @staticmethod
    def from_files(root: Path, files: List[str]) -> 'BackstopContext':
        """주어진 web-상대 파일 목록을 전부 added 로 보는 컨텍스트(빚 스캔 전용).
        dirs = 파일 조상 전부. base_files = 같은 목록이라 브라운필드 legacy core 소비
        판정(WP2)은 이 트리 기준이다. 기준점이 없으므로 WS5 는 기존 notice 로 생략된다."""
        ordered: List[str] = sorted(set(files))
        dirs: Set[str] = set()
        for f in ordered:
            s: List[str] = segs_of(f)
            for k in range(1, len(s)):
                dirs.add('/'.join(s[:k]))
        git_repo: bool = _git(root, ['rev-parse', '--is-inside-work-tree']) == 'true'
        return BackstopContext(root, git_repo, None, True, ordered, dirs,
                               _project_pkgs(root), set(ordered), set(ordered),
                               set(ordered), {})


def _project_pkgs(root: Path) -> Set[str]:
    """프로젝트 패키지 실측 — settings.py(또는 settings/) 보유 루트 직속 패키지 (§5① 대상)."""
    pkgs: Set[str] = set()
    for child in root.iterdir():
        if child.is_dir() and child.name not in ('web', '.git'):
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
