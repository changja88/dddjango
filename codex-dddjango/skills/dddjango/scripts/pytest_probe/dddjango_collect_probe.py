"""dddjango 수집 · 증거 탐침 — pytest 플러그인 · 판정하지 않는 기록기.

`behavior_guard.py support --collect` · `suite` 가 동결한 시험 명령 argv 맨 뒤에 `-p dddjango_collect_probe` 를 붙이고
이 디렉터리를 `PYTHONPATH` 앞에 하나 더해 부른다. 프로세스마다 `$DDDJANGO_PROBE_OUT/<pid>.json` 을
`pytest_unconfigure`(trylast)에서 확정한다. 판정(지원 · suite green/red)은 `behavior_support.py` 몫이다.

담는 것:
  - 허용 메커니즘의 원본 상위 집합 — 시험 함수의 실행 원본 사슬(정확한 표준 타입만 · `__wrapped__` 전부 ·
    환경 층이 클로저로 쥔 함수 한 단) · 시험 클래스 MRO 와 몸체 루틴 · fixture 관리자의 모든 정의 · 모듈 · 패키지 xunit ·
    generate · 등록 플러그인과 훅 구현(이름 · 원본 · 갈래) · Django fixtures 폴더 · 실행 중 인스턴스 lifecycle 원본.
  - 정의 자리(이름) 밖 · 원본 못 찾음 · 허용 밖(항목 종류 · 일시 중단 가능한 본문 · 결과 증거 없음 · 감시 구간 재진입 ·
    Django 찾는 자리 변화 · 적재 메서드 재정의).
  - 양 — 수집 · 선택 항목 · 구조 키 · call 보고 · skip · 완료 · 실패 보고 수 · import 실패 skip · exitstatus ·
    `sys.flags.optimize` · 역할(단일 · 조정자 · 일꾼) · 준비된 일꾼 · 확정 표지 · 확정 뒤 등록.
결과 증거: `pytest_itemcollected` 때 결속한 가장 안쪽 코드 객체 하나에만 call 단계 동안 `sys.monitoring` 지역 사건
`PY_START` · `PY_RETURN` 을 켜, 감시 구간을 연 call 실행 맥락(스레드 — greenlet 이 적재돼 있으면 그 greenlet)의 시작 ·
정상 반환과 맥락 밖 사건을 센다. passed call 보고 때 꺼내 «시작 ≥ 1 · 정상 반환 = 시작 · 맥락 밖 0 · 재진입 없음»이
아니면 허용 밖으로 남긴다. 구간이 열린 채 call 단계 훅이 다시 불리면 재진입으로 남긴다.
"""
from __future__ import annotations

import _thread
import functools
import inspect
import json
import os
import sys
import sysconfig
import types
from pathlib import Path

import _pytest
import _pytest.unittest
import pytest


XUNIT_MODULE = ("setup_module", "teardown_module", "setUpModule", "tearDownModule", "setup_function", "teardown_function")
PACKAGE_XUNIT = ("setUpModule", "setup_module", "tearDownModule", "teardown_module")
DJANGO_LOAD = ("setUpClass", "_fixture_setup", "_pre_setup")
ALLOWED_ITEMS = {"_pytest.python.Function", "_pytest.unittest.TestCaseFunction"}
ALLOWED_SOURCELESS = {("__channelexec__", "WorkerInteractor")}
PYTEST_DIR = str(Path(_pytest.__file__).resolve().parent)
SITE_DIRS = sorted({str(Path(p).resolve()) for p in (sysconfig.get_paths()["purelib"], sysconfig.get_paths()["platlib"])})
STDLIB_DIRS = sorted({str(Path(p).resolve()) for p in (sysconfig.get_paths()["stdlib"], sysconfig.get_paths()["platstdlib"])})
SELF = str(Path(__file__).resolve())
LRU = type(functools.lru_cache(maxsize=None)(lambda: None))
MON = getattr(sys, "monitoring", None)
_S: dict = {"seen_cls": set(), "tool": None, "bound": {}, "watch": None, "owner": None, "starts": 0, "returns": 0, "foreign": 0,
            "proof": {}, "suspend": set(), "initial": [], "final": [], "files": set(), "unresolved": [], "bad": [], "calls": set(),
            "skips": set(), "passed": set(), "complete": set(), "workers_ready": set(), "allowed_sourceless": set(), "django": None,
            "hookimpls": {}, "finalized": False, "late": [], "exitstatus": None,
            "failed": 0, "import_skips": [], "packages": set(), "meta": {}, "anchor": [], "names": {}, "flags": {}, "reentry": False}


