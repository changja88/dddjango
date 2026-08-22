#!/usr/bin/env python3
"""dddjango 트랜잭션 경계 검사기 — 「한 트랜잭션 = 애그리거트 하나」(D50) 축의 결정적 백스톱.

리포지토리 «파일» 계약(트리 68행)과 유스케이스의 쓰기 규율을 강제한다.

담당 규칙 (rule-owner-map · 총 11 — #343 은 admin 가족이라 check-naming 이관):
  #4   [ast]  `application_layer/**` 의 import 에 django 가 하나라도 있으면 위반 —
              트랜잭션도 시각도 DB 예외도 포트를 거친다(D4+D31).
  #195 [ast]  상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다 — save/remove
              인자는 «같은 함수 안에서 루트 메서드 호출을 받은» 객체여야 하고, UoW 를
              받았는데 루트 메서드 호출이 0 이어도 위반.
  #197 [ast]  읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다 — `*UnitOfWork` 파라미터가
              있는데 본문에 `with uow:`·save·remove·after_commit 이 0 이면 위반.
  #200 [ast]  커밋 뒤 부작용은 `unit_of_work.after_commit(...)` — 응용이
              `transaction.on_commit`·`connection.in_atomic_block` 을 직접 부르면 위반.
  #282 [path] 리포지토리 선언은 폴더가 아니라 `<aggregate>_repository.py` 파일이다.
  #283 [ast]  `<aggregate>_repository.py` 는 추상 메서드만 갖는다(계약이지 구현이 아니다).
  #285 [ast+] 요약값(exists→bool·count→int)은 리포지토리에 남는다 — bypass query 포트의
              bool/int 반환 메서드는 ⓓ 후보(「이 수가 애그리거트 컬렉션을 센 것인가」).
  #287 [ast]  쓰기 인자는 «애그리거트»다 — `update_*` 필드 갱신 메서드·조건/필드 인자면 위반.
  #355 [ast+] 확정: 리포지토리 반환이 {애그리거트, Sequence[애그리거트], 값객체,
              bool·int·None} 밖(QuerySet·Model·dict·str) / 후보: bool·int 로 남은 것
              (「주어가 애그리거트인가 화면인가」).
  #597 [ast]  애그리거트 리포지토리의 쓰기 메서드 이름은 save·remove 로 시작한다 —
              add/store/persist/delete/insert 접두면 위반. 거꾸로(비리포지토리의 save)는
              안 문다 — 세는 대상은 «이름»이 아니라 «타입이 온 파일»(predicates ⓓ).
  #599 [ast]  `save_all()` 조건 셋 — ㉠구현이 트랜잭션을 열면 위반(atomic) ㉡맨
              bulk_update(경합 가드 없음)면 위반 ㉢`add_all` 은 열지 않는다.

판정의 자(predicates ⓓ): 「무엇이 리포지토리인가」는 이름이 아니라 «타입이
`<aggregate>_repository.py` 에서 온 것»으로 가른다 — audit_log.save() 는 안 걸린다.

단순화(정직 기록): #195 의 «루트 메서드 호출을 받은 객체» 판정은 지역 흐름만 본다 —
save 인자가 같은 함수에서 메서드 호출을 받았거나 도메인 팩토리 호출로 태어났으면 통과,
`obj.field = x` 직접 대입만 받았거나 아무 일도 없었으면 위반.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74, touched 필터 없음) ·
ImportError fail-closed. ⓓ 후보는 exit 에 불산입, `[ⓓ#N]` 으로만 출력.

사용법: check-transaction-boundary.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2). 방출은 공용 ordered emitter
(emit_all) 경유 — stdout 위반·후보 라인 순서와 레코드 순서가 같고, 라인은 레코드
필드의 순수 함수다(출력 계약 v2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#74 → djr:R-3229.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import ast
import sys

import checker_target
from findings import Candidates, Findings, emit_all, zero_target_guard
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
DRIVEN_DIRS = ("driven_layer",)

# #597 — save·remove 밖의 쓰기 동사 접두(데이터 목록 — 닫지 않는다: predicates ⓒ).
WRITE_PREFIX_BAN = ("add", "store", "persist", "insert", "put", "delete", "upsert", "create")
# #355 — 반환 허용 이름(애그리거트·값객체는 import 해소로 더한다).
RETURN_WRAPPERS = {"Sequence", "list", "List", "Iterable", "Iterator", "tuple", "Tuple", "Optional", "Union"}
RETURN_PRIMITIVES = {"bool", "int", "None"}
RETURN_BAN = {"QuerySet", "dict", "Dict", "str", "float"}


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


# ── #4 · #200 — application_layer 의 django 격리 ────────────────────────────

def _check_application_purity(root: Path, app_layer: Path, f: Findings) -> None:
    for py in _py_files(app_layer):
        mod = _parse(py)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name == "django" or a.name.startswith("django."):
                        f.add("#4", _rel(root, py, node.lineno),
                              "application_layer 가 django 를 import 한다 — 트랜잭션·시각·DB 예외는 포트를 거친다")
            elif isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if m == "django" or m.startswith("django."):
                    f.add("#4", _rel(root, py, node.lineno),
                          "application_layer 가 django 를 import 한다 — 트랜잭션·시각·DB 예외는 포트를 거친다")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                fn = node.func
                if fn.attr == "on_commit" and isinstance(fn.value, ast.Name) and fn.value.id == "transaction":
                    f.add("#200", _rel(root, py, node.lineno),
                          "transaction.on_commit 직접 호출 — 커밋 뒤 부작용은 unit_of_work.after_commit(...) 에 맡긴다")
            elif isinstance(node, ast.Attribute) and node.attr == "in_atomic_block":
                f.add("#200", _rel(root, py, node.lineno),
                      "connection.in_atomic_block 직접 접근 — 트랜잭션 상태는 UnitOfWork 가 가린다")


# ── #282 — 리포지토리는 폴더가 아니라 파일 ──────────────────────────────────

def _domain_layer(bc: Path) -> Path | None:
    d = bc / "domain_layer"
    return d if d.is_dir() else None


def _aggregate_dirs(domain: Path) -> list[Path]:
    skip = {"shared_value_object", "domain_service", "__pycache__"}
    return [p for p in sorted(domain.iterdir()) if p.is_dir() and p.name not in skip]


def _check_repository_files(root: Path, bc: Path, f: Findings) -> list[Path]:
    """#282. 반환: 발견한 애그리거트 리포지토리 파일들(뒤 검사의 대상)."""
    domain = _domain_layer(bc)
    if domain is None:
        return []
    repos: list[Path] = []
    for agg in _aggregate_dirs(domain):
        if (agg / "repository").is_dir():
            f.add("#282", _rel(root, agg / "repository"),
                  "리포지토리가 폴더다 — 선언은 애그리거트당 하나라 `<aggregate>_repository.py` 파일이다")
        for p in sorted(agg.glob("*_repository.py")):
            if p.stem != f"{agg.name}_repository":
                f.add("#282", _rel(root, p),
                      f"리포지토리 파일 이름이 애그리거트와 다르다 — `{agg.name}_repository.py` 여야 한다")
            repos.append(p)
    return repos


