# S-1 ⓪ 실측 — django-stubs 제네릭 기저 처리 규칙 부재 (2026-09-04)

조사자: 현장 보고 3 ⓪ 실측(S-1 전담). 결론이 아니라 «재실측 수치·좌표·어긋남»만 낸다.
원문: `workspace/plan/2026-09-04-field-report-spring-dream-django-stubs-generic-base.md` · 결정: `…-repair-3-issues.md` §2-A.

격리 사본(`$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`):
`$S/spring`(HEAD `7bfe1aa`) · `$S/spring-d2eaafe`(보고자 시점) · `$S/spring-c20f525` · `$S/spring-f5ee428` · `$S/kkebi`(HEAD `6608fb0`).
도구: spring venv Python 3.14.7 · Django 6.1 · mypy 2.3.1 · django-stubs 6.1.0 · django-stubs-ext 6.1.0(kkebi venv도 django-stubs 6.1.0).
스크립트(이 폴더 사본): `proto_646.py`(#646 시제품 · 해소기) · `inventory.py`(A/B 인벤토리 · proto 해소기 재사용) · `runtime_probe.py`(C).
큰 산출(실검사기 전체 출력 0.7MB×3)은 `$S/S1/check645-*.txt` 에만 둔다.

---

## ① 수치 대조표 — 보고자 vs 재실측

| 항목 | 보고자(원문 L) | 재실측 | 커밋 | 근거(명령·파일) |
|---|---|---|---|---|
| admin 기저 상속 클래스 합 | 40 (L11·L69~L73) | **39** | spring `d2eaafe` | `inventory.py --label spring-d2eaafe` → `inventory-spring-d2eaafe.md` |
| ① 맨몸 | 14 (fortune_character) | **13** (fortune_character · 10파일) | d2eaafe | 같은 파일 «파일별» 표 · 14번째는 parler `CharacterAdmin(TranslatableAdmin)`/`CharacterForm(TranslatableModelForm)` 로 추정(둘 다 `[misc]` · 기저 집합 밖) |
| ② `# type: ignore[type-arg]` 헤더 | 17 + 속성 1줄 · 8 BC | **17 + 속성 1줄(accounts panel.py:80) · 8 BC** ✓ | d2eaafe | 동일 · `type: ignore[type-arg]` 줄 합 18 ✓(L179) |
| ③ TYPE_CHECKING 별칭 | 9 (service_policy) | **9** ✓ | d2eaafe | 동일 |
| ④ 직접 subscript | (언급 없음) | 0 | d2eaafe | 동일 |
| BC 수 | 10 | **10** ✓ | d2eaafe | accounts·fortune_character·fortune_intent·fortune_record·media_library·notification·promotion·query_translation·service_policy·wallet |
| 기저별 | — | ModelAdmin 18 · ModelForm 15 · TabularInline 4 · StackedInline 1 · BaseInlineFormSet 1 | d2eaafe | `inventory-spring-d2eaafe.md` «기저별» |
| mypy `[type-arg]` fortune_character | 26 (L37~L46) | **26** ✓ (10파일 · 전 오류가 type-arg) | d2eaafe | `mypy-d2eaafe-fortune_character.txt` |
| parler `[misc]` admin/form | 6 (L77) | **6** ✓ (fortune_character 2·product 2·promotion 2) + 모델 3 + chat_relay 2 + 테스트 3 = 줄 합 14 | d2eaafe | `inventory-spring-d2eaafe.md` «misc 줄» |
| HEAD 모양 | (발주측 계획: service_policy 패턴으로 상환 L186) | ① 0 · ② 17 · **③ 22**(fortune_character 13 + service_policy 9) · ④ 0 · mypy fortune_character **0** | spring `7bfe1aa` | `inventory-spring.md` · `mypy-HEAD-fortune_character.txt` · 커밋 `1288e4a` |
| c20f525 · f5ee428 | — | HEAD 와 동일(0/17/22/0 · type-arg 줄 18) | — | `$S/S1/inventory-spring-c20f525.md`·`-f5ee428.md` |
| kkebi | (범위 밖) | 67 클래스: ① 0 · ② 21(4 BC) · ③ 31(7 BC) · ④(TYPE_CHECKING 분기 안 중간 클래스) 15(saju) | kkebi `6608fb0` | `inventory-kkebi.md` |
| CBV 제네릭 상속 | (언급 없음) | **0** — application/·framework/·web/ 양 저장소 | 양 HEAD | §② B |
| `django_stubs_ext` 언급 | 0 (L28) | **0** (spring·kkebi · application/framework/settings/manage.py/pyproject) ✓ | 양 HEAD | `grep -rn django_stubs_ext` |

---

## ② 인벤토리

### A. admin·form 기저(`ModelForm`·`BaseModelForm`·`ModelAdmin`·`InlineModelAdmin`·`TabularInline`·`StackedInline`·`BaseInlineFormSet`·`BaseModelFormSet`) — `application/**` 전수(테스트 파일 포함 · 테스트 파일 적중 0)

**spring `d2eaafe`** (`inventory-spring-d2eaafe.md`)

| BC | ①bare | ②ignore | ③alias | ④direct | 합 |
|---|---|---|---|---|---|
| accounts | 0 | 2 (+속성 1줄) | 0 | 0 | 2 |
| fortune_character | 13 | 0 | 0 | 0 | 13 |
| fortune_intent | 0 | 4 | 0 | 0 | 4 |
| fortune_record | 0 | 1 | 0 | 0 | 1 |
| media_library | 0 | 2 | 0 | 0 | 2 |
| notification | 0 | 2 | 0 | 0 | 2 |
| promotion | 0 | 1 | 0 | 0 | 1 |
| query_translation | 0 | 2 | 0 | 0 | 2 |
| service_policy | 0 | 0 | 9 | 0 | 9 |
| wallet | 0 | 3 | 0 | 0 | 3 |
| **합** | **13** | **17** | **9** | **0** | **39** |

fortune_character ① 13 파일별: `admin/character/panel.py` 4(TabularInline×4) · `character/form/media_inline_form.py` 2(ModelForm·BaseInlineFormSet) · `discount_rule_inline_form.py`·`operating_hours_rule_inline_form.py`·`work_reference_inline_form.py`·`media_kind/form/media_kind_form.py`·`prompt_set/form/prompt_set_form.py` 각 1(ModelForm) · `media_kind/panel.py`·`prompt_set/panel.py` 각 1(ModelAdmin). (`CharacterAdmin(TranslatableAdmin)`·`CharacterForm(TranslatableModelForm)` 은 parler — 집합 밖.)

**spring HEAD `7bfe1aa`** (`inventory-spring.md`): ① 0 · ② 17(동일 8 BC · 동일 파일) · ③ 22 · ④ 0 · 속성 ignore 1줄(accounts panel.py:83) · `type-arg` 줄 합 18(불변).
발주측 수리 모양 = 커밋 `1288e4a` «admin django-stubs 제네릭 기저를 TYPE_CHECKING 별칭으로 — fortune_character 26·notification 2 상환(훅 범위 152→124)» — **③ 별칭(service_policy 패턴)** 로 통일 · monkeypatch 미도입 · 직접 표기 0 · 주석 전용 별칭은 `type CharacterInlineFormSet = BaseInlineFormSet[Any, CharacterModel, Any]`(character_writer.py:37) · «기저가 바뀐 클래스의 #493 첫 대입 주석(model·form·formset·extra·readonly_fields) 동일 커밋 처리» 명기. 11파일 +131/−47.

**kkebi HEAD `6608fb0`** (`inventory-kkebi.md`)

| BC | ①bare | ②ignore | ③alias | ④direct(TC 분기 안) | 합 |
|---|---|---|---|---|---|
| billing | 0 | 7 | 0 | 0 | 7 |
| consultation | 0 | 0 | 3 | 0 | 3 |
| daily | 0 | 0 | 3 | 0 | 3 |
| identity | 0 | 0 | 4 | 0 | 4 |
| image | 0 | 0 | 2 | 0 | 2 |
| notification | 0 | 0 | 3 | 0 | 3 |
| review | 0 | 0 | 1 | 0 | 1 |
| saju | 0 | 0 | 15 | 15 | 30 |
| share | 0 | 2 | 0 | 0 | 2 |
| tarot | 0 | 10 | 0 | 0 | 10 |
| top3 | 0 | 2 | 0 | 0 | 2 |
| **합** | **0** | **21** | **31** | **15** | **67** |

- 기저별 ModelAdmin 63 · ModelForm 3 · TabularInline 1. `type-arg` 줄 합 22 = 헤더 21 + admin 밖 1(`tarot/driving_layer/api/catalog/catalog_controller.py:101 … Query(None)  # type: ignore[type-arg]`). `[misc]` 18줄은 전부 test/(factories DjangoModelFactory 9 · frozen 재대입 9) — admin parler 0.
- **제3의 모양(saju 15)**: `if TYPE_CHECKING: class _BundleItemModelAdmin(admin.ModelAdmin[BundleItemModel]): pass` / `else: _BundleItemModelAdmin: type[admin.ModelAdmin] = admin.ModelAdmin` → `class BundleItemPanel(_BundleItemModelAdmin)`. 별칭이 `TypeAlias` 대입이 아니라 **TYPE_CHECKING 분기 안 중간 ClassDef** 다(mypy `application/saju` Success 593 files — `mypy-kkebi-saju.txt`). 표의 ④(TC) 15 = 그 중간 클래스 자체(런타임 미실행), ③ 15 = 그것을 상속한 실제 패널.
- consultation 등 ③ 16 은 spring 과 같은 `TypeAlias` 모양이되 else 분기가 무주석(`_X = admin.ModelAdmin`) — #493 실검사기 무발화(if 분기 첫 대입이 AnnAssign).

### B. CBV 제네릭(`DetailView`·`ListView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView`·`Base*`·`SingleObjectMixin`·`MultipleObjectMixin`·`FormMixin`·`ModelFormMixin`·`DeletionMixin`·dates 계열)

| 범위 | spring HEAD | kkebi HEAD | 명령 |
|---|---|---|---|
| `application/**` | 0 | 0 | `inventory.py` family=cbv |
| `framework/` | 0 | 0 | `inventory.py --subdir framework` |
| `web/`(kkebi · 239 .py · dddjango-web 산출) | — | 0 | `inventory.py --subdir web` |
| 저장소 전수 grep(`View`·`TemplateView`·`RedirectView` 포함) | 0 | 0 | `grep -rn -E 'class \w+\(.*\b(DetailView\|…\|View)\b'` |

→ CBV 로 범위를 넓힐 **현장 근거는 0**. 단 코퍼스에는 CBV 맨몸 예시 3줄이 있다(⑤). django-stubs 에서 `View`/`TemplateView`/`RedirectView` 는 `_ViewResponse` TypeVar 에 `default=HttpResponseBase` 가 있어(`views/generic/base.pyi:16`) 맨몸이 red 가 아니고, `_M`(detail/list/edit/dates)·`_FormT`·edit 의 `_ModelFormT` 는 default 없음 → `DetailView`·`ListView`·`FormView`·`CreateView[M, F]` 등은 맨몸이 `[type-arg]` red 다. 런타임은 전부 subscript 불가(③ 표).

---

## ③ 런타임 · monkeypatch 표 (`runtime_probe.py` · cwd=`$S/spring` · `DJANGO_SETTINGS_MODULE` 없이 · 결과 `runtime_probe.jsonl`)

| 클래스 | before `C[int]` | after `monkeypatch()` | own `__class_getitem__` | 상속 `__class_getitem__` | after `class X(C[int])` |
|---|---|---|---|---|---|
| `forms.ModelForm` | TypeError | 통과 | F | T(BaseModelForm) | 통과 |
| `forms.BaseModelForm` | TypeError | 통과 | T | F | 통과 |
| `forms.BaseInlineFormSet` | TypeError | 통과 | F | T(BaseModelFormSet) | 통과 |
| `forms.BaseModelFormSet` | TypeError | 통과 | T | T | 통과 |
| `admin.ModelAdmin` | TypeError | 통과 | T | T | 통과 |
| `admin.options.BaseModelAdmin` | TypeError | 통과 | T | F | 통과 |
| `admin.options.InlineModelAdmin` | TypeError | 통과 | F | T(BaseModelAdmin) | 통과 |
| `admin.TabularInline` / `StackedInline` | TypeError | 통과 | F | T | 통과 |
| `views.View` | TypeError | 통과 | T | F | 통과 |
| `TemplateView` / `RedirectView` | TypeError | 통과 | F | T(View) | 통과 |
| `DetailView` / `ListView` / `FormView` / `CreateView` / `UpdateView` / `DeleteView` / `ArchiveIndexView` | TypeError | 통과 | F | T | 통과 |
| `SingleObjectMixin` / `MultipleObjectMixin` / `FormMixin` | TypeError | 통과 | T | F | 통과 |
| `ModelFormMixin` | TypeError | 통과 | F | T | 통과 |

before 문면 전부 `type '<Name>' is not subscriptable`(보고자 L59~L62 와 동일 · 23종 전수). **monkeypatch 가 못 덮는 기저: 없음**(23/23).

패치 근거(`.venv/lib/python3.14/site-packages/django_stubs_ext/patch.py`): `_need_generic` 목록 L71~L115 — `ModelAdmin`(L72) · `BaseModelAdmin`(L77 → InlineModelAdmin/TabularInline/StackedInline 상속) · `BaseModelForm`(L81 → ModelForm) · `BaseModelFormSet`(L82 → BaseInlineFormSet) · `BaseFormSet`(L80) · `SingleObjectMixin`(L73)·`FormMixin`(L74)·`DeletionMixin`(L75)·`MultipleObjectMixin`(L76)·`View`(L96)·`TemplateResponseMixin`(L97). 주입은 L143 `el.cls.__class_getitem__ = classmethod(lambda cls, *args, **kwargs: cls)` — 반환이 `cls` 자체라 `class X(ModelForm[M])` 의 MRO 는 원본과 동일(③ 마지막 열 · `mp_probe_direct_admin.py` MRO 확인).

직접 표기 시제품(`synth/mp_probe_direct_admin.py` · 격리 사본 `$S/spring/mp_probe_s1/`): `django.setup()` 후 import → **monkeypatch 없이 `TypeError: type 'ModelForm' is not subscriptable`** · `django_stubs_ext.monkeypatch()` 선행 시 import OK + `ModelAdmin(...).get_urls()` 스모크 OK.

의존성 사실:
- `django-stubs-ext` 는 양 venv 에 6.1.0 설치 — 단 **`django-stubs[compatible-mypy]` 의 전이 의존성**(spring `uv.lock:484`)이고 `django-stubs` 는 `[dependency-groups] dev`(spring `pyproject.toml:41` · kkebi `:24` · 주석 «운영 배포는 uv sync --no-dev» L40). **`dependencies`(운영)에는 없다.**
- django-stubs README(`django_stubs-6.1.0.dist-info/METADATA` L206~L219): «`pip install django-stubs-ext  # as a production dependency`» + «place in your top-level settings: `import django_stubs_ext; django_stubs_ext.monkeypatch()`». `django.contrib.auth.forms` 제네릭은 `AppConfig.ready` 에서 별도 패치(L223~L240).
- 양 저장소 `django_stubs_ext` 언급 0.

---

## ④ mypy 재현

| 대상 | 명령(cwd=격리 사본) | 결과 | 파일 |
|---|---|---|---|
| spring d2eaafe `application/fortune_character` | `~/Desktop/spring_dream_server/.venv/bin/python -m mypy --follow-imports=silent application/fortune_character` | **Found 26 errors in 10 files** · `[type-arg]` 26(전 오류) · 6.7s | `mypy-d2eaafe-fortune_character.txt` |
| 〃 파일별 | — | `character/panel.py` 8(TabularInline 5·ModelForm 2·BaseInlineFormSet 1) · `feature/character_writer.py` 7(BaseInlineFormSet 4·ModelForm 3) · `media_inline_form.py` 2 · `media_kind/panel.py` 2 · `prompt_set/panel.py` 2 · `discount_rule…` `operating_hours…` `work_reference…` `media_kind_form` `prompt_set_form` 각 1 — **보고자 L41~L46 표와 완전 일치** | 〃 |
| spring HEAD `application/fortune_character` | 〃 | Success: no issues found in 264 source files · type-arg **0** | `mypy-HEAD-fortune_character.txt` |
| spring HEAD `application/service_policy` · `application/accounts` | 〃 | Success 277 / Success 250 | (stdout) |
| kkebi HEAD `application/saju`(TC 중간 클래스 모양) · `application/billing`(ignore 레인) | `~/Desktop/kkebi-server/.venv/bin/python -m mypy --follow-imports=silent …` | Success 593 / Success 623 | `mypy-kkebi-saju.txt` |
| 직접 표기 시제품 `mp_probe_s1/direct_admin.py`(spring pyproject strict) | 〃 | **1 error** — `inlines: ClassVar[list[type[admin.TabularInline[Any, CharacterModel]]]]` → `[assignment] … base class "ModelAdmin" defined the type as "list[type[InlineModelAdmin[Any, Any]]] \| tuple[type[InlineModelAdmin[Any, Any]], ...]"` · 그 외(ModelForm[M]·BaseInlineFormSet[C,P]·TabularInline[C,P]·ModelAdmin[P]·StackedInline·save_model 시그니처) 무오류 | `synth/mp_probe_direct_admin.py` |
| 별칭 기저 + `inlines` 변형 5종 `mp_probe_s1/alias_inlines.py` | 〃 | (R) 보고자 L153 그대로 `list[type[admin.TabularInline[Any, P]]]` → **red** · (1) `list[type[InlineModelAdmin[Any, Any]]]` → 통과 · (2) 무주석 `inlines = [X]` → 통과 · (3) `tuple[type[InlineModelAdmin[Any, Any]], ...]` → 통과 · (4) `Sequence[…]` → **red** | `synth/mp_probe_alias_inlines.py` |

HEAD `character/panel.py:103` 이 (R) 모양 그대로인데 통과하는 이유: `CharacterAdmin(TranslatableAdmin)` — 기저가 parler 미타입(`Any`)이라 오버라이드 호환을 검사하지 않는다. **타입 있는 기저(`_ModelAdminBase`·`admin.ModelAdmin[P]`) 아래에서는 보고자 정본 예시 L153 이 mypy strict red 다**(list 불변 · 스텁 선언 `contrib/admin/options.pyi` `inlines`).

---

## ⑤ 플러그인 문면 좌표 (file:line + 블록 IRI · IRI 접두 `<https://numchida.com/ns/djr#s/…>`)

| 좌표 | 내용 | 절 · 소유 | 블록 IRI |
|---|---|---|---|
| `dddjango/skills/implementation-django-web/references/final.md:208` | `class ArticleForm(forms.ModelForm):` (207 주석 «ModelForm: fields를 명시적으로 나열») | §6 Web forms(L169 · graph-owned L170) | `…/implementation-django-web/references/final.md/s007-6/b9`(kind-code) |
| 〃 `:177` | «`ModelForm.Meta.fields`는 명시적으로 나열한다» | §6 | `…/s007-6/b4`(kind-norm · R-2311 prefLabel) |
| 〃 `:66` | `class ArticleListView(ListView):` | §2 TemplateView/Generic CBV/FBV(L39 · graph-owned L40) | `…/s003-2/b10`(kind-code) |
| 〃 `:72` | `class ArticleCreateView(LoginRequiredMixin, CreateView):` | §2 | `…/s003-2/b10`(같은 펜스) |
| `dddjango/skills/implementation-django/references/final.md:1328` | `class EditArticleView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):` | §13.4 인증과 인가(L1314) — **산문(NAR)** · graph-owned 마커 없음 · LEDGER `implementation-django-final s065-13.4 … prose` · ttl 미수록 | **미확인(그래프 밖 · md 정본 → LEDGER 재기준선 대상)** |
| 〃 `:392` `:418` | `class OrderView(View):` `class OrderConfirmView(View):` | §4.1 | (범위 밖 — `View` 는 default 있어 red 아님) |
| 〃 `:722~728` | §7 «웹 폼(Form/ModelForm …)은 … `implementation-django-web`(§6)가 소유» — **admin 절 없음**(`grep -i admin` → 294 트리·1593/1615 «배터리»·1809 복합PK 뿐) | §7(graph-owned L723) | `…/implementation-django/references/final.md/s038-7/b1`(kind-norm) |
| 〃 절 목록 | `^#+ ` 1~17장(모델·QuerySet·뷰·폼·DRF·시그널·마이그레이션·성능·캐싱·보안·테스트·미들웨어·서비스 레이어·5.x) — «admin» 절 없음 | — | — |
| `dddjango/skills/discipline-houserules/SKILL.md:63~82` | §4 타입 어노테이션(graph-owned L64): b1 «모든 이름은 «첫 대입»에 타입 — 예외 0»(R-3148 prefLabel) … 프레임워크 선언 면제(모델 필드·Meta·enum) … b7 «`Any` 는 … 어디에도 쓰지 않는다 … JSON 문서는 `Mapping[str, object]`»(R-3447 · currentExpression `R-3447@2026-09-04`) | §4 | `…/discipline-houserules/SKILL.md/s007-4/b1` · `…/s007-4/b7` |
| 〃 `:90~94` | §6.1 «표준 도구셋(uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 직접 다룬다 … 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업» | §6.1(graph-owned L91) | `…/s011-6.1/b1` |
| `dddjango/skills/implementation-python/references/final.md` | `TYPE_CHECKING`·`TypeAlias`·`django-stubs`·`monkeypatch`·`__class_getitem__` 언급 **0줄** | — | — |
| 코퍼스 전수(`skills/*/SKILL.md`·`*/references/final.md`·`agents/*.md`·`commands/dddjango.md`) | subscript 표기 예시(`ModelForm[`…) **0** · `TYPE_CHECKING` 은 `implementation-test/references/final.md:1748,1758`(coverage `exclude_lines` 설정 예시)뿐 · `type: ignore`·`type-arg`·`django_stubs_ext` **0** | — | — |
| 검사기 `.py` | `django-stubs`·`type-arg` 0 · `TYPE_CHECKING` 은 `design_pregate.py:1236,1546`(pre-gate 바인딩 파서 · 규칙 아님) | — | 보고자 L84~L85 ✓ |
| Codex 미러 | `codex-dddjango/skills/implementation-django-web/references/final.md`·`implementation-django/…` byte-equal(`cmp`) | — | — |

**새 규칙과 모순될 예시 목록**
1. django-web `:208 class ArticleForm(forms.ModelForm):` — admin/form 집합 · 확정 §2-A 가 이미 정정 대상으로 지목(`forms.ModelForm[Article]`).
2. django-web `:66 class ArticleListView(ListView):` · `:72 class ArticleCreateView(LoginRequiredMixin, CreateView):` — CBV 집합(`ListView[M]`·`CreateView[M, F]`). 같은 펜스 `s003-2/b10`.
3. implementation-django `:1328 class EditArticleView(…, UpdateView):` — CBV(`UpdateView[M, F]`) · 산문 절.
(`View` 맨몸 2건은 default 가 있어 모순 아님.)

---

## ⑥ #646 시제품 dry-run (`proto_646.py` · 대상 규칙 = 검사기 `_is_target_file` 복제: migrations·manage/wsgi/asgi·`test_*`·conftest 제외 · `test/` 아래는 `factories/`·`fake/` 만 · 숨김 디렉터리 제외)

판정: ⓐ 맨몸(Name/Attribute · 모듈 수준 별칭이 맨몸이면 alias-bare) · ⓑ 클래스 헤더 줄(`class`~`:`)의 `# type: ignore[type-arg]` · ⓑ′ 본문 AnnAssign/Assign 줄의 같은 주석 · 통과 = Subscript 기저 · `TYPE_CHECKING` 분기의 Subscript 대입 별칭 · **`TYPE_CHECKING` 분기 안 중간 ClassDef**(kkebi saju 모양 — 초안은 이걸 ⓐ 15건 오탐했고 수정했다) · 후보(exit 불산입) = code 없는 `# type: ignore` 헤더 · TYPE_CHECKING 밖 subscript 별칭(런타임 TypeError 모양).
기저 해소 = import 바인딩으로 dotted 경로 복원 후 정본 경로(`django.forms(.models).X` · `django.contrib.admin(.options).X` · CBV 5모듈) 대조 · attr 이름만 일치는 `lenient` 별도 기록(위반 아님).

| 대상 | 파일 | ⓐ | ⓑ | ⓑ′ | pass-alias | pass-subscript | 후보 | exit | jsonl |
|---|---|---|---|---|---|---|---|---|---|
| spring d2eaafe | 2509 | 30 (=①13 + ②17 이중) | 17 | 1 | 9 | 0 | 0 | 2 | `proto646-spring-d2eaafe.jsonl` |
| spring HEAD | 2555 | 17 (=②17) | 17 | 1 | 22 | 0 | 0 | 2 | `proto646-spring.jsonl` |
| kkebi HEAD | 3525 | 21 (=②21) | 21 | 0 | 31 | 15(TC 중간 클래스) | 0 | 2 | `proto646-kkebi.jsonl` |
| 〃 `--include-cbv` | 동일 | 동일 | — | — | — | — | — | — | (CBV 적중 0) |
| 플러그인 픽스처 `workspace/eval/fixtures/**`(46 루트) | 1099(`--all-files` 1180) | **3** | 0 | 0 | 0 | 0 | 0 | 2 | `proto646-fixtures.jsonl` |
| 합성 경계 20건 | 12 | 9 | 1 | 1 | 3 | 4 | 2 | 2 | `proto646-synth.jsonl` · `synth/synth646_cases.py` |

BC별(위반 종류별)은 jsonl 의 `bc`·`kind` 로 재집계 가능 — d2eaafe: ⓐ accounts 2·fortune_character 13·fortune_intent 4·fortune_record 1·media_library 2·notification 2·promotion 1·query_translation 2·wallet 3 / ⓑ 는 fortune_character 제외 동일 / ⓑ′ accounts 1. kkebi: ⓐ=ⓑ billing 7·share 2·tarot 10·top3 2.

픽스처 적중 3건 전부 `naming/bad_rules/application/orders/django_orders/admin/order/`: `extra.py:6 ExtraPanel(ModelAdmin)` · `panel.py:7 RefundForm(ModelForm)` · `panel.py:11 OrderPanel(ModelAdmin)`(`check-naming.py` 소유 픽스처). `public_surface/{good,bad_rules}`(#493/#645 픽스처)에는 admin·form 클래스가 없다 → #646 good/bad 는 신설. `workspace/tools/checker_cross_matrix.py:184` 는 EXPECTED 미등재 쌍에 red 가 생기면 «신규 교차 red … 모순 후보» exit 2 → `('naming', 'check-public-surface-annotation.py')` 항 등재(또는 픽스처 정정) 필요. 등재 지점: `workspace/tools/fixture_matrix.py:44` `("check-public-surface-annotation.py", "public_surface")`.

합성 20건 판정(전부 기대와 일치): E01 `admin.ModelAdmin` ⓐ · E02 `from … import ModelForm as MF` ⓐ · E03 `import django.forms as f; f.ModelForm` ⓐ · E04 subscript 통과 · E05 `TypeAlias` 별칭 통과 · E06 TC 중간 클래스 통과 · E07 `typing.TYPE_CHECKING` 속성형 통과 · E08 TYPE_CHECKING 밖 subscript 별칭 → 후보 · E09 모듈 수준 맨몸 별칭 ⓐ · E10/E11 parler `TranslatableAdmin`/`TranslatableModelForm` 무발화 · E12 `(TranslatableAdmin, admin.ModelAdmin[M])` mixin 통과 · E13 타 모듈에서 import 한 별칭 무발화(**사각 · fail-open**) · E14 여러 줄 헤더의 `):  # type: ignore[type-arg]` ⓐ+ⓑ · E15 code 없는 `# type: ignore` ⓐ+후보 · E16 `inlines … # type: ignore[type-arg]` ⓑ′ · E17 `InlineModelAdmin`(options 경로) ⓐ · E18 함수 안 중첩 클래스 ⓐ · E20 로컬 재정의로 그림자진 `ModelAdmin` 무발화 · `test/unit/test_panel.py` 제외 · `test/factories/panel_factory.py` 검사(#384 재료 칸).

오탐·미탐 분석:
- parler(`TranslatableModelForm`·`TranslatableAdmin`)는 attr 이름이 집합 밖이라 무발화(양 저장소 lenient-only 0). ✓
- 별칭 해소 실패 = 타 모듈 import 별칭(E13)뿐 — 무발화(미탐). 양 저장소에 이 모양 0.
- 다중 상속 mixin: 정본 기저만 보고 나머지는 무시 — 오탐 없음(E12).
- **이중 계수**: ② 모양(맨몸 + ignore)에 ⓐ와 ⓑ가 동시에 난다(d2eaafe ⓐ 30 = 13 + 17). 클래스당 1건으로 접을지 설계 결정 필요.
- 헤더 범위: 기저 마지막 줄부터 코드부가 `:` 로 끝나는 첫 줄까지 — 헤더와 본문 사이 주석 전용 줄의 `# type: ignore` 는 mypy 도 무의미하므로 실무 영향 없음.
- `# type: ignore[type-arg]` 의 admin 밖 사용(kkebi `catalog_controller.py:101 Query(None)`)은 클래스 헤더/속성 줄이 아니라 ⓑ 범위 밖 — 의도대로.

---

## ⑦ 확정 방향(§2-A)과 어긋나는 사실

1. **`django-stubs-ext` 는 현재 양 저장소에서 dev 전용·전이 의존성이다** — `dependencies`(운영)에 없고 `uv sync --no-dev` 배포는 설치하지 않는다(spring `pyproject.toml:40~41` · kkebi `:23~24` · `uv.lock:484`). settings 에 `monkeypatch()` 를 넣으면 운영 부팅이 `ModuleNotFoundError` 다. «§6.1 표준 도구 없으면 셋업»은 dev 도구셋 절이고, 새 **운영** 의존성은 §6.2(«새 런타임 의존성의 버전 선택») 소관 — 문면·발주 체크리스트가 pyproject `dependencies` 추가 + settings 1줄을 함께 요구해야 한다. README 도 «as a production dependency» 다.
2. **발주측 HEAD 는 monkeypatch 가 아니라 ③ 별칭으로 상환했다**(`1288e4a` · spring ③ 22) — kkebi 도 ③ 31 + TC 중간 클래스 15. 현장 68 클래스가 «패치를 못 쓰는 프로젝트만 별칭» 대안 모양이고 기본(직접 표기)은 **0**. 규칙 채택 시 두 모양이 같은 저장소에 공존한다(둘 다 통과이므로 위반은 아님).
3. **제3의 모양 존재**: kkebi saju 15 — `if TYPE_CHECKING: class _X(admin.ModelAdmin[M]): pass / else: _X = admin.ModelAdmin`. #646 은 TYPE_CHECKING 분기 안 ClassDef 를 별칭으로 인정해야 한다(미인정 시 ⓐ 15 오탐 · mypy 는 Success).
4. **보고자 정본 예시 L153 `inlines: ClassVar[list[type[admin.TabularInline[Any, ParentModel]]]]` 는 타입 있는 기저 아래 mypy strict red** `[assignment]`(list 불변 · 스텁 `list[type[InlineModelAdmin[Any, Any]]] | tuple[…]`). HEAD 에서 통과하는 건 `CharacterAdmin(TranslatableAdmin)` 기저가 미타입이라서다. 정본 예시는 `ClassVar[list[type[InlineModelAdmin[Any, Any]]]]`(또는 tuple/무주석)로 써야 한다 — `Sequence` 도 red.
5. **#493 과의 상호작용**: `check-public-surface-annotation.py:199~208 _is_declarative_class` 가 `_resolved_name` 으로 기저를 풀 때 `Subscript` 는 `""`, TYPE_CHECKING 별칭은 import 바인딩이 아니라 → `admin.ModelAdmin[M]` 도 `_AliasBase` 도 **선언적 면제를 잃는다**(`synth/synth493_panel.py`: `BareAdmin` 무발화 · `SubscriptAdmin`·`AliasAdmin` 의 `list_display` #493 blocker 2건). 즉 #646 이 요구하는 «올바른» 모양은 그대로 #493 을 admin 전 필드(`list_display`·`search_fields`·`model`…)에 발동시킨다. 발주측 커밋 메시지 «기저가 바뀐 클래스의 #493 첫 대입 주석 … 동일 커밋 처리»가 그 증거. 처분 후보: (a) 그대로 두고 문면에 «admin 필드도 전부 타입»을 명시 (b) #493 이 Subscript 를 벗기고 TYPE_CHECKING 별칭을 따라가도록 개정. `Meta`/`Config` 는 이름 면제라 form 은 영향 없음.
6. **S-1g(`Any` 면제)**: HEAD 에 #645 실검사기 → `panel.py:103 inlines` 는 **ⓓ 후보**(차단 아님) · `type CharacterInlineFormSet = BaseInlineFormSet[Any, …]`(character_writer.py:37)와 `save_related(formsets: list[CharacterInlineFormSet])` 는 **무발화**(TypeAlias 재별칭 · #645 docstring «표면 밖») · fortune_character/admin blocker 0. 차단용 면제는 불필요. 단 4번의 올바른 `inlines` 형태도 `InlineModelAdmin[Any, Any]` 라 `Any` 2개를 피할 수 없어 R-3447 «`Any` 어디에도» 문면과 정본 예시가 매번 ⓓ 후보로 충돌한다 — 문면 차원의 «프레임워크 미러» 예외 언급은 필요.
7. **수치**: 클래스 합 40→**39**, 맨몸 14→**13**(parler 1 혼입 추정). mypy 26·ignore 17+1·별칭 9·BC 10·parler 6 은 일치.
8. **코퍼스 모순 예시가 :208 하나가 아니다** — CBV 맨몸 3줄(django-web `:66`·`:72` 블록 `s003-2/b10` · implementation-django `:1328` 산문 §13.4). 확정 §2-A 는 django-web `:208` 만 정정 대상으로 적었다. CBV 를 규칙 범위에 넣으면 이 3줄도 함께, 넣지 않으면 «admin·form 한정»을 문면에 명시해야 예시와 규칙이 모순되지 않는다(현장 CBV 사용 0 · 확장 근거는 코퍼스 예시뿐).
9. **픽스처 충돌**: `naming/bad_rules` 의 admin 3클래스가 #646 에 걸린다 → `checker_cross_matrix.EXPECTED` 미등재 쌍 red = exit 2. 등재 또는 픽스처 정정이 삼중 등재에 포함돼야 한다.
10. 시제품은 ② 모양을 ⓐ+ⓑ **이중 계수**한다 — 클래스당 1건(ⓑ가 ⓐ를 흡수)으로 접을지 결정 필요. 보고자 표(①/② 배타)와 다르다.
11. 보고자 «검사기 불요 — 프로젝트 mypy 가 잡음»(L11)은 ②(ignore)엔 성립하지 않고(spring 17·kkebi 21 이 mypy Success) ①엔 성립한다 — 확정 §2-A 의 «검사기 신설» 근거와 일치(어긋남 아님 · 기록).

---

## ⑧ 사각 · 불확실

- 실측은 격리 사본이지만 mypy·런타임은 실서고 venv(`~/Desktop/spring_dream_server/.venv` · `~/Desktop/kkebi-server/.venv`)의 패키지를 쓴다 — 보고자 환경(L27)과 버전이 같음을 확인했다(Django 6.1 · mypy 2.3.1 · django-stubs 6.1.0 · Py 3.14.7). 사본 안 `.mypy_cache` 생성 외 실서고 무변경.
- 시제품의 별칭 해소는 **모듈 내부**만이다 — 타 모듈에서 import 한 별칭(E13)은 무발화(fail-open). 현장 0건이라 실측 영향 없음.
- `django.contrib.auth.forms` 계열(`SetPasswordMixin` 등)은 monkeypatch 가 settings 시점엔 못 덮고 `AppConfig.ready` 가 필요(README L223~L240) — 양 저장소 사용 0 · 시제품 기저 집합에도 없음.
- 보고자 ①14 의 14번째 클래스는 원문에 목록이 없어 추정(parler)이다.
- `runtime_probe.py` 는 `DJANGO_SETTINGS_MODULE` 없이 클래스 객체만 subscript 했고, 직접 표기 시제품 import 만 `spring_dream_server.settings.test` 로 `django.setup()` 했다 — DB 접속은 없었다.
- CBV 0 은 «현재 저장소» 사실이다 — dddjango-web 이 FBV 를 만드는 한 유지되지만, 플러그인 문면(django-web §2)이 CBV 예시를 유지하는 이상 레인이 CBV 를 쓸 여지는 남는다.
- mypy 실행 시간이 5~12초라 `--follow-imports=silent` BC 단위 재현은 저비용이다 — 훅 전체 범위(`application framework spring_dream_server`)는 돌리지 않았다(보고자 152/124 미재현 · S-3 영역).
