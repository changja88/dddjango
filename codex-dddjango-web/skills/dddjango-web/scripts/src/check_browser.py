# TG4 — 브라우저 시험 꼴(빚 스캔 밖 · 슬라이스 끝에도 돈다).
#
# 새 브라우저 시험은 pytest-playwright 공용 고정물(`page` · 시험마다 새 context)만 받는다(implementation-test §4
# «브라우저는 공용 고정물만»). 이 검사는 이번 실행이 바꾼(지운 · 옮긴 것 포함) 시험 쪽 파일 전체를 묶어 두 합을
# 기준판과 현재판으로 견준다 — 어느 합이든 늘었을 때만 발견이다(늘어난 띄움 요청만 · 기존 파일을 빚으로 잡지 않는다).
#   띄움 자리 — 파일 안에서 브라우저를 띄우는 자리:
#     (가) 직접 띄우기 `X.launch` · `launch_persistent_context` · `connect` · `connect_over_cdp`(X 가 chromium ·
#          firefox · webkit · browser_type 또는 그 값을 대입받은 이름) · `sync_playwright()` · `async_playwright()` ·
#          받은 `launch_browser` 부르기
#     (나) 하위 프로세스가 띄움 JS 를 실행 — `-e`·`--eval`·`-p`·`--print` 뒤 정적 JS · 정적으로 풀리는 프로젝트 안
#          `.js`·`.cjs`·`.mjs` 경로(실행기 이름은 보지 않는다)
#     (다) 브라우저 실행 파일(첫 낱말이 브라우저 · 또는 `--headless` 와 브라우저 전용 낱말이 함께) ·
#     (라) Playwright CLI(`playwright test|open|codegen|screenshot|pdf`)
#     (마) `selenium`·`pyppeteer`·`splinter` import · (바) 시험 트리 JS 의 띄움 토큰 · (사) 브라우저 단위 고정물의
#          정의 · 덮기(`playwright`·`browser_type`·`browser`·`launch_browser`·`browser_type_launch_args`·`connect_options`)
#   띄우는 시험 경우 — 그런 자리에 닿는 시험 함수 × 매개변수 경우. 받는 고정물 · 부르는 도우미를 같은 모듈 · 조상 conftest ·
#     import 한 프로젝트 모듈(web/ 밖)로 따라간다. pytest-playwright 공용 이름을 받는 것은 닿지 않는다.
# 기준판은 파일마다 기준..HEAD 첫 부모 사슬에서 그 파일을 상류판 그대로 들인 마지막 승인 병합의 판(없으면 기준점 판)이고
# 따라간 모듈 · conftest · JS 러너도 같은 규칙으로 읽는다 — 승인 병합이 들인 띄움은 발견이 아니다(승인 유입 가름 밖).
# 기준판과 현재판 바이트가 같은 파일은 읽지 않는다. 파이썬 구문 · JS 토큰 해석에 실패한 파일은 그 파일만 두 쪽 셈에서
# 빼고 알린다(한 쪽만 빼면 거짓 늘어남이 생긴다). 함수 인자로 넘긴 도우미 · getattr · 동적 import · 기존 node 스크립트
# 안의 새 장면은 지원 밖이다(감수).

from __future__ import annotations

import ast
import copy
import posixpath
import shlex
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, List, Optional, Set, Tuple

from .check_tests import Collected, _call_name, _collect, _js_tokens, _line_delta, _recorded, _value, js_in_test_tree
from .common import JS_EXTS, BackstopContext, Finding, module_candidates
from .sdk_registry import git_blob_id

_RULE: str = 'implementation-test §4 «브라우저는 공용 고정물만» / coder-web 행위 검증 테스트'
_FIX: str = ('새 시험은 page(또는 browser 에서 시험마다 new_context)를 받는다 · 기존 시험 · 도우미는 그대로 두고 '
             'page · context 를 넘겨 쓴다 · 브라우저 단위 설정이 꼭 필요하면 고치지 말고 보고한다')

LAUNCH_OWNERS: Set[str] = {'chromium', 'firefox', 'webkit', 'browser_type'}
LAUNCH_METHODS: Set[str] = {'launch', 'launch_persistent_context', 'connect', 'connect_over_cdp'}
PLAYWRIGHT_STARTERS: Set[str] = {'sync_playwright', 'async_playwright'}
JS_OWNERS: Set[str] = {'chromium', 'firefox', 'webkit', 'browserType', 'puppeteer'}
JS_METHODS: Set[str] = {'launch', 'launchPersistentContext', 'launchServer', 'connect', 'connectOverCDP'}
BROWSER_EXES: Set[str] = {'chrome', 'chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'msedge',
                          'chrome-headless-shell'}
# 브라우저 전용 낱말 — `--headless` 와 함께 있을 때만 자리(`--headless` 하나는 다른 도구도 쓴다)
BROWSER_ONLY_FLAGS: Tuple[str, ...] = ('--dump-dom', '--screenshot', '--print-to-pdf', '--remote-debugging-port')
CLI_VERBS: Set[str] = {'test', 'open', 'codegen', 'screenshot', 'pdf'}
E2E_MODULES: Set[str] = {'selenium', 'pyppeteer', 'splinter'}
BROWSER_SCOPE_FIXTURES: Set[str] = {'playwright', 'browser_type', 'browser', 'launch_browser', 'browser_type_launch_args',
                                    'connect_options'}
