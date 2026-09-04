"""조각 1 온톨로지 편집 — S-1 + S-4 (rv3-B 최종 문안 · rv1-B §3.6/§3.7 · 코디 탐침 정정).
실행: cd /Users/hyun/Desktop/dddjango && .venv/bin/python <this> [--date YYYY-MM-DD]
선행: 편집 전 canon roundtrip byte 동일(roundtrip.py) · md 시드(§18 헤딩+마커)는 render 직전 별도 단계.
"""
import sys, pathlib
sys.path.insert(0, "/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/impl")
import ontlib as L
from ontlib import DJR, RDF, URIRef, Literal, S, D
if "--date" in sys.argv: L.DATE = sys.argv[sys.argv.index("--date") + 1]
DATE = L.DATE
MARK = "<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->"

def new_block(g, sec, n, text, norms=(), kind="norm"):
    """code·table-row = plain literal · norm/prose = @ko (ttl 원문 실측)."""
    b = URIRef(str(sec) + f"/b{n}"); assert (b, None, None) not in g, b
    prev = URIRef(str(sec) + f"/b{n-1}"); assert n == 1 or (prev, DJR.order, Literal(n - 1)) in g, ("order 불연속", b)
    g.add((b, RDF.type, DJR.Block)); g.add((b, DJR.inSection, sec)); g.add((b, DJR.kind, DJR["kind-" + kind])); g.add((b, DJR.order, Literal(n)))
    for r in norms: g.add((b, DJR.statesNorm, DJR[r]))
    g.add((b, DJR.text, Literal(text) if kind in ("table-row", "code") else Literal(text, lang="ko")))
    return b

# ═══ 1. discipline-houserules-skill ═══════════════════════════════════════════
p, g = L.load("rules/discipline-houserules-skill.ttl")
HS = "dddjango/skills/discipline-houserules/SKILL.md"
sec4 = S(HS + "/s007-4"); b7 = S(HS + "/s007-4/b7"); b5 = S(HS + "/s007-4/b5"); b61 = S(HS + "/s011-6.1/b1")
assert (b7, DJR.order, Literal(7)) in g and (S(HS + "/s007-4/b8"), None, None) not in g

B7 = ("**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다). `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.\n\n")
L.set_text(g, b7, B7)
L.revise(g, "R-3447", "Any 금지 — 시그니처(별표 인자 포함)·변수·클래스 속성·제네릭 인자 전부 · 프레임워크 오버라이드도 object/정확 타입 · 시그니처는 #645 차단·그 밖은 ⓓ 후보(#645) · dict/Mapping 값 자리 Any 는 #647 차단", "amendment")
L.revise(g, "R-3448", "경계 입력은 object/정확 타입으로 받아 받는 즉시 좁힘(TypeIs·isinstance·type() is · 자리는 architecture-ddd §3.1) · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만(반환/속성 누수 #647 차단 · 반환 자리표시 object·json.load 무검증 흐름은 ⓓ #647/#650 · 예외 프레임워크 콜백 미러·이벤트 컬렉션) · 면제 Form.clean·TypeIs", "redefinition")

L.new_work(g, "R-3451", "Prohibition", "레코드(키 고정 값 묶음)를 딕셔너리로 들고 다니지 않는다 — 내부 리터럴은 TypedDict · 파싱 JSON 은 TypeAdapter 검증 · 도메인 개념은 값 객체 · dict/Mapping[str, object|Any] 주석은 구조 미정 신호(#647)")
new_block(g, sec4, 8, "**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:\n\n", ["R-3451"])
new_block(g, sec4, 9, "| 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |\n|---|---|---|---|\n", (), "table-row")
ROWS = [
 ("R-3452", "레코드(내부 리터럴) → TypedDict(종류 여럿이면 kind: Literal 판별 키 union) · dict/Mapping[str, object|Any] 금지",
  "| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\\|Any]` |\n"),
 ("R-3453", "레코드(파싱한 JSON — 파일·타 시스템·json.loads · 우리가 쓴 파일도) → TypeAdapter(TypedDict).validate_python/json 검증 파싱(HTTP body 는 ninja Schema) · 파싱 전 값 사용 금지 · 검증 없는 -> TypedDict 반환·Any/object 흘리기 금지(ⓓ #650)",
  "| 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기(ⓓ #650) |\n"),
 ("R-3454", "도메인 개념 → dataclass·값 객체(architecture-ddd §3.1) · 딕셔너리 금지",
  "| 도메인 개념 | 도메인 계층 | dataclass·값 객체(architecture-ddd §3.1) | 딕셔너리 |\n"),
 ("R-3455", "조회표(키가 데이터) → dict[K, V] 에 K·V 구체 타입(V 가 레코드면 TypedDict) · 값 타입 object·Any 금지",
  "| 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]` 에 K·V 구체 타입(V 가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |\n"),
 ("R-3456", "구조 없는 임의 JSON 통과(직렬화·저장 경계) → 재귀 별칭 JsonValue(공변 Sequence/Mapping arm) · dict[str, object]·Any 금지",
  "| 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |\n"),
 ("R-3457", "타입이 이미 있는 값(반환·매개변수·속성) → 실제 클래스 · 입구 밖 자리표시 object 금지(입구 매개변수·즉시 검증 지역 변수는 R-3448 · 반환 주석 object 는 ⓓ #647)",
  "| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |\n\n"),
]
for i, (rid, label, row) in enumerate(ROWS):
    L.new_work(g, rid, "Obligation", label); new_block(g, sec4, 10 + i, row, [rid], "table-row")
