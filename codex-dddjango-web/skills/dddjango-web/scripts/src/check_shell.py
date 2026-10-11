# SH — 지속 셸 5종(2.4.0). 빚 스캔 밖: 켜는 diff 전수와 G0 지속 셸 점검이 본다.
# 태그는 no_comments 에서 읽고 별칭 hx-* / data-hx-* 를 같은 이름으로 판정한다.
# SH3 는 상속 사슬·렌더 의존 닫힘, SH4 는 공유 머리 필요 집합, SH5 는 검출 가능한 CSS 범위를 본다.

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Dict, List, Optional, Set, Tuple

from .common import (FOUNDATION_TOKENS, HTMX_CORE, HTMX_VERSION, HTMX_VERSION_RE, BackstopContext, Finding,
                     TemplateTag, _git_raw, ext_of, is_standard_path, loaded_file, mask_html, stem_of)
from .check_purity import (_FEATURE_JS_RE, _HTMX_LEGACY, _STATIC_ARG_RE, _changed, _sdk_global,
                           _sdk_reference_added, _sdk_reference_lines)
from .products import (REGISTRY, Products, parsed_tags, persistent_scope, persistent_shells, products_state,
                       render_closure, shell_candidate, shell_directives)
from .sdk_registry import sdk_state, strict_loads

_RULE: str = 'implementation-django §2 지속 셸 · §10 자산 자리'
_REV_RE = re.compile(r'\?v=\{\{\s*root_state\.shell_rev\s*\}\}$')
_BLOCK_RE = re.compile(r'\{%-?\s*block\s+(\w+)\s*-?%\}')
_TITLE_RE = re.compile(r'\{%-?\s*block\s+title\s*-?%\}(.*?)\{%-?\s*endblock(?:\s+title)?\s*-?%\}', re.S)
_REQUESTS: Set[str] = {'hx-get', 'hx-post', 'hx-put', 'hx-patch', 'hx-delete'}
_FORBIDDEN: Set[str] = {'hx-target', 'hx-select', 'hx-swap', 'hx-select-oob', 'hx-headers',
                        'hx-disinherit', 'hx-vals', 'hx-history'}


def _hx_names(tag: TemplateTag) -> Set[str]:
    return {name[5:] if name.startswith('data-hx-') else name for name in tag.attrs
            if name.startswith(('hx-', 'data-hx-'))}


def _hx(tag: TemplateTag, name: str) -> Optional[str]:
    for key in (name, 'data-' + name):
        if key in tag.attrs:
            return tag.attrs[key] or ''
    return None


def _alias_conflicts(tag: TemplateTag, names: Set[str]) -> List[str]:
    return ['같은 요소의 hx-* · data-hx-* 별칭 값이 다름 — ' + name for name in sorted(names)
            if name in tag.attrs and 'data-' + name in tag.attrs
            and (tag.attrs[name] or '') != (tag.attrs['data-' + name] or '')]


def _inside(tag: TemplateTag, ancestor: TemplateTag) -> bool:
    return ancestor.open_end <= tag.start < ancestor.close_start


def _execution(tag: TemplateTag) -> bool:
    return tag.name == 'script' and (tag.attrs.get('type') or '').strip().lower() in ('', 'text/javascript', 'module')


def _stylesheet(tag: TemplateTag) -> bool:
    return tag.name == 'link' and (tag.attrs.get('rel') or '').lower() == 'stylesheet'


def _path(tag: TemplateTag) -> Optional[str]:
    raw = tag.attrs.get('href' if tag.name == 'link' else 'src') or ''
    match = _STATIC_ARG_RE.fullmatch(_REV_RE.sub('', raw))
    return loaded_file(match.group(1) or match.group(2)) if match else None


def _load_line(path: str) -> str:
    arg = 'web/' + path[len('static/'):] if path.startswith('static/') else path
    address = "{% static '" + arg + "' %}?v={{ root_state.shell_rev }}"
    return ('<link rel="stylesheet" href="' + address + '">' if ext_of(path) == '.css'
            else '<script src="' + address + '" defer></script>')


def _script_order(ctx: BackstopContext, core: str, paths: List[Optional[str]]) -> List[str]:
    """실리는 실행 태그의 묶음 순서 — 선택 SDK 도 기능 JS 앞에 놓인다."""
    sdks = sorted(set(paths) & set(sdk_state(ctx).files().values()))
    features = sorted({path for path in paths if path is not None and _FEATURE_JS_RE.fullmatch(path)
                       and path not in {core, 'static/js/root_shell.js'}})
    return [core, 'static/js/root_shell.js'] + sdks + features