# pytest-playwright 공용 이름 — 받는 것은 닿음이 아니다(덮기는 (사) · launch_browser 를 부르는 것은 (가))
PUBLIC_FIXTURES: Set[str] = {'playwright', 'browser_type', 'browser', 'context', 'page', 'new_context',
                             'browser_context_args', 'browser_type_launch_args', 'connect_options', 'launch_browser'}
_PROCESS: Set[str] = {'subprocess.run', 'subprocess.Popen', 'subprocess.call', 'subprocess.check_call',
                      'subprocess.check_output', 'asyncio.create_subprocess_exec', 'asyncio.create_subprocess_shell',
                      'os.system', 'os.popen'}
_SHELL_STRING: Set[str] = {'os.system', 'os.popen', 'asyncio.create_subprocess_shell'}
_EVAL_FLAGS: Set[str] = {'-e', '--eval', '-p', '--print'}
# 시험 쪽이 아닌 모듈은 이 낱말이 없으면 띄우는 이름이 없다고 본다(구문 해석을 건너뛴다)
_LAUNCH_HINTS: Tuple[str, ...] = ('launch', 'playwright', 'subprocess', 'selenium', 'pyppeteer', 'splinter', 'os.system',
                                  'os.popen', 'chrome', 'connect')

BROKEN = object()  # 해석 실패 표지(두 쪽 셈에서 뺀다)


class Unresolved(Exception):
    """정적으로 풀 수 없는 하위 프로세스 인자."""


@dataclass
class Site:
    line: int
    kind: str  # 꼴
    target: str  # 대상
    js: Optional[str] = None  # 판정이 이 JS 파일(root 상대) 내용에 달린 자리


@dataclass
class Unit:
    """맨 위 함수 · 클래스 · 고정물 · 시험 하나."""
    name: str
    first: int
    last: int
    deco_lines: Set[int]
    sites: List[Site]
    calls: List[str]
    params: List[str]
    fixture: Optional[str] = None  # 고정물이면 그 이름
    test: bool = False
    cases: int = 1
    case_lines: Set[int] = field(default_factory=set)
    uncountable: List[int] = field(default_factory=list)

    @property
    def lines(self) -> Set[int]:
        return set(range(self.first, self.last + 1)) | self.deco_lines | self.case_lines


@dataclass
class PyModule:
    rel: str
    test_side: bool
    sites: List[Site]
    units: Dict[str, Unit]  # 정의 이름 → 함수 · 클래스 · 고정물
    fixtures: Dict[str, Unit]  # 고정물 이름 → 정의
    tests: List[Unit]
    imports: Dict[str, Tuple[str, int, Optional[str]]]  # 지역 이름 → (모듈 점 경로, 상대 점 수, 이름 | None=모듈)
    dynamic: List[int]  # 정적으로 못 푼 하위 프로세스 줄


# ---------------------------------------------------------------- 정적 값(TG4 전용 풀이 — TG2 의 _value 를 감싼다)


class _Fold(ast.NodeTransformer):
    """`X.with_name(<글자>)` · `X.with_suffix(<글자>)` 를 글자로 접는다(안쪽부터) — 나머지는 TG2 _value 가 푼다."""

    def __init__(self, env: Dict[str, str]) -> None:
        self.env = env

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr in ('with_name', 'with_suffix') and len(node.args) == 1
                and not node.keywords):
            base, arg = _value(func.value, self.env), _value(node.args[0], self.env)
            if isinstance(base, str) and isinstance(arg, str):
                try:
                    path = PurePosixPath(base)
                    folded = path.with_name(arg) if func.attr == 'with_name' else path.with_suffix(arg)
                except ValueError:
                    return node
                return ast.copy_location(ast.Constant(str(folded)), node)
        return node


def _static_value(node: Optional[ast.AST], env: Dict[str, str]) -> Optional[str]:
    if node is None:
        return None
    return _value(_Fold(env).visit(copy.deepcopy(node)), env)


def js_launches(source: str) -> List[Tuple[int, str]]:
    """JS 코드 토큰(주석 · 문자열 · 정규식 밖)의 띄움 토큰 `<owner> . <method> (` 자리 — (행, 토큰). 해석 실패는 ValueError."""
    toks = _js_tokens(source)
    found: List[Tuple[int, str]] = []
    for i in range(len(toks) - 3):
        if (toks[i][0] == 'word' and toks[i][1] in JS_OWNERS and toks[i + 1][1] == '.'
                and toks[i + 2][0] == 'word' and toks[i + 2][1] in JS_METHODS and toks[i + 3][1] == '('):
            found.append((toks[i][2] + 1, '%s.%s(' % (toks[i][1], toks[i + 2][1])))
    return found


def _project_rel(word: str, root: Path) -> Optional[str]:
    """정적 경로 글자 → 프로젝트 안 root 상대 경로(밖이면 None)."""
    if word.startswith('~'):
        return None
    path = PurePosixPath(word)
    if path.is_absolute():
        try:
            rel = PurePosixPath(posixpath.normpath(word)).relative_to(PurePosixPath(str(root)))
        except ValueError:
            return None
        return str(rel)
    norm = posixpath.normpath(word)
    return None if norm.startswith('..') else norm


def _is_fixture(node: ast.AST) -> Tuple[bool, Optional[str]]:
    """함수 장식에 pytest 고정물 표지가 있는가 → (고정물인가, name= 값)."""
    for deco in getattr(node, 'decorator_list', []):
        target = deco.func if isinstance(deco, ast.Call) else deco
        name = _call_name(target)
        if name == 'fixture' or name.endswith('.fixture'):
            alias = None
            if isinstance(deco, ast.Call):
                for kw in deco.keywords:
                    if kw.arg == 'name' and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                        alias = kw.value.value
            return True, alias
    return False, None