# ── #283 · #287 · #355 · #597 · #599㉢ — 리포지토리 파일 계약 ───────────────

def _annotation_names(node: ast.AST | None) -> set[str]:
    names: set[str] = set()
    if node is None:
        return names
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            try:
                names |= _annotation_names(ast.parse(n.value, mode="eval").body)
            except SyntaxError:
                pass
    return names


def _camel(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split("_"))


def _value_object_imports(mod: ast.Module) -> set[str]:
    """import 경로가 value_object·shared_value_object·자기 애그리거트 모듈인 심볼."""
    ok: set[str] = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom):
            m = node.module or ""
            if "value_object" in m or "domain_layer" in m:
                ok |= {a.asname or a.name for a in node.names}
    return ok


def _check_repository_contract(root: Path, repo_path: Path, agg_name: str,
                               f: Findings, cand: Candidates) -> None:
    mod = _parse(repo_path)
    if mod is None:
        return
    agg_class = _camel(agg_name)
    domain_syms = _value_object_imports(mod)
    for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
        for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            decos = {d.id if isinstance(d, ast.Name) else getattr(d, "attr", "") for d in m.decorator_list}
            if m.name.startswith("__"):
                continue
            # #283 — 추상 메서드만.
            if "abstractmethod" not in decos:
                f.add("#283", _rel(root, repo_path, m.lineno),
                      f"`{m.name}` 에 @abstractmethod 가 없다 — 리포지토리 선언은 구현이 아니라 계약이다")
            args = [a for a in m.args.args if a.arg not in ("self", "cls")]
            # #597 — 쓰기 이름은 save·remove 로 시작.
            first = m.name.split("_", 1)[0]
            if first in WRITE_PREFIX_BAN:
                if m.name == "add_all":
                    f.add("#599", _rel(root, repo_path, m.lineno),
                          "`add_all` 은 열지 않는다 — 일괄 쓰기는 `save_all` 뿐이다(T37)")
                else:
                    f.add("#597", _rel(root, repo_path, m.lineno),
                          f"쓰기 메서드 `{m.name}` — 애그리거트 리포지토리의 쓰기 이름은 save·remove 로 시작한다"
                          "(갈리면 「한 트랜잭션 = 애그리거트 하나」(#546) 검사가 못 선다)")
            # #287 — 쓰기 인자는 애그리거트다.
            if first == "update" or m.name == "bulk_update":
                f.add("#287", _rel(root, repo_path, m.lineno),
                      f"필드 단위 갱신 `{m.name}` — 판정이 SQL 로 가면 같은 판정의 도메인 메서드가 죽은 코드가 된다")
            if first in ("save", "remove"):
                prim = {"str", "int", "bool", "dict", "float"}
                if len(args) >= 2:
                    f.add("#287", _rel(root, repo_path, m.lineno),
                          f"`{m.name}` 인자가 {len(args)}개 — 쓰기 인자는 «애그리거트(또는 그 목록)» 하나다(조건·필드면 위반)")
                elif args and _annotation_names(args[0].annotation) and \
                        _annotation_names(args[0].annotation) <= prim:
                    f.add("#287", _rel(root, repo_path, m.lineno),
                          f"`{m.name}` 인자 타입이 원시값이다 — 쓰기는 애그리거트를 받는다")
            # #355 — 반환형.
            if m.returns is not None and first not in ("save", "remove"):
                names = _annotation_names(m.returns)
                core = names - RETURN_WRAPPERS - RETURN_PRIMITIVES
                if names & RETURN_BAN or any(n.endswith("Model") for n in names):
                    f.add("#355", _rel(root, repo_path, m.lineno),
                          f"`{m.name}` 반환이 {sorted(names & RETURN_BAN | {n for n in names if n.endswith('Model')})} — "
                          "리포지토리는 {애그리거트, Sequence[애그리거트], 값객체, bool·int·None} 만 돌려준다")
                elif core and not (core & {agg_class} or core <= domain_syms):
                    f.add("#355", _rel(root, repo_path, m.lineno),
                          f"`{m.name}` 반환 `{'.'.join(sorted(core))}` 이 애그리거트도 값 객체도 아니다")
                elif not core and names & {"bool", "int"}:
                    cand.add("#355", _rel(root, repo_path, m.lineno),
                             f"`{m.name}` 이 bool/int 를 돌려준다(요약값은 리포지토리에 남는 것이 맞다 — #285)",
                             "이 메서드의 주어가 애그리거트인가 화면인가")