def _finding(cid: str, file: str, line: Optional[int], message: str, fix: Optional[str] = None) -> Finding:
    return Finding(cid, file, line, message, _RULE, fix or
                   '지속 셸 표준 꼴과 공유 머리 순서를 따른다. 페이지는 title·content 만 채운다(SH1~SH5).')


_UNREADABLE: str = '이 파이썬의 HTML 파서가 읽지 못하는 글자가 있다'


def _tags(ctx: BackstopContext, f: str, text: str) -> Optional[List[TemplateTag]]:
    """판독 불가(파서 예외)면 None 과 `[info]` 한 줄 — 러너는 죽지 않고 그 파일의 태그 검사만 건너뛴다."""
    tags = parsed_tags(text)
    if tags is None:
        ctx.notices.append('[info] SH 판독 불가 — web/%s · %s — 태그 검사 생략(지속 셸 점검·감수)' % (f, _UNREADABLE))
    return tags


def _base_text(ctx: BackstopContext, file: str) -> Optional[str]:
    if not ctx.gated:
        return None
    cache = getattr(ctx, '_shell_base_text', None)
    if cache is None:
        cache = {}
        setattr(ctx, '_shell_base_text', cache)
    if file not in cache:
        cache[file] = _git_raw(ctx.root, ['show', '%s:./web/%s' % (ctx.diff_base, file)])
    return cache[file]


def _activated(ctx: BackstopContext, shell: str) -> bool:
    before = _base_text(ctx, shell)
    return before is None or not shell_candidate(mask_html(before).no_comments)


def _moved(ctx: BackstopContext, shell: str, scope: Set[str]) -> Set[str]:
    """기준점 선언과 비교해 지속 셸 제품으로 옮겨진 파일만 전수 검사한다."""
    if not ctx.gated or not (ctx.is_touched(REGISTRY) or REGISTRY in ctx.base_files - ctx.files_set):
        return set()
    before = _base_text(ctx, REGISTRY)
    old = Products()
    if before is not None:
        try:
            entries = strict_loads(before.encode())['products']
            flat = next(pid for pid, spec in entries.items() if spec['design_system'] == 'flat')
            own = tuple(sorted(pid for pid, spec in entries.items() if spec['design_system'] == 'own'))
            bcs = {bc: pid for pid, spec in entries.items() if isinstance(spec['bcs'], list) for bc in spec['bcs']}
            star = next((pid for pid, spec in entries.items() if spec['bcs'] == '*'), None)
            old = Products(True, flat, own, bcs, star)
        except (ValueError, KeyError, StopIteration, TypeError):
            return scope  # 이전 선언을 읽을 수 없음 — 새 소속을 축소해 추정하지 않는다
    state = products_state(ctx)
    pid = state.product_of_shell(shell)
    return {f for f in scope if state.product_of(f, ctx.areas) == pid
            and old.product_of(f, ctx.areas) != pid}


def _sh1(ctx: BackstopContext, scopes: Dict[str, frozenset]) -> List[Finding]:
    state = products_state(ctx)
    pages: Set[str] = set()
    scope: Set[str] = set()
    for shell, members in scopes.items():
        scope.update(members)
        pages.update(f for f in ctx._persistent_seeds[shell] | ctx._persistent_chains[shell]
                     if f not in state.shells and ext_of(f) == '.html' and (
                         (f.startswith('application/') and re.search(r'/presentation_layer/(?:view|section|widget)/', f))
                         or f.startswith('root/scaffold/view/')
                         or (f in ctx._persistent_chains[shell] and not is_standard_path(f))))
    out: List[Finding] = []
    for f in ctx.files:
        if ext_of(f) != '.html' or not ctx.is_touched(f):
            continue
        ms = ctx.mask_of(f)
        for tag in _tags(ctx, f, ms.no_comments) or []:
            if not _changed(ctx, f, ms, tag.start, tag.open_end):
                continue
            reasons: List[str] = []
            names = _hx_names(tag)
            checked: Set[str] = set()
            if 'hx-boost' in names:
                checked.add('hx-boost')
                nav = f in scopes and tag.name == 'nav' and tag.attrs.get('id') == 'root-tab-bar' and _hx(tag, 'hx-boost') == 'true'
                page = f in pages and tag.name == 'a' and bool(tag.attrs.get('href')) and _hx(tag, 'hx-boost') in ('true', 'false')
                if not (nav or page):
                    reasons.append('hx-boost 자리·값 위반 — 지속 셸 nav 또는 그 제품 화면의 <a href> 에만 true·false')
                if tag.name == 'a' and names & _REQUESTS:
                    checked.update(names & _REQUESTS)
                    reasons.append('부스트 <a> 에 요청 속성 금지 — ' + ' · '.join(sorted(names & _REQUESTS)))
            if f not in state.shells and ('data-root-shell' in tag.attrs or names & {'hx-history-elt', 'hx-history'}):
                checked.update(names & {'hx-history-elt', 'hx-history'})
                reasons.append('표준 셸 밖 지속 셸 표지·hx-history 금지')
            if f in scope and f not in state.shells and 'hx-swap-oob' in names:
                checked.add('hx-swap-oob')
                reasons.append('지속 셸 제품의 셸 밖 hx-swap-oob 금지')
            reasons.extend(_alias_conflicts(tag, checked))
            for reason in reasons:
                out.append(_finding('SH1', f, ms.line_of(tag.start), reason))
    return out