def _mark_args(deco: ast.AST, mark: str) -> Optional[ast.Call]:
    if isinstance(deco, ast.Call) and _call_name(deco.func).split('.')[-1] == mark and 'mark' in _call_name(deco.func):
        return deco
    return None


def _iter_len(node: ast.AST, consts: Dict[str, ast.AST], seen: Set[str]) -> Optional[int]:
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None if any(isinstance(e, ast.Starred) for e in node.elts) else len(node.elts)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return len(node.value)
    if isinstance(node, ast.Name) and node.id in consts and node.id not in seen:
        return _iter_len(consts[node.id], consts, seen | {node.id})
    if isinstance(node, ast.Call) and _call_name(node.func) == 'range' and 1 <= len(node.args) <= 3 and not node.keywords:
        values = [_int(a, consts, seen) for a in node.args]
        if all(v is not None for v in values):
            try:
                return len(range(*values))
            except (ValueError, OverflowError):
                return None
        return None
    return _length(node, consts, seen)


def _int(node: ast.AST, consts: Dict[str, ast.AST], seen: Set[str]) -> Optional[int]:
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _int(node.operand, consts, seen)
        return -v if v is not None else None
    if isinstance(node, ast.Name) and node.id in consts and node.id not in seen:
        return _int(consts[node.id], consts, seen | {node.id})
    return None


def _length(node: ast.AST, consts: Dict[str, ast.AST], seen: Set[str] = frozenset()) -> Optional[int]:
    """parametrize argvalues 의 경우 수 — 글자 목록 · 튜플 · 집합 · 모듈 상수 · 리터럴 반복이나 정수 range 위
    조건 없는 내포. 그 밖은 None."""
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None if any(isinstance(e, ast.Starred) for e in node.elts) else len(node.elts)
    if isinstance(node, ast.Name) and node.id in consts and node.id not in seen:
        return _length(consts[node.id], consts, seen | {node.id})
    if isinstance(node, ast.Call) and _call_name(node.func) in ('tuple', 'list') and len(node.args) == 1 and not node.keywords:
        return _length(node.args[0], consts, seen)
    if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
        total = 1
        for gen in node.generators:
            if gen.ifs or gen.is_async:
                return None
            n = _iter_len(gen.iter, consts, seen)
            if n is None:
                return None
            total *= n
        return total
    return None


# ---------------------------------------------------------------- 한 파이썬 모듈 읽기