L.new_work(g, "R-3458", "Obligation", "django-stubs 제네릭 Django 기저(기본값 없는 타입 매개변수 — ModelForm·BaseInlineFormSet·ModelAdmin·InlineModelAdmin·CBV·mixin)는 모델 타입 인자를 적는다 — TYPE_CHECKING 별칭 기본 · monkeypatch 채택(§6.1 관찰) 시 직접 표기 · admin 선언 속성은 재선언 안 함 · 열린 매개변수는 bound")
L.new_work(g, "R-3459", "Prohibition", "django-stubs 제네릭 기저를 맨몸 상속하거나 # type: ignore[type-arg] 로 덮지 않는다(#646 차단)")
new_block(g, sec4, 16, "**django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin(`View`·`TemplateView`·`RedirectView` 는 기본값이 있어 대상 밖). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.\n\n", ["R-3458", "R-3459"])

L.set_text(g, b5, "- 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·폼 필드 · `class Meta` 옵션 · enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다 · admin 패널 클래스 본문의 Django 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …) — 타입은 스텁의 `ClassVar` 가 소유하고 `inlines` 처럼 재선언이 불변성 red 가 되는 자리가 있어 적지 않는다(적으면 스텁 선언과 같아야 한다 · 선언적 클래스 본문의 메서드는 면제가 아니다)\n\n")
L.revise(g, "R-3154", "문법 부재 자리 ③ 프레임워크 선언(모델 필드·폼 필드·class Meta·enum 멤버·admin 패널 선언 속성 — 스텁 ClassVar 소유)", "amendment")
L.set_text(g, b61, "\n표준 도구셋(패키지 매니저 uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 **직접 다룬다** — 기존 프로젝트의 도구·패키지 매니저를 감지해 존중하고(§1.1), 기능에 필요한 표준 도구가 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업한다(임의 글로벌 설치 금지). `django-stubs-ext` 의 `monkeypatch()`(운영 의존성 + settings 최상단 1줄)는 프로젝트 전역 런타임 패치라 기능 흐름이 도입하지 않는다 — 채택 여부는 관찰(§1 ④)해 §4 의 기저 타입 인자 표기(별칭 / 직접)를 고른다.\n\n")
L.revise(g, "R-3163", "표준 도구셋은 기능 추가 흐름이 직접 다룬다 — 기존 도구 감지·존중, 부재 시 §2.1 버전-핀 규율 셋업(임의 글로벌 설치 금지) · django-stubs-ext monkeypatch 는 전역 패치라 미도입 — 채택 관찰(§1 ④)로 §4 표기(별칭/직접) 결정", "amendment")
L.save(p, g); print("houserules-skill ok")