def _sh2(ctx: BackstopContext, shell: str) -> List[Finding]:
    ms = ctx.mask_of(shell)
    text = ms.no_comments
    directives = shell_directives(ms.original, text)
    tags = parsed_tags(text)
    if tags is None:  # 꼴을 확인할 수 없는 지속 셸 — 표준 꼴에는 그런 글자가 없다
        return [_finding('SH2', shell, 1, '꼴 판독 불가 — ' + _UNREADABLE)]
    reasons: List[str] = []

    def require(ok: bool, number: int, detail: str) -> None:
        if not ok:
            reasons.append('꼴 %d — %s' % (number, detail))

    heads = [tag for tag in tags if tag.name == 'head']
    bodies = [tag for tag in tags if tag.name == 'body']
    head = heads[0] if len(heads) == 1 else None
    body = bodies[0] if len(bodies) == 1 else None
    mains = [tag for tag in tags if tag.name == 'main']
    navs = [tag for tag in tags if tag.name == 'nav']
    main = mains[0] if len(mains) == 1 else None
    nav = navs[0] if len(navs) == 1 else None
    metas = [tag for tag in tags if tag.name == 'meta' and tag.attrs.get('name') == 'htmx-config']
    config_ok = False
    if len(metas) == 1 and head is not None and _inside(metas[0], head):
        try:
            value = json.loads(metas[0].attrs.get('content') or '')
            config_ok = value == {'historyCacheSize': 0} and type(value.get('historyCacheSize')) is int
        except (ValueError, AttributeError):
            pass
    require(config_ok, 1, 'head 의 htmx-config 하나 · {"historyCacheSize":0}')
    titles = [tag for tag in tags if tag.name == 'title']
    title = titles[0] if len(titles) == 1 else None
    raw_title = text[title.open_end:title.close_start] if title else ''
    title_text = raw_title.strip()
    title_start = title.open_end + len(raw_title) - len(raw_title.lstrip()) if title else 0
    title_match = _TITLE_RE.fullmatch(directives[title_start:title_start + len(title_text)])
    require(bool(head and title and _inside(title, head) and title_match
                 and title_text[title_match.start(1):title_match.end(1)].strip()),
            2, 'title block 의 기본값은 비지 않는다')
    loads = [tag for tag in tags if _execution(tag) or _stylesheet(tag)]
    require(bool(head) and all(_inside(tag, head) for tag in loads), 3, '실행 script·stylesheet 는 head 안')
    scripts = [tag for tag in loads if _execution(tag)]
    paths = [_path(tag) for tag in scripts]
    order = _script_order(ctx, paths[0], paths) if paths and paths[0] in (HTMX_CORE,) + _HTMX_LEGACY else []
    require(len(paths) >= 2 and paths[0] in (HTMX_CORE,) + _HTMX_LEGACY and paths[1] == 'static/js/root_shell.js'
            and [path for path in paths if path in order] == order
            and all('defer' in tag.attrs and 'async' not in tag.attrs for tag in scripts),
            4, 'htmx core → root_shell.js → SDK → 기능 JS · 모두 defer')
    require(Counter(m.group(1) for m in _BLOCK_RE.finditer(directives)) == Counter({'title': 1, 'content': 1}),
            5, 'block 은 title·content 둘뿐')
    marker = re.compile(re.escape(stem_of(shell)) + r'@\{\{\s*root_state\.shell_rev\s*\}\}')
    require(bool(body and marker.fullmatch(body.attrs.get('data-root-shell') or '') and all(
        not re.search(r'\{[{%]', value or '') for name, value in body.attrs.items() if name != 'data-root-shell')),
        6, 'body 의 정확한 data-root-shell · 그 밖 속성은 정적 값')
    main_ok = bool(main and body and main.parent is body and main.attrs.get('id') == 'root-content'
                   and _hx(main, 'hx-history-elt') == ''
                   and set(main.attrs) <= {'id', 'hx-history-elt', 'data-hx-history-elt', 'class', 'data-testid'}
                   and all(not re.search(r'\{[{%]', main.attrs.get(key) or '') for key in ('class', 'data-testid')))
    templates = [tag for tag in tags if tag.name == 'template' and main and tag.parent is main]
    template = templates[0] if len(templates) == 1 else None
    oobs = [tag for tag in tags if template and tag.parent is template and tag.name == 'div'
            and tag.attrs.get('id') == 'root-tab-items' and _hx(tag, 'hx-swap-oob') == 'innerHTML']
    oob = oobs[0] if len(oobs) == 1 else None
    if main and template:
        before = text[main.open_end:template.start]
        # 셸 자료 줄들 → content block → 마지막 template. 그 밖 요소·텍스트는 허용하지 않는다.
        before = re.sub(r'^\s*\{\{[^{}]*\|\s*json_script\s*:\s*["\']root-[^"\']+["\']\s*\}\}', '', before)
        while re.match(r'^\s*\{\{[^{}]*\|\s*json_script\s*:', before):
            stripped = re.sub(r'^\s*\{\{[^{}]*\|\s*json_script\s*:\s*["\']root-[^"\']+["\']\s*\}\}', '', before)
            if stripped == before:
                break
            before = stripped
        content = re.fullmatch(r'\s*\{%\s*block\s+content\s*%\}\s*\{%\s*endblock(?:\s+content)?\s*%\}\s*', before)
        main_ok = main_ok and bool(content and oob and not text[template.end:main.close_start].strip())
        if oob:
            inside = text[template.open_end:template.close_start]
            inside = inside[:oob.start - template.open_end] + inside[oob.end - template.open_end:]
            main_ok = main_ok and not inside.strip()
    else:
        main_ok = False
    require(bool(main_ok), 7, 'main#root-content · history-elt · 자료 → content → 마지막 template/OOB'
            + (' — hx-history-elt 는 값 없이 쓴다' if main and _hx(main, 'hx-history-elt') else ''))
    require(bool(nav and body and main and nav.parent is body and main.end <= nav.start
                 and nav.attrs.get('id') == 'root-tab-bar' and _hx(nav, 'hx-boost') == 'true'
                 and _hx(nav, 'hx-sync') == 'this:replace' and _hx_names(nav) == {'hx-boost', 'hx-sync'}),
            8, 'main 다음 형제 nav#root-tab-bar · boost=true · sync=this:replace')
    items = [tag for tag in tags if nav and tag.parent is nav and tag.name == 'div' and tag.attrs.get('id') == 'root-tab-items']
    item = items[0] if len(items) == 1 else None
    # 공백 줄은 하나로 접고 태그 사이 공백은 지운다 — template 안 벌이 한 단 더 깊어도(표준 글) 같다.
    normalize = lambda value: re.sub(r'> <', '><', re.sub(r'\s+', ' ', value).strip())
    require(bool(item and oob and normalize(text[item.open_end:item.close_start]) == normalize(text[oob.open_end:oob.close_start])),
            9, '탭 목록 두 벌의 안쪽 글자가 같다(들여쓰기·줄바꿈 차이는 무시)')
    links = [tag for tag in tags if tag.name == 'a' and ((item and _inside(tag, item)) or (oob and _inside(tag, oob)))]
    require(bool(links) and all(re.fullmatch(r'root-tab-\{\{\s*tab\.key\s*\}\}', tag.attrs.get('id') or '')
            and re.fullmatch(r'\{\{\s*tab\.href\s*\}\}', tag.attrs.get('href') or '') and not _hx_names(tag)
            and tag.attrs.get('aria-current') == 'page'
            and '{% if tab.is_current %}' in text[tag.start:tag.open_end] for tag in links),
            10, '탭 a 의 id·href · 고른 탭 aria-current=page · hx-* 없음')
    require(all(not (_hx_names(tag) & _FORBIDDEN) for tag in tags), 11, '셸 어디에도 target·select·swap·headers·history 등 없음')
    body_ok = bool(body and main and nav and main.parent is body and nav.parent is body)
    if body_ok:
        children = [tag for tag in tags if tag.parent is body]
        residue = text[body.open_end:body.close_start]
        for tag in sorted(children, key=lambda tag: tag.start, reverse=True):
            residue = residue[:tag.start - body.open_end] + residue[tag.end - body.open_end:]
        body_ok = children == [main, nav] and not residue.strip()
    require(bool(body_ok), 12, 'body 자식은 main·nav 둘뿐 · 자료·include·텍스트는 main 안')
    require(all(_REV_RE.search(tag.attrs.get('href' if tag.name == 'link' else 'src') or '')
                and _path(tag) is not None for tag in loads), 13, '모든 머리 자산 주소는 정확한 static + ?v={{ root_state.shell_rev }}')
    for tag in tags:
        reasons.extend(_alias_conflicts(tag, _hx_names(tag)))
    return [_finding('SH2', shell, 1, reason) for reason in reasons]


