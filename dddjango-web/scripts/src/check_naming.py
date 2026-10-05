# NM — 식별자·명명 19종 (NM1~NM6 · NM8~NM20 · NM7 비움). 게이트: added 파일.
#
# *왜 결정적 백스톱인가*: 종류 폴더↔접미사↔클래스명의 3중 일치(제1 규약 §7)는
# casefold 문자열 비교로 환원된다. 본문 검사(NM9·NM10·NM13)는 주석·문자열 마스킹
# 본문 + 괄호 균형 스캔으로 멀티라인 변형까지 버틴다.
# 거짓양성 게이트 = added 한정 + 검사별 명시 예외(router·exception.py·Django 고정 자리).
# (판형: dddart check_naming.dart — NM1~NM17 번호 그대로 · NM7 = @riverpod 허용 위치라 비움 ·
#  NM8 = common 상태 동작 proxy(common @riverpod 자리) · NM18~NM20 = web 새 검사)

from __future__ import annotations

import ast
import re
from typing import Dict, List, Optional, Set, Tuple

from .common import (
    BackstopContext, Finding, FOUNDATION_TOKENS, base_name_of, bc_dir_of, bc_of, casefold, ext_of, has_seg,
    is_bc_root_path, is_string_literal, first_arg_of, parent_dir_of, scan_tokens, segs_of, stem_of,
    top_level_decls,
)

# 접미사 → 종류 (긴 것 우선 매칭 — 정의 순서)
_SUFFIX_KIND: Dict[str, str] = {
    '_shared_state.py': 'shared_state',
    '_ui_extension.py': 'ui_extension',
    '_specification.py': 'specification',
    '_data_source.py': 'data_source',
    '_use_case.py': 'use_case',
    '_section.html': 'section',
    '_service.py': 'service',
    '_handler.py': 'handler',
    '_widget.html': 'widget',
    '_view.html': 'view',
    '_state.py': 'state',
    '_view.py': 'view',
    '_repo.py': 'repository',
    '_vm.py': 'view_model',
}

# 종류 폴더 → 허용 접미사 집합
_KIND_SUFFIXES: Dict[str, List[str]] = {
    'use_case': ['_use_case.py'],
    'view_model': ['_vm.py'],
    'state': ['_state.py'],
    'shared_state': ['_shared_state.py'],
    'service': ['_service.py'],
    'data_source': ['_data_source.py'],
    'repository': ['_repo.py'],
    'view': ['_view.py', '_view.html'],
    'section': ['_section.html'],
    'widget': ['_widget.html'],
    'ui_extension': ['_ui_extension.py'],
    'domain_service': ['_service.py'],
    'specification': ['_specification.py'],
    'handler': ['_handler.py'],
}

_DENY_STEMS: List[Tuple[str, str]] = [
    ('_app', '_use_case'), ('_bridge', '_shared_state'), ('_block', '_section'),
    ('_view_state', '_state'), ('_spec', '_specification'), ('_btn', '_button'),
]  # dddart 목록 그대로 — `…_view_vm` 은 짝 view 부재로 NM4 가 잡는다(houserules §4-3)

_FOUNDATION_PREFIX: Dict[str, Tuple[str, ...]] = {
    t: (('--duration-', '--easing-') if t == 'duration' else ('--%s-' % t,)) for t in FOUNDATION_TOKENS}

_SNAKE_RE = re.compile(r'^[a-z0-9_]+(\.[a-z0-9]+)+$')
_KEBAB_VAR_RE = re.compile(r'^--[a-z][a-z0-9]*(-[a-z0-9]+)*$')
_CUSTOM_PROP_RE = re.compile(r'(?<![\w-])(--[\w-]+)\s*:')
_COLOR_RE = re.compile(
    r'(?<![&\w])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9a-zA-Z_-])'
    r'|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\s*\(')
_TYPO_OK_RE = re.compile(r'^\s*(?:(?:var\(\s*--[\w-]+\s*\)\s*)+|inherit|initial|unset|revert|revert-layer)\s*'
                         r'(?:!important\s*)?$', re.I)
