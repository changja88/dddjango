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
  #645 명시 `Any` 금지 — 시그니처(인자·`*args/**kwargs`·반환)의 bare `Any`(`Optional[Any]`·
       `Any | None`·`Any` 가 섞인 합집합·`Annotated[Any, …]`·문자열·별칭·`typing.Any`·미해소 `Any`
       이름(fail-closed) 포함)는 위반 · 시그니처 안 nested(`dict[str, Any]`)와 변수·속성·클래스
       필드의 `Any` 는 ⓓ 후보(exit 불산입) — 단 `dict`/`Mapping`/`MutableMapping` 값 자리의 `Any` 는
       #647 이 소유한다(그 애너테이션의 nested ⓓ 는 생략 · bare 는 유지). #493(주석 «존재»)과 독립.
       검출 한계: `TypeAlias` 재별칭·`cast(Any, …)`·함수 본문/`with`/클래스 본문 안 import 는 표면 밖.
  #646 django-stubs 제네릭 Django 기저(타입 매개변수에 기본값이 없는 것 — django-stubs 6.1.0 `.pyi` 전수:
       admin 5 `BaseModelAdmin`·`ModelAdmin`·`InlineModelAdmin`·`StackedInline`·`TabularInline` · forms 9
       `BaseModelForm`·`ModelForm`·`BaseModelFormSet`·`BaseInlineFormSet`·`ModelChoiceField`·
       `ModelMultipleChoiceField`·`ModelChoiceIterator`·`ModelFormOptions`·`BaseFormSet` · CBV 32(detail·list·
       edit·dates 의 `_M`/`_FormT`/`_ModelFormT` 제네릭) — `View`·`TemplateView`·`RedirectView`·
       `*TemplateResponseMixin`·`ProcessFormView` 는 기본값/비제네릭이라 제외 · 스텁 상향 시 재열거)는
       런타임이 subscript 를 못 하므로 모델 타입 인자를 **`if TYPE_CHECKING:` 별칭**(또는 분기 안 중간
       ClassDef)으로 적는다. 위반: ⓐ 맨몸 상속(직접·모듈 수준 맨몸 별칭 경유) ⓑ 클래스 헤더 범위
       (`class` 줄~괄호 깊이 0 의 첫 `:` 줄 · 데코레이터 제외)나 기저 집합 클래스 본문 직계 대입 줄의
       `# type: ignore[type-arg]`(은폐) — ⓐ+ⓑ 동시는 클래스당 1건(ⓑ 문면). ⓓ 후보: 헤더의 code 없는
       `# type: ignore` · `TYPE_CHECKING` 밖 subscript(별칭·헤더 직접 — 런타임 `TypeError` 후보 · 프로젝트가
       `django_stubs_ext.monkeypatch()` 를 채택했으면 정당). 검출 한계: 별칭 추적은 같은 모듈 안(if/try
       하위 포함 · 뒤 정의 우선)만 — 타 모듈 import 별칭의 맨몸 여부는 mypy 몫(ⓑ 헤더 판정은 기저
       해소와 독립이라 그 경우도 ignore 는 잡는다).
  #647 딕셔너리-레코드 — `dict`/`Dict`/`Mapping`/`MutableMapping` 의 값 자리(마지막 슬라이스 원소 · 문자열
       주석 재파싱 · `Literal[…]` 안 제외 · 값이 union/기타면 무발화 — #645 nested 몫). 자리×값 매트릭스:
         sig-param·sig-star·variable(AnnAssign)  : `Any` 차단(top·nested) · `object` ⓓ 후보(top·nested)
         sig-return·class-attr(ClassDef 직계)    : `Any` 차단 · `object` 차단
       면제(`object` 만): 반환 루트 `TypeIs`/`TypeGuard[...]` · 스텁이 강제하는 오버라이드
       `clean()`×{Form, BaseForm, ModelForm, BaseModelForm} · `deconstruct()`×{Field, *Field}(기저 해소는
       #646 과 같은 별칭 기계). 별도 ⓓ: 반환 주석의 자리표시 `object`(루트 · union 구성원 ·
       tuple/list/Sequence/Iterable/Iterator/set/frozenset/Collection 원소 — 같은 노드에 차단이 있으면 차단만).
  #650 (ast+ · ⓓ 전용) `json.load(s)` 결과의 무검증 흐름 — 결과가 놓이는 자리의 «선언 값 타입»이 `object`
       가 아닌 곳(AnnAssign 주석 루트 · Return 의 반환 주석 루트 · 리터럴 컨테이너 요소(그 리터럴이
       AnnAssign/Return 값이면 원소 슬롯 · 호출 인자면 비후보) · 컴프리헨션 요소 · 직접 첨자/속성 접근)로
       흐르면 후보 · union 은 전 구성원이 `object` 슬롯일 때만 비후보 · `x: object = …` 와 파서 직접
       인자·무주석 Assign(#493 몫)은 후보 아님. 좌표 = AnnAssign/Return 문장 줄 · 그 밖 호출 줄.
  #646·#647·#650 은 상대 경로 성분에 `application`/`framework` 가 있는 파일만 본다(어느 깊이든 — `src/application/**`
       도 채택 신호와 같은 판 · kkebi `web/`·`scripts/` 등 자매 플러그인·운영 스크립트 영역 제외 — 기존 5규칙의 대상은 무변).

