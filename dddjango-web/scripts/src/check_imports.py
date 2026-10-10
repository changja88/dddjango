# IM — import 방향 27종 (IM1~IM27). 게이트: touched 파일의 added 줄.
#
# *왜 결정적 백스톱인가*: 계층·컨테이너의 의존 방향(제1 규약 §3.7 매트릭스·§9-3
# 4채널·§3.6 root 규칙)은 정규화된 참조 경로 하나로 판별된다 — 의미 해석 0.
# 참조 = Python import(절대 `web.`·상대는 web/ 루트 클램핑 · 함수 안 import 포함) + 템플릿 `{% extends %}`·
# `{% include %}`·`{% static %}`(TEMPLATES DIRS = web/ 뿌리) + CSS `@import`·`url()`. 조각 CSS
# (`static/application/…`·`static/root/…`)는 소유자의 presentation 자리로 센다(houserules §5).
# 거짓양성 게이트 = added 줄 한정(레거시 파일의 기존 위반 참조에 불발화) + 표준 트리 밖 옛 배치 파일은 층 판정 불가
# 레거시라 층 무관 IM(IM24·IM25·IM27)만 건다 — 옛 배치에서는 *_data_source.py 를 DataSource 로 본다.
# + 주석·문자열 마스킹(교정 주석의 토큰이 재차 blocker가 되는 루프 차단).
# (판형: dddart check_imports.dart — IM1~IM23 번호 그대로 · IM24~IM27 = web 새 검사)
# 제품 분기(2.3.0 · web 새 분기 — dddart 대응 없음 · src/products.py — 새 검사 ID 없음). 선언이 없으면 셸은
#   root_view.html 하나 · 뿌리는 평면 하나라 2.2.x 와 같고, 아래는 제품 선언(web/product_registry.json)이 있을 때만이다.
#   IM2  — root 참조 예외 = 페이지가 선언된 셸 집합 가운데 하나를 extends 하는 줄(셸 CSS 직접 링크 예외는 없다).
#   IM26 — 선언 BC 의 템플릿은 그 BC 가 속한 제품의 셸만 · 어느 제품에도 안 든 템플릿(선언 밖 BC · root 게이트 화면)은
#          선언된 셸 가운데 하나 · 선언된 셸은 독립 문서(extends 없음) · 조각은 어느 뿌리든 `component/**.html`.
#   IM13 혼입 금지 — 소속이 정해진 문서(선언된 셸 · BC 의 템플릿과 조각 CSS · 틀 CSS · design_system 파일 — 소속 판정은
#          products.product_of: 페이지는 BC 선언이지 상속한 셸이 아니다)가 **다른 제품의 표준 자리 CSS**(foundation 표준
#          7 파일 · theme/app_theme.css · component/<군>/*.css · util/*.css)를 `{% static %}` 링크나 CSS `@import`·`url()` 로
#          실으면 발견. 대상은 실제로 실리는 파일로 본다 — 참조 원문에서 query · fragment 꼬리를 먼저 떼고 상대 경로를 풀어
#          `.` · `..` 를 접은 경로(common.loaded_file — 세 참조 꼴이 같은 술어를 지난다 · 제품 판정에만 쓴다: import edge ·
#          Finding 경로 · 빚 키와 다른 IM 은 지금처럼 참조 원문 전체를 접은 대상 그대로).
#          판정 밖: 표준 7 파일 밖 foundation 파일(옛 값 파일 — 이미 ST10 빚) · 마크업 include/extends(평면 component html 은
#          공용) · 옛 배치 페이지(소속 없음) · include 된 조각 안의 링크 · 동적 경로 · 옛 값 파일을 거친 간접 @import ·
#          `var()` 로 부르는 다른 제품 토큰.
#          게이트: 그 링크 · @import 줄이 새 줄이면 그 줄, 그 문서의 extends 줄이 새 줄이면 그 문서의 직접 CSS 링크 전부.
#          파일이 손대졌다는 이유만으로, 또는 선언 파일만 바뀌었다고 옛 링크를 새 위반으로 만들지 않는다. 빚 스캔은 전수.

from __future__ import annotations

import ast
import re
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from .common import (
    API_CLIENT, BACKEND_TOP_PKGS, ENTRY_FILES, JSON_FIELD, ROOT_VIEW_TEMPLATE, STDLIB, BackstopContext, Finding,
    MaskedSource, base_name_of, bc_of, ext_of, has_seg, is_bc_root_path, is_standard_path, parent_dir_of, ref_path,
    scan_tokens, segs_of,
)
from .products import Products, products_state

