# dddjango-web 제품 선언 — 한 web 앱에 화면 제품이 여럿일 때의 design_system 뿌리 · 문서 셸 · 화면 범위
# (값 정본: discipline-houserules §1 · web 새 분기 — dddart 대응 없음 · 2.3.0).
#
# 선언은 web/ 안 `product_registry.json` 하나다(git 추적 — 승인 유입의 부모 스냅숏에도 실린다). 이름 · 자리 꼴 · 화면 범위만
# 적고 자리는 규약으로 고정한다(«파일트리가 곧 규약»):
#   { "schema": "dddjango-web-products/1",
#     "products": { "<id>": { "design_system": "flat" | "own", "bcs": ["<bc>" | "<area>/<bc>", …] | "*" }, … } }
#   flat(정확히 한 제품) — design_system/{foundation,theme,component,util} · 셸 root/scaffold/view/root_view.html
#   own                  — design_system/<id>/{foundation,theme,component,util} · 셸 root/scaffold/view/root_<id>_view.html
#                          (틀 CSS static/root/root_<id>_view.css)
#   bcs — web/application/ 아래 BC 전체 경로 배열, 또는 "*"(application 아래 나머지 BC 전부 · 최대 한 제품)
# 선언이 없으면 «기본 한 제품»이다 — 뿌리 하나 · 셸 하나, 모든 해석이 2.2.x 의 상수와 같고 제품 폴더를 자동 발견하지 않는다.
# 선언 오류는 판정 불가다(ProductError → 러너 exit 1) — 무선언 동작이나 빈 제품 목록으로 내려앉지 않는다. 검증은 검사
# 패밀리보다 앞선 공통 preflight 다(게이트 계열 · 빚 모드 · refactor_audit plan — `--only <무엇이든>` 에서도).
# «선언 없음» 은 선언 파일이 실제로 없을 때뿐이다(web/ 가 없는 첫 실행 포함) — 있는지 조사할 수 없으면(탐색 권한 등) 판정 불가다.
# BC 경로의 성분은 소문자 snake_case 식별자다(층 폴더 이름 · 컨테이너 이름 불가 · "*" 는 배열 밖 문자열로만) — 어느 BC 와도
# 맞을 수 없는 이름이 조용히 통과해 그 제품의 화면 범위가 비는 일을 막는다.
# 제품 뿌리를 뗀 상대 경로는 검사 분류에만 쓴다 — Finding 경로 · import edge · 빚 키는 실제 물리 경로(web 상대) 그대로다.
# 소속 판정(`product_of`): BC 의 파일(페이지 포함) = 그 BC 의 선언 제품(상속한 셸이 아니다) · 셸 = 선언된 셸의 제품 ·
#   design_system 파일 = 소유 뿌리의 제품 · BC 조각 CSS(static/application/…) = 그 BC 의 제품 ·
#   틀 CSS(static/root/root[_<id>]_view.css) = 그 셸의 제품 · 옛 배치 최상위 폴더와 그 밖 = 소속 없음.

from __future__ import annotations

import os
import posixpath
import re
import stat
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from .common import (DS_DIRS, FOUNDATION_FILES, LAYER_NAMES, ROOT_VIEW_TEMPLATE, MaskedSource, TemplateTag, bc_index, ext_of,
                     ref_path, segs_of, parse_template_edges, template_tags)
from .sdk_registry import RegistryError, strict_loads

REGISTRY: str = 'product_registry.json'  # web-상대
SCHEMA: str = 'dddjango-web-products/1'
FLAT: str = 'flat'
OWN: str = 'own'
STAR: str = '*'
_ID_RE = re.compile(r'^[a-z][a-z0-9_]*$')
_BC_PART_RE = re.compile(r'^[a-z_][a-z0-9_]*$')  # BC · area 폴더 = Python 패키지 이름(소문자 snake_case)
# BC · area 이름으로 금지된 컨테이너 이름(houserules §1 area 핵심 사실 ⓓ — 층 폴더 이름 LAYER_NAMES 와 함께)
_CONTAINER_NAMES: FrozenSet[str] = frozenset({'root', 'application', 'common', 'design_system'})
_DS: str = 'design_system'
_APP: str = 'application'