문법 외 면제(도구·프로토콜 소유 — 사람이 짓는 자리가 아니다):
  - `migrations/`(#593 이 모양을 소유) · `manage.py`/`wsgi.py`/`asgi.py`(생성 골격).
  - 던더(`__all__` 등)·`urlpatterns` — 인터프리터/Django 가 이름과 형을 소유한다.
  - `test/` 의 unit/integration/e2e(«테스트 — 안이 자유» #384)와 `test_*.py`·
    `conftest.py`. 재료 칸(`factories/`·`fake/`)은 규칙이 그대로 산다.

가드 계약 (명세 조각 ⓐ): 대상 0건 가드(#74) · git 유무와 무관하게 전 파일
검사(fail-closed — 기존 코드도 면제가 아니라 빚이다).

검출 한계 (선언적 클래스 판정 — 오탐·미탐 가능 형상 · 2026-09-03 alias 해소 이후):
  - base·데코레이터 이름은 **모듈 수준 import 바인딩**으로 원명을 푼다(`StrEnum as _StrEnum`
    → StrEnum · `dataclass as _dataclass` → dataclass). 같은 이름을 뒤에서 모듈 수준으로
    재정의하면 그림자(바인딩 pop). 함수·클래스 본문 안 import 와 if/try 밖의 모듈 블록
    (`with`·`match` 등) 안 import 는 보지 않는다 — 그 형상은 별칭이면 원본과 같이 red 다.
  - `Attribute` base(`enum.StrEnum`·`models.Model`)는 attr 만 본다 — receiver 무검사.
  - 로컬 중간 base(`class _Base(StrEnum)` → `class X(_Base)`)의 전이 면제는 없다.
  - 원명 기준이라 동명 비선언 클래스의 별칭(`from x import Schema as _Schema`)은 면제되고,
    중간 base 를 선언적 이름으로 별칭한 정당 코드는 면제되지 않는다(양 저장소 실측 0).
  - 선언적 이름과 같은 이름의 **로컬** 클래스(`class StrEnum: …`)는 이름만으로 면제된다 —
    alias 해소 이전부터의 사각(그대로 둔다 · 전이 면제와 같은 이유로 receiver·정의처를 닫지 않는다).

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

# #646 — django-stubs 6.1.0 에서 타입 매개변수에 `default=` 가 없는 제네릭 Django 기저(전수 · 스텁 상향 시 재열거).
STUB_GENERIC_ADMIN_FORM_NAMES = {
    "BaseModelAdmin", "ModelAdmin", "InlineModelAdmin", "StackedInline", "TabularInline",
    "BaseModelForm", "ModelForm", "BaseModelFormSet", "BaseInlineFormSet", "ModelChoiceField",
    "ModelMultipleChoiceField", "ModelChoiceIterator", "ModelFormOptions", "BaseFormSet",
}
STUB_GENERIC_CBV_NAMES = {
    "SingleObjectMixin", "BaseDetailView", "DetailView",
    "MultipleObjectMixin", "BaseListView", "ListView",
    "FormMixin", "ModelFormMixin", "BaseFormView", "FormView", "BaseCreateView", "CreateView",
    "BaseUpdateView", "UpdateView", "DeletionMixin", "BaseDeleteView", "DeleteView",
    "BaseDateListView", "BaseArchiveIndexView", "ArchiveIndexView", "BaseYearArchiveView", "YearArchiveView",
    "BaseMonthArchiveView", "MonthArchiveView", "BaseWeekArchiveView", "WeekArchiveView",
    "BaseDayArchiveView", "DayArchiveView", "BaseTodayArchiveView", "TodayArchiveView",
    "BaseDateDetailView", "DateDetailView",
}
STUB_GENERIC_MODULES = (
    "django.contrib.admin", "django.contrib.admin.options",
    "django.forms", "django.forms.models", "django.forms.formsets",
    "django.views.generic", "django.views.generic.detail", "django.views.generic.list",
    "django.views.generic.edit", "django.views.generic.dates",
)
RULE_ROOTS = {"application", "framework"}  # #646·#647·#650 루트 필터(신규 3규칙만 — 기존 규칙 무변)
TYPE_IGNORE_RE = re.compile(r"#\s*type:\s*ignore(?:\[([^\]]*)\])?")

# #647 — 값 자리 판정 재료.
RECORD_CONTAINERS = {"dict", "Dict", "Mapping", "MutableMapping"}
SEQUENCE_CONTAINERS = {"tuple", "Tuple", "list", "List", "Sequence", "Iterable", "Iterator", "set", "frozenset", "Set", "FrozenSet", "Collection"}
TYPE_GUARDS = {"TypeIs", "TypeGuard"}
FRAMEWORK_OVERRIDE_EXEMPT = {  # 스텁이 `dict[str, Any]` 반환을 강제하는 오버라이드 — `dict[str, object]` 만 면제
    "clean": {"Form", "BaseForm", "ModelForm", "BaseModelForm"},
    "deconstruct": {"Field"},  # 이름이 Field 이거나 *Field 로 끝나는 기저
}
JSON_LOAD_NAMES = {"load", "loads"}
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


def _module_bindings(mod: ast.Module) -> dict[str, str]:
    """모듈 수준 import 바인딩 — 로컬 이름 → 원명(check-error-centralization `_final_module_bindings` 판형).

    `from enum import StrEnum as _StrEnum` → {"_StrEnum": "StrEnum"} · `import enum as e` → {"e": "enum"}.
    if/try 하위 문은 걷고, 함수·클래스 본문 안 import 는 보지 않는다(base·데코레이터 표현에 못 쓰인다).
    같은 이름의 모듈 수준 ClassDef/FunctionDef/대입이 뒤에 오면 그림자 — 바인딩을 pop 한다(소스 순서)."""
    bindings: dict[str, str] = {}

    def walk(stmts: list[ast.stmt]) -> None:
        for st in stmts:
            if isinstance(st, ast.ImportFrom):
                for a in st.names:
                    bindings[a.asname or a.name] = a.name
            elif isinstance(st, ast.Import):
                for a in st.names:
                    top: str = a.name.split(".")[0]
                    bindings[a.asname or top] = a.name if a.asname else top
            elif isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                bindings.pop(st.name, None)
            elif isinstance(st, ast.Assign):
                for t in st.targets:
                    if isinstance(t, ast.Name):
                        bindings.pop(t.id, None)
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                bindings.pop(st.target.id, None)
            elif isinstance(st, ast.If):
                walk(st.body)
                walk(st.orelse)
            elif isinstance(st, ast.Try):
                walk(st.body)
                for h in st.handlers:
                    walk(h.body)
                walk(st.orelse)
                walk(st.finalbody)

    walk(mod.body)
    return bindings


def _resolved_name(node: ast.AST, bindings: dict[str, str]) -> str:
    """base·데코레이터 이름 — `Name` 은 모듈 import 바인딩으로 원명 해소(로컬 정의면 그대로) ·
    `Attribute` 는 attr(receiver 무검사 — 라이브러리 모듈 목록을 닫지 않는다)."""
    if isinstance(node, ast.Name):
        return bindings.get(node.id, node.id)
    return _name_of(node)


def _origin_bindings(mod: ast.Module) -> dict[str, str]:
    """모듈 수준 import 바인딩 — 로컬 이름 → dotted origin(출처 모듈 보존 · `_module_bindings` 와 같은 걷기).

    `from django.contrib import admin` → {"admin": "django.contrib.admin"} · `from x import C as D` → {"D": "x.C"} ·
    `import a.b as x` → {"x": "a.b"} · `import a` → {"a": "a"}. 뒤따르는 모듈 수준 재정의는 그림자(pop)."""
    origins: dict[str, str] = {}

    def walk(stmts: list[ast.stmt]) -> None:
        for st in stmts:
            if isinstance(st, ast.ImportFrom):
                for a in st.names:
                    origins[a.asname or a.name] = f"{st.module}.{a.name}" if st.module else a.name
            elif isinstance(st, ast.Import):
                for a in st.names:
                    origins[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
            elif isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                origins.pop(st.name, None)
            elif isinstance(st, ast.Assign):
                for tg in st.targets:
                    if isinstance(tg, ast.Name):
                        origins.pop(tg.id, None)
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                origins.pop(st.target.id, None)
            elif isinstance(st, ast.If):
                walk(st.body)
                walk(st.orelse)
            elif isinstance(st, ast.Try):
                walk(st.body)
                for h in st.handlers:
                    walk(h.body)
                walk(st.orelse)
                walk(st.finalbody)

    walk(mod.body)
    return origins


def _dotted(node: ast.AST, origins: dict[str, str]) -> str:
    """`admin.ModelAdmin` → `django.contrib.admin.ModelAdmin`(루트 Name 을 origin 으로 치환) · 미해소 이름은 그대로."""
    if isinstance(node, ast.Name):
        return origins.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value, origins)
        return f"{head}.{node.attr}" if head else node.attr
    return ""


def _is_type_checking(test: ast.AST) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")


def _alias_defs(mod: ast.Module) -> "dict[str, list[tuple[ast.AST, bool]]]":
    """모듈 수준 별칭 정의 — 이름 → [(값, TYPE_CHECKING 분기 안인가)] 소스 순서.

    값 = Assign/AnnAssign 의 Name/Attribute/Subscript · `TYPE_CHECKING` 분기 안 ClassDef 의 첫 기저 + 나머지
    Subscript 기저(mixin-first 형 `class _B(Mixin, admin.ModelAdmin[M])` — 첫 기저를 마지막에 두어 «뒤 정의 우선» 을 보존).
    if/try 하위를 걷고 함수·클래스 본문 안은 보지 않는다. 같은 이름이 import 바인딩과 별칭 양쪽에 있으면
    소스 순서상 뒤 정의가 이긴다(`_resolved_base` 가 `bindings` 를 먼저 본다)."""
    out: dict[str, list[tuple[ast.AST, bool]]] = {}

    def walk(stmts: list[ast.stmt], in_tc: bool) -> None:
        for st in stmts:
            if isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None \
                    and isinstance(st.value, (ast.Name, ast.Attribute, ast.Subscript)):
                for tg in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                    if isinstance(tg, ast.Name):
                        out.setdefault(tg.id, []).append((st.value, in_tc))
            elif isinstance(st, ast.ClassDef) and in_tc and st.bases:
                lst = out.setdefault(st.name, [])
                lst.extend((b, True) for b in st.bases[1:] if isinstance(b, ast.Subscript))  # mixin-first 중간 ClassDef
                lst.append((st.bases[0], True))
            elif isinstance(st, ast.If):
                walk(st.body, in_tc or _is_type_checking(st.test))
                walk(st.orelse, in_tc)
            elif isinstance(st, ast.Try):
                walk(st.body, in_tc)
                for h in st.handlers:
                    walk(h.body, in_tc)
                walk(st.orelse, in_tc)
                walk(st.finalbody, in_tc)

    walk(mod.body, False)
    return out


def _resolved_bases(node: ast.AST, bindings: dict[str, str],
                    aliases: "dict[str, list[tuple[ast.AST, bool]]] | None", depth: int = 0) -> set[str]:
    """기저 원명 집합 — 별칭 정의가 여럿(TYPE_CHECKING 분기 · mixin-first 중간 ClassDef)이면 전부 따라간다(depth≤4)."""
    if isinstance(node, ast.Subscript):
        return _resolved_bases(node.value, bindings, aliases, depth)
    if isinstance(node, ast.Name) and aliases and node.id not in bindings and node.id in aliases and depth < 4:
        out: set[str] = set()
        for value, _tc in aliases[node.id]:
            out |= _resolved_bases(value, bindings, aliases, depth + 1)
        return out
    return {_resolved_name(node, bindings)}


def _is_declarative_class(cls: ast.ClassDef, bindings: dict[str, str],
                          aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> bool:
    if cls.name in DECLARATIVE_CLASS_NAMES:
        return True
    if set().union(*(_resolved_bases(b, bindings, aliases) for b in cls.bases)) & DECLARATIVE_BASE_NAMES:
        return True
    deco = set()
    for d in cls.decorator_list:
        deco.add(_resolved_name(d.func if isinstance(d, ast.Call) else d, bindings))
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
    out: Findings, declarative: bool, bindings: dict[str, str],
    aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None,
) -> None:
    """한 스코프의 문장열을 소스 순서로 걸으며 «첫 단순대입»의 타입 누락을 모은다.

    scope ∈ {module, class, function}. 제어 블록(if/try/for/while/with) 안은 같은
    스코프라 본문을 이어 걷는다(첫 바인딩 판정은 소스 순서)."""
    for stmt in stmts:
        if isinstance(stmt, ast.ClassDef):
            bound.add(stmt.name)
            _scan_class(stmt, rel, out, bindings, aliases)
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
            _scan_stmts(stmt.body, "function", fn_bound, rel, out, False, bindings, aliases)
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
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative, bindings, aliases)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative, bindings, aliases)
            continue
        if isinstance(stmt, (ast.For, ast.AsyncFor)):
            _record_syntax_bindings(stmt.target, bound)
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative, bindings, aliases)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative, bindings, aliases)
            continue
        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            for item in stmt.items:
                if item.optional_vars is not None:
                    _record_syntax_bindings(item.optional_vars, bound)
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative, bindings, aliases)
            continue
        if isinstance(stmt, ast.Try):
            _scan_stmts(stmt.body, scope, bound, rel, out, declarative, bindings, aliases)
            for h in stmt.handlers:
                if h.name:
                    bound.add(h.name)
                _scan_stmts(h.body, scope, bound, rel, out, declarative, bindings, aliases)
            _scan_stmts(stmt.orelse, scope, bound, rel, out, declarative, bindings, aliases)
            _scan_stmts(stmt.finalbody, scope, bound, rel, out, declarative, bindings, aliases)
            continue
        _record_syntax_bindings(stmt, bound)  # AugAssign·Import·Expr(walrus 포함) — 기록만


