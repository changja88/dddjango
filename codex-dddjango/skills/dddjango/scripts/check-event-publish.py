#!/usr/bin/env python3
"""dddjango 사실(이벤트) 발행·구독 검사기 — D40·D59 축의 결정적 백스톱.

「사실은 과거형이고, 표면은 `published_event/` 하나이고, 구독은 껍데기다」를 강제한다.

담당 규칙 (rule-owner-map · 총 16):
  #7   [ast]  application_layer 의 import 허용은 넷 — 자기 domain_layer·자기 port/·
              자기 published_event/·framework{broker,pure,계약(exception·*_in·*_out)}.
              여기서는 «층 역참조»(driving/driven import)와 framework 비계약 모듈만 문다
              (django 는 #4, 타 BC 는 #12 관할 — 중복 진단 금지).
  #96  [ast]  driving_layer 잎은 domain_layer 의 애그리거트·엔티티·리포지토리 선언·
              도메인 이벤트와 port 선언을 import 하지 않는다 — #95 예외(exception·값 객체)는
              허용이다 (api_router.py·event_router.py 는 잎이 아니다 — #99).
  #271 [ast+] 사실 이름은 과거형 — 확정: 첫 토큰이 애그리거트 공개 메서드와 같음
              (ReduceInventory↔reduce) / 후보: 끝 토큰이 -ed/-en·불규칙 과거분사 밖.
  #279 [ast]  핸들러는 application_layer 의 유스케이스다 — 구독·wiring 이
              domain_layer 를 import 하면 위반.
  #280 [ast]  핸들러는 이벤트를 애그리거트 어휘로 번역한다 — 이벤트 파라미터를 Call 에
              «통째»로 넘기면 위반, apply/handle/on_* 애그리거트 메서드 호출도 위반.
  #323 [path·면제] driven_layer 는 구체 기술을 알아도 된다 — 진단 0.
  #502 [path] `published_event/` 는 BC 루트 직계뿐 — open_host_service/ 등 다른 곳에
              있으면 위반(스키마 주인이 «보내는 쪽»).
  #503 [ast]  published_event/<event>.py 는 필드만 — domain_layer import·메서드면 위반.
  #504 [ast]  과거형 사실 하나 = 파일 하나 — 공개 클래스 2+·모듈 함수면 위반.
  #507 [ast]  event_subscription/ 은 남의 BC 를 published_event 밖으로 import 금지.
  #508 [ast]  event_router.py 는 「사실→핸들러」 표다 — import·표 대입·register 함수
              하나 밖의 최상위 노드는 위반.
  #509 [ast]  <event>_subscription.py 는 유스케이스 하나만 부른다(cron_job 껍데기와 동형).
  #564 [ast+] 진행표 금지 — 후보: ㉠saga/·process_manager/ 폴더 ㉡Enum 값 토큰이
              <use_case>/ 폴더 이름과 겹침(「업무가 이 단계 이름을 입으로 부르나」).
  #600 [ast]  공표 사실의 BC 간 순환 금지 — published_event 소유 BC → 구독 BC 방향
              그래프에 사이클이 있으면 위반.
  #601 [ast]  구독이 부른 유스케이스는 다시 발행하지 않는다(발행은 한 겹) —
              build_X → X_use_case.py(#85 짝)로 해소해 .publish 호출을 본다.
  #627 [ast]  구독 payload 를 장부로 적립·집계하면 위반(사본 — 관할 밖) —
              구독 경로 유스케이스의 `+=` 적립→save, 무조회 create→save 를 문다.

단순화(정직 기록): #601·#627 의 구독→유스케이스 해소는 «build_X ↔ X_use_case.py»
쌍(#85)과 직접 import 만 따라간다. #627 의 흐름 판정은 함수 지역(같은 함수 안에
적립/무조회-생성과 save 가 함께 있는가)이다.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
fail-closed · ⓓ 후보는 exit 불산입.

사용법: check-event-publish.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import ast
import re
import sys

import checker_target
from findings import Candidates, Findings
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
DRIVING_DIRS = ("driving_layer",)
WIRING_FILES = {"api_router.py", "event_router.py", "event_wiring.py"}  # 잎이 아니다(#99)

# #271 후보 — 불규칙 과거분사(데이터 목록 — 닫지 않는다: predicates ⓒ).
IRREGULAR_PAST = {
    "sent", "paid", "built", "made", "done", "gone", "run", "set", "put", "cut", "left",
    "sold", "bought", "caught", "taught", "brought", "thought", "held", "kept", "met",
    "shot", "won", "begun", "sung", "drawn", "grown", "known", "thrown", "shown", "flown",
    "given", "taken", "written", "driven", "risen", "chosen", "frozen", "spoken", "broken",
    "stolen", "worn", "torn", "born", "seen", "been", "had", "said", "found", "heard",
    "lost", "told", "understood", "stood", "read", "split", "hit", "shut", "spent", "lent",
}
PROGRESS_DIR_NAMES = {"saga", "sagas", "process_manager", "process_managers"}
FRAMEWORK_CONTRACT_OK = ("exception",)  # + *_in/*_out/contract 는 접미로 본다


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _find_bcs(target: Path) -> list[Path]:
    bcs: list[Path] = []
    for c in target.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return bcs


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None


def _py_files(base: Path) -> list[Path]:
    return [p for p in sorted(base.rglob("*.py")) if not set(p.parts) & SKIP_DIRS]


def _rel(root: Path, path: Path, line: int | None = None) -> str:
    s = path.relative_to(root).as_posix()
    return f"{s}:{line}" if line else s


def _camel_tokens(name: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", name)]


# ── #502 · #503 · #504 · #271 — 공표 사실 표면 ──────────────────────────────

def _aggregate_public_methods(bc: Path) -> set[str]:
    out: set[str] = set()
    domain = bc / "domain_layer"
    if not domain.is_dir():
        return out
    for agg in domain.iterdir():
        if not agg.is_dir():
            continue
        mod = _parse(agg / f"{agg.name}.py") if (agg / f"{agg.name}.py").is_file() else None
        if mod is None:
            continue
        for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
            out |= {m.name for m in cls.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("_")}
    return out


def _check_event_name(root: Path, path: Path, cls: ast.ClassDef, methods: set[str],
                      f: Findings, cand: Candidates) -> None:
    toks = _camel_tokens(cls.name)
    if not toks:
        return
    if toks[0] in methods:
        f.add("#271", _rel(root, path, cls.lineno),
              f"사실 이름 `{cls.name}` 의 첫 토큰이 애그리거트 공개 메서드 `{toks[0]}` 와 같다 — "
              "이벤트는 명령이 아니라 과거형 사실이다(ReduceInventory ✗ → OrderPlaced ✓)")
    elif not (toks[-1].endswith("ed") or toks[-1].endswith("en") or toks[-1] in IRREGULAR_PAST):
        cand.add("#271", _rel(root, path, cls.lineno),
                 f"사실 이름 `{cls.name}` 의 끝 토큰 `{toks[-1]}` 이 과거형이 아니다",
                 "이 이름이 «이미 일어난 사실»을 말하나")


def _check_published_events(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
    # #502 — published_event 는 BC 루트 직계뿐.
    for d in bc.rglob("published_event"):
        if not d.is_dir() or set(d.parts) & SKIP_DIRS:
            continue
        if d.parent != bc:
            f.add("#502", _rel(root, d),
                  "published_event/ 가 BC 루트 직계가 아니다 — 사실 표면은 하나이고 "
                  "스키마 주인이 «보내는 쪽»이라 open_host_service/contract/ 에 못 들어간다")
    pe = bc / "published_event"
    if not pe.is_dir():
        return
    methods = _aggregate_public_methods(bc)
    for py in sorted(pe.glob("*.py")):
        if py.name == "__init__.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        classes = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
        funcs = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if len(classes) != 1:
            f.add("#504", _rel(root, py), f"공개 클래스 {len(classes)}개 — 과거형 사실 하나 = 파일 하나다")
        if funcs:
            f.add("#504", _rel(root, py), "모듈 함수가 있다 — 사실 파일에는 사실 클래스 하나만 온다")
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom) and "domain_layer" in (node.module or ""):
                f.add("#503", _rel(root, py, node.lineno),
                      "published_event 가 domain_layer 를 import 한다 — 필드만 오고 도메인 타입은 0 이다")
        for cls in classes:
            for m in cls.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("__"):
                    f.add("#503", _rel(root, py, m.lineno),
                          f"사실 클래스에 메서드 `{m.name}` — 사실에는 필드만 온다")
            _check_event_name(root, py, cls, methods, f, cand)
    # domain_layer/*/event/ 의 도메인 이벤트 이름도 #271 대상이다.
    domain = bc / "domain_layer"
    if domain.is_dir():
        for py in sorted(domain.glob("*/event/*.py")):
            mod = _parse(py)
            if mod is None:
                continue
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                _check_event_name(root, py, cls, methods, f, cand)


# ── #96 · #7 — 층 import 규율 ───────────────────────────────────────────────

def _check_driving_leaf_imports(root: Path, bc: Path, f: Findings) -> None:
    for layer in DRIVING_DIRS:
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            if py.name in WIRING_FILES or py.name == "__init__.py":
                continue
            mod = _parse(py)
            if mod is None:
                continue
            for node in ast.walk(mod):
                if not isinstance(node, ast.ImportFrom):
                    continue
                m = node.module or ""
                if (".domain_layer." in m or m.endswith(".domain_layer")) and not any(
                    seg in ("exception", "value_object", "shared_value_object") for seg in m.split(".")
                ):
                    # #95 허용 목록(exception·value_object·shared_value_object)을 뺀 나머지만
                    # #96 — 2026-08-12 라운드 1′ D1′: blanket 검사가 #95 를 못 본 스펙 드리프트 교정.
                    f.add("#96", _rel(root, py, node.lineno),
                          "driving 잎이 domain_layer 를 import 한다 — 잎은 애그리거트·엔티티·"
                          "리포지토리·도메인 이벤트를 모른다(#95 예외: exception·값 객체)")
                elif ".application_layer.port." in m:
                    f.add("#96", _rel(root, py, node.lineno),
                          "driving 잎이 포트 선언을 import 한다 — 잎이 아는 것은 유스케이스와 스키마뿐이다")


def _check_application_imports(root: Path, bc: Path, f: Findings) -> None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return
    own = bc.name
    for py in _py_files(app_layer):
        mod = _parse(py)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if not isinstance(node, ast.ImportFrom):
                continue
            m = node.module or ""
            segs = m.split(".")
            if segs[0] == "application" and len(segs) >= 3 and segs[1] == own:
                if segs[2] in ("driving_layer", "driven_layer"):
                    f.add("#7", _rel(root, py, node.lineno),
                          f"application_layer 가 자기 {segs[2]} 를 import 한다 — 허용은 "
                          "domain_layer·port·published_event·framework 계약 넷뿐이다")
            elif segs[0] == "framework" and len(segs) >= 3:
                cap, leaf = segs[1], segs[-1]
                contract_ok = (leaf in FRAMEWORK_CONTRACT_OK or leaf.endswith("_in")
                               or leaf.endswith("_out") or "contract" in segs
                               or leaf.endswith("_port"))
                if cap not in ("broker", "pure") and not contract_ok:
                    f.add("#7", _rel(root, py, node.lineno),
                          f"application_layer 가 framework/{cap}/{leaf} 를 import 한다 — "
                          "framework 에서 오는 것은 계약(exception·*_in·*_out·*_port)뿐이다")


# ── #507 · #508 · #509 · #279 — 구독 껍데기 ─────────────────────────────────

def _subscription_dir(bc: Path) -> Path | None:
    for layer in DRIVING_DIRS:
        d = bc / layer / "event_subscription"
        if d.is_dir():
            return d
    return None


def _check_subscription(root: Path, bc: Path, f: Findings) -> list[tuple[Path, str]]:
    """반환: (구독 파일, build 이름) — #601·#627 이 쓰는 간선."""
    edges: list[tuple[Path, str]] = []
    sub = _subscription_dir(bc)
    if sub is None:
        return edges
    own = bc.name
    for py in _py_files(sub):
        if py.name == "__init__.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom):
                m = node.module or ""
                segs = m.split(".")
                if segs[0] == "application" and len(segs) >= 3 and segs[1] != own:
                    if "published_event" not in segs:
                        f.add("#507", _rel(root, py, node.lineno),
                              f"구독이 타 BC `{segs[1]}` 를 published_event 밖으로 import 한다")
                if ".domain_layer." in m or m.endswith(".domain_layer"):
                    f.add("#279", _rel(root, py, node.lineno),
                          "구독이 domain_layer 를 import 한다 — 핸들러는 도메인이 아니라 "
                          "application_layer 의 또 하나의 유스케이스다")
        if py.name == "event_router.py":
            _check_event_router(root, py, mod, f)
            continue
        if not py.name.endswith("_subscription.py"):
            continue
        # #509 — 유스케이스 하나만.
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            executes = 0
            flow_line: int | None = None
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "execute":
                    executes += 1
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id.startswith("build_"):
                    edges.append((py, n.func.id[len("build_"):]))
                if flow_line is None and isinstance(n, (ast.If, ast.For, ast.While, ast.Try)):
                    flow_line = n.lineno
            if flow_line is not None:
                f.add("#509", _rel(root, py, flow_line),
                      "구독 껍데기에 제어 흐름이 있다 — 유스케이스 하나를 부르는 것이 전부다")
            if executes > 1:
                f.add("#509", _rel(root, py, fn.lineno),
                      f"`{fn.name}` 이 유스케이스를 {executes}회 부른다 — 하나만 부른다")


    return edges