class ProductError(Exception):
    """제품 선언을 읽을 수 없다 — 판정 불가(exit 1 · 통과가 아니다)."""


class Products:
    """한 프로젝트의 제품 해석 — 선언이 없으면 이름 없는 «기본 한 제품»(flat = None · own 없음)."""

    def __init__(self, declared: bool = False, flat: Optional[str] = None, own: Tuple[str, ...] = (),
                 bcs: Optional[Dict[str, str]] = None, star: Optional[str] = None) -> None:
        self.declared: bool = declared
        self.flat: Optional[str] = flat          # 평면 뿌리의 제품 id
        self.own: Tuple[str, ...] = own          # 자기 뿌리를 가진 제품 id(정렬)
        self.bcs: Dict[str, str] = bcs or {}     # BC 전체 경로(`<bc>` · `<area>/<bc>`) → 제품 id
        self.star: Optional[str] = star          # "*" 를 가진 제품 — application 아래 나머지 BC 전부
        self.shells: FrozenSet[str] = frozenset([ROOT_VIEW_TEMPLATE] + [self.shell_of(p) for p in own])

    # ---- 자리

    def ds_root(self, pid: Optional[str]) -> str:
        return '%s/%s' % (_DS, pid) if pid in self.own else _DS

    def shell_of(self, pid: Optional[str]) -> str:
        return 'root/scaffold/view/root_%s_view.html' % pid if pid in self.own else ROOT_VIEW_TEMPLATE

    def ds_split(self, rel: str) -> Optional[Tuple[Optional[str], List[str]]]:
        """design_system 경로 → (소유 제품, 뿌리 안 상대 경로 성분). design_system 밖이면 None.
        평면 뿌리 직속의 선언된 own 뿌리(`design_system/<id>/…`)는 그 제품 몫이고 평면 제품의 소유 범위에서 빠진다."""
        s: List[str] = segs_of(rel)
        if s[0] != _DS:
            return None
        if len(s) > 1 and s[1] in self.own:
            return s[1], s[2:]
        return self.flat, s[1:]

    def ds_rel(self, rel: str) -> List[str]:
        """design_system 경로의 뿌리 안 상대 경로 성분(밖이면 빈 목록) — ST10 · NM10~12 가 이 성분에 같은 규칙을 건다."""
        split = self.ds_split(rel)
        return split[1] if split is not None else []

    def in_component(self, rel: str) -> bool:
        """어느 뿌리든 `component/` 아래 파일인가(선언 없으면 `design_system/component/` 접두와 같다)."""
        r: List[str] = self.ds_rel(rel)
        return len(r) >= 2 and r[0] == 'component'

    # ---- 소속

    def product_of_shell(self, rel: str) -> Optional[str]:
        """선언된 셸 템플릿의 제품(선언이 없거나 셸이 아니면 None)."""
        if not self.declared or rel not in self.shells:
            return None
        return self.flat if rel == ROOT_VIEW_TEMPLATE else next(p for p in self.own if self.shell_of(p) == rel)

    def product_of_bc(self, bc_path: str) -> Optional[str]:
        """BC 전체 경로(`<bc>` · `<area>/<bc>`)의 제품 — 적힌 BC 가 먼저, 그 밖은 "*" 제품."""
        return self.bcs.get(bc_path, self.star)

    def product_of(self, rel: str, areas: Set[str]) -> Optional[str]:
        """파일의 소속 제품(web-상대 물리 경로). 선언이 없거나 어느 제품에도 속하지 않으면 None."""
        if not self.declared:
            return None
        split = self.ds_split(rel)
        if split is not None:
            return split[0]
        view: str = ref_path(rel)  # 조각 CSS · 틀 CSS 는 소유자 자리로
        s: List[str] = segs_of(view)
        if s[0] == _APP:
            # 선언에 적힌 `<area>/<bc>` 전체 경로가 먼저다 — area 판별이 아직 안 선 중간 상태에서도 선언이 이긴다.
            if len(s) >= 4 and '%s/%s' % (s[1], s[2]) in self.bcs:
                return self.bcs['%s/%s' % (s[1], s[2])]
            bi: int = bc_index(s, areas)
            if len(s) <= bi + 1:
                return None  # BC 폴더 밖(application 직속 · area 직속 파일)
            return self.product_of_bc('/'.join(s[1:bi + 1]))
        if ext_of(view) == '.css':  # 틀 CSS static/root/root[_<id>]_view.css → 같은 stem 의 셸
            return self.product_of_shell(view[:-len('.css')] + '.html')
        return self.product_of_shell(view)

    def standard_css_owner(self, rel: str) -> Optional[str]:
        """제품 표준 자리 CSS 의 소유 제품 — foundation 표준 7 파일 · theme/app_theme.css · component/<군>/*.css · util/*.css.
        그 밖(표준 7 파일 밖 foundation 의 옛 값 파일 · 마크업 · design_system 밖)과 선언이 없을 때는 None(혼입 판정 밖).
        rel 은 실제로 실리는 파일이다 — 참조 원문에서 꼬리를 먼저 떼고 푼 경로(common.loaded_file · ctx.loads_of)를 받는다.
        import edge 의 target(원문 전체를 접은 경로)을 넘기지 않는다 — 꼬리 · 정규화 안 된 경로로 판정을 비켜 간다."""
        split = self.ds_split(rel) if self.declared else None
        if split is None or ext_of(rel) != '.css':
            return None
        pid, r = split
        standard: bool = ((len(r) == 2 and r[0] == 'foundation' and r[1] in FOUNDATION_FILES)
                          or r == ['theme', 'app_theme.css']
                          or (len(r) == 3 and r[0] == 'component')
                          or (len(r) == 2 and r[0] == 'util'))
        return pid if standard else None

    def planned_bcs(self, dirs: Set[str]) -> List[str]:
        """선언에 적혔지만 아직 web/application 에 없는 BC — `<제품> → <BC 경로>`(오류가 아니다 · 예정 BC)."""
        return ['%s → %s' % (pid, bc) for bc, pid in sorted(self.bcs.items(), key=lambda kv: (kv[1], kv[0]))
                if '%s/%s' % (_APP, bc) not in dirs]