# 층과 상관없는 IM — 표준 트리 밖 옛 배치 파일(층 판정 불가 레거시)에도 건다. 나머지 IM 은 전부 층(경로 마디)
# 의존이라 옛 배치 파일에는 걸지 않는다(houserules §7·§8 — 레거시 불발화 · 이동 요구 없음). 옛 배치에서는
# *_data_source.py 를 DataSource 로 본다.
LAYER_FREE_IM: Set[str] = {'IM24', 'IM25', 'IM27'}
_HTTP_SURFACE: Set[str] = {'requests', 'httpx', 'aiohttp', 'urllib.request', 'http.client', 'django.test'}
# 제품 분기의 규약 표지(선언이 있을 때만 쓰인다)
_RULE_MIX: str = 'discipline-houserules §5·§6 제품 CSS 혼입'
_RULE_SHELL: str = 'discipline-houserules §1·§3·§5 제품 셸'
_API_LITERAL_RE = re.compile(r'''["'`]\s*/api/''')
# IM27 리터럴 절반의 예외(.py · AST) — 들어온 요청의 경로를 비교하기만 하는 글자는 API 를 부르는 주소가 아니다.
#   경로 식 P = 함수 인자 `request` 의 `.path` · `.path_info` · `.get_full_path()` · `.get_full_path_info()`(인자 없이) ·
#     `.META["PATH_INFO"]` · `.META.get("PATH_INFO")`, 또는 그 함수 안에서 `이름 = P`(`이름: T = P`) 한 번으로만 바인딩된 지역 이름.
#   빠지는 글자 = `P == "…"` · `"…" == P` · `!=`(연쇄 비교 아님) · `P.startswith(…)` · `P.endswith(…)`(인자 하나 — 글자 또는
#     글자 튜플) · `P in (…)` · `P not in (…)`(튜플 · 리스트 · 집합 리터럴의 원소) 자리에 직접 놓인 문자열 상수의 그 위치뿐이다
#     (값이나 줄이 아니다 — 같은 줄의 다른 글자 · 같은 값의 다른 출현은 그대로 IM27).
#   경계(하나라도 어기면 그 함수의 글자는 하나도 빠지지 않는다): 인자 `request` 가 그 함수에서 다시 바인딩되지 않는다 · P 와 그
#     지역 이름이 비교 자리(비교식의 피연산자 · startswith/endswith 의 받는 쪽)와 첫 `이름 = P` 밖에서 쓰이지 않는다(호출 인자 ·
#     반환 · 다른 이름에 대입 · 조건식의 값 · 안쪽 함수 · lambda · comprehension 에서 읽기 포함).
#   로그 문장의 인자로 읽는 것은 다시 쓰는 것으로 세지 않는다 — 아래 넷이 다 맞을 때만이다(하나라도 어기면 다시 쓰는 것이다).
#     ① 받는 쪽이 logging 출처로 확인된다: `logging.<수준>(…)` · `logging.getLogger(…).<수준>(…)` · `getLogger(…).<수준>(…)` ·
#        `<이름>.<수준>(…)`. `logging` · `getLogger` 는 모듈 범위에서 `import logging [as X]` · `from logging import getLogger
#        [as Y]` 한 번으로만 바인딩되고 그 함수 · 바깥 함수가 다시 바인딩하지 않은 이름, `<이름>` 은 모듈 범위나 그 함수 범위에서
#        `이름 = logging.getLogger(…)`(`이름: T = …` · `getLogger(…)`) 한 번으로만 바인딩되고 가려지거나 global · nonlocal 로 다시
#        쓰이지 않는 이름이다.
#     ② 그 호출이 독립된 표현식 문장이다(반환 · 대입 · 다른 호출의 인자 · await 안이면 아니다).
#     ③ P 에서 그 호출까지 올라가는 길에 키워드 · f-문자열 · 튜플 · 사전 · 왼쪽이 문자열 상수인 `%` 만 낀다(다른 연산 · 호출 ·
#        walrus · await · yield · 별표 · 조건식 · 첨자 · 속성 · 안쪽 범위가 끼거나 받는 쪽에서 읽으면 아니다).
#     ④ 수준 = debug · info · warning · warn · error · exception · critical · log. `log` 는 첫 위치 인자(level)가 있고 P 가 그
#        자리가 아니다.
#     로그 인자 안의 `/api/` 글자 자체는 그대로 IM27 이다(빠지는 것은 비교 자리의 글자뿐).
#   안쪽 범위가 같은 이름을 가리면(인자 · 지역 바인딩 · comprehension 대상) 그 안의 이름은 바깥 것이 아니다 — 바깥 판정에 섞지 않는다.
#   한계: 이름이 `request` 인 인자가 실제 요청 객체인지 증명하지 않는다 · 값의 흐름을 끝까지 쫓지 않는다(`request` 를 통째로 넘긴
#     뒤의 사용 · `request` 의 별칭 · getattr 는 보지 않는다). logging 출처를 확인할 수 없는 로그(`self.logger` · 인자로 받은
#     logger · 함수 안 import · 다른 객체의 같은 이름 메서드)와 응답 · 이동 호출에 경로를 넘기는 꼴(`JsonResponse({"path": path})` ·
#     `redirect(request.path)`)은 다시 쓰는 것으로 센다(그 함수의 비교 글자는 그대로 IM27 — 과보고). f-문자열 · 인접 문자열 결합 ·
#     walrus · 변수에 담은 컨테이너 · 템플릿의 같은 꼴은 예외가 아니다(지금 판정 그대로).
_REQUEST: str = 'request'
_PATH_ATTRS: Set[str] = {'path', 'path_info'}
_PATH_CALLS: Set[str] = {'get_full_path', 'get_full_path_info'}
_PREFIX_CALLS: Set[str] = {'startswith', 'endswith'}
_LOGGING: str = 'logging'
_GET_LOGGER: str = 'getLogger'
_LOG_CALLS: Set[str] = {'debug', 'info', 'warning', 'warn', 'error', 'exception', 'critical', 'log'}
_LOG_ARG_NODES = (ast.keyword, ast.JoinedStr, ast.FormattedValue, ast.Tuple, ast.Dict)
_Function = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda]
_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_SCOPES = _FUNCTIONS + (ast.ClassDef,) + _COMPREHENSIONS
# 바인딩 값 — 대상 하나짜리 대입의 값 식 · import 꼴 표지(_LOGGING · _GET_LOGGER) · 그 밖 바인딩은 None
_Binding = Union[ast.AST, str, None]
_Bindings = Tuple[Dict[str, List[_Binding]], Set[str], Set[str]]
# 문자열 리터럴 하나(접두 허용) — 마스킹 본문(tokens_view: 문자열 내용이 공백)에서 본다. 인접 문자열 결합은 맞지 않는다.
_ONE_LITERAL_RE = re.compile(r'''[rRbBuU]{0,2}("""|\'\'\'|"|')\s*\1''')


def _split(scope: ast.AST) -> Tuple[List[ast.AST], List[ast.AST]]:
    """범위 노드의 자식 → (바깥 범위가 평가하는 것, 자기 범위의 것). 바깥 몫 = 장식자 · 인자 기본값과 주석 · 상속 목록 ·
    comprehension 의 첫 iter."""
    if isinstance(scope, _COMPREHENSIONS):
        first: ast.comprehension = scope.generators[0]
        return [first.iter], [c for c in ast.iter_child_nodes(scope) if c is not first] + [first.target] + list(first.ifs)
    body = getattr(scope, 'body')
    own: List[ast.AST] = list(body) if isinstance(body, list) else [body]
    mine: Set[int] = {id(b) for b in own}
    return [c for c in ast.iter_child_nodes(scope) if id(c) not in mine], own


def _walk_scope(roots: List[ast.AST]) -> Iterator[Tuple[ast.AST, Optional[ast.AST]]]:
    """한 범위의 (노드, 부모) — 안쪽 범위 노드는 내되 그 몸으로 들어가지 않고 바깥이 평가하는 자식으로만 들어간다."""
    stack: List[Tuple[ast.AST, Optional[ast.AST]]] = [(r, None) for r in roots]
    while stack:
        node, parent = stack.pop()
        yield node, parent
        children = _split(node)[0] if isinstance(node, _SCOPES) else ast.iter_child_nodes(node)
        stack.extend((c, node) for c in children)


