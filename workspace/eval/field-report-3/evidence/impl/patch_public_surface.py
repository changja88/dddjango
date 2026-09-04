"""④-1 조각 1 — check-public-surface-annotation.py 패치(#493 별칭 해소 수리 · #646 · #647 · #650).
계획 v2 Δ5·Δ6·Δ7 · rv3-A §2.1~§2.7 명세. 원본을 제자리 편집한다(앵커 문자열 assert · 1회만 적용).
실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib, sys

P = pathlib.Path("dddjango/scripts/check-public-surface-annotation.py")
t = P.read_text(encoding="utf-8")
assert "#646" not in t, "이미 패치됨"


def rep(old: str, new: str, count: int = 1) -> None:
    global t
    assert t.count(old) == count, (t.count(old), old[:80])
    t = t.replace(old, new)


# ── 1. docstring — 규칙 3 추가 + 검출 한계 ───────────────────────────────────
rep(
    "       이름(fail-closed) 포함)는 위반 · 시그니처 안 nested(`dict[str, Any]`)와 변수·속성·클래스\n"
    "       필드의 `Any` 는 ⓓ 후보(exit 불산입). #493(주석 «존재»)과 독립. 검출 한계: `TypeAlias`\n"
    "       재별칭·`cast(Any, …)`·함수 본문/`with`/클래스 본문 안 import 는 표면 밖.\n",
    "       이름(fail-closed) 포함)는 위반 · 시그니처 안 nested(`dict[str, Any]`)와 변수·속성·클래스\n"
    "       필드의 `Any` 는 ⓓ 후보(exit 불산입) — 단 `dict`/`Mapping`/`MutableMapping` 값 자리의 `Any` 는\n"
    "       #647 이 소유한다(그 애너테이션의 nested ⓓ 는 생략 · bare 는 유지). #493(주석 «존재»)과 독립.\n"
    "       검출 한계: `TypeAlias` 재별칭·`cast(Any, …)`·함수 본문/`with`/클래스 본문 안 import 는 표면 밖.\n"
    "  #646 django-stubs 제네릭 Django 기저(타입 매개변수에 기본값이 없는 것 — django-stubs 6.1.0 `.pyi` 전수:\n"
    "       admin 5 `BaseModelAdmin`·`ModelAdmin`·`InlineModelAdmin`·`StackedInline`·`TabularInline` · forms 9\n"
    "       `BaseModelForm`·`ModelForm`·`BaseModelFormSet`·`BaseInlineFormSet`·`ModelChoiceField`·\n"
    "       `ModelMultipleChoiceField`·`ModelChoiceIterator`·`ModelFormOptions`·`BaseFormSet` · CBV 32(detail·list·\n"
    "       edit·dates 의 `_M`/`_FormT`/`_ModelFormT` 제네릭) — `View`·`TemplateView`·`RedirectView`·\n"
    "       `*TemplateResponseMixin`·`ProcessFormView` 는 기본값/비제네릭이라 제외 · 스텁 상향 시 재열거)는\n"
    "       런타임이 subscript 를 못 하므로 모델 타입 인자를 **`if TYPE_CHECKING:` 별칭**(또는 분기 안 중간\n"
    "       ClassDef)으로 적는다. 위반: ⓐ 맨몸 상속(직접·모듈 수준 맨몸 별칭 경유) ⓑ 클래스 헤더 범위\n"
    "       (`class` 줄~괄호 깊이 0 의 첫 `:` 줄 · 데코레이터 제외)나 기저 집합 클래스 본문 직계 대입 줄의\n"
    "       `# type: ignore[type-arg]`(은폐) — ⓐ+ⓑ 동시는 클래스당 1건(ⓑ 문면). ⓓ 후보: 헤더의 code 없는\n"
    "       `# type: ignore` · `TYPE_CHECKING` 밖 subscript(별칭·헤더 직접 — 런타임 `TypeError` 후보 · 프로젝트가\n"
    "       `django_stubs_ext.monkeypatch()` 를 채택했으면 정당). 검출 한계: 별칭 추적은 같은 모듈 안(if/try\n"
    "       하위 포함 · 뒤 정의 우선)만 — 타 모듈 import 별칭의 맨몸 여부는 mypy 몫(ⓑ 헤더 판정은 기저\n"
    "       해소와 독립이라 그 경우도 ignore 는 잡는다).\n"
    "  #647 딕셔너리-레코드 — `dict`/`Dict`/`Mapping`/`MutableMapping` 의 값 자리(마지막 슬라이스 원소 · 문자열\n"
    "       주석 재파싱 · `Literal[…]` 안 제외 · 값이 union/기타면 무발화 — #645 nested 몫). 자리×값 매트릭스:\n"
    "         sig-param·sig-star·variable(AnnAssign)  : `Any` 차단(top·nested) · `object` ⓓ 후보(top·nested)\n"
    "         sig-return·class-attr(ClassDef 직계)    : `Any` 차단 · `object` 차단\n"
    "       면제(`object` 만): 반환 루트 `TypeIs`/`TypeGuard[...]` · 스텁이 강제하는 오버라이드\n"
    "       `clean()`×{Form, BaseForm, ModelForm, BaseModelForm} · `deconstruct()`×{Field, *Field}(기저 해소는\n"
    "       #646 과 같은 별칭 기계). 별도 ⓓ: 반환 주석의 자리표시 `object`(루트 · union 구성원 ·\n"
    "       tuple/list/Sequence/Iterable/Iterator/set/frozenset/Collection 원소 — 같은 노드에 차단이 있으면 차단만).\n"
    "  #650 (ast+ · ⓓ 전용) `json.load(s)` 결과의 무검증 흐름 — 결과가 놓이는 자리의 «선언 값 타입»이 `object`\n"
    "       가 아닌 곳(AnnAssign 주석 루트 · Return 의 반환 주석 루트 · 리터럴 컨테이너 요소(그 리터럴이\n"
    "       AnnAssign/Return 값이면 원소 슬롯 · 호출 인자면 비후보) · 컴프리헨션 요소 · 직접 첨자/속성 접근)로\n"
    "       흐르면 후보 · union 은 전 구성원이 `object` 슬롯일 때만 비후보 · `x: object = …` 와 파서 직접\n"
    "       인자·무주석 Assign(#493 몫)은 후보 아님. 좌표 = AnnAssign/Return 문장 줄 · 그 밖 호출 줄.\n"
    "  #646·#647·#650 은 `application/`·`framework/` 루트 안 파일만 본다(kkebi `web/`·`scripts/` 등 자매\n"
    "       플러그인·운영 스크립트 영역 제외 — 기존 5규칙의 대상은 무변).\n",
)

# ── 2. 상수 ─────────────────────────────────────────────────────────────────
rep(
    'DECLARATIVE_DECORATORS = {"dataclass", "define", "frozen", "attrs"}\n',
    'DECLARATIVE_DECORATORS = {"dataclass", "define", "frozen", "attrs"}\n'
    "\n"
    "# #646 — django-stubs 6.1.0 에서 타입 매개변수에 `default=` 가 없는 제네릭 Django 기저(전수 · 스텁 상향 시 재열거).\n"
    "STUB_GENERIC_ADMIN_FORM_NAMES = {\n"
    '    "BaseModelAdmin", "ModelAdmin", "InlineModelAdmin", "StackedInline", "TabularInline",\n'
    '    "BaseModelForm", "ModelForm", "BaseModelFormSet", "BaseInlineFormSet", "ModelChoiceField",\n'
    '    "ModelMultipleChoiceField", "ModelChoiceIterator", "ModelFormOptions", "BaseFormSet",\n'
    "}\n"
    "STUB_GENERIC_CBV_NAMES = {\n"
    '    "SingleObjectMixin", "BaseDetailView", "DetailView",\n'
    '    "MultipleObjectMixin", "BaseListView", "ListView",\n'
    '    "FormMixin", "ModelFormMixin", "BaseFormView", "FormView", "BaseCreateView", "CreateView",\n'
    '    "BaseUpdateView", "UpdateView", "DeletionMixin", "BaseDeleteView", "DeleteView",\n'
    '    "BaseDateListView", "BaseArchiveIndexView", "ArchiveIndexView", "BaseYearArchiveView", "YearArchiveView",\n'
    '    "BaseMonthArchiveView", "MonthArchiveView", "BaseWeekArchiveView", "WeekArchiveView",\n'
    '    "BaseDayArchiveView", "DayArchiveView", "BaseTodayArchiveView", "TodayArchiveView",\n'
    '    "BaseDateDetailView", "DateDetailView",\n'
    "}\n"
    "STUB_GENERIC_MODULES = (\n"
    '    "django.contrib.admin", "django.contrib.admin.options",\n'
    '    "django.forms", "django.forms.models", "django.forms.formsets",\n'
    '    "django.views.generic", "django.views.generic.detail", "django.views.generic.list",\n'
    '    "django.views.generic.edit", "django.views.generic.dates",\n'
    ")\n"
    'RULE_ROOTS = {"application", "framework"}  # #646·#647·#650 루트 필터(신규 3규칙만 — 기존 규칙 무변)\n'
    'TYPE_IGNORE_RE = __import__("re").compile(r"#\\s*type:\\s*ignore(?:\\[([^\\]]*)\\])?")\n'
    "\n"
    "# #647 — 값 자리 판정 재료.\n"
    'RECORD_CONTAINERS = {"dict", "Dict", "Mapping", "MutableMapping"}\n'
    'SEQUENCE_CONTAINERS = {"tuple", "Tuple", "list", "List", "Sequence", "Iterable", "Iterator", "set", "frozenset", "Set", "FrozenSet", "Collection"}\n'
    'TYPE_GUARDS = {"TypeIs", "TypeGuard"}\n'
    "FRAMEWORK_OVERRIDE_EXEMPT = {  # 스텁이 `dict[str, Any]` 반환을 강제하는 오버라이드 — `dict[str, object]` 만 면제\n"
    '    "clean": {"Form", "BaseForm", "ModelForm", "BaseModelForm"},\n'
    '    "deconstruct": {"Field"},  # 이름이 Field 이거나 *Field 로 끝나는 기저\n'
    "}\n"
    'JSON_LOAD_NAMES = {"load", "loads"}\n',
)

# ── 3. 별칭·origin 기계 + #493 기저 해소 수리 ───────────────────────────────
rep(
    "def _is_declarative_class(cls: ast.ClassDef, bindings: dict[str, str]) -> bool:\n"
    "    if cls.name in DECLARATIVE_CLASS_NAMES:\n"
    "        return True\n"
    "    if {_resolved_name(b, bindings) for b in cls.bases} & DECLARATIVE_BASE_NAMES:\n"
    "        return True\n",
    "def _origin_bindings(mod: ast.Module) -> dict[str, str]:\n"
    "    \"\"\"모듈 수준 import 바인딩 — 로컬 이름 → dotted origin(출처 모듈 보존 · `_module_bindings` 와 같은 걷기).\n"
    "\n"
    "    `from django.contrib import admin` → {\"admin\": \"django.contrib.admin\"} · `from x import C as D` → {\"D\": \"x.C\"} ·\n"
    "    `import a.b as x` → {\"x\": \"a.b\"} · `import a` → {\"a\": \"a\"}. 뒤따르는 모듈 수준 재정의는 그림자(pop).\"\"\"\n"
    "    origins: dict[str, str] = {}\n"
    "\n"
    "    def walk(stmts: list[ast.stmt]) -> None:\n"
    "        for st in stmts:\n"
    "            if isinstance(st, ast.ImportFrom):\n"
    "                for a in st.names:\n"
    "                    origins[a.asname or a.name] = f\"{st.module}.{a.name}\" if st.module else a.name\n"
    "            elif isinstance(st, ast.Import):\n"
    "                for a in st.names:\n"
    "                    origins[a.asname or a.name.split(\".\")[0]] = a.name if a.asname else a.name.split(\".\")[0]\n"
    "            elif isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):\n"
    "                origins.pop(st.name, None)\n"
    "            elif isinstance(st, ast.Assign):\n"
    "                for tg in st.targets:\n"
    "                    if isinstance(tg, ast.Name):\n"
    "                        origins.pop(tg.id, None)\n"
    "            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):\n"
    "                origins.pop(st.target.id, None)\n"
    "            elif isinstance(st, ast.If):\n"
    "                walk(st.body)\n"
    "                walk(st.orelse)\n"
    "            elif isinstance(st, ast.Try):\n"
    "                walk(st.body)\n"
    "                for h in st.handlers:\n"
    "                    walk(h.body)\n"
    "                walk(st.orelse)\n"
    "                walk(st.finalbody)\n"
    "\n"
    "    walk(mod.body)\n"
    "    return origins\n"
    "\n"
    "\n"
    "def _dotted(node: ast.AST, origins: dict[str, str]) -> str:\n"
    "    \"\"\"`admin.ModelAdmin` → `django.contrib.admin.ModelAdmin`(루트 Name 을 origin 으로 치환) · 미해소 이름은 그대로.\"\"\"\n"
    "    if isinstance(node, ast.Name):\n"
    "        return origins.get(node.id, node.id)\n"
    "    if isinstance(node, ast.Attribute):\n"
    "        head = _dotted(node.value, origins)\n"
    "        return f\"{head}.{node.attr}\" if head else node.attr\n"
    "    return \"\"\n"
    "\n"
    "\n"
    "def _is_type_checking(test: ast.AST) -> bool:\n"
    "    return (isinstance(test, ast.Name) and test.id == \"TYPE_CHECKING\") or (\n"
    "        isinstance(test, ast.Attribute) and test.attr == \"TYPE_CHECKING\")\n"
    "\n"
    "\n"
    "def _alias_defs(mod: ast.Module) -> \"dict[str, list[tuple[ast.AST, bool]]]\":\n"
    "    \"\"\"모듈 수준 별칭 정의 — 이름 → [(값, TYPE_CHECKING 분기 안인가)] 소스 순서.\n"
    "\n"
    "    값 = Assign/AnnAssign 의 Name/Attribute/Subscript · `TYPE_CHECKING` 분기 안 ClassDef 의 첫 기저.\n"
    "    if/try 하위를 걷고 함수·클래스 본문 안은 보지 않는다. 같은 이름이 import 바인딩과 별칭 양쪽에 있으면\n"
    "    소스 순서상 뒤 정의가 이긴다(`_resolved_base` 가 `bindings` 를 먼저 본다).\"\"\"\n"
    "    out: dict[str, list[tuple[ast.AST, bool]]] = {}\n"
    "\n"
    "    def walk(stmts: list[ast.stmt], in_tc: bool) -> None:\n"
    "        for st in stmts:\n"
    "            if isinstance(st, (ast.Assign, ast.AnnAssign)) and st.value is not None \\\n"
    "                    and isinstance(st.value, (ast.Name, ast.Attribute, ast.Subscript)):\n"
    "                for tg in (st.targets if isinstance(st, ast.Assign) else [st.target]):\n"
    "                    if isinstance(tg, ast.Name):\n"
    "                        out.setdefault(tg.id, []).append((st.value, in_tc))\n"
    "            elif isinstance(st, ast.ClassDef) and in_tc and st.bases:\n"
    "                out.setdefault(st.name, []).append((st.bases[0], True))\n"
    "            elif isinstance(st, ast.If):\n"
    "                walk(st.body, in_tc or _is_type_checking(st.test))\n"
    "                walk(st.orelse, in_tc)\n"
    "            elif isinstance(st, ast.Try):\n"
    "                walk(st.body, in_tc)\n"
    "                for h in st.handlers:\n"
    "                    walk(h.body, in_tc)\n"
    "                walk(st.orelse, in_tc)\n"
    "                walk(st.finalbody, in_tc)\n"
    "\n"
    "    walk(mod.body, False)\n"
    "    return out\n"
    "\n"
    "\n"
    "def _resolved_base(node: ast.AST, bindings: dict[str, str],\n"
    "                   aliases: \"dict[str, list[tuple[ast.AST, bool]]] | None\", depth: int = 0) -> str:\n"
    "    \"\"\"기저 원명 — Subscript 는 `.value` 를 벗기고, 모듈 수준 별칭(뒤 정의 우선)은 depth≤4 로 따라간다.\"\"\"\n"
    "    if isinstance(node, ast.Subscript):\n"
    "        return _resolved_base(node.value, bindings, aliases, depth)\n"
    "    if isinstance(node, ast.Name) and aliases and node.id not in bindings and node.id in aliases and depth < 4:\n"
    "        return _resolved_base(aliases[node.id][-1][0], bindings, aliases, depth + 1)\n"
    "    return _resolved_name(node, bindings)\n"
    "\n"
    "\n"
    "def _is_declarative_class(cls: ast.ClassDef, bindings: dict[str, str],\n"
    "                          aliases: \"dict[str, list[tuple[ast.AST, bool]]] | None\" = None) -> bool:\n"
    "    if cls.name in DECLARATIVE_CLASS_NAMES:\n"
    "        return True\n"
    "    if {_resolved_base(b, bindings, aliases) for b in cls.bases} & DECLARATIVE_BASE_NAMES:\n"
    "        return True\n",
)

# ── 4. _scan_stmts / _scan_class 에 aliases 전달 ────────────────────────────
rep(
    "    stmts: list[ast.stmt], scope: str, bound: set[str], rel: Path,\n"
    "    out: Findings, declarative: bool, bindings: dict[str, str],\n"
    ") -> None:\n",
    "    stmts: list[ast.stmt], scope: str, bound: set[str], rel: Path,\n"
    "    out: Findings, declarative: bool, bindings: dict[str, str],\n"
    "    aliases: \"dict[str, list[tuple[ast.AST, bool]]] | None\" = None,\n"
    ") -> None:\n",
)
rep("            _scan_class(stmt, rel, out, bindings)\n", "            _scan_class(stmt, rel, out, bindings, aliases)\n")
rep("            _scan_stmts(stmt.body, \"function\", fn_bound, rel, out, False, bindings)\n",
    "            _scan_stmts(stmt.body, \"function\", fn_bound, rel, out, False, bindings, aliases)\n")
rep(
    "def _scan_class(cls: ast.ClassDef, rel: Path, out: Findings, bindings: dict[str, str]) -> None:\n"
    "    declarative = _is_declarative_class(cls, bindings)\n"
    "    bound: set[str] = set()\n"
    "    _scan_stmts(cls.body, \"class\", bound, rel, out, declarative, bindings)\n",
    "def _scan_class(cls: ast.ClassDef, rel: Path, out: Findings, bindings: dict[str, str],\n"
    "                aliases: \"dict[str, list[tuple[ast.AST, bool]]] | None\" = None) -> None:\n"
    "    declarative = _is_declarative_class(cls, bindings, aliases)\n"
    "    bound: set[str] = set()\n"
    "    _scan_stmts(cls.body, \"class\", bound, rel, out, declarative, bindings, aliases)\n",
)

rep(", rel, out, declarative, bindings)\n", ", rel, out, declarative, bindings, aliases)\n", count=9)

# ── 5. #645 + #647 · #646 · #650 ─────────────────────────────────────────────
OLD_ANY = t[t.index("def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates) -> None:"):
            t.index("# ── #358 · #456 · #69 ")]
NEW_ANY = r'''RECORD_MSG = "값 자리가 `{v}` 다 — 키가 정해진 값 묶음은 `TypedDict`(파싱한 JSON 은 `TypeAdapter` 검증 파싱) · 조회표는 `dict[K, 구체 V]` · 통과 값은 `JsonValue`"
RECORD_Q = "이 `object` 는 입구(검증·좁히기 도우미의 매개변수 · 즉시 검증되는 지역 변수)인가 — 받는 즉시 `TypeAdapter`/`TypeIs` 로 좁히는가"
RETURN_OBJECT_Q = "이 `object` 를 정확 타입 / 도메인 이벤트 union(`list[<Bc>Event]`) / `JsonValue` 로 바꿀 수 있는가 — 좁히기 도우미면 `TypeIs[...]` 반환으로 · 스텁이 `object` 로 강제한 프레임워크 콜백 미러면 통과"


def _in_rule_roots(rel: Path) -> bool:
    return bool(RULE_ROOTS & set(rel.parts))


def _leaf(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def _record_value(ann: "ast.AST | None", names: set[str], mods: set[str]) -> "tuple[str | None, bool]":
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
        if _leaf(_name_of(n.value)) not in RECORD_CONTAINERS:
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


def _return_object_placeholder(ann: "ast.AST | None") -> bool:
    """반환 주석의 자리표시 `object` — 루트 · union 구성원 · 시퀀스 컨테이너 원소(`TypeIs/TypeGuard` 루트 제외)."""
    if ann is None:
        return False
    root = _unstring(ann)
    if isinstance(root, ast.Subscript) and _name_of(root.value) in TYPE_GUARDS:
        return False
    members = _union_members(root) or [root]
    for m in members:
        m = _unstring(m)
        if isinstance(m, ast.Name) and m.id == "object":
            return True
        if isinstance(m, ast.Subscript) and _leaf(_name_of(m.value)) in SEQUENCE_CONTAINERS:
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
        base = _resolved_base(b, bindings, aliases)
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
              exempt_object: bool) -> None:
        """한 애너테이션에 #647 → #645 순으로 판정한다."""
        v645 = _explicit_any(ann, names, mods)
        blocked647 = False
        if in_roots and ann is not None:
            value, _top = _record_value(ann, names, mods)
            root = _unstring(ann)
            guard_root = isinstance(root, ast.Subscript) and _name_of(root.value) in TYPE_GUARDS
            if value == "Any":
                hits.append((lineno, "v", "#647", where, f"{label} 의 " + RECORD_MSG.format(v="Any"), ""))
                blocked647 = True
            elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):
                if site in ("sig-return", "class-attr"):
                    hits.append((lineno, "v", "#647", where, f"{label} 의 " + RECORD_MSG.format(v="object") + " — 반환·속성에 남은 `object` 는 좁히지 않은 누수다", ""))
                    blocked647 = True
                else:
                    hits.append((lineno, "c", "#647", where, f"{label} 의 `dict/Mapping[…, object]`", RECORD_Q))
            if site == "sig-return" and not blocked647 and not exempt_object and _return_object_placeholder(ann):
                hits.append((lineno, "c", "#647", where, f"{label} 의 자리표시 `object`", RETURN_OBJECT_Q))
        if v645 == "bare":
            hits.append((lineno, "v", "#645", where, f"{label} 가 `Any` 다 — {ANY_MSG}", ""))
        elif v645 == "nested" and not blocked647:
            hits.append((lineno, "c", "#645", where, f"{label} 의 타입 안에 `Any`", ANY_Q))

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
                judge(ann, site, where, f"`{node.name}()` 매개변수 `{label}`", node.lineno, False)
            judge(node.returns, "sig-return", where, f"`{node.name}()` 반환 타입", node.lineno,
                  _exempt_override(node, cls, bindings, aliases))
        elif isinstance(node, ast.AnnAssign):
            site = "class-attr" if isinstance(parent.get(node), ast.ClassDef) else "variable"
            target = ast.unparse(node.target)
            judge(node.annotation, site, f"{rel}:{node.lineno}", f"`{target}` 주석", node.lineno, False)
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

    def mark_tc(stmts: list[ast.stmt], in_tc: bool) -> None:
        for st in stmts:
            if isinstance(st, ast.ClassDef) and in_tc:
                tc_classes.add(st)
            elif isinstance(st, ast.If):
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
        elif bare:
            out.add("#646", where, f"`{cls.name}` 이 django-stubs 제네릭 기저 `{_leaf(bare[0])}` 를 맨몸으로 상속했다 — mypy strict `[type-arg]` 빚 · `if TYPE_CHECKING:` 별칭으로 모델 타입 인자를 적는다")
        elif header_ignore is not None and not header_ignore:
            cands.add("#646", where, f"`{cls.name}` 헤더의 code 없는 `# type: ignore`", STUB_Q_NOCODE)
        if runtime_sub:
            cands.add("#646", where, f"`{cls.name}` 의 기저 `{_leaf(runtime_sub[0])}[…]` 가 `TYPE_CHECKING` 밖 subscript 다", STUB_Q_RUNTIME)
        if stub_bases:
            for st in cls.body:
                if isinstance(st, (ast.Assign, ast.AnnAssign)):
                    for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):
                        codes = _ignore_codes(lines[ln - 1]) if ln - 1 < len(lines) else None
                        if codes and "type-arg" in codes:
                            out.add("#646", f"{rel}:{ln}", f"`{cls.name}` 속성 줄의 `# type: ignore[type-arg]` — 스텁 선언(`ClassVar`)이 타입을 소유하는 자리는 재선언하지 않는다 · 인라인 목록은 bound 로 적는다")
                            break


