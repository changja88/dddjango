# 채널 ④ 임베드 증거 — IM5 «임베드 받는 페이지 머리의 자식 조각 CSS» 예외(discipline-houserules §5 «교차 BC CSS» · 2.8.2).
#
# 받는 페이지 D = BC 의 `presentation_layer/[<개념>/]view/<화면>_view.html` 가운데 문서 셸(선언이 없으면 root_view.html ·
# 선언이 있으면 선언된 셸 집합)을 글자 `{% extends %}` 로 상속한 것. 예외 자리 = 셸이 `<head>` 안에 둔 block 을 D 가 채운
# 구간의 `{% static %}` link 뿐이다(지속 셸은 `<head>` 안에 block 이 없어 자리가 없다 — 지속 셸 페이지의 block head 는 SH3 몫).
# 증거 네 고리(하나라도 글자로 못 읽으면 증거 없음 — IM5 그대로):
#   ① 자리 — D 와 그 글자 include 닫힘이 실제로 그리는 요소의 `hx-get` · `data-hx-get` 속성 값 `{{ <점 이름> }}`(필터 없음).
#      extends 한 템플릿은 상속 사슬이 정의한 block 안만 그린다 · verbatim 안은 글자다 · include 닫힘도 그려지는 include 만
#      따른다. 칸 이름 F = 점 이름의 끝 마디.
#   ② href — D 의 짝 VM(`view_model/<화면>_vm.py`)이 키워드 인자 `F=` 또는 이름 F 의 대입 값으로 바로
#      `<이름>.<m>(…)` 를 둔다(<이름> 은 그 파일이 `web.application.[<area>.]<bc>.<bc>_navigator` 에서 들여온 이름 —
#      별칭이면 원래 클래스 이름으로 다음 고리를 딴다).
#   ③ 라우트 — 그 navigator 의 그 클래스 메서드 m(동기 · async) 안 `reverse(…)` · `reverse_lazy(…)` 의 첫 인자(또는
#      `viewname=`)가 모두 `<R>.<K>`(R 은 그 BC router 에서 들여온 클래스)이고, router 의 그 클래스 상수 `K = "<app_name>:<name>"`
#      가 `path(…, <함수>, name="<name>")`(re_path 포함)에 묶이며, 그 함수의 원래 이름(router 의 import 별칭을 푼 이름)이
#      `<화면C>_embed_fragment` 이고 같은 BC 의 `presentation_layer/[<개념>/]view/<화면C>_view.py` 에 그 이름의 함수가 있다.
#   ④ 렌더 — 그 함수 안 `render(<요청>, T, …)` 의 T(글자 · 모듈 범위 글자 상수)와 그 include 닫힘 가운데 그 BC 의
#      view · section · widget 템플릿 → 같은 stem 의 `static/application/[<area>/]<bc>/<stem>.css` 가 허용 대상이다.
#   자식의 자식: 같은 고리를 자식 쪽(④ 의 렌더 닫힘 · 자식 짝 VM `<화면C>_vm.py`)에서 다시 따르고 그 CSS 도 D 가 싣는다.
# 읽는 파일은 web 아래 실제 파일만이다(링크 · 실제 경로가 web 밖이면 증거 없음 — 2.5.2 밖 읽기 막음과 같은 뜻). git 은
# 부르지 않는다. 보조 파싱의 경고(잘못된 이스케이프 등)는 검사기 출력에 더하지 않는다(승인 유입의 부모 측정은 stderr 를
# 실패로 읽는다). 결과 · AST 는 컨텍스트에 getattr · setattr 로 붙여 둔다.
# 받아들인 한계(해는 «안 쓰는 다른 BC CSS 한 줄 실음»에 그친다): 정적 거짓 가지(`{% if False %}`) 안 자리 · VM 의 부르지 않는
# 함수나 다른 State 생성 안 같은 이름 키워드 · navigator 의 같은 이름 클래스 두 번 정의(앞 것을 읽는다) · 버린 reverse 뒤 다른
# 값을 돌려주는 메서드.
from __future__ import annotations

import ast
import os
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from .common import (VERBATIM_RE, BackstopContext, MaskedSource, base_name_of, bc_dir_of, bc_of, has_seg,
                     is_bc_root_path, parent_dir_of, parse_template_edges)