def _scan_class(cls: ast.ClassDef, rel: Path, out: Findings, bindings: dict[str, str],
                aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
    declarative = _is_declarative_class(cls, bindings, aliases)
    bound: set[str] = set()
    _scan_stmts(cls.body, "class", bound, rel, out, declarative, bindings, aliases)
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


# ── #645 — 명시 `Any`(시그니처 bare = 위반 · 그 밖 = ⓓ 후보) ─────────────────
ANY_MODULES = {"typing", "typing_extensions"}
ANY_MSG = "검사 포기다 — `object`/정확 타입으로 받아 즉시 좁힌다(TypeIs·isinstance)"
ANY_Q = "이 `Any` 를 `object`(즉시 좁힘)·정확 타입으로 바꿀 수 있나(프레임워크 계약이라도 우리 선언은 `object` 다)"


def _any_bindings(mod: ast.Module) -> "tuple[set[str], set[str]]":
    """`typing.Any`/`typing_extensions.Any` 로 해소되는 모듈 수준 로컬 이름 + typing 계열 모듈 별칭.

    `_module_bindings` 는 출처 모듈을 버리고 원명만 남기므로 따로 센다(같은 걷기 규칙 —
    if/try 하위 문 포함 · 뒤따르는 모듈 수준 재정의는 그림자 · 함수·클래스 본문 안 import 는 안 본다)."""
    names: set[str] = {"Any"}  # fail-closed — 모듈 수준 비-Any 바인딩이 그림자하기 전까지 `Any` 이름은 Any 다
    mods: set[str] = set()

    def shadow(name: str) -> None:
        names.discard(name)
        mods.discard(name)

    def walk(stmts: list[ast.stmt]) -> None:
        for st in stmts:
            if isinstance(st, ast.ImportFrom):
                for a in st.names:
                    local: str = a.asname or a.name
                    shadow(local)
                    if st.module in ANY_MODULES and a.name == "Any":
                        names.add(local)
            elif isinstance(st, ast.Import):
                for a in st.names:
                    local = a.asname or a.name.split(".")[0]
                    shadow(local)
                    if a.name in ANY_MODULES:
                        mods.add(local)
            elif isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                shadow(st.name)
            elif isinstance(st, ast.Assign):
                for tg in st.targets:
                    if isinstance(tg, ast.Name):
                        shadow(tg.id)
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                shadow(st.target.id)
            elif isinstance(st, ast.If):
                walk(st.body)
                walk(st.orelse)
            elif isinstance(st, ast.Try):
                walk(st.body)
                for h in st.handlers:
                    walk(h.body)
                walk(st.orelse)
                walk(st.finalbody)

    walk(mod.body)
    return names, mods


def _is_any(node: ast.AST, names: set[str], mods: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, ast.Attribute):
        return node.attr == "Any" and isinstance(node.value, ast.Name) and node.value.id in mods
    return False


def _unstring(node: ast.AST) -> ast.AST:
    """문자열 애너테이션(`"Any"`)은 재파싱한 표현으로 — 실패하면 그대로."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return node
    return node


def _union_members(node: ast.AST) -> "list[ast.AST] | None":
    """`X | Y` · `Optional[X]` · `Union[X, Y]` 의 구성원(평탄화) — 합집합 꼴이 아니면 None."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        out: list[ast.AST] = []
        for side in (node.left, node.right):
            m = _union_members(_unstring(side))
            out.extend(m if m is not None else [_unstring(side)])
        return out
    if isinstance(node, ast.Subscript) and _name_of(node.value) in ("Optional", "Union"):
        sl = node.slice
        elts = list(sl.elts) if isinstance(sl, ast.Tuple) else [sl]
        out = []
        for e in elts:
            m = _union_members(_unstring(e))
            out.extend(m if m is not None else [_unstring(e)])
        if _name_of(node.value) == "Optional":
            out.append(ast.Constant(value=None))
        return out
    return None


def _explicit_any(ann: "ast.AST | None", names: set[str], mods: set[str]) -> "str | None":
    """애너테이션의 명시 `Any` — "bare"(루트가 Any · `| None`/Optional/Union 을 평탄화한 구성원에 Any 가
    하나라도 있음(Any 는 합집합을 삼킨다) · `Annotated[Any, …]` 의 루트) · "nested"(하위 어딘가에 Any —
    제네릭 인자·Callable·type[]) · None. `Literal["Any"]` 의 문자열은 타입이 아니라 값이라 제외."""
    if ann is None:
        return None
    node = _unstring(ann)
    if _is_any(node, names, mods):
        return "bare"
    if isinstance(node, ast.Subscript) and _name_of(node.value) == "Annotated":
        first = node.slice.elts[0] if isinstance(node.slice, ast.Tuple) and node.slice.elts else node.slice
        if _explicit_any(first, names, mods) == "bare":
            return "bare"
    members = _union_members(node)
    if members is not None:
        rest = [m for m in members if not (isinstance(m, ast.Constant) and m.value is None)]
        if rest and any(_is_any(m, names, mods) for m in rest):
            return "bare"
    literal_values: set[int] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Subscript) and _name_of(n.value) == "Literal":
            literal_values |= {id(v) for v in ast.walk(n.slice)}
    for n in ast.walk(node):
        if id(n) in literal_values:
            continue
        if _is_any(n, names, mods):
            return "nested"
        if n is not node and isinstance(n, ast.Constant) and isinstance(n.value, str):
            inner = _unstring(n)
            if inner is not n and any(_is_any(m, names, mods) for m in ast.walk(inner)):
                return "nested"
    return None


