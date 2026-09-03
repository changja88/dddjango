# 현장 보고 — django-stubs 제네릭 기저(admin·form) 처리 규칙 부재 (2026-09-04)

작성: spring_dream_server 발주자 세션(Claude). 대상: dddjango 플러그인 v2.17.16 (`~/.claude/plugins/cache/changja88-dddjango/dddjango/2.17.16`).
계기: mypy 빚 상환(훅 범위 `uv run mypy application framework spring_dream_server` 152건) 중 fortune_character admin 26건 + notification admin 2건을 수리하기 전에 «플러그인이 만든 모양인지» 먼저 추적했다. 같은 문제를 레인 10개가 세 가지로 다르게 풀었고, 플러그인에는 이 문제를 다루는 문면이 한 줄도 없다.
관계: `2026-09-03-field-report-spring-dream-typecheck.md`의 후속이다. 그 보고서에서 **B(G2 mypy 게이트)는 사용자 결정으로 기각 확정**(게이트는 프로젝트 소유 · 플러그인은 «생성 코드가 mypy strict·ruff와 충돌하지 않게 설계» 원칙만 소유 = R-20)됐으므로, 이 문서는 게이트를 다시 제안하지 않고 **R-20 원칙 아래의 문면 규칙 결손 1건**만 제보한다. 앞 보고서의 항목 문자(A~H)와 겹치지 않게 별도 번호를 쓴다.

## 요약 · 위임 추적표 (dddjango 소유자용)