from .products import parsed_tags, products_state

_VALUE = re.compile(r'\{\{\s*([A-Za-z_][\w.]*)\s*\}\}')
_BLOCK = re.compile(r'\{%-?\s*(block|endblock)\b\s*(\w*)[^%]*?-?%\}')
_EXTENDS = re.compile(r'''\{%-?\s*extends\s+(["'])([^"'\n]+)\1''')
_HEAD = re.compile(r'<head\b[^>]*>(.*?)</head\s*>', re.I | re.S)
_FRAGMENT: str = '_embed_fragment'
_HX_ATTRS: Tuple[str, ...] = ('hx-get', 'data-hx-get')
_REVERSE: Tuple[str, ...] = ('reverse', 'reverse_lazy')
_Fn = Union[ast.FunctionDef, ast.AsyncFunctionDef]


@dataclass
class _Trace:
    """첫 빈 고리 진단용 기록(교정 줄에만 쓴다 — 위반 문장은 참조만으로 정한다)."""
    fields: Set[str] = field(default_factory=set)
    vms: List[str] = field(default_factory=list)
    calls: List[Tuple[str, str, str]] = field(default_factory=list)   # (navigator 파일, 클래스, 메서드)
    unbound: List[str] = field(default_factory=list)                   # 임베드 라우트에 묶이지 않은 `클래스.메서드`
    bound: List[str] = field(default_factory=list)                     # 묶인 임베드 함수 `view 모듈:함수`
    fragments: Dict[str, List[str]] = field(default_factory=dict)      # BC 폴더 → 허용 CSS


def _blank(text: str, spans: List[Tuple[int, int]]) -> str:
    """구간의 글자를 공백으로 가린다(개행 · 좌표 보존)."""
    chars: List[str] = list(text)
    for a, b in spans:
        for i in range(a, b):
            if chars[i] != '\n':
                chars[i] = ' '
    return ''.join(chars)


def _inside(ctx: BackstopContext, f: str) -> bool:
    """web 아래 실제 파일인가(링크 · web 밖으로 풀리는 경로는 아니다)."""
    if f not in ctx.files_set:
        return False
    path: Path = ctx.web / f
    try:
        if path.is_symlink():
            return False
        web: str = os.path.realpath(ctx.web)
        return os.path.commonpath([web, os.path.realpath(path)]) == web
    except (OSError, ValueError):
        return False


def _text(ctx: BackstopContext, f: str) -> Optional[str]:
    """주석 · verbatim 을 가린 템플릿 본문(좌표 보존) — web 아래 실제 파일이 아니면 None."""
    cache: Optional[Dict[str, Optional[str]]] = getattr(ctx, '_embed_text_cache', None)
    if cache is None:
        cache = {}
        setattr(ctx, '_embed_text_cache', cache)
    if f not in cache:
        text: Optional[str] = None
        if _inside(ctx, f):
            masked: str = ctx.mask_of(f).no_comments
            text = _blank(masked, [(m.start(), m.end()) for m in VERBATIM_RE.finditer(masked)])
        cache[f] = text
    return cache[f]


def _blocks(text: str, top_only: bool) -> List[Tuple[str, int, int]]:
    """(이름, 본문 시작, 본문 끝) — top_only 면 바깥 block 만."""
    out: List[Tuple[str, int, int]] = []
    stack: List[Tuple[str, int]] = []
    for m in _BLOCK.finditer(text):
        if m[1] == 'block':
            stack.append((m[2], m.end()))
        elif stack:
            name, start = stack.pop()
            if not top_only or not stack:
                out.append((name, start, m.start()))
    return out


def _extends(text: str) -> Optional[str]:
    m: Optional[re.Match[str]] = _EXTENDS.search(text)
    return m[2].strip().lstrip('/') if m else None


def _chain_blocks(ctx: BackstopContext, target: str) -> Optional[Set[str]]:
    """상속 사슬(target 과 그 조상)이 정의한 block 이름 — 사슬을 끝까지 못 읽으면(파일 아님 · 순환) None."""
    names: Set[str] = set()
    seen: Set[str] = set()
    while target not in seen:
        seen.add(target)
        text: Optional[str] = _text(ctx, target)
        if text is None:
            return None
        names.update(n for n, _a, _b in _blocks(text, False))
        parent: Optional[str] = _extends(text)
        if parent is None:
            return names
        target = parent
    return None