def analyze_py(rel: str, source: str, root: Path, test_side: bool) -> PyModule:
    """한 파이썬 파일의 띄움 자리 · 정의 · 시험 · import. 구문 오류는 SyntaxError 그대로."""
    tree = ast.parse(source)
    aliases: Dict[str, str] = {}  # 지역 이름 → 표준 점 이름(import 별칭)
    imports: Dict[str, Tuple[str, int, Optional[str]]] = {}
    sites: List[Site] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split('.')[0] in E2E_MODULES:
                    sites.append(Site(node.lineno, '외부 E2E 러너', a.name.split('.')[0]))
                local = a.asname or a.name.split('.')[0]
                aliases[local] = a.name if a.asname else a.name.split('.')[0]
                imports[local] = (a.name if a.asname else a.name.split('.')[0], 0, None)
                if not a.asname:
                    imports[a.name] = (a.name, 0, None)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            if node.level == 0 and mod.split('.')[0] in E2E_MODULES:
                sites.append(Site(node.lineno, '외부 E2E 러너', mod.split('.')[0]))
            for a in node.names:
                if a.name == '*':
                    continue
                local = a.asname or a.name
                if node.level == 0 and mod:
                    aliases[local] = mod + '.' + a.name
                imports[local] = (mod, node.level, a.name)
    consts: Dict[str, ast.AST] = {}
    env: Dict[str, str] = {'__file__': str(root / rel)}
    owners: Set[str] = set()
    for st in tree.body:
        _bind(st, env, consts, owners)

    def canon(name: str) -> str:
        head, _, tail = name.partition('.')
        full = aliases.get(head)
        return (full + ('.' + tail if tail else '')) if full else name

    dynamic: List[int] = []

    def classify(call: ast.Call, scope_env: Dict[str, str], params: Set[str], scope_owners: Set[str]) -> Optional[Site]:
        func = call.func
        raw = _call_name(func)
        name = canon(raw)
        if isinstance(func, ast.Attribute) and func.attr in LAUNCH_METHODS:
            owner = func.value
            end = owner.attr if isinstance(owner, ast.Attribute) else owner.id if isinstance(owner, ast.Name) else None
            if end in LAUNCH_OWNERS or (isinstance(owner, ast.Name) and owner.id in scope_owners):
                return Site(call.lineno, '직접 띄우기', '%s.%s' % (end, func.attr))
        if name.split('.')[-1] in PLAYWRIGHT_STARTERS:
            return Site(call.lineno, '직접 띄우기', name.split('.')[-1] + '()')
        if isinstance(func, ast.Name) and func.id == 'launch_browser' and 'launch_browser' in params:
            return Site(call.lineno, '직접 띄우기', 'launch_browser()')
        if name in _PROCESS:
            try:
                words = _words(call, name, scope_env)
                return _classify_words(call.lineno, words, root)
            except Unresolved:
                dynamic.append(call.lineno)
        return None

    def walk(node: ast.AST, scope_env: Dict[str, str], params: Set[str], scope_owners: Set[str]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                args = child.args
                names = {a.arg for a in args.posonlyargs + args.args + args.kwonlyargs}
                names |= {a.arg for a in (args.vararg, args.kwarg) if a is not None}
                local_env = {k: v for k, v in scope_env.items() if k not in names}
                local_owners = set(scope_owners) - names
                if not isinstance(child, ast.Lambda):
                    for st in sorted((n for n in ast.walk(child) if isinstance(n, (ast.Assign, ast.AnnAssign))
                                      and n is not child), key=lambda n: (n.lineno, n.col_offset)):
                        _bind(st, local_env, None, local_owners)
                walk(child, local_env, params | names, local_owners)
                continue
            if isinstance(child, ast.Call):
                site = classify(child, scope_env, params, scope_owners)
                if site is not None:
                    sites.append(site)
            walk(child, scope_env, params, scope_owners)

    walk(tree, env, set(), owners)
    # (사) 브라우저 단위 고정물 정의 · 덮기
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fixture, alias = _is_fixture(node)
            if fixture and (alias or node.name) in BROWSER_SCOPE_FIXTURES:
                sites.append(Site(node.lineno, '브라우저 단위 고정물 정의', alias or node.name))

    units: Dict[str, Unit] = {}
    fixtures: Dict[str, Unit] = {}
    tests: List[Unit] = []

    def span(node: ast.AST) -> Tuple[int, int]:
        return node.lineno, node.end_lineno or node.lineno

    def calls_in(node: ast.AST) -> List[str]:
        return [_call_name(n.func) for n in ast.walk(node) if isinstance(n, ast.Call) and _call_name(n.func)]

    def make(node: ast.AST, name: str, qual: str) -> Unit:
        first, last = span(node)
        deco_lines = {d.lineno for d in getattr(node, 'decorator_list', [])}
        own = [s for s in sites if first <= s.line <= last or s.line in deco_lines]
        args = node.args if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
        params = [a.arg for a in (args.posonlyargs + args.args + args.kwonlyargs)] if args else []
        params = [p for p in params if p not in ('self', 'cls')]
        fixture, alias = _is_fixture(node)
        unit = Unit(qual, first, last, deco_lines, own, calls_in(node), params, (alias or name) if fixture else None)
        return unit

    def test_unit(node: ast.AST, qual: str, class_marks: List[ast.AST]) -> Unit:
        unit = make(node, node.name, qual)
        unit.test = True
        argnames: Set[str] = set()
        fixtures_used: List[str] = []
        for deco in list(node.decorator_list) + class_marks:
            call = _mark_args(deco, 'parametrize')
            if call is not None:
                names_node = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == 'argnames'), None)
                if isinstance(names_node, ast.Constant) and isinstance(names_node.value, str):
                    argnames |= {n.strip() for n in names_node.value.split(',') if n.strip()}
                elif isinstance(names_node, (ast.List, ast.Tuple)):
                    argnames |= {e.value for e in names_node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
                values = call.args[1] if len(call.args) > 1 else next((k.value for k in call.keywords if k.arg == 'argvalues'), None)
                n = _length(values, consts) if values is not None else None
                if deco in node.decorator_list:
                    unit.case_lines.add(deco.lineno)
                    for name_node in ast.walk(values) if values is not None else []:
                        if isinstance(name_node, ast.Name) and name_node.id in consts:
                            target = consts[name_node.id]
                            unit.case_lines |= set(range(target.lineno, (target.end_lineno or target.lineno) + 1))
                if n is None:
                    unit.uncountable.append(deco.lineno)
                else:
                    unit.cases *= n
            used = _mark_args(deco, 'usefixtures')
            if used is not None:
                fixtures_used += [a.value for a in used.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        unit.params = [p for p in unit.params if p not in argnames] + fixtures_used
        return unit

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_fixture(node)[0] and node.name.startswith('test'):
                tests.append(test_unit(node, node.name, []))
                continue
            unit = make(node, node.name, node.name)
            units[node.name] = unit
            if unit.fixture:
                fixtures[unit.fixture] = unit
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith('Test'):
                marks = list(node.decorator_list)
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if _is_fixture(item)[0]:
                            unit = make(item, item.name, item.name)
                            fixtures.setdefault(unit.fixture, unit)
                            units.setdefault(item.name, unit)
                        elif item.name.startswith('test'):
                            tests.append(test_unit(item, '%s::%s' % (node.name, item.name), marks))
            else:
                units[node.name] = make(node, node.name, node.name)
    return PyModule(rel, test_side, sites, units, fixtures, tests, imports, sorted(set(dynamic)))


def _bind(st: ast.AST, env: Dict[str, str], consts: Optional[Dict[str, ast.AST]], owners: Set[str]) -> None:
    """대입 하나를 정적 값 환경에 반영한다(흐름 무시 · 마지막 대입이 이긴다)."""
    if isinstance(st, ast.Assign):
        targets, value = st.targets, st.value
    elif isinstance(st, ast.AnnAssign) and st.value is not None:
        targets, value = [st.target], st.value
    else:
        return
    for target in targets:
        if isinstance(target, ast.Name):
            if consts is not None:
                consts[target.id] = value
            v = _static_value(value, env)
            if v is None:
                env.pop(target.id, None)
            else:
                env[target.id] = v
            end = (value.attr if isinstance(value, ast.Attribute) else value.id if isinstance(value, ast.Name) else None)
            if end in LAUNCH_OWNERS or end in owners:
                owners.add(target.id)
            else:
                owners.discard(target.id)
        else:
            for n in ast.walk(target):
                if isinstance(n, ast.Name):
                    env.pop(n.id, None)
                    owners.discard(n.id)


def _words(call: ast.Call, name: str, env: Dict[str, str]) -> List[Optional[str]]:
    """하위 프로세스 호출의 정적 낱말 목록(풀리지 않은 낱말은 None). 명령 자체를 못 풀면 Unresolved."""
    if name in _SHELL_STRING:
        value = _static_value(call.args[0], env) if call.args else None
        if value is None:
            raise Unresolved()
        try:
            return list(shlex.split(value))
        except ValueError:
            raise Unresolved()
    if name == 'asyncio.create_subprocess_exec':
        if any(isinstance(a, ast.Starred) for a in call.args):
            raise Unresolved()
        return [_static_value(a, env) for a in call.args]
    command = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == 'args'), None)
    shell = any(k.arg == 'shell' and isinstance(k.value, ast.Constant) and k.value.value is True for k in call.keywords)
    if command is None:
        raise Unresolved()
    if isinstance(command, (ast.List, ast.Tuple)):
        return [None if isinstance(e, ast.Starred) else _static_value(e, env) for e in command.elts]
    value = _static_value(command, env)
    if value is None:
        raise Unresolved()
    if shell:
        try:
            return list(shlex.split(value))
        except ValueError:
            raise Unresolved()
    return [value]


