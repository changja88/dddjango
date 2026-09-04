# 현장 보고 3 · ③ 계획 리뷰 — 리뷰어 A(기술 축 — 구현 가능성·결정성·무손실) · 2026-09-04

- 대상: `workspace/plan/2026-09-04-field-report-repair-3-plan.md`(②) — §2 검사기 · §3 픽스처·매트릭스·등재 · §4 순서 · §5 무손실 · §6 3축 · §7 리스크. 대조: rv1-A §4 · rv1-C §4~§6 · 루브릭 «1단계 결과».
- 재실행 산출: `$S/rv3A/`(`$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`). 실서고 무접촉(사본 5 + spring venv mypy · cwd=`$S/spring-c20f525` · 탐침은 실행 뒤 즉시 제거 · 사본 `git status` 무변). 검사기 레코드 sink 는 `DJR_VIOLATIONS_DIR=$S/rv3A/viol` 로 격리.
- 사본 위생: `$S/spring` 에 타 리뷰어의 untracked `mp_probe_18/`·`mp_probe_s1/` 가 남아 있다 — 아래 수치는 전부 그 경로를 제외한 값이다(§2.1·§2.9).

## 1. 판정 표

| # | 항목(필답) | 판정 | 핵심 근거(상세 §2) |
|---|---|---|---|
| A-1 | §2.1 `_alias_values`/`_origin_bindings` ↔ `_module_bindings`·`_any_bindings` | 검증됨(조건) | 네 워커가 같은 걷기 규칙(if/try 하위 · 뒤 정의 우선)이면 충돌 0 — 단 **우선순위 규칙**(import 바인딩 > 별칭 값 · 뒤 정의가 앞을 덮음)과 **전달 방식**(patch493 의 모듈 전역 `_ALIAS_VALUES` 금지 → 인자 전달)을 명시해야 결정적(§2.1) |
| A-2 | #493 수리 «검출 집합 불변» 증명 | 검증됨 | patch493 재적용 before/after: spring HEAD 4,117→4,102(lost 15 = 전부 `mp_probe_*` 오염 · 실 트리 0) · d2eaafe 4,083→4,083 · kkebi 851→851 · 픽스처 4레인 동일 · synth 5→0 — ⓓ 라인 포함 집합 기준(§2.1) |
| A-3 | #646 ⓑ(i) 헤더 범위 경계 | MINOR | 계획 문면(«모든 ClassDef 헤더 범위»)은 경계 미정의. tokenize 로 «`class` 토큰 줄 ~ 괄호 깊이 0 첫 `:` 줄» 이 결정적(데코레이터 줄 제외 · 여러 줄 기저 줄 · `):` 줄 포함 · `[misc, type-arg]` 다중 코드) — 시제품 9형 전부 기대대로(§2.2). ⓑ(ii) 속성 줄은 `stmt.lineno~end_lineno` |
| A-4 | #646 ⓐ+ⓑ 접기 · ⓓ 문안 2 · 통과 3모양의 일관성 | MINOR | 접기 = 같은 ClassDef 노드 · 좌표 `cls.lineno` · ⓑ 문면(클래스명·기저명 포함) — 단순. ⓓ ② «`TYPE_CHECKING` 밖 subscript 별칭(런타임 TypeError)» 과 통과 ③ «헤더 직접 subscript」 는 같은 런타임 위험인데 하나만 ⓓ — 둘 다 같은 ⓓ(monkeypatch 채택 물음)로 맞춘다(§2.2) |
| A-5 | #646 기저 집합 — django-stubs `.pyi` 확정 열거 | MINOR | 6.1.0(양 저장소 동일) 기준 **기본값 없는 제네릭**: admin 5·forms 9(계획 8 에 `BaseModelAdmin`·`BaseFormSet`·`ModelChoiceField`·`ModelMultipleChoiceField`·`ModelChoiceIterator`·`ModelFormOptions` 누락) · CBV **32**(proto 25 에 `Base{ArchiveIndex,YearArchive,MonthArchive,WeekArchive,DayArchive,TodayArchive,DateDetail}View` 7 누락). 현장 사용 0 이라 계수 무변 — 문면 «기본값 없는 django-stubs 제네릭 기저」와 집합이 같아지도록 전수 열거·버전 고정(§2.3) |
| A-6 | #646 루트 필터 자리 · 기존 규칙 무변 | 검증됨(조건) | `_is_target_file` 무접촉(파일 목록 동일) + 규칙 함수 안 `rel` 검사가 맞다. 단 판정을 `rel.parts[0]` 로 쓰면 `src/application/**` 중첩 컨테이너(`_adopted` 가 rglob 로 허용)에서 조용히 0건 — «`rel.parts` 에 `application` 또는 `framework` 마디 포함» 으로 적는다(§2.4) |
| A-7 | #647 매트릭스(자리×값×위치) · 면제 · #645 배타 | MINOR | 표 확정(§2.5). 계획이 안 적은 것 3: ① 값 union(`dict[str, int \| None]`) 은 #647 무발화(#645 nested 몫) ② `deconstruct`(Field 계열 스텁 `dict[str, Any]` 고정 · `object` 로 바꿔도 nested 반환 차단) 면제 부재 → 정당한 오버라이드가 쓸 형태가 없다 ③ #650 과 같은 줄 이중 ⓓ 허용 여부. 픽스처 재확인: good `order_form.py` 차단 0·ⓓ 1 → exit 0 ✓ · bad `any_signature.py:41` 차단 1 ✓ |
| A-8 | #647 «반환 object(루트·컨테이너 원소) ⓓ» 오탐 실측 | 검증됨(조건) | spring 8(root 4·list 2·tuple 2) · kkebi 42(비-union 35: root 14·list 18·tuple 2·Sequence 1 / union 7). 자리표시(`pull_events -> list[object]` 15 · VO 프로퍼티 · 포트 `fetch_merge_journal -> object` · 합성 루트 `-> object`)가 다수, 정당형(JSON 트리 도우미 `_freeze/_thaw`·`_reject_json_constant`·`_require_sequence`·해시 키 튜플)이 소수 — ⓓ 물음이 «정확 타입·이벤트 union·`JsonValue`·`TypeIs`」 네 갈래를 함께 제시하면 정당형도 답이 있다. **union(`object \| None`·`tuple[object] \| None`) 포함 여부**를 계획이 안 적었다 → 포함(§2.6) |
| A-9 | #650 refined 오라클 결정성 · 문안 · 좌표 | **MAJOR** | 재실행 spring 41 · kkebi 8 재현 — 단 kkebi 8 중 **6(리터럴 컨테이너)은 전부 정당형**(`report: dict[str, object] = {…json.loads(…)}` 3 · `report.append({…})` 1 · `return (json.loads(…),)` in `-> tuple[object] \| None` 2). «자리의 선언 값 타입이 `object` 면 비후보» 규칙을 리터럴 컨테이너에도 적용하면 kkebi 2(루트 필터 뒤 **1**) · spring 41(루트 필터 뒤 **40** — `docs/` 1 제외). 좌표: AnnAssign/Return 부모는 문장 줄(호출 줄과 불일치 0/60) · 나머지는 호출 줄(§2.7) |
| A-10 | #648/#649 구현 자리·origin 워커·평탄화 · 픽스처 신설이 타 검사기에 걸리는가 | 검증됨 | good 신설(`api/payment/payment_controller.py` `-> PaymentOut \| Status[OrdersErrorSchema]` + `schema/schema_out.py` `RootModel[Annotated[…]]` 단독 + application_layer/payment 짝) 27종 census: **신규 (레인×검사기) 쌍 0** · 기존 쌍 계수만 증가(#488 26→35 · #110 1→2 · #193/#569/#570 · #256/#299 각 +1) · api-error auto exit 0(§2.8) |
| A-11 | openapi 문면 2곳 → findings_count EXPECTED | 검증됨 | `:6` docstring 무출력 · `:3362` 는 `_print_code_findings` 의 조치 print(레코드 아님 · findings_count 는 `[#N]` 레코드 해시만 · baseline 은 `unparsed` 줄 수 무변 · findings_smoke 는 DM/CC 레인만 · api_error_backstop_matrix 문자열 매칭 0) → 영향 0. `:3477`(`[#63]` 메시지) 보류가 맞다 |
| A-12 | ⓔ2 registry_gate ⓓ 앵커 — 코드 수준 · 두 저장소 실측 · smoke 무변 | **MAJOR**(조건 1건) | 시제품(`$S/rv3A/patch_gate.py` · diff 37줄 · 6자리)으로 실측: 스모크형 저장소 «ⓓ 신규 1·legacy 1» ✓ · **spring HEAD=앵커 ⓓ 신규 0**(mp_probe 제외 · legacy 1,359 · 80s) · **kkebi ⓓ 신규 0**(legacy 1,045 · exit 0 · 96s) ✓. 조건: **ⓓ 절·sidecar 키는 N′∪L′≠∅ 일 때만** — 무조건 인쇄하면 smoke **P0′**(수리 전 게이트 `34c74a6` 와 마스킹 후 byte 동일 · P0 저장소 ⓓ=0 실측)이 red. ⓓ 레코드는 `records` 와 **분리 키**(`candidate_records`)로 — `regen_core.select_records` 는 severity 로 거르지만 `records` 계약은 «귀속 위반만」 이다(§2.9) |
| A-13 | §3 등재 — tree-revision-spec 집계 셀 | **MAJOR** | 계획의 «`ast` 63→65 · `ast+` 57→60」 은 **재분류 이력 행**(`:240` «`path` 11 · `ast` 63 · `ast+` 57」 — 08-11 산출 · 불변)을 가리킨다. 실제 갱신 셀은 「값」표 `ast` 291→293·`ast+` 57→60 / 판정×어겼을때 `ast` 279→281·계 291→293 · `ast+` 56→59·계 57→60 · 계 495→500·547→552 / 읽는 법 `path`+`ast` blocker 433→435 · `ast+` blocker 56→59. spec_lint ⑦ 은 뒤 둘만 대조하고 「값」표는 안 본다(#645 선례 diff 는 셋 다 고쳤다)(§2.10) |
| A-14 | predicates 행 형식 · rule-owner-map 열 · spec_lint 항목 | 검증됨 | predicates `\| N \| grade \| 술어 \|` 3열 · ⓓ 전용 선례 #644 = «후보 ⑴… ⑵확정 위반은 … 소유 / 물음: …」 → #650 은 「확정: 없음 — 주석 `Any`·`dict[str, Any]` 는 #647 소유」 로 ⑥ 통과. rule-owner-map 은 `workspace/plan/2026-08-11-rule-owner-map.md`(계획은 파일명만 — 경로 명시) · 6열 · ast+ → ⓒ+ⓓ(discipline-reviewer) · ast → ⓓ «—» |
| A-15 | §3 도구 — ROSTER 행 형식 · manifest_seal 시점 · regen 2회 | MINOR | ROSTER `assign_set` 은 **모듈 최상위 문자열 set 리터럴만**(`_module_assign_value`+`_const_str_set` — 컴프리헨션·`\|`·frozenset 불가) → 기저 집합을 «이름 set 리터럴 + 모듈 튜플」로 두 상수로 두고 행은 **3**(public-surface 2 · api-error 1). emit 은 None 권고(#646/#649 는 코드 형상 규칙 — Base 병기 의무 목록을 넓힐 이유 없음 · 소비자 = design-architect 표기 규약). manifest: 지금은 `--write` = **draft**(`make verify` 가 `--check --draft`) · sealed 는 설치 뒤 `docs(seal)` 커밋(45d6b7c 선례). regen 2회: EXPECTED 3개가 전부 **소스 안 dict**(스플라이스) → 조각 2 재생성 diff 가 api 레인 행만인지 확인 |
| A-16 | §4 순서 결함 · §5 무손실 스크립트 | MINOR | 순서 자체는 되돌림 없음. 빠진 의존 3: `gen_pregate --write` 는 «그 조각의 검사기 편집 전부 뒤 · `make verify` 전」 · `manifest_seal --write` 는 rulepack·symbol_kinds·미러 뒤(스크립트 트리 글롭) · **`registry_gate.py` codex byte 미러**(ⓔ2)와 `pregate_symbol_kinds.json` 미러가 §3 미러 목록에 없다(`diff -rq` 가 잡지만 계획에 적는다). 조각 1 의 게이트 변경은 조각 2 매트릭스에 무영향(baseline 은 `_FINDING_RE` 만 import). 무손실 스크립트 설계 §2.12 |
| A-17 | §7 리스크 1 — 정본 예시 mypy strict | **MAJOR** | b2 그대로(`_ChildFormSetBase = BaseInlineFormSet[ChildModel, ParentModel, "ChildInlineForm"]`)는 **red**: `ChildInline.formset = ChildInlineFormSet` 이 스텁 `type[BaseInlineFormSet[Group, User, ModelForm[Group]]]` 와 **셋째 인자 불변성 충돌**(`[assignment]`). 셋째 인자 생략(b3 문면 그대로) 또는 `ModelForm[ChildModel]` 명시 → green. 그 밖(별칭 4·TC 중간 ClassDef·직접 subscript·무주석 admin 선언 속성 6종·`readonly_fields: ClassVar`)은 green(§2.11) |
| A-18 | §7 리스크 2~6 | §2.11 | 2 검증됨(A-8 · 문안 보강) · 3 MAJOR→A-12 조건 · 4 검증됨(문면 절차 · 검사기 아님 → 소급 반송 경로 없음) · 5 검증됨 · 6 MINOR(`runtime_parity_check` 가 Coordinator 절만 대조 — SKILL.md 3개는 diff 정독뿐) |
| A-19 | §3 픽스처 — good 신설 파일 배치 | **MAJOR** | 계획의 `admin/<area>/stub_generic_panel.py`(별칭 4 + TC 1 + subscript 1 한 파일)는 **check-naming #342 두 번**(«ModelAdmin 이 panel.py 밖」 · «panel.py 에 ModelAdmin 둘」) → cross **신규 red 쌍**. `record_types.py` 를 `domain_layer/shared_value_object/` 에 두면 **check-domain-model #298·#8**(pydantic import) 신규 쌍. 검증된 배치: 엔티티 폴더별 `panel.py` 하나(`order/panel.py`(0B→별칭 ModelAdmin+TabularInline) · `shipment/panel.py`(TC ClassDef) · `invoice/panel.py`(subscript)) + `order/form/line_form.py`(폼 별칭) → 신규 쌍 0 · `record_types` 는 `driven_layer/adapter/persistence/domain_bypass_query/ledger_record_query.py`(신규 쌍 0 · 계수만) (§2.8) |
| A-20 | #646 계수 재확인 | 검증됨 | proto_646 재실행(mp_probe 제외): spring HEAD ⓐ-only 0·ⓑ헤더 17·속성 1 · d2eaafe ⓐ-only 13·ⓑ 17+1 · kkebi ⓑ 21 — 계획 §5 기대와 일치 |

BLOCKER 0 · MAJOR 6(A-9 · A-12 · A-13 · A-17 · A-19 + A-12 조건) · MINOR 8 · 검증됨 7.

## 2. 항목별 상세

### 2.1 공용 기계와 #493 (A-1 · A-2)

- 현행 워커 3: `_module_bindings`(:152~188 · 이름→원명 · Assign/AnnAssign/ClassDef 가 pop) · `_any_bindings`(:350~395 · Any 이름·typing 모듈 별칭 · 같은 걷기) · `_resolved_name`(:191). 신설 2(`_alias_values`·`_origin_bindings`)는 같은 걷기 규칙이면 **읽기 전용 사전 둘이 늘 뿐** 서로를 바꾸지 않는다. 충돌 지점은 하나 — 같은 이름이 import 와 별칭 양쪽에 있을 때(`from x import _B` 뒤 `_B = admin.ModelAdmin`): `_module_bindings` 는 pop 하고 `_alias_values` 는 기록 → patch493 `_resolved_base`(«`node.id not in bindings and node.id in _ALIAS_VALUES`」)가 «뒤 정의 우선」을 그대로 낸다. 반대 순서(별칭 뒤 import)면 bindings 가 이기고 alias 는 stale — 역시 «뒤 정의 우선」. 이 규칙을 docstring 에 적는다.
- patch493 은 모듈 전역 `_ALIAS_VALUES` 를 `main` 루프에서 `clear()+update()` 한다 — 검사기 관례(`bindings` 인자 전달 · `_scan_stmts`/`_scan_class`/`_is_declarative_class` 시그니처)에 맞춰 **인자로 전달**한다(전역은 재진입·테스트 격리에 약하다).
- before/after(`$S/rv3A/493-*-{before,after}.txt` · `[#…]`+`[ⓓ#…]` 전부 sort→comm): spring HEAD lost 15 = `mp_probe_18/canonical_admin.py:41~49`(6)·`direct_admin.py`(4)·`tc_class_admin.py:14`·`mp_probe_s1/alias_inlines.py:43`·`rv1b_probe.py:33·43·52` — 전부 타 리뷰어 synth(별칭·Subscript·TC 기저 아래 맨몸 admin 속성 = 수리가 «없애기로 한」 바로 그 형상). 실 트리 lost 0 · gained 0 · d2eaafe/kkebi 0/0 · `public_surface/{good,bad_rules}`·`naming/{good,bad_rules}` 해시 동일. ⑤ 무손실 기준 = 이 6 대상 comm ∅(mp_probe 제외 필터 명시).

### 2.2 #646 헤더 범위 · 접기 · ⓓ (A-3 · A-4)

시제품 `$S/rv3A/header_span.py`(tokenize · `class` NAME 토큰부터 괄호 깊이 0 의 첫 `:` OP 까지):

| 형상 | lineno | header_end | 잡힌 ignore |
|---|---|---|---|
| A `@admin.register(M)  # type: ignore[type-arg]` 다음 줄 `class A(admin.ModelAdmin):  # type: ignore[type-arg]` | 4 | 4 | (4,'type-arg') — 데코레이터 줄 제외 ✓ |
| B 여러 줄 기저 · 기저 줄에 ignore | 7 | 10 | (8,'type-arg') ✓ |
| C `):  # type: ignore[type-arg]` | 12 | 14 | (14,'type-arg') ✓ |
| D `[misc, type-arg]` | 16 | 16 | 코드 목록 분해 필요 ✓ |
| E `class E:  # type: ignore` | 18 | 18 | (18, None) → ⓓ ① ✓ |
| F 속성 줄·메서드 시그니처 줄 ignore | 20 | 20 | 헤더 0 → ⓑ(ii)/ⓓ 채널 ✓ |
| Inner(중첩 ClassDef) | 25 | 25 | ✓ |
| H `class H(…[M]): pass  # type: ignore[type-arg]` | 28 | 28 | 헤더 줄 ignore 로 계수(mypy 도 그 줄 전체) ✓ |

- mypy 는 `[type-arg]` 를 **기저 표현 줄**에 낸다(rv1-A A-3) → 이 범위가 은폐 위치를 전부 덮는다. 정규식 `#\s*type:\s*ignore(?:\[([^\]]*)\])?` · 코드 목록은 `,` 분해 후 `type-arg` 포함 여부.
- ⓑ(ii) 속성 줄: 여러 줄 대입(`inlines = [\n …\n]  # type: ignore[type-arg]`)의 주석은 마지막 줄 → 본문 직계 Assign/AnnAssign 의 `lineno~end_lineno` 를 본다.
- ⓐ+ⓑ(i) 접기: 같은 ClassDef 노드에서 둘 다 참이면 1건 · 좌표 `rel:cls.lineno` · 메시지 = ⓑ 문면 «`<Class>`(기저 `<origin>`) 헤더의 `# type: ignore[type-arg]` — django-stubs 제네릭 맨몸을 덮었다 · 별칭(`TYPE_CHECKING`) 또는 subscript 로 적는다」. 클래스명이 메시지에 들어가므로 update 잎의 개명은 귀속(rv1-C run4 · 설계대로).
- ⓓ 두 문안: ① 헤더의 code 없는 `# type: ignore` — 물음 «덮은 진단이 django-stubs 제네릭 `[type-arg]` 인가(그러면 #646 위반 — ignore 를 지우고 별칭으로)」 ② `TYPE_CHECKING` 밖 subscript(별칭 `_B = admin.ModelAdmin[M]` **와 헤더 직접 `class X(admin.ModelAdmin[M])` 둘 다** — 런타임 `TypeError` 후보) — 물음 «`django_stubs_ext.monkeypatch()` 를 채택했는가(houserules §6.1 관찰 — 아니면 별칭으로)」. 계획은 직접 subscript 를 통과 ③ 으로만 두었는데 물리적 위험이 같으니 ⓓ 도 같이 낸다(exit 무관 · 픽스처 good `invoice/panel.py` 가 ⓓ 1 인쇄 — exit 0 유지).

### 2.3 #646 기저 집합 — django-stubs 6.1.0 실측 (A-5)

`TypeVar(…)` 에 `default=` 가 없는 제네릭 클래스(양 저장소 venv 모두 6.1.0 · `pyproject` `>=6.0.6`):

- `django.contrib.admin.options`: `BaseModelAdmin[_ModelT]` · `ModelAdmin` · `InlineModelAdmin[_ChildModelT, _ParentModelT]` · `StackedInline` · `TabularInline` (5 · `django.contrib.admin` 재수출 = ModelAdmin·StackedInline·TabularInline 3)
- `django.forms.models`: `BaseModelForm[_M]` · `ModelForm` · `BaseModelFormSet[_M, _ModelFormT(default)]`(`_M` 무기본 → bare 는 red) · `BaseInlineFormSet[_M, _ParentM, _ModelFormT(default)]` · `ModelChoiceField[_M]` · `ModelMultipleChoiceField` · `ModelChoiceIterator` · `ModelFormOptions` (8) + `django.forms.formsets.BaseFormSet[_F]` (1) — `django.forms` 재수출 = ModelForm·BaseModelForm·BaseModelFormSet·BaseInlineFormSet·ModelChoiceField·ModelMultipleChoiceField·BaseFormSet 7
- CBV(기본값 없는 `_M`·`_FormT`·`_ModelFormT`): detail 3(`SingleObjectMixin`·`BaseDetailView`·`DetailView`) · list 3(`MultipleObjectMixin`·`BaseListView`·`ListView`) · edit 11(`FormMixin`·`ModelFormMixin`·`BaseFormView`·`FormView`·`BaseCreateView`·`CreateView`·`BaseUpdateView`·`UpdateView`·`DeletionMixin`·`BaseDeleteView`·`DeleteView`) · dates 15(`BaseDateListView`·`Base/ArchiveIndexView`·`Base/YearArchiveView`·`Base/MonthArchiveView`·`Base/WeekArchiveView`·`Base/DayArchiveView`·`Base/TodayArchiveView`·`Base/DateDetailView`) = **32**. `django.views.generic` 재수출은 공개 14(+`View`·`TemplateView`·`RedirectView` — 셋은 default TypeVar/비제네릭 → 제외 유지) · Base*/Mixin 은 서브모듈 경로만. `SingleObjectTemplateResponseMixin`·`MultipleObjectTemplateResponseMixin`·`ProcessFormView` 는 비제네릭 → 제외.
- 현장(spring·kkebi `application/`·`framework/`·`web/`): 추가분 상속 0 → 검출 집합 무변. 열거는 문면 «기본값 없는 django-stubs 제네릭 기저」의 결정적 실현이고, 도구는 스텁 버전을 모르므로 docstring 에 «6.1.0 기준 전수 · 스텁 상향 시 재열거」를 적는다.

### 2.4 루트 필터 자리 (A-6)

`_is_target_file`(:115)은 파일 목록을 만든다 — 손대면 기존 5규칙의 대상이 바뀐다. 신규 3규칙(#646·#647·#650)은 각 규칙 함수 첫 줄에서 `rel` 로 거른다(`_check_explicit_any` 는 #647 분기만 · #645 는 전 파일 그대로 — 그래야 «#645 nested ⓓ 감소분 = #647 위반 1:1」 이 루트 안에서만 성립하고 밖(kkebi `web/`·`scripts/`)은 현행 그대로다). 판정식은 `"application" in rel.parts or "framework" in rel.parts`(`_adopted` 가 `rglob("application")` 로 중첩 컨테이너를 채택 신호로 인정하므로 `parts[0]` 고정은 `src/application/**` 에서 조용한 0건). 픽스처 루트(`public_surface/good`)에서는 `rel.parts[0]=='application'` 이라 어느 식이든 같다.

### 2.5 #647 매트릭스 확정 (A-7)

컨테이너 `{dict, Dict, Mapping, MutableMapping}`(builtins·typing·typing_extensions·collections.abc 바인딩 해소 · 문자열 주석 `_unstring` · `Literal[…]` 안 제외) · 값 = 마지막 슬라이스 원소(`_unstring` 뒤 `Name`). 값이 union/기타이면 #647 무발화(#645 nested 가 Any 를 본다).

| 자리 \ 값 | `Any`(top) | `Any`(nested) | `object`(top) | `object`(nested) |
|---|---|---|---|---|
| sig-param(인자·kwonly) | 차단 | 차단 | ⓓ | ⓓ |
| sig-star(`*args`/`**kwargs`) | 차단 | 차단 | ⓓ | ⓓ |
| sig-return | 차단 | 차단 | **차단**(면제: `TypeIs/TypeGuard` 루트 · `clean`×Form 계열 · [Δ] `deconstruct`×Field 계열) | 차단 |
| variable(함수·모듈 AnnAssign) | 차단 | 차단 | ⓓ | ⓓ |
| class-attr(ClassDef 직계 AnnAssign — 선언적 클래스 포함) | 차단 | 차단 | 차단 | 차단 |

- «반환 `object` 루트·컨테이너 원소」 ⓓ 는 이 표 밖의 별도 행: 반환 주석을 union 평탄화한 구성원 중 `object` Name 이거나 `{tuple, Tuple, list, List, Sequence, Iterable, Iterator, set, frozenset, Set, FrozenSet, Collection}` 의 원소에 `object` 가 있으면 ⓓ(위 표의 차단이 같은 노드에 있으면 차단만).
- #645 배타 구현 지점: `_check_explicit_any` 슬롯 루프(:483~493 · :494~500 반환 · :501~505 AnnAssign) 각 애너테이션에서 #647 을 먼저 판정 → 위반이면 그 애너테이션의 `nested` ⓓ 를 생략 · `bare`(`dict[str, Any] | Any`)는 유지 → «#645 감소분 = #647 위반 1:1」 이 성립하는 유일한 형태(좌표 동일: def 줄 · AnnAssign 자기 줄).
- `deconstruct`: django-stubs `db/models/fields/__init__.pyi:199·672` `-> tuple[str, str, Sequence[Any], dict[str, Any]]` — `object` 로 바꿔도 nested `dict[str, object]` 반환 = 차단 → 정당한 커스텀 Field 가 쓸 형태가 없다(kkebi 1 legacy · 새 레인 재발 가능). 면제 표를 «메서드 이름 × 기저 계열」 상수로: `{clean: {Form, BaseForm, ModelForm, BaseModelForm}, deconstruct: {Field, *Field}}`.
- 이중 ⓓ: `payload: dict[str, object] = json.loads(raw)` 는 #647 variable-object ⓓ + #650 ⓓ 두 줄(물음이 다르다 — 좁힘 / 검증 파서). 허용을 명시하거나 #650 이 그 AnnAssign 을 소유(#647 ⓓ 생략)하도록 한 줄 적는다 — 결정성만 있으면 어느 쪽이든 된다(권고: 허용 · 결합 0).

### 2.6 반환 `object` 형상 실측 (A-8)

`$S/rv3A/return_object.py`(루트 필터 · `retobj-{spring,kkebi}.txt`):

| | spring | kkebi |
|---|---|---|
| 루트 `-> object` | 4(`GenerationInput.role/content` VO 프로퍼티 · admin `used_at` · rag `sanitize`) | 14(`json_value._freeze/_thaw/to_python` · `_django_value` · `normalize_code`(schema_in validator) · 포트/ACL `fetch_merge_journal` · `_reject_json_constant` ×3 · `_redact_phone` · 합성 루트 `build_get_shared_reading` ×2) |
| 원소 `list[object]` | 2(`_sequence`) | 18(`pull_events` **15** · `_decode_bundle_items/_decode_cards` · ) |
| 원소 `tuple[object, …]` | 2(해시 키) | 2 · `Sequence[object]` 1 |
| union 안 | 0 | 7(`object \| None` 4 · `tuple[object] \| None` 2 · `list[object] \| tuple[object, …]` 1) |

판독: 자리표시(정확 타입·이벤트 union 이 있는데 `object`) ≈ 2/3 · 정당형(JSON 값 트리 · 좁히기 도우미 · 해시 키) ≈ 1/3. 문면 «입구 밖 자리표시」는 자리표시엔 맞고 정당형엔 안 맞는다 → ⓓ 물음을 「이 `object` 를 정확 타입 / 도메인 이벤트 union / `JsonValue` 로 바꿀 수 있는가 — 좁히기 도우미면 `TypeIs[...]` 반환으로 옮긴다」 로 적으면 정당형도 «JsonValue/TypeIs」 로 답이 닫힌다. union 포함을 명시(7건).

### 2.7 #650 (A-9)

- `jsonload_refined.py` 재실행: spring 41(annassign 12·comprehension 25·direct 4) · kkebi 8(literal-container 6·annassign 2) — rv1-A 와 동일.
- kkebi literal-container 6 의 사용처(`$S/rv3A/650-kkebi.txt` + 추적): `import_legacy_billing_use_case.py:420~422` `report: dict[str, object] = {…, k: json.loads(…)}` ×3 · `django_adapter.py:1381` `report.append({…json.loads…})` · `analytics_controller.py:99`·`bug_report_controller.py:110` `return (json.loads(text, parse_constant=…),)` in `-> tuple[object] | None` — **6/6 정당형**(값이 `object` 슬롯으로 들어간다 · R-3448 그대로). 계획의 «정당형 0」 은 리터럴 컨테이너를 추적하지 않은 rv1-A 표본에 기댄 것이다.
- 수정 오라클(`$S/rv3A/jsonload_refined2.py`): 「결과가 놓이는 자리의 **선언 값 타입**이 `object`(루트 · 컨테이너 원소 · union 전 구성원)면 비후보」를 AnnAssign·Return·리터럴 컨테이너(그 리터럴이 AnnAssign/Return 값이면 원소 슬롯으로 판정 · 호출 인자면 비후보)에 공통 적용 → spring 41(루트별 application 8·framework 32·**docs 1**) · kkebi **2**(application 1 · **scripts 1**). 루트 필터(§2.4) 뒤 기대 = **spring 40 · kkebi 1**.
- 좌표: AnnAssign/Return 부모 60건(spring 14·kkebi 46) 전부 문장 줄 = 호출 줄이나, 정의는 «문장 줄」(여러 줄 값에도 안정) · 컴프리헨션/직접 접근/리터럴은 호출 줄. 메시지에 파서 후보 두 갈래(`TypeAdapter(<TypedDict>).validate_python/json` · `x: object` 뒤 즉시 좁힘)를 싣는다.

### 2.8 #648/#649 · 픽스처 배치 census (A-10 · A-19)

`$S/rv3A/census.py`(27종 · `checker_argv` 그대로 · public-surface 는 patch493 사본 — #646/#647 미구현이라 «회복 뒤 #493」 만 반영):

- `api_error_controller/good` + payment 신설(컨트롤러 `-> PaymentOut | Status[OrdersErrorSchema]` · `schema_out.py` `PaymentOut(RootModel[Annotated[Card | Point, Field(discriminator="kind")]])` 단독 · `application_layer/payment/get_payment/` 짝 · `domain_layer/payment/exception/`): 변화 = layer-skeleton #488 26→35 · context-isolation #110 1→2 · usecase-dto #193/#569/#570 1→2 · domain-model #256/#299 1→2 — 전부 **기존 (레인×검사기) 쌍 안의 계수 변화**(사유 최소성·골격-부재 유지) · 신규 쌍 0 · `check-api-error-controller-contract.py --error-profile auto` exit 0. 상자 하나의 두 허용형(`-> Out | Status[Err]` · `-> Status[Out | Err]`)을 good 에 하나씩 두면 #648 통과 2형이 고정된다.
- `public_surface/good` 신설 4(엔티티별 `panel.py`: order(별칭 ModelAdmin+TabularInline · 무주석 `model/extra/list_display/readonly_fields/inlines`) · shipment(TC ClassDef) · invoice(subscript) + `order/form/line_form.py` 별칭 ModelForm): 변화 0 ✓. 계획 형태(한 파일 `stub_generic_panel.py` 에 ModelAdmin 4)는 `check-naming.py:429~436` #342 두 문면에 걸린다(naming 은 현재 public_surface 레인 EXPECTED 에 없어 **신규 쌍**).
- `record_types.py`: `domain_layer/shared_value_object/` → domain-model **#298·#8**(pydantic import · 신규 쌍) + ⓓ#259/#268 · `driven_layer/adapter/external_system/ledger/ledger_adapter.py` → port-adapter #370 추가(기존 쌍 안 · 규칙 id 추가) · **`driven_layer/adapter/persistence/domain_bypass_query/ledger_record_query.py` → 기존 쌍 계수만(#359 2→4 · #488 26→25)** — Thin Read 의 «이름 붙인 정적 타입」(#358) 자리라 의미도 맞다.
- bad 신설은 자기 검사기만 도니(fixture_matrix·findings_count) 교차 문제 없음 — 단 `stub_generic_bad.py` 의 «타 모듈 별칭+헤더 ignore」 는 두 파일(`_bases.py` + 사용처)이 필요하다.

### 2.9 ⓔ2 registry_gate — 코드 수준 (A-12)

시제품 `$S/rv3A/patch_gate.py` → `$S/rv3A/scripts/registry_gate.py`(원본 대비 diff 37줄):

| 자리(원본 줄) | 변경 |
|---|---|
| `:94` `_FINDING_RE` 아래 | `_CANDIDATE_RE = re.compile(r"^\s*(\[ⓓ#\d+\].*)$")` 1줄 |
| `_run_registry` `:186~245` | 반환 4-튜플(`…, cands`) · `:208` 아래 `cands: set[str]` · `:228~230` `m is None` 분기 안에서 `_CANDIDATE_RE` 매치 → `cands.add(f"{script} :: {_normalize(…)}")` · **합성 귀속 계수 `parsed` 는 위반만**(ⓓ 만 있는 red 검사기는 여전히 fail-closed) |
| 호출처 4: `:577`(provenance `run`) · `:693`(비-git) · `:733`(앵커) · `:737`(현재) | 언패킹에 `_cands`/`l_cands`/`n_cands` 추가 · 비-git 분기 `l_cands = set()` |
| `:742` `residual` 아래 3줄 | `cand_new = sorted(n_cands - l_cands)` · `cand_legacy = len(n_cands & l_cands)` · `cand_resolved = len(l_cands - n_cands)` |
| 보고 `:780` legacy 절 뒤 | **`if n_cands or l_cands:`** 절 «== ⓓ 신규(N′∖L′) k건 · legacy n건 · 해소 m건 — exit 불산입 · 감수자 입력은 신규분만(R-0284) ==» + 신규 라인 |
| `_write_introduced` `:248` | 인자 `candidates` · **`if candidates:`** `payload["candidate_lines"]`·`payload["candidate_records"]`(severity=="info" ∧ 키 일치 · `file` 접두 제거) — `records`(위반)와 분리 · `:786` 호출에 `cand_new` |
| exit `:792` | 무접촉(`attributed` 만) · 빚·provenance 채널은 ⓓ 에 적용하지 않는다 |

실측: (i) 스모크형(`skeleton/good_bc` + `_VIOLATION_REL` + 앵커에 `assert` 파일 · working 에 다른 `assert` 파일): «ⓓ 신규 1 · legacy 1」 · sidecar `candidate_lines`/`candidate_records`(`#69`·info) 분리 · 옛 게이트(main) 출력과의 diff = **새 절 3줄뿐** · exit 2 동일. (ii) `$S/spring --anchor HEAD`(untracked 오염으로 dirty): 귀속 26(전부 `mp_probe_*`) · **ⓓ 신규 2(전부 `mp_probe_*`) → 실 트리 0** · ⓓ legacy 1,359 · 80s. (iii) `$S/kkebi`: 귀속 0 · **ⓓ 신규 0** · legacy 1,045 · exit 0 · 96s. → «HEAD=앵커 → ⓓ 신규 0」 은 두 저장소에서 성립.

smoke: 현행 케이스 계수 = rows.append 30 + U 1 = **31**. `P0′`(`:373~379`)는 `_PRE_REPAIR_COMMIT=34c74a6` 의 게이트를 현행 검사기 트리 위에 덮어 실행하고 `_mask` 뒤 stdout·sidecar dict **byte 동일**을 요구한다 — P0 저장소(`good_bc`+#96 위반)의 27종 ⓓ 출력은 **0**(직접 실측)이므로 «ⓓ 절·키는 있을 때만」 조건이면 P0′ 무변, 무조건 인쇄면 red. 새 케이스 «Q ⓓ 앵커」: 앵커 커밋에 `application/orders/domain_layer/order/value_object/legacy_probe.py`(`_N: int = 1` + `assert`) · working 에 같은 폴더 `fresh_probe.py` → 기대 «ⓓ 신규 1 · legacy 1」 · exit **0**(그 자리는 27종 위반 0 · ⓓ#69 만 — 직접 실측 · `domain_layer/` 직계는 #249·#490 red 라 부적합) · `_VIOLATION_REL` 을 함께 심은 변형은 exit 2 무변. 소비자: `design_pregate.run_gate`(:1101~1119)는 `attributed_lines` 만 읽고 `regen_core.select_records`(:88~106)는 `records` 를 severity=violation 으로 거르므로 새 키는 둘 다 무영향.

### 2.10 등재 집계 셀 (A-13)

`2026-08-08-tree-revision-spec.md`: `:219` 「값」표 `ast` **291**·`ast+` **57** / `:273~279` 판정×어겼을때 `ast` 279·7·4·1=291 · `ast+` 56·1·0·0=57 · 계 495·20·10·22=547 / `:288` 읽는 법 `path`+`ast` blocker **433** · `ast+` blocker **56**. 신설 5 = #648·#649 `ast`·blocker + #646·#647·#650 `ast+`·blocker → 위 셀 각각 +2/+3. `:240` 「`path` 11 · `ast` 63 · `ast+` 57」 은 «human 158 재분류가 어디로 갔나」 표(08-11 산출)로 불변 — #645 선례(95a95cc diff)도 그 행을 손대지 않았다. spec_lint ⑦(:283~321)은 판정×어겼을때 표와 읽는 법만 재실측 대조 → 「값」표는 도구가 안 잡는다(선례는 손으로 고쳤다).

### 2.11 §7 리스크 판정 (A-17 · A-18)

1. **정본 예시 b2**(rv1-B §3.5): spring venv mypy(2.3.1 · django-stubs 6.1.0 · strict · cwd=`$S/spring-c20f525` · 캐시 scratch · `ChildModel=Group`·`ParentModel=User` 치환): `b2.py:41: error: Incompatible types in assignment (expression has type "type[ChildInlineFormSet]", base class "InlineModelAdmin" defined the type as "type[BaseInlineFormSet[Group, User, ModelForm[Group]]]")  [assignment]` — 셋째 인자 `"ChildInlineForm"` 이 `ModelForm[Group]` 의 하위 타입이라 **불변성 충돌**. `BaseInlineFormSet[ChildModel, ParentModel]`(생략 · b3 문면 그대로) 또는 `…, ModelForm[ChildModel]]` → `Success`. 그 밖 형상(별칭 4 · TC 중간 ClassDef · 직접 subscript · `readonly_fields: ClassVar[tuple[str, ...]]` · 무주석 `model/form/formset/extra/list_display/inlines` · `save_model/save_related` `Sequence[ParentInlineFormSet]`)은 green(`$S/rv3A/mypy_probe/`). → b2 의 셋째 인자를 생략하고 b3 «생략할 수 있다」 를 «생략한다(하위 폼 타입을 적으면 `formset` 대입이 불변성으로 red)」 로.
2. 반환 `object` ⓓ 오탐 — §2.6(문안 보강으로 닫힘).
3. ⓔ2 범위 — §2.9(조건 1 · smoke 31 무변 + Q 1).
4. R-0331 rev2 — 문면은 Coordinator 절차(«scope별 실행」 `dddjango.md:119`)이고 검사기 슬라이스가 아니라 기존 lane 산출물에 소급 실행될 경로가 없다(auto 사각의 기계 봉합(rv1-A §2.6 (a) tree 슬라이스)은 이번 범위 밖으로 남는다 — 회신 3 안내 유지).
5. 채번 접미 — 검증됨(ISSUED 마지막 R-3450 · R-3451~R-3467 미사용 0건).
6. SKILL.md hand 미러 4 — `runtime_parity_check` 는 Coordinator 절만 대조(docstring) → houserules·implementation-django·ninja SKILL.md 는 diff 정독뿐 · ⑤ 리뷰 입력에 «3 파일 hunk 대조」 를 명시.

### 2.12 §5 무손실 증명 스크립트 설계 (A-16)

`scratchpad/fr3/impl/lossless.py`: 대상 = {`$S/spring`, `$S/spring-d2eaafe`, `$S/spring-c20f525`, `$S/spring-f5ee428`, `$S/kkebi`} ∪ fixture 87루트. 검사기마다 (main 사본, 새 사본) × 대상으로 `checker_argv`(auto 플래그 포함) 실행 → stdout+stderr 를 `^\s*\[(ⓓ)?#(\d+)\]` 로 걸러 (심각도, 규칙, 정규화 라인) 집합. 판정: ⓐ `규칙 ∉ {646,647,648,649,650}` 인 라인 집합: `new ∖ old = ∅` · `old ∖ new` = {#645 nested ⓓ} 만이고 그 수 = 같은 (파일,줄)에 #647 위반이 있는 수(spring 518 · kkebi 157 기대) ⓑ #493 집합 동일(§2.1 필터 `mp_probe_*` 제외) ⓒ exit 는 «0→2 는 신규 규칙 라인이 ≥1 인 대상에서만」 ⓓ openapi 는 stdout byte diff 가 `:3362` 문면 1줄뿐 ⓔ registry_gate 는 `--anchor HEAD` 두 저장소 «귀속 0(오염 제외)·ⓓ 신규 0」. 결과를 표로 `rv5` 입력에 남긴다.

## 3. Δ 목록(계획 v2 에 그대로 넣을 문장)

- **ΔA-1**(§2.1 공용 기계) «`_alias_values(mod)`·`_origin_bindings(mod)` 는 `_module_bindings`·`_any_bindings` 와 같은 걷기(if/try 하위 · 함수·클래스 본문 안 import 무시)이며, 같은 이름이 import 바인딩과 별칭 값 양쪽에 있으면 **소스 순서상 뒤 정의**가 이긴다(`_resolved_base`: `id not in bindings and id in aliases`). 두 사전은 `bindings` 처럼 **인자로 전달**한다(모듈 전역 금지 · `_scan_stmts`/`_scan_class`/`_is_declarative_class` 시그니처에 추가). 무손실 기준 = 두 저장소 3사본+픽스처 4레인 before/after(`[#…]`+`[ⓓ#…]`) comm ∅ · `mp_probe_*` 제외.»
- **ΔA-2**(§2.1 #646 ⓑ(i)) «헤더 범위 = tokenize 로 `class` NAME 토큰 줄(`cls.lineno`)부터 괄호 깊이 0 의 첫 `:` OP 토큰 줄까지(데코레이터 줄 제외 · 여러 줄 기저 줄·`):` 줄 포함). ignore 판정 = `#\s*type:\s*ignore(?:\[([^\]]*)\])?` · 코드 목록을 `,` 로 분해해 `type-arg` 포함이면 ⓑ · 코드 없음이면 ⓓ ①. ⓑ(ii) = 기저 집합 클래스 본문 직계 Assign/AnnAssign 의 `lineno~end_lineno` 줄. ⓐ+ⓑ(i) 접기 = 같은 ClassDef 노드 1건 · 좌표 `cls.lineno` · ⓑ 문면(클래스명·기저 origin 포함).»
- **ΔA-3**(§2.1 #646 ⓓ) «ⓓ ② 는 `TYPE_CHECKING` 밖의 subscript **별칭과 헤더 직접 subscript 둘 다**(같은 런타임 TypeError 후보) — 물음 «`django_stubs_ext.monkeypatch()` 를 채택했는가(houserules §6.1 관찰 — 아니면 `TYPE_CHECKING` 별칭으로)». ⓓ ① 물음 «헤더의 code 없는 `# type: ignore` 가 덮은 진단이 django-stubs 제네릭 `[type-arg]` 인가(그러면 #646 — ignore 를 지우고 별칭으로)».»
- **ΔA-4**(§2.1 #646 기저 집합) «집합은 django-stubs **6.1.0** `.pyi` 에서 `default=` 없는 TypeVar 제네릭 전수: admin 5(`BaseModelAdmin`·`ModelAdmin`·`InlineModelAdmin`·`StackedInline`·`TabularInline` × `django.contrib.admin(.options)`) · forms 9(`BaseModelForm`·`ModelForm`·`BaseModelFormSet`·`BaseInlineFormSet`·`ModelChoiceField`·`ModelMultipleChoiceField`·`ModelChoiceIterator`·`ModelFormOptions` × `django.forms(.models)` · `BaseFormSet` × `django.forms(.formsets)`) · CBV 32(detail 3 · list 3 · edit 11 · dates 15 — 공개 14 는 `django.views.generic` 재수출 포함 · Base*/Mixin 은 서브모듈만) · 제외 유지 `View`·`TemplateView`·`RedirectView`·`*TemplateResponseMixin`·`ProcessFormView`. 상수는 «이름 set 리터럴 2(`STUB_GENERIC_ADMIN_FORM_NAMES`·`STUB_GENERIC_CBV_NAMES`) + 모듈 튜플」 로 두고 origin = 모듈∈허용 ∧ 이름∈집합. docstring 에 버전 고정·재열거 의무.»
- **ΔA-5**(§2.1 루트 필터) «신규 3규칙의 루트 필터는 규칙 함수 첫 줄 `if not ({"application", "framework"} & set(rel.parts)): return`(#647 은 `_check_explicit_any` 의 #647 분기만 · #645 는 전 파일 그대로). `_is_target_file` 무접촉 → 기존 5규칙 대상 파일 동일(무변 증명 = 파일 목록 해시 동일).»
- **ΔA-6**(§2.1 #647) «매트릭스(§2.5 표)를 docstring 에 그대로 싣는다. 값이 union/기타면 #647 무발화(#645 nested 몫). 면제 상수 `FRAMEWORK_OVERRIDE_EXEMPT = {"clean": {Form, BaseForm, ModelForm, BaseModelForm}, "deconstruct": {Field 계열 — 이름 `Field` 또는 `*Field` 접미}}`(기저 해소 = `_alias_values`+`_resolved_name`). 반환 `object` ⓓ 는 union 구성원 포함 · 물음 «이 `object` 를 정확 타입 / 도메인 이벤트 union / `JsonValue` 로 바꿀 수 있는가 — 좁히기 도우미면 `TypeIs[...]` 반환으로». `payload: dict[str, object] = json.loads(…)` 의 #647 ⓓ + #650 ⓓ 동시 방출은 허용(물음이 다르다).»
- **ΔA-7**(§2.1 #650) «후보 ⟺ 결과가 놓이는 자리의 **선언 값 타입이 `object` 가 아닐 때**: AnnAssign 주석(루트) · Return 의 반환 주석(루트) · 리터럴 컨테이너 요소(그 리터럴이 AnnAssign/Return 값이면 그 주석의 원소 슬롯으로 판정 · 호출 인자면 비후보) · 컴프리헨션 요소 · 직접 Subscript/Attribute 접근. union 은 전 구성원이 `object` 슬롯일 때만 비후보. 좌표 = AnnAssign/Return 은 문장 줄 · 나머지는 호출 줄. 기대(루트 필터 뒤): **spring 40 · kkebi 1**(리터럴 컨테이너 6 은 전부 `object` 슬롯 정당형 · `docs/`·`scripts/` 제외).»
- **ΔA-8**(§2.2 #648) «good 픽스처에 상자 하나의 두 허용형(`-> Out | Status[Err]` · `-> Status[Out | Err]`)을 각 1 둔다 · 좌표 = def 줄 · 메시지에 함수명(개명 시 귀속 — 설계대로).»
- **ΔA-9**(§2.4 ⓔ2) «§2.9 표대로 6자리(정규식 1줄 · `_run_registry` 4-튜플+`cands` · 호출처 4 · 집합 3줄 · 보고 절 · sidecar 키 2). **ⓓ 절과 sidecar 키(`candidate_lines`·`candidate_records`)는 N′∪L′≠∅ 일 때만** 방출(P0′ byte 동일 유지) · ⓓ 레코드는 `records` 와 분리 · 빚·provenance·exit 은 ⓓ 에 적용하지 않는다 · 합성 귀속 `parsed` 계수는 위반 라인만. smoke 새 케이스 «Q ⓓ 앵커»(앵커 `domain_layer/order/value_object/legacy_probe.py` `assert` · working `fresh_probe.py`) 기대 «ⓓ 신규 1 · legacy 1 · exit 0» + `_VIOLATION_REL` 동반 변형 exit 2 · 기존 31 무변. 실측 기대: spring/kkebi `--anchor HEAD` ⓓ 신규 0.»
- **ΔA-10**(§3 픽스처) «public_surface/good 신설 = 엔티티 폴더별 `panel.py` 하나: `admin/order/panel.py`(0B→`TYPE_CHECKING` 별칭 ModelAdmin+TabularInline · 무주석 `model/extra/list_display/readonly_fields/inlines`) · `admin/shipment/panel.py`(TC 중간 ClassDef) · `admin/invoice/panel.py`(직접 subscript · ⓓ ② 1 인쇄) · `admin/order/form/line_form.py`(별칭 ModelForm) — check-naming #342(«panel.py 밖」·«ModelAdmin 둘」) 회피. `record_types` 예는 `driven_layer/adapter/persistence/domain_bypass_query/ledger_record_query.py`(TypedDict·TypeAdapter·`dict[str, JsonValue]` 반환·`x: object = json.loads` 즉시 검증) — `domain_layer/` 는 #298·#8 red. cross 기대 = 신규 (레인×검사기) 쌍 0 · 기존 쌍 계수 변화만(`--emit-expected` 사유 최소성/골격-부재 유지). bad `stub_generic_bad.py` 의 타 모듈 별칭 케이스는 `_bases.py` 동반 2파일.»
- **ΔA-11**(§3 등재) «tree-revision-spec 갱신 셀 = 「값」표 `ast` 291→293·`ast+` 57→60 / 판정×어겼을때 `ast` blocker 279→281·계 291→293 · `ast+` blocker 56→59·계 57→60 · 계 blocker 495→500·총 547→552 / 읽는 법 `path`+`ast` blocker 433→435 · `ast+` blocker 56→59. `:240` 재분류 이력 행(«`ast` 63 · `ast+` 57」)은 불변. predicates #650 행 = «후보 ⑴… ⑵확정 위반은 #647 소유 / 물음: …»(#644 선례). rule-owner-map 경로 `workspace/plan/2026-08-11-rule-owner-map.md` · #646/#647/#650 ⓓ=discipline-reviewer · #648/#649 ⓓ=«—».»
- **ΔA-12**(§3 도구) «`gen_pregate_symbol_kinds` ROSTER **3행**(public-surface `assign_set` 이름 set 2 · api-error `assign_set` `{"ninja.Schema", "pydantic.RootModel"}` 1) · 전부 `emit=None` + note(«코드 형상 규칙 — Base 병기 채널 방출 제외」) · `assign_set` 은 모듈 최상위 문자열 set 리터럴만 허용(컴프리헨션·`|` 금지). `manifest_seal --write` 는 조각 커밋마다(status **draft** · `make verify` 의 `--check --draft`) · sealed 재발행은 설치 뒤 `docs(seal)` 커밋. 매트릭스 EXPECTED 3개는 소스 안 dict(스플라이스) — 조각 2 재생성 diff 가 api 레인 행만인지 확인.»
- **ΔA-13**(§3 미러) «byte 미러에 `registry_gate.py`(ⓔ2)·`pregate_symbol_kinds.json`·`rulepack.json` 을 명시(`diff -rq dddjango/scripts codex-…/scripts` 가 게이트).»
- **ΔA-14**(§4 순서) «조각마다: 검사기·픽스처 → `gen_pregate --write` → 매트릭스 `--emit-expected` 스플라이스 → 온톨로지·rulepack → 등재 3문서 → 미러(검사기·게이트·json 포함) → `manifest_seal --write`(draft) → `make verify` → 무손실 스크립트(§2.12) → 커밋.»
- **ΔA-15**(§1.2 b2·b3) «b2 의 `_ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel]`(셋째 인자 **생략**) · b3 «세 번째 인자(폼 타입)는 기본값 `ModelForm[_M]` 이라 **생략한다** — 하위 폼 타입을 적으면 `formset = …` 대입이 불변성으로 red 다」. ④ 착수 mypy 1회는 `$S/rv3A/mypy_probe/rv3a_b2/b2_fixed.py` 판형으로.»
- **ΔA-16**(§5) «무손실 스크립트 = §2.12 · 결과표를 rv5 입력으로 · `mp_probe_*` 제외 필터 명시.»
- **ΔA-17**(§7) «리스크 1 → ΔA-15 로 해소(실측 red 1·수정 green) · 리스크 3 → ΔA-9 조건 · 리스크 6 → ⑤ 리뷰 입력에 SKILL.md 3 파일 hunk 대조 명시.»

## 4. 사각

- 27종 census 는 patch493 사본(#646/#647/#650 미구현)으로 돌렸다 — 신규 규칙 자체의 픽스처 발화(good ⓓ 인쇄·bad 계수)는 ④ 구현 뒤 ⑤ 에서 실측해야 한다.
- mypy 는 spring venv(py3.14 · mypy 2.3.1)만 · kkebi venv 미실행 · `PYTHONPATH` 방식은 INTERNAL ERROR 라 cwd=사본 방식만 유효(⑤ 재현 시 같은 방식).
- ⓔ2 시제품은 `--approved-merge-file`·`--legacy-debt-file` 과의 동거를 실측하지 않았다(설계상 ⓓ 는 두 채널 밖 · P1~P12 판형 무변 기대).
- ninja `Status[Out | Err]` 의 런타임·OpenAPI 의미는 열지 않았다(문면·mypy 형태만).
- 온톨로지 IRI·order·LEDGER·wiring 은 B 축.

Serena: skipped — 워크트리에 `.serena/project.yml` 없음.
