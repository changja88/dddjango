#!/usr/bin/env python3
"""dddjango 유스케이스·경계 자료 계약 검사기 — 트리 39~44행(+13~15행 schema) 규율의 결정적 백스톱.

`application_layer/<area>/<use_case>/` 의 자료 배치와 `driving_layer/api/**/schema/` 의
경계 계약을 강제한다. 경로 기대는 `standard_tree.py` 에서 도출한다.

무엇을 잡나 (규칙 번호는 트리 개정 명세):
  구조   #182 `application_layer/` 직계는 `<area>/`·`port/` 둘뿐(종류 폴더 금지)
         #183 `validation/`·`*_validation.py` 금지 · #192 `<area>/` 직계 종류 폴더 금지
         #188 `<area>` 는 `driving_layer/api/<area>` 와 1:1 · #190/#193 유스케이스
         하나=폴더 하나=진입점 하나(`<use_case>_use_case.py`)
  자료   #201 자료는 세 파일(`_command`·`_query`·`_result`) — `dto/` 겹 금지
         #569 command·query 는 둘 다 오되 클래스는 한쪽에만 · #570 `_result.py` 는
         커맨드 쪽도 갖는다(빈 파일 허용) · #571 result 는 성공 한 벌만(실패 금지)
         #202/#207 DTO 에 애그리거트·엔티티·ORM 행 금지(값 객체는 그대로 온다)
         #205 DTO 는 자기 유스케이스 폴더 안에서만 · #189 유스케이스끼리 모듈 돌려쓰기 금지
         #208 command 는 `schema_in` 과 같은 타입을 쓰지 않는다(driving import 금지)
         #567 `dto` 라는 이름을 쓰지 않는다(schema 는 기술 실물)
  진입점 #635 클래스 하나·`execute` 하나·계약 객체 하나 → result(빈 result 짝은 `-> None`)
         #211 스트림은 `Iterator[<UseCase>Result]` · #196 Boundary·Presenter 금지
  발행   #539 `pull_events()` 는 유스케이스가 부른다(리포지토리 구현이 부르면 위반)
         #540 도메인 사실을 «그대로» 브로커에 넘기면 위반(옮겨 담기는 유스케이스 몫)
         #541 커밋 «전» 발행 금지 — `.publish(` 직접 호출은 `uow.after_commit` 밖이다
  schema #139 제약 선언은 `schema_in.py` 에(컨트롤러의 Field·validator 는 위반)
         #142 요청 스키마는 도메인 객체를 만들지 않는다(#141: 값 객체 import 는 면제)
         #143/#144 `schema_out` 은 result 로 만든다 — 도메인·ORM 타입 노출 금지
         #210 컨트롤러는 result 만 보고 응답을 만든다(도메인 들여다보기 금지 —
              예외: 같은 BC `domain_layer/<agg>/exception/` 의 실선언 예외 클래스
              import 는 #95·#92(driving 잎의 도메인 예외 허용) 준거 면제 · 2026-08-14
              라운드 3 실증: 검사기 간 충돌 — billing NJ-7 확립 모양이 direct catch)

ast+ 후보 채널 (㉰ — 기계가 후보를 좁히고 사람이 물음으로 마무리):
  #68(검증 raise 의 자리) · #103(입구의 값 객체 사용 폭) · #140(제약 0 스키마)
  #191(use_case 이름은 동사) · #194(유스케이스 안 업무 규칙) — «ⓓ 후보» 로 출력하되
  exit 에 산입하지 않는다(판정 마무리는 agents/discipline-reviewer.md 몫).
  #68·#103 후보 스캔은 application_layer·driving_layer 로 한정한다(주 발생지).

가드 계약 (명세 조각 ⓐ): 대상 0건 가드(#74). touched 필터는 두지 않는다 —
미루기는 flow(G0)가 관리한다.

공유의 제자리(#189 · T61 ⓑ): 유스케이스 간 공유 모듈 칸은 없다 — 업무 판정은
`domain_layer/`, 바깥 능력은 `port/`, 기술은 `framework/`, 남으면 진입점 안 `_` 사설로
중복(#192). `<area>/` 직계 파일의 존재 판정은 skeleton(#490) 소유라 여기서 안 잡는다.

사용법: check-usecase-dto-placement.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2). 방출은 공용 ordered emitter
(emit_all) 경유 — stdout 위반·후보 라인 순서와 레코드 순서가 같고, 라인은 레코드
필드의 순수 함수다(출력 계약 v2).
"""
from __future__ import annotations