def _rendered_text(ctx: BackstopContext, f: str) -> Optional[str]:
    """실제로 그려지는 글자만 남긴 본문 — extends 한 템플릿은 사슬이 정의한 block 안만(block 밖 · 사슬에 없는 block 은
    Django 가 버린다)."""
    text: Optional[str] = _text(ctx, f)
    if text is None:
        return None
    parent: Optional[str] = _extends(text)
    if parent is None:
        return text
    names: Optional[Set[str]] = _chain_blocks(ctx, parent)
    if names is None:
        return None
    keep: List[Tuple[int, int]] = [(a, b) for n, a, b in _blocks(text, True) if n in names]
    drop: List[Tuple[int, int]] = []
    at: int = 0
    for a, b in sorted(keep):
        drop.append((at, a))
        at = b
    drop.append((at, len(text)))
    return _blank(text, drop)


def page_shell(ctx: BackstopContext, page: str) -> Optional[str]:
    """글자 extends 로 상속한 문서 셸(선언된 셸 집합의 파일) — 아니면 None."""
    text: Optional[str] = _text(ctx, page)
    target: Optional[str] = _extends(text) if text is not None else None
    return target if target in products_state(ctx).shells and target in ctx.files_set else None


def head_lines(ctx: BackstopContext, page: str) -> Set[int]:
    """문서 셸을 상속한 페이지에서, 셸이 `<head>` 안에 둔 block 을 채운 구간의 줄."""
    shell: Optional[str] = page_shell(ctx, page)
    shell_text: Optional[str] = _text(ctx, shell) if shell else None
    head: Optional[re.Match[str]] = _HEAD.search(shell_text) if shell_text else None
    if head is None:
        return set()
    names: Set[str] = {n for n, _a, _b in _blocks(head[1], False)}
    text: str = _text(ctx, page) or ''
    ms: MaskedSource = ctx.mask_of(page)
    out: Set[int] = set()
    for n, a, b in _blocks(text, True):
        if n in names:
            out.update(range(ms.line_of(a), ms.line_of(b) + 1))
    return out


def _rendered_includes(ctx: BackstopContext, t: str) -> List[str]:
    """그 템플릿이 실제로 그리는 글자 include 대상(셸에 없는 block · block 밖 · verbatim 안 include 는 따르지 않는다)."""
    text: Optional[str] = _rendered_text(ctx, t)
    if text is None:
        return []
    ms: MaskedSource = ctx.mask_of(t)
    view: MaskedSource = MaskedSource(ms.original, text, ms.tokens_view, ms.line_starts)
    return [e.target for e in parse_template_edges(view)
            if e.kind == 'include' and e.target and e.target.endswith('.html')]


def _closure(ctx: BackstopContext, roots: Set[str]) -> Set[str]:
    """roots 와 그 그려지는 include 닫힘(web 아래 실제 파일만)."""
    seen: Set[str] = set()
    stack: List[str] = [r for r in roots if _inside(ctx, r)]
    while stack:
        t: str = stack.pop()
        if t in seen:
            continue
        seen.add(t)
        stack.extend(x for x in _rendered_includes(ctx, t) if _inside(ctx, x))
    return seen


def _fields(ctx: BackstopContext, templates: Set[str]) -> Set[str]:
    """그려지는 요소의 `hx-get` · `data-hx-get` 값 `{{ <점 이름> }}` 의 끝 마디."""
    out: Set[str] = set()
    for t in templates:
        text: Optional[str] = _rendered_text(ctx, t)
        tags = (parsed_tags(text) or []) if text else []  # 파서가 못 읽으면 그 템플릿의 자리는 증거가 아니다
        for tag in tags:
            for name in _HX_ATTRS:
                m: Optional[re.Match[str]] = _VALUE.fullmatch((tag.attrs.get(name) or '').strip())
                if m:
                    out.add(m[1].split('.')[-1])
    return out