def _sh3(ctx: BackstopContext, shell: str, scope: Set[str]) -> List[Finding]:
    state = products_state(ctx)
    graph = ctx._persistent_edges
    whole: Set[str] = set(scope) if _activated(ctx, shell) else render_closure(ctx, _moved(ctx, shell, scope))
    reverse: Dict[str, Set[str]] = {}
    for f, edges in graph.items():
        for kind, target, _line in edges:
            if kind == 'extends':
                reverse.setdefault(target, set()).add(f)
    for f in sorted(scope):
        for kind, target, line in graph.get(f, []):
            if not ctx.is_touched(f) or not ctx.line_is_added(f, line):
                continue
            if kind == 'include':
                if target in scope:
                    whole.update(render_closure(ctx, {target}, parents=True))
            else:
                below = {f}
                pending = [f]
                while pending:
                    for child in (reverse.get(pending.pop(), set()) & set(ctx._persistent_chains[shell])) - below:
                        below.add(child)
                        pending.append(child)
                whole.update(render_closure(ctx, below))
                if target in scope:
                    whole.update(render_closure(ctx, {target}, parents=True))
    members = (scope | whole) - set(state.shells)
    out: List[Finding] = []
    for f in sorted(members):
        if f not in ctx.files_set or ext_of(f) != '.html':
            continue
        ms = ctx.mask_of(f)
        text = ms.no_comments
        directives = shell_directives(ms.original, text)
        active = lambda start, end: f in whole or (ctx.is_touched(f) and _changed(ctx, f, ms, start, end))
        for match in _BLOCK_RE.finditer(directives):
            if match.group(1) in ('head', 'scripts') and active(match.start(), match.end()):
                out.append(_finding('SH3', f, ms.line_of(match.start()), '지속 셸 제품의 {% block ' + match.group(1) + ' %} 정의 금지'))
        # 손대지 않은 전수 밖 파일은 발견이 설 수 없어 파싱하지 않는다(판독 불가 알림도 볼 파일에만).
        tags = _tags(ctx, f, text) if f in whole or ctx.is_touched(f) else None
        for tag in tags or []:
            if (_execution(tag) or _stylesheet(tag)) and active(tag.start, tag.open_end):
                out.append(_finding('SH3', f, ms.line_of(tag.start), '지속 셸 제품의 본문 실행 script·stylesheet 금지',
                                    '해당 자산을 지속 셸 <head> 의 정렬된 자리에 ?v={{ root_state.shell_rev }} 와 함께 둔다.'))
        for match in _TITLE_RE.finditer(directives):
            if not text[match.start(1):match.end(1)].strip() and active(match.start(), match.end()):
                out.append(_finding('SH3', f, ms.line_of(match.start()), '빈 title block — 공백·주석뿐인 제목 금지'))
        for line, reason in ctx._persistent_unreadable.get(f, []):
            if f in whole or (ctx.is_touched(f) and ctx.line_is_added(f, line)):
                ctx.notices.append('[info] SH3 판독 불가 — web/%s:%d · %s(지속 셸 점검·감수)' % (f, line, reason))
    return out