# ═══ 2. implementation-django-final — 말미 새 절 s094-18 ═══════════════════════
p, g = L.load("rules/implementation-django-final.ttl")
DF = "dddjango/skills/implementation-django/references/final.md"
sec18 = L.new_section(g, DF, "s094-18", "## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저", "18")
L.new_work(g, "R-3460", "Obligation", "admin 저작 화면의 ModelForm·BaseInlineFormSet·ModelAdmin·TabularInline/StackedInline 은 django-stubs 제네릭(런타임 subscript 불가) — 규칙은 houserules §4·§6.1 소유 · 이 절은 한 벌 예시 · 웹 폼 ModelForm 도 같은 표기")
b1 = new_block(g, sec18, 1, "\nadmin 저작 화면(`driven_layer/django_<bc>/admin/` — 배치·import 방향은 `discipline-houserules` §1 트리 82행·§5)의 `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`TabularInline`/`StackedInline` 은 django-stubs 가 제네릭으로 선언하지만 런타임 클래스는 subscript 를 못 한다 — 규칙(타입 인자 필수 · `# type: ignore[type-arg]` 금지 · 별칭 기본 / monkeypatch 채택 시 직접)은 houserules §4·§6.1 이 소유하고, 이 절은 그 «어떻게»를 한 벌로 보인다. 웹 폼의 `ModelForm` 도 같은 표기다(`implementation-django-web` §6).\n\n", ["R-3460"])
g.add((b1, DJR.restates, S(HS + "/s007-4/b16")))
CODE18 = '''```python
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeAlias

from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

if TYPE_CHECKING:  # django-stubs 전용 — 런타임 클래스는 subscript 불가
    _ChildFormBase: TypeAlias = forms.ModelForm[ChildModel]  # noqa: UP040 -- 기저로 쓰는 별칭이라 `type` 문이 될 수 없다
    _ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel]  # noqa: UP040 -- 셋째 인자(폼)는 적지 않는다: 기본값 ModelForm[ChildModel] 만 admin `formset` 자리(불변)와 맞는다
    _ChildInlineBase: TypeAlias = admin.TabularInline[ChildModel, ParentModel]  # noqa: UP040
    _ParentAdminBase: TypeAlias = admin.ModelAdmin[ParentModel]  # noqa: UP040
else:
    _ChildFormBase: type[forms.ModelForm] = forms.ModelForm
    _ChildFormSetBase: type[BaseInlineFormSet] = BaseInlineFormSet
    _ChildInlineBase: type[admin.TabularInline] = admin.TabularInline
    _ParentAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin

# 주석 전용 별칭은 `type` 문(지연 평가) — 자식 모델이 여럿이면 bound 로 적는다(`Any` 아님)
type ParentInlineFormSet = BaseInlineFormSet[Model, ParentModel, ModelForm[Model]]


class ChildInlineForm(_ChildFormBase):
    class Meta:
        model = ChildModel
        fields = ("field_a", "field_b")


class ChildInlineFormSet(_ChildFormSetBase):
    def clean(self) -> None: ...


class ChildInline(_ChildInlineBase):
    model = ChildModel            # admin 선언 속성 — 스텁 ClassVar 가 타입을 소유(houserules §4 면제)
    form = ChildInlineForm
    formset = ChildInlineFormSet
    extra = 0


@admin.register(ParentModel)
class ParentAdmin(_ParentAdminBase):
    readonly_fields = ("version",)  # 무주석 — 스텁 `ClassVar[_ListOrTuple[str]]` 가 타입을 소유
    inlines = [ChildInline]         # 재선언하면 `list[type[InlineModelAdmin[Any, Any]]]` 와 불변성 충돌 — 적지 않는다

    def save_model(self, request: HttpRequest, obj: ParentModel, form: ModelForm[ParentModel], change: bool) -> None: ...

    def save_related(self, request: HttpRequest, form: ModelForm[ParentModel], formsets: Sequence[ParentInlineFormSet], change: bool) -> None: ...
```

'''
new_block(g, sec18, 2, CODE18, (), "code")
L.new_work(g, "R-3461", "Obligation", "monkeypatch 채택 시 admin.ModelAdmin[Parent] 직접 표기 · 그 밖은 별칭 · BaseInlineFormSet 셋째 인자(폼)는 적지 않는다(기본값만 admin.formset 불변 자리와 맞음) · # type: ignore[type-arg] 로 맨몸을 덮지 않는다(#646)")
b3 = new_block(g, sec18, 3, "프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(houserules §6.1 관찰) `if TYPE_CHECKING:` 블록 없이 `class ParentAdmin(admin.ModelAdmin[ParentModel])` 로 직접 적는다 — 그 밖은 위 별칭이다. `BaseInlineFormSet` 의 세 번째 인자(폼 타입)는 적지 않는다 — 기본값 `ModelForm[_M]` 이 스텁 `InlineModelAdmin.formset`(`type[BaseInlineFormSet[_C, _P, ModelForm[_C]]]` · 불변)과 맞는 유일한 값이라 구체 폼 클래스를 적으면 `formset = …` 대입이 `[assignment]` 로 막힌다. `# type: ignore[type-arg]` 로 맨몸을 덮지 않는다(#646).\n", ["R-3461"])
g.add((b3, DJR.restates, S(HS + "/s007-4/b16")))
L.save(p, g); print("implementation-django-final ok (s094-18)")