class _Py:
    """증거로 읽는 파이썬 파일의 AST(파일마다 한 번) — web 아래 실제 파일만."""

    def __init__(self, ctx: BackstopContext) -> None:
        self.ctx: BackstopContext = ctx
        self.trees: Dict[str, Optional[ast.Module]] = {}

    def tree(self, f: str) -> Optional[ast.Module]:
        if f not in self.trees:
            tree: Optional[ast.Module] = None
            if _inside(self.ctx, f):
                try:
                    with warnings.catch_warnings():  # 보조 파싱의 경고(잘못된 이스케이프 등)를 검사기 출력에 더하지 않는다
                        warnings.simplefilter('ignore')
                        tree = ast.parse((self.ctx.web / f).read_text(encoding='utf-8'))
                except (OSError, UnicodeError, SyntaxError, ValueError, RecursionError, MemoryError):
                    tree = None
            self.trees[f] = tree
        return self.trees[f]

    @staticmethod
    def imports(node: ast.AST) -> Dict[str, Tuple[str, str]]:
        """지역 이름 → (모듈, 원래 이름) — 함수 안 import 포함 · 절대 `web.` 만."""
        out: Dict[str, Tuple[str, str]] = {}
        for n in ast.walk(node):
            if isinstance(n, ast.ImportFrom) and not n.level and (n.module or '').startswith('web.'):
                for al in n.names:
                    out[al.asname or al.name] = (n.module or '', al.name)
        return out

    def module_file(self, dotted: str) -> Optional[str]:
        f: str = '/'.join(dotted.split('.')[1:]) + '.py'
        return f if f in self.ctx.files_set else None


def _top(tree: ast.Module, cls: Optional[str], name: str) -> Optional[_Fn]:
    """모듈 범위(cls 가 None) 또는 그 이름의 첫 클래스 본문의 함수(동기 · async)."""
    body: List[ast.stmt] = tree.body
    if cls is not None:
        c: Optional[ast.ClassDef] = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls), None)
        if c is None:
            return None
        body = c.body
    return next((n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)


def _str_consts(body: List[ast.stmt]) -> Dict[str, str]:
    """`이름 = "글자"` · `이름: T = "글자"` 대입(그 본문 범위)."""
    out: Dict[str, str] = {}
    for n in body:
        tgt: Optional[ast.expr] = (n.target if isinstance(n, ast.AnnAssign) else
                                   n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else None)
        value: object = getattr(n, 'value', None)
        if isinstance(tgt, ast.Name) and isinstance(value, ast.Constant) and isinstance(value.value, str):
            out[tgt.id] = value.value
    return out


def _vms(ctx: BackstopContext, bcdir: str, screen: str) -> List[str]:
    want: str = screen + '_vm.py'
    return sorted(f for f in ctx.files if f.startswith(bcdir + '/') and parent_dir_of(f) == 'view_model'
                  and base_name_of(f) == want)


def _paired_vms(ctx: BackstopContext, template: str) -> List[str]:
    stem: str = base_name_of(template)[:-len('.html')]
    bcdir: Optional[str] = bc_dir_of(template, ctx.areas)
    if not stem.endswith('_view') or not bcdir:
        return []
    return _vms(ctx, bcdir, stem[:-len('_view')])


def _href_calls(py: _Py, vms: List[str], fields: Set[str]) -> List[Tuple[str, str, str]]:
    """(navigator 파일, 원래 클래스 이름, 메서드) — 칸 이름 키워드 · 같은 이름 대입의 값이 바로 navigator 호출."""
    out: List[Tuple[str, str, str]] = []
    for vm in vms:
        tree: Optional[ast.Module] = py.tree(vm)
        if tree is None:
            continue
        names: Dict[str, Tuple[str, str]] = py.imports(tree)
        values: List[ast.AST] = []
        for n in ast.walk(tree):
            if isinstance(n, ast.keyword) and n.arg in fields:
                values.append(n.value)
            elif isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in fields for t in n.targets):
                values.append(n.value)
            elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id in fields and n.value:
                values.append(n.value)
        for v in values:
            if not (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and isinstance(v.func.value, ast.Name)):
                continue
            module, original = names.get(v.func.value.id, ('', ''))
            nav: Optional[str] = py.module_file(module) if module else None
            bc: Optional[str] = bc_of(nav, py.ctx.areas) if nav else None
            if (nav and bc and is_bc_root_path(nav, py.ctx.areas) and base_name_of(nav) == '%s_navigator.py' % bc
                    and (nav, original, v.func.attr) not in out):
                out.append((nav, original, v.func.attr))
    return out