def _code_file(code) -> "str | None":
    f = code.co_filename                  # 파일이 아닌 코드(exec · "<string>")는 원본을 확정 못 함
    return str(Path(f).resolve()) if f and os.path.isfile(f) else None


def _chain_codes(obj) -> "list | None":
    """실제 호출 객체부터 __wrapped__ 사슬 전부의 실행 코드 객체(바깥 → 안쪽). 정확한 표준 타입만 · 확정 못 하면 None."""
    codes: list = []
    seen: set = set()
    cur = obj
    while cur is not None:
        if id(cur) in seen or len(seen) > 64:
            return None                                   # 고리 · 너무 깊음
        seen.add(id(cur))
        tp = type(cur)
        if tp is types.MethodType or tp is classmethod or tp is staticmethod:
            cur = cur.__func__
            continue
        if tp is functools.partial:
            cur = cur.func
            continue
        if tp is LRU:                                     # 표준 C 감싸개 — 실행 코드 = 표준 + __wrapped__
            cur = cur.__wrapped__
            continue
        if tp is not types.FunctionType:
            return None                                   # 하위 클래스 · 호출 가능한 인스턴스 · 내장 · C — 지원 밖
        if _code_file(cur.__code__) is None:
            return None
        codes.append(cur.__code__)
        cur = cur.__dict__.get("__wrapped__")
    return codes


def _held(fn) -> list:
    """환경 층(pytest · 표준 · 설치 패키지)의 함수가 클로저 셀에 쥔 함수 · 바운드 메서드의 코드(한 단 · Claude r11-1(a))."""
    out = []
    for cell in (fn.__closure__ or ()):
        try:
            v = cell.cell_contents
        except ValueError:
            continue
        if type(v) is types.MethodType:
            v = v.__func__
        if type(v) is types.FunctionType and _code_file(v.__code__) is not None:
            out.append(v.__code__)
    return out


def _chain(obj) -> "list[str] | None":
    """원본 상위 집합 = 사슬의 모든 층 + 환경 층이 클로저로 쥔 함수(한 단)."""
    codes = _chain_codes(obj)
    if codes is None:
        return None
    files = [_code_file(c) for c in codes]
    cur = obj
    for _ in range(64):                                   # 사슬을 다시 걸으며 환경 층의 클로저를 본다
        tp = type(cur)
        if tp is types.MethodType or tp is classmethod or tp is staticmethod:
            cur = cur.__func__
        elif tp is functools.partial:
            cur = cur.func
        elif tp is LRU:
            cur = cur.__wrapped__
        elif tp is types.FunctionType:
            if _env(_code_file(cur.__code__)):
                files += [_code_file(c) for c in _held(cur)]
            cur = cur.__dict__.get("__wrapped__")
        else:
            break
        if cur is None:
            break
    return files


def _need(obj, what: str, where: str) -> "list[str] | None":
    files = _chain(obj)
    if not files:
        _S["unresolved"].append([where, what])
        return None
    _S["files"].update(files)
    return files


def _class_file(c) -> "str | None":
    try:
        f = inspect.getsourcefile(c)
    except (TypeError, OSError):
        return None
    return str(Path(f).resolve()) if f else None


def _abs(rel: str) -> str:
    return str((Path(_S["config"].rootpath) / rel).resolve())


