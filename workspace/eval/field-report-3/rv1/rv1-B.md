# 현장 보고 3 · ① 문제 리뷰 — 리뷰어 B(규범 축: 온톨로지 정본 문면·규범 정합·소유·배치) · 2026-09-04

- 대상: `2026-09-04-field-report-repair-3-issues.md` §2-A~§2-D + 각 «수정 1» · 루브릭 ⓪ 요약·① 공격 질문(규범 축) · 증거 `evidence/{S1,S4,S5,map}/summary.md`.
- 방법: 온톨로지 정본을 rdflib 로 블록 단위 덤프(`$S/map/blocks.py`)해 IRI·order·statesNorm·문면을 직접 대조 · wiring 8 파일 `delegatedTo/enforcedBy` 전수 계수 · 렌더 md·에이전트 md 로드 지점 대조 · django-stubs 6.1.0 `.pyi` 원문 대조 · S-1g 는 격리 사본에서 mypy 탐침 1회 추가(`$S/rv1B/rv1b_probe.py` · `mypy_rv1b_probe.txt` — 사본 `$S/spring/mp_probe_s1/` 안에서 실행 · 실서고 무접촉).
- 판정 값: 검증됨 / MINOR / MAJOR / BLOCKER. BLOCKER 0 · MAJOR 7 · MINOR 9.
- IRI 접두: `<https://numchida.com/ns/djr#s/dddjango/…>` 는 `…/<doc>/<sNNN>/bN` 으로 줄여 쓴다. 규범은 `R-NNNN`.

Serena: skipped — 워크트리에 `.serena/project.yml` 없음(기본 도구 + rdflib).

---

## 1. 판정 표