RECORD_MSG = "값 자리가 `{v}` 다 — 키가 정해진 값 묶음은 `TypedDict`(파싱한 JSON 은 `TypeAdapter` 검증 파싱) · 조회표는 `dict[K, 구체 V]` · 통과 값은 `JsonValue`"
RECORD_Q = "이 `object` 는 입구(검증·좁히기 도우미의 매개변수 · 즉시 검증되는 지역 변수)인가 — 받는 즉시 `TypeAdapter`/`TypeIs` 로 좁히는가"
RETURN_OBJECT_Q = "이 `object` 를 정확 타입 / 도메인 이벤트 union(`list[<Bc>Event]`) / `JsonValue` 로 바꿀 수 있는가 — 좁히기 도우미면 `TypeIs[...]` 반환으로 · 스텁이 `object` 로 강제한 프레임워크 콜백 미러면 통과"


def _in_rule_roots(rel: Path) -> bool:
    return bool(RULE_ROOTS & set(rel.parts))


def _leaf(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def _record_value(ann: "ast.AST | None", names: set[str], mods: set[str], bindings: dict[str, str]) -> "tuple[str | None, bool]":
    """#647 재료 — 애너테이션 안 `dict/Mapping[…, V]` 의 값 V 가 `Any`/`object` 인가 · (값, 루트인가).
    `Any` 가 하나라도 있으면 ("Any", top?) · 아니면 `object` 가 있으면 ("object", top?) · 그 밖 (None, False)."""
    if ann is None:
        return None, False
    root = _unstring(ann)
    literal_values: set[int] = set()
    for n in ast.walk(root):
        if isinstance(n, ast.Subscript) and _name_of(n.value) == "Literal":
            literal_values |= {id(v) for v in ast.walk(n.slice)}
    found: dict[str, bool] = {}
    for n in ast.walk(root):
        if id(n) in literal_values or not isinstance(n, ast.Subscript):
            continue
        if _leaf(_resolved_name(n.value, bindings)) not in RECORD_CONTAINERS:
            continue
        elts = list(n.slice.elts) if isinstance(n.slice, ast.Tuple) else [n.slice]
        if not elts:
            continue
        val = _unstring(elts[-1])
        kind = "Any" if _is_any(val, names, mods) else ("object" if isinstance(val, ast.Name) and val.id == "object" else None)
        if kind is None:
            continue
        found[kind] = found.get(kind, False) or (n is root)
    if "Any" in found:
        return "Any", found["Any"]
    if "object" in found:
        return "object", found["object"]
    return None, False


def _return_object_placeholder(ann: "ast.AST | None", bindings: dict[str, str]) -> bool:
    """반환 주석의 자리표시 `object` — 루트 · union 구성원 · 시퀀스 컨테이너 원소(`TypeIs/TypeGuard` 루트 제외)."""
    if ann is None:
        return False
    root = _unstring(ann)
    if isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS:
        return False
    members = _union_members(root) or [root]
    for m in members:
        m = _unstring(m)
        if isinstance(m, ast.Name) and m.id == "object":
            return True
        if isinstance(m, ast.Subscript) and _leaf(_resolved_name(m.value, bindings)) in SEQUENCE_CONTAINERS:
            elts = list(m.slice.elts) if isinstance(m.slice, ast.Tuple) else [m.slice]
            if any(isinstance(_unstring(e), ast.Name) and _unstring(e).id == "object" for e in elts):
                return True
    return False


def _exempt_override(fn: "ast.FunctionDef | ast.AsyncFunctionDef", cls: "ast.ClassDef | None",
                     bindings: dict[str, str], aliases: "dict[str, list[tuple[ast.AST, bool]]] | None") -> bool:
    """`clean()`×Form 계열 · `deconstruct()`×Field 계열 — 스텁이 강제하는 오버라이드(`dict[str, object]` 반환 면제)."""
    if cls is None or fn.name not in FRAMEWORK_OVERRIDE_EXEMPT:
        return False
    want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]
    for b in cls.bases:
        for base in _resolved_bases(b, bindings, aliases):  # 별칭 정의 전부(mixin-first 중간 ClassDef 포함) — `_is_declarative_class` 와 같은 해소
            if base in want or (fn.name == "deconstruct" and base.endswith("Field")):
                return True
    return False