import ast
import re
import sys

import checker_target
from findings import Candidates, Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

DRIVING_NAMES = ("driving_layer",)
DRIVEN_NAMES = ("driven_layer",)

# <area> 자리에 올 수 없는 «종류 이름» — #182(층 직계)·#192(area 직계) 공용 blocklist
KIND_FOLDER_NAMES = {
    "unit_of_work", "domain_bypass_query", "dto", "service", "services",
    "validation", "validators", "common", "shared", "util", "utils",
    "helper", "helpers", "command", "query", "use_case", "use_cases",
}
ITERATOR_NAMES = {"Iterator", "AsyncIterator", "Generator", "AsyncGenerator", "Iterable"}
BOUNDARY_TOKENS = ("InputBoundary", "OutputBoundary", "Presenter")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _entries(d: Path) -> tuple[list[Path], list[Path]]:
    dirs: list[Path] = []
    files: list[Path] = []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or p.name in SKIP_DIRS:
            continue
        (dirs if p.is_dir() else files).append(p)
    return dirs, files


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _parse(f: Path) -> ast.Module | None:
    try:
        return ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _ann_idents(node: ast.expr | None) -> set[str]:
    """애너테이션의 이름 원자(문자열 애너테이션은 식별자 정규식으로 보수 추출)."""
    if node is None:
        return set()
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.update(IDENT_RE.findall(n.value))
    return out


def _import_records(mod: ast.Module) -> list[tuple[str, list[str]]]:
    """모듈의 절대 import — (점 경로, 가져온 이름들). 상대 import 는 층 판정에 안 쓴다."""
    out: list[tuple[str, list[str]]] = []
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.append((a.name, [a.name.split(".")[-1]]))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.append((node.module, [a.asname or a.name for a in node.names]))
    return out


def _domain_kind(mod_path: str) -> str | None:
    """import 경로가 도메인의 무엇을 가리키나 — 'value_object' | 'entity' | 'aggregate' | 'other'."""
    parts = mod_path.split(".")
    if "domain_layer" not in parts:
        return None
    if "value_object" in parts or "shared_value_object" in parts:
        return "value_object"
    if "entity" in parts:
        return "entity"
    i = parts.index("domain_layer")
    rest = parts[i + 1:]
    if len(rest) >= 2 and rest[0] == rest[1]:  # domain_layer.<agg>.<agg> — 애그리거트 루트
        return "aggregate"
    if "exception" in rest:  # domain_layer.<agg>.exception.* — 예외 칸(#95 가 driving 잎에 허용)
        return "exception"
    return "other"


def _is_orm_import(mod_path: str) -> bool:
    parts = mod_path.split(".")
    return any(p.startswith("django_") for p in parts) or ("driven_layer" in parts and "models" in parts)


def _exception_based(cls: "ast.ClassDef", declared: "dict[str, ast.ClassDef]", depth: int = 0) -> bool:
    """기반 사슬에 Exception/Error 가 닿는가 — 비-예외 클래스 밀반입 차단(#210 면제 조건 ⑶)."""
    if depth > 5:
        return False
    for base in cls.bases:
        name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
        if name == "Exception" or name.endswith(("Exception", "Error")):
            return True
        if name in declared and _exception_based(declared[name], declared, depth + 1):
            return True
    return False