def _required(ctx: BackstopContext, shell: str, scope: Set[str]) -> Tuple[List[str], Set[str]]:
    state = products_state(ctx)
    pid = state.product_of_shell(shell)
    ds = state.ds_root(pid)
    foundation = [ds + '/foundation/app_%s.css' % token for token in FOUNDATION_TOKENS]  # 관례 순(color … asset)
    theme = ds + '/theme/app_theme.css'
    frame = 'static/root/' + stem_of(shell) + '.css'
    css: Set[str] = set()
    for f in ctx.all_files:
        if ext_of(f) != '.css' or f == frame:
            continue
        if f.startswith((ds + '/component/', ds + '/util/')) and (not state.declared or state.product_of(f, ctx.areas) == pid):
            css.add(f)
        if f.startswith('static/application/') and (not state.declared or state.product_of(f, ctx.areas) == pid):
            css.add(f)
        if f.startswith('static/root/') and f[:-4].replace('static/root/', 'root/scaffold/view/') + '.html' in ctx._persistent_chains[shell]:
            css.add(f)
    # 옛 자리 core: 기준점 트리가 있으면 거기 있던 것만(새로 놓은 옛 이름은 core 가 아니다 — PU1) · 없으면(비git · --all 만)
    # 파일로 있는 것(SH2 꼴 ④ 와 같은 판정).
    cores = [HTMX_CORE] if HTMX_CORE in ctx.files_set else [
        f for f in _HTMX_LEGACY if f in ctx.files_set and (not ctx.can_detect_new_units or f in ctx.base_files)]
    core = cores[0] if cores else HTMX_CORE
    features = sorted(f for f in ctx.all_files if _FEATURE_JS_RE.fullmatch(f) and f not in {core, 'static/js/root_shell.js'})
    sdks: List[str] = []
    added_reference = False
    for path in sorted(sdk_state(ctx).files().values()):
        name = _sdk_global(ctx, path)
        for js in features:
            lines = _sdk_reference_lines(ctx, js, name)
            if lines is None or lines:
                if path not in sdks:
                    sdks.append(path)
                if _sdk_reference_added(ctx, js, lines):
                    added_reference = True
    setattr(ctx, '_shell_sdk_reference_added_' + shell, added_reference)
    return foundation + [theme, frame] + sorted(css) + [core, 'static/js/root_shell.js'] + sorted(sdks) + features, set(css)