def _check_event_router(root: Path, py: Path, mod: ast.Module, f: Findings) -> None:
    funcs = 0
    for i, node in enumerate(mod.body):
        if i == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            continue  # 모듈 docstring
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Dict, ast.List, ast.Tuple)):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs += 1
            if funcs > 1:
                f.add("#508", _rel(root, py, node.lineno), "함수가 둘 이상이다 — event_router 는 표 하나다")
            continue
        f.add("#508", _rel(root, py, node.lineno),
              "event_router.py 에 표 밖 최상위 노드가 있다 — 「어느 사실 → 어느 핸들러」 표만 온다"
              "(꽂는 것은 event_wiring.py 다)")


# ── #280 — 핸들러의 번역 의무 ───────────────────────────────────────────────

def _event_param_names(fn: ast.FunctionDef | ast.AsyncFunctionDef, event_syms: set[str]) -> set[str]:
    out = set()
    for a in fn.args.args + fn.args.kwonlyargs:
        ann = a.annotation
        names = set()
        for n in ast.walk(ann) if ann else []:
            if isinstance(n, ast.Name):
                names.add(n.id)
            elif isinstance(n, ast.Attribute):
                names.add(n.attr)
        if names & event_syms:
            out.add(a.arg)
    return out


def _check_handler_translation(root: Path, bc: Path, f: Findings) -> None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return
    for py in _py_files(app_layer):
        mod = _parse(py)
        if mod is None:
            continue
        event_syms: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if "published_event" in m or ".event." in m or m.endswith(".event"):
                    event_syms |= {a.asname or a.name for a in node.names}
        if not event_syms:
            continue
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            params = _event_param_names(fn, event_syms)
            if not params:
                continue
            for n in ast.walk(fn):
                if not isinstance(n, ast.Call):
                    continue
                whole = [a.id for a in n.args if isinstance(a, ast.Name) and a.id in params]
                whole += [kw.value.id for kw in n.keywords
                          if isinstance(kw.value, ast.Name) and kw.value.id in params]
                meth = n.func.attr if isinstance(n.func, ast.Attribute) else ""
                if meth in ("apply", "handle") or meth.startswith("on_"):
                    f.add("#280", _rel(root, py, n.lineno),
                          f"애그리거트 메서드 `{meth}` 호출 — 핸들러는 이벤트를 애그리거트 어휘로 "
                          "번역한다(inventory.reduce(sku, qty) ✓ / inventory.apply(event) ✗)")
                elif whole:
                    f.add("#280", _rel(root, py, n.lineno),
                          f"이벤트 파라미터 `{whole[0]}` 를 통째로 넘긴다 — 필드만 뽑아 넘긴다")