def _lawful_domain_exception_import(mod_path: str, names: "list[str]", bc: Path) -> bool:
    """같은 BC `domain_layer/<agg>/exception/<module>` 실선언 예외 클래스 import 인가.

    #95·#92(driving 잎이 domain 에서 가져올 수 있는 것: exception·값 객체) 준거 면제의
    Goodhart 방어 셋(2026-08-14 적대 리뷰): ⑴ 경로 깊이 고정(`exception/` 직계 모듈만)
    ⑵ 가져온 이름 전부가 그 모듈이 «직접 선언한» ClassDef(재수출·함수·상수 세탁 차단 —
    별칭 import 는 이름 불일치로 자연 탈락) ⑶ 기반 사슬에 Exception/Error 토큰.
    타 BC 의 exception 은 면제 밖(#12 축과 별개로 여기서도 발화 유지)이다.
    """
    parts = mod_path.split(".")
    if len(parts) != 6 or parts[:3] != ["application", bc.name, "domain_layer"]:
        return False
    if parts[4] != "exception":
        return False
    module_file = bc.joinpath(*parts[2:]).with_suffix(".py")
    if not module_file.is_file():
        return False
    mod = _parse(module_file)
    if mod is None:
        return False
    declared: "dict[str, ast.ClassDef]" = {
        c.name: c for c in mod.body if isinstance(c, ast.ClassDef) and not c.name.startswith("_")
    }
    if not names or any(n not in declared for n in names):
        return False
    return all(_exception_based(declared[n], declared) for n in names)


# ── application_layer 구조 — #182 · #183 · #188 · #190 · #192 · #193 ────────

def _app_layer(bc: Path) -> Path | None:
    d = bc / "application_layer"
    return d if d.is_dir() else None


def _driving_api(bc: Path) -> Path | None:
    for name in DRIVING_NAMES:
        d = bc / name / "api"
        if d.is_dir():
            return d
    return None