def _classify_words(line: int, words: List[Optional[str]], root: Path) -> Optional[Site]:
    rest = words[1:]
    for i, word in enumerate(rest):
        if word in _EVAL_FLAGS:
            code = rest[i + 1] if i + 1 < len(rest) else None
            if code is None:
                raise Unresolved()
            try:
                if js_launches(code):
                    return Site(line, '하위 프로세스 띄우기', '%s 코드' % word)
            except (ValueError, RecursionError):
                raise Unresolved()
    first = words[0]
    if isinstance(first, str) and PurePosixPath(first).name in BROWSER_EXES and any(
            w is None or w not in ('--version', '--help') for w in rest):
        return Site(line, '브라우저 실행 파일', PurePosixPath(first).name)
    flags = [w for w in words if isinstance(w, str) and any(w == f or w.startswith(f + '=') for f in BROWSER_ONLY_FLAGS)]
    if flags and any(isinstance(w, str) and (w == '--headless' or w.startswith('--headless=')) for w in words):
        return Site(line, '브라우저 실행 파일', ' '.join(['--headless'] + flags))
    for i, word in enumerate(words[:-1]):
        if isinstance(word, str) and PurePosixPath(word).name == 'playwright' and words[i + 1] in CLI_VERBS:
            return Site(line, '하위 프로세스 띄우기', 'playwright %s' % words[i + 1])
    for word in words:
        if isinstance(word, str) and PurePosixPath(word).suffix.lower() in JS_EXTS:
            rel = _project_rel(word, root)
            if rel is not None:
                return Site(line, '하위 프로세스 띄우기', rel, js=rel)
    if any(w is None for w in rest):
        raise Unresolved()
    return None


# ---------------------------------------------------------------- 쪽(기준판 · 현재판)