def _sh4(ctx: BackstopContext, shell: str, scope: Set[str]) -> List[Finding]:
    required, _css = _required(ctx, shell, scope)
    changed_assets = any(ctx.is_added(f) for f in required) or bool(set(required) & (ctx.base_files - ctx.files_set))
    # 삭제 자산은 기준점 집합에서도 본다 — 현재 필요 집합에는 이미 지운 CSS 가 없다.
    deleted_assets = {f for _line, f in ctx.loads_of(shell)} & (ctx.base_files - ctx.files_set)
    if not (ctx.is_touched(shell) or changed_assets or deleted_assets or ctx.is_touched(REGISTRY)
            or REGISTRY in ctx.base_files - ctx.files_set
            or _activated(ctx, shell) or getattr(ctx, '_shell_sdk_reference_added_' + shell)
            or any(ctx.is_touched(f) for f in required if f in (HTMX_CORE,) + _HTMX_LEGACY)):
        return []
    ms = ctx.mask_of(shell)
    tags = parsed_tags(ms.no_comments)
    if tags is None:  # 머리 자산을 확인할 수 없다 — 판 글자를 못 읽을 때처럼 붉음
        return [_finding('SH4', shell, 1, '공유 머리 판독 불가 — ' + _UNREADABLE)]
    heads = [tag for tag in tags if tag.name == 'head']
    head = heads[0] if len(heads) == 1 else None
    loads = [tag for tag in tags if head and _inside(tag, head) and (_execution(tag) or _stylesheet(tag))]
    paths = [_path(tag) for tag in loads]
    counts = Counter(path for path in paths if path is not None)
    out: List[Finding] = []
    missing = [f for f in required if counts[f] == 0]
    if missing:
        out.append(_finding('SH4', shell, 1, '공유 머리 필요 자산 빠짐 — ' + ' · '.join(missing),
                            '넣을 줄: ' + ' '.join(_load_line(f) for f in missing)))
    duplicates = [f for f, count in sorted(counts.items()) if count > 1]
    if duplicates:
        out.append(_finding('SH4', shell, 1, '공유 머리 자산 중복 — ' + ' · '.join(duplicates),
                            '지울 줄(한 줄만 남김): ' + ' '.join(_load_line(f) for f in duplicates)))
    absent = sorted({f for f in set(required) | set(counts) if f not in ctx.files_set})
    if absent:
        out.append(_finding('SH4', shell, 1, '공유 머리 자산 파일 없음 — ' + ' · '.join(absent),
                            '지울 줄: ' + ' '.join(_load_line(f) for f in absent if f in counts) + ' · 필요 파일은 먼저 구현한다.'))
    projected = [path for path in paths if path in required]
    theme = products_state(ctx).ds_root(products_state(ctx).product_of_shell(shell)) + '/theme/app_theme.css'
    theme_index = paths.index(theme) if theme in paths else -1
    legacy_before_theme = any(path is not None and path not in required and i <= theme_index
                              for i, path in enumerate(paths))
    script_paths = [_path(tag) for tag in loads if _execution(tag)]
    core = next(f for f in required if f in (HTMX_CORE,) + _HTMX_LEGACY)
    script_order = _script_order(ctx, core, script_paths)
    if (projected != [path for path in required if counts[path]] or legacy_before_theme
            or script_paths[:2] != [core, 'static/js/root_shell.js']
            or [path for path in script_paths if path in script_order] != script_order):
        out.append(_finding('SH4', shell, 1, '공유 머리 묶음·경로 순서 위반',
                            '지울 줄·넣을 줄(이 순서로 재배치): ' + ' '.join(_load_line(f) for f in required)))
    state = products_state(ctx)
    pid = state.product_of_shell(shell)
    mixed = sorted(f for f in counts if state.standard_css_owner(f) is not None and state.standard_css_owner(f) != pid)
    if mixed:
        out.append(_finding('SH4', shell, 1, '다른 제품의 표준 CSS 혼입 — ' + ' · '.join(mixed),
                            '지울 줄: ' + ' '.join(_load_line(f) for f in mixed)))
    if core in ctx.files_set:
        match = HTMX_VERSION_RE.search((ctx.web / core).read_text(encoding='utf-8', errors='replace'))
        if match is None or match.group(1) != HTMX_VERSION:
            message = ('core 판을 읽지 못함 — 지속 셸은 2.0.10 확인이 필요' if match is None else
                       '지속 셸 core 판 %s — 필요한 판 %s' % (match.group(1), HTMX_VERSION))
            out.append(_finding('SH4', shell, 1, message, 'G0 의 지속 셸 전제를 확인한다. core 판 맞추기는 별도 요청이다.'))
    return out