# ------------------------------------------------------------------ 적재 · 검증


def _fail(reason: str) -> ProductError:
    return ProductError('제품 선언 web/%s — %s' % (REGISTRY, reason))


def _bc_path(pid: str, value: object) -> str:
    if not isinstance(value, str):
        raise _fail('제품 `%s` 의 bcs 항목은 문자열(BC 경로)이다: %r' % (pid, value))
    parts: List[str] = value.split('/')
    if value.startswith('/') or '' in parts or '.' in parts or '..' in parts or len(parts) > 2:
        raise _fail('제품 `%s` 의 BC 경로 꼴 오류 %r — web/application/ 아래 `<bc>` 또는 `<area>/<bc>`'
                    '(절대 경로 · `..` · 빈 성분 · 세 성분 이상 불가)' % (pid, value))
    if not all(_BC_PART_RE.fullmatch(x) for x in parts):
        raise _fail('제품 `%s` 의 BC 이름 꼴 오류 %r — 성분마다 소문자 snake_case 식별자다'
                    '("*" 는 배열 밖 문자열 `"bcs": "*"` 로만 쓴다)' % (pid, value))
    if LAYER_NAMES & set(parts):
        raise _fail('제품 `%s` 의 BC 경로 %r — 층 폴더 이름(%s)은 BC · area 이름이 될 수 없다'
                    % (pid, value, ' · '.join(sorted(LAYER_NAMES & set(parts)))))
    if _CONTAINER_NAMES & set(parts):
        raise _fail('제품 `%s` 의 BC 경로 %r — 컨테이너 이름(%s)은 BC · area 이름이 될 수 없다'
                    % (pid, value, ' · '.join(sorted(_CONTAINER_NAMES & set(parts)))))
    return value