# ═══ 3. implementation-django-skill — s005/b17 2행 확장 ══════════════════════
p, g = L.load("rules/implementation-django-skill.ttl")
b17 = S("dddjango/skills/implementation-django/SKILL.md/s005/b17")
assert L.text_of(g, b17) == "| Django 5.x 새 기능 | §17 |\n\n"
L.set_text(g, b17, "| Django 5.x 새 기능 | §17 |\n| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |\n\n")
L.save(p, g); print("implementation-django-skill ok")

# ═══ 4. implementation-django-web-final — s003-2/b10 · s007-6/b9 정정 · 새 b10 ══
p, g = L.load("rules/implementation-django-web-final.ttl")
WF = "dddjango/skills/implementation-django-web/references/final.md"
L.replace_in(g, S(WF + "/s003-2/b10"),
 "from django.urls import reverse_lazy\n\n\n# Generic CBV: 보일러플레이트 최소화. queryset은 selector/Manager로 준비\nclass ArticleListView(ListView):",
 "from django.urls import reverse_lazy\nfrom typing import TYPE_CHECKING, TypeAlias\n\nif TYPE_CHECKING:  # Generic CBV 기저는 django-stubs 제네릭 — 표기는 houserules §4(별칭 기본 · monkeypatch 채택 시 ListView[Article] 직접)\n    _ArticleListBase: TypeAlias = ListView[Article]  # noqa: UP040\n    _ArticleCreateBase: TypeAlias = CreateView[Article, ArticleForm]  # noqa: UP040\nelse:\n    _ArticleListBase: type[ListView] = ListView\n    _ArticleCreateBase: type[CreateView] = CreateView\n\n\n# Generic CBV: 보일러플레이트 최소화. queryset은 selector/Manager로 준비\nclass ArticleListView(_ArticleListBase):")
L.replace_in(g, S(WF + "/s003-2/b10"), "class ArticleCreateView(LoginRequiredMixin, CreateView):", "class ArticleCreateView(LoginRequiredMixin, _ArticleCreateBase):")
L.replace_in(g, S(WF + "/s007-6/b9"), "from django.core.exceptions import ValidationError\n\n\n# 검증 순서", "from django.core.exceptions import ValidationError\nfrom typing import TYPE_CHECKING, TypeAlias\n\n\n# 검증 순서")
L.replace_in(g, S(WF + "/s007-6/b9"), "# ModelForm: fields를 명시적으로 나열한다 (\"__all__\"/exclude는 의도치 않은 노출 위험)\nclass ArticleForm(forms.ModelForm):", "if TYPE_CHECKING:  # ModelForm 기저는 django-stubs 제네릭 — 런타임은 subscript 불가(houserules §4)\n    _ArticleFormBase: TypeAlias = forms.ModelForm[Article]  # noqa: UP040\nelse:\n    _ArticleFormBase: type[forms.ModelForm] = forms.ModelForm\n\n\n# ModelForm: fields를 명시적으로 나열한다 (\"__all__\"/exclude는 의도치 않은 노출 위험)\nclass ArticleForm(_ArticleFormBase):")
L.new_work(g, "R-3462", "Obligation", "웹 폼 ModelForm 기저는 django-stubs 제네릭 — 모델 타입 인자를 적는다(TYPE_CHECKING 별칭 · 규칙은 houserules §4 · admin 한 벌은 implementation-django §18)")
new_block(g, S(WF + "/s007-6"), 10, "- `ModelForm` 기저는 django-stubs 제네릭이라 모델 타입 인자를 적는다 — 위 `ArticleForm` 의 `_ArticleFormBase`(`if TYPE_CHECKING:` 별칭 = `forms.ModelForm[Article]` · 런타임은 `forms.ModelForm`)가 그 표기이고, monkeypatch 채택 시 직접 표기와 `# type: ignore[type-arg]` 금지는 `discipline-houserules` §4 소유 · admin 쪽 한 벌은 `implementation-django` §18.\n\n", ["R-3462"])
L.save(p, g); print("implementation-django-web-final ok")