# ── #285 — bypass query 포트의 요약값 후보 ──────────────────────────────────

def _check_bypass_query_summary(root: Path, bc: Path, cand: Candidates) -> None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return
    for py in _py_files(app_layer):
        parts = py.relative_to(bc).parts
        if "domain_bypass_query" not in parts or not py.name.endswith("_query.py"):
            continue
        mod = _parse(py)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                names = _annotation_names(node.returns)
                if names and names <= {"bool", "int"}:
                    cand.add("#285", _rel(root, py, node.lineno),
                             f"bypass query `{node.name}` 이 {sorted(names)} 요약값을 돌려준다 — "
                             "애그리거트 컬렉션을 세고 합친 값(exists·count)은 리포지토리에 남는다",
                             "이 수가 «애그리거트 컬렉션»을 세거나 합친 것인가")


# ── #195 · #197 — 유스케이스의 쓰기 규율 ────────────────────────────────────

def _repo_param_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    out = set()
    for a in fn.args.args + fn.args.kwonlyargs:
        if any(n.endswith("Repository") for n in _annotation_names(a.annotation)):
            out.add(a.arg)
    return out


def _uow_param_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    out = set()
    for a in fn.args.args + fn.args.kwonlyargs:
        if any(n.endswith("UnitOfWork") for n in _annotation_names(a.annotation)):
            out.add(a.arg)
    return out