def _embed_fragments(py: _Py, nav: str, cls: str, method: str) -> Optional[List[Tuple[str, str]]]:
    """navigator 메서드 → [(자식 view 모듈, 원래 함수 이름)] — reverse 첫 인자 라우트가 모두 임베드 라우트일 때만."""
    ctx: BackstopContext = py.ctx
    bc: Optional[str] = bc_of(nav, ctx.areas)
    bcdir: Optional[str] = bc_dir_of(nav, ctx.areas)
    if not bc or not bcdir:
        return None
    router: str = '%s/%s_router.py' % (bcdir, bc)
    ntree: Optional[ast.Module] = py.tree(nav)
    rtree: Optional[ast.Module] = py.tree(router)
    if ntree is None or rtree is None:
        return None
    fn: Optional[_Fn] = _top(ntree, cls, method)
    if fn is None:
        return None
    nimports: Dict[str, Tuple[str, str]] = py.imports(ntree)
    keys: List[Tuple[str, str]] = []
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Call) and ((isinstance(n.func, ast.Name) and n.func.id in _REVERSE)
                                             or (isinstance(n.func, ast.Attribute) and n.func.attr in _REVERSE))):
            continue
        arg: Optional[ast.expr] = n.args[0] if n.args else next((k.value for k in n.keywords if k.arg == 'viewname'), None)
        if not (isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name)):
            return None
        module, original = nimports.get(arg.value.id, ('', ''))
        if not module or py.module_file(module) != router:
            return None
        keys.append((original, arg.attr))
    if not keys:
        return None
    app: Optional[str] = _str_consts(rtree.body).get('app_name')
    consts: Dict[Tuple[str, str], str] = {}
    for c in rtree.body:
        if isinstance(c, ast.ClassDef):
            consts.update({(c.name, k): v for k, v in _str_consts(c.body).items()})
    rimports: Dict[str, Tuple[str, str]] = py.imports(rtree)
    bound: Dict[str, Tuple[str, str]] = {}
    for n in ast.walk(rtree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('path', 're_path')
                and len(n.args) >= 2 and isinstance(n.args[1], ast.Name)):
            name: object = next((k.value.value for k in n.keywords if k.arg == 'name' and isinstance(k.value, ast.Constant)),
                                None)
            if isinstance(name, str) and n.args[1].id in rimports:
                bound[name] = rimports[n.args[1].id]
    out: List[Tuple[str, str]] = []
    for key in keys:
        value: Optional[str] = consts.get(key)
        if not (app and value and value.startswith(app + ':')):
            return None
        module, original = bound.get(value.split(':', 1)[1], ('', ''))
        view: Optional[str] = py.module_file(module) if module else None
        vtree: Optional[ast.Module] = py.tree(view) if view else None
        if not (view and vtree and original.endswith(_FRAGMENT) and bc_dir_of(view, ctx.areas) == bcdir
                and parent_dir_of(view) == 'view' and has_seg(view, 'presentation_layer')
                and base_name_of(view) == original[:-len(_FRAGMENT)] + '_view.py' and _top(vtree, None, original)):
            return None
        out.append((view, original))
    return out


def _rendered(py: _Py, view: str, func: str) -> Set[str]:
    """임베드 함수 안 `render(<요청>, T, …)` 의 T — 글자 또는 모듈 범위 글자 상수(web 아래 실제 템플릿만)."""
    tree: Optional[ast.Module] = py.tree(view)
    fn: Optional[_Fn] = _top(tree, None, func) if tree else None
    if tree is None or fn is None:
        return set()
    consts: Dict[str, str] = _str_consts(tree.body)
    out: Set[str] = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'render':
            arg: Optional[ast.expr] = (n.args[1] if len(n.args) >= 2 else
                                       next((k.value for k in n.keywords if k.arg == 'template_name'), None))
            value: Optional[object] = (arg.value if isinstance(arg, ast.Constant) else
                                       consts.get(arg.id) if isinstance(arg, ast.Name) else None)
            if isinstance(value, str) and _inside(py.ctx, value):
                out.add(value)
    return out


