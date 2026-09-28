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
save 인자가 같은 함수에서 메서드 호출을 받았거나 팩토리 호출로 태어났으면 통과(스칼라의
«팩토리 호출» = 리포지토리가 수신자가 아닌 호출 전부라 넓다 — `next(iter(조회))` 도 통과한다),
`obj.field = x` 직접 대입만 받았거나 아무 일도 없었으면 위반. 반복 변수(for·컴프리헨션
target)는 두 모양을 돌 때만 «팩토리로 태어남»을 물려받는다 — ① 원소식이 팩토리 호출인
컬렉션(`[F(..) for ..]`·`tuple(F(..) for ..)` 와 그 이름) ② 인자 없는 도메인 컬렉션 팩토리
호출(`C.m()`·`tuple(C.m())` 과 그 이름). ②의 C 는 같은 BC `domain_layer` 에서 최상위 절대
`from <…>.application.<bc>.domain_layer.<…> import C` 로 들여온 클래스(import 경로는 대상 루트
기준 모듈 경로의 접미여야 한다), m 은 C 의 본문에 직접 정의된 동기 @classmethod/@staticmethod
로 반환 애너테이션이 C(또는 Self)의 컬렉션(`tuple[C, ...]`·`list[C]`·`Sequence[C]` 등)인
것이다 — 도메인은 바깥을 import 하지 못하므로(#8·#1 — import 문 기준) 입력 없는 도메인 호출은
조회된 애그리거트를 손에 쥘 길이 없다(2026-09-28 R8-D2). 이 가정 밖: 클래스 속성·모듈
전역(기본값 인자 포함)에 상태 — 받은 인스턴스·자기 등록 레지스트리·주입된 로더/리포지토리
(서비스 로케이터)·그것을 내놓는 제너레이터·공유 가변 list 를 그대로 돌려주는 메서드 — 를 두는
도메인과 `importlib` 우회는 이 전파를 속이며, 애그리거트 모듈의 이런 상태는 어느 검사기도 막지
않는다(스칼라 채널은 수리 전부터 같은 통로가 더 넓게 열려 있다). 그 밖의 «컬렉션을 돌려주는 호출»
— 인자를 받는 도메인 컬렉션 팩토리·선별 헬퍼(`C.m(xs)`)·리포지토리 조회·비도메인 호출 — 과
튜플 언패킹·필터 체인·리터럴 목록·sorted/map/zip 은 전파하지 않는다. 상속한 메서드
(`Sub.m()`)·async 메서드·`list[C] | None`·`Optional[...]` 선언, 상대 import·모듈 경유 호출
(`mod.C.m()`)·최상위 밖(`if TYPE_CHECKING:`) import·`__init__` 재수출 경유 클래스, 모듈
범위에서 다시 묶이거나(`try` 안 재 import 포함) `global` 로 선언되거나 그 함수에서 다시 묶인
C 도 해소하지 않는다(fail-closed). 판정은 이름 단위이며 fail-closed 다 — 컬렉션 이름은 모든
결속이 단순 대입(`x = v`·`x: T = v`)이고 값이 원소 팩토리일 때만(값이 가리키는 이름도 같은 조건 —
대입 순서와 무관) 원소 출처를 물려준다. 값이 가변 컬렉션(list·set 등)이면 여기에 더해 그 이름이
반복 원천·복사 래퍼 인자(반복 원천이나 단순 대입 우변에 놓인 `tuple(x)`·`list(x)` 등)·원소를
들이지 못하는 순수 읽기 자리 — `len(x)`·`bool(x)`·`isinstance(x, …)` 인자, 비교 피연산자(`==`·
`!=`·`in`·`not in`·`is`·`is not`), `x.sort(..)`·`x.reverse()`, `if x`·`not x` 류 조건, 이 함수
자신의 `return x`(복사 포함) — 밖에서 읽히지 않아야 한다. 별칭·호출 인자(로깅·도메인 검증기·결과
DTO 포함)·그 밖의 메서드 수신(`extend`·`append`·`insert` 등)·첨자 대입·`+=`·`locals()`/`vars()`·
중첩 def 의 `return x` 같은 탈출이 하나라도 있으면 물려주지 않는다 — 그래서 가변 컬렉션 이름을
호출 인자로 넘기는 모양은 F4-20 때 통과했더라도 전파를 잃는다(fail-closed 비용 · 피호출자가
원소를 넣을 수 있다). 모든 값이 불변 컬렉션(함수 안에서 가려지지 않은 `tuple(..)`·`frozenset(..)`·
제너레이터 식)인 이름은 내용이 바뀌지 않으므로 탈출을 보지 않는다. 반복 변수는 이 함수 안의 결속 가운데 단순 대입·단일
이름 반복 target 밖의 것(이 함수의 파라미터·`:=`·`+=`·언패킹·with/except as·`match` 캡처·함수 안
import·def)이 하나라도 있으면 물려받지 않는다. 한계(fail-open): 중첩 def·lambda 의 파라미터는
결속으로 보지 않아 동명 파라미터로 조회 인스턴스를 save 하는 모양을 놓치고, 복사 래퍼·순수 읽기
이름(`list`·`tuple`·`len`·`isinstance` 등)이 내장인지는 보지 않아 함수 안 `list = …` 가림에
속으며, 비교·`in` 의 상대 객체가 사용자 정의 `__eq__`/`__contains__` 로 피연산자를 바꾸는 코드는
가정 밖이다(2026-09-26 F4-20 · 2026-09-29 R8-D2 리뷰 M-1 · 재검토 M-1·m-1 · 순수 읽기 확장).

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
# #195 — 도메인 컬렉션 팩토리의 반환 애너테이션 바깥 이름(반복 원소 전파 · R8-D2).
COLLECTION_RETURNS = {"tuple", "Tuple", "list", "List", "Sequence", "frozenset", "FrozenSet",
                      "set", "Set", "Iterable", "Iterator", "Collection"}
# #195 — `match` 캡처 결속 노드(3.10+ · 그 아래 파이썬에는 match 문 자체가 없다).
MATCH_CAPTURES = tuple(t for t in (getattr(ast, "MatchAs", None), getattr(ast, "MatchStar", None)) if t)
MATCH_MAPPING = getattr(ast, "MatchMapping", None)
# #195 — 컬렉션 이름을 원소를 들이지 않고 읽는 비교 연산자.
PURE_COMPARE_OPS = (ast.Eq, ast.NotEq, ast.In, ast.NotIn, ast.Is, ast.IsNot)


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


def _uow_write_reach(fn: ast.FunctionDef | ast.AsyncFunctionDef,
                     helpers: "dict[str, ast.FunctionDef | ast.AsyncFunctionDef]",
                     attr_uows: set[str], attr_repos: set[str]) -> bool:
    """#197 도달 범위의 쓰기-사용 판정(스펙 대장 #197 — 부칙 아님·측정 정밀화 2026-08-25).

    «with uow» 진입 자체는 쓰기 API 사용이 아니다 — 그래야 읽기 전용+UoW 를 성문 문면대로
    잡는다(kkebi reconcile 실물). 인정(하나라도 도달하면 True):
      ⓐ repo save/remove·after_commit 직접 호출(uow.repository 수신자 형 포함)
      ⓑ uow.repository 를 콜러블 «인자»로 전달(escape — 외부 콜러블이 그 리포지토리로
         쓰기를 수행할 수 있다는 fail-open 인정 · kkebi import `_run_batch` 실물)
    도달 범위 = 공개 메서드에서 self 헬퍼로의 추이 폐쇄(직접 호출·호출 인자 참조 전달 —
    헬퍼→헬퍼 사슬 포함 · kkebi recover 2단 사슬 실증. 어디서도 안 닿는 죽은 헬퍼는
    불산입). with 인식은 factory 호출형(`with self._factory()`)을 Call 언랩으로 받는다 —
    언랩은 uow 별칭 수집에만 쓰인다.
    """
    scan: "list[ast.FunctionDef | ast.AsyncFunctionDef]" = [fn]
    seen = {fn.name}
    frontier = [fn]
    while frontier:
        cur = frontier.pop()
        for node in ast.walk(cur):
            if not isinstance(node, ast.Call):
                continue
            cands: list[str] = []
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) \
                    and node.func.value.id == "self":
                cands.append(node.func.attr)
            for a in list(node.args) + [kw.value for kw in node.keywords]:
                if isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) \
                        and a.value.id == "self":
                    cands.append(a.attr)
            for name in cands:
                if name in helpers and name not in seen:
                    seen.add(name)
                    scan.append(helpers[name])
                    frontier.append(helpers[name])
    for g in scan:
        uow_names = _uow_param_names(g)
        repo_names = _repo_param_names(g)
        aliases: set[str] = set(uow_names)
        for node in ast.walk(g):
            if isinstance(node, ast.With):
                for item in node.items:
                    expr = item.context_expr
                    if isinstance(expr, ast.Call):
                        expr = expr.func
                    hit = (_attr_root(expr) in uow_names
                           or (isinstance(expr, ast.Attribute) and expr.attr in attr_uows))
                    if hit and isinstance(item.optional_vars, ast.Name):
                        aliases.add(item.optional_vars.id)

        def _is_uow_repo(nd: ast.AST) -> bool:
            return (isinstance(nd, ast.Attribute) and nd.attr == "repository"
                    and isinstance(nd.value, ast.Name) and nd.value.id in aliases)

        for node in ast.walk(g):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute):
                recv, meth = node.func.value, node.func.attr
                if meth == "after_commit":
                    return True
                if meth.split("_", 1)[0] in ("save", "remove"):
                    if (isinstance(recv, ast.Name) and recv.id in repo_names) \
                            or (isinstance(recv, ast.Attribute)
                                and isinstance(recv.value, ast.Name)
                                and recv.value.id == "self" and recv.attr in attr_repos) \
                            or _is_uow_repo(recv):
                        return True
            for a in list(node.args) + [kw.value for kw in node.keywords]:
                if _is_uow_repo(a):
                    return True
    return False


