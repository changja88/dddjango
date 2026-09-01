#!/usr/bin/env python3
"""dddjango 타입 전면 검사기 — «첫 대입에 타입» 규율의 결정적 백스톱.

트리 개정 명세의 타입 규칙 4개를 강제한다.

  #493 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가
       없다(T49/D58 — 옛 판의 «지역 변수는 권장» 선과 «시그니처는 mypy 몫»
       (`FunctionDef`→continue 결함)를 사용자 결정으로 뒤집었다). 빠지는 것은
       **문법이 없는 여덟 자리뿐**: `for x in xs:` · `with … as f:` · `except … as e:` ·
       `a, b = pair` · `a = b = 0` · `x += 1` · walrus · 컴프리헨션. 그리고
       **재대입**(첫 바인딩이 아니다)과 **선언적 클래스 본문**(ORM 모델 필드·
       ninja Schema 필드·enum 멤버 — 그 안의 «메서드»는 면제가 아니다)은 면제다.
  #358 Thin Read 구현(`adapter/**/domain_bypass_query/`)이 바깥으로 내보내는 것은
       «이름 붙인 정적 타입»뿐 — 반환 애너테이션에 `QuerySet`·`<Name>Model` 금지.
  #456 모양이 틀린 요청은 계약 위반이라 `contract/exception/` 이 아니라 테스트·타입
       체커가 받는다 — 판정은 raise «지점»(판정 ⑩): contract/ 안 raise·미raise 는 위반,
       창구 서비스 outcome 매핑만 raise 하는 semantic published error 는 인정.
  #69  (ast+ · ⓓ 후보) 개발자 실수를 막는 검사는 런타임이 아니라 테스트·타입 체커의
       몫 — 프로덕션 `assert` · isinstance 가드 뒤 TypeError/ValueError raise 를
       후보로만 출력한다(exit 불산입 · 마무리는 discipline-reviewer).

문법 외 면제(도구·프로토콜 소유 — 사람이 짓는 자리가 아니다):
  - `migrations/`(#593 이 모양을 소유) · `manage.py`/`wsgi.py`/`asgi.py`(생성 골격).
  - 던더(`__all__` 등)·`urlpatterns` — 인터프리터/Django 가 이름과 형을 소유한다.
  - `test/` 의 unit/integration/e2e(«테스트 — 안이 자유» #384)와 `test_*.py`·
    `conftest.py`. 재료 칸(`factories/`·`fake/`)은 규칙이 그대로 산다.

가드 계약 (명세 조각 ⓐ): 대상 0건 가드(#74) · git 유무와 무관하게 전 파일
검사(fail-closed — 기존 코드도 면제가 아니라 빚이다).

사용법: check-public-surface-annotation.py [TARGET_DIR]   (기본: 현재 디렉터리)
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
SCAFFOLD_FILES = {"manage.py", "wsgi.py", "asgi.py"}
TEST_DIR_NAMES = {"test", "tests"}
TEST_FREE_DIRS = {"unit", "integration", "e2e"}
MATERIAL_DIRS = {"factories", "fake"}

DRIVEN_DIRS = {"driven_layer"}
OHS_DIRS = {"open_host_service"}

# 선언적 프레임워크 클래스 — 본문 «필드 대입»이 관용이라 대입만 면제(메서드는 검사).
DECLARATIVE_BASE_NAMES = {
    "Model", "Enum", "IntEnum", "StrEnum", "Flag", "IntFlag",
    "Choices", "TextChoices", "IntegerChoices",
    "Form", "ModelForm", "Serializer", "ModelSerializer",
    "HyperlinkedModelSerializer", "Schema", "BaseModel",
    "TypedDict", "NamedTuple",
    "AppConfig", "ModelAdmin", "TabularInline", "StackedInline", "AdminSite",
    "Factory", "DjangoModelFactory",
    "AbstractBaseUser", "AbstractUser", "PermissionsMixin",
}
DECLARATIVE_CLASS_NAMES = {"Meta", "Config"}
DECLARATIVE_DECORATORS = {"dataclass", "define", "frozen", "attrs"}
PROTOCOL_NAMES = {"urlpatterns"}

VALIDATION_TOKENS = ("invalid", "validation", "malformed", "badrequest", "unprocessable")
GUARD_EXC = {"TypeError", "ValueError"}


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _adopted(target: Path) -> bool:
    for c in target.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        for bc in sorted(c.iterdir()):
            if bc.is_dir() and not bc.name.startswith(".") and _has_adoption_signal(bc):
                return True
    return False


def _is_target_file(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS or "migrations" in parts:
        return False
    if path.name in SCAFFOLD_FILES:
        return False
    if path.name.startswith("test_") or path.name == "conftest.py":
        return False
    if parts & TEST_DIR_NAMES:
        # «테스트=자유 · 재료=규칙»(#384) — factories/·fake/ 만 검사한다.
        if not (parts & MATERIAL_DIRS):
            return False
        if parts & TEST_FREE_DIRS:
            return False
    return True


def _name_of(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _is_declarative_class(cls: ast.ClassDef) -> bool:
    if cls.name in DECLARATIVE_CLASS_NAMES:
        return True
    if {_name_of(b) for b in cls.bases} & DECLARATIVE_BASE_NAMES:
        return True
    deco = set()
    for d in cls.decorator_list:
        deco.add(_name_of(d.func) if isinstance(d, ast.Call) else _name_of(d))
    return bool(deco & DECLARATIVE_DECORATORS)


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


# ── #493 — 시그니처 · 지역 변수 · 속성 · 모듈/클래스 변수 ────────────────────

def _check_signature(fn: ast.FunctionDef | ast.AsyncFunctionDef, in_class: bool, rel: Path, out: Findings) -> None:
    args = fn.args
    positional = list(args.posonlyargs) + list(args.args)
    for i, a in enumerate(positional):
        if in_class and i == 0 and a.arg in ("self", "cls"):
            continue  # 관례 수신자 — 애너테이션 문법 관례가 없다
        if a.annotation is None:
            out.add("#493", f"{rel}:{fn.lineno}", f"`{fn.name}()` 매개변수 `{a.arg}` 에 타입이 없다")
    for a in args.kwonlyargs:
        if a.annotation is None:
            out.add("#493", f"{rel}:{fn.lineno}", f"`{fn.name}()` 매개변수 `{a.arg}` 에 타입이 없다")
    for a in (args.vararg, args.kwarg):
        if a is not None and a.annotation is None:
            out.add("#493", f"{rel}:{fn.lineno}", f"`{fn.name}()` 매개변수 `*{a.arg}` 에 타입이 없다")
    if fn.returns is None:
        out.add("#493", f"{rel}:{fn.lineno}", f"`{fn.name}()` 반환 타입이 없다")


def _record_syntax_bindings(node: ast.AST, bound: set[str]) -> None:
    """문법이 없는 자리(for/with/except/언패킹/다중/증강/walrus/컴프리헨션)의 바인딩을 기록만 한다."""
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            bound.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                bound.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            bound.update(n.names)


def _scan_stmts(
    stmts: list[ast.stmt], scope: str, bound: set[str], rel: Path,
    out: Findings, declarative: bool,
) -> None:
    """한 스코프의 문장열을 소스 순서로 걸으며 «첫 단순대입»의 타입 누락을 모은다.

    scope ∈ {module, class, function}. 제어 블록(if/try/for/while/with) 안은 같은
    스코프라 본문을 이어 걷는다(첫 바인딩 판정은 소스 순서)."""
    for stmt in stmts:
        if isinstance(stmt, ast.ClassDef):
            bound.add(stmt.name)
            _scan_class(stmt, rel, out)
            continue
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(stmt.name)
            _check_signature(stmt, scope == "class", rel, out)
            fn_bound: set[str] = {a.arg for a in (
                list(stmt.args.posonlyargs) + list(stmt.args.args) + list(stmt.args.kwonlyargs)
            )}
            for va in (stmt.args.vararg, stmt.args.kwarg):
                if va is not None:
                    fn_bound.add(va.arg)
            _scan_stmts(stmt.body, "function", fn_bound, rel, out, False)
            continue
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                bound.add(stmt.target.id)
            continue
        if isinstance(stmt, ast.Assign):
            if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                name = stmt.targets[0].id
                first = name not in bound
                bound.add(name)
                if first and not declarative and not _is_dunder(name) and name not in PROTOCOL_NAMES:
                    where = {"module": "모듈 변수", "class": "클래스 변수", "function": "지역 변수"}[scope]
                    out.add("#493", f"{rel}:{stmt.lineno}", f"{where} `{name}` 의 첫 대입에 타입이 없다 — `name: T = …`")
            else:
                _record_syntax_bindings(stmt, bound)  # 언패킹·다중·비-Name 타깃(문법 면제)
            continue
        if isinstance(stmt, (ast.If, ast.While)):
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative)
            continue
        if isinstance(stmt, (ast.For, ast.AsyncFor)):
            _record_syntax_bindings(stmt.target, bound)
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative)
            continue
        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            for item in stmt.items:
                if item.optional_vars is not None:
                    _record_syntax_bindings(item.optional_vars, bound)
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative)
            continue
        if isinstance(stmt, ast.Try):
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative)
            for h in stmt.handlers:
                if h.name:
                    bound.add(h.name)
                _scan_stmts(h.body, scope, bound, rel, out, declarative)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative)
            _scan_stmts(stmt.finalbody, scope, bound, rel, out, declarative)
            continue
        _record_syntax_bindings(stmt, bound)  # AugAssign·Import·Expr(walrus 포함) — 기록만


def _scan_class(cls: ast.ClassDef, rel: Path, out: Findings) -> None:
    declarative = _is_declarative_class(cls)
    bound: set[str] = set()
    _scan_stmts(cls.body, "class", bound, rel, out, declarative)
    if declarative:
        return  # 선언적 본문 — 속성 규칙도 프레임워크 관용에 맡긴다
    # 속성(#493) — self.x 의 첫 대입: 클래스 본문 `x: T` 나 `self.x: T = …` 가 어디에도 없으면 위반.
    annotated: set[str] = {
        s.target.id for s in cls.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)
    }
    assigned: dict[str, int] = {}
    for node in ast.walk(cls):
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Attribute):
            target = node.target
            is_ann = True
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
            target = node.targets[0]
            is_ann = False
        else:
            continue
        if not (isinstance(target.value, ast.Name) and target.value.id == "self"):
            continue
        if is_ann:
            annotated.add(target.attr)
        else:
            assigned.setdefault(target.attr, node.lineno)
    for attr, lineno in sorted(assigned.items(), key=lambda kv: kv[1]):
        if attr not in annotated and not _is_dunder(attr):
            out.add("#493", f"{rel}:{lineno}", f"속성 `self.{attr}` 의 첫 대입에 타입이 없다 — `self.{attr}: T = …` 또는 클래스 본문 `{attr}: T`")


# ── #358 · #456 · #69 ───────────────────────────────────────────────────────

def _annotation_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for n in ast.walk(node):
        nm = _name_of(n)
        if nm:
            out.add(nm)
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            try:  # 문자열 애너테이션(`-> "QuerySet[OrderModel]"`)도 같은 판으로
                out |= _annotation_names(ast.parse(n.value, mode="eval").body)
            except SyntaxError:
                pass
    return out


def _check_thin_read(mod: ast.Module, rel: Path, out: Findings) -> None:
    """#358 — Thin Read 구현의 반환 애너테이션에 QuerySet·<Name>Model 금지."""
    for fn in (n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
        if fn.returns is None:
            continue  # 부재는 #493 이 잡는다 — 중복 진단 금지
        names = _annotation_names(fn.returns)
        bad = {n for n in names if n == "QuerySet" or (n.endswith("Model") and n != "BaseModel")}
        if bad:
            out.add("#358", f"{rel}:{fn.lineno}", f"`{fn.name}()` 반환 타입에 `{', '.join(sorted(bad))}` — Thin Read 는 이름 붙인 정적 타입만 내보낸다(ORM 로우·QuerySet 금지)")


def _raise_sites(service_dir: Path, name: str) -> "tuple[int, int]":
    """창구 폴더 안 `raise <name>(...)` 지점 전수 — (contract쪽 수, 서비스쪽 수).

    자리 기반 판별(판정 ⑩): raise 파일이 `contract/` 서브트리 안이면 contract쪽,
    그 밖(창구 서비스 파일 등)이면 서비스쪽이다. 이름 매칭은 단순명(Name·Attribute 끝)이다.
    """
    contract_n = service_n = 0
    for py in sorted(service_dir.rglob("*.py")):
        try:
            mod = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        hits = 0
        for node in ast.walk(mod):
            if isinstance(node, ast.Raise) and node.exc is not None:
                target = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
                ident = target.id if isinstance(target, ast.Name) else (
                    target.attr if isinstance(target, ast.Attribute) else None)
                if ident == name:
                    hits += 1
        if not hits:
            continue
        if "contract" in py.relative_to(service_dir).parts:
            contract_n += hits
        else:
            service_n += hits
    return contract_n, service_n


def _check_contract_exceptions(f_abs: Path, mod: ast.Module, rel: Path, out: Findings) -> None:
    """#456 — OHS contract/exception/ 의 «요청 검증 계열 이름» 예외는 raise 지점으로 판정한다
    (판정 ⑩ 2026-08-25 — 이름 토큰 단독 판정 폐기): contract/ 안(팩토리·__post_init__)에서
    raise 되면 형식 검증 — 같은 저장소 typed dataclass 호출에서 도달 불가한 방어이자 거짓
    대외 계약(위반). 창구 서비스 쪽(outcome 매핑)에서만 raise 되면 semantic 실패 — 정당한
    published error(인정). 어디서도 raise 안 되거나(죽은 대외 계약) 양쪽 다면 위반 유지."""
    parts = f_abs.parts
    ohs_idx = [i for i, seg in enumerate(parts) if seg in OHS_DIRS]
    service_dir = Path(*parts[: ohs_idx[-1] + 2]) if ohs_idx else f_abs.parent
    for cls in (n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)):
        low = cls.name.lower()
        if not any(tok in low for tok in VALIDATION_TOKENS):
            continue
        contract_n, service_n = _raise_sites(service_dir, cls.name)
        if service_n and not contract_n:
            continue  # semantic published error — 창구 outcome 매핑만 raise 한다
        where = ("contract 안에서 raise 된다" if contract_n and not service_n
                 else "contract·서비스 양쪽에서 raise 된다" if contract_n
                 else "어디서도 raise 되지 않는다(죽은 대외 계약)")
        out.add("#456", rel, f"`{cls.name}` — 모양이 틀린 요청은 계약 위반이라 테스트·타입 체커가 "
                             f"받는다(`contract/exception/` 의 자리가 아니다 — {where})")