def _check_structure(bc: Path, bc_rel: Path, out: Findings) -> list[Path]:
    """구조 규칙 검사 후 <use_case>/ 폴더 목록을 돌려준다."""
    app = _app_layer(bc)
    if app is None:
        return []
    rel = bc_rel / app.name
    dirs, _ = _entries(app)
    areas: list[Path] = []
    for p in dirs:
        if p.name == "port":
            continue
        if p.name in KIND_FOLDER_NAMES:
            out.add("#182", rel / p.name, "`application_layer/` 직계는 `<area>/`·`port/` 둘뿐이다 — 종류 폴더는 자리가 없다(`domain_bypass_query/`·`unit_of_work/` 는 `port/` 안이다)")
        else:
            areas.append(p)

    for p in app.rglob("*"):
        if set(p.relative_to(app).parts) & SKIP_DIRS:
            continue
        if p.is_dir() and p.name in ("validation", "validators"):
            out.add("#183", rel / p.relative_to(app), "`application_layer/` 아래에 `validation/` 폴더를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
        elif p.is_file() and p.name.endswith("_validation.py"):
            out.add("#183", rel / p.relative_to(app), "`*_validation.py` 를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")

    api = _driving_api(bc)
    if api is not None:
        api_dirs, _ = _entries(api)
        api_areas = {p.name for p in api_dirs if p.name != "webhook"}
        app_areas = {p.name for p in areas}
        for name in sorted(app_areas - api_areas):
            out.add("#188", rel / name, f"`<area>` 는 `driving_layer/api/<area>` 와 1:1 이다 — api 쪽에 `{name}/` 이 없다")
        for name in sorted(api_areas - app_areas):
            out.add("#188", bc_rel / api.relative_to(bc) / name, f"`<area>` 는 `application_layer/<area>` 와 1:1 이다 — application_layer 쪽에 `{name}/` 이 없다")

    ucs: list[Path] = []
    for area in areas:
        a_dirs, _ = _entries(area)
        for p in a_dirs:
            if p.name in KIND_FOLDER_NAMES:
                out.add("#192", rel / area.name / p.name, "절차 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 둔다 — `service/` 같은 종류 폴더를 만들지 않는다")
            else:
                ucs.append(p)
    return ucs


# ── <use_case>/ — #190 · #193 · #201 · #569 · #570 · #571 · #635 · #211 ────

def _top_public_classes(mod: ast.Module) -> list[ast.ClassDef]:
    return [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]


def _check_use_case(uc: Path, uc_rel: Path, agg_names: set[str], out: Findings, cand: Candidates) -> None:
    name = uc.name
    dirs, files = _entries(uc)

    for d in dirs:
        if d.name == "dto":
            out.add("#201", uc_rel / d.name, "유스케이스 자료는 세 파일(`_command`·`_query`·`_result`)이다 — `dto/` 겹을 만들지 않는다")

    entry = uc / f"{name}_use_case.py"
    strays = [f for f in files if f.name.endswith("_use_case.py") and f.name != entry.name]
    for f in strays:
        out.add("#190", uc_rel / f.name, "유스케이스 하나 = 폴더 하나 = 진입점 하나다 — 이 폴더의 진입점이 아니다")
    if not entry.is_file():
        out.add("#193", uc_rel / entry.name, f"진입점 파일 이름은 `{name}_use_case.py` 다 — 부재")

    # #191 후보 — 이름은 동사(자동 통과: 첫 토큰이 애그리거트 공개 메서드와 일치하는 경우는
    # 수집 비용 대비 이득이 낮아 후보에 포함하되, 애그리거트 «이름 그대로»와 명사 접미만 좁힌다)
    first = name.split("_")[0]
    if name in agg_names or first in agg_names and len(name.split("_")) == 1:
        cand.add("#191", uc_rel, f"폴더 이름 `{name}` 이 애그리거트 이름이다 — 동사로 짓는다", "Q1(이 이름이 «판정이 되는 물음»인가)")
    elif any(name.endswith(sfx) for sfx in ("_list", "_info", "_detail", "_status")):
        cand.add("#191", uc_rel, f"폴더 이름 `{name}` 이 명사 접미로 끝난다 — 동사로 짓는다", "Q1(이 이름이 «판정이 되는 물음»인가)")

    cmd_f, qry_f, res_f = (uc / f"{name}_{k}.py" for k in ("command", "query", "result"))
    if not res_f.is_file():
        out.add("#570", uc_rel / res_f.name, "`<use_case>_result.py` 는 커맨드 쪽도 갖는다 — 돌려줄 것이 없으면 «빈 파일»로 둔다")
    for f, label in ((cmd_f, "command"), (qry_f, "query")):
        if not f.is_file():
            out.add("#569", uc_rel / f.name, f"`<use_case>_{label}.py` 는 안 써도 «빈 파일»로 온다")

    cmd_mod = _parse(cmd_f) if cmd_f.is_file() else None
    qry_mod = _parse(qry_f) if qry_f.is_file() else None
    if cmd_mod is not None and qry_mod is not None:
        if _top_public_classes(cmd_mod) and _top_public_classes(qry_mod):
            out.add("#569", uc_rel, "command 와 query «양쪽에» 계약 클래스가 있다 — 클래스는 한쪽에만 두고 안 쓰는 쪽은 빈 파일이다")

    if res_f.is_file():
        res_mod = _parse(res_f)
        if res_mod is not None:
            pubs = _top_public_classes(res_mod)
            if len(pubs) >= 2:
                out.add("#571", uc_rel / res_f.name, f"result 에는 «성공했을 때의 모양 한 벌»만 온다 — 공개 클래스가 {len(pubs)}개면 유스케이스가 둘이라는 신호다")
            for c in pubs:
                if any(tok in c.name for tok in ("Error", "Failure", "Exception")):
                    out.add("#571", uc_rel / res_f.name, f"실패(`{c.name}`)는 result 에 오지 않는다")

    if entry.is_file():
        mod = _parse(entry)
        if mod is not None:
            _check_entry(mod, uc_rel / entry.name, out, cand)


def _check_entry(mod: ast.Module, rel, out: Findings, cand: Candidates) -> None:
    pubs = _top_public_classes(mod)
    if len(pubs) != 1:
        out.add("#635", rel, f"진입점은 클래스 «하나»다 — 공개 클래스가 {len(pubs)}개다")
    if not pubs:
        return
    cls = pubs[0]
    execute = next((n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "execute"), None)
    if execute is None:
        out.add("#635", rel, f"실행 메서드는 `execute` 하나다 — `{cls.name}` 에 없다")
        return
    a = execute.args
    n_params = len(a.posonlyargs) + len(a.args) + len(a.kwonlyargs) - 1  # self 제외
    if n_params != 1 or a.vararg or a.kwarg:
        out.add("#635", rel, "`execute` 는 자기 `_command`/`_query` 의 계약 객체 «하나»를 받는다")
    if execute.returns is not None:
        r = execute.returns
        if isinstance(r, ast.Subscript):
            base = r.value
            base_name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
            if base_name in ITERATOR_NAMES:
                inner = _ann_idents(r.slice)
                if not any(i.endswith("Result") for i in inner):
                    out.add("#211", rel, "흐름을 내보내는 유스케이스는 `Iterator[<UseCase>Result]` 로 돌려준다 — 흐르는 알맹이가 result 가 아니다")
                return
        is_none = isinstance(r, ast.Constant) and r.value is None
        if not is_none and not any(i.endswith("Result") for i in _ann_idents(r)):
            out.add("#635", rel, "`execute` 는 `<use_case>_result.py` 의 result 를 돌려준다(빈 result 짝이면 `-> None`)")

    # #194 후보 — 유스케이스 안 업무 규칙(조건이 «무엇이 옳은가»를 가르기 시작)
    for node in ast.walk(execute):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        comparators = [n for n in ast.walk(test) if isinstance(n, ast.Compare)]
        if any(isinstance(op, (ast.Is, ast.IsNot)) for c in comparators for op in c.ops):
            continue  # 존재 확인(`is None`)은 제외
        if any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute) for n in ast.walk(test)):
            cand.add("#194", f"{rel}:{node.lineno}", "조건이 도메인 속성 깊이를 들여다본다 — 업무 규칙이면 도메인으로 내린다", "Q2(이 판정의 주인이 유스케이스인가)")
            break