# ── #650 — json.load(s) 무검증 흐름(ⓓ 전용) ─────────────────────────────────
JSON_Q = "`TypeAdapter(<TypedDict>).validate_python/validate_json` 으로 검증하며 받았거나 `x: object` 로 받아 즉시 좁혔는가 — 결과가 `object` 아닌 자리로 그냥 흐른다"


def _slot_is_object(ann: "ast.AST | None", depth: int) -> bool:
    """결과가 놓이는 자리의 «선언 값 타입»이 object 인가 — depth 0 = 결과 자체 · 1 = 컨테이너 원소.
    union 은 전 구성원(None 제외)이 object 슬롯일 때만 True. 주석 부재는 False(후보 — 반환 주석 없는 함수)."""
    if ann is None:
        return False
    ann = _unstring(ann)
    members = _union_members(ann)
    if members is not None:
        rest = [m for m in members if not (isinstance(m, ast.Constant) and m.value is None)]
        return bool(rest) and all(_slot_is_object(m, depth) for m in rest)
    if depth == 0:
        return isinstance(ann, ast.Name) and ann.id == "object"
    if isinstance(ann, ast.Subscript) and _leaf(_name_of(ann.value)) in (RECORD_CONTAINERS | SEQUENCE_CONTAINERS):
        elts = list(ann.slice.elts) if isinstance(ann.slice, ast.Tuple) else [ann.slice]
        val = _unstring(elts[-1]) if elts else None
        return isinstance(val, ast.Name) and val.id == "object"
    return False