def _split_selector(text: str) -> List[Tuple[int, str]]:
    """괄호·속성 안 쉼표를 빼고 선택자 목록의 모든 갈래를 본다."""
    parts: List[Tuple[int, str]] = []
    depth = 0
    quote = ''
    start = 0
    escaped = False
    for i, char in enumerate(text):
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif quote:
            if char == quote:
                quote = ''
        elif char in ('"', "'"):
            quote = char
        elif char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif char == ',' and depth == 0:
            parts.append((start, text[start:i]))
            start = i + 1
    parts.append((start, text[start:]))
    return parts


def _css_selectors(text: str, start: int = 0, end: Optional[int] = None) -> List[Tuple[int, int, str]]:
    """CSS 규칙의 시작. 그룹 at-rule 은 내려가고 정의 at-rule 은 건너뛴다."""
    end = len(text) if end is None else end
    out: List[Tuple[int, int, str]] = []
    pos = start
    while pos < end:
        while pos < end and text[pos].isspace():
            pos += 1
        i = pos
        quote = ''
        depth = 0
        while i < end:
            char = text[i]
            if char == '\\':
                i += 2
                continue
            if quote:
                if char == quote:
                    quote = ''
            elif char in ('"', "'"):
                quote = char
            elif char in '([':
                depth += 1
            elif char in ')]':
                depth -= 1
            elif depth == 0 and char in '{;':
                break
            i += 1
        if i >= end:
            break
        if text[i] == ';':
            pos = i + 1
            continue
        j = i + 1
        braces = 1
        quote = ''
        while j < end and braces:
            char = text[j]
            if char == '\\':
                j += 2
                continue
            if quote:
                if char == quote:
                    quote = ''
            elif char in ('"', "'"):
                quote = char
            elif char == '{':
                braces += 1
            elif char == '}':
                braces -= 1
            j += 1
        selector = text[pos:i].strip()
        if re.match(r'@(?:media|supports|container|layer)\b', selector, re.I):
            out.extend(_css_selectors(text, i + 1, j - 1))
        elif not selector.startswith('@'):
            out.extend((pos + offset + len(part) - len(part.lstrip()), pos + offset + len(part.rstrip()), part.strip())
                       for offset, part in _split_selector(text[pos:i]) if part.strip())
        pos = j
    return out