def _attr_root(node: ast.AST) -> str | None:
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _init_attr_repos(cls: ast.ClassDef) -> set[str]:
    """__init__ 에서 `self._x = <Repository 애너테이션 파라미터>` 로 물린 속성 이름."""
    out: set[str] = set()
    for m in cls.body:
        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == "__init__":
            repo_params = _repo_param_names(m)
            for st in ast.walk(m):
                target = None
                if isinstance(st, ast.Assign) and len(st.targets) == 1:
                    target, value = st.targets[0], st.value
                elif isinstance(st, ast.AnnAssign) and st.value is not None:
                    target, value = st.target, st.value
                else:
                    continue
                if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                        and target.value.id == "self" and isinstance(value, ast.Name)
                        and value.id in repo_params):
                    out.add(target.attr)
    return out


def _check_use_case_writes(root: Path, bc: Path, f: Findings) -> None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return
    for py in _py_files(app_layer):
        if not py.name.endswith("_use_case.py"):
            continue
        mod = _parse(py)
        if mod is None:
            continue
        classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
        for cls in classes:
            attr_repos = _init_attr_repos(cls)
            attr_uows: set[str] = set()
            for m in cls.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == "__init__":
                    uow_params = _uow_param_names(m)
                    for st in ast.walk(m):
                        target = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1:
                            target, value = st.targets[0], st.value
                        elif isinstance(st, ast.AnnAssign) and st.value is not None:
                            target, value = st.target, st.value
                        else:
                            continue
                        if isinstance(target, ast.Attribute) and isinstance(value, ast.Name) \
                                and value.id in uow_params:
                            attr_uows.add(target.attr)
            for m in cls.body:
                if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) or m.name.startswith("_"):
                    continue
                _check_execute_body(root, py, m, attr_repos, attr_uows, f)