def _evidence(ctx: BackstopContext, page: str) -> Tuple[Set[str], _Trace]:
    """받는 페이지가 실어도 되는 다른 BC 조각 CSS 와 첫 빈 고리 기록 — 페이지마다 한 번."""
    cache: Optional[Dict[str, Tuple[Set[str], _Trace]]] = getattr(ctx, '_embed_css_cache', None)
    if cache is None:
        cache = {}
        setattr(ctx, '_embed_css_cache', cache)
    if page in cache:
        return cache[page]
    py: Optional[_Py] = getattr(ctx, '_embed_py', None)
    if py is None:
        py = _Py(ctx)
        setattr(ctx, '_embed_py', py)
    trace: _Trace = _Trace()
    allowed: Set[str] = set()
    if page_shell(ctx, page) is not None:
        seen: Set[Tuple[str, str]] = set()
        work: List[Tuple[Set[str], List[str], bool]] = [({page}, _paired_vms(ctx, page), True)]
        while work:
            roots, vms, top = work.pop()
            fields: Set[str] = _fields(ctx, _closure(ctx, roots))
            calls: List[Tuple[str, str, str]] = _href_calls(py, vms, fields)
            if top:
                trace.fields, trace.vms, trace.calls = set(fields), list(vms), list(calls)
            for nav, cls, method in calls:
                found: Optional[List[Tuple[str, str]]] = _embed_fragments(py, nav, cls, method)
                if found is None:
                    if top:
                        trace.unbound.append('%s.%s' % (cls, method))
                    continue
                for view, func in found:
                    if top:
                        trace.bound.append('%s:%s' % (view, func))
                    if (view, func) in seen:
                        continue
                    seen.add((view, func))
                    rendered: Set[str] = _rendered(py, view, func)
                    bcdir: str = bc_dir_of(view, ctx.areas) or ''
                    for t in sorted(_closure(ctx, rendered)):
                        if (bc_dir_of(t, ctx.areas) == bcdir and has_seg(t, 'presentation_layer')
                                and parent_dir_of(t) in ('view', 'section', 'widget')):
                            css: str = 'static/%s/%s.css' % (bcdir, base_name_of(t)[:-len('.html')])
                            allowed.add(css)
                            trace.fragments.setdefault(bcdir, []).append(css)
                    work.append((rendered, _vms(ctx, bcdir, func[:-len(_FRAGMENT)]), False))
    cache[page] = (allowed, trace)
    return cache[page]


def embed_css(ctx: BackstopContext, page: str) -> Set[str]:
    """받는 페이지 머리가 실어도 되는 다른 BC 조각 CSS(web-상대 `static/application/…`)."""
    return _evidence(ctx, page)[0]


def explain(ctx: BackstopContext, page: str, target: str) -> str:
    """첫 빈 고리 한 마디(교정 줄 전용 · 한 줄)."""
    allowed, tr = _evidence(ctx, page)
    if not tr.fields:
        why: str = '이 페이지가 그리는 템플릿에 hx-get="{{ … }}" 임베드 자리가 없다'
    elif not tr.vms:
        why = '짝 VM(view_model/<화면>_vm.py)이 없다'
    elif not tr.calls:
        why = '짝 VM %s 이 자리 칸(%s)에 다른 BC navigator 호출을 바로 넘기지 않는다' % (
            ' · '.join(tr.vms), ' · '.join(sorted(tr.fields)))
    elif not tr.bound:
        why = 'navigator %s 의 reverse 라우트가 <화면>_embed_fragment 에 묶이지 않는다' % ' · '.join(tr.unbound)
    elif not allowed:
        why = '임베드 함수 %s 가 그리는 그 BC 템플릿을 글자로 읽지 못했다(render 둘째 인자 · 모듈 글자 상수)' % ' · '.join(tr.bound)
    elif target not in allowed:
        why = '이 CSS 는 임베드가 그리는 템플릿의 짝이 아니다(허용: %s)' % ' · '.join(sorted(allowed))
    else:
        why = '증거 있음'
    return ' '.join(why.splitlines())