# ── DTO 파일 내용 — #202 · #205 · #189 · #208 · #567 ───────────────────────

def _check_dto_file(f: Path, rel, out: Findings) -> None:
    mod = _parse(f)
    if mod is None:
        return
    # #67 — 응용 DTO 는 raise 하지 않는다(검사 자리는 입구와 도메인 둘뿐 — D30 백스톱 S1).
    #       (rule-owner-map 정정: 키워드 «백스톱»이 checker_lint 로 오배정했었다 — #609 전례)
    for node in ast.walk(mod):
        if isinstance(node, ast.Raise):
            out.add("#67", rel,
                    f"응용 DTO 가 raise 한다(:{node.lineno}) — `<use_case>_{{command,query,result}}` 는 "
                    "검증하지 않는다(검사 자리는 입구(schema_in)와 도메인 둘뿐이다)")
            break
    for mod_path, _names in _import_records(mod):
        kind = _domain_kind(mod_path)
        if kind in ("entity", "aggregate"):
            out.add("#202", rel, f"DTO 에는 애그리거트도 엔티티도 담기지 않는다 — `{mod_path}` (값 객체는 그대로 온다 · #207)")
        elif _is_orm_import(mod_path):
            out.add("#202", rel, f"DTO 에 ORM 행이 담기지 않는다 — `{mod_path}`")
        parts = mod_path.split(".")
        if any(p in DRIVING_NAMES for p in parts):
            out.add("#208", rel, f"`_command` 은 `schema_in` 과 짝이지만 «같은 타입»을 쓰지 않는다 — `{mod_path}` import 는 안이 바깥을 아는 것이다")