def load_products(root: Path) -> Products:
    """`<root>/web/product_registry.json` 적재 · 검증. 파일이 없으면 «기본 한 제품». 오류는 전부 ProductError."""
    path: Path = root / 'web' / REGISTRY
    try:
        mode: int = os.lstat(path).st_mode
    except (FileNotFoundError, NotADirectoryError):
        return Products()  # 실제 부재 — 선언 없음(web/ 가 없는 첫 실행 포함)
    except OSError as error:  # 탐색 권한 등 — 있는지조차 모른다. «선언 없음» 으로 내려앉지 않는다
        raise _fail('있는지 조사할 수 없다(%s)' % error)
    if not stat.S_ISREG(mode):
        raise _fail('일반 파일이 아니다(폴더 · 링크)')
    try:
        data: object = strict_loads(path.read_bytes())
    except (OSError, RegistryError) as error:
        raise _fail(str(error))
    if not isinstance(data, dict):
        raise _fail('최상위는 객체다')
    unknown: List[str] = sorted(set(data) - {'schema', 'products'})
    if unknown:
        raise _fail('모르는 키 %s — 최상위는 schema · products 뿐' % ', '.join(unknown))
    if data.get('schema') != SCHEMA:
        raise _fail('schema 는 %r 다(%r)' % (SCHEMA, data.get('schema')))
    products: object = data.get('products')
    if not isinstance(products, dict):
        raise _fail('products 는 객체(<제품 id> → 선언)다')
    flats: List[str] = []
    owns: List[str] = []
    bcs: Dict[str, str] = {}
    stars: List[str] = []
    for pid, spec in products.items():
        if not _ID_RE.fullmatch(pid) or pid in DS_DIRS:
            raise _fail('제품 id %r — 소문자 snake_case 이고 %s 과 겹치지 않아야 한다' % (pid, ' · '.join(sorted(DS_DIRS))))
        if not isinstance(spec, dict):
            raise _fail('제품 `%s` 의 값은 객체(design_system · bcs)다' % pid)
        unknown = sorted(set(spec) - {'design_system', 'bcs'})
        if unknown or set(spec) != {'design_system', 'bcs'}:
            raise _fail('제품 `%s` 의 키는 design_system · bcs 둘이다%s'
                        % (pid, ' — 모르는 키 ' + ', '.join(unknown) if unknown else ''))
        if spec['design_system'] not in (FLAT, OWN):
            raise _fail('제품 `%s` 의 design_system 은 "flat" 또는 "own" 이다(%r)' % (pid, spec['design_system']))
        (flats if spec['design_system'] == FLAT else owns).append(pid)
        listed: object = spec['bcs']
        if listed == STAR:
            stars.append(pid)
            continue
        if not isinstance(listed, list):
            raise _fail('제품 `%s` 의 bcs 는 BC 경로 배열 또는 "*" 다' % pid)
        for value in listed:
            bc: str = _bc_path(pid, value)
            if bc in bcs:
                raise _fail('BC `%s` 가 두 번 적혔다(%s)' % (bc, '제품 `%s` 안 중복' % pid if bcs[bc] == pid
                                                         else '제품 `%s` · `%s`' % (bcs[bc], pid)))
            bcs[bc] = pid
    if len(flats) != 1:
        raise _fail('design_system "flat" 제품은 정확히 하나다(%d개%s)'
                    % (len(flats), ' — ' + ' · '.join(flats) if flats else ''))
    if len(stars) > 1:
        raise _fail('bcs "*" 는 최대 한 제품이다(%s)' % ' · '.join(stars))
    return Products(True, flats[0], tuple(sorted(owns)), bcs, stars[0] if stars else None)