def _origin(f: str) -> str:
    if f == SELF:
        return "탐침"
    if f.startswith(PYTEST_DIR + os.sep):
        return "pytest"
    if any(f.startswith(d + os.sep) for d in SITE_DIRS):
        return "설치 패키지"          # 저장소 범위 밖인지는 지원 쪽이 범위 목록으로 다시 본다
    if any(f.startswith(d + os.sep) for d in STDLIB_DIRS):
        return "표준 라이브러리"
    return "그 밖"                    # 저장소 파일 또는 정체 불명 — 지원 쪽이 가른다


# ── 플러그인: 컨테이너 + 훅 구현 함수 전부(이름 · 원본 · 갈래) ──
def _plugin(name, plugin, manager) -> None:
    if plugin is None:
        return
    c = plugin if inspect.isclass(plugin) else type(plugin)
    if (c.__module__, c.__qualname__) in ALLOWED_SOURCELESS:
        _S["allowed_sourceless"].add(f"{c.__module__}.{c.__qualname__}")
        return
    f = getattr(plugin, "__file__", None) or _class_file(c)
    if f:
        f = str(Path(f).resolve())
        _S["files"].add(f)
    else:
        _S["unresolved"].append(["plugin", f"{name} {c.__module__}.{c.__qualname__}"])
    for caller in (manager.get_hookcallers(plugin) or []):
        for impl in caller.get_hookimpls():
            if impl.plugin is not plugin:
                continue
            g = _need(impl.function, f"훅 {caller.name}", f"plugin {name}")
            if g:
                _S["hookimpls"][f"{g[0]}::{caller.name}::{id(impl.function)}"] = {
                    "hook": caller.name, "files": g, "origins": [_origin(x) for x in g],
                    "container": f or None, "container_origin": _origin(f) if f else None}


def _write() -> None:
    out = os.environ.get("DDDJANGO_PROBE_OUT")
    if not out or "config" not in _S:
        return
    config = _S["config"]
    pm = config.pluginmanager
    role = "worker" if _S.get("workerid") else ("controller" if pm.has_plugin("dsession") else "single")
    data = {"role": role, "workerid": _S.get("workerid"), "rootpath": str(config.rootpath),
            "inipath": str(config.inipath) if config.inipath else None, "args": list(config.invocation_params.args),
            "exitstatus": _S["exitstatus"], "initial": _S["initial"], "final": _S["final"],
            "calls": sorted(_S["calls"]), "skips": sorted(_S["skips"]), "passed": sorted(_S["passed"]), "meta": _S["meta"],
            "complete": sorted(_S["complete"]), "files": sorted(_S["files"]), "unresolved": _S["unresolved"],
            "bad": _S["bad"], "hookimpls": sorted(_S["hookimpls"].values(), key=lambda h: (h["files"][0], h["hook"])),
            "allowed_sourceless": sorted(_S["allowed_sourceless"]), "workers_ready": sorted(_S["workers_ready"]),
            "finalized": _S["finalized"], "late": _S["late"], "failed": _S["failed"], "import_skips": _S["import_skips"],
            "anchor": _S["anchor"], "optimize": sys.flags.optimize, "flags": _S["flags"],
            "greenlet_loaded": "greenlet" in sys.modules}
    Path(out).mkdir(parents=True, exist_ok=True)
    Path(out, f"{os.getpid()}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8",
                                                errors="surrogateescape")   # OS 가 surrogateescape 로 넘긴 경로도 원래 바이트로


def pytest_plugin_registered(plugin, plugin_name, manager) -> None:
    _plugin(plugin_name, plugin, manager)
    if _S["finalized"]:
        _S["late"].append(str(plugin_name))
        _write()                      # 확정 뒤 등록 — 기록을 다시 써서 정지 사유로 남긴다