# ── #564 — 진행표 후보 ─────────────────────────────────────────────────────

def _use_case_dir_names(bc: Path) -> set[str]:
    out: set[str] = set()
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return out
    for area in app_layer.iterdir():
        if area.is_dir() and area.name not in ("port", "__pycache__"):
            out |= {d.name for d in area.iterdir() if d.is_dir() and d.name != "__pycache__"}
    return out


def _check_progress_table(root: Path, target: Path, bcs: list[Path], cand: Candidates) -> None:
    for d in target.rglob("*"):
        if d.is_dir() and d.name in PROGRESS_DIR_NAMES and not set(d.parts) & SKIP_DIRS:
            cand.add("#564", _rel(root, d),
                     f"`{d.name}/` 폴더 — 진행 상태를 기억하는 «진행표»는 만들지 않는다"
                     "(순서는 유스케이스가 진다)", "이 칸이 «패턴»이 아니라 «진행표»인가")
    for bc in bcs:
        uc_names = _use_case_dir_names(bc)
        if not uc_names:
            continue
        for py in _py_files(bc):
            mod = _parse(py)
            if mod is None:
                continue
            for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                if not bases & {"Enum", "StrEnum", "TextChoices", "IntChoices", "Choices"}:
                    continue
                for st in cls.body:
                    if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                            and isinstance(st.value.value, str):
                        toks = set(re.split(r"[^a-z0-9]+", st.value.value.lower())) - {""}
                        hit = {u for u in uc_names if set(u.split("_")) <= toks or u in toks}
                        if hit:
                            cand.add("#564", _rel(root, py, st.lineno),
                                     f"Enum 값 `{st.value.value}` 이 유스케이스 폴더 {sorted(hit)} 와 겹친다",
                                     "업무가 이 단계 이름을 입으로 부르나")