def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates,
                        bindings: "dict[str, str] | None" = None,
                        aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
    """#645 — 시그니처 bare `Any` 는 위반 · 시그니처 nested 와 변수/속성/클래스 필드의 `Any` 는 ⓓ 후보.
    #647 — 같은 애너테이션에서 먼저 판정한다: `dict/Mapping` 값 자리 `Any` 는 전 자리 차단 · `object` 는
    반환/클래스 속성 차단 · 매개변수/변수 ⓓ(면제 = `TypeIs/TypeGuard` 루트 · 스텁 강제 오버라이드).
    #647 위반이 난 애너테이션은 #645 nested ⓓ 를 생략한다(bare 는 유지 — 슬롯이 다르다). #647 은
    `application/`·`framework/` 루트만. #493 과 독립이다(«존재»는 #493 · «내용»은 #645/#647)."""
    names, mods = _any_bindings(mod)
    bindings = bindings if bindings is not None else _module_bindings(mod)
    in_roots = _in_rule_roots(rel)
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(mod):
        for child in ast.iter_child_nodes(node):
            parent[child] = node
    hits: list[tuple[int, str, str, str, str, str]] = []  # (lineno, kind, rule, where, msg, question)

    def judge(ann: "ast.AST | None", site: str, where: str, label: str, lineno: int,
              exempt_object: bool, bare_msg: str, nested_msg: str) -> None:
        """한 애너테이션에 #647 → #645 순으로 판정한다(#645 문면·심각도는 종전 그대로 — 시그니처 bare 만 위반)."""
        v645 = _explicit_any(ann, names, mods)
        blocked647 = False
        if in_roots and ann is not None:
            value, _top = _record_value(ann, names, mods, bindings)
            root = _unstring(ann)
            guard_root = isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS
            if value == "Any":
                hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="Any"), ""))
                blocked647 = True
            elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):
                if site in ("sig-return", "class-attr"):
                    hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="object") + " — 반환·속성에 남은 `object` 는 좁히지 않은 누수다", ""))
                    blocked647 = True
                else:
                    hits.append((lineno, "c", "#647", where, f"{label}의 `dict/Mapping[…, object]`", RECORD_Q))
            if site == "sig-return" and not blocked647 and not exempt_object and _return_object_placeholder(ann, bindings):
                hits.append((lineno, "c", "#647", where, f"{label}의 자리표시 `object`", RETURN_OBJECT_Q))
        if v645 == "bare" and site in ("sig-param", "sig-star", "sig-return"):
            hits.append((lineno, "v", "#645", where, bare_msg, ""))
        elif v645 == "bare":
            hits.append((lineno, "c", "#645", where, bare_msg, ANY_Q))
        elif v645 == "nested" and not blocked647:
            hits.append((lineno, "c", "#645", where, nested_msg, ANY_Q))

    for node in ast.walk(mod):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cls = parent.get(node)
            cls = cls if isinstance(cls, ast.ClassDef) else None
            in_class = cls is not None
            is_static = any(_name_of(d) == "staticmethod" for d in node.decorator_list)
            args = node.args
            slots: list[tuple[str, "ast.AST | None", str]] = []
            for i, a in enumerate(list(args.posonlyargs) + list(args.args)):
                if in_class and not is_static and i == 0 and a.arg in ("self", "cls"):
                    continue
                slots.append((a.arg, a.annotation, "sig-param"))
            slots += [(a.arg, a.annotation, "sig-param") for a in args.kwonlyargs]
            slots += [(f"*{a.arg}", a.annotation, "sig-star") for a in (args.vararg, args.kwarg) if a is not None]
            where = f"{rel}:{node.lineno}"
            for label, ann, site in slots:
                judge(ann, site, where, f"`{node.name}()` 매개변수 `{label}`", node.lineno, False,
                      f"`{node.name}()` 매개변수 `{label}` 가 `Any` 다 — {ANY_MSG}",
                      f"`{node.name}()` 매개변수 `{label}` 의 타입 안에 `Any`")
            judge(node.returns, "sig-return", where, f"`{node.name}()` 반환 타입", node.lineno,
                  _exempt_override(node, cls, bindings, aliases),
                  f"`{node.name}()` 반환 타입이 `Any` 다 — {ANY_MSG}",
                  f"`{node.name}()` 반환 타입 안에 `Any`")
        elif isinstance(node, ast.AnnAssign):
            site = "class-attr" if isinstance(parent.get(node), ast.ClassDef) else "variable"
            target = ast.unparse(node.target)
            judge(node.annotation, site, f"{rel}:{node.lineno}", f"`{target}` 주석", node.lineno, False,
                  f"`{target}` 주석에 `Any`(bare)", f"`{target}` 주석에 `Any`(nested)")
    for lineno, kind, rule, where, msg, q in sorted(hits, key=lambda h: (h[0], h[2], h[1])):
        if kind == "v":
            out.add(rule, where, msg)
        else:
            cands.add(rule, where, msg, q)