def _domain_class_index(root: Path, bc: Path
                        ) -> "dict[tuple[str, ...], tuple[int, dict[str, ast.ClassDef]]]":
    """같은 BC `domain_layer/**.py` 의 최상위 클래스.

    키 = 대상 루트부터의 모듈 경로, 값 = (BC 폴더부터의 경로 길이, {클래스 이름: 정의}).
    import 경로는 키의 접미이면서 BC 폴더 한 칸 위(`application`)까지 담아야 이 BC 로 해소된다.
    """
    index: "dict[tuple[str, ...], tuple[int, dict[str, ast.ClassDef]]]" = {}
    domain = _domain_layer(bc)
    if domain is None:
        return index
    for py in _py_files(domain):
        mod = _parse(py)
        if mod is not None:
            index[py.relative_to(root).with_suffix("").parts] = (
                len(py.relative_to(bc.parent).parts),
                {n.name: n for n in mod.body if isinstance(n, ast.ClassDef)})
    return index


def _module_rebound_names(mod: ast.Module) -> set[str]:
    """모듈 범위에서 두 번 이상 묶인 이름과 어느 함수에서든 `global` 로 선언된 이름.

    모듈 범위 = 함수·클래스 본문 밖(`if`·`try` 안 포함). import 한 도메인 클래스 이름이 여기
    들면 그 이름의 호출은 도메인 클래스라고 보증할 수 없다.
    """
    counts: "dict[str, int]" = {}
    rebound: set[str] = set()
    stack: "list[ast.AST]" = list(mod.body)
    while stack:
        node = stack.pop()
        names: "list[str]" = []
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.asname or a.name.split(".")[0] for a in node.names]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = [node.name]
            rebound |= {n for g in ast.walk(node) if isinstance(g, ast.Global) for n in g.names}
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names = [node.id]
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names = [node.name]
        for n in names:
            counts[n] = counts.get(n, 0) + 1
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))
    return rebound | {n for n, c in counts.items() if c > 1}