def _bindings(roots: List[ast.AST], args: Optional[ast.arguments] = None) -> _Bindings:
    """한 범위(함수의 자기 범위 · 모듈 본문)의 이름별 바인딩 값(_Binding) · global 선언 이름 · nonlocal 선언 이름.
    comprehension 안의 walrus 는 이 범위의 바인딩이다."""
    binds: Dict[str, List[_Binding]] = {}
    global_names: Set[str] = set()
    nonlocal_names: Set[str] = set()
    if args is not None:
        for a in args.posonlyargs + args.args + args.kwonlyargs + [x for x in (args.vararg, args.kwarg) if x]:
            binds.setdefault(a.arg, []).append(None)
    nodes: List[ast.AST] = [n for n, _parent in _walk_scope(roots)]
    simple: Dict[int, ast.AST] = {}
    for node in nodes:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            simple[id(node.targets[0])] = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            simple[id(node.target)] = node.value
    for node in nodes:
        bound: List[Tuple[str, _Binding]] = []
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                bound = [(node.id, simple.get(id(node)) if isinstance(node.ctx, ast.Store) else None)]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound = [(node.name, None)]
        elif isinstance(node, _COMPREHENSIONS):
            bound = [(n.target.id, None) for n in ast.walk(node)
                     if isinstance(n, ast.NamedExpr) and isinstance(n.target, ast.Name)]
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound = [(node.name, None)]
        elif isinstance(node, ast.Import):
            bound = [(al.asname or al.name.split('.')[0], _LOGGING if al.name == _LOGGING else None) for al in node.names]
        elif isinstance(node, ast.ImportFrom):
            from_logging: bool = node.module == _LOGGING and not node.level
            bound = [(al.asname or al.name, _GET_LOGGER if from_logging and al.name == _GET_LOGGER else None)
                     for al in node.names]
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            bound = [(node.name, None)]
        elif isinstance(node, ast.MatchMapping) and node.rest:
            bound = [(node.rest, None)]
        elif isinstance(node, ast.Global):
            global_names.update(node.names)
        elif isinstance(node, ast.Nonlocal):
            nonlocal_names.update(node.names)
        for name, value in bound:
            binds.setdefault(name, []).append(value)
    return binds, global_names, nonlocal_names


def _fn_bindings(fn: _Function) -> _Bindings:
    return _bindings(_split(fn)[1], fn.args)


def _is_str(node: ast.AST, value: Optional[str] = None) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and (value is None or node.value == value)


def _is_request_meta(node: ast.AST) -> bool:
    return (isinstance(node, ast.Attribute) and node.attr == 'META'
            and isinstance(node.value, ast.Name) and node.value.id == _REQUEST)


def _is_request_path(node: _Binding) -> bool:
    """요청 경로 식(이름 `request` 를 직접 읽는 꼴)인가 — 경로 메서드는 인자 · 키워드가 없을 때만."""
    if isinstance(node, ast.Attribute):
        return node.attr in _PATH_ATTRS and isinstance(node.value, ast.Name) and node.value.id == _REQUEST
    if isinstance(node, ast.Subscript):
        return _is_request_meta(node.value) and _is_str(node.slice, 'PATH_INFO')
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and not node.keywords:
        func: ast.Attribute = node.func
        if func.attr in _PATH_CALLS and not node.args:
            return isinstance(func.value, ast.Name) and func.value.id == _REQUEST
        if func.attr == 'get' and len(node.args) == 1:
            return _is_request_meta(func.value) and _is_str(node.args[0], 'PATH_INFO')
    return False


def _shadows(scope: ast.AST) -> Set[str]:
    """안쪽 범위가 가리는 이름 — 함수 · lambda 는 인자 · 자기 범위 바인딩 · global 선언(nonlocal 선언은 바깥 것 그대로),
    comprehension 은 for 대상. 클래스 몸은 가리지 않는 것으로 본다(보수적)."""
    if isinstance(scope, _COMPREHENSIONS):
        return {n.id for g in scope.generators for n in ast.walk(g.target) if isinstance(n, ast.Name)}
    if not isinstance(scope, _FUNCTIONS):
        return set()
    binds, global_names, nonlocal_names = _fn_bindings(scope)
    return (set(binds) | global_names) - nonlocal_names


def _inner_touches(scope: ast.AST, names: Set[str], request_live: bool) -> bool:
    """안쪽 범위(와 그 안쪽들)가 가리지 않은 채 바깥의 지역 이름을 건드리거나(읽기 · nonlocal 쓰기) 바깥 `request` 의
    경로 식을 읽거나 `request` 를 다시 바인딩하는가."""
    hidden: Set[str] = _shadows(scope)
    names = names - hidden
    request_live = request_live and _REQUEST not in hidden
    if not names and not request_live:
        return False
    for node, _parent in _walk_scope(_split(scope)[1]):
        if isinstance(node, ast.Name):
            if node.id in names or (request_live and node.id == _REQUEST and not isinstance(node.ctx, ast.Load)):
                return True
        elif isinstance(node, _SCOPES):
            if _inner_touches(node, names, request_live):
                return True
        elif request_live and _is_request_path(node):
            return True
    return False


class _LogSources:
    """모듈 범위에서 한 번으로만 바인딩된 이름의 바인딩 값 — logging 출처(`import logging` · `from logging import getLogger` ·
    `이름 = logging.getLogger(…)`) 확인의 바탕. 어느 함수든 global 로 선언한 이름은 다시 쓰일 수 있어 뺀다."""

    def __init__(self, tree: ast.Module) -> None:
        self._binds: Dict[str, List[_Binding]] = _bindings(list(tree.body))[0]
        self._rewritten: Set[str] = {n for node in ast.walk(tree) if isinstance(node, ast.Global) for n in node.names}

    def once(self, name: str) -> _Binding:
        values: List[_Binding] = self._binds.get(name, [])
        return values[0] if len(values) == 1 and name not in self._rewritten else None