class Side:
    """한 쪽의 파일 읽기 · 모듈 해석 · 띄움 판정(쪽마다 따로 · 결과를 기억한다)."""

    def __init__(self, root: Path, read: Callable[[str], Optional[str]], test_side: Callable[[str], bool],
                 broken: Dict[str, str]) -> None:
        self.root = root
        self.read = read
        self.test_side = test_side
        self.broken = broken  # 두 쪽이 함께 쓰는 해석 실패 목록(경로 → 사유)
        self._modules: Dict[str, object] = {}
        self._js: Dict[str, object] = {}
        self._launching: Dict[Tuple[str, str], bool] = {}
        self._busy: Set[Tuple[str, str]] = set()
        self._cut = False  # 이번 셈이 순환(셈 중인 정의)에 걸렸는가

    def module(self, rel: str) -> Optional[PyModule]:
        if rel in self.broken:
            return None
        if rel not in self._modules:
            text = self.read(rel)
            result: object = None
            if text is not None:
                test_side = self.test_side(rel)
                if not test_side and not any(h in text for h in _LAUNCH_HINTS):
                    result = PyModule(rel, False, [], {}, {}, [], {}, [])
                else:
                    try:
                        result = analyze_py(rel, text, self.root, test_side)
                    except (SyntaxError, ValueError, RecursionError) as error:
                        self.broken[rel] = '파이썬 구문 해석 실패(%s)' % type(error).__name__
                        result = BROKEN
            self._modules[rel] = result
        got = self._modules[rel]
        return got if isinstance(got, PyModule) and rel not in self.broken else None

    def js_sites(self, rel: str) -> Optional[List[Tuple[int, str]]]:
        """JS 파일의 띄움 토큰 자리(없는 파일 · 해석 실패면 None)."""
        if rel in self.broken:
            return None
        if rel not in self._js:
            text = self.read(rel)
            value: object = None
            if text is not None:
                try:
                    value = js_launches(text)
                except (ValueError, RecursionError) as error:
                    self.broken[rel] = 'JS 토큰 해석 실패(%s)' % error
                    value = BROKEN
            self._js[rel] = value
        got = self._js[rel]
        return got if isinstance(got, list) and rel not in self.broken else None

    def active(self, site: Site) -> bool:
        return site.js is None or bool(self.js_sites(site.js))

    # ---- 이름 풀이

    def _module_file(self, origin: str, dotted: str, level: int) -> Optional[str]:
        if not level and dotted.split('.')[0] in ('', 'web'):
            return None
        for candidate in module_candidates(dotted, origin, level):
            if self.read(candidate) is not None:
                return None if candidate.startswith('web/') or _recorded(candidate) else candidate
        return None

    def _import(self, mod: PyModule, local: str) -> Optional[Tuple[str, Optional[str]]]:
        """지역 이름 → (모듈 파일, 이름 | None=모듈 자체). 시험 쪽이 아닌 모듈의 import 는 따라가지 않는다."""
        if not mod.test_side or local not in mod.imports:
            return None
        dotted, level, name = mod.imports[local]
        if name is None:
            target = self._module_file(mod.rel, dotted, level)
            return (target, None) if target else None
        sub = self._module_file(mod.rel, (dotted + '.' + name) if dotted else name, level)
        if sub is not None:
            return sub, None
        target = self._module_file(mod.rel, dotted, level)
        return (target, name) if target else None

    def resolve_call(self, mod: PyModule, chain: str) -> Optional[Tuple[str, str]]:
        parts = chain.split('.')
        if parts[0] in mod.units and len(parts) <= 2:
            return mod.rel, parts[0]
        # `import a.b.c` 꼴의 점 사슬 — 가장 긴 앞부분부터(맨 앞 이름 `a` 가 패키지로 풀려도)
        for cut in range(len(parts) - 1, 1, -1):
            prefix = '.'.join(parts[:cut])
            if prefix in mod.imports:
                got = self._import(mod, prefix)
                if got is not None and got[1] is None and cut == len(parts) - 1:
                    return got[0], parts[-1]
        got = self._import(mod, parts[0])
        if got is None:
            return None
        target, name = got
        if name is not None:
            return target, name
        return (target, parts[1]) if len(parts) == 2 else None

    def resolve_fixture(self, mod: PyModule, param: str) -> Optional[Tuple[str, str]]:
        if param in PUBLIC_FIXTURES:
            return None
        if param in mod.fixtures:
            return mod.rel, mod.fixtures[param].name
        got = self._import(mod, param)
        if got is not None and got[1] is not None:
            other = self.module(got[0])
            if other is not None and got[1] in other.units:
                return got[0], got[1]
        folder = PurePosixPath(mod.rel).parent
        while True:
            conftest = str(folder / 'conftest.py') if str(folder) != '.' else 'conftest.py'
            if conftest != mod.rel:
                found = self.module(conftest)
                if found is not None:
                    if param in found.fixtures:
                        return conftest, found.fixtures[param].name
                    got = self._import(found, param)
                    if got is not None and got[1] is not None:
                        other = self.module(got[0])
                        if other is not None and got[1] in other.units:
                            return got[0], got[1]
            if str(folder) in ('.', ''):
                return None
            folder = folder.parent

    def launching(self, rel: str, name: str) -> bool:
        key = (rel, name)
        if key in self._launching:
            return self._launching[key]
        if key in self._busy:
            self._cut = True
            return False
        mod = self.module(rel)
        unit = mod.units.get(name) if mod is not None else None
        if unit is None:
            return False
        self._busy.add(key)
        outer, self._cut = self._cut, False
        try:
            result = self.reach(mod, unit) is not None
        finally:
            self._busy.discard(key)
        cut, self._cut = self._cut, outer or self._cut
        if result or not cut or not self._busy:  # 순환 도중의 «아님» 은 기억하지 않는다(맨 바깥 셈은 끝까지 본 값)
            self._launching[key] = result
        return result

    def reach(self, mod: PyModule, unit: Unit) -> Optional[Tuple[str, str]]:
        """정의 · 시험이 띄움에 닿는가 → (꼴, 대상) | None."""
        for site in unit.sites:
            if self.active(site):
                return site.kind, site.target
        for chain in unit.calls:
            target = self.resolve_call(mod, chain)
            if target is not None and target != (mod.rel, unit.name) and self.launching(*target):
                return '띄우는 고정물 · 도우미 받기 · 부르기', chain
        if unit.fixture is not None or unit.test:
            for param in unit.params:
                target = self.resolve_fixture(mod, param)
                if target is not None and self.launching(*target):
                    return '띄우는 고정물 · 도우미 받기 · 부르기', param
        return None


@dataclass
class Place:
    """발견 줄 후보 — 띄움 자리 하나 또는 닿는 시험 하나."""
    lines: Set[int]  # 이 자리가 새것인지 보는 줄(시험이면 장식 · def · 몸 · 경우 수 상수 줄)
    anchor: int
    kind: str
    target: str
    test: Optional[str] = None  # 닿는 시험이면 그 이름
    own: Set[int] = field(default_factory=set)  # 발견 줄로 먼저 고르는 줄(시험이면 장식 · def · 몸)


@dataclass
class Count:
    sites: int = 0
    cases: int = 0
    places: List[Place] = field(default_factory=list)
    tests: Dict[str, Tuple[int, Set[int]]] = field(default_factory=dict)  # 닿는 시험 → (경우 수, 경우 수 줄)