def _returns_own_collection(m: ast.FunctionDef, cls_name: str) -> bool:
    """반환 애너테이션이 C(또는 Self)의 컬렉션인가 — `tuple[C, ...]`·`list[C]`·`Sequence["C"]` 등."""
    ret = m.returns
    if isinstance(ret, ast.Constant) and isinstance(ret.value, str):
        try:
            ret = ast.parse(ret.value, mode="eval").body
        except SyntaxError:
            return False
    if not isinstance(ret, ast.Subscript):
        return False
    outer = ret.value.id if isinstance(ret.value, ast.Name) else getattr(ret.value, "attr", "")
    return outer in COLLECTION_RETURNS and _annotation_names(ret.slice) in ({cls_name}, {"Self"})


def _domain_collection_factories(
        mod: ast.Module,
        domain_classes: "dict[tuple[str, ...], tuple[int, dict[str, ast.ClassDef]]]"
) -> "dict[str, set[str]]":
    """유스케이스 모듈의 {지역 클래스 이름: 도메인 컬렉션 팩토리 메서드 이름들}.

    최상위 절대 `from <…>.application.<bc>.domain_layer.<…> import C` 만 같은 BC 의 클래스
    정의로 해소한다(모듈 범위에서 C 가 다시 묶이면 해소하지 않는다). 도메인 컬렉션 팩토리 =
    클래스 본문에 직접 정의된 동기 `@classmethod`/`@staticmethod` 이고 반환 애너테이션이
    C(또는 Self)의 컬렉션인 메서드. 무인자·지역 가림 조건은 호출 지점(`_elements_factory_born`)이 본다.
    """
    out: "dict[str, set[str]]" = {}
    rebound = _module_rebound_names(mod)
    for node in mod.body:
        if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
            continue
        mparts = tuple(node.module.split("."))
        for parts, (bc_len, classes) in domain_classes.items():
            if not (bc_len < len(mparts) <= len(parts) and parts[-len(mparts):] == mparts):
                continue
            for a in node.names:
                cdef = classes.get(a.name)
                if cdef is None:
                    continue
                meths = {
                    m.name for m in cdef.body
                    if isinstance(m, ast.FunctionDef)
                    and {d.id if isinstance(d, ast.Name) else getattr(d, "attr", "")
                         for d in m.decorator_list} & {"classmethod", "staticmethod"}
                    and _returns_own_collection(m, cdef.name)
                }
                local = a.asname or a.name
                if meths and local not in rebound:
                    out[local] = meths
    return out