def _is_get_logger(node: _Binding, lookup: Callable[[str], _Binding]) -> bool:
    """`logging.getLogger(…)` · `getLogger(…)` 호출인가 — 이름은 lookup 이 import 꼴 표지로 확인한다."""
    if not isinstance(node, ast.Call):
        return False
    func: ast.expr = node.func
    if isinstance(func, ast.Name):
        return lookup(func.id) == _GET_LOGGER
    return (isinstance(func, ast.Attribute) and func.attr == _GET_LOGGER
            and isinstance(func.value, ast.Name) and lookup(func.value.id) == _LOGGING)


def _is_log_source(recv: ast.AST, module: _LogSources, scope: _Bindings, hidden: Set[str], rewritten: Set[str]) -> bool:
    """로그 호출의 받는 쪽이 logging 출처로 확인되는가(머리 주석 ①). scope = 그 함수의 바인딩, hidden = 바깥 함수들이 바인딩한
    이름, rewritten = 그 함수의 안쪽 함수가 nonlocal 로 선언한 이름."""
    binds, global_names, nonlocal_names = scope
    outside: Set[str] = global_names | nonlocal_names

    def imported(name: str) -> _Binding:  # 그 함수 · 바깥 함수가 바인딩하지 않은 모듈 범위 이름
        return None if name in binds or name in outside or name in hidden else module.once(name)

    if not isinstance(recv, ast.Name):
        return _is_get_logger(recv, imported)
    name: str = recv.id
    if name in outside:
        return False
    if name in binds:  # 그 함수의 지역 이름
        values: List[_Binding] = binds[name]
        return len(values) == 1 and name not in rewritten and _is_get_logger(values[0], imported)
    if name in hidden:
        return False
    value: _Binding = module.once(name)
    return value == _LOGGING or _is_get_logger(value, module.once)


def _logged(node: ast.AST, parent_of: Dict[int, Optional[ast.AST]], is_source: Callable[[ast.AST], bool]) -> bool:
    """경로 식이 logging 출처의 독립된 로그 문장 인자 안에서 읽히는가(머리 주석 ① ~ ④)."""
    child: ast.AST = node
    parent: Optional[ast.AST] = parent_of.get(id(node))
    while isinstance(parent, _LOG_ARG_NODES) or (
            isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Mod) and _is_str(parent.left)):
        child, parent = parent, parent_of.get(id(parent))
    if not (isinstance(parent, ast.Call) and isinstance(parent.func, ast.Attribute) and parent.func.attr in _LOG_CALLS
            and isinstance(parent_of.get(id(parent)), ast.Expr)):
        return False
    if not (any(child is a for a in parent.args) or any(child is k for k in parent.keywords)):
        return False  # 받는 쪽에서 읽는다
    if parent.func.attr == 'log' and (not parent.args or isinstance(parent.args[0], ast.Starred) or child is parent.args[0]):
        return False
    return is_source(parent.func.value)


def _compared_literals(fn: _Function, module: _LogSources, hidden: Set[str]) -> List[ast.expr]:
    """함수 하나에서 요청 경로와 비교되는 자리에 직접 놓인 문자열 상수 — 경계(머리 주석)를 하나라도 어기면 빈 목록.
    hidden = 바깥 함수들이 바인딩한 이름."""
    args: ast.arguments = fn.args
    if _REQUEST not in {a.arg for a in args.posonlyargs + args.args + args.kwonlyargs}:
        return []
    scope: _Bindings = _fn_bindings(fn)
    binds, global_names, nonlocal_names = scope
    outside: Set[str] = global_names | nonlocal_names
    if len(binds[_REQUEST]) != 1 or _REQUEST in outside:
        return []
    first_values: Dict[str, _Binding] = {n: vs[0] for n, vs in binds.items()
                                         if len(vs) == 1 and _is_request_path(vs[0]) and n not in outside}
    aliases: Set[str] = set(first_values)
    first_ids: Set[int] = {id(v) for v in first_values.values()}
    nodes: List[Tuple[ast.AST, Optional[ast.AST]]] = list(_walk_scope(_split(fn)[1]))
    parent_of: Dict[int, Optional[ast.AST]] = {id(n): p for n, p in nodes}
    rewritten: Set[str] = {n for node, _parent in nodes if isinstance(node, _SCOPES)
                           for inner in ast.walk(node) if isinstance(inner, ast.Nonlocal) for n in inner.names}

    def is_path(node: ast.AST) -> bool:
        return _is_request_path(node) or (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                                           and node.id in aliases)

    def is_source(recv: ast.AST) -> bool:
        return _is_log_source(recv, module, scope, hidden, rewritten)

    found: List[ast.expr] = []
    for node, parent in nodes:
        if isinstance(node, _SCOPES):
            if _inner_touches(node, aliases, True):
                return []
        elif is_path(node) and id(node) not in first_ids:
            grand: Optional[ast.AST] = parent_of.get(id(parent))
            if not (isinstance(parent, ast.Compare) or (
                    isinstance(parent, ast.Attribute) and parent.attr in _PREFIX_CALLS
                    and isinstance(grand, ast.Call) and grand.func is parent) or _logged(node, parent_of, is_source)):
                return []
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            op, lhs, rhs = node.ops[0], node.left, node.comparators[0]
            if isinstance(op, (ast.Eq, ast.NotEq)):
                found += [other for side, other in ((lhs, rhs), (rhs, lhs)) if is_path(side) and _is_str(other)]
            elif isinstance(op, (ast.In, ast.NotIn)) and is_path(lhs) and isinstance(rhs, (ast.Tuple, ast.List, ast.Set)):
                found += [e for e in rhs.elts if _is_str(e)]
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in _PREFIX_CALLS
              and len(node.args) == 1 and not node.keywords and is_path(node.func.value)):
            arg: ast.expr = node.args[0]
            found += [arg] if _is_str(arg) else [e for e in arg.elts if _is_str(e)] if isinstance(arg, ast.Tuple) else []
    return found


def _functions(tree: ast.Module) -> Iterator[Tuple[_Function, Set[str]]]:
    """모듈 안의 함수 · lambda 와 그 바깥 함수들이 바인딩(global · nonlocal 선언 포함)한 이름. 클래스 몸의 이름은 메서드에서
    보이지 않으니 넣지 않는다."""
    stack: List[Tuple[ast.AST, Set[str]]] = [(tree, set())]
    while stack:
        node, hidden = stack.pop()
        if isinstance(node, _FUNCTIONS):
            yield node, hidden
            binds, global_names, nonlocal_names = _fn_bindings(node)
            hidden = hidden | set(binds) | global_names | nonlocal_names
        stack.extend((c, hidden) for c in ast.iter_child_nodes(node))