# ── #646 — django-stubs 제네릭 기저 ──────────────────────────────────────────
STUB_Q_NOCODE = "헤더의 code 없는 `# type: ignore` 가 덮은 진단이 django-stubs 제네릭 `[type-arg]` 인가(그러면 #646 — ignore 를 지우고 `TYPE_CHECKING` 별칭으로)"
STUB_Q_RUNTIME = "`django_stubs_ext.monkeypatch()` 를 채택했는가(houserules §6.1 관찰 — 아니면 런타임 `TypeError` · `TYPE_CHECKING` 별칭으로)"


def _stub_generic_origin(node: ast.AST, origins: dict[str, str]) -> "str | None":
    """Name/Attribute 가 django-stubs 제네릭 기저(모듈∈허용 ∧ 이름∈집합)로 해소되면 dotted origin."""
    dotted = _dotted(node, origins)
    if "." not in dotted:
        return None
    module, name = dotted.rsplit(".", 1)
    if module in STUB_GENERIC_MODULES and (name in STUB_GENERIC_ADMIN_FORM_NAMES or name in STUB_GENERIC_CBV_NAMES):
        return dotted
    return None


def _classify_base(b: ast.AST, origins: dict[str, str], bindings: dict[str, str],
                   aliases: "dict[str, list[tuple[ast.AST, bool]]]", in_tc_class: bool,
                   depth: int = 0) -> "tuple[str, str] | None":
    """기저 하나의 판정 — (상태, origin) · 기저 집합 밖이면 None.
    상태: bare(맨몸 · 직접/맨몸 별칭) · alias-tc(TYPE_CHECKING 별칭·중간 ClassDef) · subscript-runtime(런타임 subscript · ⓓ) ·
    subscript-tc(TYPE_CHECKING 분기 안 클래스의 직접 subscript · 통과)."""
    if isinstance(b, ast.Subscript):
        origin = _stub_generic_origin(b.value, origins)
        if origin is None:
            return None
        return ("subscript-tc" if in_tc_class else "subscript-runtime", origin)
    if isinstance(b, ast.Name) and b.id not in bindings and b.id in aliases and depth < 4:
        defs = aliases[b.id]
        tc_sub = [v for v, tc in defs if tc and isinstance(v, ast.Subscript) and _stub_generic_origin(v.value, origins)]
        if tc_sub:
            return ("alias-tc", _stub_generic_origin(tc_sub[-1].value, origins) or "")
        rt = defs[-1][0]
        if isinstance(rt, ast.Subscript):
            origin = _stub_generic_origin(rt.value, origins)
            return None if origin is None else ("subscript-runtime", origin)
        if isinstance(rt, (ast.Name, ast.Attribute)):
            inner = _classify_base(rt, origins, bindings, aliases, False, depth + 1)
            return inner
        return None
    origin = _stub_generic_origin(b, origins)
    return None if origin is None else ("bare", origin)