def _check_json_load(mod: ast.Module, rel: Path, cands: Candidates, origins: dict[str, str]) -> None:
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

    def judge(node: ast.AST, depth: int) -> "tuple[bool, str, int]":
        p = parent.get(node)
        if isinstance(p, ast.AnnAssign):
            return (not _slot_is_object(p.annotation, depth), "주석 변수", p.lineno)
        if isinstance(p, ast.Assign):
            return (False, "", p.lineno)  # 무주석 — #493 몫
        if isinstance(p, ast.Return):
            fn = enclosing_fn(node)
            ann = fn.returns if fn is not None else None
            return (not _slot_is_object(ann, depth), "반환", p.lineno)
        if isinstance(p, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
            return (True, "컴프리헨션 요소", node.lineno)
        if isinstance(p, (ast.Subscript, ast.Attribute)):
            return (True, "직접 첨자/속성 접근", node.lineno)
        if isinstance(p, (ast.Dict, ast.List, ast.Tuple, ast.Set)) and depth == 0:
            cand, why, ln = judge(p, 1)
            return (cand, "리터럴 컨테이너 요소 → " + why if why else "", ln)
        return (False, "", node.lineno)

    for node in ast.walk(mod):
        if isinstance(node, ast.Call) and is_json_load(node):
            cand, why, ln = judge(node, 0)
            if cand:
                cands.add("#650", f"{rel}:{ln}", f"`json.{_name_of(node.func) or 'load'}(…)` 결과가 {why}로 흐른다", JSON_Q)


'''
t = t.replace(OLD_ANY, NEW_ANY)

# ── 6. main — 호출 순서 ─────────────────────────────────────────────────────
rep(
    "        rel = f.relative_to(target)\n"
    "        parts = set(rel.parts)\n"
    "        _scan_stmts(mod.body, \"module\", set(), rel, findings, False, _module_bindings(mod))\n"
    "        _check_explicit_any(mod, rel, findings, candidates)\n",
    "        rel = f.relative_to(target)\n"
    "        parts = set(rel.parts)\n"
    "        bindings = _module_bindings(mod)\n"
    "        aliases = _alias_defs(mod)\n"
    "        origins = _origin_bindings(mod)\n"
    "        _scan_stmts(mod.body, \"module\", set(), rel, findings, False, bindings, aliases)\n"
    "        _check_explicit_any(mod, rel, findings, candidates, bindings, aliases)\n"
    "        _check_stub_generic_bases(mod, src, rel, findings, candidates, origins, bindings, aliases)\n"
    "        _check_json_load(mod, rel, candidates, origins)\n",
)
rep(
    "        try:\n"
    "            mod = ast.parse(f.read_text(encoding=\"utf-8\"))\n"
    "        except (SyntaxError, OSError, UnicodeDecodeError):\n"
    "            continue\n"
    "        rel = f.relative_to(target)\n",
    "        try:\n"
    "            src = f.read_text(encoding=\"utf-8\")\n"
    "            mod = ast.parse(src)\n"
    "        except (SyntaxError, OSError, UnicodeDecodeError):\n"
    "            continue\n"
    "        rel = f.relative_to(target)\n",
)
rep(
    "        print(f\"blocker {len(findings)}건 — 타입 전면 규율 위반 (#493 «첫 대입에 타입» 외)\")\n",
    "        print(f\"blocker {len(findings)}건 — 타입 전면 규율 위반 (#493 «첫 대입에 타입» · #645/#647 `Any`·레코드 · #646 django-stubs 제네릭 기저 외)\")\n",
)
P.write_text(t, encoding="utf-8")
print("patched", P, len(t.splitlines()), "lines")
