#!/usr/bin/env python3
"""표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱.

트리 데이터는 `standard_tree.py`(정본 171행의 기계 사본) 하나에서 온다 — 이 파일에
경로 문자열을 다시 적지 않는다. 정본이 개정되면 데이터만 갈리고 이 검사기는 그대로다.

무엇을 잡나 (규칙 번호는 트리 개정 명세):
  #486  어느 BC 를 열어도 골격이 그대로 있다 — 내용 유무 무관. 채택 저장소에서는
        `application/` 직계 전부가 BC 다(신호 없는 평면 BC 도 검사 대상).
  #488  고정(·재등장) 칸은 부모가 있으면 반드시 있다 — 폴더는 비어도 `__init__.py` 로,
        파일도 비면 빈 파일로. `<project>/`(트리 167~170행)·`framework/` 고정 서브트리에도 적용.
  #489  `<…>` 자리표시자 칸만 그 개념이 생길 때 생긴다.
  #490  BC 안에 트리에 없는 경로가 있으면 위반. 재량은 «리프로 닫은 폴더 안»의 추가
        모듈뿐이다(#15 작성자 재량) — 자리표시자 «파일» 칸이 있는 층만 파일 이름이 자유다.
  #81   BC 직계는 일곱뿐. / #429·#436  `<project>/` 직계 폐쇄(면제는 넷뿐 — `settings.py` 는 아님).
  #58 #314 #393  금지 경로(management/commands · domain_layer 의 specification · BC 안 framework).
  #395  `framework/` 의 자식은 다섯(고정 셋 + `<capability>/`·`<technology>/`) — 고정 셋의
        서브트리 존재는 #488 로 본다. 인스턴스 «내용»은 content 검사기 몫.

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드: 채택 신호는 있는데 검사할 BC 가 0이면 exit 2 (#74). 가드는 어떤
    필터보다 먼저 선다(#75).
  - 채택 신호원은 둘이다(#78): ⑴ 층 폴더 glob ⑵ Django 앱 마커.

등록 순서: 이 검사는 다른 모든 검사보다 «먼저» 돌고, 걸리면 나머지를 돌리지 않는다(#487).
내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»와 동명 폴더
승격 실현의 형태 검증(#638~#641·#643·#660·#661 · ⓓ#644 후보 신호 — 2026-09-01 · ②′ 2.30.0)만 본다.

②′ 역할 내 독립 흐름(2.30.0): 유스케이스 칸(트리 42행) 승격 폴더는 부품 종류
(`checker_target.use_case_part_kinds` — 본체 · 틀 · 흐름 부품 · 잎)로 더 본다.
  #660  의존 방향 — 부품 → 본체 import 금지(모든 42행 폴더) · ②′ 폴더의 틀 · 잎은 잎만 import ·
        부품끼리 순환 금지 · 본체 객체(`self` · 본체 메서드 · 그것을 잡는 lambda · 안쪽 함수 · partial)를
        부품(형제 클래스 생성 · 형제 모듈 함수 · 부품 메서드)에 넘기지 않음 · 부품 인자 주석이 본체 클래스로
        풀리지 않음.
  #661  (②′ 폴더만) 부품 파일 이름은 업무 낱말(금지 낱말 21 · `_frame.py` 꼬리는 틀 하나) · 부품 클래스는
        `…UseCase` 가 아니고 공개 이름 · 틀 · 부품이 바깥에 내미는 메서드는 공개 이름.
  #643  ②′ 폴더에 흐름 부품이 0(틀 · 잎만)이면 «틀 · 잎만 남음» 갈래로 낸다(부품 0 문면은 그대로).

의미 묶음(2.28.0 · D60): 묶음 허용 칸(트리 64·66·68·71·73·75행)의 하위 폴더는
`folder_group.recognize` 로 가른다 — 캐시만 남은 폴더는 건너뛰고, 서비스 칸 `D/D.py` 는 승격
(#638~#641·#643), 그 밖은 묶음이다.
  #654  묶음 안 폴더 — 묶음은 한 계층이다(서비스 칸 묶음 안 승격만 파일 하나로 센다).
  #655  묶음 `__init__.py` 없음 · 내용 있음(0바이트 · docstring · 주석뿐이 아님 — #488 과 같은 잣대).
  묶음 안 파일도 부모 칸의 파일 모양(#490) · 서비스 칸이면 ⓓ#644 신호를 진다. 자리(#656)는
  `check-domain-model` 몫이다.

사용법: check-layer-skeleton.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#10 → djr:R-3196 · rule#58 → djr:R-3210 ·
  rule#74 → djr:R-3229 · rule#314 → djr:R-3212 · rule#436 → djr:R-3220 · rule#487 → djr:R-3178 ·
  rule#488 → djr:R-3181 · rule#489 → djr:R-3182 · rule#491 → djr:R-3186.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import ast as _ast
import re
import sys

import checker_target
import folder_group
from findings import Candidates, Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
IGNORE_FILES = {"__init__.py", ".DS_Store"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
PROJECT_ALLOWED = {"api.py", "urls.py", "celery.py", "settings"}
PROJECT_EXEMPT = {"health.py", "home.py", "asgi.py", "wsgi.py", "__init__.py"}
PROJECT_REQUIRED_FILES = ("api.py", "urls.py", "celery.py")  # 트리 167~169행 fixed (#488)

NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
TOKEN = re.compile(r"<([a-z_]+)>")


def _entries(d: Path) -> tuple[list[Path], list[Path]]:
    dirs, files = [], []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or p.name in SKIP_DIRS:
            continue
        if p.is_dir():
            dirs.append(p)
        elif p.name not in IGNORE_FILES and not p.name.endswith(".pyc"):
            files.append(p)
    return dirs, files


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78): 층 폴더 또는 Django 앱 마커."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


# ── 동명 폴더 승격(#490 교체형) — #638~#641·#643 + ⓓ#644 ─────────────────────────

# ⓓ#644 행위 칸 로스터 — 승격 허용 표기(swappable) 중 schema 4행(15·16·21·22) 제외
# (houserules SKILL §1 감사 주도 배정 — 신호는 무조건 방출, 판정 의무의 diff 한정은 감사자 몫)
PROMO_ACTION_ROWS = frozenset({13, 19, 25, 42, 62, 75, 93, 95, 97})
PROMO_SIGNAL_LINES = 200   # ⓓ#644 후보 문턱(물리 행·빈 줄 제외)
JUNK_DRAWER_NAMES = frozenset({"utils.py", "helpers.py", "util.py", "helper.py", "common.py", "misc.py"})
_CASCADE_Q = "역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)"


def _phys_lines(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return 0
    return sum(1 for line in text.splitlines() if line.strip())


def _init_reexport_only(path: Path) -> bool:
    """`__init__.py` 가 재수출 전용인가 — docstring · `from .<모듈> import <이름> as <이름>` · `__all__` 만."""
    try:
        mod = _ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return False
    for i, node in enumerate(mod.body):
        if i == 0 and isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Constant) \
                and isinstance(node.value.value, str):
            continue
        if isinstance(node, _ast.ImportFrom) and node.level >= 1:
            continue
        if isinstance(node, _ast.Assign) and all(
                isinstance(tg, _ast.Name) and tg.id == "__all__" for tg in node.targets):
            continue
        if isinstance(node, _ast.AnnAssign) and isinstance(node.target, _ast.Name) \
                and node.target.id == "__all__":
            continue
        return False
    return True


def _check_promoted(dir_path: Path, crow: "tree.Row", out: Findings, cand: Candidates) -> None:
    """유효한 동명 폴더 승격의 형태 검증(#638~#641·#643) + 행위 칸 ⓓ#644 신호.

    유스케이스 칸(트리 42행)이면 부품 종류(`checker_target.use_case_part_kinds`)로 #660 · #661 과
    ②′ 폴더의 #643(틀 · 잎만 남음)을 더 본다.
    """
    body = dir_path / (dir_path.name + ".py")
    init = dir_path / "__init__.py"
    kinds = checker_target.use_case_part_kinds(dir_path) if crow.r == _USE_CASE_ROW else None
    if not body.is_file():
        out.add("#638", dir_path, f"승격 폴더에 본체 `{dir_path.name}.py` 가 없다 — 위장 (트리 {crow.r}행)")
    if not init.is_file():
        out.add("#638", init, "승격 폴더에 재수출 전용 `__init__.py` 가 없다")
    elif not _init_reexport_only(init):
        out.add("#640", init, "`__init__.py` 는 재수출 전용이다 — from-as 재수출·`__all__`·docstring 밖 코드 동거 금지")
    subdirs, files = _entries(dir_path)
    for sd in subdirs:
        out.add("#641", sd, "승격 폴더 내부는 1단 평평이다 — 부품 군집의 폴더 요구는 트리 개정 신호이지 중첩 근거가 아니다")
    parts = [f for f in files if f.name not in ("__init__.py", dir_path.name + ".py")]
    for f in parts:
        if f.name in JUNK_DRAWER_NAMES:
            out.add("#640", f, "승격 폴더 안 정크드로어 이름 — 부품은 응집 단위의 이름을 가진다")
        n = _phys_lines(f)
        if crow.r in PROMO_ACTION_ROWS and n > PROMO_SIGNAL_LINES:
            cand.add("#644", f, f"행위 칸 승격 부품 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
    if body.is_file():
        if not parts:
            out.add("#643", dir_path, "부품 0개(본체+`__init__.py` 뿐)인 승격 폴더 — 환원 신호(파일 실현으로 되돌린다)")
        elif kinds is not None and _split(kinds) and not kinds.flow_parts:
            out.add("#643", dir_path, "틀 · 잎만 남은 ②′ 폴더 — 흐름 부품 0 · 환원 신호(파일 실현으로 되돌린다)")
        if crow.r in PROMO_ACTION_ROWS:
            n = _phys_lines(body)
            if n > PROMO_SIGNAL_LINES:
                cand.add("#644", body, f"행위 칸 실현 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
    if kinds is not None:
        _check_use_case_parts(kinds, out)


# ── 유스케이스 칸 승격 폴더(트리 42행) — #660 의존 방향 · #661 이름 · 공개 이름 ──────────────────
#
# 부품 종류는 `checker_target.use_case_part_kinds` 한곳이 가른다: 본체 · 틀(`<x>_frame.py`) ·
# 흐름 부품(본체 `__init__` 이 만들어 속성에 대입하는 형제 클래스의 모듈 — 갈래 · 단계) · 잎(나머지).
# ②′ 폴더 = 틀이 있거나 흐름 부품이 하나 이상. 기존 ② 폴더(틀 · 흐름 부품 없음)는 부품 → 본체 ·
# 순환 · 본체 객체 넘김만 본다.
#   #660  부품 → 본체 import(`TYPE_CHECKING` 아래 · 함수 안 · 절대 경로 포함) · (②′) 틀 · 잎 → 틀 · 흐름
#         부품 import · 부품끼리 순환(강한 연결 성분 하나에 한 줄) · 본체가 받는 호출(형제 클래스 생성 ·
#         형제 모듈 함수 호출(`from` import 한 이름 · 모듈 참조 `m.<함수 · 클래스>`) ·
#         `self.<부품 속성>.<메서드>(…)`)에 본체 객체를 넘김(`self` · 본체 메서드 · `self` 를 잡는 lambda ·
#         `self` 를 쓰는 안쪽 함수 · 그것을 품은 `partial`) · 부품 함수 인자 주석이 본체 클래스로 풀림.
#   #661  (②′ 폴더만) 부품 파일 이름의 금지 낱말 · `_frame.py` 꼬리는 틀 하나(`<x>_frame.py`) ·
#         부품 클래스 `…UseCase` · `_` 부품 클래스 · 틀 · 부품의 `_` 메서드를 바깥에서 부름.

_USE_CASE_ROW = 42
_PART_WORDS = frozenset({
    "common", "shared", "base", "core", "util", "utils", "helper", "helpers", "misc", "manager", "handler",
    "handlers", "mixin", "part", "parts", "branch", "branches", "step", "steps", "tools", "frame",
})
_FRAME_TAIL = "_frame.py"
_BODY_TOOL = "본체 도구는 틀 부품의 공개 메서드로"
_LEAF_FIX = "함께 쓰는 정의는 잎으로"
_FUNCS = (_ast.FunctionDef, _ast.AsyncFunctionDef)
_NOT_BOUND = frozenset({"staticmethod", "property", "cached_property", "setter", "getter", "deleter"})


def _split(kinds: "checker_target.UseCasePartKinds") -> bool:
    """②′ 판정이 서는가 — 본체 클래스를 못 가리면(입구 `execute` 없는 공개 클래스 둘 이상) 흐름 부품을 셀 수
    없어 모든 형제가 잎으로 보이므로 ②′ 판정(틀 · 잎 → 틀 · 흐름 부품 · #661 · #643 ②′ 갈래)을 건너뛴다."""
    return kinds.is_split and kinds.body_class is not None


def _parse_py(path: Path) -> "_ast.Module | None":
    try:
        return _ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError, ValueError):
        return None


def _sibling_imports(mod: "_ast.Module", folder: Path, stems: "dict[str, Path]") -> "list[tuple[int, Path]]":
    """모듈이 import 하는 형제 파일 — (줄, 형제) · 같은 줄의 같은 형제는 한 번."""
    found: "list[tuple[int, Path]]" = []
    for node in _ast.walk(mod):  # import 간선 — 함수 안 · `if TYPE_CHECKING:` 아래도 센다
        if isinstance(node, _ast.ImportFrom):
            stem = checker_target.sibling_stem(node, folder)
            names: "list[str]" = [stem] if stem is not None else checker_target.sibling_module_imports(node, folder)
        elif isinstance(node, _ast.Import):
            names = checker_target.sibling_module_imports(node, folder)
        else:
            continue
        for name in names:
            hit = (node.lineno, stems[name]) if name in stems else None
            if hit is not None and hit not in found:
                found.append(hit)
    return found


def _part_kind(kinds: "checker_target.UseCasePartKinds", path: Path) -> str:
    if path == kinds.body:
        return "본체"
    if path == kinds.frame:
        return "틀 부품"
    return "흐름 부품" if path in kinds.flow_parts else "잎"


def _reachable(start: Path, succ: "dict[Path, list[Path]]") -> "set[Path]":
    seen: "set[Path]" = set()
    stack: "list[Path]" = list(succ.get(start, []))
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(succ.get(node, []))
    return seen


def _check_import_direction(kinds: "checker_target.UseCasePartKinds", mods: "dict[Path, _ast.Module]",
                            out: Findings) -> None:
    """#660 import 방향 — 부품 → 본체 · (②′) 틀 · 잎 → 틀 · 흐름 부품 · 부품끼리 순환."""
    folder = kinds.body.parent
    stems: "dict[str, Path]" = {p.stem: p for p in mods}
    edges: "set[tuple[Path, Path]]" = set()
    for src, mod in sorted(mods.items()):
        if src == kinds.body:
            continue
        for lineno, dst in _sibling_imports(mod, folder, stems):
            if dst == src:
                continue
            if dst == kinds.body:
                out.add("#660", f"{src}:{lineno}", f"부품이 본체 `{dst.name}` 를 import 한다 — 의존은 본체 → 갈래 → 단계"
                        f" → 틀 → 잎 한 방향이다(`TYPE_CHECKING` 아래 · 함수 안 포함) — 타입은 잎 모듈로 · {_BODY_TOOL}")
            elif _split(kinds) and _part_kind(kinds, src) in ("틀 부품", "잎") \
                    and _part_kind(kinds, dst) in ("틀 부품", "흐름 부품"):
                out.add("#660", f"{src}:{lineno}", f"{_part_kind(kinds, src)}이 {_part_kind(kinds, dst)} `{dst.name}` 를"
                        f" import 한다 — ②′ 폴더의 틀 · 잎은 잎만 import 한다(틀은 갈래 · 단계를 모른다) — {_LEAF_FIX}")
            else:
                edges.add((src, dst))
    succ: "dict[Path, list[Path]]" = {}
    for src, dst in sorted(edges):
        succ.setdefault(src, []).append(dst)
    reach: "dict[Path, set[Path]]" = {p: _reachable(p, succ) for p in succ}
    done: "set[Path]" = set()
    for node in sorted(succ):
        component = sorted(p for p in reach[node] if p in reach and node in reach[p])
        if len(component) < 2 or node in done:
            continue
        done.update(component)
        names = " · ".join(f"`{p.name}`" for p in component)
        out.add("#660", folder, f"부품끼리 import 순환({names}) — 부품 사이 의존은 한 방향이다(단계 → 단계도 순환 없이) — {_LEAF_FIX}")


def _uses_name(node: "_ast.AST", name: str) -> bool:
    return any(isinstance(n, _ast.Name) and n.id == name for n in _ast.walk(node))


def _decorator_names(fn: "_ast.AST") -> "set[str]":
    names: "set[str]" = set()
    for dec in getattr(fn, "decorator_list", []):
        target = dec.func if isinstance(dec, _ast.Call) else dec
        if isinstance(target, _ast.Name):
            names.add(target.id)
        elif isinstance(target, _ast.Attribute):
            names.add(target.attr)
    return names


def _body_object(arg: "_ast.AST", me: str, methods: "set[str]") -> "str | None":
    """인자가 본체 객체 자체(`self`)이거나 본체 메서드(`self.m`)면 그 꼴의 이름."""
    if isinstance(arg, _ast.Name) and arg.id == me:
        return f"본체 객체 `{me}`"
    if isinstance(arg, _ast.Attribute) and isinstance(arg.value, _ast.Name) and arg.value.id == me \
            and arg.attr in methods:
        return f"본체 메서드 `{me}.{arg.attr}`"
    return None


def _passed_body(arg: "_ast.AST", me: str, methods: "set[str]", inner: "set[str]") -> "str | None":
    """인자가 실행 때 본체로 되돌아오는 고리인가 — 다섯 꼴(본체 객체 · 본체 메서드 · lambda · 안쪽 함수 · partial)."""
    direct = _body_object(arg, me, methods)
    if direct is not None:
        return direct
    if isinstance(arg, _ast.Lambda) and _uses_name(arg.body, me):
        return f"`{me}` 를 잡는 `lambda`"
    if isinstance(arg, _ast.Name) and arg.id in inner:
        return f"`{me}` 를 쓰는 안쪽 함수 `{arg.id}`"
    if isinstance(arg, _ast.Call):
        func = arg.func
        partial = (isinstance(func, _ast.Name) and func.id == "partial") or (
            isinstance(func, _ast.Attribute) and func.attr == "partial"
            and isinstance(func.value, _ast.Name) and func.value.id == "functools")
        packed: "list[_ast.AST]" = list(arg.args) + [kw.value for kw in arg.keywords]
        if partial and any(_body_object(a, me, methods) is not None for a in packed):
            return "본체를 품은 `partial(…)`"
    return None


def _class_def(mod: "_ast.Module | None", name: "str | None") -> "_ast.ClassDef | None":
    if mod is None or name is None:
        return None
    return next((n for n in mod.body if isinstance(n, _ast.ClassDef) and n.name == name), None)


def _top_callable(mod: "_ast.Module", name: str) -> bool:
    """모듈 맨 위에 클래스나 함수로 정의된 이름인가."""
    return any(isinstance(n, (_ast.ClassDef,) + _FUNCS) and n.name == name for n in mod.body)


def _dotted(node: "_ast.AST") -> "str | None":
    """`a` · `a.b.c` 꼴 이름 사슬의 점 경로 — 다른 꼴은 None."""
    if isinstance(node, _ast.Name):
        return node.id
    if isinstance(node, _ast.Attribute):
        head = _dotted(node.value)
        return None if head is None else f"{head}.{node.attr}"
    return None


def _sibling_receivers(kinds: "checker_target.UseCasePartKinds",
                       mods: "dict[Path, _ast.Module]") -> "tuple[set[str], dict[str, Path]]":
    """본체가 형제 모듈에서 들인 받는 쪽 — (형제 맨 위 클래스 · 함수를 `from <형제> import <이름>` 으로 들인 지역
    이름, 형제 모듈 자체를 가리키는 지역 참조 → 형제). 모듈 참조는 `from . import <형제>` · `from <…>.<폴더> import
    <형제>` 의 (별칭) 이름 · `import <…>.<형제> as m` 의 `m` · 별칭 없는 `import <…>.<형제>` 의 점 경로다."""
    folder = kinds.body.parent
    stems: "dict[str, Path]" = {p.stem: p for p in mods}
    local: "set[str]" = set()
    modules: "dict[str, Path]" = {}
    for node in _ast.walk(mods[kinds.body]):
        if isinstance(node, _ast.ImportFrom):
            stem = checker_target.sibling_stem(node, folder)
            if stem is not None:
                sibling = stems.get(stem)
                if sibling is None or sibling == kinds.body:
                    continue
                local |= {a.asname or a.name for a in node.names if _top_callable(mods[sibling], a.name)}
                continue
            for alias in node.names:  # 이름 하나씩 — 형제 모듈인 이름만 지역 참조로
                one = _ast.ImportFrom(module=node.module, names=[alias], level=node.level)
                for name in checker_target.sibling_module_imports(one, folder):
                    if stems.get(name) not in (None, kinds.body):
                        modules[alias.asname or alias.name] = stems[name]
        elif isinstance(node, _ast.Import):
            for alias in node.names:
                for name in checker_target.sibling_module_imports(_ast.Import(names=[alias]), folder):
                    if stems.get(name) not in (None, kinds.body):
                        modules[alias.asname or alias.name] = stems[name]
    return local, modules


def _check_body_passing(kinds: "checker_target.UseCasePartKinds", mods: "dict[Path, _ast.Module]",
                        out: Findings) -> None:
    """#660 본체가 받는 호출(형제 클래스 생성 · 형제 모듈 함수 호출 · `self.<부품 속성>.<메서드>(…)`)에 본체 객체를
    넘김. 형제는 `from <형제> import <이름>` 의 이름이나 모듈 참조(`m.<클래스 · 함수>(…)`)로 부른다."""
    cls = _class_def(mods.get(kinds.body), kinds.body_class)
    if cls is None:
        return
    methods: "set[str]" = {n.name for n in cls.body if isinstance(n, _FUNCS) and not _decorator_names(n) & _NOT_BOUND}
    receivers, sibling_refs = _sibling_receivers(kinds, mods)
    for fn in cls.body:
        if not isinstance(fn, _FUNCS) or not fn.args.args or {"staticmethod", "classmethod"} & _decorator_names(fn):
            continue
        me = fn.args.args[0].arg
        inner: "set[str]" = {n.name for n in _ast.walk(fn) if n is not fn and isinstance(n, _FUNCS) and _uses_name(n, me)}
        for call in _ast.walk(fn):
            if not isinstance(call, _ast.Call):
                continue
            func = call.func
            ref = _dotted(func.value) if isinstance(func, _ast.Attribute) else None
            if isinstance(func, _ast.Name) and func.id in receivers:
                callee = f"{func.id}(…)"
            elif ref in sibling_refs and _top_callable(mods[sibling_refs[ref]], func.attr):
                callee = f"{ref}.{func.attr}(…)"
            elif isinstance(func, _ast.Attribute) and isinstance(func.value, _ast.Attribute) \
                    and isinstance(func.value.value, _ast.Name) and func.value.value.id == me \
                    and func.value.attr in kinds.part_attrs:
                callee = f"{me}.{func.value.attr}.{func.attr}(…)"
            else:
                continue
            slots: "list[tuple[_ast.AST, str]]" = [(a, "위치 인자") for a in call.args]
            slots += [(kw.value, f"`{kw.arg}=` 인자") for kw in call.keywords if kw.arg is not None]
            for arg, slot in slots:
                what = _passed_body(arg, me, methods, inner)
                if what is not None:
                    out.add("#660", f"{kinds.body}:{arg.lineno}", f"본체가 `{callee}` 의 {slot}로 {what} 를 넘긴다 — 실행 때"
                            f" 부품 → 본체 호출 고리다(부품이 Protocol 로 받아도 같다) — {_BODY_TOOL}")


def _annotation_names(node: "_ast.AST | None") -> "set[str]":
    names: "set[str]" = set()
    if node is None:
        return names
    for n in _ast.walk(node):
        if isinstance(n, _ast.Name):
            names.add(n.id)
        elif isinstance(n, _ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, _ast.Constant) and isinstance(n.value, str):
            try:
                names |= _annotation_names(_ast.parse(n.value, mode="eval").body)
            except (SyntaxError, ValueError):
                pass
    return names


def _module_functions(mod: "_ast.Module") -> "list[tuple[str, _ast.AST]]":
    """맨 위 함수와 맨 위 클래스의 메서드 — (보이는 이름, 함수)."""
    found: "list[tuple[str, _ast.AST]]" = []
    for node in mod.body:
        if isinstance(node, _FUNCS):
            found.append((node.name, node))
        elif isinstance(node, _ast.ClassDef):
            found += [(f"{node.name}.{fn.name}", fn) for fn in node.body if isinstance(fn, _FUNCS)]
    return found


def _check_body_annotations(kinds: "checker_target.UseCasePartKinds", mods: "dict[Path, _ast.Module]",
                            out: Findings) -> None:
    """#660 부품 함수의 인자 주석이 본체 클래스로 풀림(문자열 주석 · 본체 모듈에서 가져온 별칭 포함)."""
    if kinds.body_class is None:
        return
    folder = kinds.body.parent
    for path, mod in sorted(mods.items()):
        if path == kinds.body:
            continue
        names: "set[str]" = {kinds.body_class}
        for node in _ast.walk(mod):
            if isinstance(node, _ast.ImportFrom) and checker_target.sibling_stem(node, folder) == kinds.body.stem:
                names |= {a.asname or a.name for a in node.names if a.name == kinds.body_class}
        for owner, fn in _module_functions(mod):
            a = fn.args
            for arg in a.posonlyargs + a.args + a.kwonlyargs + [x for x in (a.vararg, a.kwarg) if x is not None]:
                if _annotation_names(arg.annotation) & names:
                    out.add("#660", f"{path}:{arg.lineno}", f"부품 `{owner}` 의 인자 `{arg.arg}` 주석이 본체 클래스"
                            f" `{kinds.body_class}` 로 풀린다 — 본체 객체를 부품에 넘기지 않는다(Protocol 로 받아도 같다)"
                            f" — {_BODY_TOOL}")


def _check_part_names(kinds: "checker_target.UseCasePartKinds", mods: "dict[Path, _ast.Module]",
                      out: Findings) -> None:
    """#661 부품 파일 이름 · `_frame.py` 꼬리 · 부품 클래스 이름(`…UseCase` · `_` 시작)."""
    folder = kinds.body.parent
    want = folder.name[: -len("_use_case")] + _FRAME_TAIL
    files: "list[Path]" = sorted(
        kinds.flow_parts | kinds.leaves | ({kinds.frame} if kinds.frame is not None else frozenset()))
    for path in files:
        if path.name.endswith(_FRAME_TAIL) or path.name in JUNK_DRAWER_NAMES:
            continue
        words: "list[str]" = []
        for w in path.stem.split("_"):
            if w in _PART_WORDS and w not in words:
                words.append(w)
        if words:
            listed = " · ".join(f"`{w}`" for w in words)
            out.add("#661", path, f"②′ 부품 파일 이름에 금지 낱말 {listed} — 부품 이름은 업무 낱말이다(틀 부품만 `{want}`)")
    tails: "list[Path]" = [p for p in files if p.name.endswith(_FRAME_TAIL)]
    if len(tails) > 1:
        listed = " · ".join(f"`{p.name}`" for p in tails)
        out.add("#661", folder, f"`{_FRAME_TAIL}` 꼬리 파일이 {len(tails)}개({listed}) — 틀 부품은 폴더에 하나이고 이름은 `{want}` 다")
    elif tails and tails[0].name != want:
        out.add("#661", tails[0], f"틀 부품 이름은 `{want}` 다 — `{_FRAME_TAIL}` 꼬리는 틀 부품의 고정 이름에만 쓴다")
    for name, module in sorted(kinds.part_classes.items()):
        node = _class_def(mods.get(module), name)
        where = f"{module}:{node.lineno}" if node is not None else str(module)
        if name.endswith("UseCase"):
            out.add("#661", where, f"부품 클래스 `{name}` 가 `UseCase` 로 끝난다 — 부품은 유스케이스가 아니다"
                    "(유스케이스는 본체 하나 · 입구 `execute` 하나)")
        if name.startswith("_"):
            out.add("#661", where, f"부품 클래스 `{name}` 가 `_` 로 시작한다 — 부품 클래스는 공개 이름이다"
                    "(폴더 밖 비공개는 재수출하지 않음과 바깥 import 금지가 지킨다) — 본체 `__init__` 이 만들어"
                    " `self` 에 두는 형제 클래스는 ②′ 부품이다(② 로 두려면 `execute` 안에서 만든다)")


def _private(name: str) -> bool:
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


def _defined_names(mod: "_ast.Module") -> "set[str]":
    """맨 위 함수 · 클래스 이름과 맨 위 클래스의 메서드 이름."""
    names: "set[str]" = set()
    for node in mod.body:
        if isinstance(node, (_ast.ClassDef,) + _FUNCS):
            names.add(node.name)
        if isinstance(node, _ast.ClassDef):
            names |= {fn.name for fn in node.body if isinstance(fn, _FUNCS)}
    return names


def _private_methods(mod: "_ast.Module | None", class_name: "str | None" = None) -> "set[str]":
    """맨 위 클래스(이름을 주면 그 클래스만)의 `_` 메서드 이름 — dunder 제외."""
    if mod is None:
        return set()
    return {fn.name for node in mod.body if isinstance(node, _ast.ClassDef) and class_name in (None, node.name)
            for fn in node.body if isinstance(fn, _FUNCS) and _private(fn.name)}


def _check_public_calls(kinds: "checker_target.UseCasePartKinds", mods: "dict[Path, _ast.Module]",
                        out: Findings) -> None:
    """#661 ⓑ 받는 쪽 셋 — 흐름 부품 · 본체가 부르는 틀 `_` 메서드 · 본체가 `self.<부품 속성>.<_m>` 으로 닿는
    그 부품 클래스의 `_` 메서드(자기 `self._m` · 잎이 정의했거나 잎에서 가져온 이름은 셈 밖)."""
    folder = kinds.body.parent
    leaf_stems: "set[str]" = {p.stem for p in kinds.leaves}
    leaf_names: "set[str]" = set()
    for path in kinds.leaves:
        if path in mods:
            leaf_names |= _defined_names(mods[path])
    for mod in mods.values():
        for node in _ast.walk(mod):
            if isinstance(node, _ast.ImportFrom) and checker_target.sibling_stem(node, folder) in leaf_stems:
                leaf_names |= {a.asname or a.name for a in node.names}
    frame_private: "set[str]" = _private_methods(mods.get(kinds.frame) if kinds.frame is not None else None) - leaf_names
    for path in sorted(p for p in mods if p == kinds.body or p in kinds.flow_parts):
        who = "본체가" if path == kinds.body else "흐름 부품이"
        seen: "set[str]" = set()
        attrs: "list[_ast.Attribute]" = sorted(
            (n for n in _ast.walk(mods[path]) if isinstance(n, _ast.Attribute)), key=lambda n: (n.lineno, n.col_offset))
        for node in attrs:  # 소스 차례 — 같은 이름은 첫 자리 한 줄
            if isinstance(node.value, _ast.Name) and node.value.id == "self":
                continue
            recv = node.value
            hit = kinds.part_attrs.get(recv.attr) if path == kinds.body and isinstance(recv, _ast.Attribute) \
                and isinstance(recv.value, _ast.Name) and recv.value.id == "self" else None
            if hit is not None and hit[1] != kinds.frame:
                shown = f"self.{recv.attr}.{node.attr}"
                if shown not in seen and node.attr not in leaf_names \
                        and node.attr in _private_methods(mods.get(hit[1]), hit[0]):
                    seen.add(shown)
                    out.add("#661", f"{path}:{node.lineno}", f"본체가 부품 메서드 `{shown}` 를 부른다 — 부품 계약은 공개 이름이다(앞 `_` 없음)")
            elif node.attr in frame_private and node.attr not in seen:
                seen.add(node.attr)
                out.add("#661", f"{path}:{node.lineno}", f"{who} 틀 메서드 `{node.attr}` 를 부른다 — 틀 계약은 공개 이름이다(앞 `_` 없음)")


def _check_use_case_parts(kinds: "checker_target.UseCasePartKinds", out: Findings) -> None:
    """유스케이스 칸 승격 폴더의 #660(모든 42행 폴더) · #661(②′ 폴더만)."""
    files: "list[Path]" = [kinds.body] + sorted(
        kinds.flow_parts | kinds.leaves | ({kinds.frame} if kinds.frame is not None else frozenset()))
    mods: "dict[Path, _ast.Module]" = {}
    for path in files:
        mod = _parse_py(path)
        if mod is not None:
            mods[path] = mod
    if kinds.body not in mods:
        return
    _check_import_direction(kinds, mods, out)
    _check_body_passing(kinds, mods, out)
    _check_body_annotations(kinds, mods, out)
    if not _split(kinds):
        return
    _check_part_names(kinds, mods, out)
    _check_public_calls(kinds, mods, out)


def _check_group(group: Path, crow: "tree.Row", file_patterns: "list[str]", out: Findings,
                 cand: Candidates) -> None:
    """묶음 폴더(설계 7.1 · 7.4 — #654 · #655 · 파일 폐쇄 · ⓓ#644). 자리(#656)는 domain-model 이 본다."""
    init = group / "__init__.py"
    if not init.is_file():
        out.add("#655", init, "묶음 폴더에 `__init__.py` 가 없다 — 비워 둔다(0바이트 · docstring · 주석뿐)")
    elif not checker_target.skeleton_placeholder(init):
        out.add("#655", init, "묶음 `__init__.py` 는 내용이 없다 — 0바이트 · docstring · 주석뿐(재수출 · 코드를 두지 않는다)")
    subdirs, files = _entries(group)
    for sd in subdirs:
        kind = folder_group.recognize(sd, crow.r)
        if kind == "cache":
            continue
        if kind == "promotion":
            if (group / (sd.name + ".py")).is_file():
                out.add("#639", sd, f"형제 `{sd.name}.py` 와 승격 폴더의 공존 — import 는 패키지가 이겨 조용한 위장 중복이다")
            _check_promoted(sd, crow, out, cand)
            continue
        out.add("#654", sd, "묶음 안 폴더 — 묶음은 한 계층이다(서비스 칸 묶음 안 승격만 파일 하나로 센다)")
    for f in files:
        if not any(_file_pattern_ok(f.name, pat) for pat in file_patterns):
            out.add("#490", f, "묶음 안 파일이 부모 칸의 파일 모양이 아니다 — 트리에 없는 경로")
            continue
        if crow.r in PROMO_ACTION_ROWS:
            n = _phys_lines(f)
            if n > PROMO_SIGNAL_LINES:
                cand.add("#644", f, f"행위 칸 실현 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)


# ── 트리 대조 재귀 ──────────────────────────────────────────────────────────

def _segments(row: "tree.Row") -> list[str]:
    return row.name.rstrip("/").split("/")


def _file_pattern_ok(name: str, pattern: str) -> bool:
    """`<form>_form.py` 같은 마지막 마디 패턴과 대조 — `<tok>` 는 비지 않은 아무 이름."""
    rx = TOKEN.sub("(.+)", re.escape(pattern))
    return re.fullmatch(rx, name) is not None


def _check_multi(dir_path: Path, shapes: list[list[str]], out: Findings) -> None:
    """하위 경로를 품은 행(form/·feature/·templates/ …)의 «모양» 검사 — 트리 86~89행.

    shapes 는 남은 마디 목록들이다. 마지막 마디는 파일 패턴, 그 앞은 폴더 마디
    (`<tok>` 마디는 아무 이름). 어느 모양에도 안 맞는 항목은 트리에 없는 경로다(#490).
    """
    dirs, files = _entries(dir_path)
    for f in files:
        ok = any(len(s) == 1 and _file_pattern_ok(f.name, s[0]) for s in shapes)
        if not ok:
            out.add("#490", f, "이 자리의 파일 모양이 아니다 — 트리에 없는 경로")
    for p in dirs:
        nexts = [s[1:] for s in shapes if len(s) > 1 and (TOKEN.search(s[0]) or s[0] == p.name)]
        if nexts:
            _check_multi(p, nexts, out)
        else:
            out.add("#490", p, "트리에 없는 칸이다 — 반환")


def _check_level(dir_path: Path, row: "tree.Row", bindings: dict[str, str], out: Findings,
                 cand: Candidates, skip: frozenset[str] = frozenset()) -> None:
    """row(폴더 칸)의 실제 디렉터리 dir_path 를 트리 기대와 대조하고 재귀한다."""
    kids = tree.children(row)
    if checker_target.adapter_bundle(dir_path) or checker_target.adapter_bundle(dir_path.parent):
        init = dir_path / "__init__.py"
        if init.is_file() and not _init_reexport_only(init):
            out.add("#640", init, "어댑터 패키지의 `__init__.py` 는 재수출 전용이다")
    if not kids:  # 트리가 리프로 닫은 폴더 — 안은 작성자 재량(#490·#15)
        return

    fixed_dirs: dict[str, "tree.Row"] = {}
    fixed_files: dict[str, "tree.Row"] = {}
    dir_placeholder: "tree.Row | None" = None
    has_file_placeholder = False  # 자리표시자 «파일» 칸 — 이것이 있어야만 파일 이름이 자유다(#490)
    file_placeholders: "list[tree.Row]" = []  # 승격(#490 교체형)·ⓓ#644 신호의 칸 대조용
    multi_shapes: dict[str, list[list[str]]] = {}

    for c in kids:
        segs = _segments(c)
        if len(segs) > 1:
            multi_shapes.setdefault(segs[0], []).append(segs[1:] if not tree.is_dir(c) else segs[1:])
            continue
        if tree.is_dir(c):
            if c.kind in ("fixed", "reappear"):
                fixed_dirs[tree.concrete_name(c, bindings).rstrip("/")] = c
            else:
                dir_placeholder = c
        else:
            if c.kind in ("fixed", "reappear"):
                fixed_files[tree.concrete_name(c, bindings)] = c
            else:
                has_file_placeholder = True
                file_placeholders.append(c)

    dirs, files = _entries(dir_path)
    dirs = [p for p in dirs if p.name not in skip]
    files = [p for p in files if p.name not in skip]
    dir_names = {p.name for p in dirs}

    # #488 — 고정 칸은 부모가 있으면 반드시 있다
    for name, crow in fixed_dirs.items():
        sub = dir_path / name
        if not sub.is_dir():
            out.add("#488", sub, f"고정 칸 `{name}/` 부재 — 비어도 `__init__.py` 로 만든다 (트리 {crow.r}행)")
            continue
        if not (sub / "__init__.py").is_file():
            missing = sub / "__init__.py" if checker_target.adapter_bundle(dir_path) else sub
            out.add("#488", missing, "고정 칸 폴더에 `__init__.py` 가 없다")
        _check_level(sub, crow, bindings, out, cand)
    for name, crow in fixed_files.items():
        target = dir_path / name
        promo = dir_path / name[:-3] if name.endswith(".py") else None
        if target.is_file():
            continue
        if getattr(crow, "swappable", False) and promo is not None and promo.is_dir() \
                and (promo / name).is_file():
            continue  # 유효한 승격 실현이 #488 충족이다(형태 검증은 dir 루프의 #638~#641·#643)
        out.add("#488", target, f"고정 파일 부재 — 비면 빈 파일로 만든다 (트리 {crow.r}행)")

    # #490 — 폴더 폐쇄: 칸이 아닌 폴더는 위반. 자리표시자 폴더가 있으면 나머지는 인스턴스다.
    if row.name.startswith("migrations"):
        for p in dirs:  # <migration>.py 는 파일 자리 — 폴더는 트리에 없는 경로다
            out.add("#490", p, "`migrations/` 아래 폴더는 트리에 없는 경로다")
        return
    for p in dirs:
        if p.name in fixed_dirs:
            continue
        if p.name in multi_shapes:
            _check_multi(p, multi_shapes[p.name], out)
            continue
        kan_row = fixed_files.get(p.name + ".py")
        if kan_row is None:
            for fp in file_placeholders:
                if _file_pattern_ok(p.name + ".py", tree.concrete_name(fp, bindings)):
                    kan_row = fp
                    break
        if kan_row is not None and getattr(kan_row, "groupable", False):
            # 묶음 허용 칸의 하위 폴더 — 캐시만 · 승격 · 묶음으로 가른다(설계 7.1)
            kind = folder_group.recognize(p, kan_row.r)
            if kind == "cache":
                continue
            if kind == "promotion":
                if (dir_path / (p.name + ".py")).is_file():
                    out.add("#639", p, f"형제 `{p.name}.py` 와 승격 폴더의 공존 — import 는 패키지가 이겨 조용한 위장 중복이다")
                _check_promoted(p, kan_row, out, cand)
            else:
                _check_group(p, kan_row, [tree.concrete_name(fp, bindings) for fp in file_placeholders], out, cand)
            continue
        if kan_row is not None:  # 파일 칸의 동명 폴더 — 승격 허용 여부로 갈린다(#490 교체형)
            if getattr(kan_row, "swappable", False):
                if (dir_path / (p.name + ".py")).is_file():
                    out.add("#639", p, f"형제 `{p.name}.py` 와 승격 폴더의 공존 — import 는 패키지가 이겨 조용한 위장 중복이다")
                _check_promoted(p, kan_row, out, cand)
            else:
                out.add("#490", p, f"승격 배제 칸의 동명 폴더 — 이 칸은 파일 실현만 갖는다 (트리 {kan_row.r}행)")
            continue
        if dir_placeholder is not None:
            inst_bind = dict(bindings)
            pattern = dir_placeholder.name.rstrip("/")
            if (not pattern.endswith("_adapter") or _file_pattern_ok(p.name, pattern)) \
                    and checker_target.cache_only_instance(p):
                continue
            if pattern.endswith("_adapter"):
                if not _file_pattern_ok(p.name, pattern):
                    out.add("#490", p, "어댑터 패키지 이름은 `<이름>_adapter/` 다")
                    continue
                if not (p / "__init__.py").is_file():
                    out.add("#488", p / "__init__.py", "어댑터 패키지에 `__init__.py` 가 없다")
            for tok in set(TOKEN.findall(dir_placeholder.name)):
                inst_bind[tok] = p.name.removesuffix("_adapter") if pattern.endswith("_adapter") else p.name
            _check_level(p, dir_placeholder, inst_bind, out, cand)
        elif p.name == "commands" and dir_path.name == "management":
            out.add("#58", p, "`management/commands/` 를 만들지 않는다")
        else:
            out.add("#490", p, "트리에 없는 칸이다 — 반환")

    # ⓓ#644 — 행위 칸 «파일 실현»의 캐스케이드 후보 신호(무조건 방출 — diff 한정은 감사자 몫)
    for f in files:
        frow = fixed_files.get(f.name)
        if frow is None:
            for fp in file_placeholders:
                if _file_pattern_ok(f.name, tree.concrete_name(fp, bindings)):
                    frow = fp
                    break
        if frow is not None and frow.r in PROMO_ACTION_ROWS:
            n = _phys_lines(f)
            if n > PROMO_SIGNAL_LINES:
                cand.add("#644", f, f"행위 칸 실현 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {frow.r}행)", _CASCADE_Q)

    # 파일 폐쇄 — 자리표시자 «파일» 칸이 있는 층만 이름이 자유다. 고정 파일 칸만 있는 층의
    # 추가 파일은 트리에 없는 경로다(#490 — 재량 조항은 «리프로 닫은 폴더»에만 걸린다).
    if checker_target.adapter_bundle(dir_path.parent):
        for f in files:
            if not any(_file_pattern_ok(f.name, fp.name) for fp in file_placeholders):
                out.add("#490", f, "어댑터 역할 파일 이름이 표준 트리의 모양과 다르다")
    if not has_file_placeholder:
        for f in files:
            if f.name not in fixed_files:
                out.add("#490", f, "트리가 이 층에 이름을 준 파일이 아니다")


def _check_banned_paths(bc_dir: Path, out: Findings) -> None:
    """경로 자체가 금지인 것 — 자리표시자 인스턴스로 흡수되지 않도록 전역으로 잡는다."""
    for p in bc_dir.rglob("*"):
        if not p.is_dir() or set(p.parts) & SKIP_DIRS:
            continue
        if p.name == "commands" and p.parent.name == "management":
            out.add("#58", p, "`management/commands/` 를 만들지 않는다")
        elif p.name == "specification" and "domain_layer" in p.parts:
            out.add("#314", p, "`domain_layer/` 에 `specification/` 폴더를 두지 않는다")
        elif p.name == "framework":
            out.add("#393", p, "`framework/` 는 저장소 루트 소유다 — BC 아래에 두면 위반")


def _check_bc(bc_dir: Path, out: Findings, cand: Candidates) -> None:
    bindings = {"bounded_context": bc_dir.name}
    root = tree.bc_root()
    allowed = {tree.concrete_name(c, bindings).rstrip("/") for c in tree.children(root)}
    pre_flagged: set[str] = set()
    dirs, files = _entries(bc_dir)
    for p in dirs:
        if p.name not in allowed:
            out.add("#81", p, "BC 직계는 일곱뿐이다 — 여덟째는 없다")
            pre_flagged.add(p.name)
    _check_level(bc_dir, root, bindings, out, cand, frozenset(pre_flagged))
    _check_banned_paths(bc_dir, out)


# ── framework/ · <project>/ — BC 폐쇄(#490)의 주어는 아니지만 자기 규칙이 있다 ──

def _framework_rows() -> "tree.Row":
    return next(r for r in tree.ROWS if r.depth == 0 and r.name == "framework/")


def _check_framework(fw_dir: Path, out: Findings) -> None:
    """#395 자식 다섯 + #488 고정 서브트리 존재. 인스턴스 «내용»은 content 검사기 몫."""
    fw = _framework_rows()
    fixed = {c.name.rstrip("/"): c for c in tree.children(fw) if c.kind == "fixed"}
    dirs, files = _entries(fw_dir)
    for f in files:
        out.add("#395", f, "`framework/` 직계에 파일 칸은 없다 — 자식은 다섯(폴더)뿐")
    for name, crow in fixed.items():
        sub = fw_dir / name
        if not sub.is_dir():
            out.add("#488", sub, f"고정 칸 `{name}/` 부재 (트리 {crow.r}행)")
            continue
        if not (sub / "__init__.py").is_file():
            out.add("#488", sub, "고정 칸 폴더에 `__init__.py` 가 없다")
        _check_framework_fixed(sub, crow, out)
    # <capability>/·<technology>/ 는 이름으로 못 가른다 — 존재만 허용하고 내용은 여기서 안 본다


def _check_framework_fixed(dir_path: Path, row: "tree.Row", out: Findings) -> None:
    for c in tree.children(row):
        if c.kind != "fixed":
            continue
        name = c.name.rstrip("/")
        target = dir_path / name
        if tree.is_dir(c):
            if not target.is_dir():
                out.add("#488", target, f"고정 칸 `{name}/` 부재 (트리 {c.r}행)")
            else:
                if not (target / "__init__.py").is_file():
                    out.add("#488", target, "고정 칸 폴더에 `__init__.py` 가 없다")
                _check_framework_fixed(target, c, out)
        elif not target.is_file():
            out.add("#488", target, f"고정 파일 부재 (트리 {c.r}행)")


def _find_project_pkg(target: Path) -> tuple[Path | None, str]:
    """<project> 판정 — manage.py 의 DJANGO_SETTINGS_MODULE 이 1순위(결정적), 없으면 유일 후보만."""
    manage = target / "manage.py"
    if manage.is_file():
        m = re.search(r"DJANGO_SETTINGS_MODULE[\"']\s*,\s*[\"']([\w.]+)[\"']", manage.read_text(encoding="utf-8", errors="ignore"))
        if m:
            pkg = target / m.group(1).split(".")[0]
            if pkg.is_dir():
                return pkg, "manage.py"
    cands = [
        p for p in sorted(target.iterdir())
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
        and p.name not in ("application", "framework")
        and ((p / "settings").is_dir() or (p / "settings.py").is_file())
    ]
    if len(cands) == 1:
        return cands[0], "유일 후보"
    if len(cands) > 1:
        return None, f"후보 {len(cands)}개 — manage.py 없음, 판정 보류"
    return None, "없음"


def _check_project(pkg: Path, out: Findings) -> None:
    dirs, files = _entries(pkg)
    for p in dirs + files:
        if p.name in PROJECT_ALLOWED or p.name in PROJECT_EXEMPT:
            continue
        hint = " — `settings/` 로 이관한다" if p.name == "settings.py" else ""
        out.add("#429", p, f"`<project>/` 에는 전역에 하나만 요구되는 것만 온다 (api.py·urls.py·celery.py·settings/){hint}")
    for name in PROJECT_REQUIRED_FILES:  # #488 — 트리 167~169행 fixed
        if not (pkg / name).is_file():
            out.add("#488", pkg / name, "고정 파일 부재 — 비면 빈 파일로 만든다 (`<project>/` · 트리 167~169행)")
    if not (pkg / "settings").is_dir() and not (pkg / "settings.py").is_file():
        out.add("#488", pkg / "settings", "고정 칸 `settings/` 부재 (트리 170행)")


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]) if argv else Path(".")
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    containers = [
        p for p in (target / "application",)
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS)
    ]
    bcs: list[Path] = []
    for c in containers:
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    signaled = [b for b in bcs if _has_adoption_signal(b)]
    fw_dir = target / "framework"

    # 대상 0건 가드(#74) — 어떤 필터보다 먼저(#75)
    repo_signal = bool(signaled) or fw_dir.is_dir()
    if not repo_signal:
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0
    if not bcs:
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 검사할 BC 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    findings = Findings(defer=True)
    cand = Candidates(defer=True)  # ⓓ#644 — exit 불산입·귀속 정규식 밖(후보 채널)
    # 채택 저장소에서는 application/ 직계 «전부»가 BC 다(#486) — 신호 없는 평면 BC 도 검사한다.
    for bc in bcs:
        _check_bc(bc, findings, cand)
    if fw_dir.is_dir():
        _check_framework(fw_dir, findings)
    pkg, how = _find_project_pkg(target)
    if pkg is not None:
        _check_project(pkg, findings)
    elif how.startswith("후보"):
        print(f"주의: `<project>/` {how} — `<project>` 검사를 건너뛴다(오판 방지)")

    emit_all(cand, printer=print, indent="")
    if findings:
        print(f"blocker {len(findings)}건 — 골격이 어긋나면 나머지 검사를 돌리지 않는다(#487)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    print(f"clean — BC {len(bcs)}개 골격 일치 (트리 {len(tree.ROWS)}행 · standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