_HTMX_STATE_CLASSES = frozenset({'htmx-request', 'htmx-indicator', 'htmx-settling', 'htmx-swapping', 'htmx-added'})
_DECL_RE = re.compile(r'([-\w]+)\s*:\s*([^;{}]*)(?=[;}]|\Z)')  # 선언 `속성: 값` — 값 뒤가 `;`·`}`·끝일 때만(선택자 `a:hover {` 제외)
_TYPO_PROPS = frozenset({'font-size', 'font-family', 'font-weight', 'line-height', 'font'})
_STYLE_ATTR_RE = re.compile(r'''\bstyle\s*=\s*("([^"]*)"|'([^']*)')''', re.I)
_STYLE_BLOCK_RE = re.compile(r'<style\b[^>]*>(.*?)</style\s*>', re.I | re.S)
_PAINT_ATTR_RE = re.compile(r'''\b(fill|stroke|stop-color|flood-color|lighting-color|color|bgcolor)\s*=\s*("([^"]*)"|'([^']*)')''', re.I)
_ROUTE_ATTR_RE = re.compile(r'''\b(href|action|formaction|hx-get|hx-post|hx-put|hx-patch|hx-delete)\s*=\s*["']\s*/(?!/)''', re.I)
_URL_TAG_RE = re.compile(r'\{%-?\s*url\s')
# NM8 — common 의 상태 동작 proxy(시그널 수신 연결 · 변경 통지 · 세션 쓰기)
_COMMON_STATE_RE = re.compile(
    r'@receiver\b|\breceiver\s*\(|\.connect\s*\(|\bSignal\s*\(|\bsession\s*\[[^\]\n]*\]\s*=(?!=)'
    r'|\bsession\.(?:update|setdefault|pop|clear|flush|cycle_key|set_expiry)\s*\(')
_ALIAS_RE = re.compile(r'(?m)^(?:type[ \t]+)?([A-Za-z_]\w*)[ \t]*(?::[ \t]*TypeAlias[ \t]*)?(?:\[[^\]\n]*\])?[ \t]*=[ \t]*[^=\n]*\|')