| # | 항목 | 판정 | 한 줄 |
|---|---|---|---|
| B-1 | S-1-2·S-1-4 «별칭 기본 · monkeypatch 채택 시 직접 표기» ↔ R-3163(§6.1)·§6.2 | **MAJOR-1** | 방향은 검증됨(현장 68/68 별칭 · dev 전이 의존성). 그러나 «채택은 발주측»의 **규범 근거**가 §6.2 가 아니다 — §6.2·ninja §2.1 은 레인이 런타임 의존성을 *넣는* 절차다(django-ninja 선례). 근거는 «프로젝트 전역 런타임 패치 = 관찰 축 ④ 도구(§6.1 · R-3134~3137 닫힌 목록)». 자리 = **§6.1 b1 R-3163 amendment 1문장** + §4 새 블록의 참조 + R-12 문구. §4 단독 기재는 관찰 축 닫힌 목록과 어긋난다. |
| B-2 | S-1-4 정본 예시 ↔ R-3148(«예외 0»)·R-3154(프레임워크 선언 면제) · «`Any` 조건부 구절» ↔ R-3447 «어디에도» | **MAJOR-2** | 탐침 결과 **`Any` 없는 정본 예시가 mypy strict 통과**한다(`inlines` 무주석 = 스텁 `ClassVar` 상속 · `formsets: Sequence[BaseInlineFormSet[Model, Parent, ModelForm[Model]]]` bound 표기 · `save_model(form: ModelForm[Parent])`). 따라서 §2-A 수정 1 ⑤ «`Any` 조건부 구절»은 **불필요**하며 넣으면 R-3447 「어디에도」와 정면 모순(면제 문장). 대신 필요한 것은 **R-3154 rev2**: admin 패널 선언 속성(`inlines` 등)을 프레임워크 선언 면제 목록에 성문(검사기 `DECLARATIVE_BASE_NAMES` 는 이미 `ModelAdmin`·`TabularInline`·`StackedInline`·`Form`·`ModelForm` 을 면제 — 문면은 «모델 필드·Meta·enum»뿐). 결정 항목 ⑤ 철회 = 브리프 항목 후보(본질 불변). |
| B-3 | S-1-5 admin 예시 자리 — 새 섹션 vs s038-7 append · 좌표 | **MAJOR-3** | 지도 좌표 «s080-17» 오류: implementation-django-final 은 **§17 «Django 5.x 새 기능»이 실존**(s084~s087)하고 LEDGER 마지막 키는 **s093**(«### 커뮤니티 가이드» 산문). 말미 추가 정책(9ef6c4f · 중간 삽입 선례 0 · IRI≠order 선례 0)상 새 절은 **`## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저` = s094-18**(참고 자료 뒤 — 읽기 순서의 어색함은 정책 비용). s038-7 append 는 b2 `---` 뒤에 본문이 붙어 절 구분선 규약을 깬다 — 기각. 범위 = 타이핑만(배치는 houserules-final §1 트리 82행·§5 R-3423 참조). |
| B-4 | S-1-5 SKILL.md 상세 레퍼런스 표·미러 | **MAJOR-4** | implementation-django SKILL.md «상세 레퍼런스» 표(`implementation-django-skill` s005/b2~b17 · §6·§7 행 없음 · §17 행 있음)에 **§18 행 추가 필요** → doc_key **9번째**(`implementation-django-skill`) + codex `implementation-django/SKILL.md` **hand 미러**(cmp DIFF 확인). 지도 «8 doc» 누락. |
| B-5 | S-4-2·S-4-5 R-3447 rev2 + R-3448 rev2 문안 · 결정표 형식·정합 | 검증됨(+MINOR-1~4) | «선»은 R-3447(값 `Any` 전 자리 차단)·R-3448(`object` 는 입구·즉시 검증 지역 변수만 · 반환/속성 누수 차단 · JSON 은 `TypeAdapter`) 두 Work 로 정확히 갈린다 — b7 한 렌더 문안 §3.1. R-3448 은 JSON 처방 교체라 `revision-redefinition`. 결정표는 kind-table-row 블록 8개(머리행+구분행 1 · 데이터 6 — 행마다 R · 선례 django-web s003-2/b3~b8 R-2267~R-2271)·xsd:string — houserules-skill 에 표 선례 0 이어도 렌더러는 kind 무관(선례 계수 django-web 19/22 유노름). MINOR: 6행 «자리표시 `object` 금지»는 「입구 밖」 한정 필수(수정 1 의 선과 충돌) · 3행 «도메인 개념→값 객체»는 ddd §3.1 참조로(중복 지식) · `JsonValue` arm 은 공변(`Sequence`/`Mapping` — spring D4 실증) · «내부 JSON 검증 없이»는 수정 1 ⑥으로 폐기됐으니 표에도 반영. |
| B-6 | S-4-5 architecture-ddd s040-5.5/b10 `values: dict[str, Any]` 정정 | 검증됨(문안) | Knowledge Level 예시는 **키가 동적**(필드 정의가 런타임 데이터) → `TypedDict` ✗ · `JsonValue` ✗(`DATE` 값은 JSON 아님) · `Mapping` ✗(`set_field` 가 변경). 정답 = 결정표 4행 «조회표 `dict[K, 구체 V]`»: `type FieldValue = str | int | float | date`(`FieldType` 에서 파생한 닫힌 union) · `values: dict[str, FieldValue]` · `set_field(value: FieldValue)` · `from typing import Any` 제거. |
| B-7 | S-4 Coordinator R-0284 rev4 · R-0345 rev3 · «한 주제 한 소유자» | 검증됨(+MINOR-5) · **MAJOR-5**(R-0349 누락) | 문안 §3.9. #647 소유 = «`dict/Mapping/MutableMapping` 값 자리의 `Any`·`object`» 전부 · #645 소유 = 그 밖 nested(`Callable[..., Any]`·`list[Any]`)와 시그니처 bare. MINOR-5: `json.load(s)` ⓓ 후보는 술어가 다르므로 **별도 ⓓ 전용 번호**(선례 #69·#644 — predicates.md 1행 1술어). **MAJOR-5**: 지도가 S-5 검사기 #648·#649 의 registry #15 소개행 **R-0349 rev2** 를 빠뜨렸다(command-dddjango s007/b32 «#120~#132·#474·#62» → «·#648·#649»). |
| B-8 | S-5-1·5-4 문장 1 = R-0687 amendment vs 신설 | 검증됨(권고 = 신설) | R-0687 은 Obligation(«반환 타입 명시 · `-> object` 금지») · enforcedBy `check-public-surface-annotation.py`. 새 문장은 **Prohibition**(상자 둘 금지)이고 집행기가 `check-api-error-controller-contract.py`(#648)라 kind·집행기가 다르다 → **b13 텍스트 확장 + 신설 R 를 같은 블록 statesNorm 에 추가**(R-0687 amendment 아님 — 한 Work 두 집행기 혼합 회피). |
| B-9 | S-5-3 문장 2 자리 · 비대칭 설명 · api s022-5.2 | 검증됨(문안) | 문장 2 는 **둘로 가른다**: 2a «`RootModel` 단독·`Schema` 병행 금지» = 스키마 선언 → **s012-3.1 새 b9**(discriminator 봉투 규율 b7 옆 · kkebi tarot 실증 인용) · 2b «`response={200: A \| B}` 익명 union 금지» = operation 선언 → **s009-2.2 b1 확장 + 신설 R**. 비대칭은 architecture-api s022-5.2 새 b7 이 계약 관점 한 문장으로 설명한다: 오류 union 은 각 오류 schema 가 고정 `code`(const)로 **자기 판별**되므로 이름·discriminator 요구의 대상이 아니다. |
| B-10 | S-5 ⓑ 철회 뒤 «auto 프로필 사각» | **MAJOR-6** | Coordinator s007/b16(R-0331~R-0333) «Error response와 무관한 G2는 … `--error-profile auto`»의 «무관» 판정 기준이 문면에 없다(승인 12-slot 유무? 코드 모양?). 오류 status 를 `response=` 에 선언한 컨트롤러가 12-slot 없이 auto 로 돌면 #63·#125 가 잠든다 — **규범 결손**. 발주측 안내만으로는 플러그인 자기 배선이 그대로다 → R-0331 amendment 문안 §3.12(② 또는 브리프 항목). 리딩 레인의 12-slot 유무는 C/② 가 `.dddjango/20260831-2331-fortune-reading/` 로 확정. |
| B-11 | S-5-4 openapi 검사기 stale 문면 소유 | 검증됨(+MINOR-6) | 소유 = 검사기 코드(`check-openapi-error-declaration.py:6`·`:3362` — byte 미러) · 규범은 이미 R-0681 rev2(`@2026-08-25`)·R-0087 rev2 정합. 조치 문구 교체 문안 §3.13. MINOR-6: 등재 행도 stale — `2026-08-08-tree-revision-spec.md:387` «response={status: <Bc>ErrorSchema}」·`2026-08-11-rule-owner-map.md:61` — 08-25 개정 미반영. 같은 배치(파일을 어차피 손댄다). |
| B-12 | MAP-1 배선(delegatedTo/enforcedBy) | 검증됨(확정안 §3.15) | wiring 선례 계수: houserules-skill delegatedTo 71/enforcedBy 26(§4 는 discipline-reviewer 단독 · coder 배선은 §1 캐스케이드 R-3415~3421 뿐) · ninja 185/127(R-0681 enforcedBy-only · R-0687 both) · api 151/23(design-review-api) · django-final 220/23 · python 81/5 · ddd 169/106 · command 289/58. 새 R 배선표 §3.15. |
| B-13 | MAP-1 R-12 문구 2건 · 회신 3 발주측 항목 | 검증됨(문안 §3.14·§5) | S-3 문구는 9a258bf 로 이미 반영. S-1 monkeypatch 문구 문안 제공. |
| B-14 | Codex 미러 범위 전수 | 검증됨(+MINOR-7) | final.md byte 6(django·django-web·python·ddd·ninja·api — houserules final.md 는 이번 무접촉) · SKILL.md hand **3+1**(houserules §4 · Coordinator `dddjango/SKILL.md` :125·:150·registry #15 행 · **implementation-django SKILL.md §18 행** · 선택: ninja SKILL.md 핵심 원칙 불릿) · 검사기 byte 3(public-surface · api-error-controller · openapi-error-declaration) · rulepack 2 · 소스 미러(`workspace/reference/**`) corpus_mirror_sync. MINOR-7: ninja SKILL.md «핵심 운영 원칙»(s004/b8 이 R-0681 을 restates)에 S-5 두 규범의 restating 불릿을 두지 않으면 SKILL.md 만 읽는 레인이 배우지 못한다 — 선택이되 권고(doc_key 10번째). |
| B-15 | S-1-5 CBV 범위·예시 정정 소유 | MINOR-8 | 규칙 문면은 «타입 매개변수에 **기본값이 없는** django-stubs 제네릭 기저»로 정밀화하고 `View`·`TemplateView`·`RedirectView`(`_ViewResponse default=HttpResponseBase`)를 대상 밖으로 명시 — 아니면 implementation-django §4.1 `OrderView(View)` 2건이 «맨몸 예시»로 오독된다. django-web s003-2/b10·s007-6/b9 는 graph-owned code 블록 text 수정(+LEDGER graph 재기준선) · implementation-django §13.4(:1328)는 prose(LEDGER `s065-13.4 … prose` 확인) → md 직접 + LEDGER prose 재기준선. django-web §6 에 산문 1문장(새 b10 · R 1)이 있어야 web 레인이 «예시가 왜 별칭인지» 배운다 — 권고. |
| B-16 | S-1-5 «어떻게»의 소유(implementation-python?) | 검증됨 | 스텁 전용 제네릭·`TYPE_CHECKING` 별칭·`type` 문 지연 평가는 Python 지식이지만 우리 스택에서 발생 지점이 django-stubs 뿐이다 → implementation-django §18 이 «어떻게»까지 소유하고 python 은 무접촉(문서 말미 §26 뒤 새 절 = 비용 대비 0 효과). 한 주제 한 소유자 유지. |
| B-17 | 같은 날 2차 개정 Expression IRI | 검증됨 | 선례 `@2026-08-25b`(4)·`@2026-09-01b`(2)·`@2026-09-03b`(18 — R-3427 rev2→rev3 · R-3442). R-3447·R-3448·R-0284·R-0345 는 현행이 `@2026-09-04` 라 오늘 개정이면 `@2026-09-04b`(② 커밋일 기준으로 재확정). revisionKind: R-3447 amendment · R-3448 **redefinition** · R-0284/R-0345/R-0349/R-3163/R-3154/R-2715 amendment. |

---

## 2. 항목별 상세

### 2.1 S-1-2 · S-1-4 — 처방 순서·셋업 소유·`Any` 구절 (MAJOR-1 · MAJOR-2)

**규범 원문**
- R-3163 `…/discipline-houserules/SKILL.md/s011-6.1/b1`: «표준 도구셋(패키지 매니저 uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 **직접 다룬다** — … 기능에 필요한 표준 도구가 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업한다». `django-stubs-ext` 는 목록에 없고, 그 성격은 **운영 런타임 패치**(README «as a production dependency»)다 — S1 ⑦-1 실증.
- R-3164~R-3173 `…/s012-6.2/b1~b6`: «기능에 새 런타임 의존성이 필요한데 … 버전 *값* 규칙». ninja §2.1 R-0662~R-0669 `…/implementation-django-ninja/references/final.md/s008-2.1/b2~b3`: 레인이 `django-ninja(-extra)` 를 매니페스트에 핀하고 `INSTALLED_APPS` 까지 배선한다. → **레인이 런타임 의존성·settings 를 손댈 수 있다는 선례가 이미 있다.** 따라서 «monkeypatch 는 §6.2 소관이므로 발주측»이라는 근거는 성립하지 않는다.
- 성립하는 근거는 R-3134~R-3137 `…/s004-1/b6`: «**관찰이 결정 입력인 축은 닫힌 목록이다** … ④ 도구·러너(§6.1) … 여기 없는 축 … admin 구조 … 에서 기존 실물의 관찰은 결정의 입력이 아니다». `monkeypatch()` 는 프로젝트 전역 런타임 패치(23/23 기저에 `__class_getitem__` 주입 · S1 ③)라 기능 하나가 도입할 것이 아니고, **채택 여부의 관찰은 ④(§6.1)에서만 결정 입력**이 된다. 그러므로 «채택했으면 직접 표기 · 아니면 별칭»의 조건문은 §6.1 b1 에 살아야 닫힌 목록과 정합한다(§4 에만 두면 §4 가 새 관찰 축을 여는 셈).
- R-3154 `…/s007-4/b5`: «프레임워크 선언: Django 모델 필드 · `class Meta` 옵션 · enum 멤버 — 달면 프레임워크 의미가 오작동한다». 검사기 `check-public-surface-annotation.py:90~99 DECLARATIVE_BASE_NAMES` 는 `Form`·`ModelForm`·`Schema`·`BaseModel`·`TypedDict`·`NamedTuple`·`AppConfig`·`ModelAdmin`·`TabularInline`·`StackedInline`·`AdminSite`·`Factory`… 를 면제한다 → **문면 ⊂ 검사기**(기성 결손). S1 ⑦-5 «#493 이 Subscript/별칭 기저에서 admin 선언적 면제를 잃는다 → 수정 1 ④ 회복»은 곧 «admin 본문은 면제」를 전제하는데, 그 전제가 문면에 없다. 정본 예시가 `inlines = [ChildInline]`(무주석)을 쓰면 R-3148 «예외 0»과 충돌하는 것으로 읽힌다 — R-3154 rev2 가 필요하다.
- R-3447 `…/s007-4/b7`: «`Any` 는 … **어디에도 쓰지 않는다** … 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)» · «변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)».

**탐침**(`$S/rv1B/rv1b_probe.py` · spring venv mypy 2.3.1 · pyproject strict + django plugin · cwd=격리 사본): (A) `inlines = [MediaInline]` 무주석 통과 · (B) `save_related(…, formsets: Sequence[BaseInlineFormSet[Model, CharacterModel, ModelForm[Model]]], …)` 통과(`Any` 0) · (C) 스텁 미러 `BaseInlineFormSet[Any, CharacterModel, Any]` 통과 · (D) `Sequence[object]` → `[attr-defined] "object" has no attribute "save"` (예상 red 1건이 전부) · (E) `save_model(form: ModelForm[CharacterModel])` 통과. 스텁 원문: `contrib/admin/options.pyi:194 inlines: ClassVar[_ListOrTuple[type[InlineModelAdmin[Any, Any]]]]` · `:292 save_model(…, form: Any, change: Any)` · `:296 save_related(…, form: Any, formsets: Any, change: Any)`.

**판정**
- «별칭 기본 · 채택 시 직접 표기»: 방향 검증됨. 자리 = §6.1 b1(R-3163 amendment) 1문장 + §4 새 블록은 «(§6.1 관찰)» 참조 + R-12 발주 문구. §4 단독 기재는 MAJOR-1.
- «`Any` 조건부 구절»(§2-A 수정 1 ⑤): 정본 예시를 (A)+(B)+(E) 모양으로 쓰면 `Any` 가 0 이라 구절 자체가 불필요하고, 넣으면 R-3447 「어디에도」와 문면 모순(면제 문장)이다 → **삭제 권고(MAJOR-2 · 브리프 항목 후보 — 본질 불변·«면제 없음» 쪽으로의 후퇴)**. (B) 의 bound 표기는 불변성 관점에서 «상한 주장»이지만 스텁 매개변수가 `Any` 라 mypy 가 수용하는 관용 표기다 — 플래너가 스텁 미러(C)를 택하면 그 `Any` 는 현행 #645 ⓓ 후보 경로로 이미 처리되므로 **어느 쪽이든 새 면제 문장은 불필요**하다. 굳이 남기려면 §3.3 말미의 대안 문안(R-3447 선두 문장 clarification 동반)만 허용.
- R-3148~R-3150·R-3447 «프레임워크 오버라이드도 object/정확 타입»과 정본 예시(`save_model(form: ModelForm[Parent])`)는 무모순 — «정확 타입» 조항이 덮는다(탐침 E).
- R-3154 rev2(admin 선언 속성·폼 필드 면제 성문)는 **이 배치 필수** — 검사기 #493 회복(수정 1 ④)과 문면이 같은 렌더에서 맞아야 한다.

### 2.2 S-1-5 — 배치(MAJOR-3 · MAJOR-4 · MINOR-8)

- implementation-django-final 절 목록(rdflib): `s079-16.5` 뒤에 `s084-17`(«## 17. Django 5.x …» — SKILL.md 표 «Django 5.x 새 기능 | §17»), `s085-17.2`·`s086-17.3`(prose) · `s087`(«#### Composite Primary Key» graph) · `s088~s093`(prose — 「자동 모델 임포트」「모델 제약」「## 참고 자료」「공식 문서」「서적」「커뮤니티 가이드」). LEDGER 마지막 = `implementation-django-final s093`. 지도의 «s080-17» 은 census 좌표·절 번호 모두 오류.
- 말미 추가 선례 9ef6c4f(houserules-final s018-5 — «배경» prose 뒤 · «직전 삽입 노선은 원장 부식 red라 기각») · 코퍼스 전수에서 블록 IRI≠order 0건(rdflib 스캔) · `ontology_structural_check.py:274~281` 은 절 내 order 1..n 연속만 검사 — 중간 삽입은 기술적으로 열려 있으나 정책 선례 0(수리 2 Δ1 이 같은 이유로 b26 삽입을 BLOCKER 처리). → 새 절은 **s094-18** 말미.
- s038-7 append 안: b1(R-1225~1227 위임 문장) · b2 `---`(prose). 규범·코드를 b3·b4 로 붙이면 `---` 뒤에 본문이 오고 «## 8.» 헤딩 앞 구분선이 사라진다(문서 전체가 `---` 로 절을 닫는 규약). b1 텍스트 확장은 코드 펜스를 norm 블록 안에 넣는 꼴(§13 «펜스 = kind-code 전체 라인»)이라 불가. 기각.
- 제목·범위: `## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저`. **타이핑만** 소유. 배치는 houserules-final §1 트리 82행(`django_<bc>/admin/`)·§5 R-3423(driven 출구 면제 — admin 은 자기 앱 모델을 안다)이 소유하니 첫 문장에 «배치·import 방향은 houserules §1·§5» 참조만 둔다. 웹 폼(django-web §6)과의 관계: «admin 저작 화면의 `ModelForm` 은 표현 계층 웹 폼이 아니라 driven 층 admin 부속 — 이 절이 소유 · 웹 폼 `ModelForm` 의 타입 인자 표기도 같은 규칙(django-web §6 참조)」 1문장.
- SKILL.md 표: `implementation-django-skill` s005/b17 `| Django 5.x 새 기능 | §17 |⏎⏎` 뒤에 b18 `| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |` 추가(마지막 행 `\n\n` 이관). doc_key 9 + codex `implementation-django/SKILL.md` hand 미러(cmp DIFF).
- django-web 정정 소유: `…/implementation-django-web/references/final.md/s003-2/b10`(kind-code · `ArticleListView(ListView)`·`ArticleCreateView(LoginRequiredMixin, CreateView)`)·`s007-6/b9`(kind-code · `ArticleForm(forms.ModelForm)`) — norm 없음 · text 수정 + 렌더 + LEDGER graph 재기준선(선례: LEDGER `agent-design-architect s005 … graph … rebaseline`). implementation-django `:1328 EditArticleView(…, UpdateView)` — LEDGER `implementation-django-final s065-13.4 … prose` → md 직접 + LEDGER prose 행. 별칭 형 정정은 펜스 상단에 `if TYPE_CHECKING:` 블록 1벌을 두는 압축형(§3.5)으로.
- CBV 범위: django-stubs `views/generic/{detail,list,edit}.pyi` — `_M`·`_FormT`·`_ModelFormT` 에 default 없음(`ListView[_M]`·`CreateView[_M, _ModelFormT]`·`UpdateView`·`DeleteView[_M, _FormT]`·`FormView[_FormT]` 및 mixin) · `views/generic/base.pyi:16` `_ViewResponse default=HttpResponseBase` → `View`·`TemplateView`·`RedirectView` 는 맨몸이 red 아님. 문면은 «기본값 없는 것」으로 가르고 후자를 명시 제외(MINOR-8).

### 2.3 S-4-2 · S-4-5 — «선»의 문면·결정표·정합 (검증됨 + MINOR-1~4)

- 현행 b7 `…/discipline-houserules/SKILL.md/s007-4/b7`(statesNorm R-3447·R-3448 · 두 Expression 모두 `@2026-09-04` rev1). 문장 귀속(S4 ④ ①′ 확인): 1~4문장 R-3447 · 5~6문장(경계 입력·JSON `Mapping[str, object]`) R-3448. §2-C 수정 1 ⑥ 의 «R-3448 rev2 가 대상» 검증됨.
- 선의 두 축이 Work 경계와 일치한다: 값 `Any` 전 자리 차단 = R-3447(Prohibition) 확장 · `object` 입구 한정·반환/속성 누수 차단·JSON `TypeAdapter` = R-3448(Obligation) 처방 교체. R-3448 은 핵심 처방(«`Mapping[str, object]`» → «`TypeAdapter`»)이 뒤집히므로 `djr:revision-redefinition`(어휘 실존 · 25 선례).
- 면제 2 의 정밀화: django-stubs `forms/forms.pyi:78 BaseForm.clean(self) -> dict[str, Any] | None` · `forms/models.pyi:141 BaseModelForm.clean(self) -> None` → 면제 문면은 «`forms.Form`(BaseForm) 하위의 `clean()` 반환 `dict[str, object]`」이고 `ModelForm.clean` 은 대상이 아니다. `TypeIs/TypeGuard[Mapping[str, object]]` 반환 면제는 R-3448 «좁히기 도우미」와 정합(good 픽스처 `order_form.py:9` 가 그 형).
- «HTTP body 는 ninja `Schema` 가 이미 검증」: implementation-python `…/s072-12.0/b7` R-2762 «Django Ninja Schema가 API serialization boundary를 이미 소유하면 별도 pydantic DTO 를 추가하기 전에 …» 이 근거 — 새 문면이 «`TypeAdapter` 대상 = 파일·타 시스템·`json.loads` 결과 · HTTP body 는 `Schema`」로 가른다(§3.1·§3.6).
- architecture-ddd §3.1 R-3443 `…/architecture-ddd/references/final.md/s016-3.1/b3`: «`object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전**에 경계(Data Mapper 복원·요청 Schema·폼 `cleaned_data`)가 담당» — `TypeAdapter` 검증 파싱은 그 «경계 좁힘」의 JSON 판이라 무모순. 결정표 3행은 이 절을 **참조**로만(중복 지식 — MINOR-2).
- implementation-python §1.12 R-2717/R-2718(`TypeIs` 권장): R-3448 rev2 가 비-JSON 경계(`cleaned_data`·`request.user`·무스텁)에 `TypeIs`·`isinstance` 를 그대로 남기므로 무모순.
- pydantic §12.0 R-2760/R-2761(strict): `TypeAdapter(...).validate_python(x, strict=True)` 가 spring HEAD `service_runtime.py:100~103` 실물 — 문면에 «coercion 이 입력을 숨기면 strict」 참조 1구.
- «TypedDict ↔ JsonValue 비호환 · 브리지 `to_json_value(value: object)`»(S4 ⑧-4): 브리지의 `object` 는 **입구 매개변수** → 수정 1 의 선에서 ⓓ 후보(차단 아님) — 선이 ⑧-4 를 해소한다. 결정표 6행 «자리표시 `object` 금지」는 반드시 «입구 밖」으로 한정해야 이 해소가 문면에서 유지된다(MINOR-1).
- `JsonValue` arm: 보고자 `list[JsonValue] | dict[str, JsonValue]`(불변)는 `dict[str, str]` 조각을 못 담는다 — spring HEAD `json_value.py`(D4) 가 `Sequence`/`Mapping` 공변으로 간 이유. 문면은 공변형 권고(MINOR-3).
- «내부 JSON 은 검증 없이 `TypedDict`」(보고자 붙임 ⑴)은 수정 1 ⑥(«파싱한 JSON 은 내부 것도 `TypeAdapter`」 · strict `no-any-return`)으로 폐기 — 결정표 2행 문면에 반영(MINOR-4). 검증 없는 `TypedDict` 는 «우리 코드가 리터럴로 만든 값」뿐이라고 1행에 명시.
- 결정표 형식: kind-table-row 는 xsd:string(authoring §16 마지막 불릿 · norm 은 @ko). 규범 표의 행별 R 선례 = django-web `s003-2/b4~b8`(R-2267~R-2271 각 1) · api 44/77 · django 20/28 유노름(tdd 는 28 행 전부 무노름 — 참고 표). 레인이 «바로 고르는」 용도라 표가 맞고, 행마다 의무가 다르므로 **행별 R 6 + 도입문 R 1**.

### 2.4 S-4 Coordinator (검증됨 · MINOR-5 · MAJOR-5)

- R-0284 `…/commands/dddjango.md/s007/b6`(현행 rev3 `@2026-09-04` · 렌더 :108) · R-0345 `s007/b28`(rev2 `@2026-09-04` · :133) · **R-0349 `s007/b32`(rev1 `@2026-08-22` · :137)** — S-5 ⓐ·ⓒ 가 «표준 트리 슬라이스(#120~#132·#474·#62 — 프로필 무관 선행)」에 얹히므로 registry #15 소개행도 개정 대상인데 지도(S-4·S-5 표)에 없다(MAJOR-5). codex `dddjango/SKILL.md` 의 대응 행(:125·:150·registry 15 행)도 hand 미러.
- «한 주제 한 소유자」 분담 문면: «dict/Mapping/MutableMapping 값 자리의 `Any`·`object` 는 #647 · 그 밖(시그니처 bare · `Callable[..., Any]`·`list[Any]`·`Optional[Any]` …)은 #645」 — R-3447 rev2 3문장에 이 분담을 박고 R-0345 rev3 에 같은 말을 되풀이하지 않는다(registry 행은 «소유 검사기·규칙 번호·차단/후보」만).
- `json.load(s)` ⓓ 후보: predicates.md 는 1행 1술어(#645 :244 참조) — 주석 형상(#647)과 호출 흐름(json.load)은 술어가 다르다 → ⓓ 전용 번호 분리 권고(선례 #69 «프로덕션 assert·isinstance 가드」 ⓓ 전용 · #644 ⓓ 캐스케이드). 한 번호에 차단+후보 동거 선례(#645)도 있으므로 ② 의 선택이되, 분리가 R-0284 «ⓓ 후보(#N — …)」 열거를 깨끗하게 한다.

### 2.5 S-5 (검증됨 · MAJOR-6 · MINOR-6)

- b13 `…/implementation-django-ninja/references/final.md/s009-2.2/b13` R-0687(Obligation · rev1 `@2026-08-22` · wiring delegatedTo discipline-reviewer + enforcedBy public-surface). 신설 R(Prohibition · enforcedBy api-error-controller #648)을 같은 블록에 statesNorm 추가 — 블록 확장 선례 다수(수리 2 Δ1 s025-5.5/b24 «2불릿 1블록 + statesNorm 추가」). 근거 정정(S5 ⑧-3) 반영: «concrete 값을 직접 넣으면 막힌다 · 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지(형태 금지)」.
- 문장 2a 자리: s012-3.1 b7(R-0742~R-0748 발행 봉투 discriminator 규율 — `Annotated[Union[...], Field(discriminator=…)]` · «봉투 union 을 페이지네이션 응답에 직접 조합하지 않는다」)의 바로 뒤 b8(R-0749~R-0750) 다음 **새 b9**. 판별 키 규율(domain `StrEnum` 파생 `Literal` · birth-enum)은 b7 을 참조해 중복 회피. 실증 인용: kkebi `application/tarot/driving_layer/api/deck/schema/schema_out.py:50 TarotCardOut(RootModel[Annotated[TarotMajorCardOut | TarotMinorCardOut, Field(discriminator="type")]])` + e2e `test_tarot_openapi_success_contract.py:163~167`(`oneOf` 2 + `discriminator.propertyName == "type"`).
- 문장 2b 자리: s009-2.2 **b1**(R-0671·R-0672 «여러 status code 가 가능한 경우 `response={status: Schema}` 형태로 성공/오류 schema 를 분리한다」) 말미 1문장 + 신설 R(Prohibition · delegatedTo design-review-api + discipline-reviewer — 기계 판정 없음). b18(code) 뒤 append 는 코드 뒤에 규범이 오는 꼴이라 기각.
- 비대칭: R-0681 «둘 이상이면 `Union[...]`」은 오류 concrete 각각이 이름 붙은 컴포넌트(`$ref`)이고 고정 `code` 가 const 로 렌더돼 클라이언트가 `code` 로 판별한다(S5 ⑦: 503 `anyOf` 3개 = 이름 붙은 `$ref` 3개). 성공 union 은 그런 자기 판별 필드가 없어 `Field(discriminator)` + 이름 붙은 컴포넌트 하나가 계약이다. architecture-api s022-5.2 는 discriminator/oneOf/anyOf 언급 0(S5 ④ ④ 확인) → 새 b7(R 신설 · delegatedTo design-review-api — R-1967~R-1972 선례 100%).
- auto 사각(MAJOR-6): Coordinator `s007/b16` R-0331~R-0333 «Error response와 무관한 G2는 … `--error-profile auto` … `auto` 결과는 12-slot 증거가 아니라고 보고한다」. «무관」의 판정식이 없다. design-architect :63 은 «신규 endpoint 의 error profile 은 12-slot 기준으로 별도 결정」이라 12-slot 없는 오류 선언 컨트롤러는 Phase 1 에서 걸렸어야 하나, 그 배선이 G2 실행 문면에 없어 리딩 레인처럼 auto 로 «0건」이 나온다. 발주측 안내(§2-D 수정 1 ⑴-b)는 플러그인 자기 문면을 고치지 않는다 — 규범 결손. 문안 §3.12. 리딩 레인에 12-slot 이 있었다면 규범 결손이 아니라 Coordinator 절차 위반(R-0331) — 그래도 «오류 선언 컨트롤러 = Error response G2」 명문화는 유효하다.
- openapi 검사기 문면: `check-openapi-error-declaration.py:5~7` docstring «`response={status: <Bc>ErrorSchema}` 선언의 일치」 · `:3362` «각 직접 반환 status를 같은 BC의 <Bc>ErrorSchema base로 선언하고」 ↔ R-0681 rev2 `s009-2.2/b9`·R-0087 rev2 `s023-6.2/b34`(«base 로 뭉뚱그려 선언하지 않는다(2026-08-25 개정)」). 등재 행 `tree-revision-spec.md:387`(#63 본문 «response={status: <Bc>ErrorSchema}」 — 09-01 span 만 추가됨)·`rule-owner-map.md:61` 도 같은 stale.
- acceptance-tester 영향: RootModel 단독은 OpenAPI 바이트 동일(S5 ⑦) → 기존 스냅숏 계약 무영향 · 익명 union 금지는 신규 표면 형태 문장 · 리딩 400/503 base→concrete 는 발주측 OpenAPI 변경 승인(범위 밖 유지).

### 2.6 MAP-1 · 미러 (검증됨 · MINOR-7)

- 지도 대비 좌표 정정 3: s080-17 → **s094-18** · 8 doc → **9 doc**(+implementation-django-skill · 선택 10 = ninja-skill) · R-0349 rev2 추가.
- 렌더 `--apply` 가 implementation-django-final 말미 새 절에서 동작하는가: 9ef6c4f 는 houserules-final 이었으나 렌더러는 doc 무관(절 = headingSnapshot + 블록 연결) — md 헤딩 시드 → `--apply` → LEDGER baseline 1행 → 소스 미러 절 append(`workspace/reference/implementation-django/reference/final.md`) → `corpus_mirror_sync --write` 동일 절차. `target-counts.json`·`query-golden.json` 갱신 동반.
- 두 조각 분할: 조각 1(S-1+S-5)이 §4 b8 을 먼저 차지하고 조각 2(S-4)가 b9~b16 — b7(`Any`/JSON)과 S-4 가 떨어져 읽힌다(cosmetic). 렌더·LEDGER·rulepack·미러는 두 번(비용은 A 축).

---

## 3. 문안 초안 (② 가 그대로 가져갈 수 있게 — 기존 문장 최대 보존 · 새 R 번호는 «R-N1…» 자리표시, ② 가 ISSUED 순서로 채번)

### 3.1 `discipline-houserules-skill` s007-4/**b7** — R-3447 rev2(amendment) + R-3448 rev2(redefinition) · 한 렌더

```
**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환.
```

- 귀속: 1~5문장(«후보는 감수자가 집행」까지) = R-3447 · 이후 = R-3448. prefLabel 갱신: R-3447 «… · dict/Mapping 값 자리 Any 는 #647 차단» · R-3448 «경계 입력은 object/정확 타입으로 받아 즉시 좁힘 · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만 · 반환/속성 누수 #647 차단 · 면제 Form.clean·TypeIs».
- wiring: R-3447 기존(delegatedTo discipline-reviewer · enforcedBy public-surface) 유지 · **R-3448 에 enforcedBy `c/check-public-surface-annotation.py` 추가**(부분 집행 — 반환/속성 누수·후보 채널 · 저작 근거 4원: 문면 «#647 차단」·docstring·P0·registry #11).

### 3.2 `discipline-houserules-skill` s007-4 **새 블록 — S-4 결정표**(조각 2 · b9~b16 가정)

b9(kind-norm · 신설 R-N1 Prohibition/Obligation 1 · 도입문):
```
**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:

```
b10(kind-table-row · norms=[] · xsd:string): `| 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |\n|---|---|---|---|\n`
b11~b16(kind-table-row · 행마다 R-N2~R-N7):
```
| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
| 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기 |
| 도메인 개념 | 도메인 계층 | dataclass·값 객체(architecture-ddd §3.1) | 딕셔너리 |
| 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]` 에 K·V 구체 타입(V 가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |
| 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |
| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448) |
```
- 마지막 행이 `\n\n` 을 가진다(§4.1 헤딩 앞). wiring: R-N1~R-N7 delegatedTo discipline-reviewer · R-N1·R-N2·R-N5 enforcedBy public-surface(#647).

### 3.3 `discipline-houserules-skill` s007-4 **새 블록 — S-1**(조각 1 · b8 · kind-norm · 신설 R-N8 Obligation + R-N9 Prohibition)

```
**django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin(`View`·`TemplateView`·`RedirectView` 는 기본값이 있어 대상 밖). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.
```
- 귀속: R-N8(타입 인자·표기 의무) · R-N9(`# type: ignore[type-arg]` 금지). wiring: 둘 다 delegatedTo discipline-reviewer + enforcedBy public-surface(#646).
- **대안(결정 항목 ⑤ 를 굳이 유지할 때만)** — 첫 문장 clarification 동반: R-3447 rev2 선두를 «— **우리가 고르는 자리** 어디에도 쓰지 않는다」로 바꾸고 b8 말미에 «스텁이 타입 매개변수를 `Any` 로 고정해 대체형이 없는 자리를 그대로 옮긴 `Any` 는 #645 ⓓ 후보로 표시되고 감수자는 스텁 문면 대조로 통과시킨다(면제가 아니라 집행 분담)」. 권고는 삭제다.

### 3.4 `discipline-houserules-skill` **R-3154 rev2**(s007-4/b5 · amendment) · **R-3163 rev2**(s011-6.1/b1 · amendment)

b5:
```
- 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·폼 필드 · `class Meta` 옵션 · enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다 · admin 패널 클래스 본문의 Django 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …) — 타입은 스텁의 `ClassVar` 가 소유하고 `inlines` 처럼 재선언이 불변성 red 가 되는 자리가 있어 적지 않는다(적으면 스텁 선언과 같아야 한다 · 선언적 클래스 본문의 메서드는 면제가 아니다)

```
b1(§6.1):
```
표준 도구셋(패키지 매니저 uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 **직접 다룬다** — 기존 프로젝트의 도구·패키지 매니저를 감지해 존중하고(§1.1), 기능에 필요한 표준 도구가 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업한다(임의 글로벌 설치 금지). `django-stubs-ext` 의 `monkeypatch()`(운영 의존성 + settings 최상단 1줄)는 프로젝트 전역 런타임 패치라 기능 흐름이 도입하지 않는다 — 채택 여부는 관찰(§1 ④)해 §4 의 기저 타입 인자 표기(별칭 / 직접)를 고른다.

```

### 3.5 `implementation-django-final` **새 절 s094-18**(말미 · `## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저` · b1 norm R-N10 · b2 code · b3 norm R-N11 · b4 `---`)

b1:
```
admin 저작 화면(`driven_layer/django_<bc>/admin/` — 배치·import 방향은 `discipline-houserules` §1 트리 82행·§5)의 `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`TabularInline`/`StackedInline` 은 django-stubs 가 제네릭으로 선언하지만 런타임 클래스는 subscript 를 못 한다 — 규칙(타입 인자 필수 · `# type: ignore[type-arg]` 금지 · 별칭 기본 / monkeypatch 채택 시 직접)은 houserules §4·§6.1 이 소유하고, 이 절은 그 «어떻게»를 한 벌로 보인다. 웹 폼의 `ModelForm` 도 같은 표기다(`implementation-django-web` §6).

```
b2(code — 정본 예시 · `Any` 0 · #493 회복 전제):
```python
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar, TypeAlias

from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

if TYPE_CHECKING:  # django-stubs 전용 — 런타임 클래스는 subscript 불가
    _ChildFormBase: TypeAlias = forms.ModelForm[ChildModel]  # noqa: UP040 -- 기저로 쓰는 별칭이라 `type` 문이 될 수 없다
    _ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel, "ChildInlineForm"]  # noqa: UP040
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
    readonly_fields: ClassVar[tuple[str, ...]] = ("version",)
    inlines = [ChildInline]       # 재선언하면 `list[type[InlineModelAdmin[Any, Any]]]` 와 불변성 충돌 — 적지 않는다

    def save_model(self, request: HttpRequest, obj: ParentModel, form: ModelForm[ParentModel], change: bool) -> None: ...

    def save_related(self, request: HttpRequest, form: ModelForm[ParentModel], formsets: Sequence[ParentInlineFormSet], change: bool) -> None: ...
```
b3:
```
프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(houserules §6.1 관찰) `if TYPE_CHECKING:` 블록 없이 `class ParentAdmin(admin.ModelAdmin[ParentModel])` 로 직접 적는다 — 그 밖은 위 별칭이다. `BaseInlineFormSet` 의 세 번째 인자(폼 타입)는 기본값이 `ModelForm[_M]` 이라 생략할 수 있다. `# type: ignore[type-arg]` 로 맨몸을 덮지 않는다(#646).

```
- 주의: b2 의 `_ChildFormSetBase` 셋째 인자 문자열 전방 참조와 `readonly_fields` 주석은 ② 가 격리 사본에서 mypy 1회 재확인(내 탐침은 A·B·E 모양만 검증 — §2.1). `ChildInline.model` 등 무주석은 #493 회복(수정 1 ④) 뒤에만 green.
- wiring: R-N10·R-N11 delegatedTo discipline-reviewer(django-final 기본) · R-N11 enforcedBy public-surface(#646) · `djr:restates` → houserules-skill s007-4/b8.
- 부수: implementation-django-skill s005 **새 b18** `| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |\n\n`(b17 은 `\n` 으로).

### 3.6 `implementation-python-final` s007-1.5 — **R-2715 rev2**(b1 amendment) + **새 b3(code)**

b1:
```
외부 API, JSON 등 이종 데이터를 담는 딕셔너리에는 TypedDict를 사용하라. **키가 정해진 값 묶음(레코드)은 `dict[str, object|Any]` 가 아니라 `TypedDict` 다** — 종류가 여럿이면 `kind: Literal["…"]` 판별 키로 union 을 만든다. 파싱한 JSON(파일·타 시스템·`json.loads` — HTTP body 는 ninja `Schema` 가 이미 검증)은 `pydantic.TypeAdapter(그TypedDict)` 의 `validate_python`/`validate_json` 으로 **검증하며** 받는다(`TypedDict` 는 선언일 뿐 실행 시 검사가 없고, `json.loads` 반환은 `Any` 라 `-> TypedDict` 로 그냥 돌려주면 strict `no-any-return` 이다 · coercion 이 입력을 숨기면 `strict=True` — §12.0). 키가 데이터인 조회표는 `dict[K, 구체 V]`(V 가 레코드면 `TypedDict`). 구조를 정하지 않고 통과·직렬화만 하는 값은 재귀 별칭 `type JsonValue = bool | int | float | str | None | Sequence[JsonValue] | Mapping[str, JsonValue]` 다(arm 은 공변 — `dict[str, str]` 조각을 재확정 없이 담는다). `TypedDict` 는 `JsonValue`·`dict[str, object]` 자리에 못 들어가므로 직렬화 인자로 넘길 때는 `object` 를 받아 `JsonValue` 로 재구성하는 브리지 하나를 둔다(그 `object` 는 입구 매개변수 — houserules §4). 도메인 개념은 값 객체다(architecture-ddd §3.1).

```
b3(code · 기존 b2 펜스 뒤):
```python
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
- wiring: R-2715 delegatedTo discipline-reviewer 유지(변경 없음).

### 3.7 `architecture-ddd-final` s040-5.5/**b10**(code · norm 없음) — 예시 정정

`from typing import Any` 삭제 · `from datetime import date` 추가 · `FieldType` 뒤에 `type FieldValue = str | int | float | date  # FieldType 에서 파생한 닫힌 union — 필드 집합은 동적, 값 종류는 닫혀 있다` · `values: dict[str, FieldValue] = field(default_factory=dict)` · `def set_field(self, field_name: str, value: FieldValue) -> None:`. (`TypedDict` 는 키가 런타임 데이터라 부적합 · `JsonValue` 는 `date` 를 못 담음 · `Mapping` 은 `set_field` 가 변경하므로 부적합 — 결정표 4행.) LEDGER graph 재기준선.

### 3.8 `implementation-django-web-final` — 예시 정정 + §6 산문 1문장

- s003-2/b10: 펜스 상단 `from typing import TYPE_CHECKING, TypeAlias` + `if TYPE_CHECKING:` 블록에 `_ArticleListBase: TypeAlias = ListView[Article]  # noqa: UP040` · `_ArticleCreateBase: TypeAlias = CreateView[Article, ArticleForm]  # noqa: UP040` / `else:` 런타임 대입 → `class ArticleListView(_ArticleListBase):` · `class ArticleCreateView(LoginRequiredMixin, _ArticleCreateBase):`. 주석 1줄 «# Generic CBV 기저는 django-stubs 제네릭 — 표기는 houserules §4(별칭 기본 · monkeypatch 채택 시 `ListView[Article]` 직접)».
- s007-6/b9: 같은 판형으로 `_ArticleFormBase: TypeAlias = forms.ModelForm[Article]` → `class ArticleForm(_ArticleFormBase):`.
- s007-6 **새 b10**(norm · R-N12 · delegatedTo discipline-reviewer): «- `ModelForm` 기저는 django-stubs 제네릭이라 모델 타입 인자를 적는다 — 표기(별칭 기본 · monkeypatch 채택 시 직접)와 `# type: ignore[type-arg]` 금지는 `discipline-houserules` §4 소유, admin 쪽 한 벌은 `implementation-django` §18.\n\n»(b9 코드 뒤 append · b9 말미 `\n\n` 유지).
- implementation-django `:1328`(prose §13.4): `class EditArticleView(LoginRequiredMixin, PermissionRequiredMixin, _EditArticleBase):` + 직전 주석 «# _EditArticleBase: TYPE_CHECKING 별칭 = UpdateView[Article, ArticleForm] (houserules §4 · §18)» — md 직접 + LEDGER prose.

### 3.9 `command-dddjango` — R-0284 rev4 · R-0345 rev3 · **R-0349 rev2**

s007/b6(R-0284 · 해당 구절만):
```
… 감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(해당 범위 실행분 — 행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · #647 — 입구 매개변수·즉시 검증 지역 변수의 `dict/Mapping[…, object]` · #6NN — `json.load(s)` 결과가 `Any`/`dict[str, Any]` 주석·반환·컴프리헨션으로 흐른 자리 · 해당 범위 실행분)를 동봉한다. …
```
s007/b28(R-0345):
```
   11. `${CLAUDE_PLUGIN_ROOT}/scripts/check-public-surface-annotation.py` — 타입 전면(#493 — 시그니처·지역·속성·모듈/클래스 «모든 이름 첫 대입», 문법 없는 자리만 면제)·명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보 · dict/Mapping 값 자리는 #647 소유)·django-stubs 제네릭 기저(#646 — 맨몸·`type: ignore[type-arg]` 차단 · subscript/`TYPE_CHECKING` 별칭 통과)·딕셔너리-레코드(#647 — `dict/Mapping[…, Any]` 전 자리와 `[…, object]` 반환/속성 차단 · 입구 매개변수·즉시 검증 지역 변수의 `object` 는 ⓓ 후보 · `json.load(s)` 무검증 흐름은 ⓓ #6NN)·Thin Read 반환(#358)·계약 검증 토큰(#456).
```
s007/b32(R-0349):
```
   15. `${CLAUDE_PLUGIN_ROOT}/scripts/check-api-error-controller-contract.py` — narrow one-call `try`, concrete same-BC catch, direct no-arg concrete/event-specific BC-base `ErrorSchema`, two-argument `Status`, managed helper/handler/factory/serializer/mapping 금지 + 표준 트리 슬라이스(#120~#132·#474·#62·#648 반환 주석 `Status` 상자 하나·#649 `Schema`+`RootModel` 동시 상속 금지 — 프로필 무관 선행).
```
- 셋 다 amendment · `@2026-09-04b`(R-0284·R-0345) / `@2026-09-04`(R-0349 는 현행 08-22). codex `dddjango/SKILL.md` :125·:150·registry 15 행 hand 미러.

### 3.10 `implementation-django-ninja-final` — 문장 1 (s009-2.2/**b13** 확장 · statesNorm R-0687 + 신설 R-N13 Prohibition)

```
- **반환 타입을 명시한다** — `-> object`처럼 정보 없는 타입을 쓰지 않는다. 직렬화 자체는 `response=`가 결정하지만, 반환 타입 annotation은 사람·mypy를 위한 계약 표현이다. 직접 반환하는 성공 Schema와 BC `ErrorSchema`/`Status`를 실제 흐름에 맞게 표현한다. **반환 주석의 `Status` 상자는 하나다** — `-> Status[Out | ErrA | ErrB]`(성공·오류 union 을 한 `Status` 안에) 또는 `-> Out | Status[Err]`. `Status[A] | Status[B]`(상자 둘)는 쓰지 않는다: `Status[T]` 의 `T` 는 불변이라 concrete 값을 직접 넣는 순간 mypy strict 가 `[return-value]` 로 막히고, 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지다 — 형태 자체를 금지한다(#648).
```
- wiring: R-N13 enforcedBy `c/check-api-error-controller-contract.py`(#648 완전 커버 — R-0684 선례 enforcedBy-only) + delegatedTo discipline-reviewer(문장 근거 «사람·mypy 계약 표현」 — R-0687 과 같은 배선).

### 3.11 ninja 문장 2 — 2a s012-3.1 **새 b9**(R-N14 Prohibition/Obligation) · 2b s009-2.2/**b1** 확장(R-N15 Prohibition)

b9(§3.1):
```
- **성공 응답이 판별 키로 갈리는 union 이면 이름 붙은 `RootModel` 하나로 선언한다** — `class XResponseSchema(RootModel[Annotated[A | B, Field(discriminator="kind")]])`. ninja `Schema` 를 함께 상속하지 않는다(`ResolverMetaclass` 와 pydantic `RootModel` 메타클래스 충돌 — mypy `[metaclass]`·`[call-arg] root` · #649). 판별 키의 선언 규율은 위 발행 봉투 불릿과 같다(domain `StrEnum` 파생 `Literal`). OpenAPI 에는 `oneOf` + `discriminator` 를 가진 컴포넌트 하나로 렌더된다(실증: `TarotCardOut(RootModel[Annotated[TarotMajorCardOut | TarotMinorCardOut, Field(discriminator="type")]])` · e2e 가 `oneOf` 2 + `discriminator.propertyName` 을 단언).

```
b1(§2.2) 말미 1문장 추가:
```
… 여러 status code가⏎가능한 경우 `response={status: Schema}` 형태로 성공/오류 schema를 분리한다. 한 status 의 성공 본문이 둘 이상의 모양이면 `response={200: A | B}` 익명 union 을 적지 않는다 — 이름 붙은 컴포넌트와 discriminator 를 잃어 계약이 바뀐다(`architecture-api` §5.2) · §3.1 의 `RootModel` 하나를 선언한다.
```
- wiring: R-N14 enforcedBy api-error-controller(#649 — `Schema`+`RootModel` 동시 상속만 기계 판정) + delegatedTo design-review-api(성공 union 계약 판단) · R-N15 delegatedTo design-review-api + discipline-reviewer(기계 판정 없음 — 검사기가 `response=` 값 union 의 성공 status 를 안 본다).
- 선택(MINOR-7): ninja SKILL.md s004 «핵심 운영 원칙» 새 불릿 «- 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행 금지 · `response={200: A | B}` 금지) (§2.2·§3.1)」 · restates b13·b1·b9 · R-N16.

### 3.12 `architecture-api-final` s022-5.2 **새 b7**(R-N17 · delegatedTo design-review-api)

```
- 한 상태 코드의 성공 본문이 둘 이상의 모양이면 판별 필드(discriminator)를 가진 **이름 붙은 schema 하나**(`oneOf` + `discriminator`)로 계약한다 — 익명 `anyOf` 는 클라이언트가 분기할 이름과 판별 키를 잃는다. 오류 본문의 union 은 각 오류 schema 가 고정 `code` 로 자기 판별되므로 이 요구의 대상이 아니다(§6 에러 프로필)

```
(b6 말미 `\n\n` → `\n` · b7 이 `\n\n`.)

### 3.13 Coordinator **R-0331 amendment**(s007/b16 — MAJOR-6 · ② 또는 브리프)

```
   - **scope별 실행**: Error response G2는 승인된 code/preserve scope마다 위 command를 각각 렌더해 실행한다. Error response와 무관한 G2는 … `auto` 결과는 `Error response contract 12-slot` 증거가 아니라고 보고한다. **«무관»의 판정은 코드 모양이 아니라 승인 12-slot 유무다 — 단 승인 12-slot 없이 이번 산출물의 컨트롤러가 BC 오류 status 를 `response=` 에 선언했으면 `auto` 로 돌리지 않고 G1 반송(`STOP_FOR_USER_APPROVAL` — error profile 미결정)이다: `auto` 는 #63·#125 등 code-profile 규칙을 재우므로 오류 응답을 선언한 표면의 G2 증거가 될 수 없다.**
```

### 3.14 `check-openapi-error-declaration.py` stale 문면(코드 · byte 미러) + 등재 행

- `:5~7` docstring: «BC 오류와 ``response={status: <Bc>ErrorSchema}`` 선언의 일치」 → «BC 오류와 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·`Union`·명시값 base — base 뭉뚱그림 금지 · 2026-08-25)의 ``response=`` 선언의 일치」.
- `:3362` 조치: «각 직접 반환 status를 같은 BC의 <Bc>ErrorSchema base로 선언하고,」 → «각 직접 반환 status를 그 status에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base) 선언하고,」.
- `tree-revision-spec.md:387` #63 본문 · `rule-owner-map.md:61` 비고: 08-25 개정 span 추가(R-0681 rev2·R-0087 rev2 정합).

### 3.15 R-12 문구 2건 · 배선 확정안

R-12 행 반영 문구 추가(S-3 문구 뒤 `·` 로 병기):
```
· **반영 문구(09-04 현장 보고 3 S-1)**: «django-stubs 제네릭 기저의 타입 인자 표기 — `django-stubs-ext` 를 운영 `dependencies` 에 넣고 settings 최상단에서 `django_stubs_ext.monkeypatch()` 를 부르는 것은 프로젝트 전역 결정(발주측)이다 · 채택했으면 레인은 `X[Model]` 직접 표기, 아니면 `TYPE_CHECKING` 별칭 — 레인은 패치를 도입하지 않고 `# type: ignore[type-arg]` 는 어느 쪽이든 위반(#646)» 1줄
```

배선 확정안(wiring 파일별):

| 대상 | delegatedTo | enforcedBy | 근거 |
|---|---|---|---|
| houserules-skill R-N8·R-N9(S-1 b8) | discipline-reviewer | public-surface(#646) | §4 R-3447 선례 · 검사기 커버 |
| houserules-skill R-3154 rev2 | (없음 유지) | public-surface | 현행 배선 유지 |
| houserules-skill R-3163 rev2 | discipline-reviewer | — | 현행 유지 |
| houserules-skill R-3447 rev2 | discipline-reviewer | public-surface | 현행 유지 |
| houserules-skill R-3448 rev2 | discipline-reviewer | **public-surface 추가**(#647 부분 집행) | 문면 «#647 차단」·docstring·registry #11 |
| houserules-skill R-N1~R-N7(결정표) | discipline-reviewer | R-N1·R-N2·R-N5 public-surface(#647) · 나머지 없음 | 행별 기계 판정 유무 |
| implementation-django-final R-N10·R-N11(§18) | discipline-reviewer | R-N11 public-surface(#646) | django-final 220/220 선례 · restates b8 |
| implementation-django-skill(표 행) | — | — | table-row norms=[] |
| django-web-final R-N12(§6 b10) | discipline-reviewer | — | web 128/2 선례 |
| python-final R-2715 rev2 | discipline-reviewer | — | 현행 유지 |
| ddd-final s040-5.5/b10 | — | — | code · LEDGER 만 |
| command R-0284 rev4 | command-dddjango | — | 현행 |
| command R-0345 rev3 · R-0349 rev2 | — | public-surface / api-error-controller | 현행 |
| command R-0331 rev(선택) | command-dddjango | — | 현행 |
| ninja-final R-N13(b13 상자 하나) | discipline-reviewer | api-error-controller(#648) | R-0687 동거 · 완전 커버 |
| ninja-final R-N14(§3.1 RootModel) | design-review-api | api-error-controller(#649 부분) | 스키마 계약 |
| ninja-final R-N15(§2.2 익명 union 금지) | design-review-api · discipline-reviewer | — | 기계 판정 없음 |
| ninja-skill R-N16(선택 불릿) | design-review-api · discipline-reviewer | — | R-2929 선례(restates) |
| api-final R-N17(§5.2 b7) | design-review-api | — | R-1967~R-1972 100% |

---

## 4. 새로 발견한 규범 결손

1. **R-3154 ⊂ 검사기 `DECLARATIVE_BASE_NAMES`**(`check-public-surface-annotation.py:90~99`): 문면은 «모델 필드·Meta·enum」, 검사기는 폼 필드·admin 패널·`Schema`·`BaseModel`·`TypedDict`·`NamedTuple`·`AppConfig`·`Factory` 까지 면제. 기성 결손이나 이 배치가 admin·폼을 정면으로 다루므로 최소 «폼 필드·admin 선언 속성」은 성문(§3.4). 나머지(`Schema`·`BaseModel` 필드는 R-3155 «`x: T` 가 있어야 동작」과 겹침 — 별도 정리 후보)는 이월.
2. **Coordinator «Error response와 무관한 G2」의 판정식 부재**(R-0331~R-0333) — 오류 선언 컨트롤러가 12-slot 없이 auto 로 통과(§3.13).
3. **registry #15 소개행 R-0349 개정 누락**(지도) — #648·#649 배선 표면.
4. **implementation-django SKILL.md 상세 레퍼런스 표에 §18 행**(doc_key 9) — 없으면 SKILL 만 읽는 coder 가 §18 을 찾지 못한다(coder 는 스킬을 직접 로드 · discipline-reviewer 는 implementation-django 를 로드하지 않음 — `agents/discipline-reviewer.md:5~10` skills 목록에 없음 → §18 규범의 delegatedTo discipline-reviewer 는 «감수자가 참조 인용으로 읽는다」는 기존 django-final 220건과 같은 전제).
5. **#63 등재 행 stale**(tree-revision-spec :387 · rule-owner-map :61) + 검사기 docstring/조치 문구 — 08-25 개정이 규범만 고치고 검사기 문면·등재를 빠뜨린 흔적.
6. **django-web §6 산문에 `ModelForm` 타입 인자 언급 0** — 예시만 고치면 «왜 별칭인가」를 web 레인이 못 배운다(§3.8 b10).
7. **`View`·`TemplateView`·`RedirectView` default 존재** — 규칙 범위를 «기본값 없는 기저」로 가르지 않으면 implementation-django §4.1 `OrderView(View)` 2건이 모순 예시로 오독된다.
8. **`JsonValue` arm 불변/공변** — 보고자 표기(`list`/`dict`)는 실사용에서 재확정 비용을 낳는다(spring D4 실증) → 공변 표기 성문.
9. **`json.load(s)` ⓓ 후보의 번호·술어 분리** — predicates.md 1행 1술어 관례.
10. **결정표 6행 «자리표시 `object` 금지」와 수정 1 «입구 object 허용」의 충돌** — 표를 «그대로」 옮기면 R-3448 rev2 와 같은 렌더에서 모순(§3.2 6행 «입구 밖」 한정 필수).
11. **S-1 monkeypatch 조건문의 규범 자리** — §4 단독이면 R-3134~R-3137 닫힌 관찰 목록 밖에서 관찰을 결정 입력으로 삼는 문장이 된다(§3.4 §6.1 b1 로 귀속).

---

## 5. «② 계획에 넣을 것»

1. **좌표 정정**: implementation-django 새 절 = **s094-18**(제목 «## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저» · 참고 자료 뒤 말미) · doc_key **9**(+`implementation-django-skill` s005 새 b18) · 선택 10(`implementation-django-ninja-skill` s004 불릿) · **R-0349 rev2** 추가.
2. **결정 항목 §2-A 수정 1 ⑤(`Any` 조건부 구절) 철회**를 브리프 항목으로 올린다 — 근거: 탐침 A·B·E(`$S/rv1B/`) · 정본 예시를 `Any` 0 으로 쓰고 **R-3154 rev2**(admin 선언 속성·폼 필드 면제 성문)를 같은 배치에 넣는다(#493 회복과 한 렌더).
3. **S-1 셋업 조건 = §6.1 b1 R-3163 rev2 1문장**(관찰 축 ④ 귀속) + §4 b8 «(§6.1 의 관찰)」 참조 + R-12 문구(§3.15). §2-A «§6.1 이 덮음」·«§6.2 소관이므로 발주측」 두 근거 문장은 계획서에서 빼고 «전역 런타임 패치 = 관찰 축 ④」로 쓴다.
4. **S-1 규칙 범위 문면** = «타입 매개변수에 기본값이 없는 django-stubs 제네릭 기저」 + 목록 + `View`·`TemplateView`·`RedirectView` 제외 명시 → #646 기저 집합과 1:1.
5. **b7 한 렌더 문안(§3.1)** 채택 · R-3447 amendment(`@2026-09-04b`) · R-3448 **redefinition**(`@2026-09-04b`) · prefLabel 갱신 · R-3448 enforcedBy public-surface 추가(저작 근거 기록).
6. **결정표 = kind-table-row 8블록(xsd:string) · 행별 R 6 + 도입 R 1** · 6행 «입구 밖」 한정 · 2행 «파싱한 JSON 은 내부 것도 `TypeAdapter`」 · 5행 `JsonValue` 공변 arm · 3행 ddd §3.1 참조.
7. **python §1.5** = R-2715 rev2(§3.6) + 새 code b3 · **ddd s040-5.5/b10** = `FieldValue` 닫힌 union(§3.7) · 두 곳 모두 LEDGER graph 재기준선.
8. **Coordinator**: R-0284 rev4 · R-0345 rev3 · R-0349 rev2(§3.9) + `json.load` ⓓ 번호 결정(분리 권고) + codex `dddjango/SKILL.md` hand 미러 3행.
9. **S-5 문면**: 문장 1 = b13 확장 + 신설 R(§3.10 · R-0687 amendment 아님) · 문장 2a = s012-3.1 새 b9(§3.11 · tarot 인용) · 문장 2b = s009-2.2 b1 확장 + 신설 R · api s022-5.2 새 b7(§3.12) · 선택 ninja SKILL.md 불릿.
10. **auto 사각**: R-0331 amendment(§3.13)를 계획에 넣거나 브리프 항목으로 — 최소한 회신 3 발주측 안내와 함께 «플러그인 자기 문면 결손」으로 기록. C/② 가 리딩 레인 12-slot 유무를 `.dddjango/20260831-2331-fortune-reading/` 에서 확정.
11. **openapi 검사기 문면 2곳 + 등재 행 2곳**(§3.14) — 검사기 byte 미러 3파일(public-surface·api-error-controller·openapi-error-declaration).
12. **미러 전수**: final.md byte 6(django·django-web·python·ddd·ninja·api) · SKILL.md hand 3~4(houserules §4 · Coordinator · implementation-django §18 행 · 선택 ninja) · 소스 미러 `workspace/reference/**` corpus_mirror_sync(새 절은 수동 append 선례 9ef6c4f) · rulepack 2 · LEDGER 행 = graph 재기준선 8~9 + prose 1(implementation-django s065-13.4) · ISSUED 신설 ≈ 15~17(R-N1~R-N17 중 채택분) · target-counts·query-golden.
13. **회신 3 §(발주측) 항목**: ① S-3 mypy 자기 BC 범위 ② S-1 monkeypatch 채택 결정(운영 의존성+settings) · 미채택 시 별칭 유지 · `# type: ignore[type-arg]` 18줄(spring)·22줄(kkebi)은 빚(#646 앵커 격리) ③ S-1 #493 회복 뒤 admin 필드 첫 대입 주석은 필수 아님(1288e4a 관행은 허용) ④ S-4 legacy 1,098줄 + kkebi `web/` 111·`scripts/` 206 앵커 격리 · 2차 정리(822줄) 별도 발주 · `Form.clean -> dict[str, Any]` 22곳은 `dict[str, object]` 치환(손대면 #647 귀속) ⑤ S-4 검사기 루트 필터 부재 이월 고지 ⑥ S-5 오류 응답을 선언한 컨트롤러 G2 는 code-json 프로필(auto 는 #63·#125 침묵) · 리딩 400/503 base 선언 + e2e 동결 단언 2개 = OpenAPI 변경 승인 사안 ⑦ S-5 legacy 상자 둘 13함수(spring 7·kkebi 6)·kkebi base 선언 31자리 빚 목록 ⑧ S-5 `RootModel` 단독 = kkebi tarot 선례 인용 고지.
14. **두 조각 분할 부작용 기록**: §4 b8(S-1)·b9~(S-4) 순서로 b7(`Any`/JSON)과 S-4 가 떨어짐(cosmetic · 조각 순서의 결과) — 필요하면 조각 2 에서 b8↔b9 order 교환은 «중간 삽입 선례 0」과 같은 이유로 하지 않는다.

— 끝. 탐침·산출: `$S/rv1B/rv1b_probe.py` · `$S/rv1B/mypy_rv1b_probe.txt`(1 error = 예상 D 형 `object` 만).