# ═══ 5. implementation-python-final — s007-1.5 b1 rev · 새 b3 ═══════════════
p, g = L.load("rules/implementation-python-final.ttl")
PF = "dddjango/skills/implementation-python/references/final.md"
L.set_text(g, S(PF + "/s007-1.5/b1"), "\n외부 API, JSON 등 이종 데이터를 담는 딕셔너리에는 TypedDict를 사용하라. **키가 정해진 값 묶음(레코드)은 `dict[str, object|Any]` 가 아니라 `TypedDict` 다** — 종류가 여럿이면 `kind: Literal[\"…\"]` 판별 키로 union 을 만든다. 파싱한 JSON(파일·타 시스템·`json.loads` — HTTP body 는 ninja `Schema` 가 이미 검증)은 `pydantic.TypeAdapter(그TypedDict)` 의 `validate_python`/`validate_json` 으로 **검증하며** 받는다(`TypedDict` 는 선언일 뿐 실행 시 검사가 없고, `json.loads` 반환은 `Any` 라 `-> TypedDict` 로 그냥 돌려주면 strict `no-any-return` 이다 · coercion 이 입력을 숨기면 `strict=True` — §12.0). 키가 데이터인 조회표는 `dict[K, 구체 V]`(V 가 레코드면 `TypedDict`). 구조를 정하지 않고 통과·직렬화만 하는 값은 재귀 별칭 `type JsonValue = bool | int | float | str | None | Sequence[JsonValue] | Mapping[str, JsonValue]` 다(arm 은 공변 — `dict[str, str]` 조각을 재확정 없이 담는다). `TypedDict` 는 `JsonValue`·`dict[str, object]` 자리에 못 들어가므로 직렬화 인자로 넘길 때는 `object` 를 받아 `JsonValue` 로 재구성하는 브리지 하나를 둔다(그 `object` 는 입구 매개변수 — houserules §4). 도메인 개념은 값 객체다(architecture-ddd §3.1).\n\n")
L.revise(g, "R-2715", "레코드는 TypedDict(판별 키 union) · 파싱한 JSON 은 TypeAdapter 검증 파싱(no-any-return) · 조회표는 dict[K, 구체 V] · 통과 값은 공변 JsonValue · TypedDict→직렬화는 object 입구 브리지", "amendment")
CODE15 = '''```python
from collections.abc import Mapping, Sequence
from typing import Literal, TypedDict

from pydantic import TypeAdapter


class PageCoordinate(TypedDict):
    coordinate_kind: Literal["page"]
    page_id: str
    page_numbers: list[int]


class SpanCoordinate(TypedDict):
    coordinate_kind: Literal["span"]
    start_offset: int
    end_offset: int


type Coordinate = PageCoordinate | SpanCoordinate          # 판별 키 union — 내부에서 리터럴로 만들 땐 검증 불요

_COORDINATE: TypeAdapter[Coordinate] = TypeAdapter(Coordinate)   # 파싱한 JSON 은 여기서 검증(모듈 상수)


def load_coordinate(raw: str) -> Coordinate:
    return _COORDINATE.validate_json(raw, strict=True)      # `json.loads` → `Any` 를 직접 돌려주지 않는다


type JsonScalar = bool | int | float | str | None
type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]   # 구조 없는 통과·직렬화용


def to_json_value(value: object) -> JsonValue:               # TypedDict → 직렬화 인자 브리지(입구 object)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return {str(k): to_json_value(v) for k, v in value.items()}
    if isinstance(value, Sequence):
        return [to_json_value(v) for v in value]
    raise TypeError(f"not JSON-serializable: {value!r}")
```

'''
new_block(g, S(PF + "/s007-1.5"), 3, CODE15, (), "code")
L.save(p, g); print("implementation-python-final ok")

# ═══ 6. architecture-ddd-final — s040-5.5/b10 예시 정정 ═══════════════════════
p, g = L.load("rules/architecture-ddd-final.ttl")
AB = S("dddjango/skills/architecture-ddd/references/final.md/s040-5.5/b10")
L.replace_in(g, AB, "from dataclasses import dataclass, field\nfrom enum import Enum\nfrom typing import Any\n", "from dataclasses import dataclass, field\nfrom datetime import date\nfrom enum import Enum\n")
L.replace_in(g, AB, "    CHOICE = \"choice\"\n\n\n@dataclass(frozen=True)\nclass FieldDefinition:", "    CHOICE = \"choice\"\n\n\ntype FieldValue = str | int | float | date  # FieldType 에서 파생한 닫힌 union — 필드 집합은 동적, 값 종류는 닫혀 있다\n\n\n@dataclass(frozen=True)\nclass FieldDefinition:")
L.replace_in(g, AB, "    values: dict[str, Any] = field(default_factory=dict)\n\n    def set_field(self, field_name: str, value: Any) -> None:", "    values: dict[str, FieldValue] = field(default_factory=dict)\n\n    def set_field(self, field_name: str, value: FieldValue) -> None:")
L.save(p, g); print("architecture-ddd-final ok")