def run_naming(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    added: List[str] = [f for f in ctx.files if ctx.is_added(f)]

    # BC별 view 접두 수집(파일시스템 기준 — NM4·5·6, 같은 슬라이스 동시 생성 합법)
    view_prefixes: Dict[str, Set[str]] = {}
    for f in ctx.files:
        b: str = base_name_of(f)
        if parent_dir_of(f) == 'view' and (b.endswith('_view.py') or b.endswith('_view.html')):
            owner: str = bc_of(f, ctx.areas) or ('root' if f.startswith('root/scaffold/') else '')
            if owner:
                view_prefixes.setdefault(owner, set()).add(b[:b.rindex('_view.')])

    for f in added:
        segs: List[str] = segs_of(f)
        base: str = base_name_of(f)
        ext: str = ext_of(f)
        stem: str = stem_of(f)
        parent: str = parent_dir_of(f)
        bc: Optional[str] = bc_of(f, ctx.areas)
        in_app: bool = has_seg(f, 'application_layer')
        in_static: bool = segs[0] == 'static'
        vendored: bool = f.startswith('static/vendor/') or f.startswith('static/htmx/')
        is_router: bool = (base.endswith('_router.py') and (
            is_bc_root_path(f, ctx.areas) or f == 'root/router/root_router.py')) or f == 'urls.py'
        if base == '__init__.py':
            continue

        # ---- NM1: 종류 폴더 ↔ 접미사 (긴 접미사 우선)
        kind_of_folder: Optional[List[str]] = _KIND_SUFFIXES.get(parent)
        if kind_of_folder is not None and not in_static and _folder_context_ok(f, parent):
            file_kind: Optional[str] = next((s for s in _SUFFIX_KIND if base.endswith(s)), None)
            if file_kind is None or file_kind not in kind_of_folder:
                out.append(Finding('NM1', f, None,
                    '`%s/` 안 파일 접미사 불일치 — 허용: %s%s' % (
                        parent, '·'.join(kind_of_folder),
                        ' (현재 접미사는 %s 종류)' % _SUFFIX_KIND[file_kind] if file_kind else ''),
                    '제1 규약 §7.1-2', '종류는 폴더가 결정하고 접미사가 재확인한다 — 접미사를 폴더 종류에 맞춘다.'))

        # ---- NM2: 구접미사 deny
        if not in_static:
            for deny, good in _DENY_STEMS:
                if stem.endswith(deny):
                    out.append(Finding('NM2', f, None, '구접미사 `%s`' % deny, '제1 규약 §8·§9-8',
                        '`%s` → `%s` 로 개명한다.' % (deny, good)))
                    break

        ms = ctx.mask_of(f)
        decls = top_level_decls(ms) if ext == '.py' else []
        public_classes = [d for d in decls if d[0] == 'class' and not d[1].startswith('_')]

        # ---- NM3: 파일당 public 클래스 1개 + 파일명=클래스명 casefold
        if ext == '.py' and base != 'exception.py' and not is_router and f not in ('apps.py', 'urls.py') \
                and not _is_union_file(ms, stem):
            if len(public_classes) > 1:
                out.append(Finding('NM3', f, public_classes[1][2],
                    'top-level public 클래스 %d개(%s) — 한 파일 한 클래스' % (
                        len(public_classes), ', '.join(d[1] for d in public_classes)),
                    '제1 규약 §7.1-1', '두 번째 선언을 자기 파일로 분리한다(합 타입이면 파일명과 같은 별칭 `<Name> = A | B`로 묶는다).'))
            elif len(public_classes) == 1 and casefold(public_classes[0][1]) != casefold(stem):
                out.append(Finding('NM3', f, public_classes[0][2],
                    '클래스명 `%s` ≠ 파일명(casefold) — 파일명 = 주 클래스명 snake_case' % public_classes[0][1],
                    '제1 규약 §7.1-1', '파일명 또는 클래스명을 일치시킨다.'))

        # ---- NM4: 삼총사(VM 기준 단방향)
        if parent == 'view_model' and base.endswith('_vm.py') and (in_app or f.startswith('root/scaffold/')):
            prefix: str = base[:-len('_vm.py')]
            scope: str = (bc_dir_of(f, ctx.areas) + '/') if bc is not None else 'root/scaffold/'
            need: List[str] = ['%s_view.html' % prefix, '%s_state.py' % prefix]
            if bc is not None:
                need.insert(0, '%s_view.py' % prefix)
            missing: List[str] = [n for n in need
                                  if not any(g.startswith(scope) and base_name_of(g) == n for g in ctx.files)]
            if missing:
                out.append(Finding('NM4', f, None, '삼총사 미완 — 같은 접두 %s 부재' % '·'.join(missing),
                    '제1 규약 §7.1-3', 'VM이 있으면 view(.py+.html)·state가 1:1:1로 대응한다.'))

        # ---- NM5: section 접두 = 소속 화면
        if parent == 'section' and bc is not None and base.endswith('_section.html'):
            prefixes: Set[str] = view_prefixes.get(bc, set())
            if not any(base.startswith(p + '_') for p in prefixes):
                out.append(Finding('NM5', f, None,
                    'section 파일명이 같은 BC의 어떤 view 접두로도 시작하지 않음(view: %s)' % (
                        '·'.join(sorted(prefixes)) if prefixes else '없음'),
                    '제1 규약 §3.5', 'section은 한 화면 전속 — `<화면>…_section.html`. 비전속이면 widget이다.'))

        # ---- NM6: widget 파일명에 view 접두 금지(BC명 동일 접두는 제외)
        if parent == 'widget' and bc is not None and base.endswith('_widget.html'):
            for p in sorted(view_prefixes.get(bc, set())):
                if casefold(p) == casefold(bc):
                    continue  # BC명=화면명은 도메인 어휘와 구별 불가
                if p in base:
                    out.append(Finding('NM6', f, None, 'widget 파일명에 화면 이름 `%s` 포함 — 화면 비전속 부품' % p,
                        '제1 규약 §3.5', '화면 전속이면 section으로, 진짜 재사용 부품이면 화면 이름을 뗀다.'))
                    break

        # ---- NM8: common 상태 동작 금지 (proxy — dddart common @riverpod 자리)
        if segs[0] == 'common' and ext == '.py':
            hits = scan_tokens(ms, _COMMON_STATE_RE)
            if hits:
                out.append(Finding('NM8', f, hits[0][0],
                    'common에서 상태 동작(시그널 수신 연결·변경 통지·세션 쓰기) — common은 살아있는 상태를 갖지 않는다'
                    '(호출당하는 도구, 행위자 아님)', '제1 규약 §6·§9-13',
                    '정체를 따져 제자리로 — BC 어휘면 그 BC shared_state·service, 전 BC 배선이면 root handler·initializer.'))

        # ---- NM9: view가 자기 VM·SharedState 외 상태원 소비(import 근사)
        if parent == 'view' and base.endswith('_view.py') and bc is not None:
            prefix = base[:-len('_view.py')]
            for e in ctx.edges_of(f):
                t: str = e.target or ''
                if not (e.internal and t and has_seg(t, 'application_layer')):
                    continue
                tp: str = parent_dir_of(t)
                bad: bool = (tp == 'view_model' and base_name_of(t) != '%s_vm.py' % prefix) or tp in ('use_case', 'service')
                if bad and ctx.line_is_added(f, e.line):
                    out.append(Finding('NM9', f, e.line,
                        'view가 자기 VM(`%s_vm.py`)·SharedState 외 상태원 소비: `%s`' % (prefix, t),
                        '제1 규약 §3.5·§9-10',
                        '다른 데이터가 필요하면 자기 VM이 UseCase로 가져와 State에 담는다 — view는 바인딩이지 조회가 아니다.'))

        # ---- NM10: 시각 리터럴 금지(색 · typography) — foundation 밖
        in_visual: bool = ((bc is not None and has_seg(f, 'presentation_layer'))
                           or f.startswith('design_system/component/') or f.startswith('root/scaffold/')
                           or f.startswith('static/application/') or f.startswith('static/root/'))
        if in_visual and ext in ('.html', '.css'):
            for line, what in _visual_literals(ms, ext):
                out.append(Finding('NM10', f, line, '시각 리터럴 `%s` — foundation 토큰만' % what,
                    '제1 규약 §6·§9-12',
                    '`var(--color-…)`·`font: var(--typography-…)` 토큰을 쓴다 — 없는 값이면 foundation에 토큰을 추가하는 것이 먼저.'))

        # ---- NM11: foundation 토큰 표기
        if len(segs) == 3 and segs[0] == 'design_system' and segs[1] == 'foundation' and ext == '.css':
            token: str = stem[len('app_'):] if stem.startswith('app_') else ''
            allowed: Tuple[str, ...] = _FOUNDATION_PREFIX.get(token, ())
            for m in _CUSTOM_PROP_RE.finditer(ms.no_comments):
                name: str = m.group(1)
                if not _KEBAB_VAR_RE.match(name) or (allowed and not name.startswith(allowed)):
                    out.append(Finding('NM11', f, ms.line_of(m.start()),
                        '토큰 변수 `%s` — 이 파일의 접두(%s) + lower-kebab' % (name, '·'.join(allowed) or '파일별 접두'),
                        '제1 규약 §6', '파일별 접두(--color-*·--typography-* …)와 소문자 kebab 으로 — 표기 혼재 금지.'))

        # ---- NM12: component 부품군 표기
        if len(segs) == 4 and segs[0] == 'design_system' and segs[1] == 'component':
            group: str = segs[2]
            if base.startswith('ds_'):
                out.append(Finding('NM12', f, None, '`ds_` 접두 — 컴포넌트는 무접두(종류 접미사가 구별자)',
                    '제1 규약 §6', '접두를 뗀다.'))
            if ext not in ('.html', '.css') or (stem != group and not stem.endswith('_' + group)):
                out.append(Finding('NM12', f, None,
                    '부품군 `%s/` 안 파일명 — `*_%s.html`·`.css`(기본 부품은 `%s.html`)' % (group, group, group),
                    '제1 규약 §6', '부품군 폴더 = 파일 접미사 = CSS 클래스 접미사.'))
            elif ext == '.css':
                cls_prefix: str = stem.replace('_', '-')
                for line, cls in _css_classes(ms, cls_prefix):
                    if not (cls == cls_prefix or cls.startswith(cls_prefix + '-') or cls.startswith(cls_prefix + '_')):
                        out.append(Finding('NM12', f, line,
                            'component CSS 클래스 `.%s` — 접두 `%s` 위반' % (cls, cls_prefix), '제1 규약 §6',
                            '부품 CSS 클래스는 `<수식>-<군>` 접두(`.%s`·`.%s__…`·`.%s--…`)만 쓴다.' % ((cls_prefix,) * 3)))
                        break

        # ---- NM13: 라우트 단일 출처 근사
        if not is_router:
            if ext == '.py':
                uses_urls: bool = any(e.module and (e.module.startswith('django.urls') or e.module.startswith('django.shortcuts'))
                                      for e in ctx.edges_of(f))
                if uses_urls:
                    for line, _ in scan_tokens(ms, re.compile(r'\b(?:re_)?path\s*\(')):
                        out.append(Finding('NM13', f, line, 'path() 정의가 router 파일 밖에 등장',
                            '제1 규약 §3.1', 'path()는 `<bc>_router.py`의 urlpatterns 에만 두고 root_router가 조립한다.'))
                    for m in re.finditer(r'\b(?:reverse|reverse_lazy|redirect|resolve_url)\s*\(', ms.tokens_view):
                        arg: str = first_arg_of(ms.tokens_view, m.end())
                        if is_string_literal(arg) and ctx.line_is_added(f, ms.line_of(m.start())):
                            out.append(Finding('NM13', f, ms.line_of(m.start()),
                                '내비 호출에 URL name·경로 문자열 리터럴 직접 전달', '제1 규약 §3.1',
                                'URL path·name 리터럴은 `<bc>_router.py` 안에서만 — `<Bc>Routes` 상수를 참조한다.'))
            elif ext == '.html':
                for line, _ in scan_tokens(ms, _URL_TAG_RE, view='no_comments'):
                    out.append(Finding('NM13', f, line, '템플릿의 `{% url %}` — 템플릿은 URL name 을 직접 쓰지 않는다',
                        '제1 규약 §3.1', 'VM이 navigator 로 만든 href 를 State에 담고 템플릿은 그 값을 쓴다.'))
                for line, _ in scan_tokens(ms, _ROUTE_ATTR_RE, view='no_comments'):
                    out.append(Finding('NM13', f, line, '템플릿의 라우트 경로 리터럴(`="/…"`)',
                        '제1 규약 §3.1', 'URL 경로 리터럴은 router 전속 — State 의 href 를 쓴다(정적 자산은 `{% static %}`).'))

        # ---- NM14: ui_extension은 `register = Library()` + 필터 함수만
        if parent == 'ui_extension' and ext == '.py':
            for line, what in _ui_extension_extras((ctx.web / f).read_text(encoding='utf-8', errors='replace')):
                out.append(Finding('NM14', f, line,
                    'ui_extension 파일에 %s — `register = Library()` + 등록된 필터 함수만 허용' % what, '제1 규약 §3.5',
                    '여기는 도메인 값 → CSS 클래스·아이콘·라벨 필터의 자리 — 상태·부품·도우미는 제자리로'
                    '(필터 안 매핑 표는 `_` 비공개 상수로).'))

        # ---- NM15: 애그리거트 루트 철자 일치
        if segs[0] == 'application' and 'domain_layer' in segs and ext == '.py':
            di: int = segs.index('domain_layer')
            if di == len(segs) - 3 and base != 'exception.py' and base != '%s.py' % segs[di + 1]:
                out.append(Finding('NM15', f, None,
                    '애그리거트 폴더 `%s/` 직속 파일명 `%s` — 루트는 폴더명과 동일(`%s.py`)' % (segs[di + 1], base, segs[di + 1]),
                    '제1 규약 §3.2·§7.2', '루트 파일명=폴더명=클래스명. 다른 개념이면 5종 폴더 안으로.'))

        # ---- NM16: repository 추상 클래스 금지
        if parent == 'repository' and ext == '.py':
            for line, _ in scan_tokens(ms, re.compile(
                    r'(?m)^class\s+\w+\s*\([^)]*\b(?:ABC|ABCMeta|Protocol)\b|\bmetaclass\s*=\s*ABCMeta\b|@(?:abc\.)?abstractmethod\b')):
                out.append(Finding('NM16', f, line,
                    'repository에 추상(ABC·Protocol·abstractmethod) — 간소화 DDD는 인터페이스 없음',
                    '제1 규약 §9-1', 'Repo는 구체 클래스 하나 — DataSource를 조합하는 단일 진실 원천.'))
                break

        # ---- NM17: view 직접 빌드 차단 (주 view 함수·`<화면>_<조각>_fragment` 함수 밖의 함수·클래스 금지)
        if parent == 'view' and base.endswith('_view.py') and bc is not None:
            prefix = base[:-len('_view.py')]
            for kind, name, line, _off in decls:
                if kind == 'def' and (name == '%s_view' % prefix
                                      or re.fullmatch(r'%s_\w+_fragment' % re.escape(prefix), name)):
                    continue
                out.append(Finding('NM17', f, line,
                    'view 파일에 추가 top-level %s `%s` — view `.py`는 `%s_view`·`%s_<조각>_fragment` 함수만' % (
                        '함수' if kind == 'def' else '클래스', name, prefix, prefix),
                    '제1 규약 §3.5', '요청에서 원시값을 꺼내 자기 VM에 넘기고 렌더할 뿐 — 조립은 section/widget 템플릿으로, '
                    '변환·판정은 VM·도메인으로 옮긴다.'))

        # ---- NM18: view 짝 — `<화면>_view.py` ↔ `<화면>_view.html`
        if parent == 'view' and bc is not None and has_seg(f, 'presentation_layer') and stem.endswith('_view') \
                and ext in ('.py', '.html'):
            other: str = f[:-len(ext)] + ('.html' if ext == '.py' else '.py')
            if other not in ctx.files_set:
                out.append(Finding('NM18', f, None, 'view 짝 미완 — 같은 폴더 `%s` 부재' % base_name_of(other),
                    '제1 규약 §7.1-3', 'view 는 `<화면>_view.py`(함수) + `<화면>_view.html`(페이지 템플릿) 한 쌍이다.'))

        # ---- NM19: 조각 CSS ↔ 템플릿 stem (BC presentation · root scaffold)
        if segs[0] == 'static' and len(segs) >= 3 and segs[1] in ('application', 'root') and ext == '.css':
            owner: str = ('/'.join(segs[1:-1]) + '/presentation_layer/') if segs[1] == 'application' else 'root/scaffold/'
            if not any(g.startswith(owner) and ext_of(g) == '.html' and stem_of(g) == stem for g in ctx.files):
                out.append(Finding('NM19', f, None,
                    '조각 CSS `%s` — 소유자(BC presentation_layer · root scaffold)에 같은 stem 의 템플릿이 없다' % base,
                    '제1 규약 §2·§7', '조각 CSS 는 그 조각 템플릿과 같은 stem 으로 둔다(sparse — 필요한 조각만).'))

        # ---- NM20: 파일명 snake_case (외부 고정 사본 제외)
        if not vendored and not _SNAKE_RE.fullmatch(base):
            out.append(Finding('NM20', f, None, '파일명 `%s` — snake_case 위반(소문자·숫자·언더스코어)' % base,
                '제1 규약 §7', 'snake_case로 개명한다 — 템플릿·CSS는 파일명 자체가 참조 계약이다.'))
    return out


def _registers(node: ast.AST) -> bool:
    """`register.<x>` · `register.<x>(…)` 꼴인가."""
    if isinstance(node, ast.Call):
        node = node.func
    while isinstance(node, ast.Attribute):
        node = node.value
    return isinstance(node, ast.Name) and node.id == 'register'


def _ui_extension_extras(src: str) -> List[Tuple[int, str]]:
    """ui_extension 모듈의 허용 밖 top-level — 허용: import · docstring · `register = Library()` ·
    `_` 비공개 상수 · `register.*` 데코레이터(또는 `register.filter(…)` 호출)로 등록된 함수 · TYPE_CHECKING 블록."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    registered: Set[str] = {a.id for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                            and _registers(n.value) for a in n.value.args if isinstance(a, ast.Name)}
    out: List[Tuple[int, str]] = []
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(n, ast.Expr) and (isinstance(n.value, ast.Constant) or (isinstance(n.value, ast.Call) and _registers(n.value))):
            continue
        if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == 'TYPE_CHECKING':
            continue
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if len(names) == len(targets) and all(x == 'register' or x.startswith('_') for x in names):
                continue
            out.append((n.lineno, 'top-level 대입 `%s`' % ', '.join(names or ['?'])))
            continue
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if n.name in registered or any(_registers(d) for d in n.decorator_list):
                continue
            out.append((n.lineno, '등록되지 않은 함수 `%s`' % n.name))
            continue
        if isinstance(n, ast.ClassDef):
            out.append((n.lineno, 'top-level class `%s`' % n.name))
            continue
        out.append((n.lineno, 'top-level 문장(%s)' % type(n).__name__))
    return out


def _is_union_file(ms, stem: str) -> bool:
    """합 타입 파일 — 파일명과 같은 이름의 top-level 별칭 `<Name> = A | B`(freezed union 자리)."""
    return any(casefold(m.group(1)) == casefold(stem) for m in _ALIAS_RE.finditer(ms.tokens_view))


def _visual_literals(ms, ext: str) -> List[Tuple[int, str]]:
    """색 리터럴 · typography 리터럴 — CSS·<style>·style 속성은 선언 값에서만(선택자 `#add` 제외), SVG 칠 속성은 값 전체."""
    text: str = ms.no_comments
    regions: List[Tuple[int, str, bool]] = []  # (오프셋, 본문, 선언 목록인가)
    if ext == '.css':
        regions.append((0, text, True))
    else:
        for m in _STYLE_ATTR_RE.finditer(text):
            g: int = 2 if m.group(2) is not None else 3
            regions.append((m.start(g), m.group(g), True))
        for m in _STYLE_BLOCK_RE.finditer(text):
            regions.append((m.start(1), m.group(1), True))
        for m in _PAINT_ATTR_RE.finditer(text):
            g = 3 if m.group(3) is not None else 4
            regions.append((m.start(g), m.group(g), False))
    hits: List[Tuple[int, str]] = []
    for off, body, is_decls in regions:
        values: List[Tuple[int, str, str]] = (
            [(off + d.start(2), d.group(1).lower(), d.group(2)) for d in _DECL_RE.finditer(body)]
            if is_decls else [(off, '', body)])
        for voff, prop, value in values:
            for m in _COLOR_RE.finditer(value):
                hits.append((ms.line_of(voff + m.start()), m.group(0).rstrip('(').strip()))
            if prop in _TYPO_PROPS and not _TYPO_OK_RE.match(value):
                hits.append((ms.line_of(voff), '%s: %s' % (prop, value.strip())))
    return sorted(set(hits))


def _owned(cls: str, prefix: str) -> bool:
    return cls == prefix or cls.startswith(prefix + '-') or cls.startswith(prefix + '_')


def _css_classes(ms, prefix: str) -> List[Tuple[int, str]]:
    """CSS 선택자 프렐류드의 클래스 이름(선언 블록·@규칙 머리 제외). htmx 가 붙이는 상태 클래스는
    부품 접두 클래스와 겹친 복합 선택자(`.spinner-loading.htmx-request`) 안에서만 빼고 돌려준다."""
    out: List[Tuple[int, str]] = []
    text: str = ms.no_comments
    for m in re.finditer(r'([^{};]+)\{', text):
        prelude: str = m.group(1)
        if prelude.strip().startswith('@'):
            continue
        base: int = m.start(1)
        for cm in re.finditer(r'[^\s,>+~]+', prelude):  # 복합 선택자 단위(결합자·쉼표로 자름)
            classes = [(c.start(), c.group(1)) for c in re.finditer(r'\.(-?[_a-zA-Z][\w-]*)', cm.group(0))]
            owned: bool = any(_owned(c, prefix) for _, c in classes)
            for off, c in classes:
                if owned and c in _HTMX_STATE_CLASSES:
                    continue
                out.append((ms.line_of(base + cm.start() + off), c))
    return out


def _folder_context_ok(f: str, parent: str) -> bool:
    """종류 폴더명이 우연히 같은 비검사 위치(common/service 등)를 거른다."""
    if parent in ('view_model', 'state'):
        return has_seg(f, 'application_layer') or f.startswith('root/scaffold/')
    if parent in ('use_case', 'shared_state'):
        return has_seg(f, 'application_layer')
    if parent == 'service':
        return has_seg(f, 'application_layer') or has_seg(f, 'infra_layer') or f.startswith('common/')
    if parent in ('data_source', 'repository'):
        return has_seg(f, 'infra_layer')
    if parent == 'view':
        return has_seg(f, 'presentation_layer') or f.startswith('root/scaffold/')
    if parent in ('section', 'widget', 'ui_extension'):
        return has_seg(f, 'presentation_layer')
    if parent in ('domain_service', 'specification'):
        return has_seg(f, 'domain_layer')
    if parent == 'handler':
        return f.startswith('root/')
    return True