def pytest_configure(config) -> None:
    _S["config"] = config
    if _S["tool"] is None:
        _monitor_on()
    _S["workerid"] = getattr(config, "workerinput", {}).get("workerid")


def _meta(item) -> list:
    """구조 키 — [파일 절대 경로 · 클래스 qualname | None · 함수 originalname · 항목 이름(매개변수 id 포함)]."""
    cls = getattr(item, "cls", None)
    return [str(Path(item.path).resolve()), cls.__qualname__ if cls is not None else None,
            getattr(item, "originalname", None) or item.name, item.name]


def _routines(c) -> dict:
    return {k: v for k, v in vars(c).items() if inspect.isroutine(v) or isinstance(v, (classmethod, staticmethod))}


def _env(f: str) -> bool:
    return _origin(f) in ("pytest", "표준 라이브러리", "설치 패키지")


def _home(item) -> "tuple[str | None, str | None]":
    """정의 자리 — (정의 파일, 기대 qualname). 모듈 시험 = 수집 모듈 · 이름, 클래스 시험 = 그 이름을 가진 MRO 클래스."""
    cls = getattr(item, "cls", None)
    name = item.originalname
    if cls is None:
        return str(Path(item.path).resolve()), name
    owner = next((c for c in cls.__mro__ if name in vars(c)), None)
    if owner is None:
        return None, None
    return _class_file(owner), f"{owner.__qualname__}.{name}"


def pytest_itemcollected(item) -> None:
    """수집 때(modifyitems · fixture 앞) — 구조 키 · 원본 사슬 · 정의 자리(이름) · 결속 코드 · 일시 중단 가능 본문(v13)."""
    nid = item.nodeid
    _S["initial"].append(nid)
    _S["meta"][nid] = _meta(item)
    if not isinstance(item, pytest.Function):
        return
    obj = item.obj
    codes = _chain_codes(obj)
    if not codes:
        _S["unresolved"].append([nid, "시험 함수(지원 밖 호출 객체 타입 포함)"])
        return
    _need(obj, "시험 함수", nid)
    home, qual = _home(item)
    inner = codes[-1]
    if home is None or _code_file(inner) != home or inner.co_qualname != qual:
        _S["anchor"].append({"nid": nid, "home": home, "qual": qual, "inner": _code_file(inner), "inner_qual": inner.co_qualname})
    kinds = [n for n, f in (("generator", inspect.CO_GENERATOR), ("coroutine", inspect.CO_COROUTINE),
                            ("iterable coroutine", inspect.CO_ITERABLE_COROUTINE), ("async generator", inspect.CO_ASYNC_GENERATOR))
             if inner.co_flags & f]
    if kinds:                                         # v13 ①: 일시 중단 가능한 본문은 결과 증거로 증명하지 못한다
        _S["flags"][nid] = kinds
        _S["suspend"].add(nid)
        _S["bad"].append([nid, f"결과 증거 범위 밖 — 일시 중단 가능한 본문({' · '.join(kinds)})"])
        return
    _S["bound"][nid] = inner


def _fixture_superset(session) -> None:
    defs = getattr(getattr(session, "_fixturemanager", None), "_arg2fixturedefs", None)
    if not isinstance(defs, dict):
        _S["unresolved"].append(["fixture", "fixture 관리자 정의 목록 없음(_arg2fixturedefs)"])
        return
    for name, fds in defs.items():
        for fd in fds:
            _need(fd.func, f"fixture {name}", "fixture 관리자")


def _django_state():
    try:
        from django.apps import apps
        from django.conf import settings
        if not settings.configured or not apps.ready:
            return None
        return (tuple(str(d) for d in settings.FIXTURE_DIRS), tuple(sorted(a.path for a in apps.get_app_configs())))
    except Exception:
        return None


def _django_superset(state) -> None:
    if state is None:
        return
    fixture_dirs, app_paths = state
    for d in [Path(p) / "fixtures" for p in app_paths] + [Path(p) for p in fixture_dirs]:
        if d.is_dir():
            _S["files"].update(str(f.resolve()) for f in d.rglob("*") if f.is_file())