def _check_cross_use(app: Path, rel_base, out: Findings) -> None:
    """#205·#189 — 유스케이스끼리 DTO·모듈을 돌려쓰지 않는다(application_layer 안만 본다)."""
    for f in sorted(app.rglob("*.py")):
        rp = f.relative_to(app).parts
        if set(rp) & SKIP_DIRS or len(rp) < 3 or rp[0] == "port":
            continue
        my_area, my_uc = rp[0], rp[1]
        mod = _parse(f)
        if mod is None:
            continue
        for mod_path, _names in _import_records(mod):
            parts = mod_path.split(".")
            if "application_layer" not in parts:
                continue
            i = parts.index("application_layer")
            rest = parts[i + 1:]
            if len(rest) < 3 or rest[0] == "port":
                continue  # port 참조와 area 직계 참조는 이 규칙 밖(후자의 존재 자체를 skeleton #490 이 잡는다)
            area, uc, module = rest[0], rest[1], rest[2]
            if (area, uc) == (my_area, my_uc):
                continue
            if module.endswith(("_command", "_query", "_result")):
                out.add("#205", rel_base / Path(*rp), f"DTO 는 자기 유스케이스 폴더 안에서만 쓰인다 — `{mod_path}` 는 남의 계약이다")
            else:
                out.add("#189", rel_base / Path(*rp), f"`<use_case>/` 안 모듈은 그 유스케이스 소유다 — 남의 폴더를 import 하지 않는다(공유는 도메인/port/framework 로 «내리고», 남으면 중복한다) — `{mod_path}`")


def _check_dto_names(app: Path, rel_base, out: Findings) -> None:
    """#567 — `dto` 는 Fowler 의 «프로세스 사이» 패턴 이름이라 쓰지 않는다."""
    for f in sorted(app.rglob("*.py")):
        rp = f.relative_to(app).parts
        if set(rp) & SKIP_DIRS:
            continue
        if "dto" in f.stem.lower().split("_"):
            out.add("#567", rel_base / Path(*rp), "파일 이름에 `dto` 를 쓰지 않는다 — `schema` 는 기술 실물, 자료는 `_command`/`_query`/`_result` 다")
            continue
        mod = _parse(f)
        if mod is None:
            continue
        for cls in _top_public_classes(mod):
            if "dto" in re.sub(r"(?<!^)(?=[A-Z])", "_", cls.name).lower().split("_"):
                out.add("#567", rel_base / Path(*rp), f"클래스 이름에 `Dto` 를 쓰지 않는다 — `{cls.name}`")


# ── 사실 발행 세 걸음 — #539 · #540 · #541 ──────────────────────────────────

def _check_event_steps(f: Path, rel, is_repository: bool, out: Findings) -> None:
    mod = _parse(f)
    if mod is None:
        return
    pulled_names: set[str] = set()
    callback_names: set[str] = set()  # after_commit 에 «참조»로 등록된 이름 — 그 정의 안은 커밋 후다
    for node in ast.walk(mod):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn = node.value.func
            if isinstance(fn, ast.Attribute) and fn.attr == "pull_events":
                pulled_names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "after_commit":
            for arg in node.args:
                nm = arg.attr if isinstance(arg, ast.Attribute) else getattr(arg, "id", "")
                if nm:
                    callback_names.add(nm)
            for arg in node.args:
                direct_pull = isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == "pull_events"
                as_is = isinstance(arg, ast.Name) and arg.id in pulled_names
                if direct_pull or as_is:
                    out.add("#540", rel, "도메인 사실을 «그대로» 브로커에 넘기면 위반이다 — 유스케이스가 옮겨 담는다(타입이 다르고 1:1 도 아니다)")

    def _scan(stmts: list, scope: str) -> None:
        for node in stmts:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _scan(node.body, node.name)
                continue
            if isinstance(node, ast.ClassDef):
                _scan(node.body, scope)
                continue
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Call) or not isinstance(sub.func, ast.Attribute):
                    continue
                if sub.func.attr == "pull_events" and is_repository:
                    out.add("#539", rel, "`pull_events()` 는 «유스케이스가» 부른다 — 리포지토리 구현이 부르면 저장 경계 자동 수거(D59 기각안)다")
                if sub.func.attr == "publish" and not is_repository and scope not in callback_names:
                    out.add("#541", rel, "커밋 «전» 발행이다 — 발행은 `uow.after_commit(...)` 에 «참조»로 넘긴다(직접 `.publish(` 호출 금지)")

    _scan(mod.body, "<module>")


