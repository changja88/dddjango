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

# houserules §1 트리 v3.1 — web/ 직속 고정 파일·컨테이너
WEB_TOP_FILES: Set[str] = {'urls.py', 'apps.py'}
CONTAINER_DIRS: Set[str] = {'base', 'client', 'design_system', 'static'}
# houserules §3 — 마커 파일은 «직속 파일 금지»의 명시 예외
MARKER_FILES: Set[str] = {'__init__.py', '.gitkeep'}
# houserules §1·§2 — 화면 개념 종류 폴더 5종 (form은 조건 생성)
KIND_DIRS: Set[str] = {'view', 'view_model', 'state', 'form', 'section'}
PY_KIND_DIRS: Set[str] = {'view', 'view_model', 'state', 'form'}  # §3 마커=__init__.py
HTML_KIND_DIRS: Set[str] = {'section', 'widget'}  # §3 마커=.gitkeep
# houserules §1 — 영역·화면 이름 deny(컨테이너명·종류명)
RESERVED_NAMES: Set[str] = CONTAINER_DIRS | KIND_DIRS | {'web', 'widget'}
# houserules §1·§3 — static/ 직속 4종 + 조건부 2종
STATIC_DIRS: Set[str] = {'css', 'js', 'htmx', 'images', 'fonts', 'files'}
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

        # 프로젝트 패키지 실측 — settings.py(또는 settings/) 보유 루트 직속 패키지 (§5① 대상)
        project_pkgs: Set[str] = set()
        for child in root.iterdir():
            if child.is_dir() and child.name not in ('web', '.git'):
                if (child / 'settings.py').is_file() or (child / 'settings').is_dir():
                    project_pkgs.add(child.name)

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


def _git(root: Path, args: List[str]) -> Optional[str]:
    out: Optional[str] = _git_raw(root, args)
    return out.strip() if out is not None else None


def _git_raw(root: Path, args: List[str]) -> Optional[str]:
    r = subprocess.run(['git', '-C', str(root)] + args,
                       capture_output=True, text=True, errors='replace')
    return r.stdout if r.returncode == 0 else None