def _django_labels(cls, where: str) -> None:
    try:
        from django.test import TransactionTestCase
    except Exception:
        return
    if not (inspect.isclass(cls) and issubclass(cls, TransactionTestCase)):
        return
    for label in (getattr(cls, "fixtures", None) or []):
        if not isinstance(label, str) or os.path.isabs(label):
            _S["unresolved"].append([where, f"Django fixtures 이름 {label!r}(절대 경로 · 비문자열)"])
            continue
        sub, base = os.path.split(label)
        d = Path.cwd() / sub
        stem = base.split(".", 1)[0]
        if d.is_dir():
            _S["files"].update(str(f.resolve()) for f in d.iterdir() if f.is_file() and f.name.startswith(stem))


def pytest_collection_finish(session) -> None:
    _fixture_superset(session)
    _S["django"] = _django_state()
    _django_superset(_S["django"])
    for item in session.items:
        nid = item.nodeid
        _S["final"].append(nid)
        kind = f"{type(item).__module__}.{type(item).__qualname__}"
        if kind not in ALLOWED_ITEMS:
            _S["bad"].append([nid, f"허용 밖 항목 종류 {kind}"])
            continue
        _S["files"].update({str(Path(item.path).resolve()), _abs(item.location[0])})
        _S["meta"][nid] = _meta(item)
        mod = item.module
        for name in XUNIT_MODULE + ("pytest_generate_tests",):
            fn = getattr(mod, name, None)
            if fn is not None:
                _need(fn, f"{name}(모듈)", nid)
        cls = item.cls
        if cls is not None:
            for c in cls.__mro__:
                if c.__module__ == "builtins":
                    continue
                cf = _class_file(c)
                if cf is None:
                    _S["unresolved"].append([nid, f"클래스 {c.__qualname__}"])
                else:
                    _S["files"].add(cf)
                for attr, val in vars(c).items():
                    if inspect.isroutine(val) or isinstance(val, (classmethod, staticmethod)):
                        _need(val, f"{c.__qualname__}.{attr}", nid)
            _django_labels(cls, nid)
            _django_load_override(cls, nid)
        for node in item.listchain():
            if isinstance(node, pytest.Package):
                _S["packages"].add(str((Path(node.path) / "__init__.py").resolve()))


def _django_load_override(cls, where: str) -> None:
    """fixtures 를 가진 Django 시험 클래스의 저장소 쪽 MRO 가 적재 메서드를 재정의하면 정지(적재 동안만 바꾸는 꼴)."""
    try:
        from django.test import TransactionTestCase
    except Exception:
        return
    if not (inspect.isclass(cls) and issubclass(cls, TransactionTestCase)) or not getattr(cls, "fixtures", None):
        return
    for c in cls.__mro__:
        f = _class_file(c)
        if f is None or _origin(f) != "그 밖":
            continue
        hit = [n for n in DJANGO_LOAD if n in vars(c)]
        if hit:
            _S["bad"].append([where, f"Django fixtures 클래스가 적재 메서드 재정의 {hit}({c.__qualname__})"])