def _class_header_end(src: str, cls: ast.ClassDef) -> int:
    """헤더 범위 끝 줄 — `class` NAME 토큰(cls.lineno)부터 괄호 깊이 0 의 첫 `:` OP 토큰 줄(데코레이터 제외)."""
    import io
    import tokenize
    depth = 0
    started = False
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.start[0] < cls.lineno:
                continue
            if not started:
                if tok.type == tokenize.NAME and tok.string == "class" and tok.start[0] == cls.lineno:
                    started = True
                continue
            if tok.type == tokenize.OP:
                if tok.string in "([{":
                    depth += 1
                elif tok.string in ")]}":
                    depth -= 1
                elif tok.string == ":" and depth == 0:
                    return tok.start[0]
    except (tokenize.TokenError, IndentationError):
        pass
    return cls.lineno


def _ignore_codes(line: str) -> "list[str] | None":
    """줄의 `# type: ignore[...]` — 코드 목록(없으면 []) · 주석이 없으면 None."""
    m = TYPE_IGNORE_RE.search(line)
    if m is None:
        return None
    return [c.strip() for c in (m.group(1) or "").split(",") if c.strip()]


def _check_stub_generic_bases(mod: ast.Module, src: str, rel: Path, out: Findings, cands: Candidates,
                              origins: dict[str, str], bindings: dict[str, str],
                              aliases: "dict[str, list[tuple[ast.AST, bool]]]") -> None:
    """#646 — ⓐ 맨몸 상속 · ⓑ 헤더/속성 줄의 `# type: ignore[type-arg]` · ⓓ code 없는 ignore · 런타임 subscript."""
    if not _in_rule_roots(rel):
        return
    lines = src.splitlines()
    tc_classes: set[ast.ClassDef] = set()
    rt_only: set[ast.ClassDef] = set()  # `if TYPE_CHECKING:` 의 else 직계 ClassDef — 런타임 짝(맨몸이 정당 · ⓐ 대상 밖)

    def mark_tc(stmts: list[ast.stmt], in_tc: bool) -> None:
        for st in stmts:
            if isinstance(st, ast.ClassDef) and in_tc:
                tc_classes.add(st)
            elif isinstance(st, ast.If):
                if _is_type_checking(st.test):
                    rt_only.update(s for s in st.orelse if isinstance(s, ast.ClassDef))
                mark_tc(st.body, in_tc or _is_type_checking(st.test))
                mark_tc(st.orelse, in_tc)
            elif isinstance(st, ast.Try):
                mark_tc(st.body, in_tc)
                for h in st.handlers:
                    mark_tc(h.body, in_tc)
                mark_tc(st.orelse, in_tc)
                mark_tc(st.finalbody, in_tc)

    mark_tc(mod.body, False)
    for cls in (n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)):
        where = f"{rel}:{cls.lineno}"
        end = _class_header_end(src, cls)
        header_ignore: "list[str] | None" = None
        for ln in range(cls.lineno, end + 1):
            codes = _ignore_codes(lines[ln - 1]) if ln - 1 < len(lines) else None
            if codes is not None:
                header_ignore = codes if header_ignore is None else header_ignore + codes
        stub_bases = [c for c in (_classify_base(b, origins, bindings, aliases, cls in tc_classes) for b in cls.bases) if c]
        bare = [o for s, o in stub_bases if s == "bare"]
        runtime_sub = [o for s, o in stub_bases if s == "subscript-runtime"]
        origin_label = _leaf(bare[0]) if bare else (_leaf(stub_bases[0][1]) if stub_bases else "")
        if header_ignore is not None and "type-arg" in header_ignore:
            out.add("#646", where, f"`{cls.name}`{f'(기저 `{origin_label}`)' if origin_label else ''} 헤더의 `# type: ignore[type-arg]` — django-stubs 제네릭 맨몸을 덮었다 · 별칭(`TYPE_CHECKING`) 또는 subscript 로 적는다")
        elif bare and cls not in rt_only:
            out.add("#646", where, f"`{cls.name}` 이 django-stubs 제네릭 기저 `{_leaf(bare[0])}` 를 맨몸으로 상속했다 — mypy strict `[type-arg]` 빚 · `if TYPE_CHECKING:` 별칭으로 모델 타입 인자를 적는다")
        elif header_ignore is not None and not header_ignore:
            cands.add("#646", where, f"`{cls.name}` 헤더의 code 없는 `# type: ignore`", STUB_Q_NOCODE)
        if runtime_sub:
            cands.add("#646", where, f"`{cls.name}` 의 기저 `{_leaf(runtime_sub[0])}[…]` 가 `TYPE_CHECKING` 밖 subscript 다", STUB_Q_RUNTIME)
        if stub_bases:
            for st in cls.body:
                if isinstance(st, (ast.Assign, ast.AnnAssign)):
                    for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):
                        if ln <= end:
                            continue  # 한 줄 클래스(`class X(B): x = 1  # type: ignore[type-arg]`)는 헤더 ⓑ(i) 가 이미 셌다
                        codes = _ignore_codes(lines[ln - 1]) if ln - 1 < len(lines) else None
                        if codes and "type-arg" in codes:
                            out.add("#646", f"{rel}:{ln}", f"`{cls.name}` 속성 줄의 `# type: ignore[type-arg]` — 스텁 선언(`ClassVar`)이 타입을 소유하는 자리는 재선언하지 않는다 · 인라인 목록은 bound 로 적는다")
                            break


# ── #650 — json.load(s) 무검증 흐름(ⓓ 전용) ─────────────────────────────────
JSON_Q = "`TypeAdapter(<TypedDict>).validate_python/validate_json` 으로 검증하며 받았거나 `x: object` 로 받아 즉시 좁혔는가 — 결과가 `object` 아닌 자리로 그냥 흐른다"