def declaration_error(root: Path) -> Optional[str]:
    """선언 오류 사유(없으면 None) — 컨텍스트를 만들지 않는 입구(빚 모드 · refactor_audit)의 preflight.
    오류 여부만 보고 적재 결과는 버린다 — 빚 모드에서는 뒤이은 스캔의 컨텍스트가 선언을 다시 읽는다(`products_state`)."""
    try:
        load_products(root)
    except ProductError as error:
        return str(error)
    return None


def products_state(ctx: object) -> Products:
    """백스톱 컨텍스트의 제품 해석 — 컨텍스트마다 한 번 적재해 그 컨텍스트에 붙여 둔다(`sdk_state` 꼴).
    게이트의 `BackstopContext.build` 와 빚 스캔의 `from_files` 가 이 하나를 쓴다. 선언 오류면 ProductError.
    한 실행에 한 번은 아니다 — 빚 모드는 러너의 사전 점검(`declaration_error`)과 스캔의 컨텍스트가 따로 읽는다."""
    state: Optional[Products] = getattr(ctx, '_products', None)
    if state is None:
        state = load_products(getattr(ctx, 'root'))
        setattr(ctx, '_products', state)
    return state


def preflight(ctx: object) -> Products:
    """공통 preflight — 검사 패밀리보다 먼저 선언을 적재 · 검증하고(오류면 ProductError) 알림을 싣는다:
    (게이트가 살아 있을 때) 선언 파일이 기준점 뒤 바뀌었다는 한 줄 · 예정 BC 한 줄 · area 폴더 이름만 적은 BC 한 줄.
    선언이 없으면 아무것도 하지 않는다."""
    state: Products = products_state(ctx)
    notices: List[str] = getattr(ctx, 'notices')
    if getattr(ctx, 'gated') and (REGISTRY in getattr(ctx, 'touched') or (
            REGISTRY in getattr(ctx, 'base_files') and REGISTRY not in getattr(ctx, 'files_set'))):
        notices.append('[info] 제품 선언이 기준점 뒤 바뀌었다 — G2 배너에 diff 원문(web/%s — 선언은 사용자 결정으로만 바뀐다)'
                       % REGISTRY)
    planned: List[str] = state.planned_bcs(getattr(ctx, 'dirs')) if state.declared else []
    if planned:
        notices.append('[info] 제품 선언의 BC 가 아직 web/application 에 없다(예정 BC — 오류 아님): %s' % ' · '.join(planned))
    areas: Set[str] = getattr(ctx, 'areas')
    as_area: List[str] = ['%s → %s' % (pid, bc) for bc, pid in sorted(state.bcs.items(), key=lambda kv: (kv[1], kv[0]))
                          if bc in areas]
    if as_area:  # area 판별은 휴리스틱이라 오류로 막지 않는다 — 한 성분 이름이 area 폴더면 그 아래 BC 와는 맞지 않는다
        notices.append('[info] 제품 선언의 %s 는 area 폴더다 — BC 는 <area>/<bc> 전체 경로로 적는다'
                       '(지금은 그 아래 BC 가 이 제품으로 읽히지 않는다)' % ' · '.join(as_area))
    return state


# html.parser 가 파이썬 판에 따라 내는 예외 — 3.9 는 _markupbase.error 의 NotImplementedError · 3.10+ 는 AssertionError
_PARSER_ERRORS: Tuple[type, ...] = (AssertionError, NotImplementedError)
_MARKER_TEXT_RE = re.compile(r'data-root-shell|hx-boost|hx-history-elt', re.I)  # 별칭 data-hx-* 도 이 글자를 품는다


def parsed_tags(text: str) -> Optional[List[TemplateTag]]:
    """template_tags — 이 파이썬의 HTML 파서가 못 읽는 글자(3.9 의 `<![foo` 등)면 None = 판독 불가."""
    try:
        return template_tags(text)
    except _PARSER_ERRORS:
        return None