def _package_xunit() -> None:
    """항목 사슬의 Package 마다 __init__.py 의 setUpModule · setup_module · tearDownModule · teardown_module 원본."""
    import ast
    by_file = {}
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f:
            by_file[str(Path(f).resolve())] = m
    for init in sorted(_S["packages"]):
        m = by_file.get(init)
        if m is not None:
            for name in PACKAGE_XUNIT:
                fn = getattr(m, name, None)
                if fn is not None:
                    _need(fn, f"{name}(패키지)", init)
            continue
        try:
            tree = ast.parse(Path(init).read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            _S["unresolved"].append([init, "패키지 __init__ 읽기 실패"])
            continue
        names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        names |= {a.asname or a.name for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom)) for a in n.names}
        names |= {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
        if names & set(PACKAGE_XUNIT):
            _S["unresolved"].append([init, "패키지 __init__ 의 xunit 이름(모듈 미적재)"])


def _mro_names(tp) -> set:
    got = _S["names"].get(tp)
    if got is None:
        got = set()
        for c in tp.__mro__:
            if c is not object:
                got |= set(_routines(c))
        _S["names"][tp] = got
    return got


def _ctx():
    """call 실행 맥락 — 스레드 id 와(greenlet 이 적재돼 있으면) 그 스레드의 지금 greenlet."""
    g = sys.modules.get("greenlet")
    if g is None:
        return (_thread.get_ident(), None)
    try:
        return (_thread.get_ident(), id(g.getcurrent()))
    except Exception:
        return (_thread.get_ident(), "확인 못 함")       # 맥락을 못 가리면 다른 맥락으로 본다(정지 쪽)


def _same_ctx() -> bool:
    owner = _S["owner"]
    if owner is None or owner[1] == "확인 못 함":
        return False
    if owner[1] is None:                              # 구간을 열 때 greenlet 이 없었으면 그 앞에 만든 greenlet 도 없다
        return _thread.get_ident() == owner[0]
    return _ctx() == owner


def _on_start(code, offset):
    if code is _S["watch"]:
        if _same_ctx():
            _S["starts"] += 1
        else:
            _S["foreign"] += 1


def _on_return(code, offset, retval):
    if code is _S["watch"]:
        if _same_ctx():
            _S["returns"] += 1
        else:
            _S["foreign"] += 1


def _monitor_on() -> None:
    if MON is None:
        _S["unresolved"].append(["monitoring", "sys.monitoring 없음(Python 3.12 미만)"])
        return
    for tid in (3, 4, 5, 2):
        try:
            MON.use_tool_id(tid, "dddjango_collect_probe")
        except ValueError:
            continue
        _S["tool"] = tid
        MON.register_callback(tid, MON.events.PY_START, _on_start)
        MON.register_callback(tid, MON.events.PY_RETURN, _on_return)
        return
    _S["unresolved"].append(["monitoring", "sys.monitoring 빈 도구 자리 없음"])


def _inst_sources(item, nid) -> None:
    """(가) 실행 중 원본 상위 집합: 시험 인스턴스의 실제 클래스 MRO 몸체 루틴과, 인스턴스 __dict__ 에 붙은 MRO 이름 호출 객체의 원본.
    프레임워크가 이름으로 부르는 자리(unittest lifecycle · pytest xunit)에 붙은 함수의 파일을 M 에 넣는다(X1 · C2 · SAC)."""
    inst = getattr(item, "instance", None)
    if inst is None or not hasattr(inst, "__dict__"):
        return
    tp = type(inst)
    if tp is not getattr(item, "cls", None) and tp not in _S["seen_cls"]:   # 수집 때 본 클래스와 다를 때만(A4 꼴)
        _S["seen_cls"].add(tp)
        for c in tp.__mro__:
            if c is object:
                continue
            cf = _class_file(c)
            if cf is None:
                _S["unresolved"].append([nid, f"시험 인스턴스 클래스 {c.__qualname__}"])
                continue
            _S["files"].add(cf)
            for k, v in vars(c).items():
                if type(v) in (types.FunctionType, classmethod, staticmethod):
                    _need(v, f"{c.__qualname__}.{k}", nid)
    names = _mro_names(tp)
    for k, v in list(vars(inst).items()):
        if k not in names or not callable(v) or inspect.isclass(v):
            continue
        if _chain_codes(v) is None and _env(_class_file(type(v)) or ""):
            continue                                      # 환경 클래스의 호출 가능한 인스턴스(Mock 등) — 저장소 코드 없음
        _need(v, f"인스턴스 {k}", nid)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    """call 단계(탐침 tryfirst 래퍼): Django 찾는 자리 · 결속 코드의 시작 · 정상 반환 계수(call 실행 맥락만 · v13)."""
    nid = item.nodeid
    if _S["django"] is not None and _django_state() != _S["django"]:
        _S["bad"].append([nid, "Django FIXTURE_DIRS · 앱 목록이 수집 때와 다름"])
    cls = getattr(item, "cls", None)
    if cls is not None:
        _django_labels(cls, nid)
    if _S["watch"] is not None:                       # v13 ③: 구간이 열린 채 call 단계 훅이 다시 불림 — 셈을 건드리지 않고 정지
        _S["bad"].append([nid, "결과 증거 범위 밖 — 감시 구간 재진입(call 단계 훅이 call 단계 안에서 다시 불림)"])
        _S["reentry"] = True
        return (yield)
    code = _S["bound"].get(nid)
    tid = _S["tool"]
    if code is None or tid is None:
        _S["proof"][nid] = None
        return (yield)
    _inst_sources(item, nid)
    _S["watch"], _S["owner"], _S["starts"], _S["returns"], _S["foreign"] = code, _ctx(), 0, 0, 0
    _S["reentry"] = False
    MON.set_local_events(tid, code, MON.events.PY_START | MON.events.PY_RETURN)
    try:
        return (yield)
    finally:
        MON.set_local_events(tid, code, 0)
        _S["proof"][nid] = (_S["starts"], _S["returns"], _S["foreign"], _S["reentry"])
        _S["watch"], _S["owner"] = None, None
        _inst_sources(item, nid)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report) -> None:
    if report.failed:
        _S["failed"] += 1
    if report.skipped and isinstance(report.longrepr, tuple) and "could not import" in str(report.longrepr[-1]):
        _S["import_skips"].append(report.nodeid)
    if report.when == "call":
        (_S["skips"] if report.skipped else _S["calls"]).add(report.nodeid)
        if report.passed:
            _S["passed"].add(report.nodeid)              # passed call — 결과 증거 계수(passed 만)의 분모
        if report.passed and _S["tool"] is not None and not _S["config"].pluginmanager.has_plugin("dsession"):
            # 결과 증거는 시험을 실제로 돈 프로세스(단일 · 일꾼)에서 본다 — 조정자는 보고만 받는다
            pr = _S["proof"].pop(report.nodeid, None)    # v13 ④: 꺼내 쓴다 — 앞 구간의 셈을 다시 쓰지 못한다
            if report.nodeid in _S["suspend"]:
                pass                                      # 수집 때 이미 정지(일시 중단 가능한 본문)
            elif pr is None or pr[0] < 1 or pr[1] != pr[0] or pr[2] or pr[3]:
                s, r, f, _re = pr if pr else (0, 0, 0, False)
                _S["bad"].append([report.nodeid, f"passed 인데 결속한 시험 코드의 결과 증거 없음(시작 {s} · 정상 반환 {r} · 맥락 밖 사건 {f})"])
    elif report.when == "setup" and report.skipped:
        _S["skips"].add(report.nodeid)


def pytest_runtest_logfinish(nodeid, location) -> None:
    _S["complete"].add(nodeid)


@pytest.hookimpl(optionalhook=True)
def pytest_testnodeready(node) -> None:
    _S["workers_ready"].add(node.gateway.id)


def pytest_sessionfinish(session, exitstatus) -> None:
    _package_xunit()
    pm = session.config.pluginmanager
    for name, plugin in pm.list_name_plugin():
        _plugin(name, plugin, pm)
    _fixture_superset(session)
    if _S["django"] is not None and _django_state() != _S["django"]:
        _S["bad"].append(["session", "Django FIXTURE_DIRS · 앱 목록이 세션 끝에 다름"])
    _S["exitstatus"] = int(exitstatus)


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config) -> None:
    pm = config.pluginmanager
    for name, plugin in pm.list_name_plugin():
        _plugin(name, plugin, pm)
    _S["finalized"] = True
    _write()
