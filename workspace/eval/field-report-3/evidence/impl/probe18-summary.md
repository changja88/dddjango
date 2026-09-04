# ④ 선행 검증 — §18 정본 예시 mypy strict · #646 origin 집합 · #647 면제 스텁 (2026-09-04 · 코디)

## 정본 예시 3변형 mypy strict(spring venv 2.3.1 · django-stubs 6.1.0 · cwd=격리 사본 · `--follow-imports=silent mp_probe_18`)

| 변형 | 파일(이 폴더) | mypy | 런타임 import(monkeypatch 없이) |
|---|---|---|---|
| 별칭(계획 §1.2 b2 · 실물 모델 `MediaModel`/`CharacterModel` 바인딩) | `canonical_admin.py` | **통과** | OK(`ParentAdmin.inlines == [ChildInline]`) |
| 직접 표기(monkeypatch 채택 시) | `direct_admin.py` | **통과** | `TypeError: type 'ModelForm' is not subscriptable`(예상대로) |
| `TYPE_CHECKING` 분기 안 중간 ClassDef(kkebi saju 모양) | `tc_class_admin.py` | **통과** | OK |

**수정 1건(계획 §7 리스크 1 해소)**: rv1-B §3.5 b2의 `_ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel, "ChildInlineForm"]`는 스텁 `InlineModelAdmin.formset: type[BaseInlineFormSet[_ChildModelT, _ParentModelT, ModelForm[_ChildModelT]]]`와 어긋나 `[assignment]` red → 셋째 인자 **생략**(`BaseInlineFormSet[ChildModel, ParentModel]` · 기본값 `ModelForm[_M]`). 무주석 admin 선언 속성(`model`·`form`·`formset`·`extra`·`readonly_fields`·`inlines`) 전부 통과 — R-3154 rev2 문안과 일치. `type ParentInlineFormSet = BaseInlineFormSet[Model, ParentModel, ModelForm[Model]]` bound 표기 통과(`Any` 0).

## #646 origin 집합(django-stubs 6.1.0 `.pyi` — 타입 매개변수에 기본값 없는 제네릭 기저만)

- `django.forms(.models)`: `BaseModelForm`·`ModelForm`(`_M`) · `BaseModelFormSet`(`_M, _ModelFormT` — 둘째는 default 있음 · 첫째 없음) · `BaseInlineFormSet`(`_M, _ParentM, _ModelFormT`) · `django.forms(.formsets)`: `BaseFormSet`(`_F` — bound BaseForm · default 없음).
- `django.contrib.admin(.options)`: `BaseModelAdmin`·`ModelAdmin`(`_ModelT`) · `InlineModelAdmin`·`StackedInline`·`TabularInline`(`_ChildModelT, _ParentModelT`).
- `django.views.generic(.detail/.list/.edit/.dates)`: `SingleObjectMixin`·`BaseDetailView`·`DetailView` · `MultipleObjectMixin`·`BaseListView`·`ListView` · `FormMixin`·`BaseFormView`·`FormView`(`_FormT`) · `ModelFormMixin`·`BaseCreateView`·`CreateView`·`BaseUpdateView`·`UpdateView`(`_M, _ModelFormT`) · `DeletionMixin`·`BaseDeleteView`·`DeleteView`(`_M, _FormT`) · dates 계열 `BaseDateListView`·`BaseArchiveIndexView`·`ArchiveIndexView`·`BaseYearArchiveView`·`YearArchiveView`·`BaseMonthArchiveView`·`MonthArchiveView`·`BaseWeekArchiveView`·`WeekArchiveView`·`BaseDayArchiveView`·`DayArchiveView`·`BaseTodayArchiveView`·`TodayArchiveView`·`BaseDateDetailView`·`DateDetailView`(`_M`).
- **제외**(default 있음): `View`(`_ViewResponse default=HttpResponseBase`) · `TemplateResponseMixin`·`TemplateView`(`_TemplateResponse default=HttpResponse`) · `RedirectView`(비제네릭) · `ProcessFormView`·`SingleObjectTemplateResponseMixin`·`MultipleObjectTemplateResponseMixin`(비제네릭).
- 계수: admin 5 + forms 5 + CBV 32 = **42 origin**. 현장 CBV 사용 0(⓪)이라 CBV 항은 예시 정정(django-web §2 · django §13.4)과 규칙 문면의 일관성용.

## #647 면제 스텁 근거

- `forms/forms.pyi:78 BaseForm.clean(self) -> dict[str, Any] | None` → `forms.Form`/`BaseForm` 하위 `clean() -> dict[str, object]` 면제(`| None` 포함 형도 면제). `forms/models.pyi:141 BaseModelForm.clean(self) -> None` → `ModelForm.clean`은 대상 아님(계획대로).
- `db/models/fields/__init__.pyi:199 Field.deconstruct -> tuple[str, str, Sequence[Any], dict[str, Any]]` → rv1-A MINOR(A-9)의 `deconstruct` 면제(kkebi 1) — `dict[str, object]`로 쓰면 mypy 호환·#647 nested 반환 object 차단 대상 → **면제 표에 `{deconstruct: {Field}}` 추가**(계획 v2 Δ).