def _first_compound(selector: str) -> Tuple[str, bool, Optional[str]]:
    depth = 0
    quote = ''
    i = 0
    while i < len(selector):
        char = selector[i]
        if char == '\\':
            i += 2
            continue
        if quote:
            if char == quote:
                quote = ''
        elif char in ('"', "'"):
            quote = char
        elif char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif depth == 0 and (char.isspace() or char in '>+~'):
            break
        i += 1
    first = selector[:i]
    # 함수 안 class 만으로 범위를 확정하지 않는다. 함수 밖 class·id·속성은 유효한 범위다.
    flat = first
    while re.search(r'\([^()]*\)', flat):
        flat = re.sub(r'\([^()]*\)', '', flat)
    classes = re.findall(r'\.([a-zA-Z_][\w-]*)', re.sub(r'\[[^\]]*\]', '', flat))
    scoped = bool(classes or re.search(r'#[\w-]+|\[', flat))
    uncertain = not scoped and bool(re.search(r':(?:is|where|not|has)\(', first))
    block = next((re.split(r'__|--', name)[0] for name in classes if not name.startswith('htmx-')), None)
    return first, uncertain, block if scoped else None


def _sh5(ctx: BackstopContext, shell: str, scope: Set[str]) -> List[Finding]:
    ms = ctx.mask_of(shell)
    tags = _tags(ctx, shell, ms.no_comments)
    frame = 'static/root/' + stem_of(shell) + '.css'
    files: Set[str] = set()
    full: Set[str] = set()
    for tag in tags or []:
        if not _stylesheet(tag):
            continue
        path = _path(tag)
        if path is None or path == frame or '/foundation/' in path or '/theme/' in path or path not in ctx.files_set:
            continue
        files.add(path)
        if (_activated(ctx, shell) or path in _moved(ctx, shell, scope) or ctx.is_added(path)
                or _changed(ctx, shell, ms, tag.start, tag.open_end)):
            full.add(path)
    selectors: Dict[str, list] = {file: _css_selectors(ctx.mask_of(file).no_comments) for file in sorted(files)}
    owners: Dict[str, Set[str]] = {}
    for file, records in selectors.items():
        for _start, _end, selector in records:
            _first, _uncertain, block = _first_compound(selector)
            if block:
                owners.setdefault(block, set()).add(file)
    out: List[Finding] = []
    for file, records in selectors.items():
        css = ctx.mask_of(file)
        for start, end, selector in records:
            if file not in full and not (ctx.is_touched(file) and _changed(ctx, file, css, start, end)):
                continue
            first, uncertain, block = _first_compound(selector)
            if uncertain or '\\' in first or '&' in first:
                ctx.notices.append('[info] SH5 판독 불가 — web/%s:%d · %s(알려진 미탐과 함께 감수)' % (file, css.line_of(start), selector))
            elif not re.search(r'[.#\[]', first):
                out.append(_finding('SH5', file, css.line_of(start), '공유 머리 CSS 맨 선택자 — ' + selector,
                                    '자기 BEM block 의 class 아래로 범위를 한정한다(util 포함).'))
            elif block and len(owners[block]) > 1:
                out.append(_finding('SH5', file, css.line_of(start), '공유 머리 CSS BEM block 중복 — %s · %s' % (block, ' · '.join(sorted(owners[block]))),
                                    '파일마다 자기 block 을 쓴다. 정당한 겹침이면 검사기 이의로 판단 근거를 남긴다.'))
    return out


def run_shell(ctx: BackstopContext) -> List[Finding]:
    notice_start = len(ctx.notices)
    scopes = persistent_scope(ctx)
    out = _sh1(ctx, scopes)
    state = products_state(ctx)
    for shell in sorted(state.shells & ctx.files_set):
        if not ctx.is_touched(shell):
            continue
        before = _base_text(ctx, shell)
        if shell in scopes:
            # 비git · --all · 기준점 없음일 때만 — 게이트에서 기준점에 없던 새 셸은 걷을 표지가 없었다.
            if before is None and (not ctx.gated or shell in ctx.base_files):
                ctx.notices.append('[info] 기준점 본문 없음 — 표지 걷음 판정 생략 · web/' + shell)
            out.extend(_sh2(ctx, shell))
        elif before is not None and shell_candidate(mask_html(before).no_comments):
            ctx.notices.append('[info] 지속 셸 표지가 기준점 뒤 없어졌다 · web/' + shell)
    for shell, members in scopes.items():
        scope = set(members)
        out.extend(_sh3(ctx, shell, scope))
        out.extend(_sh4(ctx, shell, scope))
        out.extend(_sh5(ctx, shell, scope))
    # 여러 제품이 같은 조각을 include 하더라도 발견과 info 는 한 번만 출력한다.
    unique: Dict[Tuple[str, str, Optional[int], str], Finding] = {}
    for finding in out:
        unique.setdefault((finding.check_id, finding.path, finding.line, finding.message), finding)
    ctx.notices[notice_start:] = list(dict.fromkeys(ctx.notices[notice_start:]))
    return list(unique.values())