# ── #600 · #601 · #627 — 발행 그래프 ────────────────────────────────────────

def _fact_graph_edges(bcs: list[Path]) -> tuple[dict[str, set[str]], dict[str, str]]:
    owner: dict[str, str] = {}
    for bc in bcs:
        pe = bc / "published_event"
        if pe.is_dir():
            for py in pe.glob("*.py"):
                if py.name != "__init__.py":
                    owner[py.stem] = bc.name
    graph: dict[str, set[str]] = {}
    for bc in bcs:
        sub = _subscription_dir(bc)
        if sub is None:
            continue
        for py in sub.glob("*_subscription.py"):
            mod = _parse(py)
            if mod is None:
                continue
            for node in ast.walk(mod):
                if isinstance(node, ast.ImportFrom) and "published_event" in (node.module or ""):
                    segs = (node.module or "").split(".")
                    if segs[0] == "application" and len(segs) >= 2 and segs[1] != bc.name:
                        graph.setdefault(segs[1], set()).add(bc.name)
    return graph, owner


def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in set(graph) | {v for vs in graph.values() for v in vs}}
    stack: list[str] = []

    def dfs(n: str) -> list[str] | None:
        color[n] = GRAY
        stack.append(n)
        for v in graph.get(n, ()):
            if color[v] == GRAY:
                return stack[stack.index(v):] + [v]
            if color[v] == WHITE:
                found = dfs(v)
                if found:
                    return found
        stack.pop()
        color[n] = BLACK
        return None

    for n in sorted(color):
        if color[n] == WHITE:
            found = dfs(n)
            if found:
                return found
    return None