# ── schema · 컨트롤러 — #139 · #140 · #142 · #143 · #144 · #210 · #196 ─────

def _check_schema_in(f: Path, rel, out: Findings, cand: Candidates) -> None:
    mod = _parse(f)
    if mod is None:
        return
    for mod_path, _names in _import_records(mod):
        kind = _domain_kind(mod_path)
        if kind in ("entity", "aggregate"):
            out.add("#142", rel, f"요청 스키마는 도메인 객체를 만들지 않는다 — `{mod_path}` (값 객체 import 만 면제 · #141)")
    # #140 후보 — 제약 선언이 0 인 스키마(첫 관문이 비어 있다는 신호)
    has_fields = False
    has_constraint = False
    for node in ast.walk(mod):
        if isinstance(node, ast.AnnAssign):
            has_fields = True
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if nm in ("Field", "constr", "conint", "condecimal", "confloat"):
                has_constraint = True
        if isinstance(node, ast.FunctionDef) and any("validator" in _ann_idents(d) or "validator" in ast.dump(d) for d in node.decorator_list):
            has_constraint = True
    if has_fields and not has_constraint:
        cand.add("#140", rel, "제약 선언(Field·validator)이 0 인 스키마다 — 첫 관문이 비었을 수 있다", "Q2(검증이 다른 자리로 샜나)")


def _check_schema_out(f: Path, rel, out: Findings) -> None:
    mod = _parse(f)
    if mod is None:
        return
    for mod_path, _names in _import_records(mod):
        kind = _domain_kind(mod_path)
        if kind in ("entity", "aggregate"):
            out.add("#144", rel, f"응답 스키마가 도메인 타입을 직접 노출한다 — `{mod_path}` (`schema_out` 은 `<use_case>_result` 을 받아 만든다 · #143)")
        elif _is_orm_import(mod_path):
            out.add("#144", rel, f"응답 스키마에 ORM 행을 싣지 않는다 — `{mod_path}`")


def _check_controller(f: Path, rel, bc: Path, out: Findings, cand: Candidates) -> None:
    mod = _parse(f)
    if mod is None:
        return
    vo_names: set[str] = set()
    for mod_path, names in _import_records(mod):
        kind = _domain_kind(mod_path)
        if kind == "exception" and not _lawful_domain_exception_import(mod_path, names, bc):
            out.add("#210", rel, f"컨트롤러는 `<use_case>_result` 만 보고 응답을 만든다 — `{mod_path}` 로 도메인을 들여다본다(예외 면제는 같은 BC `exception/` 직계 모듈의 실선언 예외 클래스뿐 — #95)")
        elif kind in ("entity", "aggregate", "other"):
            out.add("#210", rel, f"컨트롤러는 `<use_case>_result` 만 보고 응답을 만든다 — `{mod_path}` 로 도메인을 들여다본다")
        elif kind == "value_object":
            vo_names.update(names)
    for node in ast.walk(mod):
        if isinstance(node, ast.Call):
            fn = node.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if nm in ("Field", "constr", "conint", "condecimal", "confloat"):
                out.add("#139", rel, "필드·범위 제약은 `schema_in.py` 에 선언한다 — 컨트롤러의 제약 선언은 자리가 틀렸다")
        # #103 후보 — 값 객체 사용이 «파싱·되돌려 굽기» 폭을 넘는 것
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in vo_names:
            cand.add("#103", f"{rel}:{node.lineno}", f"입구가 값 객체 `{node.value.id}` 의 속성을 들여다본다", "「이것이 «되돌려 굽기»인가 업무 사용인가」")


def _check_boundary_names(app: Path, rel_base, out: Findings) -> None:
    for f in sorted(app.rglob("*.py")):
        rp = f.relative_to(app).parts
        if set(rp) & SKIP_DIRS:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        for cls in _top_public_classes(mod):
            if any(cls.name.endswith(tok) for tok in BOUNDARY_TOKENS):
                out.add("#196", rel_base / Path(*rp), f"Input/Output Boundary·Presenter 는 `application_layer` 에 넣지 않는다 — `{cls.name}`")