def _request_path_spans(ms: MaskedSource) -> List[Tuple[int, int]]:
    """요청 경로와 비교되는 문자열 상수의 본문 오프셋 구간 [시작, 끝) — 파싱하지 못하면 빈 목록(지금처럼 IM27).
    AST 의 열은 UTF-8 바이트 자리라 글자 자리로 바꾼다. 마스킹 본문 · 원문은 읽기만 한다."""
    try:
        tree: ast.Module = ast.parse(ms.original)
    except (SyntaxError, ValueError):
        return []
    text: str = ms.original

    def offset(line: int, col: int) -> int:
        start: int = ms.line_starts[line - 1]
        end: int = ms.line_starts[line] if line < len(ms.line_starts) else len(text)
        return start + len(text[start:end].encode('utf-8')[:col].decode('utf-8', errors='ignore'))

    module: _LogSources = _LogSources(tree)
    spans: List[Tuple[int, int]] = []
    for fn, hidden in _functions(tree):
        for c in _compared_literals(fn, module, hidden):
            a, b = offset(c.lineno, c.col_offset), offset(c.end_lineno or c.lineno, c.end_col_offset or 0)
            if _ONE_LITERAL_RE.fullmatch(ms.tokens_view, a, b):  # 인접 문자열 결합은 상수 하나가 아니다
                spans.append((a, b))
    return spans


def _http_surface(module: str, names: List[str]) -> Optional[str]:
    for s in sorted(_HTTP_SURFACE):
        if module == s or module.startswith(s + '.'):
            return s
        head, _, tail = s.rpartition('.')
        if head and module == head and tail in names:
            return s
    return None