def _resolve_use_case(bc: Path, name: str) -> Path | None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return None
    hits = [p for p in app_layer.rglob(f"{name}_use_case.py") if not set(p.parts) & SKIP_DIRS]
    return hits[0] if hits else None


def _check_subscribed_use_case(root: Path, bc: Path, sub_file: Path, uc_name: str, f: Findings) -> None:
    uc_path = _resolve_use_case(bc, uc_name)
    if uc_path is None:
        return
    mod = _parse(uc_path)
    if mod is None:
        return
    for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        publishes = aug_ledger = saves = reads = creates_kw = False
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if n.func.attr == "publish":
                    publishes = True
                elif n.func.attr.split("_", 1)[0] in ("save", "remove"):
                    saves = True
                elif n.func.attr.split("_", 1)[0] in ("get", "find", "list", "exists", "count", "search"):
                    reads = True
            if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Attribute):
                aug_ledger = True
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id[:1].isupper():
                if any(not kw.arg.endswith("_id") for kw in n.keywords if kw.arg):
                    creates_kw = True
        if publishes:
            f.add("#601", _rel(root, uc_path, fn.lineno),
                  f"구독({sub_file.relative_to(root).as_posix()})이 부른 유스케이스가 다시 발행한다 — "
                  "발행은 한 겹까지다(두 겹이 필요하면 그것은 워커의 일이다 — D48 ②)")
        if aug_ledger and saves:
            f.add("#627", _rel(root, uc_path, fn.lineno),
                  "구독 payload 를 `+=` 로 적립해 저장한다 — 사본(장부)은 이 트리의 관할 밖이다"
                  "(상세는 주인의 open_host_service 에 되묻는다)")
        elif creates_kw and saves and not reads:
            f.add("#627", _rel(root, uc_path, fn.lineno),
                  "구독 payload 의 비식별자 필드로 조회 없이 생성·저장한다 — 사본 적립(ECST)은 관할 밖이다")


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    bcs = _find_bcs(root)
    adopted = [bc for bc in bcs if _has_adoption_signal(bc)]
    findings = Findings()
    cand = Candidates()

    targets = 0
    for bc in adopted:
        if (bc / "published_event").is_dir() or _subscription_dir(bc) is not None:
            targets += 1
        _check_published_events(root, bc, findings, cand)
        _check_driving_leaf_imports(root, bc, findings)
        _check_application_imports(root, bc, findings)
        edges = _check_subscription(root, bc, findings)
        _check_handler_translation(root, bc, findings)
        for sub_file, uc_name in edges or []:
            _check_subscribed_use_case(root, bc, sub_file, uc_name, findings)

    _check_progress_table(root, root, adopted, cand)

    graph, _owner = _fact_graph_edges(adopted)
    cycle = _find_cycle(graph)
    if cycle:
        findings.add("#600", " → ".join(cycle),
                     "공표 사실의 BC 간 순환 — A 발행 → B 구독·발행 → A 구독 고리는 금지다")

    # 대상 0건 가드(#74) — 채택 신호는 있는데 층 경로가 하나도 안 열리면 경로 계약 불일치다.
    # (published_event·event_subscription «내용» 부재는 정상 0 — targets 는 그 구분용이다.)
    _ = targets
    if adopted and not any(
            (bc / "application_layer").is_dir() or any((bc / d).is_dir() for d in DRIVING_DIRS)
            for bc in adopted):
        print("blocker: 채택 신호는 있는데 application_layer/driving 층이 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2

    for c in cand:
        print(c)
    if findings:
        print("blocker — 사실 발행·구독 위반 (표면은 published_event 하나 · 구독은 껍데기 — D40·D59)")
        for x in findings:
            print(f"  {x}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