| # | 결함 | 증거 규모 | 고칠 곳(플러그인) | 수정 종류 | 실현 가능성 · 규모 | 상태 |
|---|---|---|---|---|---|---|
| S-1 | django-stubs가 제네릭으로 선언한 Django 기저(`ModelForm`·`ModelAdmin`·`TabularInline`/`StackedInline`·`BaseInlineFormSet`)를 **런타임은 subscript 못 한다**는 사실과 표준 처방(`TYPE_CHECKING` 별칭)이 플러그인 어디에도 없다 → 레인마다 다른 모양(맨몸 → mypy red / `# type: ignore[type-arg]` → 빚 은폐 / `TYPE_CHECKING` 별칭 → 정답) | BC 10개 · admin 클래스 40개: 맨몸 14(fortune_character, mypy 26건) · ignore 17(+속성 1줄, 8 BC) · 별칭 9(service_policy) | `implementation-django`(admin 절 신설) 또는 `implementation-django-web` §6 web form 절 + `discipline-houserules` §4 근처 한 문단 | 문면(정본 예시 포함) | **가능 · 소**: 예시 코드 1벌 + 문장 3개. 검사기 불요(프로젝트 mypy가 잡음) | 미착수 |
| S-2 (선택) | Django 기저 `# type: ignore[type-arg]` 부착이 «통과»로 보여 8개 BC가 같은 방식으로 빚을 숨겼다 — 문면만으로는 다음 레인이 또 붙일 수 있다 | 17클래스 + 속성 1줄 | `scripts/check-public-surface-annotation.py`(#493) 확장 또는 신규 규칙: 클래스 기저·`inlines` 주석에 `type: ignore[type-arg]` = 위반 | 검사기 | **가능 · 소~중**: AST에서 `ClassDef` 줄의 `# type: ignore[type-arg]` 주석만 보면 된다. E(«명시 `Any` 금지»)와 같은 판형이라 그 배치에 얹을 수 있다 | 사용자 결정 대기 |
| S-3 (발주측 소관 · 플러그인 아님) | fortune_character 빌드(8/30) lane-report가 mypy를 `spring_dream_server framework`에만 돌리고 «Success» — 자기 BC를 빼고 돌린 공허한 통과. 증분 fortune-character-2(9/2)도 같은 범위 | 레인 2회 | 없음. B 처분대로 발주서 G2 체크리스트가 소유(`uv run mypy --follow-imports=silent application/<bc>`) — 8/30 빌드는 체크리스트(9/3) 이전 | — | R-12 발주 가이드 1줄에 «최소 자기 BC 경로» 명시 여부만 확인 | 발주측 확인 |
| S-4 (**사용자 결정 2026-09-04: 무조건 · 최대 타입 강제**) | 딕셔너리를 레코드(키 고정·이질 값)로 쓰는 모양을 플러그인이 만든다 — `dict/Mapping[str, object\|Any]` 주석이 비테스트 **1,110줄**(RAG 런타임 828 · 레인 BC 281). 값이 `object`로 뭉개져 사용 지점마다 `int(object)`·`object.get` 등 mypy red(P1 61건 + P2 9건) 또는 `Any`로 검사 소멸 | 1,110줄 · mypy 70건 | `discipline-houserules` §4 + `implementation-python`(TypedDict·pydantic 경계 파싱) + `architecture-ddd`(DTO/VO) 문면 · 검사기: 주석 `(dict\|Mapping)[…, object\|Any]` 위반 + `json.load(s)` 결과 무파싱 사용 | 문면 + 검사기 | **가능 · 중**: 주석 검사는 E(«명시 `Any` 금지»)와 같은 판형이라 그 배치에 얹는다. legacy 1,110줄은 앵커 차분으로 격리 | 미착수 |
| S-5 | ninja 컨트롤러 반환 주석 `Status[A] \| Status[B]`(상자 둘)와 오류 응답 `response=` base 뭉뚱그림, 200 discriminated union의 `Schema`+`RootModel` 다중 상속을 문면이 막지 않고 검사기도 안 잡는다 — `Status` 불변성·메타클래스 충돌로 mypy strict red(P5 9건) | 리딩 BC 1개 · 9건(컨트롤러 5 · 스키마 2 · 파생 2) | `implementation-django-ninja` 문면 2문장 + 정본 예시 · `scripts/check-api-error-controller-contract.py` 규칙 (a)(b)(c) | 문면 + 검사기 | **가능 · 소** — AST 바인딩만으로 판정, 최소 수리 실측 완료(OpenAPI 바이트 불변) | 미착수 |

상태 열은 dddjango 소유자가 갱신한다.

## 판단 기준 적용 (앞 보고서 «수정 우선순위 · 판단 기준» 4번)

- «플러그인이 만든 모양이면 문면 수정»: 맨몸 `forms.ModelForm`은 플러그인 Django 스킬의 예시 모양 그대로다(§원인). → **S-1 문면 필수**.
- «검사가 못 잡는데 레인 두 곳 이상에서 반복되면 문면 후보»: `# type: ignore[type-arg]`는 mypy가 못 잡고 8개 BC에서 반복됐다. → S-1 문면에 «금지» 문장 + S-2 검사기는 선택.
- 게이트(실행·차단)는 프로젝트 소유(B 기각) → 이 문서는 게이트를 제안하지 않는다. S-3은 발주측 기록용이다.

## 환경

- Django 6.1 · django-stubs 6.1.0 · mypy 2.3.1 · Python 3.14.7. 프로젝트 mypy는 `strict = true`(→ `disallow_any_generics` = `[type-arg]` 활성) · plugin `mypy_django_plugin.main` · `enable_error_code`에 `ignore-without-code`(→ 레인이 `# type: ignore[type-arg]`처럼 코드를 붙이면 통과). 설정은 2026-08-26 `4eaf960`부터로, 문제의 빌드(8/30)보다 앞선다 — 설정 변경 탓이 아니다.
- `django_stubs_ext.monkeypatch()`는 프로젝트가 쓰지 않는다(`grep django_stubs_ext application framework spring_dream_server pyproject.toml` → 0).
- django-stubs 선언(`django-stubs/forms/models.pyi`, `contrib/admin/options.pyi`):
  - `class ModelForm(BaseModelForm[_M], ...)` · `class BaseInlineFormSet(BaseModelFormSet[_M, _ModelFormT], Generic[_M, _ParentM, _ModelFormT])`(`_ModelFormT` 기본값 `ModelForm[_M]`)
  - `class ModelAdmin(BaseModelAdmin[_ModelT])` · `class TabularInline(InlineModelAdmin[_ChildModelT, _ParentModelT])`
  - `ModelAdmin.save_model(self, request, obj: _ModelT, form: Any, change: Any)` — 오버라이드에서 `form: ModelForm[Model]`로 좁혀도 된다.
  - `InlineModelAdmin.form: type[forms.ModelForm[_ChildModelT]]` · `.formset: type[BaseInlineFormSet[_ChildModelT, _ParentModelT, forms.ModelForm[_ChildModelT]]]` · `.extra: int` · `.model: type[_ChildModelT]`

## 증상

### mypy (훅 범위 152건 중 admin 28건)

fortune_character 26건 — 전부 `[type-arg] Missing type arguments for generic type "ModelForm" | "ModelAdmin" | "TabularInline" | "BaseInlineFormSet"`:

| 파일(`application/fortune_character/driven_layer/django_fortune_character/admin/`) | 건수 |
|---|---|
| `character/panel.py` | 8 (TabularInline 5 · ModelForm 2 · BaseInlineFormSet 1) |
| `character/feature/character_writer.py` | 7 (함수 시그니처의 `ModelForm`·`BaseInlineFormSet`) |
| `media_inline_form.py` · `media_kind/panel.py` · `prompt_set/panel.py` | 각 2 |
| `discount_rule_inline_form.py` · `operating_hours_rule_inline_form.py` · `work_reference_inline_form.py` · `media_kind_form.py` · `prompt_set_form.py` | 각 1 |

notification 2건(`admin/email_notice_template/panel.py:79-80`)은 별개 원인이다 — `obj: EmailNoticeTemplateModel`(non-Optional)에 `if obj is None or obj.pk is None`을 써서 `[redundant-expr]`+`[unreachable]`. 앞 보고서 A(선언 타입 재검사 · R-3443)의 admin 변종이라 새 항목으로 세우지 않는다(부록 참조).

### 런타임 — 맨몸에 타입 인자를 «그냥 붙이면» Django가 죽는다

발주자가 첫 시도에서 `class PromptSetForm(forms.ModelForm[PromptSetModel])`·모듈 수준 `BaseInlineFormSet[Any, CharacterModel, Any]`로 고쳤더니 `django.setup()`이 `TypeError: type 'BaseInlineFormSet' is not subscriptable`로 실패했고, 그 결과 mypy_django_plugin까지 «Error constructing plugin instance of NewSemanalDjangoPlugin»으로 죽어 mypy 전체가 INTERNAL ERROR가 됐다. 재현:

```
$ uv run python -c "from django import forms; from django.contrib import admin
for n,c in [('ModelForm',forms.ModelForm),('BaseInlineFormSet',forms.BaseInlineFormSet),('ModelAdmin',admin.ModelAdmin),('TabularInline',admin.TabularInline)]:
    try: c[int]
    except TypeError as e: print(n,'->',e)"
ModelForm -> type 'ModelForm' is not subscriptable
BaseInlineFormSet -> type 'BaseInlineFormSet' is not subscriptable
ModelAdmin -> type 'ModelAdmin' is not subscriptable
TabularInline -> type 'TabularInline' is not subscriptable
```

즉 이 문제는 «타입 인자를 빠뜨렸다»가 아니라 «stubs와 런타임이 다르다»는 지식이 필요한 문제다. 규칙 없이 mypy 메시지만 따라가면 레인은 런타임을 깨뜨리거나(위) `# type: ignore`로 도망간다.

## 실측 — 레인 10개가 같은 문제를 세 가지로 풀었다

| 처리 | BC(생성 커밋) | 클래스 | mypy | 비고 |
|---|---|---|---|---|
| ① 아무 처리 없음 `class X(forms.ModelForm):` | fortune_character(8/30 `af97086` S5 admin) | 14 | **red 26** | lane-report는 mypy `spring_dream_server framework` Success — 자기 BC 미포함(S-3) |
| ② `class X(admin.ModelAdmin):  # type: ignore[type-arg]` | accounts(3, 그중 `inlines` 속성 1줄)·fortune_intent(4)·wallet(3)·media_library(2)·notification(2)·query_translation(2)·fortune_record(1)·promotion campaign_usage(1) | 17 + 1줄 | 통과 | 빚 은폐. `ignore-without-code`는 만족 |
| ③ `if TYPE_CHECKING: _ModelFormBase: TypeAlias = forms.ModelForm[Model]  # noqa: UP040 … else: _ModelFormBase: type[forms.ModelForm] = forms.ModelForm` → `class X(_ModelFormBase):` | service_policy(8/30 `b2a2bf6` S4 admin 5화면) | 9 | 통과 | 정답. 이 레인만 자기 BC에 mypy를 돌렸고(REPORT 14행 «mypy application/service_policy: Success(strict)») 처방을 스스로 찾았다 |

①·③이 **같은 날(8/30)** 두 레인에서 나왔다. 플러그인 문면이 정하지 않으니 결과는 레인 운에 달렸다.

(별개: parler `TranslatableAdmin`·`TranslatableModelForm`은 서드파티 미타입이라 `# type: ignore[misc]`가 정당하다 — fortune_character·promotion·product 6곳. 이 문서 범위 밖.)

## 원인 — 플러그인 문면

```
$ cd ~/.claude/plugins/cache/changja88-dddjango/dddjango/2.17.16
$ grep -rn -E 'django-stubs|django_stubs|ModelForm\[|ModelAdmin\[|type-arg|_ModelFormBase|_ModelAdminBase' --include='*.md' --include='*.py' --include='*.json' . | grep -v CHANGELOG
skills/discipline-houserules/SKILL.md:91:  표준 도구셋(… mypy strict·django-stubs …)은 기능 추가 흐름이 직접 다룬다   ← 도구 이름만
scripts/design_pregate.py:1215, 1523                                            ← TYPE_CHECKING 가드를 «최상위 바인딩»으로 세는 pre-gate 파서 — 규칙 아님
```

- `implementation-django/references/final.md:725` — «웹 폼(Form/ModelForm …)은 표현 계층이므로 `implementation-django-web` §6이 소유». admin 절은 없다.
- `implementation-django-web/references/final.md:177, 207` — ModelForm 지침은 «`Meta.fields`를 명시적으로 나열» 뿐. 예시는 `class ArticleForm(forms.ModelForm):` 맨몸 — ①의 모양이 곧 플러그인 예시 모양이다.
- `discipline-houserules` §4 «모든 이름에 타입»은 있으나 «제네릭 기저의 타입 인자»와 «런타임 subscript 불가»는 없다. `type: ignore` 사용 규칙도 없다.
- 검사기 27종 어디에도 `type: ignore` 부착을 보는 규칙이 없다(플러그인 자기 코드의 ignore 6줄만 검색됨).

## 제안

### S-1. 문면 — «django-stubs 제네릭 기저» 규칙 + 정본 예시 (필수)

배치 후보: `implementation-django`에 «Django admin·ModelForm 타이핑» 절 신설(admin은 web form과 달리 driven_layer 저작 화면이라 django-web보다 django 코어 스킬이 맞다). `discipline-houserules` §4에는 한 문장으로 참조만.

문장 3개:
1. django-stubs는 `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)을 제네릭으로 선언하지만 **런타임 클래스는 subscript 불가**다. 기저에 직접 `X[Model]`을 쓰면 import 시 `TypeError`다.
2. 기저 클래스로 쓰는 별칭은 `if TYPE_CHECKING:` 분기에 `TypeAlias`로 두고(`# noqa: UP040` — 기저로 쓰이므로 `type` 문이 될 수 없다), `else:`에 런타임 클래스를 같은 이름으로 둔다. **주석(annotation)에만 쓰는 별칭은 `type` 문**(PEP 695 · 지연 평가라 런타임 안전)으로 쓴다.
3. Django 기저에 `# type: ignore[type-arg]`를 붙이지 않는다 — 통과가 아니라 은폐다.

정본 예시(spring_dream_server service_policy 실물 `admin/limit_rule/form/limit_rule_form.py`·`admin/limit_rule/panel.py`를 일반화. #493 «첫 대입 타입» 규율과 함께 완결되는 모양):

```python
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias

from django import forms
from django.contrib import admin
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

if TYPE_CHECKING:
    _ModelFormBase: TypeAlias = forms.ModelForm[ChildModel]  # noqa: UP040 -- 기저 클래스로 쓰는 별칭이라 `type` 문(TypeAliasType)이 될 수 없다
    _InlineFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel]  # noqa: UP040
    _InlineBase: TypeAlias = admin.TabularInline[ChildModel, ParentModel]  # noqa: UP040
    _ModelAdminBase: TypeAlias = admin.ModelAdmin[ParentModel]  # noqa: UP040
else:
    # 런타임 ModelForm·BaseInlineFormSet·TabularInline·ModelAdmin 은 제네릭이 아니다 — 타입 인자는 django-stubs 전용(TYPE_CHECKING)
    _ModelFormBase: type[forms.ModelForm] = forms.ModelForm
    _InlineFormSetBase: type[BaseInlineFormSet] = BaseInlineFormSet
    _InlineBase: type[admin.TabularInline] = admin.TabularInline
    _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin

# 주석 전용 별칭(여러 자식 모델의 인라인 formset이 한 목록에 섞일 때) — `type` 문은 지연 평가라 런타임 안전
type ParentInlineFormSet = BaseInlineFormSet[Any, ParentModel, Any]


class ChildInlineForm(_ModelFormBase):
    class Meta:
        model = ChildModel
        fields = ("field_a", "field_b")


class ChildInlineFormSet(_InlineFormSetBase):
    def clean(self) -> None: ...


class ChildInline(_InlineBase):
    model: type[ChildModel] = ChildModel
    form: type[ChildInlineForm] = ChildInlineForm
    formset: type[ChildInlineFormSet] = ChildInlineFormSet
    extra: int = 0


@admin.register(ParentModel)
class ParentAdmin(_ModelAdminBase):
    form: type[ParentForm] = ParentForm
    readonly_fields: ClassVar[tuple[str, ...]] = ("version",)
    inlines: ClassVar[list[type[admin.TabularInline[Any, ParentModel]]]] = [ChildInline]

    def save_model(self, request: HttpRequest, obj: ParentModel, form: ModelForm[ParentModel], change: bool) -> None: ...

    def save_related(self, request: HttpRequest, form: ModelForm[ParentModel], formsets: list[ParentInlineFormSet], change: bool) -> None: ...
```

- 인라인 자식 모델이 여럿이면 `inlines`·`formsets`의 자식 인자는 `Any`다(`_M`이 invariant라 `Model`로 못 묶는다) — E(«명시 `Any` 금지») 규범을 세울 때 이 자리는 «프레임워크 미러 조건부 허용»으로 빼야 한다.
- 대안 `django_stubs_ext.monkeypatch()`(런타임 클래스에 `__class_getitem__` 주입)는 프로젝트 전역 런타임 패치라 플러그인이 강제할 사항이 아니다. 별칭 방식은 의존성 0이라 기본값으로 적합하다. 프로젝트가 monkeypatch를 채택했으면 별칭 없이 `X[Model]` 직접 표기가 맞다 — 문면에 «프로젝트 settings/`manage.py`에 `django_stubs_ext.monkeypatch()`가 있으면 직접 표기» 한 줄을 조건으로 둔다.

### S-2. 검사기 (선택 · 사용자 결정)

`ClassDef` 헤더 줄과 `inlines` 첫 대입 줄의 `# type: ignore[type-arg]`를 위반으로 계수. 픽스처 good 1(별칭)/bad 2(맨몸은 mypy 몫이므로 제외 · ignore 부착만). E 배치와 같은 판형(문면+검사기)이므로 E 착수 시 함께 넣는 편이 싸다. 문면만으로 충분하다고 보면 기각해도 된다 — 프로젝트 mypy는 ①을 잡고, ②는 발주자 G2 체크리스트의 `grep -rn 'type: ignore\[type-arg\]' application/<bc>` 1줄로 대신할 수 있다.

### S-3. 발주측 (플러그인 아님)

발주서 G2 체크리스트의 mypy 명령은 이미 `--follow-imports=silent application/<bc>`다. R-12 발주 가이드 1줄에 «자기 BC 경로 필수 · `spring_dream_server framework`만 돌린 결과는 증거가 아니다»가 들어가는지만 확인한다.

## 부록 — notification 2건 (A/R-3443의 admin 변종)

`admin/email_notice_template/panel.py:79` `if obj is None or obj.pk is None:` — `obj: EmailNoticeTemplateModel`은 non-Optional이고 `pk`는 auto `int`(django-stubs가 non-Optional로 본다). 이 admin은 `has_add_permission → False`(change-only)라 미저장 인스턴스는 실제로도 오지 않는다. 처방은 선언 타입 재검사 제거(`obj is None` 삭제) 또는 Django 관용구 `obj._state.adding`이다. 앞 보고서 A의 «선언 타입을 코드로 재검사하지 않는다» 규범이 admin display 메서드에도 그대로 적용된다는 관측만 남긴다 — 새 항목 아님.

## 재현 명령 (spring_dream_server 루트 · main d2eaafe)

```
uv run mypy application framework spring_dream_server 2>&1 | grep -E 'fortune_character/.*admin|notification/.*admin'   # 28건
grep -rn -E 'type: ignore\[type-arg\]' --include='*.py' application | wc -l                                                # 18줄(17 클래스 + inlines 1)
grep -rn -E '^class \w+\(_Model(Form|Admin)Base\)' --include='*.py' application                                            # service_policy 9
sed -n 35,40p application/service_policy/driven_layer/django_service_policy/admin/limit_rule/panel.py                       # 정본 패턴 실물
```

## 발주측 처리 계획

- fortune_character 26건 + notification 2건은 플러그인 문면 반영을 기다리지 않고 **service_policy 패턴으로 직접 상환**한다(사용자 방침 «방향 정해진 건 직접 수정»). 검증: 훅 범위 mypy 152→124 · ruff check/format 0 · `registry_gate --anchor <main HEAD>` 귀속 0 · `make test`. (2026-09-04 초안에서 이 수치까지 확인했고 사용자 지시로 롤백 — 재적용 시 같은 결과가 기대된다. 단, 기저 클래스가 바뀌면 그 클래스의 옛 #493 «첫 대입 타입 없음» 위반이 legacy에서 귀속으로 바뀌므로 `model/form/formset/extra/readonly_fields` 주석을 같은 커밋에서 붙여야 귀속 0이 된다.)
- `# type: ignore[type-arg]` 18줄(8 BC)은 mypy 152건 밖이라 이번 상환 범위에 넣지 않는다. S-1/S-2 처분이 정해지면 한 번에 정리한다.
- 앞으로 발주서 G2 체크리스트에 `grep -rn 'type: ignore\[type-arg\]' application/<bc>` 0 조건을 추가할지는 S-2 처분과 함께 결정한다.

## S-4. 딕셔너리-레코드 금지 · `TypedDict`/pydantic 강제 (사용자 결정 2026-09-04 «무조건 · 최대한 타입을 강제»)

### 결정

발주자(사용자)가 P1 원인을 듣고 내린 결정: **레코드 모양의 딕셔너리 사용을 플러그인 차원에서 금지하고 `TypedDict`(내부 신뢰 데이터)·pydantic(외부 입력 검증 파싱)·dataclass/값 객체(도메인)를 강제한다.** 「최대한 타입을 강제」가 기준이다. 발주자 세션이 "조회표는 예외" 완화를 제안했으나 사용자가 «무조건»으로 재확인했다 — 아래 규칙은 그 결정을 기술적으로 표현 가능한 최대치로 옮긴 것이다(`TypedDict`는 키 고정 구조만 표현하므로 키가 데이터인 조회표는 «값 타입 구체 강제»가 상한이다).

### 증상 · 규모 (spring_dream_server main `c20f525`)

- mypy: P1 61건 + P2 9건 = **70건**(훅 범위 124건의 56%). 대표: `rag_builder/source_adapter.py:19` `SourceBlock.coordinate: Mapping[str, object]` → `coordinates.py`에서 `int(first["page_id"])` 11곳 `[call-overload]`, `cli.py` `"object" has no attribute "rag_id"` 10곳, `service_runtime.py` `object` 인덱스 6곳, `dict[str, object]` → rfc8785 `_Value` 6곳.
- 주석 규모(비테스트): `grep -rnE '(dict|Mapping)\[str, (object|Any)\]' framework application | grep -v /test/` → **1,110줄**. 분포: `framework/technology/rag` 828 · **레인 BC 281**(fortune_reading 59 · llm_access 48 · chat_relay 35 · fortune_character 27 · fortune_calculation 24 · promotion 16 · fortune_catalog 14 · query_translation 11 · fortune_record 10 …). BC 281줄은 dddjango 레인 산출물이므로 플러그인이 만드는 모양이다.
- 좌표 레코드의 실물 종류: `coordinates.py::_STRUCTURE_VALIDATORS` 6종 — `shidian_authorized_paragraph`·`shidian_authorized_paragraph_range`·`wikisource_fixed_revision_span`·`wikisource_fixed_revision_span_set`·`standard_intake_block`·`standard_intake_block_range`. 종류마다 필수 키가 다르다(`page_numbers`·`start_offset/end_offset`·`spans`·`block_id`·`start_block_id/end_block_id`).

### 원인 — 플러그인 문면

- 플러그인 2.17.16에서 `TypedDict`는 `implementation-python/references/final.md` §1.5 한 절(5줄)뿐이다 — «외부 API, JSON 등 이종 데이터를 담는 딕셔너리에는 TypedDict를 사용하라»는 **권고**이고, 하우스룰(`discipline-houserules`)·에이전트 프롬프트·검사기 어디에도 강제가 없다. 반대로 `architecture-ddd/references/final.md:1614`의 도메인 예시 `FormInstance.values: dict[str, Any]`는 스킬 문면 중 유일한 `dict[str, Any]` 예시다 — 권고 한 절 대 예시 한 줄이면 레인은 예시 쪽을 따른다(BC 281줄이 그 증거). «외부 JSON은 경계에서 검증 파싱한다»는 규칙은 없다.
- `discipline-houserules` §4 «모든 이름에 타입»은 `Mapping[str, object]`로 충족된다 — `object`는 타입이지만 정보가 0이다. E(«명시 `Any` 금지»)만으로는 레인이 `Any` 대신 `object`로 옮겨 가는 것(현재 RAG 런타임의 모양)을 막지 못한다.

### 규칙 (문면) — 한 줄 규칙 + 결정표 (사용자 확정 2026-09-04)

**모든 JSON은 입구에서 `TypedDict`로 받는다. 받은 뒤 `object`·`Any`·`dict[str, …]`로 흘리지 않는다.**

붙임 2 · 예외 1:
1. 외부에서 온 JSON(파일·HTTP·타 시스템)은 **검증하며** 받는다 — `pydantic.TypeAdapter(그TypedDict).validate_json/validate_python`. `TypedDict`는 선언일 뿐 실행 시 검사가 없으므로 검증만 얹는다. 우리 코드가 만든 내부 JSON은 검증 없이 `TypedDict`.
2. 키가 데이터인 JSON(조회표)은 `dict[str, 그TypedDict]` — 값 쪽을 `TypedDict`로 잡는다.
- 예외: 구조를 정하지 않고 그대로 저장·전달하는 임의 JSON만 재귀 별칭 `type JsonValue = bool | int | float | str | None | list[JsonValue] | dict[str, JsonValue]`. `object`·`Any`가 아니라 이름 붙은 타입이다.

레인이 바로 고르게 하는 결정표(문면 정본 후보):

| 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |
|---|---|---|---|
| 키가 정해진 값 묶음(레코드) | 우리 코드가 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `Literal` 판별 키로 union) | `dict[str, object\|Any]` |
| 키가 정해진 값 묶음 | 외부(파일 `json.load`·HTTP body·타 시스템) | `TypeAdapter(TypedDict)`·pydantic 모델로 **검증 파싱**. 파싱 전 값 사용 금지 | 검증 없는 `TypedDict`, `Any` 흘리기 |
| 도메인 개념 | 도메인 계층 | dataclass·값 객체 | 딕셔너리 |
| 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]`에 K·V 구체 타입(V가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |
| 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue` | `dict[str, object]`, `Any` |
| 타입이 이미 있는 값 | 함수 반환·매개변수 | 실제 클래스(`BuildPlan` 등) | 자리표시 `object` |

### 검사기 (제안)

- (a) 주석 스캔: 함수 시그니처·변수·클래스 속성 주석에서 `(dict|Mapping|MutableMapping)[…, (object|Any)]` = 위반. AST `Subscript`만 보면 되고 오탐이 거의 없다. E의 «명시 `Any`» 검사와 같은 배치·같은 판형.
- (b) `json.load(s)` 호출 결과가 pydantic `model_validate`/`TypeAdapter`/명시 파서 함수를 거치지 않고 대입·반환되는 자리 = 위반(1레인 실측 뒤 오탐률 확인).
- legacy 1,110줄은 registry_gate 앵커 차분(N∖L)으로 격리된다 — 새 레인 산출물만 막힌다.

### 발주측 처리 계획

- P1 61건은 이 규칙대로 ⑤(좌표 `TypedDict` 6종 + `SourceBlock.coordinate`를 그 union으로)와 나머지 지점의 구체 타입화로 상환한다(대장 `docs/superpowers/plans/2026-09-04-mypy-debt-ledger.md` P1). 도우미 `as_int` 방식(④)은 채택하지 않는다.
- mypy가 잡지 않는 나머지 1,040줄(`Any` 값 매핑 등)은 이번 상환 범위 밖 — 규칙 확정 뒤 RAG 런타임 타이핑 발주 후보.

## S-5. ninja `Status` 반환 주석 형태 · 오류 응답 base 뭉뚱그림 · 200 discriminated union의 `Schema`+`RootModel` 다중 상속 (mypy 대장 P5 · 2026-09-04)

### 증상 (spring_dream_server main `f5ee428` · mypy 2.3.1 strict · 리딩 BC 16행 산출물)

- `application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py:164` 반환 주석 `-> Status[EvidenceProvisionResponseSchema] | Status[_FortuneReadingErrorSchema]` + 본문 `return Status(400, _InvalidRequestErrorSchema())` 등 5곳 → `[return-value] got "Status[InvalidRequestErrorSchema]", expected "Status[EvidenceProvisionResponseSchema] | Status[FortuneReadingErrorSchema]"` **5건**. 원인은 `ninja.Status(Generic[T])`의 `T = TypeVar("T")`(불변) — `Status[하위]`는 `Status[기저]`의 하위 타입이 아니다. 같은 컨트롤러의 `response={200: …, 400: _FortuneReadingErrorSchema, 503: _FortuneReadingErrorSchema}`는 2026-08-25 개정 규칙(«base로 뭉뚱그려 선언하지 않는다»)과도 어긋나며 리딩 e2e(`test_evidence_openapi.py`)가 그 모양(`$ref …/FortuneReadingErrorSchema`, 400==503)을 동결 단언으로 고정했다.
- `…/schema/schema_out.py:151` `class EvidenceProvisionResponseSchema(_Schema, _RootModel[_EvidenceProvision])`(200 discriminated union) → `[metaclass] Metaclass conflict`(ninja `Schema`는 `metaclass=ResolverMetaclass`, `RootModel`은 pydantic `ModelMetaclass`) + `[no-untyped-call] __init_subclass__` **2건** · 파생 `[call-arg] Unexpected keyword argument "root"` 컨트롤러 71·122 **2건**. 런타임은 정상.

### 실측 (발주자 · 스크래치 mypy·ninja OpenAPI)

- 형태별 mypy: `-> Status[Resp] | Status[Base]` + `Status(400, Concrete())` → **오류** · `-> Status[Resp | Base]`(상자 하나) → 통과(반환 문맥으로 `T` 추론) · `-> Status[Resp | C1 | C2 | C3 | C4]`(교리 예시 형태) → 통과 · 값 변수를 `e: Base = Concrete()`로 선언 → 통과.
- `_Schema` 기저를 빼고 `class X(RootModel[Annotated[A | B, Field(discriminator="kind")]])`만 두면 mypy 통과 + `root=` 파생 2건 해소, OpenAPI 200 컴포넌트 6개 바이트 동일(sha256 `83b8f70c…` 동일). RootModel까지 없애고 `response={200: A | B}`로 쓰면 이름 붙은 컴포넌트가 사라지고 익명 `anyOf`(title "Response")로 렌더되며 discriminator 표기를 잃는다 — 계약 변경.
- 오류 응답을 교리대로 `response={400: InvalidRequest, 503: RegistryMismatch | Temporary | ResourceLimit}`로 바꾸면 OpenAPI가 400 concrete `$ref`, 503 `anyOf` 3개로 바뀐다 — e2e 단언 2개 변경(OpenAPI 문서 변경 승인 사안).

### 원인 — 플러그인 문면·검사기

- `implementation-django-ninja/references/final.md`는 `-> Status[OrderOut | ErrA | ErrB]`(184) · `-> OrderOut | Status[Err]`(677·727·777)를 **예시로만** 보여 주고, 산문에 «반환 주석은 `Status` 하나에 union을 넣는다 / `Status[A] | Status[B]`는 불변성 때문에 금지»라는 규칙이 없다(`grep "반환 주석"` 0). 레인은 예시를 «`A | B` 형태면 된다»로 읽어 상자 둘로 썼다.
- 200 discriminated union 응답(성공이 두 모양 이상)에 대한 문면이 없다 — `RootModel` 언급 0(`grep -rn RootModel skills/` = architecture-ddd 이벤트 봉투 `Annotated[Union, Field(discriminator)]` 1곳뿐). 레인이 «ninja 응답은 `Schema`여야 한다»는 직관으로 `Schema`+`RootModel` 다중 상속을 만들었다.
- `scripts/check-api-error-controller-contract.py`는 `ninja.Status` 바인딩(`NINJA_STATUS`)과 반환 주석(`node.returns`, `BitOr`/`Subscript`)을 읽지만 (a) `Status[…]` 항이 둘 이상인 주석, (b) `response=`의 값이 같은 `bc_error_schema.py` 안에 하위 클래스를 가진 base인 경우를 위반으로 내지 않는다 — 리딩 16행 G2에서 이 검사기 0건(`.dddjango/20260831-2331-fortune-reading/`). 플러그인은 mypy를 돌리지 않으므로(S-3) 이 두 형태는 검사기 없이는 잡히지 않는다.

### 제안

- 문면(필수): implementation-django-ninja에 두 문장 추가 — «컨트롤러 반환 주석은 `Status` **하나**에 성공·오류 타입 union을 넣는다(`-> Status[Out | ErrA | ErrB]`). `Status[A] | Status[B]`는 `Status`가 불변이라 concrete 반환이 mypy strict에서 막히므로 금지.» · «성공 응답이 판별 키로 갈리는 union이면 `class XResponseSchema(RootModel[Annotated[A | B, Field(discriminator="kind")]])`로 두고 `Schema`를 함께 상속하지 않는다(메타클래스 충돌). `response={200: A | B}` 익명 union은 discriminator 표기를 잃으므로 쓰지 않는다.» 정본 예시에 두 형태를 각각 1개씩.
- 검사기(제안·`check-api-error-controller-contract.py` 확장): (a) 반환 주석에 `ninja.Status` Subscript가 2개 이상 → 위반 «반환 주석의 `Status`는 하나» · (b) `response=` 값이 `bc_error_schema.py`에서 하위 클래스를 가진 base → 위반 «base 뭉뚱그림(2026-08-25)» · (c) `schema_out.py` 클래스가 `ninja.Schema`와 `pydantic.RootModel`을 함께 상속 → 위반. 셋 다 AST 바인딩만으로 판정 가능.

### 발주측 처리 계획

- P5 9건은 최소형으로 상환 후보: 반환 주석 1줄 `-> Status[EvidenceProvisionResponseSchema | _FortuneReadingErrorSchema]` + `_Schema` 기저 제거 1줄(OpenAPI 바이트 불변 실측). 교리 정렬(오류 응답 concrete 선언 + e2e 단언 2개 개정)은 OpenAPI 문서 변경 승인이 필요한 별도 결정.