def _check_validation_raises(scan_root: Path, rel_base, cand: Candidates) -> None:
    """#68 후보 — 검증 목적 raise 가 허용 두 자리(schema_in.py·domain_layer/**) 밖."""
    for f in sorted(scan_root.rglob("*.py")):
        rp = f.relative_to(scan_root).parts
        if set(rp) & SKIP_DIRS or "domain_layer" in rp or f.name == "schema_in.py":
            continue
        if rp[0] not in ("application_layer", *DRIVING_NAMES):
            continue
        mod = _parse(f)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if isinstance(node, ast.If) and len(node.body) == 1 and isinstance(node.body[0], ast.Raise):
                cand.add("#68", f"{rel_base / Path(*rp)}:{node.lineno}", "guard 형 raise 가 허용 두 자리(schema_in·domain) 밖에 있다", "Q2(이 검사의 값은 어디서 왔나)")
                break


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
        p for p in target.rglob("application")
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS)
    ]
    bcs: list[Path] = []
    for c in containers:
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))

    if not any(_has_adoption_signal(b) for b in bcs):
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    findings = Findings(defer=True)
    cand = Candidates(defer=True)
    scanned_layers = 0
    for bc in bcs:
        bc_rel = bc.relative_to(target)
        app = _app_layer(bc)
        agg_names: set[str] = set()
        dl = bc / "domain_layer"
        if dl.is_dir():
            agg_dirs, _ = _entries(dl)
            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}

        if app is not None:
            scanned_layers += 1
            ucs = _check_structure(bc, bc_rel, findings)
            for uc in ucs:
                uc_rel = bc_rel / "application_layer" / uc.parent.name / uc.name
                _check_use_case(uc, uc_rel, agg_names, findings, cand)
                for suffix in ("_command.py", "_query.py", "_result.py"):
                    f = uc / f"{uc.name}{suffix}"
                    if f.is_file():
                        _check_dto_file(f, uc_rel / f.name, findings)
                entry = uc / f"{uc.name}_use_case.py"
                if entry.is_file():
                    _check_event_steps(entry, uc_rel / entry.name, False, findings)
            _check_cross_use(app, bc_rel / "application_layer", findings)
            _check_dto_names(app, bc_rel / "application_layer", findings)
            _check_boundary_names(app, bc_rel / "application_layer", findings)

        api = _driving_api(bc)
        if api is not None:
            for f in sorted(api.rglob("*.py")):
                rel = bc_rel / f.relative_to(bc)
                if set(f.relative_to(bc).parts) & SKIP_DIRS:
                    continue
                if f.name == "schema_in.py":
                    _check_schema_in(f, rel, findings, cand)
                elif f.name == "schema_out.py":
                    _check_schema_out(f, rel, findings)
                elif f.name.endswith("_controller.py"):
                    _check_controller(f, rel, bc, findings, cand)

        for layer_name in DRIVEN_NAMES:
            repo_dir = bc / layer_name / "adapter" / "persistence" / "repository"
            if repo_dir.is_dir():
                for f in sorted(repo_dir.glob("*.py")):
                    _check_event_steps(f, bc_rel / f.relative_to(bc), True, findings)

        _check_validation_raises(bc, bc_rel, cand)

    if bcs and scanned_layers == 0 and not findings:
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 `application_layer/` 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    if cand:
        print(f"ⓓ 후보 {len(cand)}건 — 기계가 좁힌 후보다(exit 불산입). 마무리는 discipline-reviewer 의 물음이 한다:")
        emit_all(cand, printer=print, indent="  ")
    if findings:
        print(f"blocker {len(findings)}건 — 유스케이스·경계 자료 규율 위반")
        emit_all(findings, printer=print, indent="  ")
        return 2
    print(f"clean — BC {len(bcs)}개 · 자료 계약 규율 일치 (트리 39~44행 · standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
