#!/usr/bin/env python3
"""지원 확인 · 증거 실행 — 리팩토링 모드의 `behavior_guard.py support <폴더> --collect`(G0) · `suite <폴더>`(G2) 본체.

동결한 시험 명령(pytest)마다 탐침(`pytest_probe/dddjango_collect_probe.py`)을 argv 맨 뒤에 붙여 돌리고, 탐침 기록 ·
저장소 파일 목록 · 실행 관찰 API 정적 규칙으로 판정한다(설계 정본: workspace/plan/2026-10-03-refactor-definition/design.md
§3-1 · §4-1 · §4-5 · 끝 정오 2 · 3).

  support <폴더> --collect  승인 전 지원 확인 — `<폴더>/behavior/support/<UTC>/test-commands.md` 의 시험 명령과 동결 변수
                            여섯을 `run-definition.json` 으로 동결하고 수집만 돌려 `g0-collect.json` 을 쓴다.
                            exit 0 지원 · 2 지원 안 함(G0 정지) · 1 실행 불능.
  suite <폴더>              G2 증거 실행 — G1 이 결속한 지원 기록의 실행 정의를 그대로 돌리고(첫 실패에서 멈춤)
                            `<폴더>/behavior/<실행>/suite-<UTC>.json` 을 쓴다. exit 0 green · 2 red · 1 실행 불능.

환경: 상속 환경 · 동결 변수 여섯은 동결값으로 덮음(없음이면 지움) · PYTHONDONTWRITEBYTECODE=1 · PYTHONPATH 앞에 탐침 디렉터리 ·
DDDJANGO_PROBE_OUT=<출력 자리>/<n>/. 명령마다 상한 — 수집 600초 · suite 3,600초(제품 고정 · 스위치 없음).
넘으면 그 명령이 띄운 프로세스 묶음만 끝낸다.
실행이 만든 미추적 파일은 지운다(`behavior_guard._migrations_dynamic` 과 같은 꼴).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import behavior_guard as bg  # noqa: E402

COMMAND_TIMEOUT_SECONDS: int = 600
SUITE_COMMAND_TIMEOUT_SECONDS: int = 3600
PROBE_NAME: str = "dddjango_collect_probe"
PROBE_DIR: Path = Path(__file__).resolve().parent / "pytest_probe"
PROBE_FILE: Path = PROBE_DIR / f"{PROBE_NAME}.py"
# 프로젝트 훅 구현 허용 목록(v10) — 이름마다 근거는 설계 §4-1 «프로젝트 훅 허용 목록»
ALLOWED_HOOKS = {"pytest_addoption", "pytest_configure", "pytest_sessionstart", "pytest_collection_modifyitems",
                 "pytest_generate_tests", "pytest_make_parametrize_id", "pytest_report_header", "pytest_report_teststatus"}
FROZEN = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTEST_DISABLE_PLUGIN_AUTOLOAD", "DJANGO_SETTINGS_MODULE", "DJANGO_CONFIGURATION",
          "PYTHONOPTIMIZE")   # v11: assert 를 지우는 실행의 환경 짝(동결) — 실제 값은 탐침의 sys.flags.optimize 로 관측
ENV_ORIGINS = ("탐침", "pytest", "표준 라이브러리", "설치 패키지")
SUPPORT_STAMP_RE: "re.Pattern[str]" = re.compile(r"^\d{8}T\d{6}Z$")
COMMAND_LINE_RE: "re.Pattern[str]" = re.compile(r"^시험 명령 (\d+): (.+)$")
SOURCE_LINE_RE: "re.Pattern[str]" = re.compile(r"^출처: (.+)$")
MENTION_SKIP_PREFIXES: "tuple[str, ...]" = (".dddjango-web/",)   # `.dddjango/` 는 bg._excluded 가 이미 뺀다
PROOF_MISSING: str = "passed 인데 결속한 시험 코드의 결과 증거 없음"
REENTRY: str = "결과 증거 범위 밖 — 감시 구간 재진입"
ROLES: "tuple[str, ...]" = ("single", "controller", "worker")
# 판정 · 계수에 쓰는 탐침 기록 칸과 형식 — 없거나 형식 밖이면 기본값으로 메우지 않고 «확인 못 함» 정지
PROBE_FIELDS: "dict[str, str]" = {
    "role": "role", "workerid": "workerid", "exitstatus": "int", "failed": "int", "optimize": "int",
    "finalized": "bool", "greenlet_loaded": "bool", "workers_ready": "strs", "initial": "strs", "final": "strs",
    "calls": "strs", "skips": "strs", "passed": "strs", "complete": "strs", "import_skips": "strs", "late": "strs",
    "files": "strs", "meta": "meta", "flags": "dict", "anchor": "anchor", "hookimpls": "hooks", "bad": "pairs",
    "unresolved": "pairs",
}
ANCHOR_KEYS: "tuple[str, ...]" = ("nid", "home", "qual", "inner", "inner_qual")


class SupportError(Exception):
    """실행 불능(exit 1) — 판정하지 않는다."""


# ── v15 실행 관찰 API 정적 규칙(허용 목록 · 근거는 설계 §4-1 «실행 관찰 API 규칙» · v14 의 D1 · D2 를 대체) ──
import ast as _ast  # noqa: E402

# 위험 모듈 — 관찰 콜백 설치 · 프레임 · 코드 객체 · 모듈 재취득에 쓰일 수 있다(닫힌 목록 · 범주 근거는 설계 표)
# 값 = 안정적 결속(별칭 없는 평이 import)을 통해 읽어도 관찰을 설치할 수 없는 속성(허용 읽기 · 현장 실측 + 자명 안전)
ALLOW = {
    "sys": {"argv", "path", "modules", "version", "version_info", "hexversion", "platform", "maxsize", "maxunicode",
            "executable", "prefix", "base_prefix", "exec_prefix", "base_exec_prefix", "byteorder", "flags",
            "float_info", "int_info", "implementation", "builtin_module_names", "stdlib_module_names",
            "stdout", "stderr", "stdin", "__stdout__", "__stderr__", "defaultencoding", "getdefaultencoding",
            "getfilesystemencoding", "getrecursionlimit", "setrecursionlimit", "getsizeof", "intern", "is_finalizing",
            "exc_info", "exception", "last_type", "last_value", "last_traceback", "dont_write_bytecode", "warnoptions",
            "api_version", "copyright", "ps1", "ps2", "displayhook", "excepthook", "exit", "audit", "orig_argv",
            "pycache_prefix", "tracebacklimit", "meta_path", "path_hooks", "path_importer_cache", "set_int_max_str_digits",
            "get_int_max_str_digits", "thread_info", "abiflags", "winver", "dllhandle"},
    "threading": {"Thread", "Event", "Lock", "RLock", "Condition", "Semaphore", "BoundedSemaphore", "Barrier",
                  "BrokenBarrierError", "Timer", "local", "current_thread", "currentThread", "main_thread", "get_ident",
                  "get_native_id", "active_count", "activeCount", "enumerate", "stack_size", "excepthook", "ThreadError",
                  "TIMEOUT_MAX"},
    "_thread": {"get_ident", "get_native_id", "allocate_lock", "LockType", "RLock", "TIMEOUT_MAX", "stack_size",
                "error", "interrupt_main"},
    "importlib": {"import_module", "reload", "util", "metadata", "resources", "machinery", "abc", "invalidate_caches",
                  "__import__"},
    "types": {"SimpleNamespace", "ModuleType", "MappingProxyType", "TracebackType", "GenericAlias", "UnionType",
              "NoneType", "NotImplementedType", "EllipsisType", "new_class", "prepare_class", "resolve_bases",
              "DynamicClassAttribute", "MethodType", "GetSetDescriptorType", "MemberDescriptorType", "BuiltinFunctionType",
              "BuiltinMethodType", "WrapperDescriptorType", "MethodWrapperType", "ClassMethodDescriptorType",
              "MethodDescriptorType"},   # v15.2-pre: LambdaType 뺌(= FunctionType · r15b-6)
    "gc": {"collect", "disable", "enable", "isenabled", "freeze", "unfreeze", "get_count", "set_threshold",
           "get_threshold", "get_stats", "set_debug", "get_debug", "callbacks", "garbage", "DEBUG_LEAK", "DEBUG_STATS",
           "DEBUG_COLLECTABLE", "DEBUG_UNCOLLECTABLE", "DEBUG_SAVEALL", "is_tracked", "is_finalized", "freeze"},
    "builtins": set(),   # 현장 0 — 어떤 읽기든 정지(eval · exec · getattr · breakpoint · __import__ 재취득)
}
# inspect 는 안전면이 넓고 위험은 프레임 접근뿐 — 거부 집합으로 적는다(결속이 안 새므로 그 자리만 보면 충분)
INSPECT_DENY = {"currentframe", "stack", "trace", "getframeinfo", "getouterframes", "getinnerframes",
                "getgeneratorstate", "getgeneratorlocals", "getcoroutinestate", "getcoroutinelocals", "_getframe"}
# 관찰 · 디버그 전용 도구 모듈 — import 자체로 정지(안전 읽기 없음 · N2)
TOOL_MODULES = {"bdb", "pdb", "trace", "profile", "cProfile", "_lsprof", "ctypes", "_ctypes",
                "coverage", "pytest_cov", "hunter", "viztracer", "line_profiler", "yappi", "pyinstrument",
                "debugpy", "pydevd", "ipdb", "pudb", "snoop", "pysnooper", "birdseye", "pydev", "manhole"}
ALLOW_MODULES = set(ALLOW) | {"inspect"}
DANGER_ALL = ALLOW_MODULES | TOOL_MODULES
# from <위험 모듈> import … 로 받아도 되는 안전 이름(관찰 설치 불가 · 현장 실측 + 자명)
SAFE_FROM = {
    "sys": set(),   # from sys import 는 전부 정지(settrace 등)
    "threading": ALLOW["threading"], "_thread": ALLOW["_thread"], "types": ALLOW["types"], "gc": ALLOW["gc"],
    "importlib": {"import_module", "reload", "util", "metadata", "resources", "machinery", "abc"},
    "builtins": set(),
    "inspect": None,   # None = 거부 집합(INSPECT_DENY)만 막고 나머지 허용
}
# N1 — 위험 모듈을 거치지 않고도 쓰는 바로 그 이름(바 Name · 내장 · 어디에 나오든)
OBS_NAMES = {"settrace", "setprofile", "settrace_all_threads", "setprofile_all_threads",
             "addaudithook", "f_trace", "f_trace_lines", "f_trace_opcodes", "set_trace", "breakpoint",
             "monitoring", "_getframe", "_current_frames"}   # v15.1: 재취득한 위험 모듈에서 .monitoring · ._getframe 설치 길도 닫음(현장 0)
CODE_EXEC = {"eval", "exec", "compile"}
IMPORTERS = {"import_module", "reload", "__import__"}


def _term(node) -> "str | None":
    if isinstance(node, _ast.Name):
        return node.id
    if isinstance(node, _ast.Attribute):
        return node.attr
    return None


def _lit(node) -> "str | None":
    return node.value if isinstance(node, _ast.Constant) and isinstance(node.value, str) else None


def _allowed_attr(mod: str, attr: str) -> bool:
    if mod == "inspect":
        return attr not in INSPECT_DENY
    return attr in ALLOW.get(mod, set())


def _importer_arg(call) -> "tuple[bool, str | None]":
    """import_module · reload · __import__ 호출의 이름 인자(위치 0 또는 키워드 name=). (상수인가, 첫 조각)."""
    arg = call.args[0] if call.args else next((k.value for k in call.keywords if k.arg == "name"), None)
    if arg is None:
        return False, None
    lit = _lit(arg)
    return (lit is not None), (lit.split(".")[0] if lit else None)


def _scan_tree(tree, where: str, out: list, depth: int = 0) -> None:
    # 1) 결속 — 평이 import 만 위험 모듈 핸들로 받는다. 별칭 · from(허용 밖) · import * 는 정지.
    handles = {}   # 지역 이름 -> 위험 모듈 canonical(핸들) · 안전 leaf 는 담지 않는다(그 자체로 안전)
    for n in _ast.walk(tree):
        ln = getattr(n, "lineno", 0)
        if isinstance(n, _ast.Import):
            for a in n.names:
                top = a.name.split(".")[0]
                if top in TOOL_MODULES:
                    out.append(f"{where}:{ln} N2 import {a.name}")
                elif top in ALLOW_MODULES:
                    if a.asname and a.asname != top:
                        out.append(f"{where}:{ln} 위험 모듈 별칭 import {a.name} as {a.asname}({top})")
                    else:
                        handles[top] = top
        elif isinstance(n, _ast.ImportFrom) and n.level == 0 and n.module:
            top = n.module.split(".")[0]
            if top in TOOL_MODULES:
                out.append(f"{where}:{ln} N2 from {n.module}")
            elif top in ALLOW_MODULES:
                safe = SAFE_FROM.get(top)
                for a in n.names:
                    if a.name == "*":
                        out.append(f"{where}:{ln} from {n.module} import *({top})")
                    elif safe is None:                       # inspect — 거부 집합만
                        if a.name in INSPECT_DENY:
                            out.append(f"{where}:{ln} from {n.module} import {a.name}(프레임 접근)")
                    elif a.name not in safe:
                        out.append(f"{where}:{ln} from {n.module} import {a.name}(허용 밖 · {top})")
    # 1b) fabfile 네 줄 꼴 — 그 모듈을 import 한 것과 같은 수동 적재만 허용(② · v15.1)
    #    spec = <…>.spec_from_file_location(<상수 비위험 이름>, …) · mod = <…>.module_from_spec(spec)
    #    핸들.modules[spec.name] = mod · (그 뒤 loader.exec_module(mod))  —  이 한 묶음만 쓰기 허용.
    #    v15.2-pre(r15b-4): 받는 쪽은 문면대로 «별칭 없는 import 로 받은 importlib 핸들의 .util» 만(끝 이름만 보던 것을 좁힘).
    def _importlib_util(recv) -> bool:
        return isinstance(recv, _ast.Attribute) and recv.attr == "util" and isinstance(recv.value, _ast.Name) \
            and handles.get(recv.value.id) == "importlib"
    specs, mods = {}, {}
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], _ast.Name) and isinstance(n.value, _ast.Call):
            callee = n.value.func
            if isinstance(callee, _ast.Attribute) and not _importlib_util(callee.value):
                continue
            if isinstance(callee, _ast.Attribute) and callee.attr in ("spec_from_file_location", "spec_from_loader"):
                a0 = n.value.args[0] if n.value.args else None
                lit = _lit(a0) if a0 is not None else None
                specs[n.targets[0].id] = lit is not None and lit.split(".")[0] not in DANGER_ALL
            elif isinstance(callee, _ast.Attribute) and callee.attr == "module_from_spec" and n.value.args and isinstance(n.value.args[0], _ast.Name):
                mods[n.targets[0].id] = n.value.args[0].id
    loader_ok = set()
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
            if isinstance(t, _ast.Subscript) and isinstance(t.value, _ast.Attribute) and isinstance(t.value.value, _ast.Name) \
                    and t.value.value.id in handles and t.value.attr == "modules" \
                    and isinstance(t.slice, _ast.Attribute) and isinstance(t.slice.value, _ast.Name) and t.slice.attr == "name" \
                    and isinstance(n.value, _ast.Name):
                sp, val = t.slice.value.id, n.value.id
                if specs.get(sp) and mods.get(val) == sp:     # 키 = 그 spec.name · 값 = 그 module_from_spec 결과 · 상수 비위험 이름
                    loader_ok.add(id(t))
    # 2) 사용
    attr_values = {id(n.value) for n in _ast.walk(tree) if isinstance(n, _ast.Attribute) and isinstance(n.value, _ast.Name)}
    for n in _ast.walk(tree):
        ln = getattr(n, "lineno", 0)
        if isinstance(n, _ast.Attribute) and isinstance(n.value, _ast.Name) and n.value.id in handles:
            mod = handles[n.value.id]
            if isinstance(n.ctx, _ast.Load) and _allowed_attr(mod, n.attr):
                pass
            else:
                kind = "읽기" if isinstance(n.ctx, _ast.Load) else type(n.ctx).__name__
                out.append(f"{where}:{ln} 위험 모듈 허용 밖 {mod}.{n.attr}[{kind}]")
        elif isinstance(n, _ast.Name) and n.id in handles and id(n) not in attr_values:
            out.append(f"{where}:{ln} 위험 모듈 객체가 샘 {n.id}(이름 · 인자 · 반사)")
        elif isinstance(n, _ast.Subscript) and isinstance(n.value, _ast.Attribute) \
                and isinstance(n.value.value, _ast.Name) and n.value.value.id in handles \
                and n.value.attr == "modules":
            dm = handles[n.value.value.id]
            key = _lit(n.slice)
            if not isinstance(n.ctx, _ast.Load):             # ② 쓰기 · 삭제 — fabfile 적재 꼴(쓰기)과 그 짝 cleanup(삭제)만 허용, 그 밖 정지
                del_ok = isinstance(n.ctx, _ast.Del) and isinstance(n.slice, _ast.Attribute) \
                    and isinstance(n.slice.value, _ast.Name) and n.slice.attr == "name" and specs.get(n.slice.value.id)
                if id(n) not in loader_ok and not del_ok:
                    out.append(f"{where}:{ln} {dm}.modules[...] {'삭제' if isinstance(n.ctx, _ast.Del) else '쓰기'}")
            elif key is not None and key.split(".")[0] in DANGER_ALL:   # ③ 상수 위험 이름 읽기 재취득
                out.append(f"{where}:{ln} 위험 모듈 재취득 {dm}.modules[{key!r}]")
        elif isinstance(n, _ast.Call):
            f = _term(n.func)
            if f in IMPORTERS:                               # import_module · reload · __import__ — 상수 이름이 위험 모듈이면 정지
                const, first = _importer_arg(n)
                if const and first in DANGER_ALL:
                    out.append(f"{where}:{ln} 위험 모듈 재취득 {f}({first!r})")
            if f == "get" and isinstance(n.func, _ast.Attribute) and isinstance(n.func.value, _ast.Attribute) \
                    and isinstance(n.func.value.value, _ast.Name) and n.func.value.value.id in handles \
                    and n.func.value.attr == "modules" and n.args:   # ③ 핸들.modules.get(상수 위험) 재취득
                kl = _lit(n.args[0])
                if kl is not None and kl.split(".")[0] in DANGER_ALL:
                    out.append(f"{where}:{ln} 위험 모듈 재취득 {handles[n.func.value.value.id]}.modules.get({kl!r})")
            if isinstance(n.func, _ast.Name) and f in CODE_EXEC and n.args:
                lit = _lit(n.args[0])
                if lit is None:
                    out.append(f"{where}:{ln} D3 {f}(문자열 아닌 코드)")
                elif depth < 3:
                    try:
                        _scan_tree(_ast.parse(lit), f"{where}:{ln}<{f}>", out, depth + 1)
                    except SyntaxError:
                        out.append(f"{where}:{ln} D3 {f}(파싱 못 함)")
        if isinstance(n, _ast.Name) and n.id in OBS_NAMES:   # N1 — 어디에 나오든(도메인 동음이의 비용 · 설계 §4-1 알림)
            out.append(f"{where}:{ln} N1 {n.id}")
        if isinstance(n, _ast.Attribute) and n.attr in OBS_NAMES and not (isinstance(n.value, _ast.Name) and n.value.id in handles):
            out.append(f"{where}:{ln} N1 .{n.attr}")   # 핸들 밖에서 .settrace 등(핸들이면 위에서 이미 잡음)

def observer_scan_sources(sources: "dict[str, bytes]") -> "tuple[list[str], int]":
    """원문 바이트(rel → bytes · .py 만)의 AST 에 위험 모듈 허용 밖 · N1 · N2 · D3 꼴이 있으면 위반. 바이트로 파싱해
    PEP 263 인코딩 표지를 존중한다. (위반 목록 · 본 .py 수)."""
    out: list = []
    n = 0
    for rel in sorted(r for r in sources if r.endswith(".py")):
        n += 1
        try:
            tree = _ast.parse(sources[rel])
        except SyntaxError:
            ver = ".".join(str(x) for x in sys.version_info[:3])
            out.append(f"{rel}:0 정적 확인 못 함(파싱 실패 — 파서 판 {ver})")
            continue
        except (ValueError, UnicodeError):
            out.append(f"{rel}:0 정적 확인 못 함(원문 디코딩 실패)")
            continue
        _scan_tree(tree, rel, out)
    return sorted(set(out)), n


def observer_scan(repo: Path, rels: "set[str]") -> "tuple[list[str], int]":
    """저장소 파일 rels(.py) 를 읽어 observer_scan_sources 와 같은 판정 — 읽지 못한 파일은 «정적 확인 못 함(읽기 실패)»."""
    sources: "dict[str, bytes]" = {}
    unread: "list[str]" = []
    for rel in sorted(r for r in rels if r.endswith(".py")):
        try:
            sources[rel] = (repo / rel).read_bytes()
        except OSError:
            unread.append(f"{rel}:0 정적 확인 못 함(읽기 실패)")
    hits, n = observer_scan_sources(sources)
    return sorted(set(hits) | set(unread)), n + len(unread)


def is_test_side(path: str, test_dirs: "set[str]") -> bool:
    """리팩토링 모드 시험 쪽 분류 — `behavior_guard._is_test_refactor` 와 같은 함수다(정의는 그쪽 한 곳 · 설계 §4-1 · v6)."""
    return bg._is_test_refactor(path, test_dirs)


def fingerprint(repo: Path) -> str:
    """트리 지문 — HEAD 커밋(없으면 unborn) + 작업 트리 변경 경로(bg._dirty · `.dddjango/` 제외)마다 경로 · 내용 sha256."""
    head = bg._git(repo, "rev-parse", "--verify", "-q", "HEAD^{commit}", check=False).strip() or "unborn"
    h = hashlib.sha256(head.encode("utf-8") + b"\0")
    for rel in bg._dirty(repo):
        p = repo / rel
        sha = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "없음"
        h.update(rel.encode("utf-8", "surrogateescape") + b"\0" + sha.encode("utf-8") + b"\0")
    return h.hexdigest()[:12]


def _file_digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else "없음"


def _obj_digest(obj: object) -> str:
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8", "surrogateescape")).hexdigest()[:12]


def _definition_digest(definition: dict) -> str:
    """실행 정의 digest — argv 목록과 동결 변수 여섯만(시각 · 출처는 밖)."""
    return _obj_digest({"argvs": definition["argvs"], "env": definition["env"]})


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, data: object) -> None:
    """경로 · 환경 값은 git · OS 가 surrogateescape 로 넘긴 글자를 담을 수 있다 — 원래 바이트로 되돌려 쓴다."""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", errors="surrogateescape")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8", errors="surrogateescape"))


def _say(text: str, *, err: bool = False) -> None:
    """출력 한 줄 — 스트림 인코딩으로 못 쓰는 글자(surrogateescape 경로 등)는 `\\udcXX` 꼴로 바꿔 출력이 죽지 않게."""
    stream = sys.stderr if err else sys.stdout
    enc = getattr(stream, "encoding", None) or "utf-8"
    print(text.encode(enc, "backslashreplace").decode(enc), file=stream)


def _command_env(definition: dict, inherited: "dict[str, str]") -> "dict[str, str]":
    env = dict(inherited)
    for k in FROZEN:
        env.pop(k, None)
        if definition["env"].get(k) is not None:
            env[k] = definition["env"][k]
    env.update({"PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": os.pathsep.join([str(PROBE_DIR)] + ([inherited["PYTHONPATH"]] if inherited.get("PYTHONPATH") else []))})
    return env


def _end_group(child: "subprocess.Popen[bytes]") -> None:
    """상한을 넘은 명령 — 그 명령이 띄운 프로세스 묶음(start_new_session 의 그룹)만 끝낸다."""
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    if child.poll() is None:
        child.kill()
    try:
        child.communicate(timeout=30)
    except subprocess.TimeoutExpired:   # 묶음 밖으로 나간 자손이 출력 관을 쥐고 있다 — 그 자손에는 신호를 보내지 않는다
        for pipe in (child.stdout, child.stderr):
            if pipe is not None:
                pipe.close()
        child.wait()


def _clean_created(repo: Path, before: "set[str]") -> "list[str]":
    """실행이 만든 미추적 파일을 지운다 — 장치가 자기 부작용으로 판정 · 지문을 바꾸지 않게."""
    created = sorted(bg._untracked(repo) - before)
    for rel in created:
        if (repo / rel).is_file():
            (repo / rel).unlink()
    return created


def _scope_files(repo: Path) -> "set[str]":
    """저장소 안 파일 — git 추적 ∪ 무시되지 않은 미추적 가운데 제외 자리(`.dddjango/` 등) 밖이고 지금 파일이거나 심링크인 것.

    끊긴 심링크도 범위에 둔다 — 시험 쪽 `.py` 자리면 정적 규칙이 «읽기 실패» 로 정지한다(확인 못 한 시험 쪽 코드).
    작업 트리에서 지운 추적 파일은 범위 밖이다."""
    out = bg._git(repo, "ls-files", "-co", "--exclude-standard", "-z")
    return {p for p in set(out.split("\0"))
            if p and not bg._excluded(p) and ((repo / p).is_file() or (repo / p).is_symlink())}


def _read_outputs(out: Path, tag: str, reasons: "list[str]") -> "list[dict]":
    outs: "list[dict]" = []
    for f in sorted(out.glob("*.json")):
        try:
            data = _read_json(f)
        except (OSError, ValueError):
            reasons.append(f"확인 못 함 — 탐침 출력 읽기 실패 {f.name} · {tag}")
            continue
        if isinstance(data, dict):
            outs.append(data)
        else:
            reasons.append(f"확인 못 함 — 탐침 출력 읽기 실패 {f.name} · {tag}")
    return outs


def _strs(v: object) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _field_ok(kind: str, v: object, o: dict) -> bool:
    if kind == "int":
        return type(v) is int
    if kind == "bool":
        return type(v) is bool
    if kind == "strs":
        return _strs(v)
    if kind == "dict":
        return isinstance(v, dict)
    if kind == "role":
        return v in ROLES
    if kind == "workerid":
        return (isinstance(v, str) and v != "") if o.get("role") == "worker" else v is None
    if kind == "meta":
        return isinstance(v, dict) and all(
            isinstance(k, str) and isinstance(m, list) and len(m) == 4 and isinstance(m[0], str)
            and (m[1] is None or isinstance(m[1], str)) and isinstance(m[2], str) and isinstance(m[3], str)
            for k, m in v.items())
    if kind == "anchor":
        return isinstance(v, list) and all(
            isinstance(a, dict) and all(k in a and (a[k] is None or isinstance(a[k], str)) for k in ANCHOR_KEYS) for a in v)
    if kind == "hooks":
        return isinstance(v, list) and all(
            isinstance(h, dict) and isinstance(h.get("hook"), str) and _strs(h.get("files")) and _strs(h.get("origins"))
            and len(h["files"]) == len(h["origins"]) for h in v)
    if kind == "pairs":
        return isinstance(v, list) and all(isinstance(p, list) and len(p) == 2 and _strs(p) for p in v)
    raise ValueError(f"모르는 칸 형식 {kind}")


def _field_problems(o: dict) -> "list[tuple[str, str]]":
    """판정 · 계수에 쓰는 탐침 기록 칸 가운데 없거나 형식 밖인 것 — [(칸, «없음» | «형식 밖»)]."""
    out: "list[tuple[str, str]]" = []
    for name, kind in PROBE_FIELDS.items():
        if name not in o:
            out.append((name, "없음"))
        elif not _field_ok(kind, o[name], o):
            out.append((name, "형식 밖"))
    return out


def _new_counts() -> "dict[str, int]":
    return {k: 0 for k in ("commands", "collected", "selected", "calls", "skips", "complete", "proof_ok", "proof_total",
                           "reentry", "anchor", "suspend", "observer_files", "observer_hits", "nolist", "unresolved", "late",
                           "hooks", "M", "failed", "optimize")}


def run(repo: Path, definition: dict, mode: str, inherited: "dict[str, str]", *,
        probe_out_root: Path, scope: "set[str] | None" = None,
        drop_worker: bool = False, stop_on_fail: bool = False) -> "tuple[list[str], dict]":
    """동결 실행 정의의 명령마다 탐침을 붙여 돌리고 (정지 · red 사유 목록, 실행 정보)를 낸다. mode = collect | run.

    탐침 출력은 `<probe_out_root>/<n>/<pid>.json` 에 남긴다(지우지 않는다 · 자리는 비어 있어야 한다).
    scope 기본 = 저장소 안 파일(_scope_files — git 추적 ∪ 무시되지 않은 미추적 · `.dddjango/` 제외 · 끊긴 심링크 포함).
    drop_worker 는 시험 자리.
    stop_on_fail = 첫 실패(exit · 상한 초과)에서 남은 명령을 돌지 않는다(suite)."""
    if mode not in ("collect", "run"):
        raise ValueError(f"mode 는 collect | run — {mode!r}")
    reasons: "list[str]" = []
    counts = _new_counts()
    info: dict = {"seconds": 0.0, "outputs": 0, "fp": [], "initial": set(), "ok": set(), "meta": {}, "anchor": [], "nolist": [],
                  "flags": {}, "greenlet_loaded": False, "project_hooks": set(), "commands": [], "cleaned": [], "counts": counts}
    root = repo.resolve()
    out_root = Path(probe_out_root).resolve()
    if out_root.is_relative_to(root) and not bg._excluded(out_root.relative_to(root).as_posix() + "/"):
        raise ValueError(f"탐침 출력 자리는 저장소 밖이거나 `.dddjango/` 아래여야 한다 — {out_root}")
    scope = set(scope) if scope is not None else _scope_files(repo)
    td = bg._test_dirs(sorted(scope))
    for rel in sorted(scope):
        if rel.startswith(MENTION_SKIP_PREFIXES):
            continue
        try:
            if (root / rel).resolve() == PROBE_FILE:
                continue
            if PROBE_NAME in (repo / rel).read_text(encoding="utf-8", errors="ignore"):
                reasons.append(f"탐침을 언급하는 저장소 파일: {rel}")
        except (OSError, RuntimeError):     # 끊긴 · 맴도는 심링크 · 읽을 수 없는 파일 — 언급 확인에서는 넘긴다
            pass
    env = _command_env(definition, inherited)
    initial_all, selected_all, M = set(), set(), set()
    info["fp"].append(fingerprint(repo))
    for n, argv in enumerate(definition["argvs"], 1):
        out = out_root / str(n)
        out.mkdir(parents=True, exist_ok=True)
        if any(out.iterdir()):
            raise ValueError(f"탐침 출력 자리가 비어 있지 않다 — {out}")
        env["DDDJANGO_PROBE_OUT"] = str(out)
        cmd = [*argv, "-p", "no:cacheprovider", "-p", PROBE_NAME] + (["--collect-only", "-q"] if mode == "collect" else [])
        rec: dict = {"argv": list(argv), "exit": None, "probe_exit": None, "outputs": 0, "workers_ready": 0,
                     "worker_outputs": 0, "seconds": 0.0}
        info["commands"].append(rec)
        before = bg._untracked(repo)
        t0 = time.monotonic()
        child = subprocess.Popen(cmd, cwd=repo, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        try:
            child.communicate(timeout=SUITE_COMMAND_TIMEOUT_SECONDS if mode == "run" else COMMAND_TIMEOUT_SECONDS)
            timed_out = False
        except subprocess.TimeoutExpired:
            _end_group(child)
            timed_out = True
        elapsed = time.monotonic() - t0
        rec["seconds"], rec["exit"] = round(elapsed, 3), child.returncode
        info["cleaned"] += _clean_created(repo, before)
        if timed_out:
            reasons.append(f"확인 못 함 — 시간 초과 · {' '.join(argv)}")
            if stop_on_fail:
                break
            continue
        info["seconds"] += elapsed
        info["fp"].append(fingerprint(repo))
        rc = child.returncode
        tag = " ".join(str(a) for a in argv[-3:])
        failed_cmd = rc not in (0, 5) if mode == "collect" else rc != 0
        outs = _read_outputs(out, tag, reasons)
        if drop_worker:
            ws = [o for o in outs if o.get("role") == "worker"]
            if ws:
                outs.remove(ws[-1])
        info["outputs"] += len(outs)
        rec["outputs"] = len(outs)
        if mode == "collect" and rc not in (0, 5):
            reasons.append(f"확인 못 함 — 수집 실패 exit {rc} · {tag}")
        if mode == "run" and rc != 0:
            reasons.append(f"suite red — exit {rc} · {tag}")
        if not outs:
            reasons.append(f"확인 못 함 — 탐침 출력 없음(exit {rc}) · {tag}")
            if stop_on_fail and failed_cmd:
                break
            continue
        # 판정 · 계수에 쓰는 칸 — 없거나 형식 밖이면 정지하고, 그 칸은 아래에서 쓰지 않는다(기본값으로 메우지 않음)
        bad_fields: "dict[int, set[str]]" = {}
        for o in outs:
            probs = _field_problems(o)
            bad_fields[id(o)] = {name for name, _how in probs}
            for name, how in probs:
                reasons.append(f"확인 못 함 — 탐침 기록 칸 {how} {name} · {tag}")

        def has(o: dict, field: str) -> bool:
            return field not in bad_fields[id(o)]

        ctrl = [o for o in outs if has(o, "role") and o["role"] == "controller"]
        workers = [o for o in outs if has(o, "role") and o["role"] == "worker"]
        single = [o for o in outs if has(o, "role") and o["role"] == "single"]
        if mode == "collect":
            # 수집만 하는 실행에서는 xdist 가 꺼진다 — 명령마다 단일 출력 정확히 하나(조정자 · 일꾼 · 역할 밖 출력이 오면 정지)
            if len(outs) != 1 or len(single) != 1:
                reasons.append(f"확인 못 함 — 출력 수 이상 · {tag}")
            runners, reporter = single, (single[0] if single else None)
        elif ctrl:
            # xdist — 조정자 정확히 하나 + 준비 일꾼 id 마다 일꾼 출력 정확히 하나(중복 · 준비 밖 id · 단일 · 역할 밖 출력은 정지)
            c0 = ctrl[0]
            ready = sorted(set(c0["workers_ready"])) if has(c0, "workers_ready") else []
            got = sorted(o["workerid"] if has(o, "workerid") else "?" for o in workers)
            if len(ctrl) != 1 or single or len(outs) != len(ctrl) + len(workers) or not ready or got != ready:
                reasons.append(f"확인 못 함 — xdist 출력 불완전(준비 {ready} · 출력 {got}) · {tag}")
            runners, reporter = workers, c0
            rec["workers_ready"] = len(ready)
        else:
            # 단일 실행 — 전체 출력 정확히 하나 · 역할 single
            if len(outs) != 1 or len(single) != 1:
                reasons.append(f"확인 못 함 — 출력 수 이상 · {tag}")
            runners, reporter = single, (single[0] if single else None)
        rec["worker_outputs"] = len(workers)
        rec["probe_exit"] = reporter["exitstatus"] if reporter is not None and has(reporter, "exitstatus") else None
        initial = set().union(*(set(o["initial"]) for o in runners if has(o, "initial")))
        for o in runners:
            if has(o, "meta"):
                info["meta"].update(o["meta"])
        final = set().union(*(set(o["final"]) for o in runners if has(o, "final")))
        if mode == "run":
            def reported(field: str) -> "set[str]":
                return set(reporter[field]) if reporter is not None and has(reporter, field) else set()
            calls, skips, passed = reported("calls"), reported("skips"), reported("passed")
            ok = skips | calls
            complete = set().union(*(set(o["complete"]) for o in runners if has(o, "complete")))
            if not final <= ok or not final <= complete:
                reasons.append(f"확인 못 함 — 선택 {len(final)} · 처분 {len(final & ok)}(call 보고 {len(final & calls)} · skip {len(final & skips)}) · 완료 {len(final & complete)} · {tag}")
            info["ok"] |= ok
            failed = sum(o["failed"] for o in outs if has(o, "failed"))   # 일꾼까지 모든 출력의 합(일꾼 탐침은 tryfirst — 보고 고치기 전)
            if failed:
                reasons.append(f"실패 보고 {failed}(모든 출력 합) — exit {rc} 와 무관하게 정지 · {tag}")
            if reporter is not None and has(reporter, "exitstatus") and reporter["exitstatus"] != rc:
                reasons.append(f"탐침이 본 exit {reporter['exitstatus']} ≠ 프로세스 exit {rc} · {tag}")
            for o in outs:
                for nid in (o["import_skips"] if has(o, "import_skips") else []):
                    reasons.append(f"import 실패 skip(importorskip 꼴 — 제품 이동 의심): {nid}")
            # 결과 증거 계수 — 분모 = 선택 ∩ passed call · 분자 = 그 가운데 결과 증거 위반(증거 없음 · 일시 중단 본문)이 아닌 것
            proof_viol = {where for o in runners if has(o, "bad") for where, what in o["bad"] if what.startswith(PROOF_MISSING)}
            proof_viol |= {nid for o in runners if has(o, "flags") for nid in o["flags"]}
            counts["calls"] += len(final & calls)
            counts["skips"] += len(final & skips)
            counts["complete"] += len(final & complete)
            counts["proof_total"] += len(final & passed)
            counts["proof_ok"] += len((final & passed) - proof_viol)
        initial_all |= initial
        selected_all |= final
        for o in outs:
            role = o["role"] if has(o, "role") else "?"
            if has(o, "failed"):
                counts["failed"] += o["failed"]
            if has(o, "unresolved"):
                counts["unresolved"] += len(o["unresolved"])
            if has(o, "finalized") and not o["finalized"]:
                reasons.append(f"확인 못 함 — 탐침 확정 표지 없음 · {tag}")
            for late in (o["late"] if has(o, "late") else []):
                counts["late"] += 1
                reasons.append(f"탐침 확정 뒤 플러그인 등록: {late}")
            if has(o, "optimize") and o["optimize"]:
                counts["optimize"] += 1
                reasons.append(f"assert 를 지우는 실행(sys.flags.optimize={o['optimize']}) · {role} · {tag}")
            for a in (o["anchor"] if has(o, "anchor") else []):
                reasons.append(f"정의 자리 밖 — 가장 안쪽 코드 {_rel(a['inner'], root)}::{a['inner_qual']} ≠ {_rel(a['home'] or '?', root)}::{a['qual']}({a['nid']})")
                info["anchor"].append(a)
            nolist = o.get("nolist", [])                     # 탐침 기록 칸이 아님(옛 판 자리) — 계수만
            info["nolist"] += nolist if isinstance(nolist, list) else []
            if has(o, "flags"):
                info["flags"].update(o["flags"])
            if has(o, "greenlet_loaded"):
                info["greenlet_loaded"] = info["greenlet_loaded"] or o["greenlet_loaded"]
            for h in (o["hookimpls"] if has(o, "hookimpls") else []):
                # 원본 상위 집합(실행 코드 원본 + __wrapped__ 전부 + 환경 층이 클로저로 쥔 함수)의 한 파일이라도 저장소 파일이면 프로젝트 훅
                rels = []
                for f, origin in zip(h["files"], h["origins"]):
                    p = Path(f)
                    rel = p.relative_to(root).as_posix() if p.is_relative_to(root) else None
                    if rel is not None and rel in scope:
                        rels.append(rel)
                    elif origin not in ENV_ORIGINS:
                        reasons.append(f"정체 불명 훅 원본(저장소 · 설치 패키지 밖): {f}::{h['hook']}")
                for rel in rels:
                    info["project_hooks"].add(f"{rel}::{h['hook']}")
                    if h["hook"] not in ALLOWED_HOOKS:
                        reasons.append(f"허용 목록 밖 프로젝트 훅 {h['hook']}: {rel}")
            for where, what in (o["bad"] if has(o, "bad") else []):
                reasons.append(f"허용 밖: {what}({where})")
                if what.startswith(REENTRY):
                    counts["reentry"] += 1
            for where, what in (o["unresolved"] if has(o, "unresolved") else []):
                reasons.append(f"원본 확인 못 함 — {what}({where})")
            for f in (o["files"] if has(o, "files") else []):
                p = Path(f)
                if p.is_relative_to(root):
                    rel = p.relative_to(root).as_posix()
                    if rel in scope:
                        M.add(rel)
        if stop_on_fail and failed_cmd:
            break
    if initial_all != selected_all:
        reasons.append(f"확인 못 함 — 선택 합 {len(selected_all)} ≠ 수집 합 {len(initial_all)}")
    # 실행 관찰 API 정적 규칙 — M ∪ 시험 쪽 분류의 .py(시험 쪽 도우미는 M 밖일 수 있다)
    test_side_py = {r for r in scope if r.endswith(".py") and is_test_side(r, td)}
    m_py = {r for r in M if r.endswith(".py")}
    hits_m, n_m = observer_scan(repo, m_py)
    hits_u, n_u = observer_scan(repo, m_py | test_side_py)
    info.update({"obs_files_M": n_m, "obs_files_union": n_u, "obs_hits_M": hits_m, "obs_hits_union": hits_u})
    for h in hits_u:
        reasons.append(f"실행 관찰 API(증명 지원 밖): {h}")
    for rel in sorted(M):
        if not is_test_side(rel, td):
            reasons.append(f"시험 기계 파일이 분류 밖: {rel}")
    if len(set(info["fp"])) != 1:
        reasons.append(f"트리 지문 불일치(실행 중 변경) {info['fp']}")
    keys = {}
    for nid in initial_all:
        m = info["meta"].get(nid)
        if m is None:
            reasons.append(f"확인 못 함 — 구조 키 없음: {nid}")
            continue
        keys[nid] = _key(m, root)
    info.update({"M": len(M), "M_files": sorted(M), "selected": len(selected_all), "initial": initial_all, "keys": keys,
                 "digests": {k[0]: _file_digest(repo / k[0]) for k in keys.values()}})
    counts.update({"commands": len(info["commands"]), "collected": len(initial_all), "selected": len(selected_all),
                   "anchor": len(info["anchor"]), "suspend": len(info["flags"]), "observer_files": n_u,
                   "observer_hits": len(hits_u), "nolist": len(info["nolist"]), "hooks": len(info["project_hooks"]),
                   "M": len(M)})
    return sorted(set(reasons)), info


def _rel(f: str, root: Path) -> str:
    p = Path(f)
    return p.relative_to(root).as_posix() if p.is_relative_to(root) else f


def _key(meta: list, root: Path) -> tuple:
    """구조 키(v11) — (저장소 상대 파일 · 클래스 qualname · 함수 originalname · 항목 이름). nodeid 문자열을 쪼개지 않는다."""
    f, cls, func, name = meta
    p = Path(f)
    rel = p.relative_to(root).as_posix() if p.is_relative_to(root) else f
    return (rel, cls, func, name)


def g0_keep(g0: dict, g2: dict, repo: Path, moved: "dict[str, str] | None" = None, removed: "set | None" = None) -> "list[str]":
    """G0 유지 셋(v11 구조 키): ① 파일 단위 — 지금 있는 G0 수집 파일은 처분 항목이 하나 이상
    ② 바이트 같은 파일 — G0 항목(파일 · 클래스 · 함수 · 항목 이름) 전부 ③ 바뀐 파일 — (파일 · 클래스 · 함수)마다 처분 수 ≥ G0 수.
    예외는 감사 · 승인 자료에 있는 것만: removed(`remove` 행의 구조 키 · 지운 파일) · moved(대응표 · retain 재조직이 옮긴 자리)."""
    moved, removed = moved or {}, {tuple(x) if isinstance(x, list) else x for x in (removed or set())}
    g0 = {**g0, "keys": {n: tuple(k) for n, k in g0["keys"].items()}}       # JSON 기록(목록)도 받는다
    g2 = {**g2, "keys": {n: tuple(k) for n, k in g2["keys"].items()}}
    ok_keys = {g2["keys"][n] for n in g2["ok"] if n in g2["keys"]}
    ok_files = {k[0] for k in ok_keys}
    ok_funcs = {k[:3] for k in ok_keys}
    n_g2: dict = {}
    for k in ok_keys:
        n_g2[k[:3]] = n_g2.get(k[:3], 0) + 1
    n_g0: dict = {}
    for k in set(g0["keys"].values()):
        n_g0[k[:3]] = n_g0.get(k[:3], 0) + 1
    out = []
    for k in sorted(set(g0["keys"].values()), key=repr):
        rel = k[0]
        new = moved.get(rel, rel)
        if k in removed or k[:3] in removed or rel in removed or not (repo / new).is_file():
            continue
        k2 = (new, *k[1:])
        if new not in ok_files:
            out.append(f"파일 단위: {new}")
        elif _file_digest(repo / new) == g0["digests"].get(rel):
            if k2 not in ok_keys:
                out.append(f"항목 단위: {k2}")
        elif k2[:3] not in ok_funcs:
            out.append(f"함수 단위(바뀐 파일): {k2[:3]}")
        elif n_g2[k2[:3]] < n_g0[k[:3]]:                     # v11(Claude r10 m3): 매개변수 축소 — 처분 수 ≥ G0 수
            out.append(f"함수 단위 처분 수 {n_g2[k2[:3]]} < G0 {n_g0[k[:3]]}(바뀐 파일): {k2[:3]}")
    return sorted(set(out))


# ── 기록 자리 ─────────────────────────────────────────────────────────────────

def support_root(folder: Path) -> Path:
    """승인 전 지원 확인 기록 자리 — `<폴더>/behavior/support/` (시각 폴더마다 덮어쓰지 않는다)."""
    return Path(folder) / "behavior" / "support"


def _support_stamps(folder: Path) -> "list[Path]":
    root = support_root(folder)
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and SUPPORT_STAMP_RE.match(p.name))


def latest_support(folder: Path) -> "Path | None":
    """g0-collect.json 의 verdict 가 «지원» 인 가장 새 시각 폴더."""
    for p in reversed(_support_stamps(folder)):
        g0 = p / "g0-collect.json"
        if g0.is_file():
            try:
                if _read_json(g0).get("verdict") == "지원":
                    return p
            except (OSError, ValueError, AttributeError):
                continue
    return None


def _pending_support(folder: Path) -> Path:
    """g0-collect.json 이 아직 없는 가장 새 시각 폴더 — 판정이 끝난 가장 새 폴더보다 뒤여야 한다(낡은 자리를 다시 돌지 않는다)."""
    stamps = _support_stamps(folder)
    done = [p.name for p in stamps if (p / "g0-collect.json").exists()]
    newest_done = done[-1] if done else ""
    pending = [p for p in stamps if not (p / "g0-collect.json").exists() and p.name > newest_done]
    if not pending:
        raise SupportError(f"새 지원 확인 기록 자리 없음 — {support_root(folder)}/<UTC %Y%m%dT%H%M%SZ>/test-commands.md 를 먼저 쓴다")
    rec = pending[-1]
    used = [name for name in ("run-definition.json", "probe") if (rec / name).exists()]
    if used:
        raise SupportError(f"기록 자리 {rec.name} 는 이미 쓰였다({' · '.join(used)}) — 새 시각 폴더에 test-commands.md 를 쓴다")
    return rec


def _read_test_commands(path: Path) -> "tuple[list[list[str]], list[str]]":
    """`시험 명령 <n>: <argv 텍스트>` 다음 줄 `출처: <…>` — n 은 1 부터 차례. argv = shlex.split."""
    if not path.is_file():
        raise SupportError(f"test-commands.md 없음 — {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    argvs: "list[list[str]]" = []
    sources: "list[str]" = []
    i = 0
    while i < len(lines):
        m = COMMAND_LINE_RE.match(lines[i].strip())
        if not m:
            i += 1
            continue
        n = int(m.group(1))
        if n != len(argvs) + 1:
            raise SupportError(f"시험 명령 번호가 차례가 아니다 — {n}(기대 {len(argvs) + 1})")
        s = SOURCE_LINE_RE.match(lines[i + 1].strip()) if i + 1 < len(lines) else None
        if s is None:
            raise SupportError(f"시험 명령 {n} 다음 줄에 `출처: …` 가 없다")
        try:
            argv = shlex.split(m.group(2))
        except ValueError as exc:
            raise SupportError(f"시험 명령 {n} 을 argv 로 나누지 못함 — {exc}") from exc
        if not argv:
            raise SupportError(f"시험 명령 {n} 이 비었다")
        argvs.append(argv)
        sources.append(s.group(1).strip())
        i += 2
    if not argvs:
        raise SupportError(f"시험 명령 줄이 없다 — {path}")
    return argvs, sources


def _is_pytest(argv: "list[str]") -> bool:
    """pytest 실행 표지 — `pytest` · `py.test` 실행 파일 · `-m pytest`(`uv run … pytest` 포함)."""
    for i, a in enumerate(argv):
        if PurePosixPath(a).name in ("pytest", "py.test") or a == "-mpytest":
            return True
        if a == "-m" and i + 1 < len(argv) and argv[i + 1] == "pytest":
            return True
    return False


def _run_dir_stamp(run_dir: Path) -> str:
    """suite 기록 이름 — 같은 초의 앞 기록을 덮지 않게 다음 초까지 기다린다."""
    while True:
        stamp = _utc()
        if not (run_dir / f"suite-{stamp}.json").exists() and not (run_dir / "probe" / stamp).exists():
            return stamp
        time.sleep(0.2)


# ── support --collect ─────────────────────────────────────────────────────────

def cmd_support(folder: Path, repo: Path) -> int:
    """G0 지원 확인 — 실행 정의 동결 + 수집 탐침. exit 0 지원 · 2 지원 안 함 · 1 실행 불능."""
    folder, repo = Path(folder), Path(repo)
    try:
        rec_dir = _pending_support(folder)
        argvs, sources = _read_test_commands(rec_dir / "test-commands.md")
        inherited = dict(os.environ)
        definition = {"version": 1, "argvs": argvs, "env": {k: inherited.get(k) for k in FROZEN}, "sources": sources,
                      "frozen_at": _utc()}
        _write_json(rec_dir / "run-definition.json", definition)
        digest = _definition_digest(definition)
        started = _utc()
        non_pytest = [f"지원 안 함 — pytest 실행이 아님: 시험 명령 {n}: {shlex.join(a)}"
                      for n, a in enumerate(argvs, 1) if not _is_pytest(a)]
        if non_pytest:
            reasons, info = sorted(non_pytest), {}
        else:
            reasons, info = run(repo, definition, "collect", inherited, probe_out_root=rec_dir / "probe")
        ended = _utc()
    except (SupportError, bg.RunError, OSError, ValueError, KeyError, TypeError) as exc:
        _say(f"실행 불능: {type(exc).__name__}: {exc}", err=True)
        _say(f"요약: 지원 확인 실행 불능 — {str(exc)[:160]}")
        return 1
    verdict = "지원" if not reasons else "지원 안 함"
    hooks = sorted(info.get("project_hooks", set()))
    record = {"version": 1, "support_record": rec_dir.name, "run_definition_digest": digest, "verdict": verdict,
              "reasons": reasons, "keys": {nid: list(k) for nid, k in sorted(info.get("keys", {}).items())},
              "digests": dict(sorted(info.get("digests", {}).items())), "M_files": info.get("M_files", []),
              "project_hooks": hooks, "selected": info.get("selected", 0), "collected": len(info.get("initial", set())),
              "outputs": info.get("outputs", 0), "seconds": round(info.get("seconds", 0.0), 3),
              "fingerprints": info.get("fp", []),
              "commands": [{k: c[k] for k in ("argv", "exit", "outputs", "seconds")} for c in info.get("commands", [])],
              "started": started, "ended": ended}
    _write_json(rec_dir / "g0-collect.json", record)
    for r in reasons:
        _say(f"  정지: {r}")
    for h in hooks:
        _say(f"  프로젝트 훅: {h}")
    _say(f"요약: 지원 확인 {verdict} · 기록 {rec_dir.name} · 실행 정의 {digest} · 시험 명령 {len(argvs)} · "
          f"수집 항목 {record['collected']} · 선택 {record['selected']} · 시험 기계 파일 {len(record['M_files'])} · "
          f"분류 밖 {sum(r.startswith('시험 기계 파일이 분류 밖') for r in reasons)} · 프로젝트 훅 {len(hooks)} · 정지 사유 {len(reasons)}")
    return 0 if verdict == "지원" else 2


# ── suite ────────────────────────────────────────────────────────────────────

def _g0_keep_exceptions(run_dir: Path) -> "tuple[dict[str, str], set]":
    """그 실행의 모든 창 마지막 close 의 g0_keep_exceptions 합 — moved 는 사슬을 끝까지 따라간다."""
    moved: "dict[str, str]" = {}
    removed: set = set()
    for _n, _opened, closes in bg._windows(run_dir):
        if not closes:
            continue
        ex = closes[-1].get("g0_keep_exceptions") or {}
        moved.update(ex.get("moved") or {})
        for item in ex.get("removed") or []:
            if isinstance(item, str) and "::" in item:
                parts = item.split("::")
                if len(parts) != 3:
                    raise SupportError(f"g0_keep_exceptions.removed 판형 밖 — {item!r}(rel::cls::func 또는 rel)")
                rel, cls, func = parts
                removed.add((rel, cls if cls not in ("", "None") else None, func))
            else:
                removed.add(item)
    resolved: "dict[str, str]" = {}
    for old in moved:
        new, seen = moved[old], {old}
        while new in moved and new not in seen:
            seen.add(new)
            new = moved[new]
        resolved[old] = new
    return resolved, removed


def cmd_suite(folder: Path, repo: Path) -> int:
    """G2 증거 실행 — G1 이 결속한 지원 기록의 실행 정의를 그대로. exit 0 green · 2 red · 1 실행 불능."""
    folder, repo = Path(folder), Path(repo)
    try:
        import refactor_audit as ra
        try:
            g1 = ra.g1_confirmed(folder)
        except Exception as exc:  # noqa: BLE001 — 결속 줄을 못 읽으면 결속을 확인할 수 없다
            raise SupportError(f"G1 결속 기록을 읽지 못함 — {type(exc).__name__}: {exc}") from exc
        if g1 is None:
            raise SupportError("G1 결속 기록 없음 — 이번 실행 몫의 `G1 변경판 확정 <시각> · digest <d> · 후보 <c>` 줄이 없다")
        at, g1_digest, candidate = g1
        try:
            snap = ra.load_candidate(folder, candidate)
        except Exception as exc:  # noqa: BLE001 — 후보 스냅숏을 못 읽으면 결속을 확인할 수 없다
            raise SupportError(f"G1 후보 스냅숏 {candidate} 을 읽지 못함 — {type(exc).__name__}: {exc}") from exc
        rec_name, bound = snap["support_record"], snap["run_definition_digest"]
        rec_dir = support_root(folder) / rec_name
        definition = _read_json(rec_dir / "run-definition.json")
        digest = _definition_digest(definition)
        if digest != bound:
            raise SupportError(f"실행 정의 digest {digest} ≠ G1 결속 {bound}(지원 기록 {rec_name})")
        g0 = _read_json(rec_dir / "g0-collect.json")
        if g0.get("verdict") != "지원" or g0.get("run_definition_digest") != bound:
            raise SupportError(f"지원 기록 {rec_name} 이 «지원» 판정 · 같은 실행 정의가 아니다"
                               f"(verdict {g0.get('verdict')} · digest {g0.get('run_definition_digest')})")
        run_dir = bg._run_dir(folder)
        run_value = bg._run_value(folder)
        moved, removed = _g0_keep_exceptions(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        stamp = _run_dir_stamp(run_dir)
        started = _utc()
        reasons, info = run(repo, definition, "run", dict(os.environ), probe_out_root=run_dir / "probe" / stamp,
                            stop_on_fail=True)
        end_fp = fingerprint(repo)
        if any(r.startswith("확인 못 함 — 시간 초과 · ") for r in reasons):
            keep = ["대조 생략 — 시간 초과로 실행 증거가 불완전함"]
        else:
            keep = g0_keep({"keys": g0["keys"], "digests": g0["digests"]}, info, repo, moved, removed)
        ended = _utc()
    except (SupportError, bg.RunError, ImportError, OSError, ValueError, KeyError, TypeError) as exc:
        _say(f"실행 불능: {type(exc).__name__}: {exc}", err=True)
        _say(f"요약: suite 실행 불능 — {str(exc)[:160]}")
        return 1
    verdict = "green" if not reasons and not keep else "red"
    counts = info["counts"]
    record = {"version": 1, "run": run_value, "started": started, "ended": ended, "support_record": rec_name,
              "run_definition_digest": digest,
              "g1": {"at": at, "digest": g1_digest, "candidate": candidate, "run_definition_digest": bound,
                     "support_record": rec_name},
              "fingerprints": {"start": info["fp"][0], "between": info["fp"][1:], "end": end_fp},
              "commands": info["commands"], "counts": counts, "g0_keep": keep, "reasons": reasons, "verdict": verdict}
    _write_json(run_dir / f"suite-{stamp}.json", record)
    for r in reasons:
        _say(f"  red: {r}")
    for k in keep:
        _say(f"  red: G0 유지 — {k}")
    skipped = len(definition["argvs"]) - counts["commands"]
    if skipped:
        _say(f"  첫 실패에서 멈춤 — 돌지 않은 명령 {skipped}")
    _say(f"요약: suite {verdict} · 실행 정의 {digest} = G1 결속 · 명령 {counts['commands']}/{len(definition['argvs'])} · "
          f"선택 {counts['selected']} = 수집 {counts['collected']} · 처분 call {counts['calls']} · skip {counts['skips']} · "
          f"결과 증거 {counts['proof_ok']}/{counts['proof_total']} · 실패 보고 {counts['failed']} · 시험 기계 파일 {counts['M']} · "
          f"G0 유지 위반 {len(keep)} · 사유 {len(reasons)} · 기록 suite-{stamp}.json")
    return 0 if verdict == "green" else 2


def latest_suite_record(folder: Path) -> "dict | None":
    """그 실행의 가장 새 suite 기록(파일 이름 사전순 마지막) — 없으면 None."""
    run_dir = bg._run_dir(Path(folder))
    files = sorted(run_dir.glob("suite-*.json")) if run_dir.is_dir() else []
    if not files:
        return None
    return _read_json(files[-1])