def _check_execute_body(root: Path, py: Path, fn: ast.FunctionDef | ast.AsyncFunctionDef,
                        attr_repos: set[str], attr_uows: set[str], f: Findings) -> None:
    repo_names = _repo_param_names(fn)
    uow_names = _uow_param_names(fn)
    has_uow = bool(uow_names or attr_uows)

    def _is_repo_recv(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in repo_names
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
            return node.attr in attr_repos
        return False

    method_called: set[str] = set()      # 루트 메서드 호출을 받은 이름
    factory_born: set[str] = set()       # 도메인 팩토리/생성자 호출로 태어난 이름
    attr_assigned: set[str] = set()      # obj.field = x 직접 대입을 받은 이름
    writes: list[tuple[str, ast.Call]] = []
    uses_uow_api = False

    for node in ast.walk(fn):
        if isinstance(node, ast.With):
            for item in node.items:
                r = _attr_root(item.context_expr)
                if r in uow_names or (isinstance(item.context_expr, ast.Attribute)
                                      and item.context_expr.attr in attr_uows):
                    uses_uow_api = True
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            fn_node = node.value.func
            if isinstance(fn_node, (ast.Name, ast.Attribute)) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                callee_root = _attr_root(fn_node)
                if not _is_repo_recv(fn_node.value if isinstance(fn_node, ast.Attribute) else fn_node) \
                        and callee_root not in repo_names:
                    factory_born.add(name)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                    attr_assigned.add(t.value.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            recv, meth = node.func.value, node.func.attr
            if _is_repo_recv(recv):
                if meth in ("after_commit",):
                    uses_uow_api = True
                if meth.split("_", 1)[0] in ("save", "remove"):
                    arg = node.args[0] if node.args else None
                    writes.append((arg.id if isinstance(arg, ast.Name) else "", node))
            elif isinstance(recv, ast.Name):
                method_called.add(recv.id)
            if meth == "after_commit":
                uses_uow_api = True

    # #197 — UoW 를 받았는데 쓰기 API 를 하나도 안 쓴다.
    if has_uow and not writes and not uses_uow_api:
        f.add("#197", _rel(root, py, fn.lineno),
              f"`{fn.name}` 이 UnitOfWork 를 받는데 with/save/remove/after_commit 이 없다 — "
              "읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다")

    # #195 — save 인자가 루트 메서드 호출을 받은 객체인가.
    for arg_name, call in writes:
        if not arg_name:
            continue
        if arg_name in method_called or arg_name in factory_born:
            continue
        why = ("루트 메서드 호출 없이 필드 직접 대입만 받았다" if arg_name in attr_assigned
               else "같은 함수 안에서 루트 메서드 호출을 받은 적이 없다")
        f.add("#195", _rel(root, py, call.lineno),
              f"save/remove 인자 `{arg_name}` — {why}. 상태 변경은 애그리거트를 건너뛰지 않는다")
    if has_uow and writes and not (method_called or factory_born):
        f.add("#195", _rel(root, py, fn.lineno),
              f"`{fn.name}` 이 UnitOfWork 로 쓰기를 하는데 루트 메서드 호출이 0 이다")


# ── #599㉠㉡ — save_all 구현 조건 ───────────────────────────────────────────

def _check_save_all_impl(root: Path, bc: Path, f: Findings) -> None:
    for layer in DRIVEN_DIRS:
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            mod = _parse(py)
            if mod is None:
                continue
            for node in ast.walk(mod):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name != "save_all":
                    continue
                has_atomic = has_bulk = has_lock = False
                for n in ast.walk(node):
                    if isinstance(n, ast.Attribute):
                        if n.attr == "atomic":
                            has_atomic = True
                        elif n.attr == "bulk_update":
                            has_bulk = True
                        elif n.attr == "select_for_update":
                            has_lock = True
                if has_atomic:
                    f.add("#599", _rel(root, py, node.lineno),
                          "save_all 이 트랜잭션을 연다(atomic) — ㉠ `with unit_of_work:` 안에서만 불린다")
                if has_bulk and not has_lock:
                    f.add("#599", _rel(root, py, node.lineno),
                          "save_all 이 맨 bulk_update 다 — ㉡ WHERE 가 pk IN 뿐이라 "
                          "「내가 읽은 뒤 남이 바꿨다」를 못 잡는다(경합 가드 유지)")


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
    findings = Findings(defer=True)
    cand = Candidates(defer=True)

    domain_seen = 0
    for bc in adopted:
        app_layer = bc / "application_layer"
        if app_layer.is_dir():
            _check_application_purity(root, app_layer, findings)
            _check_use_case_writes(root, bc, findings)
            _check_bypass_query_summary(root, bc, cand)
        domain = _domain_layer(bc)
        if domain is not None:
            domain_seen += 1
            repos = _check_repository_files(root, bc, findings)
            for repo in repos:
                _check_repository_contract(root, repo, repo.stem[: -len("_repository")], findings, cand)
        _check_save_all_impl(root, bc, findings)

    # 대상 0건 가드(#74) — 채택 신호가 있는데 검사 대상 층이 하나도 안 열리면 경로 계약이 깨진 것.
    if adopted and domain_seen == 0 and not any((bc / "application_layer").is_dir() for bc in adopted):
        # 가드 발화 시에도 이미 수집된 레코드는 보존한다(라인 무인쇄 — 구판 add 시점
        # 방출과 동치 · MEDIATION-3 M3/R4). 세그먼트 순서는 정상 경로와 같다(cand→findings).
        emit_all(cand, findings, printer=None)
        guard = zero_target_guard(
            "blocker — 표준 채택 신호가 있는데 domain_layer/application_layer 대상이 0건이다 (경로 계약 불일치 — #74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    emit_all(cand, printer=print, indent="")
    if findings:
        print("blocker — 트랜잭션 경계 위반 (한 트랜잭션 = 애그리거트 하나 · D50)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