def _check_use_case_writes(root: Path, bc: Path, f: Findings) -> None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return
    domain_classes = _domain_class_index(root, bc)
    for py in _py_files(app_layer):
        # rglob+이름 필터라 동명 폴더 승격(#490 교체형)의 본체
        # (`<uc>_use_case/<uc>_use_case.py`)도 그대로 걸린다 — slot_glob 등가.
        # 승격 «부품»의 쓰기 호출 금지(«save 류는 본체에만»)는 승격 형태 규범 가족의
        # 몫(check-layer-skeleton #638~)이라 여기서 스캔을 넓히지 않는다.
        if not py.name.endswith("_use_case.py"):
            continue
        mod = _parse(py)
        if mod is None:
            continue
        collection_factories = _domain_collection_factories(mod, domain_classes)
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
            helpers = {
                m.name: m for m in cls.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                and m.name.startswith("_") and m.name != "__init__"
            }
            for m in cls.body:
                if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) or m.name.startswith("_"):
                    continue
                _check_execute_body(root, py, m, attr_repos, attr_uows, helpers, collection_factories, f)


def _check_execute_body(root: Path, py: Path, fn: ast.FunctionDef | ast.AsyncFunctionDef,
                        attr_repos: set[str], attr_uows: set[str],
                        helpers: "dict[str, ast.FunctionDef | ast.AsyncFunctionDef]",
                        collection_factories: "dict[str, set[str]]",
                        f: Findings) -> None:
    repo_names = _repo_param_names(fn)
    uow_names = _uow_param_names(fn)
    has_uow = bool(uow_names or attr_uows)

    def _is_repo_recv(node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in repo_names
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
            return node.attr in attr_repos
        return False

    def _is_factory_call(value: "ast.AST | None") -> bool:
        if not isinstance(value, ast.Call) or not isinstance(value.func, (ast.Name, ast.Attribute)):
            return False
        fn_node = value.func
        return (not _is_repo_recv(fn_node.value if isinstance(fn_node, ast.Attribute) else fn_node)
                and _attr_root(fn_node) not in repo_names)

    method_called: set[str] = set()      # 루트 메서드 호출을 받은 이름
    factory_born: set[str] = set()       # 도메인 팩토리/생성자 호출로 태어난 이름
    attr_assigned: set[str] = set()      # obj.field = x 직접 대입을 받은 이름
    writes: list[tuple[str, ast.Call]] = []

    for node in ast.walk(fn):
        target = value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        if isinstance(target, ast.Name) and _is_factory_call(value):
            factory_born.add(target.id)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                    attr_assigned.add(t.value.id)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            recv, meth = node.func.value, node.func.attr
            if _is_repo_recv(recv):
                if meth.split("_", 1)[0] in ("save", "remove"):
                    arg = node.args[0] if node.args else None
                    writes.append((arg.id if isinstance(arg, ast.Name) else "", node))
            elif isinstance(recv, ast.Name):
                method_called.add(recv.id)

    # 반복 변수 — «x = <원소식>» 과 같은 판정을 원소식에 적용해 물려준다(F4-20 · R8-D2).
    # 이름 단위 판정이고 fail-closed 다.
    #   컬렉션 이름: 모든 결속이 단순 대입(`x = v`·`x: T = v`)이고 값이 원소 팩토리일 때만(값이
    #     가리키는 이름도 같은 조건 — 최소 고정점이라 대입 순서에 기대지 않는다) 원소 출처를 싣는다.
    #     가변 컬렉션이면 반복 원천·(반복 원천·단순 대입 우변의) 복사 래퍼 인자·순수 읽기 자리
    #     (아래 목록) 밖에서 읽히지 않아야 한다 — 별칭·호출 인자·메서드 수신(extend 등)·첨자 대입처럼
    #     밖으로 새면 그 객체가 무엇을 담게 될지 모른다. 불변 컬렉션은 면제한다.
    #   반복 변수: 이 함수 안의 결속 가운데 단순 대입·단일 이름 반복 target 밖의 것(이 함수의
    #     파라미터·`:=`·`+=`·언패킹·with/except as·`match` 캡처·함수 안 import·def)이 하나라도
    #     있으면 물려받지 않는다(중첩 def·lambda 파라미터는 보지 않는다).
    wrappers = ("tuple", "list", "frozenset", "set")

    def _unwrapped(expr: ast.AST) -> ast.AST:
        while (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in wrappers
               and len(expr.args) == 1 and not expr.keywords):
            expr = expr.args[0]
        return expr

    params = {a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs}
    params |= {a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None}
    simple: "dict[str, list[ast.AST]]" = {}   # 단순 대입 이름 → 대입 값들
    simple_ids: set[int] = set()             # 단순 대입·맨 선언(`x: T`) target 노드
    loop_ids: set[int] = set()               # 단일 이름 반복 target 노드
    source_ids: set[int] = set()             # 반복 원천·복사 래퍼 인자·순수 읽기 자리의 이름 노드
    nested_returns = {id(r) for d in ast.walk(fn)
                      if d is not fn and isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))
                      for r in ast.walk(d) if isinstance(r, ast.Return)}
    for node in ast.walk(fn):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            if isinstance(node.target, ast.Name):
                loop_ids.add(id(node.target))
            src = _unwrapped(node.iter)
            if isinstance(src, ast.Name):
                source_ids.add(id(src))
        # 원소를 들이지 못하는 순수 읽기 자리 — `len(x)`·`bool(x)`·`isinstance(x, …)` 인자 · 비교
        # 피연산자(`==`·`!=`·`in`·`not in`·`is`·`is not`) · `x.sort(..)`·`x.reverse()`(순서만 바꾼다) ·
        # `if x`/`while x`/`assert x`/`… if x else …`·`not x` · 이 함수 자신의 `return x`(복사 포함 —
        # 함수를 떠난다. 중첩 def 의 return 은 그 def 를 부른 쪽으로 새므로 넣지 않는다).
        reads: "list[ast.AST]" = []
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            if node.func.id in ("len", "bool") and len(node.args) == 1:
                reads = [node.args[0]]
            elif node.func.id == "isinstance" and len(node.args) == 2:
                reads = [node.args[0]]
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("sort", "reverse"):
            reads = [node.func.value]
        elif isinstance(node, ast.Compare) and all(isinstance(op, PURE_COMPARE_OPS) for op in node.ops):
            reads = [node.left, *node.comparators]
        elif isinstance(node, (ast.If, ast.While, ast.IfExp, ast.Assert)):
            reads = [node.test]
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            reads = [node.operand]
        elif isinstance(node, ast.Return) and node.value is not None and id(node) not in nested_returns:
            reads = [_unwrapped(node.value)]
        source_ids |= {id(r) for r in reads if isinstance(r, ast.Name)}
        target = value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        if isinstance(target, ast.Name):
            simple_ids.add(id(target))
            if value is not None:
                simple.setdefault(target.id, []).append(value)
                src = _unwrapped(value)
                if src is not value and isinstance(src, ast.Name):   # 복사만 — 별칭(`x = y`)은 샌다
                    source_ids.add(id(src))
    bound_other: set[str] = set(params)      # 단순 대입·단일 이름 반복 target 밖의 결속
    loop_bound: set[str] = set()
    escaped: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store) and id(node) not in simple_ids:
                (loop_bound if id(node) in loop_ids else bound_other).add(node.id)
            elif isinstance(node.ctx, ast.Load) and node.id in simple and id(node) not in source_ids:
                escaped.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            bound_other |= {a.asname or a.name.split(".")[0] for a in node.names}
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound_other |= set(node.names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound_other.add(node.name)
        elif isinstance(node, MATCH_CAPTURES) and node.name:
            bound_other.add(node.name)
        elif MATCH_MAPPING is not None and isinstance(node, MATCH_MAPPING) and node.rest:
            bound_other.add(node.rest)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in ("locals", "vars") and not node.args):
            escaped |= set(simple)                # 이름 공간을 통째로 내준다 — 전 컬렉션 이름이 샌다
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not fn:
            bound_other.add(node.name)
    local_names = bound_other | loop_bound | set(simple)   # 이 함수에서 묶인 이름(클래스 가림 판정)

    def _immutable(value: ast.AST) -> bool:
        """내용이 태어날 때 고정되는 값 — `tuple(..)`·`frozenset(..)`(가려지지 않은 내장)·제너레이터 식."""
        return isinstance(value, ast.GeneratorExp) or (
            isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
            and value.func.id in ("tuple", "frozenset") and value.func.id not in local_names)

    # 불변 컬렉션은 별칭·인자 전달·메서드 수신으로 내용이 바뀌지 않는다(재결속은 결속 판정이 막는다).
    escaped = {n for n in escaped if not all(_immutable(v) for v in simple[n])}
    element_other = bound_other | loop_bound | escaped
    scalar_other = bound_other | {n for n, vs in simple.items() if not all(_is_factory_call(v) for v in vs)}
    element_factory: set[str] = set()        # 원소 출처를 싣는 컬렉션 이름(아래 고정점)
    loop_factory: set[str] = set()
    loop_other: set[str] = set()

    def _elements_factory_born(it: ast.AST) -> bool:
        if isinstance(it, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return _is_factory_call(it.elt)
        if (isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id in wrappers
                and len(it.args) == 1 and not it.keywords):
            return _elements_factory_born(it.args[0])
        # 인자 없는 도메인 컬렉션 팩토리 `C.m()` — 입력이 없는 도메인 호출은 조회된 애그리거트를
        # 손에 쥘 길이 없다(#8·#1). 인자가 있으면 받은 인스턴스를 돌려줄 수 있어 전파하지 않고,
        # C 가 이 함수에서 다시 묶였으면 도메인 클래스라고 보증할 수 없어 전파하지 않는다(R8-D2).
        if (isinstance(it, ast.Call) and not it.args and not it.keywords
                and isinstance(it.func, ast.Attribute) and isinstance(it.func.value, ast.Name)
                and it.func.value.id not in local_names
                and it.func.attr in collection_factories.get(it.func.value.id, ())):
            return True
        return isinstance(it, ast.Name) and it.id in element_factory

    grew = True
    while grew:
        grew = False
        for name, values in simple.items():
            if (name not in element_factory and name not in element_other
                    and all(_elements_factory_born(v) for v in values)):
                element_factory.add(name)
                grew = True
    for node in ast.walk(fn):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)) and isinstance(node.target, ast.Name):
            (loop_factory if _elements_factory_born(node.iter) else loop_other).add(node.target.id)
    factory_born |= loop_factory - loop_other - scalar_other

    # #197 — UoW 를 받았는데 도달 범위 어디에도 쓰기 API 가 없다(측정 정밀화 2026-08-25).
    # «with uow» 진입 자체는 인정하지 않는다 — 읽기 전용+UoW 는 성문 문면 그대로 위반이다.
    if has_uow and not _uow_write_reach(fn, helpers, attr_uows, attr_repos):
        f.add("#197", _rel(root, py, fn.lineno),
              f"`{fn.name}` 이 UnitOfWork 를 받는데 도달 범위에 save/remove/after_commit 이 없다"
              "(with 진입만으로는 쓰기가 아니다) — 읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다")

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