def _collect_runtime_guards(mod: ast.Module, rel: Path, cands: Candidates) -> None:
    """#69 (ⓓ 후보) — 프로덕션 assert · isinstance 가드 뒤 TypeError/ValueError."""
    for node in ast.walk(mod):
        if isinstance(node, ast.Assert):
            cands.add("#69", f"{rel}:{node.lineno}", f"프로덕션 `assert`", "이 검사는 런타임이 아니라 테스트·타입 체커의 몫인가?")
        elif isinstance(node, ast.If):
            has_isinstance = any(
                isinstance(c, ast.Call) and _name_of(c.func) == "isinstance" for c in ast.walk(node.test)
            )
            if not has_isinstance:
                continue
            for sub in node.body:
                for r in ast.walk(sub):
                    if isinstance(r, ast.Raise) and r.exc is not None:
                        exc_name = _name_of(r.exc.func) if isinstance(r.exc, ast.Call) else _name_of(r.exc)
                        if exc_name in GUARD_EXC:
                            cands.add("#69", f"{rel}:{node.lineno}", f"isinstance 가드 뒤 `raise {exc_name}`", "이 검사는 런타임이 아니라 테스트·타입 체커의 몫인가?")
                            break


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    # 숨김 디렉터리(도구·하네스 영역 — `.codex/` 등)는 공개 표면이 아니다(2026-08-14 F-C ·
    # 라운드 3 실측: 클린룸 가드 훅 파일이 #493 귀속으로 오탐). 상대 경로 성분만 본다.
    files = [
        p for p in sorted(target.rglob("*.py"))
        if _is_target_file(p) and not any(seg.startswith(".") for seg in p.relative_to(target).parts[:-1])
    ]

    # 대상 0건 가드(#74) — 채택 신호는 있는데 파일이 0건이면 경로 계약이 어긋난 것.
    if not files:
        if _adopted(target):
            guard = zero_target_guard(
                "blocker: 채택 신호는 있는데 검사 대상 파일이 0건이다 — 조용한 무동작을 금지한다(#74)"
            )
            emit_all(guard, printer=print, indent="")
            return 2
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    findings = Findings(defer=True)
    candidates = Candidates(defer=True)
    for f in files:
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = f.relative_to(target)
        parts = set(rel.parts)
        _scan_stmts(mod.body, "module", set(), rel, findings, False)
        if (parts & DRIVEN_DIRS) and "domain_bypass_query" in parts:
            _check_thin_read(mod, rel, findings)
        if (parts & OHS_DIRS) and "contract" in parts and "exception" in parts:
            _check_contract_exceptions(f, mod, rel, findings)
        _collect_runtime_guards(mod, rel, candidates)

    if findings:
        print(f"blocker {len(findings)}건 — 타입 전면 규율 위반 (#493 «첫 대입에 타입» 외)")
        emit_all(findings, printer=print, indent="  ")
    if candidates:
        print(f"ⓓ 후보 {len(candidates)}건 — 기계가 후보를 좁혔다 · 마무리 물음은 discipline-reviewer 몫(exit 불산입)")
        emit_all(candidates, printer=print, indent="  ")
    if findings:
        return 2
    print(f"clean — 파일 {len(files)}개 타입 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