def shell_candidate(text: str) -> bool:
    """G0 와 같은 후보 표지 셋 — 완전한 지속 셸 꼴의 판정은 SH2 몫이다.
    파서가 못 읽는 셸은 표지 글자가 있으면 후보(SH2 가 판독 불가로 붉힌다) · 없으면 표지 없는 셸이다."""
    tags = parsed_tags(text)
    if tags is None:
        return _MARKER_TEXT_RE.search(text) is not None
    return any((tag.name == 'body' and 'data-root-shell' in tag.attrs)
               or (tag.name == 'nav' and any(a in tag.attrs for a in ('hx-boost', 'data-hx-boost')))
               or (tag.name == 'main' and any(a in tag.attrs for a in ('hx-history-elt', 'data-hx-history-elt')))
               for tag in tags)


def persistent_shells(ctx: object) -> FrozenSet[str]:
    """표준 셸만 후보로 발견한다 — 표준 셸 밖의 표지는 SH1 위반이다."""
    cached = getattr(ctx, '_persistent_shells', None)
    if cached is None:
        cached = frozenset(f for f in products_state(ctx).shells if f in ctx.files_set
                           and shell_candidate(ctx.mask_of(f).no_comments))
        setattr(ctx, '_persistent_shells', cached)
    return cached


_DJANGO_TOKEN_RE = re.compile(r'\{%.*?%\}|\{\{.*?\}\}|\{#.*?#\}')  # Django Lexer 의 토큰 경계 — 줄을 넘지 않는다


def shell_directives(original: str, no_comments: str) -> str:
    """SH 지시문 뷰 — Django 가 실제 지시문으로 읽는 `{%` 만 남기고 HTML·좌표·개행은 보존한다.
    토큰 경계와 verbatim 구간은 원문에서 Django Lexer 와 같게 읽는다: 변수·주석 토큰 안이나 여러 줄에 걸친 `{% %}` 글자,
    verbatim 안의 지시문은 글자다 · verbatim 은 내용이 `end` + 시작 내용과 글자까지 같은 태그에서만 끝난다.
    주석 안 지시문은 no_comments 가 이미 가렸다.
    """
    real: List[Tuple[int, int]] = []  # 실제 지시문 토큰의 범위(왼쪽부터 · 겹치지 않음)
    closing: Optional[str] = None
    for match in _DJANGO_TOKEN_RE.finditer(original):
        token: str = match.group()
        if not token.startswith('{%'):
            continue
        content: str = token[2:-2].strip()
        if closing is not None:
            if content == closing:
                closing = None
        elif content[:9] in ('verbatim', 'verbatim '):
            closing = 'end' + content
        else:
            real.append((match.start(), match.end()))
    chars: List[str] = list(no_comments)
    index: int = 0
    at: int = no_comments.find('{%')
    while at != -1:
        while index < len(real) and real[index][1] <= at:
            index += 1
        if index == len(real) or at < real[index][0]:  # 실제 지시문 토큰 밖 — 토큰 안의 글자(인자)는 건드리지 않는다
            chars[at:at + 2] = '  '
        at = no_comments.find('{%', at + 2)
    return ''.join(chars)