def _slot_is_object(ann: "ast.AST | None", depth: int, bindings: dict[str, str], idx: "int | None" = None) -> bool:
    """결과가 놓이는 자리의 «선언 값 타입»이 object 인가 — depth 0 = 결과 자체 · 1 = 컨테이너 원소(`idx` = 이종 튜플의
    원소 위치 · -1 = dict 리터럴의 키 자리 · None = 값/원소 자리). `...` 는 원소가 아니다. union 은 전 구성원(None 제외)이
    object 슬롯일 때만 True. 주석 부재는 False(후보 — 반환 주석 없는 함수)."""
    if ann is None:
        return False
    ann = _unstring(ann)
    members = _union_members(ann)
    if members is not None:
        rest = [m for m in members if not (isinstance(m, ast.Constant) and m.value is None)]
        return bool(rest) and all(_slot_is_object(m, depth, bindings, idx) for m in rest)
    if depth == 0:
        return isinstance(ann, ast.Name) and ann.id == "object"
    if isinstance(ann, ast.Subscript) and _leaf(_resolved_name(ann.value, bindings)) in (RECORD_CONTAINERS | SEQUENCE_CONTAINERS):
        elts = list(ann.slice.elts) if isinstance(ann.slice, ast.Tuple) else [ann.slice]
        variadic = any(isinstance(e, ast.Constant) and e.value is Ellipsis for e in elts)
        elts = [e for e in elts if not (isinstance(e, ast.Constant) and e.value is Ellipsis)]
        if not elts:
            return False
        if idx is not None and idx >= 0 and _leaf(_resolved_name(ann.value, bindings)) in ("tuple", "Tuple") and not variadic:
            pick = elts[idx] if idx < len(elts) else elts[-1]  # 이종 튜플 — 그 원소의 자리
        elif idx == -1 and len(elts) > 1:
            pick = elts[0]  # dict 키 자리
        else:
            pick = elts[-1]  # 값/원소 자리
        val = _unstring(pick)
        return isinstance(val, ast.Name) and val.id == "object"
    return False


def _check_json_load(mod: ast.Module, rel: Path, cands: Candidates, origins: dict[str, str], bindings: dict[str, str]) -> None:
    """#650 (ⓓ) — `json.load|loads` 결과가 `object` 아닌 선언 자리로 흐르면 후보."""
    if not _in_rule_roots(rel):
        return
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(mod):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    def is_json_load(call: ast.Call) -> bool:
        fn = call.func
        if isinstance(fn, ast.Attribute):
            return fn.attr in JSON_LOAD_NAMES and _dotted(fn.value, origins) == "json"
        return isinstance(fn, ast.Name) and origins.get(fn.id, "") in {f"json.{n}" for n in JSON_LOAD_NAMES}

    def enclosing_fn(n: ast.AST) -> "ast.FunctionDef | ast.AsyncFunctionDef | None":
        q: "ast.AST | None" = n
        while q is not None:
            q = parent.get(q)
            if isinstance(q, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return q
        return None

    def judge(node: ast.AST, depth: int, idx: "int | None" = None) -> "tuple[bool, str, int]":
        p = parent.get(node)
        if isinstance(p, ast.AnnAssign):
            return (not _slot_is_object(p.annotation, depth, bindings, idx), "주석 변수", p.lineno)
        if isinstance(p, ast.Assign):
            return (False, "", p.lineno)  # 무주석 — #493 몫
        if isinstance(p, ast.Return):
            fn = enclosing_fn(node)
            ann = fn.returns if fn is not None else None
            return (not _slot_is_object(ann, depth, bindings, idx), "반환", p.lineno)
        if isinstance(p, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
            return (True, "컴프리헨션 요소", node.lineno)
        if isinstance(p, (ast.Subscript, ast.Attribute)):
            return (True, "직접 첨자/속성 접근", node.lineno)
        if isinstance(p, (ast.Dict, ast.List, ast.Tuple, ast.Set)) and depth == 0:
            pos: "int | None" = None
            if isinstance(p, ast.Tuple):
                pos = next((i for i, e in enumerate(p.elts) if e is node), None)
            elif isinstance(p, ast.Dict) and any(k is node for k in p.keys):
                pos = -1  # dict 리터럴의 키 자리
            cand, why, ln = judge(p, 1, pos)
            return (cand, "리터럴 컨테이너 요소 → " + why if why else "", ln)
        return (False, "", node.lineno)

    for node in ast.walk(mod):
        if isinstance(node, ast.Call) and is_json_load(node):
            cand, why, ln = judge(node, 0)
            if cand:
                fn_name = _dotted(node.func, origins).rsplit(".", 1)[-1] if isinstance(node.func, ast.Name) else _name_of(node.func)
                cands.add("#650", f"{rel}:{ln}", f"`json.{fn_name}(…)` 결과가 {why}로 흐른다", JSON_Q)


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
            src = f.read_text(encoding="utf-8")
            mod = ast.parse(src)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        rel = f.relative_to(target)
        parts = set(rel.parts)
        bindings = _module_bindings(mod)
        aliases = _alias_defs(mod)
        origins = _origin_bindings(mod)
        _scan_stmts(mod.body, "module", set(), rel, findings, False, bindings, aliases)
        _check_explicit_any(mod, rel, findings, candidates, bindings, aliases)
        _check_stub_generic_bases(mod, src, rel, findings, candidates, origins, bindings, aliases)
        _check_json_load(mod, rel, candidates, origins, bindings)
        if (parts & DRIVEN_DIRS) and "domain_bypass_query" in parts:
            _check_thin_read(mod, rel, findings)
        if (parts & OHS_DIRS) and "contract" in parts and "exception" in parts:
            _check_contract_exceptions(f, mod, rel, findings)
        _collect_runtime_guards(mod, rel, candidates)

    if findings:
        print(f"blocker {len(findings)}건 — 타입 전면 규율 위반 (#493 «첫 대입에 타입» · #645/#647 `Any`·레코드 · #646 django-stubs 제네릭 기저 외)")
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