# ═══ 7. command-dddjango — b6 R-0284 rev4 · b28 R-0345 rev3 ═══════════════════
p, g = L.load("rules/command-dddjango.ttl")
CM = "dddjango/commands/dddjango.md"
L.replace_in(g, S(CM + "/s007/b6"),
 "감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(해당 범위 실행분 — 행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · 해당 범위 실행분)를 동봉한다.",
 "감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · #647 — 입구 매개변수·즉시 검증 지역 변수의 `dict/Mapping[…, object]` 와 반환 주석의 자리표시 `object` · #650 — `json.load(s)` 결과의 무검증 흐름)를 동봉한다 — 두 채널 모두 동봉 범위는 registry_gate 가 앵커 차분으로 가른 **«ⓓ 신규(N′∖L′)»** 절·sidecar 레코드이고, 앵커에도 있던 «ⓓ legacy» 는 게이트 보고의 건수로만 적는다.")
L.revise(g, "R-0284", "필수 입력 5종(코드+테스트·승인 입장 표·역할별 최소 조정 보고·test diff·실행 결과·슬라이스 목록) + ⓓ 후보 동봉(registry #4 200행 신호 · #11 #645/#647/#650) — 동봉 범위는 registry_gate 앵커 차분 ⓓ 신규분", "amendment")
L.set_text(g, S(CM + "/s007/b28"), "   11. `${CLAUDE_PLUGIN_ROOT}/scripts/check-public-surface-annotation.py` — 타입 전면(#493 — 시그니처·지역·속성·모듈/클래스 «모든 이름 첫 대입», 문법 없는 자리만 면제)·명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보 · dict/Mapping 값 자리는 #647 소유)·django-stubs 제네릭 기저(#646 — 맨몸·`type: ignore[type-arg]` 차단 · subscript/`TYPE_CHECKING` 별칭 통과)·딕셔너리-레코드(#647 — `dict/Mapping[…, Any]` 전 자리와 `[…, object]` 반환/속성 차단 · 입구 매개변수·즉시 검증 지역 변수의 `object` 와 반환 주석의 자리표시 `object` 는 ⓓ 후보 · `json.load(s)` 무검증 흐름은 ⓓ #650 · 세 규칙은 `application/`·`framework/` 루트만)·Thin Read 반환(#358)·계약 검증 토큰(#456).\n")
L.revise(g, "R-0345", "registry #11 — 타입 전면(#493)·명시 Any(#645 — 시그니처 차단·변수/제네릭 안 ⓓ 후보)·django-stubs 제네릭 기저(#646)·딕셔너리-레코드(#647 · json.load ⓓ #650 · 신규 3규칙은 application/framework 루트만)·Thin Read 반환(#358)·계약 검증 토큰(#456)", "amendment")
L.save(p, g); print("command-dddjango ok")

# ═══ 8. wiring ═══════════════════════════════════════════════════════════════
DR, PS = "a/agent-discipline-reviewer", "c/check-public-surface-annotation.py"
L.wire("discipline-houserules-skill.ttl",
 [(r, "delegatedTo", DR) for r in ["R-3451","R-3452","R-3453","R-3454","R-3455","R-3456","R-3457","R-3458","R-3459"]] +
 [(r, "enforcedBy", PS) for r in ["R-3451","R-3452","R-3453","R-3455","R-3457","R-3458","R-3459","R-3448"]])
L.wire("implementation-django-final.ttl", [("R-3460","delegatedTo",DR),("R-3461","delegatedTo",DR),("R-3461","enforcedBy",PS)])
L.wire("implementation-django-web-final.ttl", [("R-3462","delegatedTo",DR)])

# ═══ 9. ISSUED ═══════════════════════════════════════════════════════════════
L.issued([(f"R-34{n}", "rules/discipline-houserules-skill.ttl") for n in range(51, 60)] +
         [("R-3460","rules/implementation-django-final.ttl"),("R-3461","rules/implementation-django-final.ttl"),("R-3462","rules/implementation-django-web-final.ttl")])
print("piece1 ontology edit done — next: md seed(§18) → gate → render --apply 7 docs")