def _persistent_graph(ctx: object) -> Dict[str, List[Tuple[str, str, int]]]:
    """SH 전용 렌더 간선. 기존 parse_template_edges 의 대상·빚 키는 바꾸지 않는다."""
    cached = getattr(ctx, '_persistent_edges', None)
    if cached is not None:
        return cached
    graph: Dict[str, List[Tuple[str, str, int]]] = {}
    unreadable: Dict[str, List[Tuple[int, str]]] = {}
    for f in ctx.files:
        if ext_of(f) != '.html':
            continue
        ms = ctx.mask_of(f)
        directives = shell_directives(ms.original, ms.no_comments)
        render_ms = MaskedSource(ms.original, directives, ms.tokens_view, ms.line_starts)
        graph[f] = []
        edges = [edge for edge in parse_template_edges(render_ms) if edge.kind in ('extends', 'include')]
        literals: Set[Tuple[str, str, int]] = set()
        for match in re.finditer(r'\{%-?\s*(extends|include)\s+(.*?)%\}', directives, re.S):  # 인자 안 % 도 읽는다(`%}` 까지)
            literal = re.match(r'''(["'])([^"'\n]+)\1(?:\s|$)''', match.group(2).strip())
            if literal is None:
                unreadable.setdefault(f, []).append((ms.line_of(match.start()), '글자 아닌 인자'))
            else:
                literals.add((match.group(1), literal.group(2).strip().lstrip('/'), ms.line_of(match.start())))
        for edge in edges:
            if (edge.kind, edge.target, edge.line) not in literals:
                continue
            name: str = edge.target
            if name.startswith(('./', '../')):
                name = posixpath.normpath(posixpath.join(posixpath.dirname(f), name))
            if name == '..' or name.startswith('../') or (edge.kind == 'extends' and name == f):
                unreadable.setdefault(f, []).append((edge.line, '뿌리 밖 경로 또는 자기 extends'))
            else:
                graph[f].append((edge.kind, name, edge.line))
    setattr(ctx, '_persistent_edges', graph)
    setattr(ctx, '_persistent_unreadable', unreadable)
    return graph


def render_closure(ctx: object, files: Set[str], parents: bool = False) -> Set[str]:
    """include 닫힘. include 로 들어온 템플릿과 그 부모에서만 extends 도 따른다.
    parents=True 는 새 연결 대상의 부모 쪽 닫힘을 검사할 때 쓴다. 방문 집합은 자기 include·순환을 끝낸다.
    """
    graph = _persistent_graph(ctx)
    pending = [(f, parents) for f in files]
    visited: Set[Tuple[str, bool]] = set()
    while pending:
        f, follow_parent = pending.pop()
        if (f, follow_parent) in visited:
            continue
        visited.add((f, follow_parent))
        for kind, target, _line in graph.get(f, []):
            if kind == 'include' or follow_parent:
                pending.append((target, True))
    return {f for f, _ in visited}


def persistent_scope(ctx: object) -> Dict[str, FrozenSet[str]]:
    """제품 소속 + 지속 셸에 이르는 상속 사슬 + 렌더 의존 닫힘(상대 경로·방문 집합)."""
    cached = getattr(ctx, '_persistent_scope', None)
    if cached is not None:
        return cached
    state = products_state(ctx)
    result: Dict[str, FrozenSet[str]] = {}
    seeds: Dict[str, FrozenSet[str]] = {}
    chains: Dict[str, FrozenSet[str]] = {}
    for shell in sorted(persistent_shells(ctx)):
        graph = _persistent_graph(ctx)
        pid = state.product_of_shell(shell)
        seed: Set[str] = set()
        for f in ctx.files:
            if ext_of(f) not in ('.html', '.css'):
                continue
            if state.declared:
                if pid is not None and state.product_of(f, ctx.areas) == pid:
                    seed.add(f)
            elif (f.startswith('application/') and '/presentation_layer/' in f) or f.startswith((
                    'root/scaffold/view/', 'design_system/', 'static/application/', 'static/root/')):
                seed.add(f)
        if not state.declared:
            seed.update(path for _line, path in ctx.loads_of(shell) if ext_of(path) == '.css')
        chain: Set[str] = {shell}
        reverse: Dict[str, Set[str]] = {}
        for f, edges in graph.items():
            for kind, target, _line in edges:
                if kind == 'extends':
                    reverse.setdefault(target, set()).add(f)
        pending = [shell]
        while pending:
            for f in reverse.get(pending.pop(), set()) - chain:
                chain.add(f)
                pending.append(f)
        seeds[shell] = frozenset(seed)
        chains[shell] = frozenset(chain)
        result[shell] = frozenset(seed | render_closure(ctx, seed | chain))
    setattr(ctx, '_persistent_scope', result)
    setattr(ctx, '_persistent_seeds', seeds)
    setattr(ctx, '_persistent_chains', chains)
    return result