def run_imports(ctx: BackstopContext) -> List[Finding]:
    out: List[Finding] = []
    backend: Set[str] = BACKEND_TOP_PKGS | ctx.project_pkgs
    products: Products = products_state(ctx)
    for f in ctx.files:
        if not ctx.is_touched(f):
            continue
        ext: str = ext_of(f)
        if ext not in ('.py', '.html', '.css'):
            continue
        fv: str = ref_path(f)  # 조각 CSS 는 소유자의 presentation 자리로 센다
        segs: List[str] = segs_of(fv)
        bc: Optional[str] = bc_of(fv, ctx.areas)
        base: str = base_name_of(fv)
        parent: str = parent_dir_of(fv)
        in_domain: bool = has_seg(fv, 'domain_layer')
        in_app: bool = has_seg(fv, 'application_layer')
        in_infra: bool = has_seg(fv, 'infra_layer')
        in_pres: bool = has_seg(fv, 'presentation_layer')
        is_bc_root_file: bool = is_bc_root_path(fv, ctx.areas)
        is_navigator: bool = is_bc_root_file and base == '%s_navigator.py' % bc
        is_bc_router: bool = is_bc_root_file and base == '%s_router.py' % bc
        is_entry: bool = f in ENTRY_FILES  # main.dart 자리(web/apps.py·web/urls.py)
        in_root: bool = segs[0] == 'root'
        is_page: bool = in_pres and parent == 'view' and ext == '.html'
        is_root_gate_page: bool = (fv.startswith('root/scaffold/view/') and base.startswith('root_')
                                   and base.endswith('_view.html') and base != 'root_view.html'
                                   and f not in products.shells)  # 선언된 제품 셸은 게이트 화면이 아니다
        is_fragment_tpl: bool = ext == '.html' and (
            (in_pres and parent in ('section', 'widget')) or products.in_component(fv))
        in_network: bool = fv.startswith('common/network/')
        legacy: bool = not is_standard_path(f)  # 표준 트리 밖 옛 배치 — 층 판정 불가
        # 제품 분기 — 이 문서의 소속 제품(선언이 없거나 옛 배치 · 소속 없음이면 None) · extends 줄이 새 줄인가
        owner: Optional[str] = None if legacy else products.product_of(f, ctx.areas)
        extends_added: bool = owner is not None and any(
            x.kind == 'extends' and ctx.line_is_added(f, x.line) for x in ctx.edges_of(f))

        def add(cid: str, line: int, msg: str, rule: str, fix: str) -> None:
            if legacy and cid not in LAYER_FREE_IM:
                return
            if ctx.line_is_added(f, line):
                out.append(Finding(cid, f, line, msg, rule, fix))

        for e in ctx.edges_of(f):
            t: str = ref_path(e.target or '')
            internal: bool = e.internal and bool(t)
            py_ext: bool = e.kind == 'py' and not e.internal
            mod: str = e.module or ''

            # ---- IM1: domain → django 금지
            if in_domain:
                if py_ext and e.top == 'django':
                    add('IM1', e.line, 'domain_layer에서 `%s` import — 순수 Python 계층' % mod,
                        '제1 규약 §3.2',
                        'UI 매핑(CSS 클래스·아이콘·라벨)은 presentation의 ui_extension/으로 — 도메인은 표준 라이브러리만.')
                # ---- IM19: domain → 비domain 내부 경로 금지 (직파싱 단일 출처 json_field 하나 예외 —
                #      dddart 모델이 json_serializable 외부 패키지를 쓰던 자리)
                if internal and not has_seg(t, 'domain_layer') and t != JSON_FIELD:
                    add('IM19', e.line, 'domain_layer에서 `%s` 참조 — domain은 domain만 본다(common 포함 금지)' % t,
                        '제1 규약 §3.7', '도메인 이유로만 바뀌는 코드만 남기고, 변환·조율은 UseCase/VM으로 올린다.')

            # ---- IM2: root 참조는 apps.py·urls.py만 (root 내부 상호 참조 · 페이지의 root_view extends 제외)
            if internal and t.startswith('root/') and not in_root and not is_entry:
                if not (e.kind == 'extends' and t in products.shells and is_page):
                    add('IM2', e.line, 'root/ 참조 `%s` — root를 아는 곳은 apps.py·urls.py뿐'
                        '(페이지 템플릿의 %s extends 1건 예외 · BC가 root를 알면 격리 붕괴)' % (
                            t, '선언된 제품 셸' if products.declared else 'root_view.html'),
                        '제1 규약 §3.6',
                        '필요한 것이 전역 인스턴스면 common으로, 전 BC 배선이면 root handler가 *이쪽을* 호출하는 방향으로 뒤집는다.')

            # ---- IM3·IM4: common·design_system → application·root 금지
            if segs[0] == 'common' and internal and (t.startswith('application/') or t.startswith('root/')):
                add('IM3', e.line, 'common에서 `%s` 참조 — common은 모두가 아는 곳, 아무도 모르면 안 된다' % t,
                    '제1 규약 §6', 'BC 어휘가 필요하면 그 코드는 common 실격 — 해당 BC로 옮기고, BC 일이 필요하면 콜백 주입으로 뒤집는다.')
            if segs[0] == 'design_system' and internal and (t.startswith('application/') or t.startswith('root/')):
                add('IM4', e.line, 'design_system에서 `%s` 참조 — 시각 요소는 BC 어휘를 모른다' % t,
                    '제1 규약 §6', '도메인 의존 부품은 그 BC presentation의 widget으로 내린다.')

            # ---- IM5: 교차 BC 4채널
            if bc is not None and internal:
                tbc: Optional[str] = bc_of(t, ctx.areas)
                if tbc is not None and tbc != bc:
                    ts: List[str] = segs_of(t)
                    in_t_domain: bool = has_seg(t, 'domain_layer')
                    domain_type: bool = in_t_domain and (
                        has_seg(t, 'entity') or has_seg(t, 'value_object') or has_seg(t, 'enum')
                        or (len(ts) >= 3 and ts[-3] == 'domain_layer' and ts[-1] == '%s.py' % ts[-2])
                        or base_name_of(t) == 'exception.py')
                    ok: bool = (domain_type or has_seg(t, 'use_case')
                                or (is_bc_root_path(t, ctx.areas) and base_name_of(t) == '%s_navigator.py' % tbc)
                                or (has_seg(t, 'presentation_layer') and has_seg(t, 'view')))
                    if not ok:
                        reason: str = ('domain_service·specification은 도메인 로직 — 채널①은 타입(엔티티·VO·enum)만, 행위는 UseCase 관문'
                                       if in_t_domain else
                                       'infra·VM·SharedState·state·section·widget·ui_extension은 채널 밖')
                        add('IM5', e.line, '타 BC `%s`의 `%s` 참조 — 교차 BC는 4채널만(%s)' % (tbc, t, reason),
                            '제1 규약 §9-3',
                            '데이터·행위는 그 BC UseCase 호출, 표시는 view 임베드, 이동은 navigator, 타입은 entity/value_object/enum만.')

            # ---- IM6: root → BC infra 금지
            if in_root and internal and has_seg(t, 'infra_layer'):
                add('IM6', e.line, 'root에서 BC infra `%s` 참조 — root도 Model 규율(UseCase만) 적용' % t,
                    '제1 규약 §3.6', '그 BC UseCase를 호출한다.')

            # ---- IM7: VM·SharedState·Service → infra·api_client 금지
            if in_app and parent in ('view_model', 'shared_state', 'service') and internal:
                if has_seg(t, 'infra_layer') or t == API_CLIENT:
                    add('IM7', e.line, 'ViewModel 변종에서 `%s` 참조 — Model 방향은 UseCase만' % t,
                        '제1 규약 §3.3', '위임 한 줄짜리라도 UseCase를 거친다 — 관문의 일관성이 지름길의 근거가 되지 않는다.')

            # ---- IM8: section·widget·ui_extension → application_layer 금지(VM·상태 계층을 모른다)
            if in_pres and parent in ('section', 'widget', 'ui_extension') and internal and has_seg(t, 'application_layer'):
                add('IM8', e.line, '%s에서 application_layer `%s` 참조 — dumb 표현 조각은 VM·상태의 존재를 모른다' % (parent, t),
                    '제1 규약 §3.5', '값은 include 인자·필터 인자로 받는다. 상태가 필요해진 것은 승격 신호 — view+vm 쌍(삼총사)으로 승격한다.')

            # ---- IM9: widget → 화면 전속 조각(section·view) 금지
            if in_pres and parent == 'widget' and internal and has_seg(t, 'presentation_layer') \
                    and (has_seg(t, 'section') or has_seg(t, 'view')):
                add('IM9', e.line, 'widget에서 화면 전속 조각 `%s` 참조 — 재사용 부품은 화면을 모른다' % t,
                    '제1 규약 §3.5', '엔티티·원시값·href 를 include 인자로 받는다. 화면 전속이면 section으로.')

            # ---- IM10·IM21: navigator의 금지 방향
            if is_navigator and internal:
                if has_seg(t, 'presentation_layer'):
                    add('IM10', e.line, 'navigator에서 presentation `%s` 참조 — URL name만 참조' % t,
                        '제1 규약 §3.1', '`<Bc>Routes` 상수(reverse)만 쓴다 — view 참조는 순환(VM→navigator→view→VM)을 만든다.')
                elif has_seg(t, 'domain_layer') or has_seg(t, 'application_layer') or has_seg(t, 'infra_layer'):
                    add('IM21', e.line, 'navigator에서 계층 코드 `%s` 참조 — navigator는 정적 href 헬퍼일 뿐' % t,
                        '제1 규약 §3.7', 'navigator의 합법 참조는 자기 router(URL name 상수)·common·django.urls뿐.')

            # ---- IM11: application → presentation 금지
            if in_app and internal and has_seg(t, 'presentation_layer'):
                add('IM11', e.line, 'application_layer에서 presentation `%s` 참조 — 역류' % t,
                    '제1 규약 §3.7', 'UI가 필요한 결정은 State로 노출하고 view가 응답(redirect·조각)으로 소비한다.')

            # ---- IM12(import 절반): application → django 전면 금지(django.utils 예외)
            if in_app and py_ext and e.top == 'django' and not (mod == 'django.utils' or mod.startswith('django.utils.')):
                add('IM12', e.line, 'application_layer에서 `%s` import — 요청·응답·템플릿 호출 금지' % mod,
                    '제1 규약 §3.3·§3.7',
                    '요청·응답은 view로, href 는 navigator로, 표시 매핑은 ui_extension으로. django.utils(비UI 유틸)만 허용.')

            # ---- IM13: design_system 참조 화이트리스트
            if internal and t.startswith('design_system/'):
                if not (in_pres or fv.startswith('root/scaffold/') or segs[0] == 'design_system'):
                    add('IM13', e.line, '`%s` 참조 — design_system은 presentation·root scaffold·design_system 내부만' % t,
                        '제1 규약 §3.7', '시각 토큰이 필요한 로직은 ui_extension(도메인→UI 매핑의 유일한 자리)으로 옮긴다.')

            # ---- IM14(import 절반): app service → navigator 금지
            if in_app and parent == 'service' and internal and base_name_of(t).endswith('_navigator.py'):
                add('IM14', e.line, 'application service에서 navigator 참조 — 내비는 VM만',
                    '제1 규약 §3.7·§3.6', '비화면 이벤트발 화면 이동은 root_destination_handler 소유 — 진입 URL로 정규화해 디스패치한다.')

            # ---- IM15: apps.py·urls.py 역참조 금지
            if internal and t in ENTRY_FILES and segs[0] in ('application', 'common', 'design_system'):
                add('IM15', e.line, '`web/%s` 참조 — 엔트리포인트를 역참조' % t,
                    '제1 규약 §3.6', '필요한 전역 인스턴스(logger 등)는 common 소속으로 옮긴다.')

            # ---- IM16: apps.py·urls.py import 화이트리스트
            if is_entry and e.kind == 'py':
                ok_ext: bool = py_ext and (e.top in STDLIB or e.top == 'django')
                ok_int: bool = internal and t.startswith('root/')
                if not (ok_ext or ok_int):
                    add('IM16', e.line, '`web/%s` 화이트리스트 외 import `%s` — 엔트리포인트 최소형' % (f, e.uri),
                        '제1 규약 §3.6',
                        '시동은 root_initializer, 라우팅은 root_router 한 줄 — 그 외는 apps.py·urls.py의 일이 아니다.')

            # ---- IM17: presentation → infra 금지
            if in_pres and internal and has_seg(t, 'infra_layer'):
                add('IM17', e.line, 'presentation에서 infra `%s` 참조 — view→Repo 직행' % t,
                    '제1 규약 §3.7', '데이터는 VM이 UseCase로 가져와 State로 노출한다.')

            # ---- IM18: infra → application·presentation 금지
            if in_infra and internal and (has_seg(t, 'application_layer') or has_seg(t, 'presentation_layer')):
                add('IM18', e.line, 'infra에서 상위 계층 `%s` 참조 — 역류' % t,
                    '제1 규약 §3.7', 'infra는 호출당하는 쪽 — 필요한 값은 인자로 받는다.')

            # ---- IM20: use_case·state·shared_state → navigator 금지
            if in_app and parent in ('use_case', 'state', 'shared_state') and internal \
                    and base_name_of(t).endswith('_navigator.py'):
                add('IM20', e.line, '%s에서 navigator 참조 — BC 루트 호출은 VM만' % parent,
                    '제1 규약 §3.7', '화면 전환은 VM의 일 — UseCase는 Either만 반환하고 결정은 VM이 한다.')

            # ---- IM22: router 허용 목록
            if is_bc_router and internal:
                tbc = bc_of(t, ctx.areas)
                ok = t.startswith('common/') or (tbc == bc and (
                    (has_seg(t, 'presentation_layer') and has_seg(t, 'view')) or is_bc_root_path(t, ctx.areas)))
                if not ok:
                    add('IM22', e.line, 'router에서 `%s` 참조 — router는 자기 BC view(path 대상 함수)·BC 루트·common만' % t,
                        '제1 규약 §3.7·§3.1', 'section·widget은 view가 조립하고, 게이트 상태 확인은 root 쪽(UseCase 직접 생성)의 일.')

            # ---- IM23(import 절반): router·navigator → datetime 직접 import 금지(날짜 직렬화 보유 금지)
            if (is_bc_router or is_navigator) and py_ext and e.top == 'datetime':
                add('IM23', e.line, 'BC 루트(%s)에서 `%s` import — 날짜 직렬화 보유 금지' % ('router' if is_bc_router else 'navigator', mod),
                    'architecture-ddd §3.72·architecture-ui §6',
                    '날짜→path 변환은 도메인 VO 메서드(우선)·VM 변환에 단일 거주하고, router·navigator는 결과 str을 전달만 한다.')

            # ---- IM24: 상대 import 금지
            if e.kind == 'py' and e.relative:
                add('IM24', e.line, '상대 import `from %s import …` — web/ 의 import 는 `web.` 절대 경로만' % e.uri,
                    '제1 규약 §2', '`from web.<경로> import …` 로 바꾼다 — 경로 한 줄로 계층·BC가 식별되는 설계.')

            # ---- IM25: 백엔드 내부 import 금지
            if py_ext and e.top in backend:
                add('IM25', e.line, 'web에서 백엔드 내부 `%s` import — web 과 백엔드의 계약은 API(URL+JSON)뿐' % mod,
                    '제1 규약 §3.7',
                    'import를 지우고 DataSource가 api_client로 API를 부른다 — 필요한 API가 없으면 가정 계약으로 짓고 '
                    '실제 API는 /dddjango 로 요청한다.')

            # ---- IM26: extends 대상 — 페이지 템플릿은 root_view.html 만 · 조각 템플릿(section·widget·component)은
            #      design_system component 만(부품이 내놓은 block 채우기 = 위젯 slot 인자 자리) · 그 밖은 root_view.html 만
            if e.kind == 'extends':
                who: str = '조각 템플릿' if is_fragment_tpl else '페이지(그 밖) 템플릿'
                rule26: str = '제1 규약 §3.6·§5'
                fix26: str = ('페이지는 root_view.html 을 extends 하고, 조각은 값은 include … only 로·마크업 자리는 '
                              'design_system component 를 extends 해 block 만 채운다.')
                if is_fragment_tpl and not (is_page or is_root_gate_page):
                    ok26: bool = products.in_component(t) and t.endswith('.html')
                    want: str = 'design_system/component/**/*.html(부품의 block 채우기)'
                    if products.declared:  # 선언 모드의 문구 — 셸 · 부품 뿌리가 하나가 아니다(무선언 문구는 글자 그대로)
                        want = '어느 제품 뿌리든 design_system component 의 html(부품의 block 채우기)'
                        fix26 = ('조각은 값은 include … only 로·마크업 자리는 어느 제품 뿌리든 design_system component 를 extends 해 '
                                 'block 만 채운다(페이지만 그 BC 가 속한 제품의 셸을 extends 한다).')
                elif not products.declared:
                    ok26 = t == ROOT_VIEW_TEMPLATE
                    want = 'root_view.html 하나'
                else:  # 제품 분기 — 셸은 독립 문서 · 선언 BC 의 템플릿은 그 제품 셸만 · 그 밖은 선언된 셸 가운데 하나
                    rule26 = _RULE_SHELL
                    fix26 = ('페이지는 그 BC 가 속한 제품의 셸을 extends 한다(제품과 화면 범위는 web/product_registry.json 의 '
                             '선언 — 선언은 사용자 결정으로만 바뀐다). 제품 셸은 독립 문서라 extends 하지 않는다.')
                    if f in products.shells:
                        ok26, who, want = False, '제품 셸', '없다(제품 셸은 독립 문서 — 다른 템플릿을 상속하지 않는다)'
                    elif owner is not None:
                        ok26 = t == products.shell_of(owner)
                        who, want = '제품 `%s` 화면' % owner, '그 제품 셸 `%s` 하나' % products.shell_of(owner)
                    else:
                        ok26 = t in products.shells
                        want = '선언된 제품 셸(%s) 가운데 하나' % ' · '.join(sorted(products.shells))
                if not ok26:
                    add('IM26', e.line, '`{%% extends %%}` 대상 `%s` — %s의 상속 대상은 %s' % (t, who, want), rule26, fix26)

            # ---- IM27(import 절반): HTTP 호출 표면은 common/network 전속
            if py_ext and not in_network:
                surf: Optional[str] = _http_surface(mod, e.names)
                if surf:
                    add('IM27', e.line, 'common/network 밖 HTTP 호출 표면 `%s` import' % surf,
                        '제1 규약 §3.4·§6',
                        'API 호출은 common/network/api_client.py·safe_api_call.py 하나로 — DataSource는 그것을 부른다.')

        # ---- IM13 제품 분기(혼입 금지 — 선언이 있을 때만 · 머리 주석): 소속이 정해진 문서가 다른 제품의 표준 자리 CSS 를 싣는다.
        #      대상은 import edge 가 아니라 그 문서가 실제로 싣는 파일이다(ctx.loads_of — 참조 원문에서 꼬리를 먼저 떼고 푼다)
        if owner is not None:
            for line, loaded in ctx.loads_of(f):
                other: Optional[str] = products.standard_css_owner(loaded)
                if other is not None and other != owner and (extends_added or ctx.line_is_added(f, line)):
                    out.append(Finding('IM13', f, line,
                        '제품 `%s` 의 문서가 다른 제품 `%s` 의 표준 자리 CSS `%s` 를 싣는다 — 제품 사이 CSS 혼입 금지'
                        % (owner, other, loaded), _RULE_MIX,
                        '그 문서의 제품 뿌리(%s/)에 있는 같은 군·같은 이름의 CSS 를 싣는다 — 없으면 그 제품 뿌리에 만든다'
                        '(마크업은 평면 component html 을 include 해 같이 써도 된다 · 제품은 web/product_registry.json 의 선언).'
                        % products.ds_root(owner)))

        # ================= 토큰 검사 (마스킹 본문, added 줄 게이트) =================
        if ext == '.py':
            ms = ctx.mask_of(f)
            import_lines: Set[int] = {e.line for e in ctx.edges_of(f)}

            def add_token(cid: str, line: int, msg: str, rule: str, fix: str) -> None:
                if line not in import_lines:
                    add(cid, line, msg, rule, fix)
            # IM12: 요청·응답 객체 토큰 (BuildContext 자리)
            if in_app:
                for line, _ in scan_tokens(ms, re.compile(
                        r'\bHttpRequest\b|\bHttpResponse\w*\b|\brequest\.(?:GET|POST|session|META|COOKIES|headers|user)\b')):
                    add_token('IM12', line, 'application_layer에서 요청·응답 객체 보유', '제1 규약 §3.3·§9-7',
                        'view가 요청에서 원시값을 꺼내 VM에 넘긴다 — 화면 전환은 navigator href, 에러는 State 노출.')
            # IM14: service의 내비 호출 토큰
            if in_app and parent == 'service':
                for line, _ in scan_tokens(ms, re.compile(r'\b(?:reverse|reverse_lazy|redirect)\s*\(')):
                    add_token('IM14', line, 'application service에서 내비 호출(`reverse(`·`redirect(`)', '제1 규약 §3.6',
                        '비화면 이벤트의 화면 이동은 root_destination_handler가 진입 URL로 디스패치한다.')
            # IM23(토큰 절반): router·navigator의 날짜 직렬화 토큰
            if is_bc_router or is_navigator:
                for line, _ in scan_tokens(ms, re.compile(r'\.strftime\s*\(|\.isoformat\s*\(\s*\)')):
                    add_token('IM23', line, 'BC 루트(%s)에서 날짜 직렬화(`strftime`/`isoformat`) 보유 — BC 루트는 변환을 모른다'
                        % ('router' if is_bc_router else 'navigator'),
                        'architecture-ddd §3.72·architecture-ui §6', '날짜→path 변환은 도메인 VO·VM 단일 거주, router·navigator는 str 전달만.')
        # IM27(리터럴 절반): API URL 리터럴은 DataSource·common/network 전속 — .py 의 요청 경로 비교 글자는 뺀다(머리 상수 주석)
        if ext != '.css' and not in_network and not (
                (in_infra and parent == 'data_source') or (legacy and base.endswith('_data_source.py'))):
            ms = ctx.mask_of(f)
            hits: List[Tuple[int, int]] = scan_tokens(ms, _API_LITERAL_RE, view='no_comments')
            compared: List[Tuple[int, int]] = _request_path_spans(ms) if ext == '.py' and hits else []
            for line, end in hits:
                if any(a < end <= b for a, b in compared):
                    continue
                add('IM27', line, 'DataSource 밖 API URL 리터럴 `/api/…`', '제1 규약 §3.4',
                    ('옛 배치 단위에서는 API path 를 <개념>_data_source.py 파일에만 둔다(표준 단위는 그 BC infra_layer/data_source/).'
                     if legacy else 'API path 는 그 BC infra_layer/data_source/<개념>_data_source.py 에만 둔다.'))
    return out