def _count(side: Side, rel: str) -> Optional[Count]:
    """바뀐 시험 쪽 파일 하나의 두 수(그 쪽에 없거나 해석 실패면 None)."""
    if PurePosixPath(rel).suffix.lower() in JS_EXTS:
        found = side.js_sites(rel)
        if found is None:
            return None
        return Count(sites=len(found), places=[Place({line}, line, 'JS 러너 띄우기', token, own={line}) for line, token in found])
    mod = side.module(rel)
    if mod is None:
        return None
    count = Count()
    for site in mod.sites:
        if side.active(site):
            count.sites += 1
            count.places.append(Place({site.line}, site.line, site.kind, site.target, own={site.line}))
    for unit in mod.tests:
        why = side.reach(mod, unit)
        if why is None:
            continue
        count.cases += unit.cases
        count.tests[unit.name] = (unit.cases, set(unit.case_lines))
        if not any(unit.first <= s.line <= unit.last and side.active(s) for s in unit.sites):
            own = set(range(unit.first, unit.last + 1)) | unit.deco_lines
            count.places.append(Place(unit.lines, min(unit.deco_lines | {unit.first}), why[0], why[1], unit.name, own))
    return count


# ---------------------------------------------------------------- 기준판(승인 병합 흡수)


class _Bases:
    """파일마다 기준판 — 기준..HEAD 첫 부모 사슬에서 그 파일을 상류판 그대로 들인 마지막 승인 병합(없으면 기준점)."""

    def __init__(self, ctx: BackstopContext, got: Collected, design_build: Optional[str]) -> None:
        from .check_vendor import _find_build
        from .debt import DebtError
        from .subst import _approved_merges, _chain, _git, _names, _tree

        self.root = ctx.root
        self.base = got.base
        self.old_source = got.old_source  # 기준점 쪽 읽기는 TG2 와 같은 캐시
        self._git, self._tree = _git, _tree
        repo = Path(_git(ctx.root, ['rev-parse', '--show-toplevel']).decode('utf-8', 'surrogateescape').removesuffix('\n'))
        head = _git(ctx.root, ['rev-parse', '--verify', 'HEAD^{commit}']).decode().strip()
        self.verbatim: Dict[str, str] = {}  # root 상대 경로 → 그 경로를 그대로 들인 마지막 승인 병합
        chain = _chain(repo, self.base, head)
        merges = [(sha, parents) for sha, parents in chain if len(parents) == 2]
        if merges:
            try:
                approved, _notes = _approved_merges(repo, _find_build(ctx, design_build), self.base, chain)
            except DebtError:
                # 승인 목록을 못 읽으면(형식 · 사슬 밖 · 얕은 이력) 기준점 판으로 센다 — 승인 유입 판정 불가 알림이
                # «모든 지적을 이 레인 몫으로 센다»를 이미 낸다(TG4 를 끄지 않는다)
                approved = {}
            for sha, parents in merges:
                if sha in approved:
                    for path in _names(self.root, parents[0], sha, ['.']) - _names(self.root, parents[1], sha, ['.']):
                        self.verbatim[path] = sha
        self._trees: Dict[str, Dict[str, Tuple[str, str]]] = {}
        self._texts: Dict[str, Optional[str]] = {}

    def _entry(self, rel: str) -> Tuple[str, Optional[Tuple[str, str]]]:
        sha = self.verbatim.get(rel, self.base)
        if sha not in self._trees:
            self._trees[sha] = self._tree(self.root, sha)
        return sha, self._trees[sha].get(rel)

    def oid(self, rel: str) -> Optional[str]:
        """기준판 blob id(없으면 None)."""
        return (self._entry(rel)[1] or (None, None))[1]

    def read(self, rel: str) -> Optional[str]:
        if rel not in self._texts:
            sha, entry = self._entry(rel)
            if entry is None:
                self._texts[rel] = None
            elif sha == self.base:
                self._texts[rel] = self.old_source(rel)
            else:
                self._texts[rel] = self._git(self.root, ['show', '%s:./%s' % (sha, rel)]).decode('utf-8', 'surrogateescape')
        return self._texts[rel]


# ---------------------------------------------------------------- 검사


