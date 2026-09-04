# rv5-A — ⑤-1 구현 리뷰 · 조각 1(`56b27e1` · S-1 + S-4) · 리뷰어 A(기술 축 — 검사기·게이트·픽스처·매트릭스 정독 + 재실행) · 2026-09-04

- 대상: `56b27e1` 의 `dddjango/scripts/check-public-surface-annotation.py` · `registry_gate.py` · `workspace/tools/{registry_gate_smoke,gen_pregate_symbol_kinds,findings_count_matrix,checker_baseline_matrix,checker_cross_matrix}.py` · `workspace/eval/fixtures/public_surface/**` · 등재 3문서 · 구현 기록 `evidence/impl/piece1-summary.md` + 로그. 대조 = 계획 v2 Δ5~Δ11·Δ14 · rv3-A §2·§3 · rv3-C §2·§3.
- 재실행 산출: `$S/rv5A/`(`$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`). 실서고 무접촉 · 사본 4(`spring`·`spring-d2eaafe`·`spring-f5ee428`·`kkebi` · 전부 tracked 무변 · untracked 는 `.dddjango/violations/*.jsonl` 뿐) · mypy 는 spring venv(cwd=픽스처 good 루트 · ΔC-8 레시피). 사본 안에 만든 파일은 `kkebi/rv5a_probe.md`(게이트 «무해 변경») 하나 — 실행 뒤 제거 확인. 옛 검사기 = `git archive main dddjango/scripts` → `$S/rv5A/old/`. 합성 트리 = `$S/rv5A/synth/`(`application/`·`framework/`·`web/` 3루트). 정정 시제품 = `$S/rv5A/proto/`(diff 34줄 · `proto.diff`).
- 사본 위생(동시 리뷰 오염): 실행 중 `$S/spring` 에 타 리뷰어의 `mp_probe_rv5b/`(untracked · 옛 검사기 +6 #493), `$S/kkebi` 에 `_rv5c_probe` 지역 변수 1줄이 잠시 존재했다 — 아래 수치는 첫 실행(오염 전 · 저자 로그와 동일)이거나 그 경로를 제외한 값이다.
- Serena: skipped — 워크트리에 `.serena/project.yml` 없음(리뷰·재실행 · 소스 수정 0).

## 1. 판정 표

| # | 필답 항목 | 판정 | 핵심 근거(상세 §2) |
|---|---|---|---|
| A-1 | Δ5 #646 — origin 집합·`_classify_base` 4상태·헤더 범위·ⓑ(ii)·접기·ⓓ 두 종·루트 필터·별칭 규칙 | **검증됨 + MAJOR 1**(§2.1 · MixUser) | 집합 admin 5·forms 9·CBV 32 + 모듈 튜플 10 (`:134~153`) ✓ · 경계 합성 40형 중 39 기대대로 — **`TYPE_CHECKING` 중간 ClassDef 의 기저가 mixin-first(`class _Base(TranslatableAdmin, admin.ModelAdmin[M])`)이면 사용 클래스가 ⓐ 위반(exit 2 · 거짓)** — `_alias_defs :331` 이 «첫 기저»만 기록해 else 별칭(맨몸)이 이긴다. 현장 4사본에 이 형상 0(잠복) · 정정 4줄(§3-1) · 정정 뒤 4사본 레코드 집합 동일 |
| A-2 | Δ6 #647 — 매트릭스 5×4·면제 3·`TypeIs[dict[str, Any]]` 차단·union 값 무발화·Literal·문자열·별칭 3·자리표시 ⓓ·#645 배타·#645 byte 동일 | 검증됨 | 합성 46형 전부 기대대로(§2.2) · 별칭 `Mapping as _Mapping`/`typing.Mapping`/`collections.abc.Mapping` 3 차단 ✓ · 자리표시 ⓓ 루트·`\| None`·`list`·`tuple[…, ...]`·`Sequence` ✓ · 같은 노드 차단 시 ⓓ 생략 ✓ · 슬롯 배타(`ex2(x: dict[str, Any], y: Callable[..., Any])` → x #647 v · y ⓓ#645 유지) ✓ · **`[#645]` 위반 라인 순서까지 byte 동일**(76/78/78/121 — `sorted((lineno, rule, kind))` 는 #645 부분수열의 상대 순서를 보존) · ⓓ#645 → #647 **슬롯 키** 1:1 = 655/642/661/55 · unmatched 0(§2.5) |
| A-3 | Δ7 #650 — 오라클 전수·좌표 | 검증됨 + MINOR 2 | 합성 27형 중 25 기대대로(§2.3) · 좌표 문장 줄(여러 줄 값 ✓) · 별칭 4(`json as j`·`from json import loads`·`… as jl`) ✓ · **`tuple[object, ...]`** 원소 슬롯이 `...` 를 «마지막 원소»로 읽어 거짓 ⓓ(이종 튜플 index·dict 키 자리도 동일 사각) · 메시지가 별칭명(`json.jl(…)`)을 찍는다 — 둘 다 ⓓ·문면이라 MINOR(§3-3·§3-4) |
| A-4 | #493 수리 — 검출 집합 불변 · `_scan_stmts` 호출 전수 | 검증됨 | 4사본 #493 (파일:줄, 메시지) 집합 lost/gained 0/0(3,216/3,225/3,225/173) + `[#493]` 라인 **순서** 동일 · main 픽스처 트리 9/9 LOSSLESS 재확인 · `_scan_stmts(` 13(정의 1 + 재귀 11 + main 1) 전부 `aliases` 전달 · `_scan_class` 1 · `_is_declarative_class` 기본값 None(§2.4) |
| A-5 | ⓔ2 registry_gate — 6자리·`parsed`·ⓓ 절 조건·sidecar 분리·exit/provenance/빚 무접촉·smoke Q/Q′·P0′ | 검증됨 + MINOR 3 | 정규식 `:95` · 4-튜플 `:191/:250` · 호출처 4(`:590`·`:706`·`:747`·`:751`) · `parsed` 는 `_FINDING_RE` 분기만 ✓ · ⓓ 절 `if n_cands or l_cands:` `:800` ✓ · exit `:816` 무접촉 · provenance `_cands` 폐기 ✓ · smoke 33/33 재실행 ✓ · P0′ 통과 = 새 절·키가 ⓓ 0 이면 부재(P0 저장소 ⓓ 0) ✓ · Q 재현으로 sidecar `candidate_lines`/`candidate_records`(`#69`·info)·`records` 0 · Q′ `records` = schema_smoke 3 · `candidate_lines` = fresh_probe 만 ✓(§2.6). MINOR: ⓐ sidecar 키 조건이 `if candidates`(= **N′∖L′≠∅**)라 Δ10 문면(N′∪L′≠∅)보다 좁다 ⓑ smoke Q 의 «records 와 분리» 단언은 records 가 빈 케이스라 공허 · Q′ 는 sidecar 를 안 본다 ⓒ 모듈 docstring·`_write_introduced` docstring 에 ⓓ 채널 무기재(계획 §2.4 «docstring») |
| A-6 | 픽스처·매트릭스 — good 0 · bad 계수 대응 · `SharedAliasPanel` #493 · mypy strict · cross 신규 쌍 0 | 검증됨 | good exit 0 · 21 파일 · 레코드 0 ✓ · bad 37 = 33 v + 4 ⓓ · 계수 문자열 8항 전부 1:1 대응(§2.7) · `stub_generic_bad.py:30` #493 = 타 모듈 별칭(의도 · 기록됨) ✓ · mypy strict(ΔC-8) 신설 4파일 0 errors · `order_form.py` 22(기존 legacy 동일) ✓ · `checker_cross_matrix` 재실행 «차이 0건» · fixture 104/104 · baseline 73 · count 73 ✓ |
| A-7 | 무손실 — 12/12 허용 규칙 = §5 · RED 3 = 신설·정정 파일 옛 #493 뿐 · main 9/9 · unmatched 5 = `mp_probe_*` | 검증됨 + MINOR 1 | `lossless_diff.py` 허용 = B∖A ∈ {646..650} · A∖B = (info,#645) ∧ 같은 (경로,**줄**)에 #647 v ✓ 계획 §5/Δ3 ⑫ 와 같다 — 단 키가 **줄** 단위(Δ3 ⑫ «(경로·줄·슬롯)»·C-3 미반영) → 본 리뷰가 슬롯 키로 재검증(unmatched 0) · RED 3 전수 = `good/…/admin/order/panel.py:19·20·21·25·26(+2)` · `shipment/panel.py` · `bad/…/stub_generic_bad.py:26`(전부 «별칭 기저 아래 무주석 admin 선언 속성» = 수리 의도) ✓ · main 트리 9/9 재실행 LOSSLESS ✓ · 내 사본엔 `mp_probe_*` 없어 unmatched 0 |
| A-8 | 등재 — tree-revision-spec 3행+집계 · predicates 3행 · rule-owner-map 3행 · spec_lint · ROSTER · pregate json · byte 미러 4 · rulepack | 검증됨 | 「값」표 `ast+` 57→60 · 판정×어겼을때 59/60 · 계 498/550 · 읽는 법 59(`path+ast` 433 불변 — 조각 1 은 `ast+` 만) ✓ · predicates 셀 `\|` 0 · ⓓ 행 «후보·물음»(#650) ✓ · rule-owner-map ⓓ=discipline-reviewer ✓ · `spec_lint` 0(«규칙 550 · ast+ 60») · ROSTER 2행 `emit` 기본값 None ✓ · `gen_pregate --check` in-sync(56) · `diff -rq` 미러 = `__pycache__` 뿐 · `ontology_rulepack --check` 정합 ✓ |
| A-9 | 새로 발견한 결함 | **MAJOR 1 · MINOR 8** | §2.8 · 정정 §3 |

**BLOCKER 0 · MAJOR 1(A-1 MixUser) · MINOR 8 · 검증됨 7.** 정정 시제품(§3-1~§3-5 · `$S/rv5A/proto`)을 4사본에 돌린 결과 = 현행 새 검사기와 **레코드 집합 동일**(4,537/4,543/4,562/1,291) — 정정은 현장 무손실이고 합성 거짓 발화 4형만 닫는다.

## 2. 항목별 상세

### 2.1 Δ5 #646 (A-1)

명세 대조(`check-public-surface-annotation.py`):
- 집합 `:134~153` — `STUB_GENERIC_ADMIN_FORM_NAMES` 14(admin 5 + forms 9) · `STUB_GENERIC_CBV_NAMES` 32 · `STUB_GENERIC_MODULES` 10 · docstring «6.1.0 기준 · 스텁 상향 시 재열거» `:29~34` ✓. origin = `_dotted(:301)` 로 모듈 dotted 복원 → 모듈∈튜플 ∧ 이름∈집합(`:792`).
- `_classify_base :803` 4상태 bare/alias-tc/subscript-runtime/subscript-tc ✓ · 별칭 depth `<4`(Name 4홉까지 해소) · 같은 이름 import+별칭은 «뒤 정의 우선»(`b.id not in bindings` 가 pop 을 본다) ✓.
- 헤더 범위 `_class_header_end :831` tokenize `class`~괄호 깊이 0 첫 `:`(데코레이터 제외) ✓ · `_ignore_codes :857` 코드 목록 `,` 분해 ✓ · ⓑ(ii) 본문 직계 Assign/AnnAssign `lineno~end_lineno` `:909~918` ✓ · 접기 `:901~906`(header type-arg → ⓑ 문면·origin 라벨 / elif bare → ⓐ / elif code 없음 → ⓓ①) ✓ · ⓓ② `runtime_sub :907` (별칭·헤더 직접 둘 다) ✓ · 루트 필터 `_in_rule_roots :637` 규칙 함수 첫 줄(`:868` · `_check_json_load :945` · `judge` 의 `in_roots`) — `_is_target_file` 무접촉 ✓ · 사전 3(`bindings`·`aliases`·`origins`)은 `main :1131~1136` 에서 인자 전달(전역 0) ✓.

합성 실행(`$S/rv5A/synth/application/orders/driven_layer/django_orders/admin/x/s646.py`·`s646b.py` · `.venv/bin/python dddjango/scripts/check-public-surface-annotation.py $S/rv5A/synth`):

| 형상 | 기대 | 실측 |
|---|---|---|
| `@admin.register(M)  # type: ignore[type-arg]` 다음 줄 맨몸 | ⓐ(데코레이터 줄 제외) | ⓐ ✓ |
| 여러 줄 기저 줄 ignore · `):` 줄 ignore · `[misc, type-arg]` | ⓑ 접기 1건(라벨 `ModelAdmin`) | ⓑ ✓ ×3 |
| `class NoCode:  # type: ignore`(기저 없음) | ⓓ① | ⓓ① ✓ |
| 맨몸 + code 없는 ignore / `[misc]` 만 | ⓐ | ⓐ ✓(ⓓ① 접힘) |
| TC 중간 ClassDef · TC 별칭 · TC 별칭의 별칭 · 중첩 `if` 안 TC 별칭 | 무발화 | 무발화 ✓ |
| TC 밖 subscript 별칭 · 헤더 직접 subscript | ⓓ② | ⓓ② ✓ ×2 |
| `import django.contrib.admin as adm; adm.ModelAdmin` · `options.ModelAdmin` · `from django.contrib.admin import ModelAdmin` | ⓐ | ⓐ ✓ ×3 |
| `ListView`·`DetailView`·`CreateView` 맨몸 / `View`·`TemplateView` 맨몸 / parler `TranslatableAdmin` | ⓐ / 무발화 / 무발화 | ✓ |
| 중첩 ClassDef(`Outer.Inner(admin.TabularInline)`) | ⓐ | ⓐ ✓ |
| 별칭 사슬 `_A4`(4홉) / `_A5`·`_A6` | ⓐ / 무발화(중단 · fail-open) | ✓ |
| `from … import View as _B; _B = admin.ModelAdmin` / 반대 순서 | ⓐ / 무발화 | ✓(뒤 정의 우선) |
| `inlines = [\n …\n]  # type: ignore[type-arg]`(TC 별칭 클래스) · AnnAssign 속성 줄 | ⓑ(ii) 마지막 줄 | ✓ |
| 메서드 시그니처 줄 ignore | 무발화 | ✓ |
| `from django.forms import ModelForm as MF` 맨몸 · `forms.BaseFormSet` 맨몸 · `forms.Form` | ⓐ · ⓐ · 무발화 | ✓ |
| `try: _T = admin.ModelAdmin except: _T = object` | 뒤 정의(`object`) 우선 → 무발화 | ✓(규칙대로) |
| TC 안 맨몸 별칭 `if TYPE_CHECKING: _X = admin.ModelAdmin` | ⓐ | ✓ |
| `framework/` 맨몸 / `web/` 맨몸 | ⓐ / 무발화(루트 필터) | ✓ |
| **TC 중간 ClassDef mixin-first `class _Mix(TranslatableAdmin, admin.ModelAdmin[M])` + else 별칭** | 무발화 | **ⓐ 위반(거짓)** — `_alias_defs :331` «첫 기저»만 기록 → `tc_sub` 공집합 → `defs[-1]`(else 맨몸 별칭) → bare |
| else 분기의 런타임 ClassDef `else: class _B(admin.ModelAdmin): …` | (규범 형은 별칭 · mypy 는 else 미도달) | ⓐ 위반 — 규범 형이 아니라 위반이라 볼 수도 있으나 문면 «[type-arg] 빚»은 거짓(MINOR · §3-2) |
| 한 줄 클래스 `class O(admin.ModelAdmin): x = 1  # type: ignore[type-arg]` | 1건 | **2건**(ⓑ(i)+ⓑ(ii) 같은 줄 · MINOR §3-5) |
| TC 클래스 안 중첩 ClassDef 직접 subscript / `if not TYPE_CHECKING:` 역분기 | 무발화 | ⓓ②(거짓 · exit 무관 · 사각 §4) |

MixUser 판정 근거: (1) 규범(houserules §4 R-3458 · tree-revision-spec #646 «`if TYPE_CHECKING:` 별칭(또는 분기 안 중간 ClassDef)»)이 중간 ClassDef 를 정당한 표기로 명시한다 (2) Django admin 에서 mixin-first(`ImportExportMixin, admin.ModelAdmin` · parler `TranslatableAdmin`)는 MRO 상 mixin 이 앞이어야 하는 관용이라 «기저 순서를 바꿔 검사기를 통과»시키면 동작이 바뀐다 (3) 위반(exit 2)이라 코더가 반송된다. 현장: kkebi TC ClassDef 15 전부 단일 subscript 기저 · spring 0 → 잠복이지만 새 레인의 첫 mixin 에서 터진다 → **MAJOR**. 계획(rv1-A §4.1 «첫 기저»)의 문면을 그대로 구현한 것이라 구현 오류가 아니라 명세 사각이다 — 정정은 §3-1(4줄 · 4사본 레코드 집합 동일 실측).

### 2.2 Δ6 #647 (A-2)

`_record_value :645`(컨테이너 이름 `_leaf(_resolved_name)` 로 import 별칭 해소 · 값 = 마지막 슬라이스 · `Literal` 제외 · 문자열 `_unstring`) · `judge :725~748`(#647 → #645 순 · 자리 5 × 값 2 · 면제 `guard_root`/`exempt_object` 는 sig-return 만 · 자리표시 ⓓ 는 `not blocked647` 조건) · `_exempt_override :695`(`clean`×Form 계열 · `deconstruct`×`Field`/`*Field` · 기저 해소 `_resolved_base`) · `_return_object_placeholder :676`(TypeIs/TypeGuard 루트 제외 · union 구성원 · SEQUENCE 원소 depth 1).

합성(`s647.py` 46 자리) 결과 전부 기대대로 — 매트릭스 20칸(sig-param/star/return/variable/class-attr × Any top/nested · object top/nested) ✓ · 면제 `TypeIs[dict[str, object]]`·`TypeGuard[…]` 무발화 · `TypeIs[dict[str, Any]]` 차단 ✓ · `clean`×`forms.Form`/`forms.ModelForm`/별칭 `_FB = forms.Form` 무발화 · 비-Form `clean` 차단 ✓ · `deconstruct`×`models.Field`/`models.CharField` 무발화 · 비-Field 차단 ✓ · `dict[str, object | None]` 무발화 · `dict[str, Any | None]` → #647 무발화 + ⓓ#645 nested 유지 ✓ · `Literal["Any"]`/`Literal["object"]` 무발화 ✓ · 문자열 주석 param v + return v ✓ · 별칭 3 차단 ✓ · 자리표시 `-> object`/`object | None`/`list[object]`/`tuple[object, ...]`/`Sequence[object] | None` ⓓ · `-> dict[str, object]` 차단만 · `TypeIs[object]` 무발화 · `tuple[str, Sequence[object]]` 무발화(depth 2 · 계획대로) ✓ · `dict[str, Any] | Any` → #645 bare v + #647 v(bare 유지) ✓ · TypedDict 직계 필드 `dict[str, object]` 차단(«선언적 클래스 포함» 계획대로) ✓ · `payload: dict[str, object] = json.loads(raw)` → ⓓ#647 + ⓓ#650 동시 ✓.

#645 byte 동일: `$S/rv5A/run_copies.sh`(옛 = main 아카이브 · 새 = 브랜치 · 각 venv · cwd=사본) → `[#645]` 위반 라인을 **순서대로** 비교 = 동일(spring 76 · d2eaafe 78 · f5ee428 78 · kkebi 121). 근거: 옛 `sorted(hits, key=(lineno, kind))` → 새 `(lineno, rule, kind)` — #645 항목끼리는 rule 이 상수라 안정 정렬이 상대 순서를 보존하고, `emit_all` 은 삽입 순서 방출(`findings.py :308`).

### 2.3 Δ7 #650 (A-3)

`_check_json_load :942`(별칭 = `_dotted(fn.value)=="json"` · Name 은 origins ∈ {json.load, json.loads}) · `judge :965`(AnnAssign/Return/컴프리헨션/첨자·속성/리터럴 컨테이너 depth 0→1 · 호출 인자 비후보) · `_slot_is_object :923`(union 전 구성원 · depth 1 = 컨테이너 마지막 원소). rv3-A `jsonload_refined2.py` 오라클과 구조 동일.

합성(`s650.py`·`s650b.py`): `x: object` 무 · `dict[str, object]` 후보 · `object | None` 무 · `object | int` 후보 · `Any` 후보 · 무주석 무 · `list[object] = [json.loads]` 무 · `list[int] = […]` 후보 · `dict[str, object] = {"k": …}` 무 · 호출 인자·`TypeAdapter(...).validate_python(json.loads)` 무 · 컴프리헨션 요소 후보 · `[…]["k"]`·`.get()` 후보 · `j.loads`/`loads`/`jl` 후보 · 여러 줄 값 좌표 = 문장 줄 ✓ · Return: `-> object` 무 · `-> dict[str, object]` 후보 · 주석 없음 후보 · `-> list[object]` `[…]` 무 · `-> tuple[object] | None` `(…,)` 무 · `-> object | None` 무 · `-> Any` 후보 · `-> list[object] | None` 무 ✓.
거짓 ⓓ 2형(MINOR): ⑴ `q: tuple[object, ...] = (json.loads(raw),)` → 후보(마지막 원소 `...` 가 Name 이 아님) · 이종 튜플 `tuple[object, str] = (json.loads, name)` → 후보(index 무시) · `dict[object, str] = {json.loads: name}` → 후보(키 자리 무시) ⑵ 메시지 `` `json.jl(…)` ``(별칭명). 정정 §3-3·§3-4(시제품 실측: 8·10·12 무 · 9 후보 · 35 `json.loads`).

### 2.4 #493 수리 (A-4)

- `_resolved_base :347` = Subscript `.value` 벗김 + 별칭 depth<4(뒤 정의 우선) → `_is_declarative_class :357` 기저 집합. 옛/새 4사본 `#493` (파일:줄, 메시지) 집합 lost 0 · gained 0(3,216/3,225/3,225/173 · `$S/rv5A/analyze.py`) + `[#493]` 라인 순서 동일 → «늘리지도 줄이지도 않음». 픽스처 main 트리(신설 파일 없음) `lossless_diff.py $S/impl/lossless-fxmain` 재실행 = 9/9 · VERDICT LOSSLESS ✓.
- `_scan_stmts(` 13곳 = 정의 1 + 재귀 11(ClassDef→`_scan_class`·FunctionDef·If/While 2·For 2·With 1·Try 4) + `main :1134` 1 — 전부 `aliases` 전달(`grep -n '_scan_stmts(\|_scan_class(' | grep -v aliases` → 정의 2줄만) ✓. 필답의 «9곳» 은 계수 착오(실제 11).

### 2.5 무손실 판형 (A-7)

`$S/rv3C/lossless_diff.py` 허용 규칙 = 계획 §5·Δ3 ⑫ 와 동일하나 A∖B 키가 **(경로, 줄)** — Δ3 ⑫ 의 «(경로·줄·슬롯)»·rv3-C C-3 «혼재 줄 spring 2» 는 판형에 반영되지 않았다. 본 리뷰가 슬롯 키(#645 nested 라벨 «`fn()` 매개변수 `x`»/«`fn()` 반환 타입»/«`t` 주석» ↔ #647 v 라벨 + 값 `Any`)로 재대조: spring 655/655 · d2eaafe 642/642 · f5ee428 661/661 · kkebi 55/55 · unmatched 0 · 비허용 A∖B/B∖A 0 · B∖A 규칙 = {#646, #647, #650} 만. → 이번 커밋은 슬롯 단위로도 LOSSLESS. 조각 2 전에 판형을 슬롯 키로 올린다(MINOR · §3-8). 실측 계수(루트 필터 뒤): #646 18/31/18/21 · #647 v 줄 594/585/603/161(Any 518/507/524/52 · obj-ret 60/61/62/59 · obj-attr 18/19/19/52) · ⓓ 입구 줄 255/261/261/253 · 자리표시 8/9/9/42 · #650 40/38/40/1 — 구현 기록·rv3-C ΔC-2 와 일치.

### 2.6 ⓔ2 registry_gate (A-5)

- diff 정독: `_CANDIDATE_RE :95` · `_run_registry` 반환 4-튜플 `:191`·`:250` + `cands` `:210` · 후보 수집은 `m is None` 분기 안 `:232~234`(→ `parsed` 는 위반만 · ⓓ 만 있는 red 검사기는 여전히 합성 귀속 fail-closed) · 호출처 4 `:590`(provenance · `_cands` 폐기) · `:706`(비-git · `l_cands=set()`) · `:747`·`:751` · 집합 3줄 `:757~759` · 보고 절 `:800~803`(`if n_cands or l_cands`) · sidecar `:291~297`(`if candidates` · `candidate_lines`/`candidate_records`=severity info ∧ 키 일치 · `records` 무접촉) · exit `:816` `attributed` 만 · 빚 `debt` 는 `attributed` 기반 무변 ✓.
- smoke 재실행 `registry_gate_smoke.py` → 케이스 33 · 일치 33(`$S/rv5A/smoke.log`). Q/Q′ 단언 문자열 «== ⓓ 신규(N′∖L′) 1건 · legacy 1건» = 출력 `:801` 판형과 일치(재현 `$S/rv5A/q_sidecar.py` 로 확인). sidecar 재현: Q keys = anchor·attributed_lines·candidate_lines·candidate_records·experiment_run_id·records·schema·unmatched_lines · `candidate_records` = [(#69, info, fresh_probe.py:2)] · `records` 0 · Q′ exit 2 · `records` 3(schema_smoke #95/#96/#490) · `candidate_lines` fresh_probe 만 → 분리 성립. **단 smoke Q 의 `not any("fresh_probe" in r.file for r in records)` 는 records 가 빈 케이스라 공허 단언이고 Q′ 는 sidecar 를 읽지 않는다**(MINOR · §3-7).
- P0′: 옛 게이트(`34c74a6`)와 현행 검사기 트리에서 마스킹 후 byte 동일 = 통과(33/33) → P0 저장소(good_bc)에 ⓓ 0 이라 새 절·키 부재가 byte 동일의 이유 ✓(무조건 인쇄였다면 red).
- 실측: `$S/kkebi --anchor HEAD` + 무해 파일(`rv5a_probe.md` · 실행 뒤 제거) → 귀속 0 · legacy 512 · **ⓓ legacy 1,269**(저자 로그와 동일) · exit 0. ⓓ 신규 1 은 실행 시점에 리뷰어 C 가 사본에 넣은 `_rv5c_probe` 지역 변수(`dict/Mapping[…, object]` ⓓ#647)로 — 오염이지만 «새 ⓓ 1줄만 신규 절에 실리고 legacy 1,269 는 접힌다»의 실증이다.
- Δ10 대조 사각 1: 계획은 «ⓓ 절·sidecar 키는 N′∪L′≠∅ 일 때만» 인데 sidecar 는 `cand_new`(N′∖L′) 만 넘겨 **legacy-only 상황에서 키가 빠진다**(보고 절은 인쇄됨). P0′·소비자(`design_pregate.run_gate` 는 `attributed_lines` 만 · `regen_core.select_records` 는 `records` 만)에는 무영향 — 문면·코드 중 하나로 맞춘다(MINOR · §3-6).
- docstring: 모듈 docstring(`:1~90`)·`_write_introduced` docstring 에 ⓓ 앵커 차분 채널 언급 0 — 계획 §2.4 «docstring» 미이행(MINOR).

### 2.7 픽스처·매트릭스 (A-6)

- good: `check-public-surface-annotation.py public_surface/good` → «clean — 파일 21개» · sink 0 레코드 · exit 0 ✓(Δ9 의 `invoice/panel.py` ⓓ② 시연은 «레코드 0» 요건과 충돌해 bad 로 옮긴 조정 — 타당 · 구현 기록에 명시됨).
- bad 37 레코드 = `#358×2`(order_summary_query fetch_all/fetch_one) · `#456×2`(invalid_lookup/malformed) · `#493×9`(place_order_use_case 7 · aliased_shadow 1 · **stub_generic_bad.py:30 `SharedAliasPanel.list_display`** = 타 모듈 별칭 미해소 · 의도·기록 ✓) · `#645×8`(any_signature 8 — `:41` 은 #647 로 승격) · `#646×7` = v 6(`:11` ⓐ Name · `:15` ⓐ Attribute · `:19` ⓑ 여러 줄 접기 · `:26` ⓑ(ii) 속성 줄 · `:29` ⓑ 타 모듈 별칭 헤더 · `:33` ⓐ ModelForm) + ⓓ 1(`:25` 헤더 직접 subscript ⓓ②) · `#647×6`(record_leak `:9` 속성 object v · `:12` 반환 object v · `:16` nested Any v · `:20` `TypeIs[dict[str, Any]]` v · `:25` `dict[str, Any]` v · any_signature `:41` v) · `#650×1`(record_leak `:25`) · `#69×2` — 계수 문자열과 1:1 ✓.
- mypy strict(ΔC-8 · `cd good && PYTHONPATH=MYPYPATH=$S/spring … --config-file $S/spring/pyproject.toml --follow-imports=silent`): 신설 `order/panel.py`·`shipment/panel.py`·`order/form/line_form.py`·`ledger_record_query.py` 0 errors · 정정 `order_form.py` 22 errors(`**kwargs: object` arg-type — 기존과 같은 legacy · 무변) ✓.
- 매트릭스 재실행: `checker_cross_matrix` «차이 0건» · EXPECTED diff 는 기존 쌍 3행의 계수만(port_adapter_pairing/transaction_boundary good 의 ⓓ#647 관찰 12·2 · public_surface×port-adapter #359 2→4) · 추가 행 0 → 신규 쌍 0 ✓ · `fixture_matrix` 104/104 · `checker_baseline_matrix` 73/73 · `findings_count_matrix` 73/73 ✓.

### 2.8 새로 발견한 결함(요약 → §3)

| # | 심각도 | 자리 | 내용 |
|---|---|---|---|
| N-1 | **MAJOR** | `check-public-surface-annotation.py:331` | TC 중간 ClassDef mixin-first → 사용 클래스 ⓐ 거짓 위반 |
| N-2 | MINOR | `:865~906` | `if TYPE_CHECKING … else: class _B(admin.ModelAdmin)` 런타임 전용 ClassDef 에 ⓐ(«[type-arg] 빚» 문면 거짓 — mypy 미도달) |
| N-3 | MINOR | `:923~939` `_slot_is_object` | `tuple[object, ...]`·이종 튜플·dict 키 자리 → 거짓 ⓓ#650 |
| N-4 | MINOR | `:988` | #650 메시지가 별칭명(`json.jl`)을 찍는다 |
| N-5 | MINOR | `:909~918` | 한 줄 클래스에서 ⓑ(i)+ⓑ(ii) 같은 줄 2건 |
| N-6 | MINOR | `registry_gate.py:291`·`:812` | sidecar ⓓ 키 조건 N′∖L′ ≠ 계획 N′∪L′ · docstring 미기재 |
| N-7 | MINOR | `registry_gate_smoke.py:295~306` | Q «records 분리» 공허 단언 · Q′ sidecar 미검 |
| N-8 | MINOR | `$S/rv3C/lossless_diff.py` | A∖B 1:1 키 (경로,줄) — 슬롯 키 미격상(이번 커밋은 본 리뷰가 슬롯 키로 닫음) |
| N-9 | 문면 | `:735·:738·:741·:744` | 라벨 뒤 ` 의 ` 조사로 «`y` 주석 의 값 자리» 띄어쓰기 · `TYPE_IGNORE_RE = __import__("re")…`(`:156`) 는 `import re` 로 |

## 3. 정정 제안(코드 수준 · 시제품 `$S/rv5A/proto/check-public-surface-annotation.py` · `proto.diff` 34줄 · 합성 확인 + 4사본 레코드 집합 동일)

### 3-1 (N-1 · MAJOR) `_alias_defs` — TC 중간 ClassDef 의 Subscript 기저 전부 기록(첫 기저는 마지막에 — `_resolved_base` 의 «뒤 정의» 의미 보존)

`dddjango/scripts/check-public-surface-annotation.py:331~332`
```python
            elif isinstance(st, ast.ClassDef) and in_tc and st.bases:
                lst = out.setdefault(st.name, [])
                lst.extend((b, True) for b in st.bases[1:] if isinstance(b, ast.Subscript))  # mixin-first 중간 ClassDef
                lst.append((st.bases[0], True))
```
docstring(`:317~322`) «`TYPE_CHECKING` 분기 안 ClassDef 의 첫 기저» → «… ClassDef 의 첫 기저 + 나머지 Subscript 기저». 합성 `MixUser` → 무발화 · 나머지 39형 무변 · 4사본 동일. codex byte 미러 함께.

### 3-2 (N-2 · MINOR · 선택) else 분기 런타임 ClassDef 는 ⓐ 대상에서 제외(ⓑ·ⓓ② 유지)

`:874~885 mark_tc` 에 `rt_only: set[ast.ClassDef]` 를 추가해 `_is_type_checking(st.test)` 인 If 의 `orelse` 직계 ClassDef 를 담고, `:903` `elif bare:` → `elif bare and cls not in rt_only:`. 규범이 else 를 별칭으로 못 박았으므로 «위반 유지 + 문면을 «런타임 분기는 별칭으로»» 로 바꾸는 선택지도 성립 — 어느 쪽이든 문면과 판정을 맞춘다.

### 3-3 (N-3 · MINOR) `_slot_is_object` — Ellipsis 제거 · 튜플 index · dict 키 자리

`:923` 시그니처 `idx: "int | None" = None` 추가 · `:935~939`:
```python
        elts = list(ann.slice.elts) if isinstance(ann.slice, ast.Tuple) else [ann.slice]
        variadic = any(isinstance(e, ast.Constant) and e.value is Ellipsis for e in elts)
        elts = [e for e in elts if not (isinstance(e, ast.Constant) and e.value is Ellipsis)]
        if not elts:
            return False
        if idx is not None and _leaf(_resolved_name(ann.value, bindings)) in ("tuple", "Tuple") and not variadic:
            pick = elts[idx] if idx < len(elts) else elts[-1]  # 이종 튜플 — 그 원소의 자리
        else:
            pick = elts[0] if idx == -1 and len(elts) > 1 else elts[-1]  # dict 키 자리(-1) · 그 밖 값/원소 자리
        val = _unstring(pick)
        return isinstance(val, ast.Name) and val.id == "object"
```
`judge :965` 에 `idx` 인자를 더해 AnnAssign/Return 호출에 전달하고 `:979~981` 리터럴 분기에서 `pos = p.elts.index(node)`(Tuple) · `-1`(Dict 키) 을 계산해 `judge(p, 1, pos)`. 실측: `tuple[object, ...]`·`tuple[object, str]=(json.loads, name)`·`dict[object, str]` 무 · `tuple[str, object]=(json.loads, name)` 후보.

### 3-4 (N-4 · MINOR) #650 메시지 이름을 origin 으로

`:988`
```python
                fn_name = _dotted(node.func, origins).rsplit(".", 1)[-1] if isinstance(node.func, ast.Name) else _name_of(node.func)
                cands.add("#650", f"{rel}:{ln}", f"`json.{fn_name}(…)` 결과가 {why}로 흐른다", JSON_Q)
```

### 3-5 (N-5 · MINOR) ⓑ(ii) 는 헤더 범위 밖 줄만

`:912` 루프 첫 줄에 `if ln <= end: continue`.

### 3-6 (N-6 · MINOR) registry_gate — 문면·코드 정합 택일

(a) 계획대로 «N′∪L′≠∅» 이면 `main :812` 호출을 `cand_new if (n_cands or l_cands) else None` 대신 별도 플래그로 넘겨 `_write_introduced :291` 을 `if candidates is not None:` 로(빈 `candidate_lines: []` 허용 · P0′ 는 ⓓ 0 이라 여전히 키 부재) · (b) 또는 코드를 정본으로 두고 계획/회신 문면을 «sidecar 키는 ⓓ 신규가 있을 때만» 으로. 어느 쪽이든 모듈 docstring `:19~31` 채널 목록에 «ⓓ 앵커 차분 채널(exit 불산입 · 신규분만 sidecar)» 1항과 `_write_introduced` docstring 에 `candidate_*` 키 설명을 추가한다.

### 3-7 (N-7 · MINOR) smoke Q/Q′ 단언 강화

`registry_gate_smoke.py:297~302` `q_ok` 에 `payload_q.get("candidate_records")` ∧ 전부 `severity=="info"` ∧ `rule=="#69"` ∧ `file` 이 `fresh_probe.py` 로 끝남 ∧ `payload_q.get("records") == []` 를 더하고, Q′(`:304~306`)도 `--introduced-json` 으로 돌려 `records` 의 file 이 전부 `schema_smoke` ∧ `candidate_lines` 가 fresh_probe 만인지 단언(본 리뷰 재현값과 같다).

### 3-8 (N-8 · MINOR) 무손실 판형 슬롯 키

`$S/rv3C/lossless_diff.py judge` 의 A∖B 허용을 «(경로, 줄, 라벨) 에 B 의 #647 v(값 Any) 존재» 로 — 라벨 추출은 `$S/rv5A/analyze.py label645/label647` 판형(#645 nested 메시지의 ` 의 타입 안에 `Any``·` 안에 `Any``·` 주석에 `Any`(nested)` 접미 제거 ↔ #647 «`<라벨>` 의 값 자리가 `Any` 다»). 조각 2 무손실 실행 전에 교체.

### 3-9 (N-9 · 문면) `f"{label} 의 "` → 라벨이 `주석`/`반환 타입` 으로 끝나므로 `f"{label}의 "`(붙임) 또는 라벨을 «`y` 주석의» 형으로 · `:156` `import re` 모듈 상단 이동.

## 4. 사각

- 합성은 문법 형상 위주다 — 실제 django-stubs `.pyi` 의 CBV 32 전수(기본값 없는 TypeVar) 재열거는 rv3-A §2.3 실측을 신뢰했다(6.1.0 `.pyi` 재열람 안 함).
- `#650` 의 «컴프리헨션 요소»는 `[json.loads(s) for s in xs]` 형(요소)만이고 `[k for k in json.loads(raw)]`(iterable 자리)는 무발화 — 계획 Δ7 오라클과 같아 결함으로 세지 않았다(문면 «컴프리헨션 요소» 그대로).
- #647 자리표시 ⓓ 는 depth 1(`tuple[str, Sequence[object]]` 무발화) — 계획대로.
- TC 클래스 안 중첩 ClassDef 의 직접 subscript(`mark_tc` 가 ClassDef 본문으로 내려가지 않음) · `if not TYPE_CHECKING:` 역분기 → 거짓 ⓓ②(exit 무관 · 현장 0) — 정정 제안에 넣지 않았다(발생 시 `mark_tc` 에 ClassDef 재귀 + `UnaryOp(Not)` 처리 2줄).
- `candidate_records` 는 `records` 와 달리 `file_raw` 를 보존하지 않는다(대칭성 · 소비자 없음).
- 온톨로지·LEDGER·미러 의미 동치·회신 문면은 B/C 축 — 여기서는 byte 미러(`diff -rq` · `__pycache__` 뿐)·rulepack `--check`·spec_lint·pregate `--check` 만 봤다. `verify1.log` 6/6 는 재실행하지 않았고(218초) 그 구성 요소 중 fixture/baseline/count/cross/smoke/spec_lint/rulepack/pregate-kinds 를 개별 재실행했다.
- 등재의 «#63 행 stale 정정»(계획 Δ3 ⑨)은 이 커밋에 없다 — Δ13 이 openapi 문면을 조각 2 로 보냈으므로 조각 2 리뷰에서 확인.
- 사본 오염: 동시 리뷰어의 `mp_probe_rv5b/`(spring)·`_rv5c_probe`(kkebi)가 실행 도중 나타났다 — 본 리뷰 수치는 오염 전 실행 또는 경로 제외값이며 `git status` 는 리뷰 종료 시점에 tracked 무변.