def run_browser(ctx: BackstopContext, design_build: Optional[str]) -> List[Finding]:
    if not ctx.can_detect_new_units:
        ctx.notices.append('[info] TG4 미실행 — git 기준점 없음 · 변경 시험 범위 미확정')
        return []
    try:
        got = _collect(ctx)
    except Exception as error:  # noqa: BLE001 — 수집 실패는 TG2·TG3 와 같이 미실행 고지
        ctx.notices.append('[info] TG4 미실행 — 기준점·설정·대응 해석 실패 · 변경 시험 범위 미확정: %s' % error)
        return []

    def test_side(rel: str) -> bool:
        return got.candidate(rel) if rel.endswith('.py') else js_in_test_tree(rel)

    files = sorted(p for p in got.changed | got.removed if test_side(p))
    if not files:
        return []
    try:
        bases = _Bases(ctx, got, design_build)
    except Exception as error:  # noqa: BLE001 — 승인 병합 판정 불가(목록 형식 · 얕은 이력 · git 실패)
        ctx.notices.append('[info] TG4 미실행 — 승인 병합 판정 불가: %s · 변경 시험 범위 미확정' % error)
        return []
    texts: Dict[str, Optional[str]] = {}

    def current(rel: str) -> Optional[str]:
        if rel not in texts:
            path = ctx.root / rel
            try:
                texts[rel] = path.read_bytes().decode('utf-8', 'surrogateescape') if path.is_file() else None
            except OSError:
                texts[rel] = None
        return texts[rel]

    def same(rel: str) -> bool:
        oid, text = bases.oid(rel), current(rel)
        if oid is None or text is None:
            return oid is None and text is None
        return git_blob_id(text.encode('utf-8', 'surrogateescape'), len(oid)) == oid

    # 기준판과 현재판 바이트가 같은 파일은 읽지 않는다(그 파일의 합 차 0 — 승인 병합이 들인 그대로 · blob id 로 견준다)
    files = [p for p in files if not same(p)]
    if not files:
        return []
    broken: Dict[str, str] = {}
    counts: Dict[str, Dict[str, Optional[Count]]] = {}
    sides: Dict[str, Side] = {}
    for _round in range(8):  # 해석 실패가 새로 나오면 두 쪽을 다시 센다(한 쪽만 빼지 않는다)
        known = dict(broken)
        sides = {'base': Side(ctx.root, bases.read, test_side, broken), 'cur': Side(ctx.root, current, test_side, broken)}
        counts = {name: {rel: _count(side, rel) for rel in files} for name, side in sides.items()}
        if broken == known:
            break
    for rel, why in sorted(broken.items()):
        ctx.notices.append('[info] TG4 일부 흐름 자동 판정 밖 — %s 기준판/현재판 %s · 그 파일은 두 쪽 셈에서 뺀다 · '
                           'discipline 감수 대상' % (rel, why))
    # 이름 바꿈 짝의 한쪽이 해석 실패면 다른 쪽도 뺀다(한 쪽만 빼면 거짓 늘어남)
    gone = (set(broken) | {new for new, old in got.pairs.items() if old in broken}
            | {old for new, old in got.pairs.items() if new in broken})
    files = [p for p in files if p not in gone]

    def total(side: str, kind: str) -> int:
        return sum(getattr(c, kind) for c in (counts[side][p] for p in files) if c is not None)

    d_sites = total('cur', 'sites') - total('base', 'sites')
    d_cases = total('cur', 'cases') - total('base', 'cases')

    def origin(rel: str) -> str:
        return got.pairs.get(rel, rel)

    # 새쪽 추가 줄 · 알림 — 현재판 파일마다 자기 기준판(이름을 바꾼 파일은 옛 이름의 기준판)과 견준다
    added: Dict[str, Set[int]] = {rel: _line_delta(bases.read(origin(rel)) or '', current(rel) or '')[0]
                                  for rel in files if counts['cur'][rel] is not None}
    side_cur = sides['cur']  # 해석 실패가 굳은 뒤의 현재판(모듈 캐시를 그대로 쓴다)
    for rel in files:
        mod = side_cur.module(rel) if rel.endswith('.py') and rel in added else None
        if mod is None:
            continue
        sited = {s.line for s in mod.sites}
        for line in mod.dynamic:
            if line in added[rel] and line not in sited:
                ctx.notices.append('[info] TG4 일부 흐름 자동 판정 밖 — %s:%d · 하위 프로세스 인자 동적 · discipline 감수 대상'
                                   % (rel, line))
        reaching = counts['cur'][rel].tests
        for unit in mod.tests:
            for line in unit.uncountable if unit.name in reaching else []:
                if line in added[rel]:
                    ctx.notices.append('[info] TG4 매개변수 경우 판정 밖 — %s:%d' % (rel, line))
    if d_sites <= 0 and d_cases <= 0:
        return []

    def delta(rel: str) -> Tuple[int, int]:
        now, was = counts['cur'].get(rel), counts['base'].get(origin(rel))
        return ((now.sites if now else 0) - (was.sites if was else 0),
                (now.cases if now else 0) - (was.cases if was else 0))

    def places(rel: str) -> List[Place]:
        count, was = counts['cur'][rel], counts['base'].get(origin(rel))
        out: List[Place] = []
        widened: Set[str] = set()
        for test, (cases, lines) in count.tests.items():
            before = was.tests.get(test) if was else None
            if before is not None and cases > before[0] and lines:
                out.append(Place(lines, min(lines), '띄우는 시험의 매개변수 경우 %+d' % (cases - before[0]), test, test, set(lines)))
                widened.add(test)
        return out + [p for p in count.places if p.test not in widened]

    grown = [p for p in files if counts['cur'].get(p) is not None
             and ((d_sites > 0 and delta(p)[0] > 0) or (d_cases > 0 and delta(p)[1] > 0))]
    if not grown:  # 옮김으로 합이 는 경우 — 새쪽 추가 줄에 자리 · 닿는 시험이 있는 파일
        grown = [p for p in files if counts['cur'].get(p) is not None
                 and any(place.lines & added.get(p, set()) for place in places(p))]
    tail = ' · 이번 실행이 늘린 띄움 자리 %+d · 띄우는 시험 경우 %+d (바뀐 시험 쪽 파일 %d 합)' % (d_sites, d_cases, len(files))
    head = '브라우저 시험이 공용 pytest-playwright 고정물 밖에서 브라우저를 띄운다'
    if not grown:
        first = next((p for p in files if counts['cur'].get(p) is not None), files[0])
        return [Finding('TG4', first, None, head + tail, _RULE, _FIX, root_rel=True)]
    out: List[Finding] = []
    for rel in grown:
        new = added.get(rel, set())
        fresh = sorted(((min(place.own & new or place.lines & new), place) for place in places(rel)
                        if place.lines & new), key=lambda item: item[0])
        chosen = fresh or sorted(((place.anchor, place) for place in places(rel)), key=lambda item: item[0])
        if not chosen:
            out.append(Finding('TG4', rel, None, head + tail, _RULE, _FIX, root_rel=True))
            continue
        line, place = chosen[0]
        shape = ' — %s(%s)' % (place.kind, place.target) + (' 외 %d곳' % (len(chosen) - 1) if len(chosen) > 1 else '')
        out.append(Finding('TG4', rel, line, head + shape + tail, _RULE, _FIX, root_rel=True))
    return out
